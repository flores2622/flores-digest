# Flores Insurance Agency — daily sales digest

Standing rules for anyone (human or Claude) working on this repo. These were
each learned the hard way from a wrong number in a sent report. Do not
re-litigate them from first principles — if one looks wrong, check the handoff
that introduced it first.

## What this builds

`python3 daily.py` reports ONE Arizona day and emails two audiences at 6:30 PM
AZ: **ops** (frank@, francisco@, veronica@, amanda@) get the digest plus the
Call Detail & Task Completion Audit; **staff** (the producers plus debbie@) get
the Sales Digest only. `--day YYYY-MM-DD` rebuilds a past day, `--audience
ops|staff|both`, `--no-send` builds without emailing.

Everything caches under `data/`, so a re-run resumes rather than restarting.

## The money rules

- **A policy whose lead source is BOB is not a sale.** Already handled.
- **A renewal is not new business.** Neither is servicing, a payment, a claim,
  or chasing paperwork on a policy already sold.
- **Selling a product the household does not have yet IS new business**, even to
  a customer of twenty years. Cross-sells count.
- **Premium Sold comes from AgencyZoom policies** by `agentId` + `soldDate`, not
  from the call log. Policy records carry no name, phone, customerId or leadId —
  only `leadSourceId`, which is the marketing source and is shared by thousands
  of policies. The join from a dialled number to a sale is the LEAD record:
  `status == 2` means sold, and all 1,517 status-2 leads carry a `soldDate`.

## The contact-rate rules

- **Never "fix" a low contact rate.** Most dials genuinely reach voicemail. On
  2026-08-13 it was 115 of 135. That is the real number.
- **Contact rate is outbound-only.** A dial is an attempt the producer made. A
  call back changes the VERDICT on a dial already made, so it lands inside the
  numerator by turning that dial live. A cold call-in had no dial and sits
  outside the rate entirely.
- **Talk time counts every conversation**, inbound included.
- **Notes win over the recording** (Frank, 2026-08-18). A producer writing "no
  answer" outranks a 12-second transcript that sounds live. Duration is the
  last resort and is labelled as such.
- **TRAQ auto-summaries are not producer notes.** They are machine output
  written on every call including voicemails.

## Identity and attribution

- **Producers**: Crystal Mango, Lorena Gonzalez, Mike Olvera, Coral Barwick,
  Sarahi Chin. Coral and Sarahi are full producers as of 2026-08-24 — the
  2026-08-28 review date is CLOSED. Sarahi's Insightful licence was assigned
  2026-08-25 and her utilization is live like everyone else's; `digest_config.
  NO_INSIGHTFUL_LICENCE` is empty and the panel branch that printed "no
  Insightful licence assigned" no longer fires for anyone.
- **Not producers**: Debbie Aguilera is the front desk and handles ~90% of
  inbound, transferring to whoever the call is for. Amanda Torricellas is
  operations manager, sells, and is deliberately not tracked.
- **Everything is keyed by (producer, number), never number alone.** Two
  producers work the same number on the same day often enough that keying on
  the number hands one of them the other's call.
- **Duplicate lead records are pervasive.** Read notes across ALL records on a
  number; prefer the one sold today when picking which represents the call.

## Phone numbers

`az_corpus.e164` keys on the **last ten digits**. AgencyZoom stores every number
as ten digits with no country code, so a Mexican number arrives from RingCentral
as `+526535380676` and from AgencyZoom as `(653) 538-0676`. Anything stricter
silently drops real customers.

## Rebuilding a past day

**Never re-fetch `data/az_service_tickets_<day>.json` for a day already built.**
Open tickets close overnight, so a rebuild disagrees with the original run.
The service-ticket test is point-in-time: a ticket counts only if it was created
on or before the day and was not already closed before it.

## How long the nightly run takes

**Expect about 85 minutes, not the 30-40 the scheduled-task prompt claims.**
Measured 2026-09-01: fired 01:45:34 UTC, finished 03:09:35 — 1h24m. The prompt's
figure is stale and this file overrides it.

Roughly 30 of those minutes are nothing but downloading recordings. RingCentral's
media endpoint allows 10 requests per rolling 60s, the downloader paces at 8/min,
and the agency averages 238 recordings a day (peak 298). Steady progress of about
20 recordings every 2.5 minutes is normal.

A stall still means the log has not advanced in ~5 minutes, or repeated "rate
limited" lines. Judge it on progress, not on total elapsed time — an 80-minute
run is healthy.

`HOURLY_RUNS.md` is the plan to move that download-and-transcribe work into
hourly runs so the evening build finds it already cached. Not built yet.

## Service tickets — the corpus changed on 2026-09-01

`service_tickets_all()` used to pass `status: "all"`, which silently returned
**open tickets only**. It now passes `status: [0, 1]` and returns open plus
closed. Because 359 of 361 closed tickets carry no `completeDate`,
`inbound.py` and `day_calls.py` fall back to `lastActivityDate` as the close
date, and only when `status == 1`.

**Expect the service-screening numbers to move slightly on the first build after
this, and do NOT report it as a data problem.** About 50 more tickets are visible
per day. Modelled against 2026-08-28 it would have screened **two** additional
answered inbound calls as service work, so contact rates shift by a point or
two, downward, for whoever took those calls. That shift is the bug being
corrected.
## Coach AI

- **The call score is NOT a 0-100 percentage.** Frank, 2026-09-01: a *perfect
  call* scores **750-800**. A producer averaging 224 is near 29% of a perfect
  call, not "over the cap". Nothing above 100 is evidence of a bug -- do not
  describe it as one, and do not "correct" a score for being over 100.
  Transcribe what the email prints, always, but for the ordinary reason that it
  is their measure and not ours.
- On that scale every figure the team currently posts is LOW: 2026-08-31 ran
  Lorena 224, Mike 148, Coral 122, Crystal 90, Sarahi 11, team 90. The team
  average is roughly 12% of a perfect call. Low scores are the finding, not a
  data fault.
- **`COACH_BAR_RANGES` is team-relative, not a share of the scale.** The Avg
  Call Score bar spans (38, 251) -- per-producer extremes over the trailing
  window -- because scaling 0-800 makes every bar a sliver. The side effect is
  that 224 renders nearly full when it is under a third of a perfect call. If
  the bar is ever relabelled or re-anchored, that is the reason.
.- **Voicemails are scored as calls, and that is the whole story of the low
  numbers.** Confirmed 2026-09-01 against TRAQ's own per-call scores, read off
  three of Sarahi's calls where TRAQ itself labels the call type:
    voicemail -> score 3,   sentiment 0
    voicemail -> score 3,   sentiment 0
    live call -> score 292, sentiment 48
  A voicemail scores ~3 against a real conversation's ~292 (~100x), and
  sentiment on a voicemail is a flat 0. Avg Call Score and Avg Sentiment are
  therefore answer-rate-weighted, NOT call-quality measures: a producer who
  reaches more voicemails posts a lower average regardless of how they talk.
  Sarahi's 25 voicemails of 35 rows are why she sits at 11. This is not a fault
  to fix in our pipeline -- it is how TRAQ scores -- but it means these two
  figures cannot rank producers with different answer rates against each other.
- The TRAQ note on every call carries its call id (app.traq.ai/call/0/<id>).
  When the TRAQ API key lands (parked to 2026-09-15, digest_config.
  TRAQ_REVISIT_DATE) those ids join TRAQ's per-call scores onto our own
  live/voicemail classification directly, which removes all of the inference
  above.
- The per-user rows ARE internally consistent: they are call-weighted averages
  over Coach's own Total Calls column and roll up exactly to the team figure
  (2026-08-31: 12,835/142 = 90.4 against a stated 90; role play 399/5 = 79.8
  against 80). The aggregation is not in question.
- **Total Calls includes voicemails**, and Coach's coverage of a producer's day
  varies wildly -- 2026-08-31 it saw 9 of Lorena's 52 dials but 35 of Sarahi's
  40. Cross-producer comparison of these averages is unsafe for that reason
  alone, independent of the scale.

## Cost

Transcription is local and free. **The Anthropic API read in `call_summary.py`
is the only paid step** — roughly one call per live contact per day. Changing
the prompt means deleting `data/callsum_<day>.json`, which re-reads everything.
Do not do that casually, and never in a loop while iterating on wording.

`python3 verify_finalize.py` reconciles all six headline figures against source
data and costs nothing. Run it after touching `daily.py`, `day_calls.py` or
`finalize.py`.

## Never

- Commit anything under `secrets/`, `data/` or `out/` (all gitignored).
- Echo credentials into a log, a report or a chat message.
- Re-send a day that has already gone out without saying so explicitly.
