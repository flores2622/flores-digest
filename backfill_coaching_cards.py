"""Reapply coaching_cards.py's CURRENT logic to already-published days.

WHY THIS EXISTS. A coaching_cards.py fix (badge wording, grouping rule,
whatever) only reaches days going forward for free -- intraday.py's
checkpoints get a cold container and pull fresh `main` on every run. A day
that already went out is a frozen days/<day>.json snapshot in R2; nothing
rebuilds it on its own (Frank, 2026-09-15: "how do we get it so that any
changes we make are always universally applied to everything"). This is
the deliberate, repeatable version of the by-hand rebuild done for
2026-09-11 the same day this file was written.

    python3 backfill_coaching_cards.py --all                   # dry run
    python3 backfill_coaching_cards.py --all --yes              # publish
    python3 backfill_coaching_cards.py --day 2026-09-11 --yes
    python3 backfill_coaching_cards.py --since 2026-09-01 --yes

WHAT THIS TOUCHES, AND WHAT IT NEVER DOES. Only the "calls"/"scan"/
"objcats" keys of a day's published document -- exactly what
coaching_cards.build() (via publish_board.build(), so a hand-authored
coaching/cards_<day>.py override is still respected) can produce.
Everything else already on the day -- totals, tiers, tasks, producers,
policy_streak, built_at -- is carried over untouched, by construction:
this script never reads board_payload's totals/tiers/tasks at all, let
alone writes them back. That is not an extra safety check bolted on, it
is the whole reason this is a separate small script instead of just
calling publish_board.publish(day) again -- that function's build() also
recomputes totals/tiers/tasks straight from THIS container's local
data/metrics_<day>.json, and a stale or partial local cache there must
never leak into an already-published day. Rebuilding 2026-09-11 the wide
way did exactly that once already: Task Completion silently went from
141/79 to 10/0 in this exact container, unrelated to any real change,
just a stale local az_tasks cache. This script cannot make that mistake.

A day whose freshly-built cards come back EMPTY is treated as a build
failure, never as "the day now has zero cards" -- coaching_cards.build()
returns [] on several soft-failure paths (no ANTHROPIC_API_KEY loaded, no
metrics cached anywhere, a transient read error), and blanking out a
day's real cards because of one of those would be worse than doing
nothing. Skipped and logged loudly instead of published.

WHY NOT FULLY AUTOMATIC (no hook, no CI, nothing that runs this on every
push). A bug in a future coaching_cards.py change would silently rewrite
every historical day's cards with no human check on the diff, and this
codebase has already hit enough "looked fine, was actually wrong"
landmines (CLAUDE.md is one long list of them) that blind auto-apply
everywhere is a worse trade than a deliberate command run when a fix is
actually worth backfilling. --dry-run is the default; --yes publishes.

COST. Only pays for a model read on a group coaching_cards.py's own cache
(data/coaching_cards_<day>.json, pulled from R2 via r2_cache if this
container doesn't already have it) has no entry for yet. A logic-only
fix that doesn't touch _group_ck's cache keys costs nothing to backfill.
A change that DOES touch grouping/cache keys will show up here as real
"writing N coaching cards with <model>..." log lines -- that means real
spend across every day being backfilled, not a free replay; read those
lines before answering --yes.
"""
import argparse
import json
import re

import coaching_cards
import publish_board
import r2_cache
import secrets_load


def _all_published_days(cli, bucket):
    days, token = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": f"{publish_board.PREFIX}/"}
        if token:
            kw["ContinuationToken"] = token
        page = cli.list_objects_v2(**kw)
        for o in page.get("Contents", []):
            m = re.match(rf"^{publish_board.PREFIX}/(\d{{4}}-\d{{2}}-\d{{2}})\.json$", o["Key"])
            if m:
                days.append(m.group(1))
        if not page.get("IsTruncated"):
            break
        token = page.get("NextContinuationToken")
    return sorted(days)


def _card_summary(cards):
    """Short, stable-order description of a calls list, for logging what
    changed -- lead name plus the fields this file actually adds/changes."""
    return {c.get("lead", ""): (c.get("call_count"), c.get("callback_kind"),
                                 tuple(c.get("call_times") or []))
            for c in (cards or [])}


def plan_one(day, cli, bucket, log=print):
    """Rebuild `day`'s coaching cards fresh and compare against what's
    published. Returns a dict describing the outcome; never writes
    anything -- see apply_one for that.

    status is one of:
      "skip-no-data"    -- nothing cached anywhere for this day, not touched
      "skip-no-live-doc" -- day isn't actually published, not touched
      "skip-build-failed" -- fresh build came back empty but the live doc
                             has real cards; treated as a failure, not a
                             deletion (see module docstring)
      "unchanged"        -- fresh build matches what's already published
      "changed"          -- fresh build differs; `new` holds the 3 keys
                             to splice in, `diff` a per-lead summary
    """
    r2_cache.sync_down_day(day, log=lambda *a: None)
    if not (coaching_cards.ROOT / f"data/metrics_{day}.json").exists():
        return {"day": day, "status": "skip-no-data"}

    try:
        body = cli.get_object(Bucket=bucket, Key=publish_board._key(day))["Body"].read()
    except Exception as e:
        return {"day": day, "status": "skip-no-live-doc", "why": str(e)}
    live = json.loads(body)

    doc = publish_board.build(day, log=lambda *a: None)
    new = {k: doc.get(k) for k in ("calls", "scan", "objcats") if k in doc}

    if not new.get("calls") and live.get("calls"):
        return {"day": day, "status": "skip-build-failed",
                "why": f"live has {len(live['calls'])} cards, fresh build has none"}

    live_view = {k: live.get(k) for k in ("calls", "scan", "objcats")}
    if json.dumps(live_view, sort_keys=True, default=str) == \
       json.dumps(new, sort_keys=True, default=str):
        return {"day": day, "status": "unchanged"}

    before = _card_summary(live.get("calls"))
    after = _card_summary(new.get("calls"))
    diff = []
    for lead in sorted(set(before) | set(after)):
        if before.get(lead) != after.get(lead):
            diff.append(f"    {lead}: {before.get(lead)} -> {after.get(lead)}")
    return {"day": day, "status": "changed", "live": live, "new": new, "diff": diff}


def apply_one(plan, cli, bucket, log=print):
    live = dict(plan["live"])
    live.update(plan["new"])
    body = json.dumps(live, default=str).encode()
    cli.put_object(
        Bucket=bucket, Key=publish_board._key(plan["day"]), Body=body,
        ContentType="application/json", CacheControl="no-store",
    )
    log(f"  published {len(body):,} bytes -> r2://{bucket}/{publish_board._key(plan['day'])}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    sel = ap.add_mutually_exclusive_group(required=True)
    sel.add_argument("--all", action="store_true", help="every published day")
    sel.add_argument("--since", metavar="YYYY-MM-DD", help="every published day on or after this one")
    sel.add_argument("--day", metavar="YYYY-MM-DD", help="just this one day")
    ap.add_argument("--yes", action="store_true",
                     help="actually publish (default is dry-run: plan and print only)")
    a = ap.parse_args()

    secrets_load.load()
    cli, bucket = publish_board._client()

    if a.day:
        days = [a.day]
    else:
        days = _all_published_days(cli, bucket)
        if a.since:
            days = [d for d in days if d >= a.since]

    print(f"{'PUBLISHING' if a.yes else 'DRY RUN'} -- {len(days)} day(s) to check")
    counts = {"changed": 0, "unchanged": 0, "skip-no-data": 0,
              "skip-no-live-doc": 0, "skip-build-failed": 0}
    for day in days:
        plan = plan_one(day, cli, bucket)
        counts[plan["status"]] += 1
        if plan["status"] == "changed":
            print(f"{day}: CHANGED")
            for line in plan["diff"]:
                print(line)
            if a.yes:
                apply_one(plan, cli, bucket)
        elif plan["status"] == "skip-build-failed":
            print(f"{day}: SKIPPED -- {plan['why']}")
        elif plan["status"] in ("skip-no-data", "skip-no-live-doc"):
            print(f"{day}: skip ({plan['status']})")
        # "unchanged" stays quiet -- the common case shouldn't scroll the log

    print(f"\n{counts['changed']} changed"
          + ("" if a.yes else " (not published -- pass --yes to publish)")
          + f", {counts['unchanged']} already up to date, "
          + f"{counts['skip-no-data'] + counts['skip-no-live-doc']} skipped (no data), "
          + f"{counts['skip-build-failed']} skipped (build failed, see above)")


if __name__ == "__main__":
    main()
