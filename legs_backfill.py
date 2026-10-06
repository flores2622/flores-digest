"""Call 1, Call 2 ... with their own outcomes, for cards read before Apollo
was asked (Frank, 2026-10-05: "are you able to re-read only multiple call
cards?" -- "yes set it up and run it").

From 2026-10-05 a card whose transcript holds two or more calls carries
`legs` from Apollo's own read (METHODOLOGY.md's "legs";
coaching_cards._legs). Cards read before that get it here, from ONE short
question per multi-call card over the transcript already on the card -- not
a re-read of the card, so nothing else on it changes. The rules are
METHODOLOGY.md's own text, cut out of it, so there is one definition. Each
call's clock time comes from the day's saved transcripts and RingCentral log
in R2 (call_summary._audio_legs, the same legs the nightly picked), blank
when they cannot be matched.

    python3 legs_backfill.py --backfill 2026-09-01 [end] [--force] [--live]

Backs each R2 day it changes up under backups/<today>-legs-backfill/ and adds
ONLY `legs` to the multi-call cards that lack it. Paid: one small read per
multi-call card (8 across 09-01..10-02, cents).
"""
import datetime as dt
import json
import sys

import call_summary as CS
import coaching_cards as cc

ROOT = CS.ROOT


def _rules():
    m = (ROOT / "coaching/METHODOLOGY.md").read_text()
    a = m[m.index('"legs"'):]
    a = a[:a.index('\n"', 1)]
    return ("You read one insurance sales transcript that holds two or more separate calls with the same lead, "
            "and judge each call's outcome on its own. The agency's rule:\n\n" + a
            + "\n\nAnswer as JSON only: {\"legs\": [[outcome, reason], ...]}, one entry per call header, in order.")


def _heads(transcript):
    return [(m.group(1), int(m.group(2)) * 60 + int(m.group(3))) for m in cc.LEG_HEAD.finditer(transcript or "")]


def read(card, model, rules=None):
    heads = _heads(card.get("transcript"))
    msg = (f"Producer: {card.get('who')}\nLead: {card.get('lead') or '(unknown)'}\n"
           f"This transcript holds {len(heads)} calls -- return `legs` with EXACTLY {len(heads)} entries, one per "
           f"header in order, even for a call of only a few words (judge it on what little was said).\nThe outcome the card gave the day as a whole: {card.get('catc') or '?'}\n"
           f"Coach's summary of the day: {card.get('summary') or ''}\n\n"
           f"Machine transcript:\n{str(card.get('transcript') or '')[:40000]}")
    body = {"model": model, "system": rules or _rules(), "max_tokens": 800,
            "messages": [{"role": "user", "content": msg}]}
    try:
        resp = CS._post(dict(body, thinking={"type": "disabled"}))
    except RuntimeError as e:
        if "thinking" not in str(e).lower():
            raise
        resp = CS._post(body)
    return (CS._extract(resp) or {}).get("legs")


def _legmeta(day, log):
    """producer|number -> [[direction, seconds, start]] for the legs the nightly read, from the day's saved
    transcripts and RC log (pulled from R2's cache/<day>/ if not on disk). {} when they are not there."""
    try:
        import r2_cache
        r2_cache.sync_down_day(day, log=lambda m: None)
        legs = CS._audio_legs(day)
    except Exception as e:
        log(f"  {day}: no saved call log for clock times ({type(e).__name__})")
        return {}
    return {CS._ck(p, n): [[w[3], w[1], w[6]] for w in CS._wanted(v)] for (p, n), v in legs.items()}


def _meta_for(card, legmeta):
    """Each header's own saved leg -- direction, length and start -- matched one call at a time across ALL of
    this producer's rows, since a card can join two rows (Mike / Maria Ortiz 09-02: three dials on one row, a
    call-in on another). A header with no match gets None, so its time stays blank."""
    pool = [m for k, meta in legmeta.items() if k.split("|")[0] == card.get("who") for m in meta]
    out = []
    for direction, secs in _heads(card.get("transcript")):
        hit = next((m for m in pool if m and m[0] == direction and abs((m[1] or 0) - secs) <= 1), None)
        if hit:
            pool[pool.index(hit)] = None
        out.append(hit or [direction, secs, None])
    return out


def _verdicts(said, n):
    """Apollo's per-call verdicts, only when there is one for every header."""
    return said if isinstance(said, list) and len(said) == n and all(
        isinstance(v, (list, tuple)) and v and v[0] in cc.cfg.CALL_CATEGORIES for v in said) else None


def backfill(start, end=None, force=False, log=print, batch=True, dry=False):
    """batch (the default): every read goes out first as one half-price Message Batch (call_summary.run_batch),
    then the loop runs for real and takes its answers from it. --live reads one by one at full price."""
    if batch and not dry:
        CS.run_batch(CS.collect(lambda: backfill(start, end, force, log=lambda m: None,
                                                 batch=False, dry=True)), log=log)

    import publish_board
    cli, bucket = publish_board._client()
    end = end or (dt.date.today() - dt.timedelta(days=1)).isoformat()
    model, rules = CS.pick_model(), _rules()
    stamp = dt.date.today().isoformat()
    total = 0
    d = dt.date.fromisoformat(start)
    while d.isoformat() <= end:
        day = d.isoformat(); d += dt.timedelta(days=1)
        key = f"days/{day}.json"
        try:
            doc = json.loads(cli.get_object(Bucket=bucket, Key=key)["Body"].read())
        except Exception:
            continue
        # a card whose legs carry no verdict (an earlier run that got the count wrong) is read again
        todo = [c for c in doc.get("calls") or []
                if len(_heads(c.get("transcript"))) > 1
                and (force or not any(l.get("oc") for l in c.get("legs") or []))]
        if not todo:
            continue
        legmeta = {} if dry else _legmeta(day, log)
        got = {}
        for c in todo:
            n_heads = len(_heads(c.get("transcript")))
            said = None
            for attempt in range(2):      # once more if the count came back wrong
                try:
                    raw = read(c, model, rules)
                    said = _verdicts(raw, n_heads)
                    if not said and not dry:
                        log(f"  {day} {c.get('who')} / {c.get('lead')}: answer {attempt + 1} not one verdict per call: "
                            + json.dumps(raw, default=str)[:600])
                except Exception as e:
                    log(f"  {day} {c.get('who')} / {c.get('lead')}: {type(e).__name__}: {str(e)[:120]}")
                if said or dry:
                    break
            if dry:
                continue
            if not said:
                log(f"  {day} {c.get('who')} / {c.get('lead')}: no verdict for each of its {n_heads} calls -- left as it was")
                continue
            # _legs matches legmeta by producer + number: hand it this card's own legs, in header order
            legs = cc._legs({"legs": said}, c.get("who"), [{"number": "card"}], c.get("transcript"),
                            {CS._ck(c.get("who"), "card"): _meta_for(c, legmeta)})
            got[(c.get("who"), c.get("lead_id"), c.get("time"))] = legs
            log(f"  {day} {c.get('who')} / {c.get('lead')}: "
                + " | ".join(f"Call {l['n']} {l['at'] or '?'} {l['dur']} {l.get('cat') or '(no verdict)'}" for l in legs))
        if dry or not got:
            continue
        bk = f"backups/{stamp}-legs-backfill/{key}"
        try:
            cli.head_object(Bucket=bucket, Key=bk)
        except Exception:
            cli.copy_object(Bucket=bucket, Key=bk, CopySource={"Bucket": bucket, "Key": key})
        # Re-read just before writing, so nothing another job saved meanwhile is lost; only `legs` is added.
        fresh = json.loads(cli.get_object(Bucket=bucket, Key=key)["Body"].read())
        n = 0
        for c in fresh.get("calls") or []:
            k = (c.get("who"), c.get("lead_id"), c.get("time"))
            if k in got:
                c["legs"] = got[k]
                n += 1
        cli.put_object(Bucket=bucket, Key=key, Body=json.dumps(fresh, default=str).encode(),
                       ContentType="application/json", CacheControl="no-store")
        total += n
        log(f"  {day}: legs added to {n} card(s)")
    if not dry:
        log(f"DONE: legs added to {total} card(s)")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--backfill"]:
        args = [a for a in sys.argv[2:] if not a.startswith("--")]
        lines = []
        def _log(m):
            print(m, flush=True)
            lines.append(m)
        try:
            backfill(args[0], args[1] if len(args) > 1 else None, force="--force" in sys.argv,
                     batch="--live" not in sys.argv, log=_log)
        except Exception as e:
            _log(f"FAILED: {type(e).__name__}: {e}")
            raise
        finally:
            # the run's own log, beside its backups, so it can be read after an unattended run
            import publish_board
            cli, bucket = publish_board._client()
            cli.put_object(Bucket=bucket, ContentType="text/plain",
                           Key=f"backups/{dt.date.today().isoformat()}-legs-backfill/run-"
                               f"{dt.datetime.utcnow().strftime('%H%M%S')}.log",
                           Body="\n".join(lines).encode())
    else:
        print(_rules())
