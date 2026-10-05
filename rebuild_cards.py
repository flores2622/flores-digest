"""Re-read a past day's coaching cards with today's Apollo (Frank,
2026-09-27: "i also wanted to rebuild all coaching cards back to 9/1 with
the new apollo changes").

The card cache is keyed by call, not prompt, so a nightly run never re-reads
a card (CLAUDE.md, Cost). This is the deliberate exception, day by day:

    python3 rebuild_cards.py 2026-09-22                # read, compare, publish nothing
    python3 rebuild_cards.py 2026-09-22 --publish      # ...and put the new cards on the board
    python3 rebuild_cards.py 2026-09-01 2026-09-25 --publish   # oldest first
    python3 rebuild_cards.py --days 2026-09-01,2026-09-04 --publish
    python3 rebuild_cards.py 2026-09-22 --publish --reuse  # publish a test run's reads
    python3 rebuild_cards.py 2026-09-01 2026-09-25 --publish --repair
        # re-read only follow-ups missing their scorecard, and failed reads
    add --live to read one by one at full price instead of one half-price
    Message Batch per day (usually minutes, at most 24 hours)

For each day:
  1. the day's own inputs come back from R2's cache/<day>/ (call rows,
     transcripts, recordings list, call logs) -- exactly what the nightly run
     read;
  2. every call row's stage moves are re-read from the lead notes, inbound
     rows included (they were [] before 2026-09-27, daily.py);
  3. every call is read again (one paid model read per live contact, the
     pure-service ones included -- they are filtered out after the read);
     the lead's stage "then" comes from its move history
     (coaching_cards._group_stage) and the quote list is left out of the lead
     history (AgencyZoom keeps no quote date);
  4. with --publish, days/<day>.json and cache/<day>/coaching_cards_<day>.json
     are backed up under backups/<today>-card-rebuild/ and the day gets its
     new `calls`, `scan` and `objcats`. Nothing else on the page changes.
     The new card cache replaces the old one in R2, so a later rebuild keeps
     these reads.

Without --publish the old and new cards are written side by side to
out/card_rebuild_<day>.json for comparison.
"""
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
INPUTS = ("metrics", "fulltx", "audiorefs", "rc_raw", "rc_window", "coaching_cards")


def _pull_inputs(cli, bucket, day, log):
    """The day's inputs from R2 -- unless the local copy is newer (a
    `daily.py --day <day> --no-send` just rebuilt it and stopped before its
    last upload, 09-03 on 2026-09-27)."""
    for name in INPUTS:
        key = f"cache/{day}/{name}_{day}.json"
        local = ROOT / f"data/{name}_{day}.json"
        try:
            obj = cli.get_object(Bucket=bucket, Key=key)
        except Exception:
            log(f"  {day}: no {name} in R2" + (" -- using the local copy" if local.exists() else ""))
            continue
        if local.exists() and local.stat().st_mtime > obj["LastModified"].timestamp():
            log(f"  {day}: local {name} is newer than R2's -- kept")
            continue
        local.write_bytes(obj["Body"].read())


def _from_old_cards(day, old_cards, log):
    """A day whose full transcripts were never saved to R2 (09-10, 09-14)
    gets them back from its own published cards, which carry the text each
    was read from -- matched to the call rows by producer and lead."""
    import call_summary as CS
    fx_path = ROOT / f"data/fulltx_{day}.json"
    if fx_path.exists():
        return
    M = json.loads((ROOT / f"data/metrics_{day}.json").read_text())
    by = {(c.get("who"), c.get("lead_id")): c.get("transcript") for c in old_cards if c.get("transcript")}
    fx, done = {}, set()
    for who, v in (M.get("producers") or {}).items():
        for r in v.get("call_detail") or []:
            k = (who, r.get("lead_id"))
            if k in by and k not in done:
                fx[CS._ck(who, r["number"])] = by[k]
                done.add(k)
    fx_path.write_text(json.dumps(fx))
    log(f"  {day}: no saved transcripts -- {len(fx)} taken from the published cards")


def _keep_recordings(cards, old_cards):
    """A rebuilt card keeps the old card's "listen to the call" ids when this
    day's recordings list was never saved (09-08, 09-11, 09-14)."""
    by = {(c.get("who"), c.get("lead_id")): c.get("recording_ids") for c in old_cards if c.get("recording_ids")}
    for c in cards:
        if not c.get("recording_ids") and (c.get("who"), c.get("lead_id")) in by:
            c["recording_ids"] = by[(c.get("who"), c.get("lead_id"))]


def _drop_bad_reads(path, log, day):
    """--repair: forget the reads a run before the follow-up retry left
    without their follow-up scorecard, so only those calls are read again."""
    import coaching_cards as cc
    cache = json.loads(path.read_text())
    bad = [k for k, d in cache.items()
           if (cc._flow(d.get("flow")) or [""])[0] in cc.FU_FLOWS
           and len(cc._clean_score(d.get("fuscore"), cc.FU_DIMS)) < 3]
    for k in bad:
        del cache[k]
    path.write_text(json.dumps(cache, indent=1))
    log(f"  {day}: {len(bad)} follow-up read(s) without their scorecard will be read again")


def _failed_reads(day, cards, old_cards):
    """Old cards whose call has no new read at all -- the read failed (a
    model answer that was not valid JSON, Joseph Valentine 2026-09-22) --
    rather than being read again as a pure service call. Those old cards
    stay on the page instead of silently disappearing."""
    import coaching_cards as cc
    M = json.loads((ROOT / f"data/metrics_{day}.json").read_text())
    cache = json.loads((ROOT / f"data/coaching_cards_{day}.json").read_text())
    groups = {}
    for who, v in (M.get("producers") or {}).items():
        for r in v.get("call_detail") or []:
            if (r.get("summary") or {}).get("source") == "recording" and r.get("lead_id") is not None:
                groups.setdefault((who, r["lead_id"]), []).append(r)
    have = {(c.get("who"), c.get("lead_id")) for c in cards}
    # Also an old card for a call the saved rows do not know at all (09-14's
    # rows hold 3 of its 6 carded calls): it cannot be read again, so it
    # stays as it was.
    return [c for c in old_cards if (c.get("who"), c.get("lead_id")) not in have
            and ((c.get("who"), c.get("lead_id")) not in groups
                 or cc._group_ck(c.get("who"), groups[(c.get("who"), c.get("lead_id"))]) not in cache)]


def _readable_rows(day, log):
    """A row the night filed under its producer note only because the model
    could not be reached (09-17: no API key in that run, 24 of 28 live
    contacts) is read like any other when its transcript is on file."""
    import call_summary as CS
    fx_path = ROOT / f"data/fulltx_{day}.json"
    if not fx_path.exists():
        return
    fx = json.loads(fx_path.read_text())
    mpath = ROOT / f"data/metrics_{day}.json"
    M = json.loads(mpath.read_text())
    n = 0
    for who, v in (M.get("producers") or {}).items():
        for r in v.get("call_detail") or []:
            s = r.get("summary") or {}
            if s.get("source") != "recording" and fx.get(CS._ck(who, r["number"])):
                r["summary"] = {**s, "source": "recording"}
                n += 1
    if n:
        mpath.write_text(json.dumps(M))
        log(f"  {day}: {n} conversation(s) with a transcript but no read that night -- read now")


def _refresh_moves(day, log):
    """Every call row's stage moves, re-read from the notes across every lead
    record on its number (what outbound rows always had; inbound rows had
    none before 2026-09-27)."""
    import live_contact as lc
    from az_corpus import phone_index
    mpath = ROOT / f"data/metrics_{day}.json"
    M = json.loads(mpath.read_text())
    ix = phone_index(json.loads((ROOT / "data/az_leads_all.json").read_text()))
    changed = 0
    for who, v in (M.get("producers") or {}).items():
        for r in v.get("call_detail") or []:
            ids = [l.get("id") for l in ix.get(r.get("number"), []) if l.get("id")] or [r.get("lead_id")]
            ids = [i for i in ids if i]
            if not ids:
                continue
            moves = [m["move"] for m in lc.evidence(ids, day, who)["stage_moves"]]
            if moves != (r.get("moves") or []):
                r["moves"] = moves
                changed += 1
    mpath.write_text(json.dumps(M))
    log(f"  {day}: stage moves re-read ({changed} row(s) changed)")


def rebuild(day, publish=False, reuse=False, repair=False, log=print, batch=True):
    """`reuse` publishes the reads a previous run of this script left in
    data/coaching_cards_<day>.json instead of paying for them again.

    `batch` (the default; --live turns it off): the day's reads go out first
    as one half-price Message Batch (call_summary.run_batch) and the build
    below takes its answers from it -- same requests, same reads."""
    import call_summary
    import coaching_cards
    import publish_board
    cli, bucket = publish_board._client()
    old_cache_path = ROOT / f"data/coaching_cards_{day}.json"
    kept = old_cache_path.read_bytes() if reuse and old_cache_path.exists() else None
    _pull_inputs(cli, bucket, day, log)
    old_cache = old_cache_path.read_bytes() if old_cache_path.exists() else None
    old_doc_raw = cli.get_object(Bucket=bucket, Key=f"days/{day}.json")["Body"].read()
    old_doc = json.loads(old_doc_raw)
    # The page as it was BEFORE any rebuild, when a backup exists: a second
    # run (a retry) must compare against the original cards, not its own.
    try:
        pages = [o["Key"] for o in cli.list_objects_v2(Bucket=bucket, Prefix="backups/").get("Contents", [])
                 if o["Key"].endswith(f"-card-rebuild/days/{day}.json")]
        if pages:
            old_doc = json.loads(cli.get_object(Bucket=bucket, Key=sorted(pages)[0])["Body"].read())
    except Exception:
        pass
    _refresh_moves(day, log)
    _from_old_cards(day, old_doc.get("calls") or [], log)
    _readable_rows(day, log)
    if reuse:
        # This script's own reads: the local copy, or -- in a fresh
        # container -- the one a publish put back in R2 (just pulled).
        if kept is not None:
            old_cache_path.write_bytes(kept)
        if repair and old_cache_path.exists():
            _drop_bad_reads(old_cache_path, log, day)
    elif old_cache_path.exists():
        old_cache_path.unlink()              # read every call again
    if batch:
        call_summary.run_batch(call_summary.collect(
            lambda: coaching_cards.build(day, log=lambda m: None)), log=log)
    cards = coaching_cards.build(day, log=log)
    # A read that failed is retried once (build only re-reads calls it has no
    # read for); one that fails again keeps its old card.
    kept_old = _failed_reads(day, cards or [], old_doc.get("calls") or []) if cards else []
    if kept_old:
        log(f"  {day}: {len(kept_old)} old card(s) without a new read -- retrying any failed read")
        cards = coaching_cards.build(day, log=log)
        kept_old = _failed_reads(day, cards or [], old_doc.get("calls") or [])
        if kept_old:
            log(f"  {day}: keeping {len(kept_old)} old card(s) that could not be read again: "
                + ", ".join(c.get("lead") or "?" for c in kept_old))
            cards = (cards or []) + kept_old
    if cards:
        _keep_recordings(cards, old_doc.get("calls") or [])
    if not cards:
        log(f"  {day}: no cards came back -- nothing changed")
        if old_cache is not None:
            old_cache_path.write_bytes(old_cache)
        return None
    if not publish:
        out = ROOT / f"out/card_rebuild_{day}.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps({"old": old_doc.get("calls") or [], "new": cards}, indent=1, default=str))
        log(f"  {day}: {len(old_doc.get('calls') or [])} old / {len(cards)} new cards -> {out}")
        return cards
    stamp = dt.date.today().isoformat()
    base = f"backups/{stamp}-card-rebuild"
    for key, body in ((f"days/{day}.json", old_doc_raw),
                      (f"cache/{day}/coaching_cards_{day}.json", old_cache)):
        if body is None:
            continue
        try:
            cli.head_object(Bucket=bucket, Key=f"{base}/{key}")
        except Exception:
            cli.put_object(Bucket=bucket, Key=f"{base}/{key}", Body=body, ContentType="application/json")
    # Re-read the page just before writing, so anything another job added
    # to it meanwhile (texts and emails) is kept.
    doc = json.loads(cli.get_object(Bucket=bucket, Key=f"days/{day}.json")["Body"].read())
    publish_board.save_doubts(day, coaching_cards.split_doubts(cards), log=log)
    doc["calls"] = cards
    doc["scan"] = coaching_cards.scan(cards)
    objc = coaching_cards.objcats(cards)
    if objc:
        doc["objcats"] = objc
    else:
        doc.pop("objcats", None)
    cli.put_object(Bucket=bucket, Key=f"days/{day}.json", Body=json.dumps(doc, default=str).encode(),
                   ContentType="application/json", CacheControl="no-store")
    cli.put_object(Bucket=bucket, Key=f"cache/{day}/coaching_cards_{day}.json",
                   Body=old_cache_path.read_bytes(), ContentType="application/json")
    log(f"  {day}: published {len(cards)} rebuilt cards (was {len(old_doc.get('calls') or [])})")
    return cards


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    only = None
    if "--days" in argv:
        only = set(argv[argv.index("--days") + 1].split(","))
        args = [a for a in args if a != argv[argv.index("--days") + 1]]
        args = [min(only), max(only)]
    start = args[0]
    end = args[1] if len(args) > 1 else start
    publish = "--publish" in argv
    reuse = "--reuse" in argv or "--repair" in argv
    repair = "--repair" in argv
    import publish_board
    cli, bucket = publish_board._client()
    days, token = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": "days/"}
        if token:
            kw["ContinuationToken"] = token
        page = cli.list_objects_v2(**kw)
        days += [o["Key"][5:15] for o in page.get("Contents", []) if o["Key"].endswith(".json")]
        if not page.get("IsTruncated"):
            break
        token = page.get("NextContinuationToken")
    for day in sorted(d for d in days if start <= d <= end and (only is None or d in only)):
        try:
            rebuild(day, publish=publish, reuse=reuse, repair=repair, log=lambda m: print(m, flush=True),
                    batch="--live" not in argv)
        except Exception as e:
            print(f"  {day}: FAILED ({type(e).__name__}: {e}) -- left as it was", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
