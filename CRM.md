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
SR categories. Pantheon's CRM keeps **Frank's own lists** as the real ones
and a **map from every AgencyZoom id** onto one of his entries; AgencyZoom's
ids stay on every record while it is the record, and the pages read through
the map. **Built 2026-10-06** from Frank's decisions that day.

**How it works.** `crm_lists.py` holds the lists (`SOURCES`, `PIPELINES` +
`STAGES`, `SERVICE`) and the placement rules, by NAME, so an AgencyZoom
entry is placed the night it first appears (`crm_import.build` calls
`add_rows`; one no rule knows is **Unsorted** on the Lists page). Migration
0004 adds `lists` (kind source / pipeline / stage / service; the one
`detail_label` kept beside an entry; a `meaning` line) and `list_map` (kind
source / workflow / stage / category, az_id -> list_id, `detail`,
`placed_by`). Every row goes INSERT OR IGNORE, so a name or a placement set
on the page is never undone by the nightly. The Worker (`site/crm.js`) reads
each record through the map: a lead's `sourceName` / `sourceDetail` /
`pipelineName` / `stageName`, a policy's `sourceName`, an SR's
`pipelineName` / `pipelineDetail` -- beside the untouched AgencyZoom-shaped
fields. `GET /api/crm/lists` is the page's read (counts per entry), `POST
/api/crm/lists` adds / edits / reorders an entry, `POST /api/crm/lists/place`
places an AgencyZoom id. **Sales Center > Lists** (`site/public/lists.js`,
the same `crm` gate) is where Frank works them. `python3 crm_lists.py
--discover` lists every AgencyZoom entry with its place from the saved files.

**Lead sources, 97 -> 17.** The partner, vendor or staff member is a FIELD on
the source, not a source of its own.

| Frank's source | Field | AgencyZoom sources placed there |
|---|---|---|
| Winback | | Winback, Winback by AgencyZoom |
| Internet lead | Vendor | Smart Financial (+ Live Transfer), SureQuote, Mav AI, Alpha Media, Enterprise, Arizona Insurance Reports (both), Hometown Quotes, Facebook (purchased, per the 09-24 rule) |
| **Call-in / Walk-in** | **How they found us** | Call-In (Called), Walk-In (Walked in), Google / Found us on Google (Google), Farmers.com -- Frank: "it should be callin/walk in, with a field on how they found us" |
| Cross-sell: Home no Auto | | Home no Auto |
| Cross-sell: Auto no Home | | Auto no Home |
| Cross-sell: Life | | Life Cross Sell |
| Cross-sell: Umbrella / other | Product | Umbrella, the plain Cross Sell -- the four lines **stay apart** (Frank) |
| Existing client, new purchase | | Existing client purchased a new |
| Customer referral | Referred by | Existing Customer Referral, Referral by AgencyZoom, Francisco Flores |
| Lender referral | Partner | every "Name at Company" source as "Company (Name)", Mariah Serna, Lender no longer in the Industry, Mortgage Lenders |
| Personal network | Staff member | the staff-name sources (Frank Flores, Lorena Gonzalez, Mike Olvera ...), each as that person |
| Social media | Network | Instagram, LinkedIn |
| Cold / event | Event or list | Cold lead, FIG QNT, Crane Benefit Fair, UTV Expo, Old MVP Leads |
| Commercial lead | Generator | Leo, Work Comp, District / Agent Promoter Comm Leads, RCFBH Group Life, Kraft Lake |
| BOB, Rewrite | | kept as the two not-a-sale sources |
| Other | What it was | X (both), Other lead, Automation Team |
| Unsorted | | Source 9308229 (an id with no name), and anything new no rule knows |

**Sales pipelines, 16 -> 5**, each with Frank's stages in order:

| Pipeline | Stages | AgencyZoom pipelines placed there |
|---|---|---|
| New Business | New, 1st / 2nd / 3rd Cycle, Contacted, In Progress, Ready to Present, Quotes Presented, Lender Referral, FSD (Pending Bind), **IL Interested, Transfer Pending** (not ours, "leave ... for now" -- Frank) | 1 Pipeline, Pipeline (junk), Tello's Leads, Test Test, x1 Pipeline Refreshed, **AZ Sun Quote Tracker** ("New business" -- Frank), 1. Personal Lines Marketing, Mortgage Lenders |
| Quotes Not Closed | 1st / 2nd / 3rd Cycle, Contacted, Quoted | 1-1 QNC, x1-1 QNC Refreshed |
| Not Quoted | the same five | 1-2 Leads Not Quoted |
| Life | New, Contacted, Quoted, Applications, Med. Records Needed, Approved | Life Pipeline |
| Commercial | New, 1st / 2nd / 3rd Cycle, Contacted, Applications, Underwriting, Set Present Appt, Quoted, Bind | Frankie's Commercial Pipeline, 2 Commercial Pipeline, 2-1 Commercial QNC, 2-2 Commercial Leads Not Quoted |

An AgencyZoom stage is placed under the stage of the same name in the
pipeline its workflow went to ("Quoted" = Quotes Presented, "Contacted" =
Contacted, In Progress, "New 1st Cycle" = 1st Cycle); a stage name no
pipeline has is Unsorted. Service workflows' stages are not mapped (only
Late Payments is worked by stage; the Service Center reads AgencyZoom's).

**Service pipelines = SR categories, 43 categories + 8 workflows -> 7**
(Frank: "the category is really the service pipeline it goes into"):

| Service pipeline | Field | AgencyZoom workflows | AgencyZoom categories |
|---|---|---|---|
| Billing | Payment | Late Payments, Reinstatement | Monthly (x3), NOC: Monthly EFT / Monthly, Mortgagee Bill |
| Contingencies | | Contingencies / Missing Documents | Missing Docs, address verification, UW Request For Driver License Number |
| Personal Renewals | Carrier | Personal Renewals, Other 30 day Renewals (Bristol West) | Renewals: Personal, Personal Renewal, VIP Personal Renewal, Non Renewals |
| Personal Endorsements | Change | Service Pipeline | Personal Policy Change, add / remove a car, add a driver, change address, deductible, Coverage Change, +/- Driver / Insured, Add discount, Client Cancelling, Pending Cancellation, COI, Question, Inspection(s), Remarket, Carrier Request |
| Commercial Renewals | | Commercial Renewals | Renewals: Commercial, Renewals: Surplus |
| Commercial Endorsements | | (none: a commercial change is a Service Pipeline SR on a commercial household, commercial.py's rule, until cutover files them here) | Commercial Endorsement |
| Claims | Claim type | Claim | Claim: Auto / Home / Life / Specialty / Commercial / Work Comp (the type is the field; Commercial and Work Comp stay Cerberus's by claims.py) |
| *follows the workflow* | | | General (1,219 SRs -- "they are all of them": the workflow says which), UNASSIGNED, Category 81878 |

An SR lands on the pipeline its category is placed under; a category that
follows the workflow lands where the SR's AgencyZoom workflow is placed.

**Still to come**: the Digest, Apollo and Coeus read `lead_sources.py`'s
groups and `pipelines.py` today, both of which the lists agree with; they
move to the lists when the leads and SRs themselves do (phases 3 and 7).
The lists are Flores's; another agency writes its own `crm_lists.py` entries
(NEW_AGENCY.md).

## Workflows (Frank, 2026-10-07: "how do we start building our own workflows? or display what we currently have so we can adjust or change as needed")

A workflow has two layers. The **pipeline** -- which stages a lead or SR
moves through -- is Frank's already (the Lists page). The **automation** --
what happens on its own when something changes: the text that goes out
when a SureQuote lead lands, the task set for whoever is up, the second
text two days later, the Smart-Cycle after three unanswered cycles, the
shot-clock task on a renewal -- is what AgencyZoom still runs. Built in
two steps:

**1. What AgencyZoom runs today (built 2026-10-07).** AgencyZoom's API does
not hand out its rules (api.agencyzoom.com's OpenAPI spec, checked
2026-10-06: pipelines and stages, no rules or drips), so `az_automations.py`
reads them back from the evidence on the leads: every automated TEXT
carries `attr.triggerRuleId`; drip EMAILs carry a template subject
(`messages.TEMPLATE_SUBJECTS`, plus any subject sent to 5+ leads with no
attachment); a TASK wording repeated on 5+ leads (the nightly's task files'
titles and the TASK notes); every MOVE_STAGE into Smart-Cycle, back into a
cycle stage or to Dead, with who made it (a staff name is a person, anything
else the automation). Each rule: its wording with the lead's and the staff's
names, numbers, links and dates blanked (`_blank`; nothing personal
travels), when it fires (the stage the lead sat in -- from its move history,
`_where` -- and the days since entering it, the days since the lead arrived,
the peak hour), the sources, how many leads in the last 90 days, how many
wrote back within 2 days (3 for email), opt-outs (STOP), opens and bounces.
`--fetch` restores the newest corpus snapshot from R2 and downloads the
notes of every lead active in the window, paced like `messages.py`'s
backfill (~5,000 leads, about half an hour; from the nightly's environment,
never the Worker's address); `--build --publish` writes
`data/az_automations.json` and R2 `crm/automations.json`. The Worker serves
it at `GET /api/crm/automations` with Frank's marks (`crm/automation_marks.json`;
`POST /api/crm/automations/mark` {key, mark keep|change|drop|null, note}),
same `crm` gate. **Sales Center > Workflows** (`site/public/workflows.js`):
Texts / Emails / Tasks / Smart-Cycle tabs, a card per rule with Keep /
Change / Drop and a note. The marks are the brief for step 2. Rerun the
read whenever the picture should refresh; it is not on the nightly.

**2. Pantheon's own rules (next).** A rule reads as a sentence: **when** a
lead arrives on a source / enters a stage / sits N days with no activity /
does not reply N hours after a text / is marked sold, or an SR opens in a
pipeline / sits N days open / a renewal is N days out / a call is missed,
**then** text (template with {first}, {producer} ...), email, a task for
someone due in N, move stage, Smart-Cycle for N days, notify, stop the
other rules on that lead. Rules and their runs live in D1
(`workflow_rules`, `rule_runs`), the Worker's one-minute cron evaluates
them. **Draft mode first**: until the leads live in the CRM the mirror is
only as fresh as the last hourly checkpoint, and sending needs phase 4's
RingCentral SMS and mail senders -- so the first version shows what each
rule WOULD have fired on today's leads beside what AgencyZoom did (the
agree-on-a-published-day test), tasks go live first (the CRM owns them),
texts and emails switch on with their senders.

## Decisions still Frank's

- **Which vendors push leads and how** (phase 5): each needs a webhook URL
  or an email we can parse. The list is `lead_sources.py`'s generated
  group; the delivery method is in each vendor's dashboard.
- **Texting**: through RingCentral's SMS API on each producer's own line
  (what AgencyZoom does now, on the service lines at least), or a dedicated
  number. Affects phase 4 and the Texts & Emails page.
- **Stage names**: decided 2026-10-06 -- Frank's stages are in
  `crm_lists.STAGES` and on the Lists page; `pipelines.py` still carries
  the meanings Apollo reads.
- **Who may delete**: nothing in the CRM deletes today (status codes and the
  audit trail instead). A `crm_admin` board key in staff.json is the
  natural place if that changes.
- **The AgencyZoom contract**: its term sets the earliest cutover date.
