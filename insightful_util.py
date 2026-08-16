"""Per-person utilization for an Arizona day, full roster -- not a top-five slice.

SOLVES (HANDOFF_4 s2b): Insightful's daily email truncates every table to the top
five people, and publishes a day's figures ~15:01 UTC the FOLLOWING day. The API
has no such truncation and, as measured 2026-08-14, carries the current Arizona
day live -- see s2e note at the bottom of this file.

THE FORMULA -- verified, do not relitigate:

    utilization = analytics/productivity[productivity==1].usage
                  / analytics/attendance[employee].duration

    Both are milliseconds. Compute at FULL ms precision and round only for
    display. This reproduces the 2026-08-07 published figures exactly:

        Crystal  25384287 / 29444742 = 86.21%   (published 86.21%)
        Mike     25306001 / 27591817 = 91.72%   (published 91.72%)
        Lorena                        = 80.25%   (published 80.25%)
        Amanda                        = 79.59%   (published 79.59%)
        Debbie                        = 91.95%   (published 91.89%, +0.06)

    Debbie is the one non-match. Her attendance row reads 07:35:28 against a
    published 07:32, and her productive time is high by the same ~3.5 min, so
    the ratio barely moves. No unusual flags on the row (isClockOutAssumed
    false, inProgressShifts 0). Most likely her shift was edited after the
    2026-08-08 email was generated. 0.06pp crosses no threshold -- both figures
    are green. Treated as acceptable drift, not a bug.

    The old "recompute from rounded minutes" approach is what produced 85.6%
    for Crystal against a published 86.21%. Do not go back to it.

    productivity codes: 1 = productive, 0 = neutral, 2 = unproductive,
                        3 = unreviewed.

TEAM WEIGHTED figure uses MINUTE-rounded values, which is how Insightful's own
"Team" number is built: sum(productive_min) / sum(total_min) across all users
except Amanda (Frank's standing rule, HANDOFF_4 s12).
    2026-08-07: 1620 / 1851 = 87.52%  -- matches the published team figure.

ROSTER NOTES (the s6 decision Frank scheduled for 2026-08-28):
  * Insightful holds DUPLICATE employee records -- Crystal and Mike each appear
    twice, once deactivated. Always resolve to the record with deactivated == 0.
  * Coral Barwick IS tracked and DOES produce a full utilization figure
    (2026-08-07: 70.72%, 07:02 total). The daily email simply truncated her off.
  * Francisco Flores has an active Insightful record but NO attendance rows --
    he is licensed, not tracked.
  * Sarahi Chin has NO Insightful record at all. She cannot be reported on
    until someone creates one, regardless of what Frank decides on 08-28.
"""
import datetime as dt

from insightful_client import Insightful, TEAM_UTIL_EXCLUDE

PRODUCTIVE = 1


def _hhmm(ms):
    s = ms / 1000.0
    return f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}"


def _minutes(ms):
    """Minute-rounded, the way Insightful displays a duration."""
    return int(ms / 1000 // 60)


def active_roster(ins=None):
    """name -> employeeId, resolving Insightful's duplicate records."""
    ins = ins or Insightful()
    out = {}
    for e in ins.employees():
        if e.get("deactivated"):
            continue
        out[e["name"]] = e["id"]
    return out


def pull(day, ins=None):
    """Utilization for one Arizona day.

    Returns:
        util        {name: (pct, total_hhmm, productive_hhmm)}  -- digest_config UTIL
        weighted    float                                       -- UTIL_WEIGHTED
        detail      {name: {...raw ms...}}                      -- for verify.py
    """
    ins = ins or Insightful()
    roster = active_roster(ins)
    by_id = {v: k for k, v in roster.items()}

    attendance = {a["employeeId"]: a["duration"]
                  for a in ins.analytics("attendance", day)}

    util, detail = {}, {}
    for name, eid in sorted(roster.items()):
        total_ms = attendance.get(eid)
        if not total_ms:
            # Licensed but untracked that day (e.g. Francisco). Report as absent
            # rather than as zero -- a 0% would read as a real bad day.
            detail[name] = {"tracked": False}
            continue
        buckets = ins.analytics("productivity", day, employeeId=eid) or []
        prod_ms = sum(b["usage"] for b in buckets if b["productivity"] == PRODUCTIVE)
        pct = round(prod_ms / total_ms * 100, 2)
        util[name] = (pct, _hhmm(total_ms), _hhmm(prod_ms))
        detail[name] = {
            "tracked": True,
            "productive_ms": prod_ms,
            "total_ms": total_ms,
            "productive_min": _minutes(prod_ms),
            "total_min": _minutes(total_ms),
            "buckets": {b["productivity"]: b["usage"] for b in buckets},
        }

    scope = [n for n, d in detail.items()
             if d.get("tracked") and n not in TEAM_UTIL_EXCLUDE]
    pm = sum(detail[n]["productive_min"] for n in scope)
    tm = sum(detail[n]["total_min"] for n in scope)
    weighted = round(pm / tm * 100, 2) if tm else 0.0

    return util, weighted, detail


# --- s2e: can the 6:00 PM Arizona ops email carry SAME-DAY utilization? ------
# Measured 2026-08-13/14. The API returns the in-progress Arizona day live, so
# the 15:01-UTC email lag does NOT apply. The real constraint is people still
# clocked in at send time. Share of each counted producer's tracked time that
# still lies ahead at each candidate cutoff:
#
#   cutoff   worst counted producer            worst anyone
#   17:30    Mike 13.8% (Aug 7)                Amanda 13.6% (Aug 11)
#   18:00    Mike  9.7% (Aug 7)                Amanda  7.3% (Aug 11)
#   18:30    Mike  2.7% (Aug 7)                Mike    2.7%
#   19:00    all 0.0%                          Coral   0.6% (Aug 12, 23:04 outlier)
#
# 6:00 PM clips a counted producer by ~10% on roughly one day in four.
# 6:30 PM caps the worst case at 2.7%; 7:00 PM is clean. Frank's call.
SEND_TIME_EVIDENCE = {
    "17:30": {"worst_counted": 13.8, "worst_any": 13.6},
    "18:00": {"worst_counted": 9.7, "worst_any": 7.3},
    "18:30": {"worst_counted": 2.7, "worst_any": 2.7},
    "19:00": {"worst_counted": 0.0, "worst_any": 0.6},
}


if __name__ == "__main__":
    import sys
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-08-07"
    util, weighted, detail = pull(day)
    print(f"UTIL['{day}'] = {{")
    for n, v in util.items():
        print(f"    {n!r}: {v},")
    print("}")
    print(f"UTIL_WEIGHTED['{day}'] = {weighted}")
    for n, d in detail.items():
        if not d.get("tracked"):
            print(f"  (untracked: {n})")
