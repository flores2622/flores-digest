"""Athena's Renewals tab: what is renewing next, how at risk it is, and the
retention rate of what renewed in the last four weeks (Frank, 2026-09-25).

WHY A SEPARATE TAB. A day's renewal SRs say what the rep DID, not whether the
customer stayed: the SRs close ~45 days before the renewal date, and the
losses show up weeks later -- 27 of the 33 cancelled Late Payment and Service
Pipeline SRs 09-01..09-24 tie to a recent renewal on the same household.
Service is not tracked day by day like sales, so this is one rolling report,
rebuilt every night (renewals/current.json, plus a dated copy).

WHAT A RENEWAL IS. Every personal-lines policy TERM in AgencyZoom's policy
records whose expiry (= renewal) date falls in the window: the last
PAST_DAYS and the next UPCOMING_DAYS. Commercial lines are Cerberus's and
left out, and so are life policies (a term life policy does not renew).
Duplicate terms of one policy are collapsed, a live term beating a
superseded (status 0) copy.

  pipeline   the renewal SR's workflow; with no SR, the carrier:
             Farmers / Foremost (FF_CARRIERS) = Personal Renewals, anything
             else = Other 30 day Renewals (Bristol West and the rest)

WHAT HAPPENED (a renewal date already passed). Frank, 2026-09-25: "if the
policy reads cancelled but no SR has that outcome? yes its still cancelled"
-- so the policy record counts, beside the team's SRs:
  lost         the policy record shows it cancelled from 30 days before the
               renewal on; OR a cancellation SR (Late Payments cancelled /
               client cancelled, Service Pipeline policy cancelled -- read
               from the notes by service_notes.py) ties to it; OR its renewal
               SR was closed on a lost resolution
  mid_term     cancelled more than 30 days before the renewal date, or the
               renewal SR says Mid-term Cancellation. NOT in the rate
               (Frank, 2026-09-25: "no mid term are not considered in the rate")
  retained     a next term exists, the household took a same-line policy
               around the renewal date, or the renewal SR says Rewrite
               Accepted (a rewrite cancels the old policy by design)
  unconfirmed  none of those yet -- AgencyZoom's policy records lag. Shown,
               outside the rate, until it settles.
The rate is retained / (retained + lost).

A cancellation SR carries a household, not a policy (a Late Payment SR's
description is a billing table with no policy number), so it ties to a
renewal only when that household has ONE renewal near the SR -- or one of
the line its subject or note names (home, auto). Otherwise it is a risk flag
on each of the household's renewals, never a loss.

RISK (a renewal still ahead):
  discussed      the renewal SR was closed on Accepted as is / Endorsed /
                 Rewrite -- a rep went over it with the customer
  not discussed  no renewal SR yet, the SR is still open, No action, or
                 Unable to Contact
  warning signs  an open Late Payment SR on the household; a cancellation SR
                 on it. NOT the premium change: AgencyZoom's terms carry stale
                 premiums (one "term" 2022-09-28..2026-09-28 at its 2022
                 price), and even fresh ones disagree with the reps' own
                 "low increase" notes (540881890: $382 -> $1,080), so the
                 report shows the issued renewal premium and no percentage.
  high    not discussed AND a warning sign
  medium  not discussed and renewing within SOON_DAYS; or discussed with a
          warning sign
  low     everything else
"""
import collections
import datetime as dt
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
AZ = dt.timezone(dt.timedelta(hours=-7))
PREFIX = "renewals"
UPCOMING_DAYS = 45
PAST_DAYS = 28
SOON_DAYS = 21
# Carrier ids whose renewals the Personal Renewals workflow carries (read off
# 3,300 renewal SRs, 2026-09-25): Farmers 484668, 102, 262, 484654.
FF_CARRIERS = {484668, 102, 262, 484654}
_LIFE = re.compile(r"\bterm\b|\blife\b|annuit", re.I)
CANCEL_SR = {"cancelled_nonpay", "client_cancelled", "policy_cancelled"}
DISCUSSED = {"renewed_as_is", "renewed_endorsed", "rewrite_accepted"}
_HOME_WORDS = re.compile(r"home|house|dwelling|mobile|manufactured|renter|landlord|condo", re.I)
_AUTO_WORDS = re.compile(r"auto|car\b|vehicle|truck", re.I)


def log(*a):
    print(f"[{dt.datetime.now(AZ):%H:%M:%S}]", *a, flush=True)


def _i(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def _days(a, b):
    return (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days


def build(day, done=None, live=None, log=log):
    """The report as of `day` (the nightly run's day). `done` is the completed
    SR pull (service_digest.completed_tickets), `live` the open SRs (that
    day's data/az_service_tickets_<day>.json); both are read when omitted."""
    import commercial
    import service_digest as sd
    import service_retention as sr
    import renewal_notes as rn

    policies = json.loads((ROOT / "data/az_policies_all.json").read_text())
    customers = json.loads((ROOT / "data/az_customers_all.json").read_text())
    hh = sr.load_household_map(log=log)
    com_any, _ = commercial.households(hh)
    if done is None:
        done = sd.completed_tickets(day, log=log)
    if live is None:
        f = ROOT / f"data/az_service_tickets_{day}.json"
        live = json.loads(f.read_text()) if f.exists() else []
    done = [t for t in done if not commercial.is_commercial_sr(t, com_any)]
    live = [t for t in live if not commercial.is_commercial_sr(t, com_any)
            and str(t.get("status")) == "1"]
    sr.load_resolution_labels(log=log)

    chains = collections.defaultdict(list)
    for p in policies:
        chains[sr._NORM(p.get("policyNumber"))].append(p)
    pn2hh = {sr._NORM(k): str(v) for k, v in sr.policy_households(hh).items()}
    names = {str(c.get("id")): (c.get("businessName") or
                                " ".join(x for x in (c.get("firstname"), c.get("lastname")) if x)).strip()
             for c in customers}

    # ---- the renewals in the window ------------------------------------
    lo, hi = sr._shift(day, -PAST_DAYS), sr._shift(day, UPCOMING_DAYS)
    terms = []
    for pn, chain in chains.items():
        by_exp = collections.defaultdict(list)
        for t in chain:
            R = sr._d(t.get("expiryDate"))
            if lo <= R <= hi and sr._d(t.get("effectiveDate")) < R:
                by_exp[R].append(t)
        for R, ts in by_exp.items():
            t = sorted(ts, key=lambda x: (x.get("status") == 0, -(float(x.get("premium") or 0))))[0]
            typ = (t.get("policyTypeName") or "").strip()
            if commercial.is_commercial_line(typ) or _LIFE.search(typ):
                continue
            terms.append((pn, R, t, chain))

    # ---- renewal SRs, by policy ----------------------------------------
    ren_srs = collections.defaultdict(list)
    for t in done + live:
        if t.get("workflowName") in sd.RENEWALS:
            pn = sr._sr_policy(t, chains)
            if pn:
                ren_srs[pn].append(t)

    def renewal_sr(pn, R):
        c = [t for t in ren_srs.get(pn, [])
             if sr._shift(R, -100) <= sr._d(t.get("createDate")) <= sr._shift(R, 20)]
        closed = [t for t in c if str(t.get("status")) == "2" or t.get("completeDate")]
        if closed:
            return max(closed, key=lambda t: str(t.get("completeDate")))
        return max(c, key=lambda t: str(t.get("createDate"))) if c else None

    matched = {}
    for pn, R, _, _ in terms:
        matched[(pn, R)] = renewal_sr(pn, R)
    closed_srs = [t for t in matched.values() if t and t.get("completeDate")]
    notes = sr.read_notes(closed_srs, log=log)

    # ---- cancellation SRs and open Late Payment SRs, by household --------
    recent = [t for t in done if sr._d(t.get("completeDate")) >= sr._shift(lo, -45)
              and sd.pipeline_of(t.get("workflowName")) in ("late_payments", "changes")]
    ended = sd.sr_outcomes(recent, log=log)
    cancels = collections.defaultdict(list)
    for t in recent:
        e = ended.get(t.get("id"))
        if e and e[0] in CANCEL_SR:
            cancels[str(t.get("householdId"))].append(t)
    late_open = collections.defaultdict(list)
    for t in live:
        if sd.pipeline_of(t.get("workflowName")) == "late_payments":
            late_open[str(t.get("householdId"))].append(t)

    by_hh = collections.defaultdict(list)
    for pn, R, t, _ in terms:
        by_hh[pn2hh.get(pn)].append((pn, R, sr._line(t.get("policyTypeName"))))
    cancel_tie, cancel_flag = {}, collections.defaultdict(list)
    for h, ts in cancels.items():
        for c in ts:
            when = sr._d(c.get("completeDate"))
            cand = [x for x in by_hh.get(h, []) if abs(_days(when, x[1])) <= 45]
            if len(cand) > 1:
                text = f"{c.get('subject') or ''} {rn.clean(c.get('resolutionDesc'))}"
                want = "home" if _HOME_WORDS.search(text) else "auto" if _AUTO_WORDS.search(text) else None
                if want:
                    cand = [x for x in cand if x[2] == want] or cand
            if len(cand) == 1:
                k = cand[0][:2]
                if k not in cancel_tie or when < sr._d(cancel_tie[k].get("completeDate")):
                    cancel_tie[k] = c
            else:
                for x in cand or by_hh.get(h, []):
                    cancel_flag[x[:2]].append(c)

    # ---- one row per renewal ------------------------------------------
    rows = []
    for pn, R, t, chain in sorted(terms, key=lambda x: x[1]):
        h = pn2hh.get(pn)
        s = matched[(pn, R)]
        sr_row = None
        if s is not None:
            if s.get("completeDate"):
                key, source, *_ = sr.sr_outcome(s, chains, hh, pn2hh, max(day, R),
                                                note_key=notes.get(str(s.get("id"))))
                sr_row = {"id": s.get("id"), "state": "done", "outcome": key, "source": source,
                          "by": s.get("modifiedBy"), "done": sr._d(s.get("completeDate")),
                          "note": rn.clean(s.get("resolutionDesc"))[:240]}
            else:
                by = next((n for n, v in sd.SERVICE_TEAM.items() if v["az_id"] == _i(s.get("csr"))), None)
                sr_row = {"id": s.get("id"), "state": "open", "stage": s.get("workflowStageName"),
                          "by": by, "created": sr._d(s.get("createDate"))}
        wf = s.get("workflowName") if s else None
        pipe = (sd.pipeline_of(wf) if wf else
                "renewals_ff" if _i(t.get("carrierId")) in FF_CARRIERS else "renewals_bw")

        nxt = [x for x in chain if x is not t and sr._d(x.get("effectiveDate")) >= R
               and x.get("status") in (1, 3, 4)]
        prem = float(t.get("premium") or 0)
        issued = [x for x in nxt if x.get("status") == 3]
        new_prem = float(min(issued, key=lambda x: sr._d(x.get("effectiveDate"))).get("premium") or 0) if issued else None

        rec, when = sr.outcome(t, chain, day)
        how, status, cancel_date = [], None, None
        tie = cancel_tie.get((pn, R))
        sr_key = (sr_row or {}).get("outcome")
        if rec == "before_window" or sr_key == "cancelled_before_sr":
            status, cancel_date = "mid_term", when
            how.append("policy record" if rec == "before_window" else "renewal SR")
        if status is None and rec == "cancelled":
            status, cancel_date = "lost", when
            how.append("policy record")
        if tie is not None:
            cw = sr._d(tie.get("completeDate"))
            if status is None:
                if cw < sr._shift(R, -30):
                    status, cancel_date = "mid_term", cw
                else:
                    status, cancel_date = "lost", cw
            how.append(f"{tie.get('workflowName')} SR {tie.get('id')}")
        if status is None and sr_key and sr._KIND.get(sr_key) == "lost":
            status = "lost"
            how.append("renewal SR")
        if status in (None, "lost") and h and rec != "retained":
            # A rewrite: a new same-line policy in the household around the
            # renewal date keeps the customer.
            line = sr._line(t.get("policyTypeName"))
            for p in (hh.get(h) or {}).get("policies") or []:
                if sr._NORM(p.get("policyNumber")) == pn or sr._line(p.get("policyTypeName")) != line:
                    continue
                if (p.get("status") in (1, 3, 4)
                        and sr._shift(R, -45) <= sr._d(p.get("effectiveDate")) <= sr._shift(R, 30)):
                    status = "retained"
                    how = [f"rewritten into {p.get('policyNumber')}"]
                    break
        if status in ("lost", "mid_term") and sr_key == "rewrite_accepted":
            # A rewrite cancels the old policy by design: the renewal SR says
            # the customer took the new one (Maria Verdugo, G01-8024842, 09-03).
            status, cancel_date = "retained", None
            how = ["rewritten, per the renewal SR"]
        if status is None:
            status = {"retained": "retained", "after_window": "retained",
                      "upcoming": "upcoming", "unconfirmed": "unconfirmed"}.get(rec, "unconfirmed")
            if status == "retained":
                how.append("policy record")
        if R >= day and status in ("retained", "unconfirmed"):
            status = "upcoming"

        flags = []
        if R >= day and status == "upcoming":
            if sr_row is None:
                flags.append("no_sr")
            elif sr_row["state"] == "open":
                flags.append("sr_open")
            elif sr_key == "no_action_review":
                flags.append("no_action")
            elif sr_key == "unable_to_contact":
                flags.append("not_reached")
            if late_open.get(h):
                flags.append("late_payment_open")
            if cancel_flag.get((pn, R)):
                flags.append("cancel_sr")
        risk = None
        if status == "upcoming":
            undiscussed = not (sr_key in DISCUSSED)
            warn = bool({"late_payment_open", "cancel_sr"} & set(flags))
            soon = _days(day, R) <= SOON_DAYS
            risk = ("high" if undiscussed and warn else
                    "medium" if (undiscussed and soon) or warn else "low")

        rows.append({
            "kind": "past" if R < day else "upcoming", "renewal": R, "policy": t.get("policyNumber"),
            "type": (t.get("policyTypeName") or "").strip(), "line": sr._line(t.get("policyTypeName")),
            "pipeline": pipe, "premium": round(prem), "renewal_premium": round(new_prem) if new_prem else None,
            "household": h, "name": names.get(h) or (s or {}).get("name"),
            "sr": sr_row, "status": status, "cancel_date": cancel_date, "how": how,
            "cancel_srs": [{"id": c.get("id"), "pipeline": sd.pipeline_of(c.get("workflowName")),
                            "done": sr._d(c.get("completeDate")),
                            "note": rn.clean(c.get("resolutionDesc"))[:160]}
                           for c in ([tie] if tie is not None else []) + cancel_flag.get((pn, R), [])],
            "late_open": len(late_open.get(h, [])), "flags": flags, "risk": risk,
        })
    return {
        "version": 1, "as_of": day,
        "built_at": dt.datetime.now(AZ).isoformat(timespec="seconds"),
        "past_days": PAST_DAYS, "upcoming_days": UPCOMING_DAYS, "soon_days": SOON_DAYS,
        "pipelines": [[k, label] for k, label, _, kind in sd.PIPELINES if kind == "renewal"],
        "sr_outcomes": sr.outcomes(),
        "team": list(sd.SERVICE_TEAM),
        "rows": rows,
    }


def publish(day, doc=None, log=log):
    import publish_board
    doc = doc if doc is not None else build(day, log=log)
    cli, bucket = publish_board._client()
    body = json.dumps(doc, default=str).encode()
    for key in (f"{PREFIX}/current.json", f"{PREFIX}/{day}.json"):
        cli.put_object(Bucket=bucket, Key=key, Body=body,
                       ContentType="application/json", CacheControl="no-store")
    past = [r for r in doc["rows"] if r["kind"] == "past"]
    kept = sum(r["status"] == "retained" for r in past)
    lost = sum(r["status"] == "lost" for r in past)
    log(f"  renewals: {len(past)} renewed in the last {PAST_DAYS} days "
        f"({kept} retained, {lost} lost), {len(doc['rows']) - len(past)} coming up "
        f"-> r2://{bucket}/{PREFIX}/current.json ({len(body):,} bytes)")
    return doc


def main():
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--day")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    day = a.day or dt.datetime.now(AZ).date().isoformat()
    os.chdir(ROOT)
    import secrets_load
    secrets_load.load()
    live = None
    if not (ROOT / f"data/az_service_tickets_{day}.json").exists():
        # By hand, before the nightly run has saved the day's open SRs: read
        # them into memory only, never into that day's file (CLAUDE.md,
        # "Rebuilding a past day").
        from az_client import AgencyZoom
        live = AgencyZoom().service_tickets_live()
    doc = build(day, live=live)
    if a.dry_run:
        print(json.dumps(doc, indent=1, default=str)[:4000])
        return
    publish(day, doc)


if __name__ == "__main__":
    main()
