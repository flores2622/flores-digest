/* The lead scrub tracker (Frank, 2026-10-02: "an interactive way to track a
   list of leads we are scrubbing, making sure they are updated in both apex
   and agency zoom"). Sales Center > Lead Scrub, shown only to the people
   /api/scrub answers (site/scrub.js, staff.json's `scrub`).

   A manager imports the report (Excel or CSV, as it comes) as a scrub
   list; the columns are matched by their headers and can be changed before
   importing. Each client is then worked in the columns of Frank's sheet --
   Client, Month, Apex Status, AZ Status (Duplicates Cleaned and Tagged
   beside it), Lead Status, Action Taken, Date, Rep, Notes, Next Step --
   each saved as soon as it is typed or ticked, redrawing only its own row,
   with who and when on hover. The columns and their suggestions come from
   the Worker (FIELDS), so this draws whatever it is sent. Filters by rep,
   what is left to do, any detail on the report and a search; clients on
   the same phone or email are marked; the list downloads as a CSV in the
   sheet's column order. Uses the board's own
   helpers ($, $$, cesc, pbadge, DOT, CENTERS, SEARCH_PAGES, paintCenterBar),
   so it loads after index.html's main script. */
(function () {
  let SC = null;            // the last /api/scrub answer (the lists)
  let LIST = null;          // the open list's /api/scrub/<id> answer
  let scId = "";            // the open list
  let scImport = null;      // {name, headers, rows, map} while importing
  let scF = { q: "", who: "", todo: "", x: "" };   // x = "<column>\u0001<value>"
  let scShow = 200;
  let scMsg = null;         // {ok|err}
  const COLS = [["name", "Name"], ["phone", "Phone"], ["email", "Email"], ["az_id", "AgencyZoom ID"],
    ["assigned", "Assigned to"], ["source", "Lead source"], ["stage", "Stage"]];

  const first = n => String(n || "").split(" ")[0];
  const badge = n => DOT[n] ? pbadge(DOT[n], first(n)) : cesc(n || "—");
  const digits = s => String(s || "").replace(/\D/g, "").slice(-10);
  const when = iso => { try { return new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }); } catch (_) { return ""; } };

  async function api(path, body) {
    const r = await fetch("/api/scrub" + (path ? "/" + path : ""), body ? {
      method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) } : { cache: "no-store" });
    const out = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(out.error || `could not reach the board (${r.status})`);
    return out;
  }

  // Unhide the page for whoever the Worker lets see it. SCRUB_READY says
  // whether it did, so a refresh on this page can reopen it (index.html).
  window.SCRUB_READY = (async function scInit() {
    try { SC = await api(""); } catch (_) { return false; }
    if (!CENTERS.salescenter.some(([k]) => k === "scrub")) CENTERS.salescenter.push(["scrub", "Lead Scrub"]);
    SEARCH_PAGES.push(["Lead Scrub", "Sales Center · leads cleaned up in Apex and AgencyZoom", "scrub"]);
    paintCenterBar();
    return true;
  })();

  /* ---- CSV ---- */
  function parseCsv(text) {
    const rows = []; let row = [], cell = "", q = false;
    text = String(text || "").replace(/^﻿/, "");
    const sep = (text.split("\n")[0].match(/\t/g) || []).length > (text.split("\n")[0].match(/,/g) || []).length ? "\t" : ",";
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (q) {
        if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; }
        else cell += c;
      } else if (c === '"') q = true;
      else if (c === sep) { row.push(cell); cell = ""; }
      else if (c === "\n" || c === "\r") {
        if (c === "\r" && text[i + 1] === "\n") i++;
        row.push(cell); cell = "";
        if (row.some(x => x.trim())) rows.push(row);
        row = [];
      } else cell += c;
    }
    row.push(cell);
    if (row.some(x => x.trim())) rows.push(row);
    return rows;
  }
  const csvCell = v => /[",\n\r]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v);

  // A report export (Farmers' "Quotes with Risk Segment", 2026-10-02) has a
  // title block above its header row, an empty first column, a Total row at
  // the bottom and a security-classification column on every row. The header
  // is the first row with three or more cells filled; empty columns, the
  // classification column and the Total line are dropped.
  function tidy(all) {
    const filled = r => r.filter(c => String(c == null ? "" : c).trim()).length;
    const at = all.findIndex(r => filled(r) >= 3);
    if (at < 0) return null;
    let rows = all.slice(at + 1).map(r => r.map(c => String(c == null ? "" : c).trim()))
      .filter(r => filled(r) >= 2 && !/^(grand )?total$/i.test(r.find(c => c) || ""));
    const head = all[at].map(c => String(c == null ? "" : c).trim());
    const keep = head.map((h, i) => !/security classification/i.test(h) && (h || rows.some(r => r[i])));
    const pick = r => r.filter((_, i) => keep[i]);
    rows = rows.map(pick);
    return { headers: pick(head).map((h, i) => h || `Column ${i + 1}`), rows };
  }
  let xlsxLib = null;
  function loadXlsx() {
    if (window.XLSX) return Promise.resolve(window.XLSX);
    return xlsxLib = xlsxLib || new Promise((ok, no) => {
      const sc = document.createElement("script");
      sc.src = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js";
      sc.onload = () => ok(window.XLSX); sc.onerror = () => { xlsxLib = null; no(new Error("could not load the Excel reader")); };
      document.head.appendChild(sc);
    });
  }
  async function readFile(f) {
    if (/\.xls[xm]?$/i.test(f.name)) {
      const X = await loadXlsx();
      const wb = X.read(await f.arrayBuffer(), { type: "array" });
      return X.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], { header: 1, raw: false, defval: "" });
    }
    return parseCsv(await f.text());
  }

  // Which export column feeds which field, from the headers.
  function guessMap(headers) {
    const h = headers.map(x => x.toLowerCase().trim());
    const find = (...res) => { for (const re of res) { const i = h.findIndex(x => re.test(x)); if (i >= 0) return i; } return -1; };
    const map = {
      name: find(/^(full |lead |contact |customer |account )?name$/, /account name/, /^name/, /client/, /name$/),
      first: find(/^first/), last: find(/^last/),
      phone: find(/^phone$/, /mobile|cell/, /phone/),
      email: find(/^e-?mail/, /email/),
      az_id: find(/^(lead )?id$/, /lead id|agencyzoom|^az/),
      assigned: find(/assigned|producer|agent|owner/),
      source: find(/source/),
      stage: find(/^stage|status|pipeline stage/),
    };
    return map;
  }
  function importRows() {
    const { headers, rows, map, merge } = scImport;
    const used = new Set(Object.values(map).filter(i => i >= 0));
    const out = rows.map(r => {
      const g = i => (i >= 0 ? String(r[i] || "").trim() : "");
      const out = { extra: {} };
      for (const [k] of COLS) out[k] = g(map[k]);
      if (!out.name) out.name = [g(map.first), g(map.last)].filter(Boolean).join(" ");
      headers.forEach((hd, i) => { if (!used.has(i) && g(i)) out.extra[hd] = g(i); });
      return out;
    });
    if (!merge) return out;
    // One lead per person: rows with the same name (and phone, when there is
    // one) become one lead, each detail column listing every distinct value
    // ("Auto, Home") -- a person quoted on two lines is scrubbed once.
    const by = new Map();
    for (const r of out) {
      const k = r.name.toLowerCase().replace(/\s+/g, " ") + "|" + digits(r.phone);
      const m = by.get(k);
      if (!m) { by.set(k, r); continue; }
      for (const [c] of COLS) if (!m[c] && r[c]) m[c] = r[c];
      for (const [c, v] of Object.entries(r.extra)) {
        const have = (m.extra[c] || "").split(", ").filter(Boolean);
        if (!have.includes(v)) m.extra[c] = [...have, v].join(", ");
      }
      m.extra["Rows in export"] = String(+(m.extra["Rows in export"] || 1) + 1);
    }
    return [...by.values()];
  }

  /* ---- what is left on a lead ---- */
  const DONE = () => (LIST && LIST.done_fields) || (SC && SC.done_fields) || ["apex", "az", "lead"];
  const filled = v => !!String(v == null ? "" : v).trim();
  function leftOn(l) {
    const s = l.s || {}, left = DONE().filter(k => !filled(s[k]));
    if (!s.az_dups) left.push("az_dups");
    if (!s.az_tagged) left.push("az_tagged");
    return left;
  }
  const TODO = [["", "Everything"], ["open", "Not done"], ["done", "Done"], ["apex", "No Apex Status"],
    ["az", "No AZ Status"], ["lead", "No Lead Status"], ["az_dups", "Duplicates not cleaned"], ["az_tagged", "Not tagged"],
    ["next", "Has a next step"], ["today", "Worked today"], ["dupe", "Same phone or email as another lead"]];

  function dupeSets(leads) {
    const by = {};
    for (const l of leads) {
      for (const k of [digits(l.phone) ? "p" + digits(l.phone) : "", l.email ? "e" + l.email.toLowerCase() : ""]) {
        if (k) (by[k] = by[k] || []).push(l.id);
      }
    }
    const n = {};
    for (const ids of Object.values(by)) if (ids.length > 1) for (const id of ids) n[id] = Math.max(n[id] || 0, ids.length);
    return n;
  }

  function filtered() {
    const leads = LIST.list.leads, dupes = dupeSets(leads), q = scF.q.toLowerCase().trim();
    return { dupes, rows: leads.filter(l => {
      const s = l.s || {};
      if (scF.who && (s.rep || "") !== scF.who) return false;
      if (scF.x) {
        const [c, val] = scF.x.split("\u0001");
        if (!String((l.extra || {})[c] || "").split(", ").includes(val)) return false;
      }
      const left = leftOn(l);
      const t = scF.todo;
      if (t === "open" && !left.length) return false;
      if (t === "done" && left.length) return false;
      if (["apex", "az", "lead", "az_dups", "az_tagged"].includes(t) && !left.includes(t)) return false;
      if (t === "next" && (!filled(s.next) || /^none$/i.test(s.next.trim()))) return false;
      if (t === "today" && s.date !== LIST.today) return false;
      if (t === "dupe" && !dupes[l.id]) return false;
      if (q && ![l.name, l.phone, l.email, l.az_id, l.source, l.stage, s.notes, s.action, s.next, s.rep, ...Object.values(l.extra || {})]
        .some(v => String(v || "").toLowerCase().includes(q))
        && !(digits(q) && digits(l.phone).includes(digits(q)))) return false;
      return true;
    }) };
  }

  /* ---- drawing ---- */
  function tile(label, n, of, hue) {
    const pct = of ? Math.round(100 * n / of) : 0;
    return `<div class="sctile" style="--th:${hue}"><span>${cesc(label)}</span><strong>${n.toLocaleString()}</strong>
      <small>of ${of.toLocaleString()} · ${pct}%</small><i style="width:${pct}%"></i></div>`;
  }
  function progressHtml(s) {
    return `<div class="sctiles">${tile("Fully done", s.done, s.count, "var(--good)")}${tile("Apex Status", s.apex, s.count, "var(--s3)")}
      ${tile("AZ Status", s.az, s.count, "var(--s4)")}${tile("Duplicates Cleaned", s.az_dups, s.count, "var(--s5)")}
      ${tile("Tagged", s.az_tagged, s.count, "var(--accent)")}${tile("Lead Status", s.lead || 0, s.count, "var(--warn)")}</div>`;
  }

  function pickerHtml() {
    const lists = SC.lists || [];
    return `<div class="sect svchero schero" style="--sc:var(--s3)">
      <h2>Lead Scrub</h2>
      <p class="sd">Each client on a scrub list is checked in <b>Apex</b> and in <b>AgencyZoom</b>: its status in both, its duplicates cleaned and tagged in AgencyZoom, and the lead updated. A client is done when Apex Status, AZ Status and Lead Status are filled in and both boxes are ticked.</p>
      <div class="controls">
        ${lists.length ? `<select id="scList" aria-label="Scrub list"><option value="">Pick a list…</option>${lists.map(l =>
          `<option value="${cesc(l.id)}"${l.id === scId ? " selected" : ""}>${cesc(l.name)} · ${l.done}/${l.count} done</option>`).join("")}</select>` : ""}
        ${SC.can_edit ? '<button type="button" class="btn ropri" id="scNew">Import a lead list</button>' : ""}
      </div>
      ${scMsg ? `<p class="romsg ${scMsg.err ? "bad" : "good"}" role="${scMsg.err ? "alert" : "status"}">${cesc(scMsg.err || scMsg.ok)}</p>` : ""}
      ${!lists.length && !scImport ? `<div class="empty">No scrub lists yet.${SC.can_edit ? " Import the report (Excel or CSV) as it comes." : ""}</div>` : ""}
    </div>`;
  }

  const thisMonth = () => { try { return new Date((SC && SC.today || "") + "T12:00:00").toLocaleDateString("en-US", { month: "short", year: "numeric" }); } catch (_) { return ""; } };

  function importHtml() {
    const { headers, rows, map, name } = scImport;
    const opt = (k) => `<select data-scmap="${k}"><option value="-1">—</option>${headers.map((h, i) =>
      `<option value="${i}"${map[k] === i ? " selected" : ""}>${cesc(h)}</option>`).join("")}</select>`;
    const preview = importRows().slice(0, 5);
    const xcols = [...new Set(preview.flatMap(r => Object.keys(r.extra)))];
    return `<div class="sect" style="--sc:var(--s4)">
      <h2>Import a lead list</h2>
      <p class="sd">${rows.length.toLocaleString()} rows in the file${scImport.merge ? `, ${importRows().length.toLocaleString()} people` : ""}. Check which column is which; every other column (line of business, risk segment, dates ...) is kept on the client as detail.</p>
      <label class="sccheck${scImport.merge ? " on" : ""}" style="margin-bottom:10px"><input type="checkbox" id="scMerge"${scImport.merge ? " checked" : ""}> One client per person (rows with the same name are combined)</label>
      <div class="scmap">
        <label>List name <input type="text" id="scName" value="${cesc(name)}" maxlength="120"></label>
        <label>Month <input type="text" id="scMonth" value="${cesc(scImport.month != null ? scImport.month : thisMonth())}" maxlength="40"></label>
        ${COLS.map(([k, l]) => `<label>${cesc(k === "name" ? "Client" : l)} ${opt(k)}</label>`).join("")}
        ${map.name < 0 ? `<label>First name ${opt("first")}</label><label>Last name ${opt("last")}</label>` : ""}
      </div>
      <div class="scroll"><table class="rotab"><thead><tr>${COLS.filter(([k]) => preview.some(r => r[k])).map(([k, l]) => `<th class="t">${cesc(k === "name" ? "Client" : l)}</th>`).join("")}${xcols.map(c => `<th class="t">${cesc(c)}</th>`).join("")}</tr></thead>
        <tbody>${preview.map(r => `<tr>${COLS.filter(([k]) => preview.some(x => x[k])).map(([k]) => `<td class="t">${cesc(r[k])}</td>`).join("")}${xcols.map(c => `<td class="t">${cesc(r.extra[c] || "")}</td>`).join("")}</tr>`).join("")}</tbody></table></div>
      <div class="rorow" style="margin-top:10px">
        <button type="button" class="btn ropri" id="scGo">Import ${importRows().length.toLocaleString()} clients</button>
        ${scId && LIST ? `<button type="button" class="btn" id="scAddTo">Add them to “${cesc(LIST.list.name)}”</button>` : ""}
        <button type="button" class="btn" id="scCancel">Cancel</button></div>
    </div>`;
  }

  // Suggestions for a choice / rep column: the field's own plus what the list already uses.
  function datalists() {
    const out = [];
    for (const f of LIST.fields) {
      if (f.type !== "choice" && f.type !== "rep") continue;
      const vals = new Set(f.options || []);
      // The ops team who work the scrub (staff.json's scrub_edit), and whoever is looking.
      if (f.type === "rep") for (const n of [...((window.STAFF || {}).people || []).filter(p => (p.status || "active") === "active" && (p.board || []).includes("scrub_edit")).map(p => p.name.split(" ")[0]), LIST.me]) if (n) vals.add(n);
      for (const l of LIST.list.leads) { const v = (l.s || {})[f.key]; if (filled(v)) vals.add(v); }
      out.push(`<datalist id="scdl-${f.key}">${[...vals].map(v => `<option value="${cesc(v)}">`).join("")}</datalist>`);
    }
    return out.join("");
  }

  function tone(f, v) {
    if (!filled(v)) return "";
    if (f.key === "apex" || f.key === "az") return /^active$/i.test(v) ? "ok" : /inactive|cancel|not in|not found/i.test(v) ? "bad" : "mid";
    if (f.key === "lead") return "ok";
    if (f.key === "next") return /^none$/i.test(v) ? "ok" : "mid";
    return "";
  }

  function cellHtml(l, f) {
    const s = l.s || {}, by = (l.by || {})[f.key];
    const tip = by ? ` title="${cesc(by.who)} · ${cesc(when(by.at))}"` : "";
    const data = `data-sclead="${cesc(l.id)}" data-scfield="${f.key}" aria-label="${cesc(f.label)}"${tip}`;
    const v = s[f.key] == null ? "" : s[f.key];
    if (f.type === "check") {
      return `<label class="sccheck${v ? " on" : ""}"${tip}><input type="checkbox" ${data}${v ? " checked" : ""}> ${cesc(f.label)}</label>`;
    }
    if (f.type === "date") return `<input type="date" class="scin scdate" ${data} value="${cesc(v)}">`;
    const list = f.type === "choice" || f.type === "rep" ? ` list="scdl-${f.key}"` : "";
    return `<input type="text" class="scin ${tone(f, v)}${f.key === "notes" ? " scwide" : ""}" ${data}${list} value="${cesc(v)}" maxlength="${f.max || 120}" placeholder="${cesc(f.key === "notes" ? "Notes" : "—")}">`;
  }

  let lastDupes = {};
  function rowHtml(l) {
    const F = k => LIST.fields.find(f => f.key === k);
    const besides = k => LIST.fields.filter(f => f.beside === k);
    const cols = LIST.fields.filter(f => !f.beside);
    const left = leftOn(l), extra = Object.entries(l.extra || {}).filter(([k]) => k !== "Rows in export");
    const cell = f => { const bs = besides(f.key);
      return `<td class="t sc-${f.key}">${cellHtml(l, f)}${bs.length ? `<div class="scbeside">${bs.map(b => cellHtml(l, b)).join("")}</div>` : ""}</td>`; };
    return `<tr class="${left.length ? "" : "scdone"}" data-row="${cesc(l.id)}">
      <td class="t scclient"><b>${cesc(l.name || "(no name)")}</b>${lastDupes[l.id] ? ` <span class="scdupe" title="${lastDupes[l.id]} clients share this phone or email">dup ×${lastDupes[l.id]}</span>` : ""}
        ${[l.phone, l.email].some(Boolean) ? `<div class="scsub">${[l.phone, l.email].filter(Boolean).map(cesc).join(" · ")}</div>` : ""}
        ${l.az_id || l.stage || l.assigned ? `<div class="scsub">${[l.az_id && "AZ " + l.az_id, l.stage, l.assigned && first(l.assigned)].filter(Boolean).map(cesc).join(" · ")}</div>` : ""}
        ${extra.length ? `<div class="scx">${extra.map(([k, v]) => `<span title="${cesc(k)}">${cesc(v)}</span>`).join("")}</div>` : ""}</td>
      ${cols.map(cell).join("")}
      <td>${left.length ? `<span class="scleft" title="Still to do: ${cesc(left.map(k => (F(k) || {}).label || k).join(", "))}">${left.length}</span>` : '<span class="scok" title="Done in both">✓</span>'}${LIST.can_edit ? `<button type="button" class="icon-btn del-btn" data-scrm="${cesc(l.id)}" aria-label="Take this client off the list" title="Take this client off the list">✕</button>` : ""}</td>
    </tr>`;
  }

  function listHtml() {
    const L = LIST.list, s = LIST.summary, fields = LIST.fields;
    const reps = [...new Set(L.leads.map(l => (l.s || {}).rep || "").filter(Boolean))].sort();
    // A filter on any detail column with a handful of values (LOB, risk segment, status).
    const xv = {};
    for (const l of L.leads) for (const [c, v] of Object.entries(l.extra || {})) for (const one of String(v).split(", ")) (xv[c] = xv[c] || new Set()).add(one);
    const xopts = Object.entries(xv).filter(([c, set]) => set.size > 1 && set.size <= 12 && c !== "Rows in export")
      .map(([c, set]) => `<optgroup label="${cesc(c)}">${[...set].sort().map(v => { const k = c + "\u0001" + v;
        return `<option value="${cesc(k)}"${k === scF.x ? " selected" : ""}>${cesc(c)}: ${cesc(v)}</option>`; }).join("")}</optgroup>`).join("");
    const { rows, dupes } = filtered();
    lastDupes = dupes;
    const head = fields.filter(f => !f.beside).map(f => `<th class="t">${cesc(f.label)}</th>`).join("");
    return `<div class="sect" style="--sc:var(--s3)">
      <h2>${cesc(L.name)}</h2>
      <p class="sd">${L.month ? cesc(L.month) + " · " : ""}Imported ${cesc(when(L.created_at))} by ${cesc(L.created_by || "")}. Every change saves at once and fills in the Date and Rep; hover a box to see who set it.</p>
      ${progressHtml(s)}
      <div class="controls scfilters">
        <input type="search" id="scQ" placeholder="Search client, notes, details" value="${cesc(scF.q)}" aria-label="Search">
        ${xopts ? `<select id="scX" aria-label="Detail"><option value="">Any detail</option>${xopts}</select>` : ""}
        ${reps.length ? `<select id="scWho" aria-label="Rep"><option value="">Every rep</option>${reps.map(w => `<option value="${cesc(w)}"${w === scF.who ? " selected" : ""}>${cesc(w)}</option>`).join("")}</select>` : ""}
        <select id="scTodo" aria-label="Show">${TODO.map(([k, l]) => `<option value="${k}"${k === scF.todo ? " selected" : ""}>${cesc(l)}</option>`).join("")}</select>
        <span class="romute">${rows.length.toLocaleString()} shown</span>
        <span style="flex:1"></span>
        <button type="button" class="btn" id="scCsv">Download CSV</button>
        ${LIST.can_edit ? `<button type="button" class="ghost rosmall" id="scRename">Rename</button><button type="button" class="ghost rosmall" id="scDel">Delete list</button>` : ""}
      </div>
      ${datalists()}
      ${rows.length ? `<div class="scroll"><table class="rotab sctab"><thead><tr><th class="t">Client</th>${head}<th></th></tr></thead><tbody>${rows.slice(0, scShow).map(rowHtml).join("")}</tbody></table></div>
        ${rows.length > scShow ? `<div class="rorow" style="margin-top:10px"><button type="button" class="btn" id="scMore">Show ${Math.min(200, rows.length - scShow)} more</button></div>` : ""}`
        : '<div class="empty">No clients match.</div>'}
    </div>`;
  }

  function repaint() {
    if (view !== "scrub" || !SC) return;
    const focus = document.activeElement && document.activeElement.id;
    $("#view").innerHTML = pickerHtml() + (scImport ? importHtml() : "") + (LIST && scId ? listHtml() : "");
    if (focus && $("#" + focus)) { const e = $("#" + focus); e.focus(); if (e.setSelectionRange && e.value) e.setSelectionRange(e.value.length, e.value.length); }
    wire();
  }

  async function openList(id) {
    scId = id; LIST = null; scShow = 200;
    if (!id) { repaint(); return; }
    try { LIST = await api(id); } catch (e) { scMsg = { err: e.message }; scId = ""; }
    repaint();
  }
  async function reloadLists() { try { SC = await api(""); } catch (_) {} }

  function showMsg() {
    const old = $("#view .schero .romsg");
    if (old) old.remove();
    if (!scMsg) return;
    const c = $("#view .schero .controls");
    if (c) c.insertAdjacentHTML("afterend", `<p class="romsg ${scMsg.err ? "bad" : "good"}" role="${scMsg.err ? "alert" : "status"}">${cesc(scMsg.err || scMsg.ok)}</p>`);
  }

  // One change: saved, then the server's copy of the client redraws just its
  // row (so typing in the next box is never lost) and the tiles.
  async function setField(leadId, field, value) {
    const L = LIST;                         // the list the change was made on, even if another opens meanwhile
    const lead = L && L.list.leads.find(l => l.id === leadId);
    if (!lead) return;
    const was = (lead.s || {})[field];
    lead.s = lead.s || {}; lead.s[field] = value;
    try {
      const out = await api(L.list.id, { op: "set", lead: leadId, field, value });
      Object.assign(lead, out.lead); L.summary = out.summary; scMsg = null;
      const card = (SC.lists || []).find(x => x.id === L.list.id); if (card) Object.assign(card, out.summary);
    } catch (e) { lead.s[field] = was; scMsg = { err: `Not saved: ${e.message}` }; }
    if (LIST !== L || view !== "scrub") return;
    showMsg();
    const t = $("#view .sctiles"); if (t) t.outerHTML = progressHtml(L.summary);
    const tr = $(`#view tr[data-row="${CSS.escape(leadId)}"]`);
    if (tr) {
      const active = document.activeElement, keep = active && tr.contains(active) ? active.dataset.scfield : "";
      tr.outerHTML = rowHtml(lead);
      const nu = $(`#view tr[data-row="${CSS.escape(leadId)}"]`);
      wireRow(nu);
      if (keep) { const e = nu.querySelector(`[data-scfield="${keep}"]`); if (e && e.type !== "checkbox") e.focus(); }
    }
  }

  function download() {
    const L = LIST.list, fields = LIST.fields;
    const extras = [...new Set(L.leads.flatMap(l => Object.keys(l.extra || {})))];
    const head = ["Client", ...fields.map(f => f.label), "Done", "Phone", "Email", "AgencyZoom ID", ...extras];
    const lines = [head.map(csvCell).join(",")];
    for (const l of filtered().rows) {
      const s = l.s || {};
      lines.push([l.name || "", ...fields.map(f => f.type === "check" ? (s[f.key] ? "Yes" : "No") : (s[f.key] || "")),
        leftOn(l).length ? "No" : "Yes", l.phone || "", l.email || "", l.az_id || "", ...extras.map(k => (l.extra || {})[k] || "")].map(csvCell).join(","));
    }
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob(["﻿" + lines.join("\r\n")], { type: "text/csv" }));
    a.download = `${L.name.replace(/[^\w -]+/g, "").trim() || "lead-scrub"}.csv`;
    document.body.appendChild(a); a.click(); a.remove();
  }

  function startImport() {
    const inp = document.createElement("input");
    inp.type = "file"; inp.accept = ".xlsx,.xls,.csv,.tsv,.txt";
    inp.onchange = async () => {
      const f = inp.files && inp.files[0]; if (!f) return;
      let t;
      try { t = tidy(await readFile(f)); } catch (e) { scMsg = { err: `Could not read that file: ${e.message}` }; repaint(); return; }
      if (!t || !t.rows.length) { scMsg = { err: "That file has no leads in it. It needs a header row and at least one lead." }; repaint(); return; }
      const nice = f.name.replace(/\.[^.]+$/, "").replace(/-\d{4}-\d{2}-\d{2}-[\d-]+(_\d+)?$/, "").replace(/_/g, " ").trim();
      scImport = { name: nice, headers: t.headers, rows: t.rows, map: guessMap(t.headers), merge: true };
      scMsg = null; repaint();
    };
    inp.click();
  }

  function wireRow(tr) {
    tr.querySelectorAll("[data-scfield]").forEach(e => e.onchange = () =>
      setField(e.dataset.sclead, e.dataset.scfield, e.type === "checkbox" ? e.checked : e.value.trim()));
    tr.querySelectorAll("input.scin[type=text]").forEach(e => e.onkeydown = ev => { if (ev.key === "Enter") e.blur(); });
    const rm = tr.querySelector("[data-scrm]"); if (rm) rm.onclick = () => removeLead(rm.dataset.scrm);
  }
  async function removeLead(id) {
    const l = LIST.list.leads.find(x => x.id === id);
    if (!l || !confirm(`Take ${l.name || "this client"} off the list?`)) return;
    try {
      const out = await api(scId, { op: "remove", lead: l.id });
      LIST.list.leads = LIST.list.leads.filter(x => x.id !== l.id); LIST.summary = out.summary;
    } catch (e) { scMsg = { err: e.message }; }
    repaint();
  }

  function wire() {
    const v = $("#view");
    const sel = $("#scList"); if (sel) sel.onchange = () => { scMsg = null; openList(sel.value); };
    const nb = $("#scNew"); if (nb) nb.onclick = startImport;
    if (scImport) {
      v.querySelectorAll("[data-scmap]").forEach(s => s.onchange = () => { scImport.map[s.dataset.scmap] = +s.value; scImport.name = $("#scName").value; repaint(); });
      $("#scName").oninput = e => { scImport.name = e.target.value; };
      $("#scMonth").oninput = e => { scImport.month = e.target.value; };
      $("#scMerge").onchange = e => { scImport.merge = e.target.checked; scImport.name = $("#scName").value; repaint(); };
      $("#scCancel").onclick = () => { scImport = null; repaint(); };
      const go = async (addTo) => {
        const rows = importRows(), name = $("#scName").value.trim(), month = $("#scMonth").value.trim();
        try {
          if (addTo) {
            const out = await api(scId, { op: "add", rows, month });
            scMsg = { ok: `Added ${out.added.toLocaleString()} clients to ${LIST.list.name}.` };
            scImport = null; await reloadLists(); await openList(scId);
          } else {
            const out = await api("", { op: "create", name, month, rows });
            scMsg = { ok: `Imported ${out.summary.count.toLocaleString()} clients as “${out.summary.name}”.` };
            scImport = null; await reloadLists(); await openList(out.summary.id);
          }
        } catch (e) { scMsg = { err: e.message }; repaint(); }
      };
      $("#scGo").onclick = () => go(false);
      const at = $("#scAddTo"); if (at) at.onclick = () => go(true);
    }
    if (!LIST) return;
    v.querySelectorAll(".sctab tbody tr").forEach(wireRow);
    const q = $("#scQ"); if (q) q.oninput = () => { scF.q = q.value; scShow = 200; repaint(); };
    const w = $("#scWho"); if (w) w.onchange = () => { scF.who = w.value; scShow = 200; repaint(); };
    const x = $("#scX"); if (x) x.onchange = () => { scF.x = x.value; scShow = 200; repaint(); };
    const t = $("#scTodo"); if (t) t.onchange = () => { scF.todo = t.value; scShow = 200; repaint(); };
    const m = $("#scMore"); if (m) m.onclick = () => { scShow += 200; repaint(); };
    $("#scCsv").onclick = download;
    const rn = $("#scRename"); if (rn) rn.onclick = async () => {
      const name = prompt("Name this list", LIST.list.name); if (!name || !name.trim()) return;
      try { await api(scId, { op: "rename", name: name.trim() }); LIST.list.name = name.trim(); await reloadLists(); } catch (e) { scMsg = { err: e.message }; }
      repaint();
    };
    const dl = $("#scDel"); if (dl) dl.onclick = async () => {
      if (!confirm(`Delete “${LIST.list.name}” and every status on it? This cannot be undone.`)) return;
      try { await api(scId, { op: "delete" }); scMsg = { ok: `Deleted ${LIST.list.name}.` }; LIST = null; scId = ""; await reloadLists(); } catch (e) { scMsg = { err: e.message }; }
      repaint();
    };
  }

  window.scrubPaint = async function scrubPaint() {
    $("#topsub").textContent = "leads cleaned up in Apex and AgencyZoom";
    if (!SC) $("#view").innerHTML = '<div class="empty">Loading…</div>';
    await reloadLists();
    if (!SC) { $("#view").innerHTML = '<div class="empty">The lead scrub is only open to the ops team.</div>'; return; }
    if (!scId && (SC.lists || []).length) scId = SC.lists[0].id;
    if (scId) { await openList(scId); return; }
    repaint();
  };

  const css = document.createElement("style");
  css.textContent = `
.sctiles { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; margin: 10px 0 14px; }
@media (max-width: 900px) { .sctiles { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.sctile { position: relative; overflow: hidden; background: var(--surface-raised); border: var(--bw, 2px) solid var(--border-strong); border-top: 5px solid var(--th); border-radius: 12px; padding: 10px 12px 14px; }
.sctile span { display: block; text-transform: uppercase; letter-spacing: .07em; font-size: 11px; font-weight: 700; color: var(--text-muted); }
.sctile strong { font-family: var(--display); font-weight: var(--dw, 700); font-size: 28px; }
.sctile small { display: block; color: var(--text-secondary); font-size: 12px; }
.sctile i { position: absolute; left: 0; bottom: 0; height: 5px; background: var(--th); }
.scfilters { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 10px; }
.scfilters input[type=search], .scmap input, .scmap select { font: inherit; font-size: 14px; padding: 7px 10px; border: 1px solid var(--border-strong); border-radius: 10px; background: var(--surface); color: var(--text-primary); }
.scfilters input[type=search] { min-width: 240px; }
.scmap { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; margin: 8px 0 12px; }
.scmap label { display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 700; color: var(--text-secondary); }
.sctab td { vertical-align: top; }
.sctab tr.scdone td { background: color-mix(in oklab, var(--good) 9%, transparent); }
.scsub { font-size: 12px; color: var(--text-secondary); }
.sctab th small { font-weight: 500; color: var(--text-muted); }
.scclient { min-width: 190px; max-width: 260px; }
.scin { box-sizing: border-box; font: inherit; font-size: 13px; padding: 5px 7px; border-radius: 8px; border: 1px solid var(--border); background: var(--surface); color: var(--text-primary); width: 128px; }
.scin:focus { border-color: var(--accent); outline: none; }
.scin.scwide { width: 220px; }
.scin.scdate { width: 132px; }
.sc-month .scin { width: 86px; } .sc-rep .scin { width: 96px; }
.scin.ok { border-color: var(--good); background: color-mix(in oklab, var(--good) 14%, var(--surface)); }
.scin.mid { border-color: var(--warn); background: color-mix(in oklab, var(--warn) 10%, var(--surface)); }
.scin.bad { border-color: var(--bad); background: color-mix(in oklab, var(--bad) 12%, var(--surface)); }
.sc-az .scin { width: 100%; min-width: 150px; }
.scbeside { display: flex; gap: 4px; margin-top: 4px; }
.scbeside .sccheck { font-size: 12px; white-space: nowrap; padding: 1px 6px; }
.scleft { display: inline-block; min-width: 20px; text-align: center; font-size: 12px; font-weight: 700; color: var(--text-muted); border: 1px solid var(--border); border-radius: 10px; margin-right: 4px; }
.sccheck { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; cursor: pointer; padding: 2px 8px; border-radius: 8px; border: 1px solid var(--border); width: fit-content; }
.sccheck.on { border-color: var(--good); background: color-mix(in oklab, var(--good) 14%, transparent); font-weight: 600; }
.scdupe { font-size: 11px; font-weight: 700; color: var(--warn); border: 1px solid var(--warn); border-radius: 6px; padding: 0 5px; }
.scok { color: var(--good); font-weight: 800; font-size: 18px; margin-right: 4px; }
.scx { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }
.scx span { font-size: 11px; padding: 1px 6px; border-radius: 6px; background: color-mix(in oklab, var(--s4) 14%, transparent); }
`;
  document.head.appendChild(css);
})();
