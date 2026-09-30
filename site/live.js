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
     contacts / talk
            RingCentral's calls since the checkpoint, judged provisionally
            from the notes quotedLive reads (live_notes.contactDeltas); the
            next checkpoint reads the recordings and settles them.
     messages
            texts and emails, messages.build's rules on those same notes,
            carried on from the checkpoint (live_notes.messageDeltas).

   Each part needs its own secrets and fails on its own: a missing or broken
   service leaves that part null with a reason, and the board keeps the
   checkpoint's figure for it. Results are cached in R2 at live/<day>.json
   for CACHE_SECONDS, so every viewer shares one refresh. */

import { contactItems, messageEvents, contactDeltas, messageDeltas, last10, e164, noteText, rxOf } from "./live_notes.js";

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
  // az_corpus.e164 on both sides (day_calls.dials_from's key, Frank
  // 2026-09-30); a checkpoint built before then listed raw RingCentral
  // numbers, which this maps the same way.
  const sets = k => Object.fromEntries(Object.entries(basis[k] || {}).map(([n, v]) => [n, new Set(v.map(x => e164(x) || x))]));
  const counted = sets("counted"), dropped = sets("dropped"), excluded = sets("excluded");
  const out = {}, fresh = {};
  for (const n of Object.keys(basis.producers || {})) {
    out[n] = { dials: 0, total_dials: 0, raw_dials: 0, unchecked: 0, calls_since: 0 };
    fresh[n] = new Set();
  }
  for (const r of recs) {
    const who = byExt[ownerExt(r)];
    if (!who || r.direction !== "Outbound") continue;
    const raw = (r.to || {}).phoneNumber, num = e164(raw) || raw;
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

/* The API's own address (Frank, 2026-09-30). AgencyZoom's published spec
   (api.agencyzoom.com/openapi/agencyzoom.yaml) names https://api.agencyzoom.com
   as the server for integrations; app.agencyzoom.com is the web app's, a
   separate AWS load balancer. From 09-28 app.agencyzoom.com refused the
   Worker (403) from 2:29 PM Arizona to the next morning, two days running,
   whatever the volume, while the same token worked from elsewhere. Same
   endpoints, same data, same login on both (checked 2026-09-30). */
const AZ = "https://api.agencyzoom.com";

/* ---- what AgencyZoom sees of us, for when it refuses ------------------- */

/* Every AgencyZoom request is counted by hour and endpoint, and every
   refusal (403 / 429, login included) is kept whole -- status, the reply's
   headers and the first of its body, the time, and the address Cloudflare
   sent it from (cloudflare.com/cdn-cgi/trace) -- in
   worker-private/az_log/<day>.json, served by no route. Enough to tell whose
   firewall said no and to hand AgencyZoom support the facts. Flushed once
   per run (flushAzLog), never per request. */
const AZ_LOG_PREFIX = "worker-private/az_log/";
const AZ_LOG_REFUSALS = 50;                        // per day, the first ones
let azCalls = {}, azRefusals = [];
const hourAZ = () => new Date(Date.now() - 7 * 3600 * 1000).toISOString().slice(11, 13);
function countAz(path) {
  const ep = path.split("?")[0].replace(/\/\d+/g, "/N");
  const h = hourAZ();
  const b = azCalls[h] || (azCalls[h] = {});
  b[ep] = (b[ep] || 0) + 1;
}
async function egress(fetchFn) {
  try {
    const t = await (await fetchFn("https://cloudflare.com/cdn-cgi/trace")).text();
    const f = Object.fromEntries(t.trim().split("\n").map(l => l.split("=")));
    return { ip: f.ip, colo: f.colo, loc: f.loc };
  } catch (_) { return null; }
}
async function noteRefusal(path, r, fetchFn) {
  let body = "";
  try { body = (await r.clone().text()).slice(0, 600); } catch (_) {}
  const keep = ["server", "content-type", "date", "via", "retry-after", "x-amzn-requestid", "x-amzn-errortype",
    "x-amz-cf-id", "x-cache", "www-authenticate"];
  const headers = {};
  for (const [k, v] of r.headers) if (keep.includes(k.toLowerCase()) || k.toLowerCase().startsWith("x-amzn")) headers[k] = v;
  azRefusals.push({ at: new Date().toISOString(), host: AZ, path, status: r.status, headers, body,
    egress: await egress(fetchFn) });
}
export async function flushAzLog(env, day) {
  if (!env.BOARD || (!Object.keys(azCalls).length && !azRefusals.length)) return;
  const calls = azCalls, refusals = azRefusals;
  azCalls = {}; azRefusals = [];
  try {
    const key = `${AZ_LOG_PREFIX}${day}.json`;
    const o = await env.BOARD.get(key);
    const log = o === null ? { day, host: AZ, calls: {}, refusals: [] } : await o.json();
    for (const [h, eps] of Object.entries(calls)) {
      const b = log.calls[h] || (log.calls[h] = {});
      for (const [ep, n] of Object.entries(eps)) b[ep] = (b[ep] || 0) + n;
    }
    for (const x of refusals) if (log.refusals.length < AZ_LOG_REFUSALS) log.refusals.push(x);
    log.refused = (log.refused || 0) + refusals.length;
    await env.BOARD.put(key, JSON.stringify(log));
  } catch (e) { console.log(`AgencyZoom log not saved: ${e && e.message || e}`); }
}
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
    countAz("/v1/api/auth/login");
    const r = await fetchFn(`${AZ}/v1/api/auth/login`, {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ username: env.AZ_USERNAME, password: env.AZ_PASSWORD }),
    });
    if (r.status === 403 || r.status === 429) await noteRefusal("/v1/api/auth/login", r, fetchFn);
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
/* A REFUSED REQUEST PAUSES AGENCYZOOM TOO, not only a refused login. On
   2026-09-28 every AgencyZoom request from the Worker began returning 403 at
   2:29 PM -- sales, sold households, quotes and messages all went dark --
   while the very same token worked from the nightly run's machine: a block
   on the addresses the Worker calls from, not on the login. The Worker kept
   asking ~40 times every two minutes all afternoon. Now a 403 pauses every
   AgencyZoom part for AZ_PAUSE_MINUTES, like a refused login; the board
   keeps each part's last good answer meanwhile (keepGood). */
let azPauseSeen = { at: 0, until: 0 };
async function azPausedUntil(env) {
  if (!env.BOARD) return 0;
  if (Date.now() - azPauseSeen.at < 20000) return azPauseSeen.until;   // once per run, not per request
  const o = await env.BOARD.get(AZ_PAUSE_KEY);
  azPauseSeen = { at: Date.now(), until: o === null ? 0 : ((await o.json()).until || 0) };
  return azPauseSeen.until;
}
export function _resetAzPauseForTests() { azPauseSeen = { at: 0, until: 0 }; }
async function azGet(env, path, fetchFn, init = {}) {
  const until = await azPausedUntil(env);
  if (Date.now() < until) throw new Error(`AgencyZoom paused until ${azClock(until)} after a refused request`);
  const tok = await azToken(env, fetchFn);
  countAz(path);
  const r = await fetchFn(`${AZ}${path}`, { ...init, headers: { ...(init.headers || {}), authorization: `Bearer ${tok}`, "content-type": "application/json" } });
  if (r.status === 403 || r.status === 429) await noteRefusal(path, r, fetchFn);
  if (r.status === 401) await azForget(env);          // the saved login stopped working: log in afresh next time
  if (r.status === 403 && env.BOARD) {
    const x = { until: Date.now() + AZ_PAUSE_MINUTES * 60000, status: 403, path, at: new Date().toISOString() };
    await env.BOARD.put(AZ_PAUSE_KEY, JSON.stringify(x));
    azPauseSeen = { at: Date.now(), until: x.until };
  }
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
/* Lead source names, fetched ONCE per Arizona day (2026-09-29, after
   AgencyZoom began refusing the Worker on 09-28): the list barely changes,
   and fetching it every two minutes was ~30 requests an hour for nothing. A
   source created mid-day is named from the next day on; BOB and Rewrite,
   the only ones that change a figure, long exist. */
const LEAD_SOURCES_KEY = "worker-private/lead_sources.json";
export async function azLeadSources(env, fetchFn = fetch) {
  const day = azToday();
  if (env.BOARD) {
    const o = await env.BOARD.get(LEAD_SOURCES_KEY);
    if (o !== null) { const x = await o.json(); if (x.day === day && x.names) return x.names; }
  }
  const rows = await azGet(env, "/v1/api/lead-sources", fetchFn);
  const names = Object.fromEntries((rows || []).map(r => [r.id, r.name]));
  if (env.BOARD) await env.BOARD.put(LEAD_SOURCES_KEY, JSON.stringify({ day, names }));
  return names;
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

/* Households sold (Frank, 2026-09-28): every lead marked sold today, read in
   the same refresh as the policies so the HH/Prem. Sold tile is live
   whenever sales are. Leads come newest activity first (lastActivityDate is
   UTC; marking a lead sold moves it), back to the start of the Arizona day.

   KEPT, NOT RE-PAGED (2026-09-29, after AgencyZoom began refusing the
   Worker on 09-28). Paging the whole day's list every two minutes was up to
   five requests each time by the afternoon. Any change to a lead -- marked
   sold, unmarked, a note, a stage move -- puts it back at the top, so the
   day's list is kept in R2 (live/<day>-leads.json) and each refresh pages
   only down to where the last one started (ACTIVE_OVERLAP_MS earlier, for
   ties), usually one page. The quotes pass reads the same copy
   (fromShared). `complete` is false only if the page cap ever stopped a
   read short of what the day's list already held -- then the board also
   keeps the checkpoint's own sold-lead rows, as before. */
const SOLD_LEAD_PAGES = 5;
const ACTIVE_OVERLAP_MS = 2 * 60000;
const utcMs = s => Date.parse(String(s || "").replace(" ", "T").slice(0, 19) + "Z");
const utcStr = ms => new Date(ms).toISOString().slice(0, 19).replace("T", " ");
export async function soldLeadsToday(env, day, basis, fetchFn = fetch, kept = null) {
  const since = `${day} 07:00:00`;   // midnight Arizona (UTC-7), in UTC
  const byAz = Object.fromEntries(Object.entries(basis.producers || {}).map(([n, v]) => [String(v.az_id), n]));
  const prev = kept && kept.day === day && Array.isArray(kept.leads) && kept.newest ? kept : null;
  const stopAt = prev ? utcStr(Math.max(utcMs(since), utcMs(prev.newest) - ACTIVE_OVERLAP_MS)) : since;
  const fresh = new Map();
  let reached = false, newest = prev ? prev.newest : "";
  for (let page = 0; page < SOLD_LEAD_PAGES; page++) {
    const jl = await azGet(env, "/v1/api/leads/list", fetchFn, {
      method: "POST", body: JSON.stringify({ page, pageSize: 100, sort: "lastActivityDate", order: "desc" }),
    });
    const ls = jl.leads || [];
    for (const l of ls) {
      const act = String(l.lastActivityDate || "");
      if (act < since) continue;
      if (act > newest) newest = act;
      if (!fresh.has(l.id)) fresh.set(l.id, leadFields(l));
    }
    if (!ls.length || String(ls[ls.length - 1].lastActivityDate || "") < stopAt) { reached = true; break; }
  }
  // Stopped short of what the kept list covers: there may be a gap, so the
  // day's list starts again from this read, marked incomplete.
  const merged = new Map(reached && prev ? prev.leads.map(l => [l.id, l]) : []);
  for (const [id, l] of fresh) merged.set(id, l);
  const complete = reached && (prev ? !!prev.complete : true);
  const per = {}, raw = [];
  const existing = new Set(basis.existing_household || []);
  const notSale = new Set(basis.not_a_sale || []);
  for (const l of merged.values()) {
    if (l.status !== 2 || !String(l.soldDate || "").startsWith(day)) continue;
    const name = [l.firstname, l.lastname].map(x => String(x || "").trim()).filter(Boolean).join(" ");
    // Everyone's, for the Sales sheet's name match (syncSalesLog), which
    // covers Amanda too; never stored or served.
    raw.push({ agentId: l.assignedTo, leadSourceId: l.leadSourceId, household: l.convertedHouseholdId ?? null, name });
    const who = byAz[String(l.assignedTo)];
    if (!who) continue;
    // digest_rows.sold_leads (keep in step): a BOB / Rewrite source or a
    // test lead is not a household sold (Frank, 2026-09-30).
    if (notSale.has(norm(l.leadSourceName)) || isTestLead(l, basis)) continue;
    (per[who] || (per[who] = [])).push({ lead_id: l.id, household: l.convertedHouseholdId ?? null, lead: name,
      existing: existing.has(norm(l.leadSourceName)) });
  }
  const leads = [...merged.values()].sort((a, b) => (a.lastActivityDate < b.lastActivityDate ? 1 : -1));
  const oldest = leads.length ? leads[leads.length - 1].lastActivityDate : null;
  return { per, complete, _raw: raw, _active: { day, newest, leads, complete, oldest } };
}

/* digest_config.is_test_lead (keep in step): an id in TEST_LEAD_IDS, or the
   name matching TEST_LEAD_RE -- both travel in basis.test_lead. */
export function isTestLead(l, basis) {
  const t = basis.test_lead || {};
  if ((t.ids || []).includes(l.id)) return true;
  const name = `${String(l.firstname || "").trim()} ${String(l.lastname || "").trim()}`.trim();
  return !!name && !!t.rx && rxOf(t.rx).test(name);
}

/* What is kept of a lead: what the sold count and the quotes pass read. */
const leadFields = l => ({ id: l.id, lastActivityDate: l.lastActivityDate, enterStageDate: l.enterStageDate,
  assignedTo: l.assignedTo, quoteDate: l.quoteDate, firstname: l.firstname, lastname: l.lastname,
  phone: l.phone, secondaryPhone: l.secondaryPhone, status: l.status, soldDate: l.soldDate,
  leadSourceId: l.leadSourceId, convertedHouseholdId: l.convertedHouseholdId,
  createDate: l.createDate, leadSourceName: l.leadSourceName });

/* ---- task completion ---------------------------------------------------- */

/* az_tasks.audit, line for line (keep in step), on the tasks due today:
   service / renewal / change work left out (a customer record, or the title
   or body patterns), each task credited to the producer assigned it, and a
   task closed without completion either EXCLUDED (the lead was lost as a
   duplicate that day) or EXCUSED (the producer smart-cycled / killed it
   that day and AgencyZoom's "cancel all related open tasks" closed it) --
   task_audit.cancellation_verdicts. The checkpoint's own verdicts come
   first; a task closed since is judged by the same patterns on the lead's
   stage moves, which the quotes pass reads anyway (taskFlags). Refreshed
   every TASKS_REFRESH_SECONDS, not every run: tasks change slowly, and it
   is one list page per producer each time. */
export const TASKS_REFRESH_SECONDS = 330;
const TASK_PAGES = 5;
export function taskFlags(notes, day, basis) {
  const t = basis.tasks;
  if (!t || !t.rx) return null;
  const loss = rxOf(t.rx.loss), dup = rxOf(t.rx.duplicate), cycle = rxOf(t.rx.cycle);
  const firsts = Object.keys(basis.producers || {}).map(n => n.split(" ")[0].toLowerCase());
  let isDup = false; const cycled = new Set();
  for (const n of notes || []) {
    if (!String(n.createDate || "").startsWith(day) || n.type !== "MOVE_STAGE") continue;
    const body = noteText(n.body);
    const g = body.match(loss);
    if (g && dup.test(g[1])) isDup = true;
    if (cycle.test(body)) for (const f of firsts) if (body.toLowerCase().includes(f)) cycled.add(f);
  }
  return isDup || cycled.size ? { dup: isDup, cycled: [...cycled] } : null;
}
async function azTasksDue(env, day, basis, fetchFn) {
  // One producer at a time (assigneeId): the whole-day list's pages overlap
  // and drop tasks (az_client.tasks, 2026-09-29), while one person's day
  // fits on a single page. Pages are 0-indexed. Merged by id.
  const out = new Map();
  let complete = true;
  for (const v of Object.values(basis.producers || {})) {
    let fetched = 0, page = 0;
    for (;;) {
      const j = await azGet(env, "/v1/api/tasks/list", fetchFn, {
        method: "POST", body: JSON.stringify({ startDate: day, endDate: day, assigneeId: v.az_id, page, pageSize: 100 }),
      });
      const batch = j.tasks || j.data || [];
      fetched += batch.length;
      for (const t of batch) if (t && t.id != null && !out.has(t.id)) out.set(t.id, t);
      page++;
      if (!batch.length || (j.totalCount != null ? fetched >= j.totalCount : batch.length < 100)) break;
      if (page >= TASK_PAGES) { complete = false; break; }
    }
  }
  return { tasks: [...out.values()], complete };
}
// Python's round(x, 1): half to even on an exact tie (13 of 16 is 81.25 ->
// 81.2), where Math.round would give 81.3.
const pyRound1 = x => {
  const t = x * 10, f = Math.floor(t);
  if (t - f === 0.5) return (f % 2 === 0 ? f : f + 1) / 10;
  return Number(x.toFixed(1));
};
export function taskCompletion(basis, tasks, flags) {
  const t = basis.tasks || {};
  const title = rxOf(t.rx.title), body = rxOf(t.rx.body);
  const verdicts = t.verdicts || {};
  const customers = new Set((t.customers || []).map(String));
  const byAz = Object.fromEntries(Object.entries(basis.producers || {}).map(([n, v]) => [String(v.az_id), n]));
  const per = Object.fromEntries(Object.keys(basis.producers || {}).map(n => [n,
    { total: 0, completed: 0, closed_not_done: 0, open: 0, excused: 0 }]));
  const rows = [];
  for (const x of tasks) {
    if (String(x.customerType || "").toLowerCase() === "customer") continue;
    if (title.test(x.title || "") || body.test(x.comments || "")) continue;
    const a = (x.assignees || []).find(a => byAz[String(a.id)]);
    const who = a ? byAz[String(a.id)] : null;
    if (!who) continue;
    let v = verdicts[String(x.id)];
    if (!v && x.status === 2 && x.customerId) {
      const f = (flags || {})[String(x.customerId)];
      if (f && f.dup) v = "excluded";
      else if (f && f.cycled.includes(who.split(" ")[0].toLowerCase())) v = "excused";
    }
    if (v === "excluded") continue;
    const p = per[who];
    const state = v === "excused" ? "excused" : x.status === 1 ? "done" : x.status === 2 ? "closed" : "open";
    rows.push({ who, id: x.id, title: x.title, state, record: x.customerName,
      due: String(x.dueDate || "").slice(0, 10), completed: String(x.completeDate || "").slice(0, 10),
      // The checkpoint's corpus says which records are customers (customerType
      // is wrong on a few rows -- task_audit._link); a lead link otherwise.
      lead_id: x.customerId && !customers.has(String(x.customerId)) ? x.customerId : null,
      customer_id: x.customerId && customers.has(String(x.customerId)) ? x.customerId : null });
    if (v === "excused") { p.excused++; continue; }
    p.total++;
    if (x.status === 1) p.completed++;
    else if (x.status === 2) p.closed_not_done++;
    else p.open++;
  }
  for (const p of Object.values(per)) p.pct = p.total ? pyRound1(p.completed / p.total * 100) : null;
  const tot = Object.values(per).reduce((s, p) => s + p.total, 0), done = Object.values(per).reduce((s, p) => s + p.completed, 0);
  return { per, team: { total: tot, completed: done, pct: tot ? pyRound1(done / tot * 100) : null }, rows };
}

/* ---- speed to dial ------------------------------------------------------ */

/* daily.speed_rows + daily.speed_to_dial, line for line (keep in step): an
   internet lead (SureQuote / MAV) created today, the first dial to its
   number, and the seconds between. Worked out whole every refresh from the
   day's kept lead list (every lead created today has activity today) and the
   full call log -- exact, not an estimate. The first dial is taken exactly
   as daily.py takes it (Frank, 2026-09-30): the EARLIEST dial to the number
   by any producer, credited to whoever made it (a tie keeps the one found
   first, in call-log order, as Python's dict order does); the lead's
   createDate (UTC) moved to Arizona before it is compared with the day; and
   both sides keyed by az_corpus.e164, the last ten digits. */
const SPEED_SOURCES = ["surequote", "mav ai", "mav"];
const median = xs => { const v = [...xs].sort((a, b) => a - b), m = v.length >> 1; return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2; };
export function speedToDial(day, basis, leads, recs) {
  const byExt = Object.fromEntries(Object.entries(basis.producers || {}).map(([n, v]) => [String(v.rc_id), n]));
  const dials = new Map();                       // producer -> Map(e164 -> earliest start)
  for (const r of recs) {
    const who = byExt[ownerExt(r)];
    if (!who || r.direction !== "Outbound") continue;
    const num = e164((r.to || {}).phoneNumber);  // day_calls.dials_from's key
    if (!num) continue;
    if (!dials.has(who)) dials.set(who, new Map());
    const m = dials.get(who), t = r.startTime;
    if (!m.has(num) || t < m.get(num)) m.set(num, t);
  }
  const first = new Map();
  for (const [w, m] of dials) for (const [num, t] of m) if (!first.has(num) || t < first.get(num)[1]) first.set(num, [w, t]);
  const rows = [];
  for (const l of leads) {
    const src = String(l.leadSourceName || "").toLowerCase();
    if (!SPEED_SOURCES.some(k => src.includes(k))) continue;
    if (!l.createDate) continue;
    const c = utcMs(l.createDate);
    if (!Number.isFinite(c) || new Date(c - 7 * 3600 * 1000).toISOString().slice(0, 10) !== day) continue;   // Arizona is UTC-7
    const k = e164(l.phone), hit = k ? first.get(k) : null;
    if (!hit) continue;
    const d = Date.parse(hit[1]);
    const secs = (d - c) / 1000;
    if (secs > 0) rows.push({ who: hit[0], lead_id: l.id,
      lead: `${String(l.firstname || "").trim()} ${String(l.lastname || "").trim()}`.trim(),
      source: String(l.leadSourceName || "").trim(),
      arrived: new Date(c).toISOString(), dialled: new Date(d).toISOString(), secs: Math.trunc(secs) });
  }
  const per = {};
  for (const n of Object.keys(basis.producers || {})) {
    const v = rows.filter(r => r.who === n).map(r => r.secs).sort((a, b) => a - b);
    if (v.length) per[n] = { median: Math.trunc(median(v)), n: v.length, quickest: v[0], longest: v[v.length - 1], secs: v };
  }
  const all = rows.map(r => r.secs);
  const summary = all.length ? { per, team: { median: Math.trunc(median(all)), quickest: Math.min(...all),
    longest: Math.max(...all), n: all.length } } : null;
  return { summary, rows };
}

/* ---- the Sales sheet --------------------------------------------------- */

/* sales_log_auto.product_name, line for line (keep in step): the sheet's
   product name for a policy, by carrier id (basis.saleslog.carrier). */
export function productName(p, carriers) {
  const raw = String(p.policyTypeName || "").trim();
  const carrier = (carriers || {})[String(p.carrierId)];
  if (!carrier || !raw) return raw;
  const auto = /auto/i.test(raw);
  if (carrier === "BW") return auto ? "BW-Auto" : `BW-${raw}`;
  if (auto) return `${carrier}-Auto`;
  if (carrier === "Foremost") {
    if (/mobile|manufactured/i.test(raw)) return "Foremost-MH";
    if (/landlord|dp\d|dwelling/i.test(raw)) return "Foremost-Landlord";
    if (/atv|motorcycle|trailer|boat|watercraft|motor home|\brv\b|golf cart|toy/i.test(raw)) return "Foremost-Toys";
    if (/vacant/i.test(raw)) return "Foremost-Vacant";
    if (/home|ho-?\d/i.test(raw)) return "Foremost-Home";
  }
  if (carrier === "Farmers") {
    if (/homeowner|^home$|ho-?\d/i.test(raw)) return "Farmers-Home";
    if (/term|life/i.test(raw)) return "Farmers-Life";
  }
  return `${carrier}-${raw}`;
}
function termOf(eff, exp) {
  const e = String(eff || "").slice(0, 10), x = String(exp || "").slice(0, 10);
  if (!e || !x) return "";
  const days = (Date.parse(x + "T00:00:00Z") - Date.parse(e + "T00:00:00Z")) / 86400000;
  if (!Number.isFinite(days)) return "";
  const months = Math.round(days / 30.44);
  return months > 0 ? `${months}mo` : "";
}

/* sales_log_auto.build_entries: one row per real sale today by a producer
   or Amanda. The name comes from the one lead marked sold today with the
   same agent and lead source, else it stays blank -- the nightly match
   reads the customer record instead, so a name here can be the lead's
   spelling of the same person. */
export function salesLogEntries(day, basis, policies, sourceNames, soldRaw) {
  const sl = basis.saleslog || {};
  const ids = sl.ids || {};
  const notSale = new Set(basis.not_a_sale || []);
  const out = [];
  for (const p of policies) {
    if (!String(p.soldDate || "").startsWith(day)) continue;
    const who = ids[String(p.agentId)];
    if (!who || notSale.has(norm(sourceNames[p.leadSourceId]))) continue;
    const cands = (soldRaw || []).filter(l => String(l.agentId) === String(p.agentId)
      && String(l.leadSourceId) === String(p.leadSourceId));
    const one = cands.length === 1 ? cands[0] : null;
    out.push({
      producer: who,
      client_name: one && one.household != null ? one.name : "",
      az_customer_id: one && one.household != null ? String(one.household) : "",
      lead_source: String(sourceNames[p.leadSourceId] || "").trim(),
      policy_number: String(p.policyNumber || ""),
      product: productName(p, sl.carrier),
      premium: p.premium != null ? Number(p.premium) : null,
      term: termOf(p.effectiveDate, p.expiryDate),
      date_sold: String(p.soldDate || "").slice(0, 10),
      effective_date: String(p.effectiveDate || "").slice(0, 10),
      az_policy_id: p.id,
    });
  }
  return out;
}

/* sales_log_auto.sync_day's rules on saleslog/<day>.json: only ever adds --
   never a policy already on the sheet (az_policy_id), never one a person
   typed by hand (their policy number) -- so the checkpoints and the nightly
   run find it there and skip it. Read right before the write, and written
   only when something is new. */
export async function syncSalesLog(env, day, basis, policies, sourceNames, soldRaw) {
  const cands = salesLogEntries(day, basis, policies, sourceNames, soldRaw);
  if (!cands.length) return 0;
  const key = `saleslog/${day}.json`;
  const doc = (await r2json(env, key)) || { day, entries: [] };
  const have = new Set(doc.entries.filter(e => e.az_policy_id != null).map(e => String(e.az_policy_id)));
  const typed = new Set(doc.entries.filter(e => e.policy_number && e.az_policy_id == null).map(e => e.policy_number));
  let added = 0;
  for (const c of cands) {
    if (c.az_policy_id != null && have.has(String(c.az_policy_id))) continue;
    if (c.policy_number && typed.has(c.policy_number)) continue;
    doc.entries.push({ ...c, id: crypto.randomUUID(), created_at: new Date().toISOString(), day,
      docs_signed: "", review_sent: false, notes: "Auto-added from AgencyZoom", source: "auto" });
    if (c.az_policy_id != null) have.add(String(c.az_policy_id));
    added++;
  }
  if (added) await r2put(env, key, doc);
  return added;
}

/* ONE LIST OF TODAY'S ACTIVE LEADS, NOT TWO (2026-09-29). The sold part
   pages this same list (newest activity first, back to Arizona midnight)
   every even minute, so the quotes pass a minute later uses that copy
   (live/<day>-leads.json) instead of paging it again -- when it is under
   ACTIVE_LIST_FRESH_SECONDS old and reaches back to the checkpoint. A lead
   active in that minute is read on the next pass. */
export const ACTIVE_LIST_FRESH_SECONDS = 150;
export function fromShared(shared, since) {
  if (!shared || !Array.isArray(shared.leads) || !shared.fetched_at) return null;
  if (Date.now() - Date.parse(shared.fetched_at) > ACTIVE_LIST_FRESH_SECONDS * 1000) return null;
  if (!shared.complete && !(shared.oldest && shared.oldest < since)) return null;
  return shared.leads.filter(l => String(l.lastActivityDate || "") >= since);
}
async function azLeadsActiveSince(env, since, fetchFn, shared = null) {
  const reuse = fromShared(shared, since);
  if (reuse) return reuse;
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

// Not found / gone: the lead itself, never the Worker's access (a 403 still
// pauses AgencyZoom, azGet).
const gone = e => e && (e.status === 404 || e.status === 410);

/* `memo` is the previous refresh's per-lead reads (R2), so a lead is only
   re-read when its activity moved; returns the deltas and the new memo. */
export async function quotedLive(env, day, basis, memo, fetchFn = fetch, wanted = [], calls = null, shared = null) {
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
  // A lead dialled since the checkpoint comes first of all: its notes are
  // what judges that dial a contact (live_notes.contactDeltas).
  const want = new Set((wanted || []).map(last10));
  const phones = l => [last10(l.phone), last10(l.secondaryPhone)].filter(Boolean);
  const rank = l => (phones(l).some(p => want.has(p)) ? -1 : String(l.enterStageDate || "") >= q.activity_since ? 0 : producerAz.has(String(l.assignedTo)) ? 1 : 2);
  const presented = b => rx.presented.test(b) && !rx.past.test(b);
  const active = (await azLeadsActiveSince(env, q.activity_since, fetchFn, shared)).sort((a, b) => rank(a) - rank(b));
  for (const l of active) {
    const id = String(l.id), was = prev[id];
    // A read from before contacts and messages were kept is read again.
    if (was && was.act === l.lastActivityDate && was.events) { leads[id] = was; continue; }
    if (notesRead >= NOTES_PER_REFRESH || limited) { pending++; if (was) leads[id] = was; continue; }
    notesRead++;
    let notes;
    try {
      if (notesRead > 1) await pause(LEAD_READ_GAP_MS);
      notes = await azGet(env, `/v1/api/leads/${id}/notes`, fetchFn);
    } catch (e) {
      // A lead AgencyZoom no longer serves (deleted, merged into another
      // record) is read as having no notes, and kept that way until its
      // activity moves: the day's kept list (soldLeadsToday) never drops an
      // id, and one unreadable lead must not stop every other one.
      if (gone(e)) notes = [];
      // Rate limited: keep what this batch read, the rest waits for the next.
      else if (e.status !== 429) throw e;
      else { limited = true; pending++; if (was) leads[id] = was; continue; }
    }
    const ns = Array.isArray(notes) ? notes : [];
    leads[id] = { act: l.lastActivityDate, who: [...quotedBy(l, ns, day, basis, rx)], prem: was ? was.prem : null,
      lead: { firstname: l.firstname, lastname: l.lastname, assignedTo: l.assignedTo, phone: l.phone, secondaryPhone: l.secondaryPhone },
      items: contactItems(ns, day, basis), events: messageEvents(l, ns, day, basis, presented),
      tf: taskFlags(ns, day, basis) };
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
        if (gone(e)) qs = [];
        else if (e.status !== 429) throw e;
        else { limited = true; pending++; continue; }
      }
      const arr = Array.isArray(qs) ? qs : (qs || {}).quotes || [];
      v.prem = arr.reduce((s, x) => s + (Number(x.premium) || 0), 0);
    }
    for (const w of fresh) { per[w].hh++; per[w].pq += v.prem; per[w].new_leads.push(Number(id)); }
  }
  for (const v of Object.values(per)) v.pq = Math.round(v.pq);
  // What each read lead says about a dial to its numbers, for contactDeltas.
  const evidence = {};
  for (const [id, v] of Object.entries(leads)) {
    if (!v.lead) continue;
    for (const p of [last10(v.lead.phone), last10(v.lead.secondaryPhone)].filter(Boolean)) {
      const e = evidence[p] || (evidence[p] = { items: [], leads: [] });
      e.leads.push(Number(id));
      e.items.push(...(v.items || []));
    }
  }
  const task_flags = {};
  for (const [id, v] of Object.entries(leads)) if (v.tf) task_flags[id] = v.tf;
  return { data: { per, pending, looked_at: Object.keys(leads).length }, evidence, task_flags,
    messages: basis.messages ? messageDeltas(basis, Object.fromEntries(Object.entries(leads).filter(([, v]) => v.events)), day, calls || []) : null,
    memo: { checkpoint_since: q.activity_since, leads } };
}

/* ---- the route --------------------------------------------------------- */

const NEEDS = {
  dials: ["RC_CLIENT_ID", "RC_CLIENT_SECRET", "RC_SERVER_URL", "RC_JWT"],
  sales: ["AZ_USERNAME", "AZ_PASSWORD"],
  util: ["INSIGHTFUL_TOKEN"],
  quotes: ["AZ_USERNAME", "AZ_PASSWORD"],
  messages: ["AZ_USERNAME", "AZ_PASSWORD"],
  contacts: ["RC_CLIENT_ID", "RC_CLIENT_SECRET", "RC_SERVER_URL", "RC_JWT"],
  sold: ["AZ_USERNAME", "AZ_PASSWORD"],
  tasks: ["AZ_USERNAME", "AZ_PASSWORD"],
};

const part = async (env, key, fn) => {
  const missing = NEEDS[key].filter(k => !env[k]);
  if (missing.length) return { ok: false, reason: `not connected: Worker secret${missing.length > 1 ? "s" : ""} ${missing.join(", ")} not set` };
  try { return { ok: true, data: await fn() }; }
  catch (e) { return { ok: false, reason: String(e && e.message || e) }; }
};

/* Dials, contacts and talk time, sales (policies and the leads marked
   sold) and utilization: a handful of requests, refreshed together.
   `evidence` is the last quotes pass's read of the lead notes
   (live/<day>-quotes.json). */
export async function computeFast(env, day, basis, fetchFn = fetch, evidence = null, kept = null, taskPrev = null, flags = null) {
  const inputs = {};   // for syncSalesLog; never stored
  let log = null;
  const callLog = async () => (log || (log = rcCallLog(env, day, fetchFn)));
  const [dials, contacts, sales, util, sold] = await Promise.all([
    part(env, "dials", async () => dialDeltas(basis, await callLog())),
    part(env, "contacts", async () => {
      if (!basis.contact || !basis.talk) throw new Error("needs a checkpoint built after this update");
      return contactDeltas(basis, await callLog(), evidence || {});
    }),
    part(env, "sales", async () => {
      const [pols, names] = await Promise.all([azPoliciesSold(env, day, fetchFn), azLeadSources(env, fetchFn)]);
      inputs.policies = pols; inputs.names = names;
      return salesFrom(basis, pols, names);
    }),
    part(env, "util", async () => insightfulUtil(env, day, basis, fetchFn)),
    part(env, "sold", async () => soldLeadsToday(env, day, basis, fetchFn, kept)),
  ]);
  // Task completion: the kept tasks are re-judged every run (a verdict can
  // arrive with the quotes pass), re-fetched only every TASKS_REFRESH_SECONDS.
  let tasks;
  if (!basis.tasks) tasks = { ok: false, reason: "needs a checkpoint built after this update" };
  else {
    const stale = !taskPrev || !taskPrev.fetched_at || Date.now() - Date.parse(taskPrev.fetched_at) > TASKS_REFRESH_SECONDS * 1000;
    const got = stale ? await part(env, "tasks", async () => azTasksDue(env, day, basis, fetchFn))
      : { ok: true, data: { tasks: taskPrev.tasks, complete: taskPrev.complete } };
    if (got.ok && stale) inputs.tasks = { tasks: got.data.tasks, complete: got.data.complete, fetched_at: new Date().toISOString() };
    tasks = !got.ok ? got : !got.data.complete ? { ok: false, reason: "more tasks due today than the page cap" }
      : { ok: true, data: taskCompletion(basis, got.data.tasks, flags) };
  }
  if (sold.ok) {
    inputs.soldRaw = sold.data._raw; delete sold.data._raw;
    inputs.active = { ...sold.data._active, fetched_at: new Date().toISOString() }; delete sold.data._active;
  }
  // Today's dials, for the messages part: a call back answers a lead's text
  // (messages.build reads the same call log).
  let calls = null;
  if (log) try { calls = dialTouches(basis, await log); } catch (_) {}
  // Speed to dial needs every lead created today, so only a complete list.
  const speed = !dials.ok ? { ok: false, reason: dials.reason }
    : !sold.ok ? { ok: false, reason: sold.reason }
    : !(inputs.active || {}).complete ? { ok: false, reason: "today's lead list was cut short" }
    : await part(env, "dials", async () => speedToDial(day, basis, inputs.active.leads, await log));
  return { fetched_at: new Date().toISOString(), dials, contacts, sales, util, sold, speed, tasks, calls, _inputs: inputs };
}

function dialTouches(basis, recs) {
  const byExt = Object.fromEntries(Object.entries(basis.producers || {}).map(([n, v]) => [String(v.rc_id), n]));
  const out = [];
  for (const r of recs) {
    const who = byExt[ownerExt(r)], n = last10((r.to || {}).phoneNumber);
    if (r.direction !== "Outbound" || !who || !n || !r.startTime) continue;
    const at = new Date(Date.parse(r.startTime) - 7 * 3600 * 1000).toISOString().slice(0, 19).replace("T", " ");
    out.push({ n, by: who, at, dur: r.duration || 0 });
  }
  return out;
}

/* Households and premium quoted: one batch of lead reads, carried on from
   the last batch's memo. */
export async function computeQuotes(env, day, basis, memo, fetchFn = fetch, wanted = [], calls = null, shared = null) {
  let next = memo, extra = null;
  const quotes = await part(env, "quotes", async () => {
    const r = await quotedLive(env, day, basis, memo, fetchFn, wanted, calls, shared);
    next = r.memo; extra = r;
    return r.data;
  });
  const messages = !quotes.ok ? { ok: false, reason: quotes.reason }
    : extra.messages ? { ok: true, data: extra.messages }
    : { ok: false, reason: "needs a checkpoint built after this update" };
  return { fetched_at: new Date().toISOString(), quotes, messages, evidence: extra ? extra.evidence : null,
    task_flags: extra ? extra.task_flags : null, memo: next };
}

// Kept for callers/tests that want every part in one go.
export async function computeLive(env, day, basis, fetchFn = fetch, memo = null) {
  const [fast, q] = await Promise.all([computeFast(env, day, basis, fetchFn), computeQuotes(env, day, basis, memo, fetchFn)]);
  const { _inputs, ...rest } = fast;
  return { day, ...rest, quotes: q.quotes, messages: q.messages, _memo: q.memo };
}

const keys = day => ({ fast: `live/${day}.json`, quotes: `live/${day}-quotes.json`, memo: `live/${day}-quote-reads.json`,
  leads: `live/${day}-leads.json`, tasks: `live/${day}-tasks.json` });
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
  const [prev, q, kept, taskPrev] = await Promise.all([r2json(env, k.fast), r2json(env, k.quotes), r2json(env, k.leads), r2json(env, k.tasks)]);
  const evidence = q && q.checkpoint === cp.as_of ? q.evidence : null;
  const flags = q && q.checkpoint === cp.as_of ? q.task_flags : null;
  const { _inputs, ...fast } = await computeFast(env, day, cp.basis, fetch, evidence, kept, taskPrev, flags);
  if (_inputs.tasks) {
    try { await r2put(env, k.tasks, _inputs.tasks); }
    catch (e) { console.log(`tasks not saved: ${e && e.message || e}`); }
  }
  // A live sale goes on the Sales sheet in the same refresh that puts it on
  // the board (Frank, 2026-09-28). Only with this run's own policies and
  // sold leads -- a sold-lead read that failed would leave names blank that
  // it could have filled -- and never at the board's expense.
  if (cp.basis.saleslog && fast.sales.ok && fast.sold.ok && _inputs.policies) {
    try { await syncSalesLog(env, day, cp.basis, _inputs.policies, _inputs.names, _inputs.soldRaw); }
    catch (e) { console.log(`sales sheet sync failed: ${e && e.message || e}`); }
  }
  // Today's active leads, for the quotes pass a minute from now (fromShared).
  // Never at the board's expense: a failed save only means the next refresh
  // pages further back.
  if (_inputs.active) {
    try { await r2put(env, k.leads, _inputs.active); }
    catch (e) { console.log(`kept lead list not saved: ${e && e.message || e}`); }
  }
  const out = keepGood(prev, { checkpoint: cp.as_of, ...fast }, cp, ["dials", "contacts", "sales", "util", "sold", "speed", "tasks"]);
  if (!out.calls && prev && prev.checkpoint === cp.as_of) out.calls = prev.calls;
  // The numbers dialled since the checkpoint, so the next quotes pass reads
  // their leads' notes first.
  out.dialled = (out.contacts || {}).ok
    ? [...new Set(Object.values(out.contacts.data).flatMap(v => v.dialled || []))]
    : (prev && prev.checkpoint === cp.as_of ? prev.dialled || [] : []);
  await r2put(env, k.fast, out);
  return out;
}
async function refreshQuotes(env, day, cp) {
  const k = keys(day);
  const [prev, memoIn, fast, shared] = await Promise.all([r2json(env, k.quotes), r2json(env, k.memo), r2json(env, k.fast), r2json(env, k.leads)]);
  const same = fast && fast.checkpoint === cp.as_of;
  const { memo, ...res } = await computeQuotes(env, day, cp.basis, memoIn, fetch,
    same ? fast.dialled || [] : [], same ? fast.calls || [] : [], shared);
  const out = keepGood(prev, { checkpoint: cp.as_of, ...res }, cp, ["quotes", "messages"]);
  if (!(res.quotes || {}).ok && prev && prev.checkpoint === cp.as_of) { out.evidence = prev.evidence; out.task_flags = prev.task_flags; }
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
  await flushAzLog(env, day);
  return jsonResp({ live: true, day, checkpoint: cp.as_of, fetched_at: f.fetched_at,
    dials: f.dials, contacts: f.contacts, sales: f.sales, util: f.util, sold: f.sold, speed: f.speed, tasks: f.tasks,
    quotes: q.quotes, messages: q.messages, quotes_fetched_at: q.fetched_at }, 200);
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
  try {
    if (minute % 2 === 0) await refreshFast(env, day, cp);
    else await refreshQuotes(env, day, cp);
  } finally { await flushAzLog(env, day); }
}

function jsonResp(body, status) {
  return new Response(JSON.stringify(body), {
    status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}
