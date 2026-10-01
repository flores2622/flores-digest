/* The editions (Frank, 2026-10-01: "all of them, go to production") ----------
   Six ways to read a published day or a folio, each with its own mechanic,
   all drawn from the same day documents as the Digest and The Flores Post:
     The Flores Feed   a social timeline: stories, reactions, comments, a poll
     Fourth and Goal   a football game: scoreboard, drives, player cards, MVP vote
     KFLR The Close    a podcast: segments, the Villain, the Countdown, the Mailbag
     FLRS 500          a market close: producers as stocks priced on folio premium
     Cold Call Comics  a comic strip: panels from the day's calls, a boss fight, a duel
     CLOSER            a magazine: cover, cover story, drawn infographic, podium
   Every one carries the leaderboard and real figures. What people do on them
   (reactions, comments, poll and MVP votes, mailbag notes, panel likes) is
   shared through the Worker's /api/editions/<key> and kept in R2, so everyone
   sees the same tally; the viewer's own picks (watchlist, cover photo, card
   flips) stay in their browser. Nothing here is paid for. */

(function () {
  const css = `
.edtabs { display: flex; gap: 6px; flex-wrap: wrap; margin: 0 0 16px; }
.edcard { background: var(--surface-raised); border: var(--bw) solid var(--border-strong); border-radius: var(--rad); box-shadow: var(--shadow); padding: 20px; display: flex; flex-direction: column; gap: 12px; min-width: 0; }
.edcard h2, .edcard h3 { margin: 0; border: 0; padding: 0; text-transform: none; letter-spacing: 0; }
.edcard h2 { font-size: 26px; } .edcard h3 { font: 400 20px var(--display); }
.ed .hrow { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.ed .lab { font-size: 11px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; color: var(--text-muted); }
.ed .note { font-size: 13px; color: var(--text-muted); margin: 0; }
.ed .echip { display: inline-block; font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 999px; background: var(--chip); }
.ed .echip.g { background: var(--goodbg); color: var(--good); } .ed .echip.r { background: var(--badbg); color: var(--bad); }
.ed .ebtn { border: 0; border-radius: 10px; padding: 9px 14px; font: 700 13px var(--body); background: var(--accent); color: #fff; cursor: pointer; }
.ed .ebtn.q { background: var(--chip); color: var(--text-primary); }
.ed input.t { font: 500 14px var(--body); padding: 9px 11px; border: 1.5px solid var(--border-strong); border-radius: 10px; background: var(--surface-raised); color: var(--text-primary); width: 100%; min-width: 0; }
.ed .av { width: 40px; height: 40px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font: 700 13px var(--body); flex: none; position: relative; }
.ed .av .st { position: absolute; right: -6px; bottom: -6px; background: var(--surface-raised); border: 2px solid var(--surface-raised); border-radius: 999px; font-size: 10px; padding: 1px 5px; color: var(--accent-d); font-weight: 800; }
.ed table.lbt { width: 100%; border-collapse: collapse; font-size: 13.5px; min-width: 980px; }
.ed table.lbt th { font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--text-muted); text-align: right; padding: 8px 6px; border-bottom: 2px solid var(--text-primary); white-space: nowrap; }
.ed table.lbt td { text-align: right; padding: 9px 6px; border-bottom: 1px solid var(--grid); white-space: nowrap; font-size: 13.5px; }
.ed table.lbt th:first-child, .ed table.lbt td:first-child { text-align: left; }
.ed table.lbt tr.tot td { border-top: 2px solid var(--text-primary); font-weight: 800; background: transparent; }
.ed .scroll { border: 0; } .ed .scroll table { background: transparent; }
.edtoast { position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%); background: var(--side); color: var(--sideInk); padding: 10px 16px; border-radius: 999px; font-size: 13px; z-index: 70; opacity: 0; transition: opacity .25s; pointer-events: none; }
.edtoast.on { opacity: 1; }
/* Feed */
.feedA { display: grid; grid-template-columns: minmax(0, 700px) minmax(0, 1fr); gap: 20px; }
.ed .col { display: flex; flex-direction: column; gap: 14px; min-width: 0; }
.pc { background: var(--surface-raised); border: var(--bw) solid var(--border-strong); border-radius: 18px; padding: 16px 18px; display: flex; flex-direction: column; gap: 10px; box-shadow: var(--shadow); }
.pc h3 { margin: 0; font: 400 20px var(--display); border: 0; padding: 0; text-transform: none; letter-spacing: 0; }
.pc p { margin: 0; font-size: 16px; line-height: 1.5; }
.ed .whor { display: flex; align-items: center; gap: 12px; } .ed .whor b { display: block; font-size: 15px; } .ed .whor small { color: var(--text-muted); font-size: 12px; } .ed .whor .ver { color: var(--good); font-size: 12px; margin-left: 4px; }
.pic { border-radius: 14px; background: var(--card2); padding: 16px; display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; } .pic b { font: 400 36px var(--display); color: var(--good); }
.rx { display: flex; gap: 6px; flex-wrap: wrap; } .rx button { border: 1.5px solid var(--border-strong); background: var(--card2); border-radius: 999px; padding: 4px 10px; font: 500 13px var(--body); color: var(--text-primary); cursor: pointer; }
.rx button[aria-pressed="true"] { border-color: var(--accent); background: color-mix(in oklab, var(--accent) 14%, var(--surface-raised)); font-weight: 800; }
.cm { display: flex; flex-direction: column; gap: 8px; border-top: 1px solid var(--grid); padding-top: 8px; }
.cm .c { display: flex; gap: 10px; align-items: flex-start; font-size: 14px; line-height: 1.45; } .cm .c b { font-size: 13px; } .cm .c small { color: var(--text-muted); margin-left: 6px; }
.cm form { display: flex; gap: 8px; }
.stories { display: flex; gap: 14px; overflow: auto; padding: 2px; } .stories button { width: 72px; flex: none; text-align: center; font: 500 12px var(--body); border: 0; background: none; color: inherit; cursor: pointer; }
.stories i { display: flex; align-items: center; justify-content: center; width: 62px; height: 62px; border-radius: 50%; margin: 0 auto 4px; border: 3px solid var(--accent); background: var(--surface-raised); font-weight: 800; font-style: normal; } .stories i.seen { border-color: var(--border-strong); }
.poll { display: flex; flex-direction: column; gap: 8px; } .poll button { position: relative; text-align: left; border: 1.5px solid var(--border-strong); background: var(--card2); border-radius: 10px; padding: 10px 12px; font: 500 14px var(--body); color: var(--text-primary); overflow: hidden; cursor: pointer; }
.poll button i { position: absolute; left: 0; top: 0; bottom: 0; background: color-mix(in oklab, var(--accent) 16%, transparent); z-index: 0; } .poll button span { position: relative; display: flex; justify-content: space-between; } .poll button[aria-pressed="true"] { border-color: var(--accent); font-weight: 800; }
.trend { display: flex; justify-content: space-between; align-items: center; font-size: 15px; padding: 8px 0; border-bottom: 1px solid var(--grid); gap: 10px; }
.prog { height: 12px; border-radius: 6px; background: var(--chip); overflow: hidden; } .prog i { display: block; height: 100%; background: var(--good); }
.edmodal { position: fixed; inset: 0; background: rgba(0,0,0,.55); display: flex; align-items: center; justify-content: center; z-index: 80; padding: 20px; }
.edmodal .edcard { width: min(680px, 100%); max-height: 85vh; overflow: auto; }
.tx p { margin: 0; font-size: 15px; line-height: 1.55; padding: 6px 8px; border-radius: 8px; } .tx p.on { background: color-mix(in oklab, var(--accent) 12%, transparent); } .tx p b { color: var(--accent-d); }
/* Fourth and Goal */
.gi { background: #0f2a1e; color: #fff; border-radius: 20px; overflow: hidden; box-shadow: var(--shadow); display: flex; flex-direction: column; }
.gi .sb { background: #071a12; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; padding: 14px 26px; gap: 16px; border-bottom: 4px solid #ffd27a; }
.gi .tm { display: flex; align-items: center; gap: 14px; } .gi .tm b { font: 400 44px/1 'Bebas Neue', Impact, sans-serif; letter-spacing: .06em; } .gi .tm .pt { font: 400 64px/1 'Bebas Neue', Impact, sans-serif; color: #ffd27a; }
.gi .q { text-align: center; font: 400 20px 'Bebas Neue', Impact, sans-serif; letter-spacing: .14em; color: #9fd3b6; } .gi .q b { display: block; font-size: 34px; color: #fff; }
.gi .tm.r { justify-content: flex-end; }
.field { position: relative; height: 220px; background: repeating-linear-gradient(90deg, #1d6b3d 0 10%, #237a46 10% 20%); border-top: 3px solid #fff; border-bottom: 3px solid #fff; overflow: hidden; }
.field .yd { position: absolute; top: 0; bottom: 0; width: 2px; background: rgba(255,255,255,.5); } .field .yd span { position: absolute; top: 8px; left: 6px; font: 400 14px 'Bebas Neue', Impact, sans-serif; color: #fff; opacity: .8; }
.field .ez { position: absolute; top: 0; bottom: 0; width: 10%; background: #b5532f; display: flex; align-items: center; justify-content: center; font: 400 28px 'Bebas Neue', Impact, sans-serif; letter-spacing: .3em; writing-mode: vertical-rl; color: #fff; }
.field .ball { position: absolute; top: 50%; transform: translate(-50%, -50%); width: 44px; height: 44px; border-radius: 50%; border: 3px solid #fff; display: flex; align-items: center; justify-content: center; font: 700 12px var(--body); color: #fff; box-shadow: 0 6px 16px rgba(0,0,0,.4); transition: left .8s cubic-bezier(.3,.8,.3,1); }
.field .cap { position: absolute; left: 12px; right: 12px; bottom: 10px; font-size: 13px; background: rgba(0,0,0,.55); padding: 6px 10px; border-radius: 8px; }
.drives { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; padding: 18px 26px; }
.drive { background: #143b2a; border-radius: 12px; padding: 12px 14px; display: flex; gap: 12px; align-items: center; cursor: pointer; border: 2px solid transparent; text-align: left; color: #fff; font: inherit; } .drive:hover { border-color: #ffd27a; }
.drive b { font: 400 26px/1 'Bebas Neue', Impact, sans-serif; color: #ffd27a; min-width: 70px; } .drive span { font-size: 13px; color: #cfe6d8; } .drive strong { font-size: 15px; display: block; color: #fff; }
.roster { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; padding: 0 26px 18px; }
.pcard { perspective: 900px; height: 300px; border: 0; padding: 0; background: none; } .pcard .in { position: relative; width: 100%; height: 100%; transition: transform .6s; transform-style: preserve-3d; cursor: pointer; } .pcard.flip .in { transform: rotateY(180deg); }
.pcard .f, .pcard .b { position: absolute; inset: 0; backface-visibility: hidden; border-radius: 14px; padding: 12px; display: flex; flex-direction: column; gap: 6px; color: #2a2320; }
.pcard .f { background: linear-gradient(160deg, #fffaf3, #e8dac9); border: 3px solid #ffd27a; } .pcard .b { background: #1b1613; color: #f3e9dc; transform: rotateY(180deg); border: 3px solid #ffd27a; font-size: 12px; }
.pcard .ovr { display: flex; justify-content: space-between; align-items: center; } .pcard .ovr b { font: 400 44px/1 'Bebas Neue', Impact, sans-serif; color: #b5532f; } .pcard .ovr small { font-size: 10px; letter-spacing: .12em; text-transform: uppercase; color: #6e5f53; }
.pcard .nm { font: 400 18px var(--display); } .pcard .pos { font-size: 11px; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: #6e5f53; }
.pcard .ph { height: 84px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font: 400 34px var(--display); }
.pcard .rt { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px; font-size: 10px; text-align: center; } .pcard .rt span { background: rgba(42,35,32,.06); border-radius: 5px; padding: 4px 0; } .pcard .rt b { display: block; font: 800 14px var(--body); }
.pcard .b .row { display: flex; justify-content: space-between; border-bottom: 1px solid #3a302b; padding: 4px 0; }
.pcard.mvp .f { background: linear-gradient(160deg, #ffe7a3, #e59a6f); border-color: #b5532f; }
.gpan { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; padding: 0 26px 22px; }
.gpan .box { background: #143b2a; border-radius: 12px; padding: 14px; font-size: 14px; line-height: 1.5; } .gpan .box h4 { margin: 0 0 6px; font: 400 22px 'Bebas Neue', Impact, sans-serif; letter-spacing: .08em; color: #ffd27a; }
.gflag { display: flex; gap: 10px; align-items: flex-start; padding: 6px 0; border-bottom: 1px solid #1f4a35; } .gflag i { width: 14px; height: 18px; background: #ffd27a; clip-path: polygon(0 0, 100% 0, 70% 50%, 100% 100%, 0 100%); flex: none; margin-top: 2px; }
.vs { display: flex; gap: 10px; align-items: center; } .vs .bar { flex: 1; height: 10px; background: #0b2318; border-radius: 5px; overflow: hidden; } .vs .bar i { display: block; height: 100%; background: #ffd27a; }
.gi .lbt, .gi .lbt td, .gi .lbt th { color: #fff; } .gi .lbt th { color: #9fd3b6; border-color: #ffd27a; } .gi .lbt td { border-color: #1f4a35; } .gi .lbt tr.tot td { border-color: #ffd27a; }
/* KFLR The Close */
.pod { display: grid; grid-template-columns: 400px minmax(0, 1fr); gap: 20px; align-items: start; }
.art { aspect-ratio: 1; border-radius: 20px; color: #fff; padding: 24px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: var(--shadow); }
.art b { font: 400 40px/1 var(--display); } .art span { font-size: 12px; letter-spacing: .12em; text-transform: uppercase; font-weight: 800; }
.player { display: flex; align-items: center; gap: 14px; } .player > button { width: 56px; height: 56px; border-radius: 50%; border: 0; background: var(--accent); color: #fff; font-size: 22px; flex: none; cursor: pointer; }
.wave { flex: 1; height: 48px; display: flex; align-items: center; gap: 3px; } .wave i { flex: 1; background: var(--chip); border-radius: 2px; } .wave i.on { background: var(--accent); }
.segs { display: flex; flex-direction: column; } .segs button { display: grid; grid-template-columns: 44px 60px 1fr auto; gap: 12px; align-items: center; text-align: left; border: 0; background: none; padding: 12px 6px; border-bottom: 1px solid var(--grid); color: inherit; font: inherit; cursor: pointer; }
.segs button:hover, .segs button.on { background: var(--card2); } .segs .ic { width: 40px; height: 40px; border-radius: 12px; background: var(--chip); display: flex; align-items: center; justify-content: center; font-size: 18px; }
.segs .t { font-size: 13px; color: var(--text-muted); } .segs b { font-size: 16px; } .segs small { display: block; color: var(--text-muted); font-size: 13px; font-weight: 400; }
.hp { height: 14px; border-radius: 7px; background: var(--badbg); overflow: hidden; border: 1.5px solid var(--accent); } .hp i { display: block; height: 100%; background: var(--accent); }
.cnt { display: flex; flex-direction: column; gap: 6px; } .cnt div { display: grid; grid-template-columns: 50px 1fr auto; gap: 10px; align-items: center; padding: 8px 10px; border-radius: 10px; background: var(--card2); } .cnt div b { font: 400 30px/1 var(--display); color: var(--accent); }
.mail { display: flex; flex-direction: column; gap: 8px; } .mail .m { background: var(--card2); border-radius: 12px; padding: 10px 12px; font-size: 14px; line-height: 1.45; } .mail .m b { display: block; font-size: 12px; color: var(--text-muted); margin-bottom: 2px; }
/* FLRS 500 */
.mkt { background: #0b0f14; color: #e8edf2; border-radius: 20px; overflow: hidden; box-shadow: var(--shadow); font-family: 'JetBrains Mono', ui-monospace, monospace; }
.tape { background: #111820; padding: 8px 0; white-space: nowrap; overflow: hidden; font-size: 14px; border-bottom: 1px solid #1f2a36; } .tape span { margin-right: 36px; }
.up { color: #4ade80; } .dn { color: #f87171; } .fl { color: #9fb0c8; }
.mkt .g { display: grid; grid-template-columns: minmax(0, 1fr) 420px; gap: 22px; padding: 22px 26px; }
.mkt h2 { margin: 0; font: 400 40px/1 var(--display); color: #fff; border: 0; padding: 0; text-transform: none; letter-spacing: 0; }
.mkt table { width: 100%; border-collapse: collapse; font-size: 14px; } .mkt th { text-align: right; font-weight: 400; color: #9fb0c8; padding: 8px 8px; border-bottom: 1px solid #1f2a36; font-size: 11px; letter-spacing: .08em; text-transform: uppercase; white-space: nowrap; }
.mkt td { text-align: right; padding: 10px 8px; border-bottom: 1px solid #141b24; white-space: nowrap; color: #e8edf2; font-size: 14px; } .mkt th:first-child, .mkt td:first-child, .mkt th:nth-child(2), .mkt td:nth-child(2) { text-align: left; }
.mkt tr.mk { cursor: pointer; } .mkt tr.mk:hover td, .mkt tr.mk.on td { background: #121b26; } .mkt tbody tr:hover { background: transparent; } .sym { font-weight: 700; color: #fff; }
.star { border: 0; background: none; color: #4b5a6b; font-size: 16px; cursor: pointer; } .star[aria-pressed="true"] { color: #ffd27a; }
.chartbox { background: #111820; border: 1px solid #1f2a36; border-radius: 14px; padding: 16px; display: flex; flex-direction: column; gap: 10px; } .chartbox svg { width: 100%; height: 260px; display: block; }
.rng { display: flex; gap: 4px; } .rng button { border: 1px solid #1f2a36; background: #0b0f14; color: #9fb0c8; border-radius: 6px; padding: 4px 10px; font: 700 12px 'JetBrains Mono', monospace; cursor: pointer; } .rng button[aria-pressed="true"] { background: #1f2a36; color: #fff; }
.anal { background: #111820; border: 1px solid #1f2a36; border-radius: 14px; padding: 16px; font-family: var(--body); display: flex; flex-direction: column; gap: 8px; font-size: 14px; line-height: 1.5; } .anal h4 { margin: 0; font: 400 22px var(--display); color: #fff; } .anal p { margin: 0; }
.anal .r { display: flex; justify-content: space-between; border-bottom: 1px solid #1f2a36; padding: 5px 0; font-family: 'JetBrains Mono', monospace; font-size: 13px; }
/* Cold Call Comics */
.comic { background: #fffdf7; color: #2a2320; border: 3px solid #2a2320; border-radius: 8px; padding: 22px; display: flex; flex-direction: column; gap: 14px; font-family: 'Comic Neue', cursive; box-shadow: var(--shadow); }
.comic .title { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 3px solid #2a2320; padding-bottom: 6px; gap: 10px; flex-wrap: wrap; } .comic .title b { font: 400 54px/1 Bangers, Impact, sans-serif; letter-spacing: .04em; color: #b5532f; }
.panels { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.panel { border: 3px solid #2a2320; background: #fffaf3; aspect-ratio: 4 / 3; position: relative; overflow: hidden; display: flex; flex-direction: column; }
.panel .cap { background: #fff2b8; border-bottom: 3px solid #2a2320; padding: 6px 10px; font-weight: 700; font-size: 14px; }
.scene { flex: 1; position: relative; background: linear-gradient(180deg, #f8efe4 60%, #e8dac9 60%); }
.fig { position: absolute; bottom: 14px; width: 70px; text-align: center; } .fig .hd { width: 44px; height: 44px; border-radius: 50%; margin: 0 auto; border: 3px solid #2a2320; } .fig .bd { width: 56px; height: 60px; border-radius: 14px 14px 4px 4px; margin: -4px auto 0; border: 3px solid #2a2320; } .fig small { display: block; font-weight: 700; font-size: 11px; margin-top: 3px; }
.sbb { position: absolute; background: #fff; border: 3px solid #2a2320; border-radius: 16px; padding: 8px 12px; font-weight: 700; font-size: 13px; line-height: 1.3; max-width: 62%; } .sbb::after { content: ""; position: absolute; bottom: -14px; left: 24px; border: 8px solid transparent; border-top: 10px solid #2a2320; }
.sbb.th { border-radius: 50%; padding: 14px 16px; } .sbb.th::after { display: none; }
.fx { position: absolute; font: 400 34px/1 Bangers, Impact, sans-serif; color: #b5532f; transform: rotate(-8deg); text-shadow: 2px 2px 0 #2a2320; }
.panel.duel .scene { background: linear-gradient(115deg, var(--l) 0 48%, #fff 48% 52%, var(--r) 52%); }
.panel.duel .vsb { position: absolute; left: 50%; top: 40%; transform: translate(-50%, -50%); font: 400 54px/1 Bangers, Impact, sans-serif; color: #ffd27a; text-shadow: 3px 3px 0 #2a2320; }
.panel.duel .hpb { position: absolute; top: 10px; width: 40%; height: 12px; background: #fff; border: 2px solid #2a2320; } .panel.duel .hpb i { display: block; height: 100%; background: #1fbf5c; }
.panel.duel .lab2 { position: absolute; top: 26px; font-weight: 700; font-size: 12px; color: #fff; text-shadow: 1px 1px 0 #2a2320; }
.panel.boss .scene { background: radial-gradient(circle at 50% 70%, #f2c9b4, #b5532f 60%, #5a2416); }
.panel.boss .mon { position: absolute; left: 50%; bottom: 10px; transform: translateX(-50%); width: 120px; height: 120px; border-radius: 50% 50% 10px 10px; background: #2a2320; border: 4px solid #000; display: flex; align-items: center; justify-content: center; color: #ffd27a; font: 400 20px Bangers, Impact, sans-serif; text-align: center; line-height: 1; padding: 6px; }
.panel.tumble .scene { background: linear-gradient(180deg, #f2c9a0, #e8dac9 70%); } .panel.tumble .tw { position: absolute; bottom: 18px; left: 40%; width: 50px; height: 50px; border-radius: 50%; border: 3px dashed #8a6a3e; }
.panel.last .scene { background: #2a2320; color: #f3e9dc; display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 6px; text-align: center; padding: 14px; } .panel.last .scene b { font: 400 46px/1 Bangers, Impact, sans-serif; color: #ffd27a; letter-spacing: .04em; }
.plike { position: absolute; right: 8px; bottom: 8px; border: 2px solid #2a2320; background: #fff; border-radius: 999px; padding: 2px 8px; font: 700 12px 'Comic Neue', cursive; cursor: pointer; } .plike[aria-pressed="true"] { background: #ffd27a; }
.comic .lbt, .comic .lbt td { color: #2a2320; }
/* CLOSER */
.mag { display: grid; grid-template-columns: 560px minmax(0, 1fr); border-radius: 20px; overflow: hidden; border: var(--bw) solid var(--border-strong); box-shadow: var(--shadow); background: var(--surface-raised); }
.cover { background: #f6f1e7; color: #2a2320; padding: 36px; display: flex; flex-direction: column; gap: 16px; min-height: 760px; }
.cover .t { font: 400 104px/.9 var(--display); letter-spacing: -.02em; border-bottom: 4px solid #2a2320; padding-bottom: 12px; }
.cover .port { flex: 1; min-height: 360px; border-radius: 8px; position: relative; overflow: hidden; display: flex; align-items: flex-end; padding: 22px; color: #fff; font: 400 42px/1.05 var(--display); text-shadow: 0 1px 10px rgba(0,0,0,.4); }
.cover .cls { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; font-size: 14px; line-height: 1.45; } .cover .cls b { display: block; font: 400 19px var(--display); }
.sil { position: absolute; left: 50%; bottom: 0; transform: translateX(-50%); width: 62%; height: 78%; } .sil::before { content: ""; position: absolute; left: 50%; top: 0; transform: translateX(-50%); width: 34%; aspect-ratio: 1; border-radius: 50%; background: var(--c); } .sil::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 58%; border-radius: 40% 40% 0 0; background: var(--c); }
.cover .seg { display: flex; gap: 3px; background: #e8dac9; padding: 4px; border-radius: 12px; flex-wrap: wrap; } .cover .seg button { border: 0; padding: 7px 11px; border-radius: 9px; background: transparent; font: 500 13px var(--body); color: #5e5046; cursor: pointer; } .cover .seg button[aria-pressed="true"] { background: #fffaf3; color: #2a2320; font-weight: 700; }
.spread { padding: 40px 44px; display: flex; flex-direction: column; gap: 16px; min-width: 0; } .spread .k { font-size: 12px; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; color: var(--accent); }
.spread h2 { margin: 0; font: 800 52px/1.02 Fraunces, serif; letter-spacing: -.01em; text-wrap: balance; border: 0; padding: 0; text-transform: none; } .spread .pq { font: italic 400 30px/1.25 Fraunces, serif; border-left: 6px solid var(--accent); padding-left: 18px; margin: 8px 0; } .spread p { margin: 0; font-size: 17px; line-height: 1.65; color: var(--text-primary); max-width: 72ch; }
.info { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.info div { background: var(--card2); border-radius: 16px; padding: 18px; display: flex; flex-direction: column; gap: 4px; position: relative; overflow: hidden; } .info b { font: 800 44px/1 Fraunces, serif; color: var(--accent); } .info span { font-size: 13px; color: var(--text-muted); }
.info .ring { width: 70px; height: 70px; border-radius: 50%; background: conic-gradient(var(--accent) 0 var(--p), var(--chip) var(--p) 100%); display: flex; align-items: center; justify-content: center; } .info .ring i { width: 48px; height: 48px; border-radius: 50%; background: var(--card2); display: flex; align-items: center; justify-content: center; font: 800 14px var(--body); font-style: normal; }
.podium { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; align-items: end; height: 260px; }
.podium div { display: flex; flex-direction: column; align-items: center; gap: 6px; text-align: center; } .podium .blk { width: 100%; border-radius: 12px 12px 0 0; background: var(--card2); display: flex; align-items: center; justify-content: center; font: 800 28px Fraunces, serif; color: var(--accent); }
.podium small { font-size: 12px; color: var(--text-muted); } .podium b { font: 400 16px var(--display); }
@media (max-width: 1100px) { .feedA, .pod, .mkt .g, .mag { grid-template-columns: 1fr; } .roster { grid-template-columns: repeat(2, minmax(0, 1fr)); } .gpan, .panels, .drives { grid-template-columns: 1fr; } .info, .podium { grid-template-columns: repeat(2, minmax(0, 1fr)); } .gi .sb { grid-template-columns: 1fr; } .cover { min-height: 0; } }
`;
  const st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
})();

const ED_PUBS = [["feed", "The Flores Feed"], ["grid", "Fourth and Goal"], ["pod", "KFLR The Close"], ["mkt", "FLRS 500"], ["comic", "Cold Call Comics"], ["closer", "CLOSER"]];
let edPub = "feed";
try { const v = localStorage.getItem("board-edition"); if (ED_PUBS.some(p => p[0] === v)) edPub = v; } catch (_) {}
const edMine = { watch: {}, cover: "", flip: {}, seen: {} };   // this viewer's own picks
try { Object.assign(edMine, JSON.parse(localStorage.getItem("board-edition-mine") || "{}")); } catch (_) {}
const edSaveMine = () => { try { localStorage.setItem("board-edition-mine", JSON.stringify(edMine)); } catch (_) {} };
const edShared = { key: "", state: null };                      // everyone's: reactions, comments, votes, mailbag, likes
let edSeg = 0, edPlaying = false, edTick = null, edSel = "FLRS", edRng = "folio";
const edMe = () => ME.name || "Someone";
const edEsc = s => cesc(s);
function edToast(t) { let e = $("#edtoast"); if (!e) { e = document.createElement("div"); e.id = "edtoast"; e.className = "edtoast"; document.body.appendChild(e); } e.textContent = t; e.classList.add("on"); clearTimeout(e._t); e._t = setTimeout(() => e.classList.remove("on"), 1800); }

/* ---- shared state through the Worker ----------------------------------------- */
async function edLoadShared(key) {
  if (edShared.key === key && edShared.state) return edShared.state;
  let s = null;
  try { const r = await fetch(`/api/editions/${encodeURIComponent(key)}`, { cache: "no-store" }); if (r.ok) s = await r.json(); } catch (_) {}
  edShared.key = key; edShared.state = s || { rx: {}, cm: {}, poll: {}, mvp: {}, mail: [], likes: {} };
  return edShared.state;
}
async function edPost(op, data) {
  try {
    const r = await fetch(`/api/editions/${encodeURIComponent(edShared.key)}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ op, ...data }) });
    if (r.ok) { edShared.state = await r.json(); return true; }
    const e = await r.json().catch(() => ({})); edToast(e.error || "Could not save that");
  } catch (_) { edToast("Could not reach the board"); }
  return false;
}

/* ---- the figures ----------------------------------------------------------------- */
function edFacts(d, folioRows, lastFolio, isFolio) {
  const F = postFacts(d);
  const names = PRODUCER_ROSTER.filter(n => F.byName[n]).concat(F.prods.map(p => p.name).filter(n => !PRODUCER_ROSTER.includes(n)));
  const P = names.map(n => ({ n, f: pfirst(n), i: n.split(" ").map(x => x[0]).join("").slice(0, 2).toUpperCase(), c: DOT[n] || "#2a2320" }));
  const sp = (d.speed_to_dial || {}).per || {};
  const M = d.messages || {};
  const sendoffAll = c => c.sendoff && (Array.isArray(c.sendoff) ? c.sendoff[0] : c.sendoff) !== "no" && (Array.isArray(c.sendoff) ? c.sendoff[0] : c.sendoff) != null;
  const NUM = Object.fromEntries(P.map(p => {
    const x = F.byName[p.n] || {}, mp = (M.producers || {})[p.n] || {}, calls = F.calls.filter(c => c.who === p.n);
    const quoteUp = calls.filter(c => c.sendoff != null && (Array.isArray(c.sendoff) ? c.sendoff[0] : c.sendoff) !== null).length;
    const sent = calls.filter(c => (Array.isArray(c.sendoff) ? c.sendoff[0] : c.sendoff) === "producer").length;
    return [p.f, { n: p.n, dials: +x.dials || 0, live: +x.live || 0, rate: +x.rate || 0, hh: +x.hh || 0, pq: +x.pq || 0, ps: +x.ps || 0, pol: +x.pol || 0,
      rp: x.coach && x.coach.roleplay != null ? +x.coach.roleplay : (x.rp_scored != null ? Math.round(x.rp_scored) : 0), util: x.util != null ? +x.util : null,
      tasks: x.tasks ? (x.tasks.pct != null ? +x.tasks.pct : (x.tasks.total ? Math.round(100 * x.tasks.completed / x.tasks.total) : null)) : null, open: x.tasks ? (+x.tasks.open || 0) : 0,
      std: sp[p.n] && sp[p.n].median != null ? +sp[p.n].median : null, talk: +x.talk || 0, texts: (+mp.texts || 0), emails: (+mp.emails || 0), sent, quoteUp, hhSold: F.hhSoldBy(p.n), pts: x.pts || 0, flags: F.flagsBy[p.n] || 0 }];
  }));
  const T = { dials: F.dials, live: F.live, rate: F.rate, hh: F.hh, pq: F.pq, ps: F.ps, pol: F.pol, hhSold: F.hhSold, talk: F.talk, util: F.util, rp: (d.totals || {}).roleplay, tasks: F.tasks,
    texts: Object.values(NUM).reduce((a, x) => a + x.texts, 0), emails: Object.values(NUM).reduce((a, x) => a + x.emails, 0), sent: F.sendoffs.length, quoteUp: Object.values(NUM).reduce((a, x) => a + x.quoteUp, 0) };
  const SALES = F.soldRows.map(r => ({ w: pfirst(r.who), n: r.who, prod: r.product || "policy", amt: +r.premium || 0, src: r.source || "" }));
  const FLAGS = F.calls.flatMap(c => (c.flags || []).map(f => [pfirst(c.who), `${f}${c.time ? ` (${c.time})` : ""}`]));
  const rows = folioRows || [];
  const dayKey = d.date || (rows.length ? rows[rows.length - 1].date : "");
  const idx = rows.findIndex(r => r.date === dayKey);
  const series = w => { let a = 0; return rows.map(r => a += (w === "FLRS" ? r.ps : (r.by[w] || 0))); };
  const FTOT = rows.reduce((a, r) => a + r.ps, 0);
  const goal = lastFolio && lastFolio.days ? Math.round(lastFolio.ps / lastFolio.days) : (rows.length > 1 ? Math.round(FTOT / rows.length) : 3000);
  const streak = {};
  for (const p of P) { let s = 0; for (let i = (idx >= 0 ? idx : rows.length - 1); i >= 0 && (rows[i].by[p.f] || 0) > 0; i--) s++; streak[p.f] = s; }
  const order = F.order.map(pfirst).filter(f => NUM[f]);
  return { F, P, NUM, T, SALES, FLAGS, rows, series, FTOT, goal, streak, order, dayKey, idx, isFolio,
    C: Object.fromEntries(P.map(p => [p.f, p.c])), INI: Object.fromEntries(P.map(p => [p.f, p.i])), full: Object.fromEntries(P.map(p => [p.f, p.n])) };
}
const edFmtStd = s => s == null ? "—" : s < 60 ? `${s}s` : s < 3600 ? `${Math.floor(s / 60)}m ${s % 60}s` : `${Math.floor(s / 3600)}h ${Math.floor((s % 3600) / 60)}m`;
const edTalk = s => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
function edLbt(X, cls = "lbt") {
  const COLS = ["Role Play", "Dials", "Avg Talk", "Contact Rate", "Texts / Emails", "Sent the Quote", "HH Quoted", "Prem. Quoted", "HH Sold", "Prem. Sold", "Util.", "Pts"];
  const row = (n) => [n.rp || "—", n.dials, edTalk(n.talk), `${ppct(n.rate)} (${n.live})`, `${n.texts} / ${n.emails}`, n.quoteUp ? `${n.sent} of ${n.quoteUp}` : "—", n.hh, pmoney(n.pq), `${n.hhSold} (${n.pol} pol)`, pmoney(n.ps), n.util != null ? ppct(n.util) : "—", n.pts];
  const T = X.T;
  const trow = [T.rp != null ? Math.round(T.rp) : "—", T.dials, edTalk(T.talk), `${ppct(T.rate)} (${T.live})`, `${T.texts} / ${T.emails}`, T.quoteUp ? `${T.sent} of ${T.quoteUp}` : "—", T.hh, pmoney(T.pq), `${T.hhSold} (${T.pol} pol)`, pmoney(T.ps), T.util != null ? ppct(T.util) : "—", ""];
  return `<div class="scroll"><table class="${cls}"><thead><tr><th>Producer</th>${COLS.map(c => `<th>${c}</th>`).join("")}</tr></thead><tbody>${
    X.order.map(f => `<tr><td><b>${edEsc(X.full[f])}</b></td>${row(X.NUM[f]).map(v => `<td>${v}</td>`).join("")}</tr>`).join("")}<tr class="tot"><td><b>Team</b></td>${trow.map(v => `<td>${v}</td>`).join("")}</tr></tbody></table></div>`;
}
function edAvatar(X, w, size = 40) {
  const c = X.C[w] || "#2a2320", ini = X.INI[w] || w[0];
  return `<span class="av" style="background:${c};color:${typeof badgeTextColor === "function" ? badgeTextColor(c) : "#fff"};width:${size}px;height:${size}px">${edEsc(ini)}${X.streak[w] ? `<span class="st">🔥${X.streak[w]}</span>` : ""}</span>`;
}
function edClip(X, w) {
  // the producer's own coached calls as a short clip: the longest one, as lines
  const calls = X.F.calls.filter(c => pfirst(c.who) === w);
  if (!calls.length) return { lines: [`Apollo: no coached call from ${w} ${X.isFolio ? "this folio" : "today"}.`], call: null };
  const durSecs = c => { const m = /(?:(\d+)m)?\s*(\d+)s/.exec(c.dur || ""); return m ? (+m[1] || 0) * 60 + +m[2] : 0; };
  const c = [...calls].sort((a, b) => durSecs(b) - durSecs(a))[0];
  const raw = String(c.transcript || "").split("\n").filter(l => l.trim() && !/^\[(outbound|inbound)/i.test(l));
  const spoken = raw.filter(l => /\(producer\)|\(lead\)|\(customer\)|^Speaker \d/.test(l)).slice(0, 6);
  const lines = spoken.length ? spoken.map(l => l.replace(/^\[\d+:\d+\]\s*/, "")) : [`${w}: ${raw.join(" ").slice(0, 260)}${raw.join(" ").length > 260 ? "…" : ""}`];
  lines.push(`Apollo: ${c.summary || ""}`);
  return { lines, call: c };
}
const edTx = lines => `<div class="tx">${lines.map((l, j) => { const i = l.indexOf(":"); return `<p class="${j === 0 ? "on" : ""}"><b>${edEsc(i > 0 && i < 40 ? l.slice(0, i) : "")}${i > 0 && i < 40 ? ":" : ""}</b>${edEsc(i > 0 && i < 40 ? l.slice(i + 1) : l)}</p>`; }).join("")}</div>`;
function edNextDay(X) {
  const base = X.dayKey || isoDate(azTodayDate());
  const d = new Date(base + "T12:00:00Z"); do { d.setUTCDate(d.getUTCDate() + 1); } while (d.getUTCDay() === 0 || d.getUTCDay() === 6);
  return pdow(isoDate(d));
}
const edWhen = X => X.isFolio ? "this folio" : pdow(X.dayKey);

/* ===== THE FLORES FEED ===== */
function edPosts(X) {
  const F = X.F, posts = [];
  const top = X.order[0];
  posts.push({ id: "wrap", who: "Apollo", when: `${X.isFolio ? "Folio" : pdow(X.dayKey)} wrap`, pic: true,
    text: `<b>${X.isFolio ? "Folio so far" : "Day closed"}: ${pmoney(F.ps)} in new premium.</b> ${plural(F.pol, "policy", "policies")}, ${F.hhSold} household${F.hhSold === 1 ? "" : "s"}${F.hh ? ` of ${F.hh} quoted, a ${ppct(F.closeHH, 0)} close` : ""}. ${top ? `${top} takes ${X.isFolio ? "the folio" : "the day"} with ${X.NUM[top].pts} points.` : ""}` });
  for (const f of X.order) {
    const n = X.NUM[f]; if (!n.ps) continue;
    const mine = X.SALES.filter(s => s.w === f);
    const call = F.calls.filter(c => pfirst(c.who) === f && (c.flags || []).length)[0];
    posts.push({ id: "s-" + f, who: f, when: "Final · Sale", text: `${plist(mine.map(s => `${s.prod} ${pmoney(s.amt)}`))}${mine.some(s => /winback/i.test(s.src)) ? " 🔁" : mine.some(s => /existing|cross/i.test(s.src)) ? " ➕" : ""}`,
      apollo: call ? `${call.flags[0]}${call.time ? ` (${call.time})` : ""}. ${call.askfix || ""}`.trim() : `${plural(n.hhSold, "household")} closed, ${n.dials} dials, ${ppct(n.rate)} contact rate.` });
  }
  if (F.spBest) posts.push({ id: "sp", who: "Apollo", when: "Speed", text: `${pfirst(F.spBest[0])} dialled a new internet lead in <b>${edFmtStd(F.spBest[1].median)}</b>.${F.spTeam != null ? ` Team median ${edFmtStd(F.spTeam)}; the goal is 2 minutes.` : ""}` });
  if (F.objs[0]) posts.push({ id: "obj", who: "Apollo", when: "Coaching", text: `<span class="lab" style="color:var(--accent)">Flag</span> ${edEsc(F.objs[0][0])} came up ${plural(F.objs[0][1], "time")}, overcome ${F.objs[0][2]}.${/busy|timing/i.test(F.objs[0][0]) ? ' "Is 5 or 6 better, or tomorrow morning?"' : ""}` });
  const quoter = X.order.map(f => X.NUM[f]).filter(n => !n.ps && n.pq).sort((a, b) => b.pq - a.pq)[0];
  if (quoter) posts.push({ id: "q-" + pfirst(quoter.n), who: pfirst(quoter.n), when: "Final · Quoted", text: `${pmoney(quoter.pq)} quoted across ${plural(quoter.hh, "household")}${quoter.pq >= Math.max(...Object.values(X.NUM).map(x => x.pq)) ? ", most on the team" : ""}. Nothing closed yet.`,
    apollo: `${quoter.dials} dials, ${plural(quoter.live, "conversation")}. ${quoter.sent ? `${plural(quoter.sent, "quote")} sent instead of presented.` : "Present on the phone and ask for the sale."}` });
  return posts;
}
function edPostHtml(X, p) {
  const S = edShared.state, rx = S.rx[p.id] || {}, cms = S.cm[p.id] || [];
  const RXS = ["🔥", "👏", "💰", "😬", "🫡"];
  return `<div class="pc" data-post="${p.id}"><div class="whor">${edAvatar(X, p.who)}<div><b>${p.who === "Apollo" ? 'Apollo <span class="ver">✓ coaching</span>' : edEsc(X.full[p.who] || p.who)}</b><small>${edEsc(p.when)}</small></div></div><p>${p.text}</p>
   ${p.pic ? `<div class="pic"><div><div class="lab">Premium sold</div><b>${pmoney(X.F.ps)}</b></div><div style="text-align:right"><div class="lab">Households</div><b>${X.F.hh ? `${X.F.hhSold} of ${X.F.hh}` : X.F.hhSold}</b></div><div style="text-align:right"><div class="lab">Closing</div><b>${X.F.closeHH == null ? "—" : ppct(X.F.closeHH, 0)}</b></div></div>` : ""}
   <div class="rx">${RXS.map(e => { const by = rx[e] || []; return `<button type="button" data-rx="${e}" aria-pressed="${by.includes(edMe())}" title="${edEsc(by.join(", "))}">${e} ${by.length || ""}</button>`; }).join("")}</div>
   <div class="cm">${p.apollo ? `<div class="c">${edAvatar(X, "Apollo", 28)}<div><b>Apollo</b><small>coaching note</small><br>${edEsc(p.apollo)}</div></div>` : ""}${cms.map(c => `<div class="c">${edAvatar(X, pfirst(c.who), 28)}<div><b>${edEsc(c.who)}</b><small>${edEsc(c.at)}</small><br>${edEsc(c.text)}</div></div>`).join("")}
   <form data-cm><input class="t" placeholder="Reply as ${edEsc(edMe())}…" aria-label="Reply" maxlength="300"><button class="ebtn">Post</button></form></div></div>`;
}
function edFeed(X) {
  const S = edShared.state, votes = S.poll || {}, mine = Object.entries(votes).find(([, by]) => by.includes(edMe())), tot = Object.values(votes).reduce((a, b) => a + b.length, 0);
  const F = X.F, done = X.rows.length, bizAll = X.bizAll || done, pace = done ? X.FTOT / done * bizAll : 0;
  const zero = X.rows.filter(r => !r.ps).length;
  return `<div class="feedA"><div class="col">
   <div class="pc"><div class="stories">${["Apollo", ...X.order].map(w => `<button type="button" data-story="${w}"><i class="${edMine.seen[X.dayKey + w] ? "seen" : ""}" style="color:${X.C[w] || "var(--text-primary)"};border-color:${edMine.seen[X.dayKey + w] ? "var(--border-strong)" : (X.C[w] || "var(--text-primary)")}">${X.INI[w] || "A"}</i>${w}</button>`).join("")}</div><p class="note">Tap a story for a clip from their ${X.isFolio ? "folio" : "day"}.</p></div>
   ${edPosts(X).map(p => edPostHtml(X, p)).join("")}</div>
   <div class="col">
    <div class="pc"><h3>Top accounts · ${edEsc(edWhen(X))}</h3>${X.order.map((f, i) => `<div class="trend"><span style="display:flex;align-items:center;gap:10px">${edAvatar(X, f, 32)}${i + 1} · ${edEsc(X.full[f])}</span><b>${X.NUM[f].pts} pts · ${X.NUM[f].pol} pol</b></div>`).join("")}</div>
    <div class="pc"><h3>Poll · who takes ${edEsc(edNextDay(X))}?</h3><div class="poll">${X.order.map(f => { const n = (votes[f] || []).length, pct = tot ? Math.round(100 * n / tot) : 0; return `<button type="button" data-vote="${f}" aria-pressed="${!!mine && mine[0] === f}"><i style="width:${pct}%"></i><span><span>${edEsc(X.full[f])}</span><span>${tot ? pct + "%" : ""}</span></span></button>`; }).join("")}</div><p class="note">${plural(tot, "vote")} · one each · everyone sees the tally</p></div>
    <div class="pc"><h3>Folio · day ${done} of ${bizAll}</h3><div class="prog"><i style="width:${pace ? Math.min(100, X.FTOT / pace * 100) : 0}%"></i></div><div class="hrow"><span class="note">${pmoney(X.FTOT)} so far</span><span class="note">pace ${pmoney(pace)}</span></div><p style="font-size:14px">${zero ? `${plural(zero, "zero day")} so far. ` : ""}${Math.max(0, F.hh - F.hhSold) ? `${plural(Math.max(0, F.hh - F.hhSold), "quoted household")} still open.` : ""}</p></div>
    <div class="pc"><h3>Trending</h3>${F.objs.slice(0, 2).map(o => `<div class="trend"><span>#${edEsc(o[0].replace(/[^A-Za-z]/g, ""))}</span><b>${o[1]}</b></div>`).join("")}${X.SALES.some(s => /winback/i.test(s.src)) ? `<div class="trend"><span>#Winback</span><b>${X.SALES.filter(s => /winback/i.test(s.src)).length}</b></div>` : ""}<div class="trend"><span>#SentTheQuote</span><b>${X.T.sent} of ${X.T.quoteUp}</b></div><div class="trend" style="border:0"><span>#Misfiled</span><b>${F.misfiled}</b></div></div>
   </div></div>
   <div class="pc" style="margin-top:14px"><div class="whor">${edAvatar(X, "Apollo")}<div><b>Apollo <span class="ver">✓</span></b><small>The leaderboard · final</small></div></div>${edLbt(X)}</div>`;
}

/* ===== GRIDIRON ===== */
const edRate = (v, lo, hi) => Math.max(40, Math.min(99, Math.round(40 + 59 * (v - lo) / (hi - lo))));
function edRatings(n) {
  return { SPD: n.std == null ? 55 : edRate(-Math.log(Math.max(1, n.std)), -Math.log(5000), -Math.log(25)), ACC: edRate(n.rate, 0, 20), PWR: edRate(n.ps + n.pq / 4, 0, 4300), STA: edRate(n.dials, 10, 50), IQ: n.rp ? edRate(n.rp, 40, 90) : 45 };
}
const edOvr = n => { const r = edRatings(n); return Math.round((r.SPD + r.ACC + r.PWR * 1.5 + r.STA + r.IQ) / 5.5); };
function edGrid(X) {
  const S = edShared.state, F = X.F, mvp = S.mvp || {}, tally = {}; Object.values(mvp).forEach(w => tally[w] = (tally[w] || 0) + 1);
  const drives = X.SALES.map((s, i) => ({ ...s, i }));
  const quoter = X.order.map(f => X.NUM[f]).filter(n => !n.ps && n.pq).sort((a, b) => b.pq - a.pq)[0];
  const top = X.order[0], topN = X.NUM[top] || {};
  const pos = ["QB · Player of the game", "WR", "RB", "OL", "TE", "K"];
  const injuries = X.order.map(f => X.NUM[f]).flatMap(n => [...(n.open ? [[pfirst(n.n), `${plural(n.open, "task")} open${n.open >= 3 ? " (questionable)" : ""}`]] : []), ...(!n.rp ? [[pfirst(n.n), "no role play"]] : [])]);
  const ballPct = Math.min(90, 10 + 80 * F.ps / (X.goal * 2));
  const recap = `${top ? `${edEsc(X.full[top])} ${topN.ps ? `opened the scoring with ${pmoney(topN.ps)}` : `led the standings with ${topN.pts} points`}` : "Nobody scored"}${F.spBest ? ` and ${pfirst(F.spBest[0]) === top ? "set" : `${pfirst(F.spBest[0])} set`} the speed record at ${edFmtStd(F.spBest[1].median)}` : ""}. ${X.SALES.filter(s => s.w !== top).map(s => `${s.w} converted ${/^[aeiou]/i.test(s.src) ? "an" : "a"} ${(s.src || "sale").toLowerCase()}`).filter((v, i, a) => a.indexOf(v) === i).join(". ")}${X.SALES.filter(s => s.w !== top).length ? ". " : ""}${quoter ? `${edEsc(quoter.n)} moved the ball all ${X.isFolio ? "folio" : "day"}, ${quoter.dials} dials and ${pmoney(quoter.pq)} quoted, and turned it over on downs. ` : ""}${F.objs[0] ? `The ${edEsc(F.objs[0][0])} objection sacked the offence ${plural(F.objs[0][1], "time")}.` : ""}`;
  return `<div class="gi"><div class="sb"><div class="tm">${edAvatar(X, "Apollo", 48)}<div><b>FLORES</b><div style="font-size:12px;color:#9fd3b6">${edEsc(edWhen(X))} · home</div></div><span class="pt">${Math.round(F.ps).toLocaleString()}</span></div><div class="q">FINAL<b>${edEsc(X.isFolio ? "THE FOLIO" : pdow3(X.dayKey).toUpperCase() + " " + pmd(X.dayKey).toUpperCase())}</b>${F.pol} TD · ${F.hhSold} HH</div><div class="tm r"><span class="pt" style="color:#9fd3b6">${X.goal.toLocaleString()}</span><div style="text-align:right"><b>GOAL</b><div style="font-size:12px;color:#9fd3b6">last folio’s average day</div></div></div></div>
   <div class="field"><div class="ez" style="left:0">FLORES</div><div class="ez" style="right:0;background:#3f5f7a">GOAL</div>${[20, 30, 40, 50, 60, 70, 80].map(x => `<div class="yd" style="left:${x}%"><span>${x <= 50 ? x - 10 : 90 - x}</span></div>`).join("")}
    <div class="ball" id="edball" style="left:${ballPct}%;background:${X.C[top] || "#b5532f"}">${edEsc(X.INI[top] || "F")}</div><div class="cap" id="edcap">Click a drive to replay it. Ball at the ${pmoney(F.ps)} yard line: ${Math.round(F.ps / X.goal * 100)}% of the goal${F.ps >= X.goal ? ", covered" : ""}.</div></div>
   <div class="drives">${drives.map(d => `<button type="button" class="drive" data-drive="${d.i}"><b>TD</b><div><strong>${edEsc(X.full[d.w] || d.n)} · ${edEsc(d.prod)}</strong><span>${pmoney(d.amt)}${d.src ? ` · ${edEsc(d.src)}` : ""}</span></div></button>`).join("")}
    ${quoter ? `<button type="button" class="drive" data-drive="x"><b style="color:#f87171">4th</b><div><strong>${edEsc(quoter.n)} · turnover on downs</strong><span>${pmoney(quoter.pq)} quoted, nothing crossed the line</span></div></button>` : ""}${!drives.length && !quoter ? `<div class="drive"><b style="color:#f87171">0</b><div><strong>No drives</strong><span>Nothing was sold or quoted</span></div></div>` : ""}</div>
   <div class="roster">${X.order.map((f, k) => { const n = X.NUM[f], r = edRatings(n); return `<div class="pcard ${k === 0 ? "mvp" : ""} ${edMine.flip[f] ? "flip" : ""}" data-flip="${f}"><div class="in"><div class="f"><div class="ovr"><div><small>OVR</small><b>${edOvr(n)}</b></div><span class="pos">${pos[k] || "ST"}</span></div><div class="ph" style="background:${X.C[f]};color:${typeof badgeTextColor === "function" ? badgeTextColor(X.C[f]) : "#fff"}">${edEsc(X.INI[f])}</div><div class="nm">${edEsc(X.full[f])}</div><div class="rt">${Object.entries(r).map(([k2, v]) => `<span><b>${v}</b>${k2}</span>`).join("")}</div></div>
    <div class="b"><div class="nm" style="color:#ffd27a">${edEsc(X.full[f])} · back</div>${[["Dials", n.dials], ["Contacts", `${n.live} (${ppct(n.rate)})`], ["HH quoted", `${n.hh} · ${pmoney(n.pq)}`], ["Sold", `${n.pol} pol · ${pmoney(n.ps)}`], ["Role play", n.rp || "none"], ["Tasks", n.tasks != null ? `${Math.round(n.tasks)}%${n.open ? ` · ${n.open} open` : ""}` : "—"], ["Speed to dial", n.std == null ? "no new lead" : edFmtStd(n.std)], ["Points", n.pts]].map(([k2, v]) => `<div class="row"><span>${k2}</span><b>${v}</b></div>`).join("")}<div style="margin-top:auto;font-size:11px;color:#a8998c">SPD speed to dial · ACC contact rate · PWR premium · STA dials · IQ role play</div></div></div></div>`; }).join("")}</div>
   <div class="gpan"><div class="box"><h4>Penalties</h4>${X.FLAGS.length ? X.FLAGS.slice(0, 6).map(f => `<div class="gflag"><i></i><div><b>${edEsc(f[0])}</b> · ${edEsc(f[1])}</div></div>`).join("") : "A clean sheet."}</div>
    <div class="box"><h4>Injury report</h4>${injuries.length ? injuries.slice(0, 5).map(f => `<div class="gflag"><i style="background:#f87171"></i><div><b>${edEsc(f[0])}</b> · ${edEsc(f[1])}</div></div>`).join("") : "Everyone healthy."}<h4 style="margin-top:12px">Halftime · the folio</h4>${X.rows.length ? X.rows.map(r => `<div class="vs"><span style="width:60px;font-size:12px">${pmd(r.date)}</span><div class="bar"><i style="width:${Math.max(...X.rows.map(x => x.ps), 1) ? r.ps / Math.max(...X.rows.map(x => x.ps), 1) * 100 : 0}%"></i></div><span style="width:64px;text-align:right;font-size:12px">${pmoney(r.ps)}</span></div>`).join("") : "No folio days yet."}</div>
    <div class="box"><h4>MVP vote</h4><p style="margin:0 0 8px">Pick the player of the game. One vote each; everyone sees the tally.</p>${X.order.map(f => `<button type="button" class="ebtn ${mvp[edMe()] === f ? "" : "q"}" data-mvp="${f}" style="margin:0 6px 6px 0">${f} ${tally[f] ? "· " + tally[f] : ""}</button>`).join("")}<h4 style="margin-top:12px">Game recap</h4>${recap}</div></div>
   <div style="padding:0 26px 22px"><div class="edcard" style="background:#143b2a;border-color:#1f4a35;color:#fff"><h3 style="color:#ffd27a;font:400 22px 'Bebas Neue',Impact,sans-serif;letter-spacing:.08em">Box score</h3>${edLbt(X)}</div></div></div>`;
}

/* ===== THE DRIVE HOME ===== */
function edSegs(X) {
  const F = X.F, top = X.order[0], call = edClip(X, X.order.find(f => X.F.calls.some(c => pfirst(c.who) === f)) || top);
  const o = F.objs[0];
  const carry = (typeof needsNowRows === "function" ? needsNowRows(X.F.d, "") : []).filter(r => r.n);
  return [
    ["🎙️", "0:00", "Cold open", `${pmoney(F.ps)}, ${plural(F.pol, "policy", "policies")}${X.rows.length && F.ps >= Math.max(...X.rows.map(r => r.ps)) && !X.isFolio ? ", the folio’s best day" : ""}`,
      [`Apollo: Good evening, team. ${X.isFolio ? "The folio" : pdow(X.dayKey)} ${X.isFolio ? "stands" : "closed"} at ${pmoney(F.ps)} in new premium. ${plural(F.pol, "policy", "policies")}, ${F.hhSold} of ${F.hh} households quoted.`, top ? `Apollo: ${X.full[top]} takes it with ${X.NUM[top].pts} points.` : "Apollo: nobody took the day."]],
    ["📊", "0:48", "The Scoreboard", `${F.dials} dials, ${F.live} contacts, ${F.hhSold} of ${F.hh} households`,
      [`Apollo: ${F.dials} dials. ${plural(F.live, "conversation")}, a ${ppct(F.rate)} contact rate. ${plural(F.hh, "household")} quoted for ${pmoney(F.pq)}.`, `Apollo: ${F.hhSold} of them bought. ${plural(F.pol, "policy", "policies")}. ${pmoney(F.ps)}.`]],
    ["⏱️", "2:10", "Speed round", F.spBest ? `${pfirst(F.spBest[0])}: ${edFmtStd(F.spBest[1].median)}. Team: ${edFmtStd(F.spTeam)}.` : "No new internet leads",
      F.spBest ? [`Apollo: ${pfirst(F.spBest[0])} had a new lead on the phone in ${edFmtStd(F.spBest[1].median)}.`, `Apollo: the team median was ${edFmtStd(F.spTeam)}. Two minutes is the goal.`] : ["Apollo: no new internet leads arrived, so no speed round tonight."]],
    ["🏆", "3:05", "Call of the Day", call.call ? `${pfirst(call.call.who)} and ${call.call.lead} · ${call.call.dur}` : "No coached calls", call.lines],
    ["👹", "4:30", "Villain of the Day", o ? `${o[0]}: ${o[1]} up, ${o[2]} down` : "No objections raised",
      o ? [`Apollo: the ${o[0]} objection came up ${plural(o[1], "time")} and was overcome ${o[2] ? o[2] + " of them" : "zero times"}. That’s the villain of the day.`, /busy|timing/i.test(o[0]) ? 'Apollo: the move: "Is 5 or 6 better, or tomorrow morning?" A choice between two yeses.' : "Apollo: name it, answer it, and ask for the sale again."] : ["Apollo: a quiet night for the villains."]],
    ["🔢", "7:15", "The Countdown", `${X.order.length} to one, with the sting`,
      [...[...X.order].reverse().map((f, i) => `Apollo: number ${X.order.length - i}, ${f}, ${X.NUM[f].pts} points${X.NUM[f].ps ? ` and ${pmoney(X.NUM[f].ps)}` : ""}.`)]],
    ["📬", "9:40", "Mailbag", "Your notes to Apollo, answered on air", ["Apollo: to the mailbag. Send a note below and tomorrow’s show answers it."]],
    ["🏃", "11:50", "Two-Minute Drill", carry.length ? carry.map(r => `${r.n} ${r.t}`).join(", ") : "Nothing left on the desk",
      carry.length ? carry.map(r => `Apollo: ${r.n} ${r.t}. ${r.sub}.`) : ["Apollo: the desk is clear. Go sell."]],
  ];
}
function edPod(X) {
  const S = edShared.state, mail = S.mail || [], segs = edSegs(X), seg = Math.min(edSeg, segs.length - 1), o = X.F.objs[0];
  const ep = X.isFolio ? "Folio special" : `Episode ${Math.max(1, DAYS.length - DAYS.indexOf(X.dayKey))}`;
  return `<div class="pod"><div class="col"><div class="art" style="background:radial-gradient(circle at 50% 62%,#ffd27a 0,#ffd27a 22%,#e59a6f 23%,#b5532f 60%,#5a2416 100%)"><span>KFLR · The Close</span><div><b>${edEsc(X.isFolio ? "The folio" : pdow3(X.dayKey) + ",")}<br>${edEsc(X.isFolio ? "so far" : pmd(X.dayKey))}</b><div style="margin-top:8px;font-size:14px">${ep} · Apollo</div></div></div>
   <div class="edcard"><div class="player"><button type="button" id="edplay" aria-label="Play">${edPlaying ? "❚❚" : "▶"}</button><div class="wave">${Array.from({ length: 60 }, (_, i) => `<i class="${i <= (seg + 1) * 60 / segs.length ? "on" : ""}" style="height:${20 + Math.round(26 * Math.abs(Math.sin(i * 1.7)))}%"></i>`).join("")}</div><span class="note" id="edpos">${segs[seg][1]} / 14:02</span></div><div class="hrow"><span class="note">Play steps through the segments</span><span class="echip">the board</span></div></div>
   <div class="edcard"><h3>Villain of the Day</h3><div class="hrow"><b style="font:400 24px var(--display)">${o ? `"${edEsc(o[0])}"` : "None"}</b><span class="echip ${o && o[2] < o[1] ? "r" : "g"}">${o ? `${o[1]} up · ${o[2]} down` : "quiet"}</span></div><div class="hp"><i style="width:${o ? Math.round(100 * (o[1] - o[2]) / o[1]) : 0}%"></i></div><p style="margin:0;font-size:14px;line-height:1.5">${o ? `${plural(o[1], "call")} hit it. Health bar at ${Math.round(100 * (o[1] - o[2]) / o[1])}%: ${o[2] ? `${o[2]} landed` : "nobody landed a hit"}.` : "No objections were raised on a coached call."}</p></div>
   <div class="edcard"><h3>The Countdown</h3><div class="cnt">${[...X.order].reverse().map((f, i) => `<div><b>${X.order.length - i}</b><span style="display:flex;align-items:center;gap:8px">${edAvatar(X, f, 28)}${edEsc(X.full[f])}</span><span class="note">${X.NUM[f].pts} pts · ${pmoney(X.NUM[f].ps)}</span></div>`).join("")}</div></div></div>
   <div class="col"><div class="edcard"><div class="hrow"><h2>${ep} · ${edEsc(X.isFolio ? "the folio" : pdow(X.dayKey))}</h2><span class="echip g">Final</span></div><p style="margin:0;font-size:16px;line-height:1.6;max-width:72ch">Same segments every night: the Scoreboard, the Call of the Day, the Villain, the Countdown, the Mailbag, the Two-Minute Drill for tomorrow.</p>
    <div class="segs">${segs.map((s, i) => `<button type="button" data-seg="${i}" class="${i === seg ? "on" : ""}"><span class="ic">${s[0]}</span><span class="t">${s[1]}</span><span><b>${edEsc(s[2])}</b><small>${edEsc(s[3])}</small></span><span class="note">${i === seg ? (edPlaying ? "playing" : "paused") : "▶"}</span></button>`).join("")}</div></div>
   <div class="edcard"><h3>Now playing · ${edEsc(segs[seg][2])}</h3>${edTx(segs[seg][4])}</div>
   <div class="edcard"><div class="hrow"><h3>Mailbag</h3><span class="note">${plural(mail.length, "note")}</span></div><div class="mail">${mail.length ? mail.slice(-6).map(m => `<div class="m"><b>${edEsc(m.who)} · ${edEsc(m.at)}</b>${edEsc(m.text)}</div>`).join("") : '<span class="note">Send Apollo a note. Tomorrow’s Mailbag answers them on air.</span>'}</div>
    <form data-mail style="display:flex;gap:8px"><input class="t" placeholder="Ask Apollo something, ${edEsc(edMe())}…" aria-label="Mailbag" maxlength="300"><button class="ebtn">Send</button></form></div>
   <div class="edcard"><h3>Show notes · the numbers</h3>${edLbt(X)}</div></div></div>`;
}

/* ===== THE CLOSING BELL ===== */
function edSym(X, f) { return (f.slice(0, 4).toUpperCase().padEnd(4, "X")); }
function edChart(X, f) {
  const all = X.series(f), n = all.length;
  const from = edRng === "1d" ? Math.max(0, (X.idx >= 0 ? X.idx : n - 1) - 1) : edRng === "1w" ? Math.max(0, (X.idx >= 0 ? X.idx : n - 1) - 5) : 0;
  const s = all.slice(from), rows = X.rows.slice(from), W = 760, H = 240, pad = 36, max = Math.max(...s, 1), hi = s.length - 1;
  if (s.length < 2) return `<svg viewBox="0 0 ${W} ${H}"><text x="${W / 2}" y="${H / 2}" fill="#9fb0c8" text-anchor="middle" font-size="13">Not enough sessions yet</text></svg>`;
  const x = i => pad + i * (W - pad * 2) / hi, y = v => H - 24 - (v / max) * (H - 60);
  const pts = s.map((v, i) => `${x(i)},${y(v)}`).join(" ");
  const di = (X.idx >= 0 ? X.idx : n - 1) - from, dayChg = di > 0 ? s[di] - s[di - 1] : s[di];
  return `<svg viewBox="0 0 ${W} ${H}"><defs><linearGradient id="edar" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#4ade80" stop-opacity=".35"/><stop offset="1" stop-color="#4ade80" stop-opacity="0"/></linearGradient></defs>
   ${[0, .25, .5, .75, 1].map(fr => `<line x1="${pad}" x2="${W - pad}" y1="${y(max * fr)}" y2="${y(max * fr)}" stroke="#1f2a36"/><text x="${W - pad + 4}" y="${y(max * fr) + 4}" fill="#4b5a6b" font-size="10">${pmoney(max * fr)}</text>`).join("")}
   <polygon points="${x(0)},${y(0)} ${pts} ${x(hi)},${y(0)}" fill="url(#edar)"/><polyline points="${pts}" fill="none" stroke="#4ade80" stroke-width="2.5"/>
   ${s.map((v, i) => { const up = i === 0 ? v > 0 : v > s[i - 1]; return `<circle cx="${x(i)}" cy="${y(v)}" r="${i === di ? 6 : 3}" fill="${up ? "#4ade80" : "#f87171"}" stroke="#0b0f14" stroke-width="2"/>`; }).join("")}
   ${di >= 0 ? `<line x1="${x(di)}" x2="${x(di)}" y1="${y(s[di])}" y2="${H - 24}" stroke="#ffd27a" stroke-dasharray="3 3"/><text x="${x(di)}" y="${y(s[di]) - 12}" fill="#ffd27a" font-size="11" text-anchor="middle">${pdow3(rows[di].date)} ${pmd(rows[di].date)} · ${dayChg >= 0 ? "+" : ""}${pmoney(dayChg)}</text>` : ""}
   ${rows.map((r, i) => `<text x="${x(i)}" y="${H - 6}" fill="#9fb0c8" font-size="10" text-anchor="middle">${r.date.slice(5).replace("-", "/").replace(/^0/, "")}</text>`).join("")}
   <rect x="${W - pad - 62}" y="${y(s[hi]) - 11}" width="62" height="20" rx="4" fill="#4ade80"/><text x="${W - pad - 31}" y="${y(s[hi]) + 3}" fill="#0b0f14" font-size="11" font-weight="700" text-anchor="middle">${Math.round(s[hi]).toLocaleString()}</text></svg>`;
}
function edMkt(X) {
  const F = X.F, di = X.idx >= 0 ? X.idx : X.rows.length - 1;
  const rows = X.order.map(f => { const s = X.series(f), n = X.NUM[f]; return { f, sym: edSym(X, f), last: s[s.length - 1] || 0, chg: X.rows[di] ? (X.rows[di].by[f] || 0) : n.ps, hi: Math.max(...s, 0), open: di > 0 ? s[di - 1] : 0, n }; }).sort((a, b) => b.chg - a.chg);
  const team = { f: "Team", sym: "FLRS", last: X.FTOT, chg: X.rows[di] ? X.rows[di].ps : F.ps, hi: X.FTOT, open: X.FTOT - (X.rows[di] ? X.rows[di].ps : F.ps) };
  const cur = edSel === "FLRS" ? team : (rows.find(r => r.sym === edSel) || team);
  const curF = edSel === "FLRS" ? "FLRS" : cur.f;
  const up = rows.filter(r => r.chg > 0), flat = rows.filter(r => !r.chg);
  const when = X.isFolio ? "this folio" : pdow(X.dayKey);
  return `<div class="mkt"><div class="tape">${[...rows, ...rows].map(r => `<span><b>${r.sym}</b> ${pmoney(r.last)} <span class="${r.chg ? "up" : "fl"}">${r.chg ? "▲" : "■"} ${r.chg ? pmoney(r.chg) : "0.00"}</span></span>`).join("")}<span><b>FLRS</b> ${pmoney(X.FTOT)} <span class="${team.chg ? "up" : "fl"}">${team.chg ? "▲ " + pmoney(team.chg) : "■ 0.00"}</span></span></div>
   <div class="g"><div><div class="hrow"><div><div class="lab" style="color:#9fb0c8">Market close · ${edEsc(X.isFolio ? "the folio so far" : plong(X.dayKey))}</div><h2>FLRS 500</h2></div><div style="text-align:right"><span class="fl">${cur.sym} · ${edEsc(cur.f === "Team" ? "Team" : X.full[cur.f])}</span><div class="up" style="font-size:40px;line-height:1">${Math.round(cur.last).toLocaleString()}</div><span class="${cur.chg ? "up" : "fl"}">${cur.chg ? `▲ +${Math.round(cur.chg).toLocaleString()} (${cur.open ? Math.round(cur.chg / cur.open * 100) + "%" : "new"}) ${edEsc(when)}` : `unchanged ${edEsc(when)}`}</span></div></div>
    <div class="chartbox"><div class="hrow"><div class="rng">${[["1d", "1D"], ["1w", "1W"], ["folio", "FOLIO"]].map(([k, l]) => `<button type="button" data-rng="${k}" aria-pressed="${edRng === k}">${l}</button>`).join("")}</div><span class="fl" style="font-size:12px">price = folio premium to date · open ${pmoney(cur.open)} · folio high ${pmoney(cur.hi)}</span></div>${edChart(X, curF)}</div>
    <div class="scroll" style="margin-top:14px"><table><thead><tr><th></th><th>Sym</th><th>Producer</th><th>Last</th><th>Chg</th><th>HH</th><th>Dials</th><th>Contact</th><th>Quoted</th><th>Util</th><th>RP</th><th>Pts</th><th>Rating</th></tr></thead><tbody>
     <tr class="mk ${edSel === "FLRS" ? "on" : ""}" data-sym="FLRS"><td></td><td class="sym">FLRS</td><td>Team · index</td><td>${pmoney(X.FTOT)}</td><td class="${team.chg ? "up" : "fl"}">${team.chg ? "+" + pmoney(team.chg) : "0.00"}</td><td>${F.hhSold ? "+" + F.hhSold : "0"}</td><td>${F.dials}</td><td>${ppct(F.rate)}</td><td>${pmoney(F.pq)}</td><td>${F.util != null ? ppct(F.util) : "—"}</td><td>${X.T.rp != null ? Math.round(X.T.rp) : "—"}</td><td></td><td class="${F.ps ? "up" : "dn"}">${F.ps ? "BUY" : "HOLD"}</td></tr>
     ${rows.map(r => { const n = r.n; return `<tr class="mk ${edSel === r.sym ? "on" : ""}" data-sym="${r.sym}"><td><button class="star" data-watch="${r.sym}" aria-pressed="${!!edMine.watch[r.sym]}" aria-label="Watch">★</button></td><td class="sym">${r.sym}</td><td>${edEsc(X.full[r.f])}</td><td>${pmoney(r.last)}</td><td class="${r.chg ? "up" : "fl"}">${r.chg ? "+" + pmoney(r.chg) : "0.00"}</td><td>${n.hhSold ? "+" + n.hhSold : "0"}</td><td>${n.dials}</td><td>${ppct(n.rate)}</td><td>${pmoney(n.pq)}</td><td>${n.util != null ? ppct(n.util) : "—"}</td><td>${n.rp || "—"}</td><td class="sym">${n.pts}</td><td class="${r.chg ? "up" : n.pq > 4000 ? "fl" : "dn"}">${r.chg ? "BUY" : n.pq > 4000 ? "HOLD · heavy volume" : "HOLD"}</td></tr>`; }).join("")}</tbody></table></div></div>
   <div class="anal"><h4>Analyst note · Apollo</h4><p>${up.length} of ${rows.length} issues closed up ${edEsc(when)}.${up.map(r => ` ${r.sym} +${pmoney(r.chg)}${X.SALES.filter(s => s.w === r.f).length ? ` on ${plist([...new Set(X.SALES.filter(s => s.w === r.f).map(s => (s.src || "a sale").toLowerCase()))])}` : ""}.`).join("")}${flat.length ? ` ${plist(flat.map(r => r.sym))} flat${flat.some(r => r.n.pq) ? ` on heavy volume: ${pmoney(flat.reduce((a, r) => a + r.n.pq, 0))} quoted between them` : ""}.` : ""}</p>
    <p>The FLRS index is at ${pmoney(X.FTOT)} after ${plural(X.rows.length, "session")}${X.rows.filter(r => !r.ps).length ? ` with ${plural(X.rows.filter(r => !r.ps).length, "zero day")}` : ""}. Catalysts: ${plural(Math.max(0, F.hh - F.hhSold), "quoted household")}, ${F.atRisk} at risk, ${F.misfiled} misfiled.</p>
    <div class="r"><span>Closing ratio</span><b class="${F.closeHH >= 25 ? "up" : "dn"}">${F.closeHH == null ? "—" : ppct(F.closeHH)}</b></div><div class="r"><span>Contact rate</span><b class="${F.rate >= 13 ? "up" : "dn"}">${ppct(F.rate)}</b></div>${F.objs[0] ? `<div class="r"><span>${edEsc(F.objs[0][0])} overcome</span><b class="${F.objs[0][2] ? "up" : "dn"}">${F.objs[0][2]} of ${F.objs[0][1]}</b></div>` : ""}<div class="r"><span>Earnings (folio close)</span><b>${X.folioEnd ? pmd(X.folioEnd) : "—"}</b></div><div class="r" style="border:0"><span>Watchlist</span><b>${Object.keys(edMine.watch).filter(k => edMine.watch[k]).join(" · ") || "tap ★ on a row"}</b></div>
    <h4 style="margin-top:8px">Full board</h4>${edLbt(X, "lbt").replace('class="lbt"', 'class="lbt" style="font-size:12px;min-width:860px"')}</div></div></div>`;
}

/* ===== COLD CALL COMICS ===== */
function edComic(X) {
  const S = edShared.state, F = X.F, likes = S.likes || {};
  const fig = (c, n, x) => `<div class="fig" style="left:${x}"><div class="hd" style="background:${c}"></div><div class="bd" style="background:${c}99"></div><small>${edEsc(n)}</small></div>`;
  const panels = [];
  const timed = [...F.calls].filter(c => c.time).sort((a, b) => feedMins(a.time) - feedMins(b.time));
  const pick = timed.length <= 5 ? timed : [timed[0], timed[Math.floor(timed.length * .25)], timed[Math.floor(timed.length * .5)], timed[Math.floor(timed.length * .75)], timed[timed.length - 1]];
  for (const c of pick) {
    const w = pfirst(c.who), lines = String(c.transcript || "").split("\n").filter(l => l.trim() && !/^\[(outbound|inbound)/i.test(l));
    const prodLine = (lines.find(l => /\(producer\)/.test(l)) || lines[0] || "").replace(/^\[\d+:\d+\]\s*/, "").replace(/^[^:]{0,40}:\s*/, "").slice(0, 90);
    const leadLine = (lines.find(l => /\(lead\)|\(customer\)/.test(l)) || "").replace(/^\[\d+:\d+\]\s*/, "").replace(/^[^:]{0,40}:\s*/, "").slice(0, 60);
    const sent = (Array.isArray(c.sendoff) ? c.sendoff[0] : c.sendoff) === "producer";
    const fx = /sold/i.test(c.catc || "") ? "SOLD!" : c.dur && /^(\d+)s$/.test(c.dur) ? `${c.dur.toUpperCase()}!` : "";
    panels.push({ cap: `${c.time}. ${w} ${c.direction === "call in" ? "takes a call-in" : c.direction === "call back" ? "gets a call back" : "dials"}${c.lead ? ` · ${c.lead}` : ""}.`,
      html: `${prodLine ? `<div class="sbb" style="left:6%;top:8%">${edEsc(prodLine)}${prodLine.length >= 90 ? "…" : ""}</div>` : ""}${leadLine ? `<div class="sbb" style="right:4%;top:44%;max-width:40%">${edEsc(leadLine)}</div>` : ""}${sent ? `<div class="sbb th" style="right:3%;top:2%;max-width:34%;font-size:11px">Apollo: present it, don’t send it…</div>` : ""}${fx ? `<div class="fx" style="left:36%;bottom:30%;font-size:24px">${edEsc(fx)}</div>` : ""}${fig(X.C[w], w, leadLine ? "12%" : "40%")}${leadLine ? fig("#c9b8a8", "Lead", "64%") : ""}` });
  }
  if (F.objs[0]) { const o = F.objs[0]; panels.push({ cap: `BOSS FIGHT. "${o[0]}"`, cls: "boss", html: `<div class="hp" style="position:absolute;left:10%;right:10%;top:10px;background:#fff"><i style="width:${Math.round(100 * (o[1] - o[2]) / o[1])}%"></i></div><div style="position:absolute;left:10%;top:28px;font-weight:700;font-size:12px;color:#fff">HP ${o[1] - o[2]}/${o[1]} · hits landed ${o[2]}</div><div class="mon">${edEsc(o[0].split(" / ")[0].toUpperCase())}</div>${X.order.slice(0, 2).map((f, i) => fig(X.C[f], "", i ? "78%" : "6%")).join("")}` }); }
  const sellers = X.order.filter(f => X.NUM[f].ps).sort((a, b) => X.NUM[b].ps - X.NUM[a].ps);
  if (sellers.length >= 2) { const [a, b] = sellers, na = X.NUM[a], nb = X.NUM[b]; panels.push({ cap: `Final. Back to back: ${a} and ${b} both close.`, cls: "duel", style: `--l:${X.C[a]};--r:${X.C[b]}`, html: `<div class="hpb" style="left:6%"><i style="width:100%"></i></div><div class="lab2" style="left:6%">${edEsc(a.toUpperCase())} · ${pmoney(na.ps)} · ${na.hhSold} HH</div><div class="hpb" style="right:6%"><i style="width:${Math.round(100 * nb.ps / na.ps)}%"></i></div><div class="lab2" style="right:6%">${edEsc(b.toUpperCase())} · ${pmoney(nb.ps)} · ${nb.hhSold} HH</div><div class="vsb">VS</div>${fig(X.C[a], a, "8%")}${fig(X.C[b], b, "70%")}<div class="fx" style="left:38%;bottom:14%;font-size:22px;color:#ffd27a">DUEL!</div>` }); }
  const cross = X.SALES.find(s => /existing|cross/i.test(s.src));
  if (cross) panels.push({ cap: `Final. ${cross.w}’s quiet cross-sell.`, html: `<div class="sbb" style="left:8%;top:10%">While I have you: the ${edEsc(cross.prod.replace(/^.*-/, "").toLowerCase())} isn’t covered yet.</div><div class="fx" style="right:8%;bottom:36%;font-size:26px">+${pmoney(X.SALES.filter(s => s.w === cross.w && /existing|cross/i.test(s.src)).reduce((a, s) => a + s.amt, 0))}</div>${fig(X.C[cross.w], cross.w, "40%")}` });
  if (!F.ps) panels.push({ cap: `${edEsc(edWhen(X))}. Nothing crossed the line.`, cls: "tumble", html: `<div class="tw"></div><div class="fx" style="left:10%;top:14%;font-size:22px">TUMBLEWEED</div>${fig("#c9b8a8", "", "70%")}` });
  panels.push({ cap: `Final.`, cls: "last", html: `<b>${pmoney(F.ps)}</b><span>${plural(F.pol, "policy", "policies")} · ${F.hhSold} of ${F.hh} households${F.closeHH != null ? ` · ${ppct(F.closeHH, 0)} close` : ""}</span><span style="font-size:13px">${X.order.map(f => `${f} ${X.NUM[f].pts}`).join(" · ")}</span><span style="font-size:12px;color:#e59a6f">${F.objs[0] ? `${edEsc(F.objs[0][0])} ${F.objs[0][2]}-for-${F.objs[0][1]}. ` : ""}${F.misfiled} leads misfiled.</span>` });
  return `<div class="comic"><div class="title"><b>COLD CALL COMICS</b><span style="font-weight:700">${edEsc(X.isFolio ? "The folio so far" : plong(X.dayKey))} · drawn by Apollo</span></div>
  <div class="panels">${panels.map((p, i) => { const by = likes[i] || []; return `<div class="panel ${p.cls || ""}"${p.style ? ` style="${p.style}"` : ""}><div class="cap">${edEsc(p.cap)}</div><div class="scene">${p.html}</div><button type="button" class="plike" data-like="${i}" aria-pressed="${by.includes(edMe())}" title="${edEsc(by.join(", "))}">😂 ${by.length || ""}</button></div>`; }).join("")}</div>
  <div style="font-family:var(--body);display:flex;flex-direction:column;gap:12px;border-top:3px solid #2a2320;padding-top:14px"><div class="hrow"><b style="font:400 30px Bangers,Impact,sans-serif;letter-spacing:.04em">THE BOX SCORE</b><span class="lab">final · the whole leaderboard</span></div>${edLbt(X)}</div>
  <p class="note" style="font-family:var(--body)">Running gags come from the data: a duel when two producers close, a boss fight for the objection that cost most, a tumbleweed on a zero day, Apollo’s thought bubble whenever a quote goes by email.</p></div>`;
}

/* ===== CLOSER ===== */
function edCloser(X) {
  const F = X.F, top = X.order[0], n = X.NUM[top] || {}, pickC = edMine.cover || "illus";
  const port = { illus: `<div style="position:absolute;inset:0;background:linear-gradient(180deg,#e8dac9,#c9b8a8)"></div><div class="sil" style="--c:${X.C[top] || "#3f5f7a"}"></div>`,
    desert: `<div style="position:absolute;inset:0;background:linear-gradient(180deg,#f2c9a0 0,#e59a6f 38%,#b5532f 60%,#5a2416 100%)"></div><div style="position:absolute;left:0;right:0;bottom:0;height:34%;background:#2a2320;clip-path:polygon(0 60%,8% 40%,15% 55%,22% 20%,30% 50%,40% 35%,52% 60%,60% 30%,70% 45%,80% 25%,90% 50%,100% 40%,100% 100%,0 100%)"></div>`,
    number: `<div style="position:absolute;inset:0;background:#2a2320"></div><div style="position:absolute;left:14px;top:14px;right:14px;font:800 clamp(80px,14vw,150px)/.85 Fraunces,serif;color:#e59a6f;letter-spacing:-.04em">${Math.round(F.ps).toLocaleString()}</div>` }[pickC];
  const { E } = X.isFolio ? { E: null } : writeDay(F.d);
  const story = E ? E.body : [`${pmoney(F.ps)} in new premium across ${plural(F.pol, "policy", "policies")}.`];
  const heights = [240, 200, 180, 110, 80];
  const podOrder = X.order.length >= 5 ? [X.order[3], X.order[1], X.order[0], X.order[2], X.order[4]] : X.order;
  const podH = X.order.length >= 5 ? [110, 200, 240, 180, 80] : heights.slice(0, X.order.length);
  const podRank = X.order.length >= 5 ? [4, 2, 1, 3, 5] : X.order.map((_, i) => i + 1);
  return `<div class="mag"><div class="cover"><div class="t">CLOSER</div><div class="port">${port}<span style="position:relative">${pickC === "number" ? edEsc(X.isFolio ? "The folio so far" : (X.rows.length && F.ps >= Math.max(...X.rows.map(r => r.ps)) ? "The folio’s best day" : pdow(X.dayKey))) : edEsc(X.full[top] || "The team")}<br><span style="font:700 16px var(--body)">${pickC === "number" ? edEsc(X.isFolio ? "" : plong(X.dayKey)) : `Producer of the ${X.isFolio ? "folio" : "day"} · ${n.pts || 0} points`}</span></span></div>
    <div class="cls"><div><b>${pmoney(F.ps)} ${edEsc(X.isFolio ? "so far" : "on " + pdow(X.dayKey))}</b>${plural(F.pol, "policy", "policies")}, ${plural(F.hhSold, "household")}.</div>${F.objs[0] ? `<div><b>The ${edEsc(F.objs[0][0])} objection</b>${plural(F.objs[0][1], "call")}, ${F.objs[0][2]} overcome.</div>` : `<div><b>${ppct(F.rate)} contact rate</b>${plural(F.dials, "dial")}, ${plural(F.live, "conversation")}.</div>`}<div><b>${F.spBest ? edFmtStd(F.spBest[1].median) : "—"}</b>${F.spBest ? `How fast ${pfirst(F.spBest[0])} dialled a new lead.` : "No new internet leads."}</div><div><b>Folio pace</b>${pmoney(X.FTOT)} after ${plural(X.rows.length, "day")}.</div></div>
    <div class="hrow"><span class="lab">Cover photo</span><div class="seg">${[["illus", "Illustrated portrait"], ["desert", "Sonoran"], ["number", "The number"]].map(([k, l]) => `<button type="button" data-cover="${k}" aria-pressed="${pickC === k}">${l}</button>`).join("")}</div></div></div>
   <div class="spread"><div class="k">Cover story</div><h2>${edEsc(E ? E.hl : `The folio stands at ${pmoney(F.ps)}`)}</h2><p>${edEsc(story[0] || "")}</p>
    <div class="pq">${edEsc(E ? E.pull[0] : (F.objs[0] ? `${F.objs[0][0]} came up ${plural(F.objs[0][1], "time")} this folio.` : "Every dial is a maybe."))}</div>
    ${story.slice(1, 3).map(p => `<p>${edEsc(p)}</p>`).join("")}
    <div class="k" style="margin-top:8px">By the numbers · drawn, not tabled</div>
    <div class="info"><div><b>${pmoney(F.ps)}</b><span>new premium · ${plural(F.pol, "policy", "policies")}</span></div><div><div class="ring" style="--p:${F.closeHH == null ? 0 : Math.min(100, Math.round(F.closeHH))}%"><i>${F.closeHH == null ? "—" : ppct(F.closeHH, 0)}</i></div><span>${F.hhSold} of ${F.hh} households bought</span></div><div><b>${F.spBest ? edFmtStd(F.spBest[1].median) : "—"}</b><span>${F.spBest ? `${pfirst(F.spBest[0])}’s first dial · team ${edFmtStd(F.spTeam)}` : "no new internet leads"}</span></div><div><b>${F.objs[0] ? `${F.objs[0][2]}/${F.objs[0][1]}` : ppct(F.rate)}</b><span>${F.objs[0] ? `${edEsc(F.objs[0][0])} overcome` : "contact rate"}</span></div></div>
    <div class="k" style="margin-top:8px">The podium</div><div class="podium">${podOrder.map((f, i) => `<div><b>${edEsc(f)}</b><small>${X.NUM[f].pts} pts · ${pmoney(X.NUM[f].ps)}</small><div class="blk" style="height:${podH[i]}px;background:${X.C[f]}22;color:${X.C[f]}">${podRank[i]}</div></div>`).join("")}</div>
    <div class="k" style="margin-top:8px">The numbers in full</div>${edLbt(X)}</div></div>`;
}

/* ===== the page ===== */
const ED_R = { feed: edFeed, grid: edGrid, pod: edPod, mkt: edMkt, comic: edComic, closer: edCloser };
let edX = null;
async function editionsPanel(err) {
  const today = isoDate(azTodayDate());
  if (rangeMode === "day") {
    if (!cur) return postGateHtml("No report for this day yet.", "Pick a published day in Day, or choose Folio.");
    if (curLive || (cur.date === today && !DAYS.includes(today))) return postGateHtml("Today's editions come out after the 5:55 PM run.", "Pick a published day in Day, or choose Folio for the folio's editions.");
  } else if (rangeMode !== "folio") return postGateHtml("The editions are made for a published day or a folio.", `${RANGE_LABELS[rangeMode] || "That range"} is on the Digest. Pick a published day in Day, or choose Folio.`);
  else if (err) return postGateHtml("Nothing to print yet.", cesc(err));
  const isFolio = rangeMode === "folio";
  const day = isFolio ? null : cur.date;
  const curEnd = folioEndFor(today), end = isFolio ? (folioPick || curEnd) : folioEndFor(day), start = folioStartFor(end) || "";
  let docs;
  if (isFolio) docs = [...curRangeDocs];
  else { if (!postCache.fdocs || postCache.fdocsKey !== end + day) { postCache.fdocs = await fetchRangeDocs(start, day); postCache.fdocsKey = end + day; } docs = postCache.fdocs; }
  docs = docs.filter(x => x && x.date).sort((a, b) => a.date.localeCompare(b.date));
  const rows = docs.map(x => { const f = postFacts(x); const by = {}; for (const p of f.prods) by[pfirst(p.name)] = +p.ps || 0; return { date: x.date, ps: f.ps, by }; });
  const last = await lastFolioTotal(end);
  const X = edFacts(isFolio ? cur : cur, rows, last, isFolio);
  X.folioEnd = end; X.bizAll = rows.length + pbizDays(start || rows[0]?.date || today, end).filter(d => d > (rows.length ? rows[rows.length - 1].date : "")).length;
  const key = isFolio ? `folio-${end}` : day;
  await edLoadShared(key);
  edX = X;
  return `<div class="ed"><div class="subtabs edtabs">${ED_PUBS.map(([k, l]) => `<button type="button" class="subtab ${k === edPub ? "sel" : ""}" data-pub="${k}">${l}</button>`).join("")}</div><div id="edbody">${ED_R[edPub](X)}</div></div>`;
}
function edRepaint() { const b = $("#edbody"); if (b && edX) b.innerHTML = ED_R[edPub](edX); }
function edOpenModal(h) { edCloseModal(); const m = document.createElement("div"); m.className = "edmodal ed"; m.id = "edmodal"; m.innerHTML = `<div class="edcard">${h}</div>`; m.addEventListener("click", e => { if (e.target === m) edCloseModal(); }); document.body.appendChild(m); }
function edCloseModal() { const m = $("#edmodal"); if (m) m.remove(); }
document.addEventListener("click", async e => {
  if (view !== "editions" || !edX) return;
  const t = e.target, d = k => t.closest(`[data-${k}]`); let el;
  if (el = d("pub")) { edPub = el.dataset.pub; try { localStorage.setItem("board-edition", edPub); } catch (_) {} clearInterval(edTick); edPlaying = false; paint(); return; }
  if (el = d("rx")) { const id = el.closest("[data-post]").dataset.post; if (await edPost("rx", { id, emoji: el.dataset.rx })) edRepaint(); return; }
  if (el = d("story")) { const w = el.dataset.story; edMine.seen[edX.dayKey + w] = 1; edSaveMine(); const clip = w === "Apollo" ? { lines: edSegs(edX)[0][4].concat(edSegs(edX)[1][4]), call: null } : edClip(edX, w);
    edOpenModal(`<div class="hrow"><h3>${edEsc(w)}’s story</h3><button type="button" class="ebtn q" data-edclose>Close</button></div>${edTx(clip.lines)}${clip.call ? `<button type="button" class="ebtn q" data-edcard="${edX.F.calls.indexOf(clip.call)}">Open the coaching card</button>` : ""}`); edRepaint(); return; }
  if (el = d("edclose")) { edCloseModal(); return; }
  if (el = d("edcard")) { const c = edX.F.calls[+el.dataset.edcard]; edCloseModal(); if (c) openCoachingCard(c); return; }
  if (el = d("vote")) { if (await edPost("poll", { choice: el.dataset.vote })) edRepaint(); return; }
  if (el = d("drive")) { const i = el.dataset.drive, ball = $("#edball"), cap = $("#edcap"); if (!ball) return;
    if (i === "x") { const q = edX.order.map(f => edX.NUM[f]).filter(n => !n.ps && n.pq).sort((a, b) => b.pq - a.pq)[0]; ball.style.left = "46%"; ball.style.background = edX.C[pfirst(q.n)]; ball.textContent = edX.INI[pfirst(q.n)]; cap.textContent = `${q.n}: ${q.dials} dials and ${pmoney(q.pq)} quoted drove to midfield, then turned it over on downs.`; }
    else { const s = edX.SALES[+i]; ball.style.left = Math.min(90, 10 + 80 * s.amt / edX.goal * 0.5) + "%"; ball.style.background = edX.C[s.w]; ball.textContent = edX.INI[s.w]; cap.textContent = `${edX.full[s.w]}: ${s.prod} for ${pmoney(s.amt)}${s.src ? `, ${s.src.toLowerCase()}` : ""}. Touchdown.`; setTimeout(() => { ball.style.left = "92%"; }, 850); }
    return; }
  if (el = d("flip")) { const f = el.dataset.flip; edMine.flip[f] = !edMine.flip[f]; edSaveMine(); el.classList.toggle("flip"); return; }
  if (el = d("mvp")) { if (await edPost("mvp", { choice: el.dataset.mvp })) { edRepaint(); edToast("Vote counted: " + el.dataset.mvp); } return; }
  if (el = d("seg")) { edSeg = +el.dataset.seg; edRepaint(); return; }
  if (t.id === "edplay") { edPlaying = !edPlaying; clearInterval(edTick); if (edPlaying) edTick = setInterval(() => { if (view !== "editions" || edPub !== "pod") { clearInterval(edTick); edPlaying = false; return; } edSeg = (edSeg + 1) % 8; edRepaint(); }, 6000); edRepaint(); return; }
  if (el = d("rng")) { edRng = el.dataset.rng; edRepaint(); return; }
  if (el = d("watch")) { edMine.watch[el.dataset.watch] = !edMine.watch[el.dataset.watch]; edSaveMine(); edRepaint(); return; }
  if (el = d("sym")) { edSel = el.dataset.sym; edRepaint(); return; }
  if (el = d("like")) { if (await edPost("like", { panel: el.dataset.like })) edRepaint(); return; }
  if (el = d("cover")) { edMine.cover = el.dataset.cover; edSaveMine(); edRepaint(); return; }
});
document.addEventListener("submit", async e => {
  if (view !== "editions" || !edX) return;
  const f = e.target; if (!f.hasAttribute("data-cm") && !f.hasAttribute("data-mail")) return;
  e.preventDefault(); const inp = f.querySelector("input"), text = inp.value.trim(); if (!text) return;
  if (f.hasAttribute("data-cm")) { if (await edPost("cm", { id: f.closest("[data-post]").dataset.post, text })) edRepaint(); }
  else if (await edPost("mail", { text })) { edRepaint(); edToast("Sent to tomorrow’s Mailbag"); }
});
