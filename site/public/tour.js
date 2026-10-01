/* Take a tour (Frank, 2026-10-01: Field notes, option 3): a ruled index card
   with a paper clip beside whatever is being explained, the rest of the board
   dimmed with the thing itself left lit. Ten short steps across the Digest,
   The Flores Post, the Editions, search and Settings. Nothing on the board
   changes; the tour only moves between pages the way a click would. */
(function () {
  const css = `
.tourbtn { border: 1.5px solid var(--border-strong); background: var(--surface-raised); color: var(--text-primary); border-radius: 12px; padding: 0 12px; height: 40px; font: 600 13px var(--body); cursor: pointer; white-space: nowrap; }
.tourbtn:hover { border-color: var(--accent); }
.tourhole { position: fixed; z-index: 90; border-radius: 14px; box-shadow: 0 0 0 9999px rgba(42,35,32,.55); outline: 3px solid var(--livegreen); outline-offset: 3px; pointer-events: none; transition: left .25s, top .25s, width .25s, height .25s; }
.tourcard { position: fixed; z-index: 91; width: 380px; max-width: calc(100vw - 24px); background: #fffdf5; color: #2a2320; border: 1px solid #d9c8b4; border-radius: 4px; box-shadow: 0 14px 40px rgba(0,0,0,.28); padding: 0 0 12px; background-image: linear-gradient(0deg, transparent 0 27px, #f1d9d9 27px 28px); background-size: 100% 28px; background-position: 0 56px; font-family: var(--body); }
.tourcard .clip { position: absolute; top: -14px; left: 28px; width: 22px; height: 40px; border: 3px solid #9a9a9a; border-radius: 11px; border-bottom: 0; }
.tourcard .top { height: 56px; border-bottom: 2px solid #e59a9a; display: flex; align-items: center; justify-content: space-between; padding: 0 16px; margin: 0; max-width: none; }
.tourcard .top b { font: 400 20px var(--display); }
.tourcard .num { width: 30px; height: 30px; border-radius: 50%; background: #2a2320; color: #fff; display: flex; align-items: center; justify-content: center; font: 700 13px var(--body); }
.tourcard p { margin: 0; padding: 10px 16px 0; font-size: 14px; line-height: 28px; }
.tourcard .btns { display: flex; gap: 8px; align-items: center; padding: 8px 16px 0; }
.tourcard .cnt { font-size: 12px; font-weight: 700; color: #6e5f53; margin-left: auto; }
.tourcard .b { border: 0; border-radius: 10px; padding: 8px 14px; font: 700 13px var(--body); background: #b5532f; color: #fff; cursor: pointer; }
.tourcard .b.q { background: #e8dac9; color: #2a2320; }
@media (max-width: 760px) { .tourcard { left: 12px !important; right: 12px; width: auto; top: auto !important; bottom: 12px; } }
`;
  const st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);

  const STEPS = [
    { view: "digest", sel: ".tabs", title: "The menu", text: "Three desks: Apollo for sales, Athena for service, Cerberus for commercial. Each Center lists its pages under it. The Settings button at the bottom picks your look." },
    { view: "digest", sel: "#view .controls", title: "The day", text: "Day shows one day; the other ranges merge every day in them into one report. Today is live; past days are as they went out. The producer filter narrows everything to one person." },
    { view: "digest", sel: "#view .tiles-6", title: "The six numbers", text: "Dials, live contacts, quoted, sold, utilization and the closing ratio, coloured by the same goals as the email. A green glow means the number is live right now. Click a card to open every account behind it." },
    { view: "digest", sel: "#view .sect:has(.podium2), #view .sect", title: "The leaderboard", text: "Seven categories, 5-4-3-2-1 points, medals on the podium. Every number in the table opens that producer's list underneath it." },
    { view: "digest", sel: "#view .chatbox", title: "The day as a chat", text: "Apollo on the left: every coached call and text as it happened. The producers on the right: each sale, quote presented and quote sent. A line opens its coaching card." },
    { view: "digest", sel: "#view .todo", title: "What needs someone", text: "Texts waiting on a reply, leads misfiled in Pipeline, quoted leads going cold. Each one opens the page where it gets fixed." },
    { view: "post", sel: "#view .paper .mast, #view .press", title: "The Flores Post", text: "A published day or a folio as a newspaper: the headline, the goal board, who is close, what to try on a slow day, and Primetime, the sports section, with the standings." },
    { view: "editions", sel: "#view .edtabs", title: "The editions", text: "Six more ways to read the same day: a social feed, a football game, a podcast, a market close, a comic strip and a magazine. React, vote, comment: everyone sees the same tally." },
    { view: null, sel: ".search", title: "Search", text: "Ctrl K from anywhere. Pages, the sections on the page you are on, producers, and every lead on the loaded day: a lead opens its coaching card or its AgencyZoom record." },
    { view: null, sel: "#setBtn", title: "Make it yours", text: "Five looks, each with its Desert Night: Sonoran, Saguaro, Turquoise & Silver, Canyon Sunset, Mesa Minimal. Light, dark or your device's choice. Remembered on this browser." },
  ];
  let i = -1, hole = null, card = null, timer = null;
  const q = sel => sel.split(",").map(s => document.querySelector(s.trim())).find(Boolean) || null;
  function place() {
    const s = STEPS[i], el = q(s.sel);
    if (!hole) { hole = document.createElement("div"); hole.className = "tourhole"; document.body.appendChild(hole); }
    if (!card) { card = document.createElement("div"); card.className = "tourcard"; document.body.appendChild(card); }
    let r = el ? el.getBoundingClientRect() : { left: innerWidth / 2 - 10, top: innerHeight / 2 - 10, width: 20, height: 20 };
    if (el && (r.top < 60 || r.bottom > innerHeight - 40) && r.height < innerHeight - 120) { el.scrollIntoView({ block: "center", behavior: "instant" }); r = el.getBoundingClientRect(); }
    const pad = 6;
    Object.assign(hole.style, { left: (r.left - pad) + "px", top: (r.top - pad) + "px", width: (r.width + pad * 2) + "px", height: (r.height + pad * 2) + "px" });
    card.innerHTML = `<div class="clip"></div><div class="top"><b>${s.title}</b><span class="num">${i + 1}</span></div><p>${s.text}</p>
      <div class="btns"><button type="button" class="b q" data-t="skip">${i === STEPS.length - 1 ? "Done" : "Skip tour"}</button><span class="cnt">Step ${i + 1} of ${STEPS.length}</span>${i ? '<button type="button" class="b q" data-t="back">Back</button>' : ""}${i < STEPS.length - 1 ? '<button type="button" class="b" data-t="next">Next →</button>' : ""}</div>`;
    const cw = Math.min(380, innerWidth - 24), ch = card.offsetHeight || 220;
    let left = r.right + 24, top = r.top;
    if (left + cw > innerWidth - 12) { left = Math.max(12, Math.min(r.left, innerWidth - cw - 12)); top = r.bottom + 24; }
    if (top + ch > innerHeight - 12) top = Math.max(12, r.top - ch - 24);
    if (top + ch > innerHeight - 12) top = Math.max(12, innerHeight - ch - 12);
    card.style.left = left + "px"; card.style.top = top + "px";
  }
  async function go(n) {
    i = n;
    if (i < 0 || i >= STEPS.length) return stop();
    const s = STEPS[i];
    if (s.view && view !== s.view) { await goView(s.view); for (let k = 0; k < 30 && !q(s.sel); k++) await new Promise(r => setTimeout(r, 150)); }
    place();
  }
  function stop() {
    if (hole) hole.remove(); if (card) card.remove(); hole = card = null; i = -1;
    try { localStorage.setItem("board-tour-done", "1"); } catch (_) {}
  }
  window.startTour = () => go(0);
  document.addEventListener("click", e => {
    if (e.target.closest("#tourbtn")) { e.preventDefault(); go(0); return; }
    const b = e.target.closest(".tourcard [data-t]"); if (!b) return;
    if (b.dataset.t === "skip") stop(); else if (b.dataset.t === "back") go(i - 1); else go(i + 1);
  });
  document.addEventListener("keydown", e => { if (i < 0) return; if (e.key === "Escape") stop(); else if (e.key === "ArrowRight") go(i + 1); else if (e.key === "ArrowLeft") go(i - 1); });
  addEventListener("resize", () => { if (i >= 0) { clearTimeout(timer); timer = setTimeout(place, 100); } });
  addEventListener("scroll", () => { if (i >= 0) { clearTimeout(timer); timer = setTimeout(place, 60); } }, true);
  const host = document.querySelector(".top .search");
  if (host) { const b = document.createElement("button"); b.type = "button"; b.id = "tourbtn"; b.className = "tourbtn"; b.textContent = "Take a tour"; host.insertAdjacentElement("afterend", b); }
})();
