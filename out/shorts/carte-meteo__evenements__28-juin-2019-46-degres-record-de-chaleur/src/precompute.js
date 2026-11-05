// precompute.js — lignes de courant de l'épisode de chaleur (flux de sud), intégrées en Node une fois -> wind.json.
// Usage (depuis la racine) : node out/shorts/carte-meteo__evenements__28-juin-2019-46-degres-record-de-chaleur/src/precompute.js
// Champ SCHÉMATIQUE (°/s, lon/lat) : remontée d'air chaud du sud entre une dépression sur la péninsule Ibérique
// (rotation antihoraire) et un anticyclone sur l'Europe centrale (rotation horaire). Ce n'est pas une analyse du 28/06/2019.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { streamlines } from './meteo.js';
import { rng } from '../../../tools/lib/svi.js';

const SEED = 28;
const here = path.dirname(fileURLToPath(import.meta.url));
function vel(lon, lat) {
  let u = 0.05, v = 0.36;
  const hx = lon - 11, hy = lat - 50.5, lx = lon + 4, ly = lat - 40.5;
  const wh = 0.07 * Math.exp(-(hx * hx + hy * hy) / 60), wl = 0.09 * Math.exp(-(lx * lx + ly * ly) / 40);
  u += wh * hy - wl * ly; v += -wh * hx + wl * lx;          // horaire autour de l'A, antihoraire autour de la D
  return [u, v];
}
const r = rng(SEED);
const seeds = [];
for (let lat = 34; lat <= 54; lat += 0.7) for (let lon = -7; lon <= 13; lon += 0.75) seeds.push([lon + (r() - 0.5) * 0.5, lat + (r() - 0.5) * 0.5]);
const STEPS_PER_SEC = 15;
const lines = streamlines(vel, seeds, { dt: 1 / STEPS_PER_SEC, steps: 130, bounds: [-9, 33, 15, 56] });
const GAP = 18;
const particles = lines.map((l, i) => ({ l: i, ph: +(r() * (l.length + GAP)).toFixed(2), sp: +(0.85 + r() * 0.3).toFixed(3) }));
fs.writeFileSync(path.join(here, 'wind.json'), JSON.stringify({ seed: SEED, stepsPerSec: STEPS_PER_SEC, gap: GAP, field: 'flux de sud (schématique)', lines, particles }));
console.log(JSON.stringify({ lines: lines.length, points: lines.reduce((a, l) => a + l.length, 0), kb: Math.round(fs.statSync(path.join(here, 'wind.json')).size / 1024) }));
