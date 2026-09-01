# Hourly runs — settled rules

Two features share one hourly schedule and one persistence problem:

1. **Transcript prefetch** (§12) — pull and transcribe each hour so the evening
   digest is not doing 30 minutes of downloading at 6:45pm. **This is what Frank
   asked for first, and it is the bigger win.**
2. **Missed-call tasks** (§1–§11) — create a task in AgencyZoom when an inbound
   call goes unanswered.

Everything below was adjudicated by Frank across the 08-31 and 09-01 sessions.
These are decisions, not proposals. Do not re-litigate them; if something here
is wrong, it changed, and the change should be recorded here.

Neither prototype exists yet. This file is the spec they have to satisfy.

---

## 1. What triggers a task

A RingCentral inbound call that nobody answered. On 08-28 that was 21 people.

**No dry run.** Frank asked for this live from day one.

## 2. Where the task goes

Resolved against AgencyZoom, in this order:

| What we find for the caller | Task goes to | Attached to |
|---|---|---|
| An open lead | the lead's producer | the lead |
| An open service request | the assigned CSR | the service request |
| A customer record, nothing open | Amanda | a **new** service request she opens |
| A closed lead, no customer record | **Amanda, to triage** | the closed lead |
| No record at all | Debbie | standalone task (dashboard task, no record needed) |

**Volume, measured over 20 business days (Aug 3–28).** 685 unanswered inbound
calls → **517 tasks** after one-hour grouping, ~26/day:

| Route | Tasks | Share | Per day |
|---|---|---|---|
| Customer, nothing open → Amanda | 218 | 42% | 10.9 |
| No record at all → Debbie | 155 | 30% | 7.8 |
| Open lead → producer | 55 | 11% | 2.8 |
| Former lead, not a customer → Amanda (triage) | 45 | 9% | 2.2 |
| Open service request → CSR | 44 | 9% | 2.2 |

**Do not plan from 08-28.** That day was 57% no-record; the four-week figure is
30%, and the dominant bucket is Amanda's, not Debbie's. Amanda's route means
**~11 new service requests a day** — decide whether that is wanted before going
live.

**Amanda carries both middle buckets: 218 + 45 = 263 tasks, ~13/day.** Frank,
09-01, on the former-lead group: *"those should go to amanda to delegate as leads
or service."* She triages; she does not have to work them herself.

Composition of those 45 (36 distinct numbers): **31 smart-cycled, 4 lost/dead, 1
sold.** Worth knowing — a smart-cycled lead still has an assigned producer
(Crystal, Mike, Lorena, Sarahi and Adrian all appear). Routing to Amanda instead
of back to that producer is deliberate: the lead is not being actively worked, so
the producer is not expecting the call. Median gap since last activity is 12
days.

Frank on Debbie's fourteen: *"once Debbie starts seeing so many tasks for missed
calls she will be a lot better with picking up the phone. I dont mind that the
tasks become redundant."* Volume in her queue is the intended signal. Do not
add throttling to make the number look better.

## 3. Grouping — one task per person, one-hour window

One task per caller per rolling hour. Calls more than an hour apart get their
own task. Ricardo Perea's five calls between 12:08 and 12:49 on 08-27 are one
task, not five.

## 4. Format — option B, worded per account type

Frank picked B out of three mockups on 09-01, then: *"you should specify on each
task the type instead of giving different options to avoid confusion, all
language and vocab should reference the correct type of account."* Then, after
the Lupita Hernandez case (§10c): *"add that as a bullet for everyone, it will
help greatly with housekeeping."*

We know which bucket the caller landed in before the task is written, so the body
never offers a choice. Four bodies, one per route.

**Title, all four** — `Missed Call from <name>`, or the phone number when we have
no name.

**Meta line, all four** — number, call count, time window, voicemail flag, and
**RingCentral's caller ID** when it supplies one:

    (928) 318-3033 · called 3× 10:14–10:51 AM · left voicemail
    caller ID: HERNANDEZ, LUPIT

The caller ID is worth showing even on a matched record — it tells the producer
*which member of the household* is on the phone.

### Open lead → the lead's producer

    Attempt to contact this lead
    • if they don't answer, leave a voicemail and send a text. Complete this
      task as long as the lead is open with automation on
    • if contact has already been made, complete this task
    • if you know why the lead is calling and you are working on it, let them
      know via phone/text
    • before you complete this, check that the number they called from, their
      email and their address are on the lead in AgencyZoom. Fix anything
      missing or wrong

### Open service request → the assigned CSR

    Attempt to contact this customer
    • if they don't answer, leave a voicemail and send a text. Complete this
      task as long as the service request is open with automation on
    • if contact has already been made, complete this task
    • if you know why the customer is calling and you are working on it, let
      them know via phone/text
    • before you complete this, check that the number they called from, their
      email and their address are on the customer record in AgencyZoom. Fix
      anything missing or wrong

### Customer, nothing open → Amanda

    Attempt to contact this customer
    • a service request has been opened for this call. If they don't answer,
      leave a voicemail and send a text, then complete this task as long as that
      service request stays open with automation on
    • if contact has already been made, complete this task
    • if you know why the customer is calling and you are working on it, let
      them know via phone/text
    • before you complete this, check that the number they called from, their
      email and their address are on the customer record in AgencyZoom. Fix
      anything missing or wrong

### Closed lead, no customer record → Amanda, to triage

Task goes on the closed lead so she has the history in front of her.

    Attempt to contact this caller — their lead is closed and they are not a
    customer on this number
    • if they don't answer, leave a voicemail and send a text
    • if contact has already been made, complete this task
    • once you know why they are calling, delegate it: open a new lead and assign
      a producer if they are shopping, or open a service request if it is service
    • before you complete this, check that the number they called from, their
      email and their address are on the record in AgencyZoom. Fix anything
      missing or wrong

### No record at all → Debbie

    Attempt to contact this caller — we have no record for this number
    • if they don't answer, leave a voicemail and send a text
    • if contact has already been made, complete this task
    • if you know why they are calling and you are working on it, let them know
      via phone/text
    • before you complete this, get this number onto a record. If they turn out
      to be an existing customer or lead on another number, add it there and
      check Apex; if they are shopping, create a lead. Nothing else will do this,
      and until it happens the same number generates a fresh task every time it
      rings
    • nothing will follow up automatically on this one. There is no lead and no
      service request behind it, so do not complete it until you have either
      reached them or left both a voicemail and a text

**NO match hints on Debbie's tasks.** Frank, 09-01: *"No hints for Debbie,
creates room for error and mistakes."* A surname-only CNAM match is weak evidence
and a wrong one sends her editing the wrong household's record. The pipeline must
not print a "possible match" line, and must not name a candidate record.

The raw `caller ID:` line stays — that is what the carrier reported, not an
inference the pipeline made. If that also needs to go, it is a one-line change.

The housekeeping bullet is Frank's, added 09-01. The rest of each body is his
original wording with the noun swapped.

**OPEN — "with automation on" is not safe on the service routes.** Frank, 09-01:
*"no automation is sent to the client, only tasks for us."* Service Pipeline
tickets do carry `enrolled: 1` (156 of 158 at stage New), but what that
automation produces is internal tasks, not messages to the customer — and the
sampling above found zero TEXT or EMAIL notes on any service household.

That undercuts the escape clause on **two** bodies. "Complete this task as long
as the service request is open with automation on" is true on the lead routes,
where automation really does text the client (3,234 automation texts in the
corpus). On the CSR and Amanda routes it tells someone they can close a
missed-call task and let automation take over when nothing will contact the
customer at all — the same trap Debbie's route was given an explicit warning
about. Needs Frank's wording, but those two bullets should probably read like
Debbie's: do not complete until you have reached them or left a voicemail and a
text.

## 5. Already handled → no task, digest row instead

At run time, if a human has already reached the caller, do not create the task.
Put the row in the digest with the response time instead — Frank wants to see
how long it took the team to call back, not just that the call was missed.

"Human interaction" means an outbound call, or a **hand-typed** text. It does
NOT mean an automation text.

**The endpoint** — `GET /v1/api/leads/{id}/notes`. It accepts customer and
household ids as well as lead ids (all 200).

**CORRECTION, 09-01 — this only solves the LEAD routes.** An earlier version of
this file said one endpoint covered every route. It does not.

    lead ids        TEXT 5,804 · EMAIL 3,489 · TASK 3,188 · CALL 2,225
    household ids   0 TEXT · 0 EMAIL · 0 CALL   (25 households sampled,
                    102 notes: MOVE_STAGE, TAG, enroll/unenroll, expiry only)

For a customer the endpoint returns the **lead-lifecycle history**, not the
conversation. No communication history is exposed for customers anywhere:
`/customers/{id}/` + `notes`, `texts`, `sms`, `communications`, `timeline`,
`history` all 404, as do `/households/{id}/notes` and `/v1/api/notes?customerId=`.

So the already-handled test differs by route:

| Route | Outbound call | Hand-typed text |
|---|---|---|
| Open lead | RingCentral log | note with no `attr.triggerRuleId` |
| Closed lead → Amanda | RingCentral log | note with no `attr.triggerRuleId` |
| Open SR / customer / no record | RingCentral log | **not visible — accept the gap** |

Frank already ruled the equivalent gap acceptable for unknown callers (*"Its fine
for no text on unknown contacts"*). It now extends to every customer route. A
customer texted back but never called will still get a task.

`GET /v1/api/customers/{id}/tasks` **does** work (200) — useful for §8, to
re-derive what is already on a record instead of keeping a ledger.

**Discriminating automation from human texts:** the note's `attr.triggerRuleId`
is present on automated messages and absent on hand-typed ones. `createdBy` is
useless — automation signs the producer's name. Measured over the corpus: 4,406
outbound texts = 3,234 automation (73%) / 1,172 hand-typed (27%).

RingCentral's call log has no SMS at all (every record is `type: Voice`), so the
text check must come from AgencyZoom.

Unknown callers with no record have no text history to check. Frank: *"Its fine
for no text on unknown contacts."*

## 6. Closing tasks we created

If a later run sees the caller was reached after the task was created, close the
task automatically — but keep it visible. Frank wants the record that a missed
call happened AND how long it took to get back to them.

    PUT /v1/api/tasks/{id}  {"status": 1}

`status:1` does NOT populate `completeDate` / `completedBy`. If the close
timestamp matters for reporting, the pipeline has to record it itself when it
issues the close.

## 7. Run schedule — office hours only

Frank, 09-01: *"I only want it reading them during hours the assigned producer
even has a chance to call back."*

**Staff hours, Arizona:**

| | Hours |
|---|---|
| Debbie, Crystal, Lorena | 8:30 AM – 5:30 PM |
| Sarahi, Amanda, Coral, Mike | 9:00 AM – 5:30 PM |
| Everyone | lunch 12:00 – 1:00 |

**Runs — Frank's times, Arizona, Monday–Friday. Ten a day. No Saturday.**

    8:35   9:50   10:55   11:45   1:00   2:00   3:00   4:00   4:45   5:15

Rationale, his: 8:35 catches everything that came in overnight. 4:45 and earlier
is same-day work for everyone. 5:15 is next-day for the early shift and still
same-day for the late shift.

No run between 11:45 and 1:00 — the office is at lunch. Because lunch is
universal, the schedule handles it and no per-person logic is needed.

Arizona does not observe DST, so AZ = UTC-7 all year.

    35 15  * * 1-5    UTC  →  8:35 AM AZ
    50 16  * * 1-5           9:50 AM
    55 17  * * 1-5          10:55 AM
    45 18  * * 1-5          11:45 AM
    0  20-23 * * 1-5         1:00, 2:00, 3:00, 4:00 PM
    45 23  * * 1-5           4:45 PM
    15 0   * * 2-6           5:15 PM AZ (lands on the next UTC day)

**No per-assignee gating anywhere.** Frank, 09-01: *"its okay for the late
staff on the early time, it can be there for them when they come in."* The 8:35
run creates tasks for everyone, including the 9:00 crew, who find them waiting.

That collapses the whole hours question into the run times. There is no hold
state, no escape hatch for a call whose assignee is out, and no staff-hours
table in code — the table above is documentation of why the ten times are what
they are, nothing reads it. A call is either in the log at run time or it is not.

Calls after 5:15 roll into the next morning's 8:35 run.

**Ten runs a day changes the data-access pattern.** The nightly digest pulls the
whole AgencyZoom corpus. An hourly job must not. It should resolve callers by
querying the phone number directly and touch nothing else. This is also the
cheap way to avoid repeating the §5 staleness bug in HANDOFF 11, where a re-used
container served a day-old lead corpus and hid four sales.

## 8. Idempotency — the thing that will break first

Every hourly run re-reads the same call log. Ricardo's 12:08 call is still in it
at 1:30, 2:30, 3:30. Without a memory of what was already created, one missed
call becomes a task every hour until close.

Each run starts in a fresh container, so in-process state is worthless. The
ledger — caller number + hour-window → AgencyZoom task id — has to survive
between runs. Two options:

1. A tracked file in the repo, written after each create.
2. Re-derive it: query AgencyZoom for open tasks matching the number and window
   before creating. No state to lose, but a call per run.

This is the same persistence problem as keeping transcripts between hourly runs.
Solve it once for both.

## 9. AgencyZoom write API — confirmed live

Probed against Frank's own customer record 38420894 on 08-31 and 09-01. Fifteen
probe tasks were created and all closed; the earliest, 125562525, is still on
that record.

### Tasks

    create   POST /v1/api/tasks        → {"message":"Create task successfully","id":…,"result":true}
    close    PUT  /v1/api/tasks/{id}   {"status": 1}
    assign   PUT  /v1/api/tasks/{id}   {"assigneeId": …}

Working create body:

    {"title": …, "comments": "<p>…</p>", "customerId": …,
     "customerType": "customer" | "lead", "assigneeId": …, "type": "call"}

**Three silent no-ops, all returning HTTP 200. This API does not reject a field
it does not recognise — it accepts it and ignores it.** Every one of these had
to be caught by reading the record back.

1. **`type`, not `taskType`.** The create body key is `type`; the record reads
   back as `agencyTodo.taskType`. Sending `taskType`, `todoType`, `typeId`, or a
   nested `agencyTodo` object all return 200 and leave the type null. Values seen
   in the corpus: `call` (207), `todo` (73), `reminder` (62). `typeId` is null on
   all 342 records — it is a dead field, ignore it.
2. **`assigneeId` only.** `assignedTo`, `employeeId`, `assignees` and
   `assignedToId` all 200 and do nothing.
3. **The due date cannot be set.** Tried on create: `dueDate` as `2026-09-02`,
   `2026-09-02 23:59:59`, `09/02/2026`, ISO-8601, epoch millis; plus `date`,
   `taskDate`, `dueDateStr`, `datetime`, `dueDateTime`, `taskDateTime`,
   `dueInDays`, and `wholeDay`/`timeSpecific` combinations. Tried after create:
   `PUT /v1/api/tasks/{id}` with `dueDate` and `taskDateTime` — returns
   `{"message":"Task updated","result":true}` and changes nothing.
   `PUT /v1/api/tasks` and `POST /v1/api/tasks/{id}` are both 404.

   **Every task is due the day it is created.** "Due the next morning" is not
   available through the API. See §10.

A task can be created with no customer or lead record attached — that is
Debbie's bucket.

### Service requests — Amanda's bucket

    create   POST /v1/api/serviceTicket/service-tickets/create

The path is the find: `/service-tickets`, `/serviceTicket`, `/serviceTickets`,
`/service-tickets`, and `/serviceTicket/create` are all 404. Only the `/create`
suffix on the full list path exists.

An empty body returns the required-field list:

    customerId · workflowId · workflowStageId · subject
    categoryId · priorityId · otherCsrs (array)

Values read off the 343 live tickets in `az_service_tickets_2026-08-28.json`:

| Field | Use | Why |
|---|---|---|
| `workflowId` | **23074** — Service Pipeline | the general queue, 162 of 343 tickets |
| `workflowStageId` | **78844** — New | 149 of the 162 sit here |
| `priorityId` | **24501** | normal; 314 of 343 |
| `categoryId` | **25617**, probably | 104 tickets, mixed subjects including "call back" — this is the misc/general bucket. The API returns no category names and there is no lookup endpoint, so **confirm with Amanda before shipping.** 25622 is the other big one (103) and is clearly renewals. |
| `csr` | **105006** — Amanda Torricellas | see the correction below |

**Correction, 09-01.** An earlier note in this file guessed that csr `83597` was
Amanda because that id holds 254 of 343 open tickets. `GET /v1/api/employees`
says **83597 is Debbie Aguilera**. Amanda Torricellas is **105006**. Debbie, not
Amanda, is the CSR of record on most open service tickets today — Frank's routing
decision still stands, but do not infer identities from volume again.

Attach the task to the new ticket via `agencyTodo.serviceTicketId`; 42 of the
342 task records already do this, so the linkage works.

### Employee ids for `assigneeId`

    Debbie Aguilera      83597        Sarahi Chin        185441
    Crystal Mango       174445        Coral Barwick      185440
    Lorena Gonzalez      82587        Mike Olvera         82588
    Amanda Torricellas  105006        Frank Flores        82589

Full roster is 24 people via `GET /v1/api/employees`; those are the eight in the
missed-call routing and the hours table.

## 10a. How cold is Amanda's bucket

Measured 09-01 over the same 20 days. Days between the missed call and the last
lead or SR activity dated **before** the call (a callback made afterwards must
not flatter the number — `lastActivityDate` is live, not a snapshot, and using it
raw produced negative gaps).

    median 46 days · mean 177 days · p25 7 · p75 274

Two populations, not one. **82 of 218 (38%)** were touched within the last 30
days — a new SR there likely duplicates something that just closed. **54 (25%)**
had gone over six months untouched, which is exactly what a new SR is for. Last
touch was a lead for 136 and an SR for only 47: most of this bucket is people we
sold and then stopped hearing from. 35 (16%) have a customer record but no lead
or SR predating the call at all.

## 10b. FOUND — the SR corpus has only ever read OPEN tickets

`az_client.service_tickets_all()` passes `status: "all"` and its docstring claims
that returns open plus completed. **It does not.** Probed 09-01:

    status="all"   → 344 rows, all status 0 (OPEN)
    status omitted → 361 rows, all status 1 (CLOSED)
    status=[0, 1]  → 705 rows, both

So the function named `_all` has been returning open tickets only, and the
renewal exclusion that rests on it has never been able to see an SR completed
that day — the exact failure its own comment warns about.

**The one-line fix is NOT safe on its own.** `inbound.py` decides whether a
ticket was open on the day being built with:

    created > day        -> not yet open
    completeDate < day   -> already closed

**359 of the 361 closed tickets have no `completeDate`.** Only 2 do. So under a
bare `status: [0, 1]` every closed ticket reads as permanently open. Measured
against 2026-08-28: 324 closed tickets would be counted open, when only 50
actually were — **274 phantom open tickets, every single day**. That would screen
real inbound calls out as service work and quietly depress contact rates.

`lastActivityDate` is the usable close proxy; on closed tickets it lands seconds
to hours after `createDate`.

**The fix is two parts, and both are needed:**

1. `service_tickets_all()` passes `status: [0, 1]` — the list, not the string
   `"0,1"`, which silently falls back to open-only.
2. Everywhere a ticket's open-on-day test runs (`inbound.py`, `day_calls.py`),
   a `status == 1` ticket closes on `completeDate` **or, when that is null,
   `lastActivityDate`**.

Land them together or not at all.

## 10c. WHY the "no record" bucket is inflated — the Lupita Hernandez case

Frank, 09-01, on customer **31650722**: *"im thinking this is going to be a lack
of updating contacts and info in agency zoom. i found it through apex which i
cant give you access."* Confirmed, and the call log makes it unarguable.

The record is **Eduardo Castrejon Rios**, one of Amanda's accounts, two policies,
phone on file **(928) 318-0441**. The missed calls came from **(928) 318-3033**,
caller ID `HERNANDEZ,LUPIT`. Nothing in AgencyZoom connects them — not phone, not
email, not household. The link exists only in Apex.

    (928) 318-0441   on the record       0 calls in all of August
    (928) 318-3033   on no record       16 calls, incl. 13 min on 8/12
                                        and 25 min across three calls on 8/25

The household does all its business on a phone AgencyZoom has never heard of, and
the number the record *does* carry is dead.

**Phone matching structurally cannot fix this.** There is no field that would
link 318-3033 to Eduardo. The 32 surname-match numbers in §10d are very likely
all this same story.

Two consequences:

1. Debbie's tasks are partly a **data-hygiene mechanism**. Every one she works
   that turns out to be an Apex match puts one more number into AgencyZoom, and
   that caller never generates a false "no record" task again. That is why the
   housekeeping bullet went on all four bodies.
2. The best the pipeline can do unaided is offer the caller-ID surname as a hint
   (§4). It cannot resolve the match itself.

Contact-data gaps measured over the same 20 days, for scale: of 398 distinct
callers, 265 matched a record; 21 of those (8%) have no email on file, and 2
matched only on `secondaryPhone`. The unmatched 133 are the real problem, not the
matched ones.

## 10d. The 133 unmatched numbers, categorised

Only 42 look genuinely unknown.

| | Numbers | Share |
|---|---|---|
| Caller-ID surname matches a record on a different phone | 32 | 24% |
| We have dialled this number ourselves | 32 | 24% |
| We have answered them, no record was ever made | 20 | 15% |
| Toll-free / business line (carriers, claims, one flagged spam) | 7 | 5% |
| Genuinely cold | 42 | 32% |

Standouts: **(928) 318-3033** — dialled 7 times, answered 5, no record (the
Lupita case). **(800) 238-9671** — we dialled it 21 times; a line we work with,
not a caller. **(256) 857-4880** — answered 12 times, never dialled, no record.
RingCentral flags spam itself in `from.name == "Possible spam call"` (7 records in
August) — cheap filter, worth using.

**RingCentral caller ID is not read anywhere in the pipeline today.** It is what
surfaced all of the above.

## 11. What is left

Rules and API are settled. Nothing below is a rules question except the two
marked **ASK**.

**Needs a person**

- **ASK Amanda: what is `categoryId` 25617?** Inferred from 104 tickets with
  mixed subjects including "call back". The API returns no category names and
  there is no lookup endpoint, so this cannot be resolved from data. Blocks the
  first real service request.
- **ASK Frank: is ~26 tasks/day the load you want?** 13 of them Amanda's. The
  rules are built; this is a volume call, and it is easier to answer after a week
  of the digest reporting what the job *would* have created than in advance.

**Needs a build**

1. **Persistence.** Decides §8. Test whether an hourly run gets a warm container
   or a cold clone; that picks the idempotency ledger (tracked file vs. re-derive
   from AgencyZoom open tasks). Same answer serves the hourly transcript work.
2. **Caller resolution by phone**, narrow — never the full corpus pull the nightly
   digest does (§7).
3. **The §5 already-handled check** — outbound call in the RC log for every
   route, plus for the two lead routes a note on `/v1/api/leads/{id}/notes` with
   no `attr.triggerRuleId`. Customer routes are call-only; the text gap is
   accepted.
4. **Create + assign + link**, per §9. Five routes, five bodies, five assignees.
5. **The digest row** for calls that were handled before the run — with the
   response time, which is the seed of the future service and retention digest.

**Adjacent, not part of this**

- `service_tickets_all()` reads OPEN tickets only (§10b). One-line fix, but it is
  in the nightly digest and affects the renewal exclusion.
- RingCentral caller ID is read nowhere in the pipeline. It is what surfaced
  every finding in §10c and §10d.
- RingCentral flags spam itself in `from.name == "Possible spam call"` — 7
  records in August. Cheap suppression filter.

---

## 12. The other half — hourly transcript prefetch

Frank, 08-31: *"how can we start doing hourly check ins to ringcentral to
download and transcribe the calls?"* This is the original ask. The missed-call
work was added on top of it and then took over the conversation; the run
schedule in §7 exists to serve both.

### BUILT — `hourly.py`, written and tested 2026-09-01

    python3 hourly.py                # today, Arizona
    python3 hourly.py --day 2026-09-01
    python3 hourly.py --dry-run      # report state, fetch nothing

It is thin on purpose. `daily.transcribe_day()` was already incremental — it
reads the existing transcripts file and processes only what is missing — so the
script's real job is just to keep today's call log fresh and call it. The one
thing it must NOT reuse is `daily.pull_sources`'s `if not f.exists()` guard on
`rc_raw_<day>.json`: that is right for a finished day and wrong for one still in
progress, and would leave the 4pm run reading the 8:35 snapshot.

Measured end to end on 2026-09-01, both runs real:

    first run, empty cache      18m36s   6m corpus cold start, 8m30s download
                                         61 recordings, 63 transcripts
                                         (voicemail 44 / live 12 / no answer 3 / unclear 4)
    second run, warm cache       3s      +2 call records, +0 transcripts

**Three seconds.** That is the whole case for this design: a warm run costs
nothing, so ten a day is free, and the evening build arrives to a full cache.

It also shows what a COLD run costs — about six minutes of AgencyZoom corpus
pulls before it can screen inbound calls, plus a full re-download. Ten cold runs
a day would be roughly 2,000 media requests against a 10-per-minute ceiling and
would collide with the nightly build. **Do not switch the schedule on until
persistence is confirmed.**

### What it costs today

Measured over 20 business days, Aug 3–28:

    4,762 recordings          238/day average
    496 min of audio/day      peak day 8/25: 298 recordings

RingCentral's media endpoint is capped at 10 requests per rolling 60s and the
downloader paces at 8/min (HANDOFF 11 §3 — 12/min stalled the 08-27 run for 30
minutes at record 115 of 203). At 8/min, **238 recordings is 30 minutes of the
evening run spent doing nothing but downloading**, before a single second of
transcription. The peak day is 37 minutes.

### What the hourly runs change

Spread across the ten runs in §7, a normal day is **~24 recordings per run, about
3 minutes each**. The 30-minute block disappears, and so does any chance of a
rate-limit stall — 24 requests inside an hour never approaches a 10-per-minute
ceiling.

By 5:15pm the evening run finds everything already transcribed and goes straight
to metrics. Calls after 5:15 are the only ones it still has to fetch.

### COLD CONTAINERS — measured 2026-09-01, this is the design constraint

A probe scheduled task wrote a marker file, then ran again an hour later:

    run 1, 19:33 UTC   wrote ~/persist_probe.log
    run 2, 20:34 UTC   NO PROBE FILE — and uptime "0 min"

**Every scheduled run gets a fresh container.** Nothing under `data/` survives.
Two consequences needing different answers, because the artifacts differ by
three orders of magnitude:

    transcripts_<day>.json      32 KB    carry it in the repo
    az_*_all.json (corpus)      25 MB    too big — stop needing it
    rc_window_<day>.json        27 MB    too big — stop needing it
    data/audio/                 46 MB by 1pm, ~240 MB a full day — disposable

**Answer 1: commit the transcript file.** `hourly.py` pulls at the start of a
run and force-adds `data/transcripts_<day>.json` past the gitignore at the end.
32 KB a run, and it is the only thing that makes the next run cheap.

This needs push access, which a scheduled session does NOT have today:

    remote: access denied by the git proxy: flores2622/flores-digest is not in
    this session's authorized repository set... To fix, add the repository to
    the session's sources.

Clone works, push does not. HANDOFF 11 §9 saw the same on 08-31. **The fix is a
settings change on the scheduled task — add the repo to its sources.** Until
then `hourly.py` completes but warns loudly, and the schedule stays paused:
without it every run re-downloads the whole day and burns the RingCentral media
quota the nightly build needs.

**Answer 2: stop needing the corpus.** `daily.transcribe_day()` grew an
`outbound_only` flag and `hourly.py` passes it. The inbound branch is what
pulled the 25 MB corpus and the 31-day RingCentral window — about eight minutes
— to screen roughly three calls a day. In a cold container that price would be
paid ten times daily. The nightly build does inbound itself, so the hourly
prefetch skips it and still captures the expensive part: the recordings.

A run is now: clone, pull transcripts, one call-log request, download what is
new, transcribe, commit. Measured warm after both changes: **15 seconds**.

**`outbound_only` does NOT affect the missed-call feature.** Frank asked,
09-01. What it skips is `inbound.answered()`, which selects
`result == "Accepted"` — inbound calls a producer PICKED UP — and transcribes
them for the contact rate. A missed call by definition was not accepted, so it
was never in that path.

Missed-call detection reads `rc_raw_<day>.json` for
`result in ("Missed", "Voicemail")`, and `hourly.py` **re-pulls that file every
run**. The hourly schedule is the missed-call trigger source, not a casualty of
it. The routing lookups in §2 are narrow per-number AgencyZoom queries and never
needed the corpus either.

### Open

- Whether a scheduled task can be created with repo push access at all (above).
- Merge semantics for `transcripts_<day>.json` when two runs overlap. Keyed by
  recording id, so a dict merge is safe, but the write must not clobber.
- Whether transcription of ~24 recordings fits comfortably inside one run's
  budget. Whisper is local via sherpa-onnx and free, so this is wall-clock only.
