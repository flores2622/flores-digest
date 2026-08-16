"""Decide which dialled numbers were real conversations.

LIVE CONTACT IS NOT A DURATION RULE (Notes & Methodology, Aug 12):
"a 28-second call can be a live contact while a longer one is a voicemail."
It comes from producer-written AgencyZoom notes cross-referenced to the call
log. Duration is only a last-resort fallback, and the report labels those rows
"duration only" so the reader knows the difference.

Note shapes on a lead (all datetimes ARIZONA-LOCAL, unlike lead/task records):
  type "CALL"        auto-written by the RingCentral integration. Body carries
                     From/To/Call Status/Duration. Evidence a call happened,
                     NOT evidence anyone picked up.
  type null          free-text the producer typed. This is the real signal.
  type "comment"     same.
  type "MOVE_STAGE"  stage change; a "Comments:" block often carries the outcome
                     in the producer's own words ("never answered", "Quoted over
                     the phone, $400 was too high").
  everything else    automation, tags, texts, emails, task churn -- noise here.
"""
import html
import json
import pathlib
import re

NOTE_DIR = pathlib.Path("data/notes")

# Producer text that means nobody was reached.
NEGATIVE = re.compile(
    r"never answered|no answer|no ans\b|didn'?t answer|left ?vm|left a? ?message"
    r"|voice ?mail|\bvm\b|\blm\b|no machine|disconnected|not in service"
    r"|bad number|number might be bad|wrong number|busy signal|line busy"
    r"|no longer in service|mailbox (is )?full",
    re.I)

# System-generated free text that is not a producer outcome.
SYSTEM = re.compile(
    r"^lead created$|lead source changed|unenroll|enroll(ed)? (from|in|to)"
    r"|automatically unenroll|automation|expiry date|tag added|assigned to"
    r"|^moved to|reassign",
    re.I)

MEANINGFUL_TYPES = {None, "", "comment", "MOVE_STAGE", "Sold"}

# If a call actually connected, it counts (Frank, 2026-08-14). A producer who
# held a real conversation and simply did not write it up still made contact.
#
# The floor separates a conversation from a ring-out or a voicemail drop, and it
# is set from the data rather than picked: across the day's dials, notes that
# explicitly say no-answer / voicemail cluster below a minute --
#
#     talk time   explicit no-contact notes
#      1-14s                5
#     15-29s                5
#     30-59s                4
#     60-119s               1
#       120s+               0
#
# so 60 seconds of connected audio is where "nobody picked up" stops being a
# plausible explanation. Talk time is the longer of AgencyZoom's own CALL-note
# duration and the RingCentral leg.
#
# An explicit no-contact note always wins over duration -- if the producer wrote
# "never answered", that is the answer regardless of how long the leg ran.
# Rows that qualify on duration alone are labelled "duration only" in Call
# Detail so the weaker evidence is visible.
DURATION_FALLBACK_SECONDS = 60


def _text(body):
    body = re.sub(r"<audio.*?</audio>", " ", body or "", flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    return re.sub(r"\s+", " ", html.unescape(body)).strip()


def _move_stage_parts(text):
    """('1 Pipeline | New to Smart-Cycle', 'never answered')"""
    comment = ""
    m = re.search(r"Comments:\s*(.+)$", text)
    if m:
        comment = m.group(1).strip()
        text = text.split(" Comments:")[0]
    move = re.sub(r"^Lead .*? moved from ", "", text).strip()
    return move, comment


def load_notes(lead_id):
    f = NOTE_DIR / f"{lead_id}.json"
    return json.loads(f.read_text()) if f.exists() else []


def evidence(lead_id, day, producer):
    """Everything the producer wrote on this lead on this Arizona day."""
    out = {"written": [], "stage_moves": [], "call_notes": [], "negative": False}
    for n in load_notes(lead_id):
        if not str(n.get("createDate") or "").startswith(day):
            continue
        if n.get("createdBy") != producer:
            continue
        t = n.get("type")
        body = _text(n.get("body"))
        if t == "CALL":
            d = re.search(r"Duration:\s*(\d+)", body)
            out["call_notes"].append({"seconds": int(d.group(1)) if d else 0,
                                      "status": "completed" in body.lower()})
            continue
        if t not in MEANINGFUL_TYPES:
            continue
        if t == "MOVE_STAGE":
            move, comment = _move_stage_parts(body)
            out["stage_moves"].append({"move": move, "comment": comment})
            if comment and not SYSTEM.search(comment):
                if NEGATIVE.search(comment):
                    out["negative"] = True
                else:
                    out["written"].append(comment)
            continue
        if not body or SYSTEM.search(body):
            continue
        if NEGATIVE.search(body):
            out["negative"] = True
        else:
            out["written"].append(body)
    return out


def is_live(ev, talk_seconds=None, transcript_class=None):
    """(bool, basis) -- basis is what the report prints for the row.

    ORDER OF EVIDENCE. The recording wins, because it is the only source that
    actually knows what happened. On 2026-08-13 the transcripts split 135
    recorded calls into 86 voicemails and 49 live -- including a 77-second
    voicemail greeting and a 2-second human pickup, which no duration rule and
    no note could have separated.

    Producer notes come second: they cover calls with no recording, and a
    producer writing "never answered" outranks silence.

    Duration is LAST and only where there is neither a recording nor a note. It
    is a poor signal in both directions and is labelled as such in Call Detail.
    """
    if transcript_class == "live":
        return True, "recording"
    if transcript_class in ("voicemail", "no answer"):
        return False, f"recording ({transcript_class})"
    if ev["written"]:
        return True, "producer note"
    if ev["negative"]:
        return False, "producer note (no contact)"
    longest = max([c["seconds"] for c in ev["call_notes"]] + [talk_seconds or 0])
    if longest >= DURATION_FALLBACK_SECONDS:
        return True, "duration only"
    return False, "no outcome logged"


def outcome_bucket(ev, live):
    """Call Outcome Breakdown segment."""
    if live:
        return "Live Contact"
    joined = " ".join(m["comment"] for m in ev["stage_moves"]) + " "
    if re.search(r"voice ?mail|left ?vm|\bvm\b|left a? ?message|\blm\b", joined, re.I):
        return "Voicemail"
    if re.search(r"screener|gatekeeper|receptionist", joined, re.I):
        return "Screener"
    if ev["negative"]:
        return "No Answer"
    return "No Outcome Logged"
