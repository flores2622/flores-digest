"""Match a day's RingCentral calls to AgencyZoom leads, and pull their notes.

This is the join the whole report rests on. RingCentral knows a producer dialled
+19285550134 for 71 seconds; AgencyZoom knows that number belongs to a lead in
Quotes Presented with a note from that morning. Neither system knows they are
the same event.

Key rule (Notes & Methodology, Aug 12): LIVE CONTACT IS NOT A DURATION RULE.
It is established from producer-written AgencyZoom notes cross-referenced to the
call log -- "a 28-second call can be a live contact while a longer one is a
voicemail." Confirmed independently: no duration threshold reproduces the
published contact rates on any day tested.

CALL VOLUME is distinct numbers dialled, new business only. A number is excluded
when its household has a service or renewal task due that day assigned to the
same producer, or a service/renewal ticket opened that day with that producer as
CSR, or it matches no AgencyZoom record at all.
"""
import collections
import json
import pathlib

from az_client import AgencyZoom
from az_corpus import e164, fetch, phone_index
from az_tasks import service_reason
from digest_config import PRODUCERS, TRAINING_LEAD_OWNERS
from rc_client import owner_ext_id

NOTE_CACHE = pathlib.Path("data/notes")


def producer_dials(day):
    """{producer: {number: [call records]}} -- outbound only."""
    recs = json.load(open(f"data/rc_raw_{day}.json"))
    names = {v["rc_id"]: k for k, v in PRODUCERS.items()}
    out = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in recs:
        who = names.get(owner_ext_id(r) or "")
        if not who or r.get("direction") != "Outbound":
            continue
        num = (r.get("to") or {}).get("phoneNumber")
        if num:
            out[who][num].append(r)
    return out


def build_context(day):
    leads = fetch()
    lead_idx = phone_index(leads)
    customers = json.load(open("data/az_customers_all.json"))
    cust_idx = collections.defaultdict(list)
    for c in customers:
        for f in ("phone", "secondaryPhone"):
            p = e164(c.get(f))
            if p:
                cust_idx[p].append(c)

    tasks = json.load(open(f"data/az_tasks_{day}.json"))
    az_ids = {v["az_id"]: k for k, v in PRODUCERS.items()}
    svc_customers = collections.defaultdict(set)
    for t in tasks:
        if not service_reason(t) or not t.get("customerId"):
            continue
        for a in t.get("assignees") or []:
            if a.get("id") in az_ids:
                svc_customers[az_ids[a["id"]]].add(t["customerId"])
    return lead_idx, cust_idx, svc_customers


def pick_lead(cands):
    """Duplicate lead records are pervasive. Prefer the most recently active."""
    if not cands:
        return None
    return sorted(cands, key=lambda l: (l.get("lastActivityDate") or "",
                                        l.get("createDate") or ""))[-1]


def classify(day):
    """Per producer: which dialled numbers count as new-business call volume."""
    lead_idx, cust_idx, svc_customers = build_context(day)
    dials = producer_dials(day)
    out = {}
    for who, bynum in dials.items():
        rows = []
        for num, calls in bynum.items():
            cands = lead_idx.get(num, [])
            lead = pick_lead(cands)
            custs = cust_idx.get(num, [])
            excluded = None
            if not cands and not custs:
                excluded = "no AgencyZoom record"
            elif not cands:
                excluded = "customer record only (service/renewal)"
            elif any(c["id"] in svc_customers.get(who, set()) for c in custs):
                excluded = "service/renewal task due today for this producer"
            rows.append({
                "number": num,
                "lead_id": lead.get("id") if lead else None,
                "lead_name": (f"{(lead.get('firstname') or '').strip()} "
                              f"{(lead.get('lastname') or '').strip()}".strip()
                              if lead else None),
                "assigned_to": lead.get("assignedTo") if lead else None,
                "calls": len(calls),
                "talk_seconds": sum(c.get("duration", 0) for c in calls),
                "excluded": excluded,
                "training_lead": bool(lead and lead.get("assignedTo")
                                      in TRAINING_LEAD_OWNERS),
            })
        out[who] = rows
    return out


def fetch_notes(lead_ids, az=None):
    """Cache lead notes to disk -- these drive live-contact and outcome logic."""
    NOTE_CACHE.mkdir(parents=True, exist_ok=True)
    az = az or AgencyZoom()
    got = {}
    for i, lid in enumerate(sorted(set(lead_ids))):
        f = NOTE_CACHE / f"{lid}.json"
        if f.exists():
            got[lid] = json.loads(f.read_text())
            continue
        try:
            n = az.lead_notes(lid)
        except Exception:
            n = []
        f.write_text(json.dumps(n))
        got[lid] = n
    return got


if __name__ == "__main__":
    import sys
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-08-13"
    rows = classify(day)
    for who, rs in sorted(rows.items()):
        counted = [r for r in rs if not r["excluded"]]
        print(f"{who:18} dialled {len(rs):3}  counted {len(counted):3}  "
              f"excluded {len(rs) - len(counted):2} "
              f"{collections.Counter(r['excluded'] for r in rs if r['excluded'])}")
    ids = [r["lead_id"] for rs in rows.values() for r in rs if r["lead_id"]]
    print(f"\nfetching notes for {len(set(ids))} leads...")
    notes = fetch_notes(ids)
    types = collections.Counter(n.get("type") for v in notes.values() for n in v)
    print("note types seen:", dict(types))
