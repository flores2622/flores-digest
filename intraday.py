"""Intraday snapshot: the day's numbers so far, checked and published at each
business-hour check through the day.

    python3 intraday.py                # today, Arizona
    python3 intraday.py --day 2026-09-10
    python3 intraday.py --dry-run      # compute and print, publish nothing

WHAT THIS IS, AND IS NOT. This runs the SAME pipeline the 6:30 PM digest does
-- daily.pull_sources() -> daily.transcribe_day() -> daily.build_metrics() ->
call_summary.build() -> publish_board.build() (board_payload.build() plus
coaching_cards.build(), same as the nightly path) -> publish_board.
apply_policy_streak() -- stopped before only the truly final/one-way steps:
no missed-call-task creation, no email, and it never writes days/<day>.json
(the finalized document publish_board.publish() writes). Reusing the exact
same functions the nightly build uses is the whole point -- an intraday
number, coaching card included, can never disagree with the final one on
method, only on how much of the day has happened yet.

THE BOARD RENDERS THIS AS THE WHOLE REPORT, NOT A SEPARATE STRIP (Frank,
2026-09-12: "I want the whole report uploading in real time"). Before this,
the frontend only ever showed a small "so far today" box of totals next to
whatever day was already finalized -- and since intraday.py refuses to
touch a day once it finalizes, that leftover box would freeze at its last
pre-finalization reading forever, including the pull_sources() staleness
bug's 0-dial readings on days it hit. Now the frontend's loadDay() falls
back to /api/intraday/<day> whenever /api/days/<day> 404s (i.e. the day
hasn't finalized yet) and renders the SAME leaderboard/task-completion/
outcomes/coaching/etc. panels from it unchanged, since the document this
module publishes is publish_board.build()'s exact shape.

CALL SUMMARIES AND COACHING CARDS NOW RUN HERE TOO (Frank, 2026-09-14: "I
have live contacts and data, but no coaching cards, how do we get that to
be generated in those runs"). Originally deferred to the once-a-night
build -- coaching_cards.build()'s own row filter needs summary.source ==
"recording", which only call_summary.build() ever sets, so skipping one
meant skipping both. Both are cached per (producer, number) in
data/callsum_<day>.json / data/coaching_cards_<day>.json, both already
round-tripped through r2_cache same as everything else this module
touches, so a live contact gets read ONCE across the whole day's
checkpoints combined, same total paid cost as reading it all at once
at 6:30 PM -- this only changes WHEN in the day that cost lands, not
how much of it there is. A read failing (no API key, a bad call) must
never block the checkpoint's numbers from publishing, so both are
wrapped to degrade gracefully -- see run()'s try/except and
publish_board.build()'s own docstring.

WHY THIS CAN RUN AT EACH CHECKPOINT AT THE SAME TOTAL COST AS ONCE A NIGHT
(Frank, 2026-09-10). r2_cache (see that module's docstring) makes every input
incremental: recordings and transcripts an earlier checkpoint already fetched
are pulled from R2 instead of re-downloaded, so cost only ever pays for the
delta since the last check. The AgencyZoom corpus is refetched fresh every
run on purpose -- it is the one thing that must never be stale, and its list
APIs are fast enough that caching it would only bring back HANDOFF_12 #3's
bug at a new layer.

Runs as part of the same business-hour schedule HOURLY_RUNS.md's missed-call
tasks already use (Frank, 2026-09-11: folded onto that schedule rather than a
separate one) -- ten checkpoints from 8:35 AM to 5:15 PM Arizona, NOT evenly
hourly (the gaps run 30-75 minutes). Nothing here assumes a fixed interval:
sanity_gate.check() compares against whatever the last snapshot actually was,
and its zero-dial check gates on the clock, not elapsed time since the last
run.

GUARD. Refuses to touch a day that has already been finalized (days/<day>.json
already exists on the board): a late or mis-scheduled run must never
re-fetch az_service_tickets_<day>.json / az_tasks_<day>.json for a day
CLAUDE.md's own rule says is locked.

WHAT IT PUBLISHES. intraday/<day>.json on the same flores-board R2 bucket,
via publish_board.publish_intraday() -- a separate key from days/<day>.json,
read by a separate Worker route, so an in-progress snapshot can never be
mistaken for the finalized board document.
"""
import argparse
import datetime as dt
import json
import sys

import daily
import publish_board
import r2_cache
import sanity_gate

AZ = dt.timezone(dt.timedelta(hours=-7))
log = daily.log


def run(day, dry_run=False):
    cli, bucket = publish_board._client()
    if publish_board.day_is_finalized(day, cli=cli, bucket=bucket):
        log(f"{day} is already finalized (days/{day}.json exists) -- "
            f"refusing to touch it. Nothing to do.")
        return None

    # pull_sources() itself now refreshes every per-day cache (call log,
    # recontact window, service tickets, tasks) whenever `day` is still the
    # Arizona day in progress -- not just here but for daily.py's own nightly
    # build too, which is the gap this call used to paper over (2026-09-12:
    # daily.py's build was still serving a stale mid-day call log even after
    # this fixed intraday.py's own checkpoints). Calling refresh_call_log /
    # refresh_window again here would just double the RingCentral requests
    # every checkpoint makes for no reason.
    daily.pull_sources(day)

    # Sales Sheet automation (Frank, 2026-09-15: "i want automation for the
    # sales sheet for all producers, including amanda") only needs the
    # corpus pull_sources() just refreshed -- no paid API, R2 reads/writes
    # only, so there's no reason it should wait for tonight's nightly build
    # any more than the policy-streak colouring above does. Guarded the same
    # way call_summary is below: a failure here costs only this feature, not
    # the checkpoint's numbers.
    try:
        import sales_log_auto
        sales_log_auto.sync_day(day, log=log, dry_run=dry_run)
    except Exception as e:
        log(f"  sales log auto: failed ({type(e).__name__}: {e})")

    daily.ensure_model()
    # Call-ins too (Frank, 2026-09-23). outbound_only exists for hourly.py,
    # which never pulls AgencyZoom and would pay ~2 minutes cold to screen a
    # handful of calls. This checkpoint already pulled everything screening
    # needs in pull_sources() above, so the only extra cost is downloading the
    # few call-ins that survive screening -- and without them the checkpoint
    # showed no call backs, no inbound talk time and no inbound Call Detail
    # until the nightly build.
    daily.transcribe_day(day)
    daily.build_metrics(day)

    # Populates summary.source == "recording" on each call_detail row, which
    # coaching_cards.build() (called inside publish_board.build() below)
    # filters on -- skip this and every card silently has nothing to
    # generate from, however many live contacts there are. Never allowed to
    # block the checkpoint's numbers: a failure here means this checkpoint's
    # cards are missing or stale, not that dials/premium/etc. don't publish.
    try:
        import call_summary
        call_summary.build(day, log=log)
    except Exception as e:
        log(f"  call summaries: failed ({type(e).__name__}: {e}) -- "
            f"coaching cards will be missing or stale this checkpoint")

    doc = publish_board.build(day, log=log, live=True)

    # call_summary.build() and coaching_cards.build() (the latter runs inside
    # publish_board.build() above) both write to data/, and r2_cache's own
    # last push in this run happened inside transcribe_day() -- BEFORE either
    # of those exist on disk yet. Left unfixed, callsum_<day>.json and
    # coaching_cards_<day>.json never make it to R2 at all: each checkpoint's
    # container is torn down having generated real summaries and cards that
    # simply vanish, so the NEXT checkpoint re-reads and re-summarizes the
    # same live contacts from zero (paying the Anthropic API cost again, the
    # opposite of this module's own "read exactly once across however many
    # checkpoints" design) and a checkpoint that generated a real card can
    # publish a board with none at all if torn down before a later checkpoint
    # regenerates it (confirmed 2026-09-15: Sarahi Chin's live contact got a
    # real "sales" card this way and it never reached the published board).
    r2_cache.sync_up_day(day, log=log)

    # Free (R2 reads only, no paid API), so the live board's Policies/Premium
    # Sold columns get the same sale-streak colouring as the finalized one
    # instead of going uncoloured until tonight -- publish_board.build() alone
    # can't do this itself, it needs prior days' documents from R2.
    publish_board.apply_policy_streak(doc, cli, bucket, log=log)

    prior = None
    try:
        prior = json.loads(cli.get_object(
            Bucket=bucket, Key=publish_board._intraday_key(day))["Body"].read())
    except Exception:
        pass
    flags = sanity_gate.check(doc, prior=prior)

    totals = doc.get("totals") or {}
    log(f"  {day} so far: {totals.get('dials') or 0} dials, "
        f"{totals.get('live') or 0} live ({totals.get('rate') or 0}%), "
        f"{totals.get('pol') or 0} sold, ${totals.get('ps') or 0:,} premium")
    for f in flags:
        log(f"  FLAG: {f}")

    if dry_run:
        log("[dry-run] not publishing")
        return doc, flags

    publish_board.publish_intraday(day, doc, flags, cli=cli, bucket=bucket, log=log)
    return doc, flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    day = a.day or dt.datetime.now(AZ).date().isoformat()
    log(f"intraday snapshot for {day}")
    result = run(day, dry_run=a.dry_run)
    if result and result[1]:
        # Non-zero exit on a tripped flag, so a Routine/CI-style caller can
        # tell "ran clean" from "ran and found something" without parsing
        # log text.
        sys.exit(1)


if __name__ == "__main__":
    main()
