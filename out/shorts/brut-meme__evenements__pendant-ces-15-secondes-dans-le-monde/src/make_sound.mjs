// make_sound.mjs — écrit sound.json (preset « pulse » 120 bpm + SFX calés sur les cuts et les compteurs de index.html)
// usage : node out/shorts/brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde/src/make_sound.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const r3 = x => Math.round(x * 1000) / 1000;
const ev = [];
const add = (t, type, gain, extra = {}) => ev.push({ t: r3(t), type, gain, ...extra });

const CUTS = [0, 2.2, 3.9, 5.5, 7.2, 8.9, 10.9, 12.4, 13.9];
CUTS.forEach(t => add(t, 'impact', 0.95));
[0.6, 2.7, 4.4, 6.0, 7.7, 9.4, 11.4].forEach(t => add(t, 'pop', 0.7));        // slams des stickers
// naissances : un blip par bébé compté (4,2/s) pendant la scène
for (let k = Math.ceil(2.2 * 4.2); k / 4.2 < 3.9; k++) add(k / 4.2, 'blip', 0.3, { note: 'E6' });
// décès : thud sourd (1,9/s)
for (let k = Math.ceil(3.9 * 1.9); k / 1.9 < 5.5; k++) add(k / 1.9, 'thud', 0.35);
// éclairs : un claquement par temps (nouvelle salve d'éclairs dessinés)
for (let t = 5.5; t < 7.2; t += 0.5) add(t, 'click', 0.7);
// e-mails : ticks rapides
for (let t = 7.3; t < 8.9; t += 0.125) add(t, 'tick', 0.22, { note: 'A6' });
add(8.95, 'whoosh', 0.6); add(9.9, 'whoosh', 0.45);
// coeur : battement à 72/min
for (let k = Math.ceil(10.9 * 1.2); k / 1.2 < 12.4; k++) add(k / 1.2, 'thud', 0.9);
[12.55, 12.75, 12.95, 13.15, 13.35, 13.55].forEach((t, i) => add(t, 'tick', 0.6, { note: ['A5', 'B5', 'C6', 'D6', 'E6', 'A6'][i] }));
add(14.1, 'whoosh', 0.5); add(14.25, 'impact', 0.7); add(14.4, 'pop', 0.8);
add(15.0, 'impact', 1.0); add(15.0, 'chime', 0.6, { note: 'A5' });

const spec = { duration: 16.0, seed: 15, bpm: 120, key: 'A', scale: 'minor',
  music: { preset: 'pulse', gain: 0.45, octave: 3, density: 0.6, loop: false }, events: ev.sort((a, b) => a.t - b.t) };
fs.writeFileSync(path.join(here, 'sound.json'), JSON.stringify(spec, null, 1));
console.log('sound.json', ev.length, 'events');
