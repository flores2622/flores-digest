"""Renewal SR outcomes, for the service digest's Renewal Outcome Breakdown.

FRAMING (Frank, 2026-09-23): not an agency-wide retention rate. Of the
renewal SRs COMPLETED on a day (or across a filtered range of days), what was
the outcome -- and the retention rate among just those SRs.

WHERE AN OUTCOME COMES FROM. Frank's resolutions are the ONLY outcomes
(Frank, 2026-09-24) -- Renewed: Accepted as is, No action: Review if needed,
Renewed: Endorsed, Rewrite Accepted, Cancelled: Rewrite Declined, Cancelled,
no endorse/rewrite available, Client Cancelled, Unable to Contact/No Show and
Mid-term Cancellation -- read in this order:
  1. the SR's own resolution, matched by id (RESOLUTION_KEY_BY_ID);
  2. for an SR closed on anything else (Completed), the rep's note, read by
     the model in renewal_notes.py into one of them;
  3. no note, or a note that does not say: Unable to Contact/No Show.
The policy record is read only to tell a cancellation that came before the SR
was opened (Mid-term Cancellation, outside the rate) and for the premium.

HOW A POLICY'S OUTCOME IS READ. AgencyZoom keeps one record per policy TERM,
chained by policyNumber, and the status codes carry no labels. Read off the
chains (2026-09-23): 1 = in force, 3 = the next term already issued (it carries
the renewal premium), 4 = a past term that was replaced, 0 = cancelled -- or a
superseded duplicate of a term that also exists as a 4, which is why a 0 only
means cancelled when no live term follows it.

outcome() reads a term as retained, cancelled (and when), or not yet decided;
only its cancellation date is used now, to tell a cancellation that came
before the SR was opened.

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
# The ONLY resolutions the team uses on renewal tickets from 2026-09-24
# (RESOLUTIONS_FROM). They are read on EVERY renewal SR, past ones included
# (Frank, 2026-09-24): the ids that now carry the names were used for the
# same outcomes before the rename -- 32570's notes are cancellations, 32574's
# are renewals reviewed with the customer. What RESOLUTIONS_FROM still decides
# is only which SRs closed on anything ELSE are listed on the Service tab as
# not a renewal resolution; before it, "Completed" was the normal choice. The names
# and what each counts as are OUTCOMES below.
RESOLUTIONS_FROM = "2026-09-24"
# SRs carry resolutionId only; the names come from /v1/api/service-resolutions
# (found 2026-09-24), re-read every build by load_resolution_labels() so a
# rename in AgencyZoom is picked up. This is that endpoint's list on
# 2026-09-24, kept as the fallback when the read fails.
RESOLUTION_LABELS = {
    32574: "Renewed: Accepted as is",
    32575: "Renewed: Endorsed",
    38307: "Rewrite Accepted",
    38308: "Cancelled: Rewrite Declined",
    32570: "Cancelled, no endorse/rewrite available",
    38304: "Unable to Contact/No Show",         # renamed 2026-09-24
    101591: "No action: Review if needed",      # added 2026-09-24
    101627: "Client Cancelled",                 # added 2026-09-24
    101637: "Mid-term Cancellation",            # added 2026-09-24
    # Not renewal outcomes. A renewal SR closed on one of these from
    # RESOLUTIONS_FROM falls back to the policy record and is listed on the
    # Service tab as not a renewal resolution. Completed is kept in AgencyZoom for
    # changes, NOC and missing documents -- never renewals (Frank, 2026-09-24).
    # The other four were DELETED in AgencyZoom on 2026-09-24 and no longer
    # come back from the endpoint; keep them here, since past SRs still carry
    # those ids.
    32571: "Completed",
    38303: "Unable to Complete",
    38305: "Cancelled by Carrier",
    38306: "Cancelled by Client",
    40108: "Shot Clock Expired",
}
_SNAPSHOT = dict(RESOLUTION_LABELS)

# Deleting a resolution in AgencyZoom MOVES every SR that carried it onto
# another one. Frank's 2026-09-24 clean-up moved Shot Clock Expired (357
# renewal SRs, none with a note) and Unable to Complete (112: "wrong dates",
# "took noc payment") onto Unable to Contact, which a renewal SR had carried
# exactly once before. So on SRs completed before the date here, that id
# says nothing about the renewal and is read as if it were not a renewal
# resolution: the rep's note, then the policy record.
RESOLUTION_VALID_FROM = {38304: "2026-09-24"}


def resolution_label(sr):
    """The resolution name on an SR, or None when its id cannot be trusted
    for the day the SR was completed (see RESOLUTION_VALID_FROM)."""
    rid = sr.get("resolutionId")
    since = RESOLUTION_VALID_FROM.get(rid)
    if since and _d(sr.get("completeDate")) < since:
        return None
    return RESOLUTION_LABELS.get(rid)


def load_resolution_labels(az=None, log=print):
    """Refresh RESOLUTION_LABELS in place from AgencyZoom. A name that no
    longer matches the snapshot is logged: renaming a resolution changes what
    every SR already closed on it reads as."""
    try:
        if az is None:
            from az_client import AgencyZoom
            az = AgencyZoom()
        live = {int(r["id"]): r["name"].strip() for r in az.get("/v1/api/service-resolutions") or []}
    except Exception as e:
        log(f"  resolution names: using the 2026-09-24 list ({type(e).__name__}: {e})")
        return RESOLUTION_LABELS
    for rid, name in live.items():
        if rid in _SNAPSHOT and _SNAPSHOT[rid] != name:
            log(f"  resolution {rid} RENAMED in AgencyZoom: {_SNAPSHOT[rid]!r} -> {name!r}")
    RESOLUTION_LABELS.update(live)
    return RESOLUTION_LABELS

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



# The Renewal Outcome Breakdown's segments, in display order: (key, label,
# counts as) -- "kept" and "lost" make the rate, "open" sits outside it.
# FRANK'S RESOLUTIONS ARE THE ONLY OUTCOMES (Frank, 2026-09-24): every renewal
# SR lands on one of the nine below, never on a category of ours. The label
# here is the fallback; the board shows AgencyZoom's current name (outcomes()).
OUTCOMES = (
    ("renewed_as_is", "Renewed: Accepted as is", "kept"),
    # No action (Frank, 2026-09-24): the rep reviewed the renewal and did not
    # call because the change did not call for it. It renewed as is.
    ("no_action_review", "No action: Review if needed", "kept"),
    ("renewed_endorsed", "Renewed: Endorsed", "kept"),
    ("rewrite_accepted", "Rewrite Accepted", "kept"),
    ("cancelled_rewrite_declined", "Cancelled: Rewrite Declined", "lost"),
    ("cancelled_no_option", "Cancelled, no endorse/rewrite available", "lost"),
    # Client Cancelled (Frank, 2026-09-24): went to the carrier directly to
    # cancel, or never gave us the chance to review or retain. A lost
    # renewal, in the rate. A policy cancelled mid term, before the SR, is
    # Mid-term Cancellation instead.
    ("client_cancelled", "Client Cancelled", "lost"),
    # Unable to Contact (renamed Unable to Contact/No Show, 2026-09-24) RENEWED
    # as is and counts as retained. It is also the outcome of a renewal SR
    # whose note is missing or says nothing (Frank, 2026-09-24).
    ("unable_to_contact", "Unable to Contact/No Show", "kept"),
    # Mid-term Cancellation (Frank, 2026-09-24, id 101637): the policy was
    # already cancelled -- mid term, or any time -- before the renewal SR was
    # generated, so an old SR closed out ("Cancelled in 2025", "sold home").
    # Also where a cancellation resolution lands when the policy record shows
    # it cancelled well before the SR was opened. Shown as cancelled, OUTSIDE
    # the rate.
    ("cancelled_before_sr", "Mid-term Cancellation", "open"),
)
# Matched by resolution ID, never by name, so a rename in AgencyZoom cannot
# drop an outcome.
RESOLUTION_KEY_BY_ID = {
    32574: "renewed_as_is", 101591: "no_action_review", 32575: "renewed_endorsed",
    38307: "rewrite_accepted", 38308: "cancelled_rewrite_declined",
    32570: "cancelled_no_option", 101627: "client_cancelled", 38304: "unable_to_contact",
    101637: "cancelled_before_sr",
}
RESOLUTION_KEYS = list(RESOLUTION_KEY_BY_ID.values())
_KIND = {key: kind for key, _, kind in OUTCOMES}
_ID_BY_KEY = {k: i for i, k in RESOLUTION_KEY_BY_ID.items()}


def outcomes():
    """OUTCOMES for a document, with each resolution's current AgencyZoom name."""
    return [[k, RESOLUTION_LABELS.get(_ID_BY_KEY.get(k)) or l, c] for k, l, c in OUTCOMES]


def resolution_key(sr):
    """The outcome key of the SR's own resolution, or None when it is not one
    of the nine -- or not trusted for that day (RESOLUTION_VALID_FROM)."""
    rid = sr.get("resolutionId")
    since = RESOLUTION_VALID_FROM.get(rid)
    if since and _d(sr.get("completeDate")) < since:
        return None
    return RESOLUTION_KEY_BY_ID.get(rid)


_NORM = lambda x: re.sub(r"[^A-Z0-9]", "", str(x or "").upper())


def _sr_policy(sr, chains):
    """The policy a renewal SR is about. The subject is "<Line> - <number>"
    (641 of 645 renewal SRs since August match that way); anything else
    policy-number-shaped in the subject or description is the fallback."""
    subj = sr.get("subject") or ""
    cand = [_NORM(x) for x in re.split(r"\s[-\u2013]\s", subj)[1:]]
    cand += [_NORM(w) for w in re.findall(r"[A-Za-z0-9-]{7,}", subj + " " + (sr.get("serviceDesc") or ""))]
    return next((c for c in cand if c in chains), None)


def sr_outcome(sr, chains, hh, pn2hh, as_of, note_key=None):
    """(key, source, policyNumber, premium, line) for one completed renewal SR,
    always one of Frank's resolutions (OUTCOMES):
      1. the SR's own resolution, when it is one of the nine    source "resolution"
      2. else `note_key`, what renewal_notes read from the note  source "notes"
      3. else Unable to Contact/No Show -- no note, or a note that does not
         say (Frank, 2026-09-24)                                 source "no_note"
         ... or a note not read yet (the read failed)            source "unread"
    The policy record only decides whether a cancellation came before the SR
    was opened (cancelled_before_sr, outside the rate), and gives the premium."""
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
    key = resolution_key(sr)
    source = "resolution"
    if not key:
        import renewal_notes
        if note_key == "cancelled_before_sr":
            # the note itself says the policy was gone before this renewal
            # ("Policy cancelled in 2025", SR 12498281, 09-02)
            return "cancelled_before_sr", "notes", pn, premium, line
        if note_key in RESOLUTION_KEYS:
            key, source = note_key, "notes"
        elif renewal_notes.clean(sr.get("resolutionDesc")) and note_key is None:
            key, source = "unable_to_contact", "unread"
        else:
            key, source = "unable_to_contact", "no_note"
    if _KIND[key] == "lost":
        # A cancellation counts as a renewal LOST only on a policy with a term
        # renewing near the SR, not cancelled well before the SR was opened.
        # Of the 12 SRs resolved "Cancelled, no endorse/rewrite available"
        # 09-15..09-23, 9 were policies cancelled long before ("Cancelled in
        # 2025") and 3 had no term renewing anywhere near ("cancelled for noc
        # 10/2025", "not a right policy").
        stale = not term
        if term:
            _, when = outcome(term, terms, as_of)
            opened = _d(sr.get("createDate"))
            stale = bool(when and opened and when < _shift(opened, -15))
        if stale:
            return "cancelled_before_sr", source, pn, premium, line
    return key, source, pn, premium, line


def read_notes(srs, log=print):
    """renewal_notes.read() for the SRs NOT closed on one of the nine."""
    import renewal_notes
    return renewal_notes.read([t for t in srs if not resolution_key(t)], log=log)


def renewal_srs(day, done_tickets, policies, customers, az=None, log=print, refresh=True):
    """One row per renewal SR completed on `day`: who completed it, the
    outcome, where the outcome came from, and the policy's premium. Rows, not
    totals, so the board can add any range of days together. Also the
    SRs completed from RESOLUTIONS_FROM on a resolution that is not one of
    the nine renewal resolutions, counted by resolution name."""
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
    load_resolution_labels(az=az, log=log)
    notes = read_notes(srs, log=log)
    rows, unnamed = [], collections.Counter()
    # The policy record is read as of TODAY, not as of the SR's day: renewal
    # SRs are worked before the renewal date, so on the day one closes the
    # record almost always says "still ahead". Today it says what happened.
    import datetime as _dt
    today = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=-7))).date().isoformat()
    as_of = max(day, today)
    for t in srs:
        key, source, pn, prem, line = sr_outcome(t, chains, hh, pn2hh, as_of,
                                                 note_key=notes.get(str(t.get("id"))))
        rid = t.get("resolutionId")
        if day >= RESOLUTIONS_FROM and not resolution_key(t):
            unnamed[RESOLUTION_LABELS.get(rid) or ("No resolution" if rid is None else f"id {rid}")] += 1
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
        print(f"id {rid}: {len(ts)} SR(s), {RESOLUTION_LABELS.get(rid, '-- unknown id --')}")
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
        load_resolution_labels()
        list_resolutions(completed_tickets(today), since)
