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
         "Mike Olvera": "Mike", "Coral Barwick": "Coral",
         "Sarahi Chin": "Sarahi"}
# Historical name -- it was three producers until 2026-08-24, when Coral and
# Sarahi were added and it became five. Derived from the roster now so adding or
# removing a producer is a digest_config change only. Every panel below iterates
# it; none may assume a length.
P3 = list(cfg.PRODUCERS)


def _pts(v):
    """Point values as people write them: 30 not 30.0, 12.5 not 12.50.

    Needed once the scheme went to 3-2-1-.5-0 (Frank, 2026-08-24) and totals
    stopped being whole numbers.
    """
    return f"{v:g}"


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
    """Two cards per row, producers then Team. Was a fixed 2x2 for three
    producers plus Team; now any count, with the padding alternating left/right
    exactly as the approved layout did and the bottom row losing its 12px gap.
    An odd card out spans both columns rather than leaving a ragged half-width
    cell, which is how the Coaching panel handles the same situation."""
    cards = [_s2d_card(p, s2d.get(p)) for p in P3] + [_s2d_card("Team", team)]
    rows = []
    for i in range(0, len(cards), 2):
        pair = cards[i:i + 2]
        pad_b = "0" if i + 2 >= len(cards) else "12px"
        if len(pair) == 2:
            rows.append(
                f'<tr><td valign="top" style="width:50%;border-bottom:none;'
                f'padding:0 8px {pad_b} 0">{pair[0]}</td>'
                f'<td valign="top" style="width:50%;border-bottom:none;'
                f'padding:0 0 {pad_b} 8px">{pair[1]}</td></tr>')
        else:
            rows.append(
                f'<tr><td valign="top" colspan="2" style="border-bottom:none;'
                f'padding:0 0 {pad_b} 0">{pair[0]}</td></tr>')
    return ('<table role="presentation" cellpadding="0" cellspacing="0" '
            'style="width:100%;border-collapse:collapse;table-layout:fixed">'
            + "".join(rows) + '</table>')


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
    # Two columns per row, any producer count. An odd producer out spans both
    # columns on the final row, which is exactly how the approved three-producer
    # layout behaved -- so the two-per-row rhythm and padding are preserved.
    cols = [col(p) for p in P3]
    rows = []
    for i in range(0, len(cols), 2):
        pair = cols[i:i + 2]
        last = i + 2 >= len(cols)
        pad_b = "0" if last else "12px"
        if len(pair) == 2:
            rows.append(
                f'<tr><td valign="top" style="width:50%;border-bottom:none;'
                f'padding:0 6px {pad_b} 0">{pair[0]}</td>'
                f'<td valign="top" style="width:50%;border-bottom:none;'
                f'padding:0 0 {pad_b} 6px">{pair[1]}</td></tr>')
        else:
            rows.append(
                f'<tr><td valign="top" colspan="2" style="border-bottom:none;'
                f'padding:0 0 {pad_b} 0">{pair[0]}</td></tr>')
    return ('<table role="presentation" cellpadding="0" cellspacing="0" '
            'style="width:100%;border-collapse:collapse;table-layout:fixed">'
            + "".join(rows) + '</table>')


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
    def place(i):
        """Points for finishing i-th. Beyond the scheme, zero -- never IndexError."""
        return cfg.LEADERBOARD_POINTS[i] if i < len(cfg.LEADERBOARD_POINTS) else 0

    for name, v, fmt in cats:
        order = sorted(P3, key=lambda p: -v[p])
        pts = {}
        # Ties take the LOWEST place they occupy (Frank, 2026-08-25: "if they
        # tie, lower the score"). On the 5-4-3-2-1 scale a three-way tie for
        # first is all three on 3 pts -- places 1, 2 and 3 are consumed and the
        # worst of them is what pays -- then 2, then 1. A two-way tie for first
        # is 4 pts each, then 3, 2, 1.
        #
        # This REVERSES the 08-24 rule, where a tie took the BEST place it
        # occupied (three tied at the top were all "first"). Same walk, one index
        # changed: place(j) instead of place(i).
        #
        # Before either rule, ties were broken silently by roster order: three
        # producers all scoring 81 on role play took 3, 2 and 1 points, and
        # whoever sat last in the roster was penalised for an identical result.
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            best = place(j)
            for q in order[i:j + 1]:
                # Zero-activity override: no recorded activity scores 0, not a
                # rank -- it still consumes its place, so a zero never promotes
                # anyone behind it.
                pts[q] = 0 if not v[q] else best
                points[q] += pts[q]
            i = j + 1
        cells = "".join(
            f'<td class="num"><span class="pb">{_pts(pts[p])}'
            f'{"pt" if pts[p] == 1 else "pts"}</span>'
            f'<span class="pv">{fmt(v[p])}</span></td>' for p in P3)
        rows.append(f'<tr><td>{name}</td>{cells}</tr>')

    def tiebreak(p):
        return (points[p], M[p]["premium_sold"], M[p]["households_quoted"],
                M[p]["call_volume"])
    standing = sorted(P3, key=tiebreak, reverse=True)
    top = max(points.values()) or 1
    # Gold/silver/bronze are the only medal colours the template defines. Fourth
    # place onward gets the template's own slate tone inline, so the podium
    # extends to any roster size without a stylesheet change (and inline
    # backgrounds are the safe choice in email anyway).
    medals = ["gold", "silver", "bronze"]

    def medal(i):
        if i < len(medals):
            return f'class="mvp-medal {medals[i]}"'
        return 'class="mvp-medal" style="background:#52514e"'

    podium = "".join(
        f'<table role="presentation" cellpadding="0" cellspacing="0" '
        f'class="mvp-row-table mvp-{i + 1}"><tr>'
        f'<td class="mvp-medal-cell" style="width:38px;padding-right:12px">'
        f'<div {medal(i)}>{i + 1}</div></td>'
        f'<td class="mvp-name-cell">{p}</td>'
        f'<td><div class="mvp-track"><div class="mvp-fill {DOT[p]}" '
        f'style="width:{points[p] / top * 100:.2f}%"></div></div></td>'
        f'<td class="mvp-pts-cell">{_pts(points[p])} pts</td></tr></table>'
        for i, p in enumerate(standing))
    head = ("<thead><tr><th>Category</th>" +
            "".join(f'<th class="num">{SHORT[p]}</th>' for p in P3) + "</tr></thead>")
    total = ('<tr><td><b>Total Points</b></td>' +
             "".join(f'<td class="num"><b>{_pts(points[p])} pts</b></td>'
                     for p in P3) +
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
# Must stay in step with DOT in render_report and the .cN rules in the template
# stylesheet -- these are the same colours, inlined for the Call Detail table.
# Producer identity colours, set by Frank 2026-08-25. These are swatches beside
# a name, never the only carrier of meaning, which is why the pale ones are fine
# here -- but note Amanda #baffff, Coral #00ffcf and Sarahi #ffb48c sit below the
# 3:1 mark-vs-background floor (1.11, 1.15 and 1.73 against a white card), so as
# a large filled funnel bar they read faint. Keep them paired with the name.
DOT_HEX = {"Crystal Mango": "#ff4b4b", "Lorena Gonzalez": "#cd81ff",
           "Mike Olvera": "#5656fe", "Coral Barwick": "#00ffcf",
           "Sarahi Chin": "#ffb48c", "Amanda Torricellas": "#baffff"}


def _fmt_phone(e164):
    d = "".join(ch for ch in (e164 or "") if ch.isdigit())[-10:]
    return f"({d[:3]}) {d[3:6]}-{d[6:]}" if len(d) == 10 else (e164 or "")


def _call_category(row):
    """One of cfg.CALL_CATEGORIES -- the seven-way Call Detail outcome.

    Splits the old five ways into seven by asking WHEN the quote went out
    (Frank, 2026-08-25). `quote_state` comes off the row, set in build_metrics
    from the day's task titles for that lead:

        'today' -> a quote went out on this call
        'open'  -> a quote was already out and this call chased it
        'none'  -> no quote in play

    A quote presented verbally and never entered in AgencyZoom still counts for
    the category, but does not feed Premium Quoted. A "recycled back from
    Smart-Cycle" move is a move OUT of the cycle and is not a dead outcome.
    """
    moves = " ".join(row.get("moves") or []).lower()
    note = (row.get("note") or "").lower()
    # DESTINATION ONLY. Splitting the whole "A to B" string and testing every
    # segment let the ORIGIN count: "Quotes Presented to Smart-Cycle" is a move
    # OUT of the quote stage, and reading "quote" off the left-hand side filed
    # Harry Anderson, Angel Inda and Juan Avila as quoted-on-this-call when all
    # three had been quoted days earlier and this call was the follow-up that
    # lost them. Also match the STAGE, not the pipeline -- "1-2 Leads Not
    # Quoted" is where NEVER-quoted leads get recycled (Frank, 2026-08-17:
    # Lazaro Rueda showed red).
    dests = []
    for mv in (row.get("moves") or []):
        mv = (mv or "").lower()
        d = mv.rsplit(" to ", 1)[-1] if " to " in mv else mv
        dests.append(d.split("|")[-1])
    quoted_here = (any("quote" in d and "not quoted" not in d for d in dests)
                   or "quote" in note)
    dead = ("dead" in moves or "smart-cycle" in moves)
    sold = "sold" in moves or "sold" in note
    qs = row.get("quote_state") or ("today" if quoted_here else "none")
    # A stage move into a quote stage on this call outranks the task title: the
    # title says what the producer sat down to do, the move says what happened.
    if quoted_here:
        qs = "today"

    if sold:
        return "sold_on_call"
    if dead:
        if qs == "today":
            return "quoted_call_lost"
        if qs == "open":
            return "followup_lost"
        return "dead_no_quote"
    if qs == "today":
        return "quoted_call_open"
    if qs == "open":
        return "followup_open"
    return "live_no_quote"


def _outcome_rank(row):
    """Call Detail sort key -- best first, matching cfg.CALL_CATEGORY_ORDER."""
    try:
        return cfg.CALL_CATEGORY_ORDER.index(_call_category(row))
    except ValueError:
        return len(cfg.CALL_CATEGORY_ORDER)


def _dead_word(row):
    """"Dead" only when the outcome actually says dead; otherwise "Lost".

    Both land in the same category -- the difference is what we can honestly
    claim. A smart-cycled lead is parked on a cadence, and calling it dead
    overstates it (Frank, 2026-08-25: 'anything "dead" should always read
    ... unless you actually see the dead outcome' -- then, on the wording,
    'instead of "SmartCycle/Dead" just say "Lost"').
    """
    moves = " ".join(row.get("moves") or []).lower()
    note = (row.get("note") or "").lower()
    return "Dead" if ("dead" in moves or "dead" in note) else "Lost"


def _cat_label(key, row=None):
    lab = cfg.CALL_CATEGORIES[key]["label"]
    return lab.replace("{d}", _dead_word(row) if row else "Lost")


def _cat_chip(key, small=False, row=None):
    """Labelled chip. FILLED = it happened on this call, OUTLINED = follow-up.

    The label is always present, so colour is never the only carrier -- which is
    also what lets seven states ride on five hues.
    """
    return (f'<span class="cg g{cfg.CALL_CATEGORY_ORDER.index(key) + 1}">'
            f'{_cat_label(key, row)}</span>')


def _cat_legend():
    """Panel legend. At the TOP of Call Detail from 2026-08-25 (Frank)."""
    items = "".join(
        f'<span><i class="k{cfg.CALL_CATEGORY_ORDER.index(k) + 1}"></i>'
        f'{_cat_label(k)}</span>' for k in cfg.CALL_CATEGORY_ORDER)
    return ('<div class="cdl">' + items
            + '<span class="cdn">Solid = it happened on this call '
            '&nbsp;&middot;&nbsp; striped = follow-up on a quote already out'
            '</span></div>')


# X3 (Frank, 2026-08-25): one chip per objection, and the chip says the word.
# Colour always means "did it work", never "did he try" -- a producer can
# address an objection well and still lose it, and Angel Inda's call is exactly
# that. "Not addressed" needs no result half: an objection nobody engaged was
# not overcome by definition.
OBJ_CHIP = {("no", None): ("cdc-r", "Not addressed"),
            ("yes", "yes"): ("cdc-g", "Addressed, overcome"),
            ("yes", "no"): ("cdc-r", "Addressed, not overcome"),
            ("yes", "unclear"): ("cdc-y", "Addressed, unclear")}


def _obj_chip(o):
    a = o.get("addressed")
    key = ("no", None) if a != "yes" else ("yes", o.get("overcome") or "unclear")
    cls, txt = OBJ_CHIP.get(key, ("cdc-y", "Addressed, unclear"))
    return f'<span class="cdch {cls}">{txt}</span>'


def _obj_rollup(objs):
    """How many landed, and which one was still standing at the end.

    Only a flat "no" is named. An unclear objection is not the thing that
    killed the call -- naming it would put a refusal in the prospect's mouth
    that the transcript never recorded. Guillermo Lara's third objection is
    that case: 2 of 3, nothing named.
    """
    won = sum(1 for o in objs if o.get("overcome") == "yes")
    tot = len(objs)
    cls = "cdc-g" if won == tot else "cdc-r" if not won else "cdc-y"
    v = f'<span class="cdch {cls}">{won} of {tot} overcome</span>'
    left = [o["objection"] for o in objs if o.get("overcome") == "no"]
    if left:
        v += f'<span class="cdst">left standing: {left[-1]}</span>'
    return v


def _grid(pairs):
    body = "".join(f'<tr><td class="cdgl">{k}</td><td class="cdgv">{v}</td></tr>'
                   for k, v in pairs)
    return f'<table class="cdg">{body}</table>'


def _call_note(r):
    """The labelled grid: what the call was, then every objection and its fate.

    Replaces the first ~280 characters of the raw transcript, which was the
    opening of the producer's own greeting and told a reader nothing (Frank,
    2026-08-25). Layout is D1c + M2 + X3 from the 08-25 mock-ups: fixed labels
    in a left gutter, one line per objection, and a roll-up row so a producer
    who won two of three does not read as a flat loss.

    `summary` is written by call_summary. When it is absent -- no API key, or
    metrics built before this existed -- fall back to the old raw-transcript
    behaviour so the panel never comes out empty.
    """
    d = r.get("summary") or {}
    rec_txt = (r.get("note_recording") or "").strip()
    prod_txt = (r.get("note_producer") or r.get("note") or "").strip()

    if not d:
        out = ""
        if rec_txt:
            out += f'<div class="cdq">&ldquo;{rec_txt}&rdquo;</div>'
        if prod_txt:
            out += f'<div class="cdw">{prod_txt}</div>'
        return out or ('<div class="cdx">Live contact from the recording; no '
                       'producer-written outcome in AgencyZoom.</div>')

    import call_summary
    d = call_summary.upgrade(d)
    pairs = []
    summ = (d.get("summary") or "").strip()
    if summ:
        pairs.append(("Call", summ))
    objs = d.get("objections") or []
    if objs:
        lines = "".join(
            f'<div class="cdol"><span class="cdon">{i}</span>'
            f'<span class="cdot">{o["objection"]}</span>{_obj_chip(o)}</div>'
            for i, o in enumerate(objs, 1))
        pairs.append(("Objection" + ("s" if len(objs) > 1 else ""), lines))
        # The roll-up only earns its line when there is something to add up.
        # On a single-objection call it just reprints the chip and the
        # objection text: "0 of 1 overcome, left standing: already bought
        # elsewhere" says nothing the line above it did not.
        if len(objs) > 1:
            pairs.append(("Overcome", _obj_rollup(objs)))
    elif summ:
        # An empty list is a real finding, not missing data: nobody pushed back.
        pairs.append(("Objections",
                      '<span class="cdch cdc-n">None raised</span>'))
    out = _grid(pairs) if pairs else ""
    # Always say where this came from, so nobody reads a typed note as a
    # transcript read or the other way round.
    if d.get("source") == "producer note":
        why = d.get("why") or "no recording"
        out += (f'<div class="cdsrc">from the producer&rsquo;s note '
                f'&mdash; {why}</div>')
    return out or ('<div class="cdx">Live contact, but nothing recorded and '
                   'nothing written.</div>')


def call_detail(M, day):
    """Option D (Frank, 2026-08-25): a section per rep, each opening with a
    stacked bar of that rep's outcome mix, then the calls full width beneath it.

    Replaces a 32-row table whose every row was flooded with one of five pastel
    fills. That read as a single wash with no rep boundaries -- and two of the
    fills were not even distinguishable: dead-with-quote #FCA5A5 against
    dead-no-quote #FDBA74 measured Delta E 9.3 for normal vision against a floor
    of 15, and all five sat under 3:1 contrast on the panel. Colour now rides a
    3px row edge and a labelled chip beside the talk time (Frank: "add the
    outcome tag by the talk time like option B").
    """
    groups = {}
    for p in P3:
        for r in M[p]["call_detail"]:
            groups.setdefault(p, []).append(r)
    for rows in groups.values():
        rows.sort(key=lambda r: (_outcome_rank(r), -(r["seconds"] or 0)))

    out = [_cat_legend()]
    for p in P3:
        rows = groups.get(p) or []
        if not rows:
            continue
        n = len(rows)
        counts = {}
        for r in rows:
            k = _call_category(r)
            counts[k] = counts.get(k, 0) + 1
        keys = [k for k in cfg.CALL_CATEGORY_ORDER if counts.get(k)]
        # Mix bar. A dashed-edge category reads as a paler band so the bar
        # carries the same this-call/follow-up split the chips do.
        seg = "".join(
            f'<td class="b{cfg.CALL_CATEGORY_ORDER.index(k) + 1}" '
            f'style="width:{100.0 * counts[k] / n:.3f}%">&nbsp;</td>'
            for k in keys)
        key = "".join(
            f'<span><i class="k{cfg.CALL_CATEGORY_ORDER.index(k) + 1}"></i>'
            f'{counts[k]} {_cat_label(k).lower()}</span>' for k in keys)
        out.append(
            '<div class="cdh"><table class="cdi"><tr>'
            f'<td class="cdr"><span class="dot" style="background:'
            f'{DOT_HEX[p]}"></span>{SHORT[p]}</td>'
            f'<td align="right" class="cdc">{n} live contact'
            f'{"s" if n != 1 else ""}</td></tr></table>'
            f'<table class="cdi cdb"><tr>{seg}</tr></table>'
            f'<div class="cdk">{key}</div></div>')

        body = []
        for r in rows:
            k = _call_category(r)
            c = cfg.CALL_CATEGORIES[k]
            secs = r["seconds"] or 0
            badge = ('<span class="badge-new" style="background:#9a988f;'
                     'color:#fff">duration only</span>'
                     if r["basis"] == "duration only" else "")
            link = (_lead_link(r["lead_id"], r["lead"]) if r["lead_id"]
                    else (r["lead"] or _fmt_phone(r["number"])))
            note = _call_note(r)
            body.append(
                f'<tr><td class="cdcell e{cfg.CALL_CATEGORY_ORDER.index(k) + 1}">'
                '<table class="cdi"><tr>'
                f'<td class="cdn2">{link}{badge}'
                f'<span class="cdp">&nbsp; {_fmt_phone(r["number"])}</span></td>'
                f'<td align="right" class="cdd" style="white-space:nowrap">'
                f'{_cat_chip(k, True, r)}&nbsp; '
                f'{secs // 60}:{secs % 60:02d}</td></tr></table>'
                f'{note}</td></tr>')
        out.append(f'<table class="cdi cdt">{"".join(body)}</table>')
    return "".join(out)


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


def _verdict_cell(r):
    """Why a cancelled task does or does not count. Printed so the excuse is
    auditable rather than silent (Frank, 2026-08-25)."""
    if r.get("verdict") == "excused":
        return ('<span class="tier-text-good" style="font-weight:600">excused'
                '</span><span class="sq">smart-cycled that day</span>')
    return '<span class="tier-text-critical" style="font-weight:600">counts</span>'


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
            f'{_record_cell(r)}<td>{r["title"]}</td>'
            f'<td class="note-cell">{_clip(r["comment"])}</td>'
            f'<td class="nowrap-cell">{_fmt_phone(r["number"])}</td></tr>'
            for r in audit["a"])
        out.append('<table><tr><th>Rep</th><th>Lead</th><th>Task</th>'
                   '<th>Comment</th>'
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
        out.append('<table><tr><th>Rep</th><th>Lead</th><th>Task</th>'
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
        out.append('<table><tr><th>Rep</th><th>Lead</th><th>Task</th>'
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
    n_exc = sum(1 for r in audit["d"] if r.get("verdict") == "excused")
    out.append(title("d", "Cancelled rather than completed", len(audit["d"]),
                     f", {len(audit['d']) - n_exc} counted against the rate"
                     + (f", {n_exc} excused" if n_exc else "")))
    if audit["d"]:
        rows = "".join(
            f'<tr><td class="name-cell">{SHORT[r["producer"]]}</td>'
            f'{_record_cell(r)}<td>{r["title"]}</td>'
            f'<td>{_activity_cell(r)}</td>'
            f'<td class="note-cell">{_why_cell(r)}</td>'
            f'<td class="nowrap-cell">{_verdict_cell(r)}</td></tr>'
            for r in audit["d"])
        out.append('<table><tr><th>Rep</th><th>Lead</th><th>Task</th>'
                   '<th>Activity that day</th><th>Why / instruction</th>'
                   f'<th>Counts?</th></tr>{rows}</table>'
                   '<div class="footnote">A task the producer did not complete '
                   'because they smart-cycled or killed the lead that day is '
                   'excused &mdash; AgencyZoom&rsquo;s &ldquo;cancel all related '
                   'open tasks&rdquo; checkbox is what closed it, so it leaves '
                   'the completion-rate denominator but stays listed here. A '
                   'duplicate lead&rsquo;s task is dropped from the audit '
                   'entirely and is not shown.</div>')
    else:
        out.append(empty(f'No producer task due {label} was cancelled.'))

    # (e) Frank, 2026-08-25: "going to have to start including a section in the
    # audit with the incomplete tasks." Section (d) already covers the ones that
    # were actively closed without being done; these are the ones simply left
    # open when the day ended, which until now showed only as a number in the
    # Task Completion Rate panel with no way to see WHICH tasks they were.
    out.append(title("e", "Still open at the end of the day",
                     len(audit.get("e") or []),
                     ", all counted against the rate"))
    if audit.get("e"):
        rows = "".join(
            f'<tr><td class="name-cell">{SHORT[r["producer"]]}</td>'
            f'{_record_cell(r)}<td>{r["title"]}</td>'
            f'<td class="nowrap-cell">{r["due"]}</td>'
            f'<td class="note-cell">{_clip(r["comment"])}</td></tr>'
            for r in audit["e"])
        out.append('<table><tr><th>Rep</th><th>Lead</th><th>Task</th>'
                   '<th>Due</th><th>Comment</th></tr>'
                   f'{rows}</table>')
    else:
        out.append(empty(f'Every producer task due {label} was closed out one '
                         f'way or another &mdash; none left open.'))

    return "".join(out)
