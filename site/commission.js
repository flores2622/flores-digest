/* Commission: where each producer stands this folio (Frank, 2026-10-02:
 * "build this into the digest ... since its a calculator, make it reflect
 * live where they stand"). The two schedules are Frank's Commission Sheet
 * and Team Commission Sheet (2026-10-01), word for word in the numbers:
 *
 *   Individual (Crystal, Lorena, Mike): monthly Personal Lines premium
 *   $25,000 3% Good, $30,000 3.3% Better, $35,000 4.29% Best, $40,000
 *   4.38% Great, $45,000 4.44% Excellent, $50,000+ 5% Outstanding; below
 *   $25,000 no commission. The rate applies to the whole premium.
 *   Team (Sarahi + Coral): the same rates on their COMBINED premium at
 *   $50,000 / 60 / 70 / 80 / 90 / 100,000+, split 50/50.
 *   Flat (Crystal; her own "Crystal Comm Schedule" sheet, Frank 2026-10-06:
 *   "crystals comm schedule and goal is different than the others"): a set
 *   dollar amount per tier of monthly Personal Lines premium, not a rate --
 *   $15,000 $600, $20,000 $800, $25,000 $1,000, $30,000 $1,250, $35,000
 *   $1,500, $40,000+ $1,750; below $15,000 nothing (Frank: the table, not
 *   the sheet's stale "less than $30,000" note). Her extras are the same as
 *   everyone's (Frank: "bonus's and life is the same as the rest" -- the
 *   sheet's $75 life, $50 umbrella and 35% business are not used).
 *
 *   Additional: life $100 each whatever the tier (a policy count -- its
 *   premium never counts toward the tier, Frank 2026-10-05); multiline bundle to a NEW
 *   household $50 once; cross-sell to an EXISTING household $25 per line
 *   (both once the tier minimum is met; Auto, Home, Renters and Foremost
 *   lines only); umbrella $25 each; Farmers business 3.5% of the premium,
 *   which does not count toward the tier; Kraft Lake $300 at $10,000 of
 *   Kraft Lake premium with the tier met.
 *
 * Frank's answers (2026-10-02): the premium is the SALES SHEET's for the
 * folio (it is live -- the Worker adds a sale the refresh it is sold), and
 * "anything on the sales sheet counts" toward the tier (business aside, per
 * his own sheet; life aside too, 2026-10-05). A Winback is a new household. Who sees what is the
 * Worker's call (getCommission): each producer their own, Sarahi and Coral
 * their team, Frank and Amanda everyone.
 *
 * Households: a sheet row carries an AgencyZoom customer id or a client
 * name, so a household is the id, else the name; a row with neither stands
 * alone (it cannot make a bundle). Existing = the row's lead source is an
 * existing-household source (lead_sources.EXISTING_HOUSEHOLD, spelled any
 * way the sheet spells it: "Cross-Sell", "FFR-Cross Sell", "Existing client
 * purchased a new", "Home no Auto" ...). */

import { COMMISSION_UNITS, COMMISSION, AGENCY } from "./staff.js";
import LEAD_SOURCES from "./lead_sources_data.js";

// The numbers are staff.json's `commission` (Frank's two sheets, and Crystal's own: a schedule with `pay`
// pays that amount at each tier instead of the rate on the premium).
const TIER_NAMES = COMMISSION.tier_names;
const RATES = COMMISSION.rates;
export const SCHEDULES = COMMISSION.schedules;
export const UNITS = COMMISSION_UNITS;   // staff.json
export const PAY = COMMISSION.pay;
const CARRIER_RX = new RegExp((AGENCY.carrier || "farmers").replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i");

export function tiersOf(schedule) {
  const s = SCHEDULES[schedule];
  return s.mins.map((min, i) => (s.pay ? { name: TIER_NAMES[i], min, pay: s.pay[i] } : { name: TIER_NAMES[i], min, rate: RATES[i] }));
}

export function kindOf(product) {
  const p = String(product || "");
  if (/\blife\b|\bterm\b/i.test(p)) return "life";
  if (/umbrella/i.test(p)) return "umbrella";
  if (/kraft|\bkl\b/i.test(p)) return "kraft";
  if (/business|commercial|\bbop\b|work.?comp|general liab|\bgl\b/i.test(p)) return "business";
  return "pl";
}
const ELIGIBLE = /auto|home|renter|condo|foremost/i;
function isExisting(source) {
  const s = String(source || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  return /cross sell/.test(s) || s.startsWith("existing client") || s.startsWith("existing customer purchased")
    || EXISTING_SOURCES.includes(s);
}
// lead_sources.json's cross-sell sources (the existing-household groups), in this function's own spelling.
const EXISTING_SOURCES = LEAD_SOURCES.existing_household.map((n) => n.replace(/[^a-z0-9]+/g, " ").trim());
function householdKey(e) {
  if (e.az_customer_id) return "c:" + String(e.az_customer_id).trim();
  const n = String(e.client_name || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  return n ? "n:" + n : "e:" + (e.id || Math.random());
}
const num = (x) => (Number.isFinite(+x) ? +x : 0);
const row = (e) => ({ id: e.id, day: e.day, producer: e.producer, client: e.client_name || "",
  product: e.product || "", premium: num(e.premium), lead_source: e.lead_source || "" });

/** One unit's standing from the folio's sheet rows. */
export function standing(unit, entries) {
  const mine = entries.filter((e) => unit.members.includes(e.producer));
  const tiers = tiersOf(unit.schedule);
  const sched = SCHEDULES[unit.schedule];
  // Life pays by the policy ($100 each), never by premium (Frank,
  // 2026-10-05: "life is based only off of policy count, not premium"), so
  // neither it nor business counts toward the tier.
  const tierRows = mine.filter((e) => !["business", "life"].includes(kindOf(e.product)));
  const premium = tierRows.reduce((s, e) => s + num(e.premium), 0);
  let at = -1;
  tiers.forEach((t, i) => { if (premium >= t.min) at = i; });
  const tier = at >= 0 ? tiers[at] : null;
  const next = tiers[at + 1] || null;
  const met = at >= 0;
  const base = !tier ? 0 : tier.pay != null ? tier.pay : premium * tier.rate;

  // Each line's rows carry their own pay, so a team member's share of the
  // extras is the sum of their own rows.
  const lines = [];
  const add = (key, label, paid, pending, note, count) => lines.push({
    key, label, count: count ?? paid.length, pending, note,
    pay: Math.round(paid.reduce((s, x) => s + x.pay, 0) * 100) / 100,
    premium: paid.reduce((s, x) => s + num(x.e.premium), 0),
    rows: paid.map((x) => ({ ...row(x.e), pay: Math.round(x.pay * 100) / 100 })),
  });
  const of = (kind) => mine.filter((e) => kindOf(e.product) === kind);
  add("life", "Life policies", of("life").map((e) => ({ e, pay: PAY.life })), false,
    `$${PAY.life} each, whatever the tier`);
  add("umbrella", "Umbrellas", of("umbrella").map((e) => ({ e, pay: PAY.umbrella })), false, `$${PAY.umbrella} each`);

  // Bundles and cross-sells, within each producer's own households.
  const bundles = [], xsells = [];
  for (const who of unit.members) {
    const hh = new Map();
    for (const e of mine) {
      if (e.producer !== who || kindOf(e.product) !== "pl" || !ELIGIBLE.test(e.product || "")) continue;
      const k = householdKey(e);
      if (!hh.has(k)) hh.set(k, []);
      hh.get(k).push(e);
    }
    for (const rs of hh.values()) {
      if (rs.some((e) => isExisting(e.lead_source))) xsells.push(...rs);
      else if (rs.length >= 2) bundles.push(rs);
    }
  }
  const tierWord = `once ${unit.schedule === "team" ? "the team reaches" : "you reach"} $${tiers[0].min.toLocaleString("en-US")}`;
  add("bundle", "New household bundles",
    bundles.flatMap((rs) => rs.map((e, i) => ({ e, pay: met && i === 0 ? PAY.bundle : 0 }))),
    !met && bundles.length > 0, `$${PAY.bundle} per new household with 2+ lines, ${tierWord}`, bundles.length);
  add("xsell", "Cross-sells to existing households", xsells.map((e) => ({ e, pay: met ? PAY.xsell : 0 })),
    !met && xsells.length > 0, `$${PAY.xsell} per new line, ${tierWord}`);
  add("business", `${AGENCY.carrier || "Farmers"} business policies`,
    of("business").map((e) => ({ e, pay: CARRIER_RX.test(e.product || "") ? num(e.premium) * PAY.business : 0 })),
    false, "3.5% of the premium; does not count toward the tier");
  const kraft = of("kraft"), kraftPrem = kraft.reduce((s, e) => s + num(e.premium), 0);
  const kraftOn = kraftPrem >= PAY.kraftMin;
  add("kraft", "Kraft Lake", kraft.map((e, i) => ({ e, pay: kraftOn && met && i === 0 ? PAY.kraft : 0 })),
    kraftOn && !met, `$${PAY.kraft} at $${PAY.kraftMin.toLocaleString("en-US")} of Kraft Lake premium, ${tierWord}`);

  const extras = lines.reduce((s, l) => s + l.pay, 0);
  const members = unit.members.map((m) => {
    const own = tierRows.filter((e) => e.producer === m);
    const ex = lines.reduce((s, l) => s + l.rows.filter((r) => r.producer === m).reduce((t, r) => t + r.pay, 0), 0);
    const share = base * sched.split;
    return { name: m, premium: Math.round(own.reduce((s, e) => s + num(e.premium), 0) * 100) / 100,
      sales: own.length, share: Math.round(share * 100) / 100, extras: Math.round(ex * 100) / 100,
      total: Math.round((share + ex) * 100) / 100 };
  });
  return {
    key: unit.key, label: unit.label, schedule: unit.schedule, members,
    premium: Math.round(premium * 100) / 100, sales: tierRows.length,
    tiers, tier: tier && { ...tier, index: at },
    next: next && { ...next, gap: Math.round((next.min - premium) * 100) / 100 },
    base: Math.round(base * 100) / 100,
    extras: Math.round(extras * 100) / 100,
    total: Math.round((base + extras) * 100) / 100,
    lines,
    rows: tierRows.map(row),
  };
}

/** Every unit `visible` allows, from the folio's sheet rows. */
export function commission(entries, visible) {
  return UNITS.filter((u) => visible(u)).map((u) => standing(u, entries));
}
