// node --test proxy/server.test.mjs -- the proxy against a fake AgencyZoom.
import { test } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const KEY = "test-key-0123456789abcdefghijklmnop";

function fakeUpstream() {
  const seen = [];
  const srv = http.createServer((req, res) => {
    let body = "";
    req.on("data", c => body += c);
    req.on("end", () => {
      seen.push({ method: req.method, url: req.url, auth: req.headers.authorization, ua: req.headers["user-agent"], key: req.headers["x-pantheon-key"], body });
      if (req.url.startsWith("/v1/api/refuse")) {
        res.writeHead(403, { "content-type": "text/html", server: "cloudflare", "retry-after": "7" });
        return res.end("<html>403 Forbidden</html>");
      }
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ echo: req.url, body: body ? JSON.parse(body) : null }));
    });
  });
  return new Promise(r => srv.listen(0, () => r({ srv, seen, port: srv.address().port })));
}

function startProxy(upstreamPort) {
  return new Promise((resolve, reject) => {
    const p = spawn(process.execPath, [path.join(HERE, "server.js")], {
      env: { ...process.env, PORT: "0", PROXY_KEY: KEY, UPSTREAM: `http://127.0.0.1:${upstreamPort}` },
      stdio: ["ignore", "pipe", "pipe"],
    });
    let out = "";
    p.stdout.on("data", c => { out += c; const m = out.match(/on :(\d+)/); if (m) resolve({ p, port: Number(m[1]) }); });
    p.stderr.on("data", c => process.stderr.write(c));
    p.on("exit", code => reject(new Error(`proxy exited ${code}`)));
  });
}

// PORT=0 asks for any free port; server.js prints the one it got.
test("forwards API calls verbatim, refuses everything else", async () => {
  const up = await fakeUpstream();
  const px = await startProxy(up.port);
  try {
    const base = `http://127.0.0.1:${px.port}`;
    // no key -> 401, nothing reaches AgencyZoom
    let r = await fetch(`${base}/v1/api/leads/list`, { method: "POST", body: "{}" });
    assert.equal(r.status, 401);
    assert.equal(up.seen.length, 0);
    // a POST with the token and a body goes through as it came
    r = await fetch(`${base}/v1/api/leads/list?x=1`, {
      method: "POST", headers: { "x-pantheon-key": KEY, authorization: "Bearer tok", "content-type": "application/json" },
      body: JSON.stringify({ page: 2 }),
    });
    assert.equal(r.status, 200);
    assert.deepEqual(await r.json(), { echo: "/v1/api/leads/list?x=1", body: { page: 2 } });
    assert.equal(up.seen[0].auth, "Bearer tok");
    assert.equal(up.seen[0].key, undefined, "the proxy key never reaches AgencyZoom");
    assert.match(up.seen[0].ua, /PantheonProxy/);
    // a refusal comes back as it was, status and headers, so the Worker pauses as before
    r = await fetch(`${base}/v1/api/refuse`, { headers: { "x-pantheon-key": KEY } });
    assert.equal(r.status, 403);
    assert.equal(r.headers.get("server"), "cloudflare");
    assert.equal(r.headers.get("retry-after"), "7");
    assert.match(await r.text(), /403 Forbidden/);
    // outside /v1/api/ -> 404; a method we never use -> 405
    r = await fetch(`${base}/admin`, { headers: { "x-pantheon-key": KEY } });
    assert.equal(r.status, 404);
    r = await fetch(`${base}/v1/api/leads/1`, { method: "DELETE", headers: { "x-pantheon-key": KEY } });
    assert.equal(r.status, 405);
    assert.equal(up.seen.length, 2);
    // health
    r = await fetch(`${base}/healthz`, { headers: { "x-pantheon-key": KEY } });
    assert.equal(r.status, 200);
    assert.equal((await r.json()).upstream, `http://127.0.0.1:${up.port}`);
  } finally {
    px.p.kill();
    up.srv.close();
  }
});
