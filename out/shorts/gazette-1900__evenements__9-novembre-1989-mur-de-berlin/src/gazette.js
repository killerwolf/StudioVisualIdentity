/**
 * gazette.js — système partagé de l'identité « Gazette 1900 » (module ES, copié à l'identique dans chaque short).
 * - TOKENS : couleurs, typo, timings (bpm 128 : 1 page = 6 temps = 2,8125 s)
 * - injectCSS() / pageHTML(cfg) : une « une » de journal 1080×1920 (manchette, kicker, date-titre, sous-titre,
 *   gravure canvas 894×430, légende, dépêche typewriter, tampon rouge)
 * - gravures procédurales en hachures (canvas 2D) : ciel, cylindres, silhouettes inventées, foule
 * - beats GSAP : spinIn (tourniquet), stampIn (coup de tampon), zoomKick (zoom brusque), dimOut
 * - typewriter déterministe piloté par renderAt(t)
 * Les silhouettes sont stylisées et inventées : aucun portrait de personne réelle.
 */
import * as S from '/out/tools/lib/svi.js';

export const T = {
  bg: '#E9E1CF', surface: '#D8CDB4', plate: '#E4DAC4', red: '#B3261E', ink: '#1E1B18', desk: '#1E1B18',
  bpm: 128, beat: 60 / 128,
  spin: { dur: 0.55, ease: 'power3.out', fromRot: -540, fromScale: 0.06 },
  stamp: { dur: 0.16, ease: 'power4.in', fromScale: 2.6 },
  zoom: { dur: 0.14, ease: 'expo.out', scale: 1.1 },
  typeCps: 34,
};

export const FONTS = [
  { family: 'Playfair Display', pkg: 'playfair-display', weight: 900 },
  { family: 'DM Serif Display', pkg: 'dm-serif-display', weight: 400 },
  { family: 'DM Serif Display', pkg: 'dm-serif-display', weight: 400, style: 'italic' },
  { family: 'IBM Plex Mono', pkg: 'ibm-plex-mono', weight: 500 },
  { family: 'IBM Plex Mono', pkg: 'ibm-plex-mono', weight: 600 },
  { family: 'IBM Plex Mono', pkg: 'ibm-plex-mono', weight: 700 },
];

export function injectCSS() {
  const css = `
  html,body{margin:0;background:${T.desk};width:1080px;height:1920px;overflow:hidden}
  #stage{position:absolute;inset:0;overflow:hidden;background:${T.desk}}
  .sheet{position:absolute;left:0;top:0;width:1080px;height:1920px;transform-origin:50% 50%;visibility:hidden;
    box-shadow:0 0 0 2px rgba(0,0,0,.25), 0 30px 80px rgba(0,0,0,.55)}
  .zoom{position:absolute;inset:0;background:${T.bg};color:${T.ink};transform-origin:50% 600px}
  .border{position:absolute;inset:26px;border:3px solid ${T.ink};outline:1px solid ${T.ink};outline-offset:-12px}
  .col{position:absolute;left:60px;top:228px;width:900px;height:1372px;display:flex;flex-direction:column;align-items:center}
  .mast{width:900px;text-align:center}
  .mast .name{font:900 92px/1 'Playfair Display';letter-spacing:1px;white-space:nowrap}
  .mast .rule{border-top:5px solid ${T.ink};border-bottom:1.5px solid ${T.ink};height:0;padding-top:5px;margin-top:12px}
  .mast .meta{display:flex;justify-content:space-between;white-space:nowrap;font:500 54px/1 'IBM Plex Mono';padding:12px 4px;border-bottom:1.5px solid ${T.ink}}
  .kicker{margin-top:14px;font:400 60px/1.05 'DM Serif Display';color:${T.red};text-align:center;white-space:nowrap}
  .big{margin-top:6px;font:900 240px/0.86 'Playfair Display';letter-spacing:-4px;white-space:nowrap;text-align:center;font-variant-numeric:lining-nums}
  .sub{margin-top:8px;font:900 84px/1.0 'Playfair Display';text-align:center;width:900px}
  .plate{position:relative;margin-top:18px;width:894px;height:430px;border:3px solid ${T.ink};overflow:visible;flex:none}
  .plate .clip{position:absolute;inset:0;overflow:hidden}
  .plate canvas{display:block;transform-origin:50% 60%}
  .cap{margin-top:12px;font:italic 400 54px/1.05 'DM Serif Display';text-align:center;white-space:nowrap}
  .dep{margin-top:14px;width:900px;border-top:5px solid ${T.ink};padding-top:16px;font:500 54px/1.16 'IBM Plex Mono';min-height:126px;white-space:pre-wrap}
  .dep b{color:${T.red};font-weight:700}
  .stamp{position:absolute;right:18px;bottom:22px;padding:10px 22px;text-align:center;border:7px solid ${T.red};color:${T.red};
    font:400 60px/1.0 'DM Serif Display';text-transform:uppercase;letter-spacing:3px;transform-origin:50% 50%;
    outline:2px solid ${T.red};outline-offset:-16px;background:rgba(233,225,207,.9);white-space:nowrap;opacity:0;box-shadow:0 4px 0 rgba(30,27,24,.25)}
  .stamp small{display:block;font:600 30px/1.3 'IBM Plex Mono';letter-spacing:2px}
  .dim{position:absolute;inset:0;background:${T.ink};opacity:0;pointer-events:none}
  .caret{opacity:1}
  `;
  const el = document.createElement('style'); el.textContent = css; document.head.appendChild(el);
}

/** cfg: {id, date, price, kicker, big, sub, cap, depLabel, dep, stamp:{small,text}, inner(optionnel: HTML à la place de la gravure)} */
export function pageHTML(c) {
  const stamp = c.stamp ? `<div class="stamp" id="${c.id}-stamp">${c.stamp.small ? `<small>— ${c.stamp.small} —</small>` : ''}${c.stamp.text}</div>` : '';
  const plate = c.inner != null ? c.inner : `<div class="plate"><div class="clip"><canvas id="${c.id}-cv" width="894" height="430"></canvas></div>${stamp}</div>`;
  return `<div class="sheet" id="${c.id}"><div class="zoom">
    <div class="border"></div>
    <div class="col">
      <div class="mast"><div class="name">LE PETIT CRIEUR</div><div class="rule"></div>
        <div class="meta"><span>${c.date}</span><span>${c.price || '5 CENT.'}</span></div></div>
      <div class="kicker">${c.kicker}</div>
      <div class="big">${c.big}</div>
      ${c.sub ? `<div class="sub">${c.sub}</div>` : ''}
      ${plate}
      ${c.cap ? `<div class="cap">${c.cap}</div>` : ''}
      ${c.dep != null ? `<div class="dep" id="${c.id}-dep"></div>` : ''}
    </div>
    ${c.inner != null ? stamp : ''}
  </div><div class="dim"></div></div>`;
}

/** ajuste la taille d'une ligne pour qu'elle tienne dans maxW (manchette justifiée à la largeur de colonne) */
export function fitWidth(el, maxW = 900, maxPx = 240, minPx = 110) {
  let px = maxPx; el.style.fontSize = px + 'px';
  while (el.scrollWidth > maxW && px > minPx) { px -= 4; el.style.fontSize = px + 'px'; }
  return px;
}
/** réduit un bloc multi-lignes jusqu'à maxLines lignes */
export function fitLines(el, maxLines = 2, maxPx = 84, minPx = 60) {
  let px = maxPx; el.style.fontSize = px + 'px';
  const lh = () => parseFloat(getComputedStyle(el).lineHeight);
  while (el.getBoundingClientRect().height > lh() * maxLines + 2 && px > minPx) { px -= 2; el.style.fontSize = px + 'px'; }
  return px;
}

// ---------------- typewriter déterministe ----------------
const typers = [];
export function typewriter(el, label, text, t0, cps = T.typeCps) { typers.push({ el, label, text, t0, cps }); return t0 + text.length / cps; }
export function renderTypers(t) {
  for (const k of typers) {
    if (!k.el) continue;
    const n = Math.max(0, Math.min(k.text.length, Math.floor((t - k.t0) * k.cps)));
    const caretOn = t >= k.t0 - 0.3 && (Math.floor(t * 3) % 2 === 0 || n < k.text.length);
    const lab = k.label ? `<b>${k.label}</b>` : '';
    const vis = t >= k.t0 - 0.3;
    k.el.innerHTML = vis ? `${lab}${escapeHTML(k.text.slice(0, n))}<span class="caret" style="opacity:${caretOn ? 1 : 0}">▌</span>` : '';
  }
}
const escapeHTML = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
/** instants où un caractère non-espace apparaît (pour caler les « ticks » du son) */
export function typeTicks(text, t0, cps = T.typeCps, every = 3) {
  const out = []; let k = 0;
  for (let i = 0; i < text.length; i++) if (text[i] !== ' ' && (k++ % every === 0)) out.push(+(t0 + (i + 1) / cps).toFixed(3));
  return out;
}

// ---------------- beats GSAP (timeline seekée, jamais jouée) ----------------
export function spinIn(tl, sel, t, land = -1.2, opt = {}) {
  const fr = opt.fromRot ?? T.spin.fromRot, fs = opt.fromScale ?? T.spin.fromScale;
  tl.set(sel, { visibility: 'visible' }, t);
  tl.fromTo(sel, { rotation: fr + land, scale: fs }, { rotation: land, scale: 1, duration: opt.dur ?? T.spin.dur, ease: T.spin.ease, immediateRender: false }, t);
}
export function stampIn(tl, sel, t, rot = -8) {
  tl.fromTo(sel, { scale: T.stamp.fromScale, rotation: rot + 6, opacity: 0 }, { scale: 1, rotation: rot, opacity: 1, duration: T.stamp.dur, ease: T.stamp.ease, immediateRender: false }, t);
}
export function zoomKick(tl, sel, t, scale = T.zoom.scale) {
  tl.fromTo(sel, { scale: 1 }, { scale, duration: T.zoom.dur, ease: T.zoom.ease, immediateRender: false }, t);
}
export function dimOut(tl, sel, t, to = 0.45) {
  tl.fromTo(sel, { opacity: 0 }, { opacity: to, duration: T.spin.dur, ease: 'power1.in', immediateRender: false }, t);
}
export function kenBurns(tl, sel, t, dur, to = 1.07) {
  tl.fromTo(sel, { scale: 1 }, { scale: to, duration: dur, ease: 'none', immediateRender: false }, t);
}

// ---------------- gravure : primitives en hachures ----------------
export function paper(g, W, H) { g.fillStyle = T.plate; g.fillRect(0, 0, W, H); g.strokeStyle = T.ink; g.fillStyle = T.ink; g.lineCap = 'round'; }

/** lignes horizontales dont l'épaisseur = wfn(x,y) (0 = blanc) */
export function hHatch(g, x0, x1, y0, y1, step, wfn) {
  for (let y = y0; y < y1; y += step) {
    let open = false;
    for (let x = x0; x <= x1; x += 6) {
      const w = wfn(x, y);
      if (w < .25) { if (open) { g.stroke(); open = false; } continue; }
      if (!open) { g.beginPath(); g.lineWidth = w; g.moveTo(x, y); open = true; }
      else { g.lineWidth = w; g.lineTo(x, y + Math.sin(x / 40) * .5); }
    }
    if (open) g.stroke();
  }
}
/** cylindre (tour, colonne) ombré par hachures verticales, lumière à gauche */
export function cylinder(g, x0, top, w, h, courses = 22) {
  g.fillStyle = T.plate; g.fillRect(x0, top, w, h);
  for (let x = x0 + 2; x < x0 + w; x += 4) {
    const u = (x - x0) / w, sh = Math.pow(S.clamp(u * 1.2 - .1), 1.4);
    g.lineWidth = S.lerp(.4, 3.4, sh); g.beginPath(); g.moveTo(x, top + 6); g.lineTo(x, top + h); g.stroke();
  }
  if (courses) { g.lineWidth = .9; for (let y = top + 30; y < top + h; y += courses) { g.beginPath(); g.moveTo(x0, y); g.quadraticCurveTo(x0 + w / 2, y + 6, x0 + w, y); g.stroke(); } }
  g.lineWidth = 3; g.strokeRect(x0, top, w, h); g.fillStyle = T.ink;
}
/** rayons (soleil levant) depuis (cx,cy) */
export function rays(g, cx, cy, n, r0, r1, wmax = 3) {
  for (let i = 0; i < n; i++) {
    const a = Math.PI + (i + .5) / n * Math.PI; const w = (i % 2 ? .6 : wmax);
    g.lineWidth = w; g.beginPath(); g.moveTo(cx + Math.cos(a) * r0, cy + Math.sin(a) * r0); g.lineTo(cx + Math.cos(a) * r1, cy + Math.sin(a) * r1); g.stroke();
  }
}
/** silhouette inventée, encre pleine. hat: none|cap|tricorn|tall|bonnet ; arm: 0 (bas) | 1 (bras levé droit) */
export function figure(g, x, y, r, hat = 'none', arm = 0, R = Math.random) {
  g.fillStyle = T.ink; g.strokeStyle = T.ink;
  g.beginPath(); g.arc(x, y - r * 1.6, r, 0, Math.PI * 2); g.fill();                       // tête
  g.beginPath(); g.ellipse(x, y + r, r * 2, r * 1.8, 0, Math.PI, 0); g.fill();             // épaules
  g.fillRect(x - r * 2, y + r - 1, r * 4, r * 6);                                           // buste
  const hy = y - r * 2.4;
  if (hat === 'tricorn') { g.beginPath(); g.moveTo(x - r * 1.9, hy + r * .5); g.quadraticCurveTo(x, hy - r * 1.4, x + r * 1.9, hy + r * .5); g.quadraticCurveTo(x, hy, x - r * 1.9, hy + r * .5); g.fill(); }
  else if (hat === 'tall') { g.fillRect(x - r * .9, hy - r * 1.1, r * 1.8, r * 1.3); g.fillRect(x - r * 1.6, hy + r * .1, r * 3.2, r * .35); }
  else if (hat === 'cap') { g.beginPath(); g.arc(x, hy + r * .6, r * 1.05, Math.PI, 0); g.fill(); }
  else if (hat === 'bonnet') { g.fillStyle = T.red; g.beginPath(); g.moveTo(x - r, hy + r * .7); g.quadraticCurveTo(x - r * .2, hy - r * 1.3, x + r * 1.4, hy - r * .2); g.lineTo(x + r, hy + r * .7); g.fill(); g.fillStyle = T.ink; }
  if (arm) {
    g.lineWidth = r * .9; g.lineCap = 'round';
    const ax = x + r * 1.6, ay = y + r * .4, ex = ax + r * (0.8 + R() * .8), ey = y - r * (4.2 + R());
    g.beginPath(); g.moveTo(ax, ay); g.lineTo(ex, ey); g.stroke();
    g.beginPath(); g.arc(ex, ey, r * .55, 0, Math.PI * 2); g.fill();
  }
}
/** rangée de silhouettes */
export function crowd(g, W, yBase, n, rMin, rMax, R, opts = {}) {
  for (let i = 0; i < n; i++) {
    const x = (i + R() * .8) * (W / (n - 2)) - 10, y = yBase + R() * (opts.jitter ?? 10), r = rMin + R() * (rMax - rMin);
    const hats = opts.hats || ['none']; const hat = hats[Math.floor(R() * hats.length)];
    figure(g, x, y, r, hat, R() < (opts.arms ?? 0) ? 1 : 0, R);
    if (opts.pikes && R() < opts.pikes) { g.lineWidth = 3; g.beginPath(); g.moveTo(x + 8, y); g.lineTo(x + 8 + (R() - .5) * 30, y - 120 - R() * 50); g.stroke(); }
  }
}
export function frame(g, W, H) { g.lineWidth = 2; g.strokeStyle = T.ink; g.strokeRect(1, 1, W - 2, H - 2); }

export { S };
