/* The lead scrub tracker (Frank, 2026-10-02: "an interactive way to track a
   list of leads we are scrubbing, making sure they are updated in both apex
   and agency zoom"). Sales Center > Lead Scrub, shown only to the people
   /api/scrub answers (site/scrub.js, SCRUB_VIEWERS).

   A manager imports an AgencyZoom lead export (CSV) as a scrub list; the
   columns are matched by their headers and can be changed before importing.
   Each lead then gets its Apex status and its AgencyZoom status with the
   Duplicates Cleaned and Tagged boxes beside it, saved as soon as it is
   picked, with who and when on hover. The fields and their options come
   from the Worker (FIELDS), so this draws whatever it is sent. Filters by
   who the lead is assigned to, what is left to do and a search; leads on
   the same phone or email are marked so the duplicates are easy to find;
   the list downloads as a CSV with every status. Uses the board's own
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

  (async function scInit() {
    try { SC = await api(""); } catch (_) { return; }
    if (!CENTERS.salescenter.some(([k]) => k === "scrub")) CENTERS.salescenter.push(["scrub", "Lead Scrub"]);
    SEARCH_PAGES.push(["Lead Scrub", "Sales Center · leads cleaned up in Apex and AgencyZoom", "scrub"]);
    paintCenterBar();
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
  const DONE = () => (SC && SC.done_statuses) || ["Updated", "No changes needed"];
  function leftOn(l) {
    const s = l.s || {}, d = DONE(), left = [];
    if (!d.includes(s.apex)) left.push("apex");
    if (!d.includes(s.az)) left.push("az");
    if (!s.az_dups) left.push("az_dups");
    if (!s.az_tagged) left.push("az_tagged");
    return left;
  }
  const TODO = [["", "Everything"], ["open", "Not done"], ["done", "Done"], ["apex", "Needs Apex"],
    ["az", "Needs AgencyZoom"], ["az_dups", "Duplicates not cleaned"], ["az_tagged", "Not tagged"], ["dupe", "Same phone or email as another lead"],
    ["problem", "Not found / needs follow-up"]];

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
      if (scF.who && (l.assigned || "") !== scF.who) return false;
      if (scF.x) {
        const [c, val] = scF.x.split("\u0001");
        if (!String((l.extra || {})[c] || "").split(", ").includes(val)) return false;
      }
      const left = leftOn(l);
      const t = scF.todo;
      if (t === "open" && !left.length) return false;
      if (t === "done" && left.length) return false;
      if (["apex", "az", "az_dups", "az_tagged"].includes(t) && !left.includes(t)) return false;
      if (t === "dupe" && !dupes[l.id]) return false;
      if (t === "problem" && !["Not found", "Needs follow-up"].some(x => (l.s || {}).apex === x || (l.s || {}).az === x)) return false;
      if (q && ![l.name, l.phone, l.email, l.az_id, l.source, l.stage, (l.s || {}).notes].some(v => String(v || "").toLowerCase().includes(q))
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
    return `<div class="sctiles">${tile("Fully done", s.done, s.count, "var(--good)")}${tile("Apex", s.apex, s.count, "var(--s3)")}
      ${tile("AgencyZoom", s.az, s.count, "var(--s4)")}${tile("Duplicates Cleaned", s.az_dups, s.count, "var(--s5)")}
      ${tile("Tagged", s.az_tagged, s.count, "var(--accent)")}</div>`;
  }

  function pickerHtml() {
    const lists = SC.lists || [];
    return `<div class="sect svchero schero" style="--sc:var(--s3)">
      <h2>Lead Scrub</h2>
      <p class="sd">Every lead on a scrub list is checked off in <b>Apex</b> and in <b>AgencyZoom</b>, where its duplicates are cleaned and it is tagged. A lead is done when all four are.</p>
      <div class="controls">
        ${lists.length ? `<select id="scList" aria-label="Scrub list"><option value="">Pick a list…</option>${lists.map(l =>
          `<option value="${cesc(l.id)}"${l.id === scId ? " selected" : ""}>${cesc(l.name)} · ${l.done}/${l.count} done</option>`).join("")}</select>` : ""}
        ${SC.can_edit ? '<button type="button" class="btn ropri" id="scNew">Import a lead list</button>' : ""}
      </div>
      ${scMsg ? `<p class="romsg ${scMsg.err ? "bad" : "good"}" role="${scMsg.err ? "alert" : "status"}">${cesc(scMsg.err || scMsg.ok)}</p>` : ""}
      ${!lists.length && !scImport ? `<div class="empty">No scrub lists yet.${SC.can_edit ? " Export the leads from AgencyZoom as a CSV and import it here." : " A manager imports the first one."}</div>` : ""}
    </div>`;
  }

  function importHtml() {
    const { headers, rows, map, name } = scImport;
    const opt = (k) => `<select data-scmap="${k}"><option value="-1">—</option>${headers.map((h, i) =>
      `<option value="${i}"${map[k] === i ? " selected" : ""}>${cesc(h)}</option>`).join("")}</select>`;
    const preview = importRows().slice(0, 5);
    const xcols = [...new Set(preview.flatMap(r => Object.keys(r.extra)))];
    return `<div class="sect" style="--sc:var(--s4)">
      <h2>Import a lead list</h2>
      <p class="sd">${rows.length.toLocaleString()} rows in the file${scImport.merge ? `, ${importRows().length.toLocaleString()} people` : ""}. Check which column is which; every other column (line of business, risk segment, dates ...) is kept on the lead as detail.</p>
      <label class="sccheck${scImport.merge ? " on" : ""}" style="margin-bottom:10px"><input type="checkbox" id="scMerge"${scImport.merge ? " checked" : ""}> One lead per person (rows with the same name are combined)</label>
      <div class="scmap">
        <label>List name <input type="text" id="scName" value="${cesc(name)}" maxlength="120"></label>
        ${COLS.map(([k, l]) => `<label>${cesc(l)} ${opt(k)}</label>`).join("")}
        ${map.name < 0 ? `<label>First name ${opt("first")}</label><label>Last name ${opt("last")}</label>` : ""}
      </div>
      <div class="scroll"><table class="rotab"><thead><tr>${COLS.filter(([k]) => preview.some(r => r[k])).map(([, l]) => `<th class="t">${cesc(l)}</th>`).join("")}${xcols.map(c => `<th class="t">${cesc(c)}</th>`).join("")}</tr></thead>
        <tbody>${preview.map(r => `<tr>${COLS.filter(([k]) => preview.some(x => x[k])).map(([k]) => `<td class="t">${cesc(r[k])}</td>`).join("")}${xcols.map(c => `<td class="t">${cesc(r.extra[c] || "")}</td>`).join("")}</tr>`).join("")}</tbody></table></div>
      <div class="rorow" style="margin-top:10px">
        <button type="button" class="btn ropri" id="scGo">Import ${importRows().length.toLocaleString()} leads</button>
        ${scId && LIST ? `<button type="button" class="btn" id="scAddTo">Add them to “${cesc(LIST.list.name)}”</button>` : ""}
        <button type="button" class="btn" id="scCancel">Cancel</button></div>
    </div>`;
  }

  function cellHtml(l, f) {
    const s = l.s || {}, by = (l.by || {})[f.key];
    const tip = by ? ` title="${cesc(by.who)} · ${cesc(when(by.at))}"` : "";
    if (f.type === "check") {
      return `<label class="sccheck${s[f.key] ? " on" : ""}"${tip}><input type="checkbox" data-sclead="${cesc(l.id)}" data-scfield="${f.key}"${s[f.key] ? " checked" : ""}> ${cesc(f.label)}</label>`;
    }
    const v = s[f.key] || f.options[0];
    const cls = DONE().includes(v) ? "ok" : /not found|follow/i.test(v) ? "bad" : v === f.options[0] ? "" : "mid";
    return `<select class="scsel ${cls}" data-sclead="${cesc(l.id)}" data-scfield="${f.key}" aria-label="${cesc(f.label)}"${tip}>${f.options.map(o =>
      `<option${o === v ? " selected" : ""}>${cesc(o)}</option>`).join("")}</select>`;
  }

  function listHtml() {
    const L = LIST.list, s = LIST.summary, fields = LIST.fields;
    const apex = fields.filter(f => !f.group && f.key !== "az"), az = fields.filter(f => f.key === "az" || f.group === "az");
    const who = [...new Set(L.leads.map(l => l.assigned || ""))].sort();
    // A filter on any detail column with a handful of values (LOB, risk segment, status).
    const xv = {};
    for (const l of L.leads) for (const [c, v] of Object.entries(l.extra || {})) for (const one of String(v).split(", ")) (xv[c] = xv[c] || new Set()).add(one);
    const xopts = Object.entries(xv).filter(([c, set]) => set.size > 1 && set.size <= 12 && c !== "Rows in export")
      .map(([c, set]) => `<optgroup label="${cesc(c)}">${[...set].sort().map(v => { const k = c + "\u0001" + v;
        return `<option value="${cesc(k)}"${k === scF.x ? " selected" : ""}>${cesc(c)}: ${cesc(v)}</option>`; }).join("")}</optgroup>`).join("");
    const { rows, dupes } = filtered();
    const anyAssigned = L.leads.some(l => l.assigned || l.source);
    const shown = rows.slice(0, scShow);
    const tr = shown.map(l => {
      const left = leftOn(l), extra = Object.entries(l.extra || {});
      return `<tr class="${left.length ? "" : "scdone"}" data-row="${cesc(l.id)}">
        <td class="t"><b>${cesc(l.name || "(no name)")}</b>${dupes[l.id] ? ` <span class="scdupe" title="${dupes[l.id]} leads share this phone or email">dup ×${dupes[l.id]}</span>` : ""}
          <div class="scsub">${[l.phone, l.email].filter(Boolean).map(cesc).join(" · ")}</div>
          ${l.az_id ? `<div class="scsub">AZ ${cesc(l.az_id)}${l.stage ? " · " + cesc(l.stage) : ""}</div>` : l.stage ? `<div class="scsub">${cesc(l.stage)}</div>` : ""}
          ${extra.length ? `<div class="scx">${extra.map(([k, v]) => `<span title="${cesc(k)}"><i>${cesc(k)}</i> ${cesc(v)}</span>`).join("")}</div>` : ""}</td>
        ${anyAssigned ? `<td class="t">${badge(l.assigned)}${l.source ? `<div class="scsub">${cesc(l.source)}</div>` : ""}</td>` : ""}
        <td class="t scapex">${apex.map(f => cellHtml(l, f)).join("")}</td>
        <td class="t scaz">${az.map(f => cellHtml(l, f)).join("")}</td>
        <td class="t"><input type="text" class="scnote" data-sclead="${cesc(l.id)}" data-scfield="notes" value="${cesc((l.s || {}).notes || "")}" maxlength="500" placeholder="Note"${(l.by || {}).notes ? ` title="${cesc(l.by.notes.who)} · ${cesc(when(l.by.notes.at))}"` : ""}></td>
        <td>${left.length ? "" : '<span class="scok" title="Done in both">✓</span>'}${LIST.can_edit ? `<button type="button" class="icon-btn del-btn" data-scrm="${cesc(l.id)}" aria-label="Take this lead off the list" title="Take this lead off the list">✕</button>` : ""}</td>
      </tr>`;
    }).join("");
    return `<div class="sect" style="--sc:var(--s3)">
      <h2>${cesc(L.name)}</h2>
      <p class="sd">Imported ${cesc(when(L.created_at))} by ${cesc(L.created_by || "")}. Every change saves at once; hover a status to see who set it.</p>
      ${progressHtml(s)}
      <div class="controls scfilters">
        <input type="search" id="scQ" placeholder="Search name, phone, email, ID" value="${cesc(scF.q)}" aria-label="Search">
        ${xopts ? `<select id="scX" aria-label="Detail"><option value="">Any detail</option>${xopts}</select>` : ""}
        <select id="scWho" aria-label="Assigned to"${who.length < 2 ? " hidden" : ""}><option value="">Everyone</option>${who.map(w => `<option value="${cesc(w)}"${w === scF.who ? " selected" : ""}>${cesc(w || "Unassigned")}</option>`).join("")}</select>
        <select id="scTodo" aria-label="Show">${TODO.map(([k, l]) => `<option value="${k}"${k === scF.todo ? " selected" : ""}>${cesc(l)}</option>`).join("")}</select>
        <span class="romute">${rows.length.toLocaleString()} shown</span>
        <span style="flex:1"></span>
        <button type="button" class="btn" id="scCsv">Download CSV</button>
        ${LIST.can_edit ? `<button type="button" class="ghost rosmall" id="scRename">Rename</button><button type="button" class="ghost rosmall" id="scDel">Delete list</button>` : ""}
      </div>
      ${rows.length ? `<div class="scroll"><table class="rotab sctab"><thead><tr><th class="t">Lead</th>${anyAssigned ? '<th class="t">Assigned</th>' : ""}<th class="t">Apex</th><th class="t">AgencyZoom</th><th class="t">Note</th><th></th></tr></thead><tbody>${tr}</tbody></table></div>
        ${rows.length > scShow ? `<div class="rorow" style="margin-top:10px"><button type="button" class="btn" id="scMore">Show ${Math.min(200, rows.length - scShow)} more</button></div>` : ""}`
        : '<div class="empty">No leads match.</div>'}
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

  // One change: shown at once, saved, then the server's copy of the lead.
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
    if (field !== "notes") repaint();
    else if (LIST === L) { const t = $("#view .sctiles"); if (t) t.outerHTML = progressHtml(L.summary); }
  }

  function download() {
    const L = LIST.list, fields = LIST.fields;
    const extras = [...new Set(L.leads.flatMap(l => Object.keys(l.extra || {})))];
    const head = [...COLS.map(c => c[1]), ...fields.map(f => f.label), "Note", "Done", "Last changed by", ...extras];
    const lines = [head.map(csvCell).join(",")];
    for (const l of filtered().rows) {
      const s = l.s || {}, last = Object.values(l.by || {}).sort((a, b) => String(b.at).localeCompare(String(a.at)))[0];
      lines.push([...COLS.map(([k]) => l[k] || ""), ...fields.map(f => f.type === "check" ? (s[f.key] ? "Yes" : "No") : (s[f.key] || "")),
        s.notes || "", leftOn(l).length ? "No" : "Yes", last ? `${last.who} ${when(last.at)}` : "", ...extras.map(k => (l.extra || {})[k] || "")].map(csvCell).join(","));
    }
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([lines.join("\r\n")], { type: "text/csv" }));
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

  function wire() {
    const v = $("#view");
    const sel = $("#scList"); if (sel) sel.onchange = () => { scMsg = null; openList(sel.value); };
    const nb = $("#scNew"); if (nb) nb.onclick = startImport;
    if (scImport) {
      v.querySelectorAll("[data-scmap]").forEach(s => s.onchange = () => { scImport.map[s.dataset.scmap] = +s.value; scImport.name = $("#scName").value; repaint(); });
      $("#scName").oninput = e => { scImport.name = e.target.value; };
      $("#scMerge").onchange = e => { scImport.merge = e.target.checked; scImport.name = $("#scName").value; repaint(); };
      $("#scCancel").onclick = () => { scImport = null; repaint(); };
      const go = async (addTo) => {
        const rows = importRows(), name = $("#scName").value.trim();
        try {
          if (addTo) {
            const out = await api(scId, { op: "add", rows });
            scMsg = { ok: `Added ${out.added.toLocaleString()} leads to ${LIST.list.name}.` };
            scImport = null; await reloadLists(); await openList(scId);
          } else {
            const out = await api("", { op: "create", name, rows });
            scMsg = { ok: `Imported ${out.summary.count.toLocaleString()} leads as “${out.summary.name}”.` };
            scImport = null; await reloadLists(); await openList(out.summary.id);
          }
        } catch (e) { scMsg = { err: e.message }; repaint(); }
      };
      $("#scGo").onclick = () => go(false);
      const at = $("#scAddTo"); if (at) at.onclick = () => go(true);
    }
    if (!LIST) return;
    v.querySelectorAll("select.scsel").forEach(s => s.onchange = () => setField(s.dataset.sclead, s.dataset.scfield, s.value));
    v.querySelectorAll(".sccheck input").forEach(c => c.onchange = () => setField(c.dataset.sclead, c.dataset.scfield, c.checked));
    v.querySelectorAll("input.scnote").forEach(n => n.onchange = () => setField(n.dataset.sclead, "notes", n.value.trim()));
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
    v.querySelectorAll("[data-scrm]").forEach(b => b.onclick = async () => {
      const l = LIST.list.leads.find(x => x.id === b.dataset.scrm);
      if (!l || !confirm(`Take ${l.name || "this lead"} off the list?`)) return;
      try {
        const out = await api(scId, { op: "remove", lead: l.id });
        LIST.list.leads = LIST.list.leads.filter(x => x.id !== l.id); LIST.summary = out.summary;
      } catch (e) { scMsg = { err: e.message }; }
      repaint();
    });
  }

  window.scrubPaint = async function scrubPaint() {
    $("#topsub").textContent = "leads cleaned up in Apex and AgencyZoom";
    if (!SC) $("#view").innerHTML = '<div class="empty">Loading…</div>';
    await reloadLists();
    if (!SC) { $("#view").innerHTML = '<div class="empty">The lead scrub is not open to you.</div>'; return; }
    if (!scId && (SC.lists || []).length) scId = SC.lists[0].id;
    if (scId) { await openList(scId); return; }
    repaint();
  };

  const css = document.createElement("style");
  css.textContent = `
.sctiles { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin: 10px 0 14px; }
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
.scapex, .scaz { min-width: 170px; }
.scaz { display: flex; flex-direction: column; gap: 5px; }
.scsel { font: inherit; font-size: 13px; padding: 5px 8px; border-radius: 8px; border: 1px solid var(--border-strong); background: var(--surface); color: var(--text-primary); }
.scsel.ok { border-color: var(--good); background: color-mix(in oklab, var(--good) 16%, var(--surface)); }
.scsel.mid { border-color: var(--warn); }
.scsel.bad { border-color: var(--bad); background: color-mix(in oklab, var(--bad) 14%, var(--surface)); }
.sccheck { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; cursor: pointer; padding: 2px 8px; border-radius: 8px; border: 1px solid var(--border); width: fit-content; }
.sccheck.on { border-color: var(--good); background: color-mix(in oklab, var(--good) 14%, transparent); font-weight: 600; }
.scnote { font: inherit; font-size: 13px; padding: 5px 8px; border-radius: 8px; border: 1px solid var(--border); background: var(--surface); color: var(--text-primary); min-width: 160px; width: 100%; }
.scdupe { font-size: 11px; font-weight: 700; color: var(--warn); border: 1px solid var(--warn); border-radius: 6px; padding: 0 5px; }
.scok { color: var(--good); font-weight: 800; font-size: 18px; margin-right: 4px; }
.scx { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }
.scx span { font-size: 12px; padding: 1px 6px; border-radius: 6px; background: color-mix(in oklab, var(--s4) 14%, transparent); }
.scx i { font-style: normal; color: var(--text-muted); }
`;
  document.head.appendChild(css);
})();
