"""Renewal SR outcomes, for the service digest's Renewal Outcome Breakdown.

FRAMING (Frank, 2026-09-23): not an agency-wide retention rate. Of the
renewal SRs COMPLETED on a day (or across a filtered range of days), what was
the outcome -- and the retention rate among just those SRs.

WHERE AN OUTCOME COMES FROM. The SR's own resolution, when it can be read:
Frank's six renewal resolutions (Renewed: Accepted as is, Renewed: Endorsed,
Rewrite Accepted, Cancelled: Rewrite Declined, Cancelled, no endorse/rewrite
available, Unable to Contact) on SRs completed from RESOLUTIONS_FROM. Before
that -- or for an id not named yet -- the policy record is read instead, for
the policy the SR's subject names ("Auto - G014549916"), and is shown as its
own "(policy record)" segment so the two sources are never blended.

HOW A POLICY'S OUTCOME IS READ. AgencyZoom keeps one record per policy TERM,
chained by policyNumber, and the status codes carry no labels. Read off the
chains (2026-09-23): 1 = in force, 3 = the next term already issued (it carries
the renewal premium), 4 = a past term that was replaced, 0 = cancelled -- or a
superseded duplicate of a term that also exists as a 4, which is why a 0 only
means cancelled when no live term follows it.

    renewed      a term starting on or after the renewal date is 1, 3 or 4
    cancelled    the renewal term is 0, or the expiring term is 0 with no
                 successor
    rewritten    cancelled or no renewal on file, but the same household took
                 a new policy number of the same line from 30 days before to
                 45 after the renewal (a rewrite, or the carrier re-numbering)
    no renewal   the renewal date has passed and nothing follows it yet
    still ahead  the renewal date has not come yet

There is no cancellation date in any AgencyZoom policy payload; a term's own
modifyDate stands in for it where one is needed.

HOUSEHOLDS. Policy records carry no customer or household. The only link is
/v1/api/customers/{id}/policies, one request per household, so the map
(policyNumber -> household) is built once and kept current a slice at a time
-- see refresh_household_map().
"""
import collections
import datetime as dt
import json
import pathlib
import re
import time

ROOT = pathlib.Path(__file__).resolve().parent
MAP_FILE = ROOT / "data/az_household_policies.json"
MAP_R2_KEY = "cache/az_household_policies.json"
BEFORE, AFTER = 30, 45                 # the renewal window, in days
REFRESH_STALE_DAYS = 30                # every household re-read at least monthly
REFRESH_BATCH = 150                    # of those, how many per night
# Hard cap on household reads in one build. The whole book is ~4,100 reads at
# AgencyZoom's ~1 per 0.7s -- most of an hour. A night that starts without the
# saved map (or a burst of new customers) must never spend that inside the
# nightly run; it works through the backlog a few hundred a night instead.
MAX_FETCH = 400

# ---- renewal SR resolutions (Frank, 2026-09-23) ----------------------------
# The ONLY resolutions the team uses on renewal tickets from 2026-09-24. Frank
# renamed some old choices and added others, and the old ones could not all be
# deleted -- so an old id now carries a new name that does not describe what
# was picked when it was used. Resolutions are therefore read only on tickets
# completed on or after RESOLUTIONS_FROM; everything earlier stays with the
# policy-chain reading. The names and what each counts as are OUTCOMES below.
RESOLUTIONS_FROM = "2026-09-24"
# AgencyZoom's API returns resolutionId only, never the name, and has no lookup
# for it. Each id is named here once, by hand, the first time an SR closed
# with it shows up -- the Service tab lists any id it cannot name yet.
RESOLUTION_LABELS = {}

_HOME = re.compile(r"home|dwelling|\bdp\d?\b|mobile|manufactured|landlord|condo|renter|ho-?\d", re.I)


def _d(x):
    return str(x or "")[:10]


def _pn(p):
    return re.sub(r"\s+", "", str(p or ""))


def _line(type_name):
    t = type_name or ""
    if re.search(r"auto|vehicle|car\b", t, re.I):
        return "auto"
    if _HOME.search(t):
        return "home"
    return t.strip().lower()


def _shift(day, n):
    return (dt.date.fromisoformat(day) + dt.timedelta(days=n)).isoformat()


# ---- household map ---------------------------------------------------------
def load_household_map(log=print):
    """{customer_id: {"fetched": ts, "policies": [...]}}, local file first,
    then the R2 copy a previous container left."""
    if MAP_FILE.exists():
        return json.loads(MAP_FILE.read_text())
    try:
        import publish_board
        cli, bucket = publish_board._client()
        body = cli.get_object(Bucket=bucket, Key=MAP_R2_KEY)["Body"].read()
        MAP_FILE.write_bytes(body)
        log(f"  household map: restored from R2")
        return json.loads(body)
    except Exception:
        return {}


def save_household_map(hh, log=print):
    MAP_FILE.write_text(json.dumps(hh))
    try:
        import publish_board
        cli, bucket = publish_board._client()
        cli.put_object(Bucket=bucket, Key=MAP_R2_KEY, Body=MAP_FILE.read_bytes(),
                       ContentType="application/json")
    except Exception as e:
        log(f"  household map: R2 save failed ({type(e).__name__})")


def _fetch_household(az, cid):
    ps = az.get(f"/v1/api/customers/{cid}/policies") or []
    return {"fetched": time.time(), "policies": [
        {k: p.get(k) for k in ("id", "policyNumber", "policyTypeName", "status",
                               "effectiveDate", "expiryDate", "premium", "soldDate")}
        for p in ps]}


def refresh_household_map(hh, customers, must=(), az=None, log=print):
    """Bring the map current enough for today's figures:
      - every household not in it yet (new customers),
      - `must`: households whose figures depend on a fresh read today (the
        cancelled policies' households, where a rewrite would show up),
      - then the REFRESH_BATCH stalest households older than
        REFRESH_STALE_DAYS, so the whole book is re-read about monthly and a
        cross-sale into an existing household reaches the map eventually.
    """
    if az is None:
        from az_client import AgencyZoom
        az = AgencyZoom()
    ids = {str(c["id"]) for c in customers}
    new = [c for c in ids if c not in hh]
    stale_before = time.time() - REFRESH_STALE_DAYS * 86400
    stale = sorted((c for c in ids if c in hh and hh[c]["fetched"] < stale_before),
                   key=lambda c: hh[c]["fetched"])[:REFRESH_BATCH]
    todo = list(dict.fromkeys([str(m) for m in must] + new + stale))[:MAX_FETCH]
    failed = 0
    for cid in todo:
        try:
            hh[cid] = _fetch_household(az, cid)
        except Exception:
            failed += 1
    left = len(dict.fromkeys([str(m) for m in must] + new + stale)) - len(todo)
    log(f"  household map: {len(todo)} read ({len(new)} new, {len(must)} rewrite checks,"
        f" {len(stale)} stale){f', {left} left for later' if left else ''}"
        f"{f', {failed} failed' if failed else ''}")
    return hh


def policy_households(hh):
    """policyNumber -> customer id."""
    out = {}
    for cid, v in hh.items():
        for p in v.get("policies") or []:
            n = _pn(p.get("policyNumber"))
            if n:
                out.setdefault(n, cid)
    return out


# ---- outcomes --------------------------------------------------------------
def outcome(expiring, terms, day):
    """(outcome, cancel_date_or_None) for one renewal, as known on `day`."""
    R = _d(expiring["expiryDate"])
    after = [t for t in terms if t is not expiring and _d(t["effectiveDate"]) >= R]
    if any(t["status"] in (1, 3, 4) for t in after):
        # An issued renewal term ahead of its date is not retained yet.
        return ("upcoming" if R > day else "retained"), None
    dead = [t for t in after if t["status"] == 0]
    if dead:
        when = min(_d(t.get("modifyDate")) for t in dead)
    elif expiring["status"] == 0:
        when = _d(expiring.get("modifyDate"))
    else:
        return ("upcoming" if R > day else "unconfirmed"), None
    if when > day:
        # Cancelled after the day being reported -- as of `day` it was not.
        return ("upcoming" if R > day else "unconfirmed"), None
    if when < _shift(R, -BEFORE):
        return "before_window", when
    if when > _shift(R, AFTER):
        return "after_window", when
    return "cancelled", when


def _rewritten(pn, expiring, household, R, day):
    line = _line(expiring.get("policyTypeName"))
    lo, hi = _shift(R, -BEFORE), min(_shift(R, AFTER), day)
    for p in (household or {}).get("policies") or []:
        if _NORM(p.get("policyNumber")) == _NORM(pn) or _line(p.get("policyTypeName")) != line:
            continue
        start = max(_d(p.get("effectiveDate")), _d(p.get("soldDate")))
        if lo <= start <= hi and p.get("status") != 0:
            return True
    return False



# The Renewal Outcome Breakdown's segments, in display order: (key, label,
# counts as) -- "kept" and "lost" make the rate, "open" sits outside it. The
# first six are the team's own resolutions; the rest are the policy-record
# reading used when an SR carries no nameable resolution (anything completed
# before RESOLUTIONS_FROM, or an id not named yet).
OUTCOMES = (
    ("renewed_as_is", "Renewed: Accepted as is", "kept"),
    ("renewed_endorsed", "Renewed: Endorsed", "kept"),
    ("rewrite_accepted", "Rewrite Accepted", "kept"),
    ("cancelled_rewrite_declined", "Cancelled: Rewrite Declined", "lost"),
    ("cancelled_no_option", "Cancelled, no endorse/rewrite available", "lost"),
    # Unable to Contact RENEWED as is (Frank, 2026-09-24) and counts as
    # retained. Its own segment only records that nobody ever discussed the
    # renewal with the customer.
    ("unable_to_contact", "Unable to Contact", "kept"),
    ("renewed_record", "Renewed (policy record)", "kept"),
    ("rewritten_record", "Rewritten (policy record)", "kept"),
    ("cancelled_record", "Cancelled (policy record)", "lost"),
    ("already_cancelled", "Already cancelled before the SR", "open"),
    ("pending_record", "Renewal date still ahead", "open"),
    ("no_renewal_record", "No renewal on file", "open"),
    ("unmatched", "Policy record not current", "open"),
)
_BY_LABEL = {label: key for key, label, _ in OUTCOMES}
_NORM = lambda x: re.sub(r"[^A-Z0-9]", "", str(x or "").upper())


def _sr_policy(sr, chains):
    """The policy a renewal SR is about. The subject is "<Line> - <number>"
    (641 of 645 renewal SRs since August match that way); anything else
    policy-number-shaped in the subject or description is the fallback."""
    subj = sr.get("subject") or ""
    cand = [_NORM(x) for x in re.split(r"\s[-\u2013]\s", subj)[1:]]
    cand += [_NORM(w) for w in re.findall(r"[A-Za-z0-9-]{7,}", subj + " " + (sr.get("serviceDesc") or ""))]
    return next((c for c in cand if c in chains), None)


def sr_outcome(sr, chains, hh, pn2hh, as_of):
    """(key, source, policyNumber, premium, line) for one completed renewal SR.
    The SR's own resolution when it can be read (completed on or after
    RESOLUTIONS_FROM with a named id); otherwise the policy record, read as of
    `as_of`, for the term renewing nearest the SR's completion."""
    done = _d(sr.get("completeDate"))
    pn = _sr_policy(sr, chains)
    term, terms = None, chains.get(pn) or []
    if terms:
        lo, hi = _shift(done, -75), _shift(done, 90)
        near = [t for t in terms if lo <= _d(t["expiryDate"]) <= hi
                and _d(t["effectiveDate"]) < _d(t["expiryDate"])]
        near.sort(key=lambda t: (abs((dt.date.fromisoformat(_d(t["expiryDate"]))
                                      - dt.date.fromisoformat(done)).days), t["status"] == 0))
        term = near[0] if near else None
    premium = float((term or {}).get("premium") or 0)
    line = _line((term or (terms[0] if terms else {})).get("policyTypeName"))
    label = RESOLUTION_LABELS.get(sr.get("resolutionId")) if done >= RESOLUTIONS_FROM else None
    if label in _BY_LABEL:
        return _BY_LABEL[label], "resolution", pn, premium, line
    if not term and terms:
        # Chains have gaps: G014379316 has no record for the term that ended
        # 2026-09-19, only the one STARTING that day -- which is the renewal.
        lo, hi = _shift(done, -75), _shift(done, 90)
        start = [t for t in terms if lo <= _d(t["effectiveDate"]) <= hi and t["status"] in (1, 3, 4)]
        if start:
            t = min(start, key=lambda t: _d(t["effectiveDate"]))
            prem = float(t.get("premium") or 0)
            key = "pending_record" if _d(t["effectiveDate"]) > as_of else "renewed_record"
            return key, "record", pn, prem, _line(t.get("policyTypeName"))
    if not term:
        # No term renews anywhere near: a policy AgencyZoom stopped updating
        # (918831825's newest term is 2022-2023, still "in force"), or no
        # policy number in the SR at all.
        return "unmatched", "record", pn, premium, line
    out, when = outcome(term, terms, as_of)
    # A policy cancelled well before the SR was even opened is a stale SR
    # being closed out ("Policy was cancelled in 2025"), not a renewal lost:
    # 9 of the 11 "cancelled" renewal SRs of 09-15..09-22 were exactly that.
    opened = _d(sr.get("createDate"))
    if out != "retained" and when and opened and when < _shift(opened, -15):
        return "already_cancelled", "record", pn, premium, line
    if out == "retained":
        return "renewed_record", "record", pn, premium, line
    if out in ("cancelled", "before_window", "after_window", "unconfirmed"):
        cid = pn2hh.get(pn)
        if cid and _rewritten(pn, term, hh.get(cid), _d(term["expiryDate"]), as_of):
            return "rewritten_record", "record", pn, premium, line
        return ("no_renewal_record" if out == "unconfirmed" else "cancelled_record"), "record", pn, premium, line
    return "pending_record", "record", pn, premium, line


def renewal_srs(day, done_tickets, policies, customers, az=None, log=print, refresh=True):
    """One row per renewal SR completed on `day`: who completed it, the
    outcome, where the outcome came from, and the policy's premium. Rows, not
    totals, so the board can add any range of days together. Also the
    resolution ids completed from RESOLUTIONS_FROM that have no name yet."""
    from service_digest import RENEWALS, SERVICE_TEAM
    srs = [t for t in done_tickets if t.get("workflowName") in RENEWALS
           and _d(t.get("completeDate")) == day]
    chains = collections.defaultdict(list)
    for p in policies:
        chains[_NORM(p.get("policyNumber"))].append(p)
    hh = load_household_map(log=log)
    if refresh and srs:
        # A rewrite shows up as a NEW policy in the household, which only a
        # fresh read of that household can see.
        pn2hh = policy_households(hh)
        must = {pn2hh.get(_sr_policy(t, chains)) for t in srs} - {None}
        hh = refresh_household_map(hh, customers, must=must, az=az, log=log)
        save_household_map(hh, log=log)
    pn2hh = {_NORM(k): v for k, v in policy_households(hh).items()}
    rows, unnamed = [], collections.Counter()
    # The policy record is read as of TODAY, not as of the SR's day: renewal
    # SRs are worked before the renewal date, so on the day one closes the
    # record almost always says "still ahead". Today it says what happened.
    import datetime as _dt
    today = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=-7))).date().isoformat()
    as_of = max(day, today)
    for t in srs:
        key, source, pn, prem, line = sr_outcome(t, chains, hh, pn2hh, as_of)
        rid = t.get("resolutionId")
        if day >= RESOLUTIONS_FROM and rid is not None and rid not in RESOLUTION_LABELS:
            unnamed[rid] += 1
        by = t.get("modifiedBy")
        from service_digest import pipeline_of
        rows.append({"id": t.get("id"), "pipeline": pipeline_of(t.get("workflowName")),
                     "by": by if by in SERVICE_TEAM else None,
                     "by_name": by, "outcome": key, "source": source,
                     "policy": pn, "premium": round(prem), "line": line,
                     "name": t.get("name"), "subject": (t.get("subject") or "").strip()})
    return rows, dict(unnamed)


def list_resolutions(done_tickets, since=RESOLUTIONS_FROM):
    """Every resolutionId on renewal tickets completed since `since`, with two
    examples each -- what to show Frank to name an id once."""
    from service_digest import RENEWALS
    by = collections.defaultdict(list)
    for t in done_tickets:
        if t.get("workflowName") in RENEWALS and _d(t.get("completeDate")) >= since:
            by[t.get("resolutionId")].append(t)
    for rid, ts in sorted(by.items(), key=lambda x: -len(x[1])):
        print(f"id {rid}: {len(ts)} ticket(s), named: {RESOLUTION_LABELS.get(rid, '-- not yet --')}")
        for t in ts[:2]:
            note = re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", t.get("resolutionDesc") or ""))[:80]
            print(f"    {t.get('name')} | {t.get('subject')} | closed {_d(t.get('completeDate'))}"
                  f" by {t.get('modifiedBy')} | {note}")


if __name__ == "__main__":
    # python3 service_retention.py --resolutions [--since YYYY-MM-DD]
    import sys
    import os
    os.chdir(ROOT)
    import secrets_load
    secrets_load.load()
    if "--resolutions" in sys.argv:
        from service_digest import completed_tickets
        import datetime as _dt
        since = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else RESOLUTIONS_FROM
        today = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=-7))).date().isoformat()
        list_resolutions(completed_tickets(today), since)
