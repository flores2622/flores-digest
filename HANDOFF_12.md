# HANDOFF 12 — 2026-09-02

Written by the nightly scheduled run. Both emails sent 19:13 AZ. Team: 178
dials, 13 live, 7.3%; 16 households quoted, $29,911 quoted, $4,151 sold.

Everything below was re-verified against the code and the API tonight, because
several items the handoffs still carry as OPEN are in fact closed, and one is
implemented on the read side only. Trust this file over the older sections it
names.

---

## Verified CLOSED — stop carrying these forward

1. **"Fixtures cannot run in a fresh container."** CLOSED. `tests_live_contact.
   py` reads `fixtures/live_contact_2026-08-31.json` (194 cases), not
   `data/transcripts_2026-08-27.json`. It ran clean in tonight's cold clone:
   **151 passed, 0 failed, 43 awaiting adjudication.** The scheduled-task prompt
   still describes the FileNotFoundError gap — that text is stale.

2. **HANDOFF 11 §6, "RingCentral `result` is never read."** CLOSED.
   `live_contact.outcome_bucket(ev, live, rc_results)` now falls back to
   `rc_outcome()` last, after notes and recording (`daily.py:428`).
   Evidence: **No Outcome Logged fell to 2 across the whole team tonight**,
   against Lorena's 19 by herself on 08-28.

3. **"A lead reached on two numbers makes the live count one too high."**
   CLOSED — the scheduled prompt still lists this as a known open bug and it
   should be removed. `_one_row_per_lead` returns `(kept, collapsed)` and the
   caller marks the duplicates `dropped`, so they leave the numerator AND the
   denominator (`daily.py:225`, 553). Evidence tonight: for all five producers
   `len(call_detail) - inbound == live` exactly, and Coral's 16 dial records
   collapsed to a call volume of 15.

4. **HANDOFF 11 §7, `verify_finalize.py` day hardcoded to 2026-08-25.** CLOSED,
   it takes `sys.argv[1]` now.

---

## STILL OPEN, ranked

### 1. Missed-call tasks cannot be created on LEADS — costs tasks every night

`POST /v1/api/tasks` answers `400 {"error":"The customer is not found",
"fieldErrors":[]}` for every lead-bucket caller. Customer and standalone tasks
are fine. Two of eleven were lost to this tonight.

Established read-only tonight, so nobody repeats it:

* **The shape we send is the shape AgencyZoom itself stores.** An existing lead
  task pulled from `/v1/api/tasks/list` (id 125760240, Edgar Gutierrez) carries
  `customerId: 35856046` with `customerType: "lead"` — exactly what `create()`
  builds.
* **The ids we send are valid.** `GET /v1/api/leads/88605283` → 200, likewise
  88941892. Both are real leads in `az_leads_all.json`.
* **`GET /v1/api/customers/<lead id>/tasks` returns `null`** for leads
  generally. That is what crashed `already_there()`; fixed in this branch.

So this is a create-side contract mismatch, **not** bad data and not a missing
record. I could not test payload variants — writes to the live CRM were blocked
in this session, deliberately.

Next step, in a session permitted to POST, stopping at the first success (a
success creates a task that is genuinely wanted, so nothing is wasted):

    A. leadId=<id>  instead of customerId/customerType
    B. customerType as a numeric enum (2) rather than the string "lead"
    C. POST /v1/api/leads/<id>/tasks
    D. add dueDate / taskDateTime — a missing required field can surface as
       this same misleading "customer is not found" message

Cheaper oracle: AgencyZoom's own automation creates these every day ("Never
quoted lead- Day 4/7 NEW"). Ask AgencyZoom support what POST body creates a task
on a lead, rather than guessing against production.

Until then the branch keeps the batch alive and logs
`STILL NEEDS A TASK BY HAND` for each one.

### 2. Two tasks from 09-02 were never created

Create by hand in AgencyZoom:

* **Lonnie Mcknight → Crystal** (lead 88605283, called 4:20 PM, (707) 236-2439)
* **Nancy Martens → Sarahi** (lead 88941892)

### 3. Corpus caches are still not date-scoped — HANDOFF 11 §5, still open

`pull_sources` guards `az_leads_all.json`, `az_customers_all.json` and
`az_policies_all.json` with `if not p.exists()` (`daily.py:100,108,113,118`).
A fresh container is fine — that is why tonight was fine. **A re-run in a warm
container silently reports stale numbers**; on 08-28 it hid four sales and
reported $0. Fix: refresh when the file's mtime predates the day being built.
Until then, delete those three files before any re-run in a warm container.

### 4. The smart-cycle ">30 days is lost" rule has never actually run

`panels._is_lost_action` reads `row.get("smartcycle_days")` (`panels.py:719`)
and **nothing anywhere assigns that key** — grep finds only the read. So it is
always `None`, every smart-cycle scores "not lost", and the rule Frank set on
08-28 has been dead since it was written while looking implemented. Either plumb
the smart-cycle target date onto the row or delete the branch. This is the one
that most deserves attention, because it reads as done.

### 5. No wrong-number outcome — HANDOFF 11 §7

Kenneth Payne counts live and in the contact rate but has no Call Detail
category; there is no "Wrong Number" string in `panels.py` or `digest_config.py`
at all. Needs the colour-by-family rework HANDOFF 10 deferred (nine categories
on six hues already). Note the **data is now free**: RingCentral's `result`
supplies "Wrong Number" and is finally being read (closed item 2 above). Only
the chip is missing.

### 6. Nothing checks the report before it sends — HANDOFF 11 §8

A cheap gate would catch: contact rate moving more than ~5 points overnight, a
producer at zero, a live contact whose transcript says voicemail, a duplicate
`lead_id`, a sub-5-second contact. **Tonight Crystal at 0.0% on 41 dials would
have tripped it.** It looks real (see below), but the point stands that it
should surface before the send, not in a report afterwards.

### 7. Legend gap — HANDOFF 11 §7

Only the green callback swatch is in the legend. The amber stripe (called back
after a voicemail) is unexplained, and that conversation is counted in Call
Detail while the bar still shows the dial as Voicemail.

### 8. Scheduled sessions still cannot push

Asked for since at least 08-31. Add `flores2622/flores-digest` to the scheduled
task's sources. Two costs while it is missing: every nightly code fix comes back
as a hand-carried patch, and `hourly.py` cannot cache transcripts between runs,
so a lost container re-downloads the whole day against RingCentral's quota.

---

## Not a bug — do not re-report

* **Call scores over 100, and low scores generally.** A perfect call is 750-800;
  TRAQ scores voicemails as calls (3 against a live call's 292), so Avg Call
  Score and Avg Sentiment track answer rate, not call quality. Both were removed
  from leaderboard points on 09-01 and still display in Coaching.
* **`hourly.py` printing "COULD NOT SAVE THE TRANSCRIPTS".** Meaningless in the
  single-session flow — the transcripts are already on local disk, which is all
  `daily.py` needs.
* **Crystal at 0.0% on 09-02.** 41 dials: 28 voicemail, 8 no answer, 5 screener,
  0 live, plus one 19-minute inbound conversation that sits outside the rate by
  design. Her Coach AI score of 48 is consistent with an almost entirely
  unanswered day. Reads as real; a coaching question for Frank, not a data
  fault. Do not "fix" it.
