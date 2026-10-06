// Pantheon's CRM data layer against a real SQLite (node:sqlite, Node 22+)
// dressed as a D1 binding. Run: node --test site/crm.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { DatabaseSync } from "node:sqlite";
import { crm, phoneKey, checkValue, nextDay, OBJECTS } from "./crm.js";
import STAFF from "./staff_data.js";

/* ---- a D1 shim: prepare().bind().first()/all()/run(), batch() ---------------- */
function d1(db) {
  const stmt = (sql, args = []) => ({
    bind: (...a) => stmt(sql, a),
    first: async (col) => { const r = db.prepare(sql).get(...args) || null; return col && r ? r[col] : r; },
    all: async () => ({ results: db.prepare(sql).all(...args), success: true }),
    run: async () => { const r = db.prepare(sql).run(...args); return { success: true, meta: { changes: r.changes, last_row_id: Number(r.lastInsertRowid) } }; },
  });
  // batch() must give .results for a SELECT and run a write: .all() does both in node:sqlite.
  return { prepare: (sql) => stmt(sql), batch: async (stmts) => { const out = []; for (const s of stmts) out.push(await s.all()); return out; } };
}
function fresh() {
  const db = new DatabaseSync(":memory:");
  db.exec(readFileSync(new URL("./crm/migrations/0001_init.sql", import.meta.url), "utf8"));
  db.exec(`INSERT INTO lead_sources (id, name) VALUES (1, 'Facebook'), (2, 'Home no Auto');
    INSERT INTO workflows (id, name, kind) VALUES (10, '1 Pipeline', 'sales'), (20, 'Service Pipeline', 'service');
    INSERT INTO stages (id, workflow_id, name, ord) VALUES (101, 10, 'New', 1), (102, 10, 'Contacted, In Progress', 2), (103, 10, 'Quotes Presented', 3), (201, 20, 'New', 1);
    INSERT INTO resolutions (id, name) VALUES (32571, 'Completed'), (32574, 'Renewed: Accepted as is');
    INSERT INTO carriers (id, name, short) VALUES (484668, 'Farmers Insurance', 'Farmers');`);
  return { raw: db, env: { CRM: d1(db) } };
}
const FRANK = STAFF.people.find((p) => p.name.startsWith("Frank"));
const CRYSTAL = STAFF.people.find((p) => p.name.startsWith("Crystal"));
const who = { email: FRANK.email };
const identityOf = (req) => ({ email: req.headers.get("x-test-email") || who.email });
async function call(env, method, path, body, email) {
  const url = new URL("https://board.test" + path);
  const req = new Request(url, { method, body: body ? JSON.stringify(body) : undefined,
    headers: { "content-type": "application/json", "x-test-email": email || who.email } });
  const parts = url.pathname.split("/").filter(Boolean).slice(2);
  const res = await crm(req, env, identityOf, parts, url);
  return { status: res.status, body: await res.json() };
}

test("values: phone keys and field types", () => {
  assert.equal(phoneKey("(928) 726-0300"), "+19287260300");
  assert.equal(phoneKey("+526535380676"), "+16535380676");   // last ten digits, like az_corpus.e164
  assert.equal(phoneKey("12345"), null);
  assert.deepEqual(checkValue("datetime", "2026-10-06"), [true, "2026-10-06 00:00:00"]);
  assert.deepEqual(checkValue("datetime", "2026-10-06T09:15"), [true, "2026-10-06 09:15:00"]);
  assert.equal(checkValue("date", "10/06/2026")[0], false);
  assert.equal(checkValue("int", "12")[1], 12);
  assert.equal(checkValue("int", "1.5")[0], false);
  assert.equal(checkValue("enum:a|b", "c")[0], false);
  assert.equal(nextDay("2026-12-31"), "2027-01-01");
  for (const spec of Object.values(OBJECTS)) for (const k of [...spec.create, ...spec.edit, ...spec.required]) assert.ok(spec.fields[k], `${spec.table}.${k}`);
});

test("gate: outsiders 403, no binding 503", async () => {
  const { env } = fresh();
  assert.equal((await call(env, "GET", "/api/crm/lookups", null, "nobody@example.com")).status, 403);
  assert.equal((await call({}, "GET", "/api/crm/lookups")).status, 503);
});

test("lookups carry staff.json's people as employees", async () => {
  const { env } = fresh();
  const r = await call(env, "GET", "/api/crm/lookups");
  assert.equal(r.status, 200);
  assert.equal(r.body.workflows.find((w) => w.id === 10).stages.length, 3);
  assert.ok(r.body.employees.some((e) => e.id === CRYSTAL.az_id && e.producer));
});

test("a lead's life: create, note, quote, move, sold, policy -- AgencyZoom-shaped", async () => {
  const { env, raw } = fresh();
  let r = await call(env, "POST", "/api/crm/leads", { firstname: "Maria", lastname: "Ortiz", phone: "(602) 555-0101",
    assignedTo: CRYSTAL.az_id, leadSourceId: 1, workflowStageId: 101 }, CRYSTAL.email);
  assert.equal(r.status, 200, JSON.stringify(r.body));
  const lead = r.body;
  assert.equal(lead.status, 0);
  assert.equal(lead.leadSourceName, "Facebook");
  assert.equal(lead.workflowId, 10);
  assert.equal(lead.workflowStageName, "New");
  assert.equal(lead.assignedToName, CRYSTAL.name);
  assert.match(lead.createDate, /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/);

  // required and unknown fields are refused
  assert.equal((await call(env, "POST", "/api/crm/leads", { firstname: "x" })).status, 400);
  assert.equal((await call(env, "POST", "/api/crm/leads", { lastname: "x", status: 2 })).status, 400);
  assert.equal((await call(env, "POST", `/api/crm/leads/${lead.id}`, { soldDate: "2026-10-06" })).status, 400);

  // search by the number as RingCentral gives it
  r = await call(env, "GET", "/api/crm/search?phone=%2B16025550101");
  assert.equal(r.body.leads.length, 1);
  assert.equal(r.body.key, "+16025550101");

  // a CALL note, then the list reads newest first
  r = await call(env, "POST", `/api/crm/leads/${lead.id}/notes`, { type: "CALL", body: "Reached, quoting auto", attr: { outbound: true } }, CRYSTAL.email);
  assert.equal(r.status, 201);
  assert.equal(r.body.createdByName, CRYSTAL.name);
  assert.equal((await call(env, "POST", `/api/crm/leads/${lead.id}/notes`, { type: "BOGUS", body: "x" })).status, 400);

  // the move writes the MOVE_STAGE note the pipeline reads
  r = await call(env, "POST", `/api/crm/leads/${lead.id}/move`, { to: "1 Pipeline | Contacted, In Progress" }, CRYSTAL.email);
  assert.equal(r.status, 200, JSON.stringify(r.body));
  assert.equal(r.body.workflowStageId, 102);
  assert.equal((await call(env, "POST", `/api/crm/leads/${lead.id}/move`, { to: "1 Pipeline | Contacted, In Progress" })).status, 409);
  assert.equal((await call(env, "POST", `/api/crm/leads/${lead.id}/move`, { to: "Nowhere" })).status, 400);
  r = await call(env, "GET", `/api/crm/leads/${lead.id}/notes`);
  assert.equal(r.body[0].type, "MOVE_STAGE");
  assert.equal(r.body[0].body, `Lead Maria Ortiz moved from 1 Pipeline | New to 1 Pipeline | Contacted, In Progress by ${CRYSTAL.name}`);
  assert.equal(r.body[1].type, "CALL");

  // a quote stamps the lead's quoteDate once
  r = await call(env, "POST", `/api/crm/leads/${lead.id}/quotes`, { policyTypeName: "Auto", premium: 1234.5, carrierId: 484668 }, CRYSTAL.email);
  assert.equal(r.status, 200, JSON.stringify(r.body));
  assert.equal(r.body.leadId, lead.id);
  r = await call(env, "GET", `/api/crm/leads/${lead.id}`);
  assert.ok(r.body.quoteDate);
  const firstQuote = r.body.quoteDate;
  await call(env, "POST", `/api/crm/leads/${lead.id}/quotes`, { policyTypeName: "Home", premium: 900 });
  assert.equal((await call(env, "GET", `/api/crm/leads/${lead.id}`)).body.quoteDate, firstQuote);
  assert.equal((await call(env, "GET", `/api/crm/leads/${lead.id}/quotes`)).body.quotes.length, 2);

  // sold: status 2, a soldDate, a household made from the lead
  r = await call(env, "POST", `/api/crm/leads/${lead.id}/sold`, {}, CRYSTAL.email);
  assert.equal(r.status, 200, JSON.stringify(r.body));
  assert.equal(r.body.status, 2);
  assert.ok(r.body.soldDate);
  assert.ok(r.body.convertedHouseholdId);
  assert.equal((await call(env, "POST", `/api/crm/leads/${lead.id}/sold`, {})).status, 409);
  const hh = (await call(env, "GET", `/api/crm/households/${r.body.convertedHouseholdId}`)).body;
  assert.equal(hh.name, "Maria Ortiz");
  assert.equal(hh.phone, "(602) 555-0101");

  // the policy, by agentId + soldDate, as is_real_sale reads it
  r = await call(env, "POST", "/api/crm/policies", { householdId: hh.id, leadId: lead.id, agentId: CRYSTAL.az_id, leadSourceId: 1,
    carrierId: 484668, policyTypeName: "Auto", policyNumber: "A1", premium: 1234.5, term: 6, effectiveDate: "2026-10-07", soldDate: "2026-10-06" }, CRYSTAL.email);
  assert.equal(r.status, 200, JSON.stringify(r.body));
  assert.equal(r.body.carrierName, "Farmers Insurance");
  assert.equal(r.body.agentName, CRYSTAL.name);
  r = await call(env, "GET", `/api/crm/policies?agentId=${CRYSTAL.az_id}&soldFrom=2026-10-06&soldTo=2026-10-06`);
  assert.equal(r.body.policies.length, 1);
  assert.equal(r.body.totalCount, 1);
  assert.equal((await call(env, "GET", `/api/crm/policies?agentId=${FRANK.az_id}`)).body.policies.length, 0);

  // a premium change is an update with an audit event
  r = await call(env, "POST", `/api/crm/policies/${r.body.policies[0].id}`, { premium: 1300 });
  assert.equal(r.body.premium, 1300);
  const ev = (await call(env, "GET", `/api/crm/events?object=policy&id=${r.body.id}`)).body;
  assert.equal(ev[0].action, "update");
  assert.deepEqual(ev[0].before, { premium: 1234.5 });
  assert.deepEqual(ev[0].after, { premium: 1300 });
  assert.equal(ev[0].who, FRANK.email);
  assert.equal(raw.prepare("SELECT count(*) AS n FROM stage_moves").get().n, 2);
});

test("tasks: due today per assignee, complete leaves a TASK note", async () => {
  const { env } = fresh();
  const lead = (await call(env, "POST", "/api/crm/leads", { lastname: "Lopez", phone: "6025550102", assignedTo: CRYSTAL.az_id })).body;
  let r = await call(env, "POST", "/api/crm/tasks", { title: "Call back", assigneeId: CRYSTAL.az_id, leadId: lead.id, dueDate: "2026-10-06" });
  assert.equal(r.status, 200, JSON.stringify(r.body));
  assert.equal(r.body.customerType, "lead");
  assert.equal(r.body.customerId, lead.id);
  assert.equal(r.body.assignees[0].name, CRYSTAL.name);
  r = await call(env, "GET", `/api/crm/tasks?assigneeId=${CRYSTAL.az_id}&dueFrom=2026-10-06&dueTo=2026-10-06&status=0`);
  assert.equal(r.body.tasks.length, 1);   // a bare "to" day runs through the end of that day
  assert.equal((await call(env, "GET", `/api/crm/tasks?dueTo=2026-10-05`)).body.tasks.length, 0);
  r = await call(env, "POST", `/api/crm/tasks/${r.body.tasks[0].id}/complete`, { comment: "spoke" }, CRYSTAL.email);
  assert.equal(r.body.status, 1);
  assert.ok(r.body.completeDate);
  assert.equal((await call(env, "GET", `/api/crm/tasks?assigneeId=${CRYSTAL.az_id}&status=0`)).body.tasks.length, 0);
  const notes = (await call(env, "GET", `/api/crm/leads/${lead.id}/notes`)).body;
  assert.equal(notes[0].type, "TASK");
  assert.match(notes[0].body, /Task completed: Call back -- spoke/);
});

test("SRs: live 1 -> completed 2 on a known resolution, with the closing note", async () => {
  const { env } = fresh();
  const hh = (await call(env, "POST", "/api/crm/households", { firstname: "Dana", lastname: "Sanchez", phone: "6025550103" })).body;
  assert.equal(hh.status, 1);
  let r = await call(env, "POST", "/api/crm/srs", { householdId: hh.id, workflowId: 20, workflowStageId: 201, subject: "Add vehicle", csr: CRYSTAL.az_id });
  assert.equal(r.status, 200, JSON.stringify(r.body));
  assert.equal(r.body.status, 1);
  assert.equal(r.body.workflowName, "Service Pipeline");
  assert.equal(r.body.csrFirstname, "Crystal");
  assert.equal(r.body.customerType, "customer");
  assert.equal((await call(env, "POST", "/api/crm/srs", { householdId: hh.id, workflowId: 20, workflowStageId: 101, subject: "x" })).status, 400);
  const id = r.body.id;
  assert.equal((await call(env, "POST", `/api/crm/srs/${id}/complete`, { resolutionId: 1 })).status, 400);
  r = await call(env, "POST", `/api/crm/srs/${id}/complete`, { resolutionId: 32571, note: "Added the 2024 Tacoma, premium up $40" }, CRYSTAL.email);
  assert.equal(r.status, 200, JSON.stringify(r.body));
  assert.equal(r.body.status, 2);
  assert.equal(r.body.resolutionDesc, "Completed");
  assert.equal(r.body.completedBy, CRYSTAL.az_id);
  assert.equal((await call(env, "GET", `/api/crm/srs?status=1`)).body.serviceTickets.length, 0);
  assert.equal((await call(env, "GET", `/api/crm/srs?status=2&completedFrom=2000-01-01`)).body.serviceTickets.length, 1);
  const notes = (await call(env, "GET", `/api/crm/srs/${id}/notes`)).body;
  assert.equal(notes.length, 1);
  assert.equal(notes[0].householdId, hh.id);
  const s = (await call(env, "GET", "/api/crm/search?phone=6025550103")).body;
  assert.equal(s.customers.length, 1);
  assert.equal(s.serviceTickets.length, 0);   // completed SRs are not open
});

test("lists page from 0 and cap the page size", async () => {
  const { env } = fresh();
  for (let i = 0; i < 7; i++) await call(env, "POST", "/api/crm/households", { lastname: `H${i}` });
  const p0 = (await call(env, "GET", "/api/crm/households?limit=3&page=0")).body;
  const p2 = (await call(env, "GET", "/api/crm/households?limit=3&page=2")).body;
  assert.equal(p0.customers.length, 3);
  assert.equal(p0.totalCount, 7);
  assert.equal(p2.customers.length, 1);
  assert.equal((await call(env, "GET", "/api/crm/households?limit=9999")).body.limit, 500);
  assert.equal((await call(env, "GET", "/api/crm/households?q=h3")).body.customers.length, 1);
});
