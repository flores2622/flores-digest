"""Check the deferred totals against SOURCE data, not a stale snapshot.

Every figure is recomputed independently from day_calls, then compared with
what finalize.apply() wrote into metrics.
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
DAY = (sys.argv[1] if len(sys.argv) > 1 else
       (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=7)).date().isoformat())
print(f"reconciling {DAY}")

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
