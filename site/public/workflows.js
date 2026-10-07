/* Workflows -- what AgencyZoom's automations run today, read back from the
   leads (Frank, 2026-10-07: "how do we start building our own workflows? or
   display what we currently have so we can adjust or change as needed").
   Sales Center > Workflows, shown only to whoever /api/crm answers (Frank
   alone for now). The report is az_automations.py's (R2 crm/automations.json,
   through /api/crm/automations): every text rule, drip email, repeated task
   and the Smart-Cycle moves, each with its wording blanked of names, when it
   fires, who it hits and what came back. Frank marks each keep / change /
   drop with a note; the marks are the brief for the rules Pantheon will run
   itself (CRM.md, Workflows). Loads after tasks.js: it waits on CRM_READY. */
(function () {
  const TABS = [["texts", "Texts"], ["emails", "Emails"], ["tasks", "Tasks"], ["cycles", "Smart-Cycle"]];
  let D = null, wfTab = "texts", wfBusy = false, wfMsg = null, wfOpen = {};
  try { const w = JSON.parse(sessionStorage.getItem("workflows-where") || "{}"); if (TABS.some(([k]) => k === w.tab)) wfTab = w.tab; } catch (_) {}
  const saveWhere = () => { try { sessionStorage.setItem("workflows-where", JSON.stringify({ tab: wfTab })); } catch (_) {} };

  async function api(path, body) {
    const r = await fetch("/api/crm/" + path, body ? { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) } : { cache: "no-store" });
    let j = null; try { j = await r.json(); } catch (_) {}
    if (!r.ok) { const e = new Error((j && j.error) || `HTTP ${r.status}`); e.status = r.status; throw e; }
    return j;
  }
  window.WORKFLOWS_READY = (async function () {
    const ok = await (window.CRM_READY || Promise.resolve(false));
    if (!ok) return false;
    if (!CENTERS.salescenter.some(([k]) => k === "workflows")) CENTERS.salescenter.push(["workflows", "Workflows"]);
    SEARCH_PAGES.push(["Workflows", "Sales Center · what AgencyZoom's automations run today, and what to keep", "workflows"]);
    paintCenterBar();
    return true;
  })();

  const n = (x) => (x || 0).toLocaleString("en-US");
  const pct = (a, b) => (b ? Math.round(100 * a / b) : 0);
  const hour = (h) => (h == null ? "" : `${h % 12 || 12} ${h < 12 ? "AM" : "PM"}`);
  const stageName = (s) => (s || "").split(" | ").pop() || s;
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
    const open = wfOpen[r.key];
    return `<div class="wfmark">
      ${["keep", "change", "drop"].map((k) => `<button type="button" class="wfmk ${k}${m.mark === k ? " on" : ""}" data-mark="${k}" data-key="${cesc(r.key)}"${wfBusy ? " disabled" : ""}>${k[0].toUpperCase() + k.slice(1)}</button>`).join("")}
      <button type="button" class="ghost tksmall" data-note="${cesc(r.key)}">${m.note ? "Edit note" : "Add a note"}</button>
      ${m.mark || m.note ? `<small class="lsmute">${m.by ? cesc(m.by.split(" ")[0]) : ""} ${m.at ? cesc(m.at.slice(0, 10)) : ""}</small>` : ""}
      ${m.note && !open ? `<div class="wfnote">${cesc(m.note)}</div>` : ""}
      ${open ? `<form class="lsform" data-notefor="${cesc(r.key)}"><input type="text" class="lsin lswide" name="note" value="${cesc(m.note || "")}" placeholder="What should change, or why it goes" maxlength="500" autofocus><button type="submit" class="btn tkpri">Save</button><button type="button" class="btn" data-cancelnote="1">Cancel</button></form>` : ""}
    </div>`;
  }
  function ruleCard(r) {
    const m = (D.marks || {})[r.key] || {};
    const came = r.kind === "text" ? `${n(r.replied)} wrote back within 2 days (${r.replied_pct}%)${r.opted_out ? ` · <span class="wfbad">${n(r.opted_out)} opted out</span>` : ""}`
      : r.kind === "email" ? `${n(r.opened)} opened (${pct(r.opened, r.fired)}%) · ${n(r.replied)} wrote back within 3 days${r.bounced ? ` · <span class="wfbad">${n(r.bounced)} bounced</span>` : ""}`
      : "";
    return `<li class="wfcard${m.mark ? " wf-" + m.mark : ""}" id="wf-${cesc(r.key)}">
      <div class="wfhead"><strong>${cesc(r.title)}</strong><span class="wfcount">${n(r.fired)} time${r.fired === 1 ? "" : "s"} · ${n(r.leads)} lead${r.leads === 1 ? "" : "s"}</span>${r.first ? `<small class="lsmute">${cesc(r.first)} to ${cesc(r.last)}</small>` : ""}</div>
      ${r.template ? `<blockquote class="wftpl">${cesc(r.template)}${r.variants > 1 ? ` <small class="lsmute">(${r.variants} wordings; the commonest shown)</small>` : ""}</blockquote>` : ""}
      <p class="wfwhen">${whenLine(r)}</p>
      <div class="wfgrid">
        <div>${chips(r.sources, "Sources")}${chips(r.stages, "Stage when it fired")}${chips(r.by, r.kind === "task" ? "For" : "Signed by")}</div>
        <div>${r.days_in_stage && r.days_in_stage.median != null ? `<div class="wflab">Days in the stage when it fired</div>${hist(r.days_in_stage)}` : ""}</div>
      </div>
      ${came ? `<p class="wfcame">${came}</p>` : ""}
      ${markHtml(r)}
    </li>`;
  }
  function cyclesHtml(R) {
    const park = R.cycles.find((c) => c.key === "cycle:park"), back = R.cycles.find((c) => c.key === "cycle:back"), dead = R.cycles.find((c) => c.key === "cycle:dead");
    const auto = (c) => (c.by || []).filter((b) => !/^(Crystal|Lorena|Mike|Coral|Sarahi|Amanda|Debbie|Frank|Francisco|Veronica)/.test(b.name)).reduce((a, b) => a + b.n, 0);
    const line = (c, verb) => c && c.fired ? `<li class="wfcard"><div class="wfhead"><strong>${cesc(c.title)}</strong><span class="wfcount">${n(c.fired)} leads</span></div>
      <p class="wfwhen">${verb} about <b>${c.days_in_stage.median} days</b> after the lead got to where it was; ${n(auto(c))} of ${n(c.fired)} by the automation, the rest by a person.</p>
      <div class="wfgrid"><div>${chips(c.stages, c.key === "cycle:back" ? "Came back into" : "From")}${chips(c.sources, "Sources")}${chips(c.by, "By")}</div><div><div class="wflab">Days there first</div>${hist(c.days_in_stage)}</div></div>${markHtml(c)}</li>` : "";
    const parked = Object.entries(R.parked_days || {}).map(([k, v]) => `<span class="wfchip">${cesc(stageName(k))} <small>${v.median} days parked · ${n(v.n)}</small></span>`).join("");
    const trans = (R.transitions || []).slice(0, 20).map((t) => `<tr><td>${cesc(stageName(t.from))}</td><td>→</td><td>${cesc(stageName(t.to))}</td><td>${t.who === "automation" ? "<span class=\"wfauto\">automation</span>" : "a person"}</td><td class="num">${n(t.n)}</td></tr>`).join("");
    return `<ul class="wflist">${line(park, "Parked")}${line(back, "Brought back")}${line(dead, "Deaded")}</ul>
      ${parked ? `<div class="wfchips"><span class="wflab">How long a lead stays parked before each return</span>${parked}</div>` : ""}
      <h3 class="wfh3">Every stage move in the period</h3>
      <div class="scroll"><table class="tktab wftrans"><thead><tr><th>From</th><th></th><th>To</th><th>Who</th><th class="num">Leads</th></tr></thead><tbody>${trans}</tbody></table></div>`;
  }

  function repaint() {
    const v = $("#view");
    const R = D && D.report;
    const counts = R ? { texts: R.texts.length, emails: R.emails.length, tasks: R.tasks.length, cycles: R.cycles.filter((c) => c.fired).length } : {};
    const tabs = TABS.map(([k, l]) => `<button type="button" class="tktile${k === wfTab ? " on" : ""}" data-wftab="${k}" style="--th:${{ texts: "var(--accent)", emails: "var(--s4)", tasks: "var(--s3)", cycles: "var(--good)" }[k]}"><span>${l}</span><strong>${counts[k] == null ? "…" : counts[k]}</strong></button>`).join("");
    const marked = Object.values((D && D.marks) || {});
    const tally = marked.length ? `<span class="lsbadge lsok">${marked.filter((m) => m.mark === "keep").length} keep · ${marked.filter((m) => m.mark === "change").length} change · ${marked.filter((m) => m.mark === "drop").length} drop</span>` : "";
    let body;
    if (!R) body = `<div class="empty">The read has not run yet. It reads the last 90 days' active leads' notes from AgencyZoom and rebuilds the rules from what they sent; it runs from the nightly's environment in the evening.</div>`;
    else if (wfTab === "cycles") body = cyclesHtml(R);
    else {
      const list = R[wfTab] || [];
      body = list.length ? `<ul class="wflist">${list.map(ruleCard).join("")}</ul>` : `<div class="empty">Nothing of this kind in the last ${R.days} days.</div>`;
    }
    v.innerHTML = `<section class="tkpage wfpage">
      <div class="tkhead"><div class="tktiles">${tabs}</div>${tally}</div>
      ${wfMsg ? `<p class="tkmsg ${wfMsg.err ? "bad" : "good"}">${cesc(wfMsg.err || wfMsg.ok)}</p>` : ""}
      <p class="lsintro">What AgencyZoom's automations actually do, read back from the leads${R ? ` -- the last ${R.days} days, ${n(R.leads_read)} leads' notes, as of ${cesc(R.built)}` : ""}. AgencyZoom does not hand out its rules, so each one is rebuilt from what it sent: its wording with names blanked, when it fires, who it hits and what came back. Mark each <b>Keep</b>, <b>Change</b> or <b>Drop</b> and say why; that is the brief for the rules Pantheon runs itself.</p>
      ${body}
      <p class="tkfoot">Pantheon's own CRM. Nothing here changes AgencyZoom. Texts carry the rule that sent them; emails are known by their template subject; a task counts when the same wording went to five or more leads.</p>
    </section>`;
    const f = v.querySelector(".lsform input[autofocus]"); if (f) f.focus();
  }
  async function refresh(msg) {
    wfMsg = msg || null;
    try { D = await api("automations"); } catch (e) { $("#view").innerHTML = `<div class="empty">${cesc(e.message)}</div>`; return; }
    repaint();
  }
  async function act(fn, ok) {
    if (wfBusy) return;
    wfBusy = true;
    try { const r = await fn(); if (r && r.marks) D.marks = r.marks; wfOpen = {}; wfMsg = ok ? { ok } : null; }
    catch (e) { wfMsg = { err: e.message }; }
    wfBusy = false; repaint();
  }
  function onClick(e) {
    const t = e.target.closest("[data-wftab],[data-mark],[data-note],[data-cancelnote]");
    if (!t || !$("#view").contains(t) || !$("#view").querySelector(".wfpage")) return;
    if (t.dataset.wftab) { wfTab = t.dataset.wftab; wfOpen = {}; saveWhere(); repaint(); return; }
    if (t.dataset.mark) {
      const key = t.dataset.key, cur = (D.marks || {})[key] || {};
      const mark = cur.mark === t.dataset.mark ? null : t.dataset.mark;   // the same button again clears it
      act(() => api("automations/mark", { key, mark, note: cur.note || "" }), mark ? "Marked." : "Cleared."); return;
    }
    if (t.dataset.note) { wfOpen = { [t.dataset.note]: true }; repaint(); return; }
    if (t.dataset.cancelnote) { wfOpen = {}; repaint(); return; }
  }
  function onSubmit(e) {
    const form = e.target.closest("form[data-notefor]");
    if (!form || !$("#view").contains(form)) return;
    e.preventDefault();
    const key = form.dataset.notefor, cur = (D.marks || {})[key] || {};
    act(() => api("automations/mark", { key, mark: cur.mark || null, note: String(new FormData(form).get("note") || "").trim() }), "Saved.");
  }
  document.addEventListener("click", onClick);
  document.addEventListener("submit", onSubmit);

  window.workflowsPaint = async function workflowsPaint() {
    $("#topsub").textContent = "what AgencyZoom's automations run today";
    $("#view").innerHTML = '<div class="empty">Loading…</div>';
    wfMsg = null; wfOpen = {};
    await refresh();
  };

  const css = document.createElement("style");
  css.textContent = `
.wflist { list-style: none; margin: 0; padding: 0; }
.wfcard { border: 1px solid var(--border-strong); border-left: 6px solid var(--border-strong); border-radius: 12px; padding: 12px 14px; margin-bottom: 12px; background: var(--surface); }
.wfcard.wf-keep { border-left-color: var(--good); } .wfcard.wf-change { border-left-color: var(--s4, #d9a21b); } .wfcard.wf-drop { border-left-color: var(--bad); }
.wfhead { display: flex; flex-wrap: wrap; align-items: baseline; gap: 10px; } .wfhead strong { font-size: 16px; }
.wfcount { font-weight: 700; color: var(--text-secondary); }
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
.wfh3 { margin: 16px 0 6px; font-size: 15px; } .wftrans td.num, .wftrans th.num { text-align: right; }
@media (max-width: 900px) { .wfgrid { grid-template-columns: 1fr; } }
`;
  document.head.appendChild(css);
})();
