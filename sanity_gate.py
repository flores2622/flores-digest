"""Cheap, deterministic checks against a day's own numbers so far.

HANDOFF_12 #6 ("nothing checks the report before it sends"), plus the checks
worth running at each business-hour checkpoint through the day, not just at
6:30 PM: a contact-rate swing since the last snapshot, a producer at zero
dials well into the day, a duplicate lead_id that should already have been
collapsed, a sub-5-second dial counted as a live contact. Deliberately makes
no assumption about how far apart two checks are -- the schedule these run
on isn't evenly spaced (HOURLY_RUNS.md's ten checkpoints run 30-75 minutes
apart) -- the rate-swing check only fires once BOTH snapshots clear a sample
floor, and the zero-dial check gates on the clock, not on elapsed time.

NOT a replacement for verify_finalize.py -- these are checks a run can make
for free from data it already has in hand (metrics_<day>.json,
board_payload's doc), not a full reconciliation against source data. They
only ever INFORM (a flag string to read), never block a send or change a
number.
"""
import datetime as dt

AZ = dt.timezone(dt.timedelta(hours=-7))

MIN_SAMPLE_DIALS = 15      # below this a contact-rate swing is just noise
RATE_SWING_POINTS = 5      # HANDOFF_12 #6's own figure
ZERO_DIAL_CUTOFF_HOUR = 11  # AZ local -- don't flag a slow start at 9:05am
MIN_LIVE_SECONDS = 5        # live_contact.MIN_CONTACT_SECONDS, duplicated
                            # here rather than imported so this module has
                            # zero dependency on the pipeline it is checking


def check(doc, prior=None, now=None):
    """doc is a board_payload.build()-shaped dict (this day, so far).
    prior is the last intraday snapshot's own doc, or None on the day's
    first check. Returns a list of short human-readable flag strings."""
    now = now or dt.datetime.now(AZ)
    flags = []

    totals = doc.get("totals") or {}
    dials, live = totals.get("dials") or 0, totals.get("live") or 0
    rate = round(100 * live / dials, 1) if dials else 0.0

    if prior:
        ptotals = prior.get("totals") or {}
        pdials = ptotals.get("dials") or 0
        if dials >= MIN_SAMPLE_DIALS and pdials >= MIN_SAMPLE_DIALS:
            prate = round(100 * (ptotals.get("live") or 0) / pdials, 1) if pdials else 0.0
            if abs(rate - prate) > RATE_SWING_POINTS:
                flags.append(f"contact rate moved {prate}% -> {rate}% "
                             f"since the last check ({pdials} -> {dials} dials)")

    if now.hour >= ZERO_DIAL_CUTOFF_HOUR:
        for p in doc.get("producers") or []:
            if (p.get("dials") or 0) == 0:
                flags.append(f"{p['name']}: 0 dials logged by "
                             f"{now.strftime('%-I:%M %p')}")

    seen_leads = {}
    for p in doc.get("producers") or []:
        for row in p.get("call_detail") or []:
            lid = row.get("lead_id")
            if lid is None:
                continue
            key = (p["name"], lid)
            if key in seen_leads:
                flags.append(f"{p['name']}: lead {lid} appears twice in "
                             f"Call Detail -- _one_row_per_lead should have "
                             f"collapsed this")
            seen_leads[key] = True
            secs = row.get("seconds")
            if secs is not None and secs < MIN_LIVE_SECONDS:
                flags.append(f"{p['name']}: {row.get('lead') or 'a lead'} "
                             f"counted live at {secs}s, under the "
                             f"{MIN_LIVE_SECONDS}s floor")

    return flags
