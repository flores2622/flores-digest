# Pantheon's own CRM -- the plan and where it stands

Frank, 2026-10-06: "i basically want to build my own, built into Pantheon."
This is the plan for replacing AgencyZoom with a CRM inside Pantheon, what
was built on the first day, and what each next step is. CLAUDE.md's "Pantheon's
own CRM" section carries the standing rules; this file carries the roadmap.

## The decision that makes it tractable

**The CRM speaks AgencyZoom's shapes.** Everything the nightly and the live
refresh read from AgencyZoom -- a lead's `assignedTo`, `leadSourceId`,
`status` (2 = sold), `soldDate`, `convertedHouseholdId`, `workflowStageId`;
a policy's `agentId` + `soldDate` + `premium` + `policyTypeName` +
`carrierId`; a task's `assigneeId` / `dueDate` / `status`; an SR's
`workflowName`, `csr`, `createDate`, `completeDate`, `resolutionId`, status
0 / 1 / 2; a lead's notes newest first with a `MOVE_STAGE` note per stage
move -- comes back from Pantheon's CRM under the same names with the same
meaning. Imported rows keep AgencyZoom's ids; people are staff.json's
`az_id`. So the 45 Python modules and the Worker's live refresh move over by
swapping the client (`az_client.py`, `live.js azGet`), not by being
rewritten, and every rule in CLAUDE.md -- BOB is not a sale, status 2 means
sold, Unable to Contact is retained, ONE ACCOUNT ONE CONTACT -- keeps
meaning what it means.

## What AgencyZoom does today, and what has to exist before it can go

| AgencyZoom holds / does | Pantheon's CRM |
|---|---|
| Leads (~11,600), stages, quotes, lead sources | `leads`, `stages`, `quotes`, `lead_sources` -- built, API live |
| Customers / households, policies | `households`, `policies` -- built, API live |
| Notes: calls, texts, emails, tasks, stage moves, TRAQ summaries | `notes` (same types), `stage_moves` -- built, API live |
| Tasks per producer | `tasks` -- built, API live |
| Service requests, workflows, categories, resolutions | `service_requests`, `workflows`, `service_categories`, `resolutions` -- built, API live |
| Who changed what (AgencyZoom has no audit trail) | `events` -- every write, who, before and after |
| The screens the producers and service team type into all day | **not built** -- phase 2 on |
| Texting and email through the RingCentral lines, drips and automations | **not built** -- phase 4 |
| Lead intake from vendors (Mav AI, SmartFinancial, SureQuote, Facebook) and TRAQ's notes | **not built** -- phase 5; needs each vendor's delivery method |
| The AgencyZoom mobile app, email open tracking | not planned |

## Phases, in order, each with its cutover test

Each phase moves one workflow into Pantheon while AgencyZoom stays the record
for the rest. Nothing is switched until the two agree on a published day.

1. **Foundation** (done 2026-10-06, below): the database, the data layer,
   the importer, the audit trail. Cutover test: the importer loads the
   saved corpus and `python3 verify_finalize.py` on a past day reads the same
   six headline figures from Pantheon's copy as from AgencyZoom's files.
2. **Tasks and missed-call tasks** (the one thing the pipeline WRITES to
   AgencyZoom): a Tasks page in the Sales Center (due today per producer,
   complete with a comment), `missed_call_tasks.create` writing to
   `/api/crm/tasks` instead, `az_tasks.audit` and `live.js taskCompletion`
   reading from it. Cutover test: Task Completion identical both ways on a
   day run in parallel.
3. **Notes, calls and the lead screen**: the lead page (the coaching card's
   lead opens it), typed notes, the call log written by the nightly's own
   RingCentral pass as CALL notes, stage moves from the page.
   `lead_history`, `messages.py` and `day_calls.fetch_notes` read Pantheon.
   Cutover test: a day's contacts, outcomes and Texts & Emails identical.
4. **Texting and email from the page**, through RingCentral's message API
   (the service lines already feed `rc_client.texts`) and the agency's own
   mail; templates and drips as scheduled jobs in the Worker (a cron it
   already has). This is what retires the producers' AgencyZoom login.
5. **Lead intake**: a webhook per vendor (or an inbox parser where a vendor
   only emails), Facebook's lead form, the walk-in / call-in form on the
   Rotation page creating the lead in the same click. TRAQ's summaries by
   whatever TRAQ offers (email or webhook; no API today).
6. **Service requests and the Service Center**: the SR queue and page,
   completion on Frank's resolutions, `service_digest`, `renewal_report`,
   `claims` and `commercial` reading Pantheon. Cutover test: the Service
   Center, Renewals and Commercial pages identical for a parallel day.
7. **Policies and households**: policy entry on the sale (the Sales sheet's
   auto-add becomes the policy itself), renewal terms, cancellations.
   Cutover test: Premium Sold, HH Sold and the Renewals rates identical.
8. **Retire AgencyZoom**: final import of everything changed since the first
   load, read-only month, cancel.

Phase 1 is one session's work; 2 and 3 are a week or two each; 4 to 7 are
the bulk, two to four months; 8 is a month of running both. Hosting is
under $20 a month (Workers Paid $5, D1 and R2 in cents); the Anthropic,
Deepgram, RingCentral and Insightful bills do not change.

## What was built on day one (2026-10-06)

- `site/crm/migrations/0001_init.sql` -- the schema (Cloudflare D1 is
  SQLite). Every table's comment says what it is and which AgencyZoom codes
  it keeps.
- `site/crm.js` -- the data layer and API, `/api/crm/...`, routed from
  `site/worker.js` behind the same Access gate, open to every active person
  in staff.json. Lists page from 0 like AgencyZoom's; every write lands in
  `events` with the Access email. A lead's `move` writes the structured
  move AND the `MOVE_STAGE` note `pipelines.parse_move` reads; `sold` sets
  status 2, `soldDate` and converts the lead to a household; a task's
  `complete` leaves the TASK note; an SR's `complete` takes one of Frank's
  resolutions only. Without the D1 binding every call answers 503 and
  nothing else on the board changes.
- `site/crm.test.mjs` -- `node --test site/crm.test.mjs`: the whole life of
  a lead (create, note, move, quote, sold, policy, premium change with its
  audit event), tasks, SRs, search by number, paging and the gate, on a real
  SQLite dressed as D1.
- `crm_import.py` -- the first load from the files the nightly already
  saves under `data/` (leads, customers, policies, household map, stages,
  tasks, SRs, notes; stage moves from the MOVE_STAGE notes), AgencyZoom's
  ids kept. `--sqlite` builds a local copy to check; `--sql` writes the
  files for `wrangler d1 execute`.
- `wrangler.jsonc` -- the D1 binding, commented, with the turn-on steps.

## Turning it on

1. `wrangler d1 create pantheon-crm`; paste the id into wrangler.jsonc's
   `d1_databases` block and uncomment it; deploy (Workers Builds does it on
   merge).
2. `wrangler d1 migrations apply pantheon-crm --remote`.
3. On the nightly's machine, where `data/` holds the corpus:
   `python3 crm_import.py --sqlite out/crm_import.db` to see the counts,
   then `python3 crm_import.py --sql out/crm_import` and apply each file
   with `wrangler d1 execute pantheon-crm --remote --file=...`.
4. `GET /api/crm/lookups` from the board (signed in) answers with the lead
   sources, pipelines, stages, resolutions, carriers and staff.

## Decisions still Frank's

- **Which vendors push leads and how** (phase 5): each needs a webhook URL
  or an email we can parse. The list is `lead_sources.py`'s generated
  group; the delivery method is in each vendor's dashboard.
- **Texting**: through RingCentral's SMS API on each producer's own line
  (what AgencyZoom does now, on the service lines at least), or a dedicated
  number. Affects phase 4 and the Texts & Emails page.
- **Stage names**: keep AgencyZoom's as they are (the import does) or
  simplify when the producers move over. `pipelines.py` is the one place
  the meanings live.
- **Who may delete**: nothing in the CRM deletes today (status codes and the
  audit trail instead). A `crm_admin` board key in staff.json is the
  natural place if that changes.
- **The AgencyZoom contract**: its term sets the earliest cutover date.
