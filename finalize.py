"""Total each producer AFTER the call read, not during the build.

Frank, 2026-08-26: "can we just not compute the call volume until later?"

Yes. build_metrics now keeps every counted dial on M[who]["dials"] instead of
collapsing them into six numbers on the spot. Nothing between that point and
here could previously drop a dial and still leave an honest call volume behind
-- the raw material was already gone.

The read is the reason it matters. AgencyZoom is not always right about which
calls are service work: Luis Martinez's renewal had no service ticket, no
service task and a customer record the exclusion rules could not see, and the
only source that knew was Crystal saying "I went ahead and reviewed your
renewal" thirty seconds in. call_summary marks those rows; this drops them and
re-totals what is left.

BLAST RADIUS. These six numbers feed the leaderboard, the funnel, the contact
rate panel and the audit, so a bug here is wrong everywhere at once and looks
consistent while it does it. Hence verify(): on a day where nothing is flagged
the deferred totals must equal what the old in-loop code produced, exactly.
"""
import collections


def _totals(dials, rows):
    """Six figures from the dial rows and the Call Detail rows.

    CONTACT RATE STAYS OUTBOUND. A dial is an attempt the producer made. A call
    back changes the VERDICT on a dial already made -- so it lands inside the
    numerator by turning that dial live, never beside it -- and a cold call-in
    had no dial at all. Counting call-ins in the numerator would make the rate
    mean nothing and let it pass 100%.

    TALK TIME COUNTS EVERY CONVERSATION, inbound included (Frank, 2026-08-26:
    "I want call ins to be considered for talk time, and in the call detail").
    The average is over real conversations, not over dials, so an inbound row
    brings both its seconds and itself to the divisor.
    """
    kept = [d for d in dials if not d.get("dropped")]
    live = [d for d in kept if d.get("live")]
    convos = list(rows)                       # outbound live rows + inbound rows
    talk = sum(r.get("seconds") or 0 for r in convos)
    inbound_rows = [r for r in convos if r.get("inbound")]
    return {
        # DISTINCT numbers; attempts is every dial on those same numbers, so a
        # producer working one number three times shows 1 against 3.
        "call_volume": len(kept),
        "total_dials": sum(d.get("attempts") or 0 for d in kept),
        "live": len(live),
        "contact_rate": round(len(live) / len(kept) * 100, 1) if kept else 0,
        "avg_talk": round(talk / len(convos)) if convos else 0,
        "outcomes": dict(collections.Counter(d["bucket"] for d in kept)),
        # How many dials in each bucket got a call back the same day. Drawn as
        # a candy-cane slice INSIDE its bucket, so the segments still sum to
        # the dial count and Live Contact keeps meaning one thing everywhere
        # (Frank, 2026-08-27).
        "outcomes_callback": dict(collections.Counter(
            d["bucket"] for d in kept if d.get("callback"))),
        "inbound": len(inbound_rows),
        "inbound_seconds": sum(r.get("seconds") or 0 for r in inbound_rows),
        "call_detail": convos,
    }


def apply(M):
    """Re-total every producer in place. Safe to call more than once."""
    for who, v in M.get("producers", {}).items():
        dials = v.get("dials") or []
        dropped = {d["number"] for d in dials if d.get("dropped")}
        detail = [r for r in (v.get("call_detail") or [])
                  if r["number"] not in dropped]
        v.update(_totals(dials, detail))
    return M


def flag_service(M, who, number, why="service/renewal (from the call)"):
    """Mark one dial as service work found by the read. apply() does the rest.

    REFUSED while an OPEN lead sits on that number. Somebody is working the
    household for new business, so the call belongs to that effort whatever the
    audio sounded like.

    Coral's 2026-08-25 call to Carlos Cruz is the case: she was chasing his
    CURRENT carrier's declarations page to compare against her offer, the model
    read "documents needed to issue his policy" as service, and a live
    new-business contact vanished from her day (Frank, 2026-08-26: "its an open
    lead and shes chasing competitor dec pages to compare our offer").

    "Has this household ever bought anything" CANNOT carry the test, which is
    what this guard tried first. Carlos and Crystal's Ruben Serrano are both
    converted customer households with a customer record and no soldDate on any
    lead -- indistinguishable on that question. The open lead is what separates
    them: Carlos has a status-0 lead assigned to Coral, Ruben's single lead is
    status 5 and his renewal-review call is real service.

    The model's judgment is the weaker signal and the records overrule it.
    """
    for d in (M["producers"].get(who, {}).get("dials") or []):
        if d["number"] == number:
            if d.get("open_lead"):
                d["service_refused"] = "an open lead is being worked on this number"
                return False
            d["dropped"] = why
            return True
    return False
