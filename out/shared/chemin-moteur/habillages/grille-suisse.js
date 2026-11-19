// grille-suisse.js — habillage « grille-suisse » (pâte de l'identité swiss-data) pour la mécanique trace-chemin.
// Essai C2 de la composition (out/report/notes/composition/matrice.md) : premier habillage porté sur une 2ᵉ mécanique.
// Pâte reprise de out/identities/swiss-data/ (objet T de src/grille.js) : blanc cassé chaud #F4F1EA, grille visible de 12 colonnes,
// noir #111111, rouge #E3241B, bleu #1B4DE3 et rien d'autre ; Archivo Black pour les mots et les chiffres, Inter 800 pour les
// en-têtes de section (« 01 · MONDE », source à droite) sous un filet noir. Le mot dit s'écrit en rouge et sèche en noir.
// Décor du dessin (dessins/barres-humains.json) : filets de section (G.regles) et barres horizontales (G.barres) qui se
// remplissent de gauche à droite pendant que leur ligne s'écrit ; une barre peut passer au rouge à un instant donné (rougeA).
// Pointe : un petit carré rouge plein (le « carré » de l'unit chart de swiss-data). Pas de vignette ni de grain : aplat net.
// Le moteur chemin.js n'est pas modifié.
import { S, W, H } from '../outils.js';

const T = { bg: '#F4F1EA', ink: '#111111', red: '#E3241B', blue: '#1B4DE3', rule: '#D5CFC2', muted: '#6B665C' };
const CAP = 0.688, GAP = 0.20;   // Archivo Black : hauteur de capitale 0,688 em
const COLS = 12, GX = 96, GW = 888, GUT = 24;   // grille de 12 colonnes sur la largeur utile du dessin

function floor(c) { c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.fillStyle = T.bg; c.fillRect(0, 0, W, H); c.restore(); }
function sheet(c, cam, t, env) {
  c.fillStyle = T.bg; c.fillRect(-1600, -1600, W + 3200, H + 3200);
  // 12 colonnes : un filet clair de chaque côté de chaque gouttière, sur toute la hauteur
  const cw = (GW - GUT * (COLS - 1)) / COLS;
  c.fillStyle = 'rgba(17,17,17,0.055)';
  for (let k = 0; k < COLS; k++) { const x = GX + k * (cw + GUT); c.fillRect(x - 1, -1600, 2, H + 3200); c.fillRect(x + cw - 1, -1600, 2, H + 3200); }
  // filets de section et en-têtes
  for (const R of env.G.regles || []) {
    c.fillStyle = T.ink; c.fillRect(GX, R.y, GW, 4);
    c.font = "800 30px 'Inter'"; c.textBaseline = 'alphabetic';
    c.fillStyle = T.red; c.textAlign = 'left'; c.fillText(R.g, GX, R.y + 44);
    c.fillStyle = T.ink; c.textAlign = 'right'; c.fillText(R.d, GX + GW, R.y + 44); c.textAlign = 'left';
  }
}
const COL = { rouge: T.red, bleu: T.blue, noir: T.ink };
// sous l'encre : les barres, remplies au rythme de leur ligne (fin de remplissage 0,25 s après le dernier mot)
function under(c, cam, t, env) {
  for (const B of env.G.barres || []) {
    const L = env.LINES.find(X => X.id === B.arete); if (!L) continue;
    const k = S.ease.outCubic(S.clamp((t - L.tStart + 0.05) / (L.tEnd - L.tStart + 0.25))); if (k <= 0) continue;
    // fond de piste (comme le top 5 de swiss-data), puis la barre
    c.fillStyle = 'rgba(17,17,17,0.08)'; c.fillRect(B.x, B.y, GW, B.h);
    const rouge = B.rougeA != null ? S.clamp((t - B.rougeA) / 0.3) : 0;
    c.fillStyle = COL[B.col]; c.fillRect(B.x, B.y, B.w * k, B.h);
    if (rouge > 0) { c.fillStyle = T.red; c.fillRect(B.x, B.y, B.w * k * S.ease.outCubic(rouge), B.h); }
  }
}
function tip(c, L, tp, cam, t, env) {   // pointe : carré rouge plein qui suit l'écriture
  if (t > env.T_OUT0 + 0.2) return;
  const p = L.path.at(tp.d), em = L.emW, s = em * 0.42, off = -(GAP + CAP / 2) * em;
  c.save(); c.translate(p.x - Math.sin(p.a) * off, p.y + Math.cos(p.a) * off); c.rotate(p.a);
  c.fillStyle = T.red; c.fillRect(em * 0.12, -s / 2, s, s); c.restore();
}
const annotations = {
  // filet rouge épais sous une ligne
  souligne(c, L, A, k) { const p0 = L.path.at(L.d0); c.fillStyle = T.red; c.fillRect(p0.x, p0.y + 14, L.total * S.ease.outCubic(k), 10); },
};

export const habillage = {
  id: 'grille-suisse',
  fonts: [{ family: 'Archivo Black', weight: 400, pkg: 'archivo-black' }, { family: 'Inter', weight: 800, pkg: 'inter' }],
  font: 'Archivo Black', weight: 400, wFinal: 400, cap: CAP, gap: GAP,
  em: [36, 60], trackMax: 0.03, floorPx: 120, floorFast: 92, maxPx: 240, dryCloseAlpha: 0.75, lineWidth: 4,
  col: { fresh: T.red, dry: T.ink, stroke: T.ink, annot: T.red },
  ghost: { mode: 'wipe', alpha: 0.35 },
  floor, sheet, under, tip, annotations,
};
