// Maquette de direction artistique des déclinaisons de « lyrics-chemin » (habillages et dessins nouveaux).
// IMAGES FIXES SEULEMENT : pas de transitions, pas de flou de mouvement, pas d'audit. Ce n'est PAS le moteur :
// le moteur reste out/shared/chemin-moteur/chemin.js ; ce fichier montre ce qu'un « habillage » (skin) doit pouvoir changer.
// Contrat de out/tools/render.mjs : window.ready / window.renderAt(t).
import * as S from '/out/tools/lib/svi.js';
export { S };
export const W = 1080, H = 1920, ANCHOR = { x: 512, y: 860 };
export const rad = d => d * Math.PI / 180;
const LIVE_MIN = 0.30, FRAME_W = 780;

export function straight(a, b) { const dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy), ang = Math.atan2(dy, dx);
  return { len, at: d => ({ x: a[0] + dx * d / len, y: a[1] + dy * d / len, a: ang }) }; }
export function polyline(pts) {   // chemin courbe : points denses, abscisse curviligne ; angle = corde sur ±h (mot rigide)
  const ds = [0]; for (let i = 1; i < pts.length; i++) ds.push(ds[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  const len = ds.at(-1);
  const pos = d => { d = S.clamp(d, 0, len); let lo = 0, hi = ds.length - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (ds[m] <= d) lo = m; else hi = m; }
    const k = (d - ds[lo]) / (ds[hi] - ds[lo] || 1); return [pts[lo][0] + (pts[hi][0] - pts[lo][0]) * k, pts[lo][1] + (pts[hi][1] - pts[lo][1]) * k]; };
  return { len, pts, ds, at: (d, h = 6) => { const p = pos(d), a = pos(d - h), b = pos(d + h); return { x: p[0], y: p[1], a: Math.atan2(b[1] - a[1], b[0] - a[0]) }; } };
}
export function sub(path, d0, d1) { return { len: d1 - d0, at: (d, h) => path.at(d0 + d, h) }; }
export function catmull(P, step = 4) {   // lissage Catmull-Rom centripète simplifié -> points denses
  const out = []; for (let i = 0; i < P.length - 1; i++) { const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(P.length - 1, i + 2)];
    const n = Math.max(2, Math.ceil(Math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / step));
    for (let j = 0; j < n; j++) { const t = j / n, t2 = t * t, t3 = t2 * t;
      out.push([0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
                0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)]); } }
  out.push(P.at(-1)); return out; }
export function wave(x0, x1, y, amp, wl, ph = 0) { const pts = []; for (let x = x0; x <= x1; x += 3) pts.push([x, y + amp * Math.sin(ph + (x - x0) / wl * 2 * Math.PI)]); return polyline(pts); }

export function noiseTile(n, seed, fn) { const c = document.createElement('canvas'); c.width = c.height = n; const x = c.getContext('2d'), im = x.createImageData(n, n), r = S.rng(seed);
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { const [v, a, g, b] = fn(i, j, r); const o = (j * n + i) * 4; im.data[o] = v; im.data[o + 1] = g ?? v; im.data[o + 2] = b ?? v; im.data[o + 3] = a; }
  x.putImageData(im, 0, 0); return c; }
export function shadowed(c, cam, fn, blur = 14, ox = 9, oy = 13, a = 0.38, col = '10,10,20') {   // ombre attachée à la lumière du monde
  c.save(); const cs = Math.cos(-cam.th), sn = Math.sin(-cam.th); c.shadowColor = `rgba(${col},${a})`; c.shadowBlur = blur * cam.s;
  c.shadowOffsetX = (cs * ox - sn * oy) * cam.s; c.shadowOffsetY = (sn * ox + cs * oy) * cam.s; fn(); c.restore(); }
export function rr(c, x, y, w, h, r) { c.beginPath(); c.roundRect(x, y, w, h, r); }

export async function lancer({ skin, G, D }) {
  const q = new URLSearchParams(location.search);
  await S.loadFonts(skin.fonts);
  if (skin.prepare) await skin.prepare();
  const cv = document.getElementById('c'), ctx = cv.getContext('2d');
  const layer = document.createElement('canvas'); layer.width = W; layer.height = H; const lctx = layer.getContext('2d');
  const FONT = `'${skin.font}'`, CAP = skin.cap ?? 0.70, GAP = skin.gap ?? 0.16;
  const P = G.points || {}, pt = v => typeof v === 'string' ? P[v] : v;
  const mkPath = c => c.path ? c.path : c.type === 'vague' ? wave(c.x0, c.x1, c.y, c.amp, c.wl, c.ph) : straight(pt(c.a), pt(c.b));
  const [T_OUT0, T_OUT1] = D.zoomArriere, DURATION = D.duree;
  const wOf = (str, weight = skin.weight) => { ctx.font = `${weight} 100px ${FONT}`; ctx.letterSpacing = '0px'; return ctx.measureText(str).width / 100; };

  const LINES = D.lignes.map(l => { const A = G.aretes[l.arete]; if (!A) throw new Error('arête inconnue : ' + l.arete);
    return { ...A, id: l.arete, path: mkPath(A.chemin), u: l.u, cad: l.cad, arr: l.arr, minPx: l.minPx, maxPx: l.maxPx, annotation: l.annotation }; });
  for (const L of LINES) {
    const full = L.u.map(u => u[0]).join(' '), n = full.length, m = L.m || [0, 0];
    const gw = L.gapW ?? skin.gapW ?? 0, nGap = full.split(' ').length - 1;   // gapW : espace ajouté entre les mots (mots rigides sur une courbe)
    const usable = L.path.len - m[0] - m[1], wn = wOf(full, L.weight) + gw * nGap, [e0, e1] = L.em || skin.em || [36, 54];
    const em = S.clamp(usable / (wn + (L.track || 0) * (n - 1)), e0, e1);
    let tr = (L.track || 0) * em;
    if (!L.noFit && !L.track) tr = S.clamp((usable - em * wn) / (n - 1), 0, (L.trackMax ?? skin.trackMax ?? 0.15) * em);
    const total = em * wn + tr * (n - 1), d0 = m[0] + (L.center ? (usable - total) / 2 : 0);
    Object.assign(L, { emW: em, tr, words: [], units: [], d0, total }); let ci = 0, wi0 = 0;
    L.u.forEach((u, ui) => { const first = L.words.length;
      for (const wd of u[0].split(' ')) { L.words.push({ txt: wd, ui, d0: d0 + em * wOf(full.slice(0, ci), L.weight) + tr * ci + gw * em * (wi0++), w: em * wOf(wd, L.weight) + tr * (wd.length - 1) }); ci += wd.length + 1; }
      const a = L.words[first], b = L.words.at(-1), nw = L.words.length - first, per = (u[2] - u[1]) / nw;
      L.units.push({ txt: u[0], t: u[1], end: u[2], cls: u[3], d0: a.d0, d1: b.d0 + b.w, w0: first, w1: L.words.length, per, pre: per < LIVE_MIN }); });
    L.textEnd = L.units.at(-1).d1; L.tStart = L.units[0].t; L.tEnd = L.units.at(-1).end;
  }
  // rangs finaux (équivalent du refrain dans la mer) : même corps, même espace, centrés
  const M = G.final, RU = D.final.u, WF = skin.wFinal ?? 800;
  const rowTxt = D.final.rangs.map(r => r.map(i => RU[i][0]).join(' '));
  const rowW = s => s.split(' ').reduce((a, w) => a + wOf(w, WF), 0) + (s.split(' ').length - 1) * M.espace;
  const SEA_EM = Math.min(M.emMax, ...rowTxt.map(s => M.largeurMax / rowW(s))), SEA = [];
  D.final.rangs.forEach((r, ri) => { const R = M.rangs[ri], width = rowW(rowTxt[ri]) * SEA_EM, x0 = (M.gauche ?? (M.cx - width / 2));
    const path = R.amp ? wave(x0 - 10, x0 + width + 10, R.y, R.amp, R.wl, R.ph) : straight([x0 - 10, R.y], [x0 + width + 10, R.y]); let d = 10;
    r.forEach(i => { const [txt, t0, t1, cls] = RU[i], words = [];
      for (const w of txt.split(' ')) { const ww = SEA_EM * wOf(w, WF); words.push({ txt: w, d0: d, w: ww }); d += ww + M.espace * SEA_EM; }
      SEA.push({ path, txt, t0, t1, cls, words, row: ri, x0, y: R.y }); }); });

  // caméra : un cadrage par groupe d'unités (mêmes règles que le moteur), sans transitions
  const POSES = [];
  for (const L of LINES) L.cad.forEach((g, gi) => {
    const a = L.units[g[0]], b = L.units[g.at(-1)], dc = (a.d0 + b.d1) / 2, w = b.d1 - a.d0, p = L.path.at(dc, w / 2);
    const lift = L.below ? -L.emW * 0.52 : L.emW * 0.50, nx = Math.sin(p.a), ny = -Math.cos(p.a);
    const floor = L.minPx || skin.floorPx || 120, s = S.clamp(FRAME_W / w, floor / L.emW, (L.maxPx || 220) / L.emW);
    const th = p.a - S.clamp(Math.atan2(Math.sin(p.a), Math.cos(p.a)) * 0.1, rad(-6), rad(6));
    POSES.push({ line: L.id, x: p.x + nx * lift, y: p.y + ny * lift, s, th, arr: gi === 0 ? (L.arr ?? a.t - 0.2) : a.t - 0.06 }); });
  const FINAL = { x: ANCHOR.x, y: ANCHOR.y, s: 1, th: 0 };
  function camAt(t) {
    if (q.get('cam')) { const [x, y, s, th] = q.get('cam').split(',').map(Number); return { x, y, s, th: rad(th) }; }
    let i = 0; while (i + 1 < POSES.length && t >= POSES[i + 1].arr) i++; const p = POSES[i];
    if (t < T_OUT0) return p;
    if (t >= T_OUT1) { const e = 1 - Math.pow(1 - S.clamp((t - T_OUT1) / (DURATION - T_OUT1)), 2); return { ...FINAL, s: 1 - 0.045 * e }; }
    const u = (t - T_OUT0) / (T_OUT1 - T_OUT0), e = S.cubicBezier(0.5, 0, 0.12, 1)(u), ep = S.cubicBezier(0.3, 0, 0.1, 1)(u);
    let dth = -p.th; while (dth > Math.PI) dth -= 2 * Math.PI; while (dth < -Math.PI) dth += 2 * Math.PI;
    return { x: S.lerp(p.x, FINAL.x, ep), y: S.lerp(p.y, FINAL.y, ep), s: Math.exp(S.lerp(Math.log(p.s), 0, e)), th: p.th + dth * e };
  }
  const applyCam = (c, cam) => { c.translate(ANCHOR.x, ANCHOR.y); c.rotate(-cam.th); c.scale(cam.s, cam.s); c.translate(-cam.x, -cam.y); };

  function drawWord(c, L, wd, fill, alpha = 1, f = 1, weight, style = '') {
    const p = L.path.at(wd.d0 + wd.w / 2, wd.w / 2), em = L.emW ?? SEA_EM, tr = L.tr || 0;
    c.save(); c.translate(p.x, p.y); c.rotate(p.a); c.font = `${style}${weight} ${em}px ${FONT}`; c.letterSpacing = tr + 'px';
    let sag = 0; if (L.courbe) for (let i = 0; i <= 6; i++) { const q2 = L.path.at(wd.d0 + wd.w * i / 6, 2), ly = -(q2.x - p.x) * Math.sin(p.a) + (q2.y - p.y) * Math.cos(p.a); sag = L.below ? Math.max(sag, ly) : Math.max(sag, -ly); }
    const y = L.inside ? CAP * em / 2 : L.below ? GAP * em + CAP * em + sag : -GAP * em - sag;
    if (f < 1) { c.beginPath(); c.rect(-wd.w / 2 - 4, y - em * 1.1, (wd.w + 8) * f, em * 1.6); c.clip(); }
    c.globalAlpha = alpha; c.fillStyle = fill; c.textBaseline = 'alphabetic'; c.fillText(wd.txt, -wd.w / 2, y); c.restore(); }
  function strokePath(c, path, d0, d1, lw, col, dash, step = 4) { if (d1 <= d0) return; c.save(); c.beginPath(); c.lineWidth = lw; c.strokeStyle = col; c.lineCap = 'round'; c.lineJoin = 'round'; if (dash) c.setLineDash(dash);
    for (let d = d0; d < d1; d += step) { const p = path.at(d, 2); d === d0 ? c.moveTo(p.x, p.y) : c.lineTo(p.x, p.y); } const e = path.at(d1, 2); c.lineTo(e.x, e.y); c.stroke(); c.restore(); }

  function lineState(L, t) {   // avancement de la pointe sur une ligne
    if (t < L.tStart - 0.08) return { tip: null, end: 0 };
    let tipD = L.d0, writing = false;
    for (const u of L.units) for (let wi = u.w0; wi < u.w1; wi++) { const wd = L.words[wi], t0 = u.pre ? u.t : u.t + (wi - u.w0) * u.per - 0.08, dur = u.pre ? 0.01 : Math.min(0.5 * u.per, 0.28);
      if (t >= t0) { const f = S.clamp((t - t0) / dur); tipD = wd.d0 + wd.w * f; writing = t < u.end; } }
    const done = t > L.tEnd ? S.clamp((t - L.tEnd) / 0.35) : 0;
    return { tip: t <= L.tEnd + 0.1 ? tipD : null, tipD, end: S.lerp(Math.min(L.path.len, tipD + 0.3 * L.emW), L.path.len, done), writing };
  }
  function drawLines(c, cam, t) {
    const dryA = S.lerp(1, skin.dryCloseAlpha ?? 0.6, S.clamp((cam.s - 1.2) / 1.5));
    for (const L of LINES) { const st = lineState(L, t); L.st = st;
      if (!L.noLine && st.end > 0) (skin.stroke || ((c2, L2, d0, d1) => strokePath(c2, L2.path, d0, d1, 3.2, skin.col.stroke)))(c, L, 0, st.end, cam, t);
      for (const u of L.units) for (let wi = u.w0; wi < u.w1; wi++) { const wd = L.words[wi], wgt = L.weight || skin.weight;
        if (u.pre) { const tg = u.t - (skin.ghostLead ?? 0.5);
          if (t < tg) continue;
          if (t < u.t) { drawWord(c, L, wd, skin.col.ghost || skin.col.dry, (skin.ghostAlpha ?? 0.5) * S.clamp((t - tg) / 0.15), 1, skin.ghostWeight || wgt, skin.ghostStyle || ''); continue; } }
        const t0 = u.pre ? u.t : u.t + (wi - u.w0) * u.per - 0.08, dur = u.pre ? 0.01 : Math.min(0.5 * u.per, 0.28); if (t < t0) continue;
        const f = S.clamp((t - t0) / dur), k = S.clamp((t - u.end - 0.10) / 0.35), dry = skin.dryColor ? skin.dryColor(u, L) : skin.col.dry;
        if (k > 0) drawWord(c, L, wd, dry, dryA * k + (1 - k) * 0, f, wgt);
        if (k < 1) drawWord(c, L, wd, skin.col.fresh, 1 - k, f, wgt); } }
    for (const R of SEA) { if (t < R.t0 - 0.08) continue; const f = S.clamp((t - R.t0 + 0.08) / 0.22), k = S.clamp((t - R.t1 - 0.10) / 0.35), last = R === SEA.at(-1);
      const dry = skin.dryColor ? skin.dryColor(R, null) : skin.col.dry;
      R.words.forEach((wd, i) => { const fw = S.clamp(f * R.words.length - i); if (fw <= 0) return;
        if (k > 0 && !last) drawWord(c, { path: R.path, emW: SEA_EM }, wd, dry, k, fw, WF);
        if (k < 1 || last) drawWord(c, { path: R.path, emW: SEA_EM }, wd, skin.col.fresh, last ? 1 : 1 - k, fw, WF); }); }
    for (const L of LINES) if (L.st.tip != null && t < T_OUT0 + 0.2) { const p = L.path.at(L.st.tipD, 4), em = L.emW, off = L.inside ? 0 : L.below ? GAP * em + CAP * em * 0.5 : -GAP * em - CAP * em * 0.5;
      const tp = { x: p.x - Math.sin(p.a) * off, y: p.y + Math.cos(p.a) * off, a: p.a, em, L, writing: L.st.writing }; env.tips.push(tp); (skin.tip || defaultTip)(c, tp, em, cam, t, L); }
  }
  function defaultTip(c, p, em) { c.save(); c.fillStyle = skin.col.fresh; c.shadowColor = skin.col.fresh; c.shadowBlur = 18; c.beginPath(); c.arc(p.x, p.y + em * 0.35, em * 0.11, 0, 7); c.fill(); c.restore(); }

  const env = { S, LINES, SEA, SEA_EM, POSES, strokePath, drawWord, shadowed, wOf, T_OUT0, T_OUT1, DURATION, G, D, FONT, lineOf: id => LINES.find(l => l.id === id) };
  function render(t) {
    const cam = camAt(t), c = ctx; env.cam = cam; env.t = t; env.tips = [];
    c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = 'source-over';
    skin.floor(c, cam, env);
    c.save(); applyCam(c, cam);
    skin.sheet(c, cam, t, env);
    if (skin.under) skin.under(c, cam, t, env);
    if (skin.textErode) { lctx.setTransform(1, 0, 0, 1, 0, 0); lctx.clearRect(0, 0, W, H); lctx.save(); applyCam(lctx, cam); drawLines(lctx, cam, t); if (skin.inkExtras) skin.inkExtras(lctx, cam, t, env);
      lctx.globalCompositeOperation = 'destination-out'; skin.textErode(lctx, cam); lctx.restore(); lctx.globalCompositeOperation = 'source-over';
      c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.drawImage(layer, 0, 0); c.restore(); }
    else { drawLines(c, cam, t); if (skin.inkExtras) skin.inkExtras(c, cam, t, env); }
    if (skin.objects) skin.objects(c, cam, t, env);
    c.restore();
    if (skin.finish) skin.finish(c, cam, env);
    if (q.get('guides')) { c.save(); c.strokeStyle = 'rgba(255,0,255,.7)'; c.lineWidth = 2; c.strokeRect(64, 220, 896, 1380); c.restore(); }
  }
  window.DURATION = DURATION; window.renderAt = t => { render(t); };
  window.STORYBOARD = { extra: skin.debug ? skin.debug() : undefined, em: LINES.map(L => [L.id, +L.emW.toFixed(1), +L.tr.toFixed(1), Math.round(L.path.len), Math.round(L.total)]), finalEm: +SEA_EM.toFixed(1),
    poses: POSES.map(p => ({ line: p.line, x: Math.round(p.x), y: Math.round(p.y), s: +p.s.toFixed(2), th: +(p.th * 180 / Math.PI).toFixed(1), arr: +p.arr.toFixed(2) })) };
  const first = q.get('t'); render(first ? +first : DURATION - 0.1);
}

// finition écran commune : vignette douce + grain fixe très léger
let GRAIN;
export function finish(c, vig = 0.28, grainA = 0.05) {
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
  const g = c.createRadialGradient(W / 2, H / 2, 620, W / 2, H / 2, 1250); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${vig})`); c.fillStyle = g; c.fillRect(0, 0, W, H);
  GRAIN ||= noiseTile(256, 77, (i, j, r) => { const v = r() * 255; return [v, 255]; });
  c.globalAlpha = grainA; c.globalCompositeOperation = 'overlay'; c.fillStyle = c.createPattern(GRAIN, 'repeat'); c.fillRect(0, 0, W, H); c.restore();
}
