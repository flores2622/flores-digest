/* Blueprints -- the plain-language guides to the Sales Floor (Frank,
   2026-09-30: "if Im out for a week and want amanda to coach, she should
   know what everything means, how the model coaches, where everything is";
   "They should be in regular language, not AI prompt language").

   One manager guide (Apollo's Road Map, the ARM), Athena's Road Map for the
   service team (Frank, 2026-09-30: "make an Athena Road Map for the service
   team too"), and three producer guides (new,
   mid-level, experienced). The board renders them on Apollo's Academy >
   Apollo's Road Map and Service Center > Athena's Road Map (blueprintPanel in
   index.html). Frank, 2026-09-30: "call it Apollo's Road Map (ARM)";
   "Apollos road map should be the name of the full tab, with a dropdown
   that has options for manager/coaching, and one for the 3 producer
   levels". `map` says which tab a guide is on, `label` its dropdown name.

   KEEP THIS CURRENT. Whenever a change alters what a number means, how
   Apollo scores or coaches a call, what a page shows or where it sits,
   update the matching lines here in the same change and move `updated`.
   CLAUDE.md says the same.

   Format: each guide is a list of sections {h, body}; body items are a
   paragraph string, {list: [...]}, {steps: [...]} (numbered), {terms:
   [[term, meaning], ...]}, {table: {head: [...], rows: [[...], ...]}},
   {checks: [[box, [step, ...]], ...]} (tick boxes, each with its numbered
   how-to steps; ticks are kept per browser) or {code: "..."} (a block to
   copy as it stands, e.g. a note template).
   **bold** works inside any text. Nothing else is interpreted.

   The Worker imports this file too (site/coeus.js): Coeus answers "what does
   this number mean" questions from these same words, so the board and the
   assistant can never disagree. That is why the assignment below lands on
   `window` in the browser and on the global in the Worker -- keep it a plain
   script (no import/export), or the <script src> in index.html breaks. */
(typeof window !== "undefined" ? window : globalThis).BLUEPRINTS = {
  updated: "2026-10-05",
  guides: [

  /* ------------------------------------------------------------------ */
  { key: "manager", map: "apollo", label: "Manager / Coaching", manager: true, title: "Apollo's Road Map (ARM)",
    who: "For managers: how Pantheon works, what every number means, how Apollo coaches, and how to run coaching when Frank is out.",
    sections: [
    { h: "What this is",
      body: [
        "Pantheon is the agency's board. It pulls the day's calls from RingCentral, the leads, quotes, policies, tasks and notes from AgencyZoom, and utilization from Insightful, and turns them into one picture of the day.",
        "It has three coaches, each with a name:",
        { terms: [
          ["Apollo", "Sales and coaching. Listens to every recorded sales conversation, writes a coaching card for it, and runs Role Play."],
          ["Athena", "Service. The Service Center: SRs, renewals, tasks, call backs, texts, and the Service Playbook."],
          ["Cerberus", "Commercial. Frank's alone; nobody else's numbers include commercial work."],
          ["On your phone", "The board works as an app on an iPhone. Open it in Safari, tap **Share**, then **Add to Home Screen**: it gets the owl, Apollo's, as its icon and opens full screen, without Safari's address bar. Sign in once inside the app, the same way as on the computer; it keeps its own sign-in, separate from Safari. On a phone the menu is one row across the top that scrolls sideways. On Android, Chrome offers **Install app** from its menu."],
          ["Apollo, the assistant", "The board's assistant is Apollo, the same Apollo that reads every sales call. The owl button at the bottom right of every page (or Ctrl /) opens a chat. Ask it how a day or a range went, what a producer should work on, what it saw on a call, how to answer an objection, or what any number means and how it is counted. It reads the same published reports and checkpoints the board draws, these guides and Apollo's methodology, so it cannot tell you anything the board does not know, and it will say so. It knows who is asking: a producer can see every producer's figures, as on the board, but only their own Role Play sessions; the Commercial Center is Frank's alone. Every conversation is kept for you under **Past chats**, on any device you sign in from; New chat starts another without losing the old one. One account pays for every question; **Usage** (Frank's view) shows who asked how much and what it cost."],
        ] },
        "The ARM covers Apollo. Anything commercial is Frank's and is left out of every producer figure.",
      ] },

    { h: "The day's rhythm",
      body: [
        { terms: [
          ["8:55 AM to 4:55 PM", "Every hour on the :55, a checkpoint pulls the day so far: calls, recordings, transcripts, coaching cards, sales, quotes, tasks. Weekdays only."],
          ["Between checkpoints", "The board keeps dials, sales, quotes, contacts, talk time, texts and emails, speed to dial, task completion and utilization live. A live number has a **pulsing green glow**. Anything without the glow is from the last checkpoint."],
          ["5:30 PM", "Coach AI (TRAQ) sends its daily emails with call scores and role play scores."],
          ["5:55 PM", "The final run. It reads the Coach AI emails, builds the day, sends the emails and publishes the boards. Expect the emails a little after 6:00."],
        ] },
        "Two emails go out. **Ops** (Frank, Francisco, Veronica, Amanda) get the Sales Digest plus the Call Detail and Task Completion Audit. **Staff** (the producers and Debbie) get the Sales Digest only.",
        "Live contact rate and talk time are **provisional** until the next checkpoint. The board can't hear a recording between checkpoints, so it judges a new dial from the notes and the call length. The checkpoint listens and settles every call. It is normal for these to shift by a call or two on the hour.",
        "A day that has already gone out is never changed after the fact unless Frank asks.",
      ] },

    { h: "Where everything is",
      body: [
        "The left bar holds the Centers: the Sales Center, **Apollo's Academy** (the coaching cards plus Role Play, Session History, Training and this Road Map), the Service Center and the Commercial Center. **Each Center opens like a dropdown to its pages**; click its arrow to open or close it. Each Center also has tabs across the top. Every page shares two filters at the top: **the day or range** (a single day, this week, month to date, year to date, a folio, or custom dates) and **the producer** (everyone, or one person). **Every number, card and bar opens the accounts behind it**; click it and the list appears underneath.",
        "**Ask Apollo** when you cannot find something or want a number read out: the button at the bottom right of every page. It knows which page, day and producer you are looking at, so \"how did we do?\" means that day and that person.",
        { table: { head: ["Where", "What it's for"], rows: [
          ["Sales Center > Digest", "The day at a glance: dials, contacts, quotes, sales, closing ratio, the leaderboard, speed to dial and reply, task completion, household completion, utilization, Coach AI scores."],
          ["Sales Center > Sales", "The Sales sheet. Log a sale, look back at any folio, and break sales down by lead source, product or producer. Self-reported, not the official Premium Sold. Live sales are added to it automatically, and the nightly run adds any sale entered late in the last two weeks. Flood is never added, since nobody is paid for it. An added sale keeps the premium it was sold at: if AgencyZoom's premium changes afterwards (a correction, or an endorsement nobody is paid on), an amber \"AZ $...\" tag shows AgencyZoom's figure beside it for someone to check. Click a producer's card, their name or their slice of the pie in Totals to show only their sales in the folio log; click it again, or Team, to see everyone."],
          ["Sales Center > Sales > Commission", "Where each producer stands on the commission schedule this folio, worked out from the Sales sheet as sales are logged: their tier and rate, how far to the next tier and what it pays, and the extras (life $100 a policy whatever the tier -- life is counted by policies, and its premium never counts toward the tier; a bundle to a new household $50 and a cross-sell to an existing household $25 a line once the tier minimum is met; umbrella $25; Farmers business 3.5% of the premium, which doesn't count toward the tier; Kraft Lake $300). Crystal, Lorena and Mike are on the individual schedule; Sarahi and Coral share the team schedule, split 50/50. A Winback counts as a new household. Each producer sees only their own (Sarahi and Coral their team's); Frank and Amanda see everyone. Estimates: a wrong entry on the Sales sheet changes it, and the rates are subject to change."],
          ["Sales Center > Texts & Emails", "Every text and email with a lead: what each producer typed (automation counted apart), replies still waiting, and how fast replies were answered."],
          ["Sales Center > Rotation", "Who gets the next new-business walk-in or call-in. Three rotations, each with its own turn: **Personal lines** (Lorena, Sarahi, Amanda, Coral, Crystal; never Mike), **Life** (Mike, Lorena, Coral) and **Mexico policies** (Lorena, Amanda, Crystal, Mike, Coral, Sarahi). Debbie types the client and gives it to whoever is up. If they're **busy**, the client goes to the next person and whoever was busy stays up for the next one; the person who covered gets passed over once, so covering counts as their turn. If they're **out**, the client goes to the next person and the one who's out loses that turn (with no client name typed, their turn is just skipped, for when you know someone is out before anyone walks in). When the client asks for someone, she gives it out of turn and the turn stays where it was. Below the rotations is the folio's log: what each person got. Only Debbie, Crystal and the ops team can see it. Managers and Debbie change an order or who is up. It replaced the Rotation Sheet in Google Drive on October 2."],
          ["Sales Center > Lead Scrub", "Tracks a list of clients being cleaned up in both **Apex** and **AgencyZoom**, in the same columns as the scrub sheet: Client, Month, Apex Status, AZ Status (with **Duplicates Cleaned** and **Tagged** boxes beside it), Lead Status, Action Taken, Date, Rep, Notes and Next Step. A manager imports the report as it comes (Excel or CSV; someone quoted on two lines becomes one client). The status boxes suggest the usual answers (Active, Updated / Smart Cycled, Account reviewed, None) and take anything typed. Every change saves at once and fills in the Date and Rep with today and whoever made it. A client is done when Apex Status, AZ Status and Lead Status are filled in and both boxes are ticked. Filter by rep, by what is left, by anything on the report (line of business, risk segment) or search. Download CSV gives the list back in the sheet's column order. Only the ops team can see it."],

          ["Apollo's Academy > Cards", "One coaching card per recorded sales conversation. Filter by producer, day or objection."],
          ["Apollo's Academy > Objections", "Every objection Apollo found, grouped, with how each was handled."],
          ["Apollo's Academy > Wins and Losses", "Patterns across calls: assumed the quote, assumed the sale, sent the quote instead of keeping them on the phone, and the patterns that only show up across many calls, each with the calls behind it."],
          ["Apollo's Academy > Role Play", "Practice calls against an AI prospect, graded by Apollo."],
          ["Apollo's Academy > Session History", "Every graded Role Play session. Managers see everyone's; a producer sees their own."],
          ["Apollo's Academy > Training", "Flashcards, quizzes and matching games on objections, information gathering and technique."],
          ["Apollo's Academy > Apollo's Road Map", "This guide (Manager / Coaching) and the three producer guides, picked from the dropdown. Athena's Road Map is in the Service Center."],
          ["Service Center", "Athena's side: the Service Digest and the Renewals tab."],
          ["Claims Center", "Every claim: what's open, who opened and worked it, and close time by type."],
        ] } },
        "**Refreshing the page keeps you where you were**: the same page, tab, day or range and producer. A new tab or window starts on the Digest.",
        "Anyone can press **Take the tour** at the bottom of the left bar for a walk through the board.",
      ] },

    { h: "What the numbers mean",
      body: [
        "Colours follow one rule everywhere: **green** is on or over goal, **yellow** is off pace but close, **red** is off track and needs a look. During the day, dials and households quoted are judged against where the producer should be by that hour, not the whole day's goal.",
        { terms: [
          ["Dials", "Outbound calls the producer made on new business. One account is one attempt, even if we called two of their numbers. Numbers that aren't new business, like a customer calling about a payment, are left out."],
          ["Live contacts / Contact rate", "Dials that reached a person, over dials. **Outbound only.** A lead calling back turns their earlier dial into a contact. A cold call-in is a conversation but sits outside the rate. **Most dials reach voicemail; a low contact rate is real, not a fault.** The producer's own note wins over the recording (\"no answer\" means no answer)."],
          ["Avg Talk Time", "Average length of the day's conversations, call-ins included."],
          ["HH / Prem. Quoted", "Households quoted and the premium quoted. A household counts once however many quotes it got. A quote counts when AgencyZoom's quote date is today, the producer moved the lead into a quoted stage, or the producer's note says a quote was sent."],
          ["HH / Prem. Sold", "Households marked sold, and the premium on the policies sold. **A sale entered with no lead marked sold still counts** when a brand-new customer record for that producer sits behind the policy (the list shows it as a customer record). **BOB and Rewrite are not sales.** A renewal is not a sale. Selling a product the household doesn't have yet is a sale, even to a twenty-year customer. **Life insurance is not counted here.**"],
          ["Life Sold", "Life policies sold (term, whole, universal life), **counted on their own** -- a count of policies, no premium figure, since life premium is not tracked. They never count as a household sold, in Premium Sold, on the leaderboard or in the closing ratio. **The goal is 1 life policy a week per producer** (5 for the team): green once the week has one, yellow Monday to Thursday without one, red on Friday without one."],
          ["Closing Ratio", "Households sold over households quoted, and premium sold over premium quoted."],
          ["Speed to Dial", "For internet leads that arrived today (SureQuote, MAV), how long until the first dial. The Team card is the middle of everyone's times."],
          ["Speed to Reply", "When a lead texts or emails us, how long until the producer answered by text, email or call. Green at 15 minutes or less, red over an hour. Replies still waiting are listed."],
          ["Task Completion", "AgencyZoom tasks due today that were done. Duplicate leads and smart-cycled leads are excused."],
          ["Household Completion", "Policies sold per household sold. Green when they sold to an existing customer or a new household bought more than one policy; yellow when every sale was one policy to a new household; a red dash for no sales."],
          ["Utilization", "Insightful's productive time over tracked time."],
          ["Sent the Quote", "On the leaderboard, how many of the producer's calls where a quote came up ended with them offering to send it instead of presenting it on the phone. Shown, not scored."],
          ["Texts / Emails", "What each producer typed to leads themselves. Automation is never counted."],
        ] },
        { table: { head: ["Goal", "Green", "Yellow from"], rows: [
          ["Dials a day", "50", "40"],
          ["Avg talk time", "7 min", "3 min"],
          ["Contact rate", "13%", "10%"],
          ["Households quoted a day", "5", "2"],
          ["Premium quoted per household", "$900", "$501"],
          ["Premium sold per policy", "$900", "$501"],
          ["Closing ratio", "25%", "15%"],
          ["Utilization", "85%", "80%"],
          ["Task completion", "100%", "90%"],
          ["Role play score", "80", "anything above 0"],
        ] } },
        "**The leaderboard** ranks the five producers in seven categories (Role Play, Call Volume, Avg Talk Time, Contact Rate, Households Quoted, Premium Quoted, Premium Sold): 5 points for first down to 1 for fifth. Ties are broken by premium sold, then households quoted, then dials. Over a date range it ranks each producer's daily averages over the days they worked, so a day off costs nothing; a worked day with no role play counts as zero for the ranking but not in the Role Play average shown.",
        "**Coach AI scores** are TRAQ's, copied from its email. A perfect call scores 750 to 800, not 100. A voicemail scores about 3, so a producer who reaches more voicemails posts a lower average however well they talk. Don't rank producers on these averages.",
      ] },

    { h: "How Apollo coaches a call",
      body: [
        "Every recorded conversation with a lead gets a coaching card. Before it reads the call, Apollo is told the lead source and what that source means, the pipeline and stage the lead was in when the call started, every stage move the producer made that day, and the lead's history: dials to the number in the last 30 days, quotes on file, earlier coaching cards, and notes. It reads the full transcript and the producer's own notes.",
        "**First it decides what the call was for:**",
        { terms: [
          ["First conversation", "The first real talk with this lead."],
          ["Finish the quote", "An earlier call started the quote; this call is to finish discovery and present it."],
          ["Follow-up", "A quote was already presented (on a call, or by email or text) and this call is working it to a close."],
        ] },
        "Who dialled (the producer, a lead calling back, or a call-in) is noted separately. A call back can still be a first conversation.",
        "It also decides whether the call was **sales, service or mixed**. A service call on a household missing a product we could sell counts as mixed, whether or not anyone raised it.",
        "**First conversations and finish-quote calls** are scored on nine steps, each **Strong** (done well, and the transcript shows it), **Weak** (tried but thin), **Missing** (the chance was there and nothing was done) or **N/A** (no chance on this call):",
        { steps: [
          "Opening and identification",
          "Discovery",
          "Current premium captured",
          "Renewal / X-date captured",
          "Product knowledge",
          "Presenting numbers",
          "Bundle / cross-sell raised",
          "Next step specificity",
          "CRM after the call (the note in AgencyZoom)",
        ] },
        "On a finish-quote call, anything an earlier call already captured is N/A, not Missing.",
        "**Occupation discounts.** Apollo expects the occupation asked open (\"What do you do for a living?\") and followed up (\"What did you retire from?\"), since retirees of an eligible career still qualify. A yes / no checklist, or \"retired\" left there, is weak discovery and gets the \"Occupation discount not dug into\" flag. A price presented without a discount the prospect qualifies for counts against presenting the numbers. The whole list is in the Training tab's Occupation Discounts deck.",
        "**Verify against the reports.** ALTA's reports already show the drivers, vehicles, limits, coverages, dates, prior carrier, policy status and the term (six or twelve months). Discovery still matters: it buys time while the quote builds, builds rapport and finds what the reports don't. But what the prospect says about their current policy has to be checked against the **Prior Insurance** screen. People misremember the term: \"about $1,000 a year\" is often the six-month premium. Apollo marks the current premium and the price comparison weak when the producer takes the prospect's word on a figure that doesn't add up, and flags it as \"Didn't verify against the reports\".",
        "**Apollo's Doubts** (Frank's page, in Apollo's Academy): every coaching card Apollo wasn't sure of, or where it heard something for the first time, for the day or range you pick. Apollo writes its own doubts on each call it reads (a verdict it couldn't settle, a misheard price, an objection or a discount it had never come across), and the page adds what the card itself shows: speakers it couldn't tell apart, a recording cut short, verdicts that disagree, a lead source or objection it has no group for. Mark each one **Looks right** or **Needs a fix**; for a fix, a sticky note on the card is how Apollo learns it. Producers never see this page.",
        "**Sticky notes.** Open any coaching card and write a sticky note in the box at the top. Everyone sees it in yellow on the front of the card, so the producer gets your coaching right where they read Apollo's. Leave **Apollo learns this** ticked and Apollo uses the note on every call it reads from then on: it applies the lesson wherever a call shows the same thing, in your words. Untick it for a note that's only for that card. Cards already written aren't read again, so a lesson shows up on the next calls, not the old ones.",
        "It also marks six named techniques when they're used: elevator pitch, feel-felt-found, risk reversal, social proof, trial close, and takeaway / urgency.",
        "**Follow-ups** have their own six steps instead:",
        { steps: [
          "Reconnect and assume the sale up front: name, agency, the last conversation, and a close in the same breath (\"I'm calling to get your auto started on the $812 quote I sent Tuesday. Do you have your card handy?\")",
          "Check where they are: did they review it, has anything changed",
          "Handle what stalled it last time",
          "Re-present only what's needed, against what they pay now",
          "Assume the sale again at the end",
          "If it still doesn't close, a dated, specific next step",
        ] },
      ] },

    { h: "Assuming, and keeping them on the phone",
      body: [
        "These are the habits Frank cares about most, and Apollo judges them strictly.",
        { list: [
          "**Always assume, never ask.** Any line asking permission (\"would it be OK if...\", \"do you want me to...\") counts against them, however soft.",
          "**Assuming the quote means building it and presenting it on this call.** Setting up from the start that you'll put it together and send it is an early exit, not an assumption.",
          "**Assuming the sale**: going straight to the next step (\"which card would you like to use?\") instead of asking whether they want it. On a follow-up it is judged three times: up front, through the objections, and at the end.",
          "**No chance to assume counts neither way.** A call that was cut off, too short or not recorded is N/A.",
          "**Sent the quote** is marked on every card where a quote came up: **offered it on their own**, **the prospect was busy**, **the prospect asked for it by email first**, or **kept them on the phone**. \"I'll have the numbers for you tomorrow\" and \"let me work on it and call you back\" count as offering it.",
          "Asking the prospect to send us their documents (dec page, current policy, VINs) is good discovery, **but the review happens on the phone**. \"Send it over and I'll call you back\" is getting off the phone.",
          "Sending the quote is only for a prospect who says they're busy, and it is scored as handling the **Bad Timing / Busy** objection: get a specific better time, or send it and hold them for a quick discovery. \"I'll send it\" and hanging up is a dropped objection.",
          "A quote emailed or texted after a call counts as presented, so the next call is a follow-up. Ending a finish-quote call to send the quote instead of presenting it is flagged as a bad habit.",
          "The card's **\"Assumptive version\"** line, and every objection's better line, show how to finish the quote on the call. They never suggest emailing it unless the prospect said they were busy.",
        ] },
      ] },

    { h: "The rest of the card",
      body: [
        { terms: [
          ["Objections", "Each one Apollo found, in one of twelve groups: Price / Can't Afford, Bad Timing / Busy, Already Insured / Satisfied, Coverage / Eligibility, Spouse / Decision-Maker, Missing Info / Confusion, Not Interested, Shopping Around / Comparing, Wants to Wait / Think It Over, Payment / Billing, Trust / Bad Experience, Other. For each: what they said, whether the producer addressed it and overcame it, and a better line."],
          ["Lead source fit", "Did the call suit the lead source? A Home no Auto lead should hear about their auto; a winback should be asked why they left."],
          ["Stage fit", "Did the call do what the lead's stage asked for, and were the stage moves right?"],
          ["Greeting", "On a call the producer answered on their own line: \"Hi David! How are you today?\" when they know who it is, \"This is Mike, how can I help?\" when they don't. **No agency name, no \"insurance\", no full introduction**; people hang up when they hear they're being sold something. A transferred call picks up where the front desk left off, by name. Only the producer's own words count as the greeting."],
          ["Flags", "Each flag has a colour. **Red**: No next step, Quote not presented, Discovery missed, Approach skipped, Objection dropped, Call cut short, Stage / pipeline mistake, Compliance. **Yellow**: Cross-sell in progress, Callback set, Pipeline note. **Green**: Strong moment. Hover a flag for Apollo's words."],
          ["The recording", "Most cards play the call with the transcript underneath. Click a line to jump there; the play button on each line pauses and resumes in place, and hovering it shows volume and speed."],
        ] },
      ] },

    { h: "Lead sources",
      body: [
        "Every lead source in AgencyZoom belongs to a group, and the group tells Apollo who the lead is, what to sell and how to work it. The groups:",
        { terms: [
          ["Cross-sell", "An existing customer missing a product. **Home no Auto means we have the home and we're selling the auto; Auto no Home is the opposite.** Also Life Cross Sell, Umbrella and plain Cross Sell."],
          ["Existing client, new purchase", "A customer who bought something new, usually a property, and came to us."],
          ["Generated / purchased", "Leads we paid for or generated: SureQuote, Smart Financial, MAV AI, Alpha Media, Arizona Insurance Reports, Facebook. Speed wins; expect shopping."],
          ["Winback", "A **former** customer who now insures elsewhere. Find out why they left before quoting."],
          ["Referral", "A customer's referral, or Francisco's name as the source."],
          ["Call-in / walk-in", "They came to us: called, walked in, or found us on Google or farmers.com."],
          ["Personal network", "A staff member's own name as the source. Each person works their own network, never someone else's."],
          ["Social media", "Instagram or LinkedIn."],
          ["Center of influence", "A lender or realtor (\"Name at Company\"). We deal with them, not the client."],
          ["Cold / misc, Other one-offs", "Old lists, fairs, and odds and ends."],
          ["Commercial", "Frank's (Cerberus)."],
          ["Not a sale", "BOB and Rewrite. A policy under either never counts as a sale."],
        ] },
      ] },

    { h: "Pipelines and stages",
      body: [
        "Producers work four pipelines: **1 Pipeline** (every new lead starts here), **1-1 QNC** (quoted, not closed), **1-2 Leads Not Quoted**, and **Life Pipeline**. A pipeline called just \"Pipeline\" is 1 Pipeline filed there by mistake by an integration; the Sales Center lists those leads so someone can move them. Anything commercial or AZ Sun is Frank's.",
        { terms: [
          ["New", "If we reach them, the goal is the one-call close."],
          ["New 1st / 2nd / 3rd Cycle", "Smart-cycled back for another try. A live conversation here is a rare chance."],
          ["Contacted / In Progress", "Working a quote or waiting on information. Collect what's missing and present."],
          ["Ready to Present", "The quote is ready but held for a reason. Clear it and present."],
          ["Quotes Presented / Quoted", "This call is a close attempt. Starting discovery over is a miss."],
          ["1-1 QNC", "Quoted, didn't close. Find what stopped it and close."],
          ["FSD (Pending Bind)", "Sold, pending bind. Lock the details; don't reopen the sale."],
          ["Lender Referral", "Sent to us by a lender or realtor; skips the usual automation."],
          ["IL Interested, Transfer Pending", "Not our stages (made for an outside texting company). Moving a lead into one is a mistake, and Apollo flags it."],
        ] },
      ] },

    { h: "Running coaching when Frank is out",
      body: [
        "**Every morning (10 minutes)**",
        { steps: [
          "Open Sales Center > Digest on yesterday. Look at the red tiles and the leaderboard.",
          "Open Apollo's Academy > Wins and Losses for the last week. Note each producer's Sent the Quote count and assumed-the-quote rate.",
          "Pick one card per producer to listen to. Start with red flags: Quote not presented, No next step, Objection dropped.",
        ] },
        "**Each producer, once a week (20 minutes)**",
        { steps: [
          "Pick two cards: one win and one loss. Play the key moment from the transcript.",
          "Read the card's \"Assumptive version\" or the objection's better line out loud, and have them say it back in their own words.",
          "Agree on one focus for the week, never more than one.",
          "Have them do Role Play on that objection group: Beginner for a new habit, Medium once it's comfortable, Professional to stress-test. Check their sessions in Session History.",
          "Next week, check the same stat in Wins and Losses before anything else.",
        ] },
        "**What to look at first**, in order: keeping them on the phone (Sent the Quote), assuming the quote, a dated next step, discovery (current premium and renewal date), then the cross-sell.",
        "**What not to do**:",
        { list: [
          "Don't push a producer on contact rate alone. Most dials reach voicemail.",
          "Don't compare Coach AI averages between producers.",
          "Don't treat a provisional live contact rate as final before the hour's checkpoint.",
          "Don't count a renewal, a payment or paperwork as a sale.",
        ] },
      ] },

    { h: "Role Play",
      body: [
        "Role Play is a practice call against an AI prospect with a face and a voice. The producer picks a difficulty and, if they want, the objections to drill. The lead source is drawn from their own real calls over the last four weeks, so they practise what they actually get. Prospects speak English, Spanish, or a mix (Crystal always gets English).",
        { terms: [
          ["Beginner", "Warm, leaning yes, one soft objection."],
          ["Medium", "Two or three objections that fold easily when addressed."],
          ["Professional", "Skeptical; makes them earn it and holds objections firmly."],
        ] },
        "Every prospect gives real small talk if the producer builds rapport. When the call ends, Apollo grades four things: **assumptive language**, **addressed the real concern**, **re-asked immediately** after an objection, and **kept driving the call**, plus whether it closed and one tip. Some lead sources never come up in Role Play (centers of influence, cold lists, a producer's own network, commercial, BOB, Rewrite), but those calls still get coaching cards.",
      ] },

    { h: "When something looks wrong",
      body: [
        { list: [
          "A live number that jumps on the hour is the checkpoint settling it. That's expected.",
          "A day that went out stays as it went out.",
          "A call with no card is usually one with no recording, or a pure service call.",
          "A low contact rate is almost always real.",
          "If the emails haven't arrived by about 6:30 PM, tell Frank.",
        ] },
      ] },

    { h: "Keeping the ARM current",
      body: [
        "The ARM is updated whenever the way Apollo coaches, a number is counted, or the board is laid out changes. The date at the top says when it last changed.",
      ] },
    ] },

  /* ------------------------------------------------------------------ */
  { key: "athena", map: "athena", label: "Service team", title: "Athena's Road Map",
    who: "For the service team (Amanda, Crystal and Debbie) and anyone covering for them: each role, how the Service Center counts your work, and how renewals are judged.",
    sections: [
    { h: "What Athena is",
      body: [
        "Athena is the service side of Pantheon, the way Apollo is the sales side. It reads the day's service requests, tasks, calls, texts and emails from AgencyZoom and RingCentral, and shows them on the **Service Center**.",
        "The rules Athena works from are **Amanda's Service Playbook**: the roles, who handles what, the note standard and the daily checklist. When the playbook changes, Athena changes with it.",
        { list: [
          "We say **SR** (service request), never \"ticket\".",
          "**Credit goes to whoever completed the SR or task**, not whoever created it.",
          "Anything commercial is Frank's (Cerberus) and stays out of the service team's numbers. The team's work on a commercial household, like a payment or the owner's personal lines, still counts here.",
        ] },
        "**Apollo**, the board's assistant (the round button at the bottom right, or Ctrl /), answers questions about the Service Center too: how the team did on a day, retention over a period, which renewals are at risk, and what any figure here means.",
      ] },

    { h: "The standard",
      body: [
        "**Listen, Understand, Handle, Document, Follow Up.** Every client should feel heard, helped, and confident their request is being handled.",
        "The goal isn't for one person to handle everything. It's for everyone to know their role, own their work, and work together to keep things moving.",
      ] },

    { h: "The three roles",
      body: [
        { terms: [
          ["Service Lead: Amanda", "Oversight, delegation, complex service, training, and keeping the department moving. Handles complex or sensitive issues, Spanish-speaking service clients, involved policy changes and coverage questions, and reviews renewals. Watches missed calls, texts and pending tasks, audits notes, and steps in when someone needs help. A licensed rep, so she opens and works claims. **The Service Lead is not the default person for every request**; the goal is to delegate and support, not become the team's backlog."],
          ["Service Team Member: Crystal", "Handles day-to-day service independently: policy questions and changes, billing questions, vehicles and drivers, lienholders, documents and ID cards, renewal questions, and follow-ups. **If you can handle it, handle it.** Check the account, the policy and the notes before passing anything on. Crystal also sells, so she works an opportunity herself. A licensed rep, so she opens and works claims."],
          ["Front Desk: Debbie", "The first impression of the agency. Answers calls, greets walk-ins, handles basic billing, NOCs and admin tasks, and gets each client to the right person. **The front desk doesn't need to solve every issue**; the goal is to identify the need and route it confidently. Debbie passes sales opportunities to a producer. **Debbie doesn't open claims**: a client calling with a claim goes to Amanda or Crystal."],
        ] },
      ] },

    { h: "Who handles what",
      body: [
        { table: { head: ["Request", "Who"], rows: [
          ["Basic billing question, NOC or admin", "Front Desk"],
          ["Documents, ID cards, address, vehicle, driver or lienholder change", "Service team"],
          ["Routine policy change, renewal question, cancellation", "Service team"],
          ["A claim", "A licensed rep only: Amanda or Crystal (or Frank, Francisco or Veronica)"],
          ["Complex coverage question or an unresolved issue", "Service Lead"],
          ["New business, a cross-sell, a requote, new coverage", "A producer: whoever is up on the rotation (Sales Center > Rotation). Crystal and Amanda can work it themselves"],
          ["Anything that needs the owner", "Frank"],
        ] } },
        "**When in doubt, start with the service team.** We decide where the request needs to go.",
        "**Service first, opportunity second.** Don't force a sales conversation into every call, but don't miss the ones clients hand you. \"I'm adding a new vehicle\": handle the change, then see if the household could be reviewed. \"We're buying a house\": handle the need, and make sure the home gets to a producer.",
      ] },

    { h: "The note standard",
      body: [
        "Every note should answer five things, so the next person can pick up without making the client repeat themselves:",
        { steps: [
          "**Who** contacted us, or who we contacted",
          "**What** they needed",
          "**Why**, the reason behind it",
          "**Outcome**: what was done or decided",
          "**Next step**: what happens next, or that nothing more is needed",
        ] },
        "Good: \"Client called regarding upcoming renewal increase. Reviewed policy changes and discussed deductible options. Client wants to keep current coverage. No changes made.\"",
        "Too vague: \"Talked to client about renewal.\"",
        "Athena reads the note on every completed SR against this and counts the parts that are missing. A renewal reviewed without calling the client (\"low increase, review if needed\") already answers who and why.",
      ] },

    { h: "Your day",
      body: [
        { terms: [
          ["Start of the day", "Check missed calls, texts and emails. Review your tasks and anything urgent or pending. Find the follow-ups due today."],
          ["During the day", "Answer and return calls, work SRs, complete tasks, document every conversation, follow up on pending items, route sales opportunities, ask for help when you need it, and help teammates when you can."],
          ["End of the day", "Review unfinished tasks, finish your notes, return priority calls, make sure anything urgent has a next step, and tell the team what carries over."],
        ] },
        "**Priority order**: time-sensitive items, then client callbacks, then anything stopping a policy from moving forward, then older tasks, then routine requests.",
        "**How to sound**: warm, clear, confident, solution-focused. Instead of \"I don't know\" or \"That's not my job\", say \"Let me take a look at that for you\", \"Let me check and get back to you\", or \"I'll get you to the right person.\"",
      ] },

    { h: "The Service Center",
      body: [
        "The Service Center has two tabs, **Service Digest** and **Renewals**, and uses the same date filter as the Sales Center: a day, a week, month to date, or your own dates. **Every card opens the accounts behind it.**",
        "**Service Digest.** Across the top is one small card per person (Amanda, Crystal, Debbie) showing their SRs, tasks, reply speed and overdue items. Below it is one grid of cards: the team's totals until you pick a person, then that person's, with their role's checklist. Nobody is ranked.",
        { terms: [
          ["SRs completed", "SRs you closed in the period, and how long each took from created to completed."],
          ["Tasks done", "AgencyZoom service tasks completed."],
          ["Open SRs", "What's still open at the end of the day, and how much is overdue."],
          ["Dials", "Service calls you made. For Crystal, only calls to service numbers (a customer or an open SR); her new-business dials are on the Sales Center."],
          ["Call backs", "Missed service calls and how fast they were returned."],
          ["Speed to reply", "When a customer texts or emails, how long until someone answered."],
          ["Texts / Emails", "What each person typed to customers themselves. Automated messages are counted apart."],
          ["Calls answered", "Inbound calls each person picked up first. **Listen & read** plays the call with its transcript."],
          ["SRs created", "SRs each person opened."],
          ["Note standard", "How many notes left out a part of the note standard, and which part."],
          ["Opportunities", "Sales opportunities in the SRs: worked (quoted, a lead set, or passed to a producer) or not noted."],
          ["Utilization", "Insightful's productive time over tracked time."],
        ] },
        "Under the cards: Texts & Emails, Note Standard, Completion Time, and each pipeline's outcomes. Claims have their own page, the Claims Center.",
        "**Card, bank account and social security numbers are removed** from texts and call transcripts before they reach the board. A call where a number was said shows as text only, never the recording.",
      ] },

    { h: "The pipelines",
      body: [
        { terms: [
          ["Personal Renewals", "Farmers and Foremost renewals. Judged on completion time and outcome."],
          ["Other 30 day Renewals", "Bristol West renewals. The same."],
          ["Service Pipeline", "Changes, endorsements and basic service. Outcome read from your note: change made, policy cancelled, other service, not done, or unable to contact."],
          ["Late Payments", "The only pipeline worked stage by stage. Outcome: paid, cancelled for non-pay, client cancelled, unable to contact, or other. \"Saved\" is paid over paid or cancelled."],
          ["Contingencies", "Anything pending on a policy (AgencyZoom calls it Missing Documents). Outcome: cleared, policy cancelled, closed without clearing, or unable to contact. It also shows whether the selling producer or the service team closed it."],
          ["Claim", "Every claim. It has its own page, the **Claims Center**, below."],
        ] },
        "Service Pipeline, Late Payments and Contingencies SRs are all closed on **Completed**, so Athena reads the outcome from your note. A note that says what happened gets the right outcome; no note reads as \"No note\".",
      ] },

    { h: "The Claims Center",
      body: [
        "Every claim is an SR in AgencyZoom's **Claim** pipeline, and it has its own page in the menu: the **Claims Center**, under the Service Center.",
        { list: [
          "**Only a licensed rep opens or works a claim:** Amanda or Crystal, or Frank, Francisco or Veronica. **Debbie doesn't open claims**: a client calling with a claim goes to Amanda or Crystal.",
          "**Pick the type of claim as the SR's category** when you open it: Claim: Auto, Claim: Home, Claim: Life or Claim: Specialty. A claim left on any other category shows as **Not set** until someone picks one.",
          "**Commercial and Work Comp claims are Frank's.** Opened as Claim: Commercial or Work Comp Claim, they show on the Commercial Center, not here.",
        ] },
        "What the page shows, for the day or dates you pick:",
        { terms: [
          ["One card per person", "What each licensed rep opened, closed and holds open now, and their median time to close. Click a card to see only theirs; click it again for the team."],
          ["Open, Overdue, Opened, Completed", "Open is every claim still open at the end of the day; Overdue is the ones past their due date. Completed shows the median time to close and the time 90% closed within."],
          ["Close Time by Type", "For each type of claim: how many were opened, completed and are still open, and how long they took, from the day opened to the day completed."],
          ["Open Claims", "Where the open claims sit, by stage and by how long they've been open (0-7 days, 8-30, 31-90, 90+)."],
        ] },
        "Every number opens the claims behind it.",
      ] },

    { h: "Renewals",
      body: [
        "Renewal SRs are counted on the **Renewals** tab, not the Service Digest. Renewal tasks, calls, texts and emails go with them.",
        "**Close every renewal SR on one of Frank's resolutions.** They are the only outcomes Athena uses:",
        { table: { head: ["Resolution", "Counts as"], rows: [
          ["Renewed: Accepted as is", "Retained"],
          ["Renewed: Endorsed", "Retained"],
          ["Rewrite Accepted", "Retained"],
          ["No action: Review if needed", "Retained (reviewed, didn't need a call)"],
          ["Unable to Contact/No Show", "Retained (renewed as is)"],
          ["Cancelled: Rewrite Declined", "Lost"],
          ["Cancelled, no endorse/rewrite available", "Lost"],
          ["Client Cancelled", "Lost (went to the carrier, or never gave us the chance)"],
          ["Mid-term Cancellation", "Left out of the rate (already cancelled before the renewal SR opened)"],
          ["Cancelled: Sold/Moved", "Left out of the rate"],
        ] } },
        "**Completed is not a renewal outcome.** It's for changes, NOCs and missing documents. A renewal SR closed on Completed is listed on the Service Center as not one of the resolutions, and Athena reads your note, and the customer's texts, to decide what happened.",
        "Write the note the way it happened: \"renewed\" or \"reviewed\" alone reads as No action; a customer who went over it with you and changed nothing is Accepted as is; a bad number or email is Unable to Contact; \"cancelled in 2025\" is a Mid-term Cancellation.",
        "**The customer's texts count.** If a customer texts that they're switching or cancelling, that decides the outcome even when the note said \"renewed\".",
        "A Mid-term Cancellation with nothing that dates it (no date or year in the note, a policy record that never changed) is listed under **Cancellations to check** for someone to confirm.",
      ] },

    { h: "The Renewals tab",
      body: [
        { terms: [
          ["Retention", "Three rates. The **settled 4 weeks** (renewals 14 to 41 days ago; the newest two weeks are still settling), the **date filter's period**, and the **last 12 months**, the one to compare with Farmers'. Here the policy record counts too: a policy the record shows cancelled is lost even if no SR says so."],
          ["Renewal SR Work", "One card per person (renewal SRs, retained, open, overdue) and a grid below, the team's until you pick someone: renewal SRs completed, retained, reviewed with the customer, renewal tasks, open and overdue, coming up and high risk, lost, renewal dials, call backs, speed to reply, and texts and emails."],
          ["Renewal Outcome Breakdown", "A bar per person, split by resolution."],
          ["Coming up", "Renewals in the next 45 days, and how each renewal SR is being worked. **High risk** means not yet discussed with the customer and a warning sign: an open Late Payment or a cancellation SR on the household."],
          ["Lost, Not confirmed", "Policies lost in the period, and ones the records haven't settled yet."],
        ] },
        "Mid-term cancellations and \"not confirmed yet\" stay out of the rate.",
      ] },

    { h: "For the Service Lead: running the team",
      body: [
        { steps: [
          "Each morning, open the Service Digest on yesterday with no person picked. Look at open and overdue SRs, call backs and speed to reply.",
          "Pick each person's card. Compare what they did with their role's checklist, not with each other.",
          "Open **Note Standard** and read two or three notes that missed a part. Coach the part, not the person.",
          "Check **Opportunities** for anything not noted.",
          "On the Renewals tab, work **Coming up** and **High risk** first, then **Cancellations to check**.",
          "Watch your own share of routine SRs. If it's high, that's work to hand back to the team.",
        ] },
      ] },

    { h: "Our expectations",
      body: [
        { terms: [
          ["Ownership", "If you take the request, own it until it's resolved or properly handed off."],
          ["Communication", "Don't let someone else discover that a client has been waiting."],
          ["Documentation", "If it isn't documented, the next person doesn't know what happened."],
          ["Follow-through", "Don't make the client chase us for an answer."],
          ["Teamwork", "We help each other. We don't work as individual islands."],
          ["Accountability", "Different responsibilities don't mean different levels of importance."],
          ["Growth", "Ask questions, learn from mistakes, and become more independent over time."],
        ] },
        "We don't all have to do the same job, but we all have to do our part. We answer. We listen. We solve. We document. We follow up. We communicate. We help each other.",
      ] },
    ] },

  /* ------------------------------------------------------------------ */
  { key: "new", map: "apollo", label: "New Producer", title: "New Producer",
    who: "For someone brand new to insurance sales: what the board is, how you're measured, and how to build good habits from day one.",
    sections: [
    { h: "Welcome",
      body: [
        "Pantheon is where you see how your day is going and how to get better. Every recorded conversation you have with a lead is reviewed by **Apollo**, the agency's sales coach, and turned into a coaching card: what went well, what to fix, and the words you could have used.",
        "Nobody expects you to be good at this on day one. The point of the board is to show you one thing to work on at a time.",
        "Stuck on what a number means, or what to say to an objection? **Ask Apollo**, the round button at the bottom right of every page. It explains the board in plain words and coaches from its own playbook.",
      ] },

    { h: "Words you'll hear",
      body: [
        { terms: [
          ["Lead", "A person who might buy insurance from us. They live in AgencyZoom."],
          ["Household", "Everyone insured together at one address. We count sales and quotes by household."],
          ["Dial", "A call you make to a lead."],
          ["Contact", "A dial where you actually talked to the person, not voicemail."],
          ["Quote", "The price for the coverage they need."],
          ["Premium", "What the customer pays for the policy."],
          ["Bundle / cross-sell", "Selling another policy to the same household, like auto to someone whose home we insure."],
          ["X-date", "When their current policy renews. It's the best time to switch them."],
          ["Lead source", "How the lead got to us. It tells you who they are and what to offer."],
          ["Pipeline and stage", "Where the lead is in AgencyZoom: new, contacted, quoted, and so on."],
        ] },
      ] },

    { h: "Your day",
      body: [
        { steps: [
          "Start on Sales Center > Digest. Pick your name at the top to see only your numbers.",
          "Call new internet leads first. Speed to Dial measures how fast you call a SureQuote or MAV lead after it arrives, and the first real conversation usually wins.",
          "Work your AgencyZoom tasks. Task Completion shows how many of today's are done.",
          "Answer texts and emails from leads quickly. Speed to Reply turns green at 15 minutes.",
          "Write a note in AgencyZoom after every call: who you talked to, what they need, what happens next.",
          "Do one Role Play session.",
          "Check Sales Center > Sales > Commission to see your tier this folio and how much more premium the next one needs. It updates as sales are logged, so keep the Sales sheet right.",
        ] },
        "Numbers with a **pulsing green glow** are live. The rest update every hour on the :55.",
      ] },

    { h: "How you're measured",
      body: [
        "Green means on goal, yellow means close, red means off track. Click any number to see the calls or accounts behind it.",
        { table: { head: ["What", "Goal"], rows: [
          ["Dials", "50 a day"],
          ["Contact rate", "13% (most calls go to voicemail; that's normal)"],
          ["Avg talk time", "7 minutes"],
          ["Households quoted", "5 a day"],
          ["Closing ratio", "25% of households quoted"],
          ["Life sold", "1 life policy a week"],
          ["Task completion", "100%"],
          ["Role play score", "80"],
        ] } },
        "The leaderboard ranks everyone in seven categories. Don't worry about the leaderboard in your first month. Worry about your coaching cards.",
      ] },

    { h: "The shape of a good first call",
      body: [
        "Apollo scores your first conversations on nine steps. Here they are in plain terms:",
        { steps: [
          "**Open well.** Say your name and the agency, and make sure you're talking to the right person. \"Hi Maria, this is Lorena with Farmers.\"",
          "**Ask questions (discovery).** Who drives, what vehicles, the home, who's in the household, and **what they do for a living**. Farmers has occupation discounts for about twenty careers (teachers, nurses, engineers, military, police, firefighters and more). Ask it open, never as a yes / no list, and if they say they're retired, ask what they retired from: a retiree of those careers still gets the discount. The Training tab has a deck with the whole list.",
          "**Get what they pay now, and check it.** You can't beat a price you don't know. Look at the **Prior Insurance** screen in ALTA: is their policy six months or a year? \"About $1,000 a year\" is often the six-month price.",
          "**Get their renewal date.** If now isn't the time, you know when is.",
          "**Know the product.** Answer their questions clearly.",
          "**Give them the numbers on the call.** Say the price and what it covers, while they're still on the phone.",
          "**Offer the bundle.** Home and auto together, and ask about anything else they have elsewhere.",
          "**Set a specific next step.** A day and a time, not \"I'll call you sometime.\"",
          "**Write your note** in AgencyZoom after the call.",
          "**Read your sticky notes.** A yellow note on one of your coaching cards is from Frank or a manager, about that call.",
        ] },
        "Each step gets Strong, Weak, Missing, or N/A (there was no chance for it on that call). Missing is where to start.",
      ] },

    { h: "The two habits that matter most",
      body: [
        "**1. Assume, don't ask.** Don't ask permission to do your job. Instead of \"Would it be OK if I ran a quote for you?\", say \"Let's get you a quote. What's the year and model of your car?\" Instead of \"Do you want to go ahead?\", say \"Which card would you like to use?\"",
        "**2. Keep them on the phone.** A quote takes a few minutes. Build it and present it while they're on the line. \"Let me put this together and email it to you\" usually means you lose them. Only send it if they tell you they're busy, and then either set a specific time to talk or keep them for a few quick questions first.",
        "If they need to send you something, like their current policy, have them send it while you're on the phone and go over it together.",
      ] },

    { h: "Reading your coaching card",
      body: [
        { steps: [
          "Read the summary at the top: what happened on the call.",
          "Look at the flags. Red ones are what to fix first; green means you did something great.",
          "Read the **Assumptive version** line. It's how you could have said it.",
          "Look at the objections: what they said, how you answered, and a better line.",
          "Play the recording. Click any line of the transcript to jump to it.",
        ] },
        "Pick **one** thing from your cards to fix this week. Not five.",
      ] },

    { h: "Lead sources in plain terms",
      body: [
        { terms: [
          ["Home no Auto", "We insure their home, not their car. Offer the auto."],
          ["Auto no Home", "We insure their car, not their home. Offer the home."],
          ["Winback", "A former customer who went to another company. Ask why they left."],
          ["SureQuote, Smart Financial, MAV", "They asked for a quote online, probably from several agents. Call fast."],
          ["Call-in, Walk-in, Google, farmers.com", "They came to us. They're ready now."],
          ["Referral", "Someone sent them. Say who, right away."],
        ] },
      ] },

    { h: "Practise with Role Play",
      body: [
        "Apollo's Academy > Role Play gives you a practice call with an AI prospect. Start on **Beginner**. Talk to them like a real person: they'll chat back if you build rapport. When you finish, Apollo grades you on four things: assumptive language, answering the real concern, asking again right after an objection, and keeping the call moving.",
        "Use Apollo's Academy > **Training** for flashcards on objections and what to ask.",
      ] },

    { h: "Your first 30 days",
      body: [
        { steps: [
          "Week 1: take the tour, read this guide, and do a Beginner role play every day.",
          "Week 2: work on opening and discovery. Get the current premium and renewal date on every call.",
          "Week 3: present the numbers on the call, every time.",
          "Week 4: stop asking permission. Listen to your own cards for \"would it be OK\" and \"do you want\".",
        ] },
      ] },
    ] },

  /* ------------------------------------------------------------------ */
  { key: "mid", map: "apollo", label: "Mid-Level Producer", title: "Mid-Level Producer",
    who: "For producers who have the basics and want to close more consistently.",
    sections: [
    { h: "Where to focus",
      body: [
        "You know how to run a call. Now the gains come from consistency: assuming every time, handling objections instead of accepting them, and treating follow-ups as their own kind of call.",
        "Apollo's Academy > **Wins and Losses** is your scoreboard for this. It shows, for you and the team, how often you assumed the quote, assumed the sale, and sent the quote instead of keeping them on the phone, with every call behind each number.",
        "**Ask Apollo** (the round button at the bottom right) for your own figures over any range, what your cards keep flagging, and what to say instead.",
      ] },

    { h: "Assuming the quote and the sale",
      body: [
        { list: [
          "Apollo counts any permission-seeking line against you, however polite. \"Is it OK if...\", \"Would you like me to...\", \"Do you want to...\" all count.",
          "Assuming the quote means building and presenting it on this call. Promising to send it isn't assuming it.",
          "Assuming the sale means moving straight to the next step: the payment method, the start date, who else is on the policy.",
          "If the call was too short or cut off, it doesn't count against you either way.",
        ] },
      ] },

    { h: "Objections",
      body: [
        "Apollo sorts objections into groups (price, busy, already insured, spouse, want to think about it, shopping around, and more) and shows how each was handled. The ones that come up most:",
        { terms: [
          ["\"I'm busy\"", "Get a specific better time (\"Is 5:30 today good, or tomorrow at 9?\"), or send the quote and keep them for two or three quick questions. Hanging up after \"I'll send it\" is a dropped objection."],
          ["\"Your price is higher\"", "Find out what they have now, deductible and coverage, before you defend the price. Compare like for like."],
          ["\"I need to talk to my spouse\"", "Offer to include them now, or set a time when both are available."],
          ["\"Let me think about it\"", "Ask what specifically they want to think over. It's usually price or the spouse."],
        ] },
        "After you handle one, **ask for the sale again right away**. That's one of the four things Role Play grades.",
      ] },

    { h: "Follow-ups are their own call",
      body: [
        "When a quote was already given (on a call or by email or text), your next call is a follow-up, and Apollo scores it on six steps:",
        { steps: [
          "Reconnect and assume the sale up front: \"Hi Ana, it's Mike with Farmers. I'm calling to get your auto started on the $812 quote I sent Tuesday. Do you have your card handy?\"",
          "Check where they are: did they review it, has anything changed.",
          "Handle what stalled it last time.",
          "Re-present only what's needed, against what they pay now.",
          "Assume the sale again at the end.",
          "If it doesn't close, set a dated, specific next step.",
        ] },
        "Don't start discovery over on a follow-up. The card shows you what earlier calls already captured.",
      ] },

    { h: "Use the lead source and the stage",
      body: [
        "Each card tells you whether your call suited the lead source and the stage. Home no Auto means sell the auto; a winback means ask why they left; a lead in Quotes Presented means this is a close attempt. A lead in New that you reach is a chance at a one-call close: keep them on the phone and go all the way.",
      ] },

    { h: "Grow the household",
      body: [
        "Household Completion shows your policies per household. Green means you sold to an existing customer or a new household took more than one policy. On every sale, ask what else they have with another company: home, auto, renters, life, umbrella.",
      ] },

    { h: "Your weekly routine",
      body: [
        { steps: [
          "Monday: open Wins and Losses for last week and pick one stat to move.",
          "Every day: one Role Play session at **Medium**, focused on that stat's objection group.",
          "Every day: listen to one of your own cards all the way through.",
          "Friday: check the stat again.",
        ] },
      ] },
    ] },

  /* ------------------------------------------------------------------ */
  { key: "exp", map: "apollo", label: "Experienced Producer", title: "Experienced Producer",
    who: "For seasoned producers: the fine points Apollo looks for, and how to use the board to stay sharp.",
    sections: [
    { h: "What separates the best calls",
      body: [
        { list: [
          "**The one-call close.** A lead in New that you reach is a chance to go from hello to sold. A move to Contacted or Quotes Presented is fine only when something real stopped the close (missing information, a decision-maker who isn't there). Apollo will say what stopped it, or that nothing did.",
          "**The up-front close on a follow-up.** Put the close in your opening line. A ready customer finishes in minutes, and one who isn't tells you why in the first thirty seconds instead of the last.",
          "**Documents on the call.** When you need a dec page or VINs, have them send it while you're still on the phone and review it together.",
          "**Techniques, named.** Apollo marks six when you use them: elevator pitch, feel-felt-found, risk reversal, social proof, trial close, and takeaway / urgency. Look at which ones you lean on and which you never reach for.",
          "**The greeting on your own line.** When a lead calls you back, use their name: \"Hi David! How are you today?\" When you don't know who it is, \"This is Mike, how can I help?\" Leave out the agency name and the word insurance; people hang up when they hear they're being sold something.",
        ] },
        "**Ask Apollo** (the round button at the bottom right) to pull your numbers over any range, or to compare your closing ratio and Sent the Quote count with the team's.",
      ] },

    { h: "Where experienced producers slip",
      body: [
        { list: [
          "Sending the quote out of habit because the call is going well. The leaderboard's **Sent the Quote** column shows how often you do it.",
          "Skipping discovery because you've seen a hundred of these, then missing the current premium or renewal date.",
          "Taking the prospect's word on what they pay instead of checking the Prior Insurance screen. A six-month policy read as a yearly one makes a better rate look higher.",
          "Letting a follow-up turn into a second first call.",
          "Not writing the note after the call. The next person to touch the lead, and Apollo's next card, depend on it.",
          "Moving a lead to the wrong stage. IL Interested and Transfer Pending aren't our stages.",
        ] },
      ] },

    { h: "Speed and responsiveness",
      body: [
        "Speed to Dial and Speed to Reply are where experience shows. Internet leads go to whoever calls first, and a lead who texts you is ready to talk. Aim for green on both: under 15 minutes to answer a reply.",
      ] },

    { h: "Stay sharp",
      body: [
        { list: [
          "Role Play on **Professional**. The prospect is skeptical and holds objections; make them earn it.",
          "Drill the objection group you lose most (Apollo's Academy > Objections, filtered to you).",
          "Read your Wins and Losses monthly, not just your sales.",
          "Help newer producers: sit in on a Role Play or play them one of your strong calls.",
        ] },
      ] },

    { h: "What Apollo can't see",
      body: [
        "Apollo only knows what's recorded and written down. A call on your cell, a conversation in the office, or a quote you never noted doesn't exist to it. If the board is wrong about you, the fix is usually a note in AgencyZoom.",
      ] },
    ] },


  /* ------------------------------------------------------------------ */
  /* Frank, 2026-10-02: the producer out-of-office checklist "with specific
     instructions on how to do those things", built into the board. */
  { key: "ooo", map: "apollo", label: "Out of Office Checklist", title: "Out of Office Checklist",
    who: "For producers taking time off: everything to hand over before you leave, and how to do each step. Tick the boxes as you go; your ticks stay in this browser.",
    sections: [
    { h: "How to use this checklist",
      body: [
        "Start **two business days before you leave** and finish by the end of your last day. Each box has the steps for doing it underneath.",
        "**The main rule:** don't just tell someone you'll be gone. Set them up to cover you. If a client calls tomorrow asking for you, another team member should be able to open the account and know exactly what's going on.",
        "**Who gets the sale:** a sale that closes while you're gone stays yours only if your notes, files and information are properly in AgencyZoom. If the producer helping bind it has to go digging or investigating, or doesn't have the pieces needed to finalize it for you, it becomes their sale.",
        "Before you start, agree with Amanda or Frank on the producer covering you, and get that producer's yes. Write down your dates out, who covers your leads and quotes, who covers your calls (usually the same producer), and Amanda as the manager to go to if they get stuck.",
      ] },

    { h: "1. Email",
      body: [
        "Do this on your last afternoon. The forwarding step has a **Gmail** part and an **Outlook** part. Use the one for the email you use.",
        { checks: [
          ["**Auto-forward your email to the person covering you**", [
            "**Gmail:** click the gear, then **See all settings**, then the **Forwarding and POP/IMAP** tab. Click **Add a forwarding address**, enter the covering producer's email, then **Next** and **Proceed**. Gmail emails them a confirmation code; get it from them, enter it and click **Verify**. Pick **Forward a copy of incoming mail to** their address and **keep Gmail's copy in the Inbox**, so nothing is lost. Click **Save Changes**.",
            "**Outlook (web, or the new Outlook app):** click the gear, then **Mail**, then **Forwarding**. Turn on **Enable forwarding**, enter the covering producer's email, tick **Keep a copy of forwarded messages**, and click **Save**.",
            "**Outlook (classic desktop app):** click **File**, then **Manage Rules & Alerts**, then **New Rule**. Pick **Apply rule on messages I receive** and **Next**; leave the conditions blank, **Next**, and **Yes** to apply it to every message. Tick **forward it to people or public group**, pick the covering producer, and **Finish**. Leave Outlook open: a classic rule like this only runs while Outlook is running on your computer.",
            "Forwarding blocked or the option missing? Ask Amanda to turn it on, or to give the covering producer access to your mailbox instead.",
          ] ],
          ["**Answer urgent and current client emails before you leave**", [
            "Search your inbox for unread mail, and anything from the last 7 days that's waiting on you.",
            "Reply to each one, or tell the client who will help them while you're out.",
            "Anything you can't finish goes on the lead in AgencyZoom as a note (section 2), never only in your inbox.",
          ] ],
          ["**Make sure no lead or prospect is sitting in your inbox**", [
            "Look for dec pages, IDs, VINs, signed forms and \"call me\" emails from prospects.",
            "Upload each document to that lead's file in AgencyZoom and add a note saying what it is.",
            "If an email changes what happens next, write that on the lead too.",
          ] ],
        ] },
      ] },

    { h: "2. Leads and new business",
      body: [
        "Every open lead of yours leaves with a clear next step and an owner. **Don't leave a lead with no clear next step.**",
        { checks: [
          ["**Pull up all your open leads and active prospects**", [
            "In AgencyZoom, open **Leads** and filter **Assigned To** to you.",
            "Look at **1 Pipeline**, **1-1 QNC** and **Life Pipeline** first, sorted by last activity, newest first.",
            "Focus on the stages where someone is waiting on you: **Contacted, In Progress**, **Ready to Present**, **Quotes Presented** and **FSD (Pending Bind)**.",
            "Check **Pipeline** (no number) too. It should be empty; move anything there into 1 Pipeline.",
          ] ],
          ["**Pick out the leads that need follow-up while you're gone**", [
            "Anything with a call back, quote or document due while you're out.",
            "Anything in Quotes Presented or Ready to Present.",
            "Anything pending bind: waiting on a signature, a payment or an inspection.",
            "New leads not dialled yet. These are often best handed over completely.",
          ] ],
          ["**Assign or reroute those leads to the person covering you**", [
            "One lead: open it, click **Edit**, change **Assigned To** to the covering producer and **Save**.",
            "Many leads: tick them in the Leads list and use **Bulk Actions** to change the assigned agent.",
            "Open each lead's **Tasks** and reassign any open task due while you're out, with a clear due date.",
            "Never move a lead into IL Interested or Transfer Pending. Those aren't our stages.",
            "Leads that can wait stay with you, with a task dated the day you're back.",
          ] ],
          ["**Add a hand-off note on every lead you hand over**", [
            "Open the lead, click **Notes**, then **Add Note**.",
            "Start it with OUT OF OFFICE HAND-OFF so the covering producer can spot it.",
            "Fill in all six lines of the template below.",
          ] ],
        ] },
        "**Hand-off note template.** Copy it, then fill it in:",
        { code: "OUT OF OFFICE HAND-OFF (<your name>, out <dates>)\nWants: <products, e.g. auto + home>\nQuote status: <not started / in progress / presented on <date> / sent <date>>\nDiscussed: <drivers, vehicles, current carrier & premium, discounts, objections>\nWaiting on: <them: dec page, license, VINs / us: a rate, underwriting>\nNext step: <what to do, and by when>\nBest way to reach: <call / text, best time, language>" },
        "**Example note:** \"OUT OF OFFICE HAND-OFF (Lorena, out 10/6 to 10/8). Spoke with client 10/1. Interested in auto + home. Quote sent 10/1, waiting on driver's license. Follow up Friday 10/3 if no response. Best by text after 5 PM, prefers Spanish.\"",
        "The test for a good note: could the covering producer call this person without asking you anything?",
      ] },

    { h: "3. Inbound calls",
      body: [
        "You don't need to forward your phone. RingCentral already sends every unanswered call to the agency. What you set up is who handles the calls that come in for you.",
        { checks: [
          ["**Confirm who covers your calls, your sales leads and your quote and client follow-ups**", []],
          ["**Tell Debbie and the team where to send calls for you**", [
            "Debbie answers about 90% of inbound calls, so she has to know first.",
            "Send her, the covering producer and Amanda the routing below.",
          ] ],
        ] },
        "**If a client calls while you're gone:**",
        { table: { head: ["Who's calling", "Where the call goes"], rows: [
          ["Existing client with a service need (billing, claim, change, ID cards)", "Service: Debbie, Amanda or Crystal"],
          ["Someone you were already quoting or selling to", "The producer covering you"],
          ["A new lead", "The designated sales team member"],
          ["A client who asks for you by name", "The producer covering you. They read your hand-off note and help, instead of saying \"call back next week\""],
        ] } },
        "If the covering producer can't help with something, they take a message and set a dated task. They never just tell the client to call back.",
      ] },

    { h: "4. Appointments",
      body: [
        "Every appointment on the days you're out is either covered or moved, and the client knows which.",
        { checks: [
          ["**List the appointments booked while you're gone**", [
            "Open your calendar (Google Calendar and the AgencyZoom calendar) and look at every day you're out.",
            "In AgencyZoom, check **Tasks** assigned to you and due on those days. Call backs booked as tasks count.",
          ] ],
          ["**Make sure the covering producer knows which appointments are yours**", [
            "Add them as a guest on each calendar event, or forward the invite.",
            "Reassign the matching AgencyZoom task to them.",
            "Send them one list: name, day and time, phone, and what the appointment is for.",
          ] ],
          ["**Reschedule anything that can't be covered**", [
            "Call or text the client before you leave: \"I'll be out on <day>. Can we move our call to <new day and time>?\"",
            "Move the calendar event and the AgencyZoom task to the new date.",
            "Note it on the lead: \"Rescheduled from <old> to <new>, I'm out.\"",
          ] ],
          ["**Add context where the covering producer needs it**", [
            "Paste the hand-off note, or a link to the lead, in the calendar event's description.",
            "Say what the call should end with: a quote presented, a policy bound, or a dated next step.",
          ] ],
        ] },
      ] },

    { h: "5. Active quotes",
      body: [
        "If someone else takes over, they should be able to open the account and know exactly what to do next. For every quote that may need attention while you're gone, answer these five in a note on the lead:",
        { checks: [
          ["**Quote completed?**", ["Make sure the final quote is saved on the lead in AgencyZoom with its premium, and the quote PDF is in the lead's files. Still working on it? Write down what's missing (a driver, a VIN, a coverage choice)."]],
          ["**Quote sent?**", ["Emailed or texted: put the date and how it went in the note. Presented on the phone: say so, and move the lead to **Quotes Presented**."]],
          ["**Client contacted?**", ["Note the last time you actually spoke and what they said, e.g. \"wants to compare with State Farm\" or \"spouse has to agree\"."]],
          ["**Follow-up needed?**", ["Create an AgencyZoom task on the lead with the date and what to say. A follow-up with no date doesn't count."]],
          ["**Who is responsible for the follow-up?**", ["Assign that task to the covering producer, or to yourself only if the date is after you're back."]],
        ] },
        "For a sale pending bind (FSD), also write down what's left to finish it (signature, down payment, inspection, proof of prior) and who is doing each one.",
      ] },

    { h: "6. Final check before leaving",
      body: [
        "Ask yourself: **\"If a client calls tomorrow asking for me, can another team member open the account and know exactly what's going on?\"** Spend 15 minutes with the covering producer on your last afternoon and go through this together.",
        { checks: [
          ["Emails routed: auto-forward set (Gmail or Outlook)", []],
          ["Leads assigned: every lead that needs follow-up is on the covering producer", []],
          ["Quotes documented: every active quote answers the five questions", []],
          ["Follow-ups assigned: every follow-up is a dated task with an owner", []],
          ["Appointments covered or rescheduled", []],
          ["Important client information is in the lead notes, not in your head or your inbox", []],
          ["Team knows who is covering what: Debbie, the covering producer and Amanda all have the routing", []],
        ] },
      ] },

    { h: "The day you're back",
      body: [
        { checks: [
          ["Turn off email forwarding: in Gmail set forwarding to **Disable forwarding**; in Outlook turn off **Enable forwarding**, or delete the classic rule", []],
          ["Meet the covering producer for 10 minutes: what was sold, quoted and promised while you were out", []],
          ["Take back the leads that are still open, keeping any notes they added", []],
        ] },
        "A sale the covering producer closed from your notes and files is yours; one they had to dig for, or couldn't finish without chasing the pieces, is theirs.",
        "**Main rule:** don't just tell someone you're going to be gone. Set them up to cover you.",
      ] },
    ] },
  ],
};
