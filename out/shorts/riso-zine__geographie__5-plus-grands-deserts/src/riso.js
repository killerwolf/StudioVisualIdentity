/**
 * riso.js — système partagé de l'identité « riso-zine » (copie identique dans chaque short).
 *
 * Principe d'impression simulée :
 *  - chaque encre (jaune, rose, bleu) a sa propre couche p5.Graphics en niveaux de gris (blanc = 100 % d'encre) ;
 *  - au tirage, chaque couche est tramée (points sur une grille tournée, angle/pas propres à l'encre)
 *    et imprimée en MULTIPLY sur le papier, avec un défaut de repérage qui change à chaque « pas » (12 fps, on twos) ;
 *  - les titres DOM sont imprimés en deux passes (rose dessous, bleu dessus) décalées du même défaut de repérage ;
 *  - le grain, les manques d'encre et l'ondulation du papier sont ajoutés ensuite par post.py (OpenCV).
 */
import * as S from '/out/tools/lib/svi.js';

export const W = 1080, H = 1920;
export const HEX = { pink: '#FF48B0', blue: '#0078BF', yel: '#FFE800', ink: '#1A1A1A', paper: '#F6F0E4' };
export const INK = { yel: [255, 232, 0], pink: [255, 72, 176], blue: [0, 120, 191] };
export const PAPER = [246, 240, 228];
export const STEP_FPS = 12;                                   // animation « on twos »
export const qt = t => Math.floor(t * STEP_FPS + 1e-4) / STEP_FPS;
export const stepIndex = t => Math.floor(t * STEP_FPS + 1e-4);
// trames : angle (rad), pas (px). Angles différents = pas de moiré entre encres.
export const SCREENS = { yel: { angle: 0, pitch: 9 }, pink: { angle: Math.PI / 4, pitch: 8 }, blue: { angle: Math.PI / 12, pitch: 7 } };
export const ORDER = ['yel', 'pink', 'blue'];               // ordre de passage des tambours

export const FONTS = [
  { family: 'Space Mono', pkg: 'space-mono', weight: 700 },
  { family: 'Space Mono', pkg: 'space-mono', weight: 400 },
  { family: 'Permanent Marker', pkg: 'permanent-marker', weight: 400 },
];

function lattice(angle, pitch, seed) {
  const ca = Math.cos(angle), sa = Math.sin(angle), R = Math.hypot(W, H) / 2 + pitch;
  const r = S.rng(seed), out = [];
  for (let v = -R; v < R; v += pitch) for (let u = -R; u < R; u += pitch) {
    const x = W / 2 + u * ca - v * sa, y = H / 2 + u * sa + v * ca;
    if (x < -pitch || y < -pitch || x > W + pitch || y > H + pitch) continue;
    out.push(x, y, 0.86 + 0.28 * r());                       // facteur de taille stable par point (dots irréguliers)
  }
  return Float32Array.from(out);
}

/** crée la presse : canvas p5 principal + 3 couches d'encre. Résout {p, L, print}. */
export function makePress(parentId, seed = 1) {
  return new Promise(res => {
    new p5(p => {
      p.setup = () => {
        p.pixelDensity(1);
        p.createCanvas(W, H).parent(parentId);
        p.noLoop();
        const L = {};
        for (const k of ORDER) { const g = p.createGraphics(W, H); g.pixelDensity(1); L[k] = g; }
        const lat = {};
        for (const k of ORDER) lat[k] = lattice(SCREENS[k].angle, SCREENS[k].pitch, seed * 31 + k.length);
        const press = {
          p, L, lat,
          clear() { for (const k of ORDER) { const g = L[k]; g.push(); g.resetMatrix(); g.background(0); g.pop(); g.noStroke(); g.fill(255); } },
          /** imprime les 3 couches. mis = {yel:[dx,dy], pink:[..], blue:[..]} */
          print(mis) {
            const ctx = p.drawingContext;
            ctx.globalCompositeOperation = 'source-over';
            ctx.fillStyle = HEX.paper; ctx.fillRect(0, 0, W, H);
            ctx.globalCompositeOperation = 'multiply';
            for (const k of ORDER) {
              const px = L[k].drawingContext.getImageData(0, 0, W, H).data;
              const pts = lat[k], pitch = SCREENS[k].pitch, [ox, oy] = mis[k] || [0, 0];
              ctx.fillStyle = `rgb(${INK[k].join(',')})`;
              ctx.beginPath();
              for (let i = 0; i < pts.length; i += 3) {
                const x = pts[i], y = pts[i + 1];
                const xi = x < 0 ? 0 : x >= W ? W - 1 : x | 0, yi = y < 0 ? 0 : y >= H ? H - 1 : y | 0;
                const c = px[(yi * W + xi) * 4] / 255;
                if (c < 0.03) continue;
                const r = (c > 0.97 ? pitch * 0.8 : pitch * 0.64 * Math.sqrt(c)) * pts[i + 2];
                ctx.moveTo(x + ox + r, y + oy); ctx.arc(x + ox, y + oy, r, 0, 6.2832);
              }
              ctx.fill();
            }
            ctx.globalCompositeOperation = 'source-over';
          },
        };
        res(press);
      };
    }, document.getElementById(parentId));
  });
}

/** défaut de repérage pour un pas donné ; kick (0..1) = secousse supplémentaire (impacts) */
export function misreg(step, seed, kick = 0) {
  const R = S.rng(seed * 7919 + step * 104729);
  const a = 4 + 10 * kick;
  const pink = [(R() - 0.5) * 2 * a + 6, (R() - 0.5) * 2 * a + 4];
  const blue = [(R() - 0.5) * a * 0.8, (R() - 0.5) * a * 0.8];
  const yel = [(R() - 0.5) * a * 0.5, (R() - 0.5) * a * 0.5];
  return { pink, blue, yel };
}

/** applique la passe rose décalée aux titres DOM (.passP) */
export function shiftPasses(mis) {
  const [dx, dy] = mis.pink, [bx, by] = mis.blue;
  document.querySelectorAll('.passP').forEach(e => { e.style.translate = `${(dx - bx).toFixed(1)}px ${(dy - by).toFixed(1)}px`; });
}

/** blob « découpé main » : contour bruité autour d'une ellipse (aire ≈ π r² sx sy) */
export function blobPts(cx, cy, r, seed, { sx = 1, sy = 1, amp = 0.16, freq = 1.6, lobes = [], n = 120, rot = 0 } = {}) {
  const pts = [];
  for (let i = 0; i < n; i++) {
    const a = i / n * Math.PI * 2;
    let rr = 1 + amp * (S.noise2(Math.cos(a) * freq + seed * 3.7, Math.sin(a) * freq + seed * 1.3) - 0.5) * 2
      + 0.05 * (S.noise2(Math.cos(a) * 7 + seed, Math.sin(a) * 7 - seed) - 0.5);       // dentelure du ciseau
    for (const [la, lw, lh] of lobes) { const d = Math.atan2(Math.sin(a - la), Math.cos(a - la)); rr += lh * Math.exp(-(d * d) / (lw * lw)); }
    const x = Math.cos(a) * rr * r * sx, y = Math.sin(a) * rr * r * sy;
    pts.push([cx + x * Math.cos(rot) - y * Math.sin(rot), cy + x * Math.sin(rot) + y * Math.cos(rot)]);
  }
  return pts;
}
export function poly(g, pts) { g.beginShape(); for (const [x, y] of pts) g.vertex(x, y); g.endShape('close'); }

/** révélation d'un mot au marqueur, par pas : clip-path gauche->droite */
export function markerReveal(el, k) { el.style.clipPath = `inset(-20% ${((1 - S.clamp(k)) * 100).toFixed(1)}% -20% -10%)`; }

/** après un ctx.save()/restore() manuel (clip), p5 v2 garde en cache un style qui n'est plus celui du contexte :
 *  un stroke() identique au cache serait ignoré (trait « sans encre »). On réaligne cache et contexte. */
export function resync(g) { g.fill(1); g.stroke(1); g.strokeWeight(1.01); g.strokeWeight(1); g.noStroke(); g.fill(255); }
