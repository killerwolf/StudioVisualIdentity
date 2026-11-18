// lyrics.js — moteur de l'identité Lyrics punchy (out/identities/lyrics-punchy/, concept : out/report/notes/lyrics-punchy/).
// Lit un lyrics.json (format de pipeline.md) et dessine l'image au temps t. Aucun état : tout est une fonction de t et des
// données (pas de SEQUENTIAL). Texte en DOM (police variable Anybody, axe wdth 50–150), pictogrammes en SVG (dessins.js).
//
//   import { start } from '/out/shared/lyrics-moteur/lyrics.js';
//   start({ data: 'lyrics.json' });            // la scène passe ?data=… ; ?debug affiche les zones sûres
//   window.audit(t) -> boîtes du texte visible (taille, ton, rectangle des capitales) et du carton, pour le contrôle
import { dessins, dessinManquant } from './dessins.js';

const W = 1080, H = 1920, X0 = 64, X1 = 940, COL = X1 - X0, FPS = 30;
const CREME = '#FFF6E5';
export const CAMAIEUX = {
  nuit:   { bg: '#2A1160', mur: ['#B9A4F5', '#8468DB', '#5F45B8'], accent: '#E6FF4F', encre: '#140A33' },
  lagon:  { bg: '#063F4A', mur: ['#8FD9DC', '#4FA9B0', '#2F8791'], accent: '#FF8A5C', encre: '#04252C' },
  braise: { bg: '#5E0F2C', mur: ['#F2A5B5', '#D0708A', '#A64A66'], accent: '#FFD166', encre: '#33061A' },
};
const L = {                       // grille (concept.md § 5)
  curTop: 850, curBottom: 1500, rangGap: 34, curMin: 120, curMax: 250,
  murBottom: 800, murTop: 300, murGap: 26, murMin: 56, murMax: 118, murLignes: 4,
  carton: { side: 440, cx: 712, cy: 476, angle: 4, top: 232, gap: 14, minSide: 340 },
  dots: { x: 77, y: 262, r: 13, step: 40 },
};
const F = (n) => n / FPS;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const out3 = (k) => 1 - Math.pow(1 - clamp(k), 3);
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
function mix(a, b, k) {
  const p = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const A = p(a), B = p(b);
  return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * clamp(k)).toString(16).padStart(2, '0')).join('');
}

// ---------- mesure du texte (une fois, après le chargement de la police) ----------
let meas, CAP = 0.7, BASE = 0.9;
function setupMeasure() {
  meas = document.createElement('span');
  meas.style.cssText = 'position:absolute;left:-5000px;top:0;white-space:nowrap;font-family:"Anybody Variable";letter-spacing:0;line-height:1';
  document.body.appendChild(meas);
  // ligne de base dans une boîte line-height:1 : un inline-block vide est posé sur la ligne de base
  const probe = document.createElement('div');
  probe.style.cssText = 'position:absolute;left:-5000px;top:0;font-family:"Anybody Variable";font-size:1000px;line-height:1;font-variation-settings:"wdth" 100,"wght" 900';
  probe.innerHTML = 'H<span style="display:inline-block;width:0;height:0;vertical-align:baseline"></span>';
  document.body.appendChild(probe);
  BASE = (probe.lastChild.getBoundingClientRect().top - probe.getBoundingClientRect().top) / 1000;
  probe.remove();
  const c = document.createElement('canvas').getContext('2d');
  c.font = '900 1000px "Anybody Variable"';
  CAP = c.measureText('H').actualBoundingBoxAscent / 1000;
  const w50 = width('PLAN MODE', 100, 50, 900), w150 = width('PLAN MODE', 100, 150, 900);
  if (!(w150 > w50 * 1.5)) throw new Error(`axe wdth inactif : ${w50} / ${w150} px (mauvais fichier de police ?)`);
  return { CAP, BASE, w50, w150 };
}
const wcache = new Map();
function width(txt, size, wdth, wght) {
  const k = `${txt}|${size}|${wdth}|${wght}`;
  if (wcache.has(k)) return wcache.get(k);
  meas.style.fontSize = size + 'px';
  meas.style.fontVariationSettings = `"wdth" ${wdth}, "wght" ${wght}`;
  meas.textContent = txt;
  const w = meas.getBoundingClientRect().width;
  wcache.set(k, w);
  return w;
}
// concept.md § 4 : taille d'abord, puis l'axe de largeur pour remplir exactement la colonne
const warnings = [];
function fit(txt, wght, smin, smax, cible = COL) {
  let size = clamp(smax * cible / width(txt, smax, 100, wght), smin, smax);
  let lo = 50, hi = 150;
  for (let i = 0; i < 14; i++) {
    const mid = (lo + hi) / 2;
    if (width(txt, size, mid, wght) > cible) hi = mid; else lo = mid;
  }
  let wd = Math.round(lo * 10) / 10;
  while (width(txt, size, wd, wght) > cible + 0.5 && size > smin) size -= 2;
  size = Math.max(smin, size);
  const w = width(txt, size, wd, wght);
  if (w > cible + 1) warnings.push(`trop long à ${smin}px / wdth 50 : « ${txt} » ${w.toFixed(0)} px`);
  return { size, wdth: wd, w, cap: CAP * size };
}

// ---------- préparation des lignes ----------
let D, beat, S;
function prepare(data) {
  D = data; beat = 60 / D.bpm;
  const secs = D.sections.map((s, i) => ({ ...s, i, pal: CAMAIEUX[s.camaieu] || CAMAIEUX.nuit }));
  const lines = D.lignes.map((ln, li) => {
    const sec = secs.find((s) => s.id === ln.section && ln.debut >= s.debut - 1e-3) || secs.find((s) => s.id === ln.section);
    const units = ln.unites.map((u, ui) => ({ ...u, ui, te: u.t - F(2) }));
    const nr = Math.max(...units.map((u) => u.rang)) + 1;
    let smax = L.curMax, rangs;
    for (;;) {                                         // rangs justifiés ; on réduit si le bloc dépasse y 1 500
      rangs = [];
      for (let r = 0; r < nr; r++) {
        const us = units.filter((u) => u.rang === r);
        const txt = us.map((u) => u.texte).join(' ');
        const f = fit(txt, 900, L.curMin, smax);
        let acc = '';
        // x d'une unité = largeur de « ce qui précède + espace + unité » moins celle de l'unité (une espace finale ne se mesure pas)
        us.forEach((u, j) => { u.w = width(u.texte, f.size, f.wdth, 900); u.x = X0 + (j ? width(acc + ' ' + u.texte, f.size, f.wdth, 900) - u.w : 0); acc += (j ? ' ' : '') + u.texte; u.r = r; });
        rangs.push({ ...f, txt, us });
      }
      let y = L.curTop;
      rangs.forEach((r) => { r.y = y; y += r.cap + L.rangGap; });
      if (y - L.rangGap <= L.curBottom || smax <= L.curMin) break;
      smax -= 10;
    }
    const txt = units.map((u) => u.texte).join(' ');
    const mur = fit(txt, 800, L.murMin, L.murMax);
    return { li, sec, units, rangs, mur, txt, start: units[0].te, debut: ln.debut, fin: ln.fin };
  });
  secs.forEach((s) => { s.lines = lines.filter((l) => l.sec === s); });
  const cartons = [];
  lines.forEach((l) => l.units.forEach((u) => { if (u.declencheur) cartons.push({ ...u.declencheur, mot: u.texte, line: l }); }));
  cartons.forEach((c, i) => { c.angle = (i % 2 ? 1 : -1) * L.carton.angle; place(c, lines); });
  S = { secs, lines, cartons };
  return S;
}

// position du mur : lignes empilées depuis le bas (y 800), la plus récente en bas
function murSlots(list) {
  let yb = L.murBottom; const out = [];
  for (const l of list) { const top = yb - l.mur.cap; out.push(top); yb = top - L.murGap; }
  return out;
}
function murAt(line) {        // lignes du mur quand `line` est la ligne en cours (même section, plus récente d'abord)
  const ls = line.sec.lines; const i = ls.indexOf(line);
  return ls.slice(0, i).reverse();
}
const tone = (pal, n) => pal.mur[Math.min(2, n)];

// carton : par défaut carré 440 centré (712, 476) ; s'il couvrirait une ligne du mur encore lisible (tons 1 et 2),
// il se pose plus haut et plus petit (≥ 340 px) ; sinon (rare) ces lignes passent au ton 3, décoratif, pendant le carton.
function place(c, lines) {
  const k = Math.cos(c.angle * Math.PI / 180) + Math.sin(Math.abs(c.angle) * Math.PI / 180);
  const def = L.carton;
  c.side = def.side; c.cx = def.cx; c.cy = def.cy; c.dimmed = new Set();
  let readTop = Infinity;
  // états du mur pendant le carton : celui de la ligne qui porte le mot, puis de chaque ligne qui commence avant la sortie
  const states = c.line.sec.lines.filter((l) => l === c.line || (l.start > c.debut && l.start < c.fin));
  for (const cur of states) {
    const m = murAt(cur); const ys = murSlots(m);
    m.forEach((l, n) => { if (n < 2) readTop = Math.min(readTop, ys[n]); });
  }
  const bottom = (side, cy) => cy + side * k / 2;
  if (bottom(def.side, def.cy) <= readTop - def.gap) return;
  const side = Math.min(def.side, (readTop - def.gap - def.top) / k);
  const right = def.cx + def.side * k / 2;
  if (side >= def.minSide) {
    c.side = side; c.cy = def.top + side * k / 2; c.cx = right - side * k / 2; c.adapte = true;
  } else {
    c.dimmed = new Set(states.flatMap((cur) => murAt(cur)).map((l) => l.li)); c.estompe = true;
  }
}

// ---------- animation d'une unité (concept.md § 7) ----------
function unitAnim(u, t, rang) {
  const f = (t - u.te) * FPS;
  let s = 1, op = 1, wd = rang.wdth, dy = 0;
  if (u.accent === 0) { op = clamp(f / 2); s = 0.9 + 0.1 * clamp(f / 2); }
  else {
    const fr = u.accent === 2 ? 4 : 3, amp = u.accent === 2 ? 0.7 : 0.3;
    s = 1 + amp * Math.pow(1 - clamp(f / fr), 3);
    wd = Math.min(150, rang.wdth * (1 + 0.4 * Math.pow(1 - clamp(f / 5), 3)));
  }
  return { s, op, wd };
}
function colShake(t, line) {     // `coup` : toute la colonne descend de 12 px et revient en 5 images, après l'arrivée du mot
  let dy = 0;
  for (const l of S.lines) for (const u of l.units) {
    if (u.accent !== 2) continue;
    const f = (t - u.te) * FPS - 4;
    if (f >= 0 && f <= 5) dy = Math.max(dy, 12 * Math.sin(Math.PI * f / 5));
  }
  return dy;
}

// ---------- rendu ----------
let stage, debug = false;
function textBox({ x, top, size, wdth, wght, color, txt, w, cap, s = 1, sy = 1, op = 1, origin = '50% 50%', kind, tr = false, extra = '' }) {
  const off = BASE * size - cap;               // décalage entre le haut de la boîte line-height:1 et le haut des capitales
  return `<div class="t" data-k="${kind}" data-tr="${tr ? 1 : 0}" data-size="${size.toFixed(1)}" data-tone="${color}" style="left:${x.toFixed(1)}px;top:${top.toFixed(1)}px;width:${w.toFixed(1)}px;height:${cap.toFixed(1)}px;`
    + `opacity:${op.toFixed(3)};transform:scale(${s.toFixed(4)},${(s * sy).toFixed(4)});transform-origin:${origin};${extra}">`
    + `<span style="top:${(-off).toFixed(1)}px;font-size:${size.toFixed(1)}px;font-variation-settings:'wdth' ${wdth.toFixed(1)},'wght' ${wght};color:${color}">${esc(txt)}</span></div>`;
}

function sectionAt(t) { let s = S.secs[0]; for (const x of S.secs) if (t >= x.debut - 1e-6) s = x; return s; }
function lineAt(sec, t) { let c = null; for (const l of sec.lines) if (t >= l.start) c = l; return c; }

// la ligne en cours (rangs vifs) et le mur, tels qu'ils sont dans la section `sec` au temps t
function drawSection(sec, t, opts = {}) {
  const pal = sec.pal; let h = '';
  const cur = lineAt(sec, t);
  if (!cur) return h;
  const fall = opts.fall;                       // chute-de-pile : f (images depuis le début de la chute)
  const fallY = (n) => { if (fall === undefined) return 0; const k = clamp((fall - n) / 10); return 2200 * k * k; };
  const dimmed = opts.dimmed || new Set();
  // mur : interpolation entre l'état précédent et le nouveau pendant l'empilement (6 images)
  const m = murAt(cur); const ys = murSlots(m);
  const prevM = m.slice(1); const prevYs = murSlots(prevM);
  const k6 = out3((t - cur.start) * FPS / 6), k4 = clamp((t - cur.start) * FPS / 4);
  m.forEach((l, n) => {
    if (n >= L.murLignes + 1) return;
    let y = ys[n], col = tone(pal, n), op = 1;
    if (n === 0) {                                // la ligne finie glisse du haut du bloc vif vers le bas du mur
      y = L.curTop + (ys[0] - L.curTop) * k6; col = mix(CREME, tone(pal, 0), k6);
    } else { y = prevYs[n - 1] + (ys[n] - prevYs[n - 1]) * k6; col = mix(tone(pal, n - 1), tone(pal, n), k6); }
    if (n === L.murLignes) op = 1 - k4;           // la 5e disparaît en 4 images
    if (op <= 0) return;
    if (dimmed.has(l.li)) col = tone(pal, 2);
    const fy = fallY(n + 1);
    h += textBox({ x: X0, top: y + fy + (opts.dy || 0), size: l.mur.size, wdth: l.mur.wdth, wght: 800, color: col, txt: l.txt, w: l.mur.w, cap: l.mur.cap, op,
      kind: fall !== undefined ? 'chute' : (n < 2 && !dimmed.has(l.li) ? 'mur-lisible' : 'mur'), tr: n === 0 && k6 < 1, origin: '0 0' });
  });
  // ligne en cours : respiration sur chaque temps (1,02 en 4 images, en hauteur seulement : la largeur reste celle de la
  // colonne, sinon le rang justifié déborderait de 17 px dans la zone de droite), unités d'accent
  const bf = ((t - D.t0) / beat - Math.floor((t - D.t0) / beat + 1e-6)) * beat * FPS;
  const breath = fall === undefined ? 1 + 0.02 * Math.sin(Math.PI * clamp(bf / 4)) : 1;
  const visible = cur.units.filter((u) => t >= u.te);
  const lastVisible = visible[visible.length - 1];
  cur.rangs.forEach((r, ri) => {
    for (const u of r.us) {
      if (t < u.te) continue;
      const a = fall === undefined ? unitAnim(u, t, r) : { s: 1, op: 1, wd: r.wdth };
      const color = u === lastVisible ? pal.accent : CREME;
      const w = width(u.texte, r.size, a.wd, 900);
      const top = L.curTop + (r.y - L.curTop) * breath + (r.cap * (breath - 1)) / 2 + fallY(0) + (opts.dy || 0);
      const tr = fall === undefined && u.accent > 0 && (t - u.te) * FPS < 5;      // entrée claque / coup : 3 à 5 images
      h += textBox({ x: u.x, top, size: r.size, wdth: a.wd, wght: 900, color, txt: u.texte, w, cap: r.cap, s: a.s, sy: breath, op: a.op, kind: fall !== undefined ? 'chute' : 'vif', tr });
    }
  });
  return h;
}

function drawCarton(t) {
  const c = S.cartons.find((c) => t >= c.debut - F(2) && t < c.fin);
  if (!c) return { h: '', c: null };
  const pal = c.line.sec.pal;
  const lt = t - c.debut;
  const fin = c.fin >= D.duree - 1e-3 ? Infinity : c.fin;      // le dernier carton est tenu jusqu'à la fin
  let s = 1;
  const f = (t - (c.debut - F(2))) * FPS;
  s = 1 + 0.3 * Math.pow(1 - clamp(f / 3), 3);                 // entrée en claque
  if (t > fin - F(3)) s = clamp((fin - t) * FPS / 3);           // sortie : échelle 1 -> 0 en 3 images
  const fn = dessins[c.dessin];
  const inner = fn ? fn({ lt: Math.max(0, lt), beat, pal, creme: CREME }) : dessinManquant({ mot: c.mot, pal });
  const r = 36 * 500 / 440;
  const h = `<div class="carton" data-k="carton" style="left:${(c.cx - c.side / 2).toFixed(1)}px;top:${(c.cy - c.side / 2).toFixed(1)}px;width:${c.side.toFixed(1)}px;height:${c.side.toFixed(1)}px;transform:rotate(${c.angle}deg) scale(${s.toFixed(4)})">`
    + `<svg viewBox="0 0 500 500" width="100%" height="100%"><rect width="500" height="500" rx="${r}" fill="${pal.accent}"/>${inner}</svg></div>`;
  return { h, c, s };
}

function dots(t, pal) {
  const b = Math.floor((t - D.t0) / beat + 1e-6) % D.tempsParMesure;
  let h = '';
  for (let i = 0; i < 4; i++) h += `<div class="dot" style="left:${L.dots.x - L.dots.r + i * L.dots.step}px;top:${L.dots.y - L.dots.r}px;background:${i === b ? pal.accent : pal.mur[2]}"></div>`;
  return h;
}

function draw(t) {
  const sec = sectionAt(t);
  const prev = S.secs[sec.i - 1];
  let bg = sec.pal.bg;
  const fs = (t - sec.debut) * FPS;
  if (prev && fs < 10) bg = mix(prev.pal.bg, sec.pal.bg, fs / 10);   // le fond passe à la nouvelle teinte en 10 images
  const car = drawCarton(t);
  const dimmed = car.c ? car.c.dimmed : new Set();
  const dy = colShake(t);
  let h = `<div class="bg" style="background:${bg}"></div>` + dots(t, sec.pal);
  if (prev && fs < 10 + 12) h += drawSection(prev, sec.debut - 1e-4, { fall: fs });   // chute-de-pile de la section précédente
  h += drawSection(sec, t, { dimmed, dy });
  h += car.h;
  if (debug) h += zones();
  stage.innerHTML = h;
}

function zones() {
  return `<div style="position:absolute;inset:0 0 auto 0;height:220px;background:rgba(255,40,40,.3)"></div>`
    + `<div style="position:absolute;left:0;right:0;bottom:0;height:360px;background:rgba(255,40,40,.3)"></div>`
    + `<div style="position:absolute;top:0;bottom:0;right:0;width:140px;background:rgba(255,40,40,.3)"></div>`
    + `<div style="position:absolute;left:${X0}px;top:220px;width:${COL}px;height:1340px;outline:2px solid #fff"></div>`;
}

// contrôle : boîtes des capitales visibles (avec transformations) et polygone du carton
function audit(t) {
  window.renderAt(t);
  const items = [...stage.querySelectorAll('.t')].map((e) => {
    const b = e.getBoundingClientRect();
    return { k: e.dataset.k, tr: e.dataset.tr === '1', txt: e.textContent, size: +e.dataset.size, tone: e.dataset.tone, op: +getComputedStyle(e).opacity, x0: b.left, y0: b.top, x1: b.right, y1: b.bottom };
  }).filter((i) => i.op > 0.01);
  const c = S.cartons.find((c) => t >= c.debut - F(2) && t < c.fin);
  let carton = null;
  if (c) {
    const a = c.angle * Math.PI / 180, hs = c.side / 2;
    carton = { id: c.id, side: c.side, adapte: !!c.adapte, estompe: !!c.estompe,
      pts: [[-hs, -hs], [hs, -hs], [hs, hs], [-hs, hs]].map(([x, y]) => [c.cx + x * Math.cos(a) - y * Math.sin(a), c.cy + x * Math.sin(a) + y * Math.cos(a)]) };
  }
  return { t, items, carton };
}

export async function start(opts = {}) {
  let resolve, reject;
  window.ready = new Promise((r, j) => { resolve = r; reject = j; });
  debug = !!opts.debug;
  stage = document.getElementById('stage');
  window.renderAt = (t) => { if (S) draw(t); };
  try {
    const data = await fetch(opts.data).then((r) => { if (!r.ok) throw new Error('données introuvables : ' + opts.data); return r.json(); });
    window.DURATION = data.duree;
    await document.fonts.load('900 100px "Anybody Variable"', 'AÉÇ');
    await document.fonts.load('800 100px "Anybody Variable"', 'AÉÇ');
    await document.fonts.ready;
    const m = setupMeasure();
    prepare(data);
    window.audit = audit;
    window.lyricsInfo = { ...m, warnings, cartons: S.cartons.map((c) => ({ id: c.id, debut: c.debut, fin: c.fin, side: +c.side.toFixed(1), cx: +c.cx.toFixed(1), cy: +c.cy.toFixed(1), adapte: !!c.adapte, estompe: !!c.estompe })),
      lignes: S.lines.map((l) => ({ txt: l.txt, mur: { size: +l.mur.size.toFixed(1), wdth: l.mur.wdth }, rangs: l.rangs.map((r) => ({ txt: r.txt, size: +r.size.toFixed(1), wdth: r.wdth, y: +r.y.toFixed(1) })) })) };
    if (warnings.length) console.warn('[lyrics] ' + warnings.join(' ; '));
    draw(0);
    resolve();
  } catch (e) { console.error('[lyrics] ' + e.message); reject(e); }
}
