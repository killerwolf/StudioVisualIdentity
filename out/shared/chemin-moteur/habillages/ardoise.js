// ardoise.js — habillage « ardoise » de lyrics-chemin (déclinaison A2, « Le quatre-quarts », short narré).
// Craie sur une ardoise de bistrot dans un cadre en chêne, posée sur un plan de travail en marbre. Mot dit en jaune beurre,
// craie sèche blanc cassé, annotations à la craie rose. Le calque d'encre est érodé par un grain attaché au monde (textErode) :
// c'est lui qui fait la craie, et il grossit avec le zoom. Pointe = bâton de craie jaune (objet avec ombre).
// Décor du dessin quatre-quarts : moule cannelé tracé d'un tour (G.moule, temps dans D.moule), œufs, fouet, cuillère, beurre.
// Maquette d'origine : out/report/notes/lyrics-chemin/declinaisons/proto/quatre-quarts.js (Fable).
import { S, W, H, rad, noiseTile, shadowed, rr } from '../outils.js';

const C = { slate: '#2C3836', slateHi: '#364643', slateLo: '#222C2B', craie: '#F1EEE6', beurre: '#FFD766', rose: '#F29A85', chene: '#C39A62', marbre: '#E7E3DC' };
const FR = 30, CAP = 0.70, GAP = 0.18;
const PAT = {};
function prepare() {
  PAT.dust = noiseTile(256, 21, (i, j) => { const n = S.noise2(i / 60, j / 60) * 0.6 + S.noise2(i / 17, j / 26) * 0.4; return [255, S.clamp((n - 0.45) * 2.2) * 34]; });
  PAT.streak = noiseTile(256, 22, (i, j) => { const n = S.noise2(i / 90, j / 4) * 0.7 + S.noise2(i / 30, j / 2) * 0.3; return [255, S.clamp((n - 0.5) * 2.4) * 20]; });
  PAT.speck = noiseTile(256, 23, (i, j, r) => { const v = r(); return [255, v > 0.985 ? 70 : 0]; });
  PAT.erode = noiseTile(256, 24, (i, j, r) => { const n = S.noise2(i / 3.1, j / 3.1) * 0.55 + r() * 0.45; return [0, n > 0.63 ? 150 : n > 0.56 ? 60 : 0]; });
  PAT.wood = noiseTile(256, 25, (i, j) => { const n = S.noise2(i / 120, j / 3) * 0.6 + S.noise2(i / 40, j / 1.4) * 0.4; return [70, S.clamp((n - 0.35) * 1.8) * 70, 40, 10]; });
  PAT.marble = noiseTile(256, 26, (i, j) => { const n = S.noise2(i / 70, j / 70) * 0.7 + S.noise2(i / 20, j / 20) * 0.3; return [120, S.clamp((n - 0.5) * 2) * 50]; });
  PAT.grain = noiseTile(256, 77, (i, j, r) => { const v = r() * 255; return [v, 255]; });
  // nappes de poussière de craie essuyée : positions fixes (graine 31)
  const r = S.rng(31); PAT.blobs = []; for (let i = 0; i < 46; i++) PAT.blobs.push([r(), r(), 90 + r() * 240, 0.025 + r() * 0.045]);
}
const pat = (c, k) => c.createPattern(PAT[k], 'repeat');
function floor(c) { c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.fillStyle = C.marbre; c.fillRect(0, 0, W, H); c.restore(); }
function sheet(c, cam, t, env) {
  const { x, y, w, h } = env.G.feuille;
  c.fillStyle = C.marbre; c.fillRect(-1400, -1400, W + 2800, H + 2800); c.save(); c.scale(4, 4); c.fillStyle = pat(c, 'marble'); c.fillRect(-350, -350, 1000, 1200); c.restore();
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
  for (const [u, v, br, a] of PAT.blobs) { c.save(); c.translate(sx + u * sw, sy + v * sh); c.rotate(rad(-14)); c.scale(1.9, 0.75);
    const bg = c.createRadialGradient(0, 0, 0, 0, 0, br); bg.addColorStop(0, `rgba(235,240,236,${a})`); bg.addColorStop(1, 'rgba(235,240,236,0)'); c.fillStyle = bg; c.beginPath(); c.arc(0, 0, br, 0, 7); c.fill(); c.restore(); }
  c.save(); c.translate(540, 900); c.rotate(rad(-14)); c.scale(3, 3); c.globalAlpha = 0.45; c.fillStyle = pat(c, 'streak'); c.fillRect(-300, -400, 600, 800); c.restore();
  c.save(); c.scale(1.2, 1.2); c.fillStyle = pat(c, 'speck'); c.fillRect(0, 0, 900, 1600); c.restore();
  for (const [a, b, d, e] of [[sx, 0, sx + 26, 0], [0, sy, 0, sy + 30]]) { const e2 = c.createLinearGradient(a, b, d, e); e2.addColorStop(0, 'rgba(0,0,0,0.42)'); e2.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = e2; c.fillRect(sx, sy, sw, sh); }   // ombre intérieure du cadre
  c.restore();
}
// après l'encre (dans le calque de craie) : le moule cannelé, tracé d'un tour pendant que la voix dit « moule »
function afterInk(c, cam, t, env) {
  const M = env.G.moule, T = env.D.moule; if (!M || !T) return;
  const kk = S.clamp((t - T[0]) / (T[1] - T[0])); if (kk <= 0) return; const e = S.ease.inOutSine(kk) * Math.PI * 2;
  c.save(); c.strokeStyle = C.craie; c.lineCap = 'round'; c.lineWidth = 3.6; c.beginPath(); c.arc(M.c[0], M.c[1], M.r, -Math.PI / 2, -Math.PI / 2 + e); c.stroke();
  c.lineWidth = 2.6; c.beginPath(); const n = Math.floor(90 * S.ease.inOutSine(kk)); for (let i = 0; i < n; i++) { const a0 = -Math.PI / 2 + i * Math.PI / 45, a1 = a0 + Math.PI / 45, am = (a0 + a1) / 2; if (i === 0) c.moveTo(M.c[0] + M.r2 * Math.cos(a0), M.c[1] + M.r2 * Math.sin(a0));
    c.quadraticCurveTo(M.c[0] + (M.r2 + 9) * Math.cos(am), M.c[1] + (M.r2 + 9) * Math.sin(am), M.c[0] + M.r2 * Math.cos(a1), M.c[1] + M.r2 * Math.sin(a1)); } c.stroke(); c.restore();
}
const annotations = {
  // double soulignement à la craie rose sous une ligne (le titre)
  souligne(c, L, A, k) { const p0 = L.path.at(L.d0), x0 = p0.x, x1 = x0 + L.total, y = p0.y + 28; c.strokeStyle = C.rose; c.lineWidth = 5; c.lineCap = 'round';
    for (let i = 0; i < 2; i++) { const kx = S.clamp(k * 2 - i); if (kx <= 0) continue; c.beginPath(); c.moveTo(x0 + 10, y + i * 14); c.quadraticCurveTo((x0 + x1) / 2, y - 8 + i * 14, x0 + 10 + (x1 - x0 - 20) * kx, y + 2 + i * 14 - 4 * kx); c.stroke(); } },
};
function textErode(c) { c.save(); c.scale(0.9, 0.9); c.fillStyle = c.createPattern(PAT.erode, 'repeat'); c.fillRect(-600, -600, 2400, 3200); c.restore(); }
function chalk(c, cam, t, env) {   // bâton de craie jaune à la pointe de la ligne en cours
  if (t > env.T_OUT0 + 0.2) return;
  let L = null; for (const X of env.LINES) if (X.tStart - 0.08 <= t && t <= X.tEnd + 0.3) L = X; if (!L) return;
  const tp = env.tipOf(L, t); if (!tp) return;
  const p = L.path.at(tp.d), em = L.emW, off = L.below ? (GAP + CAP / 2) * em : -(GAP + CAP / 2) * em;
  c.save(); c.translate(p.x - Math.sin(p.a) * off, p.y + Math.cos(p.a) * off); c.rotate(p.a); c.translate(em * 0.16, em * 0.36); c.rotate(rad(-52));
  shadowed(c, cam, () => { c.fillStyle = '#E9E5DA'; rr(c, 0, -em * 0.12, em * 1.5, em * 0.24, em * 0.05); c.fill(); }, 8, 7, 10, 0.55, '0,0,0');
  const g = c.createLinearGradient(0, -em * 0.12, 0, em * 0.12); g.addColorStop(0, '#FFF3C4'); g.addColorStop(0.5, C.beurre); g.addColorStop(1, '#D9B145'); c.fillStyle = g; rr(c, 0, -em * 0.12, em * 1.5, em * 0.24, em * 0.05); c.fill(); c.restore();
}
function objects(c, cam, t, env) {
  const O = env.G.objets; let g;
  chalk(c, cam, t, env);
  // fouet
  c.save(); c.translate(O.fouet.x, O.fouet.y); c.rotate(rad(O.fouet.angle));
  c.lineCap = 'round'; for (const hw of [50, 34, 17, 0.01]) for (const sgn of hw > 1 ? [-1, 1] : [1]) { shadowed(c, cam, () => { c.strokeStyle = '#C9CFD2'; c.lineWidth = 3.2; c.beginPath(); c.moveTo(150, 0); c.bezierCurveTo(215, sgn * hw * 0.9, 300, sgn * hw * 1.25, 346, sgn * hw * 0.35); c.quadraticCurveTo(356, 0, 346, 0); c.stroke(); }, 5, 5, 8, 0.4, '0,0,0'); }
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
  // beurre sur son papier, voile de farine
  c.save(); c.translate(O.beurre.x, O.beurre.y); c.rotate(rad(O.beurre.angle));
  { const r = S.rng(55); for (let i = 0; i < 26; i++) { const a = r() * 7, d = 60 + r() * 120; c.fillStyle = `rgba(255,255,255,${0.10 + r() * 0.12})`; c.beginPath(); c.arc(-140 + Math.cos(a) * d * 0.6, 40 + Math.sin(a) * d * 0.4, 4 + r() * 14, 0, 7); c.fill(); } }
  shadowed(c, cam, () => { c.fillStyle = '#EFE9DA'; c.beginPath(); c.moveTo(-92, -70); c.lineTo(88, -78); c.lineTo(96, 66); c.lineTo(-84, 74); c.closePath(); c.fill(); }, 8, 5, 8, 0.4, '0,0,0');
  c.strokeStyle = 'rgba(160,150,130,0.5)'; c.lineWidth = 1; c.beginPath(); c.moveTo(-60, -70); c.lineTo(-52, 72); c.moveTo(60, -76); c.lineTo(66, 68); c.stroke();
  shadowed(c, cam, () => { c.fillStyle = '#F2D56A'; rr(c, -56, -36, 112, 72, 6); c.fill(); }, 10, 7, 10, 0.45, '60,40,0');
  g = c.createLinearGradient(-56, -36, 56, 36); g.addColorStop(0, '#FBE894'); g.addColorStop(1, '#EBC858'); c.fillStyle = g; rr(c, -56, -36, 112, 72, 6); c.fill(); c.fillStyle = 'rgba(255,255,255,0.35)'; rr(c, -50, -31, 100, 12, 5); c.fill();
  c.strokeStyle = 'rgba(190,150,40,0.5)'; c.lineWidth = 1.5; c.beginPath(); c.moveTo(-18, -36); c.lineTo(-18, 36); c.moveTo(20, -36); c.lineTo(20, 36); c.stroke(); c.restore();
}
function finish(c) {
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
  const g = c.createRadialGradient(W / 2, H / 2, 620, W / 2, H / 2, 1250); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.3)'); c.fillStyle = g; c.fillRect(0, 0, W, H);
  c.globalAlpha = 0.05; c.globalCompositeOperation = 'overlay'; c.fillStyle = c.createPattern(PAT.grain, 'repeat'); c.fillRect(0, 0, W, H); c.restore();
}

export const habillage = {
  id: 'ardoise',
  fonts: [{ family: 'Barlow Condensed', weight: 700, pkg: 'barlow-condensed' }, { family: 'Barlow Condensed', weight: 800, pkg: 'barlow-condensed' }],
  font: 'Barlow Condensed', weight: 700, wFinal: 800, cap: CAP, gap: GAP,
  em: [34, 54], trackMax: 0.15, floorPx: 120, floorFast: 92, maxPx: 220, dryCloseAlpha: 0.66, lineWidth: 3.6,
  col: { fresh: C.beurre, dry: C.craie, stroke: C.craie, annot: C.rose },
  ghost: { mode: 'wipe', alpha: 0.5 },
  prepare, floor, sheet, afterInk, annotations, textErode, objects, finish,
};
