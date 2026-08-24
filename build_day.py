"""Render one day's operations report from the approved layout + that day's data.

Usage: python3 build_day.py 2026-08-13

Reads data/metrics_<day>.json, rewrites every panel, and writes
out/Ops_Report_<day>.html. Every panel swap is guarded by a div-balance check.
"""
import importlib
import json
import pathlib
import re
import sys

import panels
import render_report as rr
import util_panel
from util_panel import assert_div_balance

TEMPLATE = "template/report_template.html"
WEEKDAY = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
           4: "Friday", 5: "Saturday", 6: "Sunday"}


def build(day, template=TEMPLATE):
    import datetime as dt
    importlib.reload(panels)
    d = dt.date.fromisoformat(day)
    label = d.strftime("%b %-d, %Y")
    long_label = f"{WEEKDAY[d.weekday()]}, {d.strftime('%B %-d, %Y')}"

    M = json.loads(pathlib.Path(f"data/metrics_{day}.json").read_text())
    src = pathlib.Path(template).read_text()
    h = src
    h = h.replace("Wednesday, August 12, 2026", long_label)
    h = h.replace("Aug 12, 2026", label).replace("August 12, 2026",
                                                 d.strftime("%B %-d, %Y"))
    h = h.replace("2026-08-12", day)

    P = M["producers"]
    s2d = M["speed_to_dial"]
    meds = [v["median"] for v in s2d.values() if v]
    team_s2d = ({"median": sorted(meds)[len(meds) // 2],
                 "quickest": min(meds), "longest": max(meds)} if meds else None)

    for heading, new in [
        ("Sales Funnel by Producer", rr.build_funnel(P, label)),
        ("Task Completion Rate", panels.task_table(M["tasks"], {})),
        ("Recontact Struggle",
         panels.recontact_cards(M["recontact"], f"Recontact_Detail_{day}.pdf")),
        ("Team Leaderboard", panels.leaderboard(P, M["coach"])),
        ("Call Outcome Breakdown", panels.outcome_rows(P)),
        ("Speed to Dial", panels.speed_table(s2d, team_s2d)),
        ("Coaching &amp; Call Quality", panels.coach_cards(M["coach"])),
        ("Call Detail &nbsp;", panels.call_detail(P, day)),
        # Was static template HTML until 2026-08-18 -- see task_audit.
        # "&middot;" pins this to the panel's own h2 -- the bare phrase also
        # appears in the document title and matches there first.
        ("Task Completion Audit &middot;",
         panels.task_audit_tables(M["task_audit"], label)),
    ]:
        before = h
        h = rr.swap_panel(h, heading, new)
        assert_div_balance(before, h, heading)

    h = util_panel.patch(h, day)

    # Frank, 2026-08-24: he is not sold on the Recontact Struggle panel and asked
    # to "just do the file". It is the single biggest panel in the body at about
    # 12.5 KB, and Recontact_Detail_<day>.pdf already ships the same content in
    # full, built from its own template -- so dropping it here loses nothing and
    # buys back the headroom the fourth and fifth producers cost. Swapped first,
    # then removed, so that deleting this one line can never ship the template's
    # stale placeholder rows.
    h = rr.drop_panel(h, "Recontact Struggle")

    # Frank, 2026-08-24: Call Outcome Breakdown goes last in the digest, spanning
    # the full width. It already sat outside the two-column table, so it was
    # already as wide as both columns -- this is purely a reorder, moving it from
    # just after the columns to after Coaching & Call Quality, immediately before
    # the audit section starts.
    # The "Notes & Methodology -- attached" strip is gone entirely (Frank,
    # 2026-08-24: "its not needed"). Both companion PDFs still attach to the
    # email; this only removes the in-body pointer to them. The footnote markers
    # in the panel headings still number through to the notes attachment.
    # Dropped BEFORE the move below, so the audit section is once again the right
    # anchor for putting Call Outcome last in the digest.
    h = rr.drop_panel(h, "Notes &amp; Methodology &mdash; attached")

    h = rr.move_panel_before(h, "Call Outcome Breakdown",
                             '<div id="audit-section"')

    assert_div_balance(src, h, "final")

    out = f"out/Ops_Report_{day}.html"
    pathlib.Path(out).parent.mkdir(exist_ok=True)
    pathlib.Path(out).write_text(h)
    return out, h

if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-08-13"
    out, h = build(day)
    o = len(re.findall(r"<div\b", h)), len(re.findall(r"</div>", h))
    print(f"{out}  {len(h.encode()):,} bytes  divs {o[0]}/{o[1]}")
