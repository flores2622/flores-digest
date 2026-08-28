# HANDOFF 10 — 2026-08-27

Frank's review of the 2026-08-25 rebuild, worked through in one session.
**Nothing was re-emailed.** The 08-25 digest that reached ops at 22:56 MST on
08-26 is the build described in HANDOFF 9 plus the Call Detail panel; every
figure below is what the NEXT run will produce.

The day moved **210 dials / 33 live / 15.7%** to **208 / 31 / 14.9%**.
Sales are unchanged at **$4,370** and always were.

---

## 1. Two producers were being handed each other's calls

Every transcript cache was keyed on the dialled number alone. Sarahi reached
Juan Rojas at 9:36 (77s, live); Mike's own 4:15pm dial to him went to voicemail.
Mike's row printed Sarahi's live verdict, her transcript and her summary.

`bynum`, `txt`, `all_txt`, `_audio_legs` and the summary cache are now keyed on
**(producer, number)**. Separately, notes are now read across every duplicate
lead record on a number — which is what actually removed Mike's row, since his
own no-contact note outranks any recording.

## 2. The report never looked at inbound calls

~90 minutes of producer conversation a day was invisible, including Abner
Castanon's 19m54s call back to Lorena and Rasha Hassoun's 87 seconds to Sarahi —
which is why Rasha read as a voicemail when she had plainly spoken to Sarahi.

New `inbound.py`. Two attribution routes: a producer's **personal DID** (a
number exactly one person dials out from — derived, so the shared main line
excludes itself), and a **ring-group transfer**, where Debbie's hold is a
FindMe leg and the producer's pickup is a Park Location leg. Talk time is the
producer's leg, never the whole call.

On 08-25: 14 of 38 answered inbound reached a producer — 9 call backs, 5 cold
call-ins. Screened against the same record tests as outbound BEFORE any audio is
fetched, leaving 9 to transcribe.

A **same-day** call back merges into the dial it answers: combined time, and a
summary written from both recordings when both were live. Anything else — a cold
call-in, or a call back to an earlier day's dial — becomes its own inbound line
on the day it happened, because that earlier day's report has already gone out.

### RingCentral loses the transferred half

Automatic recording stops at the park. Abner's call is 1,194 seconds of call and
**67 seconds of audio**. Outbound is unaffected (98-99% of logged duration).
Every producer extension already has `callDirection: All`, so this is not a
settings problem — confirmed against the account. Affected rows say "recording
covers the opening only" under the summary. Talk time is unaffected; it comes
from the call log.

## 3. Service and renewal work was leaking in, and new business was leaking out

- Service tickets are fetched with `status: "all"` (the old fetch returned 321
  of 338 open) and tested **point in time** — created on or before the day, not
  already closed before it. A rebuild no longer reaches into later data.
- New exclusion replacing the converted-household rule: **a household that has
  bought, with no open lead created since the sale**. Never fires on the day of
  the sale. An open lead created after the sale — AgencyZoom names them "Life
  Cross Sell", "Winback" — means an additional-product attempt and stays in.
  4 of 212 dials. A bare "sold household" test would have taken 34.
- The call read can now flag a service call the records missed. **Guarded**: it
  is refused while an OPEN lead sits on the number. Coral chasing Carlos Cruz's
  *competitor's* declarations page read as service and deleted a live contact.
  "Has this household ever bought" cannot carry that test — Carlos and Crystal's
  Ruben Serrano are both converted households with no soldDate on any lead. The
  open lead is what separates them.

## 4. Totals are computed after the read, not during

`build_metrics` keeps every counted dial on `M[who]["dials"]` instead of
collapsing to six numbers on the spot. New `finalize.py` totals them, is
idempotent, and runs twice per build. Nothing between the dial classification
and the read could previously drop a dial and still leave an honest call volume
behind — the raw material was already gone.

`verify_finalize.py` reconciles all six figures against source data. Free.

## 5. Outcome and objection changes

- **"Sold on the call"** now honours the lead's own sold status ahead of stage
  moves. Coral's Hugo Bojorquez bound two policies ($1,020 + $731) while the
  duplicate lead carrying the moves ended "Dead, Loss Reason: Duplicate Lead".
- **A price spoken aloud counts as a quote presented** — tightened to OUR rated
  price for a policy being proposed, not the prospect's current premium, a
  competitor's quote, ballpark pricing, or a renewal figure.
- **`overcome` gained "advanced"** — addressed, not resolved, but the call kept
  selling. Fires on 6 of 27 objections. The parser whitelist was silently
  coercing it to "unclear", which is why it looked like the model refused it.
- **An objection must be the prospect withholding something.** Background
  commentary goes in the summary. 34 objections became 27.
- Two new categories: **"Contacted, okay to quote, no action"** (orange
  candy-cane, dashed rail) and **"Called back, no conversation"** (grey
  candy-cane, dashed rail).
- Objection chips moved from saturated fills to pale tints so the outcome chip
  wins the row, and the two reds now differ: **solid = never engaged**,
  **candy-cane = engaged and lost**.
- Call backs show as a **candy-cane slice inside their existing segment** in the
  Call Outcome Breakdown, so segments still sum to the day's dials and Live
  Contact means the same thing there as in the contact-rate panel.

## 6. Two render bugs

- `.e8`/`.b8` lacked the `.cdt td` / `.cdb td` prefixes the other categories
  use, so the eighth category lost on specificity and **call-in rows rendered
  with no left rail at all**.
- One tag per row at most. "Opening only" moved to the source line under the
  summary; a merged call back's split moved into the time cell.

---

## Open, not built

- **Cold call-ins are not in contact rate** and should not be — but nothing yet
  reports them as their own figure. They currently appear only as Call Detail
  rows and in talk time.
- **The palette is at nine categories on six hues.** Adding more will not fit.
  The discussed fix is colour-by-family (won / in play / lost / no traction)
  with the state carried in the chip text, which scales indefinitely. Frank has
  seen it rendered and deferred it.
- **`quote_presented` and `service_call` prompt wording** is unproven against a
  fresh paid read — the record-based guard is the safety net either way.
- Overflow to PDF now fires **every** day (body ~110KB against Gmail's 102,400
  limit), where it used to be occasional.
