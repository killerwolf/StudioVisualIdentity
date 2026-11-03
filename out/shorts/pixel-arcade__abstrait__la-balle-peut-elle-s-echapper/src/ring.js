/* ring.js — balle dans un anneau tournant à brèche (physique maison, pas fixe 1/240 s, 8 sous-pas / frame 30 fps).
 * Partagé entre la pré-simulation Node (simulate.cjs) et la page p5 (index.html). Coordonnées LOGIQUES 270×480.
 * Aucune fonction transcendante « fragile » (pas d'atan2/asin/hypot) dans la boucle : seulement sqrt, cos/sin
 * sur des angles quantifiés -> résultats identiques Node 22 / Chromium (vérifié, voir README).
 * Chaque rebond : la balle grandit (+GROW px), la tuile touchée s'allume ; la brèche (GAP_TILES tuiles) tourne par paliers de 5°.
 */
(function (root) {
  const CX = 135, CY = 250, R = 88, TH = 6;          // anneau : rayon médian, épaisseur
  const RIN = R - TH / 2, ROUT = R + TH / 2;
  const TILES = 72, TILE = Math.PI * 2 / TILES;      // 5°
  const FPS = 30, SUB = 8, DT = 1 / (FPS * SUB);
  function rng(seed) { let a = seed >>> 0; return function () { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  // table cos/sin des 72 orientations (calculée une fois)
  const COS = [], SIN = [];
  for (let k = 0; k < TILES; k++) { COS.push(Math.cos(k * TILE)); SIN.push(Math.sin(k * TILE)); }

  function create(seed, o) {
    o = Object.assign({ g: 420, grow: 0.4, r0: 5, gapTiles: 9, stepFrames: 3, dir: 1, speed: 220, vmin: 240 }, o || {});
    const Rn = rng(seed);
    const a = Rn() * Math.PI * 2;
    return {
      seed, o, frame: 0, step: 0,
      x: CX + (Rn() - 0.5) * 20, y: CY - 30 + (Rn() - 0.5) * 10,
      vx: Math.cos(a) * o.speed, vy: Math.sin(a) * o.speed * 0.5 - 40,
      r: o.r0, bounces: 0, escaped: false, escT: null, events: [], hits: [], // hits: [{tile, n, f}]
      gap0: Math.floor(Rn() * TILES),
    };
  }
  // index de la première tuile de la brèche au pas courant (rotation par paliers d'une tuile toutes stepFrames frames)
  function gapStart(s, frame) { return ((s.gap0 + s.o.dir * Math.floor(frame / s.o.stepFrames)) % TILES + TILES) % TILES; }
  // la direction (dx,dy) normalisée tombe-t-elle dans la brèche, avec la marge angulaire de la balle ?
  function tileOf(dx, dy) {
    // tuile = secteur angulaire, trouvé par produit scalaire max sur la table (sans atan2)
    let best = 0, bd = -2;
    for (let k = 0; k < TILES; k++) { const d = dx * COS[k] + dy * SIN[k]; if (d > bd) { bd = d; best = k; } }
    return best; // tuile dont le CENTRE angulaire est k·5° (secteur [k·5°-2.5°, k·5°+2.5°])
  }
  function inGap(s, frame, dx, dy) {
    const g0 = gapStart(s, frame), n = s.o.gapTiles;
    // centre de la brèche = tuile g0 + (n-1)/2 ; demi-largeur = n·2.5° ; marge = r/R rad
    const mid = g0 + (n - 1) / 2;
    const cm = Math.cos(mid * TILE), sm = Math.sin(mid * TILE);
    const half = n * TILE / 2 - s.r / R;
    return half > 0 && (dx * cm + dy * sm) > Math.cos(half);
  }
  function stepFrame(s) {
    for (let k = 0; k < SUB; k++) {
      const t = s.step * DT;
      s.vy += s.o.g * DT;
      s.x += s.vx * DT; s.y += s.vy * DT;
      s.step++;
      if (s.escaped) continue;
      const dx = s.x - CX, dy = s.y - CY, dist = Math.sqrt(dx * dx + dy * dy);
      const nx = dx / dist, ny = dy / dist;
      if (dist + s.r >= RIN) {
        if (inGap(s, s.frame, nx, ny)) {
          if (dist - s.r > ROUT) { s.escaped = true; s.escT = +(s.step * DT).toFixed(4); s.events.push({ t: s.escT, type: 'escape', n: s.bounces }); }
          continue;
        }
        const vn = s.vx * nx + s.vy * ny;
        if (vn > 0) {
          s.vx -= 2 * vn * nx; s.vy -= 2 * vn * ny;
          // petit élan tangentiel donné par l'anneau qui tourne + plancher de vitesse
          const sp = Math.sqrt(s.vx * s.vx + s.vy * s.vy);
          const want = Math.max(sp, s.o.vmin);
          s.vx *= want / sp; s.vy *= want / sp;
          s.bounces++;
          const tile = tileOf(nx, ny);
          s.hits.push({ tile, n: s.bounces, f: s.frame + 1 });
          s.events.push({ t: +(s.step * DT).toFixed(4), type: 'bounce', n: s.bounces, tile, v: +vn.toFixed(2), r: s.r });
          s.r = Math.min(26, s.r + s.o.grow);
        }
        // repositionnement à l'intérieur
        const lim = RIN - s.r - 0.01;
        if (dist > lim) { s.x = CX + nx * lim; s.y = CY + ny * lim; }
      }
    }
    s.frame++;
  }
  const api = { CX, CY, R, TH, RIN, ROUT, TILES, TILE, FPS, SUB, DT, COS, SIN, rng, create, stepFrame, gapStart, tileOf };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.Ring = api;
})(typeof window !== 'undefined' ? window : globalThis);
