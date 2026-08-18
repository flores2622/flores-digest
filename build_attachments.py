"""Generate the two companion documents for a day, as HTML ready for PDF."""
import datetime as dt
import json
import pathlib

import notes_patch

ROOT = pathlib.Path(__file__).resolve().parent
DOT = {"Crystal Mango": "cA", "Lorena Gonzalez": "cB", "Mike Olvera": "cC"}
SHORT = {"Crystal Mango": "Crystal", "Lorena Gonzalez": "Lorena",
         "Mike Olvera": "Mike"}
NUM = ' class="num"'
WEEKDAY = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
           "Saturday", "Sunday"]


def _d(x):
    try:
        return dt.date.fromisoformat(str(x)).isoformat()
    except Exception:
        return "&mdash;"


def _link(i, n):
    return (f'<a class="lead-link" href="https://app.agencyzoom.com/lead?id&#61;{i}" '
            f'target="_blank">{n}</a>')


def _table(items, cols, row):
    if not items:
        return '<div class="empty-row">None on this day.</div>'
    th = "".join("<th" + (NUM if c[1] else "") + ">" + c[0] + "</th>" for c in cols)
    return ("<table><thead><tr>" + th + "</tr></thead><tbody>"
            + "".join(row(r) for r in items) + "</tbody></table>")


def recontact_detail(day, M, template):
    src = pathlib.Path(template).read_text()
    d = dt.date.fromisoformat(day)
    head = src[:src.index('<div class="panel">')]
    head = head.replace("Aug 12, 2026", d.strftime("%b %-d, %Y"))
    head = head.replace("Wednesday, August 12, 2026",
                        f"{WEEKDAY[d.weekday()]}, {d.strftime('%B %-d, %Y')}")
    rc = M["recontact"]
    ar = sorted(rc["at_risk"],
                key=lambda r: (r["producer"], r["stage"], -r["business_days"]))
    lo = sorted(rc["lost"],
                key=lambda r: (r["producer"], r["stage"], -(r["calls"] or 0)))
    pa = sorted(rc.get("paused", []),
                key=lambda r: (r["returns_in"], r["producer"]))

    def rowA(r):
        return ('<tr><td class="name-cell"><span class="dot ' + DOT[r["producer"]]
                + '"></span>' + SHORT[r["producer"]] + '</td><td>'
                + _link(r["lead_id"], r["lead_name"]) + '</td>'
                '<td style="font-size:11px">' + r["stage"] + '</td>'
                '<td class="nowrap-cell">' + _d(r["entered"]) + '</td>'
                '<td class="num">' + str(r["business_days"]) + '</td>'
                '<td class="num">' + str(r["calls"]) + '</td>'
                '<td style="font-size:11px">' + r["flag"] + '</td></tr>')

    def rowL(r):
        return ('<tr><td class="name-cell"><span class="dot ' + DOT[r["producer"]]
                + '"></span>' + SHORT[r["producer"]] + '</td><td>'
                + _link(r["lead_id"], r["lead_name"]) + '</td>'
                '<td style="font-size:11px">' + r["stage"] + '</td>'
                '<td class="nowrap-cell">' + _d(r["entered"]) + '<span class="sq">'
                + str(r.get("entered_basis", "")) + '</span></td>'
                '<td style="font-size:11px">' + r["outcome"] + '</td>'
                '<td class="nowrap-cell">' + r["outcome_date"] + '</td>'
                '<td class="num">' + str(r["days"]) + '</td>'
                '<td class="num">' + str(r["calls"]) + '</td></tr>')

    def rowP(r):
        return ('<tr><td class="name-cell"><span class="dot ' + DOT[r["producer"]]
                + '"></span>' + SHORT[r["producer"]] + '</td><td>'
                + _link(r["lead_id"], r["lead_name"]) + '</td>'
                '<td style="font-size:11px">' + r["stage"] + '</td>'
                '<td class="nowrap-cell">' + _d(r["entered"]) + '</td>'
                '<td class="nowrap-cell">' + _d(r["returns"]) + '</td>'
                '<td class="num">' + str(r["returns_in"]) + '</td>'
                '<td class="num">' + str(r["calls"]) + '</td></tr>')

    body = ('<div class="panel"><h2>Recontact Detail &nbsp;&middot;&nbsp; '
            'at risk, paused, lost and won</h2>'
            '<div class="section-title">At risk of going cold &mdash; '
            + str(len(ar)) + '</div>'
            '<div class="panel-subtitle">In a post-contact stage with more than 3 '
            'business days since the last stage move, or more than 3 dials since '
            'entering it without the lead moving. Ranked by days stalled. '
            '<b>not worked</b> = 0-1 calls since entering the stage; '
            '<b>under-worked</b> = 2-3; <b>no traction</b> = 4 or more and '
            'still not moving.</div>'
            + _table(ar, [("Rep", 0), ("Lead", 0), ("Stage", 0), ("Entered", 0),
                          ("Business days", 1), ("Calls since", 1), ("Flag", 0)], rowA)
            + '<div class="section-title">Lost &mdash; ' + str(len(lo)) + '</div>'
            '<div class="panel-subtitle">Moved to Dead, or smart-cycled with the '
            'cycle 30+ days out, on this day. A cycle returning within 29 days is '
            'a pause and is listed separately below. Ranked by calls invested '
            'before the loss.</div>'
            + _table(lo, [("Rep", 0), ("Lead", 0), ("Stage they were in", 0),
                          ("Entered", 0), ("Outcome", 0), ("Outcome date", 0),
                          ("Days", 1), ("Calls between", 1)], rowL)
            + '<div class="section-title">On pause &mdash; ' + str(len(pa))
            + '</div>'
            '<div class="panel-subtitle">Smart-cycled on this day with the cycle '
            'returning within 29 days &mdash; parked for a week or two, or waiting '
            'for automation to restart. Not counted as a loss. The return date is '
            'the Smart-Cycle date shown on the lead in AgencyZoom.</div>'
            + _table(pa, [("Rep", 0), ("Lead", 0), ("Stage they were in", 0),
                          ("Entered", 0), ("Returns", 0), ("Days out", 1),
                          ("Calls", 1)], rowP)
            + '<div class="section-title">Won &mdash; '
            + (str(len(rc["won"])) if rc["won"] else "none") + '</div>'
            '<div class="empty-row">Sold on this day.</div>'
            '<div class="footnote"><b>How the Entered date is determined.</b> '
            'Preferred source is the recorded stage move into that stage. A lead is '
            '<i>created</i> into New and AgencyZoom writes no move note for that, so '
            'early-funnel stages use the lead&rsquo;s creation date. <b>AgencyZoom '
            'overwrites <code>enterStageDate</code> when it moves a lead to '
            'Smart-Cycle</b>, so that field reads as the outcome date and is never '
            'used here.<br><br>&ldquo;Calls between&rdquo; counts that '
            'producer&rsquo;s dials to the lead&rsquo;s number between entering the '
            'stage and the outcome. Leads assigned to Frank, Coral, Sarahi and '
            'Amanda are excluded throughout &mdash; those are training leads.</div>'
            '</div></div></div></body></html>')
    return head + body


def notes_and_methodology(day, M, template):
    d = dt.date.fromisoformat(day)
    h = pathlib.Path(template).read_text()
    h = h.replace("Wednesday, August 12, 2026",
                  f"{WEEKDAY[d.weekday()]}, {d.strftime('%B %-d, %Y')}")
    h = h.replace("Aug 12, 2026", d.strftime("%b %-d, %Y")).replace("2026-08-12", day)
    h = notes_patch.patch(h)

    P = M["producers"]
    tl = sum(P[p]["live"] for p in P)
    tv = sum(P[p]["call_volume"] for p in P)
    tx = json.loads((ROOT / f"data/transcripts_{day}.json").read_text())
    import collections
    c = collections.Counter(v["class"] for v in tx.values())

    start = h.index("<b>Live Contact</b>")
    end = h.index("<b>Premium Quoted</b>")
    new = ("<b>Live Contact</b> is decided from the call recording. Every recorded "
           "producer call is transcribed at build time and classified as a "
           "conversation, a voicemail or a no-answer from what was actually said. "
           f"On this day {sum(c.values())} calls were recorded: "
           f"{c.get('voicemail', 0)} voicemail, {c.get('no answer', 0)} no-answer, "
           f"{c.get('live', 0)} live. Duration is not used and cannot be &mdash; a "
           "two-second pickup is a live contact, while a 77-second voicemail "
           "greeting is not. Where a call has no recording the producer&rsquo;s own "
           "AgencyZoom note decides, and an explicit &ldquo;never answered&rdquo; "
           "always outranks anything else. Rows resting on duration alone are "
           "labelled <b>duration only</b> in Call Detail.<br><br>"
           f"<b>Avg Talk Time</b> is total talk across live contacts divided by the "
           f"live-contact count ({tl} on this day), not across all {tv} dials.<br><br>"
           "<b>A policy whose lead source is BOB is not a sale.</b> BOB is "
           "book-of-business &mdash; existing policies moved onto a producer&rsquo;s "
           "name rather than new business won. It is excluded from Premium Sold, "
           "policy counts and the leaderboard.<br><br>")
    h = h[:start] + new + h[end:]
    h = h.replace(
        "<b>Coral Barwick and Sarahi Chin are excluded from every calculation on "
        "this report</b>",
        "<b>Coral Barwick and Sarahi Chin are excluded from every calculation on "
        "this report</b>, with one exception: <b>a genuine sale by either of them "
        "is shown on their placeholder card on the day it happens</b>, though it "
        "still enters no team total")
    return h


def build(day, template_dir="template"):
    M = json.loads((ROOT / f"data/metrics_{day}.json").read_text())
    (ROOT / "out").mkdir(exist_ok=True)
    n = ROOT / f"out/Notes_and_Methodology_{day}.html"
    r = ROOT / f"out/Recontact_Detail_{day}.html"
    n.write_text(notes_and_methodology(
        day, M, ROOT / template_dir / "notes_template.html"))
    r.write_text(recontact_detail(
        day, M, ROOT / template_dir / "recontact_template.html"))
    return str(n), str(r)
