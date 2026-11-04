/**
 * brut.js — moteur partagé de l'identité « Brut Mème » (PixiJS 8 + GSAP 3, scènes 1080×1920).
 * Copié à l'identique dans chaque short brut-meme (src/brut.js).
 *
 * - C / X            : palette (CSS / entiers Pixi) : noir #111111, jaune #FFE600, rouge #FF2D2D, blanc
 * - initPixi(host)   : PIXI.Application headless (preserveDrawingBuffer, autoStart:false, ticker arrêté)
 * - halftone(app)    : sprite trame de points (texture blanche pré-rendue, teintée selon le fond)
 * - camera(t, cuts, shakes) : punch-in (scale 1,15 -> 1 en 3 frames) + shake seedé amorti -> {s, x, y}
 * - starburst / sticker / hazardBar / block : formes « autocollant » dessinées dans un PIXI.Graphics
 * - fitAll(root)     : ajuste font-size des [data-fit] pour que le texte remplisse data-fit px de large
 * - scenes(t, list)  : affiche la scène active (coupe franche), renvoie son index
 */
import * as S from '/out/tools/lib/svi.js';

export const C = { bg: '#111111', yel: '#FFE600', red: '#FF2D2D', white: '#FFFFFF' };
export const X = { bg: 0x111111, yel: 0xFFE600, red: 0xFF2D2D, white: 0xFFFFFF, black: 0x000000 };
export const PUNCH = { scale: 1.15, frames: 3 };
export const FONTS = [{ family: 'Anton', pkg: 'anton', weight: 400 }, { family: 'Inter', pkg: 'inter', weight: 900 }];

export async function initPixi(host) {
  const app = new PIXI.Application();
  await app.init({ width: S.W, height: S.H, background: X.bg, antialias: true, autoStart: false,
    preserveDrawingBuffer: true, preference: 'webgl' });
  app.ticker.stop();
  host.appendChild(app.canvas);
  return app;
}

/** trame de points en diagonale (plus grosse en bas à gauche), pré-rendue une fois en texture */
export function halftone(app) {
  const g = new PIXI.Graphics();
  const step = 24;
  for (let y = 0; y < S.H + step; y += step) for (let x = 0; x < S.W + step; x += step) {
    const k = S.clamp(((S.H - y) * -0.55 + (S.W - x) * 0.45 + 900) / 1500);
    const r = 7.5 * k * k;
    if (r < 0.8) continue;
    g.circle(x + ((y / step) % 2) * step / 2, y, r).fill({ color: 0xffffff });
  }
  g.rect(0, 0, S.W, S.H).fill({ color: 0xffffff, alpha: 0.001 });
  const tex = app.renderer.generateTexture(g);
  g.destroy();
  return new PIXI.Sprite(tex);
}

/** caméra : cuts = [[t, force]] (force 1 = punch 1,15), shakes = [[t, amplitude px]] */
export function camera(t, cuts, shakes) {
  const dur = PUNCH.frames / S.FPS;
  let s = 1;
  for (const [c, f = 1] of cuts) {
    if (t >= c - 1e-6 && t < c + dur) {
      const k = S.clamp((t - c) / dur);
      s = 1 + (PUNCH.scale - 1) * f * (1 - k) * (1 - k);
    }
  }
  let x = 0, y = 0;
  const fr = Math.round(t * S.FPS);
  for (const [e, a] of shakes) {
    const dt = t - e;
    if (dt < 0 || dt > 0.45) continue;
    const r = S.rng(fr * 7 + Math.round(e * 100));
    const amp = a * Math.exp(-dt / 0.12);
    x += (r() - 0.5) * 2 * amp; y += (r() - 0.5) * 2 * amp;
  }
  return { s, x, y };
}

export function applyCamera(el, cam) {
  el.style.transform = `translate(${cam.x.toFixed(2)}px,${cam.y.toFixed(2)}px) scale(${cam.s.toFixed(4)})`;
}

/** étoile « promo » : n pointes */
export function starburst(g, x, y, R, r, n, rot, color, stroke = X.bg, sw = 8) {
  const pts = [];
  for (let i = 0; i < n * 2; i++) {
    const a = rot + (i * Math.PI) / n, rr = i % 2 ? r : R;
    pts.push(x + Math.cos(a) * rr, y + Math.sin(a) * rr);
  }
  g.poly(pts.map((v, i) => v + 12)).fill({ color: X.black }); // ombre dure décalée
  g.poly(pts).fill({ color }).stroke({ width: sw, color: stroke, join: 'miter' });
}

/** sticker rond rouge cerclé (noir + anneau blanc) comme l'affiche Phase 1 */
export function sticker(g, x, y, R, color = X.red, ring = X.white) {
  g.circle(x, y, R + 14).fill({ color: ring });
  g.circle(x, y, R + 6).fill({ color: X.bg });
  g.circle(x, y, R).fill({ color });
}

/** bloc plein + ombre dure décalée */
export function block(g, x, y, w, h, color, shadow = X.black, off = 14) {
  if (shadow !== null) g.rect(x + off, y + off, w, h).fill({ color: shadow });
  g.rect(x, y, w, h).fill({ color });
}

/** barre « ruban de chantier » : rayures diagonales jaune/noir, remplie de 0..k */
export function hazardBar(g, x, y, w, h, k, c1 = X.yel, c2 = X.bg) {
  g.rect(x - 6, y - 6, w + 12, h + 12).fill({ color: X.white });
  g.rect(x, y, w, h).fill({ color: X.bg });
  const fw = w * S.clamp(k);
  if (fw <= 0) return;
  g.rect(x, y, fw, h).fill({ color: c1 });
  const sw = 34;
  for (let sx = x - h - sw; sx < x + fw; sx += sw * 2) {
    const pts = clipX([[sx, y + h], [sx + sw, y + h], [sx + sw + h, y], [sx + h, y]], x, x + fw);
    if (pts.length >= 3) g.poly(pts.flat()).fill({ color: c2 });
  }
}

/** découpe d'un polygone convexe entre deux verticales (Sutherland–Hodgman) */
function clipX(poly, x0, x1) {
  const clip = (P, inside, ix) => {
    const out = [];
    for (let i = 0; i < P.length; i++) {
      const a = P[i], b = P[(i + 1) % P.length];
      const ia = inside(a), ib = inside(b);
      if (ia) out.push(a);
      if (ia !== ib) { const k = (ix - a[0]) / (b[0] - a[0]); out.push([ix, a[1] + (b[1] - a[1]) * k]); }
    }
    return out;
  };
  return clip(clip(poly, p => p[0] >= x0, x0), p => p[0] <= x1, x1);
}

/** coeur (béziers) centré en x,y, largeur ~2*R */
export function heart(g, x, y, R, color) {
  const d = (ox, oy) => {
    g.moveTo(x + ox, y + oy + R * 0.95)
      .bezierCurveTo(x + ox - R * 1.25, y + oy + R * 0.1, x + ox - R * 1.05, y + oy - R * 0.95, x + ox, y + oy - R * 0.45)
      .bezierCurveTo(x + ox + R * 1.05, y + oy - R * 0.95, x + ox + R * 1.25, y + oy + R * 0.1, x + ox, y + oy + R * 0.95)
      .closePath();
  };
  d(14, 14); g.fill({ color: X.black });
  d(0, 0); g.fill({ color }).stroke({ width: 10, color: X.bg });
}

/** éclair en zigzag (seedé) */
export function bolt(g, x, y, len, seed, color = X.yel) {
  const r = S.rng(seed);
  const pts = [[x, y]];
  let cx = x, cy = y;
  const n = 5;
  for (let i = 0; i < n; i++) { cx += (i % 2 ? 1 : -1) * (20 + r() * 40); cy += len / n; pts.push([cx, cy]); }
  const path = (ox) => { g.moveTo(pts[0][0] + ox, pts[0][1] + ox); for (const [px, py] of pts.slice(1)) g.lineTo(px + ox, py + ox); };
  path(8); g.stroke({ width: 22, color: X.black, join: 'miter', cap: 'square' });
  path(0); g.stroke({ width: 22, color: X.bg, join: 'miter', cap: 'square' });
  path(0); g.stroke({ width: 12, color, join: 'miter', cap: 'square' });
}

/** ajuste les titres [data-fit="largeur"] (data-max = taille max px) ; à appeler après chargement des polices */
export function fitAll(root = document) {
  const scenes = [...root.querySelectorAll('.sc')];
  scenes.forEach(s => { s.style.display = 'block'; s.style.visibility = 'hidden'; });
  root.querySelectorAll('[data-fit]').forEach(el => {
    const target = +el.dataset.fit, max = +(el.dataset.max || 420);
    el.style.fontSize = max + 'px';
    const w = el.scrollWidth || el.getBoundingClientRect().width;
    const size = Math.min(max, Math.floor(max * target / w));
    el.style.fontSize = size + 'px';
    el.dataset.size = size;
  });
  scenes.forEach(s => { s.style.display = 'none'; s.style.visibility = ''; });
}

/** scènes à coupe franche : list = [[el, t0, t1]] */
export function scenes(t, list) {
  let idx = -1;
  list.forEach(([el, a, b], i) => { const on = t >= a - 1e-6 && t < b - 1e-6; el.style.display = on ? 'block' : 'none'; if (on) idx = i; });
  return idx;
}

/** slam GSAP : arrive de très près (scale 2,4) en 0,1 s, power4.in */
export function slam(tl, sel, at, { from = 2.4, rot = 0, dur = 0.1 } = {}) {
  tl.fromTo(sel, { scale: from, rotation: rot + 18, autoAlpha: 0 },
    { scale: 1, rotation: rot, autoAlpha: 1, duration: dur, ease: 'power4.in', immediateRender: false }, at);
}

/** entre en glissant (bande / tag) */
export function slide(tl, sel, at, { x = -1100, y = 0, dur = 0.1 } = {}) {
  tl.fromTo(sel, { x, y, autoAlpha: 1 }, { x: 0, y: 0, autoAlpha: 1, duration: dur, ease: 'power4.out', immediateRender: false }, at);
}

export const fmt = n => String(Math.floor(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
export const BASE_CSS = `
:root{--bg:#111111;--yel:#FFE600;--red:#FF2D2D;--white:#FFFFFF}
html,body{margin:0;background:var(--bg);width:1080px;height:1920px;overflow:hidden}
#cam{position:absolute;left:0;top:0;width:1080px;height:1920px;transform-origin:540px 900px}
#pix{position:absolute;inset:0}#pix canvas{display:block}
.sc{position:absolute;inset:0;display:none}
.a{position:absolute;white-space:nowrap}
.big{white-space:nowrap;font-family:'Anton';font-weight:400;line-height:0.86;text-transform:uppercase;letter-spacing:-2px}
.tag{font:900 56px/1 'Inter';letter-spacing:-1px;padding:12px 20px 10px;background:var(--red);color:var(--white)}
.hl{background:var(--yel);color:var(--bg);padding:18px 22px 0px}
.inv{background:var(--bg);color:var(--yel);padding:18px 22px 0px}
.stk{font:900 66px/0.98 'Inter';letter-spacing:-2px;text-align:center;color:var(--white);transform-origin:50% 50%}
.later{visibility:hidden}
`;
