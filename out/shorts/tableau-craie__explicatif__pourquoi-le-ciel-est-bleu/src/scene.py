"""Tableau Craie — « Pourquoi le ciel est bleu ? » (Manim 0.22, rendu Cairo, 1080×1920 30 fps).

Manim dessine toutes les formes (tracés craie tremblés, hachures, ondes, barres, Terre/atmosphère, chiffon).
Le texte (Caveat/Nunito) et le grain de craie sont des overlays PNG posés ensuite par assemble.py (voir build.sh) :
Text()/MathTex ne sont pas disponibles ici (manimpango stub, pas de LaTeX).
Variables d'env : SVI_ASSETS (dossier de board.png), SVI_FPS (30 par défaut ; 6 pour la prévisualisation).
"""
import os, json
from pathlib import Path
import numpy as np
from manim import *
from manim.animation.animation import prepare_animation

HERE = Path(__file__).resolve().parent
TL = json.loads((HERE / 'timeline.json').read_text())
TOK = json.loads((HERE / 'tokens.json').read_text())
C = TOK['color']
CREAM, ORANGE, BLUE, RED = C['accent']
TEXT, GREEN = C['text'], C['success']
ASSETS = Path(os.environ.get('SVI_ASSETS', '/tmp/svi/tableau-craie__explicatif__pourquoi-le-ciel-est-bleu/assets'))

config.frame_width = 9; config.frame_height = 16
config.pixel_width = 1080; config.pixel_height = 1920
config.frame_rate = int(os.environ.get('SVI_FPS', '30'))
config.background_color = C['bg']

SEED = TL['seed']
RNG = np.random.default_rng(SEED)


def P(px, py):
    """pixels (1080×1920, origine en haut à gauche) -> unités Manim."""
    return np.array([px / 120 - 4.5, 8 - py / 120, 0.0])


def wobble(mob, amp, seed):
    """Tremblé main levée : déplacement lisse (somme de sinus) fonction de la position -> pas de cassure."""
    r = np.random.default_rng(seed)
    f = r.uniform(1.2, 2.6, 4); ph = r.uniform(0, 6.28, 4)
    def fn(p):
        return p + amp * np.array([np.sin(f[0] * p[1] + ph[0]) + 0.5 * np.sin(f[1] * p[0] * 1.7 + ph[1]),
                                   np.sin(f[2] * p[0] + ph[2]) + 0.5 * np.sin(f[3] * p[1] * 1.7 + ph[3]), 0])
    mob.apply_function(fn)
    return mob


def chalk(mob, color, width=7.0, seed=0, n=10):
    """3 passes de craie : trait principal, trait fin décalé, halo de poussière très léger."""
    base = mob.copy()
    if n:
        for sm in base.family_members_with_points():
            sm.insert_n_curves(n)
    layers = []
    for k, (w, op, amp) in enumerate([(width * 1.7, 0.10, 0.018), (width, 0.88, 0.014), (width * 0.45, 0.65, 0.03)]):
        m = base.copy().set_fill(opacity=0).set_stroke(color, width=w, opacity=op)
        layers.append(wobble(m, amp, seed * 7 + k))
    return VGroup(*layers)


def hachure_circle(c, r, color, gap=0.13, seed=0, angle=PI / 4, width=3.0):
    lines = VGroup()
    u = np.array([np.cos(angle), np.sin(angle), 0]); nrm = np.array([-u[1], u[0], 0])
    d = -r + gap / 2
    while d < r:
        h = np.sqrt(max(r * r - d * d, 0)) * 0.94
        lines.add(Line(c + nrm * d - u * h, c + nrm * d + u * h))
        d += gap
    return chalk(lines, color, width, seed, n=2)


def wave(p0, p1, amp, lam, color, seed=0, width=6.0, head=True):
    p0, p1 = np.array(p0), np.array(p1)
    L = np.linalg.norm(p1 - p0); u = (p1 - p0) / L; nrm = np.array([-u[1], u[0], 0])
    curve = ParametricFunction(lambda s: p0 + u * s + nrm * amp * np.sin(2 * PI * s / lam) * min(1, s / (lam * 0.5)),
                               t_range=[0, L, L / 120])
    g = VGroup(curve)
    if head:
        g.add(VMobject().set_points_as_corners([p1 - u * 0.22 + nrm * 0.14, p1, p1 - u * 0.22 - nrm * 0.14]))
    return chalk(g, color, width, seed, n=2)


def stick_figure(base, s=1.0, color=CREAM, seed=0):
    x, y = base[0], base[1]
    g = VGroup(Circle(radius=0.17 * s).move_to([x, y + 0.83 * s, 0]),
               Line([x, y + 0.66 * s, 0], [x, y + 0.2 * s, 0]),
               VMobject().set_points_as_corners([[x - 0.22 * s, y + 0.38 * s, 0], [x, y + 0.5 * s, 0], [x + 0.24 * s, y + 0.42 * s, 0]]),
               VMobject().set_points_as_corners([[x - 0.18 * s, y - 0.18 * s, 0], [x, y + 0.2 * s, 0], [x + 0.18 * s, y - 0.18 * s, 0]]))
    return chalk(g, color, 6, seed)


def later(anim, delay):
    return Succession(Wait(run_time=delay), anim) if delay > 0 else anim


class Sky(MovingCameraScene):
    def at(self, t):
        now = self.renderer.time  # temps réellement rendu (évite la dérive d'arrondi des frames)
        if t > now + 1e-3:
            self.wait(t - now)
        self.T = t

    def run(self, t, dur, *anims):
        """Joue un bloc d'animations sur [t, t+dur] ; une animation sans durée explicite remplit le bloc."""
        self.at(t)
        anims = [prepare_animation(a) for a in anims]
        for a in anims:
            if abs(a.run_time - 1.0) < 1e-9:
                a.run_time = dur
        self.play(AnimationGroup(*anims, Wait(run_time=dur)), run_time=dur)
        self.T = t + dur

    def chiffon(self, t, dur, mobs, extra=()):
        """Transition signature : un chiffon balaie de gauche à droite ; chaque tracé s'efface quand il passe."""
        cloth = VGroup(*[Ellipse(width=w, height=18, stroke_width=0).set_fill(CREAM, op)
                         for w, op in [(3.2, 0.03), (2.0, 0.045), (1.0, 0.06)]]).move_to([-7, 0, 0])
        self.add(cloth)
        items = sorted(mobs, key=lambda m: m.get_center()[0])
        x0, x1 = -7.0, 7.0
        anims = [prepare_animation(cloth.animate(rate_func=rate_functions.ease_in_out_sine, run_time=dur).move_to([x1, 0, 0]))]
        for m in items:
            # instant où le chiffon atteint le centre de l'objet (avec easing approximé linéaire)
            k = np.clip((m.get_center()[0] - x0) / (x1 - x0), 0, 1)
            delay = dur * (0.15 + 0.7 * k) - 0.12
            anims.append(later(FadeOut(m, run_time=0.24), max(0, min(delay, dur - 0.24))))
        # traces de chiffon qui restent sur le tableau
        smear = VGroup(*[Rectangle(width=RNG.uniform(3, 6), height=RNG.uniform(0.25, 0.6), stroke_width=0)
                         .set_fill(CREAM, 0.025).move_to([RNG.uniform(-3, 3), RNG.uniform(-5, 5), 0])
                         .rotate(RNG.uniform(-0.15, 0.15)) for _ in range(3)])
        anims.append(later(FadeIn(smear, run_time=0.3), dur * 0.4))
        anims += list(extra)
        self.run(t, dur, *anims)
        self.remove(cloth)
        self.bring_to_back(smear); self.bring_to_back(self.board)

    def construct(self):
        self.T = 0.0
        board = ImageMobject(str(ASSETS / 'board.png')); board.set_height(16); board.move_to(ORIGIN)
        self.board = board
        self.add(board)
        # caméra : zooms lents pilotés par le temps absolu (déterministe), via un mobject invisible à updater
        frame = self.camera.frame
        self.clock = 0.0
        mc0 = P(540, 1000)
        def cam(t):
            e = rate_functions.ease_in_out_sine
            k1 = e(np.clip((t - 5.8) / 3.0, 0, 1)) - e(np.clip((t - 8.9) / 0.5, 0, 1))
            k2 = e(np.clip((t - 15.0) / 1.4, 0, 1))
            sc = 1 - 0.07 * k1 - 0.035 * k2
            ctr = mc0 * 0.6 * k1 + P(540, 1150) * 0.35 * k2
            return sc, ctr
        def tick(m, dt):
            self.clock = self.renderer.time  # temps exact des frames déjà écrites
            sc, ctr = cam(self.clock)
            frame.set(width=9 * sc); frame.move_to(ctr)
        ticker = Dot(radius=0.001).set_opacity(0).add_updater(tick)
        self.add(ticker)
        S = {s['name']: s for s in TL['sections']}

        # ---------- 1. lumière blanche (hook : soleil dessiné < 0.6 s, titre en overlay dès t=0)
        sc, sr = P(210, 720), 0.7
        sun = chalk(Circle(radius=sr).move_to(sc), ORANGE, 7, 1)
        sun_fill = hachure_circle(sc, sr * 0.95, ORANGE, 0.11, 2)
        rays = VGroup(*[chalk(Line(sc + 0.93 * np.array([np.cos(a), np.sin(a), 0]), sc + 1.25 * np.array([np.cos(a), np.sin(a), 0])), ORANGE, 6, 10 + i)
                        for i, a in enumerate(np.linspace(0, 2 * PI, 11)[:-1])])
        underline = chalk(ArcBetweenPoints(P(330, 506), P(600, 500), angle=-0.15), BLUE, 7, 3)
        self.run(0.0, 0.7, Create(sun), later(Create(sun_fill, lag_ratio=0.4, run_time=0.5), 0.15),
                 later(LaggedStart(*[Create(r) for r in rays], lag_ratio=0.3, run_time=0.5), 0.2),
                 later(Create(underline, run_time=0.35), 0.3))
        beam = VGroup(chalk(Line(P(312, 772), P(560, 932)), CREAM, 12, 20), chalk(Line(P(318, 790), P(556, 946)), CREAM, 4, 21))
        self.run(0.9, 0.8, Create(beam))
        fan = P(566, 940)
        waves = VGroup(*[wave(fan, P(950, y), a, lam, col, 30 + i) for i, (y, a, lam, col) in enumerate(
            [(830, 0.16, 0.95, RED), (910, 0.14, 0.75, ORANGE), (990, 0.12, 0.6, GREEN), (1070, 0.1, 0.45, BLUE)])])
        self.run(2.6, 1.2, LaggedStart(*[Create(w) for w in waves], lag_ratio=0.25))
        s1 = [sun, sun_fill, rays, underline, beam, waves]
        self.chiffon(S['chiffon-1']['t0'], 0.5, s1)

        # ---------- 2. la molécule : le rouge passe, le bleu rebondit partout (zoom lent)
        mc = P(540, 1000)
        mol = VGroup(chalk(Circle(radius=0.26).move_to(mc + [-0.17, 0.05, 0]), TEXT, 6, 40),
                     chalk(Circle(radius=0.22).move_to(mc + [0.2, -0.04, 0]), TEXT, 6, 41),
                     hachure_circle(mc + [-0.17, 0.05, 0], 0.24, TEXT, 0.09, 42), hachure_circle(mc + [0.2, -0.04, 0], 0.2, TEXT, 0.09, 43, angle=-PI / 4))
        self.run(5.4, 0.4, Create(mol))
        frame = self.camera.frame
        red_in = wave(P(70, 1000), mc + [-0.5, 0, 0], 0.16, 0.95, RED, 50, head=False)
        red_out = wave(mc + [0.5, 0, 0], P(955, 1000), 0.16, 0.95, RED, 51)
        blue_in = wave(P(90, 700), mc + [-0.35, 0.25, 0], 0.1, 0.42, BLUE, 52, head=False)
        self.run(5.8, 1.1, Succession(Create(red_in, run_time=0.55), Create(red_out, run_time=0.55)), later(Create(blue_in, run_time=0.6), 0.45))
        scat = VGroup()
        for i, ang in enumerate([92, 55, 20, 128, 160, 200, 338]):
            a = np.deg2rad(ang); d = np.array([np.cos(a), np.sin(a), 0])
            scat.add(wave(mc + d * 0.5, mc + d * 2.45, 0.09, 0.42, BLUE, 60 + i, width=5))
        self.run(6.9, 1.3, LaggedStart(*[Create(s) for s in scat], lag_ratio=0.18))
        self.chiffon(8.9, 0.5, [mol, red_in, red_out, blue_in, scat])

        # ---------- 3. ×5 : barres
        base_y = 1450
        axis = chalk(Line(P(150, base_y), P(900, base_y)), CREAM, 6, 70)
        def bar(cx, h, col, seed):
            x0, x1, y1 = cx - 95, cx + 95, base_y - h
            outline = chalk(VMobject().set_points_as_corners([P(x0, base_y), P(x0, y1), P(x1, y1), P(x1, base_y)]), col, 7, seed)
            hl = VGroup(*[Line(P(x0 + 8, yy), P(x1 - 8, yy - 60)) for yy in np.arange(base_y - 10, y1 + 70, -26)])
            return VGroup(outline, chalk(hl, col, 4, seed + 1, n=1))
        rbar, bbar = bar(340, 130, RED, 72), bar(700, 650, BLUE, 74)
        self.run(9.4, 0.45, Create(axis))
        self.run(9.85, 1.0, GrowFromEdge(rbar, DOWN, rate_func=rate_functions.ease_out_cubic),
                 later(GrowFromEdge(bbar, DOWN, run_time=0.8, rate_func=rate_functions.ease_out_back), 0.2))
        self.at(11.6)
        self.chiffon(11.6, 0.4, [axis, rbar, bbar])

        # ---------- 4. coucher de soleil : trajet plus long dans l'air
        ec = P(540, 2150)
        tint = Circle(radius=1000 / 120).move_to(ec).set_stroke(width=0).set_fill(ORANGE, 0)
        earth = Circle(radius=700 / 120).move_to(ec).set_stroke(width=0).set_fill(C['surface'], 0.0)
        earth_line = chalk(Circle(radius=700 / 120).move_to(ec), CREAM, 7, 80, n=30)
        atmo = chalk(DashedVMobject(Circle(radius=1000 / 120).move_to(ec), num_dashes=90, dashed_ratio=0.55), BLUE, 5, 81, n=0)
        obs = stick_figure(P(540, 1450), 0.9, CREAM, 82)
        self.add(tint, earth)
        self.run(12.0, 0.6, Create(earth_line), Create(atmo), earth.animate.set_fill(opacity=0.9), later(Create(obs, run_time=0.35), 0.25))
        nsun = VGroup(chalk(Circle(radius=0.42).move_to(P(540, 640)), CREAM, 7, 83), hachure_circle(P(540, 640), 0.4, CREAM, 0.1, 84))
        nray = chalk(Line(P(540, 712), P(540, 1330)), CREAM, 8, 85)
        nblue = VGroup(*[wave(P(540, y), P(540 + dx, y - 110), 0.06, 0.3, BLUE, 86 + i, 4) for i, (y, dx) in enumerate([(1200, 120), (1270, -120)])])
        self.run(12.6, 0.4, Create(nsun))
        self.run(13.0, 0.5, Create(nray), later(LaggedStart(*[Create(b) for b in nblue], lag_ratio=0.4, run_time=0.4), 0.15))
        self.at(13.9)
        esun = VGroup(chalk(Circle(radius=0.55).move_to(P(30, 1420)), RED, 8, 90), hachure_circle(P(30, 1420), 0.52, ORANGE, 0.1, 91))
        self.run(13.9, 0.4, FadeOut(nsun), FadeOut(nray), FadeOut(nblue), Create(esun))
        eray = chalk(Line(P(100, 1416), P(500, 1416)), CREAM, 9, 92)
        for l in eray:
            l.set_stroke(color=[CREAM, ORANGE, RED])
        eblue = VGroup(*[wave(P(x, 1404), P(x + 40, 1290), 0.05, 0.28, BLUE, 93 + i, 4) for i, x in enumerate([120, 200, 280, 360, 440])])
        self.run(14.3, 0.7, Create(eray), later(LaggedStart(*[Create(b) for b in eblue], lag_ratio=0.3, run_time=0.6), 0.3))
        self.run(15.0, 0.9, tint.animate(rate_func=rate_functions.ease_in_out_sine).set_fill(ORANGE, 0.17))
        self.at(TL['duration'])
