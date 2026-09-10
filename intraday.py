"""Intraday snapshot: the day's numbers so far, checked and published hourly.

    python3 intraday.py                # today, Arizona
    python3 intraday.py --day 2026-09-10
    python3 intraday.py --dry-run      # compute and print, publish nothing

WHAT THIS IS, AND IS NOT. This runs the SAME pipeline the 6:30 PM digest does
-- daily.pull_sources() -> daily.transcribe_day() -> daily.build_metrics() ->
board_payload.build() -- stopped before anything paid or final: no
call_summary.py read, no coaching_cards.py read, no email, and it never
writes days/<day>.json (the finalized document publish_board.publish()
writes). Reusing the exact same functions the nightly build uses is the
whole point -- an intraday number can never disagree with the final one on
method, only on how much of the day has happened yet.

WHY THIS CAN RUN HOURLY AT THE SAME COST AS ONCE A NIGHT (Frank, 2026-09-10).
r2_cache (see that module's docstring) makes every input incremental:
recordings and transcripts an earlier hour already fetched are pulled from R2
instead of re-downloaded, so cost only ever pays for that hour's delta. The
AgencyZoom corpus is refetched fresh every run on purpose -- it is the one
thing that must never be stale, and its list APIs are fast enough that
caching it would only bring back HANDOFF_12 #3's bug at a new layer.

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

import board_payload
import daily
import publish_board
import sanity_gate

AZ = dt.timezone(dt.timedelta(hours=-7))
log = daily.log


def run(day, dry_run=False):
    cli, bucket = publish_board._client()
    if publish_board.day_is_finalized(day, cli=cli, bucket=bucket):
        log(f"{day} is already finalized (days/{day}.json exists) -- "
            f"refusing to touch it. Nothing to do.")
        return None

    daily.pull_sources(day)
    daily.ensure_model()
    daily.transcribe_day(day, outbound_only=True)
    daily.build_metrics(day)
    doc = board_payload.build(day)

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
