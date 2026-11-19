// chemin.js — moteur de l'identité « lyrics-chemin » (vidéo de paroles muette, famille « paroles »).
// Les paroles s'écrivent à plat sur un plan bleu posé au sol, au moment où elles sont chantées ; une caméra verticale
// (translation, rotation, échelle) suit la pointe du tracé en un seul plan-séquence ; zoom arrière final : les lignes
// dessinaient une image (ici un bateau en papier).
//
// Un épisode = un fichier de paroles (?data=…) + un dessin (dessins/<id>.json). Canvas 2D, image par image :
// contrat window.ready / window.renderAt(t) de out/tools/render.mjs. Aucun état entre les images.
// Issu de la maquette de Fable (out/report/notes/lyrics-chemin/proto/scene.html) ; écarts notés dans identity.md.
import * as S from '/out/tools/lib/svi.js';

const W = 1080, H = 1920;
export const COL = { paper: '#1B4C92', paperHi: '#2460AE', paperLo: '#133A74', ink: '#F3F0E4', wet: '#FFD84A', red: '#FF7D5C',
  floor: '#CFC8BA', floorLo: '#B9B1A2' };
const FONT = "'Barlow Condensed'", MONO = "'JetBrains Mono'";
export const ANCHOR = { x: 512, y: 860 };   // point de lecture à l'écran
const LIVE_MIN = 0.30;
const FRAME_W = 780;                         // largeur d'un cadrage à l'écran (dérive et poussée comprises, il reste dans x 64–960)                       // s par mot : en dessous, l'unité est pré-posée au crayon
const CAP = 0.70;                            // hauteur de capitale de Barlow Condensed, en em
const rad = d => d * Math.PI / 180;

// ---------- chemins ----------
function straight(a, b) {
  const dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy), ang = Math.atan2(dy, dx);
  return { len, at: d => ({ x: a[0] + dx * d / len, y: a[1] + dy * d / len, a: ang }) };
}
function wave(x0, x1, y, amp, wl, ph = 0) {
  const N = 400, xs = [], ds = [0]; let px = x0, py = y + amp * Math.sin(ph), d = 0;
  const yAt = x => y + amp * Math.sin(ph + (x - x0) / wl * 2 * Math.PI);
  for (let i = 0; i <= N; i++) { const x = x0 + (x1 - x0) * i / N, yy = yAt(x);
    if (i) { d += Math.hypot(x - px, yy - py); ds.push(d); } xs.push(x); px = x; py = yy; }
  return { len: d, at: dd => { let i = 0; while (i < N - 1 && ds[i + 1] < dd) i++; const k = (dd - ds[i]) / (ds[i + 1] - ds[i] || 1);
    const x = xs[i] + (xs[i + 1] - xs[i]) * k;
    return { x, y: yAt(x), a: Math.atan(amp * 2 * Math.PI / wl * Math.cos(ph + (x - x0) / wl * 2 * Math.PI)) }; } };
}

export async function lancer({ data: defaultData }) {
  const q = new URLSearchParams(location.search);
  const D = await (await fetch(new URL(q.get('data') || defaultData, location.href).href)).json();
  const G = await (await fetch(`/out/shared/chemin-moteur/dessins/${D.dessin || 'bateau'}.json`)).json();
  await S.loadFonts([{ family: 'Barlow Condensed', weight: 700, pkg: 'barlow-condensed' }, { family: 'Barlow Condensed', weight: 800, pkg: 'barlow-condensed' },
    { family: 'JetBrains Mono', weight: 400, pkg: 'jetbrains-mono' }]);

  const BEAT = 60 / D.bpm, DURATION = D.duree, [T_OUT0, T_OUT1] = D.zoomArriere;
  const cv = document.getElementById('c'), ctx = cv.getContext('2d', { willReadFrequently: true });
  const buf = document.createElement('canvas'); buf.width = W; buf.height = H;
  const bctx = buf.getContext('2d', { willReadFrequently: true });
  const SHEET = G.feuille, P = G.points;
  const pt = v => typeof v === 'string' ? P[v] : v;
  const mkPath = c => c.type === 'vague' ? wave(c.x0, c.x1, c.y, c.amp, c.wl, c.ph) : straight(pt(c.a), pt(c.b));

  // ---------- lignes ----------
  const LINES = D.lignes.map(l => {
    const A = G.aretes[l.arete]; if (!A) throw new Error('arête inconnue : ' + l.arete);
    return { ...A, id: l.arete, path: mkPath(A.chemin), u: l.u, cad: l.cad, arr: l.arr, dur: (l.temps || 0) * BEAT, kind: l.kind,
      glide: l.glide, minPx: l.minPx, maxPx: l.maxPx, annotation: l.annotation };
  });
  function wOf(str, weight = 700) { ctx.font = `${weight} 100px ${FONT}`; return ctx.measureText(str).width / 100; }
  for (const L of LINES) {
    const full = L.u.map(u => u[0]).join(' '), n = full.length;
    const usable = L.path.len - L.m[0] - L.m[1], wn = wOf(full), [e0, e1] = L.em || [36, 54];
    const em = S.clamp(usable / (wn + (L.track || 0) * (n - 1)), e0, e1);
    let tr = (L.track || 0) * em;
    if (!L.noFit && !L.track) tr = S.clamp((usable - em * wn) / (n - 1), 0, 0.15 * em);
    const total = em * wn + tr * (n - 1), d0 = L.m[0] + (L.center ? (usable - total) / 2 : 0);
    L.emW = em; L.tr = tr; L.words = []; L.units = []; L.d0 = d0; L.total = total;
    let ci = 0, wi = 0;
    L.u.forEach((u, ui) => {
      const first = L.words.length;
      for (const wd of u[0].split(' ')) { L.words.push({ txt: wd, ui, d0: d0 + em * wOf(full.slice(0, ci)) + tr * ci + (L.gapW || 0) * em * (wi++), w: em * wOf(wd) + tr * (wd.length - 1) }); ci += wd.length + 1; }
      const a = L.words[first], b = L.words.at(-1), nw = L.words.length - first, per = (u[2] - u[1]) / nw;
      L.units.push({ txt: u[0], t: u[1], end: u[2], d0: a.d0, d1: b.d0 + b.w, w0: first, w1: L.words.length, per, pre: per < LIVE_MIN });
    });
    L.textEnd = L.units.at(-1).d1; L.tEnd = L.units.at(-1).end;
  }

  // ---------- la mer : le refrain, en rangs réguliers centrés, même corps, même espace entre tous les mots ----------
  const M = G.mer, RU = D.refrain.u;
  const rowTxt = D.refrain.rangs.map(r => r.map(i => RU[i][0]).join(' '));
  const rowW = s => s.split(' ').reduce((a, w) => a + wOf(w, 800), 0) + (s.split(' ').length - 1) * M.espace;
  const SEA_EM = Math.min(M.emMax, ...rowTxt.map(s => M.largeurMax / rowW(s)));
  const SEA = [];
  D.refrain.rangs.forEach((r, ri) => {
    const R = M.rangs[ri], width = rowW(rowTxt[ri]) * SEA_EM, x0 = M.cx - width / 2;
    const path = wave(x0 - 10, x0 + width + 10, R.y, R.amp, R.wl, R.ph + (x0 - 96) / R.wl * 2 * Math.PI);
    let d = 10;
    r.forEach(i => { const [txt, t0, t1] = RU[i]; const words = [];
      for (const w of txt.split(' ')) { const ww = SEA_EM * wOf(w, 800); words.push({ txt: w, d0: d, w: ww }); d += ww + M.espace * SEA_EM; }
      SEA.push({ path, txt, t0, t1, words, d0: words[0].d0, d1: words.at(-1).d0 + words.at(-1).w }); });
  });

  // ---------- caméra ----------
  let POSES = [];
  for (const L of LINES) {
    L.cad.forEach((g, gi) => {
      const a = L.units[g[0]], b = L.units[g.at(-1)], dc = (a.d0 + b.d1) / 2, p = L.path.at(dc), w = b.d1 - a.d0;
      const lift = L.below ? -L.emW * 0.52 : L.emW * 0.50, nx = Math.sin(p.a), ny = -Math.cos(p.a);
      // corps plancher : 120 px ; 104 si la ligne le permet (passage rapide) ; 92 si tout le cadrage dépasse 4,5 mots/s (ligne entière pré-posée)
      const nWords = g.reduce((k, i) => k + (L.units[i].w1 - L.units[i].w0), 0), fast = (b.end - a.t) / nWords < 0.22;
      const floor = fast ? Math.min(92, L.minPx || 120) : (L.minPx || 120);
      const s = S.clamp(FRAME_W / w, floor / L.emW, (L.maxPx || 220) / L.emW);
      g.forEach(i => { L.units[i].floor = floor; });
      const th = p.a - S.clamp(p.a * 0.1, rad(-6), rad(6));
      const first = gi === 0;
      // priorités : 1) ne pas quitter le mot chanté avant 60 % de sa durée ; 2) arriver au plus tard sur l'attaque ; 3) avance du pré-posé
      let arr = L.arr, dur = L.dur;
      if (!first) {
        const prevU = L.units[g[0] - 1], leaveMin = prevU.t + 0.6 * (prevU.end - prevU.t), lead = a.pre ? BEAT / 2 : 0.06;
        dur = L.glide ? L.glide[gi - 1] : S.clamp((prevU.end - prevU.t) * 0.4, 0.16, 0.24);
        arr = Math.min(a.t, Math.max(a.t - lead, leaveMin + dur)); dur = Math.max(0.12, Math.min(dur, arr - leaveMin));
      }
      POSES.push({ line: L.id, txt: g.map(i => L.units[i].txt).join(' '), x: p.x + nx * lift, y: p.y + ny * lift, s, th, arr, dur,
        kind: first ? L.kind : 'glide', tSing: a.t, tEnd: b.end, pre: g.map(i => L.units[i].pre), dirx: Math.cos(p.a), diry: Math.sin(p.a), w });
    });
  }
  if (D.respiration) {   // recul lent après une phrase isolée : on devine que les lignes dessinent quelque chose
    const r = D.respiration, i = POSES.findIndex(p => p.arr > r.arrivee);
    POSES.splice(i, 0, { line: 'respiration', txt: '(recul)', x: r.x, y: r.y, s: r.zoom, th: rad(r.angle), arr: r.arrivee, dur: r.temps * BEAT,
      kind: 'ease', tSing: null, w: 0, dirx: 1, diry: 0 });
  }
  POSES.push({ line: 'final', txt: '(image d’ensemble)', x: ANCHOR.x, y: ANCHOR.y, s: 1, th: 0, arr: T_OUT1, dur: T_OUT1 - T_OUT0, kind: 'zoomout',
    tSing: null, w: 0, dirx: 0, diry: 0, final: true });
  POSES.forEach((p, i) => { p.leave = i + 1 < POSES.length ? POSES[i + 1].arr - POSES[i + 1].dur : DURATION; });

  function hold(i, t) {   // pose i et sa dérive lente (la caméra accompagne la pointe), vitesse plafonnée à 50 px/s à l'écran
    const p = POSES[i], span = Math.max(0.01, p.leave - p.arr), k = S.clamp((t - p.arr) / span);
    if (p.final) { const e = 1 - Math.pow(1 - S.clamp((t - p.arr) / (DURATION - p.arr)), 2); return { x: p.x, y: p.y, s: p.s * (1 - 0.045 * e), th: 0 }; }
    const amp = Math.min(0.08 * p.w, 40 * span / p.s), pan = (k - 0.5) * amp;
    return { x: p.x + p.dirx * pan, y: p.y + p.diry * pan, s: p.s * (1 + 0.03 * k), th: p.th };
  }
  const EASE = { whip: S.cubicBezier(0.7, 0, 0.2, 1), pivot: S.cubicBezier(0.5, 0, 0.3, 1), glide: S.cubicBezier(0.3, 0, 0.15, 1),
    ease: S.cubicBezier(0.45, 0, 0.55, 1), zoomout: S.cubicBezier(0.5, 0, 0.12, 1), cut: () => 1 };
  const POS_OUT = S.cubicBezier(0.3, 0, 0.1, 1);
  function camAt(t) {
    let i = 0; while (i + 1 < POSES.length && t >= POSES[i + 1].arr) i++;
    const nx = POSES[i + 1];
    if (!nx || t < nx.arr - nx.dur) return hold(i, Math.max(t, POSES[i].arr));
    const a = hold(i, nx.arr - nx.dur), b = hold(i + 1, nx.arr), u = (t - (nx.arr - nx.dur)) / nx.dur, e = EASE[nx.kind](u);
    let dth = b.th - a.th; while (dth > Math.PI) dth -= 2 * Math.PI; while (dth < -Math.PI) dth += 2 * Math.PI;
    const bump = nx.kind === 'whip' ? 1 - 0.28 * Math.sin(Math.PI * u) : nx.kind === 'pivot' ? 1 - 0.30 * Math.sin(Math.PI * u) : 1;
    const ep = nx.kind === 'zoomout' ? POS_OUT(u) : e;   // zoom arrière : la position rejoint le centre plus vite que l'échelle
    return { x: S.lerp(a.x, b.x, ep), y: S.lerp(a.y, b.y, ep), s: Math.exp(S.lerp(Math.log(a.s), Math.log(b.s), e)) * bump, th: a.th + dth * e };
  }
  const toScreen = (cam, wx, wy) => { const c = Math.cos(-cam.th), s = Math.sin(-cam.th), dx = (wx - cam.x) * cam.s, dy = (wy - cam.y) * cam.s;
    return [ANCHOR.x + c * dx - s * dy, ANCHOR.y + s * dx + c * dy]; };
  const toWorld = (cam, sx, sy) => { const c = Math.cos(cam.th), s = Math.sin(cam.th), dx = (sx - ANCHOR.x) / cam.s, dy = (sy - ANCHOR.y) / cam.s;
    return [cam.x + c * dx - s * dy, cam.y + s * dx + c * dy]; };

  // ---------- textures (graine fixe) ----------
  function noiseTile(n, seed, fn) { const c = document.createElement('canvas'); c.width = c.height = n; const x = c.getContext('2d'), im = x.createImageData(n, n), r = S.rng(seed);
    for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { const [v, a] = fn(i, j, r); const o = (j * n + i) * 4; im.data[o] = im.data[o + 1] = im.data[o + 2] = v; im.data[o + 3] = a; }
    x.putImageData(im, 0, 0); return c; }
  const per = (i, j, f, n) => { const x = i / n * f, y = j / n * f, xi = Math.floor(x), yi = Math.floor(y), fx = x - xi, fy = y - yi,
    h = (a, b) => { const qq = Math.sin(((a % f) + f) % f * 127.1 + ((b % f) + f) % f * 311.7) * 43758.5453; return qq - Math.floor(qq); };
    const sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
    return S.lerp(S.lerp(h(xi, yi), h(xi + 1, yi), sx), S.lerp(h(xi, yi + 1), h(xi + 1, yi + 1), sx), sy); };
  const PAT = {
    blotch: noiseTile(256, 3, (i, j) => { const v = per(i, j, 5, 256) * 0.6 + per(i, j, 11, 256) * 0.4; return v > 0.5 ? [255, (v - 0.5) * 2 * 26] : [0, (0.5 - v) * 2 * 34]; }),
    fibre: noiseTile(256, 7, (i, j, r) => { const v = r(); return v > 0.5 ? [255, (v - 0.5) * 30] : [0, (0.5 - v) * 36]; }),
    speck: noiseTile(256, 11, (i, j, r) => { const v = r(), b = per(i, j, 9, 256); return v > 0.93 ? [60, 70] : v < 0.08 ? [255, 60] : [b > 0.5 ? 255 : 0, Math.abs(b - 0.5) * 30]; }),
    grain: noiseTile(256, 19, (i, j, r) => { const v = r(); return [v > 0.5 ? 255 : 0, Math.abs(v - 0.5) * 22]; }),
    wood: noiseTile(64, 23, (i, j) => { const v = per(i, j * 0.15, 8, 64); return [v > 0.5 ? 255 : 60, Math.abs(v - 0.5) * 70]; }),
  };
  const pats = {};
  function pat(c, k) { return c.createPattern(PAT[k], 'repeat'); }

  // ---------- encre et mots ----------
  const inkColor = (t, end) => S.mix(COL.wet, COL.ink, S.clamp((t - (end + 0.10)) / 0.35));
  function drawWord(c, L, wd, fill, alpha = 1, f = 1, weight = 700, gap = 0.16) {   // mot rigide posé sur le chemin, révélé de gauche à droite (f)
    if (f <= 0 || alpha <= 0) return;
    const p = L.path.at(wd.d0 + wd.w / 2), em = L.emW, by = L.below ? em * 0.88 : -gap * em;
    c.save(); c.translate(p.x, p.y); c.rotate(p.a); c.globalAlpha = alpha; c.fillStyle = fill;
    if (f < 1) { c.beginPath(); c.rect(-wd.w / 2 - 3, by - em * 1.1, (wd.w + 6) * f, em * 1.5); c.clip(); }
    c.font = `${weight} ${em}px ${FONT}`; c.letterSpacing = (L.tr || 0) + 'px'; c.textAlign = 'left'; c.textBaseline = 'alphabetic'; c.fillText(wd.txt, -wd.w / 2, by); c.restore();
  }
  function wordBox(L, wd, gap = 0.16) {   // 4 coins (monde) de la boîte des capitales d'un mot
    const p = L.path.at(wd.d0 + wd.w / 2), em = L.emW, by = L.below ? em * 0.88 : -gap * em, c = Math.cos(p.a), s = Math.sin(p.a);
    return [[-wd.w / 2, by - CAP * em], [wd.w / 2, by - CAP * em], [wd.w / 2, by], [-wd.w / 2, by]].map(([x, y]) => [p.x + c * x - s * y, p.y + s * x + c * y]);
  }
  function strokePath(c, path, d0, d1, lw, col, dash) {
    if (d1 <= d0) return; c.beginPath(); const n = Math.max(2, Math.ceil((d1 - d0) / 6));
    for (let i = 0; i <= n; i++) { const p = path.at(d0 + (d1 - d0) * i / n); i ? c.lineTo(p.x, p.y) : c.moveTo(p.x, p.y); }
    c.lineWidth = lw; c.strokeStyle = col; c.lineCap = 'round'; c.lineJoin = 'round'; if (dash) c.setLineDash(dash); c.stroke(); c.setLineDash([]);
  }
  const writeDur = u => Math.min(0.5 * (u.end - u.t), 0.28);
  function tipOf(L, t) {   // position de la pointe le long de la ligne
    let d = null, writing = false;
    for (const u of L.units) {
      if (u.pre) { if (t >= u.t) d = u.d1; continue; }
      const f = S.clamp((t - (u.t - 0.08)) / writeDur(u));
      if (f > 0) { d = u.d0 + (u.d1 - u.d0) * f; writing = f < 1; }
    }
    return d === null ? null : { d, writing };
  }
  function shadowed(c, cam, fn, blur = 14, ox = 9, oy = 13, a = 0.38) {   // ombre attachée à la lumière du monde
    c.save(); c.shadowColor = `rgba(4,14,40,${a})`; c.shadowBlur = blur * cam.s;
    const co = Math.cos(-cam.th), si = Math.sin(-cam.th);
    c.shadowOffsetX = (ox * co - oy * si) * cam.s; c.shadowOffsetY = (ox * si + oy * co) * cam.s; fn(); c.restore();
  }
  const rr = (c, x, y, w, h, r) => { c.beginPath(); c.roundRect(x, y, w, h, r); };
  const lin = (c, x0, y0, x1, y1, stops) => { const g = c.createLinearGradient(x0, y0, x1, y1); stops.forEach(([k, col]) => g.addColorStop(k, col)); return g; };

  // ---------- objets posés (les seules choses qui ont une épaisseur) ----------
  function tape(c, cam, w, h, seed) {   // ruban de masquage translucide, bouts déchirés
    const r = S.rng(seed), edge = (x, sgn) => { const pts = []; for (let k = 0; k <= 8; k++) pts.push([x + sgn * (r() * 5 - 1), -h / 2 + h * k / 8]); return pts; };
    const L = edge(-w / 2, -1), Rr = edge(w / 2, 1).reverse();
    const shape = () => { c.beginPath(); L.forEach(([x, y], i) => i ? c.lineTo(x, y) : c.moveTo(x, y)); Rr.forEach(([x, y]) => c.lineTo(x, y)); c.closePath(); };
    shadowed(c, cam, () => { c.fillStyle = 'rgba(233,223,195,0.9)'; shape(); c.fill(); }, 4, 2, 3, 0.22);
    c.fillStyle = lin(c, 0, -h / 2, 0, h / 2, [[0, 'rgba(241,233,208,0.86)'], [0.5, 'rgba(232,222,193,0.80)'], [1, 'rgba(221,209,176,0.86)']]); shape(); c.fill();
    c.save(); shape(); c.clip(); c.globalAlpha = 0.5; c.fillStyle = pat(c, 'fibre'); c.fillRect(-w, -h, 2 * w, 2 * h); c.restore();
    c.strokeStyle = 'rgba(255,255,255,0.35)'; c.lineWidth = 1.2; c.beginPath(); c.moveTo(-w / 2 + 4, -h / 2 + 1.5); c.lineTo(w / 2 - 4, -h / 2 + 1.5); c.stroke();
  }
  function drawObjects(c, cam) {
    const O = G.objets;
    [[SHEET.x, SHEET.y, -45], [SHEET.x + SHEET.w, SHEET.y, 45], [SHEET.x, SHEET.y + SHEET.h, 45], [SHEET.x + SHEET.w, SHEET.y + SHEET.h, -45]].forEach(([tx, ty, r], i) => {
      c.save(); c.translate(tx, ty); c.rotate(rad(r + (i % 2 ? 3 : -2))); tape(c, cam, 124, 34, 31 + i); c.restore(); });
    if (O.tasse) {   // tasse vue de dessus : auréole sèche, bord éclairé, paroi intérieure, ménisque, reflet de fenêtre
      c.save(); c.translate(O.tasse.x, O.tasse.y);
      const rs = S.rng(41); for (let k = 0; k < 3; k++) { c.strokeStyle = `rgba(20,24,40,${0.10 + 0.05 * k})`; c.lineWidth = 2 + 3 * rs(); c.beginPath(); c.arc(-88 + rs() * 3, 118 + rs() * 3, 50 + k * 1.5, 0.3 + rs() * 0.4, 5.3 + rs() * 0.5); c.stroke(); }
      c.fillStyle = 'rgba(30,22,30,0.06)'; c.beginPath(); c.arc(-88, 118, 49, 0, 7); c.fill();
      shadowed(c, cam, () => { c.fillStyle = '#EDE8DC'; c.beginPath(); c.arc(0, 0, 56, 0, 7); c.fill(); rr(c, -80, -12, 32, 24, 10); c.fill(); }, 20, 12, 17, 0.45);
      c.fillStyle = lin(c, -80, -12, -80, 12, [[0, '#F6F2E8'], [0.5, '#E6E0D2'], [1, '#CFC8B8']]); rr(c, -80, -12, 32, 24, 10); c.fill();
      c.fillStyle = 'rgba(40,30,20,0.25)'; rr(c, -72, -5, 16, 10, 5); c.fill();
      c.fillStyle = lin(c, -50, -50, 50, 50, [[0, '#FBF8F0'], [0.6, '#E9E3D5'], [1, '#CEC6B4']]); c.beginPath(); c.arc(0, 0, 56, 0, 7); c.fill();
      c.fillStyle = lin(c, -40, -40, 40, 40, [[0, '#BDB5A3'], [0.5, '#DDD7C9'], [1, '#F2EEE4']]); c.beginPath(); c.arc(0, 0, 49, 0, 7); c.fill();
      const g = c.createRadialGradient(-10, -12, 4, 0, 0, 46); g.addColorStop(0, '#6A4528'); g.addColorStop(0.7, '#3A2413'); g.addColorStop(1, '#25160B');
      c.fillStyle = g; c.beginPath(); c.arc(0, 0, 45, 0, 7); c.fill();
      c.strokeStyle = 'rgba(176,128,80,0.55)'; c.lineWidth = 2.2; c.beginPath(); c.arc(0, 0, 44, 0, 7); c.stroke();   // ménisque
      c.fillStyle = 'rgba(205,160,110,0.18)'; for (let k = 0; k < 14; k++) { const a = rs() * 7, d = 28 + rs() * 14; c.beginPath(); c.arc(Math.cos(a) * d, Math.sin(a) * d, 1 + rs() * 2, 0, 7); c.fill(); }
      c.save(); c.beginPath(); c.arc(0, 0, 45, 0, 7); c.clip(); c.rotate(-0.6); c.fillStyle = 'rgba(255,255,255,0.16)'; rr(c, -8, -38, 26, 14, 4); c.fill(); rr(c, 22, -38, 12, 14, 4); c.fill(); c.restore();
      c.strokeStyle = 'rgba(255,255,255,0.55)'; c.lineWidth = 2; c.beginPath(); c.arc(0, 0, 54, 3.4, 4.6); c.stroke();
      c.restore();
    }
    if (O.crayon) {   // crayon : trois facettes, cône de bois veiné, mine, virole cannelée, gomme
      c.save(); c.translate(O.crayon.x, O.crayon.y); c.rotate(rad(O.crayon.angle));
      const body = () => { c.beginPath(); c.moveTo(-122, -8); c.lineTo(84, -8); c.lineTo(118, 0); c.lineTo(84, 8); c.lineTo(-122, 8); c.closePath(); c.fill(); };
      shadowed(c, cam, () => { c.fillStyle = '#F2C230'; body(); }, 9, 6, 9, 0.45);
      c.fillStyle = '#FFDE6E'; c.fillRect(-98, -8, 182, 5.3); c.fillStyle = '#F2C230'; c.fillRect(-98, -2.7, 182, 5.4); c.fillStyle = '#C9921A'; c.fillRect(-98, 2.7, 182, 5.3);
      c.fillStyle = 'rgba(255,255,255,0.35)'; c.fillRect(-98, -6.6, 182, 1.2);
      c.save(); c.beginPath(); c.moveTo(84, -8); c.lineTo(118, 0); c.lineTo(84, 8); c.closePath(); c.clip();
      c.fillStyle = lin(c, 0, -8, 0, 8, [[0, '#F1DDBA'], [0.5, '#E2C79C'], [1, '#C7A676']]); c.fillRect(82, -9, 40, 18);
      c.strokeStyle = 'rgba(150,105,60,0.45)'; c.lineWidth = 0.9; [-4, 0, 4].forEach(y => { c.beginPath(); c.moveTo(84, y); c.quadraticCurveTo(98, y * 0.6, 112, y * 0.2); c.stroke(); });
      c.restore();
      c.fillStyle = '#2B2B2B'; c.beginPath(); c.moveTo(106, -2.8); c.lineTo(118, 0); c.lineTo(106, 2.8); c.closePath(); c.fill();
      c.fillStyle = 'rgba(255,255,255,0.35)'; c.beginPath(); c.moveTo(108, -1.6); c.lineTo(116, -0.3); c.lineTo(108, -0.6); c.fill();
      c.fillStyle = lin(c, 0, -8, 0, 8, [[0, '#E2E6EC'], [0.45, '#AEB4BE'], [1, '#7D838D']]); c.fillRect(-108, -8.5, 12, 17);
      c.strokeStyle = 'rgba(60,64,72,0.5)'; c.lineWidth = 0.8; [-105, -102, -99].forEach(x => { c.beginPath(); c.moveTo(x, -8.5); c.lineTo(x, 8.5); c.stroke(); });
      c.fillStyle = lin(c, 0, -8, 0, 8, [[0, '#F7A797'], [1, '#D9705E']]); rr(c, -122, -8, 16, 16, 4); c.fill();
      c.restore();
    }
    if (O.cle) {   // clé en laiton : dégradé, biseau, dents
      c.save(); c.translate(O.cle.x, O.cle.y); c.rotate(rad(O.cle.angle));
      const key = () => { c.beginPath(); c.arc(-34, 0, 21, 0, 7); c.rect(-16, -5, 76, 10); c.moveTo(34, 4); c.lineTo(42, 4); c.lineTo(42, 15); c.lineTo(38, 17); c.lineTo(34, 15); c.closePath();
        c.moveTo(47, 4); c.lineTo(56, 4); c.lineTo(56, 12); c.lineTo(51, 14); c.lineTo(47, 12); c.closePath(); c.fill('nonzero'); };
      shadowed(c, cam, () => { c.fillStyle = '#C9A24A'; key(); }, 7, 5, 7, 0.5);
      c.fillStyle = lin(c, -50, -20, 50, 20, [[0, '#E9CC7E'], [0.45, '#C9A24A'], [1, '#9C7A2E']]); key();
      c.strokeStyle = 'rgba(255,240,190,0.7)'; c.lineWidth = 1.6; c.beginPath(); c.arc(-34, 0, 18, 3.6, 5.4); c.stroke(); c.beginPath(); c.moveTo(-14, -3.4); c.lineTo(58, -3.4); c.stroke();
      c.strokeStyle = 'rgba(90,64,20,0.5)'; c.lineWidth = 1.2; c.beginPath(); c.arc(-34, 0, 13, 0.4, 2.6); c.stroke();
      c.fillStyle = COL.paper; c.beginPath(); c.arc(-40, 0, 8, 0, 7); c.fill();
      c.fillStyle = 'rgba(4,14,40,0.35)'; c.beginPath(); c.arc(-39, 1.5, 8, 0, 7); c.fill();
      c.restore();
    }
    if (O.note) {   // note collée : coin relevé, trois traits au stylo, ruban
      c.save(); c.translate(O.note.x, O.note.y); c.rotate(rad(O.note.angle));
      const sq = () => { c.beginPath(); c.moveTo(-56, -56); c.lineTo(56, -56); c.lineTo(56, 34); c.quadraticCurveTo(50, 50, 32, 56); c.lineTo(-56, 56); c.closePath(); };
      shadowed(c, cam, () => { c.fillStyle = '#F4E6A6'; sq(); c.fill(); }, 12, 7, 11, 0.4);
      shadowed(c, cam, () => { c.fillStyle = 'rgba(0,0,0,0)'; c.beginPath(); c.moveTo(56, 30); c.quadraticCurveTo(52, 52, 28, 56); c.lineTo(40, 40); c.closePath(); c.fillStyle = '#E9D88F'; c.fill(); }, 16, 10, 14, 0.35);
      c.fillStyle = lin(c, -56, -56, 56, 56, [[0, '#FAF0BE'], [0.75, '#EEDD96'], [1, '#D9C67A']]); sq(); c.fill();
      c.fillStyle = lin(c, 56, 30, 30, 56, [[0, '#FFF6CF'], [1, '#E2CF84']]); c.beginPath(); c.moveTo(56, 34); c.quadraticCurveTo(46, 40, 32, 56); c.quadraticCurveTo(50, 50, 56, 34); c.fill();
      c.strokeStyle = 'rgba(40,50,80,0.6)'; c.lineWidth = 3.4; c.lineCap = 'round';
      [[-38, -22, 34], [-38, 0, 44], [-38, 22, 16]].forEach(([x, y, w]) => { c.beginPath(); c.moveTo(x, y); c.quadraticCurveTo(x + w * 0.5, y - 3, x + w + 26, y - 1); c.stroke(); });
      c.save(); c.translate(0, -56); c.rotate(rad(-4)); tape(c, cam, 62, 22, 57); c.restore();
      c.restore();
    }
  }

  // ---------- sol et feuille ----------
  function drawFloor(c) {
    c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.fillStyle = COL.floor; c.fillRect(0, 0, W, H); c.restore();
    c.save(); c.fillStyle = pat(c, 'speck'); c.scale(1.5, 1.5); c.fillRect(-2000, -2000, 5000, 5000); c.restore();
  }
  function drawSheet(c, cam) {
    const { x, y, w, h } = SHEET, px = 1 / cam.s;   // px = un pixel écran, en unités monde
    shadowed(c, cam, () => { c.fillStyle = COL.paper; c.fillRect(x, y, w, h); }, 26, 12, 18, 0.45);
    c.fillStyle = lin(c, x, y, x + w, y + h, [[0, COL.paperHi], [0.55, COL.paper], [1, COL.paperLo]]); c.fillRect(x, y, w, h);
    c.save(); c.beginPath(); c.rect(x, y, w, h); c.clip();
    // facettes : chaque panneau plié prend la lumière un peu différemment (cassure de lumière, sans bande)
    const cols = [x, 540, x + w], rows = [0, 1, 2, 3, 4].map(k => y + h * k / 4);
    for (let i = 0; i < 2; i++) for (let j = 0; j < 4; j++) { const v = ((i + j) % 2 ? 1 : -1) * (0.022 + 0.008 * ((i * 3 + j) % 3));
      c.fillStyle = v > 0 ? `rgba(255,255,255,${v})` : `rgba(0,8,30,${-v})`; c.fillRect(cols[i], rows[j], cols[i + 1] - cols[i], rows[j + 1] - rows[j]); }
    c.save(); c.scale(4, 4); c.fillStyle = pat(c, 'blotch'); c.fillRect(0, 0, 300, 480); c.restore();
    c.save(); c.scale(0.75, 0.75); c.fillStyle = pat(c, 'fibre'); c.fillRect(0, 0, 1500, 2500); c.restore();
    // quadrillage : 1 px écran
    const aMin = 0.035 + 0.035 * S.clamp((cam.s - 1) / 2);
    c.lineWidth = Math.max(px, 0.5); c.strokeStyle = `rgba(255,255,255,${aMin})`; c.beginPath();
    for (let gx = 40; gx < x + w; gx += 20) if (gx % 100) { c.moveTo(gx, y); c.lineTo(gx, y + h); }
    for (let gy = 100; gy < y + h; gy += 20) if (gy % 100) { c.moveTo(x, gy); c.lineTo(x + w, gy); } c.stroke();
    c.lineWidth = Math.max(1.4 * px, 0.8); c.strokeStyle = 'rgba(255,255,255,0.10)'; c.beginPath();
    for (let gx = 100; gx < x + w; gx += 100) { c.moveTo(gx, y); c.lineTo(gx, y + h); }
    for (let gy = 100; gy < y + h; gy += 100) { c.moveTo(x, gy); c.lineTo(x + w, gy); } c.stroke();
    // plis : largeur constante à l'écran (≈ 10 px de halo, arête nette de 1,5 px claire / 1,5 px sombre)
    const hw = Math.min(14, 10 * px), e = Math.max(1.5 * px, 0.6);
    const crease = (x0, y0, x1, y1) => { const vert = x0 === x1;
      const gg = vert ? c.createLinearGradient(x0 - hw, 0, x0 + hw, 0) : c.createLinearGradient(0, y0 - hw, 0, y0 + hw);
      gg.addColorStop(0, 'rgba(255,255,255,0)'); gg.addColorStop(0.5, 'rgba(255,255,255,0.07)'); gg.addColorStop(0.5, 'rgba(0,10,40,0.08)'); gg.addColorStop(1, 'rgba(0,10,40,0)');
      c.fillStyle = gg; vert ? c.fillRect(x0 - hw, y0, 2 * hw, y1 - y0) : c.fillRect(x0, y0 - hw, x1 - x0, 2 * hw);
      c.fillStyle = 'rgba(255,255,255,0.20)'; vert ? c.fillRect(x0 - e, y0, e, y1 - y0) : c.fillRect(x0, y0 - e, x1 - x0, e);
      c.fillStyle = 'rgba(0,10,40,0.22)'; vert ? c.fillRect(x0, y0, e, y1 - y0) : c.fillRect(x0, y0, x1 - x0, e); };
    crease(540, y, 540, y + h); [1, 2, 3].forEach(k => crease(x, y + h * k / 4, x + w, y + h * k / 4));
    c.strokeStyle = 'rgba(243,240,228,0.42)'; c.lineWidth = 2; c.strokeRect(x + 22, y + 22, w - 44, h - 44);
    c.fillStyle = 'rgba(243,240,228,0.55)'; c.font = `400 15px ${MONO}`; c.textAlign = 'left'; c.textBaseline = 'alphabetic'; c.fillText('PL. 01 — 1:1', x + 36, y + 52);
    c.restore();
  }

  // ---------- le dessin ----------
  const TITLE = LINES.find(L => L.guide);
  function drawConstruction(c, cam, t) {   // repères d'architecte autour du titre, visibles dès l'image 0
    if (!TITLE) return;
    const a = TITLE.path.at(TITLE.d0), b = TITLE.path.at(TITLE.d0 + TITLE.total), em = TITLE.emW, px = 1 / cam.s;
    const k = S.seg(t, -0.25, 0.55, S.ease.outCubic), mid = (a.x + b.x) / 2, yd = a.y - em * 1.22;
    c.save(); c.strokeStyle = 'rgba(243,240,228,0.5)'; c.fillStyle = 'rgba(243,240,228,0.55)'; c.lineWidth = Math.max(1.6 * px, 0.7);
    const half = (b.x - a.x) / 2 * k;
    c.beginPath(); c.moveTo(mid - half, yd); c.lineTo(mid + half, yd); c.stroke();   // cote
    if (k > 0.98) { [a.x, b.x].forEach(xx => { c.beginPath(); c.moveTo(xx, yd - 7); c.lineTo(xx, yd + 7); c.moveTo(xx - 5, yd + 5); c.lineTo(xx + 5, yd - 5); c.stroke(); }); }
    c.font = `400 ${11}px ${MONO}`; c.textAlign = 'center'; c.globalAlpha = S.seg(t, 0.2, 0.6);
    c.save(); c.fillStyle = COL.paper; c.fillRect(mid - 20, yd - 7, 40, 13); c.restore(); c.fillText(String(Math.round(b.x - a.x)), mid, yd + 4);
    c.globalAlpha = 1;
    [[a.x - 18, a.y + 4], [b.x + 18, a.y + 4]].forEach(([xx, yy]) => { c.beginPath(); c.moveTo(xx - 6, yy); c.lineTo(xx + 6, yy); c.moveTo(xx, yy - 6); c.lineTo(xx, yy + 6); c.stroke(); });   // croix de repère
    c.setLineDash([5, 6]); c.strokeStyle = 'rgba(243,240,228,0.32)';   // ligne de construction sous le titre, tirée par la pointe
    const tip = tipOf(TITLE, t), gx = tip ? Math.max(a.x + (b.x - a.x) * S.seg(t, -0.2, 0.0), TITLE.path.at(tip.d).x + 0.3 * em) : a.x;
    c.beginPath(); c.moveTo(a.x - 30, a.y + 9); c.lineTo(Math.min(b.x + 30, gx), a.y + 9); c.stroke(); c.setLineDash([]);
    c.restore();
  }
  function drawBoat(c, cam, t) {
    const lwLine = 3.2, zk = S.clamp((cam.s - 1.2) / 1.5);
    if (G.mat) {   // mât en pointillé : se trace pendant l'arrivée sur la ligne indiquée
      const mast = straight(pt(G.mat.a), pt(G.mat.b)), Lm = LINES.find(L => L.id === G.mat.pendant);
      const km = Lm ? S.seg(t, Lm.arr - Lm.dur, Lm.arr, S.ease.inOutCubic) : 1;
      strokePath(c, mast, 0, mast.len * km, 2.2, 'rgba(243,240,228,0.7)', [9, 9]);
    }
    const dryA = S.lerp(1, 0.6, zk);   // l'encre sèche s'efface un peu en gros plan : le mot chanté domine
    for (const L of LINES) {
      const tip = tipOf(L, t), endK = S.seg(t, L.tEnd + 0.05, L.tEnd + 0.4, S.ease.outCubic);
      if (!L.noLine && tip) {
        const d1 = S.lerp(Math.min(L.path.len, tip.d + 0.3 * L.emW), L.path.len, endK);
        c.globalAlpha = S.lerp(1, 0.75, zk); strokePath(c, L.path, 0, d1, lwLine, COL.ink); c.globalAlpha = 1;
      }
      for (const u of L.units) {
        const words = L.words.slice(u.w0, u.w1), dry = t > u.end + 0.45 ? dryA : 1;
        const frac = (wd, d) => S.clamp((d - wd.d0) / wd.w);
        if (u.pre) {
          const pose = POSES.find(p => p.line === L.id && p.tSing !== null && p.tSing <= u.t && u.t < p.tEnd + 1e-6) || POSES.find(p => p.line === L.id);
          const tG = Math.max(pose.arr - 0.04, u.t - BEAT), kg = S.clamp((t - tG) / 0.15);
          if (t >= u.t) words.forEach(wd => drawWord(c, L, wd, inkColor(t, u.end), dry));
          else words.forEach(wd => drawWord(c, L, wd, COL.ink, 0.5, frac(wd, u.d0 + (u.d1 - u.d0) * kg)));   // pré-posé au crayon
        } else {
          const f = S.clamp((t - (u.t - 0.08)) / writeDur(u));
          words.forEach(wd => drawWord(c, L, wd, inkColor(t, u.end), dry, frac(wd, u.d0 + (u.d1 - u.d0) * f)));
        }
      }
      if (tip && (tip.writing || (L === TITLE && t < 0.3))) { const p = L.path.at(tip.d), r = L.emW * 0.11;
        c.save(); c.shadowColor = COL.wet; c.shadowBlur = 16 * cam.s; c.fillStyle = COL.wet; c.beginPath(); c.arc(p.x, p.y + (L.noLine ? 9 : 0), r, 0, 7); c.fill(); c.restore(); }
      drawAnnotation(c, L, t);
    }
    // la mer : le refrain
    for (const s of SEA) {
      const wdur = Math.min(0.5 * (s.t1 - s.t0), 0.3), f = S.clamp((t - (s.t0 - 0.08)) / wdur), d = s.d0 + (s.d1 - s.d0) * f;
      s.words.forEach(wd => drawWord(c, { path: s.path, emW: SEA_EM }, wd, inkColor(t, s.t1), 1, S.clamp((d - wd.d0) / wd.w), 800, 0));
    }
    // suite de la première vague et filets d'eau, tracés pendant le zoom arrière
    const V = LINES.find(L => L.id === 'vague1'), t0 = SEA.length ? SEA[0].t0 : T_OUT0, kw = S.seg(t, t0, t0 + 1.4, S.ease.inOutCubic);
    if (kw > 0 && V && M.suiteVague1) { const ch = V.chemin, w2 = wave(M.suiteVague1.x0, M.suiteVague1.x1, ch.y, ch.amp, ch.wl, ch.ph + (M.suiteVague1.x0 - ch.x0) / ch.wl * 2 * Math.PI);
      strokePath(c, w2, 0, w2.len * kw, 3.2, COL.ink);
      (M.filets || []).forEach(([y, x0, x1, ph], i) => { const w3 = wave(x0, x1, y, 10, 300, ph), k3 = S.seg(t, T_OUT0 + 0.685 + i * 0.35, T_OUT0 + 2.085 + i * 0.35, S.ease.inOutCubic);
        c.globalAlpha = 0.55; strokePath(c, w3, 0, w3.len * k3, 2.6, COL.ink); c.globalAlpha = 1; }); }
  }
  function drawAnnotation(c, L, t) {   // annotations au crayon rouge, accrochées à la mise en page (jamais du texte)
    const A = L.annotation; if (!A) return;
    const k = S.seg(t, A.t, A.t + A.d, S.ease.inOutCubic); if (k <= 0) return;
    c.save(); c.strokeStyle = COL.red; c.lineCap = 'round'; c.lineJoin = 'round';
    if (A.type === 'croix') {   // croix en marge, à côté du dernier mot de l'unité
      const u = L.units[A.unite || 0], wd = L.words[u.w1 - 1], p = L.path.at(wd.d0 + wd.w / 2), em = L.emW;
      const ly = (L.below ? 1 : -1) * em * 1.75, cx = p.x - Math.sin(p.a) * ly, cy = p.y + Math.cos(p.a) * ly, s = 13;
      c.lineWidth = 3.2; c.beginPath(); const k1 = Math.min(1, k * 2), k2 = S.clamp(k * 2 - 1);
      c.moveTo(cx - s, cy - s); c.lineTo(cx - s + 2 * s * k1, cy - s + 2 * s * k1);
      if (k2 > 0) { c.moveTo(cx + s, cy - s); c.lineTo(cx + s - 2 * s * k2, cy - s + 2 * s * k2); } c.stroke();
    } else if (A.type === 'fanion') {   // drapeau autour de la ligne isolée
      const a = L.path.at(0), fw = L.textEnd + 44, x0 = a.x - 16, yT = a.y - 46, yB = a.y + 18;
      const pts = [[x0, yT], [x0 + fw, yT], [x0 + fw - 26, (yT + yB) / 2], [x0 + fw, yB], [x0, yB]];
      const seg = pts.map((p, i) => straight(p, pts[(i + 1) % 5])), tot = seg.reduce((s2, sg) => s2 + sg.len, 0); let rem = tot * k;
      for (const sg of seg) { strokePath(c, sg, 0, Math.min(sg.len, rem), 3, COL.red); rem -= sg.len; if (rem <= 0) break; }
    } else if (A.type === 'boucle') {   // boucle de correcteur autour de toute la ligne
      const mid = L.path.at((L.units[0].d0 + L.textEnd) / 2), rw = (L.textEnd - L.units[0].d0) / 2 + 14, rh = L.emW * 0.58, sg = L.below ? 1 : -1;
      c.translate(mid.x - Math.sin(mid.a) * L.emW * 0.52 * sg, mid.y + Math.cos(mid.a) * L.emW * 0.52 * sg); c.rotate(mid.a - 0.03);
      c.beginPath(); c.ellipse(0, 0, rw, rh, 0, -2.6, -2.6 + k * 6.6); c.lineWidth = 3; c.stroke();
    }
    c.restore();
  }

  // ---------- une image ----------
  function renderScene(c, t) {
    const cam = camAt(t);
    c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1;
    c.translate(ANCHOR.x, ANCHOR.y); c.rotate(-cam.th); c.scale(cam.s, cam.s); c.translate(-cam.x, -cam.y);
    drawFloor(c); drawSheet(c, cam); drawConstruction(c, cam, t); drawBoat(c, cam, t); drawObjects(c, cam);
    c.setTransform(1, 0, 0, 1, 0, 0);   // finition écran : vignette douce + grain fixe
    const v = c.createRadialGradient(W / 2, H * 0.47, H * 0.28, W / 2, H * 0.5, H * 0.74); v.addColorStop(0, 'rgba(3,10,30,0)'); v.addColorStop(1, 'rgba(3,10,30,0.34)');
    c.fillStyle = v; c.fillRect(0, 0, W, H);
    c.fillStyle = pat(c, 'grain'); c.fillRect(0, 0, W, H);
  }
  // flou de mouvement : obturateur 180° (1/60 s), N sous-images au pas de 3 px du point le plus rapide (coins compris),
  // 64 au plus (au-delà on raccourcit l'obturateur plutôt que d'espacer les copies), moyenne en flottants.
  const SH = 1 / 60, STEP = 3, NMAX = 64, PROBES = [[0, 0], [W, 0], [0, H], [W, H], [ANCHOR.x, ANCHOR.y], [W / 2, 0], [W / 2, H], [0, H / 2], [W, H / 2]];
  function travel(t0, t1) { const a = camAt(t0), b = camAt(t1); let m = 0;
    for (const [x, y] of PROBES) { const [wx, wy] = toWorld(a, x, y), [sx, sy] = toScreen(b, wx, wy); m = Math.max(m, Math.hypot(sx - x, sy - y)); } return m; }
  let acc = null;
  function render(t) {
    t = Math.min(t, DURATION);
    const disp = travel(t - SH, t);
    if (disp < 2) { renderScene(ctx, t); return; }
    let n = Math.ceil(disp / STEP) + 1, sh = SH;
    if (n > NMAX) { sh = SH * (NMAX - 1) * STEP / disp; n = NMAX; }
    if (!acc) acc = new Float32Array(W * H * 3); else acc.fill(0);
    for (let i = 0; i < n; i++) {
      renderScene(bctx, t - sh * i / (n - 1));
      const d = bctx.getImageData(0, 0, W, H).data;
      for (let p = 0, q = 0; p < d.length; p += 4, q += 3) { acc[q] += d[p]; acc[q + 1] += d[p + 1]; acc[q + 2] += d[p + 2]; }
    }
    const out = ctx.createImageData(W, H), o = out.data;
    for (let p = 0, q = 0; p < o.length; p += 4, q += 3) { o[p] = acc[q] / n + 0.5; o[p + 1] = acc[q + 1] / n + 0.5; o[p + 2] = acc[q + 2] / n + 0.5; o[p + 3] = 255; }
    ctx.putImageData(out, 0, 0);
  }

  // ---------- mesure (audit) ----------
  function metrics(t) {
    const cam = camAt(t), sung = [];
    for (const L of LINES) for (const u of L.units) if (t >= u.t && t < u.end) {
      let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
      for (const wd of L.words.slice(u.w0, u.w1)) for (const [wx, wy] of wordBox(L, wd)) { const [sx, sy] = toScreen(cam, wx, wy); x0 = Math.min(x0, sx); x1 = Math.max(x1, sx); y0 = Math.min(y0, sy); y1 = Math.max(y1, sy); }
      sung.push({ line: L.id, txt: u.txt, pre: u.pre, per: u.per, t: u.t, end: u.end, px: L.emW * cam.s, floor: u.floor, maxPx: L.maxPx || 220, box: [x0, y0, x1, y1] });
    }
    return { cam: { ...cam, th: cam.th * 180 / Math.PI }, sung, disp: travel(t - SH, t) };
  }
  // boîtes de tous les mots dans l'image finale (zoom 1) : contrôle des chevauchements
  function finalBoxes() {
    const out = [];
    for (const L of LINES) for (const wd of L.words) out.push({ line: L.id, txt: wd.txt, poly: wordBox(L, wd) });
    for (const s of SEA) for (const wd of s.words) out.push({ line: 'mer', txt: wd.txt, poly: wordBox({ path: s.path, emW: SEA_EM }, wd, 0) });
    return out;
  }

  window.DURATION = DURATION;
  window.renderAt = t => { render(t); };
  window.chemin = { metrics, finalBoxes, poses: POSES, beat: BEAT, duree: DURATION, zoomArriere: D.zoomArriere, seaEm: SEA_EM };
  window.STORYBOARD = { poses: POSES.map(p => ({ ...p, th: +(p.th * 180 / Math.PI).toFixed(1), x: Math.round(p.x), y: Math.round(p.y), s: +p.s.toFixed(2) })),
    lines: LINES.map(L => ({ id: L.id, em: +L.emW.toFixed(1), track: +L.tr.toFixed(1), len: Math.round(L.path.len), units: L.units.map(u => ({ txt: u.txt, t: u.t, end: u.end, per: +u.per.toFixed(2), pre: u.pre })) })),
    refrain: { em: +SEA_EM.toFixed(1), rangs: rowTxt.length } };
  if (q.has('guides')) S.guides();
}
