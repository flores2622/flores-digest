"""Frank's own lists for Pantheon's CRM, and where each AgencyZoom entry lands.

    python3 crm_lists.py                    print the lists
    python3 crm_lists.py place <name> ...   where a lead source / pipeline / SR
                                            category of that name is placed
    python3 crm_lists.py --discover         every AgencyZoom lookup the saved
                                            data/ files hold, with its place;
                                            the unsorted first
    python3 crm_lists.py --check            the lists are well formed

AgencyZoom's lists grew by accretion (97 lead sources, 16 sales pipelines,
43 SR categories on 2026-10-06). The CRM keeps Frank's lists as the real
ones (the `lists` table) and a map from every AgencyZoom id to one of his
entries (`list_map`); the records keep AgencyZoom's ids and the pages read
through the map. Frank decided the shape on 2026-10-06:

  * lead sources: the partner, vendor or staff member is a FIELD on the
    source, not a source of its own; **Call-in / Walk-in is one source with
    "How they found us"** (called, walked in, Google, the carrier's site);
    **the four cross-sell lines stay apart**; BOB and Rewrite stay as the
    two not-a-sale sources (lead_sources.NOT_A_SALE);
  * sales pipelines: five -- New Business (**AZ Sun Quote Tracker goes
    here**, not Commercial), Quotes Not Closed, Not Quoted, Life, Commercial;
    **IL Interested and Transfer Pending stay as stages for now** ("leave
    the IL interested and pending transfer stages for now");
  * **the SR category IS the service pipeline** ("the category is really the
    service pipeline it goes into"): Billing, Contingencies, Personal
    Renewals, Personal Endorsements, Commercial Renewals, Commercial
    Endorsements -- and Claims, the workflow Frank made on 2026-10-02, with
    the claim's type as its field. An SR lands on the pipeline its category
    is placed under; a category that says nothing (General, UNASSIGNED)
    follows the SR's workflow.

The placement rules below are by NAME, so a new AgencyZoom entry is placed
the night it first appears (crm_import.build calls add_rows); one no rule
knows is Unsorted on the Lists page for Frank to place. Every row is
written INSERT OR IGNORE, so a name or a placement set on the Lists page is
never overwritten by the nightly. The lists are this agency's -- another
agency writes its own (NEW_AGENCY.md).
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import lead_sources   # noqa: E402

# ---- Frank's lists -------------------------------------------------------------
# (id, name, detail_label, meaning). Ids are fixed: list_map rows point at them.
SOURCES = [
    (1, "Winback", None, "A former customer who insures elsewhere now; we are winning them back."),
    (2, "Internet lead", "Vendor", "A lead the agency bought or generated online; the vendor is the field."),
    (3, "Call-in / Walk-in", "How they found us", "Someone who came to us on their own: called, walked in, or found us online and asked for a call."),
    (4, "Cross-sell: Home no Auto", None, "We insure the home; selling the auto."),
    (5, "Cross-sell: Auto no Home", None, "We insure the auto; selling the home."),
    (6, "Cross-sell: Life", None, "An existing household; selling life. A sale here is a life sale, not a household sold."),
    (7, "Cross-sell: Umbrella / other", "Product", "An existing household; selling the umbrella or whatever the household is missing."),
    (8, "Existing client, new purchase", None, "An existing customer who bought something new and came to us to cover it."),
    (9, "Customer referral", "Referred by", "A customer's referral, or one that came through the referral staff member."),
    (10, "Lender referral", "Partner", "A loan officer or realtor sent us the home; the partner is the field."),
    (11, "Personal network", "Staff member", "A staff member's own network; each works their own."),
    (12, "Social media", "Network", "Reached the agency through its Instagram or LinkedIn."),
    (13, "Cold / event", "Event or list", "Dug out of the system, or a one-off list or event booth."),
    (14, "Commercial lead", "Generator", "Commercial lead generators and lists -- Cerberus's."),
    (15, "BOB", None, "Not a sale: CRM housekeeping for policies that were not sold."),
    (16, "Rewrite", None, "Not a sale: the service department's, from 2026-09-24."),
    (17, "Other", "What it was", "Little volume and no set meaning."),
]
SOURCE_OF_GROUP = {"winback": 1, "generated": 2, "inbound": 3, "existing_new_purchase": 8, "referral": 9,
                   "center_of_influence": 10, "personal_network": 11, "social_media": 12, "cold": 13,
                   "commercial": 14, "one_off": 17}
# (id, name, meaning) and the stages of each: (name, meaning, aliases AgencyZoom uses)
PIPELINES = [
    (1, "New Business", "Every new or updated lead comes into New here. The goal on a first contact is a one-call close."),
    (2, "Quotes Not Closed", "Quoted the last time we talked and it did not close."),
    (3, "Not Quoted", "Never got hold of them, or they declined even being quoted."),
    (4, "Life", "Life insurance leads."),
    (5, "Commercial", "Cerberus's: commercial leads, their quotes not closed and not quoted."),
]
_CYCLES = [("1st Cycle", "Smart-Cycled back for a first new attempt.", ("New 1st Cycle",)),
           ("2nd Cycle", "Smart-Cycled back a second time.", ("New 2nd Cycle",)),
           ("3rd Cycle", "The last cycle: deaded if it does not advance.", ("New 3rd Cycle",))]
_CONTACTED = ("Contacted", "We got hold of them and are working on a quote or waiting on info.", ("Contacted, In Progress",))
_QUOTED = ("Quoted", "We presented numbers and are following up on the quote.", ("Quotes Presented",))
STAGES = {
    1: [("New", "A new or updated lead.", ()), *_CYCLES,
        ("Contacted, In Progress", _CONTACTED[1], ("Contacted",)),
        ("Ready to Present", "The quote is ready; waiting to present it for a specific reason.", ()),
        ("Quotes Presented", _QUOTED[1], ("Quoted",)),
        ("Lender Referral", "An account a center of influence sent us, held out of the full automation.", ()),
        ("FSD (Pending Bind)", "Future sale date: sold, pending bind.", ()),
        # Frank, 2026-10-06: "leave the IL interested and pending transfer stages for now"
        ("IL Interested", "Not an agency stage (made for an outside texting company); kept for now.", ()),
        ("Transfer Pending", "Not an agency stage (made for an outside texting company); kept for now.", ())],
    2: [*_CYCLES, _CONTACTED, _QUOTED],
    3: [*_CYCLES, _CONTACTED, _QUOTED],
    4: [("New", "A new life lead.", ()), _CONTACTED, _QUOTED,
        ("Applications", "The application is being taken or has been submitted.", ()),
        ("Med. Records Needed", "The carrier needs medical records before it decides.", ()),
        ("Approved", "The carrier approved the life policy.", ())],
    5: [("New", "A new commercial lead.", ()), *_CYCLES, _CONTACTED,
        ("Applications", "Applications in.", ()), ("Underwriting", "With underwriting.", ()),
        ("Set Present Appt", "Presentation appointment set.", ()), _QUOTED, ("Bind", "Binding.", ())],
}
# The service pipelines, which are the SR categories (id, name, detail_label, meaning).
SERVICE = [
    (1, "Billing", "Payment", "Late payments, NOC, monthly and mortgagee billing."),
    (2, "Contingencies", None, "Anything pending on a policy: missing documents, verifications, underwriting requests."),
    (3, "Personal Renewals", "Carrier", "Personal-lines renewals, every carrier."),
    (4, "Personal Endorsements", "Change", "Changes, endorsements and basic service on personal lines."),
    (5, "Commercial Renewals", None, "Commercial renewals -- Cerberus's."),
    (6, "Commercial Endorsements", None, "Changes and service on commercial policies -- Cerberus's."),
    (7, "Claims", "Claim type", "Claims, opened and worked by a licensed service rep."),
]


def _norm(s):
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def stage_id(pipeline_id, n):
    return pipeline_id * 100 + n


# ---- placement -----------------------------------------------------------------
_COI = re.compile(r"^\s*(.+?)\s+(?:at|@)\s+(.+?)\s*$", re.I)
_VENDOR = {"smart financial live transfer": "Smart Financial (live transfer)", "old mvp leads": "MVP",
           "arizona insurance reports": "Arizona Insurance Reports"}


def place_source(name):
    """-> (list id, detail) or (None, None) when no rule knows the name."""
    n = lead_sources.norm(name)
    if not n:
        return None, None
    g = lead_sources.classify(name)
    raw = re.sub(r"\s+", " ", str(name)).strip().rstrip("!").strip()
    if g == "not_a_sale":
        return (15 if n == "bob" else 16), None
    if g == "cross_sell":
        if n == "home no auto":
            return 4, None
        if n == "auto no home":
            return 5, None
        if n == "life cross sell":
            return 6, None
        return 7, ("Umbrella" if n == "umbrella" else "Not specified")
    if g == "inbound":
        detail = "Called" if n == "call-in" else "Walked in" if n == "walk-in" else "Google" if "google" in n else raw
        return 3, detail
    if g == "generated":
        return 2, _VENDOR.get(n, raw)
    if g == "one_off":
        if n == "hometown quotes":            # a vendor, not a one-off (CRM.md's proposal)
            return 2, "Hometown Quotes"
        return 17, raw
    if g == "center_of_influence":
        m = _COI.match(raw)
        if m:
            return 10, f"{m.group(2).strip()} ({m.group(1).strip()})"
        return 10, ("Former partner" if "no longer" in n else raw)
    if n == "mortgage lenders":
        return 10, "Not specified"
    if g in ("referral", "personal_network", "social_media", "cold", "commercial"):
        detail = None if n in ("existing customer referral", "referral by agencyzoom") else raw
        return SOURCE_OF_GROUP[g], detail
    if g in SOURCE_OF_GROUP:
        return SOURCE_OF_GROUP[g], None
    return None, None          # unclassified: Unsorted, for Frank to place


_SALES_WF = [
    (re.compile(r"commercial.*(qnc|not quoted)|(qnc|not quoted).*commercial|commercial", re.I), 5),
    (re.compile(r"life", re.I), 4),
    (re.compile(r"qnc|quotes? not closed", re.I), 2),
    (re.compile(r"not quoted", re.I), 3),
    (re.compile(r"^(1 )?pipeline$|pipeline refreshed|tello|test|az sun|personal lines marketing|mortgage lenders", re.I), 1),
]
_SERVICE_WF = [
    (re.compile(r"commercial", re.I), 5, None),
    (re.compile(r"claim", re.I), 7, None),
    (re.compile(r"late payment|reinstate", re.I), 1, None),
    (re.compile(r"contingenc|missing doc", re.I), 2, None),
    (re.compile(r"other 30 day|bristol", re.I), 3, "Bristol West"),
    (re.compile(r"renewal", re.I), 3, None),
    (re.compile(r"^service( pipeline)?$|service", re.I), 4, None),
]


def place_workflow(name, kind):
    """A sales workflow -> (pipeline id, None); a service workflow -> (service id, detail)."""
    n = _norm(name)
    rules = _SALES_WF if kind == "sales" else _SERVICE_WF
    for rule in rules:
        if rule[0].search(n):
            return rule[1], (rule[2] if len(rule) > 2 else None)
    return None, None


def place_stage(pipeline_id, stage_name):
    """An AgencyZoom stage of a workflow placed under `pipeline_id` -> the stage's list id."""
    n = _norm(stage_name)
    for k, (sname, _, aliases) in enumerate(STAGES.get(pipeline_id, []), 1):
        if n == _norm(sname) or any(n == _norm(a) for a in aliases):
            return stage_id(pipeline_id, k)
    return None


_CATEGORY = [
    # a claim first: "Claim: Commercial" and "Claim: Work Comp" are claims (Cerberus's
    # by claims.COMMERCIAL_CATEGORIES, a rule in code, not a different pipeline)
    (re.compile(r"^claim:?\s*(.+)$", re.I), 7, True),
    (re.compile(r"renewals?:? ?commercial|commercial renewal|surplus", re.I), 5, False),
    (re.compile(r"commercial endorsement|commercial", re.I), 6, False),
    (re.compile(r"monthly|noc|mortgagee|payment|bill", re.I), 1, True),
    (re.compile(r"missing|verification|uw request|driver license|contingenc", re.I), 2, False),
    (re.compile(r"renewal", re.I), 3, False),
    (re.compile(r"^general$|unassigned|^category \d+$", re.I), None, False),
]


def place_category(name):
    """-> (service id or None, detail, known): None with known=True follows the workflow."""
    raw = re.sub(r"\s+", " ", str(name or "")).strip()
    n = _norm(raw)
    if not n:
        return None, None, False
    for rx, sid, keep in _CATEGORY:
        m = rx.search(n)
        if m:
            if sid == 7:
                return 7, (m.group(1).strip().title() if m.groups() and m.group(1) else raw), True
            return sid, (raw if keep else None), True
    return 4, raw, True        # a change, a question, a COI, a cancellation: Personal Endorsements


# ---- the rows -------------------------------------------------------------------
def list_rows():
    out = []
    for k, (i, name, label, meaning) in enumerate(SOURCES, 1):
        out.append({"kind": "source", "id": i, "name": name, "parent_id": None, "detail_label": label, "meaning": meaning, "ord": k})
    for k, (i, name, meaning) in enumerate(PIPELINES, 1):
        out.append({"kind": "pipeline", "id": i, "name": name, "parent_id": None, "detail_label": None, "meaning": meaning, "ord": k})
        for j, (sname, smeaning, _) in enumerate(STAGES[i], 1):
            out.append({"kind": "stage", "id": stage_id(i, j), "name": sname, "parent_id": i, "detail_label": None, "meaning": smeaning, "ord": j})
    for k, (i, name, label, meaning) in enumerate(SERVICE, 1):
        out.append({"kind": "service", "id": i, "name": name, "parent_id": None, "detail_label": label, "meaning": meaning, "ord": k})
    return out


def add_rows(rows, sources, workflows, stages, categories):
    """Add the lists and every placement the rules give to a crm_import.Rows.
    sources {az id: name}; workflows {az id: (name, kind)}; stages {az id:
    (az workflow id, name)}; categories {az id: name}. Returns the unsorted:
    [(kind, az id, name)]."""
    for r in list_rows():
        rows.insert("lists", r)
    unsorted = []
    for sid, name in sorted(sources.items()):
        lid, detail = place_source(name)
        if lid:
            rows.insert("list_map", {"kind": "source", "az_id": sid, "list_id": lid, "detail": detail, "placed_by": "rule"})
        else:
            unsorted.append(("source", sid, name))
    wf_place = {}
    for wid, (name, kind) in sorted(workflows.items()):
        lid, detail = place_workflow(name, kind)
        if lid:
            wf_place[wid] = (kind, lid)
            rows.insert("list_map", {"kind": "workflow", "az_id": wid, "list_id": lid, "detail": detail, "placed_by": "rule"})
        else:
            unsorted.append(("workflow", wid, name))
    for sid, (wid, name) in sorted(stages.items()):
        kind, lid = wf_place.get(wid, (None, None))
        if kind != "sales":            # service stages are read as AgencyZoom names them (only Late Payments is worked by stage)
            continue
        st = place_stage(lid, name)
        if st:
            rows.insert("list_map", {"kind": "stage", "az_id": sid, "list_id": st, "detail": None, "placed_by": "rule"})
        else:
            unsorted.append(("stage", sid, f"{workflows[wid][0]} | {name}"))
    for cid, name in sorted(categories.items()):
        lid, detail, known = place_category(name)
        if known:
            rows.insert("list_map", {"kind": "category", "az_id": cid, "list_id": lid, "detail": detail, "placed_by": "rule"})
        else:
            unsorted.append(("category", cid, name))
    return unsorted


def check():
    problems = []
    for kind, items in (("source", SOURCES), ("pipeline", PIPELINES), ("service", SERVICE)):
        names = [x[1] for x in items]
        if len(set(n.lower() for n in names)) != len(names):
            problems.append(f"{kind}: a name repeats")
        ids = [x[0] for x in items]
        if len(set(ids)) != len(ids):
            problems.append(f"{kind}: an id repeats")
    for pid, sts in STAGES.items():
        if pid not in {p[0] for p in PIPELINES}:
            problems.append(f"stages for pipeline {pid}, which does not exist")
        names = [_norm(s[0]) for s in sts]
        if len(set(names)) != len(names):
            problems.append(f"pipeline {pid}: a stage name repeats")
    for v in SOURCE_OF_GROUP.values():
        if v not in {s[0] for s in SOURCES}:
            problems.append(f"SOURCE_OF_GROUP points at source {v}, which does not exist")
    for g in lead_sources.GROUPS:
        if g not in SOURCE_OF_GROUP and g not in ("cross_sell", "not_a_sale", "unclassified"):
            problems.append(f"lead_sources group {g} has no source")
    return problems


def discover():
    """Every lookup in data/ with its place (needs the saved files)."""
    import crm_import
    rows = crm_import.Rows()
    crm_import.build(rows, days=set())
    lists = {(r["kind"], r["id"]): r["name"] for t, r in rows.rows if t == "lists"}
    placed = {(r["kind"], r["az_id"]): r for t, r in rows.rows if t == "list_map"}
    look = {}
    for t, r in rows.rows:
        if t in ("lead_sources", "workflows", "stages", "service_categories"):
            look.setdefault(t, {})[r["id"]] = r
    kind_of = {"lead_sources": ("source", "source"), "workflows": ("workflow", None), "stages": ("stage", "stage"), "service_categories": ("category", "service")}
    for t, (mk, lk) in kind_of.items():
        print(f"\n{t}:")
        for aid, r in sorted(look.get(t, {}).items(), key=lambda kv: ((mk, kv[0]) in placed, kv[1]["name"])):
            m = placed.get((mk, aid))
            if not m:
                print(f"  UNSORTED  {aid}  {r['name']}")
                continue
            lkind = lk or ("pipeline" if r.get("kind") == "sales" else "service")
            target = lists.get((lkind, m["list_id"]), "follows the workflow" if m["list_id"] is None else f"?{m['list_id']}")
            print(f"  {aid}  {r['name']!r:50} -> {target}" + (f"  [{m['detail']}]" if m.get("detail") else ""))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--check"]:
        p = check()
        print("\n".join(p) if p else "crm_lists: the lists check out")
        sys.exit(1 if p else 0)
    if a[:1] == ["--discover"]:
        discover()
    elif a[:1] == ["place"]:
        for name in a[1:]:
            print(f"{name!r}: source -> {place_source(name)}; sales workflow -> {place_workflow(name, 'sales')}; "
                  f"service workflow -> {place_workflow(name, 'service')}; category -> {place_category(name)}")
    else:
        for i, name, label, _ in SOURCES:
            print(f"source   {i:>3}  {name}" + (f"  ({label})" if label else ""))
        for i, name, _ in PIPELINES:
            print(f"pipeline {i:>3}  {name}: " + ", ".join(s[0] for s in STAGES[i]))
        for i, name, label, _ in SERVICE:
            print(f"service  {i:>3}  {name}" + (f"  ({label})" if label else ""))
