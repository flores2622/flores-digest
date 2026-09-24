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

A SECOND real conversation with the same lead that day -- the producer
calling back, or the lead calling back on their own -- is coached on the
SAME card as the first, not a separate one (Frank, 2026-09-15). Grouped by
(producer, lead_id); see build()'s own comment for exactly which cases
that catches (only rows daily.py's _one_row_per_lead already left as
separate call_detail entries -- this never touches that function or the
contact-rate math it feeds).

A live-contact row that qualifies still gets no card in the RETURNED list if
Apollo's own calltype judgment (see METHODOLOGY.md's Core judgment) comes
back pure "service" -- a renewal, payment, claim or paperwork call with no
sales opportunity (Frank, 2026-09-14: "that is purely for new business
opportunities"). A "mixed" call (a cross-sell raised mid-service-call) still
gets a card. The model read still happens and is cached for every live
contact regardless -- see build()'s filter, and the COST note above.
"""
import datetime as dt
import json
import pathlib
import re

import call_summary as CS
import day_calls
import digest_config as cfg
import panels

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

def _ask_card(model, transcript, notes, seconds, producer, lead, call_count=1):
    length_line = (f"Call length: {seconds} seconds" if call_count == 1 else
                   f"Total length across {call_count} calls with this same lead "
                   f"today: {seconds} seconds -- read the transcript below as ONE "
                   f"continuing relationship, in the order the calls happened")
    msg = [{"role": "user", "content":
            f"Producer on this call: {producer}\n"
            f"Lead: {lead or '(name unknown)'}\n"
            f"{length_line}\n\n"
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


def _call_time(raw_dials, producer, numbers):
    """Earliest dial's clock time, Arizona local -- e.g. "9:19 AM", across
    every number in the group (a "2 calls coached together" card can span
    two different numbers for the same lead, Frank 2026-09-15).

    Pulled from the day's raw RingCentral log (already on disk by the time
    this runs, and the same file day_calls.classify reads), not from
    anything this module fetches itself.
    """
    calls = []
    for n in numbers:
        calls += (raw_dials.get(producer) or {}).get(n) or []
    starts = [c["startTime"] for c in calls if c.get("startTime")]
    if not starts:
        return ""
    try:
        t = dt.datetime.fromisoformat(min(starts).replace("Z", "+00:00"))
        return t.astimezone(AZ).strftime("%-I:%M %p")
    except (ValueError, TypeError):
        return ""


def _earliest_start(raw_dials, producer, number):
    """Raw ISO start time of the earliest dial on this number, or None --
    the sort key _call_times uses to put a group's calls in chronological
    order (not outbound-then-inbound, which isn't always the true order)."""
    calls = (raw_dials.get(producer) or {}).get(number) or []
    starts = [c["startTime"] for c in calls if c.get("startTime")]
    return min(starts) if starts else None


def _call_times(producer, group, raw_dials):
    """[seconds, ...], one entry per real conversation, earliest first --
    so the board can show "1st talk time + 2nd talk time" instead of only
    the combined total (Frank, 2026-09-15: "should show 1st talk time +
    2nd talk time to know the split").

    Deliberately over `group`'s raw rows, NOT _distinct_calls() -- a
    callback doesn't need a second number (Frank, 2026-09-15: "it
    shouldn't need to be 2 different numbers, it can be from the same
    number a call back"). Two rows on the same number are still two real
    telephony sessions with their own logged `seconds`; _distinct_calls'
    number-dedup exists only to stop the TRANSCRIPT/RECORDING from
    repeating the one cached blob those rows share (see _group_transcript),
    not to hide that a second call happened.

    Covers all three ways two conversations with the same lead end up on
    one card: two rows on different numbers, two rows on the SAME number
    (this module's own cross-row grouping either way), and daily.py's own
    same-number same-day merge, where ONE row's `seconds` already
    includes a `callback_seconds` sub-total folded in by build_metrics --
    see daily.py's inbound-callback merge for exactly where that field is
    set. A single ordinary call returns a one-element list.

    Ordering: day_calls.producer_dials() (raw_dials) is OUTBOUND ONLY, so
    it can only ever place an outbound row by its actual dial time; an
    inbound row on a number the producer never dialed has no timestamp to
    sort by there. Two rows on the SAME number also tie (both look up the
    identical raw_dials entry). Both cases fall back to outbound-before-
    inbound, the same convention call_summary._wanted() already uses when
    it orders same-number legs for transcription.
    """
    if len(group) == 1:
        r = group[0]
        cb = r.get("callback_seconds")
        if cb:
            return [max((r.get("seconds") or 0) - cb, 0), cb]
        return [r.get("seconds") or 0]
    ordered = sorted(group, key=lambda r: (
        _earliest_start(raw_dials, producer, r["number"]) or "9999",
        bool(r.get("inbound"))))
    return [r.get("seconds") or 0 for r in ordered]


def _callback_kind(producer, group):
    """"call back" / "call in" / None -- what kind of repeat contact this
    card represents, matching the email digest's own wording for the same
    situation (Frank, 2026-09-15: "did we lose that when we moved over to
    the board... it should specify under the clients name if... its a call
    back"). None when there's only one real conversation.

    Over `group`'s raw rows, same as _call_times -- a same-number pair is
    still two real calls, not one (see that function's docstring).

    daily.py's own same-number merge (see _call_times) only ever folds an
    inbound leg into an existing OUTBOUND row when that leg's own `kind`
    is "callback" -- so callback_seconds being set always means a genuine
    call back, never a cold call-in, by construction. For this module's
    own cross-row grouping, the inbound row's own `kind` decides, exactly
    like the email's badge did.
    """
    if len(group) == 1:
        return "call back" if group[0].get("callback_seconds") else None
    inbound = [r for r in group if r.get("inbound")]
    if not inbound:
        return None
    return "call back" if any(r.get("kind") == "callback" for r in inbound) else "call in"


def _category(rows):
    """(label, category key) -- reuses panels.py's own nine-way Call Detail
    outcome (panels._call_category / digest_config.CALL_CATEGORIES), from
    the same mechanical facts daily.py already attaches to the row(s),
    never from the model's read of the call (Frank, 2026-09-16: "I had
    developed colored live contact cards based on if it was a follow up,
    quoted on that call, no quote but still open, lost and quoted, lost
    and not quoted. I want the coaching cards to follow those color rules,
    not the green yellow red rule we have right now").

    Coaching and the emailed Call Detail panel now colour and label the
    same call the same way, instead of Coaching running its own
    three-state approximation of the same thing.

    A merged (callback) card takes the BEST outcome across its rows,
    ranked by panels.CALL_CATEGORY_ORDER (sold beats quoted beats
    follow-up beats lost beats live-contact beats no-contact) -- a lead
    sold on the second of two calls still reads as sold, not whatever the
    first row alone would have said.
    """
    best = min(rows, key=panels._outcome_rank)
    key = panels._call_category(best)
    return panels._cat_label(key, best), key


def _tab(key):
    """Card accent colour -- the exact paint used for this same outcome in
    the Call Detail panel (digest_config.CALL_CATEGORIES), not a separate
    judgment call over the model's assumptive-language read. Replaces the
    former green/yellow/red-by-askq/asks rule (Frank, 2026-09-16 -- see
    _category's docstring)."""
    return cfg.CALL_CATEGORIES[key]["paint"]


def _bool_pair(raw):
    # The model sometimes answers with a bare true/false instead of the
    # [bool, reason] pair METHODOLOGY.md asks for -- 12 of 314 cached reads
    # did, and every one of them used to display "no" whatever it said
    # (Joaquin Guillen, 2026-09-22: "exit": true shown as "no").
    if isinstance(raw, bool):
        return [raw, ""]
    if not isinstance(raw, (list, tuple)) or not raw:
        return [False, ""]
    return [bool(raw[0]), str(raw[1]).strip() if len(raw) > 1 else ""]


CALLTYPE_VALUES = ("sales", "service", "mixed")


def _calltype(raw):
    """Apollo's own sales-vs-service judgment (Frank, 2026-09-10) -- distinct
    from _category() above, which is a mechanically-computed deal-stage badge.
    Defaults to "sales" (the pre-2026-09-10 assumption) if the model's value
    is missing or malformed, rather than dropping the field."""
    if isinstance(raw, (list, tuple)) and raw and str(raw[0]).lower() in CALLTYPE_VALUES:
        return [str(raw[0]).lower(), str(raw[1]).strip() if len(raw) > 1 else ""]
    # Same drift as _bool_pair: 42 of 314 cached reads returned a plain
    # string -- "service", or "sales -- <reason>" -- which used to fall
    # through to "sales", so 11 calls Apollo called pure service still got a
    # card. Read the leading word as the verdict, the rest as the reason.
    if isinstance(raw, str):
        m = re.match(r"\s*(sales|service|mixed)\b[\s,.:;\-\u2014\u2013]*(.*)", raw, re.I | re.S)
        if m:
            return [m.group(1).lower(), m.group(2).strip()]
    return ["sales", ""]


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


# Approximate scores for a cache entry written before this file moved from
# one shared "chipt" verdict to a per-objection 0-10 score -- see
# _clean_objs' `legacy` param. Never guessed for a card that HAS a real
# score; only stands in until that call's model read is refreshed.
_LEGACY_CHIPT_SCORE = {"Addressed, overcome": 9, "Addressed, kept going": 5,
                        "Addressed, not overcome": 2}


def _clean_objs(raw, legacy=None, cap=6):
    """Every distinct objection the model found, each scored 0-10 on its own
    (Frank, 2026-09-15: "I want them as their own badge, with a 0-10 score
    based on how well they attempted to overcome the objection" -- a card
    with a spousal-approval objection AND a separate mortgage/bundle
    objection gets two entries here, not one with the second folded into
    the first's "anal" text). `cap` guards against a runaway model response;
    no real call has raised more than a handful.

    `legacy` is the OLD single-object "obj" dict shape (with a "chipt"
    enum instead of "score") a cache entry written before this schema
    change still carries -- used only when `raw` (today's "objs" list) is
    absent, so a day whose model read hasn't been refreshed yet still
    shows the one real objection it has instead of going silently blank.
    Its score is approximated from "chipt" and is replaced by a real per-
    objection score the next time that call's model read happens.

    "addressed" and "score" are independent verdicts (Frank, 2026-09-15,
    re: Miguel Acosta -- ding the missing verbal acknowledgment without
    dragging down a score that reflects the objection actually being
    handled well in practice): never derive one from the other here, only
    read whatever pair of values the model actually gave.
    """
    if not isinstance(raw, list):
        raw = [legacy] if isinstance(legacy, dict) else []
    out = []
    for item in raw[:cap]:
        if not isinstance(item, dict):
            continue
        cat = str(item.get("cat") or "").strip()
        they = str(item.get("they") or "").strip()
        you = str(item.get("you") or "").strip()
        if not cat or not they:
            continue
        try:
            score = max(0, min(10, int(round(float(item.get("score"))))))
        except (TypeError, ValueError):
            score = _LEGACY_CHIPT_SCORE.get(item.get("chipt"))
        # The model's own group when it gave a valid one (METHODOLOGY.md's
        # "group" key); a card read before that key existed, or an invented
        # group name, falls back to the keyword rules.
        group = str(item.get("group") or "").strip()
        if group not in cfg.OBJECTION_GROUPS:
            group = cfg.objection_group(cat)
        out.append({
            "cat": cat, "group": group, "at": str(item.get("at") or "").strip(),
            "they": they, "theyen": str(item.get("theyen") or "").strip(),
            "you": you, "youen": str(item.get("youen") or "").strip(),
            "noresp": bool(item.get("noresp")),
            "addressed": bool(item.get("addressed")),
            "score": score,
            "anal": str(item.get("anal") or "").strip(),
            "fix": [str(f).strip() for f in item.get("fix") if str(f).strip()][:3]
                   if isinstance(item.get("fix"), list) else [],
        })
    return out


def _call_breakdown(producer, group, raw_dials):
    """One entry per real conversation on this card, [{"cat", "catc", "kind"},
    ...], in the same chronological order as _call_times -- each call's own
    outcome and its own call-in/call-back kind, read off THAT call's row,
    never the group's merged "best across all calls" cat/catc and never one
    kind label standing in for a card that can mix a cold call-in with a
    genuine call back (Frank, 2026-09-16: the outcome and call-in/call-back
    badges "are not on a single call" -- both were only ever computed once
    for the whole group, so a 2-call card showed one badge that didn't
    clearly belong to either conversation). A lone call still returns a
    single-element list, same shape, so the board needs no separate code
    path for the common case.

    Mirrors _call_times'/_callback_kind's own logic exactly (same
    same-number-split case, same sort key) so `calls[i]` always pairs with
    `call_times[i]`.
    """
    if len(group) == 1:
        r = group[0]
        key = panels._call_category(r)
        entry = {"cat": panels._cat_label(key, r), "catc": key}
        if r.get("callback_seconds"):
            return [dict(entry, kind=""), dict(entry, kind="call back")]
        return [dict(entry, kind="")]
    ordered = sorted(group, key=lambda r: (
        _earliest_start(raw_dials, producer, r["number"]) or "9999",
        bool(r.get("inbound"))))
    out = []
    for r in ordered:
        key = panels._call_category(r)
        kind = ""
        if r.get("inbound"):
            kind = "call back" if r.get("kind") == "callback" else "call in"
        out.append({"cat": panels._cat_label(key, r), "catc": key, "kind": kind})
    return out


def _finish_card(d, producer, group, raw_dials, day, transcript, recording_ids):
    """Merge the model's judgment with everything already known from the
    pipeline. Every mechanical field below is cheaper and more reliable to
    compute here than to ask the model for -- see the module docstring.

    `group` is a list of one or more call_detail rows: more than one when
    a second real conversation with the same lead that day -- a callback
    either direction -- is being coached together as one card (Frank,
    2026-09-15). Mechanical fields that only make sense per-call (lead
    name, lead source) take the first non-empty value across the group,
    since they describe the same person either way; `dur`/`time` combine
    across all of them.
    """
    askq = _bool_pair(d.get("askq"))
    asks = _bool_pair(d.get("asks"))
    # The producer ending a call with no objection, request to go, or time
    # constraint standing in the way (Frank, 2026-09-23). None, not
    # [False, ""], on a card read before METHODOLOGY.md had the key, so the
    # board can leave the row off rather than claim "no" it never checked.
    exit_ = _bool_pair(d.get("exit")) if "exit" in d else None
    cat, catc = _category(group)
    lead = next((r.get("lead") for r in group if r.get("lead")), "") or ""
    # AgencyZoom lead id, straight off the same call_detail rows day_calls.
    # classify()/daily.py already resolved it onto by phone number -- no new
    # lookup here (Frank, 2026-09-15: "i want links to AZ on the coaching
    # cards ... on the lead/client name"). It is a LEAD id even for a sold
    # lead: AgencyZoom leads don't stop existing on conversion (CLAUDE.md's
    # own money rules already lean on lead.status==2 staying queryable), so
    # app.agencyzoom.com/lead?id=<this> resolves whether the lead is still
    # open or long since sold.
    lead_id = next((r.get("lead_id") for r in group if r.get("lead_id")), None)
    leadsrc = next((r.get("lead_source") for r in group if r.get("lead_source")), "") or ""
    numbers = [r["number"] for r in group]
    total_seconds = sum(r.get("seconds") or 0 for r in group)
    return {
        "day": day,
        # The machine transcript this card was read from, and the raw
        # RingCentral recording id(s) (call_summary._audio_legs' own
        # `_wanted` picks) behind it, so the board can offer "read the
        # transcript" / "listen to the call" on the card itself (Frank,
        # 2026-09-14) instead of the summary being the only way to check
        # Apollo's read against the actual call. recording_ids is [] for
        # a day built before this existed (see call_summary.build) or a
        # row _wanted() found no usable leg for. Both cover the WHOLE
        # group when call_count > 1 -- one per call, in order.
        "transcript": transcript,
        "recording_ids": recording_ids,
        "lead": lead,
        "lead_id": lead_id,
        # Full name, not first name: coachingPanel() (site/public/index.html)
        # groups cards by matching `who` against its own `order` list of full
        # producer names -- a first-name-only value matches nothing, so every
        # card silently fails the filter and the tab renders as if there were
        # no cards at all (found 2026-09-10, 18 real cards on 2026-09-09 all
        # invisible this way, first ever real day the automated pipeline ran).
        "who": producer,
        "time": _call_time(raw_dials, producer, numbers),
        "dur": _dur(total_seconds),
        # Per-call talk-time split, earliest first, and what kind of repeat
        # contact this is (Frank, 2026-09-15: "should show 1st talk time +
        # 2nd talk time to know the split... specify under the clients name
        # if its 2 calls, if its a call back"). call_count is len(call_times),
        # not len(group) -- a same-number merge is ONE call_detail row that
        # still represents two real conversations (see _call_times).
        "call_times": [_dur(s) for s in _call_times(producer, group, raw_dials)],
        "call_count": len(_call_times(producer, group, raw_dials)),
        "callback_kind": _callback_kind(producer, group),
        # Per-call outcome + kind, same order as call_times above -- see
        # _call_breakdown's own docstring for why this exists alongside
        # callback_kind/cat/catc rather than replacing them: those two stay
        # as the card-level "best across all calls" summary (used for the
        # left border, filtering and the day-level scan stats), while this
        # is what the board now badges each individual call with.
        "calls": _call_breakdown(producer, group, raw_dials),
        # AgencyZoom's own leadSourceName, not the Google Sheet's (Frank,
        # 2026-09-12) -- blank when the call never resolved to a lead record.
        "leadsrc": leadsrc,
        "lang": str(d.get("lang") or "").strip() or "English",
        "src": "recording",
        "cat": cat, "catc": catc,
        "tab": _tab(catc),
        "calltype": _calltype(d.get("calltype")),
        "summary": str(d.get("summary") or "").strip(),
        "askq": askq, "asks": asks, "exit": exit_,
        "askfix": str(d.get("askfix") or "").strip(),
        "objs": _clean_objs(d.get("objs"), d.get("obj")),
        "good": _clean_pairs(d.get("good")),
        "bad": _clean_pairs(d.get("bad")),
        "score": _clean_score(d.get("score")),
        "techniques": _clean_score(d.get("techniques"), TECH_DIMS),
        "spine": _clean_spine(d.get("spine")),
        "flags": [str(f).strip() for f in (d.get("flags") or []) if str(f).strip()][:6],
    }


def _distinct_calls(producer, group):
    """One row per distinct (producer, number) in the group, first-seen kept
    as the representative.

    ONLY for what gets READ/PLAYED (the paid model call, the transcript
    text, the recording players) -- NOT for whether this was "2 calls":
    see _call_times/_callback_kind, which count every row in `group`
    regardless of number (Frank, 2026-09-15: "it shouldn't need to be 2
    different numbers, it can be from the same number a call back").

    Guards a real, narrow, pre-existing quirk: two call_detail rows can
    share one number (seen in real 2026-09-11 data -- an outbound dial and
    an unrelated same-day cold call-in that happened to land on the same
    number). call_summary.py caches its read by (producer, number), so both
    rows can only ever have fetched the identical transcript/summary --
    reading/showing it twice under two "[Call N of M]" tags would just be
    the same text twice, not a second call's worth of content. Duration
    still sums every row in the group (see _finish_card); only which CALLS
    get a separate paid read / transcript segment narrows here."""
    seen = {}
    for r in group:
        seen.setdefault(CS._ck(producer, r["number"]), r)
    return list(seen.values())


def _group_ck(producer, group):
    """Cache key for one coaching card: a single row's own call_summary._ck
    for a lone call, or a stable combined key when 2+ DISTINCT calls with
    the same lead_id are being coached together (Frank, 2026-09-15) --
    sorted so the key is stable regardless of which row was seen first."""
    distinct = _distinct_calls(producer, group)
    if len(distinct) == 1:
        return CS._ck(producer, distinct[0]["number"])
    return producer + "||" + "+".join(sorted(r["number"] for r in distinct))


def _group_transcript(producer, group, fx):
    """The transcript text this card is read from and displays -- one call's
    text unchanged, or every DISTINCT call's text concatenated and tagged
    with which call it is, in order, when coaching 2+ calls together. A leg
    with no transcript on file (shouldn't happen for a row that reached
    this point, but cheap to guard) is skipped rather than leaving a blank
    tagged section."""
    distinct = _distinct_calls(producer, group)
    multi = len(distinct) > 1
    segs = []
    for j, r in enumerate(distinct, 1):
        text = fx.get(CS._ck(producer, r["number"]), "")
        if not text:
            continue
        if multi:
            tag = (f"[Call {j} of {len(distinct)} -- "
                   f"{'inbound' if r.get('inbound') else 'outbound'}, "
                   f"{_dur(r.get('seconds'))}]")
            segs.append(f"{tag}\n{text}")
        else:
            segs.append(text)
    return "\n\n".join(segs)


def _group_recordings(producer, group, audiorefs):
    """recording_ids for every DISTINCT call in the group, in order --
    audiorefs.get() already returns [] for a call with no usable leg, so
    this just concatenates whatever each distinct call actually has (see
    _distinct_calls for why "distinct" and not every row)."""
    ids = []
    for r in _distinct_calls(producer, group):
        ids += audiorefs.get(CS._ck(producer, r["number"]), [])
    return ids


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
    ar_path = ROOT / f"data/audiorefs_{day}.json"
    audiorefs = json.loads(ar_path.read_text()) if ar_path.exists() else {}

    rows = [(p, r) for p, v in M.get("producers", {}).items()
            for r in v.get("call_detail", [])
            if (r.get("summary") or {}).get("source") == "recording"]

    # GROUPED BY (producer, lead_id): a second real conversation with the
    # same lead that day -- whether the producer called them back or they
    # called back on their own -- becomes ONE coaching card covering both,
    # not two (Frank, 2026-09-15: "it should be on the same coaching card,
    # saying its 2 calls coached together"). This only ever groups rows
    # that already reached call_detail as SEPARATE entries: a same-
    # direction repeat to the same lead is already collapsed to one row
    # upstream by daily.py's own _one_row_per_lead (settled contact-rate
    # math, untouched here); what actually groups here is the cross-
    # direction case that function deliberately leaves as two rows in its
    # own words ("an inbound row is never merged into an outbound one").
    # Rows with no lead_id can't be shown to be the same person, so each
    # stays a group of one -- exactly today's per-call behaviour.
    groups = {}
    for p, r in rows:
        lid = r.get("lead_id")
        gkey = (p, lid) if lid is not None else (p, id(r))
        groups.setdefault(gkey, (p, []))[1].append(r)
    group_list = [(p, grp) for p, grp in groups.values()]

    todo = [(p, grp) for p, grp in group_list if _group_ck(p, grp) not in cache]

    if todo:
        model = CS.pick_model()
        log(f"  writing {len(todo)} coaching cards with {model}...")
        for i, (p, grp) in enumerate(todo, 1):
            gck = _group_ck(p, grp)
            text = _group_transcript(p, grp, fx)
            total_seconds = sum(r.get("seconds") or 0 for r in grp)
            lead_name = next((r.get("lead") for r in grp if r.get("lead")), "") or ""
            ok, why = CS.usable(text, total_seconds)
            if not ok:
                log(f"    {lead_name}: {why} -- no card")
                continue
            notes = " / ".join(
                n for n in ((r.get("note_producer") or "").replace("&middot;", ";").strip()
                            for r in grp) if n)
            try:
                d = _ask_card(model, text[:16000], notes, total_seconds,
                             p.split()[0], lead_name,
                             call_count=len(_distinct_calls(p, grp)))
                cache[gck] = d
            except Exception as e:
                log(f"    {lead_name}: coaching read failed ({type(e).__name__}) -- no card")
            if i % 5 == 0:
                log(f"    {i}/{len(todo)}")
        cpath.write_text(json.dumps(cache, indent=1))

    raw_dials = day_calls.producer_dials(day)
    pairs = [(p, _finish_card(cache[_group_ck(p, grp)], p, grp, raw_dials, day,
                               _group_transcript(p, grp, fx),
                               _group_recordings(p, grp, audiorefs)))
             for p, grp in group_list if _group_ck(p, grp) in cache]
    rank = {name: i for i, name in enumerate(ROSTER_ORDER)}
    pairs.sort(key=lambda pc: rank.get(pc[0], 99))
    all_cards = [c for _, c in pairs]
    # This list is coaching for new-business opportunities, not a service-desk
    # log (Frank, 2026-09-14: "If those are pure service calls with no sales
    # opportunity, they should not be on that coaching list, that is purely
    # for new business opportunities"). A "mixed" call keeps a real cross-sell
    # attempt per Core judgment, so only "service" -- pure renewal/payment/
    # claim/paperwork, per calltype's own definition -- drops here. The read
    # is still paid for and cached above for every live contact regardless
    # (COST note up top): this filters what gets DISPLAYED, not what gets
    # summarized, since calltype isn't known until after the model reads it.
    cards = [c for c in all_cards if c.get("calltype", ["sales", ""])[0] != "service"]
    dropped = len(all_cards) - len(cards)
    combined = sum(1 for c in cards if c.get("call_count", 1) > 1)
    log(f"  coaching cards: {len(cards)} for {day}"
        + (f" ({dropped} pure-service calls filtered out)" if dropped else "")
        + (f" ({combined} combining 2+ calls)" if combined else ""))
    return cards


def split_by_lead_source(cards):
    """(coached, not_coached). A call on a lead source the guide marks as not
    coached -- a center of influence or cold / misc (Frank, 2026-09-24: "we
    barely use them and center of influence we dont even talk to the client,
    only the referral partner"), a one-off, a commercial source, a BOB or
    Rewrite -- leaves the coaching cards entirely, so it cannot reach scan(),
    objcats(), the objection chart or Role Play's weak spots. What is left
    of it is one line naming the call and why, for the Coaching Center's note."""
    import lead_sources
    coached, skipped = [], []
    for c in cards or []:
        src = c.get("leadsrc") or ""
        if lead_sources.coached(src):
            coached.append(c)
            continue
        skipped.append({
            "day": c.get("day"), "who": c.get("who"), "lead": c.get("lead"),
            "lead_id": c.get("lead_id"), "time": c.get("time"),
            "leadsrc": src.strip(), "group": lead_sources.group(src)["label"],
        })
    return coached, skipped


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
        # A quote went out ON THIS CALL -- sold, or quoted today whether
        # still open or since lost. A follow-up call chasing an
        # ALREADY-out quote (followup_open/followup_lost) doesn't count;
        # this call didn't do the pricing. Keys match cfg.CALL_CATEGORIES.
        "priced": sum(1 for c in cards if c.get("catc") in
                      ("sold_on_call", "quoted_call_open", "quoted_call_lost")),
        "closed": sum(1 for c in cards if c.get("catc") == "sold_on_call"),
        "premium": strong("Current premium captured"),
        "xdate": strong("Renewal / X-date captured"),
        "bundle": strong("Bundle / cross-sell raised"),
        "timeset": strong("Next step specificity"),
    }


def objcats(cards):
    """[[group, raised, won], ...] by objection GROUP (cfg.OBJECTION_GROUPS),
    not the free-text label -- "won" means a strong resolution
    (score 8+ out of 10), one row per objection now that a card can carry
    several (Frank, 2026-09-15: each objection scored on its own, not one
    shared addressed/overcome verdict for the whole card)."""
    agg = {}
    for c in cards:
        for o in c.get("objs") or []:
            g = o.get("group") or cfg.objection_group(o["cat"])
            raised, won = agg.get(g, (0, 0))
            agg[g] = (raised + 1, won + (1 if (o.get("score") or 0) >= 8 else 0))
    return sorted(([cat, n, w] for cat, (n, w) in agg.items()), key=lambda row: -row[1])


if __name__ == "__main__":
    import sys
    d = sys.argv[1] if len(sys.argv) > 1 else dt.datetime.now(AZ).date().isoformat()
    print(json.dumps(build(d), indent=1, default=str))
