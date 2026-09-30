/* Blueprints -- the plain-language guides to the Sales Floor (Frank,
   2026-09-30: "if Im out for a week and want amanda to coach, she should
   know what everything means, how the model coaches, where everything is";
   "They should be in regular language, not AI prompt language").

   One manager guide (Apollo's Road Map, the ARM) and three producer guides (new,
   mid-level, experienced). The board renders them on Learning Center >
   Road Map (blueprintPanel in index.html). Frank named it 2026-09-30:
   "call it Apollo's Road Map (ARM)".

   KEEP THIS CURRENT. Whenever a change alters what a number means, how
   Apollo scores or coaches a call, what a page shows or where it sits,
   update the matching lines here in the same change and move `updated`.
   CLAUDE.md says the same.

   Format: each guide is a list of sections {h, body}; body items are a
   paragraph string, {list: [...]}, {steps: [...]} (numbered), {terms:
   [[term, meaning], ...]} or {table: {head: [...], rows: [[...], ...]}}.
   **bold** works inside any text. Nothing else is interpreted. */
window.BLUEPRINTS = {
  updated: "2026-09-30",
  guides: [

  /* ------------------------------------------------------------------ */
  { key: "manager", manager: true, title: "Apollo's Road Map (ARM)",
    who: "For managers: how the Sales Floor works, what every number means, how Apollo coaches, and how to run coaching when Frank is out.",
    sections: [
    { h: "What this is",
      body: [
        "The Sales Floor is the agency's board. It pulls the day's calls from RingCentral, the leads, quotes, policies, tasks and notes from AgencyZoom, and utilization from Insightful, and turns them into one picture of the day.",
        "It has three coaches, each with a name:",
        { terms: [
          ["Apollo", "Sales and coaching. Listens to every recorded sales conversation, writes a coaching card for it, and runs Role Play."],
          ["Athena", "Service. The Service Center: SRs, renewals, tasks, call backs, texts, and the Service Playbook."],
          ["Cerberus", "Commercial. Frank's alone; nobody else's numbers include commercial work."],
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
        "The left bar holds the Centers. Each Center has tabs across the top. Every page shares two filters at the top: **the day or range** (a single day, this week, month to date, year to date, a folio, or custom dates) and **the producer** (everyone, or one person). **Every number, card and bar opens the accounts behind it**; click it and the list appears underneath.",
        { table: { head: ["Where", "What it's for"], rows: [
          ["Sales Center > Digest", "The day at a glance: dials, contacts, quotes, sales, closing ratio, the leaderboard, speed to dial and reply, task completion, household completion, utilization, Coach AI scores."],
          ["Sales Center > Sales", "The Sales sheet. Log a sale, look back at any folio, and break sales down by lead source, product or producer. Self-reported, not the official Premium Sold. Live sales are added to it automatically."],
          ["Sales Center > Texts & Emails", "Every text and email with a lead: what each producer typed (automation counted apart), replies still waiting, and how fast replies were answered."],
          ["Coaching Center > Cards", "One coaching card per recorded sales conversation. Filter by producer, day or objection."],
          ["Coaching Center > Objections", "Every objection Apollo found, grouped, with how each was handled."],
          ["Coaching Center > Wins and Losses", "Patterns across calls: assumed the quote, assumed the sale, sent the quote instead of keeping them on the phone, and the patterns that only show up across many calls, each with the calls behind it."],
          ["Learning Center > Role Play", "Practice calls against an AI prospect, graded by Apollo."],
          ["Learning Center > Session History", "Every graded Role Play session. Managers see everyone's; a producer sees their own."],
          ["Learning Center > Training", "Flashcards, quizzes and matching games on objections, information gathering and technique."],
          ["Learning Center > Road Map", "The ARM and the producer guides."],
          ["Service Center", "Athena's side: the Service Digest and the Renewals tab."],
        ] } },
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
          ["HH / Prem. Sold", "Households marked sold, and the premium on the policies sold. **BOB and Rewrite are not sales.** A renewal is not a sale. Selling a product the household doesn't have yet is a sale, even to a twenty-year customer."],
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
          "Open Coaching Center > Wins and Losses for the last week. Note each producer's Sent the Quote count and assumed-the-quote rate.",
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
  { key: "new", title: "New Producer",
    who: "For someone brand new to insurance sales: what the board is, how you're measured, and how to build good habits from day one.",
    sections: [
    { h: "Welcome",
      body: [
        "The Sales Floor is where you see how your day is going and how to get better. Every recorded conversation you have with a lead is reviewed by **Apollo**, the agency's sales coach, and turned into a coaching card: what went well, what to fix, and the words you could have used.",
        "Nobody expects you to be good at this on day one. The point of the board is to show you one thing to work on at a time.",
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
          "**Ask questions (discovery).** Who drives, what vehicles, the home, who's in the household.",
          "**Get what they pay now.** You can't beat a price you don't know.",
          "**Get their renewal date.** If now isn't the time, you know when is.",
          "**Know the product.** Answer their questions clearly.",
          "**Give them the numbers on the call.** Say the price and what it covers, while they're still on the phone.",
          "**Offer the bundle.** Home and auto together, and ask about anything else they have elsewhere.",
          "**Set a specific next step.** A day and a time, not \"I'll call you sometime.\"",
          "**Write your note** in AgencyZoom after the call.",
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
        "Learning Center > Role Play gives you a practice call with an AI prospect. Start on **Beginner**. Talk to them like a real person: they'll chat back if you build rapport. When you finish, Apollo grades you on four things: assumptive language, answering the real concern, asking again right after an objection, and keeping the call moving.",
        "Use Learning Center > **Training** for flashcards on objections and what to ask.",
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
  { key: "mid", title: "Mid-Level Producer",
    who: "For producers who have the basics and want to close more consistently.",
    sections: [
    { h: "Where to focus",
      body: [
        "You know how to run a call. Now the gains come from consistency: assuming every time, handling objections instead of accepting them, and treating follow-ups as their own kind of call.",
        "Coaching Center > **Wins and Losses** is your scoreboard for this. It shows, for you and the team, how often you assumed the quote, assumed the sale, and sent the quote instead of keeping them on the phone, with every call behind each number.",
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
  { key: "exp", title: "Experienced Producer",
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
      ] },

    { h: "Where experienced producers slip",
      body: [
        { list: [
          "Sending the quote out of habit because the call is going well. The leaderboard's **Sent the Quote** column shows how often you do it.",
          "Skipping discovery because you've seen a hundred of these, then missing the current premium or renewal date.",
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
          "Drill the objection group you lose most (Coaching Center > Objections, filtered to you).",
          "Read your Wins and Losses monthly, not just your sales.",
          "Help newer producers: sit in on a Role Play or play them one of your strong calls.",
        ] },
      ] },

    { h: "What Apollo can't see",
      body: [
        "Apollo only knows what's recorded and written down. A call on your cell, a conversation in the office, or a quote you never noted doesn't exist to it. If the board is wrong about you, the fix is usually a note in AgencyZoom.",
      ] },
    ] },

  ],
};
