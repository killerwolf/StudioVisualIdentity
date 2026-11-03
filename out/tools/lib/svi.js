/**
 * svi.js — helpers partagés pour les scènes (module ES). Import :
 *   import * as S from '/out/tools/lib/svi.js';
 *
 * - S.W, S.H, S.FPS, S.SAFE            : format 1080×1920, zones sûres TikTok {top:220,bottom:320,right:120,left:60}
 * - S.rng(seed)                        : PRNG mulberry32 déterministe -> () => [0,1)
 * - S.noise2(x,y) / S.noise3(x,y,z)    : value-noise déterministe lissé (pas de dépendance)
 * - S.ease.<nom>(x)                    : easings nommés (inOutCubic, outBack, outExpo, inOutSine, outElastic, …)
 * - S.cubicBezier(x1,y1,x2,y2)         : renvoie une fonction d'easing identique à CSS cubic-bezier
 * - S.seg(t,a,b,ease?)                 : progression 0..1 de t dans [a,b] (clampée, easée)
 * - S.lerp, S.clamp, S.smoothstep, S.mix(colorA,colorB,k)
 * - S.loadFonts([{family:'Inter', weight:700, pkg:'inter'}]) : injecte @font-face @fontsource + attend
 * - S.guides()                         : si l'URL contient ?guides=1, superpose les zones sûres (debug stills)
 * - S.installContract({renderAt, ready, sequential, duration}) : pose window.renderAt etc. proprement
 */
export const W = 1080, H = 1920, FPS = 30;
export const SAFE = { top: 220, bottom: 320, right: 120, left: 60 };

export function rng(seed = 1) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function hash3(x, y, z) {
  let h = (x * 374761393 + y * 668265263 + z * 2147483647) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}
const fade = t => t * t * t * (t * (t * 6 - 15) + 10);
export function noise3(x, y, z = 0) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  const xf = fade(x - xi), yf = fade(y - yi), zf = fade(z - zi);
  const L = (a, b, k) => a + (b - a) * k;
  const c = (i, j, k) => hash3(xi + i, yi + j, zi + k);
  return L(L(L(c(0,0,0), c(1,0,0), xf), L(c(0,1,0), c(1,1,0), xf), yf),
           L(L(c(0,0,1), c(1,0,1), xf), L(c(0,1,1), c(1,1,1), xf), yf), zf);
}
export const noise2 = (x, y) => noise3(x, y, 0);

export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, k) => a + (b - a) * k;
export const smoothstep = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };

export function cubicBezier(x1, y1, x2, y2) {
  const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
  const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
  const sx = t => ((ax * t + bx) * t + cx) * t;
  const sy = t => ((ay * t + by) * t + cy) * t;
  const dx = t => (3 * ax * t + 2 * bx) * t + cx;
  return x => {
    if (x <= 0) return 0; if (x >= 1) return 1;
    let t = x;
    for (let i = 0; i < 8; i++) { const e = sx(t) - x; const d = dx(t); if (Math.abs(e) < 1e-6 || d === 0) break; t -= e / d; }
    return sy(clamp(t));
  };
}

export const ease = {
  linear: x => x,
  inQuad: x => x * x, outQuad: x => 1 - (1 - x) * (1 - x), inOutQuad: x => x < .5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2,
  inCubic: x => x * x * x, outCubic: x => 1 - Math.pow(1 - x, 3), inOutCubic: x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2,
  outQuart: x => 1 - Math.pow(1 - x, 4), inOutQuart: x => x < .5 ? 8 * x ** 4 : 1 - Math.pow(-2 * x + 2, 4) / 2,
  outExpo: x => x === 1 ? 1 : 1 - Math.pow(2, -10 * x), inExpo: x => x === 0 ? 0 : Math.pow(2, 10 * x - 10),
  inOutExpo: x => x === 0 ? 0 : x === 1 ? 1 : x < .5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2,
  inOutSine: x => -(Math.cos(Math.PI * x) - 1) / 2, outSine: x => Math.sin(x * Math.PI / 2),
  outBack: x => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); },
  inBack: x => { const c1 = 1.70158; return (c1 + 1) * x * x * x - c1 * x * x; },
  outElastic: x => x === 0 ? 0 : x === 1 ? 1 : Math.pow(2, -10 * x) * Math.sin((x * 10 - 0.75) * (2 * Math.PI) / 3) + 1,
  outBounce: x => { const n = 7.5625, d = 2.75; if (x < 1 / d) return n * x * x; if (x < 2 / d) return n * (x -= 1.5 / d) * x + .75; if (x < 2.5 / d) return n * (x -= 2.25 / d) * x + .9375; return n * (x -= 2.625 / d) * x + .984375; },
};

export function seg(t, a, b, e = ease.linear) { return e(clamp((t - a) / (b - a))); }

export function hexToRgb(h) { h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); const n = parseInt(h, 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
export function mix(a, b, k) { const A = hexToRgb(a), B = hexToRgb(b); return `rgb(${A.map((v, i) => Math.round(lerp(v, B[i], k))).join(',')})`; }

/** fonts: [{family:'Space Grotesk', pkg:'space-grotesk', weight:700, style:'normal', subset:'latin'}] */
export async function loadFonts(fonts) {
  const css = fonts.map(f => {
    const subset = f.subset || 'latin', style = f.style || 'normal', w = f.weight || 400;
    const url = `/node_modules/@fontsource/${f.pkg}/files/${f.pkg}-${subset}-${w}-${style}.woff2`;
    return `@font-face{font-family:'${f.family}';font-style:${style};font-weight:${w};font-display:block;src:url(${url}) format('woff2');}`;
  }).join('\n');
  const el = document.createElement('style'); el.textContent = css; document.head.appendChild(el);
  await Promise.all(fonts.map(f => document.fonts.load(`${f.style === 'italic' ? 'italic ' : ''}${f.weight || 400} 40px '${f.family}'`, 'AÉéçà0123')));
  await document.fonts.ready;
}

export function guides() {
  if (!/guides=1/.test(location.search)) return;
  const d = document.createElement('div');
  d.style.cssText = `position:fixed;inset:0;pointer-events:none;z-index:99999;
    box-shadow: inset 0 ${SAFE.top}px 0 rgba(255,0,0,.25), inset 0 -${SAFE.bottom}px 0 rgba(255,0,0,.25), inset -${SAFE.right}px 0 0 rgba(255,0,0,.25);`;
  document.body.appendChild(d);
}

export function installContract({ renderAt, ready, sequential = false, duration = 15 }) {
  window.SEQUENTIAL = !!sequential;
  window.DURATION = duration;
  window.renderAt = (t) => { renderAt(t); };   // jamais de valeur de retour (évite les thenables)
  window.ready = Promise.resolve(ready).then(() => { guides(); });
}
