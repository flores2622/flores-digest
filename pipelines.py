"""What each AgencyZoom sales pipeline and stage means (Frank, 2026-09-24).

The lead-source guide (lead_sources.py) says who a lead is. This says where
the lead is in the sale. Apollo reads a call knowing both: which stage the
lead sat in when the call started, and every stage move the producer made
on it that day.

    python3 pipelines.py       every pipeline and stage, with its meaning

Only four pipelines are worked by the producers. "Pipeline" is the same as
1 Pipeline: integrations drop leads there by mistake, and it should be empty.
Anything commercial and AZ Sun Quote Tracker are Frank's, for Cerberus.
Every other pipeline is unused and ignored.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent

PIPELINES = {
    "1 Pipeline": {
        "owner": "apollo",
        "what": "The main pipeline. Every new or updated lead comes into New here.",
    },
    "1-1 QNC": {
        "owner": "apollo",
        "what": "Quotes Not Closed: we quoted them the last time we talked, and it "
                "did not close for whatever reason.",
    },
    "1-2 Leads Not Quoted": {
        "owner": "apollo",
        "what": "We never got hold of them, or they declined even being quoted.",
    },
    "Life Pipeline": {
        "owner": "apollo",
        "what": "Life insurance leads.",
    },
}
# Integrations put leads in "Pipeline" that belong in 1 Pipeline (Frank,
# 2026-09-24: "pipeline should be empty, they should be moving them").
SAME_AS = {"Pipeline": "1 Pipeline"}
# Frank's alone: anything commercial, and AZ Sun (Frank, 2026-09-24).
CERBERUS = re.compile(r"commercial|az sun", re.I)

# Stage name -> meaning. "Stages in other pipelines with the same names serve
# the same purpose, the leads are just there for another reason" (Frank,
# 2026-09-24).
STAGES = {
    "New": "A new or updated lead. If the producer gets hold of them, the goal is "
           "to keep them on the phone and go all the way to sold: a one-call close. "
           "The stages in between are for everything in between.",
    "New 1st Cycle": "Smart-Cycled back into this pipeline for a first new attempt. "
                     "Cycles go 1st, 2nd, 3rd, and the lead is deaded if it never "
                     "advances past the 3rd.",
    "New 2nd Cycle": "Smart-Cycled back into this pipeline a second time. One cycle "
                     "left before the lead is deaded if it never advances.",
    "New 3rd Cycle": "The last cycle: if the lead does not advance now, it is deaded.",
    "Contacted, In Progress": "We got hold of them and are working on a quote or "
                              "waiting on info.",
    "Ready to Present": "The quote is ready, but we are waiting to present it for "
                        "a specific reason.",
    "Quotes Presented": "We presented numbers to this person and are following up "
                        "on the quote.",
    "FSD (Pending Bind)": "Future sale date: sold, pending bind.",
}
# Same purpose, shorter name in the other pipelines (Frank confirmed,
# 2026-09-24): "Quoted" is Quotes Presented, "Contacted" is Contacted, In
# Progress.
STAGES["Contacted"] = STAGES["Contacted, In Progress"]
STAGES["Quoted"] = STAGES["Quotes Presented"]
# 1 Pipeline's holding stage for centers of influence (Frank, 2026-09-24).
STAGES["Lender Referral"] = ("An account a center of influence (a loan officer or "
                             "realtor) sent us, held here so it does not go through "
                             "the full automation process.")
# Life Pipeline's own stages, read as they sound (Frank, 2026-09-24).
STAGES["Applications"] = "The life application is being taken or has been submitted."
STAGES["Med. Records Needed"] = "The carrier needs medical records before it decides."
STAGES["Approved"] = "The carrier approved the life policy."

# Stages made for an outside company that texted our leads for us; the agency
# never uses them itself (Frank, 2026-09-24: "Crystal used it on accident").
# A producer moving a lead INTO one is a mistake to flag.
NOT_OURS = {"IL Interested", "Transfer Pending"}
for _s in NOT_OURS:
    STAGES[_s] = ("Not an agency stage: made for an outside texting company. A "
                  "producer moving a lead here did it by mistake.")

# Where a move can end that is not a stage.
EXITS = {
    "Smart-Cycle": "Smart-Cycled: parked, to come back into a pipeline later on its own.",
    "Dead": "Deaded: the lead is closed as lost.",
    "Sold": "Sold.",
}


def pipeline_of(name):
    """(pipeline to read it as, owner): owner is "apollo", "cerberus" or None
    (an unused pipeline, ignored)."""
    name = (name or "").strip()
    name = SAME_AS.get(name, name)
    if name in PIPELINES:
        return name, PIPELINES[name]["owner"]
    if CERBERUS.search(name):
        return name, "cerberus"
    return name, None


def split(where):
    """'1 Pipeline | Quotes Presented' -> ('1 Pipeline', 'Quotes Presented');
    'Smart-Cycle' -> ('', 'Smart-Cycle')."""
    where = (where or "").strip()
    if "|" in where:
        p, s = where.split("|", 1)
        return p.strip(), s.strip()
    return "", where


# "1 Pipeline | New to 1 Pipeline | Quotes Presented by Lorena Gonzalez"
# "1 Pipeline | Contacted, In Progress to Dead by Lorena Gonzalez Loss Reason: Not interested"
# "1 Pipeline | Ready to Present to Smart-Cycle by Sarahi Chin"  <- " to " inside a stage name
_TAIL = re.compile(r"^(?P<body>.+?)(?: by (?P<by>.+?))?(?: Loss Reason: (?P<why>.+))?$")


def _is_location(where, known):
    where = where.strip()
    if where in EXITS:
        return True
    if known:
        return where in known
    p, s = split(where)
    return bool(p) and " to " not in p and "|" not in s


def parse_move(text):
    """One MOVE_STAGE line (live_contact._move_stage_parts's `move`) ->
    {"from", "to", "loss_reason"}, or None if it doesn't read as a move.

    Splits at the " to " that leaves a real location on both sides -- a
    "Pipeline | Stage" AgencyZoom knows (data/az_stages.json), or an exit --
    since a stage name can itself contain " to " (Ready to Present)."""
    m = _TAIL.match((text or "").strip())
    if not m:
        return None
    body = m.group("body")
    known = set(_stage_map().values())
    parts = body.split(" to ")
    for k in range(1, len(parts)):
        frm, to = " to ".join(parts[:k]).strip(), " to ".join(parts[k:]).strip()
        if _is_location(frm, known) and _is_location(to, known):
            return {"from": frm, "to": to, "loss_reason": (m.group("why") or "").strip()}
    return None


def describe(where):
    """What a 'Pipeline | Stage' (or an exit) means, in one or two sentences."""
    p, s = split(where)
    if not p:
        return EXITS.get(s, "")
    pipe, owner = pipeline_of(p)
    if owner == "cerberus":
        return "A commercial / AZ Sun pipeline: Frank's, not coached here."
    if owner is None:
        return "An unused pipeline."
    meaning = STAGES.get(s, "No set meaning for this stage.")
    return f"{PIPELINES[pipe]['what']} Stage: {meaning}"


_STAGE_MAP = None


def _stage_map():
    """workflowStageId -> 'Pipeline | Stage', from daily.py's cached
    data/az_stages.json (written from /v1/api/pipelines-and-stages)."""
    global _STAGE_MAP
    if _STAGE_MAP is None:
        p = ROOT / "data/az_stages.json"
        _STAGE_MAP = json.loads(p.read_text()) if p.exists() else {}
    return _STAGE_MAP


def current_stage(lead):
    """'Pipeline | Stage' a lead record sits in now, or "". Only open leads
    carry a stage id; a sold or closed lead reads ""."""
    return _stage_map().get(str((lead or {}).get("workflowStageId") or ""), "")


def _chronological(parsed):
    """The day's moves oldest first. Notes arrive newest first (Sarahi's
    Patricia Acosta, 2026-09-22: "Ready to Present to Smart-Cycle" listed
    before "New to Ready to Present"), so the list is reversed -- unless the
    order as given is the one that chains (each move starting where the last
    ended) and the reversed one does not."""
    def chains(ms):
        return all(a["to"] == b["from"] for a, b in zip(ms, ms[1:]))
    rev = list(reversed(parsed))
    return parsed if chains(parsed) and not chains(rev) else rev


def call_stage(moves, stage_now="", sold_today=False):
    """(before, after) for a call. `moves` are the producer's MOVE_STAGE lines
    on this lead that day, in either order. With a move, `before` is where the
    first move came from; without one the lead has not moved, so `before` is
    where it sits now (the corpus is read at the end of the day)."""
    parsed = _chronological([m for m in (parse_move(x) for x in moves or ()) if m])
    before = parsed[0]["from"] if parsed else stage_now
    after = parsed[-1]["to"] if parsed else stage_now
    if sold_today:
        after = "Sold"
    return before, after


def prompt_block(moves, stage_now="", sold_today=False):
    """What Apollo is told about where the lead was in the sale. How to use
    it is coaching/METHODOLOGY.md's "Pipeline and stage" section."""
    before, after = call_stage(moves, stage_now, sold_today)
    if not before and not after:
        return "Pipeline stage: unknown (no stage on the lead record and no move today)"
    lines = []
    if before:
        lines.append(f"Stage when the call started: {before}. {describe(before)}")
    parsed = _chronological([m for m in (parse_move(x) for x in moves or ()) if m])
    for m in parsed:
        why = f" (loss reason: {m['loss_reason']})" if m["loss_reason"] else ""
        if split(m["to"])[1] in NOT_OURS:
            why += " -- NOT an agency stage (made for an outside texting company); moving a lead here is a mistake"
        lines.append(f"Producer moved it today: {m['from']} -> {m['to']}{why}")
    if sold_today:
        lines.append("The lead is marked sold today.")
    elif not parsed:
        lines.append("No stage move on this lead today.")
    return "\n".join(lines)


def misfiled(leads):
    """Open leads sitting in "Pipeline", which integrations fill by mistake
    and which should be empty (Frank, 2026-09-24): one row each, for the
    Sales Center's list of leads to move into 1 Pipeline."""
    rows = []
    for l in leads or ():
        if l.get("status") != 0:
            continue
        p, stage = split(current_stage(l))
        if p != "Pipeline":
            continue
        rows.append({
            "lead_id": l.get("id"),
            "lead": " ".join(x for x in (l.get("firstname"), l.get("lastname")) if x) or "(no name)",
            "assigned": " ".join(x for x in (l.get("assignToFirstname"), l.get("assignToLastname")) if x),
            "stage": stage,
            "source": (l.get("leadSourceName") or "").strip(),
            "last_activity": str(l.get("lastActivityDate") or "")[:10],
        })
    rows.sort(key=lambda r: r["last_activity"], reverse=True)
    return rows


def main():
    for name, p in PIPELINES.items():
        print(f"\n{name}  ({p['owner']}): {p['what']}")
    print("\nPipeline -> read as 1 Pipeline (should be empty)")
    print("Commercial / AZ Sun -> Cerberus.  Everything else: unused, ignored.")
    print("\nStages:")
    for s, m in STAGES.items():
        print(f"  {s:24s} {m}")
    print("\nExits:")
    for s, m in EXITS.items():
        print(f"  {s:24s} {m}")


if __name__ == "__main__":
    main()
