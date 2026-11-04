// make_sound.mjs — écrit sound.json (preset « pulse » 120 bpm + SFX calés sur les cuts de index.html)
// usage : node out/shorts/brut-meme__engagement__test-des-3-secondes-stroop/src/make_sound.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const r3 = x => Math.round(x * 1000) / 1000;
const ev = [];
const add = (t, type, gain, extra = {}) => ev.push({ t: r3(t), type, gain, ...extra });

[0, 1.0, 2.0, 4.25, 6.45, 8.6, 12.2].forEach(t => add(t, 'impact', 0.95));   // cuts de scène
add(0.4, 'pop', 0.8); add(1.25, 'whoosh', 0.5); add(1.5, 'thud', 0.8);
const ROUNDS = [[2.0, 0.5], [4.25, 0.4], [6.45, 0.3]];
ROUNDS.forEach(([t0, step], i) => {
  ['E5', 'E5', 'E5'].forEach((n, k) => { add(t0 + k * step, 'tick', 0.75, { note: n }); if (k) add(t0 + k * step, 'impact', 0.45); });
  const rev = t0 + 3 * step;
  add(rev, 'impact', 1.0); add(rev, 'coin', 0.55, { note: ['A5', 'C6', 'E6'][i] });
});
add(5.85, 'riser', 0.5, { dur: 0.6 });
add(9.1, 'whoosh', 0.55); add(10.4, 'impact', 0.7); add(12.45, 'whoosh', 0.5);
add(12.7, 'pop', 0.8); add(13.0, 'pop', 0.7); add(13.0, 'thud', 0.6);
[13.5, 14.0, 14.5].forEach(t => add(t, 'tick', 0.35, { note: 'A5' }));
add(15.0, 'chime', 0.5, { note: 'A5' });

const spec = { duration: 15.5, seed: 47, bpm: 120, key: 'A', scale: 'minor',
  music: { preset: 'pulse', gain: 0.45, octave: 3, density: 0.6, loop: false }, events: ev.sort((a, b) => a.t - b.t) };
fs.writeFileSync(path.join(here, 'sound.json'), JSON.stringify(spec, null, 1));
console.log('sound.json', ev.length, 'events');
