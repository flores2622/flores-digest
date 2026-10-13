"""Phase 2's cutover test: Task Completion from AgencyZoom and from the CRM,
side by side, on a published day (CRM.md: "Task Completion identical both
ways on a day run in parallel").

    python3 task_check.py 2026-10-07            # print the comparison
    python3 task_check.py 2026-10-07 --publish  # and write it to R2
    python3 task_check.py 2026-10-07 --sqlite out/x.db

The nightly calls `run(day)` after `crm_sync` has mirrored the day, so the
CRM holds what AgencyZoom held when the figure was built. It audits both
sides with the same verdicts (`task_audit.cancellation_verdicts` on the
AgencyZoom file) and writes R2 `crm/task_check/<day>.json`: each side's
per-producer total / completed / pct and team figure, whether they agree,
every difference, and the task ids one side has and the other does not.
The Tasks page shows the last 14 days (`GET /api/crm/taskcheck`). Never
raises from the nightly.
"""
import json
import pathlib
import sys

import az_tasks
import crm_tasks
import staff
from digest_config import PRODUCERS

ROOT = pathlib.Path(__file__).resolve().parent
R2_PREFIX = "crm/task_check/"


def _figures(audit):
    per = {n: {"total": p["total"], "completed": p["completed"], "pct": p["pct"], "excused": p.get("excused", 0)}
           for n, p in audit["per_producer"].items()}
    return {"per": per, "team": {k: audit["team"][k] for k in ("total", "completed", "pct")}}


def compare(day, az_rows, crm_rows, verdicts):
    a, c = az_tasks.audit(az_rows, verdicts), az_tasks.audit(crm_rows, verdicts)
    fa, fc = _figures(a), _figures(c)
    diffs = []
    for n in PRODUCERS:
        x, y = fa["per"][n], fc["per"][n]
        if (x["total"], x["completed"]) != (y["total"], y["completed"]):
            diffs.append({"who": n, "agencyzoom": x, "crm": y})
    if (fa["team"]["total"], fa["team"]["completed"]) != (fc["team"]["total"], fc["team"]["completed"]):
        diffs.append({"who": "Team", "agencyzoom": fa["team"], "crm": fc["team"]})
    az_ids = {t.get("id") for t in az_rows}
    crm_ids = {t.get("id") for t in crm_rows}
    return {
        "day": day, "built": staff.now().strftime("%Y-%m-%d %H:%M:%S"), "source": crm_tasks.SOURCE,
        "agencyzoom": fa, "crm": fc, "agree": not diffs, "differences": diffs,
        "counts": {"agencyzoom": len(az_rows), "crm": len(crm_rows)},
        "missing_in_crm": sorted(i for i in az_ids - crm_ids if i is not None)[:50],
        "extra_in_crm": sorted(i for i in crm_ids - az_ids if i is not None)[:50],
    }


def build(day, sqlite=None, log=print):
    path = ROOT / f"data/az_tasks_{day}.json"
    if not path.exists():
        log(f"  task check: no data/az_tasks_{day}.json -- skipped")
        return None
    az_rows = json.loads(path.read_text())
    crm_rows = crm_tasks.read_day(day, sqlite=sqlite, log=log)
    if crm_rows is None:
        return None
    import task_audit
    verdicts = task_audit.cancellation_verdicts(day, az_rows, {v["az_id"]: k for k, v in PRODUCERS.items()})
    return compare(day, az_rows, crm_rows, verdicts)


def publish(doc, log=print):
    import publish_board
    cli, bucket = publish_board._client()
    cli.put_object(Bucket=bucket, Key=f"{R2_PREFIX}{doc['day']}.json", Body=json.dumps(doc).encode(), ContentType="application/json")
    log(f"  task check {doc['day']}: AgencyZoom {doc['agencyzoom']['team']['completed']}/{doc['agencyzoom']['team']['total']}, "
        f"CRM {doc['crm']['team']['completed']}/{doc['crm']['team']['total']} -- {'agree' if doc['agree'] else str(len(doc['differences'])) + ' differences'}")


def run(day, log=print):
    """The nightly's call, after crm_sync: never raises."""
    try:
        doc = build(day, log=log)
        if doc:
            publish(doc, log=log)
        return doc
    except (Exception, SystemExit) as e:
        log(f"  task check failed ({type(e).__name__}: {str(e)[:200]}) -- carrying on")
        return None


if __name__ == "__main__":
    a = sys.argv[1:]
    day = next((x for x in a if x[:4].isdigit()), staff.today())
    sqlite = a[a.index("--sqlite") + 1] if "--sqlite" in a else None
    doc = build(day, sqlite=sqlite)
    if not doc:
        sys.exit("nothing to compare")
    print(json.dumps({k: doc[k] for k in ("day", "agree", "counts", "differences", "missing_in_crm", "extra_in_crm")}, indent=1))
    for n in PRODUCERS:
        print(f"  {n:18s} AgencyZoom {doc['agencyzoom']['per'][n]['completed']}/{doc['agencyzoom']['per'][n]['total']}   CRM {doc['crm']['per'][n]['completed']}/{doc['crm']['per'][n]['total']}")
    if "--publish" in a:
        publish(doc)
