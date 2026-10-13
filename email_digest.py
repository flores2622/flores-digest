"""email_digest.py -- the nightly email, a reflection of the board.

Frank, 2026-10-13: "the email needs to be brought up to date ... it shouldnt
have its own rules or cards or anything, it should now be a reflection of the
board data and coaching info"; "more coaching focused"; "one per producer,
debbie gets the only the leaderboard".

Everything here is read from ONE published day document -- the same
`days/<day>.json` the board renders (publish_board.build) -- so an email
figure can never disagree with the board. No metric is computed here beyond
adding up what the document already holds; a rule about what a number means
lives in daily.py / digest_rows.py / coaching_cards.py and nowhere in this
file.

Three versions, from the same document (`jobs`):

  ops        Frank, Francisco, Veronica, Amanda (staff.json `digest: ops`):
             every producer's section, the team's objections, Left on the
             desk, the leaderboard -- and the Missed Call Audit PDF attached
             by daily.py.
  producer   each producer (staff.json `producer` + `digest: staff`): their
             own section only -- figures, Apollo's coaching card per
             conversation, their texts waiting on a reply -- then the team's
             objections and the leaderboard.
  front      anyone else on the staff digest (Debbie): the day's line and the
             leaderboard, nothing more.

A coaching card is one short block: who and what the call was for, Apollo's
outcome, the top strength, the top miss, one "Next time" line (the first
objection not overcome's fix, else the assume-the-quote fix) and the flag
categories -- the card's own verdicts, never re-judged. Each lead's name
opens its full card on the board (`#card/<day>/<lead_id>`, index.html).

Email-safe HTML: tables, inline styles for everything that must survive
Gmail, one <style> block under render_report's old 16 KB cap for the card
classes, no flex / grid / <details>. The body must stay under Gmail's
102,400-byte clip (digest_config.GMAIL_CLIP_BYTES): `fit` renders at three
levels of card detail and takes the first that fits, so a heavy day shortens
the cards rather than losing the email.

By hand, for a test copy of a published day:
    python3 email_digest.py 2026-10-12 --as ops --to frank@...
    python3 email_digest.py 2026-10-12 --as "Crystal Mango" --out out/x.html
"""
import argparse
import collections
import datetime as dt
import html as _html
import json
import pathlib
import re

import digest_config as cfg
import staff

ROOT = pathlib.Path(__file__).resolve().parent
AZ = staff.TZ
# The board's address (staff.json agency.board_url, deployment -- set per
# agency). Without it the email names leads without links.
BOARD_URL = (staff.AGENCY.get("board_url") or "").rstrip("/")
# Keep a margin under the clip: Resend adds headers and its own tracking.
BODY_LIMIT = cfg.GMAIL_CLIP_BYTES - 4_096

TIER = {"green": "#1d7a3a", "yellow": "#b8860b", "red": "#b3261e"}
_TONE = {"bad": "red", "neutral": "yellow", "good": "green"}
FLAG_TONE = {g: _TONE.get(t, "yellow") for g, t in cfg.FLAG_GROUPS.items()}
COLOR = {p["name"]: p.get("color") or "#8a877f" for p in staff.producers()}
# Light badge text on a pale producer colour (Coral's cyan, Sarahi's peach).
_DARK_INK = {"#00ffcf", "#ffb48c", "#baffff"}

STYLE = """<style>
.cw{padding:6px 22px 6px 22px}.card{border:1px solid #e3d9c6;border-radius:8px;background:#fff}
.ch{padding:9px 12px 4px 12px;font-size:13.5px}.ld{color:#1a1a1a;font-weight:800;text-decoration:none}.mt{color:#52514e;font-size:12px}
.oc{float:right;display:inline-block;background:#1a1a1a;color:#fff;border-radius:999px;padding:2px 9px;font-size:11px;margin-left:6px}
.cb{padding:2px 12px 0 12px;font-size:12.5px;line-height:1.45}.m2{margin-top:3px}.g{color:#1d7a3a}.r{color:#b3261e}.a{color:#8a6d3b}
.nt{margin-top:3px;background:#fbf6ea;border-radius:6px;padding:6px 8px}.cf{padding:4px 12px 9px 12px}
.fg{display:inline-block;border-radius:6px;padding:1px 7px;font-size:11px;margin:2px 4px 0 0}
.fr{background:#f9e0de;color:#8f1d16}.fy{background:#fbf0d2;color:#7a5a00}.fgr{background:#e4f3e8;color:#1d5a2c}
.sec{padding:16px 22px 6px 22px;border-top:2px solid #eee3d2}.h2{font-size:16px;font-weight:800}
.th{font-size:9.5px;line-height:1.15;color:#8a6d3b;text-transform:uppercase;padding:5px 3px;border-bottom:2px solid #eee3d2;vertical-align:bottom}
.td{padding:5px 3px;border-bottom:1px solid #eee3d2;font-size:11px;white-space:nowrap}
.pill{display:inline-block;color:#fff;border-radius:999px;padding:2px 9px;font-size:12px;font-weight:700}
.sub{font-size:12.5px;color:#52514e}.one{padding:3px 22px;font-size:12.5px}
</style>"""


def E(s):
    return _html.escape(str(s if s is not None else ""))


def money(v):
    return f"${(v or 0):,.0f}"


def hhmm(sec):
    sec = int(sec or 0)
    return f"{sec // 60}m {sec % 60:02d}s" if sec >= 60 else f"{sec}s"


def first(name):
    return str(name or "").split()[0] if name else ""


def clip(s, n):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def tri(v):
    """A card verdict: a [value, reason] pair, a bare value, or None."""
    if isinstance(v, (list, tuple)):
        return v[0] if v else None
    return v


def pct(n, d):
    return f"{round(100 * n / d)}%" if d else "—"


def slug(person):
    s = re.sub(r"[^a-z0-9]+", "", first(person["name"]).lower()) or "staff"
    return s


# ---------------------------------------------------------------------------
# What the document holds, read the way the board reads it
# ---------------------------------------------------------------------------

def _tier_style(doc, name, key, tier=None):
    t = tier or ((doc.get("tiers") or {}).get(name) or {}).get(key)
    return f' style="color:{TIER[t]};font-weight:700"' if t in TIER else ""


def hh_sold(doc, name=None):
    """Households sold, one per household per day, like the board's
    hhSoldSplit: the lead's household id, else its name."""
    keys = set()
    for r in (doc.get("rows") or {}).get("sold_leads") or []:
        if name and r.get("who") != name:
            continue
        k = (r.get("day") or doc.get("date") or "",
             f"h{r['household']}" if r.get("household") is not None
             else "n" + str(r.get("lead") or r.get("lead_id") or "").lower())
        keys.add(k)
    return len(keys)


def sendoff_counts(cards):
    """Sent the Quote, the leaderboard's way: calls where the producer
    offered on their own to send it, of the calls where a quote came up."""
    came = [c for c in cards if tri(c.get("sendoff"))]
    mine = [c for c in came if tri(c["sendoff"]) == "producer"]
    return len(mine), len(came)


def assumed_counts(cards):
    """Assumed the quote / asked for it, off each card's own verdict: a
    follow-up's up-front assumptive close, else `askq`. n/a counts neither."""
    yes = no = 0
    for c in cards:
        flow = (c.get("flow") or [""])[0]
        if flow == "follow-up" and isinstance(c.get("assume"), dict):
            v = tri(c["assume"].get("start"))
        else:
            v = tri(c.get("askq"))
        if v is True:
            yes += 1
        elif v is False:
            no += 1
    return yes, no


def next_time(card):
    """One line to say next time: the first objection not overcome's fix,
    else the assume-the-quote fix (the board's Quick coaching rule)."""
    for o in card.get("objs") or []:
        try:
            sc = float(o.get("score"))
        except (TypeError, ValueError):
            sc = None
        if sc is not None and sc < 8 and o.get("fix"):
            fx = o["fix"]
            fx = fx[0] if isinstance(fx, list) else fx
            return f"On “{clip(o.get('cat') or o.get('group'), 50)}”: {fx}"
    return card.get("askfix") or ""


def card_flags(card):
    """[(group, tone, Apollo's words)], each category once."""
    out, seen = [], set()
    groups = card.get("flag_groups") or []
    words = card.get("flags") or []
    for i, g in enumerate(groups):
        if not g or g in seen:
            continue
        seen.add(g)
        out.append((g, FLAG_TONE.get(g, "yellow"), words[i] if i < len(words) else ""))
    return out


def waiting_replies(doc, name=None):
    """Texts and emails still waiting on a reply (the Digest's Left on the
    desk): nobody answered, not an ack, not an opt-out."""
    rows = (doc.get("messages") or {}).get("replies") or []
    return [r for r in rows
            if not r.get("answered_by") and not r.get("ack") and not r.get("optout")
            and (not name or r.get("who") == name)]


def card_link(doc, card):
    lid = card.get("lead_id")
    if BOARD_URL and lid is not None:
        return f"{BOARD_URL}/#card/{doc.get('date')}/{lid}"
    return ""


# ---------------------------------------------------------------------------
# The pieces
# ---------------------------------------------------------------------------

def _badge(name, size=13):
    col = COLOR.get(name, "#8a877f")
    ink = "#1a1a1a" if col.lower() in _DARK_INK else "#fff"
    return (f'<span class="pill" style="background:{col};color:{ink};font-size:{size}px">'
            f'{E(name)}</span>')


def header(doc, kind, name=None):
    T = doc.get("totals") or {}
    cards = doc.get("calls") or []
    sold = hh_sold(doc)
    life = T.get("life") or 0
    line = (f'<b>{T.get("dials", 0)}</b> dials · <b>{T.get("live", 0)}</b> contacts '
            f'({T.get("rate", 0)}%) · <b>{T.get("hh", 0)}</b> HH / <b>{money(T.get("pq"))}</b> quoted · '
            f'<b>{sold}</b> HH / <b>{T.get("pol", 0)}</b> pol / <b>{money(T.get("ps"))}</b> sold'
            + (f' · <b>{life}</b> life' if life else "")
            + (f' · Apollo read <b>{len(cards)}</b> call{"s" if len(cards) != 1 else ""}'
               if kind != "front" else ""))
    who = {"ops": "Apollo's coaching digest", "producer": f"{first(name)}'s coaching digest",
           "front": "The sales leaderboard"}[kind]
    return (f'<tr><td style="padding:18px 22px 8px 22px">'
            f'<div style="font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:#8a6d3b;font-weight:700">'
            f'Pantheon · {E(who)}</div>'
            f'<div style="font-size:22px;font-weight:800;margin-top:4px">{E(doc.get("label") or doc.get("date"))}</div>'
            f'<div style="font-size:13px;color:#52514e;margin-top:6px">The team: {line}</div></td></tr>')


def _card_html(doc, card, col, level):
    n = {2: 170, 1: 90, 0: 0}[level]
    good = (card.get("good") or [[None, None]])[0] or [None, None]
    bad = (card.get("bad") or [[None, None]])[0] or [None, None]
    link = card_link(doc, card)
    lead = E(card.get("lead") or "Unknown lead")
    lead = f'<a href="{E(link)}" class="ld">{lead}</a>' if link else f'<span class="ld">{lead}</span>'
    meta = [card.get("time"), card.get("dur"), (card.get("flow") or [""])[0], card.get("direction")]
    if (card.get("call_count") or 1) > 1:
        meta.append(f"{card['call_count']} calls")
    meta = " · ".join(E(m) for m in meta if m)
    flags = "".join(
        f'<span class="fg f{ {"red": "r", "yellow": "y", "green": "gr"}[tone] }" title="{E(w)}">{E(g)}</span>'
        for g, tone, w in card_flags(card))
    if level == 0:
        return (f'<tr><td class="one"><b>{lead}</b> <span class="mt">· {meta}</span> '
                f'<span class="oc" style="float:none">{E(card.get("cat"))}</span> {flags}</td></tr>')
    body = []
    if good[0]:
        body.append(f'<div><b class="g">Strength</b> · <b>{E(good[0])}</b> — {E(clip(good[1], n))}</div>')
    if bad[0]:
        body.append(f'<div class="m2"><b class="r">Miss</b> · <b>{E(bad[0])}</b> — {E(clip(bad[1], n))}</div>')
    nt = next_time(card)
    if nt:
        body.append(f'<div class="nt"><b class="a">Next time</b> · {E(clip(nt, n + 40))}</div>')
    if not body and card.get("summary"):
        body.append(f'<div class="sub">{E(clip(card["summary"], n + 60))}</div>')
    return (f'<tr><td class="cw"><table role="presentation" cellpadding="0" cellspacing="0" width="100%" '
            f'class="card" style="border-left:4px solid {col}">'
            f'<tr><td class="ch">{lead}<span class="mt"> · {meta}</span>'
            f'<span class="oc">{E(card.get("cat"))}</span></td></tr>'
            f'<tr><td class="cb">{"".join(body)}</td></tr>'
            + (f'<tr><td class="cf">{flags}</td></tr>' if flags else "")
            + '</table></td></tr>')


def producer_section(doc, name, level=2, own=False):
    P = {p["name"]: p for p in doc.get("producers") or []}
    p = P.get(name)
    if not p:
        return ""
    cards = [c for c in (doc.get("calls") or []) if c.get("who") == name]
    sent, came = sendoff_counts(cards)
    ayes, ano = assumed_counts(cards)
    rp = p.get("coach") or {}
    rps = rp.get("sessions") or 0
    lb = doc.get("leaderboard") or {}
    order = lb.get("order") or []
    rank = f" · #{order.index(name) + 1}" if name in order else ""
    pts = (lb.get("points") or {}).get(name, 0)
    sold = hh_sold(doc, name)
    hh_style = _tier_style(doc, name, "pol", "green" if sold else None)
    tasks = (p.get("tasks") or {}).get("pct")
    tasks = f"{tasks:.0f}%" if isinstance(tasks, (int, float)) else "—"
    col = COLOR.get(name, "#8a877f")
    title = "Your day" if own else _badge(name)
    t = lambda key: _tier_style(doc, name, key)
    out = [f'''<tr><td class="sec">
 <table role="presentation" cellpadding="0" cellspacing="0" width="100%"><tr>
  <td class="h2">{title} <span class="sub" style="font-weight:400">{pts} pts{rank}</span></td>
  <td align="right" class="sub"><b{t("dials")}>{p.get("dials", 0)}</b> dials · <b{t("rate")}>{p.get("rate", 0)}%</b> contact · <b{t("hh")}>{p.get("hh", 0)}</b> HH / <b{t("pq")}>{money(p.get("pq"))}</b> quoted · <b{hh_style}>{sold}</b> HH / <b{t("ps")}>{money(p.get("ps"))}</b> sold{f' · <b>{p["life"]}</b> life' if p.get("life") else ""}</td>
 </tr></table>
 <div class="sub" style="margin-top:6px">Apollo heard <b>{len(cards)}</b> conversation{"" if len(cards) == 1 else "s"}{f" · sent the quote instead of presenting it <b>{sent} of {came}</b>" if came else ""}{f" · assumed the quote <b>{ayes}</b>, asked for it <b>{ano}</b>" if ayes or ano else ""} · role play <b{t("roleplay")}>{rp.get("roleplay", 0)}</b> ({rps} session{"" if rps == 1 else "s"}) · tasks <b{t("tasks")}>{tasks}</b> · utilization <b{t("util")}>{round(p.get("util") or 0)}%</b></div>
</td></tr>''']
    if not cards:
        out.append('<tr><td class="one" style="padding-bottom:10px">No recorded conversation long enough to coach.</td></tr>')
    for c in cards:
        out.append(_card_html(doc, c, col, level))
    return "".join(out)


def desk_section(doc, name=None, level=2):
    """Left on the desk -- every producer's (ops) or one producer's own."""
    waiting = waiting_replies(doc, name)
    mis = doc.get("misfiled") or []
    if name and not waiting:
        return ""
    show = {2: 8, 1: 5, 0: 3}[level]
    byw = collections.Counter(first(r.get("who")) for r in waiting)
    rows = "".join(
        f'<tr><td style="padding:4px 8px;font-size:12.5px;border-bottom:1px solid #eee3d2"><b>{E(r.get("lead"))}</b>'
        f'<span class="sub"> · {"" if name else E(first(r.get("who"))) + " · "}{E(r.get("at"))} · {E(r.get("channel"))}</span>'
        f'<div class="sub">“{E(clip(r.get("said"), 110))}”</div></td></tr>'
        for r in waiting[:show])
    title = "Your texts waiting on a reply" if name else "Left on the desk"
    count = (f'<b style="color:{"#b3261e" if waiting else "#1d7a3a"};font-size:18px">{len(waiting)}</b> '
             f'text{"" if len(waiting) == 1 else "s"} or email{"" if len(waiting) == 1 else "s"} waiting on a reply'
             + ("" if name or not byw else " · " + " · ".join(f"{n} {k}" for k, n in byw.most_common())))
    more = (f'<div class="sub" style="margin-top:4px">… and {len(waiting) - show} more on the board.</div>'
            if len(waiting) > show else "")
    misline = ("" if name else
               f'<div style="font-size:13px;margin-top:10px"><b style="color:{"#b3261e" if mis else "#1d7a3a"};font-size:18px">{len(mis)}</b> '
               f'open lead{"" if len(mis) == 1 else "s"} misfiled in “Pipeline”</div>')
    return (f'<tr><td class="sec"><div class="h2">{title}</div>'
            f'<div style="font-size:13px;margin-top:6px">{count}</div>'
            f'<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin-top:4px">{rows}</table>'
            f'{more}{misline}</td></tr>')


def team_section(doc):
    """What the team ran into: the objection groups and the wins and losses
    line, from the document's objcats and scan."""
    sc = doc.get("scan") or {}
    cards = doc.get("calls") or []
    fg = collections.Counter(g for c in cards for g, _, _ in card_flags(c))
    th = lambda t, al="right": f'<th align="{al}" class="th">{t}</th>'
    td = lambda t, al="right": f'<td align="{al}" class="td" style="font-size:12px">{t}</td>'
    rows = "".join(f"<tr>{td(E(g), 'left')}{td(r)}{td(w)}{td(pct(w, r))}</tr>"
                   for g, r, w in (doc.get("objcats") or [])[:8])
    if not rows:
        rows = f'<tr>{td("No objections heard today.", "left")}</tr>'
    n_ass = sc.get("assumed_open", 0)
    wl = (f'Wins and losses: of <b>{sc.get("of_first", 0)}</b> first and finish-quote calls, the quote was '
          f'<b>assumed {n_ass}</b> time{"" if n_ass == 1 else "s"} and <b>asked for {sc.get("asked_open", 0)}</b>; '
          f'<b>{sc.get("priced", 0)}</b> priced, <b>{sc.get("closed", 0)}</b> closed on the call, '
          f'<b>{sc.get("timeset", 0)}</b> set a dated next step.')
    flags = (" Flags today: " + " · ".join(f"<b>{E(g)}</b> {n}" for g, n in fg.most_common(5)) + "."
             if fg else "")
    return (f'<tr><td class="sec"><div class="h2">What the team ran into</div>'
            f'<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin-top:8px">'
            f'<tr>{th("Objection", "left")}{th("Raised")}{th("Overcome")}{th("Won")}</tr>{rows}</table>'
            f'<div class="sub" style="margin-top:8px">{wl}{flags}</div></td></tr>')


def leaderboard(doc):
    """The board's leaderboard, its own order, points and tiers. Sent the
    Quote, Closing and Texts / Emails are shown, not scored, as there."""
    P = {p["name"]: p for p in doc.get("producers") or []}
    T = doc.get("totals") or {}
    lb = doc.get("leaderboard") or {}
    order = [n for n in (lb.get("order") or []) if n in P] or list(P)
    points = lb.get("points") or {}
    cards = doc.get("calls") or []
    MP = (doc.get("messages") or {}).get("producers") or {}
    any_so = any(tri(c.get("sendoff")) for c in cards)
    th = lambda t, al="right": f'<th align="{al}" class="th">{t}</th>'

    def td(t, name=None, key=None, al="right", tier=None):
        return f'<td align="{al}" class="td"{_tier_style(doc, name, key, tier) if (name and key) or tier else ""}>{t}</td>'

    def closing(name, src):
        hh, pq, ps = src.get("hh") or 0, src.get("pq") or 0, src.get("ps") or 0
        sold = hh_sold(doc, name if name != "team" else None)
        a = 100 * sold / hh if hh else None
        b = 100 * ps / pq if pq else None
        tiers = (doc.get("tiers") or {}).get(name) or {}
        ta = tiers.get("closing_hh") or (cfg.tier("closing_ratio_pct", a) if a is not None else None)
        tb = tiers.get("closing_pq") or (cfg.tier("closing_ratio_pct", b) if b is not None else None)
        f = lambda v, t: (f'<span style="color:{TIER[t]};font-weight:700">' if t in TIER else "<span>") \
            + (f"{round(v)}%" if v is not None else "—") + "</span>"
        return f"{f(a, ta)} / {f(b, tb)}"

    rows = []
    sum_sent = sum_came = 0
    for name in order:
        p = P[name]
        mine = [c for c in cards if c.get("who") == name]
        sent, came = sendoff_counts(mine)
        sum_sent += sent
        sum_came += came
        m = MP.get(name) or {}
        sold = hh_sold(doc, name)
        rp = (p.get("coach") or {}).get("roleplay", 0)
        rows.append(
            "<tr>" + td(f'{_badge(first(name), 11)}<br><span class="sub" style="font-size:10.5px">{points.get(name, 0)} pts</span>', al="left")
            + td(rp, name, "roleplay") + td(p.get("dials", 0), name, "dials")
            + td(hhmm(p.get("talk")), name, "talk") + td(f'{p.get("rate", 0)}%', name, "rate")
            + td(f'<span{_tier_style(doc, name, "hh")}>{p.get("hh", 0)}</span> / <span{_tier_style(doc, name, "pq")}>{money(p.get("pq"))}</span>')
            + td(f'<span{_tier_style(doc, name, "pol", "green" if sold else None)}>{sold}</span> / <span{_tier_style(doc, name, "ps")}>{money(p.get("ps"))}</span>')
            + td(closing(name, p))
            + (td(f"{sent} of {came}" if came else "—") if any_so else "")
            + td(f'{m.get("texts", 0)} / {m.get("emails", 0)}')
            + td(f'{round(p.get("util") or 0)}%', name, "util") + "</tr>")
    tt = lambda k: _tier_style(doc, "team", k)
    sold_team = hh_sold(doc)
    texts = sum((MP.get(n) or {}).get("texts", 0) for n in order)
    emails = sum((MP.get(n) or {}).get("emails", 0) for n in order)
    rows.append(
        '<tr style="background:#f3ece0;font-weight:700">' + td("Team", al="left")
        + td(round(T.get("roleplay") or 0), tier=(doc.get("tiers") or {}).get("team", {}).get("roleplay"))
        + td(T.get("dials", 0), "team", "dials") + td(hhmm(T.get("talk")), "team", "talk")
        + td(f'{T.get("rate", 0)}%', "team", "rate")
        + td(f'<span{tt("hh")}>{T.get("hh", 0)}</span> / <span{tt("pq")}>{money(T.get("pq"))}</span>')
        + td(f'<span{_tier_style(doc, "team", "pol", "green" if sold_team else None)}>{sold_team}</span> / <span{tt("ps")}>{money(T.get("ps"))}</span>')
        + td(closing("team", T))
        + (td(f"{sum_sent} of {sum_came}" if sum_came else "—") if any_so else "")
        + td(f"{texts} / {emails}") + td(f'{round(T.get("util") or 0)}%', "team", "util") + "</tr>")
    return (f'<tr><td class="sec"><div class="h2">Leaderboard</div>'
            f'<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin-top:6px">'
            f'<tr>{th("Producer", "left")}{th("Role play")}{th("Dials")}{th("Avg talk")}{th("Contact")}'
            f'{th("HH / $ quoted")}{th("HH / $ sold")}{th("Closing")}{th("Sent quote") if any_so else ""}'
            f'{th("Texts / em.")}{th("Util")}</tr>{"".join(rows)}</table>'
            f'<div style="font-size:11px;color:#52514e;margin-top:6px">Colours are the board\'s own tiers. '
            f'Role play is the share of Apollo\'s checklist met in the producer\'s own sessions. '
            f'Closing is households sold over quoted, then premium. Sent the quote, closing and texts / emails are shown, not scored.</div>'
            f'</td></tr>')


def footer(kind):
    link = (f' <a href="{E(BOARD_URL)}/" style="color:#8a6d3b;font-weight:700">Open Pantheon</a>'
            if BOARD_URL else "")
    note = {"ops": "Every lead name opens its coaching card on the board. Attached: the Missed Call Audit.",
            "producer": "Every lead name opens your full coaching card on the board, with the recording and transcript.",
            "front": "The whole day is on the board."}[kind]
    return (f'<tr><td style="padding:12px 22px 18px 22px;border-top:1px solid #eee3d2;font-size:12px;color:#52514e">'
            f'{note}{link}</td></tr>')


# ---------------------------------------------------------------------------
# The three versions
# ---------------------------------------------------------------------------

def render(doc, kind, name=None, level=2):
    """One email's HTML. kind: ops / producer / front; name for a producer."""
    lb = doc.get("leaderboard") or {}
    P = [p["name"] for p in doc.get("producers") or []]
    order = [n for n in (lb.get("order") or []) if n in P] or P
    parts = [header(doc, kind, name)]
    if kind == "ops":
        for n in order:
            parts.append(producer_section(doc, n, level))
        parts.append(team_section(doc))
        parts.append(leaderboard(doc))
        parts.append(desk_section(doc, None, level))
    elif kind == "producer":
        parts.append(producer_section(doc, name, level, own=True))
        parts.append(desk_section(doc, name, level))
        parts.append(team_section(doc))
        parts.append(leaderboard(doc))
    else:
        parts.append(leaderboard(doc))
    parts.append(footer(kind))
    body = "".join(parts)
    title = E(f"{doc.get('label') or doc.get('date')} — Pantheon")
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{title}</title>{STYLE}</head>'
            f'<body style="margin:0;background:#f3ece0">'
            f'<div style="background:#f3ece0;padding:18px 0;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1a1a1a">'
            f'<table role="presentation" cellpadding="0" cellspacing="0" align="center" width="680" '
            f'style="width:680px;max-width:100%;background:#fffdf8;border:2px solid #d9cfbc;border-radius:12px">'
            f'{body}</table></div></body></html>')


def fit(doc, kind, name=None, log=print):
    """The first level of card detail whose body fits under Gmail's clip."""
    for level in (2, 1, 0):
        h = render(doc, kind, name, level)
        size = len(h.encode())
        if size < BODY_LIMIT:
            if level < 2:
                log(f"  email {kind}{' ' + first(name) if name else ''}: cards shortened "
                    f"(level {level}) to fit Gmail's clip -- {size:,} bytes")
            return h
    raise SystemExit(f"email {kind}: {size:,} bytes even with one-line cards -- over Gmail's clip")


def jobs(day, doc, audience="both", log=print):
    """[{key, kind, name, subject, to, html}] -- one email per recipient
    group, from staff.json: `ops` (digest: ops, together), each producer
    (digest: staff, their own), and the rest of the staff digest (front).
    `key` names the sent marker (data/sent_<day>_<key>.json)."""
    label = dt.date.fromisoformat(day).strftime("%b %-d, %Y")
    out = []
    if audience in ("ops", "both"):
        to = staff.digest_recipients("ops")
        if to:
            out.append({"key": "ops", "kind": "ops", "name": None,
                        "subject": f"Apollo's coaching digest — {label}", "to": to,
                        "html": fit(doc, "ops", log=log)})
    if audience in ("staff", "both"):
        names = {p["name"] for p in doc.get("producers") or []}
        for p in staff.active():
            if p.get("digest") != "staff" or not p.get("email"):
                continue
            if p.get("producer"):
                if p["name"] not in names:
                    log(f"  email: {p['name']} is not on {day}'s board -- no email")
                    continue
                out.append({"key": slug(p), "kind": "producer", "name": p["name"],
                            "subject": f"Your coaching digest — {label}", "to": [p["email"]],
                            "html": fit(doc, "producer", p["name"], log=log)})
            else:
                out.append({"key": slug(p), "kind": "front", "name": p["name"],
                            "subject": f"Sales leaderboard — {label}", "to": [p["email"]],
                            "html": fit(doc, "front", log=log)})
    keys = [j["key"] for j in out]
    if len(set(keys)) != len(keys):
        raise SystemExit(f"email: two recipients share a marker key -- {keys}")
    return out


def load_published(day):
    """The published day document from R2 (days/<day>.json) -- for a test
    copy of a day that already went out, the board's exact document."""
    import publish_board
    cli, bucket = publish_board._client()
    body = cli.get_object(Bucket=bucket, Key=f"days/{day}.json")["Body"].read()
    return json.loads(body)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("day")
    ap.add_argument("--as", dest="who", default="ops",
                    help="ops, front, or a producer's name")
    ap.add_argument("--to", nargs="*", default=[], help="send a test copy to these addresses")
    ap.add_argument("--out", help="write the HTML here instead of out/")
    ap.add_argument("--doc", help="a saved day document instead of R2's")
    a = ap.parse_args(argv)
    doc = json.loads(pathlib.Path(a.doc).read_text()) if a.doc else load_published(a.day)
    if a.who in ("ops", "front"):
        kind, name = a.who, None
    else:
        kind, name = "producer", a.who
        if name not in {p["name"] for p in doc.get("producers") or []}:
            raise SystemExit(f"{name!r} is not on {a.day}'s board")
    h = fit(doc, kind, name)
    out = pathlib.Path(a.out or f"out/email_{a.day}_{a.who.split()[0].lower()}.html")
    out.parent.mkdir(exist_ok=True)
    out.write_text(h)
    print(f"{out}: {len(h.encode()):,} bytes")
    if a.to:
        import send_digest
        label = dt.date.fromisoformat(a.day).strftime("%b %-d, %Y")
        subj = f"TEST — {kind} email for {label}" + (f" ({first(name)})" if name else "")
        send_digest.send(subj, h, a.to, binary=True)
        print(f"sent to {', '.join(a.to)}")


if __name__ == "__main__":
    main()
