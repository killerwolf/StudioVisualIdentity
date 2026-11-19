// outils.js — briques communes au moteur « lyrics-chemin » et à ses habillages (out/shared/chemin-moteur/habillages/*.js).
// Chemins (droite, vague, polyligne lissée), textures à graine fixe, ombre attachée à la lumière du monde, petits raccourcis Canvas.
import * as S from '/out/tools/lib/svi.js';
export { S };
export const W = 1080, H = 1920;
export const rad = d => d * Math.PI / 180;

// ---------- chemins : { len, at(d) -> {x, y, a} } ----------
export function straight(a, b) {
  const dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy), ang = Math.atan2(dy, dx);
  return { len, at: d => ({ x: a[0] + dx * d / len, y: a[1] + dy * d / len, a: ang }) };
}
export function wave(x0, x1, y, amp, wl, ph = 0) {
  const N = 400, xs = [], ds = [0]; let px = x0, py = y + amp * Math.sin(ph), d = 0;
  const yAt = x => y + amp * Math.sin(ph + (x - x0) / wl * 2 * Math.PI);
  for (let i = 0; i <= N; i++) { const x = x0 + (x1 - x0) * i / N, yy = yAt(x);
    if (i) { d += Math.hypot(x - px, yy - py); ds.push(d); } xs.push(x); px = x; py = yy; }
  return { len: d, at: dd => { let i = 0; while (i < N - 1 && ds[i + 1] < dd) i++; const k = (dd - ds[i]) / (ds[i + 1] - ds[i] || 1);
    const x = xs[i] + (xs[i + 1] - xs[i]) * k;
    return { x, y: yAt(x), a: Math.atan(amp * 2 * Math.PI / wl * Math.cos(ph + (x - x0) / wl * 2 * Math.PI)) }; } };
}
// chemin courbe : points denses, abscisse curviligne ; at(d, h) : angle = corde sur ±h (un mot rigide prend la corde de sa largeur)
export function polyline(pts) {
  const ds = [0]; for (let i = 1; i < pts.length; i++) ds.push(ds[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  const len = ds.at(-1);
  const pos = d => { d = S.clamp(d, 0, len); let lo = 0, hi = ds.length - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (ds[m] <= d) lo = m; else hi = m; }
    const k = (d - ds[lo]) / (ds[hi] - ds[lo] || 1); return [pts[lo][0] + (pts[hi][0] - pts[lo][0]) * k, pts[lo][1] + (pts[hi][1] - pts[lo][1]) * k]; };
  return { len, pts, ds, pos, at: (d, h = 6) => { const p = pos(d), a = pos(d - h), b = pos(d + h); return { x: p[0], y: p[1], a: Math.atan2(b[1] - a[1], b[0] - a[0]) }; } };
}
export function sub(path, d0, d1) { return { len: d1 - d0, at: (d, h) => path.at(d0 + d, h), off: d0, parent: path }; }
export function catmull(P, step = 4) {   // lissage Catmull-Rom -> points denses
  const out = []; for (let i = 0; i < P.length - 1; i++) { const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(P.length - 1, i + 2)];
    const n = Math.max(2, Math.ceil(Math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / step));
    for (let j = 0; j < n; j++) { const t = j / n, t2 = t * t, t3 = t2 * t;
      out.push([0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
                0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)]); } }
  out.push(P.at(-1)); return out; }

// ---------- textures (graine fixe) ----------
// fn(i, j, rng) -> [v, alpha] (gris) ou [r, alpha, g, b]
export function noiseTile(n, seed, fn) { const c = document.createElement('canvas'); c.width = c.height = n; const x = c.getContext('2d'), im = x.createImageData(n, n), r = S.rng(seed);
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { const [v, a, g, b] = fn(i, j, r); const o = (j * n + i) * 4; im.data[o] = v; im.data[o + 1] = g ?? v; im.data[o + 2] = b ?? v; im.data[o + 3] = a; }
  x.putImageData(im, 0, 0); return c; }
// bruit de valeur périodique (période f sur n pixels)
export const per = (i, j, f, n) => { const x = i / n * f, y = j / n * f, xi = Math.floor(x), yi = Math.floor(y), fx = x - xi, fy = y - yi,
  h = (a, b) => { const qq = Math.sin(((a % f) + f) % f * 127.1 + ((b % f) + f) % f * 311.7) * 43758.5453; return qq - Math.floor(qq); };
  const sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
  return S.lerp(S.lerp(h(xi, yi), h(xi + 1, yi), sx), S.lerp(h(xi, yi + 1), h(xi + 1, yi + 1), sx), sy); };

// ---------- dessin ----------
// ombre attachée à la lumière du monde (elle tourne avec la caméra, garde sa longueur à l'écran)
export function shadowed(c, cam, fn, blur = 14, ox = 9, oy = 13, a = 0.38, col = '4,14,40') {
  c.save(); c.shadowColor = `rgba(${col},${a})`; c.shadowBlur = blur * cam.s;
  const co = Math.cos(-cam.th), si = Math.sin(-cam.th);
  c.shadowOffsetX = (ox * co - oy * si) * cam.s; c.shadowOffsetY = (ox * si + oy * co) * cam.s; fn(); c.restore();
}
export const rr = (c, x, y, w, h, r) => { c.beginPath(); c.roundRect(x, y, w, h, r); };
export const lin = (c, x0, y0, x1, y1, stops) => { const g = c.createLinearGradient(x0, y0, x1, y1); stops.forEach(([k, col]) => g.addColorStop(k, col)); return g; };
export function strokePath(c, path, d0, d1, lw, col, dash) {
  if (d1 <= d0) return; c.beginPath(); const n = Math.max(2, Math.ceil((d1 - d0) / 6));
  for (let i = 0; i <= n; i++) { const p = path.at(d0 + (d1 - d0) * i / n); i ? c.lineTo(p.x, p.y) : c.moveTo(p.x, p.y); }
  c.lineWidth = lw; c.strokeStyle = col; c.lineCap = 'round'; c.lineJoin = 'round'; if (dash) c.setLineDash(dash); c.stroke(); c.setLineDash([]);
}
