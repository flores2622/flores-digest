"""Pull the AgencyZoom lead corpus once and index it by phone number.

This is the foundation of the call-to-lead matcher. Everything downstream --
new-business classification, live contacts, outcome colours, recontact -- needs
to answer "which lead did this RingCentral number belong to".

Notes on the data (HANDOFF_4 s5):
  * Pervasive DUPLICATE lead records for the same person. Dedupe by
    (producer, name); keep every id so stage history can be merged later.
  * Lead dates are UTC; notes are Arizona-local.
"""
import json
import pathlib
import re
import sys

from az_client import AgencyZoom

CACHE = pathlib.Path("data/az_leads_all.json")


def e164(raw):
    """RingCentral gives +1XXXXXXXXXX; AgencyZoom gives (928) 726-0300."""
    if not raw:
        return None
    d = re.sub(r'\D', '', str(raw))
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    return f"+1{d}" if len(d) == 10 else None


def fetch(force=False):
    if CACHE.exists() and not force:
        return json.loads(CACHE.read_text())
    az = AgencyZoom()
    # No date filter -> the whole corpus.
    leads = az._paged("/v1/api/leads/list", "leads", {})
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(leads))
    return leads


def phone_index(leads):
    """+1XXXXXXXXXX -> [lead, ...] (a number can hit several duplicate records)."""
    idx = {}
    for l in leads:
        for field in ("phone", "secondaryPhone"):
            p = e164(l.get(field))
            if p:
                idx.setdefault(p, []).append(l)
    return idx


if __name__ == "__main__":
    leads = fetch(force="--force" in sys.argv)
    idx = phone_index(leads)
    print(f"leads: {len(leads):,}")
    print(f"distinct phone numbers indexed: {len(idx):,}")
    multi = sum(1 for v in idx.values() if len(v) > 1)
    print(f"numbers hitting more than one lead record: {multi:,}")
    print(f"leads with no usable phone: "
          f"{sum(1 for l in leads if not e164(l.get('phone')) and not e164(l.get('secondaryPhone'))):,}")
