#!/usr/bin/env node
/* simulate.cjs — pré-simulation Node de ring.js : choisit la graine (évasion entre 11,4 et 12,4 s, ≥ 24 rebonds)
 * USAGE : node out/shorts/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper/src/simulate.cjs --scan 1 2000
 *         node out/shorts/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper/src/simulate.cjs --seed N   -> trace.json
 */
const fs = require('fs'), path = require('path');
const Rg = require('./ring.js');
const DUR = 15;
const opts = {}; const argv = process.argv.slice(2);
['g', 'grow', 'gapTiles', 'stepFrames', 'speed', 'vmin'].forEach(k => { const i = argv.indexOf('--' + k); if (i >= 0) opts[k] = +argv[i + 1]; });
function run(seed) { const s = Rg.create(seed, opts); for (let f = 0; f < DUR * Rg.FPS; f++) Rg.stepFrame(s); return s; }
if (argv[0] === '--scan') {
  const a = +argv[1], b = +argv[2]; const ok = []; const esc = [];
  for (let seed = a; seed <= b; seed++) { const s = run(seed); if (s.escaped) esc.push(s.escT); if (s.escaped && s.escT >= 11.4 && s.escT <= 12.4 && s.bounces >= 24) ok.push({ seed, escT: s.escT, n: s.bounces, r: s.r }); }
  esc.sort((x, y) => x - y);
  console.log('escaped', esc.length, '/', b - a + 1, 'median escT', esc[Math.floor(esc.length / 2)], 'ok', ok.length);
  ok.sort((x, y) => y.n - x.n).slice(0, 8).forEach(r => console.log(JSON.stringify(r)));
} else {
  const seed = +argv[argv.indexOf('--seed') + 1]; const s = run(seed);
  fs.writeFileSync(path.join(__dirname, 'trace.json'), JSON.stringify({ seed, opts, escT: s.escT, bounces: s.bounces, rFinal: s.r, events: s.events }));
  console.log(JSON.stringify({ seed, escT: s.escT, bounces: s.bounces, r: s.r, events: s.events.length }));
}
