"""Keep the digest sendable on a heavy day instead of refusing to send it.

THE PROBLEM
-----------
Gmail clips an HTML body over 102,400 bytes and replaces the tail with
"[Message clipped]", so send_digest refuses at that threshold rather than
delivering a report with whole panels silently missing. Correct, but the
failure mode is that NOBODY gets anything -- ops and staff both -- because one
panel grew.

The Aug 24 build measured 89,864 bytes for 25 live contacts, and Call Detail
costs about 956 bytes per contact. That puts the wall near 38 live contacts,
which is a busy day, not an impossible one.

WHAT THIS DOES
--------------
Frank, 2026-08-25: "can you just include the call detail and task completion as
a PDF if its too large? that way we dont lose it entirely."

So: shed panels from the email body, cheapest first, until the body fits --
and everything shed rides along as a PDF attachment, complete. A notice at the
top of the email says what moved, because a short report nobody flags reads as
a quiet day rather than a truncated one.

Nothing here runs on a normal day. Under the threshold, relieve() returns the
body untouched and no extra attachment is built.
"""
import pathlib
import re

import digest_config as cfg
import render_report as rr

ROOT = pathlib.Path(__file__).resolve().parent

# Leave room for the notice banner we are about to insert, and for any header
# a relay adds on the way. Shedding one panel too early costs far less than
# discovering at send time that we are still 300 bytes over.
SAFETY_BYTES = 2_000

# Shed order: least-read first. Call Detail is the panel Frank actually reads,
# so it goes second-to-last of the two he named, and the four below it exist
# only so that a truly enormous day still delivers something rather than
# tripping the hard guard in send_digest.
SHED_ORDER = [
    ("Task Completion Audit &middot;", "Task Completion Audit"),
    ("Call Detail &nbsp;&middot;&nbsp;", "Call Detail"),
    ("Coaching &amp; Call Quality", "Coaching &amp; Call Quality"),
    ("Speed to Dial &middot;", "Speed to Dial"),
    ("Call Outcome Breakdown &middot;", "Call Outcome Breakdown"),
]

# The notice goes above the first panel -- after the report header, not
# before it, so the email still opens with its own title.
NOTICE_ANCHOR = '<div class="panel'


def _fits(html):
    return len(html.encode()) + SAFETY_BYTES < cfg.GMAIL_CLIP_BYTES


def _notice(labels, pdf_name):
    names = labels[0] if len(labels) == 1 else (
        ", ".join(labels[:-1]) + " and " + labels[-1])
    plural = "panel is" if len(labels) == 1 else "panels are"
    return (
        '<div class="panel" style="background:#fdf1d6;border-color:#fab219;'
        'margin-bottom:20px">'
        '<div style="font-size:13px;color:#0b0b0b;line-height:1.5">'
        f'<b>{names}</b> moved to the attached PDF '
        f'(<b>{pdf_name}</b>). Today was big enough that the full report '
        "would have hit Gmail's size limit and been cut off mid-page, so the "
        f'{plural} attached in full instead of arriving half-printed. '
        'Nothing was dropped.</div></div>')


# Print-only, and only for the PDF -- the email body never sees this.
#
# A Call Detail row that straddles a page break makes Chromium paint that row's
# collapsed left border down the FULL height of the next page. On the first
# build, Mary Gunn's yellow rail ran the entire length of the following page,
# straight through Mike's section, so every row under it looked like it was
# tagged "lost, never quoted". Keeping rows whole fixes the colour bleed and
# stops summaries splitting mid-sentence at the same time.
PRINT_CSS = ("<style>@media print{.cdt tr{page-break-inside:avoid;"
             "break-inside:avoid}.cdh{page-break-inside:avoid;"
             "break-inside:avoid}}</style>")


def _standalone(report_html, panels_html, day):
    """Wrap the shed panels in the report's own <head>, so the PDF matches."""
    head_end = report_html.index("</head>")
    head = report_html[:head_end] + PRINT_CSS + "</head>"
    title = re.search(r"<h1[^>]*>(.*?)</h1>", report_html, re.S)
    sub = re.search(r'<div class="subtitle">(.*?)</div>', report_html, re.S)
    return (head + '<body><div class="wrap"><div class="header">'
            f'<h1>{title.group(1) if title else "Call Detail"}</h1>'
            f'<div class="subtitle">{sub.group(1) if sub else day} '
            '&middot; moved out of the email body to stay under Gmail&rsquo;s '
            'size limit</div></div>'
            + "".join(panels_html) + '</div></body></html>')


def relieve(day, html, log=print):
    """(html, extra_pdf_or_None). Sheds panels only if the body will not fit."""
    if _fits(html):
        return html, None

    size = len(html.encode())
    log(f"  body is {size:,} bytes -- over the "
        f"{cfg.GMAIL_CLIP_BYTES:,} clip limit with {SAFETY_BYTES:,} reserved; "
        "shedding panels to PDF")

    shed, labels = [], []
    for heading, label in SHED_ORDER:
        if heading not in html:
            continue
        html, panel = rr.cut_panel(html, heading)
        shed.append(panel)
        labels.append(label)
        log(f"    moved {label} ({len(panel.encode()):,} bytes)")
        if _fits(html):
            break
    else:
        if not _fits(html):
            # Every sheddable panel is gone and it still does not fit. Send what
            # is left rather than nothing; the hard guard in send_digest is the
            # last word and this at least gives it its best shot.
            log("    WARNING: still over the limit with every panel shed")

    # Name the file after what is in it, so the attachment is self-explaining
    # in a phone's mail list where the body text is not visible.
    slug = (labels[0].replace(" ", "_").replace("&amp;", "and")
            if len(labels) == 1 else "Report_Detail")
    name = f"{slug}_{day}.pdf"
    src = ROOT / f"out/{slug}_{day}.html"
    src.write_text(_standalone(html, shed, day))

    import attachments
    dest = ROOT / f"out/{name}"
    attachments.to_pdf(str(src), str(dest), landscape=False)
    # Panel headings render through text-transform:uppercase, so the PDF text
    # layer carries "TASK COMPLETION AUDIT", not the mixed case we cut on.
    # Check both rather than fail a good PDF over letter case.
    want = labels[0]
    pages, chars, missing = attachments.verify_pdf(str(dest), [want])
    if missing:
        pages, chars, missing = attachments.verify_pdf(str(dest), [want.upper()])
    if missing or chars < 500:
        raise SystemExit(
            f"{name} did not render ({pages} pages, {chars:,} chars, "
            f"missing {missing}) -- refusing to send")
    log(f"    {name}: {pages} pages, {chars:,} characters")

    i = html.index(NOTICE_ANCHOR)
    html = html[:i] + _notice(labels, name) + html[i:]
    log(f"  body now {len(html.encode()):,} bytes")
    return html, str(dest)
