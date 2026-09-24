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
     quotes AgencyZoom: households and premium quoted, daily.py's three rules
            applied to leads active since the checkpoint (see quotedLive).

   Each part needs its own secrets and fails on its own: a missing or broken
   service leaves that part null with a reason, and the board keeps the
   checkpoint's figure for it. Results are cached in R2 at live/<day>.json
   for CACHE_SECONDS, so every viewer shares one refresh. */

export const CACHE_SECONDS = 120;
export const QUOTES_STALE_SECONDS = 180;
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
/* ONE AgencyZoom login, shared. The timer runs every minute and Cloudflare
   starts each run fresh, so a per-run login meant ~30 logins an hour -- and
   on 2026-09-24 AgencyZoom began refusing the Worker's logins (403) within
   an hour, while the same account still logged in fine from the nightly
   run's machine. So: the token (24 h TTL) is kept in R2 and reused by every
   run until it nears expiry; parallel calls in one run share one login; and
   a refused login pauses AgencyZoom for AZ_PAUSE_MINUTES instead of retrying
   every minute. worker-private/ is never served by any route. */
const AZ_TOKEN_KEY = "worker-private/az_token.json";
const AZ_PAUSE_KEY = "worker-private/az_pause.json";
export const AZ_PAUSE_MINUTES = 30;
let azJwt = null, azJwtExp = 0, azLogin = null;
export function _resetAzForTests() { azJwt = null; azJwtExp = 0; azLogin = null; }
const azClock = ms => new Date(ms).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", timeZone: "America/Phoenix" });

async function azToken(env, fetchFn) {
  if (azJwt && Date.now() < azJwtExp) return azJwt;
  if (azLogin) return azLogin;
  azLogin = (async () => {
    const R2 = env.BOARD;
    if (R2) {
      const saved = await R2.get(AZ_TOKEN_KEY);
      if (saved !== null) {
        const t = await saved.json();
        if (t.jwt && Date.now() < t.exp) { azJwt = t.jwt; azJwtExp = t.exp; return azJwt; }
      }
      const paused = await R2.get(AZ_PAUSE_KEY);
      if (paused !== null) {
        const x = await paused.json();
        if (Date.now() < x.until) throw new Error(`AgencyZoom paused until ${azClock(x.until)} after a refused login (${x.status})`);
      }
    }
    const r = await fetchFn(`${AZ}/v1/api/auth/login`, {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ username: env.AZ_USERNAME, password: env.AZ_PASSWORD }),
    });
    if (!r.ok) {
      if (R2 && (r.status === 403 || r.status === 429)) {
        await R2.put(AZ_PAUSE_KEY, JSON.stringify({ until: Date.now() + AZ_PAUSE_MINUTES * 60000, status: r.status, at: new Date().toISOString() }));
      }
      throw new Error(`AgencyZoom login ${r.status}`);
    }
    azJwt = (await r.json()).jwt;
    azJwtExp = Date.now() + 20 * 3600 * 1000;      // AgencyZoom's is 24 h; renew early
    if (R2) await R2.put(AZ_TOKEN_KEY, JSON.stringify({ jwt: azJwt, exp: azJwtExp }));
    return azJwt;
  })();
  try { return await azLogin; } finally { azLogin = null; }
}
async function azForget(env) {
  azJwt = null; azJwtExp = 0;
  if (env.BOARD) await env.BOARD.delete(AZ_TOKEN_KEY);
}
async function azGet(env, path, fetchFn, init = {}) {
  const tok = await azToken(env, fetchFn);
  const r = await fetchFn(`${AZ}${path}`, { ...init, headers: { ...(init.headers || {}), authorization: `Bearer ${tok}`, "content-type": "application/json" } });
  if (r.status === 401) await azForget(env);          // the saved login stopped working: log in afresh next time
  if (!r.ok) { const e = new Error(`AgencyZoom ${path} ${r.status}`); e.status = r.status; throw e; }
  return r.json();
}
const pause = ms => new Promise(res => setTimeout(res, ms));
// Between per-lead reads: az_client paces itself at 0.7 s, and a burst of
// note reads draws AgencyZoom 429s.
export const LEAD_READ_GAP_MS = 250;

/* Policies sold on `day`: newest-sold first (a handful of typo'd future
   dates sit on top), paged until the sold dates fall before `day`. */
export async function azPoliciesSold(env, day, fetchFn = fetch) {
  const out = [], seen = new Set();
  for (let page = 0; page < 10; page++) {
    const j = await azGet(env, "/v1/api/policies", fetchFn, {
      method: "POST", body: JSON.stringify({ page, pageSize: 100, sort: "soldDate", order: "desc" }),
    });
    const ps = j.policies || [];
    for (const p of ps) {
      if (!String(p.soldDate || "").startsWith(day)) continue;
      if (p.id != null) { if (seen.has(p.id)) continue; seen.add(p.id); }   // deduped by id, as az_client._paged does
      out.push(p);
    }
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

/* ---- households & premium quoted: AgencyZoom ---------------------------- */
/* daily.build_metrics's `hh`, the same three rules, extended past the
   checkpoint: a lead counts as a household quoted for a producer when (1)
   its quoteDate is today and it is assigned to them, (2) they moved it into
   a quoted stage today (the STAGE only, never the pipeline), or (3) a note
   of theirs today delivers a quote (daily.quote_presented). The patterns
   come from the checkpoint (live_basis.quotes), i.e. from daily.py itself.
   Premium quoted is every quote on each NEW household's lead, summed, as
   daily.py sums it. Only leads active since the checkpoint read its notes
   are looked at, newest first, and a lead is re-read only when its
   lastActivityDate moves. */

// Per run. Sized for the Workers free plan's 50 outside requests per
// invocation: 30 note reads + 8 quote reads + the lead list and a login.
export const NOTES_PER_REFRESH = 30;
export const QUOTES_PER_REFRESH = 8;

const ENTITIES = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", "#39": "'", nbsp: " " };
function unescapeHtml(s) {
  return s.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e) => {
    const k = e.toLowerCase();
    if (k.startsWith("#x")) return String.fromCodePoint(parseInt(k.slice(2), 16));
    if (k.startsWith("#")) return String.fromCodePoint(parseInt(k.slice(1), 10));
    return ENTITIES[k] ?? m;
  });
}
// live_contact._text
export function azText(body) {
  let b = String(body || "").replace(/<audio[\s\S]*?<\/audio>/g, " ");
  b = b.replace(/<[^>]+>/g, " ");
  return unescapeHtml(b).replace(/\s+/g, " ").trim();
}
// live_contact._move_stage_parts's move
function moveOf(text) {
  const m = text.match(/Comments:\s*(.+)$/);
  if (m) text = text.split(" Comments:")[0];
  return text.replace(/^Lead .*? moved from /, "").trim();
}

export function quotedBy(lead, notes, day, basis, rx) {
  const byAz = Object.fromEntries(Object.entries(basis.producers || {}).map(([n, v]) => [String(v.az_id), n]));
  const names = new Set(Object.keys(basis.producers || {}));
  const out = new Set();
  if (String(lead.quoteDate || "").startsWith(day)) {
    const w = byAz[String(lead.assignedTo)];
    if (w) out.add(w);
  }
  for (const n of notes || []) {
    if (!String(n.createDate || "").startsWith(day) || !names.has(n.createdBy)) continue;
    const text = azText(n.body);
    if (n.type === "MOVE_STAGE") {
      const mv = moveOf(text);
      const dest = (mv.includes(" to ") ? mv.split(" to ").pop() : mv).split("|").pop();
      if (rx.stage.test(dest)) out.add(n.createdBy);
    } else {
      const b = text.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
      if (rx.presented.test(b) && !rx.past.test(b)) out.add(n.createdBy);
    }
  }
  return out;
}

async function azLeadsActiveSince(env, since, fetchFn) {
  const out = [], seen = new Set();
  for (let page = 0; page < 5; page++) {
    const j = await azGet(env, "/v1/api/leads/list", fetchFn, {
      method: "POST", body: JSON.stringify({ page, pageSize: 100, sort: "lastActivityDate", order: "desc" }),
    });
    const ls = j.leads || [];
    for (const l of ls) if (String(l.lastActivityDate || "") >= since && !seen.has(l.id)) { seen.add(l.id); out.push(l); }
    if (!ls.length || String(ls[ls.length - 1].lastActivityDate || "") < since) break;
  }
  return out;
}

/* `memo` is the previous refresh's per-lead reads (R2), so a lead is only
   re-read when its activity moved; returns the deltas and the new memo. */
export async function quotedLive(env, day, basis, memo, fetchFn = fetch) {
  const q = basis.quotes;
  if (!q) throw new Error("needs a checkpoint built after this update");
  const rx = { stage: new RegExp(q.stage_pattern, "i"), presented: new RegExp(q.presented_pattern, "i"), past: new RegExp(q.past_pattern, "i") };
  const already = Object.fromEntries(Object.entries(q.quoted_leads || {}).map(([w, ids]) => [w, new Set(ids.map(String))]));
  const prev = (memo && memo.checkpoint_since === q.activity_since && memo.leads) || {};
  const leads = {};
  let notesRead = 0, quotesRead = 0, pending = 0, limited = false;
  // Most likely quoted first: moved stage since the checkpoint, then
  // assigned to a producer, then everything else; newest activity first
  // within each (the list already arrives newest first, and sort is stable).
  const producerAz = new Set(Object.values(basis.producers || {}).map(v => String(v.az_id)));
  const rank = l => (String(l.enterStageDate || "") >= q.activity_since ? 0 : producerAz.has(String(l.assignedTo)) ? 1 : 2);
  const active = (await azLeadsActiveSince(env, q.activity_since, fetchFn)).sort((a, b) => rank(a) - rank(b));
  for (const l of active) {
    const id = String(l.id), was = prev[id];
    if (was && was.act === l.lastActivityDate) { leads[id] = was; continue; }
    if (notesRead >= NOTES_PER_REFRESH || limited) { pending++; if (was) leads[id] = was; continue; }
    notesRead++;
    let notes;
    try {
      if (notesRead > 1) await pause(LEAD_READ_GAP_MS);
      notes = await azGet(env, `/v1/api/leads/${id}/notes`, fetchFn);
    } catch (e) {
      // Rate limited: keep what this batch read, the rest waits for the next.
      if (e.status !== 429) throw e;
      limited = true; pending++; if (was) leads[id] = was; continue;
    }
    leads[id] = { act: l.lastActivityDate, who: [...quotedBy(l, Array.isArray(notes) ? notes : [], day, basis, rx)], prem: was ? was.prem : null };
  }
  const per = Object.fromEntries(Object.keys(basis.producers || {}).map(n => [n, { hh: 0, pq: 0, new_leads: [] }]));
  for (const [id, v] of Object.entries(leads)) {
    const fresh = v.who.filter(w => per[w] && !(already[w] || new Set()).has(id));
    if (!fresh.length) continue;
    if (v.prem == null) {
      if (quotesRead >= QUOTES_PER_REFRESH || limited) { pending++; continue; }
      quotesRead++;
      let qs;
      try {
        await pause(LEAD_READ_GAP_MS);
        qs = await azGet(env, `/v1/api/leads/${id}/quotes`, fetchFn);
      } catch (e) {
        if (e.status !== 429) throw e;
        limited = true; pending++; continue;
      }
      const arr = Array.isArray(qs) ? qs : (qs || {}).quotes || [];
      v.prem = arr.reduce((s, x) => s + (Number(x.premium) || 0), 0);
    }
    for (const w of fresh) { per[w].hh++; per[w].pq += v.prem; per[w].new_leads.push(Number(id)); }
  }
  for (const v of Object.values(per)) v.pq = Math.round(v.pq);
  return { data: { per, pending, looked_at: Object.keys(leads).length }, memo: { checkpoint_since: q.activity_since, leads } };
}

/* ---- the route --------------------------------------------------------- */

const NEEDS = {
  dials: ["RC_CLIENT_ID", "RC_CLIENT_SECRET", "RC_SERVER_URL", "RC_JWT"],
  sales: ["AZ_USERNAME", "AZ_PASSWORD"],
  util: ["INSIGHTFUL_TOKEN"],
  quotes: ["AZ_USERNAME", "AZ_PASSWORD"],
};

const part = async (env, key, fn) => {
  const missing = NEEDS[key].filter(k => !env[k]);
  if (missing.length) return { ok: false, reason: `not connected: Worker secret${missing.length > 1 ? "s" : ""} ${missing.join(", ")} not set` };
  try { return { ok: true, data: await fn() }; }
  catch (e) { return { ok: false, reason: String(e && e.message || e) }; }
};

/* Dials, sales and utilization: a handful of requests, refreshed together. */
export async function computeFast(env, day, basis, fetchFn = fetch) {
  const [dials, sales, util] = await Promise.all([
    part(env, "dials", async () => dialDeltas(basis, await rcCallLog(env, day, fetchFn))),
    part(env, "sales", async () => {
      const [pols, names] = await Promise.all([azPoliciesSold(env, day, fetchFn), azLeadSources(env, fetchFn)]);
      return salesFrom(basis, pols, names);
    }),
    part(env, "util", async () => insightfulUtil(env, day, basis, fetchFn)),
  ]);
  return { fetched_at: new Date().toISOString(), dials, sales, util };
}

/* Households and premium quoted: one batch of lead reads, carried on from
   the last batch's memo. */
export async function computeQuotes(env, day, basis, memo, fetchFn = fetch) {
  let next = memo;
  const quotes = await part(env, "quotes", async () => {
    const r = await quotedLive(env, day, basis, memo, fetchFn);
    next = r.memo;
    return r.data;
  });
  return { fetched_at: new Date().toISOString(), quotes, memo: next };
}

// Kept for callers/tests that want every part in one go.
export async function computeLive(env, day, basis, fetchFn = fetch, memo = null) {
  const [fast, q] = await Promise.all([computeFast(env, day, basis, fetchFn), computeQuotes(env, day, basis, memo, fetchFn)]);
  return { day, ...fast, quotes: q.quotes, _memo: q.memo };
}

const keys = day => ({ fast: `live/${day}.json`, quotes: `live/${day}-quotes.json`, memo: `live/${day}-quote-reads.json` });
async function r2json(env, key) {
  const o = await env.BOARD.get(key);
  return o === null ? null : o.json();
}
async function r2put(env, key, v) {
  await env.BOARD.put(key, JSON.stringify(v), { httpMetadata: { contentType: "application/json" } });
}
async function checkpointFor(env, day) {
  const snap = await r2json(env, `intraday/${day}.json`);
  if (!snap) return { reason: "no checkpoint yet today" };
  if (!snap.live_basis) return { reason: "the last checkpoint predates live figures", as_of: snap.as_of };
  return { as_of: snap.as_of, basis: snap.live_basis };
}
const fresh = (c, cp, secs) => c && c.checkpoint === cp && Date.now() - Date.parse(c.fetched_at) < secs * 1000;

/* A part that fails this run (a 429, a timeout) keeps its last good answer
   for the same checkpoint rather than blanking the board; `as_of` says how
   old that answer is. */
function keepGood(prev, next, cp, parts) {
  const out = { ...next };
  for (const k of parts) {
    const p = prev && prev.checkpoint === cp.as_of ? prev[k] : null;
    if (!(next[k] || {}).ok && p && p.ok) out[k] = { ...p, as_of: p.as_of || prev.fetched_at };
  }
  return out;
}
async function refreshFast(env, day, cp) {
  const k = keys(day);
  const prev = await r2json(env, k.fast);
  const out = keepGood(prev, { checkpoint: cp.as_of, ...(await computeFast(env, day, cp.basis)) }, cp, ["dials", "sales", "util"]);
  await r2put(env, k.fast, out);
  return out;
}
async function refreshQuotes(env, day, cp) {
  const k = keys(day);
  const [prev, memoIn] = await Promise.all([r2json(env, k.quotes), r2json(env, k.memo)]);
  const { memo, ...res } = await computeQuotes(env, day, cp.basis, memoIn);
  const out = keepGood(prev, { checkpoint: cp.as_of, ...res }, cp, ["quotes"]);
  if (memo && res.quotes.ok) await r2put(env, k.memo, memo);
  await r2put(env, k.quotes, out);
  return out;
}

export async function getLive(env, day) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) return jsonResp({ error: "bad day" }, 400);
  if (day !== azToday()) return jsonResp({ live: false, reason: "only today is live" }, 200);
  const cp = await checkpointFor(env, day);
  if (!cp.basis) return jsonResp({ live: false, reason: cp.reason, checkpoint: cp.as_of }, 200);
  const k = keys(day);
  // The one-minute timer (scheduled below) normally keeps both fresh; a
  // viewer only pays for a refresh when it has fallen behind.
  let fast = await r2json(env, k.fast), quotes = await r2json(env, k.quotes);
  const [f, q] = await Promise.all([
    fresh(fast, cp.as_of, CACHE_SECONDS) ? fast : refreshFast(env, day, cp),
    fresh(quotes, cp.as_of, QUOTES_STALE_SECONDS) ? quotes : refreshQuotes(env, day, cp),
  ]);
  return jsonResp({ live: true, day, checkpoint: cp.as_of, fetched_at: f.fetched_at,
    dials: f.dials, sales: f.sales, util: f.util, quotes: q.quotes, quotes_fetched_at: q.fetched_at }, 200);
}

/* Worker cron (wrangler.jsonc, every minute in business hours): even minutes
   refresh dials/sales/utilization, odd minutes read the next batch of
   leads, so no one run needs more than ~45 outside requests and the board
   stays live whether or not anyone has it open. */
export async function scheduledLive(event, env) {
  const day = azToday();
  const cp = await checkpointFor(env, day);
  if (!cp.basis) return;
  const minute = new Date(event.scheduledTime || Date.now()).getUTCMinutes();
  if (minute % 2 === 0) await refreshFast(env, day, cp);
  else await refreshQuotes(env, day, cp);
}

function jsonResp(body, status) {
  return new Response(JSON.stringify(body), {
    status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}
