/**
 * topo.js — moteur commun de l'identité « topo-relief » (copié à l'identique dans chaque short).
 *  - heightfield procédural (bruit ridged, déterministe via S.noise2)
 *  - courbes de niveau d3.contours -> 2 textures canvas : carte hypsométrique (map) + lignes lumineuses (emissiveMap)
 *  - maquette en relief découpée : surface + flancs striés, shader « les courbes s'allument en montant » (uLevel)
 *  - utilitaires : renderer, scène, sprite lumineux, tube de route, projection 3D -> 2D
 * Dépend de : three (importmap), d3 (global, d3.min.js), /out/tools/lib/svi.js
 */
import * as THREE from 'three';
import * as S from '/out/tools/lib/svi.js';

export const C = { bg: '#14221C', surface: '#1E3329', gold: '#E8C872', clay: '#D9734E', mint: '#9FD3C7', text: '#F1EEDC' };
export const FONTS = [
  { family: 'Inter', pkg: 'inter', weight: 800 },
  { family: 'JetBrains Mono', pkg: 'jetbrains-mono', weight: 500 },
  { family: 'JetBrains Mono', pkg: 'jetbrains-mono', weight: 700 },
];
// easings nommés de l'identité
export const E = {
  rise: S.cubicBezier(0.16, 0.84, 0.30, 1),     // extrusion / montée des courbes
  glide: S.cubicBezier(0.45, 0, 0.25, 1),       // survol drone
  settle: S.ease.outBack,                        // puces / balises
};

export function ridged(x, y, { oct = 6, f0 = 3, ox = 3.1, oy = 7.7 } = {}) {
  let r = 0, a = .5, f = f0;
  for (let o = 0; o < oct; o++) { const n = 1 - Math.abs(S.noise2(x * f + ox, y * f + oy) * 2 - 1); r += a * n * n; a *= .5; f *= 2.03; }
  return r;
}

/** fn(x,y) avec x,y ∈ [0,1] -> hauteur brute ; renvoie Float64Array normalisée 0..1 */
export function heightfield(N, fn) {
  const H = new Float64Array(N * N);
  let lo = Infinity, hi = -Infinity;
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const v = fn(i / (N - 1), j / (N - 1)); H[j * N + i] = v; if (v < lo) lo = v; if (v > hi) hi = v;
  }
  for (let k = 0; k < H.length; k++) H[k] = (H[k] - lo) / (hi - lo);
  return H;
}
export function sampleH(H, N, x, y) {   // bilinéaire, x,y ∈ [0,1]
  const fx = S.clamp(x) * (N - 1), fy = S.clamp(y) * (N - 1);
  const i = Math.min(N - 2, Math.floor(fx)), j = Math.min(N - 2, Math.floor(fy)), u = fx - i, v = fy - j;
  const a = H[j * N + i], b = H[j * N + i + 1], c = H[(j + 1) * N + i], d = H[(j + 1) * N + i + 1];
  return S.lerp(S.lerp(a, b, u), S.lerp(c, d, u), v);
}

/** d3.contours -> {map, emissive} CanvasTextures. levels = nb d'intervalles ; gold au-dessus de hiGold */
export function contourMaps(H, N, { levels = 40, T = 2048, hiGold = .62, extra } = {}) {
  const thresholds = d3.range(0, 1.0001, 1 / levels);
  const cs = d3.contours().size([N, N]).thresholds(thresholds)(Array.from(H));
  const mk = () => { const c = document.createElement('canvas'); c.width = c.height = T; return c; };
  const cMap = mk(), gm = cMap.getContext('2d'), cEm = mk(), ge = cEm.getContext('2d');
  const proj = g => d3.geoPath(d3.geoTransform({ point(x, y) { this.stream.point(x * T / N, y * T / N); } }), g);
  const pm = proj(gm), pe = proj(ge);
  const hyps = d3.scaleLinear().domain([0, .3, .6, .85, 1]).range(['#12241b', '#1E3329', '#33442d', '#4d4a32', '#6a5f3e']);
  for (const k of cs) { gm.beginPath(); pm(k); gm.fillStyle = hyps(k.value); gm.fill(); }
  cs.forEach((k, idx) => { gm.beginPath(); pm(k); gm.strokeStyle = 'rgba(241,238,220,.10)'; gm.lineWidth = 2; gm.stroke(); });
  ge.fillStyle = '#000'; ge.fillRect(0, 0, T, T);
  const lineCol = d3.scaleLinear().domain([0, hiGold - .05, hiGold, 1]).range([C.mint, C.mint, C.gold, '#ffe9a8']);
  cs.forEach((k, idx) => {
    if (idx === 0) return;
    const master = idx % 5 === 0;
    ge.beginPath(); pe(k);
    ge.strokeStyle = lineCol(k.value); ge.globalAlpha = master ? 1 : .62;
    ge.shadowColor = lineCol(k.value); ge.shadowBlur = master ? 18 : 8;
    ge.lineWidth = master ? 6 : 2.6; ge.stroke();
  });
  ge.globalAlpha = 1; ge.shadowBlur = 0;
  if (extra) extra(gm, ge, T);
  const tex = c => { const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
  return { map: tex(cMap), emissive: tex(cEm), contours: cs };
}

export function setup({ fogNear = 10, fogFar = 26, fov = 54 } = {}) {
  const ren = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  ren.setSize(S.W, S.H); ren.setPixelRatio(1); ren.toneMapping = THREE.NoToneMapping;
  document.body.prepend(ren.domElement);
  const scene = new THREE.Scene(); scene.background = new THREE.Color(C.bg); scene.fog = new THREE.Fog(C.bg, fogNear, fogFar);
  const cam = new THREE.PerspectiveCamera(fov, S.W / S.H, .05, 120);   // fov vertical 54° ≈ focale 35 mm (plein format, vertical)
  scene.add(new THREE.HemisphereLight(0xf1eedc, 0x14221c, .85));
  const sun = new THREE.DirectionalLight(0xffe2b0, 2.4); sun.position.set(-6, 6, -3); scene.add(sun);
  // table quadrillée menthe (le « plan de travail » de la maquette)
  const grid = new THREE.GridHelper(60, 60, 0x9fd3c7, 0x9fd3c7);
  grid.material.transparent = true; grid.material.opacity = .10; grid.position.y = -0.62; scene.add(grid);
  return { ren, scene, cam, sun, grid };
}

/** Maquette : surface + flancs striés. Renvoie {group, mesh, U(uniforms), SZ, AMP, toWorld(x,y,h)} */
export function makeRelief(H, N, maps, { SZ = 12, AMP = 3.4, base = 0.6 } = {}) {
  const group = new THREE.Group();
  const geo = new THREE.PlaneGeometry(SZ, SZ, N - 1, N - 1); geo.rotateX(-Math.PI / 2);
  const pos = geo.attributes.position;
  for (let k = 0; k < pos.count; k++) pos.setY(k, H[k] * AMP);   // PlaneGeometry : k = j*N+i (rangée j = z)
  geo.computeVertexNormals();
  const U = { uLevel: { value: 1 }, uLow: { value: .14 }, uAmp: { value: AMP }, uSnow: { value: 0 }, uScan: { value: 1 } };
  const mat = new THREE.MeshStandardMaterial({ map: maps.map, emissiveMap: maps.emissive, emissive: 0xffffff, emissiveIntensity: 1.15, roughness: .95, metalness: 0 });
  mat.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, U);
    sh.vertexShader = 'varying float vH;\n' + sh.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\n vH = position.y;');
    sh.fragmentShader = 'uniform float uLevel; uniform float uLow; uniform float uAmp; uniform float uSnow; uniform float uScan; varying float vH;\n' + sh.fragmentShader
      .replace('#include <map_fragment>', `#include <map_fragment>
        float hh0 = vH / uAmp;
        diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.86, 0.85, 0.80), uSnow * smoothstep(0.88, 0.95, hh0));`)
      .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
        float hh = vH / uAmp;
        float lit = smoothstep(uLevel + 0.006, uLevel - 0.006, hh);
        float band = exp(-pow((hh - uLevel) / 0.014, 2.0)) * uScan;
        totalEmissiveRadiance *= (uLow + (1.0 - uLow) * lit + 1.8 * band);
        totalEmissiveRadiance += vec3(0.62, 0.83, 0.78) * 0.16 * band;`);
  };
  const mesh = new THREE.Mesh(geo, mat); group.add(mesh);
  // flancs : bandes verticales à stries horizontales (strates)
  const sc = document.createElement('canvas'); sc.width = 8; sc.height = 256; const sg = sc.getContext('2d');
  sg.fillStyle = C.surface; sg.fillRect(0, 0, 8, 256);
  for (let y = 0; y < 256; y += 16) { sg.fillStyle = y % 64 === 0 ? 'rgba(159,211,199,.55)' : 'rgba(159,211,199,.18)'; sg.fillRect(0, y, 8, 2); }
  const st = new THREE.CanvasTexture(sc); st.wrapT = THREE.RepeatWrapping; st.colorSpace = THREE.SRGBColorSpace;
  const wallMat = new THREE.MeshStandardMaterial({ map: st, roughness: 1, side: THREE.DoubleSide, emissive: 0x1e3329, emissiveIntensity: .5 });
  const edges = [[k => [k, 0]], [k => [k, N - 1]], [k => [0, k]], [k => [N - 1, k]]];
  for (const [f] of edges) {
    const vtx = [], uv = [], idx = [];
    for (let k = 0; k < N; k++) {
      const [i, j] = f(k), x = i / (N - 1) * SZ - SZ / 2, z = j / (N - 1) * SZ - SZ / 2, h = H[j * N + i] * AMP;
      vtx.push(x, h, z, x, -base, z); uv.push(k / (N - 1), (h + base) / 1.2, k / (N - 1), 0);
      if (k) { const a = (k - 1) * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
    }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(vtx, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx); g.computeVertexNormals();
    group.add(new THREE.Mesh(g, wallMat));
  }
  group.position.y = 0;
  const toLocal = (x, y, h = null) => new THREE.Vector3(x * SZ - SZ / 2, (h ?? sampleH(H, N, x, y)) * AMP, y * SZ - SZ / 2);
  return { group, mesh, U, SZ, AMP, toLocal };
}

let _glowTex = null;
export function glowTexture() {
  if (_glowTex) return _glowTex;
  const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
  const r = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(.22, 'rgba(255,255,255,.85)'); r.addColorStop(.5, 'rgba(255,255,255,.22)'); r.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = r; g.fillRect(0, 0, 128, 128);
  _glowTex = new THREE.CanvasTexture(c); return _glowTex;
}
export function glowSprite(color, size = .6) {
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTexture(), color, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, fog: false }));
  s.scale.setScalar(size); return s;
}

/** Tube lumineux le long d'une courbe ; draw(p) révèle 0..p */
export function glowTube(points, color, { r = .045, seg = 400, halo = 2.6 } = {}) {
  const curve = new THREE.CatmullRomCurve3(points, false, 'catmullrom', .5);
  const g = new THREE.TubeGeometry(curve, seg, r, 8, false);
  const core = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color, fog: false }));
  const gh = new THREE.TubeGeometry(curve, seg, r * halo, 8, false);
  const hal = new THREE.Mesh(gh, new THREE.MeshBasicMaterial({ color, transparent: true, opacity: .28, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }));
  const grp = new THREE.Group(); grp.add(core, hal);
  const per = 8 * 6;
  grp.draw = p => { const n = Math.floor(S.clamp(p) * seg) * per; g.setDrawRange(0, n); gh.setDrawRange(0, n); grp.visible = n > 0; };
  grp.curve = curve;
  return grp;
}

/** projette un point monde -> px écran */
export function toScreen(v, cam) { const p = v.clone().project(cam); return [(p.x + 1) / 2 * S.W, (1 - p.y) / 2 * S.H, p.z]; }

/** fondu + glissement d'un élément DOM : visible sur [a,d], entrée a->b, sortie c->d */
export function show(el, t, a, b, c = 1e9, d = 1e9, dy = 26) {
  const k = Math.min(S.seg(t, a, b, S.ease.outCubic), 1 - S.seg(t, c, d, S.ease.inCubic));
  el.style.opacity = k.toFixed(3); el.style.transform = `translateY(${((1 - k) * dy).toFixed(1)}px)`;
  el.style.display = k <= 0.001 ? 'none' : '';
  return k;
}

export const fmt = d3.formatLocale({ decimal: ',', thousands: ' ', grouping: [3], currency: ['', ' €'] });
