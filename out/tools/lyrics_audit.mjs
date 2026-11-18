#!/usr/bin/env node
/**
 * lyrics_audit.mjs — contrôle image par image d'une scène Lyrics punchy (out/shared/lyrics-moteur/lyrics.js).
 *
 *   node out/tools/lyrics_audit.mjs <scene.html> [--query data=…] [--step 1] [--json rapport.json]
 *
 * Pour chaque image échantillonnée, la scène rend t puis window.audit(t) donne les boîtes des capitales visibles
 * (transformations comprises) et le polygone du carton. Vérifie :
 *   - texte dans la colonne x 64–940 et y 220–1 560 (zones sûres du concept : haut 220, bas 360, droite 140, gauche 64) ;
 *   - tailles : ligne en cours ≥ 120 px, mur ≥ 56 px ;
 *   - au plus 6 unités vives et 4 lignes de mur ;
 *   - le carton ne recouvre aucune ligne du mur encore lisible (tons 1 et 2) ni la ligne en cours.
 * Les dépassements pendant l'entrée d'une unité (claque / coup : le mot arrive trop large et se resserre en 3 à 5 images)
 * sont comptés à part comme « transitoires ».
 * Navigateur : comme render.mjs (playwright, ou playwright-core + SVI_CHROME).
 */
import { createRequire } from 'node:module';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const require = createRequire(import.meta.url);
let pw; try { pw = require('playwright'); } catch { pw = require('playwright-core'); }
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const args = { _: [] };
for (let i = 2; i < process.argv.length; i++) {
  const a = process.argv[i];
  if (a.startsWith('--')) { args[a.slice(2)] = process.argv[i + 1]; i++; } else args._.push(a);
}
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.json': 'application/json', '.css': 'text/css', '.woff2': 'font/woff2' };
const srv = http.createServer((req, res) => {
  const u = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  const p = path.join(ROOT, u);
  if (!p.startsWith(ROOT) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise((r) => srv.listen(0, '127.0.0.1', r));
const opts = { args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] };
if (process.env.SVI_CHROME) opts.executablePath = process.env.SVI_CHROME;
const browser = await pw.chromium.launch(opts);
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') console.error('[page]', m.text()); });
const rel = path.relative(ROOT, path.resolve(args._[0])).split(path.sep).join('/');
await page.goto(`http://127.0.0.1:${srv.address().port}/${rel}${args.query ? '?' + args.query : ''}`);
await page.waitForFunction(() => typeof window.renderAt === 'function');
await page.evaluate(async () => { await window.ready; });
const info = await page.evaluate(() => window.lyricsInfo);
const dur = await page.evaluate(() => window.DURATION);
const step = +(args.step || 1);
const frames = [];
for (let f = 0; f < Math.round(dur * 30); f += step) frames.push(await page.evaluate((t) => window.audit(t), f / 30));
await browser.close(); srv.close();

// séparation d'axes : polygone convexe contre rectangle
function hit(poly, r) {
  const rp = [[r.x0, r.y0], [r.x1, r.y0], [r.x1, r.y1], [r.x0, r.y1]];
  for (const P of [poly, rp]) for (let i = 0; i < 4; i++) {
    const [ax, ay] = P[i], [bx, by] = P[(i + 1) % 4], nx = by - ay, ny = ax - bx;
    const pa = poly.map(([x, y]) => x * nx + y * ny), pb = rp.map(([x, y]) => x * nx + y * ny);
    if (Math.max(...pa) <= Math.min(...pb) || Math.max(...pb) <= Math.min(...pa)) return false;
  }
  return true;
}
const TOL = 1;
const rep = { frames: frames.length, step, hors: [], horsTransitoire: 0, tailles: [], densite: [], carton: [], maxVifs: 0, maxMur: 0, tailleMin: { vif: 999, mur: 999 } };
for (const fr of frames) {
  const vifs = fr.items.filter((i) => i.k === 'vif'), mur = fr.items.filter((i) => i.k.startsWith('mur'));
  rep.maxVifs = Math.max(rep.maxVifs, vifs.length); rep.maxMur = Math.max(rep.maxMur, mur.length);
  if (vifs.length > 6) rep.densite.push(`${fr.t.toFixed(2)} s : ${vifs.length} unités vives`);
  if (mur.length > 5) rep.densite.push(`${fr.t.toFixed(2)} s : ${mur.length} lignes de mur`);
  for (const i of fr.items) {
    const min = i.k === 'vif' ? 120 : 56;
    rep.tailleMin[i.k === 'vif' ? 'vif' : 'mur'] = Math.min(rep.tailleMin[i.k === 'vif' ? 'vif' : 'mur'], i.size);
    if (i.size < min - 0.5) rep.tailles.push(`${fr.t.toFixed(2)} s « ${i.txt} » ${i.size} px`);
    if (i.k === 'chute') continue;                     // chute-de-pile : le texte tombe volontairement sous le cadre
    const out = i.x0 < 64 - TOL || i.x1 > 940 + TOL || i.y0 < 220 - TOL || i.y1 > 1560 + TOL;
    if (!out) continue;
    if (i.tr) { rep.horsTransitoire++; continue; }     // entrée claque / coup (3 à 5 images) ou empilement (6 images)
    const msg = `${fr.t.toFixed(2)} s ${i.k} « ${i.txt} » x ${i.x0.toFixed(0)}–${i.x1.toFixed(0)} y ${i.y0.toFixed(0)}–${i.y1.toFixed(0)}`;
    rep.hors.push(msg);
  }
  if (fr.carton) {
    for (const i of fr.items) {
      if (i.k === 'mur' || i.k === 'chute') continue;    // ton 3 : décoratif, déjà lu
      if (hit(fr.carton.pts, i)) rep.carton.push(`${fr.t.toFixed(2)} s carton ${fr.carton.id} sur ${i.k} « ${i.txt} »`);
    }
  }
}
// regroupe les dépassements en épisodes consécutifs (un épisode court = entrée d'un mot ou chute-de-pile)
const ep = [];
for (const m of rep.hors) {
  const t = parseFloat(m), txt = m.split('«')[1];
  const last = ep[ep.length - 1];
  if (last && last.txt === txt && t - last.t1 <= step / 30 + 1e-6) { last.t1 = t; last.n++; } else ep.push({ t0: t, t1: t, n: 1, txt, ex: m });
}
const res = { info: { cartons: info.cartons, warnings: info.warnings, CAP: info.CAP }, frames: rep.frames, maxVifs: rep.maxVifs, maxMur: rep.maxMur,
  tailleMin: rep.tailleMin, taillesSousMin: rep.tailles.length, densite: rep.densite.slice(0, 10), cartonSurTexteLisible: rep.carton.slice(0, 20),
  depassementsTransitoires: rep.horsTransitoire, depassements: { images: rep.hors.length, episodes: ep.map((e) => ({ de: e.t0, a: e.t1, images: e.n, exemple: e.ex })) } };
if (args.json) fs.writeFileSync(args.json, JSON.stringify(res, null, 1));
console.log(JSON.stringify(res, null, 1));
