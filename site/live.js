/* Live figures between checkpoints (Frank, 2026-09-24: "just live data where
   its already at on everything possible, and the header up there specifying
   what is stale from the last hourly run").

   GET /api/live/<day>, today only. The last checkpoint (intraday.py) is the
   checked figure; this keeps three things current from the source itself,
   by the same rules the Python pipeline uses:

     dials  RingCentral call log. Extends the checkpoint's OWN per-number
            verdicts (live_basis, from live_board.py) with the calls it has not
            seen yet -- it never re-decides what counts. An excluded number
            stays excluded, a duplicate-lead number adds attempts but no
            contact, and a number nobody has checked yet counts as new
            business until the next checkpoint checks it ("unchecked").
     sales  AgencyZoom policies by agentId + soldDate, minus BOB and Rewrite
            (live_basis.not_a_sale, from lead_sources.py) -- the same rule as
            digest_config.is_real_sale. Cross-sells by the same
            existing-household lead sources.
     util   Insightful, insightful_util.pull()'s formula: productive usage over
            attendance, per person; team minute-rounded, Amanda excluded.

   Each part needs its own secrets and fails on its own: a missing or broken
   service leaves that part null with a reason, and the board keeps the
   checkpoint's figure for it. Results are cached in R2 at live/<day>.json
   for CACHE_SECONDS, so every viewer shares one refresh. */

export const CACHE_SECONDS = 120;
const AZ_OFFSET = "-07:00";

export function azToday(now = new Date()) {
  return new Date(now.getTime() - 7 * 3600 * 1000).toISOString().slice(0, 10);
}
function nextDay(day) {
  const d = new Date(`${day}T12:00:00Z`);
  d.setUTCDate(d.getUTCDate() + 1);
  return d.toISOString().slice(0, 10);
}
const norm = n => String(n || "").trim().replace(/!+$/, "").trim().replace(/\s+/g, " ").toLowerCase();

/* ---- dials: RingCentral ------------------------------------------------ */

let rcToken = null, rcTokenExp = 0;
async function rcAccessToken(env, fetchFn) {
  if (rcToken && Date.now() < rcTokenExp - 120000) return rcToken;
  const base = env.RC_SERVER_URL.replace(/\/+$/, "");
  const r = await fetchFn(`${base}/restapi/oauth/token`, {
    method: "POST",
    headers: {
      authorization: "Basic " + btoa(`${env.RC_CLIENT_ID}:${env.RC_CLIENT_SECRET}`),
      "content-type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
      assertion: env.RC_JWT,
    }),
  });
  if (!r.ok) throw new Error(`RingCentral login ${r.status}`);
  const j = await r.json();
  rcToken = j.access_token;
  rcTokenExp = Date.now() + (Number(j.expires_in) || 3600) * 1000;
  return rcToken;
}

export async function rcCallLog(env, day, fetchFn = fetch) {
  const base = env.RC_SERVER_URL.replace(/\/+$/, "");
  const tok = await rcAccessToken(env, fetchFn);
  const recs = [];
  for (let page = 1; page < 20; page++) {
    const q = new URLSearchParams({
      dateFrom: `${day}T00:00:00${AZ_OFFSET}`, dateTo: `${nextDay(day)}T00:00:00${AZ_OFFSET}`,
      view: "Detailed", perPage: "1000", page: String(page),
    });
    const r = await fetchFn(`${base}/restapi/v1.0/account/~/call-log?${q}`,
      { headers: { authorization: `Bearer ${tok}` } });
    if (!r.ok) throw new Error(`RingCentral call log ${r.status}`);
    const j = await r.json();
    recs.push(...(j.records || []));
    if (page >= ((j.paging || {}).totalPages || 1)) break;
  }
  return recs;
}

// rc_client.owner_ext_id: extension.id, else from.extensionId.
const ownerExt = r => String((r.extension || {}).id || (r.from || {}).extensionId || "");

/* The calls since the checkpoint, applied to its own verdicts. Returns, per
   producer, how much to ADD to the checkpoint's dials / total_dials /
   raw_dials, and how many numbers nobody has checked yet. */
export function dialDeltas(basis, recs) {
  const seen = new Set(basis.rc_ids || []);
  const byExt = Object.fromEntries(Object.entries(basis.producers || {}).map(([n, v]) => [String(v.rc_id), n]));
  const sets = k => Object.fromEntries(Object.entries(basis[k] || {}).map(([n, v]) => [n, new Set(v)]));
  const counted = sets("counted"), dropped = sets("dropped"), excluded = sets("excluded");
  const out = {}, fresh = {};
  for (const n of Object.keys(basis.producers || {})) {
    out[n] = { dials: 0, total_dials: 0, raw_dials: 0, unchecked: 0, calls_since: 0 };
    fresh[n] = new Set();
  }
  for (const r of recs) {
    const who = byExt[ownerExt(r)];
    if (!who || r.direction !== "Outbound") continue;
    const num = (r.to || {}).phoneNumber;
    if (!num || seen.has(String(r.id))) continue;
    const o = out[who];
    o.calls_since++;
    o.raw_dials++;
    if (excluded[who].has(num)) continue;          // service / renewal / no record
    o.total_dials++;
    if (counted[who].has(num) || dropped[who].has(num)) continue;   // known number, one more attempt
    if (!fresh[who].has(num)) { fresh[who].add(num); o.dials++; o.unchecked++; }
  }
  return out;
}

/* ---- sales: AgencyZoom -------------------------------------------------- */

const AZ = "https://app.agencyzoom.com";
let azJwt = null, azJwtExp = 0;
async function azToken(env, fetchFn) {
  if (azJwt && Date.now() < azJwtExp) return azJwt;
  const r = await fetchFn(`${AZ}/v1/api/auth/login`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ username: env.AZ_USERNAME, password: env.AZ_PASSWORD }),
  });
  if (!r.ok) throw new Error(`AgencyZoom login ${r.status}`);
  azJwt = (await r.json()).jwt;
  azJwtExp = Date.now() + 12 * 3600 * 1000;
  return azJwt;
}
async function azGet(env, path, fetchFn, init = {}) {
  const tok = await azToken(env, fetchFn);
  const r = await fetchFn(`${AZ}${path}`, { ...init, headers: { ...(init.headers || {}), authorization: `Bearer ${tok}`, "content-type": "application/json" } });
  if (!r.ok) throw new Error(`AgencyZoom ${path} ${r.status}`);
  return r.json();
}

/* Policies sold on `day`: newest-sold first (a handful of typo'd future
   dates sit on top), paged until the sold dates fall before `day`. */
export async function azPoliciesSold(env, day, fetchFn = fetch) {
  const out = [];
  for (let page = 0; page < 10; page++) {
    const j = await azGet(env, "/v1/api/policies", fetchFn, {
      method: "POST", body: JSON.stringify({ page, pageSize: 100, sort: "soldDate", order: "desc" }),
    });
    const ps = j.policies || [];
    for (const p of ps) if (String(p.soldDate || "").startsWith(day)) out.push(p);
    const last = ps.length ? String(ps[ps.length - 1].soldDate || "").slice(0, 10) : "";
    if (!ps.length || last < day) break;
  }
  return out;
}
export async function azLeadSources(env, fetchFn = fetch) {
  const rows = await azGet(env, "/v1/api/lead-sources", fetchFn);
  return Object.fromEntries((rows || []).map(r => [r.id, r.name]));
}

/* digest_config.real_sales + bundle_classification's cross_sell, per producer. */
export function salesFrom(basis, policies, sourceNames) {
  const notSale = new Set(basis.not_a_sale || []);
  const existing = new Set(basis.existing_household || []);
  const byAz = Object.fromEntries(Object.entries(basis.producers || {}).map(([n, v]) => [String(v.az_id), n]));
  const out = Object.fromEntries(Object.keys(basis.producers || {}).map(n => [n, { pol: 0, ps: 0, cross_sell: 0 }]));
  for (const p of policies) {
    const who = byAz[String(p.agentId)];
    if (!who) continue;
    const src = norm(sourceNames[p.leadSourceId]);
    if (notSale.has(src)) continue;
    out[who].pol++;
    out[who].ps += Number(p.premium) || 0;
    if (existing.has(src)) out[who].cross_sell++;
  }
  for (const v of Object.values(out)) v.ps = Math.round(v.ps);
  return out;
}

/* ---- utilization: Insightful ------------------------------------------- */

const INS = "https://app.insightful.io/api/v1";
const hhmmMs = ms => { const s = ms / 1000; return `${String(Math.floor(s / 3600)).padStart(2, "0")}:${String(Math.floor(s % 3600 / 60)).padStart(2, "0")}`; };
async function insGet(env, path, params, fetchFn) {
  const q = params ? `?${new URLSearchParams(params)}` : "";
  const r = await fetchFn(`${INS}/${path}${q}`, { headers: { authorization: `Bearer ${env.INSIGHTFUL_TOKEN}` } });
  if (!r.ok) throw new Error(`Insightful ${path} ${r.status}`);
  const j = await r.json();
  return Array.isArray(j) ? j : (j || {}).data || [];
}
export async function insightfulUtil(env, day, basis, fetchFn = fetch) {
  const start = Date.parse(`${day}T00:00:00${AZ_OFFSET}`), end = start + 86400000;
  const win = { start: String(start), end: String(end), timezone: "America/Phoenix" };
  const roster = {};
  for (const e of await insGet(env, "employee", null, fetchFn)) if (!e.deactivated) roster[e.name] = e.id;
  const attendance = {};
  for (const a of await insGet(env, "analytics/attendance", win, fetchFn)) attendance[a.employeeId] = a.duration;
  const exclude = new Set(basis.util_exclude || []);
  const per = {};
  let pm = 0, tm = 0;
  for (const [name, eid] of Object.entries(roster)) {
    const total = attendance[eid];
    if (!total) continue;                          // licensed but not tracked today
    const buckets = await insGet(env, "analytics/productivity", { ...win, employeeId: eid }, fetchFn);
    const prod = buckets.filter(b => b.productivity === 1).reduce((s, b) => s + (b.usage || 0), 0);
    // (pct, total "HH:MM", productive "HH:MM") -- insightful_util.pull()'s shape
    per[name] = [Math.round(prod / total * 10000) / 100, hhmmMs(total), hhmmMs(prod)];
    if (!exclude.has(name)) { pm += Math.floor(prod / 60000); tm += Math.floor(total / 60000); }
  }
  return { per, team: tm ? Math.round(pm / tm * 10000) / 100 : null };
}

/* ---- the route --------------------------------------------------------- */

const NEEDS = {
  dials: ["RC_CLIENT_ID", "RC_CLIENT_SECRET", "RC_SERVER_URL", "RC_JWT"],
  sales: ["AZ_USERNAME", "AZ_PASSWORD"],
  util: ["INSIGHTFUL_TOKEN"],
};

export async function computeLive(env, day, basis, fetchFn = fetch) {
  const part = async (key, fn) => {
    const missing = NEEDS[key].filter(k => !env[k]);
    if (missing.length) return { ok: false, reason: `not connected: Worker secret${missing.length > 1 ? "s" : ""} ${missing.join(", ")} not set` };
    try { return { ok: true, data: await fn() }; }
    catch (e) { return { ok: false, reason: String(e && e.message || e) }; }
  };
  const [dials, sales, util] = await Promise.all([
    part("dials", async () => dialDeltas(basis, await rcCallLog(env, day, fetchFn))),
    part("sales", async () => {
      const [pols, names] = await Promise.all([azPoliciesSold(env, day, fetchFn), azLeadSources(env, fetchFn)]);
      return salesFrom(basis, pols, names);
    }),
    part("util", async () => insightfulUtil(env, day, basis, fetchFn)),
  ]);
  return { day, fetched_at: new Date().toISOString(), dials, sales, util };
}

export async function getLive(env, day) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) return jsonResp({ error: "bad day" }, 400);
  if (day !== azToday()) return jsonResp({ live: false, reason: "only today is live" }, 200);
  const snap = await env.BOARD.get(`intraday/${day}.json`);
  if (snap === null) return jsonResp({ live: false, reason: "no checkpoint yet today" }, 200);
  const doc = await snap.json();
  const basis = doc.live_basis;
  if (!basis) return jsonResp({ live: false, reason: "the last checkpoint predates live figures", checkpoint: doc.as_of }, 200);

  const key = `live/${day}.json`;
  const cached = await env.BOARD.get(key);
  if (cached !== null) {
    const c = await cached.json();
    if (c.checkpoint === doc.as_of && Date.now() - Date.parse(c.fetched_at) < CACHE_SECONDS * 1000) {
      return jsonResp({ live: true, cached: true, ...c }, 200);
    }
  }
  const out = { checkpoint: doc.as_of, ...(await computeLive(env, day, basis)) };
  await env.BOARD.put(key, JSON.stringify(out), { httpMetadata: { contentType: "application/json" } });
  return jsonResp({ live: true, cached: false, ...out }, 200);
}

function jsonResp(body, status) {
  return new Response(JSON.stringify(body), {
    status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}
