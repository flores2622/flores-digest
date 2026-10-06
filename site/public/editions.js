/* The editions (Frank, 2026-10-01: "all of them, go to production") ----------
   Six ways to read a published day or a folio, each with its own mechanic,
   all drawn from the same day documents as the Digest and The Flores Post:
     The Flores Feed   a social timeline: stories, reactions, comments, a poll
     Fourth and Goal   a football game: scoreboard, drives, player cards, MVP vote
     KFLR The Close    a podcast: segments, the Villain, the Countdown, the Mailbag
     FLRS 500          a market close: producers as stocks priced on folio premium
     Cold Call Comics  a comic strip: the day's story, its turning points in order
     CLOSER            a magazine: cover, cover story, drawn infographic, podium
   Every one carries the leaderboard and real figures. What people do on them
   (reactions, comments, poll and MVP votes, mailbag notes, panel likes) is
   shared through the Worker's /api/editions/<key> and kept in R2, so everyone
   sees the same tally; the viewer's own picks (watchlist, cover photo, card
   flips) stay in their browser. Nothing here is paid for. */

(function () {
  const css = `.ed .edtabs { display: flex; gap: 6px; flex-wrap: wrap; margin: 0 0 16px; align-items: center; }
.ed .eddl { margin-left: auto; display: flex; gap: 6px; } .ed .eddl .ebtn { padding: 7px 12px; }
.ed .edcard { background: var(--surface-raised); border: var(--bw) solid var(--border-strong); border-radius: var(--rad); box-shadow: var(--shadow); padding: 20px; display: flex; flex-direction: column; gap: 12px; min-width: 0; }
.ed .edcard h2, .ed .edcard h3 { margin: 0; border: 0; padding: 0; text-transform: none; letter-spacing: 0; }
.ed .edcard h2 { font-size: 26px; }
.ed .edcard h3 { font: 400 20px var(--display); }
.ed .hrow { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.ed .lab { font-size: 11px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; color: var(--text-muted); }
.ed .note { font-size: 13px; color: var(--text-muted); margin: 0; }
.ed .echip { display: inline-block; font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 999px; background: var(--chip); }
.ed .echip.g { background: var(--goodbg); color: var(--good); }
.ed .echip.r { background: var(--badbg); color: var(--bad); }
.ed .ebtn { border: 0; border-radius: 10px; padding: 9px 14px; font: 700 13px var(--body); background: var(--accent); color: #fff; cursor: pointer; }
.ed .ebtn.q { background: var(--chip); color: var(--text-primary); }
.ed input.t { font: 500 14px var(--body); padding: 9px 11px; border: 1.5px solid var(--border-strong); border-radius: 10px; background: var(--surface-raised); color: var(--text-primary); width: 100%; min-width: 0; }
.ed .av { width: 40px; height: 40px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font: 700 13px var(--body); flex: none; position: relative; }
.ed .av .st { position: absolute; right: -6px; bottom: -6px; background: var(--surface-raised); border: 2px solid var(--surface-raised); border-radius: 999px; font-size: 10px; padding: 1px 5px; color: var(--accent-d); font-weight: 800; }
.ed table.lbt { width: 100%; border-collapse: collapse; font-size: 13.5px; }
.ed table.lbt.mktlb { font-size: 12px; }
.ed table.lbt th { font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--text-muted); text-align: right; padding: 8px 6px; border-bottom: 2px solid var(--text-primary); white-space: nowrap; }
.ed table.lbt td { text-align: right; padding: 9px 6px; border-bottom: 1px solid var(--grid); white-space: nowrap; font-size: 13.5px; }
.ed table.lbt th:first-child, .ed table.lbt td:first-child { text-align: left; }
.ed table.lbt tr.tot td { border-top: 2px solid var(--text-primary); font-weight: 800; background: transparent; }
.ed .scroll { border: 0; }
.ed .scroll table { background: transparent; }
.edtoast { position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%); background: var(--side); color: var(--sideInk); padding: 10px 16px; border-radius: 999px; font-size: 13px; z-index: 70; opacity: 0; transition: opacity .25s; pointer-events: none; }
.edtoast.on { opacity: 1; }
/* Feed */
.ed .feedA { display: grid; grid-template-columns: minmax(0, 700px) minmax(0, 1fr); gap: 20px; }
.ed .col { display: flex; flex-direction: column; gap: 14px; min-width: 0; }
.ed .pc { background: var(--surface-raised); border: var(--bw) solid var(--border-strong); border-radius: 18px; padding: 16px 18px; display: flex; flex-direction: column; gap: 10px; box-shadow: var(--shadow); }
.ed .pc h3 { margin: 0; font: 400 20px var(--display); border: 0; padding: 0; text-transform: none; letter-spacing: 0; }
.ed .pc p { margin: 0; font-size: 16px; line-height: 1.5; }
.ed .whor { display: flex; align-items: center; gap: 12px; }
.ed .whor b { display: block; font-size: 15px; }
.ed .whor small { color: var(--text-muted); font-size: 12px; }
.ed .whor .ver { color: var(--good); font-size: 12px; margin-left: 4px; }
.ed .hdl { color: var(--accent); font-weight: 700; }
.ed .cheer { font: 700 9.5px var(--body); letter-spacing: .06em; text-transform: uppercase; background: var(--chip, #efe6da); color: var(--text-muted); border-radius: 999px; padding: 1px 6px; cursor: help; }
.ed .pic { border-radius: 14px; background: var(--card2); padding: 16px; display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; }
.ed .pic b { font: 400 36px var(--display); color: var(--good); }
.ed .rx { display: flex; gap: 6px; flex-wrap: wrap; }
.ed .rx button { border: 1.5px solid var(--border-strong); background: var(--card2); border-radius: 999px; padding: 4px 10px; font: 500 13px var(--body); color: var(--text-primary); cursor: pointer; }
.ed .rx button[aria-pressed="true"] { border-color: var(--accent); background: color-mix(in oklab, var(--accent) 14%, var(--surface-raised)); font-weight: 800; }
.ed .cm { display: flex; flex-direction: column; gap: 8px; border-top: 1px solid var(--grid); padding-top: 8px; }
.ed .cm .c { display: flex; gap: 10px; align-items: flex-start; font-size: 14px; line-height: 1.45; }
.ed .cm .c b { font-size: 13px; }
.ed .cm .c small { color: var(--text-muted); margin-left: 6px; }
.ed .cm form { display: flex; gap: 8px; }
/* GIFs and memes (Frank, 2026-10-01: "add GIF's and memes to the flores feed").
   The reaction GIFs are drawn in CSS so nothing leaves the board; a pasted
   Giphy / Tenor / .gif link shows as the picture. Memes are Apollo's,
   written in rules from the day. */
.ed .gif { display: inline-flex; align-items: center; justify-content: center; width: 150px; height: 100px; border-radius: 12px; background: var(--card2); font-size: 40px; position: relative; overflow: hidden; line-height: 1; }
.ed .gif i { font-style: normal; display: inline-block; position: relative; }
.ed .gif small { position: absolute; left: 0; right: 0; bottom: 6px; font: 800 10px/1 var(--body); letter-spacing: .1em; text-transform: uppercase; color: var(--text-muted); text-align: center; }
.ed .gifpick { display: flex; flex-wrap: wrap; gap: 8px; padding: 6px 0 2px; }
.ed .gifpick button { border: 1.5px solid var(--border-strong); background: var(--card2); border-radius: 12px; padding: 0; cursor: pointer; }
.ed .gifpick button:hover { border-color: var(--accent); }
.ed .gifpick .gif { width: 96px; height: 70px; font-size: 28px; }
.ed .gifimg { max-width: 260px; max-height: 220px; border-radius: 12px; display: block; margin-top: 4px; }
.ed .g-fire i { animation: edflk .5s infinite alternate; } .ed .g-fire i:nth-child(2) { animation-delay: .17s; font-size: 52px; } .ed .g-fire i:nth-child(3) { animation-delay: .33s; }
@keyframes edflk { from { transform: scaleY(.9) translateY(3px); } to { transform: scaleY(1.1) translateY(-4px); } }
.ed .g-clap i { animation: edclap .55s infinite alternate ease-in-out; } @keyframes edclap { from { transform: scale(.85) rotate(-8deg); } to { transform: scale(1.15) rotate(8deg); } }
.ed .g-money i { position: absolute; top: -40px; animation: edfall 1.6s linear infinite; } .ed .g-money i:nth-child(1) { left: 14%; } .ed .g-money i:nth-child(2) { left: 42%; animation-delay: .5s; } .ed .g-money i:nth-child(3) { left: 70%; animation-delay: 1s; }
@keyframes edfall { to { transform: translateY(150px) rotate(25deg); } }
.ed .g-crickets i { animation: edhop 1.2s infinite; } .ed .g-crickets small { animation: eddots 1.5s steps(4) infinite; }
@keyframes edhop { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-10px); } }
@keyframes eddots { from { opacity: .2; } to { opacity: 1; } }
.ed .g-confetti i:first-child { animation: edpop .9s infinite alternate; } .ed .g-confetti b { position: absolute; width: 8px; height: 8px; border-radius: 2px; top: -10px; animation: edfall 1.4s linear infinite; }
@keyframes edpop { from { transform: scale(.9) rotate(-10deg); } to { transform: scale(1.15) rotate(10deg); } }
.ed .g-facepalm i { animation: edshake .7s infinite; } @keyframes edshake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-5px) rotate(-4deg); } 75% { transform: translateX(5px) rotate(4deg); } }
.ed .g-rocket i { animation: edlaunch 1.8s ease-in infinite; } @keyframes edlaunch { 0% { transform: translate(-40px, 30px); opacity: 0; } 15% { opacity: 1; } 100% { transform: translate(50px, -50px); opacity: 0; } }
.ed .g-mic i { animation: eddrop 1.6s cubic-bezier(.5, 0, 1, 1) infinite; } @keyframes eddrop { 0% { transform: translateY(-30px) rotate(0); } 60% { transform: translateY(18px) rotate(90deg); } 75% { transform: translateY(8px) rotate(90deg); } 100% { transform: translateY(18px) rotate(90deg); } }
.ed .g-fine { background: linear-gradient(180deg, #ffb27e, #d9622b); } .ed .g-fine i:nth-child(3), .ed .g-fine i:nth-child(1) { animation: edflk .4s infinite alternate; }
.ed .g-stonks { background: linear-gradient(180deg, #dbe9ff, #9ec1ff); } .ed .g-stonks i:first-child { animation: edrise 1.8s ease-out infinite; } @keyframes edrise { 0% { transform: translateY(14px) scale(.8); opacity: .4; } 100% { transform: translateY(-12px) scale(1.1); opacity: 1; } }
.ed .g-slow i { animation: edcrawl 4s linear infinite; } @keyframes edcrawl { from { transform: translateX(-60px); } to { transform: translateX(60px); } }
.ed .meme { border-radius: 14px; overflow: hidden; border: 2px solid #111; background: #111; max-width: 520px; }
.ed .meme .mimg { position: relative; container-type: inline-size; background: #222; }
.ed .meme .mimg img { display: block; width: 100%; height: 100%; }
.ed .meme .mbox { position: absolute; display: flex; align-items: center; justify-content: center; text-align: center; padding: 0 1.5cqw; box-sizing: border-box; line-height: 1.05; overflow: hidden; }
.ed .meme .mbox.w { color: #fff; font-family: Impact, "Anton", "Arial Black", "Helvetica Neue", sans-serif; text-transform: uppercase; letter-spacing: .02em; -webkit-text-stroke: .5cqw #000; paint-order: stroke fill; text-shadow: .3cqw .3cqw 0 #000, -.3cqw -.3cqw 0 #000, .3cqw -.3cqw 0 #000, -.3cqw .3cqw 0 #000; }
.ed .meme .mbox.t { align-items: flex-start; } .ed .meme .mbox.b { align-items: flex-end; }
.ed .meme .mbox.d { color: #111; font: 700 1em Arial, "Helvetica Neue", sans-serif; padding: 0 3cqw; }
.ed .meme .cap { background: #111; color: #cfc6ba; font: 600 12px var(--body); padding: 6px 12px 2px; }
.ed .meme .mname { background: #111; color: #8f867b; font: 600 10.5px var(--body); letter-spacing: .08em; text-transform: uppercase; padding: 0 12px 7px; }
.ed .stories { display: flex; gap: 14px; overflow: auto; padding: 2px; }
.ed .stories button { width: 72px; flex: none; text-align: center; font: 500 12px var(--body); border: 0; background: none; color: inherit; cursor: pointer; }
.ed .stories i { display: flex; align-items: center; justify-content: center; width: 62px; height: 62px; border-radius: 50%; margin: 0 auto 4px; border: 3px solid var(--accent); background: var(--surface-raised); font-weight: 800; font-style: normal; }
.ed .stories i.seen { border-color: var(--border-strong); }
.ed .poll { display: flex; flex-direction: column; gap: 8px; }
.ed .poll button { position: relative; text-align: left; border: 1.5px solid var(--border-strong); background: var(--card2); border-radius: 10px; padding: 10px 12px; font: 500 14px var(--body); color: var(--text-primary); overflow: hidden; cursor: pointer; }
.ed .poll button i { position: absolute; left: 0; top: 0; bottom: 0; background: color-mix(in oklab, var(--accent) 16%, transparent); z-index: 0; }
.ed .poll button span { position: relative; display: flex; justify-content: space-between; }
.ed .poll button[aria-pressed="true"] { border-color: var(--accent); font-weight: 800; }
.ed .trend { display: flex; justify-content: space-between; align-items: center; font-size: 15px; padding: 8px 0; border-bottom: 1px solid var(--grid); gap: 10px; }
.ed .prog { height: 12px; border-radius: 6px; background: var(--chip); overflow: hidden; }
.ed .prog i { display: block; height: 100%; background: var(--good); }
.edmodal { position: fixed; inset: 0; background: rgba(0,0,0,.55); display: flex; align-items: center; justify-content: center; z-index: 80; padding: 20px; }
.edmodal .edcard { width: min(680px, 100%); max-height: 85vh; overflow: auto; }
.ed .tx p { margin: 0; font-size: 15px; line-height: 1.55; padding: 6px 8px; border-radius: 8px; }
.ed .tx p.on { background: color-mix(in oklab, var(--accent) 12%, transparent); }
.ed .tx p b { color: var(--accent-d); }
/* Fourth and Goal */
.ed .gi { background: #0f2a1e; color: #fff; border-radius: 20px; overflow: hidden; box-shadow: var(--shadow); display: flex; flex-direction: column; }
.ed .gi .sb { background: #071a12; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; padding: 14px 26px; gap: 16px; border-bottom: 4px solid #ffd27a; }
.ed .gi .tm { display: flex; align-items: center; gap: 14px; }
.ed .gi .tm b { font: 400 44px/1 'Bebas Neue', Impact, sans-serif; letter-spacing: .06em; }
.ed .gi .tm .pt { font: 400 64px/1 'Bebas Neue', Impact, sans-serif; color: #ffd27a; }
.ed .gi .q { text-align: center; font: 400 20px 'Bebas Neue', Impact, sans-serif; letter-spacing: .14em; color: #9fd3b6; }
.ed .gi .q b { display: block; font-size: 34px; color: #fff; }
.ed .gi .tm.r { justify-content: flex-end; }
.ed .field { position: relative; height: 220px; background: repeating-linear-gradient(90deg, #1d6b3d 0 10%, #237a46 10% 20%); border-top: 3px solid #fff; border-bottom: 3px solid #fff; overflow: hidden; }
.ed .field .yd { position: absolute; top: 0; bottom: 0; width: 2px; background: rgba(255,255,255,.5); }
.ed .field .yd span { position: absolute; top: 8px; left: 6px; font: 400 14px 'Bebas Neue', Impact, sans-serif; color: #fff; opacity: .8; }
.ed .field .ez { position: absolute; top: 0; bottom: 0; width: 10%; background: #b5532f; display: flex; align-items: center; justify-content: center; font: 400 28px 'Bebas Neue', Impact, sans-serif; letter-spacing: .3em; writing-mode: vertical-rl; color: #fff; }
.ed .field .ball { position: absolute; top: 50%; transform: translate(-50%, -50%); width: 44px; height: 44px; border-radius: 50%; border: 3px solid #fff; display: flex; align-items: center; justify-content: center; font: 700 12px var(--body); color: #fff; box-shadow: 0 6px 16px rgba(0,0,0,.4); transition: left .8s cubic-bezier(.3,.8,.3,1); }
.ed .field .cap { position: absolute; left: 12px; right: 12px; bottom: 10px; font-size: 13px; background: rgba(0,0,0,.55); padding: 6px 10px; border-radius: 8px; }
.ed .drives { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; padding: 18px 26px; }
.ed .drive { background: #143b2a; border-radius: 12px; padding: 12px 14px; display: flex; gap: 12px; align-items: center; cursor: pointer; border: 2px solid transparent; text-align: left; color: #fff; font: inherit; }
.ed .drive:hover { border-color: #ffd27a; }
.ed .drive b { font: 400 26px/1 'Bebas Neue', Impact, sans-serif; color: #ffd27a; min-width: 70px; }
.ed .drive span { font-size: 13px; color: #cfe6d8; }
.ed .drive strong { font-size: 15px; display: block; color: #fff; }
.ed .roster { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; padding: 0 26px 18px; }
.ed .pcard { perspective: 900px; height: 300px; border: 0; padding: 0; background: none; }
.ed .pcard .in { position: relative; width: 100%; height: 100%; transition: transform .6s; transform-style: preserve-3d; cursor: pointer; }
.ed .pcard.flip .in { transform: rotateY(180deg); }
.ed .pcard .f, .ed .pcard .b { position: absolute; inset: 0; backface-visibility: hidden; border-radius: 14px; padding: 12px; display: flex; flex-direction: column; gap: 6px; color: #2a2320; }
.ed .pcard .f { background: linear-gradient(160deg, #fffaf3, #e8dac9); border: 3px solid #ffd27a; }
.ed .pcard .b { background: #1b1613; color: #f3e9dc; transform: rotateY(180deg); border: 3px solid #ffd27a; font-size: 12px; }
.ed .pcard .ovr { display: flex; justify-content: space-between; align-items: center; }
.ed .pcard .ovr b { font: 400 44px/1 'Bebas Neue', Impact, sans-serif; color: #b5532f; }
.ed .pcard .ovr small { font-size: 10px; letter-spacing: .12em; text-transform: uppercase; color: #6e5f53; }
.ed .pcard .nm { font: 400 18px var(--display); }
.ed .pcard .pos { font-size: 11px; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: #6e5f53; }
.ed .pcard .ph { height: 84px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font: 400 34px var(--display); }
.ed .pcard .rt { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px; font-size: 10px; text-align: center; }
.ed .pcard .rt span { background: rgba(42,35,32,.06); border-radius: 5px; padding: 4px 0; }
.ed .pcard .rt b { display: block; font: 800 14px var(--body); }
.ed .pcard .b .row { display: flex; justify-content: space-between; border-bottom: 1px solid #3a302b; padding: 4px 0; }
.ed .pcard.mvp .f { background: linear-gradient(160deg, #ffe7a3, #e59a6f); border-color: #b5532f; }
.ed .gpan { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; padding: 0 26px 22px; }
.ed .gpan .box { background: #143b2a; border-radius: 12px; padding: 14px; font-size: 14px; line-height: 1.5; }
.ed .gpan .box h4 { margin: 0 0 6px; font: 400 22px 'Bebas Neue', Impact, sans-serif; letter-spacing: .08em; color: #ffd27a; }
.ed .gflag { display: flex; gap: 10px; align-items: flex-start; padding: 6px 0; border-bottom: 1px solid #1f4a35; }
.ed .gflag i { width: 14px; height: 18px; background: #ffd27a; clip-path: polygon(0 0, 100% 0, 70% 50%, 100% 100%, 0 100%); flex: none; margin-top: 2px; }
.ed .vs { display: flex; gap: 10px; align-items: center; }
.ed .vs .bar { flex: 1; height: 10px; background: #0b2318; border-radius: 5px; overflow: hidden; }
.ed .vs .bar i { display: block; height: 100%; background: #ffd27a; }
.ed .gi .lbt, .ed .gi .lbt td, .ed .gi .lbt th { color: #fff; }
.ed .gi .lbt th { color: #9fd3b6; border-color: #ffd27a; }
.ed .gi .lbt td { border-color: #1f4a35; }
.ed .gi .lbt tr.tot td { border-color: #ffd27a; }
/* KFLR The Close */
.ed .pod { display: grid; grid-template-columns: 400px minmax(0, 1fr); gap: 20px; align-items: start; }
.ed .pod .playlist { grid-column: 1 / -1; }
.ed .art { aspect-ratio: 1; border-radius: 20px; color: #fff; padding: 24px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: var(--shadow); }
.ed .art b { font: 400 40px/1 var(--display); }
.ed .art span { font-size: 12px; letter-spacing: .12em; text-transform: uppercase; font-weight: 800; }
.ed .player { display: flex; align-items: center; gap: 14px; }
.ed .player > button { width: 56px; height: 56px; border-radius: 50%; border: 0; background: var(--accent); color: #fff; font-size: 22px; flex: none; cursor: pointer; }
.ed .wave { flex: 1; height: 48px; display: flex; align-items: center; gap: 3px; }
.ed .wave i { flex: 1; background: var(--chip); border-radius: 2px; }
.ed .wave i.on { background: var(--accent); }
.ed .segs { display: flex; flex-direction: column; }
.ed .segs button { display: grid; grid-template-columns: 44px 60px 1fr auto; gap: 12px; align-items: center; text-align: left; border: 0; background: none; padding: 12px 6px; border-bottom: 1px solid var(--grid); color: inherit; font: inherit; cursor: pointer; }
.ed .segs button:hover, .ed .segs button.on { background: var(--card2); }
.ed .segs .ic { width: 40px; height: 40px; border-radius: 12px; background: var(--chip); display: flex; align-items: center; justify-content: center; font-size: 18px; }
.ed .segs .t { font-size: 13px; color: var(--text-muted); }
.ed .segs b { font-size: 16px; }
.ed .segs small { display: block; color: var(--text-muted); font-size: 13px; font-weight: 400; }
.ed .hp { height: 14px; border-radius: 7px; background: var(--badbg); overflow: hidden; border: 1.5px solid var(--accent); }
.ed .hp i { display: block; height: 100%; background: var(--accent); }
.ed .cnt { display: flex; flex-direction: column; gap: 6px; }
.ed .cnt div { display: grid; grid-template-columns: 50px 1fr auto; gap: 10px; align-items: center; padding: 8px 10px; border-radius: 10px; background: var(--card2); }
.ed .cnt div b { font: 400 30px/1 var(--display); color: var(--accent); }
.ed .mail { display: flex; flex-direction: column; gap: 8px; }
.ed .mail .m { background: var(--card2); border-radius: 12px; padding: 10px 12px; font-size: 14px; line-height: 1.45; }
.ed .mail .m b { display: block; font-size: 12px; color: var(--text-muted); margin-bottom: 2px; }
/* FLRS 500 */
.ed .mkt { background: #0b0f14; color: #e8edf2; border-radius: 20px; overflow: hidden; box-shadow: var(--shadow); font-family: 'JetBrains Mono', ui-monospace, monospace; }
.ed .tape { background: #111820; padding: 8px 0; white-space: nowrap; overflow: hidden; font-size: 14px; border-bottom: 1px solid #1f2a36; }
.ed .tape span { margin-right: 36px; }
.ed .up { color: #4ade80; }
.ed .dn { color: #f87171; }
.ed .fl { color: #9fb0c8; }
.ed .mkt .g { display: grid; grid-template-columns: minmax(0, 1fr) 420px; gap: 22px; padding: 22px 26px; }
.ed .mkt .mktfull { padding: 0 26px 24px; } .ed .mkt .mktfull h4 { margin: 0 0 8px; font: 400 20px var(--display); color: #e8edf2; }
.ed .mkt .mktfull .lbt, .ed .mkt .mktfull .lbt td { color: #e8edf2; } .ed .mkt .mktfull .lbt th { color: #8fa3b5; border-color: #2a3a4a; } .ed .mkt .mktfull .lbt td { border-color: #1f2a36; } .ed .mkt .mktfull .lbt tr.tot td { border-color: #8fa3b5; }
.ed .mkt h2 { margin: 0; font: 400 40px/1 var(--display); color: #fff; border: 0; padding: 0; text-transform: none; letter-spacing: 0; }
.ed .mkt table { width: 100%; border-collapse: collapse; font-size: 14px; }
.ed .mkt th { text-align: right; font-weight: 400; color: #9fb0c8; padding: 8px 8px; border-bottom: 1px solid #1f2a36; font-size: 11px; letter-spacing: .08em; text-transform: uppercase; white-space: nowrap; }
.ed .mkt td { text-align: right; padding: 10px 8px; border-bottom: 1px solid #141b24; white-space: nowrap; color: #e8edf2; font-size: 14px; }
.ed .mkt th:first-child, .ed .mkt td:first-child, .ed .mkt th:nth-child(2), .ed .mkt td:nth-child(2) { text-align: left; }
.ed .mkt tr.mk { cursor: pointer; }
.ed .mkt tr.mk:hover td, .ed .mkt tr.mk.on td { background: #121b26; }
.ed .mkt tbody tr:hover { background: transparent; }
.ed .sym { font-weight: 700; color: #fff; }
.ed .star { border: 0; background: none; color: #4b5a6b; font-size: 16px; cursor: pointer; }
.ed .star[aria-pressed="true"] { color: #ffd27a; }
.ed .chartbox { background: #111820; border: 1px solid #1f2a36; border-radius: 14px; padding: 16px; display: flex; flex-direction: column; gap: 10px; }
.ed .chartbox svg { width: 100%; height: 260px; display: block; }
.ed .rng { display: flex; gap: 4px; }
.ed .rng button { border: 1px solid #1f2a36; background: #0b0f14; color: #9fb0c8; border-radius: 6px; padding: 4px 10px; font: 700 12px 'JetBrains Mono', monospace; cursor: pointer; }
.ed .rng button[aria-pressed="true"] { background: #1f2a36; color: #fff; }
.ed .anal { background: #111820; border: 1px solid #1f2a36; border-radius: 14px; padding: 16px; font-family: var(--body); display: flex; flex-direction: column; gap: 8px; font-size: 14px; line-height: 1.5; }
.ed .anal h4 { margin: 0; font: 400 22px var(--display); color: #fff; }
.ed .anal p { margin: 0; }
.ed .anal .r { display: flex; justify-content: space-between; border-bottom: 1px solid #1f2a36; padding: 5px 0; font-family: 'JetBrains Mono', monospace; font-size: 13px; }
/* Cold Call Comics */
.ed .comic { background: #fffdf7; color: #2a2320; border: 3px solid #2a2320; border-radius: 8px; padding: 22px; display: flex; flex-direction: column; gap: 14px; font-family: 'Comic Neue', cursive; box-shadow: var(--shadow); }
.ed .comic .title { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 3px solid #2a2320; padding-bottom: 6px; gap: 10px; flex-wrap: wrap; }
.ed .comic .title b { font: 400 54px/1 Bangers, Impact, sans-serif; letter-spacing: .04em; color: #b5532f; }
.ed .panels { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.ed .panel { border: 3px solid #2a2320; background: #fffaf3; aspect-ratio: 4 / 3; position: relative; overflow: hidden; display: flex; flex-direction: column; }
.ed .comic .panel { aspect-ratio: auto; min-height: 330px; overflow: visible; }
.ed .comic .scene { display: flex; flex-direction: column; justify-content: space-between; gap: 10px; padding: 12px 12px 0; background: linear-gradient(180deg, #f8efe4 calc(100% - 64px), #e8dac9 calc(100% - 64px)); }
.ed .comic .dlg { display: flex; flex-direction: column; gap: 14px; }
.ed .comic .sbb { position: relative; max-width: 82%; align-self: flex-start; }
.ed .comic .sbb.rt { align-self: flex-end; }
.ed .comic .stage { position: relative; display: flex; justify-content: space-around; align-items: flex-end; min-height: 104px; padding-bottom: 10px; }
.ed .comic .fig { position: static; flex: 0 1 70px; min-width: 0; } .ed .comic .fig small { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ed .comic .dlg { flex: 1 1 auto; } .ed .comic .fxrow { text-align: center; margin-bottom: -4px; } .ed .comic .fxrow .fx { position: static; display: inline-block; font-size: 26px; white-space: nowrap; }
.ed .panel .foot { flex-wrap: nowrap; } .ed .panel .foot > span { flex: 1 1 auto; min-width: 0; }
.ed .comic .stage .tw { position: static; }
.ed .panel .foot { display: flex; align-items: flex-end; justify-content: space-between; gap: 10px; border-top: 3px solid #2a2320; background: #fff; padding: 6px 8px 6px 10px; font-weight: 700; font-size: 12.5px; line-height: 1.35; }
.ed .panel .foot .plike { position: static; flex: 0 0 auto; }
.ed .comic .sbb { z-index: 2; } .ed .sbb.rt::after { left: auto; right: 24px; }
.ed .panel .cap { background: #fff2b8; border-bottom: 3px solid #2a2320; padding: 6px 10px; font-weight: 700; font-size: 14px; }
.ed .scene { flex: 1; position: relative; background: linear-gradient(180deg, #f8efe4 60%, #e8dac9 60%); }
.ed .fig { position: absolute; bottom: 14px; width: 70px; text-align: center; }
.ed .fig .hd { width: 44px; height: 44px; border-radius: 50%; margin: 0 auto; border: 3px solid #2a2320; }
.ed .fig .bd { width: 56px; height: 60px; border-radius: 14px 14px 4px 4px; margin: -4px auto 0; border: 3px solid #2a2320; }
.ed .fig small { display: block; font-weight: 700; font-size: 11px; margin-top: 3px; }
.ed .sbb { position: absolute; background: #fff; border: 3px solid #2a2320; border-radius: 16px; padding: 8px 12px; font-weight: 700; font-size: 13px; line-height: 1.3; max-width: 62%; }
.ed .sbb::after { content: ""; position: absolute; bottom: -14px; left: 24px; border: 8px solid transparent; border-top: 10px solid #2a2320; }
.ed .sbb.th { border-radius: 50%; padding: 14px 16px; }
.ed .sbb.th::after { display: none; }
.ed .fx { position: absolute; font: 400 34px/1 Bangers, Impact, sans-serif; color: #b5532f; transform: rotate(-8deg); text-shadow: 2px 2px 0 #2a2320; }
.ed .panel.duel .scene { background: linear-gradient(115deg, var(--l) 0 48%, #fff 48% 52%, var(--r) 52%); }
.ed .panel.duel .vsb { position: absolute; left: 50%; top: 40%; transform: translate(-50%, -50%); font: 400 54px/1 Bangers, Impact, sans-serif; color: #ffd27a; text-shadow: 3px 3px 0 #2a2320; }
.ed .panel.duel .hpb { position: absolute; top: 10px; width: 40%; height: 12px; background: #fff; border: 2px solid #2a2320; }
.ed .panel.duel .hpb i { display: block; height: 100%; background: #1fbf5c; }
.ed .panel.duel .lab2 { position: absolute; top: 26px; font-weight: 700; font-size: 12px; color: #fff; text-shadow: 1px 1px 0 #2a2320; }
.ed .panel.boss .scene { background: radial-gradient(circle at 50% 70%, #f2c9b4, #b5532f 60%, #5a2416); }
.ed .panel.boss .mon { position: absolute; left: 50%; bottom: 10px; transform: translateX(-50%); width: 120px; height: 120px; border-radius: 50% 50% 10px 10px; background: #2a2320; border: 4px solid #000; display: flex; align-items: center; justify-content: center; color: #ffd27a; font: 400 20px Bangers, Impact, sans-serif; text-align: center; line-height: 1; padding: 6px; }
.ed .panel.tumble .scene { background: linear-gradient(180deg, #f2c9a0, #e8dac9 70%); }
.ed .panel.tumble .tw { position: absolute; bottom: 18px; left: 40%; width: 50px; height: 50px; border-radius: 50%; border: 3px dashed #8a6a3e; }
.ed .panel.last .scene { background: #2a2320; color: #f3e9dc; display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 6px; text-align: center; padding: 14px; }
.ed .panel.last .scene b { font: 400 46px/1 Bangers, Impact, sans-serif; color: #ffd27a; letter-spacing: .04em; }
.ed .plike { position: absolute; right: 8px; bottom: 8px; border: 2px solid #2a2320; background: #fff; border-radius: 999px; padding: 2px 8px; font: 700 12px 'Comic Neue', cursive; cursor: pointer; }
.ed .plike[aria-pressed="true"] { background: #ffd27a; }
.ed .comic .lbt, .ed .comic .lbt td { color: #2a2320; }
/* CLOSER */
.ed .mag { display: grid; grid-template-columns: 560px minmax(0, 1fr); border-radius: 20px; overflow: hidden; border: var(--bw) solid var(--border-strong); box-shadow: var(--shadow); background: var(--surface-raised); }
.ed .mag .masthead { grid-column: 1 / -1; padding: 14px 44px 36px; border-top: 1px solid var(--border); } .ed .mag .masthead .k { margin-bottom: 8px; }
.ed .cover { background: #f6f1e7; color: #2a2320; padding: 36px; display: flex; flex-direction: column; gap: 16px; min-height: 760px; }
.ed .cover .t { font: 400 104px/.9 var(--display); letter-spacing: -.02em; border-bottom: 4px solid #2a2320; padding-bottom: 12px; }
.ed .cover .port { flex: 1; min-height: 360px; border-radius: 8px; position: relative; overflow: hidden; display: flex; align-items: flex-end; padding: 22px; color: #fff; font: 400 42px/1.05 var(--display); text-shadow: 0 1px 10px rgba(0,0,0,.4); }
.ed .cover .cls { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; font-size: 14px; line-height: 1.45; }
.ed .cover .cls b { display: block; font: 400 19px var(--display); }
.ed .sil { position: absolute; left: 50%; bottom: 0; transform: translateX(-50%); width: 62%; height: 78%; }
.ed .sil::before { content: ""; position: absolute; left: 50%; top: 0; transform: translateX(-50%); width: 34%; aspect-ratio: 1; border-radius: 50%; background: var(--c); }
.ed .sil::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 58%; border-radius: 40% 40% 0 0; background: var(--c); }
.ed .cover .seg { display: flex; gap: 3px; background: #e8dac9; padding: 4px; border-radius: 12px; flex-wrap: wrap; }
.ed .cover .seg button { border: 0; padding: 7px 11px; border-radius: 9px; background: transparent; font: 500 13px var(--body); color: #5e5046; cursor: pointer; }
.ed .cover .seg button[aria-pressed="true"] { background: #fffaf3; color: #2a2320; font-weight: 700; }
.ed .spread { padding: 40px 44px; display: flex; flex-direction: column; gap: 16px; min-width: 0; }
.ed .spread .k { font-size: 12px; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; color: var(--accent); }
.ed .spread h2 { margin: 0; font: 800 52px/1.02 Fraunces, serif; letter-spacing: -.01em; text-wrap: balance; border: 0; padding: 0; text-transform: none; }
.ed .spread .pq { font: italic 400 30px/1.25 Fraunces, serif; border-left: 6px solid var(--accent); padding-left: 18px; margin: 8px 0; }
.ed .spread .pq small { display: block; font: 600 13px var(--body); letter-spacing: .06em; text-transform: uppercase; color: var(--text-muted); margin-top: 8px; }
.ed .spread p.dek { font: 400 21px/1.4 var(--display); color: var(--text-secondary); }
.ed .spread p { margin: 0; font-size: 17px; line-height: 1.65; color: var(--text-primary); max-width: 72ch; }
.ed .info { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.ed .info div { background: var(--card2); border-radius: 16px; padding: 18px; display: flex; flex-direction: column; gap: 4px; position: relative; overflow: hidden; }
.ed .info b { font: 800 44px/1 Fraunces, serif; color: var(--accent); }
.ed .info span { font-size: 13px; color: var(--text-muted); }
.ed .info .ring { width: 70px; height: 70px; border-radius: 50%; background: conic-gradient(var(--accent) 0 var(--p), var(--chip) var(--p) 100%); display: flex; align-items: center; justify-content: center; }
.ed .info .ring i { width: 48px; height: 48px; border-radius: 50%; background: var(--card2); display: flex; align-items: center; justify-content: center; font: 800 14px var(--body); font-style: normal; }
.ed .podium { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; align-items: end; height: 260px; }
.ed .podium div { display: flex; flex-direction: column; align-items: center; gap: 6px; text-align: center; }
.ed .podium .blk { width: 100%; border-radius: 12px 12px 0 0; background: var(--card2); display: flex; align-items: center; justify-content: center; font: 800 28px Fraunces, serif; color: var(--accent); }
.ed .podium small { font-size: 12px; color: var(--text-muted); }
.ed .podium b { font: 400 16px var(--display); }
@media (max-width: 1100px) {.ed .feedA, .ed .pod, .ed .mkt .g, .ed .mag { grid-template-columns: 1fr; }
.ed .roster { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.ed .gpan, .ed .panels, .ed .drives { grid-template-columns: minmax(0, 1fr); }
.ed .info, .ed .podium { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.ed .gi .sb { grid-template-columns: 1fr; }
.ed .cover { min-height: 0; } }
`;
  const st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
})();

const ED_PUBS = [["post", "The Flores Post"], ["feed", "The Flores Feed"], ["grid", "Fourth and Goal"], ["pod", "KFLR The Close"], ["mkt", "FLRS 500"], ["comic", "Cold Call Comics"], ["closer", "CLOSER"]];
let edPub = "post";
try { const v = localStorage.getItem("board-edition"); if (ED_PUBS.some(p => p[0] === v)) edPub = v; } catch (_) {}
const edMine = { watch: {}, cover: "", flip: {}, seen: {} };   // this viewer's own picks
try { Object.assign(edMine, JSON.parse(localStorage.getItem("board-edition-mine") || "{}")); } catch (_) {}
const edSaveMine = () => { try { localStorage.setItem("board-edition-mine", JSON.stringify(edMine)); } catch (_) {} };
const edShared = { key: "", state: null };                      // everyone's: reactions, comments, votes, mailbag, likes
let edSeg = 0, edPlaying = false, edTick = null, edSel = "FLRS", edRng = "folio";
const edMe = () => ME.name || "Someone";
let edGifOpen = "";   // the post whose GIF picker is open
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
// Every edition's leaderboard is post.js's lbTableHtml: the Digest's
// columns by priority, fitted to its box (Frank, 2026-10-02).
function edLbt(X, cls = "lbt") { return lbTableHtml(X.order, X.NUM, X.T, X.full, { cls }); }
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
// Reaction GIFs, drawn in CSS (no outside service, nothing to key). A
// comment carries `gif: key`; a pasted Giphy / Tenor / .gif link shows too.
const ED_GIFS = {
  fire: ["Fire", `<i>🔥</i><i>🔥</i><i>🔥</i>`], clap: ["Slow clap", `<i>👏</i><i>👏</i>`], money: ["Money rain", `<i>💸</i><i>💵</i><i>💸</i><small>cha-ching</small>`],
  confetti: ["Confetti", `<i>🎉</i><b style="left:20%;background:#e59a6f"></b><b style="left:45%;background:#1baf7a;animation-delay:.4s"></b><b style="left:70%;background:#2a78d6;animation-delay:.8s"></b><b style="left:85%;background:#eda100;animation-delay:.2s"></b>`],
  rocket: ["To the moon", `<i>🚀</i>`], stonks: ["Stonks", `<i>📈</i><i>🧍</i><small>stonks</small>`], mic: ["Mic drop", `<i>🎤</i>`],
  crickets: ["Crickets", `<i>🦗</i><small>. . .</small>`], facepalm: ["Facepalm", `<i>🤦</i>`], fine: ["This is fine", `<i>🔥</i><i>🐶☕</i><i>🔥</i><small>this is fine</small>`],
  slow: ["Speed to dial", `<i>🐢</i>`],
};
const edGifHtml = (k, cls = "") => ED_GIFS[k] ? `<span class="gif g-${k} ${cls}" title="${edEsc(ED_GIFS[k][0])}" role="img" aria-label="${edEsc(ED_GIFS[k][0])}">${ED_GIFS[k][1]}</span>` : "";
const ED_GIF_LINK = /^https:\/\/(?:media\d*\.giphy\.com\/|media\.tenor\.com\/|i\.imgur\.com\/|\S+\.gif(?:\?\S*)?$)\S*$/i;
const edCmText = t => ED_GIF_LINK.test(t.trim()) ? `<img class="gifimg" src="${edEsc(t.trim())}" alt="GIF" loading="lazy" referrerpolicy="no-referrer">` : edEsc(t);
// Apollo's memes: picked by rule from the day, three at most, written on the
// real templates (Frank, 2026-10-04: "can we use real ones?"), kept under
// memes/ so nothing is hot-linked. Each template: file, size, name, what it
// means (shown on hover) and where its words go -- boxes in % of the picture.
const ED_MEME = {
  fine: ["this-is-fine.jpg", 580, 282, "This Is Fine", "A dog sips coffee in a burning room: acting like a bad situation is fine.", [[2, 72, 96, 26, "w b"]]],
  skeleton: ["waiting-skeleton.jpg", 298, 403, "Waiting Skeleton", "Waited so long they turned to bones.", "tb"],
  cheers: ["dicaprio-cheers.jpg", 600, 400, "Leonardo DiCaprio Cheers", "Raising a glass to someone who earned it.", "tb"],
  success: ["success-kid.jpg", 500, 500, "Success Kid", "A small, satisfying win.", "tb"],
  drake: ["drake.jpg", 1200, 1200, "Drake Hotline Bling", "No thanks to the top one; yes to the bottom one.", [[50, 0, 50, 50, "d"], [50, 50, 50, 50, "d"]]],
  simply: ["one-does-not-simply.jpg", 568, 335, "One Does Not Simply", "Boromir's warning: it is harder than it looks.", "tb"],
  cmm: ["change-my-mind.jpg", 482, 361, "Change My Mind", "A strong opinion on a sign, held until someone proves it wrong.", [[2, 2, 96, 30, "w t"]]],
  brain: ["brain.jpg", 857, 1202, "Expanding Brain", "Each idea is bigger than the last; the brightest brain is the best one.", [[0, 0, 46.5, 25, "d"], [0, 25, 46.5, 26, "d"], [0, 51, 46.5, 22.5, "d"], [0, 73.5, 46.5, 26.5, "d"]]],
  harold: ["harold.jpg", 480, 601, "Hide the Pain Harold", "Smiling through something that hurts.", "tb"],
  rollsafe: ["roll-safe.jpg", 702, 395, "Roll Safe", "Tapping his head: a 'smart' idea that is obvious once said.", "tb"],
  exit: ["exit-12.jpg", 804, 767, "Left Exit 12 Off Ramp", "Swerving off at the last second, for the wrong exit.", [[18, 22, 30, 13, "w"], [48, 22, 30, 13, "w"], [12, 78, 60, 14, "w"]]],
};
const edMemeHtml = m => {
  const t = ED_MEME[m.k]; if (!t) return "";
  const boxes = t[5] === "tb" ? [[2, 2, 96, 30, "w t"], [2, 68, 96, 30, "w b"]] : t[5];
  const words = t[5] === "tb" ? [m.top, m.bottom] : m.t;
  const box = ([x, y, w, h, kind], txt) => {
    if (!txt) return "";
    const base = kind === "d" ? 5.2 * w / 50 : 7 * w / 96, fs = Math.max(2.6, base * Math.min(1, 26 / String(txt).length) ** .55);
    return `<span class="mbox ${kind}" style="left:${x}%;top:${y}%;width:${w}%;height:${h}%;font-size:${fs.toFixed(2)}cqw"><span>${edEsc(txt)}</span></span>`;
  };
  return `<div class="meme" title="${edEsc(`${t[3]}: ${t[4]}`)}"><div class="mimg" style="aspect-ratio:${t[1]}/${t[2]}"><img src="memes/${t[0]}" alt="${edEsc(t[3])} meme" loading="lazy">${boxes.map((b, i) => box(b, words[i])).join("")}</div>${m.cap ? `<div class="cap">${edEsc(m.cap)}</div>` : ""}<div class="mname">${edEsc(t[3])}</div></div>`;
};
function edMemes(X) {
  const F = X.F, top = X.order[0], n = top ? X.NUM[top] : null, when = X.isFolio ? "this folio" : pdow(X.dayKey), out = [];
  const up = s => String(s).toUpperCase();
  const sentBy = [...new Set(F.sendoffs.map(c => pfirst(c.who)))];
  const obj = F.objs[0], busy = obj && /busy|timing/i.test(obj[0]);
  // 1. the day itself
  if (!F.ps && F.hh && F.sendoffs.length) out.push({ k: "skeleton", top: "WAITING FOR THEM TO READ", bottom: `THE ${F.sendoffs.length === 1 ? "QUOTE" : F.sendoffs.length + " QUOTES"} WE EMAILED`, cap: `${plural(F.hh, "household")} quoted ${when}, none closed. Present it on the call.` });
  else if (!F.ps) out.push({ k: "fine", top: `NO SALES ${up(when)}`, t: [`NO SALES ${up(when)}`], cap: `${plural(F.dials, "dial")}, ${plural(F.live, "conversation")}${F.hh ? `, ${plural(F.hh, "household")} still waiting on a close` : ""}.` });
  else if (n && n.ps >= X.goal) out.push({ k: "cheers", top: `${up(top)}: ${pmoney(n.ps)}`, bottom: `OVER THE ${pmoney(X.goal)} DAY`, cap: `On ${plural(n.hhSold, "household")}. ${n.pts} points.` });
  else if (n) out.push({ k: "success", top: `${up(top)} CLOSED ${n.hhSold || n.pol} ${(n.hhSold || n.pol) === 1 ? "HOUSEHOLD" : "HOUSEHOLDS"}`, bottom: `${pmoney(n.ps)} ON THE BOARD`, cap: `The team's day: ${pmoney(F.ps)} across ${plural(F.pol, "policy", "policies")}.` });
  // 2. how the quotes went
  if (F.sendoffs.length) out.push({ k: "drake", t: ["Emailing the quote and hoping they read it", "Building it on the call and asking for the sale"], cap: `${plural(F.sendoffs.length, "quote")} went out by email ${when}: ${plist(sentBy)}.` });
  else if (busy) out.push({ k: "simply", top: "ONE DOES NOT SIMPLY", bottom: "LET \"CALL ME BACK\" GO WITHOUT A TIME", cap: `${obj[0]} came up ${plural(obj[1], "time")}, overcome ${obj[2]}. "Is 5 or 6 better, or tomorrow morning?"` });
  else if (obj) out.push({ k: "cmm", t: [`"${up(obj[0])}" IS NOT A NO`], cap: `${plural(obj[1], "call")} heard it ${when}; ${obj[2]} turned it around.` });
  // 3. the phones
  if (F.spBest && F.spTeam != null) out.push({ k: "brain", t: ["Calling the new lead tomorrow", "Calling within the hour", `Team median: ${edFmtStd(F.spTeam)}`, `${pfirst(F.spBest[0])}: ${edFmtStd(F.spBest[1].median)}`], cap: "Speed to dial. The goal is 2 minutes." });
  else if (F.rate < ((((window.GOALS || {}).thresholds || {}).contact_rate_pct || {}).green ?? 13) && F.dials) out.push({ k: "harold", top: "VOICEMAIL IS NOT A CONVERSATION", bottom: `${ppct(F.rate, 0)} CONTACT RATE`, cap: `${plural(F.dials, "dial")} reached ${plural(F.live, "person", "people")}. The goal is 13%.` });
  else if (F.misfiled) out.push({ k: "exit", t: ["1 PIPELINE", "\"PIPELINE\"", `${F.misfiled} OPEN LEAD${F.misfiled === 1 ? "" : "S"}`], cap: "Open leads an integration misfiled in \"Pipeline\". Someone move them to 1 Pipeline." });
  else if (X.SALES.some(s => /winback/i.test(s.src))) out.push({ k: "rollsafe", top: "CAN'T LOSE A CUSTOMER", bottom: "IF YOU WIN THEM BACK", cap: `${plist([...new Set(X.SALES.filter(s => /winback/i.test(s.src)).map(s => s.w))])} closed a winback ${when}.` });
  return out.slice(0, 3).map((m, i) => ({ id: "m-" + (m.top ? m.top.slice(0, 12).replace(/[^A-Z0-9]/g, "").toLowerCase() || i : m.k === "brain" ? "brain" : m.k), who: "Apollo", when: "Meme desk", meme: m, text: m.cap || "" }));
}
/* The front office chimes in (Frank, 2026-10-05: "Francisco is our DM, can
   you have him and myself chime in with funny motivational content wherever
   possible"; "Veronica is office manager/HR, have her chime in with the both
   of us as well"). Written by rule from the day -- never typed by them, so
   every line carries a small "cheer" tag that says so on hover. Lines are
   picked by the day, so a day always reads the same. */
const ED_CHEER_TAG = `<span class="cheer" title="A cheer written by Apollo from the day's numbers, in their voice">cheer</span>`;
function edCheers(X) {
  const F = X.F, when = X.isFolio ? "this folio" : "today", tmr = X.isFolio ? "the rest of the folio" : "tomorrow";
  const h = k => { let x = 7; for (const ch of String(X.dayKey || "folio") + k) x = (x * 31 + ch.charCodeAt(0)) >>> 0; return x; };
  const pick = (k, arr) => arr[h(k) % arr.length];
  const top = X.order[0], tn = top ? X.NUM[top] : null;
  const frank = !F.ps ? pick("f0", [
      `No sales ${when}. The phones didn't break and the leads didn't move away. ${tmr[0].toUpperCase() + tmr.slice(1)} we eat. 📞`,
      `Rough one. Every "no" is just a "yes" that hasn't met you yet. Go introduce yourselves. 💪`,
      `Zero on the board ${when}. Good news: the board resets and I still believe in every one of you. Let's go. 🚀`])
    : F.ps >= X.goal ? pick("f1", [
      `${pmoney(F.ps)} ${when}. I'm framing this one. 🖼️`,
      `${pmoney(F.ps)}?! Somebody check on the printer, it's out of breath. 🖨️💨`,
      `This is the kind of day that pays for the good coffee. ${pmoney(F.ps)}. Keep it rolling. ☕`])
    : pick("f2", [
      `${pmoney(F.ps)} on the board. Good. Now let's make ${tmr} jealous. 😤`,
      `${plural(F.hhSold || F.pol, "family", "families")} sleeping better tonight because of this floor. That's the job. 🙌`,
      `${pmoney(F.ps)} ${when}. Not bad. Not done either. 😎`]);
  const francisco = {
    sale: w => pick("s" + w, [`${w} said "let's bind it" like it was nothing. 🔥`, `That's a W, ${w}. Somebody ring the bell! 🔔`, `${w} out here protecting households like a superhero with a quote tool. 🦸`, `Another one, ${w}! Save some premium for the rest of the floor 😂`, `${w} didn't come to play, ${w} came to close. 🏆`]),
    quoter: (w, pq) => pick("q" + w, [`${w}, that's ${pmoney(pq)} in quotes sitting on the table. Go pick it up. 💰`, `Quotes don't close themselves, ${w}. Believe me, I've asked them. 😂`, `${w}, ${pmoney(pq)} quoted is a great warm-up. Now the main event. 🥊`]),
    obj: o => pick("o", [`"${o}" is just a yes wearing a disguise. Take the mask off. 🎭`, `Next time someone says "${o}", hear "tell me more." 👂`, `"${o}"? Never heard of her. 😏`]),
    speed: (w, secs) => secs <= 120 ? pick("sp", [`${w} dialed so fast the lead hadn't finished typing their zip code. ⚡`, `${w} with the speed. Leads don't even get to blink. 👀`])
      : pick("sps", [`Two minutes is the goal, team. New leads are like fresh tortillas: best when they're hot. 🌮`, `A new lead gets cold faster than my coffee. Dial it while it's hot! ☕⏱️`]),
    wrap: pick("fw", [`Same energy ${tmr}, more dials. Let's ride! 🏇`, `Proud of this floor. Now hydrate and go get 'em ${tmr}. 💧`, `Big things happen to people who pick up the phone. Pick it up. 📞`]),
  };
  const veronica = {
    wrap: pick("vw", [`Reminder from HR: celebrating a sale counts as a team-building activity. Celebrate responsibly. 🎉`, `Great work today. Please take your breaks, drink water, and stop hiding snacks in the supply closet. 🥨`, `Office manager announcement: whoever closes next gets first pick of the good parking spot. 🅿️`, `Proud of you all. Also, please sign your timesheets. Love, HR. 📝`]),
    sale: w => pick("vs" + w, [`So proud of you, ${w}! Paperwork in today, please 😉📎`, `${w}, this is going in your file. The good file. ⭐`, `HR approves this sale. Highly recommend more of them, ${w}. ✅`]),
    meme: pick("vm", [`Apollo, please keep the memes office appropriate. These are fine. For now. 😂`, `Who gave Apollo meme privileges? (Don't take them away.)`]),
    slow: pick("vsl", [`Tough day? Stretch, refill your water, call the next one. You've got this. 💛`, `Friendly HR reminder: a slow day is not a slow you. Back at it ${tmr}. 💛`]),
  };
  return { frank, francisco, veronica, top, tn };
}
function edPosts(X) {
  const F = X.F, posts = [];
  const top = X.order[0];
  posts.push({ id: "wrap", who: "Apollo", when: `${X.isFolio ? "Folio" : pdow(X.dayKey)} wrap`, pic: true,
    text: `<b>${X.isFolio ? "Folio so far" : "Day closed"}: ${pmoney(F.ps)} in new premium.</b> ${plural(F.pol, "policy", "policies")}, ${F.hhSold} household${F.hhSold === 1 ? "" : "s"}${F.hh ? ` of ${F.hh} quoted, a ${ppct(F.closeHH, 0)} close` : ""}. ${top ? `${top} takes ${X.isFolio ? "the folio" : "the day"} with ${X.NUM[top].pts} points.` : ""}` });
  const CH = edCheers(X);
  posts[0].chime = [["Francisco", CH.francisco.wrap], ["Veronica", X.F.ps ? CH.veronica.wrap : CH.veronica.slow]];
  posts.push({ id: "frank-hype", who: "Frank", when: "Owner", cheer: true, text: edEsc(CH.frank) });
  for (const f of X.order) {
    const n = X.NUM[f]; if (!n.ps) continue;
    const mine = X.SALES.filter(s => s.w === f);
    const call = F.calls.filter(c => pfirst(c.who) === f && (c.flags || []).length)[0];
    posts.push({ id: "s-" + f, who: f, when: "Final · Sale", text: `${plist(mine.map(s => `${s.prod} ${pmoney(s.amt)}`))}${mine.some(s => /winback/i.test(s.src)) ? " 🔁" : mine.some(s => /existing|cross/i.test(s.src)) ? " ➕" : ""}`,
      apollo: call ? `${call.flags[0]}${call.time ? ` (${call.time})` : ""}. ${call.askfix || ""}`.trim() : `${plural(n.hhSold, "household")} closed, ${n.dials} dials, ${ppct(n.rate)} contact rate.`,
      chime: [["Francisco", CH.francisco.sale(f)], ...(f === X.order.find(g => X.NUM[g].ps) ? [["Veronica", CH.veronica.sale(f)]] : [])] });
  }
  if (F.spBest) posts.push({ id: "sp", who: "Apollo", when: "Speed", chime: [["Francisco", CH.francisco.speed(pfirst(F.spBest[0]), F.spBest[1].median)]], text: `${pfirst(F.spBest[0])} dialled a new internet lead in <b>${edFmtStd(F.spBest[1].median)}</b>.${F.spTeam != null ? ` Team median ${edFmtStd(F.spTeam)}; the goal is 2 minutes.` : ""}` });
  if (F.objs[0]) posts.push({ id: "obj", who: "Apollo", when: "Coaching", chime: [["Francisco", CH.francisco.obj(F.objs[0][0].split(" / ")[0])]], text: `<span class="lab" style="color:var(--accent)">Flag</span> ${edEsc(F.objs[0][0])} came up ${plural(F.objs[0][1], "time")}, overcome ${F.objs[0][2]}.${/busy|timing/i.test(F.objs[0][0]) ? ' "Is 5 or 6 better, or tomorrow morning?"' : ""}` });
  const quoter = X.order.map(f => X.NUM[f]).filter(n => !n.ps && n.pq).sort((a, b) => b.pq - a.pq)[0];
  if (quoter) posts.push({ id: "q-" + pfirst(quoter.n), who: pfirst(quoter.n), when: "Final · Quoted", text: `${pmoney(quoter.pq)} quoted across ${plural(quoter.hh, "household")}${quoter.pq >= Math.max(...Object.values(X.NUM).map(x => x.pq)) ? ", most on the team" : ""}. Nothing closed yet.`,
    apollo: `${quoter.dials} dials, ${plural(quoter.live, "conversation")}. ${quoter.sent ? `${plural(quoter.sent, "quote")} sent instead of presented.` : "Present on the phone and ask for the sale."}`,
    chime: [["Francisco", CH.francisco.quoter(pfirst(quoter.n), quoter.pq)]] });
  // Apollo's memes land after the wrap, in the middle and at the end.
  const memes = edMemes(X), slots = [1, Math.ceil(posts.length / 2) + 1, posts.length + 2];
  if (memes[0]) memes[0].chime = [["Veronica", CH.veronica.meme]];
  memes.forEach((m, i) => posts.splice(Math.min(posts.length, slots[i]), 0, m));
  return posts;
}
// Everyone's handle on The Flores Feed (Frank, 2026-10-05: "give everyone a
// creative, insurance focused username"), by first name; anyone else gets one
// made from their name. A person's own is their `handle` in staff.json.
const ED_HANDLES = Object.assign({ Apollo: "coach.apollo" },
  Object.fromEntries(((window.STAFF || {}).people || []).filter(p => p.handle).map(p => [p.name.split(" ")[0], p.handle])));
const edHandle = who => { const f = pfirst(String(who || "")); return "@" + (ED_HANDLES[f] || `${f.toLowerCase().replace(/[^a-z]/g, "") || "agent"}.always.covered`); };
function edPostHtml(X, p) {
  const S = edShared.state, rx = S.rx[p.id] || {}, cms = S.cm[p.id] || [];
  const RXS = ["🔥", "👏", "💰", "😬", "🫡"];
  return `<div class="pc" data-post="${p.id}"><div class="whor">${edAvatar(X, p.who)}<div><b>${p.who === "Apollo" ? 'Apollo <span class="ver">✓ coaching</span>' : edEsc(X.full[p.who] || p.who)}</b><small><span class="hdl">${edEsc(edHandle(p.who))}</span> · ${edEsc(p.when)}${p.cheer ? ` · ${ED_CHEER_TAG}` : ""}</small></div></div><p>${p.text}</p>
   ${p.pic ? `<div class="pic"><div><div class="lab">Premium sold</div><b>${pmoney(X.F.ps)}</b></div><div style="text-align:right"><div class="lab">Households</div><b>${X.F.hh ? `${X.F.hhSold} of ${X.F.hh}` : X.F.hhSold}</b></div><div style="text-align:right"><div class="lab">Closing</div><b>${X.F.closeHH == null ? "—" : ppct(X.F.closeHH, 0)}</b></div></div>` : ""}
   ${p.meme ? edMemeHtml(p.meme) : ""}
   <div class="rx">${RXS.map(e => { const by = rx[e] || []; return `<button type="button" data-rx="${e}" aria-pressed="${by.includes(edMe())}" title="${edEsc(by.join(", "))}">${e} ${by.length || ""}</button>`; }).join("")}</div>
   <div class="cm">${(p.chime || []).map(([w, t]) => `<div class="c">${edAvatar(X, w, 28)}<div><b>${edEsc(w)}</b> <small><span class="hdl">${edEsc(edHandle(w))}</span> · ${ED_CHEER_TAG}</small><br>${edEsc(t)}</div></div>`).join("")}${p.apollo ? `<div class="c">${edAvatar(X, "Apollo", 28)}<div><b>Apollo</b> <small><span class="hdl">${edHandle("Apollo")}</span> · coaching note</small><br>${edEsc(p.apollo)}</div></div>` : ""}${cms.map(c => `<div class="c">${edAvatar(X, pfirst(c.who), 28)}<div><b>${edEsc(c.who)}</b> <small><span class="hdl">${edEsc(edHandle(c.who))}</span> · ${edEsc(c.at)}</small><br>${c.gif ? edGifHtml(c.gif) : ""}${c.text && c.gif ? "<br>" : ""}${c.text ? edCmText(c.text) : ""}</div></div>`).join("")}
   <form data-cm><input class="t" placeholder="Reply as ${edEsc(edHandle(edMe()))}… or paste a GIF link" aria-label="Reply" maxlength="300"><button type="button" class="ebtn q" data-gifpick="${p.id}" aria-expanded="${edGifOpen === p.id}">GIF</button><button class="ebtn">Post</button></form>
   ${edGifOpen === p.id ? `<div class="gifpick">${Object.keys(ED_GIFS).map(k => `<button type="button" data-gif="${k}" title="${edEsc(ED_GIFS[k][0])}">${edGifHtml(k)}</button>`).join("")}</div>` : ""}</div></div>`;
}
function edFeed(X) {
  const S = edShared.state, votes = S.poll || {}, mine = Object.entries(votes).find(([, by]) => by.includes(edMe())), tot = Object.values(votes).reduce((a, b) => a + b.length, 0);
  const F = X.F, done = X.rows.length, bizAll = X.bizAll || done, pace = done ? X.FTOT / done * bizAll : 0;
  const zero = X.rows.filter(r => !r.ps).length;
  return `<div class="feedA"><div class="col">
   <div class="pc"><div class="stories">${["Apollo", ...X.order].map(w => `<button type="button" data-story="${w}"><i class="${edMine.seen[X.dayKey + w] ? "seen" : ""}" style="color:${X.C[w] || "var(--text-primary)"};border-color:${edMine.seen[X.dayKey + w] ? "var(--border-strong)" : (X.C[w] || "var(--text-primary)")}">${X.INI[w] || "A"}</i>${w}</button>`).join("")}</div><p class="note">Tap a story for a clip from their ${X.isFolio ? "folio" : "day"}.</p></div>
   ${edPosts(X).map(p => edPostHtml(X, p)).join("")}</div>
   <div class="col">
    <div class="pc"><h3>Top accounts · ${edEsc(edWhen(X))}</h3>${X.order.map((f, i) => `<div class="trend"><span style="display:flex;align-items:center;gap:10px">${edAvatar(X, f, 32)}<span>${i + 1} · ${edEsc(X.full[f])}<br><small class="hdl">${edEsc(edHandle(f))}</small></span></span><b>${X.NUM[f].pts} pts · ${X.NUM[f].pol} pol</b></div>`).join("")}</div>
    <div class="pc"><h3>Poll · who takes ${edEsc(edNextDay(X))}?</h3><div class="poll">${X.order.map(f => { const n = (votes[f] || []).length, pct = tot ? Math.round(100 * n / tot) : 0; return `<button type="button" data-vote="${f}" aria-pressed="${!!mine && mine[0] === f}" title="${edEsc((votes[f] || []).length ? (votes[f] || []).join(", ") : "No votes yet")}"><i style="width:${pct}%"></i><span><span>${edEsc(X.full[f])}</span><span>${tot ? pct + "%" : ""}</span></span></button>`; }).join("")}</div><p class="note">${plural(tot, "vote")} · one each · everyone sees the tally</p></div>
    <div class="pc"><h3>Folio · day ${done} of ${bizAll}</h3><div class="prog"><i style="width:${pace ? Math.min(100, X.FTOT / pace * 100) : 0}%"></i></div><div class="hrow"><span class="note">${pmoney(X.FTOT)} so far</span><span class="note">pace ${pmoney(pace)}</span></div><p style="font-size:14px">${zero ? `${plural(zero, "zero day")} so far. ` : ""}${Math.max(0, F.hh - F.hhSold) ? `${plural(Math.max(0, F.hh - F.hhSold), "quoted household")} still open.` : ""}</p></div>
    <div class="pc"><h3>Trending</h3>${F.objs.slice(0, 2).map(o => `<div class="trend"><span>#${edEsc(o[0].replace(/[^A-Za-z]/g, ""))}</span><b>${o[1]}</b></div>`).join("")}${X.SALES.some(s => /winback/i.test(s.src)) ? `<div class="trend"><span>#Winback</span><b>${X.SALES.filter(s => /winback/i.test(s.src)).length}</b></div>` : ""}<div class="trend"><span>#SentTheQuote</span><b>${X.T.sent} of ${X.T.quoteUp}</b></div><div class="trend" style="border:0"><span>#Misfiled</span><b>${F.misfiled}</b></div></div>
   </div></div>
   <div class="pc" style="margin-top:14px"><div class="whor">${edAvatar(X, "Apollo")}<div><b>Apollo <span class="ver">✓</span></b><small><span class="hdl">${edHandle("Apollo")}</span> · Trending accounts · every stat, final</small></div></div>${edLbt(X)}</div>`;
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
    <div class="box"><h4>MVP vote</h4><p style="margin:0 0 8px">Pick the player of the game. One vote each; everyone sees the tally.</p>${X.order.map(f => `<button type="button" class="ebtn ${mvp[edMe()] === f ? "" : "q"}" data-mvp="${f}" style="margin:0 6px 6px 0" title="${edEsc(Object.entries(mvp).filter(([, w]) => w === f).map(([who]) => who).join(", ") || "No votes yet")}">${f} ${tally[f] ? "· " + tally[f] : ""}</button>`).join("")}<h4 style="margin-top:12px">Game recap</h4>${recap}</div></div>
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
    (CH => ["☎️", "9:10", "Front office call-ins", "Frank, Francisco and Veronica on the line",
      [`Frank (cheer): ${CH.frank}`, `Francisco (cheer): ${CH.francisco.wrap}`, `Veronica (cheer): ${X.F.ps ? CH.veronica.wrap : CH.veronica.slow}`]])(edCheers(X)),
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
</div><div class="edcard playlist"><h3>The playlist · tonight’s numbers, track by track</h3>${edLbt(X)}</div></div>`;
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
</div></div><div class="mktfull"><h4>Closing prices · the full tape</h4>${edLbt(X, "lbt mktlb")}</div></div>`;
}

/* ===== COLD CALL COMICS ===== */
/* The strip tells the day as a story (Frank, 2026-10-04: "i want it to be a
   story based off the days events, not random interactions"): the floor
   opens, then the day's turning points in the order they happened -- each
   sale, the objection best handled and the one dropped, a quote sent by
   email instead of presented, the fastest first dial, a sale written off a
   call -- each in the words said at that moment (the coaching card's
   objection lines and spine quotes; never a line with a long number in it),
   and it ends on the tally with what is left open for tomorrow. */
function edComic(X) {
  const S = edShared.state, F = X.F, likes = S.likes || {};
  const fig = (c, n) => `<div class="fig"><div class="hd" style="background:${c}"></div><div class="bd" style="background:${c}99"></div><small>${edEsc(n)}</small></div>`;
  const clip = (t, n = 110) => { t = String(t || "").replace(/\s+/g, " ").trim(); if (t.length <= n) return t; const c = t.slice(0, n); return c.slice(0, Math.max(c.lastIndexOf(" "), n - 20)).replace(/[,;:\s.]+$/, "") + "…"; };
  const safe = t => t && !/\d{4,}|\d{3}[\s-]\d{2,}/.test(t);  // no account, card or phone numbers in a bubble
  const quoted = t => (String(t || "").match(/(?:^|[\s(])['"“](.{8,}?)['"”](?=[\s.,;:)!?]|$)/) || [])[1] || "";
  const leadOf = c => c && c.lead ? pfirst(c.lead) : "the lead";
  const tlines = c => String(c.transcript || "").split("\n").map(l => /^(?:\[\d+:\d+\]\s*)?([^:\[\]]{1,40}):\s*(.+)$/.exec(l)).filter(Boolean).map(m => ({ who: m[1], prod: /\(producer\)/.test(m[1]), text: m[2] }));
  const verb = c => c.direction === "call in" ? `takes a call from ${leadOf(c)}` : c.direction === "call back" ? `gets a call back from ${leadOf(c)}` : `dials ${leadOf(c)}`;
  const mins = c => feedMins(c && c.time);
  const at = c => c && c.time ? `${c.time}. ` : "Later. ";
  const P = c => ({ n: pfirst(c.who), c: X.C[pfirst(c.who)] || "#b5532f" }), L = c => ({ n: leadOf(c), c: "#c9b8a8" });
  // two people, the first speaker on the left: their line on top, the reply below on the right
  const fxh = (fx, fxc) => fx ? `<div class="fx"${fxc ? ` style="color:${fxc}"` : ""}>${edEsc(fx)}</div>` : "";
  const stage = (figs, fx, fxc) => `${fx ? `<div class="fxrow">${fxh(fx, fxc)}</div>` : ""}<div class="stage">${figs.join("")}</div>`;
  const sc = (l, r, { fx, fxc } = {}) => `<div class="dlg">${l.text ? `<div class="sbb">${edEsc(l.text)}</div>` : ""}${r && r.text ? `<div class="sbb rt">${edEsc(r.text)}</div>` : ""}</div>${stage([fig(l.c, l.n), ...(r ? [fig(r.c, r.n)] : [])], fx, fxc)}`;
  // a spine moment's quote, said by the lead or by the producer
  const spineSaid = (c, byLead) => { const lf = leadOf(c).toLowerCase(); for (const x of [...(c.spine || [])].reverse()) { if (!byLead && x[1] !== "g") continue; const q = quoted(x[3]); if (!q || !safe(q)) continue; const lead = /^(lead|prospect|customer|caller|he |she |they )/i.test(x[2]) || x[2].toLowerCase().startsWith(lf); if (lead === byLead) return q; } return ""; };
  const beats = [];
  // the sales made on a call: the close in their own words
  const soldCalls = F.calls.filter(c => /sold/.test(c.catc || ""));
  for (const c of soldCalls.slice(0, 3)) {
    const ls = tlines(c), tail = ls.slice(Math.floor(ls.length * .6)), you = spineSaid(c, false) || ((tail.filter(l => l.prod && safe(l.text) && l.text.length >= 15).pop() || {}).text || ""), they = spineSaid(c, true) || ((tail.filter(l => /\((lead|customer)\)/.test(l.who) && safe(l.text) && l.text.length >= 10).pop() || {}).text || "");
    beats.push({ t: mins(c) == null ? null : mins(c) + .5, pri: 1, cap: `${at(c)}${pfirst(c.who)} ${verb(c)}${c.dur ? ` (${c.dur})` : ""}. The close.`, foot: ((c.good || [])[0] || [])[0], html: sc({ ...P(c), text: clip(you) }, { ...L(c), text: clip(they, 80) }, { fx: "SOLD!", fxc: "#2f8f5b" }) });
  }
  // a sale written with no sold call behind it: narration only
  const soldBy = new Set(soldCalls.map(c => pfirst(c.who)));
  for (const w of [...new Set(X.SALES.map(s => s.w))].filter(w => !soldBy.has(w)).slice(0, 2)) {
    const mine = X.SALES.filter(s => s.w === w), kinds = {};
    for (const s of mine) { const k = `${s.prod}${s.src.trim() ? ` (${s.src.trim()})` : ""}`; kinds[k] = (kinds[k] || 0) + 1; }
    beats.push({ t: null, pri: 2, cap: `Meanwhile, ${w} writes ${plist(Object.entries(kinds).slice(0, 3).map(([k, n]) => n > 1 ? `${n} ${k}` : k))}.`, html: `<div class="dlg"></div>${stage([fig(X.C[w] || "#b5532f", w)], `+${pmoney(mine.reduce((a, s) => a + s.amt, 0))}`, "#2f8f5b")}` });
  }
  // the objections: the best handled and the one that got away -- the lead speaks first
  const objs = F.calls.flatMap(c => (c.objs || []).map(o => ({ c, o }))).filter(x => x.o.they && x.o.you && safe(x.o.they) && safe(x.o.you));
  const won = objs.filter(x => +x.o.score >= 8).sort((a, b) => b.o.score - a.o.score)[0];
  const lost = objs.filter(x => +x.o.score <= 4 && !(won && x.c === won.c)).sort((a, b) => a.o.score - b.o.score)[0];
  if (won) beats.push({ t: mins(won.c), pri: 2, cap: `${at(won.c)}${pfirst(won.c.who)} ${verb(won.c)}. "${won.o.group || won.o.cat}."`, foot: won.o.cat, html: sc({ ...L(won.c), text: clip(won.o.they, 80) }, { ...P(won.c), text: clip(won.o.you) }, { fx: "OVERCOME!", fxc: "#2f8f5b" }) });
  if (lost) beats.push({ t: mins(lost.c), pri: 3, cap: `${at(lost.c)}${pfirst(lost.c.who)} ${verb(lost.c)}. "${lost.o.group || lost.o.cat}."`, foot: lost.o.fix ? `Apollo: ${clip(lost.o.fix, 120)}` : "", html: sc({ ...L(lost.c), text: clip(lost.o.they, 80) }, { ...P(lost.c), text: clip(lost.o.you, 90) }, { fx: "DROPPED", fxc: "#c0392b" }) });
  // a quote sent instead of presented
  const sent = F.calls.find(c => (Array.isArray(c.sendoff) ? c.sendoff[0] : c.sendoff) === "producer" && !(won && c === won.c) && !(lost && c === lost.c));
  if (sent) {
    const l = tlines(sent).filter(x => x.prod && safe(x.text) && /send|email|mand|correo|text/i.test(x.text)).pop();
    beats.push({ t: mins(sent), pri: 3, cap: `${at(sent)}${pfirst(sent.who)} ${verb(sent)}. The quote goes by email.`, foot: "Apollo: present it on the call, don't send it.", html: sc({ ...P(sent), text: clip((q => safe(q) && q)(quoted(Array.isArray(sent.sendoff) ? sent.sendoff[1] : "")) || (l ? l.text : "") || "I'll send it over to you.") }, L(sent), { fx: "SENT ✉" }) });
  }
  // the fastest first dial on a new lead
  if (F.spBest && F.spBest[1].median != null && F.spBest[1].median <= 120) beats.push({ t: null, pri: 4, cap: `A new lead lands. ${pfirst(F.spBest[0])} dials it in ${edFmtStd(F.spBest[1].median)}.`, html: `<div class="dlg"></div>${stage([fig(X.C[pfirst(F.spBest[0])] || "#b5532f", pfirst(F.spBest[0]))], "ZOOM!")}` });
  // the most important six, then told in the order they happened
  const story = beats.sort((a, b) => a.pri - b.pri).slice(0, 6).map((b, i) => ({ ...b, i })).sort((a, b) => (a.t ?? 1e4 + a.i) - (b.t ?? 1e4 + b.i));
  const timed = F.calls.map(mins).filter(x => x != null), first = F.calls.find(c => mins(c) === Math.min(...timed));
  const panels = [{ cap: X.isFolio ? "The folio so far." : `${pdow(X.dayKey)}${first ? `, ${first.time}` : ""}. The floor opens.`, html: `<div class="dlg"><div class="sbb">${edEsc(first ? `${pfirst(first.who)} is on the phone first. ${plural(F.dials, "dial")} to go.` : `${plural(F.dials, "dial")} ahead.`)}</div></div>${stage(X.order.slice(0, 5).map(f => fig(X.C[f], f)))}` }, ...story];
  if (!F.ps) panels.push({ cap: `${edEsc(edWhen(X))}. Nothing crossed the line.`, cls: "tumble", html: `<div class="dlg"></div>${stage(['<div class="tw"></div>'], "TUMBLEWEED")}` });
  const open = Math.max(0, F.hh - F.hhSold);
  panels.push({ cap: open ? `Final. To be continued: ${plural(open, "quoted household")} still open.` : "Final.", cls: "last", html: `<b>${pmoney(F.ps)}</b><span>${plural(F.pol, "policy", "policies")} · ${F.hhSold} of ${F.hh} households${F.closeHH != null ? ` · ${ppct(F.closeHH, 0)} close` : ""}</span><span style="font-size:13px">${X.order.map(f => `${f} ${X.NUM[f].pts}`).join(" · ")}</span>` });
  return `<div class="comic"><div class="title"><b>COLD CALL COMICS</b><span style="font-weight:700">${edEsc(X.isFolio ? "The folio so far" : plong(X.dayKey))} · drawn by Apollo</span></div>
  <div class="panels">${panels.map((p, i) => { const by = likes[i] || []; return `<div class="panel ${p.cls || ""}"${p.style ? ` style="${p.style}"` : ""}><div class="cap">${edEsc(p.cap)}</div><div class="scene">${p.html}</div><div class="foot"><span>${p.foot ? edEsc(p.foot) : ""}</span><button type="button" class="plike" data-like="${i}" title="${edEsc(by.length ? by.join(", ") : "No likes yet")}" aria-pressed="${by.includes(edMe())}">😂 ${by.length || ""}</button></div></div>`; }).join("")}</div>
  <div style="font-family:var(--body);display:flex;flex-direction:column;gap:12px;border-top:3px solid #2a2320;padding-top:14px"><div class="hrow"><b style="font:400 30px Bangers,Impact,sans-serif;letter-spacing:.04em">THE LAST PANEL</b><span class="lab">every number, no drawings</span></div>${edLbt(X)}</div>
  <p class="note" style="font-family:var(--body)">The day as it happened: its sales, the objection best handled and the one dropped, a quote sent instead of presented, the fastest first dial, in the words said on the calls and in the order they happened.</p></div>`;
}

/* ===== CLOSER ===== */
/* CLOSER's own copy (Frank, 2026-10-01: "the magazine and the newspaper have
   the same wording, they should be different"). The Post reports the day;
   the magazine profiles whoever carried it, opening on a call Apollo heard,
   with their own words as the pull quote. Written in rules from the same
   facts, never from writeDay. */
function edMagStory(X) {
  const F = X.F, top = X.order[0], n = top ? X.NUM[top] : null, full = top ? X.full[top] : "The team", first = top || "the floor";
  const when = X.isFolio ? "this folio" : pdow(X.dayKey), seed = (X.dayKey || "") + "closer";
  const clip = top ? edClip(X, top) : { lines: [], call: null }, call = clip.call;
  const said = call ? (String(call.transcript || "").split("\n").map(l => l.replace(/^\[\d+:\d+\]\s*/, "")).find(l => /\(producer\):/.test(l) && l.split(":").slice(1).join(":").trim().length > 40) || "") : "";
  // their own words: the first sentence or two, under ~120 characters
  const quote = (() => { if (!said) return ""; const t = said.split(":").slice(1).join(":").trim().replace(/\s+/g, " "); let q = "", parts = t.split(/(?<=[.?!])\s+/); for (const x of parts) { if (q && (q + " " + x).length > 120) break; q = q ? q + " " + x : x; if (q.length >= 60) break; } return q.slice(0, 140).replace(/[,;:\s.]+$/, ""); })();
  const lead = call && call.lead ? pfirst(call.lead) : "a prospect";
  const mine = top ? X.SALES.filter(s => s.w === top) : [];
  const others = X.order.slice(1).map(f => X.NUM[f]);
  const obj = F.objs[0], busy = obj && /busy|timing/i.test(obj[0]);
  const myFlags = top ? X.FLAGS.filter(x => x[0] === top).map(x => x[1]) : [];
  const nextDay = edNextDay(X);
  const S = { paras: [] };
  if (X.isFolio) {
    S.hl = ppick([`The folio at ${pmoney(X.FTOT)}, and the ${plural(X.rows.length, "day")} that built it`, `Who is carrying the folio`, `${pmoney(X.FTOT)} and counting: the folio, so far`], seed);
    S.dek = `${full} leads it with ${pmoney(n ? n.ps : 0)}. ${X.rows.filter(r => !r.ps).length ? `${plural(X.rows.filter(r => !r.ps).length, "day")} closed with nothing.` : "Every day has put something on the board."}`;
  } else if (!F.ps) {
    S.hl = ppick([`Everything but the close`, `The quiet floor`, `${plural(F.dials, "dial")}, ${plural(F.live, "conversation")}, no sale`], seed);
    S.dek = F.hh ? `${plural(F.hh, "household")} heard a number ${when} and none said yes. A look at where the calls went.` : `Nothing was quoted ${when}, so nothing could close. A look at the phones.`;
  } else {
    S.hl = ppick([`${full} and the art of the ${pmoney(n.ps)} ${when === "this folio" ? "folio" : "day"}`, `How ${first} built ${pmoney(n.ps)} one call at a time`, `${first}, on the line`], seed);
    S.dek = `A profile of ${first}'s ${when}, told through the calls Apollo heard${n.hhSold ? `: ${plural(n.hhSold, "household")}, ${pmoney(n.ps)}, first in the standings` : ""}.`;
  }
  // the scene
  if (call) S.paras.push(`${call.time ? `It is ${call.time}` : "It is midmorning"} and ${first} is on with ${lead}.${quote ? ` "${quote}${/[.?!]$/.test(quote) ? "" : "."}"` : ""}${call.dur ? ` The call runs ${call.dur}.` : ""}${call.summary ? ` Apollo's read: ${String(call.summary).trim().replace(/\.?$/, ".")}` : ""}`);
  else if (n) S.paras.push(`${first} made ${plural(n.dials, "dial")} ${when} and reached ${plural(n.live, "person", "people")}, a ${ppct(n.rate)} contact rate. Apollo heard none of them: no call of ${first}'s was recorded long enough to coach.`);
  // the number
  if (n && n.ps) S.paras.push(`By the close ${first} had ${pmoney(n.ps)} in new premium${mine.length ? `: ${plist(mine.map(s => `${/^[aeiou]/i.test(s.prod) ? "an" : "a"} ${s.prod} at ${pmoney(s.amt)}${/winback/i.test(s.src) ? ", a winback" : /existing|cross/i.test(s.src) ? ", to a household we already insure" : ""}`))}` : ""}. That is ${n.pts} points and the top of the standings, on ${plural(n.dials, "dial")} and ${plural(n.hh, "quoted household")}.`);
  else if (n) S.paras.push(`${first} finished on top of the standings anyway, with ${n.pts} points from ${plural(n.dials, "dial")}, ${plural(n.live, "conversation")} and ${pmoney(n.pq)} quoted. The sale did not come.`);
  // the rest of the floor
  const floor = others.map(o => o.ps ? `${pfirst(o.n)} added ${pmoney(o.ps)}` : o.pq ? `${pfirst(o.n)} quoted ${pmoney(o.pq)} and is still waiting on it` : `${pfirst(o.n)} made ${plural(o.dials, "dial")} without a quote`);
  if (floor.length) S.paras.push(`The rest of the floor: ${plist(floor)}. ${F.ps ? `Together the team wrote ${pmoney(F.ps)} on ${plural(F.pol, "policy", "policies")}${F.hh ? `, closing ${F.hhSold} of ${F.hh} households` : ""}.` : `Nobody closed${F.hh ? `; ${plural(F.hh, "household")} quoted for ${pmoney(F.pq)} ${F.hh === 1 ? "is" : "are"} still open` : ""}.`}`);
  // what Apollo saw
  const saw = [];
  if (myFlags.length) saw.push(`On ${first}'s cards Apollo flagged ${myFlags.length === 1 ? "one thing" : `${myFlags.length} things`}: ${plist(myFlags.slice(0, 2).map(x => x.toLowerCase()))}.`);
  if (obj) saw.push(`Across the floor the objection of the ${X.isFolio ? "folio" : "day"} was ${obj[0]}, ${plural(obj[1], "time")}, ${obj[2] ? `turned ${obj[2] === obj[1] ? "every time" : `${obj[2]} of them`}` : "never turned"}.`);
  if (F.sendoffs.length) saw.push(`${plural(F.sendoffs.length, "quote")} left by email instead of being presented on the call.`);
  if (saw.length) S.paras.push(saw.join(" "));
  // the ask
  S.paras.push(busy ? `${nextDay}'s assignment is a time, not a maybe: when the next person says they are busy, the answer is "5 or 6, or tomorrow morning?"`
    : F.sendoffs.length ? `${nextDay}'s assignment is to stay on the line: build the quote while they are listening and ask for the sale before anyone offers to email anything.`
    : F.closeHH != null && F.closeHH < 25 ? `${nextDay}'s assignment is the close: ${F.hhSold} of ${F.hh} is under one in four. Assume the sale from the first sentence.`
    : `${nextDay}'s assignment is to do it again, and to dial the new leads inside two minutes.`);
  S.pull = quote ? [`"${quote}${/[.?!]$/.test(quote) ? "" : "."}"`, `${full}, to ${lead}, ${X.isFolio ? "this folio" : pdow(X.dayKey)}`]
    : obj ? [`${obj[0]} is not a no. It is a question the producer has not answered yet.`, "Apollo"]
    : ["The day is won on the second sentence, not the first.", "Apollo"];
  S.cover = [
    ["Inside", `${S.hl}.`],
    call ? ["The call", `${first} with ${lead}${call.dur ? `, ${call.dur}` : ""}${call.lead_source ? `, ${call.lead_source}` : ""}.`] : ["The phones", `${plural(F.dials, "dial")}, ${plural(F.live, "conversation")}, ${ppct(F.rate)}.`],
    obj ? ["The objection", `${obj[0]}, ${plural(obj[1], "time")}, ${obj[2]} overcome.`] : ["The quotes", `${plural(F.hh, "household")} for ${pmoney(F.pq)}.`],
    ["The standings", `${pmoney(X.FTOT)} after ${plural(X.rows.length, "day")} of the folio.`],
  ];
  return S;
}
function edCloser(X) {
  const F = X.F, top = X.order[0], n = X.NUM[top] || {}, pickC = edMine.cover || "illus";
  const port = { illus: `<div style="position:absolute;inset:0;background:linear-gradient(180deg,#e8dac9,#c9b8a8)"></div><div class="sil" style="--c:${X.C[top] || "#3f5f7a"}"></div>`,
    desert: `<div style="position:absolute;inset:0;background:linear-gradient(180deg,#f2c9a0 0,#e59a6f 38%,#b5532f 60%,#5a2416 100%)"></div><div style="position:absolute;left:0;right:0;bottom:0;height:34%;background:#2a2320;clip-path:polygon(0 60%,8% 40%,15% 55%,22% 20%,30% 50%,40% 35%,52% 60%,60% 30%,70% 45%,80% 25%,90% 50%,100% 40%,100% 100%,0 100%)"></div>`,
    number: `<div style="position:absolute;inset:0;background:#2a2320"></div><div style="position:absolute;left:14px;top:14px;right:14px;font:800 clamp(80px,14vw,150px)/.85 Fraunces,serif;color:#e59a6f;letter-spacing:-.04em">${Math.round(F.ps).toLocaleString()}</div>` }[pickC];
  const S = edMagStory(X), story = S.paras;
  const heights = [240, 200, 180, 110, 80];
  const podOrder = X.order.length >= 5 ? [X.order[3], X.order[1], X.order[0], X.order[2], X.order[4]] : X.order;
  const podH = X.order.length >= 5 ? [110, 200, 240, 180, 80] : heights.slice(0, X.order.length);
  const podRank = X.order.length >= 5 ? [4, 2, 1, 3, 5] : X.order.map((_, i) => i + 1);
  return `<div class="mag"><div class="cover"><div class="t">CLOSER</div><div class="port">${port}<span style="position:relative">${pickC === "number" ? edEsc(X.isFolio ? "The folio so far" : (X.rows.length && F.ps >= Math.max(...X.rows.map(r => r.ps)) ? "The folio’s best day" : pdow(X.dayKey))) : edEsc(X.full[top] || "The team")}<br><span style="font:700 16px var(--body)">${pickC === "number" ? edEsc(X.isFolio ? "" : plong(X.dayKey)) : `Producer of the ${X.isFolio ? "folio" : "day"} · ${n.pts || 0} points`}</span></span></div>
    <div class="cls">${S.cover.map(([b, t]) => `<div><b>${edEsc(b)}</b>${edEsc(t)}</div>`).join("")}</div>
    <div class="hrow"><span class="lab">Cover photo</span><div class="seg">${[["illus", "Illustrated portrait"], ["desert", "Sonoran"], ["number", "The number"]].map(([k, l]) => `<button type="button" data-cover="${k}" aria-pressed="${pickC === k}">${l}</button>`).join("")}</div></div></div>
   <div class="spread"><div class="k">Cover story</div><h2>${edEsc(S.hl)}</h2><p class="dek">${edEsc(S.dek)}</p><p>${edEsc(story[0] || "")}</p>
    <div class="pq">${edEsc(S.pull[0])}<small>${edEsc(S.pull[1])}</small></div>
    ${story.slice(1).map(p => `<p>${edEsc(p)}</p>`).join("")}
    <div class="k" style="margin-top:8px">By the numbers · drawn, not tabled</div>
    <div class="info"><div><b>${pmoney(F.ps)}</b><span>new premium · ${plural(F.pol, "policy", "policies")}</span></div><div><div class="ring" style="--p:${F.closeHH == null ? 0 : Math.min(100, Math.round(F.closeHH))}%"><i>${F.closeHH == null ? "—" : ppct(F.closeHH, 0)}</i></div><span>${F.hhSold} of ${F.hh} households bought</span></div><div><b>${F.spBest ? edFmtStd(F.spBest[1].median) : "—"}</b><span>${F.spBest ? `${pfirst(F.spBest[0])}’s first dial · team ${edFmtStd(F.spTeam)}` : "no new internet leads"}</span></div><div><b>${F.objs[0] ? `${F.objs[0][2]}/${F.objs[0][1]}` : ppct(F.rate)}</b><span>${F.objs[0] ? `${edEsc(F.objs[0][0])} overcome` : "contact rate"}</span></div></div>
    <div class="k" style="margin-top:8px">The podium</div><div class="podium">${podOrder.map((f, i) => `<div><b>${edEsc(f)}</b><small>${X.NUM[f].pts} pts · ${pmoney(X.NUM[f].ps)}</small><div class="blk" style="height:${podH[i]}px;background:${X.C[f]}22;color:${X.C[f]}">${podRank[i]}</div></div>`).join("")}</div>
</div><div class="masthead"><div class="k">The masthead · who did what, in full</div>${edLbt(X)}</div></div>`;
}

/* ===== the page ===== */
const ED_R = { feed: edFeed, grid: edGrid, pod: edPod, mkt: edMkt, comic: edComic, closer: edCloser };
let edX = null;
async function editionsPanel(err) {
  const today = isoDate(azTodayDate());
  const tabs = `<div class="subtabs edtabs">${ED_PUBS.map(([k, l]) => `<button type="button" class="subtab ${k === edPub ? "sel" : ""}" data-pub="${k}">${l}</button>`).join("")}</div>`;
  if (rangeMode === "day") {
    if (!cur) return tabs + postGateHtml("No report for this day yet.", "Pick a published day in Day, or choose Folio.");
    if (curLive || (cur.date === today && !DAYS.includes(today))) return tabs + postGateHtml("Today's editions come out after the 5:55 PM run.", "Pick a published day in Day, or choose Folio for the folio's editions.");
  } else if (rangeMode !== "folio") return tabs + postGateHtml("The editions are made for a published day or a folio.", `${RANGE_LABELS[rangeMode] || "That range"} is on the Digest. Pick a published day in Day, or choose Folio.`);
  else if (err) return tabs + postGateHtml("Nothing to print yet.", cesc(err));
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
  // The Flores Post is the first edition (Frank, 2026-10-01); it has its own
  // writer and gate in post.js.
  const body = edPub === "post" ? await postPanel(err) : ED_R[edPub](X);
  return `<div class="ed"><div class="subtabs edtabs">${ED_PUBS.map(([k, l]) => `<button type="button" class="subtab ${k === edPub ? "sel" : ""}" data-pub="${k}">${l}</button>`).join("")}
    <span class="eddl"><button type="button" class="ebtn q" data-eddl="pdf" title="Opens the print dialog; choose Save as PDF">Download PDF</button><button type="button" class="ebtn q" data-eddl="html" title="A single web page file of this edition, as it looks now">Save page</button></span></div><div id="edbody">${body}</div></div>`;
}
/* Downloadable editions (Frank, 2026-10-02: "make the editions
   downloadable"): the edition as it stands, with the board's own styles, as
   a single HTML file, or through the print dialog for a PDF. Buttons stay
   as they look but do nothing; a live edition's pictures are CSS, so they
   travel with it. */
function edExportDoc() {
  const R = document.documentElement, body = $("#edbody");
  if (!body) return null;
  const css = [...document.querySelectorAll("style")].map(el => el.textContent).join("\n");
  const fonts = [...document.querySelectorAll('link[rel="stylesheet"]')].map(l => l.outerHTML).join("");
  const pub = (ED_PUBS.find(p => p[0] === edPub) || [, "Edition"])[1];
  const when = edX ? (edX.isFolio ? `Folio to ${edX.folioEnd || ""}` : plong(edX.dayKey)) : "";
  const title = `${pub} · ${when}`;
  const html = `<!doctype html><html lang="en" data-look="${R.getAttribute("data-look") || "sonoran"}" data-mode="${R.getAttribute("data-mode") || "light"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${edEsc(title)}</title>${fonts}<style>${css}
body { margin: 0; padding: 24px; background: var(--surface); } .ed { max-width: 1600px; margin: 0 auto; } .ed button, .ed input, .ed form { pointer-events: none; } .ed form, .ed .eddl, .ed .edtabs { display: none; }
@media print { body { padding: 0; } * { -webkit-print-color-adjust: exact; print-color-adjust: exact; } .pc, .sect, .tile, .mag, .comic .panel { break-inside: avoid; } }</style></head>
<body><div class="ed"><div id="edbody">${body.innerHTML.replace(/src="memes\//g, `src="${new URL("memes/", location.href).href}`)}</div></div></body></html>`;
  const file = `${pub.replace(/[^A-Za-z0-9]+/g, "-").replace(/^-|-$/g, "")}-${edX ? (edX.isFolio ? "folio-" + (edX.folioEnd || "") : edX.dayKey) : "edition"}`;
  return { html, title, file };
}
function edDownload(kind) {
  const doc = edExportDoc(); if (!doc) return;
  if (kind === "html") {
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([doc.html], { type: "text/html" })); a.download = doc.file + ".html";
    document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000); edToast("Saved " + a.download); return;
  }
  const w = window.open("", "_blank"); if (!w) { edToast("Allow pop-ups to download the PDF"); return; }
  w.document.open(); w.document.write(doc.html); w.document.close();
  w.document.title = doc.title;
  const go = () => { try { w.focus(); w.print(); } catch (_) {} };
  if (w.document.fonts && w.document.fonts.ready) w.document.fonts.ready.then(() => setTimeout(go, 300)); else setTimeout(go, 800);
}
function edRepaint() { const b = $("#edbody"); if (b && edX) { if (edPub === "post") { paint(); return; } b.innerHTML = ED_R[edPub](edX); } }
function edOpenModal(h) { edCloseModal(); const m = document.createElement("div"); m.className = "edmodal ed"; m.id = "edmodal"; m.innerHTML = `<div class="edcard">${h}</div>`; m.addEventListener("click", e => { if (e.target === m) edCloseModal(); }); document.body.appendChild(m); }
function edCloseModal() { const m = $("#edmodal"); if (m) m.remove(); }
document.addEventListener("click", async e => {
  if (view !== "editions" || !edX) return;
  const t = e.target, d = k => t.closest(`[data-${k}]`); let el;
  if (el = d("pub")) { edPub = el.dataset.pub; try { localStorage.setItem("board-edition", edPub); } catch (_) {} clearInterval(edTick); edPlaying = false; paint(); return; }
  if (el = d("rx")) { const id = el.closest("[data-post]").dataset.post; if (await edPost("rx", { id, emoji: el.dataset.rx })) edRepaint(); return; }
  if (el = d("eddl")) { edDownload(el.dataset.eddl); return; }
  if (el = d("gifpick")) { edGifOpen = edGifOpen === el.dataset.gifpick ? "" : el.dataset.gifpick; edRepaint(); return; }
  if (el = d("gif")) { const id = el.closest("[data-post]").dataset.post; edGifOpen = ""; if (await edPost("cm", { id, gif: el.dataset.gif, text: "" })) edRepaint(); return; }
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
