"""What Apollo knows about a lead from before today's call (Frank, 2026-09-25:
"apollo can access whatever history he needs to be able to make sense of
everything").

A follow-up or a call back is a different call from a first conversation:
the producer should reconnect to the last conversation, assume the sale up
front, deal with whatever stalled it, and not redo discovery that was
already done. Apollo can only coach that if it can see what was done
before. This module builds that picture from what the day's run already
has, so it costs no extra model reads:

  * which way today's call went (the producer dialled, the lead called in,
    or the lead returned the producer's call);
  * how often the number was dialled in the trailing 30 days, and when;
  * the quotes on the lead (carrier, product, premium, sold) -- the one
    AgencyZoom request per card here, made only when a card is being read;
  * earlier coaching cards on the same lead (the board's days/ documents in
    R2, trailing 30 days): what was said and which objections came up;
  * the lead's recent notes before today (data/notes, fetched earlier in
    the run), TRAQ's auto-summaries labelled as such.

How Apollo uses it is coaching/METHODOLOGY.md's "Follow-ups and call backs".
"""
import collections
import datetime as dt
import json
import pathlib
import re

import live_contact as lc

ROOT = pathlib.Path(__file__).resolve().parent
WINDOW_DAYS = 30
MAX_NOTES = 8
NOTE_CHARS = 220
SKIP_NOTE_TYPES = {"CALL", "auto_unenroll_automation"}   # call-log rows: the dial counts cover them
TRAQ = re.compile(r"traq call|app\.traq\.ai", re.I)
# A note that says the quote went out -- sent, emailed, texted, attached --
# whether it delivers the quote (daily.quote_presented) or chases one already
# sent ("the quote I sent you"). Either way the quote was PRESENTED (Frank,
# 2026-09-27), so the next call is a follow-up whatever the stage says
# (Frank, 2026-09-30).
QUOTE_SENT = re.compile(
    r"\b(sent|send you|emailed|e-mailed|texted|attached|attaching)\b[^.!?]{0,40}\b(quotes?|cotizaci[oó]n(es)?)\b"
    r"|\b(quotes?|cotizaci[oó]n(es)?)\b[^.!?]{0,30}\b(sent|emailed|e-mailed|texted|attached|enviad[ao]s?)\b"
    r"|\bte (mand[eé]|envi[eé])\b[^.!?]{0,30}\bcotizaci[oó]n", re.I)


def _automated(n):
    """An AgencyZoom drip, or the lead's own message: neither is someone on
    the team saying a quote went out (messages.py's own markers -- a text's
    triggerRuleId, an email on a template subject with no attachment)."""
    a = n.get("attr") or {}
    if a.get("outbound") in (False, 0) or a.get("triggerRuleId"):
        return True
    if n.get("type") == "EMAIL" and not a.get("attachments"):
        try:
            import messages
            subj = re.sub(r"^\s*(re|fwd?):\s*", "", str(a.get("emailSubject") or ""), flags=re.I).strip().lower()
            return any(subj == t or subj.endswith(t) for t in messages.TEMPLATE_SUBJECTS)
        except Exception:
            return False
    return False


def quote_sent(text):
    """True when a note says a quote was sent to the lead."""
    try:
        import daily
        if daily.quote_presented(text):
            return True
    except Exception:
        pass
    return bool(QUOTE_SENT.search(text or ""))


def direction_key(group):
    """"dialled", "call back" (the lead returned the producer's call) or
    "call in" (the lead called in on their own) -- WHO dialled, which is not
    what the call was for: a call back can be a first conversation, a call
    to finish the quote, or a follow-up (Frank, 2026-09-25). Apollo decides
    that (`flow`) from the stage and the history."""
    inbound = [r for r in group if r.get("inbound")]
    outbound = [r for r in group if not r.get("inbound")]
    if any(r.get("callback_seconds") for r in outbound) or any(r.get("kind") == "callback" for r in inbound):
        return "call back"
    return "call in" if inbound else "dialled"


def answered(group):
    """True when the producer picked up an inbound call on this lead today --
    a call back or a call-in, most likely on their direct line -- so the
    greeting is scored (Frank, 2026-09-25)."""
    return direction_key(group) != "dialled"


def _last10(s):
    d = re.sub(r"\D", "", str(s or ""))
    return d[-10:] if len(d) >= 10 else None


def answer_route(group, producer, ctx=None):
    """"transferred" (the front desk picked up and handed the call over),
    "direct" (it rang the producer's own line), or None when nothing on file
    says -- for the inbound call(s) on this card (Frank, 2026-09-30: a
    transferred call is its own kind of greeting). From what the day already
    holds, no new request: an inbound row whose recording stops at the
    hand-off (`partial` -- RingCentral stops recording at a park, which only
    a transfer does), else inbound.attribute's own route over the day's RC
    log (ctx.routes)."""
    if not answered(group):
        return None
    if any(r.get("inbound") and r.get("partial") for r in group):
        return "transferred"
    routes = set()
    for r in group:
        if r.get("inbound") or r.get("callback_seconds"):
            routes |= (ctx.routes() if ctx else {}).get((producer, _last10(r.get("number"))), set())
    if len(routes) == 1:
        return next(iter(routes))
    return None


def direction(group, route=None):
    """How today's conversation(s) with this lead came about, for Apollo."""
    key = direction_key(group)
    dialled_too = any(not r.get("inbound") for r in group)
    if key == "call back":
        text = "a call back: the producer dialled and the lead returned the call"
    elif key == "call in":
        text = ("the producer dialled, and the lead also called in" if dialled_too
                else "the lead called in")
    else:
        return "the producer dialled the lead"
    if route == "transferred":
        text += (". The front desk answered and TRANSFERRED the call to the producer, so the "
                 "producer picked up knowing who was on the line and why -- a transfer pickup "
                 "(see \"The greeting on a call the producer ANSWERED\"); the recording may "
                 "open with the front desk, whose words are never the producer's greeting")
    elif route == "direct":
        text += ". It rang the producer's own direct line and the producer picked up"
    return (text + " -- the producer ANSWERED an inbound call, so score `greeting`. "
            "Who dialled is not the flow: decide `flow` from the stage and the history")


class Context:
    """Per-day sources, loaded once per coaching build and only when a card
    is being read."""

    def __init__(self, day, log=print, past=False):
        self.day = day
        # A day rebuilt after the fact: AgencyZoom keeps no date on a quote,
        # so today's list could hold quotes made after that day's call.
        self.past = past
        self.log = log
        self._dials = None
        self._cards = None
        self._az = None
        self._routes = None

    def routes(self):
        """{(producer, last ten digits): {"direct"/"transferred"}} for the
        day's answered call-ins, by inbound.answered over the day's saved RC
        log (data/rc_raw_<day>.json) -- the same legs the run already read."""
        if self._routes is None:
            self._routes = collections.defaultdict(set)
            try:
                import inbound
                recs = json.loads((ROOT / f"data/rc_raw_{self.day}.json").read_text())
                for r in inbound.answered(self.day, recs):
                    if r.get("route"):
                        self._routes[(r["producer"], _last10(r.get("number")))].add(r["route"])
            except Exception as e:
                self.log(f"    lead history: no call-in routes ({type(e).__name__})")
        return self._routes

    def dials(self):
        """{number: [(startTime, producer)]} over the trailing window, before today."""
        if self._dials is None:
            self._dials = collections.defaultdict(list)
            try:
                import day_calls
                for who, bynum in day_calls.window_dials(self.day).items():
                    for num, recs in bynum.items():
                        for r in recs:
                            t = str(r.get("startTime") or "")
                            if t[:10] < self.day:
                                self._dials[num].append((t, who))
            except Exception as e:
                self.log(f"    lead history: no dial window ({type(e).__name__})")
        return self._dials

    def cards(self):
        """{lead_id: [card, ...]} from the board's published days before today."""
        if self._cards is None:
            self._cards = collections.defaultdict(list)
            try:
                import publish_board
                cli, bucket = publish_board._client()
                start = dt.date.fromisoformat(self.day) - dt.timedelta(days=WINDOW_DAYS)
                d = start
                while d.isoformat() < self.day:
                    try:
                        doc = json.loads(cli.get_object(Bucket=bucket, Key=f"days/{d.isoformat()}.json")["Body"].read())
                        for c in doc.get("calls") or []:
                            if c.get("lead_id"):
                                self._cards[c["lead_id"]].append({**c, "day": d.isoformat()})
                    except Exception:
                        pass
                    d += dt.timedelta(days=1)
            except Exception as e:
                self.log(f"    lead history: no earlier cards ({type(e).__name__})")
        return self._cards

    def quotes(self, lead_id):
        try:
            if self._az is None:
                from az_client import AgencyZoom
                self._az = AgencyZoom()
            q = self._az.quotes(lead_id) or []
            return q.get("quotes") if isinstance(q, dict) else q
        except Exception:
            return None


def _fmt_money(v):
    try:
        return f"${float(v):,.0f}"
    except (TypeError, ValueError):
        return "?"


def block(group, day, ctx, producer=None):
    """The "Lead history" text for one card's rows."""
    lines = [f"Today's call: {direction(group, answer_route(group, producer, ctx))}."]
    lead_ids = [r.get("lead_id") for r in group if r.get("lead_id")]
    lead_id = lead_ids[0] if lead_ids else None
    numbers = {r.get("number") for r in group if r.get("number")}

    prior = sorted((t for n in numbers for t in ctx.dials().get(n, [])), reverse=True)
    if prior:
        who = collections.Counter(w for _, w in prior).most_common(1)[0][0]
        lines.append(f"Dialled {len(prior)} time{'s' if len(prior) != 1 else ''} in the {WINDOW_DAYS} days "
                     f"before today, last on {prior[0][0][:10]} (mostly by {who}).")
    else:
        lines.append(f"Not dialled in the {WINDOW_DAYS} days before today.")

    if lead_id is None:
        lines.append("No AgencyZoom lead record, so no quotes, earlier cards or notes to show.")
        return _render(lines)

    qs = None if ctx.past else ctx.quotes(lead_id)
    if ctx.past:
        lines.append("Quotes on file: left out -- this day was rebuilt later, and AgencyZoom keeps no "
                     "quote date, so today's list could hold quotes made after this call. Go by the "
                     "notes and earlier cards for what was quoted before it.")
    elif qs is None:
        lines.append("Quotes on file: unavailable.")
    elif not qs:
        lines.append("Quotes on file: none.")
    else:
        parts = [f"{(q.get('carrierName') or '').strip() or 'carrier?'} {q.get('productName') or ''} "
                 f"{_fmt_money(q.get('premium'))}{' (sold)' if q.get('sold') else ''}".strip() for q in qs[:6]]
        lines.append("Quotes on file (AgencyZoom keeps no quote date): " + "; ".join(parts) + ".")

    earlier = sorted(ctx.cards().get(lead_id, []), key=lambda c: c["day"], reverse=True)[:3]
    if earlier:
        lines.append("Earlier coaching cards on this lead:")
        for c in earlier:
            objs = ", ".join(sorted({o.get("group") or o.get("cat") or "" for o in c.get("objs") or []} - {""}))
            lines.append(f"    {c['day']} with {(c.get('who') or '').split(' ')[0]} -- {c.get('cat') or ''}: "
                         f"{(c.get('summary') or '').strip()[:300]}"
                         + (f" [objections: {objs}]" if objs else ""))
    else:
        lines.append(f"No earlier coaching card on this lead in the {WINDOW_DAYS} days before today.")

    notes, sent = [], []
    for lid in lead_ids:
        for n in lc.load_notes(lid):
            if str(n.get("createDate") or "")[:10] >= day or n.get("type") in SKIP_NOTE_TYPES:
                continue
            text = lc._text(n.get("body"))
            if not text:
                continue
            who = (n.get("createdBy") or "").strip() or "the lead or an automation"
            traq = TRAQ.search(text)
            kind = "TRAQ auto-summary of a past call" if traq else (n.get("type") or "note")
            when = str(n.get("createDate") or "")[:16]
            # Read over the whole note, before it is cut for the prompt.
            if not traq and not _automated(n) and quote_sent(text):
                kind += ", says a quote was sent"
                sent.append(when[:10])
            notes.append((when, kind, who, text[:NOTE_CHARS]))
    notes = sorted(set(notes), reverse=True)[:MAX_NOTES]
    if sent:
        lines.append(f"A note before today says a quote was sent to this lead (last {max(sent)}): the quote "
                     f"counts as PRESENTED, so `flow` is follow-up whatever the stage says.")
    if notes:
        lines.append("Recent notes before today, newest first:")
        for when, kind, who, text in notes:
            lines.append(f"    {when} {kind} by {who}: {text}")
    else:
        lines.append("No notes on the lead before today.")
    return _render(lines)


def _render(lines):
    return "Lead history (before today):\n" + "\n".join(l if l.startswith("    ") else f"- {l}" for l in lines)
