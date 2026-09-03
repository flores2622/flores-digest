"""Find the payload that creates a task on a LEAD, then stop.

    python3 probe_lead_task.py                 # DRY RUN, prints the candidates
    python3 probe_lead_task.py --live          # try them for real, stop at the
                                               # first one that works
    python3 probe_lead_task.py --live --day 2026-09-02

WHY THIS EXISTS. `POST /v1/api/tasks` answers
`400 {"error":"The customer is not found","fieldErrors":[]}` for every
LEAD-bucket missed caller, so those tasks are never created. Established
read-only on 2026-09-02, so do not re-derive it:

  * the shape we send is the shape AgencyZoom itself stores -- an existing lead
    task read back from /v1/api/tasks/list carries customerId + customerType
    "lead" (task 125760240, Edgar Gutierrez, customerId 35856046);
  * the ids we send are real -- GET /v1/api/leads/88605283 returns 200;
  * GET /v1/api/customers/<lead id>/tasks returns null for leads generally,
    which is a different bug (it used to crash the run) and is already fixed.

So it is a create-side contract mismatch, not bad data. What is NOT known is
which field or route AgencyZoom wants, and that cannot be settled by reading --
only by trying. Hence this script rather than a guess wired into the nightly
build.

IT IS SAFE TO RUN. A success is a task that is genuinely wanted -- the caller
really did ring and really does need chasing -- so nothing is wasted, and it
stops at the first success so it cannot create duplicates. A failure creates
nothing at all.

WHEN ONE WORKS, fold it into `missed_call_tasks.create()` and delete this file.
If ALL of them fail, stop guessing and ask AgencyZoom support what body creates
a task on a lead: their own automation does it every day ("Never quoted lead-
Day 4 NEW"), so there is a documented answer.
"""
import argparse
import datetime as dt

import secrets_load  # noqa: F401  -- loads secrets/all.env
import missed_call_audit as audit
import missed_call_tasks as m
from az_client import AgencyZoom, BASE

log = audit.log


def candidates(base, lead_id, day):
    """Ordered most to least likely. Each is one POST."""
    due = (day + dt.timedelta(days=1)).isoformat()
    return [
        ("A  leadId instead of customerId",
         "/v1/api/tasks", dict(base, leadId=lead_id)),
        ("B  customerType as a numeric enum",
         "/v1/api/tasks", dict(base, customerId=lead_id, customerType=2)),
        ("C  nested under the lead",
         f"/v1/api/leads/{lead_id}/tasks", dict(base)),
        ("D  current shape plus a due date",
         "/v1/api/tasks",
         dict(base, customerId=lead_id, customerType="lead", dueDate=due)),
    ]


def run(day, live=False):
    azc = AgencyZoom()
    rows = m.enrich(audit.build(day, refresh=False), day)
    todo = [r for r in rows
            if r["back_in"] is None and r.get("record_type") == "lead"]
    if not todo:
        log("no lead-bucket missed callers on this day -- nothing to probe")
        return None
    r = todo[0]
    log(f"probing with {r['name']} -> {r['who']} (lead {r['record_id']})")
    if len(todo) > 1:
        log(f"  {len(todo) - 1} more lead task(s) waiting on the answer: "
            + ", ".join(x["name"] or "?" for x in todo[1:]))
    base = {"title": m.title_for(r),
            "comments": m.meta_line(r) + m.BODIES[r["bucket"]],
            "type": "call",
            "assigneeId": m.EMPLOYEE.get(r["who"], m.FALLBACK)}
    for label, path, body in candidates(base, r["record_id"], day):
        if not live:
            log(f"  would try {label}  POST {path}")
            log(f"    extra keys: "
                f"{ {k: v for k, v in body.items() if k not in base} }")
            continue
        resp = azc.http.request("POST", f"{BASE}{path}",
                                headers={"Authorization": f"Bearer {azc.jwt()}"},
                                json=body, timeout=60)
        log(f"  {label}: HTTP {resp.status_code}")
        if 200 <= resp.status_code < 300:
            log(f"    *** THIS ONE WORKS *** POST {path}")
            log(f"    extra keys: "
                f"{ {k: v for k, v in body.items() if k not in base} }")
            log(f"    response: {resp.text[:200]}")
            log("    Fold this into missed_call_tasks.create() and delete "
                "probe_lead_task.py.")
            return label
        log(f"    {resp.text[:160]}")
    if live:
        log("ALL CANDIDATES FAILED -- do not invent a fifth. Ask AgencyZoom "
            "support what POST body creates a task on a lead.")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", default=None)
    ap.add_argument("--live", action="store_true",
                    help="actually POST; without it nothing is written")
    a = ap.parse_args()
    day = (dt.date.fromisoformat(a.day) if a.day
           else dt.datetime.now(dt.timezone(dt.timedelta(hours=-7))).date())
    if not a.live:
        log("DRY RUN -- nothing will be created. Pass --live to try them.")
    run(day, live=a.live)


if __name__ == "__main__":
    main()
