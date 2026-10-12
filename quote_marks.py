"""Which quotes are new: premium quoted counts only what was quoted in the
last day (Frank, 2026-10-12: "make a rule to not include old premium? only
anything quoted in the last day" -- Mike / Adrian Alcantara Renteria showed
$3,664 for a $1,340 home quote, the rest an auto and home from May).

AgencyZoom puts no date on a quote -- not on the record, not in the API --
but it numbers quotes in the order they are made (an old Home 5,051,698; the
10-09 quotes ~15.59M; 10-12's 15,603,743). So every run notes the highest
quote id it read that day, and a day counts only quotes above the highest
id noted on any EARLIER day: what was entered since the last business day.

The ledger is {day: highest quote id read}, data/quote_marks.json + an R2
copy. Only a run for today writes to it: a rebuild of a past day reads
quotes as they are now, which would set that day's mark too high. A day
with no earlier mark counts every quote, as before, and says so.
"""
import json
import pathlib

import staff

ROOT = pathlib.Path(__file__).resolve().parent
FILE = ROOT / "data/quote_marks.json"
R2_KEY = "cache/quote_marks.json"


def load():
    try:
        import publish_board
        cli, bucket = publish_board._client()
        led = json.loads(cli.get_object(Bucket=bucket, Key=R2_KEY)["Body"].read())
    except Exception:
        led = json.loads(FILE.read_text()) if FILE.exists() else {}
    return {d: int(v) for d, v in led.items()}


def mark_before(day, ledger=None):
    """The highest quote id seen on any day before `day`, or None."""
    led = load() if ledger is None else ledger
    earlier = [v for d, v in led.items() if d < day]
    return max(earlier) if earlier else None


def is_new(quote, mark):
    """A quote made since the mark (every quote when there is no mark)."""
    if mark is None:
        return True
    try:
        return int(quote.get("id")) > mark
    except (TypeError, ValueError):
        return True


def note(day, ids, log=print):
    """Record the highest quote id read today. Past days are never written."""
    ids = [int(i) for i in ids if str(i).isdigit()]
    if not ids or day != staff.today():
        return
    led = load()
    if led.get(day, 0) >= max(ids):
        return
    led[day] = max(ids)
    FILE.parent.mkdir(exist_ok=True)
    FILE.write_text(json.dumps(led, sort_keys=True))
    try:
        import publish_board
        cli, bucket = publish_board._client()
        cli.put_object(Bucket=bucket, Key=R2_KEY, Body=FILE.read_bytes(), ContentType="application/json")
    except Exception as e:
        log(f"  quote marks: R2 copy not saved ({type(e).__name__})")
