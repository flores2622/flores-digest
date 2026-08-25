"""Roster, exclusion rules, thresholds and per-day facts.

Every value here is a decision Frank has already made. HANDOFF_4 s12 lists the
ones that must not be re-asked. Section references below point back at it.
"""
import datetime as dt
import re

# --- time -------------------------------------------------------------------
AZ_TZ = dt.timezone(dt.timedelta(hours=-7))   # Arizona: UTC-7, never DST

# Send times, settled 2026-08-14. The ops slot moved 6:00 -> 6:30 PM because the
# Insightful API carries the live Arizona day, and at 6:00 PM a counted producer
# was still clocked in often enough to understate them by ~10% about one day in
# four. 6:30 PM caps the worst case under 3%. (See insightful_util.SEND_TIME_EVIDENCE.)
# BOTH emails go out together at 6:30 PM Arizona, same day (Frank, 2026-08-14).
# One build, one send. The earlier 8:00 AM staff slot is retired: it would have
# rebuilt the same reporting day in a separate container the next morning, and
# anything logged after 6:30 PM would have made the two copies of the same day
# disagree. Sending together makes them byte-identical by construction.
SEND_OPS_AZ = "18:30"      # = 01:30 UTC next day
SEND_STAFF_AZ = "18:30"    # same run, same moment

RECIPIENTS_OPS = ["frank@floresinsuranceagency.com",
                  "francisco@floresinsuranceagency.com",
                  "veronica@floresinsuranceagency.com",
                  "amanda@floresinsuranceagency.com"]
# Coral and Sarahi added to the staff list by Frank, 2026-08-14. They receive
# the digest even though they are excluded from every figure in it.
RECIPIENTS_STAFF = ["crystal@floresinsuranceagency.com",
                    "lorena@floresinsuranceagency.com",
                    "mike@floresinsuranceagency.com",
                    "debbie@floresinsuranceagency.com",
                    "coral@floresinsuranceagency.com",
                    "sarahi@floresinsuranceagency.com"]
SENDER = "salesdigest@floresinsuranceagency.com"

# --- roster (HANDOFF_4 s5) --------------------------------------------------
# Producers whose numbers are counted. Team straight-sums scale x3, not x5.
PRODUCERS = {
    "Crystal Mango":   {"ext": "106", "rc_id": "193226052", "az_id": 174445},
    "Lorena Gonzalez": {"ext": "104", "rc_id": "173445052", "az_id": 82587},
    "Mike Olvera":     {"ext": "105", "rc_id": "173446052", "az_id": 82588},
    # Frank, 2026-08-24: "lets get Sarahi and Coral added on as regular
    # producers effective today." This lands the s6 decision four days ahead of
    # the 2026-08-28 review date, which is therefore closed, not pending.
    # Coral has a full Insightful record. Sarahi has NONE -- she counts in every
    # call, quote and sales figure, but her utilization card reads as unlicensed
    # until someone creates her Insightful record (NO_INSIGHTFUL_LICENCE below).
    "Coral Barwick":   {"ext": "108", "rc_id": "774861052", "az_id": 185440},
    "Sarahi Chin":     {"ext": "109", "rc_id": "774862052", "az_id": 185441},
}
TEAM_SCALE = len(PRODUCERS)  # 5 as of 2026-08-24 (was 3)

# Shown as placeholders only, excluded from every calculation.
# Frank, 2026-08-13: "leave them out of everything for calculating the data for
# now, just put placeholders on the report." Revisit 2026-08-28 (s6).
# EMPTIED 2026-08-24: both moved into PRODUCERS above. The name is kept so the
# `name in cfg.PLACEHOLDERS` guards and placeholder_sales() stay valid -- they
# are now no-ops rather than dead code, which is what keeps the utilization
# panel's card loop and its order assertion working unchanged.
PLACEHOLDERS = {}

# ONE EXCEPTION to the placeholder pin, Frank 2026-08-14: "put a pin in Sarahi
# and Coral's data display until the 28th as agreed, UNLESS THEY SELL
# SOMETHING, add that. Leave their placeholders in there."
#
# So: a sale by either of them is surfaced on the day it happens, on their
# existing placeholder card -- the card stays, it just gains a line. Everything
# else about them stays blank until 2026-08-28, and a sale still does NOT enter
# any team total, because they remain excluded from every calculation.
# Both of them do sell: Coral has 1 policy on the book, Sarahi has 8.
PLACEHOLDER_SHOW_SALES = True

# A policy whose lead source is BOB is NOT a sale (Frank, 2026-08-14). BOB is
# book-of-business: existing policies moved onto a producer's name, not new
# business won. Excluding it is not cosmetic --
#   * Sarahi's entire "8 policies" are BOB. She has never sold.
#   * Crystal's 2026-08-13 "$2,363 Premium Sold" is BOB, so the real figure
#     for that day is $0.
# Applies everywhere a policy is counted: Premium Sold, policy counts, the
# leaderboard's premium-sold category and its tie-break, and placeholder sales.
NON_SALE_LEAD_SOURCES = {"bob"}


def lead_source_map(leads):
    """leadSourceId -> leadSourceName, built from the lead corpus.

    Policies carry only leadSourceId; the name lives on leads.
    """
    return {l["leadSourceId"]: l["leadSourceName"] for l in leads
            if l.get("leadSourceId") and l.get("leadSourceName")}


def is_real_sale(policy, source_map):
    name = (source_map.get(policy.get("leadSourceId")) or "").strip().lower()
    return name not in NON_SALE_LEAD_SOURCES


def real_sales(day, policies, source_map, ids):
    """{name: (count, premium)} of genuine sales on `day` for the given ids."""
    out = {}
    for p in policies:
        if not str(p.get("soldDate") or "").startswith(day):
            continue
        who = ids.get(p.get("agentId"))
        if not who or not is_real_sale(p, source_map):
            continue
        n, prem = out.get(who, (0, 0.0))
        out[who] = (n + 1, prem + float(p.get("premium") or 0))
    return out


def placeholder_sales(day, policies, source_map):
    """Sales by Coral/Sarahi on `day` -- displayed only, never in a team total."""
    return real_sales(day, policies, source_map,
                      {v["az_id"]: k for k, v in PLACEHOLDERS.items()})

# Non-producer extensions.
OTHER_EXT = {
    "Veronica Flores":    {"ext": "101", "rc_id": "173440052"},
    "Amanda Torricellas": {"ext": "102", "rc_id": "173443052", "az_id": 105006},
    "Debbie Aguilera":    {"ext": "103", "rc_id": "173444052", "az_id": 83597},
    "Frank Flores":       {"ext": "33",  "rc_id": "173442052", "az_id": 82589},
}
# Debbie is a recipient and appears in Utilization; she is not a producer.
# AgencyZoom agrees: isProducer False. francisco@ has no phone extension --
# confirmed correct as a recipient.

# --- utilization panel ------------------------------------------------------
# Everyone the panel renders, EVERY DAY. The layout depends on this: when the
# panel only rendered people Insightful had published, it swung ~700px and
# forced the two columns apart (s9).
UTIL_PANEL_ORDER = ["Crystal Mango", "Lorena Gonzalez", "Mike Olvera",
                    "Debbie Aguilera", "Amanda Torricellas",
                    "Coral Barwick", "Sarahi Chin"]

# Sarahi has NO Insightful record at all -- not merely untracked. Flagged in the
# audit so a licence can be assigned (Frank, 2026-08-14).
NO_INSIGHTFUL_LICENCE = {"Sarahi Chin"}
# Francisco holds an active licence but produces no attendance rows.
LICENSED_NOT_TRACKED = {"Francisco Flores"}

# --- exclusion rules (HANDOFF_4 s5) -----------------------------------------
# Leads assigned to these people are TEST/TRAINING leads. Excluded from every
# lead-derived metric: recontact struggle, households quoted, premium quoted.
# Their DIALS still count where the producer is counted.
# Test and dummy records seeded by vendors (Mav AI) or typed by hand. They are
# real leads in AgencyZoom with real dials against them, so nothing upstream
# filters them -- Frank spotted "John Doe" sitting in Call Detail as a live
# contact (2026-08-18). Matched on name, not lead source: the Mav AI test rows
# and the hand-typed ones share nothing but the name.
TEST_LEAD_RE = re.compile(
    r"^\s*(john|jane)\s+doe\s*$|(^|\s)test(\s|$)|^test\b|\btest$"
    r"|do not call|^asdf|^xxx", re.I)


# Internal or test calls against a lead record that looks completely ordinary,
# so no name pattern can catch it without risking real prospects. Matched on ID
# only -- deliberately explicit and auditable. Add an id here when a call turns
# out to have been a test.
#   49675255  Frankie Flores -- Sarahi's test call, 2026-08-24 (Frank confirmed).
#             Real-looking record created 2025-05-01 and assigned to Mike, and
#             "Flores" is the agency's own surname, so TEST_LEAD_RE must not be
#             widened to catch it.
TEST_LEAD_IDS = {49675255}


def is_test_lead(lead):
    if lead.get("id") in TEST_LEAD_IDS:
        return True
    name = (f"{(lead.get('firstname') or '').strip()} "
            f"{(lead.get('lastname') or '').strip()}").strip()
    return bool(name) and bool(TEST_LEAD_RE.search(name))


TRAINING_LEAD_OWNERS = {82589,   # Frank Flores
                        185440,  # Coral Barwick
                        185441,  # Sarahi Chin
                        105006}  # Amanda Torricellas

# Service, renewal and change work is excluded ENTIRELY -- from the numbers and
# from the report. A task qualifies if it hangs off a CUSTOMER record rather
# than a lead, or its title or body matches below.
SERVICE_TITLE_RE = re.compile(
    r"renewal|service request|audit change|shot clock reminder|thank you card",
    re.I)
SERVICE_BODY_RE = re.compile(
    r"\bFFR\b|renewal|service request|service center|audit change|"
    r"audit the change|endorse|policy change", re.I)
# Deliberately NOT matched: bare "Carrier:" or "Policy Number:". New-business
# notes routinely record a prospect's current carrier.

# A lead vendor's broken integration dumps leads into a pipeline literally named
# "Pipeline". The agency does not use it. Ignore every move INTO it; a move OUT
# of it says nothing about where the lead really was. Without this, a lead
# sitting in "1 Pipeline | Quotes Presented" reads as lost from "New".
JUNK_WORKFLOW_ID = 23073
JUNK_WORKFLOW_NAME = "Pipeline"

# --- thresholds (HANDOFF_4 s7) ----------------------------------------------
# (green_at, yellow_at) -- read as: >= green is green, >= yellow is yellow,
# else red. Metrics where lower is better carry "lower_better": True.
THRESHOLDS = {
    "call_volume":       {"green": 50,   "yellow": 40},
    "avg_talk_min":      {"green": 7,    "yellow": 3},
    "contact_rate_pct":  {"green": 13,   "yellow": 10},
    "households_quoted": {"green": 5,    "yellow": 2},
    "premium_quoted_per_hh":  {"green": 900, "yellow": 501},
    "premium_sold_per_policy": {"green": 900, "yellow": 501},
    "task_completion_pct": {"green": 100, "yellow": 90},
    "speed_to_dial_min": {"green": 2, "yellow": 5, "lower_better": True},
    "utilization_pct":   {"green": 85,   "yellow": 80},
}

# Straight-sum metrics scale x3 for the team row. Rate, percentage and per-unit
# metrics apply the per-producer threshold UNSCALED.
TEAM_SCALED_METRICS = {"call_volume", "households_quoted"}

TIER_LABELS = {                       # wording set by Frank 2026-08-13
    "green":  "On or exceeding goal",
    "yellow": "Off pace, but close",
    "red":    "Off track, needs review",
}
TIER_COLORS = {"green": "#16A34A", "yellow": "#CA8A04", "red": "#DC2626"}


def tier(metric, value):
    """Colour tier for a value. Boundary rules are settled -- see s7.

    premium red is under $501; task completion green only at exactly 100%;
    contact rate at exactly 13.0% is green; premium sold with 0 policies is red.
    """
    t = THRESHOLDS[metric]
    if value is None:
        return "red"
    if t.get("lower_better"):
        if value < t["green"]:
            return "green"
        return "yellow" if value <= t["yellow"] else "red"
    if metric == "task_completion_pct":
        if value >= 100:
            return "green"
        return "yellow" if value >= t["yellow"] else "red"
    if value >= t["green"]:
        return "green"
    return "yellow" if value >= t["yellow"] else "red"


# --- MVP leaderboard (HANDOFF_4 s7) -----------------------------------------
# Nine categories in this exact order. 3/2/1 by rank; bars scale to the leading
# total. Zero-activity override: no recorded activity in a category scores 0,
# not a ranked point.
LEADERBOARD_CATEGORIES = [
    "Role Play", "Call Volume", "Avg Talk Time", "Avg Sentiment",
    "Avg Call Score", "Contact Rate", "Households Quoted",
    "Premium Quoted", "Premium Sold",
]
# Frank, 2026-08-24: "lets do 3-2-1-.5-0 for the points". Keeps the original
# 3/2/1 podium intact, so totals stay on the same scale as the three-producer
# reports, and gives fourth place a half point for showing up rather than
# nothing. Fifth scores zero, same as no activity at all.
# Places beyond this list score 0 -- see the padding in panels.leaderboard, which
# is what stops a sixth producer from raising IndexError.
# Frank, 2026-08-25: five places, and a tie takes the LOWEST place it occupies
# -- "if they tie, lower the score". A three-way tie for first is all three on
# 3 pts (places 1-2-3 consumed, worst of them paid), then 2, then 1. A two-way
# tie for first is 4 pts each, then 3, 2, 1. This REVERSES the 08-24 rule, where
# a tie took the BEST place it occupied; see panels.leaderboard.
LEADERBOARD_POINTS = [5, 4, 3, 2, 1]
# Tie-break, from Frank: premium sold, then households quoted, then call volume.
LEADERBOARD_TIEBREAK = ["premium_sold", "households_quoted", "call_volume"]

# --- Coach AI (HANDOFF_4 s7) ------------------------------------------------
# VERIFIED, DO NOT RELITIGATE. Coach AI titles each email with the UTC date at
# generation, ONE DAY AHEAD of the Arizona day it describes. The email titled
# "Aug 08" reports Arizona Aug 7. Proof: it reports 76 scored calls, and Arizona
# Aug 8 was a Saturday with zero producer dials.
COACH_TITLE_IS_NEXT_DAY = True
# Bars scale against PER-PRODUCER extremes over the trailing window -- not team
# daily averages, which put individual scores below the floor.
COACH_BAR_RANGES = {
    "Avg Call Score": (38, 251),
    "Avg Sentiment": (11, 43),
    "Role Play": (58, 87),
}

# --- Call Detail row colours (HANDOFF_4 s7) ---------------------------------
# Recovered from the approved design, then amended by Frank.
# Frank, 2026-08-25: "I want to know if the quote was presented on that call, or
# if its a follow up from a previously presented quote." That splits the two
# quote states in two, giving seven categories on five hues -- the follow-up
# pair reuses its parent hue and is told apart by an OUTLINED chip and a DASHED
# row edge rather than by a sixth and seventh colour. Seven hues cannot clear
# the all-pairs colour-separation floors; five can, and every chip carries its
# label anyway, so the extra state rides a non-colour channel.
#
# hue: the validated status set. fill=False draws the outlined/dashed variant.
# fill  -- True = solid chip, False = BORDERED box (white, coloured rule + ink)
# dash  -- True = follow-up on a quote already out: dashed rule, pale mix bar
# light -- the mix-bar/legend tint for a dashed category (~45% hue over white)
#
# Frank, 2026-08-25: "leave the bordered blue and red boxes for Quoted no
# action, Quote follow up no action, and quoted lost, quote follow up lost."
# All four quote states are bordered boxes, and the on-this-call / follow-up
# split is carried by the RULE -- solid against dashed -- not by filling them.
# Only the three non-quote states are solid chips.
# paint  -- the colour of the chip, the mix-bar segment and the row rail
# stripe -- candy-cane band colour for a follow-up: 45-degree bands of this over
#           white, on the chip, the legend swatch, the bar segment and the rail.
#           A dotted 1px rule was too quiet to see (Frank, 2026-08-25). The band
#           is the PALE tint, not `paint`, so chip text stays readable; `paint`
#           still draws the 2px rule around it, which is what a client that
#           strips CSS gradients falls back to.
# fill   -- True = solid block of `paint`; False = white box outlined in `paint`
# stroke -- "solid" for something that happened ON this call, "dotted" for a
#           follow-up on a quote already out. Applies to the chip border AND the
#           row rail, so the two read as one signal.
# ink    -- text colour on a bordered box (a filled one computes its own)
#
# Frank, 2026-08-25: "solid light blue for quoted, no action, dotted border
# light blue for quote follow up, no action. Solid red for quoted on this call
# lost, and dotted red border for quote follow up, lost ... on the left bar,
# dotted or solid as well depending on which one it is."
CALL_CATEGORIES = {
    "sold_on_call":    {"paint": "#008300", "fill": True,  "stroke": "solid",
                        "label": "Sold on the call"},
    "quoted_call_open":{"paint": "#9fc2ed", "fill": True,  "stroke": "solid",
                        "label": "Quoted, no action"},
    "followup_open":   {"paint": "#2a78d6", "fill": False, "stroke": "solid",
                        "ink": "#0b0b0b", "stripe": "#d4e4f7",
                        "label": "Quote follow up, no action yet"},
    "quoted_call_lost":{"paint": "#e34948", "fill": True,  "stroke": "solid",
                        "label": "Quoted on this call, {d}"},
    "followup_lost":   {"paint": "#e34948", "fill": False, "stroke": "solid",
                        "ink": "#0b0b0b", "stripe": "#f9dada",
                        "label": "Quote follow up, {d}"},
    # Frank, 2026-08-25: "yellow and orange are 2 different colors, use them
    # both". #f0e800 sits outside the validator's mark-lightness band, which is
    # what highlighter yellow means; the pair that matters clears the
    # normal-vision floor at Delta E 17.7 against #eda100, and both take dark ink.
    "dead_no_quote":   {"paint": "#f0e800", "fill": True,  "stroke": "solid",
                        "label": "{d}, never quoted"},
    "live_no_quote":   {"paint": "#eda100", "fill": True,  "stroke": "solid",
                        "label": "Contacted, No Action"},
}
# Reading order, best first -- also the Call Detail sort order.
CALL_CATEGORY_ORDER = ["sold_on_call", "quoted_call_open", "followup_open",
                       "quoted_call_lost", "followup_lost", "dead_no_quote",
                       "live_no_quote"]

# Which quote state a call is in, read off the TASK TITLES due on that lead that
# day (Frank, 2026-08-25: "you should be able to tell just by the task title
# and/or quote submission date ... the flaw with quote submission day is they can
# start it one day and present another, task title is probably best"). The titles
# are a controlled vocabulary in this agency, so they are the primary signal and
# quoteDate is not used at all.
#   FOLLOWUP -> a quote is already out and this call chases it
#   PENDING  -> no quote out yet; the task is about getting one built or sent
QUOTE_FOLLOWUP_TITLE_RE = re.compile(
    r"quoted?\b[^.]*\bfollow|\bfollow[- ]?up\b[^.]*\bquote|\bquote follow\b", re.I)
QUOTE_PENDING_TITLE_RE = re.compile(
    r"never quoted|\bnew\b.*lead|lead day \d|send quote|finish quotes?"
    r"|present quote|quote to prospect", re.I)
# Checked BEFORE the two above and short-circuits both: 'QNC Lead Day 4' also
# matches the pending pattern's "lead day N", so without this guard it would be
# silently filed as pending.
# Frank, 2026-08-25: "QNC Pipeline is where leads go when they did not close the
# LAST time they were presented, but the stages in that pipeline serve the same
# function as the ones in the 1 pipeline they share names with. So when someone
# goes into the quotes stage in the QNC Pipeline, they got quoted." A QNC lead
# has therefore already been presented a quote -- 'QNC Lead Day 4' is a
# follow-up, not an unknown. Checked BEFORE the pending pattern, which its
# "Lead Day N" would otherwise match.
QUOTE_QNC_TITLE_RE = re.compile(r"\bQNC\b", re.I)

# Fallback when no task title settles it: a MOVE_STAGE into a quote stage inside
# this window means a quote is genuinely still in play. Unbounded, it relabelled
# half the board -- Genaro Cortez was last quoted 2022-09-01 and Frankie Flores
# 2025-05-01, and neither is a live follow-up.
QUOTE_OPEN_WINDOW_DAYS = 30

CALL_ROW_COLORS = {
    "one_call_close":   "#4ADE80",  # quoted AND sold on the same call
    "quote_no_action":  "#D8B4FE",  # quote presented, no action yet
    "dead_with_quote":  "#FCA5A5",  # dead/smart-cycled WITH a quote presented
    "dead_no_quote":    "#FDBA74",  # dead/smart-cycled, no quote presented
    "live_no_quote":    "#BFDBFE",  # live contact, no quote, no dead outcome
}
# A quote presented VERBALLY and never entered in AgencyZoom still counts for
# the row colour, but does NOT feed Premium Quoted. A "recycled back from
# Smart-Cycle" move is a move OUT of the cycle and is not a dead outcome.

# --- Recontact Struggle (HANDOFF_4 s7) --------------------------------------
# Frank's definition: momentum lost AFTER a real conversation.
AT_RISK_BUSINESS_DAYS = 3     # > 3 business days since last stage move
AT_RISK_DIALS = 3             # or > 3 dials since entering the stage
AT_RISK_MAX_STAGE_AGE_DAYS = 30
# "Most critical" is the MOST RECENTLY CONTACTED -- those leads are still warm.
CRITICAL_SORT = "most_recently_contacted"
INLINE_RECONTACT_PER_GROUP = 3   # overflow lives in the attachment
# The old three-stage-card visual is retired but its methodology is preserved in
# the notes attachment -- Frank wants it back later.

# --- layout (HANDOFF_4 s9) --------------------------------------------------
# FIXED ORDER -- do not solve it per day. A report whose panels move around is
# harder to read than one slightly uneven.
COLUMN_LEFT = ["Sales Funnel by Producer", "Task Completion Rate",
               "Recontact Struggle"]
COLUMN_RIGHT = ["Team Leaderboard", "Call Outcome Breakdown", "Speed to Dial",
                "Utilization and Efficiency", "Coaching & Call Quality"]
# Sales Funnel is BY DATA CATEGORY -- one card per metric, producers ranked
# highest to lowest inside each, then Team Total. Producer bars scale to the top
# producer, not the team total.
FUNNEL_METRICS = ["Call Volume", "Avg Talk Time", "Contact Rate",
                  "Households Quoted", "Premium Quoted", "Premium Sold"]

# --- email delivery (HANDOFF_4 s10) -----------------------------------------
# Gmail clips HTML bodies above ~102,400 bytes and replaces the tail with
# "[Message clipped]" -- a clipped digest silently loses whole panels.
GMAIL_CLIP_BYTES = 102_400
# Gmail also strips <details>/<summary> and <input>/:checked. There is NO
# working disclosure widget in HTML email. Do not add one.

# --- parked items -----------------------------------------------------------
# Frank, 2026-08-14:
#   * Credential rotation -- deferred, he will do it himself. Do not chase.
#   * TRAQ.ai / Coach AI API key -- DROPPED until 2026-09-15. It is not arriving
#     soon, so stop treating it as imminent. Call transcription is handled
#     locally now (transcribe.py, Whisper base via sherpa-onnx), which removes
#     the dependency entirely; the key would only make it cheaper.
TRAQ_REVISIT_DATE = dt.date(2026, 9, 15)

# --- open questions (HANDOFF_4 s6) ------------------------------------------
# Surfaced automatically as a highlighted block in the audit on/after this date.
REVISIT_DATE = dt.date(2026, 8, 28)
REVISIT_QUESTIONS = [
    "Should Coral Barwick and Sarahi Chin be included in the utilization panel? "
    "(Confirmed 2026-08-14: Coral IS tracked by Insightful and produces a full "
    "utilization figure every day. Sarahi has no Insightful record at all and "
    "needs a licence before she can ever appear.)",
    "Should Coral's and Sarahi's leads enter the lead-derived metrics?",
]

# --- per-day facts ----------------------------------------------------------
# UTIL[date] = {name: (published_pct, total_time, productive_time)}
# Populated from insightful_util.pull(); no longer hand-maintained.
UTIL = {}
UTIL_WEIGHTED = {}
