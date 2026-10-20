/* Workflows -- what AgencyZoom's automations run today, read back from the
   leads (Frank, 2026-10-07: "how do we start building our own workflows? or
   display what we currently have so we can adjust or change as needed"),
   drawn as a timeline (Frank, 2026-10-12: "easier to look at as a timeline,
   the way the automation tab looks for current leads in agency zoom, with a
   way to filter to lead source, pipeline, or language"). Sales Center >
   Workflows, shown only to whoever /api/crm answers (Frank alone for now).
   The report is az_automations.py's (R2 crm/automations.json, through
   /api/crm/automations): every text rule, drip email, repeated task and the
   Smart-Cycle moves, each with its wording blanked of names, the stage it
   fires in and on which day, who it hits and what came back. The page lays
   them out pipeline by pipeline, stage by stage, Day 0 downwards, like
   AgencyZoom's automation tab on a lead; the filters are Frank's lead
   sources and pipelines (crm_lists) and the wording's language. A row
   opens to the whole rule; Frank marks each keep / change / drop with a
   note; the marks are the brief for the rules Elysium Pro will run itself
   (CRM.md, Workflows). Loads after tasks.js: it waits on CRM_READY. */
(function () {
  const KINDS = [["text", "Texts", "var(--accent)"], ["email", "Emails", "var(--s4)"], ["task", "Tasks", "var(--s3)"], ["cycle", "Smart-Cycle", "var(--good)"]];
  const PIPE_ORDER = ["New Business", "Quotes Not Closed", "Not Quoted", "Life", "Commercial", "Smart-Cycle", "Dead", "No sales stage on record"];
  const MIN_LEADS = 5;
  let D = null, wfBusy = false, wfMsg = null, wfNote = null, wfExp = {};
  let wfForm = null;   // {id|null, at: stage key or "", rule: the fields as typed}
  let wfSug = null;    // the rule key (or "general") whose suggestion box is open
  let F = { kinds: { text: true, email: true, task: true, cycle: true }, source: "", pipeline: "", lang: "", q: "", small: false };
  try { const w = JSON.parse(sessionStorage.getItem("workflows-where") || "{}"); if (w.F) F = Object.assign(F, w.F, { kinds: Object.assign(F.kinds, w.F.kinds || {}) }); if (w.exp) wfExp = w.exp; } catch (_) {}
  const saveWhere = () => { try { sessionStorage.setItem("workflows-where", JSON.stringify({ F, exp: wfExp })); } catch (_) {} };

  async function api(path, body) {
    const r = await fetch("/api/crm/" + path, body ? { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) } : { cache: "no-store" });
    let j = null; try { j = await r.json(); } catch (_) {}
    if (!r.ok) { const e = new Error((j && j.error) || `HTTP ${r.status}`); e.status = r.status; throw e; }
    return j;
  }
  window.WORKFLOWS_READY = (async function () {
    // its own probe: the ops team (workflows_suggest) sees this page and no other CRM page
    try { D = await api("automations"); } catch (_) { return false; }
    if (!CENTERS.salescenter.some(([k]) => k === "workflows")) CENTERS.salescenter.push(["workflows", "Workflows"]);
    SEARCH_PAGES.push(["Workflows", "Sales Center · what AgencyZoom's automations run today, as a timeline, and what to keep", "workflows"]);
    paintCenterBar();
    return true;
  })();

  const n = (x) => (x || 0).toLocaleString("en-US");
  const pct = (a, b) => (b ? Math.round(100 * a / b) : 0);
  const hour = (h) => (h == null ? "" : `${h % 12 || 12} ${h < 12 ? "AM" : "PM"}`);
  const stageName = (s) => (s || "").split(" | ").pop() || s;
  const azPipe = (s) => ((s || "").includes(" | ") ? s.split(" | ")[0] : "");
  // AgencyZoom's own count: Day 1 is the day the lead gets to the stage, in business days
  const dayN = (d) => (d == null ? null : Math.max(1, Math.round(d)));
  const dayLabel = (d) => (d == null ? "No set day" : `Day ${n(d)}`);
  const daySub = (d) => (d == null ? "fires with no fixed day on record" : d === 1 ? "the day the lead gets there" : d === 2 ? "the next business day" : d >= 250 ? `about ${(d / 250).toFixed(1).replace(/\.0$/, "")} years in the stage` : d >= 45 ? `about ${Math.round(d / 21.7)} months in the stage` : `${n(d - 1)} business days after it gets there`);
  const ICON = { text: "💬", email: "✉️", task: "☑️", cycle: "🔁" };
  const KIND_WORD = { text: "Text", email: "Email", task: "Task", cycle: "Move" };
  const LANG = { en: "English", es: "Spanish" };
  const canEdit = () => !!(D && D.can && D.can.edit);
  const sugsOf = (key) => ((D && D.suggestions) || []).filter((x) => x.key === key);
  const openSugs = (key) => sugsOf(key).filter((x) => !x.done);
  const isPerson = (name) => /^(Crystal|Lorena|Mike|Coral|Sarahi|Amanda|Debbie|Frank|Francisco|Veronica)/.test(name || "");

  // ---- where a rule sits on the timeline ----
  // every AgencyZoom stage -> its pipeline (Frank's name), Frank's own stage for it when it has one
  // (the Lists page's; "1 Pipeline | New" and "AZ Sun | New" both read as New), and its order
  function stageMap(R) {
    const m = {}; (R.stage_order || []).forEach((s, i) => { m[s.stage] = { pipeline: s.pipeline, az: s.az_pipeline, ord: s.my_ord != null ? s.my_ord : 1000 + i, my: s.my_stage || null }; });
    return m;
  }
  const myStages = (R, pipeline) => (pipeline === "Smart-Cycle" ? ["Smart-Cycle"] : ((R.stages || {})[pipeline] || []));
  function placeOf(r, sm, R) {
    if (r.own) {
      const k = sm[r.stage];                                   // a draft written against an AgencyZoom stage name
      const stage = k && k.my ? k.my : r.stage, i = myStages(R || D.report || {}, r.pipeline).indexOf(stage);
      return { pipeline: r.pipeline, stage, ord: i >= 0 ? i + 1 : (k ? k.ord : (stage === "Smart-Cycle" ? 0 : 5000)) };
    }
    const st = (r.stages || [])[0], name = st && st.name !== "(unknown)" ? st.name : "";
    if (r.kind === "cycle") return { pipeline: r.key === "cycle:dead" ? "Dead" : "Smart-Cycle", stage: r.key === "cycle:park" ? "Into Smart-Cycle" : r.key === "cycle:back" ? "Smart-Cycle" : "Dead", ord: r.key === "cycle:park" ? -1 : 0 };
    if (!name) return { pipeline: "No sales stage on record", stage: "Service tasks, and tasks on customers", ord: 9999 };
    if (name === "Smart-Cycle") return { pipeline: "Smart-Cycle", stage: "Smart-Cycle", ord: 0 };
    if (name === "Dead") return { pipeline: "Dead", stage: "Dead", ord: 0 };
    const k = sm[name];
    return { pipeline: k ? k.pipeline : azPipe(name) || "No sales stage on record", stage: k && k.my ? k.my : name, az: name, ord: k ? k.ord : 5000 };
  }
  function allRules(R) {
    return [].concat(R.texts || [], R.emails || [], R.tasks || [], (R.cycles || []).filter((c) => c.fired));
  }
  // Elysium Pro's own rules (drafts), shaped enough to sit on the timeline
  function ownRules() {
    return ((D && D.rules) || []).map((r) => Object.assign({}, r, { own: true, key: r.id, kind: r.kind === "move" ? "cycle" : r.kind, rkind: r.kind, day: r.day, lang: r.lang || "en" }));
  }
  function passes(r) {
    if (r.own) {
      if (!F.kinds[r.kind]) return false;
      if (F.source && r.sources.length && !r.sources.includes(F.source)) return false;
      if (F.lang && r.lang !== F.lang) return false;
      if (F.q) { const q = F.q.toLowerCase(); if (!((r.title || "") + " " + (r.subject || "") + " " + (r.body || "")).toLowerCase().includes(q)) return false; }
      return true;
    }
    if (!F.kinds[r.kind]) return false;
    if (!F.small && r.kind !== "cycle" && r.leads < MIN_LEADS) return false;
    if (F.source && !(r.groups || []).some((g) => g.name === F.source)) return false;
    if (F.lang && r.kind !== "cycle" && (r.lang || "en") !== F.lang) return false;
    if (F.q) { const q = F.q.toLowerCase(); if (!((r.title || "") + " " + (r.template || "")).toLowerCase().includes(q)) return false; }
    return true;
  }
  function options(R) {
    const sources = {}, pipes = {}, sm = stageMap(R);
    allRules(R).forEach((r) => { (r.groups || []).forEach((g) => { sources[g.name] = (sources[g.name] || 0) + g.n; }); const p = placeOf(r, sm, R).pipeline; pipes[p] = (pipes[p] || 0) + 1; });
    const pipeKeys = Object.keys(pipes).sort((a, b) => (PIPE_ORDER.indexOf(a) + 1 || 99) - (PIPE_ORDER.indexOf(b) + 1 || 99) || a.localeCompare(b));
    return { sources: Object.keys(sources).sort((a, b) => sources[b] - sources[a]), pipes: pipeKeys };
  }

  // ---- the pieces of an open rule (the old card) ----
  function whenLine(r) {
    const st = (r.stages || [])[0], ds = r.days_in_stage || {}, da = r.days_since_arrival || {};
    const parts = [];
    if (st && st.name && st.name !== "(unknown)") parts.push(`while the lead sits in <b>${cesc(stageName(st.name))}</b> (${pct(st.n, r.fired)}% of the time)`);
    if (ds.median != null) parts.push(ds.median < 0.5 ? "the same day it got there" : `about <b>${ds.median} day${ds.median === 1 ? "" : "s"}</b> after it got there`);
    if (da.median != null) parts.push(`${da.median < 0.5 ? "the day" : `<b>${da.median} day${da.median === 1 ? "" : "s"}</b> after`} the lead arrived`);
    if (r.peak_hour != null) parts.push(`mostly around ${hour(r.peak_hour)}`);
    return parts.length ? "Fires " + parts.join(", ") + "." : "";
  }
  const chips = (list, label) => (list && list.length ? `<div class="wfchips"><span class="wflab">${label}</span>${list.map((x) => `<span class="wfchip">${cesc(stageName(x.name))} <small>${n(x.n)}</small></span>`).join("")}</div>` : "");
  function hist(h) {
    if (!h || !h.hist || !h.hist.length) return "";
    const max = Math.max(...h.hist.map((x) => x.n));
    return `<div class="wfhist">${h.hist.map((x) => `<div class="wfbar" title="${cesc(x.name)}: ${n(x.n)}"><i style="height:${Math.max(3, Math.round(40 * x.n / max))}px"></i><span>${cesc(x.name)}</span></div>`).join("")}</div>`;
  }
  function markHtml(r) {
    const m = (D.marks || {})[r.key] || {};
    const open = wfNote === r.key;
    if (!canEdit()) return `<div class="wfmark">${m.mark ? `<span class="wfbadge ${m.mark}">${m.mark[0].toUpperCase() + m.mark.slice(1)}</span>` : ""}${m.note ? `<div class="wfnote">${cesc(m.note)}</div>` : ""}</div>${sugHtml(r.key)}`;
    return `<div class="wfmark">
      ${["keep", "change", "drop"].map((k) => `<button type="button" class="wfmk ${k}${m.mark === k ? " on" : ""}" data-mark="${k}" data-key="${cesc(r.key)}"${wfBusy ? " disabled" : ""}>${k[0].toUpperCase() + k.slice(1)}</button>`).join("")}
      <button type="button" class="ghost tksmall" data-note="${cesc(r.key)}">${m.note ? "Edit note" : "Add a note"}</button>
      ${m.mark || m.note ? `<small class="lsmute">${m.by ? cesc(m.by.split(" ")[0]) : ""} ${m.at ? cesc(m.at.slice(0, 10)) : ""}</small>` : ""}
      ${m.note && !open ? `<div class="wfnote">${cesc(m.note)}</div>` : ""}
      ${open ? `<form class="lsform" data-notefor="${cesc(r.key)}"><input type="text" class="lsin lswide" name="note" value="${cesc(m.note || "")}" placeholder="What should change, or why it goes" maxlength="500" autofocus><button type="submit" class="btn tkpri">Save</button><button type="button" class="btn" data-cancelnote="1">Cancel</button></form>` : ""}
    </div>${sugHtml(r.key)}`;
  }
  // the suggestions on one rule (or the page, key "general"): the list, then the box
  function sugHtml(key, big) {
    const list = sugsOf(key), me = (D.can || {}).name;
    const items = list.map((x) => `<li class="wfsug${x.done ? " done" : ""}">
      <span class="wfsugtxt">${cesc(x.text)}</span>
      <small class="lsmute">${cesc(x.by.split(" ")[0])} ${cesc(x.at.slice(0, 10))}${x.done ? ` · done by ${cesc((x.done_by || "").split(" ")[0])}` : ""}</small>
      ${canEdit() ? `<button type="button" class="ghost tksmall" data-sugdone="${cesc(x.id)}:${x.done ? 0 : 1}">${x.done ? "Reopen" : "Done"}</button>` : ""}
      ${canEdit() || x.by === me ? `<button type="button" class="ghost tksmall" data-sugdel="${cesc(x.id)}">Remove</button>` : ""}
    </li>`).join("");
    const open = wfSug === key;
    return `<div class="wfsugs${big ? " big" : ""}">
      ${items ? `<ul class="wfsuglist">${items}</ul>` : (big ? `<p class="lsmute">No suggestions yet.</p>` : "")}
      ${open ? `<form class="lsform wfsugform" data-sugfor="${cesc(key)}"><input type="text" class="lsin lswide" name="text" maxlength="1000" placeholder="${key === "general" ? "A rule we should have, a stage that needs one, anything on the page" : "What should change on this one"}" autofocus><button type="submit" class="btn tkpri">Suggest</button><button type="button" class="btn" data-cancelsug="1">Cancel</button></form>`
        : `<button type="button" class="ghost tksmall wfsugbtn" data-suggest="${cesc(key)}">💡 ${big ? "Add a suggestion" : "Suggest"}</button>`}
    </div>`;
  }
  function cameLine(r) {
    if (r.kind === "text") return `${n(r.replied)} wrote back within 2 days (${r.replied_pct}%)${r.opted_out ? ` · <span class="wfbad">${n(r.opted_out)} opted out</span>` : ""}`;
    if (r.kind === "email") return `${n(r.opened)} opened (${pct(r.opened, r.fired)}%) · ${n(r.replied)} wrote back within 3 days${r.bounced ? ` · <span class="wfbad">${n(r.bounced)} bounced</span>` : ""}`;
    return "";
  }
  function detail(r) {
    if (r.kind === "cycle") {
      const auto = (r.by || []).filter((b) => !isPerson(b.name)).reduce((a, b) => a + b.n, 0);
      const verb = r.key === "cycle:park" ? "Parked" : r.key === "cycle:back" ? "Brought back" : "Deaded";
      return `<p class="wfwhen">${verb} about <b>${r.days_in_stage.median} days</b> after the lead got to where it was; ${n(auto)} of ${n(r.fired)} by the automation, the rest by a person.</p>
        <div class="wfgrid"><div>${chips(r.stages, r.key === "cycle:back" ? "Came back into" : "From")}${chips(r.groups, "Lead sources")}${chips(r.by, "By")}</div><div><div class="wflab">Days there first</div>${hist(r.days_in_stage)}</div></div>${markHtml(r)}`;
    }
    const came = cameLine(r);
    return `${r.template ? `<blockquote class="wftpl">${cesc(r.template)}${r.variants > 1 ? ` <small class="lsmute">(${r.variants} wordings; the commonest shown)</small>` : ""}</blockquote>` : ""}
      <p class="wfwhen">${whenLine(r)}${r.first ? ` <small class="lsmute">${cesc(r.first)} to ${cesc(r.last)}.</small>` : ""}</p>
      <div class="wfgrid">
        <div>${chips(r.groups, "Lead sources")}${chips(r.stages, "Stage when it fired")}${chips(r.by, r.kind === "task" ? "For" : "Signed by")}</div>
        <div>${r.days_in_stage && r.days_in_stage.median != null ? `<div class="wflab">Days in the stage when it fired</div>${hist(r.days_in_stage)}` : ""}${chips(r.sources, "AgencyZoom sources")}</div>
      </div>
      ${came ? `<p class="wfcame">${came}</p>` : ""}
      ${markHtml(r)}`;
  }

  // ---- one row on the timeline ----
  const sugBadge = (key) => { const o = openSugs(key).length; return o ? `<span class="wfbadge sug" title="${o} open suggestion${o === 1 ? "" : "s"}">💡 ${o}</span>` : ""; };
  function excerpt(r) {
    if (r.kind === "cycle") return r.title;
    const t = r.kind === "email" ? r.title : (r.template || r.title || "");
    const one = t.replace(/\s+/g, " ").trim();
    return one.length > 150 ? one.slice(0, 148) + "…" : one;
  }
  function ownRow(r) {
    const open = !!wfExp[r.key];
    const what = r.rkind === "email" ? r.subject : r.rkind === "task" ? r.title : r.rkind === "move" ? `Move to ${stageName(r.to_stage)}` : (r.body || "");
    const one = what.replace(/\s+/g, " ").trim();
    const srcs = r.sources.length ? `${r.sources.length} source${r.sources.length === 1 ? "" : "s"}` : "every source";
    return `<li class="wfev wf-${r.kind} own${open ? " open" : ""}${openSugs(r.id).length ? " hl" : ""}" id="wf-${cesc(r.key)}">
      <button type="button" class="wfrow" data-open="${cesc(r.key)}" aria-expanded="${open}">
        <span class="wfico" title="${KIND_WORD[r.kind]}">${ICON[r.kind]}</span>
        <span class="wftxt"><span class="wfkind">${KIND_WORD[r.kind]}</span> ${cesc(one.length > 150 ? one.slice(0, 148) + "…" : one)}</span>
        <span class="wfmeta">${sugBadge(r.id)}${r.lang === "es" ? `<span class="wflang">Spanish</span>` : ""}<span class="wfbadge draft">Elysium Pro · draft</span><span class="wfn">${srcs}</span><span class="wfarrow">${open ? "▲" : "▼"}</span></span>
      </button>
      ${open ? `<div class="wfdetail">${wfForm && wfForm.id === r.id ? formHtml(D.report) : ownDetail(r)}</div>` : ""}
    </li>`;
  }
  function ownDetail(r) {
    const when = `Day ${n(r.day)} in <b>${cesc(stageName(r.stage))}</b> (${cesc(r.pipeline)})${r.hour != null ? `, around ${hour(r.hour)}` : ""}, for ${r.sources.length ? r.sources.map((x) => `<span class="wfchip">${cesc(x)}</span>`).join(" ") : "every lead source"}${r.lang === "es" ? ", Spanish-speaking leads" : ""}.`;
    const what = r.rkind === "text" ? `<blockquote class="wftpl">${cesc(r.body)}</blockquote>`
      : r.rkind === "email" ? `<p class="wfwhen"><b>Subject:</b> ${cesc(r.subject)}</p><blockquote class="wftpl">${cesc(r.body)}</blockquote>`
      : r.rkind === "task" ? `<p class="wfwhen"><b>Task:</b> ${cesc(r.title)} -- for ${cesc(r.who || "the lead's producer")}${r.body ? `</p><blockquote class="wftpl">${cesc(r.body)}</blockquote><p>` : ""}</p>`
      : `<p class="wfwhen"><b>Move the lead to</b> ${cesc(r.to_stage)}.</p>`;
    return `<p class="wfwhen">${when}</p>${what}${r.note ? `<div class="wfnote">${cesc(r.note)}</div>` : ""}
      <div class="wfmark"><span class="wfdraftnote">A draft: Elysium Pro does not run it yet. It will, once the CRM owns the tasks and the text and email senders are in.</span>
        ${canEdit() ? `<button type="button" class="btn tksmall" data-editrule="${cesc(r.id)}">Edit</button>
        <button type="button" class="ghost tksmall" data-delrule="${cesc(r.id)}">Delete</button>` : ""}
        <small class="lsmute">${cesc((r.updated_by || r.by || "").split(" ")[0])} ${cesc((r.updated || r.at || "").slice(0, 10))}</small></div>${sugHtml(r.id)}`;
  }
  // the add / edit form, prefilled from wfForm.rule
  function formHtml(R) {
    const f = wfForm.rule, sm = stageMap(R || {});
    const pipes = Object.keys(R.stages || {}).concat(["Smart-Cycle"]);
    const stages = myStages(R, f.pipeline);
    const allStages = pipes.flatMap((p) => myStages(R, p).map((st) => [p === "Smart-Cycle" ? st : `${p} | ${st}`, p === "Smart-Cycle" ? st : `${p} · ${st}`])).concat([["Dead", "Dead"]]);
    const o = options(R);
    const sel = (name, list, cur, blank) => `<select class="lsin" name="${name}">${blank ? `<option value="">${blank}</option>` : ""}${list.map(([v, t]) => `<option value="${cesc(v)}"${v === cur ? " selected" : ""}>${cesc(t)}</option>`).join("")}</select>`;
    const kind = f.kind || "text";
    void sm;
    return `<form class="wfform" data-ruleform="${cesc(wfForm.id || "")}">
      <div class="wfformh"><strong>${wfForm.id ? "Edit the rule" : "A rule of Elysium Pro's own"}</strong><span class="wfbadge draft">draft</span></div>
      <div class="wfformgrid">
        <label><span>What</span>${sel("kind", [["text", "Text"], ["email", "Email"], ["task", "Task"], ["move", "Move the lead"]], kind)}</label>
        <label><span>Pipeline</span>${sel("pipeline", pipes.map((p) => [p, p]), f.pipeline)}</label>
        <label><span>Stage</span>${sel("stage", stages.map((s) => [s, s]), f.stage)}</label>
        <label><span>Day</span><input type="number" class="lsin" name="day" min="1" max="3650" value="${cesc(String(f.day || 1))}" required><small>Day 1 is the day it gets there, in business days</small></label>
        <label><span>Around</span>${sel("hour", [...Array(24).keys()].filter((h) => h >= 7 && h <= 19).map((h) => [String(h), hour(h)]), f.hour == null ? "" : String(f.hour), "any time")}</label>
        <label><span>Language</span>${sel("lang", [["en", "English"], ["es", "Spanish"]], f.lang || "en")}</label>
        ${kind === "email" ? `<label class="wfwide"><span>Subject</span><input type="text" class="lsin" name="subject" value="${cesc(f.subject || "")}" maxlength="200" required></label>` : ""}
        ${kind === "task" ? `<label class="wfwide"><span>Task title</span><input type="text" class="lsin" name="title" value="${cesc(f.title || "")}" maxlength="200" required></label><label><span>For</span>${sel("who", [["producer", "the lead's producer"], ["front desk", "the front desk"], ["service", "the service team"]], f.who || "producer")}</label>` : ""}
        ${kind === "move" ? `<label class="wfwide"><span>Move to</span>${sel("to_stage", allStages, f.to_stage)}</label>` : ""}
        ${kind !== "move" ? `<label class="wfwide"><span>${kind === "task" ? "Task description (optional)" : "Wording"}</span><textarea class="lsin" name="body" rows="4" maxlength="2000"${kind === "task" ? "" : " required"} placeholder="{first} is the lead's first name, {producer} the producer's">${cesc(f.body || "")}</textarea></label>` : ""}
        <fieldset class="wfwide wfsrcs"><legend>Lead sources <small>(none ticked = every source)</small></legend>${o.sources.filter((src) => !/^\(|^Unsorted$/.test(src)).map((src) => `<label class="wfck"><input type="checkbox" name="sources" value="${cesc(src)}"${(f.sources || []).includes(src) ? " checked" : ""}> ${cesc(src)}</label>`).join("")}</fieldset>
        <label class="wfwide"><span>Note</span><input type="text" class="lsin" name="note" value="${cesc(f.note || "")}" maxlength="500" placeholder="why, or what it replaces"></label>
      </div>
      <div class="wfmark"><button type="submit" class="btn tkpri"${wfBusy ? " disabled" : ""}>${wfForm.id ? "Save" : "Add the draft"}</button><button type="button" class="btn" data-cancelrule="1">Cancel</button>
        ${wfMsg && wfMsg.err ? `<span class="wfbad">${cesc(wfMsg.err)}</span>` : ""}</div>
    </form>`;
  }
  function row(r) {
    if (r.own) return ownRow(r);
    const m = (D.marks || {})[r.key] || {};
    const open = !!wfExp[r.key];
    const g = F.source ? (r.groups || []).find((x) => x.name === F.source) : null;
    const leads = r.kind === "cycle" ? `${n(r.fired)} leads` : g ? `${n(g.n)} of ${n(r.leads)} leads` : `${n(r.leads)} lead${r.leads === 1 ? "" : "s"}`;
    const back = r.kind === "text" ? `${r.replied_pct}% wrote back${r.opted_out ? ` · <span class="wfbad">${n(r.opted_out)} opted out</span>` : ""}`
      : r.kind === "email" ? `${pct(r.opened, r.fired)}% opened · ${pct(r.replied, r.fired)}% wrote back` : "";
    const lang = r.kind !== "cycle" && r.lang === "es" ? `<span class="wflang">Spanish</span>` : "";
    const mark = m.mark ? `<span class="wfbadge ${m.mark}">${m.mark[0].toUpperCase() + m.mark.slice(1)}</span>` : "";
    const noteDot = m.note ? `<span class="wfnotedot" title="${cesc(m.note)}">✎</span>` : "";
    return `<li class="wfev wf-${r.kind}${m.mark ? " m-" + m.mark : ""}${open ? " open" : ""}${openSugs(r.key).length ? " hl" : ""}" id="wf-${cesc(r.key)}">
      <button type="button" class="wfrow" data-open="${cesc(r.key)}" aria-expanded="${open}">
        <span class="wfico" title="${KIND_WORD[r.kind]}">${ICON[r.kind]}</span>
        <span class="wftxt"><span class="wfkind">${KIND_WORD[r.kind]}</span> ${cesc(excerpt(r))}${r.aka && r.aka.length ? ` <small class="wfaka">the text of ${r.aka.map((a) => `“${cesc(a)}”`).join(" / ")}</small>` : ""}</span>
        <span class="wfmeta">${sugBadge(r.key)}${lang}${mark}${noteDot}<span class="wfn">${leads}</span>${back ? `<span class="wfback">${back}</span>` : ""}<span class="wfarrow">${open ? "▲" : "▼"}</span></span>
      </button>
      ${open ? `<div class="wfdetail">${detail(r)}</div>` : ""}
    </li>`;
  }

  // ---- the timeline ----
  function timelineHtml(R) {
    const sm = stageMap(R);
    const rules = allRules(R).concat(ownRules()).filter(passes);
    const byPipe = {}, ownAt = {};
    rules.forEach((r) => {
      const p = placeOf(r, sm, R);
      if (F.pipeline && p.pipeline !== F.pipeline) return;
      const P = byPipe[p.pipeline] || (byPipe[p.pipeline] = { stages: {} });
      const S = P.stages[p.stage] || (P.stages[p.stage] = { ord: p.ord, days: {}, n: 0, az: {} });
      if (p.az && p.az !== p.stage) S.az[p.az] = (S.az[p.az] || 0) + 1;
      const d = r.key === "cycle:park" ? null : dayN(r.day);
      if (r.own) ownAt[p.pipeline + "|" + p.stage] = true;
      const k = d == null ? "none" : String(d);
      (S.days[k] || (S.days[k] = [])).push(r); S.n++;
    });
    const pipes = Object.keys(byPipe).sort((a, b) => (PIPE_ORDER.indexOf(a) + 1 || 99) - (PIPE_ORDER.indexOf(b) + 1 || 99) || a.localeCompare(b));
    if (!pipes.length) return `<div class="empty">No rule matches these filters.</div>`;
    const addBtn = (pn, sn) => (canEdit() && myStages(R, pn).includes(sn) ? `<button type="button" class="ghost tksmall wfaddhere" data-addrule="${cesc(pn + "|" + sn)}" title="Add a rule of Elysium Pro's own at this stage">＋ Add here</button>` : "");
    const kindOrd = { text: 0, email: 1, task: 2, cycle: 3 };
    void ownAt;
    return pipes.map((pn) => {
      const P = byPipe[pn];
      const stages = Object.keys(P.stages).sort((a, b) => P.stages[a].ord - P.stages[b].ord || a.localeCompare(b));
      const total = stages.reduce((a, s) => a + P.stages[s].n, 0);
      const az = [...new Set(stages.flatMap((sn) => Object.keys(P.stages[sn].az).map(azPipe).concat(azPipe(sn) ? [azPipe(sn)] : [])).filter(Boolean))];
      return `<section class="wfpipe">
        <h2 class="wfpipeh"><span>${cesc(pn)}</span><small>${az.length ? `AgencyZoom's ${az.map((x) => `“${cesc(x)}”`).join(", ")} · ` : ""}${n(total)} rule${total === 1 ? "" : "s"}</small></h2>
        ${stages.map((sn) => {
          const S = P.stages[sn];
          const days = Object.keys(S.days).sort((a, b) => (a === "none" ? 1e9 : +a) - (b === "none" ? 1e9 : +b));
          return `<div class="wfstage">
            <h3 class="wfstageh">${cesc(stageName(sn))}<small>${n(S.n)}</small>${Object.keys(S.az).length ? `<small class="wfazst" title="AgencyZoom's own stage names folded in here">${Object.keys(S.az).map(cesc).join(" · ")}</small>` : ""}${addBtn(pn, sn)}</h3>
            ${wfForm && !wfForm.id && wfForm.at === pn + "|" + sn ? formHtml(R) : ""}
            <ol class="wftl">${days.map((dk) => {
              const d = dk === "none" ? null : +dk;
              const list = S.days[dk].sort((a, b) => kindOrd[a.kind] - kindOrd[b.kind] || b.fired - a.fired);
              return `<li class="wfday"><div class="wfdaylab"><b>${dayLabel(d)}</b><small>${daySub(d)}</small></div><ul class="wfevs">${list.map(row).join("")}</ul></li>`;
            }).join("")}</ol>
          </div>`;
        }).join("")}
      </section>`;
    }).join("");
  }
  // the page's own suggestions box, and Frank's list of everything still open
  function sugBoxHtml() {
    const all = (D.suggestions || []), open = all.filter((x) => !x.done);
    const onRules = open.filter((x) => x.key !== "general");
    const name = (key) => { const r = allRules(D.report || {}).concat(ownRules()).find((x) => x.key === key); return r ? (r.own ? excerpt(r) : (r.title || key)) : key; };
    const where = canEdit() && onRules.length ? `<ul class="wfsugwhere">${onRules.map((x) => `<li><button type="button" class="linkish" data-goto="${cesc(x.key)}">${cesc(name(x.key).slice(0, 80))}</button> <small class="lsmute">${cesc(x.by.split(" ")[0])}: ${cesc(x.text.slice(0, 120))}</small></li>`).join("")}</ul>` : "";
    return `<details class="wfsugbox"${open.length || wfSug === "general" ? " open" : ""}><summary>💡 Suggestions${open.length ? ` <span class="wfbadge sug">${open.length} open</span>` : ""}${canEdit() ? "" : " <small class=\"lsmute\">-- what you would change; Frank reads these</small>"}</summary>
      ${canEdit() ? `<p class="lsmute">${open.length ? `${open.length} open, ${onRules.length} on rules (💡 on the row; open the rule to tick it done).` : "Nothing open. The ops team leaves suggestions here and on any rule."}</p>${where}` : `<p class="lsmute">Open any rule for a <b>Suggest</b> button, or use the box here for the page as a whole. A rule with an open suggestion carries 💡 until Frank ticks it done.</p>`}
      ${sugHtml("general", true)}
    </details>`;
  }
  function movesHtml(R) {
    const parked = Object.entries(R.parked_days || {}).map(([k, v]) => `<span class="wfchip">${cesc(stageName(k))} <small>${v.median} days parked · ${n(v.n)}</small></span>`).join("");
    const trans = (R.transitions || []).slice(0, 20).map((t) => `<tr><td>${cesc(stageName(t.from))}</td><td>→</td><td>${cesc(stageName(t.to))}</td><td>${t.who === "automation" ? "<span class=\"wfauto\">automation</span>" : "a person"}</td><td class="num">${n(t.n)}</td></tr>`).join("");
    return `<details class="wfmoves"><summary>Every stage move in the period, and how long leads stay parked</summary>
      ${parked ? `<div class="wfchips"><span class="wflab">How long a lead stays parked before each return</span>${parked}</div>` : ""}
      <div class="scroll"><table class="tktab wftrans"><thead><tr><th>From</th><th></th><th>To</th><th>Who</th><th class="num">Leads</th></tr></thead><tbody>${trans}</tbody></table></div></details>`;
  }

  function repaint() {
    const v = $("#view");
    const R = D && D.report;
    const counts = {};
    if (R) allRules(R).forEach((r) => { if (F.small || r.kind === "cycle" || r.leads >= MIN_LEADS) counts[r.kind] = (counts[r.kind] || 0) + 1; });
    const tiles = KINDS.map(([k, l, c]) => `<button type="button" class="tktile${F.kinds[k] ? " on" : " off"}" data-wfkind="${k}" style="--th:${c}" title="${F.kinds[k] ? "Hide" : "Show"} ${l.toLowerCase()}"><span>${l}</span><strong>${!R ? "…" : n(counts[k] || 0)}</strong></button>`).join("");
    const marked = Object.values((D && D.marks) || {});
    const tally = marked.length ? `<span class="lsbadge lsok">${marked.filter((m) => m.mark === "keep").length} keep · ${marked.filter((m) => m.mark === "change").length} change · ${marked.filter((m) => m.mark === "drop").length} drop</span>` : "";
    let body, filters = "";
    if (!R) body = `<div class="empty">The read has not run yet. It reads the last 90 days' active leads' notes from AgencyZoom and rebuilds the rules from what they sent; it runs from the nightly's environment in the evening.</div>`;
    else {
      const o = options(R);
      const sel = (name, label, list, cur, any) => `<label class="wff"><span>${label}</span><select class="lsin" data-wff="${name}"><option value="">${any}</option>${list.map(([val, txt]) => `<option value="${cesc(val)}"${val === cur ? " selected" : ""}>${cesc(txt)}</option>`).join("")}</select></label>`;
      filters = `<div class="wffilters">
        ${sel("source", "Lead source", o.sources.map((s) => [s, s]), F.source, "Every source")}
        ${sel("pipeline", "Pipeline", o.pipes.map((p) => [p, p]), F.pipeline, "Every pipeline")}
        ${sel("lang", "Language", [["en", "English"], ["es", "Spanish"]], F.lang, "Any language")}
        <label class="wff wfq"><span>Find</span><input type="search" class="lsin" data-wff="q" value="${cesc(F.q)}" placeholder="a word in the wording"></label>
        <label class="wff wfck"><input type="checkbox" data-wff="small"${F.small ? " checked" : ""}> include rules under ${MIN_LEADS} leads</label>
        ${F.source || F.pipeline || F.lang || F.q ? `<button type="button" class="ghost tksmall" data-wfclear="1">Clear</button>` : ""}
        ${canEdit() ? `<button type="button" class="btn tkpri wfaddbtn" data-addrule="">＋ Add a rule</button>` : ""}
      </div>
      ${wfForm && !wfForm.id && !wfForm.at ? formHtml(R) : ""}
      ${sugBoxHtml()}`;
      body = timelineHtml(R) + movesHtml(R);
    }
    v.innerHTML = `<section class="tkpage wfpage">
      <div class="tkhead"><div class="tktiles">${tiles}</div>${tally}</div>
      ${wfMsg ? `<p class="tkmsg ${wfMsg.err ? "bad" : "good"}">${cesc(wfMsg.err || wfMsg.ok)}</p>` : ""}
      <p class="lsintro">What AgencyZoom's automations actually do, read back from the leads${R ? ` -- the last ${R.days} days, ${n(R.leads_read)} leads' notes, as of ${cesc(R.built)}` : ""}, laid out the way a lead sees them: pipeline by pipeline, stage by stage, from the day it gets there. AgencyZoom does not hand out its rules, so each is rebuilt from what it sent. Open a row for the wording and what came back${canEdit() ? "; mark it <b>Keep</b>, <b>Change</b> or <b>Drop</b> and say why -- that is the brief for the rules Elysium Pro runs itself" : ", and <b>Suggest</b> what you would change"}.</p>
      ${filters}
      ${body}
      <p class="tkfoot">Elysium Pro's own CRM. Nothing here changes AgencyZoom. A rule you add is Elysium Pro's own, a draft on the timeline beside AgencyZoom's until the CRM runs it. Texts carry the rule that sent them; emails are known by their template subject; a task counts when the same wording went to five or more leads. The day is counted the way AgencyZoom counts it: Day 1 is the day the lead got to the stage, in business days, and each rule sits on its usual day (the median over every time it fired); a task's day is the day it was due. A task wording the Day 2, 4 and 7 reminders share is listed once, named after them.</p>
    </section>`;
    const f = v.querySelector(".lsform input[autofocus]"); if (f) f.focus();
  }
  async function refresh(msg) {
    wfMsg = msg || null;
    try { D = await api("automations"); } catch (e) { if (view === "workflows") $("#view").innerHTML = `<div class="empty">${cesc(e.message)}</div>`; return; }
    if (view !== "workflows") return;   // another page was opened while this loaded
    repaint();
  }
  async function act(fn, ok) {
    if (wfBusy) return;
    wfBusy = true;
    try { const r = await fn(); if (r && r.marks) D.marks = r.marks; wfNote = null; wfMsg = ok ? { ok } : null; }
    catch (e) { wfMsg = { err: e.message }; }   // a form stays open with the error beside its button
    wfBusy = false; repaint();
  }
  const onPage = () => !!$("#view").querySelector(".wfpage");
  function onClick(e) {
    const t = e.target.closest("[data-wfkind],[data-open],[data-mark],[data-note],[data-cancelnote],[data-wfclear],[data-addrule],[data-editrule],[data-delrule],[data-cancelrule],[data-suggest],[data-cancelsug],[data-sugdone],[data-sugdel],[data-goto]");
    if (!t || !$("#view").contains(t) || !onPage()) return;
    if (t.dataset.suggest != null) { wfSug = t.dataset.suggest; wfMsg = null; repaint(); return; }
    if (t.dataset.cancelsug) { wfSug = null; repaint(); return; }
    if (t.dataset.sugdone) { const [id, done] = t.dataset.sugdone.split(":"); act(() => api("automations/suggest", { op: done === "1" ? "done" : "undone", id }).then((j) => { D.suggestions = j.suggestions; return j; }), done === "1" ? "Done." : "Reopened."); return; }
    if (t.dataset.sugdel) { act(() => api("automations/suggest", { op: "del", id: t.dataset.sugdel }).then((j) => { D.suggestions = j.suggestions; return j; }), "Removed."); return; }
    if (t.dataset.goto) { wfExp[t.dataset.goto] = true; saveWhere(); repaint(); const el = document.getElementById("wf-" + t.dataset.goto); if (el) el.scrollIntoView({ block: "center" }); return; }
    if (t.dataset.addrule != null) {
      const [pipeline, stage] = t.dataset.addrule.split("|");
      wfForm = { id: null, at: t.dataset.addrule, rule: { kind: "text", pipeline: pipeline || "New Business", stage: stage || "", day: 1, lang: "en", sources: [] } };
      if (!wfForm.rule.stage) wfForm.rule.stage = myStages(D.report || {}, wfForm.rule.pipeline)[0] || "Smart-Cycle";
      wfMsg = null; repaint(); const f = $("#view").querySelector(".wfform"); if (f) f.scrollIntoView({ block: "center" }); return;
    }
    if (t.dataset.editrule) { const r = (D.rules || []).find((x) => x.id === t.dataset.editrule); if (!r) return; wfForm = { id: r.id, at: "", rule: Object.assign({}, r) }; wfExp[r.id] = true; wfMsg = null; repaint(); return; }
    if (t.dataset.cancelrule) { wfForm = null; wfMsg = null; repaint(); return; }
    if (t.dataset.delrule) {
      const r = (D.rules || []).find((x) => x.id === t.dataset.delrule);
      if (r && confirm("Delete this draft rule?")) act(() => api("automations/rule", { op: "del", id: r.id }).then((j) => { D.rules = j.rules; return j; }), "Deleted.");
      return;
    }
    if (t.dataset.wfkind) { F.kinds[t.dataset.wfkind] = !F.kinds[t.dataset.wfkind]; saveWhere(); repaint(); return; }
    if (t.dataset.open) { const k = t.dataset.open; if (wfExp[k]) delete wfExp[k]; else wfExp[k] = true; if (wfNote && wfNote !== k) wfNote = null; saveWhere(); repaint(); return; }
    if (t.dataset.wfclear) { F.source = F.pipeline = F.lang = F.q = ""; saveWhere(); repaint(); return; }
    if (t.dataset.mark) {
      const key = t.dataset.key, cur = (D.marks || {})[key] || {};
      const mark = cur.mark === t.dataset.mark ? null : t.dataset.mark;   // the same button again clears it
      act(() => api("automations/mark", { key, mark, note: cur.note || "" }), mark ? "Marked." : "Cleared."); return;
    }
    if (t.dataset.note) { wfNote = t.dataset.note; repaint(); return; }
    if (t.dataset.cancelnote) { wfNote = null; repaint(); return; }
  }
  function onChange(e) {
    const fm = e.target.closest("form.wfform");
    if (fm && $("#view").contains(fm) && wfForm) {
      // the form redraws on a kind or pipeline change (its fields depend on them); the rest is read on submit
      wfForm.rule = readForm(fm);
      if (e.target.name === "kind" || e.target.name === "pipeline") {
        if (e.target.name === "pipeline") wfForm.rule.stage = myStages(D.report || {}, wfForm.rule.pipeline)[0] || "Smart-Cycle";
        repaint();
      }
      return;
    }
    const t = e.target.closest("[data-wff]");
    if (!t || !$("#view").contains(t) || !onPage()) return;
    const k = t.dataset.wff;
    if (k === "small") F.small = t.checked; else F[k] = t.value.trim();
    saveWhere(); repaint();
    if (k === "q") { const i = $("#view").querySelector('[data-wff="q"]'); if (i) { i.focus(); i.setSelectionRange(i.value.length, i.value.length); } }
  }
  let qTimer = null;
  function onInput(e) {
    const t = e.target.closest('[data-wff="q"]');
    if (!t || !$("#view").contains(t) || !onPage()) return;
    clearTimeout(qTimer); qTimer = setTimeout(() => onChange(e), 250);
  }
  function readForm(fm) {
    const fd = new FormData(fm), g = (k) => String(fd.get(k) == null ? "" : fd.get(k));
    return { kind: g("kind"), pipeline: g("pipeline"), stage: g("stage"), day: Number(g("day")) || 1, hour: g("hour") === "" ? null : Number(g("hour")), lang: g("lang") || "en",
      subject: g("subject"), title: g("title"), who: g("who"), to_stage: g("to_stage"), body: g("body"), note: g("note"), sources: fd.getAll("sources").map(String) };
  }
  function onSubmit(e) {
    const sf = e.target.closest("form[data-sugfor]");
    if (sf && $("#view").contains(sf)) {
      e.preventDefault();
      const key = sf.dataset.sugfor, text = String(new FormData(sf).get("text") || "").trim();
      if (!text) return;
      act(() => api("automations/suggest", { op: "add", key, text }).then((j) => { D.suggestions = j.suggestions; wfSug = null; return j; }), "Suggested. Frank sees it on the rule.");
      return;
    }
    const rf = e.target.closest("form.wfform");
    if (rf && $("#view").contains(rf) && wfForm) {
      e.preventDefault();
      const rule = readForm(rf), id = wfForm.id;
      act(() => api("automations/rule", id ? { op: "edit", id, rule } : { op: "add", rule }).then((j) => { D.rules = j.rules; wfForm = null; if (!id) { const last = j.rules[j.rules.length - 1]; if (last) wfExp[last.id] = true; } return j; }), id ? "Saved." : "Added as a draft.");
      return;
    }
    const form = e.target.closest("form[data-notefor]");
    if (!form || !$("#view").contains(form)) return;
    e.preventDefault();
    const key = form.dataset.notefor, cur = (D.marks || {})[key] || {};
    act(() => api("automations/mark", { key, mark: cur.mark || null, note: String(new FormData(form).get("note") || "").trim() }), "Saved.");
  }
  document.addEventListener("click", onClick);
  document.addEventListener("change", onChange);
  document.addEventListener("input", onInput);
  document.addEventListener("submit", onSubmit);

  window.workflowsPaint = async function workflowsPaint() {
    $("#topsub").textContent = "what AgencyZoom's automations run today";
    $("#view").innerHTML = '<div class="empty">Loading…</div>';
    wfMsg = null; wfNote = null; wfSug = null;
    await refresh();
  };

  const css = document.createElement("style");
  css.textContent = `
.wfpage .tktile.off { opacity: .45; } .wfpage .tktile.off strong { text-decoration: line-through; }
.wffilters { display: flex; flex-wrap: wrap; align-items: flex-end; gap: 10px 16px; margin: 6px 0 14px; padding: 10px 12px; border: 1px solid var(--border-strong); border-radius: 12px; background: var(--surface-raised); }
.wff { display: flex; flex-direction: column; gap: 3px; font-size: 12px; color: var(--text-secondary); } .wff > span { font-weight: 700; text-transform: uppercase; letter-spacing: .06em; font-size: 10px; }
.wff select.lsin, .wff input.lsin { min-width: 170px; } .wfq input.lsin { min-width: 220px; }
.wfck { flex-direction: row; align-items: center; gap: 6px; padding-bottom: 6px; }
.wfpipe { margin: 0 0 22px; }
.wfpipeh { display: flex; flex-wrap: wrap; align-items: baseline; gap: 10px; margin: 0 0 8px; padding-bottom: 6px; border-bottom: 2px solid var(--accent); font-size: 20px; }
.wfpipeh small { font-size: 12px; font-weight: 500; color: var(--text-muted); }
.wfstage { margin: 0 0 14px 4px; }
.wfstageh { display: flex; align-items: baseline; gap: 8px; margin: 10px 0 4px; font-size: 15px; } .wfstageh small { font-size: 11px; color: var(--text-muted); font-weight: 600; } .wfstageh .wfazst { font-weight: 500; font-style: italic; }
.wftl { list-style: none; margin: 0; padding: 0 0 0 14px; border-left: 3px solid var(--border-strong); }
.wfday { position: relative; padding: 2px 0 10px 16px; }
.wfday::before { content: ""; position: absolute; left: -23px; top: 9px; width: 13px; height: 13px; border-radius: 50%; background: var(--accent); border: 3px solid var(--surface); box-shadow: 0 0 0 2px var(--accent); }
.wfdaylab { display: flex; align-items: baseline; gap: 8px; margin: 0 0 4px; } .wfdaylab b { font-size: 14px; } .wfdaylab small { font-size: 12px; color: var(--text-muted); }
.wfevs { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: minmax(0, 1fr); gap: 4px; }
.wfev { min-width: 0; border: 1px solid var(--border); border-left: 5px solid var(--border-strong); border-radius: 10px; background: var(--surface); }
.wfev.wf-text { border-left-color: var(--accent); } .wfev.wf-email { border-left-color: var(--s4, #d9a21b); } .wfev.wf-task { border-left-color: var(--s3, #7a8); } .wfev.wf-cycle { border-left-color: var(--good); }
.wfev.m-keep { background: color-mix(in oklab, var(--good) 8%, var(--surface)); } .wfev.m-change { background: color-mix(in oklab, var(--s4, #d9a21b) 10%, var(--surface)); } .wfev.m-drop { background: color-mix(in oklab, var(--bad) 8%, var(--surface)); }
.wfrow { display: flex; min-width: 0; align-items: center; gap: 10px; width: 100%; text-align: left; font: inherit; color: inherit; background: none; border: 0; padding: 7px 10px; cursor: pointer; border-radius: 10px; }
.wfrow:hover { background: color-mix(in oklab, var(--accent) 6%, transparent); }
.wfico { flex: 0 0 auto; font-size: 15px; width: 22px; text-align: center; }
.wftxt { flex: 1 1 auto; min-width: 0; font-size: 13.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.wfev.open .wftxt { white-space: normal; }
.wfaka { color: var(--text-muted); font-size: 12px; }
.wfkind { font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: .07em; color: var(--text-muted); margin-right: 4px; }
.wfmeta { flex: 0 0 auto; display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-secondary); white-space: nowrap; }
.wfn { font-weight: 700; } .wfback { color: var(--text-muted); } .wfarrow { font-size: 10px; color: var(--text-muted); }
.wflang { font-size: 10px; font-weight: 800; letter-spacing: .05em; text-transform: uppercase; padding: 1px 7px; border-radius: 999px; background: color-mix(in oklab, var(--s4, #d9a21b) 22%, var(--surface)); color: var(--text); }
.wfbadge { font-size: 10px; font-weight: 800; letter-spacing: .05em; text-transform: uppercase; padding: 1px 7px; border-radius: 999px; color: #fff; }
.wfbadge.draft { background: var(--text-secondary); }
.wfbadge.sug { background: #e0a800; color: #1d1a14; }
.wfev.hl { box-shadow: inset 4px 0 0 #e0a800, 0 0 0 2px color-mix(in oklab, #e0a800 55%, transparent); }
.wfsugs { margin-top: 8px; } .wfsugs.big { margin-top: 4px; }
.wfsuglist { list-style: none; margin: 0 0 6px; padding: 0; display: grid; gap: 4px; }
.wfsug { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding: 6px 10px; border-radius: 8px; background: color-mix(in oklab, #e0a800 14%, var(--surface)); border-left: 4px solid #e0a800; font-size: 13px; }
.wfsug.done { opacity: .6; border-left-color: var(--good); background: color-mix(in oklab, var(--good) 8%, var(--surface)); } .wfsug.done .wfsugtxt { text-decoration: line-through; }
.wfsugtxt { flex: 1 1 260px; }
.wfsugbox { margin: 6px 0 14px; padding: 8px 12px; border: 1px solid #e0a800; border-radius: 12px; background: color-mix(in oklab, #e0a800 6%, var(--surface)); } .wfsugbox summary { cursor: pointer; font-weight: 700; }
.wfsugwhere { margin: 4px 0 8px; padding-left: 18px; font-size: 13px; } .wfsugwhere li { margin: 2px 0; }
.linkish { font: inherit; color: var(--accent); background: none; border: 0; padding: 0; cursor: pointer; text-decoration: underline; }
.wfev.own { border-style: dashed; background: color-mix(in oklab, var(--accent) 5%, var(--surface)); }
.wfdraftnote { flex-basis: 100%; font-size: 12px; color: var(--text-muted); }
.wfaddhere { margin-left: auto; } .wfaddbtn { margin-left: auto; align-self: flex-end; }
.wfform { margin: 6px 0 12px; padding: 12px 14px; border: 2px dashed var(--accent); border-radius: 12px; background: var(--surface); }
.wfformh { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.wfformgrid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px 14px; }
.wfformgrid label { display: flex; flex-direction: column; gap: 3px; font-size: 12px; color: var(--text-secondary); }
.wfformgrid label > span, .wfformgrid legend { font-weight: 700; text-transform: uppercase; letter-spacing: .06em; font-size: 10px; }
.wfformgrid label small { font-weight: 500; text-transform: none; letter-spacing: 0; color: var(--text-muted); }
.wfformgrid .lsin { width: 100%; box-sizing: border-box; } .wfformgrid textarea.lsin { font: inherit; resize: vertical; }
.wfwide { grid-column: 1 / -1; }
.wfsrcs { border: 1px solid var(--border); border-radius: 10px; padding: 6px 10px 8px; display: flex; flex-wrap: wrap; gap: 4px 14px; }
.wfsrcs .wfck { padding: 0; font-size: 12px; }
@media (max-width: 900px) { .wfformgrid { grid-template-columns: 1fr; } }
.wfbadge.keep { background: var(--good); } .wfbadge.change { background: var(--s4, #d9a21b); } .wfbadge.drop { background: var(--bad); }
.wfnotedot { color: var(--accent); font-weight: 700; cursor: help; }
.wfdetail { padding: 2px 12px 10px 42px; border-top: 1px dashed var(--border); }
.wftpl { margin: 8px 0; padding: 8px 12px; border-left: 3px solid var(--accent); background: color-mix(in oklab, var(--accent) 7%, var(--surface)); font-size: 14px; white-space: pre-wrap; }
.wfwhen { margin: 4px 0 8px; font-size: 14px; color: var(--text-secondary); } .wfcame { margin: 6px 0 4px; font-size: 14px; }
.wfgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 18px; }
.wfchips { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin: 4px 0; }
.wflab { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; color: var(--text-muted); margin-right: 4px; }
.wfchip { font-size: 12px; padding: 2px 8px; border-radius: 999px; border: 1px solid var(--border-strong); } .wfchip small { color: var(--text-muted); }
.wfhist { display: flex; align-items: flex-end; gap: 6px; height: 64px; margin-top: 4px; }
.wfbar { display: flex; flex-direction: column; align-items: center; justify-content: flex-end; min-width: 44px; height: 100%; }
.wfbar i { display: block; width: 26px; background: var(--accent); border-radius: 4px 4px 0 0; }
.wfbar span { font-size: 10px; color: var(--text-muted); margin-top: 2px; white-space: nowrap; }
.wfmark { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-top: 8px; padding-top: 8px; border-top: 1px dashed var(--border); }
.wfmk { font: inherit; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 999px; border: 1px solid var(--border-strong); background: var(--surface-raised); color: var(--text-secondary); cursor: pointer; }
.wfmk.keep.on { background: var(--good); border-color: var(--good); color: #fff; } .wfmk.change.on { background: var(--s4, #d9a21b); border-color: var(--s4, #d9a21b); color: #fff; } .wfmk.drop.on { background: var(--bad); border-color: var(--bad); color: #fff; }
.wfnote { flex-basis: 100%; font-size: 13px; color: var(--text-secondary); font-style: italic; }
.wfbad { color: var(--bad); font-weight: 700; } .wfauto { color: var(--accent); font-weight: 700; }
.wfmoves { margin: 10px 0; padding: 8px 12px; border: 1px solid var(--border-strong); border-radius: 12px; background: var(--surface); } .wfmoves summary { cursor: pointer; font-weight: 700; }
.wftrans td.num, .wftrans th.num { text-align: right; }
@media (max-width: 900px) { .wfgrid { grid-template-columns: 1fr; } .wfrow { flex-wrap: wrap; } .wftxt { flex-basis: 100%; white-space: normal; } .wfmeta { padding-left: 32px; } }
`;
  document.head.appendChild(css);
})();
