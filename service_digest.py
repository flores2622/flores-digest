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
    # Contingencies: any contingency pending on a policy. AgencyZoom's
    # "Missing Documents" workflow, renamed by Frank 2026-09-24 -- the list
    # endpoint returns the new name on every SR, old ones included. The key
    # stays missing_docs so earlier days' rows still add up with new ones.
    ("missing_docs", "Contingencies", {"Contingencies", "Missing Documents"}, "docs"),
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
    n_pulled = len(out)
    out = list({r.get("id"): r for r in out}.values())     # paging can repeat a row
    # An SR can also LEAVE the completed list: Debbie completed Late Payments
    # SR 12245539 on 09-01 and Amanda reopened it on 09-24, so every pull from
    # that afternoon lost it and 09-01's day file read 32 SRs, not 33. It was
    # completed on 09-01 all the same, so anything in the last saved file that
    # this pull is missing is added back -- a day's SRs never shrink. If it is
    # completed again, the fresh copy (new completeDate) wins, above.
    prev_day, prev = _previous_done(day, log=log)
    if prev:
        have = {r.get("id") for r in out}
        back = [r for r in prev if r.get("id") not in have
                and str(r.get("createDate") or "")[:10] >= floor]
        out += back
        if back:
            log(f"  completed service tickets: {len(back)} missing from this pull, "
                f"added back from {prev_day}'s saved file")
    else:
        log("  completed service tickets: no earlier saved file to check this pull against")
    f.write_text(json.dumps(out))
    log(f"  completed service tickets: {len(out)} ({page} pages, {n_pulled} rows pulled)")
    return out


def _previous_done(day, log=log, back_days=10):
    """(day, rows) of the most recent completed-SR file saved before `day`,
    local first and then the R2 day cache -- or (None, None)."""
    d = dt.date.fromisoformat(day)
    cli = None
    for i in range(1, back_days + 1):
        p_day = (d - dt.timedelta(days=i)).isoformat()
        name = f"az_service_tickets_done_{p_day}.json"
        f = ROOT / "data" / name
        if f.exists():
            return p_day, json.loads(f.read_text())
        try:
            import r2_cache
            if cli is None:
                cli, bucket = r2_cache._client()
            return p_day, json.loads(cli.get_object(Bucket=bucket, Key=r2_cache._key(p_day, name))["Body"].read())
        except Exception:
            continue
    return None, None


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


def sr_outcomes(srs, log=log):
    """{sr id: (outcome, source)} for the Service Pipeline, Late Payments and
    Contingencies SRs among `srs`, read from the reps' notes (service_notes.py,
    Frank, 2026-09-24). Never raises: a failed read leaves those SRs out."""
    import service_notes as sn
    out = {}
    try:
        by_pipe = collections.defaultdict(list)
        for t in srs:
            pipe = pipeline_of(t.get("workflowName"))
            if pipe in sn.OUTCOMES:
                by_pipe[pipe].append(t)
        for pipe, ts in by_pipe.items():
            reads = sn.read(pipe, ts, log=log)
            for t in ts:
                out[t.get("id")] = sn.sr_outcome(pipe, t, reads.get(str(t.get("id"))))
    except Exception as e:
        log(f"  SR outcomes failed ({type(e).__name__}: {e})")
    return out


def sr_outcome_labels():
    import service_notes as sn
    return {pipe: sn.outcomes(pipe) for pipe in sn.OUTCOMES}


def sr_figures(day, done, live, log=log):
    """SRs completed on the day -- one row each: the SR, which pipeline, who
    completed it, hours from opened to completed, for Contingencies who took
    care of it, and for Service Pipeline, Late Payments and Contingencies how
    it ended (sr_outcomes) -- plus each person's open and overdue SRs at the
    end of the day, and the Late Payment pipeline's open SRs by stage."""
    completed, sellers = [], None
    day_srs = [r for r in done if str(r.get("completeDate") or "")[:10] == day]
    ended = sr_outcomes(day_srs, log=log)
    for r in day_srs:
        h = _hours(r.get("createDate"), r.get("completeDate"))
        pipe = pipeline_of(r.get("workflowName"))
        row = {"id": r.get("id"), "by": _team_name(r.get("modifiedBy")), "by_name": r.get("modifiedBy"),
               "pipeline": pipe, "hours": round(h, 2) if h is not None else None}
        if pipe == "missing_docs":
            if sellers is None:
                sellers = _seller_index(log=log)
            row["handler"], row["seller"] = _handler(r, sellers)
        if r.get("id") in ended:
            row["outcome"], row["source"] = ended[r.get("id")]
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
    return {"completed": completed, "outcomes": sr_outcome_labels(),
            "backlog": backlog, "late_payment_stages": late_stages}


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
                    "outcomes": sr.outcomes()}
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


# How far back refresh_past_renewals() re-reads published days. Renewal SRs
# are worked ~45 days before the renewal date (median 44, 09-15..09-23), and
# a cancellation or rewrite shows in the record up to 45 days after it.
REFRESH_BACK_DAYS = 120


def refresh_past_renewals(day, log=log):
    """Re-derive the renewal outcome of every SR on the published days before
    `day`, and republish a day only if one changed.

    A day's document is built once, so its renewal rows froze at the policy
    record as of that night -- an SR worked 44 days early read "Renewal date
    still ahead" for good (found 2026-09-24). This re-reads ONLY the renewal
    rows' outcome and where it came from (the rep's note, then the record as
    of today); every other section, and which SRs are in the day, stay exactly
    as first built -- the point-in-time rule for live SRs is untouched."""
    import commercial
    import publish_board
    import service_retention as sr
    done = completed_tickets(day, log=log)
    com_any, _ = commercial.households(sr.load_household_map(log=log))
    done = [t for t in done if not commercial.is_commercial_sr(t, com_any)]
    pol = json.loads((ROOT / "data/az_policies_all.json").read_text())
    cus = json.loads((ROOT / "data/az_customers_all.json").read_text())
    floor = (dt.date.fromisoformat(day) - dt.timedelta(days=REFRESH_BACK_DAYS)).isoformat()
    cli, bucket = publish_board._client()
    keys, token = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": f"{PREFIX}/"}
        if token:
            kw["ContinuationToken"] = token
        r = cli.list_objects_v2(**kw)
        keys += [o["Key"] for o in r.get("Contents", [])]
        if not r.get("IsTruncated"):
            break
        token = r["NextContinuationToken"]
    days = sorted(k[len(PREFIX) + 1:-5] for k in keys if k.endswith(".json"))
    changed, sellers = 0, None
    for d in [x for x in days if floor <= x < day]:
        try:
            doc = json.loads(cli.get_object(Bucket=bucket, Key=_key(d))["Body"].read())
            n, names = 0, False
            ren = doc.get("renewals") or {}
            if ren.get("rows"):
                fresh, _ = sr.renewal_srs(d, done, pol, cus, log=log, refresh=False)
                fresh = {r["id"]: r for r in fresh}
                for row in ren["rows"]:
                    f = fresh.get(row["id"])
                    if f and (f["outcome"], f["source"]) != (row["outcome"], row["source"]):
                        for k in ("outcome", "source", "policy", "premium", "line"):
                            row[k] = f[k]
                        n += 1
                # A resolution added or renamed in AgencyZoom changes the names
                # every day's legend shows, even where no row's outcome moved.
                if ren.get("outcomes") != sr.outcomes():
                    ren["outcomes"], names = sr.outcomes(), True
            if sellers is None:
                sellers = _seller_index(log=log)
            m, sr_names = refresh_completed_outcomes(d, doc, done, sellers, log=log)
            if not (n or names or m or sr_names):
                continue
            doc["renewals_refreshed"] = dt.datetime.now(AZ).isoformat(timespec="seconds")
            cli.put_object(Bucket=bucket, Key=_key(d), Body=json.dumps(doc, default=str).encode(),
                           ContentType="application/json", CacheControl="no-store")
            changed += 1
            log(f"  refresh: {d} -- {n} renewal outcome(s), {m} other SR row change(s)"
                + (", outcome names updated" if names or sr_names else ""))
        except Exception as e:
            log(f"  renewals: {d} not refreshed ({type(e).__name__}: {e})")
    log(f"  renewals: {changed} earlier day(s) republished")
    return changed


def refresh_completed_outcomes(d, doc, done, sellers, log=log):
    """For one earlier day's document: every completed Service Pipeline, Late
    Payments and Contingencies row's outcome, as refresh_past_renewals does
    for renewals. Rows built before 2026-09-24 carry no SR id, so each is
    matched to that day's SR by who completed it and its hours (both come
    from the SR itself); a Contingencies SR built while the pipeline was
    missed after its rename (pipeline "other") gets its pipeline and who took
    care of it. Which SRs are in the day, and who each is credited to, never
    change. Returns (rows
    changed, outcome names changed)."""
    srs_doc = doc.get("srs") or {}
    rows = srs_doc.get("completed") or []
    day_srs = [t for t in done if str(t.get("completeDate") or "")[:10] == d]
    by_id = {t.get("id"): t for t in day_srs}
    free = collections.defaultdict(list)
    for t in day_srs:
        h = _hours(t.get("createDate"), t.get("completeDate"))
        free[(t.get("modifiedBy"), round(h, 2) if h is not None else None)].append(t)
    used = {r["id"] for r in rows if r.get("id") in by_id}
    ended = sr_outcomes(day_srs, log=log)
    n = 0
    for row in rows:
        t = by_id.get(row.get("id"))
        if t is None:
            cand = [x for x in free.get((row.get("by_name"), row.get("hours")), [])
                    if x.get("id") not in used]
            if not cand:
                # Someone edited the SR since (its modifiedBy moved): the
                # pipeline and hours alone. The row keeps who was credited.
                cand = [x for k, xs in free.items() if k[1] == row.get("hours") for x in xs
                        if x.get("id") not in used
                        and pipeline_of(x.get("workflowName")) in (row.get("pipeline"), "missing_docs")]
            if not cand:
                continue
            t = cand[0]
            used.add(t.get("id"))
            row["id"] = t.get("id")
            n += 1
        pipe = pipeline_of(t.get("workflowName"))
        if row.get("pipeline") != pipe:
            row["pipeline"] = pipe
            n += 1
        if pipe == "missing_docs" and "handler" not in row:
            row["handler"], row["seller"] = _handler(t, sellers)
            n += 1
        e = ended.get(t.get("id"))
        if e and (row.get("outcome"), row.get("source")) != e:
            row["outcome"], row["source"] = e
            n += 1
    names = srs_doc.get("outcomes") != sr_outcome_labels()
    if names and "srs" in doc:
        srs_doc["outcomes"] = sr_outcome_labels()
    # Pipeline names too (Missing Documents became Contingencies, 2026-09-24).
    pipes = [[k, label, kind] for k, label, _, kind in PIPELINES]
    if doc.get("pipelines") != pipes:
        doc["pipelines"], names = pipes, True
    return n, names


# How far back backfill_missing_days() looks for a working day with no page.
BACKFILL_BACK_DAYS = 14


def _published_days(cli, bucket):
    keys, token = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": f"{PREFIX}/"}
        if token:
            kw["ContinuationToken"] = token
        r = cli.list_objects_v2(**kw)
        keys += [o["Key"] for o in r.get("Contents", [])]
        if not r.get("IsTruncated"):
            break
        token = r["NextContinuationToken"]
    return {k[len(PREFIX) + 1:-5] for k in keys if k.endswith(".json")}


def backfill_missing_days(day, log=log):
    """Build the Service Center page of any recent working day that has none
    (Frank, 2026-09-24) -- a night the run failed or never happened, as 09-04
    did. Built from that day's own saved files in the R2 day cache; what was
    never saved is recreated only where it cannot have changed since:

      completed SRs   today's pull, cut to SRs created in that day's look-back
                      and completed by the end of it
      tasks           AgencyZoom, a task completed AFTER the day counted open
      call log        RingCentral (a past day's calls do not change)
      open SRs        NOT recreatable -- open SRs close overnight. The page is
                      built without the backlog and Late Payment stages, and
                      says so (open_srs_unavailable).

    Weekends are skipped, and so is a weekday with no SR completed (a holiday
    -- 09-07 had none). Only ever ADDS a page, never touches an existing one."""
    import publish_board
    import r2_cache
    cli, bucket = publish_board._client()
    have = _published_days(cli, bucket)
    d0 = dt.date.fromisoformat(day)
    want = [x.isoformat() for x in (d0 - dt.timedelta(days=i) for i in range(1, BACKFILL_BACK_DAYS + 1))
            if x.weekday() < 5 and x.isoformat() not in have]
    if not want:
        log("  service backfill: no missing days")
        return []
    today_done = completed_tickets(day, log=log)
    rcli, rbucket = r2_cache._client()
    built = []
    for d in sorted(want):
        try:
            if not any(str(t.get("completeDate") or "")[:10] == d for t in today_done):
                log(f"  service backfill: {d} had no SR completed -- skipped (holiday?)")
                continue

            def saved(name):
                try:
                    return rcli.get_object(Bucket=rbucket, Key=r2_cache._key(d, name))["Body"].read()
                except Exception:
                    return None

            def keep(name, body, upload):
                (ROOT / "data" / name).write_bytes(body)
                if not upload:          # already in the day cache
                    return
                try:
                    rcli.put_object(Bucket=rbucket, Key=r2_cache._key(d, name), Body=body,
                                    ContentType="application/json")
                except Exception as e:
                    log(f"  service backfill: {name} not saved to R2 ({type(e).__name__})")

            recreated = []
            name = f"az_service_tickets_done_{d}.json"
            body = saved(name)
            if body is None:
                lo = (dt.date.fromisoformat(d) - dt.timedelta(days=TICKET_LOOKBACK_DAYS)).isoformat()
                body = json.dumps([t for t in today_done if lo <= str(t.get("createDate") or "")[:10]
                                   and str(t.get("completeDate") or "")[:10] <= d]).encode()
                recreated.append("completed SRs")
            keep(name, body, "completed SRs" in recreated)

            name = f"az_tasks_{d}.json"
            body = saved(name)
            if body is None:
                from az_client import AgencyZoom
                from az_tasks import STATUS_COMPLETED
                tasks = AgencyZoom().tasks(d, d)
                for t in tasks:
                    if t.get("status") == STATUS_COMPLETED and str(t.get("completeDate") or "")[:10] > d:
                        t["status"], t["completedBy"] = 0, None     # done later: open that evening
                body = json.dumps(tasks).encode()
                recreated.append("tasks")
            keep(name, body, "tasks" in recreated)

            for name in (f"rc_raw_{d}.json", f"rc_window_{d}.json"):
                body = saved(name)
                if body is None and name.startswith("rc_raw"):
                    from rc_client import RingCentral
                    nxt = (dt.date.fromisoformat(d) + dt.timedelta(days=1)).isoformat()
                    body = json.dumps(RingCentral().call_log(f"{d}T00:00:00-07:00",
                                                             f"{nxt}T00:00:00-07:00")).encode()
                    recreated.append("call log")
                if body is not None:
                    keep(name, body, name.startswith("rc_raw") and "call log" in recreated)

            name = f"az_service_tickets_{d}.json"
            live = saved(name)
            if live is not None:
                (ROOT / "data" / name).write_bytes(live)
            else:
                (ROOT / "data" / name).unlink(missing_ok=True)

            doc = build(d, log=log, refresh_households=False)
            if live is None:
                doc["srs"]["backlog"], doc["srs"]["late_payment_stages"] = {}, []
                doc["open_srs_unavailable"] = ("no end-of-day open-SR snapshot was saved for this "
                                               "day; backlog and Late Payment stages left out")
            doc["backfilled"] = {"on": day, "recreated": recreated}
            publish(d, doc, log=log)
            built.append(d)
            log(f"  service backfill: built {d}" + (f" (recreated: {', '.join(recreated)})" if recreated else "")
                + ("" if live is not None else " -- no open-SR snapshot, backlog left out"))
        except Exception as e:
            log(f"  service backfill: {d} failed ({type(e).__name__}: {e})")
    return built


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--refresh-renewals", action="store_true",
                    help="only re-read the renewal outcomes of earlier published days")
    ap.add_argument("--backfill", action="store_true",
                    help="only build recent working days that have no page")
    a = ap.parse_args()
    day = a.day or dt.datetime.now(AZ).date().isoformat()
    import os
    os.chdir(ROOT)
    import secrets_load
    secrets_load.load()
    if a.backfill:
        backfill_missing_days(day)
        return
    if a.refresh_renewals:
        refresh_past_renewals(day)
        return
    doc = build(day)
    if a.dry_run:
        print(json.dumps(doc, indent=1, default=str))
        return
    publish(day, doc)


if __name__ == "__main__":
    main()
