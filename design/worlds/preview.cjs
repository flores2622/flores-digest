// usage: node preview.cjs <key>  -> out/<key>/sky.png (Digest mock, light+dark) and out/<key>/sheet.png (vistas + strips)
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const key=process.argv[2];const D=path.join(__dirname,'out',key);const meta=JSON.parse(fs.readFileSync(path.join(D,'meta.json'),'utf8'));
const u=n=>`url('data:image/svg+xml;utf8,${encodeURIComponent(fs.readFileSync(path.join(D,n+'.svg'),'utf8'))}')`;
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
// 1. the Digest: top card (tiles over the picture from the top) and the leaderboard card (same picture from 377 of 1700 down)
let h='<body style="margin:0;background:#888;font-family:sans-serif">';
for(const m of ['l','d']){
 const sky=fs.readFileSync(path.join(D,`sky_${m}.svg`),'utf8');const lb=sky.replace('viewBox="0 0 1600 1700"','viewBox="0 377 1600 1323"');
 h+=`<div style="width:1420px;margin:10px;border-radius:16px;overflow:hidden;padding:150px 18px 18px;background:${u('sky_'+m)} center top/100% auto no-repeat;position:relative">
  <b style="position:absolute;left:24px;top:22px;color:#fff;font-size:30px;text-shadow:0 1px 3px #000">The day on the floor</b>
  <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:12px">${'<div style="height:190px;border-radius:10px;background:rgba(250,250,250,.93)"></div>'.repeat(7)}</div></div>
 <div style="width:1420px;margin:10px;border-radius:16px;overflow:hidden;padding:18px 20px;height:560px;background:url('data:image/svg+xml;utf8,${encodeURIComponent(lb)}') center top/100% auto no-repeat;position:relative">
  <b style="color:#fff;font-size:28px;text-shadow:0 1px 3px #000">Team Leaderboard</b>
  <div style="position:absolute;left:420px;width:580px;top:180px;display:flex;justify-content:center;gap:6px;align-items:flex-end">${[[0,150],[90,180],[130,160],[70,200],[0,220]].map(([x,t])=>`<div style="width:110px;display:flex;flex-direction:column;align-items:center;gap:4px"><div style="width:44px;height:44px;border-radius:50%;background:#c58af0;border:3px solid #fff"></div><b style="color:#fff;font:700 13px sans-serif;text-shadow:0 1px 2px #000">Producer</b>${x?`<div style="width:100px;height:${x}px;background:#e0b030;border-radius:6px 6px 0 0"></div>`:'<div style="height:0"></div>'}</div>`).join('')}</div>
  <div style="position:absolute;left:20px;right:20px;top:420px;bottom:0;background:rgba(250,250,250,.96);border-radius:10px"></div></div>`;}
h+='</body>';let pg=await b.newPage({viewport:{width:1460,height:900}});await pg.setContent(h);await pg.screenshot({path:path.join(D,'sky.png'),fullPage:true});
// 2. vistas (170px banner, title bottom-left, line bottom-right) and card strips (58px band, outcome pill at the right)
const V=["sales","messages","coaching","roleplay","rphistory","training","blueprint","athenamap","service","renewals","claims","commercial"];
const S=["sold_on_call","quoted_call_open","quoted_call_lost","dead_no_quote","live_quote_ok","live_no_quote","callback_no_contact"];
h='<body style="margin:0;background:#333;display:grid;grid-template-columns:1fr 1fr;gap:6px;padding:6px;font-family:sans-serif">';
for(const k of V)for(const m of ['l','d'])h+=`<div style="height:170px;border-radius:12px;background:${u(`v_${k}_${m}`)} center/cover;position:relative"><b style="position:absolute;left:18px;bottom:12px;color:#fff;font-size:26px;text-shadow:0 1px 3px rgba(0,0,0,.6)">${meta.lines[k][0]}</b><span style="position:absolute;right:18px;bottom:16px;color:#fff;font:700 11px sans-serif;letter-spacing:.08em;text-transform:uppercase;text-shadow:0 1px 3px rgba(0,0,0,.6)">${meta.lines[k][1]}</span></div>`;
for(const k of S)for(const m of ['l','d'])h+=`<div style="height:58px;border-radius:8px 8px 0 0;background:${u(`s_${k}_${m}`)} center/cover;position:relative"><span style="position:absolute;right:12px;top:16px;background:#ffd27a;border:2px solid #b8860b;border-radius:99px;padding:3px 10px;font:700 11px sans-serif">OUTCOME PILL</span><i style="position:absolute;left:6px;bottom:2px;color:#fff;font:10px sans-serif;opacity:.7">${k}</i></div>`;
h+='</body>';pg=await b.newPage({viewport:{width:1440,height:2400}});await pg.setContent(h);await pg.screenshot({path:path.join(D,'sheet.png'),fullPage:true});
await b.close();console.log('wrote',path.join(D,'sky.png'),path.join(D,'sheet.png'))})();
