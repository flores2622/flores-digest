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
export const COMMISSION_UNITS = STAFF.commission_units;
