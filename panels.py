"""Generators for the remaining report panels.

Markup mirrors the approved TEST 7 build exactly -- same classes, same table
scaffolding -- so the layout work in HANDOFF s9 is preserved. Only the values
change. Every caller must run assert_div_balance afterwards.
"""
import datetime as dt
import re

import digest_config as cfg
from render_report import DOT, TIER, hhmm, money

SHORT = {"Crystal Mango": "Crystal", "Lorena Gonzalez": "Lorena",
         "Mike Olvera": "Mike"}
P3 = ["Crystal Mango", "Lorena Gonzalez", "Mike Olvera"]


# ---- Task Completion Rate --------------------------------------------------
def task_table(tasks, audited):
    rows = []
    for p in P3:
        t = tasks["per_producer"][p]
        pct = t["pct"] or 0
        a = audited.get(p, pct)
        rows.append(
            f'<tr><td class="name-cell"><span class="dot {DOT[p]}"></span>'
            f'{SHORT[p]}</td><td class="num">{t["total"]}</td>'
            f'<td class="num">{t["completed"]}</td>'
            f'<td class="num"><span class="{TIER[cfg.tier("task_completion_pct", pct)]}">'
            f'{pct:.1f}%</span></td>'
            f'<td style="width:96px"><div class="sk" style="width:96px">'
            f'<span class="sf {DOT[p]}" style="width:{pct:.2f}%"></span></div></td>'
            f'<td class="num"><span class="{TIER[cfg.tier("task_completion_pct", a)]}">'
            f'{a:.1f}%</span></td></tr>')
    tm = tasks["team"]
    tp = tm["pct"] or 0
    ta = audited.get("TEAM", tp)
    rows.append(
        f'<tr><td class="name-cell"><b>Team Total</b></td>'
        f'<td class="num">{tm["total"]}</td><td class="num">{tm["completed"]}</td>'
        f'<td class="num"><span class="{TIER[cfg.tier("task_completion_pct", tp)]}">'
        f'{tp:.1f}%</span></td>'
        f'<td style="width:96px"><div class="sk" style="width:96px">'
        f'<span class="sf cE" style="width:{tp:.2f}%"></span></div></td>'
        f'<td class="num"><span class="{TIER[cfg.tier("task_completion_pct", ta)]}">'
        f'{ta:.1f}%</span></td></tr>')
    return ('<table><tr><th>Producer</th><th class="num">Due</th>'
            '<th class="num">Done</th><th class="num">Rate</th><th></th>'
            '<th class="num">Audited</th></tr>' + "".join(rows) + '</table>')


# ---- Call Outcome Breakdown ------------------------------------------------
# Segment order and colours follow the approved legend.
# Colours read off the approved build: cF green, cH amber, cD teal, cI grey,
# cG stone. Order matters -- the legend and the stacked bar must agree.
SEGMENTS = [("Live Contact", "cF"), ("Voicemail", "cH"), ("Screener", "cD"),
            ("No Answer", "cI"), ("No Outcome Logged", "cG")]


def outcome_rows(M):
    """Rows ranked by call volume, bars scaled ACROSS producers.

    Frank, 2026-08-18: "sort the bars by highest volume to lowest, by producer,
    and scale the bars to show the highest quantity as a full bar, and smaller
    bars for the producers with lower calls."

    So the busiest producer's bar runs the full width and everyone else is drawn
    to the same scale -- the row length is itself the volume comparison. Segment
    order inside each bar stays the canonical legend order.
    """
    out = []
    busiest = max((M[p]["call_volume"] for p in P3), default=0) or 1
    for p in sorted(P3, key=lambda q: -M[q]["call_volume"]):
        m = M[p]
        total = m["call_volume"] or 1
        row_pct = m["call_volume"] / busiest * 100
        cells, bars = [], []
        for name, colour in SEGMENTS:
            n = m["outcomes"].get(name, 0)
            if not n:
                continue
            pct = n / total * 100
            cells.append(f'<td style="width:{pct:.2f}%">{n}</td>')
            bars.append(f'<span class="og {colour}" style="width:{pct:.2f}%"></span>')
        out.append(
            f'<div class="outcome-row"><div class="outcome-row-head">'
            f'<span class="rep-name"><span class="dot {DOT[p]}"></span>{SHORT[p]}</span>'
            f'<span class="total">{m["call_volume"]} new-business dials</span></div>'
            f'<div style="width:{row_pct:.2f}%"><table role="presentation" cellpadding="0" '
            f'cellspacing="0" class="outcome-label-table"><tr>{"".join(cells)}</tr></table>'
            f'<div class="outcome-track">{"".join(bars)}</div></div></div>')
    legend = ('<div class="oc-legend">' + "".join(
        f'<span class="item"><span class="dot {c}"></span>{n}</span>'
        for n, c in SEGMENTS) + '</div>')
    return "".join(out) + legend


# ---- Speed to Dial ---------------------------------------------------------
def _s2d_card(name, d):
    if not d:
        return (f'<div class="s2d-card"><div class="rep">'
                f'<span class="dot {DOT[name]}"></span>{SHORT.get(name, name)}</div>'
                f'<div class="big">&mdash;</div>'
                f'<div class="med-label">no internet leads assigned</div>'
                f'<div class="stats"><div class="stat">Quickest<b>&mdash;</b></div>'
                f'<div class="stat">Longest<b>&mdash;</b></div></div></div>')
    med = d["median"]
    klass = TIER[cfg.tier("speed_to_dial_min", med / 60)]
    val = f'{med}<span class="unit">s</span>' if med < 60 else hhmm(med)
    q = hhmm(d["quickest"]) if d.get("quickest") else "&mdash;"
    lo = hhmm(d["longest"]) if d.get("longest") else "&mdash;"
    return (f'<div class="s2d-card"><div class="rep">'
            f'<span class="dot {DOT.get(name, "cE")}"></span>{SHORT.get(name, name)}</div>'
            f'<div class="big {klass}">{val}</div>'
            f'<div class="med-label">median speed to dial</div>'
            f'<div class="stats"><div class="stat">Quickest<b>{q}</b></div>'
            f'<div class="stat">Longest<b>{lo}</b></div></div></div>')


def speed_table(s2d, team):
    cards = [_s2d_card(p, s2d.get(p)) for p in P3] + [_s2d_card("Team", team)]
    pads = ['0 8px 12px 0', '0 0 12px 8px', '0 8px 12px 0', '0 0 12px 8px']
    cells = [f'<td valign="top" style="width:50%;border-bottom:none;padding:{pads[i]}">'
             f'{c}</td>' for i, c in enumerate(cards)]
    return ('<table role="presentation" cellpadding="0" cellspacing="0" '
            'style="width:100%;border-collapse:collapse;table-layout:fixed">'
            f'<tr>{cells[0]}{cells[1]}</tr><tr>{cells[2]}{cells[3]}</tr></table>')


# ---- Coaching & Call Quality ----------------------------------------------
def coach_cards(coach):
    def bar(p, label, val, lo, hi):
        pct = max(0.0, min(100.0, (val - lo) / (hi - lo) * 100)) if hi > lo else 0
        return (f'<div class="ss"><div class="sl">{label}</div>'
                f'<table role="presentation" cellpadding="0" cellspacing="0" class="st">'
                f'<tr><td><div class="sk"><div class="sf {DOT[p]}" '
                f'style="width:{pct:.2f}%"></div></div></td>'
                f'<td class="sy"><span class="sv">{val}</span></td></tr></table></div>')

    def col(p):
        c = coach[p]
        r = cfg.COACH_BAR_RANGES
        return (f'<div class="lb-col"><div class="rep">'
                f'<span class="dot {DOT[p]}"></span>{p}</div>'
                + bar(p, "Avg Call Score", c["score"], *r["Avg Call Score"])
                + bar(p, "Avg Sentiment", c["sentiment"], *r["Avg Sentiment"])
                + bar(p, "Role Play", c["roleplay"], *r["Role Play"])
                + '</div>')
    a, b, d = (col(p) for p in P3)
    return ('<table role="presentation" cellpadding="0" cellspacing="0" '
            'style="width:100%;border-collapse:collapse;table-layout:fixed">'
            f'<tr><td valign="top" style="width:50%;border-bottom:none;'
            f'padding:0 6px 12px 0">{a}</td>'
            f'<td valign="top" style="width:50%;border-bottom:none;'
            f'padding:0 0 12px 6px">{b}</td></tr>'
            f'<tr><td valign="top" colspan="2" style="border-bottom:none;'
            f'padding:0">{d}</td></tr></table>')


# ---- Team Leaderboard ------------------------------------------------------
def leaderboard(M, coach):
    cats = []
    def vals(key, fn):
        return {p: fn(M[p], coach[p]) for p in P3}
    cats.append(("Role Play", vals(None, lambda m, c: c["roleplay"]), lambda v: str(v)))
    cats.append(("Call Volume", vals(None, lambda m, c: m["call_volume"]), str))
    cats.append(("Avg Talk Time", vals(None, lambda m, c: m["avg_talk"]), hhmm))
    cats.append(("Avg Sentiment", vals(None, lambda m, c: c["sentiment"]), str))
    cats.append(("Avg Call Score", vals(None, lambda m, c: c["score"]), str))
    cats.append(("Contact Rate", vals(None, lambda m, c: m["contact_rate"]),
                 lambda v: f"{v}%"))
    cats.append(("Households Quoted", vals(None, lambda m, c: m["households_quoted"]), str))
    cats.append(("Premium Quoted", vals(None, lambda m, c: m["premium_quoted"]), money))
    cats.append(("Premium Sold", vals(None, lambda m, c: m["premium_sold"]), money))

    points = {p: 0 for p in P3}
    rows = []
    for name, v, fmt in cats:
        order = sorted(P3, key=lambda p: -v[p])
        pts = {}
        rank = 0
        for i, p in enumerate(order):
            # Zero-activity override: no recorded activity scores 0, not a rank.
            pts[p] = 0 if not v[p] else cfg.LEADERBOARD_POINTS[i]
            points[p] += pts[p]
        cells = "".join(
            f'<td class="num"><span class="pb">{pts[p]}'
            f'{"pt" if pts[p] == 1 else "pts"}</span>'
            f'<span class="pv">{fmt(v[p])}</span></td>' for p in P3)
        rows.append(f'<tr><td>{name}</td>{cells}</tr>')

    def tiebreak(p):
        return (points[p], M[p]["premium_sold"], M[p]["households_quoted"],
                M[p]["call_volume"])
    standing = sorted(P3, key=tiebreak, reverse=True)
    top = max(points.values()) or 1
    medals = ["gold", "silver", "bronze"]
    podium = "".join(
        f'<table role="presentation" cellpadding="0" cellspacing="0" '
        f'class="mvp-row-table mvp-{i + 1}"><tr>'
        f'<td class="mvp-medal-cell" style="width:38px;padding-right:12px">'
        f'<div class="mvp-medal {medals[i]}">{i + 1}</div></td>'
        f'<td class="mvp-name-cell">{p}</td>'
        f'<td><div class="mvp-track"><div class="mvp-fill {DOT[p]}" '
        f'style="width:{points[p] / top * 100:.2f}%"></div></div></td>'
        f'<td class="mvp-pts-cell">{points[p]} pts</td></tr></table>'
        for i, p in enumerate(standing))
    head = ("<thead><tr><th>Category</th>" +
            "".join(f'<th class="num">{SHORT[p]}</th>' for p in P3) + "</tr></thead>")
    total = ('<tr><td><b>Total Points</b></td>' +
             "".join(f'<td class="num"><b>{points[p]} pts</b></td>' for p in P3) +
             "</tr>")
    return (f'<div class="mvp-podium">{podium}</div>'
            f'<div class="table-scroll"><table>{head}<tbody>'
            f'{"".join(rows)}{total}</tbody></table></div>')


# ---- Recontact Struggle ----------------------------------------------------
def _lead_link(lid, name):
    return (f'<a class="lead-link" href="https://app.agencyzoom.com/lead?id&#61;{lid}" '
            f'target="_blank">{name}</a>')


def recontact_cards(rc, attachment):
    """Row shape copied from the approved build:

        <div class="row"><span><a>NAME</a><i> &mdash; stage</i></span>
        <b>in stage since ... &middot; 4bd &middot; 0 calls</b></div>

    Two SIBLINGS -- the name block and the meta block. Nesting the meta inside
    the name span made it render first, ahead of the lead it describes.
    """
    def d(x):
        return dt.date.fromisoformat(str(x)).strftime("%b %-d") if x else "?"

    cards = []
    for p in P3:
        risk = [r for r in rc["at_risk"] if r["producer"] == p]
        lost = [r for r in rc["lost"] if r["producer"] == p]
        paused = [r for r in rc.get("paused", []) if r["producer"] == p]
        won = [r for r in rc["won"] if r["producer"] == p]
        body = (f'<div class="rep" style="font-size:12.5px;font-weight:700;'
                f'margin-bottom:2px"><span class="dot {DOT[p]}"></span>{SHORT[p]}</div>')

        groups = [
            (f'At risk &mdash; {len(risk)}', risk,
             lambda r: (r["stage"],
                        f'in stage since {d(r["entered"])} &middot; '
                        f'{r["business_days"]}bd &middot; {r["calls"]} calls')),
            (f'Lost &mdash; {len(lost)}', lost,
             lambda r: (r["stage"],
                        f'{d(r["entered"])} &rarr; {d(r["outcome_date"])} '
                        f'&middot; {r["days"]}d &middot; {r["calls"]} calls')),
            (f'On pause &mdash; {len(paused)}', paused,
             lambda r: (r["stage"],
                        f'smart cycle returns {d(r["returns"])} '
                        f'&middot; in {r["returns_in"]}d '
                        f'&middot; {r["calls"]} calls')),
            (f'Won &mdash; {len(won) if won else "none"}', won,
             lambda r: (r.get("stage", "Sold"), d(r.get("outcome_date")))),
        ]
        for title, items, meta in groups:
            body += (f'<div class="title" style="font-size:11px;'
                     f'margin:8px 0 4px">{title}</div>')
            shown = items[:cfg.INLINE_RECONTACT_PER_GROUP]
            for r in shown:
                stage, tail = meta(r)
                body += (
                    f'<div class="row" style="padding:2px 0;font-size:11.5px">'
                    f'<span>{_lead_link(r["lead_id"], r["lead_name"])}'
                    f'<i style="color:#86847d;font-style:normal"> &mdash; '
                    f'{stage}</i></span>'
                    f'<b style="font-weight:600;color:#52514e">{tail}</b></div>')
            if not shown:
                body += ('<div class="empty-row" style="font-size:11.5px">'
                         'none</div>')
            elif len(items) > len(shown):
                body += (f'<div class="row" style="padding:2px 0;font-size:11px;'
                         f'color:#86847d">and {len(items) - len(shown)} more '
                         f'&mdash; full list with dates and call counts in '
                         f'{attachment}</div>')
        cards.append(f'<div class="stage-card">{body}</div>')

    sub = ('<div class="panel-subtitle">At risk of going cold: more than 3 '
           'business days since the last stage move, or more than 3 dials since '
           'entering the stage, with no outcome yet. Lost and won are that '
           'day&rsquo;s outcomes. A smart cycle returning within 29 days is a '
           'pause, not a loss. Every lead links to AgencyZoom.</div>')
    return sub + '<div class="stage-summary">' + "".join(cards) + '</div>'


# ---- Call Detail -----------------------------------------------------------
DOT_HEX = {"Crystal Mango": "#cc0000", "Lorena Gonzalez": "#9900ff",
           "Mike Olvera": "#0000ff"}


def _fmt_phone(e164):
    d = "".join(ch for ch in (e164 or "") if ch.isdigit())[-10:]
    return f"({d[:3]}) {d[3:6]}-{d[6:]}" if len(d) == 10 else (e164 or "")


def _outcome_rank(row):
    """Call Detail sort key: the five-way outcome, best first.

    Matches the colour bands in _row_colour so the table reads top to bottom as
    sold -> quoted -> dead-with-quote -> dead -> live-no-quote.
    """
    order = {"one_call_close": 0, "quote_no_action": 1, "dead_with_quote": 2,
             "dead_no_quote": 3, "live_no_quote": 4}
    inv = {v: k for k, v in cfg.CALL_ROW_COLORS.items()}
    return order.get(inv.get(_row_colour(row), "live_no_quote"), 4)


def _row_colour(row):
    """Five-way Call Detail colour (HANDOFF s7).

    A quote presented verbally and never entered in AgencyZoom still counts for
    the colour, but does not feed Premium Quoted. A "recycled back from
    Smart-Cycle" move is a move OUT of the cycle and is not a dead outcome.
    """
    moves = " ".join(row.get("moves") or []).lower()
    note = (row.get("note") or "").lower()
    # Match the STAGE, not the pipeline -- same trap already fixed in the
    # households-quoted count. "1-2 Leads Not Quoted" is the pipeline leads are
    # recycled into when they were NEVER quoted, and a bare "quote" substring
    # test reads it as a quote. Frank, 2026-08-17: Lazaro Rueda showed red.
    stages = " ".join(seg.split("|")[-1] for seg in
                      re.split(r"\s+to\s+", moves) if seg)
    quoted = ("quote" in stages or "quote" in note)
    dead = ("dead" in moves or "smart-cycle" in moves)
    sold = "sold" in moves or "sold" in note
    if quoted and sold:
        return cfg.CALL_ROW_COLORS["one_call_close"]
    if dead and quoted:
        return cfg.CALL_ROW_COLORS["dead_with_quote"]
    if dead:
        return cfg.CALL_ROW_COLORS["dead_no_quote"]
    if quoted:
        return cfg.CALL_ROW_COLORS["quote_no_action"]
    return cfg.CALL_ROW_COLORS["live_no_quote"]


def call_detail(M, day):
    rows = []
    everything = []
    for p in P3:
        for r in M[p]["call_detail"]:
            everything.append((p, r))
    # Producer first, then call outcome, then longest call (Frank, 2026-08-17).
    # Was a single global sort on duration, which interleaved the three reps.
    everything.sort(key=lambda x: (P3.index(x[0]), _outcome_rank(x[1]),
                                   -x[1]["seconds"]))
    for p, r in everything:
        badge = ('<span class="badge-new" style="background:#9a988f;color:#fff">'
                 'duration only</span>' if r["basis"] == "duration only" else "")
        secs = r["seconds"] or 0
        # Frank, 2026-08-17: "give me a summary of the transcribed portion of
        # the call recording when avail, and a copy of the notes when not."
        rec_txt = (r.get("note_recording") or "").strip()
        prod_txt = (r.get("note_producer") or r.get("note") or "").strip()
        if rec_txt:
            note = f"From the call recording: &ldquo;{rec_txt}&rdquo;"
            if prod_txt:
                note += f'<br><span style="color:#86847d">Producer note: {prod_txt}</span>'
        elif prod_txt:
            note = f"Producer note: {prod_txt}"
        else:
            note = ("Live contact established from the call recording; no "
                    "producer-written outcome in AgencyZoom.")
        link = (_lead_link(r["lead_id"], r["lead"]) if r["lead_id"]
                else (r["lead"] or _fmt_phone(r["number"])))
        rows.append(
            f'<tr style="background:{_row_colour(r)}">'
            f'<td class="name-cell"><span class="dot" '
            f'style="background:{DOT_HEX[p]}"></span>{SHORT[p]}</td>'
            f'<td>{link}{badge}</td>'
            f'<td class="nowrap-cell">{_fmt_phone(r["number"])}</td>'
            f'<td class="num nowrap-cell">{secs // 60}:{secs % 60:02d}</td>'
            f'<td class="note-cell">{note}</td></tr>')
    legend = ('<div class="row-legend">' + "".join(
        f'<span class="item"><span class="row-swatch" style="background:{c}"></span>{t}</span>'
        for c, t in [
            (cfg.CALL_ROW_COLORS["one_call_close"],
             "One-call close &mdash; quote presented AND the sale closed on the same call"),
            (cfg.CALL_ROW_COLORS["quote_no_action"],
             "Quote presented, no action yet &mdash; not sold, not dead/smart-cycled"),
            (cfg.CALL_ROW_COLORS["dead_with_quote"],
             "Marked dead/smart-cycled WITH a quote presented"),
            (cfg.CALL_ROW_COLORS["dead_no_quote"],
             "Marked dead/smart-cycled with NO quote presented"),
            (cfg.CALL_ROW_COLORS["live_no_quote"],
             "Live contact, no quote, no dead/smart-cycle outcome")]) + '</div>')
    return ('<table><thead><tr><th>Rep</th><th>Lead Name (AZ)</th><th>Phone</th>'
            '<th class="num">Duration</th><th>Note</th></tr></thead><tbody>'
            + "".join(rows) + '</tbody></table>' + legend)


# ---- Task Completion Audit -------------------------------------------------
# Generated per day. This block used to be static HTML in the template, so the
# same two exceptions shipped every day from 2026-08-12 (Frank, 2026-08-18).
AZ_URL = {"lead": "https://app.agencyzoom.com/lead?id&#61;{}",
          "customer": "https://app.agencyzoom.com/customer?id&#61;{}"}


def _az_link(kind, rid, name):
    """Same treatment Call Detail gives lead names, for tasks."""
    name = name or "&mdash;"
    if not kind or not rid:
        return name
    return (f'<a class="lead-link" href="{AZ_URL[kind].format(rid)}" '
            f'target="_blank">{name}</a>')


def _record_cell(r):
    return (f'<td class="nowrap-cell">{_az_link(r["link_kind"], r["link_id"], r["record"])}'
            f'<span class="sq">{r["link_kind"] or "&mdash;"}</span></td>')


def _clip(t, n=190):
    t = (t or "").strip()
    return (t[:n] + "&hellip;") if len(t) > n else (t or "&mdash;")



def _activity_cell(r):
    """Every AgencyZoom touch that day, not just the phone."""
    kinds = r.get("activity") or []
    if kinds:
        return (f'<span class="tier-text-good">{", ".join(kinds)}</span>')
    if r.get("call_on_record") == "yes":
        return '<span class="tier-text-good">call</span>'
    if r.get("call_on_record") == "no number":
        return '<span class="tier-text-warning">no number on file</span>'
    return '<span class="tier-text-critical">none</span>'


def _why_cell(r):
    """Loss reason and the lead's own reply outrank the canned task text."""
    bits = []
    if r.get("loss_reason"):
        bits.append(f'<b>{r["loss_reason"]}</b>')
    for msg in (r.get("inbound") or [])[:1]:
        bits.append(f'Lead replied: &ldquo;{_clip(msg, 150)}&rdquo;')
    if r.get("move_comment") and not r.get("inbound"):
        bits.append(f'Producer: &ldquo;{_clip(r["move_comment"], 150)}&rdquo;')
    if not bits:
        bits.append(_clip(r.get("comment")))
    return " &middot; ".join(bits)

def task_audit_tables(audit, label):
    def title(letter, text, n, suffix=""):
        return (f'<div class="section-title">({letter}) {text} &mdash; '
                f'{n} found{suffix}</div>')

    def empty(msg):
        # A clear section should LOOK clear at a glance (Frank, 2026-08-18).
        # Inline styles, not classes: the ops report is read in Gmail, which
        # strips or ignores <style> rules often enough not to rely on them.
        return ('<div style="display:flex;align-items:center;gap:10px;'
                'padding:10px 12px;margin:2px 0 4px;background:#DCFCE7;'
                'border:1px solid #4ADE80;border-radius:6px">'
                '<span style="color:#0ca30c;font-size:18px;font-weight:700;'
                'line-height:1">&#10004;</span>'
                f'<span style="font-size:12.5px;color:#166534">{msg}</span></div>')

    out = []

    # (a) completed on a call that is not in the call log
    out.append(title("a", "Completed on the strength of a call that is not in "
                          "the call log", len(audit["a"])))
    if audit["a"]:
        rows = "".join(
            f'<tr><td class="name-cell">{SHORT[r["producer"]]}</td>'
            f'{_record_cell(r)}<td class="note-cell">{_clip(r["comment"])}</td>'
            f'<td class="nowrap-cell">{_fmt_phone(r["number"])}</td></tr>'
            for r in audit["a"])
        out.append('<table><tr><th>Rep</th><th>Household</th><th>Comment</th>'
                   f'<th>Number on file</th></tr>{rows}</table>')
    else:
        out.append(empty(
            f'Every producer task due {label} whose comment reports a call has '
            f'a matching dial in the RingCentral log.'))

    # (b) closed after the due date
    out.append(title("b", "Closed noticeably after the due date", len(audit["b"])))
    if audit["b"]:
        rows = "".join(
            f'<tr><td class="name-cell">{SHORT[r["producer"]]}</td>'
            f'{_record_cell(r)}<td>{r["title"]}</td>'
            f'<td class="num">{r["due"]}</td><td class="num">{r["completed"]}</td>'
            f'<td class="num">{r["days_late"]}</td></tr>' for r in audit["b"])
        out.append('<table><tr><th>Rep</th><th>Linked record</th><th>Task</th>'
                   '<th class="num">Due</th><th class="num">Completed</th>'
                   f'<th class="num">Days late</th></tr>{rows}</table>')
    else:
        out.append(empty(f'No producer task due {label} was completed '
                         f'materially after its due date.'))

    # (c) reschedule-shaped modifications
    out.append(title("c", "Due date was changed", len(audit["c"])))
    if audit["c"]:
        rows = "".join(
            f'<tr><td class="name-cell">{SHORT[r["producer"]]}</td>'
            f'{_record_cell(r)}<td>{r["title"]}</td>'
            f'<td class="nowrap-cell">{r["created"][:10]}</td>'
            f'<td class="nowrap-cell">{r["modified"][:10]}</td>'
            f'<td class="nowrap-cell">{r["due"]}</td></tr>' for r in audit["c"])
        out.append('<table><tr><th>Rep</th><th>Linked record</th><th>Task</th>'
                   '<th>Created</th><th>Last modified</th><th>Due</th></tr>'
                   f'{rows}</table>'
                   '<div class="footnote">AgencyZoom exposes when a task was '
                   'last modified but not which field changed, so these are '
                   'tasks altered on a later day than they were created &mdash; '
                   'the shape of a reschedule, not a confirmed due-date edit.</div>')
    else:
        out.append(empty(f'No producer task due {label} was modified after the '
                         f'day it was created.'))

    # (d) cancelled rather than completed
    out.append(title("d", "Cancelled rather than completed", len(audit["d"]),
                     ", all counted against the rate"))
    if audit["d"]:
        rows = "".join(
            f'<tr><td class="name-cell">{SHORT[r["producer"]]}</td>'
            f'<td>{r["title"]}</td>{_record_cell(r)}'
            f'<td>{_activity_cell(r)}</td>'
            f'<td class="note-cell">{_why_cell(r)}</td></tr>'
            for r in audit["d"])
        out.append('<table><tr><th>Rep</th><th>Task</th><th>Linked record</th>'
                   '<th>Activity that day</th><th>Why / instruction</th></tr>'
                   f'{rows}</table>')
    else:
        out.append(empty(f'No producer task due {label} was cancelled.'))

    return "".join(out)
