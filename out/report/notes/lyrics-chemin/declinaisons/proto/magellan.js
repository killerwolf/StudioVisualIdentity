// A1 — « Le premier tour du monde » (Magellan–Elcano, 1519–1522) : habillage « portulan » + dessin « tour-du-monde ».
// Carte : projection azimutale équidistante centrée sur le pôle Sud (le tour du monde devient une boucle fermée),
// côtes réelles (world-atlas land-50m, domaine public Natural Earth). Maquette d'images fixes.
import { S, W, H, rad, polyline, sub, catmull, straight, noiseTile, shadowed, rr, finish } from './core.js';

const CX = 512, CY = 846, K = 4.6, L0 = -6, RD = 640;          // px par degré depuis le pôle Sud ; méridien de l'Espagne en haut
export const proj = (lon, lat) => { const r = (lat + 90) * K, a = rad(lon - L0); return [CX + r * Math.sin(a), CY - r * Math.cos(a)]; };
const SHEET = { x: 36, y: 96, w: 1008, h: 1704 };
const C = { parch: '#E9DCBC', parchHi: '#F1E7CC', parchLo: '#D9C79E', sepia: '#3A2718', verm: '#B8301A', bleu: '#27506E', land: '#CDB684', table: '#2B1D14' };

// ---- route (lon, lat) : jalons du voyage, au large des côtes ----
const WP = [['espagne', -6.35, 36.78], ['g1', -13, 31.5], ['canaries', -19, 23], ['a1', -22.5, 14.5], ['a2', -26, 6], ['a3', -29, -1], ['bresil', -32.5, -8], ['rio', -38.5, -24], ['plata', -51, -37.5],
  ['julian', -63, -49.6], ['entree', -67.6, -52.4], ['sortie', -75.6, -52.6], ['chili', -79.5, -41], ['p1', -86, -30], ['p2', -101, -21], ['p3', -130, -14], ['p4', -160, -5], ['p5', -182, 5], ['p6', -201, 10.5],
  ['guam', -215.25, 13.45], ['samar', -233.6, 11.2], ['cebu', -236.2, 10.2], ['palawan', -241.5, 9.2], ['brunei', -244.8, 5.4], ['sulu', -239.5, 6.6], ['mindanao', -234.5, 5.2], ['tidore', -232.6, 0.7], ['banda', -233, -5],
  ['timor', -235, -9.8], ['i1', -252, -19], ['i2', -275, -35], ['i3', -305, -40.5], ['i4', -328, -39.5], ['cap', -341.8, -36.6], ['c1', -348, -28], ['c2', -358, -14], ['c3', -370, -2], ['c4', -378, 7], ['verde', -383.5, 15],
  ['n1', -396, 27], ['acores', -391, 38.2], ['n2', -379, 40.3], ['retour', -366.35, 36.78]];
const PTS = WP.map(w => proj(w[1], w[2]));
const dense = catmull(PTS, 3), ROUTE = polyline(dense);
const AT = {}; { let k = 0; for (let i = 0; i < PTS.length; i++) { let best = 1e9, bi = k; for (let j = k; j < dense.length; j++) { const d = Math.hypot(dense[j][0] - PTS[i][0], dense[j][1] - PTS[i][1]); if (d < best) { best = d; bi = j; } if (d > best + 60) break; } k = bi; AT[WP[i][0]] = ROUTE.ds[bi]; } }
const rel = (from, off, len) => abs(AT[from] + off, AT[from] + off + len);
function abs(d0, d1) { return ({ chemin: { path: sub(ROUTE, d0, d1) }, _off: d0, m: [0, 0], noLine: true, courbe: true }); }

export const G = {
  id: 'tour-du-monde', feuille: SHEET,
  aretes: {   // tronçons de la route : jalon de départ + décalage et longueur en px (abscisse curviligne) ; contrôler avec dump.mjs
    depart:   { ...rel('espagne', 50, 158), em: [32, 44], below: true },
    an:       { ...rel('a1', 26, 100), em: [34, 44], center: true, below: true },
    magellan: { ...rel('bresil', 30, 200), em: [32, 40], center: true },
    detroit:  { ...rel('sortie', 118, 210), em: [34, 40], center: true },
    ocean:    { ...rel('sortie', 346, 360), em: [34, 40] },
    tue:      { ...rel('guam', -284, 348), em: [34, 40], center: true },
    elcano:   { ...rel('timor', 46, 192), em: [36, 44], center: true },
    victoria: { ...rel('i2', 23, 252), em: [34, 40], center: true },
    retour:   { ...rel('cap', 37, 206), em: [34, 42], center: true },
    hommes:   { ...rel('acores', 30, 205), em: [36, 46], center: true },
  },
  final: { cx: 512, largeurMax: 800, emMax: 96, espace: 0.3, rangs: [{ y: 1452 }, { y: 1556 }] },
  objets: { boussole: { x: CX, y: CY }, compas: { x: 966, y: 206, angle: 83 }, sceau: { x: 912, y: 1668 } },
};
// Temps ESTIMÉS (voix non générée) : à recaler sur les mots horodatés de la vraie narration.
export const D = {
  titre: 'LE PREMIER TOUR DU MONDE', langue: 'fr', duree: 41.0, zoomArriere: [35.6, 37.4],
  lignes: [
    { arete: 'depart', u: [['20 SEPT.', 0.15, 1.2]], cad: [[0]], arr: 0, maxPx: 250 },
    { arete: 'an', u: [['1519', 1.2, 2.3]], cad: [[0]], arr: 1.1, maxPx: 250 },
    { arete: 'magellan', u: [['MAGELLAN', 5.1, 6.3]], cad: [[0]], arr: 4.6 },
    { arete: 'detroit', u: [['LE DÉTROIT', 13.6, 14.8]], cad: [[0]], arr: 13.2 },
    { arete: 'ocean', u: [['UN OCÉAN', 17.3, 18.2], ['IMMENSE', 18.2, 19.2]], cad: [[0], [1]], arr: 16.9 },
    { arete: 'tue', u: [['MAGELLAN', 22.0, 22.8], ['EST TUÉ', 22.8, 23.8]], cad: [[0], [1]], arr: 21.5, annotation: { type: 'croix', t: 23.3 } },
    { arete: 'elcano', u: [['ELCANO', 26.2, 27.2]], cad: [[0]], arr: 25.6 },
    { arete: 'victoria', u: [['LA VICTORIA', 28.3, 29.3]], cad: [[0]], arr: 27.9 },
    { arete: 'retour', u: [['6 SEPT.', 31.7, 32.6], ['1522', 32.6, 33.4]], cad: [[0, 1]], arr: 31.2 },
    { arete: 'hommes', u: [['18 HOMMES', 34.4, 35.3]], cad: [[0]], arr: 34.2 },
  ],
  final: { u: [['LE PREMIER', 37.2, 38.0], ['TOUR DU MONDE', 38.0, 39.2]], rangs: [[0], [1]] },
};

let LAND, COAST, PAT = {};
async function prepare() {
  await new Promise((ok, ko) => { const s = document.createElement('script'); s.src = '/node_modules/topojson-client/dist/topojson-client.min.js'; s.onload = ok; s.onerror = ko; document.head.appendChild(s); });
  const topo = await (await fetch('/node_modules/world-atlas/land-50m.json')).json();
  const land = window.topojson.feature(topo, topo.objects.land); LAND = new Path2D();
  const polys = []; for (const f of (land.features || [land])) { const g = f.geometry; if (g.type === 'Polygon') polys.push(g.coordinates); else for (const p of g.coordinates) polys.push(p); }
  for (const poly of polys) for (const ring of poly) { if (ring.every(p => p[1] < -60)) continue; let first = true;
    for (const [lon, lat] of ring) { const [x, y] = proj(lon, Math.min(lat, 62)); first ? LAND.moveTo(x, y) : LAND.lineTo(x, y); first = false; } LAND.closePath(); }
  PAT.fib = noiseTile(256, 11, (i, j, r) => { const v = r(); return [v > 0.5 ? 255 : 60, v > 0.93 || v < 0.07 ? 26 : 0]; });
  PAT.blot = noiseTile(128, 5, (i, j) => { const n = S.noise2(i / 21, j / 21) * 0.6 + S.noise2(i / 7, j / 7) * 0.4; return [90, S.clamp((n - 0.52) * 3.2) * 70, 60, 20]; });
  PAT.wood = noiseTile(256, 9, (i, j) => { const n = S.noise2(i / 3.2, j / 140) * 0.55 + S.noise2(i / 1.3, j / 60) * 0.45; return [0, S.clamp((n - 0.3) * 1.6) * 70]; });
}
const pat = (c, k) => c.createPattern(PAT[k], 'repeat');

function floor(c) { c.fillStyle = C.table; c.fillRect(0, 0, W, H); }
function sheet(c, cam, t, env) {
  const { x, y, w, h } = SHEET;
  // table en noyer (attachée au monde)
  c.save(); c.fillStyle = '#3A281B'; c.fillRect(-400, -400, W + 800, H + 800); c.save(); c.scale(2, 2); c.fillStyle = pat(c, 'wood'); c.fillRect(-200, -200, 1000, 1500); c.restore(); c.restore();
  shadowed(c, cam, () => { c.fillStyle = C.parch; c.fillRect(x, y, w, h); }, 26, 12, 18, 0.55, '0,0,0');
  const g = c.createLinearGradient(x, y, x + w, y + h); g.addColorStop(0, C.parchHi); g.addColorStop(0.55, C.parch); g.addColorStop(1, C.parchLo); c.fillStyle = g; c.fillRect(x, y, w, h);
  c.save(); c.beginPath(); c.rect(x, y, w, h); c.clip();
  c.save(); c.scale(5, 5); c.globalAlpha = 0.36; c.fillStyle = pat(c, 'blot'); c.fillRect(0, 0, 220, 400); c.restore();
  c.save(); c.scale(1.5, 1.5); c.globalAlpha = 0.5; c.fillStyle = pat(c, 'fib'); c.fillRect(0, 0, 720, 1280); c.restore();
  // bords brunis
  for (const [gx0, gy0, gx1, gy1] of [[x, 0, x + 70, 0], [x + w, 0, x + w - 70, 0], [0, y, 0, y + 80], [0, y + h, 0, y + h - 80]]) { const e = c.createLinearGradient(gx0, gy0, gx1, gy1); e.addColorStop(0, 'rgba(120,80,30,0.38)'); e.addColorStop(1, 'rgba(120,80,30,0)'); c.fillStyle = e; c.fillRect(x, y, w, h); }
  // lignes de rhumb (réseau de portulan) : centre + 16 nœuds sur un cercle
  const nodes = []; for (let i = 0; i < 16; i++) nodes.push([CX + 560 * Math.sin(i * Math.PI / 8), CY - 560 * Math.cos(i * Math.PI / 8)]);
  c.lineWidth = 0.9 / Math.sqrt(cam.s); for (let i = 0; i < 16; i++) for (let j = i + 1; j < 16; j++) { if ((j - i) % 2 && (j - i) !== 1 && (j - i) !== 15) continue; c.strokeStyle = (i + j) % 4 === 0 ? 'rgba(184,48,26,0.16)' : (i + j) % 4 === 2 ? 'rgba(39,80,110,0.14)' : 'rgba(58,39,24,0.10)';
    c.beginPath(); c.moveTo(...nodes[i]); c.lineTo(...nodes[j]); c.stroke(); }
  // terres : aplat ocre, liseré côtier, trait de côte ; la carte s'efface vers le bas (place du texte final)
  const lay = document.createElement('canvas'); lay.width = W; lay.height = H; const lc = lay.getContext('2d'); lc.setTransform(c.getTransform());
  lc.save(); lc.beginPath(); lc.arc(CX, CY, RD, 0, 7); lc.clip();
  lc.lineJoin = 'round'; lc.strokeStyle = 'rgba(39,80,110,0.09)'; lc.lineWidth = 11; lc.stroke(LAND); lc.strokeStyle = 'rgba(39,80,110,0.11)'; lc.lineWidth = 5; lc.stroke(LAND);
  lc.fillStyle = C.land; lc.fill(LAND, 'evenodd'); lc.save(); lc.clip(LAND, 'evenodd'); lc.scale(5, 5); lc.globalAlpha = 0.55; lc.fillStyle = lc.createPattern(PAT.blot, 'repeat'); lc.fillRect(0, 0, 220, 400); lc.restore();
  lc.strokeStyle = 'rgba(58,39,24,0.85)'; lc.lineWidth = Math.max(0.7, 1.5 / Math.sqrt(cam.s)); lc.stroke(LAND);
  lc.restore();
  lc.strokeStyle = 'rgba(58,39,24,0.8)'; lc.lineWidth = 2; lc.beginPath(); lc.arc(CX, CY, RD, 0, 7); lc.stroke(); lc.lineWidth = 0.9; lc.beginPath(); lc.arc(CX, CY, RD + 9, 0, 7); lc.stroke();
  for (let i = 0; i < 72; i++) { const a = i * Math.PI / 36; lc.lineWidth = i % 2 ? 0.8 : 2.4; lc.beginPath(); lc.moveTo(CX + RD * Math.sin(a), CY - RD * Math.cos(a)); lc.lineTo(CX + (RD + 9) * Math.sin(a), CY - (RD + 9) * Math.cos(a)); lc.stroke(); }
  lc.globalCompositeOperation = 'destination-in'; const fd = lc.createLinearGradient(0, 1290, 0, 1385); fd.addColorStop(0, '#000'); fd.addColorStop(1, 'rgba(0,0,0,0)'); lc.fillStyle = fd; lc.fillRect(-500, -500, 2200, 3000);
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.drawImage(lay, 0, 0); c.restore();
  { c.save(); c.translate(196, 1196); c.rotate(rad(11)); for (let i = 0; i < 16; i++) { const a = i * Math.PI / 8, len = i % 4 === 0 ? 62 : i % 2 === 0 ? 44 : 28; c.fillStyle = i % 4 === 0 ? 'rgba(58,39,24,0.7)' : i % 2 === 0 ? 'rgba(184,48,26,0.55)' : 'rgba(39,80,110,0.5)';
      c.beginPath(); c.moveTo(Math.sin(a) * len, -Math.cos(a) * len); c.lineTo(Math.sin(a + 0.2) * 9, -Math.cos(a + 0.2) * 9); c.lineTo(0, 0); c.closePath(); c.fill(); c.strokeStyle = 'rgba(58,39,24,0.6)'; c.lineWidth = 0.7; c.beginPath(); c.moveTo(Math.sin(a) * len, -Math.cos(a) * len); c.lineTo(Math.sin(a - 0.2) * 9, -Math.cos(a - 0.2) * 9); c.lineTo(0, 0); c.closePath(); c.stroke(); }
    c.strokeStyle = 'rgba(58,39,24,0.5)'; c.lineWidth = 0.9; c.beginPath(); c.arc(0, 0, 20, 0, 7); c.stroke(); c.beginPath(); c.arc(0, 0, 70, 0, 7); c.stroke(); c.restore(); }
  // noms (décor, jamais un mot de la narration) : italique fin, à l'endroit dans l'image finale
  const lab = (txt, lon, lat, size = 17, ang = 0, tr = 5) => { const [px, py] = proj(lon, lat); c.save(); c.translate(px, py); c.rotate(rad(ang)); c.font = `italic 500 ${size}px 'Cormorant Garamond'`; c.letterSpacing = tr + 'px'; c.fillStyle = 'rgba(58,39,24,0.55)'; c.textAlign = 'center'; c.fillText(txt, 0, 0); c.restore(); };
  lab('OCÉAN PACIFIQUE', -150, -47, 20, 0, 8); lab('OCÉAN INDIEN', 74, -17, 19, -8, 8); lab('ATLANTIQUE', -17, -27, 17, 78, 6); lab('AFRIQUE', 21, 6, 17, 0, 7); lab('AMÉRIQUE', -60, -12, 16, 62, 6);
  lab('Moluques', 135, 2.5, 15, 0, 1); lab('Philippines', 129, 21.5, 15, 0, 1); lab('Espagne', -3.4, 40.6, 15, 0, 1); lab('Bonne-Espérance', 30.5, -31.2, 14, 0, 1);
  // plis de la feuille (parenté avec l'identité) : arête fine à largeur constante à l'écran
  for (const [ax, ay, bx, by] of [[540, y, 540, y + h], [x, y + h * 0.25, x + w, y + h * 0.25], [x, y + h * 0.5, x + w, y + h * 0.5], [x, y + h * 0.75, x + w, y + h * 0.75]]) {
    c.lineWidth = 9 / cam.s; c.strokeStyle = 'rgba(90,60,20,0.07)'; c.beginPath(); c.moveTo(ax, ay); c.lineTo(bx, by); c.stroke();
    c.lineWidth = 1.5 / cam.s; c.strokeStyle = 'rgba(255,250,235,0.5)'; c.beginPath(); c.moveTo(ax, ay); c.lineTo(bx, by); c.stroke();
    c.strokeStyle = 'rgba(70,45,15,0.22)'; c.beginPath(); c.moveTo(ax + 1.5 / cam.s, ay + 1.5 / cam.s); c.lineTo(bx + 1.5 / cam.s, by + 1.5 / cam.s); c.stroke(); }
  // filet d'encadrement et échelle (décor)
  c.strokeStyle = 'rgba(58,39,24,0.55)'; c.lineWidth = 1.6; c.strokeRect(x + 22, y + 22, w - 44, h - 44); c.lineWidth = 0.6; c.strokeRect(x + 28, y + 28, w - 56, h - 56);
  c.restore();
}
// la route : UN trait continu ; la pointe ne saute jamais (entre deux textes elle trace le trajet « muet »)
function routeD(t, env) { const keys = [[-1, 0]]; for (const L of env.LINES) { const off = L._off; for (const u of L.units) { keys.push([u.t - 0.08, off + u.d0], [u.t + (u.end - u.t) * 0.6, off + u.d1]); } }
  keys.push([env.T_OUT0 + 0.4, ROUTE.len]); let i = 0; while (i + 1 < keys.length && t >= keys[i + 1][0]) i++; if (i + 1 >= keys.length) return ROUTE.len;
  const k = S.clamp((t - keys[i][0]) / (keys[i + 1][0] - keys[i][0])); return S.lerp(keys[i][1], keys[i + 1][1], S.ease.inOutSine(k)); }
function inkExtras(c, cam, t, env) {
  const d = routeD(t, env); env.routeD = d;
  env.strokePath(c, ROUTE, 0, d, 3.2, C.sepia, null, 3);
  // escales : petits cercles à l'encre, posés quand la pointe y passe
  for (const [n, , ] of WP) if (['espagne', 'entree', 'guam', 'cebu', 'tidore', 'cap', 'verde'].includes(n) && AT[n] <= d) { const p = ROUTE.at(AT[n], 0); c.fillStyle = C.parch; c.strokeStyle = C.sepia; c.lineWidth = 2.2; c.beginPath(); c.arc(p.x, p.y, 5.5, 0, 7); c.fill(); c.stroke(); }
  if (d >= ROUTE.len - 1) { const p = ROUTE.at(0, 0); c.fillStyle = C.verm; c.beginPath(); c.arc(p.x, p.y, 4.2, 0, 7); c.fill(); }
  // annotations au bleu de Prusse (jamais du texte) : cinq navires au départ, croix à Mactan
  c.strokeStyle = C.bleu; c.fillStyle = C.bleu; c.lineWidth = 2.2; c.lineCap = 'round';
  // cinq navires le long du trait, en face de « 1519 » (côté opposé au texte), posés un par un
  if (t > 2.6) { const k = S.clamp((t - 2.6) / 1.0), La = env.lineOf('an'); for (let i = 0; i < Math.ceil(5 * k); i++) { const p = ROUTE.at(La._off + 2 + i * 24, 6); c.save(); c.translate(p.x + Math.sin(p.a) * 17, p.y - Math.cos(p.a) * 17); c.rotate(p.a); c.scale(0.8, 0.8);
      c.beginPath(); c.moveTo(-9, 0); c.lineTo(9, 0); c.lineTo(6, 5); c.lineTo(-6, 5); c.closePath(); c.fill(); c.lineWidth = 2; c.beginPath(); c.moveTo(0, -1); c.lineTo(0, -15); c.lineTo(8, -4); c.closePath(); c.stroke(); c.restore(); } }
  // croix à côté de « TUÉ » (accrochée à la mise en page)
  const Lt = env.lineOf('tue'); if (t > 23.3) { const k = S.clamp((t - 23.3) / 0.3), p = ROUTE.at(Lt._off + Lt.units.at(-1).d1 + 20, 4), em = Lt.emW; c.save(); c.translate(p.x + Math.sin(p.a) * em * 0.55, p.y - Math.cos(p.a) * em * 0.55); c.rotate(p.a); c.lineWidth = 3; c.beginPath(); c.moveTo(0, -em * 0.42); c.lineTo(0, -em * 0.42 + em * 0.8 * k); c.moveTo(-em * 0.2, -em * 0.16); c.lineTo(-em * 0.2 + em * 0.4 * k, -em * 0.16); c.stroke(); c.restore(); }
}
function objects(c, cam, t, env) {
  const O = G.objets;
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
function tip(c, p, em) { c.save(); c.fillStyle = C.verm; c.shadowColor = 'rgba(184,48,26,0.6)'; c.shadowBlur = 10; c.beginPath(); c.arc(p.x + Math.cos(p.a) * em * 0.1, p.y + Math.sin(p.a) * em * 0.1, em * 0.10, 0, 7); c.fill(); c.shadowBlur = 0; c.fillStyle = 'rgba(255,255,255,0.7)'; c.beginPath(); c.arc(p.x + Math.cos(p.a) * em * 0.1 - em * 0.03, p.y + Math.sin(p.a) * em * 0.1 - em * 0.03, em * 0.025, 0, 7); c.fill(); c.restore(); }

export const skin = {
  id: 'portulan', font: 'Cormorant Garamond', weight: 700, wFinal: 700, cap: 0.63, gap: 0.2, em: [34, 46], trackMax: 0.12, gapW: 0.16, dryCloseAlpha: 0.62,
  fonts: [{ family: 'Cormorant Garamond', weight: 700, pkg: 'cormorant-garamond' }, { family: 'Cormorant Garamond', weight: 500, style: 'italic', pkg: 'cormorant-garamond' }],
  col: { dry: C.sepia, fresh: C.verm, stroke: C.sepia }, ghostAlpha: 0.4,
  debug: () => ({ AT: Object.fromEntries(Object.entries(AT).map(([k, v]) => [k, Math.round(v)])), len: Math.round(ROUTE.len) }), prepare, floor, sheet, inkExtras, objects, tip, finish: c => finish(c, 0.34, 0.06),
};
