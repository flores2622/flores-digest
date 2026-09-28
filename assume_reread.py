"""Re-read "assumed the quote", "assumed the sale" and the "Assumptive
version" line on cards read before 2026-09-28's rules (Frank, 2026-09-28:
"yes, run it"): always assume, never ask; offering to send the quote is not
assuming it; no chance to assume is n/a; the fix keeps them on the phone
for the few minutes it takes to finish the quote.

One short read per FIRST or FINISH-QUOTE card over the transcript already
on it -- not a re-read of the card, so every other field stays as it was.
The rules are METHODOLOGY.md's own text, cut out of it.

    python3 assume_reread.py --backfill 2026-09-01 [end] [--force]

Backs each R2 day up under backups/<today>-assume-reread/, replaces only
askq / asks / askfix on those cards, recomputes the day's `scan`, and marks
each card `assume_reread` so a second run leaves it alone.
"""
import datetime as dt
import json
import pathlib
import sys

import call_summary as CS
import coaching_cards as cc

ROOT = pathlib.Path(__file__).resolve().parent


def _rules():
    m = (ROOT / "coaching/METHODOLOGY.md").read_text()
    a = m[m.index("- Distinguish an ASSUMPTIVE close"):m.index('- "Addressed" is about effort')]
    b = m[m.index('"askq"     [boolean'):m.index('"exit"     [boolean')]
    return ("You read one insurance sales call and answer three questions about it. "
            "The agency's rules:\n\n" + a
            + "\nAnswer as JSON only: {\"askq\": [...], \"asks\": [...], \"askfix\": \"...\"}, where\n" + b)


def due(card):
    """A first conversation or a call to finish the quote (a follow-up has
    no askq -- its sale is judged three times in `assume`)."""
    flow = (card.get("flow") or [""])[0] if isinstance(card.get("flow"), list) else ""
    return flow in ("first", "finish quote") or (not flow and card.get("askq") is not None)


def read(card, model, rules=None):
    flow = (card.get("flow") or [""])[0] if isinstance(card.get("flow"), list) else ""
    objs = "; ".join(f"{o.get('group') or o.get('cat')}: \"{o.get('they') or ''}\"" for o in card.get("objs") or [])
    msg = (f"Producer: {card.get('who')}\nLead: {card.get('lead') or '(unknown)'}\n"
           f"What the call was for: {flow or 'unknown'}; who dialled: {card.get('direction') or 'dialled'}\n"
           f"Length: {card.get('dur') or '?'}\n"
           f"Coach's summary of the call: {card.get('summary') or ''}\n"
           f"Objections the coach found: {objs or 'none'}\n\n"
           f"Machine transcript:\n{str(card.get('transcript') or '')[:16000]}")
    body = {"model": model, "system": rules or _rules(), "max_tokens": 700,
            "messages": [{"role": "user", "content": msg}]}
    try:
        resp = CS._post(dict(body, thinking={"type": "disabled"}))
    except RuntimeError as e:
        if "thinking" not in str(e).lower():
            raise
        resp = CS._post(body)
    d = CS._extract(resp)
    if not d or "askq" not in d or "asks" not in d:
        raise ValueError("no askq/asks in the answer")
    return cc._verdict(d.get("askq")), cc._verdict(d.get("asks")), str(d.get("askfix") or "").strip()


def backfill(start, end=None, force=False, log=print):
    import publish_board
    cli, bucket = publish_board._client()
    end = end or (dt.date.today() - dt.timedelta(days=1)).isoformat()
    model, rules = CS.pick_model(), _rules()
    stamp = dt.date.today().isoformat()
    d = dt.date.fromisoformat(start)
    while d.isoformat() <= end:
        day = d.isoformat(); d += dt.timedelta(days=1)
        key = f"days/{day}.json"
        try:
            doc = json.loads(cli.get_object(Bucket=bucket, Key=key)["Body"].read())
        except Exception:
            continue
        todo = [c for c in doc.get("calls") or [] if due(c) and (force or not c.get("assume_reread"))]
        if not todo:
            continue
        got, flips = {}, 0
        for c in todo:
            try:
                q, s, fix = read(c, model, rules)
            except Exception as e:
                log(f"  {day} {c.get('who')} / {c.get('lead')}: kept as it was ({type(e).__name__}: {str(e)[:100]})")
                continue
            flips += ((c.get("askq") or [None])[0] != q[0]) + ((c.get("asks") or [None])[0] != s[0])
            got[(c.get("who"), c.get("lead_id"), c.get("time"))] = (q, s, fix)
        if not got:
            continue
        bk = f"backups/{stamp}-assume-reread/{key}"
        try:
            cli.head_object(Bucket=bucket, Key=bk)
        except Exception:
            cli.copy_object(Bucket=bucket, Key=bk, CopySource={"Bucket": bucket, "Key": key})
        # Re-read just before writing so nothing another job saved meanwhile
        # is lost; only these three fields are carried over.
        fresh = json.loads(cli.get_object(Bucket=bucket, Key=key)["Body"].read())
        for c in fresh.get("calls") or []:
            k = (c.get("who"), c.get("lead_id"), c.get("time"))
            if k in got:
                c["askq"], c["asks"], c["askfix"] = got[k]
                c["assume_reread"] = stamp
        fresh["scan"] = cc.scan(fresh.get("calls") or [])
        cli.put_object(Bucket=bucket, Key=key, Body=json.dumps(fresh, default=str).encode(),
                       ContentType="application/json", CacheControl="no-store")
        sc = fresh["scan"] or {}
        log(f"  {day}: {len(got)} re-read, {flips} verdicts changed -- "
            f"opening asked permission {sc.get('asked_open')} of {sc.get('of_first')}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--backfill"]:
        args = [a for a in sys.argv[2:] if not a.startswith("--")]
        backfill(args[0], args[1] if len(args) > 1 else None, force="--force" in sys.argv)
    else:
        print(_rules())
