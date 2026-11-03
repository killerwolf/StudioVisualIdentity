#!/usr/bin/env node
/* make_sound.cjs — écrit sound.json (spec de out/tools/sound.py) depuis trace.json (rebonds enregistrés par ring.js) :
 * chiptune 125 bpm (même tempo que le short engagement de l'identité) ; 1 blip par rebond, hauteur qui MONTE
 * dans la pentatonique de C à chaque rebond (2 octaves puis on reboucle) ; riser avant l'évasion, glass + coin à l'évasion.
 * USAGE : node out/shorts/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper/src/make_sound.cjs
 */
const fs = require('fs'), path = require('path');
const tr = JSON.parse(fs.readFileSync(path.join(__dirname, 'trace.json'), 'utf8'));
const PENTA = ['C', 'D', 'E', 'G', 'A'];
const note = n => { const k = (n - 1) % 10; return PENTA[k % 5] + (5 + Math.floor(k / 5)); };
const ev = [{ t: 0.05, type: 'coin', note: 'E6', gain: 0.7 }];
for (const e of tr.events) {
  if (e.type === 'bounce') { ev.push({ t: e.t, type: 'blip', note: note(e.n), gain: +Math.min(0.85, 0.45 + e.n * 0.008).toFixed(2), dur: 0.12 }); if (e.n % 10 === 0) ev.push({ t: e.t, type: 'coin', note: 'C7', gain: 0.5 }); }
  if (e.type === 'escape') { ev.push({ t: e.t - 1.5, type: 'riser', gain: 0.45, dur: 1.5 }); ev.push({ t: e.t, type: 'glass', note: 'C6', gain: 0.8 }); ev.push({ t: e.t, type: 'impact', gain: 0.7 }); ev.push({ t: e.t + 0.1, type: 'coin', note: 'G6', gain: 0.9 }); }
}
ev.push({ t: 13.25, type: 'whoosh', gain: 0.6, dur: 0.6 });   // transition pixel-mosaic
ev.push({ t: 13.55, type: 'coin', note: 'G6', gain: 0.8 });     // carte de fin
ev.push({ t: 13.85, type: 'chime', note: 'C6', gain: 0.5, dur: 1.2 });
const spec = { duration: 15.0, seed: 1007, bpm: 125, key: 'A', scale: 'minpent', reverb: 0.14,
  music: { preset: 'chiptune', gain: 0.36, octave: 4, loop: false }, events: ev.sort((a, b) => a.t - b.t) };
fs.writeFileSync(path.join(__dirname, 'sound.json'), JSON.stringify(spec, null, 1));
console.log('events', ev.length);
