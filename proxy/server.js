#!/usr/bin/env node
/* Pantheon's AgencyZoom proxy -- a dedicated address for the board's reads.

   WHY (2026-10-13). The board's Worker (site/live.js) reads AgencyZoom
   every couple of minutes through api.agencyzoom.com, and every Cloudflare
   Worker in a region leaves through a handful of shared outbound addresses
   (ours: 2a06:98c0:3600::103). AgencyZoom's firewall judges that address,
   not our account: on 10-01, 10-06, 10-07 and 10-12 it refused the Worker
   with bare 403s for the afternoon, and on 10-13 from the first request of
   the day, the login included -- while the same login and token answered
   200 from anywhere else. Frank, 2026-10-13: "start on the proxy".

   WHAT. One small Node process on a machine with an address of its own (a
   $5 VPS; proxy/README.md). The Worker sends its AgencyZoom calls here
   instead (AZ_PROXY_URL + AZ_PROXY_KEY in the Worker's secrets; live.js
   azBase), and this forwards each one to api.agencyzoom.com unchanged --
   method, path, query, body, the Authorization header -- and hands the
   answer back verbatim, 403s and 429s included, so the Worker's own pacing
   and pausing keep working exactly as before. AgencyZoom then sees ONE
   address that is ours alone.

   WHAT IT WILL NOT DO. Nothing without the shared key (x-pantheon-key).
   Nothing outside /v1/api/. No method but GET and POST. It never logs a
   body or a token: one line per request -- time, method, path, status,
   milliseconds. No dependencies, Node 18+.

   RUN.   PROXY_KEY=<long random string> PORT=8787 node proxy/server.js
   CHECK. curl -H "x-pantheon-key: $PROXY_KEY" http://localhost:8787/healthz
          -> {"ok":true,"upstream":"https://api.agencyzoom.com","egress":"<this machine's address>"}
   UPSTREAM overrides the target (the test points it at a local server). */
"use strict";
const http = require("http");

const PORT = Number(process.env.PORT || 8787);
const KEY = process.env.PROXY_KEY || "";
const UPSTREAM = (process.env.UPSTREAM || "https://api.agencyzoom.com").replace(/\/$/, "");
const UA = process.env.PROXY_UA || "PantheonProxy/1.0 (+frank@floresinsuranceagency.com)";
const MAX_BODY = 1 << 20;                                   // 1 MB: a lead-list page is ~100 KB
const FORWARD = ["authorization", "content-type", "accept"];  // request headers that go through
const RETURN = ["content-type", "retry-after", "server", "date", "via", "x-amzn-requestid",
  "x-amzn-errortype", "x-amz-cf-id", "x-cache", "www-authenticate", "cf-ray"];

if (!KEY || KEY.length < 24) {
  console.error("PROXY_KEY must be set to a long random string (24+ characters)");
  process.exit(2);
}

let egressCache = { at: 0, ip: null };
async function egress() {
  if (Date.now() - egressCache.at < 6 * 3600 * 1000 && egressCache.ip) return egressCache.ip;
  try {
    const t = await (await fetch("https://cloudflare.com/cdn-cgi/trace")).text();
    const ip = Object.fromEntries(t.trim().split("\n").map(l => l.split("="))).ip || null;
    egressCache = { at: Date.now(), ip };
  } catch (_) { egressCache = { at: Date.now(), ip: egressCache.ip }; }
  return egressCache.ip;
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = []; let size = 0;
    req.on("data", c => { size += c.length; if (size > MAX_BODY) { reject(new Error("body too large")); req.destroy(); } else chunks.push(c); });
    req.on("end", () => resolve(Buffer.concat(chunks)));
    req.on("error", reject);
  });
}

function reply(res, status, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(status, { "content-type": "application/json", "content-length": Buffer.byteLength(body) });
  res.end(body);
}

const server = http.createServer(async (req, res) => {
  const t0 = Date.now();
  const url = new URL(req.url, "http://proxy");
  const log = (status, note = "") =>
    console.log(`${new Date().toISOString()} ${req.method} ${url.pathname} ${status} ${Date.now() - t0}ms${note ? " " + note : ""}`);
  if (req.headers["x-pantheon-key"] !== KEY) { log(401, "bad key"); return reply(res, 401, { error: "no" }); }
  if (url.pathname === "/healthz") { log(200); return reply(res, 200, { ok: true, upstream: UPSTREAM, egress: await egress() }); }
  if (!url.pathname.startsWith("/v1/api/") || url.pathname.includes("..")) { log(404); return reply(res, 404, { error: "not an API path" }); }
  if (req.method !== "GET" && req.method !== "POST") { log(405); return reply(res, 405, { error: "GET or POST" }); }
  let body;
  try { body = await readBody(req); } catch (e) { log(413, e.message); return reply(res, 413, { error: e.message }); }
  const headers = { "user-agent": UA };
  for (const h of FORWARD) if (req.headers[h]) headers[h] = req.headers[h];
  let up;
  try {
    up = await fetch(UPSTREAM + url.pathname + url.search, {
      method: req.method, headers, body: req.method === "POST" ? body : undefined,
      redirect: "manual", signal: AbortSignal.timeout(60_000),
    });
  } catch (e) { log(502, e.name); return reply(res, 502, { error: `upstream: ${e.name}` }); }
  const out = {};
  for (const h of RETURN) { const v = up.headers.get(h); if (v) out[h] = v; }
  const buf = Buffer.from(await up.arrayBuffer());
  out["content-length"] = buf.length;
  res.writeHead(up.status, out);
  res.end(buf);
  log(up.status);
});

server.listen(PORT, () => console.log(`pantheon az proxy on :${server.address().port} -> ${UPSTREAM}`));
module.exports = server;
