// B — version « tech » de la vidéo de paroles : habillage « editeur » (éditeur de code sombre sur un écran vertical,
// vu de dessus avec le clavier) + dessin « cargo » (un porte-conteneurs : chaque ligne de paroles est un conteneur,
// *ship*). Mots = jeu de REMPLISSAGE du dépôt (« Monday's draft »), jamais les vraies paroles. Maquette d'images fixes.
import { S, W, H, rad, noiseTile, shadowed, rr, finish } from './core.js';

const SCR = { x: 44, y: 120, w: 992, h: 1440 }, BZ = 14, CHIN = 52;
const C = { bg0: '#141B30', bg1: '#0B101D', bar: '#182037', plain: '#D5DCEA', kw: '#B79CF7', str: '#93D8A0', num: '#F2A65A', com: '#66769A', trait: '#8497C4',
  fresh: '#FFD84A', err: '#FF6B5E', desk: '#16171B', bezel: '#0A0B0E' };
const ROWH = 80;
// conteneurs : x, y, w ; ligne = arête qui porte une ligne de paroles (sinon conteneur de décor) ; c = couleur de syntaxe
const BOX = [
  { id: 'c1', x: 200, y: 622, w: 560, c: C.kw, n: '01' }, { x: 768, y: 622, w: 172, c: C.com, decor: 'c1' },
  { x: 200, y: 536, w: 130, c: C.com, decor: 'c2' }, { id: 'c2', x: 338, y: 536, w: 582, c: C.str, n: '02' },
  { id: 'c3', x: 230, y: 450, w: 510, c: C.num, n: '03' }, { x: 748, y: 450, w: 152, c: C.com, decor: 'c3' },
  { id: 'c8', x: 566, y: 364, w: 300, c: C.err, n: '08', rot: -8 },
];
const bx = id => BOX.find(b => b.id === id);
const inBox = (id, pad = 34) => { const b = bx(id), cy = b.y + ROWH / 2; if (!b.rot) return { type: 'droite', a: [b.x + pad + 26, cy], b: [b.x + b.w - pad + 14, cy] };
  const r = rad(b.rot), ox = b.x, oy = b.y + ROWH, tr = (px, py) => [ox + (px - ox) * Math.cos(r) - (py - oy) * Math.sin(r), oy + (px - ox) * Math.sin(r) + (py - oy) * Math.cos(r)];
  return { type: 'droite', a: tr(b.x + pad + 20, cy), b: tr(b.x + b.w - pad + 10, cy) }; };

export const G = {
  id: 'cargo', feuille: SCR,
  points: { L: [110, 706], R: [946, 706], BL: [288, 1120], BR: [780, 1120] },
  aretes: {
    titre:  { chemin: { type: 'droite', a: [290, 846], b: [766, 846] }, em: [44, 58], center: true, noLine: true, weight: 800, track: 0.04 },
    c1:     { chemin: inBox('c1'), inside: true, noLine: true, center: true, noFit: true },
    c2:     { chemin: inBox('c2'), inside: true, noLine: true, center: true, noFit: true },
    c3:     { chemin: inBox('c3'), inside: true, noLine: true, center: true, noFit: true },
    coqueG: { chemin: { type: 'droite', a: 'L', b: 'BL' }, m: [24, 12], below: true },
    quille: { chemin: { type: 'droite', a: 'BL', b: 'BR' }, m: [12, 12] },
    coqueD: { chemin: { type: 'droite', a: 'BR', b: 'R' }, m: [16, 30], below: true },
    fanion: { chemin: { type: 'droite', a: [166, 286], b: [366, 286] }, em: [44, 44], noLine: true, noFit: true },
    c8:     { chemin: inBox('c8', 26), inside: true, noLine: true, center: true, noFit: true, em: [38, 38] },
    vague1: { chemin: { type: 'vague', x0: 96, x1: 640, y: 1182, amp: 7, wl: 180, ph: 0.4 }, m: [8, 8], noFit: true },
  },
  final: { gauche: 176, cx: 512, largeurMax: 760, emMax: 68, espace: 0.6, rangs: [{ y: 1262 }, { y: 1344 }, { y: 1426 }, { y: 1508 }] },
  tour: { x: 96, y: 414, w: 86, h: 292, mat: [139, 236] },
  ui: { toast: { x: 312, y: 912 }, cle: { x: 596, y: 1022 }, fichier: { x: 664, y: 914 } },
  objets: { note: { x: 1002, y: 566, angle: 6 }, clavier: { x: -34, y: 1668 }, canette: { x: 934, y: 1792 } },
};
// Mêmes temps que la version actuelle (154,5 BPM). Unité = [texte, début, fin, classe de coloration une fois sèche].
export const D = {
  titre: "MONDAY'S DRAFT", langue: 'en', bpm: 154.5, duree: 32.62, zoomArriere: [29.515, 31.068],
  lignes: [
    { arete: 'titre', u: [["MONDAY'S", 0, 1.553], ['DRAFT', 1.553, 2.62]], cad: [[0], [1]], arr: 0, maxPx: 200 },
    { arete: 'c1', u: [['i fold', 3.2, 4.466], ['my day', 4.466, 5.049], ['in draft mode', 5.049, 5.86, 'kw']], cad: [[0, 1], [2]], arr: 3.01 },
    { arete: 'c2', u: [['i draw', 7.184, 7.573], ['lines', 7.573, 7.961], ['but not', 7.961, 8.26], ['for show', 8.26, 9.14]], cad: [[0, 1], [2, 3]], arr: 6.95 },
    { arete: 'c3', u: [["i've been", 10.291, 10.78], ['up since', 10.78, 11.068], ['5 a.m.', 11.068, 12.2, 'num']], cad: [[0], [1], [2]], arr: 9.9 },
    { arete: 'coqueG', u: [['printer down', 13.01, 14.175], ['cuz no ink', 14.175, 15.48]], cad: [[0], [1]], arr: 12.82, annotation: { type: 'croix', t: 13.7 } },
    { arete: 'quille', u: [["draft mode's", 16.699, 17.087, 'kw'], ['my spare keys', 17.087, 18.58]], cad: [[0], [1]], arr: 16.31 },
    { arete: 'coqueD', u: [['make another', 19.36, 20.44], ['note.txt', 20.44, 21.26, 'str']], cad: [[0], [1]], arr: 19.16 },
    { arete: 'fanion', u: [['and yet', 22.88, 23.52]], cad: [[0]], arr: 22.52 },
    { arete: 'c8', u: [['wrong', 25.98, 26.64], ['fold', 26.64, 27.2]], cad: [[0, 1]], arr: 25.79, annotation: { type: 'ondule', t: 26.75 } },
    { arete: 'vague1', u: [['such a lot', 27.62, 28.1], ['of wrong', 28.1, 28.58], ['folds', 28.58, 29.2]], cad: [[0], [1], [2]], arr: 27.42 },
  ],
  final: { u: [['we sail,', 29.2, 29.9], ['we sail,', 29.9, 30.7], ['and we sail,', 30.7, 31.54], ['and we sail,', 31.54, 32.12], ['and we sail,', 32.12, 32.9]], rangs: [[0, 1], [2], [3], [4]] },
};

// ?data=<chemin relatif à scene.html> : remplace les MOTS (mêmes arêtes, mêmes temps) — sert à essayer les vraies paroles,
// qui restent hors dépôt (lien symbolique dans proto/tmp/, ignoré par git). Format : { titre, lignes: { <arête>: [[texte, classe?], …] }, final: [texte, …] }
export async function avant() { const q = new URLSearchParams(location.search).get('data'); if (!q) return; const X = await (await fetch(new URL(q, location.href).href)).json();
  for (const l of D.lignes) if (X.lignes[l.arete]) l.u = l.u.map((u, i) => [X.lignes[l.arete][i][0], u[1], u[2], X.lignes[l.arete][i][1]]);
  D.final.u = D.final.u.map((u, i) => [X.final[i], u[1], u[2]]); D.titre = X.titre; }
const PAT = {};
function prepare() { PAT.felt = noiseTile(256, 41, (i, j, r) => { const v = r(); return [255, v > 0.6 ? 10 : 0]; }); }
function floor(c) { c.fillStyle = C.desk; c.fillRect(0, 0, W, H); }
const mono = (c, px, wgt = 400, st = '') => { c.font = `${st}${wgt} ${px}px 'JetBrains Mono'`; c.letterSpacing = '0px'; };
const bars = (c, x, y, ws, h = 7, col = 'rgba(160,175,210,0.28)') => { c.fillStyle = col; let cx = x; for (const w of ws) { rr(c, cx, y, w, h, h / 2); c.fill(); cx += w + 8; } };

function sheet(c, cam, t) {
  const { x, y, w, h } = SCR;
  // tapis de bureau
  c.fillStyle = C.desk; c.fillRect(-400, -400, W + 800, H + 800); c.save(); c.fillStyle = c.createPattern(PAT.felt, 'repeat'); c.fillRect(-400, -400, W + 800, H + 800); c.restore();
  // écran : coque, dalle
  shadowed(c, cam, () => { c.fillStyle = C.bezel; rr(c, x - BZ, y - BZ, w + 2 * BZ, h + BZ + CHIN, 30); c.fill(); }, 34, 10, 20, 0.7, '0,0,0');
  let g = c.createLinearGradient(x, y - BZ, x, y + h + CHIN); g.addColorStop(0, '#1A1C22'); g.addColorStop(0.04, '#0C0D10'); g.addColorStop(1, '#0A0B0E'); c.fillStyle = g; rr(c, x - BZ, y - BZ, w + 2 * BZ, h + BZ + CHIN, 30); c.fill();
  c.strokeStyle = 'rgba(255,255,255,0.10)'; c.lineWidth = 1.2; rr(c, x - BZ + 0.6, y - BZ + 0.6, w + 2 * BZ - 1.2, h + BZ + CHIN - 1.2, 30); c.stroke();
  c.save(); rr(c, x, y, w, h, 16); c.clip();
  g = c.createLinearGradient(x, y, x + w, y + h); g.addColorStop(0, C.bg0); g.addColorStop(1, C.bg1); c.fillStyle = g; c.fillRect(x, y, w, h);
  g = c.createRadialGradient(360, 520, 60, 360, 520, 900); g.addColorStop(0, 'rgba(90,110,200,0.10)'); g.addColorStop(1, 'rgba(90,110,200,0)'); c.fillStyle = g; c.fillRect(x, y, w, h);
  // grille de points (équivalent du quadrillage) : 20 px, croix tous les 100 px
  const a20 = S.lerp(0.10, 0.16, S.clamp((cam.s - 1) / 2)), rdot = Math.max(0.9, 1.5 / Math.sqrt(cam.s));
  c.fillStyle = `rgba(150,170,225,${a20})`; for (let gy = 180; gy < y + h; gy += 20) for (let gx = 100; gx < x + w; gx += 20) { if (gx % 100 === 0 && gy % 100 === 0) continue; c.fillRect(gx - rdot / 2, gy - rdot / 2, rdot, rdot); }
  c.strokeStyle = 'rgba(150,170,225,0.30)'; c.lineWidth = Math.max(0.6, 1 / Math.sqrt(cam.s)); c.beginPath(); for (let gy = 200; gy < y + h; gy += 100) for (let gx = 100; gx < x + w; gx += 100) { c.moveTo(gx - 4, gy); c.lineTo(gx + 4, gy); c.moveTo(gx, gy - 4); c.lineTo(gx, gy + 4); } c.stroke();
  // gouttière : numéros de ligne (décor)
  c.fillStyle = 'rgba(11,15,28,0.55)'; c.fillRect(x, y, 44, h); mono(c, 11); c.textAlign = 'right'; c.fillStyle = 'rgba(102,118,154,0.75)'; for (let i = 1, gy = 200; gy < y + h - 40; gy += 20, i++) c.fillText(String(i), x + 34, gy + 4); c.textAlign = 'left';
  // barre de titre : pastilles, onglet, pastille « mode »
  c.fillStyle = C.bar; c.fillRect(x, y, w, 54); c.fillStyle = 'rgba(255,255,255,0.05)'; c.fillRect(x, y + 53, w, 1);
  ['#E0655C', '#E2B24C', '#62C36A'].forEach((col, i) => { c.fillStyle = col; c.globalAlpha = 0.85; c.beginPath(); c.arc(x + 30 + i * 24, y + 27, 7, 0, 7); c.fill(); }); c.globalAlpha = 1;
  c.fillStyle = C.bg0; rr(c, x + 112, y + 10, 250, 44, [10, 10, 0, 0]); c.fill(); c.fillStyle = C.str; rr(c, x + 128, y + 22, 13, 17, 2); c.fill(); bars(c, x + 152, y + 27, [96, 42]); c.fillStyle = C.fresh; c.beginPath(); c.arc(x + 340, y + 31, 4, 0, 7); c.fill();
  bars(c, x + 384, y + 27, [80, 30], 7, 'rgba(160,175,210,0.16)');
  c.strokeStyle = C.kw; c.lineWidth = 1.5; rr(c, x + w - 206, y + 13, 180, 28, 14); c.stroke(); c.fillStyle = C.kw; for (const dx of [0, 11]) { c.beginPath(); c.moveTo(x + w - 190 + dx, y + 20); c.lineTo(x + w - 181 + dx, y + 27); c.lineTo(x + w - 190 + dx, y + 34); c.closePath(); c.fill(); } bars(c, x + w - 160, y + 24, [70, 34], 7, 'rgba(183,156,247,0.55)');
  // barre d'état
  c.fillStyle = C.bar; c.fillRect(x, y + h - 30, w, 30); bars(c, x + 20, y + h - 19, [60, 24, 90], 7, 'rgba(160,175,210,0.22)'); bars(c, x + w - 250, y + h - 19, [40, 70, 30, 44], 7, 'rgba(160,175,210,0.22)'); c.fillStyle = C.str; c.beginPath(); c.arc(x + w - 268, y + h - 15, 4, 0, 7); c.fill();
  c.restore();
}
const lineT = (env, id) => env.lineOf(id).tStart;
function box(c, b, kk, env) {   // conteneur : contour tracé de gauche à droite avec la ligne, ondulations aux deux bouts, numéro de ligne (décor)
  c.save(); if (b.rot) { c.translate(b.x, b.y + ROWH); c.rotate(rad(b.rot)); c.translate(-b.x, -(b.y + ROWH)); }
  const w = b.w * kk; c.globalAlpha = 0.09; c.fillStyle = b.c; rr(c, b.x, b.y, w, ROWH, 5); c.fill(); c.globalAlpha = 1;
  c.strokeStyle = b.c; c.lineWidth = 2.4; c.globalAlpha = b.id ? 0.9 : 0.5; rr(c, b.x, b.y, w, ROWH, 5); c.stroke();
  c.globalAlpha = b.id ? 0.30 : 0.22; c.lineWidth = 1.4; c.beginPath(); for (let gx = b.x + 8; gx < b.x + w - 4; gx += 9) { if (b.id && gx > b.x + 22 && gx < b.x + b.w - 22) continue; c.moveTo(gx, b.y + 7); c.lineTo(gx, b.y + ROWH - 7); } c.stroke();
  if (!b.id && kk >= 1) { c.globalAlpha = 1; bars(c, b.x + 20, b.y + ROWH / 2 - 4, b.w > 150 ? [b.w - 96, 34] : [b.w - 44], 8, 'rgba(102,118,154,0.45)'); }
  if (b.n && kk > 0.1) { c.globalAlpha = 0.9; mono(c, 12); c.fillStyle = C.com; c.fillText(b.n, b.x + 27, b.y + ROWH / 2 + 4); }
  c.restore();
}
function under(c, cam, t, env) {
  const P = G.points, T = G.tour;
  // coque (aplat discret) : visible dès que le flanc gauche est tracé
  const kh = S.clamp((t - lineT(env, 'coqueD') - 1.2) / 0.6); if (kh > 0) { c.fillStyle = `rgba(132,151,196,${0.06 * kh})`; c.beginPath(); c.moveTo(...P.L); c.lineTo(...P.BL); c.lineTo(...P.BR); c.lineTo(...P.R); c.closePath(); c.fill(); }
  // pont, château et mât : tracés avec le premier conteneur
  const kd = S.clamp((t - lineT(env, 'c1') + 0.25) / 0.5); if (kd > 0) { c.strokeStyle = C.trait; c.lineWidth = 3.2; c.lineCap = 'round'; c.beginPath(); c.moveTo(...P.L); c.lineTo(P.L[0] + (P.R[0] - P.L[0]) * kd, P.L[1]); c.stroke(); }
  const kt = S.clamp((t - lineT(env, 'c3') + 0.4) / 0.6); if (kt > 0) { c.strokeStyle = C.trait; c.lineWidth = 2.8; c.fillStyle = 'rgba(132,151,196,0.07)'; rr(c, T.x, T.y + T.h * (1 - kt), T.w, T.h * kt, [6, 6, 0, 0]); c.fill(); c.stroke();
    if (kt >= 1) { for (let i = 0; i < 4; i++) { c.fillStyle = i === 0 ? 'rgba(255,216,74,0.55)' : 'rgba(132,151,196,0.35)'; rr(c, T.x + 12, T.y + 16 + i * 30, T.w - 24, 12, 3); c.fill(); } } }
  const km = S.clamp((t - lineT(env, 'fanion') + 0.45) / 0.4); if (km > 0) { c.strokeStyle = C.trait; c.lineWidth = 2.8; c.beginPath(); c.moveTo(T.mat[0], T.y); c.lineTo(T.mat[0], T.y + (T.mat[1] - T.y) * km); c.stroke();
    if (km >= 1) { const kf = S.clamp((t - lineT(env, 'fanion') + 0.3) / 0.6); c.strokeStyle = C.err; c.lineWidth = 2.6; c.lineJoin = 'round'; c.beginPath(); const Lf = env.lineOf('fanion'), fw = Lf.path.at(Lf.d0).x + Lf.total + 46 - T.mat[0];   // fanion accroché à la mise en page : il s'allonge avec le texte
      c.moveTo(T.mat[0], 242); c.lineTo(T.mat[0] + fw * kf, 242); if (kf >= 1) { c.lineTo(T.mat[0] + fw - 24, 271); c.lineTo(T.mat[0] + fw, 300); c.lineTo(T.mat[0], 300); } c.stroke(); } }
  // conteneurs
  for (const b of BOX) { const id = b.id || b.decor, L = env.lineOf(id), t0 = L.tStart - 0.25, kk = b.id ? S.clamp((t - t0) / Math.max(0.4, (L.tEnd - L.tStart) * 0.8)) : S.clamp((t - L.tEnd + 0.2) / 0.4); if (kk > 0) box(c, b, S.ease.outCubic(kk), env); }
  // hublots et ligne de flottaison (décor), une fois la coque fermée
  if (kh > 0) { c.globalAlpha = kh; c.strokeStyle = 'rgba(132,151,196,0.5)'; c.lineWidth = 1.6; c.setLineDash([10, 9]); c.beginPath(); c.moveTo(246, 1010); c.lineTo(822, 1010); c.stroke(); c.setLineDash([]); c.globalAlpha = 1; }
  // suite de la vague et invites des rangs finaux (décor)
  const kv = S.clamp((t - env.lineOf('vague1').tEnd) / 0.5); if (kv > 0) { c.strokeStyle = C.trait; c.lineWidth = 3.2; c.beginPath(); for (let wx = 700; wx <= 700 + 240 * kv; wx += 4) { const wy = 1182 + 7 * Math.sin(0.4 + (wx - 96) / 180 * 2 * Math.PI); wx === 700 ? c.moveTo(wx, wy) : c.lineTo(wx, wy); } c.stroke(); }
  for (const R of env.SEA) if (t >= R.t0 - 0.1 && (R === env.SEA[0] || R.row !== env.SEA[env.SEA.indexOf(R) - 1].row)) { mono(c, env.SEA_EM * 0.8, 700); c.fillStyle = C.com; c.fillText('>', 112, R.y); }
}
function stroke(c, L, d0, d1) { c.save(); c.strokeStyle = C.trait; c.lineWidth = 3.2; c.lineCap = 'round'; c.beginPath(); for (let d = d0; d < d1; d += 4) { const p = L.path.at(d, 2); d === d0 ? c.moveTo(p.x, p.y) : c.lineTo(p.x, p.y); } const e = L.path.at(d1, 2); c.lineTo(e.x, e.y); c.stroke(); c.restore(); }
function inkExtras(c, cam, t, env) {
  // annotations rouges = idiomes de l'éditeur : ✗ d'un contrôle en échec, soulignement ondulé d'une erreur (jamais du texte)
  const Lg = env.lineOf('coqueG'); if (t > 13.7) { const u = Lg.units[0], p = Lg.path.at(u.d1 + 30, 2), k = S.clamp((t - 13.7) / 0.3), em = Lg.emW; c.save(); c.translate(p.x, p.y); c.rotate(p.a); c.translate(-em * 0.5, -em * 0.95); c.strokeStyle = C.err; c.lineWidth = 4; c.lineCap = 'round'; c.beginPath(); c.moveTo(-9, -9); c.lineTo(-9 + 18 * Math.min(1, k * 2), -9 + 18 * Math.min(1, k * 2)); if (k > 0.5) { c.moveTo(9, -9); c.lineTo(9 - 18 * (k * 2 - 1), -9 + 18 * (k * 2 - 1)); } c.stroke(); c.restore(); }
  const L8 = env.lineOf('c8'); if (t > 26.75) { const k = S.clamp((t - 26.75) / 0.45), d0 = L8.d0, d1 = d0 + L8.total * k; c.save(); c.strokeStyle = C.err; c.lineWidth = 3; c.lineJoin = 'round'; c.beginPath(); for (let d = d0, i = 0; d <= d1; d += 7, i++) { const p = L8.path.at(d, 2), off = L8.emW * 0.48 + (i % 2 ? 5 : 0), px = p.x - Math.sin(p.a) * off, py = p.y + Math.cos(p.a) * off; i ? c.lineTo(px, py) : c.moveTo(px, py); } c.stroke(); c.restore(); }
}
function panel(c, cam, x, y, w, h, fn) { shadowed(c, cam, () => { c.fillStyle = '#1C2640'; rr(c, x, y, w, h, 10); c.fill(); }, 14, 6, 10, 0.55, '0,0,0'); c.strokeStyle = 'rgba(150,170,225,0.28)'; c.lineWidth = 1.2; rr(c, x + 0.6, y + 0.6, w - 1.2, h - 1.2, 10); c.stroke(); fn(); }
function objects(c, cam, t, env) {
  const U = G.ui, O = G.objets; let g;
  // objets d'interface croisés en route (aucun mot dessus) : notification d'échec, pastille « clé », onglet de fichier
  if (t > 13.3) panel(c, cam, U.toast.x, U.toast.y, 178, 56, () => { c.fillStyle = C.err; c.beginPath(); c.arc(U.toast.x + 28, U.toast.y + 28, 12, 0, 7); c.fill(); c.strokeStyle = '#1C2640'; c.lineWidth = 3; c.lineCap = 'round'; c.beginPath(); c.moveTo(U.toast.x + 23, U.toast.y + 23); c.lineTo(U.toast.x + 33, U.toast.y + 33); c.moveTo(U.toast.x + 33, U.toast.y + 23); c.lineTo(U.toast.x + 23, U.toast.y + 33); c.stroke(); bars(c, U.toast.x + 52, U.toast.y + 17, [96], 8, 'rgba(213,220,234,0.55)'); bars(c, U.toast.x + 52, U.toast.y + 33, [50, 34], 6, 'rgba(160,175,210,0.3)'); });
  if (t > 17.0) panel(c, cam, U.cle.x, U.cle.y, 138, 44, () => { c.strokeStyle = C.num; c.fillStyle = C.num; c.lineWidth = 3.2; c.beginPath(); c.arc(U.cle.x + 24, U.cle.y + 22, 7, 0, 7); c.stroke(); c.beginPath(); c.moveTo(U.cle.x + 31, U.cle.y + 22); c.lineTo(U.cle.x + 54, U.cle.y + 22); c.moveTo(U.cle.x + 46, U.cle.y + 22); c.lineTo(U.cle.x + 46, U.cle.y + 29); c.moveTo(U.cle.x + 53, U.cle.y + 22); c.lineTo(U.cle.x + 53, U.cle.y + 28); c.stroke(); for (let i = 0; i < 5; i++) { c.globalAlpha = 0.7; c.beginPath(); c.arc(U.cle.x + 72 + i * 12, U.cle.y + 22, 3.2, 0, 7); c.fill(); } c.globalAlpha = 1; });
  if (t > 20.3) panel(c, cam, U.fichier.x, U.fichier.y, 128, 50, () => { c.fillStyle = C.str; c.beginPath(); c.moveTo(U.fichier.x + 16, U.fichier.y + 11); c.lineTo(U.fichier.x + 30, U.fichier.y + 11); c.lineTo(U.fichier.x + 38, U.fichier.y + 19); c.lineTo(U.fichier.x + 38, U.fichier.y + 39); c.lineTo(U.fichier.x + 16, U.fichier.y + 39); c.closePath(); c.fill(); c.fillStyle = '#1C2640'; c.fillRect(U.fichier.x + 20, U.fichier.y + 24, 14, 2.5); c.fillRect(U.fichier.x + 20, U.fichier.y + 30, 10, 2.5); bars(c, U.fichier.x + 50, U.fichier.y + 21, [58], 8, 'rgba(147,216,160,0.6)'); });
  // curseur bloc à la pointe (plein pendant la frappe, clignote au repos sur le temps)
  for (const tp of env.tips) { const em = tp.em, on = tp.writing || Math.floor(t / (60 / D.bpm)) % 2 === 0; if (!on) continue; c.save(); c.translate(tp.x, tp.y); c.rotate(tp.a); c.fillStyle = C.fresh; c.globalAlpha = 0.92; c.fillRect(em * 0.08, -em * 0.62, em * 0.56, em * 1.18); c.restore(); }
  // objets physiques autour de l'écran : note collée, autocollants, clavier mécanique, canette
  c.save(); c.translate(O.note.x, O.note.y); c.rotate(rad(O.note.angle)); shadowed(c, cam, () => { c.fillStyle = '#F2DC6B'; c.fillRect(-48, -48, 96, 96); }, 10, 5, 9, 0.5, '0,0,0'); g = c.createLinearGradient(-48, -48, 48, 48); g.addColorStop(0, '#F8E680'); g.addColorStop(1, '#E9CE55'); c.fillStyle = g; c.fillRect(-48, -48, 96, 96);
  c.fillStyle = 'rgba(0,0,0,0.07)'; c.fillRect(-48, -48, 96, 14); c.strokeStyle = 'rgba(70,60,20,0.55)'; c.lineWidth = 3; c.lineCap = 'round'; for (const [yy, ww] of [[-14, 58], [2, 44], [18, 52]]) { c.beginPath(); c.moveTo(-30, yy); c.lineTo(-30 + ww, yy); c.stroke(); } c.restore();
  const cy = SCR.y + SCR.h + CHIN / 2 - 2;
  shadowed(c, cam, () => { g = c.createLinearGradient(110, cy - 17, 144, cy + 17); g.addColorStop(0, '#7FE3D0'); g.addColorStop(0.5, '#B79CF7'); g.addColorStop(1, '#F2A65A'); c.fillStyle = g; c.beginPath(); c.arc(127, cy, 17, 0, 7); c.fill(); }, 3, 1, 2, 0.5, '0,0,0'); c.strokeStyle = '#0B101D'; c.lineWidth = 2.6; c.lineCap = 'round'; c.lineJoin = 'round'; c.beginPath(); c.moveTo(121, cy - 6); c.lineTo(127, cy); c.lineTo(121, cy + 6); c.moveTo(129, cy + 7); c.lineTo(136, cy + 7); c.stroke();
  c.save(); c.translate(184, cy); c.rotate(rad(-7)); shadowed(c, cam, () => { c.fillStyle = '#EDE8DC'; rr(c, -24, -14, 48, 28, 6); c.fill(); }, 3, 1, 2, 0.5, '0,0,0'); c.fillStyle = C.err; for (const [hx, hy] of [[-9, -5], [-3, -5], [3, -5], [9, -5], [-9, 0], [-3, 0], [3, 0], [9, 0], [-6, 5], [0, 5], [6, 5], [0, 9]]) c.fillRect(hx - 3, hy - 3, 6, 5.5); c.restore();
  c.fillStyle = '#62C36A'; c.beginPath(); c.arc(1006, cy, 3, 0, 7); c.fill();
  // clavier mécanique (coupé par le bas du cadre)
  shadowed(c, cam, () => { c.fillStyle = '#2A2C32'; rr(c, O.clavier.x, O.clavier.y, 850, 330, 22); c.fill(); }, 30, 10, 18, 0.7, '0,0,0'); g = c.createLinearGradient(0, O.clavier.y, 0, O.clavier.y + 300); g.addColorStop(0, '#3A3D45'); g.addColorStop(0.06, '#2A2C32'); g.addColorStop(1, '#202227'); c.fillStyle = g; rr(c, O.clavier.x, O.clavier.y, 850, 330, 22); c.fill();
  const key = (kx, ky, kw, col, top) => { c.fillStyle = 'rgba(0,0,0,0.5)'; rr(c, kx, ky + 3, kw, 62, 9); c.fill(); c.fillStyle = col; rr(c, kx, ky, kw, 60, 9); c.fill(); c.fillStyle = top; rr(c, kx + 6, ky + 4, kw - 12, 46, 7); c.fill(); };
  const rows = [[62, 62, 62, 62, 62, 62, 62, 62, 62, 62, 62, 62], [94, 62, 62, 62, 62, 62, 62, 62, 62, 62, 62, 62], [112, 62, 62, 62, 62, 62, 62, 62, 62, 62, 62], [144, 62, 62, 62, 62, 62, 62, 62, 62, 62]];
  rows.forEach((r, ri) => { let kx = O.clavier.x + 46; r.forEach((kw, ki) => { const accent = ri === 0 && ki === 0, mod = ki === 0 && ri > 0; key(kx, O.clavier.y + 22 + ri * 70, kw, accent ? '#D9B02F' : mod ? '#5B606C' : '#C9C5BB', accent ? C.fresh : mod ? '#6C7280' : '#E4E0D6'); kx += kw + 8; }); });
  // canette vue de dessus (sans marque)
  c.save(); c.translate(O.canette.x, O.canette.y); shadowed(c, cam, () => { c.fillStyle = '#3FB8A0'; c.beginPath(); c.arc(0, 0, 86, 0, 7); c.fill(); }, 26, 14, 22, 0.7, '0,0,0');
  g = c.createLinearGradient(-86, -86, 86, 86); g.addColorStop(0, '#7FE3D0'); g.addColorStop(1, '#2A8F7C'); c.fillStyle = g; c.beginPath(); c.arc(0, 0, 86, 0, 7); c.fill();
  g = c.createLinearGradient(-74, -74, 74, 74); g.addColorStop(0, '#F4F6F7'); g.addColorStop(0.5, '#B9C0C4'); g.addColorStop(1, '#8C9499'); c.fillStyle = g; c.beginPath(); c.arc(0, 0, 76, 0, 7); c.fill();
  g = c.createLinearGradient(-60, -60, 60, 60); g.addColorStop(0, '#AEB5BA'); g.addColorStop(1, '#E6E9EB'); c.fillStyle = g; c.beginPath(); c.arc(0, 0, 64, 0, 7); c.fill();
  c.rotate(rad(38)); c.fillStyle = '#15171A'; c.beginPath(); c.ellipse(0, 34, 19, 22, 0, 0, 7); c.fill();
  g = c.createLinearGradient(-14, -40, 14, 16); g.addColorStop(0, '#F7F8F9'); g.addColorStop(1, '#9FA7AC'); c.fillStyle = g; rr(c, -13, -40, 26, 58, 12); c.fill();
  c.strokeStyle = '#8C9499'; c.lineWidth = 2.5; rr(c, -7, -33, 14, 20, 6); c.stroke(); c.fillStyle = '#7C858A'; c.beginPath(); c.arc(0, 4, 3.5, 0, 7); c.fill();
  c.restore();
}
const CLS = { kw: C.kw, str: C.str, num: C.num };
export const skin = {
  id: 'editeur', font: 'JetBrains Mono', weight: 700, wFinal: 800, cap: 0.55, gap: 0.3, em: [28, 46], trackMax: 0.04, dryCloseAlpha: 0.6, floorPx: 96,
  fonts: [{ family: 'JetBrains Mono', weight: 400, pkg: 'jetbrains-mono' }, { family: 'JetBrains Mono', weight: 700, pkg: 'jetbrains-mono' }, { family: 'JetBrains Mono', weight: 800, pkg: 'jetbrains-mono' }, { family: 'JetBrains Mono', weight: 400, style: 'italic', pkg: 'jetbrains-mono' }],
  col: { dry: C.plain, fresh: C.fresh, stroke: C.trait, ghost: '#8B98B8' }, ghostAlpha: 0.8, ghostWeight: 400, ghostStyle: 'italic ', ghostLead: 0.39,
  dryColor: u => CLS[u.cls] || C.plain, tip: () => {},
  prepare, floor, sheet, under, stroke, inkExtras, objects, finish: c => finish(c, 0.3, 0.05),
};
