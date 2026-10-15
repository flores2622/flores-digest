/* The lead page -- CRM.md phase 3 (Frank, 2026-10-13: "go"). Sales Center >
   Leads, shown only to whoever /api/crm answers (site/crm.js: staff.json's
   `crm` -- Frank alone for now); for anyone else the page never enters the
   menu or the search, and openLead falls back to the coaching card.

   What it is: one screen per lead, the way AgencyZoom's lead screen is used
   today -- who they are, where they sit (Frank's pipeline and stage names,
   AgencyZoom's beside them), the producer, the source, the household and its
   policies once sold, the quotes, the tasks (Done on each), the household's
   SRs, the stage history and every note newest first (notes, texts, emails,
   calls, tasks, stage moves, the automations' own lines) with a filter -- and
   the writes the CRM already takes: a typed note, a stage move, Mark sold, a
   new task. A lead's coaching card is a click away (openLeadCard), and the
   coaching cards and the Tasks page open the lead page in turn (any element
   with data-ldopen). The picker (no lead chosen) searches by name or phone
   and lists the leads worked most recently.

   Uses the board's own helpers ($, cesc, escAttr, pbadge, DOT, azTodayDate,
   isoDate, fmtPhone, goView, openLeadCard, AZ_URL), so it loads after
   index.html's main script and after tasks.js (it waits on CRM_READY).
   Nothing here reads AgencyZoom. */
(function () {
  const FILTERS = [["all", "Everything"], ["note", "Notes"], ["text", "Texts"], ["email", "Emails"], ["call", "Calls"], ["task", "Tasks"], ["stage", "Stages"], ["system", "System"]];
  const TYPES = [["call", "Call"], ["text", "Text"], ["email", "Email"], ["todo", "To do"]];
  const STATUS = { 0: "Open", 2: "Sold", 3: "Lost", 5: "X-dated" };
  let LK = null;                       // /api/crm/lookups
  let ldId = null, ldName = "";        // the lead on screen (null: the picker)
  let P = null;                        // /api/crm/leads/<id>/page
  let ldFilter = "all", ldForm = null, ldBusy = false, ldMsg = null, ldErr = "";
  let ldOpenTask = {};                 // task id -> true (its Done form is open)
  let ldQ = "", ldHits = null, ldRecent = null, ldWho = "", ldDoneOpen = false, ldEventsOpen = false;
  try { const w = JSON.parse(sessionStorage.getItem("lead-where") || "{}"); if (w.id) { ldId = w.id; ldName = w.name || ""; } if (FILTERS.some(([k]) => k === w.filter)) ldFilter = w.filter; if (typeof w.who === "string") ldWho = w.who; } catch (_) {}

  const first = n => String(n || "").split(" ")[0];
  const today = () => isoDate(azTodayDate());
  const person = id => (LK && LK.employees || []).find(e => String(e.id) === String(id)) || null;
  const badge = id => { const p = person(id); return p ? (DOT[p.name] ? pbadge(DOT[p.name], first(p.name)) : `<b>${cesc(first(p.name))}</b>`) : '<span class="ldmute">nobody</span>'; };
  const saveWhere = () => { try { sessionStorage.setItem("lead-where", JSON.stringify({ id: ldId, name: ldName, filter: ldFilter, who: ldWho })); } catch (_) {} };
  const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const clock = s => { if (!s || s.length < 16) return ""; const [h, m] = s.slice(11, 16).split(":").map(Number); return `${h % 12 || 12}:${String(m).padStart(2, "0")} ${h < 12 ? "AM" : "PM"}`; };
  const dayOf = s => { if (!s) return ""; const d = new Date(s.slice(0, 10) + "T12:00:00Z"); return `${MONTHS[d.getUTCMonth()]} ${d.getUTCDate()}${d.getUTCFullYear() !== new Date().getFullYear() ? ", " + d.getUTCFullYear() : ""}`; };
  const dayLong = s => { const d = new Date(s.slice(0, 10) + "T12:00:00Z"); const t = today(); return (s.slice(0, 10) === t ? "Today · " : "") + `${DAYS[d.getUTCDay()]}, ${MONTHS[d.getUTCMonth()]} ${d.getUTCDate()}, ${d.getUTCFullYear()}`; };
  const when = s => s ? `${dayOf(s)}${s.length >= 16 && s.slice(11, 16) !== "00:00" ? " · " + clock(s) : ""}` : "—";
  const money = n => n == null ? "—" : "$" + Math.round(+n).toLocaleString("en-US");
  const tel = p => p ? `<a href="tel:${cesc(String(p).replace(/[^\d+]/g, ""))}">${cesc(fmtPhone(p))}</a>` : "";
  /* AgencyZoom's notes come as HTML (a <p>, <a href='javascript:...'>, <br>,
     an <audio> player, a whole Gmail quote). Only the words reach the page. */
  function plain(html) {
    let s = String(html || "");
    s = s.replace(/<(audio|style|script)[\s\S]*?<\/\1>/gi, "").replace(/<div class="gmail_quote[\s\S]*$/i, "").replace(/<blockquote[\s\S]*?<\/blockquote>/gi, "");
    s = s.replace(/<br\s*\/?>\s*/gi, "\n").replace(/<\/(p|div|li|tr|h\d)>\s*/gi, "\n").replace(/<hr\s*\/?>/gi, "\n").replace(/<[^>]+>/g, "");
    const t = document.createElement("textarea"); t.innerHTML = s;
    return t.value.replace(/\r/g, "").replace(/[ \t]+\n/g, "\n").replace(/\n{3,}/g, "\n\n").trim();
  }

  async function api(path, body) {
    const r = await fetch("/api/crm/" + path, body ? { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) } : { cache: "no-store" });
    let j = null; try { j = await r.json(); } catch (_) {}
    if (!r.ok) { const e = new Error((j && j.error) || `HTTP ${r.status}`); e.status = r.status; throw e; }
    return j;
  }

  // Unhide the page for whoever the Worker lets in (the same gate as Tasks).
  window.LEAD_READY = (async function () {
    const ok = await (window.CRM_READY || Promise.resolve(false));
    if (!ok) return false;
    try { LK = await api("lookups"); } catch (_) { return false; }
    window.CRM_OK = true;   // the coaching cards and the Tasks page show their "Lead page" buttons
    if (!CENTERS.salescenter.some(([k]) => k === "lead")) CENTERS.salescenter.push(["lead", "Leads"]);
    SEARCH_PAGES.push(["Leads", "Sales Center · the CRM's lead page: notes, texts, tasks, stage, household", "lead"]);
    paintCenterBar();
    return true;
  })();
  /** Open a lead's page (from a coaching card, the Tasks page, the picker).
      Before the CRM has let this login in, the coaching card is the page. */
  window.openLead = async function openLead(id, name) {
    if (!(await window.LEAD_READY)) { openLeadCard({ id, l: name || "" }); return; }
    ldId = String(id); ldName = name || ""; ldForm = null; ldMsg = null; ldOpenTask = {}; ldDoneOpen = false; ldEventsOpen = false; P = null;
    saveWhere();
    if (view !== "lead") goView("lead"); else await leadPaint();
  };
  // Any element on the board with data-ldopen opens that lead here (capture,
  // so a button inside a coaching card's summary does not fold the card).
  document.addEventListener("click", e => {
    const t = e.target.closest("[data-ldopen]");
    if (!t) return;
    e.preventDefault(); e.stopPropagation();
    openLead(t.dataset.ldopen, t.dataset.ldname || "");
  }, true);

  /* ---- the picker ------------------------------------------------------------ */
  async function loadRecent() {
    try { ldRecent = (await api(`leads?limit=40${ldWho ? "&assignedTo=" + encodeURIComponent(ldWho) : ""}`)).leads || []; } catch (e) { ldRecent = []; ldErr = e.message; }
  }
  let findTimer = 0;
  async function find(q) {
    ldQ = q;
    if (q.trim().length < 2) { ldHits = null; repaint(); return; }
    try { const r = await api(`search?q=${encodeURIComponent(q.trim())}`); if (ldQ === q) { ldHits = { leads: r.leads || [], hh: (r.customers || []).length }; repaint(); } }
    catch (e) { ldHits = { leads: [], hh: 0, err: e.message }; repaint(); }
  }
  const leadRow = l => `<tr class="ldpick" data-ldopen="${l.id}" data-ldname="${escAttr(l.name || "")}" tabindex="0" role="button">
    <td><b>${cesc(l.name || l.businessName || "#" + l.id)}</b>${l.businessName && l.name ? ` <small class="ldmute">${cesc(l.businessName)}</small>` : ""}</td>
    <td>${l.phone ? cesc(fmtPhone(l.phone)) : ""}</td><td>${badge(l.assignedTo)}</td>
    <td>${cesc(l.sourceName || l.leadSourceName || "")}${l.sourceDetail ? ` <small class="ldmute">${cesc(l.sourceDetail)}</small>` : ""}</td>
    <td>${statusPill(l)}${l.workflowStageId ? " " + cesc(whereText(l)) : ""}</td><td class="ldwhen">${cesc(when(l.lastActivityDate))}</td></tr>`;
  function pickerHtml() {
    const people = (LK.employees || []).filter(e => e.producer || e.service);
    const table = rows => `<div class="scroll"><table class="ldtab"><thead><tr><th>Lead</th><th>Phone</th><th>Producer</th><th>Source</th><th>Where</th><th>Last activity</th></tr></thead><tbody>${rows.map(leadRow).join("")}</tbody></table></div>`;
    let hits = "";
    if (ldHits) hits = ldHits.err ? `<p class="ldmsg bad">${cesc(ldHits.err)}</p>` : `<h3 class="ldh3">${ldHits.leads.length} lead${ldHits.leads.length === 1 ? "" : "s"} match${ldHits.hh ? ` <small class="ldmute">· ${ldHits.hh} household${ldHits.hh === 1 ? "" : "s"} too (no page yet)</small>` : ""}</h3>${ldHits.leads.length ? table(ldHits.leads) : ""}`;
    return `<section class="ldpage">
      <div class="ldpickhead">
        <input type="search" class="tkin ldq" placeholder="Find a lead by name or phone number" value="${escAttr(ldQ)}" autocomplete="off" autofocus>
        <label class="ldwho">Recent for <select class="tkin" data-ldwho="1"><option value="">everyone</option>${people.map(e => `<option value="${e.id}"${String(e.id) === String(ldWho) ? " selected" : ""}>${cesc(e.name)}</option>`).join("")}</select></label>
      </div>
      ${hits}
      <h3 class="ldh3">Worked most recently</h3>
      ${ldRecent === null ? '<div class="empty">Loading…</div>' : ldRecent.length ? table(ldRecent) : `<div class="empty">No leads on file${ldErr ? ": " + cesc(ldErr) : ""}.</div>`}
      <p class="ldfoot">Elysium Pro's own CRM. A lead's coaching card and the Tasks page open its page here; the search (Ctrl K) still opens coaching cards.</p>
    </section>`;
  }

  /* ---- the page --------------------------------------------------------------- */
  const whereText = l => l.exit && !l.workflowStageId ? l.exit : [l.pipelineName || l.workflowName, l.stageName || l.workflowStageName].filter(Boolean).join(" · ");
  const azWhere = l => l.workflowStageId ? `${l.workflowName} | ${l.workflowStageName}` : "";
  function statusPill(l) {
    const s = l.status, lab = l.exit === "Smart-Cycle" && s === 0 ? "Smart-Cycle" : STATUS[s] || `Status ${s}`;
    const cls = s === 2 ? "ldst-sold" : s === 0 ? (l.exit === "Smart-Cycle" ? "ldst-cycle" : "ldst-open") : "ldst-lost";
    return `<span class="ldst ${cls}">${cesc(lab)}</span>`;
  }
  /** What kind of line a note is on the timeline, and how it reads. */
  function noteView(n) {
    const a = n.attr || {}, t = n.type;
    const who = n.createdByName || (a.createdByName || "").trim() || "";
    const v = { kind: "system", label: t.replace(/_/g, " ").toLowerCase(), who, text: plain(n.body), dir: "", extra: "" };
    if (t === "NOTE" || t === "COMMENT") { v.kind = "note"; v.label = "Note"; }
    else if (t === "TEXT" || t === "TEXT-FAILED") {
      v.kind = "text"; v.dir = a.outbound ? "out" : "in"; v.label = t === "TEXT-FAILED" ? "Text failed" : a.outbound ? "Text sent" : "Text received";
      if (a.triggerRuleId) v.extra = "automation"; if (!a.outbound) v.who = "the lead"; if (a.toNumber) v.extra = [v.extra, "to " + fmtPhone(a.toNumber)].filter(Boolean).join(" · ");
    } else if (t === "EMAIL") {
      v.kind = "email"; v.dir = a.outbound ? "out" : "in"; v.label = a.outbound ? "Email sent" : "Email received";
      v.subject = a.emailSubject || ""; v.text = plain(n.body) || a.emailSnippet || "";
      if (!a.outbound) v.who = "the lead"; const ex = []; if ((a.attachments || []).length) ex.push(`${a.attachments.length} attachment${a.attachments.length === 1 ? "" : "s"}`); if (a.lastOpenDate) ex.push("opened " + when(a.lastOpenDate)); v.extra = ex.join(" · ");
    } else if (t === "CALL") {
      v.kind = "call"; v.dir = a.outbound ? "out" : "in"; v.label = a.outbound ? "Call" : "Call-in";
      const lines = v.text.split("\n").filter(x => !/^(From|To):\s*$/.test(x));
      const st = (lines.find(x => /^Call Status:/i.test(x)) || "").replace(/^Call Status:\s*/i, ""), du = (lines.find(x => /^Duration:/i.test(x)) || "").replace(/^Duration:\s*/i, "").replace(/^\(s\)$/, "");
      const secs = +(du.replace(/\D/g, "") || 0), len = !du ? "" : secs >= 60 ? `${Math.floor(secs / 60)}m ${secs % 60}s` : `${secs}s`;
      v.text = [st && st.replace(/([a-z])([A-Z])/g, "$1 $2").toLowerCase(), len].filter(Boolean).join(" · ") || lines.join("\n");
      const rest = lines.filter(x => !/^(Call Status|Start Time|End Time|Duration):/i.test(x)).join("\n").trim(); if (rest) v.text += "\n" + rest;
    } else if (t === "TASK") { v.kind = "task"; v.label = "Task"; }
    else if (t === "MOVE_STAGE") { v.kind = "stage"; v.label = "Stage"; v.text = v.text.replace(/\s+/g, " "); }
    else if (t === "SOLD") { v.kind = "stage"; v.label = "Sold"; }
    else if (t === "QUOTE") { v.kind = "note"; v.label = "Quote"; }
    else v.text = v.text.replace(/\s+/g, " ");
    if (!v.who && n.origin === "import") v.who = v.kind === "system" ? "AgencyZoom" : "";
    return v;
  }
  function timelineHtml() {
    const notes = P.notes.map(n => ({ n, v: noteView(n) }));
    const counts = {}; for (const { v } of notes) counts[v.kind] = (counts[v.kind] || 0) + 1;
    const chips = FILTERS.map(([k, l]) => `<button type="button" class="ldchip${k === ldFilter ? " on" : ""}" data-ldfilter="${k}">${l}${k === "all" ? ` <small>${notes.length}</small>` : counts[k] ? ` <small>${counts[k]}</small>` : ""}</button>`).join("");
    const shown = notes.filter(({ v }) => ldFilter === "all" || v.kind === ldFilter);
    let out = "", day = "";
    for (const { n, v } of shown) {
      const d = (n.createDate || "").slice(0, 10);
      if (d !== day) { day = d; out += `<div class="ldday">${cesc(dayLong(n.createDate))}</div>`; }
      out += `<div class="ldnote ld-${v.kind}${v.dir ? " ld-" + v.dir : ""}"><div class="ldnhead"><span class="ldtime">${cesc(clock(n.createDate) || "")}</span><span class="ldkind">${cesc(v.label)}</span>${v.who ? `<span class="ldwho2">${cesc(v.who)}</span>` : ""}${v.extra ? `<span class="ldmute">${cesc(v.extra)}</span>` : ""}</div>
        ${v.subject ? `<div class="ldsubj">${cesc(v.subject)}</div>` : ""}${v.text ? `<div class="ldbody">${cesc(v.text)}</div>` : ""}${(n.attachments || []).length ? `<div class="ldmute">${n.attachments.length} attachment${n.attachments.length === 1 ? "" : "s"}</div>` : ""}</div>`;
    }
    return `<div class="ldchips">${chips}</div>${noteForm()}${out || `<div class="empty">Nothing ${ldFilter === "all" ? "on this lead yet" : "of that kind"}.</div>`}`;
  }
  function noteForm() {
    if (ldForm !== "note") return "";
    return `<form class="ldform" data-ldnote="1"><textarea class="tkin ldta" name="body" rows="3" placeholder="What happened, in your words" maxlength="20000" required autofocus></textarea>
      <div class="tkrow"><button type="submit" class="btn tkpri"${ldBusy ? " disabled" : ""}>Save note</button><button type="button" class="btn" data-ldcancel="1">Cancel</button></div></form>`;
  }
  function moveForm() {
    const L = P.lead, groups = new Map();
    for (const o of P.stageOptions) { const g = o.pipelineName || o.workflow; if (!groups.has(g)) groups.set(g, []); groups.get(g).push(o); }
    const opts = [...groups].map(([g, os]) => `<optgroup label="${escAttr(g)}">${os.map(o => `<option value="${escAttr(o.where)}" title="AgencyZoom: ${escAttr(o.where)}"${o.current ? " disabled" : ""}>${cesc(o.stageName || o.stage)}${!o.stageName ? ` (${cesc(o.workflow)})` : ""}${o.current ? " · now" : ""}</option>`).join("")}</optgroup>`).join("");
    const exits = `<optgroup label="Out of the pipeline">${P.exits.map(x => `<option value="${x}"${L.exit === x && !L.workflowStageId ? " disabled" : ""}>${x}${x === "Dead" ? " (lost)" : ""}</option>`).join("")}</optgroup>`;
    return `<form class="ldform" data-ldmove="1"><label>Move to<select class="tkin" name="to" required><option value="">Pick a stage…</option>${opts}${exits}</select></label>
      <label>Why <small class="ldmute">(optional; the loss reason on Dead)</small><input type="text" class="tkin tkwide" name="why" maxlength="500"></label>
      <div class="tkrow"><button type="submit" class="btn tkpri"${ldBusy ? " disabled" : ""}>Move</button><button type="button" class="btn" data-ldcancel="1">Cancel</button></div></form>`;
  }
  function taskForm() {
    const L = P.lead, people = (LK.employees || []).map(e => `<option value="${e.id}"${String(e.id) === String(L.assignedTo) ? " selected" : ""}>${cesc(e.name)}</option>`).join("");
    return `<form class="ldform" data-ldtask="1"><div class="tkgrid">
      <label>Task<input type="text" class="tkin tkwide" name="title" placeholder="Call back about the home quote" maxlength="200" required autofocus></label>
      <label>For<select class="tkin" name="assigneeId" required>${people}</select></label>
      <label>Due<span class="tkrow"><input type="date" class="tkin" name="day" value="${today()}" required><input type="time" class="tkin" name="time" value="09:00"></span></label>
      <label>Kind<select class="tkin" name="type">${TYPES.map(([k, l]) => `<option value="${k}">${l}</option>`).join("")}</select></label>
      <label class="tkspan">Notes<input type="text" class="tkin tkwide" name="comments" placeholder="Optional" maxlength="1000"></label></div>
      <div class="tkrow"><button type="submit" class="btn tkpri"${ldBusy ? " disabled" : ""}>Add task</button><button type="button" class="btn" data-ldcancel="1">Cancel</button></div></form>`;
  }
  function soldForm() {
    return `<form class="ldform" data-ldsold="1"><p>Mark <b>${cesc(P.lead.name)}</b> sold today? The lead becomes a household (its policies hang there) and leaves the pipeline. The policies themselves still come in from AgencyZoom until phase 7.</p>
      <div class="tkrow"><button type="submit" class="btn tkpri"${ldBusy ? " disabled" : ""}>Mark sold</button><button type="button" class="btn" data-ldcancel="1">Cancel</button></div></form>`;
  }
  function headHtml() {
    const L = P.lead, H = P.household;
    const addr = [L.address, [L.city, L.state].filter(Boolean).join(", "), L.zip].filter(Boolean).join(" · ");
    const facts = [
      ["Producer", badge(L.assignedTo)],
      ["Source", `${cesc(L.sourceName || L.leadSourceName || "—")}${L.sourceDetail ? ` <small class="ldmute">${cesc(L.sourceDetail)}</small>` : ""}${L.sourceName && L.leadSourceName && L.sourceName !== L.leadSourceName && L.sourceDetail !== L.leadSourceName ? ` <small class="ldaz" title="AgencyZoom's name">${cesc(L.leadSourceName)}</small>` : ""}`],
      ["Where", `${cesc(whereText(L) || "—")}${azWhere(L) && azWhere(L) !== whereText(L).replace(" · ", " | ") ? ` <small class="ldaz" title="AgencyZoom's pipeline and stage">${cesc(azWhere(L))}</small>` : ""}${L.enterStageDate ? ` <small class="ldmute">since ${cesc(when(L.enterStageDate))}</small>` : ""}${L.lossReason ? ` <small class="ldmute">· ${cesc(L.lossReason)}</small>` : ""}`],
      ["Phone", [tel(L.phone), tel(L.secondaryPhone)].filter(Boolean).join(" · ") || "—"],
      ["Email", L.email ? `<a href="mailto:${escAttr(L.email)}">${cesc(L.email)}</a>` : "—"],
      ["Address", cesc(addr || "—")],
      ["Language", cesc(L.language || "—")],
      ["Created", cesc(when(L.createDate))],
      ["Last activity", cesc(when(L.lastActivityDate))],
      L.quoteDate ? ["Quoted", cesc(when(L.quoteDate))] : null,
      L.soldDate ? ["Sold", cesc(when(L.soldDate))] : null,
      H ? ["Household", `${cesc(H.name)}${H.asCustomerDate ? ` <small class="ldmute">customer since ${cesc(dayOf(H.asCustomerDate))}</small>` : ""}`] : null,
    ].filter(Boolean);
    const openTasks = P.tasks.filter(t => t.status === 0).length;
    return `<div class="ldhead">
      <div class="ldtitle"><h2 class="ldname">${cesc(L.name || L.businessName || "#" + L.id)}</h2>${statusPill(L)}${L.businessName && L.name ? `<span class="ldmute">${cesc(L.businessName)}</span>` : ""}
        <span class="ldmute ldid">#${L.id}${L.azId ? " · AgencyZoom's record" : " · made in Elysium Pro"}</span></div>
      <div class="ldacts">
        <button type="button" class="btn tkpri" data-ldformopen="note"${ldForm === "note" ? " disabled" : ""}>+ Note</button>
        <button type="button" class="btn" data-ldformopen="task"${ldForm === "task" ? " disabled" : ""}>+ Task${openTasks ? ` <small>${openTasks} open</small>` : ""}</button>
        <button type="button" class="btn" data-ldformopen="move"${ldForm === "move" ? " disabled" : ""}>Move stage</button>
        ${L.status !== 2 ? `<button type="button" class="btn" data-ldformopen="sold"${ldForm === "sold" ? " disabled" : ""}>Mark sold</button>` : ""}
        <button type="button" class="ghost" data-ldcard="1">Coaching card</button>
        ${L.azId ? `<a class="ghost ldlink" href="${AZ_URL.lead}${encodeURIComponent(L.azId)}" target="_blank" rel="noopener">AgencyZoom ↗</a>` : ""}
      </div>
      <dl class="ldfacts">${facts.map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join("")}</dl>
      ${ldMsg ? `<p class="ldmsg ${ldMsg.err ? "bad" : "good"}" role="${ldMsg.err ? "alert" : "status"}">${cesc(ldMsg.err || ldMsg.ok)}</p>` : ""}
      ${ldForm === "move" ? moveForm() : ldForm === "task" ? taskForm() : ldForm === "sold" ? soldForm() : ""}
    </div>`;
  }
  function taskRow(t) {
    const late = t.status === 0 && t.dueDate && t.dueDate < today() + " 00:00:00";
    const form = ldOpenTask[t.id] ? `<form class="tkform" data-lddone="${t.id}"><input type="text" class="tkin tkwide" name="comment" placeholder="What happened? (optional)" maxlength="500" autofocus>
      <button type="submit" class="btn tkpri"${ldBusy ? " disabled" : ""}>Mark done</button><button type="button" class="btn" data-ldtaskclose="${t.id}">Cancel</button></form>` : "";
    return `<li class="ldtask${t.status === 1 ? " done" : ""}${late ? " late" : ""}"><div class="ldtaskrow"><span class="ldwhen">${t.status === 1 ? "done " + cesc(when(t.completeDate)) : cesc(when(t.dueDate))}</span>${badge(t.assigneeId)}<b>${cesc(t.title)}</b><span class="tkpill">${cesc((TYPES.find(([k]) => k === t.type) || [, t.type])[1])}</span>
      ${t.status === 0 ? `<button type="button" class="btn tksmall tkpri" data-ldtaskopen="${t.id}">Done</button>` : ""}</div>${t.comments ? `<div class="tkcomm">${cesc(t.comments)}</div>` : ""}${form}</li>`;
  }
  function sideHtml() {
    const L = P.lead, H = P.household;
    const open = P.tasks.filter(t => t.status === 0), done = P.tasks.filter(t => t.status !== 0);
    const pol = P.policies.length ? `<table class="ldtab ldsmall"><thead><tr><th>Policy</th><th>Carrier</th><th>Premium</th><th>Sold</th><th>Status</th></tr></thead><tbody>${P.policies.map(p => `<tr><td><b>${cesc(p.policyTypeName || "")}</b>${p.policyNumber ? `<br><small class="ldmute">${cesc(p.policyNumber)}</small>` : ""}</td><td>${cesc(p.carrierName || "")}</td><td>${money(p.premium)}</td><td>${cesc(dayOf(p.soldDate))}${p.agentName ? `<br><small class="ldmute">${cesc(first(p.agentName))}</small>` : ""}</td><td>${cesc(p.status || "")}${p.expiryDate ? `<br><small class="ldmute">to ${cesc(dayOf(p.expiryDate))}</small>` : ""}</td></tr>`).join("")}</tbody></table>` : `<p class="ldmute">${L.status === 2 ? "No policies on the household yet (they come in from AgencyZoom with the nightly)." : "None yet."}</p>`;
    const quotes = P.quotes.length ? `<ul class="ldlist">${P.quotes.map(q => `<li><b>${cesc(q.policyTypeName || "")}</b> ${cesc(q.carrierName || "")} · ${money(q.premium)}${q.term ? ` / ${q.term} mo` : ""} · ${cesc(q.status || "")} <small class="ldmute">${cesc(when(q.quoteDate))}</small></li>`).join("")}</ul>` : `<p class="ldmute">No quotes on file.${L.quoteDate ? " AgencyZoom dates the last one " + cesc(dayOf(L.quoteDate)) + "." : ""}</p>`;
    const srs = P.serviceTickets.length ? `<ul class="ldlist">${P.serviceTickets.map(s => `<li><b>${cesc(s.subject || "")}</b> <small class="ldmute">${cesc(s.pipelineName || s.workflowName || "")} · ${s.status === 2 ? "completed " + cesc(dayOf(s.completeDate)) + (s.resolutionDesc ? " · " + cesc(s.resolutionDesc) : "") : s.status === 1 ? "open" : "deleted"} · ${cesc(s.csrFirstname || "")}</small></li>`).join("")}</ul>` : `<p class="ldmute">No SRs${H ? "" : " (no household yet)"}.</p>`;
    const moves = P.moves.length ? P.moves.map(m => `<li><span class="ldwhen">${cesc(when(m.at))}</span> ${cesc(m.from || "New lead")} → <b>${cesc(m.to)}</b>${m.movedByName ? ` <small class="ldmute">by ${cesc(first(m.movedByName))}</small>` : ""}${m.lossReason ? ` <small class="ldmute">· ${cesc(m.lossReason)}</small>` : ""}</li>`).join("")
      : P.notes.filter(n => n.type === "MOVE_STAGE").map(n => `<li><span class="ldwhen">${cesc(when(n.createDate))}</span> ${cesc(plain(n.body).replace(/^Lead\s+.*?\s+moved\s+/i, "").replace(/\s+/g, " "))}</li>`).join("");
    const ev = P.events.length ? `<ul class="ldlist ldsmall">${P.events.map(e => `<li><span class="ldwhen">${cesc(when(e.at))}</span> ${cesc(e.action)} <small class="ldmute">${cesc(e.who)}${e.after ? " · " + cesc(JSON.stringify(e.after).slice(0, 120)) : ""}</small></li>`).join("")}</ul>` : `<p class="ldmute">No changes made in Elysium Pro.</p>`;
    return `<div class="ldside">
      <section class="ldbox"><h3>Tasks <small class="ldmute">${open.length} open</small></h3>${open.length ? `<ul class="ldtasks">${open.map(taskRow).join("")}</ul>` : `<p class="ldmute">Nothing open.</p>`}
        ${done.length ? `<details class="ldfold"${ldDoneOpen ? " open" : ""} data-ldfold="done"><summary>${done.length} done</summary><ul class="ldtasks">${done.map(taskRow).join("")}</ul></details>` : ""}</section>
      <section class="ldbox"><h3>Quotes</h3>${quotes}</section>
      <section class="ldbox"><h3>Policies${H ? ` <small class="ldmute">${cesc(H.name)}</small>` : ""}</h3>${pol}</section>
      ${H ? `<section class="ldbox"><h3>Household</h3><dl class="ldfacts one"><div><dt>Name</dt><dd>${cesc(H.name)}${H.azId ? ` <a class="ldaz" href="${AZ_URL.customer}${encodeURIComponent(H.azId)}" target="_blank" rel="noopener">AgencyZoom ↗</a>` : ""}</dd></div><div><dt>Phone</dt><dd>${[tel(H.phone), tel(H.secondaryPhone)].filter(Boolean).join(" · ") || "—"}</dd></div><div><dt>Email</dt><dd>${H.email ? `<a href="mailto:${escAttr(H.email)}">${cesc(H.email)}</a>` : "—"}</dd></div><div><dt>Address</dt><dd>${cesc([H.address, [H.city, H.state].filter(Boolean).join(", "), H.zip].filter(Boolean).join(" · ") || "—")}</dd></div><div><dt>Assigned</dt><dd>${badge(H.assignedTo)}</dd></div><div><dt>Since</dt><dd>${cesc(dayOf(H.asCustomerDate) || "—")}</dd></div></dl></section>` : ""}
      <section class="ldbox"><h3>Service requests</h3>${srs}</section>
      <section class="ldbox"><h3>Stage history</h3>${moves ? `<ul class="ldlist">${moves}</ul>` : `<p class="ldmute">No moves on record.</p>`}</section>
      <details class="ldfold ldbox"${ldEventsOpen ? " open" : ""} data-ldfold="events"><summary>Changes made in Elysium Pro <small class="ldmute">${P.events.length}</small></summary>${ev}</details>
    </div>`;
  }
  function pageHtml() {
    return `<section class="ldpage">
      <p class="ldback"><button type="button" class="ghost" data-ldback="1">◂ All leads</button></p>
      ${headHtml()}
      <div class="ldcols"><div class="ldmain"><h3 class="ldh3">Notes &amp; activity</h3>${timelineHtml()}</div>${sideHtml()}</div>
    </section>`;
  }

  function repaint() {
    const v = $("#view");
    if ($("#view").dataset.view !== "lead") return;
    v.innerHTML = ldId ? (P ? pageHtml() : `<section class="ldpage"><p class="ldback"><button type="button" class="ghost" data-ldback="1">◂ All leads</button></p><div class="empty">${ldErr ? cesc(ldErr) : "Loading " + cesc(ldName || "the lead") + "…"}</div></section>`) : pickerHtml();
    const f = v.querySelector("[autofocus]"); if (f && f.tagName !== "INPUT" || (f && f.classList.contains("ldq") && ldQ)) f.focus(); else if (f) f.focus();
  }
  async function load() {
    try { P = await api(`leads/${encodeURIComponent(ldId)}/page`); ldErr = ""; ldName = P.lead.name || ldName; saveWhere(); }
    catch (e) { P = null; ldErr = e.status === 404 ? `Lead #${ldId} is not in the CRM.` : e.message; }
  }
  async function act(fn, ok) {
    if (ldBusy) return;
    ldBusy = true; repaint();
    try { await fn(); ldForm = null; ldOpenTask = {}; ldMsg = { ok }; await load(); }
    catch (e) { ldMsg = { err: e.message }; }
    ldBusy = false; repaint();
  }

  function onClick(e) {
    const t = e.target.closest("[data-ldfilter],[data-ldformopen],[data-ldcancel],[data-ldcard],[data-ldback],[data-ldtaskopen],[data-ldtaskclose]");
    if (!t || !$("#view").contains(t) || $("#view").dataset.view !== "lead") return;
    if (t.dataset.ldfilter) { ldFilter = t.dataset.ldfilter; saveWhere(); repaint(); return; }
    if (t.dataset.ldformopen) { ldForm = t.dataset.ldformopen; ldMsg = null; repaint(); return; }
    if (t.dataset.ldcancel) { ldForm = null; repaint(); return; }
    if (t.dataset.ldcard) { openLeadCard({ id: ldId, l: ldName }); return; }
    if (t.dataset.ldback) { ldId = null; P = null; ldForm = null; ldMsg = null; saveWhere(); repaint(); if (ldRecent === null) loadRecent().then(repaint); return; }
    if (t.dataset.ldtaskopen) { ldOpenTask = { [t.dataset.ldtaskopen]: true }; repaint(); return; }
    if (t.dataset.ldtaskclose) { ldOpenTask = {}; repaint(); return; }
  }
  function onToggle(e) {
    const d = e.target.closest("[data-ldfold]"); if (!d || $("#view").dataset.view !== "lead") return;
    if (d.dataset.ldfold === "done") ldDoneOpen = d.open; else if (d.dataset.ldfold === "events") ldEventsOpen = d.open;
  }
  function onKey(e) {
    const r = e.target.closest("tr.ldpick"); if (!r || (e.key !== "Enter" && e.key !== " ")) return;
    e.preventDefault(); openLead(r.dataset.ldopen, r.dataset.ldname);
  }
  function onInput(e) {
    const q = e.target.closest(".ldq"); if (!q || $("#view").dataset.view !== "lead") return;
    ldQ = q.value; clearTimeout(findTimer); findTimer = setTimeout(() => find(q.value), 220);
  }
  function onChange(e) {
    const s = e.target.closest("[data-ldwho]"); if (!s || $("#view").dataset.view !== "lead") return;
    ldWho = s.value; saveWhere(); ldRecent = null; repaint(); loadRecent().then(repaint);
  }
  function onSubmit(e) {
    const f = e.target.closest("form"); if (!f || !$("#view").contains(f) || $("#view").dataset.view !== "lead") return;
    const d = Object.fromEntries(new FormData(f).entries());
    if (f.dataset.ldnote) { e.preventDefault(); act(() => api(`leads/${ldId}/notes`, { type: "NOTE", body: d.body }), "Note saved."); }
    else if (f.dataset.ldmove) { e.preventDefault(); act(() => api(`leads/${ldId}/move`, { to: d.to, why: d.why || "" }), `Moved to ${d.to}.`); }
    else if (f.dataset.ldsold) { e.preventDefault(); act(() => api(`leads/${ldId}/sold`, {}), "Marked sold."); }
    else if (f.dataset.ldtask) { e.preventDefault(); act(() => api("tasks", { title: d.title, assigneeId: +d.assigneeId, leadId: +ldId, dueDate: `${d.day} ${d.time || "09:00"}`, type: d.type || "todo", comments: d.comments || "" }), "Task added."); }
    else if (f.dataset.lddone) { e.preventDefault(); act(() => api(`tasks/${f.dataset.lddone}/complete`, { comment: d.comment || "" }), "Task done."); }
  }
  document.addEventListener("click", onClick);
  document.addEventListener("toggle", onToggle, true);
  document.addEventListener("keydown", onKey);
  document.addEventListener("input", onInput);
  document.addEventListener("change", onChange);
  document.addEventListener("submit", onSubmit);

  window.leadPaint = async function leadPaint() {
    const v = $("#view"); v.dataset.view = "lead";
    if (!(await window.LEAD_READY)) { v.innerHTML = '<div class="empty">The CRM is not open to this login.</div>'; return; }
    if (ldId) { if (!P || String(P.lead.id) !== String(ldId)) { repaint(); await load(); } }
    else if (ldRecent === null) { repaint(); await loadRecent(); }
    repaint();
  };

  const css = document.createElement("style");
  css.textContent = `
.ldpage { padding: 4px 0 24px; }
.ldpickhead { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin-bottom: 14px; } .ldq { flex: 1; min-width: 260px; font-size: 16px; padding: 10px 14px; }
.ldh3 { margin: 14px 0 8px; font-size: 15px; } .ldfoot { margin: 12px 0 0; font-size: 12px; color: var(--text-muted); } .ldmute { color: var(--text-muted); font-weight: 500; }
.ldtab { width: 100%; border-collapse: collapse; } .ldtab th, .ldtab td { text-align: left; vertical-align: top; padding: 7px 8px; border-bottom: 1px solid var(--border); font-size: 14px; }
.ldtab th { font-size: 11px; text-transform: uppercase; letter-spacing: .07em; color: var(--text-muted); } .ldtab.ldsmall th, .ldtab.ldsmall td { font-size: 13px; padding: 5px 6px; }
tr.ldpick { cursor: pointer; } tr.ldpick:hover td, tr.ldpick:focus td { background: color-mix(in oklab, var(--accent) 10%, transparent); } tr.ldpick:focus { outline: none; }
.ldwhen { white-space: nowrap; color: var(--text-secondary); font-size: 13px; }
.ldst { display: inline-block; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: .06em; padding: 2px 8px; border-radius: 999px; border: 1px solid transparent; }
.ldst-open { background: color-mix(in oklab, var(--accent) 16%, var(--surface)); color: var(--accent); border-color: var(--accent); }
.ldst-sold { background: color-mix(in oklab, var(--good) 18%, var(--surface)); color: var(--good); border-color: var(--good); }
.ldst-lost { background: color-mix(in oklab, var(--bad) 14%, var(--surface)); color: var(--bad); border-color: var(--bad); }
.ldst-cycle { background: color-mix(in oklab, var(--s4) 18%, var(--surface)); color: var(--text-secondary); border-color: var(--border-strong); }
.ldback { margin: 0 0 8px; }
.cname .ldopen { font-size: 11px; padding: 2px 8px; margin-left: 8px; vertical-align: middle; }
.ldhead { padding: 16px 18px; border: 2px solid var(--border-strong); border-radius: 14px; background: var(--surface); border-top: 6px solid var(--accent); }
.ldtitle { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; } .ldname { margin: 0; font-size: 26px; } .ldid { font-size: 12px; margin-left: auto; }
.ldacts { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 4px; align-items: center; } .ldacts .btn small { font-weight: 600; opacity: .8; } .ldlink { text-decoration: none; }
.ldfacts { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 6px 18px; margin: 12px 0 0; } .ldfacts.one { grid-template-columns: 1fr; gap: 4px; }
.ldfacts div { display: grid; grid-template-columns: 92px 1fr; gap: 8px; align-items: baseline; } .ldfacts dt { font-size: 11px; text-transform: uppercase; letter-spacing: .07em; color: var(--text-muted); } .ldfacts dd { margin: 0; font-size: 14px; }
.ldaz { font-size: 12px; color: var(--text-muted); font-style: italic; }
.ldmsg { margin: 10px 0 0; font-weight: 600; } .ldmsg.bad { color: var(--bad); } .ldmsg.good { color: var(--good); }
.ldform { margin: 12px 0 0; padding: 12px; border: 1px solid var(--border-strong); border-radius: 12px; background: var(--surface-raised); display: grid; gap: 8px; } .ldform label { display: grid; gap: 4px; font-size: 13px; font-weight: 600; } .ldta { width: 100%; font: inherit; resize: vertical; }
.ldcols { display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(300px, 1fr); gap: 18px; margin-top: 16px; align-items: start; }
.ldchips { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 10px; } .ldchip { font: inherit; font-size: 13px; font-weight: 600; padding: 4px 10px; border-radius: 999px; border: 1px solid var(--border-strong); background: var(--surface); color: var(--text-secondary); cursor: pointer; } .ldchip.on { background: var(--accent); color: #fff; border-color: var(--accent); } .ldchip small { font-weight: 500; opacity: .8; }
.ldday { font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; color: var(--text-muted); margin: 16px 0 6px; padding-bottom: 4px; border-bottom: 1px solid var(--border); }
.ldnote { padding: 8px 12px; margin: 6px 0; border-radius: 12px; border: 1px solid var(--border); background: var(--surface); border-left: 5px solid var(--border-strong); }
.ldnote.ld-note { border-left-color: var(--accent); } .ldnote.ld-text { border-left-color: var(--s3); } .ldnote.ld-email { border-left-color: var(--s4); } .ldnote.ld-call { border-left-color: var(--good); } .ldnote.ld-task { border-left-color: #8e5bd6; } .ldnote.ld-stage { border-left-color: #c5872b; }
.ldnote.ld-in { background: color-mix(in oklab, var(--s3) 10%, var(--surface)); }
.ldnote.ld-system { padding: 4px 12px; font-size: 12.5px; opacity: .78; border-style: dashed; } .ldnote.ld-system .ldbody { display: inline; white-space: normal; margin-left: 6px; } .ldnote.ld-system .ldnhead { display: inline-flex; }
.ldnhead { display: flex; flex-wrap: wrap; gap: 8px; align-items: baseline; font-size: 12.5px; } .ldtime { color: var(--text-muted); min-width: 64px; } .ldkind { font-weight: 800; text-transform: uppercase; letter-spacing: .05em; font-size: 11px; } .ldwho2 { font-weight: 600; }
.ldsubj { font-weight: 700; margin-top: 3px; } .ldbody { white-space: pre-wrap; margin-top: 3px; font-size: 14px; overflow-wrap: anywhere; }
.ldside { display: grid; gap: 12px; } .ldbox { padding: 12px 14px; border: 1px solid var(--border-strong); border-radius: 12px; background: var(--surface); } .ldbox h3 { margin: 0 0 8px; font-size: 14px; } .ldbox summary { cursor: pointer; font-weight: 700; font-size: 14px; }
.ldlist { margin: 0; padding-left: 18px; font-size: 13.5px; } .ldlist li { margin: 4px 0; } .ldlist.ldsmall { font-size: 12.5px; }
.ldtasks { list-style: none; margin: 0; padding: 0; } .ldtask { padding: 6px 0; border-bottom: 1px solid var(--border); } .ldtask:last-child { border-bottom: 0; } .ldtask.done { opacity: .7; } .ldtask.late .ldwhen { color: var(--bad); font-weight: 700; }
.ldtask .tkcomm { max-height: 7.5em; overflow: auto; }
.ldtaskrow { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; font-size: 13.5px; } .ldtaskrow b { flex: 1; min-width: 120px; }
@media (max-width: 980px) { .ldcols { grid-template-columns: 1fr; } .ldid { margin-left: 0; } }
`;
  document.head.appendChild(css);
})();
