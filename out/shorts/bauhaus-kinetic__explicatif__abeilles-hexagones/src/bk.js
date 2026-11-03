/**
 * bk.js — noyau de l'identité « Bauhaus Cinétique » (bauhaus-kinetic), partagé par les deux shorts.
 * Tokens (couleurs, grille 6×10, easings), géométrie (hexagones, carrés, cercles en points pour flubber),
 * fond-grille Paper.js et transition « grid-wipe » (6 colonnes colorées en DOM, au-dessus du texte).
 * Toutes les animations sont pilotées par une timeline anime.js v4 en pause, seekée dans renderAt(t).
 */
export const C = { bg: '#F2EDE3', surface: '#FFFFFF', red: '#E63B2E', yel: '#F5B700', blue: '#1D4ED8', ink: '#111111', muted: '#6B6458', white: '#FFFFFF' };
export const ACC = [C.red, C.yel, C.blue, C.ink];
export const CW = 180, CH = 192;                 // grille 6 × 10 sur 1080 × 1920
export const EASE = { enter: 'outBack(1.6)', exit: 'inQuart', emphasis: 'inOutQuart', wipe: 'inOutQuart' };
export const DUR = { fast: 280, base: 450, slow: 900 };
export const STAGGER = 60;                        // ms entre éléments d'une grille
export const FONTS = [{ family: 'Unbounded', pkg: 'unbounded', weight: 800 }, { family: 'Space Grotesk', pkg: 'space-grotesk', weight: 500 }];

// ---- géométrie (points [x,y]) ----
export const hexPts = (cx, cy, r, rot = 0) => Array.from({ length: 6 }, (_, i) => { const a = Math.PI / 180 * (60 * i - 90) + rot; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; });
export const polyPts = (cx, cy, r, n, rot = 0) => Array.from({ length: n }, (_, i) => { const a = 2 * Math.PI * i / n - Math.PI / 2 + rot; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; });
export const circlePts = (cx, cy, r, n = 72) => Array.from({ length: n }, (_, i) => { const a = 2 * Math.PI * i / n - Math.PI / 2; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; });
export const sqPts = (cx, cy, s) => [[cx - s, cy - s], [cx + s, cy - s], [cx + s, cy + s], [cx - s, cy + s]];
export const toD = pts => 'M' + pts.map(p => p.map(v => v.toFixed(2)).join(',')).join('L') + 'Z';

/** Paper path fermé depuis une liste de points */
export function poly(P, pts, fill, stroke, sw = 0) {
  const p = new P.Path({ segments: pts, closed: true });
  if (fill) p.fillColor = fill;
  if (stroke) { p.strokeColor = stroke; p.strokeWidth = sw; p.strokeJoin = 'miter'; }
  return p;
}

/** fond : grille 6×10 qui se « dessine » (k 0..1) */
export function drawGrid(P, k = 1, op = 0.09) {
  for (let i = 1; i < 6; i++) { const l = new P.Path.Line([i * CW, 0], [i * CW, 1920 * k]); l.strokeColor = C.ink; l.opacity = op; l.strokeWidth = 2; }
  for (let j = 1; j < 10; j++) { const l = new P.Path.Line([0, j * CH], [1080 * k, j * CH]); l.strokeColor = C.ink; l.opacity = op; l.strokeWidth = 2; }
}

/** transition grid-wipe : 6 colonnes (rouge/jaune/bleu/noir…) tombent en stagger, couvrent, puis repartent vers le bas.
 *  Elle se pose sur la timeline à `at` (ms) ; la coupe de scène doit être faite à at + WIPE_COVER. */
export const WIPE_IN = 300, WIPE_STAG = 45, WIPE_COVER = WIPE_IN + 5 * WIPE_STAG, WIPE_TOTAL = WIPE_COVER + WIPE_IN + 5 * WIPE_STAG;
export function makeWipe(root) {
  const cols = [C.red, C.yel, C.blue, C.ink, C.red, C.yel];
  const els = cols.map((c, i) => { const d = document.createElement('div'); d.style.cssText = `position:absolute;left:${i * CW}px;top:0;width:${CW + 1}px;height:1920px;background:${c};z-index:50;transform:translateY(-1920px)`; root.appendChild(d); return d; });
  const st = cols.map(() => ({ y: -1920 }));
  return {
    st, els,
    add(tl, at) {
      tl.add(st, { y: [-1920, 0], duration: WIPE_IN, ease: EASE.wipe, delay: (_, i) => i * WIPE_STAG }, at)
        .add(st, { y: [0, 1920], duration: WIPE_IN, ease: EASE.wipe, delay: (_, i) => i * WIPE_STAG }, at + WIPE_COVER);
    },
    apply() { st.forEach((s, i) => { els[i].style.transform = `translateY(${s.y.toFixed(1)}px)`; }); },
  };
}

/** applique {o, y, s, r} d'un objet animé à un élément DOM */
export function css(el, o) {
  el.style.opacity = o.o ?? 1;
  el.style.transform = `translate(${(o.x ?? 0).toFixed(1)}px,${(o.y ?? 0).toFixed(1)}px) scale(${(o.s ?? 1).toFixed(4)}) rotate(${(o.r ?? 0).toFixed(2)}deg)`;
}
