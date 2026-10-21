/* Demo mode (site/demo.js) over a made-up document: every customer masked
 * the same way everywhere, numbers to 555, staff and figures untouched, the
 * blocked and skipped routes right. `node --test site/demo.test.mjs`. */
import test from "node:test";
import assert from "node:assert/strict";
import { demoize, demoResponse, demoOn, blockedInDemo, skipInDemo, DEMO_COOKIE } from "./demo.js";
import { PEOPLE } from "./staff.js";

const producer = PEOPLE.find((p) => p.producer).name;          // a real staff name: never masked
const first = producer.split(" ")[0];
const ops = PEOPLE.find((p) => (p.board || []).includes("demo")); // a login that may switch it on

const doc = () => ({
  date: "2026-10-19",
  producers: [{ name: producer, dials: 41, ps: 1673 }],
  rows: {
    dials: [{ who: producer, lead: "Jose Lugo", lead_id: 123, last4: "6995", talk: 620 },
            { who: producer, lead: "Jill Shubert", lead_id: 124, last4: "1234", talk: 0 }],
    sold: [{ who: producer, product: "Farmers-Auto", policy: "552768155", premium: 1673 }],
    tasks: [{ who: producer, record: "Celerino A. Gallardo, L.L.C.", title: "Call back" }, { who: producer, record: "997 LLC" }],
  },
  calls: [{
    lead: "Jose Lugo", who: producer, dur: "2m 38s",
    transcript: `[outbound call, 2m38s]\n[0:02] ${first} (producer): Hi, Jose. This is ${first} with Farmers.\n[0:08] Jose (lead): Hi. Call me back at (928) 726-7222 or jose.lugo@gmail.com.`,
    turns: [{ t: 2.6, who: `${first} (producer)`, text: `Hi, Jose. This is ${first} with Farmers.`, w: [2.5, 3], r: 0 },
            { t: 8.1, who: "Jose (lead)", text: "JOSE LUGO speaking. Jill's sister is here too.", r: 0 }],
    summary: `${first} dialled Jose Lugo to follow up. Jose's wife answered.`,
    good: [["Asked for Jose Lugo by name", "Opened with 'Hi, Jose'"]],
  }],
  messages: { replies: [{ who: producer, lead: "Jill Shubert", said: "Stop", number: "+19287267222" }] },
  live_basis: { messages: { people: { "+19287267222": { name: "Jill Shubert", owner: producer } } },
                talk: { [producer]: { seconds: 575, numbers: ["+19287267222", "+526535380676"] } } },
  service: { callbacks: [{ name: "El Centro    Ca - 17609701372", number: "7609701372", by: producer }] },
});

test("a customer is made up the same way everywhere, and the staff and figures are not", () => {
  const d = demoize(doc());
  const lead = d.rows.dials[0].lead;
  assert.notEqual(lead, "Jose Lugo");
  assert.match(lead, /^[A-Z][a-z]+ [A-Z][a-z]+$/);
  assert.equal(d.calls[0].lead, lead);                     // the card's lead
  assert.ok(d.calls[0].summary.includes(lead));            // the summary's full name
  assert.ok(d.calls[0].good[0][0].includes(lead));
  const fakeFirst = lead.split(" ")[0];
  assert.equal(d.calls[0].turns[1].who, `${fakeFirst} (lead)`);          // the speaker label
  assert.ok(d.calls[0].transcript.includes(`Hi, ${fakeFirst}. This is ${first} with Farmers.`));  // the bare first name; the producer kept
  assert.ok(d.calls[0].summary.includes(`${fakeFirst}'s wife`));         // a possessive
  assert.ok(d.calls[0].turns[1].text.startsWith(lead.toUpperCase() + " speaking"));   // ALL CAPS kept
  assert.equal(d.producers[0].name, producer);
  assert.equal(d.producers[0].dials, 41);
  assert.equal(d.rows.sold[0].premium, 1673);
  assert.equal(d.rows.sold[0].policy, "552768155");
  assert.equal(d.calls[0].turns[0].w[0], 2.5);
  assert.ok(!JSON.stringify(d).includes("Lugo"));
  assert.ok(!JSON.stringify(d).includes("Shubert"));
  assert.ok(!JSON.stringify(d).includes("Jill"));
  // the same real name gives the same made-up one on another document
  assert.equal(demoize({ rows: { dials: [{ lead: "Jose Lugo" }] } }).rows.dials[0].lead, lead);
});

test("phone numbers keep their area code and shape, become 555 numbers, and keys move with them", () => {
  const d = demoize(doc());
  assert.match(d.calls[0].transcript, /\(928\) 555-\d{4}/);
  assert.ok(!d.calls[0].transcript.includes("726-7222"));
  const key = Object.keys(d.live_basis.messages.people)[0];
  assert.match(key, /^\+1928555\d{4}$/);
  assert.equal(d.messages.replies[0].number, key);           // a value and a key on the same number agree
  assert.equal(d.live_basis.talk[producer].numbers[0], key);
  assert.match(d.live_basis.talk[producer].numbers[1], /^\+52653555\d{4}$/);
  assert.match(d.service.callbacks[0].number, /^760555\d{4}$/);
  assert.notEqual(d.rows.dials[0].last4, "6995");
  assert.match(d.rows.dials[0].last4, /^\d{4}$/);
  assert.ok(d.calls[0].transcript.includes("@example.com"));
  assert.ok(!d.calls[0].transcript.includes("gmail"));
});

test("a business or an odd caller string is made up whole", () => {
  const d = demoize(doc());
  assert.ok(!d.rows.tasks[0].record.includes("Gallardo"));
  assert.ok(d.rows.tasks[0].record.endsWith(" L.L.C."));
  assert.ok(!d.rows.tasks[1].record.includes("997"));
  assert.ok(!d.service.callbacks[0].name.includes("Centro"));
  assert.ok(!d.service.callbacks[0].name.includes("1760"));
});

test("a made-up name never lands on a real one from the same document", () => {
  // every pairing of these first and last names; whichever the hash picks for one must not be another row's real name
  const names = [];
  for (const f of ["Mateo", "Sofia", "Daniel", "Valeria", "Lucas", "Camila"]) for (const l of ["Reyes", "Navarro", "Castillo", "Herrera", "Delgado"]) names.push(`${f} ${l}`);
  const d = demoize({ rows: { dials: names.map((lead) => ({ lead })) } });
  const real = new Set(names);
  for (const r of d.rows.dials) assert.ok(!real.has(r.lead), `${r.lead} is a real name on the document`);
});

test("the switch: the cookie, from a login that may; the routes it refuses and the ones it leaves alone", () => {
  const req = (cookie) => new Request("https://x/api/days", { headers: cookie ? { Cookie: cookie } : {} });
  assert.equal(demoOn(req(`${DEMO_COOKIE}=1`), ops.email), true);
  assert.equal(demoOn(req(`a=b; ${DEMO_COOKIE}=1`), ops.email), true);
  assert.equal(demoOn(req(`${DEMO_COOKIE}=0`), ops.email), false);
  assert.equal(demoOn(req(""), ops.email), false);
  const producerEmail = PEOPLE.find((p) => p.producer && p.email).email;
  assert.equal(demoOn(req(`${DEMO_COOKIE}=1`), producerEmail), false);
  for (const path of ["crm/lookups", "scrub", "hygiene", "campaigns", "cardreview/2026-10-19", "folio-goals/2026-10-31", "commission/2026-10-31", "coeus/usage"]) {
    assert.equal(blockedInDemo(["api", ...path.split("/")]), true, path);
  }
  for (const path of ["days/2026-10-19", "rotation", "service/2026-10-19", "commercial/2026-10-19", "renewals", "leads", "saleslog/2026-10-19", "coeus", "cardnotes", "editions/2026-10-19", "recordings/2026-10-19/abc"]) {
    assert.equal(blockedInDemo(["api", ...path.split("/")]), false, path);
  }
  for (const path of ["me", "prefs", "training", "leadsources", "roleplay/sessions", "saleslog/options"]) assert.equal(skipInDemo(["api", ...path.split("/")]), true, path);
  for (const path of ["days/2026-10-19", "saleslog/2026-10-19", "leads"]) assert.equal(skipInDemo(["api", ...path.split("/")]), false, path);
});

test("a JSON answer is masked and marked; audio and errors pass as they are", async () => {
  const json = new Response(JSON.stringify({ rows: { dials: [{ lead: "Jose Lugo" }] } }), { headers: { "content-type": "application/json; charset=utf-8" } });
  const out = await demoResponse(json);
  assert.equal(out.headers.get("x-pantheon-demo"), "1");
  assert.equal(out.headers.get("cache-control"), "no-store");
  assert.notEqual((await out.json()).rows.dials[0].lead, "Jose Lugo");
  const audio = new Response("mp3", { headers: { "content-type": "audio/mpeg" } });
  assert.equal(await demoResponse(audio), audio);
  const err = new Response(JSON.stringify({ error: "no" }), { status: 404, headers: { "content-type": "application/json" } });
  assert.equal(await demoResponse(err), err);
});
