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

# GMAIL DROPS A <style> BLOCK OVER ~16 KB -- silently, and the WHOLE block, so
# the email arrives as unstyled text (Frank, 2026-08-28: "the whole formatting
# has been lost"). Measured against delivered mail:
#
#     2026-08-25 code   style 15,864   under   Aug 26 email rendered correctly
#     2026-08-27 fixes  style 17,851   OVER    first email built on it was the
#                                              first one that arrived unstyled
#
# Nothing else moved: the broken email's BODY was SMALLER than the working
# one's (84 KB vs 92 KB), the MIME tree, the quoted-printable encoding and the
# markup were identical, and it happened with and without attachments.
#
# SPLITTING INTO TWO BLOCKS DOES NOT WORK. That was tried on 2026-08-31 and
# Gmail applied only the FIRST block: Crystal, Lorena, Mike and Debbie kept
# their colours (.cA .cB .cC .cE, block one) while Coral, Sarahi and Amanda
# lost theirs (.cJ .cK .cL, block two). Gmail honours one <style> and discards
# the rest. Everything has to fit in a single block.
#
# So the sheet is pruned instead: a rule whose every class selector is absent
# from THIS document cannot affect it, and dropping it is a no-op on rendering.
# That is worth ~2.3 KB on a normal day and more once overflow.py has shed a
# panel, because the shed panel's styles go with it. It is also self-adjusting,
# which a hand-trimmed sheet would not be.
STYLE_BLOCK_LIMIT = 16_384


def prune_css(html, log=None):
    """Drop style rules whose classes appear nowhere in this document.

    Only class selectors are considered. Element and id selectors, @media
    blocks and anything else are always kept -- the test has to be certain,
    and a rule wrongly dropped is a silent visual regression.
    """
    m = re.search(r"(<style[^>]*>)(.*?)(</style>)", html, re.S | re.I)
    if not m:
        return html
    open_tag, css, close_tag = m.group(1), m.group(2), m.group(3)
    used = {c for group in re.findall(r'class="([^"]*)"', html)
            for c in group.split()}

    # Brace-aware: an @media block is ONE unit. A flat regex splits inside it
    # and silently loses the wrapper.
    units, start, depth = [], 0, 0
    for i, ch in enumerate(css):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                units.append(css[start:i + 1])
                start = i + 1
    if start < len(css) or "".join(units) != css:
        return html                      # could not parse it cleanly; leave alone

    keep = []
    for unit in units:
        sel = unit.split("{", 1)[0]
        classes = re.findall(r"\.([A-Za-z0-9_-]+)", sel)
        if sel.strip().startswith("@") or not classes or any(c in used for c in classes):
            keep.append(unit)
    # Drop byte-identical duplicate rules, keeping the LAST occurrence.
    # A rule repeated verbatim is dead weight: same selector, same specificity,
    # same declarations, so the later copy already wins and deleting the earlier
    # one cannot change a single computed value. Keeping the last (not the
    # first) is the safe direction -- anything declared between the two copies
    # still gets overridden exactly as it did before.
    #
    # This is a guard, not the fix. The 810 bytes it found on 2026-08-31 were a
    # block of base rules pasted twice into report_template.html, which is what
    # took the sheet from 15,864 to 17,851 "in one merge" (HANDOFF 11 s4). The
    # template has been deduped; this keeps the next stray paste from silently
    # eating the headroom again.
    last = {}
    for i, unit in enumerate(keep):
        last[unit] = i
    deduped = [u for i, u in enumerate(keep) if last[u] == i]
    dups = len(keep) - len(deduped)

    out = "".join(deduped)
    if log:
        log(f"  css pruned {len(css):,} -> {len(out):,} bytes "
            f"({len(units) - len(keep)} rules unused in this document"
            + (f", {dups} duplicate rules dropped" if dups else "") + ")")
    if len(out) > STYLE_BLOCK_LIMIT:
        raise SystemExit(
            f"REFUSING TO SEND: stylesheet is {len(out):,} bytes, over Gmail's "
            f"~{STYLE_BLOCK_LIMIT:,} single-block cap. Gmail discards the whole "
            f"block and the email arrives as unstyled text. Splitting does not "
            f"help -- Gmail honours only the first block. Shrink the sheet.")
    return html[:m.start()] + open_tag + out + close_tag + html[m.end():]



import digest_config as cfg
from util_panel import assert_div_balance

# Identity colours, taken from the row-2 key of Frank's Sales.xlsx so the report
# and the sheet agree: Crystal #CC0000, Lorena #9900FF, Mike #0000FF -- all three
# already matched cA/cB/cC exactly, which confirms that sheet is the source.
#
# Row 2 of the sheet gives Coral and Sarahi the SAME orange, so Frank set theirs
# directly on 2026-08-24: Coral #E6CFF2, Sarahi #FFCFC9 -- the two tints row 3
# already used to tell them apart. They live on cJ and cK, both added to the
# template stylesheet for them.
# Deliberately NOT reused: cD, which the Call Outcome bars already use (og cD),
# and cF green / cH amber, which carry good/warning tier meaning elsewhere. A
# producer dot must not double as a status colour.
DOT = {"Crystal Mango": "cA", "Lorena Gonzalez": "cB", "Mike Olvera": "cC",
       "Debbie Aguilera": "cE", "Coral Barwick": "cJ", "Sarahi Chin": "cK",
       "Amanda Torricellas": "cL"}
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
    # Its own hardcoded roster until 2026-08-24, which is why the funnel kept
    # showing three producers and three-producer team totals after Coral and
    # Sarahi were promoted everywhere else. Driven off the config now.
    P = list(cfg.PRODUCERS)
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


def move_panel_before(html, heading, marker):
    """Relocate a whole panel so it sits immediately before `marker`.

    Same depth walk as swap_panel and drop_panel, so the boundary cannot be
    guessed wrong. Used to put Call Outcome Breakdown last in the digest (Frank,
    2026-08-24). Panels outside the two-column table are already full width, so
    moving one there is a position change only -- no wrapper or width to adjust.
    """
    i = html.find(heading)
    if i < 0:
        raise SystemExit(f"panel not found: {heading}")
    open_tag = html.rfind('<div class="panel', 0, i)
    if open_tag < 0:
        raise SystemExit(f"panel opening tag not found: {heading}")
    depth = 0
    for m in TAG_RE.finditer(html, open_tag):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            block = html[open_tag:m.end()]
            rest = html[:open_tag] + html[m.end():]
            j = rest.find(marker)
            if j < 0:
                raise SystemExit(f"move target not found: {marker}")
            return rest[:j] + block + rest[j:]
    raise SystemExit(f"panel close not found: {heading}")


def cut_panel(html, heading):
    """drop_panel, but hand back the panel it removed.

    Same depth walk, so the boundary cannot be guessed wrong. The overflow
    rescue needs the markup it cut, not just the shortened body: a panel that
    leaves the email has to arrive as a PDF instead.
    """
    i = html.find(heading)
    if i < 0:
        raise SystemExit(f"panel not found: {heading}")
    open_tag = html.rfind('<div class="panel', 0, i)
    if open_tag < 0:
        raise SystemExit(f"panel opening tag not found: {heading}")
    depth = 0
    for m in TAG_RE.finditer(html, open_tag):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return html[:open_tag] + html[m.end():], html[open_tag:m.end()]
    raise SystemExit(f"panel close not found: {heading}")


def drop_panel(html, heading):
    """Remove a whole panel -- its <div class="panel"> through its own close.

    Same depth walk as swap_panel, so it cannot guess the boundary wrong. Used to
    keep a panel out of an email body while its PDF companion still ships: the
    attachments are built from their own templates and do not read the report, so
    removing a panel here costs nothing downstream.
    """
    i = html.find(heading)
    if i < 0:
        raise SystemExit(f"panel not found: {heading}")
    open_tag = html.rfind('<div class="panel', 0, i)
    if open_tag < 0:
        raise SystemExit(f"panel opening tag not found: {heading}")
    depth = 0
    for m in TAG_RE.finditer(html, open_tag):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return html[:open_tag] + html[m.end():]
    raise SystemExit(f"panel close not found: {heading}")
