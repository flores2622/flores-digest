"""Build the two companion attachments as PDF, and make the body QP-safe.

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


if __name__ == "__main__":
    import quopri
    jobs = [
        ("recovered/Notes_and_Methodology_2026-08-12.html",
         "out/Notes_and_Methodology_2026-08-12.pdf", False,
         ["Utilization and Efficiency", "Live Contact", "Avg Talk Time"]),
        ("recovered/Recontact_Detail_2026-08-12.html",
         "out/Recontact_Detail_2026-08-12.pdf", True,
         ["Lance Savard", "At risk of going cold", "Pamela Rice"]),
    ]
    # notes attachment gets the updated footnote 6 first
    import notes_patch
    src = pathlib.Path("recovered/Notes_and_Methodology_2026-08-12.html").read_text()
    pathlib.Path("out/Notes_and_Methodology_2026-08-12.html").write_text(
        notes_patch.patch(src))
    jobs[0] = ("out/Notes_and_Methodology_2026-08-12.html",) + jobs[0][1:]

    for src, dest, land, checks in jobs:
        to_pdf(src, dest, land)
        pages, chars, missing = verify_pdf(dest, checks)
        size = pathlib.Path(dest).stat().st_size
        print(f"{dest:48} {pages:3} pages  {size:>8,}b  {chars:>7,} chars text"
              f"  {'OK' if not missing else 'MISSING ' + str(missing)}")

    body = pathlib.Path("out/Ops_Report_2026-08-12_util.html").read_text()
    safe = qp_safe(body)
    pathlib.Path("out/Ops_Report_2026-08-12_final.html").write_text(safe)
    print(f"\nbody qp_safe: {len(QP_HAZARD.findall(body))} hazards escaped")
    print(f"  survives a QP decode unchanged: "
          f"{quopri.decodestring(safe.encode()) == safe.encode()}"
          f"   (before: {quopri.decodestring(body.encode()) == body.encode()})")
