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

PERSISTENCE. Scheduled runs get a COLD container every time -- measured
2026-09-01, a marker written by one run was gone an hour later and uptime read
0 minutes. data/ does NOT survive on its own, so this script carries the one
file that matters, data/transcripts_<day>.json (32 KB), in the repository: it
pulls at the start of a run and commits at the end.

If the commit cannot be pushed the run still completes, but every later run
that day re-downloads the whole day. It says so loudly rather than quietly
burning the RingCentral media quota.

Inbound calls are deliberately NOT screened here -- see transcribe_day's
outbound_only. Screening them needs the whole AgencyZoom corpus and a 31-day
RingCentral window, about eight minutes, which in a cold container would be
paid ten times a day to classify roughly three calls. The nightly build does
inbound itself.
"""
import argparse
import datetime as dt
import json
import pathlib
import subprocess

import daily

AZ = dt.timezone(dt.timedelta(hours=-7))
ROOT = pathlib.Path(__file__).resolve().parent
log = daily.log


TRANSCRIPTS = "data/transcripts_{day}.json"


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT,
                          capture_output=True, text=True)


def pull_transcripts(dry=False):
    """Bring in whatever an earlier run committed today."""
    if dry:
        log("  [dry-run] would git pull")
        return
    r = git("pull", "--ff-only", "--quiet")
    if r.returncode:
        log(f"  git pull failed: {(r.stderr or '').strip()[:160]}")


def commit_transcripts(day, dry=False):
    """Carry the transcript file forward.

    data/ is gitignored for good reason -- the audio and the AgencyZoom corpus
    run to hundreds of megabytes. This one 32 KB file is force-added past the
    ignore rule because it is the only thing worth keeping.
    """
    f = TRANSCRIPTS.format(day=day)
    if dry or not (ROOT / f).exists():
        return None
    git("add", "-f", f)
    if git("diff", "--cached", "--quiet").returncode == 0:
        log("  nothing new to commit")
        return True
    git("-c", "user.name=Flores hourly prefetch",
        "-c", "user.email=frank.automation@floresinsuranceagency.com",
        "commit", "-m", f"Transcripts for {day}, hourly prefetch")
    r = git("push")
    if r.returncode:
        log("  !! COULD NOT SAVE THE TRANSCRIPTS -- the next run starts from "
            "nothing and re-downloads the whole day.")
        log(f"     {(r.stderr or '').strip()[:200]}")
        log("     Fix: add flores2622/flores-digest to this task's sources. "
            "Until then the schedule wastes RingCentral quota -- pause it.")
        return False
    log(f"  saved {f} for the next run")
    return True


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

    pull_transcripts(a.dry_run)
    if tf.exists():
        prior = len(json.loads(tf.read_text()))
        log(f"  AFTER PULL: prior transcripts {prior}")

    before, after = refresh_call_log(day, a.dry_run)
    log(f"  call log: {before} -> {after} records")

    if a.dry_run:
        log("[dry-run] stopping before download/transcribe")
        return

    daily.ensure_model()
    done = daily.transcribe_day(day, outbound_only=True)
    commit_transcripts(day, a.dry_run)

    new = len(done) - prior
    log(f"DONE: {len(done)} transcripts on file (+{new} this run)")
    if new > 40:
        log(f"  NOTE: {new} in one run is high. Either a fire was missed or "
            f"the cache was lost; expect ~24 on a normal hour.")


if __name__ == "__main__":
    main()
