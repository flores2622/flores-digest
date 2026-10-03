// Renders the app icon SVGs to the PNGs the board serves (see app_icon.py).
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const out=path.join(__dirname,'..','site','public','app');fs.mkdirSync(out,{recursive:true});
for(const [src,name,px] of [['app_icon.svg','icon-180.png',180],['app_icon.svg','icon-192.png',192],['app_icon.svg','icon-512.png',512],['app_icon_maskable.svg','icon-maskable-512.png',512],['app_icon.svg','favicon-32.png',32]]){
 const svg=fs.readFileSync(path.join(__dirname,src),'utf8');const pg=await b.newPage({viewport:{width:px,height:px}});
 await pg.setContent(`<body style="margin:0">${svg.replace('width="1024" height="1024"',`width="${px}" height="${px}"`)}</body>`);
 await pg.screenshot({path:path.join(out,name),omitBackground:false});await pg.close();console.log(name);}
await b.close()})();
