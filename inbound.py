"""Inbound calls that actually reach a producer.

THE PROBLEM THIS SOLVES. Nothing in the pipeline has ever looked at inbound
calls, so roughly 90 minutes of real producer conversation a day was invisible
-- including Abner Castanon's 19m54s call back to Lorena and Rasha Hassoun's
87-second one to Sarahi, which is why Rasha read as a voicemail.

ATTRIBUTION. Frank, 2026-08-26: "Debbie is our front desk, she handles probably
90% of all inbound calls, period. she transfers to who the call in is for, or to
the next producer available if its a cold call in."

That shape is visible in the legs and there are exactly two routes:

  DIRECT      the caller rang a producer's own DID.
  TRANSFERRED the caller rang the main line, the ring group "Flores Insurance
              Inbounds" rang everyone, Debbie picked up, and the producer took
              it off park. Debbie's hold shows as FindMe, the producer's pickup
              as Park Location.

Talk time is the PRODUCER'S leg, never the whole call. Debbie held Crystal's
Barrandey Flores call 117 seconds before handing it over: the call is 562s and
Crystal's conversation is 371s. Charging producers with front-desk time would
quietly pad every average.

A personal DID is a number exactly ONE person dials out from. That is what
keeps the main line out: +19287267222 is dialled out from by Amanda, Debbie,
Mike, Sarahi and Veronica, so it identifies nobody. Deriving it beats a
hardcoded list, which would rot the first time an extension moves. Debbie and
Amanda match neither route, so their calls -- 24 of the 38 answered on
2026-08-25 -- drop out with no special-casing. Amanda sells but is deliberately
not tracked (Frank, 2026-08-26).
"""
import collections
import datetime as dt

from digest_config import PRODUCERS

AZ_OFFSET = dt.timedelta(hours=7)      # Arizona does not observe DST
RING_GROUP_ACTIONS = ("Park Location", "FindMe")
# Frank, 2026-08-26: "doesnt have to be that day, could be the next day, we dial
# leads every other day, usually." An every-other-day cadence means a call back
# can arrive a day or two after the dial it answers.
CALLBACK_LOOKBACK_DAYS = 3

# WHERE A CALL BACK IS REPORTED. Frank, 2026-08-26: "the call back should stay
# on the day the call happened, so it would be a new line on that days call
# detail as an inbound call in."
#
# So a call back never moves to the day of the dial it answers -- that day's
# report has already gone out and must not change under anyone. It lands on the
# day it happened, as its own Call Detail line marked inbound, carrying a
# reference to the dial it is answering. Only a call back arriving on the SAME
# day as its dial merges into that dial's row, which is the case Frank
# described earlier: combined talk time and a summary covering both
# conversations, when both were live.


def az_day(rec):
    ts = str(rec.get("startTime") or "")
    if not ts:
        return None
    try:
        t = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (t - AZ_OFFSET).date().isoformat()


def last10(s):
    d = "".join(c for c in (s or "") if c.isdigit())
    return d[-10:] if len(d) >= 10 else None


def personal_dids(records):
    """DID -> producer, for numbers exactly one person dials out from."""
    users = collections.defaultdict(set)
    for r in records:
        if r.get("direction") != "Outbound":
            continue
        f = r.get("from") or {}
        if f.get("phoneNumber") and f.get("name"):
            users[f["phoneNumber"]].add(f["name"])
    return {d: next(iter(v)) for d, v in users.items()
            if len(v) == 1 and next(iter(v)) in PRODUCERS}


def attribute(rec, dids):
    """(producer, talk_seconds, route) for one inbound record, or (None, 0, None)."""
    who = dids.get((rec.get("to") or {}).get("phoneNumber"))
    if who:
        return who, rec.get("duration") or 0, "direct"
    best = None
    for l in rec.get("legs") or []:
        if l.get("result") != "Call connected":
            continue
        f = (l.get("from") or {}).get("name")
        if f not in PRODUCERS or l.get("action") not in RING_GROUP_ACTIONS:
            continue
        # A FindMe leg is someone's phone ringing THEMSELVES; anything else on
        # that action is the group hunting and is not a pickup.
        if l.get("action") == "FindMe" and (l.get("to") or {}).get("name") != f:
            continue
        if best is None or (l.get("duration") or 0) > best[1]:
            best = (f, l.get("duration") or 0)
    return (best[0], best[1], "transferred") if best else (None, 0, None)


def answered(day, records):
    """Answered inbound calls on `day` that reached a producer."""
    dids = personal_dids(records)
    out = []
    for r in records:
        if r.get("direction") != "Inbound" or r.get("result") != "Accepted":
            continue
        if az_day(r) != day:
            continue
        who, secs, route = attribute(r, dids)
        if not who:
            continue
        out.append({"id": r["id"], "producer": who, "seconds": secs,
                    "route": route, "day": day,
                    "number": (r.get("from") or {}).get("phoneNumber"),
                    "recording": bool(r.get("recording")),
                    "start": r.get("startTime")})
    return out


def link_callbacks(rows, window, day, lookback=CALLBACK_LOOKBACK_DAYS):
    """Mark each inbound row as a call back to a recent dial, or a cold call-in.

    Attached to the producer's MOST RECENT prior dial to that number, which is
    the one it is answering. Anything older is a cold call-in as far as this
    day's report is concerned.
    """
    floor = (dt.date.fromisoformat(day) - dt.timedelta(days=lookback)).isoformat()
    dialled = collections.defaultdict(list)
    for r in window:
        if r.get("direction") != "Outbound":
            continue
        d = az_day(r)
        if not d or d > day or d < floor:
            continue
        n = last10((r.get("to") or {}).get("phoneNumber"))
        w = (r.get("from") or {}).get("name")
        if n and w in PRODUCERS:
            dialled[(w, n)].append((d, r))
    for row in rows:
        prior = dialled.get((row["producer"], last10(row["number"])) , [])
        prior.sort(key=lambda x: x[0])
        row["callback_of"] = prior[-1][1]["id"] if prior else None
        row["callback_day"] = prior[-1][0] if prior else None
        row["kind"] = "callback" if prior else "cold call-in"
    return rows


def screen(rows, day):
    """Decide which inbound calls are worth transcribing, BEFORE fetching audio.

    Frank, 2026-08-26: "We need to not transcribe inbound calls that are
    service, renewals, or not sales."

    Deliberately the SAME record tests day_calls applies to outbound dials, run
    against the caller's number, so the two directions cannot disagree about
    what counts as service. Each row gets a `skip` reason or None.
    """
    import day_calls
    from az_corpus import e164
    lead_idx, cust_idx, svc_customers, svc_phones = day_calls.build_context(day)
    for row in rows:
        num = e164(row["number"])
        cands = lead_idx.get(num, []) if num else []
        custs = cust_idx.get(num, []) if num else []
        who = row["producer"]
        skip = None
        if not num:
            skip = "no caller id"
        elif not cands and not custs:
            skip = "no AgencyZoom record"
        elif not cands:
            skip = "customer record only (service/renewal)"
        elif any(c["id"] in svc_customers.get(who, set()) for c in custs):
            skip = "service/renewal task due today for this producer"
        elif svc_phones.get((who, num)):
            wf = svc_phones[(who, num)][0].get("workflowName") or "service"
            skip = f"open {wf} ticket with this producer as CSR"
        elif day_calls.is_household_housekeeping(cands, day):
            skip = day_calls.is_household_housekeeping(cands, day)
        row["e164"] = num
        row["skip"] = skip
    return rows
