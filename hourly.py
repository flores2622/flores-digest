"""Hourly prefetch: pull today's calls, download and transcribe them.

    python3 hourly.py                # today, Arizona
    python3 hourly.py --day 2026-09-01
    python3 hourly.py --dry-run      # report what it WOULD do, fetch nothing

Why this exists. The evening build spends about thirty minutes doing nothing
but downloading call recordings: the agency averages 238 a day (peak 298) and
RingCentral's media endpoint allows ten requests per rolling sixty seconds, so
the downloader paces at 8/min and there is no way to make one big run faster.
Measured 2026-09-01 the whole nightly run took 1h24m.

Spread across the ten runs in HOURLY_RUNS.md it is roughly 24 recordings per
fire, about three minutes each, and by 5:15pm the evening build finds
everything already transcribed.

This script does NOT build or send anything. It only fills the cache.

IT DOES NOTHING USEFUL UNLESS data/ SURVIVES BETWEEN RUNS. See the
"persistence" note in HOURLY_RUNS.md section 12. Every run prints what it found
on arrival, so the first two fires answer that question by themselves --
`prior transcripts: 0` on the second fire of the day means the cache is being
thrown away and the schedule is pointless until that is fixed.
"""
import argparse
import datetime as dt
import json
import pathlib

import daily

AZ = dt.timezone(dt.timedelta(hours=-7))
ROOT = pathlib.Path(__file__).resolve().parent
log = daily.log


def refresh_call_log(day, dry=False):
    """Re-pull today's call log. Unlike daily.pull_sources this OVERWRITES.

    daily.pull_sources guards the fetch with `if not f.exists()`, which is
    right for a finished day and wrong for one still in progress -- the 9:50
    file would still be serving the 8:35 snapshot at 4pm and every call after
    breakfast would be invisible.
    """
    from rc_client import RingCentral
    nxt = (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat()
    f = ROOT / f"data/rc_raw_{day}.json"
    before = len(json.loads(f.read_text())) if f.exists() else 0
    if dry:
        log(f"  [dry-run] would re-pull the call log (have {before} records)")
        return before, before
    recs = RingCentral().call_log(f"{day}T00:00:00-07:00",
                                  f"{nxt}T00:00:00-07:00")
    f.write_text(json.dumps(recs))
    return before, len(recs)


def refresh_window(day, dry=False):
    """Keep rc_window_<day>.json current without re-walking 31 days.

    The recontact window is a month of daily chunks and costs ~32 requests to
    build. Only TODAY's chunk changes during the day, so merge today's records
    into the existing file instead of rebuilding it. If the file is missing --
    a genuinely cold container -- hand off to daily.pull_sources, which knows
    how to build it properly.
    """
    wf = ROOT / f"data/rc_window_{day}.json"
    rf = ROOT / f"data/rc_raw_{day}.json"
    if not wf.exists():
        log("  recontact window missing; building it (about 32 requests)")
        if dry:
            log("  [dry-run] skipped")
            return
        daily.pull_sources(day)
        return
    win = json.loads(wf.read_text())
    seen = {r.get("id") for r in win}
    fresh = [r for r in json.loads(rf.read_text()) if r.get("id") not in seen]
    if fresh and not dry:
        win.extend(fresh)
        wf.write_text(json.dumps(win))
    log(f"  recontact window: +{len(fresh)} today")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    day = a.day or dt.datetime.now(AZ).date().isoformat()

    (ROOT / "data").mkdir(exist_ok=True)
    tf = ROOT / f"data/transcripts_{day}.json"
    prior = len(json.loads(tf.read_text())) if tf.exists() else 0
    audio = ROOT / "data/audio"
    n_audio = len(list(audio.glob("*.mp3"))) if audio.exists() else 0

    log(f"hourly prefetch for {day}")
    log(f"  ON ARRIVAL: prior transcripts {prior}, cached audio files {n_audio}")
    if prior == 0 and n_audio == 0:
        log("  cache is EMPTY -- either this is the first run of the day or "
            "data/ did not survive the last one. See HOURLY_RUNS.md s12.")

    before, after = refresh_call_log(day, a.dry_run)
    log(f"  call log: {before} -> {after} records")
    refresh_window(day, a.dry_run)

    if a.dry_run:
        log("[dry-run] stopping before download/transcribe")
        return

    daily.ensure_model()
    done = daily.transcribe_day(day)

    new = len(done) - prior
    log(f"DONE: {len(done)} transcripts on file (+{new} this run)")
    if new > 40:
        log(f"  NOTE: {new} in one run is high. Either a fire was missed or "
            f"the cache was lost; expect ~24 on a normal hour.")


if __name__ == "__main__":
    main()
