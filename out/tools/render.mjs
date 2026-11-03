#!/usr/bin/env node
/**
 * render.mjs — Rendu déterministe d'une scène HTML en vidéo 1080×1920 (ou en stills).
 *
 * CONTRAT DE SCÈNE (dans la page HTML) :
 *   window.ready      : Promise résolue quand la scène est prête (polices, assets, warm-up)
 *   window.renderAt(t): dessine l'image au temps t (secondes). Ne RIEN retourner (pas de thenable !)
 *   window.SEQUENTIAL : true si la scène a un état (physique, trails) -> rendu frame à frame depuis t=0
 *   window.DURATION   : (optionnel) durée par défaut en secondes
 *
 * La page est servie par un serveur statique local dont la racine est la RACINE DU DÉPÔT,
 * donc une scène importe ses librairies via  /node_modules/<lib>/...  et les helpers via /out/tools/lib/...
 *
 * USAGE
 *   node out/tools/render.mjs <scene.html> --out short_video.mp4 [--duration 15] [--fps 30]
 *   node out/tools/render.mjs <scene.html> --stills 0.5,3,8,12 --stills-dir stills/   # JPEG 1080×1920
 *   options : --width 1080 --height 1920 --crf 14 --start 0 --quality 92 --no-slot --gl swiftshader|egl
 *
 * SORTIE : écrit d'abord <out>.part.mp4, puis renomme. Imprime un JSON {frames, seconds, secPer100Frames}.
 * SLOTS CPU : chaque rendu réserve un slot parmi nproc (verrous dans /tmp/svi-slots) — plusieurs agents
 *   peuvent lancer des rendus sans jamais dépasser le nombre de cœurs. --no-slot pour désactiver.
 */
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright'); // résolu via NODE_PATH (Playwright préinstallé) ou node_modules
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..', '..');

function parseArgs(argv) {
  const a = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k.startsWith('--')) {
      const key = k.slice(2);
      const nxt = argv[i + 1];
      if (nxt === undefined || nxt.startsWith('--')) a[key] = true;
      else { a[key] = nxt; i++; }
    } else a._.push(k);
  }
  return a;
}

const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml', '.woff': 'font/woff', '.woff2': 'font/woff2', '.ttf': 'font/ttf',
  '.wasm': 'application/wasm', '.glsl': 'text/plain', '.map': 'application/json', '.txt': 'text/plain',
  '.geojson': 'application/json', '.wav': 'audio/wav', '.mp3': 'audio/mpeg',
};

function startServer() {
  return new Promise((resolve) => {
    const srv = http.createServer((req, res) => {
      try {
        const u = decodeURIComponent(new URL(req.url, 'http://x').pathname);
        let p = path.join(ROOT, u);
        if (!p.startsWith(ROOT)) { res.writeHead(403); return res.end(); }
        if (fs.existsSync(p) && fs.statSync(p).isDirectory()) p = path.join(p, 'index.html');
        if (!fs.existsSync(p)) { res.writeHead(404); return res.end('404 ' + u); }
        res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
        fs.createReadStream(p).pipe(res);
      } catch (e) { res.writeHead(500); res.end(String(e)); }
    });
    srv.listen(0, '127.0.0.1', () => resolve(srv));
  });
}

// ---- CPU slot semaphore (mkdir is atomic) ----
const SLOT_DIR = '/tmp/svi-slots';
function pidAlive(pid) { try { process.kill(pid, 0); return true; } catch { return false; } }
async function acquireSlot(n) {
  fs.mkdirSync(SLOT_DIR, { recursive: true });
  let warned = false;
  for (;;) {
    for (let i = 0; i < n; i++) {
      const d = path.join(SLOT_DIR, `slot${i}`);
      try {
        fs.mkdirSync(d);
        fs.writeFileSync(path.join(d, 'pid'), String(process.pid));
        return d;
      } catch {
        // stale lock?
        try {
          const pid = parseInt(fs.readFileSync(path.join(d, 'pid'), 'utf8'));
          if (pid && !pidAlive(pid)) fs.rmSync(d, { recursive: true, force: true });
        } catch { /* pid file not yet written */ }
      }
    }
    if (!warned) { console.error(`[render] waiting for a free CPU slot (${n} slots)…`); warned = true; }
    await new Promise(r => setTimeout(r, 1500));
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const scene = args._[0];
  if (!scene) { console.error('usage: render.mjs <scene.html> --out x.mp4 | --stills t1,t2'); process.exit(2); }
  const sceneAbs = path.resolve(scene);
  const rel = path.relative(ROOT, sceneAbs).split(path.sep).join('/');
  if (rel.startsWith('..')) { console.error('scene must live inside the repo: ' + ROOT); process.exit(2); }

  const W = +(args.width || 1080), H = +(args.height || 1920), FPS = +(args.fps || 30);
  const quality = +(args.quality || 92);
  const nSlots = +(process.env.SVI_SLOTS || os.cpus().length);
  let slot = null;
  if (!args['no-slot']) slot = await acquireSlot(nSlots);
  const release = () => { if (slot) { try { fs.rmSync(slot, { recursive: true, force: true }); } catch {} slot = null; } };
  process.on('exit', release);
  process.on('SIGINT', () => { release(); process.exit(130); });
  process.on('SIGTERM', () => { release(); process.exit(143); });

  const srv = await startServer();
  const port = srv.address().port;
  const gl = args.gl || 'swiftshader';
  const flags = gl === 'swiftshader'
    ? ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-accelerated-2d-canvas']
    : ['--ignore-gpu-blocklist', '--disable-accelerated-2d-canvas'];
  const browser = await chromium.launch({ args: [...flags, '--autoplay-policy=no-user-gesture-required', '--disable-web-security'] });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  const logs = [];
  page.on('console', m => { const s = `[page:${m.type()}] ${m.text()}`; logs.push(s); if (m.type() === 'error' || args.verbose) console.error(s); });
  page.on('pageerror', e => console.error('[pageerror]', e.message));
  page.setDefaultTimeout(+(args.timeout || 180000));

  const url = `http://127.0.0.1:${port}/${rel}${args.query ? '?' + args.query : ''}`;
  await page.goto(url, { waitUntil: 'load' });
  await page.waitForFunction(() => typeof window.renderAt === 'function', null, { timeout: 60000 });
  await page.evaluate(async () => { if (window.ready) await window.ready; if (document.fonts) await document.fonts.ready; });
  const meta = await page.evaluate(() => ({ seq: !!window.SEQUENTIAL, dur: window.DURATION || null }));

  const duration = +(args.duration || meta.dur || 15);
  const start = +(args.start || 0);
  const t0 = Date.now();
  const renderFrame = async (t) => { await page.evaluate((tt) => { window.renderAt(tt); }, t); };
  const shoot = async (file) => page.screenshot({ type: 'jpeg', quality, path: file, clip: { x: 0, y: 0, width: W, height: H } });

  if (args.stills) {
    const times = String(args.stills).split(',').map(Number).sort((a, b) => a - b);
    const dir = path.resolve(args['stills-dir'] || path.join(path.dirname(sceneAbs), '..', 'stills'));
    fs.mkdirSync(dir, { recursive: true });
    const prefix = args.prefix || 'still';
    if (meta.seq) {
      // step frame by frame from 0 up to the last requested time
      const last = Math.round(times[times.length - 1] * FPS);
      const want = new Set(times.map(t => Math.round(t * FPS)));
      for (let f = 0; f <= last; f++) {
        await renderFrame(f / FPS);
        if (want.has(f)) {
          const file = path.join(dir, `${prefix}_${(f / FPS).toFixed(2)}s.jpg`);
          await shoot(file); console.log(file);
        }
      }
    } else {
      for (const t of times) {
        await renderFrame(t);
        const file = path.join(dir, `${prefix}_${t.toFixed(2)}s.jpg`);
        await shoot(file); console.log(file);
      }
    }
    const secs = (Date.now() - t0) / 1000;
    console.log(JSON.stringify({ mode: 'stills', count: times.length, seconds: +secs.toFixed(1) }));
  } else {
    const out = path.resolve(args.out || 'out.mp4');
    const part = out.replace(/\.mp4$/, '') + '.part.mp4';
    fs.mkdirSync(path.dirname(out), { recursive: true });
    const nFrames = Math.round(duration * FPS);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', String(args.crf || 14), '-pix_fmt', 'yuv420p', '-r', String(FPS),
      '-movflags', '+faststart', part], { stdio: ['pipe', 'inherit', 'inherit'] });
    const ffDone = new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))));
    // sequential scenes must be stepped from t=0 even if --start>0
    const firstFrame = Math.round(start * FPS);
    if (meta.seq && firstFrame > 0) for (let f = 0; f < firstFrame; f++) await renderFrame(f / FPS);
    for (let f = firstFrame; f < firstFrame + nFrames; f++) {
      await renderFrame(f / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality, clip: { x: 0, y: 0, width: W, height: H } });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if ((f - firstFrame) % 60 === 0) process.stderr.write(`\r[render] ${f - firstFrame}/${nFrames}`);
    }
    ff.stdin.end();
    await ffDone;
    fs.renameSync(part, out);
    const secs = (Date.now() - t0) / 1000;
    process.stderr.write('\n');
    console.log(JSON.stringify({ mode: 'video', out, frames: nFrames, seconds: +secs.toFixed(1), secPer100Frames: +(secs / nFrames * 100).toFixed(1), sequential: meta.seq }));
  }
  await browser.close();
  srv.close();
  release();
}

main().catch(e => { console.error(e); process.exit(1); });
