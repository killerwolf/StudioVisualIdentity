/**
 * cosmos.js — module commun de l'identité « Cosmos Doc » (documentaire spatial cinématographique).
 * Copié À L'IDENTIQUE dans chaque short de l'identité : changer le contenu (planètes, textes), pas ce module.
 *
 *  - TOK                       : tokens couleur (sRGB) réellement utilisés
 *  - setup({fov})              : renderer ACES + scène noir vrai + caméra ~50 mm + composer
 *                                (RenderPass scène -> RenderPass flare ortho -> UnrealBloom -> OutputPass -> FilmPass)
 *  - stars(scene, R, opts)     : champ d'étoiles shader (disques doux, température warm/ice, scintillement lent)
 *  - dust(scene, R, opts)      : voile de poussière galactique très faible (photographique, pas de néon)
 *  - Flare                     : flare « optique » maison : cœur, halo, traînée anamorphique bleu glacier, fantômes hexagonaux
 *  - atmosphere(r, color, …)   : coquille fresnel éclairée côté soleil
 *  - craterTex / bandTex / hotTex : textures planétaires procédurales (canvas, déterministes)
 *  - Motes                     : photons/points de lumière doux avec traîne (flou de bougé), pas de lignes
 *  - text reveal helpers       : reveal / hide (GSAP, fondu + resserrement de l'interlettrage, sine.inOut)
 */
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import * as S from '/out/tools/lib/svi.js';

export { THREE, S };
export const TOK = {
  bg: '#000004', surface: '#0C1024', amber: '#FFB347', ice: '#6EC6FF', white: '#FFFFFF',
  text: '#EAF2FF', muted: '#AEBBD4', ember: '#FF6A2A',
};
export const FONTS = [{ family: 'Bebas Neue', pkg: 'bebas-neue', weight: 400 }, { family: 'Inter', pkg: 'inter', weight: 400 }];

// ------------------------------------------------------------------ renderer / composer
export function setup({ fov = 36, bloom = [0.62, 0.7, 0.78], exposure = 1.0 } = {}) {
  const ren = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  ren.setSize(S.W, S.H); ren.setPixelRatio(1); document.body.prepend(ren.domElement);
  ren.toneMapping = THREE.ACESFilmicToneMapping; ren.toneMappingExposure = exposure;
  const scene = new THREE.Scene(); scene.background = new THREE.Color(TOK.bg);
  const cam = new THREE.PerspectiveCamera(fov, S.W / S.H, 0.05, 2000); // fov 36° vertical ≈ 50 mm plein format en 9:16
  const flareScene = new THREE.Scene();
  const ortho = new THREE.OrthographicCamera(0, S.W, 0, -S.H, -10, 10); // coordonnées pixel : x à droite, y vers le bas = -y
  const comp = new EffectComposer(ren);
  comp.addPass(new RenderPass(scene, cam));
  const fp = new RenderPass(flareScene, ortho); fp.clear = false; comp.addPass(fp);
  const bl = new UnrealBloomPass(new THREE.Vector2(S.W / 2, S.H / 2), bloom[0], bloom[1], bloom[2]); comp.addPass(bl);
  comp.addPass(new OutputPass());
  const film = new ShaderPass({
    uniforms: { tDiffuse: { value: null }, frame: { value: 0 }, grain: { value: 0.028 }, vig: { value: 0.38 }, dip: { value: 1 } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: `uniform sampler2D tDiffuse; uniform float frame, grain, vig, dip; varying vec2 vUv;
      float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233))) * 43758.5453); }
      void main(){
        vec4 c = texture2D(tDiffuse, vUv);
        vec2 q = vUv - .5; q.x *= 0.5625;
        float v = 1. - vig * smoothstep(.18, .62, length(q));
        vec2 g = floor(vUv * vec2(540., 960.));                 // grain 2 px, pas de scintillement pixel
        float n = h(g + vec2(frame * 17.13, frame * 3.71)) - .5;
        float lum = dot(c.rgb, vec3(.299,.587,.114));
        c.rgb = c.rgb * v + n * grain * (0.35 + lum);             // grain plus visible dans les tons moyens
        c.rgb *= dip;
        gl_FragColor = vec4(max(c.rgb, 0.), 1.);
      }`,
  });
  comp.addPass(film);
  return { ren, scene, cam, comp, flareScene, ortho, film, bloomPass: bl };
}

// ------------------------------------------------------------------ textures utilitaires
export function canvasTex(w, h, draw, srgb = true) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t;
}
export function radialTex(stops, size = 256) {
  return canvasTex(size, size, (g, w) => {
    const gr = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2);
    stops.forEach(([o, s]) => gr.addColorStop(o, s)); g.fillStyle = gr; g.fillRect(0, 0, w, w);
  });
}
function hexTex() {
  return canvasTex(256, 256, (g) => {
    g.translate(128, 128); g.filter = 'blur(6px)'; g.beginPath();
    for (let i = 0; i < 6; i++) { const a = Math.PI / 6 + i * Math.PI / 3; g.lineTo(Math.cos(a) * 100, Math.sin(a) * 100); }
    g.closePath(); g.fillStyle = 'rgba(255,255,255,.55)'; g.fill(); g.lineWidth = 6; g.strokeStyle = 'rgba(255,255,255,.9)'; g.stroke();
  });
}
function streakTex() {
  return canvasTex(512, 64, (g, w, h) => {
    const im = g.createImageData(w, h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const dx = (x - w / 2) / (w / 2), dy = (y - h / 2) / (h / 2);
      const a = Math.exp(-dx * dx * 3.2) * Math.exp(-dy * dy * 9) + Math.exp(-dx * dx * 40) * Math.exp(-dy * dy * 20) * .6;
      const k = (y * w + x) * 4; im.data[k] = im.data[k + 1] = im.data[k + 2] = 255; im.data[k + 3] = Math.min(255, a * 255);
    }
    g.putImageData(im, 0, 0);
  });
}

// ------------------------------------------------------------------ étoiles
export function stars(scene, { n = 2600, R = 300, seed = 7, size = 1, warm = .2, ice = .15 } = {}) {
  const rnd = S.rng(seed);
  const pos = new Float32Array(n * 3), col = new Float32Array(n * 3), sz = new Float32Array(n), ph = new Float32Array(n);
  const cw = new THREE.Color(TOK.amber), ci = new THREE.Color('#BFE3FF'), cn = new THREE.Color('#FFF6EA');
  for (let i = 0; i < n; i++) {
    const th = rnd() * Math.PI * 2, p = Math.acos(2 * rnd() - 1);
    pos.set([R * Math.sin(p) * Math.cos(th), R * Math.sin(p) * Math.sin(th), R * Math.cos(p)], i * 3);
    const m = Math.pow(rnd(), 4.5);                       // magnitude : beaucoup de petites, quelques brillantes
    const w = rnd(), c = w < warm ? cw : w > 1 - ice ? ci : cn;
    const b = 0.25 + m * 1.6;
    col.set([c.r * b, c.g * b, c.b * b], i * 3);
    sz[i] = (1.6 + m * 7.5) * size; ph[i] = rnd() * 6.283;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  geo.setAttribute('sz', new THREE.BufferAttribute(sz, 1));
  geo.setAttribute('ph', new THREE.BufferAttribute(ph, 1));
  const mat = new THREE.ShaderMaterial({
    uniforms: { t: { value: 0 }, gain: { value: 1 } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: `attribute float sz; attribute float ph; attribute vec3 color; varying vec3 vC; uniform float t, gain;
      void main(){ vC = color * gain * (0.85 + 0.15 * sin(t * 1.3 + ph)); vec4 mv = modelViewMatrix * vec4(position,1.);
        gl_PointSize = sz; gl_Position = projectionMatrix * mv; }`,
    fragmentShader: `varying vec3 vC; void main(){ vec2 d = gl_PointCoord - .5; float r = dot(d,d) * 4.;
      float a = exp(-r * 9.) + exp(-r * 2.2) * .18; gl_FragColor = vec4(vC * a, a); }`,
  });
  const pts = new THREE.Points(geo, mat); pts.frustumCulled = false; scene.add(pts);
  return pts;
}

// voile de poussière : sphère inversée, bande lumineuse très faible (ambre/glacier), photographique
export function dust(scene, { R = 600, seed = 3, intensity = 0.07, tilt = 0.5 } = {}) {
  const tex = canvasTex(512, 256, (g, w, h) => {
    const im = g.createImageData(w, h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const u = x / w, v = y / h;
      let n = 0, a = 1, f = 1; for (let o = 0; o < 4; o++) { n += a * S.noise3(u * 6 * f + seed, v * 6 * f, seed); a *= .5; f *= 2.05; }
      n /= 1.875;
      const band = Math.exp(-Math.pow((v - .5 - .08 * Math.sin(u * 6.283)) / .12, 2));
      const lane = S.smoothstep(.5, .7, S.noise3(u * 14, v * 9, 9)) * .7;           // bandes sombres
      const k = Math.max(0, band * (n * 1.5 - .35) * (1 - lane));
      const warmish = S.noise3(u * 3, v * 3, 4);
      const q = (y * w + x) * 4;
      im.data[q] = 255 * k * (0.75 + .25 * warmish); im.data[q + 1] = 255 * k * .78; im.data[q + 2] = 255 * k * (1.05 - .45 * warmish); im.data[q + 3] = 255;
    }
    g.putImageData(im, 0, 0);
  });
  const m = new THREE.Mesh(new THREE.SphereGeometry(R, 48, 24), new THREE.MeshBasicMaterial({ map: tex, side: THREE.BackSide, transparent: true, opacity: intensity, depthWrite: false, blending: THREE.AdditiveBlending }));
  m.rotation.set(tilt, 0.6, 0.3); scene.add(m); return m;
}

// ------------------------------------------------------------------ flare optique (overlay ortho, en pixels)
export class Flare {
  constructor(flareScene) {
    const add = (tex, color, blend = THREE.AdditiveBlending) => {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: tex, color, transparent: true, depthTest: false, depthWrite: false, blending: blend }));
      flareScene.add(m); return m;
    };
    this.halo = add(radialTex([[0, 'rgba(255,236,200,1)'], [.08, 'rgba(255,214,150,.75)'], [.3, 'rgba(255,179,71,.22)'], [.6, 'rgba(255,140,40,.06)'], [1, 'rgba(255,120,30,0)']]), new THREE.Color(1, 1, 1));
    this.core = add(radialTex([[0, 'rgba(255,255,255,1)'], [.25, 'rgba(255,250,235,.9)'], [.5, 'rgba(255,230,190,.25)'], [1, 'rgba(255,220,170,0)']]), new THREE.Color(2.2, 2.1, 2));
    this.streak = add(streakTex(), new THREE.Color(TOK.ice).multiplyScalar(1.6));
    this.streak2 = add(streakTex(), new THREE.Color(TOK.amber).multiplyScalar(1.2));
    this.ring = add(radialTex([[0, 'rgba(110,198,255,0)'], [.78, 'rgba(110,198,255,0)'], [.86, 'rgba(160,215,255,.22)'], [.9, 'rgba(255,190,110,.12)'], [1, 'rgba(255,179,71,0)']]), new THREE.Color(1, 1, 1));
    const hx = hexTex();
    this.ghosts = [[.42, 70, TOK.amber, .10], [.66, 150, TOK.ice, .06], [1.18, 54, TOK.amber, .16], [1.42, 230, TOK.ice, .05], [1.75, 110, TOK.amber, .08]]
      .map(([k, s, c, a]) => ({ k, s, a, m: add(hx, new THREE.Color(c)) }));
  }
  /** x,y pixels écran (y vers le bas), I intensité 0..1.5, s échelle */
  set(x, y, I = 1, s = 1) {
    const P = (m, px, py, w, h, op) => { m.position.set(px, -py, 0); m.scale.set(w, h, 1); m.material.opacity = Math.max(0, op); m.visible = op > 0.002; };
    P(this.halo, x, y, 1050 * s, 1050 * s, I * .6);
    P(this.core, x, y, 240 * s, 240 * s, I);
    P(this.streak, x, y, 2300 * s, 34 * s, I * .55);
    P(this.streak2, x, y, 900 * s, 14 * s, I * .45);
    P(this.ring, x, y, 1150 * s, 1150 * s, I * .16);
    const cx = S.W / 2, cy = S.H / 2;
    for (const g of this.ghosts) P(g.m, x + (cx - x) * 2 * g.k, y + (cy - y) * 2 * g.k, g.s * s, g.s * s, I * g.a * 1.4);
  }
}
/** projette un point 3D en pixels écran */
export function toScreen(v, cam) { const p = v.clone().project(cam); return [(p.x + 1) / 2 * S.W, (1 - p.y) / 2 * S.H, p.z]; }

// ------------------------------------------------------------------ atmosphère fresnel
export function atmosphere(r, color, { power = 3, gain = 1.6, wrap = .35 } = {}) {
  const mat = new THREE.ShaderMaterial({
    transparent: true, blending: THREE.AdditiveBlending, depthWrite: false,
    uniforms: { L: { value: new THREE.Vector3(-1, 0, 0) }, C: { value: new THREE.Color(color) }, gain: { value: gain }, P: { value: power }, wrap: { value: wrap }, night: { value: 0 } },
    vertexShader: 'varying vec3 vN; varying vec3 vW; void main(){ vN=normalize(mat3(modelMatrix)*normal); vW=(modelMatrix*vec4(position,1.)).xyz; gl_Position=projectionMatrix*viewMatrix*vec4(vW,1.);}',
    fragmentShader: `uniform vec3 L, C; uniform float gain, P, wrap, night; varying vec3 vN; varying vec3 vW;
      void main(){ vec3 V=normalize(cameraPosition-vW); float f=pow(1.-max(dot(vN,V),0.),P);
        float lit=mix(smoothstep(-wrap,.7,dot(vN,L)), 1., night); gl_FragColor=vec4(C*f*lit*gain, f*lit); }`,
  });
  return new THREE.Mesh(new THREE.SphereGeometry(r, 96, 64), mat);
}

// ------------------------------------------------------------------ textures planétaires (déterministes)
function fbm(x, y, z, oct = 5) { let n = 0, a = 1, f = 1, s = 0; for (let o = 0; o < oct; o++) { n += a * S.noise3(x * f, y * f, z); s += a; a *= .5; f *= 2.07; } return n / s; }
/** sol cratérisé (Mercure) : albédo + relief, cratères rasterisés par boîte englobante */
export function craterTex({ w = 1024, h = 512, seed = 5, n = 520, tint = [1, .96, .9], base = .5 } = {}) {
  const rnd = S.rng(seed), alb = new Float32Array(w * h), hg = new Float32Array(w * h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const v = fbm(x / w * 9, y / h * 4.5, seed), m = S.smoothstep(.5, .66, fbm(x / w * 3, y / h * 1.5, seed + 3, 3));
    alb[y * w + x] = base + (v - .5) * .4 - m * .12; hg[y * w + x] = v;
  }
  for (let i = 0; i < n; i++) {
    const cx = rnd() * w, cy = h * (.08 + .84 * rnd()), r = Math.pow(rnd(), 3.2) * 34 + 2;
    const ray = r > 16 && rnd() < .35;
    for (let y = Math.max(0, Math.floor(cy - r * 1.5)); y < Math.min(h, cy + r * 1.5); y++)
      for (let xx = Math.floor(cx - r * 1.5); xx < cx + r * 1.5; xx++) {
        const x = ((xx % w) + w) % w, d = Math.hypot(xx - cx, y - cy) / r; if (d > 1.5) continue;
        const k = y * w + x, bowl = d < 1 ? -(1 - d * d) * .55 : 0, rim = Math.exp(-Math.pow((d - 1) / .18, 2)) * .2;
        hg[k] += (bowl * .6 + rim) * Math.min(1, r / 20); alb[k] += rim * .22 + (ray ? .06 * (1 - d / 1.5) : 0) - (d < .9 ? .02 : 0);
      }
  }
  const map = canvasTex(w, h, (g) => { const im = g.createImageData(w, h); for (let i = 0; i < w * h; i++) { const a = S.clamp(alb[i]) * 255; im.data[i * 4] = a * tint[0]; im.data[i * 4 + 1] = a * tint[1]; im.data[i * 4 + 2] = a * tint[2]; im.data[i * 4 + 3] = 255; } g.putImageData(im, 0, 0); });
  const bump = canvasTex(w, h, (g) => { const im = g.createImageData(w, h); for (let i = 0; i < w * h; i++) { const a = S.clamp(hg[i] * .6 + .25) * 255; im.data[i * 4] = im.data[i * 4 + 1] = im.data[i * 4 + 2] = a; im.data[i * 4 + 3] = 255; } g.putImageData(im, 0, 0); }, false);
  return { map, bump };
}
/** nuages en bandes torsadées (Vénus, géantes) : c0 sombre -> c1 clair */
export function bandTex({ w = 1024, h = 512, seed = 9, c0 = [150, 112, 60], c1 = [242, 222, 172], bands = 7, warp = .9 } = {}) {
  return canvasTex(w, h, (g) => {
    const im = g.createImageData(w, h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const u = x / w, v = y / h;
      const wx = fbm(u * 5 + 1.3, v * 3, seed, 4), wy = fbm(u * 5 + 7.1, v * 3 + 2, seed, 4);
      const lat = v + (wy - .5) * .16 * warp + Math.sin(u * 6.283 * 2 + v * 9) * .015;
      let k = .5 + .5 * Math.sin(lat * bands * 6.283 + (wx - .5) * 6 * warp);
      k = k * .55 + fbm(u * 18 + wx * 3, v * 9, seed + 1, 3) * .45;
      k = S.clamp((k - .25) * 1.6);
      const q = (y * w + x) * 4;
      im.data[q] = S.lerp(c0[0], c1[0], k); im.data[q + 1] = S.lerp(c0[1], c1[1], k); im.data[q + 2] = S.lerp(c0[2], c1[2], k); im.data[q + 3] = 255;
    }
    g.putImageData(im, 0, 0);
  });
}
/** carte émissive « chaleur » : réseau de plaines brûlantes (sert à faire rougeoyer une surface) */
export function hotTex({ w = 1024, h = 512, seed = 21 } = {}) {
  return canvasTex(w, h, (g) => {
    const im = g.createImageData(w, h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const u = x / w, v = y / h;
      const r = 1 - Math.abs(fbm(u * 10, v * 5, seed, 4) * 2 - 1);               // crêtes
      const k = Math.pow(S.clamp(r), 3) * .8 + fbm(u * 4, v * 2, seed + 5, 3) * .35;
      const q = (y * w + x) * 4;
      im.data[q] = 255 * S.clamp(k * 1.2); im.data[q + 1] = 255 * S.clamp(k * k * .75); im.data[q + 2] = 255 * S.clamp(k * k * k * .25); im.data[q + 3] = 255;
    }
    g.putImageData(im, 0, 0);
  });
}

// ------------------------------------------------------------------ photons / points de lumière avec traîne
/** paths: [{pts:[[x,y,z],...], ts:[t0,t1,...], c0:Color, c1:Color, hit:index où la couleur bascule}] */
export class Motes {
  constructor(scene, paths, { trail = 9, dt = .011, size = 22 } = {}) {
    this.paths = paths; this.trail = trail; this.dt = dt;
    const n = paths.length * trail;
    this.pos = new Float32Array(n * 3); this.col = new Float32Array(n * 3); this.sz = new Float32Array(n);
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(this.pos, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(this.col, 3));
    geo.setAttribute('sz', new THREE.BufferAttribute(this.sz, 1));
    this.geo = geo; this.size = size;
    this.mat = new THREE.ShaderMaterial({
      uniforms: { gain: { value: 1 } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      vertexShader: 'attribute float sz; attribute vec3 color; varying vec3 vC; uniform float gain; void main(){ vC=color*gain; vec4 mv=modelViewMatrix*vec4(position,1.); gl_PointSize=sz*(10./-mv.z); gl_Position=projectionMatrix*mv; }',
      fragmentShader: 'varying vec3 vC; void main(){ vec2 d=gl_PointCoord-.5; float r=dot(d,d)*4.; float a=exp(-r*7.)+exp(-r*1.6)*.25; gl_FragColor=vec4(vC*a,a); }',
    });
    this.pts = new THREE.Points(geo, this.mat); this.pts.frustumCulled = false; scene.add(this.pts);
  }
  static at(p, t) {
    const ts = p.ts; if (t < ts[0] || t > ts[ts.length - 1]) return null;
    let i = 0; while (i < ts.length - 2 && t > ts[i + 1]) i++;
    const k = (t - ts[i]) / (ts[i + 1] - ts[i]), a = p.pts[i], b = p.pts[i + 1];
    return { x: a[0] + (b[0] - a[0]) * k, y: a[1] + (b[1] - a[1]) * k, z: a[2] + (b[2] - a[2]) * k, seg: i, k };
  }
  update(t, fade = 1) {
    let j = 0;
    for (const p of this.paths) for (let s = 0; s < this.trail; s++, j++) {
      const q = Motes.at(p, t - s * this.dt);
      if (!q) { this.sz[j] = 0; this.pos.set([0, 0, -9999], j * 3); continue; }
      const c = q.seg >= p.hit ? p.c1 : p.c0, w = Math.pow(1 - s / this.trail, 1.6) * fade * (p.alpha ?? 1);
      const born = S.clamp((t - p.ts[0]) / .25), end = S.clamp((p.ts[p.ts.length - 1] - t) / .4);
      const b = w * born * end;
      this.pos.set([q.x, q.y, q.z], j * 3); this.col.set([c.r * b, c.g * b, c.b * b], j * 3);
      this.sz[j] = this.size * (s === 0 ? 1 : .85 - s * .05);
    }
    this.geo.attributes.position.needsUpdate = this.geo.attributes.color.needsUpdate = this.geo.attributes.sz.needsUpdate = true;
  }
}

// ------------------------------------------------------------------ texte (GSAP) : fondu + interlettrage qui se resserre
export const EASE = 'sine.inOut';
export function reveal(tl, sel, at, { dur = 1.4, from = '0.32em', to = '0.02em', y = 0 } = {}) {
  tl.fromTo(sel, { opacity: 0, letterSpacing: from, y }, { opacity: 1, letterSpacing: to, y: 0, duration: dur, ease: EASE, immediateRender: false }, at);
}
export function hide(tl, sel, at, dur = 0.7) { tl.to(sel, { opacity: 0, duration: dur, ease: EASE }, at); }
/** dip-to-black : facteur 0..1 à partir de fenêtres [début, fin] (descente 45 %, plancher bref, remontée 45 %) */
export function dipAt(t, dips, floor = 0.06) {
  let f = 1;
  for (const [a, b] of dips) if (t > a && t < b) {
    const k = (t - a) / (b - a); const v = k < .45 ? 1 - S.ease.inOutSine(k / .45) : k > .55 ? S.ease.inOutSine((k - .55) / .45) : 0;
    f = Math.min(f, floor + (1 - floor) * v);
  }
  return f;
}
