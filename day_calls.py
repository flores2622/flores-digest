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
import datetime as dt
import json
import pathlib

from az_client import AgencyZoom
from az_corpus import e164, fetch, phone_index
from az_tasks import service_reason
from digest_config import PRODUCERS, TRAINING_LEAD_OWNERS, is_test_lead
from rc_client import owner_ext_id

NOTE_CACHE = pathlib.Path("data/notes")


def dials_from(recs):
    """{producer: {number: [call records]}} -- outbound only."""
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


def producer_dials(day):
    """Dials made on `day` -- the basis for call volume and contact rate."""
    return dials_from(json.load(open(f"data/rc_raw_{day}.json")))


def window_dials(day):
    """Dials over the trailing recontact window (see daily.pull_sources).

    Recontact asks "how many dials since this lead entered its stage", which
    reaches back weeks. Answering that from the single-day log reported 0 for
    every lead not dialled today.
    """
    return dials_from(json.load(open(f"data/rc_window_{day}.json")))


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

    # OPEN service tickets (SRs) by dialled number, but only where the CALLING
    # producer is the CSR (Frank, 2026-08-25). Dana Sanchez and Genaro Cortez
    # were both counted as new-business live contacts for Crystal when both are
    # "full blown renewals" -- an open Renewal SR with Crystal as CSR, the
    # linked lead sold or smart-cycled and assigned to someone else. Lead status
    # cannot express this: 19 of Aug 24's 32 contacts sat on a non-active lead
    # and most were smart-cycled BY the call being reported. The SR can, and it
    # is narrow -- 2 of 32 contacts, 5 of 190 dials.
    #
    # The CSR test is what keeps it honest. Wesley Knowlton has an open Missing
    # Documents ticket under a different CSR, and Mike's call to him is real new
    # business. Angel Inda has no ticket at all, so Lorena's call stays new
    # business, which is right -- "it will ALWAYS be new business".
    svc_phones = collections.defaultdict(list)
    sr_file = pathlib.Path(f"data/az_service_tickets_{day}.json")
    if sr_file.exists():
        for t in json.loads(sr_file.read_text()):
            # POINT IN TIME: did this ticket exist yet on `day`? Anything else
            # makes a rebuild disagree with the original run, which is fatal
            # for weekly and monthly roll-ups.
            # Rebuilding Aug 25 on Aug 26 was excluding Mike's Abraham
            # Carrillo dial on a ticket created 2026-08-26 -- a day AFTER the
            # call it was being used to explain.
            #
            # There is no closed state to fall back on here: status 0 is
            # DELETED (Frank confirmed 2026-09-02) and az_client now fetches
            # status=[1] only, so every ticket in this file is live. The
            # completeDate/lastActivityDate close-date fallback added
            # 2026-09-01, when [0, 1] was believed to mean open+closed, is
            # gone -- a live ticket is simply open on `day`.
            created = str(t.get("createDate") or "")[:10]
            if created and created > day:
                continue
            who = az_ids.get(t.get("csr"))
            if not who:
                continue
            ph = e164(t.get("phone"))
            if ph:
                svc_phones[(who, ph)].append(t)
    return lead_idx, cust_idx, svc_customers, svc_phones


# Frank, 2026-08-26: "lets do 30 or 60 days". 60 -- missing documents and
# paperless enrolments on a fresh sale routinely drag past a month, and the
# open-lead test above is what actually does the discriminating, so the window
# only has to be generous enough to name the reason honestly.
RECENT_SALE_DAYS = 60


def is_household_housekeeping(cands, day):
    """This number is an existing customer and nobody is selling them anything.

    Frank, 2026-08-26: "we also need to exclude those service request calls and
    calls to recent sales (if not to sell an additional product) because they
    are doing housekeeping for their recent sells, its not new business".

    Three tests, in order, over EVERY lead record on the number:

    1. Was anything sold to this household? status 2 with convertedHouseholdId.
       All 1,517 status-2 leads carry a soldDate and nothing else does.
    2. Was it sold TODAY? Then this IS the sale call -- Hugo Bojorquez, whose
       two policies bound on 2026-08-25. Never exclude it.
    3. Is there an OPEN lead (status not 2) created on or after the sale? That
       is the additional-product attempt Frank carved out, and AgencyZoom names
       it plainly: Adriana Navarro's is "Life Cross Sell", created 8/21 against
       a 8/14 sale; Cipriano Duarte's is a "Winback" opened the day after his.
       Both are real new business and both stay in.

    What is left is a customer with no open opportunity -- Mike's day-after
    call to Abraham Carrillo, Coral's to Francisco Vizcaino. Housekeeping.

    Age is deliberately NOT a test of WHETHER to exclude -- a 2022 customer
    being re-quoted has an open lead and passes on step 3, which is why this
    catches 4 of 212 dials rather than the 34 a bare "sold household" test
    would take. Age only decides WHICH reason is reported, so the audit can
    tell "finishing off last week's sale" from "an old customer with nothing
    open". Both are excluded either way.

    Returns None, or the reason string.
    """
    sold = [l for l in cands
            if l.get("status") == 2 and l.get("convertedHouseholdId")
            and l.get("soldDate")]
    if not sold:
        return None
    last_sale = max(str(l["soldDate"])[:10] for l in sold)
    if last_sale >= day:
        return None
    if any(l.get("status") != 2
           and str(l.get("createDate") or "")[:10] >= last_sale
           for l in cands):
        return None
    try:
        age = (dt.date.fromisoformat(day)
               - dt.date.fromisoformat(last_sale)).days
    except ValueError:
        age = None
    if age is not None and age <= RECENT_SALE_DAYS:
        return "housekeeping on a recent sale"
    return "existing customer, nothing open"


def pick_lead(cands, day=None):
    """Duplicate lead records are pervasive. Prefer the most recently active.

    A lead SOLD on `day` outranks recency (Frank, 2026-08-26). Hugo Bojorquez
    had three records: 61514431 (status 2, soldDate 2026-08-25, the real one)
    and 88468860, a duplicate created at 20:20 that same evening which Coral
    then marked Dead with Loss Reason "Duplicate Lead". Recency picked the
    duplicate, so the row read "Quoted on this call, Dead" for a household that
    bound two policies worth $1,751 that afternoon. status 2 is unambiguous --
    all 1,517 of them carry a soldDate and nothing else does.
    """
    if not cands:
        return None
    sold_today = [l for l in cands
                  if day and str(l.get("soldDate") or "").startswith(day)]
    pool = sold_today or cands
    return sorted(pool, key=lambda l: (l.get("lastActivityDate") or "",
                                       l.get("createDate") or ""))[-1]


def classify(day):
    """Per producer: which dialled numbers count as new-business call volume."""
    lead_idx, cust_idx, svc_customers, svc_phones = build_context(day)
    dials = producer_dials(day)
    out = {}
    for who, bynum in dials.items():
        rows = []
        for num, calls in bynum.items():
            cands = lead_idx.get(num, [])
            lead = pick_lead(cands, day)
            custs = cust_idx.get(num, [])
            excluded = None
            if not cands and not custs:
                excluded = "no AgencyZoom record"
            elif not cands:
                excluded = "customer record only (service/renewal)"
            elif any(c["id"] in svc_customers.get(who, set()) for c in custs):
                excluded = "service/renewal task due today for this producer"
            elif svc_phones.get((who, num)):
                wf = svc_phones[(who, num)][0].get("workflowName") or "service"
                excluded = f"open {wf} ticket with this producer as CSR"
            elif lead and is_test_lead(lead):
                excluded = "test/dummy lead record"
            elif is_household_housekeeping(cands, day):
                excluded = is_household_housekeeping(cands, day)
            rows.append({
                "number": num,
                "lead_id": lead.get("id") if lead else None,
                # EVERY duplicate record on this number, so the note search can
                # cover all of them (see live_contact.evidence).
                "lead_ids": [c.get("id") for c in cands if c.get("id")],
                # AgencyZoom lead status 2 == sold, and every status-2 lead
                # carries a soldDate. This is the ONLY join from a dialled
                # number to a sale: policy records hold no name, phone,
                # customerId or leadId -- only leadSourceId, which is the
                # marketing source and is shared by thousands of policies.
                "sold_today": bool(lead and str(lead.get("soldDate") or ""
                                                ).startswith(day)),
                # An ACTIVE lead on this number (status 0) means somebody is
                # working this household for new business right now. "Ever
                # sold" cannot carry this test: Carlos Cruz and Ruben Serrano
                # are BOTH converted customer households with a customer
                # record, and the only thing that separates them is that
                # Carlos has an open status-0 lead assigned to Coral while
                # Ruben's only lead is status 5.
                "open_lead": any(c.get("status") == 0 for c in cands),
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
