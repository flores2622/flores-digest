"""Repair AgencyZoom lead links mangled by quoted-printable decoding.

THE DAMAGE. Every inline lead link in the report body is shaped
`?id=86771961`. `=86` is a valid quoted-printable escape meaning byte 0x86, so
any hop that QP-decodes the part without the sender having escaped `=` as `=3D`
eats the first two digits of every lead id and leaves one byte in their place.
This has been happening since at least TEST 7 -- the build Frank approved --
where all 27 inline lead links are broken. Nobody noticed because the links
still look like links; they just go nowhere.

RECOVERY, in order of confidence:

  1. NAME MAP. Recontact_Detail carries the same leads with intact ids, because
     that part was base64-encoded and survived. Match on the anchor text.
     Resolves 25 of 31.

  2. BYTE INVERSION. If the surviving byte is < 0x80 it round-trips: the byte
     value IS the two lost hex digits. 0x70 -> "70", 0x16 -> "16". Note these
     include non-printable control bytes (0x15, 0x16), so test on ord() < 128,
     not on str.isprintable(). Resolves 5 more.

  3. API LOOKUP. If the byte was >= 0x80 it was invalid UTF-8 and Gmail replaced
     it with U+FFFD, destroying the value. Lead ids are numeric, so the lost
     pair is two decimal digits whose byte value is >= 0x80 -- that is 80-99,
     twenty candidates. Fetch each and keep the one whose name matches.
     Resolves the last 1.

Every recovered id is then verified against AgencyZoom by name before it is
written back, so a wrong guess cannot ship.
"""
import re
import unicodedata

LINK_RE = re.compile(
    r'href="https://app\.agencyzoom\.com/lead\?id([^"]{0,14})"([^>]*)>([^<]{0,60})</a>')
INTACT_RE = re.compile(r'lead\?id=(\d+)"[^>]*>([^<]+)</a>')


def _norm(s):
    s = unicodedata.normalize("NFKD", s)
    return re.sub(r'\s+', ' ', s).strip().casefold()


def name_map(intact_html):
    return {_norm(t): i for i, t in INTACT_RE.findall(intact_html)}


def candidates(fragment, names):
    """Possible full ids for one mangled fragment, best guess first."""
    head, suffix = fragment[0], fragment[1:]
    if head == "=":                       # never decoded; already intact
        return [suffix]
    nm = names.get(_norm(fragment[0] and "")) if False else None  # placeholder
    out = []
    if ord(head) < 128:                   # byte survived -> digits recoverable
        pair = f"{ord(head):02d}" if ord(head) < 100 else f"{ord(head):02X}"
        pair = f"{ord(head):02X}"
        if pair.isdigit():
            out.append(pair + suffix)
    else:                                 # U+FFFD -- value destroyed
        out.extend(f"{d}{suffix}" for d in range(80, 100))
    return out


def repair(body_html, intact_html, az=None, verify=True):
    """Return (repaired_html, report rows)."""
    names = name_map(intact_html)
    rows, cache = [], {}

    def fix(m):
        frag, attrs, label = m.group(1), m.group(2), m.group(3)
        key = (frag, label)
        if key in cache:
            new = cache[key]
        else:
            lead = _norm(label)
            new, how = None, None
            if lead in names:
                new, how = names[lead], "name map"
            else:
                for c in candidates(frag, names):
                    if len(c) < 7:
                        continue
                    if az is None:
                        new, how = c, "byte inversion (unverified)"
                        break
                    got = _safe_lead(az, c)
                    if got and _norm(got) == lead:
                        new, how = c, "API lookup"
                        break
                if new is None:
                    rows.append((label, frag, None, "UNRECOVERABLE"))
                    return m.group(0)
            if verify and az is not None and how == "name map":
                got = _safe_lead(az, new)
                how = "name map + API confirmed" if got and _norm(got) == lead \
                    else "name map (API MISMATCH)"
            cache[key] = new
            rows.append((label, frag, new, how))
        return (f'href="https://app.agencyzoom.com/lead?id={new}"{attrs}>'
                f'{label}</a>')

    return LINK_RE.sub(fix, body_html), rows


def _safe_lead(az, lead_id):
    try:
        j = az.lead(lead_id) or {}
    except Exception:
        return None
    d = j.get("lead") if isinstance(j.get("lead"), dict) else j
    first = (d.get("firstname") or "").strip()
    last = (d.get("lastname") or "").strip()
    mid = (d.get("middlename") or "").strip()
    full = " ".join(x for x in (first, mid, last) if x)
    return full or None


if __name__ == "__main__":
    import sys
    from az_client import AgencyZoom
    body = open(sys.argv[1] if len(sys.argv) > 1
                else "out/Ops_Report_2026-08-12_util.html").read()
    intact = open("recovered/Recontact_Detail_2026-08-12.html").read()
    az = AgencyZoom()
    out, rows = repair(body, intact, az)
    bad = [r for r in rows if r[2] is None or "MISMATCH" in (r[3] or "")]
    for label, frag, new, how in rows:
        flag = "  <<<" if (new is None or "MISMATCH" in how) else ""
        print(f"  {label[:30]:30} {frag!r:12} -> {str(new):10} {how}{flag}")
    print(f"\n{len(rows) - len(bad)}/{len(rows)} links repaired and verified")
    if bad:
        raise SystemExit(f"{len(bad)} link(s) could not be verified -- not writing")
    open("out/Ops_Report_2026-08-12_final.html", "w").write(out)
    print("wrote out/Ops_Report_2026-08-12_final.html")
