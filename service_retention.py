"""Retention across the renewal window, for the service digest.

For every policy renewing in a window, what happened between 30 days before
its renewal date and 45 days after it (Frank, 2026-09-23): retained,
rewritten, cancelled -- in households, policies and premium -- plus which of
those households had a change (endorsement) processed in the same window.
Two views side by side:

    live   renewal dates from 45 days ago to 30 days ahead, as things stand
           today; renewals still ahead of us are "upcoming"
    month  the last calendar month whose every renewal has had its full 45
           days, so the outcome is final

HOW A POLICY'S OUTCOME IS READ. AgencyZoom keeps one record per policy TERM,
chained by policyNumber, and the status codes carry no labels. Read off the
chains (2026-09-23): 1 = in force, 3 = the next term already issued (it carries
the renewal premium), 4 = a past term that was replaced, 0 = cancelled -- or a
superseded duplicate of a term that also exists as a 4, which is why a 0 only
means cancelled when no live term follows it.

    retained     a term starting on or after the renewal date is 1, 3 or 4
    cancelled    the renewal term is 0, or the expiring term is 0 with no
                 successor; the cancellation must fall inside the window
    rewritten    cancelled or no renewal on file, but the same household took
                 a new policy number of the same line inside the window
                 (a rewrite, or a carrier re-numbering the renewal)
    unconfirmed  the renewal date has passed and nothing follows it yet
    upcoming     (live view only) renewal date still ahead, not cancelled
    before_window cancelled MORE than 30 days before renewal: reported on its
                 own row, outside the rate -- 49 of July's 335 renewals
                 were, most of them months earlier

THERE IS NO CANCELLATION DATE in any AgencyZoom policy payload. The term's
own modifyDate stands in for it -- the day the record last changed, which for
a cancelled term is the day it was cancelled or later. That is what keeps a
policy cancelled in February out of a July renewal's window. From 2026-09-24
the daily AgencyZoom snapshot (r2_cache.save_corpus) records the day a term
flips to 0, which is the real date going forward.

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
LIVE_BACK, LIVE_AHEAD = 45, 30         # the live view's span of renewal dates
REFRESH_STALE_DAYS = 30                # every household re-read at least monthly
REFRESH_BATCH = 150                    # of those, how many per night
# Hard cap on household reads in one build. The whole book is ~4,100 reads at
# AgencyZoom's ~1 per 0.7s -- most of an hour. A night that starts without the
# saved map (or a burst of new customers) must never spend that inside the
# nightly run; it works through the backlog a few hundred a night instead.
MAX_FETCH = 400

_HOME = re.compile(r"home|dwelling|\bdp\d?\b|mobile|manufactured|landlord|condo|renter|ho-?\d", re.I)
CHANGE = re.compile(r"endors|change|add|remov|replac|swap|delet|updat|vehicle|driver|"
                    r"lienholder|mortgagee|coverage", re.I)
CANCEL = re.compile(r"cancel|canc\b|non.?renew", re.I)


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
def renewals(policies, lo, hi):
    """One row per policyNumber whose term expires (renews) in [lo, hi]."""
    chains = collections.defaultdict(list)
    for p in policies:
        n = _pn(p.get("policyNumber"))
        if n:
            chains[n].append(p)
    out = []
    for n, terms in chains.items():
        exp = [t for t in terms if lo <= _d(t["expiryDate"]) <= hi
               and _d(t["effectiveDate"]) < _d(t["expiryDate"])]
        if not exp:
            continue
        # A 0 alongside a live copy of the same term is a duplicate, not a
        # cancellation -- prefer the live copy.
        exp.sort(key=lambda t: (t["status"] == 0, _d(t.get("createDate"))))
        out.append((n, exp[0], terms))
    return out


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
        if _pn(p.get("policyNumber")) == pn or _line(p.get("policyTypeName")) != line:
            continue
        start = max(_d(p.get("effectiveDate")), _d(p.get("soldDate")))
        if lo <= start <= hi and p.get("status") != 0:
            return True
    return False


def _cohort(policies, hh, pn2hh, lo, hi, day):
    rows = []
    for pn, e, terms in renewals(policies, lo, hi):
        out, when = outcome(e, terms, day)
        if out == "after_window":
            continue            # its loss belongs to a later renewal's window
        cid = pn2hh.get(pn)
        R = _d(e["expiryDate"])
        # A policy with no renewal on file is often one the carrier re-numbered
        # (the old G01-xxxxxxx-00 style), which looks exactly like a rewrite:
        # a new number, same line, same household, inside the window.
        if out in ("cancelled", "unconfirmed") and cid and _rewritten(pn, e, hh.get(cid), R, day):
            out = "rewritten"
        rows.append({"policy": pn, "household": cid, "renewal": R, "outcome": out,
                     "premium": float(e.get("premium") or 0), "line": _line(e.get("policyTypeName")),
                     "cancelled_on": when})
    return rows


def _endorsed(rows, done_tickets, day):
    """Households in the cohort with a change ticket completed inside their
    own renewal window (and by `day`)."""
    by_hh = collections.defaultdict(list)
    for t in done_tickets:
        if t.get("workflowName") != "Service Pipeline":
            continue
        text = " ".join(str(t.get(k) or "") for k in ("subject", "serviceDesc", "resolutionDesc"))
        if CANCEL.search(t.get("subject") or "") or not CHANGE.search(text):
            continue
        by_hh[str(t.get("householdId"))].append(_d(t.get("completeDate")))
    hit = set()
    for r in rows:
        lo, hi = _shift(r["renewal"], -BEFORE), min(_shift(r["renewal"], AFTER), day)
        if r["household"] and any(lo <= c <= hi for c in by_hh.get(r["household"], [])):
            hit.add(r["policy"])
    return hit


def _summarize(rows, endorsed):
    def agg(rs):
        return {"households": len({r["household"] or f"?{r['policy']}" for r in rs}),
                "policies": len(rs), "premium": round(sum(r["premium"] for r in rs))}
    by = collections.defaultdict(list)
    for r in rows:
        by[r["outcome"]].append(r)
    out = {k: agg(by.get(k, [])) for k in ("retained", "rewritten", "cancelled",
                                           "unconfirmed", "upcoming", "before_window")}
    out["endorsed"] = agg([r for r in rows if r["policy"] in endorsed
                           and r["outcome"] != "before_window"])
    decided = out["retained"]["policies"] + out["rewritten"]["policies"] + out["cancelled"]["policies"]
    kept_prem = out["retained"]["premium"] + out["rewritten"]["premium"]
    decided_prem = kept_prem + out["cancelled"]["premium"]
    out["rate_policies"] = round(100 * (decided - out["cancelled"]["policies"]) / decided, 1) if decided else None
    out["rate_premium"] = round(100 * kept_prem / decided_prem, 1) if decided_prem else None
    # The same rate with "no renewal on file" counted as lost -- the floor,
    # since some of those are only a renewal term AgencyZoom has not got yet.
    worst = decided + out["unconfirmed"]["policies"]
    out["rate_policies_floor"] = round(100 * (decided - out["cancelled"]["policies"]) / worst, 1) if worst else None
    in_window = [r for r in rows if r["outcome"] != "before_window"]
    out["matched"] = sum(1 for r in in_window if r["household"])
    out["total"] = len(in_window)
    return out


def figures(day, policies, customers, done_tickets, az=None, log=print, refresh=True):
    hh = load_household_map(log=log)
    pn2hh = policy_households(hh)
    live_lo, live_hi = _shift(day, -LIVE_BACK), _shift(day, LIVE_AHEAD)
    # Last month whose final renewal has had its full AFTER days.
    m_end = (dt.date.fromisoformat(day) - dt.timedelta(days=AFTER)).replace(day=1) - dt.timedelta(days=1)
    m_lo, m_hi = m_end.replace(day=1).isoformat(), m_end.isoformat()
    if refresh:
        pre = _cohort(policies, hh, pn2hh, min(live_lo, m_lo), max(live_hi, m_hi), day)
        must = {r["household"] for r in pre
                if r["outcome"] in ("cancelled", "unconfirmed") and r["household"]}
        hh = refresh_household_map(hh, customers, must=must, az=az, log=log)
        save_household_map(hh, log=log)
        pn2hh = policy_households(hh)
    live = _cohort(policies, hh, pn2hh, live_lo, live_hi, day)
    month = _cohort(policies, hh, pn2hh, m_lo, m_hi, day)
    return {
        "window": {"before": BEFORE, "after": AFTER},
        "live": {"from": live_lo, "to": live_hi, **_summarize(live, _endorsed(live, done_tickets, day))},
        "month": {"month": m_lo[:7], "from": m_lo, "to": m_hi,
                  **_summarize(month, _endorsed(month, done_tickets, day))},
        "cancel_date_note": "modifyDate stands in for the cancellation date until daily snapshots cover the window",
    }
