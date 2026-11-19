// editeur.js — habillage « éditeur de code » de lyrics-chemin (déclinaison B, « Claude's Plan » version tech).
// Un éditeur sombre sur un écran vertical posé sur un tapis de bureau, vu de dessus avec le clavier et une canette.
// Mot chanté en jaune, encre sèche en coloration syntaxique (classe de l'unité : kw, str, num), pré-posé = texte fantôme
// d'une suggestion (italique gris), pointe = curseur bloc qui clignote sur le temps, annotations rouges = idiomes d'éditeur
// (✗ d'un contrôle en échec, soulignement ondulé). Décor sans aucun mot : barre de titre, gouttière de numéros, barre d'état.
// Dessin associé : cargo (conteneurs, château, mât, fanion, ligne de flottaison, panneaux d'interface lus dans dessins/cargo.json).
// Maquette d'origine : out/report/notes/lyrics-chemin/declinaisons/proto/cargo.js (Fable).
import { S, W, H, rad, noiseTile, shadowed, rr, strokePath } from '../outils.js';

const C = { bg0: '#141B30', bg1: '#0B101D', bar: '#182037', plain: '#D5DCEA', kw: '#B79CF7', str: '#93D8A0', num: '#F2A65A', com: '#66769A', trait: '#8497C4',
  fresh: '#FFD84A', err: '#FF6B5E', desk: '#16171B', bezel: '#0A0B0E', ghost: '#8B98B8' };
const BZ = 14, CHIN = 52, CAP = 0.55, GAP = 0.3;
const CLS = { kw: C.kw, str: C.str, num: C.num, com: C.com, err: C.err };
let PAT = {};
function prepare() {
  PAT.felt = noiseTile(256, 41, (i, j, r) => { const v = r(); return [255, v > 0.6 ? 10 : 0]; });
  PAT.grain = noiseTile(256, 77, (i, j, r) => { const v = r() * 255; return [v, 255]; });
}
const mono = (c, px, wgt = 400, st = '') => { c.font = `${st}${wgt} ${px}px 'JetBrains Mono'`; c.letterSpacing = '0px'; };
const bars = (c, x, y, ws, h = 7, col = 'rgba(160,175,210,0.28)') => { c.fillStyle = col; let cx = x; for (const w of ws) { rr(c, cx, y, w, h, h / 2); c.fill(); cx += w + 8; } };

function floor(c) { c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.fillStyle = C.desk; c.fillRect(0, 0, W, H); c.restore(); }
function sheet(c, cam, t, env) {
  const { x, y, w, h } = env.G.feuille;
  // tapis de bureau feutré (attaché au monde)
  c.fillStyle = C.desk; c.fillRect(-1400, -1400, W + 2800, H + 2800); c.save(); c.fillStyle = c.createPattern(PAT.felt, 'repeat'); c.fillRect(-1400, -1400, W + 2800, H + 2800); c.restore();
  // écran : coque, dalle
  shadowed(c, cam, () => { c.fillStyle = C.bezel; rr(c, x - BZ, y - BZ, w + 2 * BZ, h + BZ + CHIN, 30); c.fill(); }, 34, 10, 20, 0.7, '0,0,0');
  let g = c.createLinearGradient(x, y - BZ, x, y + h + CHIN); g.addColorStop(0, '#1A1C22'); g.addColorStop(0.04, '#0C0D10'); g.addColorStop(1, '#0A0B0E'); c.fillStyle = g; rr(c, x - BZ, y - BZ, w + 2 * BZ, h + BZ + CHIN, 30); c.fill();
  c.strokeStyle = 'rgba(255,255,255,0.10)'; c.lineWidth = 1.2; rr(c, x - BZ + 0.6, y - BZ + 0.6, w + 2 * BZ - 1.2, h + BZ + CHIN - 1.2, 30); c.stroke();
  c.save(); rr(c, x, y, w, h, 16); c.clip();
  g = c.createLinearGradient(x, y, x + w, y + h); g.addColorStop(0, C.bg0); g.addColorStop(1, C.bg1); c.fillStyle = g; c.fillRect(x, y, w, h);
  g = c.createRadialGradient(360, 520, 60, 360, 520, 900); g.addColorStop(0, 'rgba(90,110,200,0.10)'); g.addColorStop(1, 'rgba(90,110,200,0)'); c.fillStyle = g; c.fillRect(x, y, w, h);
  // grille de points (l'équivalent du quadrillage) : 20 px, croix tous les 100 px ; seulement la partie visible
  const a20 = S.lerp(0.10, 0.16, S.clamp((cam.s - 1) / 2)), rdot = Math.max(0.9, 1.5 / Math.sqrt(cam.s));
  const vr = 1100 / cam.s, gx0 = Math.max(100, Math.floor((cam.x - vr) / 20) * 20), gx1 = Math.min(x + w, cam.x + vr), gy0 = Math.max(180, Math.floor((cam.y - vr) / 20) * 20), gy1 = Math.min(y + h, cam.y + vr);
  c.fillStyle = `rgba(150,170,225,${a20})`; c.beginPath(); for (let gy = gy0; gy < gy1; gy += 20) for (let gx = gx0; gx < gx1; gx += 20) { if (gx % 100 === 0 && gy % 100 === 0) continue; c.rect(gx - rdot / 2, gy - rdot / 2, rdot, rdot); } c.fill();
  c.strokeStyle = 'rgba(150,170,225,0.30)'; c.lineWidth = Math.max(0.6, 1 / Math.sqrt(cam.s)); c.beginPath(); for (let gy = 200; gy < y + h; gy += 100) for (let gx = 100; gx < x + w; gx += 100) { c.moveTo(gx - 4, gy); c.lineTo(gx + 4, gy); c.moveTo(gx, gy - 4); c.lineTo(gx, gy + 4); } c.stroke();
  // gouttière : numéros de ligne (seul texte de décor, équivalent du « PL. 01 — 1:1 »)
  c.fillStyle = 'rgba(11,15,28,0.55)'; c.fillRect(x, y, 44, h); mono(c, 11); c.textAlign = 'right'; c.fillStyle = 'rgba(102,118,154,0.75)'; for (let i = 1, gy = 200; gy < y + h - 40; gy += 20, i++) c.fillText(String(i), x + 34, gy + 4); c.textAlign = 'left';
  // barre de titre : pastilles, onglet, pastille « mode » (▶▶)
  c.fillStyle = C.bar; c.fillRect(x, y, w, 54); c.fillStyle = 'rgba(255,255,255,0.05)'; c.fillRect(x, y + 53, w, 1);
  ['#E0655C', '#E2B24C', '#62C36A'].forEach((col, i) => { c.fillStyle = col; c.globalAlpha = 0.85; c.beginPath(); c.arc(x + 30 + i * 24, y + 27, 7, 0, 7); c.fill(); }); c.globalAlpha = 1;
  c.fillStyle = C.bg0; rr(c, x + 112, y + 10, 250, 44, [10, 10, 0, 0]); c.fill(); c.fillStyle = C.str; rr(c, x + 128, y + 22, 13, 17, 2); c.fill(); bars(c, x + 152, y + 27, [96, 42]); c.fillStyle = C.fresh; c.beginPath(); c.arc(x + 340, y + 31, 4, 0, 7); c.fill();
  bars(c, x + 384, y + 27, [80, 30], 7, 'rgba(160,175,210,0.16)');
  c.strokeStyle = C.kw; c.lineWidth = 1.5; rr(c, x + w - 206, y + 13, 180, 28, 14); c.stroke(); c.fillStyle = C.kw; for (const dx of [0, 11]) { c.beginPath(); c.moveTo(x + w - 190 + dx, y + 20); c.lineTo(x + w - 181 + dx, y + 27); c.lineTo(x + w - 190 + dx, y + 34); c.closePath(); c.fill(); } bars(c, x + w - 160, y + 24, [70, 34], 7, 'rgba(183,156,247,0.55)');
  // barre d'état
  c.fillStyle = C.bar; c.fillRect(x, y + h - 30, w, 30); bars(c, x + 20, y + h - 19, [60, 24, 90], 7, 'rgba(160,175,210,0.22)'); bars(c, x + w - 250, y + h - 19, [40, 70, 30, 44], 7, 'rgba(160,175,210,0.22)'); c.fillStyle = C.str; c.beginPath(); c.arc(x + w - 268, y + h - 15, 4, 0, 7); c.fill();
  c.restore();
}

// conteneur : contour tracé de gauche à droite avec la ligne, ondulations aux deux bouts, numéros de ligne (décor)
function box(c, b, kk) {
  const col = CLS[b.couleur] || C.com, ROWH = b.h;
  c.save(); if (b.rot) { c.translate(b.x, b.y + ROWH); c.rotate(rad(b.rot)); c.translate(-b.x, -(b.y + ROWH)); }
  const w = b.w * kk; c.globalAlpha = 0.09; c.fillStyle = col; rr(c, b.x, b.y, w, ROWH, 5); c.fill(); c.globalAlpha = 1;
  c.strokeStyle = col; c.lineWidth = 2.4; c.globalAlpha = b.id ? 0.9 : 0.5; rr(c, b.x, b.y, w, ROWH, 5); c.stroke();
  c.globalAlpha = b.id ? 0.30 : 0.22; c.lineWidth = 1.4; c.beginPath(); for (let gx = b.x + 8; gx < b.x + w - 4; gx += 9) { if (b.id && gx > b.x + 22 && gx < b.x + b.w - 22) continue; c.moveTo(gx, b.y + 7); c.lineTo(gx, b.y + ROWH - 7); } c.stroke();
  if (!b.id && kk >= 1) { c.globalAlpha = 1; for (let i = 0, n = Math.max(1, Math.round(ROWH / 60)); i < n; i++) bars(c, b.x + 16, b.y + ROWH * (i + 0.5) / n - 4, [Math.max(16, b.w - 34)], 8, 'rgba(102,118,154,0.45)'); }
  if (b.rangs && kk > 0.1) { c.globalAlpha = 0.9; mono(c, 13); c.fillStyle = C.com; for (const [, n, y] of b.rangs) c.fillText(n, b.x + 22, y + 5); }
  c.restore();
}
function under(c, cam, t, env) {
  const G = env.G, P = G.points, T = G.tour, L = id => env.lineOf(id), first = L => L.tStart;
  // coque (aplat discret) : visible quand le flanc droit est fini
  const kh = S.clamp((t - first(L('coqueD')) - 1.2) / 0.6); if (kh > 0) { c.fillStyle = `rgba(132,151,196,${0.06 * kh})`; c.beginPath(); c.moveTo(...P.L); c.lineTo(...P.BL); c.lineTo(...P.BR); c.lineTo(...P.R); c.closePath(); c.fill(); }
  // pont : tracé avec le premier conteneur ; château : avec le troisième ; mât et fanion : avec la ligne isolée
  const kd = S.clamp((t - first(L('c1a')) + 0.25) / 0.5); if (kd > 0) { c.strokeStyle = C.trait; c.lineWidth = 3.2; c.lineCap = 'round'; c.beginPath(); c.moveTo(...P.L); c.lineTo(P.L[0] + (P.R[0] - P.L[0]) * kd, P.L[1]); c.stroke(); }
  const kt = S.clamp((t - first(L('c3a')) + 0.4) / 0.6); if (kt > 0) { c.strokeStyle = C.trait; c.lineWidth = 2.8; c.fillStyle = 'rgba(132,151,196,0.07)'; rr(c, T.x, T.y + T.h * (1 - kt), T.w, T.h * kt, [6, 6, 0, 0]); c.fill(); c.stroke();
    if (kt >= 1) { for (let i = 0; i < 4; i++) { c.fillStyle = i === 0 ? 'rgba(255,216,74,0.55)' : 'rgba(132,151,196,0.35)'; rr(c, T.x + 12, T.y + 16 + i * 30, T.w - 24, 12, 3); c.fill(); } } }
  const Lf = L('fanion'), km = S.clamp((t - first(Lf) + 0.45) / 0.4); if (km > 0) { c.strokeStyle = C.trait; c.lineWidth = 2.8; c.lineCap = 'round'; c.beginPath(); c.moveTo(T.mat[0], T.y); c.lineTo(T.mat[0], T.y + (T.mat[1] - T.y) * km); c.stroke();
    if (km >= 1) { const kf = S.clamp((t - first(Lf) + 0.3) / 0.6), yF = Lf.path.at(0).y, y0 = yF - 34, y1 = yF + 24, ym = (y0 + y1) / 2;   // fanion accroché à la mise en page : il s'allonge avec le texte
      const fw = Lf.path.at(Lf.d0).x + Lf.total + 46 - T.mat[0];
      c.strokeStyle = C.err; c.lineWidth = 2.6; c.lineJoin = 'round'; c.beginPath(); c.moveTo(T.mat[0], y0); c.lineTo(T.mat[0] + fw * kf, y0); if (kf >= 1) { c.lineTo(T.mat[0] + fw - 24, ym); c.lineTo(T.mat[0] + fw, y1); c.lineTo(T.mat[0], y1); } c.stroke(); } }
  // conteneurs : tracés pendant l'écriture de leur ligne ; conteneurs de décor : à la fin de la ligne voisine
  for (const b of G.boites) {
    let kk;
    if (b.id) { const La = L(b.rangs[0][0]), Lb = L(b.rangs.at(-1)[0]), t0 = La.tStart - 0.25; kk = S.clamp((t - t0) / Math.max(0.4, (Lb.tEnd - La.tStart) * 0.8)); }
    else { const Ld = L(b.decor); kk = S.clamp((t - Ld.tEnd + 0.2) / 0.4); }
    if (kk > 0) box(c, b, S.ease.outCubic(kk));
  }
  // ligne de flottaison (décor), une fois la coque fermée
  if (kh > 0) { const F = G.flottaison; c.globalAlpha = kh; c.strokeStyle = 'rgba(132,151,196,0.5)'; c.lineWidth = 1.6; c.setLineDash([10, 9]); c.beginPath(); c.moveTo(F.x0, F.y); c.lineTo(F.x1, F.y); c.stroke(); c.setLineDash([]); c.globalAlpha = 1; }
  // suite de la première vague, sans texte
  const V = L('vague1'), kv = S.clamp((t - V.tEnd) / 0.5); if (kv > 0) { const ch = V.chemin, sv = G.suiteVague1; c.strokeStyle = C.trait; c.lineWidth = 3.2; c.lineCap = 'round'; c.beginPath();
    for (let wx = sv.x0; wx <= sv.x0 + (sv.x1 - sv.x0) * kv; wx += 4) { const wy = ch.y + ch.amp * Math.sin(ch.ph + (wx - ch.x0) / ch.wl * 2 * Math.PI); wx === sv.x0 ? c.moveTo(wx, wy) : c.lineTo(wx, wy); } c.stroke(); }
  // invites « > » des rangs finaux (sortie de terminal)
  for (let i = 0; i < env.SEA.length; i++) { const R = env.SEA[i]; if (t >= R.t0 - 0.1 && (i === 0 || R.row !== env.SEA[i - 1].row)) { mono(c, env.SEA_EM * 0.8, 700); c.fillStyle = C.com; c.fillText('>', G.final.invite, R.y); } }
}

// annotations rouges (jamais du texte)
const annotations = {
  // ✗ d'un contrôle en échec, de l'autre côté du trait que le texte, après la fin de l'unité
  x(c, L, A, k) { const u = L.units[A.unite || 0], p = L.path.at(u.d1 + 30), em = L.emW, side = L.below ? 1 : -1, off = em * 0.75 * side;
    c.translate(p.x + Math.sin(p.a) * off, p.y - Math.cos(p.a) * off); c.rotate(p.a); c.strokeStyle = C.err; c.lineWidth = 4; c.lineCap = 'round'; const s = 9 + em * 0.05;
    const k1 = Math.min(1, k * 2), k2 = S.clamp(k * 2 - 1); c.beginPath(); c.moveTo(-s, -s); c.lineTo(-s + 2 * s * k1, -s + 2 * s * k1); if (k2 > 0) { c.moveTo(s, -s); c.lineTo(s - 2 * s * k2, -s + 2 * s * k2); } c.stroke(); },
  // soulignement ondulé d'une erreur, sous tout le texte de la ligne
  ondule(c, L, A, k) { const d0 = L.d0, d1 = d0 + L.total * k, off = (L.inside ? CAP / 2 : 0) * L.emW + L.emW * 0.22; c.strokeStyle = C.err; c.lineWidth = 3; c.lineJoin = 'round'; c.beginPath();
    for (let d = d0, i = 0; d <= d1; d += 7, i++) { const p = L.path.at(d), o = off + (i % 2 ? 5 : 0), px = p.x - Math.sin(p.a) * o, py = p.y + Math.cos(p.a) * o; i ? c.lineTo(px, py) : c.moveTo(px, py); } c.stroke(); },
};

function panel(c, cam, x, y, w, h, k, fn) {   // panneau flottant (notification, pastille) : apparaît en 0,15 s
  if (k <= 0) return; c.save(); c.globalAlpha = k; c.translate(x + w / 2, y + h / 2); const sc = 0.9 + 0.1 * k; c.scale(sc, sc); c.translate(-x - w / 2, -y - h / 2);
  shadowed(c, cam, () => { c.fillStyle = '#1C2640'; rr(c, x, y, w, h, 10); c.fill(); }, 14, 6, 10, 0.55, '0,0,0'); c.strokeStyle = 'rgba(150,170,225,0.28)'; c.lineWidth = 1.2; rr(c, x + 0.6, y + 0.6, w - 1.2, h - 1.2, 10); c.stroke(); fn(); c.restore(); }
function cursor(c, cam, t, env) {   // curseur bloc à la pointe : plein pendant la frappe, clignote sur le temps au repos
  const LINES = env.LINES, beat = env.BEAT;
  let L = null, d = null, writing = false, em, off = 0;
  if (t < env.T_OUT0 + 0.2) {
    for (const X of LINES) if (X.tStart - 0.08 <= t) L = X;
    if (!L) L = LINES[0];
    const tp = env.tipOf(L, t); d = tp ? tp.d : L.units[0].d0; writing = tp ? tp.writing : false; em = L.emW;
    off = L.inside ? 0 : L.below ? (0.85 - CAP / 2) * em : -(GAP + CAP / 2) * em;
    const wd = L.words.find(w => d >= w.d0 - 1 && d <= w.d0 + w.w + 1);   // caler sur la frappe : après le dernier caractère tapé
    if (wd) { const cw = wd.w / wd.txt.length; d = wd.d0 + Math.min(wd.txt.length, Math.floor((d - wd.d0) / cw + 1e-6)) * cw; }
  } else {
    let R = null; for (const X of env.SEA) if (X.t0 - 0.08 <= t) R = X; if (!R) return;
    const wdur = Math.min(0.5 * (R.t1 - R.t0), 0.3), f = S.clamp((t - (R.t0 - 0.08)) / wdur); writing = f < 1; em = env.SEA_EM;
    L = { path: R.path }; d = R.d0 + (R.d1 - R.d0) * f; off = -CAP / 2 * em;
  }
  const on = writing || Math.floor(t / beat) % 2 === 0; if (!on) return;
  const p = L.path.at(d); c.save(); c.translate(p.x - Math.sin(p.a) * off, p.y + Math.cos(p.a) * off); c.rotate(p.a); c.fillStyle = C.fresh; c.globalAlpha = 0.92; c.fillRect(em * 0.08, -em * 0.62, em * 0.56, em * 1.18); c.restore();
}
function objects(c, cam, t, env) {
  const G = env.G, U = G.ui, O = G.objets, SCR = G.feuille; let g;
  const tU = k => { const L = env.lineOf(U[k].ligne); return L.units[U[k].unite].t + U[k].decalage; }, kp = k => S.clamp((t - tU(k)) / 0.15);
  // objets d'interface croisés en route (aucun mot dessus) : notification d'échec, pastille « clé », onglet de fichier
  { const T = U.toast; panel(c, cam, T.x, T.y, 178, 56, kp('toast'), () => { c.fillStyle = C.err; c.beginPath(); c.arc(T.x + 28, T.y + 28, 12, 0, 7); c.fill(); c.strokeStyle = '#1C2640'; c.lineWidth = 3; c.lineCap = 'round'; c.beginPath(); c.moveTo(T.x + 23, T.y + 23); c.lineTo(T.x + 33, T.y + 33); c.moveTo(T.x + 33, T.y + 23); c.lineTo(T.x + 23, T.y + 33); c.stroke(); bars(c, T.x + 52, T.y + 17, [96], 8, 'rgba(213,220,234,0.55)'); bars(c, T.x + 52, T.y + 33, [50, 34], 6, 'rgba(160,175,210,0.3)'); }); }
  { const K = U.cle; panel(c, cam, K.x, K.y, 138, 44, kp('cle'), () => { c.strokeStyle = C.num; c.fillStyle = C.num; c.lineWidth = 3.2; c.beginPath(); c.arc(K.x + 24, K.y + 22, 7, 0, 7); c.stroke(); c.beginPath(); c.moveTo(K.x + 31, K.y + 22); c.lineTo(K.x + 54, K.y + 22); c.moveTo(K.x + 46, K.y + 22); c.lineTo(K.x + 46, K.y + 29); c.moveTo(K.x + 53, K.y + 22); c.lineTo(K.x + 53, K.y + 28); c.stroke(); for (let i = 0; i < 5; i++) { c.globalAlpha *= 0.7; c.beginPath(); c.arc(K.x + 72 + i * 12, K.y + 22, 3.2, 0, 7); c.fill(); c.globalAlpha /= 0.7; } }); }
  { const F = U.fichier; panel(c, cam, F.x, F.y, 128, 50, kp('fichier'), () => { c.fillStyle = C.str; c.beginPath(); c.moveTo(F.x + 16, F.y + 11); c.lineTo(F.x + 30, F.y + 11); c.lineTo(F.x + 38, F.y + 19); c.lineTo(F.x + 38, F.y + 39); c.lineTo(F.x + 16, F.y + 39); c.closePath(); c.fill(); c.fillStyle = '#1C2640'; c.fillRect(F.x + 20, F.y + 24, 14, 2.5); c.fillRect(F.x + 20, F.y + 30, 10, 2.5); bars(c, F.x + 50, F.y + 21, [58], 8, 'rgba(147,216,160,0.6)'); }); }
  cursor(c, cam, t, env);
  // objets physiques autour de l'écran : note collée, autocollants, clavier mécanique, canette (aucune marque)
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
function finish(c) {   // vignette douce + grain fixe très léger
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
  const g = c.createRadialGradient(W / 2, H / 2, 620, W / 2, H / 2, 1250); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.3)'); c.fillStyle = g; c.fillRect(0, 0, W, H);
  c.globalAlpha = 0.05; c.globalCompositeOperation = 'overlay'; c.fillStyle = c.createPattern(PAT.grain, 'repeat'); c.fillRect(0, 0, W, H); c.restore();
}

export const habillage = {
  id: 'editeur',
  fonts: [{ family: 'JetBrains Mono', weight: 400, pkg: 'jetbrains-mono' }, { family: 'JetBrains Mono', weight: 700, pkg: 'jetbrains-mono' },
    { family: 'JetBrains Mono', weight: 800, pkg: 'jetbrains-mono' }, { family: 'JetBrains Mono', weight: 400, style: 'italic', pkg: 'jetbrains-mono' }],
  font: 'JetBrains Mono', weight: 700, wFinal: 800, cap: CAP, gap: GAP,   // minuscules : œil 0,55 em ; texte posé 0,3 em au-dessus du trait
  em: [28, 46], trackMax: 0.04, floorPx: 96, floorFast: 80, maxPx: 220, dryCloseAlpha: 0.6, typed: true,
  col: { fresh: C.fresh, dry: C.plain, stroke: C.trait, annot: C.err },
  dryColor: u => CLS[u.cls],
  ghost: { mode: 'fade', color: C.ghost, alpha: 0.8, weight: 400, style: 'italic ' },   // suggestion d'assistant, acceptée à l'attaque
  prepare, floor, sheet, under, annotations, objects, finish,
};
