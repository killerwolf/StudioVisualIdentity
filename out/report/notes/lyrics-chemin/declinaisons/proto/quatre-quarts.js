// A2 — « Le quatre-quarts » (recette) : habillage « ardoise » (craie sur ardoise de bistrot) + dessin « quatre-quarts »
// (un gâteau rond vu de dessus, coupé en quatre parts égales : le dessin EST la recette). Maquette d'images fixes.
import { S, W, H, rad, noiseTile, shadowed, rr, finish } from './core.js';

const SHEET = { x: 36, y: 96, w: 1008, h: 1704 }, FR = 30;   // cadre en chêne de 30 px
const CC = [512, 930], R = 390, k = R * Math.SQRT1_2;
const C = { slate: '#2C3836', slateHi: '#364643', slateLo: '#222C2B', craie: '#F1EEE6', beurre: '#FFD766', rose: '#F29A85', chene: '#C39A62', marbre: '#E7E3DC' };

export const G = {
  id: 'quatre-quarts', feuille: SHEET,
  points: { C: CC, TL: [CC[0] - k, CC[1] - k], TR: [CC[0] + k, CC[1] - k], BL: [CC[0] - k, CC[1] + k], BR: [CC[0] + k, CC[1] + k] },
  aretes: {
    titre: { chemin: { type: 'droite', a: [192, 400], b: [832, 400] }, em: [92, 112], center: true, noLine: true, weight: 800, track: 0.02 },
    coupe1a: { chemin: { type: 'droite', a: 'TL', b: 'C' }, m: [34, 62] },
    coupe1b: { chemin: { type: 'droite', a: 'C', b: 'BR' }, m: [62, 34] },
    oeufs:  { chemin: { type: 'droite', a: [352, 712], b: [672, 712] }, em: [84, 84], center: true, noLine: true, noFit: true, weight: 800 },
    sucre:  { chemin: { type: 'droite', a: [618, 960], b: [878, 960] }, em: [84, 84], center: true, noLine: true, noFit: true, weight: 800 },
    farine: { chemin: { type: 'droite', a: [372, 1146], b: [652, 1146] }, em: [84, 84], center: true, noLine: true, noFit: true, weight: 800 },
    beurre: { chemin: { type: 'droite', a: [140, 960], b: [410, 960] }, em: [84, 84], center: true, noLine: true, noFit: true, weight: 800 },
    coupe2a: { chemin: { type: 'droite', a: 'BL', b: 'C' }, m: [34, 62] },
    coupe2b: { chemin: { type: 'droite', a: 'C', b: 'TR' }, m: [62, 34] },
  },
  moule: { c: CC, r: R, r2: R + 17, t: [18.9, 20.8] },
  final: { cx: 512, largeurMax: 780, emMax: 100, espace: 0.27, rangs: [{ y: 1452 }, { y: 1562 }] },
  objets: { fouet: { x: 1022, y: 196, angle: 173 }, oeufs: [[150, 238, -20], [236, 204, 14]], cuillere: { x: 96, y: 1722, angle: -17 }, beurre: { x: 902, y: 1682, angle: 9 } },
};
// Temps ESTIMÉS (voix non générée) : à recaler sur les mots horodatés de la vraie narration.
export const D = {
  titre: 'QUATRE-QUARTS', langue: 'fr', duree: 30.0, zoomArriere: [19.0, 20.8],
  lignes: [
    { arete: 'titre', u: [['QUATRE-QUARTS', 0.15, 1.3]], cad: [[0]], arr: 0, maxPx: 250 },
    { arete: 'coupe1a', u: [['QUATRE', 3.3, 3.8], ['INGRÉDIENTS', 3.8, 4.4]], cad: [[0, 1]], arr: 2.9 },
    { arete: 'coupe1b', u: [['À PARTS', 4.5, 4.9], ['ÉGALES', 4.9, 5.5]], cad: [[0, 1]], arr: 4.45 },
    { arete: 'oeufs', u: [['3 ŒUFS', 6.5, 7.3]], cad: [[0]], arr: 6.1 },
    { arete: 'sucre', u: [['SUCRE', 9.9, 10.5]], cad: [[0]], arr: 9.2, maxPx: 200 },
    { arete: 'farine', u: [['FARINE', 10.9, 11.5]], cad: [[0]], arr: 10.75 },
    { arete: 'beurre', u: [['BEURRE', 12.1, 12.7]], cad: [[0]], arr: 11.9 },
    { arete: 'coupe2a', u: [['ŒUFS', 14.6, 15.0], ['+ SUCRE', 15.2, 15.8]], cad: [[0, 1]], arr: 14.0 },
    { arete: 'coupe2b', u: [['+ FARINE', 16.6, 17.2], ['+ BEURRE', 17.6, 18.3]], cad: [[0, 1]], arr: 16.3 },
  ],
  final: { u: [['45 MINUTES', 21.2, 22.4], ['À 180 °C', 22.6, 24.4]], rangs: [[0], [1]] },
  annotation: { type: 'souligne', arete: 'titre', t: 25.2, d: 0.6 },
};

const PAT = {};
function prepare() {
  PAT.dust = noiseTile(256, 21, (i, j) => { const n = S.noise2(i / 60, j / 60) * 0.6 + S.noise2(i / 17, j / 26) * 0.4; return [255, S.clamp((n - 0.45) * 2.2) * 34]; });
  PAT.streak = noiseTile(256, 22, (i, j) => { const n = S.noise2(i / 90, j / 4) * 0.7 + S.noise2(i / 30, j / 2) * 0.3; return [255, S.clamp((n - 0.5) * 2.4) * 20]; });
  PAT.speck = noiseTile(256, 23, (i, j, r) => { const v = r(); return [255, v > 0.985 ? 70 : 0]; });
  PAT.erode = noiseTile(256, 24, (i, j, r) => { const n = S.noise2(i / 3.1, j / 3.1) * 0.55 + r() * 0.45; return [0, n > 0.63 ? 150 : n > 0.56 ? 60 : 0]; });
  PAT.wood = noiseTile(256, 25, (i, j) => { const n = S.noise2(i / 120, j / 3) * 0.6 + S.noise2(i / 40, j / 1.4) * 0.4; return [70, S.clamp((n - 0.35) * 1.8) * 70, 40, 10]; });
  PAT.marble = noiseTile(256, 26, (i, j) => { const n = S.noise2(i / 70, j / 70) * 0.7 + S.noise2(i / 20, j / 20) * 0.3; return [120, S.clamp((n - 0.5) * 2) * 50]; });
}
const pat = (c, kx) => c.createPattern(PAT[kx], 'repeat');
function floor(c) { c.fillStyle = C.marbre; c.fillRect(0, 0, W, H); }
function sheet(c, cam) {
  const { x, y, w, h } = SHEET;
  c.fillStyle = C.marbre; c.fillRect(-400, -400, W + 800, H + 800); c.save(); c.scale(4, 4); c.fillStyle = pat(c, 'marble'); c.fillRect(-100, -100, 500, 700); c.restore();
  c.strokeStyle = 'rgba(120,125,130,0.25)'; c.lineWidth = 2.5; for (const [a, b, d, e, f, g] of [[-50, 300, 30, 700, 20, 1100], [1060, 0, 1090, 500, 1050, 900], [1040, 1100, 1100, 1500, 1060, 2000], [-20, 1300, 40, 1600, 0, 1950]]) { c.beginPath(); c.moveTo(a, b); c.quadraticCurveTo(d, e, f, g); c.stroke(); }
  // cadre en chêne
  shadowed(c, cam, () => { c.fillStyle = C.chene; rr(c, x, y, w, h, 10); c.fill(); }, 26, 12, 18, 0.42, '40,30,20');
  let g = c.createLinearGradient(x, y, x + w, y + h); g.addColorStop(0, '#D2AC74'); g.addColorStop(1, '#B58A52'); c.fillStyle = g; rr(c, x, y, w, h, 10); c.fill();
  c.save(); rr(c, x, y, w, h, 10); c.clip(); c.save(); c.scale(2, 2); c.globalAlpha = 0.6; c.fillStyle = pat(c, 'wood'); c.fillRect(0, 0, 600, 1000); c.restore();
  c.strokeStyle = 'rgba(90,60,25,0.45)'; c.lineWidth = 1.2; for (const [a, b, d, e] of [[x, y, x + FR, y + FR], [x + w, y, x + w - FR, y + FR], [x, y + h, x + FR, y + h - FR], [x + w, y + h, x + w - FR, y + h - FR]]) { c.beginPath(); c.moveTo(a, b); c.lineTo(d, e); c.stroke(); } c.restore();
  // ardoise
  const sx = x + FR, sy = y + FR, sw = w - 2 * FR, sh = h - 2 * FR;
  g = c.createLinearGradient(sx, sy, sx + sw, sy + sh); g.addColorStop(0, C.slateHi); g.addColorStop(0.5, C.slate); g.addColorStop(1, C.slateLo); c.fillStyle = g; c.fillRect(sx, sy, sw, sh);
  c.save(); c.beginPath(); c.rect(sx, sy, sw, sh); c.clip();
  { const r = S.rng(31); for (let i = 0; i < 46; i++) { const bx = sx + r() * sw, by = sy + r() * sh, br = 90 + r() * 240, a = 0.025 + r() * 0.045; c.save(); c.translate(bx, by); c.rotate(rad(-14)); c.scale(1.9, 0.75);
      const bg = c.createRadialGradient(0, 0, 0, 0, 0, br); bg.addColorStop(0, `rgba(235,240,236,${a})`); bg.addColorStop(1, 'rgba(235,240,236,0)'); c.fillStyle = bg; c.beginPath(); c.arc(0, 0, br, 0, 7); c.fill(); c.restore(); } }
  c.save(); c.translate(540, 900); c.rotate(rad(-14)); c.scale(3, 3); c.globalAlpha = 0.45; c.fillStyle = pat(c, 'streak'); c.fillRect(-300, -400, 600, 800); c.restore();
  c.save(); c.scale(1.2, 1.2); c.fillStyle = pat(c, 'speck'); c.fillRect(0, 0, 900, 1600); c.restore();
  // ombre intérieure du cadre
  for (const [a, b, d, e] of [[sx, 0, sx + 26, 0], [0, sy, 0, sy + 30]]) { const e2 = c.createLinearGradient(a, b, d, e); e2.addColorStop(0, 'rgba(0,0,0,0.42)'); e2.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = e2; c.fillRect(sx, sy, sw, sh); }
  c.restore();
}
function stroke(c, L, d0, d1, cam, t) { const p0 = L.path.at(0), p1 = L.path.at(L.path.len); const a = L.id.endsWith('a') ? 0 : 0;   // les deux demi-coupes forment un seul trait de bord à bord
  c.save(); c.strokeStyle = C.craie; c.lineWidth = 3.6; c.lineCap = 'round'; c.beginPath(); const s = L.path.at(d0), e = L.path.at(d1); c.moveTo(s.x, s.y); c.lineTo(e.x, e.y); c.stroke(); c.restore(); }
function inkExtras(c, cam, t, env) {
  const M = G.moule, kk = S.clamp((t - M.t[0]) / (M.t[1] - M.t[0])); if (kk > 0) { const e = S.ease.inOutSine(kk) * Math.PI * 2;
    c.strokeStyle = C.craie; c.lineCap = 'round'; c.lineWidth = 3.6; c.beginPath(); c.arc(M.c[0], M.c[1], M.r, -Math.PI / 2, -Math.PI / 2 + e); c.stroke();
    c.lineWidth = 2.6; c.beginPath(); for (let i = 0; i <= 90 * kk; i++) { const a0 = -Math.PI / 2 + i * Math.PI / 45, a1 = a0 + Math.PI / 45, am = (a0 + a1) / 2; if (i === 0) c.moveTo(M.c[0] + M.r2 * Math.cos(a0), M.c[1] + M.r2 * Math.sin(a0));
      c.quadraticCurveTo(M.c[0] + (M.r2 + 9) * Math.cos(am), M.c[1] + (M.r2 + 9) * Math.sin(am), M.c[0] + M.r2 * Math.cos(a1), M.c[1] + M.r2 * Math.sin(a1)); } c.stroke(); }
  const A = env.D.annotation; if (t > A.t) { const L = env.lineOf('titre'), kk2 = S.clamp((t - A.t) / A.d), x0 = L.path.at(L.d0).x, x1 = x0 + L.total;
    c.strokeStyle = C.rose; c.lineWidth = 5; c.lineCap = 'round'; for (let i = 0; i < 2; i++) { const kx = S.clamp(kk2 * 2 - i); if (kx <= 0) continue; c.beginPath(); c.moveTo(x0 + 10, 428 + i * 14); c.quadraticCurveTo((x0 + x1) / 2, 420 + i * 14, x0 + 10 + (x1 - x0 - 20) * kx, 430 + i * 14 - 4 * kx); c.stroke(); } }
}
function textErode(c) { c.save(); c.scale(0.9, 0.9); c.fillStyle = c.createPattern(PAT.erode, 'repeat'); c.fillRect(-200, -200, 1700, 2600); c.restore(); }
function objects(c, cam, t, env) {
  const O = G.objets; let g;
  for (const tp of env.tips) craie(c, cam, tp);
  // fouet
  c.save(); c.translate(O.fouet.x, O.fouet.y); c.rotate(rad(O.fouet.angle));
  c.lineCap = 'round'; for (const hw of [50, 34, 17, 0.01]) for (const sgn of hw > 1 ? [-1, 1] : [1]) { shadowed(c, cam, () => { c.strokeStyle = '#C9CFD2'; c.lineWidth = 3.2; c.beginPath(); c.moveTo(150, 0); c.bezierCurveTo(215, sgn * hw * 0.9, 300, sgn * hw * 1.25, 346, sgn * hw * 0.35); c.quadraticCurveTo(356, 0, 346, -sgn * hw * 0.0); c.stroke(); }, 5, 5, 8, 0.4, '0,0,0'); }
  c.strokeStyle = '#EEF1F2'; c.lineWidth = 1; for (const hw of [50, 34, 17]) for (const sgn of [-1, 1]) { c.beginPath(); c.moveTo(152, -1); c.bezierCurveTo(215, sgn * hw * 0.9 - 1, 300, sgn * hw * 1.25 - 1, 345, sgn * hw * 0.35 - 1); c.stroke(); }
  shadowed(c, cam, () => { c.fillStyle = '#B88A55'; rr(c, 0, -13, 150, 26, 12); c.fill(); }, 10, 7, 10, 0.45, '0,0,0');
  g = c.createLinearGradient(0, -13, 0, 13); g.addColorStop(0, '#D9B27C'); g.addColorStop(0.5, '#BF915A'); g.addColorStop(1, '#94683A'); c.fillStyle = g; rr(c, 0, -13, 150, 26, 12); c.fill();
  g = c.createLinearGradient(0, -10, 0, 10); g.addColorStop(0, '#F1F3F4'); g.addColorStop(1, '#9AA2A6'); c.fillStyle = g; rr(c, 138, -10, 22, 20, 4); c.fill(); c.restore();
  // œufs
  for (const [ex, ey, ea] of O.oeufs) { c.save(); c.translate(ex, ey); c.rotate(rad(ea)); const egg = () => { c.beginPath(); c.moveTo(0, -46); c.bezierCurveTo(30, -46, 37, 6, 37, 14); c.bezierCurveTo(37, 34, 20, 44, 0, 44); c.bezierCurveTo(-20, 44, -37, 34, -37, 14); c.bezierCurveTo(-37, 6, -30, -46, 0, -46); };
    shadowed(c, cam, () => { c.fillStyle = '#D9BE98'; egg(); c.fill(); }, 12, 8, 12, 0.5, '0,0,0'); g = c.createRadialGradient(-10, -14, 4, 0, 4, 52); g.addColorStop(0, '#FBEBD3'); g.addColorStop(0.6, '#E8CFA9'); g.addColorStop(1, '#C8A77C'); c.fillStyle = g; egg(); c.fill();
    c.fillStyle = 'rgba(255,255,255,0.55)'; c.beginPath(); c.ellipse(-11, -20, 6, 10, -0.4, 0, 7); c.fill(); c.restore(); }
  // cuillère en bois
  c.save(); c.translate(O.cuillere.x, O.cuillere.y); c.rotate(rad(O.cuillere.angle)); const spoon = () => { c.beginPath(); c.ellipse(52, 0, 58, 40, 0, 0, 7); rr(c, 96, -11, 290, 22, 11); };
  shadowed(c, cam, () => { c.fillStyle = '#B98B58'; spoon(); c.fill(); }, 12, 8, 12, 0.5, '0,0,0'); g = c.createLinearGradient(0, -40, 0, 40); g.addColorStop(0, '#DDB583'); g.addColorStop(1, '#A77A48'); c.fillStyle = g; spoon(); c.fill();
  g = c.createRadialGradient(46, 6, 4, 52, 0, 50); g.addColorStop(0, '#A87B4B'); g.addColorStop(1, '#CDA26F'); c.fillStyle = g; c.beginPath(); c.ellipse(52, 0, 46, 30, 0, 0, 7); c.fill(); c.restore();
  // beurre sur son papier
  c.save(); c.translate(O.beurre.x, O.beurre.y); c.rotate(rad(O.beurre.angle));
  shadowed(c, cam, () => { c.fillStyle = '#EFE9DA'; c.beginPath(); c.moveTo(-92, -70); c.lineTo(88, -78); c.lineTo(96, 66); c.lineTo(-84, 74); c.closePath(); c.fill(); }, 8, 5, 8, 0.4, '0,0,0');
  c.strokeStyle = 'rgba(160,150,130,0.5)'; c.lineWidth = 1; c.beginPath(); c.moveTo(-60, -70); c.lineTo(-52, 72); c.moveTo(60, -76); c.lineTo(66, 68); c.stroke();
  shadowed(c, cam, () => { c.fillStyle = '#F2D56A'; rr(c, -56, -36, 112, 72, 6); c.fill(); }, 10, 7, 10, 0.45, '60,40,0');
  g = c.createLinearGradient(-56, -36, 56, 36); g.addColorStop(0, '#FBE894'); g.addColorStop(1, '#EBC858'); c.fillStyle = g; rr(c, -56, -36, 112, 72, 6); c.fill(); c.fillStyle = 'rgba(255,255,255,0.35)'; rr(c, -50, -31, 100, 12, 5); c.fill();
  c.strokeStyle = 'rgba(190,150,40,0.5)'; c.lineWidth = 1.5; c.beginPath(); c.moveTo(-18, -36); c.lineTo(-18, 36); c.moveTo(20, -36); c.lineTo(20, 36); c.stroke(); c.restore();
}
function tip() {}   // la pointe est un bâton de craie (objet avec ombre), dessiné dans objects()
function craie(c, cam, tp) { const em = tp.em; c.save(); c.translate(tp.x, tp.y + 0); c.rotate(tp.a); c.translate(em * 0.16, em * 0.36); c.rotate(rad(-52));
  shadowed(c, cam, () => { c.fillStyle = '#E9E5DA'; rr(c, 0, -em * 0.12, em * 1.5, em * 0.24, em * 0.05); c.fill(); }, 8, 7, 10, 0.55, '0,0,0');
  const g = c.createLinearGradient(0, -em * 0.12, 0, em * 0.12); g.addColorStop(0, '#FFF3C4'); g.addColorStop(0.5, C.beurre); g.addColorStop(1, '#D9B145'); c.fillStyle = g; rr(c, 0, -em * 0.12, em * 1.5, em * 0.24, em * 0.05); c.fill(); c.restore(); }
export const skin = {
  id: 'ardoise', font: 'Barlow Condensed', weight: 700, wFinal: 800, cap: 0.70, gap: 0.18, em: [34, 54], dryCloseAlpha: 0.66,
  fonts: [{ family: 'Barlow Condensed', weight: 700, pkg: 'barlow-condensed' }, { family: 'Barlow Condensed', weight: 800, pkg: 'barlow-condensed' }],
  col: { dry: C.craie, fresh: C.beurre, stroke: C.craie },
  prepare, floor, sheet, stroke, inkExtras, textErode, objects, tip, finish: c => finish(c, 0.3, 0.05),
};
