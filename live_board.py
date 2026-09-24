"""What the board needs to keep today's numbers live between checkpoints
(Frank, 2026-09-24: "just live data where its already at on everything
possible, and the header up there specifying what is stale from the last
hourly run").

A checkpoint (intraday.py) is the checked figure: every dial classified,
every transcript read. Between checkpoints the board's Worker
(site/worker.js, /api/live/<day>) keeps three things current straight from
the source, by the same rules:

  * DIALS -- RingCentral's call log. The Worker never re-decides which dials
    count; it takes this checkpoint's own verdict per number and only adds
    the calls made since. A number the checkpoint excluded (service, renewal,
    no record) stays excluded; a duplicate-lead number adds attempts to its
    person but no second contact; a number nobody has checked yet counts as
    new business until the next checkpoint checks it. So a live dial count
    equals the checkpoint's own at the moment it was built, and the next
    checkpoint settles whatever came in between.
  * SALES -- AgencyZoom policies by agentId + soldDate, BOB and Rewrite
    excluded: the lead-source sets below come from lead_sources.py, so the
    Worker applies exactly the rule digest_config.is_real_sale does.
  * UTILIZATION -- Insightful, same formula as insightful_util.pull().

Everything else -- contact rate, live contacts, talk time, outcomes, quotes,
tasks, speed to dial, the leaderboard, coaching cards -- needs a transcript
or a note read, so it stays the checkpoint's, and the board says so.

`basis(day)` is published inside the intraday document (publish_board.build,
live=True only), so the Worker needs nothing but R2 and the three services.
"""
import datetime as dt
import json
import pathlib

import day_calls
import digest_config as cfg
import lead_sources

ROOT = pathlib.Path(__file__).resolve().parent


def basis(day):
    """The checkpoint's own verdicts, for the Worker to extend. None when the
    day's metrics or call log aren't on disk (the board then just shows the
    checkpoint, as it always has)."""
    mpath = ROOT / f"data/metrics_{day}.json"
    rpath = ROOT / f"data/rc_raw_{day}.json"
    if not (mpath.exists() and rpath.exists()):
        return None
    M = json.loads(mpath.read_text())
    recs = json.loads(rpath.read_text())
    dialled = day_calls.dials_from(recs)          # {producer: {number: [records]}}

    counted, dropped, excluded = {}, {}, {}
    for who in cfg.PRODUCERS:
        rows = (M.get("producers", {}).get(who) or {}).get("dials") or []
        keep = {d["number"] for d in rows if not d.get("dropped")}
        # Only a DUPLICATE-LEAD drop keeps its attempts: daily.py moves them
        # onto the same person's surviving number (one person, one contact,
        # every attempt). A dial the service/renewal read dropped counts for
        # nothing (finalize.py), exactly like one never classified as new
        # business -- so it joins `excluded`.
        drop = {d["number"] for d in rows
                if str(d.get("dropped") or "").startswith("duplicate lead")}
        seen = set(dialled.get(who, {}))
        counted[who] = sorted(keep)
        dropped[who] = sorted(drop)
        # Dialled but not counted: service, renewal, no record, a test lead
        # (day_calls.classify), or dropped by the service/renewal read.
        excluded[who] = sorted(seen - keep - drop)

    return {
        "day": day,
        # Every call record this checkpoint already counted, so the Worker
        # adds only records it has not seen -- by id, not by time, since a
        # call still in progress at the checkpoint is logged later with an
        # earlier start time.
        "rc_ids": sorted({str(r.get("id")) for r in recs if r.get("id")}),
        "counted": counted,
        "dropped": dropped,
        "excluded": excluded,
        "producers": {n: {"rc_id": v["rc_id"], "az_id": v["az_id"]}
                      for n, v in cfg.PRODUCERS.items()},
        "not_a_sale": sorted(lead_sources.NOT_A_SALE),
        "existing_household": sorted(lead_sources.EXISTING_HOUSEHOLD),
        "util_exclude": sorted(_util_exclude()),
        "quotes": _quote_basis(M),
        "business_hours": [f"{cfg.BUSINESS_START_HOUR:02d}:{cfg.BUSINESS_START_MIN:02d}",
                           f"{cfg.BUSINESS_END_HOUR:02d}:{cfg.BUSINESS_END_MIN:02d}"],
    }


def _quote_basis(M):
    """What the Worker needs to keep households and premium quoted live:
    the checkpoint's own quoted leads per producer (daily.py's `hh`), when
    the lead activity was read (anything active since is re-checked), and
    daily.py's own quote rules as regex source, so the Worker applies the
    very same patterns rather than a copy that can drift. None for a
    checkpoint built before daily.py kept the lead ids."""
    import daily
    per = {who: (M.get("producers", {}).get(who) or {}) for who in cfg.PRODUCERS}
    if any("quoted_leads" not in v for v in per.values() if v):
        return None
    corpus = ROOT / "data/az_leads_all.json"
    if not corpus.exists():
        return None
    # The lead corpus is refetched at the start of every checkpoint and the
    # notes are read after it, so everything active from a little before
    # that fetch on is re-checked; the overlap only costs a re-read, since
    # leads already counted are skipped.
    since = dt.datetime.fromtimestamp(corpus.stat().st_mtime, dt.timezone.utc) - dt.timedelta(minutes=10)
    return {
        "quoted_leads": {who: v.get("quoted_leads") or [] for who, v in per.items()},
        # lead lastActivityDate is UTC, "YYYY-MM-DD HH:MM:SS"
        "activity_since": since.strftime("%Y-%m-%d %H:%M:%S"),
        "stage_pattern": daily.QUOTED_STAGE.pattern,
        "presented_pattern": daily._PRESENTED.pattern,
        "past_pattern": daily._PAST.pattern,
    }


def _util_exclude():
    try:
        from insightful_client import TEAM_UTIL_EXCLUDE
        return set(TEAM_UTIL_EXCLUDE)
    except Exception:
        return {"Amanda Torricellas"}


if __name__ == "__main__":
    import sys
    b = basis(sys.argv[1])
    if not b:
        print("no metrics/call log on disk for that day")
    else:
        print(f"{len(b['rc_ids'])} call records seen")
        for who in b["counted"]:
            print(f"  {who:16s} counted {len(b['counted'][who]):3d}  "
                  f"dropped {len(b['dropped'][who]):2d}  excluded {len(b['excluded'][who]):3d}")
