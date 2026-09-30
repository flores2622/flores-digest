"""Full transcripts of the service team's calls (Frank, 2026-09-30: "full
transcripts for service calls too").

The nightly only ever downloaded the five producers' recordings, and full-
transcribed only the calls Apollo coaches, so a call Debbie picked up at the
front desk, Amanda's call back on a late payment or Crystal's renewal call had
no transcript to read. This module covers exactly the calls the Service
Center's own rows list, so every transcript opens from a row that counts it:

  * every inbound call a service team member picked up first
    (service_digest.front_figures -- "calls answered"), and
  * every connected dial on service_digest.dial_figures' rows (Debbie's and
    Amanda's every dial, Crystal's only to numbers that route to service,
    commercial-only households left out -- Cerberus's).

For each recorded one it downloads the recording (transcribe.download's own
8/min pacing; producers' calls are usually already on disk) and saves
Deepgram's timed, labelled turns: the team member's side reads
"<First name> (service)" from how they introduce themselves, the customer's
"<First name> (customer)" when the call shows who they are
(deepgram_stt.other_party), everyone else Speaker N. A recording Deepgram has
read before is never paid for again (data/deepgram/ + R2).

    python3 service_calls.py 2026-09-28        # build that day's file
    python3 service_calls.py --backfill 2026-09-01 2026-09-29   # published days

Output: data/servicetx_<day>.json, {recording id: {who, number, direction,
at, seconds, turns}}, carried between containers by r2_cache like the other
day files. service_digest.build() adds it to service/<day>.json as `calls_tx`.
Nothing here raises into a build; a failure leaves the rows without a
transcript, never without their counts.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent

# Card, bank and social security numbers are never stored (messages.redact's
# rule, CLAUDE.md "Texts and emails with customers"). Debbie takes payments
# by phone, and a number read out loud comes back from Deepgram in pieces --
# "4111, 1111", or split across turns by an "okay" -- so after any mention of
# a card, account, routing or social number, every run of 4+ digits in the
# next few turns goes too, whoever said it. A call where that happened is
# `redacted`: the board shows its transcript but never plays it, since the
# recording still has the number in it.
PAY_WORDS = re.compile(
    r"\b(card|credit|debit|visa|master ?card|amex|discover|account|routing|"
    r"social|ssn|cvv|security code|expiration|tarjeta|cr[eé]dito|d[eé]bito|"
    r"cuenta|ruta|seguro social|c[oó]digo|vencimiento)\b", re.I)
_DIGIT_RUN = re.compile(r"(?<!\d)(?:\d[ ,./\-]?){3,}\d(?!\d)")
PAY_REACH = 6


def redact_turns(turns):
    """(turns, redacted) -- messages.redact on every line, plus the payment
    rule above."""
    import messages
    out, hot, hit = [], 0, False
    for x in turns:
        t = re.sub(r"(?<=\d),\s*(?=\d)", " ", x.get("text") or "")
        clean = messages.redact(t)
        if PAY_WORDS.search(t):
            hot = PAY_REACH
        if hot:
            clean = _DIGIT_RUN.sub("[number removed]", clean)
            hot -= 1
        row = dict(x, text=clean)
        if clean != t:
            hit = True
        if clean != (x.get("text") or ""):
            row.pop("w", None)   # the word times no longer line up with the words
        out.append(row)
    return out, hit


def path(day):
    return ROOT / f"data/servicetx_{day}.json"


def load(day):
    try:
        return json.loads(path(day).read_text())
    except (OSError, ValueError):
        return {}


def wanted(day, recs=None, commercial_only=None):
    """{recording id: {who, number, direction, at, seconds}} for every recorded
    call the Service Center's calls-answered and dials rows list."""
    import missed_call_audit as mca
    import service_digest as sd
    recs = recs if recs is not None else mca.collect(day, refresh=False)
    if commercial_only is None:
        import commercial
        import service_retention
        _, commercial_only = commercial.households(service_retention.load_household_map(log=lambda *_: None))
    by_id = {r.get("id"): r for r in recs}
    out = {}
    for c in (sd.front_figures(day, [], [], recs=recs) or {}).get("calls") or []:
        if c.get("rec"):
            out[c["rec"]] = {"who": c["who"], "number": c.get("number"), "direction": "inbound",
                             "at": c.get("at"), "seconds": c.get("seconds")}
    for row in sd.dial_figures(day, recs=recs, commercial_only=commercial_only).get("rows") or []:
        for rid in row.get("recs") or []:
            r = by_id.get(rid) or {}
            out.setdefault(rid, {"who": row["who"], "number": row.get("number"), "direction": "outbound",
                                 "at": r.get("startTime"), "seconds": int(r.get("duration") or 0)})
    return out, by_id


def build(day, log=print, recs=None, commercial_only=None):
    """Download and transcribe what is missing; returns the day's dict."""
    import deepgram_stt as DG
    import transcribe as T
    have = load(day)
    try:
        want, by_id = wanted(day, recs=recs, commercial_only=commercial_only)
    except Exception as e:
        log(f"  service transcripts: could not list the calls ({type(e).__name__}: {e})")
        return have
    todo = [rid for rid in want if not (have.get(rid) or {}).get("turns")]
    if not todo:
        log(f"  service transcripts: {len(want)} calls, all already transcribed")
        return have
    audio = ROOT / T.AUDIO
    fetch = [by_id[r] for r in todo if r in by_id and not (audio / f"{r}.mp3").exists()]
    if fetch:
        log(f"  service transcripts: downloading {len(fetch)} recordings (throttled)...")
        try:
            from rc_client import RingCentral
            T.download(fetch, RingCentral().token(), log=log)
        except Exception as e:
            log(f"  service transcripts: download failed ({type(e).__name__}: {e})")
    if not DG.available():
        log("  service transcripts: DEEPGRAM_API_KEY is not set -- none built")
        return have
    n = 0
    for rid in todo:
        meta = want[rid]
        ap = audio / f"{rid}.mp3"
        if not ap.exists():
            continue
        ts = DG.turns(ap, None, producer=meta["who"], number=meta.get("number"), role="service",
                      answered=meta.get("direction") == "inbound", log=log)
        if ts is None:
            continue
        ts, hit = redact_turns(ts)
        have[rid] = dict(meta, turns=ts, redacted=hit)
        n += 1
    path(day).parent.mkdir(parents=True, exist_ok=True)
    path(day).write_text(json.dumps(have))
    log(f"  service transcripts: {n} built, {len(have)} of {len(want)} calls on file")
    return have


def _front_recs(calls, recs):
    """Each calls-answered row's recording id, matched on the call's start
    and the caller's number -- for pages built before rows carried `rec`."""
    import missed_call_audit as mca
    by = {(r.get("startTime"), mca.norm((r.get("from") or {}).get("phoneNumber"))): r
          for r in recs if r.get("direction") == "Inbound"}
    for c in calls:
        if "rec" not in c:
            r = by.get((c.get("at"), c.get("number")))
            c["rec"] = r["id"] if r and r.get("recording") else None


def backfill(start, end, log=print, force=False):
    """Give published days from `start` to `end` their service transcripts
    (Frank, 2026-09-30: "do the same for all of september"). Per day, from
    that day's saved files in R2 (call log, open SRs; the day's corpus
    snapshot when there is one, else today's customers and leads):

      * backs the page up under backups/<today>-service-calls/ (once);
      * adds `dials` (dial_figures) if the page has none -- a new figure on
        a page that never had one; an existing one is left as it is and only
        gains each row's `recs`;
      * adds each calls-answered row's `rec`;
      * downloads and transcribes the listed calls (build), uploads the new
        recordings, the day file and the Deepgram reads to R2, and adds
        `calls_tx`.

    Nothing else on the page changes. A day whose page already has calls_tx
    is skipped unless `force`, so a stopped run picks up where it left off."""
    import datetime as dt
    import commercial
    import publish_board
    import r2_cache
    import service_digest as sd
    import service_retention
    cli, bucket = publish_board._client()
    stamp = dt.date.today().isoformat()
    _, com_only = commercial.households(service_retention.load_household_map(log=log))
    # Today's customers and leads, for a day with no corpus snapshot of its
    # own -- read once, restored before each such day, so no day inherits
    # another day's snapshot.
    import az_corpus
    from az_client import AgencyZoom
    az_corpus.fetch(force=True)
    (ROOT / "data/az_customers_all.json").write_text(
        json.dumps(AgencyZoom()._paged("/v1/api/customers/list", "customers", {})))
    today = {n: (ROOT / "data" / n).read_bytes() for n in ("az_leads_all.json", "az_customers_all.json")}
    done = []
    for d in sorted(x for x in sd._published_days(cli, bucket) if start <= x <= end):
        key = sd._key(d)
        raw = cli.get_object(Bucket=bucket, Key=key)["Body"].read()
        doc = json.loads(raw)
        if doc.get("calls_tx") and not force:
            log(f"{d}: already has {len(doc['calls_tx'])} transcripts, left alone")
            continue
        for name in (f"rc_raw_{d}.json", f"az_service_tickets_{d}.json"):
            f = ROOT / "data" / name
            if not f.exists():
                try:
                    f.write_bytes(cli.get_object(Bucket=bucket, Key=r2_cache._key(d, name))["Body"].read())
                except Exception:
                    pass
        f = ROOT / "data" / f"rc_raw_{d}.json"
        if not f.exists():
            log(f"{d}: no call log saved, left alone")
            continue
        recs = json.loads(f.read_text())
        snap = r2_cache.load_corpus(d)
        if not snap:
            for name, body in today.items():
                (ROOT / "data" / name).write_bytes(body)
        log(f"{d}: customers and leads {'of the day' if snap else 'as of today (no snapshot saved)'}")
        backup = f"backups/{stamp}-service-calls/{key}"
        try:
            cli.head_object(Bucket=bucket, Key=backup)
        except Exception:
            cli.put_object(Bucket=bucket, Key=backup, Body=raw, ContentType="application/json")
        fresh = sd.dial_figures(d, recs=recs, commercial_only=com_only)
        if doc.get("dials") is None:
            doc["dials"] = fresh
        else:
            by = {(r["who"], r["number"]): r.get("recs") or [] for r in fresh["rows"]}
            for r in doc["dials"].get("rows") or []:
                r.setdefault("recs", by.get((r.get("who"), r.get("number")), []))
        front = doc.get("front") or {}
        _front_recs(front.get("calls") or [], recs)
        tx = build(d, log=log, recs=recs, commercial_only=com_only)
        listed = {c.get("rec") for c in front.get("calls") or [] if c.get("rec")}
        listed |= {i for r in doc["dials"].get("rows") or [] for i in r.get("recs") or []}
        doc["calls_tx"] = {k: v for k, v in tx.items() if k in listed and v.get("turns")}
        # The new recordings, the day file and Deepgram's reads -- to R2
        # directly (sync_up_day would also re-send every other day file).
        up = 0
        for rid in tx:
            ap = ROOT / "data/audio" / f"{rid}.mp3"
            k = r2_cache._audio_key(d, rid)
            if not ap.exists():
                continue
            try:
                cli.head_object(Bucket=bucket, Key=k)
            except Exception:
                cli.put_object(Bucket=bucket, Key=k, Body=ap.read_bytes(), ContentType="audio/mpeg")
                up += 1
        if path(d).exists():
            cli.put_object(Bucket=bucket, Key=r2_cache._key(d, f"servicetx_{d}.json"),
                           Body=path(d).read_bytes(), ContentType="application/json")
        bk = r2_cache._key(d, f"deepgram_{d}.json")
        try:
            dg = json.loads(cli.get_object(Bucket=bucket, Key=bk)["Body"].read())
        except Exception:
            dg = {}
        for rid in tx:
            f = ROOT / "data/deepgram" / f"{rid}.json"
            if rid not in dg and f.exists():
                dg[rid] = json.loads(f.read_text())
        cli.put_object(Bucket=bucket, Key=bk, Body=json.dumps(dg).encode(), ContentType="application/json")
        sd.publish(d, doc=doc, log=log)
        log(f"{d}: {len(doc['calls_tx'])} transcripts on the page "
            f"({len(front.get('calls') or [])} calls answered, {len(doc['dials'].get('rows') or [])} numbers dialled), "
            f"{up} recordings uploaded")
        # A month of recordings would fill the disk; they are in R2 now.
        for rid in tx:
            ap = ROOT / "data/audio" / f"{rid}.mp3"
            if ap.exists():
                ap.unlink()
        done.append(d)
    return done


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--backfill"]:
        backfill(args[1], args[2] if len(args) > 2 else args[1], force="--force" in args)
    else:
        for d in args:
            build(d)
