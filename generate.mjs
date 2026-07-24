import fs from "node:fs";
import path from "node:path";

const username = process.env.GH_USERNAME || "muhrafi-fsdev";
const token = process.env.GH_TOKEN;
if (!token) {
  console.error("GH_TOKEN belum diatur. Set environment variable GH_TOKEN lalu jalankan kembali.");
  process.exit(1);
}

const now = new Date();
const from = new Date(now);
from.setUTCFullYear(now.getUTCFullYear() - 1);

const query = `query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){
    contributionsCollection(from:$from,to:$to){
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount weekday } }
      }
    }
  }
}`;

const response = await fetch("https://api.github.com/graphql", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json",
    "User-Agent": "muhrafi-profile-heatmap-generator"
  },
  body: JSON.stringify({ query, variables: { login: username, from: from.toISOString(), to: now.toISOString() } })
});

if (!response.ok) throw new Error(`GitHub API error ${response.status}: ${await response.text()}`);
const payload = await response.json();
if (payload.errors) throw new Error(JSON.stringify(payload.errors, null, 2));
const calendar = payload.data?.user?.contributionsCollection?.contributionCalendar;
if (!calendar) throw new Error(`Contribution data untuk ${username} tidak ditemukan.`);

const flat = calendar.weeks.flatMap(w => w.contributionDays);
const positive = flat.map(d => d.contributionCount).filter(Boolean).sort((a,b)=>a-b);
const q = p => positive.length ? positive[Math.min(positive.length-1, Math.floor((positive.length-1)*p))] : 1;
const thresholds = [0, q(.25), q(.5), q(.75), q(.92)];
const level = count => {
  if (!count) return 0;
  if (count <= thresholds[1]) return 1;
  if (count <= thresholds[2]) return 2;
  if (count <= thresholds[3]) return 3;
  return 4;
};

const themes = {
  dark: { bg:"#030712", panel:"#0F172A", text:"#F8FAFC", muted:"#94A3B8", border:"rgba(255,255,255,.09)", cells:["#182235","#312E81","#2563EB","#06B6D4","#10B981"], a:"#7C3AED", b:"#22D3EE", c:"#10B981" },
  light:{ bg:"#FFFFFF", panel:"#F8FAFC", text:"#0F172A", muted:"#475569", border:"rgba(15,23,42,.09)", cells:["#E2E8F0","#BFDBFE","#60A5FA","#06B6D4","#10B981"], a:"#2563EB", b:"#06B6D4", c:"#10B981" }
};

function escapeXml(value){return String(value).replace(/[<>&'\"]/g,ch=>({"<":"&lt;",">":"&gt;","&":"&amp;","'":"&apos;",'"':"&quot;"}[ch]));}
function makeSvg(themeName){
  const t=themes[themeName];
  const cell=13, gap=5, step=18, startX=92, startY=91;
  const cells=[];
  calendar.weeks.forEach((week, wi)=>week.contributionDays.forEach(day=>{
    const x=startX+wi*step, y=startY+day.weekday*step, l=level(day.contributionCount);
    cells.push(`<g><title>${escapeXml(day.date)}: ${day.contributionCount} contributions</title><rect x="${x}" y="${y}" width="${cell}" height="${cell}" rx="3" fill="${t.cells[l]}"><animate attributeName="opacity" values=".72;1;.72" dur="${4+(wi%9)*.22}s" repeatCount="indefinite"/></rect></g>`);
  }));
  const first = flat[0]?.date || ""; const last = flat.at(-1)?.date || "";
  return `<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 1180 270" role="img" aria-labelledby="title desc">
  <title id="title">${escapeXml(username)} GitHub contribution flight</title><desc id="desc">Animated contribution heatmap from ${first} to ${last}, totaling ${calendar.totalContributions} public contributions.</desc>
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="${t.a}"/><stop offset=".5" stop-color="${t.b}"/><stop offset="1" stop-color="${t.c}"/><animate attributeName="x1" values="0;.35;0" dur="6s" repeatCount="indefinite"/></linearGradient>
    <filter id="gl" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <rect x="5" y="5" width="1170" height="260" rx="26" fill="${t.panel}" stroke="${t.border}"/>
  <text x="54" y="49" fill="${t.text}" font-size="24" font-weight="800" font-family="ui-sans-serif,system-ui">Contribution Flight</text>
  <text x="54" y="70" fill="${t.muted}" font-size="12.5" font-family="ui-monospace,monospace">${escapeXml(username)} · ${calendar.totalContributions} public contributions · last 12 months</text>
  ${cells.join("")}
  <path id="flight" d="M92 226 C270 192 380 208 548 150 S830 70 1080 119" fill="none" stroke="url(#g)" stroke-width="2" stroke-dasharray="6 10" opacity=".48"/>
  <g filter="url(#gl)"><path d="M-8 -7 L18 0 L-8 7 L-2 0 Z" fill="url(#g)"/><animateMotion dur="8s" repeatCount="indefinite" rotate="auto"><mpath href="#flight"/></animateMotion></g>
  <circle r="3" fill="${t.b}" opacity=".55"><animateMotion dur="8s" begin="-.45s" repeatCount="indefinite"><mpath href="#flight"/></animateMotion><animate attributeName="opacity" values="0;.65;0" dur="1.2s" repeatCount="indefinite"/></circle>
  <text x="1128" y="49" text-anchor="end" fill="${t.muted}" font-size="12" font-family="ui-monospace,monospace">${first} → ${last}</text>
  </svg>`;
}

const out = path.resolve("assets/heatmap");
fs.mkdirSync(out,{recursive:true});
for (const theme of ["dark","light"]) fs.writeFileSync(path.join(out,`${theme}.svg`),makeSvg(theme),"utf8");
console.log(`Heatmap berhasil dibuat untuk ${username}: ${calendar.totalContributions} contributions.`);
