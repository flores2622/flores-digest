/* Live contacts, talk time and texts & emails between checkpoints (Frank,
   2026-09-28: "avg talk time, contact rate, and texts and emails should all
   be live as well").

   Everything here reads the same AgencyZoom notes the quotes part already
   downloads (live.js quotedLive), so it costs no extra requests, and every
   pattern comes from the checkpoint (live_basis.contact from live_contact.py,
   live_basis.messages from messages.py) -- never retyped in JS.

   CONTACTS ARE PROVISIONAL. The checkpoint decides a contact from the call
   recording first (live_contact.is_live); the Worker cannot hear it. For a
   dial made since the checkpoint it applies is_live's own order with the
   recording left out -- a producer's note stating contact, a no-contact
   note, an outcome note, TRAQ's voicemail summary, RingCentral's own
   disposition -- and, where nothing is written, how long the leg ran
   (live_basis.contact.provisional_seconds, measured in live_board.py). The
   next checkpoint reads the recordings and settles every one of them. */

const AZ_OFFSET = "-07:00";
export const last10 = s => { const d = String(s || "").replace(/\D/g, ""); return d.length >= 10 ? d.slice(-10) : null; };
// az_corpus.e164: "+1" and the last ten digits -- the match key, not a real E.164 number.
export const e164 = s => { const t = last10(s); return t ? "+1" + t : null; };
export const rxOf = v => (Array.isArray(v) ? new RegExp(v[0], v[1] || "") : new RegExp(v, "i"));
const azMs = s => Date.parse(String(s).trim().replace(" ", "T").slice(0, 19) + AZ_OFFSET);   // note times are Arizona-local

const ENTITIES = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", "#39": "'", nbsp: " " };
function unescapeHtml(s) {
  return s.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e) => {
    const k = e.toLowerCase();
    if (k.startsWith("#x")) return String.fromCodePoint(parseInt(k.slice(2), 16));
    if (k.startsWith("#")) return String.fromCodePoint(parseInt(k.slice(1), 10));
    return ENTITIES[k] ?? m;
  });
}
// live_contact._text
export function noteText(body) {
  let b = String(body || "").replace(/<audio[\s\S]*?<\/audio>/g, " ");
  b = b.replace(/<[^>]+>/g, " ");
  return unescapeHtml(b).replace(/\s+/g, " ").trim();
}

/* ---- contact evidence: live_contact._evidence_into, note by note -------- */

const MEANINGFUL = new Set([null, undefined, "", "comment", "MOVE_STAGE", "Sold"]);
// Compiled once per checkpoint basis, not once per lead.
const compiled = new WeakMap();
const once = (obj, make) => { if (!obj) return {}; let r = compiled.get(obj); if (!r) compiled.set(obj, r = make(obj)); return r; };
const contactRx = c => once(c, contactRx_);
function contactRx_(c) {
  const r = {};
  for (const [k, v] of Object.entries((c || {}).rx || {})) r[k] = rxOf(v);
  return r;
}
function outcomeText(t, R) {                     // live_contact.is_outcome_text
  t = (t || "").trim();
  if (!t || R.NOT_AN_OUTCOME.test(t)) return false;
  if (t.split(/\s+/).length <= 3 && !R.ASSERTS_CONTACT.test(t)) return false;
  return true;
}
const dataCapture = (t, R) => !!t && R.DATA_ONLY.test(t) && !R.CONTACT_VERB.test(t);
function judge(text, R, item) {                  // one producer-written text
  if (R.SCREENER.test(text)) item.scr = true;
  if (R.NEGATIVE.test(text)) item.neg = true;
  else if (!dataCapture(text, R)) {
    if (outcomeText(text, R)) item.out = true;
    if (outcomeText(text, R) && R.ASSERTS_CONTACT.test(text)) item.asr = true;
  }
}

/* Every note on one lead that could decide a contact on `day`, as small
   items {at, by, task, neg, scr, vm, out, asr}. TASK notes are stamped 5 PM
   the day before (live_contact.task_note_day) and carry their author in the
   body, so they have no usable time (`task: true`). */
export function contactItems(notes, day, basis) {
  const R = contactRx(basis.contact);
  if (!R.NEGATIVE) return [];
  const names = new Set(Object.keys(basis.producers || {}));
  const out = [];
  const prevDay = new Date(Date.parse(`${day}T12:00:00Z`) - 86400000).toISOString().slice(0, 10);
  for (const n of notes || []) {
    const t = n.type, cd = String(n.createDate || "");
    const item = { at: cd.slice(0, 19), by: n.createdBy || "" };
    if (t === "TASK") {
      if (!cd.startsWith(prevDay)) continue;
      const raw = noteText(n.body);
      const m = raw.match(R.TASK_COMPLETED_BY);
      if (!m || !names.has(m[1])) continue;
      item.by = m[1]; item.task = true;
      if (R.SCREENER.test(raw)) item.scr = true;
      if (R.NEGATIVE.test(raw)) item.neg = true;
      const body = raw.replace(taskStrip(R), " ").replace(/\s+/g, " ").replace(/^[ .~-]+|[ .~-]+$/g, "");
      if (body) { if (R.SCREENER.test(body)) item.scr = true; if (R.NEGATIVE.test(body)) item.neg = true; }
      if (item.neg || item.scr) out.push(item);
      continue;
    }
    if (!cd.startsWith(day) || !names.has(n.createdBy) || t === "CALL" || !MEANINGFUL.has(t)) continue;
    const text = noteText(n.body);
    if (t === "MOVE_STAGE") {
      const m = text.match(/Comments:\s*(.+)$/);
      const comment = m ? m[1].trim() : "";
      if (comment && !R.SYSTEM.test(comment)) judge(comment, R, item);
    } else {
      if (!text || R.SYSTEM.test(text)) continue;
      if (R.TRAQ_NOTE.test(text)) {               // machine summary: a voicemail tell, never a contact
        if (R.TRAQ_VOICEMAIL.test(text)) item.vm = true;
        if (R.SCREENER.test(text)) item.scr = true;
      } else judge(text, R, item);
    }
    if (item.neg || item.scr || item.vm || item.out || item.asr) out.push(item);
  }
  return out;
}

/* is_live's order with no recording: (bool, basis). `legs` are the dials to
   one number being judged, `items` the evidence on its leads, already
   filtered to this producer and to the notes that can speak for these legs. */
export function provisionalLive(legs, items, c) {
  const talk = legs.reduce((s, l) => s + (l.dur || 0), 0);
  if (talk < (c.min_contact_seconds ?? 5)) return [false, "too short to be a conversation"];
  const noConnect = new Set(c.rc_no_connect || []);
  const res = legs.map(l => String(l.result || "").trim().toLowerCase());
  // Notes win (Frank, 2026-08-18): RingCentral's disposition only speaks
  // where nobody wrote anything, as in live_contact.outcome_bucket.
  if (items.some(i => i.asr)) return [true, "producer note (states contact)"];
  if (items.some(i => i.neg)) return [false, "producer note (no contact)"];
  if (items.some(i => i.out)) return [true, "producer note"];
  if (items.some(i => i.vm)) return [false, "call summary reports a voicemail"];
  if (res.length && res.every(r => noConnect.has(r))) return [false, "RingCentral: did not connect"];
  const longest = Math.max(0, ...legs.map(l => l.dur || 0));
  if (c.provisional_seconds && longest >= c.provisional_seconds) return [true, "duration, until the recording is read"];
  return [false, "no outcome logged yet"];
}

/* ---- inbound: inbound.answered / attribute / personal_dids -------------- */

const PICKUP = new Set(["Park Location", "FindMe", "VoIP Call"]);
export function answeredInbound(recs, names) {
  const users = {};
  for (const r of recs) {
    if (r.direction !== "Outbound") continue;
    const f = r.from || {};
    if (f.phoneNumber && f.name) (users[f.phoneNumber] || (users[f.phoneNumber] = new Set())).add(f.name);
  }
  const out = [];
  for (const r of recs) {
    if (r.direction !== "Inbound" || r.result !== "Accepted") continue;
    let best = null;
    for (const l of r.legs || []) {
      if (l.result !== "Call connected") continue;
      const f = (l.from || {}).name;
      if (!names.has(f) || !PICKUP.has(l.action)) continue;
      if (l.action === "FindMe" && (l.to || {}).name !== f) continue;
      if (!best || (l.duration || 0) > best[1]) best = [f, l.duration || 0];
    }
    if (best) out.push({ id: String(r.id), who: best[0], secs: best[1], num: (r.from || {}).phoneNumber, start: r.startTime });
  }
  return out;
}

/* Contacts and talk time since the checkpoint, per producer: the ADDITIONS
   to the checkpoint's live contacts and to the conversations and seconds
   behind Avg Talk Time (finalize._totals).

     outbound   a number already live adds its seconds; a counted, dropped
                or never-checked number is judged by provisionalLive on the
                legs since the checkpoint (a counted one keeps the seconds it
                already had); an excluded one (service, renewal) adds nothing.
     inbound    a call back to a number dialled today turns that dial live,
                as the checkpoint does; any other answered call-in is a
                conversation for talk time. A number the checkpoint excluded
                stays out, and one nobody has checked counts until one does
                -- the dials rule.

   `evidence` is {last10: {items, leads}} from the lead notes the quotes part
   read; a number with none yet is judged on the call log alone. */
export function contactDeltas(basis, recs, evidence) {
  const c = basis.contact || {};
  const seen = new Set(basis.rc_ids || []);
  const names = new Set(Object.keys(basis.producers || {}));
  const byExt = Object.fromEntries(Object.entries(basis.producers || {}).map(([n, v]) => [String(v.rc_id), n]));
  const ten = k => Object.fromEntries(Object.entries(basis[k] || {}).map(([n, v]) => [n, new Set(v.map(last10))]));
  const counted = ten("counted"), dropped = ten("dropped"), excluded = ten("excluded"), live = ten("live");
  const convo = Object.fromEntries(Object.entries(basis.talk || {}).map(([n, v]) => [n, new Set((v.numbers || []).map(last10))]));
  const out = {}, legs = {}, before = {};
  for (const n of names) { out[n] = { live: 0, conversations: 0, seconds: 0, provisional: [], dialled: [] }; legs[n] = {}; before[n] = {}; }
  for (const r of recs) {
    if (r.direction !== "Outbound") continue;
    const who = byExt[String((r.extension || {}).id || (r.from || {}).extensionId || "")];
    const num = last10((r.to || {}).phoneNumber);
    // A duplicate-lead number adds attempts only (dialDeltas); its person's
    // contact is on the surviving number.
    if (!who || !num || excluded[who].has(num) || dropped[who].has(num)) continue;
    const leg = { id: String(r.id), dur: r.duration || 0, result: r.result, start: r.startTime };
    const into = seen.has(leg.id) ? before : legs;
    (into[who][num] || (into[who][num] = [])).push(leg);
  }
  const people = new Set();                     // one account, one contact
  for (const who of names) {
    out[who].dialled = Object.keys(legs[who]);
    for (const [num, ls] of Object.entries(legs[who])) {
      const secs = ls.reduce((s, l) => s + l.dur, 0);
      if (live[who].has(num)) { out[who].seconds += secs; continue; }
      const ev = (evidence || {})[num] || {};
      const fresh = !counted[who].has(num);
      const first = Math.min(...ls.map(l => Date.parse(l.start)));
      // A counted number was already judged "no contact" on its earlier
      // dials, from its notes; only a note written since this call began can
      // speak for it. A never-checked number gets all of today's notes.
      const items = (ev.items || []).filter(i => i.by === who &&
        (fresh || (!i.task && azMs(i.at) >= first - 60000)));
      const [ok, why] = provisionalLive(ls, items, c);
      if (!ok) continue;
      const lead = (ev.leads || []).slice().sort().join(",");
      if (lead && people.has(`${who}|${lead}`)) continue;
      if (lead) people.add(`${who}|${lead}`);
      const prior = (before[who][num] || []).reduce((s, l) => s + l.dur, 0);
      out[who].live++;
      out[who].conversations++;
      out[who].seconds += secs + prior;
      out[who].provisional.push({ number: num, seconds: secs + prior, basis: why });
      live[who].add(num); convo[who].add(num);
    }
  }
  // inbound.screen's verdicts on today's call-ins as the checkpoint saw
  // them (live_board._inbound_basis); null on an older checkpoint.
  const IB = basis.inbound || null;
  const inSet = (who, k) => new Set(((IB && IB[who]) || {})[k] || []);
  const screenedIn = Object.fromEntries([...names].map(n => [n, inSet(n, "in")]));
  const screenedOut = Object.fromEntries([...names].map(n => [n, inSet(n, "out")]));
  for (const r of answeredInbound(recs, names)) {
    if (seen.has(r.id)) continue;
    const who = r.who, num = last10(r.num);
    if (!num || excluded[who].has(num) || dropped[who].has(num)) continue;
    const callback = counted[who].has(num) || !!legs[who][num] || !!before[who][num];
    // Only a call-in inbound.screen would keep adds talk time: a number the
    // checkpoint already kept or is talking on, a call back to today's
    // dial, or a number the lead notes read since show is a lead's. A
    // number the checkpoint screened out (service, renewal, customer only)
    // or one nobody can place yet waits for the next checkpoint
    // (2026-09-30: the Worker counted every answered call-in).
    const known = callback || convo[who].has(num) || live[who].has(num) || screenedIn[who].has(num);
    if (!known && (screenedOut[who].has(num) || !(((evidence || {})[num] || {}).leads || []).length)) continue;
    out[who].seconds += r.secs;
    if (convo[who].has(num) || live[who].has(num)) continue;       // talking on a row already counted
    convo[who].add(num);
    out[who].conversations++;
    // A same-day call back turns the dial it answers live; a call-in to a
    // number never dialled stays outside the rate.
    if (callback) {
      out[who].live++; live[who].add(num);
      out[who].provisional.push({ number: num, seconds: r.secs, basis: "call back" });
    }
  }
  return out;
}

/* ---- texts & emails: messages.build, carried on from the checkpoint ----- */

const msgRx = m => once(m, m => { const r = {}; for (const [k, v] of Object.entries(m.rx || {})) r[k] = rxOf(v);
  r.ssn_g = new RegExp(r.ssn.source, "g" + r.ssn.flags); r.long_g = new RegExp(r.long_digits.source, "g" + r.long_digits.flags);
  r.code_g = new RegExp(r.code.source, "g" + r.code.flags); r.templates = new Set(m.templates || []); return r; });
const taskStrip = R => once(R.TASK_BOILERPLATE, x => new RegExp(x.source, "gi"));
function redact(t, R) {                          // messages.redact
  t = String(t || "").replace(R.ssn_g, "[number removed]");
  t = t.replace(R.long_g, "[number removed]");
  t = t.replace(R.code_g, (m, g1) => g1 + " [removed] ");
  return t.replace(/  +/g, " ").trim();
}
function msgText(n, R) {                         // messages._text
  const a = n.attr || {};
  const body = n.type === "EMAIL" && a.emailSnippet ? a.emailSnippet : n.body;
  let t = String(body || "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
  t = t.replace(/&nbsp;/g, " ").replace(/&#39;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&");
  return redact(t.replace(R.email_quote, "").trim(), R);
}
const inbound = a => "outbound" in (a || {}) && a.outbound !== null && a.outbound !== undefined && !a.outbound;
function subjectKey(n, first) {
  let s = String((n.attr || {}).emailSubject || n.title || "").replace(/^\s*((re|fw|fwd):\s*)+/i, "").trim();
  if (first && s.toLowerCase().startsWith(first.toLowerCase())) s = s.slice(first.length);
  return s.replace(/^[\s,.:;!\-]+/, "").trim().toLowerCase();
}
const isReplySubject = n => /^\s*(re|fw|fwd):/i.test(String((n.attr || {}).emailSubject || ""));

function windowStart(day, close) {               // messages.window: last business day's close
  const d = new Date(`${day}T12:00:00Z`);
  do d.setUTCDate(d.getUTCDate() - 1); while ([0, 6].includes(d.getUTCDay()));
  return `${d.toISOString().slice(0, 10)} ${close}:00`;
}

/* The message events on one lead from the reply window's start, tagged the
   way messages.build tags them (sent / auto / in / failed / call). Texts are
   redacted before anything is kept. */
export function messageEvents(lead, notes, day, basis, presented) {
  const M = basis.messages;
  if (!M) return [];
  const R = msgRx(M);
  const start = windowStart(day, M.office_close || "17:30");
  const templates = R.templates;
  const first = String(lead.firstname || "").trim();
  const wroteIn = (notes || []).filter(n => n.type === "EMAIL" && inbound(n.attr)).map(n => String(n.createDate || "").slice(0, 19));
  const out = [];
  let prior = null;           // the last message typed to them before the window: whose conversation it is
  for (const n of notes || []) {
    const t = n.type, at = String(n.createDate || "").slice(0, 19);
    if (!["TEXT", "EMAIL", "TEXT-FAILED", "CALL"].includes(t)) continue;
    const a = n.attr || {};
    if (at <= start) {
      // Blank author included: messages.build's partner is the last typed
      // message's author, and a blank one falls to the lead's owner.
      if ((t === "TEXT" && !inbound(a) && !a.triggerRuleId || t === "EMAIL" && !inbound(a)) && (!prior || at > prior.at)) {
        const auto = t === "EMAIL" && templates.has(subjectKey(n, first)) && !(a.attachments || []).length
          && !(isReplySubject(n) && wroteIn.some(w => w < at));
        if (!auto) prior = { at, by: String(n.createdBy || "").trim() };
      }
      continue;
    }
    const ev = { at, type: t, by: String(n.createdBy || "").trim(), text: "" };
    if (t === "CALL") {
      const m = String(n.body || "").match(/Duration:\s*(\d+)/);
      ev.kind = "call"; ev.dur = m ? Number(m[1]) : 0; ev.inbound = inbound(a);
      if (ev.inbound && ev.dur < (M.conversation_seconds || 30)) continue;
    } else {
      ev.text = msgText(n, R);
      if (t === "TEXT-FAILED") ev.kind = "failed";
      else if (inbound(a)) ev.kind = "in";
      else if (t === "TEXT") ev.kind = a.triggerRuleId ? "auto" : "sent";
      else {
        const realReply = isReplySubject(n) && wroteIn.some(w => w < at);
        ev.kind = templates.has(subjectKey(n, first)) && !(a.attachments || []).length && !realReply ? "auto" : "sent";
        ev.subject = String(a.emailSubject || "").trim();
        ev.attachments = (a.attachments || []).length;
        ev.opened = !!a.lastOpenDate;
        ev.bounced = !!a.bounced;
        ev.bounce_reason = String(a.bounceReason || "").trim();
      }
      if (ev.kind === "sent") {
        const b = ev.text.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
        ev.quote = (t === "EMAIL" && ev.attachments > 0) || (presented && presented(b));
      }
    }
    out.push(ev);
  }
  if (prior) out.push({ at: prior.at, kind: "prior", type: "", by: prior.by, text: "" });
  return out;
}

/* A reply run's verdict, messages.build's order: not a producer's
   conversation (counted nowhere), opted out, wrong person (bad contact, no
   reply row), every message an acknowledgement, answered, or waiting. */
function runStatus(r) {
  if (!r) return "none";
  if (!r.listed) return "none";
  if (r.anyOpt) return "optout";
  if (r.anyWrong) return "wrong";
  if (r.allAck) return "ack";
  return r.answered ? "answered" : "open";
}
const RUN_COUNTS = {
  none: {}, wrong: { bad: 1 },
  optout: { replies: 1, optouts: 1 }, ack: { replies: 1, acks: 1 },
  open: { replies: 1, unanswered: 1 }, answered: { replies: 1, answered: 1 },
};
// One more message into a run: all() of the acknowledgements, any() of the
// opt-outs and wrong-person lines, over the messages with text.
function judgeInto(run, text, R) {
  if (!text) return;
  if (R.opt_out.test(text)) run.anyOpt = true;
  if (R.wrong.test(text)) run.anyWrong = true;
  const ack = R.ack.test(text) || (R.ack_short.test(text) && !text.includes("?") && text.split(/\s+/).length <= 6);
  if (!ack) run.allAck = false;
}

/* messages.build's figures for everything that happened since the
   checkpoint: per-producer additions to its counts, new reply rows, updates
   to replies it left waiting, and new quote / bad-contact rows.
   `leads` is {id: {lead, events}} for every lead read since the checkpoint;
   `calls` today's RingCentral dials [{n, by, at, dur}], which answer a text
   the way messages.build's call log does. */
export function messageDeltas(basis, leads, day, calls = []) {
  const M = basis.messages;
  const names = new Set(Object.keys(basis.producers || {}));
  const byAz = Object.fromEntries(Object.entries(basis.producers || {}).map(([n, v]) => [String(v.az_id), n]));
  const R = msgRx(M);
  const close = M.office_close || "17:30";
  const winStart = windowStart(day, close), winEnd = `${day} ${close}:00`;
  const opensMs = azMs(`${day} ${M.office_open || "08:30"}:00`);
  const people = M.people || {};
  const keyOfLead = {};
  for (const [k, p] of Object.entries(people)) for (const id of p.leads || []) keyOfLead[String(id)] = k;

  const groups = {};
  const newest = evs => { let m = ""; for (const e of evs || []) if (e.kind !== "prior" && e.at > m) m = e.at; return m; };
  for (const [id, v] of Object.entries(leads)) {
    const l = v.lead || {};
    const k = keyOfLead[id] || e164(l.phone) || e164(l.secondaryPhone) || `lead:${id}`;
    (groups[k] || (groups[k] = { leads: [], events: [], newest: "" })).leads.push({ id: Number(id), l, v });
    const n = newest(v.events);
    if (n > groups[k].newest) groups[k].newest = n;
  }
  // Nothing newer than the checkpoint read on this person: nothing to add
  // (a dial can still answer a reply it left waiting -- below).
  for (const k of Object.keys(groups)) if (groups[k].newest <= ((people[k] || {}).seen || "") && !(people[k] || {}).open) delete groups[k];
  // A reply the checkpoint left waiting can be answered by a dial alone,
  // with no new note on the lead to get it re-read.
  for (const [k, p] of Object.entries(people))
    if (p.open && !groups[k]) groups[k] = { leads: (p.leads || []).map(id => ({ id: Number(id), l: {}, v: {} })), events: [] };
  for (const [k, g] of Object.entries(groups)) {
    // The same message on two duplicate records is kept from the record
    // messages.build meets first -- the checkpoint's order.
    const order = ((people[k] || {}).leads || []).map(Number);
    const pos = id => { const i = order.indexOf(id); return i < 0 ? order.length : i; };
    g.leads.sort((a, b) => pos(a.id) - pos(b.id));
    for (const x of g.leads) g.events.push(...((x.v || {}).events || []).map(e => ({ ...e, lead_id: x.id })));
  }
  const dialsTo = {};
  for (const c of calls || []) (dialsTo[c.n] || (dialsTo[c.n] = [])).push(c);
  for (const [k, g] of Object.entries(groups)) {
    const nums = new Set([last10(k), ...g.leads.flatMap(x => [last10(x.l.phone), last10(x.l.secondaryPhone)])].filter(Boolean));
    for (const n of nums) for (const c of dialsTo[n] || [])
      g.events.push({ at: c.at, kind: "call", type: "CALL", by: c.by, text: "", dur: c.dur, inbound: false, lead_id: g.leads[0].id });
  }
  const stat = Object.fromEntries([...names].map(n => [n, {}]));
  const bump = (who, k, by = 1) => { if (stat[who]) stat[who][k] = (stat[who][k] || 0) + by; };
  const rows = [], updates = [], quotes = [], bad = [];
  const hhmm = at => at.slice(0, 10) === day ? at.slice(11, 16) : `${at.slice(5, 10)} ${at.slice(11, 16)}`;

  for (const [k, g] of Object.entries(groups)) {
    const cp = people[k] || null;
    const since = cp ? cp.seen || "" : "";
    const sig = new Set(), evs = [];
    for (const e of g.events.sort((a, b) => a.at < b.at ? -1 : a.at > b.at ? 1 : 0)) {
      const s = [e.at.slice(0, 16), e.kind, e.type, (e.text || "").slice(0, 80), e.by].join("|");
      if (!sig.has(s)) { sig.add(s); evs.push(e); }
    }
    const fresh = evs.filter(e => e.at > since && e.kind !== "prior");
    if (!fresh.length) continue;
    const l0 = (g.leads[0] || {}).l || {};
    const owner = (cp && cp.owner) || g.leads.map(x => byAz[String(x.l.assignedTo)]).find(Boolean) || null;
    const name = (cp && cp.name) || [String(l0.firstname || "").trim(), String(l0.lastname || "").trim()].filter(Boolean).join(" ") || "(no name)";
    const leadId = cp && cp.leads && cp.leads.length ? cp.leads[0] : (g.leads[0] || {}).id;
    const priors = evs.filter(e => e.kind === "prior").sort((a, b) => (a.at < b.at ? 1 : -1));
    let lastSender = cp ? cp.last_sender : null;
    if (!cp) {
      // messages.build: whoever typed the last message before, blank -> the owner.
      const typed = evs.filter(e => e.kind === "sent" && e.at <= since);
      lastSender = typed.length ? typed[typed.length - 1].by || null : priors.length ? priors[0].by || null : null;
    }
    const sentBy = new Set(cp ? cp.sent_by : []), wrote = new Set(cp ? cp.wrote_back : []);
    // The wait still running: the checkpoint's (cp.run, messages.build's
    // own state for the run nothing had answered) or one this refresh
    // opened. messages.build groups EVERY message until an answer into one
    // row and judges it over all of them -- an "ok" then a question is one
    // wait, from the "ok" (2026-09-30) -- so each message joins the run and
    // it is re-judged, its counts moved from what it was to what it is.
    let run = null;
    if (cp && cp.run) {
      const r = cp.run;
      run = { cp: true, key: { lead_id: r.lead_id, at: r.at }, who: r.who, listed: !!r.listed, startMs: Date.parse(r.start),
        lead_id: r.lead_id, at: r.at, channel: r.channel || "text", messages: r.messages || 1, said: r.said || "",
        allAck: !!r.all_ack, anyOpt: !!r.any_optout, anyWrong: !!r.any_wrong, answered: null, added: 0, addedSaid: [] };
    } else if (cp && cp.open) {
      // A checkpoint built before `run` was handed over: only the reply it
      // left waiting is known, and messages are added to it.
      const o = cp.open;
      run = { cp: true, legacy: true, key: { lead_id: o.lead_id, at: o.at }, who: o.who, listed: true, startMs: Date.parse(o.start),
        lead_id: o.lead_id, at: o.at, channel: "text", messages: 1, said: "",
        allAck: false, anyOpt: false, anyWrong: false, answered: null, added: 0, addedSaid: [] };
    }
    if (run) run.was = runStatus(run);
    const dayEnd = `${day} 23:59:00`;            // messages.build's day_end
    const touchEnd = t => azMs(t.at) + (t.dur || 0) * 1000;
    // Counts follow the run's verdict: moved from what it was counted as to
    // what it is now (a new run was counted as nothing).
    const recount = (r, from, to) => {
      if (from === to) return;
      for (const [k, v] of Object.entries(RUN_COUNTS[from] || {})) bump(r.who, k, -v);
      for (const [k, v] of Object.entries(RUN_COUNTS[to] || {})) bump(r.who, k, v);
    };
    const rowOf = (r, status) => ({ who: r.who, lead: name, lead_id: r.lead_id, day, at: r.at, channel: r.channel,
      said: r.said.slice(0, 300), messages: r.messages, optout: status === "optout", ack: status === "ack",
      answered_by: r.answered ? r.answered.by : null, via: r.answered ? r.answered.via : null,
      minutes: r.answered ? r.answered.minutes : null });
    const badOf = r => ({ who: r.who, lead: name, lead_id: r.lead_id, day, channel: r.channel,
      reason: "wrong person (the lead said so): " + r.said.slice(0, 80) });
    const close = () => {
      if (!run) return;
      const r = run, now = runStatus(r);
      run = null;
      if (!r.cp) {
        recount(r, "none", now);
        if (now === "wrong") bad.push(badOf(r));
        else if (now !== "none") rows.push(rowOf(r, now));
        return;
      }
      recount(r, r.was, now);
      if (r.legacy) {
        if (r.answered || r.added)
          updates.push({ ...r.key, ...(r.answered ? { answered_by: r.answered.by, via: r.answered.via, minutes: r.answered.minutes } : {}),
            ...(r.added ? { add_messages: r.added, add_said: r.addedSaid.join(" / ") } : {}) });
        return;
      }
      if (now === r.was && !r.added && !r.answered) return;
      updates.push({ ...r.key, was: r.was, status: now, add_messages: r.added, add_said: r.addedSaid.join(" / "),
        row: now === "wrong" || now === "none" ? null : rowOf(r, now), bad: now === "wrong" ? badOf(r) : null });
    };
    // A touch after the run began answers it (messages.build's `ans`) and
    // ends it; only a wait still open is credited as answered.
    const answer = (t, atMs) => {
      if (runStatus(run) === "open") {
        const clock = Math.max(run.startMs, opensMs);
        run.answered = { by: t.by || null, via: { TEXT: "text", EMAIL: "email", CALL: "call" }[t.type] || t.type,
          minutes: Math.max(0, Math.floor((atMs - clock) / 60000)) };
      }
      close();
    };
    for (const e of fresh) {
      const ms = azMs(e.at), today = e.at.slice(0, 10) === day;
      const credit = names.has(e.by) ? e.by : owner;
      if (today && e.kind === "sent" && names.has(e.by)) {
        bump(e.by, e.type === "TEXT" ? "texts" : "emails");
        if (!sentBy.has(e.by)) { sentBy.add(e.by); bump(e.by, "leads"); }
        if (e.quote) {
          bump(e.by, "quotes"); if (e.type === "EMAIL" && e.opened) bump(e.by, "quotes_opened");
          quotes.push({ who: e.by, lead: name, lead_id: e.lead_id, at: e.at.slice(11, 16), day,
            channel: e.type === "EMAIL" ? "email" : "text", subject: e.subject || "", opened: e.type === "EMAIL" ? !!e.opened : null });
        }
      } else if (today && e.kind === "auto" && names.has(credit)) {
        bump(credit, e.type === "TEXT" ? "auto_texts" : "auto_emails");
      }
      if (today && names.has(credit) && (e.kind === "failed" || e.bounced)) {
        bump(credit, "bad");
        bad.push({ who: credit, lead: name, lead_id: e.lead_id, day, channel: e.type === "EMAIL" ? "email" : "text",
          reason: e.bounce_reason || (e.kind === "failed" ? "text failed" : "bounced") });
      }
      if (e.kind === "sent" || e.kind === "call") {
        if (run && ms >= run.startMs && e.at <= dayEnd) answer(e, ms);
        // Whose conversation it is: the last one typed, and a blank author
        // falls to the lead's owner (messages.build's `partner`).
        if (e.kind === "sent") lastSender = e.by || null;
        continue;
      }
      if (e.kind !== "in") continue;
      if (e.at <= dayEnd) for (const w of sentBy) if (!wrote.has(w)) { wrote.add(w); bump(w, "wrote_back"); }
      if (!(e.at > winStart && e.at <= winEnd)) continue;
      const text = e.text || "";
      if (run) {                                 // the same wait, one more message
        run.messages++;
        if (run.cp) run.added++;
        if (text) { run.said = [run.said, text].filter(Boolean).join(" / ").slice(0, 300); if (run.cp) run.addedSaid.push(text); }
        judgeInto(run, text, R);
        continue;
      }
      const partner = lastSender || owner;
      run = { cp: false, who: partner, listed: names.has(partner), startMs: ms, lead_id: e.lead_id, at: hhmm(e.at),
        channel: e.type === "EMAIL" ? "email" : "text", messages: 1, said: text.slice(0, 300),
        allAck: true, anyOpt: false, anyWrong: false, answered: null, added: 0, addedSaid: [] };
      judgeInto(run, text, R);
      // A call or message still going when this arrived answers it
      // (messages.build: the first touch that ends at or after it).
      const t = evs.find(x => (x.kind === "call" || x.kind === "sent") && x.at <= dayEnd && azMs(x.at) <= ms && touchEnd(x) >= ms);
      if (t) answer(t, ms);
    }
    close();
  }
  return { producers: stat, replies: rows, updates, quotes, bad_contact: bad };
}
