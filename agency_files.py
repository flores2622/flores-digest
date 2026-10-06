"""Which agency's setup files to read.

Flores's live at the repository root (staff.json, agencyzoom.json,
lead_sources.json, goals.json, coaching/carrier/<carrier>/). Another
agency's live under agencies/<key>/ -- the same four files plus a carrier/
folder -- and are picked by the PANTHEON_AGENCY environment variable:

    PANTHEON_AGENCY=copperline python3 agency_check.py --fix

Every reader (staff, agencyzoom, lead_sources, goals, coaching_text) asks
here for its file, so one variable switches the whole pipeline, the
generated Worker and page files and the rendered coaching documents to
that agency. With it unset, nothing changes. The generated files are
still written to their one place under site/ and coaching/: a deploy is
for one agency at a time (NEW_AGENCY.md).
"""
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
KEY = (os.environ.get("PANTHEON_AGENCY") or "").strip()
DIR = ROOT / "agencies" / KEY if KEY else ROOT

if KEY and not DIR.is_dir():
    raise FileNotFoundError(f"PANTHEON_AGENCY={KEY!r}: no agencies/{KEY}/ folder")


def path(name):
    """The agency's copy of a setup file (staff.json, agencyzoom.json ...)."""
    return DIR / name


def carrier_dir(carrier):
    """The coaching documents' carrier layer: the agency's own carrier/
    folder when it has one, else coaching/carrier/<carrier>/."""
    own = DIR / "carrier"
    if KEY and own.is_dir():
        return own
    return ROOT / "coaching" / "carrier" / (carrier or "generic").lower()
