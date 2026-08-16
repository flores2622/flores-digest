"""Generators for the remaining report panels.

Markup mirrors the approved TEST 7 build exactly -- same classes, same table
scaffolding -- so the layout work in HANDOFF s9 is preserved. Only the values
change. Every caller must run assert_div_balance afterwards.
"""
import datetime as dt

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
    out = []
    for p in P3:
        m = M[p]
        total = m["call_volume"] or 1
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
            f'<div style="width:100.00%"><table role="presentation" cellpadding="0" '
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
           'day&rsquo;s outcomes. Every lead links to AgencyZoom.</div>')
    return sub + '<div class="stage-summary">' + "".join(cards) + '</div>'


# ---- Call Detail -----------------------------------------------------------
DOT_HEX = {"Crystal Mango": "#cc0000", "Lorena Gonzalez": "#9900ff",
           "Mike Olvera": "#0000ff"}


def _fmt_phone(e164):
    d = "".join(ch for ch in (e164 or "") if ch.isdigit())[-10:]
    return f"({d[:3]}) {d[3:6]}-{d[6:]}" if len(d) == 10 else (e164 or "")


def _row_colour(row):
    """Five-way Call Detail colour (HANDOFF s7).

    A quote presented verbally and never entered in AgencyZoom still counts for
    the colour, but does not feed Premium Quoted. A "recycled back from
    Smart-Cycle" move is a move OUT of the cycle and is not a dead outcome.
    """
    moves = " ".join(row.get("moves") or []).lower()
    note = (row.get("note") or "").lower()
    quoted = ("quote" in moves or "quoted" in note or "quote" in note)
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
    everything.sort(key=lambda x: -x[1]["seconds"])
    for p, r in everything:
        badge = ('<span class="badge-new" style="background:#9a988f;color:#fff">'
                 'duration only</span>' if r["basis"] == "duration only" else "")
        secs = r["seconds"] or 0
        note = r["note"] or ""
        if not note:
            note = ("Live contact established from the call recording; no "
                    "producer-written outcome in AgencyZoom.")
        elif r["basis"] == "recording":
            note = f"From the call recording: &ldquo;{note}&rdquo;"
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
