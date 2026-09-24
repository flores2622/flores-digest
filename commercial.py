"""Cerberus -- what counts as COMMERCIAL work. (Apollo is sales coaching,
Athena is service, Cerberus is Commercial.)

COMMERCIAL IS FRANK'S ALONE (Frank, 2026-09-24). He is the only person who
works it, so nothing commercial may touch anyone else's numbers: Athena's
renewal outcomes, completion times, SR counts and call backs all leave it out.
This module is the one definition both sides import -- Athena to exclude,
Cerberus to count -- so the two can never disagree about an SR.

WHICH SRs ARE COMMERCIAL (Frank, 2026-09-24):
  - every SR in the AgencyZoom workflow "Commercial Renewals", whoever
    completed it;
  - a commercial service change: a "Service Pipeline" SR on a household that
    holds a commercial policy, COMPLETED by Frank -- or, while still open,
    assigned to him (CSR 82589). The completer decides, not the assignee: on
    2026-09-23 Amanda closed five SRs assigned to Frank, and those are hers.
    AgencyZoom has no commercial service pipeline -- these sit in Service
    Pipeline with free-text subjects ("needs COI", "add AI on Progressive
    commercial policy") and no policy number, so the household is the only
    signal. Frank's own Service Pipeline SRs are a mix of personal and
    commercial work, which is why the household test is required as well.
The service team's work on a commercial household (Debbie's late payments,
Amanda's personal renewals for a business owner) is NOT commercial: credit
stays with whoever completed it, and it stays in Athena.

WHICH CALLERS ARE COMMERCIAL (Frank, 2026-09-24): a household whose every
policy on record is a commercial line. A business owner calling about their
home or car stays in Athena's call backs.

A HOUSEHOLD'S POLICIES come from the household map
(service_retention.load_household_map(), R2 cache/az_household_policies.json);
policy records themselves carry no household.
"""
import re

FRANK_ID = 82589                     # AgencyZoom user id; also the CSR id on SRs
FRANK_NAME = "Frank Flores"          # as an SR's modifiedBy prints it
RENEWAL_WORKFLOWS = {"Commercial Renewals"}
SERVICE_WORKFLOWS = {"Service Pipeline"}

# policyTypeName values that are commercial lines, as seen in the household
# map on 2026-09-24. Anything named "Commercial ..." counts automatically, so a
# new commercial type needs no change here. Deliberately NOT commercial:
# "Umbrella" (personal; "Commercial Umbrella" is caught by name) and "Course
# of Construction" (a dwelling under construction on Farmers' personal side).
COMMERCIAL_LINES = {
    "Workers Comp", "General Liability", "Professional Liability",
    "Liquor Liability", "Bond", "Dealer Bond",
}
_COMMERCIAL_NAME = re.compile(r"\bcommercial\b", re.I)


def is_commercial_line(policy_type):
    t = (policy_type or "").strip()
    return t in COMMERCIAL_LINES or bool(_COMMERCIAL_NAME.search(t))


def households(hh):
    """(any, only) -- household ids (int) holding at least one commercial
    policy on record, and those whose every policy on record is commercial.
    `hh` is the household map: {customer_id: {"policies": [...]}}."""
    any_, only = set(), set()
    for cid, v in (hh or {}).items():
        ps = v.get("policies") or []
        flags = [is_commercial_line(p.get("policyTypeName")) for p in ps]
        if any(flags):
            any_.add(int(cid))
            if all(flags):
                only.add(int(cid))
    return any_, only


def is_commercial_sr(sr, commercial_hh):
    """True when an SR (live or completed) is commercial work. `commercial_hh`
    is households(hh)[0]."""
    wf = sr.get("workflowName")
    if wf in RENEWAL_WORKFLOWS:
        return True
    if wf not in SERVICE_WORKFLOWS or sr.get("householdId") not in commercial_hh:
        return False
    if sr.get("completeDate"):
        return sr.get("modifiedBy") == FRANK_NAME
    return sr.get("csr") == FRANK_ID


def is_commercial_caller(hit, commercial_only_hh):
    """True when a missed-call index hit (missed_call_audit._index: customer,
    lead and SR records on the number) belongs to a commercial-only
    household."""
    if not hit:
        return False
    ids = {c.get("id") for c in hit.get("cust") or []}
    ids |= {t.get("householdId") for t in hit.get("tix") or []}
    return bool({i for i in ids if i is not None} & commercial_only_hh)
