/**
 * meteo.js — système partagé de l'identité carte-meteo (copie identique dans chaque short).
 *
 * Navigateur : charger avant ce module  /node_modules/d3/dist/d3.min.js  et
 *              /node_modules/topojson-client/dist/topojson-client.min.js  (globaux `d3`, `topojson`).
 * Node       : seules `streamlines()` et `C` sont utilisées (precompute.js) ; rien ne touche au DOM à l'import.
 *
 * Principe de coût : la géographie (world-atlas countries-50m, Natural Earth) est décodée UNE fois par
 * topojson-client dans window.ready, filtrée (DROM retirés), découpée (Europe de l'Ouest) et projetée UNE fois
 * (d3.geoConicConformal) en coordonnées « base » -> Path2D. La caméra n'est qu'un ctx.setTransform.
 * Par image : isobares d3.contours (grille 116×200), traînées de vent lues dans des lignes de courant précalculées.
 */

export const C = {
  sea: '#CFE6F5', land: '#A9D486', coast: '#3E5A72', border: '#3E5A72', white: '#FFFFFF',
  warm: '#D63A2A', cold: '#1F5FD6', heat: '#F59A2C', text: '#10263D', muted: '#3E5A72',
  iso: '#587A96', wind: '#10263D', mount: '#86BE68', cloudEdge: '#8FB0C8',
};
export const FONT = { title: "'Space Grotesk'", body: "'Atkinson Hyperlegible'" };
export const FONTS = [
  { family: 'Space Grotesk', pkg: 'space-grotesk', weight: 700 },
  { family: 'Atkinson Hyperlegible', pkg: 'atkinson-hyperlegible', weight: 400 },
  { family: 'Atkinson Hyperlegible', pkg: 'atkinson-hyperlegible', weight: 700 },
];

// ───────────────────────── easings (équivalents GSAP nommés) ─────────────────────────
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const E = {
  backOut: (s = 1.4) => x => { const c3 = s + 1; return 1 + c3 * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2); },
  p2out: x => 1 - (1 - x) * (1 - x),
  p2inout: x => x < .5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2,
  p2in: x => x * x,
  sineInOut: x => -(Math.cos(Math.PI * x) - 1) / 2,
  linear: x => x,
};
export const seg = (t, a, b, e = E.linear) => e(clamp((t - a) / (b - a)));

// ───────────────────────── géographie (une fois) ─────────────────────────
/** Décode world-atlas, retire les DROM, découpe l'Europe de l'Ouest, projette une fois. */
export async function loadGeo({ fit = [[90, 560], [990, 1480]], clip = [[-400, -400], [1480, 2320]] } = {}) {
  const t0 = performance.now();
  const topo = await (await fetch('/node_modules/world-atlas/countries-50m.json')).json();   // fichier local (npm), pas de réseau
  const fc = topojson.feature(topo, topo.objects.countries);
  const fr = fc.features.find(f => f.properties.name === 'France');
  const before = fr.geometry.coordinates.length;
  // DROM et îles lointaines : on ne garde que les polygones dont le centroïde est en Europe (métropole, Corse, îles atlantiques)
  fr.geometry.coordinates = fr.geometry.coordinates.filter(p => {
    const [lon, lat] = d3.geoCentroid({ type: 'Polygon', coordinates: p });
    return lon > -6 && lon < 10 && lat > 41 && lat < 52;
  });
  const europe = fc.features.filter(f => {
    if (f.properties.name === 'France') return true;
    const [[x0, y0], [x1, y1]] = d3.geoBounds(f);
    return x0 < x1 && x1 > -16 && x0 < 22 && y1 > 33 && y0 < 60;
  });
  const proj = d3.geoConicConformal().parallels([44, 49]).rotate([-2.5, 0]).fitExtent(fit, fr).clipExtent(clip);
  const path = d3.geoPath(proj);
  const land = new Path2D(europe.map(f => path(f) || '').join(''));
  const france = new Path2D(path(fr));
  const keep = new Set(europe.map(f => f.id));
  const coast = new Path2D(path(topojson.mesh(topo, topo.objects.countries, (a, b) => a === b && keep.has(a.id))) || '');
  const borders = new Path2D(path(topojson.mesh(topo, topo.objects.countries, (a, b) => a !== b && keep.has(a.id) && keep.has(b.id))) || '');
  const P = (lon, lat) => proj([lon, lat]);
  const info = { franceParts: [before, fr.geometry.coordinates.length], countries: europe.length, decodeMs: Math.round(performance.now() - t0),
    scale: proj.scale(), translate: proj.translate() };
  return { proj, P, land, france, coast, borders, info };
}

// ───────────────────────── caméra 2D ─────────────────────────
/** caméra : le point base (bx,by) va à l'écran (sx,sy) au zoom k */
export const cam = (k, bx, by, sx = 540, sy = 1000) => ({ k, tx: sx - k * bx, ty: sy - k * by });
export const camLerp = (a, b, u) => ({ k: a.k + (b.k - a.k) * u, tx: a.tx + (b.tx - a.tx) * u, ty: a.ty + (b.ty - a.ty) * u });
export const toScreen = (c, [x, y]) => [c.k * x + c.tx, c.k * y + c.ty];
/** dérive lente dans un temps : zoom ×(1+dz) autour du centre écran */
export function drift(c, u, dz = 0.04, sx = 540, sy = 1000) {
  const k2 = c.k * (1 + dz * u);
  const bx = (sx - c.tx) / c.k, by = (sy - c.ty) / c.k;
  return { k: k2, tx: sx - k2 * bx, ty: sy - k2 * by };
}

const mapCache = new Map();   // clé caméra -> canvas : le fond de carte n'est rastérisé qu'une fois par plan fixe
function paintMap(ctx, geo, c, coastW) {
  ctx.fillStyle = C.sea; ctx.fillRect(0, 0, 1080, 1920);
  ctx.save();
  ctx.setTransform(c.k, 0, 0, c.k, c.tx, c.ty);
  ctx.fillStyle = C.land; ctx.fill(geo.land);
  ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.strokeStyle = C.border; ctx.globalAlpha = 0.55; ctx.lineWidth = 2 / c.k; ctx.setLineDash([9 / c.k, 7 / c.k]);
  ctx.stroke(geo.borders);
  ctx.setLineDash([]); ctx.globalAlpha = 1;
  ctx.strokeStyle = C.coast; ctx.lineWidth = coastW / c.k; ctx.stroke(geo.coast);
  ctx.restore();
}
/** fond de carte (mer, terres, frontières pointillées, trait de côte 3 px) ; cache=true pour un plan fixe */
export function drawMap(ctx, geo, c, { coastW = 3, cache = true } = {}) {
  if (!cache) return paintMap(ctx, geo, c, coastW);
  const key = `${c.k.toFixed(4)}|${c.tx.toFixed(2)}|${c.ty.toFixed(2)}|${coastW}`;
  let cv = mapCache.get(key);
  if (!cv) {
    if (mapCache.size > 6) mapCache.delete(mapCache.keys().next().value);
    cv = document.createElement('canvas'); cv.width = 1080; cv.height = 1920;
    paintMap(cv.getContext('2d'), geo, c, coastW); mapCache.set(key, cv);
  }
  ctx.drawImage(cv, 0, 0);
}

// ───────────────────────── isobares ─────────────────────────
const GX = 116, GY = 200, CELL = 10, OX = -40, OY = -40;   // grille écran débordante : les bords des contours restent hors cadre
const grid = new Float64Array(GX * GY);
/** pressure(bx,by,t) en hPa, coordonnées base. Recalcul par image (≈ 23 k échantillons + d3.contours). */
export function drawIsobars(ctx, c, pressure, t, { step = 4, from = 984, to = 1044, width = 3, color = C.iso } = {}) {
  for (let j = 0; j < GY; j++) for (let i = 0; i < GX; i++) {
    const sx = OX + i * CELL, sy = OY + j * CELL;
    grid[j * GX + i] = pressure((sx - c.tx) / c.k, (sy - c.ty) / c.k, t);
  }
  const th = []; for (let v = from; v <= to; v += step) th.push(v);
  const cs = d3.contours().size([GX, GY]).thresholds(th)(grid);
  ctx.save();
  ctx.strokeStyle = color; ctx.lineWidth = width; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.beginPath();
  for (const m of cs) for (const poly of m.coordinates) for (const ring of poly) {
    // lissage par milieux (courbes quadratiques) : pas d'escalier de grille
    const pts = ring.map(([x, y]) => [OX + x * CELL, OY + y * CELL]);
    if (pts.length < 3) continue;
    let [x0, y0] = pts[0], [x1, y1] = pts[1];
    ctx.moveTo((x0 + x1) / 2, (y0 + y1) / 2);
    for (let k = 1; k < pts.length; k++) {
      const [xa, ya] = pts[k], [xb, yb] = pts[(k + 1) % pts.length];
      ctx.quadraticCurveTo(xa, ya, (xa + xb) / 2, (ya + yb) / 2);
    }
  }
  ctx.stroke();
  ctx.restore();
}
/** champ de pression : centres gaussiens (base) + souffle lent noise3 (cycle ≈ 20 s) */
export function pressureField(centers, noise3, amp = 2.2) {
  return (x, y, t) => {
    let p = 1014;
    for (const c of centers) { const dx = x - c.x, dy = y - c.y; p += c.a * Math.exp(-(dx * dx + dy * dy) / (2 * c.s * c.s)); }
    return p + amp * (noise3(x / 240, y / 240, t / 20) - 0.5) * 2;
  };
}

// ───────────────────────── vent (lignes de courant précalculées) ─────────────────────────
/** Node : intègre des lignes de courant (RK2, pas dt) depuis des graines, dans un champ vel(lon,lat)->[u,v] en °/s */
export function streamlines(vel, seeds, { dt = 1 / 15, steps = 150, bounds = [-9, 36, 15, 55] } = {}) {
  const out = [];
  for (const [lon0, lat0] of seeds) {
    let lon = lon0, lat = lat0; const pts = [[lon, lat]];
    for (let s = 0; s < steps; s++) {
      const [u1, v1] = vel(lon, lat);
      const [u2, v2] = vel(lon + u1 * dt / 2, lat + v1 * dt / 2);
      lon += u2 * dt; lat += v2 * dt;
      if (lon < bounds[0] || lat < bounds[1] || lon > bounds[2] || lat > bounds[3]) break;
      pts.push([+lon.toFixed(3), +lat.toFixed(3)]);
    }
    if (pts.length > 12) out.push(pts);
  }
  return out;
}
/** navigateur : projette une fois les lignes (lon/lat -> base) */
export function prepareWind(geo, wind) {
  const lines = wind.lines.map(l => { const a = new Float32Array(l.length * 2); l.forEach((p, i) => { const q = geo.P(p[0], p[1]); a[2 * i] = q[0]; a[2 * i + 1] = q[1]; }); return a; });
  return { lines, particles: wind.particles, fps: wind.stepsPerSec };
}
/** traînées sombres translucides : position fermée en t (aucun état) */
export function drawWind(ctx, c, W, t, { alpha = 0.75, width = 6, trail = 16, gap = 18, speed = 1, density = 0.42, slow = 3, fast = 8, color = C.wind } = {}) {
  ctx.save();
  ctx.strokeStyle = color; ctx.lineWidth = width; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const at = (a, f) => { const i = Math.floor(f), u = f - i; const x = a[2 * i] + (a[2 * i + 2] - a[2 * i]) * u, y = a[2 * i + 1] + (a[2 * i + 3] - a[2 * i + 1]) * u; return [c.k * x + c.tx, c.k * y + c.ty]; };
  for (const p of W.particles) {
    if (((p.l * 0.6180339887) % 1) > density) continue;
    const a = W.lines[p.l], n = a.length / 2;
    const cyc = n + gap;
    const f = ((p.ph + t * W.fps * p.sp * speed) % cyc + cyc) % cyc;
    if (f < 1 || f > n - 1.001) continue;
    const head = f, tail = Math.max(0, f - trail);
    const life = Math.min(1, head / 8, (n - 1 - head) / 8);
    if (life <= 0) continue;
    const h = at(a, head);
    if (h[0] < -60 || h[0] > 1140 || h[1] < -60 || h[1] > 1980) continue;
    // vitesse locale (px base par pas) : les traînées rapides sont plus sombres et plus épaisses (le couloir ressort)
    const ih = Math.min(n - 2, Math.floor(head)), spd = Math.hypot(a[2 * ih + 2] - a[2 * ih], a[2 * ih + 3] - a[2 * ih + 1]);
    const w = Math.min(1, Math.max(0, (spd - slow) / (fast - slow)));
    // traînée effilée : 3 tronçons, de la queue pâle à la tête sombre
    for (let k = 0; k < 3; k++) {
      const f0 = tail + (head - tail) * k / 3, f1 = tail + (head - tail) * (k + 1) / 3;
      ctx.globalAlpha = alpha * life * [0.25, 0.55, 1][k] * (0.28 + 0.72 * w);
      ctx.lineWidth = width * [0.6, 0.8, 1][k] * (0.6 + 0.55 * w);
      ctx.beginPath();
      let q = at(a, f0); ctx.moveTo(q[0], q[1]);
      for (let g = Math.ceil(f0); g < f1; g++) { q = at(a, g); ctx.lineTo(q[0], q[1]); }
      q = at(a, f1); ctx.lineTo(q[0], q[1]);
      ctx.stroke();
    }
  }
  ctx.restore();
}

// ───────────────────────── le passage du front (transition signature) ─────────────────────────
const M = [0.5, 0.8660254];            // direction de déplacement : diagonale haut-gauche -> bas-droite (60°)
const D = [0.8660254, -0.5];           // direction de la ligne de front
export const FRONT = { dur: 0.9, s0: -160, s1: 2380 };
export const frontS = (t, t0) => FRONT.s0 + (FRONT.s1 - FRONT.s0) * seg(t, t0, t0 + FRONT.dur, E.p2inout);
const wave = u => 34 * Math.sin(u / 210 + 0.7) + 14 * Math.sin(u / 77 + 2.1);
function frontPts(s) {
  const pts = [];
  for (let u = -1250; u <= 1250; u += 25) { const o = s + wave(u); pts.push([D[0] * u + M[0] * o, D[1] * u + M[1] * o, u]); }
  return pts;
}
/** l'écran au temps t a-t-il déjà été balayé au point (x,y) ? -> temps de passage du front sur ce point */
export function frontPassTime(x, y, t0) {
  const sp = x * M[0] + y * M[1];
  for (let k = 0; k <= 60; k++) { const t = t0 + FRONT.dur * k / 60; if (frontS(t, t0) >= sp) return t; }
  return t0 + FRONT.dur;
}
/** clip = demi-plan déjà balayé (derrière le front) */
export function clipBehind(ctx, s) {
  const pts = frontPts(s);
  ctx.beginPath();
  ctx.moveTo(pts[0][0], pts[0][1]);
  for (const p of pts) ctx.lineTo(p[0], p[1]);
  const L = pts[pts.length - 1], F = pts[0];
  ctx.lineTo(L[0] - M[0] * 4000, L[1] - M[1] * 4000);
  ctx.lineTo(F[0] - M[0] * 4000, F[1] - M[1] * 4000);
  ctx.closePath();
  ctx.clip();
}
/** dessine la ligne de front : 'cold' = triangles bleus, 'warm' = demi-cercles rouges, symboles côté avant (+M) */
export function drawFront(ctx, s, kind = 'cold') {
  const col = kind === 'cold' ? C.cold : C.warm;
  const pts = frontPts(s);
  ctx.save();
  // liseré blanc pour détacher le front de la carte
  ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.strokeStyle = C.white; ctx.lineWidth = 20; ctx.beginPath();
  pts.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.stroke();
  ctx.strokeStyle = col; ctx.lineWidth = 11; ctx.stroke();
  ctx.fillStyle = col;
  const SP = 128, R = 34;
  for (let u = -1250 + 40; u < 1250; u += SP) {
    const i = Math.round((u + 1250) / 25), a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)], p = pts[i];
    let tx = b[0] - a[0], ty = b[1] - a[1]; const l = Math.hypot(tx, ty); tx /= l; ty /= l;
    let nx = -ty, ny = tx; if (nx * M[0] + ny * M[1] < 0) { nx = -nx; ny = -ny; }
    ctx.beginPath();
    if (kind === 'cold') {
      ctx.moveTo(p[0] - tx * R, p[1] - ty * R); ctx.lineTo(p[0] + tx * R, p[1] + ty * R);
      ctx.lineTo(p[0] + nx * R * 1.35, p[1] + ny * R * 1.35); ctx.closePath();
    } else {
      const ang = Math.atan2(ty, tx);
      const ccw = (nx * -ty + ny * tx) > 0;   // le demi-cercle passe par la normale avant
      ctx.moveTo(p[0] - tx * R, p[1] - ty * R);
      ctx.arc(p[0], p[1], R, ang + Math.PI, ang, ccw);
      ctx.closePath();
    }
    ctx.fill();
  }
  ctx.restore();
}

// ───────────────────────── typographie & cartouches ─────────────────────────
function rr(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
/** bandeau titre blanc en haut (sous la zone des 220 px) ; u = progression d'entrée 0..1 */
export function titleBand(ctx, { title, sub, accent = C.cold, y = 246, u = 1, titleSize = 108, subSize = 56 }) {
  if (u <= 0) return;
  const sc = E.backOut(1.4)(clamp(u));
  ctx.save();
  ctx.translate(72, y); ctx.scale(1, Math.max(0.001, sc)); ctx.translate(-72, -y);
  ctx.font = `700 ${titleSize}px ${FONT.title}`;
  let tw = ctx.measureText(title).width;
  if (tw > 796) { titleSize = Math.max(90, Math.floor(titleSize * 796 / tw)); ctx.font = `700 ${titleSize}px ${FONT.title}`; tw = ctx.measureText(title).width; }
  ctx.font = `700 ${subSize}px ${FONT.body}`;
  const sw = sub ? ctx.measureText(sub).width : 0;
  const w = Math.min(888, Math.max(tw, sw) + 92), h = sub ? titleSize + subSize + 70 : titleSize + 52;
  ctx.fillStyle = C.white; rr(ctx, 60, y, w, h, 26); ctx.fill();
  ctx.fillStyle = accent; rr(ctx, 60, y, 16, h, [26, 0, 0, 26]); ctx.fill();
  ctx.fillStyle = C.text; ctx.textBaseline = 'alphabetic';
  ctx.font = `700 ${titleSize}px ${FONT.title}`; ctx.fillText(title, 106, y + 24 + titleSize * 0.82);
  if (sub) { ctx.fillStyle = C.muted; ctx.font = `700 ${subSize}px ${FONT.body}`; ctx.fillText(sub, 108, y + 36 + titleSize + subSize * 0.8); }
  ctx.restore();
}
/** cartouche blanc (noms de lieux, légendes) ≥ 54 px ; ancre = point (x,y), placement 'r' | 'l' | 'c' | 'b' */
export function label(ctx, x, y, text, { size = 54, place = 'r', u = 1, dot = true, color = C.text, weight = 700 } = {}) {
  if (u <= 0) return;
  const sc = E.backOut(1.4)(clamp(u));
  ctx.save();
  ctx.font = `${weight} ${size}px ${FONT.body}`;
  const w = ctx.measureText(text).width + 44, h = size + 26;
  let bx = place === 'r' ? x + 26 : place === 'l' ? x - 26 - w : x - w / 2;
  let by = place === 'b' ? y + 24 : place === 'c' ? y - h / 2 : y - h / 2;
  if (place === 'b') bx = x - w / 2;
  bx = clamp(bx, 60, 960 - w);
  if (dot) { ctx.fillStyle = C.white; ctx.beginPath(); ctx.arc(x, y, 15 * sc, 0, 7); ctx.fill(); ctx.fillStyle = C.text; ctx.beginPath(); ctx.arc(x, y, 9 * sc, 0, 7); ctx.fill(); }
  ctx.translate(bx + w / 2, by + h / 2); ctx.scale(sc, sc); ctx.translate(-(bx + w / 2), -(by + h / 2));
  ctx.fillStyle = C.white; rr(ctx, bx, by, w, h, h / 2); ctx.fill();
  ctx.fillStyle = color; ctx.textBaseline = 'middle'; ctx.fillText(text, bx + 22, by + h / 2 + size * 0.04);
  ctx.restore();
}
/** pastille ronde : anneau coloré + disque blanc + valeur (Atkinson 700, auto-ajustée, ≥ 54 px) ; fill=true -> pastille pleine */
export function pastille(ctx, x, y, { r = 110, text, unit = '', ring = C.heat, u = 1, fill = false, max = 92 }) {
  if (u <= 0) return;
  const sc = E.backOut(1.4)(clamp(u));
  ctx.save();
  ctx.translate(x, y); ctx.scale(sc, sc);
  ctx.fillStyle = C.white; ctx.beginPath(); ctx.arc(0, 0, r + 7, 0, 7); ctx.fill();
  ctx.fillStyle = ring; ctx.beginPath(); ctx.arc(0, 0, r, 0, 7); ctx.fill();
  if (!fill) { ctx.fillStyle = C.white; ctx.beginPath(); ctx.arc(0, 0, r - 18, 0, 7); ctx.fill(); }
  const inner = 2 * (r - 18) - 22;
  let fs = max; ctx.font = `700 ${fs}px ${FONT.body}`;
  const tw = ctx.measureText(text).width; if (tw > inner) fs = Math.max(54, Math.floor(fs * inner / tw));
  ctx.font = `700 ${fs}px ${FONT.body}`;
  ctx.fillStyle = fill ? C.white : C.text; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(text, 0, unit ? -fs * 0.22 : fs * 0.04);
  if (unit) { ctx.font = `700 54px ${FONT.body}`; ctx.fillStyle = fill ? C.white : C.muted; ctx.fillText(unit, 0, fs * 0.5); }
  ctx.restore();
}
/** centre de pression : « A » (anticyclone, bleu) ou « D » (dépression, rouge), sur disque blanc */
export function pressureMark(ctx, x, y, letter, u = 1) {
  if (u <= 0) return;
  const sc = E.backOut(1.4)(clamp(u));
  ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc);
  ctx.fillStyle = C.white; ctx.beginPath(); ctx.arc(0, 0, 66, 0, 7); ctx.fill();
  ctx.fillStyle = letter === 'A' ? C.cold : C.warm; ctx.font = `700 100px ${FONT.title}`;
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(letter, 0, 6);
  ctx.restore();
}
/** pictogramme montagne plat (3 triangles), sans visage */
export function mountains(ctx, x, y, s = 1, u = 1) {
  if (u <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(s * u, s * u);
  const tri = (cx, h, w) => { ctx.beginPath(); ctx.moveTo(cx - w, 0); ctx.lineTo(cx, -h); ctx.lineTo(cx + w, 0); ctx.closePath(); ctx.fill(); ctx.stroke(); };
  ctx.fillStyle = C.mount; ctx.strokeStyle = C.coast; ctx.lineWidth = 4; ctx.lineJoin = 'round';
  tri(-46, 64, 40); tri(46, 70, 42); tri(0, 104, 54);
  ctx.fillStyle = C.white; ctx.beginPath(); ctx.moveTo(-17, -72); ctx.lineTo(0, -104); ctx.lineTo(17, -72); ctx.closePath(); ctx.fill();
  ctx.restore();
}
/** nuage plat (union de disques), contour bleu-gris */
export function cloud(ctx, x, y, s = 1, alpha = 1) {
  if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha = alpha; ctx.translate(x, y); ctx.scale(s, s);
  const blobs = [[-62, 8, 46], [-14, -22, 60], [44, -4, 50], [80, 18, 34], [0, 24, 44]];
  ctx.beginPath(); for (const [bx, by, r] of blobs) { ctx.moveTo(bx + r, by); ctx.arc(bx, by, r, 0, 7); }
  ctx.strokeStyle = C.cloudEdge; ctx.lineWidth = 10; ctx.stroke();
  ctx.fillStyle = C.white; ctx.fill();
  ctx.restore();
}
/** soleil plat : disque orange + 8 rayons (triangles), sans visage */
export function sun(ctx, x, y, r = 70, u = 1, rot = 0) {
  if (u <= 0) return;
  const sc = E.backOut(1.4)(clamp(u));
  ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc); ctx.rotate(rot);
  ctx.fillStyle = C.heat; ctx.strokeStyle = C.white; ctx.lineWidth = 8;
  for (let k = 0; k < 8; k++) { const a = k * Math.PI / 4; ctx.beginPath();
    ctx.moveTo(Math.cos(a - 0.2) * (r + 14), Math.sin(a - 0.2) * (r + 14)); ctx.lineTo(Math.cos(a) * (r + 52), Math.sin(a) * (r + 52));
    ctx.lineTo(Math.cos(a + 0.2) * (r + 14), Math.sin(a + 0.2) * (r + 14)); ctx.closePath(); ctx.fill(); }
  ctx.beginPath(); ctx.arc(0, 0, r, 0, 7); ctx.stroke(); ctx.fill();
  ctx.restore();
}
/** trait de rappel pastille -> lieu */
export function leader(ctx, x0, y0, x1, y1, u = 1) {
  if (u <= 0) return;
  ctx.save(); ctx.strokeStyle = C.white; ctx.lineWidth = 12; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x0 + (x1 - x0) * u, y0 + (y1 - y0) * u); ctx.stroke();
  ctx.strokeStyle = C.text; ctx.lineWidth = 5; ctx.stroke(); ctx.restore();
}
/** voile de chaleur : dégradé radial translucide (aucun filtre) */
export function heatVeil(ctx, x, y, r, color, alpha) {
  if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha = alpha;
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  const [r0, g0, b0] = [1, 3, 5].map(i => parseInt(color.slice(i, i + 2), 16));
  g.addColorStop(0, color); g.addColorStop(0.55, color); g.addColorStop(1, `rgba(${r0},${g0},${b0},0)`);
  ctx.fillStyle = g; ctx.fillRect(x - r, y - r, 2 * r, 2 * r); ctx.restore();
}
