/* Lists -- Frank's own lead sources, sales pipelines and service pipelines,
   and where every AgencyZoom entry lands (Frank, 2026-10-06: "i want to
   consolidate lead sources, pipelines, service request categories. I want to
   customize and rebuild"). Sales Center > Lists, shown only to whoever
   /api/crm answers (staff.json's `crm` -- Frank alone for now).

   What it shows: three tabs. On each, Frank's list in his order -- rename,
   add, retire, move up or down, the one field kept beside an entry ("How
   they found us" on Call-in / Walk-in) -- and under each entry the
   AgencyZoom names placed there with how much sits on them, each with a
   "Move to" and its field's value. Anything the nightly's rules could not
   place sits in Unsorted at the top until it is placed. A placement made
   here is never undone by the nightly (site/crm.js, crm_lists.py).
   Loads after tasks.js: it waits on CRM_READY. */
(function () {
  const TABS = [["sources", "Lead sources"], ["pipelines", "Sales pipelines"], ["service", "Service pipelines"]];
  let D = null, lsTab = "sources", lsBusy = false, lsMsg = null, lsEdit = null, lsAdd = null, lsOpen = {};
  try { const w = JSON.parse(sessionStorage.getItem("lists-where") || "{}"); if (TABS.some(([k]) => k === w.tab)) lsTab = w.tab; } catch (_) {}
  const saveWhere = () => { try { sessionStorage.setItem("lists-where", JSON.stringify({ tab: lsTab })); } catch (_) {} };

  async function api(path, body) {
    const r = await fetch("/api/crm/" + path, body ? { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) } : { cache: "no-store" });
    let j = null; try { j = await r.json(); } catch (_) {}
    if (!r.ok) { const e = new Error((j && j.error) || `HTTP ${r.status}`); e.status = r.status; throw e; }
    return j;
  }
  window.LISTS_READY = (async function () {
    const ok = await (window.CRM_READY || Promise.resolve(false));
    if (!ok) return false;
    if (!CENTERS.salescenter.some(([k]) => k === "lists")) CENTERS.salescenter.push(["lists", "Lists"]);
    SEARCH_PAGES.push(["Lists", "Sales Center · the CRM's lead sources, pipelines and service pipelines", "lists"]);
    paintCenterBar();
    return true;
  })();

  const n = (x) => (x || 0).toLocaleString("en-US");
  const who = (p) => (!p || p === "rule" ? "placed by the nightly's rules" : `placed by ${p.split("@")[0]}`);
  const opt = (list, cur, blank) => (blank ? `<option value=""${cur == null ? " selected" : ""}>${blank}</option>` : "") + list.map((x) => `<option value="${x.id}"${x.id === cur ? " selected" : ""}>${cesc(x.name)}</option>`).join("");

  /* --- what each tab lays out ------------------------------------------------- */
  // Frank's entries of this tab, with the AgencyZoom rows under each and the unsorted
  function model() {
    const L = D.lists, A = D.az;
    if (lsTab === "sources") {
      return { kind: "source", mapKind: "source", entries: L.sources, counts: (rows) => `${n(rows.reduce((a, r) => a + r.leads, 0))} leads · ${n(rows.reduce((a, r) => a + r.policies, 0))} policies`,
        azOf: (e) => A.sources.filter((x) => x.placed && x.listId === e.id), azLine: (x) => `${n(x.leads)} leads · ${n(x.policies)} policies`,
        unsorted: A.sources.filter((x) => !x.placed).map((x) => ({ ...x, mapKind: "source", what: "lead source", line: `${n(x.leads)} leads · ${n(x.policies)} policies`, targets: L.sources })),
        targets: () => L.sources, detailable: true };
    }
    if (lsTab === "pipelines") {
      const placedWf = (e) => A.workflows.filter((x) => x.kind === "sales" && x.placed && x.listId === e.id);
      const stagesOf = (e, st) => A.stages.filter((x) => x.placed && x.listId === st.id && placedWf(e).some((w) => w.id === x.workflowId));
      const wfName = (id) => ((A.workflows.find((w) => w.id === id) || {}).name || "?");
      const unsortedWf = A.workflows.filter((x) => x.kind === "sales" && !x.placed).map((x) => ({ ...x, mapKind: "workflow", what: "pipeline", line: `${n(x.leads)} open leads`, targets: L.pipelines }));
      const unsortedSt = A.stages.filter((x) => !x.placed && !x.waits).map((x) => { const wf = A.workflows.find((w) => w.id === x.workflowId); const pipe = L.pipelines.find((p) => p.id === (wf || {}).listId); return { ...x, name: `${wfName(x.workflowId)} | ${x.name}`, mapKind: "stage", what: "stage", line: `${n(x.leads)} open leads`, targets: pipe ? pipe.stages : [] }; });
      return { kind: "pipeline", mapKind: "workflow", entries: L.pipelines, counts: (rows) => `${n(rows.reduce((a, r) => a + r.leads, 0))} open leads`,
        azOf: placedWf, azLine: (x) => `${n(x.leads)} open leads`, unsorted: [...unsortedWf, ...unsortedSt], targets: () => L.pipelines,
        stages: { of: stagesOf, line: (x) => `${wfName(x.workflowId)} · ${n(x.leads)} open` } };
    }
    const cats = (e) => A.categories.filter((x) => x.placed && x.listId === e.id);
    const wfs = (e) => A.workflows.filter((x) => x.kind === "service" && x.placed && x.listId === e.id);
    return { kind: "service", mapKind: "workflow", entries: L.service, counts: (rows) => `${n(rows.reduce((a, r) => a + r.srs, 0))} SRs`,
      azOf: wfs, azLine: (x) => `${n(x.srs)} SRs · workflow`, cats, catLine: (x) => `${n(x.srs)} SRs · category`,
      unsorted: [...A.workflows.filter((x) => x.kind === "service" && !x.placed).map((x) => ({ ...x, mapKind: "workflow", what: "workflow", line: `${n(x.srs)} SRs`, targets: L.service })),
        ...A.categories.filter((x) => !x.placed).map((x) => ({ ...x, mapKind: "category", what: "SR category", line: `${n(x.srs)} SRs`, targets: L.service, follows: true }))],
      targets: () => L.service, detailable: true,
      follows: A.categories.filter((x) => x.placed && x.listId == null) };
  }

  function azRow(x, mapKind, targets, label, line, detailable, follows) {
    const sel = `<select class="lsin lsmove" data-place="${mapKind}" data-az="${x.id}" title="Move to">${opt(targets, x.listId, follows ? "Follows the workflow" : null)}</select>`;
    const det = detailable ? `<input type="text" class="lsin lsdetail" data-detail="${mapKind}" data-az="${x.id}" value="${cesc(x.detail || "")}" placeholder="${cesc(label || "detail")}" maxlength="120" title="${cesc(label || "The field kept beside this entry")}">` : "";
    return `<li class="lsaz" title="${cesc(who(x.placedBy))}"><span class="lsazname">${cesc(x.name)}</span><small class="lsmute">${line}</small>${det}${sel}</li>`;
  }
  function entryHtml(m, e, idx, all) {
    const az = m.azOf(e);
    const open = lsOpen[`${m.kind}:${e.id}`] !== false;
    const editing = lsEdit && lsEdit.kind === m.kind && lsEdit.id === e.id;
    const head = editing ? `<form class="lsform" data-edit="${m.kind}" data-id="${e.id}"><input type="text" class="lsin" name="name" value="${cesc(e.name)}" maxlength="80" required autofocus>
        <input type="text" class="lsin" name="detailLabel" value="${cesc(e.detailLabel || "")}" placeholder="Field kept beside it (optional)" maxlength="60">
        <input type="text" class="lsin lswide" name="meaning" value="${cesc(e.meaning || "")}" placeholder="What it is, in a line" maxlength="400">
        <button type="submit" class="btn tkpri">Save</button><button type="button" class="btn" data-canceledit="1">Cancel</button></form>`
      : `<button type="button" class="lstoggle" data-toggle="${m.kind}:${e.id}" aria-expanded="${open}">${open ? "▾" : "▸"}</button>
         <strong class="lsname${e.active ? "" : " lsoff"}">${cesc(e.name)}</strong>${e.detailLabel ? `<span class="lspill" title="The one field kept beside this entry">${cesc(e.detailLabel)}</span>` : ""}
         ${e.active ? "" : '<span class="lspill lsoffpill">retired</span>'}<small class="lsmute">${m.counts(az)}</small>
         <span class="lsacts"><button type="button" class="ghost tksmall" data-up="${m.kind}:${e.id}"${idx === 0 ? " disabled" : ""} aria-label="Move up">▲</button><button type="button" class="ghost tksmall" data-down="${m.kind}:${e.id}"${idx === all.length - 1 ? " disabled" : ""} aria-label="Move down">▼</button>
         <button type="button" class="ghost tksmall" data-rename="${m.kind}:${e.id}">Rename</button><button type="button" class="ghost tksmall" data-retire="${m.kind}:${e.id}:${e.active ? 0 : 1}">${e.active ? "Retire" : "Bring back"}</button></span>`;
    let body = "";
    if (open) {
      if (e.meaning && !editing) body += `<p class="lsmeaning">${cesc(e.meaning)}</p>`;
      if (m.stages) {
        body += `<ol class="lsstages">${e.stages.map((st, j) => `<li><div class="lsstage"><strong>${cesc(st.name)}</strong><small class="lsmute">${st.meaning ? cesc(st.meaning) : ""}</small>
            <span class="lsacts"><button type="button" class="ghost tksmall" data-up="stage:${st.id}:${e.id}"${j === 0 ? " disabled" : ""} aria-label="Move up">▲</button><button type="button" class="ghost tksmall" data-down="stage:${st.id}:${e.id}"${j === e.stages.length - 1 ? " disabled" : ""} aria-label="Move down">▼</button><button type="button" class="ghost tksmall" data-renamestage="${st.id}:${e.id}">Rename</button></span></div>
            ${lsEdit && lsEdit.kind === "stage" && lsEdit.id === st.id ? `<form class="lsform" data-edit="stage" data-id="${st.id}"><input type="text" class="lsin" name="name" value="${cesc(st.name)}" maxlength="80" required autofocus><input type="text" class="lsin lswide" name="meaning" value="${cesc(st.meaning || "")}" placeholder="What it means" maxlength="400"><button type="submit" class="btn tkpri">Save</button><button type="button" class="btn" data-canceledit="1">Cancel</button></form>` : ""}
            <ul class="lsazlist">${m.stages.of(e, st).map((x) => azRow(x, "stage", e.stages, null, m.stages.line(x), false)).join("") || '<li class="lsmute lsnone">no AgencyZoom stage here</li>'}</ul></li>`).join("")}</ol>
          ${lsAdd && lsAdd.kind === "stage" && lsAdd.parentId === e.id ? `<form class="lsform" data-add="stage" data-parent="${e.id}"><input type="text" class="lsin" name="name" placeholder="New stage" maxlength="80" required autofocus><button type="submit" class="btn tkpri">Add</button><button type="button" class="btn" data-canceladd="1">Cancel</button></form>` : `<button type="button" class="ghost tksmall" data-addstage="${e.id}">+ Add a stage</button>`}`;
      }
      body += `<div class="lsazhead">${m.stages ? "AgencyZoom pipelines placed here" : m.cats ? "AgencyZoom workflows and categories placed here" : "AgencyZoom sources placed here"}</div>
        <ul class="lsazlist">${az.map((x) => azRow(x, m.mapKind, m.targets(), e.detailLabel, m.azLine(x), m.detailable && m.kind === "source" && !!e.detailLabel)).join("")}
        ${m.cats ? m.cats(e).map((x) => azRow(x, "category", m.targets(), e.detailLabel, m.catLine(x), !!e.detailLabel, true)).join("") : ""}
        ${!az.length && !(m.cats && m.cats(e).length) ? '<li class="lsmute lsnone">nothing placed here yet</li>' : ""}</ul>`;
    }
    return `<li class="lsentry${e.active ? "" : " lsretired"}"><div class="lshead">${head}</div>${body}</li>`;
  }
  function unsortedHtml(m) {
    if (!m.unsorted.length) return "";
    return `<section class="lsunsorted"><h3>Unsorted <small>${m.unsorted.length} AgencyZoom ${m.unsorted.length === 1 ? "entry" : "entries"} no rule could place -- pick where each goes</small></h3>
      <ul class="lsazlist">${m.unsorted.map((x) => `<li class="lsaz lsnew"><span class="lsazname">${cesc(x.name)}</span><small class="lsmute">${x.what} · ${x.line}</small>
        ${m.detailable ? `<input type="text" class="lsin lsdetail" data-detail="${x.mapKind}" data-az="${x.id}" value="" placeholder="its field (optional)" maxlength="120">` : ""}
        <select class="lsin lsmove" data-place="${x.mapKind}" data-az="${x.id}"><option value="" selected disabled>Place under…</option>${x.follows ? '<option value="follows">Follows the workflow</option>' : ""}${opt(x.targets, null)}</select></li>`).join("")}</ul></section>`;
  }
  function followsHtml(m) {
    if (!m.follows || !m.follows.length) return "";
    return `<li class="lsentry lsfollows"><div class="lshead"><strong class="lsname">Follows the workflow</strong><small class="lsmute">a category that says nothing on its own (General, Unassigned): the SR lands where its AgencyZoom workflow is placed</small></div>
      <ul class="lsazlist">${m.follows.map((x) => azRow(x, "category", m.targets(), null, `${n(x.srs)} SRs`, false, true)).join("")}</ul></li>`;
  }

  function repaint() {
    const v = $("#view");
    if (!D) return;
    const m = model();
    const tabs = TABS.map(([k, l]) => `<button type="button" class="tktile${k === lsTab ? " on" : ""}" data-lstab="${k}" style="--th:${{ sources: "var(--accent)", pipelines: "var(--s4)", service: "var(--good)" }[k]}"><span>${l}</span><strong>${{ sources: D.lists.sources.length, pipelines: D.lists.pipelines.length, service: D.lists.service.length }[k]}</strong></button>`).join("");
    const addForm = lsAdd && lsAdd.kind === m.kind ? `<form class="lsform lsaddform" data-add="${m.kind}"><input type="text" class="lsin" name="name" placeholder="Name" maxlength="80" required autofocus><input type="text" class="lsin" name="detailLabel" placeholder="Field kept beside it (optional)" maxlength="60"><input type="text" class="lsin lswide" name="meaning" placeholder="What it is, in a line" maxlength="400"><button type="submit" class="btn tkpri">Add</button><button type="button" class="btn" data-canceladd="1">Cancel</button></form>`
      : `<button type="button" class="btn tkpri" data-add="${m.kind}">+ Add ${{ source: "a lead source", pipeline: "a sales pipeline", service: "a service pipeline" }[m.kind]}</button>`;
    v.innerHTML = `<section class="tkpage lspage">
      <div class="tkhead"><div class="tktiles">${tabs}</div>${D.unsorted ? `<span class="lsbadge">${D.unsorted} unsorted</span>` : '<span class="lsbadge lsok">everything placed</span>'}</div>
      ${lsMsg ? `<p class="tkmsg ${lsMsg.err ? "bad" : "good"}" role="${lsMsg.err ? "alert" : "status"}">${cesc(lsMsg.err || lsMsg.ok)}</p>` : ""}
      ${!D.ready ? '<p class="tkmsg bad">The lists are not loaded yet: they arrive with the first nightly sync after this went live.</p>' : ""}
      <p class="lsintro">${{ sources: "Your lead sources. The vendor, partner or staff member is a field on the source, not a source of its own; Call-in / Walk-in carries how they found us. Every AgencyZoom source sits under one of these, and a lead shows your name for it.",
        pipelines: "Your sales pipelines and their stages, in order. Every AgencyZoom pipeline and stage sits under one of these; AZ Sun is New Business. IL Interested and Transfer Pending stay for now.",
        service: "Your service pipelines. The SR category is the pipeline it goes into: an SR lands where its AgencyZoom category is placed, and a category that says nothing (General) follows the SR's workflow." }[lsTab]}</p>
      ${unsortedHtml(m)}
      <div class="lsnewbox">${addForm}</div>
      <ol class="lsentries">${m.entries.map((e, i) => entryHtml(m, e, i, m.entries)).join("")}${followsHtml(m)}</ol>
      <p class="tkfoot">Pantheon's own CRM. AgencyZoom's own names and ids stay on every record; the board reads them through these lists. A placement or a name set here is never undone by the nightly.</p>
    </section>`;
    const f = v.querySelector(".lsform input[autofocus]"); if (f) f.focus();
  }

  async function refresh(msg) {
    lsMsg = msg || null;
    try { D = await api("lists"); } catch (e) { $("#view").innerHTML = `<div class="empty">${cesc(e.message)}</div>`; return; }
    repaint();
  }
  async function act(fn, ok) {
    if (lsBusy) return;
    lsBusy = true;
    try { await fn(); lsEdit = null; lsAdd = null; await refresh({ ok }); }
    catch (e) { lsMsg = { err: e.message }; repaint(); }
    lsBusy = false;
  }
  function entryOf(kind, id) { const m = model(); if (kind === "stage") { for (const p of m.entries) { const s = (p.stages || []).find((x) => x.id === id); if (s) return { list: p.stages, parent: p }; } return null; } return { list: m.entries }; }

  function onClick(e) {
    const t = e.target.closest("[data-lstab],[data-toggle],[data-up],[data-down],[data-rename],[data-renamestage],[data-retire],[data-add],[data-addstage],[data-canceladd],[data-canceledit]");
    if (!t || !$("#view").contains(t) || !$("#view").querySelector(".lspage")) return;
    if (t.dataset.lstab) { lsTab = t.dataset.lstab; lsEdit = lsAdd = null; saveWhere(); repaint(); return; }
    if (t.dataset.toggle) { lsOpen[t.dataset.toggle] = lsOpen[t.dataset.toggle] === false; repaint(); return; }
    if (t.dataset.up || t.dataset.down) {
      const [kind, idS] = (t.dataset.up || t.dataset.down).split(":"), id = Number(idS), dir = t.dataset.up ? -1 : 1;
      const where = entryOf(kind, id); if (!where) return;
      const ids = where.list.map((x) => x.id), i = ids.indexOf(id), j = i + dir;
      if (j < 0 || j >= ids.length) return;
      [ids[i], ids[j]] = [ids[j], ids[i]];
      act(() => api("lists", { op: "order", kind, ids }), "Order saved."); return;
    }
    if (t.dataset.rename) { const [kind, id] = t.dataset.rename.split(":"); lsEdit = { kind, id: Number(id) }; lsAdd = null; repaint(); return; }
    if (t.dataset.renamestage) { lsEdit = { kind: "stage", id: Number(t.dataset.renamestage.split(":")[0]) }; lsAdd = null; repaint(); return; }
    if (t.dataset.retire) { const [kind, id, active] = t.dataset.retire.split(":"); act(() => api("lists", { op: "edit", kind, id: Number(id), active: active === "1" }), active === "1" ? "Brought back." : "Retired. It stays on past records."); return; }
    if (t.dataset.add) { lsAdd = { kind: t.dataset.add }; lsEdit = null; repaint(); return; }
    if (t.dataset.addstage) { lsAdd = { kind: "stage", parentId: Number(t.dataset.addstage) }; lsEdit = null; repaint(); return; }
    if (t.dataset.canceladd) { lsAdd = null; repaint(); return; }
    if (t.dataset.canceledit) { lsEdit = null; repaint(); return; }
  }
  function onChange(e) {
    const s = e.target.closest("[data-place]");
    const d = e.target.closest("[data-detail]");
    if (s && $("#view").contains(s)) {
      const kind = s.dataset.place, azId = Number(s.dataset.az);
      const detailBox = $("#view").querySelector(`[data-detail="${kind}"][data-az="${azId}"]`);
      const detail = detailBox ? detailBox.value.trim() : (findAz(kind, azId) || {}).detail || null;
      const listId = s.value === "follows" || s.value === "" ? null : Number(s.value);
      act(() => api("lists/place", { kind, azId, listId, detail }), "Placed."); return;
    }
    if (d && $("#view").contains(d)) {
      const kind = d.dataset.detail, azId = Number(d.dataset.az), x = findAz(kind, azId);
      if (!x || !x.placed) return;   // an unsorted entry's detail goes with its placement
      act(() => api("lists/place", { kind, azId, listId: x.listId, detail: d.value.trim() || null }), "Saved.");
    }
  }
  function findAz(kind, id) { const A = D.az; const list = { source: A.sources, workflow: A.workflows, stage: A.stages, category: A.categories }[kind] || []; return list.find((x) => x.id === id) || null; }
  function onSubmit(e) {
    const form = e.target.closest("form.lsform");
    if (!form || !$("#view").contains(form)) return;
    e.preventDefault();
    const fd = new FormData(form), val = (k) => String(fd.get(k) || "").trim();
    if (form.dataset.add) {
      const body = { op: "add", kind: form.dataset.add, name: val("name"), detailLabel: val("detailLabel") || null, meaning: val("meaning") || null };
      if (form.dataset.parent) body.parentId = Number(form.dataset.parent);
      act(() => api("lists", body), "Added.");
    } else if (form.dataset.edit) {
      const body = { op: "edit", kind: form.dataset.edit, id: Number(form.dataset.id), name: val("name"), meaning: val("meaning") || null };
      if (fd.has("detailLabel")) body.detailLabel = val("detailLabel") || null;
      act(() => api("lists", body), "Saved.");
    }
  }
  document.addEventListener("click", onClick);
  document.addEventListener("change", onChange);
  document.addEventListener("submit", onSubmit);

  window.listsPaint = async function listsPaint() {
    $("#topsub").textContent = "the CRM's lists: lead sources, pipelines, service pipelines";
    $("#view").innerHTML = '<div class="empty">Loading…</div>';
    lsMsg = null; lsEdit = null; lsAdd = null;
    await refresh();
  };

  const css = document.createElement("style");
  css.textContent = `
.lsintro { margin: 0 0 12px; color: var(--text-secondary); font-size: 14px; }
.lsbadge { font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 999px; background: color-mix(in oklab, var(--bad) 16%, var(--surface)); color: var(--bad); border: 1px solid var(--bad); }
.lsbadge.lsok { background: color-mix(in oklab, var(--good) 14%, var(--surface)); color: var(--good); border-color: var(--good); }
.lsunsorted { border: 2px dashed var(--bad); border-radius: 12px; padding: 10px 14px 12px; margin-bottom: 12px; background: color-mix(in oklab, var(--bad) 6%, var(--surface)); }
.lsunsorted h3 { margin: 0 0 8px; font-size: 15px; } .lsunsorted h3 small { font-weight: 500; color: var(--text-secondary); margin-left: 8px; }
.lsnewbox { margin: 6px 0 12px; }
.lsentries, .lsstages, .lsazlist { list-style: none; margin: 0; padding: 0; }
.lsentry { border: 1px solid var(--border-strong); border-radius: 12px; padding: 10px 14px 12px; margin-bottom: 10px; background: var(--surface); }
.lsentry.lsretired { opacity: .7; } .lsentry.lsfollows { border-style: dashed; }
.lshead { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.lshead .lsname { font-size: 16px; } .lsname.lsoff { text-decoration: line-through; }
.lstoggle { font: inherit; background: none; border: 0; color: var(--text-secondary); cursor: pointer; padding: 0 4px; font-size: 14px; }
.lsacts { margin-left: auto; display: inline-flex; gap: 4px; }
.lspill { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; padding: 2px 7px; border-radius: 999px; border: 1px solid var(--accent); color: var(--accent); }
.lspill.lsoffpill { border-color: var(--text-muted); color: var(--text-muted); }
.lsmeaning { margin: 6px 0 4px; font-size: 13px; color: var(--text-secondary); }
.lsazhead { margin: 10px 0 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; color: var(--text-muted); }
.lsaz { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding: 5px 0; border-top: 1px solid var(--border); font-size: 14px; }
.lsaz.lsnew { border-top: 0; }
.lsazname { font-weight: 600; min-width: 200px; } .lsnone { padding: 4px 0; font-size: 13px; }
.lsin { box-sizing: border-box; font: inherit; font-size: 13px; padding: 5px 8px; border: 1px solid var(--border-strong); border-radius: 8px; background: var(--surface-raised); color: var(--text-primary); }
.lsin:focus { border-color: var(--accent); outline: none; } .lsin.lswide { flex: 1; min-width: 240px; }
.lsdetail { width: 220px; } .lsmove { margin-left: auto; max-width: 260px; }
.lsform { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; flex: 1; }
.lsstages { margin: 8px 0 8px 16px; border-left: 3px solid var(--border-strong); padding-left: 12px; }
.lsstages > li { margin-bottom: 6px; }
.lsstage { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; } .lsstage small { font-size: 12px; }
.lsstages .lsazlist { margin-left: 12px; } .lsstages .lsaz { font-size: 13px; padding: 3px 0; }
.lsmute { color: var(--text-muted); }
@media (max-width: 900px) { .lsmove, .lsdetail { margin-left: 0; width: 100%; max-width: none; } .lsacts { margin-left: 0; } }
`;
  document.head.appendChild(css);
})();
