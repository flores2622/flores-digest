# HANDOFF 11 — 2026-08-28

Frank's review of the 08-27 rebuild, worked through live, plus everything that
broke while shipping the fixes. **Five commits sit on
`claude/2026-08-28-review-fixes` and NONE of them are pushed** — the git proxy
refuses this repo (`not in this session's authorized repository set`). They are
also bundled as patches; `git am *.patch` onto a fresh clone.

The 08-28 digest went out FOUR times tonight (18:44 mine, ~19:20 the scheduled
task on unfixed `main`, 22:46 mine again). Gmail threads them under one subject.
The team saw broken formatting on all of them. Do not send again until the
transport problem below is fixed.

---

## 1. What Frank adjudicated — these are settled, do not re-litigate

| Case | Verdict |
|---|---|
| Francisca Celaya | **Correct as built.** Crystal cross-selling on a renewal IS her job. The open-lead guard did the right thing. |
| John Hoeppner | Not a contact. Note was "Rachel Anderson"; her task comment said "Called, MB full". |
| Robert Munoz | Not a contact — **No Answer**. "Hello? Robert?" is the producer talking into a dead line. |
| Juan Esquivel | Not a contact. The "note" was pasted coaching-script copy. |
| Nazzer Robles | Not a contact. Smart-cycled for next day to restart automation; he never answered. |
| Guillermo Lara, Cynthia Atondo | Not contacts. Coral is not logging no-answer outcomes — **producer error, no code change for it**, but duration must not promote them. |
| Roger Ryan | One contact, not two. Same lead on two numbers; the 1-second dial is not a contact. |
| Kenneth Payne | **IS a live contact and counts in the contact rate.** Wrong number still needs its own Call Detail outcome — they coach producers to offer that person a quote anyway. |
| Elizabeth Los | Objection was **overcome**, not "kept going". She refused, then let us quote and talk numbers. |
| Armando Alvarez | Service call-in. Open service requests, no open lead. |
| Jose Gonzalez | **Open**, not lost. Quoted, yes; lost, no. |
| Maria de Avina | Addressed / not overcome, still an open opportunity → yellow, not red. |

**Lost action, per Frank:** moved to Dead, **or** smart-cycled more than 30 days
out. Not lead status — Elizabeth, Maria, Armando and Eliacin are all status 5
and none of them is lost.

## 2. Objection chip colour — the agreed matrix

Two independent axes plus green. Implemented in `panels.OBJ_CHIP`.

| Addressed | Result | Lost action | Chip |
|---|---|---|---|
| no | — | yes | solid red (`cdc-r`) |
| no | — | no | solid yellow (`cdc-y`) |
| yes | not overcome | yes | candy-cane red (`cdc-rx`) |
| yes | not overcome | no | candy-cane amber (`cdc-yx`) |
| yes | kept going | yes | candy-cane red |
| yes | kept going | no | candy-cane amber |
| yes | overcome | either | green (`cdc-g`) |

Texture = did the producer engage it. Colour = did the lead take a lost action.
Green overrides both.

`_is_lost_action()` currently returns False for a smart-cycle because the move
string carries no date. **The >30-day test is not implemented** — it needs the
smart-cycle target date plumbed onto the row.

## 3. What the five commits changed

**Contact-rate evidence** (`live_contact.py`, `daily.py`)
- A no-contact note no longer vetoes the whole day. Sarahi's 11:49 "Called No
  Answer" on Ricardo Perea was beating her own 13:25 "Spoke with Ricardo have
  appoiment set for 1:30" and a 15m44s recording. A negative is now overruled
  by an explicit statement of contact (`asserts_contact`) or a sustained live
  recording (`LIVE_OVERRIDE_SECONDS = 60`). Jose Garcia and Guadalupe Garcia
  were lost the same way.
- Text in a notes field is no longer proof of a conversation — `is_outcome_text`
  rejects bare names, quoted script copy and to-do lists.
- **Duration no longer promotes a dial to live.** It was the sole basis for
  exactly two rows on 08-27 and both were wrong.
- `MIN_CONTACT_SECONDS = 5` floor for dials with no recording.
- `_one_row_per_lead()` collapses one lead reachable on two numbers.

**Transcription** (`transcribe.py`) — a ≤4-word greeting with no dialogue is
`no answer`, not live. Downloads pace at **8/min** honouring `Retry-After`
(RingCentral media is 10 per rolling 60s; both callers asked for 12, which
stalled the 08-27 run for 30 minutes at record 115 of 203).

**Service screening** (`inbound.py`) — inbound drops the CSR condition.
Outbound keeps it (Wesley Knowlton). Cached inbound is **re-screened at read
time** in `build_metrics`, because the transcripts file is a cache and Armando
survived his own exclusion rule purely by already being on disk.

**Display** (`panels.py`) — `dead` reads the move DESTINATION, not the whole
string. Objection matrix above. Call-in badge stripes in the category tint with
dark ink (it shipped as amber-on-amber and was unreadable). `_s2d_card` uses
`DOT.get(name, TEAM_DOT)` — it raised `KeyError('Team')` and killed the whole
build the first time the TEAM had no internet leads, which was 08-28.

## 4. OPEN — the email arrives with holes in it

**This is the live problem. Do not send until it is solved.**

Evidence gathered tonight:
- A **6 KB** probe through Resend arrives with the `<style>` block byte-for-byte
  intact and `&#61;`-escaped links intact.
- An **85 KB** probe, same content padded, **never arrived at all**.
- The real **84 KB** digest arrives, but every AgencyZoom link is mangled:
  `?id=87607238` → `?id�607238`.

The sent body contains **zero** literal `=`-followed-by-two-hex; all 27 links
are `&#61;` (written by `panels.py:339` and `AZ_URL`, then `qp_safe`). So on the
large-message path something decodes the entity back to `=` and a
quoted-printable decode then eats `=`+2 chars. That deletion runs through the
whole body including the 18 KB `<style>` block, which is what destroys the
layout. **It is not Gmail stripping CSS.**

Direction: stop shipping an 84 KB HTML body. Either inline the critical CSS and
drop inline Call Detail, or send a light HTML email with the report as the PDF.
Prove it with a probe before sending to all ten.

## 5. OPEN — the bare-name corpus caches go stale

`pull_sources` writes `az_leads_all.json`, `az_customers_all.json` and
`az_policies_all.json` under undated names guarded by `if not p.exists()`. In a
fresh nightly container they are pulled that day. **In a re-used container they
never refresh.** Tonight's 08-28 build ran against a lead corpus fetched
08-27 18:53 containing **zero leads created on 08-28**, which is why Speed to
Dial reported "no internet leads assigned" for everyone when internet leads did
arrive. Households Quoted and Premium Quoted for 08-28 are also suspect.

Fix: date-scope them, or re-fetch when the file predates the day being built.

## 6. OPEN — RingCentral's `result` field is never read

Lorena logged 19 "No Outcome Logged" on 08-28. She made 70 outbound dials and
only **47 were recorded (67%, against 84–97% for everyone else)**. RingCentral
labels the 23 unrecorded ones itself:

    Hang Up 13 · Call Failed 4 · Wrong Number 3 · Call connected 2

Nothing in the pipeline looks at `result`. Reading it would empty most of the
No Outcome Logged bucket across every producer, and it hands over the
**wrong-number outcome Frank asked for** for free. Highest-value fix on the
board.

## 7. OPEN — smaller

- **Wrong-number chip.** Kenneth Payne counts live and in the rate, but has no
  distinct Call Detail category. The palette is at nine categories on six hues;
  adding a tenth needs the colour-by-family rework HANDOFF 10 deferred.
- **Elizabeth Los / `overcome`.** A model judgement, not a code path. Tightening
  the prompt means deleting `callsum_<day>.json` and re-paying — CLAUDE.md warns
  against doing that casually.
- **Legend gap.** Only the GREEN callback swatch is in the legend. An amber
  stripe (called back after a voicemail — Lorena / Fredis Flores) is
  unexplained. Worse, that conversation IS counted in Call Detail as
  "Contacted, okay to quote" while the bar still shows the dial as Voicemail.
- **`verify_finalize.py` has the day hardcoded** to 2026-08-25.
- A callback answering an EARLIER day's dial is reported beside the bar, not in
  it, because that dial is not in today's denominator. Working as designed
  (Sarahi / Roger Ryan on 08-28).

## 8. No tests, no pre-send check — the real gap

Every rule in this repo is a hand-adjudicated case buried in a handoff and
defended by a prose comment. There is no executable test. Thirteen fixtures
built from Frank's 08-27 adjudications live in `/tmp/fixture.py` in a session
container and will be lost — **promote them into the repo**.

Nothing checks the report before it sends. Both of tonight's worst failures were
mechanically detectable: a rendered screenshot of Call Detail would have caught
the unreadable badge, and a sanity gate (live contact whose transcript says
voicemail, duplicate lead_id, sub-5-second contact, contact rate moving more
than 5 points overnight) would have caught most of the 08-27 batch.

## 9. Operational notes for whoever runs this next

- **Cannot push.** Add `flores2622/flores-digest` to the session's sources.
- **Cannot pause the scheduled task** from inside a session — the permission is
  blocked. `SEND_HOLD` (commit `bfb87e3`, since removed) is a tracked file that
  `daily.py` checks before sending; re-add it if a send needs holding, since the
  nightly task clones `main` and runs a bare `daily.py` with no flags.
- **Never re-fetch `az_service_tickets_<day>.json`** for a day already built.
- Two probe emails ("PROBE encoding test", "PROBE large body") were sent to
  frank@ tonight. Harmless, delete them.
