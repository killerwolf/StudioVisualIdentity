#!/usr/bin/env node
/* make_sound.cjs — écrit sound.json (spec de out/tools/sound.py) depuis trace.json (événements de l'automate) :
 * chiptune 125 bpm (tempo de l'identité) ; compte à rebours sur les temps ; à chaque temps de la bataille, un blip
 * à la note de la couleur EN TÊTE (le leader « chante ») ; poussées (force 5) = pop dans la couleur ; changement de leader
 * = coin ; écran plein = chime ; gel 12,0 s = impact + coin ; pixel-mosaic = whoosh ; carte de fin = coin + chime.
 * USAGE : node out/shorts/pixel-arcade__engagement__quelle-couleur-conquiert-l-ecran/src/make_sound.cjs
 */
const fs = require('fs'), path = require('path');
const tr = JSON.parse(fs.readFileSync(path.join(__dirname, 'trace.json'), 'utf8'));
const NOTE = ['', 'E5', 'G5', 'A5', 'C6'];              // ROSE, VERTE, JAUNE, BLEUE (mêmes notes que la course de billes)
const ev = [{ t: 0.05, type: 'coin', note: 'E6', gain: 0.7 }];
[0.96, 1.44, 1.92].forEach(t => ev.push({ t, type: 'blip', note: 'A5', gain: 0.9, dur: 0.16 }));
ev.push({ t: 2.4, type: 'blip', note: 'A6', gain: 1.0, dur: 0.3 }, { t: 2.4, type: 'whoosh', gain: 0.5, dur: 0.5 });
// leader au fil du temps (depuis les événements 'lead')
const leads = tr.events.filter(e => e.type === 'lead');
const leaderAt = t => { let L = 0; for (const e of leads) if (e.t <= t) L = e.c; return L; };
for (let t = 2.88; t < tr.endT - 0.01; t += 0.48) { const L = leaderAt(t); if (L) ev.push({ t: +t.toFixed(3), type: 'blip', note: NOTE[L], gain: 0.55 }); }
let lastCoin = -1;
for (const e of tr.events) {
  if (e.type === 'surge') ev.push({ t: e.t, type: 'pop', note: NOTE[e.c], gain: 0.6 });
  if (e.type === 'lead' && e.t > 2.8 && e.t - lastCoin > 0.25 && e.t < tr.endT) { ev.push({ t: e.t, type: 'coin', note: 'C7', gain: 0.45 }); lastCoin = e.t; }
  if (e.type === 'full') ev.push({ t: e.t, type: 'chime', note: 'G5', gain: 0.6 }, { t: e.t, type: 'impact', gain: 0.4 });
}
ev.push({ t: tr.endT, type: 'impact', gain: 0.7 }, { t: tr.endT, type: 'coin', note: 'C7', gain: 0.9 }, { t: tr.endT + 0.05, type: 'chime', note: 'G5', gain: 0.5 });
ev.push({ t: 13.3, type: 'whoosh', gain: 0.6, dur: 0.6 }, { t: 13.6, type: 'coin', note: 'G6', gain: 0.8 }, { t: 13.9, type: 'chime', note: 'C6', gain: 0.5, dur: 1.4 });
const spec = { duration: 15.5, seed: 175, bpm: 125, key: 'C', scale: 'majpent', reverb: 0.12,
  music: { preset: 'chiptune', gain: 0.4, octave: 4, loop: false }, events: ev.sort((a, b) => a.t - b.t) };
fs.writeFileSync(path.join(__dirname, 'sound.json'), JSON.stringify(spec, null, 1));
console.log('events', ev.length);
