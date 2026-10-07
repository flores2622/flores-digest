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
| Tasks per producer | `tasks` -- built, API live, **Sales Center > Tasks page built** |
| Service requests, workflows, categories, resolutions | `service_requests`, `workflows`, `service_categories`, `resolutions` -- built, API live |
| Who changed what (AgencyZoom has no audit trail) | `events` -- every write, who, before and after |
| The screens the producers and service team type into all day | Tasks built; leads, households, SRs and policies **not built** -- phases 3 on |
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
   AgencyZoom). **The Tasks page is built** (2026-10-06, `site/public/
   tasks.js`: due today / overdue / next 7 days / done today / all open, per
   person, Done with a comment, Reschedule, New task on a lead or household,
   the lead's coaching card a click away). **The mirror is built**
   (`crm_sync.py`, same day): every checkpoint and the nightly copy what
   they saved from AgencyZoom into the database, so the Tasks page shows the
   real book from the first run with `CF_API_TOKEN` set. Still to do:
   `missed_call_tasks.create` writing to `/api/crm/tasks` instead of
   AgencyZoom, and `az_tasks.audit` / `live.js taskCompletion` reading from
   it. Cutover test: Task Completion identical both ways on a day run in
   parallel.
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
- `wrangler.jsonc` -- the D1 binding (the database was created and the
  schema applied the same day).
- `crm_sync.py` -- the AgencyZoom mirror, run by every checkpoint and the
  nightly; only what changed, fingerprints in R2, upserts that never touch a
  row Pantheon made. Migrations 0002 (one stage move per note) and 0003
  (lead source names repeat) came out of the first real build.

## Who sees it

Frank alone, until further notice (2026-10-06): staff.json's `crm` board
key. Add it to a person's `board` (and run `python3 staff.py --write-js`) to
let them in; the Tasks page then appears in their Sales Center menu.

## Turning it on

1. Done 2026-10-06: the D1 database `pantheon-crm` was created in the
   account (WNAM, id in wrangler.jsonc) and `0001_init.sql` applied; the
   binding deploys with the next merge (Workers Builds). A later schema
   change is a new file in `site/crm/migrations/`, applied with
   `wrangler d1 migrations apply pantheon-crm --remote`.
2. **The load is the nightly's own job now** (`crm_sync.py`, step 1 of
   phase 2, built 2026-10-06): every checkpoint and the nightly mirror the
   files they just saved into the database through Cloudflare's D1 API,
   sending only what changed. It needs one variable in the cloud
   environment beside the R2 keys: `CF_API_TOKEN`, a Cloudflare API token
   with D1 edit. The first run with it loads everything (37,248 rows on the
   2026-10-06 snapshot, a few minutes); every run after sends the day's
   changes. `python3 crm_import.py --sql out/crm_import` still writes the
   files for `wrangler d1 execute` if a load by hand is ever wanted.
3. `GET /api/crm/lookups` from the board (signed in) answers with the lead
   sources, pipelines, stages, resolutions, carriers and staff, and Sales
   Center > Tasks shows the mirrored tasks.

## Consolidating the lists (Frank, 2026-10-06: "i want to consolidate lead sources, pipelines, service request categories. I want to customize and rebuild")

AgencyZoom's lists grew by accretion: 97 lead sources, 16 sales pipelines, 43
SR categories. Pantheon's CRM gets Frank's own lists, and AgencyZoom's ids
are mapped onto them while AgencyZoom is still the record.

**How it works.** The CRM keeps Frank's lists as the real ones (lead sources,
pipelines with their stages, SR categories) and a map from every AgencyZoom
id to one of his entries. The mirror keeps writing AgencyZoom's ids on each
record, and the pages, the Digest and Apollo read through the map, so a lead
sourced "Nellie Robertson at Guild Mortgage" in AgencyZoom shows as **Lender
referral · Guild Mortgage (Nellie Robertson)** in Pantheon. An AgencyZoom id
nobody has placed lands in an **Unsorted** bucket on the page for Frank to
drag into place. The mirror adds a lookup the first time AgencyZoom shows it
and never rewrites one (from 2026-10-06), so a name Frank sets stays. Nothing
changes in AgencyZoom itself; at cutover, Frank's lists simply are the lists.
`lead_sources.py` and `pipelines.py` already carry the agency's meaning for
most of these -- the proposal below starts from them and from the counts in
the loaded database (leads ever / in the last 90 days; SRs ever / 90 days).

**Lead sources, 97 -> 15** (the partner, vendor or staff member becomes a
field on the source, not a source of its own):

| Proposed | AgencyZoom sources folded in | Leads ever / 90d |
|---|---|---|
| Winback | Winback, Winback by AgencyZoom | 2,084 / 197 |
| Internet lead (vendor kept as a field) | Smart Financial (1,918 / 0), Smart Financial Live Transfer, SureQuote (517 / 414), Mav AI (282 / 282), Alpha Media (307 / 136), Enterprise (207 / 5), Arizona Insurance Reports x2 (620 / 0), Hometown Quotes, Old MVP Leads | 3,897 / 838 |
| Call-in | Call-In | 884 / 39 |
| Walk-in | Walk-In | 268 / 13 |
| Found us online | Google, Farmers.com | 524 / 41 |
| Cross-sell: Home no Auto | Home no Auto | 768 / 144 |
| Cross-sell: Auto no Home | Auto no Home | 200 / 66 |
| Cross-sell: Life | Life Cross Sell | 181 / 38 |
| Cross-sell: Umbrella / other | Umbrella, Cross Sell (the plain one, 762 / 24, retired for new leads) | 771 / 25 |
| Existing client, new purchase | Existing client purchased a new | 41 / 4 |
| Customer referral | Existing Customer Referral, Referral by AgencyZoom, Francisco Flores | 434 / 32 |
| Lender referral (partner kept as a field) | the 30 "<name> at <lender>" sources, Mortgage Lenders | ~1,000 / 20 |
| Personal network (staff member kept as a field) | the 16 staff-name sources (Frank Flores 471 / 4 the largest) | ~660 / 14 |
| Social media | Facebook, Instagram, LinkedIn | 66 / 41 |
| Cold / event | Cold lead, FIG QNT, Crane Benefit Fair, UTV Expo | 104 / 56 |
| Commercial lead (Cerberus) | Leo, Work Comp, District Comm Leads, Agent Promoter Comm Leads, RCFBH Group Life, Kraft Lake | 187 / 0 |
| Not a sale: BOB / Rewrite | kept as two, for the service bookkeeping | 150 / 6 |
| Other | X, X, Other lead, Lender no longer in the Industry, Automation Team | 23 / 5 |

**Sales pipelines, 16 -> 5** (stages in Frank's order; IL Interested and
Transfer Pending go, since they were never agency stages):

| Proposed | Stages | From | Open leads now |
|---|---|---|---|
| New Business | New, Contacted / In Progress, Ready to Present, Quotes Presented, Lender Referral (holding), FSD (Pending Bind) | 1 Pipeline (593), Pipeline (2, junk), Tello's Leads (2), Test Test (1), x1 Pipeline Refreshed | 598 |
| Quotes Not Closed | 1st Cycle, 2nd Cycle, 3rd Cycle, Contacted, Quoted | 1-1 QNC (57), x1-1 QNC Refreshed | 57 |
| Not Quoted | 1st Cycle, 2nd Cycle, 3rd Cycle, Contacted, Quoted | 1-2 Leads Not Quoted | 212 |
| Life | New, Contacted, Quoted, Applications, Med. Records Needed, Approved | Life Pipeline | 27 |
| Commercial (Cerberus) | New, Contacted, Applications, Underwriting, Set Present Appt, Quoted, Bind; cycles for QNC / not quoted | Frankie's Commercial Pipeline (95), 2 Commercial Pipeline (74), 2-1 Commercial QNC, 2-2 Commercial Leads Not Quoted (6), AZ Sun Quote Tracker (126) | 301 |
| retired | | 1. Personal Lines Marketing (0 leads), Mortgage Lenders (8 -- partners become the Lender referral field) | |

**Service workflows, 8 -> 7**: Personal Renewals (3,757 SRs), Bristol West
Renewals (Other 30 day Renewals, 1,028), Service (1,572), Late Payments
(909, taking Reinstatement's 2 -- it already has a Cancelled/Reinstate
stage), Contingencies (271), Commercial Renewals (105, Cerberus), Claims (2).

**SR categories, 43 -> 11** (a claim's type and a payment's kind become a
field on the category):

| Proposed | AgencyZoom categories folded in | SRs ever / 90d |
|---|---|---|
| Renewal | Renewals: Personal, Personal Renewal, VIP Personal Renewal, Non Renewals | 4,881 / 1,150 |
| Commercial renewal | Renewals: Commercial, Renewals: Surplus | 105 / 24 |
| Payment | Monthly x3, NOC: Monthly EFT, NOC: Monthly x2, Mortgagee Bill | 914 / 190 |
| Missing documents | Missing Docs, Missing the address verification documentation, UW Request For Driver License Number | 275 / 73 |
| Policy change | Personal Policy Change, requested to add / remove a car, add a driver, change your address, increase the deductible, Coverage Change, +/- Driver, +/- Insured, Add discount, Commercial Endorsement | 146 / 6 |
| Cancellation | Service: Client Cancelling, Service: Pending Cancellation | 77 / 11 |
| Certificate (COI) | Service: COI | 18 / 0 |
| Claim (type kept as a field) | Claim: Auto / Home / Life / Specialty / Commercial / Work Comp | 7 / 0 |
| Question / general | General (1,219 / 211 -- the catch-all; worth a look at what lands there), Service: Question, UNASSIGNED, Category 81878 | 1,223 / 211 |
| Inspection | Service: Inspection, Inspections | 0 |
| Remarket / carrier request | Service: Remarket, Service: Carrier Request | 0 |

What Frank decides: the names, which of the Cross-sell lines stay separate,
whether Call-in and Walk-in stay apart (the rotation treats them alike),
whether AZ Sun belongs under Commercial, and what "General" should become.
Then the build: the three lists and the map as tables, a Lists page under
the CRM to edit them and sort the Unsorted bucket, and the Digest, Apollo
and Coeus reading the consolidated names.

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
