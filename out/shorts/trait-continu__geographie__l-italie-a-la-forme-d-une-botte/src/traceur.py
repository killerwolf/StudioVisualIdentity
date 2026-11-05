#!/usr/bin/env python3
"""
traceur.py — moteur de l'identité « Trait continu » (le traceur). Copie identique dans chaque short.

Principe : un seul trait graphite continu, jamais levé, avance à vitesse constante en escalier (deux axes, pas de 12 px)
sur une plaque gris métal à angles vifs posée sur un fond orange plein cadre. Deux règles graduées (bord haut, bord
gauche) portent chacune un curseur triangulaire qui suit x et y ; un chariot suit la pointe. Entre deux scènes,
« l'avance plaque » : la plaque remonte en 3 crans (0,6 s) et sort par le haut, une plaque vierge entre par le bas (clac).

- shapely 2.2.0 : construction du chemin unique (segmentize, simplify, linemerge, ponts entre composantes par
  nearest_points, état à t = substring(chemin, 0, L(t))).
- opensimplex 0.4.5.1 : grain de surface de la plaque, masque de grain du trait, vibration ±0,5 px. Champs calculés
  UNE fois par short et mis en cache (.npy), jamais par image.
- pycairo : dessin ; Pillow (polices @fontsource .woff2 via out/tools/textpng.py) : textes ; ffmpeg rawvideo bgra.

Chaque image i est un pur calcul de t = i/30 : aucun état caché, rendu déterministe (graine fixée).
"""
import math, os, sys, subprocess, time, json
from pathlib import Path
import numpy as np
import cairo
from PIL import Image, ImageDraw, ImageFont
import shapely
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import substring, linemerge, nearest_points
import opensimplex

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'out' / 'tools'))
from textpng import font_path  # noqa: E402

W, H, FPS = 1080, 1920, 30

# ---------- palette (contrastes vérifiés : voir identity.md) ----------
ORANGE = '#F26A21'      # fond plein cadre
PLATE = '#D3D4CE'       # plaque gris métal
GRAPHITE = '#3A3D42'    # trait, curseurs, chariot (7,31:1 sur la plaque)
INK_ORANGE = '#1A1410'  # texte sur l'orange (5,96:1)
INK_PLATE = '#22252A'   # texte sur plaque / étiquette crème (10,3:1 / 14,6:1)
BLUE = '#1D47A8'        # repères (5,59:1 sur la plaque)
CREAM = '#FFF8EE'       # étiquettes (jamais de texte crème sur l'orange)

# ---------- mise en page (px sur 1080×1920) ----------
PX0, PY0, PX1, PY1 = 120, 500, 940, 1460     # plaque (angles vifs)
RW = 56                                       # largeur des règles
DX0, DY0 = PX0 + RW, PY0 + RW                 # origine de la zone de dessin
TITLE_Y = 355                                 # centre vertical de la bande titre (230–470)
CX = 510                                      # centre horizontal de la zone sûre (60..960)
STEP = 12                                     # pas de l'escalier (≥ 12 px : pas d'aliasing sur téléphone)
LINE_W = 7                                    # épaisseur du trait (6–8 px)
SPEED = 850                                   # px/s, constant (650–900)
CRAN = 0.2                                    # durée d'un cran d'avance plaque (3 crans = 0,6 s)
ENTER = 0.35                                  # entrée de la plaque vierge
D_OUT = PY1 + 24                              # course de sortie (la plaque quitte le cadre par le haut)
D_IN = H - PY0 + 20                           # course d'entrée (depuis le bas)
ENTER_DELAY = 0.25                            # la plaque vierge commence à entrer 0,25 s après le 1er cran
OVERLAP = 3 * CRAN - ENTER_DELAY              # = 0,35 s de chevauchement : aucune image quasi uniforme (mesuré ≤ 78 % d'orange)


def next_enter(exit_t):
    """Instant du « clac » de la plaque suivante quand la précédente commence ses crans à exit_t."""
    return round(exit_t + ENTER_DELAY + ENTER, 3)   # clac à la fin du 3e cran


def rgb(h, a=1.0):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


def ease_out_cubic(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 3


def ease_back_out(u, s=1.6):
    u = min(max(u, 0.0), 1.0)
    u -= 1
    return u * u * ((s + 1) * u + s) + 1


# ---------- bruit (opensimplex, une seule fois) ----------
def noise_fields(seed, cache_dir):
    """Champs de grain mis en cache : fine (grain) et coarse (marbrure), taille plaque, valeurs ~[-1, 1]."""
    cache_dir = Path(cache_dir); cache_dir.mkdir(parents=True, exist_ok=True)
    f = cache_dir / f'noise_seed{seed}.npz'
    pw, ph = PX1 - PX0, PY1 - PY0
    if f.exists():
        z = np.load(f)
        return z['fine'], z['coarse'], z['vib'], 0.0
    t0 = time.time()
    opensimplex.seed(seed)
    fine = opensimplex.noise2array(np.arange(pw // 2) * 0.45, np.arange(ph // 2) * 0.45)
    coarse = opensimplex.noise2array(np.arange(pw // 8) * 0.07, np.arange(ph // 8) * 0.07)
    vib = opensimplex.noise2array(np.arange(4096) * 0.21, np.array([0.0, 31.7]))
    up = lambda a: np.asarray(Image.fromarray(a.astype(np.float32), 'F').resize((pw, ph), Image.BILINEAR))
    fine, coarse = up(fine), up(coarse)
    np.savez(f, fine=fine, coarse=coarse, vib=vib)
    return fine, coarse, vib, time.time() - t0


# ---------- chemin unique ----------
def _merge_collinear(cells):
    """Fusionne les points alignés de même sens (garde les demi-tours : allers-retours superposés)."""
    out = [cells[0]]
    for c in cells[1:]:
        if len(out) >= 2:
            a, b = out[-2], out[-1]
            d1 = (np.sign(b[0] - a[0]), np.sign(b[1] - a[1]))
            d2 = (np.sign(c[0] - b[0]), np.sign(c[1] - b[1]))
            if d1 == d2:
                out[-1] = c
                continue
        out.append(c)
    return out


def stair_cells(coords, start_cell=None):
    """Polyligne -> suite de cellules d'une grille de STEP px, chaque pas sur un seul axe (escalier)."""
    ls = shapely.segmentize(LineString(coords), 2.0)
    pts = np.asarray(ls.coords)
    cells = np.round((pts - (DX0, DY0)) / STEP).astype(int)
    cur = tuple(cells[0]) if start_cell is None else start_cell
    out = [cur]
    for c in cells:
        tx, ty = int(c[0]), int(c[1])
        cx, cy = cur
        while (cx, cy) != (tx, ty):
            dx, dy = tx - cx, ty - cy
            if dx != 0 and (abs(dx) >= abs(dy)):
                cx += 1 if dx > 0 else -1
            else:
                cy += 1 if dy > 0 else -1
            out.append((cx, cy))
        cur = (cx, cy)
    return out


class Trace:
    """Chemin unique d'une scène. pieces = [(nom, coords)], reliées par des ponts calculés si elles ne se touchent pas.
    Timeline : départ `start`, vitesse constante `speed`, arrêts {nom_de_piece: durée} en fin de pièce."""

    def __init__(self, pieces, start, speed=SPEED, stops=None, vib=None):
        cells, self.milestones, self.bridges = [], {}, []
        prev_end = None
        for name, coords in pieces:
            coords = list(map(tuple, coords))
            if prev_end is not None and Point(prev_end).distance(Point(coords[0])) > 1.0:
                # pont : segment le plus court entre la pointe et la pièce suivante (il fait partie du dessin)
                self.bridges.append((prev_end, coords[0]))
                c = stair_cells([prev_end, coords[0]], start_cell=cells[-1])
                cells += c[1:]
            c = stair_cells(coords, start_cell=cells[-1] if cells else None)
            cells += c[1:] if cells else c
            prev_end = coords[-1]
            self.milestones[name] = len(cells) - 1
        cells = _merge_collinear(cells)
        pts = np.array(cells, float) * STEP + (DX0, DY0)
        if vib is not None:  # vibration ±0,5 px, fixe par sommet (pas de « boil »)
            n = len(pts)
            pts = pts + 0.5 * np.stack([vib[0, :n], vib[1, :n]], 1) / max(1e-6, np.abs(vib).max())
        self.line = LineString(pts)
        self.total = self.line.length
        seg = np.hypot(*np.diff(pts, axis=0).T)
        self.cum = np.concatenate([[0], np.cumsum(seg)])
        self.pts = pts
        self.start, self.speed = start, speed
        self.stops = []
        # chaque pas non fusionné fait exactement STEP px : longueur au jalon = index × STEP
        self.mlen = {n: k * STEP for n, k in self.milestones.items()}

    # t -> longueur tracée
    def length_at(self, t):
        tt = t - self.start
        if tt <= 0:
            return 0.0
        L, tc = 0.0, 0.0
        for Ls, d in self.stops:
            travel = (Ls - L) / self.speed
            if tt < tc + travel:
                return L + (tt - tc) * self.speed
            tc += travel; L = Ls
            if tt < tc + d:
                return L
            tc += d
        return min(L + (tt - tc) * self.speed, self.total)

    def time_at(self, Lt):
        L, tc = 0.0, 0.0
        for Ls, d in self.stops:
            if Lt <= Ls:
                return self.start + tc + (Lt - L) / self.speed
            tc += (Ls - L) / self.speed + d; L = Ls
        return self.start + tc + (Lt - L) / self.speed

    @property
    def end_time(self):
        return self.time_at(self.total)

    def moving(self, t):
        L = self.length_at(t)
        return 0 < L < self.total and abs(self.length_at(t + 1 / FPS) - L) > 1e-6

    def point(self, L):
        p = self.line.interpolate(L)
        return p.x, p.y

    def partial(self, L):
        if L <= 0:
            return None
        if L >= self.total:
            return self.pts
        return np.asarray(substring(self.line, 0, L).coords)


def build_path(pieces, start, speed=SPEED, stops=None, vib=None):
    """pieces : [(nom, coords)] ; stops : {nom: durée} (arrêt quand la pointe atteint la fin de la pièce nommée)."""
    p = Trace(pieces, start, speed, vib=vib)
    lengths = p.mlen
    p.stops = sorted((lengths[n], d) for n, d in (stops or {}).items())
    return p


def chaikin(pts, n=3):
    """Adoucit une polyligne ouverte (extrémités conservées)."""
    p = np.asarray(pts, float)
    for _ in range(n):
        q = 0.75 * p[:-1] + 0.25 * p[1:]
        r = 0.25 * p[:-1] + 0.75 * p[1:]
        p = np.vstack([p[:1], np.column_stack([q, r]).reshape(-1, 2), p[-1:]])
    return p


def spiral(cx, cy, R, turns, end_angle=math.pi / 2, n=900):
    """Spirale d'Archimède qui part du centre et s'enroule dans le sens horaire (écran, y vers le bas)."""
    th = np.linspace(0, 2 * math.pi * turns, n)
    phi = end_angle - th[-1]
    r = R * th / th[-1]
    return np.column_stack([cx + r * np.cos(th + phi), cy + r * np.sin(th + phi)])


def loop(cx, cy, r, a0=math.pi / 2, n=40):
    a = np.linspace(a0, a0 + 2 * math.pi, n)
    return np.column_stack([cx + r * np.cos(a), cy + r * np.sin(a)])


def bridge_ring(from_xy, ring_coords):
    """Fait tourner un contour fermé pour qu'il commence au point le plus proche de from_xy (pont le plus court)."""
    ring = LineString(list(ring_coords) + [ring_coords[0]])
    _, q = nearest_points(Point(from_xy), ring)
    pts = list(ring_coords)
    k = int(np.argmin([math.hypot(x - q.x, y - q.y) for x, y in pts]))
    rot = pts[k:] + pts[:k]
    return rot + [rot[0]]


# ---------- textes (PIL lit les .woff2 @fontsource) ----------
_FONTS = {}
_KEEP = []


def font(weight, size):
    k = (weight, size)
    if k not in _FONTS:
        _FONTS[k] = ImageFont.truetype(font_path('fredoka', weight), size)
    return _FONTS[k]


def pil_to_surface(img):
    a = np.asarray(img.convert('RGBA'), dtype=np.uint16)
    al = a[..., 3:4]
    pre = (a[..., :3] * al // 255).astype(np.uint8)
    bgra = np.concatenate([pre[..., ::-1], a[..., 3:4].astype(np.uint8)], axis=2).copy()
    h, w = bgra.shape[:2]
    stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, w)
    buf = np.zeros((h, stride // 4, 4), np.uint8); buf[:, :w] = bgra
    s = cairo.ImageSurface.create_for_data(buf, cairo.FORMAT_ARGB32, w, h, stride)
    _KEEP.append(buf)  # le tampon numpy doit vivre aussi longtemps que la surface
    return s


def text_surface(text, weight=700, size=100, color=INK_ORANGE, line_h=1.08, label=None, pad=(26, 14)):
    """Texte (multi-lignes) recadré ; label=CREAM -> étiquette crème à angles vifs avec liseré graphite."""
    f = font(weight, size)
    lines = text.split('\n')
    d0 = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    widths = [d0.textlength(l, font=f) for l in lines]
    asc, desc = f.getmetrics()
    lh = int(size * line_h)
    tw, th = int(max(widths)) + 2, lh * (len(lines) - 1) + asc + desc
    px, py = pad if label else (4, 4)
    img = Image.new('RGBA', (tw + 2 * px, th + 2 * py), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if label:
        d.rectangle([0, 0, img.width - 1, img.height - 1], fill=label, outline=INK_PLATE, width=3)
    for i, (l, w) in enumerate(zip(lines, widths)):
        d.text((px + (tw - w) / 2, py + i * lh - 2), l, font=f, fill=color)
    return pil_to_surface(img)


# ---------- le short ----------
class Plate:
    def __init__(self, enter=None, exit=None):
        self.enter, self.exit = enter, exit   # enter = instant du « clac » (None : présente dès t=0) ; exit = début des crans
        self.path = None
        self.items = []    # repères / étiquettes : dicts {kind, t, ...}

    def offset(self, t):
        y = 0.0
        if self.enter is not None:
            if t < self.enter - ENTER:
                return None
            if t < self.enter:
                y = D_IN * (1 - ease_out_cubic((t - (self.enter - ENTER)) / ENTER))
        if self.exit is not None and t >= self.exit:
            k = (t - self.exit) / CRAN
            i = int(k)
            if i >= 3:
                return None
            f = ease_out_cubic(min((k - i) / 0.45, 1.0))
            y = -D_OUT * (i + f) / 3
        return y


class Short:
    def __init__(self, seed, duration, cache_dir):
        self.seed, self.duration = seed, duration
        self.fine, self.coarse, self.vib, self.noise_sec = noise_fields(seed, cache_dir)
        self.plates, self.titles = [], []
        self._plate_surface = self._make_plate_surface()
        self._mask = self._make_stroke_mask()

    # surfaces statiques (une fois) ------------------------------------------------
    def _make_plate_surface(self):
        pw, ph = PX1 - PX0, PY1 - PY0
        base = np.array(rgb(PLATE)[:3]) * 255
        lum = 1 + 0.035 * self.coarse + 0.028 * self.fine
        img = np.clip(base[None, None, :] * lum[..., None], 0, 255).astype(np.uint8)
        uw, uh = pw + 16, ph + 20
        unit = cairo.ImageSurface(cairo.FORMAT_ARGB32, uw, uh)
        c = cairo.Context(unit)
        c.set_source_rgba(0.30, 0.09, 0.0, 0.30)       # ombre portée sur l'orange
        c.rectangle(10, 14, pw, ph); c.fill()
        c.set_source_surface(pil_to_surface(Image.fromarray(img, 'RGB')), 0, 0); c.paint()
        # règles graduées (bord haut, bord gauche)
        c.set_source_rgba(0, 0, 0, 0.075)
        c.rectangle(0, 0, pw, RW); c.fill()
        c.rectangle(0, RW, RW, ph - RW); c.fill()
        c.set_source_rgba(*rgb(GRAPHITE, 0.55)); c.set_line_width(2)
        c.move_to(RW, RW); c.line_to(pw, RW); c.stroke()
        c.move_to(RW, RW); c.line_to(RW, ph); c.stroke()
        c.set_source_rgba(*rgb(GRAPHITE, 0.85))
        for k, x in enumerate(range(RW, pw, 24)):
            L = 22 if k % 5 == 0 else 11
            c.set_line_width(2.5 if k % 5 == 0 else 2)
            c.move_to(x, RW); c.line_to(x, RW - L); c.stroke()
        for k, y in enumerate(range(RW, ph, 24)):
            L = 22 if k % 5 == 0 else 11
            c.set_line_width(2.5 if k % 5 == 0 else 2)
            c.move_to(RW, y); c.line_to(RW - L, y); c.stroke()
        # 4 vis aux coins
        for sx, sy in [(RW / 2, RW / 2), (pw - 24, 24), (24, ph - 24), (pw - 24, ph - 24)]:
            c.arc(sx, sy, 10, 0, 2 * math.pi); c.set_source_rgba(*rgb('#B3B4AD')); c.fill_preserve()
            c.set_source_rgba(*rgb('#7E7F79')); c.set_line_width(2); c.stroke()
            c.move_to(sx - 6, sy - 3); c.line_to(sx + 6, sy + 3); c.set_line_width(2.5); c.stroke()
        return unit

    def _make_stroke_mask(self):
        pw, ph = PX1 - PX0, PY1 - PY0
        a = np.clip(0.84 + 0.16 * np.tanh(self.fine * 3.0) + 0.04 * self.coarse, 0.62, 1.0)
        stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_A8, pw)
        buf = np.zeros((ph, stride), np.uint8); buf[:, :pw] = (a * 255).astype(np.uint8)
        s = cairo.ImageSurface.create_for_data(buf, cairo.FORMAT_A8, pw, ph, stride)
        _KEEP.append(buf)
        return s

    # description de la scène ------------------------------------------------------
    def plate(self, enter=None, exit=None):
        p = Plate(enter, exit); self.plates.append(p); return p

    def title(self, t0, t1, text, size=104):
        self.titles.append(dict(t0=t0, t1=t1, surf=text_surface(text, 700, size, INK_ORANGE)))

    # dessin d'une image ------------------------------------------------------------
    def _draw_items(self, c, plate, t):
        for it in plate.items:
            if t < it['t']:
                continue
            u = (t - it['t']) / 0.28
            s = ease_back_out(u) if u < 1 else 1.0
            k = it['kind']
            if k == 'lead':   # fil de repère bleu, tiré en 0,25 s
                (ax, ay), (bx, by) = it['a'], it['b']
                f = min(1.0, (t - it['t']) / 0.25)
                c.set_source_rgba(*rgb(BLUE)); c.set_line_width(5); c.set_dash([])
                c.move_to(ax, ay); c.line_to(ax + (bx - ax) * f, ay + (by - ay) * f); c.stroke()
                continue
            x, y = it['xy']
            c.save(); c.translate(x, y); c.scale(max(s, 0.001), max(s, 0.001))
            if k == 'ring':
                c.arc(0, 0, 17, 0, 2 * math.pi); c.set_source_rgba(*rgb(BLUE)); c.set_line_width(6); c.stroke()
            elif k == 'pin':
                c.arc(0, 0, 13, 0, 2 * math.pi); c.set_source_rgba(*rgb(BLUE)); c.fill()
                c.arc(0, 0, 26, 0, 2 * math.pi); c.set_line_width(5); c.stroke()
            elif k == 'arrow':   # arc fléché horaire (repère de sens)
                r, a0, a1 = it['r'], it['a0'], it['a1']
                c.set_source_rgba(*rgb(BLUE)); c.set_line_width(9); c.set_line_cap(cairo.LINE_CAP_ROUND)
                n = max(2, int(abs(a1 - a0) * 40))
                aa = np.linspace(a0, a0 + (a1 - a0) * min(1.0, max(0.0, (t - it['t']) / 0.5)), n)
                c.move_to(r * math.cos(aa[0]), r * math.sin(aa[0]))
                for a in aa[1:]:
                    c.line_to(r * math.cos(a), r * math.sin(a))
                c.stroke()
                ae = aa[-1]; ex, ey = r * math.cos(ae), r * math.sin(ae)
                tx, ty = -math.sin(ae), math.cos(ae)     # tangente sens horaire (y vers le bas)
                nx, ny = math.cos(ae), math.sin(ae)
                c.move_to(ex + tx * 30, ey + ty * 30); c.line_to(ex + nx * 22, ey + ny * 22)
                c.line_to(ex - nx * 22, ey - ny * 22); c.close_path(); c.fill()
            elif k in ('text', 'label'):
                surf = it['surf']
                c.set_source_surface(surf, -surf.get_width() / 2, -surf.get_height() / 2); c.paint()
            c.restore()

    def _draw_plate(self, c, plate, t, oy):
        c.save(); c.translate(PX0, PY0 + oy)
        c.set_source_surface(self._plate_surface, 0, 0); c.paint()
        c.restore()
        path = plate.path
        if path is not None:
            L = path.length_at(t)
            pts = path.partial(L)
            if pts is not None and len(pts) >= 2:
                pw, ph = PX1 - PX0, PY1 - PY0
                layer = cairo.ImageSurface(cairo.FORMAT_ARGB32, pw, ph)
                lc = cairo.Context(layer)
                lc.translate(-PX0, -PY0)
                lc.set_source_rgba(*rgb(GRAPHITE)); lc.set_line_width(LINE_W)
                lc.set_line_join(cairo.LINE_JOIN_MITER); lc.set_line_cap(cairo.LINE_CAP_SQUARE)
                lc.move_to(*pts[0])
                for x, y in pts[1:]:
                    lc.line_to(x, y)
                lc.stroke()
                c.save(); c.translate(PX0, PY0 + oy)
                c.set_source_surface(layer, 0, 0); c.mask_surface(self._mask, 0, 0)
                c.restore()
        c.save(); c.translate(0, oy)
        self._draw_items(c, plate, t)
        if path is not None:
            x, y = path.point(path.length_at(t))
            self._draw_carriage(c, x, y)
        c.restore()

    def _draw_carriage(self, c, x, y):
        # guides des deux axes (fils fins), curseurs triangulaires sur les règles, chariot carré à angles vifs
        c.set_source_rgba(*rgb(GRAPHITE, 0.32)); c.set_line_width(2); c.set_dash([10, 8])
        c.move_to(x, DY0 + 2); c.line_to(x, y - 26); c.stroke()
        c.move_to(DX0 + 2, y); c.line_to(x - 26, y); c.stroke()
        c.set_dash([])
        c.set_source_rgba(*rgb(GRAPHITE))
        c.move_to(x - 15, PY0 + 8); c.line_to(x + 15, PY0 + 8); c.line_to(x, DY0 - 4); c.close_path(); c.fill()
        c.move_to(PX0 + 8, y - 15); c.line_to(PX0 + 8, y + 15); c.line_to(DX0 - 4, y); c.close_path(); c.fill()
        c.rectangle(x - 23, y - 23, 46, 46)
        c.set_source_rgba(*rgb('#ECEDE8', 0.55)); c.fill_preserve()
        c.set_source_rgba(*rgb(GRAPHITE)); c.set_line_width(4); c.stroke()
        c.arc(x, y, 5.5, 0, 2 * math.pi); c.fill()

    def frame(self, t):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        c = cairo.Context(surf)
        c.set_source_rgba(*rgb(ORANGE)); c.paint()
        for tt in self.titles:
            if tt['t0'] - 0.0 <= t < tt['t1']:
                u = (t - tt['t0']) / 0.3
                a = min(1.0, max(0.0, u)) * min(1.0, max(0.0, (tt['t1'] - t) / 0.2))
                dy = 26 * (1 - ease_back_out(u)) if u < 1 else 0
                s = tt['surf']
                c.set_source_surface(s, CX - s.get_width() / 2, TITLE_Y - s.get_height() / 2 + dy)
                c.paint_with_alpha(a)
        # la plaque passe au-dessus de la bande titre pendant l'avance (elle la masque, pas de texte sur la plaque)
        for p in self.plates:
            oy = p.offset(t)
            if oy is not None:
                self._draw_plate(c, p, t, oy)
        surf.flush()
        return surf

    def frame_bgra(self, t):
        s = self.frame(t)
        return bytes(s.get_data())

    def frame_pil(self, t):
        s = self.frame(t)
        a = np.ndarray((H, s.get_stride() // 4, 4), np.uint8, s.get_data())[:, :W]
        return Image.fromarray(a[..., 2::-1].copy(), 'RGB')

    # sons calés sur la scène (cliquetis du traceur, crans, clac) ---------------------
    def sound_events(self):
        ev = []
        for p in self.plates:
            if p.path is not None:
                t = p.path.start
                while t < min(p.path.end_time, self.duration):
                    if p.path.moving(t):
                        ev.append({'t': round(t, 3), 'type': 'tick', 'gain': 0.22})
                    t += 0.24
                for Ls, d in p.path.stops:
                    ev.append({'t': round(p.path.time_at(Ls), 3), 'type': 'click', 'gain': 0.5})
            if p.exit is not None:
                for i in range(3):
                    ev.append({'t': round(p.exit + i * CRAN, 3), 'type': 'click', 'gain': 0.7})
            if p.enter is not None:
                ev.append({'t': round(p.enter, 3), 'type': 'thud', 'gain': 0.75})
            for it in p.items:
                if it.get('sfx'):
                    ev.append({'t': round(it['t'], 3), 'type': it['sfx'], 'gain': it.get('gain', 0.5), 'note': it.get('note', 'E6')})
        return sorted(ev, key=lambda e: e['t'])


def render(short, out, t_list=None):
    """Rendu complet -> mp4 (pipe rawvideo bgra vers x264)."""
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    part = str(out) + '.part.mp4'
    n = int(round(short.duration * FPS))
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16',
                           '-pix_fmt', 'yuv420p', '-r', str(FPS), part], stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(n):
        ff.stdin.write(short.frame_bgra(i / FPS))
    ff.stdin.close(); ff.wait(); os.replace(part, out)
    sec = time.time() - t0
    return {'frames': n, 'seconds': round(sec, 1), 'secPer100Frames': round(sec / n * 100, 2), 'noiseSec': round(short.noise_sec, 2)}


def main(build, default_out):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=default_out)
    ap.add_argument('--stills'); ap.add_argument('--dir')
    ap.add_argument('--sound-json')
    ap.add_argument('--info', action='store_true')
    a = ap.parse_args()
    tb = time.time()
    short = build()
    build_sec = time.time() - tb
    if a.info:
        for i, p in enumerate(short.plates):
            if p.path:
                print(json.dumps({'plate': i, 'start': p.path.start, 'end': round(p.path.end_time, 2), 'length': round(p.path.total),
                                  'milestones': {k: round(p.path.time_at(v), 2) for k, v in p.path.mlen.items()},
                                  'vertices': len(p.path.pts)}))
        print(json.dumps({'buildSec': round(build_sec, 2), 'noiseSec': round(short.noise_sec, 2)}))
        return
    if a.sound_json:
        spec = json.loads(Path(a.sound_json).read_text())
        spec['events'] = short.sound_events() + spec.get('extraEvents', [])
        spec['duration'] = short.duration
        Path(a.sound_json).write_text(json.dumps(spec, indent=1, ensure_ascii=False))
        print(a.sound_json, len(spec['events']), 'events')
        return
    if a.stills:
        Path(a.dir).mkdir(parents=True, exist_ok=True)
        for s in a.stills.split(','):
            t = float(s)
            t0 = time.time(); im = short.frame_pil(t); dt = time.time() - t0
            p = Path(a.dir) / f'still_{t:05.2f}s.jpg'
            im.save(p, quality=92)
            print(p, f'{dt * 1000:.0f} ms/frame')
        return
    print(json.dumps(render(short, a.out) | {'buildSec': round(build_sec, 2)}))
