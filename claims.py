"""Claims -- the one definition (Frank, 2026-10-02: "i want to make a claims
section and begin to utilize the claims pipeline. Licensed service reps will
be the only ones able to open claims, amanda and crystal are the only 2
licensed reps of that team. Debbie is not licensed, she cannot open claims
moving forward").

A claim is an SR in AgencyZoom's "Claim" service workflow (workflowId 23672),
and its type is the SR's category (CLAIM_TYPES). How long it took to close is
created -> completed, like every other pipeline.
Before 2026-10-02 it held one SR, a test (Veronica, 2026-03-11, "replace
vehicle"), so the section starts empty.

The rule: a claim SR is OPENED by someone in LICENSED (`createdBy`) and
WORKED by one (assigned `csr`). AgencyZoom does not stop anyone else from
creating one, so Athena flags it instead: a claim opened on or after
RULE_FROM by anyone outside LICENSED, or assigned to anyone outside it, is
listed under "Not licensed" on the Service Center. Claims opened before the
rule are never flagged.

Rows, never medians (like every Service Center section), so the board adds
any range up:
    opened     every claim SR created on the day (live or already completed)
    completed  every claim SR completed on the day, with hours open
    open       every claim SR still open at the end of the day
    flags      every claim SR created on the day that breaks the rule
"""
import datetime as dt

CLAIM_WORKFLOWS = {"Claim"}
CLAIM_WORKFLOW_ID = 23672

# Who may open and work a claim: the ops team and Crystal (Frank,
# 2026-10-02: "yes, the ops team and crystal") -- of the service team that is
# Amanda and Crystal; Debbie is not licensed. By AgencyZoom employee id (the
# SR's `csr`) and by name (its `createdBy`).
LICENSED = {82589: "Frank Flores", 82372: "Francisco Flores", 82592: "Veronica Flores",
            105006: "Amanda Torricellas", 174445: "Crystal Mango"}

# The type of claim is the SR's own AgencyZoom category (Frank, 2026-10-02:
# "type of claim"; /v1/api/service-categories). Matched by id, so a rename in
# AgencyZoom breaks nothing: Frank renamed them "Claim: Auto" etc. on
# 2026-10-02, and "Claim Services" (25618) became "Claim: Specialty". Any other
# category (General ...) is "Not set", for the rep to pick the right one.
CLAIM_TYPES = {40942: "Auto", 40944: "Home", 40946: "Life", 25618: "Specialty",
               40943: "Commercial", 40945: "Work Comp"}
NOT_SET = "Not set"
# Commercial and Work Comp claims are Cerberus's (Frank, 2026-10-02:
# "commercial"): commercial.is_commercial_sr counts them, so they leave the
# Service Center and show on the Commercial Center instead -- same rules.
COMMERCIAL_CATEGORIES = {40943, 40945}
SERVICE_TYPES = [t for c, t in CLAIM_TYPES.items() if c not in COMMERCIAL_CATEGORIES] + [NOT_SET]
COMMERCIAL_TYPES = [CLAIM_TYPES[c] for c in sorted(COMMERCIAL_CATEGORIES)]
LICENSED_NAMES = set(LICENSED.values())
RULE_FROM = "2026-10-02"


def is_claim(sr):
    return (sr.get("workflowName") in CLAIM_WORKFLOWS
            or sr.get("workflowId") == CLAIM_WORKFLOW_ID)


def _csr_name(csr):
    from missed_call_audit import CSR_NAMES
    import service_digest
    full = {v["az_id"]: k for k, v in service_digest.SERVICE_TEAM.items()}
    return full.get(csr) or CSR_NAMES.get(csr) or (f"employee {csr}" if csr else None)


def is_commercial_claim(sr):
    return is_claim(sr) and sr.get("categoryId") in COMMERCIAL_CATEGORIES


def problems(sr):
    """Why this claim SR breaks the rule, or [] -- only for claims created on
    or after RULE_FROM."""
    if str(sr.get("createDate") or "")[:10] < RULE_FROM:
        return []
    out = []
    by = (sr.get("createdBy") or "").strip()
    if by and by not in LICENSED_NAMES:
        out.append("opened")
    if sr.get("csr") and sr.get("csr") not in LICENSED:
        out.append("assigned")
    return out


def _row(sr, day):
    import service_digest as sd
    row = dict(sd.sr_detail(sr), id=sr.get("id"),
               opened_by=(sr.get("createdBy") or "").strip() or None,
               assigned=_csr_name(sr.get("csr")),
               stage=sr.get("workflowStageName") or None,
               due=str(sr.get("dueDate") or "")[:10] or None)
    row["type"] = CLAIM_TYPES.get(sr.get("categoryId"), NOT_SET)
    row["licensed"] = row["opened_by"] in LICENSED_NAMES if row["opened_by"] else None
    row["problems"] = problems(sr)
    if sr.get("completeDate"):
        h = sd._hours(sr.get("createDate"), sr.get("completeDate"))
        row["hours"] = round(h, 2) if h is not None else None
        row["completed_by"] = sr.get("modifiedBy")
    else:
        try:
            age = (dt.datetime.fromisoformat(f"{day}T23:59:59")
                   - dt.datetime.fromisoformat(str(sr.get("createDate"))[:19])).total_seconds() / 86400
            row["days_open"] = round(age, 1) if age >= 0 else None
        except ValueError:
            row["days_open"] = None
        row["overdue"] = bool(row["due"] and row["due"] < day)
    return row


def figures(day, done, live, types=SERVICE_TYPES):
    """The day's claims from the day's saved SR files: `done` is every
    completed SR (service_digest.completed_tickets), `live` every live one as
    of the day (data/az_service_tickets_<day>.json)."""
    done_c = [t for t in done if is_claim(t)]
    live_c = [t for t in live if is_claim(t) and str(t.get("createDate") or "")[:10] <= day]
    by_id = {t.get("id"): t for t in live_c}
    by_id.update({t.get("id"): t for t in done_c})     # a completed copy wins
    opened = [_row(t, day) for t in by_id.values() if str(t.get("createDate") or "")[:10] == day]
    completed = [_row(t, day) for t in done_c if str(t.get("completeDate") or "")[:10] == day]
    done_ids = {t.get("id") for t in done_c if str(t.get("completeDate") or "")[:10] <= day}
    still_open = [_row(t, day) for t in live_c if t.get("id") not in done_ids]
    return {"licensed": sorted(LICENSED_NAMES), "rule_from": RULE_FROM,
            "types": list(types),
            "opened": opened, "completed": completed, "open": still_open,
            "flags": [r for r in opened if r["problems"]]}


if __name__ == "__main__":
    import json, sys, pathlib
    import service_digest
    day = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    live_f = pathlib.Path(__file__).parent / f"data/az_service_tickets_{day}.json"
    live = json.loads(live_f.read_text()) if live_f.exists() else []
    print(json.dumps(figures(day, service_digest.completed_tickets(day), live), indent=1, default=str))
