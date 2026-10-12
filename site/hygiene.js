/* The CRM Hygiene & Audit Log (Frank, 2026-10-06: "go into my drive and look
   at file named CRM Hygiene, build that into pantheon, in a new category for
   operatonis only"). Amanda's Google Doc "CRM Hygeine" -- "CSR Redirection &
   Process Tracking": a table of accounts that were handled incorrectly,
   assigned improperly, or left without the notes, tasks or follow-ups the
   playbook asks for, reviewed in the one-on-one check-ins. The doc's
   columns are the log's:

     Client Name   Policy Number   Note / Description of Issue   Date

   plus what the one-on-ones need: the REP the entry is about, which line
   of the doc's Redirection Standard it missed (STANDARDS below -- the doc's
   own three, and Other), who logged it and when, and a "Reviewed in a
   one-on-one" tick with who and when. The doc's six rows are the log's
   first entries (SEED: logged as "Amanda (CRM Hygiene doc)", rep left
   blank -- the doc names none).

   One R2 file, hygiene/log.json, etag-guarded and retried like the
   rotation. Who sees it is staff.json's `hygiene` -- the ops team (Frank,
   Francisco, Veronica, Amanda); anyone else gets a 403 and the board keeps
   the Operations Center out of the menu. Everyone who sees it logs, edits
   and removes entries; every change keeps who and when. Always the
   verified Access email, never a request parameter. */

import { hasBoard, localDay } from "./staff.js";

const KEY = "hygiene/log.json";
const MAX_ENTRIES = 5000;

// The doc's "Redirection Standard Checklist", word for word; `key` is what
// an entry carries. The board draws whatever this sends.
export const STANDARDS = [
  { key: "check", label: "Check before passing",
    text: "Always review policy status, open SRs, and recent notes before assigning tasks or escalating to licensed service." },
  { key: "own", label: "Ownership",
    text: "If a client call or task is touched, ensure complete notes are logged and clear next steps/tasks are created." },
  { key: "cal", label: "Calendar accuracy",
    text: "Double-check team calendars for conflicts before confirming or moving appointment times." },
  { key: "other", label: "Other", text: "" },
];
export const INTRO = "Use this table to log accounts that were handled incorrectly, assigned improperly, or missing required documentation/notes. Reviewing these regularly during one-on-one check-ins helps ensure our service team builds strong accountability and consistent client care standards.";

// The doc's rows as they stood on 2026-10-06, carried in like the Rotation Sheet's.
const SEED_BY = "Amanda (CRM Hygiene doc)";
const SEED = [
  ["Alexis Baez", "557375416", "Flagged returned payment alert without reviewing account; payment had already processed and was paid in full.", "2026-09-25", "check"],
  ["Oliver Conde", "G006384213", "Account listed under former spouse; created SR without updating contact details, head of household, or noting divorce updates.", "2026-09-25", "own"],
  ["Victoria Gonzalez", "G016249494", "Rescheduled appointment to 10:00 AM without reviewing calendar, causing a double-booking conflict. Turns out she meant to move to Friday, I told her to fix twice and was not done until day of and told CM “well I guess I will do it or ill get in trouble”", "2026-10-02", "cal"],
  ["Michele Durnil", "200438550", "FFR set when it was a billing question sent in an email and a quick look at the billing would have answered their question", "2026-10-06", "check"],
  ["Estefanie Ovando", "G018280157", "Inquired about NOC document but left on Friday without logging call notes or setting a follow-up task or working it. Put it off until Monday so she could leave on time.", "2026-10-02", "own"],
  ["Roberto Diaz", "542022382", "She was working on cancellation with client from last week, no SR, no task, no notes, so when call came in today as inbound i was so confused on what was happening and the cancellation was not passed to anyone to retain.", "2026-10-06", "own"],
];

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
const str = (v, n) => String(v == null ? "" : v).trim().slice(0, n);
const isDay = (s) => /^\d{4}-\d{2}-\d{2}$/.test(s);

function fresh() {
  return { entries: SEED.map(([client, policy, issue, date, standard], i) => ({
    id: "doc" + (i + 1), client, policy, issue, date, standard, rep: "",
    by: SEED_BY, at: "2026-10-06T19:00:00.000Z", reviewed: null })) };
}
async function load(env) {
  const obj = await env.BOARD.get(KEY);
  if (!obj) return { state: fresh(), etag: null };
  let state;
  try { state = await obj.json(); } catch (_) { state = null; }
  if (!state || !Array.isArray(state.entries)) state = fresh();
  return { state, etag: obj.etag };
}
async function save(env, state, etag) {
  const opts = { httpMetadata: { contentType: "application/json" } };
  opts.onlyIf = etag ? { etagMatches: etag } : { etagDoesNotMatch: "*" };
  return (await env.BOARD.put(KEY, JSON.stringify(state), opts)) !== null;
}

function access(me) {
  return hasBoard(me.email, "hygiene");
}
function answer(state, me) {
  return { entries: state.entries, standards: STANDARDS, intro: INTRO, me: me.name, today: localDay() };
}

/** GET /api/hygiene -> {entries, standards, intro, me, today}; 403 for anyone but staff.json's `hygiene`. */
export async function hygieneGet(request, env, identityOf) {
  const me = identityOf(request, env);
  if (!access(me)) return json({ error: "not permitted" }, 403);
  const { state } = await load(env);
  return json(answer(state, me));
}

/** POST /api/hygiene {op, ...}
 *    add      {client, policy, issue, date, rep, standard}     a new entry
 *    edit     {id, client?, policy?, issue?, date?, rep?, standard?}   keeps every earlier version under `edits`
 *    review   {id, on: true|false}                             reviewed in a one-on-one (who and when), or not yet
 *    remove   {id}                                            off the log for good */
export async function hygienePost(request, env, identityOf) {
  const me = identityOf(request, env);
  if (!access(me)) return json({ error: "not permitted" }, 403);
  let body;
  try { body = await request.json(); } catch (_) { return json({ error: "bad request body" }, 400); }
  const now = new Date().toISOString();
  for (let attempt = 0; attempt < 5; attempt++) {
    const { state, etag } = await load(env);
    const r = apply(state, body, me, now);
    if (r.error) return json({ error: r.error }, r.status || 400);
    if (await save(env, state, etag)) return json({ ...r, ...answer(state, me) });
  }
  return json({ error: "the log is busy -- try again" }, 503);
}

function fields(body, partial) {
  const out = {};
  const has = (k) => !partial || body[k] !== undefined;
  if (has("client")) out.client = str(body.client, 120);
  if (has("policy")) out.policy = str(body.policy, 40);
  if (has("issue")) out.issue = str(body.issue, 1500);
  if (has("rep")) out.rep = str(body.rep, 60);
  if (has("date")) {
    out.date = str(body.date, 10);
    if (out.date && !isDay(out.date)) return { error: "bad date" };
  }
  if (has("standard")) {
    out.standard = str(body.standard, 20);
    if (out.standard && !STANDARDS.some((s) => s.key === out.standard)) return { error: "bad standard" };
  }
  return out;
}

function apply(state, body, me, now) {
  const op = String(body.op || "");
  if (op === "add") {
    if (state.entries.length >= MAX_ENTRIES) return { error: `the log holds ${MAX_ENTRIES} entries at most` };
    const f = fields(body, false);
    if (f.error) return f;
    if (!f.client && !f.policy) return { error: "name the client or the policy" };
    if (!f.issue) return { error: "say what happened" };
    const e = { id: crypto.randomUUID().slice(0, 10), ...f, date: f.date || localDay(), by: me.name, at: now, reviewed: null };
    state.entries.push(e);
    return { entry: e };
  }
  const e = state.entries.find((x) => x.id === String(body.id || ""));
  if (!e) return { error: "entry not found", status: 404 };
  if (op === "edit") {
    const f = fields(body, true);
    if (f.error) return f;
    if (!Object.keys(f).length) return { error: "nothing to change" };
    const was = {};
    for (const k of Object.keys(f)) if (e[k] !== f[k]) was[k] = e[k] == null ? "" : e[k];
    if (!Object.keys(was).length) return { entry: e };
    (e.edits = e.edits || []).push({ by: me.name, at: now, was });
    Object.assign(e, f);
    if (!e.client && !e.policy) return { error: "name the client or the policy" };
    if (!e.issue) return { error: "say what happened" };
    return { entry: e };
  }
  if (op === "review") {
    e.reviewed = body.on ? { by: me.name, at: now } : null;
    return { entry: e };
  }
  if (op === "remove") {
    state.entries = state.entries.filter((x) => x !== e);
    return { removed: e.id };
  }
  return { error: "bad op" };
}
