#!/usr/bin/env node
/**
 * Render Nightshift Signal Desk assets:
 * - Desktop & compact mobile hero banners (dark/light SVG)
 * - Labeled social link buttons (dark/light SVG)
 * - Subtle frame-based signal pulse divider (animated WebP + static fallback via ffmpeg)
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import zlib from 'node:zlib';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'assets', 'nightshift', 'signal-desk');

const THEMES = {
  dark: {
    bg0: '#0d131f',
    bg1: '#121b2b',
    bar: '#152033',
    panel: '#0a101a',
    pill: '#152236',
    border: '#26354d',
    borderSoft: '#1c293d',
    ink: '#f3f7ff',
    muted: '#9fb3cf',
    dim: '#6e83a3',
    cyan: '#67d4ff',
    cyanBg: '#122b3d',
    amber: '#f0b35a',
    amberBg: '#2b2216',
    dot: '#4d607d',
  },
  light: {
    bg0: '#f4f7fc',
    bg1: '#e6eef9',
    bar: '#e1ebf7',
    panel: '#ffffff',
    pill: '#edf3fb',
    border: '#c2d3e8',
    borderSoft: '#d7e3f2',
    ink: '#0f1f36',
    muted: '#425b78',
    dim: '#667e9c',
    cyan: '#0d6c96',
    cyanBg: '#dff0fa',
    amber: '#a85c0d',
    amberBg: '#faeedc',
    dot: '#98aec9',
  },
};

const FONT_SANS = 'DejaVu Sans, Segoe UI, -apple-system, BlinkMacSystemFont, Arial, sans-serif';
const FONT_MONO = 'DejaVu Sans Mono, Consolas, ui-monospace, monospace';

function wavePath(x0, y0, width, amp, cycles, samples = 90) {
  const pts = [];
  for (let i = 0; i <= samples; i++) {
    const t = i / samples;
    const x = x0 + t * width;
    const env = Math.sin(Math.PI * t);
    const y = y0 + Math.sin(t * Math.PI * 2 * cycles) * amp * env;
    pts.push(`${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`);
  }
  return pts.join(' ');
}

function focusIcons(c1, c2) {
  return {
    nusamind: `<g stroke="${c1}" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z"/><path d="M12 12l8-4.5M12 12v9M12 12L4 7.5"/></g>`,
    nusmonitor: `<g stroke="${c1}" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="3.5"/><path d="M12 3.5v3M12 17.5v3M3.5 12h3M17.5 12h3"/></g>`,
    iot: `<g stroke="${c2}" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="16" r="2"/><path d="M7.8 12.2a6 6 0 0 1 8.4 0"/><path d="M4.6 9a10.5 10.5 0 0 1 14.8 0"/><path d="M12 18v3"/></g>`,
  };
}

function renderHeroDesktop(mode) {
  const t = THEMES[mode];
  const icons = focusIcons(t.cyan, t.amber);
  const bgWave = wavePath(42, 232, 660, 26, 4.5, 110);
  const panelWave = wavePath(780, 256, 316, 13, 4, 80);

  return `<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="320" viewBox="0 0 1160 320" role="img" aria-labelledby="title desc">
  <title id="title">Muhammad Rafi Priyo Sembodo — Nightshift Signal Desk</title>
  <desc id="desc">Terminal-styled profile banner for Muhammad Rafi Priyo Sembodo with verified focus on NusaMind, NusaMonitor, and Raspberry Pi MQTT experiments.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${t.bg0}"/>
      <stop offset="100%" stop-color="${t.bg1}"/>
    </linearGradient>
    <clipPath id="frameClip"><rect x="1" y="1" width="1158" height="318" rx="16"/></clipPath>
  </defs>

  <rect x="1" y="1" width="1158" height="318" rx="16" fill="url(#bg)" stroke="${t.border}" stroke-width="2"/>
  <g clip-path="url(#frameClip)">
    <!-- Terminal Header -->
    <rect x="0" y="0" width="1160" height="38" fill="${t.bar}"/>
    <line x1="0" y1="38" x2="1160" y2="38" stroke="${t.border}" stroke-width="1"/>
    <circle cx="24" cy="19" r="5" fill="${t.dot}"/>
    <circle cx="42" cy="19" r="5" fill="${t.dot}"/>
    <circle cx="60" cy="19" r="5" fill="${t.dot}"/>
    <text x="84" y="24" fill="${t.muted}" font-family="${FONT_MONO}" font-size="13" font-weight="500">muhrafi-fsdev — signal-desk</text>
    <text x="1126" y="24" text-anchor="end" fill="${t.dim}" font-family="${FONT_MONO}" font-size="12" letter-spacing="0.8">TELKOM UNIV · ID</text>

    <!-- Subtle background signal trace -->
    <line x1="42" y1="232" x2="702" y2="232" stroke="${t.borderSoft}" stroke-width="1" stroke-dasharray="3 6"/>
    <path d="${bgWave}" fill="none" stroke="${t.cyan}" stroke-opacity="0.14" stroke-width="2"/>
    <circle cx="207" cy="232" r="3" fill="${t.cyan}" fill-opacity="0.35"/>
    <circle cx="537" cy="232" r="3" fill="${t.amber}" fill-opacity="0.45"/>

    <!-- Left Main Identity -->
    <text x="44" y="74" fill="${t.cyan}" font-family="${FONT_MONO}" font-size="14" font-weight="600">&gt; whoami --desk</text>
    <line x1="44" y1="96" x2="44" y2="206" stroke="${t.cyan}" stroke-width="3.5" stroke-linecap="round"/>

    <text x="64" y="144" fill="${t.ink}" font-family="${FONT_SANS}" font-size="56" font-weight="700" letter-spacing="-1.4">Muhammad Rafi</text>
    <text x="64" y="204" fill="${t.ink}" font-family="${FONT_SANS}" font-size="56" font-weight="700" letter-spacing="-1.4">Priyo Sembodo</text>

    <text x="44" y="244" fill="${t.muted}" font-family="${FONT_SANS}" font-size="17" font-weight="500">Telecommunication Engineering · Web Development · Local AI</text>

    <!-- Topic Pills -->
    <g font-family="${FONT_MONO}" font-size="12.5" font-weight="600">
      <rect x="44" y="264" width="102" height="28" rx="7" fill="${t.pill}" stroke="${t.border}"/>
      <text x="95" y="282" text-anchor="middle" fill="${t.cyan}">Web Apps</text>

      <rect x="156" y="264" width="98" height="28" rx="7" fill="${t.pill}" stroke="${t.border}"/>
      <text x="205" y="282" text-anchor="middle" fill="${t.ink}">Local AI</text>

      <rect x="264" y="264" width="166" height="28" rx="7" fill="${t.amberBg}" stroke="${t.amber}" stroke-opacity="0.55"/>
      <text x="347" y="282" text-anchor="middle" fill="${t.amber}">Raspberry Pi · MQTT</text>
    </g>

    <!-- Right Focus Panel -->
    <rect x="756" y="56" width="370" height="240" rx="12" fill="${t.panel}" stroke="${t.border}" stroke-width="1.5"/>
    <text x="778" y="84" fill="${t.cyan}" font-family="${FONT_MONO}" font-size="12.5" font-weight="700" letter-spacing="1.1">VERIFIED FOCUS</text>
    <text x="1104" y="84" text-anchor="end" fill="${t.dim}" font-family="${FONT_MONO}" font-size="11.5">3 TRACKS</text>
    <line x1="778" y1="96" x2="1104" y2="96" stroke="${t.borderSoft}" stroke-width="1"/>

    <!-- Row 1: NusaMind -->
    <g transform="translate(778, 110)">
      <rect width="32" height="32" rx="8" fill="${t.cyanBg}"/>
      <g transform="translate(4, 4)">${icons.nusamind}</g>
      <text x="44" y="14" fill="${t.ink}" font-family="${FONT_SANS}" font-size="15" font-weight="700">NusaMind</text>
      <text x="44" y="31" fill="${t.muted}" font-family="${FONT_SANS}" font-size="12.5">Local-first AI workspace</text>
    </g>

    <!-- Row 2: NusaMonitor -->
    <g transform="translate(778, 156)">
      <rect width="32" height="32" rx="8" fill="${t.cyanBg}"/>
      <g transform="translate(4, 4)">${icons.nusmonitor}</g>
      <text x="44" y="14" fill="${t.ink}" font-family="${FONT_SANS}" font-size="15" font-weight="700">NusaMonitor</text>
      <text x="44" y="31" fill="${t.muted}" font-family="${FONT_SANS}" font-size="12.5">Live public data map</text>
    </g>

    <!-- Row 3: IoT Bench -->
    <g transform="translate(778, 202)">
      <rect width="32" height="32" rx="8" fill="${t.amberBg}"/>
      <g transform="translate(4, 4)">${icons.iot}</g>
      <text x="44" y="14" fill="${t.ink}" font-family="${FONT_SANS}" font-size="15" font-weight="700">IoT &amp; MQTT Bench</text>
      <text x="44" y="31" fill="${t.muted}" font-family="${FONT_SANS}" font-size="12.5">Raspberry Pi telemetry</text>
    </g>

    <!-- Signal trace footer inside right panel -->
    <line x1="778" y1="256" x2="1096" y2="256" stroke="${t.borderSoft}" stroke-width="1"/>
    <path d="${panelWave}" fill="none" stroke="${t.cyan}" stroke-width="1.8" stroke-opacity="0.75"/>
    <circle cx="859" cy="256" r="2.8" fill="${t.amber}"/>
    <circle cx="1017" cy="256" r="2.8" fill="${t.cyan}"/>
    <text x="778" y="282" fill="${t.dim}" font-family="${FONT_MONO}" font-size="11">CH-01 // SIGNAL TRACE</text>
    <text x="1104" y="282" text-anchor="end" fill="${t.amber}" font-family="${FONT_MONO}" font-size="11">RF · WEB · AI</text>
  </g>
</svg>`;
}

function renderHeroCompact(mode) {
  const t = THEMES[mode];
  const icons = focusIcons(t.cyan, t.amber);
  const wave = wavePath(32, 468, 656, 12, 5, 90);

  return `<svg xmlns="http://www.w3.org/2000/svg" width="720" height="500" viewBox="0 0 720 500" role="img" aria-labelledby="title desc">
  <title id="title">Muhammad Rafi Priyo Sembodo — Nightshift Signal Desk</title>
  <desc id="desc">Mobile terminal-styled profile banner for Muhammad Rafi Priyo Sembodo.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${t.bg0}"/>
      <stop offset="100%" stop-color="${t.bg1}"/>
    </linearGradient>
    <clipPath id="frameClip"><rect x="1" y="1" width="718" height="498" rx="16"/></clipPath>
  </defs>

  <rect x="1" y="1" width="718" height="498" rx="16" fill="url(#bg)" stroke="${t.border}" stroke-width="2"/>
  <g clip-path="url(#frameClip)">
    <rect x="0" y="0" width="720" height="38" fill="${t.bar}"/>
    <line x1="0" y1="38" x2="720" y2="38" stroke="${t.border}" stroke-width="1"/>
    <circle cx="24" cy="19" r="5" fill="${t.dot}"/>
    <circle cx="42" cy="19" r="5" fill="${t.dot}"/>
    <circle cx="60" cy="19" r="5" fill="${t.dot}"/>
    <text x="82" y="24" fill="${t.muted}" font-family="${FONT_MONO}" font-size="13" font-weight="500">muhrafi-fsdev — signal-desk</text>

    <text x="32" y="72" fill="${t.cyan}" font-family="${FONT_MONO}" font-size="14" font-weight="600">&gt; whoami --desk</text>
    <line x1="32" y1="90" x2="32" y2="190" stroke="${t.cyan}" stroke-width="3.5" stroke-linecap="round"/>

    <text x="50" y="134" fill="${t.ink}" font-family="${FONT_SANS}" font-size="48" font-weight="700" letter-spacing="-1.2">Muhammad Rafi</text>
    <text x="50" y="186" fill="${t.ink}" font-family="${FONT_SANS}" font-size="48" font-weight="700" letter-spacing="-1.2">Priyo Sembodo</text>

    <text x="32" y="222" fill="${t.muted}" font-family="${FONT_SANS}" font-size="17" font-weight="500">Telecommunication Engineering · Telkom University</text>

    <g font-family="${FONT_MONO}" font-size="13" font-weight="600">
      <rect x="32" y="240" width="106" height="30" rx="7" fill="${t.pill}" stroke="${t.border}"/>
      <text x="85" y="260" text-anchor="middle" fill="${t.cyan}">Web Apps</text>

      <rect x="148" y="240" width="102" height="30" rx="7" fill="${t.pill}" stroke="${t.border}"/>
      <text x="199" y="260" text-anchor="middle" fill="${t.ink}">Local AI</text>

      <rect x="260" y="240" width="176" height="30" rx="7" fill="${t.amberBg}" stroke="${t.amber}" stroke-opacity="0.55"/>
      <text x="348" y="260" text-anchor="middle" fill="${t.amber}">Raspberry Pi · MQTT</text>
    </g>

    <!-- Stacked Verified Focus Card -->
    <rect x="32" y="290" width="656" height="156" rx="12" fill="${t.panel}" stroke="${t.border}" stroke-width="1.5"/>
    <text x="52" y="316" fill="${t.cyan}" font-family="${FONT_MONO}" font-size="13" font-weight="700" letter-spacing="1">VERIFIED FOCUS</text>
    <line x1="52" y1="326" x2="668" y2="326" stroke="${t.borderSoft}" stroke-width="1"/>

    <g transform="translate(52, 340)">
      <rect width="30" height="30" rx="7" fill="${t.cyanBg}"/>
      <g transform="translate(3, 3)">${icons.nusamind}</g>
      <text x="42" y="13" fill="${t.ink}" font-family="${FONT_SANS}" font-size="15.5" font-weight="700">NusaMind</text>
      <text x="42" y="30" fill="${t.muted}" font-family="${FONT_SANS}" font-size="13">Local-first AI workspace</text>
    </g>

    <g transform="translate(366, 340)">
      <rect width="30" height="30" rx="7" fill="${t.cyanBg}"/>
      <g transform="translate(3, 3)">${icons.nusmonitor}</g>
      <text x="42" y="13" fill="${t.ink}" font-family="${FONT_SANS}" font-size="15.5" font-weight="700">NusaMonitor</text>
      <text x="42" y="30" fill="${t.muted}" font-family="${FONT_SANS}" font-size="13">Live public data map</text>
    </g>

    <g transform="translate(52, 392)">
      <rect width="30" height="30" rx="7" fill="${t.amberBg}"/>
      <g transform="translate(3, 3)">${icons.iot}</g>
      <text x="42" y="13" fill="${t.ink}" font-family="${FONT_SANS}" font-size="15.5" font-weight="700">IoT &amp; MQTT Bench</text>
      <text x="42" y="30" fill="${t.muted}" font-family="${FONT_SANS}" font-size="13">Raspberry Pi telemetry experiments</text>
    </g>

    <path d="${wave}" fill="none" stroke="${t.cyan}" stroke-width="1.8" stroke-opacity="0.7"/>
    <circle cx="250" cy="468" r="3" fill="${t.amber}"/>
    <circle cx="470" cy="468" r="3" fill="${t.cyan}"/>
  </g>
</svg>`;
}

const SOCIAL_BUTTONS = [
  {
    id: 'portfolio',
    label: 'Portfolio',
    width: 146,
    accent: 'cyan',
    icon: `<rect x="2" y="3" width="16" height="14" rx="2.5"/><path d="M2 7.5h16M6.5 11.5h4"/>`,
  },
  {
    id: 'linkedin',
    label: 'LinkedIn',
    width: 144,
    accent: 'cyan',
    icon: `<rect x="2" y="2" width="16" height="16" rx="3"/><path d="M6.5 8.5v5.5M6.5 5.8v.2M10 14v-3.5a2 2 0 0 1 4 0V14"/>`,
  },
  {
    id: 'instagram',
    label: 'Instagram',
    width: 156,
    accent: 'amber',
    icon: `<rect x="2.5" y="2.5" width="15" height="15" rx="4"/><circle cx="10" cy="10" r="3.4"/><circle cx="14.3" cy="5.7" r="0.8" fill="currentColor" stroke="none"/>`,
  },
  {
    id: 'email',
    label: 'Email',
    width: 128,
    accent: 'amber',
    icon: `<rect x="2" y="4" width="16" height="12" rx="2.2"/><path d="M2.5 5.2 10 11l7.5-5.8"/>`,
  },
];

function renderButton(btn, mode) {
  const t = THEMES[mode];
  const color = btn.accent === 'amber' ? t.amber : t.cyan;
  const w = btn.width;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="42" viewBox="0 0 ${w} 42" role="img" aria-label="${btn.label}">
  <rect x="1" y="1" width="${w - 2}" height="40" rx="10" fill="${t.pill}" stroke="${t.border}" stroke-width="1.5"/>
  <g transform="translate(13, 11)" color="${color}" stroke="${color}" stroke-width="1.75" fill="none" stroke-linecap="round" stroke-linejoin="round">${btn.icon}</g>
  <text x="41" y="26" fill="${t.ink}" font-family="${FONT_SANS}" font-size="14.5" font-weight="600">${btn.label}</text>
  <path d="M${w - 19} 17l4.5 4-4.5 4" fill="none" stroke="${t.dim}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`;
}

// Pure-Node PNG encoder for small frame-based animated WebP signal pulse
const CRC_TABLE = new Uint32Array(256);
for (let n = 0; n < 256; n++) {
  let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  CRC_TABLE[n] = c >>> 0;
}
function crc32(buf) {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
function pngChunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const t = Buffer.from(type, 'ascii');
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([t, data])), 0);
  return Buffer.concat([len, t, data, crc]);
}
function encodePng(width, height, rgba) {
  const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8; // bit depth
  ihdr[9] = 6; // RGBA
  const raw = Buffer.alloc(height * (1 + width * 4));
  for (let y = 0; y < height; y++) {
    const rowOff = y * (1 + width * 4);
    raw[rowOff] = 0;
    rgba.copy(raw, rowOff + 1, y * width * 4, (y + 1) * width * 4);
  }
  const idat = zlib.deflateSync(raw);
  return Buffer.concat([sig, pngChunk('IHDR', ihdr), pngChunk('IDAT', idat), pngChunk('IEND', Buffer.alloc(0))]);
}

function hexToRgb(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

function drawPulseFrame(width, height, mode, phase) {
  const t = THEMES[mode];
  const border = hexToRgb(t.border);
  const cyan = hexToRgb(t.cyan);
  const amber = hexToRgb(t.amber);
  const buf = Buffer.alloc(width * height * 4);

  const blend = (x, y, rgb, alpha) => {
    if (x < 0 || x >= width || y < 0 || y >= height || alpha <= 0) return;
    const i = (y * width + x) * 4;
    const a = Math.min(1, alpha);
    const oldA = buf[i + 3] / 255;
    const outA = a + oldA * (1 - a);
    if (outA <= 0) return;
    buf[i] = Math.round((rgb[0] * a + buf[i] * oldA * (1 - a)) / outA);
    buf[i + 1] = Math.round((rgb[1] * a + buf[i + 1] * oldA * (1 - a)) / outA);
    buf[i + 2] = Math.round((rgb[2] * a + buf[i + 2] * oldA * (1 - a)) / outA);
    buf[i + 3] = Math.round(outA * 255);
  };

  const cy = Math.floor(height / 2);
  for (let x = 24; x < width - 24; x++) {
    blend(x, cy, border, 0.55);
  }

  const pulseX = 24 + phase * (width - 48);
  for (let x = 24; x < width - 24; x++) {
    const dist = Math.abs(x - pulseX);
    if (dist < 46) {
      const env = Math.exp(-(dist * dist) / (2 * 14 * 14));
      const yOff = Math.round(Math.sin((x - pulseX) * 0.28) * 6 * env);
      const col = dist < 10 ? amber : cyan;
      blend(x, cy + yOff, col, 0.92 * env + 0.15);
      blend(x, cy + yOff - 1, col, 0.4 * env);
      blend(x, cy + yOff + 1, col, 0.4 * env);
    }
  }
  return encodePng(width, height, buf);
}

async function renderSignalPulse(mode) {
  const width = 760;
  const height = 22;
  const frames = 24;
  const tmpDir = path.join(OUT, `_tmp_${mode}`);
  await fs.mkdir(tmpDir, { recursive: true });
  for (let f = 0; f < frames; f++) {
    const png = drawPulseFrame(width, height, mode, f / frames);
    await fs.writeFile(path.join(tmpDir, `frame_${String(f).padStart(2, '0')}.png`), png);
  }
  await fs.copyFile(
    path.join(tmpDir, 'frame_12.png'),
    path.join(tmpDir, 'still.png'),
  );
  execFileSync('ffmpeg', [
    '-y', '-framerate', '15', '-i', path.join(tmpDir, 'frame_%02d.png'),
    '-c:v', 'libwebp_anim', '-lossless', '0', '-q:v', '82', '-loop', '0',
    path.join(OUT, `signal-pulse-${mode}.webp`),
  ], { stdio: 'ignore' });
  execFileSync('ffmpeg', [
    '-y', '-i', path.join(tmpDir, 'still.png'),
    '-c:v', 'libwebp', '-lossless', '0', '-q:v', '88',
    path.join(OUT, `signal-pulse-${mode}-still.webp`),
  ], { stdio: 'ignore' });
  await fs.rm(tmpDir, { recursive: true, force: true });
}

async function main() {
  await fs.mkdir(OUT, { recursive: true });
  for (const mode of ['dark', 'light']) {
    await fs.writeFile(path.join(OUT, `hero-${mode}.svg`), renderHeroDesktop(mode), 'utf8');
    await fs.writeFile(path.join(OUT, `hero-${mode}-compact.svg`), renderHeroCompact(mode), 'utf8');
    for (const btn of SOCIAL_BUTTONS) {
      await fs.writeFile(path.join(OUT, `btn-${btn.id}-${mode}.svg`), renderButton(btn, mode), 'utf8');
    }
    await renderSignalPulse(mode);
  }
  console.log('Generated Nightshift Signal Desk assets in', OUT);
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
