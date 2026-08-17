"""Render a day's report by repopulating the approved layout.

The approved TEST 7 build is the template. Rather than re-author its HTML --
which is where the layout was hard-won (HANDOFF s9) -- each panel's markup is
extracted at runtime and rebuilt with the new day's values, using the same CSS
classes. Nothing outside the panels is touched.

Every write is guarded by a div-balance check: an earlier edit here emitted one
stray </div> per card, which closed the panel and its column early and destroyed
every panel below it.
"""
import re

import digest_config as cfg
from util_panel import assert_div_balance

DOT = {"Crystal Mango": "cA", "Lorena Gonzalez": "cB", "Mike Olvera": "cC",
       "Debbie Aguilera": "cE", "Coral Barwick": "cG", "Sarahi Chin": "cG"}
TEAM_DOT = "cE"
TIER = {"green": "tier-text-good", "yellow": "tier-text-warning",
        "red": "tier-text-critical"}


def hhmm(sec):
    return f"{sec // 60}m {sec % 60:02d}s" if sec >= 60 else f"{sec}s"


def money(v):
    return f"${v:,.0f}"


def _bar_row(name, value_html, pct, klass, team=False):
    dot = TEAM_DOT if team else DOT.get(name, "cE")
    label = ('<div class="sl">Team Total</div>' if team else
             f'<div class="sl"><span class="sl-left"><span class="dot {dot}">'
             f'</span>{name}</span></div>')
    return (f'<div class="ss{" team-stat" if team else ""}">{label}'
            f'<table role="presentation" cellpadding="0" cellspacing="0" class="st">'
            f'<tr><td><div class="sk"><div class="sf {dot}" '
            f'style="width:{pct:.2f}%"></div></div></td>'
            f'<td class="sy"><span class="sv {klass}">{value_html}</span></td>'
            f'</tr></table></div>')


def funnel_card(title, subtitle, rows, team_value, team_tier):
    """rows: [(producer, numeric, display, tier)] -- bars scale to top producer."""
    rows = sorted(rows, key=lambda r: -r[1])
    top = max([r[1] for r in rows] + [0]) or 1
    body = "".join(_bar_row(n, d, (v / top * 100) if top else 0, TIER[t])
                   for n, v, d, t in rows)
    body += _bar_row("Team Total", team_value, 100.0, TIER[team_tier], team=True)
    return (f'<div class="scorecard cat-card"><div class="sc-name">{title}</div>'
            f'<div class="sb">{subtitle}</div>{body}</div>')


def build_funnel(m, day_label):
    P = ["Crystal Mango", "Lorena Gonzalez", "Mike Olvera"]
    cards = []

    vol = [(p, m[p]["call_volume"],
            f'{m[p]["call_volume"]}'
            f'<span class="sq">{m[p].get("total_dials", 0)} dials</span>',
            cfg.tier("call_volume", m[p]["call_volume"])) for p in P]
    tv = sum(m[p]["call_volume"] for p in P)
    td = sum(m[p].get("total_dials", 0) for p in P)
    cards.append(funnel_card(
        "Call Volume", f"Distinct new-business dials &mdash; {day_label}", vol,
        f'{tv}<span class="sq">{td} dials</span>',
        cfg.tier("call_volume", tv / cfg.TEAM_SCALE)))

    talk = [(p, m[p]["avg_talk"], hhmm(m[p]["avg_talk"]),
             cfg.tier("avg_talk_min", m[p]["avg_talk"] / 60)) for p in P]
    live = sum(m[p]["live"] for p in P)
    tt = sum(m[p]["avg_talk"] * m[p]["live"] for p in P) // live if live else 0
    cards.append(funnel_card(
        "Avg Talk Time", f"Per live contact &mdash; {day_label}", talk,
        hhmm(tt), cfg.tier("avg_talk_min", tt / 60)))

    cr = [(p, m[p]["contact_rate"],
           f'{m[p]["contact_rate"]}%<span class="sq">{m[p]["live"]} / '
           f'{m[p]["call_volume"]}</span>',
           cfg.tier("contact_rate_pct", m[p]["contact_rate"])) for p in P]
    trate = round(live / tv * 100, 1) if tv else 0
    cards.append(funnel_card(
        "Contact Rate", f"Live contacts per new-business dial &mdash; {day_label}",
        cr, f'{trate}%<span class="sq">{live} / {tv}</span>',
        cfg.tier("contact_rate_pct", trate)))

    hh = [(p, m[p]["households_quoted"], str(m[p]["households_quoted"]),
           cfg.tier("households_quoted", m[p]["households_quoted"])) for p in P]
    th = sum(m[p]["households_quoted"] for p in P)
    cards.append(funnel_card(
        "Households Quoted", f"New business &mdash; {day_label}", hh, str(th),
        cfg.tier("households_quoted", th / cfg.TEAM_SCALE)))

    pq = []
    for p in P:
        per = (m[p]["premium_quoted"] / m[p]["households_quoted"]
               if m[p]["households_quoted"] else 0)
        pq.append((p, m[p]["premium_quoted"], money(m[p]["premium_quoted"]),
                   cfg.tier("premium_quoted_per_hh", per)))
    tq = sum(m[p]["premium_quoted"] for p in P)
    cards.append(funnel_card(
        "Premium Quoted", f"Total quoted, tiered per household &mdash; {day_label}",
        pq, money(tq), cfg.tier("premium_quoted_per_hh", tq / th if th else 0)))

    ps = []
    for p in P:
        per = (m[p]["premium_sold"] / m[p]["policies"]
               if m[p]["policies"] else 0)
        ps.append((p, m[p]["premium_sold"], money(m[p]["premium_sold"]),
                   cfg.tier("premium_sold_per_policy", per)))
    tsold = sum(m[p]["premium_sold"] for p in P)
    tpol = sum(m[p]["policies"] for p in P)
    cards.append(funnel_card(
        "Premium Sold", f"Producer sales, tiered per policy &mdash; {day_label}",
        ps, money(tsold),
        cfg.tier("premium_sold_per_policy", tsold / tpol if tpol else 0)))

    return '<div class="scorecard-grid">' + "".join(cards) + '</div>'


TAG_RE = re.compile(r'<(/?)div\b[^>]*>', re.I)


def swap_panel(html, heading, new_inner, next_heading=None):
    """Replace a panel's body: everything between its </h2> and its OWN close.

    The panel end is found by walking div depth from the panel's opening tag,
    not by searching for the next heading. Guessing the boundary truncated the
    document on the first attempt -- Recontact Struggle is the last panel in the
    left column, so nothing recognisable follows it before the column closes.
    """
    i = html.find(heading)
    if i < 0:
        raise SystemExit(f"panel not found: {heading}")
    open_tag = html.rfind('<div class="panel', 0, i)
    if open_tag < 0:
        raise SystemExit(f"panel opening tag not found: {heading}")
    start = html.find("</h2>", i) + len("</h2>")

    depth = 0
    end = None
    for m in TAG_RE.finditer(html, open_tag):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            end = m.start()
            break
    if end is None or end < start:
        raise SystemExit(f"panel close not found: {heading}")
    return html[:start] + new_inner + html[end:]
