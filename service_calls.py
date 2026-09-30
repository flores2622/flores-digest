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
        if clean != t:
            hit = True
        out.append(dict(x, text=clean))
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


if __name__ == "__main__":
    for d in sys.argv[1:]:
        build(d)
