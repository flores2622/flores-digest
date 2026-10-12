/* Tasks -- the first page of Pantheon's own CRM (Frank, 2026-10-06: "start
   on the tasks page next, all of this is available to only me until further
   notice"). Sales Center > Tasks, shown only to whoever /api/crm answers
   (site/crm.js: staff.json's `crm` -- Frank alone for now); for anyone else
   the page never enters the menu or the search.

   What it is: every task in the CRM, as AgencyZoom's task list is used today
   -- due today, overdue, the week ahead and what was done today, per person
   or for everyone -- with Done (and what happened) on each row, Reschedule,
   New task (for whom, due when, hung on a lead or household found by name or
   number), and the lead's coaching card a click away (the CRM keeps
   AgencyZoom's lead ids, so the search index finds it). Uses the board's
   own helpers ($, cesc, pbadge, DOT, azTodayDate, isoDate, openLeadCard),
   so it loads after index.html's main script.

   Nothing here reads AgencyZoom: a task made here lives only in Pantheon
   until phase 2 of CRM.md moves the pipeline's own task writes over. */
(function () {
  const TABS = [["today", "Due today"], ["overdue", "Overdue"], ["week", "Next 7 days"], ["done", "Done today"], ["all", "All open"]];
  const TYPES = [["call", "Call"], ["text", "Text"], ["email", "Email"], ["todo", "To do"]];
  let LK = null;                    // /api/crm/lookups
  let tkTab = "today", tkWho = "";  // who: an employee id as a string, "" = everyone
  let tkRows = [], tkCounts = {}, tkBusy = false, tkMsg = null, tkErr = "";
  let tkOpen = {};                  // row id -> "done" | "when" (an inline form open)
  let tkNew = false;                // the New task form is open
  let tkLink = null;                // {kind, id, name} the new task hangs on
  let tkHits = [];                  // search hits for the link box
  // A refresh reopens the tab and person it was on (per browser tab, like the board's own saveWhere).
  try { const w = JSON.parse(sessionStorage.getItem("tasks-where") || "{}"); if (TABS.some(([k]) => k === w.tab)) tkTab = w.tab; if (typeof w.who === "string") tkWho = w.who; } catch (_) {}

  const first = n => String(n || "").split(" ")[0];
  const today = () => isoDate(azTodayDate());
  const addDays = (day, n) => { const d = new Date(day + "T00:00:00Z"); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
  const person = id => (LK && LK.employees || []).find(e => String(e.id) === String(id)) || null;
  const badge = id => { const p = person(id); return p ? (DOT[p.name] ? pbadge(DOT[p.name], first(p.name)) : `<b>${cesc(first(p.name))}</b>`) : '<span class="tkmute">nobody</span>'; };
  const clock = s => { if (!s) return ""; const [d, t] = s.split(" "); const [h, m] = (t || "00:00").split(":").map(Number); const hh = h % 12 || 12; return `${hh}:${String(m).padStart(2, "0")} ${h < 12 ? "AM" : "PM"}`; };
  const dayLabel = s => { if (!s) return "no date"; const d = s.slice(0, 10); const t = today(); if (d === t) return "today"; if (d === addDays(t, 1)) return "tomorrow"; if (d === addDays(t, -1)) return "yesterday"; return new Date(d + "T12:00:00").toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" }); };
  const saveWhere = () => { try { sessionStorage.setItem("tasks-where", JSON.stringify({ tab: tkTab, who: tkWho })); } catch (_) {} };

  async function api(path, body) {
    const r = await fetch("/api/crm/" + path, body ? { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) } : { cache: "no-store" });
    let j = null; try { j = await r.json(); } catch (_) {}
    if (!r.ok) { const e = new Error((j && j.error) || `HTTP ${r.status}`); e.status = r.status; throw e; }
    return j;
  }

  // Unhide the page for whoever the Worker lets in. CRM_READY says whether
  // it did, so a refresh on this page can reopen it (index.html init).
  window.CRM_READY = (async function tkInit() {
    try { LK = await api("lookups"); } catch (_) { return false; }
    if (!CENTERS.salescenter.some(([k]) => k === "tasks")) CENTERS.salescenter.push(["tasks", "Tasks"]);
    SEARCH_PAGES.push(["Tasks", "Sales Center · the CRM's tasks: due today, overdue, done", "tasks"]);
    paintCenterBar();
    return true;
  })();

  // The filters each tab sends. "to" days are inclusive (site/crm.js list).
  function query(tab) {
    const t = today(), who = tkWho ? `&assigneeId=${encodeURIComponent(tkWho)}` : "";
    const q = { today: `status=0&dueFrom=${t}&dueTo=${t}`, overdue: `status=0&dueTo=${addDays(t, -1)}`,
      week: `status=0&dueFrom=${addDays(t, 1)}&dueTo=${addDays(t, 7)}`, done: `status=1&completedFrom=${t}&completedTo=${t}`, all: "status=0" }[tab];
    return `tasks?${q}${who}&limit=500`;
  }
  async function load() {
    const [rows, ...counts] = await Promise.all([api(query(tkTab)), ...TABS.map(([k]) => k === tkTab ? null : api(query(k) + "&limit=1"))]);
    tkRows = rows.tasks || [];
    tkCounts = {};
    TABS.forEach(([k], i) => { tkCounts[k] = k === tkTab ? rows.totalCount : (counts[i] || {}).totalCount || 0; });
  }

  function rowHtml(r) {
    const open = tkOpen[r.id];
    const late = r.status === 0 && r.dueDate && r.dueDate < today() + " 00:00:00";
    const whoFor = r.customerName ? `<a href="#" class="tklead" data-lead="${r.leadId || ""}" data-name="${cesc(r.customerName)}" title="${r.leadId ? "Open the lead's coaching card" : "A household: no coaching card"}">${cesc(r.customerName)}</a>${r.customerPhone ? ` <small class="tkmute">${cesc(r.customerPhone)}</small>` : ""}` : '<span class="tkmute">no one attached</span>';
    const when = r.status === 1 ? `<span class="tkdone">done ${clock(r.completeDate)}</span>` : `<span class="${late ? "tklate" : ""}">${cesc(dayLabel(r.dueDate))}${r.dueDate && r.dueDate.slice(11, 16) !== "00:00" ? " · " + clock(r.dueDate) : ""}</span>`;
    const form = open === "done" ? `<form class="tkform" data-done="${r.id}"><input type="text" class="tkin tkwide" name="comment" placeholder="What happened? (optional)" maxlength="500" autofocus>
        <button type="submit" class="btn tkpri"${tkBusy ? " disabled" : ""}>Mark done</button><button type="button" class="btn" data-close="${r.id}">Cancel</button></form>`
      : open === "when" ? `<form class="tkform" data-when="${r.id}"><input type="date" class="tkin" name="day" value="${cesc((r.dueDate || today()).slice(0, 10))}" required><input type="time" class="tkin" name="time" value="${cesc((r.dueDate || "").slice(11, 16) || "09:00")}">
        <button type="submit" class="btn tkpri"${tkBusy ? " disabled" : ""}>Save</button><button type="button" class="btn" data-close="${r.id}">Cancel</button></form>` : "";
    return `<tr class="${r.status === 1 ? "tkrow-done" : ""}${late ? " tkrow-late" : ""}" data-id="${r.id}">
      <td class="tkwhen">${when}</td>
      <td>${badge(r.assigneeId)}</td>
      <td class="tktitle"><strong>${cesc(r.title)}</strong>${r.comments ? `<div class="tkcomm">${cesc(r.comments)}</div>` : ""}${form}</td>
      <td>${whoFor}</td>
      <td class="tktype"><span class="tkpill">${cesc((TYPES.find(([k]) => k === r.type) || [, r.type])[1])}</span></td>
      <td class="tkact">${r.status === 0 ? `<button type="button" class="btn tksmall tkpri" data-open="done" data-id="${r.id}">Done</button> <button type="button" class="ghost tksmall" data-open="when" data-id="${r.id}">Reschedule</button>` : `<span class="tkmute">by ${cesc(first((person(r.completedBy) || {}).name) || "—")}</span>`}</td>
    </tr>`;
  }

  function newHtml() {
    if (!tkNew) return `<button type="button" class="btn tkpri" data-new="1">+ New task</button>`;
    const people = (LK.employees || []).map(e => `<option value="${e.id}"${String(e.id) === String(tkWho) ? " selected" : ""}>${cesc(e.name)}</option>`).join("");
    return `<form class="tknew" data-create="1">
      <div class="tkgrid">
        <label>Task<input type="text" class="tkin tkwide" name="title" placeholder="Call back about the auto quote" maxlength="200" required autofocus></label>
        <label>For<select class="tkin" name="assigneeId" required><option value="">Pick who…</option>${people}</select></label>
        <label>Due<span class="tkrow"><input type="date" class="tkin" name="day" value="${today()}" required><input type="time" class="tkin" name="time" value="09:00"></span></label>
        <label>Kind<select class="tkin" name="type">${TYPES.map(([k, l]) => `<option value="${k}">${l}</option>`).join("")}</select></label>
        <label class="tkspan">Who it's about<span class="tkrow">
          ${tkLink ? `<span class="tklinked">${cesc(tkLink.name)} <small class="tkmute">${tkLink.kind === "lead" ? "lead" : "household"}</small> <button type="button" class="icon-btn" data-unlink="1" aria-label="Take off">✕</button></span>`
            : `<input type="search" class="tkin tkwide" name="find" placeholder="Name or phone number" autocomplete="off">`}
        </span>${tkHits.length ? `<ul class="tkhits">${tkHits.map((h, i) => `<li><button type="button" data-hit="${i}">${cesc(h.name)} <small>${cesc(h.kind === "lead" ? "lead" : "household")}${h.phone ? " · " + cesc(h.phone) : ""}${h.who ? " · " + cesc(first(h.who)) : ""}</small></button></li>`).join("")}</ul>` : ""}</label>
        <label class="tkspan">Notes<input type="text" class="tkin tkwide" name="comments" placeholder="Optional" maxlength="1000"></label>
      </div>
      <div class="tkrow"><button type="submit" class="btn tkpri"${tkBusy ? " disabled" : ""}>Add task</button><button type="button" class="btn" data-cancelnew="1">Cancel</button></div>
    </form>`;
  }

  function repaint() {
    const v = $("#view");
    const people = (LK.employees || []);
    const tiles = TABS.map(([k, l]) => `<button type="button" class="tktile${k === tkTab ? " on" : ""}" data-tab="${k}" style="--th:${{ today: "var(--accent)", overdue: "var(--bad)", week: "var(--s4)", done: "var(--good)", all: "var(--s3)" }[k]}"><span>${l}</span><strong>${tkCounts[k] == null ? "…" : tkCounts[k]}</strong></button>`).join("");
    v.innerHTML = `<section class="tkpage">
      <div class="tkhead">
        <div class="tktiles">${tiles}</div>
        <label class="tkwho">For <select class="tkin" data-who="1"><option value="">everyone</option>${people.map(e => `<option value="${e.id}"${String(e.id) === String(tkWho) ? " selected" : ""}>${cesc(e.name)}</option>`).join("")}</select></label>
      </div>
      ${tkMsg ? `<p class="tkmsg ${tkMsg.err ? "bad" : "good"}" role="${tkMsg.err ? "alert" : "status"}">${cesc(tkMsg.err || tkMsg.ok)}</p>` : ""}
      <div class="tknewbox">${newHtml()}</div>
      ${tkRows.length ? `<div class="scroll"><table class="tktab"><thead><tr><th>${tkTab === "done" ? "Done" : "Due"}</th><th>Who</th><th>Task</th><th>About</th><th>Kind</th><th></th></tr></thead><tbody>${tkRows.map(rowHtml).join("")}</tbody></table></div>`
        : `<div class="empty">${{ today: "Nothing due today", overdue: "Nothing overdue", week: "Nothing due in the next 7 days", done: "Nothing done yet today", all: "No open tasks" }[tkTab]}${tkWho ? ` for ${cesc(first((person(tkWho) || {}).name))}` : ""}.</div>`}
      <p class="tkfoot">Pantheon's own CRM. ${LK.employees.length} people, ${LK.workflows.length} pipelines and workflows, ${LK.leadSources.length} lead sources on file. Tasks made here live only in Pantheon until the pipeline's task writes move over (CRM.md, phase 2).</p>
    </section>`;
    const f = v.querySelector(".tkform input[autofocus], .tknew input[autofocus]"); if (f) f.focus();
  }

  async function refresh(msg) {
    tkMsg = msg || null;
    try { await load(); tkErr = ""; } catch (e) { tkErr = e.message; }
    repaint();
  }

  async function act(fn, ok) {
    if (tkBusy) return;
    tkBusy = true; repaint();
    try { await fn(); tkOpen = {}; await refresh({ ok }); }
    catch (e) { tkBusy = false; tkMsg = { err: e.message }; repaint(); return; }
    tkBusy = false; repaint();
  }

  function onClick(e) {
    const t = e.target.closest("[data-tab],[data-open],[data-close],[data-new],[data-cancelnew],[data-unlink],[data-hit],.tklead");
    if (!t || !$("#view").contains(t) || $("#view").dataset.view !== "tasks") return;   // lists.js shares the look, not the clicks
    if (t.dataset.tab) { tkTab = t.dataset.tab; tkOpen = {}; saveWhere(); refresh(); return; }
    if (t.dataset.open) { tkOpen = { [t.dataset.id]: t.dataset.open }; repaint(); return; }
    if (t.dataset.close) { delete tkOpen[t.dataset.close]; repaint(); return; }
    if (t.dataset.new) { tkNew = true; tkLink = null; tkHits = []; repaint(); return; }
    if (t.dataset.cancelnew) { tkNew = false; tkLink = null; tkHits = []; repaint(); return; }
    if (t.dataset.unlink) { tkLink = null; repaint(); return; }
    if (t.dataset.hit) { tkLink = tkHits[+t.dataset.hit] || null; tkHits = []; repaint(); return; }
    if (t.classList.contains("tklead")) {
      e.preventDefault();
      if (t.dataset.lead) openLeadCard({ id: t.dataset.lead, l: t.dataset.name });
      return;
    }
  }
  function onChange(e) {
    const s = e.target.closest("[data-who]");
    if (s && $("#view").contains(s) && $("#view").dataset.view === "tasks") { tkWho = s.value; saveWhere(); refresh(); }
  }
  let findTimer = 0;
  function onInput(e) {
    const f = e.target.closest(".tknew input[name=find]");
    if (!f) return;
    clearTimeout(findTimer);
    const q = f.value.trim();
    if (q.length < 2) { tkHits = []; return; }
    findTimer = setTimeout(async () => {
      try {
        const j = await api(`search?q=${encodeURIComponent(q)}`);
        tkHits = [...(j.leads || []).map(l => ({ kind: "lead", id: l.id, name: l.name, phone: l.phone, who: l.assignedToName })),
          ...(j.customers || []).map(h => ({ kind: "household", id: h.id, name: h.name, phone: h.phone, who: h.assignedToName }))].slice(0, 8);
      } catch (_) { tkHits = []; }
      // keep what was typed while the list is drawn under it
      const keep = f.value, pos = f.selectionStart;
      repaint();
      const nf = $(".tknew input[name=find]"); if (nf) { nf.value = keep; nf.focus(); try { nf.setSelectionRange(pos, pos); } catch (_) {} }
    }, 250);
  }
  function onSubmit(e) {
    const form = e.target.closest("form.tkform, form.tknew");
    if (!form || !$("#view").contains(form)) return;
    e.preventDefault();
    const fd = new FormData(form);
    if (form.dataset.done) {
      const id = form.dataset.done;
      act(() => api(`tasks/${id}/complete`, { comment: String(fd.get("comment") || "").trim() }), "Done.");
    } else if (form.dataset.when) {
      const id = form.dataset.when;
      act(() => api(`tasks/${id}`, { dueDate: `${fd.get("day")} ${fd.get("time") || "00:00"}` }), "Rescheduled.");
    } else if (form.dataset.create) {
      const body = { title: String(fd.get("title") || "").trim(), assigneeId: Number(fd.get("assigneeId")) || null, type: String(fd.get("type") || "call"),
        dueDate: `${fd.get("day")} ${fd.get("time") || "00:00"}`, comments: String(fd.get("comments") || "").trim() || null };
      if (tkLink) body[tkLink.kind === "lead" ? "leadId" : "householdId"] = tkLink.id;
      act(async () => { const t = await api("tasks", body); tkNew = false; tkLink = null; tkHits = [];
        // show the task where it landed
        const d = (t.dueDate || "").slice(0, 10), td = today();
        tkTab = d === td ? "today" : d < td ? "overdue" : d <= addDays(td, 7) ? "week" : "all"; saveWhere(); }, "Task added.");
    }
  }
  document.addEventListener("click", onClick);
  document.addEventListener("change", onChange);
  document.addEventListener("input", onInput);
  document.addEventListener("submit", onSubmit);

  window.tasksPaint = async function tasksPaint() {
    $("#topsub").textContent = "the CRM's tasks: due today, overdue, done";
    $("#view").innerHTML = '<div class="empty">Loading…</div>';
    if (!LK) { try { LK = await api("lookups"); } catch (e) { $("#view").innerHTML = `<div class="empty">${e.status === 503 ? "The CRM is not turned on yet." : "Tasks are not open to this login."}</div>`; return; } }
    tkMsg = null; tkOpen = {};
    await refresh();
    if (tkErr) $("#view").insertAdjacentHTML("afterbegin", `<p class="tkmsg bad" role="alert">${cesc(tkErr)}</p>`);
  };

  const css = document.createElement("style");
  css.textContent = `
.tkpage { background: var(--surface-raised); border: var(--bw, 2px) solid var(--border-strong); border-top: 6px solid var(--accent); border-radius: 14px; padding: 14px 16px 16px; box-shadow: var(--shadow); }
.tkhead { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
.tktiles { display: flex; flex-wrap: wrap; gap: 10px; }
.tktile { font: inherit; cursor: pointer; text-align: left; min-width: 118px; background: var(--surface); color: var(--text-primary); border: var(--bw, 2px) solid var(--border-strong); border-top: 5px solid var(--th); border-radius: 12px; padding: 8px 12px 10px; }
.tktile span { display: block; text-transform: uppercase; letter-spacing: .07em; font-size: 11px; font-weight: 700; color: var(--text-muted); }
.tktile strong { font-family: var(--display); font-weight: var(--dw, 700); font-size: 26px; line-height: 1.1; }
.tktile.on { outline: 3px solid var(--th); outline-offset: -1px; }
.tkwho { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; color: var(--text-secondary); }
.tkin { box-sizing: border-box; font: inherit; font-size: 14px; padding: 7px 10px; border: 1px solid var(--border-strong); border-radius: 10px; background: var(--surface); color: var(--text-primary); }
.tkin:focus { border-color: var(--accent); outline: none; }
.tkin.tkwide { width: 100%; min-width: 220px; }
.tknewbox { margin: 6px 0 12px; }
.tknew { background: var(--surface); border: 1px solid var(--border-strong); border-radius: 12px; padding: 12px 14px; }
.tkgrid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 10px 12px; margin-bottom: 10px; }
.tkgrid label { display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 700; color: var(--text-secondary); min-width: 0; position: relative; }
.tkgrid .tkspan { grid-column: 1 / -1; }
.tkrow { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.tklinked { display: inline-flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 600; color: var(--text-primary); padding: 6px 10px; border: 1px solid var(--border-strong); border-radius: 10px; background: color-mix(in oklab, var(--good) 12%, var(--surface)); }
.tkhits { list-style: none; margin: 4px 0 0; padding: 4px; border: 1px solid var(--border-strong); border-radius: 10px; background: var(--surface-raised); box-shadow: var(--shadow); max-width: 520px; }
.tkhits button { font: inherit; width: 100%; text-align: left; background: none; border: 0; color: var(--text-primary); padding: 6px 8px; border-radius: 8px; cursor: pointer; }
.tkhits button:hover, .tkhits button:focus { background: color-mix(in oklab, var(--accent) 14%, transparent); outline: none; }
.tkhits small { color: var(--text-muted); font-weight: 500; }
.tktab { width: 100%; border-collapse: collapse; }
.tktab th, .tktab td { text-align: left; vertical-align: top; padding: 8px 8px; border-bottom: 1px solid var(--border); font-size: 14px; }
.tktab th { font-size: 11px; text-transform: uppercase; letter-spacing: .07em; color: var(--text-muted); }
.tktab tr.tkrow-done td { opacity: .72; }
.tktab tr.tkrow-late .tkwhen { color: var(--bad); font-weight: 700; }
.tkwhen { white-space: nowrap; min-width: 120px; } .tklate { color: var(--bad); font-weight: 700; } .tkdone { color: var(--good); font-weight: 700; }
.tkcomm { font-size: 13px; color: var(--text-secondary); margin-top: 2px; white-space: pre-wrap; }
.tkform { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-top: 8px; }
.tkform .tkin { font-size: 13px; padding: 5px 8px; } .tkform .tkwide { min-width: 240px; width: auto; flex: 1; }
.tkpill { display: inline-block; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; padding: 2px 7px; border-radius: 999px; border: 1px solid var(--border-strong); color: var(--text-secondary); }
.tkact { white-space: nowrap; text-align: right; }
.btn.tksmall, .ghost.tksmall { font-size: 12px; padding: 4px 9px; }
.btn.tkpri { background: var(--accent); color: #fff; border-color: var(--accent); }
.tklead { color: var(--text-primary); font-weight: 600; text-decoration: underline dotted; }
.tkmute { color: var(--text-muted); }
.tkmsg { margin: 0 0 10px; font-weight: 600; } .tkmsg.bad { color: var(--bad); } .tkmsg.good { color: var(--good); }
.tkfoot { margin: 12px 0 0; font-size: 12px; color: var(--text-muted); }
@media (max-width: 900px) { .tkgrid { grid-template-columns: 1fr 1fr; } .tktile { min-width: 96px; } .tktab th:nth-child(5), .tktab td:nth-child(5) { display: none; } }
`;
  document.head.appendChild(css);
})();
