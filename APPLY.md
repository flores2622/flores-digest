# Flores digest — 2026-08-25, revision 2

**You already pushed revision 1, so DROP THE FILES IN, don't apply the patch.**
The twelve `.py`/`.html` files here are complete and current — copy them over the
repo (note `template/report_template.html` is a second copy of the same
template; both are kept in sync) and commit.

`cumulative-from-original.patch` is a diff against the ORIGINAL pre-Aug-25
clone, not against what you just pushed, so `git apply` will conflict. It is
included for reading, not for applying.

Verify with:

    python3 daily.py --day 2026-08-24 --no-send

**Pass `--day` for any rebuild of a past day.** With no argument the build takes
today's Arizona date, which after midnight is a day with no cached data and the
run dies on a missing transcripts file.

Aug 24 lands at **90,156 bytes — 12,244 under the 102,400 clip limit**. Nothing
here sends mail.

---

## What changed in revision 2

**Call Detail chip and rail styling, as specified.**

| Category | Chip | Row rail |
|---|---|---|
| Sold on the call | solid green #008300 | solid |
| Quoted, no action | **solid light blue #9fc2ed** | solid light blue |
| Quote follow up, no action yet | **dotted light blue border**, white ground | **dotted** light blue |
| Quoted on this call, Lost/Dead | **solid red #e34948** | solid red |
| Quote follow up, Lost/Dead | **dotted red border**, white ground | **dotted** red |
| Lost/Dead, never quoted | solid highlighter yellow #f0e800 | solid |
| Contacted, No Action | solid orange-yellow #eda100 | solid |

Solid means it happened on this call; dotted means a follow-up on a quote
already out. The rail carries the same solid/dotted distinction as the chip, so
the two read as one signal.

One thing the spec could not cover: a 9px mix-bar segment cannot be a bordered
box — it rendered as a white gap in the bar. The bar and the key swatch beside
it take a solid tint one step paler than the on-this-call sibling (#d3e4f7 and
#f2adad), so the bar still reads as a bar while the chip keeps its dotted
outline.

**Bug found while doing it.** The row rail was invisible in revision 1:
`.cdi td{border:none}` and `.eN{border-left:...}` are both specificity
(0,0,1,1), and the reset came later in source order, so it won. The rail rules
are now `.cdt td.eN` — (0,0,2,1) — so they cannot tie.

---

## Everything from revision 1 (still in place)

### Renewals no longer count as new business

Dana Sanchez and Genaro Cortez were counted as new-business live contacts for
Crystal. Both are full renewals — an **open Renewal SR with Crystal as the
CSR**, the linked lead sold or smart-cycled and assigned to another producer.
Service tickets were never being read at all: `service_tickets()` existed in the
client and nothing called it.

`day_calls.build_context` now indexes every OPEN service ticket by phone and
CSR; `classify` excludes a dial when a ticket matches the number AND the calling
producer is the CSR. Pulled once a day via the new
`AgencyZoom.service_tickets_all`, cached day-scoped
(`data/az_service_tickets_<day>.json` — a bare filename would have frozen the
snapshot on day one).

The CSR test is what keeps it honest: Wesley Knowlton has an open Missing
Documents ticket under a different CSR, so Mike's call to him stays new
business; Angel Inda has no ticket, so Lorena keeps him. Lead status could not
express this — 19 of Aug 24's 32 contacts sat on a non-active lead and most were
smart-cycled BY the call being reported. And `SERVICE_BODY_RE` on the call text
fires on Dana, Genaro *and* Angel Inda, costing a real contact to catch two.

Blast radius: 2 of 32 live contacts, 5 of 190 dials, all Crystal.

| | Before | After |
|---|---|---|
| Crystal calls / dials | 48 / 51 | 43 / 46 |
| Crystal live / rate | 7 / 14.6% | 5 / 11.6% |
| Team live / rate | 32 / 16.8% | 30 / 16.2% |

### Bugs

**transcribe.py — the build hang.** `classify()` tested for a repeated greeting
with `r"(\W*(hello|hola|bueno|hi)\W*){2,}"`. The `\W*` on both sides of the inner
group makes every partition of the separators its own path, so a Whisper
repetition-loop transcript ("Hello? " x300) that does not fully match backtracks
exponentially and never returns. It stopped the Aug 24 build for 50 minutes on
one call. Now `r"(?:\W*(?:hello|hola|bueno|hi)){2,}\W*"` — same strings accepted
(verified equal on 66,666 generated cases), linear time.

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

**daily.py — only the first note was shown.** `evidence()` has always collected
every note the producer wrote on the lead that day, but Call Detail printed
`written[0]` alone. Five of Aug 24's 32 contacts had two or three notes. Now all
of them, de-duplicated, capped at 480 chars.

### Requested changes

**Leaderboard 5-4-3-2-1, ties take the LOWEST place.** Three-way tie for first =
3 pts each, then 2, 1. Two-way tie for first = 4 pts each, then 3, 2, 1. Zero
activity still scores 0 and still consumes its place.

**Call Detail rebuilt as option D** — a section per rep opening with a stacked
bar of that rep's outcome mix, calls full width beneath, legend at the TOP,
outcome chip beside the talk time, coloured rail down the left of every row.

**Quote state from TASK TITLES** — "Quote follow #7", "Quoted Yesterday 1st
Follow Up call" against "Never quoted lead- Day 4 NEW", "Send quote to
prospect". quoteDate is not used: a quote can be started one day and presented
another. **QNC titles count as follow-ups** — that pipeline is where leads land
when they did not close the last time they were presented. Checked before the
pending pattern, whose "Lead Day N" would otherwise match. Falls back to stage
history, which needs a quote-stage move inside 30 days; unbounded, it made
follow-ups of leads last quoted in 2022.

**"Lost", not "Dead"**, unless the outcome actually says dead.

**Audit:** new section (e) for tasks still open at end of day; every table reads
rep › lead › task › category data.

**Layout:** Team Leaderboard full width at the top; Call Outcome Breakdown back
to a normal-width panel in the column.
