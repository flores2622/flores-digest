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
  2026-08-28 review date is CLOSED. Sarahi has no Insightful licence, so her
  utilization card says so; every other figure for her is live.
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
