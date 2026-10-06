"""The coaching documents, rendered from their templates for THIS agency and
its carrier.

coaching/METHODOLOGY.md and coaching/TRAINING.md -- what every coaching read,
Role Play grade, Apollo chat answer and Training deck is built on -- are
WRITTEN by this script from coaching/src/METHODOLOGY.md and
coaching/src/TRAINING.md. The templates hold the method; two layers fill
them:

  the carrier layer   coaching/carrier/<carrier>/ (staff.json's
                      agency.carrier, lower-cased): carrier.json (the name,
                      its possessive, how transcripts mishear it, the quoting
                      system, its website) and the occupation-discount text
                      for METHODOLOGY (occupations_methodology.md) and the
                      Training deck (occupations_training.md)
  the agency layer    staff.json: the agency's name, short name, the other
                      names people say for it (also_known_as), how
                      transcripts mishear it (misheard_as), the front desk
                      (the service person whose playbook role is front_desk)
                      and the staff member whose name as a lead source is a
                      referral (the referral_source tag)

Placeholders are {{key}}. Everything else in the templates -- the rules,
Frank's rulings and their dates, the example calls -- is the method and
stays as written. ROLEPLAY.md names no carrier or agency and is not rendered.

    python3 coaching_text.py --write   render coaching/METHODOLOGY.md and TRAINING.md
    python3 coaching_text.py --check   fail if either is out of date
    python3 coaching_text.py --fills   print every placeholder's value

Edit the templates or a layer, never the rendered files.
"""
import json
import pathlib
import re
import sys

import staff

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "coaching" / "src"
OUT = ROOT / "coaching"
DOCS = ("METHODOLOGY.md", "TRAINING.md")
_PH = re.compile(r"\{\{(\w+)\}\}")


def carrier_dir():
    return ROOT / "coaching" / "carrier" / (staff.CARRIER or "generic").lower()


def fills():
    cdir = carrier_dir()
    c = json.loads((cdir / "carrier.json").read_text())
    name = c.get("name") or staff.CARRIER
    qs = c.get("quoting_system") or "the quoting system"
    front = [p for p in staff.service_team() if (p.get("service") or {}).get("playbook") == "front_desk"]
    referral = staff.tagged("referral_source")
    names = list(staff.AGENCY.get("also_known_as") or []) + [staff.AGENCY_NAME]
    return {
        "carrier": name,
        "carrier_pos": c.get("possessive") or (name + ("'" if name.endswith("s") else "'s")),
        "carrier_misheard": c.get("misheard_as") or name,
        "quoting_system": qs,
        "quoting_system_a": ("an " if qs[:1].lower() in "aeiou" else "a ") + qs,   # "an ALTA screen"
        "carrier_site": c.get("website") or (name + ".com"),
        "carrier_site_lc": (c.get("website") or (name + ".com")).lower(),
        "occupations_methodology": (cdir / "occupations_methodology.md").read_text().rstrip("\n"),
        "occupations_training": (cdir / "occupations_training.md").read_text().rstrip("\n"),
        "agency_short": staff.SHORT_NAME,
        "agency_misheard": staff.AGENCY.get("misheard_as") or staff.SHORT_NAME,
        # the names people say for the agency, the way the greeting rule lists them
        "agency_names": ", ".join(f'"{n}"' for n in names),
        "front_desk": staff.first(front[0]) if front else "the front desk",
        "referral_staff": referral[0]["name"] if referral else "a staff member Frank names",
    }


def render(doc, f=None):
    f = f or fills()
    text = (SRC / doc).read_text()
    missing = sorted({k for k in _PH.findall(text) if k not in f})
    if missing:
        raise KeyError(f"coaching/src/{doc}: no fill for {missing}")
    return _PH.sub(lambda m: f[m.group(1)], text)


def main(argv):
    if "--fills" in argv:
        for k, v in fills().items():
            print(f"{k}: {v if len(v) < 90 else v[:87] + '...'}")
        return 0
    f = fills()
    if "--write" in argv:
        for doc in DOCS:
            (OUT / doc).write_text(render(doc, f))
            print(f"wrote coaching/{doc}")
        return 0
    if "--check" in argv:
        stale = [doc for doc in DOCS if not (OUT / doc).exists() or (OUT / doc).read_text() != render(doc, f)]
        for doc in stale:
            print(f"coaching/{doc} is out of date: run python3 coaching_text.py --write")
        if not stale:
            print("coaching/METHODOLOGY.md and TRAINING.md match their templates")
        return 1 if stale else 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
