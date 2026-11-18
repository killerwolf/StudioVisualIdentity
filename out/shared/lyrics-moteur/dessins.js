// dessins.js — pictogrammes des cartons de Lyrics punchy (concept.md § 8), dessinés par code en SVG.
// Chaque fonction reçoit { lt (s depuis le début du carton), beat (durée d'un temps), pal (camaïeu), creme }
// et rend le contenu d'un <svg viewBox="0 0 500 500"> posé sur le carré couleur d'accent.
// Règle : 3 couleurs au plus (encre, crème, UNE couleur vraie), aplats, formes arrondies, lisible en 0,5 s. Aucune image.

export const VRAIES = { rouge: '#FF3B3B', vert: '#3DDC84', bleu: '#1F3FBF', blanc: '#F4F1EA', rougeDrapeau: '#E1262D' };

const FONT = `font-family:'Anybody Variable';font-weight:900;font-variation-settings:'wdth' 78,'wght' 900`;   // apostrophes : la valeur va dans style="…"
const ease = (k) => 1 - Math.pow(1 - Math.min(1, Math.max(0, k)), 3);
const rect = (x, y, w, h, f, r = 0, extra = '') => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${f}" ${extra}/>`;
const text = (x, y, s, size, f, extra = '') => `<text x="${x}" y="${y}" font-size="${size}" fill="${f}" style="${FONT}" ${extra}>${s}</text>`;
// « claque » d'un élément interne : échelle 1,7 -> 1 en 4 images autour de (cx, cy)
const slam = (lt, t0, cx, cy, amp = 0.7, frames = 4) => {
  if (lt < t0) return null;
  const k = Math.min(1, (lt - t0) * 30 / frames);
  const s = 1 + amp * Math.pow(1 - k, 3);
  return `transform="translate(${cx} ${cy}) scale(${s.toFixed(4)}) translate(${-cx} ${-cy})"`;
};

export const dessins = {
  // pastille « PLAN MODE » + liste de 3 lignes ; les 2 premières cases se cochent sur 2 temps
  planMode({ lt, beat, pal, creme }) {
    let s = rect(50, 54, 400, 96, pal.encre, 48) + text(250, 125, 'PLAN MODE', 62, creme, 'text-anchor="middle"');
    for (let i = 0; i < 3; i++) {
      const y = 200 + i * 86;
      s += rect(50, y, 56, 56, pal.encre, 10) + rect(134, y + 10, [300, 230, 270][i], 36, pal.encre, 8);
      const tc = (i + 1) * beat;                         // case i cochée sur le temps i+1
      if (i < 2 && lt >= tc) {
        const k = ease((lt - tc) * 30 / 3);
        const len = 60;
        s += `<polyline points="62,${y + 30} 76,${y + 44} 96,${y + 14}" fill="none" stroke="${creme}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="${len}" stroke-dashoffset="${(len * (1 - k)).toFixed(1)}"/>`;
      }
    }
    return s;
  },

  // 5 barres de texte qui se tapent une à une, une par croche, sans couleur de syntaxe ; curseur crème
  lignes({ lt, beat, pal, creme }) {
    const W = [330, 250, 300, 190, 270], X = [60, 60, 110, 110, 60];
    let s = '';
    const croche = beat / 2;
    let cur = null;
    for (let i = 0; i < 5; i++) {
      const y = 78 + i * 72;
      const k = Math.min(1, Math.max(0, (lt - i * croche) / croche));
      if (k <= 0) { if (cur === null) cur = { x: X[i], y }; continue; }
      const w = Math.round(W[i] * k / 20) * 20;          // tapé par blocs de 20 px (frappe, pas un glissé)
      s += rect(X[i], y, Math.max(20, w), 38, pal.encre, 8);
      if (k < 1) cur = { x: X[i] + w + 8, y };
    }
    if (!cur) cur = { x: X[4] + W[4] + 8, y: 78 + 4 * 72 };
    if (Math.floor(lt / croche) % 2 === 0 || lt < 5 * croche) s += rect(cur.x, cur.y - 4, 18, 46, creme, 3);
    return s;
  },

  // étiquette « v2.0 » (encre, œillet), puis tampon rouge « RELEASE » qui tombe en coup sur le 2e temps
  version({ lt, beat, pal, creme }) {
    let s = `<path d="M70 150 L330 150 L430 250 L330 350 L70 350 Q50 350 50 330 L50 170 Q50 150 70 150 Z" fill="${pal.encre}"/>`;
    s += `<circle cx="340" cy="250" r="20" fill="${pal.accent}"/>`;
    s += text(80, 292, 'v2.0', 130, creme);
    const t1 = 2 * beat;
    const tr = slam(lt, t1, 250, 410);
    if (tr) {
      s += `<g ${tr}><g transform="rotate(-8 250 410)">${rect(110, 370, 280, 84, 'none', 12, `stroke="${VRAIES.rouge}" stroke-width="10"`)}`
        + text(250, 432, 'RELEASE', 56, VRAIES.rouge, 'text-anchor="middle"') + '</g></g>';
    }
    return s;
  },

  // baie de 3 tiroirs ; sur le temps suivant la diode du milieu passe au rouge, « 503 » et la croix tombent
  serveurPanne({ lt, beat, pal, creme }) {
    const panne = lt >= beat;
    let s = '';
    for (let i = 0; i < 3; i++) {
      const y = 70 + i * 104;
      s += rect(60, y, 380, 84, pal.encre, 14);
      if (!(i === 1 && panne)) for (let j = 0; j < 3; j++) s += rect(250 + j * 56, y + 30, 40, 24, creme, 6);   // tiroir en panne : voyants éteints
      const col = (i === 1 && panne) ? VRAIES.rouge : creme;
      s += `<circle cx="110" cy="${y + 42}" r="18" fill="${col}"/>`;
    }
    if (panne) {
      const tr = slam(lt, beat, 250, 420) || '';
      s += `<g ${tr}>` + text(60, 455, '503', 84, pal.encre)
        + `<path d="M300 395 L370 455 M370 395 L300 455" stroke="${VRAIES.rouge}" stroke-width="18" stroke-linecap="round"/></g>`;
    }
    return s;
  },

  // une clé et une chaîne masquée « sk-•••••• » dont les points s'ajoutent un par croche
  clesApi({ lt, beat, pal, creme }) {
    let s = `<circle cx="140" cy="150" r="82" fill="${pal.encre}"/><circle cx="140" cy="150" r="32" fill="${pal.accent}"/>`;
    s += rect(200, 128, 230, 44, pal.encre, 10) + rect(350, 160, 30, 50, pal.encre, 6) + rect(400, 160, 30, 66, pal.encre, 6);
    s += rect(50, 300, 400, 110, pal.encre, 22) + text(78, 378, 'SK-', 64, creme);
    const n = Math.min(6, 1 + Math.floor(lt / (beat / 2)));
    for (let i = 0; i < n; i++) s += `<circle cx="${210 + i * 38}" cy="356" r="13" fill="${VRAIES.rouge}"/>`;
    return s;
  },
};

// carton générique quand la fonction de dessin manque encore : le mot déclencheur en encre
export function dessinManquant({ mot, pal }) {
  return text(250, 280, mot, 64, pal.encre, 'text-anchor="middle"');
}
