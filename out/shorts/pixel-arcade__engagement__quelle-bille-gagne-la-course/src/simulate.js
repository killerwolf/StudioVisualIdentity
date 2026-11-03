#!/usr/bin/env node
/* simulate.js — pré-simulation Matter.js en Node pur (aucun navigateur) pour choisir la graine.
 * USAGE : node out/shorts/pixel-arcade__engagement__quelle-bille-gagne-la-course/src/simulate.js [--scan 1 400] [--seed N]
 *   --scan a b : teste les graines a..b, imprime les meilleures (vainqueur 11–14 s, tous arrivés, arrivée serrée)
 *   --seed N   : simule N et écrit trace.json (temps d'arrivée, rangs, collisions, nudges) à côté de ce fichier
 */
const path = require('path');
const fs = require('fs');
const Matter = require(path.resolve(__dirname, '../../../../node_modules/matter-js'));
const C = require('./course.js');
const DUR = 16.0;

function run(seed, opts) {
  const s = C.create(Matter, seed, opts);
  const leaders = [];
  for (let f = 0; f < DUR * C.FPS; f++) {
    C.stepFrame(Matter, s);
    if (s.rank.length === 4) break;
    // leader = la plus basse parmi les non-arrivées (ou première arrivée)
    if (s.rank.length === 0) {
      let li = 0; s.marbles.forEach((m, i) => { if (m.position.y > s.marbles[li].position.y) li = i; });
      if (!leaders.length || leaders[leaders.length - 1].m !== li) leaders.push({ t: +(s.frame / C.FPS).toFixed(2), m: li });
    }
  }
  return { s, leaders };
}

function score(r) {
  const s = r.s, ft = s.finishT;
  if (ft.some(x => x === null)) return null;
  const sorted = [...ft].sort((a, b) => a - b);
  const win = sorted[0], last = sorted[3], gap12 = sorted[1] - sorted[0];
  const ok = win >= 11.2 && win <= 13.2 && last <= 14.6 && s.nudges.length <= 2;
  const leadChanges = r.leaders.filter(l => l.t > C.START_T + 0.5).length;
  const comeback = r.leaders.length && r.leaders.filter(l => l.t > 6)[0] && r.leaders.filter(l => l.t > 6)[0].m !== s.rank[0] ? 1 : 0;
  return { seed: s.seed, ok, win, last, gap12: +gap12.toFixed(3), leadChanges, comeback, nudges: s.nudges.length, rank: s.rank,
    sc: (ok ? 100 : 0) - gap12 * 40 + Math.min(leadChanges, 8) * 2 + comeback * 6 - s.nudges.length * 8 };
}

const argv = process.argv.slice(2);
const opts = {};
const gi = argv.indexOf('--g'); if (gi >= 0) opts.gScale = +argv[gi + 1];
const ai = argv.indexOf('--air'); if (ai >= 0) opts.air = +argv[ai + 1];
if (argv[0] === '--scan') {
  const a = +argv[1] || 1, b = +argv[2] || 200;
  const res = [];
  const t0 = Date.now();
  for (let seed = a; seed <= b; seed++) { const r = run(seed, opts); const sc = score(r); res.push(sc || { seed, ok: false, dnf: r.s.finishT, nudges: r.s.nudges.length }); }
  const fin = res.filter(r => r.win);
  console.log('scanned', res.length, 'in', ((Date.now() - t0) / 1000).toFixed(1), 's; all-finished', fin.length, '; ok', res.filter(r => r.ok).length);
  if (fin.length) {
    const ws = fin.map(r => r.win).sort((x, y) => x - y);
    console.log('winner time min/med/max', ws[0], ws[Math.floor(ws.length / 2)], ws[ws.length - 1], 'nudged runs', res.filter(r => r.nudges).length);
  }
  res.filter(r => r.ok).sort((x, y) => y.sc - x.sc).slice(0, 10).forEach(r => console.log(JSON.stringify(r)));
} else {
  const seed = +(argv[argv.indexOf('--seed') + 1] || 1);
  const r = run(seed, opts);
  const out = { seed, opts, startT: C.START_T, finishT: r.s.finishT, rank: r.s.rank, nudges: r.s.nudges, leaders: r.leaders,
    finalPos: r.s.marbles.map(m => [+m.position.x.toFixed(3), +m.position.y.toFixed(3)]), score: score(r), events: r.s.events };
  fs.writeFileSync(path.join(__dirname, 'trace.json'), JSON.stringify(out));
  console.log(JSON.stringify({ seed, finishT: out.finishT, rank: out.rank, nudges: out.nudges.length, events: out.events.length, score: out.score }));
}
