"""Athena -- the service digest: the service team's day, published to the
board's Service Center. (Apollo is the sales coaching brain; Athena is service's.)

    python3 service_digest.py                  # today, Arizona
    python3 service_digest.py --day 2026-09-22 --dry-run

THE TEAM (Frank, 2026-09-23): Debbie Aguilera (CSR), Amanda Torricellas
(Ops Mngr, titled so on the board from 2026-09-24) and Crystal Mango
(hybrid). Amanda is fully in this digest -- she is
deliberately not tracked on the sales side. Crystal is on both: here only her
service work counts, and her utilization is the whole day, marked hybrid,
because Insightful cannot split a day into sales and service time.

CREDIT GOES TO WHOEVER CLOSED IT (Frank, 2026-09-23), not the assigned CSR:
an SR's `modifiedBy` on completion, a task's `completedBy`. The agency calls
them SRs (service requests), never tickets -- the board says SR throughout.

SERVICE TICKET STATUS 2 IS COMPLETED. CLAUDE.md's "no closed state in this
payload" is about what service_tickets_live() fetches (status [1] only, which
is right for screening calls against OPEN work). Asking for status [2]
returns 19,287 completed tickets, each with completeDate and resolutionDesc --
found 2026-09-23. This module is the only reader of the completed set.

RENEWAL OUTCOMES -- of the renewal SRs completed that day, what happened --
live in service_retention.py. CALL-BACK resolution reuses the missed-call
audit's own grouping and routing, keeping the service-side calls.
"""
import argparse
import collections
import datetime as dt
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
AZ = dt.timezone(dt.timedelta(hours=-7))
PREFIX = "service"

# name -> AgencyZoom user id (the same id is the CSR id on tickets).
SERVICE_TEAM = {
    "Debbie Aguilera": {"az_id": 83597, "role": "CSR"},
    "Amanda Torricellas": {"az_id": 105006, "role": "Ops Mngr"},
    "Crystal Mango": {"az_id": 174445, "role": "Hybrid"},
}
HYBRID_UTIL = {"Crystal Mango"}      # whole-day utilization, shared with sales

# AgencyZoom service pipelines, as the agency uses them (Frank, 2026-09-23).
# Commercial Renewals is not one of them: commercial is Frank's alone and lives
# in Cerberus (commercial.py), and build() drops every commercial SR before
# any figure is read (Frank, 2026-09-24).
# None of these is worked stage by stage except Late Payments; for the rest
# Athena tracks start (createDate) to completion (completeDate) only.
#   (key, board label, AgencyZoom workflowName(s), kind)
PIPELINES = (
    ("renewals_ff", "Farmers & Foremost Renewals", {"Personal Renewals"}, "renewal"),
    ("renewals_bw", "Bristol West Renewals", {"Other 30 day Renewals"}, "renewal"),
    ("changes", "Changes & Service", {"Service Pipeline"}, "service"),   # changes, endorsements, basic service
    ("late_payments", "Late Payments", {"Late Payments"}, "late"),       # the one pipeline tracked by stage
    ("missing_docs", "Missing Documents", {"Missing Documents"}, "docs"),  # contingencies on newly bound policies
    ("reinstatement", "Reinstatement", {"Reinstatement"}, "other"),
)
RENEWALS = {w for _, _, ws, kind in PIPELINES if kind == "renewal" for w in ws}
CHANGES = {"Service Pipeline"}


def pipeline_of(workflow):
    return next((k for k, _, ws, _ in PIPELINES if workflow in ws), "other")
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
    # A day that has ended keeps its first pull (point in time, like every
    # other day file). A day still in progress is re-pulled every build --
    # tickets keep closing, and an earlier checkpoint's copy is stale.
    if f.exists() and day != dt.datetime.now(AZ).date().isoformat():
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
# Every section is stored as ROWS or plain counts, never as a median, so the
# board can add any range of days together and compute the median over the
# whole range itself (Frank, 2026-09-23: "of the renewal SR's that were
# COMPLETED that day (or the range of days filtered to)").
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
    return {name: {"due": due[name], "completed": done[name]} for name in SERVICE_TEAM}


def _seller_index(log=log):
    """household id -> [(soldDate, agentName)], for Missing Documents: the
    SR's household is known, its policies (and their selling producer) come
    from the household map joined to the policy corpus by policy id."""
    import service_retention as sr
    agents = {p["id"]: p.get("agentName") for p in
              json.loads((ROOT / "data/az_policies_all.json").read_text())}
    out = collections.defaultdict(list)
    for cid, v in sr.load_household_map(log=log).items():
        for p in v.get("policies") or []:
            if p.get("soldDate") and agents.get(p.get("id")):
                out[cid].append((str(p["soldDate"])[:10], agents[p["id"]]))
    return out


def _handler(sr_row, sellers):
    """Missing Documents: who took care of it -- the policy's own selling
    producer, a service/hybrid rep, or another producer. The seller is whoever
    sold the household's policy most recently before the SR opened (within
    60 days): a missing-document SR is opened just after binding."""
    import digest_config as cfg
    closer = sr_row.get("modifiedBy")
    opened = str(sr_row.get("createDate") or "")[:10]
    lo = (dt.date.fromisoformat(opened) - dt.timedelta(days=60)).isoformat() if opened else ""
    sold = sorted(x for x in sellers.get(str(sr_row.get("householdId")), []) if lo <= x[0] <= opened)
    seller = sold[-1][1] if sold else None
    if seller and closer == seller:
        kind = "selling producer"
    elif closer in SERVICE_TEAM:
        kind = "service/hybrid rep"
    elif closer in cfg.PRODUCERS:
        kind = "another producer" if seller else "producer"
    else:
        kind = "other"
    return kind, seller


def sr_figures(day, done, live, log=log):
    """SRs completed on the day -- one row each: which pipeline, who completed
    it, hours from opened to completed, and for Missing Documents who took
    care of it -- plus each person's open and overdue SRs at the end of the
    day, and the Late Payment pipeline's open SRs by stage."""
    completed, sellers = [], None
    for r in done:
        if str(r.get("completeDate") or "")[:10] != day:
            continue
        h = _hours(r.get("createDate"), r.get("completeDate"))
        pipe = pipeline_of(r.get("workflowName"))
        row = {"by": _team_name(r.get("modifiedBy")), "by_name": r.get("modifiedBy"),
               "pipeline": pipe, "hours": round(h, 2) if h is not None else None}
        if pipe == "missing_docs":
            if sellers is None:
                sellers = _seller_index(log=log)
            row["handler"], row["seller"] = _handler(r, sellers)
        completed.append(row)

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

    # Late Payments is the one pipeline worked by stage: where the open SRs
    # sit at the end of the day, and how long they have been there.
    end = dt.datetime.fromisoformat(f"{day}T23:59:59")
    stages = collections.defaultdict(list)
    for t in live:
        if pipeline_of(t.get("workflowName")) != "late_payments":
            continue
        created = str(t.get("createDate") or "")[:10]
        if created and created > day:
            continue
        since = t.get("enterStageTS") or t.get("createDate")
        try:
            in_stage = (end - dt.datetime.fromisoformat(str(since)[:19])).total_seconds() / 86400
        except ValueError:
            in_stage = None
        stages[t.get("workflowStageName") or "(no stage)"].append(
            round(in_stage, 1) if in_stage is not None and in_stage >= 0 else None)
    late_stages = [{"stage": k, "open": len(v),
                    "days_in_stage": sorted(x for x in v if x is not None)}
                   for k, v in sorted(stages.items(), key=lambda kv: -len(kv[1]))]
    return {"completed": completed, "backlog": backlog, "late_payment_stages": late_stages}


# Missed-call buckets (missed_call_audit.route) that are service work. An open
# lead or a closed lead is a sales call back; those stay with the producers.
SERVICE_CALL_BUCKETS = {"customer", "open SR", "no record"}


def callback_figures(day, recs=None, commercial_only=frozenset()):
    """Call-back resolution: each missed or voicemail call-in to the office
    (grouped per caller per hour, exactly as the missed-call audit does) that
    routes to service, and the minutes until the first outbound call back to
    that number, credited to whoever made it. Same-day only: a call missed at
    5:20 and returned tomorrow reads as not returned. Texts are not counted --
    a hand-typed reply lives on LEAD notes, which a service customer usually
    does not have. A caller from a commercial-only household is Cerberus's,
    not the team's, and is left out (Frank, 2026-09-24)."""
    import commercial
    import missed_call_audit as mca
    recs = recs if recs is not None else mca.collect(day, refresh=False)
    idx, *_ = mca.build_index(day)
    rows = []
    for n, calls in mca.group(recs):
        bucket = mca.route(idx.get(n))[0]
        if bucket not in SERVICE_CALL_BUCKETS:
            continue
        if commercial.is_commercial_caller(idx.get(n), commercial_only):
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
                     "by": (back[1] if back[1] in SERVICE_TEAM else "other") if back else None})
    return {"rows": rows}


def util_figures(day):
    import insightful_util as iu
    util, _, detail = iu.pull(day)
    out = {}
    for name in SERVICE_TEAM:
        u, d = util.get(name), detail.get(name) or {}
        out[name] = {"pct": u[0] if u else None,
                     "total": u[1] if u else None,
                     "productive": u[2] if u else None,
                     "productive_min": d.get("productive_min"),
                     "total_min": d.get("total_min"),
                     "hybrid": name in HYBRID_UTIL,
                     "tracked": bool(d.get("tracked"))}
    return out


def build(day, log=log, refresh_households=True):
    tasks = json.loads((ROOT / f"data/az_tasks_{day}.json").read_text())
    live_f = ROOT / f"data/az_service_tickets_{day}.json"
    live = json.loads(live_f.read_text()) if live_f.exists() else []
    done = completed_tickets(day, log=log)
    # Commercial work is Cerberus's (commercial.py): it leaves every figure
    # below, SRs, renewal outcomes and call backs alike.
    import commercial
    import service_retention
    com_any, com_only = commercial.households(service_retention.load_household_map(log=log))
    done = [t for t in done if not commercial.is_commercial_sr(t, com_any)]
    live = [t for t in live if not commercial.is_commercial_sr(t, com_any)]
    # Each section may fail alone: a bad renewal read must not cost the task
    # and SR cards that are already right.
    try:
        util = util_figures(day)
    except Exception as e:
        log(f"  utilization failed ({type(e).__name__}: {e})")
        util = {}
    try:
        callbacks = callback_figures(day, commercial_only=com_only)
    except Exception as e:
        log(f"  call backs failed ({type(e).__name__}: {e})")
        callbacks = None
    try:
        import service_retention as sr
        rows, unnamed = sr.renewal_srs(
            day, done, json.loads((ROOT / "data/az_policies_all.json").read_text()),
            json.loads((ROOT / "data/az_customers_all.json").read_text()),
            log=log, refresh=refresh_households)
        renewals = {"rows": rows, "unnamed": unnamed,
                    "resolutions_from": sr.RESOLUTIONS_FROM,
                    "outcomes": [list(o) for o in sr.OUTCOMES]}
    except Exception as e:
        log(f"  renewal outcomes failed ({type(e).__name__}: {e})")
        renewals = None
    return {
        "version": 2,
        "date": day,
        "label": dt.date.fromisoformat(day).strftime("%A, %B %-d, %Y"),
        "built_at": dt.datetime.now(AZ).isoformat(timespec="seconds"),
        "team": [{"name": n, "role": v["role"]} for n, v in SERVICE_TEAM.items()],
        "tasks": task_figures(tasks),
        "srs": sr_figures(day, done, live, log=log),
        "pipelines": [[k, label, kind] for k, label, _, kind in PIPELINES],
        "renewals": renewals,
        "callbacks": callbacks,
        "utilization": util,
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
