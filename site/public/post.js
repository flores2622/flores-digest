/* The Flores Post (Frank, 2026-10-01) --------------------------------------
   The dateline's agency line is staff.json's agency (name · place), through
   the page's STAFF. */
const AGENCY_LINE = (() => { const a = (window.STAFF || {}).agency || {}; return [a.name, a.place].filter(Boolean).join(" · "); })();
/*
   The published day, and the folio, as a newspaper: its own page under the
   Sales Center, no links back to the Digest ("tabs on the left is enough").
   Written here, in rules, from the same day documents the Digest draws --
   nothing is typed by hand and nothing is paid for: a day edition reads
   the published day's document, a folio edition merges the folio's days
   (ensureCurForRange keeps them in curRangeDocs) and reads the last
   folio's for the pace to beat. Sales come first, always. A slow edition
   -- no sales on a day, a week under the goal (goals.json's week_premium_goal), a folio under last folio's
   pace -- says so and carries "What to try / What to look for". Primetime,
   the sports section, is a permanent part of the paper and is the only
   place the paper carries the standings table. */

(function () {
  const css = `
.paper { background: var(--surface-raised); border: var(--bw) solid var(--border-strong); border-radius: 6px; box-shadow: var(--shadow); padding: 32px 40px 40px; display: flex; flex-direction: column; gap: 26px; color: var(--text-primary); }
.paper .lab { font-size: 12px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--text-muted); }
.paper .kick { color: var(--accent); }
.mast { border-bottom: 3px double var(--text-primary); padding-bottom: 12px; display: flex; flex-direction: column; gap: 10px; }
.mrow { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; }
.mast h1 { margin: 0; text-align: center; font: 400 clamp(48px, 6.5vw, 104px)/1 var(--display); letter-spacing: -.01em; }
.mast .rule { border-top: 1px solid var(--text-primary); padding-top: 8px; }
.eds { display: flex; flex-wrap: wrap; gap: 4px 22px; align-items: baseline; border-bottom: 1px solid var(--border-strong); padding-bottom: 12px; margin-top: -12px; }
.eds button { border: 0; background: none; padding: 2px 0; font: 600 14px var(--body); color: var(--accent); cursor: pointer; text-decoration: underline; text-underline-offset: 3px; }
.eds button[aria-current="page"] { font-weight: 800; color: var(--text-primary); text-decoration: none; border-bottom: 2px solid var(--text-primary); }
.eds .tocome { font-size: 14px; color: var(--text-muted); }
.front { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 40px; }
.story { display: flex; flex-direction: column; gap: 12px; min-width: 0; }
.story h2.hl { margin: 0; font: 400 clamp(34px, 3.6vw, 58px)/1.02 var(--display); text-wrap: balance; border: 0; padding: 0; text-transform: none; letter-spacing: 0; }
.story .deck { margin: 0; font: italic 400 clamp(19px, 1.5vw, 23px)/1.35 var(--display); color: var(--text-secondary); max-width: 70ch; }
.byline { font-size: 12px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--text-muted); border-top: 1px solid var(--border-strong); border-bottom: 1px solid var(--border-strong); padding: 6px 0; }
.pbody { columns: 3 240px; column-gap: 32px; column-rule: 1px solid var(--grid); font-size: 16px; line-height: 1.62; color: var(--text-primary); }
.pbody p { margin: 0 0 12px; break-inside: avoid-column; }
.pbody p:first-child::first-letter { float: left; font: 400 58px/.85 var(--display); margin: 6px 8px 0 0; color: var(--accent); }
.pull { margin: 4px 0; padding: 14px 0; border-top: 3px solid var(--text-primary); border-bottom: 1px solid var(--text-primary); font: italic 400 24px/1.3 var(--display); }
.pull cite { display: block; margin-top: 8px; font: 700 12px var(--body); letter-spacing: .1em; text-transform: uppercase; font-style: normal; color: var(--text-muted); }
.btn-box { border: 1px solid var(--text-primary); padding: 16px; display: flex; flex-direction: column; gap: 2px; align-self: stretch; }
.btn-box h4 { margin: 0 0 8px; font: 400 22px var(--display); border-bottom: 3px double var(--text-primary); padding-bottom: 6px; }
.btn-box .r { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; padding: 7px 0; border-bottom: 1px dotted var(--border-strong); }
.btn-box .r span { font-size: 13px; color: var(--text-muted); } .btn-box .r b { font: 400 22px var(--display); }
.btn-box .r:last-child { border-bottom: 0; }
.paper.islive .btn-box b, .paper.islive .tlr.today .m { color: var(--livegreen); text-shadow: 0 0 10px var(--liveglow); }
.row3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0; border-top: 3px double var(--text-primary); padding-top: 18px; }
.row3 > article { padding: 0 28px; display: flex; flex-direction: column; gap: 8px; min-width: 0; }
.row3 > article:first-child { padding-left: 0; } .row3 > article:last-child { padding-right: 0; }
.row3 > article + article { border-left: 1px solid var(--border-strong); }
.row3 h3 { margin: 0; font: 400 26px/1.1 var(--display); text-wrap: balance; }
.row3 p { margin: 0; font-size: 15px; line-height: 1.6; color: var(--text-primary); }
.shead { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; flex-wrap: wrap; border-bottom: 1px solid var(--text-primary); padding-bottom: 8px; }
.shead h3 { margin: 0; font: 400 28px var(--display); } .shead h3 em { font-size: 18px; color: var(--text-muted); }
.shead .sd { margin: 0; }
table.box { width: 100%; border-collapse: collapse; font-size: 15px; }
.lbwrap { container-type: inline-size; width: 100%; overflow: hidden; }
.lbwrap table { width: 100%; min-width: 0 !important; }
@container (max-width: 1264px) { .lbwrap [data-p="12"] { display: none; } }
@container (max-width: 1172px) { .lbwrap [data-p="11"] { display: none; } }
@container (max-width: 1080px) { .lbwrap [data-p="10"] { display: none; } }
@container (max-width: 988px) { .lbwrap [data-p="9"] { display: none; } }
@container (max-width: 896px) { .lbwrap [data-p="8"] { display: none; } }
@container (max-width: 804px) { .lbwrap [data-p="7"] { display: none; } }
@container (max-width: 712px) { .lbwrap [data-p="6"] { display: none; } }
@container (max-width: 620px) { .lbwrap [data-p="5"] { display: none; } }
@container (max-width: 528px) { .lbwrap [data-p="4"] { display: none; } }
table.box th { font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--text-muted); text-align: right; padding: 4px 0; border-bottom: 1px solid var(--text-primary); }
table.box th:nth-child(-n+2), table.box td:nth-child(-n+2) { text-align: left; }
table.box td { padding: 7px 0; border-bottom: 1px dotted var(--border-strong); text-align: right; font-size: 15px; }
table.box td:nth-child(2) { font: 400 17px var(--display); }
table.box tbody tr:hover { background: transparent; }
.briefs div { display: block; padding: 7px 0; border-bottom: 1px dotted var(--border-strong); font-size: 14px; line-height: 1.45; }
.briefs b { font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: var(--accent); margin-right: 6px; }
.goals { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 28px; }
.goal { display: grid; grid-template-columns: 170px 1fr; gap: 10px; padding: 8px 0; border-bottom: 1px dotted var(--border-strong); font-size: 14px; align-items: baseline; }
.goal .g { font-weight: 700; } .goal .g small { display: block; font-weight: 500; color: var(--text-muted); font-size: 12px; }
.goal .w { line-height: 1.5; } .goal .w.none { color: var(--text-muted); font-style: italic; }
.tips { background: var(--side); color: var(--sideInk); padding: 22px 26px; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 8px 40px; border-radius: 4px; }
html[data-look="mesa"] .tips { background: var(--text-primary); color: var(--surface); }
.tips h3 { grid-column: 1 / -1; margin: 0 0 6px; font: 400 30px/1.1 var(--display); color: inherit; }
.tips h3 em { color: var(--brand2); font-style: normal; }
.tips .col h4 { margin: 0 0 6px; font-size: 12px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--brand2); }
.tips ol, .tips ul { margin: 0; padding-left: 20px; display: flex; flex-direction: column; gap: 8px; font-size: 15px; line-height: 1.5; }
.tips b { color: #fff; } html[data-look="mesa"] .tips b { color: var(--surface); }
.count { background: var(--side); color: var(--sideInk); padding: 22px 26px; display: grid; grid-template-columns: auto 1fr; gap: 6px 28px; align-items: center; border-radius: 4px; }
.count .big { grid-row: span 2; font: 400 clamp(56px, 6vw, 88px)/.9 var(--display); color: var(--brand2); }
.count .l1 { font: 400 clamp(26px, 2.6vw, 38px)/1.1 var(--display); } .count .l2 { font-size: 16px; line-height: 1.5; max-width: 75ch; }
.tl { display: flex; flex-direction: column; gap: 0; }
.tlr { display: grid; grid-template-columns: 92px minmax(0, 1fr) 92px minmax(0, 1.3fr); gap: 14px; align-items: center; padding: 7px 0; border-bottom: 1px dotted var(--border-strong); font-size: 14px; }
.tlr .d { font-weight: 700; } .tlr .d small { display: block; font-weight: 500; color: var(--text-muted); font-size: 12px; }
.tlr .b { height: 14px; background: var(--grid); border-radius: 3px; } .tlr .b > div { height: 14px; border-radius: 3px; background: var(--accent); }
.tlr .m { text-align: right; font: 400 18px var(--display); } .tlr .m.zero { color: var(--bad); }
.tlr.dim { color: var(--text-muted); } .tlr.dim .b > div { background: var(--border-strong); }
.tlr.ahead { color: var(--text-muted); } .tlr.ahead .b { background: repeating-linear-gradient(135deg, var(--grid) 0 6px, transparent 6px 12px); }
.tlr.today .b > div { background: var(--livegreen); }
.foot { border-top: 3px double var(--text-primary); padding-top: 10px; display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.press { padding: 40px; display: flex; flex-direction: column; gap: 10px; align-items: flex-start; }
.press h2 { font-size: 34px; border: 0; text-transform: none; letter-spacing: 0; margin: 0; padding: 0; }
/* Primetime: the sports section */
.sp { border-top: 3px double var(--text-primary); padding-top: 18px; display: flex; flex-direction: column; gap: 14px; }
.sp .hd { font: 400 64px/1 'Bebas Neue', Impact, sans-serif; letter-spacing: .04em; border-bottom: 4px solid var(--text-primary); padding-bottom: 6px; display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px; }
.sp .hd small { font: 700 12px var(--body); letter-spacing: .12em; }
.sp .big { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; }
.sp .big div { background: var(--card2); border: 2px solid var(--text-primary); padding: 12px; text-align: center; }
.sp .big b { display: block; font: 400 44px/1 'Bebas Neue', Impact, sans-serif; }
.sp .big span { font-size: 11px; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; }
.sp .take { font: italic 400 22px/1.35 var(--display); border-left: 5px solid var(--accent); padding-left: 14px; }
table.box.spt th { padding: 6px 4px; } table.box.spt td { padding: 7px 4px; white-space: nowrap; } table.box.spt th { font: 400 15px 'Bebas Neue', Impact, sans-serif; letter-spacing: .06em; color: var(--text-primary); border-bottom: 2px solid var(--text-primary); }
.sp .scroll { border: 0; }
@media (max-width: 1000px) { .front { grid-template-columns: 1fr; } .row3 { grid-template-columns: 1fr; } .row3 > article { padding: 14px 0 !important; border-left: 0 !important; border-top: 1px solid var(--border-strong); } .goals, .tips { grid-template-columns: 1fr; } .paper { padding: 24px 20px; } .sp .big { grid-template-columns: repeat(2, minmax(0, 1fr)); } .tlr { grid-template-columns: 70px 1fr 70px; } .tlr .e { grid-column: 1 / -1; } }
`;
  const st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
})();

let postEd = "";                                   // the edition picked on a folio ("" = the default)
const postCache = { lastFolio: {}, today: null, todayAt: 0 };

const pmoney = n => "$" + Math.round(+n || 0).toLocaleString("en-US");
const pfirst = n => String(n || "").split(" ")[0];
const ppct = (n, d = 1) => n == null || !isFinite(n) ? "—" : (+n).toFixed(d) + "%";
const plural = (n, s, p) => `${n} ${n === 1 ? s : (p || s + "s")}`;
const pseed = s => { let h = 0; for (const c of String(s)) h = (h * 31 + c.charCodeAt(0)) >>> 0; return h; };
const ppick = (arr, seed) => arr[pseed(seed) % arr.length];
const plist = arr => arr.length <= 1 ? arr.join("") : arr.slice(0, -1).join(", ") + " and " + arr[arr.length - 1];
const pdow = iso => new Date(iso + "T12:00:00Z").toLocaleDateString("en-US", { weekday: "long", timeZone: "UTC" });
const pmd = iso => new Date(iso + "T12:00:00Z").toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" });
const pdow3 = iso => new Date(iso + "T12:00:00Z").toLocaleDateString("en-US", { weekday: "short", timeZone: "UTC" });
const plong = iso => new Date(iso + "T12:00:00Z").toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric", timeZone: "UTC" });
function pbizDays(from, to) {
  const out = [];
  for (let d = new Date(from + "T12:00:00Z"); isoDate(d) <= to; d.setUTCDate(d.getUTCDate() + 1)) { const w = d.getUTCDay(); if (w && w !== 6) out.push(isoDate(d)); }
  return out;
}
const pord = n => `${n}${["th", "st", "nd", "rd"][(n % 10 > 3 || [11, 12, 13].includes(n % 100)) ? 0 : n % 10]}`;
const pmins = s => s == null ? "—" : s < 60 ? `${Math.round(s)}s` : s < 3600 ? `${Math.floor(s / 60)}m ${Math.round(s % 60)}s` : `${Math.floor(s / 3600)}h ${Math.floor((s % 3600) / 60)}m`;

/* ---- the figures an edition is written from ------------------------------ */
function postFacts(d) {
  const T = d.totals || {};
  const ps = +T.ps || 0, pol = +T.pol || 0, hh = +T.hh || 0, pq = +T.pq || 0, dials = +T.dials || 0, live = +T.live || 0;
  const rate = T.rate != null ? +T.rate : (dials ? 100 * live / dials : 0);
  const pts = (d.leaderboard || {}).points || {};
  const prods = (d.producers || []).map(p => ({ ...p, pts: +pts[p.name] || 0, worked: p.worked || 1 }));
  const byName = Object.fromEntries(prods.map(p => [p.name, p]));
  const order = ((d.leaderboard || {}).order || [...prods].sort((a, b) => b.pts - a.pts).map(p => p.name)).filter(n => byName[n]);
  const sellers = prods.filter(p => +p.ps > 0).sort((a, b) => b.ps - a.ps);
  const R = d.rows || {};
  const soldRows = R.sold || [], soldLeads = R.sold_leads || [], quotedRows = R.quoted || [];
  const hhKey = r => r.lead_id || r.lead;
  const hhSold = soldLeads.length ? new Set(soldLeads.map(hhKey)).size : pol;
  const hhSoldBy = name => soldLeads.length ? new Set(soldLeads.filter(r => r.who === name).map(hhKey)).size : (+(byName[name] || {}).pol || 0);
  const calls = d.calls || [];
  const sendoffs = calls.filter(c => (Array.isArray(c.sendoff) ? c.sendoff[0] : c.sendoff) === "producer");
  const objs = (d.objcats || []).map(o => Array.isArray(o) ? o : [o.name, o.n, o.won]).filter(o => o && o[0]).sort((a, b) => b[1] - a[1]);
  const flagCount = {}, flagsBy = {};
  for (const c of calls) {
    (c.flags || []).forEach((f, i) => {   // the same category the card's badges use (flagGroupOf)
      const k = (typeof flagGroupOf === "function" ? flagGroupOf(f, (c.flag_groups || [])[i]) : "") || "Other flags";
      flagCount[k] = (flagCount[k] || 0) + 1;
    });
    flagsBy[c.who] = (flagsBy[c.who] || 0) + (c.flags || []).length;
  }
  const topFlags = Object.entries(flagCount).sort((a, b) => b[1] - a[1]);
  const sp = d.speed_to_dial || {};
  const spTeam = sp.team && sp.team.median != null ? +sp.team.median : null;
  const spBest = Object.entries(sp.per || {}).filter(([, v]) => v && v.median != null).sort((a, b) => a[1].median - b[1].median)[0] || null;
  const M = d.messages || {};
  const reps = (M.replies || []).filter(r => !r.ack && !r.optout);
  const answered = reps.filter(r => r.minutes != null).map(r => +r.minutes).sort((a, b) => a - b);
  const replyMed = answered.length ? answered[Math.floor(answered.length / 2)] : null;
  const waiting = reps.filter(r => !r.answered_by).length;
  const tasks = T.tasks || {};
  const tiers = d.tiers || {};
  // the longest coached call stands in for the "best" one: a card's score is
  // a per-dimension object, never one number
  const durSecs = c => { const m = /(?:(\d+)m)?\s*(\d+)s/.exec(c.dur || ""); return m ? (+m[1] || 0) * 60 + +m[2] : 0; };
  const bestCall = [...calls].sort((a, b) => durSecs(b) - durSecs(a))[0] || null;
  const soldCall = calls.find(c => /sold/i.test(c.catc || "") || /^sold/i.test(c.cat || "")) || null;
  const overGoal = key => prods.filter(p => (tiers[p.name] || {})[key] === "green").map(p => p.name);
  return { d, T, ps, pol, hh, pq, dials, live, rate, prods, byName, order, sellers, soldRows, soldLeads, quotedRows, hhSold, hhSoldBy, calls, sendoffs, objs,
    topFlags, flagsBy, spTeam, spBest, replyMed, waiting, tasks, tiers, bestCall, soldCall, overGoal,
    closeHH: hh ? 100 * hhSold / hh : null, closePQ: pq ? 100 * ps / pq : null, talk: +T.talk || 0, util: T.util != null ? +T.util : null,
    misfiled: (d.misfiled || []).length, atRisk: ((d.recontact || {}).counts || {}).at_risk || 0 };
}

/* ---- the pieces every edition shares -------------------------------------- */
/* The goal board's lines, from goals.json's thresholds (window.GOALS, written
   by `python3 goals.py --write-js`): each metric's green number in words. */
const POST_GOALS = (() => {
  const T = (window.GOALS || {}).thresholds || {}, g = m => (T[m] || {}).green;
  const n = v => (v == null ? "?" : Number(v).toLocaleString("en-US"));
  return [["dials", "Dials", `${n(g("call_volume"))} or more a day`], ["talk", "Avg talk time", `${n(g("avg_talk_min"))} min or more`],
    ["rate", "Contact rate", `${n(g("contact_rate_pct"))}% or more`], ["hh", "Households quoted", `${n(g("households_quoted"))} or more a day`],
    ["pq", "Premium quoted per HH", `$${n(g("premium_quoted_per_hh"))} or more`], ["tasks", "Task completion", `${n(g("task_completion_pct"))}%`],
    ["util", "Utilization", `${n(g("utilization_pct"))}% or more`], ["roleplay", "Role play", `${n(g("roleplay_score"))} or more`],
    ["closing_hh", "Closing ratio", `${n(g("closing_ratio_pct"))}% or more`]];
})();
const WEEK_GOAL = (window.GOALS || {}).week_premium_goal || 20000;   // goals.json: a week under it is slow
function goalBoardHtml(F, title) {
  const rows = POST_GOALS.filter(([k]) => F.prods.some(p => (F.tiers[p.name] || {})[k] != null));
  const hit = rows.map(([k]) => F.prods.filter(p => (F.tiers[p.name] || {})[k] === "green").map(p => pfirst(p.name)));
  const near = [];
  rows.forEach(([k, label], i) => F.prods.forEach(p => { if ((F.tiers[p.name] || {})[k] === "yellow") near.push(`${pfirst(p.name)} on ${label.toLowerCase()}`); }));
  const counts = {}; hit.flat().forEach(n => counts[n] = (counts[n] || 0) + 1);
  const lead = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  return `<section style="display:flex;flex-direction:column;gap:10px"><div class="shead"><h3>${cesc(title)} <em>— who hit their goals</em></h3><span class="sd">${lead.length ? lead.map(([n, c]) => `${cesc(n)} ${c} of ${rows.length}`).join(" · ") : "Nobody hit a goal"}</span></div>
    <div class="goals">${rows.map(([k, label, goal], i) => `<div class="goal"><span class="g">${label}<small>${goal}</small></span><span class="w ${hit[i].length ? "" : "none"}">${hit[i].length ? cesc(hit[i].join(", ")) : "Nobody yet"}</span></div>`).join("")}</div>
    ${near.length ? `<p class="sd" style="font-size:14px">Close: ${cesc(near.slice(0, 3).join("; "))}.</p>` : ""}</section>`;
}
function tipsHtml(title, tries, looks) {
  return `<section class="tips"><h3>${title}</h3>
    <div class="col"><h4>What to try</h4><ol>${tries.map(t => `<li>${t}</li>`).join("")}</ol></div>
    <div class="col"><h4>What to look for</h4><ul>${looks.map(t => `<li>${t}</li>`).join("")}</ul></div></section>`;
}
const LOOK_FOR = ['Quotes ending with "I’ll email it to you". The Sent the Quote column on the leaderboard counts them.',
  "Leads sitting in Contacted or Ready to Present with a quote on file and no dated next step.",
  "Call backs that went unanswered, and texts still waiting on a reply.",
  "Talk time under 3 minutes on a live call: usually the quote was never built.",
  "Speed to Dial over 5 minutes on a new internet lead."];
function slowTips(F, when) {
  const obj = F.objs[0];
  const tries = [];
  if (F.hh) tries.push(`<b>Call the ${plural(F.hh, "quoted household")} back before 10 AM.</b> Present the quote on the phone and ask for the sale.${F.sendoffs.length ? ` Start with the ${F.sendoffs.length} that were sent instead of presented.` : ""}`);
  else tries.push("<b>Quote something before noon.</b> Nothing was quoted, so nothing could close. The first quote of the day is the hardest; book it early.");
  tries.push("<b>Work 1-1 QNC before new leads.</b> Quotes from the last 30 days that never closed are the quickest premium on the board. A new rate, a discount or a bundle is a reason to call.");
  if (obj) tries.push(`<b>Role play the ${cesc(obj[0])} objection.</b> It came up ${plural(obj[1], "time")} ${when} and was overcome ${obj[2] ? `${obj[2]} of them` : "not once"}.`);
  tries.push("<b>Cross-sell the book.</b> Customers with auto and no home or renters are the quickest sale on a slow day.");
  if (F.rate < 13) tries.push(`<b>Move the dial block later.</b> The contact rate was ${ppct(F.rate)}; people pick up more after 3 PM than before noon.`);
  return tries;
}
/* One leaderboard for every edition (Frank, 2026-10-02: "this is also the
   only leaderboard you didnt include all the info in, but it has the space
   ... make the ones that we have to scroll have the space and give the big
   ones the info they have space for, by priority"): the Digest's columns in
   the Digest's order, each with a priority. The table never scrolls: as its
   box narrows it drops the lowest-priority columns (container queries in
   the stylesheet below), and a wide box shows every one. */
const LB_COLS = [["Role Play", "rp", 8], ["Dials", "dials", 6], ["Avg Talk", "talk", 9], ["Contact Rate", "rate", 7], ["Texts / Emails", "msgs", 11],
  ["Sent the Quote", "sent", 10], ["HH Quoted", "hh", 4], ["Prem. Quoted", "pq", 5], ["HH Sold", "hhSold", 3], ["Prem. Sold", "ps", 2], ["Util.", "util", 12], ["Pts", "pts", 1]];
const lbTalk = s => `${Math.floor((s || 0) / 60)}:${String(Math.round(s || 0) % 60).padStart(2, "0")}`;
function lbCell(n, key, team) {
  switch (key) {
    case "rp": return n.rp != null && n.rp !== 0 ? String(Math.round(n.rp)) : (n.rp === 0 && !team ? "0" : "—");
    case "dials": return String(n.dials || 0);
    case "talk": return lbTalk(n.talk);
    case "rate": return `${ppct(n.rate)} (${n.live || 0})`;
    case "msgs": return `${n.texts || 0} / ${n.emails || 0}`;
    case "sent": return n.quoteUp ? `${n.sent} of ${n.quoteUp}` : "—";
    case "hh": return String(n.hh || 0);
    case "pq": return pmoney(n.pq);
    case "hhSold": return `${n.hhSold || 0} (${n.pol || 0} pol)`;
    case "ps": return pmoney(n.ps);
    case "util": return n.util != null ? ppct(n.util) : "—";
    case "pts": return team ? "" : `<b>${n.pts || 0}</b>`;
  }
  return "";
}
function lbTableHtml(order, NUM, T, full, opts = {}) {
  const cls = opts.cls || "lbt", rank = !!opts.rank;
  const th = LB_COLS.map(([l, , p]) => `<th data-p="${p}">${l}</th>`).join("");
  const tr = (f, i) => `<tr>${rank ? `<td>${i + 1}</td>` : ""}<td><b>${cesc(full ? (full[f] || f) : f)}</b>${rank && i === 0 ? " ★" : ""}</td>${LB_COLS.map(([, k, p]) => `<td data-p="${p}">${lbCell(NUM[f], k, false)}</td>`).join("")}</tr>`;
  return `<div class="lbwrap"><table class="${cls}"><thead><tr>${rank ? "<th>#</th>" : ""}<th>Producer</th>${th}</tr></thead><tbody>${order.map(tr).join("")}${
    T ? `<tr class="tot">${rank ? "<td></td>" : ""}<td><b>Team</b></td>${LB_COLS.map(([, k, p]) => `<td data-p="${p}">${lbCell(T, k, true)}</td>`).join("")}</tr>` : ""}</tbody></table></div>`;
}
// The Post's own numbers for it, from postFacts (the editions build the same
// shape in edFacts).
function lbNums(F) {
  const d = F.d, M = (d.messages || {}).producers || {}, so = c => Array.isArray(c.sendoff) ? c.sendoff[0] : c.sendoff;
  const NUM = {};
  for (const name of F.order) {
    const x = F.byName[name] || {}, mp = M[name] || {}, calls = F.calls.filter(c => c.who === name);
    NUM[name] = { dials: +x.dials || 0, live: +x.live || 0, rate: +x.rate || 0, hh: +x.hh || 0, pq: +x.pq || 0, ps: +x.ps || 0, pol: +x.pol || 0, talk: +x.talk || 0,
      rp: x.coach && x.coach.roleplay != null ? +x.coach.roleplay : (x.rp_scored != null ? Math.round(x.rp_scored) : 0), util: x.util != null ? +x.util : null,
      texts: +mp.texts || 0, emails: +mp.emails || 0, hhSold: F.hhSoldBy(name), pts: x.pts || 0,
      quoteUp: calls.filter(c => so(c) != null).length, sent: calls.filter(c => so(c) === "producer").length };
  }
  const sum = k => Object.values(NUM).reduce((a, n) => a + (n[k] || 0), 0);
  const T = { dials: F.dials, live: F.live, rate: F.rate, hh: F.hh, pq: F.pq, ps: F.ps, pol: F.pol, hhSold: F.hhSold, talk: F.talk, util: F.util, rp: (F.T || {}).roleplay,
    texts: sum("texts"), emails: sum("emails"), sent: F.sendoffs.length, quoteUp: sum("quoteUp") };
  return { NUM, T };
}
function standingsRows(F, isFolio) {
  return F.order.map(n => { const p = F.byName[n]; return [n, p.pts, F.hhSoldBy(n), pmoney(p.ps), p]; });
}
function boxHtml(rows, isFolio) {
  return `<table class="box"><thead><tr><th>#</th><th>Producer</th><th>Pts</th><th>HH sold</th><th>Premium</th></tr></thead><tbody>${
    rows.map((r, i) => `<tr><td>${i + 1}</td><td>${cesc(r[0])}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join("")}</tbody></table>`;
}
const briefsHtml = items => `<div class="briefs">${items.map(([k, x]) => `<div><b>${cesc(k)}</b>${cesc(x)}</div>`).join("")}</div>`;

function primetimeHtml(F, nums, isFolio, take) {
  const rows = standingsRows(F, isFolio);
  const top = rows[0];
  const play = F.soldCall || F.bestCall;
  const pen = Object.entries(F.flagsBy).sort((a, b) => b[1] - a[1]).map(([n, c]) => `${pfirst(n)} ${c}`).join(" · ");
  return `<section class="sp"><div class="hd">PRIMETIME<small>THE SPORTS SECTION · ${isFolio ? "THIS FOLIO" : "TODAY"} · ${F.live ? "FINAL" : "FINAL"}</small></div>
    <div class="big">${nums.slice(0, 5).map(([k, v]) => `<div><b>${cesc(v)}</b><span>${cesc(k)}</span></div>`).join("")}</div>
    <div class="take">${cesc(take)}</div>
    <div class="lab kick">The standings${isFolio ? " · per-day averages" : ""}</div>
    ${(() => { const { NUM, T } = lbNums(F); return lbTableHtml(F.order, NUM, T, null, { cls: "box spt", rank: true }); })()}
    <div class="row3" style="border-top:0;padding-top:0">
      <article><div class="lab kick">Player of the ${isFolio ? "folio" : "day"}</div><h3>${top ? cesc(top[0]) : "—"}</h3><p>${top ? `${plural(top[2], "household")} · ${top[3]} · ${top[1]} pts` : "No standings yet."}</p></article>
      <article><div class="lab kick">Play of the ${isFolio ? "folio" : "day"}</div><h3>${play ? cesc(`${pfirst(play.who)} and ${play.lead}`) : "No coached calls"}</h3><p>${play ? cesc(`${play.time ? play.time + ". " : ""}${(play.summary || "").slice(0, 220)}${(play.summary || "").length > 220 ? "…" : ""}`) : ""}</p></article>
      <article><div class="lab kick">Penalties</div><h3>${plural(Object.values(F.flagsBy).reduce((a, b) => a + b, 0), "flag")}</h3><p>${pen ? cesc(pen) : "A clean sheet."}${F.sendoffs.length ? ` · ${plural(F.sendoffs.length, "quote")} sent instead of presented` : ""}</p></article>
    </div></section>`;
}

/* ---- the day edition ------------------------------------------------------- */
function writeDay(d) {
  const F = postFacts(d), day = d.date, seed = day, dow = pdow(day);
  const n = F.prods.length || 5;
  const top = F.sellers[0], topName = top ? top.name : null;
  const prodWord = { 1: "one", 2: "two", 3: "three", 4: "four", 5: "five" }[F.sellers.length] || String(F.sellers.length);
  const nWord = { 1: "one", 2: "two", 3: "three", 4: "four", 5: "five" }[n] || String(n);
  const soldFor = name => F.soldRows.filter(r => r.who === name);
  const describeSales = name => { const rs = soldFor(name); if (!rs.length) return ""; return plist(rs.map(r => `${/^[aeiou]/i.test(r.product || "") ? "an" : "a"} ${r.product || "policy"} at ${pmoney(r.premium)}${/winback/i.test(r.source || "") ? " (a winback)" : /existing|cross/i.test(r.source || "") ? " (an existing customer)" : ""}`)); };
  const E = { dateline: plong(day), by: "By Apollo · Sales coaching", goalTitle: "The goal board" };
  const built = d.built_at ? fmtClock(d.built_at) : "";
  E.edition = `Daily edition${built ? ` · published ${built}` : ""}`;
  const nums = [["Premium sold", pmoney(F.ps)], ["Households sold", F.hh ? `${F.hhSold} of ${F.hh}` : String(F.hhSold)], ["Closing ratio", F.closeHH == null ? "—" : ppct(F.closeHH)],
    ["Premium quoted", pmoney(F.pq)], ["Dials", String(F.dials)], ["Contact rate", ppct(F.rate)]];
  E.nums = nums;
  const body = [];
  if (!F.ps) {
    E.kicker = "Sales desk";
    E.hl = F.hh ? ppick([`No sales on ${dow}. ${plural(F.hh, "quoted household")} ${F.hh === 1 ? "is" : "are"} waiting.`, `${dow} ends without a sale; ${plural(F.hh, "household")} quoted and none closed.`], seed)
      : `No sales and no quotes on ${dow}.`;
    E.deck = `${plural(F.dials, "dial")} reached ${plural(F.live, "person", "people")}${F.hh ? ` and ${plural(F.hh, "household")} ${F.hh === 1 ? "was" : "were"} quoted for ${pmoney(F.pq)}` : ""}. None closed.`;
    body.push(`Nobody sold on ${dow}.${F.hh ? ` The quoting was there: ${plural(F.hh, "household")} for ${pmoney(F.pq)}, an average of ${pmoney(F.pq / F.hh)} each. What was missing was the close.` : " Nothing was quoted, so nothing could close."}${F.sendoffs.length ? ` ${F.sendoffs.length} of the quotes ended with an offer to send them instead of presenting them on the call.` : ""}`);
  } else {
    E.kicker = "Sales desk";
    const share = top ? top.ps / F.ps : 0;
    if (F.sellers.length === 1) E.hl = ppick([`${topName} is the only sale on ${dow}: ${pmoney(F.ps)}`, `${pfirst(topName)} carries ${dow} alone with ${pmoney(F.ps)}`], seed);
    else if (share >= 0.5) E.hl = `${topName} carries ${dow} with ${pmoney(top.ps)} of the team's ${pmoney(F.ps)}`;
    else E.hl = ppick([`${topName} closes ${plural(F.hhSoldBy(topName), "household")} as the team clears ${pmoney(F.ps)}`, `${pmoney(F.ps)} in new premium; ${pfirst(topName)} leads with ${pmoney(top.ps)}`], seed);
    E.deck = `${plural(F.hhSold, "household")} bought${F.hh ? ` from ${F.hh} quoted${F.closeHH != null ? `, a ${F.closeHH >= 48 ? "one-in-two" : F.closeHH >= 30 ? "one-in-three" : F.closeHH >= 22 ? "one-in-four" : ppct(F.closeHH, 0)} close` : ""}` : ""}, on a day when ${plural(F.dials, "dial")} reached ${plural(F.live, "person", "people")}.`;
    const tp = F.byName[topName] || {};
    const stand = F.order.indexOf(topName) + 1;
    body.push(`${topName} sold ${plural(+tp.pol || 0, "policy", "policies")}${F.hhSoldBy(topName) ? ` to ${plural(F.hhSoldBy(topName), "household")}` : ""} for ${pmoney(tp.ps)}${describeSales(topName) ? `: ${describeSales(topName)}` : ""}, and finished ${stand === 1 ? "first" : stand === 2 ? "second" : stand === 3 ? "third" : stand + "th"} in the standings with ${tp.pts} points.${
      F.prods.every(p => (+p.dials || 0) <= (+tp.dials || 0)) && tp.dials ? ` ${pfirst(topName)} also led the team in dials, ${tp.dials}, and reached ${plural(+tp.live || 0, "person", "people")}.` : ""}`);
    const others = F.sellers.slice(1);
    const nonSellersQuoted = F.prods.filter(p => !(+p.ps > 0) && +p.hh > 0);
    if (others.length || nonSellersQuoted.length) body.push(`${F.sellers.length === n ? "Every producer sold." : `${prodWord[0].toUpperCase() + prodWord.slice(1)} of the ${nWord} producers sold.`}${
      others.map(p => ` ${p.name} wrote ${describeSales(p.name) || `${pmoney(p.ps)} in new premium`}.`).join("")}${
      nonSellersQuoted.map(p => ` ${p.name} quoted ${plural(+p.hh, "household")} but did not close one.`).join("")}`);
  }
  if (F.hh) body.push(`The close was ${F.hhSold} of ${F.hh} households${F.closeHH != null ? `, ${F.closeHH >= 25 ? "over" : "under"} the 25% goal` : ""}.${F.pq ? ` By premium it was ${ppct(F.closePQ)}, ${pmoney(F.ps)} of ${pmoney(F.pq)} quoted.` : ""}`);
  const overRate = F.overGoal("rate").map(pfirst);
  body.push(`The phones: ${plural(F.dials, "dial")} reached ${plural(F.live, "person", "people")}, a ${ppct(F.rate)} contact rate, ${F.rate >= 13 ? "over" : "under"} the 13% goal.${
    overRate.length ? ` ${overRate.length === 1 ? `Only ${overRate[0]} was` : `${plist(overRate)} were`} over it.` : " Nobody was over it."}${
    F.talk ? ` A live call ran ${pmins(F.talk)} on average${F.talk >= 420 ? ", over the 7-minute goal" : ""}.` : ""}${
    F.spTeam != null ? ` A new internet lead waited ${pmins(F.spTeam)} for its first dial${F.spBest ? `; ${pfirst(F.spBest[0])} was quickest at ${pmins(F.spBest[1].median)}` : ""}.` : ""}`);
  if (F.calls.length) {
    const o = F.objs[0];
    body.push(`Apollo read ${plural(F.calls.length, "call")}.${o ? ` ${o[0]} came up ${plural(o[1], "time")} and was overcome ${o[2] ? `${o[2]} of them` : "not once"}.` : ""}${
      F.sendoffs.length ? ` ${plural(F.sendoffs.length, "quote")} ${F.sendoffs.length === 1 ? "was" : "were"} sent instead of presented on the call (${plist([...new Set(F.sendoffs.map(c => pfirst(c.who)))])}).` : ""}${
      F.topFlags.length ? ` The flag raised most: ${F.topFlags[0][0].toLowerCase()}, ${plural(F.topFlags[0][1], "time")}.` : ""}`);
  }
  E.body = body;
  const o = F.objs[0];
  E.pull = o ? [`${o[0]} came up ${plural(o[1], "time")} today. ${o[2] ? `${o[2]} overcome.` : "None was overcome."}${/busy|timing/i.test(o[0]) ? " A time to talk is the whole answer." : ""}`, "Apollo, on today’s coaching cards"]
    : F.sendoffs.length ? ["Build the quote and present it on the call. It was sent instead.", "Apollo, on today’s coaching cards"]
    : [`${plural(F.dials, "dial")}, ${plural(F.live, "conversation")}. Every one of them is a maybe.`, "Apollo"];
  E.tips = !F.ps ? [`No sales on ${dow}. <em>Here is where to start tomorrow.</em>`, slowTips(F, "today"), LOOK_FOR] : null;
  E.s1 = ["Coaching desk", F.sendoffs.length ? `${plural(F.sendoffs.length, "quote")} sent instead of presented` : F.topFlags.length ? `${plural(F.topFlags[0][1], "call")} flagged for ${F.topFlags[0][0].toLowerCase()}` : "A clean day on the cards",
    F.calls.length ? `Apollo read ${plural(F.calls.length, "coached call")}.${F.topFlags.slice(0, 3).map(([g, c]) => ` ${g}: ${c}.`).join("")}${F.bestCall ? ` The strongest call was ${pfirst(F.bestCall.who)}'s with ${F.bestCall.lead}.` : ""}` : "No calls were coached."];
  E.s2 = ["Follow-up", F.replyMed != null ? `Texts answered in ${fmtMins(F.replyMed)}` : "Texts and tasks",
    `${F.replyMed != null ? `The team answered texts in a median of ${fmtMins(F.replyMed)}. ` : ""}${F.waiting ? `${plural(F.waiting, "text")} ${F.waiting === 1 ? "was" : "were"} still waiting at close. ` : "No text was left waiting. "}${
      F.tasks.total ? `Tasks: ${F.tasks.completed} of ${F.tasks.total} closed${F.tasks.pct >= 100 ? ", the 100% goal met" : `, ${ppct(F.tasks.pct, 0)} against a 100% goal`}.` : ""}`];
  E.wire = (typeof digestFeedItems === "function" ? digestFeedItems(d, "") : []).filter(it => it.t != null).sort((a, b) => b.t - a.t).slice(0, 8).map(it => [feedClock(it.t), `${it.me ? firstName(it.who) : "Apollo"}: ${it.text}`]);
  E.carry = (typeof needsNowRows === "function" ? needsNowRows(d, "") : []).filter(r => r.n).map(r => [String(r.n), r.t]);
  E.foot = built ? `Figures final as of ${built} Arizona` : "Figures as published";
  E.take = F.ps ? `The team goes ${F.hhSold}-for-${F.hh || F.hhSold} on households and ${F.closeHH != null && F.closeHH >= 25 ? "covers the 25% line" : "misses the 25% line"}; ${pfirst(topName)} leads with ${pmoney(top.ps)}.${F.sendoffs.length ? ` ${plural(F.sendoffs.length, "quote")} left on the field, sent and never presented.` : ""}`
    : `A shutout. ${plural(F.hh, "household")} quoted, none closed; ${plural(F.dials, "dial")} for ${plural(F.live, "conversation")}.`;
  return { E, F };
}

/* ---- the folio ------------------------------------------------------------- */
function folioDayRow(doc, live) {
  const F = postFacts(doc);
  const top = F.sellers[0];
  const note = !F.ps ? `No sales · ${plural(F.dials, "dial")}` : F.sellers.length === 1 ? `${pfirst(top.name)} sold ${plural(F.hhSoldBy(top.name), "household")} · the only sale` : `${pfirst(top.name)} led with ${pmoney(top.ps)} · ${plural(F.hhSold, "household")}`;
  return { date: doc.date, ps: F.ps, pol: F.pol, hhSold: F.hhSold, dials: F.dials, note, live: !!live, doc };
}
async function lastFolioTotal(end) {
  if (postCache.lastFolio[end] !== undefined) return postCache.lastFolio[end];
  const i = FOLIO_CLOSE_DATES.indexOf(end);
  let total = null;
  if (i > 0) {
    const prevEnd = FOLIO_CLOSE_DATES[i - 1], prevStart = folioStartFor(prevEnd) || "";
    const docs = await fetchRangeDocs(prevStart, prevEnd);
    if (docs.length) total = { ps: docs.reduce((a, x) => a + (+(x.totals || {}).ps || 0), 0), days: docs.length, start: prevStart, end: prevEnd };
  }
  postCache.lastFolio[end] = total;
  return total;
}
async function todayCheckpoint(today) {
  if (postCache.today && Date.now() - postCache.todayAt < 120000) return postCache.today;
  let doc = null;
  try { const r = await fetch(`/api/intraday/${today}`, { cache: "no-store" }); if (r.ok) doc = await r.json(); } catch (_) {}
  postCache.today = doc; postCache.todayAt = Date.now();
  return doc;
}
function folioEditions(bizdays, docDates, open) {
  const have = new Set(docDates);
  const out = []; let wk = 0, from = bizdays[0];
  bizdays.forEach((day, i) => {
    const left = bizdays.length - 1 - i;
    if (left === 0) { out.push({ id: "close", label: "Closing edition", date: day, ahead: open || !have.has(day), def: !open }); return; }
    if (pdow3(day) !== "Fri") return;
    wk++;
    out.push({ id: day, week: wk, label: `Week ${wk}`, date: day, from, upto: day, left, final: left <= 2, ahead: !have.has(day) && !(docDates.length && docDates[docDates.length - 1] > day) });
    from = bizdays[i + 1];
  });
  if (open) out.unshift({ id: "now", label: "Live now", date: "updating", def: true });
  return out;
}
function editionsNav(eds) {
  const curId = eds.some(x => x.id === postEd && !x.ahead) ? postEd : (eds.find(x => x.def) || {}).id;
  return `<nav class="eds" aria-label="Editions this folio"><span class="lab">Editions this folio</span>${eds.map(x => x.ahead
    ? `<span class="tocome">${x.label} · ${pmd(x.date)} · to come</span>`
    : `<button type="button" data-ed="${x.id}" aria-current="${x.id === curId ? "page" : "false"}">${x.label} · ${x.date === "updating" ? "updating" : pmd(x.date)}</button>`).join("")}</nav>`;
}
function timelineHtml(rows, ahead, title, sub, inWeek) {
  const max = Math.max(1, ...rows.map(r => r.ps));
  return `<section style="display:flex;flex-direction:column;gap:8px"><div class="shead"><h3>${title} <em>— premium sold</em></h3><span class="sd">${cesc(sub)}</span></div>
    <div class="tl">${rows.map(r => `<div class="tlr${r.live ? " today" : ""}${inWeek && !inWeek(r) ? " dim" : ""}"><span class="d">${pmd(r.date)}<small>${pdow3(r.date)}${r.live ? " · live" : ""}</small></span><div class="b"><div style="width:${r.ps / max * 100}%"></div></div><span class="m${r.ps ? "" : " zero"}">${pmoney(r.ps)}</span><span class="e">${cesc(r.note)}</span></div>`).join("")}
    ${ahead.map(day => `<div class="tlr ahead"><span class="d">${pmd(day)}<small>${pdow3(day)}</small></span><div class="b"></div><span class="m">—</span><span class="e">ahead</span></div>`).join("")}</div></section>`;
}
function writeFolio(merged, rows, ctx) {
  // merged: the days' documents merged (ensureCurForRange's), rows: one per day, ctx: {start, end, bizdays, ahead, open, last, live, ed}
  const F = postFacts(merged);
  const tot = rows.reduce((a, r) => a + r.ps, 0), nDone = rows.length, all = nDone + ctx.ahead.length;
  const pace = nDone ? tot / nDone * all : 0;
  const last = ctx.last, gap = last ? last.ps - pace : null;
  const best = rows.reduce((a, r) => !a || r.ps > a.ps ? r : a, null), worst = rows.reduce((a, r) => !a || r.ps < a.ps ? r : a, null);
  const hhSold = rows.reduce((a, r) => a + r.hhSold, 0);
  const span = `${pmd(ctx.start)} – ${pmd(ctx.end)}`;
  const topName = F.order[0];
  const perDay = (p, k) => p.worked ? (+p[k] || 0) / p.worked : 0;
  const E = { dateline: `Folio ${span}, ${ctx.end.slice(0, 4)}`, goalTitle: "The goal board · per-day averages" };
  const left = ctx.ahead.length;
  const zeroDays = rows.filter(r => !r.ps);
  const mondays = rows.filter(r => pdow3(r.date) === "Mon"), notMon = rows.filter(r => pdow3(r.date) !== "Mon");
  const avg = xs => xs.length ? xs.reduce((a, r) => a + r.ps, 0) / xs.length : 0;
  const slow = last ? pace < last.ps : false;
  if (ctx.open) {
    E.edition = `Folio edition · day ${nDone} of ${all} · ${ctx.live ? "updating live" : "as of the last published day"}`;
    E.kicker = "The folio so far"; E.by = "By Apollo · Updated every published day";
    E.hl = gap != null ? `${nDone === 1 ? "One day" : `${nDone} days`} in, the folio has ${pmoney(tot)} and is ${pmoney(Math.abs(gap))} ${gap > 0 ? "behind" : "ahead of"} last folio’s pace`
      : `${nDone === 1 ? "One day" : `${nDone} days`} in, the folio has ${pmoney(tot)}`;
    E.deck = `${nDone} of ${all} business days are done. At this pace it finishes near ${pmoney(pace)}${last ? `; last folio closed at ${pmoney(last.ps)}` : ""}.`;
    E.body = [
      `The folio has ${pmoney(tot)} in new premium after ${plural(nDone, "business day")}.${best && best.ps ? ` Its best day was ${pdow(best.date)} the ${pord(+best.date.slice(8))}, ${pmoney(best.ps)}: ${best.note}.` : ""}${worst && !worst.ps ? ` Its worst was ${pdow(worst.date)} the ${pord(+worst.date.slice(8))}, with no sales at all.` : ""}`,
      gap != null ? `At the current pace the folio closes near ${pmoney(pace)}, ${gap > 0 ? `about ${pmoney(gap)} short of the last one` : `about ${pmoney(-gap)} over the last one`}.${left ? ` ${plural(left, "business day")} ${left === 1 ? "is" : "are"} left${gap > 0 ? ` to close that gap: roughly ${pmoney(gap / left)} a day more than the team is averaging` : ""}.` : ""}`
        : `${left ? `${plural(left, "business day")} ${left === 1 ? "is" : "are"} left; at this pace the folio closes near ${pmoney(pace)}.` : "The folio is on its last day."}`,
      topName ? `${topName} leads on per-day averages with ${F.byName[topName].pts} points${perDay(F.byName[topName], "dials") >= 50 ? " and is over the 50-dial goal" : ""}.${
        F.sellers[0] && F.sellers[0].name !== topName ? ` ${F.sellers[0].name} has sold the most premium, ${pmoney(F.sellers[0].ps)}.` : ""}${
        F.overGoal("talk").length ? ` ${plist(F.overGoal("talk").map(pfirst))} ${F.overGoal("talk").length === 1 ? "has" : "have"} the longest calls.` : ""}` : "",
      F.hh ? `${plural(F.hh - hhSold > 0 ? F.hh - hhSold : 0, "quoted household")} ${F.hh - hhSold === 1 ? "has" : "have"} not bought yet. They are the fastest way back to pace.` : "",
    ].filter(Boolean);
    E.pull = gap != null && gap > 0 && left ? [`${pmoney(gap / left)} more a day closes the gap to last folio.`, `The gap to last folio’s total, spread over the ${plural(left, "day")} left`]
      : best ? [`${best.note}.`, `${pdow(best.date)}, ${pmd(best.date)}, the best day so far`] : ["The folio is open.", "Apollo"];
    E.nums = [["Premium sold", pmoney(tot)], ["Pace to close", pmoney(pace)], ["Last folio", last ? pmoney(last.ps) : "—"], ["Days to go", String(left)], ["Households sold", F.hh ? `${hhSold} of ${F.hh}` : String(hhSold)], ["Closing ratio", F.hh ? ppct(100 * hhSold / F.hh) : "—"]];
    E.tips = slow ? [`Behind last folio’s pace. <em>What to try with ${plural(left, "day")} left.</em>`, [
      `<b>Close what is already quoted.</b> ${plural(Math.max(0, F.hh - hhSold), "household")} have a quote and no sale. A call to each, presenting on the phone, is worth more than new leads.`,
      mondays.length && notMon.length && avg(mondays) < avg(notMon) * 0.6 ? `<b>Protect Mondays.</b> This folio’s Mondays average ${pmoney(avg(mondays))} against ${pmoney(avg(notMon))} on other days. Start Monday with call backs, not new dials.` : "<b>Protect the first hour.</b> Start the day with call backs and follow-ups, then new dials.",
      "<b>Bundle every auto quote.</b> Households with two policies close at a higher rate and lift premium per household.",
      F.objs[0] ? `<b>Role play the ${cesc(F.objs[0][0])} objection, every producer, every day.</b> It has come up ${plural(F.objs[0][1], "time")} this folio and was overcome ${F.objs[0][2]}.` : "<b>One role play a day for everyone.</b> A missed role play counts as zero in the standings."],
      ["Quotes presented but not closed after 3 days: they go cold fast.", "Producers under the 50-dial goal before noon.", "Speed to Dial over 5 minutes on a new internet lead.", 'Leads misfiled in "Pipeline" that nobody is working.']] : null;
    E.s1 = ["The race", topName && F.order[1] ? `${pfirst(topName)} leads ${pfirst(F.order[1])} by ${F.byName[topName].pts - F.byName[F.order[1]].pts} points` : "The standings",
      F.order.slice(0, 3).map((n, i) => `${i ? ", " : ""}${pfirst(n)} ${F.byName[n].pts}`).join("") + (F.order.length ? " on per-day averages." : "") + (F.prods.some(p => p.rp_missed) ? ` Missed role plays count as zeros: ${plist(F.prods.filter(p => p.rp_missed).map(p => `${pfirst(p.name)} ${p.rp_missed}`))}.` : "")];
    E.s2 = ["Bright spots", F.overGoal("rate").length ? `${plural(F.overGoal("rate").length, "producer")} over the contact-rate goal` : "What is working",
      `${F.overGoal("rate").length ? `${plist(F.overGoal("rate").map(pfirst))} ${F.overGoal("rate").length === 1 ? "is" : "are"} over the 13% contact-rate goal for the folio. ` : ""}${F.overGoal("pq").length ? `${plist(F.overGoal("pq").map(pfirst))} ${F.overGoal("pq").length === 1 ? "is" : "are"} quoting more than $900 per household.` : ""}` || "Every producer has room on every goal."];
    E.wireT = "Biggest moments"; E.wire = [...rows].sort((a, b) => b.ps - a.ps).slice(0, 6).map(r => [pmd(r.date), r.note]);
    E.carryT = "Still on the desk"; E.carry = [[String(Math.max(0, F.hh - hhSold)), "quoted households not yet closed"], [String(F.misfiled), 'leads misfiled in "Pipeline"'], [String(F.atRisk), "quoted leads going cold"]].filter(x => +x[0]);
    E.foot = `Updates every published day until the folio closes ${pmd(ctx.end)}`;
    E.take = `${pfirst(topName || "Nobody")} leads the folio${F.order[1] ? ` by ${F.byName[topName].pts - F.byName[F.order[1]].pts} on per-day averages` : ""}. ${plural(Math.max(0, F.hh - hhSold), "quoted household")} ${F.hh - hhSold === 1 ? "is" : "are"} the open play.`;
  } else {
    E.edition = `Folio closing edition · ${pmd(ctx.end)}`;
    E.kicker = "Folio in review"; E.by = "By Apollo · Closing edition";
    E.hl = best && best.date === rows[rows.length - 1].date && best.ps ? `The folio closes at ${pmoney(tot)} on its best day` : `The folio closes at ${pmoney(tot)}`;
    E.deck = `${plural(nDone, "business day")}, ${plural(hhSold, "household")} sold${best ? `, and a ${pmoney(best.ps)} best day on ${pmd(best.date)}` : ""}.`;
    E.body = [
      `The folio ran from ${pmd(ctx.start)} to ${pmd(ctx.end)}.${best ? ` Its best day was ${pdow(best.date)} ${pmd(best.date)} at ${pmoney(best.ps)}: ${best.note}.` : ""}${zeroDays.length ? ` ${plural(zeroDays.length, "day")} ended without a sale${zeroDays.length <= 3 ? ` (${plist(zeroDays.map(r => pmd(r.date)))})` : ""}.` : " Every business day had a sale."}`,
      topName ? `${topName} won the folio with ${F.byName[topName].pts} points on per-day averages${F.sellers[0] ? `, and ${F.sellers[0].name === topName ? "the most premium" : `${F.sellers[0].name} sold the most premium`}, ${pmoney(F.sellers[0].ps)}` : ""}.` : "",
      `Across the folio the team sold ${plural(hhSold, "household")}${F.hh ? ` of the ${F.hh} it quoted, a ${ppct(100 * hhSold / F.hh)} close` : ""}, on ${plural(F.dials, "dial")} and a ${ppct(F.rate)} contact rate.${last ? ` Last folio closed at ${pmoney(last.ps)}; this one ${tot >= last.ps ? "beat it" : "fell short"} by ${pmoney(Math.abs(tot - last.ps))}.` : ""}`,
    ].filter(Boolean);
    E.pull = best ? [`${best.note}.`, `${pdow(best.date)}, ${pmd(best.date)}, the best day of the folio`] : ["The folio is closed.", "Apollo"];
    E.nums = [["Premium sold", pmoney(tot)], ["Households sold", F.hh ? `${hhSold} of ${F.hh}` : String(hhSold)], ["Closing ratio", F.hh ? ppct(100 * hhSold / F.hh) : "—"], ["Best day", best ? pmoney(best.ps) : "—"], ["Dials", String(F.dials)], ["Contact rate", ppct(F.rate)]];
    E.tips = null;
    E.s1 = ["Folio honours", `${pfirst(topName || "Nobody")} wins the folio`, `Top producer: ${topName || "—"}.${F.sellers[0] ? ` Most premium: ${F.sellers[0].name}, ${pmoney(F.sellers[0].ps)}.` : ""}${best ? ` Best day: ${pmd(best.date)}, ${pmoney(best.ps)}.` : ""}${F.overGoal("rate").length ? ` Over the contact-rate goal: ${plist(F.overGoal("rate").map(pfirst))}.` : ""}`];
    E.s2 = ["Carried forward", `${plural(Math.max(0, F.hh - hhSold), "quoted household")} still open`, `${Math.max(0, F.hh - hhSold)} households quoted this folio had not bought when it closed. They open the new folio as its first calls.`];
    E.wireT = "Biggest moments"; E.wire = [...rows].sort((a, b) => b.ps - a.ps).slice(0, 6).map(r => [pmd(r.date), r.note]);
    E.carryT = "Into the new folio"; E.carry = [[String(Math.max(0, F.hh - hhSold)), "quoted households still open"], [String(F.misfiled), 'leads misfiled in "Pipeline"']].filter(x => +x[0]);
    E.foot = `Final as of the ${pmd(ctx.end)} run`;
    E.take = `${pfirst(topName || "Nobody")} takes the folio${F.sellers[0] && F.sellers[0].name !== topName ? `; ${pfirst(F.sellers[0].name)} owns the premium` : ""}. ${plural(hhSold, "household")} on ${plural(nDone, "day")}.`;
  }
  return { E, F, tot, pace, best, hhSold };
}
function writeWeek(docsUpto, rows, ctx, ed) {
  const weekRows = rows.filter(r => r.date >= ed.from && r.date <= ed.upto);
  const wkTot = weekRows.reduce((a, r) => a + r.ps, 0), fTot = rows.reduce((a, r) => a + r.ps, 0);
  const all = rows.length + ctx.ahead.length, pace = rows.length ? fTot / rows.length * all : 0;
  const best = weekRows.reduce((a, r) => !a || r.ps > a.ps ? r : a, null);
  const slowW = wkTot < WEEK_GOAL;
  const zeroDays = weekRows.filter(r => !r.ps);
  const nWord = ["", "One more day", "Two more days"][ed.left] || `${ed.left} more days`;
  const closeDay = ctx.end;
  const F = postFacts(mergeDayDocs(docsUpto.filter(x => x.date >= ed.from && x.date <= ed.upto)));
  return { kind: "week", F, weekRows, wkTot, fTot, pace, best, slowW, zeroDays, nWord, closeDay, all };
}

/* ---- rendering --------------------------------------------------------------- */
function postPaperHtml(E, F, opts) {
  const { isFolio, live, eds, extra, timeline } = opts;
  const k = t => `<div class="lab kick">${cesc(t)}</div>`;
  return `<article class="paper${live ? " islive" : ""}">
  <header class="mast">
    <div class="mrow lab"><span>${cesc(E.edition)}</span></div>
    <h1>The Flores Post</h1>
    <div class="mrow lab rule"><span>${cesc(E.dateline)}</span><span>${cesc(AGENCY_LINE)}</span><span>Apollo · Athena · Cerberus</span></div>
  </header>
  ${eds ? editionsNav(eds) : ""}
  ${extra || ""}
  <div class="front">
    <section class="story">${k(E.kicker)}<h2 class="hl">${cesc(E.hl)}</h2><p class="deck">${cesc(E.deck)}</p><div class="byline">${cesc(E.by)}</div>
      <div class="pbody">${E.body.map(p => `<p>${cesc(p)}</p>`).join("")}</div></section>
    <aside style="display:flex;flex-direction:column;gap:22px">
      <div class="btn-box"><h4>By the numbers</h4>${E.nums.map(([a, v]) => `<div class="r"><span>${cesc(a)}</span><b>${cesc(v)}</b></div>`).join("")}</div>
      <blockquote class="pull">“${cesc(E.pull[0])}”<cite>${cesc(E.pull[1])}</cite></blockquote>
    </aside>
  </div>
  ${E.tips ? tipsHtml(E.tips[0], E.tips[1], E.tips[2]) : ""}
  ${timeline || ""}
  <div class="row3">
    <article style="grid-column:span 2">${goalBoardHtml(F, E.goalTitle)}</article>
    <article>${k(E.s1[0])}<h3>${cesc(E.s1[1])}</h3><p>${cesc(E.s1[2])}</p></article>
  </div>
  <div class="row3">
    <article>${k(E.s2[0])}<h3>${cesc(E.s2[1])}</h3><p>${cesc(E.s2[2])}</p></article>
    <article>${k(E.carryT || "Still on the desk")}${E.carry && E.carry.length ? briefsHtml(E.carry.map(([n, t]) => [n, t[0].toUpperCase() + t.slice(1)])) : '<p class="sd">Nothing left waiting.</p>'}</article>
    <article>${k(E.wireT || "The wire")}${E.wire && E.wire.length ? briefsHtml(E.wire) : '<p class="sd">Quiet.</p>'}</article>
  </div>
  ${primetimeHtml(F, E.nums, isFolio, E.take)}
  <footer class="foot lab"><span>The Flores Post</span><span>${cesc(E.foot)}</span><span>Every figure is on the Digest</span></footer>
  </article>`;
}
function postGateHtml(title, text) {
  return `<section class="sect press"><span class="lab" style="font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--text-muted)">The Flores Post</span><h2>${title}</h2><p class="sd" style="font-size:15px;max-width:62ch;margin:0">${text}</p></section>`;
}

async function postPanel(err) {
  const today = isoDate(azTodayDate());
  if (rangeMode === "day") {
    if (!cur) return postGateHtml("No report for this day yet.", "Pick a published day in Day, or choose Folio to read the folio's edition.");
    if (curLive || cur.date === today && !DAYS.includes(today)) return postGateHtml("Today's Post goes to press after the 5:55 PM run.", "Pick a published day in Day, or choose Folio to read the folio's edition, which updates through the day.");
    const { E, F } = writeDay(cur);
    return postPaperHtml(E, F, { isFolio: false, live: false });
  }
  if (rangeMode !== "folio") return postGateHtml("The Post is written for a published day or a folio.", `${RANGE_LABELS[rangeMode] || "That range"} is on the Digest. Pick a published day in Day, or choose Folio.`);
  if (err) return postGateHtml("Nothing to print yet.", cesc(err));
  const b = rangeBounds(); if (b.err) return postGateHtml("Nothing to print yet.", cesc(b.err));
  const curEnd = folioEndFor(today), end = folioPick || curEnd, start = folioStartFor(end) || (curRangeDocs[0] || {}).date || b.from;
  const open = end >= today;
  let docs = [...curRangeDocs].sort((x, y) => x.date.localeCompare(y.date));
  const bizdays = pbizDays(start, end);
  let liveDoc = null;
  if (open && today >= start && !DAYS.includes(today)) liveDoc = await todayCheckpoint(today);
  const docDates = docs.map(x => x.date);
  const eds = folioEditions(bizdays, docDates, open);
  const edId = eds.some(x => x.id === postEd && !x.ahead) ? postEd : (eds.find(x => x.def) || {}).id;
  const ed = eds.find(x => x.id === edId) || eds[0];
  const last = await lastFolioTotal(end);
  if (ed && ed.week) {
    const upto = docs.filter(x => x.date <= ed.upto);
    const rows = upto.map(x => folioDayRow(x));
    const ahead = bizdays.filter(day => day > ed.upto);
    const W = writeWeek(upto, rows, { start, end, ahead }, ed);
    const F = W.F;
    const E = {
      edition: `Week ${ed.week} edition · published Fri ${pmd(ed.date)}`, dateline: `Folio ${pmd(start)} – ${pmd(end)}, ${end.slice(0, 4)} · week of ${pmd(ed.from)} – ${pmd(ed.date)}`,
      kicker: ed.final ? "The last Friday of the folio" : `Week ${ed.week} in review`, by: `By Apollo · Week ${ed.week} edition`, goalTitle: "The goal board · this week",
      hl: ed.final ? `${W.nWord} left: the folio stands at ${pmoney(W.fTot)}` : W.slowW ? `A slow week: ${pmoney(W.wkTot)} in, under the ${pmoney(WEEK_GOAL)} line` : `Week ${ed.week} adds ${pmoney(W.wkTot)}; the folio stands at ${pmoney(W.fTot)}`,
      deck: `${rows.length} of ${W.all} business days done. At this pace the folio finishes near ${pmoney(W.pace)}${last ? `; last folio closed at ${pmoney(last.ps)}` : ""}.`,
      body: [`The team sold ${pmoney(W.wkTot)} in new premium from ${pmd(ed.from)} to ${pmd(ed.date)}, across ${plural(W.weekRows.length, "business day")}.${W.best ? ` The best day was ${pdow(W.best.date)} ${pmd(W.best.date)}, at ${pmoney(W.best.ps)}: ${W.best.note}.` : ""}`,
        W.weekRows.filter(r => r.ps && r !== W.best).length ? W.weekRows.filter(r => r !== W.best).map(r => `${pmd(r.date)}: ${r.note}.`).join(" ") : "",
        `The folio has ${pmoney(W.fTot)} after ${plural(rows.length, "day")}. ${ed.final ? `${W.nWord} before it closes on ${pdow(W.closeDay)} ${pmd(W.closeDay)}: follow up every open quote, call back every lead that asked, and put the rest of the day's dials on the phone.` : `${plural(ahead.length, "business day")} remain before it closes on ${pmd(end)}.`}`].filter(Boolean),
      pull: W.best ? [`${W.best.note}.`, `${pdow(W.best.date)}, ${pmd(W.best.date)}, the best day of the week`] : ["No sales this week.", "Apollo"],
      nums: [["This week", pmoney(W.wkTot)], ["Folio to date", pmoney(W.fTot)], ["Best day", W.best ? pmoney(W.best.ps) : "—"], ["Days done", `${rows.length} of ${W.all}`], ["Pace to close", pmoney(W.pace)], ["Last folio", last ? pmoney(last.ps) : "—"]],
      tips: W.slowW ? [`A slow week: ${pmoney(W.wkTot)}, under the ${pmoney(WEEK_GOAL)} line.${ed.final ? " <em>Here is how to finish the folio.</em>" : ""}`, [
        "<b>Call back every household quoted this week.</b> Present the quote on the phone and ask for the sale; a quote sent by email rarely closes on its own.",
        "<b>Work 1-1 QNC before new leads.</b> Quotes that never closed in the last 30 days are the quickest premium on the board.",
        W.zeroDays.length ? `<b>Find out what happened on ${plist(W.zeroDays.map(r => `${pdow3(r.date)} ${pmd(r.date)}`))}.</b> A day with no sales usually means no quotes presented: check that day’s coaching cards.` : "<b>Protect the first hour.</b> Start the day with call backs and follow-ups, then new dials.",
        "<b>Bundle and cross-sell.</b> Existing customers missing a product are the easiest yes on a slow week.",
        F.objs[0] ? `<b>Role play the ${cesc(F.objs[0][0])} objection</b>, every producer, every day. It was dropped most this week.` : "<b>Role play the objection dropped most this week</b>, every producer, every day."], LOOK_FOR] : null,
      s1: ["Coaching desk", F.sendoffs.length ? `${plural(F.sendoffs.length, "quote")} sent instead of presented` : F.topFlags.length ? `${F.topFlags[0][0]} flagged ${plural(F.topFlags[0][1], "time")}` : "A clean week on the cards",
        F.calls.length ? `Apollo read ${plural(F.calls.length, "coached call")} this week.${F.topFlags.slice(0, 3).map(([g, c]) => ` ${g}: ${c}.`).join("")}` : "No calls were coached this week."],
      s2: ["The phones", `${ppct(F.rate)} contact rate on ${plural(F.dials, "dial")}`, `${plural(F.live, "conversation")} this week.${F.overGoal("rate").length ? ` Over the 13% goal: ${plist(F.overGoal("rate").map(pfirst))}.` : " Nobody was over the 13% goal."}${F.spTeam != null ? ` New leads waited ${pmins(F.spTeam)} for a first dial.` : ""}`],
      wireT: "This week's moments", wire: [...W.weekRows].sort((a, b) => b.ps - a.ps).slice(0, 6).map(r => [pmd(r.date), r.note]),
      carryT: "Into next week", carry: [[String(Math.max(0, F.hh - W.weekRows.reduce((a, r) => a + r.hhSold, 0))), "households quoted this week, not yet closed"]].filter(x => +x[0]),
      foot: `Frozen as it went out on ${pmd(ed.date)}`,
      take: `Week ${ed.week}: ${pmoney(W.wkTot)}${W.slowW ? ", under the ${pmoney(WEEK_GOAL)} line" : ""}. ${pfirst(F.order[0] || "Nobody")} tops the week's standings.`,
    };
    const count = ed.final ? `<section class="count"><div class="big">${ed.left}</div><div class="l1">${W.nWord}. The folio closes ${pdow(W.closeDay)}, ${pmd(W.closeDay)}.</div><div class="l2">${last ? `${pmoney(Math.max(0, last.ps - W.fTot))} to beat last folio's ${pmoney(last.ps)}. ` : ""}Every household still quoted is a sale that counts this folio if it closes by ${pmd(W.closeDay)}. Make the calls.</div></section>` : "";
    const inWeek = r => r.date >= ed.from && r.date <= ed.upto;
    return postPaperHtml(E, F, { isFolio: true, live: false, eds, extra: count, timeline: timelineHtml(rows, ahead, `The folio through week ${ed.week}`, "this week in colour", inWeek) });
  }
  // the live / closing edition
  const rows = docs.map(x => folioDayRow(x));
  if (liveDoc) rows.push(folioDayRow(liveDoc, true));
  const lastDate = rows.length ? rows[rows.length - 1].date : start;
  const ahead = bizdays.filter(day => day > lastDate && day > (liveDoc ? today : lastDate));
  const merged = cur;
  const W = writeFolio(merged, rows, { start, end, bizdays, ahead, open, last, live: !!liveDoc, ed });
  const tl = timelineHtml(rows, ahead, open ? "The folio, day by day" : "How the folio went, day by day", open ? `${plural(ahead.length, "business day")} to go` : "every business day of the folio");
  return postPaperHtml(W.E, W.F, { isFolio: true, live: !!liveDoc, eds, timeline: tl });
}
function wirePost() {
  $$("#view .eds [data-ed]").forEach(b => b.onclick = () => { postEd = b.dataset.ed; paint(); });
}
