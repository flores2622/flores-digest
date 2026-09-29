"""Quote sent instead of kept on the phone, for cards read before Apollo was
asked (Frank, 2026-09-28: "can you show me how many times the producers
offer to send the quote on their own instead of keeping that lead on the
phone? and I want to add that stat to the coaching center in the wins and
losses").

From 2026-09-28 every card read carries `sendoff` from Apollo's own read
(METHODOLOGY.md's "sendoff"). Cards read before that get it here, from ONE
short question per card over the transcript already on the card -- not a
re-read of the card, so nothing else on it changes. The rules are
METHODOLOGY.md's own text, cut out of it, so there is one definition.

    python3 sendoff.py --backfill 2026-09-01 [end] [--force]

Backs each R2 day up under backups/<today>-sendoff-backfill/ and adds ONLY
`sendoff` to the cards that lack it. Paid: one small read per card (~$1-2
for September).
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
    a = m[m.index("- Assuming the quote means"):m.index("- ALWAYS ASSUME, NEVER ASK")]
    b = m[m.index('"sendoff"'):m.index('"askfix"')]
    return ("You read one insurance sales call and answer one question. The agency's rules:\n\n"
            + a + "\nAnswer as JSON only: {\"sendoff\": [verdict or null, reason]}, where\n" + b)


def read(card, model, rules=None):
    flow = (card.get("flow") or [""])[0] if isinstance(card.get("flow"), list) else ""
    msg = (f"Producer: {card.get('who')}\nLead: {card.get('lead') or '(unknown)'}\n"
           f"What the call was for: {flow or 'unknown'}; who dialled: {card.get('direction') or 'dialled'}\n"
           f"Length: {card.get('dur') or '?'}\n"
           f"Coach's summary of the call: {card.get('summary') or ''}\n\n"
           f"Machine transcript:\n{str(card.get('transcript') or '')[:16000]}")
    body = {"model": model, "system": rules or _rules(), "max_tokens": 400,
            "messages": [{"role": "user", "content": msg}]}
    try:
        resp = CS._post(dict(body, thinking={"type": "disabled"}))
    except RuntimeError as e:
        if "thinking" not in str(e).lower():
            raise
        resp = CS._post(body)
    d = CS._extract(resp) or {}
    return cc._sendoff(d.get("sendoff"))


def backfill(start, end=None, force=False, log=print, batch=True, dry=False):
    """batch (the default): every read goes out first as one half-price
    Message Batch (call_summary.run_batch), then the loop runs for real and
    takes its answers from it. --live reads one by one at full price."""
    if batch and not dry:
        CS.run_batch(CS.collect(lambda: backfill(start, end, force, log=lambda m: None,
                                                 batch=False, dry=True)), log=log)

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
        cards = doc.get("calls") or []
        todo = [c for c in cards if force or "sendoff" not in c]
        if not todo:
            continue
        n = 0
        for c in todo:
            try:
                c["sendoff"] = read(c, model, rules)
                n += 1
            except Exception as e:
                log(f"  {day} {c.get('who')} / {c.get('lead')}: {type(e).__name__}: {str(e)[:120]}")
        if dry:
            continue
        bk = f"backups/{stamp}-sendoff-backfill/{key}"
        try:
            cli.head_object(Bucket=bucket, Key=bk)
        except Exception:
            cli.copy_object(Bucket=bucket, Key=bk, CopySource={"Bucket": bucket, "Key": key})
        # Re-read just before writing, so nothing another job saved meanwhile
        # is lost; only `sendoff` is carried over.
        fresh = json.loads(cli.get_object(Bucket=bucket, Key=key)["Body"].read())
        got = {(c.get("who"), c.get("lead_id"), c.get("time")): c.get("sendoff") for c in todo if "sendoff" in c}
        for c in fresh.get("calls") or []:
            k = (c.get("who"), c.get("lead_id"), c.get("time"))
            if k in got:
                c["sendoff"] = got[k]
        cli.put_object(Bucket=bucket, Key=key, Body=json.dumps(fresh, default=str).encode(),
                       ContentType="application/json", CacheControl="no-store")
        kinds = {}
        for c in fresh.get("calls") or []:
            k = (c.get("sendoff") or ["n/a"])[0]
            kinds[k] = kinds.get(k, 0) + 1
        log(f"  {day}: {n} read -- " + ", ".join(f"{k} {v}" for k, v in sorted(kinds.items())))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--backfill"]:
        args = [a for a in sys.argv[2:] if not a.startswith("--")]
        backfill(args[0], args[1] if len(args) > 1 else None, force="--force" in sys.argv,
                 batch="--live" not in sys.argv)
    else:
        print(_rules())
