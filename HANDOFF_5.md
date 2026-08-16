# Flores Insurance — Daily Reports: HANDOFF 5

**Read this first. It supersedes HANDOFF_4.md (2026-08-14).**
Prepared 2026-08-14. Attach this file, and the code archive, to a NEW Cowork session.

**What changed since HANDOFF_4:** the Insightful integration — the item HANDOFF_4
called "the main remaining work" — is **built and verified**. The utilization
formula is solved and reproduces Insightful's published percentages exactly.
The send-time question is **answered and decided**. Four API traps that were
costing sessions are now documented with their exact failure signatures.
Everything else in HANDOFF_4 was correct and is carried forward.

---

## 0. First actions, in order

### 0a. Verify egress

Confirmed working 2026-08-14 with the org on **All domains**:

```bash
for h in app.insightful.io app.agencyzoom.com platform.ringcentral.com api.resend.com api.traq.ai; do
  curl -sS -o /dev/null -w "$h -> %{http_code}\n" --max-time 12 "https://$h/"
done
```

Observed: `app.insightful.io` **200**, `app.agencyzoom.com` **302**,
`platform.ringcentral.com` **404**, `api.resend.com` **200**, `api.traq.ai` **404**.
All five hosts reachable. **Do not ask Frank to allowlist anything.**

If a host ever returns 000, read the gateway status before drawing conclusions —
**403** = not allowlisted; **502 / "upstream dial failed"** = allowed but the host
is wrong or dead, and restarting the session will not help:

```bash
curl -sS --noproxy '*' "http://127.0.0.1:${https_proxy##*:}/__agentproxy/status"
```

### 0b. Ask Frank to re-paste two credentials

**The container is ephemeral — every file and secret is gone between sessions.**
RingCentral and AgencyZoom credentials are in §3 of this document and can be used
directly. The two that are *not* written down, by design, are:

1. **Insightful API token** — a JWT, `userType: api`, PROD audience, no practical
   expiry. Insightful → API page → create and name a token → generate. Shown once.
2. **Resend API key** — starts `re_`. resend.com → API keys → Create API key
   (Sending access).

Store with `umask 077` and `chmod 600`. Never echo them back.

### 0c. Rebuild the working files

The code archive accompanying this handoff contains everything built so far.
Unpack it, drop the two secrets into `secrets/`, and run `verify_insightful.py`
— it should print **27/27 assertions passed**. §8 lists what still needs writing.

---

## 1. What the system produces

Two daily HTML emails, built fresh from live data. Single self-contained HTML
files, inline CSS, table-based layout for Outlook/Gmail.

1. **Operations email** — Daily Sales Digest + Call Detail & Task Completion Audit
   combined in one body. **6:30 PM Arizona** (changed from 6:00 — see §2e).
   Recipients: frank@, francisco@, veronica@, amanda@.
2. **Staff email** — Sales Digest only. 8:00 AM Arizona. Recipients: crystal@,
   lorena@, mike@, debbie@.

Both carry **two attachments**: `Notes_and_Methodology_<date>.html` and
`Recontact_Detail_<date>.html`.

Arizona is **UTC-7, never DST**. 6:30 PM AZ = 01:30 UTC next day; 8:00 AM AZ = 15:00 UTC.

---

## 2. THE INSIGHTFUL JOB — DONE

### 2a. The host

| | |
|---|---|
| **Base URL** | `https://app.insightful.io/api/v1/` |
| **Auth** | `Authorization: Bearer <token>` |
| **Rate limit** | 200 requests/minute per organization; 429 on exceed |

The API is served from the **same host as the web app**; `api` is in the **path**,
not the hostname. `api.insightful.io` resolves nowhere. **Ignore
`dlthub.com/context/source/insightful`** — it asserts `api.insightful.io` and
`/v2/employees`; both wrong.

**Endpoint surface, probed live 2026-08-14** (401 = exists, 404 = does not):

| Exists (401) | Does not exist (404) |
|---|---|
| `employee`, `team`, `project`, `task` | `teamcategory`, `shift`, `activity` |
| `organization`, `me` | `analytics/utilization`, `analytics/employee` |
| `analytics/project-time`, `analytics/window` | `analytics/team`, `analytics/summary` |
| `analytics/app`, `analytics/productivity` | `analytics/time-and-activity` |
| `analytics/screenshot`, `analytics/attendance` | `analytics/category`, `analytics/app-usage` |
| `analytics/activity` | `settings/productivity` |

**There is no `analytics/utilization` endpoint.** Utilization is assembled.

### 2b. THE FORMULA — verified, do not relitigate

```
utilization = analytics/productivity[productivity == 1].usage
              / analytics/attendance[employee].duration
```

Both are **milliseconds**. Compute at full ms precision; round only for display.
Query params: `start`, `end` (epoch ms for the Arizona day), `timezone=America/Phoenix`,
and `employeeId` for the per-person productivity breakdown.

`productivity` codes: **1 = productive, 0 = neutral, 2 = unproductive, 3 = unreviewed**.

Reproduces the 2026-08-07 published figures:

| Person | Calculated | Published | Δ |
|---|---|---|---|
| Crystal Mango | 86.21% | 86.21% | exact |
| Mike Olvera | 91.72% | 91.72% | exact |
| Lorena Gonzalez | 80.25% | 80.25% | exact |
| Amanda Torricellas | 79.59% | 79.59% | exact |
| Debbie Aguilera | 91.95% | 91.89% | +0.06 |
| **Team weighted** | **87.54%** | **87.52%** | +0.02 |

**Debbie is the one non-match.** Her attendance row reads 07:35:28 against the
07:32 in the email, with productive time high by the same ~3.5 min, so the ratio
barely moves. No unusual flags (`isClockOutAssumed` false, `inProgressShifts` 0).
Most likely her shift was edited after the 2026-08-08 email was generated.
0.06pp crosses no threshold — both are green. **Accepted drift, not a bug.**

The old "recompute from rounded minutes" approach is what produced 85.6% for
Crystal against a published 86.21%. Do not go back to it.

**Team weighted uses MINUTE-rounded values**, which is how Insightful builds its
own Team number: `sum(productive_min) / sum(total_min)`.
2026-08-07: 1620 / 1851 = 87.52%.

**Scope of the team figure:** Frank's rule is "all users except Amanda", but
Coral and Sarahi are excluded from every calculation until 2026-08-28, so they
drop out too. This is arithmetically confirmed: Insightful's own published
1620m/1851m is exactly Crystal + Mike + Debbie + Lorena. Coral is **not** in it.

### 2c. Roster findings — the §6 decision, answered early

- **Insightful holds DUPLICATE employee records.** Crystal and Mike each appear
  twice, one copy deactivated. **Always resolve to `deactivated == 0`.** Querying
  the deactivated id returns `[]`, not an error — it looks like a person with no
  data rather than a wrong id. `verify_insightful.py` guards this.
- **Coral Barwick IS fully tracked** and produces a real utilization figure every
  day — 70.72% (Aug 7), 80.06% (Aug 11), 83.81% (Aug 12), 67.50% (Aug 13). The
  daily email was simply truncating her off at the top-five boundary.
- **Francisco Flores** holds an active licence but has **no attendance rows** —
  licensed, not tracked. Report him as absent, never as 0%; a zero reads as a
  terrible day rather than as no data.
- **Sarahi Chin has no Insightful record at all.** Not merely untracked — she
  does not exist in the system. A licence must be assigned before she can ever
  appear, whatever Frank decides on the 28th.

**Frank's decisions, 2026-08-14:** Coral stays a placeholder until 2026-08-28
(the audit notes her data is confirmed available, so the 28th is a straight
yes/no). Sarahi stays a placeholder **and the report flags the missing licence**
so it can be assigned.

### 2d. Send time — SETTLED at 6:30 PM Arizona

HANDOFF_4 assumed the 15:01-UTC publication lag made same-day utilization
impossible. **That lag applies only to Insightful's email.** The API carries the
in-progress Arizona day live — verified 2026-08-13 at 22:19 AZ, which already
returned complete attendance for all six tracked people.

The real constraint is people still being clocked in at send time. Share of each
counted producer's tracked day still ahead of them at each cutoff, across
Aug 7 and 11–13:

| Cutoff | Worst counted producer | Worst anyone |
|---|---|---|
| 5:30 PM | Mike 13.8% (Aug 7) | Amanda 13.6% (Aug 11) |
| 6:00 PM | Mike 9.7% (Aug 7) | Amanda 7.3% (Aug 11) |
| **6:30 PM** | **Mike 2.7% (Aug 7)** | **Mike 2.7%** |
| 7:00 PM | 0.0% | Coral 0.6% (Aug 12, a 23:04 outlier) |

**Frank chose 6:30 PM Arizona** — worst-case understatement under 3%, still an
end-of-day email. Ops send is therefore **01:30 UTC the following day**.

---

## 3. Credentials

**All of these should be rotated — they have been pasted in plaintext chat.**

### RingCentral (server-side JWT app, Production) — CONFIRMED WORKING 2026-08-14

```
RC_CLIENT_ID=69K1APV0Vy4dOuJ4kqYBwb
RC_CLIENT_SECRET=e8Ds57GnDW1dezL3dljhUzVqVHKIMVnNdepkzzZkQb6w
RC_SERVER_URL=https://platform.ringcentral.com
RC_JWT=eyJraWQiOiI4NzYyZjU5OGQwNTk0NGRiODZiZjVjYTk3ODA0NzYwOCIsInR5cCI6IkpXVCIsImFsZyI6IlJTMjU2In0.eyJhdWQiOiJodHRwczovL3BsYXRmb3JtLnJpbmdjZW50cmFsLmNvbS9yZXN0YXBpL29hdXRoL3Rva2VuIiwic3ViIjoiMTczNDQyMDUyIiwiaXNzIjoiaHR0cHM6Ly9wbGF0Zm9ybS5yaW5nY2VudHJhbC5jb20iLCJleHAiOjM5MzMyNzM3MzMsImlhdCI6MTc4NTc5MDA4NiwianRpIjoieVY2TS1oQ0dTaGFCZjJJdWZmckpRUSJ9.N41x7IHb6qFvUvusx7YOjk2fhh5ycK93mqB6IWBWiMGZsUV6zEuvlCTBSoxS64qi-MrCRBLr3sRrhfaq6AAtbssHFw4nZ7CL0Bdqk3-HBmsFeqyWgectaiSwtcLb0onxcEvA1NQt4EKAj1vaaCmTbLNbneLj5EYag5BgF_9X5I3M2bOF8kzHsUVxtu35dLx4WjU6_dx8d44wmj-Hihp8KviREGCkWJLZTtaxqFgdz791aEyic8MHbp_72mhryfmMH6WLnqqFbJzKYQokx6t9SuzL6jyXiEi1FEnz2dQKHnZkpNx7YyuT_phTErJMLWPMqOzwVW5HMMxl_Y8Lo8vV8g
```

Auth: `POST /restapi/oauth/token`, HTTP Basic `clientId:clientSecret`, form body
`grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer` + `assertion=<JWT>`.
Access token lives 3600s. Scopes: `ReadAccounts RingSense ReadCallLog ReadCallRecording`.
**RingSense is granted but unusable** — every documented endpoint returns AGW-404.

### AgencyZoom — CONFIRMED WORKING 2026-08-14

```
AZ_USERNAME=frank.automation@floresinsuranceagency.com
AZ_PASSWORD=Automation2026!
```

`POST https://app.agencyzoom.com/v1/api/auth/login` with `{"username","password"}` →
`{"jwt":...}`, then `Authorization: Bearer <jwt>`. 24h TTL. Rate limit ~90 req/min.
**`api.agencyzoom.com` is a dead end** — the OpenAPI spec's own `servers:` block
names it, which is the trap. Use `app.agencyzoom.com`.

*(The pattern: AgencyZoom and Insightful both publish a wrong `api.` hostname in
their own documentation, and in both cases the working host is the `app.` one.
When a new integration's documented host fails to resolve, try the web app's host first.)*

### Resend — ask Frank for a fresh key

Account under **frank@floresinsuranceagency.com**, org `floresinsuranceagency`.
Domain **floresinsuranceagency.com is Verified** (North Virginia) — no DNS work.
Sender: `salesdigest@floresinsuranceagency.com`.
**Cloudflare fronts `api.resend.com` and rejects Python's default user-agent with
error 1010.** Send an explicit `User-Agent` header.

### Insightful — ask Frank for a fresh token

Bearer JWT, `userType: api`, `aud: PROD`, no practical expiry. Host per §2a.

---

## 4. Data pulls that are known to work

### RingCentral call log

```python
DATE_FROM = '2026-08-07T00:00:00-07:00'   # Arizona day
DATE_TO   = '2026-08-08T00:00:00-07:00'
GET /restapi/v1.0/account/~/call-log?dateFrom=..&dateTo=..&view=Detailed&perPage=1000&page=N
```

Paginate on `paging.totalPages`. Retry 429/5xx with `Retry-After`. Owner
extension: prefer `extension.id`, fall back to `from.extensionId`.
Verified record counts: **Aug 7 → 273, Aug 12 → 275, Aug 13 → 315.**

Of Aug 7's 273 records, **188 attribute to a producer or named extension and all
188 are outbound**. Inbound calls land on the main line and do not carry a
producer extension id — do not expect inbound-per-producer figures from this feed.

### AgencyZoom

| Need | Call |
|---|---|
| Leads by date | `POST /v1/api/leads/list` with `startDate`/`endDate` |
| Lead detail | `GET /v1/api/leads/{id}` |
| Stage history | `GET /v1/api/leads/{id}/notes`, `type == "MOVE_STAGE"` |
| Quotes | `GET /v1/api/leads/{id}/quotes` |
| Policies sold | `POST /v1/api/policies` (**undocumented**, found by probing) |
| Tasks | `POST /v1/api/tasks/list` (filters on **dueDate**, not createDate) |
| Roster | `GET /v1/api/employees` |
| Service tickets | `POST /v1/api/serviceTicket/service-tickets/list` |
| Pipelines/stages | `GET /v1/api/pipelines-and-stages` |

**NEW — two pagination traps, both of which return HTTP 400, not an empty list.**
Either one looks like an auth or body-shape failure and cost time this session:

- **Pages are ZERO-indexed.** `page: 1` as a first page is a 400.
- **`pageSize` is capped at 100.** Larger values return
  `{"error": "Invalid page size", "message": "The page size should be less than
  or equals 100"}`.

Paginate on `totalCount`, which every list response carries. Corpus size:
**11,427 leads**, 103,662 tasks.

**Gotchas that cost real time:**

- `workflowStageName` is always null, and `workflowStageId` is **0 for ~10,300 of
  11,400 leads**. Stage must come from MOVE_STAGE notes.
- AgencyZoom **overwrites `enterStageDate`** when it moves a lead to Smart-Cycle,
  so that field reads as the outcome date. **Never use it for stage-entry timing**
  — doing so collapsed every recontact window to zero days and hid every call.
- Notes datetimes are **Arizona-local**; leads, policies and tasks are **UTC**.
- Policy premium is dollars on `/policies` but **cents** on `/customers/{id}/policies`.
- `asContacted` / `asQuoted` flags on stages are unreliable and must not be used.
- Pervasive **duplicate lead records** for the same person — dedupe by (producer, name).

### Task status semantics — NEW, decoded 2026-08-14

The `status` field is a bare integer with no label anywhere in the payload:

| Value | Meaning | Aug 7 count |
|---|---|---|
| **1** | **COMPLETED** — always has `completeDate` and `completedBy` | 206 of 226 |
| 2 | Closed WITHOUT completion; `completeDate`/`completedBy` always null | 19 |
| 0 | Still open | 1 |

**The trap:** `agencyTodo.closeDate` is set on about half the status-2 rows, so
treating "has a close date" as done marks dismissed tasks complete and returns a
flat **100% for every producer**. **Completion is `status == 1`, nothing else.**

Verified output with the service exclusions applied:

| Day | Crystal | Lorena | Mike | Team | Excluded as service |
|---|---|---|---|---|---|
| Aug 7 | 22/22 = 100% | 56/61 = 91.8% | 79/79 = 100% | 157/162 = 96.9% | 48 of 226 |
| Aug 12 | 26/26 = 100% | 41/53 = 77.4% | 89/95 = 93.7% | 156/174 = 89.7% | 45 of 240 |
| Aug 13 | 11/11 = 100% | 41/44 = 93.2% | 82/82 = 100% | 134/137 = 97.8% | 43 of 209 |

Nearly all exclusions come from the customer-record rule; title and body matches
add 0–1 per day. That is expected, not a sign the patterns are broken.

---

## 5. People and roster rules

### Producers whose numbers are counted (3)

| Name | Ext | RC extension ID | AgencyZoom id |
|---|---|---|---|
| Crystal Mango | 106 | 193226052 | 174445 |
| Lorena Gonzalez | 104 | 173445052 | 82587 |
| Mike Olvera | 105 | 173446052 | 82588 |

### Shown as placeholders only, excluded from every calculation

| Name | Ext | RC extension ID | AgencyZoom id |
|---|---|---|---|
| Coral Barwick | 108 | 774861052 | 185440 |
| Sarahi Chin | 109 | 774862052 | 185441 |

Frank, 2026-08-13: *"leave them out of everything for calculating the data for
now, just put placeholders on the report."* Team sums scale **×3**, not ×5.

### Other extensions

Veronica Flores 101 (173440052) · Amanda Torricellas 102 (173443052, AZ 105006) ·
Debbie Aguilera 103 (173444052, **AZ 83597**) · Frank Flores 33 (173442052, AZ 82589).
Debbie is a **recipient and appears in Utilization**, not a producer — AgencyZoom
agrees, `isProducer: false`. `francisco@` (AZ 82372) has no phone extension;
confirmed correct as a recipient.

### Exclusion rules — all from Frank, all settled

- **Leads assigned to Frank, Coral, Sarahi and Amanda are TEST/TRAINING leads.**
  Excluded from every lead-derived metric: recontact struggle, households quoted,
  premium quoted. Their *dials* still count where the producer is counted.
- **Service, renewal and change work is excluded entirely** — from the numbers
  *and* from the report. A task qualifies if it hangs off a **customer** record
  rather than a lead, or its **title** matches `renewal|service request|audit
  change|shot clock reminder|thank you card`, or its **body** matches
  `\bFFR\b|renewal|service request|service center|audit change|audit the change|
  endorse|policy change`.
  **Do not match on bare "Carrier:" or "Policy Number:"** — new-business notes
  routinely record a prospect's current carrier.
- **A lead vendor's broken integration dumps leads into a pipeline literally named
  "Pipeline"** (workflow **23073**, stages New / Contacted / Quoted). The agency
  does not use it. **Ignore every move into it** when reconstructing stage
  history; a move *out* of it tells you nothing about where the lead really was.

---

## 6. Open questions scheduled for 2026-08-28

Surfaced automatically as a highlighted block in the audit on/after that date
(`REVISIT_DATE` in `digest_config.py`). Both concern Coral and Sarahi:

1. Should they be included in the **utilization panel**?
   **Now answerable:** Coral is fully tracked and has real figures every day
   (§2c). Sarahi has no Insightful record and needs a licence first.
2. Should their **leads** enter the lead-derived metrics?

Frank confirmed 2026-08-14 that both stay as they are until the 28th.

---

## 7. Thresholds and business rules

| Metric | Green | Yellow | Red |
|---|---|---|---|
| Call Volume | 50+ | 40–49 | under 40 |
| Avg Talk Time | 7+ min | 3–6:59 | under 3 min |
| Contact Rate | 13%+ | 10–13% | under 10% |
| Households Quoted | 5+ | 2–4 | 0–1 |
| Premium Quoted (per household) | $900+ | $501–899 | under $501 |
| Premium Sold (per policy) | $900+ | $501–899 | under $501 |
| Task Completion | exactly 100% | 90–99.9% | under 90% |
| Speed to Dial (median) | under 2 min | 2–5 min | over 5 min |
| Utilization | 85%+ | 80–84% | under 80% |

**Tier legend wording, set by Frank 2026-08-13:** green = *On or exceeding goal*,
yellow = *Off pace, but close*, red = *Off track, needs review*.

**Team totals:** rate, percentage and per-unit metrics apply the per-producer
threshold **unscaled**. Straight-sum metrics (Call Volume, Households Quoted)
scale **×3**.

**Boundary rules (settled):** premium red is under $501; task completion green
only at exactly 100%; contact rate at exactly 13.0% is green; premium sold with
0 policies is red.

**MVP leaderboard:** nine categories in this exact order — Role Play, Call Volume,
Avg Talk Time, Avg Sentiment, Avg Call Score, Contact Rate, Households Quoted,
Premium Quoted, Premium Sold. 3/2/1 by rank; bars scale to the leading total.
**Zero-activity override:** no recorded activity in a category scores 0, not a
ranked point. **Tie-break:** premium sold, then households quoted, then call volume.

**Coach AI date attribution — verified, do not relitigate.** Coach AI titles each
email with the **UTC date at generation, one day ahead of the Arizona day it
describes**. The email titled "Aug 08" reports Arizona **Aug 7**. Proof: it
reports 76 scored calls, and Arizona Aug 8 was a Saturday with zero producer
dials. Bars scale against **per-producer** extremes over the trailing window
(Avg Call Score 38–251, Avg Sentiment 11–43, Role Play 58–87) — *not* team daily
averages, which put individual scores below the floor.

**Call Detail row colours:**

| Colour | Meaning |
|---|---|
| `#4ADE80` | One-call close — quoted AND sold on the same call |
| `#D8B4FE` | Quote presented, no action yet |
| `#FCA5A5` | Dead/smart-cycled WITH a quote presented |
| `#FDBA74` | Dead/smart-cycled with NO quote presented |
| `#BFDBFE` | Live contact, no quote, no dead/smart-cycle outcome |

A quote presented **verbally** and never entered in AgencyZoom still counts for
the row colour, but does **not** feed Premium Quoted. A "recycled back from
Smart-Cycle" move is a move *out* of the cycle and is not a dead outcome.

**Recontact Struggle** — momentum lost *after* a real conversation.

- **At risk of going cold**: in a post-contact stage, >3 business days since the
  last stage move **or** >3 dials since entering it, no outcome yet, stage entered
  within 30 days.
- **Lost / Won**: that day's outcomes, with stage entered, outcome date and calls between.
- **"Most critical" is the most recently contacted**, since those leads are still warm.
- Grouped per producer. The old three-stage-card visual is **retired but its
  methodology is preserved** in the notes attachment — Frank wants it back later.

### ⚠ Contact Rate and Avg Talk Time are NOT duration-derived — NEW

This was tested directly on 2026-08-14 and the result rules out the obvious
implementation. Distinct-number contact rates at every plausible duration
threshold, Aug 7 / 12 / 13:

| Threshold | Crystal | Lorena | Mike |
|---|---|---|---|
| ≥30s | 80.0 / 79.7 / 74.5% | 54.1 / 34.9 / 22.5% | 60.7 / 64.0 / 62.5% |
| ≥60s | 26.7 / 31.9 / 27.7% | 10.8 / 9.3 / 7.5% | 21.3 / 28.0 / 19.6% |
| ≥90s | 8.3 / 2.9 / 6.4% | 2.7 / 4.7 / 5.0% | 6.6 / 8.0 / 1.8% |

**No threshold lands near the 13% target consistently**, and average talk time
never approaches the 7-minute green mark at any threshold (best observed: 4.0 min
over calls ≥60s). Both metrics must therefore come from **AgencyZoom note
matching**, exactly as §11.4 of HANDOFF_4 implied — a "conversation" is an
RC call matched to a lead by phone number whose note records a real contact.
**Do not implement these from call duration.** Rebuilding them means building the
RC-call-to-lead matcher first.

---

## 8. Files

### Built and working (in the accompanying archive)

| File | Status |
|---|---|
| `secrets_load.py` | Loads `secrets/*.env`, never prints values |
| `rc_client.py` | RingCentral auth, roster, paginated call log — **verified, 273 records Aug 7** |
| `az_client.py` | AgencyZoom auth + one function per capability — **verified, both pagination traps handled** |
| `insightful_client.py` | Bearer auth, roster, analytics — **verified**, endpoint surface documented inline |
| `insightful_util.py` | Per-person utilization + team weighted — **verified against published figures** |
| `az_tasks.py` | Task completion audit with service exclusions — **verified across 3 days** |
| `digest_config.py` | Roster, exclusions, thresholds, layout, all settled decisions |
| `verify_insightful.py` | **27 assertions, all passing.** Run after every change |

### Still to write

| File | Purpose | Blocked on |
|---|---|---|
| `rc_analyze.py` | Per-producer distinct-number volumes, writes `rc_detail_<date>.json` | — (volumes are straightforward; contact rate needs the matcher) |
| `az_leads.py` | RC-call-to-lead matcher, live contacts, NB classification, quotes, policies | **the key missing piece** — see §7 warning |
| `recontact2.py` | At risk / lost / won, stage history, calls between | the matcher |
| `call_outcomes.py` | Five-way Call Detail row colours | the matcher |
| `speed_to_dial.py` | Internet-lead speed to dial (Mav AI + SureQuote) | — |
| `build_digest.py` | Renders the digest, both attachments, both audiences | the above |
| `minify.py` | Shrinks for email, drops unreferenced CSS | — |
| `send_digest.py` | Sends via Resend, reading HTML from disk | — |
| `verify.py` | Full assertion suite across both days | the above |
| `measure_balance.js` | Renders in Chromium, reports column balance | `build_digest.py` |

**`verify.py` is the most valuable artifact.** It previously caught: a stale
hard-coded footnote naming FFR tasks that had been excluded; the staff build
overwriting the ops notes attachment; an over-aggressive CSS purge; and the
leaderboard being silently overwritten by a duplicate code block. Recreate it
early and run it after every change. `verify_insightful.py` is the working model.

---

## 9. Layout, fixed by Frank 2026-08-14

Two columns, **fixed order — do not solve it per day**, because a report whose
panels move around is harder to read than one slightly uneven.

- **Left:** Sales Funnel by Producer · Task Completion Rate · Recontact Struggle
- **Right:** Team Leaderboard · Call Outcome Breakdown · Speed to Dial ·
  Utilization and Efficiency · Coaching & Call Quality

Columns end ~241px apart on a ~3,300px column, and never worse than ~370px across
a typical day, a light day, and a future five-producer day. **This depends on the
Utilization panel rendering its full roster every day** — when it only rendered
people Insightful had published, it swung ~700px and forced the columns apart.
The API now makes the full roster available unconditionally, which removes the
original cause of that swing.

`#digest-section table td { vertical-align: middle }` is an ID-specificity rule
that beats the column rule; the column `<td>`s need **inline**
`vertical-align:top` or the shorter column centres itself against the taller one.

**Sales Funnel is by data category** — one card per metric (Call Volume, Avg Talk
Time, Contact Rate, Households Quoted, Premium Quoted, Premium Sold), producers
ranked highest to lowest inside each, then Team Total. **Producer bars scale to
the top producer**, not the team total.

**Panel footnotes are lifted into the notes attachment** at build time, each
replaced by a superscript marker. Only the attachment pointer stays inline.

---

## 10. Email delivery

**Gmail clips HTML bodies above ~102,400 bytes** and replaces the tail with
"[Message clipped]" — a clipped digest silently loses whole panels. `minify.py`
collapses whitespace and drops unreferenced CSS (~10% saving, render verified
pixel-identical). `send_digest.py` **refuses to send** a body at or over the
threshold, and first tries shrinking the inline recontact list (3 → 2 → 1 → 0 per
group) and says so in the report.

Current sizes: ops body ~60KB, staff ~55KB, notes attachment ~17KB, recontact
detail ~49KB.

**Gmail strips `<details>`/`<summary>`** — the summary text survives but the
collapse does not, leaving a control that looks clickable and is not. There is
**no working disclosure widget in HTML email**; the checkbox hack needs `<input>`
and `:checked`, also stripped. Overflow leads therefore live in the attachment,
with the three most pressing inline.

Confirmed working: `Daily Sales Digest & Call Detail Audit — Aug 12, 2026`, sent
2026-08-14 from `salesdigest@floresinsuranceagency.com`, both attachments delivered.

---

## 11. Still to do

1. **Build the RC-call-to-lead matcher** (`az_leads.py`). This is now the
   critical path — Contact Rate, Avg Talk Time, Call Detail colours, Recontact
   Struggle and the leaderboard all depend on it, and §7 proves none of them can
   be derived from call duration.
2. **Wire AgencyZoom task comments into outcome detection.** 102 of 189 producer
   task comments carry rep-written outcome text ("Called for FFR, no answer, no
   machine", "Got a message saying number is disconnected"). Only *lead* notes are
   read today. 127 of 393 conversations have no lead note at all, and that gap is
   the ceiling on live-contact detection, outcome colours and at-risk detection
   alike. **The single biggest accuracy win available and it costs nothing.**
3. **Rebuild the renderer** — `build_digest.py`, `minify.py`, `send_digest.py`,
   `verify.py`, `measure_balance.js`.
4. **Create the two scheduled tasks** with `create_trigger`, once the digest
   builds end to end. Ops **6:30 PM AZ (01:30 UTC next day)**, staff 8:00 AM AZ
   (15:00 UTC). **Scheduled tasks fire in a FRESH session with no filesystem and
   no memory** — credentials and the full method must be embedded in the trigger
   prompt, or the run must rebuild from scratch.
5. **Assign Sarahi Chin an Insightful licence** — she has no record at all, so no
   decision on 08-28 can make her reportable until this is done.
6. **Rotate every credential** — RingCentral secret and JWT, AgencyZoom password,
   Resend key, Insightful token.
7. **Coach AI / TRAQ.ai API key** — Frank has requested one; they are working on
   it. It would give per-call transcripts and scores directly and remove the note
   dependency — and would also resolve the Contact Rate / Avg Talk Time problem in
   §7 far more cleanly than note matching. `api.traq.ai` is reachable; only the
   key is outstanding.

---

## 12. Answers Frank has already given — do not re-ask

- Utilization scope = **all users except Amanda** (and, until 08-28, except Coral
  and Sarahi — confirmed arithmetically against Insightful's own team figure).
- Crystal does service and renewals; **all service/renewal/change work is excluded
  entirely**, from the numbers and from the report.
- Coral and Sarahi: **excluded from every calculation**, placeholders only,
  revisit 08-28. Confirmed again 2026-08-14 after Coral's data was found.
- Sarahi's **missing Insightful licence is flagged in the audit** (Frank, 08-14).
- Leads assigned to Frank, Coral, Sarahi, Amanda are **training leads**.
- The **"Pipeline"** pipeline is a vendor integration error — ignore it.
- Tie-break: **premium sold → households quoted → call volume**.
- Tier legend wording: **On or exceeding goal / Off pace, but close / Off track, needs review**.
- Layout order is **fixed**, not per-day.
- "Most critical" in Recontact = **most recently contacted**.
- Notes and methodology go in an **attachment**, not the body.
- Network access is set to **All domains** — do not ask him to allowlist anything.
- **Ops email sends at 6:30 PM Arizona** (Frank, 2026-08-14), chosen over 6:00 PM
  because 6:00 understates a counted producer by ~10% about one day in four.
