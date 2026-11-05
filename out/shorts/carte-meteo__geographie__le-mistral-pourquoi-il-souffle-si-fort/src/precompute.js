// precompute.js — lignes de courant du mistral, intégrées en Node une fois -> wind.json (le navigateur ne fait que relire).
// Usage (depuis la racine) : node out/shorts/carte-meteo__geographie__le-mistral-pourquoi-il-souffle-si-fort/src/precompute.js
// Champ schématique (°/s, lon/lat) : flux de nord-nord-ouest, convergence vers le couloir rhodanien entre le Massif central
// (à l'ouest) et les Alpes (à l'est) qui repoussent et freinent l'air, accélération dans le couloir, éventail sur le golfe du Lion.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { streamlines } from './meteo.js';
import { rng } from '../../../tools/lib/svi.js';

const SEED = 11;
const here = path.dirname(fileURLToPath(import.meta.url));
const ss = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
// axe du couloir : Lyon 45,76 / 4,83 -> Valence 44,93 / 4,89 -> Montélimar 44,56 / 4,75 -> Avignon 43,95 / 4,81 -> delta
const AX = [[47.5, 4.9], [46.3, 4.85], [45.76, 4.83], [45.2, 4.80], [44.93, 4.89], [44.56, 4.75], [43.95, 4.81], [43.6, 4.65], [43.3, 4.72], [40, 5.4]];
function axis(lat) {
  for (let i = 0; i < AX.length - 1; i++) { const [a, la] = AX[i], [b, lb] = AX[i + 1]; if (lat <= a && lat >= b) return la + (lb - la) * (a - lat) / (a - b); }
  return lat > AX[0][0] ? AX[0][1] : AX[AX.length - 1][1];
}
function vel(lon, lat) {
  const dx = lon - axis(lat);
  let u = 0.14, v = -0.40;
  // rotation géostrophique : horaire autour de l'anticyclone (golfe de Gascogne), antihoraire autour de la dépression (golfe de Gênes)
  const hx = lon + 5.5, hy = lat - 47.2, lx = lon - 9.6, ly = lat - 43.6;
  const wh = 0.16 * Math.exp(-(hx * hx + hy * hy) / 50), wl = 0.2 * Math.exp(-(lx * lx + ly * ly) / 30);
  u += wh * hy - wl * ly; v += -wh * hx + wl * lx;
  const conv = ss(43.9, 44.8, lat) * (1 - ss(47.4, 48.6, lat)) * Math.exp(-(((dx / 2.4)) ** 2));
  u += -0.30 * dx * conv;                                   // l'air converge vers le couloir
  const inC = ss(43.2, 43.8, lat) * (1 - ss(45.9, 46.6, lat)) * Math.exp(-(((dx / 0.6)) ** 2));
  v -= 0.95 * inC; u *= (1 - 0.75 * inC);                   // et accélère dans le couloir
  const sea = 1 - ss(43.0, 43.75, lat);
  u += sea * (0.30 * dx * Math.exp(-(((dx / 2.2)) ** 2)) + 0.06); v -= sea * 0.55 * Math.exp(-(((dx / 1.9)) ** 2));   // éventail en mer
  const mc = Math.exp(-(((lon - 3.0) / 1.15) ** 2 + ((lat - 45.1) / 1.0) ** 2));   // Massif central
  const al = Math.exp(-(((lon - 6.75) / 0.85) ** 2 + ((lat - 45.1) / 1.35) ** 2)); // Alpes
  u += 0.42 * (lon - 3.0) * mc + 0.42 * (lon - 6.75) * al;  // les reliefs repoussent l'air vers le couloir
  const f = 1 - 0.6 * Math.max(mc, al);
  return [u * f, v * f];
}
const r = rng(SEED);
const seeds = [];
for (let lat = 40.8; lat <= 54.5; lat += 0.55) for (let lon = -6; lon <= 12; lon += 0.6) seeds.push([lon + (r() - 0.5) * 0.5, lat + (r() - 0.5) * 0.5]);
// renfort de graines au nord du couloir (pour densifier les traînées qui s'y engouffrent)
for (let k = 0; k < 90; k++) seeds.push([3.6 + r() * 2.6, 45.6 + r() * 2.2]);
const STEPS_PER_SEC = 15;
const lines = streamlines(vel, seeds, { dt: 1 / STEPS_PER_SEC, steps: 130, bounds: [-9, 36, 15, 56] });
const GAP = 18;
const particles = lines.map((l, i) => ({ l: i, ph: +(r() * (l.length + GAP)).toFixed(2), sp: +(0.85 + r() * 0.3).toFixed(3) }));
const out = { seed: SEED, stepsPerSec: STEPS_PER_SEC, gap: GAP, field: 'mistral (schématique)', lines, particles };
fs.writeFileSync(path.join(here, 'wind.json'), JSON.stringify(out));
const npts = lines.reduce((a, l) => a + l.length, 0);
console.log(JSON.stringify({ lines: lines.length, points: npts, kb: Math.round(fs.statSync(path.join(here, 'wind.json')).size / 1024) }));
