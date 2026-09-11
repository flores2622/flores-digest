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
import METHODOLOGY_MD from "../coaching/METHODOLOGY.md";
import ROLEPLAY_MD from "../coaching/ROLEPLAY.md";
import TRAINING_MD from "../coaching/TRAINING.md";

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

      if (parts[1] === "intraday" && parts.length === 3) {
        return getIntraday(env, parts[2]);
      }

      if (parts[1] === "training" && parts.length === 2) {
        return json(trainingDecks());
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

/** GET /api/intraday/:day -> that day's latest intraday snapshot, or 404 if
 * intraday.py hasn't run yet today, or the day has already been finalized
 * and intraday.py refused to touch it (see that script's own guard) --
 * either way the UI's fallback is simply not to show a live panel, same as
 * getDay's "no report for this day". A SEPARATE key from days/<day>.json on
 * purpose: an in-progress snapshot must never be servable from, or mistaken
 * for, the finalized document. */
async function getIntraday(env, day) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) {
    return json({ error: "bad day" }, 400);
  }
  const obj = await env.BOARD.get(`intraday/${day}.json`);
  if (obj === null) {
    return json({ error: "no intraday snapshot for this day", day }, 404);
  }
  return new Response(obj.body, {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

/** Parses coaching/TRAINING.md into [{ name, cards: [{ front, back }] }].
 * Static content bundled with the Worker (no R2 read, no per-request
 * computation beyond this parse) -- `## Deck Name` starts a deck, `### Front
 * text` starts a card, everything until the next `###` or `##` is the back.
 * Prose before the first `## ` (the file's own editorial notes) is skipped
 * on purpose -- it's for whoever edits this file next, not the flashcard UI.
 * Cached at module scope: parsed once per Worker isolate, not per request. */
let _trainingCache = null;
function trainingDecks() {
  if (_trainingCache) return _trainingCache;
  const lines = TRAINING_MD.split("\n");
  const decks = [];
  let deck = null, card = null;
  for (const line of lines) {
    const deckMatch = line.match(/^## (.+)/);
    const cardMatch = line.match(/^### (.+)/);
    if (deckMatch) {
      deck = { name: deckMatch[1].trim(), cards: [] };
      decks.push(deck);
      card = null;
    } else if (cardMatch && deck) {
      card = { front: cardMatch[1].trim(), back: "" };
      deck.cards.push(card);
    } else if (card) {
      card.back += (card.back ? "\n" : "") + line;
    }
  }
  for (const d of decks) {
    for (const c of d.cards) c.back = c.back.trim();
  }
  _trainingCache = { decks };
  return _trainingCache;
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

   THE PERSONA PROMPTS ARE THE ANSWER KEY AND MUST NEVER REACH THE CLIENT.
   They encode which objection(s) the persona raises and what a good
   response looks like, so the model can judge in character whether the
   producer's real reply earns a concession. Sending this to the browser
   would let a producer read the correct answer instead of practicing it --
   it lives only in coaching/ROLEPLAY.md, read at build time (below), never
   served to a client.

   ONE BRAIN, NOT TWO (Frank, 2026-09-10: "I feel like it should all be one
   brain"). Apollo's judgment -- what counts as an objection, an overcome
   attempt, an assumptive close -- is defined exactly once, in
   coaching/METHODOLOGY.md's "Core judgment" section, and reused verbatim
   here for grading Role Play. The persona prompts (the simulated PROSPECT,
   not Apollo) live in coaching/ROLEPLAY.md instead, since they're a
   different concern -- character behavior, not judgment. Both files are
   imported as raw text below (see wrangler.jsonc's `rules` entry for how
   Workers gets a filesystem-free build to treat a .md file as a string) and
   split into named sections by _section(). Change what Apollo considers an
   objection/addressed/overcome/assumptive in METHODOLOGY.md ONLY -- it
   takes effect here automatically. Change a persona's behavior, or Role
   Play's own grading framing (the checklist, the JSON shape), in
   ROLEPLAY.md.

   No streaming yet (v1): the board's frontend is plain script-tag JS
   with no fetch-stream reader wired up. A ~1-3 sentence reply comes back
   fast enough non-streaming that this is a reasonable place to start;
   revisit if replies feel slow in practice.
*/

/** Splits a "brain" markdown file into named sections by exact header text
 * match, e.g. "### Beginner" or "## Grading (Apollo)". A section runs from
 * right after its own header to the next markdown heading of any level (or
 * EOF) -- so sections don't need to be listed together or in order. Throws
 * if the header text isn't found so a renamed/retyped heading fails loudly
 * at Worker startup, rather than silently sending Apollo an empty prompt. */
function _section(md, header) {
  const marker = `\n${header}\n`;
  const start = md.indexOf(marker);
  if (start === -1) throw new Error(`brain file missing section: ${header}`);
  const contentStart = start + marker.length;
  const nextHeading = md.slice(contentStart).search(/\n#{1,6} /);
  const contentEnd = nextHeading === -1 ? md.length : contentStart + nextHeading;
  return md.slice(contentStart, contentEnd).trim();
}

const CORE_JUDGMENT = _section(
  METHODOLOGY_MD,
  "## Core judgment (shared with Role Play grading — do not fork this list)"
);

const PERSONAS = {
  easy: {
    label: "Beginner",
    blurb: "Open to a quote, minimal resistance",
    system: _section(ROLEPLAY_MD, "### Beginner"),
  },
  medium: {
    label: "Medium",
    blurb: "Interested, but raises multiple objections that don't hold much resistance",
    system: _section(ROLEPLAY_MD, "### Medium"),
  },
  hard: {
    label: "Professional",
    blurb: "Skeptical, cycles through objections, doesn't fold easily",
    system: _section(ROLEPLAY_MD, "### Professional"),
  },
};

// Apollo (Frank's name for the coaching brain, 2026-09-10) grading a Role
// Play session: METHODOLOGY.md's shared judgment, prepended to ROLEPLAY.md's
// own grading framing -- see the "ONE BRAIN, NOT TWO" note above.
const GRADE_SYSTEM = CORE_JUDGMENT + "\n\n" + _section(ROLEPLAY_MD, "## Grading (Apollo)");

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

/** Appended to a persona's system prompt when the frontend sends
 * lead_source -- backstory flavor only (site/public/index.html's
 * LEAD_SOURCES), shown to the producer on the pre-call debrief screen so
 * they know the same context you do (Frank, 2026-09-11: "they should know
 * ... what the lead source is"). This is scene-setting, not the answer
 * key -- it must never change which objections you raise or how hard you
 * hold them, only how you'd naturally react if asked how you were
 * contacted or why you're on the phone. */
function leadSourceInstruction(backstory) {
  if (!backstory) return "";
  return `\n\nBackstory context for how this call came about: ${backstory} If the producer asks how you were contacted or why you're on the phone, answer consistently with this -- but it does not change which objections you raise, how hard you hold them, or anything else about your difficulty level above.`;
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
  const leadSource = typeof body.lead_source === "string" ? body.lead_source.slice(0, 500) : "";
  const system = persona.system + focusObjectionInstruction(focusObjections) + leadSourceInstruction(leadSource);

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
    lead_source: typeof body.lead_source === "string" ? body.lead_source.slice(0, 200) : "",
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
