// Apollo's chat handler (coeus.js) end to end with the model stubbed: the
// question is set up (the system block, the context block, the messages)
// and the answer streams back. Run: node --test site/coeus.test.mjs
//
// Written 2026-10-13 after every question had failed since 10-06 on a bare
// Cloudflare 500: contextBlock used a variable the time-zone change had
// removed, which nothing ran before a deploy. This loads the module the
// way the Worker does (the .md files as text) and asks it one question.
import { register } from "node:module";
import { pathToFileURL } from "node:url";
import test from "node:test";
import assert from "node:assert/strict";

// Wrangler's text rule for the coaching documents, for node.
register("data:text/javascript," + encodeURIComponent(`
export async function load(url, context, next) {
  if (url.endsWith(".md")) {
    const { readFileSync } = await import("node:fs");
    const text = readFileSync(new URL(url), "utf8");
    return { format: "module", shortCircuit: true, source: "export default " + JSON.stringify(text) + ";" };
  }
  return next(url, context);
}`), pathToFileURL("./"));

const { coeusChat } = await import("./coeus.js");

function sse(events) {
  return new Response(events.map((e) => `data: ${JSON.stringify(e)}\n`).join("\n") + "\n",
    { status: 200, headers: { "content-type": "text/event-stream" } });
}
const env = { ANTHROPIC_API_KEY: "test", BOARD: { get: async () => null, put: async () => null, list: async () => ({ objects: [] }) } };
const deps = {
  identityOf: () => ({ name: "Mike", email: "mike@example.com", all: false }),
  rpScope: () => ({ all: false, producer: "Mike Olvera" }),
  rpMaySee: () => true,
  commercialAllowed: () => false,
};
const ctx = { waitUntil: (p) => { ctx.pending = p; } };

async function ask(text, onFetch) {
  const calls = [];
  globalThis.fetch = async (url, init) => { calls.push({ url, body: JSON.parse(init.body) }); return onFetch(calls.length); };
  const request = new Request("https://board.test/api/coeus", { method: "POST", body: JSON.stringify({
    messages: [{ role: "user", content: text }], context: { page: "Digest", day: "2026-10-12", producer: "Mike Olvera" } }) });
  const res = await coeusChat(request, env, ctx, deps);
  const body = await res.text();
  if (ctx.pending) await ctx.pending;
  return { res, body, calls };
}

test("a question is set up and answered", async () => {
  const { res, body, calls } = await ask("how did I do yesterday?", () => sse([
    { type: "message_start", message: { usage: { input_tokens: 10, output_tokens: 0 } } },
    { type: "content_block_start", index: 0, content_block: { type: "text", text: "" } },
    { type: "content_block_delta", index: 0, delta: { type: "text_delta", text: "You made 40 dials." } },
    { type: "message_delta", delta: { stop_reason: "end_turn" }, usage: { output_tokens: 5 } },
  ]));
  assert.equal(res.status, 200, body);
  assert.match(body, /You made 40 dials\./);
  assert.match(body, /"done":true/);
  assert.doesNotMatch(body, /"error"/);
  const sys = calls[0].body.system.map((b) => b.text).join("\n");
  assert.match(sys, /# Apollo/);
  assert.match(sys, /Today is (Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday) \d{4}-\d{2}-\d{2}, \d{2}:\d{2}/);
  assert.match(sys, /Asking: Mike \(mike@example.com\), a producer \(Mike Olvera\)/);
  assert.match(sys, /looking at the Digest page for 2026-10-12 filtered to Mike Olvera/);
  assert.equal(calls[0].body.messages[0].content, "how did I do yesterday?");
});

test("a fault before the stream is a JSON error, not a bare 500", async () => {
  const bad = { ...deps, rpScope: () => { throw new Error("no scope today"); } };
  const request = new Request("https://board.test/api/coeus", { method: "POST", body: JSON.stringify({ messages: [{ role: "user", content: "hi" }] }) });
  const res = await coeusChat(request, env, ctx, bad);
  assert.equal(res.status, 500);
  assert.match((await res.json()).error, /no scope today/);
});

test("the model refusing is reported on the stream", async () => {
  const { res, body } = await ask("anything", () => new Response("prompt too long", { status: 400 }));
  assert.equal(res.status, 200);
  assert.match(body, /"error":"Claude API 400: prompt too long"/);
});
