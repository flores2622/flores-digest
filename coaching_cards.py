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
import lead_history
import pipelines
import staff

ROOT = pathlib.Path(__file__).resolve().parent
AZ = staff.TZ

METHODOLOGY = (ROOT / "coaching/METHODOLOGY.md").read_text()

# The card schema (spine, 9-dim scorecard, 6-technique scorecard, objection
# deep-dive, strengths and gaps) is much richer than call_summary.py's
# one-paragraph read, so it needs a much bigger budget. Sized off a 15-20
# minute call's worth of transcript; the retry tier exists for the same
# reason call_summary.py's does -- a long call can still fill the first
# budget with thinking or run past it. Bumped 2026-09-10 when "techniques"
# (6 more scored dimensions) was added to the schema, and to 9000 on
# 2026-09-30: a reply bills only the tokens it writes, so the higher first
# ceiling costs nothing on a normal card and saves the retry on a long one.
MAX_TOKENS = 9000
# 16000 since 2026-09-28: a two-call card (Joaquin Guillen, 09-22) ran past
# 8000 and came back with no JSON even with thinking off. A reply only bills
# the tokens it writes, so the bigger ceiling costs nothing on a normal card.
RETRY_TOKENS = 16000

DIMS = ["Opening & identification", "Discovery", "Current premium captured",
        "Renewal / X-date captured", "Product knowledge", "Presenting numbers",
        "Bundle / cross-sell raised", "Next step specificity", "CRM after the call"]

# Named sales techniques (Frank, 2026-09-10) -- same [letter, detail] shape as
# DIMS/score above, scored separately because these are about WHICH technique
# a producer reached for, not the mechanical call-flow checklist above.
TECH_DIMS = ["Elevator pitch", "Feel-Felt-Found", "Risk reversal",
             "Social proof", "Trial close", "Takeaway / urgency"]

# A follow-up has its own scorecard (Frank, 2026-09-25: "follow ups should
# have their own score card ... based off of the steps we just decided on")
# -- the steps in METHODOLOGY.md's "Follow-ups and call backs", in order,
# replacing DIMS on those cards. The quote is already done, so nothing here
# asks whether it was assumed; the SALE is assumed three times. A call back
# is scored on this only when it IS a follow-up: "a call back doesnt
# necessarily have to be a follow up" (Frank, 2026-09-25) -- `flow` is what
# the call was for, and who dialled is `direction`.
FU_DIMS = ["Reconnect & assumed the sale up front", "Checked where they are",
           "Handled what stalled it, assuming the sale", "Re-presented only what's needed",
           "Assumed the sale at the end", "Dated next step"]
FU_FLOWS = ("follow-up",)

def _ask_card(model, transcript, notes, seconds, producer, lead, call_count=1,
              lead_source="", stage_block="", history_block=""):
    # The lead source and the agency's approach for it (Frank, 2026-09-24:
    # coaching reads judged by lead source). Facts from lead_sources.py;
    # METHODOLOGY.md's "Lead source" section says how to use them.
    import lead_sources
    source_block = lead_sources.prompt_block(lead_source) or \
        "Lead source: unknown (the call did not resolve to a lead with a source)"
    length_line = (f"Call length: {seconds} seconds" if call_count == 1 else
                   f"Total length across {call_count} calls with this same lead "
                   f"today: {seconds} seconds -- read the transcript below as ONE "
                   f"continuing relationship, in the order the calls happened")
    n_legs = len(LEG_HEAD.findall(transcript or ""))
    if n_legs > 1:
        length_line += (f"\nThis transcript holds {n_legs} calls -- return `legs` with EXACTLY {n_legs} entries, "
                        f"one per header in order, even for a call of only a few words")
    msg = [{"role": "user", "content":
            f"Producer on this call: {producer}\n"
            f"Lead: {lead or '(name unknown)'}\n"
            f"{length_line}\n\n"
            f"{source_block}\n\n"
            f"{stage_block or 'Pipeline stage: unknown'}\n\n"
            f"{history_block or 'Lead history (before today): unavailable'}\n\n"
            f"Producer's own notes (may be empty):\n{notes or '(none)'}\n\n"
            f"Machine transcript:\n{transcript}"}]
    base = {"model": model, "system": METHODOLOGY + lessons_block(), "messages": msg}

    # Same two failure modes as call_summary._ask, same fix -- see that
    # function's docstring for why thinking is disabled and truncation gets
    # one retry with a bigger budget.
    think = {"thinking": {"type": "disabled"}}
    try:
        resp = CS._post(dict(base, max_tokens=MAX_TOKENS, **think))
    except RuntimeError as e:
        if "thinking" not in str(e).lower():
            raise
        think = {}
        resp = CS._post(dict(base, max_tokens=RETRY_TOKENS))

    d = CS._extract(resp)
    if d is None:
        # The retry keeps thinking off too, or it thinks into its own budget.
        resp = CS._post(dict(base, max_tokens=RETRY_TOKENS, **think))
        d = CS._extract(resp)
    if d is None:
        raise ValueError("no JSON in response")
    # A follow-up read that left out its own scorecard (2 of 9 on 2026-09-22's
    # rebuild -- the model filled the nine-point `score` instead) is asked
    # once more, with its own answer in front of it.
    f = _flow(d.get("flow")) if "flow" in d else None
    if f and f[0] in FU_FLOWS and len(_clean_score(d.get("fuscore"), FU_DIMS)) < 3:
        fix = msg + [{"role": "assistant", "content": json.dumps(d, ensure_ascii=False)},
                     {"role": "user", "content":
                      "You set flow to follow-up but did not score `fuscore`. Return the whole JSON "
                      "object again, the same read, with `fuscore` scoring the six follow-up steps, "
                      "`assume` for the three moments, and `score` as {} (see \"Scoring a follow-up\")."}]
        try:
            d2 = CS._extract(CS._post(dict(base, messages=fix, max_tokens=RETRY_TOKENS,
                                           thinking={"type": "disabled"})))
        except Exception:
            d2 = None
        if d2 and len(_clean_score(d2.get("fuscore"), FU_DIMS)) >= 3:
            d = d2
    return d


# Each recorded conversation on a card opens with call_summary's own header, "[outbound call, 2m09s" /
# "[inbound call, 0m33s -- ONLY THE OPENING ...]" -- the card's Call 1, Call 2 ... in the order they happened.
LEG_HEAD = re.compile(r"^\[(outbound|inbound) call, (\d+)m(\d+)s", re.M)


def _legs(d, producer, group, transcript, legmeta):
    """Call 1, Call 2 ... on one card (Frank, 2026-10-05: "if we can make a call 1 and call 2 on the same card
    that would be ideal"): one entry per recorded conversation in the transcript, in order, with its direction,
    talk time, clock time (call_summary's legmeta, matched by direction and length) and, when Apollo judged the
    calls one by one (`legs`, reads from 2026-10-05), that call's own outcome. [] for a single call."""
    heads = [(m.group(1), int(m.group(2)) * 60 + int(m.group(3))) for m in LEG_HEAD.finditer(transcript or "")]
    if len(heads) < 2:
        return []
    meta = []
    for r in _distinct_calls(producer, group):
        meta += legmeta.get(CS._ck(producer, r["number"]), [])
    said = d.get("legs") if isinstance(d.get("legs"), list) and len(d.get("legs")) == len(heads) else None
    out = []
    for i, (direction, secs) in enumerate(heads):
        at = ""
        for j, m in enumerate(meta):
            if m and m[0] == direction and abs((m[1] or 0) - secs) <= 1:
                try:
                    at = dt.datetime.fromisoformat(m[2].replace("Z", "+00:00")).astimezone(AZ).strftime("%-I:%M %p")
                except (TypeError, ValueError, AttributeError):
                    at = ""
                meta[j] = None
                break
        leg = {"n": i + 1, "dir": direction, "dur": _dur(secs), "at": at}
        v = said[i] if said else None
        key = v[0] if isinstance(v, (list, tuple)) and v else v
        if isinstance(key, str) and key in cfg.CALL_CATEGORIES:
            leg.update(oc=key, cat=panels._cat_label(key),
                       why=(v[1] if isinstance(v, (list, tuple)) and len(v) > 1 else "") or "")
        out.append(leg)
    return out


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


_TRUE = {"true", "yes", "y", "1"}
_FALSE = {"false", "no", "n", "0"}
_NULL = {"null", "none", "n/a", "na", "", "unclear", "not applicable"}


def _truth(v):
    """True / False / None from whatever the model put in a verdict's place.
    Strings map explicitly -- bool("false") is True, which is how a quoted
    "false" used to read as yes -- and anything unrecognised is None, never
    a guess either way."""
    if v is None or isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    t = str(v).strip().lower()
    if t in _NULL:
        return None
    return True if t in _TRUE else False if t in _FALSE else None


def _bool_pair(raw):
    """[True/False/None, reason] for a [verdict, reason] field.

    The model sometimes answers with a bare true/false instead of the
    [bool, reason] pair METHODOLOGY.md asks for -- 12 of 314 cached reads
    did, and every one of them used to display "no" whatever it said
    (Joaquin Guillen, 2026-09-22: "exit": true shown as "no"). A bare or
    quoted null, "n/a", or nothing at all is None -- counted neither way --
    never False (2026-09-30); so is "true - reason" read as one string."""
    if isinstance(raw, (list, tuple)):
        if not raw:
            return [None, ""]
        return [_truth(raw[0]), str(raw[1]).strip() if len(raw) > 1 and raw[1] is not None else ""]
    if isinstance(raw, str):
        m = re.match(r"\s*(true|false|yes|no|null|none|n/a)\b[\s,.:;\-—–]*(.*)", raw, re.I | re.S)
        if m:
            return [_truth(m.group(1)), m.group(2).strip()]
        return [None, raw.strip()]
    if isinstance(raw, dict):
        v = next((raw[k] for k in ("verdict", "value", "answer") if k in raw), None)
        return [_truth(v), str(raw.get("reason") or raw.get("why") or "").strip()]
    return [_truth(raw), ""]


def _verdict(raw):
    """[True/False/None, reason]: a null verdict stays None -- no chance to
    assume (Frank, 2026-09-28). The same reading as _bool_pair since
    2026-09-30, kept as its own name for the callers that mean that."""
    return _bool_pair(raw)


SENDOFF_KINDS = ("producer", "busy", "asked", "no")


def _sendoff(raw):
    """[kind, reason] -- did the quote get sent instead of presented on the
    call, and whose idea was it (Frank, 2026-09-28). kind is one of
    SENDOFF_KINDS; None when no quote came up, or the read left it out."""
    if isinstance(raw, str):
        # "producer -- I'll email it over" as one string (2026-09-30).
        m = re.match(r"\s*(producer|busy|asked|no)\b[\s,.:;\-\u2014\u2013]*(.*)", raw, re.I | re.S)
        return [m.group(1).lower(), m.group(2).strip()] if m else None
    if not isinstance(raw, (list, tuple)) or not raw or raw[0] is None:
        return None
    kind = str(raw[0]).strip().lower()
    return ([kind, str(raw[1]).strip() if len(raw) > 1 and raw[1] is not None else ""]
            if kind in SENDOFF_KINDS else None)


# What the call was FOR, whoever dialled (Frank, 2026-09-25): a first
# conversation, a call to finish the quote now that the info is in, or a
# follow-up on a quote already presented.
FLOW_VALUES = ("first", "finish quote", "follow-up")
# Read before the call's purpose was split from who dialled: a "call back"
# was then always coached as a follow-up, a "call in" as a first call.
_OLD_FLOWS = {"call back": "follow-up", "call in": "first"}


_FLOW_RE = re.compile(
    r"\s*(first(?:[ _-](?:conversation|call|contact|time))?|finish(?:ing)?[ _-](?:the[ _-])?quote|"
    r"follow[ _-]?up|call[ _-]?back|call[ _-]?in)\b[\s,.:;\-\u2014\u2013]*(.*)", re.I | re.S)


def _flow_kind(text):
    """(kind, rest) for a flow written any of the ways the model writes it --
    "follow up", "followup", "Follow-Up", "first conversation", "finishing
    the quote", the old "call back" / "call in" -- or (None, "")."""
    m = _FLOW_RE.match(str(text or ""))
    if not m:
        return None, ""
    k = re.sub(r"[ _-]+", " ", m.group(1).lower())
    kind = ("first" if k.startswith("first") else "finish quote" if k.startswith("finish")
            else "follow-up" if k.startswith("follow") else _OLD_FLOWS.get(k.replace("callback", "call back")
                                                                           .replace("callin", "call in")))
    return kind, m.group(2).strip()


def _flow(raw):
    """Apollo's [kind, reason] for what this conversation was for in the
    sale; None when missing or malformed, so the card simply leaves it off.
    The list form and the string form go through the same reading
    (2026-09-30): ["follow up", ...] used to be dropped."""
    kind, why = None, ""
    if isinstance(raw, (list, tuple)) and raw:
        kind, _ = _flow_kind(raw[0])
        why = str(raw[1]).strip() if len(raw) > 1 and raw[1] is not None else ""
    elif isinstance(raw, str):
        kind, why = _flow_kind(raw)
    return [kind, why] if kind in FLOW_VALUES else None


def _assume(raw):
    """{"start", "objections", "end"} -> [bool|None, reason]. "objections" is
    None when no objection was raised (nothing to assume through)."""
    out = {}
    if not isinstance(raw, dict):
        return None
    for k in ("start", "objections", "end"):
        v = raw.get(k)
        if v is not None:
            out[k] = _verdict(v)
    return out or None


# The front desk's script. On a producer's card it is Debbie picking up the
# main line before the transfer, never the producer's greeting -- unless the
# transcript itself labels the producer saying it on their own line.
FRONT_DESK = re.compile(
    r"thank(s| you) for calling|gracias por (llamar|su llamada)|"
    r"(farmers|flores)( insurance)?,? (this is \w+,? )?how (can|may) i help", re.I)
# Staff first names as a transcript spells them -> who that is.
STAFF_NAMES = {"crystal": "crystal", "cristal": "crystal", "lorena": "lorena",
               "mike": "mike", "coral": "coral", "sarahi": "sarahi", "sarai": "sarahi",
               "debbie": "debbie", "amanda": "amanda", "frank": "frank",
               "francisco": "francisco", "veronica": "veronica"}
# The tag call_summary.build puts on an inbound leg whose recording stopped at
# the park: only the front desk's side of the call exists.
OPENING_ONLY = "ONLY THE OPENING WAS RECORDED"
_LEG_TAG = re.compile(r"\[(inbound|outbound) call,[^\]]*\]")


def _pickup_missing(transcript):
    """True when every inbound leg in the transcript is tagged as holding only
    the front desk's opening -- the producer's pick-up was never recorded."""
    tags = [m.group(0) for m in _LEG_TAG.finditer(transcript or "") if m.group(1) == "inbound"]
    return bool(tags) and all(OPENING_ONLY in t for t in tags)


def _speaker_of(first, transcript):
    """The label on the transcript line the quoted first sentence comes from
    ("Mike (producer)", "Speaker 1", ...), or None when it cannot be found
    (an older transcript with no labels, or a loose quote)."""
    import deepgram_stt
    want = re.sub(r"\W+", " ", first.lower()).strip()[:40]
    if len(want) < 4:
        return None
    for line in (transcript or "").splitlines():
        m = deepgram_stt.LINE.match(line.strip())
        if m and want in re.sub(r"\W+", " ", m.group("text").lower()):
            return m.group("who").strip()
    return None


def _greeting(raw, producer="", transcript="", route=None):
    """[letter, detail] for the pick-up line on an answered call, scored on
    the PRODUCER's own words only (Frank, 2026-09-30).

    Apollo quotes the call's first sentence and says who said it. "n" --
    the pick-up wasn't recorded -- whatever letter came back, when:
      * `by` is anyone but the producer ("caller", "front desk"): on the
        first reads the model scored a caller's "Hi Crystal", and a call
        opening with the caller's own words, as the producer's greeting;
      * every inbound leg is tagged OPENING_ONLY (the recording stopped at
        the park, so only the front desk is on it);
      * the sentence names a staff member other than this producer ("This
        is Debbie"), or is on a line the transcript labels as the lead's or
        the customer's;
      * it is the front desk's script and nothing shows it is the producer's
        own -- a transferred call, or a line not labelled "(producer)"."""
    if isinstance(raw, dict):
        first = str(raw.get("first") or raw.get("line") or "").strip()
        by = str(raw.get("by") or "producer").strip().lower()
        sc = _clean_score({"x": raw.get("score")}, ["x"]).get("x")
        if not first or by != "producer":
            who = "the front desk" if "front" in by or "desk" in by else "the caller"
            return ["n", f"The pick-up wasn't recorded: the call opens with {who}."]
        if _pickup_missing(transcript):
            return ["n", "The pick-up wasn't recorded: only the front desk's opening was, "
                         "before the transfer."]
        mine = (producer or "").split()[0].lower() if producer else ""
        named = re.search(r"\b(this is|it'?s|soy|my name is|me llamo|habla)\s+(\w+)", first, re.I)
        who_named = STAFF_NAMES.get(named.group(2).lower()) if named else None
        if who_named and who_named != mine:
            return ["n", f"The pick-up wasn't recorded: \u201c{first}\u201d is {named.group(2).title()}, "
                         f"not the producer."]
        label = _speaker_of(first, transcript)
        if label and re.search(r"\((lead|customer|service)\)", label):
            return ["n", "The pick-up wasn't recorded: the call opens with the caller."]
        if FRONT_DESK.search(first) and (route == "transferred" or not (label and "(producer)" in label)):
            return ["n", "The pick-up wasn't recorded: the call opens with the front desk's greeting."]
        if not sc:
            return None
        if sc[0] == "n":
            return sc
        return [sc[0], f"\u201c{first}\u201d \u2014 {sc[1]}" if sc[1] else f"\u201c{first}\u201d"]
    if _pickup_missing(transcript):
        return ["n", "The pick-up wasn't recorded: only the front desk's opening was, before the transfer."]
    return _clean_score({"x": raw}, ["x"]).get("x")


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


# The model sometimes keys the scorecards in shorthand instead of the exact
# names METHODOLOGY.md asks for -- "opening", "crm", "next_step", "fff",
# "trial_close", or a full name in lower case. 27 of 343 cached reads did (a
# survey of every read in R2, 2026-09-24), and every such dimension used to be
# dropped, leaving the card's scorecard empty or "not scored". Each alias
# below is one actually seen in those reads, compared after _norm_key.
SCORE_ALIASES = {
    "Opening & identification": ("opening",),
    "Discovery": ("discovery",),
    "Current premium captured": ("premium", "premiumcaptured", "currentpremium"),
    "Renewal / X-date captured": ("renewal", "renewalcaptured", "renewaldate", "xdate"),
    "Product knowledge": ("product",),
    "Presenting numbers": ("numbers", "numberspresented"),
    "Bundle / cross-sell raised": ("bundle", "crosssell", "bundlecrosssell"),
    "Next step specificity": ("nextstep",),
    "CRM after the call": ("crm", "crmafter"),
    "Elevator pitch": ("elevator", "pitch"),
    "Feel-Felt-Found": ("fff", "feltfound"),
    "Risk reversal": ("risk",),
    "Social proof": ("social",),
    "Trial close": ("trial",),
    "Takeaway / urgency": ("urgency", "takeaway"),
    "Reconnect & assumed the sale up front": ("reconnect", "reconnectassumed", "upfront", "assumedupfront"),
    "Checked where they are": ("checked", "checkwheretheyare", "wheretheyare"),
    "Handled what stalled it, assuming the sale": ("stalled", "handledstalled", "handledwhatstalledit"),
    "Re-presented only what's needed": ("represented", "represent", "representedonlywhatsneeded"),
    "Assumed the sale at the end": ("assumedend", "assumedtheend", "end"),
    "Dated next step": ("nextstep", "datednextstep"),
}


def _norm_key(k):
    return re.sub(r"[^a-z0-9]", "", str(k).lower())


def _clean_score(raw, dims=DIMS):
    out = {}
    if not isinstance(raw, dict):
        return out
    by_norm = {}
    for k, e in raw.items():
        by_norm.setdefault(_norm_key(k), e)
    for dim in dims:
        # The exact name wins; then the name in any case/punctuation; then a
        # shorthand the model has been seen to use for it.
        e = raw.get(dim)
        if e is None:
            for alias in (_norm_key(dim),) + SCORE_ALIASES.get(dim, ()):
                if alias in by_norm:
                    e = by_norm[alias]
                    break
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
        anal = str(item.get("anal") or "").strip()
        # An objection with no quote of the prospect is still an objection
        # Apollo found and scored (2026-09-30): it used to vanish from the
        # card and from objcats. Only an entry with nothing in it is dropped.
        if not (cat or they or you or anal):
            continue
        if not cat:
            g = str(item.get("group") or "").strip()
            cat = g if g in cfg.OBJECTION_GROUPS else "Objection"
        fix = item.get("fix")
        if isinstance(fix, str):
            fix = [fix]
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
            "noresp": _truth(item.get("noresp")) is True,
            "addressed": _truth(item.get("addressed")) is True,
            "score": score,
            "anal": anal,
            # One line as a plain string is still a fix (2026-09-30).
            "fix": [str(f).strip() for f in fix if f is not None and str(f).strip()][:3]
                   if isinstance(fix, (list, tuple)) else [],
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


def _history(producer, group, day, ctx, log=print):
    """lead_history.block, never raising: a card is still worth reading
    without its history."""
    try:
        text = lead_history.block(group, day, ctx, producer=producer)
    except Exception as e:
        log(f"    lead history: skipped ({type(e).__name__}: {e})")
        text = ""
    notes = manager_notes(day, group)
    return (text + "\n\n" + notes).strip() if notes else text


def manager_notes(day, group):
    """What Frank or a manager saw that the call cannot show -- an ALTA
    screen, a policy record -- for this card: coaching/manager_notes.json,
    plus the managers' sticky notes pinned to this lead's card that day
    (sticky_notes). The card cache is keyed by call, so a note reaches a
    card only when it is read (or re-read) after the note is written."""
    try:
        rows = json.loads((ROOT / "coaching/manager_notes.json").read_text())
    except (OSError, ValueError):
        rows = []
    ids = {r.get("lead_id") for r in group if r.get("lead_id") is not None}
    hits = [(n.get("by", "manager"), n.get("written", ""), n["note"]) for n in rows
            if n.get("day") == day and n.get("lead_id") in ids]
    hits += [(n.get("by", "manager"), str(n.get("at", ""))[:10], n["text"]) for n in sticky_notes()
             if n.get("day") == day and n.get("lead_id") in ids and n.get("text")]
    return "\n".join(f"Manager's note ({by}, {when}): {text}" for by, when, text in hits)


# The managers' sticky notes on coaching cards (Frank, 2026-10-02: "Any way
# apollo can learn from my sticky notes?"): written on the board, kept by the
# Worker in R2 (card-notes/notes.json), read once per run. Never fails a run.
_STICKY = None
LESSON_NOTES, LESSON_CHARS = 40, 9000


def sticky_notes(log=print):
    global _STICKY
    if _STICKY is None:
        try:
            import publish_board
            cli, bucket = publish_board._client()
            _STICKY = json.loads(cli.get_object(Bucket=bucket, Key="card-notes/notes.json")["Body"].read()).get("notes") or []
        except Exception as e:
            if "NoSuchKey" not in type(e).__name__ + str(e):
                log(f"  sticky notes: not read ({type(e).__name__}) -- cards are read without them")
            _STICKY = []
    return _STICKY


def lessons_block():
    """Every sticky note marked "Apollo learns this", newest first, as part
    of the instructions of every coaching read (METHODOLOGY.md's "Manager's
    sticky notes" says how to use them). Capped so the instructions stay a
    cacheable, steady prefix."""
    out, size = [], 0
    for n in sorted((n for n in sticky_notes() if n.get("teach") and n.get("text")),
                    key=lambda n: str(n.get("at", "")), reverse=True)[:LESSON_NOTES]:
        line = (f"- {n.get('by', 'Manager')}, {str(n.get('at', ''))[:10]}, on {n.get('who') or 'a producer'}'s "
                f"call with {(n.get('lead') or 'a lead').split()[0]} ({n.get('day', '')}): {n['text'].strip()}")
        if size + len(line) > LESSON_CHARS:
            break
        out.append(line); size += len(line)
    if not out:
        return ""
    return ("\n\n## The managers' sticky notes (lessons from earlier cards)\n\n"
            "Frank and the managers wrote these on earlier coaching cards and asked Apollo "
            "to learn from them. Apply the lesson wherever the call in front of you shows the "
            "same thing; they are not facts about this call.\n\n" + "\n".join(out))


_LEADS_BY_ID = None


def _corpus_day():
    """The Arizona day the lead snapshot was taken -- a card for an earlier
    day cannot read the lead's stage off it."""
    p = ROOT / "data/az_leads_all.json"
    if not p.exists():
        return ""
    return dt.datetime.fromtimestamp(p.stat().st_mtime, staff.TZ).date().isoformat()


def _group_stage(group, day=None):
    """(moves, stage_now, sold_today) for a card's rows -- what
    pipelines.call_stage/prompt_block read. Moves come off the rows (the
    producer's own MOVE_STAGE notes that day, daily.py); the lead's current
    stage off the day's lead corpus, which is the end-of-day snapshot. For a
    day OLDER than the snapshot (a rebuild, Frank 2026-09-27) the stage is
    read off the lead's own move history as of that day instead -- the
    snapshot would give where the lead sits today."""
    global _LEADS_BY_ID
    if _LEADS_BY_ID is None:
        p = ROOT / "data/az_leads_all.json"
        _LEADS_BY_ID = ({l.get("id"): l for l in json.loads(p.read_text())}
                        if p.exists() else {})
    moves = list(dict.fromkeys(m for r in group for m in (r.get("moves") or [])))
    lead_id = next((r.get("lead_id") for r in group if r.get("lead_id")), None)
    now = pipelines.current_stage(_LEADS_BY_ID.get(lead_id))
    if day and day < _corpus_day():
        import live_contact as lc
        ids = list(dict.fromkeys(r.get("lead_id") for r in group if r.get("lead_id")))
        now = pipelines.stage_as_of([n for i in ids for n in lc.load_notes(i)], day) or now
    return moves, now, any(r.get("sold_today") for r in group)


def _lead_group(leadsrc):
    """The lead-source guide's group label for the card ("" with no source)."""
    import lead_sources
    return lead_sources.group(leadsrc)["label"] if leadsrc.strip() else ""


def _finish_card(d, producer, group, raw_dials, day, transcript, recording_ids, ctx=None):
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
    # [None, reason] when the call never gave the producer the chance --
    # cut off, too short, not recorded -- so it counts neither way (Frank,
    # 2026-09-28: "it shouldnt count against them"). An early "no" before
    # the quote came up is an objection to work, not a lack of chance
    # (Frank, 2026-09-30): false unless the producer assumed the quote.
    askq = _verdict(d.get("askq"))
    asks = _verdict(d.get("asks"))
    # The producer ending a call with no objection, request to go, or time
    # constraint standing in the way (Frank, 2026-09-23). None, not
    # [False, ""], on a card read before METHODOLOGY.md had the key, so the
    # board can leave the row off rather than claim "no" it never checked.
    exit_ = _bool_pair(d.get("exit")) if "exit" in d else None
    # Did the producer work the lead the way its source calls for (Frank,
    # 2026-09-24)? None on a card read before METHODOLOGY.md asked, so the
    # board leaves the row off rather than show a verdict nobody gave.
    leadfit = _clean_score({"x": d.get("leadfit")}, ["x"]).get("x") if "leadfit" in d else None
    # Did the call do what the lead's stage called for (Frank, 2026-09-24)?
    # Same None-when-never-asked rule as leadfit.
    stagefit = _clean_score({"x": d.get("stagefit")}, ["x"]).get("x") if "stagefit" in d else None
    stage_before, stage_after = pipelines.call_stage(*_group_stage(group, day))
    # What the call was for -- first conversation, finishing the quote, or a
    # follow-up -- decided from the stage and history, not from who dialled
    # (Frank, 2026-09-25). None on a card read before METHODOLOGY.md asked.
    flow = _flow(d.get("flow")) if "flow" in d else None
    followup = bool(flow and flow[0] in FU_FLOWS)
    direction = lead_history.direction_key(group)
    # A call the producer answered: a direct, by-name greeting, not the
    # front desk's "thanks for calling Farmers" (Frank, 2026-09-25).
    # Scored on the producer's own words only (Frank, 2026-09-30): the front
    # desk's pick-up, an opening-only recording, or a line naming someone
    # else is "n" whatever the model said.
    greeting = (_greeting(d.get("greeting"), producer, transcript,
                          lead_history.answer_route(group, producer, ctx))
                if lead_history.answered(group) and "greeting" in d else None)
    # On a follow-up: the follow-up scorecard, and whether the
    # SALE was assumed at each of the three moments (start, objections, end)
    # in place of "assumed the quote" -- the quote is already done.
    fuscore = _clean_score(d.get("fuscore"), FU_DIMS) if followup else None
    assume = _assume(d.get("assume")) if followup and "assume" in d else None
    if followup:
        askq = None
    sendoff = _sendoff(d.get("sendoff"))
    askq = _askq_after_sendoff(askq, sendoff)
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
        # The recordings as timed, labelled turns -- the card's player jumps
        # to whichever line is clicked (Frank, 2026-09-29: "the transcript
        # and recording combined ... skip to a specific part that I am
        # reading"). Only for recordings Deepgram has read; [] otherwise,
        # and the card falls back to the plain transcript.
        "turns": _timed_turns(producer, lead, day, recording_ids),
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
        "leadgroup": _lead_group(leadsrc),
        "leadfit": leadfit,
        "stage_before": stage_before,
        "stage_after": stage_after,
        "stagefit": stagefit,
        "flow": flow,
        "direction": direction,
        "greeting": greeting,
        "fuscore": fuscore,
        "assume": assume,
        "lang": str(d.get("lang") or "").strip() or "English",
        "src": "recording",
        "cat": cat, "catc": catc,
        "tab": _tab(catc),
        "calltype": _calltype(d.get("calltype")),
        "summary": str(d.get("summary") or "").strip(),
        "askq": askq, "asks": asks, "exit": exit_,
        # Quote sent instead of presented, and whose idea (Frank, 2026-09-28).
        "sendoff": sendoff,
        "askfix": str(d.get("askfix") or "").strip(),
        "objs": _clean_objs(d.get("objs"), d.get("obj")),
        "good": _clean_pairs(d.get("good")),
        "bad": _clean_pairs(d.get("bad")),
        # A follow-up is scored on fuscore alone; any nine-dimension score the
        # model still returns would count in scan() as if it were a first call.
        "score": {} if fuscore else _answered_opening(_clean_score(d.get("score")), transcript),
        "techniques": _clean_score(d.get("techniques"), TECH_DIMS),
        "spine": _clean_spine(d.get("spine")),
        **_clean_flags(d.get("flags")),
        # Where Apollo was unsure, or heard something new (Frank, 2026-10-05).
        # Frank's alone: split_doubts takes it off the card before the day
        # is published, into review/<day>.json.
        "doubts": _clean_doubts(d.get("doubts")),
        # The model that read the card (2026-09-30); None on a card read
        # before it was kept.
        "model": d.get("_model"),
    }


def _askq_after_sendoff(askq, sendoff):
    """A producer who offered to send the quote on their own HAD the chance
    to assume it (Frank, 2026-09-30): `askq` cannot be null then. A null
    askq beside sendoff "producer" becomes false, with the sendoff's own
    reason. Only a [None, reason] askq changes -- a follow-up's askq (None,
    not a pair) does not apply at all."""
    if (isinstance(askq, list) and askq and askq[0] is None
            and sendoff and sendoff[0] == "producer"):
        why = sendoff[1] or "the producer offered to send the quote instead of presenting it"
        return [False, f"Set the quote up to be sent instead of presented on the call: {why}"]
    return askq


def _answered_opening(score, transcript):
    """On a card whose every recorded call is one the producer ANSWERED,
    "Opening & identification" is "n": the pick-up is scored as `greeting`
    (Frank, 2026-09-30). A card that holds a dial too keeps the letter."""
    dirs = [m.group(1) for m in _LEG_TAG.finditer(transcript or "")]
    if score and dirs and all(x == "inbound" for x in dirs) and "Opening & identification" in score:
        score = dict(score)
        score["Opening & identification"] = ["n", "An answered call: the pick-up is scored as "
                                                  "the greeting, not here."]
    return score


def _clean_doubts(raw):
    """[[kind, text], ...], kind "unsure" or "new"; at most 5."""
    out = []
    for x in raw or []:
        if isinstance(x, (list, tuple)) and len(x) >= 2:
            kind, text = str(x[0]).strip().lower(), str(x[1]).strip()
        elif isinstance(x, dict):
            kind, text = str(x.get("kind") or "").strip().lower(), str(x.get("text") or "").strip()
        else:
            continue
        if text and kind in ("unsure", "new"):
            out.append([kind, text[:400]])
    return out[:5]


def card_key(c):
    """The board's own key for a card (index.html cardKey -- keep in step)."""
    lid = c.get("lead_id")
    return f"{c.get('day') or ''}|{lid if lid is not None else 'n:' + (c.get('lead') or '')}|{c.get('who') or ''}"


def split_doubts(cards):
    """Take Apollo's doubts off the cards (they are Frank's alone and the day
    document is everyone's) and return them as {card_key: doubts}."""
    out = {}
    for c in cards or []:
        d = c.pop("doubts", None)
        if d:
            out[card_key(c)] = d
    return out


def _clean_flags(raw):
    """`flags` stays a list of strings (what every card already has), with
    `flag_groups` beside it: each flag's category from cfg.FLAG_GROUPS, or
    None when the model gave none or an invented one -- the board then
    guesses from the wording, as it does for cards read before the list."""
    import digest_config as cfg
    flags, groups = [], []
    for f in raw or []:
        if isinstance(f, (list, tuple)) and f:
            text, group = str(f[0]).strip(), str(f[1]).strip() if len(f) > 1 else ""
        elif isinstance(f, dict):
            text, group = str(f.get("text") or "").strip(), str(f.get("group") or "").strip()
        else:
            text, group = str(f).strip(), ""
        if not text:
            continue
        flags.append(text)
        groups.append(group if group in cfg.FLAG_GROUPS else None)
        if len(flags) == 6:
            break
    return {"flags": flags, "flag_groups": groups}


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


def _timed_turns(producer, lead, day, recording_ids):
    """[{"r": index into recording_ids, "t": seconds, "who", "text"}] from
    Deepgram's saved reads only -- never a new, paid read. Each leg is cut
    to the part the transcript used (an inbound call's producer leg starts
    at its offset), and times are into the recording itself, so the player
    seeks straight to them."""
    import deepgram_stt
    tpath = ROOT / f"data/transcripts_{day}.json"
    try:
        tx = json.loads(tpath.read_text()) if tpath.exists() else {}
    except ValueError:
        tx = {}
    out = []
    for i, rid in enumerate(recording_ids or []):
        v = tx.get(rid) or {}
        ts = deepgram_stt.turns(ROOT / f"data/audio/{rid}.mp3",
                                v.get("audio_seconds") or v.get("duration") or 0,
                                offset=v.get("offset") or 0, producer=producer,
                                lead=lead, cached_only=True, number=v.get("to"))
        out += [dict(x, r=i) for x in ts or []]
    return out


def _group_recordings(producer, group, audiorefs):
    """recording_ids for every DISTINCT call in the group, in order --
    audiorefs.get() already returns [] for a call with no usable leg, so
    this just concatenates whatever each distinct call actually has (see
    _distinct_calls for why "distinct" and not every row)."""
    ids = []
    for r in _distinct_calls(producer, group):
        ids += audiorefs.get(CS._ck(producer, r["number"]), [])
    return ids


ROSTER_ORDER = staff.order("coaching")   # staff.json


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
    lm_path = ROOT / f"data/legmeta_{day}.json"
    legmeta = json.loads(lm_path.read_text()) if lm_path.exists() else {}

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
        # What came before this call (lead_history.py): loaded once, only
        # when a card is actually being read.
        history_ctx = lead_history.Context(day, log=log, past=day < _corpus_day())
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
            src = next((r.get("lead_source") for r in grp if r.get("lead_source")), "") or ""
            try:
                # A long call is cut with a marker, never silently (2026-09-30:
                # it was text[:16000], which dropped the close off the end).
                d = _ask_card(model, CS.clip(text), notes, total_seconds,
                             p.split()[0], lead_name,
                             call_count=len(_distinct_calls(p, grp)),
                             lead_source=src,
                             stage_block=pipelines.prompt_block(*_group_stage(grp, day)),
                             history_block=_history(p, grp, day, history_ctx, log))
                # Which model read it, kept on the card (2026-09-30).
                cache[gck] = dict(d, _model=model)
                # Saved after EVERY card, as call_summary.build saves each
                # row (2026-09-30): a run killed partway through used to lose
                # every card it had already paid for, and the next run bought
                # them all again.
                cpath.write_text(json.dumps(cache, indent=1))
            except Exception as e:
                log(f"    {lead_name}: coaching read failed ({type(e).__name__}) -- no card")
            if i % 5 == 0:
                log(f"    {i}/{len(todo)}")
        cpath.write_text(json.dumps(cache, indent=1))

    raw_dials = day_calls.producer_dials(day)
    # Only the day's saved RC log (inbound.answered's transfer / direct route
    # for each call-in); nothing is fetched.
    route_ctx = lead_history.Context(day, log=log)
    def _card(p, grp):
        d, tx = cache[_group_ck(p, grp)], _group_transcript(p, grp, fx)
        c = _finish_card(d, p, grp, raw_dials, day, tx, _group_recordings(p, grp, audiorefs), ctx=route_ctx)
        legs = _legs(d, p, grp, tx, legmeta)
        if legs:
            c["legs"] = legs
        return c
    pairs = [(p, _card(p, grp)) for p, grp in group_list if _group_ck(p, grp) in cache]
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


def scan(cards):
    """The "What the day says" cross-call figures digestDay renders, computed
    straight off the generated cards -- mechanical, not a model read."""
    if not cards:
        return None
    def strong(dim):
        return sum(1 for c in cards if (c.get("score") or {}).get(dim, ["", ""])[0] == "s")
    return {
        "of": len(cards),
        # "Assumed the quote" only exists on a first conversation; a
        # follow-up's quote is already done (Frank, 2026-09-25).
        # A call that never reached the quote (askq [None, ...]) is in
        # neither count (Frank, 2026-09-28).
        "of_first": sum(1 for c in cards if c.get("askq") and c["askq"][0] is not None),
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
        "timeset": strong("Next step specificity") + sum(
            1 for c in cards if (c.get("fuscore") or {}).get("Dated next step", ["", ""])[0] == "s"),
        # Calls the producer answered, and how many opened direct and by name
        # (Frank, 2026-09-25).
        "greet_of": sum(1 for c in cards if c.get("greeting") and c["greeting"][0] != "n"),
        "greet_ok": sum(1 for c in cards if (c.get("greeting") or ["", ""])[0] == "s"),
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
