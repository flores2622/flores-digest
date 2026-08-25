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
import datetime as dt
import re

NOTE_DIR = pathlib.Path("data/notes")

# Producer text that means nobody was reached.
NEGATIVE = re.compile(
    # Original list.
    r"never answered|no answer|no ans\b|didn'?t answer|left ?vm|left a? ?message"
    r"|voice ?mail|\bvm\b|\blm\b|no machine|disconnected|not in service"
    r"|bad number|number might be bad|wrong number|busy signal|line busy"
    r"|no longer in service|mailbox (is )?full"
    # Frank walked the 2026-08-17 Call Detail and found rows that were plainly
    # not contacts. Every one of them was a producer note whose text SAYS no
    # one was reached, but which this pattern did not recognise, so the
    # "any note means live" rule scored it as a contact:
    #   Edward Federico  "did not respond to my calls"
    #   Arturo Morales   "got a message saying call was restricted"
    #   John Doe         "phone and email are not good"
    r"|did ?n'?o?t respond|no response|didn'?t pick|did not pick|no pick ?up"
    r"|unable to (reach|connect|contact)|could ?n'?o?t (reach|connect|get)"
    r"|un(able|reachable)|no contact|never (reached|connected|picked)"
    r"|call (was )?restricted|restricted (call|number)|call could not be"
    r"|(phone|number|email)s? (and \w+ )?(are|is|was|were) not good"
    # "Number does not seem to be in service" -- the old pattern needed the
    # exact phrase "not in service" and this misses it by three words.
    r"|(does|did|do)\s*n[o']?o?t\s+(seem|appear|work|go through|connect)"
    r"|to be in service|out of service"
    r"|not a good (number|phone)|no valid (number|phone)"
    r"|tried calling|keep getting|kept getting|straight to"
    r"|ghosted|no callback|has not called back|hasn'?t called back"
    # Frank, 2026-08-25 on Juan Avila: "not a live contact". 21 seconds, no
    # recording, note read "Juan stopped responding to me." The pattern already
    # had "did not respond" and "no response" but not the stopped/quit form.
    # Frank, 2026-08-25 on Diego Rodriguez: "theres a note that says 'Called No
    # Anwer'". The task note read exactly that -- answer misspelled by one
    # letter -- so "no answer", "no ans\b" and "didn't answer" all missed it and
    # the call scored as a live contact off the OTHER note on the lead. Anchored
    # to a negating word so a bare "she answered" (which IS contact) is untouched,
    # and the 3rd letter must be s or w so "no another"/"no anchor" do not match.
    r"|(?:\bno|\bnever|\bdid ?n'?o?t|\bdoes ?n'?o?t)\s+an[sw]\w{0,3}r(ed)?\b"
    r"|stopped (respond|answer|reply|return)\w*|quit (respond|answer)\w*"
    r"|no longer respond\w*"
    # Could not leave one at all -- invisible to every system until now.
    r"|could ?n'?o?t leave (a )?(vm|voicemail|message)"
    r"|un(able|available) to leave (a )?(vm|voicemail|message)"
    # An AI attendant, a screener or a dropped transfer is not a conversation
    # with the prospect. Frank, 2026-08-18 on Elsa Aguilera: "call dropped
    # after AI transferred me ... that was a call screener".
    r"|call dropped|dropped (the )?call|got dropped|dropped after"
    r"|ai transfer|transferred me|auto ?attendant|phone tree|\bivr\b"
    r"|screener|gatekeeper|receptionist|never got (through|past)"
    # Spanish.
    r"|no contest[oó]|no contesta|no responde|no respondi[oó]"
    r"|buz[oó]n|n[uú]mero (malo|equivocado)",
    re.I)

# Policy facts the producer looks up WHILE DIALLING -- carrier, premium,
# renewal date -- pulled off the Progressive/carrier report with the phone
# still ringing. It reads like a producer note and is not an outcome at all.
# Frank, 2026-08-18: "the progressive note is deceiving ... he pulls that info
# up while the phone is ringing." Treated as neither positive nor negative:
# a genuine conversation of any length also leaves a recording, which still
# decides the row.
DATA_ONLY = re.compile(
    r"renewal is|\bpays?\b|\bpremium\b|x-?date|expires?|policy ?number"
    r"|\bcurrently (with|insured)\b|\$\s?[\d,]+", re.I)

# Something a person said or did -- what separates an outcome from a data dump.
CONTACT_VERB = re.compile(
    r"\b(spoke|speaking|talked|answered|hung up|said|told|asked|mentioned"
    r"|wants?|interested|declined|refused|agreed|scheduled|appointment"
    r"|discussed|explained|reviewed|confirmed|call(ed)? (back|him|her|them)"
    r"|will call|going to|follow ?up with|quoted (him|her|them))\b", re.I)


SCREENER = re.compile(
    r"screener|gatekeeper|receptionist|ai transfer|transferred me"
    r"|call dropped|dropped after|auto ?attendant|phone tree|\bivr\b"
    # What a call-screening service says. Elsa Aguilera's recording: "if you
    # record your name and reason for calling, I'll see if this person is
    # available" -- a screener, though it reads as a machine greeting.
    r"|reason for calling|see if (this|the) person is available"
    r"|who('?s| is) calling( please)?|may i (ask )?who|screening (this |your )?call", re.I)


def is_data_capture(text):
    """Carrier facts with nobody in them."""
    t = (text or "").strip()
    return bool(t) and bool(DATA_ONLY.search(t)) and not CONTACT_VERB.search(t)


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


# ---- TASK notes -------------------------------------------------------------
# The producers' real outcome write-ups live on TASK notes, and NONE of them
# reached this module until 2026-08-18. Two reasons, both silent:
#   1. Every TASK note is stamped exactly 17:00:00 -- Arizona 5pm, which is
#      00:00 UTC of the day the task is DUE. So Aug 17's tasks carry a
#      createDate of 2026-08-16 and the day filter dropped all of them.
#   2. createdBy is null on all 1,724 of them, so the producer filter dropped
#      whatever survived. Authorship is in the body: "Completed by <Name>".
# Frank, 2026-08-18: "on 5/5 the notes clear up the uncertainty" -- they did,
# and the code could not see one of them.
TASK_COMPLETED_BY = re.compile(r"Completed by ([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+)")

# Canned text AgencyZoom staples onto the task. It is not a producer outcome
# and must not read as one -- "Make Final Attempts to contact" is an
# instruction, not evidence that anybody was reached.
TASK_BOILERPLATE = re.compile(
    r"the following lead was assigned to you[^.]{0,60}\.?"
    # Bounded to the VALUE. "[^\n]*" ran to the end of a single-line note and
    # deleted the producer's own "CALL DROPPED AFTER AI TRANSFERRED ME"
    # (Elsa Aguilera, 08-17) -- the second time an unbounded strip has eaten
    # the only words that mattered.
    r"|lead('s)? (source|name)\s*:\s*\S+( \S+)?"
    r"|phone( number)?\s*:\s*\(?\d[\d\s().-]{6,}"
    r"|email\s*:\s*\S+@\S+"
    # Bounded on purpose: "[^.]*" ran to the end of a note with no full stop
    # and swallowed the producer's own "Left VM" (Roberto Juarez, 08-17).
    r"|automated (text|email)[^.]{0,30}?(went out|going out)"
    r"( today| yesterday| tomorrow| Yesterday-)?"
    r"|from arizona insurance reports!?"
    r"|phone number \(?\d[\d\s().-]{6,}"
    r"|another text and email will go out[^.]{0,40}"
    r"|will smart ?cycle in \d+ days?"
    r"|make final attempts[^.]{0,60}"
    r"|remove tag[^.]{0,60}"
    r"|call to try to quote"
    r"|this is the last call reminder"
    r"|follow up with lead\.?"
    r"|lead quoted:\s*\d+[^.]{0,25}"
    r"|completed by [A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+",
    re.I)


def task_note_day(create_date):
    """Arizona day a TASK note actually belongs to (its stamp is the eve)."""
    try:
        d = dt.date.fromisoformat(str(create_date)[:10])
    except Exception:
        return None
    return (d + dt.timedelta(days=1)).isoformat()


def task_note_parts(body):
    """(author, producer-written remainder) with the canned text removed."""
    txt = _text(body)
    who = TASK_COMPLETED_BY.search(txt or "")
    stripped = TASK_BOILERPLATE.sub(" ", txt or "")
    stripped = re.sub(r"\s+", " ", stripped).strip(" .~-")
    return (who.group(1) if who else None), stripped


QUOTE_STAGE_RE = re.compile(r"quote", re.I)


def quote_state(lead_id, day, task_titles=()):
    """'today' | 'open' | 'none' -- is a quote out on this lead, and how old?

    TASK TITLES FIRST (Frank, 2026-08-25). The titles in this agency are a
    controlled vocabulary -- "Quote follow #7", "Quoted Yesterday 1st Follow Up
    call" against "Never quoted lead- Day 4 NEW", "Send quote to prospect" --
    and they say plainly whether a quote is already out. quoteDate is NOT used:
    a producer can start a quote one day and present it another, so the date
    does not mean the prospect has seen it.

    'today' is reserved for a quote that went out ON this call, which only a
    same-day MOVE_STAGE into a quote stage can establish -- a task title
    describes the job the producer sat down to do, not what came of it.

    Falls back to stage history when the titles are silent or ambiguous (QNC).
    The window matters: unbounded, "has ever been quoted" made follow-ups of
    leads last quoted in 2022.
    """
    from digest_config import (QUOTE_QNC_TITLE_RE, QUOTE_FOLLOWUP_TITLE_RE,
                               QUOTE_PENDING_TITLE_RE, QUOTE_OPEN_WINDOW_DAYS)
    titled = None
    for t in task_titles:
        t = t or ""
        # QNC == already presented once and did not close, so any QNC task is a
        # follow-up. Checked first: "QNC Lead Day 4" also matches the pending
        # pattern's "Lead Day N" (Frank, 2026-08-25).
        if QUOTE_QNC_TITLE_RE.search(t) or QUOTE_FOLLOWUP_TITLE_RE.search(t):
            titled = "open"      # a quote is already out; strongest signal
            break
        if QUOTE_PENDING_TITLE_RE.search(t):
            titled = "none"      # keep looking -- a follow-up title outranks it

    moved_today, latest_prior = False, None
    for n in load_notes(lead_id):
        if n.get("type") != "MOVE_STAGE":
            continue
        d = str(n.get("createDate") or "")[:10]
        if not d:
            continue
        move, _ = _move_stage_parts(_text(n.get("body")))
        dest = (move.split(" to ")[-1] if " to " in move else move).split("|")[-1]
        # Same "match the stage, not the pipeline" trap as households quoted:
        # "1-2 Leads Not Quoted" is where NEVER-quoted leads are recycled.
        if not QUOTE_STAGE_RE.search(dest) or "not quoted" in dest.lower():
            continue
        if d == day:
            moved_today = True
        elif d < day and (latest_prior is None or d > latest_prior):
            latest_prior = d

    if moved_today:
        return "today"
    if titled is not None:
        return titled
    if latest_prior:
        cutoff = (dt.date.fromisoformat(day)
                  - dt.timedelta(days=QUOTE_OPEN_WINDOW_DAYS)).isoformat()
        return "open" if latest_prior >= cutoff else "none"
    return "none"


# TRAQ writes an AI summary note on EVERY call, voicemails included. It is long
# prose, so NEGATIVE almost never matches it, and the "any note means live" rule
# in is_live turned it into proof of a conversation. On 2026-08-24 five of the 30
# live contacts rested on a TRAQ summary alone -- including an 11-second call to
# Patricia Denhardt whose own summary says "the guest was prompted to leave a
# message", and a 7-second call to Gerardo Ramos Martinez summarised as "the
# guest identification number ... was provided".
TRAQ_NOTE = re.compile(r"^\s*traq call\s*:", re.I)

# What a TRAQ summary of a voicemail says, almost verbatim, every time.
#
# Deliberately NOT added to NEGATIVE. NEGATIVE is checked before `written` in
# is_live, so a machine-read voicemail on one leg of the day would override a
# real conversation the producer wrote up on another. That is exactly what
# happened to Juan Esquivel: a 5-second voicemail at 7:26 PM and a genuine
# 94-second conversation at 7:40 PM ("he mentioned he already has insurance for
# his condo"). This is a WEAKER signal than a human note, and is_live consults
# it only after `written`.
TRAQ_VOICEMAIL = re.compile(
    r"prompted to leave a message|asked to leave a message"
    r"|to leave (a |their )?message for", re.I)


def evidence(lead_id, day, producer):
    """Everything the producer wrote on this lead on this Arizona day."""
    out = {"written": [], "stage_moves": [], "call_notes": [], "negative": False,
           "screener": False, "machine_vm": False}
    for n in load_notes(lead_id):
        t = n.get("type")
        if t == "TASK":
            if task_note_day(n.get("createDate")) != day:
                continue
            author, body = task_note_parts(n.get("body"))
            if author != producer:
                continue
            # Read the no-contact signals off the RAW text as well: stripping
            # exists to stop boilerplate counting as a POSITIVE outcome, and it
            # must never be able to hide a negative one.
            raw = _text(n.get("body")) or ""
            if SCREENER.search(raw):
                out["screener"] = True
            if NEGATIVE.search(raw):
                out["negative"] = True
            if not body:
                continue
            # Task write-ups are trusted for NO-contact only. What is left after
            # the boilerplate is often still instruction text, and treating that
            # as proof of a conversation is how the contact rate got inflated in
            # the first place.
            if SCREENER.search(body):
                out["screener"] = True
            if NEGATIVE.search(body):
                out["negative"] = True
            continue
        if not str(n.get("createDate") or "").startswith(day):
            continue
        if n.get("createdBy") != producer:
            continue
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
                elif not is_data_capture(comment):
                    out["written"].append(comment)
            continue
        if not body or SYSTEM.search(body):
            continue
        # Machine-written summary: read it for a voicemail tell and a screener,
        # but it can never stand as the producer saying they spoke to someone,
        # and it must not set `negative` -- see TRAQ_VOICEMAIL above.
        if TRAQ_NOTE.search(body):
            if TRAQ_VOICEMAIL.search(body):
                out["machine_vm"] = True
            if SCREENER.search(body):
                out["screener"] = True
            continue
        if SCREENER.search(body):
            out["screener"] = True
        if NEGATIVE.search(body):
            out["negative"] = True
        elif not is_data_capture(body):
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
    # ORDER CHANGED 2026-08-18 (Frank: "notes win"). The recording used to be
    # checked first, on the reasoning that only the audio knows what happened.
    # True when the audio is clear -- but it is a 30-second window of a call
    # that may run minutes, in a language the model half-reads, and it was
    # overriding producers who had explicitly written "no answer". Denise
    # Milleville: 12 seconds of "Hi, this is Denise." beat Lorena's own
    # "~Called to offer new quote, no answer."
    #
    # A producer saying nobody was reached is now final. A producer saying they
    # spoke to someone is trusted next. Only then the recording, then duration.
    if ev["negative"]:
        return False, "producer note (no contact)"
    if ev["written"]:
        return True, "producer note"
    # Nobody wrote anything, and the call summary describes a voicemail.
    if ev.get("machine_vm"):
        return False, "call summary reports a voicemail"
    if transcript_class == "live":
        return True, "recording"
    if transcript_class in ("voicemail", "no answer"):
        return False, f"recording ({transcript_class})"
    # We read the audio and found no sign of a second person. Duration must not
    # rescue it: a 53-second voicemail is 53 seconds long (Maria Rodriguez,
    # 2026-08-18). Distinct from "unknown", which means the audio was
    # unreadable and where the duration fallback below still applies.
    if transcript_class == "unclear":
        return False, "recording (no contact evidence)"
    longest = max([c["seconds"] for c in ev["call_notes"]] + [talk_seconds or 0])
    if longest >= DURATION_FALLBACK_SECONDS:
        return True, "duration only"
    return False, "no outcome logged"


def outcome_bucket(ev, live):
    """Call Outcome Breakdown segment."""
    if live:
        return "Live Contact"
    if ev.get("screener"):
        return "Screener"
    joined = " ".join(m["comment"] for m in ev["stage_moves"]) + " "
    if re.search(r"voice ?mail|left ?vm|\bvm\b|left a? ?message|\blm\b", joined, re.I):
        return "Voicemail"
    if re.search(r"screener|gatekeeper|receptionist|ai transfer|transferred me"
                 r"|call dropped|dropped after|auto ?attendant|phone tree|\bivr\b",
                 joined, re.I):
        return "Screener"
    if ev["negative"]:
        return "No Answer"
    return "No Outcome Logged"
