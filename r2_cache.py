"""R2-backed cache for the raw materials daily.py/hourly.py/intraday.py pull,
so a fresh COLD container can pick up where an earlier one left off instead of
re-fetching, re-downloading and re-transcribing the whole day from scratch.

WHY THIS EXISTS. Every scheduled/triggered session gets a cold container --
`data/` is gitignored and does not survive between separate firings (see
hourly.py's own docstring, and CLAUDE.md's "THE RUN STARTS AT 5:35 PM" section
for how the single-session workaround works today). That was fine when the
whole day's work happened once, inside one long session. It stops being fine
the moment checks run repeatedly through the day across separate firings
(Frank, 2026-09-10 -- in practice the business-hour schedule these ride on
isn't evenly hourly at all, see HOURLY_RUNS.md's ten checkpoints): each
firing would re-download every recording an earlier firing already paid
RingCentral's throttled media endpoint for, so cost would climb with every
extra checkpoint instead of staying flat. This module is what makes it flat
-- push what a run produced, pull what an earlier run already produced, so a
checkpoint only ever pays for the DELTA since the last one.

WHAT LIVES HERE, AND WHAT DOES NOT.

  DAY-SCOPED (cache/<day>/<name>.json), safe to reuse across separate runs
  on the SAME day: rc_raw, rc_window, transcripts, fulltx, callsum,
  coaching_cards, metrics, az_service_tickets, az_tasks, audiorefs. All
  either day-locked snapshots or keyed per-call/per-lead, so re-using an
  earlier run's copy and only fetching what changed is always correct,
  never stale in a way that matters -- rc_raw/rc_window/az_service_tickets/
  az_tasks are still refreshed
  ON TOP of the cached copy while the day is in progress (see intraday.py and
  hourly.refresh_call_log/refresh_window), never served untouched.

  RECORDINGS (cache/<day>/audio/<id>.mp3): cached alongside transcripts so
  call_summary.py's fulltx stage -- which needs the actual audio, not just the
  transcript text -- still works even when it runs in a container that never
  itself downloaded that recording. Scoped to one day at a time; nothing here
  keeps a recording around after the day it was recorded, and this module
  never reads or writes a day's audio once transcribe_day() and
  call_summary.build() ORIGINALLY DID (both already skip work already in
  their own JSON caches) -- so old recordings are not permanently retained,
  only carried across the containers that touch this one day.

  DELIBERATELY NOT CACHED HERE: az_leads_all.json, az_customers_all.json,
  az_policies_all.json -- the whole AgencyZoom corpus. Caching THAT would
  reintroduce, at the R2 layer, the exact bug HANDOFF_12 #3 already named at
  the local-disk layer: a re-run silently serving an hours-stale corpus that
  hides a real sale. AgencyZoom's list APIs run at ~90 req/min (az_client.py),
  nowhere near RingCentral's 10-req/60s media throttle, so there is no cost
  reason to cache them -- daily.pull_sources() now fetches all three fresh on
  every call instead. That is a deliberate fix riding along with this change,
  not an oversight.

Persists to the SAME `flores-board` R2 bucket publish_board.py already
writes to (same account, same credentials), under a `cache/` prefix so it
never collides with `days/`, `months/`, `folios/` or `roleplay/`.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
PREFIX = "cache"

# name -> local path template. {day} is substituted by the day-scoped helpers.
DAY_FILES = [
    "rc_raw_{day}.json", "rc_window_{day}.json", "transcripts_{day}.json",
    "fulltx_{day}.json", "callsum_{day}.json", "coaching_cards_{day}.json",
    "metrics_{day}.json", "az_service_tickets_{day}.json", "az_tasks_{day}.json",
    "audiorefs_{day}.json",
]


def _client():
    """Reuse publish_board's exact R2 client/bucket rather than a second copy."""
    import publish_board
    return publish_board._client()


def _key(day, name):
    return f"{PREFIX}/{day}/{name}"


def _audio_key(day, call_id):
    return f"{PREFIX}/{day}/audio/{call_id}.mp3"


def sync_down_day(day, log=print):
    """Pull down whatever an earlier run already cached for this day.

    Only fills in files that are NOT already present locally -- never
    overwrites a file this container already has, so a run that is itself the
    one with the freshest data never gets clobbered by an older R2 copy.
    """
    cli, bucket = _client()
    pulled = []
    for name in DAY_FILES:
        fname = name.format(day=day)
        p = ROOT / "data" / fname
        if p.exists():
            continue
        try:
            body = cli.get_object(Bucket=bucket, Key=_key(day, fname))["Body"].read()
        except cli.exceptions.NoSuchKey:
            continue
        except Exception:
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(body)
        pulled.append(fname)

    # Audio: only the recordings this day's (possibly just-pulled) transcripts
    # file actually references -- never a bulk directory listing, so this
    # never pulls another day's leftover mp3s into the same local folder.
    tpath = ROOT / "data" / f"transcripts_{day}.json"
    if tpath.exists():
        ids = list(json.loads(tpath.read_text()).keys())
        audio_dir = ROOT / "data/audio"
        n = 0
        for cid in ids:
            ap = audio_dir / f"{cid}.mp3"
            if ap.exists():
                continue
            try:
                body = cli.get_object(Bucket=bucket, Key=_audio_key(day, cid))["Body"].read()
            except cli.exceptions.NoSuchKey:
                continue
            except Exception:
                continue
            audio_dir.mkdir(parents=True, exist_ok=True)
            ap.write_bytes(body)
            n += 1
        if n:
            pulled.append(f"audio/*.mp3 (+{n})")

    if pulled:
        log(f"  r2 cache: pulled {', '.join(pulled)}")
    return pulled


def sync_up_day(day, log=print):
    """Push whatever this run produced (or already had) back to R2, so the
    NEXT run -- this session's next business-hour check, or tonight's build
    in a genuinely fresh container -- doesn't pay to re-fetch it.

    PUTs unconditionally rather than checking first: these are the day's own
    JSON caches, small next to what re-fetching them would cost, and a PUT of
    unchanged bytes is harmless. Audio is the one case explicitly listed
    first (see below) to keep from re-uploading megabytes of unchanged mp3s
    on every check.
    """
    cli, bucket = _client()
    pushed = []
    for name in DAY_FILES:
        fname = name.format(day=day)
        p = ROOT / "data" / fname
        if not p.exists():
            continue
        cli.put_object(Bucket=bucket, Key=_key(day, fname), Body=p.read_bytes(),
                       ContentType="application/json")
        pushed.append(fname)

    # Keyed off rc_raw_<day>.json's own recording ids, not transcripts_<day>.json's
    # -- a strict superset, so a recording that DOWNLOADED but has not been
    # TRANSCRIBED yet still gets pushed (Frank, 2026-09-14: "what happened to
    # the intraday runs" -- every business-hour checkpoint is a fresh cold
    # container per HOURLY_RUNS.md's own finding, and the ~14-minute download
    # phase is by far the likeliest place for one to run out of time before
    # this function's caller ever reaches its OWN sync_up_day call. Keying on
    # transcripts.json meant a checkpoint killed mid-download pushed nothing
    # at all, so the next one paid to re-download every recording from zero.
    rc_path = ROOT / "data" / f"rc_raw_{day}.json"
    if rc_path.exists():
        ids = {r["id"] for r in json.loads(rc_path.read_text()) if r.get("id")}
        # Only upload ids not already in R2, one LIST instead of one HEAD per
        # file -- keeps a repeated push from re-sending the same megabytes of
        # audio an earlier check already sent.
        have = set()
        token = None
        prefix = f"{PREFIX}/{day}/audio/"
        while True:
            kw = {"Bucket": bucket, "Prefix": prefix}
            if token:
                kw["ContinuationToken"] = token
            page = cli.list_objects_v2(**kw)
            for o in page.get("Contents", []):
                have.add(o["Key"].rsplit("/", 1)[-1].removesuffix(".mp3"))
            if not page.get("IsTruncated"):
                break
            token = page.get("NextContinuationToken")

        audio_dir = ROOT / "data/audio"
        n = 0
        for cid in ids - have:
            ap = audio_dir / f"{cid}.mp3"
            if not ap.exists():
                continue
            cli.put_object(Bucket=bucket, Key=_audio_key(day, cid),
                           Body=ap.read_bytes(), ContentType="audio/mpeg")
            n += 1
        if n:
            pushed.append(f"audio/*.mp3 (+{n})")

    if pushed:
        log(f"  r2 cache: pushed {', '.join(pushed)}")
    return pushed


# ---- AgencyZoom snapshot, for rebuilding a past day as it was ----------------
#
# The three corpus files are pulled fresh on every run for TODAY, and that does
# not change: serving a saved copy as if it were current is HANDOFF_12 #3, which
# hid four real sales. A snapshot saved here is only ever READ to rebuild a day
# that has already ended, so `daily.py --day 2026-09-22` sees the leads,
# customers and policies the 09-22 report saw instead of whatever AgencyZoom
# says now (Frank, 2026-09-23: "go back and look at data as if we were still on
# that day"). Without it a rebuild drifts -- leads reassigned, merged or sold
# since -- which is why verify_finalize.py warns on any past day.
#
# Saved on every pull for today, so the last one of the day wins: the nightly
# build's, i.e. the copy the report was actually built from. ~26 MB raw, a few
# MB gzipped.
CORPUS_FILES = ("az_leads_all.json", "az_customers_all.json", "az_policies_all.json")


def _corpus_key(day, fname):
    return f"{PREFIX}/{day}/corpus/{fname}.gz"


def save_corpus(day, log=print):
    """Push today's freshly pulled corpus as <day>'s snapshot."""
    import gzip
    cli, bucket = _client()
    for fname in CORPUS_FILES:
        body = gzip.compress((ROOT / "data" / fname).read_bytes(), compresslevel=6)
        cli.put_object(Bucket=bucket, Key=_corpus_key(day, fname), Body=body,
                       ContentType="application/gzip")
    log(f"  r2 cache: saved AgencyZoom snapshot for {day}")


def load_corpus(day, log=print):
    """Restore <day>'s snapshot over data/. True only if ALL three were there --
    a partial set would mix one day's leads with another day's policies."""
    import gzip
    cli, bucket = _client()
    bodies = {}
    for fname in CORPUS_FILES:
        try:
            bodies[fname] = cli.get_object(
                Bucket=bucket, Key=_corpus_key(day, fname))["Body"].read()
        except cli.exceptions.NoSuchKey:
            return False
    for fname, body in bodies.items():
        (ROOT / "data" / fname).write_bytes(gzip.decompress(body))
    log(f"  r2 cache: restored the AgencyZoom snapshot saved for {day}")
    return True
