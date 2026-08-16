"""Recontact Struggle -- momentum lost AFTER a real conversation (Frank).

  At risk of going cold : in a post-contact stage, more than 3 business days
                          since the last stage move OR more than 3 dials since
                          entering it, no outcome yet, stage entered within 30 days.
  Lost                  : moved to Dead or Smart-Cycle on the day.
  Won                   : sold on the day.
  "Most critical"       : the MOST RECENTLY CONTACTED -- those leads are still warm.

STAGE ENTRY DATE. Preferred source is the MOVE_STAGE note into that stage
("exact"). A lead is created into New and AgencyZoom writes no move note for
that, so early-funnel stages fall back to the lead's creation date ("from lead
creation"). NEVER use enterStageDate: AgencyZoom overwrites it when it moves a
lead to Smart-Cycle, so it reads as the outcome date -- trusting it collapsed
every window to zero days and hid every call on the lead (HANDOFF_4 s5).

A "recycled back from Smart-Cycle" move is a move OUT of the cycle and is NOT a
dead outcome. Moves into the junk "Pipeline" workflow (vendor integration error)
are ignored entirely.
"""
import datetime as dt
import json
import re

import live_contact as lc
from az_corpus import e164
from digest_config import JUNK_WORKFLOW_NAME, PRODUCERS, TRAINING_LEAD_OWNERS

POST_CONTACT = re.compile(
    r'quoted|quotes presented|contacted|fsd|pending bind|lender referral', re.I)
DEAD = re.compile(r'\bdead\b|smart[- ]cycle', re.I)
AT_RISK_BD = 3
AT_RISK_DIALS = 3
MAX_STAGE_AGE = 30


def business_days(a, b):
    d, n = a, 0
    while d < b:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def stage_history(lead_id):
    """[(datetime, from_stage, to_stage, comment, who)] oldest first."""
    out = []
    for n in lc.load_notes(lead_id):
        if n.get("type") != "MOVE_STAGE":
            continue
        text = lc._text(n.get("body"))
        move, comment = lc._move_stage_parts(text)
        frm, _, to = move.partition(" to ")
        to = to.split(" by ")[0].strip()
        frm = frm.strip()
        # Vendor integration error: ignore moves INTO the junk pipeline; a move
        # OUT of it says nothing about where the lead really was.
        if to.strip().startswith(JUNK_WORKFLOW_NAME + " |"):
            continue
        try:
            when = dt.datetime.fromisoformat(str(n["createDate"]).replace(" ", "T"))
        except Exception:
            continue
        out.append((when, frm, to, comment, n.get("createdBy")))
    return sorted(out, key=lambda r: r[0])


def entered_stage(lead, hist, current_stage):
    """(date, basis) for when the lead entered its current stage."""
    tail = current_stage.split("|")[-1].strip().casefold()
    for when, _frm, to, _c, _w in reversed(hist):
        if to.split("|")[-1].strip().casefold() == tail:
            return when.date(), "exact"
    cd = str(lead.get("createDate") or "")[:10]
    try:
        return dt.date.fromisoformat(cd), "from lead creation"
    except Exception:
        return None, "unknown"


def dials_between(dials_by_number, lead, start, end):
    p = e164(lead.get("phone")) or e164(lead.get("secondaryPhone"))
    if not p:
        return 0, None
    calls = dials_by_number.get(p, [])
    n, last = 0, None
    for c in calls:
        d = dt.datetime.fromisoformat(c["startTime"].replace("Z", "+00:00")).date()
        if start and d < start:
            continue
        if end and d > end:
            continue
        n += 1
        last = d if last is None or d > last else last
    return n, last


def build(day, leads, stage_map, dials_by_producer):
    az_ids = {v["az_id"]: k for k, v in PRODUCERS.items()}
    today = dt.date.fromisoformat(day)
    at_risk, lost, won = [], [], []

    per_number = {}
    for who, bynum in dials_by_producer.items():
        per_number[who] = bynum

    for lead in leads:
        who = az_ids.get(lead.get("assignedTo"))
        if not who or lead.get("assignedTo") in TRAINING_LEAD_OWNERS:
            continue
        last_act = str(lead.get("lastActivityDate") or "")[:10]
        hist = None

        # ---- Won ----------------------------------------------------------
        if str(lead.get("soldDate") or "").startswith(day):
            won.append({"producer": who, "lead": lead, "stage": "Sold",
                        "entered": None, "outcome_date": day})
            continue

        # ---- Lost: a move to Dead / Smart-Cycle on the day -----------------
        if last_act == day:
            hist = stage_history(lead["id"])
            todays = [h for h in hist if h[0].date() == today and DEAD.search(h[2])]
            if todays:
                when, frm, to, comment, _ = todays[-1]
                ent, basis = entered_stage(lead, [h for h in hist if h[0] < when],
                                           frm or "New")
                n, _ = dials_between(per_number.get(who, {}), lead, ent, today)
                lost.append({"producer": who, "lead": lead,
                             "stage": frm or "New", "entered": ent,
                             "entered_basis": basis, "outcome": to,
                             "outcome_date": day, "calls": n,
                             "days": (today - ent).days if ent else None,
                             "comment": comment})
                continue

        # ---- At risk -------------------------------------------------------
        if lead.get("status") != 0:
            continue
        stage = stage_map.get(lead.get("workflowStageId"), "")
        if not stage or not POST_CONTACT.search(stage.split("|")[-1]):
            continue
        if hist is None:
            hist = stage_history(lead["id"])
        ent, basis = entered_stage(lead, hist, stage)
        if not ent or (today - ent).days > MAX_STAGE_AGE:
            continue
        bd = business_days(ent, today)
        n, last_dial = dials_between(per_number.get(who, {}), lead, ent, today)
        stalled, overdialled = bd > AT_RISK_BD, n > AT_RISK_DIALS
        if not (stalled or overdialled):
            continue
        at_risk.append({"producer": who, "lead": lead,
                        "stage": stage.split("|")[-1].strip(),
                        "entered": ent, "entered_basis": basis,
                        "business_days": bd, "calls": n, "last_dial": last_dial,
                        "flag": "both" if stalled and overdialled
                                else ("stalled" if stalled else "over-dialled")})

    # "Most critical" is the most recently contacted -- still warm.
    at_risk.sort(key=lambda r: (r["last_dial"] or dt.date.min), reverse=True)
    lost.sort(key=lambda r: -(r["calls"] or 0))
    return {"at_risk": at_risk, "lost": lost, "won": won}
