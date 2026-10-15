/* Operations Center > Campaigns (Frank, 2026-10-15: "tomorrow after
   receiving the results of what they did ill decide who will be getting the
   highest load of these leads, how can we create me a tracker for it" --
   "just me for now"). A lead campaign is a list of leads handed out to the
   producers -- the Rate Decrease Campaign's first batch was 10 each from his
   sheet's QNC tab: 5 found in AgencyZoom and reassigned to them, 5 not in
   AgencyZoom for them to create. This tracks what each producer did with
   theirs, from what the board already reads, and makes no request of its
   own to AgencyZoom or RingCentral:

     - each day's published document (days/<day>.json), or the day's
       checkpoint while it is not published yet (intraday/<day>.json): the
       rows the Digest's lists show -- dials, contacts, quoted, sold leads --
       matched to the campaign's leads by AgencyZoom lead id;
     - the Worker's kept list of the day's active leads
       (live/<day>-leads.json): a lead to CREATE is found there by its phone
       number (last ten digits, like az_corpus.e164) once someone makes it,
       which gives its lead id; a dial row by the producer on the same last
       four digits and name finds it too.

   The list itself is R2 campaigns/<key>/list.json -- customer names, phones
   and addresses, so never in the repository -- written once when a batch is
   handed out:

     { key, title, start: "YYYY-MM-DD", source, created_at,
       leads: [{ id, producer: "<full name>", kind: "reassign" | "create",
                 name, phone, email, address, quotes: [{line, premium, date}],
                 lead_id (reassign; null for create), from, note }] }

   A producer is credited only with their own dials, contacts, quotes and
   sales on their own campaign leads; another producer working one is shown
   on the lead, never counted. The ranking is the leaderboard's 5-4-3-2-1 per
   category (ties share the higher points, nothing for zero). Who sees it is
   staff.json's `campaigns` board key -- Frank alone (2026-10-15). */

import { hasBoard, localDay } from "./staff.js";

const PREFIX = "campaigns/";
const MAX_DAYS = 62;

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
const ten = (s) => { const d = String(s || "").replace(/\D/g, ""); return d.length >= 10 ? d.slice(-10) : ""; };
const words = (s) => String(s || "").toLowerCase().replace(/[^a-z ]/g, " ").split(/\s+/).filter((w) => w.length > 1);

function daysFrom(start, end) {
  const out = [];
  const t = new Date(start + "T12:00:00Z"), e = new Date(end + "T12:00:00Z");
  while (t <= e && out.length < MAX_DAYS) { out.push(t.toISOString().slice(0, 10)); t.setUTCDate(t.getUTCDate() + 1); }
  return out;
}

async function getJson(env, key) {
  const obj = await env.BOARD.get(key);
  if (!obj) return null;
  try { return await obj.json(); } catch (_) { return null; }
}

async function listCampaigns(env) {
  const out = [];
  let cursor;
  do {
    const page = await env.BOARD.list({ prefix: PREFIX, cursor });
    for (const o of page.objects) {
      if (!o.key.endsWith("/list.json")) continue;
      const c = await getJson(env, o.key);
      if (c) out.push({ key: c.key, title: c.title, start: c.start, leads: (c.leads || []).length });
    }
    cursor = page.truncated ? page.cursor : undefined;
  } while (cursor);
  return out.sort((a, b) => String(b.start).localeCompare(String(a.start)));
}

// The day's rows: the published document, else the checkpoint.
async function dayRows(env, day) {
  let doc = await getJson(env, `days/${day}.json`), src = "published";
  if (!doc) { doc = await getJson(env, `intraday/${day}.json`); src = "checkpoint"; }
  if (!doc) return null;
  return { src, built_at: doc.built_at || doc.as_of || "", rows: doc.rows || {} };
}

const RANK = ["sold", "quoted", "reached", "dialed", "created", "untouched"];

export function track(campaign, days) {
  const leads = (campaign.leads || []).map((l) => ({
    ...l, ids: new Set(l.lead_id ? [Number(l.lead_id)] : []), phone10: ten(l.phone),
    created: null, dials: 0, dial_days: [], talk: 0, reached: false, reached_secs: 0,
    summary: "", quoted: 0, is_quoted: false, sold: false, sold_day: "", first_day: "", last_day: "", others: new Set(),
  }));
  const byPhone = new Map();
  for (const l of leads) if (l.phone10) byPhone.set(l.phone10, l);

  // 1. Find the leads to create: a lead record on the phone, from the kept active-lead lists.
  for (const d of days) {
    for (const r of (d.active || [])) {
      for (const ph of [r.phone, r.secondaryPhone]) {
        const l = byPhone.get(ten(ph));
        if (!l || l.kind !== "create") continue;
        l.ids.add(Number(r.id));
        const made = String(r.createDate || "").slice(0, 10);
        if (made >= campaign.start && (!l.created || made < l.created.day))
          l.created = { day: made, lead_id: r.id, assigned_to: r.assignedTo, name: `${r.firstname || ""} ${r.lastname || ""}`.trim() };
      }
    }
  }
  // ...and from the producer's own dial rows: same last four, a name word in common.
  for (const d of days) {
    for (const r of ((d.rows || {}).dials || [])) {
      if (!r.lead_id) continue;
      for (const l of leads) {
        if (l.kind !== "create" || l.ids.has(Number(r.lead_id)) || r.who !== l.producer) continue;
        if (!l.phone10 || r.last4 !== l.phone10.slice(-4)) continue;
        const a = words(l.name), b = words(r.lead);
        if (a.some((w) => b.includes(w))) l.ids.add(Number(r.lead_id));
      }
    }
  }
  const owner = new Map();
  for (const l of leads) for (const id of l.ids) owner.set(id, l);
  const touch = (l, day) => { if (!l.first_day || day < l.first_day) l.first_day = day; if (day > l.last_day) l.last_day = day; };

  // 2. What each producer did with their own leads, day by day.
  for (const d of days) {
    const rows = d.rows || {};
    for (const r of rows.dials || []) {
      const l = owner.get(Number(r.lead_id));
      if (!l) continue;
      if (r.who !== l.producer) { l.others.add(r.who); continue; }
      l.dials += +r.attempts || 1;
      l.talk += +r.talk || 0;
      if (!l.dial_days.includes(d.day)) l.dial_days.push(d.day);
      touch(l, d.day);
    }
    for (const r of rows.contacts || []) {
      const l = owner.get(Number(r.lead_id));
      if (!l) continue;
      if (r.who !== l.producer) { l.others.add(r.who); continue; }
      l.reached = true;
      l.reached_secs += +r.seconds || 0;
      if (r.summary) l.summary = r.summary;
      touch(l, d.day);
    }
    for (const r of rows.quoted || []) {
      const l = owner.get(Number(r.lead_id));
      if (!l) continue;
      if (r.who !== l.producer) { l.others.add(r.who); continue; }
      l.is_quoted = true;
      l.quoted = Math.max(l.quoted, +r.premium || 0);
      touch(l, d.day);
    }
    for (const r of rows.sold_leads || []) {
      const l = owner.get(Number(r.lead_id));
      if (!l) continue;
      if (r.who !== l.producer) { l.others.add(r.who); continue; }
      l.sold = true;
      if (!l.sold_day) l.sold_day = d.day;
      touch(l, d.day);
    }
  }

  const out = leads.map((l) => {
    const status = l.sold ? "sold" : l.is_quoted ? "quoted" : l.reached ? "reached" : l.dials ? "dialed"
      : (l.kind === "create" && l.created) ? "created" : "untouched";
    const { ids, others, phone10, ...rest } = l;
    return { ...rest, quoted: Math.round(l.quoted), lead_ids: [...ids], others: [...others], status };
  });

  // 3. The scoreboard.
  const names = [];
  for (const l of out) if (!names.includes(l.producer)) names.push(l.producer);
  const board = names.map((n) => {
    const mine = out.filter((l) => l.producer === n), create = mine.filter((l) => l.kind === "create");
    return {
      producer: n, leads: mine.length,
      worked: mine.filter((l) => l.dials || l.reached).length,
      dials: mine.reduce((a, l) => a + l.dials, 0),
      reached: mine.filter((l) => l.reached).length,
      talk: mine.reduce((a, l) => a + l.reached_secs, 0),
      quoted: mine.filter((l) => l.is_quoted).length,
      premium_quoted: mine.reduce((a, l) => a + l.quoted, 0),
      sold: mine.filter((l) => l.sold).length,
      to_create: create.length,
      created: create.filter((l) => l.created || l.lead_ids.length).length,
      first_day: mine.map((l) => l.first_day).filter(Boolean).sort()[0] || "",
    };
  });
  const CATS = ["worked", "reached", "quoted", "premium_quoted", "sold", "created"];
  for (const b of board) b.points = 0;
  for (const c of CATS) {
    for (const b of board) {
      if (!(b[c] > 0)) continue;
      const better = board.filter((x) => x[c] > b[c]).length;
      b.points += Math.max(0, 5 - better);
    }
  }
  board.sort((a, b) => b.points - a.points || b.sold - a.sold || b.premium_quoted - a.premium_quoted || b.reached - a.reached);
  out.sort((a, b) => names.indexOf(a.producer) - names.indexOf(b.producer) || (a.kind > b.kind ? -1 : a.kind < b.kind ? 1 : 0) || RANK.indexOf(a.status) - RANK.indexOf(b.status));
  return { leads: out, board, categories: CATS };
}

export async function campaignsGet(request, env, identityOf, key) {
  const me = identityOf(request, env);
  if (!hasBoard(me.email, "campaigns")) return json({ error: "not available" }, 403);
  if (!key) return json({ campaigns: await listCampaigns(env) });
  const campaign = await getJson(env, `${PREFIX}${key}/list.json`);
  if (!campaign) return json({ error: "no such campaign" }, 404);
  const today = localDay();
  const days = [];
  for (const day of daysFrom(campaign.start, today)) {
    const [r, act] = await Promise.all([dayRows(env, day), getJson(env, `live/${day}-leads.json`)]);
    if (!r && !act) continue;
    days.push({ day, src: r ? r.src : "", built_at: r ? r.built_at : "", rows: r ? r.rows : {}, active: (act && act.leads) || [] });
  }
  const t = track(campaign, days);
  const last = days.filter((d) => d.src).slice(-1)[0];
  return json({
    key: campaign.key, title: campaign.title, start: campaign.start, source: campaign.source || "",
    today, as_of: last ? { day: last.day, src: last.src, built_at: last.built_at } : null,
    days_read: days.length, ...t, campaigns: await listCampaigns(env),
  });
}
