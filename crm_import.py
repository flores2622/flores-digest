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
    data/az_stages.json               workflowStageId -> "Pipeline | Stage"
    data/az_lead_sources.json         [{id, name}] if saved; else the names
                                      the leads and policies carry
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
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agencyzoom   # noqa: E402
import staff        # noqa: E402

DATA = ROOT / "data"
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
class Rows:
    def __init__(self):
        self.stmts = []
        self.counts = {}

    def insert(self, table, row):
        keys = list(row)
        self.stmts.append(f"INSERT OR IGNORE INTO {table} ({', '.join(keys)}) VALUES ({', '.join(q(row[k]) for k in keys)});")
        self.counts[table] = self.counts.get(table, 0) + 1


def build(rows):
    stages_file = load("az_stages.json", {}) or {}
    leads = load("az_leads_all.json", []) or []
    customers = load("az_customers_all.json", []) or []
    policies = load("az_policies_all.json", []) or []
    hh_map = load("az_household_policies.json", {}) or {}
    sources_file = load("az_lead_sources.json", None)

    # lookups: lead sources
    sources = {}
    for s in sources_file or []:
        if intval(s.get("id")):
            sources[int(s["id"])] = s.get("name") or f"Source {s['id']}"
    for r in leads + policies:
        sid = intval(r.get("leadSourceId"))
        if sid and sid not in sources and r.get("leadSourceName"):
            sources[sid] = r["leadSourceName"]
    for sid, name in sorted(sources.items()):
        rows.insert("lead_sources", {"id": sid, "name": name})

    # lookups: workflows and stages. Sales pipelines from the stage map
    # ("Pipeline | Stage" per stage id); service workflows from
    # agencyzoom.json's names (ids where it knows them).
    wf_ids = {agencyzoom.JUNK_WORKFLOW_NAME: agencyzoom.JUNK_WORKFLOW_ID}
    claim = agencyzoom.WORKFLOWS.get("claim") or {}
    for n in claim.get("names", []):
        if claim.get("id"):
            wf_ids[n] = int(claim["id"])
    next_wf = SYNTHETIC_WORKFLOW_FROM
    kinds = {}
    for sid, where in stages_file.items():
        pipe = str(where).split(" | ")[0]
        kinds.setdefault(pipe, "sales")
    for names in agencyzoom.WORKFLOWS.get("service", {}).values():
        for n in names:
            kinds[n] = "service"
    for n in (agencyzoom.WORKFLOWS.get("commercial_renewals") or {}).get("names", []):
        kinds[n] = "service"
    for n in claim.get("names", []):
        kinds[n] = "service"
    for name in sorted(kinds):
        if name not in wf_ids:
            wf_ids[name] = next_wf
            next_wf += 1
        rows.insert("workflows", {"id": wf_ids[name], "name": name, "kind": kinds[name]})
    ords = {}
    for sid, where in stages_file.items():
        pipe, _, stage = str(where).partition(" | ")
        ords[pipe] = ords.get(pipe, 0) + 1
        rows.insert("stages", {"id": int(sid), "workflow_id": wf_ids[pipe], "name": stage or where, "ord": ords[pipe]})
    stage_by_name = {}          # (workflow name, stage name) -> id, for SRs
    next_stage = [SYNTHETIC_STAGE_FROM]

    def service_stage(wf_name, stage_name):
        if not wf_name or not stage_name or wf_name not in wf_ids:
            return None
        k = (wf_name, stage_name)
        if k not in stage_by_name:
            stage_by_name[k] = next_stage[0]
            next_stage[0] += 1
            rows.insert("stages", {"id": stage_by_name[k], "workflow_id": wf_ids[wf_name], "name": stage_name, "ord": len([x for x in stage_by_name if x[0] == wf_name])})
        return stage_by_name[k]

    for cid, name in sorted(agencyzoom.DATA.get("claim_categories", {}).items()):
        rows.insert("service_categories", {"id": int(cid), "name": f"Claim: {name}"})
    for rid, name in sorted(agencyzoom.DATA["resolutions"]["labels"].items(), key=lambda kv: int(kv[0])):
        rows.insert("resolutions", {"id": int(rid), "name": name})
    for cid, short in sorted(agencyzoom.DATA.get("carriers", {}).items(), key=lambda kv: int(kv[0])):
        rows.insert("carriers", {"id": int(cid), "name": short, "short": short})
    seen_carriers = {int(c) for c in agencyzoom.DATA.get("carriers", {})}
    for p in policies:
        cid = intval(p.get("carrierId"))
        if cid and cid not in seen_carriers:
            seen_carriers.add(cid)
            rows.insert("carriers", {"id": cid, "name": p.get("carrierName") or f"Carrier {cid}", "short": None})

    # households (customers)
    for c in as_list(customers):
        cid = intval(c.get("id"))
        if not cid:
            continue
        rows.insert("households", {
            "id": cid, "az_id": cid,
            "firstname": c.get("firstname") or "", "lastname": c.get("lastname") or "",
            "business_name": c.get("businessName") or None,
            "phone": c.get("phone") or None, "phone_key": e164(c.get("phone")),
            "secondary_phone": c.get("secondaryPhone") or None, "secondary_phone_key": e164(c.get("secondaryPhone")),
            "email": c.get("email") or None, "address": c.get("address") or None, "city": c.get("city") or None,
            "state": c.get("state") or None, "zip": c.get("zip") or c.get("zipCode") or None,
            "assigned_to": intval(c.get("assignedTo") or c.get("agentId")),
            "customer_type": c.get("customerType") or "customer",
            "as_customer_date": local_dt(c.get("asCustomerDate")),
            "create_date": local_dt(c.get("createDate")) or local_dt(c.get("asCustomerDate")) or "1970-01-01 00:00:00",
            "modify_date": local_dt(c.get("modifyDate")), "status": 0 if c.get("status") == 0 else 1,
        })

    # leads
    for l in leads:
        lid = intval(l.get("id"))
        if not lid:
            continue
        sid = intval(l.get("workflowStageId"))
        where = stages_file.get(str(sid)) if sid else None
        pipe = where.split(" | ")[0] if where else None
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
            "assigned_to": intval(l.get("assignedTo")), "lead_source_id": intval(l.get("leadSourceId")),
            "workflow_id": wf_ids.get(pipe) if pipe else None, "workflow_stage_id": sid if where else None,
            "enter_stage_date": local_dt(l.get("enterStageDate")),
            "status": status, "exit": "Sold" if status == 2 else None,
            "create_date": local_dt(l.get("createDate")) or "1970-01-01 00:00:00",
            "last_activity_date": local_dt(l.get("lastActivityDate")),
            "quote_date": local_dt(l.get("quoteDate")), "sold_date": local_dt(l.get("soldDate")),
            "converted_household_id": intval(l.get("convertedHouseholdId")),
            "created_by": intval(l.get("createdBy")),
        })

    # policies, with the household the map ties them to
    pol_household = {}
    for hid, plist in (hh_map or {}).items():
        for p in as_list(plist) if not isinstance(plist, list) else plist:
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
            "lead_id": intval(p.get("leadId")),
            "agent_id": intval(p.get("agentId")), "lead_source_id": intval(p.get("leadSourceId")),
            "carrier_id": intval(p.get("carrierId")), "carrier_name": p.get("carrierName") or None,
            "policy_type_name": p.get("policyTypeName") or None, "policy_number": p.get("policyNumber") or None,
            "premium": num(p.get("premium")), "term_months": intval(p.get("term") or p.get("termMonths")),
            "effective_date": local_day(p.get("effectiveDate")), "expiry_date": local_day(p.get("expiryDate")),
            "sold_date": local_day(p.get("soldDate")),
            "status": _policy_status(p), "cancel_date": local_day(p.get("cancelDate") or p.get("cancellationDate")),
            "create_date": local_dt(p.get("createDate")) or local_dt(p.get("soldDate")) or "1970-01-01 00:00:00",
            "modify_date": local_dt(p.get("modifyDate")), "created_by": intval(p.get("createdBy")),
        })

    # tasks: every saved day, merged by id (the newest file wins)
    tasks = {}
    for f in sorted(glob.glob(str(DATA / "az_tasks_*.json"))):
        for t in as_list(json.loads(pathlib.Path(f).read_text())):
            if intval(t.get("id")):
                tasks[int(t["id"])] = t
    for tid, t in sorted(tasks.items()):
        ctype = t.get("customerType") or None
        cid = intval(t.get("customerId"))
        assignee = intval(t.get("assigneeId")) or intval(((t.get("assignees") or [{}])[0] or {}).get("id"))
        rows.insert("tasks", {
            "id": tid, "az_id": tid, "title": t.get("title") or "", "comments": t.get("comments") or None,
            "type": (t.get("type") or "call").lower() if (t.get("type") or "call").lower() in ("call", "email", "text", "todo") else "todo",
            "assignee_id": assignee,
            "lead_id": cid if ctype == "lead" else intval(t.get("leadId")),
            "household_id": cid if ctype == "customer" else None,
            "sr_id": cid if ctype == "serviceTicket" else None,
            "customer_type": ctype, "due_date": local_dt(t.get("dueDate")),
            "status": 1 if intval(t.get("status")) else 0, "complete_date": local_dt(t.get("completeDate")),
            "completed_by": intval(t.get("completedBy")), "agency_todo": 1 if t.get("agencyTodo") else 0,
            "created_by": intval(t.get("createdBy")),
            "create_date": local_dt(t.get("createDate")) or local_dt(t.get("dueDate")) or "1970-01-01 00:00:00",
        })

    # SRs: live and completed files of every day, merged by id
    srs = {}
    for f in sorted(glob.glob(str(DATA / "az_service_tickets_*.json"))):
        for t in as_list(json.loads(pathlib.Path(f).read_text())):
            if intval(t.get("id")):
                srs[int(t["id"])] = t
    for sid, t in sorted(srs.items()):
        wf_name = t.get("workflowName")
        wf_id = intval(t.get("workflowId")) or wf_ids.get(wf_name)
        if wf_name and wf_name not in wf_ids and wf_id:
            wf_ids[wf_name] = wf_id
            rows.insert("workflows", {"id": wf_id, "name": wf_name, "kind": "service"})
        if wf_name and wf_name not in wf_ids:
            wf_ids[wf_name] = next_wf
            wf_id = next_wf
            next_wf += 1
            rows.insert("workflows", {"id": wf_id, "name": wf_name, "kind": "service"})
        ctype = t.get("customerType") or None
        cid = intval(t.get("householdId") or t.get("customerId"))
        rows.insert("service_requests", {
            "id": sid, "az_id": sid,
            "household_id": cid if ctype != "lead" else None, "lead_id": cid if ctype == "lead" else None,
            "customer_type": ctype, "workflow_id": wf_id,
            "workflow_stage_id": service_stage(wf_name, t.get("workflowStageName")),
            "enter_stage_date": local_dt(t.get("enterStageTS") or t.get("enterStageDate")),
            "category_id": intval(t.get("categoryId")),
            "subject": t.get("subject") or t.get("title") or "", "description": t.get("serviceDesc") or t.get("description") or None,
            "csr": intval(t.get("csr")), "created_by": intval(t.get("createdBy")),
            "create_date": local_dt(t.get("createDate")) or "1970-01-01 00:00:00",
            "due_date": local_dt(t.get("dueDate")), "expiry_date": local_day(t.get("expiryDate")),
            "effective_date": local_day(t.get("effectiveDate")), "policy_id": intval(t.get("policyId")),
            "status": intval(t.get("status")) if intval(t.get("status")) is not None else 1,
            "complete_date": local_dt(t.get("completeDate")), "completed_by": intval(t.get("completedBy")),
            "resolution_id": intval(t.get("resolutionId")), "resolution_desc": t.get("resolutionDesc") or None,
            "modify_date": local_dt(t.get("modifyDate")), "modified_by": intval(t.get("modifiedBy")),
        })

    # notes and stage moves (notes are on the agency's clock already)
    try:
        import pipelines
        import live_contact
    except Exception:
        pipelines = live_contact = None
    lead_ids = {intval(l.get("id")) for l in leads}
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
            created_by = intval(n.get("createdBy"))
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
    s = str(p.get("status") or p.get("policyStatus") or "").lower()
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
    files = []
    for i in range(0, len(rows.stmts), STATEMENTS_PER_FILE):
        p = out.parent / f"{out.name}_{i // STATEMENTS_PER_FILE:03d}.sql"
        p.write_text("\n".join(rows.stmts[i:i + STATEMENTS_PER_FILE]) + "\n")
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
        print(f"{len(rows.stmts):,} statements in {len(files)} file(s): {files[0]} .. {files[-1] if files else ''}")
        print("apply in order:  for f in <files>; do wrangler d1 execute pantheon-crm --remote --file=$f; done")
    else:
        counts = write_sqlite(rows, args[1])
        print(f"{args[1]}: " + ", ".join(f"{t} {n:,}" for t, n in counts.items()))
