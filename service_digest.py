"""Service digest: the service team's day, published to the board's Service tab.

    python3 service_digest.py                  # today, Arizona
    python3 service_digest.py --day 2026-09-22 --dry-run

THE TEAM (Frank, 2026-09-23): Debbie Aguilera (CSR) and the two hybrids,
Amanda Torricellas and Crystal Mango. Amanda is fully in this digest -- she is
deliberately not tracked on the sales side. Crystal is on both: here only her
service work counts, and her utilization is the whole day, marked hybrid,
because Insightful cannot split a day into sales and service time.

CREDIT GOES TO WHOEVER CLOSED IT (Frank, 2026-09-23), not the assigned CSR:
a ticket's `modifiedBy` on completion, a task's `completedBy`.

SERVICE TICKET STATUS 2 IS COMPLETED. CLAUDE.md's "no closed state in this
payload" is about what service_tickets_live() fetches (status [1] only, which
is right for screening calls against OPEN work). Asking for status [2]
returns 19,287 completed tickets, each with completeDate and resolutionDesc --
found 2026-09-23. This module is the only reader of the completed set.

RETENTION across the renewal window lives in service_retention.py (its
docstring says how each outcome is read). CALL-BACK resolution reuses the
missed-call audit's own grouping and routing, keeping the service-side calls.
"""
import argparse
import collections
import datetime as dt
import json
import pathlib
import statistics

ROOT = pathlib.Path(__file__).resolve().parent
AZ = dt.timezone(dt.timedelta(hours=-7))
PREFIX = "service"

# name -> AgencyZoom user id (the same id is the CSR id on tickets).
SERVICE_TEAM = {
    "Debbie Aguilera": {"az_id": 83597, "role": "CSR"},
    "Amanda Torricellas": {"az_id": 105006, "role": "Hybrid"},
    "Crystal Mango": {"az_id": 174445, "role": "Hybrid"},
}
HYBRID_UTIL = {"Crystal Mango"}      # whole-day utilization, shared with sales

# Ticket workflows -> the digest's resolution-time buckets.
CHANGES = {"Service Pipeline"}
RENEWALS = {"Personal Renewals", "Other 30 day Renewals", "Commercial Renewals"}
BUCKETS = (("changes", "Changes", CHANGES), ("renewals", "Renewals", RENEWALS))
TRAILING_DAYS = 30                   # resolution-time window
TICKET_LOOKBACK_DAYS = 365           # how far back the completed pull pages


def log(*a):
    print(f"[{dt.datetime.now(AZ):%H:%M:%S}]", *a, flush=True)


def _key(day):
    return f"{PREFIX}/{day}.json"


# ---- sources ---------------------------------------------------------------
def completed_tickets(day, az=None, log=log):
    """Completed (status 2) tickets created within TICKET_LOOKBACK_DAYS of
    `day`, cached as data/az_service_tickets_done_<day>.json. The list comes
    back roughly newest-created first; paging stops at the first page with
    nothing inside the lookback. A year covers every ticket completed in the
    last 30 days -- the slowest renewals since June took 46 days at p90."""
    f = ROOT / f"data/az_service_tickets_done_{day}.json"
    if f.exists():
        return json.loads(f.read_text())
    if az is None:
        from az_client import AgencyZoom
        az = AgencyZoom()
    floor = (dt.date.fromisoformat(day) - dt.timedelta(days=TICKET_LOOKBACK_DAYS)).isoformat()
    out, page = [], 0
    while True:
        j = az.service_tickets({"status": [2], "page": page, "pageSize": 100}) or {}
        rows = j.get("serviceTickets") or []
        keep = [r for r in rows if str(r.get("createDate") or "")[:10] >= floor]
        out += keep
        page += 1
        if len(rows) < 100 or not keep:
            break
    f.write_text(json.dumps(out))
    log(f"  completed service tickets: {len(out)} ({page} pages)")
    return out


def _team_name(name):
    return name if name in SERVICE_TEAM else None


def _hours(a, b):
    try:
        t0 = dt.datetime.fromisoformat(str(a)[:19])
        t1 = dt.datetime.fromisoformat(str(b)[:19])
    except ValueError:
        return None
    h = (t1 - t0).total_seconds() / 3600
    return h if h >= 0 else None


# ---- figures ---------------------------------------------------------------
def task_figures(tasks):
    """Service tasks due on the day: per person due (by assignee) and done (by
    whoever completed it). Uses the sales audit's own service test, so a task
    is service here exactly when it is excluded from the sales audit."""
    from az_tasks import STATUS_COMPLETED, service_reason
    by_id = {v["az_id"]: k for k, v in SERVICE_TEAM.items()}
    due = collections.Counter()
    done = collections.Counter()
    for t in tasks:
        if not service_reason(t):
            continue
        for a in t.get("assignees") or []:
            if a.get("id") in by_id:
                due[by_id[a["id"]]] += 1
        if t.get("status") == STATUS_COMPLETED and t.get("completedBy") in by_id:
            done[by_id[t["completedBy"]]] += 1
    out = {}
    for name in SERVICE_TEAM:
        d, c = due[name], done[name]
        out[name] = {"due": d, "completed": c,
                     "pct": round(100 * c / d, 1) if d else None}
    td, tc = sum(due.values()), sum(done.values())
    out["team"] = {"due": td, "completed": tc,
                   "pct": round(100 * tc / td, 1) if td else None}
    return out


def ticket_figures(day, done, live):
    """Tickets closed today, open backlog, and resolution time (open ->
    complete) over the trailing window, per bucket and per closer."""
    lo = (dt.date.fromisoformat(day) - dt.timedelta(days=TRAILING_DAYS - 1)).isoformat()
    window = [r for r in done if lo <= str(r.get("completeDate") or "")[:10] <= day]
    today = [r for r in window if str(r.get("completeDate") or "")[:10] == day]

    def bucket_of(r):
        wf = r.get("workflowName")
        return next((k for k, _, s in BUCKETS if wf in s), "other")

    def summary(rows):
        hs = sorted(h for h in (_hours(r.get("createDate"), r.get("completeDate"))
                                for r in rows) if h is not None)
        if not hs:
            return {"n": 0, "median_h": None, "p90_h": None}
        return {"n": len(hs), "median_h": round(statistics.median(hs), 1),
                "p90_h": round(hs[min(len(hs) - 1, int(len(hs) * 0.9))], 1)}

    resolution = {}
    for key, label, _ in BUCKETS:
        rows = [r for r in window if bucket_of(r) == key]
        resolution[key] = {
            "label": label,
            "team": summary(rows),
            "by_person": {n: summary([r for r in rows if _team_name(r.get("modifiedBy")) == n])
                          for n in SERVICE_TEAM},
        }

    closed_today = {n: collections.Counter() for n in SERVICE_TEAM}
    for r in today:
        n = _team_name(r.get("modifiedBy"))
        if n:
            closed_today[n][bucket_of(r)] += 1

    by_csr = {v["az_id"]: k for k, v in SERVICE_TEAM.items()}
    backlog = {n: {"open": 0, "overdue": 0} for n in SERVICE_TEAM}
    for t in live:
        n = by_csr.get(t.get("csr"))
        created = str(t.get("createDate") or "")[:10]
        if not n or (created and created > day):
            continue
        backlog[n]["open"] += 1
        if str(t.get("dueDate") or "")[:10] and str(t.get("dueDate"))[:10] < day:
            backlog[n]["overdue"] += 1

    return {
        "window_days": TRAILING_DAYS,
        "resolution": resolution,
        "closed_today": {n: dict(c) | {"total": sum(c.values())}
                         for n, c in closed_today.items()},
        "backlog": backlog,
    }


# Missed-call buckets (missed_call_audit.route) that are service work. An open
# lead or a closed lead is a sales call back; those stay with the producers.
SERVICE_CALL_BUCKETS = {"customer", "open SR", "no record"}


def callback_figures(day, recs=None):
    """Call-back resolution: each missed or voicemail call-in to the office
    (grouped per caller per hour, exactly as the missed-call audit does) that
    routes to service, and the time until the first outbound call back to
    that number. Credit goes to whoever made the return call. Same-day only:
    a call missed at 5:20 and returned tomorrow reads as not yet returned.
    Texts are not counted here -- a hand-typed reply lives on LEAD notes,
    which a service customer usually does not have."""
    import missed_call_audit as mca
    recs = recs if recs is not None else mca.collect(day, refresh=False)
    idx, *_ = mca.build_index(day)
    names = set(SERVICE_TEAM)
    rows = []
    for n, calls in mca.group(recs):
        bucket = mca.route(idx.get(n))[0]
        if bucket not in SERVICE_CALL_BUCKETS:
            continue
        last = mca.parse(calls[-1]["startTime"])
        back = None
        for r in recs:
            if r.get("direction") != "Outbound":
                continue
            if mca.norm((r.get("to") or {}).get("phoneNumber")) != n:
                continue
            t = mca.parse(r.get("startTime"))
            if t and last and t > last and (back is None or t < back[0]):
                back = (t, (r.get("from") or {}).get("name") or "")
        rows.append({"bucket": bucket,
                     "minutes": round((back[0] - last).total_seconds() / 60) if back else None,
                     "by": back[1] if back else None})
    done = [r for r in rows if r["minutes"] is not None]
    med = lambda xs: round(statistics.median(xs)) if xs else None
    by_person = {}
    for name in SERVICE_TEAM:
        mine = [r["minutes"] for r in done if r["by"] == name]
        by_person[name] = {"returned": len(mine), "median_min": med(mine)}
    others = [r for r in done if r["by"] not in names]
    return {"missed": len(rows), "returned": len(done),
            "unreturned": len(rows) - len(done),
            "median_min": med([r["minutes"] for r in done]),
            "returned_by_others": len(others),
            "by_bucket": dict(collections.Counter(r["bucket"] for r in rows)),
            "by_person": by_person}


def util_figures(day):
    import insightful_util as iu
    util, _, detail = iu.pull(day)
    out = {}
    for name in SERVICE_TEAM:
        u = util.get(name)
        out[name] = {"pct": u[0] if u else None,
                     "total": u[1] if u else None,
                     "productive": u[2] if u else None,
                     "hybrid": name in HYBRID_UTIL,
                     "tracked": bool((detail.get(name) or {}).get("tracked"))}
    scope = [n for n in SERVICE_TEAM if (detail.get(n) or {}).get("tracked")]
    pm = sum(detail[n]["productive_min"] for n in scope)
    tm = sum(detail[n]["total_min"] for n in scope)
    out["team"] = {"pct": round(100 * pm / tm, 1) if tm else None}
    return out


def build(day, log=log, refresh_households=True):
    tasks = json.loads((ROOT / f"data/az_tasks_{day}.json").read_text())
    live_f = ROOT / f"data/az_service_tickets_{day}.json"
    live = json.loads(live_f.read_text()) if live_f.exists() else []
    done = completed_tickets(day, log=log)
    try:
        util = util_figures(day)
    except Exception as e:
        log(f"  utilization failed ({type(e).__name__}: {e})")
        util = {}
    # Each section may fail alone: a bad retention read must not cost the
    # task and ticket cards that are already right.
    try:
        callbacks = callback_figures(day)
    except Exception as e:
        log(f"  call backs failed ({type(e).__name__}: {e})")
        callbacks = None
    try:
        import service_retention
        retention = service_retention.figures(
            day, json.loads((ROOT / "data/az_policies_all.json").read_text()),
            json.loads((ROOT / "data/az_customers_all.json").read_text()),
            done, log=log, refresh=refresh_households)
    except Exception as e:
        log(f"  retention failed ({type(e).__name__}: {e})")
        retention = None
    return {
        "date": day,
        "label": dt.date.fromisoformat(day).strftime("%A, %B %-d, %Y"),
        "built_at": dt.datetime.now(AZ).isoformat(timespec="seconds"),
        "team": [{"name": n, "role": v["role"]} for n, v in SERVICE_TEAM.items()],
        "tasks": task_figures(tasks),
        "tickets": ticket_figures(day, done, live),
        "utilization": util,
        "callbacks": callbacks,
        "retention": retention,
    }


def publish(day, doc=None, log=log):
    import publish_board
    doc = doc if doc is not None else build(day, log=log)
    cli, bucket = publish_board._client()
    body = json.dumps(doc, default=str).encode()
    cli.put_object(Bucket=bucket, Key=_key(day), Body=body,
                   ContentType="application/json", CacheControl="no-store")
    log(f"  service: {len(body):,} bytes -> r2://{bucket}/{_key(day)}")
    return _key(day)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    day = a.day or dt.datetime.now(AZ).date().isoformat()
    import os
    os.chdir(ROOT)
    import secrets_load
    secrets_load.load()
    doc = build(day)
    if a.dry_run:
        print(json.dumps(doc, indent=1, default=str))
        return
    publish(day, doc)


if __name__ == "__main__":
    main()
