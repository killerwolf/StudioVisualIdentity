#!/usr/bin/env node
/* simulate.cjs — pré-simulation Node pure de conquest.js : choisit la graine.
 * Critères : écran plein entre 4,5 et 7 s, ≥ 3 changements de leader après le plein, écart 1er–2e au gel (12 s) < 1,2 %,
 * personne sous 8 %. --scan a b | --seed N (écrit trace.json : % finaux, rang, événements).
 */
const fs = require('fs'), path = require('path');
const Q = require('./conquest.js');
function run(seed) { const s = Q.create(seed); for (let f = 0; f < Q.END_F + 5; f++) Q.stepFrame(s); return s; }
function score(s) {
  const pct = s.counts.slice(1).map(c => 100 * c / Q.N), sorted = [...pct].sort((a, b) => b - a);
  const gap = sorted[0] - sorted[1], leads = s.events.filter(e => e.type === 'lead' && s.fullF && e.t * 30 > s.fullF).length;
  const fullT = s.fullF / 30;
  const ok = s.fullF && fullT >= 4.5 && fullT <= 7 && leads >= 3 && gap < 1.2 && gap > 0.05 && sorted[3] > 8;
  return { seed: s.seed, ok, fullT: +fullT.toFixed(2), leads, gap: +gap.toFixed(2), pct: pct.map(p => +p.toFixed(2)), sc: (ok ? 100 : 0) + Math.min(leads, 10) * 2 - gap * 10 };
}
const argv = process.argv.slice(2);
if (argv[0] === '--scan') {
  const a = +argv[1], b = +argv[2], t0 = Date.now(), res = [];
  for (let seed = a; seed <= b; seed++) res.push(score(run(seed)));
  console.log('scanned', res.length, 'in', ((Date.now() - t0) / 1000).toFixed(1), 's ; ok', res.filter(r => r.ok).length, '; fullT median', res.map(r => r.fullT).sort((x, y) => x - y)[res.length >> 1], '; leads median', res.map(r => r.leads).sort((x, y) => x - y)[res.length >> 1]);
  res.sort((x, y) => y.sc - x.sc).slice(0, 8).forEach(r => console.log(JSON.stringify(r)));
} else {
  const seed = +argv[argv.indexOf('--seed') + 1], s = run(seed), sc = score(s);
  const rank = [1, 2, 3, 4].sort((x, y) => s.counts[y] - s.counts[x]);
  fs.writeFileSync(path.join(__dirname, 'trace.json'), JSON.stringify({ seed, startT: Q.START_F / 30, endT: Q.END_F / 30, counts: s.counts, pct: sc.pct, rank, fullT: sc.fullT, events: s.events, history: s.history }));
  console.log(JSON.stringify(sc), 'rank', rank);
}
