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
     skip  whoever was next was OUT: their turn passes. With a client typed
           (Frank, 2026-10-05: "yes, do it") the client goes to the next
           person in the same click, as that person's own `in` turn -- the
           two lines are paired and come back together. With no client it
           just passes, for someone known to be out before anyone walks in
     busy  whoever was next was BUSY (Frank, 2026-10-02: "when they are busy,
           it should give it to the next producer, but still keep who was
           busy up next"): the client goes to the next person in line, the
           busy person stays up, and whoever covered is `owed` -- the
           rotation passes over them once, so covering is their turn
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
// Who covers when `list.next` is busy: the next person after them who has
// not already covered (and so is not owed a pass).
export function coverFor(list) {
  const owed = list.owed || [];
  let n = list.next;
  for (let i = 0; i < list.order.length; i++) {
    n = after(list.order, n);
    if (n === list.next) return "";
    if (!owed.includes(n)) return n;
  }
  return "";
}
// Move the rotation on from `from`, passing once over anyone who covered for
// a busy person. Returns who was passed, so a removed turn can put them back.
function advance(list, from) {
  const owed = list.owed || [], passed = [];
  let n = after(list.order, from);
  for (let i = 0; i < list.order.length && n !== from && owed.includes(n); i++) {
    owed.splice(owed.indexOf(n), 1); passed.push(n); n = after(list.order, n);
  }
  list.owed = owed; list.next = n;
  return passed;
}

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
    if (!["in", "skip", "busy", "out"].includes(kind)) return { error: "bad kind" };
    const producer = String(body.producer || "");
    if (kind !== "out" && String(body.expect || "") !== list.next) {
      return { error: `the rotation moved: ${list.next.split(" ")[0]} is up now`, status: 409 };
    }
    if ((kind === "in" || kind === "skip") && producer !== list.next) return { error: "that person is not up" };
    if (kind === "busy") {
      const cover = coverFor(list);
      if (!cover) return { error: "nobody else on this rotation can take it" };
      if (producer !== cover) return { error: `the rotation moved: ${cover.split(" ")[0]} covers now`, status: 409 };
    }
    if (kind === "out" && !list.order.includes(producer)) return { error: "that person is not on this rotation" };
    const client = String(body.client || "").trim().slice(0, 120);
    if (kind !== "skip" && !client) return { error: "who is the client?" };
    const date = /^\d{4}-\d{2}-\d{2}$/.test(String(body.date || "")) ? body.date : new Date(Date.now() - 7 * 3600000).toISOString().slice(0, 10);
    const how = HOW.includes(body.how) ? body.how : "call in";
    const entry = {
      id: crypto.randomUUID(), list: body.list, kind, producer, client: kind === "skip" ? "" : client,
      how: kind === "skip" ? "" : how,
      date, notes: String(body.notes || "").trim().slice(0, 300),
      logged_by: me.name, created_at: new Date().toISOString(),
    };
    if (kind === "busy") {
      entry.busy = list.next;                       // stays up
      list.owed = (list.owed || []).concat([producer]);
    } else if (kind !== "out") {
      const passed = advance(list, producer);
      if (passed.length) entry.passed = passed;
    }
    state.entries.push(entry);
    // Out with a client: the client goes to whoever is up now, on their turn.
    if (kind === "skip" && client && list.next && list.next !== producer) {
      const given = { ...entry, id: crypto.randomUUID(), kind: "in", producer: list.next, client, how,
        pair: entry.id, created_at: new Date(Date.parse(entry.created_at) + 1).toISOString() };
      delete given.passed;
      entry.pair = given.id;
      const passed = advance(list, given.producer);
      if (passed.length) given.passed = passed;
      state.entries.push(given);
      return { entry, given };
    }
    return { entry };
  }
  if (op === "del") {
    const id = String(body.id || "");
    const e = state.entries.find((x) => x.id === id);
    if (!e) return { error: "entry not found", status: 404 };
    if (!a.edit && e.logged_by !== me.name) return { error: "only whoever logged it, or a manager, can remove it", status: 403 };
    // An out and the client it handed on are one action: both go together,
    // and the undo is worked from the out (the earlier of the two).
    const pair = e.pair ? state.entries.find((x) => x.id === e.pair) : null;
    const gone = new Set([e.id].concat(pair ? [pair.id] : []));
    state.entries = state.entries.filter((x) => !gone.has(x.id));
    if (pair && pair.kind === "skip") return undo(state, pair, e);
    if (pair) return undo(state, e, pair);
    // Taking back the newest turn on a rotation gives that person the turn
    // back -- the usual reason is it was logged by mistake.
    const list = state.lists[e.list];
    if (list && e.kind === "busy") {
      // Whoever covered is no longer owed a pass (if they still are).
      const owed = list.owed || [], i = owed.indexOf(e.producer);
      if (i >= 0) owed.splice(i, 1);
      list.owed = owed;
    } else if (list && e.kind !== "out") {
      const newer = state.entries.some((x) => x.list === e.list && x.kind !== "out" && x.kind !== "busy" && x.created_at > e.created_at);
      if (!newer && list.order.includes(e.producer)) {
        list.next = e.producer;
        // ...and anyone that turn passed over is owed their pass again.
        list.owed = (list.owed || []).concat((e.passed || []).filter((p) => list.order.includes(p)));
      }
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
    list.owed = (list.owed || []).filter((p) => order.includes(p));
    const next = String(body.next || "");
    list.next = order.includes(next) ? next : order.includes(list.next) ? list.next : order[0];
    state.changes = (state.changes || []).concat([{ list: body.list, order, next: list.next, by: me.name, at: new Date().toISOString() }]).slice(-100);
    return { ok: true };
  }
  return { error: "bad op" };
}

// Take back an out that handed its client on: the out person is up again and
// anyone either turn passed over is owed their pass again -- if nothing newer
// has moved the rotation since.
function undo(state, out, given) {
  const list = state.lists[out.list];
  if (!list) return { ok: true };
  const newer = state.entries.some((x) => x.list === out.list && x.kind !== "out" && x.kind !== "busy" && x.created_at > given.created_at);
  if (!newer && list.order.includes(out.producer)) {
    list.next = out.producer;
    list.owed = (list.owed || []).concat([...(out.passed || []), ...(given.passed || [])].filter((p) => list.order.includes(p)));
  }
  return { ok: true };
}
