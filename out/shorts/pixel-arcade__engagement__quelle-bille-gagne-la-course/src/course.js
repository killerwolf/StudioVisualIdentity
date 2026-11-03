/* course.js — course de billes Matter.js, partagée entre la pré-simulation Node (simulate.js)
 * et la page de rendu (index.html). Coordonnées LOGIQUES 270×480 (×4 à l'écran = 1080×1920).
 * Déterministe : même graine -> même course (pas fixe 1000/120 ms, 4 sous-pas par frame vidéo 30 fps).
 * UMD minimal : module.exports en Node, window.Course dans le navigateur.
 */
(function (root) {
  const LW = 270, LH = 480;
  const FX0 = 16, FX1 = 238;              // couloir (pixels logiques)
  const FINISH = 386;                     // ligne d'arrivée (y logique)
  const FLOOR = 398;
  const COLS = ['#FF4F79', '#3CF2A0', '#FFD23F', '#4FB3FF'];
  const NAMES = ['ROSE', 'VERTE', 'JAUNE', 'BLEUE'];
  const FPS = 30, SUB = 4, DT = 1000 / (FPS * SUB);
  const START_T = 2.4;                    // ouverture de la grille (s)
  const STUCK_S = 1.2;                    // nudge si pas de progrès vertical pendant 1,2 s

  function rng(seed) {                    // mulberry32 (identique à svi.js)
    let a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // rampes : [x0,y0,x1,y1] (haut -> bas), épaisseur 4
  const RAMPS = [[FX0, 184, 194, 204], [FX1, 226, 60, 246], [FX0, 302, 194, 320], [FX1, 338, 60, 356]];
  // angles figés en littéraux : Math.atan2 diffère au dernier bit entre le V8 de Node 22 et celui de Chromium 153
  // (mesuré : 0.17467219900823971 vs 0.1746721990082397) -> la course divergeait (chaos). Valeurs = atan2 calculé en Node.
  const RAMP_ANG = [0.1118902661716761, 3.029702387418117, 0.10078099908466776, 3.0408116545051254];
  const RAMP_LEN = [179.12007146045917, 179.12007146045917, 178.90779748239035, 178.90779748239035]; // idem pour Math.hypot

  function create(Matter, seed, opts) {
    opts = opts || {};
    const { Engine, Bodies, Composite, Body, Events } = Matter;
    const R = rng(seed);
    const gScale = opts.gScale || 0.001;
    const engine = Engine.create({ positionIterations: 8, velocityIterations: 6 });
    engine.gravity.y = 1; engine.gravity.scale = gScale;
    const st = { isStatic: true, restitution: 0.35, friction: 0, frictionStatic: 0 };
    const pegs = [], ramps = [], spinners = [];
    // champ de picots 1 (sous la grille)
    for (let r = 0; r < 3; r++) for (let c = 0; c < 10; c++) {
      const x = FX0 + 14 + c * 24 + (r % 2 ? 12 : 0) + (R() - 0.5) * 2, y = 120 + r * 16 + (R() - 0.5) * 1.5;
      if (x > FX1 - 8) continue;
      const b = Bodies.circle(x, y, 2.5, Object.assign({ label: 'peg' }, st, { restitution: 0.55 })); pegs.push(b);
    }
    // rampes
    RAMPS.forEach(([x0, y0, x1, y1], i) => {
      const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, len = RAMP_LEN[i];
      const b = Bodies.rectangle(cx, cy, len, 4, Object.assign({ label: 'ramp', angle: RAMP_ANG[i] }, st));
      b.seg = [x0, y0, x1, y1]; ramps.push(b);
    });
    // section des hélices (entre rampe 2 et 3)
    const sp0 = R() * Math.PI;
    [[86, 268, 1], [170, 268, -1]].forEach(([x, y, dir], i) => {
      const b = Bodies.rectangle(x, y, 36, 4, Object.assign({ label: 'spinner' }, st, { restitution: 0.5 }));
      b.dir = dir; b.cx = x; b.cy = y; b.phase = sp0 + i * 0.9; spinners.push(b);
    });
    [[128, 256], [128, 280]].forEach(([x, y]) => pegs.push(Bodies.circle(x, y, 2.5, Object.assign({ label: 'peg' }, st, { restitution: 0.6 }))));
    // sprint final : picots
    for (let c = 0; c < 9; c++) { const x = FX0 + 14 + c * 24, y = 372; pegs.push(Bodies.circle(x, y, 2.5, Object.assign({ label: 'peg' }, st, { restitution: 0.55 }))); }
    // murs, sol, grille de départ
    const H = FLOOR - 70;
    const walls = [
      Bodies.rectangle(FX0 - 5, 70 + H / 2, 10, H + 40, Object.assign({ label: 'wall' }, st)),
      Bodies.rectangle(FX1 + 5, 70 + H / 2, 10, H + 40, Object.assign({ label: 'wall' }, st)),
      Bodies.rectangle((FX0 + FX1) / 2, FLOOR + 5, FX1 - FX0 + 20, 10, Object.assign({ label: 'floor' }, st)),
    ];
    const gate = Bodies.rectangle((FX0 + FX1) / 2, 104, FX1 - FX0, 4, Object.assign({ label: 'gate' }, st));
    // billes : ordre des couleurs + positions tirés de la graine
    const order = [0, 1, 2, 3];
    for (let i = 3; i > 0; i--) { const j = Math.floor(R() * (i + 1)); [order[i], order[j]] = [order[j], order[i]]; }
    const marbles = COLS.map((c, i) => {
      const slot = order.indexOf(i);
      const b = Bodies.circle(64 + slot * 42 + (R() - 0.5) * 4, 94 - (R() * 2), 6,
        { label: 'marble', restitution: 0.45, friction: 0, frictionStatic: 0, frictionAir: opts.air || 0.014, density: 0.002 });
      b.idx = i; b.col = c; return b;
    });
    Composite.add(engine.world, [...pegs, ...ramps, ...spinners, ...walls, gate, ...marbles]);

    const state = {
      seed, engine, marbles, pegs, ramps, spinners, gate, frame: 0, step: 0,
      finished: [], finishT: [null, null, null, null], rank: [], events: [], nudges: [],
      best: marbles.map(m => m.position.y), bestStep: marbles.map(() => 0), trails: marbles.map(() => []),
      gateOpen: false,
    };
    Events.on(engine, 'collisionStart', ev => {
      const t = state.step * DT / 1000;
      for (const p of ev.pairs) {
        const a = p.bodyA, b = p.bodyB;
        const m = a.label === 'marble' ? a : b.label === 'marble' ? b : null;
        if (!m) continue;
        const o = m === a ? b : a;
        const rv = Math.hypot(a.velocity.x - b.velocity.x, a.velocity.y - b.velocity.y);
        state.events.push({ t: +t.toFixed(3), m: m.idx, with: o.label === 'marble' ? 'marble' : o.label, o: o.label === 'marble' ? o.idx : -1, v: +rv.toFixed(3), id: o.id });
      }
    });
    return state;
  }

  function stepFrame(Matter, s) {
    const { Engine, Body, Composite } = Matter;
    for (let k = 0; k < SUB; k++) {
      const t = s.step * DT / 1000;
      if (!s.gateOpen && t >= START_T) { Composite.remove(s.engine.world, s.gate); s.gateOpen = true; s.bestStep = s.bestStep.map(() => s.step); s.events.push({ t: +t.toFixed(3), m: -1, with: 'start', o: -1, v: 0 }); }
      s.spinners.forEach(b => Body.setAngle(b, b.phase + b.dir * 2.4 * t, true));
      Engine.update(s.engine, DT);
      s.step++;
      const tt = s.step * DT / 1000;
      s.marbles.forEach((m, i) => {
        if (s.finishT[i] !== null) return;
        if (m.position.y > FINISH) {
          s.finishT[i] = +tt.toFixed(3); s.rank.push(i);
          s.finishPos = s.finishPos || []; s.finishPos[i] = [m.position.x, m.position.y];
          Composite.remove(s.engine.world, m);
          s.events.push({ t: +tt.toFixed(3), m: i, with: 'finish', o: s.rank.length, v: 0 });
          return;
        }
        // anti-blocage : progrès vertical
        if (m.position.y > s.best[i] + 1) { s.best[i] = m.position.y; s.bestStep[i] = s.step; }
        if (s.gateOpen && (s.step - s.bestStep[i]) * DT / 1000 > STUCK_S) {
          // direction : vers le bas de la rampe la plus proche sous la bille, sinon vers le centre
          let dir = m.position.x < (FX0 + FX1) / 2 ? 1 : -1;
          for (const [x0, y0, x1, y1] of RAMPS) if (m.position.y < Math.max(y0, y1) + 2 && m.position.y > Math.min(y0, y1) - 14) dir = x1 > x0 ? 1 : -1;
          Body.setVelocity(m, { x: dir * 1.0, y: -0.6 });
          s.nudges.push({ t: +tt.toFixed(3), m: i }); s.bestStep[i] = s.step; s.best[i] = m.position.y;
        }
      });
    }
    s.frame++;
    s.marbles.forEach((m, i) => { if (s.finishT[i] === null) { s.trails[i].push([m.position.x, m.position.y]); if (s.trails[i].length > 14) s.trails[i].shift(); } else s.trails[i] = []; });
  }

  const api = { LW, LH, FX0, FX1, FINISH, FLOOR, COLS, NAMES, FPS, SUB, DT, START_T, RAMPS, rng, create, stepFrame };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.Course = api;
})(typeof window !== 'undefined' ? window : globalThis);
