# Addendum to HANDOFF_5 — pipeline rebuild, 2026-08-14

HANDOFF_5 still applies. This records what was built after it, so the next
session starts from working code rather than a spec.

## Status: Aug 13 data is COMPLETE. The renderer is HALF DONE. Nothing was sent.

`data/metrics_2026-08-13.json` holds every figure for the day. Two of eight
panels have been rendered into `out/step2.html`. **The rest of that file still
shows Aug 12 figures under an Aug 13 heading — it must not be sent as-is.**

## Aug 13 figures (verified)

| | Crystal | Lorena | Mike | Team |
|---|---|---|---|---|
| Call Volume | 39 | 40 | 55 | 134 |
| Live contacts | 9 | 5 | 13 | 27 |
| Contact Rate | 23.1% | 12.5% | 23.6% | 20.1% |
| Avg Talk Time | 1m45s | 1m35s | 1m11s | — |
| Households Quoted | 0 | 0 | 4 | 4 |
| Premium Quoted | $0 | $0 | $7,025 | $7,025 |
| Premium Sold | $2,363 | $0 | $0 | $2,363 |
| Task Completion | 11/11 | 41/44 | 82/82 | 134/137 (97.8%) |
| Utilization | 82.1% | 74.7% | 87.9% | 83.4% weighted |
| Coach AI score / sentiment | 66 / 16 | 155 / 33 | 50 / 14 | 75 / 18 |

Recontact: 49 at risk, 27 lost, 0 won. Role play: Coral only (3 sessions, 59),
so all three producers take the zero-activity override in that category.
Speed to dial: Crystal median 247s (n=5), Lorena 23s (n=5), Mike no internet leads.

## What was built

| File | Does |
|---|---|
| `az_corpus.py` | Pulls all 11,427 leads, indexes 8,314 phone numbers to E.164 |
| `day_calls.py` | Joins RingCentral dials to leads; new-business classification; caches lead notes |
| `live_contact.py` | Live-contact and outcome-bucket classification from notes |
| `recontact.py` | At risk / lost / won, stage history, calls between |
| `render_report.py` | Sales Funnel generator; `swap_panel` for panel replacement |
| `link_repair.py` | Repairs quoted-printable-mangled AgencyZoom lead links |
| `attachments.py` | HTML→PDF for the two companions; `qp_safe` for the body |

Cached under `data/`: lead corpus, customer corpus (4,081), all policies
(12,078), stage-id map, call logs, and 528 lead note sets.

## Rules established this session

**LIVE CONTACT.** A connected call counts (Frank, 2026-08-14). Live if the
producer wrote an outcome note, or — absent an explicit no-contact note — the
call carried **60+ seconds** of connected audio, taken as the longer of
AgencyZoom's CALL-note duration and the RingCentral leg. The 60s floor is set
from the data: explicit no-answer/voicemail notes cluster below a minute
(5 under 15s, 5 at 15–29s, 4 at 30–59s, 1 at 60–119s, none above 120s). An
explicit no-contact note always overrides duration. Rows qualifying on duration
alone are labelled "duration only".

**CALL VOLUME.** Distinct numbers dialled, new business only. Excluded when the
household has a service/renewal task due that day for the same producer, or the
number matches only a customer record, or matches no AgencyZoom record.

**PREMIUM QUOTED.** Union of leads with a `quoteDate` that day and leads with a
MOVE_STAGE into a quoted stage that day; premium summed from
`/leads/{id}/quotes`. This reproduced Aug 12's published $11,883 exactly.

**COACH AI.** Confirmed again: the email titled one day ahead describes the
Arizona day. The "Aug 13"-titled email reports 81 calls / score 90 / sentiment
16, matching the Aug 12 report's notes exactly. Per-user rows are in the HTML
body only — the plaintext part has an empty table.

**AgencyZoom endpoints found:** `/v1/api/customers/list` (4,081 customers with
phones — needed for the service/renewal exclusion) and `/v1/api/pipelines-and-stages`
for the stage-id map. `status` on a lead: 0 = active with a real stage,
3 and 5 = closed (stage id reads 0).

## What remains

1. Render the six stale panels into `out/step2.html`: Task Completion Rate,
   Recontact Struggle, Team Leaderboard, Call Outcome Breakdown, Speed to Dial,
   Coaching & Call Quality — plus the whole Call Detail & Task Completion Audit
   section. `render_report.swap_panel` + `build_funnel` show the pattern; extract
   each panel's row markup at runtime rather than re-authoring it.
2. Regenerate both attachments for the day (`attachments.py`), as PDF.
3. Send: ops = frank@, amanda@, francisco@, veronica@; staff = debbie@, coral@,
   sarahi@, crystal@, lorena@, mike@. **Staff gets the Sales Digest only** — the
   Call Detail & Task Completion Audit section is ops-only (HANDOFF_5 s1). Frank
   added Coral and Sarahi to the staff list on 2026-08-14.
4. Then the two scheduled tasks: ops 6:30 PM AZ (01:30 UTC next day), staff
   8:00 AM AZ (15:00 UTC).

## Guardrails worth keeping

`util_panel.assert_div_balance` compares open/close `<div>` counts before and
after every patch and refuses to write on a mismatch. It exists because one
stray `</div>` per card closed the panel and its column early and destroyed
every panel below it — Coach AI first. Run it after every panel swap.
