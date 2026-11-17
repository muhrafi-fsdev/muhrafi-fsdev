// Run with Node 18+ and sharp from the repo root.
// The dashboard uses the dated SVG snapshot rendered by render_profile_activity.py.
const sharp = require('sharp');
const path = require('node:path');
const fs = require('node:fs/promises');

const A = path.resolve(__dirname,'../assets/nightshift');
const OUT = path.join(A,'refined');
const THEMES = {
  dark:{paper:'#101827',inside:'#141e2f',alt:'#121b2b',line:'#26384f',ink:'#e9f0fa',dim:'#9eb2cc',accent:'#75caff'},
  light:{paper:'#f5f8fd',inside:'#ffffff',alt:'#edf4fc',line:'#cedded',ink:'#182b45',dim:'#466284',accent:'#176b9a'},
};
const TOOLS = [
  ['typescript','TypeScript'],['react','React'],['nodejs','Node.js'],['php','PHP'],
  ['python','Python'],['javascript','JavaScript'],['sqlite','SQLite'],['postgresql','PostgreSQL'],
  ['docker','Docker'],['linux','Linux'],['raspberrypi','Raspberry Pi'],['git','Git'],
];

function svg(w,h,inner) {
  return Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${inner}</svg>`);
}

async function toolkit(theme,cols,icons) {
  const c=THEMES[theme], cw=176, ch=121;
  const w=cw*cols, h=ch*12/cols;
  let parts=`<rect x="1" y="1" width="${w-2}" height="${h-2}" rx="13" fill="${c.paper}" stroke="${c.line}" stroke-width="2"/>`;
  const overlays=[];
  for(const [i,[key,name]] of TOOLS.entries()) {
    const x=i%cols*cw,y=Math.floor(i/cols)*ch;
    parts+=`<rect x="${x+7}" y="${y+7}" width="${cw-14}" height="${ch-14}" rx="8" fill="${i%2===0?c.inside:c.alt}" stroke="${c.line}"/>
      <text x="${x+cw/2}" y="${y+96}" text-anchor="middle" font-family="DejaVu Sans,sans-serif" font-size="22" font-weight="500" fill="${c.ink}">${name}</text>`;
    const icon=icons[i];
    overlays.push({input:icon.data,left:Math.round(x+(cw-icon.info.width)/2),top:19+y+Math.floor((55-icon.info.height)/2)});
  }
  await sharp(svg(w,h,parts)).composite(overlays).webp({quality:93})
    .toFile(path.join(OUT,`toolkit-${theme}${cols===4?'-compact':''}.webp`));
}

async function activity(theme) {
  const c=THEMES[theme], w=1160,h=424;
  const bg=svg(w,h,`
    <rect x="1" y="1" width="1158" height="422" rx="17" fill="${c.paper}" stroke="${c.line}" stroke-width="2"/>
    <path d="M26 67H806 M829 26V395" stroke="${c.line}" stroke-width="2"/>
    <path d="M977 49v321 M851 216h275" stroke="${c.line}" stroke-dasharray="3 9"/>
    <circle cx="977" cy="216" r="119" fill="${c.alt}" stroke="${c.line}"/>
    <circle cx="977" cy="216" r="103" fill="none" stroke="${c.line}" stroke-dasharray="2 9"/>
    <text x="30" y="45" fill="${c.accent}" font-family="DejaVu Sans Mono,monospace" font-size="20" letter-spacing="2">01 / CONTRIBUTION LOG</text>
    <text x="1128" y="45" text-anchor="end" fill="${c.dim}" font-family="DejaVu Sans Mono,monospace" font-size="14" letter-spacing="1.2">AFTER HOURS</text>
    <text x="30" y="393" fill="${c.dim}" font-family="DejaVu Sans Mono,monospace" font-size="14" letter-spacing="1">SOURCE / GITHUB PUBLIC CALENDAR</text>`);
  const old=await fs.readFile(path.join(A,`activity-${theme}.svg`),'utf8');
  // Strip only the self-generated outer card. Keep data, semantic labels and scales.
  const chart=await sharp(Buffer.from(old.replace(/<rect x="\.5"[^>]*\/>/,'').replace(/#f2f6fc/g,c.paper)))
    .resize({width:798}).png().toBuffer();
  const art=await sharp(path.join(OUT,'operator.webp')).resize({height:341,width:275,fit:'inside'})
    .png().toBuffer({resolveWithObject:true});
  await sharp(bg).composite([
    {input:chart,left:16,top:80},
    {input:art.data,left:Math.floor(977-art.info.width/2),top:61+Math.floor((341-art.info.height)/2)},
  ]).webp({quality:93}).toFile(path.join(OUT,`activity-${theme}-wide.webp`));
}

async function socials() {
  const ICONS = {
    portfolio:'<rect x="11" y="13" width="18" height="14" rx="2"/><path d="M11 17h18m-14 4h5"/>',
    linkedin:'<path d="M13 18v9m0-14v1m6 13v-9m0 3c3-5 8-4 8 1v5"/>',
    instagram:'<rect x="11" y="11" width="18" height="18" rx="5"/><circle cx="20" cy="20" r="4"/><path d="M25 15h.1"/>',
    email:'<rect x="11" y="13" width="18" height="14" rx="2"/><path d="m11 15 9 7 9-7"/>',
  };
  await Promise.all(Object.entries(ICONS).map(([key,shape])=>fs.writeFile(path.join(OUT,`${key}.svg`),
    svg(40,40,`<rect x="1" y="1" width="38" height="38" rx="10" fill="#17253a" stroke="#466487" stroke-width="1.5"/><g stroke="#cfebff" stroke-width="1.65" fill="none" stroke-linecap="round" stroke-linejoin="round">${shape}</g>`))));
}

async function main() {
  await fs.mkdir(OUT,{recursive:true});
  const icons=await Promise.all(TOOLS.map(([key])=>sharp(path.join(A,'toolkit',key+(key==='linux'?'.webp':'.svg')),
      {density:144}).resize(55,55,{fit:'inside'}).png().toBuffer({resolveWithObject:true})));
  await Promise.all([socials(),...Object.keys(THEMES).flatMap(theme=>
    [toolkit(theme,6,icons),toolkit(theme,4,icons),activity(theme)])]);
}
main().catch(err=>{console.error(err);process.exitCode=1;});
