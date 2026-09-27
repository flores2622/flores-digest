"""Re-read a past day's coaching cards with today's Apollo (Frank,
2026-09-27: "i also wanted to rebuild all coaching cards back to 9/1 with
the new apollo changes").

The card cache is keyed by call, not prompt, so a nightly run never re-reads
a card (CLAUDE.md, Cost). This is the deliberate exception, day by day:

    python3 rebuild_cards.py 2026-09-22                # read, compare, publish nothing
    python3 rebuild_cards.py 2026-09-22 --publish      # ...and put the new cards on the board
    python3 rebuild_cards.py 2026-09-01 2026-09-25 --publish   # oldest first

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
    for name in INPUTS:
        key = f"cache/{day}/{name}_{day}.json"
        try:
            body = cli.get_object(Bucket=bucket, Key=key)["Body"].read()
        except Exception:
            log(f"  {day}: no {name} in R2")
            continue
        (ROOT / f"data/{name}_{day}.json").write_bytes(body)


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


def rebuild(day, publish=False, log=print):
    import coaching_cards
    import publish_board
    cli, bucket = publish_board._client()
    _pull_inputs(cli, bucket, day, log)
    old_cache_path = ROOT / f"data/coaching_cards_{day}.json"
    old_cache = old_cache_path.read_bytes() if old_cache_path.exists() else None
    old_doc_raw = cli.get_object(Bucket=bucket, Key=f"days/{day}.json")["Body"].read()
    old_doc = json.loads(old_doc_raw)
    _refresh_moves(day, log)
    if old_cache_path.exists():
        old_cache_path.unlink()              # read every call again
    cards = coaching_cards.build(day, log=log)
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
    start = args[0]
    end = args[1] if len(args) > 1 else start
    publish = "--publish" in argv
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
    for day in sorted(d for d in days if start <= d <= end):
        try:
            rebuild(day, publish=publish, log=lambda m: print(m, flush=True))
        except Exception as e:
            print(f"  {day}: FAILED ({type(e).__name__}: {e}) -- left as it was", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
