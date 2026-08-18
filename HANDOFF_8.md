# HANDOFF 8 — 2026-08-18

Everything below came out of one review session with Frank, the evening of
2026-08-17 into the early hours of 08-18, going row by row through that day's
report. Nine files changed, one added. **Nothing was emailed** — the 08-17
digest that reached the ops and staff lists at 19:21 was the *old* build, and
its headline contact rate (21.2%) is wrong. See §2.

Ordered by how much damage each was doing.

---

## 1. The Task Completion Audit was static HTML — stale since 08-12

**Severity: highest.** Sections (a)–(d) of the ops report were hardcoded in
`report_template.html`. Only the date label was substituted, so every ops email
from 2026-08-12 onward carried the *same two exceptions* and the *same thirteen
cancellations*. Any real exception after 08-12 went unreported for five days.

Evidence: 08-17's output named Terucko Couch and Higinio Vigil, neither of whom
appears anywhere in 08-17's task data, and claimed "among the 167 tasks" when
08-17 had 133 producer tasks due.

**Fix:** new module `task_audit.py`, generated per day, wired through
`daily.py` → `metrics_<day>.json["task_audit"]` → `panels.task_audit_tables`.

What each section can honestly claim:

| | basis |
|---|---|
| (a) completed on a call not in the call log | producer's comment claims a call, record has a phone, RingCentral shows no dial |
| (b) closed after the due date | `completeDate > dueDate` |
| (c) due date changed | **cannot be proven.** AgencyZoom exposes `modifyDate`/`createDate` but not field-level history. Reports tasks modified on a later *day* than created — reschedule-shaped — and says so in a footnote |
| (d) cancelled rather than completed | `status == 2` |

(c) previously printed "No evidence of a due-date edit", which was a false
all-clear for a check that had never run.

08-17 actual: 133 counted tasks → (a) 0, (b) 0, (c) 5, (d) 3. The zero in (a)
is earned: 94 completed tasks claim a call, 93 match a real dial, 1 explains
itself ("call was restricted").

---

## 2. Live contact was badly over-counted — 21.2% → real figure ~6%

Six independent defects, all inflating. Corrected 08-17 figures:

| | volume | live | rate | was |
|---|---|---|---|---|
| Crystal | 38 | 3 | 7.9% | 20.0% |
| Lorena | 53 | 1 | 1.9% | 22.6% |
| Mike | 44 | 4 | 9.1% | 20.5% |
| **Team** | **135** | **8** | **5.9%** | **21.2%** |

### 2a. TASK notes were invisible to the entire pipeline

The single biggest cause. **All 1,724 TASK notes** are stamped exactly
`17:00:00` — 5pm Arizona, i.e. midnight UTC of the day the task is *due*. So
08-17's task notes carry a `createDate` of **08-16** and the day filter dropped
every one. `createdBy` is also null on all of them; authorship lives in the body
as `Completed by <Name>`.

These are where producers actually write outcomes — "~Called to offer quote, no
answer", "Called, left VM", "CALL DROPPED AFTER AI TRANSFERRED ME". The
live-contact logic had never seen a single one.

`live_contact.task_note_day()` shifts the date; `task_note_parts()` extracts the
author and strips AgencyZoom's canned instruction text. Task notes are trusted
for **no-contact only** — what survives stripping is often still boilerplate,
and treating that as proof of a conversation is how this started.

### 2b. Evidence order: notes now beat the recording

Was: recording → notes → duration. The recording is a 30-second window of a
call that may run minutes, in a language the model half-reads, and it was
overriding producers who had explicitly written "no answer". Denise Milleville:
12 seconds of "Hi, this is Denise." beat Lorena's own "~Called to offer new
quote, no answer."

Now: **negative note → positive note → recording → duration.**

Checked for over-correction: exactly 5 rows have a live recording against a
no-contact note, and in every one the recording is a bare "Hello." or a Spanish
voicemail greeting. No genuine conversation is overridden.

### 2c. `NEGATIVE` was far too narrow

Any producer note counted as proof of contact unless it matched a short list.
Missed, all found by Frank reading the 08-17 rows:

- "did not respond to my calls" (Edward Federico)
- "got a message saying call was restricted" (Arturo Morales)
- "Number does not seem to be in service" (Gail M Clemente — the pattern
  required the exact phrase "not in service")
- "Keep getting busy dial tone" (Stephany Showers — it knew "busy signal")
- "phone and email are not good" (John Doe)

### 2d. Whisper only read the first 30 seconds

67% of 08-17's recordings run longer. `transcribe_file()` now reads the **first
and last** window and classifies on both.

Last-30-only would be *worse*: Robert Valenzuela's tail is Lorena delivering her
pitch into his voicemail and reads as a live conversation opening. The machine
greeting that proves a voicemail is always at the start; the outcome is at the
end. Both, or neither.

### 2e. Spanish calls auto-scored as live contacts

Whisper emits `(speaking in foreign language)` for untranscribable Spanish — and
the `HUMAN` pattern matches the word **"speaking"**. Every such call scored live.

`_model()` now accepts a language and retries in Spanish. Whisper base was
always multilingual; the parameter was simply never passed. Cost: nil.

Also: bare bracketed tags (`[no audio]`, `[COUGH]`) fell through to a default of
*live*; `NON_SPEECH` catches them now.

### 2f. Screeners were filed as voicemail

An AI attendant reads as a machine greeting, so it short-circuited to Voicemail
before the screener check ran. **17 of 08-17's calls were screeners** —
13% of the day's dials reaching a screening layer and never the prospect,
previously invisible. Detected from the producer's note *and* from the
recording ("if you record your name and reason for calling…").

### 2g. Data-capture notes counted as contact

`PROGRESSIVE RENEWAL IS $1074.50 09/14/2026` is research pulled off the carrier
report **while the phone rings** — Frank: "he pulls that info up while the phone
is ringing". Notes carrying policy data with no verb of interaction are now
treated as neither positive nor negative. Safe because a real conversation also
leaves a recording: Brian Nauenburg has the same note shape and stays live on
his 9:49 audio.

---

## 3. Recontact counted dials from a one-day call log

`recontact` asks "how many dials since this lead entered its stage" — up to 30
days back — and was answering from `rc_raw_<day>.json`. Every "calls since"
collapsed to that day's dials. Frank's trigger: Pamela Rice showed 0 against
three real dials on 08-12, 08-13 and 08-14.

`pull_sources` now builds `rc_window_<day>.json`, **fetched one day at a time**:
a single request spanning 31 days comes back capped at 1000 records with
`totalPages=1`, so the first attempt silently returned only the most recent ~5
days. 7,027 records over 32 days.

Consequences: the over-dialled trigger had **never once fired** in the report's
history — it now catches 28 of 52 leads. Rows with a real last-dial date went
from 8 to 48, so "most critical = most recently contacted" actually sorts.

Pamela Rice now reads 7 calls since 08-05, last dial 08-14.

---

## 4. Smart cycle: short cycles are a pause, not a loss

Frank: a cycle returning within 29 days is "giving them a week or 2, or wanting
automation to restart".

**The cycle date is `xDate`.** Confirmed on two leads whose `xDate` and
`nextExpirationDate` disagree — Larry Pihlman 02/03/2027, Brian Nauenburg
02/10/2027 — both badges matched `xDate`. Corroborating: `xDate` is populated on
**all 4,560** smart-cycled leads and future-dated on 4,557, versus 382 of 1,063
active leads with only 33 future.

**Not** `nextExpirationDate`, despite the "modified Next Expiration Date"
activity (all 79 of those edit `nextExpirationDate`) — it is absent on 40% of
smart-cycled leads, so it cannot drive the badge.

New "On pause" section in the card panel and the Recontact PDF. 08-17: 1 paused
(Tiffany Comstock, returning in 1 day), Lost 37 → 34.

---

## 5. At-risk flags now describe effort

Was `stalled` / `over-dialled` / `both`. Frank: over-dialling isn't the
problem, the lead not moving is — and `both` only ever restated `stalled`,
since no lead reaches 4+ dials inside 3 business days.

| flag | calls since entering stage | 08-17 |
|---|---|---|
| **not worked** | 0–1 | 13 |
| **under-worked** | 2–3 | 11 |
| **no traction** | 4+, still not moving | 28 |

---

## 6. Smaller corrections

- **Call Detail sort** — was one global sort on duration, interleaving all three
  reps. Now producer → outcome → longest call. The attachment used a different
  code path, which is why the file looked right and the email body didn't.
- **Note attribution** — the note column took the producer's typed note but
  labelled it "From the call recording" (Lazaro Rueda). Recording text and
  producer text are now separate fields, each labelled for what it is.
- **Row colour** — `"quote" in moves` matched the pipeline name **"Leads Not
  Quoted"**, colouring Lazaro Rueda red. Matches the stage segment only now.
  The same trap was already fixed once in the households-quoted count.
- **Test leads excluded** — 34 in the corpus (Mav AI seeds, hand-typed "Test Do
  Not Call"). "John Doe" was a live contact; "John Doe" and "John Test" were in
  the Lost list.
- **Green check** on any clear audit section, inline-styled — Gmail can't be
  trusted with a `<style>` block.
- **AgencyZoom links** on audit rows, leads to `/lead?id=`, customers to
  `/customer?id=`. Which is which is decided by corpus membership, not
  `customerType`, which is wrong on a few rows. *The customer URL pattern is
  unverified — worth one click.*
- **Outcome breakdown** — rows ranked by call volume, bars scaled across
  producers so the busiest runs full width. Segment order stays canonical.

---

## Watch out

- **Greedy patterns ate real text twice.** `[^.]*` after "automated text went
  out" swallowed Roberto Juarez's "Left VM"; `[^\n]*` after "Lead source:"
  swallowed the whole of Elsa Aguilera's note. Every stripper is bounded now,
  and no-contact signals are read from the raw note as well as the stripped one.
  **Bound your quantifiers.**
- **Over-correction is as real as under-correction.** Adding the agency's
  voicemail script to `MACHINE` flipped Lorna Lawrence — a genuine conversation
  containing "Hi, is this Mourna? Yes, it is." The script body is said word for
  word to live prospects; only the closing lines ("please give me a call back")
  are machine-only.
- **Lorena at 1 live contact of 53** rests entirely on her own notes. It is not
  the classifier guessing, but it is a number worth a human check.
- Still unresolved: **Vincent Grant** (11s, entire recording is "Hello.", no
  notes) and **Roberto Juarez** (no recording at all, 80s AgencyZoom call note).
  Both now resolve via task notes, but neither has independent evidence.
- **Call summaries** in the note column would need a multilingual model and
  full-length transcription. Chunking every 30s is possible with the current
  model — roughly +20 minutes on the run. TRAQ/Agency Coach AI already
  transcribes these calls and is already paid for; their API is worth checking
  before building anything.
