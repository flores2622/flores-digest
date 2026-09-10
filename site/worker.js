/**
 * The Sales Floor board's Worker.
 *
 * ORIGINALLY WRITTEN AS TWO PAGES FUNCTIONS (functions/api/days/index.js and
 * functions/api/days/[day].js). That is the wrong shape for what got
 * provisioned: `flores-board` is a plain Cloudflare Workers project (Workers
 * Builds, Git-connected), not a Pages project, and Workers has no built-in
 * file-based routing for a functions/ folder -- see Cloudflare's own
 * Pages-to-Workers migration guide, which says a functions/ folder must
 * either be compiled with `wrangler pages functions build` or rewritten as a
 * single Worker script. This repo has no npm/wrangler toolchain otherwise
 * (it is a Python project), so rewriting by hand is simpler than adding a
 * compile step for two small routes. Consolidated here 2026-09-05.
 *
 * ROUTING. `/api/days` and `/api/days/:day` are handled below; everything
 * else falls through to the ASSETS binding, which serves site/public/
 * (index.html, the dashboard).
 *
 * THE DATA IS NOT PUBLIC, AND THIS WORKER FAILS CLOSED. Everything served
 * under /api/days is customer NPI -- lead names, phone numbers, notes on what
 * coverage someone was quoted. The R2 bucket itself is private (no r2.dev
 * URL, no public custom domain) and the site is meant to sit behind
 * Cloudflare Access.
 *
 * An earlier version of this comment said the Worker "deliberately does NOT
 * re-check identity" because Access would already have allowed the request,
 * and that a second check would be security theatre. That was wrong in a way
 * worth recording: it assumed Access was configured. On 2026-09-06 it was
 * not -- the Worker was deployed and reachable on its workers.dev URL with no
 * policy in front of it, and the only reason nothing leaked is that the
 * bucket happened to still be empty. One unticked dashboard box was the whole
 * control.
 *
 * So /api/* now verifies the Access JWT itself, and refuses when it cannot:
 *
 *   - ACCESS_TEAM_DOMAIN or ACCESS_AUD unset -> 503, serve no data at all.
 *     Unconfigured means closed, never open. This is what makes the dangerous
 *     window impossible rather than merely unlikely.
 *   - Header/cookie missing, signature bad, aud wrong, expired -> 403.
 *
 * The static shell (index.html) is still served unauthenticated on purpose:
 * it contains no customer data, and letting it load means a misconfiguration
 * shows up as a visible error in the UI instead of a blank page nobody
 * investigates.
 *
 * This is defence in depth, not a replacement for Access. Turn Access on.
 *
 * BINDINGS (wrangler.jsonc): `BOARD` -> the flores-board R2 bucket, `ASSETS`
 * -> site/public.
 * VARS: `ACCESS_TEAM_DOMAIN` (e.g. "floresinsurance" for
 * floresinsurance.cloudflareaccess.com) and `ACCESS_AUD` (the Access
 * application's Application Audience tag). Set both in the Worker's
 * Settings -> Variables. Until they are set, /api/* returns 503.
 */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const parts = url.pathname.split("/").filter(Boolean);

    if (parts[0] === "api") {
      // Fail closed BEFORE any bucket read. Every early return below leaves
      // R2 untouched, so a misconfigured or unauthenticated request cannot
      // even cause a lookup, let alone a response body.
      const gate = await requireAccess(request, env);
      if (gate) return gate;

      if (parts[1] === "days") {
        if (parts.length === 2) return listDays(env);
        if (parts.length === 3) return getDay(env, parts[2]);
      }

      if (parts[1] === "months" && parts.length === 3) {
        return getMonth(env, parts[2]);
      }

      if (parts[1] === "folios" && parts.length === 3) {
        return getFolio(env, parts[2]);
      }

      if (parts[1] === "roleplay") {
        if (parts[2] === "turn" && request.method === "POST") {
          return roleplayTurn(request, env);
        }
        if (parts[2] === "grade" && request.method === "POST") {
          return roleplayGrade(request, env);
        }
        if (parts[2] === "history" && request.method === "GET") {
          return roleplayHistory(env, url.searchParams.get("producer"));
        }
      }
      return json({ error: "not found" }, 404);
    }

    return env.ASSETS.fetch(request);
  },
};

/** GET /api/days -> { days: ["2026-09-04", "2026-09-03", ...] }, newest first.
 *
 * The date picker's list. Keys only -- never object bodies, so this stays
 * cheap however many days accumulate. R2 list is paginated (1000 keys per
 * page, about four years of business days); we follow the cursor rather than
 * assuming one page, because the failure mode of not doing so is the picker
 * silently losing its oldest days years from now, which nobody would connect
 * back to this file.
 */
async function listDays(env) {
  const days = [];
  let cursor;
  do {
    const listed = await env.BOARD.list({ prefix: "days/", cursor });
    for (const o of listed.objects) {
      const m = o.key.match(/^days\/(\d{4}-\d{2}-\d{2})\.json$/);
      if (m) days.push(m[1]);
    }
    cursor = listed.truncated ? listed.cursor : undefined;
  } while (cursor);
  days.sort().reverse();
  // A new day lands every weekday at ~7 PM Arizona. Caching this for even a
  // minute means someone refreshing at 7:01 does not see tonight.
  return json({ days });
}

/** GET /api/days/:day -> the day document from R2. */
async function getDay(env, day) {
  // Only ever ISO dates. The bucket key is built from user-supplied path, so
  // this is what stops `../` and friends from reaching another prefix.
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) {
    return json({ error: "bad day" }, 400);
  }

  const obj = await env.BOARD.get(`days/${day}.json`);
  if (obj === null) {
    // A day with no document is ordinary -- weekends, holidays, and any day
    // before the board went live. The UI shows "no report for this day"
    // rather than an error.
    return json({ error: "no report for this day", day }, 404);
  }

  return new Response(obj.body, {
    headers: {
      "content-type": "application/json; charset=utf-8",
      // Never cache a day document at the edge. Tonight's document is
      // rewritten if the run is re-run, and a stale board that disagrees
      // with the email is exactly the failure this whole migration exists
      // to end.
      "cache-control": "no-store",
    },
  });
}

function json(body, status) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}


/* -------------------------------------------------------------------------
   Cloudflare Access verification.

   Returns a Response to REFUSE the request, or null to allow it. Written so
   that every path that is not a fully verified identity returns a Response --
   there is no fall-through that reaches the data.
   ------------------------------------------------------------------------- */

let jwksCache = { keys: null, at: 0 };
const JWKS_TTL_MS = 60 * 60 * 1000;   // Access rotates keys ~every 6 weeks

async function requireAccess(request, env) {
  const team = env.ACCESS_TEAM_DOMAIN;
  const aud = env.ACCESS_AUD;

  // UNCONFIGURED MEANS CLOSED. If someone deploys this Worker without the
  // Access vars -- or Access is removed and the vars go with it -- the data
  // endpoints stop working rather than becoming public. A loud outage is the
  // correct failure here; a quiet leak is not.
  if (!team || !aud) {
    return json({
      error: "board is not configured for authenticated access",
      detail: "ACCESS_TEAM_DOMAIN and ACCESS_AUD must be set on this Worker. " +
              "Refusing to serve customer data without them.",
    }, 503);
  }

  const token =
    request.headers.get("Cf-Access-Jwt-Assertion") ||
    cookie(request, "CF_Authorization");
  if (!token) return json({ error: "not authenticated" }, 403);

  try {
    const payload = await verifyJwt(token, team, aud);
    if (!payload) return json({ error: "not authenticated" }, 403);
  } catch (_) {
    // Never surface the reason: a verification oracle is a gift to whoever is
    // probing. The Worker's own logs carry the detail if it is ever needed.
    return json({ error: "not authenticated" }, 403);
  }
  return null;
}

function cookie(request, name) {
  const raw = request.headers.get("Cookie") || "";
  for (const part of raw.split(";")) {
    const [k, ...v] = part.trim().split("=");
    if (k === name) return v.join("=");
  }
  return null;
}

function b64urlToBytes(s) {
  const b64 = s.replace(/-/g, "+").replace(/_/g, "/")
               .padEnd(s.length + ((4 - (s.length % 4)) % 4), "=");
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

async function jwks(team) {
  const now = Date.now();
  if (jwksCache.keys && now - jwksCache.at < JWKS_TTL_MS) return jwksCache.keys;
  const r = await fetch(`https://${team}.cloudflareaccess.com/cdn-cgi/access/certs`);
  if (!r.ok) throw new Error(`jwks ${r.status}`);
  const { keys } = await r.json();
  jwksCache = { keys, at: now };
  return keys;
}

async function verifyJwt(token, team, aud) {
  const [h, p, sig] = token.split(".");
  if (!h || !p || !sig) return null;

  const header = JSON.parse(new TextDecoder().decode(b64urlToBytes(h)));
  const payload = JSON.parse(new TextDecoder().decode(b64urlToBytes(p)));

  // Signature must actually be checked -- decoding a JWT proves nothing, and
  // "alg": "none" is the classic way this check gets bypassed.
  if (header.alg !== "RS256") return null;

  const key = (await jwks(team)).find((k) => k.kid === header.kid);
  if (!key) return null;

  const pub = await crypto.subtle.importKey(
    "jwk", key,
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false, ["verify"],
  );
  const ok = await crypto.subtle.verify(
    "RSASSA-PKCS1-v1_5", pub,
    b64urlToBytes(sig),
    new TextEncoder().encode(`${h}.${p}`),
  );
  if (!ok) return null;

  // A valid signature from the right team is not enough: without the aud
  // check, a token minted for ANY other Access application on this account
  // would open the board.
  const auds = Array.isArray(payload.aud) ? payload.aud : [payload.aud];
  if (!auds.includes(aud)) return null;
  if (payload.iss !== `https://${team}.cloudflareaccess.com`) return null;

  const now = Math.floor(Date.now() / 1000);
  if (typeof payload.exp !== "number" || payload.exp <= now) return null;
  if (typeof payload.nbf === "number" && payload.nbf > now) return null;

  return payload;
}

/** GET /api/months/:month -> the month-to-date rollup, e.g. 2026-09.
 *
 * Served straight from months/<YYYY-MM>.json, which publish_board.py rewrites
 * every night from that month's day documents. The Worker deliberately does
 * NOT aggregate days itself: a full month is up to 23 documents at 20-135 KB
 * each, so doing it here would mean megabytes of R2 reads on every page load,
 * for every viewer, growing through the month.
 */
async function getMonth(env, month) {
  if (!/^\d{4}-\d{2}$/.test(month)) {
    return json({ error: "bad month" }, 400);
  }
  const obj = await env.BOARD.get(`months/${month}.json`);
  if (obj === null) {
    return json({ error: "no rollup for this month", month }, 404);
  }
  return new Response(obj.body, {
    headers: {
      "content-type": "application/json; charset=utf-8",
      // Rewritten nightly, and rewritten again by any past-day rebuild.
      "cache-control": "no-store",
    },
  });
}

/** GET /api/folios/:end -> the folio rollup ending on that date, e.g.
 * 2026-09-18. Folios (Frank's "Folio Close Dates" calendar) do not align to
 * calendar months, so this is a separate object from months/<YYYY-MM>.json --
 * see publish_board.publish_folio, which rewrites it every night alongside
 * the month rollup, and on any past-day rebuild.
 */
async function getFolio(env, end) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(end)) {
    return json({ error: "bad folio end date" }, 400);
  }
  const obj = await env.BOARD.get(`folios/${end}.json`);
  if (obj === null) {
    return json({ error: "no folio rollup for this date", end }, 404);
  }
  return new Response(obj.body, {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

/* -----------------------------------------------------------------------
   Role Play — an objection/closing practice partner.

   Grounded in Coral's licensed "One Call Close" workbook (Insurance Sales
   Lab): its Closing Objections Workflow is a numbered decision tree --
   "I want to think about it", "I need to talk to my spouse", "your price
   is too high", etc. -- each with the agency's own scripted technique
   (address the REAL concern behind the objection, then immediately
   re-ask for the sale as a direct question, never a soft "would that be
   ok"). That is also exactly the assumptive-vs-permission-seeking
   distinction coaching_cards.py already grades real calls on
   (askq/asks), so the practice partner and the real-call coaching speak
   the same language on purpose.

   THE PERSONA PROMPTS BELOW ARE THE ANSWER KEY AND MUST NEVER REACH THE
   CLIENT. They encode which objection(s) the persona raises and what a
   good response looks like, so the model can judge in character whether
   the producer's real reply earns a concession. Sending this to the
   browser would let a producer read the correct answer instead of
   practicing it -- it exists only in this Worker's memory, server-side.

   No streaming yet (v1): the board's frontend is plain script-tag JS
   with no fetch-stream reader wired up. A ~1-3 sentence reply comes back
   fast enough non-streaming that this is a reasonable place to start;
   revisit if replies feel slow in practice.
*/
const PERSONAS = {
  easy: {
    label: "Beginner",
    blurb: "Open to a quote, minimal resistance",
    system: `You are playing a phone prospect on a call with an insurance producer who is practicing their pitch. You are warm and already leaning toward yes -- you like the price and coverage discussed so far.

The call can open with one soft HOOK-stage line if it fits ("who's calling?" or "I already have insurance, but sure, go ahead") -- answer it and move on right away, don't dwell on it. Then raise exactly ONE soft closing objection, in your own words, along the lines of "can you just email me the quote" or "what do I need to do to get started." Do not raise any other closing objection after that.

If the producer responds by directly and confidently asking for the next step (a specific, direct question -- which card, which bank, what day to start -- not a tentative or permission-seeking one), agree and move toward closing within the next reply or two. If they hesitate, only ask soft permission questions, or let a reply go by without asking for the sale, stay warm but non-committal ("yeah, maybe, let me think about it") until they ask directly.

If the producer brings up life insurance near the end and you already have it through work or elsewhere, say so plainly but don't make it a fight -- if they explain a real reason to also have a personal policy, you're open to hearing more.

Never break character, never explain your own reasoning, never mention this is practice. Reply in 1-3 short sentences, like a real phone call -- no stage directions, no narration.`,
  },
  // Redefined 2026-09-10 (Frank): breadth of objections, not depth of
  // resistance -- multiple objections in one call, but each one folds easily,
  // as distinct from "hard" below which holds firmly onto fewer objections.
  medium: {
    label: "Medium",
    blurb: "Interested, but raises multiple objections that don't hold much resistance",
    system: `You are playing a phone prospect on a call with an insurance producer who is practicing their pitch. You are genuinely interested and easy to work with, but you don't just say yes right away -- you raise several small objections along the way.

The call can open with one soft HOOK-stage line if it fits ("I'm kind of busy" / "I just renewed with my current company") -- give the producer one exchange to get past it, then move on into the pitch either way.

As the call goes on, raise TWO or THREE of these real closing objections in sequence, one at a time, in your own words -- pick whichever fit the conversation so far: "I want to think about it" / "your price is higher than what I'm paying now" / "I need to talk to my spouse first" / "I'd want to shop this around a bit" / "can you just email me the quote."

You don't hold these objections hard. As soon as the producer says ANYTHING that responds to what you actually raised -- even an imperfect or generic attempt -- ease up and move on to the next objection, or agree if that was the last one. Only restate the same objection once, and only if the producer's reply completely ignored it (talked about something else entirely, or just repeated the price/coverage pitch with no acknowledgment at all).

If the producer brings up life insurance near the end and you already have it through work or elsewhere, raise it as a soft one-line objection too, but give in easily if they say anything relevant back.

Never break character, never explain your own reasoning, never mention this is practice. Reply in 1-3 short sentences, like a real phone call -- no stage directions, no narration.`,
  },
  hard: {
    label: "Professional",
    blurb: "Skeptical, cycles through objections, doesn't fold easily",
    system: `You are playing a phone prospect on a call with an insurance producer who is practicing their pitch. You are skeptical, though not rude, and genuinely hard to close.

Open with a real HOOK-stage objection ("who is this, and how'd you get my number" / "I never requested a quote" / "I'm not interested, I just renewed") and make the producer actually earn their way past it before you engage with the pitch at all.

Once you're engaged, raise TWO or THREE of these closing objections in sequence (pick the order that fits the conversation, but don't skip more than one): "I want to think about it", "I need to talk to my spouse", "your price is too high", "I'm loyal to my current agent", "I want to shop this around."

For EACH objection, only ease up (move to the next objection, or agree if that was the last one) if the producer's response both (a) speaks to the REAL concern behind that specific objection rather than a generic answer, AND (b) immediately re-asks for the sale as a direct, assumptive question -- never "would that be okay" or a reply that trails off without asking. If they do only one of those, or neither, hold firm and restate the SAME objection in different words -- do not concede and do not move on. If the producer goes more than two replies in a row without directly asking for the close again, end the call ("I have to go, maybe another time").

If they bring up life insurance, push back hard by default ("I already have it, I'm covered") and only engage seriously if they give you a specific, real reason (mortgage payoff, dependents) rather than a generic pitch.

Never break character, never explain your own reasoning, never mention this is practice. Reply in 1-3 short sentences, natural and a little impatient, like a real phone call -- no stage directions, no narration.`,
  },
};

// Apollo (Frank's name for the coaching brain, 2026-09-10) grading a Role
// Play session -- the same "person" as coaching/METHODOLOGY.md's live-call
// grader, applied to a practice call instead of a real one.
const GRADE_SYSTEM = `You are Apollo, grading a practice sales call. A producer was practicing objection handling and closing against an AI playing a skeptical prospect, primed with real objections from this agency's own closing script. Read the full transcript (roles: "producer" is the human practicing, "prospect" is the character they were practicing against).

Score these four items, each as {"item": <name>, "met": true|false, "note": <one sentence, quote the producer's own words where useful>}:
  "Assumptive language"        -- did the producer state next steps/information rather than asking permission for them, especially at the close?
  "Addressed the real concern" -- when an objection came up, did the producer respond to the actual concern behind it, not a generic price/coverage recap?
  "Re-asked immediately"       -- after addressing an objection, did the producer immediately ask for the sale again as a direct question, not "would that be ok"?
  "Kept driving the call"      -- did the producer keep moving the conversation forward rather than pausing, hesitating, or dropping the thread?

Then return:
  "resolved" -- true only if the prospect actually conceded/agreed to move forward by the end of this transcript.
  "summary"  -- 2 sentences, plain, what happened.
  "tip"      -- one specific, actionable tip for next time. Quote the producer's own weakest line if there is one.

Return ONLY a JSON object with exactly these keys: checklist, resolved, summary, tip. No prose outside the JSON.`;

async function callClaude(env, { system, messages, maxTokens }) {
  if (!env.ANTHROPIC_API_KEY) {
    throw new Error("ANTHROPIC_API_KEY is not configured on this Worker");
  }
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": env.ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model: "claude-sonnet-5",
      max_tokens: maxTokens,
      system,
      messages,
      thinking: { type: "disabled" },
    }),
  });
  if (!r.ok) {
    throw new Error(`Claude API ${r.status}: ${(await r.text()).slice(0, 300)}`);
  }
  const data = await r.json();
  return (data.content || [])
    .filter((b) => b.type === "text")
    .map((b) => b.text)
    .join("");
}

function roleplaySlug(name) {
  return String(name || "unknown").trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "unknown";
}

/** Appended to a persona's system prompt when the frontend sends
 * focus_objections -- this producer's own real, unresolved objection
 * categories from the trailing 4 completed weeks (site/public/index.html's
 * producerWeakSpots/objectionWindow4wk). Steers WHICH objection the
 * persona reaches for, not how hard it holds -- that's still entirely the
 * difficulty-level text above (Frank, 2026-09-10: "the objections
 * presented to the producer by the AI bot should be based off of what
 * they have been unsuccessful on"). */
function focusObjectionInstruction(categories) {
  if (!categories || !categories.length) return "";
  return `\n\nThis producer's real calls over the last 4 weeks show they have NOT been overcoming these specific objection types: ${categories.join(", ")}. When you raise your closing objection(s) this call, phrase them so they land as one of these categories rather than a generic one from the list above -- everything else about how hard you push stays exactly as described for your difficulty level.`;
}

/** POST /api/roleplay/turn {persona, history, focus_objections} -> {reply}
 *
 * `history` is the growing [{role: "producer"|"prospect", content}, ...]
 * transcript the frontend already holds -- the Claude API is stateless, so
 * the full conversation rides on every turn, same as any other multi-turn
 * chat. `focus_objections` (optional, up to 3 category strings) steers
 * which objections the persona reaches for -- see
 * focusObjectionInstruction(). Mapped to the API's user/assistant roles
 * here so the persona
 * prompt above can talk about "producer" and "prospect" in plain English.
 */
async function roleplayTurn(request, env) {
  let body;
  try {
    body = await request.json();
  } catch (_) {
    return json({ error: "bad request body" }, 400);
  }
  const persona = PERSONAS[body.persona];
  if (!persona) return json({ error: "unknown persona" }, 400);
  const history = Array.isArray(body.history) ? body.history : [];
  if (!history.length || history[history.length - 1].role !== "producer") {
    return json({ error: "history must end with a producer turn" }, 400);
  }

  const messages = history.map((h) => ({
    role: h.role === "producer" ? "user" : "assistant",
    content: String(h.content || "").slice(0, 4000),
  }));
  const focusObjections = Array.isArray(body.focus_objections)
    ? body.focus_objections.filter((c) => typeof c === "string").slice(0, 3)
    : [];
  const system = persona.system + focusObjectionInstruction(focusObjections);

  try {
    const reply = await callClaude(env, { system, messages, maxTokens: 300 });
    return json({ reply: reply.trim() });
  } catch (e) {
    return json({ error: "role-play turn failed", detail: String(e).slice(0, 300) }, 502);
  }
}

/** POST /api/roleplay/grade {producer, persona, history} -> {grade}
 *
 * Grades the transcript, then stores the whole session (transcript +
 * grade) under roleplay/<producer-slug>/<iso-timestamp>.json in the same
 * private R2 bucket the day documents live in -- same bucket, new prefix,
 * no new infrastructure. Scores and sessions persist across devices this
 * way, not just in one browser's local storage.
 */
async function roleplayGrade(request, env) {
  let body;
  try {
    body = await request.json();
  } catch (_) {
    return json({ error: "bad request body" }, 400);
  }
  const persona = PERSONAS[body.persona];
  if (!persona) return json({ error: "unknown persona" }, 400);
  const history = Array.isArray(body.history) ? body.history : [];
  if (!history.length) return json({ error: "no transcript to grade" }, 400);
  const producer = String(body.producer || "").trim();
  if (!producer) return json({ error: "producer is required" }, 400);

  const transcriptText = history
    .map((h) => `${h.role === "producer" ? "Producer" : "Prospect"}: ${h.content}`)
    .join("\n");

  let grade;
  try {
    const raw = await callClaude(env, {
      system: GRADE_SYSTEM,
      messages: [{ role: "user", content: transcriptText.slice(0, 12000) }],
      maxTokens: 1000,
    });
    const m = raw.match(/\{[\s\S]*\}/);
    grade = m ? JSON.parse(m[0]) : null;
  } catch (e) {
    return json({ error: "grading failed", detail: String(e).slice(0, 300) }, 502);
  }
  if (!grade) return json({ error: "grading returned no parsable result" }, 502);

  const now = new Date();
  const session = {
    producer,
    persona: body.persona,
    persona_label: persona.label,
    history,
    grade,
    created_at: now.toISOString(),
  };
  const key = `roleplay/${roleplaySlug(producer)}/${now.toISOString()}.json`;
  try {
    await env.BOARD.put(key, JSON.stringify(session), {
      httpMetadata: { contentType: "application/json" },
    });
  } catch (e) {
    // The producer still gets their grade even if the save failed -- a
    // lost practice record is a much smaller problem than a lost grade.
    return json({ grade, saved: false, save_error: String(e).slice(0, 200) });
  }
  return json({ grade, saved: true, key });
}

/** GET /api/roleplay/history?producer=X -> {sessions: [...]}
 *
 * Most recent first, capped at 25. Without a producer filter, lists
 * across everyone -- small volume expected (practice reps, not a
 * once-a-day batch), so a plain list-then-fetch is fine; no rollup file
 * the way months/folios have one.
 */
async function roleplayHistory(env, producer) {
  const prefix = producer ? `roleplay/${roleplaySlug(producer)}/` : "roleplay/";
  const keys = [];
  let cursor;
  do {
    const listed = await env.BOARD.list({ prefix, cursor });
    for (const o of listed.objects) keys.push(o.key);
    cursor = listed.truncated ? listed.cursor : undefined;
  } while (cursor);
  keys.sort().reverse();

  const sessions = [];
  for (const key of keys.slice(0, 25)) {
    const obj = await env.BOARD.get(key);
    if (obj) sessions.push(await obj.json());
  }
  return json({ sessions });
}
