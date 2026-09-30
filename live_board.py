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

  * QUOTES -- households and premium quoted, daily.py's three rules.
  * CONTACTS AND TALK TIME -- a dial since the checkpoint is judged from the
    notes the quotes part already reads, then how long it ran
    (PROVISIONAL_LIVE_SECONDS); answered call-ins add talk time, and a call
    back turns its dial live. Provisional: the checkpoint reads the
    recordings and settles every one.
  * TEXTS AND EMAILS -- messages.build's rules on the same notes, carried on
    from the checkpoint's own per-person state (messages.live_basis).

Everything else -- outcomes, tasks, speed to dial, coaching cards -- needs a
transcript or a model read, so it stays the checkpoint's.

`basis(day)` is published inside the intraday document (publish_board.build,
live=True only), so the Worker needs nothing but R2 and the three services.
"""
import datetime as dt
import json
import pathlib

import day_calls
import sales_log_auto
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

    counted, dropped, excluded, live, talk = {}, {}, {}, {}, {}
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
        # Contacts and talk time (finalize._totals): which counted numbers
        # are already live, and the conversations behind Avg Talk Time --
        # every Call Detail row, inbound included, on a number not dropped.
        live[who] = sorted(d["number"] for d in rows if not d.get("dropped") and d.get("live"))
        gone = {d["number"] for d in rows if d.get("dropped")}
        convos = [r for r in ((M.get("producers", {}).get(who) or {}).get("call_detail") or [])
                  if r.get("number") not in gone]
        talk[who] = {"seconds": sum(r.get("seconds") or 0 for r in convos),
                     "conversations": len(convos),
                     "numbers": sorted({r["number"] for r in convos if r.get("number")})}

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
        "live": live,
        "talk": talk,
        "contact": _contact_basis(),
        "tasks": _task_basis(day),
        "producers": {n: {"rc_id": v["rc_id"], "az_id": v["az_id"]}
                      for n, v in cfg.PRODUCERS.items()},
        "not_a_sale": sorted(lead_sources.NOT_A_SALE),
        "existing_household": sorted(lead_sources.EXISTING_HOUSEHOLD),
        "util_exclude": sorted(_util_exclude()),
        # The Sales sheet's auto rows (sales_log_auto), so the Worker adds a
        # live sale to the sheet with the same people and product names.
        "saleslog": {
            "ids": {str(k): v for k, v in sales_log_auto._ids().items()},
            "carrier": {str(k): v for k, v in sales_log_auto.CARRIER.items()},
        },
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


# How long a dial made since the checkpoint must run, with nothing written
# on the lead, for the board to show it as a contact until the next
# checkpoint reads the recording. Measured 2026-09-28 on every counted dial
# of 09-22..09-25 (687 with their notes; 66 live by the checkpoints' own
# verdicts), applying is_live's order with the recording left out:
#
#     notes alone         16 shown   (10 right)     real 66
#     notes + 45s                     day totals 32/16/14/19 vs 31/11/11/13
#     notes + 60s         64 shown   (44 right)     day totals 27/12/12/13
#     notes + 90s         48 shown   (36 right)     day totals 21/9/8/10
#
# Sixty seconds keeps the day's count where the recordings put it; about a
# third of the individual calls it picks are wrong either way, which is why
# it is provisional and the checkpoint settles every one. Duration alone
# (no notes) at 60s showed 474 against a real 303 over September.
PROVISIONAL_LIVE_SECONDS = 60


def _contact_basis():
    """live_contact's note rules as regex source, for the Worker's
    provisional read of a dial made since the checkpoint (site/live.js
    contactsLive) -- the same patterns, never retyped in JS."""
    import live_contact as lc
    import re
    rx = lambda r: [r.pattern, "i" if r.flags & re.I else ""]
    return {"rx": {k: rx(getattr(lc, k)) for k in (
        "NEGATIVE", "SCREENER", "SYSTEM", "DATA_ONLY", "CONTACT_VERB",
        "TRAQ_NOTE", "TRAQ_VOICEMAIL", "ASSERTS_CONTACT", "NOT_AN_OUTCOME",
        "TASK_COMPLETED_BY", "TASK_BOILERPLATE")},
        "rc_no_connect": sorted(lc.RC_NO_CONNECT),
        "min_contact_seconds": lc.MIN_CONTACT_SECONDS,
        "provisional_seconds": PROVISIONAL_LIVE_SECONDS,
    }


def _task_basis(day):
    """What the Worker needs to keep Task Completion live (site/live.js
    tasksLive): az_tasks.audit's exclusion patterns and task_audit's
    cancellation patterns as regex source, and this checkpoint's own
    verdicts on the tasks it saw closed (duplicate lead -> excluded,
    smart-cycled by the producer -> excused). A task closed after the
    checkpoint is judged by the same patterns on the lead's stage moves."""
    import re
    import task_audit
    rx = lambda r: [r.pattern, "i" if r.flags & re.I else ""]
    verdicts, customers = {}, []
    path = ROOT / f"data/az_tasks_{day}.json"
    if path.exists():
        tasks = json.loads(path.read_text())
        try:
            verdicts = task_audit.cancellation_verdicts(
                day, tasks, {v["az_id"]: k for k, v in cfg.PRODUCERS.items()})
        except Exception:
            verdicts = {}
        # Which records the tasks hang off are customers, not leads -- the
        # lead corpus decides, as digest_rows / task_audit._link do, because
        # customerType is wrong on a few rows. For the list's links only.
        corpus = ROOT / "data/az_leads_all.json"
        if corpus.exists():
            lead_ids = {l.get("id") for l in json.loads(corpus.read_text())}
            customers = sorted({t["customerId"] for t in tasks
                                if t.get("customerId") and t["customerId"] not in lead_ids})
    return {
        "verdicts": {str(k): v for k, v in verdicts.items()},
        "customers": customers,
        "rx": {"title": rx(cfg.SERVICE_TITLE_RE), "body": rx(cfg.SERVICE_BODY_RE),
               "loss": rx(task_audit.LOSS_RE), "duplicate": rx(task_audit.LOSS_DUPLICATE_RE),
               "cycle": rx(task_audit.SMART_CYCLE_RE)},
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
