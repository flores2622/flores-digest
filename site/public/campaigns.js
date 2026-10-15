/* Operations Center > Campaigns (Frank, 2026-10-15: "after receiving the
   results of what they did ill decide who will be getting the highest load
   of these leads ... create me a tracker for it"; "just me for now"). How
   each producer worked a batch of campaign leads -- the Rate Decrease
   Campaign's 10 each (5 reassigned to them in AgencyZoom, 5 they had to
   create) -- from the board's own day documents and checkpoints
   (site/campaigns.js, /api/campaigns). Shown only to staff.json's
   `campaigns` (Frank); for anyone else the page never enters the menu or the
   search. Uses the board's helpers ($, cesc, pbadge, DOT, money, opsShow,
   fmtShortDate, openLeadCard, paint), so it loads after index.html's main
   script. */
(function () {
  let CP = null;           // the last /api/campaigns/<key> answer
  let cpKey = "";          // the campaign picked ("" = the newest)
  let cpWho = "";          // producer filter on the lead list
  let cpKind = "";         // "", "reassign", "create"

  async function load(key) {
    const r = await fetch(`/api/campaigns${key ? "/" + key : ""}`, { cache: "no-store" });
    const out = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(out.error || `could not reach the board (${r.status})`);
    return out;
  }

  window.CAMPAIGNS_READY = (async function cpInit() {
    let list;
    try { list = await load(""); } catch (_) { return false; }
    if (!(list.campaigns || []).length) return false;
    opsShow("campaigns", "Campaigns", "how each producer worked their campaign leads");
    return true;
  })();

  const first = n => String(n || "").split(" ")[0];
  const badge = n => DOT[n] ? pbadge(DOT[n], first(n)) : `<b>${cesc(first(n) || "—")}</b>`;
  const day = d => d ? fmtShortDate(d) : "—";
  const mins = s => s ? (s >= 60 ? `${Math.round(s / 60)}m` : `${s}s`) : "—";
  const STATUS = {
    sold: ["Sold", "tg"], quoted: ["Quoted", "tg"], reached: ["Reached", "ty"],
    dialed: ["Dialed", "ty"], created: ["Created, not dialed", "ty"], untouched: ["Not touched", "tr"],
  };
  const CAT_LABEL = { worked: "Worked", reached: "Reached", quoted: "Quoted", premium_quoted: "Premium quoted", sold: "Sold", created: "Created" };

  function boardHtml() {
    const b = CP.board || [];
    const top = b[0] && b[0].points ? b[0].points : 0;
    const rows = b.map((x, i) => `<tr>
      <td class="num">${x.points && x.points === top ? "🏆" : i + 1}</td>
      <td>${badge(x.producer)}</td>
      <td class="num"><b>${x.points}</b></td>
      <td class="num">${x.worked} / ${x.leads}</td>
      <td class="num">${x.dials}</td>
      <td class="num">${x.reached}</td>
      <td class="num">${mins(x.talk)}</td>
      <td class="num">${x.quoted}</td>
      <td class="num">${money(x.premium_quoted)}</td>
      <td class="num">${x.sold ? `<b class="tg">${x.sold}</b>` : 0}</td>
      <td class="num">${x.to_create ? `<span class="${x.created === x.to_create ? "tg" : x.created ? "ty" : "tr"}">${x.created} / ${x.to_create}</span>` : "—"}</td>
      <td>${day(x.first_day)}</td></tr>`).join("");
    return `<div class="sect"><h2>Scoreboard</h2>
      <p class="sd">Points are the leaderboard's 5-4-3-2-1 in each of ${(CP.categories || []).map(c => CAT_LABEL[c] || c).join(", ")} (a tie shares the higher points; nothing for zero). A producer is credited only with their own work on their own campaign leads.</p>
      <div class="scroll"><table class="msgt"><thead><tr><th></th><th>Producer</th><th class="num">Points</th><th class="num">Worked</th><th class="num">Dials</th><th class="num">Reached</th><th class="num">Talk</th><th class="num">Quoted</th><th class="num">Premium quoted</th><th class="num">Sold</th><th class="num">Created</th><th>First worked</th></tr></thead>
      <tbody>${rows}</tbody></table></div></div>`;
  }

  function leadsHtml() {
    const names = [...new Set((CP.leads || []).map(l => l.producer))];
    const ls = (CP.leads || []).filter(l => (!cpWho || l.producer === cpWho) && (!cpKind || l.kind === cpKind));
    const rows = ls.map((l, i) => {
      const [label, cls] = STATUS[l.status] || [l.status, ""];
      const id = (l.lead_ids || [])[0] || "";
      const kind = l.kind === "create"
        ? (l.created ? `Create · <span class="tg" title="Created ${cesc(l.created.day)}${l.created.name ? " as " + cesc(l.created.name) : ""}">made ${day(l.created.day)}</span>`
          : (l.lead_ids || []).length ? `Create · <span class="tg">found</span>` : `Create · <span class="tr">not yet</span>`)
        : `Reassign${l.from ? ` <span class="sd">from ${cesc(l.from)}</span>` : ""}`;
      const q = (l.quotes || []).map(x => `${x.line} ${money(x.premium)} (${x.date})`).join("; ");
      return `<tr>
        <td>${badge(l.producer)}</td>
        <td>${id ? `<a href="#" class="cplead" data-i="${i}">${cesc(l.name)}</a>` : cesc(l.name)}<div class="sd" style="font-size:11px" title="${cesc(q)}">${cesc(q.length > 60 ? q.slice(0, 60) + "…" : q)}</div></td>
        <td>${kind}</td>
        <td><b class="${cls}">${label}</b>${(l.others || []).length ? `<div class="sd" style="font-size:11px">also worked by ${cesc(l.others.map(first).join(", "))}</div>` : ""}</td>
        <td class="num">${l.dials || "—"}</td>
        <td class="num">${l.reached ? mins(l.reached_secs) : "—"}</td>
        <td class="num">${l.quoted ? money(l.quoted) : l.status === "quoted" || l.status === "sold" ? "yes" : "—"}</td>
        <td>${l.sold ? `<b class="tg">${day(l.sold_day)}</b>` : "—"}</td>
        <td>${day(l.last_day)}</td>
        <td class="sd" style="max-width:340px">${cesc(l.summary || "")}</td></tr>`;
    }).join("");
    const opt = (v, t, cur) => `<option value="${cesc(v)}"${v === cur ? " selected" : ""}>${cesc(t)}</option>`;
    return `<div class="sect"><div class="mgtop"><h2>The leads</h2>
        <span><select id="cpwho">${opt("", "Every producer", cpWho)}${names.map(n => opt(n, n, cpWho)).join("")}</select>
        <select id="cpkind">${opt("", "Reassigned and created", cpKind)}${opt("reassign", "Reassigned", cpKind)}${opt("create", "To create", cpKind)}</select></span></div>
      <p class="sd">A name with a lead behind it opens its coaching card. Reached is talk time on the calls that counted as contacts; the last column is Apollo's summary of the latest one.</p>
      <div class="scroll"><table class="msgt"><thead><tr><th>Producer</th><th>Lead</th><th>Kind</th><th>Where it stands</th><th class="num">Dials</th><th class="num">Reached</th><th class="num">Quoted</th><th>Sold</th><th>Last worked</th><th>Latest call</th></tr></thead>
      <tbody>${rows || `<tr><td colspan="10" class="sd">No leads match.</td></tr>`}</tbody></table></div></div>`;
  }

  window.campaignsPaint = async function () {
    const v = $("#view");
    if (!CP || (cpKey && CP.key !== cpKey)) {
      try {
        if (!cpKey) { const list = await load(""); cpKey = ((list.campaigns || [])[0] || {}).key || ""; }
        CP = cpKey ? await load(cpKey) : null;
      } catch (e) { v.innerHTML = `<div class="sect"><p class="sd">${cesc(e.message)}</p></div>`; return; }
    }
    if (!CP) { v.innerHTML = `<div class="sect"><p class="sd">No campaigns yet.</p></div>`; return; }
    const pick = (CP.campaigns || []).length > 1
      ? `<select id="cppick">${CP.campaigns.map(c => `<option value="${cesc(c.key)}"${c.key === CP.key ? " selected" : ""}>${cesc(c.title)}</option>`).join("")}</select>` : "";
    const asof = CP.as_of ? `${CP.as_of.src === "checkpoint" ? "Today's last checkpoint" : "Published"} ${fmtShortDate(CP.as_of.day)}` : "nothing read yet";
    v.innerHTML = `<div class="sect"><div class="mgtop"><h2>${cesc(CP.title)}</h2>${pick}</div>
        <p class="sd" style="margin:6px 0 0">Handed out ${fmtShortDate(CP.start)}${CP.source ? ` from ${cesc(CP.source)}` : ""} · ${(CP.leads || []).length} leads · as of ${asof} (the board's hourly checkpoints; today's last hour shows after the next one).</p></div>
      ${boardHtml()}${leadsHtml()}`;
    const s = $("#cppick"); if (s) s.onchange = () => { cpKey = s.value; CP = null; paint(); };
    const w = $("#cpwho"); if (w) w.onchange = () => { cpWho = w.value; paint(); };
    const k = $("#cpkind"); if (k) k.onchange = () => { cpKind = k.value; paint(); };
    const shown = (CP.leads || []).filter(l => (!cpWho || l.producer === cpWho) && (!cpKind || l.kind === cpKind));
    for (const a of v.querySelectorAll("a.cplead")) a.onclick = ev => {
      ev.preventDefault();
      const l = shown[+a.dataset.i];
      if (l) openLeadCard({ id: (l.lead_ids || [])[0], l: l.name });
    };
  };
})();
