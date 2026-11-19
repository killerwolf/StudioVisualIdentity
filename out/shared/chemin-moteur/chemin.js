// chemin.js — moteur de l'identité « lyrics-chemin » (famille « paroles », et ses déclinaisons narrées).
// Le texte s'écrit à plat sur une surface au moment où il est chanté ou dit ; une caméra verticale (translation, rotation,
// échelle) suit la pointe du tracé en un seul plan-séquence ; zoom arrière final : les lignes dessinaient une image.
//
// Un épisode = un fichier (?data=…) qui nomme un dessin (dessins/<id>.json) et un habillage (habillages/<id>.js, défaut
// « plan-bleu »). Le moteur garde la mise en page des mots, la pose de l'encre, la caméra, le flou de mouvement et les mesures
// de l'audit ; l'habillage ne fournit que la matière (sol, feuille, objets, pointe, couleurs, polices, décor du dessin).
// Canvas 2D, image par image : contrat window.ready / window.renderAt(t) de out/tools/render.mjs. Aucun état entre les images.
// Issu de la maquette de Fable (out/report/notes/lyrics-chemin/proto/) ; déclinaisons : out/report/notes/lyrics-chemin/declinaisons/.
import * as S from '/out/tools/lib/svi.js';
import { straight, wave, polyline, catmull, sub, strokePath } from './outils.js';

const W = 1080, H = 1920;
export const ANCHOR = { x: 512, y: 860 };   // point de lecture à l'écran
const LIVE_MIN = 0.30;                       // s par mot : en dessous, l'unité est pré-posée
const FRAME_W = 780;                         // largeur d'un cadrage à l'écran (dérive et poussée comprises, il reste dans x 64–960)
const rad = d => d * Math.PI / 180;

export async function lancer({ data: defaultData }) {
  const q = new URLSearchParams(location.search);
  const D = await (await fetch(new URL(q.get('data') || defaultData, location.href).href)).json();
  const G = await (await fetch(`/out/shared/chemin-moteur/dessins/${D.dessin || 'bateau'}.json`)).json();
  const HB = (await import(`/out/shared/chemin-moteur/habillages/${D.habillage || 'plan-bleu'}.js`)).habillage;
  await S.loadFonts(HB.fonts);
  if (HB.prepare) await HB.prepare({ G, D });

  const FONT = `'${HB.font}'`, CAP = HB.cap, GAP = HB.gap, BELOW = HB.belowY ?? (HB.gap + HB.cap), WL = HB.weight;
  const LIFT_A = HB.liftAbove ?? (GAP + CAP / 2), LIFT_B = HB.liftBelow ?? (BELOW - CAP / 2);
  // un « temps » : celui du morceau, ou pour un short narré une durée de référence (D.temps, 0,5 s par défaut)
  const BEAT = D.bpm ? 60 / D.bpm : (D.temps || 0.5), DURATION = D.duree, [T_OUT0, T_OUT1] = D.zoomArriere;
  const cv = document.getElementById('c'), ctx = cv.getContext('2d', { willReadFrequently: true });
  const buf = document.createElement('canvas'); buf.width = W; buf.height = H;
  const bctx = buf.getContext('2d', { willReadFrequently: true });
  let lay = null, lctx = null;   // calque d'encre (habillages qui l'érodent : craie)
  if (HB.textErode) { lay = document.createElement('canvas'); lay.width = W; lay.height = H; lctx = lay.getContext('2d'); }
  const P = G.points || {};
  const pt = v => typeof v === 'string' ? P[v] : v;
  const mkPath = c => {
    if (c.type === 'vague') return wave(c.x0, c.x1, c.y, c.amp, c.wl, c.ph);
    if (c.type === 'courbe') return polyline(catmull(c.points.map(pt), c.pas || 4));
    if (c.type === 'troncon') { const R = HB.route; if (!R) throw new Error('tronçon sans route (habillage)'); const d0 = R.at0(c.depuis) + (c.decalage || 0); return sub(R.path, d0, d0 + c.longueur); }
    return straight(pt(c.a), pt(c.b));
  };

  // ---------- lignes ----------
  const LINES = D.lignes.map(l => {
    const A = G.aretes[l.arete]; if (!A) throw new Error('arête inconnue : ' + l.arete);
    return { ...A, id: l.arete, path: mkPath(A.chemin), u: l.u, cad: l.cad, arr: l.arr, dur: l.duree ?? (l.temps || 0) * BEAT, kind: l.kind,
      glide: l.glide, minPx: l.minPx, maxPx: l.maxPx, annotation: l.annotation };
  });
  function wOf(str, weight = WL) { ctx.font = `${weight} 100px ${FONT}`; return ctx.measureText(str).width / 100; }
  for (const L of LINES) {
    const wt = L.weight || WL, full = L.u.map(u => u[0]).join(' '), n = full.length, m = L.m || [0, 0];
    const gw = L.gapW ?? HB.gapW ?? 0, nGap = full.split(' ').length - 1;   // gapW : espace ajouté entre les mots (mots rigides sur une courbe)
    const usable = L.path.len - m[0] - m[1], wn = wOf(full, wt), [e0, e1] = L.em || HB.em;
    const em = S.clamp(usable / (wn + gw * nGap + (L.track || 0) * (n - 1)), e0, e1);
    let tr = (L.track || 0) * em;
    if (!L.noFit && !L.track) tr = S.clamp((usable - em * (wn + gw * nGap)) / (n - 1), 0, (L.trackMax ?? HB.trackMax) * em);
    const total = em * (wn + gw * nGap) + tr * (n - 1), d0 = m[0] + (L.center ? (usable - total) / 2 : 0);
    L.emW = em; L.tr = tr; L.wt = wt; L.words = []; L.units = []; L.d0 = d0; L.total = total;
    let ci = 0, wi = 0;
    L.u.forEach((u, ui) => {
      const first = L.words.length;
      for (const wd of u[0].split(' ')) { L.words.push({ txt: wd, ui, d0: d0 + em * wOf(full.slice(0, ci), wt) + tr * ci + gw * em * (wi++), w: em * wOf(wd, wt) + tr * (wd.length - 1) }); ci += wd.length + 1; }
      const a = L.words[first], b = L.words.at(-1), nw = L.words.length - first, per = (u[2] - u[1]) / nw;
      L.units.push({ txt: u[0], t: u[1], end: u[2], cls: u[3], d0: a.d0, d1: b.d0 + b.w, w0: first, w1: L.words.length, per, pre: per < LIVE_MIN });
    });
    L.textEnd = L.units.at(-1).d1; L.tStart = L.units[0].t; L.tEnd = L.units.at(-1).end;
  }

  // ---------- rangs finaux (la « mer » du bateau) : même corps, même espace entre tous les mots ; centrés, ou alignés à gauche ----------
  const M = G.mer || G.final, FIN = D.refrain || D.final, RU = FIN.u, WF = HB.wFinal ?? 800;
  const rowTxt = FIN.rangs.map(r => r.map(i => RU[i][0]).join(' '));
  const rowW = s => s.split(' ').reduce((a, w) => a + wOf(w, WF), 0) + (s.split(' ').length - 1) * M.espace;
  const SEA_EM = Math.min(M.emMax, ...rowTxt.map(s => M.largeurMax / rowW(s)));
  const SEA = [];
  FIN.rangs.forEach((r, ri) => {
    const R = M.rangs[ri], width = rowW(rowTxt[ri]) * SEA_EM, x0 = M.gauche ?? (M.cx - width / 2);
    const path = R.amp ? wave(x0 - 10, x0 + width + 10, R.y, R.amp, R.wl, R.ph + (x0 - 96) / R.wl * 2 * Math.PI) : straight([x0 - 10, R.y], [x0 + width + 10, R.y]);
    let d = 10;
    r.forEach(i => { const [txt, t0, t1, cls] = RU[i]; const words = [];
      for (const w of txt.split(' ')) { const ww = SEA_EM * wOf(w, WF); words.push({ txt: w, d0: d, w: ww }); d += ww + M.espace * SEA_EM; }
      SEA.push({ path, txt, t0, t1, cls, words, row: ri, x0, y: R.y, d0: words[0].d0, d1: words.at(-1).d0 + words.at(-1).w }); });
  });
  const SEA_L = { path: null, emW: SEA_EM, wt: WF, final: true };

  // ---------- caméra ----------
  let POSES = [];
  for (const L of LINES) {
    L.cad.forEach((g, gi) => {
      const a = L.units[g[0]], b = L.units[g.at(-1)], dc = (a.d0 + b.d1) / 2, w = b.d1 - a.d0, p = L.path.at(dc, w / 2);
      const lift = L.inside ? 0 : L.below ? -L.emW * LIFT_B : L.emW * LIFT_A, nx = Math.sin(p.a), ny = -Math.cos(p.a);
      // corps plancher (habillage, 120 px pour le plan bleu) ; L.minPx si la ligne le permet ; floorFast si tout le cadrage dépasse 4,5 mots/s (ligne entière pré-posée)
      const nWords = g.reduce((k, i) => k + (L.units[i].w1 - L.units[i].w0), 0), fast = (b.end - a.t) / nWords < 0.22;
      const base = L.minPx || HB.floorPx, floor = fast ? Math.min(HB.floorFast, base) : base;
      const s = S.clamp(FRAME_W / w, floor / L.emW, (L.maxPx || HB.maxPx) / L.emW);
      g.forEach(i => { L.units[i].floor = floor; });
      const th = p.a - S.clamp(p.a * 0.1, rad(-6), rad(6));
      const first = gi === 0;
      // priorités : 1) ne pas quitter le mot dit avant 60 % de sa durée ; 2) arriver au plus tard sur l'attaque ; 3) avance du pré-posé
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
  // reculs « muets » (respirations) : après une phrase isolée, ou pendant un trajet sans texte ; durée en temps ou en secondes
  for (const r of [].concat(D.respiration || [], D.respirations || [])) {
    const i = POSES.findIndex(p => p.arr > r.arrivee);
    POSES.splice(i < 0 ? POSES.length : i, 0, { line: 'respiration', txt: '(recul)', x: r.x, y: r.y, s: r.zoom, th: rad(r.angle || 0), arr: r.arrivee,
      dur: r.duree ?? r.temps * BEAT, kind: r.kind || 'ease', tSing: null, w: r.derive || 0, dirx: r.dir ? Math.cos(rad(r.dir)) : 1, diry: r.dir ? Math.sin(rad(r.dir)) : 0 });
  }
  POSES.push({ line: 'final', txt: '(image d’ensemble)', x: ANCHOR.x, y: ANCHOR.y, s: 1, th: 0, arr: T_OUT1, dur: T_OUT1 - T_OUT0, kind: 'zoomout',
    tSing: null, w: 0, dirx: 0, diry: 0, final: true });
  POSES.forEach((p, i) => { p.leave = i + 1 < POSES.length ? POSES[i + 1].arr - POSES[i + 1].dur : DURATION; });

  function hold(i, t) {   // pose i et sa dérive lente (la caméra accompagne la pointe), vitesse plafonnée à 40 px/s à l'écran
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

  // ---------- encre et mots ----------
  const COLS = HB.col, dryOf = u => (HB.dryColor && HB.dryColor(u)) || COLS.dry;
  const inkColor = (t, end, dry = COLS.dry) => S.mix(COLS.fresh, dry, S.clamp((t - (end + 0.10)) / 0.35));
  // flèche : sur une courbe, un mot rigide est décollé du trait de la flèche de l'arc sous lui (côté du texte)
  function sagOf(L, wd, p) { if (!L.courbe) return 0; let sag = 0;
    for (let i = 0; i <= 6; i++) { const q2 = L.path.at(wd.d0 + wd.w * i / 6, 2), ly = -(q2.x - p.x) * Math.sin(p.a) + (q2.y - p.y) * Math.cos(p.a); sag = L.below ? Math.max(sag, ly) : Math.max(sag, -ly); }
    return sag; }
  function baseY(L, wd, p, gap) { const em = L.emW; if (L.inside) return CAP * em / 2; return L.below ? BELOW * em + sagOf(L, wd, p) : -gap * em - sagOf(L, wd, p); }
  function drawWord(c, L, wd, fill, alpha = 1, f = 1, weight = L.wt || WL, gap = GAP, style = '') {   // mot rigide posé sur le chemin, révélé de gauche à droite (f)
    if (f <= 0 || alpha <= 0) return;
    let txt = wd.txt;
    if (HB.typed && f < 1) { const k = Math.floor(f * txt.length + 1e-6); if (k <= 0) return; txt = txt.slice(0, k); f = 1; }   // frappe : caractère par caractère
    const p = L.path.at(wd.d0 + wd.w / 2, wd.w / 2), em = L.emW, by = baseY(L, wd, p, gap);
    c.save(); c.translate(p.x, p.y); c.rotate(p.a); c.globalAlpha = alpha; c.fillStyle = fill;
    if (f < 1) { c.beginPath(); c.rect(-wd.w / 2 - 3, by - em * 1.1, (wd.w + 6) * f, em * 1.5); c.clip(); }
    c.font = `${style}${weight} ${em}px ${FONT}`; c.letterSpacing = (L.tr || 0) + 'px'; c.textAlign = 'left'; c.textBaseline = 'alphabetic'; c.fillText(txt, -wd.w / 2, by); c.restore();
  }
  function wordBox(L, wd, gap = GAP) {   // 4 coins (monde) de la boîte des capitales d'un mot
    const p = L.path.at(wd.d0 + wd.w / 2, wd.w / 2), em = L.emW, by = baseY(L, wd, p, gap), c = Math.cos(p.a), s = Math.sin(p.a);
    return [[-wd.w / 2, by - CAP * em], [wd.w / 2, by - CAP * em], [wd.w / 2, by], [-wd.w / 2, by]].map(([x, y]) => [p.x + c * x - s * y, p.y + s * x + c * y]);
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
  const TITLE = LINES.find(L => L.guide);
  const GH = HB.ghost || { mode: 'wipe', alpha: 0.5 };
  function drawInk(c, cam, t) {
    const lwLine = HB.lineWidth ?? 3.2, zk = S.clamp((cam.s - 1.2) / 1.5);
    const dryA = S.lerp(1, HB.dryCloseAlpha ?? 0.6, zk);   // l'encre sèche s'efface un peu en gros plan : le mot dit domine
    for (const L of LINES) {
      const tip = tipOf(L, t), endK = S.seg(t, L.tEnd + 0.05, L.tEnd + 0.4, S.ease.outCubic);
      if (!L.noLine && tip) {
        const d1 = S.lerp(Math.min(L.path.len, tip.d + 0.3 * L.emW), L.path.len, endK);
        c.globalAlpha = S.lerp(1, 0.75, zk);
        if (HB.stroke) HB.stroke(c, L, 0, d1, cam, t, env); else strokePath(c, L.path, 0, d1, lwLine, COLS.stroke);
        c.globalAlpha = 1;
      }
      for (const u of L.units) {
        const words = L.words.slice(u.w0, u.w1), dry = t > u.end + 0.45 ? dryA : 1, dc = dryOf(u);
        const frac = (wd, d) => S.clamp((d - wd.d0) / wd.w);
        if (u.pre) {
          const pose = POSES.find(p => p.line === L.id && p.tSing !== null && p.tSing <= u.t && u.t < p.tEnd + 1e-6) || POSES.find(p => p.line === L.id);
          const tG = Math.max(pose.arr - 0.04, u.t - BEAT), kg = S.clamp((t - tG) / 0.15);
          if (t >= u.t) words.forEach(wd => drawWord(c, L, wd, inkColor(t, u.end, dc), dry));
          else if (GH.mode === 'fade') words.forEach(wd => drawWord(c, L, wd, GH.color || dc, GH.alpha * kg, 1, GH.weight || L.wt, GAP, GH.style || ''));   // suggestion : apparaît d'un coup
          else words.forEach(wd => drawWord(c, L, wd, GH.color || dc, GH.alpha, frac(wd, u.d0 + (u.d1 - u.d0) * kg)));   // pré-posé au crayon
        } else {
          const f = S.clamp((t - (u.t - 0.08)) / writeDur(u));
          words.forEach(wd => drawWord(c, L, wd, inkColor(t, u.end, dc), dry, frac(wd, u.d0 + (u.d1 - u.d0) * f)));
        }
      }
      if (tip && HB.tip) HB.tip(c, L, tip, cam, t, env);
      drawAnnotation(c, L, t, cam);
    }
    // rangs finaux
    for (const s of SEA) {
      const wdur = Math.min(0.5 * (s.t1 - s.t0), 0.3), f = S.clamp((t - (s.t0 - 0.08)) / wdur), d = s.d0 + (s.d1 - s.d0) * f;
      s.words.forEach(wd => drawWord(c, { ...SEA_L, path: s.path }, wd, inkColor(t, s.t1, dryOf(s)), 1, S.clamp((d - wd.d0) / wd.w), WF, 0));
    }
    if (HB.afterInk) HB.afterInk(c, cam, t, env);
  }
  function drawAnnotation(c, L, t, cam) {   // annotations dans la seconde couleur, accrochées à la mise en page (jamais du texte)
    const A = L.annotation; if (!A) return;
    const k = S.seg(t, A.t, A.t + A.d, S.ease.inOutCubic); if (k <= 0) return;
    if (HB.annotations && HB.annotations[A.type]) { c.save(); HB.annotations[A.type](c, L, A, k, cam, t, env); c.restore(); return; }
    c.save(); c.strokeStyle = COLS.annot; c.lineCap = 'round'; c.lineJoin = 'round';
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
      for (const sg of seg) { strokePath(c, sg, 0, Math.min(sg.len, rem), 3, COLS.annot); rem -= sg.len; if (rem <= 0) break; }
    } else if (A.type === 'boucle') {   // boucle de correcteur autour de toute la ligne
      const mid = L.path.at((L.units[0].d0 + L.textEnd) / 2), rw = (L.textEnd - L.units[0].d0) / 2 + 14, rh = L.emW * 0.58, sg = L.below ? 1 : -1;
      c.translate(mid.x - Math.sin(mid.a) * L.emW * 0.52 * sg, mid.y + Math.cos(mid.a) * L.emW * 0.52 * sg); c.rotate(mid.a - 0.03);
      c.beginPath(); c.ellipse(0, 0, rw, rh, 0, -2.6, -2.6 + k * 6.6); c.lineWidth = 3; c.stroke();
    }
    c.restore();
  }

  // ---------- une image ----------
  const applyCam = (c, cam) => { c.translate(ANCHOR.x, ANCHOR.y); c.rotate(-cam.th); c.scale(cam.s, cam.s); c.translate(-cam.x, -cam.y); };
  function renderScene(c, t) {
    const cam = camAt(t);
    c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1;
    applyCam(c, cam);
    HB.floor(c, cam, t, env); HB.sheet(c, cam, t, env); if (HB.under) HB.under(c, cam, t, env);
    if (lay) {   // encre sur un calque, érodée par le grain de la surface (attaché au monde), puis posée
      lctx.setTransform(1, 0, 0, 1, 0, 0); lctx.globalCompositeOperation = 'source-over'; lctx.globalAlpha = 1; lctx.clearRect(0, 0, W, H);
      lctx.save(); applyCam(lctx, cam); drawInk(lctx, cam, t); lctx.globalCompositeOperation = 'destination-out'; HB.textErode(lctx, cam, t, env); lctx.restore();
      lctx.globalCompositeOperation = 'source-over';
      c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.drawImage(lay, 0, 0); c.restore();
    } else drawInk(c, cam, t);
    if (HB.objects) HB.objects(c, cam, t, env);
    c.setTransform(1, 0, 0, 1, 0, 0);   // finition écran
    if (HB.finish) HB.finish(c, cam, t, env);
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
      sung.push({ line: L.id, txt: u.txt, pre: u.pre, per: u.per, t: u.t, end: u.end, px: L.emW * cam.s, floor: u.floor, maxPx: L.maxPx || HB.maxPx, box: [x0, y0, x1, y1] });
    }
    return { cam: { ...cam, th: cam.th * 180 / Math.PI }, sung, disp: travel(t - SH, t) };
  }
  // boîtes de tous les mots dans l'image finale (zoom 1) : contrôle des chevauchements ; corps à l'image finale
  function finalBoxes() {
    const out = [];
    for (const L of LINES) for (const wd of L.words) out.push({ line: L.id, txt: wd.txt, px: L.emW, poly: wordBox(L, wd) });
    for (const s of SEA) for (const wd of s.words) out.push({ line: 'final', txt: wd.txt, px: SEA_EM, poly: wordBox({ ...SEA_L, path: s.path }, wd, 0) });
    return out;
  }

  const env = { G, D, HB, LINES, SEA, SEA_EM, POSES, BEAT, T_OUT0, T_OUT1, DURATION, TITLE, ANCHOR, pt, tipOf, drawWord, wordBox, wOf, camAt, toScreen,
    lineOf: id => LINES.find(L => L.id === id), FONT };
  window.DURATION = DURATION;
  window.renderAt = t => { render(t); };
  window.chemin = { metrics, finalBoxes, poses: POSES, beat: BEAT, duree: DURATION, zoomArriere: D.zoomArriere, seaEm: SEA_EM, floorPx: HB.floorPx, habillage: HB.id };
  window.STORYBOARD = { poses: POSES.map(p => ({ ...p, th: +(p.th * 180 / Math.PI).toFixed(1), x: Math.round(p.x), y: Math.round(p.y), s: +p.s.toFixed(2) })),
    lines: LINES.map(L => ({ id: L.id, em: +L.emW.toFixed(1), track: +L.tr.toFixed(1), len: Math.round(L.path.len), units: L.units.map(u => ({ txt: u.txt, t: u.t, end: u.end, per: +u.per.toFixed(2), pre: u.pre })) })),
    refrain: { em: +SEA_EM.toFixed(1), rangs: rowTxt.length } };
  if (q.has('guides')) S.guides();
}
