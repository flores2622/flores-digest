# Running Pantheon for another agency

Everything that is this agency's -- its people, its clock, its AgencyZoom
account's numbers, its lead sources, its name and carrier, its goals, its
commission sheet, the words its calls are judged by -- lives in a handful
of files at the root of this repository. The code reads them and nothing
else; the rules (what a sale is, how a call is coached, how a tier is
judged) are the same for every agency. To run Pantheon for a new agency,
fill in these files, run one check, and deploy.

Put the agency's files in `agencies/<key>/` (the four JSON files and a
`carrier/` folder) and set `PANTHEON_AGENCY=<key>` for every command below;
`agencies/copperline/` is a complete fictional example to copy. Flores's own
files stay at the repository root, read when the variable is unset.

`PANTHEON_AGENCY=<key> python3 agency_check.py --fix` rewrites every generated file and checks all
of them. Run it after every change below; it must say "every setup file
checks out" before anything is deployed.

## 1. The people and the agency -- `staff.json`

`agency`: the agency's `name`, `short_name` (what the front desk says:
"thank you for calling Flores"), `carrier` (the one it writes for, as
said on calls), `carriers_spoken` (every carrier name said on calls, for
the transcriber), `place` (the state or city, as Role Play prospects would
say it), `also_known_as` (other ways people say the agency's name),
`misheard_as` (how transcripts garble it), `timezone` (an IANA name),
`sender` (the nightly email's From) and `contact` (the address in every
API client's User-Agent).

`people`: one entry each, with `email`, RingCentral `ext` and `rc_id`,
AgencyZoom `az_id`, `producer` (true when their numbers are counted),
`digest` (which nightly email: `ops` or `staff`), `service` (role,
playbook role and order, for the service team), `tags`, `board`, `color`,
`email_dot`, `handle` and `heard_as` (how transcripts spell their first
name). `staff.py`'s docstring says what every tag and board key means.
Former staff stay, with `status: former`, since their names are still lead
sources and SR assignees.

`rotation`, `commission_units` and `commission` (the tier names, rates,
monthly minimums per schedule and the additional pay), `sales_teams` and
`orders` (the display orders) round it out.

Then `python3 staff.py --write-js` (the Worker's and the page's copies) and
`python3 staff.py --crons`, which prints the Worker's cron lines for the
zone to paste into `wrangler.jsonc`'s `triggers.crons`.

## 2. The AgencyZoom account's numbers -- `agencyzoom.json`

AgencyZoom hands every account its own ids. With the account's credentials
in `secrets/`, `python3 agencyzoom.py --discover` reads its workflows,
service categories and resolutions (and, after a nightly pull, its
carriers off the policy corpus) and prints each beside what the file says,
marking NEW and GONE. Fill in:

- `workflows.junk` (a pipeline leads are dumped into by mistake, if any),
  `workflows.claim`, `workflows.commercial_renewals`, and
  `workflows.service` -- which workflow name(s) each Service Center
  pipeline key covers -- with `service_labels` for what the board calls
  them;
- `claim_categories` and which are `commercial_claim_categories`;
- `resolutions`: every resolution's name (`labels`), which renewal outcome
  each counts as (`outcome_by_id`, keys from `service_retention.OUTCOMES`),
  any id not to trust before a date (`valid_from`), and the ones that say
  the outcome on their own per pipeline (`trusted_by_pipeline`);
- `carriers` (carrier id -> the short name the Sales sheet uses),
  `product_names` (how the sheet names a policy: ordered rules on carrier
  and policy type), `renewal_ff_carriers`;
- `email_template_subjects` (the account's drip email subjects, lower-cased,
  the lead's first name taken off the front) and `test_lead_ids`.

## 3. The lead sources -- `lead_sources.json`

After a nightly pull, `python3 lead_sources.py --discover` lists every
source in the lead corpus by group with the unclassified ones first.
`sources` maps each name (lower-cased, trimmed) to a group from
`lead_sources.GROUPS` -- cross_sell, existing_new_purchase, generated,
winback, referral, social_media, center_of_influence, inbound, cold,
one_off, commercial, not_a_sale. Every agency needs at least one
`not_a_sale` source (the CRM housekeeping label policies that were not
sold carry). `cross_sell_product` says what each cross-sell source sells;
`source_backstory` gives a source its own Role Play backstory where the
group's is wrong; `speed_sources` are the internet sources Speed to Dial
times; `group_who` is the agency's own wording of who a group's leads are,
naming its sources, for Apollo and the board. A staff member's name as a source needs no entry.

## 4. The goals -- `goals.json`

The green / yellow pair for every metric, the straight-count metrics that
scale for the team row, the life goal, the reply-speed goal, the week's
premium goal and the Coach AI bar ranges. The guides in
`site/public/blueprints.js` still say the numbers in words; change them
too.

## 5. The coaching documents -- `coaching/carrier/<carrier>/`

`coaching/METHODOLOGY.md` and `coaching/TRAINING.md` are rendered from
`coaching/src/` by `python3 coaching_text.py --write`. The carrier layer is
a folder named after `agency.carrier` (lower-cased): `carrier.json` (the
name, its possessive, how transcripts mishear it, `heard_as_regex` for
Whisper, the quoting system, the website) and the occupation-discount text
(`occupations_methodology.md`, `occupations_training.md`). Copy the
Farmers folder and rewrite it. The agency layer comes from `staff.json`.

## 6. Deployment

- `secrets/*.env`: `RC_CLIENT_ID`, `RC_CLIENT_SECRET`, `RC_SERVER_URL`,
  `RC_JWT`, `AZ_USERNAME`, `AZ_PASSWORD`, `INSIGHTFUL_TOKEN`,
  `RESEND_API_KEY`, `DEEPGRAM_API_KEY`, `ANTHROPIC_API_KEY`, and
  `HEALTHCHECK_URL` in the cloud environment (README.md).
- `wrangler.jsonc`: the Worker's `name`, the R2 `bucket_name`,
  `ACCESS_TEAM_DOMAIN` and `ACCESS_AUD` (the agency's Cloudflare Access
  application), and the cron lines from `python3 staff.py --crons`. The
  Worker's secrets (`RC_*`, `AZ_*`, `INSIGHTFUL_TOKEN`, `DEEPGRAM_API_KEY`,
  `ANTHROPIC_API_KEY`) are set in Cloudflare.
- The nightly routine: `CRON_TZ=<agency.timezone> 55 8-17 * * 1-5`
  (CLAUDE.md, "THE RUN STARTS AT 5:35 PM").

## 7. The CRM's own lists -- `crm_lists.py`

Pantheon's CRM (CRM.md) keeps the agency's OWN lead sources, sales pipelines
with their stages, and service pipelines (which are the SR categories), and
maps every AgencyZoom id onto them by name. `crm_lists.py`'s `SOURCES`,
`PIPELINES` / `STAGES` and `SERVICE` are Flores's lists and its placement
rules name Flores's AgencyZoom entries (Call-In, Farmers.com, AZ Sun ...);
another agency writes its own and runs `python3 crm_lists.py --discover`
over its saved files to see what lands Unsorted. `--check` validates the
lists.

## What is still Flores's in words

The editions' names (The Flores Post, The Flores Feed, KFLR The Close,
FLRS 500) and the Feed's handles, the guides' plain words in
`site/public/blueprints.js`, the `Flores_ANTHROPIC_API_KEY` environment
name, and the example calls in the coaching documents. None of them
changes a figure.
