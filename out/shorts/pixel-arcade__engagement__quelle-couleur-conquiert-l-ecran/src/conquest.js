/* conquest.js — guerre de territoire à 4 couleurs sur une grille de 111×154 cellules (2 px logiques chacune),
 * automate cellulaire synchrone déterministe, partagé entre la pré-simulation Node (simulate.cjs) et la page PixiJS.
 * Uniquement de l'arithmétique entière + PRNG mulberry32 (Math.imul) : aucune fonction transcendante,
 * donc bit-à-bit identique Node 22 / Chromium (leçon atan2 du short course de billes).
 * Règle par frame (30 fps), pour chaque cellule : on regarde UN voisin tiré au sort (4-voisinage) ;
 *  (2 sous-pas synchrones par frame)
 *  - cellule vide, voisin coloré : conquise (p = 1) ;
 *  - cellule ennemie : conquise avec p = 0.12 × force(attaquant)² / 9, force ∈ {1..5} retirée toutes les 24 frames.
 */
(function (root) {
  const GW = 111, GH = 154, CELL = 2, OX = 16, OY = 88;   // grille -> pixels logiques 270×480
  const N = GW * GH, FPS = 30, START_F = 72, END_F = 360, SURGE_EVERY = 24;
  const PE = 1.0, PA = 0.12, SUB = 2;
  function rng(seed) { let a = seed >>> 0; return function () { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function create(seed) {
    const R = rng(seed);
    const col = new Uint8Array(N), prev = new Uint8Array(N), born = new Int32Array(N).fill(-99);
    // ordre des coins (graine) : 1 ROSE, 2 VERTE, 3 JAUNE, 4 BLEUE
    const order = [1, 2, 3, 4]; for (let i = 3; i > 0; i--) { const j = Math.floor(R() * (i + 1)); [order[i], order[j]] = [order[j], order[i]]; }
    const corners = [[1, 1], [GW - 4, 1], [1, GH - 4], [GW - 4, GH - 4]];
    corners.forEach(([x, y], k) => { for (let j = 0; j < 3; j++) for (let i = 0; i < 3; i++) col[(y + j) * GW + x + i] = order[k]; });
    const s = { seed, R, col, prev, born, frame: 0, strength: [0, 3, 3, 3, 3], counts: [0, 0, 0, 0, 0], leader: 0, events: [], fullF: null, corners, order, history: [] };
    count(s); return s;
  }
  function count(s) { const c = [0, 0, 0, 0, 0]; for (let i = 0; i < N; i++) c[s.col[i]]++; s.counts = c; }
  function stepFrame(s) {
    const f = s.frame;
    if (f >= START_F && f < END_F) {
      const R = s.R;
      if ((f - START_F) % SURGE_EVERY === 0) {
        for (let c = 1; c <= 4; c++) { s.strength[c] = 1 + Math.floor(R() * 5); if (s.strength[c] === 5 && f > START_F) s.events.push({ t: +(f / FPS).toFixed(3), type: 'surge', c }); }
      }
      const prev = s.prev, col = s.col;
      for (let k = 0; k < SUB; k++) {
      prev.set(col);
      for (let y = 0; y < GH; y++) for (let x = 0; x < GW; x++) {
        const i = y * GW + x, d = (R() * 4) | 0, roll = R();
        const nx = x + (d === 0 ? 1 : d === 1 ? -1 : 0), ny = y + (d === 2 ? 1 : d === 3 ? -1 : 0);
        if (nx < 0 || ny < 0 || nx >= GW || ny >= GH) continue;
        const cn = prev[ny * GW + nx], ci = prev[i];
        if (cn === 0 || cn === ci) continue;
        if (ci === 0 ? roll < PE : roll < PA * s.strength[cn] * s.strength[cn] / 9) { col[i] = cn; s.born[i] = f + 1; }
      }
      }
      count(s);
      if (s.fullF === null && s.counts[0] === 0) { s.fullF = f + 1; s.events.push({ t: +((f + 1) / FPS).toFixed(3), type: 'full' }); }
      let L = 1; for (let c = 2; c <= 4; c++) if (s.counts[c] > s.counts[L]) L = c;
      if (L !== s.leader) { if (s.leader) s.events.push({ t: +((f + 1) / FPS).toFixed(3), type: 'lead', c: L }); s.leader = L; }
    }
    s.frame++;
    if (s.frame % 3 === 0) s.history.push(s.counts.slice(1));
  }
  const api = { GW, GH, CELL, OX, OY, N, FPS, START_F, END_F, rng, create, stepFrame };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.Conquest = api;
})(typeof window !== 'undefined' ? window : globalThis);
