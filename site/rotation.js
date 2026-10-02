/* The new-business rotation (Frank, 2026-10-02: "fix the rotation sheet ...
   its how we rotate new business walkin and call ins ... i want this to be
   part of the board"). It replaces Debbie's "Rotation Sheet" in Google
   Drive: three rotations, each a loop of people taking turns.

     personal   Personal lines: every producer and Amanda, never Mike
     life       Life: Mike, Lorena, Coral
     mexico     Mexico policies: Lorena, Amanda, Crystal, Mike, Coral, Sarahi

   One R2 file, rotation/state.json: each rotation's order and who is next,
   and every turn ever logged. A turn is one of
     in    the walk-in / call-in went to whoever was next; the rotation moves on
     skip  whoever was next was out or busy; it moves on with nobody given
     out   it went to someone out of turn (the client asked for them); it
           does NOT move on
   A turn names who was next when it was logged (`expect`), so two people
   logging at once cannot both hand the same turn out: the second is told
   the rotation moved (409) and sees the new next-up.

   Who sees it (ROTATION_VIEWERS, wrangler.jsonc): Debbie, Crystal and the
   ops team (Frank, Francisco, Veronica, Amanda) -- "This rotation should
   only be visible to debiie, crystal, and the ops team". Anyone else gets
   a 403 and the board keeps the page out of the menu. Everyone who sees it
   logs turns; ROTATION_EDITORS change an order or who is next. Always the
   verified Access email, never a request parameter. */

const KEY = "rotation/state.json";

export const ROTATION_PEOPLE = ["Lorena Gonzalez", "Sarahi Chin", "Amanda Torricellas", "Coral Barwick",
  "Crystal Mango", "Mike Olvera"];

// Frank, 2026-10-02. Personal lines keeps the sheet's own order
// (Sep 19 - Oct 19 tab, column A); life and Mexico keep theirs with the
// new names added at the end.
const DEFAULT_LISTS = {
  personal: { label: "Personal lines", order: ["Lorena Gonzalez", "Sarahi Chin", "Amanda Torricellas", "Coral Barwick", "Crystal Mango"] },
  life: { label: "Life", order: ["Mike Olvera", "Lorena Gonzalez", "Coral Barwick"] },
  mexico: { label: "Mexico policies", order: ["Lorena Gonzalez", "Amanda Torricellas", "Crystal Mango", "Mike Olvera", "Coral Barwick", "Sarahi Chin"] },
};
const HOW = ["call in", "walk in", "transfer", "other"];

const emails = (s) => String(s || "").toLowerCase().split(",").map((x) => x.trim()).filter(Boolean);
function access(me, env) {
  const see = emails(env.ROTATION_VIEWERS).includes(me.email);
  return { see, edit: see && emails(env.ROTATION_EDITORS).includes(me.email) };
}
const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

function fresh() {
  const lists = {};
  for (const [k, l] of Object.entries(DEFAULT_LISTS)) lists[k] = { label: l.label, order: [...l.order], next: l.order[0] };
  return { lists, entries: [] };
}
async function load(env) {
  const obj = await env.BOARD.get(KEY);
  if (!obj) return { state: fresh(), etag: null };
  const state = await obj.json();
  for (const [k, l] of Object.entries(DEFAULT_LISTS)) if (!state.lists[k]) state.lists[k] = { label: l.label, order: [...l.order], next: l.order[0] };
  state.entries = state.entries || [];
  return { state, etag: obj.etag };
}
// Written only if nobody wrote since it was read; otherwise the caller
// reads again and re-applies (or refuses, for a turn that is now stale).
async function save(env, state, etag) {
  const opts = { httpMetadata: { contentType: "application/json" } };
  if (etag) opts.onlyIf = { etagMatches: etag };
  return (await env.BOARD.put(KEY, JSON.stringify(state), opts)) !== null;
}
const after = (order, name) => {
  if (!order.length) return "";
  const i = order.indexOf(name);
  return order[(i + 1) % order.length];
};

/** GET /api/rotation -> {lists, entries, people, can_edit, me}. */
export async function rotationGet(request, env, identityOf) {
  const me = identityOf(request, env);
  const a = access(me, env);
  if (!a.see) return json({ error: "not permitted" }, 403);
  const { state } = await load(env);
  return json({ ...state, people: ROTATION_PEOPLE, how: HOW, can_edit: a.edit, me: me.name });
}

/** POST /api/rotation {op, ...}
 *   log    {list, kind: in|skip|out, producer, expect, client, how, date, notes}
 *   del    {id}                      the newest turn on its rotation puts its person back up
 *   order  {list, order: [...], next} editors only */
export async function rotationPost(request, env, identityOf) {
  const me = identityOf(request, env);
  const a = access(me, env);
  if (!a.see) return json({ error: "not permitted" }, 403);
  let body;
  try { body = await request.json(); } catch (_) { return json({ error: "bad request body" }, 400); }
  for (let attempt = 0; attempt < 4; attempt++) {
    const { state, etag } = await load(env);
    const r = apply(state, body, me, a);
    if (r.error) return json({ error: r.error, lists: state.lists }, r.status || 400);
    if (await save(env, state, etag)) return json({ ...r, lists: state.lists });
  }
  return json({ error: "the rotation is busy -- try again" }, 503);
}

function apply(state, body, me, a) {
  const op = String(body.op || "");
  if (op === "log") {
    const list = state.lists[String(body.list || "")];
    if (!list) return { error: "no such rotation" };
    const kind = String(body.kind || "");
    if (!["in", "skip", "out"].includes(kind)) return { error: "bad kind" };
    const producer = String(body.producer || "");
    if (kind !== "out" && String(body.expect || "") !== list.next) {
      return { error: `the rotation moved: ${list.next.split(" ")[0]} is up now`, status: 409 };
    }
    if (kind !== "out" && producer !== list.next) return { error: "that person is not up" };
    if (kind === "out" && !list.order.includes(producer)) return { error: "that person is not on this rotation" };
    const client = String(body.client || "").trim().slice(0, 120);
    if (kind !== "skip" && !client) return { error: "who is the client?" };
    const date = /^\d{4}-\d{2}-\d{2}$/.test(String(body.date || "")) ? body.date : new Date(Date.now() - 7 * 3600000).toISOString().slice(0, 10);
    const entry = {
      id: crypto.randomUUID(), list: body.list, kind, producer, client,
      how: HOW.includes(body.how) ? body.how : (kind === "skip" ? "" : "call in"),
      date, notes: String(body.notes || "").trim().slice(0, 300),
      logged_by: me.name, created_at: new Date().toISOString(),
    };
    state.entries.push(entry);
    if (kind !== "out") list.next = after(list.order, producer);
    return { entry };
  }
  if (op === "del") {
    const id = String(body.id || "");
    const e = state.entries.find((x) => x.id === id);
    if (!e) return { error: "entry not found", status: 404 };
    if (!a.edit && e.logged_by !== me.name) return { error: "only whoever logged it, or a manager, can remove it", status: 403 };
    state.entries = state.entries.filter((x) => x.id !== id);
    // Taking back the newest turn on a rotation gives that person the turn
    // back -- the usual reason is it was logged by mistake.
    const list = state.lists[e.list];
    if (list && e.kind !== "out") {
      const newer = state.entries.some((x) => x.list === e.list && x.kind !== "out" && x.created_at > e.created_at);
      if (!newer && list.order.includes(e.producer)) list.next = e.producer;
    }
    return { ok: true };
  }
  if (op === "order") {
    if (!a.edit) return { error: "only a manager can change a rotation", status: 403 };
    const list = state.lists[String(body.list || "")];
    if (!list) return { error: "no such rotation" };
    const order = (Array.isArray(body.order) ? body.order : []).map(String);
    if (!order.length) return { error: "a rotation needs someone on it" };
    if (order.some((p) => !ROTATION_PEOPLE.includes(p)) || new Set(order).size !== order.length) return { error: "bad order" };
    list.order = order;
    const next = String(body.next || "");
    list.next = order.includes(next) ? next : order.includes(list.next) ? list.next : order[0];
    state.changes = (state.changes || []).concat([{ list: body.list, order, next: list.next, by: me.name, at: new Date().toISOString() }]).slice(-100);
    return { ok: true };
  }
  return { error: "bad op" };
}
