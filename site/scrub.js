/* The lead scrub tracker (Frank, 2026-10-02: "an interactive way to track a
   list of leads we are scrubbing, making sure they are updated in both apex
   and agency zoom"). A lead list exported from AgencyZoom is imported as a
   scrub list; each lead is then marked off as it is cleaned up in both
   systems:

     Apex          its status in Apex
     AgencyZoom    its status in AgencyZoom, plus two boxes beside it:
                   Duplicates Cleaned and Tagged

   A lead is DONE when Apex and AgencyZoom both read a finished status
   (DONE_STATUSES) and both AgencyZoom boxes are ticked. The options are
   FIELDS below and nowhere else -- the board draws whatever this sends, so
   changing an option is a change here only (and the Road Map line).

   One R2 file per list, scrub/lists/<id>.json, with the list's progress in
   its customMetadata so the picker never reads every list. Writes are
   etag-guarded and retried, like the rotation: two people ticking leads on
   the same list at once both land.

   Who sees it is SCRUB_VIEWERS (wrangler.jsonc); SCRUB_EDITORS also import,
   rename and delete lists and remove leads. Every change records who made
   it and when, from the verified Access email. */

const PREFIX = "scrub/lists/";

const STATUS = ["Not started", "Updated", "No changes needed", "Not found", "Needs follow-up"];
export const FIELDS = [
  { key: "apex", label: "Apex", type: "select", options: STATUS },
  { key: "az", label: "AgencyZoom", type: "select", options: STATUS },
  { key: "az_dups", label: "Duplicates Cleaned", type: "check", group: "az" },
  { key: "az_tagged", label: "Tagged", type: "check", group: "az" },
];
export const DONE_STATUSES = ["Updated", "No changes needed"];
const COLS = ["name", "phone", "email", "az_id", "assigned", "source", "stage"];
const MAX_ROWS = 5000, MAX_EXTRA = 30, MAX_VAL = 200;

const emails = (s) => String(s || "").toLowerCase().split(",").map((x) => x.trim()).filter(Boolean);
function access(me, env) {
  const edit = emails(env.SCRUB_EDITORS).includes(me.email);
  return { see: edit || emails(env.SCRUB_VIEWERS).includes(me.email), edit };
}
const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
const str = (v, n = MAX_VAL) => String(v == null ? "" : v).trim().slice(0, n);

export function isDone(s) {
  s = s || {};
  return DONE_STATUSES.includes(s.apex) && DONE_STATUSES.includes(s.az) && !!s.az_dups && !!s.az_tagged;
}
function summary(list) {
  const leads = list.leads || [];
  const ok = (k) => leads.filter((l) => DONE_STATUSES.includes((l.s || {})[k])).length;
  return {
    id: list.id, name: list.name, created_at: list.created_at, created_by: list.created_by,
    count: leads.length, done: leads.filter((l) => isDone(l.s)).length,
    apex: ok("apex"), az: ok("az"),
    az_dups: leads.filter((l) => (l.s || {}).az_dups).length,
    az_tagged: leads.filter((l) => (l.s || {}).az_tagged).length,
    updated_at: list.updated_at || list.created_at,
  };
}
function meta(list) {
  const m = {};
  for (const [k, v] of Object.entries(summary(list))) m[k] = String(v == null ? "" : v);
  return m;
}
async function load(env, id) {
  const obj = await env.BOARD.get(PREFIX + id + ".json");
  if (!obj) return null;
  return { list: await obj.json(), etag: obj.etag };
}
async function save(env, list, etag) {
  list.updated_at = new Date().toISOString();
  const opts = { httpMetadata: { contentType: "application/json" }, customMetadata: meta(list) };
  opts.onlyIf = etag ? { etagMatches: etag } : { etagDoesNotMatch: "*" };
  return (await env.BOARD.put(PREFIX + list.id + ".json", JSON.stringify(list), opts)) !== null;
}

function cleanRows(rows) {
  if (!Array.isArray(rows)) return [];
  return rows.slice(0, MAX_ROWS).map((r) => {
    const lead = { id: crypto.randomUUID().slice(0, 12), extra: {}, s: { apex: STATUS[0], az: STATUS[0], az_dups: false, az_tagged: false, notes: "" }, by: {} };
    for (const c of COLS) lead[c] = str((r || {})[c]);
    const extra = (r && typeof r.extra === "object" && r.extra) || {};
    for (const [k, v] of Object.entries(extra).slice(0, MAX_EXTRA)) lead.extra[str(k, 60)] = str(v);
    return lead;
  }).filter((l) => l.name || l.phone || l.email || l.az_id);
}

/** GET /api/scrub -> {lists: [summary], fields, done_statuses, can_edit, me}
 *  GET /api/scrub/<id> -> {list, fields, ...} */
export async function scrubGet(request, env, identityOf, id) {
  const me = identityOf(request, env);
  const a = access(me, env);
  if (!a.see) return json({ error: "not permitted" }, 403);
  const base = { fields: FIELDS, done_statuses: DONE_STATUSES, can_edit: a.edit, me: me.name };
  if (id) {
    const got = await load(env, id);
    if (!got) return json({ error: "no such list" }, 404);
    return json({ ...base, list: got.list, summary: summary(got.list) });
  }
  const lists = [];
  let cursor;
  do {
    const page = await env.BOARD.list({ prefix: PREFIX, cursor, include: ["customMetadata"] });
    for (const o of page.objects) {
      const m = o.customMetadata || {};
      const n = (k) => Number(m[k] || 0);
      lists.push({ id: m.id || o.key.slice(PREFIX.length, -5), name: m.name || "", created_at: m.created_at || "",
        created_by: m.created_by || "", updated_at: m.updated_at || "", count: n("count"), done: n("done"),
        apex: n("apex"), az: n("az"), az_dups: n("az_dups"), az_tagged: n("az_tagged") });
    }
    cursor = page.truncated ? page.cursor : undefined;
  } while (cursor);
  lists.sort((x, y) => String(y.created_at).localeCompare(String(x.created_at)));
  return json({ ...base, lists });
}

/** POST /api/scrub {op: "create", name, rows}               editors
 *  POST /api/scrub/<id> {op, ...}
 *    set     {lead, field, value}   anyone who sees it; field is a FIELDS key or "notes"
 *    add     {rows}                 editors: more leads onto the list
 *    rename  {name}                 editors
 *    remove  {lead}                 editors: one lead off the list
 *    delete  {}                     editors: the whole list */
export async function scrubPost(request, env, identityOf, id) {
  const me = identityOf(request, env);
  const a = access(me, env);
  if (!a.see) return json({ error: "not permitted" }, 403);
  let body;
  try { body = await request.json(); } catch (_) { return json({ error: "bad request body" }, 400); }
  const op = String(body.op || "");
  const now = new Date().toISOString();

  if (!id) {
    if (op !== "create") return json({ error: "bad op" }, 400);
    if (!a.edit) return json({ error: "only a manager can import a list" }, 403);
    const leads = cleanRows(body.rows);
    if (!leads.length) return json({ error: "no leads in that file" }, 400);
    const list = { id: crypto.randomUUID().slice(0, 8), name: str(body.name, 120) || `Scrub ${now.slice(0, 10)}`,
      created_at: now, created_by: me.name, leads };
    if (!(await save(env, list, null))) return json({ error: "could not save -- try again" }, 503);
    return json({ ok: true, summary: summary(list) });
  }

  if (op === "delete") {
    if (!a.edit) return json({ error: "only a manager can delete a list" }, 403);
    await env.BOARD.delete(PREFIX + id + ".json");
    return json({ ok: true });
  }
  for (let attempt = 0; attempt < 5; attempt++) {
    const got = await load(env, id);
    if (!got) return json({ error: "no such list" }, 404);
    const { list, etag } = got;
    const r = apply(list, body, me, a, now);
    if (r.error) return json({ error: r.error }, r.status || 400);
    if (await save(env, list, etag)) return json({ ...r, summary: summary(list) });
  }
  return json({ error: "the list is busy -- try again" }, 503);
}

function apply(list, body, me, a, now) {
  const op = String(body.op || "");
  if (op === "set") {
    const lead = list.leads.find((l) => l.id === String(body.lead || ""));
    if (!lead) return { error: "lead not found", status: 404 };
    const key = String(body.field || "");
    const f = FIELDS.find((x) => x.key === key);
    let value;
    if (key === "notes") value = str(body.value, 500);
    else if (!f) return { error: "bad field" };
    else if (f.type === "check") value = !!body.value;
    else if (f.options.includes(body.value)) value = body.value;
    else return { error: "bad value" };
    lead.s = lead.s || {};
    lead.s[key] = value;
    lead.by = lead.by || {};
    lead.by[key] = { who: me.name, at: now };
    return { lead };
  }
  if (!a.edit) return { error: "only a manager can change the list itself", status: 403 };
  if (op === "add") {
    const more = cleanRows(body.rows);
    if (list.leads.length + more.length > MAX_ROWS) return { error: `a list holds ${MAX_ROWS} leads at most` };
    list.leads.push(...more);
    return { added: more.length };
  }
  if (op === "rename") {
    const name = str(body.name, 120);
    if (!name) return { error: "give it a name" };
    list.name = name;
    return { ok: true };
  }
  if (op === "remove") {
    const n = list.leads.length;
    list.leads = list.leads.filter((l) => l.id !== String(body.lead || ""));
    if (list.leads.length === n) return { error: "lead not found", status: 404 };
    return { ok: true };
  }
  return { error: "bad op" };
}
