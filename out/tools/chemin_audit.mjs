#!/usr/bin/env node
/**
 * chemin_audit.mjs — contrôle image par image d'une scène Lyrics chemin (out/shared/chemin-moteur/chemin.js), sans rendu.
 *
 *   node out/tools/chemin_audit.mjs <scene.html> [--query data=…] [--json rapport.json]
 *
 * Règles (concept lyrics-chemin, § Règles de lisibilité) :
 *   1. le mot chanté est entièrement dans x 64–960, y 220–1600 de son attaque à 60 % de sa durée
 *      (après 60 %, la caméra peut partir vers le mot suivant, règle 4) ; zoom arrière exclu (règle 7) ;
 *   2. corps à l'écran du mot chanté : ≥ 120 px (104 si la ligne le permet, 92 si tout le cadrage dépasse 4,5 mots/s),
 *      ≤ 220 px (titre 250), tolérance 4 % (poussée lente) ;
 *   3. un cadrage dure ≥ 0,5 s ;
 *   4. la caméra ne quitte pas une unité avant 60 % de sa durée et arrive au plus tard sur l'attaque de la suivante ;
 *   5. au repos, déplacement du point de lecture < 60 px/s à l'écran.
 * Imprime aussi, pour chaque transition, la rotation et la vitesse de pointe (jugement du confort), et vérifie qu'aucun
 * mot n'en recouvre un autre dans l'image finale. Code de sortie 1 si une règle échoue.
 * Navigateur : playwright, ou playwright-core + SVI_CHROME.
 */
import { createRequire } from 'node:module';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const require = createRequire(import.meta.url);
let pw; try { pw = require('playwright'); } catch { pw = require('playwright-core'); }
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const args = { _: [] };
for (let i = 2; i < process.argv.length; i++) { const a = process.argv[i]; if (a.startsWith('--')) { args[a.slice(2)] = process.argv[i + 1]; i++; } else args._.push(a); }
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.json': 'application/json', '.woff2': 'font/woff2' };
const srv = http.createServer((req, res) => { const p = path.join(ROOT, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(res); });
await new Promise(r => srv.listen(0, '127.0.0.1', r));
const opts = {}; if (process.env.SVI_CHROME) opts.executablePath = process.env.SVI_CHROME;
const browser = await pw.chromium.launch(opts); const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
page.on('pageerror', e => console.error('PAGE', e.message));
const rel = path.relative(ROOT, path.resolve(args._[0]));
await page.goto(`http://127.0.0.1:${srv.address().port}/${rel}${args.query ? '?' + args.query : ''}`);
await page.evaluate(() => window.ready);
const R = await page.evaluate(() => {
  const C = window.chemin, FPS = 30, n = Math.round(C.duree * FPS), [z0] = C.zoomArriere, frames = [];
  for (let f = 0; f <= n; f++) { const t = f / FPS; frames.push({ t, ...C.metrics(t) }); }
  return { frames, poses: C.poses.map(p => ({ line: p.line, txt: p.txt, arr: p.arr, dur: p.dur, leave: p.leave, kind: p.kind, tSing: p.tSing, tEnd: p.tEnd })), boxes: C.finalBoxes(), z0, beat: C.beat };
});
await browser.close(); srv.close();
const err = [], info = [];
const tag = (r, m) => err.push(`[${r}] ${m}`);
// 1 et 2
const seen = {};
for (const F of R.frames) {
  if (F.t >= R.z0) continue;
  const moving = F.disp > 2;
  for (const s of F.sung) {
    const k = s.line + ':' + s.txt, [x0, y0, x1, y1] = s.box;
    const st = seen[k] ||= { out: 0, small: 0, big: 0, minPx: 1e9, maxPx: 0, first: null };
    if (F.t < s.t + 0.6 * (s.end - s.t) && (x0 < 64 || x1 > 960 || y0 < 220 || y1 > 1600)) { st.out++; if (st.first === null) { st.first = F.t; st.box = s.box.map(v => Math.round(v)); st.moving = moving; } }
    if (!moving) { st.minPx = Math.min(st.minPx, s.px); st.maxPx = Math.max(st.maxPx, s.px);
      const lo = s.floor;
      if (s.px < lo * 0.96) st.small++; if (s.px > s.maxPx * 1.04) st.big++; }
  }
}
for (const [k, st] of Object.entries(seen)) {
  if (st.out) tag(1, `${k} hors zone sûre sur ${st.out} image(s) dès ${st.first.toFixed(2)} s (boîte ${st.box}${st.moving ? ', caméra en mouvement' : ''})`);
  if (st.small) tag(2, `${k} trop petit (${st.minPx.toFixed(0)} px) sur ${st.small} image(s)`);
  if (st.big) tag(2, `${k} trop grand (${st.maxPx.toFixed(0)} px) sur ${st.big} image(s)`);
  info.push(`${k.padEnd(28)} corps ${st.minPx.toFixed(0)}–${st.maxPx.toFixed(0)} px`);
}
// 3 et 4
R.poses.forEach((p, i) => {
  const hold = p.leave - p.arr;
  if (p.tSing !== null && hold < 0.5 - 1e-6) tag(3, `cadrage « ${p.txt} » tenu ${hold.toFixed(2)} s`);
  if (p.tSing !== null && p.arr > p.tSing + 1e-6) tag(4, `arrivée sur « ${p.txt} » à ${p.arr.toFixed(2)} s après l'attaque ${p.tSing.toFixed(2)} s`);
  const prev = R.poses[i - 1];
  if (prev && prev.tSing !== null && prev.tEnd) {
    // dernière unité du cadrage précédent : on n'a que sa fin ; la règle est vérifiée sur les unités chantées pendant le départ
  }
});
for (const F of R.frames) for (const s of F.sung) {
  const mid = s.t + 0.6 * (s.end - s.t);
  if (F.t < mid && F.t >= s.t) {
    const p = R.poses.find(q => q.arr - q.dur <= F.t && F.t < q.arr && q.dur > 0);
    if (p && !(p.tSing !== null && p.tSing <= s.end && p.txt.includes(s.txt))) tag(4, `départ vers « ${p.txt} » à ${F.t.toFixed(2)} s avant 60 % de « ${s.txt} »`);
  }
}
// 5 + mesures de confort par transition
const FPS = 30;
for (let i = 1; i < R.frames.length; i++) {
  const a = R.frames[i - 1], b = R.frames[i];
  const inT = F => R.poses.some(q => q.arr - q.dur - 1e-6 <= F.t && F.t <= q.arr + 1e-6 && q.dur > 0), inTrans = inT(a) || inT(b);
  b.v = Math.hypot((b.cam.x - a.cam.x) * b.cam.s, (b.cam.y - a.cam.y) * b.cam.s) * FPS;   // vitesse du point de lecture
  b.w = Math.abs(((b.cam.th - a.cam.th + 540) % 360) - 180) * FPS;
  if (!inTrans && b.t < R.z0 && b.v > 60) tag(5, `${b.t.toFixed(2)} s : ${b.v.toFixed(0)} px/s au repos`);
}
const trans = R.poses.filter(p => p.dur > 0).map(p => {
  const fr = R.frames.filter(F => F.t >= p.arr - p.dur && F.t <= p.arr);
  return `${p.kind.padEnd(8)} → ${p.txt.slice(0, 22).padEnd(22)} ${(p.arr - p.dur).toFixed(2)}–${p.arr.toFixed(2)} s (${(p.dur / R.beat).toFixed(1)} t)  rotation max ${Math.max(0, ...fr.map(F => F.w || 0)).toFixed(0)}°/s  vitesse max ${Math.max(0, ...fr.map(F => F.v || 0)).toFixed(0)} px/s  coin max ${Math.max(0, ...fr.map(F => F.disp)).toFixed(0)} px/demi-image`;
});
// chevauchements dans l'image finale (boîtes orientées, test des axes séparateurs)
function sat(A, B) { for (const P of [A, B]) for (let i = 0; i < 4; i++) { const [x0, y0] = P[i], [x1, y1] = P[(i + 1) % 4], nx = y0 - y1, ny = x1 - x0;
  const pa = A.map(([x, y]) => x * nx + y * ny), pb = B.map(([x, y]) => x * nx + y * ny);
  if (Math.max(...pa) <= Math.min(...pb) || Math.max(...pb) <= Math.min(...pa)) return false; } return true; }
for (let i = 0; i < R.boxes.length; i++) for (let j = i + 1; j < R.boxes.length; j++) if (sat(R.boxes[i].poly, R.boxes[j].poly)) tag('final', `« ${R.boxes[i].txt} » (${R.boxes[i].line}) recouvre « ${R.boxes[j].txt} » (${R.boxes[j].line})`);
const report = { ok: err.length === 0, errors: err, sizes: info, transitions: trans };
console.log(info.join('\n')); console.log('--- transitions'); console.log(trans.join('\n')); console.log('--- erreurs'); console.log(err.length ? err.join('\n') : 'aucune');
if (args.json) fs.writeFileSync(args.json, JSON.stringify(report, null, 1));
process.exit(err.length ? 1 : 0);
