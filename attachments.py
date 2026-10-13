"""Render an HTML file to PDF (the Missed Call Audit, ops only) and verify
it; qp_safe is kept for any HTML body that carries `=XX` sequences.

Until 2026-10-13 this also built the Notes & Methodology and Recontact
Detail PDFs for the template email; email_digest.py replaced that email.

WHY PDF INSTEAD OF HTML
-----------------------
The attachments were delivered as .html through TEST 9 and TEST 10 and arrived
unreadable both times. The mechanism is quoted-printable: `Recontact_Detail`
carries 108 AgencyZoom links shaped `?id=86771961`, and `=86` is a valid QP
escape meaning byte 0x86. Any mail hop that treats the part as text and
QP-decodes it without the sender having escaped `=` as `=3D` injects 109 random
bytes, the file stops being valid UTF-8, and it opens as garbage.

This is not new and it is not confined to attachments. The TEST 7 body -- the
build Frank approved -- has all 27 of its inline lead links mangled the same
way. They have never been clickable. Only the attachments survived that round,
which is why nobody noticed.

PDF removes the entire class of failure: it is binary, so it is always
base64-encoded and never QP-encoded. Gmail also previews PDFs inline, so the
notes can be read on a phone without downloading anything. Chromium preserves
hyperlinks through print-to-PDF, so the AgencyZoom links stay live.

The body still has to go as HTML, so it gets qp_safe() instead -- every `=`
followed by two hex digits becomes `&#61;`, which HTML parsers decode back to
`=` in both text and attribute values. Proven with quopri: the escaped form
survives a QP decode byte-for-byte unchanged.
"""
import pathlib
import re

QP_HAZARD = re.compile(r'=(?=[0-9A-Fa-f]{2})')
# <style> and <script> content is NOT entity-decoded by HTML parsers, so an
# escape inside one would render literally. Neither attachment nor body has a
# "=XX" sequence inside a style block (checked), but skip them to be safe.
BLOCK_RE = re.compile(r'(<(style|script)\b[^>]*>.*?</\2>)', re.S | re.I)


def qp_safe(html):
    """Escape quoted-printable escape sequences, outside style/script.

    Built with finditer over the protected spans rather than re.split: BLOCK_RE
    has two capture groups, so split() interleaves BOTH of them into the result
    list, and naive index arithmetic silently drops content. An earlier version
    did exactly that and emptied the file -- 0 divs, 0 links. Length is asserted
    to be non-decreasing as a cheap guard against the same class of bug.
    """
    out, pos = [], 0
    for m in BLOCK_RE.finditer(html):
        out.append(QP_HAZARD.sub('&#61;', html[pos:m.start()]))
        out.append(m.group(0))          # style/script passes through untouched
        pos = m.end()
    out.append(QP_HAZARD.sub('&#61;', html[pos:]))
    result = "".join(out)
    if len(result) < len(html):
        raise SystemExit("qp_safe lost content -- refusing to emit")
    return result


def to_pdf(src_html_path, dest_pdf_path, landscape=False):
    """Render an HTML file to PDF with Chromium, preserving links."""
    from playwright.sync_api import sync_playwright
    src = pathlib.Path(src_html_path).resolve()
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = b.new_page()
        pg.goto(f"file://{src}")
        pg.wait_for_timeout(500)
        pg.pdf(path=dest_pdf_path, format="Letter", landscape=landscape,
               print_background=True,
               margin={"top": "12mm", "bottom": "12mm",
                       "left": "10mm", "right": "10mm"})
        b.close()
    return dest_pdf_path


def verify_pdf(path, must_contain):
    """Read the PDF back and confirm the text really survived."""
    import pdfplumber
    text = []
    with pdfplumber.open(path) as pdf:
        pages = len(pdf.pages)
        for p in pdf.pages:
            text.append(p.extract_text() or "")
    joined = "\n".join(text)
    missing = [s for s in must_contain if s not in joined]
    return pages, len(joined), missing
