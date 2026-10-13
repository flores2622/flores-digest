/* Operations Center > Minimums & Goal (Frank, 2026-10-13: "give the ops team a
   tab with everyone's and the team goal"). Every producer's minimum -- the first
   tier of their commission schedule, a requirement rather than a goal -- and
   the team's monthly goal, for the folio, from the Sales sheet. Shown only to
   the people /api/folio-goals answers (site/worker.js, staff.json's
   `folio_goals`: the ops team); for anyone else the page never enters the menu
   or the search. The bars are the Digest card's own (folioGoalsHtml in
   index.html); under them a table per producer. Uses the board's helpers
   ($, cesc, pbadge, DOT, money, opsShow, folioStartFor, fmtShortDate), so it
   loads after index.html's main script. */
(function () {
  let FG = null;          // the last /api/folio-goals answer
  let fgEnd = "";         // the folio picked ("" = the current one)

  async function load(end) {
    const r = await fetch(`/api/folio-goals${end ? "/" + end : ""}`, { cache: "no-store" });
    if (!r.ok) throw new Error(`could not reach the board (${r.status})`);
    return r.json();
  }

  window.FG_READY = (async function fgInit() {
    try { FG = await load(""); } catch (_) { return false; }
    if (!FG.ops) return false;   // everyone reads the figures (the Digest's card); the page is the ops team's
    opsShow("goals", "Minimums & Goal", "every producer's minimum and the team goal");
    return true;
  })();

  const sum = rs => rs.reduce((a, r) => a + (+r.premium || 0), 0);
  const first = n => String(n || "").split(" ")[0];
  const badge = n => DOT[n] ? pbadge(DOT[n], first(n)) : `<b>${cesc(first(n) || "—")}</b>`;

  function tableHtml(asof, done, all) {
    const left = all - done;
    const sheet = (FG.sheet || []).filter(r => r.day <= asof);
    const team = sum(sheet);
    const unitOf = n => (FG.units || []).find(u => u.members.includes(n));
    const names = [];
    for (const u of FG.units || []) for (const m of u.members) if (!names.includes(m)) names.push(m);
    for (const r of sheet) if (r.producer && !names.includes(r.producer)) names.push(r.producer);
    const rows = names.map(n => {
      const u = unitOf(n), mine = sheet.filter(r => r.producer === n), sold = sum(mine);
      if (!u) return `<tr><td>${badge(n)}</td><td class="num">${money(sold)}</td><td class="num">${mine.length}</td><td class="num">—</td><td>no minimum</td><td class="num">—</td><td class="num">—</td><td>—</td><td class="num">${team ? Math.round(100 * sold / team) : 0}%</td></tr>`;
      const urows = (u.rows || []).filter(r => r.day <= asof), have = sum(urows), own = sum(urows.filter(r => r.producer === n));
      const min = u.tiers[0].min, need = Math.max(0, min - have), due = min * done / all;
      const tier = have >= min || have >= due ? "tg" : have >= due * 0.9 ? "ty" : "tr";
      const next = u.tiers.find(t => t.min > have);
      const shared = u.members.length > 1;
      return `<tr><td>${badge(n)}</td><td class="num">${money(sold)}</td><td class="num">${mine.length}</td>
        <td class="num">${money(own)}${shared ? `<div class="sd" style="font-size:11px">${cesc(u.label)}: ${money(have)}</div>` : ""}</td>
        <td>${money(min)}${shared ? " team" : ""} <span class="sd">(${cesc(u.tiers[0].name)})</span></td>
        <td class="num"><b class="${tier}">${Math.round(100 * have / min)}%</b></td>
        <td class="num">${need ? money(need) : `<b class="tg">Met</b>`}${need && left ? `<div class="sd" style="font-size:11px">${money(need / left)} a day</div>` : ""}</td>
        <td>${need ? (u.tiers[1] ? `then ${cesc(u.tiers[1].name)} at ${money(u.tiers[1].min)}` : "—") : next ? `${cesc(next.name)} at ${money(next.min)} · ${money(next.min - have)} to go` : "at the top tier"}</td>
        <td class="num">${team ? Math.round(100 * sold / team) : 0}%</td></tr>`;
    }).join("");
    return `<div class="sect"><h2>By producer</h2>
      <p class="sd">Sold is everything on the Sales sheet. "Toward the minimum" leaves out life and business, as the Commission page does; Sarahi and Coral share one team minimum. Share is of the team's total.</p>
      <div class="scroll"><table class="msgt"><thead><tr><th>Producer</th><th class="num">Sold</th><th class="num">Sales</th><th class="num">Toward the minimum</th><th>Minimum</th><th class="num">Of the minimum</th><th class="num">To go</th><th>Next tier</th><th class="num">Share of team</th></tr></thead>
      <tbody>${rows}<tr class="tot"><td><b>Team</b></td><td class="num">${money(team)}</td><td class="num">${sheet.length}</td><td></td><td></td><td></td><td></td><td></td><td class="num">100%</td></tr></tbody></table></div></div>`;
  }

  window.folioGoalsPaint = async function () {
    const v = $("#view");
    if (!FG || (fgEnd && FG.folio_end !== fgEnd)) {
      try { FG = await load(fgEnd); } catch (e) { v.innerHTML = `<div class="sect"><p class="sd">${cesc(e.message)}</p></div>`; return; }
    }
    const end = FG.folio_end, start = FG.folio_start || folioStartFor(end) || end;
    const asof = FG.today < end ? FG.today : end;
    const biz = pbizDays(start, end), all = biz.length || 1, done = Math.max(1, biz.filter(x => x <= asof).length);
    const S = { upto: d => sum((FG.sheet || []).filter(r => r.day <= d)) };
    const opts = (FG.folios || [end]).slice().reverse().map(e => `<option value="${e}"${e === end ? " selected" : ""}>${fmtShortDate(folioStartFor(e) || e)} – ${fmtShortDate(e)}${e >= FG.today ? " (this folio)" : ""}</option>`).join("");
    v.innerHTML = `<div class="sect mgoal" style="cursor:default">
        <div class="mgtop"><h2>Minimums &amp; the team goal</h2>
          <label class="sd">Folio <select id="fgfolio">${opts}</select></label></div>
        <p class="sd" style="margin:6px 0 0">${asof === end ? "The folio as it closed." : `As of ${fmtShortDate(asof)}, ${done} of ${all} business days in.`} A minimum is the first tier of the producer's commission schedule: what they have to reach, not a goal. The team goal is everyone on the Sales sheet.</p>
        ${folioGoalsHtml(S, FG.units || [], end, asof, "", true)}</div>
      ${tableHtml(asof, done, all)}`;
    const sel = $("#fgfolio");
    if (sel) sel.onchange = () => { fgEnd = sel.value; FG = null; paint(); };
  };
})();
