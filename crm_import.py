"""First load of Pantheon's own CRM from the nightly's saved AgencyZoom files.

    python3 crm_import.py --sql out/crm_import          write out/crm_import_NNN.sql
                                                        (then: wrangler d1 execute
                                                        pantheon-crm --remote --file=...)
    python3 crm_import.py --sqlite out/crm_import.db    build a local SQLite copy
                                                        (the same rows) and print counts

Reads only what the pipeline already keeps under data/ (nothing is fetched):
    data/az_leads_all.json            every lead (az_corpus.fetch)
    data/az_customers_all.json        every customer record
    data/az_policies_all.json         every policy
    data/az_household_policies.json   household id -> its policies (which
                                      policy belongs to which household;
                                      policy records carry no customer)
    data/az_pipelines.json            /v1/api/pipelines-and-stages as it came
                                      (daily.py saves it beside az_stages.json):
                                      the real workflow and stage ids
    data/az_stages.json               workflowStageId -> "Pipeline | Stage"
                                      (the fallback when the above is missing)
    data/az_service_categories.json   /v1/api/service-categories (daily.py
                                      saves it): the SR categories' names
    data/az_lead_sources.json         {names: {id: name}} or [{id, name}] if
                                      saved; else the names the leads and
                                      policies carry
    data/az_tasks_<day>.json          every day's tasks, merged by id
    data/az_service_tickets_<day>.json, _done_<day>.json   SRs, merged by id
                                      (the newest day's copy of an SR wins)
    data/notes/<lead>.json            every lead's notes; MOVE_STAGE notes
                                      also become stage_moves rows
    agencyzoom.json                   resolutions, claim categories, carriers

Every row keeps AgencyZoom's own id (`id` AND `az_id`), so the published day
documents' lead_ids, the Sales sheet's policy ids and the Service Center's
SR ids all still point at the right record. People stay staff.json's az_id.
AgencyZoom's lead / customer / policy / task / SR dates are UTC and its notes
are on the agency's clock (CLAUDE.md); everything is written on the
agency's clock (staff.TZ). A file that is missing is skipped with a line
saying so -- run it again once the nightly has saved it. INSERT OR IGNORE
throughout: a second run adds what is new and changes nothing already there.
"""
import datetime as dt
import glob
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agencyzoom   # noqa: E402
import staff        # noqa: E402

# A name AgencyZoom hands back instead of an id (an SR's createdBy / modifiedBy,
# a task's completedBy) -> the person's staff.json az_id.
NAME_TO_ID = {p["name"].strip().lower(): p.get("az_id") for p in staff.PEOPLE if p.get("az_id")}

DATA = pathlib.Path(os.environ.get("CRM_DATA") or ROOT / "data")
SCHEMA = ROOT / "site" / "crm" / "migrations" / "0001_init.sql"
SYNTHETIC_WORKFLOW_FROM = 900001   # a sales pipeline AgencyZoom never gave us an id for
SYNTHETIC_STAGE_FROM = 800001      # a service stage known only by name
STATEMENTS_PER_FILE = 4000


def log(*a):
    print(*a, file=sys.stderr)


# ---- values ------------------------------------------------------------------
def q(v):
    """One SQL literal."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def e164(raw):
    d = re.sub(r"\D", "", str(raw or ""))
    return f"+1{d[-10:]}" if 10 <= len(d) <= 15 else None


_ISO = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2}))?(?:\.\d+)?(Z|[+-]\d{2}:?\d{2})?)?")


def local_dt(text, utc=True):
    """An AgencyZoom stamp -> 'YYYY-MM-DD HH:MM:SS' on the agency's clock.
    A naive stamp is UTC when `utc` (records), local when not (notes)."""
    if not text:
        return None
    m = _ISO.match(str(text).strip())
    if not m:
        return None
    day, hh, mm, ss, zone = m.groups()
    if hh is None:
        return f"{day} 00:00:00"
    t = dt.datetime.fromisoformat(f"{day}T{hh}:{mm}:{ss or '00'}")
    if zone and zone != "Z":
        sign = 1 if zone[0] == "+" else -1
        z = zone[1:].replace(":", "")
        t = t - sign * dt.timedelta(hours=int(z[:2]), minutes=int(z[2:]))
        zone = "Z"
    if zone == "Z" or utc:
        t = t.replace(tzinfo=dt.timezone.utc).astimezone(staff.TZ).replace(tzinfo=None)
    return t.strftime("%Y-%m-%d %H:%M:%S")


def local_day(text):
    v = local_dt(text)
    return v[:10] if v else None


def num(v):
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def intval(v):
    try:
        return int(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def person(v):
    """A staff id from an AgencyZoom id or a name ("Debbie Aguilera")."""
    if isinstance(v, dict):
        v = v.get("id") or f"{v.get('firstname', '')} {v.get('lastname', '')}"
    i = intval(v)
    if i is not None:
        return i
    return NAME_TO_ID.get(str(v or "").strip().lower())


# AgencyZoom's policy status codes, as renewal_report reads them: 1 the current
# term, 3 the next term already issued, 4 a past term, 0 cancelled.
POLICY_STATUS = {0: "cancelled", 1: "active", 3: "pending", 4: "expired"}


def load(name, default=None):
    p = DATA / name
    if not p.exists():
        log(f"  {name}: not saved yet -- skipped")
        return default
    return json.loads(p.read_text())


def as_list(x):
    if isinstance(x, dict):
        return list(x.values())
    return x or []


# ---- the rows -----------------------------------------------------------------
# Tables AgencyZoom owns while it is still the record: a sync UPDATES an
# imported row (az_id set) when AgencyZoom's copy changed, and never touches a
# row Pantheon made itself (az_id NULL). Lookups are added once and never
# rewritten (Frank consolidates and renames them in Pantheon); notes and stage
# moves never change once written.
AZ_OWNED = {"leads", "households", "policies", "tasks", "service_requests"}
LOOKUPS = {"lead_sources", "workflows", "stages", "service_categories", "resolutions", "carriers"}


def statement(table, row, mode="ignore"):
    """One INSERT for `row`. mode "ignore": INSERT OR IGNORE (the first load);
    "upsert": AgencyZoom's version replaces an imported row's fields."""
    keys = list(row)
    head = f"INSERT INTO {table} ({', '.join(keys)}) VALUES ({', '.join(q(row[k]) for k in keys)})"
    if mode == "upsert" and table in AZ_OWNED:
        sets = ", ".join(f"{k} = excluded.{k}" for k in keys if k not in ("id", "az_id"))
        return f"{head} ON CONFLICT(id) DO UPDATE SET {sets} WHERE {table}.az_id IS NOT NULL;"
    # A lookup (lead source, pipeline, stage, category, resolution, carrier) is
    # added when AgencyZoom first shows it and never rewritten: Frank is
    # consolidating and renaming these in Pantheon (2026-10-06), so his names
    # win over AgencyZoom's from the moment he sets them.
    return f"INSERT OR IGNORE{head[6:]};"


class Rows:
    def __init__(self):
        self.rows = []          # (table, row)
        self.counts = {}

    def insert(self, table, row):
        self.rows.append((table, row))
        self.counts[table] = self.counts.get(table, 0) + 1

    def statements(self, mode="ignore"):
        return [statement(t, r, mode) for t, r in self.rows]

    @property
    def stmts(self):
        return self.statements("ignore")


def build(rows, days=None):
    """Every row the saved files give. `days` (a set of YYYY-MM-DD) limits the
    per-day task and SR files read -- the nightly sync passes the days it is
    responsible for; the first load reads them all."""
    stages_file = load("az_stages.json", {}) or {}
    leads = load("az_leads_all.json", []) or []
    customers = load("az_customers_all.json", []) or []
    policies = load("az_policies_all.json", []) or []
    hh_map = load("az_household_policies.json", {}) or {}
    sources_file = load("az_lead_sources.json", None)

    # lookups: lead sources
    sources = {}
    if isinstance(sources_file, dict) and isinstance(sources_file.get("names"), dict):
        sources.update({int(k): v for k, v in sources_file["names"].items() if intval(k)})
    else:
        for src in sources_file or []:
            if intval(src.get("id")):
                sources[int(src["id"])] = src.get("name") or f"Source {src['id']}"
    for r in leads + policies:
        sid = intval(r.get("leadSourceId"))
        if sid and sid not in sources and r.get("leadSourceName"):
            sources[sid] = r["leadSourceName"]
    for r in leads + policies:          # an id with no name anywhere still needs its row (foreign keys)
        sid = intval(r.get("leadSourceId"))
        if sid and sid not in sources:
            sources[sid] = f"Source {sid}"
    for sid, name in sorted(sources.items()):
        rows.insert("lead_sources", {"id": sid, "name": name})

    # tasks: every saved day's file, merged by id (the newest file wins); read
    # early so the household stubs below know what they point at
    tasks_seen_by_id = {}
    for f in sorted(glob.glob(str(DATA / "az_tasks_*.json"))):
        if days is not None and not any(d in f for d in days):
            continue
        for t in as_list(json.loads(pathlib.Path(f).read_text())):
            if intval(t.get("id")):
                tasks_seen_by_id[int(t["id"])] = t
    tasks_seen = list(tasks_seen_by_id.values())

    # lookups: workflows and stages, with AgencyZoom's own ids wherever a file
    # carries them -- the pipelines response (sales) and the SRs (service) --
    # and a synthetic id only for a workflow known by name alone.
    pipelines_raw = load("az_pipelines.json", None)
    wf_ids, wf_kind, stage_rows = {}, {}, {}      # name -> id; name -> kind; stage id -> (wf id, name, ord)
    stage_wf = {}                                  # stage id -> workflow id
    if pipelines_raw:
        for w in as_list(pipelines_raw):
            wid, wname = intval(w.get("id")), w.get("name")
            if not wid or not wname:
                continue
            wf_ids[wname] = wid
            wf_kind[wname] = "sales"
            for k, st in enumerate(w.get("stages") or []):
                sid = intval(st.get("id"))
                if sid:
                    stage_rows[sid] = (wid, st.get("name") or "", intval(st.get("seq")) or k + 1)
                    stage_wf[sid] = wid
    for sid, where in stages_file.items():       # the fallback map: names only
        pipe, _, stage = str(where).partition(" | ")
        wf_kind.setdefault(pipe, "sales")
        if intval(sid) and intval(sid) not in stage_rows:
            stage_rows[int(sid)] = (None, stage or where, 0)   # workflow id filled in below
            stage_wf[int(sid)] = pipe
    service_names = set()
    for names in agencyzoom.WORKFLOWS.get("service", {}).values():
        service_names.update(names)
    service_names.update((agencyzoom.WORKFLOWS.get("commercial_renewals") or {}).get("names", []))
    claim = agencyzoom.WORKFLOWS.get("claim") or {}
    service_names.update(claim.get("names", []))
    for n in service_names:
        wf_kind[n] = "service"
    wf_ids.setdefault(agencyzoom.JUNK_WORKFLOW_NAME, agencyzoom.JUNK_WORKFLOW_ID)
    for n in claim.get("names", []):
        if claim.get("id"):
            wf_ids.setdefault(n, int(claim["id"]))

    # SRs: every saved day's live and completed files, merged by id (newest file wins)
    srs = {}
    for f in sorted(glob.glob(str(DATA / "az_service_tickets_*.json"))):
        if days is not None and not any(d in f for d in days):
            continue
        for t in as_list(json.loads(pathlib.Path(f).read_text())):
            if intval(t.get("id")):
                srs[int(t["id"])] = t
    for t in srs.values():
        wname, wid = t.get("workflowName"), intval(t.get("workflowId"))
        if wname and wid:
            wf_ids.setdefault(wname, wid)
            wf_kind.setdefault(wname, "service")
        sid, sname = intval(t.get("workflowStageId")), t.get("workflowStageName")
        if sid and wid and sid not in stage_rows:
            stage_rows[sid] = (wid, sname or "", 0)
            stage_wf[sid] = wid
    next_wf = SYNTHETIC_WORKFLOW_FROM
    sr_names = {intval(t.get("workflowId")): t.get("workflowName") for t in srs.values() if intval(t.get("workflowId")) and t.get("workflowName")}
    wf_done = set()
    for name in sorted(wf_kind):
        if name not in wf_ids:
            wf_ids[name] = next_wf
            next_wf += 1
        wid = wf_ids[name]
        if wid in wf_done:        # one row per id: a renamed workflow (Missing Documents ->
            continue              # Contingencies, 61459) is known by both names
        wf_done.add(wid)
        rows.insert("workflows", {"id": wid, "name": sr_names.get(wid, name), "kind": wf_kind[name]})
    ords = {}
    for sid, (wid, sname, ord_) in sorted(stage_rows.items(), key=lambda kv: (str(kv[1][0]), kv[1][2], kv[0])):
        if wid is None:                           # from the fallback map: its pipeline's name
            wid = wf_ids.get(stage_wf.get(sid))
            stage_wf[sid] = wid
        if not wid:
            continue
        ords[wid] = ords.get(wid, 0) + 1
        rows.insert("stages", {"id": sid, "workflow_id": wid, "name": sname, "ord": ord_ or ords[wid]})

    def service_stage(wf_name, stage_name):
        """A service SR's stage id when its file carried none: by workflow and name."""
        wid = wf_ids.get(wf_name)
        for sid, (w, n, _) in stage_rows.items():
            if w == wid and n == stage_name:
                return sid
        return None

    cat_names = {int(k): f"Claim: {v}" for k, v in agencyzoom.DATA.get("claim_categories", {}).items()}
    for cat in as_list(load("az_service_categories.json", []) or []):   # the account's own names
        if isinstance(cat, dict) and intval(cat.get("id")) and intval(cat.get("id")) not in cat_names:
            cat_names[int(cat["id"])] = cat.get("name") or cat.get("categoryName") or f"Category {cat['id']}"
    for t in srs.values():
        cid = intval(t.get("categoryId"))
        if cid and cid not in cat_names:
            cat_names[cid] = t.get("categoryName") or f"Category {cid}"
    for cid, name in sorted(cat_names.items()):
        rows.insert("service_categories", {"id": cid, "name": name})
    res_names = {int(k): v for k, v in agencyzoom.DATA["resolutions"]["labels"].items()}
    for t in srs.values():               # a resolution id the SRs carry that the file does not name
        rid = intval(t.get("resolutionId"))
        if rid and rid not in res_names:
            res_names[rid] = f"Resolution {rid}"
    for rid, name in sorted(res_names.items()):
        rows.insert("resolutions", {"id": rid, "name": name})
    for cid, short in sorted(agencyzoom.DATA.get("carriers", {}).items(), key=lambda kv: int(kv[0])):
        rows.insert("carriers", {"id": int(cid), "name": short, "short": short})
    seen_carriers = {int(c) for c in agencyzoom.DATA.get("carriers", {})}
    for p in policies:
        cid = intval(p.get("carrierId"))
        if cid and cid not in seen_carriers:
            seen_carriers.add(cid)
            rows.insert("carriers", {"id": cid, "name": p.get("carrierName") or f"Carrier {cid}", "short": None})

    # households (customers), then a stub for every household id a lead, policy,
    # task or SR points at that the customer corpus does not carry -- the
    # database's foreign keys need the row, and a later sync fills it in when
    # the customer record appears (an az_id row follows AgencyZoom).
    known_hh = set()
    for c in as_list(customers):
        cid = intval(c.get("id"))
        if not cid:
            continue
        known_hh.add(cid)
        rows.insert("households", {
            "id": cid, "az_id": cid,
            "firstname": c.get("firstname") or "", "lastname": c.get("lastname") or "",
            "business_name": c.get("businessName") or None,
            "phone": c.get("phone") or None, "phone_key": e164(c.get("phone")),
            "secondary_phone": c.get("secondaryPhone") or None, "secondary_phone_key": e164(c.get("secondaryPhone")),
            "email": c.get("email") or None, "address": c.get("streetAddress") or c.get("address") or None, "city": c.get("city") or None,
            "state": c.get("state") or None, "zip": c.get("zip") or c.get("zipCode") or None,
            "assigned_to": person(c.get("agentId") or c.get("assignedTo")),
            "customer_type": (c.get("customerType") or "Personal").lower(),
            "as_customer_date": local_dt(c.get("asCustomerDate")),
            "create_date": local_dt(c.get("createDate")) or local_dt(c.get("asCustomerDate")) or "1970-01-01 00:00:00",
            "modify_date": local_dt(c.get("modifyDate")), "status": 0 if c.get("status") == 0 else 1,
        })

    referenced = set()
    for l in leads:
        referenced.add(intval(l.get("convertedHouseholdId")))
    for hid, entry in (hh_map or {}).items():
        plist = entry.get("policies") if isinstance(entry, dict) and "policies" in entry else entry
        if plist:
            referenced.add(intval(hid))
    for t in srs.values():
        if (t.get("customerType") or "customer").lower() != "lead":
            referenced.add(intval(t.get("householdId") or t.get("customerId")))
    for t in tasks_seen:
        if t.get("customerType") == "customer":
            referenced.add(intval(t.get("customerId")))
    for hid in sorted(h for h in referenced if h and h not in known_hh):
        rows.insert("households", {"id": hid, "az_id": hid, "firstname": "", "lastname": "", "customer_type": "customer",
                                   "create_date": "1970-01-01 00:00:00", "status": 1})
        known_hh.add(hid)

    lead_ids = {intval(l.get("id")) for l in leads}
    # leads
    for l in leads:
        lid = intval(l.get("id"))
        if not lid:
            continue
        sid = intval(l.get("workflowStageId"))
        wid = stage_wf.get(sid) if sid else None
        if isinstance(wid, str):
            wid = wf_ids.get(wid)
        status = intval(l.get("status")) or 0
        rows.insert("leads", {
            "id": lid, "az_id": lid,
            "firstname": l.get("firstname") or "", "lastname": l.get("lastname") or "",
            "business_name": l.get("businessName") or None,
            "phone": l.get("phone") or None, "phone_key": e164(l.get("phone")),
            "secondary_phone": l.get("secondaryPhone") or None, "secondary_phone_key": e164(l.get("secondaryPhone")),
            "email": l.get("email") or None, "address": l.get("address") or None, "city": l.get("city") or None,
            "state": l.get("state") or None, "zip": l.get("zip") or l.get("zipCode") or None,
            "language": l.get("language") or None,
            "assigned_to": person(l.get("assignedTo")), "lead_source_id": intval(l.get("leadSourceId")),
            "workflow_id": wid, "workflow_stage_id": sid if sid in stage_rows else None,
            "enter_stage_date": local_dt(l.get("enterStageDate")),
            "status": status, "exit": "Sold" if status == 2 else None,
            "create_date": local_dt(l.get("createDate")) or "1970-01-01 00:00:00",
            "last_activity_date": local_dt(l.get("lastActivityDate")),
            "quote_date": local_dt(l.get("quoteDate")), "sold_date": local_dt(l.get("soldDate")),
            "converted_household_id": intval(l.get("convertedHouseholdId")),
            "created_by": person(l.get("createdBy")),
        })

    # policies, with the household the map ties them to
    # (data/az_household_policies.json: household id -> {"fetched": t, "policies": [...]})
    pol_household = {}
    for hid, entry in (hh_map or {}).items():
        plist = entry.get("policies") if isinstance(entry, dict) and "policies" in entry else entry
        for p in (plist if isinstance(plist, list) else as_list(plist)):
            pid = intval(p.get("id") if isinstance(p, dict) else p)
            if pid:
                pol_household[pid] = intval(hid)
    for p in as_list(policies):
        pid = intval(p.get("id"))
        if not pid:
            continue
        rows.insert("policies", {
            "id": pid, "az_id": pid,
            "household_id": pol_household.get(pid) or intval(p.get("householdId") or p.get("customerId")),
            "lead_id": intval(p.get("leadId")) if intval(p.get("leadId")) in lead_ids else None,
            "agent_id": person(p.get("agentId")), "lead_source_id": intval(p.get("leadSourceId")),
            "carrier_id": intval(p.get("carrierId")), "carrier_name": p.get("carrierName") or None,
            "policy_type_name": p.get("policyTypeName") or None, "policy_number": p.get("policyNumber") or None,
            "premium": num(p.get("premium")), "term_months": intval(p.get("term") or p.get("termMonths")),
            "effective_date": local_day(p.get("effectiveDate")), "expiry_date": local_day(p.get("expiryDate")),
            "sold_date": local_day(p.get("soldDate")),
            "status": _policy_status(p), "cancel_date": local_day(p.get("cancelDate") or p.get("cancellationDate")),
            "create_date": local_dt(p.get("createDate")) or local_dt(p.get("soldDate")) or "1970-01-01 00:00:00",
            "modify_date": local_dt(p.get("modifyDate")), "created_by": person(p.get("createdBy")),
        })

    # tasks: every saved day, merged by id (the newest file wins)
    tasks = tasks_seen_by_id
    for tid, t in sorted(tasks.items()):
        ctype = t.get("customerType") or None
        cid = intval(t.get("customerId"))
        assignee = person(t.get("assigneeId")) or person((t.get("assignees") or [None])[0])
        due = local_dt(t.get("taskDateTime")) if t.get("timeSpecific") and t.get("taskDateTime") else (
            f"{str(t.get('dueDate'))[:10]} 00:00:00" if t.get("dueDate") else None)
        title = t.get("title") or ""
        kind = (t.get("type") or "").lower()
        if kind not in ("call", "email", "text", "todo"):
            kind = "call" if re.search(r"\bcall|llam", title, re.I) else "email" if re.search(r"\bemail", title, re.I) else "text" if re.search(r"\btext", title, re.I) else "todo"
        rows.insert("tasks", {
            "id": tid, "az_id": tid, "title": title, "comments": t.get("comments") or None,
            "type": kind, "assignee_id": assignee,
            "lead_id": (cid if ctype == "lead" else intval(t.get("leadId"))) if (cid if ctype == "lead" else intval(t.get("leadId"))) in lead_ids else None,
            "household_id": cid if ctype == "customer" else None,
            "sr_id": cid if ctype == "serviceTicket" else None,
            "customer_type": ctype, "due_date": due,
            "status": intval(t.get("status")) or 0, "complete_date": local_dt(t.get("completeDate")),
            "completed_by": person(t.get("completedBy")), "agency_todo": 1 if t.get("agencyTodo") else 0,
            "created_by": person(t.get("createdBy")),
            "create_date": local_dt(t.get("createDate")) or due or "1970-01-01 00:00:00",
        })

    # SRs (merged above): AgencyZoom's own workflow and stage ids; createdBy and
    # modifiedBy come back as names, so they go through person().
    for sid, t in sorted(srs.items()):
        wf_name = t.get("workflowName")
        wf_id = intval(t.get("workflowId")) or wf_ids.get(wf_name)
        ctype = (t.get("customerType") or "customer").lower()
        cid = intval(t.get("householdId") or t.get("customerId"))
        status = intval(t.get("status"))
        modified_by = person(t.get("modifiedBy"))
        rows.insert("service_requests", {
            "id": sid, "az_id": sid,
            "household_id": cid if ctype != "lead" else None, "lead_id": cid if ctype == "lead" and cid in lead_ids else None,
            "customer_type": ctype, "workflow_id": wf_id,
            "workflow_stage_id": intval(t.get("workflowStageId")) or service_stage(wf_name, t.get("workflowStageName")),
            "enter_stage_date": local_dt(t.get("enterStageTS") or t.get("enterStageDate")),
            "category_id": intval(t.get("categoryId")),
            "subject": t.get("subject") or t.get("name") or t.get("title") or "", "description": t.get("serviceDesc") or t.get("description") or None,
            "csr": person(t.get("csr")), "created_by": person(t.get("createdBy")),
            "create_date": local_dt(t.get("createDate")) or "1970-01-01 00:00:00",
            "due_date": local_dt(t.get("dueDate")), "expiry_date": local_day(t.get("expiryDate")),
            "effective_date": local_day(t.get("effectiveDate")), "policy_id": intval(t.get("policyId")),
            "status": status if status is not None else 1,
            "complete_date": local_dt(t.get("completeDate")) if status == 2 else None,
            "completed_by": (person(t.get("completedBy")) or modified_by) if status == 2 else None,
            "resolution_id": intval(t.get("resolutionId")), "resolution_desc": t.get("resolutionDesc") or None,
            "modify_date": local_dt(t.get("modifyDate")), "modified_by": modified_by,
        })

    # notes and stage moves (notes are on the agency's clock already)
    try:
        import pipelines
        import live_contact
    except Exception:
        pipelines = live_contact = None
    n_files = 0
    for f in sorted(glob.glob(str(DATA / "notes" / "*.json"))):
        lid = intval(pathlib.Path(f).stem)
        if not lid or (lead_ids and lid not in lead_ids):
            continue
        n_files += 1
        for n in as_list(json.loads(pathlib.Path(f).read_text())):
            nid = intval(n.get("id"))
            if not nid:
                continue
            attr = n.get("attr") if isinstance(n.get("attr"), dict) else {}
            body = n.get("body") if n.get("body") is not None else (n.get("text") or "")
            ntype = str(n.get("type") or "NOTE").upper()
            created_by = person(n.get("createdBy"))
            if created_by is None and n.get("createdBy"):
                attr = dict(attr, createdByName=str(n["createdBy"]))
            origin = "automation" if attr.get("triggerRuleId") else ("traq" if str(body).lstrip().lower().startswith("traq") else "import")
            when = local_dt(n.get("createDate"), utc=False) or "1970-01-01 00:00:00"
            rows.insert("notes", {
                "id": nid, "az_id": nid, "lead_id": lid, "type": ntype, "body": str(body),
                "attr": json.dumps(attr) if attr else None,
                "attachments": json.dumps(n.get("attachments")) if n.get("attachments") else None,
                "origin": origin, "created_by": created_by, "create_date": when,
            })
            if ntype == "MOVE_STAGE" and pipelines is not None:
                move, comment = live_contact._move_stage_parts(str(body))
                mv = pipelines.parse_move(move)
                if mv:
                    rows.insert("stage_moves", {"lead_id": lid, "from_where": mv["from"], "to_where": mv["to"],
                                                "loss_reason": mv.get("loss_reason") or comment or None, "moved_by": created_by,
                                                "at": when, "note_id": nid})
    log(f"  notes: {n_files} leads' files read")
    return rows


def _policy_status(p):
    v = p.get("status")
    if intval(v) is not None:
        return POLICY_STATUS.get(intval(v), "active")
    s = str(v or p.get("policyStatus") or "").lower()
    if "cancel" in s:
        return "cancelled"
    if "expire" in s or "lapse" in s:
        return "expired"
    if "pend" in s:
        return "pending"
    return "active"


def write_sql(rows, prefix):
    out = pathlib.Path(prefix)
    out.parent.mkdir(parents=True, exist_ok=True)
    files, stmts = [], rows.stmts
    for i in range(0, len(stmts), STATEMENTS_PER_FILE):
        p = out.parent / f"{out.name}_{i // STATEMENTS_PER_FILE:03d}.sql"
        p.write_text("\n".join(stmts[i:i + STATEMENTS_PER_FILE]) + "\n")
        files.append(p)
    return files


def write_sqlite(rows, path):
    import sqlite3
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.unlink()
    c = sqlite3.connect(p)
    c.executescript(SCHEMA.read_text())
    c.executescript("\n".join(rows.stmts))
    c.commit()
    counts = {t: c.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in sorted(rows.counts)}
    c.close()
    return counts


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] not in ("--sql", "--sqlite") or len(args) < 2:
        print(__doc__)
        sys.exit(2)
    rows = build(Rows())
    log("  rows built: " + ", ".join(f"{t} {n:,}" for t, n in sorted(rows.counts.items())))
    if args[0] == "--sql":
        files = write_sql(rows, args[1])
        print(f"{len(rows.rows):,} statements in {len(files)} file(s): {files[0]} .. {files[-1] if files else ''}")
        print("apply in order:  for f in <files>; do wrangler d1 execute pantheon-crm --remote --file=$f; done")
    else:
        counts = write_sqlite(rows, args[1])
        print(f"{args[1]}: " + ", ".join(f"{t} {n:,}" for t, n in counts.items()))
