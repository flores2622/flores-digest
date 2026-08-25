"""Task completion audit, with service/renewal/change work excluded entirely.

TASK STATUS SEMANTICS (decoded 2026-08-14 from the 2026-08-07 task set; the
field is an integer with no accompanying label anywhere in the payload):

    status 1  -> COMPLETED. Always accompanied by completeDate and completedBy.
                 206 of 226 tasks due 2026-08-07.
    status 2  -> closed WITHOUT completion. completeDate and completedBy are
                 always null; agencyTodo.closeDate is set on about half of them.
                 19 of 226.
    status 0  -> still open. 1 of 226.

    The trap: agencyTodo.closeDate is set on some status-2 rows, so treating
    "has a close date" as done marks dismissed tasks complete and returns a
    flat 100% for every producer. Completion is status == 1, nothing else.

EXCLUSIONS (HANDOFF_4 s5): service, renewal and change work is excluded
entirely -- from the numbers AND from the report. Of the 226 tasks due
2026-08-07, 47 hang off a customer record and 1 matches on body text.
"""
import json

from digest_config import (PRODUCERS, SERVICE_BODY_RE, SERVICE_TITLE_RE,
                           TEAM_SCALE)

STATUS_COMPLETED = 1
STATUS_CLOSED_NOT_COMPLETED = 2
STATUS_OPEN = 0


def service_reason(task):
    """Why this task is service/renewal/change work, or None if it is not."""
    if (task.get("customerType") or "").lower() == "customer":
        return "hangs off a customer record"
    if SERVICE_TITLE_RE.search(task.get("title") or ""):
        return "title matches service/renewal pattern"
    if SERVICE_BODY_RE.search(task.get("comments") or ""):
        return "body matches service/renewal pattern"
    return None
    # Deliberately NOT matched: bare "Carrier:" or "Policy Number:".
    # New-business notes routinely record a prospect's current carrier.


def owner(task, az_ids):
    for a in task.get("assignees") or []:
        if a.get("id") in az_ids:
            return az_ids[a["id"]]
    return None


def audit(tasks, verdicts=None):
    """Per-producer task completion, plus the excluded-work tally for the notes.

    `verdicts` is {task_id: 'excluded'|'excused'} from
    task_audit.cancellation_verdicts (Frank, 2026-08-25):

      excluded -- a duplicate lead's task. Not a real task; leaves the audit
                  entirely, like service work.
      excused  -- the producer smart-cycled or killed the lead that day and
                  AgencyZoom's "cancel all related open tasks" checkbox closed
                  the task. Counted OUT of the denominator so it does not drag
                  the rate, but still listed in audit section (d).
    """
    az_ids = {v["az_id"]: k for k, v in PRODUCERS.items()}
    per = {n: {"total": 0, "completed": 0, "closed_not_done": 0, "open": 0,
               "excused": 0, "outstanding": []} for n in PRODUCERS}
    excluded = {"customer record": 0, "title": 0, "body": 0, "duplicate lead": 0}
    verdicts = verdicts or {}

    for t in tasks:
        reason = service_reason(t)
        if reason:
            key = ("customer record" if "customer" in reason
                   else "title" if "title" in reason else "body")
            excluded[key] += 1
            continue
        who = owner(t, az_ids)
        if not who:
            continue
        v = verdicts.get(t.get("id"))
        if v == "excluded":
            excluded["duplicate lead"] += 1
            continue
        p = per[who]
        if v == "excused":
            # Out of the denominator entirely -- neither a pass nor a fail.
            p["excused"] += 1
            continue
        p["total"] += 1
        if t.get("status") == STATUS_COMPLETED:
            p["completed"] += 1
        else:
            if t.get("status") == STATUS_CLOSED_NOT_COMPLETED:
                p["closed_not_done"] += 1
            else:
                p["open"] += 1
            p["outstanding"].append({
                "id": t.get("id"),
                "title": t.get("title"),
                "status": t.get("status"),
                "customer": t.get("customerName"),
            })

    for p in per.values():
        p["pct"] = round(p["completed"] / p["total"] * 100, 1) if p["total"] else None

    tot = sum(p["total"] for p in per.values())
    done = sum(p["completed"] for p in per.values())
    team = {"total": tot, "completed": done,
            "pct": round(done / tot * 100, 1) if tot else None,
            "scale": TEAM_SCALE}
    return {"per_producer": per, "team": team, "excluded": excluded}


if __name__ == "__main__":
    import sys
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-08-07"
    try:
        tasks = json.load(open(f"data/az_tasks_{day}.json"))
    except FileNotFoundError:
        from az_client import AgencyZoom
        tasks = AgencyZoom().tasks(day, day)
        json.dump(tasks, open(f"data/az_tasks_{day}.json", "w"))
    r = audit(tasks)
    print(f"{day}: {len(tasks)} tasks due, "
          f"{sum(r['excluded'].values())} excluded as service/renewal "
          f"({r['excluded']})")
    for n, p in sorted(r["per_producer"].items()):
        print(f"  {n:20} {p['completed']:3}/{p['total']:<3} = {p['pct']}%"
              f"   (closed-not-done {p['closed_not_done']}, open {p['open']})")
    t = r["team"]
    print(f"  {'TEAM':20} {t['completed']:3}/{t['total']:<3} = {t['pct']}%")
