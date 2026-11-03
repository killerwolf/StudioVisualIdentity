/**
 * aq.js — moteur partagé de l'identité « Aquarelle Conte » (copié à l'identique dans chaque short).
 *  - p5.js v2 (mode instance, pas de preload) : lavis aquarelle = polygones déformés récursivement,
 *    ~20-40 couches à faible opacité, pré-rendus UNE fois dans des p5.Graphics (ready), puis composés
 *    par frame via drawingContext.drawImage (rapide).
 *  - transition signature « lavis qui s'ouvre » : un calque est révélé à travers une tache déformée
 *    qui grandit, en 3 paliers d'opacité (bord de lavis).
 *  - grain de papier : relief cold-press calculé une fois en JS -> canvas en soft-light au-dessus de tout.
 *  - Paper.js : helpers « vecteur aquarelle » (copies jitterées translucides + bord foncé).
 */
import * as S from '/out/tools/lib/svi.js';

export const T = {
  bg: '#F7F1E6', surface: '#EFE4D0', coral: '#E88D72', blue: '#6C9BCF', gold: '#F2C14E', green: '#7FB685',
  text: '#3A3042', coralDeep: '#B2573E', blueDeep: '#4E7FB8', night: '#33406E', ink: '#2B2440', bark: '#8A6A55',
  sand: '#E9D3A8', stone: '#D9C29A', stoneEdge: '#A88A5E', sea: '#5B8CC4',
};
export const FONTS = [{ family: 'Fraunces', pkg: 'fraunces', weight: 700 }, { family: 'Nunito', pkg: 'nunito', weight: 600 }];
export const MOTION = { enter: 0.6, exit: 0.4, bloom: 0.8, fadeEnd: 0.8, stagger: 0.12 };

export const hex = h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];

/* ---------- lavis (p5) ---------- */
export function washer(seed) {
  const R = S.rng(seed);
  const gauss = () => { let u = 0, v = 0; while (!u) u = R(); while (!v) v = R(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  function deform(pts, depth, vari) {
    if (depth === 0) return pts;
    const out = [];
    for (let i = 0; i < pts.length; i++) {
      const a = pts[i], b = pts[(i + 1) % pts.length];
      const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
      out.push(a, [(a[0] + b[0]) / 2 + gauss() * len * vari * a[2], (a[1] + b[1]) / 2 + gauss() * len * vari * a[2], S.clamp(a[2] * (0.8 + R() * 0.4), .2, 2)]);
    }
    return deform(out, depth - 1, vari);
  }
  const poly = (pts, v = 1) => pts.map(p => [p[0], p[1], p[2] ?? v]);
  function wash(g, pts, color, { layers = 30, alpha = 9, vari = .2, base = 3, sub = 2, edge = true } = {}) {
    const [r, gg, b] = hex(color);
    const basePts = deform(poly(pts), base, vari);
    g.noStroke();
    for (let k = 0; k < layers; k++) {
      const p = deform(basePts, sub, vari * .9);
      g.fill(r, gg, b, alpha); g.beginShape(); for (const q of p) g.vertex(q[0], q[1]); g.endShape(g.CLOSE);
      if (edge && k % 6 === 0) {
        g.noFill(); g.stroke(r * .8, gg * .8, b * .8, alpha * 1.6); g.strokeWeight(1.4);
        g.beginShape(); for (const q of p) g.vertex(q[0], q[1]); g.endShape(g.CLOSE); g.noStroke();
      }
    }
  }
  /** contour normalisé (rayon 1) d'une tache pour la transition « lavis qui s'ouvre » */
  function blob(n = 12, depth = 3) { return deform(poly(circle(0, 0, 1, n)), depth, .16).map(p => [p[0], p[1]]); }
  return { R, gauss, deform, wash, blob };
}
export const circle = (cx, cy, r, n = 14) => Array.from({ length: n }, (_, i) => [cx + Math.cos(i / n * 6.283) * r, cy + Math.sin(i / n * 6.283) * r]);
export const ellipse = (cx, cy, rx, ry, n = 16) => Array.from({ length: n }, (_, i) => [cx + Math.cos(i / n * 6.283) * rx, cy + Math.sin(i / n * 6.283) * ry]);
export const hill = (y0, amp, freq, phase, yb = 1920, x0 = -80, x1 = 1260) => { const pts = []; for (let x = x0; x <= x1; x += 80) pts.push([x, y0 + Math.sin(x * freq + phase) * amp]); pts.push([x1, yb], [x0, yb]); return pts; };
export const star = (cx, cy, r) => Array.from({ length: 10 }, (_, i) => { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * .45 : r; return [cx + Math.cos(a) * rr, cy + Math.sin(a) * rr, .4]; });
/** bande horizontale subdivisée (bord supérieur tous les `step` px) : lavis de ciel sans « montagnes » */
export const band = (y0, y1, slope = 0, step = 90, x0 = -80, x1 = 1320) => { const pts = []; for (let x = x0; x <= x1; x += step) pts.push([x, y0 + slope * (x - x0) / (x1 - x0)]); pts.push([x1, y1], [x0, y1]); return pts; };
export const rect = (x, y, w, h) => [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];

/** démarre p5 (instance) et crée les calques demandés {nom:[w,h]} */
export function startP5(parent, layers) {
  return new Promise(res => {
    new p5(p => {
      p.setup = () => {
        p.pixelDensity(1); p.createCanvas(1080, 1920).parent(parent); p.noLoop();
        const L = {};
        for (const [k, [w, h]] of Object.entries(layers)) { L[k] = p.createGraphics(w, h); L[k].pixelDensity(1); L[k].clear(); }
        res({ p, L });
      };
    });
  });
}
export const el = g => g.elt || g.canvas;
/** composite un calque (alpha, décalage) */
export function draw(ctx, g, x = 0, y = 0, a = 1) {
  if (a <= 0.002) return;
  ctx.globalAlpha = Math.min(1, a); ctx.drawImage(el(g), x, y); ctx.globalAlpha = 1;
}
/** transition signature : révèle g à travers une tache (blob normalisé) de rayon r centrée (cx,cy) */
export function bloom(ctx, g, x, y, blobPts, cx, cy, r, a = 1) {
  if (r <= 1 || a <= 0) return;
  for (const [k, al] of [[1.0, .35], [.93, .45], [.86, 1]]) {
    ctx.save(); ctx.beginPath();
    blobPts.forEach((q, i) => { const X = cx + q[0] * r * k, Y = cy + q[1] * r * k; i ? ctx.lineTo(X, Y) : ctx.moveTo(X, Y); });
    ctx.closePath(); ctx.clip(); ctx.globalAlpha = al * a; ctx.drawImage(el(g), x, y); ctx.restore();
  }
  ctx.globalAlpha = 1;
}

/** variante douce (5 paliers) pour les grands écarts de valeur (nuit -> matin) */
export function bloomSoft(ctx, g, x, y, blobPts, cx, cy, r, a = 1) {
  if (r <= 1 || a <= 0) return;
  for (const [k, al] of [[1.0, .16], [.965, .22], [.93, .3], [.895, .45], [.86, 1]]) {
    ctx.save(); ctx.beginPath();
    blobPts.forEach((q, i) => { const X = cx + q[0] * r * k, Y = cy + q[1] * r * k; i ? ctx.lineTo(X, Y) : ctx.moveTo(X, Y); });
    ctx.closePath(); ctx.clip(); ctx.globalAlpha = al * a; ctx.drawImage(el(g), x, y); ctx.restore();
  }
  ctx.globalAlpha = 1;
}

/* ---------- grain de papier (soft-light) + vignette chaude ---------- */
export function paperGrain(parent, seed = 31) {
  const w = 1080, h = 1920, R = S.rng(seed);
  const hgt = new Float32Array(w * h);
  for (const [div, amp] of [[1, .5], [3, .9], [9, 1.6]]) {
    const sw = Math.ceil(w / div), sh = Math.ceil(h / div);
    const c = document.createElement('canvas'); c.width = sw; c.height = sh;
    const cx = c.getContext('2d'), im = cx.createImageData(sw, sh);
    for (let i = 0; i < sw * sh; i++) { const v = R() * 255; im.data[i * 4] = im.data[i * 4 + 1] = im.data[i * 4 + 2] = v; im.data[i * 4 + 3] = 255; }
    cx.putImageData(im, 0, 0);
    const big = document.createElement('canvas'); big.width = w; big.height = h;
    const bx = big.getContext('2d'); bx.imageSmoothingEnabled = true; bx.filter = `blur(${Math.max(.6, div * .5)}px)`; bx.drawImage(c, 0, 0, w, h);
    const d = bx.getImageData(0, 0, w, h).data;
    for (let i = 0; i < w * h; i++) hgt[i] += (d[i * 4] / 255 - .5) * amp;
  }
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const cx = c.getContext('2d'), im = cx.createImageData(w, h);
  for (let y = 1; y < h - 1; y++) for (let x = 1; x < w - 1; x++) {
    const i = y * w + x;
    const l = (hgt[i + 1] - hgt[i - 1]) * .6 + (hgt[i + w] - hgt[i - w]) * .4;
    const v = S.clamp(128 + l * 170 - hgt[i] * 14, 0, 255);
    im.data[i * 4] = im.data[i * 4 + 1] = im.data[i * 4 + 2] = v; im.data[i * 4 + 3] = 255;
  }
  cx.putImageData(im, 0, 0);
  c.style.cssText = 'position:absolute;inset:0;mix-blend-mode:soft-light;opacity:.55;pointer-events:none;z-index:50';
  document.getElementById(parent).appendChild(c);
  const v = document.createElement('div');
  v.style.cssText = 'position:absolute;inset:0;pointer-events:none;z-index:51;mix-blend-mode:multiply;background:radial-gradient(ellipse 75% 70% at 50% 45%, rgba(0,0,0,0) 62%, rgba(150,110,80,.22) 100%)';
  document.getElementById(parent).appendChild(v);
}

/* ---------- texte : « l'encre s'imbibe » ---------- */
/** opacité/flou/translation d'un bloc de texte entre tin et tout */
export function inkText(node, t, tin, tout) {
  const a = S.seg(t, tin, tin + MOTION.enter, S.ease.outCubic) * (1 - S.seg(t, tout - MOTION.exit, tout, S.ease.inOutSine));
  node.style.opacity = a.toFixed(3);
  const blur = (1 - S.seg(t, tin, tin + MOTION.enter, S.ease.outCubic)) * 8;
  node.style.filter = blur > .05 ? `blur(${blur.toFixed(2)}px)` : 'none';
  node.style.transform = `translateY(${((1 - a) * 18).toFixed(1)}px) scale(${(1 + Math.sin(t * .9) * .004).toFixed(4)})`;
}
/** fondu final vers le papier (fin commune aux shorts de l'identité) */
export function paperFade(node, t, dur) { node.style.opacity = S.seg(t, dur - MOTION.fadeEnd, dur, S.ease.inOutSine).toFixed(3); }

/* ---------- Paper.js : vecteur aquarelle ---------- */
export function paperSetup(canvas) {
  canvas.setAttribute('hidpi', 'off'); canvas.setAttribute('data-paper-hidpi', 'off');
  canvas.width = 1080; canvas.height = 1920;
  paper.setup(canvas); paper.view.autoUpdate = false;
  return paper;
}
/** transforme un Path en Group « aquarelle » : n copies translucides légèrement déformées + bord foncé */
export function wc(path, color, { seed = 1, copies = 3, jitter = 2.5, alpha = .5, edge = .55, edgeW = 1.8 } = {}) {
  const R = S.rng(seed), g = new paper.Group(); g.applyMatrix = false;
  for (let k = 0; k < copies; k++) {
    const c = path.clone({ insert: false });
    if (c.segments) for (const s of c.segments) s.point = s.point.add([(R() - .5) * jitter * 2, (R() - .5) * jitter * 2]);
    c.fillColor = new paper.Color(color); c.fillColor.alpha = alpha + (k === 0 ? .25 : 0); c.strokeColor = null;
    g.addChild(c);
  }
  if (edge > 0) {
    const e = path.clone({ insert: false }); e.fillColor = null;
    const [r, gg, b] = hex(color); e.strokeColor = new paper.Color(r * .62 / 255, gg * .62 / 255, b * .62 / 255, edge); e.strokeWidth = edgeW;
    g.addChild(e);
  }
  path.remove();
  return g;
}
export const P = (x, y) => new paper.Point(x, y);
