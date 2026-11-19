// craie-verte.js — habillage « craie-verte » (pâte de l'identité tableau-craie) pour la mécanique trace-chemin.
// Essai C1 de la composition (out/report/notes/composition/matrice.md) : le même dessin et la même voix que le quatre-quarts
// (habillage « ardoise »), habillés de la pâte de Tableau Craie, pour savoir si « craie-verte » et « ardoise » sont un doublon.
// Pâte reprise de out/identities/tableau-craie/identity.md : tableau vert pleine image (#1F3A30, vignette #24443A → #16291F,
// traces de chiffon, poussière), craies blanche #FFF6D5 / orange #FFB84C / bleue #7FD1FF / rouge #FF7A7A, texte #F7F3E3,
// écriture manuscrite Caveat, rebord en bois avec bâtons de craie en bas du tableau. Pas de cadre en chêne ni de marbre (ardoise) :
// le tableau est le sol. Le décor du dessin (œufs, fouet, cuillère, beurre, moule) est dessiné à la craie, dans le calque d'encre
// érodé, au lieu d'objets réalistes. Mot dit en craie orange, craie sèche blanc cassé, annotations à la craie bleue.
// Dérivé d'ardoise.js (mêmes crochets) ; le moteur chemin.js n'est pas modifié.
import { S, W, H, rad, noiseTile, shadowed, rr } from '../outils.js';

const C = { board: '#1F3A30', boardHi: '#24443A', boardLo: '#16291F', craie: '#F7F3E3', blanc: '#FFF6D5', orange: '#FFB84C',
  bleu: '#7FD1FF', rouge: '#FF7A7A', vert: '#9BE58A', bois: '#6E4426', boisHi: '#8A5A34' };
const CAP = 0.62, GAP = 0.16;   // Caveat : hauteur de capitale ≈ 0,62 em (minuscules dominantes : œil ≈ 0,40 em)
const PAT = {};
function prepare() {
  PAT.dust = noiseTile(256, 21, (i, j) => { const n = S.noise2(i / 60, j / 60) * 0.6 + S.noise2(i / 17, j / 26) * 0.4; return [255, S.clamp((n - 0.45) * 2.2) * 30]; });
  PAT.streak = noiseTile(256, 22, (i, j) => { const n = S.noise2(i / 90, j / 4) * 0.7 + S.noise2(i / 30, j / 2) * 0.3; return [255, S.clamp((n - 0.5) * 2.4) * 18]; });
  PAT.speck = noiseTile(256, 23, (i, j, r) => { const v = r(); return [255, v > 0.988 ? 60 : 0]; });
  PAT.erode = noiseTile(256, 24, (i, j, r) => { const n = S.noise2(i / 3.1, j / 3.1) * 0.55 + r() * 0.45; return [0, n > 0.62 ? 160 : n > 0.55 ? 70 : 0]; });
  PAT.wood = noiseTile(256, 25, (i, j) => { const n = S.noise2(i / 120, j / 3) * 0.6 + S.noise2(i / 40, j / 1.4) * 0.4; return [40, S.clamp((n - 0.35) * 1.8) * 80, 20, 10]; });
  PAT.grain = noiseTile(256, 77, (i, j, r) => { const v = r() * 255; return [v, 255]; });
  // 26 traces de chiffon (comme tableau-craie), positions fixes (graine 31)
  const r = S.rng(31); PAT.blobs = []; for (let i = 0; i < 26; i++) PAT.blobs.push([r(), r(), 120 + r() * 260, 0.03 + r() * 0.04, -25 + r() * 30]);
}
const pat = (c, k) => c.createPattern(PAT[k], 'repeat');
function floor(c) { c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.fillStyle = C.boardLo; c.fillRect(0, 0, W, H); c.restore(); }
function sheet(c, cam, t, env) {
  const { x, y, w, h } = env.G.feuille;
  // le tableau déborde largement de la feuille : au zoom arrière on ne voit que du vert, puis le rebord en bas
  const bx = -1400, by = -1400, bw = W + 2800, bh = y + h + 1400;
  let g = c.createRadialGradient(x + w / 2, y + h * 0.45, 200, x + w / 2, y + h * 0.45, 1500); g.addColorStop(0, C.boardHi); g.addColorStop(0.55, C.board); g.addColorStop(1, C.boardLo);
  c.fillStyle = g; c.fillRect(bx, by, bw, bh);
  for (const [u, v, br, a, ang] of PAT.blobs) { c.save(); c.translate(x - 200 + u * (w + 400), y - 200 + v * (h + 300)); c.rotate(rad(ang)); c.scale(2.1, 0.6);
    const bg = c.createRadialGradient(0, 0, 0, 0, 0, br); bg.addColorStop(0, `rgba(230,240,232,${a})`); bg.addColorStop(1, 'rgba(230,240,232,0)'); c.fillStyle = bg; c.beginPath(); c.arc(0, 0, br, 0, 7); c.fill(); c.restore(); }
  c.save(); c.translate(540, 900); c.rotate(rad(-8)); c.scale(3, 3); c.globalAlpha = 0.4; c.fillStyle = pat(c, 'streak'); c.fillRect(-500, -500, 1000, 1000); c.restore();
  c.save(); c.scale(2, 2); c.globalAlpha = 0.5; c.fillStyle = pat(c, 'dust'); c.fillRect(-700, -700, 1900, 2000); c.restore();
  c.save(); c.scale(1.2, 1.2); c.fillStyle = pat(c, 'speck'); c.fillRect(-1100, -1100, 3000, 3600); c.restore();
  // rebord en bois sous le tableau, trois bâtons de craie et une brosse
  const ly = y + h + 14, lh = 46;
  shadowed(c, cam, () => { c.fillStyle = C.bois; c.fillRect(bx, ly, bw, lh); }, 10, 0, 14, 0.5, '0,0,0');
  g = c.createLinearGradient(0, ly, 0, ly + lh); g.addColorStop(0, C.boisHi); g.addColorStop(0.3, C.bois); g.addColorStop(1, '#4A2C18'); c.fillStyle = g; c.fillRect(bx, ly, bw, lh);
  c.save(); c.beginPath(); c.rect(bx, ly, bw, lh); c.clip(); c.globalAlpha = 0.5; c.fillStyle = pat(c, 'wood'); c.fillRect(bx, ly, bw, lh); c.restore();
  c.fillStyle = '#16291F'; c.fillRect(bx, ly + lh, bw, 1400);
  for (const [sx, col] of [[x + 120, C.blanc], [x + 250, C.orange], [x + 380, C.bleu]]) {
    shadowed(c, cam, () => { c.fillStyle = col; rr(c, sx, ly - 14, 96, 20, 6); c.fill(); }, 4, 4, 6, 0.45, '0,0,0');
    c.fillStyle = 'rgba(255,255,255,0.35)'; rr(c, sx + 4, ly - 12, 88, 5, 3); c.fill();
  }
  shadowed(c, cam, () => { c.fillStyle = '#3B3F44'; rr(c, x + w - 330, ly - 30, 200, 36, 8); c.fill(); }, 6, 5, 8, 0.5, '0,0,0');
  c.fillStyle = '#C9C2B2'; rr(c, x + w - 330, ly - 4, 200, 10, 4); c.fill();
}
// --- décor du dessin à la craie (dans le calque d'encre : érodé comme l'écriture) ---
function chalkLine(c, col, lw, a = 0.9) { c.strokeStyle = col; c.lineWidth = lw; c.lineCap = 'round'; c.lineJoin = 'round'; c.globalAlpha = a; }
function decor(c, env) {
  const O = env.G.objets; if (!O) return;
  c.save();
  // œufs
  for (const [ex, ey, ea] of O.oeufs) { c.save(); c.translate(ex, ey); c.rotate(rad(ea)); chalkLine(c, C.blanc, 4);
    c.beginPath(); c.moveTo(0, -46); c.bezierCurveTo(30, -46, 37, 6, 37, 14); c.bezierCurveTo(37, 34, 20, 44, 0, 44); c.bezierCurveTo(-20, 44, -37, 34, -37, 14); c.bezierCurveTo(-37, 6, -30, -46, 0, -46); c.stroke();
    chalkLine(c, C.blanc, 3, 0.5); c.beginPath(); c.arc(-12, -18, 9, rad(200), rad(290)); c.stroke(); c.restore(); }
  // fouet : manche et boucles
  c.save(); c.translate(O.fouet.x, O.fouet.y); c.rotate(rad(O.fouet.angle)); chalkLine(c, C.blanc, 4);
  c.beginPath(); rr(c, 0, -12, 150, 24, 11); c.stroke();
  for (const hw of [50, 32, 14]) for (const sgn of [-1, 1]) { c.beginPath(); c.moveTo(150, 0); c.bezierCurveTo(215, sgn * hw * 0.9, 300, sgn * hw * 1.25, 346, sgn * hw * 0.35); c.quadraticCurveTo(356, 0, 346, 0); c.stroke(); }
  c.restore();
  // cuillère
  c.save(); c.translate(O.cuillere.x, O.cuillere.y); c.rotate(rad(O.cuillere.angle)); chalkLine(c, C.orange, 4, 0.85);
  c.beginPath(); c.ellipse(52, 0, 58, 40, 0, 0, 7); c.stroke(); c.beginPath(); c.moveTo(108, -10); c.lineTo(380, -10); c.quadraticCurveTo(390, 0, 380, 10); c.lineTo(108, 10); c.stroke(); c.restore();
  // beurre : plaquette hachurée
  c.save(); c.translate(O.beurre.x, O.beurre.y); c.rotate(rad(O.beurre.angle)); chalkLine(c, '#FFE08A', 4, 0.9);
  c.strokeRect(-56, -36, 112, 72); c.beginPath(); c.rect(-56, -36, 112, 72); c.clip(); c.lineWidth = 2.4; c.globalAlpha = 0.55;
  for (let k = -110; k < 120; k += 16) { c.beginPath(); c.moveTo(k, 40); c.lineTo(k + 76, -40); c.stroke(); }
  c.restore();
  c.restore();
}
// après l'encre : décor à la craie, puis le moule cannelé tracé d'un tour pendant que la voix dit « moule »
function afterInk(c, cam, t, env) {
  decor(c, env);
  const M = env.G.moule, T = env.D.moule; if (!M || !T) return;
  const kk = S.clamp((t - T[0]) / (T[1] - T[0])); if (kk <= 0) return; const e = S.ease.inOutSine(kk) * Math.PI * 2;
  c.save(); c.strokeStyle = C.craie; c.lineCap = 'round'; c.lineWidth = 4; c.beginPath(); c.arc(M.c[0], M.c[1], M.r, -Math.PI / 2, -Math.PI / 2 + e); c.stroke();
  c.strokeStyle = C.bleu; c.lineWidth = 3; c.beginPath(); const n = Math.floor(90 * S.ease.inOutSine(kk)); for (let i = 0; i < n; i++) { const a0 = -Math.PI / 2 + i * Math.PI / 45, a1 = a0 + Math.PI / 45, am = (a0 + a1) / 2; if (i === 0) c.moveTo(M.c[0] + M.r2 * Math.cos(a0), M.c[1] + M.r2 * Math.sin(a0));
    c.quadraticCurveTo(M.c[0] + (M.r2 + 9) * Math.cos(am), M.c[1] + (M.r2 + 9) * Math.sin(am), M.c[0] + M.r2 * Math.cos(a1), M.c[1] + M.r2 * Math.sin(a1)); } c.stroke(); c.restore();
}
const annotations = {
  // double soulignement à la craie bleue sous une ligne (le titre)
  souligne(c, L, A, k) { const p0 = L.path.at(L.d0), x0 = p0.x, x1 = x0 + L.total, y = p0.y + 30; c.strokeStyle = C.bleu; c.lineWidth = 5; c.lineCap = 'round';
    for (let i = 0; i < 2; i++) { const kx = S.clamp(k * 2 - i); if (kx <= 0) continue; c.beginPath(); c.moveTo(x0 + 10, y + i * 14); c.quadraticCurveTo((x0 + x1) / 2, y - 8 + i * 14, x0 + 10 + (x1 - x0 - 20) * kx, y + 2 + i * 14 - 4 * kx); c.stroke(); } },
};
function textErode(c) { c.save(); c.scale(0.9, 0.9); c.fillStyle = c.createPattern(PAT.erode, 'repeat'); c.fillRect(-1600, -1600, 4400, 5200); c.restore(); }
function chalk(c, cam, t, env) {   // bâton de craie orange à la pointe de la ligne en cours
  if (t > env.T_OUT0 + 0.2) return;
  let L = null; for (const X of env.LINES) if (X.tStart - 0.08 <= t && t <= X.tEnd + 0.3) L = X; if (!L) return;
  const tp = env.tipOf(L, t); if (!tp) return;
  const p = L.path.at(tp.d), em = L.emW, off = L.below ? (GAP + CAP / 2) * em : -(GAP + CAP / 2) * em;
  c.save(); c.translate(p.x - Math.sin(p.a) * off, p.y + Math.cos(p.a) * off); c.rotate(p.a); c.translate(em * 0.16, em * 0.36); c.rotate(rad(-52));
  shadowed(c, cam, () => { c.fillStyle = '#E8A23A'; rr(c, 0, -em * 0.12, em * 1.4, em * 0.24, em * 0.05); c.fill(); }, 8, 7, 10, 0.55, '0,0,0');
  const g = c.createLinearGradient(0, -em * 0.12, 0, em * 0.12); g.addColorStop(0, '#FFE1A6'); g.addColorStop(0.5, C.orange); g.addColorStop(1, '#D9922E'); c.fillStyle = g; rr(c, 0, -em * 0.12, em * 1.4, em * 0.24, em * 0.05); c.fill(); c.restore();
}
function objects(c, cam, t, env) { chalk(c, cam, t, env); }
function finish(c) {
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
  const g = c.createRadialGradient(W / 2, H / 2, 640, W / 2, H / 2, 1250); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.28)'); c.fillStyle = g; c.fillRect(0, 0, W, H);
  c.globalAlpha = 0.05; c.globalCompositeOperation = 'overlay'; c.fillStyle = c.createPattern(PAT.grain, 'repeat'); c.fillRect(0, 0, W, H); c.restore();
}

export const habillage = {
  id: 'craie-verte',
  fonts: [{ family: 'Caveat', weight: 700, pkg: 'caveat' }],
  font: 'Caveat', weight: 700, wFinal: 700, cap: CAP, gap: GAP,
  em: [40, 64], trackMax: 0.06, floorPx: 130, floorFast: 100, maxPx: 240, dryCloseAlpha: 0.66, lineWidth: 3.6,
  col: { fresh: C.orange, dry: C.craie, stroke: C.blanc, annot: C.bleu },
  ghost: { mode: 'wipe', alpha: 0.5 },
  prepare, floor, sheet, afterInk, annotations, textErode, objects, finish,
};
