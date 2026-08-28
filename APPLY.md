# Flores digest — all changes through 2026-08-27

Fifteen files: twelve changed, three new (`inbound.py`, `finalize.py`,
`verify_finalize.py`), plus `CLAUDE.md` and `HANDOFF_10.md`. Apply with:

    git apply flores-fixes-2026-08-27.patch

Verify with `python3 daily.py --no-send --day 2026-08-25`, then
`python3 verify_finalize.py` — it reconciles all six headline figures against
source data and costs nothing. Nothing here sends mail.

**2026-08-25 moves from 210 dials / 33 live / 15.7% to 208 / 31 / 14.9%.**
Sales are unchanged at $4,370 and always were. Full reasoning in HANDOFF_10.md.

**Watch the headroom — there isn't any.** The body now runs ~110 KB against the
102,400 clip limit, so `overflow.py` fires every day and the ops email always
carries the Task Completion Audit as a PDF. That is expected. Only "REFUSING TO
SEND" is a problem.

---

## Two producers were being handed each other's calls

Every transcript cache was keyed on the dialled number alone. Sarahi reached
Juan Rojas at 9:36 (77s, live); Mike's own 4:15pm dial went to voicemail. Mike's
row printed Sarahi's verdict, transcript and summary.

`bynum`, `txt`, `all_txt`, `_audio_legs` and the summary cache are now keyed on
**(producer, number)**. Notes are also read across every duplicate lead record
on a number, which is what actually removed Mike's row — his own no-contact note
outranks any recording.

## Inbound calls now count

New `inbound.py`. ~90 minutes of producer conversation a day was invisible,
including Abner Castanon's 19m54s call back to Lorena and Rasha Hassoun's 87
seconds to Sarahi — which is why Rasha read as a voicemail.

Two attribution routes: a producer's **personal DID** (a number exactly one
person dials out from, derived so the shared main line excludes itself), and a
**ring-group transfer**, where Debbie's hold is a FindMe leg and the producer's
pickup is a Park Location leg. Talk time is the producer's leg, never the whole
call — Debbie held one of Crystal's calls for 117 of its 562 seconds.

Screened against the same record tests as outbound BEFORE any audio is fetched.
A **same-day** call back merges into the dial it answers; anything else becomes
its own inbound line on the day it happened.

RingCentral stops recording at the park, so a transferred call keeps only the
front-desk opening — Abner's call is 1,194 seconds with 67 seconds of audio.
Those rows say "recording covers the opening only". Talk time is unaffected.
Every producer extension already has `callDirection: All`; this is not a
settings problem.

## Service and renewal work in, new business out

* Service tickets fetched with `status: "all"` — the old fetch returned 321 of
  338 open — and tested **point in time**: created on or before the day, not
  already closed before it. Rebuilds no longer reach into later data.
* New exclusion: **a household that has bought, with no open lead created since
  the sale**. Never fires on the day of the sale. An open lead created after it
  ("Life Cross Sell", "Winback") means an additional-product attempt and stays
  in. 4 of 212 dials — a bare "sold household" test would have taken 34.
* The call read can flag a service call the records missed, but is **refused
  while an open lead sits on the number**. Coral chasing Carlos Cruz's
  *competitor's* dec page read as service and deleted a live contact.

## Totals are computed after the read

`build_metrics` keeps every counted dial on `M[who]["dials"]` instead of
collapsing to six numbers on the spot; new `finalize.py` totals them and is
idempotent. Nothing downstream could previously drop a dial and still leave an
honest call volume behind.

## Outcomes and objections

* "Sold on the call" honours the lead's own sold status ahead of stage moves —
  Hugo Bojorquez bound $1,020 + $731 while the duplicate lead carrying the moves
  ended "Dead, Duplicate Lead".
* A price spoken aloud counts as a quote presented — our rated price only, not
  the prospect's current premium or a competitor's quote.
* `overcome` gained **"advanced"**; the parser whitelist was silently coercing
  it to "unclear".
* An objection must be the prospect withholding something. 34 became 27.
* Two new categories: **"Contacted, okay to quote, no action"** (orange
  candy-cane, dashed rail) and **"Called back, no conversation"** (grey
  candy-cane, dashed rail).
* Objection chips are pale tints so the outcome chip wins the row, and the two
  reds differ: solid = never engaged, candy-cane = engaged and lost.
* Call backs stripe **inside** their existing segment in the Call Outcome
  Breakdown, so segments still sum to the day's dials.

## Two render bugs

* `.e8`/`.b8` lacked the `.cdt td` / `.cdb td` prefixes, so the eighth category
  lost on specificity and **call-in rows rendered with no left rail**.
* One tag per row at most; provenance moved under the summary, the merged call
  back's split moved into the time cell.

## Phone numbers

`az_corpus.e164` keys on the **last ten digits**. AgencyZoom stores ten digits
with no country code, so Sarahi's 5m41s call with Leticia Urias arrived as
`+526535380676`, matched nothing, and vanished.
