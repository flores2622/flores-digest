/* The new-business rotation (Frank, 2026-10-02: "fix the rotation sheet ...
   its how we rotate new business walkin and call ins ... i want this to be
   part of the board"). Sales Center > Rotation, shown only to the people
   /api/rotation answers (site/rotation.js: Debbie, Crystal and the ops team);
   for anyone else the page never enters the menu or the search.

   Three rotations side by side -- Personal lines, Life, Mexico policies --
   each with who is up, the order after them, and the buttons Debbie uses on
   a walk-in or call-in: give it to whoever is up, mark them out or busy
   (their turn passes), or give it out of turn to the person the client
   asked for (the turn stays). Under them, the folio's log. Managers change
   an order or who is next. Uses the board's own helpers ($, cesc, pbadge,
   DOT, FOLIO_CLOSE_DATES, folioStartFor, azTodayDate, isoDate), so it loads
   after index.html's main script. */
(function () {
  const ROT_KEYS = ["personal", "life", "mexico"];
  const ROT_HUE = { personal: "var(--s3)", life: "var(--s5)", mexico: "var(--s4)" };
  const ROT_SUB = { personal: "Auto, home, renters and the rest of personal lines",
    life: "Life insurance", mexico: "Policies for Mexico" };
  const KIND = { in: "Given", skip: "Out", busy: "Covered", out: "Out of turn" };
  let ROT = null;                 // the last /api/rotation answer
  let rotFolio = "";              // a FOLIO_CLOSE_DATES entry; "" = the current folio
  let rotEdit = "";               // which rotation's order is being changed
  let rotDraft = null;            // {order, next} while editing
  let rotMsg = {};                // per rotation: {ok|err: text}
  let rotBusy = false;

  const first = n => String(n || "").split(" ")[0];
  const badge = n => DOT[n] ? pbadge(DOT[n], first(n)) : `<b>${cesc(first(n))}</b>`;
  const today = () => isoDate(azTodayDate());

  async function rotLoad() {
    const r = await fetch("/api/rotation", { cache: "no-store" });
    if (!r.ok) return null;
    ROT = await r.json();
    return ROT;
  }

  // Unhide the page for whoever the Worker lets see it. ROT_READY says
  // whether it did, so a refresh on this page can reopen it (index.html init).
  window.ROT_READY = (async function rotInit() {
    try { if (!(await rotLoad())) return false; } catch (_) { return false; }
    if (!CENTERS.salescenter.some(([k]) => k === "rotation")) CENTERS.salescenter.push(["rotation", "Rotation"]);
    SEARCH_PAGES.push(["Rotation", "Sales Center · who gets the next walk-in or call-in", "rotation"]);
    paintCenterBar();
    return true;
  })();

  function folioOf() {
    const end = rotFolio || folioEndFor(today()) || FOLIO_CLOSE_DATES[FOLIO_CLOSE_DATES.length - 1];
    return { end, start: folioStartFor(end) || "0000-00-00" };
  }

  // The order from whoever is up: one full lap, with anyone who covered
  // for a busy person marked -- the rotation passes over them once.
  function upcoming(list) {
    const o = list.order, i = Math.max(0, o.indexOf(list.next)), owed = list.owed || [];
    return o.map((_, k) => { const p = o[(i + k) % o.length]; return { p, pass: k > 0 && owed.includes(p) }; });
  }
  // Who takes it when whoever is up is busy (the Worker's coverFor).
  function coverFor(list) {
    const o = list.order, owed = list.owed || [];
    let n = list.next;
    for (let k = 0; k < o.length; k++) {
      n = o[(o.indexOf(n) + 1) % o.length];
      if (n === list.next) return "";
      if (!owed.includes(n)) return n;
    }
    return "";
  }

  function cardHtml(key) {
    const list = ROT.lists[key];
    const msg = rotMsg[key] || {};
    const up = upcoming(list), cover = coverFor(list);
    const afterUp = (up.slice(1).find(x => !x.pass) || {}).p || "";
    if (rotEdit === key) return editHtml(key);
    const others = list.order.filter(p => p !== list.next);
    const how = (ROT.how || []).map(h => `<option value="${cesc(h)}">${cesc(h[0].toUpperCase() + h.slice(1))}</option>`).join("");
    return `<div class="rocard" style="--rh:${ROT_HUE[key]}" data-rot="${key}">
      <div class="rohead"><h3>${cesc(list.label)}</h3>${ROT.can_edit ? `<button type="button" class="ghost rosmall" data-roedit="${key}">Change order</button>` : ""}</div>
      <p class="rosub">${cesc(ROT_SUB[key] || "")}</p>
      <div class="roup"><span>Up next</span>${list.next ? `<strong style="--pc:${DOT[list.next] || "var(--text-primary)"}">${cesc(first(list.next))}</strong>` : "<strong>nobody</strong>"}</div>
      <ol class="roorder" aria-label="The order from here">${up.map((x, i) => `<li class="${i === 0 ? "now" : ""}${x.pass ? " ropass" : ""}"${x.pass ? ` title="${cesc(first(x.p))} covered for someone busy, so the rotation passes over them once"` : ""}>${badge(x.p)}${x.pass ? "<small>passes</small>" : ""}</li>`).join("")}</ol>
      <div class="roform">
        <input type="text" class="roclient" placeholder="Client name" maxlength="120" aria-label="Client name">
        <div class="rorow"><select class="rohow" aria-label="Call in or walk in">${how}</select>
          <input type="text" class="ronotes" placeholder="Note (optional)" maxlength="300" aria-label="Note"></div>
        <div class="rorow">
          <button type="button" class="btn ropri" data-rogive="${key}"${rotBusy || !list.next ? " disabled" : ""}>Give to ${cesc(first(list.next))}</button>
          <button type="button" class="btn" data-robusy="${key}" data-cover="${cesc(cover)}"${rotBusy || !cover ? " disabled" : ""} title="${cesc(first(list.next))} is busy: this client goes to ${cesc(first(cover))}, and ${cesc(first(list.next))} stays up for the next one">${cesc(first(list.next))} is busy → ${cesc(first(cover))}</button>
          <button type="button" class="btn" data-roskip="${key}"${rotBusy || !list.next ? " disabled" : ""} title="${cesc(first(afterUp))} gets this client and ${cesc(first(list.next))}'s turn is skipped. With no client name, ${cesc(first(list.next))}'s turn is just skipped.">${cesc(first(list.next))} is out</button>
        </div>
        ${others.length ? `<div class="rorow roout"><span>Client asked for</span><select class="roasked" aria-label="Client asked for"><option value="" selected>Pick who…</option>${others.map(p => `<option value="${cesc(p)}">${cesc(first(p))}</option>`).join("")}</select>
          <button type="button" class="btn" data-roout="${key}"${rotBusy ? " disabled" : ""} title="Give it to them without using the rotation: ${cesc(first(list.next))} stays up">Give out of turn</button></div>` : ""}
        ${msg.err ? `<p class="romsg bad" role="alert">${cesc(msg.err)}</p>` : msg.ok ? `<p class="romsg good" role="status">${cesc(msg.ok)}</p>` : ""}
      </div>
    </div>`;
  }

  function editHtml(key) {
    const list = ROT.lists[key], d = rotDraft;
    const add = (ROT.people || []).filter(p => !d.order.includes(p));
    const msg = rotMsg[key] || {};
    return `<div class="rocard roedit" style="--rh:${ROT_HUE[key]}" data-rot="${key}">
      <div class="rohead"><h3>${cesc(list.label)}: order</h3></div>
      <p class="rosub">Move people up or down, take them off, or pick who is up next. The rotation goes top to bottom, then starts again.</p>
      <ol class="roelist">${d.order.map((p, i) => `<li>
        <label class="ronext" title="Up next"><input type="radio" name="ronext-${key}" value="${cesc(p)}"${d.next === p ? " checked" : ""}> next</label>
        ${badge(p)}
        <span class="rotools">
          <button type="button" class="icon-btn" data-romv="-1" data-i="${i}" aria-label="Move ${cesc(first(p))} up"${i === 0 ? " disabled" : ""}>▲</button>
          <button type="button" class="icon-btn" data-romv="1" data-i="${i}" aria-label="Move ${cesc(first(p))} down"${i === d.order.length - 1 ? " disabled" : ""}>▼</button>
          <button type="button" class="icon-btn del-btn" data-rorm="${i}" aria-label="Take ${cesc(first(p))} off">✕</button>
        </span></li>`).join("")}</ol>
      ${add.length ? `<div class="rorow"><select class="roadd" aria-label="Add someone">${add.map(p => `<option value="${cesc(p)}">${cesc(first(p))}</option>`).join("")}</select>
        <button type="button" class="btn" data-roaddbtn="1">Add</button></div>` : ""}
      <div class="rorow"><button type="button" class="btn ropri" data-rosave="${key}"${rotBusy ? " disabled" : ""}>Save order</button>
        <button type="button" class="btn" data-rocancel="1">Cancel</button></div>
      ${msg.err ? `<p class="romsg bad" role="alert">${cesc(msg.err)}</p>` : ""}
    </div>`;
  }

  let rotTallyOpen = false;   // the Count by person fold, kept across repaints this visit

  function tallyHtml(entries) {
    const rows = ROT_KEYS.map(key => {
      const list = ROT.lists[key];
      const mine = entries.filter(e => e.list === key);
      const people = [...new Set([...list.order, ...mine.map(e => e.producer)])];
      const cells = people.map(p => {
        const got = mine.filter(e => e.producer === p && e.kind !== "skip").length;
        const out = mine.filter(e => e.producer === p && e.kind === "skip").length;
        const busy = mine.filter(e => e.busy === p).length;
        return `<span class="rotal">${badge(p)} <b>${got}</b>${busy ? `<small>${busy} busy</small>` : ""}${out ? `<small>${out} out</small>` : ""}</span>`;
      }).join("");
      return `<div class="rotrow"><span class="rotlbl" style="--rh:${ROT_HUE[key]}">${cesc(list.label)}</span>${cells}</div>`;
    }).join("");
    // folded by default (Frank, 2026-10-06: "make this expandable or a dropdown it draws too much
    // attention"); the fold stays open across repaints once opened this visit
    const total = entries.filter(e => e.kind !== "skip").length;
    return `<details class="rotally"${rotTallyOpen ? " open" : ""}><summary>Count by person<span class="rotsum">${total} turn${total === 1 ? "" : "s"} this folio</span></summary><div class="rotrows">${rows}</div></details>`;
  }

  function logHtml() {
    const { start, end } = folioOf();
    const cur = folioEndFor(today());
    const ends = FOLIO_CLOSE_DATES.filter(e => !cur || e <= cur).sort((a, b) => b.localeCompare(a));
    const opts = ends.map(e => {
      const s = folioStartFor(e);
      return `<option value="${e === cur ? "" : e}"${(rotFolio || cur) === e ? " selected" : ""}>${s ? fmtShortDate(s) + " – " : ""}${fmtShortDate(e)}${e === cur ? " (this folio)" : ""}</option>`;
    }).join("");
    const entries = (ROT.entries || []).filter(e => e.date >= start && e.date <= end)
      .sort((a, b) => (b.date + b.created_at).localeCompare(a.date + a.created_at));
    const rows = entries.map(e => `<tr>
      <td>${cesc(fmtShortDate(e.date))}</td>
      <td class="t"><span class="rotlbl" style="--rh:${ROT_HUE[e.list] || "var(--border-strong)"}">${cesc((ROT.lists[e.list] || {}).label || e.list)}</span></td>
      <td class="t">${badge(e.producer)}${e.kind === "busy" && e.busy ? ` <small class="romute">for ${cesc(first(e.busy))}</small>` : ""}</td>
      <td class="t">${e.kind === "skip" ? `<span class="romute">${e.pair ? "turn skipped, client went to the next person" : "nobody — turn skipped"}</span>` : cesc(e.client)}</td>
      <td class="t">${cesc(e.how || "")}</td>
      <td class="t"><span class="rokind k-${cesc(e.kind)}">${cesc(KIND[e.kind] || e.kind)}</span></td>
      <td class="t">${cesc(e.notes || "")}</td>
      <td class="t romute">${cesc(e.logged_by || "")}</td>
      <td>${ROT.can_edit || e.logged_by === ROT.me ? `<button type="button" class="icon-btn del-btn" data-rodel="${cesc(e.id)}" aria-label="Remove this line" title="Remove this line">✕</button>` : ""}</td>
    </tr>`).join("");
    return `<div class="sect" style="--sc:var(--s3)">
      <h2>This folio's rotation</h2>
      <div class="controls"><select id="rotFolio" aria-label="Folio">${opts}</select></div>
      <p class="sd">Every walk-in and call-in logged, newest first. Taking back the newest line on a rotation gives that person their turn back.</p>
      ${tallyHtml(entries)}
      ${entries.length ? `<div class="scroll"><table class="rotab"><thead><tr><th>Date</th><th class="t">Rotation</th><th class="t">Who</th><th class="t">Client</th><th class="t">How</th><th class="t">Turn</th><th class="t">Note</th><th class="t">Logged by</th><th></th></tr></thead><tbody>${rows}</tbody></table></div>`
        : '<div class="empty">Nothing logged in this folio yet.</div>'}
    </div>`;
  }

  function panelHtml() {
    return `<div class="sect svchero rohero" style="--sc:var(--s3)">
      <h2>Who's up</h2>
      <p class="sd">New business that walks in or calls in goes to whoever is up on its rotation. Personal lines, life and Mexico policies each keep their own turn.</p>
      <div class="rogrid">${ROT_KEYS.filter(k => ROT.lists[k]).map(cardHtml).join("")}</div>
    </div>${logHtml()}`;
  }

  async function post(body, key) {
    rotMsg = {}; rotBusy = true; repaint();
    try {
      const r = await fetch("/api/rotation", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
      const out = await r.json().catch(() => ({}));
      if (out.lists) ROT.lists = out.lists;
      if (!r.ok) { rotMsg[key] = { err: out.error || `could not save (${r.status})` }; if (r.status === 409) await rotLoad(); return false; }
      await rotLoad();
      return out;
    } catch (_) {
      rotMsg[key] = { err: "could not reach the board -- nothing was saved" };
      return false;
    } finally { rotBusy = false; repaint(); }
  }

  function wire() {
    const v = $("#view");
    const tally = v.querySelector(".rotally");
    if (tally) tally.addEventListener("toggle", () => { rotTallyOpen = tally.open; });
    const card = el => el.closest(".rocard");
    const vals = el => {
      const c = card(el);
      return { client: c.querySelector(".roclient").value.trim(), how: c.querySelector(".rohow").value,
        notes: c.querySelector(".ronotes").value.trim(), date: today() };
    };
    v.querySelectorAll("[data-rogive]").forEach(b => b.onclick = async () => {
      const key = b.dataset.rogive, list = ROT.lists[key], f = vals(b);
      if (!f.client) { rotMsg[key] = { err: "Type the client's name first." }; repaint(); return; }
      const ok = await post({ op: "log", list: key, kind: "in", producer: list.next, expect: list.next, ...f }, key);
      if (ok) { rotMsg[key] = { ok: `${f.client} went to ${first(ok.entry.producer)}. ${first(ROT.lists[key].next)} is up next.` }; repaint(); }
    });
    v.querySelectorAll("[data-roskip]").forEach(b => b.onclick = async () => {
      const key = b.dataset.roskip, list = ROT.lists[key], f = vals(b);
      const ok = await post({ op: "log", list: key, kind: "skip", producer: list.next, expect: list.next, ...f }, key);
      if (ok) {
        const out = first(ok.entry.producer), up = first(ROT.lists[key].next);
        rotMsg[key] = { ok: ok.given ? `${out} is out, so ${f.client} went to ${first(ok.given.producer)}. ${up} is up next.` : `${out}'s turn was skipped. ${up} is up next.` };
        repaint();
      }
    });
    v.querySelectorAll("[data-robusy]").forEach(b => b.onclick = async () => {
      const key = b.dataset.robusy, list = ROT.lists[key], f = vals(b), cover = b.dataset.cover;
      if (!f.client) { rotMsg[key] = { err: "Type the client's name first." }; repaint(); return; }
      const ok = await post({ op: "log", list: key, kind: "busy", producer: cover, expect: list.next, ...f }, key);
      if (ok) { rotMsg[key] = { ok: `${f.client} went to ${first(cover)} while ${first(ok.entry.busy)} is busy. ${first(ROT.lists[key].next)} is still up next.` }; repaint(); }
    });
    v.querySelectorAll("[data-roout]").forEach(b => b.onclick = async () => {
      const key = b.dataset.roout, f = vals(b), who = card(b).querySelector(".roasked").value;
      if (!f.client) { rotMsg[key] = { err: "Type the client's name first." }; repaint(); return; }
      if (!who) { rotMsg[key] = { err: "Pick who the client asked for." }; repaint(); return; }
      const ok = await post({ op: "log", list: key, kind: "out", producer: who, ...f }, key);
      if (ok) { rotMsg[key] = { ok: `${f.client} went to ${first(who)} out of turn. ${first(ROT.lists[key].next)} is still up.` }; repaint(); }
    });
    v.querySelectorAll("[data-rodel]").forEach(b => b.onclick = async () => {
      const e = (ROT.entries || []).find(x => x.id === b.dataset.rodel);
      const mate = e && e.pair ? (ROT.entries || []).find(x => x.id === e.pair) : null;
      const skip = e && (e.kind === "skip" ? e : mate && mate.kind === "skip" ? mate : null);
      const given = e && (e.kind === "skip" ? mate : e);
      const what = skip && given ? `${first(skip.producer)}'s skipped turn and ${given.client} (${first(given.producer)})`
        : e && e.kind === "skip" ? first(e.producer) + "'s skipped turn" : e && (e.client + " (" + first(e.producer) + ")");
      if (!e || !confirm(`Remove ${what} from the rotation?`)) return;
      rotMsg = {};
      await post({ op: "del", id: e.id }, e.list);
    });
    const sel = $("#rotFolio");
    if (sel) sel.onchange = () => { rotFolio = sel.value; repaint(); };
    v.querySelectorAll("[data-roedit]").forEach(b => b.onclick = () => {
      rotEdit = b.dataset.roedit; rotMsg = {};
      const l = ROT.lists[rotEdit]; rotDraft = { order: [...l.order], next: l.next };
      repaint();
    });
    const ed = v.querySelector(".roedit");
    if (ed) {
      ed.querySelectorAll("input[type=radio]").forEach(r => r.onchange = () => { rotDraft.next = r.value; });
      ed.querySelectorAll("[data-romv]").forEach(b => b.onclick = () => {
        const i = +b.dataset.i, j = i + +b.dataset.romv, o = rotDraft.order;
        [o[i], o[j]] = [o[j], o[i]]; repaint();
      });
      ed.querySelectorAll("[data-rorm]").forEach(b => b.onclick = () => {
        const [gone] = rotDraft.order.splice(+b.dataset.rorm, 1);
        if (rotDraft.next === gone) rotDraft.next = rotDraft.order[0] || "";
        repaint();
      });
      const addb = ed.querySelector("[data-roaddbtn]");
      if (addb) addb.onclick = () => { rotDraft.order.push(ed.querySelector(".roadd").value); repaint(); };
      ed.querySelector("[data-rocancel]").onclick = () => { rotEdit = ""; rotDraft = null; rotMsg = {}; repaint(); };
      ed.querySelector("[data-rosave]").onclick = async () => {
        const key = rotEdit;
        if (!rotDraft.order.length) { rotMsg[key] = { err: "A rotation needs at least one person." }; repaint(); return; }
        const ok = await post({ op: "order", list: key, order: rotDraft.order, next: rotDraft.next }, key);
        if (ok) { rotEdit = ""; rotDraft = null; rotMsg[key] = { ok: `Saved. ${first(ROT.lists[key].next)} is up next.` }; repaint(); }
      };
    }
  }

  function repaint() {
    if (view !== "rotation" || !ROT) return;
    // Keep what was typed across a repaint.
    const kept = {};
    $$("#view .rocard").forEach(c => {
      const g = s => (c.querySelector(s) || {}).value;
      kept[c.dataset.rot] = { client: g(".roclient"), how: g(".rohow"), notes: g(".ronotes"), asked: g(".roasked") };
    });
    $("#view").innerHTML = panelHtml();
    $$("#view .rocard").forEach(c => {
      const k = kept[c.dataset.rot], m = rotMsg[c.dataset.rot] || {};
      if (!k || m.ok) return;                 // a saved turn clears its form
      for (const [s, val] of [[".roclient", k.client], [".rohow", k.how], [".ronotes", k.notes], [".roasked", k.asked]]) {
        const el = c.querySelector(s); if (el && val != null) el.value = val;
      }
    });
    wire();
  }

  window.rotationPaint = async function rotationPaint() {
    $("#topsub").textContent = "who gets the next walk-in or call-in";
    if (!ROT) $("#view").innerHTML = '<div class="empty">Loading…</div>';
    try { await rotLoad(); } catch (_) {}
    if (!ROT) { $("#view").innerHTML = '<div class="empty">The rotation is only open to the front desk, Crystal and the ops team.</div>'; return; }
    rotMsg = {};
    repaint();
  };

  const css = document.createElement("style");
  css.textContent = `
.rogrid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin-top: 14px; }
@media (max-width: 1100px) { .rogrid { grid-template-columns: 1fr; } }
.rocard { background: var(--surface-raised); color: var(--text-primary); border: var(--bw, 2px) solid var(--border-strong); border-top: 6px solid var(--rh); border-radius: 14px; padding: 14px 16px 16px; box-shadow: var(--shadow); min-width: 0; }
.rohead { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.rocard h3 { margin: 0; font-family: var(--display); font-weight: var(--dw, 700); font-size: 20px; }
.rosub { margin: 2px 0 10px; color: var(--text-secondary); font-size: 13px; }
.rosmall { font-size: 12px; padding: 4px 9px; }
.roup { display: flex; align-items: baseline; gap: 10px; margin: 4px 0 8px; }
.roup span { text-transform: uppercase; letter-spacing: .08em; font-size: 11px; font-weight: 700; color: var(--text-muted); }
.roup strong { font-family: var(--display); font-weight: var(--dw, 700); font-size: 36px; line-height: 1.05; border-bottom: 5px solid var(--pc); }
.roorder { list-style: none; display: flex; flex-wrap: wrap; gap: 6px; padding: 0; margin: 0 0 12px; }
.roorder li { opacity: .75; } .roorder li.now { opacity: 1; }
.roorder li + li::before { content: "→"; margin-right: 6px; color: var(--text-muted); }
.roform { display: flex; flex-direction: column; gap: 8px; border-top: 1px solid var(--border); padding-top: 12px; }
.roform input[type=text], .roedit select { font: inherit; font-size: 14px; padding: 8px 10px; border: 1px solid var(--border-strong); border-radius: 10px; background: var(--surface); color: var(--text-primary); min-width: 0; }
.rorow { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.rorow .ronotes { flex: 1; }
.ropri { background: var(--accent); border-color: var(--accent-d, var(--accent)); color: #fff; }
.ropri:hover { filter: none; border-color: var(--text-primary); }
.btn[disabled] { opacity: .5; cursor: default; }
.roout { font-size: 13px; color: var(--text-secondary); }
.romsg { margin: 2px 0 0; font-size: 13px; font-weight: 600; } .romsg.bad { color: var(--bad); } .romsg.good { color: var(--good); }
.roelist { list-style: none; padding: 0; margin: 0 0 10px; display: flex; flex-direction: column; gap: 6px; }
.roelist li { display: flex; align-items: center; gap: 10px; padding: 6px 8px; border: 1px solid var(--border); border-radius: 10px; }
.roelist .rotools { margin-left: auto; display: flex; gap: 2px; }
.ronext { font-size: 12px; color: var(--text-muted); display: flex; align-items: center; gap: 4px; }
.rotally { margin: 6px 0 14px; border: 1px solid var(--border); border-radius: 10px; background: var(--card2); }
.rotally > summary { cursor: pointer; list-style: none; padding: 8px 12px; font-size: 13px; font-weight: 700; color: var(--text-secondary); display: flex; align-items: center; gap: 10px; }
.rotally > summary::-webkit-details-marker { display: none; }
.rotally > summary::before { content: "▸"; font-size: 11px; transition: transform .15s; } .rotally[open] > summary::before { transform: rotate(90deg); }
.rotally .rotsum { margin-left: auto; font-weight: 500; color: var(--text-muted); }
.rotrows { display: flex; flex-direction: column; gap: 8px; padding: 2px 12px 12px; }
.rotrow { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.rotlbl { display: inline-block; font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 6px; background: color-mix(in oklab, var(--rh) 22%, transparent); border-left: 4px solid var(--rh); white-space: nowrap; }
.rotrow > .rotlbl { min-width: 120px; }
.rotal { display: inline-flex; align-items: center; gap: 5px; } .rotal small { color: var(--text-muted); }
.rotab td, .rotab th { vertical-align: middle; text-align: left; }
.romute { color: var(--text-muted); }
.rokind { font-size: 12px; font-weight: 600; } .rokind.k-skip { color: var(--warn); } .rokind.k-out { color: var(--text-secondary); } .rokind.k-busy { color: var(--accent); }
.roorder li.ropass { opacity: .45; } .roorder li.ropass small { margin-left: 4px; font-size: 11px; color: var(--text-muted); }
`;
  document.head.appendChild(css);
})();
