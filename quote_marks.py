"""Which quotes are new: premium quoted counts only what was quoted in the
last day (Frank, 2026-10-12: "make a rule to not include old premium? only
anything quoted in the last day" -- Mike / Adrian Alcantara Renteria showed
$3,664 for a $1,340 home quote, the rest an auto and home from May).

AgencyZoom puts no date on a quote -- not on the record, not in the API --
but it numbers quotes in the order they are made (an old Home 5,051,698; the
10-09 quotes ~15.59M; 10-12's 15,603,743). So every run notes the highest
quote id it read that day (the marks), and a day counts a quote when

  * it was made in the last WINDOW business days -- its id is above the mark
    of the run-day WINDOW-1 run-days back (`window_mark`), and
  * no earlier day has already counted it (`counted_before`).

The window is three days, not one (Frank, 2026-10-15: Coral's Ryan Baker and
Jose Tulao, $2,008 and $1,423, built on 10-13 and presented on 10-14, read $0
on 10-14 -- the one-day rule counted them on no day at all, since their
households were first quoted the day after). The counted record is what
stops a quote counting twice when its household is quoted again.

The marks are {day: highest quote id read}, data/quote_marks.json + an R2
copy; the counted record is {quote id: day}, data/quote_counted.json + an R2
copy, the last COUNTED_DAYS days. Only a run for today writes either: a
rebuild of a past day reads quotes as they are now. A day with no mark far
enough back counts every quote it has not counted before, and says so.

Careful: a lead's own record (GET /v1/api/leads/<id>) lists its quotes under
other numbers (Dayanne Martinez's read 3,730,646 there and 15,650,391 from
/v1/api/leads/<id>/quotes). The marks are the /quotes list's numbers, which
is all daily.py and the Worker read.
"""
import datetime
import json
import pathlib

import staff

ROOT = pathlib.Path(__file__).resolve().parent
FILE = ROOT / "data/quote_marks.json"
R2_KEY = "cache/quote_marks.json"
COUNTED_FILE = ROOT / "data/quote_counted.json"
COUNTED_KEY = "cache/quote_counted.json"
WINDOW = 3            # business days a quote may wait to be presented, today included
COUNTED_DAYS = 45     # how long the counted record keeps a quote


def _r2_json(key, path):
    try:
        import publish_board
        cli, bucket = publish_board._client()
        return json.loads(cli.get_object(Bucket=bucket, Key=key)["Body"].read())
    except Exception:
        return json.loads(path.read_text()) if path.exists() else {}


def _save(key, path, data, log):
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, sort_keys=True))
    try:
        import publish_board
        cli, bucket = publish_board._client()
        cli.put_object(Bucket=bucket, Key=key, Body=path.read_bytes(), ContentType="application/json")
    except Exception as e:
        log(f"  quote marks: R2 copy of {path.name} not saved ({type(e).__name__})")


def load():
    return {d: int(v) for d, v in _r2_json(R2_KEY, FILE).items()}


def load_counted():
    return {str(k): v for k, v in _r2_json(COUNTED_KEY, COUNTED_FILE).items()}


def mark_before(day, ledger=None):
    """The highest quote id seen on any day before `day`, or None."""
    led = load() if ledger is None else ledger
    earlier = [v for d, v in led.items() if d < day]
    return max(earlier) if earlier else None


def window_mark(day, ledger=None, window=WINDOW):
    """The highest quote id seen before the window: on run-days earlier than
    the last window-1 run-days before `day`. A quote above it was made in the
    window. None when the marks do not reach back that far."""
    led = load() if ledger is None else ledger
    earlier = sorted(d for d in led if d < day)
    keep = earlier[:-(window - 1)] if window > 1 else earlier
    return max(led[d] for d in keep) if keep else None


def counted_before(day, counted=None):
    """The quote ids an earlier day already counted."""
    c = load_counted() if counted is None else counted
    return {k for k, d in c.items() if d < day}


def is_new(quote, mark, counted=()):
    """A quote made in the window (every quote when there is no mark) and not
    counted on an earlier day."""
    qid = quote.get("id")
    if counted and str(qid) in counted:
        return False
    if mark is None:
        return True
    try:
        return int(qid) > mark
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
    _save(R2_KEY, FILE, led, log)


def record(day, ids, log=print):
    """Record the quotes `day` counted, so no later day counts them again.
    Today only; drops what is older than COUNTED_DAYS."""
    ids = [str(i) for i in ids if str(i).isdigit()]
    if not ids or day != staff.today():
        return
    c = load_counted()
    if all(c.get(i) == day for i in ids):
        return
    for i in ids:
        c.setdefault(i, day)
    floor = (datetime.date.fromisoformat(day) - datetime.timedelta(days=COUNTED_DAYS)).isoformat()
    c = {k: d for k, d in c.items() if d >= floor}
    _save(COUNTED_KEY, COUNTED_FILE, c, log)
