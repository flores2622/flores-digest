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
