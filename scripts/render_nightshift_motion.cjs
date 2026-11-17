// Run from the repo with Node 18+, sharp and FFmpeg with libwebp_anim.
// node scripts/render_nightshift_motion.cjs
const sharp = require('sharp');
const {spawn} = require('node:child_process');
const {once} = require('node:events');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const WIDTH = 1080, HEIGHT = 400, FPS = 25, FRAMES = 90;
const asset = (...p) => path.join(root, 'assets', 'nightshift', ...p);
let seed = 9712;
function random() {
  seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
  return seed / 2 ** 32;
}

function light(frame,x,y,radius,strength,color) {
  const x0 = Math.max(0, Math.floor(x - radius));
  const x1 = Math.min(WIDTH - 1, Math.ceil(x + radius));
  const y0 = Math.max(0, Math.floor(y - radius));
  const y1 = Math.min(HEIGHT - 1, Math.ceil(y + radius));
  for(let py=y0; py<=y1; py++) {
    for(let px=x0; px<=x1; px++) {
      const falloff = 1 - Math.hypot(px - x, py - y) / radius;
      if(falloff <= 0) continue;
      const a = falloff * strength;
      const loc = 3 * (py * WIDTH + px);
      for(let i=0; i<3; i++) frame[loc+i] += Math.round(a * (color[i] - frame[loc+i]));
    }
  }
}

function rainfall(frame,phase,drops) {
  // All drops tile at a y position outside the frame. The portrait stays still.
  const cloud = [164,203,229];
  for(const d of drops) {
    const y = ((phase * d.laps + d.offset) % 1) * (HEIGHT + 74) - 37;
    const x = d.x - .24 * y;
    for(let j=0; j<d.length; j++) {
      const fade = Math.sin(Math.PI * (j + 1) / (d.length + 1));
      light(frame,x + .24*j,y-j,d.radius,d.opacity*fade,cloud);
    }
  }
  // A few warm/cool pinpoints brighten against the existing skyline.
  const windows = [[340,206],[454,239],[556,146],[581,195],[296,307],[205,291],[438,231]];
  for(const [i,[x,y]] of windows.entries()) {
    const pulse = Math.pow(.5 + .5*Math.cos(Math.PI*2*(phase + i*.173)),4);
    light(frame,x,y,4.2,.29*pulse,i===1?[250,196,118]:[136,197,230]);
  }
}

async function main() {
  const base = await sharp(asset('banner.webp')).resize(WIDTH,HEIGHT,{fit:'fill'}).removeAlpha().raw().toBuffer();
  const drops = Array.from({length:34},(_,i)=>({
    x: 20 + random()*(i<28?765:1115),
    offset:random(), length: 8 + Math.floor(random()*12),
    laps: i%3 === 0 ? 2 : 1, radius: .68 + random()*.26,
    opacity: .14 + random()*.22,
  }));
  const args=['-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',
    `${WIDTH}x${HEIGHT}`,'-framerate',String(FPS),'-i','pipe:0','-an','-c:v','libwebp_anim',
    '-lossless','1','-quality','84','-compression_level','5','-loop','0',asset('refined','banner-motion.webp')];
  const ffmpeg = spawn('ffmpeg',args,{stdio:['pipe','ignore','inherit']});
  const done = once(ffmpeg,'close');
  for(let i=0;i<FRAMES;i++) {
    const data = Buffer.from(base);
    rainfall(data,i/FRAMES,drops);
    if(!ffmpeg.stdin.write(data)) await once(ffmpeg.stdin,'drain');
  }
  ffmpeg.stdin.end();
  const [code] = await done;
  if(code !== 0) throw new Error(`WebP encoder exited with code ${code}`);
}
main().catch(e=>{console.error(e);process.exitCode=1;});
