"""The CRM's tasks, read and written by the pipeline in AgencyZoom's shape.

    TASKS_SOURCE=agencyzoom   (default) Task Completion, the missed-call
                              tasks and the live figure read and write
                              AgencyZoom, as they always have
    TASKS_SOURCE=crm          they read and write Pantheon's own CRM (D1)

CRM.md phase 2: the one thing the pipeline WRITES to AgencyZoom is the
missed-call task, and Task Completion is what it reads back. This module is
the CRM side of both, in the same shape `az_client.tasks` returns -- id,
title, comments, status, customerType / customerId / customerName,
assignees, dueDate, completeDate -- so `az_tasks.audit`, `task_audit` and
`missed_call_tasks` do not change. The switch is the environment's: nothing
moves until `task_check.py` shows the two sides agree on published days.

    python3 crm_tasks.py 2026-10-07          # print the day's tasks from the CRM
    python3 crm_tasks.py 2026-10-07 --sqlite out/x.db

The database is the D1 REST API with crm_sync's token and ids (CF_API_TOKEN,
CF_ACCOUNT_ID, wrangler.jsonc's database_id), or a local SQLite for a test.
"""
import json
import os
import pathlib
import sys

import crm_import
import crm_sync
import staff

ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = (os.environ.get("TASKS_SOURCE") or "agencyzoom").strip().lower()
WRITER = "pantheon:missed_call_tasks"      # the events row's `who` for a task the nightly makes


def uses_crm():
    return SOURCE == "crm"


class DB:
    """query(sql) -> rows as dicts, over D1's REST API or a SQLite file."""
    def __init__(self, d1=None, sqlite=None):
        self.d1, self.sqlite = d1, sqlite
        if sqlite:
            import sqlite3
            self.c = sqlite3.connect(sqlite)
            self.c.row_factory = sqlite3.Row

    def query(self, sql):
        if self.sqlite:
            cur = self.c.execute(sql)
            rows = [dict(r) for r in cur.fetchall()]
            self.c.commit()
            return rows
        res = self.d1.execute(sql) or []
        return list((res[0] or {}).get("results") or []) if res else []


def connect(sqlite=None, log=print):
    """The CRM, or None (with one log line) when it cannot be reached."""
    if sqlite:
        return DB(sqlite=sqlite)
    tok, dbid, account = crm_sync.token(), crm_sync.database_id(), os.environ.get("CF_ACCOUNT_ID")
    if not (tok and dbid and account):
        log("  crm tasks: CF_API_TOKEN / CF_ACCOUNT_ID / database id missing -- the CRM cannot be read")
        return None
    return DB(d1=crm_sync.D1(account, dbid, tok))


_NAMES = {p["az_id"]: p["name"] for p in staff.PEOPLE if p.get("az_id")}


def _assignee(aid):
    name = _NAMES.get(aid) or ""
    first, _, last = name.partition(" ")
    return {"id": aid, "firstname": first, "lastname": last, "isEmployee": True}


def to_az(row):
    """A CRM task row -> the shape AgencyZoom's /v1/api/tasks/list gives."""
    ctype = row.get("customer_type") or ("lead" if row.get("lead_id") else "customer" if row.get("household_id") else "serviceTicket" if row.get("sr_id") else None)
    cid = row.get("lead_id") or row.get("household_id") or row.get("sr_id")
    due = row.get("due_date") or ""
    return {
        "id": row.get("az_id") or row.get("id"), "crm_id": row.get("id"), "az_id": row.get("az_id"),
        "title": row.get("title") or "", "comments": row.get("comments"), "type": row.get("type"),
        "status": int(row.get("status") or 0),
        "customerType": ctype, "customerId": cid, "customerName": row.get("customer_name"),
        "assigneeId": row.get("assignee_id"),
        "assignees": [_assignee(row["assignee_id"])] if row.get("assignee_id") else [],
        "dueDate": due[:10] or None, "taskDateTime": due or None,
        "timeSpecific": bool(due and not due.endswith("00:00:00")),
        "completeDate": row.get("complete_date"), "completedBy": row.get("completed_by"),
        "createDate": row.get("create_date"), "agencyTodo": bool(row.get("agency_todo")),
    }


SELECT = ("SELECT t.id, t.az_id, t.title, t.comments, t.type, t.assignee_id, t.lead_id, t.household_id, t.sr_id, "
          "t.customer_type, t.due_date, t.status, t.complete_date, t.completed_by, t.agency_todo, t.create_date, "
          "coalesce(nullif(trim(l.firstname || ' ' || l.lastname), ''), l.business_name, "
          "nullif(trim(h.firstname || ' ' || h.lastname), ''), h.business_name) AS customer_name "
          "FROM tasks t LEFT JOIN leads l ON l.id = t.lead_id LEFT JOIN households h ON h.id = t.household_id ")


def read_day(day, db=None, sqlite=None, log=print):
    """Every task due on `day` (the agency's clock), AgencyZoom-shaped, or
    None when the CRM cannot be read -- the callers fall back on that."""
    db = db or connect(sqlite, log=log)
    if db is None:
        return None
    try:
        rows = db.query(SELECT + f"WHERE substr(t.due_date, 1, 10) = {crm_import.q(day)} ORDER BY t.due_date, t.id")
    except Exception as e:
        log(f"  crm tasks: read failed ({type(e).__name__}: {str(e)[:160]})")
        return None
    return [to_az(r) for r in rows]


def create_task(body, day, db=None, sqlite=None, log=print):
    """One task of the nightly's own in the CRM (missed_call_tasks.create's
    AgencyZoom body: title, comments, type, assigneeId, leadId or
    customerId + customerType). az_id NULL -- Pantheon's, never AgencyZoom's
    -- and an events row saying who wrote it. Returns the new id."""
    db = db or connect(sqlite, log=log)
    if db is None:
        raise RuntimeError("the CRM cannot be reached")
    ctype = body.get("customerType")
    cid = body.get("customerId")
    row = {
        "title": body["title"], "comments": body.get("comments"), "type": body.get("type") or "call",
        "assignee_id": body.get("assigneeId"),
        "lead_id": body.get("leadId") or (cid if ctype == "lead" else None),
        "household_id": cid if ctype == "customer" else None,
        "sr_id": cid if ctype == "serviceTicket" else None,
        "customer_type": "lead" if body.get("leadId") else ctype,
        "due_date": f"{day} 00:00:00", "status": 0, "agency_todo": 0,
        "create_date": staff.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    keys = list(row)
    got = db.query(f"INSERT INTO tasks ({', '.join(keys)}) VALUES ({', '.join(crm_import.q(row[k]) for k in keys)}) RETURNING id")
    tid = got[0]["id"] if got else None
    if tid is not None:
        db.query("INSERT INTO events (at, who, object, object_id, action, before, after) VALUES "
                 f"({crm_import.q(row['create_date'])}, {crm_import.q(WRITER)}, 'task', {int(tid)}, 'create', NULL, {crm_import.q(json.dumps(row))})")
    return tid


if __name__ == "__main__":
    a = sys.argv[1:]
    day = next((x for x in a if x[:4].isdigit()), staff.today())
    sqlite = a[a.index("--sqlite") + 1] if "--sqlite" in a else None
    rows = read_day(day, sqlite=sqlite)
    if rows is None:
        sys.exit("could not read the CRM")
    for t in rows:
        print(t["id"], t["status"], (t["assignees"] or [{}])[0].get("firstname", "-"), t["customerType"], t["customerName"], "|", t["title"][:60])
    print(len(rows), "tasks due", day)
