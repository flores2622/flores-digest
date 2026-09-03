"""Create the missed-call tasks in AgencyZoom.

    python3 missed_call_tasks.py                 # DRY RUN, prints what it would do
    python3 missed_call_tasks.py --live          # actually creates them
    python3 missed_call_tasks.py --live --day 2026-09-01

The write half. `missed_call_audit.py` decides WHO and WHERE -- this one does
it. Rules are HOURLY_RUNS.md sections 1-6 and are settled; do not re-derive them
here.

**IT DOES NOTHING WITHOUT --live.** A dry run prints the exact payloads so a
change can be read before it touches anybody's queue.

WHEN THIS RUNS. Once a day, inside the 5:35 PM build, not hourly. The hourly
schedule does not exist -- scheduled runs get a cold container and cannot push,
so it was abandoned on 2026-09-01 (HOURLY_RUNS.md s12). It costs nothing here:
the tasks are due the next morning anyway, and by 5:35 the phones are off, so a
single end-of-day pass creates exactly the same tasks the ten hourly runs would
have, minus the ones people had already handled -- which is the point.

IDEMPOTENCY. Re-running must not double up. Before creating, it reads the
existing tasks on that record and skips any whose title already matches. For
Debbie's standalone tasks there is no record to read, so the day's already-open
missed-call tasks are pulled once and matched on title.
"""
import argparse
import datetime as dt
import json
import pathlib
import re

import missed_call_audit as audit

ROOT = pathlib.Path(__file__).resolve().parent
AZ = dt.timezone(dt.timedelta(hours=-7))
log = audit.log

# From GET /v1/api/employees, 2026-09-01. Only the people in the routing.
EMPLOYEE = {
    "Debbie": 83597, "Crystal": 174445, "Lorena": 82587, "Sarahi": 185441,
    "Amanda": 105006, "Coral": 185440, "Mike": 82588, "Frank": 82589,
    "Adrian": 82590, "Francisco": 82372,
}
FALLBACK = EMPLOYEE["Debbie"]

# NO SERVICE REQUEST IS OPENED. Frank, 2026-09-02: "make it a plain task for
# amanda and let her figure out what to do with it."
#
# Two reasons it went this way. Most of these callers turn out to need nothing,
# so pre-opening ~11 tickets a day fills the pipeline with tickets closed
# unread. And the API cannot tie a task to a service ticket anyway -- probed
# 2026-09-02, seven variants across create and update, all returning success and
# all leaving serviceTicketId null -- so the pair arrived unlinked.
#
# There was also a real bug in doing it: the SR payload carried no `csr`, so
# AgencyZoom picked one. Yvonne Meza's landed on Mike while the task sat with
# Amanda. If SR creation ever comes back, SEND THE CSR EXPLICITLY.
#
# Reference values, kept because they were expensive to work out:
#   workflowId 23074 Service Pipeline, workflowStageId 78844 New,
#   categoryId 25617 "General", priorityId 24501 normal, csr = the assignee.

TITLE = "Missed Call from {who}"

BODY_TAIL = (
    "<li>if contact has already been made, complete this task</li>"
    "<li>if you know why {noun} is calling and you are working on it, let them "
    "know via phone/text</li>"
    "<li>before you complete this, check that the number they called from, "
    "their email and their address are on {record} in AgencyZoom. Fix anything "
    "missing or wrong</li>")

BODIES = {
    "open lead": (
        "<p>Attempt to contact this lead</p><ul>"
        "<li>if they don't answer, leave a voicemail and send a text. Complete "
        "this task as long as the lead is open with automation on</li>"
        + BODY_TAIL.format(noun="the lead", record="the lead")),
    "open SR": (
        "<p>Attempt to contact this customer</p><ul>"
        "<li>if they don't answer, leave a voicemail and send a text. Complete "
        "this task as long as the service request is open with automation on</li>"
        + BODY_TAIL.format(noun="the customer", record="the customer record")),
    "customer": (
        "<p>Attempt to contact this customer</p><ul>"
        "<li>if they don't answer, leave a voicemail and send a text</li>"
        "<li>if it turns out to need service work, open a service request and "
        "let the automation take it from there</li>"
        + BODY_TAIL.format(noun="the customer", record="the customer record")),
    "closed lead": (
        "<p>Attempt to contact this caller &mdash; their lead is closed and "
        "they are not a customer on this number</p><ul>"
        "<li>if they don't answer, leave a voicemail and send a text</li>"
        "<li>if contact has already been made, complete this task</li>"
        "<li>once you know why they are calling, delegate it: open a new lead "
        "and assign a producer if they are shopping, or open a service request "
        "if it is service</li>"
        "<li>before you complete this, check that the number they called from, "
        "their email and their address are on the record in AgencyZoom. Fix "
        "anything missing or wrong</li></ul>"),
    "no record": (
        "<p>Attempt to contact this caller &mdash; we have no record for this "
        "number</p><ul>"
        "<li>if they don't answer, leave a voicemail and send a text</li>"
        "<li>if contact has already been made, complete this task</li>"
        "<li>if you know why they are calling and you are working on it, let "
        "them know via phone/text</li>"
        "<li>before you complete this, get this number onto a record. If they "
        "turn out to be an existing customer or lead on another number, add it "
        "there and check Apex; if they are shopping, create a lead. Nothing "
        "else will do this, and until it happens the same number generates a "
        "fresh task every time it rings</li>"
        "<li>nothing will follow up automatically on this one. There is no lead "
        "and no service request behind it, so do not complete it until you have "
        "either reached them or left both a voicemail and a text</li></ul>"),
}
for k in ("open lead", "open SR", "customer"):
    BODIES[k] += "</ul>"


def meta_line(r):
    when = (f"{r['first']:%-I:%M %p}" if r["rings"] == 1
            else f"{r['first']:%-I:%M}–{r['last']:%-I:%M %p}")
    bits = [audit.pretty(r["number"])]
    bits.append(when if r["rings"] == 1 else f"called {r['rings']}× {when}")
    if r["vm"]:
        bits.append("left voicemail")
    line = " &middot; ".join(bits)
    if r["cnam"]:
        cnam = re.sub(r"\s+", " ", r["cnam"]).strip()
        line += f"<br>caller ID: {cnam}"
    return f"<p>{line}</p>"


def title_for(r):
    """Name if we have a real one, otherwise the number.

    For the no-record bucket the only "name" is carrier caller ID -- often a
    surname in caps, sometimes just a city, and never authoritative. It belongs
    on the meta line, not in the title, so Debbie is not chasing "Greenwood De".
    """
    who = r["name"] if r["bucket"] != "no record" else None
    return TITLE.format(who=who or audit.pretty(r["number"]))


def already_there(azc, r, day):
    """Has a task with this title already been made for this caller?"""
    rec = r.get("record_id")
    if not rec:
        return r["number"] in _standalone_titles(azc, day)
    try:
        j = azc.get(f"/v1/api/customers/{rec}/tasks")
    except Exception:
        return False
    # A record with no tasks comes back as JSON null, not [] or {} -- seen
    # 2026-09-02, where it killed the run after the first caller and left 10
    # of 11 missed-call tasks uncreated. Anything that is not a list or a dict
    # means "no tasks on this record", which is exactly "not already there".
    if isinstance(j, list):
        rows = j
    elif isinstance(j, dict):
        rows = j.get("data") or j.get("tasks") or []
    else:
        rows = []
    want = title_for(r)
    return any((t.get("title") or "").strip() == want
               for t in rows if isinstance(t, dict))


_STANDALONE = None


def _standalone_titles(azc, day):
    """Titles of missed-call tasks already open, for the no-record bucket.

    Those tasks hang off no record, so there is nothing to query per caller.
    One pass over the day's tasks is enough, and the phone number is in the
    title whenever we had no name.
    """
    global _STANDALONE
    if _STANDALONE is None:
        _STANDALONE = set()
        try:
            for t in azc.tasks(day, day):
                title = (t.get("title") or "")
                if title.startswith("Missed Call from"):
                    for n in re.findall(r"\d", title):
                        pass
                    digits = re.sub(r"\D", "", title)
                    if len(digits) >= 10:
                        _STANDALONE.add(digits[-10:])
        except Exception as e:
            log(f"  could not read today's tasks ({e}); "
                f"skipping the duplicate check for standalone tasks")
    return _STANDALONE


def create(azc, r, live):
    body = {"title": title_for(r),
            "comments": meta_line(r) + BODIES[r["bucket"]],
            "type": "call",
            "assigneeId": EMPLOYEE.get(r["who"], FALLBACK)}
    if r.get("record_id"):
        body["customerId"] = r["record_id"]
        body["customerType"] = r["record_type"]
    if not live:
        where = (f"on {r['record_type']} {r['record_id']}"
                 if r.get("record_id") else "standalone")
        log(f"    would create: {body['title']} -> {r['who']} ({where})")
        return None
    j = azc.post("/v1/api/tasks", body) or {}
    return j.get("id")


def enrich(rows, day):
    """Attach the AgencyZoom record each task hangs off."""
    idx, *_ = audit.build_index(day)
    for r in rows:
        hit = idx.get(r["number"]) or {}
        r["record_id"], r["record_type"] = None, None
        if r["bucket"] == "open lead":
            open_leads = [l for l in hit.get("lead", []) if l.get("status") == 0]
            if open_leads:
                r["record_id"], r["record_type"] = open_leads[0]["id"], "lead"
        elif r["bucket"] in ("open SR", "customer"):
            if hit.get("cust"):
                r["record_id"], r["record_type"] = hit["cust"][0]["id"], "customer"
        elif r["bucket"] == "closed lead":
            if hit.get("lead"):
                r["record_id"], r["record_type"] = hit["lead"][0]["id"], "lead"
    return rows


def run(day, live=False):
    from az_client import AgencyZoom
    azc = AgencyZoom()
    rows = enrich(audit.build(day, refresh=False), day)
    todo = [r for r in rows if r["back_in"] is None]
    log(f"{len(rows)} missed callers, {len(rows) - len(todo)} already reached, "
        f"{len(todo)} need a task")
    made, skipped, failed = [], [], []
    for r in todo:
        who = r["name"] or audit.pretty(r["number"])
        if already_there(azc, r, day):
            skipped.append(who)
            log(f"  skip {who} -- a task already exists")
            continue
        log(f"  {who} -> {r['who']} ({r['bucket']})")
        try:
            tid = create(azc, r, live)
        except Exception as e:
            # One record AgencyZoom rejects must not abandon the rest of the
            # batch. Seen 2026-09-02: POST /v1/api/tasks answers 400 {"error":
            # "The customer is not found"} for every LEAD-bucket caller,
            # because customerId is sent a lead id. The lead contract is not
            # known, so these are reported for manual handling rather than
            # guessed at -- but the customer and standalone tasks still land.
            failed.append((who, r["who"], r.get("record_type"), str(e)[:120]))
            log(f"    FAILED ({r.get('record_type') or 'standalone'}): {e}")
            continue
        if live:
            log(f"    task {tid}")
        made.append((who, r["who"], tid))
    log(f"{'CREATED' if live else 'WOULD CREATE'} {len(made)} tasks, "
        f"skipped {len(skipped)} already there"
        + (f", {len(failed)} FAILED" if failed else ""))
    for who, assignee, kind, err in failed:
        log(f"  STILL NEEDS A TASK BY HAND: {who} -> {assignee} ({kind}): {err}")
    return made, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", default=None)
    ap.add_argument("--live", action="store_true",
                    help="actually create the tasks; without it nothing is written")
    a = ap.parse_args()
    day = a.day or dt.datetime.now(AZ).date().isoformat()
    if not a.live:
        log("DRY RUN -- nothing will be created. Pass --live to write.")
    run(day, live=a.live)


if __name__ == "__main__":
    main()
