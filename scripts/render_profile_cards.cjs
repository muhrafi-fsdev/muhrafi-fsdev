// Generate the README's visual bio and six project covers. Run with Node 18+ and sharp.
const fs = require('node:fs/promises');
const path = require('node:path');
const sharp = require('sharp');
const ROOT = path.join(__dirname, '../assets/nightshift');
const OUT = path.join(ROOT,'profile-cards');
const MODES = {
 dark: {bg:'#101a2a', rail:'#111f31', border:'#2b425b', muted:'#9eb8d2', ink:'#edf5ff', blue:'#83d2ff', tile:'#18283d', photo:'#132337'},
 light: {bg:'#f3f7fd', rail:'#e5eef9', border:'#bbd0e7', muted:'#425e7b', ink:'#112c4a', blue:'#176995', tile:'#e7f0fb', photo:'#edf4fc'},
};
const REPOS = [
 ['zenith','NusaMind Zenith','LOCAL AI','A workspace for multi-file projects','#c5afff','#644ba3',
  '<path d="m0-48 60 33-60 35-60-35z"/><path d="m-60 0 60 35 60-35m-120 17 60 35 60-35"/><path d="M0-22v23m-12-12h24"/>'],
 ['swift','NusaMind Swift','LOCAL AI','File analysis, retrieval and memory','#8ddaff','#126d9e',
  '<path d="M-12-46 39 0-12 46l11-33-44-13 44-13z"/><path d="M-71-28h36m-60 28h34m-10 28h36M26-26l30 26-30 26"/>'],
 ['monitor','NusaMonitor','LIVE MAPS','Public live data mapped for Indonesia','#83e4d0','#167c72',
  '<circle cx="0" cy="0" r="48"/><circle cx="0" cy="0" r="31"/><circle cx="0" cy="0" r="14"/><path d="M-57 0H57M0-57V57M0 0l32-32"/><circle cx="22" cy="12" r="3" fill="currentColor"/>'],
 ['ryka','RYKA Core','DESKTOP TOOLS','Gesture-driven desktop interaction','#ffcb8c','#8d5519',
  '<rect x="-45" y="-44" width="37" height="37" rx="6"/><rect x="8" y="-44" width="37" height="37" rx="6"/><rect x="-45" y="7" width="37" height="37" rx="6"/><rect x="8" y="7" width="37" height="37" rx="6"/><path d="M0-54v108m-55-54h110" stroke-dasharray="4 7"/>'],
 ['raystore','RayStore','WEB APP','A game top-up storefront prototype','#ffa89e','#a64b54',
  '<path d="M-45-31h18l12 53h47l10-37h-63"/><circle cx="-10" cy="37" r="7"/><circle cx="27" cy="37" r="7"/><path d="m9-25-9 14h14l-8 15"/>'],
 ['academic','Academic Organizer','STUDENT TOOLS','Tasks, schedules and academic planning','#a4c4ff','#3f5d9b',
  '<rect x="-47" y="-36" width="94" height="78" rx="9"/><path d="M-47-13h94m-70-34v20m46-20v20m-49 36h11m12 0h11m12 0h11m-57 14h11m12 0h11"/>'],
];
const svg = (w,h,body) => Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${body}</svg>`);
const txt = ({x,y,s,c,sz=22,weight=400,font='DejaVu Sans'}) =>
  `<text x="${x}" y="${y}" fill="${c}" font-family="${font},sans-serif" font-size="${sz}" font-weight="${weight}">${s}</text>`;
const mono = (x,y,s,c,sz=16) => txt({x,y,s,c,sz,font:'DejaVu Sans Mono'});

function marks(w,h,c) {
  return `<path d="M19 44V19h25 M${w-44} 19h25v25 M19 ${h-44}v25h25 M${w-44} ${h-19}h25v-25" fill="none" stroke="${c}" stroke-width="2" stroke-opacity=".55"/>`;
}
async function cover(mode,i) {
  const p=MODES[mode], [id,name,tag,description,dark,light,art]=REPOS[i];
  const accent=mode==='dark'?dark:light, w=760,h=206;
  const frame=svg(w,h,`
    <defs><linearGradient id="a"><stop stop-color="${p.bg}"/><stop offset="1" stop-color="${p.rail}"/></linearGradient></defs>
    <rect x="1" y="1" width="758" height="204" rx="16" fill="url(#a)" stroke="${p.border}" stroke-width="2"/>
    <path d="M18 18V188" stroke="${accent}" stroke-width="3"/>
    <circle cx="642" cy="105" r="77" fill="${accent}" fill-opacity=".07"/>
    <circle cx="642" cy="105" r="77" fill="none" stroke="${accent}" stroke-opacity=".24"/>
    <circle cx="642" cy="105" r="62" fill="none" stroke="${accent}" stroke-opacity=".39" stroke-dasharray="2 7"/>
    <g transform="translate(642 105)" fill="none" color="${accent}" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">${art}</g>
    <rect x="39" y="35" width="8" height="8" rx="2" fill="${accent}"/>
    ${mono(61,45,`0${i+1} / ${tag}`,accent,19)}
    ${txt({x:38,y:105,s:name,c:p.ink,sz:43,weight:700})}
    ${txt({x:40,y:148,s:description,c:p.muted,sz:21})}
    <path d="M40 174H507 m15 0h14" stroke="${p.border}" stroke-width="2"/>
    <path d="M725 27h10v10m0-10-13 13" fill="none" stroke="${accent}" stroke-width="1.7"/>
  `);
  await sharp(frame).webp({quality:94}).toFile(path.join(OUT,`repo-${id}-${mode}.webp`));
}

const FIELD = [
 ['01','STUDYING','Telecommunication Engineering','Telkom University',
  '<path d="M-14-8c5-2 10-1 14 2 4-3 9-4 14-2v17c-6-2-10-1-14 2-4-3-8-4-14-2z M0-6v17"/>'],
 ['02','BUILDING','Web apps and local-first AI','NusaMind and personal tools',
  '<rect x="-15" y="-11" width="30" height="22" rx="4"/><path d="m-9-4 5 4-5 4m9 1h7"/>'],
 ['03','ON THE BENCH','Raspberry Pi and MQTT','IoT experiments',
  '<circle cx="0" cy="5" r="2"/><path d="M-7 1a10 10 0 0 1 14 0 M-12-4a17 17 0 0 1 24 0 M-16-9a23 23 0 0 1 32 0"/>'],
];
async function bio(mode,compact) {
  const p=MODES[mode], w=compact?704:1160, h=compact?574:399;
  const left=compact?26:30, rowWidth=compact?652:730, rowHeight=compact?113:86;
  const start=compact?179:94, step=compact?120:91;
  const cx=compact?568:946,cy=compact?95:205,rad=compact?67:151;
  const rowColors=mode==='dark'?['#8fd2fd','#c9b8ff','#8ae4cb']:['#166795','#6551a3','#16756b'];
  const rows=FIELD.map(([num,label,line,second,icon],i)=>{
    const y=start+i*step, tone=rowColors[i], iconX=left+(compact?47:42), from=left+(compact?104:92);
    return `<rect x="${left}" y="${y}" width="${rowWidth}" height="${rowHeight}" rx="11" fill="${p.tile}" stroke="${p.border}"/>
      <rect x="${left}" y="${y+12}" width="3" height="${rowHeight-24}" rx="2" fill="${tone}"/>
      <circle cx="${iconX}" cy="${y+rowHeight/2}" r="${compact?27:25}" fill="${tone}" fill-opacity=".13" stroke="${tone}" stroke-opacity=".55"/>
      <g transform="translate(${iconX} ${y+rowHeight/2})" stroke="${tone}" fill="none" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">${icon}</g>
      ${mono(from,y+(compact?30:23),`${num} / ${label}`,tone,compact?21:16)}
      ${txt({x:from,y:y+(compact?66:54),s:line,c:p.ink,sz:compact?29:26,weight:700})}
      ${txt({x:from,y:y+(compact?95:75),s:second,c:p.muted,sz:compact?21:17})}`;
  }).join('');
  const frame=svg(w,h,`
    <rect x="1" y="1" width="${w-2}" height="${h-2}" rx="17" fill="${p.bg}" stroke="${p.border}" stroke-width="2"/>
    ${marks(w,h,p.blue)}
    <path d="M${left} ${compact?156:76}H${left+rowWidth} ${compact?'':'M784 78v280'}" stroke="${p.border}" fill="none"/>
    <circle cx="${cx}" cy="${cy}" r="${rad}" fill="${p.photo}" stroke="${p.border}" stroke-width="1.5"/>
    <circle cx="${cx}" cy="${cy}" r="${rad-15}" fill="none" stroke="${p.blue}" stroke-opacity=".28" stroke-dasharray="2 8"/>
    ${mono(compact?35:30,compact?51:44,'FIELD NOTES',p.blue,compact?23:20)}
    ${txt({x:compact?35:211,y:compact?109:45,s:'Rafi / Web, AI &amp; Telecom',c:p.ink,sz:compact?33:23,weight:700})}
    ${compact?'':mono(833,374,'SIDEKICK / RADIO CREW',p.muted,15)}
    ${rows}`);
  const mascot=await sharp(path.join(ROOT,'mascot.webp')).resize({width:compact?122:257,height:compact?122:257,fit:'inside'})
    .png().toBuffer({resolveWithObject:true});
  await sharp(frame).composite([{input:mascot.data,left:Math.round(cx-mascot.info.width/2),top:Math.round(cy-mascot.info.height/2)}])
    .webp({quality:94}).toFile(path.join(OUT,`about-${mode}${compact?'-compact':''}.webp`));
}
(async()=>{
 await fs.mkdir(OUT,{recursive:true});
 for(const mode of Object.keys(MODES)) await Promise.all([
  bio(mode,false),bio(mode,true),...REPOS.map((_,i)=>cover(mode,i))
 ]);
})().catch(e=>{console.error(e);process.exitCode=1;});
