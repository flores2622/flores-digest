"""Check the deferred totals against SOURCE data, not a stale snapshot.

Every figure is recomputed independently from day_calls, then compared with
what finalize.apply() wrote into metrics.

SAME-DAY ONLY (Frank, 2026-09-14, after 2026-09-11 showed 12 "mismatches"
that were nothing of the kind). day_calls.classify() reads
data/az_leads_all.json and data/az_customers_all.json, and r2_cache.py's own
docstring says why those two are DELIBERATELY NOT day-scoped or cached:
daily.pull_sources() always fetches them fresh. That is correct for building
TODAY's report, but it means there is no way to recover the exact leads/
customers snapshot a past day was originally built against -- re-running
classify() for an old day just uses whatever corpus happens to be on disk
now. Every one of 2026-09-11's 12 mismatches traced to a number that
genuinely resolved to a lead or customer record at build time and genuinely
does not anymore (reassigned, merged, converted, a service task's due date
moved on) -- not a bug in the published day. This is the exact same
point-in-time hazard CLAUDE.md already documents for service tickets,
just unguarded here. Warn loudly rather than print a confusing mismatch
list for anyone who reaches for this days later, the way this session did.
"""
import json, sys, collections, datetime as dt
import os, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
import day_calls

# The day was hardcoded to 2026-08-25 from the day this was written, so it
# silently reconciled a stale file whenever anyone ran it against a newer build
# (HANDOFF_11 s7). Takes the day as an argument now, defaulting to today in
# Arizona, which is what the nightly build reports.
TODAY_AZ = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=7)).date().isoformat()
DAY = sys.argv[1] if len(sys.argv) > 1 else TODAY_AZ
print(f"reconciling {DAY}")
if DAY != TODAY_AZ:
    print(f"  WARNING: {DAY} is not today ({TODAY_AZ}) -- az_leads_all.json/"
          f"az_customers_all.json are never day-scoped, so any mismatch below "
          f"may just mean a lead or customer record has changed since {DAY} "
          f"was built, not that the published day is wrong. Only a mismatch "
          f"you can trace to something OTHER than a lead/customer/service-task "
          f"lookup (e.g. avg_talk, live, or a raw dial-count difference) "
          f"points at a real bug.")

M = json.load(open(f'data/metrics_{DAY}.json'))
rows = day_calls.classify(DAY)
dials = day_calls.producer_dials(DAY)
bad = 0
for who, v in M['producers'].items():
    counted = [r for r in rows.get(who, []) if not r['excluded']]
    dropped = {d['number'] for d in (v.get('dials') or []) if d.get('dropped')}
    # A dial dropped as a DUPLICATE LEAD keeps its attempt -- the producer
    # really made that call, and it was merged onto the surviving row for the
    # same person (Frank, 2026-09-01: "it 2 dials, one unique
    # number/contact"). Every other drop reason takes its attempt with it: a
    # service/renewal call is not new-business activity at all.
    merged = {d['number'] for d in (v.get('dials') or [])
              if 'duplicate lead' in str(d.get('dropped') or '')}
    expect_numbers = {r['number'] for r in counted} - dropped
    checks = {
        'call_volume': (v['call_volume'], len(expect_numbers)),
        'total_dials': (v['total_dials'],
                        sum(len(dials.get(who, {}).get(n) or [])
                            for n in expect_numbers | merged)),
        # call_detail now carries inbound rows too, which are conversations
        # but not dials -- so live counts only the OUTBOUND rows.
        'live':        (v['live'],
                        len([r for r in v['call_detail'] if not r.get('inbound')])),
        'contact_rate': (v['contact_rate'],
                         round(len([r for r in v['call_detail']
                                    if not r.get('inbound')])
                               / len(expect_numbers) * 100, 1)
                         if expect_numbers else 0),
        # talk time is over every conversation, inbound included
        'avg_talk':    (v['avg_talk'],
                        round(sum(r['seconds'] for r in v['call_detail'])
                              / len(v['call_detail'])) if v['call_detail'] else 0),
        'outcomes_sum': (sum(v['outcomes'].values()), len(expect_numbers)),
        'live_bucket': (v['outcomes'].get('Live Contact', 0),
                        len([r for r in v['call_detail'] if not r.get('inbound')])),
    }
    for k, (got, want) in checks.items():
        if got != want:
            print(f"  MISMATCH {who:16} {k}: metrics={got} recomputed={want}")
            bad += 1
print("ALL SIX FIGURES RECONCILE" if not bad else f"{bad} mismatches")
tot_v = sum(v['call_volume'] for v in M['producers'].values())
tot_l = sum(v['live'] for v in M['producers'].values())
print(f"team: {tot_v} dials, {tot_l} live, {round(tot_l/tot_v*100,1)}%")
print("dropped by the read:",
      [(w, d['number'], d['dropped']) for w, v in M['producers'].items()
       for d in (v.get('dials') or []) if d.get('dropped')] or "none")
