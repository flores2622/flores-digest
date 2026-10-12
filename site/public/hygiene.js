/* The CRM Hygiene & Audit Log (Frank, 2026-10-06: "go into my drive and look
   at file named CRM Hygiene, build that into pantheon, in a new category for
   operatonis only"). Operations Center > CRM Hygiene, shown only to the
   people /api/hygiene answers (site/hygiene.js, staff.json's `hygiene`: the
   ops team); for anyone else the page never enters the menu or the search.

   Amanda's doc, as a log: accounts handled incorrectly, assigned improperly
   or left without the notes, tasks and follow-ups the playbook asks for --
   Client, Policy #, Rep, What happened, Date -- plus which line of the
   doc's Redirection Standard it missed and a "Reviewed in a one-on-one"
   tick. The standard itself sits beside the log in the doc's words. Every
   change saves at once with who and when; hover a cell to see it. Uses
   the board's own helpers ($, cesc, pbadge, DOT, opsShow, view), so it
   loads after index.html's main script. */
(function () {
  let HG = null;            // the last /api/hygiene answer
  let hgF = { q: "", rep: "", std: "", show: "" };   // show: "" all, "open" not yet reviewed, "done" reviewed
  let hgMsg = null;         // {ok|err}
  let hgEdit = "";          // the entry open for editing
  let hgAddOpen = false;

  const first = n => String(n || "").split(" ")[0];
  const badge = n => n ? (DOT[n] ? pbadge(DOT[n], first(n)) : `<b>${cesc(first(n))}</b>`) : '<span class="romute">—</span>';
  const when = iso => { try { return new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }); } catch (_) { return ""; } };
  const dayTxt = d => { try { return new Date(d + "T12:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }); } catch (_) { return d || ""; } };
  const stdOf = k => (HG.standards || []).find(s => s.key === k);

  async function api(body) {
    const r = await fetch("/api/hygiene", body ? {
      method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) } : { cache: "no-store" });
    const out = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(out.error || `could not reach the board (${r.status})`);
    return out;
  }

  // Unhide the page for whoever the Worker lets see it. HYG_READY says
  // whether it did, so a refresh on this page can reopen it (index.html).
  window.HYG_READY = (async function hgInit() {
    try { HG = await api(); } catch (_) { return false; }
    opsShow("hygiene", "CRM Hygiene", "accounts handled wrong, for the one-on-ones");
    return true;
  })();

  // The people an entry can be about: the service team first (the doc is
  // about CSR redirection), then everyone else active -- and anything typed.
  function repNames() {
    const people = ((window.STAFF || {}).people || []).filter(p => (p.status || "active") === "active" && p.name);
    const svc = people.filter(p => p.service).sort((a, b) => ((a.service || {}).order || 9) - ((b.service || {}).order || 9));
    const rest = people.filter(p => !p.service);
    const out = [];
    for (const p of [...svc, ...rest]) if (!out.includes(p.name)) out.push(p.name);
    for (const e of HG.entries || []) if (e.rep && !out.includes(e.rep)) out.push(e.rep);
    return out;
  }

  function filtered() {
    const q = hgF.q.trim().toLowerCase();
    return (HG.entries || []).filter(e => {
      if (hgF.rep && e.rep !== hgF.rep) return false;
      if (hgF.std && e.standard !== hgF.std) return false;
      if (hgF.show === "open" && e.reviewed) return false;
      if (hgF.show === "done" && !e.reviewed) return false;
      if (q && ![e.client, e.policy, e.issue, e.rep, e.by].some(v => String(v || "").toLowerCase().includes(q))) return false;
      return true;
    }).sort((a, b) => String(b.date).localeCompare(String(a.date)) || String(b.at).localeCompare(String(a.at)));
  }

  function tile(label, n, hue, sub) {
    return `<div class="hgtile" style="--th:${hue}"><span>${cesc(label)}</span><strong>${n.toLocaleString()}</strong>${sub ? `<small>${sub}</small>` : ""}</div>`;
  }
  function heroHtml() {
    const E = HG.entries || [], open = E.filter(e => !e.reviewed).length;
    const month = (HG.today || "").slice(0, 7), thisMonth = E.filter(e => String(e.date || "").startsWith(month)).length;
    const byRep = {};
    for (const e of E) byRep[e.rep || ""] = (byRep[e.rep || ""] || 0) + 1;
    const reps = Object.entries(byRep).filter(([r]) => r).sort((a, b) => b[1] - a[1]);
    const byStd = {};
    for (const e of E) if (e.standard) byStd[e.standard] = (byStd[e.standard] || 0) + 1;
    const top = Object.entries(byStd).sort((a, b) => b[1] - a[1])[0];
    return `<div class="sect svchero" style="--sc:var(--s5)">
      <h2>CRM Hygiene &amp; Audit Log</h2>
      <p class="sd">${cesc(HG.intro || "")}</p>
      <div class="hgtiles">
        ${tile("Entries", E.length, "var(--s5)")}
        ${tile("This month", thisMonth, "var(--s3)")}
        ${tile("To review in a one-on-one", open, open ? "var(--warn)" : "var(--good)", open ? "not yet reviewed" : "all reviewed")}
        ${tile("Missed most", top ? top[1] : 0, "var(--s4)", top ? cesc((stdOf(top[0]) || {}).label || top[0]) : "—")}
      </div>
      ${reps.length ? `<div class="hgreps">${reps.map(([r, n]) => `<button type="button" class="hgrep${hgF.rep === r ? " on" : ""}" data-hgrep="${cesc(r)}">${badge(r)} <b>${n}</b></button>`).join("")}</div>` : ""}
      ${hgMsg ? `<p class="romsg ${hgMsg.err ? "bad" : "good"}" role="${hgMsg.err ? "alert" : "status"}">${cesc(hgMsg.err || hgMsg.ok)}</p>` : ""}
    </div>`;
  }

  function standardHtml() {
    return `<div class="sect" style="--sc:var(--s3)">
      <h2>Redirection Standard Checklist</h2>
      <p class="sd">The doc's own three lines. Each entry on the log names the one it missed, so the one-on-ones can see the pattern.</p>
      <ul class="hgstd">${(HG.standards || []).filter(s => s.text).map(s => `<li><b>${cesc(s.label)}:</b> ${cesc(s.text)}</li>`).join("")}</ul>
    </div>`;
  }

  function formHtml(e) {
    const v = e || {};
    const id = e ? e.id : "new";
    const stds = (HG.standards || []).map(s => `<option value="${cesc(s.key)}"${(v.standard || "") === s.key ? " selected" : ""}>${cesc(s.label)}</option>`).join("");
    return `<form class="hgform" data-hgform="${cesc(id)}">
      <label>Client <input type="text" name="client" value="${cesc(v.client || "")}" maxlength="120" placeholder="Client name" ${e ? "" : "autofocus"}></label>
      <label>Policy # <input type="text" name="policy" value="${cesc(v.policy || "")}" maxlength="40" placeholder="Policy number"></label>
      <label>Rep <input type="text" name="rep" list="hgdl-rep" value="${cesc(v.rep || "")}" maxlength="60" placeholder="Who handled it"></label>
      <label>Date <input type="date" name="date" value="${cesc(v.date || HG.today || "")}"></label>
      <label>Standard missed <select name="standard"><option value="">—</option>${stds}</select></label>
      <label class="hgwide">What happened <textarea name="issue" rows="3" maxlength="1500" placeholder="What was handled wrong, assigned wrong or left out">${cesc(v.issue || "")}</textarea></label>
      <div class="rorow hgwide">
        <button type="submit" class="btn ropri">${e ? "Save" : "Add to the log"}</button>
        <button type="button" class="btn" data-hgcancel="${cesc(id)}">Cancel</button>
      </div>
    </form>`;
  }

  function rowHtml(e) {
    const s = stdOf(e.standard);
    const who = `${cesc(e.by || "")} · ${cesc(when(e.at))}${e.edits && e.edits.length ? ` · edited ${e.edits.length}× (last ${cesc(e.edits[e.edits.length - 1].by)} ${cesc(when(e.edits[e.edits.length - 1].at))})` : ""}`;
    if (hgEdit === e.id) return `<tr class="hgediting" data-row="${cesc(e.id)}"><td colspan="7">${formHtml(e)}</td></tr>`;
    return `<tr class="${e.reviewed ? "hgdone" : ""}" data-row="${cesc(e.id)}" title="${who}">
      <td class="t hgdate">${cesc(dayTxt(e.date))}</td>
      <td class="t"><b>${cesc(e.client || "(no name)")}</b>${e.policy ? `<div class="hgsub">${cesc(e.policy)}</div>` : ""}</td>
      <td class="t">${badge(e.rep)}</td>
      <td class="t hgissue">${cesc(e.issue || "")}</td>
      <td class="t">${s ? `<span class="hgstdchip hg-${cesc(s.key)}" title="${cesc(s.text)}">${cesc(s.label)}</span>` : '<span class="romute">—</span>'}</td>
      <td class="t"><label class="sccheck${e.reviewed ? " on" : ""}" title="${e.reviewed ? `Reviewed by ${cesc(e.reviewed.by)} · ${cesc(when(e.reviewed.at))}` : "Tick once it has been gone over in a one-on-one"}"><input type="checkbox" data-hgrev="${cesc(e.id)}"${e.reviewed ? " checked" : ""}> ${e.reviewed ? "Reviewed" : "Review"}</label></td>
      <td class="hgact"><button type="button" class="ghost rosmall" data-hgedit="${cesc(e.id)}">Edit</button><button type="button" class="icon-btn del-btn" data-hgrm="${cesc(e.id)}" aria-label="Take this entry off the log" title="Take this entry off the log">✕</button></td>
    </tr>`;
  }

  function logHtml() {
    const rows = filtered();
    const reps = repNames();
    const stds = (HG.standards || []);
    return `<div class="sect" style="--sc:var(--s5)">
      <h2>Audit &amp; Redirection Tracker</h2>
      <p class="sd">Newest first. Hover a line to see who logged it and when; tick <b>Review</b> once it has been gone over in a one-on-one.</p>
      <datalist id="hgdl-rep">${reps.map(n => `<option value="${cesc(n)}">`).join("")}</datalist>
      <div class="controls hgfilters">
        <button type="button" class="btn ropri" id="hgAdd"${hgAddOpen ? " disabled" : ""}>Log an account</button>
        <input type="search" id="hgQ" placeholder="Search client, policy, notes" value="${cesc(hgF.q)}" aria-label="Search">
        <select id="hgRep" aria-label="Rep"><option value="">Every rep</option>${reps.map(n => `<option value="${cesc(n)}"${n === hgF.rep ? " selected" : ""}>${cesc(n)}</option>`).join("")}</select>
        <select id="hgStd" aria-label="Standard"><option value="">Any standard</option>${stds.map(s => `<option value="${cesc(s.key)}"${s.key === hgF.std ? " selected" : ""}>${cesc(s.label)}</option>`).join("")}</select>
        <select id="hgShow" aria-label="Show"><option value="">All entries</option><option value="open"${hgF.show === "open" ? " selected" : ""}>Not yet reviewed</option><option value="done"${hgF.show === "done" ? " selected" : ""}>Reviewed</option></select>
        <span class="romute">${rows.length.toLocaleString()} shown</span>
        <span style="flex:1"></span>
        <button type="button" class="btn" id="hgCsv">Download CSV</button>
      </div>
      ${hgAddOpen ? formHtml(null) : ""}
      ${rows.length ? `<div class="scroll"><table class="rotab hgtab"><thead><tr><th class="t">Date</th><th class="t">Client · Policy #</th><th class="t">Rep</th><th class="t">What happened</th><th class="t">Standard</th><th class="t">One-on-one</th><th></th></tr></thead><tbody>${rows.map(rowHtml).join("")}</tbody></table></div>`
        : '<div class="empty">Nothing on the log matches.</div>'}
    </div>`;
  }

  function repaint() {
    if (view !== "hygiene" || !HG) return;
    const focus = document.activeElement && document.activeElement.id;
    $("#view").innerHTML = heroHtml() + `<div class="hggrid">${logHtml()}${standardHtml()}</div>`;
    if (focus && $("#" + focus)) { const el = $("#" + focus); el.focus(); if (el.setSelectionRange && el.value) el.setSelectionRange(el.value.length, el.value.length); }
    const af = $("#view .hgform input[autofocus]"); if (af) af.focus();
    wire();
  }

  async function post(body, ok) {
    try { HG = await api(body); hgMsg = ok ? { ok } : null; }
    catch (e) { hgMsg = { err: e.message }; }
    repaint();
  }

  function download() {
    const csvCell = v => /[",\n\r]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v);
    const head = ["Client Name", "Policy Number", "Rep", "Note / Description of Issue", "Date", "Standard missed", "Reviewed in one-on-one", "Logged by", "Logged at"];
    const lines = [head.map(csvCell).join(",")];
    for (const e of filtered()) lines.push([e.client, e.policy, e.rep, e.issue, e.date, (stdOf(e.standard) || {}).label || "", e.reviewed ? `${e.reviewed.by} ${e.reviewed.at.slice(0, 10)}` : "", e.by, e.at].map(v => csvCell(v == null ? "" : v)).join(","));
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob(["﻿" + lines.join("\r\n")], { type: "text/csv" }));
    a.download = `crm-hygiene-${(HG.today || "").replace(/-/g, "")}.csv`;
    document.body.appendChild(a); a.click(); a.remove();
  }

  function wire() {
    const v = $("#view");
    const add = $("#hgAdd"); if (add) add.onclick = () => { hgAddOpen = true; hgEdit = ""; hgMsg = null; repaint(); };
    const q = $("#hgQ"); if (q) q.oninput = () => { hgF.q = q.value; repaint(); };
    const r = $("#hgRep"); if (r) r.onchange = () => { hgF.rep = r.value; repaint(); };
    const sd = $("#hgStd"); if (sd) sd.onchange = () => { hgF.std = sd.value; repaint(); };
    const sh = $("#hgShow"); if (sh) sh.onchange = () => { hgF.show = sh.value; repaint(); };
    const csv = $("#hgCsv"); if (csv) csv.onclick = download;
    v.querySelectorAll("[data-hgrep]").forEach(b => b.onclick = () => { hgF.rep = hgF.rep === b.dataset.hgrep ? "" : b.dataset.hgrep; repaint(); });
    v.querySelectorAll("[data-hgform]").forEach(f => f.onsubmit = async ev => {
      ev.preventDefault();
      const d = Object.fromEntries(new FormData(f).entries());
      const id = f.dataset.hgform;
      if (id === "new") { hgAddOpen = false; await post({ op: "add", ...d }, `Logged ${d.client || d.policy}.`); }
      else { hgEdit = ""; await post({ op: "edit", id, ...d }, "Saved."); }
    });
    v.querySelectorAll("[data-hgcancel]").forEach(b => b.onclick = () => { if (b.dataset.hgcancel === "new") hgAddOpen = false; else hgEdit = ""; repaint(); });
    v.querySelectorAll("[data-hgedit]").forEach(b => b.onclick = () => { hgEdit = b.dataset.hgedit; hgAddOpen = false; hgMsg = null; repaint(); });
    v.querySelectorAll("[data-hgrev]").forEach(c => c.onchange = () => post({ op: "review", id: c.dataset.hgrev, on: c.checked }));
    v.querySelectorAll("[data-hgrm]").forEach(b => b.onclick = () => {
      const e = (HG.entries || []).find(x => x.id === b.dataset.hgrm);
      if (!e || !confirm(`Take ${e.client || e.policy || "this entry"} off the log? This cannot be undone.`)) return;
      post({ op: "remove", id: e.id }, "Removed.");
    });
  }

  window.hygienePaint = async function hygienePaint() {
    $("#topsub").textContent = "accounts handled wrong, assigned wrong or left without notes -- for the one-on-ones";
    if (!HG) $("#view").innerHTML = '<div class="empty">Loading…</div>';
    try { HG = await api(); } catch (_) { HG = null; }
    if (!HG) { $("#view").innerHTML = '<div class="empty">The CRM Hygiene log is only open to the ops team.</div>'; return; }
    repaint();
  };

  const css = document.createElement("style");
  css.textContent = `
.hgtiles { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 12px 0 10px; }
@media (max-width: 900px) { .hgtiles { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.hgtile { background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.18); border-top: 5px solid var(--th); border-radius: 12px; padding: 10px 12px 12px; }
html[data-look="mesa"] .hgtile { background: rgba(255,255,255,.1); }
.hgtile span { display: block; text-transform: uppercase; letter-spacing: .07em; font-size: 11px; font-weight: 700; opacity: .8; }
.hgtile strong { font-family: var(--display); font-weight: var(--dw, 700); font-size: 28px; }
.hgtile small { display: block; font-size: 12px; opacity: .85; }
.hgreps { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.hgrep { font: inherit; display: inline-flex; align-items: center; gap: 6px; padding: 3px 8px; border-radius: 999px; border: 1px solid rgba(255,255,255,.3); background: rgba(255,255,255,.08); color: inherit; cursor: pointer; }
.hgrep.on { background: rgba(255,255,255,.22); border-color: #fff; }
.hggrid { display: grid; grid-template-columns: minmax(0, 3fr) minmax(260px, 1fr); gap: 16px; align-items: start; }
@media (max-width: 1100px) { .hggrid { grid-template-columns: 1fr; } }
.hgstd { margin: 6px 0 0; padding-left: 18px; line-height: 1.5; } .hgstd li { margin-bottom: 8px; }
.hgfilters { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 10px; }
.hgfilters input[type=search], .hgfilters select { font: inherit; font-size: 14px; padding: 7px 10px; border: 1px solid var(--border-strong); border-radius: 10px; background: var(--surface); color: var(--text-primary); }
.hgfilters input[type=search] { min-width: 220px; }
.hgform { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; margin: 6px 0 14px; padding: 12px; border: 1px dashed var(--border-strong); border-radius: 12px; background: color-mix(in oklab, var(--s5) 7%, var(--surface)); }
.hgform label { display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 700; color: var(--text-secondary); }
.hgform input, .hgform select, .hgform textarea { font: inherit; font-size: 14px; padding: 7px 9px; border: 1px solid var(--border-strong); border-radius: 10px; background: var(--surface); color: var(--text-primary); }
.hgform textarea { resize: vertical; min-height: 64px; }
.hgform .hgwide { grid-column: 1 / -1; }
.hgtab td { vertical-align: top; }
.hgtab tr.hgdone td { background: color-mix(in oklab, var(--good) 9%, transparent); }
.hgtab tr.hgediting td { background: color-mix(in oklab, var(--s5) 8%, transparent); }
.hgdate { white-space: nowrap; }
.hgsub { font-size: 12px; color: var(--text-secondary); }
.hgissue { min-width: 200px; max-width: 460px; white-space: pre-wrap; line-height: 1.45; }
.hgtab { width: 100%; table-layout: auto; }
.hgstdchip { display: inline-block; font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 999px; border: 1px solid var(--border-strong); line-height: 1.3; }
.hgstdchip.hg-check { background: color-mix(in oklab, var(--s3) 18%, transparent); }
.hgstdchip.hg-own { background: color-mix(in oklab, var(--s5) 18%, transparent); }
.hgstdchip.hg-cal { background: color-mix(in oklab, var(--s4) 18%, transparent); }
.hgact { white-space: nowrap; } .hgact .ghost { margin-right: 4px; }
`;
  document.head.appendChild(css);
})();
