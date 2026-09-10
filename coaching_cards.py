"""Generate this board's per-call coaching cards, automatically, nightly.

    python3 coaching_cards.py 2026-09-08 > out/cards_2026-09-08.json

WHERE THIS SITS. `coaching/METHODOLOGY.md` is the entire coaching "brain" --
Frank's name for it is Apollo (2026-09-10) -- and it is sent verbatim as the
system prompt; nothing about HOW a call gets coached lives in this file.
This file only does the mechanical part: which
calls qualify, what to hand the model, how to parse what comes back, and the
handful of fields that are cheaper and safer to compute than to ask an LLM
for (lead, who, time, dur, cat/catc, tab -- see _finish_card).

BOARD ONLY, NEVER THE EMAIL (Frank, 2026-09-09: "put those coaching cards
only on the domain, not the email"). This module is wired into
publish_board.build(), never into render_report.py or daily.py's own email
path. Nobody reading the digest email sees a word of this.

WHY THIS RUNS UNATTENDED, UNLIKE THE HAND-AUTHORED cards_<day>.py FILES IT
CAN STILL BE OVERRIDDEN BY. Those were deliberately never generated -- an
invented coaching card is worse than an empty tab, because someone coaches a
producer on it. That objection is exactly why this exists: right now, only
Frank has the board link, nobody is being coached off an unreviewed card, and
he is running daily sessions to rewrite coaching/METHODOLOGY.md until the
rubric itself is trustworthy. Automating the mechanical generation is what
makes that iteration possible -- there is no other way to see what a
methodology edit actually produces across a real day's calls without
re-authoring every card by hand each time.

COST. This is a SECOND paid Anthropic read per live contact, on top of
call_summary.py's existing one -- roughly doubling that per-day cost, and
with a materially larger output budget (MAX_TOKENS below) because the card
schema is far richer than call_summary's one-paragraph read. Both reads
share the same transcript cache (data/fulltx_<day>.json) so neither
re-transcribes; only the model call itself is duplicated. Deleting
data/coaching_cards_<day>.json re-pays for every card on that day, same
caution as call_summary.py's own docstring gives for data/callsum_<day>.json.

WHAT QUALIFIES FOR A CARD. Only a live-contact row whose call_summary.py
read came from the RECORDING (`summary.source == "recording"`), never one
that fell back to producer notes. The methodology is built entirely around
quoting the transcript -- "a finding without a quote is not a finding" -- so
a row with no usable audio gets no card, not a card built from notes alone.
That is a known v1 gap, not an oversight: it means a real conversation with
unusable audio (foreign language, a repetition loop) goes uncoached even
though call_summary.py still reports it elsewhere.
"""
import datetime as dt
import json
import pathlib

import call_summary as CS
import day_calls

ROOT = pathlib.Path(__file__).resolve().parent
AZ = dt.timezone(dt.timedelta(hours=-7))

METHODOLOGY = (ROOT / "coaching/METHODOLOGY.md").read_text()

# The card schema (spine, 9-dim scorecard, 6-technique scorecard, objection
# deep-dive, strengths and gaps) is much richer than call_summary.py's
# one-paragraph read, so it needs a much bigger budget. Sized off a 15-20
# minute call's worth of transcript; the retry tier exists for the same
# reason call_summary.py's does -- a long call can still fill the first
# budget with thinking or run past it. Bumped 2026-09-10 when "techniques"
# (6 more scored dimensions) was added to the schema.
MAX_TOKENS = 4800
RETRY_TOKENS = 8000

DIMS = ["Opening & identification", "Discovery", "Current premium captured",
        "Renewal / X-date captured", "Product knowledge", "Presenting numbers",
        "Bundle / cross-sell raised", "Next step specificity", "CRM after the call"]

# Named sales techniques (Frank, 2026-09-10) -- same [letter, detail] shape as
# DIMS/score above, scored separately because these are about WHICH technique
# a producer reached for, not the mechanical call-flow checklist above.
TECH_DIMS = ["Elevator pitch", "Feel-Felt-Found", "Risk reversal",
             "Social proof", "Trial close", "Takeaway / urgency"]

CHIPT_VALUES = ("Addressed, overcome", "Addressed, not overcome", "Addressed, kept going")


def _ask_card(model, transcript, notes, seconds, producer, lead):
    msg = [{"role": "user", "content":
            f"Producer on this call: {producer}\n"
            f"Lead: {lead or '(name unknown)'}\n"
            f"Call length: {seconds} seconds\n\n"
            f"Producer's own notes (may be empty):\n{notes or '(none)'}\n\n"
            f"Machine transcript:\n{transcript}"}]
    base = {"model": model, "system": METHODOLOGY, "messages": msg}

    # Same two failure modes as call_summary._ask, same fix -- see that
    # function's docstring for why thinking is disabled and truncation gets
    # one retry with a bigger budget.
    try:
        resp = CS._post(dict(base, max_tokens=MAX_TOKENS,
                             thinking={"type": "disabled"}))
    except RuntimeError as e:
        if "thinking" not in str(e).lower():
            raise
        resp = CS._post(dict(base, max_tokens=RETRY_TOKENS))

    d = CS._extract(resp)
    if d is None:
        resp = CS._post(dict(base, max_tokens=RETRY_TOKENS))
        d = CS._extract(resp)
    if d is None:
        raise ValueError("no JSON in response")
    return d


def _dur(seconds):
    n = round(seconds or 0)
    m, s = divmod(n, 60)
    return f"{m}m {s:02d}s" if m else f"{s}s"


def _call_time(raw_dials, producer, number):
    """First dial's clock time, Arizona local -- e.g. "9:19 AM".

    Pulled from the day's raw RingCentral log (already on disk by the time
    this runs, and the same file day_calls.classify reads), not from
    anything this module fetches itself.
    """
    calls = (raw_dials.get(producer) or {}).get(number) or []
    starts = [c["startTime"] for c in calls if c.get("startTime")]
    if not starts:
        return ""
    try:
        t = dt.datetime.fromisoformat(min(starts).replace("Z", "+00:00"))
        return t.astimezone(AZ).strftime("%-I:%M %p")
    except (ValueError, TypeError):
        return ""


def _category(r):
    """(label, css class) -- from the same mechanical facts daily.py already
    attaches to the row, never from the model's read of the call.

    v1 covers only the three states cheaply knowable from call_detail: Sold
    (today), Quoted (a quote went out on this call), and Live Contact
    (everything else). The board's cat-dead and cat-fsd classes exist in the
    CSS but need a post-call lead-status join this module does not do yet --
    a gap to close later, not a silent miscoloring today.
    """
    if r.get("sold_today"):
        return "Sold", "cat-sold"
    if r.get("quote_state") == "today":
        return "Quoted", "cat-q"
    return "Live Contact", "cat-live"


def _tab(askq, asks):
    """Card accent colour, derived from the two assumption verdicts the model
    already gave -- not a separate judgment call. Green when the producer
    worked assumptively start to finish, red when they asked permission at
    both the quote and the close, yellow for a mixed call. This mirrors the
    methodology's own framing of askq/asks as the throughline of the card.
    """
    aq = bool((askq or [False])[0])
    ac = bool((asks or [False])[0])
    if aq and ac:
        return "var(--good)"
    if not aq and not ac:
        return "var(--bad)"
    return "var(--warn)"


def _bool_pair(raw):
    if not isinstance(raw, (list, tuple)) or not raw:
        return [False, ""]
    return [bool(raw[0]), str(raw[1]).strip() if len(raw) > 1 else ""]


def _clean_pairs(raw, cap=6):
    out = []
    for item in (raw or [])[:cap]:
        if isinstance(item, (list, tuple)) and item:
            title = str(item[0] or "").strip()
            detail = str(item[1]).strip() if len(item) > 1 else ""
            if title:
                out.append([title, detail])
    return out


def _clean_score(raw, dims=DIMS):
    out = {}
    if not isinstance(raw, dict):
        return out
    for dim in dims:
        e = raw.get(dim)
        if isinstance(e, (list, tuple)) and e and str(e[0]).lower() in ("s", "w", "m", "n"):
            out[dim] = [str(e[0]).lower(), str(e[1]).strip() if len(e) > 1 else ""]
    return out


def _clean_spine(raw, cap=8):
    out = []
    for item in (raw or [])[:cap]:
        if not isinstance(item, (list, tuple)) or len(item) < 3:
            continue
        t = str(item[0] or "").strip()
        m = str(item[1] or "n").strip().lower()
        h = str(item[2] or "").strip()
        s = str(item[3]).strip() if len(item) > 3 else ""
        if m not in ("g", "y", "r", "n"):
            m = "n"
        if h:
            out.append([t, m, h, s])
    return out


def _clean_obj(raw):
    if not isinstance(raw, dict):
        return None
    cat = str(raw.get("cat") or "").strip()
    they = str(raw.get("they") or "").strip()
    you = str(raw.get("you") or "").strip()
    if not cat or not they:
        return None
    out = {
        "cat": cat, "at": str(raw.get("at") or "").strip(),
        "they": they, "theyen": str(raw.get("theyen") or "").strip(),
        "you": you, "youen": str(raw.get("youen") or "").strip(),
        "noresp": bool(raw.get("noresp")),
        "addressed": bool(raw.get("addressed")),
        "anal": str(raw.get("anal") or "").strip(),
    }
    chipt = raw.get("chipt")
    if out["addressed"] and chipt in CHIPT_VALUES:
        out["chipt"] = chipt
    fix = raw.get("fix")
    out["fix"] = [str(f).strip() for f in fix if str(f).strip()][:3] if isinstance(fix, list) else []
    return out


def _finish_card(d, producer, r, raw_dials):
    """Merge the model's judgment with everything already known from the
    pipeline. Every mechanical field below is cheaper and more reliable to
    compute here than to ask the model for -- see the module docstring."""
    askq = _bool_pair(d.get("askq"))
    asks = _bool_pair(d.get("asks"))
    cat, catc = _category(r)
    return {
        "lead": r.get("lead") or "",
        # Full name, not first name: coachingPanel() (site/public/index.html)
        # groups cards by matching `who` against its own `order` list of full
        # producer names -- a first-name-only value matches nothing, so every
        # card silently fails the filter and the tab renders as if there were
        # no cards at all (found 2026-09-10, 18 real cards on 2026-09-09 all
        # invisible this way, first ever real day the automated pipeline ran).
        "who": producer,
        "time": _call_time(raw_dials, producer, r["number"]),
        "dur": _dur(r.get("seconds")),
        "lang": str(d.get("lang") or "").strip() or "English",
        "src": "recording",
        "cat": cat, "catc": catc,
        "tab": _tab(askq, asks),
        "summary": str(d.get("summary") or "").strip(),
        "askq": askq, "asks": asks,
        "askfix": str(d.get("askfix") or "").strip(),
        "obj": _clean_obj(d.get("obj")),
        "good": _clean_pairs(d.get("good")),
        "bad": _clean_pairs(d.get("bad")),
        "score": _clean_score(d.get("score")),
        "techniques": _clean_score(d.get("techniques"), TECH_DIMS),
        "spine": _clean_spine(d.get("spine")),
        "flags": [str(f).strip() for f in (d.get("flags") or []) if str(f).strip()][:6],
    }


ROSTER_ORDER = ["Lorena Gonzalez", "Crystal Mango", "Mike Olvera",
               "Coral Barwick", "Sarahi Chin"]


def build(day, log=print):
    """Every coaching card for `day`. [] if there is nothing to write (no
    API key, no metrics yet, no live contacts with usable audio) -- this
    never raises over a missing prerequisite, only over a real bug, because
    a nightly run must still publish the day's stats without cards rather
    than fail outright (see publish_board.build's caller)."""
    mpath = ROOT / f"data/metrics_{day}.json"
    if not mpath.exists():
        log(f"  coaching cards: no metrics_{day}.json yet")
        return []
    M = json.loads(mpath.read_text())

    key = CS._key()
    if not key:
        log("  coaching cards: ANTHROPIC_API_KEY not set, skipping")
        return []

    cpath = ROOT / f"data/coaching_cards_{day}.json"
    cache = json.loads(cpath.read_text()) if cpath.exists() else {}
    fx_path = ROOT / f"data/fulltx_{day}.json"
    fx = json.loads(fx_path.read_text()) if fx_path.exists() else {}

    rows = [(p, r) for p, v in M.get("producers", {}).items()
            for r in v.get("call_detail", [])
            if (r.get("summary") or {}).get("source") == "recording"]
    todo = [(p, r) for p, r in rows if CS._ck(p, r["number"]) not in cache]

    if todo:
        model = CS.pick_model()
        log(f"  writing {len(todo)} coaching cards with {model}...")
        for i, (p, r) in enumerate(todo, 1):
            ck = CS._ck(p, r["number"])
            text = fx.get(ck, "")
            ok, why = CS.usable(text, r.get("seconds"))
            if not ok:
                log(f"    {r['lead']}: {why} -- no card")
                continue
            notes = (r.get("note_producer") or "").replace("&middot;", ";").strip()
            try:
                d = _ask_card(model, text[:16000], notes, r.get("seconds") or 0,
                             p.split()[0], r.get("lead") or "")
                cache[ck] = d
            except Exception as e:
                log(f"    {r['lead']}: coaching read failed ({type(e).__name__}) -- no card")
            if i % 5 == 0:
                log(f"    {i}/{len(todo)}")
        cpath.write_text(json.dumps(cache, indent=1))

    raw_dials = day_calls.producer_dials(day)
    pairs = [(p, _finish_card(cache[CS._ck(p, r["number"])], p, r, raw_dials))
            for p, r in rows if CS._ck(p, r["number"]) in cache]
    rank = {name: i for i, name in enumerate(ROSTER_ORDER)}
    pairs.sort(key=lambda pc: rank.get(pc[0], 99))
    cards = [c for _, c in pairs]
    log(f"  coaching cards: {len(cards)} for {day}")
    return cards


def scan(cards):
    """The "What the day says" cross-call figures digestDay renders, computed
    straight off the generated cards -- mechanical, not a model read."""
    if not cards:
        return None
    def strong(dim):
        return sum(1 for c in cards if (c.get("score") or {}).get(dim, ["", ""])[0] == "s")
    return {
        "of": len(cards),
        "asked_open": sum(1 for c in cards if c.get("askq") and c["askq"][0] is False),
        "assumed_open": sum(1 for c in cards if c.get("askq") and c["askq"][0] is True),
        "priced": sum(1 for c in cards if c.get("catc") in ("cat-sold", "cat-q")),
        "closed": sum(1 for c in cards if c.get("catc") == "cat-sold"),
        "premium": strong("Current premium captured"),
        "xdate": strong("Renewal / X-date captured"),
        "bundle": strong("Bundle / cross-sell raised"),
        "timeset": strong("Next step specificity"),
    }


def objcats(cards):
    """[[category, raised, won], ...] -- "won" means addressed AND overcome,
    per the methodology's own addressed-vs-overcome distinction."""
    agg = {}
    for c in cards:
        o = c.get("obj")
        if not o:
            continue
        raised, won = agg.get(o["cat"], (0, 0))
        agg[o["cat"]] = (raised + 1,
                         won + (1 if o.get("chipt") == "Addressed, overcome" else 0))
    return sorted(([cat, n, w] for cat, (n, w) in agg.items()), key=lambda row: -row[1])


if __name__ == "__main__":
    import sys
    d = sys.argv[1] if len(sys.argv) > 1 else dt.datetime.now(AZ).date().isoformat()
    print(json.dumps(build(d), indent=1, default=str))
