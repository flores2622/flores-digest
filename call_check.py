"""Phase 3's cutover test for calls: AgencyZoom's CALL notes against
Pantheon's own (crm_calls.py), on one day, lead by lead.

    python3 call_check.py 2026-10-13            # print the comparison
    python3 call_check.py 2026-10-13 --publish  # and write it to R2
    python3 call_check.py 2026-10-13 --sqlite out/x.db

The nightly calls `run(day)` after crm_sync and crm_calls, so the CRM holds
both sides. Every CALL note stamped on `day` is read from the CRM: those
with origin "pantheon" are ours, the rest AgencyZoom's (the mirror's
"import"). A pair is MATCHED when the two sit on the same lead, in the
same direction, with starts within MATCH_SECONDS. The result (R2
`crm/call_check/<day>.json`): per producer, how many AgencyZoom wrote,
how many Pantheon wrote, how many matched, and the first 50 of each side
that the other did not have -- an AgencyZoom note Pantheon missed means a
lead the two matched differently (or a call by someone Pantheon does not
write for); a Pantheon note AgencyZoom missed means its integration did
not log the call. `agree` is both lists empty. The Tasks page shows the
last 14 days under the Cutover check (`GET /api/crm/callcheck`). Never
raises from the nightly.
"""
import datetime as dt
import json
import pathlib
import re
import sys

import crm_calls
import crm_tasks
import staff
from digest_config import PRODUCERS

ROOT = pathlib.Path(__file__).resolve().parent
R2_PREFIX = "crm/call_check/"
MATCH_SECONDS = 180
NAMES = {p["az_id"]: p["name"] for p in staff.PEOPLE if p.get("az_id")}

SELECT = ("SELECT n.id, n.lead_id, n.origin, n.attr, n.body, n.created_by, n.create_date, "
          "coalesce(nullif(trim(l.firstname || ' ' || l.lastname), ''), l.business_name) AS lead_name "
          "FROM notes n LEFT JOIN leads l ON l.id = n.lead_id WHERE n.type = 'CALL' AND substr(n.create_date, 1, 10) = {day} "
          "ORDER BY n.create_date, n.id")


def _outbound(row):
    try:
        a = json.loads(row.get("attr") or "{}")
    except ValueError:
        a = {}
    v = a.get("outbound")
    if v is None:
        return None
    return v in (True, 1, "1", "true", "True")


def _secs(row):
    try:
        return dt.datetime.fromisoformat(str(row["create_date"])[:19]).timestamp()
    except ValueError:
        return None


def _line(row):
    return {"note_id": row["id"], "lead_id": row["lead_id"], "lead": row.get("lead_name"), "at": row["create_date"],
            "outbound": _outbound(row), "who": NAMES.get(row.get("created_by")) or None}


NO_NUMBER = re.compile(r"From:\s*<br\s*/?>\s*To:\s*<br", re.I)


def compare(day, rows):
    """AgencyZoom's integration also writes CALL notes with no number at all
    (From: / To: empty, Duration: (s) -- a ring on a group line, a queue
    event); those are `noise`, counted and left out. Inbound notes are
    compared and listed but do not decide `agree`: AgencyZoom logs a call-in
    on whoever's line rang, Pantheon on whoever answered. `agree` is every
    outbound note with a number matched both ways."""
    ours = [r for r in rows if r.get("origin") == crm_calls.ORIGIN]
    theirs_all = [r for r in rows if r.get("origin") != crm_calls.ORIGIN]
    noise = [r for r in theirs_all if NO_NUMBER.search(str(r.get("body") or ""))]
    theirs = [r for r in theirs_all if r["id"] not in {n["id"] for n in noise}]
    used, matched = set(), 0
    only_ours = []
    for o in ours:
        t0, lead, ob = _secs(o), o["lead_id"], _outbound(o)
        best = None
        for t in theirs:
            if t["id"] in used or t["lead_id"] != lead:
                continue
            tb = _outbound(t)
            if tb is not None and ob is not None and tb != ob:
                continue
            t1 = _secs(t)
            if t0 is None or t1 is None or abs(t0 - t1) > MATCH_SECONDS:
                continue
            if best is None or abs(t1 - t0) < abs(_secs(best) - t0):
                best = t
        if best is None:
            only_ours.append(_line(o))
        else:
            used.add(best["id"])
            matched += 1
    only_theirs = [_line(t) for t in theirs if t["id"] not in used]
    per = {}
    for n, p in PRODUCERS.items():
        aid = p["az_id"]
        per[n] = {"agencyzoom": sum(1 for t in theirs if t.get("created_by") == aid),
                  "pantheon": sum(1 for o in ours if o.get("created_by") == aid),
                  "only_agencyzoom": sum(1 for x in only_theirs if x["who"] == n),
                  "only_pantheon": sum(1 for x in only_ours if x["who"] == n)}
    out_theirs = [x for x in only_theirs if x["outbound"]]
    out_ours = [x for x in only_ours if x["outbound"]]
    return {
        "day": day, "built": staff.now().strftime("%Y-%m-%d %H:%M:%S"),
        "counts": {"agencyzoom": len(theirs), "pantheon": len(ours), "matched": matched, "noise": len(noise),
                   "only_agencyzoom_outbound": len(out_theirs), "only_pantheon_outbound": len(out_ours),
                   "only_agencyzoom_inbound": len(only_theirs) - len(out_theirs), "only_pantheon_inbound": len(only_ours) - len(out_ours)},
        "per": per, "agree": not out_ours and not out_theirs,
        "only_agencyzoom": (out_theirs + [x for x in only_theirs if not x["outbound"]])[:50],
        "only_pantheon": (out_ours + [x for x in only_ours if not x["outbound"]])[:50],
    }


def build(day, sqlite=None, log=print):
    db = crm_tasks.connect(sqlite, log=log)
    if db is None:
        return None
    try:
        import crm_import
        rows = db.query(SELECT.format(day=crm_import.q(day)))
    except Exception as e:
        log(f"  call check: read failed ({type(e).__name__}: {str(e)[:160]})")
        return None
    return compare(day, rows)


def publish(doc, log=print):
    import publish_board
    cli, bucket = publish_board._client()
    cli.put_object(Bucket=bucket, Key=f"{R2_PREFIX}{doc['day']}.json", Body=json.dumps(doc).encode(), ContentType="application/json")
    c = doc["counts"]
    log(f"  call check {doc['day']}: AgencyZoom {c['agencyzoom']}, Pantheon {c['pantheon']}, matched {c['matched']} -- "
        f"{'agree' if doc['agree'] else str(c['only_agencyzoom_outbound']) + ' dials only in AgencyZoom, ' + str(c['only_pantheon_outbound']) + ' only in Pantheon'}")


def run(day, log=print):
    """The nightly's call, after crm_calls: never raises."""
    try:
        doc = build(day, log=log)
        if doc:
            publish(doc, log=log)
        return doc
    except (Exception, SystemExit) as e:
        log(f"  call check failed ({type(e).__name__}: {str(e)[:200]}) -- carrying on")
        return None


if __name__ == "__main__":
    a = sys.argv[1:]
    day = next((x for x in a if x[:4].isdigit()), staff.today())
    sqlite = a[a.index("--sqlite") + 1] if "--sqlite" in a else None
    doc = build(day, sqlite=sqlite)
    if not doc:
        sys.exit("nothing to compare")
    print(json.dumps({k: doc[k] for k in ("day", "agree", "counts", "per")}, indent=1))
    for k in ("only_agencyzoom", "only_pantheon"):
        print(f"{k}: {len(doc[k])}")
        for x in doc[k][:15]:
            print(f"   {x['at']}  {x['lead']} ({x['lead_id']})  {'dial' if x['outbound'] else 'call-in' if x['outbound'] is False else '?'}  {x['who']}")
    if "--publish" in a:
        publish(doc)
