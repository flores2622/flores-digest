/* The agency's people for the Worker -- staff.json, through site/staff_data.js
 * (written by `python3 staff.py --write-js`; never edit that by hand). Who is a
 * producer, the first name the board greets someone by, who may log sales for
 * whom, and every "who may see this" list (the `board` keys, staff.py) come
 * from here and nowhere else. Emails are compared lower-cased, as Cloudflare
 * Access reports them. */
import STAFF from "./staff_data.js";

const lower = (s) => String(s || "").toLowerCase();
const ACTIVE = STAFF.people.filter((p) => (p.status || "active") === "active");
const firstOf = (p) => p.name.split(" ")[0];

/** producer email -> full name, in staff.json's order. */
export const PRODUCER_EMAILS = Object.fromEntries(
  ACTIVE.filter((p) => p.producer && p.email).map((p) => [lower(p.email), p.name]));
export const PRODUCER_NAMES = ACTIVE.filter((p) => p.producer).map((p) => p.name);

/** everyone else signed in -> the first name the board greets them by. */
export const STAFF_FIRST_NAMES = Object.fromEntries(
  ACTIVE.filter((p) => !p.producer && p.email).map((p) => [lower(p.email), firstOf(p)]));

/** non-producers whose sales go on the Sales sheet (Amanda). */
export const SALES_SHEET_NAMES = ACTIVE.filter((p) => (p.tags || []).includes("sales_sheet")).map((p) => p.name);

/** producers who log sales for each other: one email list per sales_team. */
export const SALES_TEAMS = Object.values(ACTIVE.reduce((acc, p) => {
  if (p.sales_team && p.email) (acc[p.sales_team] = acc[p.sales_team] || []).push(lower(p.email));
  return acc;
}, {}));

/** emails of the active people holding board key `key`. */
export function boardEmails(key) {
  return ACTIVE.filter((p) => p.email && (p.board || []).includes(key)).map((p) => lower(p.email));
}
export function hasBoard(email, key) {
  return !!email && boardEmails(key).includes(lower(email));
}

export const ROTATION = STAFF.rotation;
/** The agency itself (staff.json `agency`): name, short_name, carrier, place, sender, contact. */
export const AGENCY = STAFF.agency || {};
export const COMMISSION_UNITS = STAFF.commission_units;
/** Frank's commission schedules and additional pay (staff.json `commission`). */
export const COMMISSION = STAFF.commission || {};

/* ---- the agency's clock (staff.json agency.timezone) -----------------------
   Every day boundary and clock time the Worker works out goes through these,
   so nothing subtracts "7 hours": an agency in a zone with daylight saving
   gets the right day on both sides of the change. The Python side is
   staff.py's TZ / today / local_date; keep the two in step. */
export const TZ = (STAFF.agency || {}).timezone || "America/Phoenix";
const PARTS = new Intl.DateTimeFormat("en-US", { timeZone: TZ, hourCycle: "h23", year: "numeric", month: "2-digit",
  day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", weekday: "short" });
const DOW = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
/** The agency's wall clock at an instant: {y, m, d, h, min, s, dow} (m 1-12, dow 0 = Sunday). */
export function localParts(ms = Date.now()) {
  const o = {};
  for (const p of PARTS.formatToParts(new Date(ms))) o[p.type] = p.value;
  return { y: +o.year, m: +o.month, d: +o.day, h: +o.hour % 24, min: +o.minute, s: +o.second, dow: DOW[o.weekday] };
}
const pad = n => String(n).padStart(2, "0");
/** The agency's calendar date of an instant, "YYYY-MM-DD". */
export function localDay(ms = Date.now()) { const p = localParts(ms); return `${p.y}-${pad(p.m)}-${pad(p.d)}`; }
/** The agency's wall-clock text of an instant, "YYYY-MM-DD HH:MM:SS". */
export function localStr(ms = Date.now()) { const p = localParts(ms); return `${localDay(ms)} ${pad(p.h)}:${pad(p.min)}:${pad(p.s)}`; }
/** The zone's offset from UTC at an instant, in ms (Arizona: -7 h). */
export function tzOffsetMs(ms = Date.now()) {
  const p = localParts(ms);
  return Date.UTC(p.y, p.m - 1, p.d, p.h, p.min, p.s) - Math.floor(ms / 1000) * 1000;
}
/** The same offset as "-07:00". */
export function tzOffsetStr(ms = Date.now()) {
  const o = Math.round(tzOffsetMs(ms) / 60000), a = Math.abs(o);
  return `${o < 0 ? "-" : "+"}${pad(Math.floor(a / 60))}:${pad(a % 60)}`;
}
/** The instant (ms) of a wall-clock time in the agency's zone. */
export function localToUtcMs(y, m, d, h = 0, min = 0, s = 0) {
  const guess = Date.UTC(y, m - 1, d, h, min, s);
  const once = guess - tzOffsetMs(guess);
  return guess - tzOffsetMs(once);
}
/** "YYYY-MM-DD HH:MM:SS" (or ISO without a zone) on the agency's clock -> the instant (ms); NaN when it does not parse. */
export function localTextMs(text) {
  const m = /^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::(\d{2}))?/.exec(String(text || "").trim());
  return m ? localToUtcMs(+m[1], +m[2], +m[3], +m[4], +m[5], +(m[6] || 0)) : NaN;
}
/** Local midnight starting a "YYYY-MM-DD" day, as an instant (ms). */
export function dayStartMs(day) { const [y, m, d] = day.split("-").map(Number); return localToUtcMs(y, m, d); }
/** That midnight as an ISO stamp with the zone's offset ("2026-10-06T00:00:00-07:00"). */
export function dayStartIso(day) { return `${day}T00:00:00${tzOffsetStr(dayStartMs(day))}`; }
/** A clock time on the agency's clock, "2:05 PM". */
export function localClock(ms) { return new Date(ms).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", timeZone: TZ }); }
