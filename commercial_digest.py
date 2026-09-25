"""Cerberus -- the Commercial Center's document. (Apollo is sales coaching,
Athena is service, Cerberus is Commercial.)

    python3 commercial_digest.py                   # today, Arizona
    python3 commercial_digest.py --day 2026-09-23 --dry-run
    python3 commercial_digest.py --backfill 2026-01-01   # completed rows back to then

COMMERCIAL IS FRANK'S ALONE (Frank, 2026-09-24). What counts as commercial is
commercial.py, the one definition Athena also excludes by. The board shows
this section to Frank only: site/worker.js refuses /api/commercial to anyone
else, and the left-bar entry stays hidden for them.

ONE DOCUMENT PER DAY, commercial/<day>.json, holding ROWS (Athena's rule), so
the board can add up any range and take medians over the whole of it:
  completed   every commercial SR COMPLETED that day -- renewal or service
              change, who completed it, hours from created to completed, and
              for a renewal its outcome (service_retention.sr_outcome: the
              same seven resolutions, then the rep's note, then Unable to Contact/No Show) and premium;
  open        every commercial SR open at the end of the day, from that day's
              live SR file (data/az_service_tickets_<day>.json, point in
              time -- never re-fetched for a day already built). None on a
              day with no live file (a backfilled day).
The open queue leads: on 2026-09-23 there were 87 open commercial renewal SRs
against 1 completed since June.
"""
import argparse
import collections
import datetime as dt
import json
import pathlib
import re

import commercial

ROOT = pathlib.Path(__file__).resolve().parent
AZ = dt.timezone(dt.timedelta(hours=-7))
PREFIX = "commercial"


def log(*a):
    print(f"[{dt.datetime.now(AZ):%H:%M:%S}]", *a, flush=True)


def _key(day):
    return f"{PREFIX}/{day}.json"


def _d(x):
    return str(x or "")[:10]


def _hours(a, b):
    try:
        t0 = dt.datetime.fromisoformat(str(a)[:19])
        t1 = dt.datetime.fromisoformat(str(b)[:19])
    except ValueError:
        return None
    h = (t1 - t0).total_seconds() / 3600
    return round(h, 2) if h >= 0 else None


def _kind(sr):
    return "renewal" if sr.get("workflowName") in commercial.RENEWAL_WORKFLOWS else "service"


def _current_term(terms):
    """The term the policy is on now: the newest live one (1 in force, 3 next
    term issued), else the newest of any status."""
    live = [t for t in terms if t.get("status") in (1, 3)]
    pool = live or terms
    return max(pool, key=lambda t: _d(t.get("effectiveDate"))) if pool else None


def _policy_fields(sr, chains):
    """(policyNumber, line, premium) for the policies a renewal SR names, from
    each one's current term. A subject can name several ("General Liability -
    P102.624.271 | Professional Liability - P102.624.270"): the premium is
    their sum and the lines are joined. The first number is the one
    service_retention._sr_policy reads, and is the one kept as `policy`. Lines
    are AgencyZoom's own policyTypeName ("Workers Comp")."""
    import service_retention as sr_mod
    first = sr_mod._sr_policy(sr, chains)
    pns = list(dict.fromkeys(
        [first] + [sr_mod._NORM(x) for part in (sr.get("subject") or "").split("|")
                   for x in re.split(r"\s[-\u2013]\s", part)[1:]]))
    terms = [(pn, _current_term(chains.get(pn) or [])) for pn in pns if pn in chains]
    terms = [(pn, t) for pn, t in terms if t]
    if not terms:
        return first, None, None
    lines = [x for x in dict.fromkeys((t.get("policyTypeName") or "").strip() for _, t in terms) if x]
    return (first, " + ".join(lines) or None,
            round(sum(float(t.get("premium") or 0) for _, t in terms)))


def _chains(policies):
    import service_retention as sr_mod
    out = collections.defaultdict(list)
    for p in policies:
        out[sr_mod._NORM(p.get("policyNumber"))].append(p)
    return out


def _row(sr):
    return {"id": sr.get("id"), "kind": _kind(sr), "name": sr.get("name"),
            "subject": (sr.get("subject") or "").strip(),
            "created": _d(sr.get("createDate"))}


def completed_rows(day, done, hh, chains, az=None, log=log):
    """Every commercial SR completed on `day`, one row each."""
    import service_retention as sr_mod
    com_any, _ = commercial.households(hh)
    srs = [t for t in done if _d(t.get("completeDate")) == day
           and commercial.is_commercial_sr(t, com_any)]
    if not srs:
        return [], {}
    pn2hh = {sr_mod._NORM(k): v for k, v in sr_mod.policy_households(hh).items()}
    sr_mod.load_resolution_labels(az=az, log=log)
    today = dt.datetime.now(AZ).date().isoformat()
    as_of = max(day, today)            # the policy record as of today, as Athena reads it
    notes = sr_mod.read_notes([t for t in srs if _kind(t) == "renewal"], log=log)
    rows, unnamed = [], collections.Counter()
    for t in srs:
        row = _row(t)
        row.update({"by_name": t.get("modifiedBy"), "completed": day,
                    "hours": _hours(t.get("createDate"), t.get("completeDate"))})
        if row["kind"] == "renewal":
            key, source, pn, prem, _ = sr_mod.sr_outcome(t, chains, hh, pn2hh, as_of,
                                                         note_key=notes.get(str(t.get("id"))))
            _, line, _ = _policy_fields(t, chains)
            rid = t.get("resolutionId")
            label = sr_mod.RESOLUTION_LABELS.get(rid)
            if day >= sr_mod.RESOLUTIONS_FROM and not sr_mod.resolution_key(t):
                unnamed[label or ("No resolution" if rid is None else f"id {rid}")] += 1
            row.update({"outcome": key, "source": source, "policy": pn,
                        "premium": round(prem), "line": line})
        rows.append(row)
    return rows, dict(unnamed)


def open_rows(day, live, hh, chains):
    """Every commercial SR open at the end of `day`: stage, age, due date and,
    for a renewal, the policy and its current premium."""
    com_any, _ = commercial.households(hh)
    out = []
    for t in live:
        if not commercial.is_commercial_sr(t, com_any):
            continue
        created = _d(t.get("createDate"))
        if created and created > day:
            continue
        if _d(t.get("completeDate")) and _d(t.get("completeDate")) <= day:
            continue
        row = _row(t)
        row.update({"stage": t.get("workflowStageName") or "(no stage)",
                    "due": _d(t.get("dueDate")) or None})
        if row["kind"] == "renewal":
            row["policy"], row["line"], row["premium"] = _policy_fields(t, chains)
        out.append(row)
    return out


def _outcomes():
    import service_retention as sr_mod
    return sr_mod.outcomes(), sr_mod.RESOLUTIONS_FROM


def build(day, done=None, live=None, log=log):
    import service_digest
    import service_retention as sr_mod
    hh = sr_mod.load_household_map(log=log)
    chains = _chains(json.loads((ROOT / "data/az_policies_all.json").read_text()))
    done = done if done is not None else service_digest.completed_tickets(day, log=log)
    if live is None:
        f = ROOT / f"data/az_service_tickets_{day}.json"
        live = json.loads(f.read_text()) if f.exists() else None
    rows, unnamed = completed_rows(day, done, hh, chains, log=log)
    outcomes, since = _outcomes()
    return {
        "version": 1,
        "date": day,
        "label": dt.date.fromisoformat(day).strftime("%A, %B %-d, %Y"),
        "built_at": dt.datetime.now(AZ).isoformat(timespec="seconds"),
        "owner": commercial.FRANK_NAME,
        "completed": rows,
        "unnamed": unnamed,
        "open": open_rows(day, live, hh, chains) if live is not None else None,
        "outcomes": outcomes,
        "resolutions_from": since,
    }


def publish(day, doc=None, log=log):
    import publish_board
    doc = doc if doc is not None else build(day, log=log)
    cli, bucket = publish_board._client()
    body = json.dumps(doc, default=str).encode()
    cli.put_object(Bucket=bucket, Key=_key(day), Body=body,
                   ContentType="application/json", CacheControl="no-store")
    log(f"  commercial: {len(body):,} bytes -> r2://{bucket}/{_key(day)}")
    return _key(day)


REFRESH_BACK_DAYS = 365     # every commercial day on the board (back to 2026-01); only ~13 renewal SRs in all


def refresh_past_renewals(day, log=log):
    """Re-derive the outcome of every commercial renewal SR on the published
    days before `day`, and republish a day only if one changed -- the same
    nightly re-read the Service Center gets (Frank, 2026-09-24). A day's
    document froze its rows on the night it was built, so a note read, a
    resolution picked or renamed later, never reached it. Only each renewal
    row's outcome and where it came from change; which SRs are in a day, the
    service changes and the open queue stay exactly as first built."""
    import publish_board
    import service_digest
    import service_retention as sr_mod
    done = service_digest.completed_tickets(day, log=log)
    hh = sr_mod.load_household_map(log=log)
    chains = _chains(json.loads((ROOT / "data/az_policies_all.json").read_text()))
    floor = (dt.date.fromisoformat(day) - dt.timedelta(days=REFRESH_BACK_DAYS)).isoformat()
    cli, bucket = publish_board._client()
    days = sorted(d for d in service_digest._published_days(cli, bucket, prefix=PREFIX)
                  if floor <= d < day)
    docs = {}
    for d in days:
        try:
            docs[d] = json.loads(cli.get_object(Bucket=bucket, Key=_key(d))["Body"].read())
        except Exception as e:
            log(f"  commercial renewals: {d} not read ({type(e).__name__})")
    # Commercial renewal SRs can be much older than the nightly pull's year
    # (6836965, created 2025-08-03, completed 2026-04-14). If a row on Frank's
    # old categories is missing from the pull, reach back once to its SR.
    keys = {k for k, _, _ in sr_mod.OUTCOMES}
    have = {t.get("id") for t in done}
    stale = [r for doc in docs.values() for r in doc.get("completed") or []
             if r.get("kind") == "renewal" and r.get("id") not in have and r.get("outcome") not in keys]
    if stale:
        oldest = min(_d(r.get("created")) or day for r in stale)
        from az_client import AgencyZoom
        az, page, extra = AgencyZoom(), 0, []
        while True:
            rows = (az.service_tickets({"status": [2], "page": page, "pageSize": 100}) or {}).get("serviceTickets") or []
            keep = [r for r in rows if _d(r.get("createDate")) >= oldest]
            extra += [r for r in keep if r.get("id") not in have]
            page += 1
            if len(rows) < 100 or not keep:
                break
        done = done + extra
        log(f"  commercial renewals: {len(stale)} older SR(s) not in tonight's pull -- "
            f"reached back to {oldest} ({page} pages)")
    changed = 0
    for d in days:
        if d not in docs:
            continue
        try:
            doc = docs[d]
            rows = [r for r in doc.get("completed") or [] if r.get("kind") == "renewal"]
            if not rows:
                continue
            fresh, _ = completed_rows(d, done, hh, chains, log=log)
            fresh = {r["id"]: r for r in fresh if r.get("kind") == "renewal"}
            n = 0
            for row in rows:
                f = fresh.get(row["id"])
                if f and (f.get("outcome"), f.get("source")) != (row.get("outcome"), row.get("source")):
                    for k in ("outcome", "source", "policy", "premium", "line"):
                        row[k] = f.get(k)
                    n += 1
            outcomes, _ = _outcomes()
            if not n and doc.get("outcomes") == outcomes:
                continue
            doc["outcomes"] = outcomes
            doc["renewals_refreshed"] = dt.datetime.now(AZ).isoformat(timespec="seconds")
            cli.put_object(Bucket=bucket, Key=_key(d), Body=json.dumps(doc, default=str).encode(),
                           ContentType="application/json", CacheControl="no-store")
            changed += 1
            log(f"  commercial renewals: {d} -- {n} SR outcome(s) updated")
        except Exception as e:
            log(f"  commercial renewals: {d} not refreshed ({type(e).__name__}: {e})")
    log(f"  commercial renewals: {changed} earlier day(s) republished")
    return changed


def backfill(since, until, log=log):
    """Publish every weekday from `since` to `until`: completed rows from one
    pull of the completed set, the open queue only where that day's live SR
    file is on disk (pulled down from R2's cache/<day>/ when it exists). A
    day already published is rebuilt."""
    import publish_board
    from az_client import AgencyZoom
    az = AgencyZoom()
    done, page = [], 0
    floor = (dt.date.fromisoformat(since) - dt.timedelta(days=365)).isoformat()
    while True:
        j = az.service_tickets({"status": [2], "page": page, "pageSize": 100}) or {}
        rows = j.get("serviceTickets") or []
        keep = [r for r in rows if _d(r.get("createDate")) >= floor]
        done += keep
        page += 1
        if len(rows) < 100 or not keep:
            break
    log(f"  completed SRs since {floor}: {len(done)} ({page} pages)")
    cli, bucket = publish_board._client()
    d = dt.date.fromisoformat(since)
    while d.isoformat() <= until:
        day = d.isoformat()
        d += dt.timedelta(days=1)
        if dt.date.fromisoformat(day).weekday() >= 5:
            continue
        f = ROOT / f"data/az_service_tickets_{day}.json"
        if not f.exists():
            try:
                f.write_bytes(cli.get_object(
                    Bucket=bucket, Key=f"cache/{day}/az_service_tickets_{day}.json")["Body"].read())
            except Exception:
                pass
        publish(day, build(day, done=done, log=log), log=log)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backfill", metavar="SINCE")
    ap.add_argument("--refresh-renewals", action="store_true",
                    help="only re-read the renewal outcomes of earlier published days")
    a = ap.parse_args()
    day = a.day or dt.datetime.now(AZ).date().isoformat()
    import os
    os.chdir(ROOT)
    import secrets_load
    secrets_load.load()
    if a.backfill:
        backfill(a.backfill, day)
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
