/* The all-time lead index behind the board's search (Frank, 2026-10-02:
   "can it just be a universal all time search?"). One compact entry per
   lead across every published day: name, AgencyZoom id, producer, and for
   each day the lead appears on, what it was there as -- c coaching card,
   s sold, q quoted, r reached, d dialled, t texted, m misfiled. Kept in R2
   at worker-private/lead_index.json and topped up with any newly published
   day on each request, so the first call after a quiet spell reads a day or
   two, never the whole bucket again. Served by GET /api/leads behind the
   same Access gate as the day documents (it is customer NPI). */

const KEY = "worker-private/lead_index.json";

/** The lead entries of one day document: { key: { l, id, who, f } }. */
export function indexDay(doc) {
  const out = {};
  const add = (name, id, who, flag) => {
    name = String(name || "").trim(); if (!name) return;
    const k = id != null && id !== "" ? "i" + id : "n" + name.toLowerCase();
    const e = out[k] || (out[k] = { l: name, id: id != null && id !== "" ? String(id) : "", who: who || "", f: "" });
    if (!e.who && who) e.who = who;
    if (!e.f.includes(flag)) e.f += flag;
  };
  const R = doc.rows || {};
  for (const c of doc.calls || []) add(c.lead, c.lead_id, c.who, "c");
  for (const r of R.sold_leads || []) add(r.lead, r.lead_id, r.who, "s");
  for (const r of R.quoted || []) add(r.lead, r.lead_id, r.who, "q");
  for (const r of R.contacts || []) add(r.lead, r.lead_id, r.who, "r");
  for (const r of R.dials || []) add(r.lead, r.lead_id, r.who, "d");
  for (const r of (doc.messages || {}).replies || []) add(r.lead, r.lead_id, r.who, "t");
  for (const r of doc.misfiled || []) add(r.lead, r.lead_id, r.assigned, "m");
  return out;
}

/** Fold one day's entries into the index. */
export function foldDay(index, day, entries) {
  for (const [k, e] of Object.entries(entries)) {
    const cur = index.leads[k] || (index.leads[k] = { l: e.l, id: e.id, who: e.who, d: {} });
    if (!cur.who && e.who) cur.who = e.who;
    cur.d[day] = e.f;
  }
  if (!index.days.includes(day)) index.days.push(day);
}

/** The index as the browser wants it: one row per lead, days newest first. */
export function serveIndex(index) {
  const leads = Object.values(index.leads).map((e) => {
    const days = Object.entries(e.d).sort((a, b) => (a[0] < b[0] ? 1 : -1));
    return { l: e.l, id: e.id, who: e.who, days };
  });
  return { days: [...index.days].sort().reverse(), leads };
}

export async function leadsIndex(env) {
  const got = await env.BOARD.get(KEY);
  let index = null;
  if (got) { try { index = await got.json(); } catch (_) { index = null; } }
  if (!index || !index.leads || !Array.isArray(index.days)) index = { days: [], leads: {} };
  // every published day, newest first
  const published = [];
  let cursor;
  do {
    const listed = await env.BOARD.list({ prefix: "days/", cursor });
    for (const o of listed.objects) { const m = o.key.match(/^days\/(\d{4}-\d{2}-\d{2})\.json$/); if (m) published.push(m[1]); }
    cursor = listed.truncated ? listed.cursor : undefined;
  } while (cursor);
  const missing = published.filter((d) => !index.days.includes(d)).sort().reverse();
  let changed = false;
  for (const day of missing) {
    const obj = await env.BOARD.get(`days/${day}.json`);
    if (!obj) continue;
    let doc = null;
    try { doc = await obj.json(); } catch (_) { doc = null; }
    if (!doc) continue;
    foldDay(index, day, indexDay(doc));
    changed = true;
  }
  if (changed) await env.BOARD.put(KEY, JSON.stringify(index), { httpMetadata: { contentType: "application/json" } });
  return new Response(JSON.stringify(serveIndex(index)), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}
