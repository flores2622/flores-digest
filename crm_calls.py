"""Pantheon's own CALL notes, from the RingCentral call log (CRM.md phase 3;
Frank, 2026-10-14: "go").

AgencyZoom's integration writes a CALL note on a lead for every call; the
nightly mirrors those into the CRM. This writes the same note from the
RingCentral log the run already saved (data/rc_raw_<day>.json), so a lead's
call history in Pantheon no longer depends on AgencyZoom: every call a staff
member made to a number the lead corpus knows, and every call-in a producer
answered, on EVERY lead record on the number (az_corpus.phone_index),
as AgencyZoom's own note is and as lead_history reads them.

    python3 crm_calls.py 2026-10-13                 # print what would be written
    python3 crm_calls.py 2026-10-13 --write         # write it to the CRM (D1)
    python3 crm_calls.py 2026-10-13 --sqlite out/x.db --write

The note is AgencyZoom's own shape -- From / To / Call Status / Start Time /
End Time / Duration in the body, `attr.outbound` -- so live_contact,
messages.py and the lead page read it exactly like AgencyZoom's, with
`origin` "pantheon" and `attr.source` "ringcentral" to tell it apart, the
RingCentral record id in `attr.rcId`, and an id made from the lead and that
record id (crm_import.note_id), so a checkpoint and the nightly writing the
same call land on one row (INSERT OR IGNORE). The lead's own stamps are not
touched. Called after crm_sync at every checkpoint and by the nightly; never
raises. call_check.py compares what landed with AgencyZoom's notes.
"""
import datetime as dt
import json
import pathlib
import sys

import az_corpus
import crm_import
import crm_sync
import crm_tasks
import staff

ROOT = pathlib.Path(__file__).resolve().parent
ORIGIN = "pantheon"
SOURCE = "ringcentral"
BATCH = 80          # statements per D1 request
# RingCentral's result -> the status word AgencyZoom's own CALL note carries
# for a connected call ("completed", which live_contact reads); any other
# result keeps RingCentral's own word (Voicemail, No Answer, Hang Up ...),
# where AgencyZoom writes only "canceled".
STATUS = {"Call connected": "completed", "Accepted": "completed"}
BY_NAME = {p["name"]: p for p in staff.PEOPLE if p.get("az_id")}
# Everyone with a RingCentral extension (staff.json): az_id by RingCentral id.
BY_RC = {str(p["rc_id"]): p for p in staff.PEOPLE if p.get("rc_id") and p.get("az_id")}


def _local(iso):
    """A RingCentral stamp ('2026-10-14T00:22:04.124Z') on the agency's clock."""
    if not iso:
        return None
    try:
        t = dt.datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    except ValueError:
        return None
    return staff.local(t).replace(tzinfo=None)


def _status(result):
    return STATUS.get(result or "", result or "Unknown")


def _num(raw):
    """A number as AgencyZoom's own note writes it: (928) 726-3221 for a US
    number, anything else as RingCentral gave it."""
    d = "".join(c for c in str(raw or "") if c.isdigit())
    if len(d) == 11 and d[0] == "1":
        d = d[1:]
    return f"({d[:3]}) {d[3:6]}-{d[6:]}" if len(d) == 10 else str(raw or "")


def answerer(rec):
    """(staff person, seconds, route) for a call-in: the staff member on the
    longest connected pick-up leg -- inbound.attribute's rule, over everyone
    on staff rather than the producers alone (Debbie's and Amanda's answers
    get AgencyZoom's note too)."""
    import inbound
    best = None
    for l in rec.get("legs") or []:
        if l.get("result") != "Call connected":
            continue
        f = (l.get("from") or {}).get("name")
        if f not in BY_NAME or l.get("action") not in inbound.PICKUP_ACTIONS:
            continue
        if l.get("action") == "FindMe" and (l.get("to") or {}).get("name") != f:
            continue
        if best is None or (l.get("duration") or 0) > best[1]:
            best = (f, l.get("duration") or 0)
    if not best:
        return None, 0, None
    return BY_NAME[best[0]], best[1], None


def note_row(lead_id, rec, who, outbound, seconds=None, route=None):
    """One CALL note for `rec` on `lead_id`, by staff az_id `who`."""
    start = _local(rec.get("startTime"))
    secs = int(rec.get("duration") or 0)
    end = start + dt.timedelta(seconds=secs) if start else None
    frm = _num((rec.get("from") or {}).get("phoneNumber"))
    to = _num((rec.get("to") or {}).get("phoneNumber"))
    fmt = lambda t: t.strftime("%Y-%m-%d %H:%M:%S") if t else ""
    body = (f"From: {frm}<br>To: {to}<br>Call Status: {_status(rec.get('result'))}<br>"
            f"Start Time: {fmt(start)}<br>End Time: {fmt(end)}<br>Duration: {secs}(s)")
    attr = {"outbound": bool(outbound), "source": SOURCE, "rcId": rec.get("id"), "sessionId": rec.get("sessionId"),
            "result": rec.get("result"), "duration": secs, "from": frm, "to": to, "producer": who,
            "recording": bool(rec.get("recording"))}
    if seconds is not None:
        attr["producerSeconds"] = int(seconds)
    if route:
        attr["route"] = route
    return {
        "id": crm_import.note_id(lead_id, rec.get("id"), "CALL", SOURCE), "az_id": None, "lead_id": lead_id,
        "type": "CALL", "body": body, "attr": json.dumps(attr), "attachments": None,
        "origin": ORIGIN, "created_by": who, "create_date": fmt(start) or f"{staff.today()} 00:00:00",
    }


def rows_for(day, recs, leads=None, log=print):
    """Every CALL note the day's log gives: a dial by anyone on staff to a
    number the lead corpus knows, and a call-in someone on staff answered --
    on EVERY lead record on that number, as AgencyZoom's own note is (and as
    lead_history reads: duplicate records are pervasive). Returns
    (rows, skipped) -- skipped counts the calls no lead matched."""
    from rc_client import owner_ext_id
    leads = az_corpus.fetch() if leads is None else leads
    idx = az_corpus.phone_index(leads)
    rows, skipped = [], 0
    for r in recs:
        if r.get("type") not in (None, "Voice"):
            continue
        if r.get("direction") == "Outbound":
            p = BY_RC.get(owner_ext_id(r) or "")
            num = az_corpus.e164((r.get("to") or {}).get("phoneNumber"))
            secs = route = None
        elif r.get("direction") == "Inbound":
            p, secs, route = answerer(r)
            num = az_corpus.e164((r.get("from") or {}).get("phoneNumber"))
        else:
            continue
        if not p:
            continue
        cands = list({l["id"]: l for l in (idx.get(num, []) if num else []) if l.get("id")}.values())
        if not cands:
            skipped += 1
            continue
        for lead in cands:
            rows.append(note_row(lead["id"], r, p["az_id"], r.get("direction") == "Outbound", seconds=secs, route=route))
    return rows, skipped


def known_leads(db, ids):
    """Which of `ids` the CRM holds (a note on a lead it has not mirrored
    yet would be refused by the foreign key)."""
    out = set()
    ids = sorted({i for i in ids if i})
    for i in range(0, len(ids), 400):
        chunk = ids[i:i + 400]
        for r in db.query(f"SELECT id FROM leads WHERE id IN ({', '.join(str(x) for x in chunk)})"):
            out.add(r["id"])
    return out


def write(rows, db, log=print):
    """INSERT OR IGNORE every row, BATCH statements a request. Returns the
    number of statements sent (not the rows new to the table: D1 does not
    say which an IGNORE skipped)."""
    have = known_leads(db, [r["lead_id"] for r in rows])
    todo = [r for r in rows if r["lead_id"] in have]
    if len(todo) < len(rows):
        log(f"  crm calls: {len(rows) - len(todo)} notes wait for their lead to be mirrored")
    sent = 0
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        sql = "\n".join(crm_import.statement("notes", r, "ignore") for r in chunk)
        try:
            db.query(sql) if db.sqlite else db.d1.execute(sql)
            sent += len(chunk)
        except Exception as e:
            if crm_sync.REFUSED_ALL.search(str(e)):
                raise
            for r in chunk:
                try:
                    s = crm_import.statement("notes", r, "ignore")
                    db.query(s) if db.sqlite else db.d1.execute(s)
                    sent += 1
                except Exception as e1:
                    log(f"    refused note {r['id']} (lead {r['lead_id']}): {str(e1)[:120]}")
    return sent


def build(day, recs=None, leads=None, log=print):
    if recs is None:
        path = ROOT / f"data/rc_raw_{day}.json"
        if not path.exists():
            log(f"  crm calls: no data/rc_raw_{day}.json -- skipped")
            return None
        recs = json.loads(path.read_text())
    rows, skipped = rows_for(day, recs, leads=leads, log=log)
    calls = {json.loads(r["attr"])["rcId"]: json.loads(r["attr"])["outbound"] for r in rows}
    log(f"  crm calls {day}: {len(calls)} calls on leads ({sum(1 for v in calls.values() if v)} dialled, "
        f"{sum(1 for v in calls.values() if not v)} call-ins) -> {len(rows)} notes over their lead records; {skipped} calls with no lead")
    return rows


def run(day, log=print, sqlite=None, recs=None, leads=None):
    """The checkpoints' and the nightly's call, after crm_sync: never raises."""
    try:
        rows = build(day, recs=recs, leads=leads, log=log)
        if not rows:
            return 0
        db = crm_tasks.connect(sqlite, log=log)
        if db is None:
            return 0
        n = write(rows, db, log=log)
        log(f"  crm calls: {n} statements sent")
        return n
    except (Exception, SystemExit) as e:
        log(f"  crm calls failed ({type(e).__name__}: {str(e)[:200]}) -- carrying on")
        return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    day = next((x for x in a if x[:4].isdigit()), staff.today())
    sqlite = a[a.index("--sqlite") + 1] if "--sqlite" in a else None
    if "--write" in a:
        run(day, sqlite=sqlite)
    else:
        rows = build(day) or []
        for r in rows[:20]:
            at = json.loads(r["attr"])
            print(f"  {r['create_date']}  lead {r['lead_id']}  {'dial' if at['outbound'] else 'call-in'}  {at['result']}  {at['duration']}s  by {r['created_by']}")
        if len(rows) > 20:
            print(f"  ... {len(rows) - 20} more")
