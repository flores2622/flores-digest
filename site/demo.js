/* Demo mode (Frank, 2026-10-20: "can we make a demo mode for me? I want to
 * present this to other agents at an event ... show them the coaching and
 * stat tracking aspect of it all, as well as service. No agency zoom
 * transitions, workflows, audits, lead scrubs, or that stuff, the rotation
 * staying is fine").
 *
 * Demo mode is a switch on the board for the people holding staff.json's
 * `demo` board key (Frank and the ops team). While it is on, this Worker:
 *
 *   1. MASKS every customer in every JSON answer it serves -- the day
 *      documents, the checkpoints and live figures, the Service, Commercial
 *      and Renewals documents, the lead index behind the search, the Sales
 *      sheet, the rotation log, the sticky notes, and what Apollo's tools
 *      read for the chat. A person's name becomes a made-up one, the same
 *      made-up one wherever that name appears (a hash of the real name picks
 *      it, so a lead reads the same on the Digest, in the transcript, on the
 *      Service Center and in the search); a phone number keeps its area code
 *      and formatting but its last seven digits become 555-xxxx (by the same
 *      hash, so rows keyed by number still line up); an email outside the
 *      agency becomes demo…@example.com. Staff are never masked. The figures
 *      themselves -- dials, premium, scores, every tier -- are untouched: a
 *      demo shows the real numbers behind made-up people.
 *
 *   2. HIDES the pages that are AgencyZoom's transition and the agency's own
 *      housekeeping: the CRM (Tasks, Leads, Lists, Workflows), Campaigns, the
 *      Lead Scrub, CRM Hygiene, Minimums & Goal, the Commission tab, Apollo's
 *      Doubts and Apollo's usage. Each answers 403 in demo mode, and the page
 *      already keeps a page out of the menu when its Worker route refuses, so
 *      nothing on the page had to learn the list. The Rotation stays.
 *
 * The switch is a cookie (`pantheon_demo=1`) the page sets from Settings and
 * reloads on, honoured only for a login with the `demo` key. A plain reload
 * with the cookie gone is the real board again. Nothing is written anywhere;
 * nothing in R2 changes; the nightly never sees it.
 *
 * What it cannot mask: the recordings themselves (a customer says their own
 * name on the call) and a name typed by hand into a comment or a sticky note
 * that is not also on the document being served. The transcript text IS
 * masked, so the player's words and the sound can disagree in a demo.
 *
 * `node --test site/demo.test.mjs` runs it over a made-up document.
 */

import { PEOPLE, AGENCY, hasBoard } from "./staff.js";

export const DEMO_COOKIE = "pantheon_demo";

/* ---- the switch --------------------------------------------------------- */

function cookieValue(request, name) {
  const raw = request.headers.get("Cookie") || "";
  for (const part of raw.split(";")) {
    const [k, ...v] = part.trim().split("=");
    if (k === name) return v.join("=");
  }
  return null;
}

/** May this login turn demo mode on at all (staff.json's `demo` board key)? */
export function demoAllowed(email) {
  return hasBoard(email, "demo");
}

/** Is demo mode on for this request: the cookie, from a login that may. */
export function demoOn(request, email) {
  return demoAllowed(email) && cookieValue(request, DEMO_COOKIE) === "1";
}

/* The routes demo mode refuses outright (403): AgencyZoom's transition (the
 * CRM), the ops team's housekeeping (campaigns, the lead scrub, CRM hygiene,
 * minimums and the commission schedule) and Apollo's own audit pages. The
 * page hides each one when its route refuses, exactly as it does for a login
 * without the key. */
const BLOCKED = new Set(["crm", "scrub", "hygiene", "campaigns", "cardreview", "folio-goals", "commission"]);
/* Answers never masked: who is looking, their settings, the Training decks,
 * the lead-source list (the Digest's rows carry the same source names
 * unmasked), the Sales sheet's dropdowns and Role Play, whose prospects are
 * made up already. */
export function skipInDemo(parts) {
  if (["me", "prefs", "training", "leadsources", "roleplay"].includes(parts[1])) return true;
  if (parts[1] === "saleslog" && parts[2] === "options") return true;
  return false;
}
export function blockedInDemo(parts) {
  if (BLOCKED.has(parts[1])) return true;
  if (parts[1] === "coeus" && parts[2] === "usage") return true;
  return false;
}

/* ---- made-up names ------------------------------------------------------- */

const FIRST = [
  "Mateo", "Sofia", "Daniel", "Valeria", "Lucas", "Camila", "Diego", "Isabella", "Gabriel", "Elena",
  "Adrian", "Natalia", "Sebastian", "Lucia", "Emilio", "Renata", "Tomas", "Ximena", "Julian", "Paula",
  "Andres", "Mariana", "Nicolas", "Daniela", "Rafael", "Fernanda", "Santiago", "Regina", "Alejandro", "Carla",
  "Oliver", "Emma", "Noah", "Ava", "Liam", "Mia", "Ethan", "Chloe", "Owen", "Zoe",
  "Henry", "Lily", "Leo", "Nora", "Jack", "Ruby", "Caleb", "Hazel", "Miles", "Ivy",
  "Wyatt", "Stella", "Levi", "Violet", "Isaac", "Aurora", "Eli", "Luna", "Theo", "Clara",
  "Marcus", "Simone", "Andre", "Jasmine", "Darius", "Imani", "Malik", "Nia", "Jerome", "Keisha",
  "Kenji", "Hana", "Ravi", "Priya", "Arjun", "Mei", "Omar", "Layla", "Yusuf", "Amira",
  "Walter", "Dorothy", "Harold", "Mildred", "Eugene", "Beverly", "Ralph", "Gloria", "Leonard", "Irene",
  "Ramon", "Beatriz", "Ernesto", "Graciela", "Ignacio", "Marisol", "Rodrigo", "Pilar", "Esteban", "Rocio",
  "Trevor", "Megan", "Brandon", "Kayla", "Tyler", "Brooke", "Dustin", "Haley", "Colin", "Paige",
  "Felix", "Greta", "Hugo", "Ingrid", "Anton", "Freya", "Bruno", "Liv", "Otto", "Sigrid",
];
const LAST = [
  "Reyes", "Navarro", "Castillo", "Herrera", "Delgado", "Serrano", "Vargas", "Molina", "Rojas", "Salazar",
  "Ibarra", "Montoya", "Cordova", "Escobar", "Fuentes", "Guerrero", "Lozano", "Medina", "Orozco", "Pacheco",
  "Quintero", "Rosales", "Sandoval", "Trujillo", "Urbina", "Valdez", "Zamora", "Aguirre", "Barrera", "Cabrera",
  "Bennett", "Carver", "Dawson", "Ellison", "Fletcher", "Gardner", "Hawkins", "Ingram", "Jennings", "Keller",
  "Lambert", "Mercer", "Norwood", "Osborne", "Parrish", "Quigley", "Ramsey", "Sutton", "Thornton", "Underwood",
  "Vickers", "Whitaker", "Yates", "Ashford", "Blackwell", "Calloway", "Draper", "Easton", "Fairbanks", "Granger",
  "Holloway", "Irvine", "Jarvis", "Kimball", "Lockhart", "Marlowe", "Nash", "Oakley", "Pemberton", "Radford",
  "Sheridan", "Tilden", "Upton", "Vance", "Wakefield", "Yardley", "Abbott", "Briggs", "Coleman", "Dunbar",
  "Okafor", "Mensah", "Adeyemi", "Nakamura", "Tanaka", "Patel", "Sharma", "Haddad", "Farouk", "Nassar",
  "Lindqvist", "Berger", "Novak", "Petrov", "Kowalski", "Meyer", "Fischer", "Weber", "Schulz", "Hoffmann",
];
const BIZ_ADJ = ["Blue Mesa", "Red Rock", "Sunrise", "Canyon", "Saguaro", "Copper", "Silver Creek", "High Desert", "Palo Verde", "Ironwood", "Mesquite", "Painted Sky", "Dry River", "North Star", "Four Peaks", "Juniper"];
const BIZ_NOUN = ["Builders", "Landscaping", "Dental", "Logistics", "Auto Care", "Roofing", "Catering", "Fitness", "Plumbing", "Floral", "Cleaning", "Transport", "Welding", "Bakery", "Electric", "Tires"];

/* A short, stable hash (FNV-1a, 32-bit) of a normalised string: the same
 * real name gives the same made-up one on every answer, in every file. */
function fnv(s) {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
  return h >>> 0;
}
const norm = (s) => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const pick = (list, s, salt) => list[fnv(salt + norm(s)) % list.length];

/* Words that look like a first name but are not one to replace on their own
 * in free text: the staff (and how transcripts mishear them), the agency and
 * its carriers, the board's own names, calendar words, and English / Spanish
 * words that are also given names. A full name ("Will Turner") still masks
 * whole; only the bare word is left alone. */
const STOP_WORDS = [
  "farmers", "foremost", "bristol", "west", "kraft", "lake", "apollo", "athena", "cerberus", "coeus", "pantheon", "elysium",
  "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december",
  "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
  "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
  "lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo",
  "will", "bill", "mark", "rose", "grace", "hope", "faith", "guy", "pat", "art", "sol", "luz", "angel", "cruz", "paz", "rio", "rey",
  "don", "dona", "max", "van", "von", "del", "los", "las", "san", "santa", "chase", "smart", "alpha", "capital", "desert", "home",
  "auto", "life", "cross", "sell", "mesa", "sun", "star", "summer", "winter", "autumn", "dawn", "joy", "lane", "page", "park",
  "ray", "rich", "sky", "storm", "wade", "ward", "chance", "christian", "dean", "earl", "grant", "king", "long", "major", "miles",
  "pearl", "prince", "rob", "rusty", "sandy", "flor", "rosa", "blanca", "cielo", "luna", "reina", "paloma", "victoria", "mercedes",
  "america", "arizona", "yuma", "phoenix", "tucson", "mexico", "texas", "california", "progressive", "geico", "allstate", "liberty",
  "mutual", "state", "farm", "nationwide", "travelers", "root", "general", "direct", "national", "american", "family", "united",
  "ok", "okay", "yes", "no", "si", "hi", "hello", "hola", "bueno", "gracias", "thanks", "thank", "please", "por", "favor",
];
function stopWords() {
  const set = new Set(STOP_WORDS);
  for (const p of PEOPLE) {
    for (const tok of String(p.name || "").split(/\s+/)) if (tok) set.add(norm(tok));
    for (const h of p.heard_as || []) set.add(norm(h));
  }
  for (const k of ["name", "short_name", "carrier", "also_known_as", "misheard_as", "place"]) {
    for (const tok of String(AGENCY[k] || "").split(/[\s,]+/)) if (tok) set.add(norm(tok));
  }
  for (const c of AGENCY.carriers_spoken || []) for (const tok of String(c).split(/\s+/)) set.add(norm(tok));
  return set;
}
const STOP = stopWords();
const STAFF_FULL = new Set(PEOPLE.map((p) => norm(p.name).replace(/\s+/g, " ")));
const STAFF_FIRST = new Set(PEOPLE.map((p) => norm(String(p.name).split(/\s+/)[0])));

const BIZ_WORDS = new Set(["inc", "inc.", "llc", "l.l.c.", "l.l.c", "corp", "corp.", "co", "co.", "ltd", "ltd.", "llp", "pllc", "dba", "company",
  "trust", "storage", "services", "service", "group", "insurance", "church", "farms", "farm", "market", "shop", "restaurant", "center", "centre",
  "construction", "enterprises", "properties", "realty", "solutions", "&", "and", "of", "the", "bank", "credit", "union", "school", "district",
  "city", "county", "state", "department", "dept", "office", "clinic", "hospital", "motors", "auto", "tire", "tires", "cafe", "grill", "taqueria"]);

/* Tokens of a value: runs of letters (a hyphen inside is part of the word;
 * an apostrophe is not, so "Jill's" is the word Jill and "O'Brien" two words
 * that the full-name match joins back up), by position. */
const WORD = /\p{L}[\p{L}\-]*/gu;
const words = (s) => Array.from(String(s).matchAll(WORD), (m) => ({ t: m[0], i: m.index, e: m.index + m[0].length }));
const keyOf = (toks) => toks.map((t) => norm(t.t)).join(" ");

/** Is this name value a person (first + surname(s)) rather than a business? */
function looksLikePerson(toks, raw) {
  if (toks.length < 1 || toks.length > 4) return false;
  if (/\d|[@#$%]/.test(raw)) return false;
  for (const t of toks) if (BIZ_WORDS.has(norm(t.t))) return false;
  // the words must be all of the value (a value like "El Centro Ca - 1760..." is not a name)
  const joined = toks.map((t) => t.t).join(" ");
  if (norm(joined).replace(/[\s,.]/g, "") !== norm(raw).replace(/[\s,.]/g, "")) return false;
  return true;
}

const fakeFirst = (first) => pick(FIRST, first, "f:");
const fakeLast = (last) => pick(LAST, last, "l:");
function fakeBusiness(raw) {
  const m = /,?\s*((?:inc|llc|l\.l\.c|corp|ltd|llp|pllc|co)\.?)$/i.exec(raw.trim());   // keep an "LLC" / "Inc." ending
  const suffix = m ? " " + m[1] : "";
  return `${pick(BIZ_ADJ, raw, "ba:")} ${pick(BIZ_NOUN, raw, "bn:")}${suffix}`;
}
const caseLike = (orig, fake) => /^[^a-z]*$/.test(orig) && /[A-Z]/.test(orig) && orig.length > 1 ? fake.toUpperCase() : fake;

/* ---- phone numbers and emails -------------------------------------------- */

const PHONE = /(?<!\d)(?:\+52\d{10}|\+?1?[ .-]?\(?\d{3}\)?[ .-]?\d{3}[ .-]?\d{4})(?!\d)/g;
const PHONE_KEY = /^\+?\d{10,13}$/;
function fakePhone(match) {
  const digits = match.replace(/\D/g, "");
  const local = String(fnv("p:" + digits.slice(-10)) % 10000).padStart(4, "0");
  const repl = "555" + local;   // the last seven digits: a 555 exchange and a line from the hash
  let out = "", k = 0, n = 0;
  const total = digits.length;
  for (const ch of match) {
    if (/\d/.test(ch)) { n++; out += n > total - 7 ? repl[k++] : ch; }
    else out += ch;
  }
  return out;
}
const EMAIL = /[\w.+-]+@[\w-]+(?:\.[\w-]+)+/g;
const AGENCY_DOMAINS = new Set([...PEOPLE.map((p) => String(p.email || "").split("@")[1]), String(AGENCY.contact || "").split("@")[1], String(AGENCY.sender || "").split("@")[1]].filter(Boolean).map((d) => d.toLowerCase()));
function fakeEmail(m) {
  const dom = m.split("@")[1].toLowerCase();
  if (AGENCY_DOMAINS.has(dom)) return m;
  return `demo${String(fnv("e:" + m.toLowerCase()) % 10000).padStart(4, "0")}@example.com`;
}
const LAST4_KEYS = new Set(["last4"]);

/* ---- the masking --------------------------------------------------------- */

/* Keys whose string value is a customer's or lead's name. The staff are
 * never masked, so a staff name under one of these keys is left alone. */
const NAME_KEYS = new Set(["lead", "lead_name", "name", "record", "customer", "client", "client_name", "caller", "l",
  "holder", "contact", "household_name", "person", "from_name", "to_name", "insured", "prospect", "cust"]);
const SOURCE_KEYS = new Set(["leadsrc", "source", "lead_source"]);
/* "<First> (lead):" / "<First> (customer):" -- how a transcript labels the other voice. */
const SPEAKER = /(\p{L}[\p{L}'’\-]*) \((?:lead|customer)\)/gu;

/** Does a value that is not a person's name read as a business or a place
 * (two words or more, no label in brackets)? "Speaker 2" and "Edgar (lead)"
 * are neither. */
const looksLikeBusiness = (toks, raw) => !/[()]/.test(raw) && (toks.length >= 2 || /\d/.test(raw) || BIZ_WORDS.has(norm(toks[0].t)));

export function demoize(value) {
  const full = new Map();     // "jose lugo" -> "Daniel Navarro"
  const first = new Map();    // "jose" -> "Daniel"
  const biz = new Map();      // a business's whole value -> its made-up name
  const realFull = new Set(); // every person's key, so no made-up name lands on a real one

  function register(raw) {
    if (typeof raw !== "string") return;
    const s = raw.trim();
    if (!s || s.length > 80) return;
    const toks = words(s);
    if (!toks.length) return;
    const key = keyOf(toks);
    if (STAFF_FULL.has(key) || (toks.length === 1 && STAFF_FIRST.has(key))) return;
    if (!looksLikePerson(toks, s)) { if (looksLikeBusiness(toks, s) && !biz.has(s)) biz.set(s, fakeBusiness(s)); return; }
    const f = norm(toks[0].t);
    // a bare first name is replaced in free text only when it is unmistakably one
    const firstOk = f.length >= 3 && !STOP.has(f);
    if (toks.length === 1) { if (firstOk && !first.has(f)) first.set(f, fakeFirst(f)); return; }
    if (firstOk && !first.has(f)) first.set(f, fakeFirst(f));
    realFull.add(key);
    if (!full.has(key)) full.set(key, fakeFull(f, keyOf(toks.slice(1))));
  }
  function fakeFull(f, lastKey) {
    const ff = fakeFirst(f);
    let i = fnv("l:" + lastKey) % LAST.length;
    for (let tries = 0; tries < LAST.length; tries++, i = (i + 1) % LAST.length) {
      const name = `${ff} ${LAST[i]}`;
      if (!realFull.has(norm(name))) return name;
    }
    return `${ff} ${LAST[i]}`;
  }

  // pass 1: who is on this document
  (function collect(o, key) {
    if (Array.isArray(o)) { for (const v of o) collect(v, key); return; }
    if (o && typeof o === "object") { for (const [k, v] of Object.entries(o)) collect(v, k); return; }
    if (typeof o !== "string") return;
    if (key && NAME_KEYS.has(key)) register(o);
    // a center-of-influence source names its person ("Fernando Ochoa @ Alo", "Name at Company")
    if (key && SOURCE_KEYS.has(key)) { const m = /^(\p{L}[\p{L}'’\-]*(?: \p{L}[\p{L}'’\-]*){1,3})\s+(?:@|at)\s/u.exec(o); if (m) register(m[1]); }
    if (o.length > 8) for (const m of o.matchAll(SPEAKER)) register(m[1]);
  })(value, "");
  // a made-up full name must not be a real one on the same document; the
  // register pass could not know the names still to come, so settle them now
  for (const [k, v] of full) if (realFull.has(norm(v)) && norm(v) !== k) full.set(k, fakeFull(k.split(" ")[0], k.split(" ").slice(1).join(" ") + "'"));
  const bizLong = Array.from(biz.keys()).filter((b) => b.length >= 6).slice(0, 2000);

  function text(s) {
    if (s.length < 2) return s;
    const trimmed = s.trim();
    if (biz.has(trimmed)) return s.replace(trimmed, biz.get(trimmed));
    if (s.length > 20) for (const b of bizLong) if (s.includes(b)) s = s.split(b).join(biz.get(b));
    const toks = words(s);
    let out = "", at = 0;
    for (let i = 0; i < toks.length;) {
      let hit = null, n = 0;
      for (n = Math.min(4, toks.length - i); n >= 2; n--) {
        // the words of a full name sit next to each other, with only spaces (or an apostrophe) between
        let contiguous = true;
        for (let j = i + 1; j < i + n; j++) if (!/^[\s'’]+$/.test(s.slice(toks[j - 1].e, toks[j].i))) { contiguous = false; break; }
        if (!contiguous) continue;
        const k = keyOf(toks.slice(i, i + n));
        if (full.has(k)) { hit = full.get(k); break; }
      }
      if (!hit) {
        n = 1;
        const t = toks[i], k = norm(t.t);
        if (first.has(k) && /^\p{Lu}/u.test(t.t)) hit = first.get(k);
      }
      if (hit) {
        const a = toks[i].i, b = toks[i + n - 1].e;
        out += s.slice(at, a) + caseLike(s.slice(a, b), hit);
        at = b; i += n;
      } else i++;
    }
    out += s.slice(at);
    return out.replace(PHONE, fakePhone).replace(EMAIL, fakeEmail);
  }

  function key(k) {
    if (PHONE_KEY.test(k)) return fakePhone(k);
    return k;
  }

  // pass 2: the same document with every person made up
  return (function walk(o, k) {
    if (Array.isArray(o)) return o.map((v) => walk(v, k));
    if (o && typeof o === "object") {
      const out = {};
      for (const [kk, v] of Object.entries(o)) out[key(kk)] = walk(v, kk);
      return out;
    }
    if (typeof o !== "string") return o;
    if (k && LAST4_KEYS.has(k) && /^\d{4}$/.test(o)) return String(fnv("p4:" + o) % 10000).padStart(4, "0");
    return text(o);
  })(value, "");
}

/** A JSON Response, masked; anything else (audio, a non-200, an error) as is. */
export async function demoResponse(res) {
  if (!res || res.status !== 200) return res;
  const type = res.headers.get("content-type") || "";
  if (!type.includes("application/json")) return res;
  let body;
  try { body = await res.json(); } catch (_) { return res; }
  const headers = new Headers(res.headers);
  headers.set("cache-control", "no-store");
  headers.set("x-pantheon-demo", "1");
  return new Response(JSON.stringify(demoize(body)), { status: 200, headers });
}
