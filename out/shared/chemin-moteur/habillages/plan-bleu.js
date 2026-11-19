// plan-bleu.js — habillage d'origine de « lyrics-chemin » : plan d'architecte bleu scotché sur un sol clair, encre ivoire,
// mot chanté en jaune, crayon rouge pour les annotations, tasse, crayon, clé et note posés. Extraction à l'identique de
// l'ancien chemin.js (contrôle : les images du short de preuve ressortent identiques).
// Dessins associés : bateau (mât en pointillé G.mat, suite de la première vague et filets d'eau G.mer).
import { S, W, H, rad, straight, wave, noiseTile, per, shadowed, rr, lin, strokePath } from '../outils.js';

export const COL = { paper: '#1B4C92', paperHi: '#2460AE', paperLo: '#133A74', ink: '#F3F0E4', wet: '#FFD84A', red: '#FF7D5C',
  floor: '#CFC8BA', floorLo: '#B9B1A2' };
const MONO = "'JetBrains Mono'";

let PAT;
function prepare() {
  PAT = {
    blotch: noiseTile(256, 3, (i, j) => { const v = per(i, j, 5, 256) * 0.6 + per(i, j, 11, 256) * 0.4; return v > 0.5 ? [255, (v - 0.5) * 2 * 26] : [0, (0.5 - v) * 2 * 34]; }),
    fibre: noiseTile(256, 7, (i, j, r) => { const v = r(); return v > 0.5 ? [255, (v - 0.5) * 30] : [0, (0.5 - v) * 36]; }),
    speck: noiseTile(256, 11, (i, j, r) => { const v = r(), b = per(i, j, 9, 256); return v > 0.93 ? [60, 70] : v < 0.08 ? [255, 60] : [b > 0.5 ? 255 : 0, Math.abs(b - 0.5) * 30]; }),
    grain: noiseTile(256, 19, (i, j, r) => { const v = r(); return [v > 0.5 ? 255 : 0, Math.abs(v - 0.5) * 22]; }),
    wood: noiseTile(64, 23, (i, j) => { const v = per(i, j * 0.15, 8, 64); return [v > 0.5 ? 255 : 60, Math.abs(v - 0.5) * 70]; }),
  };
}
const pat = (c, k) => c.createPattern(PAT[k], 'repeat');

// ---------- objets posés (les seules choses qui ont une épaisseur) ----------
function tape(c, cam, w, h, seed) {   // ruban de masquage translucide, bouts déchirés
  const r = S.rng(seed), edge = (x, sgn) => { const pts = []; for (let k = 0; k <= 8; k++) pts.push([x + sgn * (r() * 5 - 1), -h / 2 + h * k / 8]); return pts; };
  const L = edge(-w / 2, -1), Rr = edge(w / 2, 1).reverse();
  const shape = () => { c.beginPath(); L.forEach(([x, y], i) => i ? c.lineTo(x, y) : c.moveTo(x, y)); Rr.forEach(([x, y]) => c.lineTo(x, y)); c.closePath(); };
  shadowed(c, cam, () => { c.fillStyle = 'rgba(233,223,195,0.9)'; shape(); c.fill(); }, 4, 2, 3, 0.22);
  c.fillStyle = lin(c, 0, -h / 2, 0, h / 2, [[0, 'rgba(241,233,208,0.86)'], [0.5, 'rgba(232,222,193,0.80)'], [1, 'rgba(221,209,176,0.86)']]); shape(); c.fill();
  c.save(); shape(); c.clip(); c.globalAlpha = 0.5; c.fillStyle = pat(c, 'fibre'); c.fillRect(-w, -h, 2 * w, 2 * h); c.restore();
  c.strokeStyle = 'rgba(255,255,255,0.35)'; c.lineWidth = 1.2; c.beginPath(); c.moveTo(-w / 2 + 4, -h / 2 + 1.5); c.lineTo(w / 2 - 4, -h / 2 + 1.5); c.stroke();
}
function objects(c, cam, t, env) {
  const O = env.G.objets, SHEET = env.G.feuille;
  [[SHEET.x, SHEET.y, -45], [SHEET.x + SHEET.w, SHEET.y, 45], [SHEET.x, SHEET.y + SHEET.h, 45], [SHEET.x + SHEET.w, SHEET.y + SHEET.h, -45]].forEach(([tx, ty, r], i) => {
    c.save(); c.translate(tx, ty); c.rotate(rad(r + (i % 2 ? 3 : -2))); tape(c, cam, 124, 34, 31 + i); c.restore(); });
  if (O.tasse) {   // tasse vue de dessus : auréole sèche, bord éclairé, paroi intérieure, ménisque, reflet de fenêtre
    c.save(); c.translate(O.tasse.x, O.tasse.y);
    const rs = S.rng(41); for (let k = 0; k < 3; k++) { c.strokeStyle = `rgba(20,24,40,${0.10 + 0.05 * k})`; c.lineWidth = 2 + 3 * rs(); c.beginPath(); c.arc(-88 + rs() * 3, 118 + rs() * 3, 50 + k * 1.5, 0.3 + rs() * 0.4, 5.3 + rs() * 0.5); c.stroke(); }
    c.fillStyle = 'rgba(30,22,30,0.06)'; c.beginPath(); c.arc(-88, 118, 49, 0, 7); c.fill();
    shadowed(c, cam, () => { c.fillStyle = '#EDE8DC'; c.beginPath(); c.arc(0, 0, 56, 0, 7); c.fill(); rr(c, -80, -12, 32, 24, 10); c.fill(); }, 20, 12, 17, 0.45);
    c.fillStyle = lin(c, -80, -12, -80, 12, [[0, '#F6F2E8'], [0.5, '#E6E0D2'], [1, '#CFC8B8']]); rr(c, -80, -12, 32, 24, 10); c.fill();
    c.fillStyle = 'rgba(40,30,20,0.25)'; rr(c, -72, -5, 16, 10, 5); c.fill();
    c.fillStyle = lin(c, -50, -50, 50, 50, [[0, '#FBF8F0'], [0.6, '#E9E3D5'], [1, '#CEC6B4']]); c.beginPath(); c.arc(0, 0, 56, 0, 7); c.fill();
    c.fillStyle = lin(c, -40, -40, 40, 40, [[0, '#BDB5A3'], [0.5, '#DDD7C9'], [1, '#F2EEE4']]); c.beginPath(); c.arc(0, 0, 49, 0, 7); c.fill();
    const g = c.createRadialGradient(-10, -12, 4, 0, 0, 46); g.addColorStop(0, '#6A4528'); g.addColorStop(0.7, '#3A2413'); g.addColorStop(1, '#25160B');
    c.fillStyle = g; c.beginPath(); c.arc(0, 0, 45, 0, 7); c.fill();
    c.strokeStyle = 'rgba(176,128,80,0.55)'; c.lineWidth = 2.2; c.beginPath(); c.arc(0, 0, 44, 0, 7); c.stroke();   // ménisque
    c.fillStyle = 'rgba(205,160,110,0.18)'; for (let k = 0; k < 14; k++) { const a = rs() * 7, d = 28 + rs() * 14; c.beginPath(); c.arc(Math.cos(a) * d, Math.sin(a) * d, 1 + rs() * 2, 0, 7); c.fill(); }
    c.save(); c.beginPath(); c.arc(0, 0, 45, 0, 7); c.clip(); c.rotate(-0.6); c.fillStyle = 'rgba(255,255,255,0.16)'; rr(c, -8, -38, 26, 14, 4); c.fill(); rr(c, 22, -38, 12, 14, 4); c.fill(); c.restore();
    c.strokeStyle = 'rgba(255,255,255,0.55)'; c.lineWidth = 2; c.beginPath(); c.arc(0, 0, 54, 3.4, 4.6); c.stroke();
    c.restore();
  }
  if (O.crayon) {   // crayon : trois facettes, cône de bois veiné, mine, virole cannelée, gomme
    c.save(); c.translate(O.crayon.x, O.crayon.y); c.rotate(rad(O.crayon.angle));
    const body = () => { c.beginPath(); c.moveTo(-122, -8); c.lineTo(84, -8); c.lineTo(118, 0); c.lineTo(84, 8); c.lineTo(-122, 8); c.closePath(); c.fill(); };
    shadowed(c, cam, () => { c.fillStyle = '#F2C230'; body(); }, 9, 6, 9, 0.45);
    c.fillStyle = '#FFDE6E'; c.fillRect(-98, -8, 182, 5.3); c.fillStyle = '#F2C230'; c.fillRect(-98, -2.7, 182, 5.4); c.fillStyle = '#C9921A'; c.fillRect(-98, 2.7, 182, 5.3);
    c.fillStyle = 'rgba(255,255,255,0.35)'; c.fillRect(-98, -6.6, 182, 1.2);
    c.save(); c.beginPath(); c.moveTo(84, -8); c.lineTo(118, 0); c.lineTo(84, 8); c.closePath(); c.clip();
    c.fillStyle = lin(c, 0, -8, 0, 8, [[0, '#F1DDBA'], [0.5, '#E2C79C'], [1, '#C7A676']]); c.fillRect(82, -9, 40, 18);
    c.strokeStyle = 'rgba(150,105,60,0.45)'; c.lineWidth = 0.9; [-4, 0, 4].forEach(y => { c.beginPath(); c.moveTo(84, y); c.quadraticCurveTo(98, y * 0.6, 112, y * 0.2); c.stroke(); });
    c.restore();
    c.fillStyle = '#2B2B2B'; c.beginPath(); c.moveTo(106, -2.8); c.lineTo(118, 0); c.lineTo(106, 2.8); c.closePath(); c.fill();
    c.fillStyle = 'rgba(255,255,255,0.35)'; c.beginPath(); c.moveTo(108, -1.6); c.lineTo(116, -0.3); c.lineTo(108, -0.6); c.fill();
    c.fillStyle = lin(c, 0, -8, 0, 8, [[0, '#E2E6EC'], [0.45, '#AEB4BE'], [1, '#7D838D']]); c.fillRect(-108, -8.5, 12, 17);
    c.strokeStyle = 'rgba(60,64,72,0.5)'; c.lineWidth = 0.8; [-105, -102, -99].forEach(x => { c.beginPath(); c.moveTo(x, -8.5); c.lineTo(x, 8.5); c.stroke(); });
    c.fillStyle = lin(c, 0, -8, 0, 8, [[0, '#F7A797'], [1, '#D9705E']]); rr(c, -122, -8, 16, 16, 4); c.fill();
    c.restore();
  }
  if (O.cle) {   // clé en laiton : dégradé, biseau, dents
    c.save(); c.translate(O.cle.x, O.cle.y); c.rotate(rad(O.cle.angle));
    const key = () => { c.beginPath(); c.arc(-34, 0, 21, 0, 7); c.rect(-16, -5, 76, 10); c.moveTo(34, 4); c.lineTo(42, 4); c.lineTo(42, 15); c.lineTo(38, 17); c.lineTo(34, 15); c.closePath();
      c.moveTo(47, 4); c.lineTo(56, 4); c.lineTo(56, 12); c.lineTo(51, 14); c.lineTo(47, 12); c.closePath(); c.fill('nonzero'); };
    shadowed(c, cam, () => { c.fillStyle = '#C9A24A'; key(); }, 7, 5, 7, 0.5);
    c.fillStyle = lin(c, -50, -20, 50, 20, [[0, '#E9CC7E'], [0.45, '#C9A24A'], [1, '#9C7A2E']]); key();
    c.strokeStyle = 'rgba(255,240,190,0.7)'; c.lineWidth = 1.6; c.beginPath(); c.arc(-34, 0, 18, 3.6, 5.4); c.stroke(); c.beginPath(); c.moveTo(-14, -3.4); c.lineTo(58, -3.4); c.stroke();
    c.strokeStyle = 'rgba(90,64,20,0.5)'; c.lineWidth = 1.2; c.beginPath(); c.arc(-34, 0, 13, 0.4, 2.6); c.stroke();
    c.fillStyle = COL.paper; c.beginPath(); c.arc(-40, 0, 8, 0, 7); c.fill();
    c.fillStyle = 'rgba(4,14,40,0.35)'; c.beginPath(); c.arc(-39, 1.5, 8, 0, 7); c.fill();
    c.restore();
  }
  if (O.note) {   // note collée : coin relevé, trois traits au stylo, ruban
    c.save(); c.translate(O.note.x, O.note.y); c.rotate(rad(O.note.angle));
    const sq = () => { c.beginPath(); c.moveTo(-56, -56); c.lineTo(56, -56); c.lineTo(56, 34); c.quadraticCurveTo(50, 50, 32, 56); c.lineTo(-56, 56); c.closePath(); };
    shadowed(c, cam, () => { c.fillStyle = '#F4E6A6'; sq(); c.fill(); }, 12, 7, 11, 0.4);
    shadowed(c, cam, () => { c.fillStyle = 'rgba(0,0,0,0)'; c.beginPath(); c.moveTo(56, 30); c.quadraticCurveTo(52, 52, 28, 56); c.lineTo(40, 40); c.closePath(); c.fillStyle = '#E9D88F'; c.fill(); }, 16, 10, 14, 0.35);
    c.fillStyle = lin(c, -56, -56, 56, 56, [[0, '#FAF0BE'], [0.75, '#EEDD96'], [1, '#D9C67A']]); sq(); c.fill();
    c.fillStyle = lin(c, 56, 30, 30, 56, [[0, '#FFF6CF'], [1, '#E2CF84']]); c.beginPath(); c.moveTo(56, 34); c.quadraticCurveTo(46, 40, 32, 56); c.quadraticCurveTo(50, 50, 56, 34); c.fill();
    c.strokeStyle = 'rgba(40,50,80,0.6)'; c.lineWidth = 3.4; c.lineCap = 'round';
    [[-38, -22, 34], [-38, 0, 44], [-38, 22, 16]].forEach(([x, y, w]) => { c.beginPath(); c.moveTo(x, y); c.quadraticCurveTo(x + w * 0.5, y - 3, x + w + 26, y - 1); c.stroke(); });
    c.save(); c.translate(0, -56); c.rotate(rad(-4)); tape(c, cam, 62, 22, 57); c.restore();
    c.restore();
  }
}

// ---------- sol et feuille ----------
function floor(c) {
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.fillStyle = COL.floor; c.fillRect(0, 0, W, H); c.restore();
  c.save(); c.fillStyle = pat(c, 'speck'); c.scale(1.5, 1.5); c.fillRect(-2000, -2000, 5000, 5000); c.restore();
}
function sheet(c, cam, t, env) {
  const { x, y, w, h } = env.G.feuille, px = 1 / cam.s;   // px = un pixel écran, en unités monde
  shadowed(c, cam, () => { c.fillStyle = COL.paper; c.fillRect(x, y, w, h); }, 26, 12, 18, 0.45);
  c.fillStyle = lin(c, x, y, x + w, y + h, [[0, COL.paperHi], [0.55, COL.paper], [1, COL.paperLo]]); c.fillRect(x, y, w, h);
  c.save(); c.beginPath(); c.rect(x, y, w, h); c.clip();
  // facettes : chaque panneau plié prend la lumière un peu différemment (cassure de lumière, sans bande)
  const cols = [x, 540, x + w], rows = [0, 1, 2, 3, 4].map(k => y + h * k / 4);
  for (let i = 0; i < 2; i++) for (let j = 0; j < 4; j++) { const v = ((i + j) % 2 ? 1 : -1) * (0.022 + 0.008 * ((i * 3 + j) % 3));
    c.fillStyle = v > 0 ? `rgba(255,255,255,${v})` : `rgba(0,8,30,${-v})`; c.fillRect(cols[i], rows[j], cols[i + 1] - cols[i], rows[j + 1] - rows[j]); }
  c.save(); c.scale(4, 4); c.fillStyle = pat(c, 'blotch'); c.fillRect(0, 0, 300, 480); c.restore();
  c.save(); c.scale(0.75, 0.75); c.fillStyle = pat(c, 'fibre'); c.fillRect(0, 0, 1500, 2500); c.restore();
  // quadrillage : 1 px écran
  const aMin = 0.035 + 0.035 * S.clamp((cam.s - 1) / 2);
  c.lineWidth = Math.max(px, 0.5); c.strokeStyle = `rgba(255,255,255,${aMin})`; c.beginPath();
  for (let gx = 40; gx < x + w; gx += 20) if (gx % 100) { c.moveTo(gx, y); c.lineTo(gx, y + h); }
  for (let gy = 100; gy < y + h; gy += 20) if (gy % 100) { c.moveTo(x, gy); c.lineTo(x + w, gy); } c.stroke();
  c.lineWidth = Math.max(1.4 * px, 0.8); c.strokeStyle = 'rgba(255,255,255,0.10)'; c.beginPath();
  for (let gx = 100; gx < x + w; gx += 100) { c.moveTo(gx, y); c.lineTo(gx, y + h); }
  for (let gy = 100; gy < y + h; gy += 100) { c.moveTo(x, gy); c.lineTo(x + w, gy); } c.stroke();
  // plis : largeur constante à l'écran (≈ 10 px de halo, arête nette de 1,5 px claire / 1,5 px sombre)
  const hw = Math.min(14, 10 * px), e = Math.max(1.5 * px, 0.6);
  const crease = (x0, y0, x1, y1) => { const vert = x0 === x1;
    const gg = vert ? c.createLinearGradient(x0 - hw, 0, x0 + hw, 0) : c.createLinearGradient(0, y0 - hw, 0, y0 + hw);
    gg.addColorStop(0, 'rgba(255,255,255,0)'); gg.addColorStop(0.5, 'rgba(255,255,255,0.07)'); gg.addColorStop(0.5, 'rgba(0,10,40,0.08)'); gg.addColorStop(1, 'rgba(0,10,40,0)');
    c.fillStyle = gg; vert ? c.fillRect(x0 - hw, y0, 2 * hw, y1 - y0) : c.fillRect(x0, y0 - hw, x1 - x0, 2 * hw);
    c.fillStyle = 'rgba(255,255,255,0.20)'; vert ? c.fillRect(x0 - e, y0, e, y1 - y0) : c.fillRect(x0, y0 - e, x1 - x0, e);
    c.fillStyle = 'rgba(0,10,40,0.22)'; vert ? c.fillRect(x0, y0, e, y1 - y0) : c.fillRect(x0, y0, x1 - x0, e); };
  crease(540, y, 540, y + h); [1, 2, 3].forEach(k => crease(x, y + h * k / 4, x + w, y + h * k / 4));
  c.strokeStyle = 'rgba(243,240,228,0.42)'; c.lineWidth = 2; c.strokeRect(x + 22, y + 22, w - 44, h - 44);
  c.fillStyle = 'rgba(243,240,228,0.55)'; c.font = `400 15px ${MONO}`; c.textAlign = 'left'; c.textBaseline = 'alphabetic'; c.fillText('PL. 01 — 1:1', x + 36, y + 52);
  c.restore();
}

// ---------- sous le dessin : repères d'architecte autour du titre (dès l'image 0), mât en pointillé ----------
function under(c, cam, t, env) {
  const TITLE = env.TITLE;
  if (TITLE) {
    const a = TITLE.path.at(TITLE.d0), b = TITLE.path.at(TITLE.d0 + TITLE.total), em = TITLE.emW, px = 1 / cam.s;
    const k = S.seg(t, -0.25, 0.55, S.ease.outCubic), mid = (a.x + b.x) / 2, yd = a.y - em * 1.22;
    c.save(); c.strokeStyle = 'rgba(243,240,228,0.5)'; c.fillStyle = 'rgba(243,240,228,0.55)'; c.lineWidth = Math.max(1.6 * px, 0.7);
    const half = (b.x - a.x) / 2 * k;
    c.beginPath(); c.moveTo(mid - half, yd); c.lineTo(mid + half, yd); c.stroke();   // cote
    if (k > 0.98) { [a.x, b.x].forEach(xx => { c.beginPath(); c.moveTo(xx, yd - 7); c.lineTo(xx, yd + 7); c.moveTo(xx - 5, yd + 5); c.lineTo(xx + 5, yd - 5); c.stroke(); }); }
    c.font = `400 ${11}px ${MONO}`; c.textAlign = 'center'; c.globalAlpha = S.seg(t, 0.2, 0.6);
    c.save(); c.fillStyle = COL.paper; c.fillRect(mid - 20, yd - 7, 40, 13); c.restore(); c.fillText(String(Math.round(b.x - a.x)), mid, yd + 4);
    c.globalAlpha = 1;
    [[a.x - 18, a.y + 4], [b.x + 18, a.y + 4]].forEach(([xx, yy]) => { c.beginPath(); c.moveTo(xx - 6, yy); c.lineTo(xx + 6, yy); c.moveTo(xx, yy - 6); c.lineTo(xx, yy + 6); c.stroke(); });   // croix de repère
    c.setLineDash([5, 6]); c.strokeStyle = 'rgba(243,240,228,0.32)';   // ligne de construction sous le titre, tirée par la pointe
    const tip = env.tipOf(TITLE, t), gx = tip ? Math.max(a.x + (b.x - a.x) * S.seg(t, -0.2, 0.0), TITLE.path.at(tip.d).x + 0.3 * em) : a.x;
    c.beginPath(); c.moveTo(a.x - 30, a.y + 9); c.lineTo(Math.min(b.x + 30, gx), a.y + 9); c.stroke(); c.setLineDash([]);
    c.restore();
  }
  const G = env.G;
  if (G.mat) {   // mât en pointillé : se trace pendant l'arrivée sur la ligne indiquée
    const mast = straight(env.pt(G.mat.a), env.pt(G.mat.b)), Lm = env.LINES.find(L => L.id === G.mat.pendant);
    const km = Lm ? S.seg(t, Lm.arr - Lm.dur, Lm.arr, S.ease.inOutCubic) : 1;
    strokePath(c, mast, 0, mast.len * km, 2.2, 'rgba(243,240,228,0.7)', [9, 9]);
  }
}

// pointe : point d'encre jaune lumineux pendant l'écriture (et sur le titre à l'image 0)
function tip(c, L, tp, cam, t, env) {
  if (!(tp.writing || (L === env.TITLE && t < 0.3))) return;
  const p = L.path.at(tp.d), r = L.emW * 0.11;
  c.save(); c.shadowColor = COL.wet; c.shadowBlur = 16 * cam.s; c.fillStyle = COL.wet; c.beginPath(); c.arc(p.x, p.y + (L.noLine ? 9 : 0), r, 0, 7); c.fill(); c.restore();
}

// après l'encre : suite de la première vague et filets d'eau, tracés pendant le zoom arrière
function afterInk(c, cam, t, env) {
  const M = env.G.mer, SEA = env.SEA, T_OUT0 = env.T_OUT0;
  const V = env.LINES.find(L => L.id === 'vague1'), t0 = SEA.length ? SEA[0].t0 : T_OUT0, kw = S.seg(t, t0, t0 + 1.4, S.ease.inOutCubic);
  if (kw > 0 && V && M && M.suiteVague1) { const ch = V.chemin, w2 = wave(M.suiteVague1.x0, M.suiteVague1.x1, ch.y, ch.amp, ch.wl, ch.ph + (M.suiteVague1.x0 - ch.x0) / ch.wl * 2 * Math.PI);
    strokePath(c, w2, 0, w2.len * kw, 3.2, COL.ink);
    (M.filets || []).forEach(([y, x0, x1, ph], i) => { const w3 = wave(x0, x1, y, 10, 300, ph), k3 = S.seg(t, T_OUT0 + 0.685 + i * 0.35, T_OUT0 + 2.085 + i * 0.35, S.ease.inOutCubic);
      c.globalAlpha = 0.55; strokePath(c, w3, 0, w3.len * k3, 2.6, COL.ink); c.globalAlpha = 1; }); }
}

// finition écran : vignette douce + grain fixe
function finish(c) {
  const v = c.createRadialGradient(W / 2, H * 0.47, H * 0.28, W / 2, H * 0.5, H * 0.74); v.addColorStop(0, 'rgba(3,10,30,0)'); v.addColorStop(1, 'rgba(3,10,30,0.34)');
  c.fillStyle = v; c.fillRect(0, 0, W, H);
  c.fillStyle = pat(c, 'grain'); c.fillRect(0, 0, W, H);
}

export const habillage = {
  id: 'plan-bleu',
  fonts: [{ family: 'Barlow Condensed', weight: 700, pkg: 'barlow-condensed' }, { family: 'Barlow Condensed', weight: 800, pkg: 'barlow-condensed' },
    { family: 'JetBrains Mono', weight: 400, pkg: 'jetbrains-mono' }],
  font: 'Barlow Condensed', weight: 700, wFinal: 800,
  cap: 0.70, gap: 0.16, belowY: 0.88, liftAbove: 0.50, liftBelow: 0.52,   // hauteur de capitale, écart au trait (au-dessus), ligne de base sous le trait, centre du texte pour la caméra
  em: [36, 54], trackMax: 0.15, floorPx: 120, floorFast: 92, maxPx: 220, dryCloseAlpha: 0.6,
  col: { fresh: COL.wet, dry: COL.ink, stroke: COL.ink, annot: COL.red },
  ghost: { mode: 'wipe', alpha: 0.5 },   // pré-posé au crayon : encre sèche à 50 %, révélée de gauche à droite
  prepare, floor, sheet, under, tip, afterInk, objects, finish,
};
