// grille.js — système "Grille Suisse" (swiss-data), partagé par les deux shorts (copie identique dans chaque src/).
// D3 construit le SVG (échelles, grille 12 colonnes, textes) ; GSAP anime (timeline seekée par renderAt).
// Tokens : voir out/identities/swiss-data/tokens.json (valeurs identiques).
import * as S from '/out/tools/lib/svi.js';

export const T = {
  bg: '#F4F1EA', surface: '#FFFFFF', red: '#E3241B', ink: '#111111', blue: '#1B4DE3',
  muted: '#6B665C', rail: '#E7E2D7', gridLine: '#E2DDD2', ghost: '#B9B3A6',
  L: 72, R: 960, W: 888, col: 74,              // 12 colonnes de 74 px entre 72 et 960 (droite libre : 120 px)
  headerY: 232,                                 // filet noir 8 px juste sous la zone sûre haute (220)
  floorY: 1600,                                 // rien d'important sous 1600 (zone sûre basse 320)
  display: "'Archivo Black'", sans: 'Inter',
};
export const gx = d3.scaleLinear().domain([0, 12]).range([T.L, T.R]);

export const fontsReady = () => S.loadFonts([
  { family: 'Inter', pkg: 'inter', weight: 600 }, { family: 'Inter', pkg: 'inter', weight: 800 },
  { family: 'Archivo Black', pkg: 'archivo-black', weight: 400 }]);

export function txt(parent, x, y, s, size, { weight = 800, fill = T.ink, anchor = 'start', family = T.sans, track = null } = {}) {
  const fam = family === T.sans ? 'Inter' : family;
  const e = parent.append('text').attr('x', x).attr('y', y).attr('fill', fill).attr('text-anchor', anchor)
    .style('font', `${family === T.sans ? weight : 400} ${size}px ${fam}`).text(s);
  const tr = track ?? (size >= 200 ? -0.06 : size >= 90 ? -0.045 : -0.02);
  e.style('letter-spacing', `${tr}em`);
  return e;
}

// Fond, grille 12 colonnes, en-tête (filet + kicker + repère à droite). Retourne les nœuds variables.
export function frame(svg, { kicker, right }) {
  svg.append('rect').attr('width', 1080).attr('height', 1920).attr('fill', T.bg);
  const grid = svg.append('g').attr('id', 'grid');
  d3.range(13).forEach(i => grid.append('line').attr('x1', gx(i)).attr('x2', gx(i)).attr('y1', 0).attr('y2', 1920)
    .attr('stroke', T.gridLine).attr('stroke-width', 1.5));
  const head = svg.append('g').attr('id', 'head');
  const rule = head.append('rect').attr('x', T.L).attr('y', T.headerY).attr('width', T.W).attr('height', 8).attr('fill', T.ink);
  const k = txt(head, T.L, 306, kicker, 54, { fill: T.red, track: 0 });
  const r = txt(head, T.R, 306, right, 54, { weight: 600, anchor: 'end', track: 0 });
  return { grid, rule, kicker: k, right: r };
}

// Ligne de titre révélée par un masque (wipe horizontal outExpo) : renvoie {g, clip} — animer clip.width.
let clipId = 0;
export function wipeLine(parent, x, y, s, size, opts = {}) {
  const id = `c${clipId++}`;
  const cp = parent.append('clipPath').attr('id', id);
  const clip = cp.append('rect').attr('x', x - 20).attr('y', y - size * 1.05).attr('height', size * 1.35).attr('width', 0);
  const g = parent.append('g').attr('clip-path', `url(#${id})`);
  const t = txt(g, x, y, s, size, opts);
  return { g, t, clip: clip.node(), full: 1080 };
}

// Transition signature "volet rouge" : panneau rouge plein cadre qui balaie gauche -> droite (expo.inOut).
// cover : 0.45 s (x -1080 -> 0), coupe sous le volet, reveal : 0.45 s (0 -> 1080).
export function makeWipe(svg) {
  const g = svg.append('g').attr('id', 'wipe');
  const r = g.append('rect').attr('x', -1100).attr('y', 0).attr('width', 1100).attr('height', 1920).attr('fill', T.red);
  const bar = g.append('rect').attr('x', -1100).attr('y', 0).attr('width', 24).attr('height', 1920).attr('fill', T.ink);
  return { r: r.node(), bar: bar.node() };
}
export function addWipe(tl, w, at) {
  tl.fromTo(w.r, { attr: { x: -1100 } }, { attr: { x: -10 }, duration: 0.45, ease: 'expo.inOut', immediateRender: false }, at);
  tl.fromTo(w.bar, { attr: { x: -1100 } }, { attr: { x: -10 + 1076 }, duration: 0.45, ease: 'expo.inOut', immediateRender: false }, at);
  tl.to(w.r, { attr: { x: 1100 }, duration: 0.45, ease: 'expo.inOut', immediateRender: false }, at + 0.5);
  tl.to(w.bar, { attr: { x: 1100 + 1076 }, duration: 0.45, ease: 'expo.inOut', immediateRender: false }, at + 0.5);
  return at + 0.475; // instant de la coupe (volet couvrant)
}

// Affiche la scène active (coupes nettes sous le volet) : scenes = [{g, from, to}]
export function showScenes(scenes, t) {
  scenes.forEach(s => s.g.attr('display', t >= s.from && t < s.to ? null : 'none'));
}

export const fr = (v, d = 2) => d3.format(`.${d}f`)(v).replace('.', ',');
export { S };
