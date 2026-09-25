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


def direction(group):
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
    return (text + " -- the producer ANSWERED an inbound call, so score `greeting`. "
            "Who dialled is not the flow: decide `flow` from the stage and the history")


class Context:
    """Per-day sources, loaded once per coaching build and only when a card
    is being read."""

    def __init__(self, day, log=print):
        self.day = day
        self.log = log
        self._dials = None
        self._cards = None
        self._az = None

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


def block(group, day, ctx):
    """The "Lead history" text for one card's rows."""
    lines = [f"Today's call: {direction(group)}."]
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

    qs = ctx.quotes(lead_id)
    if qs is None:
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

    notes = []
    for lid in lead_ids:
        for n in lc.load_notes(lid):
            if str(n.get("createDate") or "")[:10] >= day or n.get("type") in SKIP_NOTE_TYPES:
                continue
            text = lc._text(n.get("body"))
            if not text:
                continue
            who = (n.get("createdBy") or "").strip() or "the lead or an automation"
            kind = "TRAQ auto-summary of a past call" if TRAQ.search(text) else (n.get("type") or "note")
            notes.append((str(n.get("createDate") or "")[:16], kind, who, text[:NOTE_CHARS]))
    notes = sorted(set(notes), reverse=True)[:MAX_NOTES]
    if notes:
        lines.append("Recent notes before today, newest first:")
        for when, kind, who, text in notes:
            lines.append(f"    {when} {kind} by {who}: {text}")
    else:
        lines.append("No notes on the lead before today.")
    return _render(lines)


def _render(lines):
    return "Lead history (before today):\n" + "\n".join(l if l.startswith("    ") else f"- {l}" for l in lines)
