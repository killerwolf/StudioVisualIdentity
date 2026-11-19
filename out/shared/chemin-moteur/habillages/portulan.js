// portulan.js — habillage « portulan » de lyrics-chemin (déclinaison A1, « Le premier tour du monde », short narré).
// Carte marine à l'encre sur parchemin, posée sur une table en noyer. Carte vue du pôle Sud (projection azimutale
// équidistante) : un tour du monde y devient une boucle fermée. Encre sèche sépia, mot dit au vermillon, annotations au bleu
// de Prusse (navires, croix). La route est UN trait continu : la pointe ne saute jamais, entre deux textes elle trace le trajet
// « muet ». Côtes réelles : world-atlas 2.0.2 land-50m (Natural Earth, domaine public), rendues une fois en image (cache).
// Dessin associé : tour-du-monde (projection, jalons de la route, tronçons portant le texte, escales, objets).
// Maquette d'origine : out/report/notes/lyrics-chemin/declinaisons/proto/magellan.js (Fable).
import { S, W, H, rad, polyline, catmull, noiseTile, shadowed } from '../outils.js';

const C = { parch: '#E9DCBC', parchHi: '#F1E7CC', parchLo: '#D9C79E', sepia: '#3A2718', verm: '#B8301A', bleu: '#27506E', land: '#CDB684' };
const CAP = 0.63, GAP = 0.20;
let PR, ROUTE, AT = {}, MAP, PAT = {};
const proj = (lon, lat) => { const r = (lat + 90) * PR.k, a = rad(lon - PR.l0); return [PR.cx + r * Math.sin(a), PR.cy - r * Math.cos(a)]; };

async function prepare({ G }) {
  PR = G.projection;
  // route : jalons (lon, lat) lissés ; abscisse curviligne de chaque jalon
  const P = G.route.map(w => proj(w[1], w[2])), dense = catmull(P, 3); ROUTE = polyline(dense);
  let k = 0; for (let i = 0; i < P.length; i++) { let best = 1e9, bi = k; for (let j = k; j < dense.length; j++) { const d = Math.hypot(dense[j][0] - P[i][0], dense[j][1] - P[i][1]); if (d < best) { best = d; bi = j; } if (d > best + 60) break; } k = bi; AT[G.route[i][0]] = ROUTE.ds[bi]; }
  habillage.route = { path: ROUTE, at0: n => { if (!(n in AT)) throw new Error('jalon inconnu : ' + n); return AT[n]; } };
  await new Promise((ok, ko) => { const s = document.createElement('script'); s.src = '/node_modules/topojson-client/dist/topojson-client.min.js'; s.onload = ok; s.onerror = ko; document.head.appendChild(s); });
  const topo = await (await fetch('/node_modules/world-atlas/land-50m.json')).json();
  const land = window.topojson.feature(topo, topo.objects.land), LAND = new Path2D();
  const polys = []; for (const f of (land.features || [land])) { const g = f.geometry; if (g.type === 'Polygon') polys.push(g.coordinates); else for (const p of g.coordinates) polys.push(p); }
  for (const poly of polys) for (const ring of poly) { if (ring.every(p => p[1] < -60)) continue; let first = true;
    for (const [lon, lat] of ring) { const [x, y] = proj(lon, Math.min(lat, 62)); first ? LAND.moveTo(x, y) : LAND.lineTo(x, y); first = false; } LAND.closePath(); }
  PAT.fib = noiseTile(256, 11, (i, j, r) => { const v = r(); return [v > 0.5 ? 255 : 60, v > 0.93 || v < 0.07 ? 26 : 0]; });
  PAT.blot = noiseTile(128, 5, (i, j) => { const n = S.noise2(i / 21, j / 21) * 0.6 + S.noise2(i / 7, j / 7) * 0.4; return [90, S.clamp((n - 0.52) * 3.2) * 70, 60, 20]; });
  PAT.wood = noiseTile(256, 9, (i, j) => { const n = S.noise2(i / 3.2, j / 140) * 0.55 + S.noise2(i / 1.3, j / 60) * 0.45; return [0, S.clamp((n - 0.3) * 1.6) * 70]; });
  PAT.grain = noiseTile(256, 77, (i, j, r) => { const v = r() * 255; return [v, 255]; });
  // la carte (terres, côtes, bordure graduée), rendue UNE fois à 3 px par unité monde ; s'efface vers le bas (place des rangs finaux)
  const RD = PR.rayon, Q = 3, x0 = PR.cx - RD - 12, y0 = PR.cy - RD - 12, sz = 2 * RD + 24;
  MAP = { c: document.createElement('canvas'), x0, y0, sz }; MAP.c.width = MAP.c.height = Math.ceil(sz * Q);
  const lc = MAP.c.getContext('2d'); lc.scale(Q, Q); lc.translate(-x0, -y0);
  lc.save(); lc.beginPath(); lc.arc(PR.cx, PR.cy, RD, 0, 7); lc.clip();
  lc.lineJoin = 'round'; lc.strokeStyle = 'rgba(39,80,110,0.09)'; lc.lineWidth = 11; lc.stroke(LAND); lc.strokeStyle = 'rgba(39,80,110,0.11)'; lc.lineWidth = 5; lc.stroke(LAND);
  lc.fillStyle = C.land; lc.fill(LAND, 'evenodd'); lc.save(); lc.clip(LAND, 'evenodd'); lc.scale(5, 5); lc.globalAlpha = 0.55; lc.fillStyle = lc.createPattern(PAT.blot, 'repeat'); lc.fillRect(0, 0, 220, 400); lc.restore();
  lc.strokeStyle = 'rgba(58,39,24,0.85)'; lc.lineWidth = 0.8; lc.stroke(LAND);
  lc.restore();
  lc.strokeStyle = 'rgba(58,39,24,0.8)'; lc.lineWidth = 2; lc.beginPath(); lc.arc(PR.cx, PR.cy, RD, 0, 7); lc.stroke(); lc.lineWidth = 0.9; lc.beginPath(); lc.arc(PR.cx, PR.cy, RD + 9, 0, 7); lc.stroke();
  for (let i = 0; i < 72; i++) { const a = i * Math.PI / 36; lc.lineWidth = i % 2 ? 0.8 : 2.4; lc.beginPath(); lc.moveTo(PR.cx + RD * Math.sin(a), PR.cy - RD * Math.cos(a)); lc.lineTo(PR.cx + (RD + 9) * Math.sin(a), PR.cy - (RD + 9) * Math.cos(a)); lc.stroke(); }
  lc.globalCompositeOperation = 'destination-in'; const fd = lc.createLinearGradient(0, PR.fondu[0], 0, PR.fondu[1]); fd.addColorStop(0, '#000'); fd.addColorStop(1, 'rgba(0,0,0,0)'); lc.fillStyle = fd; lc.fillRect(x0 - 10, y0 - 10, sz + 20, sz + 20);
}
const pat = (c, k) => c.createPattern(PAT[k], 'repeat');

function floor(c) { c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.fillStyle = '#2B1D14'; c.fillRect(0, 0, W, H); c.restore(); }
function sheet(c, cam, t, env) {
  const { x, y, w, h } = env.G.feuille;
  c.save(); c.fillStyle = '#3A281B'; c.fillRect(-1400, -1400, W + 2800, H + 2800); c.save(); c.scale(2, 2); c.fillStyle = pat(c, 'wood'); c.fillRect(-700, -700, 1600, 2300); c.restore(); c.restore();
  shadowed(c, cam, () => { c.fillStyle = C.parch; c.fillRect(x, y, w, h); }, 26, 12, 18, 0.55, '0,0,0');
  const g = c.createLinearGradient(x, y, x + w, y + h); g.addColorStop(0, C.parchHi); g.addColorStop(0.55, C.parch); g.addColorStop(1, C.parchLo); c.fillStyle = g; c.fillRect(x, y, w, h);
  c.save(); c.beginPath(); c.rect(x, y, w, h); c.clip();
  c.save(); c.scale(5, 5); c.globalAlpha = 0.36; c.fillStyle = pat(c, 'blot'); c.fillRect(0, 0, 220, 400); c.restore();
  c.save(); c.scale(1.5, 1.5); c.globalAlpha = 0.5; c.fillStyle = pat(c, 'fib'); c.fillRect(0, 0, 720, 1280); c.restore();
  for (const [gx0, gy0, gx1, gy1] of [[x, 0, x + 70, 0], [x + w, 0, x + w - 70, 0], [0, y, 0, y + 80], [0, y + h, 0, y + h - 80]]) { const e = c.createLinearGradient(gx0, gy0, gx1, gy1); e.addColorStop(0, 'rgba(120,80,30,0.38)'); e.addColorStop(1, 'rgba(120,80,30,0)'); c.fillStyle = e; c.fillRect(x, y, w, h); }   // bords brunis
  // lignes de rhumb (réseau de portulan) : 16 nœuds sur un cercle
  const nodes = []; for (let i = 0; i < 16; i++) nodes.push([PR.cx + 560 * Math.sin(i * Math.PI / 8), PR.cy - 560 * Math.cos(i * Math.PI / 8)]);
  c.lineWidth = 0.9 / Math.sqrt(cam.s); for (let i = 0; i < 16; i++) for (let j = i + 1; j < 16; j++) { if ((j - i) % 2 && (j - i) !== 1 && (j - i) !== 15) continue; c.strokeStyle = (i + j) % 4 === 0 ? 'rgba(184,48,26,0.16)' : (i + j) % 4 === 2 ? 'rgba(39,80,110,0.14)' : 'rgba(58,39,24,0.10)';
    c.beginPath(); c.moveTo(...nodes[i]); c.lineTo(...nodes[j]); c.stroke(); }
  c.drawImage(MAP.c, MAP.x0, MAP.y0, MAP.sz, MAP.sz);
  { const R = env.G.rose; c.save(); c.translate(R.x, R.y); c.rotate(rad(11)); for (let i = 0; i < 16; i++) { const a = i * Math.PI / 8, len = i % 4 === 0 ? 62 : i % 2 === 0 ? 44 : 28; c.fillStyle = i % 4 === 0 ? 'rgba(58,39,24,0.7)' : i % 2 === 0 ? 'rgba(184,48,26,0.55)' : 'rgba(39,80,110,0.5)';
      c.beginPath(); c.moveTo(Math.sin(a) * len, -Math.cos(a) * len); c.lineTo(Math.sin(a + 0.2) * 9, -Math.cos(a + 0.2) * 9); c.lineTo(0, 0); c.closePath(); c.fill(); c.strokeStyle = 'rgba(58,39,24,0.6)'; c.lineWidth = 0.7; c.beginPath(); c.moveTo(Math.sin(a) * len, -Math.cos(a) * len); c.lineTo(Math.sin(a - 0.2) * 9, -Math.cos(a - 0.2) * 9); c.lineTo(0, 0); c.closePath(); c.stroke(); }
    c.strokeStyle = 'rgba(58,39,24,0.5)'; c.lineWidth = 0.9; c.beginPath(); c.arc(0, 0, 20, 0, 7); c.stroke(); c.beginPath(); c.arc(0, 0, 70, 0, 7); c.stroke(); c.restore(); }
  // noms (décor, jamais un mot de la narration) : italique fin, à l'endroit dans l'image finale
  for (const [txt, lon, lat, size, ang, tr] of env.G.noms) { const [px, py] = proj(lon, lat); c.save(); c.translate(px, py); c.rotate(rad(ang)); c.font = `italic 500 ${size}px 'Cormorant Garamond'`; c.letterSpacing = tr + 'px'; c.fillStyle = 'rgba(58,39,24,0.55)'; c.textAlign = 'center'; c.fillText(txt, 0, 0); c.restore(); }
  // plis de la feuille : arête fine à largeur constante à l'écran
  for (const [ax, ay, bx, by] of [[540, y, 540, y + h], [x, y + h * 0.25, x + w, y + h * 0.25], [x, y + h * 0.5, x + w, y + h * 0.5], [x, y + h * 0.75, x + w, y + h * 0.75]]) {
    c.lineWidth = 9 / cam.s; c.strokeStyle = 'rgba(90,60,20,0.07)'; c.beginPath(); c.moveTo(ax, ay); c.lineTo(bx, by); c.stroke();
    c.lineWidth = 1.5 / cam.s; c.strokeStyle = 'rgba(255,250,235,0.5)'; c.beginPath(); c.moveTo(ax, ay); c.lineTo(bx, by); c.stroke();
    c.strokeStyle = 'rgba(70,45,15,0.22)'; c.beginPath(); c.moveTo(ax + 1.5 / cam.s, ay + 1.5 / cam.s); c.lineTo(bx + 1.5 / cam.s, by + 1.5 / cam.s); c.stroke(); }
  c.strokeStyle = 'rgba(58,39,24,0.55)'; c.lineWidth = 1.6; c.strokeRect(x + 22, y + 22, w - 44, h - 44); c.lineWidth = 0.6; c.strokeRect(x + 28, y + 28, w - 56, h - 56);
  c.restore();
}
// avance de la pointe sur la route : elle suit l'écriture de chaque unité, et entre deux textes trace le trajet muet
const writeDur = u => Math.min(0.5 * (u.end - u.t), 0.28);
function routeD(t, env) {
  const keys = [[-1, 0]];
  for (const L of env.LINES) { const off = L.path.off; for (const u of L.units) { const t0 = u.pre ? u.t - 0.01 : u.t - 0.08, t1 = u.pre ? u.t : t0 + writeDur(u); keys.push([t0, off + u.d0], [t1, off + u.d1]); } }
  keys.push([env.D.routeFin, ROUTE.len]);
  let i = 0; while (i + 1 < keys.length && t >= keys[i + 1][0]) i++; if (i + 1 >= keys.length) return ROUTE.len;
  const k = S.clamp((t - keys[i][0]) / (keys[i + 1][0] - keys[i][0])), muet = keys[i + 1][1] - keys[i][1] > 0 && (i % 2 === 0);
  return S.lerp(keys[i][1], keys[i + 1][1], muet ? S.ease.inOutSine(k) : k);
}
function under(c, cam, t, env) {   // la route, sous le texte : UN trait continu jusqu'à la pointe
  const d = routeD(t, env), n = Math.max(2, Math.ceil(d / 3)); if (d <= 0) return;
  c.save(); c.beginPath(); for (let i = 0; i <= n; i++) { const p = ROUTE.pos(d * i / n); i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1]); }
  c.lineWidth = 3.2; c.strokeStyle = C.sepia; c.lineCap = 'round'; c.lineJoin = 'round'; c.stroke();
  // escales : petits cercles à l'encre, posés quand la pointe y passe ; point vermillon sur l'Espagne quand la boucle se ferme
  for (const nm of env.G.escales) if (AT[nm] <= d) { const p = ROUTE.pos(AT[nm]); c.fillStyle = C.parch; c.strokeStyle = C.sepia; c.lineWidth = 2.2; c.beginPath(); c.arc(p[0], p[1], 5.5, 0, 7); c.fill(); c.stroke(); }
  if (d >= ROUTE.len - 1) { const p = ROUTE.pos(0); c.fillStyle = C.verm; c.beginPath(); c.arc(p[0], p[1], 4.2, 0, 7); c.fill(); }
  c.restore();
}
function afterInk(c, cam, t, env) {
  // pointe : point d'encre vermillon luisant au bout de la route (jusqu'au zoom arrière)
  if (t < env.T_OUT1) { const d = routeD(t, env), p = ROUTE.at(d, 4), em = 40 * Math.min(1, 3.2 / cam.s) ;
    c.save(); c.fillStyle = C.verm; c.shadowColor = 'rgba(184,48,26,0.6)'; c.shadowBlur = 10 * cam.s; c.beginPath(); c.arc(p.x, p.y, 4.2, 0, 7); c.fill(); c.shadowBlur = 0; c.fillStyle = 'rgba(255,255,255,0.7)'; c.beginPath(); c.arc(p.x - 1.1, p.y - 1.1, 1.1, 0, 7); c.fill(); c.restore(); }
}
const annotations = {
  // navires au bleu de Prusse le long du trait, côté opposé au texte, posés un à un
  navires(c, L, A, k) { const n = A.n || 5; c.strokeStyle = C.bleu; c.fillStyle = C.bleu; c.lineCap = 'round';
    for (let i = 0; i < Math.ceil(n * k - 1e-6); i++) { const p = L.path.at(L.units[0].d0 + 4 + i * 22, 6), side = L.below ? 1 : -1, o = 17 * side; c.save(); c.translate(p.x + Math.sin(p.a) * o, p.y - Math.cos(p.a) * o); c.rotate(p.a + (side < 0 ? 0 : 0)); c.scale(0.8, 0.8);
      c.beginPath(); c.moveTo(-9, 0); c.lineTo(9, 0); c.lineTo(6, 5); c.lineTo(-6, 5); c.closePath(); c.fill(); c.lineWidth = 2; c.beginPath(); c.moveTo(0, -1); c.lineTo(0, -15); c.lineTo(8, -4); c.closePath(); c.stroke(); c.restore(); } },
  // croix † accrochée au dernier mot
  croix(c, L, A, k) { const p = L.path.at(L.units.at(-1).d1 + 20, 4), em = L.emW; c.save(); c.translate(p.x + Math.sin(p.a) * em * 0.55, p.y - Math.cos(p.a) * em * 0.55); c.rotate(p.a); c.strokeStyle = C.bleu; c.lineWidth = 3; c.lineCap = 'round';
    c.beginPath(); c.moveTo(0, -em * 0.42); c.lineTo(0, -em * 0.42 + em * 0.8 * k); c.moveTo(-em * 0.2, -em * 0.16); c.lineTo(-em * 0.2 + em * 0.4 * k, -em * 0.16); c.stroke(); c.restore(); },
};
function objects(c, cam, t, env) {
  const O = env.G.objets;
  // boussole en laiton posée sur le pôle
  c.save(); c.translate(O.boussole.x, O.boussole.y);
  shadowed(c, cam, () => { c.fillStyle = '#8E6B2A'; c.beginPath(); c.arc(0, 0, 96, 0, 7); c.fill(); }, 18, 10, 14, 0.5, '30,15,0');
  let g = c.createLinearGradient(-90, -90, 90, 90); g.addColorStop(0, '#E9CF86'); g.addColorStop(0.5, '#B98F3C'); g.addColorStop(1, '#7A5A22'); c.fillStyle = g; c.beginPath(); c.arc(0, 0, 96, 0, 7); c.fill();
  g = c.createLinearGradient(-80, -80, 80, 80); g.addColorStop(0, '#8A6A2A'); g.addColorStop(1, '#E2C77C'); c.fillStyle = g; c.beginPath(); c.arc(0, 0, 84, 0, 7); c.fill();
  c.fillStyle = '#F2EAD2'; c.beginPath(); c.arc(0, 0, 78, 0, 7); c.fill();
  c.strokeStyle = 'rgba(58,39,24,0.8)'; for (let i = 0; i < 64; i++) { const a = i * Math.PI / 32, r0 = i % 8 === 0 ? 58 : i % 4 === 0 ? 64 : 69; c.lineWidth = i % 8 === 0 ? 1.8 : 0.9; c.beginPath(); c.moveTo(Math.sin(a) * r0, -Math.cos(a) * r0); c.lineTo(Math.sin(a) * 74, -Math.cos(a) * 74); c.stroke(); }
  for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4, len = i % 2 ? 30 : 50; c.fillStyle = i % 2 ? 'rgba(58,39,24,0.35)' : 'rgba(58,39,24,0.75)'; c.beginPath(); c.moveTo(Math.sin(a) * len, -Math.cos(a) * len); c.lineTo(Math.sin(a + 0.5) * 9, -Math.cos(a + 0.5) * 9); c.lineTo(0, 0); c.closePath(); c.fill();
    c.fillStyle = 'rgba(58,39,24,0.18)'; c.beginPath(); c.moveTo(Math.sin(a) * len, -Math.cos(a) * len); c.lineTo(Math.sin(a - 0.5) * 9, -Math.cos(a - 0.5) * 9); c.lineTo(0, 0); c.closePath(); c.fill(); }
  c.save(); c.rotate(rad(-24)); c.fillStyle = C.verm; c.beginPath(); c.moveTo(0, -62); c.lineTo(7, 0); c.lineTo(-7, 0); c.closePath(); c.fill(); c.fillStyle = '#3B4A57'; c.beginPath(); c.moveTo(0, 62); c.lineTo(7, 0); c.lineTo(-7, 0); c.closePath(); c.fill(); c.restore();
  c.fillStyle = '#C9A24A'; c.beginPath(); c.arc(0, 0, 6, 0, 7); c.fill();
  g = c.createRadialGradient(-30, -36, 4, -30, -36, 70); g.addColorStop(0, 'rgba(255,255,255,0.5)'); g.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = g; c.beginPath(); c.arc(0, 0, 78, 0, 7); c.fill();
  c.restore();
  // compas à pointes sèches
  c.save(); c.translate(O.compas.x, O.compas.y); c.rotate(rad(O.compas.angle));
  const leg = (a) => { c.save(); c.rotate(rad(a)); shadowed(c, cam, () => { c.fillStyle = '#B98F3C'; c.beginPath(); c.moveTo(-7, 0); c.lineTo(7, 0); c.lineTo(3.5, 170); c.lineTo(-3.5, 170); c.closePath(); c.fill(); }, 8, 6, 9, 0.45, '30,15,0');
    const lg = c.createLinearGradient(-7, 0, 7, 0); lg.addColorStop(0, '#E7CC82'); lg.addColorStop(0.5, '#C29A48'); lg.addColorStop(1, '#8A6828'); c.fillStyle = lg; c.beginPath(); c.moveTo(-7, 0); c.lineTo(7, 0); c.lineTo(3.5, 170); c.lineTo(-3.5, 170); c.closePath(); c.fill();
    c.fillStyle = '#9AA3A8'; c.beginPath(); c.moveTo(-3.5, 170); c.lineTo(3.5, 170); c.lineTo(0, 236); c.closePath(); c.fill(); c.fillStyle = '#E3E7E8'; c.beginPath(); c.moveTo(-3.5, 170); c.lineTo(-0.5, 170); c.lineTo(0, 236); c.closePath(); c.fill(); c.restore(); };
  leg(-13); leg(13); shadowed(c, cam, () => { c.fillStyle = '#C9A24A'; c.beginPath(); c.arc(0, 0, 15, 0, 7); c.fill(); }, 6, 4, 6, 0.4, '30,15,0'); c.fillStyle = '#8A6828'; c.beginPath(); c.arc(0, 0, 6, 0, 7); c.fill();
  c.fillStyle = '#C9A24A'; c.fillRect(-4, -34, 8, 24); c.beginPath(); c.arc(0, -36, 7, 0, 7); c.fill(); c.restore();
  // sceau de cire et ruban
  c.save(); c.translate(O.sceau.x, O.sceau.y);
  shadowed(c, cam, () => { c.fillStyle = '#7C1F14'; c.beginPath(); c.moveTo(-14, 10); c.lineTo(-40, 120); c.lineTo(-22, 108); c.lineTo(-8, 126); c.lineTo(8, 14); c.closePath(); c.fill(); }, 6, 4, 6, 0.35, '30,15,0');
  shadowed(c, cam, () => { c.fillStyle = '#A3271A'; c.beginPath(); for (let i = 0; i <= 40; i++) { const a = i / 40 * Math.PI * 2, r = 58 + 6 * Math.sin(a * 5 + 1) + 3 * Math.sin(a * 9); i ? c.lineTo(Math.cos(a) * r, Math.sin(a) * r) : c.moveTo(Math.cos(a) * r, Math.sin(a) * r); } c.fill(); }, 12, 7, 10, 0.5, '30,15,0');
  g = c.createRadialGradient(-16, -18, 4, 0, 0, 60); g.addColorStop(0, '#D24A36'); g.addColorStop(1, '#8F2015'); c.fillStyle = g; c.beginPath(); c.arc(0, 0, 44, 0, 7); c.fill();
  c.strokeStyle = 'rgba(80,10,5,0.55)'; c.lineWidth = 2.5; c.beginPath(); c.arc(0, 0, 36, 0, 7); c.stroke(); c.beginPath(); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; c.moveTo(0, 0); c.lineTo(Math.cos(a) * (i % 2 ? 16 : 30), Math.sin(a) * (i % 2 ? 16 : 30)); } c.stroke();
  c.restore();
}
function finish(c) {
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
  const g = c.createRadialGradient(W / 2, H / 2, 620, W / 2, H / 2, 1250); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.34)'); c.fillStyle = g; c.fillRect(0, 0, W, H);
  c.globalAlpha = 0.06; c.globalCompositeOperation = 'overlay'; c.fillStyle = c.createPattern(PAT.grain, 'repeat'); c.fillRect(0, 0, W, H); c.restore();
}

export const habillage = {
  id: 'portulan',
  fonts: [{ family: 'Cormorant Garamond', weight: 700, pkg: 'cormorant-garamond' }, { family: 'Cormorant Garamond', weight: 500, style: 'italic', pkg: 'cormorant-garamond' }],
  font: 'Cormorant Garamond', weight: 700, wFinal: 700, cap: CAP, gap: GAP,
  em: [34, 46], trackMax: 0.12, gapW: 0.16, floorPx: 120, floorFast: 92, maxPx: 250, dryCloseAlpha: 0.62,
  col: { fresh: C.verm, dry: C.sepia, stroke: C.sepia, annot: C.bleu },
  ghost: { mode: 'wipe', alpha: 0.4 },
  prepare, floor, sheet, under, afterInk, annotations, objects, finish,
};
