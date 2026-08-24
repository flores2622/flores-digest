"""Update the Notes & Methodology attachment for the live Insightful pull.

Two passages went stale the moment utilization came from the API instead of
Insightful's daily email. Both are rewritten in place; nothing else in the
attachment is touched.

  * Footnote 6 (Utilization and Efficiency) opened "This is a scheduling
    conflict, not a data fault, and it recurs every day" and listed three ways
    out, the third being "pull them directly from the Insightful API". That is
    now what happens, so the footnote must state the method rather than the
    problem. It also asserted "Also absent from Insightful: Francisco Flores;
    its tables truncate to the top five people" -- the truncation was the
    EMAIL's, not the API's, and the roster facts are now known precisely.

  * The Sources paragraph listed "Insightful daily report email".
"""
import re

FOOTNOTE_6_NEW = (
    "<b>6.</b><b>Utilization is pulled live from the Insightful API at build "
    "time.</b> The scheduling conflict this note used to describe is resolved. "
    "Insightful&rsquo;s daily <i>email</i> lands around 15:01 UTC the following "
    "day, which is after the send window, but the API carries the current "
    "Arizona day &mdash; verified 2026-08-13 at 22:19 Arizona, which already "
    "returned complete attendance for every tracked person. The operations "
    "digest moved from 6:00 to <b>6:30 PM Arizona</b> for a separate reason: at "
    "6:00 a producer is still clocked in often enough to understate them by "
    "about 10% roughly one day in four; at 6:30 the worst case is under 3%."
    "<br><br><b>Method.</b> Utilization is productive time over tracked time "
    "&mdash; <code>analytics/productivity</code> where productivity is "
    "&ldquo;productive&rdquo;, divided by <code>analytics/attendance</code> "
    "duration for that person and Arizona day. Both are milliseconds and the "
    "division is done at full precision, rounded only for display. Recomputing "
    "from minute-rounded values is what previously published 85.6% for Crystal "
    "against Insightful&rsquo;s own 86.21%. Checked against the five figures "
    "Insightful published for Aug 7: Crystal, Mike, Lorena and Amanda match "
    "exactly, and the team weighted figure lands at 87.54% against a published "
    "87.52%. Debbie differs by 0.06 points because her attendance row now reads "
    "07:35:28 against the 07:32 in that email, with productive time high by the "
    "same ~3.5 minutes &mdash; her shift appears to have been edited after the "
    "email was generated. Nothing is estimated. Green 85%+, yellow 80&ndash;84%, "
    "red under 80%; the bar is tinted to match."
    "<br><br><b>Scope and roster.</b> <b>As of Aug 24 Coral Barwick and Sarahi "
    "Chin are regular producers</b> and count in every figure in this report, "
    "including the team totals. The training pin that kept them blank, and the "
    "Aug 28 review it was waiting for, are both closed. The team is therefore "
    "five producers, not three, so team totals and the goal thresholds on call "
    "volume and households quoted step up accordingly &mdash; <b>figures before "
    "and after Aug 24 are not directly comparable</b> on those two metrics. "
    "The team weighted utilization figure is all users except Amanda; it now "
    "includes Coral, who is fully tracked by Insightful and has a real figure "
    "every day (the old daily email was simply truncating her off at its "
    "top-five limit). One gap remains: <b>Sarahi has no Insightful record at "
    "all</b> &mdash; not merely untracked &mdash; so her utilization card alone "
    "stays blank until a licence is assigned to her. Every other figure for her "
    "is live. Francisco Flores holds an active licence but produces no "
    "attendance rows; he is reported as absent rather than 0%, since a zero "
    "would read as a bad day rather than as no data."
)

SOURCES_OLD = "Insightful daily report email"
SOURCES_NEW = ("Insightful API (per-person attendance and productivity, "
               "pulled live at build time)")


def patch(html):
    start = html.find("<b>6.</b>")
    if start < 0:
        raise SystemExit("footnote 6 not found -- attachment structure changed?")
    end = html.find("</div>", start)
    out = html[:start] + FOOTNOTE_6_NEW + html[end:]

    if SOURCES_OLD not in out:
        raise SystemExit("sources line not found -- attachment changed?")
    out = out.replace(SOURCES_OLD, SOURCES_NEW)
    return out


if __name__ == "__main__":
    import sys
    src = sys.argv[1]
    dest = sys.argv[2]
    html = open(src).read()
    out = patch(html)
    open(dest, "w").write(out)
    print(f"{dest}  {len(out):,} bytes (was {len(html):,})")
