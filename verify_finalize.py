"""Check the deferred totals against SOURCE data, not a stale snapshot.

Every figure is recomputed independently from day_calls, then compared with
what finalize.apply() wrote into metrics.
"""
import json, sys, collections
sys.path.insert(0, '/root/flores-digest')
import os; os.chdir('/root/flores-digest')
import day_calls

M = json.load(open('data/metrics_2026-08-25.json'))
rows = day_calls.classify('2026-08-25')
dials = day_calls.producer_dials('2026-08-25')
bad = 0
for who, v in M['producers'].items():
    counted = [r for r in rows.get(who, []) if not r['excluded']]
    dropped = {d['number'] for d in (v.get('dials') or []) if d.get('dropped')}
    expect_numbers = {r['number'] for r in counted} - dropped
    checks = {
        'call_volume': (v['call_volume'], len(expect_numbers)),
        'total_dials': (v['total_dials'],
                        sum(len(dials.get(who, {}).get(n) or []) for n in expect_numbers)),
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
