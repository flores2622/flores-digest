"""Fill the Utilization and Efficiency panel with live Insightful data.

This does NOT rebuild the report. It takes the approved TEST 7 layout and
replaces only the six utilization cards and the panel footer, leaving every
other panel, style rule and byte untouched.

WHY THIS EXISTS: on 2026-08-12 the panel rendered six identical dead cards --
"not published by Insightful for this day / Nothing estimated" -- because the
build depended on Insightful's daily EMAIL, which lands ~15:01 UTC the following
day, after the send window. The API has no such lag (see insightful_util), so
the panel can now be filled at send time.

CARD MARKUP, taken from the approved builds -- do not invent new structure:

    <div class="insight-card">
      <div class="rep"><span class="dot cX"></span>NAME</div>
      <div class="insight-util"><span class="num TIER">86.2%</span>
                                <span class="lbl">utilization</span></div>
      <div class="sk"><span class="sf cI" style="width:86%"></span></div>
      <div class="insight-stats">
        <div class="stat"><b>7h 03m</b> productive / 8h 10m tracked</div>
        <div class="stat"><b>1h 07m</b> idle</div>
      </div>
    </div>

    TIER is tier-text-good / tier-text-warning / tier-text-critical
    (.tier-text-good #0ca30c, -warning #fab219, -critical #DC2626), applied with
    the Utilization thresholds: 85+ green, 80-84 yellow, under 80 red.

    The Aug 7 build wrote "productive / 7h 32m expected". "Expected" is wrong --
    the denominator is analytics/attendance duration, i.e. time actually tracked,
    not a target. Changed to "tracked". Flagged to Frank 2026-08-14.

PANEL ORDER is taken from the approved TEST 7 layout: Crystal, Mike, Debbie,
Lorena, Coral, Sarahi. Amanda is NOT in this panel -- she is in the utilization
SCOPE rule ("all users except Amanda") but was never rendered as a card.

PLACEHOLDERS: Coral and Sarahi keep their dashed, deliberately-blank cards
(Frank, 2026-08-14: hold until the 08-28 review). Their second stat line is
updated to record what we now know -- Coral's data exists, Sarahi has no
licence -- so the 28th is a straight yes/no rather than another investigation.
"""
import re

from digest_config import AZ_TZ, tier as tier_for  # noqa: F401
import digest_config as cfg
import insightful_util as iu

PANEL_ORDER = ["Crystal Mango", "Mike Olvera", "Debbie Aguilera",
               "Lorena Gonzalez", "Coral Barwick", "Sarahi Chin"]

TIER_CLASS = {"green": "tier-text-good",
              "yellow": "tier-text-warning",
              "red": "tier-text-critical"}

# Bar fill. TEST 7 shipped these as `class="sf cI"` at width:0% -- cI is #d8d6cf,
# a neutral grey, which was right for a dead card and wrong for a live one.
# Frank asked for tier colours 2026-08-14. Set as an INLINE background so it
# beats the .cI class rule without needing new CSS in the head (which minify.py
# would then have to be taught not to purge).
TIER_BAR = {"green": "#0ca30c",      # --status-good
            "yellow": "#fab219",     # --status-warning
            "red": "#DC2626"}        # --status-critical, matches TIER_COLORS'
                                      # "red" -- was #d64545, too muted to read
                                      # as an alert (Frank, 2026-08-25)

CARD_RE = re.compile(
    r'(<div class="insight-card"[^>]*>.*?</div></div>)', re.S)
NAME_RE = re.compile(r'<div class="rep"><span class="dot c\w+"></span>([^<]+)</div>')

# The stats block, which is what each card path rewrites.
#
#   <div class="insight-stats"><div class="stat">A</div><div class="stat">B</div></div>
#    ^open 1                    ^open 2         ^close 1  ^open 3        ^close 2 ^close 3
#
# THREE opens, THREE closes. The non-greedy `.*?</div></div>` below stops at the
# second stat's close plus the insight-stats close -- it does NOT swallow the
# card's own closing tag. An earlier version of this file emitted a replacement
# ending in `</div></div>`, adding one stray `</div>` per card. Six cards meant
# six stray closes, which shut the panel and its column <td> early and destroyed
# the layout of every panel after this one -- Coaching & Call Quality first.
# Only Crystal, the first card, still looked right.
#
# assert_div_balance() below makes that class of mistake impossible to ship.
STATS_RE = re.compile(r'<div class="insight-stats">.*?</div></div>', re.S)


def _stats(a, b):
    """Build a balanced insight-stats block: 3 opens, 3 closes. No trailing div."""
    return (f'<div class="insight-stats">'
            f'<div class="stat">{a}</div>'
            f'<div class="stat">{b}</div>'
            f'</div>')


def assert_div_balance(before, after, label=""):
    o1, c1 = len(re.findall(r'<div\b', before)), len(re.findall(r'</div>', before))
    o2, c2 = len(re.findall(r'<div\b', after)), len(re.findall(r'</div>', after))
    if (o1 - c1) != (o2 - c2):
        raise SystemExit(
            f"div balance changed{' in ' + label if label else ''}: "
            f"was {o1} open / {c1} close (delta {o1 - c1}), "
            f"now {o2} open / {c2} close (delta {o2 - c2}). "
            f"Refusing to emit broken HTML.")


def _hm(ms):
    """7h 03m, matching the approved build's wording."""
    m = int(round(ms / 60000))
    return f"{m // 60}h {m % 60:02d}m" if m >= 60 else f"{m}m"


# The percentage and the bar used to be written with str.replace() keyed on the
# EMPTY forms -- '<span class="num zero">&mdash;</span>' and 'width:0%'. Only the
# two placeholder cards carry those; Crystal, Mike, Debbie and Lorena ship from
# the template with Aug 12 values already baked in ("84.9%", 'width:85%'), so the
# replace matched nothing and silently left the stale number while _stats() below
# happily refreshed the times beside it. Lorena read 84.9% every day from Aug 12
# to Aug 24 (Frank, 2026-08-25: "still stuck at 84.9%"), and Crystal read 89.5%
# against a real 81.4%. These rewrite whatever is there and RAISE if the span has
# gone, so the failure can never again be a silently wrong number.
NUM_RE = re.compile(
    r'(<div class="insight-util"><span class="num )[^"]*(">)[^<]*(</span>)')
BAR_RE = re.compile(r'<span class="sf cI" style="width:[^"]*"></span>')


def _set_num(card, cls, inner):
    card, n = NUM_RE.subn(
        lambda m: f"{m.group(1)}{cls}{m.group(2)}{inner}{m.group(3)}", card, 1)
    if not n:
        raise SystemExit("utilization card: number span not found -- layout changed?")
    return card


def _set_bar(card, pct, bg=None):
    style = f"width:{pct:.0f}%" + (f";background:{bg}" if bg else "")
    card, n = BAR_RE.subn(f'<span class="sf cI" style="{style}"></span>', card, 1)
    if not n:
        raise SystemExit("utilization card: bar span not found -- layout changed?")
    return card


def _blank(card):
    """No figure for this card: em dash, empty bar. Never a stale % or a 0%."""
    return _set_bar(_set_num(card, "zero", "&mdash;"), 0)


def _card_html(card, name, detail):
    """Rewrite one card's number, bar and stats. Everything else is preserved."""
    d = detail.get(name) or {}

    if name in cfg.PLACEHOLDERS:
        # Deliberately blank until 2026-08-28 -- except a sale, which is shown
        # on the day it happens (Frank, 2026-08-14). The sale is displayed only;
        # it does not enter any team total.
        sale = (detail.get("_placeholder_sales") or {}).get(name)
        if sale:
            n, prem = sale
            s1 = (f'<b>Sold {n} polic{"y" if n == 1 else "ies"} today &mdash; '
                  f'${prem:,.0f}</b>')
        elif name == "Coral Barwick":
            s1 = "in training, excluded from every figure"
        else:
            s1 = "in training, excluded from every figure"
        if name == "Coral Barwick":
            s2 = ("Insightful data <b>is</b> available &mdash; "
                  "include-or-not decision due Aug 28")
        else:
            s2 = ("no Insightful licence assigned &mdash; "
                  "cannot be tracked until one is")
        return STATS_RE.sub(_stats(s1, s2), _blank(card))

    if name in cfg.NO_INSIGHTFUL_LICENCE:
        # No Insightful record AT ALL -- a different fact from "licensed but no
        # rows today", and the only figure still missing for her now that she is
        # a regular producer (2026-08-24). Wired up here so the card states the
        # actual reason instead of implying she simply did not work.
        return STATS_RE.sub(
            _stats("no Insightful licence assigned &mdash; "
                   "cannot be tracked until one is",
                   "Every other figure for her is live"), _blank(card))

    if not d.get("tracked"):
        # Licensed but no attendance rows. Never render 0% -- a zero reads as a
        # terrible day rather than as no data.
        return STATS_RE.sub(
            _stats("no tracked time in Insightful for this day",
                   "Nothing estimated"), _blank(card))

    prod, total = d["productive_ms"], d["total_ms"]
    pct = prod / total * 100
    t = cfg.tier("utilization_pct", pct)

    card = _set_num(card, TIER_CLASS[t], f"{pct:.1f}%")
    card = _set_bar(card, pct, TIER_BAR[t])
    return STATS_RE.sub(
        _stats(f'<b>{_hm(prod)}</b> productive / {_hm(total)} tracked',
               f'<b>{_hm(total - prod)}</b> idle'), card)


# The panel footer is REMOVED, not rewritten (Frank, 2026-08-14). TEST 7 used
# that <div class="empty-row"> to explain why the panel was empty; with the
# panel populated there is nothing to apologise for, and the sourcing and
# method belong in the notes attachment (footnote 6), not in the panel.
FOOTER_RE = re.compile(r'<div class="empty-row">.*?</div>', re.S)


def patch(html, day, detail=None, weighted=None, policies=None):
    """Return the report HTML with the Utilization panel filled for `day`."""
    if detail is None:
        _, weighted, detail = iu.pull(day)
    if cfg.PLACEHOLDER_SHOW_SALES:
        import json
        import pathlib
        if policies is None:
            f = pathlib.Path("data/az_policies_all.json")
            policies = json.loads(f.read_text()) if f.exists() else []
        from az_corpus import fetch
        smap = cfg.lead_source_map(fetch())
        detail = dict(detail)
        detail["_placeholder_sales"] = cfg.placeholder_sales(day, policies, smap)

    start = html.find("Utilization and Efficiency")
    if start < 0:
        raise SystemExit("Utilization panel not found -- layout changed?")
    end = html.find('<div class="panel"', start)
    panel = html[start:end]

    seen = []

    def repl(m):
        card = m.group(1)
        nm = NAME_RE.search(card)
        if not nm:
            return card
        name = nm.group(1).strip()
        seen.append(name)
        return _card_html(card, name, detail)

    new_panel = CARD_RE.sub(repl, panel)
    new_panel = FOOTER_RE.sub("", new_panel)
    # The dead cards were dimmed because they carried no data. Undim the ones
    # that now do; placeholders keep their dashed, deliberately-faint styling.
    new_panel = new_panel.replace('<div class="insight-card" style="opacity:.8">',
                                  '<div class="insight-card">')

    if [s for s in seen if s not in cfg.PLACEHOLDERS] != \
            [n for n in PANEL_ORDER if n not in cfg.PLACEHOLDERS]:
        raise SystemExit(f"panel order changed: {seen}")

    out = html[:start] + new_panel + html[end:]
    assert_div_balance(html, out, "utilization panel")
    return out


if __name__ == "__main__":
    import sys
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-08-12"
    src = sys.argv[2] if len(sys.argv) > 2 else "recovered/ops_body_2026-08-12.html"
    html = open(src).read()
    out = patch(html, day)
    dest = f"out/Ops_Report_{day}_util.html"
    open(dest, "w").write(out)
    print(f"{dest}  {len(out):,} bytes (was {len(html):,})")
    print(f"Gmail clip limit {cfg.GMAIL_CLIP_BYTES:,} -- "
          f"{'OK' if len(out.encode()) < cfg.GMAIL_CLIP_BYTES else 'TOO BIG'}")
