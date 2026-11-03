#!/usr/bin/env node
/* make_sound.cjs — écrit sound.json (spec de out/tools/sound.py) à partir de trace.json :
 * chiptune 125 bpm + SFX calés sur les événements PHYSIQUES enregistrés par la simulation Matter
 * (blip par collision, hauteur = couleur de la bille, gain ∝ vitesse relative ; coin aux arrivées).
 * USAGE : node out/shorts/pixel-arcade__engagement__quelle-bille-gagne-la-course/src/make_sound.cjs
 */
const fs = require('fs'), path = require('path');
const tr = JSON.parse(fs.readFileSync(path.join(__dirname, 'trace.json'), 'utf8'));
const NOTE = ['E5', 'G5', 'A5', 'C6'];          // ROSE, VERTE, JAUNE, BLEUE (pentatonique de C)
const ev = [];
ev.push({ t: 0.05, type: 'coin', note: 'E6', gain: 0.7 });                      // « insert coin » du hook
[0.96, 1.44, 1.92].forEach(t => ev.push({ t, type: 'blip', note: 'A5', gain: 0.9, dur: 0.16 }));
ev.push({ t: 2.4, type: 'blip', note: 'A6', gain: 1.0, dur: 0.3 }); ev.push({ t: 2.4, type: 'whoosh', gain: 0.5, dur: 0.5 });
let lastT = -1, nBlip = 0;
for (const e of tr.events) {
  if (e.m < 0 || e.with === 'gate') continue;
  if (e.with === 'finish') {
    const rank = e.o;
    ev.push({ t: e.t, type: rank === 1 ? 'coin' : 'pop', note: rank === 1 ? 'C7' : NOTE[e.m], gain: rank === 1 ? 1.0 : 0.6 });
    if (rank === 1) ev.push({ t: e.t, type: 'impact', gain: 0.5 });
    continue;
  }
  if (e.v < 0.5 || e.t - lastT < 0.06) continue;                               // limite de densité : 1 blip / 60 ms
  lastT = e.t; nBlip++;
  const g = Math.min(0.75, 0.25 + e.v * 0.22);
  if (e.with === 'marble') ev.push({ t: e.t, type: 'click', gain: 0.5 });
  ev.push({ t: e.t, type: 'blip', note: e.with === 'spinner' ? 'E6' : NOTE[e.m], gain: +g.toFixed(2) });
}
ev.push({ t: 12.0, type: 'chime', note: 'G5', gain: 0.5 });                     // PHOTO FINISH
ev.push({ t: 13.95, type: 'whoosh', gain: 0.6, dur: 0.6 });                      // transition pixel-mosaic
ev.push({ t: 14.25, type: 'coin', note: 'G6', gain: 0.8 });                      // carte de fin
ev.push({ t: 14.55, type: 'chime', note: 'C6', gain: 0.5, dur: 1.4 });
const spec = { duration: 16.0, seed: 17, bpm: 125, key: 'C', scale: 'majpent', reverb: 0.12,
  music: { preset: 'chiptune', gain: 0.42, octave: 4, loop: false }, events: ev.sort((a, b) => a.t - b.t) };
fs.writeFileSync(path.join(__dirname, 'sound.json'), JSON.stringify(spec, null, 1));
console.log('events', ev.length, 'collision blips', nBlip);
