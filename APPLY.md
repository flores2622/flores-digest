# Flores digest — all changes through 2026-08-25

Twelve files. `template/report_template.html` is a second copy of the same
template; both are kept in sync. Drop them over the repo, or:

    git apply flores-fixes-2026-08-25.patch

Verify with `python3 daily.py --no-send`. Aug 24 rebuilds in ~20s once `data/`
is warm and lands at **90,237 bytes — 12,163 under the 102,400 clip limit**.
Nothing here sends mail.

**Watch the headroom.** The new Call Detail is ~35 KB against the old table's
22.6 KB, and audit section (e) adds a row per open task.

---

## New: renewals no longer count as new business

Dana Sanchez and Genaro Cortez were being counted as new-business live contacts
for Crystal. Both are full renewals — an **open Renewal SR with Crystal as the
CSR**, the linked lead sold or smart-cycled and assigned to another producer.

The rule is the service ticket, not lead status. `day_calls.build_context` now
indexes every OPEN service ticket by phone number and CSR, and `classify`
excludes a dial when a ticket matches the number AND the calling producer is the
CSR. Tickets are pulled once a day via the new `AgencyZoom.service_tickets_all`
and cached day-scoped (`data/az_service_tickets_<day>.json` — a bare filename
would have frozen the snapshot on day one and gone stale).

Why the CSR test matters, and why lead status was the wrong signal:

* **Lead status cannot express it.** 19 of Aug 24's 32 live contacts sat on a
  non-active lead, and most were smart-cycled BY the very call being reported —
  real new business. Excluding on `status != 0` would have gutted the day.
* **The existing service regex is too wide.** `SERVICE_BODY_RE` fired on the
  call text for Dana (right) but also Genaro *and* Angel Inda — and Angel Inda
  is Lorena's, so it is always new business.
* **The CSR test keeps it narrow and correct.** Wesley Knowlton has an open
  Missing Documents ticket under a different CSR, so Mike's call to him stays
  new business. Angel Inda has no ticket, so Lorena keeps him.

Blast radius: **2 of 32 live contacts, 5 of 190 dials**, all Crystal — which is
right, since she is the only producer doing service and renewals.

| | Before | After |
|---|---|---|
| Crystal calls / dials | 48 / 51 | 43 / 46 |
| Crystal live contacts | 7 | 5 |
| Crystal contact rate | 14.6% | 11.6% |
| Team calls | 190 | 185 |
| Team live / rate | 32 / 16.8% | 30 / 16.2% |

## Bugs found and fixed

**transcribe.py — the build hang.** `classify()` tested for a repeated greeting
with `r"(\W*(hello|hola|bueno|hi)\W*){2,}"`. The `\W*` on both sides of the
inner group makes every partition of the separators its own path, so a Whisper
repetition-loop transcript ("Hello? " x300) that does not fully match backtracks
exponentially and never returns. It stopped the Aug 24 build for 50 minutes on
one call. Now `r"(?:\W*(?:hello|hola|bueno|hi)){2,}\W*"` — same strings
accepted (verified equal on 66,666 generated cases), linear time.

**az_client.py — tasks counted twice.** `_paged()` starts at `page=0`.
`/leads/list` is 0-indexed and clean; `/tasks/list` is 1-indexed and clamps
page=0 to the first page, so the first 100 tasks came back twice — 253 records
for 153 real tasks. Team tasks due read 180 against a real 102; Sarahi 35.7%
against a real 40.0%. Deduped by `id` inside `_paged`; the loop still terminates
on the RAW fetched count, or a repeated first page would end it early and
silently drop the tail.

**util_panel.py — utilization frozen since Aug 12.** The percentage and bar were
written with `str.replace()` keyed on the EMPTY placeholder forms, which only
Coral's and Sarahi's cards carry. The other four ship from the template with Aug
12 values baked in, so the replace matched nothing and left the stale number
while the code below it refreshed the times beside it. Lorena read 84.9% every
day for twelve days (real Aug 24: 89.0%); Crystal read 89.5% against a real
81.3%. Now rewrites whatever is present and RAISES if the span is gone.

**panels.py — quote origin read as destination.** The "was this quoted on the
call" test split `"A to B"` and checked every segment, so the ORIGIN counted:
"Quotes Presented to Smart-Cycle" is a move OUT of the quote stage. Harry
Anderson, Angel Inda and Juan Avila were filed as quoted-on-this-call when all
three were quoted days earlier and this call was the follow-up that lost them.
Destination only now.

**daily.py — only the first note was shown.** `evidence()` has always collected
every note the producer wrote on the lead that day, but Call Detail printed
`written[0]` alone. Five of Aug 24's 32 contacts had two or three notes. Now all
of them, de-duplicated, capped at 480 chars.

**report_template.html — the row rail was invisible.** `.cdi td{border:none}`
and `.eN{border-left:...}` are both specificity (0,0,1,1); the reset came later
in source order and won. The rail rules are now `.cdt td.eN` — (0,0,2,1) — so
they cannot tie.

## Requested changes

**Leaderboard 5-4-3-2-1, ties take the LOWEST place** (reverses the 08-24 rule).
Three-way tie for first = 3 pts each, then 2, 1. Two-way tie for first = 4 pts
each, then 3, 2, 1. Zero activity still scores 0 and still consumes its place.

**Call Detail rebuilt as option D** — a section per rep opening with a stacked
bar of that rep's outcome mix, calls full width beneath, legend at the TOP,
outcome chip beside the talk time, coloured rail down the left of every row.

**Seven categories on five hues.** The quote state splits in two: presented ON
the call versus a follow-up on one already out. The follow-up pair reuses its
parent hue at ~45% over white with a dashed chip border and dashed rail.

| Category | Colour | Chip |
|---|---|---|
| Sold on the call | green #008300 | solid |
| Quoted, no action | blue #2a78d6 | solid |
| Quote follow up, no action yet | light blue #9fc2ed | dashed |
| Quoted on this call, Lost/Dead | red #e34948 | solid |
| Quote follow up, Lost/Dead | light red #f2adad | dashed |
| Lost/Dead, never quoted | highlighter yellow #f0e800 | solid |
| Contacted, No Action | orange-yellow #eda100 | solid |

The old five pastels failed measurably: dead-with-quote #FCA5A5 against
dead-no-quote #FDBA74 was ΔE 9.3 for normal vision against a floor of 15, and
all five sat under 3:1 contrast. The set above clears the normal-vision floor on
every pair (worst 17.7, the two yellows); #f0e800 sits outside the validator's
mark-lightness band, which is what "highlighter yellow" means, and both yellow
chips carry dark ink.

**Quote state from TASK TITLES** — "Quote follow #7", "Quoted Yesterday 1st
Follow Up call" against "Never quoted lead- Day 4 NEW", "Send quote to
prospect". quoteDate is not used: a quote can be started one day and presented
another. **QNC titles count as follow-ups** — that pipeline is where leads land
when they did not close the last time they were presented, so a quote has
already been out. Checked before the pending pattern, whose "Lead Day N" would
otherwise match. Falls back to stage history, which needs a quote-stage move
inside 30 days; unbounded, it made follow-ups of leads last quoted in 2022.

**"Lost", not "Dead"**, unless the outcome actually says dead.

**Audit:** new section (e) for tasks still open at end of day; every table reads
rep › lead › task › category data.

**Layout:** Team Leaderboard full width at the top; Call Outcome Breakdown back
to a normal-width panel in the column.
