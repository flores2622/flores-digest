"""Give past days' coaching cards the synced recording + transcript (Frank,
2026-09-29: "do september's cards").

    python3 card_turns_backfill.py 2026-09-01 2026-09-28

Cards read before Deepgram was switched on (2026-09-29) have recordings but
no timed lines, so their player cannot jump to what is being read. For each
published day this reads each card's recordings with Deepgram ONCE (paid
per audio minute; cached like any other read, and the day's R2 bundle
cache/<day>/deepgram_<day>.json gets them too), then adds ONLY `turns` to
the day's cards -- exactly what coaching_cards._timed_turns puts on a card
today. Nothing else on the page changes: not the transcript Apollo read,
not a grade, not a figure, and not data/transcripts_<day>.json, so no
live/voicemail verdict moves. Each day's page is backed up first under
backups/<today>-card-turns/. A card that already has turns is left alone.
"""
import datetime as dt
import json
import pathlib
import sys

import deepgram_stt as DG

ROOT = pathlib.Path(__file__).resolve().parent


def _get(cli, bucket, key):
    try:
        return cli.get_object(Bucket=bucket, Key=key)["Body"].read()
    except Exception:
        return None


def backfill_day(cli, bucket, day, stamp, log=print):
    raw = _get(cli, bucket, f"days/{day}.json")
    if not raw:
        return 0, 0
    doc = json.loads(raw)
    todo = [c for c in doc.get("calls") or [] if c.get("recording_ids") and not c.get("turns")]
    if not todo:
        return 0, 0
    tx = json.loads(_get(cli, bucket, f"cache/{day}/transcripts_{day}.json") or b"{}")
    audio = ROOT / "data/audio"
    audio.mkdir(parents=True, exist_ok=True)
    got, secs = {}, 0
    for c in todo:
        turns = []
        for i, rid in enumerate(c["recording_ids"]):
            p = audio / f"{rid}.mp3"
            if not p.exists():
                body = _get(cli, bucket, f"cache/{day}/audio/{rid}.mp3")
                if not body:
                    continue
                p.write_bytes(body)
            v = tx.get(rid) or {}
            ts = DG.turns(p, v.get("audio_seconds") or v.get("duration") or 0,
                          offset=v.get("offset") or 0, producer=c.get("who"),
                          lead=c.get("lead") or "", log=log)
            if ts:
                turns += [dict(x, r=i) for x in ts]
            d = DG.raw(p, cached_only=True)
            secs += (d or {}).get("duration") or 0
        if turns:
            got[(c.get("who"), c.get("lead_id"), c.get("time"))] = turns
    # Deepgram's reads into the day's R2 bundle, merged with what is there.
    bundle = json.loads(_get(cli, bucket, f"cache/{day}/deepgram_{day}.json") or b"{}")
    for c in todo:
        for rid in c["recording_ids"]:
            f = ROOT / "data/deepgram" / f"{rid}.json"
            if f.exists() and rid not in bundle:
                bundle[rid] = json.loads(f.read_text())
    if bundle:
        cli.put_object(Bucket=bucket, Key=f"cache/{day}/deepgram_{day}.json",
                       Body=json.dumps(bundle).encode(), ContentType="application/json")
    if not got:
        return 0, secs
    bk = f"backups/{stamp}-card-turns/days/{day}.json"
    if not _get(cli, bucket, bk):
        cli.put_object(Bucket=bucket, Key=bk, Body=raw, ContentType="application/json")
    # Re-read just before writing, so nothing another job saved meanwhile is
    # lost; only `turns` is added.
    fresh = json.loads(_get(cli, bucket, f"days/{day}.json"))
    n = 0
    for c in fresh.get("calls") or []:
        k = (c.get("who"), c.get("lead_id"), c.get("time"))
        if k in got and not c.get("turns"):
            c["turns"] = got[k]
            n += 1
    cli.put_object(Bucket=bucket, Key=f"days/{day}.json",
                   Body=json.dumps(fresh, default=str).encode(),
                   ContentType="application/json", CacheControl="no-store")
    return n, secs


def main(start, end, log=print):
    import publish_board
    if not DG.available():
        raise SystemExit("DEEPGRAM_API_KEY is not set")
    cli, bucket = publish_board._client()
    stamp = dt.date.today().isoformat()
    d, total_cards, total_secs = dt.date.fromisoformat(start), 0, 0
    while d.isoformat() <= end:
        day = d.isoformat()
        d += dt.timedelta(days=1)
        n, secs = backfill_day(cli, bucket, day, stamp, log=log)
        total_cards += n
        total_secs += secs
        if n or secs:
            log(f"  {day}: {n} cards given timed lines ({secs / 60:.0f} min of audio)")
    log(f"done: {total_cards} cards, {total_secs / 60:.0f} min of audio read")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else sys.argv[1])
