"""Texts and emails: what the producers send, what comes back, and how fast
they answer it (Frank, 2026-09-27: "how can we start including the reading
of texts and emails, and creating stats around them?").

Everything comes from the lead notes the nightly run already downloads
(data/notes/<lead>.json, day_calls.fetch_notes). AgencyZoom stores every
text and email on the lead as a note, beside the calls:

  TEXT   attr.outbound   True = we sent it, False = the lead's reply
         attr.triggerRuleId set = sent by an AgencyZoom automation
         createdBy       the producer (blank on a reply)
  EMAIL  attr.outbound   1 / 0, not True / False (checked 2026-09-27; `_inbound`
                         reads both); createdBy is the mailbox (the producer)
         attr.attachments, lastOpenDate, bounced
  TEXT-FAILED            a text that did not go through

Note times are Arizona local ("2026-09-25 15:22:57"; the text inbox's own
lastMessageDateUTC is seven hours ahead).

EMAIL CARRIES NO AUTOMATION MARKER, so an automation email is recognised by
its template subject (TEMPLATE_SUBJECTS, read off 3,191 sent emails on
2026-09-27, plus any subject sent to 5+ leads in the night's notes), once
the lead's own first name is taken off the front. A template email with an
attachment is the producer's own, and so is a "Re:" -- but only when the lead
had emailed us first: a drip sends "Re: Your insurance quote options" to look
like a reply (four producers' leads between 2:30 and 2:36, 2026-09-23). A template sent by
hand counts as automation too -- the notes cannot tell the two apart.

What a day holds (rows, never medians, so the board can add up any range):

  producers   per producer: texts and emails they sent themselves, the
              automation messages on their leads (never credited to them),
              leads they messaged, how many wrote back the same day, replies
              waiting on them, answered and not, opt-outs, quotes sent by
              email or text and how many were opened, bad contact info
  replies     one row per time a lead wrote in and waited for us: when, what
              they said, and who answered, how (text / email / call) and in
              how many minutes. Consecutive messages before an answer are one
              row. The clock starts at the reply, or at opening time for one
              that came in while the office was closed.
  quotes      every quote a producer sent by email or text (daily.py's own
              quote_presented rule, or an attachment), and whether it was
              opened (emails only; texts carry no open tracking)
  bad_contact bounced emails and failed texts

The day's window for REPLIES starts when the office closed the business day
before, so an evening or weekend reply lands on the next business day's page
and never falls between two. Messages SENT are counted on the day they were
sent. Leads only: a text to a customer (service) is Athena's, not here.
"""
import collections
import datetime as dt
import json
import pathlib
import re

import digest_config as cfg
import live_contact as lc
from az_corpus import e164

ROOT = pathlib.Path(__file__).resolve().parent
AZ = dt.timezone(dt.timedelta(hours=-7))
OFFICE_OPEN = (8, 30)
OFFICE_CLOSE = (17, 30)     # "the office closes at 5:30" (CLAUDE.md)

# A reply that asks for nothing -- "ok", "thanks", a thumbs up. Counted as a
# reply (the lead wrote back) but never listed as waiting on an answer.
ACK = re.compile(r"^\s*(ok(ay)?|k|thanks?|thank you( so much)?|ty|gracias|muchas gracias|"
                 r"perfect|perfecto|sounds good|great|👍|🙏|❤️|😊)[\s!.,👍🙏😊❤️]*$", re.I)
# A short "you too" / "thank you again" -- no question in it -- is an
# acknowledgement too (2026-09-27, a September spot-check).
ACK_SHORT = re.compile(r"^\s*(ok(ay)?|thanks?|thank you|gracias|grx|you too|same to you|igualmente|"
                       r"have a (good|great|nice)|perfect|perfecto|sounds good)\b", re.I)
# The lead asking us to stop: counted, never waiting on an answer.
OPT_OUT = re.compile(r"^\s*(stop( all)?|unsubscribe|cancel|end|quit|alto|baja|"
                     r"stop texting( me)?|no more texts?)\s*[.!]*\s*$"
                     r"|(please )?(do not|don'?t|dont) (reach out|contact|text|call|message|email)( to)?( me)?( anymore| again)"
                     r"|stop (texting|calling|contacting|messaging)|remove me|take me off|unsubscribe", re.I)
# The lead saying we have the wrong person: bad contact info, not a reply
# waiting on us ("I dont know who that is! Never ever heard that name").
WRONG = re.compile(r"wrong (number|person)|(don'?t|dont|do not) know who (that|this) is|"
                   r"never (ever )?heard (of )?(that|this) name|n[uú]mero equivocado", re.I)
# Quoted history under an email reply ("On Tue, Jul 14 ... wrote:").
_EMAIL_QUOTE = re.compile(r"\s(On|El) [^<>]{5,80}(wrote|escribió):.*$", re.S)

# AgencyZoom automation email subjects, lower-case, with the lead's first
# name taken off the front (sent to 5+ leads with no attachment, 2026-09-27).
TEMPLATE_SUBJECTS = {
    "do you still need insurance?", "i'm getting worried", "can we try again?",
    "we lowered rates!", "i'll check back in a few months", "your insurance quote options",
    "there's a reason…", "can we try again again?", "just checking in 😊",
    "would you like to get started?", "thanks for connecting with us", "got a quick min to talk?",
    "in love or just paying a bill?", "updated quote?", "we miss you (pig time 🐷)",
    "¿te gustaría empezar?", "thank you for your time today", "don't forget",
    "tienes un minuto para hablar?", "what's holding you back?", "¿podemos intentarlo de nuevo?",
    "about your home policy!", "te extrañamos", "cotización actualizada?", "i work for you...",
    "we've missed you", "no te olvides", "bajaron nuestras tarifas!", "me estoy preocupando",
    "¿qué te esta deteniendo?", "shop small for your insurance", "auto insurance quote",
    "about your auto insurance!", "it's been a week", "we’ll be in touch soon",
    "save on your current home insurance!", "nuestras tarifas bajaron!",
    "estoy empezando a preocuparme", "do you have 5 min?", "una oficina local para tu seguro",
    "hay una razón", "call, text or email?", "are you ready to discuss the next steps?",
    "podemos intentarlo de nuevo?", "gracias por su tiempo hoy flores insurance agency",
    "gracias por su tiempo hoy ~ flores insurance agency", "thanks for connecting on facebook",
    "can we try again again again? 😂", "thanks for connecting on farmers.com",
    "save 20% off your current home insurance!", "look-over-your-shoulder syndrome",
    "yo le ayudare con el arizona insurance reports!", "llamada, texto o correo electronico?",
    "thanks for connecting on google", "life insurance awareness???", "porque usted lo pidio",
    "volveré a comunicarme con usted en unos meses", "¿aún necesitas un seguro?",
    "acerca de el seguro de su casa!", "enamorado o simplemente pagando una cuenta??",
    "estas listo para revisar los siguientes pasos?", "save on your current auto insurance!",
    "acerca de el seguro de sus autos!", "what happens in 6 months?",
    "💭 are you still interested in hearing from us? 💭", "síndrome de mirar por encima del hombro",
}
LEARN_TEMPLATE_LEADS = 5
# A call the lead made that answers their text only if it was a conversation.
CONVERSATION_SECONDS = 30


def _at(s):
    """A note's createDate ("YYYY-MM-DD HH:MM:SS", Arizona) as an aware time."""
    try:
        return dt.datetime.fromisoformat(str(s).strip().replace(" ", "T")[:19]).replace(tzinfo=AZ)
    except ValueError:
        return None


def _prev_business_day(day):
    d = dt.date.fromisoformat(day) - dt.timedelta(days=1)
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d


def _clock(d, hm):
    return dt.datetime(d.year, d.month, d.day, hm[0], hm[1], tzinfo=AZ)


def window(day):
    """(start, end) of the day's reply window: the office's close the
    business day before, to its close on `day`."""
    return (_clock(_prev_business_day(day), OFFICE_CLOSE),
            _clock(dt.date.fromisoformat(day), OFFICE_CLOSE))


def active_leads(leads, day):
    """Lead ids with activity inside the reply window or on the day itself --
    what daily.py downloads notes for, so a lead who only texted (or was only
    texted) is read too. lastActivityDate is UTC."""
    start, _ = window(day)
    end = _clock(dt.date.fromisoformat(day), (23, 59))
    out = []
    for l in leads:
        s = str(l.get("lastActivityDate") or "").strip()
        try:
            t = dt.datetime.fromisoformat(s.replace(" ", "T")[:19]).replace(tzinfo=dt.timezone.utc)
        except ValueError:
            continue
        if start <= t <= end:
            out.append(l["id"])
    return out


# Card, bank and social security numbers customers text or email in to pay
# (2026-09-24: a full card number, texted to pay a bill). Never stored: the
# day document is on the board. A run of 9+ digits (spaces and dashes
# allowed) is any of them; a 3-4 digit code right after "cvv" / "code" /
# "exp" goes too.
_LONG_DIGITS = re.compile(r"(?<!\d)(?:\d[ \-.]?){8,}\d(?!\d)")
_SSN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
_CODE = re.compile(r"(?i)\b(cvv|cvc|csc|security code|c[oó]digo|code|exp(iration)?|vence)\b[\s:#]*\d[\d/ ]{1,6}")


def redact(t):
    t = _SSN.sub("[number removed]", str(t or ""))
    t = _LONG_DIGITS.sub("[number removed]", t)
    return re.sub(r"  +", " ", _CODE.sub(lambda m: m.group(1) + " [removed] ", t)).strip()


def _inbound(attr):
    """The lead wrote to us. TEXT notes say outbound False, EMAIL notes 0 --
    `is False` alone read every emailed reply as one the producer sent."""
    return "outbound" in attr and attr["outbound"] is not None and not attr["outbound"]


def _text(n):
    a = n.get("attr") or {}
    body = a.get("emailSnippet") if n.get("type") == "EMAIL" and a.get("emailSnippet") else n.get("body")
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(body or ""))).strip()
    t = re.sub(r"&nbsp;", " ", t).replace("&#39;", "'").replace("&quot;", '"').replace("&amp;", "&")
    return redact(_EMAIL_QUOTE.sub("", t).strip())


def _subject_key(n, first):
    s = str((n.get("attr") or {}).get("emailSubject") or n.get("title") or "")
    s = re.sub(r"^\s*((re|fw|fwd):\s*)+", "", s, flags=re.I).strip()
    if first and s.lower().startswith(first.lower()):
        s = s[len(first):]
    return re.sub(r"^[\s,.:;!\-]+", "", s).strip().lower()


def _is_reply_subject(n):
    return bool(re.match(r"^\s*(re|fw|fwd):", str((n.get("attr") or {}).get("emailSubject") or ""), re.I))


def build(day, log=print, live=False):
    """The day's texts-and-emails document, or None when there is nothing to
    read (no lead corpus or no notes on disk). `live` (checkpoints only) adds
    `_live`, what the board's Worker needs to carry the figures on between
    checkpoints (see live_basis below); publish_board moves it into the
    document's live_basis."""
    corpus = ROOT / "data/az_leads_all.json"
    if not corpus.exists():
        return None
    leads = json.loads(corpus.read_text())
    by_az = {str(v["az_id"]): n for n, v in cfg.PRODUCERS.items()}
    producers = set(cfg.PRODUCERS)
    start, end = window(day)
    day_end = _clock(dt.date.fromisoformat(day), (23, 59))
    opens_at = _clock(dt.date.fromisoformat(day), OFFICE_OPEN)

    # One person per phone number: duplicate lead records are pervasive, and
    # a reply on one record answered from another is still answered.
    person, owner, name, lead_of, first = {}, {}, {}, {}, {}
    for l in leads:
        lid = l.get("id")
        if not (ROOT / f"data/notes/{lid}.json").exists():
            continue
        key = e164(l.get("phone")) or e164(l.get("secondaryPhone")) or f"lead:{lid}"
        person[lid] = key
        who = by_az.get(str(l.get("assignedTo")))
        if who:
            owner.setdefault(key, who)
        name.setdefault(key, " ".join(x for x in ((l.get("firstname") or "").strip(),
                                                   (l.get("lastname") or "").strip()) if x) or "(no name)")
        lead_of.setdefault(key, lid)
        first[lid] = (l.get("firstname") or "").strip()
    if not person:
        return None

    # Every text / email on those leads, tagged.
    events = collections.defaultdict(list)     # person -> [event]
    learn = collections.defaultdict(set)
    raw = []
    wrote_in = collections.defaultdict(list)    # lead -> times the lead emailed us
    seen_at = {}                                # person -> newest note this build read
    for lid, key in person.items():
        for n in lc.load_notes(lid):
            t = n.get("type")
            if t not in ("TEXT", "EMAIL", "TEXT-FAILED", "CALL"):
                continue
            # Only the message notes say how far this build read: a TASK note
            # is stamped 5 PM the day before it is due, so it would put
            # `seen` hours ahead of the checkpoint and hide every text the
            # Worker finds before then (2026-09-30).
            c = str(n.get("createDate") or "")[:19]
            if c > seen_at.get(key, ""):
                seen_at[key] = c
            at = _at(n.get("createDate"))
            if at is None:
                continue
            raw.append((lid, key, n, at))
            a = n.get("attr") or {}
            if t == "EMAIL" and _inbound(a):
                wrote_in[lid].append(at)
    def real_reply(lid, n, at):
        return _is_reply_subject(n) and any(w < at for w in wrote_in.get(lid, ()))
    for lid, key, n, at in raw:
        a = n.get("attr") or {}
        if n.get("type") == "EMAIL" and a.get("outbound") and not a.get("attachments") and not real_reply(lid, n, at):
            learn[_subject_key(n, first.get(lid))].add(lid)
    templates = TEMPLATE_SUBJECTS | {k for k, v in learn.items() if k and len(v) >= LEARN_TEMPLATE_LEADS}

    import daily
    for lid, key, n, at in raw:
        t = n.get("type")
        a = n.get("attr") or {}
        by = (n.get("createdBy") or "").strip()
        ev = {"at": at, "lead_id": lid, "type": t, "by": by, "text": _text(n) if t != "CALL" else ""}
        if t == "CALL":
            # AgencyZoom's own call log note, either direction. A call the
            # lead made counts as answering them only if it was a real
            # conversation; any call the producer made back counts.
            m = re.search(r"Duration:\s*(\d+)", str(n.get("body") or ""))
            ev.update(kind="call", dur=int(m.group(1)) if m else 0, inbound=_inbound(a))
            if ev["inbound"] and ev["dur"] < CONVERSATION_SECONDS:
                continue
        elif t == "TEXT-FAILED":
            ev["kind"] = "failed"
        elif _inbound(a):
            ev["kind"] = "in"
        elif t == "TEXT":
            ev["kind"] = "auto" if a.get("triggerRuleId") else "sent"
        else:
            tmpl = (_subject_key(n, first.get(lid)) in templates
                    and not a.get("attachments") and not real_reply(lid, n, at))
            ev["kind"] = "auto" if tmpl else "sent"
            ev["subject"] = str(a.get("emailSubject") or "").strip()
            ev["attachments"] = len(a.get("attachments") or [])
            ev["opened"] = bool(a.get("lastOpenDate"))
            ev["bounced"] = bool(a.get("bounced"))
            ev["bounce_reason"] = str(a.get("bounceReason") or "").strip()
        events[key].append(ev)

    # Dials by the producers to each person's numbers, as "call" touches.
    try:
        import day_calls
        for who, bynum in day_calls.producer_dials(day).items():
            for num, calls in bynum.items():
                if num not in events:
                    continue
                for c in calls:
                    try:
                        ct = dt.datetime.fromisoformat(str(c["startTime"]).replace("Z", "+00:00")).astimezone(AZ)
                    except (KeyError, ValueError):
                        continue
                    events[num].append({"at": ct, "kind": "call", "by": who, "type": "CALL", "text": "",
                                        "dur": int(c.get("duration") or 0), "inbound": False})
    except Exception as e:
        log(f"  messages: no call log for answers by phone ({type(e).__name__})")

    # The same message on two duplicate lead records is one message.
    for key in list(events):
        seen, keep = set(), []
        for e in sorted(events[key], key=lambda e: e["at"]):
            sig = (e["at"].isoformat()[:16], e["kind"], e["type"], e.get("text", "")[:80], e.get("by", ""))
            if sig not in seen:
                seen.add(sig)
                keep.append(e)
        events[key] = keep

    stats = {p: collections.Counter() for p in cfg.PRODUCERS}
    replies, quotes, bad = [], [], []
    carry = {}                                  # person -> live state (live=True)
    for key, evs in events.items():
        evs.sort(key=lambda e: e["at"])
        own = owner.get(key)
        lead = name.get(key, "(no name)")

        # --- what went out today -------------------------------------------
        first_sent = {}
        for e in evs:
            if e["at"].date().isoformat() != day:
                continue
            credit = e["by"] if e["by"] in producers else own
            if e["kind"] == "sent" and e["by"] in producers:
                stats[e["by"]]["texts" if e["type"] == "TEXT" else "emails"] += 1
                first_sent.setdefault(e["by"], e["at"])
                if e["type"] == "EMAIL" and (e.get("attachments") or daily.quote_presented(e["text"])) \
                        or e["type"] == "TEXT" and daily.quote_presented(e["text"]):
                    opened = e.get("opened") if e["type"] == "EMAIL" else None
                    stats[e["by"]]["quotes"] += 1
                    stats[e["by"]]["quotes_opened"] += bool(opened)
                    quotes.append({"who": e["by"], "lead": lead, "lead_id": e["lead_id"],
                                   "at": e["at"].strftime("%H:%M"), "day": day,
                                   "channel": "email" if e["type"] == "EMAIL" else "text",
                                   "subject": e.get("subject", ""), "opened": opened})
            elif e["kind"] == "auto" and credit in producers:
                stats[credit]["auto_texts" if e["type"] == "TEXT" else "auto_emails"] += 1
            if credit in producers and (e["kind"] == "failed" or e.get("bounced")):
                stats[credit]["bad"] += 1
                bad.append({"who": credit, "lead": lead, "lead_id": e["lead_id"], "day": day,
                            "channel": "text" if e["type"] != "EMAIL" else "email",
                            "reason": e.get("bounce_reason") or ("text failed" if e["kind"] == "failed" else "bounced")})
        wrote_back = []
        for who, t0 in first_sent.items():
            stats[who]["leads"] += 1
            if any(e["kind"] == "in" and e["at"] > t0 and e["at"] <= day_end for e in evs):
                stats[who]["wrote_back"] += 1
                wrote_back.append(who)
        open_row = run_state = None

        # --- replies waiting on us ------------------------------------------
        # A touch answers the lead: a message someone typed, a call back, or
        # a call still going when their text arrived (Stephanie Esquivel,
        # 2026-09-24, texted Mike five seconds into her own call to him).
        touches = [t for t in evs if t["kind"] in ("sent", "call") and t["at"] <= day_end]
        def ends(t):
            return t["at"] + dt.timedelta(seconds=t.get("dur") or 0)
        i = 0
        while i < len(evs):
            e = evs[i]
            if e["kind"] != "in" or not (start < e["at"] <= end):
                i += 1
                continue
            # Whose conversation it is: whoever last typed to this person, or
            # the lead's producer when only automations had (a reply to a drip
            # text). Someone else's -- Debbie on a payment -- is service, not
            # a producer's reply to answer (Suzanne Mendenhall, 2026-09-23).
            before = [t for t in evs if t["kind"] == "sent" and t["at"] < e["at"]]
            partner = before[-1]["by"] if before and before[-1]["by"] else own
            ans = next((t for t in touches if ends(t) >= e["at"]), None)
            # Nothing answered it: every message to the end of the window is the
            # same wait (Nery Pulido, 2026-09-10: two texts a minute apart).
            stop = end if ans is None else (ans["at"] if ans["at"] > e["at"] else e["at"])
            run = [x for x in evs[i:] if x["kind"] == "in" and x["at"] <= max(stop, e["at"]) and x["at"] <= end] or [e]
            i = evs.index(run[-1]) + 1
            said = " / ".join(x["text"] for x in run if x["text"])[:300]
            any_optout = any(OPT_OUT.search(x["text"] or "") for x in run)
            any_wrong = any(WRONG.search(x["text"] or "") for x in run)
            all_ack = all(
                ACK.match(x["text"] or "") or (ACK_SHORT.match(x["text"] or "") and "?" not in x["text"]
                                               and len(x["text"].split()) <= 6)
                for x in run if x["text"])
            if ans is None:
                # Nothing has answered this wait yet, so every later message
                # in the window joins it: the Worker carries it on from here
                # (live_notes.messageDeltas) and re-judges it over all of its
                # messages, as this loop does -- ack, opt-out or not listed
                # at all (2026-09-30).
                run_state = {"lead_id": e["lead_id"],
                             "at": e["at"].strftime("%H:%M") if e["at"].date().isoformat() == day else e["at"].strftime("%m-%d %H:%M"),
                             "who": partner, "listed": partner in producers, "start": e["at"].isoformat(),
                             "channel": "email" if e["type"] == "EMAIL" else "text",
                             "messages": len(run), "said": said,
                             "all_ack": all_ack, "any_optout": any_optout, "any_wrong": any_wrong}
            if partner not in producers:
                continue
            optout = any_optout
            wrong = not optout and any_wrong
            ack = not optout and not wrong and all_ack
            if wrong:
                stats[partner]["bad"] += 1
                bad.append({"who": partner, "lead": lead, "lead_id": e["lead_id"], "day": day,
                            "channel": "email" if e["type"] == "EMAIL" else "text",
                            "reason": "wrong person (the lead said so): " + said[:80]})
                continue
            stats[partner]["replies"] += 1
            row = {"who": partner, "lead": lead, "lead_id": e["lead_id"], "day": day,
                   "at": e["at"].strftime("%H:%M") if e["at"].date().isoformat() == day else e["at"].strftime("%m-%d %H:%M"),
                   "channel": "email" if e["type"] == "EMAIL" else "text",
                   "said": said, "messages": len(run), "optout": optout, "ack": ack,
                   "answered_by": None, "via": None, "minutes": None}
            if optout:
                stats[partner]["optouts"] += 1
            elif ack:
                stats[partner]["acks"] += 1
            elif ans:
                # A reply that came in while the office was closed starts
                # the clock at opening time.
                clock = max(e["at"], opens_at)
                row.update(answered_by=ans["by"] or None,
                           via={"TEXT": "text", "EMAIL": "email", "CALL": "call"}.get(ans["type"], ans["type"]),
                           minutes=max(0, int((ans["at"] - clock).total_seconds() // 60)))
                stats[partner]["answered"] += 1
            else:
                stats[partner]["unanswered"] += 1
                open_row = {"lead_id": row["lead_id"], "at": row["at"], "who": partner,
                            "start": e["at"].isoformat()}
            replies.append(row)
        if live and any(e["at"] > start for e in evs):
            sent = [t for t in evs if t["kind"] == "sent" and t["at"] <= day_end]
            carry[key] = {
                "leads": [l for l, k in person.items() if k == key],     # messages.build's own order
                "seen": seen_at.get(key, ""), "owner": own, "name": lead,
                "last_sender": sent[-1]["by"] if sent and sent[-1]["by"] else None,
                "sent_by": sorted(first_sent), "wrote_back": sorted(wrote_back),
                "open": open_row, "run": run_state}

    replies.sort(key=lambda r: (r["answered_by"] is not None, r["at"]))
    quotes.sort(key=lambda r: r["at"])
    log(f"  messages: {sum(s['texts'] for s in stats.values())} texts and "
        f"{sum(s['emails'] for s in stats.values())} emails sent by producers, "
        f"{sum(s['replies'] for s in stats.values())} replies "
        f"({sum(s['unanswered'] for s in stats.values())} unanswered)")
    out = {"day": day, "window": [start.isoformat(), end.isoformat()],
           "producers": {p: dict(c) for p, c in stats.items()},
           "replies": replies, "quotes": quotes, "bad_contact": bad}
    if live:
        out["_live"] = live_basis(carry, templates)
    return out


def live_basis(people, templates):
    """What the Worker (site/live.js messagesLive) needs to carry the day on
    from this checkpoint: per person (phone number), the lead records, the
    newest note this build read (anything later is new), whose lead it is,
    who last typed to them, who has already messaged them today and been
    written back, and the reply still waiting on an answer. Plus this
    module's own patterns as regex source, so the Worker reads messages by
    the very same rules -- never retyped in JS."""
    def rx(r):
        # As (source, flags) for JavaScript's RegExp, which has no inline (?i).
        src = r.pattern.replace("(?i)", "")
        return [src, ("i" if r.flags & re.I or "(?i)" in r.pattern else "") + ("s" if r.flags & re.S else "")]
    return {
        "people": people,
        "templates": sorted(templates),
        "rx": {k: rx(v) for k, v in (("ack", ACK), ("ack_short", ACK_SHORT), ("opt_out", OPT_OUT),
                                     ("wrong", WRONG), ("email_quote", _EMAIL_QUOTE),
                                     ("ssn", _SSN), ("long_digits", _LONG_DIGITS), ("code", _CODE))},
        "office_open": "%02d:%02d" % OFFICE_OPEN, "office_close": "%02d:%02d" % OFFICE_CLOSE,
        "conversation_seconds": CONVERSATION_SECONDS,
    }


def _fetch_notes_paced(lead_ids, fresh_after, log=print, pause=0.35):
    """Download notes for many leads without tripping AgencyZoom's burst
    limit (it 429s on bursts of note reads). A copy fetched after
    `fresh_after` is kept; a failed fetch keeps the old copy."""
    import time
    from az_client import AgencyZoom
    az = AgencyZoom()
    lc.NOTE_DIR.mkdir(parents=True, exist_ok=True)
    got = failed = 0
    for i, lid in enumerate(sorted(set(lead_ids)), 1):
        f = lc.NOTE_DIR / f"{lid}.json"
        if f.exists() and f.stat().st_mtime >= fresh_after:
            continue
        try:
            f.write_text(json.dumps(az.lead_notes(lid) or []))
            got += 1
        except Exception:
            failed += 1
        if i % 200 == 0:
            log(f"    notes: {i} of {len(set(lead_ids))} checked")
        time.sleep(pause)
    log(f"  notes: {got} downloaded" + (f", {failed} failed (old copy kept)" if failed else ""))


def backfill(start, end=None, refresh=True, force=False, log=print):
    """Add `messages` to the published day documents from `start` to `end`
    (Frank, 2026-09-27: "anyway to build it back to 9/1?").

    Notes hold a lead's whole history, so reading them now recovers any past
    day's texts and emails. Which leads had messages on a past day cannot be
    told from today's lead snapshot, so every producer lead with activity
    since the window before `start` is read. Each day document is backed up
    under backups/<today>-messages-backfill/ first, and only its `messages`
    key is added: every other figure stays exactly as it went out. Past
    days have no RingCentral call log on disk, so a call back is seen only
    through AgencyZoom's own CALL notes; email opens are as of now, not as
    of that night."""
    import time
    import publish_board
    end = end or (dt.date.today() - dt.timedelta(days=1)).isoformat()
    if refresh:
        import az_corpus
        leads = az_corpus.fetch(force=True)
        log(f"  lead snapshot refreshed: {len(leads):,} leads")
    else:
        leads = json.loads((ROOT / "data/az_leads_all.json").read_text())
    azid = {v["az_id"] for v in cfg.PRODUCERS.values()}
    since = window(start)[0].astimezone(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    ids = [l["id"] for l in leads if l.get("assignedTo") in azid
           and str(l.get("lastActivityDate") or "") >= since]
    log(f"  {len(ids):,} producer leads active since {start}")
    _fetch_notes_paced(ids, fresh_after=time.time() - 6 * 3600, log=log)

    cli, bucket = publish_board._client()
    keys, token = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": "days/2026-"}
        if token:
            kw["ContinuationToken"] = token
        page = cli.list_objects_v2(**kw)
        keys += [o["Key"] for o in page.get("Contents", [])]
        if not page.get("IsTruncated"):
            break
        token = page.get("NextContinuationToken")
    days = sorted(m.group(1) for k in keys
                  for m in [re.match(r"^days/(\d{4}-\d{2}-\d{2})\.json$", k)] if m
                  and start <= m.group(1) <= end)
    stamp = dt.date.today().isoformat()
    done = []
    for day in days:
        key = f"days/{day}.json"
        raw = cli.get_object(Bucket=bucket, Key=key)["Body"].read()
        doc = json.loads(raw)
        if doc.get("messages") and not force:
            log(f"  {day}: already has texts and emails, left as is")
            continue
        m = build(day, log=log)
        if not m:
            log(f"  {day}: nothing to add")
            continue
        backup = f"backups/{stamp}-messages-backfill/{key}"
        try:
            cli.head_object(Bucket=bucket, Key=backup)
        except Exception:
            cli.put_object(Bucket=bucket, Key=backup, Body=raw, ContentType="application/json")
        doc["messages"] = m
        cli.put_object(Bucket=bucket, Key=key, Body=json.dumps(doc, default=str).encode(),
                       ContentType="application/json", CacheControl="no-store")
        done.append(day)
    log(f"  backfilled {len(done)} day(s): {', '.join(done) or 'none'}")
    return done


if __name__ == "__main__":
    import sys
    if sys.argv[1:2] == ["--backfill"]:
        backfill(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None,
                 refresh="--no-refresh" not in sys.argv, force="--force" in sys.argv)
        sys.exit(0)
    d = build(sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat())
    if not d:
        print("nothing to read")
    else:
        for p, s in d["producers"].items():
            print(f"{p:16s} {s}")
        print(f"\n{len(d['replies'])} replies, {len(d['quotes'])} quotes sent, {len(d['bad_contact'])} bad contact")
        for r in d["replies"][:15]:
            print(" ", r["who"].split()[0], r["lead"][:20], r["at"], r["channel"], "|", r["said"][:60], "|",
                  r["answered_by"], r["via"], r["minutes"], "ack" if r["ack"] else "", "OPT-OUT" if r["optout"] else "")
