# Flores Insurance Agency — daily sales digest

Standing rules for anyone (human or Claude) working on this repo. These were
each learned the hard way from a wrong number in a sent report. Do not
re-litigate them from first principles — if one looks wrong, check the handoff
that introduced it first.

## What this builds

`python3 daily.py` reports ONE Arizona day and emails two audiences at 6:30 PM
AZ: **ops** (frank@, francisco@, veronica@, amanda@) get the digest plus the
Call Detail & Task Completion Audit; **staff** (the producers plus debbie@) get
the Sales Digest only. `--day YYYY-MM-DD` rebuilds a past day, `--audience
ops|staff|both`, `--no-send` builds without emailing.

Everything caches under `data/`, so a re-run resumes rather than restarting.

## The money rules

- **A policy whose lead source is BOB is not a sale.** Already handled.
- **Neither is Rewrite** (Frank, 2026-09-24). It is kept for the service
  department from now on. Its one tracked-producer sale was Crystal's $652 on
  2026-08-20, which leaves Premium Sold on any rebuild of that day. **The
  published 08-20 stays as it went out** (Frank: "no i dont want it off the
  board") -- do not rebuild or patch it to drop that sale.
- **What each lead source means is `lead_sources.py`** (Frank, 2026-09-24): the
  groups, what to sell each, and the not-a-sale and cross-sell sets that
  `digest_config` reads. Commercial sources (Leo, Work Comp, the Comm Leads
  lists) are Cerberus's. Frank confirmed the `approach` lines on 2026-09-24.
  **A staff member's name as a source is Personal network** -- their own,
  never each other's, and never in Role Play -- **except Francisco's, which
  is a Referral** (and so can come up in Role Play);
  Instagram / LinkedIn are Social media (Facebook stays Generated); Found us
  (Google, Farmers.com) is part of Call-in / walk-in (Frank, 2026-09-24).
  The Sales tab's Premium per Lead Source uses these same groups.
- **The Sales sheet names products the way the team types them** (Frank,
  2026-09-25: "we only have 2 auto products. Farmers and BW"):
  `sales_log_auto.product_name` turns an auto-added row's AgencyZoom policy
  type into Farmers-Auto / BW-Auto / Farmers-Home / Foremost-MH / ... by
  carrier id (Farmers 484668, 484654, 1030958; BW 186, 2448054; Foremost
  102, 262). The nightly sync re-applies it to the last 14 days' auto rows,
  never to a row a person typed or edited.
- **Apollo judges each call against its lead source** (Frank, 2026-09-24).
  `coaching_cards._ask_card` sends `lead_sources.prompt_block()`; METHODOLOGY.md's
  "Lead source" section says how to use it, and the card's `leadfit` verdict
  is the result. Only reads made from 2026-09-24 on carry it: the card cache
  is keyed by call, not prompt, so past cards are not re-read (and must not
  be, for cost) -- **except by `rebuild_cards.py`, run only when Frank asks**
  (he did for 09-01..09-25 on 2026-09-27). It re-reads a day from R2's
  cache/<day>/ inputs, re-reads stage moves from the notes, takes the lead's
  stage THEN from its move history (`pipelines.stage_as_of`; the lead
  snapshot only knows where it sits now) and leaves quotes out of the lead
  history (no quote date). `--publish` backs up the page and the old card
  cache under `backups/<today>-card-rebuild/` and swaps only `calls`, `scan`
  and `objcats`.
- **What each sales pipeline and stage means is `pipelines.py`** (Frank,
  2026-09-24). Producers work 1 Pipeline, 1-1 QNC (quotes not closed), 1-2
  Leads Not Quoted and Life Pipeline; "Pipeline" is 1 Pipeline misfiled by
  integrations and should be empty; anything commercial or AZ Sun is
  Cerberus's; every other pipeline is unused. Apollo gets the lead's stage
  when the call started plus the producer's moves that day, and scores
  `stagefit`. The day's MOVE_STAGE notes arrive NEWEST FIRST, and a stage
  name can contain " to " (Ready to Present) -- `pipelines.parse_move` and
  `_chronological` handle both; do not split moves on the first " to ".
  **Lender Referral** holds accounts a center of influence sent us, so they
  skip the full automation. **IL Interested and Transfer Pending are not
  agency stages** (made for an outside texting company): a producer moving a
  lead into one is a mistake Apollo flags. Open leads misfiled in "Pipeline"
  are listed on the Sales Center for someone to move (`pipelines.misfiled`).
- **Apollo coaches follow-ups and call backs as their own kind of call**
  (Frank, 2026-09-25). Every read gets `lead_history.block()`: today's call
  direction, dials to the number in the last 30 days, the quotes on file,
  earlier coaching cards on the lead (R2 days/, 30 days) and its notes
  before today. **`flow` is what the call was FOR, not who dialled** ("a
  call back doesnt necessarily have to be a follow up"): first / finish
  quote / follow-up, from the stage (New etc. / Contacted, In Progress or
  Ready to Present / Quotes Presented, Quoted, 1-1 QNC), then the history.
  Who dialled is the card's own `direction` (dialled / call back / call in,
  `lead_history.direction_key`). A follow-up gets the six-step `fuscore`
  (reconnect WITH AN UP-FRONT ASSUMPTIVE CLOSE ... dated next step) and
  `assume` (the sale at the start, through objections, at the end) instead
  of the nine dimensions and "assumed the quote"; first and finish-quote
  calls keep the nine, with what the history already captured as "n".
  **Offering to SEND the quote is not assuming it** (Frank, 2026-09-28):
  assuming the quote means building and presenting it on the call; a
  producer who sets up from the start that she'll put it together and send
  it (Lorena, Eva Moraila 09-01) scores `askq` false -- an early exit.
  Sending is only for a prospect who says they are busy, and that is scored
  as overcoming a "Bad Timing / Busy" objection (`objs`): a better, specific
  time to talk, or send it AND hold them for a brief discovery, scores well;
  "I'll send it" and hanging up is a dropped objection.
  **Always assume, never ask**: any permission-seeking line is false, however
  soft. **No chance to assume is null, not false** -- cut off, too short,
  hung up, not recorded -- and counts neither way (`scan`'s `of_first`
  leaves it out).
  **Quote sent instead of kept on the phone** (Frank, 2026-09-28) is each
  card's `sendoff`: "producer" (offered on their own), "busy" (the prospect
  said they had no time -- the Busy objection's to score), "asked" (the
  prospect asked for email first), "no", or null (no quote came up). "producer" includes "I'll have the numbers for you tomorrow" / "let me work
  on it and call you back". **Asking the prospect to send US their documents
  (dec page, current policy, VINs) is discovery** (Frank, 2026-09-28; the 56
  "producer" verdicts were re-read under this, backups under
  `backups/2026-09-28-sendoff-recheck/`) -- **but the review happens on the
  phone**: asking for them and ending with "I'll review it and call you
  back" is getting off the phone, "producer" (Coral / Randell Otis 09-25:
  "she should review it with him on the phone").
  Coaching Center > Wins and Losses counts it per producer and lists the
  calls. **Every assumption stat is there too** (Frank, 2026-09-28): the quote,
  the sale, and a follow-up's up front / objections / end, per producer and
  team, off each card's own verdicts (n/a counts neither way), each with its
  calls listed. It replaced "The opening asks permission". The Digest's
  leaderboard shows the same count per producer as **Sent the Quote**
  ("N of M", shown, not scored -- Frank, 2026-09-28). Apollo returns it from 2026-09-28; earlier cards got it from
  `sendoff.py --backfill` (one short read per card over its transcript --
  nothing else on the card changed).
  **The card's fix lines keep them on the phone** (Frank, 2026-09-28):
  `askfix` and each objection's `fix` finish the quote on the call -- a few
  minutes, never "30 seconds" -- and never suggest emailing or texting it
  unless the prospect said they were busy.
  September's first and finish-quote cards were re-judged under these rules
  by `assume_reread.py --backfill` (Frank asked, 2026-09-28): one short read
  per card, replacing only `askq` / `asks` / `askfix` and the day's `scan`
  (backups under `backups/2026-09-28-assume-reread/`). Follow-ups the same
  way with `--followups` (Frank, 2026-09-28: "re-read the follow-ups too"):
  `assume`, `asks`, `askfix` and the three scorecard lines about assuming
  the sale (`assume_reread.FU_ASSUME`), backups under `...-assume-reread-fu/`.
  **A quote emailed or texted after a call counts as presented** (Frank,
  2026-09-27), so the next call is a follow-up; **ending a finish-quote call
  to send the quote instead of presenting it is a flagged bad habit**.
  Inbound rows carry the producer's stage moves like outbound ones (they
  were `[]`, so a call back read the end-of-day stage as its start).
  **A call the producer ANSWERED scores `greeting`**: on their direct line,
  the caller's name when they knew who it was, "This is Mike, how can I
  help?" when they didn't, never the front desk's "thank you for calling
  Farmers". Apollo quotes the call's first sentence and who said it; when
  the caller spoke first the pick-up wasn't recorded and the code makes it
  "n" (`coaching_cards._greeting`) -- the model guessed otherwise.
  **No agency, no insurance, no full intro on a pick-up** (Frank,
  2026-09-30: "people hang up when they hear an agency or insurance or
  realize we want to sell them something"): "This is Coral, how can I
  help?" when they don't know who it is, "Hi David! How are you today?"
  when they do (caller ID / a saved contact explains it if asked). Saying
  Farmers, an agency name, "insurance" or a full introduction is "m".
  **Only the producer's own words are the greeting** (Frank, 2026-09-30):
  `by` is producer / caller / front desk, and `_greeting` forces "n" when
  it is not the producer, when the leg is tagged "ONLY THE OPENING WAS
  RECORDED", when the line names another staff member ("This is Debbie"),
  is labelled (lead)/(customer), or is the front-desk script on a
  transferred or unlabelled line. A **transferred** call
  (`lead_history.answer_route`: the row's `partial`, else `inbound.answered`'s
  route over the saved RC log -- no new request) is its own greeting: by
  name, own name, pick up where the front desk left off. The agency name is
  never needed; a misheard name is never marked down; an answered-only
  card's "Opening & identification" is "n".
- **Apollo's rulings of 2026-09-30** (new reads only; no past card re-read):
  **`exit` is rare** -- decided in order: recording ends mid-call or the
  prospect hung up, the prospect started the wrap-up, the sale closed ->
  false; only the producer's own line ending an engaged call is true; null
  when not recorded to the end. **An early "no" before the quote is an
  objection**: `askq` false unless the producer assumed the quote in reply;
  **`sendoff` "producer" makes a null `askq` false** in code
  (`_askq_after_sendoff`). `asks` is null when the quote could not be
  finished for a reason outside the producer. **`calltype` "service" only
  when no sales opportunity existed at all**; a household missing a product
  is "mixed". **A note / TEXT / EMAIL saying a quote was sent makes the call
  a follow-up whatever the stage** (`lead_history.quote_sent`, drips and the
  lead's own messages left out); a quote on file with no such note at
  Contacted / Ready to Present is finish quote. Objection bands: 8-10
  overcome, 5-7 partial, 0-4 not; a Busy handled well is 8+. Fix lines are
  in the language the producer was speaking at that moment. Reads get up to
  40,000 characters (`call_summary.clip`, "[TRANSCRIPT CUT HERE]" when cut;
  was 16,000 / 12,000 silently), the card's first budget is 9,000 tokens,
  each new card keeps `model`, and `_bool_pair` reads "true"/"false"/"null"/
  "n/a" strings for what they say (a bare None is None, never False).
- **A closed card's right half is Quick coaching** (Frank, 2026-09-30:
  "the right half of the card be a quick coaching summary, while leaving
  the left of the card whats currently there"; `quickCoachHtml`), from what
  the card already holds -- no new read: the top two `good` and `bad`
  titles (detail on hover) and one line to say next time, the first
  objection not overcome's first `fix`, else `askfix`. One column under
  900px; no panel when there is nothing to say. **A card opens from
  "▼ Expand ▼" at its bottom and closes from "▲ Collapse ▲" at the bottom of
  the open card** (Frank, 2026-09-30, replacing the small top-right arrow;
  the header still opens it too), which scrolls back to the card's top.
- **Card flags are categorised** (Frank, 2026-09-27): Apollo names each
  flag's category from `digest_config.FLAG_GROUPS` (No next step, Quote not
  presented, Discovery missed, Approach skipped, Objection dropped, Call cut
  short, Stage / pipeline mistake, Compliance = red; Cross-sell in progress,
  Callback set, Pipeline note = yellow; Strong moment = green), stored as
  `flag_groups` beside `flags`. The board shows each category once per card
  with Apollo's words on hover. Cards read before that are **guessed from the
  wording on the board** (`FLAG_GUESS`, Frank chose that over a paid re-read).
- **Role Play never uses a center of influence, cold / misc or existing
  client, new purchase lead source** (Frank, 2026-09-24), nor a personal
  network, one-off, commercial, BOB or Rewrite source
  (`GROUPS[...]["roleplay"]`). That is Role Play only: **calls on those
  sources still get coaching cards** and count in every coaching figure like
  any other call. Role Play draws a session's lead source from the
  producer's own cards over the trailing 4 weeks.
- **Role Play prospects speak with Deepgram voices** (Frank, 2026-09-29).
  `RP_VOICES` (index.html) tags each Aura-2 voice by language, sex and age
  band, and each prospect gets one that fits. **English, Spanish and mixed**
  ("some should be spanish, some english, and some mixed"): random, a third
  each, with **no language choice on the screen** (Frank, 2026-09-29: "i dont
  want a language dropdown"). Spanish uses Mexican / Latin American voices,
  mixed Deepgram's five code-switching ones. First names come from the whole
  American + Hispanic list in every language; a Spanish or mixed prospect
  has a Hispanic surname. **Crystal never gets Spanish or mixed** (Frank,
  2026-09-29: "she doesnt speak it") -- `RP_ENGLISH_ONLY`.
  They speak at 1.3x (`RP_SPEAK_SPEED`, Deepgram's `speed`; Frank,
  2026-09-29: "they talk to slow"; 1.2 was only ~8% shorter in Spanish, 1.5
  -- Deepgram's maximum -- "just a tad bit too fast", 2026-09-30) -- a
  refused speed is retried at normal speed. **A Spanish
  prospect uses no English words** (Frank, 2026-09-30: "its mixing English
  words with Spanish"): `languageInstruction("es")` names the Spanish
  insurance words; only company names stay. The MIXED third code-switches
  by design. **They start talking on the first sentence** (Frank, 2026-09-30,
  still on claude-sonnet-5 -- "i dont want haiku 4.5"): the turn is
  streamed (`callClaudeStream`, `stream: true`), each finished sentence goes
  to Deepgram at once and they play back to back (`rpSpeechQueue`; under 20
  characters is held for the next), and the mic returns only after the last. The turn goes out
  streamed as `text/event-stream` with `no-transform` (Cloudflare may hold
  back a text/plain body), with the persona and conversation prompt-cached,
  and **the reply is asked for early** (2026-09-30, "it still takes too long
  to respond"): at `RP_EARLY_MS` (0.7 s) of silence, quietly; more words
  throw it away, and the prospect still answers only the whole turn at 1.5 s.
  A streamed line keeps its sentences as `parts`; the grade attaches every
  clip as `audios` (first also as `audio`), and Session History plays them
  in order. The Worker's `/api/roleplay/speak` streams them and needs the
  `DEEPGRAM_API_KEY` secret (without it the browser's voice speaks). Apollo
  grades in English whatever the call's language. **Producers rate the voice
  after each graded session** (stars, again yes / no, a comment), saved on
  the session and in `roleplay-voices/ratings.json`; the ratings table on
  the Role Play tab is Frank's alone (`ROLEPLAY_VOICE_VIEWERS`). **Every
  prospect has an AI-drawn headshot that glows green while they speak**
  (Frank, 2026-09-29: "remove the talking face, its too slow and cuts me
  off. lets just do headshots of AI generated faces with glow when they are
  speaking" -- the TalkingHead 3D face, its test page and `faces/` are gone;
  do not bring them back). A fixed library: sex x age band x look (Latino
  for a Hispanic surname, else white / Black / Asian American) x 4 variants,
  at most 96 faces, each drawn ONCE by Workers AI (FLUX.1 [schnell], the
  `AI` binding in wrangler.jsonc, ~$0.0006 a face) the first time a prospect
  needs it and kept in R2 under `roleplay-faces/` (`/api/roleplay/face/<key>`).
  **No `seed`** -- the model refuses it (AiError 5006, 2026-09-29), which is
  why no face drew on the first day. No binding or a failed draw shows the
  initials.
  **Every prospect gives rapport** (Frank, 2026-09-30: "they keep just
  turning me back to the quote after 1 sentence"): ROLEPLAY.md's `###
  Rapport`, appended to every persona -- small talk and questions about
  them get a real answer with a detail or two, sometimes a question back,
  for as long as the producer keeps it going; the prospect never steers back
  to the quote or an objection themselves, and rapport never counts as not
  asking for the close. Difficulty still decides the objections.
  **The mic waits for the producer to finish** (Frank, 2026-09-29: "fix the
  mic cutting off"): it listens continuously and sends the turn after
  `RP_PAUSE_MS` (1.5 s, Frank's pick -- 2 s felt slow) of silence -- a tap on the mic sends at once -- never
  at the browser's first final result, which cut people off mid-sentence.
  When Chrome ends the session itself it restarts at once, keeping the words
  and the turn's recording; a blocked mic stops for good.
  **What the producer is saying shows as their own bubble at the bottom of
  the conversation** (Frank, 2026-09-30 -- it was in the mic button and ran
  the width of the screen; `rpShowLive`), and the conversation keeps
  scrolled to the newest line unless they scroll up to read (`rpFollow`);
  the box fits the window so the mic stays in view. **Apollo's grade and the
  voice rating sit beside the conversation** (`.rpside`; Frank, 2026-09-30:
  "were losing a lot of space, and the feedback is off centered"), and the
  board is 1600px wide on a big monitor (`.main`; it was 1120px because it
  began as an email -- Frank, 2026-09-30); narrow screens stack.
- **Every graded Role Play session is kept and can be read back** (Frank,
  2026-09-29: "a full history of role play sessions ... producers see their
  own"). Learning Center > **Session History**: a date range (7 / 30 / 90
  days, all time, custom), a summary per producer (sessions, resolved,
  checklist met, the checklist items missed most, the objections drilled),
  and every session, which opens in place to Apollo's grade and the whole
  conversation. **Who sees what is the Worker's call, from the Access email**
  (`rpScope`): `ROLEPLAY_HISTORY_VIEWERS` (wrangler.jsonc -- Frank and the
  ops recipients) see everyone and the beta sessions; a producer
  (`RP_PRODUCER_EMAILS`, their staff-digest address) sees only their own --
  on the Role Play tab's Past sessions list too; anyone else sees none. The
  list reads `roleplay-index.json` (one summary per session, added on save,
  and healed on every list call from what is actually under `roleplay/` and
  `roleplay-beta/`); a session opens from its own file. Sessions saved from
  2026-09-29 also carry `focus`, the objection groups they drilled.
- **Sessions and coaching cards play back line by line** (Frank, 2026-09-29:
  "i want to be able to hear it ... the transcript and recording combined, to
  be able to skip to a specific part that I am reading. This should also be
  reflected in the coaching cards"). **Role Play**: each producer turn is
  recorded in the browser while they speak (MediaRecorder on the same mic,
  `rpClipStart`) and uploaded to `roleplay-audio/<producer-slug or beta>/`
  (`/api/roleplay/clip`); every prospect line `/api/roleplay/speak` streams is
  also kept at `roleplay-audio/tts/<sha of voice + text>.mp3`, and the grade
  puts each turn's `audio` key on the saved transcript -- a producer clip only
  if it sits under that session's own prefix. `/api/roleplay/audio` serves a
  producer's clips by `rpScope` (their own, or everyone's for the history
  viewers); the prospect's machine voice to anyone signed in. Session History
  plays a session from any line, **and word by word like the cards** (Frank,
  2026-09-30; `rphWords` / `rphClip`): neither voice has word times, so each
  word sits at its share of its clip's speech by length, the speech found in
  the sound itself (a producer's clip holds the silence before they spoke and
  the 1.5 s pause after) -- close, not exact. Sessions before 2026-09-29 have no sound.
  **Coaching cards**: `coaching_cards._timed_turns` adds `turns` ({r, t, who,
  text}; t = seconds into recording r) from Deepgram's SAVED reads only
  (`deepgram_stt.turns(..., cached_only=True)` -- a card build never pays
  for a read), and the card shows one player with the transcript under it:
  a line click seeks there, the line playing is lit (inside its edge, so
  the box never covers it), **the word being said is highlighted and any
  word plays from there** (Frank, 2026-09-30; `wordSpans`: Deepgram's own
  word starts, `w` on each turn, cached from 2026-09-30 on -- older reads
  spread a line's words across it by length -- and a redacted line loses
  its `w`), and **each line's button
  pauses and resumes in place** (Frank, 2026-09-29: "pause the playback
  without stopping or restarting it") -- the same on a Role Play session's
  lines. Hovering the button opens **volume and speed** (0.75x-2x; `ppBtn`,
  `pb`), one setting for every line, card and session, kept in the browser --
  a **vertical bar to the LEFT of the circle**, speed as a dropdown (Frank,
  2026-09-30: it covered
  the transcript), `position: fixed` and placed by `ppPlace` so the scroll
  box cannot clip it (below the circle when there is no room). Keep the
  panel inline elements (a card line is a <p>; a <div> inside one ends the
  line early) and give no ancestor a `filter` or `transform` -- either makes
  it the fixed bar's frame and the bar lands in the wrong place. Cards with no Deepgram
  read keep the plain transcript. **September's cards were given theirs**
  (Frank, 2026-09-29: "do september's cards") by `card_turns_backfill.py
  2026-09-01 2026-09-28`: one paid Deepgram read per carded recording, added
  to the day's R2 bundle, and ONLY `turns` added to each day's page (backups
  under `backups/<today>-card-turns/`) -- the transcript Apollo read, the
  grades and data/transcripts_<day>.json (so every verdict) untouched.
- **Life insurance is its own stat** (Frank, 2026-09-30: "life insurance
  sales are separate than the rest. I want it on the sales digest still, but
  i dont want it to count as a HH or premium, make it its own stat"). A
  policy is life by its AgencyZoom type (`digest_config.is_life`: "N year
  term", Whole / Universal / Index / Variable Universal / Individual Life,
  "Life"); `real_sales` and `bundle_classification` leave it out and
  `life_sales` counts it (`life_policies` / `life_premium`; the board's
  `life` / `life_ps`). A lead sold on Life Cross Sell is not a household
  sold (`is_life_lead`), **nor is a lead on any source whose sale was life**
  (Frank, 2026-09-30: "still shows coral with 1 HH" -- Alondra Angulo, Home
  no Auto, marked sold 09-30 for Coral's 09-29 Individual Life): every
  policy its producer sold on its lead source within 3 days of its soldDate
  is life (`life_lead_policies`, `LIFE_LEAD_DAYS`; the Worker's
  `isLifeLead` gets them as `live_basis.life.recent` plus today's own
  policy read). Policy records carry no customer, so that tie is the only
  one; it changed no other September lead. So life is never in Policies, Premium Sold, HH
  Sold, Household Completion, the leaderboard or the closing ratio; the
  Digest's **Life Sold** tile shows it (its list is `rows.life`), the email
  adds a Life Sold card only on a day with one, and the Worker keeps a live
  life sale apart the same way (`live_basis.life`). The Sales sheet still
  lists it. BOB life policies stay not-a-sale: no producer had a counted
  life sale in September (Crystal's two, 09-02 and 09-15, were BOB).
  **The goal is 1 life policy a week** (Frank, 2026-10-01), per producer,
  Monday to Friday (team: 1 x `TEAM_SCALE`): `digest_config.life_week_tier`
  over the board's `life_week` (Monday to the day; `lifeTier` in index.html
  mirrors it) -- green once the week has one, yellow before Friday without
  one, red on Friday without one. A range wants 1 per week it touches.
- **A renewal is not new business.** Neither is servicing, a payment, a claim,
  or chasing paperwork on a policy already sold.
- **Selling a product the household does not have yet IS new business**, even to
  a customer of twenty years. Cross-sells count.
- **Premium Sold comes from AgencyZoom policies** by `agentId` + `soldDate`, not
  from the call log. Policy records carry no name, phone, customerId or leadId —
  only `leadSourceId`, which is the marketing source and is shared by thousands
  of policies. The join from a dialled number to a sale is the LEAD record:
  `status == 2` means sold, and all 1,517 status-2 leads carry a `soldDate`.

## The contact-rate rules

- **Never "fix" a low contact rate.** Most dials genuinely reach voicemail. On
  2026-08-13 it was 115 of 135. That is the real number.
- **Contact rate is outbound-only.** A dial is an attempt the producer made. A
  call back changes the VERDICT on a dial already made, so it lands inside the
  numerator by turning that dial live. A cold call-in had no dial and sits
  outside the rate entirely.
- **ONE ACCOUNT, ONE CONTACT AND ONE ATTEMPT** (Frank, 2026-09-01). The same
  lead reached on two of their own numbers is one person: `_one_row_per_lead`
  collapses the Call Detail row and the duplicate dial is marked `dropped`, so
  it leaves the numerator AND the denominator. Reaching someone on their mobile
  after their landline must not read as a 50% contact rate. Mike / Nicole
  Santana, 2026-08-31 -- 252s and 67s on one lead -- and Roger Ryan before her.
  **Reached or not** (Frank, 2026-09-30): every counted dial on one lead
  collapses to one (`daily._one_attempt_per_lead`) -- the live number, else
  the one dialled most -- the rest dropped as "duplicate lead" with their
  attempts moved over, so an unanswered lead on two numbers is one dial, not
  two. A call-in from a dropped duplicate number stays a conversation
  (`finalize.conversations`).
- **An answered call-in is a conversation** (Frank, 2026-09-23). If it survives
  `inbound.screen` -- Accepted, and connected on a producer's own phone -- it is
  live, whatever the transcript says; the producer's "Thank you for calling
  Farmers" reads as an auto-attendant greeting to `transcribe.MACHINE`. Only a
  SAME-DAY call back may turn a dial live; any other call-in stays outside the rate.
  **A screened same-day call back makes its dial live, full stop** (Frank,
  2026-09-30): `is_live(..., callback=True)` is "answered call back" over a
  "no answer" note and under 60s. A screened call-in with no recording is
  still a conversation (an entry with no text: talk time and Call Detail,
  no coaching card); it is read once a recording appears.
- **Talk time counts every conversation**, inbound included. **So does the
  team's** (Frank, 2026-09-30): `finalize.team_avg_talk` weights each
  producer by live + inbound, `_totals`' own divisor, for the email and the
  board alike -- it was avg x outbound live only.
- **Notes win over the recording** (Frank, 2026-08-18). A producer writing "no
  answer" outranks a 12-second transcript that sounds live. Duration is the
  last resort and is labelled as such.
- **TRAQ auto-summaries are not producer notes.** They are machine output
  written on every call including voicemails.

## Identity and attribution

- **Producers**: Crystal Mango, Lorena Gonzalez, Mike Olvera, Coral Barwick,
  Sarahi Chin. Coral and Sarahi are full producers as of 2026-08-24 — the
  2026-08-28 review date is CLOSED. Sarahi's Insightful licence was assigned
  2026-08-25 and her utilization is live like everyone else's; `digest_config.
  NO_INSIGHTFUL_LICENCE` is empty and the panel branch that printed "no
  Insightful licence assigned" no longer fires for anyone.
- **Not producers**: Debbie Aguilera is the front desk and handles ~90% of
  inbound, transferring to whoever the call is for. Amanda Torricellas is
  operations manager, sells, and is deliberately not tracked.
- **Everything is keyed by (producer, number), never number alone.** Two
  producers work the same number on the same day often enough that keying on
  the number hands one of them the other's call.
- **Duplicate lead records are pervasive.** Read notes across ALL records on a
  number; prefer the one sold today when picking which represents the call.

## Phone numbers

`az_corpus.e164` keys on the **last ten digits**. AgencyZoom stores every number
as ten digits with no country code, so a Mexican number arrives from RingCentral
as `+526535380676` and from AgencyZoom as `(653) 538-0676`. Anything stricter
silently drops real customers.
**Dials are keyed that way too** (Frank, 2026-09-30): `day_calls.dials_from`
keys every dialled number by `e164` (a number too short keeps its raw form),
so a +52 dial meets its lead; transcripts, call backs, `task_audit` and the
Worker's `dialDeltas` / `speedToDial` use the same key.

## Rebuilding a past day

**Never re-fetch `data/az_service_tickets_<day>.json` for a day already built.**
Open tickets close overnight, so a rebuild disagrees with the original run.
The service-ticket test is point-in-time: a ticket counts only if it was created
on or before the day and was not already closed before it.

## THE RUN STARTS AT 5:35 PM AND PREFETCHES FIRST

**ONE ROUTINE RUNS THE WHOLE DAY** (Frank, 2026-09-28: "I want to consolidate
and have 1 routine that takes care of the whole day"). "Flores daily: hourly
checkpoints + 5:55 PM final (AZ)" fires `CRON_TZ=America/Phoenix 55 8-17 * *
1-5`: 8:55 AM-4:55 PM are checkpoints (`intraday.py`, then
`missed_call_tasks.py --live`), and **5:55 PM is the final run** -- Coach AI
from Gmail into `data/coach_<day>.json`, then `daily.py`, which sends, publishes
the boards and creates the rest of the day's missed-call tasks. It skips the
final if `publish_board.day_is_finalized` is already true. It runs in the
environment that holds the secrets (no credentials in the prompt) with Gmail
on the routine. The 5:35 PM "Flores Daily Sales Digest" routine and the seven
per-time missed-call routines are disabled, not deleted. The prefetch section
below describes that retired 5:35 flow; `hourly.py` is not needed at 5:55
because the checkpoints have already cached the day.

**This overrides the scheduled-task prompt, which still describes a single
6:45 PM `python3 daily.py` and is stale.** Changed 2026-09-01.

    1.  python3 hourly.py        <- FIRST. Downloads and transcribes the day.
    2.  wait for the Coach AI emails, then write data/coach_<day>.json
    3.  python3 daily.py         <- finds every transcript already cached

**Why.** Roughly 30 minutes of the old run was nothing but downloading
recordings: the agency averages 238 a day (peak 298) and RingCentral's media
endpoint allows 10 requests per rolling 60 seconds, so the downloader paces at
8/min and no amount of tuning makes one big pass faster. The office closes at
5:30, so by 5:35 every call of the day already exists. Doing the download while
waiting for Coach AI, instead of after it, moves delivery from about 8:10 PM to
about 7:00 PM.

`hourly.py` and `daily.py` share `data/`, and this is all ONE session in ONE
container, so the transcripts are simply there when `daily.py` runs. That is the
whole trick, and it is why this works when a separate hourly schedule does not:
scheduled runs get a COLD container every time (HOURLY_RUNS.md s12), so nothing
survives between them, and a scheduled session cannot push to the repository to
carry it either. Both were measured on 2026-09-01. Do not rebuild the separate
hourly schedule until one of those two facts changes.

**Coach AI's emails arrive at 5:30 PM Arizona** (Frank moved their send time
from 6:30 on 2026-09-28). Until then they landed at 6:30 every night
(measured 09-22..09-25: 01:30 UTC), and the nightly sat idle for most of an
hour waiting for them -- the digest went out 6:42-6:56, 12-26 minutes after
they arrived. The recordings, transcripts, call summaries and coaching cards
are NOT the slow part: the hourly checkpoints (`intraday.py`) build all of
them through the day into R2's cache/<day>/, so by 5:21 PM nearly every
recording is already there and the nightly only adds the last half hour's.
If the emails have not arrived, wait for them rather than writing zeros.

**Timing to expect.**

    5:30   Coach AI emails land
    5:35   hourly.py starts        a few minutes: only the calls since the last checkpoint
    ~5:40  Coach AI figures        already in the mailbox
    ~5:45  daily.py starts         transcription and cards already cached
    ~6:00-6:15  both emails sent   (was 6:42-6:56 with Coach AI at 6:30)

**`SEND_HOLD` stops the email only** (Frank, 2026-09-24: "i still want the
board to build"). A held night still publishes the Sales, Service and
Commercial boards and saves the day to R2; it skips the sales-log sync and the
AgencyZoom missed-call tasks along with the email. `--no-send` (hand rebuilds)
still stops before anything is published.

**Each audience that is emailed leaves a sent marker** (2026-09-30):
`data/sent_<day>_ops.json` / `_staff.json`, carried in R2 with the day's
files. A re-run skips an audience already sent, and says so; `--resend`
(or deleting the marker here AND in R2's cache/<day>/) sends it again. A
send that fails (after `send_digest`'s three tries) no longer stops the
run: the other audience, the boards, the R2 save, the sales log and the
missed-call tasks still run, then the run fails so the healthcheck alerts.
It also refuses to email -- boards still built -- when more than 10% (and
10+) of the leads' notes could not be fetched (`day_calls.notes_shortfall`).
R2 cache syncs and Insightful never stop the run; they log and carry on.

**The nightly run checks in** (`healthcheck.py`, Frank, 2026-09-29): with
`HEALTHCHECK_URL` (a Healthchecks.io ping URL) in the cloud environment's
variables, `daily.py` pings start, success ("sent" / "held") and failure
(with the traceback). Only a bare nightly `daily.py` pings -- never
`--day` or `--no-send`. The check's own schedule and grace time are what
alert when the run never started or hung.

A stall still means the log has not advanced in ~5 minutes, or repeated "rate
limited" lines. Judge it on progress, not on elapsed time.

`hourly.py` ends by trying to push the transcripts to the repo, and on failure
prints "COULD NOT SAVE THE TRANSCRIPTS ... pause it". In this single-session
flow that warning is meaningless — the transcripts are already on local disk,
which is all `daily.py` needs — so just note it in one line and carry on to
the Coach AI step. Do not treat it as a run failure and do not pause anything.
A real failure looks like a traceback or no `DONE:` line, and the response to
that is still the same: just run `daily.py`.

If `hourly.py` fails for any reason, **just run `daily.py`** — it does its own
downloading and the day still goes out, only later. Never skip the digest
because the prefetch broke.

## Live figures between checkpoints

**Today's board is the last checkpoint, with dials, sales, utilization,
quotes, contacts, talk time, texts & emails, speed to dial and task
completion kept live** (Frank, 2026-09-24: "just live data where its already at on
everything possible, and the header up there specifying what is stale from
the last hourly run"). No separate live strip: the Worker's `/api/live/<day>`
(`site/live.js`) is written into the same document the page renders. The
header shows only "Live · updated <time>" and "Last checkpoint <time>";
**a live figure has a pulsing green glow** (tiles, leaderboard cells, utilization cards),
and anything without the glow is the checkpoint's (Frank, 2026-09-24).

- **Dials** extend the checkpoint's OWN verdicts (`live_board.basis`, carried
  in the intraday document as `live_basis`), never re-decide them: excluded
  numbers stay excluded, a duplicate-lead number adds attempts only, and a
  number no checkpoint has checked counts as new business until one does.
  Record ids, not times, mark what the
  checkpoint saw.
- **Sales** are AgencyZoom policies by agentId + soldDate minus
  `lead_sources.NOT_A_SALE`, the same rule as `is_real_sale`.
- **Households sold** ride with sales (Frank, 2026-09-28): the same even-minute
  refresh reads every lead marked sold today (`site/live.js soldLeadsToday`,
  leads newest activity first back to Arizona midnight -- kept in R2 and
  topped up from the newest end each refresh, up to 5 pages), so
  HH/Prem. Sold glows whenever sales are live. That list stands on its own
  for the day; the checkpoint's `rows.sold_leads` are added only if the read
  stopped at the page cap. **The list the tile opens is the tile's**
  (2026-09-30): applyLive merges the live sold leads into `rows.sold_leads`
  (one per lead_id, the checkpoint's row keeping its source); a list with
  no live rows (dials, contacts, quoted, policies) under a live card says
  "Live figure; this list is as of the last checkpoint <time> -- N more
  since".
- **Utilization** is `insightful_util.pull()`'s formula.
- **Speed to Dial** (Frank, 2026-09-29: "make speed to dial live too") is
  worked out WHOLE every even minute (`site/live.js speedToDial`, a line-for-
  line mirror of `daily.speed_rows` / `speed_to_dial` -- keep them in step)
  from the day's kept lead list (every lead created today has activity today)
  and the full call log, so it is exact, not provisional, and it replaces the
  checkpoint's cards and their list. Only when the lead list is complete. The
  Team card is the median of every lead's seconds pooled (Frank, 2026-09-01);
  `board_payload.speed_to_dial` now pools the saved `secs` too instead of
  rebuilding them from each producer's summary -- 09-25's team read 69m23s
  that way against a true 34m56s. Checked identical to the Python on every
  day R2 holds a lead snapshot for (09-23, 09-24, 09-25, 09-28).
  **Three corrections** (Frank, 2026-09-30; published days not rebuilt): the
  first dial is the EARLIEST by any producer, credited to them (it was the
  first producer in the log's order); a lead "arrived today" by its
  createDate in ARIZONA time (UTC-7 -- a 5:30 PM lead was lost); both sides
  keyed by `e164`. `speed_to_dial` is now built from `speed_rows`.
- **Task Completion** (Frank, 2026-09-29: "task completion should be live")
  is worked out whole like Speed to Dial (`site/live.js taskCompletion`, a
  line-for-line mirror of `az_tasks.audit` -- keep them in step, rounding
  included: Python's half-to-even), from the producers' tasks due today,
  re-read every 5.5 minutes, one page per producer. The checkpoint hands
  over its own duplicate-lead / smart-cycle verdicts (`live_basis.tasks`);
  a task closed since is judged by the same patterns on the lead's stage
  moves, which the quotes pass already reads (`taskFlags`). Checked identical
  to Python on all 20 September days with a saved task file, both ways.
- **AgencyZoom's whole-day task list cannot be paged** (found 2026-09-29):
  its pages overlap, so 09-28's 214 rows gave 141 distinct tasks, and only
  115 of the producers' 183. Every Task Completion before 2026-09-29 counted
  about six in ten of their tasks (Lorena 15 due against a real 42; team
  85/96 against 151/164), and `missed_call_tasks`' duplicate check and the
  Service Center's task figures missed the rest too. `az_client.tasks` now
  reads each active employee on their own (`assigneeId`, one page each) and
  merges by id; the Worker reads the five producers the same way. Published
  days were not rebuilt.
- **A live sale goes on the Sales sheet in the same refresh** (Frank,
  2026-09-28: "the sales on the leaderboard are live, but the sales werent
  added to the sales sheet"). `site/live.js syncSalesLog` applies
  `sales_log_auto.sync_day`'s rules to `saleslog/<day>.json`: producers and
  Amanda (`live_basis.saleslog.ids`), BOB / Rewrite left out, product names
  by carrier (`productName` mirrors `product_name` -- keep them in step),
  only ever adding, never a policy already there or typed by hand. The name
  is the one lead marked sold today with the same agent and lead source,
  else blank.
- **Households and premium quoted** are daily.py's own three rules (quoteDate
  today; a producer's move into a quoted stage; a producer's note delivering
  a quote), applied only to leads active since the checkpoint, newest first,
  on top of the checkpoint's own `quoted_leads`. The regexes travel in
  `live_basis.quotes` from daily.py itself (`QUOTED_STAGE`, `_PRESENTED`,
  `_PAST`) -- never retype them in JS. Plurals count ("here are the
  quotes", "your quotes are attached"; Frank, 2026-09-24). A lead is re-read only when its
  lastActivityDate moves. The closing ratio is live once both sales and
  quotes are.
- **A one-minute Worker cron** (wrangler.jsonc, business hours) refreshes
  the parts in batches sized for the free plan's 50 outside requests per
  run: even minutes dials/contacts/sales/utilization, odd minutes up to 30
  lead reads (quotes, contact evidence and messages from the same reads). AgencyZoom 429s on bursts of note reads; a failed part keeps its
  last good answer for the same checkpoint instead of blanking the board.
- **The Worker logs in to AgencyZoom ONCE a day, not once a run.** A per-run
  login meant ~30 an hour, and on 2026-09-24 AgencyZoom began refusing the
  Worker's logins (403) within the hour while the same account still worked
  from the nightly run's machine. The token lives in R2 at
  `worker-private/az_token.json` (served by no route) and is shared by every
  run; a refused login pauses AgencyZoom for 30 minutes
  (`worker-private/az_pause.json`) instead of retrying every minute.
  **So does a refused REQUEST** (2026-09-28): from 2:29 PM every AgencyZoom
  call from the Worker got 403 -- sales, households sold, quotes and texts
  all stopped glowing -- while the same saved token answered 200 from the
  nightly run's machine (any User-Agent). AgencyZoom (nginx, not Cloudflare)
  was refusing the addresses the Worker calls from, not the login, and the
  Worker kept asking ~40 times every two minutes. A 403 now pauses every
  AgencyZoom part for 30 minutes (`site/live.js azGet`); the board keeps
  each part's last good answer for the checkpoint meanwhile.
  **And it asks less** (2026-09-29): the day's active-leads list is KEPT in
  R2 (`live/<day>-leads.json`) and each even-minute refresh pages only down
  to where the last one started (any change to a lead puts it back on top),
  usually one page instead of up to five; the quotes pass reuses that copy
  instead of paging its own (`fromShared`); lead source names are fetched
  once a day (`worker-private/lead_sources.json`). Same figures, measured on
  a mocked day with leads marked and unmarked sold: 132 AgencyZoom requests
  -> 75 over 30 refreshes.
  **It calls api.agencyzoom.com** (Frank, 2026-09-30), the address
  AgencyZoom's published spec gives integrations
  (api.agencyzoom.com/openapi/agencyzoom.yaml: "rate limit of 120 calls per
  minute during the day and night"), not app.agencyzoom.com, the web app's
  own -- a separate AWS load balancer. The refusals above were all on the
  app address, from 2:29 PM two days running whatever the volume; same
  endpoints, data and login on both (checked 2026-09-30). The nightly run
  still uses app.agencyzoom.com (never refused). **Every AgencyZoom request
  is counted** by hour and endpoint, and every refusal kept whole -- status,
  headers (`server` says whose firewall), the first of the body, and the
  address Cloudflare sent it from -- in `worker-private/az_log/<day>.json`
  (`flushAzLog`, once per run). Read that before guessing why it refused.
- **Contact rate, live contacts and Avg Talk Time are live too** (Frank,
  2026-09-28: "avg talk time, contact rate, and texts and emails should all
  be live as well"), and they are PROVISIONAL: the Worker cannot hear a
  recording, so a dial since the checkpoint is judged by `is_live`'s order
  with the recording left out -- a producer note stating contact, a
  no-contact note, an outcome note, TRAQ's voicemail summary, RingCentral's
  disposition -- then, with nothing written, a leg of 60s or more
  (`live_board.PROVISIONAL_LIVE_SECONDS`; measured 09-22..09-25: day totals
  27/12/12/13 against the recordings' 31/11/11/13, about a third of the
  individual calls wrong either way). The next checkpoint reads the
  recordings and settles every one. A counted number is judged only on its
  new legs and the notes written since; an excluded one stays excluded; a
  call back turns its dial live; any other answered call-in adds talk time,
  never a contact -- **but only on a number the checkpoint kept, is already
  talking on, or the lead notes show is a lead's** (2026-09-30:
  `live_basis.inbound` carries inbound.screen's in / out numbers; a
  screened-out or unplaced call-in waits for the next checkpoint).
  **Team Avg Talk Time live is total seconds over total conversations**
  (live + inbound + the live deltas), like `finalize.team_avg_talk`, and a
  range weights each day's talk by live + inbound; rates and averages round
  half-to-even like Python (`pyRound`, 2026-09-30). The rate is live contacts over LIVE dials, so it is live
  only when dials are. The notes come from the quotes part's own reads
  (dialled leads first), so it costs no extra AgencyZoom requests.
  `site/live_notes.js contactDeltas`; the checkpoint's side is
  `live_basis.live` / `.talk` / `.contact`.
- **Texts & emails are live** the same way (`live_notes.messageDeltas`,
  `live_basis.messages` from `messages.build(live=True)`): the checkpoint
  hands over, per person, the newest note it read, who last typed to them,
  who has messaged them today and the reply still waiting; the Worker adds
  only what is newer, by messages.py's own patterns and templates. Checked
  against a full rebuild at 12 checkpoint times on 09-23 and 09-25: every
  count and reply row identical, except one tie between two producers'
  duplicate lead records, which Python breaks by corpus order the Worker
  cannot see (the next checkpoint fixes it). **A wait is one row however
  many messages it holds** (2026-09-30): the checkpoint hands over the run
  nothing has answered yet (`people[].run`: start, messages, ack / opt-out /
  wrong so far) and the Worker adds to it, re-judges it over all its
  messages and moves its counts (an "ok" then a question is one waiting
  row from the "ok"; minutes run from the first message). `seen` is the
  newest TEXT / EMAIL / TEXT-FAILED / CALL note only (a TASK note is stamped
  the evening before). The closing ratio falls back to the checkpoint's
  (`cp_pol`/`cp_ps`, and since 2026-09-30 `cp_hh`/`cp_pq` and the
  checkpoint's sold-lead rows for the households half) until
  `liveOn(d, "closing")` -- sales, quotes and households sold all live.
- The Worker needs its own secrets, set in Cloudflare (Workers & Pages ->
  flores-board -> Settings -> Variables and Secrets, type Secret):
  `RC_CLIENT_ID`, `RC_CLIENT_SECRET`, `RC_SERVER_URL`, `RC_JWT`,
  `AZ_USERNAME`, `AZ_PASSWORD`, `INSIGHTFUL_TOKEN`. A missing one leaves that
  part on the checkpoint, so it simply does not glow. **The header never
  lists what is or is not live, or why** (Frank, 2026-09-25: "I know whats
  flashing green is live, and whats not flashing green is not") -- do not
  add that back.

## The Digest's cards open their rows

**Every card on the Sales Center's Digest opens the list it counts** (Frank,
2026-09-27: "like we did on the service digest"): Dials, Live contacts,
HH/Prem. Quoted, Pol/Prem. Sold, Closing Ratio, Speed to Dial, Speed to
Reply and the Call Outcome Breakdown's segments and legend.
`digest_rows.py` puts the rows in the day document's `rows` (dials,
contacts, quoted, sold, sold_leads, speed); no figure on the page comes
from them, and the lists must agree with the cards: a call-in is a
conversation but sits OUTSIDE the contact rate, so the Live contacts list
says "N in the contact rate · M call-ins". daily.py keeps the premium quoted
per lead (`quoted_premium`) and `speed_rows` -- the same first-dial rule as
`speed_to_dial`, so the list matches the tile. Policy records carry no
customer, so Sold lists the leads marked sold beside the policies. Past days:
`python3 digest_rows.py --backfill 2026-09-01` from R2's saved inputs (no
quoted premium, and no quoted list before 2026-09-24's `quoted_leads`).
**Everything on the Digest opens its accounts** (Frank, 2026-09-29:
"anything we add/create should be clickable to display the accounts"), and
anything added later should too. The leaderboard's numbers open that
producer's list under the leaderboard (the Team row, everyone's):
dials, talk time and contact rate the contacts, quoted, sold, and **Sent
the Quote** every call where a quote came up (the cards' `sendoff`); Texts
/ Emails goes to the Texts & Emails page. Task Completion's rows open the
tasks in the rate (`rows.tasks`, from `az_tasks.audit`'s own `items`, from
2026-09-29 on) and Household Completion's cards the policies sold, cross-
sells marked. Role play and utilization have no accounts behind them.
A tab that fails to draw (an old or partial document) shows "This section
could not be drawn: <message>" under its date controls instead of a blank
page (2026-09-30).

## Apollo's Road Map (ARM) and the tour

**Learning Center > Apollo's Road Map is one tab with a dropdown** (Frank,
2026-09-30: "if Im out for a week and want amanda to coach, she should know
what everything means, how the model coaches, where everything is ... in
regular language, not AI prompt language"; "Apollos road map should be the
name of the full tab, with a dropdown that has options for manager/coaching,
and one for the 3 producer levels"): **Manager / Coaching** (the ARM, shown
only to `ROLEPLAY_HISTORY_VIEWERS`, via the Worker's `/api/me`) and **New /
Mid-Level / Experienced Producer** for everyone. **Service Center > Athena's
Road Map** is the service team's (Frank, 2026-09-30: "make an Athena Road Map
for the service team too"): Amanda's Service Playbook in plain words plus how
the Service Center counts, for everyone; when `service_playbook.py` changes,
it changes with it. The words live in `site/public/blueprints.js`, nowhere
else (`map` = which tab, `label` = the dropdown name).
**Take the tour** at the foot of the left bar walks anyone through the
board (`TOUR_STEPS` in index.html).
**KEEP THEM CURRENT, in the same change** (Frank: "continues updating as we
make changes"): anything that changes what a number means, a goal, how
Apollo reads or scores a call, what a page shows or where it sits, or adds
a page, also updates the matching lines in `blueprints.js` (and a tour step
if a page moved or was added) and moves its `updated` date. Write them the
way you'd explain it to a person at their desk -- no field names, file
names or prompt wording.

## Date ranges on the Digest

**The range leaderboard is re-ranked on averages** (Frank, 2026-09-28):
the same seven categories and 5-4-3-2-1 scoring as a single day
(`rankLeaderboard` on the board, a mirror of `digest_config.
leaderboard_score` -- keep them in step; checked equal on 200 random
cases), fed each producer's range figures: dials, households quoted,
premium quoted and premium sold as **per-day averages over the days they
worked** (a day off costs nothing), talk time and contact rate as the
range's own. **Role play is shown one way and ranked another**: the Role
Play column is the true average of the sessions they did; the ranking
uses `rp_scored`, where a day they WORKED without a role play counts as 0
("hurt their points but not average"). A day off, or a day with no role
play figures for anyone (no Coach AI email), counts neither way.

## Households, not policies, on the Digest

**Sold is counted in households, like quoted** (Frank, 2026-09-28: "it
needs to be one or the other. i would prefer HH"). The board's **HH/Prem.
Sold** tile, the leaderboard's **HH Sold** column and the Closing Ratio's
households half (households sold over households quoted) count the leads
marked sold (`rows.sold_leads`; live, the sales refresh's own read of
today's sold leads), one per household per day -- `household` is the lead's
convertedHouseholdId, else its name, since duplicate lead records are
pervasive. **A BOB / Rewrite lead (`lead_sources.NOT_A_SALE`) or a test lead
(`digest_config.is_test_lead`) is not a household sold** (Frank,
2026-09-30), in `digest_rows` and `live.js soldLeadsToday` alike
(`live_basis.test_lead`). **Premium Sold is still the policies' own premium** and the
policy count still shows beside it (policies per HH). A lead can be marked
sold a few days off its policy's soldDate, so a day can show a household
with no policy or the reverse. A day with no sold-lead rows keeps the old
Policies display. The emailed digest is unchanged.
**Household Completion is policies sold over those same households sold**
(Frank, 2026-09-29: "too much description on the bottom, even im
confused"): no more policy -> lead match (it placed about half of sales and
blanked Coral's 3-policy household on 09-28), no "0+ new bundle" or
"matched" line. Under the number, how many were existing customers (the
sold lead's source is `lead_sources.EXISTING_HOUSEHOLD` -- a cross-sell) and
how many new, from each sold lead's `existing` (digest_rows, live.js;
09-01..09-28 tagged from their saved source, backups under
`backups/2026-09-29-hh-existing/`). A day with policies but no household
marked sold, or the reverse, shows "—" and says which.
**Its colour is what was sold, not a threshold** (Frank, 2026-09-29): green
for an existing customer (the household's source, or the policy's own
cross-sell source) or a new household that bundled (more policies than
households, every one new); yellow when every sale was one policy to a new
household; a red "—" for no sales (every producer gets a card). A day with
policies and households on different days, no cross-sell, is uncoloured.
The Team card takes its producers' best colour. The old 1.5 / 1.1
policies-per-household thresholds are gone.

## Texts and emails

**`messages.py` builds the Sales Center's Texts & Emails page** (Frank,
2026-09-27), into the day document's `messages`, from the lead notes the run
already downloads. Leads only; a customer's texts are Athena's.
- **Who sent it:** TEXT/EMAIL notes carry `attr.outbound` (True/False on a
  text, 1/0 on an email -- `messages._inbound` reads both); a text with
  `attr.triggerRuleId` is an AgencyZoom automation. **Emails have no
  automation marker**: a template subject (`TEMPLATE_SUBJECTS`, plus any
  subject sent to 5+ leads that night, lead's first name stripped) is
  automation unless it has an attachment, or is a "Re:" to a lead who had
  emailed us first -- drips send "Re: Your insurance quote options" to look
  like replies. Automation is counted apart and never credited.
- **A reply belongs to whoever last typed to that person** (else the lead's
  producer); someone else's -- Debbie on a payment -- is service and stays
  out. It is answered by the next typed text or email, any call back (the
  RC call log or AgencyZoom's CALL notes), or a call the lead made that was
  still going when the text arrived (30s+). One row per wait; "ok" / "thanks"
  and STOP are counted but never listed as waiting.
- **Replies are windowed from the office's close the business day before**
  (5:30 PM) to 5:30 PM, so evening and weekend replies land on the next
  business day; the clock starts at 8:30 for a reply that came in closed.
  daily.py downloads notes for every producer lead active in that window
  (`messages.active_leads`) -- lastActivityDate is UTC.
- Quotes sent are `daily.quote_presented` or an email attachment; opens are
  AgencyZoom's tracking as of that night. Rows, never medians.
- **On the Digest** (Frank, 2026-09-27; the email is unchanged): a **Speed to
  Reply** card beside Speed to Dial -- median time to answer per producer,
  green at 15 minutes or less, red over an hour (`REPLY_GOAL`), with the
  replies still waiting -- and a leaderboard **Texts / Emails** column of what
  each producer typed themselves, uncoloured until Frank sets a goal.
- **Past days: `python3 messages.py --backfill 2026-09-01 [end]`** (Frank,
  2026-09-27). Notes hold a lead's whole history, so it reads every producer
  lead active since the start (paced, ~1,800 leads for September), backs each
  R2 day up under `backups/<today>-messages-backfill/` and adds ONLY the
  `messages` key -- every other figure stays as it went out. A day that
  already has one is left alone (`--force` rebuilds). Past days have no RC
  call log on disk, so call backs come from AgencyZoom's CALL notes only, and
  email opens are as of the backfill.

## Service ticket status is DELETED/LIVE, not OPEN/CLOSED

**Corrected 2026-09-02 — do not revert to the 2026-09-01 understanding.**
Ticket `status` is not open/closed. Frank confirmed against AgencyZoom:
**status 0 is DELETED** (two he couldn't find at all, a third with a deletion
event in its own activity log; median age 812 days, 61% over a year old,
nearly all stranded in stage "New") and **status 1 is LIVE** (median age 28
days; Dana Sanchez and Genaro Cortez, both hand-confirmed active on 08-25,
are in this set). There is no closed state in this payload at all.

`az_client.service_tickets_live()` (renamed from `service_tickets_all`)
passes `status: [1]` only — a deleted ticket should never have been fetched.
`inbound.py` and `day_calls.py` drop only the `lastActivityDate` fallback
added 09-01 to guess a close date for a "closed" state that doesn't exist;
they keep a bare `completeDate` check (only 7 of 705 tickets carry one, but
where it's set the work was genuinely done as of that date) alongside the
`createDate` point-in-time guard. `missed_call_audit.route()` tests
`status == 1` for a live SR, not `status == 0` — but a *lead's* `status == 0`
in the same function genuinely does mean open and is untouched; same field
name, different object. That function also maps a ticket's `csr` id to a
first name (`CSR_NAMES`), since `csrFirstname` comes back null on every row
from the list endpoint.

**Status 2 is COMPLETED** (found 2026-09-23). "No closed state" above is true
of what `service_tickets_live()` asks for, not of AgencyZoom: requesting
`status: [2]` returns every completed ticket (19,287) with `completeDate` and
`resolutionDesc`. Screening calls still wants live tickets only. The completed
set is read by `service_digest.py` alone, for resolution times.
**A completed SR can leave the completed list** -- reopened (Late Payments SR
12245539: completed 09-01 by Debbie, reopened 09-24 by Amanda). So
`service_digest.completed_tickets` adds back anything in the last saved
day file that a new pull is missing: a past day's completed SRs never shrink.
## Athena -- the service digest

**Athena is the service side's name** (Frank, 2026-09-23), as Apollo is sales
coaching's. `service_digest.py` builds `service/<day>.json`; the board's
Service Center renders it. The team is Debbie (CSR) plus Amanda (Ops Mngr) and
Crystal (hybrid); credit always goes to whoever COMPLETED the SR or task.

- **Say "SR" (service request), never "ticket"** -- on the board and in
  anything the agency reads.
- **The pipelines, as the agency uses them** (Frank, 2026-09-23). Only Late
  Payments is worked stage by stage; for the rest Athena tracks created ->
  completed and nothing about stages.
    Personal Renewals        Farmers & Foremost renewals: completion time + outcome %
    Other 30 day Renewals    Bristol West renewals: same
    Service Pipeline         changes, endorsements, basic service: completion time
    Late Payments            stage breakdown + completion time
    Contingencies            any contingency pending on a policy (AgencyZoom's "Missing
                             Documents", renamed by Frank 2026-09-24; key missing_docs):
                             completion time + whether the SELLING producer or a
                             service/hybrid rep closed it
- **The Renewal Outcome Breakdown is not an agency retention rate.** It is the
  outcomes of the renewal SRs COMPLETED in the filtered period, and a rate
  among just those. From 2026-09-24 the outcome is the SR's own resolution
  (Frank's six: Renewed: Accepted as is / Endorsed, Rewrite Accepted,
  Cancelled: Rewrite Declined, Cancelled, no endorse/rewrite available, Unable
  to Contact) plus a seventh, **No action: Review if needed** (id 101591,
  added 2026-09-24: the rep reviewed the renewal and did not call because the
  change did not call for it). **Unable to Contact and No action both renewed
  as is** (Frank, 2026-09-24) -- nobody discussed the renewal with the
  customer -- so both count as RETAINED in the rate, each on its own segment. **The six are read on
  PAST SRs too** (Frank, 2026-09-24): the ids now carrying those names meant
  the same outcomes before the rename. **Except Unable to Contact before
  2026-09-24** (`RESOLUTION_VALID_FROM`): deleting a resolution in AgencyZoom
  MOVES its SRs onto another, and the clean-up moved Shot Clock Expired (357
  renewal SRs) and Unable to Complete (112) onto Unable to Contact, which had
  been used once. Never trust an id's history after a deletion without
  checking the counts.
- **FRANK'S RESOLUTIONS ARE THE ONLY OUTCOMES** (Frank, 2026-09-24: "those
  are the ONLY outcomes i want being used"). No category of ours -- no policy
  record reading, no "Renewal date still ahead", no separate "(rep's notes)"
  segments. Every renewal SR lands on one of the nine (the seven above plus
  **Client Cancelled**, id 101627, added 2026-09-24: went to the carrier to
  cancel, or never gave us the chance -- LOST, in the rate -- and
  **Mid-term Cancellation**, below), matched by resolution
  ID (`RESOLUTION_KEY_BY_ID`, so a rename in AgencyZoom breaks nothing):
    1. the SR's own resolution;
    2. closed on anything else (Completed): the rep's note, read by the model
       into one of the nine (`renewal_notes.py`; keyword rules misread
       "possible deductible options" and "left vm and autos on noc" -- do not
       go back to them);
    3. no note, or a note that does not say: **Unable to Contact/No Show**
       (Frank renamed Unable to Contact to that, 2026-09-24).
  **The customer's texts help decide** (Frank, 2026-09-27: "i want the
  texts to be used to help decide ... it should be built in"):
  `service_messages.renewal_texts` gathers every text between the customer's
  numbers and the service lines from the SR's createDate to 3 days after it
  closed (only when the customer wrote back or someone typed to them), and
  `renewal_notes.read_texts` reads them ON THEIR OWN into leaving /
  sold_moved / already_cancelled / discussed_kept / discussed_changed /
  other. `service_retention.with_texts` then applies them to the note's read
  by rule: leaving -> Client Cancelled, sold -> Sold/Moved, already gone ->
  Mid-term Cancellation, a renewal talked over -> Accepted as is (Endorsed
  if a change was made) -- the last two only over No action, Unable to
  Contact or a note that does not say. **Never one prompt with note and texts
  together**: tried 2026-09-27, the model let payment and ID-card texts turn
  "Already reviewed" into "unclear" and No action into Unable to Contact (22
  of 61 SRs). **Checked in code, not only asked** (`renewal_notes._guard`):
  leaving / sold / already cancelled need the CUSTOMER's own text to say so
  (cancel, switch, sold, moved ...) -- Kenneth Lansford's "Stop" to a
  bundling text is not leaving, a rep's non-payment warning is not a
  cancellation; a renewal "talked over" needs a customer text; texts make an
  Endorsed only where there is no note (over "no premium change, review if
  needed" it is Accepted as is). Gone before the SR opened (the customer's
  first such text, or the policy record) is Mid-term; on or after is Client
  Cancelled, lost -- the note's date rule. Isaiah Tullis (noted "renewed"
  09-22, texted 09-23 "We've decided to switch insurance providers") is the case. Source `notes+texts`
  / `texts` when the texts changed it; each row keeps `texts`. The texts come
  from `data/rc_texts_archive.json` (+ R2 copy, 240 days, topped up every 12
  hours); text reads share the note cache under `tx:<id>`.
  **Mid-term Cancellation** (id 101637, Frank added it 2026-09-24: "mid term
  cancellations, prior cancellations, anything that cancelled prior to
  renewal SR generating") is an old SR closed out on a policy already
  cancelled ("Cancelled in 2025", "sold home", all 22 cancellations
  09-01..09-23). It shows hatched, OUTSIDE the rate (key
  `cancelled_before_sr`). A cancellation resolution on a policy the record
  shows cancelled well before the SR was opened lands there too. The policy
  record is read for that and for the premium, nothing else.
  **How the notes read** (fixed 2026-09-24 from a spot-check of all 274
  renewal SRs 09-01..09-23): a bare "renewed" / "reviewed" is No action; a
  customer who reviewed it with a rep and changed nothing is Accepted as is,
  even with changes planned for later; bad number / bad email is Unable to
  Contact; "cancelled in 2025" is Mid-term Cancellation. The read cache is
  keyed by SR and note, not prompt, so a prompt change reaches only new
  notes -- re-read old ones by removing just their entries, never the file.
- **A Mid-term Cancellation is flagged when nothing dates it** (Frank,
  2026-09-27: "flag them"). AgencyZoom has no cancellation date, and a policy
  record never changed after it was loaded (modifyDate on createDate's day)
  dates nothing -- Alan Garcia Cabrera's G015059251 read "changed 06-26", the
  day its 02-16 term was loaded; he was lost at the 08-16 renewal (late
  payment 08-21, Win Back 09-22). `service_retention.cancel_flag` marks the
  row "not dated" (that record, and a note with no year / date / sold /
  transferred) or "after the SR opened" (the note's own date is on or after
  the renewal SR's createDate -- Paloma Juarez, cancelled 07-24, SR 07-15).
  The outcome stays as is; the Service Center lists them as cancellations to
  check. Do not count them as lost without Frank. **But a note that dates the
  cancellation on or after the renewal SR opened is not flagged -- it is a
  cancellation DURING the renewal and the team's cancel resolution stands,
  LOST** (Frank, 2026-09-27: "you put notes that clearly state what
  happened" -- Paloma Juarez 07-24, Eduardo Sanchez 09-22, Luis
  Alvarez-Hernandez 09-02). **Cancelled: Sold/Moved** (id 101638, added
  2026-09-27) is its own outcome, OUTSIDE the rate, on the Service Center and
  the Renewals tab (status `sold_moved`) alike.
- **Past days' renewal rows are re-read every night**
  (`service_digest.refresh_past_renewals`, last 120 days): a day's document is
  built once, so without this a note read (or a resolution renamed) after the
  night a day was built would never reach it. Only each row's outcome and
  source change; which SRs
  are in a day, and every other section, stay as first built. **Resolution names come from `/v1/api/service-resolutions`**
  (found 2026-09-24), re-read every build; `RESOLUTION_LABELS` is that list as
  of 2026-09-24, the fallback. A renewal SR closed from 2026-09-24 on anything
  else (Completed, Shot Clock Expired, Unable to Complete, Cancelled by
  Carrier/Client) is also listed on the Service Center as not one of the six;
  before that date "Completed" was the normal choice, so it is not flagged.
  On 2026-09-24 Frank deleted every other resolution in AgencyZoom except
  **Completed, which is for changes, NOC and missing documents -- not
  renewals**. The deleted ones stay in `RESOLUTION_LABELS` because past SRs
  still carry their ids; do not prune them. `python3 service_retention.py --resolutions`
  prints each id in use with examples.
- **Every pipeline has its own daily outcome breakdown** (Frank, 2026-09-24):
  of the SRs COMPLETED that day, how each ended -- Renewals (above), plus
  **Late Payments** (Paid / Cancelled for non-pay / Client cancelled / Unable
  to Contact / Other; "saved" = paid over paid or cancelled), **Service
  Pipeline** (Change made / Policy cancelled / Other service / Not done /
  Unable to Contact; no rate) and **Contingencies** (Cleared / Policy
  cancelled / Closed, not cleared / Unable to Contact; "cleared" rate). These
  SRs are all closed on Completed, so **the outcome is read from the rep's
  note** ("go based off of the notes for now") by `service_notes.py`, its own
  cache `data/service_note_reads.json` + R2 copy, never the renewal one. No
  note is "No note". These are categories of ours: if Frank adds AgencyZoom
  resolutions for these pipelines, match them by id first. Each completed row
  now carries its SR `id`, `outcome` and `source`; the nightly refresh adds
  them to earlier days, matching old rows (built without an id) by who
  completed the SR and its hours.
- **Renewal SRs are the Renewals tab's, not the Service Digest's** (Frank,
  2026-09-27: "a service digest and a renewal digest, but no changes to the
  tab titles"). The board's `splitRenewals` takes the two renewal pipelines
  out of every Service Digest figure -- SRs completed, completion time, each
  person's open and overdue -- and the Renewals tab's **Renewal SR Work**
  shows them: completed in the last 28 days per person and pipeline, created
  to completed, and the open ones. The documents still hold every row; the
  split is made on the board, so every published day splits the same way.
  **Renewal tasks go with them** (Frank, 2026-09-27: "I see renewal tasks in
  the list"): a task whose title says renewal ("♾️Personal Renewal 30 Days",
  its shot clock reminder, "Renewal we have renewal info") leaves Service
  Tasks Done and is counted on the Renewals tab; the counts are rebuilt from
  `task_rows`, which reproduce `task_figures` exactly (09-01..09-25).
  **Call backs, texts and emails too** (Frank, 2026-09-27: "everything should
  be separated if possible"): a number is renewal business when every SR it
  has open at the end of the day is a renewal SR (`service_digest.
  renewal_caller`); a text or email also is when it mentions the renewal
  (`service_messages.RENEWAL_WORDS` -- the reminders), and so is a reply to
  one. Rows carry `renewal`; the board splits them and rebuilds the message
  counts from the rows. Utilization cannot be split (Insightful measures the
  whole day). 09-01..09-25 were flagged from their saved files (backups
  under `backups/2026-09-27-renewal-split/`).
- **Renewal SR Work is the Service Center's person strip** (Frank,
  2026-09-30: "same as the service center, person strip with team
  totals"). The agency's retention rates stay on top; under them one small
  card per person (renewal SRs, retained, open, overdue) and one grid -- the
  team's until a person is picked (`renPerson`), then theirs
  (`renewalWorkHtml(m, doc, rb)`): renewal SRs completed, retained (of the
  renewal SRs completed), reviewed with the customer (every outcome but No
  action / Unable to Contact and the two outside the rate --
  `REN_DISCUSSED`), renewal tasks, open / overdue, coming up and high risk,
  settled 4-week retention and lost (the policies on their renewal SRs),
  renewal dials, call backs, speed to reply, texts / emails. Every card
  opens its accounts (`rw:<list>[:<person>]`). The settled section's "By
  who worked the renewal SR" row went into the cards.
- **Both tabs take the Sales Digest's date filter** (Frank, 2026-09-27).
  On the Renewals tab, Renewal SR Work, Lost and Not confirmed follow it
  (Lost and Not confirmed by the day the policy renewed); Coming up stays
  the next 45 days.
- **Renewal Outcome Breakdown on the Renewals tab** (Frank, 2026-09-28: "the
  same way we display the call outcome breakdown on the sales digest. Per
  CSR rep and a total"): `renOutcomeHtml` -- a bar per person who completed
  renewal SRs in the date filter's period, scaled to the busiest, split by
  Frank's resolutions; the team is a totals line, not a bar ("so the
  producer bars are the main focus"). Segments and legend open the SRs.
- **Three retention rates** (Frank, 2026-09-27: "build all three"): the
  **settled 4 weeks** (renewals 14-41 days ago, `REN_SETTLE_DAYS`; the
  newest two weeks show as settling, and the breakdowns by week, how worked,
  pipeline and person are these four weeks), the **date filter's period**,
  and the **last 12 months** -- the one to set beside Farmers'. So
  `renewal_report.PAST_DAYS` is 365 (the report is ~2.4 MB). A year measured
  2026-09-27: losses do not show up late; only "not confirmed" settles.
  **Cancellations to check** (the "not dated" flag) moved to the Renewals
  tab too, from `renewal_report`'s `sr.flag`: a dropdown, closed until
  clicked, following the date filter by the day the policy renewed (Frank,
  2026-09-28).
- **The Renewals tab is its own report** (Frank, 2026-09-25: "service cant be
  tracked daily the same as sales"). `renewal_report.py` builds
  `renewals/current.json` (and a dated copy) every night from `daily.py`
  after the service board; the Worker serves it at `/api/renewals`, and the
  Service Center's second tab renders it. The Service Digest keeps only a
  count of renewal SRs worked. It covers every personal-lines policy TERM
  (commercial and life left out) renewing in the last 365 days -- what
  happened -- and the next 45 -- how the renewal SR was worked, and risk.
  **The policy record counts** here (Frank, 2026-09-25: "if the policy reads
  cancelled but no SR has that outcome ... its still cancelled"), beside the
  team's SRs: lost = the record shows it cancelled from 30 days before the
  renewal on, a Late Payment / Service Pipeline cancellation SR ties to it,
  or the renewal SR closed on a lost resolution; retained = a next term, a
  same-line rewrite, or Rewrite Accepted on the renewal SR (a rewrite cancels
  the old policy by design). **Mid-term Cancellation stays out of the rate**
  ("no mid term are not considered in the rate"), and so does "not confirmed
  yet" (the records lag). A cancellation SR carries a household, never a
  policy (a Late Payment SR's description is a billing table), so it ties
  only when the household has ONE renewal near it, or one of the line its
  note names; otherwise it is a risk flag. **No premium-change figure**:
  AgencyZoom terms carry stale premiums and disagree with the reps' own "low
  increase" notes (540881890: $382 -> $1,080), so risk uses the SRs only
  (not discussed + an open Late Payment or cancellation SR on the household).
  The renewal-SR outcome columns in `service/<day>.json` stay as before.
- **A missed night builds itself** (`service_digest.backfill_missing_days`,
  Frank, 2026-09-24): each nightly run builds any weekday of the last 14 with
  no page, from that day's saved files; completed SRs, tasks (completed after
  the day = open) and the call log are recreated if they were never saved.
  Open SRs cannot be -- such a day has no backlog and says so
  (`open_srs_unavailable`). A weekday with no SR completed is a holiday and
  skipped. It only ever adds a page. By hand: `python3 service_digest.py --backfill`.
- **Texts and emails with customers are `service_messages.py`** (Frank,
  2026-09-27: mirror the Sales Center's), the document's `messages` key and
  the Service Center's Texts & Emails section. **Texts come from RingCentral's
  message store** (`rc_client.texts`, every text on Debbie's, Amanda's and
  Crystal's own lines, saved as `data/rc_texts_<day>.json` + R2 day cache),
  **never AgencyZoom's TEXT notes**: AgencyZoom sends through those same
  lines, so reading both counts each text twice. **Emails come from
  AgencyZoom** notes on the customer's lead records (RingCentral has none;
  Outlook is not seen). RingCentral marks nothing as automation, so a body
  one person sent to 5+ numbers in 30 days (name and numbers taken out) is
  automation, counted apart; a picture or PDF is always typed. Only numbers
  that route to service count (`missed_call_audit.route`: customer, open SR);
  leads are Apollo's, commercial-only households Cerberus's, and a number
  AgencyZoom does not know is counted but never listed. Replies, answers and
  the window follow `messages.py`. **Card, bank and social security numbers
  are removed before anything is stored** (`messages.redact`, both sides) --
  customers text card numbers to pay. Past days: `python3 service_messages.py
  --backfill 2026-09-01 [end]` (adds only `messages`, backs up under
  `backups/<today>-service-messages-backfill/`).
- **Amanda's Service Playbook is how Athena judges the service team**
  (Frank, 2026-09-28: "Teach Athena this and build the digest to be focused
  on their own roles and responsibilities"). `service_playbook.py` is her
  document -- roles, who handles what, the note standard, the daily checklist,
  the team expectations -- and the only place to change it; each day carries
  it as `playbook`. Roles: **Service Lead = Amanda, Service Team Member =
  Crystal, Front Desk = Debbie** (`ROLE_OF`). **Crystal and Amanda sell**
  (`SELLS`; Frank, 2026-09-28: "she can do the opportunity herself, amanda as
  well. Debbie is the only one that would identify and pass to any
  producer"): the playbook's "identify opportunities to pass to a producer" is
  Debbie's line; theirs is "work the opportunities that come up" (quoted, a
  lead set, or passed -- versus not noted). `service_audit.py` reads every
  completed SR against it (request type from her "Who handles what" table,
  which of Who / What / Why / Outcome / Next step the note leaves out, a
  sales opportunity passed or not, escalated), cached by SR + note text in
  `data/service_audit_reads.json` + R2 -- a paid read, never delete it
  casually. A renewal reviewed without contacting the client ("low increase,
  review if needed") answers who and why. `front_figures` adds the Front
  Desk's rows: inbound calls each team member picked up first, and the SRs
  each created. The Service Digest's **By Role** cards give each person the
  measures of their own role's responsibilities in her words (the Lead's
  "not the default person" is the share of her SRs that were routine), and
  **Note Standard** counts the missing parts. Past days: `python3
  service_digest.py --add-roles 2026-09-01 2026-09-25` (backs up under
  `backups/<today>-roles/`).
- **The Service Digest is one card per person, no leaderboard** (Frank,
  2026-09-29, option D: "when I dont have a rep selected i want it to display
  the team totals"). A strip of small cards (Amanda, Crystal, Debbie in the
  playbook's order: SRs, tasks, reply speed, overdue); under it one grid --
  the team's totals until a person is picked, then theirs with their role's
  checklist from the playbook (`serviceStatsHtml`): SRs completed, tasks,
  open / overdue, dials, call backs, speed to reply, texts / emails, calls
  answered, SRs created, note standard, opportunities, utilization. Nobody
  is ranked; every tile opens its accounts (keys `g-...`). It replaced the
  Service Team tiles, By Role cards and Speed to Call Back by person.
  **Dials** are `service_digest.dial_figures` (`dials.rows`, one per person
  and number, from the day's RC call log): Debbie's and Amanda's every dial,
  **Crystal's only to numbers that route to service** (customer or open SR;
  her new-business dials are the Sales Center's), commercial-only households
  left out, renewal numbers split to the Renewals side. Past days: `python3
  service_digest.py --add-dials 2026-09-01 2026-09-28` (backs up under
  `backups/<today>-dials/`, adds only `dials`). The Renewals tab is next.
  **Laid out for the full-width board** (Frank, 2026-09-30: "it looks
  off"): the person strip is three equal columns (`.svcstrip`), the stat
  cards come in even rows of six (`.svcgrid`; four, then two, on narrower
  screens), Texts & Emails stays full width, and the rest sits two to a row
  like the Sales Digest (`.digestgrid`): Note Standard, Completion Time and
  Late Payments on the left, the pipeline outcomes and Contingencies on the
  right.
- **Every recorded service call has its full transcript** (Frank,
  2026-09-30: "full transcripts for service calls too"). `service_calls.py`
  takes exactly the calls the Service Center's rows list -- every inbound
  call a team member picked up first (`front_figures`, "calls answered",
  each row's `rec`) and every connected dial on `dial_figures`' rows (each
  row's `recs`: Debbie's and Amanda's every dial, Crystal's only to service
  numbers, commercial-only households left out) -- downloads the recordings
  the producers' pass did not (Debbie's and Amanda's were never downloaded
  before; transcribe.download's 8/min pacing) and saves Deepgram's timed
  turns in `data/servicetx_<day>.json` (a DAY_FILE in R2; the audio rides
  with the rest of the day's recordings). The team member reads "<First
  name> (service):" from their own introduction -- or, on a call-in the call
  log says they picked up, from the agency's greeting ("Thank you for calling
  Farmers Insurance", which Debbie says without her name;
  `deepgram_stt.ANSWER_GREETING`, never used on producers' calls, whose
  transferred call-ins start with the front desk's greeting) -- the customer
  "<First name> (customer):" by the lead rule, everyone else Speaker N.
  **Payment numbers never reach the board** (`service_calls.redact_turns`):
  `messages.redact` on every line, and after any mention of a card /
  account / routing / social number every run of 4+ digits in the next six
  turns, whoever said it (a number read aloud comes back split). It errs
  toward removing too much (phone numbers, a premium). A call where that
  happened is `redacted` and the board shows it as text only, never the
  recording, which still holds the number (7 of 73 on 09-28). Built at every
  checkpoint (`intraday.py`) and topped up by the nightly's
  `service_digest.build`, which keeps the listed ones as the document's
  `calls_tx`; the Calls answered and Dials lists get a **Listen & read**
  button that opens the coaching cards' own player under the row
  (`svcTxRow`). ~60 recordings / ~150 minutes a day (09-28), about $1 of
  Deepgram. **September was given theirs** (Frank, 2026-09-30: "do the same
  for all of september") by `python3 service_calls.py --backfill 2026-09-01
  2026-09-29`: per published day it backs the page up under
  `backups/<today>-service-calls/`, adds `dials` where the page had none
  (a new Dials figure on those days -- Frank asked for it on 09-28 and then
  the month), each calls-answered row's `rec`, and `calls_tx`; nothing else
  changes. Days with no corpus snapshot (all but 09-23..09-25, 09-28, 09-29)
  route numbers with the customers and leads as of the backfill. A day that
  already has `calls_tx` is skipped (`--force` redoes it); the recordings
  go to R2 and leave the disk as each day finishes.
- **Documents hold rows, never medians**, so the board can add any range up.
  **Every card opens the rows it counts** (Frank, 2026-09-25), so the rows
  carry what a list needs: SRs name, household (= the AgencyZoom customer
  id), subject, dates and the rep's note (`sr_detail`); `task_rows`;
  `srs.open_rows` (every open SR at the end of the day, team or Late
  Payments); call backs with caller, times and a customer/lead link. Pages
  built before 2026-09-25 got theirs from their saved files
  (`python3 service_digest.py --add-lists`, which only adds detail and
  never changes a count).

## Cerberus -- Commercial

**Cerberus is Commercial's name** (Frank, 2026-09-24), beside Apollo and
Athena. **Commercial is Frank's alone**, so nothing commercial touches anyone
else's numbers. `commercial.py` is the one definition, imported by Athena to
exclude and by Cerberus to count:
- every SR in the **Commercial Renewals** workflow, whoever completed it;
- a **commercial service change**: a Service Pipeline SR on a household holding
  a commercial policy, COMPLETED by Frank (open: assigned to him, CSR 82589).
  AgencyZoom has no commercial service pipeline; the household is the only
  signal. The completer decides -- Amanda closing Frank's SR makes it hers;
- **call backs** from a commercial-ONLY household leave Athena's counts.

The service team's work on a commercial household (payments, a business
owner's personal lines) stays in Athena. Commercial renewals use the same six
resolutions, Unable to Contact retained, and the section is visible to Frank only.

**The Commercial Center** (Frank named it, 2026-09-24): `commercial_digest.py`
builds `commercial/<day>.json` from `daily.py` after the service board (board
only, never raises) -- rows of every commercial SR completed that day, plus
the open queue at the end of the day from that day's live SR file. The
Worker's `/api/commercial` answers only the emails in `COMMERCIAL_VIEWERS`
(wrangler.jsonc); the left-bar entry stays hidden for everyone else. Most
commercial policy chains stop being updated in AgencyZoom, so a renewal SR
closed on anything but the six resolutions usually reads "Policy record not
current" -- another reason the six matter here. **Its renewal outcomes follow
Athena's rules exactly** (Frank's resolutions only) and are re-read every night
like the Service Center's (`commercial_digest.refresh_past_renewals`, every
day on the board, back 365 days; an SR older than the nightly pull's year is
reached for once, e.g. 6836965 created 2025-08-03).

## Coach AI

- **The call score is NOT a 0-100 percentage.** Frank, 2026-09-01: a *perfect
  call* scores **750-800**. A producer averaging 224 is near 29% of a perfect
  call, not "over the cap". Nothing above 100 is evidence of a bug -- do not
  describe it as one, and do not "correct" a score for being over 100.
  Transcribe what the email prints, always, but for the ordinary reason that it
  is their measure and not ours.
- On that scale every figure the team currently posts is LOW: 2026-08-31 ran
  Lorena 224, Mike 148, Coral 122, Crystal 90, Sarahi 11, team 90. The team
  average is roughly 12% of a perfect call. Low scores are the finding, not a
  data fault.
- **`COACH_BAR_RANGES` is team-relative, not a share of the scale.** The Avg
  Call Score bar spans (38, 251) -- per-producer extremes over the trailing
  window -- because scaling 0-800 makes every bar a sliver. The side effect is
  that 224 renders nearly full when it is under a third of a perfect call. If
  the bar is ever relabelled or re-anchored, that is the reason.
.- **Voicemails are scored as calls, and that is the whole story of the low
  numbers.** Confirmed 2026-09-01 against TRAQ's own per-call scores, read off
  three of Sarahi's calls where TRAQ itself labels the call type:
    voicemail -> score 3,   sentiment 0
    voicemail -> score 3,   sentiment 0
    live call -> score 292, sentiment 48
  A voicemail scores ~3 against a real conversation's ~292 (~100x), and
  sentiment on a voicemail is a flat 0. Avg Call Score and Avg Sentiment are
  therefore answer-rate-weighted, NOT call-quality measures: a producer who
  reaches more voicemails posts a lower average regardless of how they talk.
  Sarahi's 25 voicemails of 35 rows are why she sits at 11. This is not a fault
  to fix in our pipeline -- it is how TRAQ scores -- but it means these two
  figures cannot rank producers with different answer rates against each other.
- **Getting a real per-call score, with no API.** TRAQ has no API key and one is
  not coming soon (Frank, 2026-09-01). The working route is manual and takes
  about two minutes:
    1. Every TRAQ note cached under `data/notes/` carries the call id, the
       duration, and TRAQ's own prose summary. Grep them for `Traq Call`.
    2. TRAQ states the call type in its own summary -- "the call was directed to
       voicemail", "un mensaje dejado" -- so calls can be picked by type without
       trusting our classification.
    3. Hand someone with a TRAQ login the `app.traq.ai/call/0/<id>` links and
       have them read back score and sentiment.
  That is exactly how the 3 / 3 / 292 figures above were obtained. Do NOT ask
  for or accept a person's own TRAQ password to automate this. If it is ever
  worth automating, the right shape is a TRAQ **service account** in
  `secrets/all.env`, the way `AZ_USERNAME=frank.automation@...` already works
  for AgencyZoom -- never an individual's credentials.
- **A live-call-only score can be ESTIMATED without TRAQ at all**, since a
  voicemail scores ~3: `live_avg ~= (calls x avg_score - voicemails x 3) /
  live_calls`, taking calls and avg_score from the Coach AI email and the
  voicemail/live split from our own transcripts. Not implemented. It would be a
  DERIVED figure and would have to be labelled as one everywhere it appeared.
- The TRAQ note on every call carries its call id (app.traq.ai/call/0/<id>).
  IF a TRAQ API key ever lands, those ids join TRAQ's per-call scores onto our
  own live/voicemail classification directly and remove all of the inference
  above. Do NOT plan around a date: 2026-09-15 (digest_config.
  TRAQ_REVISIT_DATE) is when Frank FOLLOWS UP, not when the key arrives, and he
  has said explicitly it is not guaranteed. Until it exists the manual route
  works -- pull the app.traq.ai links out of the cached TRAQ notes, pick calls
  by the type TRAQ states in its own summary, and have someone with a login
  read the scores back. That is how the numbers above were obtained.
- The per-user rows ARE internally consistent: they are call-weighted averages
  over Coach's own Total Calls column and roll up exactly to the team figure
  (2026-08-31: 12,835/142 = 90.4 against a stated 90; role play 399/5 = 79.8
  against 80). The aggregation is not in question.
- **Total Calls includes voicemails**, and Coach's coverage of a producer's day
  varies wildly -- 2026-08-31 it saw 9 of Lorena's 52 dials but 35 of Sarahi's
  40. Cross-producer comparison of these averages is unsafe for that reason
  alone, independent of the scale.

## Cost

Transcription is Deepgram, paid per audio minute (about $1-2 a day; below). **The Anthropic API reads in `call_summary.py`,
`renewal_notes.py` and `service_notes.py` are the only paid steps** (plus
`sendoff.py` and `assume_reread.py --backfill`, each run once for September) — roughly one call per live
contact per day, plus one call per 25 renewal SR notes (each SR's note is read
once and kept in `data/renewal_note_reads.json` and its R2 copy; only an edited
note is read again -- never delete that cache casually). Changing
the prompt means deleting `data/callsum_<day>.json`, which re-reads everything.
Do not do that casually, and never in a loop while iterating on wording.

**Every read's instructions are prompt-cached** (Frank, 2026-09-29):
`call_summary._post`, which every Claude API read goes through, marks the
system prompt for caching, so a coaching card's ~20,800-token METHODOLOGY is
billed at a tenth on each read after the first within five minutes. The
answers are the same. **The one-off re-reads go as a half-price Message
Batch** by default -- `sendoff.py` / `assume_reread.py --backfill` and
`rebuild_cards.py` (`--live` for one by one): the read loop runs once to
record its requests (`call_summary.collect`), they go out as one batch
(`run_batch`, usually minutes, at most 24 hours), then the loop runs for real
and every identical request is answered from the batch; retries go live.
Never the nightly run -- it cannot wait.

**Reads run at the model's lowest thinking setting** (2026-09-28,
`call_summary._NO_THINKING`): the code asks for thinking "disabled";
claude-sonnet-5-5 refuses that (400), so `_post` switches to
"between_tools" (0 thinking tokens) for the rest of the run. The old
fallback dropped the setting, the model thought inside the answer budget,
and long coaching cards came back cut off. Frank did not choose this on
2026-09-29 -- he was told reads ran with thinking on, which was only true of
the branch he was looking at; this had already landed on main.

**Deepgram is ON** (Frank, 2026-09-29: Whisper base mishears too much and
cannot separate speakers; switched on the same day after the 09-25 / 09-28
side-by-side). `deepgram_stt.py` (Nova-3, language=multi, diarized, keyed on
`DEEPGRAM_API_KEY` in the cloud environment) transcribes every recording
unless `TRANSCRIBE_ENGINE=whisper`, and falls back to Whisper on any failure
(a missing key says so once in the log). Full transcripts are one line per
turn, **each starting with its real start time, "[m:ss]" into the
recording** (2026-09-30, `deepgram_stt.full` / `LINE`; Apollo uses them for
objections' `at` and the spine and never invents one). Transcripts saved
before that have none and stay as they are; speakers are found on the
utterances, never on this text, and `turns` (the card player) is unchanged.
The producer's turns read "<First name> (producer):", found from how
they introduce themselves ("This is Crystal with Farmers", "Le habla Mike, de
la aseguranza", "Soy Sarahi"; `deepgram_stt.producer_speaker`, own name
only -- a caller saying "Hi, Crystal" does not count); everyone else, and
every turn when no one introduces themselves or two speakers tie, stays
"Speaker N:" -- never guessed. On 09-25 / 09-28 it named the producer on
50 of 57 calls with two voices, every one checked by hand. **The other voice
is "<First name> (lead):"** (`deepgram_stt.lead_speaker`, the Call Detail
row's lead) only when the producer is found, there is ONE other voice, and
the call shows it: the producer greets or asks for them by name in the
opening ("Hi, Harry", "Is this Carlos?", "Hablo con Maria?"), or they give
it ("This is Brianna", "Speaking"). A name only mentioned is someone talked
about (Coral asking Jessica about Jesse, 09-25), and a spouse, "you just
missed him" or a wrong number stays Speaker N. **Customers are named the
same way** (`deepgram_stt.other_party`, Frank, 2026-09-29: "match customers
to their names too"): with no lead matched, the first names on the number's
AgencyZoom customer records (`customer_names`, from the nightly's own
`data/az_customers_all.json`) go through the same test and read "<First
name> (customer):", in the record's spelling. Names match across a
transcription's or a record's spelling (Brianna / Brayana, Meredith /
Merideth) only with the same first AND last letter, so Juan is never Juana
nor Mario Maria -- a husband and wife on one number. 09-25 / 09-28: 11
leads and 8 customers named, all checked by hand. **The service team's
calls are full-transcribed too** (Athena, below: `service_calls.py`). It is paid per audio minute (~226
min on 2026-09-28), cached per recording under `data/deepgram/` and carried
between containers in R2 as `cache/<day>/deepgram_<day>.json` (`r2_cache`), so a
recording is paid for once however many checkpoints touch it. A leg with
no speech at all is `[silence]`, read as no answer like Whisper's "[Music]",
never as a pickup that said nothing. **Past days stay as they went out**: a
rebuild reuses the day's saved transcripts. `python3 compare_stt.py <day>
...` still writes `out/stt_compare_<day>.md` (verdicts both ways and every
live call's transcript both ways) for any day with saved recordings.

`python3 verify_finalize.py` reconciles all six headline figures against source
data and costs nothing. Run it after touching `daily.py`, `day_calls.py` or
`finalize.py`.

## The Arizona look, The Flores Post and the Editions (2026-10-01)

**The board wears the desert** (Frank, 2026-10-01: "a pure design change").
`site/public/index.html` keeps every view's markup, hooks, tier colours,
lists and links; only the token values moved (checked with a before/after
capture of 16 views in a local harness). Five looks a person picks in
**Settings** at the bottom of the menu (Sonoran, Saguaro, Turquoise &
Silver, Canyon Sunset, Mesa Minimal), each with its Desert Night; light /
dark / device as icons only, remembered per browser (`board-look`). The
menu lists each Center's pages; the header greets whoever is looking by
first name (`/api/me`, ~90 random lines) and carries the search (Ctrl K:
pages, sections, producers, every lead on the loaded day) and **Take a
tour** (the board's own system tour, its card styled as the Field note). Every section is a cream card
with a 2px border. **A feed line never names a stage** ("Mike presented
$2,500 in premium"): the Digest's day reads as Apollo's group chat
(`digestFeedItems`) beside **Needs someone now** / **Left on the desk**
(`needsNowRows`); the Service Digest's is **Off the desk · done today**.
- **The Flores Post** (`site/public/post.js`) is its own page under the
  Sales Center, written in rules from the day documents -- nothing typed,
  nothing paid. Day editions for published days; the folio edition
  updates every published day (and from today's checkpoint while open),
  Friday editions frozen as they went out, a countdown at two or fewer
  business days left, a closing edition. Slow editions (no sales on a day,
  a week under $20,000, a folio under last folio's pace) carry What to try /
  What to look for and the goal board. **Primetime is a permanent part of
  the paper and the only place it carries the standings.** No links back to
  the Digest ("tabs on the left is enough").
- **The Editions** (`site/public/editions.js`): The Flores Feed, Fourth and
  Goal, KFLR The Close, FLRS 500, Cold Call Comics, CLOSER (Frank named
  them, 2026-10-01) -- each with its own
  mechanic, every one carrying the leaderboard, all from the same
  documents. What people do on them (reactions, comments, poll and MVP
  votes, mailbag notes, panel likes) is shared through the Worker's
  `/api/editions/<key>` in R2 (`editions/<day>.json`,
  `editions/folio-<end>.json`), one each per person by the Access name;
  a viewer's own picks (watchlist, cover photo, card flips) stay in their
  browser. The `/api/me` first names live in the Worker's `FIRST_NAMES` +
  `RP_PRODUCER_EMAILS`.
- **Everyone is themselves, from the Access login -- no "viewing as"**
  (Frank, 2026-10-01). The Worker's `identityOf` decides: **Frank, Amanda
  and Crystal log sales for everyone; Coral and Sarahi for each other
  (a team); every other producer their own; anyone else none**
  (`SALES_LOG_ALL`, `SALES_LOG_TEAMS`; enforced on POST / track / delete,
  and the Sales form only offers those names -- one name is picked for
  them, none hides the form; each entry carries `logged_by`). **A producer
  role plays as themselves**: the picker and "change" are gone for them
  and `roleplayGrade` refuses another name; Frank and the ops viewers
  (`rpScope.all`) still pick who, and the Beta tester.
- The local harness used to check all of this (a mock of the Worker over
  saved day documents, Playwright captures) lives in the session's
  scratchpad, not the repo; `design/flores-board-preview.html` is the
  approved mock-up the restyle followed.

## Never

- Commit anything under `secrets/`, `data/` or `out/` (all gitignored).
- Echo credentials into a log, a report or a chat message.
- Re-send a day that has already gone out without saying so explicitly.
