"""Task Completion Audit -- GENERATED, one day at a time.

Until 2026-08-17 the four findings tables in the ops report were static HTML
baked into report_template.html. Only the date label was substituted, so every
ops email from 2026-08-12 onward carried the SAME two exceptions and the same
thirteen cancellations, and any real exception after 08-12 went unreported.
Frank, 2026-08-18: "i want a true daily audit not a repeat that does me no
good." This module is that audit.

The four questions, and what each can honestly be answered with:

  (a) Completed on the strength of a call that is not in the call log.
      The producer's own comment claims a call ("called", "left vm", "no
      answer"), the linked record has a phone, and RingCentral shows no dial
      to that number by that producer on the day. Scoped to numbers, so a call
      placed from a personal mobile legitimately shows up here.

  (b) Closed noticeably after the due date. completeDate > dueDate.

  (c) Due date changed. AgencyZoom exposes modifyDate/createDate but NOT
      field-level history, so a due-date edit cannot be proven. What is
      reported is the honest proxy: tasks modified on a later DAY than they
      were created, which is what a reschedule looks like. Labelled as such --
      never as a confirmed edit.

  (d) Cancelled rather than completed. status == 2, always counted against the
      completion rate (see az_tasks for the status semantics).
"""
import datetime as dt
import json
import re

import az_tasks
from az_corpus import e164
from digest_config import PRODUCERS

# The producer's comment asserting that a call happened.
CLAIMS_CALL = re.compile(
    r"\bcalled\b|\bcalling\b|\bcall(ed)? (back|him|her|them)\b|left ?(a )?(vm|voicemail|message)"
    r"|\blvm\b|\bl/m\b|no answer|didn'?t answer|did not answer|rang|reached out by phone"
    r"|spoke (with|to)|talked (with|to)|llam[eé]|habl[eé]", re.I)

# Comments that explicitly say the call could NOT be placed -- not an exception,
# the producer is telling us why there is no call.
EXPLAINS_NO_CALL = re.compile(
    r"no (phone|number)|bad number|not in service|no valid|wrong number"
    r"|number (does ?n'?t|not) (seem|work)|restricted|disconnected"
    r"|do not call|dnc|email(ed)? only|texted", re.I)


def _strip(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(html or ""))).strip()


def _phone_index(leads, customers):
    """record id -> (display name, [e164 phones])."""
    idx = {}
    for src in (leads, customers):
        for r in src:
            ph = [p for p in (e164(r.get("phone")), e164(r.get("secondaryPhone")))
                  if p]
            nm = (f"{(r.get('firstname') or r.get('firstName') or '').strip()} "
                  f"{(r.get('lastname') or r.get('lastName') or '').strip()}").strip()
            idx[r["id"]] = (nm or None, ph)
    return idx


ACTIVITY_LABEL = {"CALL": "call", "TEXT": "text", "EMAIL": "email",
                  "TEXT-FAILED": "text failed", "CONTACT": "contact"}
LOSS_RE = re.compile(r"Loss Reason:\s*([^|]+?)(?:\s+Comments:|$)", re.I)
MOVE_COMMENT_RE = re.compile(r"Comments:\s*(.+)$", re.S)


# Frank, 2026-08-25. Two rules for a task that was closed without being
# completed, both driven by what the producer actually did on the lead that day:
#
#   EXCLUDED  the lead was a duplicate. "If Jorge was a duplicate then that was a
#             duplicate task and therefore not a true task" -- it leaves the
#             audit entirely, the same way service work does.
#
#   EXCUSED   the producer moved the lead into Smart-Cycle or Dead that day, and
#             AgencyZoom's "cancel all related open tasks" checkbox is what
#             closed the task. They made the call and made a decision; the
#             cancellation is the CRM doing as it was told, not work left undone.
#             Covers both a real loss (Angel Inda: "my quote was coming up higher
#             at this time") and a cadence restart (David Garcia, smart-cycled to
#             re-enroll the automation for the next day -- the same reasoning as
#             the Recontact pause rule).
#
# Excused tasks come OUT of the completion-rate denominator but stay VISIBLE in
# audit section (d) with their verdict printed. Visibility is the guard against
# this being used to clear a task list, not a narrower rule.
LOSS_DUPLICATE_RE = re.compile(r"duplicate", re.I)
SMART_CYCLE_RE = re.compile(r"to\s+.{0,40}(smart-?cycle|\bdead\b)", re.I)


def cancellation_verdicts(day, tasks, az_ids):
    """{task_id: 'excluded'|'excused'} for closed-not-completed tasks."""
    import live_contact as lc
    out = {}
    for t in tasks:
        if t.get("status") != az_tasks.STATUS_CLOSED_NOT_COMPLETED:
            continue
        who = az_tasks.owner(t, az_ids)
        lid = t.get("customerId")
        if not who or not lid:
            continue
        dup = cycled = False
        for n in lc.load_notes(lid):
            if not str(n.get("createDate") or "").startswith(day):
                continue
            if n.get("type") != "MOVE_STAGE":
                continue
            body = lc._text(n.get("body")) or ""
            g = LOSS_RE.search(body)
            if g and LOSS_DUPLICATE_RE.search(g.group(1)):
                dup = True
            # The move has to be BY this producer -- someone else cycling the
            # lead is not this producer's decision.
            if SMART_CYCLE_RE.search(body) and who.split()[0].lower() in body.lower():
                cycled = True
        if dup:
            out[t["id"]] = "excluded"
        elif cycled:
            out[t["id"]] = "excused"
    return out


def day_activity(lead_id, day):
    """What AgencyZoom recorded on this lead that day, beyond the phone.

    The audit used to print "call on record: no" off the RingCentral log alone,
    which reads as "the producer did nothing". Frank, 2026-08-18: "they said no
    by text or email, theres notes." A cancelled task with a texted reply IS a
    worked lead, so the audit has to say so.
    """
    import live_contact as lc
    kinds, inbound, loss, moved = [], [], None, None
    for n in lc.load_notes(lead_id):
        if not str(n.get("createDate") or "").startswith(day):
            continue
        typ = n.get("type")
        if typ == "MOVE_STAGE":
            body = lc._text(n.get("body")) or ""
            g = LOSS_RE.search(body)
            if g:
                loss = g.group(1).strip()
            # The producer's own words on the move say more than the canned
            # task text ever will -- Larry Pihlman, "Should have been
            # smartcycled last week".
            c = MOVE_COMMENT_RE.search(body)
            if c:
                moved = re.sub(r"\s+", " ", c.group(1)).strip()
        label = ACTIVITY_LABEL.get(typ)
        if not label:
            continue
        if label not in kinds:
            kinds.append(label)
        # A note with no author is the lead replying, not the producer.
        if not (n.get("createdBy") or "").strip():
            txt = _strip(n.get("body"))
            if txt and txt not in inbound:
                inbound.append(txt)
    return {"kinds": kinds, "inbound": inbound, "loss_reason": loss,
            "move_comment": moved}


def _link(task, leads_ids):
    """(kind, id) for an AgencyZoom deep link -- corpus membership decides,
    because customerType is wrong on a small number of rows."""
    cid = task.get("customerId")
    if not cid:
        return None, None
    return ("lead" if cid in leads_ids else "customer"), cid


def build(day, tasks, dials_by_producer, leads, customers, verdicts=None):
    az_ids = {v["az_id"]: k for k, v in PRODUCERS.items()}
    idx = _phone_index(leads, customers)
    lead_ids = {l["id"] for l in leads}
    dialled = {who: set(bynum) for who, bynum in dials_by_producer.items()}

    verdicts = verdicts or {}
    counted = [t for t in tasks
               if not az_tasks.service_reason(t) and az_tasks.owner(t, az_ids)
               and verdicts.get(t.get("id")) != "excluded"]

    a, b, c, d, e = [], [], [], [], []
    for t in counted:
        who = az_tasks.owner(t, az_ids)
        todo = t.get("agencyTodo") or {}
        comment = _strip(t.get("comments") or todo.get("comments"))
        kind, rid = _link(t, lead_ids)
        name, phones = idx.get(t.get("customerId"), (None, []))
        name = name or t.get("customerName")
        row = {"producer": who, "title": t.get("title"), "task_id": t.get("id"),
               "record": name, "link_kind": kind, "link_id": rid,
               "comment": comment, "phones": phones}

        # (a) claims a call, has a number, but the number was never dialled
        if (t.get("status") == az_tasks.STATUS_COMPLETED
                and CLAIMS_CALL.search(comment)
                and not EXPLAINS_NO_CALL.search(comment)
                and phones
                and not any(p in dialled.get(who, ()) for p in phones)):
            a.append({**row, "number": phones[0]})

        # (b) completed after the due date
        cd, dd = str(t.get("completeDate") or "")[:10], str(t.get("dueDate") or "")[:10]
        if cd and dd and cd > dd:
            days = (dt.date.fromisoformat(cd) - dt.date.fromisoformat(dd)).days
            b.append({**row, "due": dd, "completed": cd, "days_late": days})

        # (c) modified on a later day than created -- reschedule-shaped
        cr, md = str(todo.get("createDate") or "")[:19], str(todo.get("modifyDate") or "")[:19]
        if cr and md and md[:10] > cr[:10]:
            c.append({**row, "created": cr, "modified": md, "due": dd})

        # (e) never closed out at all -- still status 0 when the day ended.
        # Distinct from (d): nobody decided anything about these, they were just
        # left. Both count against the completion rate (Frank, 2026-08-25).
        if t.get("status") == az_tasks.STATUS_OPEN:
            e.append({**row, "due": dd})

        # (d) cancelled rather than completed
        if t.get("status") == az_tasks.STATUS_CLOSED_NOT_COMPLETED:
            act = day_activity(t.get("customerId"), day) if rid else {
                "kinds": [], "inbound": [], "loss_reason": None,
                "move_comment": None}
            called = bool(phones) and any(p in dialled.get(who, ()) for p in phones)
            d.append({**row,
                      "verdict": verdicts.get(t.get("id")),
                      "call_on_record": ("no number" if not phones else
                                         ("yes" if called else "no")),
                      "activity": act["kinds"],
                      "inbound": act["inbound"],
                      "loss_reason": act["loss_reason"],
                      "move_comment": act.get("move_comment")})

    for lst, key in ((a, "producer"), (b, "days_late"), (c, "producer"),
                     (d, "producer"), (e, "producer")):
        lst.sort(key=lambda r: (str(r.get(key)), str(r.get("producer"))),
                 reverse=(key == "days_late"))
    return {"counted": len(counted), "a": a, "b": b, "c": c, "d": d, "e": e}


if __name__ == "__main__":
    import sys
    import day_calls
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-08-17"
    r = build(day, json.load(open(f"data/az_tasks_{day}.json")),
              day_calls.producer_dials(day),
              json.load(open("data/az_leads_all.json")),
              json.load(open("data/az_customers_all.json")))
    print(f"{r['counted']} counted tasks")
    for k in "abcd":
        print(f"  ({k}) {len(r[k])} found")
        for row in r[k][:6]:
            print(f"       {row['producer']:16} {str(row['record'])[:24]:26} "
                  f"{str(row['title'])[:36]}")
