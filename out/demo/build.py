#!/usr/bin/env python3
"""
build.py — vidéo démo « Caméléon » en français (43 s), en 16:9 (1920×1080) et 9:16 (1080×1920).

Tout est dessiné image par image en Python (numpy + OpenCV + Pillow), sans navigateur : la démo prend tour à tour
le fond, la police et la couleur de chacune des 18 identités, avec les vrais shorts du dépôt comme matière.

USAGE (depuis la racine du dépôt, avec le venv du dépôt)
  .venv/bin/python out/demo/build.py clips            # extrait les images des shorts utiles (cache dans $SVI_TMP)
  .venv/bin/python out/demo/build.py stills 16x9 0.9 3.2 8.0   # images de contrôle -> $SVI_TMP/stills/
  .venv/bin/python out/demo/build.py video 16x9|9x16  # image seule -> $SVI_TMP/video_<fmt>.mp4
  .venv/bin/python out/demo/build.py audio            # musique + bruitages -> $SVI_TMP/bed.wav (+ voix si voice_fr/NN.mp3)
  .venv/bin/python out/demo/build.py final 16x9|9x16  # mux -> demo_<fmt>_novo.mp4 (sans voix) et demo_<fmt>.mp4
  .venv/bin/python out/demo/build.py gif | thumb | sheet
  .venv/bin/python out/demo/build.py all

VOIX OFF : aucune voix n'est générée ici. Le texte et le minutage sont dans narration_fr.json. Dès que les fichiers
out/demo/voice_fr/NN.mp3 existent (un par ligne, NN = index de la ligne), `audio` puis `final` les mixent avec
atténuation de la musique (ducking) dans demo_<fmt>.mp4 ; demo_<fmt>_novo.mp4 reste sans voix.
Cache : $SVI_TMP (défaut /tmp/svi/demo_fr).
"""
import json, math, os, subprocess, sys
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TMP = Path(os.environ.get('SVI_TMP', '/tmp/svi/demo_fr'))
SHORTS = ROOT / 'out' / 'shorts'
FPS = 30
NB = ' '  # espace insécable

# ------------------------------------------------------------------ minutage (120 BPM : un temps = 0,5 s)
T_MUT = 2.5     # une carte se met à changer de style
T_COV = 4.0     # carrousel des 18 identités
T_WALL = 14.0   # mur des 45 shorts
T_JUDGE = 18.0  # juge à l'aveugle
T_TERM = 22.0   # le prompt
T_CHK = [26.0, 27.0, 29.0]   # ✓ style, ✓ studio, ✓ épisode 1
T_EP = [29.0, 31.0, 33.0]    # épisodes 1, 2, 3
T_SLAM = 35.0   # 4 panneaux, un par seconde
T_END = 39.0
DUR = 43.0

# ------------------------------------------------------------------ les 18 identités (du plus clair au plus sombre)
DELA = 'out/shared/papier-moteur/assets/fonts/DelaGothicOne-Regular.woff2'
# id, nom, short, début (s), police d'affichage, graisse, fond, encre, accent
IDS = [
    ('swiss-data', 'Grille Suisse', 'swiss-data__geographie__ou-vivent-8-milliards', 1.2, 'archivo-black', 400, '#F4F1EA', '#111111', '#E3241B'),
    ('bauhaus-kinetic', 'Bauhaus Cinétique', 'bauhaus-kinetic__explicatif__abeilles-hexagones', 0.3, 'unbounded', 800, '#F2EDE3', '#111111', '#1D4ED8'),
    ('riso-zine', 'Zine Riso', 'riso-zine__evenements__geminides-j-39', 0.6, 'space-mono', 700, '#F6F0E4', '#1A1A1A', '#FF48B0'),
    ('gazette-1900', 'Gazette 1900', 'gazette-1900__histoire__1789-en-20-secondes', 3.0, 'playfair-display', 900, '#E9E1CF', '#1E1B18', '#B3261E'),
    ('atlas-grave', 'Atlas Gravé', 'atlas-grave__histoire__premier-tour-du-monde-1519-1522', 8.0, 'cormorant-garamond', 700, '#EFE3C8', '#2A1F14', '#8C2F1B'),
    ('aquarelle-conte', 'Aquarelle Conte', 'aquarelle-conte__histoire__phare-d-alexandrie', 5.0, 'fraunces', 700, '#F7F1E6', '#3A3042', '#E88D72'),
    ('pastel-diorama', 'Diorama Pastel', 'pastel-diorama__engagement__choisis-ta-boite-renard', 10.0, 'baloo-2', 800, '#FFE8EF', '#3B2E5A', '#FF8FAB'),
    ('carte-meteo', 'Carte Météo', 'carte-meteo__geographie__le-mistral-pourquoi-il-souffle-si-fort', 7.0, 'space-grotesk', 700, '#CFE6F5', '#10263D', '#D63A2A'),
    ('trait-continu', 'Trait continu', 'trait-continu__geographie__l-italie-a-la-forme-d-une-botte', 5.0, 'fredoka', 700, '#F26A21', '#1A1410', '#FFF8EE'),
    ('survol-pixel', 'Survol pixel', 'survol-pixel__histoire__machu-picchu-pourquoi-une-cite-en-escaliers', 3.0, 'jersey-15', 400, '#1E5AA8', '#FBF3D5', '#FFC94A'),
    ('papier-decoupe', 'Papier découpé', 'papier-decoupe__histoire__la-fourchette-a-fait-scandale', 0.3, DELA, 400, '#1F5A4A', '#F7F4EC', '#FFD23F'),
    ('tableau-craie', 'Tableau Craie', 'tableau-craie__enfants__comment-une-graine-devient-un-arbre', 9.0, 'nunito', 800, '#1F3A30', '#F7F3E3', '#FFB84C'),
    ('topo-relief', 'Relief Topo', 'topo-relief__geographie__comment-mesure-t-on-l-everest', 2.0, 'jetbrains-mono', 700, '#14221C', '#F1EEDC', '#E8C872'),
    ('pixel-arcade', 'Arcade Pixel', 'pixel-arcade__engagement__quelle-couleur-conquiert-l-ecran', 4.0, 'rubik-mono-one', 400, '#0E0B1F', '#FFFFFF', '#3CF2A0'),
    ('neon-lab', 'Labo Néon', 'neon-lab__explicatif__lune-meme-face', 7.0, 'space-grotesk', 700, '#05060B', '#F2F6FF', '#38F9FF'),
    ('cosmos-doc', 'Cosmos Doc', 'cosmos-doc__explicatif__pourquoi-venus-plus-chaude-que-mercure', 10.0, 'bebas-neue', 400, '#07070D', '#EAF2FF', '#FFB347'),
    ('liquid-chrome', 'Chrome Liquide', 'liquid-chrome__abstrait__quatre-peintures-mpm', 4.0, 'syne', 800, '#0B0B10', '#FFFFFF', '#FF9AE8'),
    ('brut-meme', 'Brut Mème', 'brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde', 0.2, 'anton', 400, '#111111', '#FFFFFF', '#FFE600'),
]
N = len(IDS)
IDX = {r[0]: k for k, r in enumerate(IDS)}
FAMILIES = {}
for _i in json.load(open(ROOT / 'out/identities/index.json'))['identities']:
    FAMILIES[_i['id']] = _i['familiesProven']
FAM_FR = {'abstrait': 'abstrait', 'enfants': 'enfants', 'explicatif': 'explicatif', 'histoire': 'histoire',
          'geographie': 'géographie', 'evenements': 'événements', 'engagement': 'engagement'}
ALL_SHORTS = sorted(p.name for p in SHORTS.iterdir() if (p / 'short.mp4').exists())
MUTANTS = ['gazette-1900', 'pixel-arcade', 'pastel-diorama', 'cosmos-doc', 'trait-continu']  # 2,5 -> 3,75 s
EPISODES = [('pixel-arcade__engagement__quelle-bille-gagne-la-course', 4.0),
            ('pixel-arcade__engagement__quelle-couleur-conquiert-l-ecran', 4.5),
            ('pixel-arcade__abstrait__la-balle-peut-elle-s-echapper', 6.0)]
PANELS = [('gazette-1900', '18', 'identités'), ('brut-meme', '21', 'déclinaisons'),
          ('pixel-arcade', '45', 'shorts'), ('neon-lab', '100' + NB + '%', 'open source')]
DARK = '#0B0D17'
YEL = '#FFE600'
DEMO = ('unbounded', 800)
MONO = ('jetbrains-mono', 500)
MONOB = ('jetbrains-mono', 700)
GROT = ('space-grotesk', 600)

PROMPT = ['> Lis AGENTS.md de',
          '  github.com/killerwolf/StudioVisualIdentity.',
          '  Choisis le style d’une chaîne de défis',
          '  pour ados, crée notre studio,',
          '  puis réalise notre premier épisode.']
CHECKS = ['style choisi' + NB + ': Arcade Pixel', 'studio créé' + NB + ': defis-ados/', 'épisode 1 rendu · contrôle qualité OK',
          'épisode 2 rendu', 'épisode 3 rendu']
T_CHECKS = T_CHK + [T_EP[1], T_EP[2]]
TYPE0, TYPE1 = T_TERM + 0.5, T_TERM + 3.7

NARRATION = [
    (0.3, 2.0, 'Encore la même vidéo' + NB + '?'),
    (2.6, 5.8, 'Et si la vôtre ne ressemblait à aucune autre' + NB + '?'),
    (6.2, 9.4, 'Voici dix-huit identités visuelles pour vos vidéos courtes.'),
    (9.8, 13.6, 'Gazette, pixel, néon, aquarelle' + NB + ': à chacune sa signature.'),
    (14.3, 17.6, 'Quarante-cinq shorts le prouvent, tous rendus par du code.'),
    (18.3, 21.7, 'Testées à l’aveugle' + NB + ': dix-huit reconnues sur dix-huit.'),
    (22.3, 25.6, 'Le plus simple' + NB + '? Donnez un prompt à votre agent.'),
    (26.0, 28.7, 'Il choisit le style, crée votre studio…'),
    (29.1, 31.0, '… et réalise votre premier épisode.'),
    (31.3, 34.6, 'Puis le deuxième. Le troisième. À votre image.'),
    (35.0, 38.8, 'Dix-huit identités. Quarante-cinq shorts. Tout est open source.'),
    (39.4, 42.0, 'Studio Visual Identity. À vous de jouer.'),
]

# ------------------------------------------------------------------ géométrie par format
FMT = {
    '16x9': dict(W=1920, H=1080,
                 card=(405, 720), ccx=960, ccy=500, sp=(410, 300, 250),
                 head_y=66, head_size=50, head_w=1700, name_y=932, name_size=84, meta_y=1004, bar_y=1050, bar_w=1100,
                 hook_y=(300, 530, 760), hook_size=176,
                 wall=dict(cols=15, rows=3, speed=250), wall_ty=905,
                 judge=dict(cols=18, rows=4, pw=96, ph=160, tw=84, th=150, x0=102, y0=50), judge_ty=880,
                 term=dict(x=90, y=215, w=1050, h=680, fs=33, lh=51), th_xy=(90, 62), th_size=78,
                 menu=dict(x=1190, y=235, pw=116, ph=206, tw=106, th=188), phone=(1335, 175, 405, 720),
                 ),
    '9x16': dict(W=1080, H=1920,
                 card=(520, 924), ccx=540, ccy=880, sp=(470, 330, 260),
                 head_y=276, head_size=44, head_w=880, name_y=1438, name_size=80, meta_y=1514, bar_y=1566, bar_w=820,
                 hook_y=(700, 880, 1060), hook_size=132,
                 wall=dict(cols=9, rows=5, speed=180), wall_ty=1440,
                 judge=dict(cols=9, rows=8, pw=100, ph=140, tw=76, th=134, x0=100, y0=250), judge_ty=1500,
                 term=dict(x=60, y=345, w=900, h=590, fs=30, lh=46), th_xy=(60, 240), th_size=64,
                 menu=dict(x=124, y=985, pw=138, ph=200, tw=106, th=188), phone=(336, 965, 348, 618),
                 ),
}
F = {}
W = H = 0


def setfmt(fmt):
    global F, W, H
    F = FMT[fmt]
    F['fmt'] = fmt
    W, H = F['W'], F['H']


# ------------------------------------------------------------------ petits outils
def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, x):
    return tuple(int(round(a[i] + (b[i] - a[i]) * x)) for i in range(3))


def u(t, t0, d):
    return 0.0 if t <= t0 else 1.0 if t >= t0 + d else (t - t0) / d


def eo3(x):
    return 1 - (1 - x) ** 3


def eio(x):
    return x * x * (3 - 2 * x)


def back(x, c=1.70158):
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


@lru_cache(None)
def font(fkey, size):
    slug, wt = fkey
    if '/' in slug:
        p = ROOT / slug
    else:
        p = ROOT / f'node_modules/@fontsource/{slug}/files/{slug}-latin-{wt}-normal.woff2'
    return ImageFont.truetype(str(p), int(size))


@lru_cache(4000)
def T(txt, fkey, size, fill, stroke=0, sfill='#000000'):
    """Texte -> sprite RGBA (hauteur = métriques de la police : la ligne de base ne bouge pas)."""
    f = font(fkey, size)
    asc, desc = f.getmetrics()
    w = int(f.getlength(txt)) + 2 * stroke + 8
    im = Image.new('RGBA', (max(w, 2), asc + desc + 2 * stroke + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 + stroke, 4 + stroke + asc), txt, font=f, fill=fill, anchor='ls', stroke_width=stroke, stroke_fill=sfill)
    return np.array(im)


@lru_cache(4000)
def Tt(txt, fkey, size, fill, stroke=0, sfill='#000000'):
    """Comme T, mais rogné au plus près de l'encre (pour centrer optiquement les gros titres)."""
    a = T(txt, fkey, size, fill, stroke, sfill)
    ys = np.where(a[..., 3].max(1) > 0)[0]
    xs = np.where(a[..., 3].max(0) > 0)[0]
    if len(ys) == 0:
        return a
    return np.ascontiguousarray(a[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1])


def fit(txt, fkey, size, maxw):
    f = font(fkey, size)
    w = f.getlength(txt)
    return size if w <= maxw else int(size * maxw / w)


def blit(fr, spr, x, y, a=1.0):
    """Colle un sprite RGBA (coin haut-gauche x, y), avec rognage."""
    x, y = int(round(x)), int(round(y))
    h, w = spr.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, fr.shape[1]), min(y + h, fr.shape[0])
    if x1 <= x0 or y1 <= y0 or a <= 0:
        return
    s = spr[y0 - y:y1 - y, x0 - x:x1 - x]
    al = s[..., 3:4].astype(np.float32) * (a / 255.0)
    reg = fr[y0:y1, x0:x1]
    reg[:] = (reg * (1 - al) + s[..., :3] * al + 0.5).astype(np.uint8)


def blitc(fr, spr, cx, cy, a=1.0, sc=1.0):
    if sc != 1.0:
        h, w = spr.shape[:2]
        nw, nh = max(1, int(w * sc)), max(1, int(h * sc))
        spr = cv2.resize(spr, (nw, nh), interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_LINEAR)
    blit(fr, spr, cx - spr.shape[1] / 2, cy - spr.shape[0] / 2, a)


def rect(fr, x0, y0, x1, y1, col, a=1.0):
    x0, y0, x1, y1 = max(int(x0), 0), max(int(y0), 0), min(int(x1), fr.shape[1]), min(int(y1), fr.shape[0])
    if x1 <= x0 or y1 <= y0:
        return
    if a >= 1:
        fr[y0:y1, x0:x1] = col
    else:
        reg = fr[y0:y1, x0:x1]
        reg[:] = (reg * (1 - a) + np.array(col, np.float32) * a).astype(np.uint8)


@lru_cache(600)
def rr(w, h, r, fill, outline=None, ow=0):
    """Rectangle arrondi anti-crénelé -> sprite RGBA. fill/outline : '#rrggbb' ou '#rrggbbaa' ou None."""
    S = 3
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w * S - 1, h * S - 1), r * S, fill=fill, outline=outline, width=ow * S)
    return np.array(im.resize((w, h), Image.LANCZOS))


@lru_cache(200)
def shadow(w, h, r, blur, alpha=150):
    pad = blur * 3
    im = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.uint8)
    m = rr(w, h, r, '#000000')[..., 3]
    im[pad:pad + h, pad:pad + w, 3] = m
    im[..., 3] = (cv2.GaussianBlur(im[..., 3], (0, 0), blur).astype(np.float32) * alpha / 255).astype(np.uint8)
    return im


@lru_cache(64)
def glow(size, col):
    """Halo radial doux, teinté."""
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    d = np.sqrt((x - size / 2) ** 2 + (y - size / 2) ** 2) / (size / 2)
    a = np.clip(1 - d, 0, 1) ** 2
    im = np.zeros((size, size, 4), np.uint8)
    im[..., :3] = rgb(col)
    im[..., 3] = (a * 255).astype(np.uint8)
    return im


@lru_cache(32)
def check_spr(size, col):
    S = 4
    im = Image.new('RGBA', (size * S, size * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    p = [(0.12, 0.55), (0.40, 0.82), (0.90, 0.20)]
    d.line([(x * size * S, y * size * S) for x, y in p], fill=col, width=int(size * S * 0.16), joint='curve')
    return np.array(im.resize((size, size), Image.LANCZOS))


def quad_blit(fr, src, quad, a=1.0):
    """Colle src (RGBA) déformé en perspective sur le quadrilatère quad (hg, hd, bd, bg)."""
    q = np.float32(quad)
    x0, y0 = np.floor(q.min(0)).astype(int)
    x1, y1 = np.ceil(q.max(0)).astype(int)
    cx0, cy0, cx1, cy1 = max(x0, 0), max(y0, 0), min(x1, fr.shape[1]), min(y1, fr.shape[0])
    if cx1 <= cx0 or cy1 <= cy0 or a <= 0:
        return
    h, w = src.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), q - np.float32([cx0, cy0]))
    out = cv2.warpPerspective(src, M, (int(cx1 - cx0), int(cy1 - cy0)), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    al = out[..., 3:4].astype(np.float32) * (a / 255.0)
    reg = fr[cy0:cy1, cx0:cx1]
    reg[:] = (reg * (1 - al) + out[..., :3] * al + 0.5).astype(np.uint8)


# ------------------------------------------------------------------ cache des images des shorts
def clip_dir(key):
    return TMP / 'clips' / key


CLIPS = {}  # key -> (short, t0, dur, w, h, fps)
for _k, _r in enumerate(IDS):
    CLIPS['c_' + _r[0]] = (_r[2], _r[3], 4.6, 540, 960, 30)
for _s in ALL_SHORTS:
    CLIPS['w_' + _s] = (_s, 1.0, 5.0, 188, 334, 15)
for _k, (_s, _t0) in enumerate(EPISODES):
    CLIPS[f'e_{_k}'] = (_s, _t0, 2.6, 540, 960, 30)


def clips():
    for key, (s, t0, dur, w, h, fps) in CLIPS.items():
        d = clip_dir(key)
        tag = d / f'{w}x{h}.ok'
        if tag.exists():
            continue
        for f in d.glob('*.jpg') if d.exists() else []:
            f.unlink()
        d.mkdir(parents=True, exist_ok=True)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(t0), '-t', str(dur), '-i', str(SHORTS / s / 'short.mp4'),
                        '-vf', f'fps={fps},scale={w}:{h}:flags=area', '-q:v', '3', str(d / '%04d.jpg')], check=True)
        tag.write_text('ok')
        print(key, len(list(d.glob('*.jpg'))), flush=True)


@lru_cache(None)
def clip_len(key):
    return len(list(clip_dir(key).glob('*.jpg')))


@lru_cache(900)
def cframe(key, i):
    n = clip_len(key)
    i = max(0, min(n - 1, int(i)))
    im = cv2.imread(str(clip_dir(key) / f'{i + 1:04d}.jpg'))
    return cv2.cvtColor(im, cv2.COLOR_BGR2RGB)


def pingpong(i, n):
    i = int(i) % (2 * n - 2)
    return i if i < n else 2 * n - 2 - i


@lru_cache(8)
def card_mask(w, h, r):
    return rr(w, h, r, '#ffffff')[..., 3]


def card_rgba(img, r=40, border=None, bw=5):
    """Image RGB -> carte RGBA à coins arrondis, avec liseré optionnel."""
    h, w = img.shape[:2]
    out = np.dstack([img, card_mask(w, h, r)])
    if border:
        b = rr(w, h, r, None, border, bw)
        al = b[..., 3:4].astype(np.float32) / 255
        out[..., :3] = (out[..., :3] * (1 - al) + b[..., :3] * al).astype(np.uint8)
    return out


@lru_cache(2000)
def thumb(key, i, w, h, r=0):
    im = cv2.resize(cframe(key, i), (w, h), interpolation=cv2.INTER_AREA)
    return card_rgba(im, r) if r else np.dstack([im, np.full((h, w), 255, np.uint8)])


def lum(c):
    return (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 255


# ------------------------------------------------------------------ fond commun
@lru_cache(4)
def vignette(w, h):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    v = 1 - 0.30 * np.clip(d - 0.35, 0, 1.2) ** 1.6
    return np.dstack([v, v, v]).astype(np.float32)


@lru_cache(4)
def grain(w, h, k):
    return np.random.default_rng(k).integers(0, 9, (h, w, 1), dtype=np.uint8).repeat(3, 2)


def finish(fr, n):
    fr = cv2.multiply(fr, vignette(W, H), dtype=cv2.CV_8U)
    return cv2.subtract(cv2.add(fr, grain(W, H, n % 5)), 4)


def dark_bg(t, col=DARK):
    fr = np.empty((H, W, 3), np.uint8)
    fr[:] = rgb(col)
    g = glow(1200, '#2B3BFF')
    blitc(fr, g, W * 0.2 + 60 * math.sin(t * 0.5), H * 0.15, 0.20)
    blitc(fr, glow(1200, '#FF3DCB'), W * 0.85, H * 0.9 + 50 * math.cos(t * 0.4), 0.13)
    return fr


# ------------------------------------------------------------------ scène 1 : l'accroche
@lru_cache(2)
def template_card(w, h):
    """La carte « template générique » : dégradé violet-bleu, avatar, titre, lignes."""
    S = 2
    im = Image.new('RGB', (w * S, h * S))
    g = np.linspace(0, 1, h * S)[:, None, None]
    arr = (np.array(rgb('#7B5CF0'), np.float32) * (1 - g) + np.array(rgb('#3D8BFF'), np.float32) * g).repeat(w * S, 1)
    im = Image.fromarray(arr.astype(np.uint8))
    d = ImageDraw.Draw(im)
    cx = w * S // 2
    d.ellipse((cx - 46 * S, 70 * S, cx + 46 * S, 162 * S), fill='#FFFFFF')
    d.ellipse((cx - 16 * S, 98 * S, cx + 16 * S, 130 * S), fill='#6F6BF2')
    d.rounded_rectangle((22 * S, 210 * S, (w - 22) * S, 300 * S), 12 * S, fill='#FFFFFF')
    f = font(('inter', 800), 20 * S)
    d.text((cx, 245 * S), 'VOTRE TITRE ICI', font=f, fill='#2A2F45', anchor='mm')
    d.rounded_rectangle((60 * S, 268 * S, (w - 60) * S, 276 * S), 4 * S, fill='#C9CEE0')
    for k, ww in enumerate((0.78, 0.6)):
        d.rounded_rectangle((22 * S, (330 + k * 26) * S, int(22 + (w - 44) * ww) * S, (342 + k * 26) * S), 6 * S, fill='#FFFFFF')
    d.rounded_rectangle((22 * S, (h - 60) * S, (w - 22) * S, (h - 22) * S), 19 * S, fill='#1B1E33')
    d.text((cx, (h - 41) * S), 'S’ABONNER', font=font(('inter', 800), 15 * S), fill='#FFFFFF', anchor='mm')
    out = np.array(im.resize((w, h), Image.LANCZOS))
    return card_rgba(out, 22)


@lru_cache(2)
def template_grid(gw, gh, pw, ph):
    g = np.empty((gh, gw, 3), np.uint8)
    g[:] = rgb('#0B0D17')
    c = template_card(pw - 26, ph - 26)
    sh = shadow(pw - 26, ph - 26, 22, 10, 140)
    for y in range(0, gh, ph):
        for x in range(0, gw, pw):
            blit(g, sh, x + 13 - 30, y + 13 - 22)
            blit(g, c, x + 13, y + 13)
    return g


def hook_words(fr, t):
    lines = [('ENCORE', -0.10), ('LA MÊME', 0.50), ('VIDÉO' + NB + '?', 0.90)]   # « ENCORE » est déjà là à la première image
    out = u(t, T_MUT - 0.05, 0.22)
    if out >= 1:
        return
    size = F['hook_size']
    blitc(fr, glow(int(max(W, H) * 0.9), '#05060B'), W / 2, F['hook_y'][1], 0.55 * eo3(u(t, -0.1, 0.2)) * (1 - out))
    for k, (txt, t0) in enumerate(lines):
        x = u(t, t0, 0.16)
        if x <= 0:
            continue
        sc = (1.9 - 0.9 * back(x, 2.2)) * (1 - 0.25 * out)
        a = min(1, x * 3) * (1 - out)
        cy = F['hook_y'][k] - 60 * out
        if k == 1:
            s = Tt(txt, ('unbounded', 900), size, '#111111')
            box = rr(s.shape[1] + 70, s.shape[0] + 50, 10, YEL)
            blitc(fr, shadow(box.shape[1], box.shape[0], 10, 14, 170), W / 2 + 10, cy + 16, a, sc)
            blitc(fr, box, W / 2, cy, a, sc)
            blitc(fr, s, W / 2, cy, a, sc)
        else:
            s = Tt(txt, ('unbounded', 900), size, '#FFFFFF')
            b = Tt(txt, ('unbounded', 900), size, '#0A0A12')
            blitc(fr, b, W / 2 + 9 * sc, cy + 11 * sc, a, sc)
            blitc(fr, s, W / 2, cy, a, sc)


def header(fr, t, ink, shadow_col=None):
    """La phrase du haut : la question (2,7 -> 6 s) puis « 18 identités visuelles »."""
    def line(txt, a, dy, col, fk=DEMO):
        size = fit(txt, fk, F['head_size'], F['head_w'])
        s = T(txt, fk, size, col)
        if shadow_col:
            blitc(fr, T(txt, fk, size, shadow_col), W / 2 + 3, F['head_y'] + dy + 4, a * 0.8)
        blitc(fr, s, W / 2, F['head_y'] + dy, a)
    q = 'Et si la vôtre ne ressemblait à aucune autre' + NB + '?'
    a1 = eo3(u(t, 2.7, 0.3)) * (1 - u(t, 5.75, 0.25))
    a2 = eo3(u(t, 6.0, 0.3))
    if a1 > 0:
        if F['fmt'] == '9x16':
            line('Et si la vôtre ne ressemblait', a1, -34 + 20 * (1 - a1), ink)
            line('à aucune autre' + NB + '?', a1, 34 + 20 * (1 - a1), ink)
        else:
            line(q, a1, 14 * (1 - a1), ink)
    if a2 > 0:
        txt = '18 identités visuelles'
        size = fit(txt, DEMO, 58, F['head_w'])
        blitc(fr, T(txt, DEMO, size, ink), W / 2, F['head_y'] + 14 * (1 - a2), a2)


def scene_hook(t, n):
    fmt9 = F['fmt'] == '9x16'
    pw, ph = (300, 500) if not fmt9 else (290, 484)
    gw, gh = (W + 1500, H + 1400)
    gw, gh = (gw // pw + 1) * pw, (gh // ph + 1) * ph
    G = template_grid(gw, gh, pw, ph)
    # défilement qui ralentit puis s'arrête à 2,5 s
    sc_t = min(t, T_MUT)
    scroll = (430 * sc_t - 430 * sc_t * sc_t / (2 * T_MUT)) % ph
    ang = math.radians(-7)
    c, s = math.cos(ang), math.sin(ang)
    A = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], np.float64)
    Tc = np.array([[1, 0, -gw / 2], [0, 1, -gh / 2 - scroll + ph / 2], [0, 0, 1]], np.float64)
    Pm = np.array([[1, 0, 0], [0, 1, 0], [0, -0.00022 if not fmt9 else -0.00012, 1]], np.float64)
    Tb = np.array([[1, 0, W / 2], [0, 1, H / 2], [0, 0, 1]], np.float64)
    fr = cv2.warpPerspective(G, Tb @ Pm @ A @ Tc, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=rgb('#0B0D17'))
    # après 2,5 s : la grille s'éteint, une carte prend vie
    m = u(t, T_MUT, 0.5)
    z = eio(u(t, 3.55, 0.45))  # fondu vers le fond de la première identité
    if m > 0:
        fr = cv2.convertScaleAbs(fr, alpha=1 - 0.62 * eo3(m))
    if z > 0:
        bg = np.empty_like(fr)
        bg[:] = rgb(IDS[0][6])
        fr = cv2.addWeighted(fr, 1 - z, bg, z, 0)
    hook_words(fr, t)
    if t >= T_MUT:
        k = int((t - T_MUT) / 0.25)
        ident = MUTANTS[k] if k < len(MUTANTS) else IDS[0][0]
        r = IDS[IDX[ident]]
        cw, chh = F['card']
        grow = eo3(u(t, T_MUT, 0.3)) * 0.78 + 0.22 * eio(u(t, 3.4, 0.6))
        pop = back(u(t, T_MUT, 0.3))
        local = u(t, T_MUT + 0.25 * k, 0.12) if k < len(MUTANTS) + 1 and k > 0 else 1
        sc = (0.45 + 0.55 * pop) * (0.9 + 0.1 * eio(u(t, 3.4, 0.6))) * (1 + 0.05 * (1 - eo3(local)))
        w2, h2 = int(cw * sc), int(chh * sc)
        fi = 60 + (t - T_MUT) * 30 if ident != IDS[0][0] else (t - (T_COV - 0.25)) * 30
        img = cv2.resize(cframe('c_' + ident, fi), (w2, h2), interpolation=cv2.INTER_AREA)
        blitc(fr, glow(int(h2 * 1.9), r[8]), F['ccx'], F['ccy'], 0.45)
        blitc(fr, shadow(w2, h2, 30, 24, 170), F['ccx'], F['ccy'] + 26)
        blitc(fr, card_rgba(img, max(8, int(40 * sc * 0.75)), r[8] if ident != IDS[0][0] else None, 6), F['ccx'], F['ccy'])
    ink = (255, 255, 255) if z < 0.5 else rgb(IDS[0][7])
    header(fr, t, ink, (10, 10, 18) if z < 0.5 else None)
    return fr


# ------------------------------------------------------------------ scène 2 : le carrousel caméléon
def cov_start(k):
    return T_COV + (k if k < 2 else 2 + 0.5 * (k - 2))


def cov_pos(t):
    """Position flottante du carrousel (indice de la carte au centre)."""
    if t < T_COV + 1:
        return 0.0
    k = 1 if t < T_COV + 2 else min(N - 1, 2 + int((t - T_COV - 2) / 0.5))
    return k - 1 + eo3(u(t, cov_start(k), 0.26))


def card_quad(d, extra=0.0):
    """Quadrilatère d'une carte à la distance d du centre (carrousel convexe : les côtés reculent)."""
    cw, chh = F['card']
    ad = abs(d)
    sg = 1 if d >= 0 else -1
    a, b, c = F['sp']
    off = a * min(ad, 1) + b * max(0, min(ad - 1, 1)) + c * max(0, ad - 2)
    sc = 1 - 0.20 * min(ad, 1) - 0.13 * max(0, min(ad - 1, 1)) - 0.08 * max(0, ad - 2)
    yaw = min(ad, 1.0)
    w2 = cw * sc * (1 - 0.30 * yaw)
    hn, hf = chh * sc, chh * sc * (1 - 0.17 * yaw)   # bord proche (intérieur), bord lointain (extérieur)
    cx = F['ccx'] + sg * (off + extra)
    cy = F['ccy'] + 10 * min(ad, 2)
    xi, xo = cx - sg * w2 / 2, cx + sg * w2 / 2
    pi_ = [(xi, cy - hn / 2), (xi, cy + hn / 2)]
    po = [(xo, cy - hf / 2), (xo, cy + hf / 2)]
    if sg > 0:
        return [pi_[0], po[0], po[1], pi_[1]], sc
    return [po[0], pi_[0], pi_[1], po[1]], sc


@lru_cache(64)
def ghost(txt, fkey, size, col):
    return Tt(txt, fkey, size, col)


def scene_cover(t, n):
    p = cov_pos(t)
    k0 = int(math.floor(p))
    k1 = min(N - 1, k0 + 1)
    x = p - k0
    A, B = IDS[k0], IDS[k1]
    bgc = mix(rgb(A[6]), rgb(B[6]), eio(x))
    ink = mix(rgb(A[7]), rgb(B[7]), 1 if x > 0.5 else 0)
    cur = IDS[int(round(p))]
    fr = np.empty((H, W, 3), np.uint8)
    fr[:] = bgc
    # nom fantôme géant, dans la police de l'identité
    for ident, a in ((A, 1 - x), (B, x)) if k1 != k0 else ((A, 1.0),):
        if a <= 0.02:
            continue
        gc = mix(rgb(ident[6]), rgb(ident[7]), 0.10)
        kk = IDX[ident[0]]
        gsz = int(H * (0.30 if F['fmt'] == '16x9' else 0.13))
        g = ghost(ident[1].upper(), (ident[4], ident[5]), gsz, '#%02x%02x%02x' % gc)
        drift = (t - cov_start(kk)) * 60
        gy = F['ccy'] - F['card'][1] * (0.30 if F['fmt'] == '16x9' else 0.36)
        blitc(fr, g, W / 2 - drift + (kk - p) * W * 0.5, gy, a)
    # halo d'accent derrière la carte centrale
    acc = mix(rgb(A[8]), rgb(B[8]), x)
    blitc(fr, glow(int(F['card'][1] * 2.1), '#%02x%02x%02x' % acc), F['ccx'], F['ccy'], 0.30 if lum(bgc) < 0.4 else 0.22)
    # cartes, de la plus lointaine à la plus proche
    ent = 1 - eo3(u(t, T_COV - 0.05, 0.55))
    def dist(k):
        return (k - p + N / 2) % N - N / 2
    order = sorted(range(N), key=lambda k: -abs(dist(k)))
    for k in order:
        d = dist(k)
        if abs(d) > 3.4:
            continue
        quad, sc = card_quad(d, extra=ent * W * 0.6 * (abs(d) > 0.01))
        ident = IDS[k]
        fi = (t - (cov_start(k) - 2.0)) * 30
        if k == 0 and t < T_COV + 4:
            fi = (t - (T_COV - 0.25)) * 30
        elif fi < 0 or fi >= clip_len('c_' + ident[0]):
            fi = pingpong(abs(fi), clip_len('c_' + ident[0]))
        img = cframe('c_' + ident[0], fi)
        dim = min(1.0, abs(d)) * 0.38 + max(0, abs(d) - 1) * 0.2
        if dim > 0.01:
            bgl = np.empty_like(img)
            bgl[:] = bgc
            img = cv2.addWeighted(img, 1 - dim, bgl, dim, 0)
        src = card_rgba(img, 40)
        # ombre au sol
        q = np.float32(quad)
        ww = (q[:, 0].max() - q[:, 0].min())
        hh = (q[:, 1].max() - q[:, 1].min())
        shw = shadow(int(ww), int(hh), 30, 22, 120 if lum(bgc) > 0.4 else 190)
        blitc(fr, shw, q[:, 0].mean(), q[:, 1].mean() + 24 * sc)
        quad_blit(fr, src, quad)
    # titre du haut
    header(fr, t, ink)
    # nom de l'identité, dans SA police, + méta
    ki = int(round(p))
    tk = cov_start(ki)
    ap = eo3(u(t, tk + 0.04, 0.2)) if ki > 0 else eo3(u(t, T_COV + 0.05, 0.3))
    fk = (cur[4], cur[5])
    inkc = '#%02x%02x%02x' % rgb(cur[7])
    size = fit(cur[1], fk, F['name_size'] * (1.25 if cur[4] in ('jersey-15', 'bebas-neue', 'anton', 'cormorant-garamond') else 1.0), W - 260 if F['fmt'] == '9x16' else 1100)
    blitc(fr, Tt(cur[1], fk, size, inkc), W / 2, F['name_y'] + 26 * (1 - ap), ap)
    fam = ' · '.join(FAM_FR[f] for f in FAMILIES[cur[0]])
    meta = f'{ki + 1:02d}/18  —  {fam}'
    blitc(fr, T(meta, MONOB, 30, inkc), W / 2, F['meta_y'], 0.85 * ap)
    # barre de progression : 18 pastilles aux couleurs des identités
    bw = F['bar_w']
    seg = bw / N
    for k in range(N):
        x0 = W / 2 - bw / 2 + k * seg
        on = k <= ki
        col = rgb(IDS[k][8]) if on else mix(bgc, ink, 0.22)
        hgt = 14 if k == ki else 8
        rect(fr, x0 + 3, F['bar_y'] - hgt / 2, x0 + seg - 3, F['bar_y'] + hgt / 2, col)
        if on:
            rect(fr, x0 + 3, F['bar_y'] + hgt / 2, x0 + seg - 3, F['bar_y'] + hgt / 2 + 2, mix(bgc, ink, 0.5))
    return fr


# ------------------------------------------------------------------ scène 3 : le mur des 45 shorts
def big_caption(fr, t, t0, big, small, y, col=YEL, small2=None):
    """Gros chiffre + phrase, centrés (bandeau sombre derrière)."""
    a = eo3(u(t, t0, 0.2))
    if a <= 0:
        return
    bs = 150 if F['fmt'] == '16x9' else 118
    ss = 58 if F['fmt'] == '16x9' else 46
    sb = Tt(big, ('unbounded', 900), bs, col)
    a2 = eo3(u(t, t0 + 0.8, 0.25))
    if F['fmt'] == '16x9':
        ssp = T(small, GROT, ss, '#FFFFFF')
        tw = sb.shape[1] + 50 + ssp.shape[1]
        x0 = W / 2 - tw / 2
        sc = 1.6 - 0.6 * back(u(t, t0, 0.2), 2.0)
        blitc(fr, sb, x0 + sb.shape[1] / 2, y, a, sc)
        blit(fr, ssp, x0 + sb.shape[1] + 50, y - ssp.shape[0] / 2 - (28 if small2 else 0) + 16 * (1 - a2), a2)
        if small2:
            blit(fr, T(small2, MONO, 34, '#C4CBE6'), x0 + sb.shape[1] + 54, y + 26 + 16 * (1 - a2), a2)
    else:
        sc = 1.6 - 0.6 * back(u(t, t0, 0.2), 2.0)
        blitc(fr, sb, W / 2 - 30, y - 30, a, sc)
        blitc(fr, T(small, GROT, ss, '#FFFFFF'), W / 2 - 30, y + 66 + 16 * (1 - a2), a2)
        if small2:
            blitc(fr, T(small2, MONO, 26, '#AEB6D4'), W / 2 - 30, y + 118 + 16 * (1 - a2), a2)


def scene_wall(t, n, t0=T_WALL, caption=True):
    """Le même mur incliné que l'accroche, mais cette fois chaque carte est un vrai short, toutes différentes."""
    g = F['wall']
    fmt9 = F['fmt'] == '9x16'
    cols, rows = g['cols'], g['rows']
    pw, ph, tw, th = 200, 356, 188, 334
    cw, chh = cols * pw, rows * ph
    can = np.empty((chh, cw, 3), np.uint8)
    can[:] = rgb(DARK)
    ccx, ccy = (cols - 1) / 2, (rows - 1) / 2
    for r in range(rows):
        for c in range(cols):
            j = r * cols + c
            key = 'w_' + ALL_SHORTS[(j * 7 + 3) % 45]   # ordre mélangé : les styles voisins diffèrent
            dist = math.hypot((c - ccx) / max(ccx, 1), (r - ccy) / max(ccy, 1))
            a = eo3(u(t, t0 - 0.12 + 0.22 * dist, 0.25))
            if a <= 0:
                continue
            fi = pingpong((t - t0) * 15 + j * 5, clip_len(key))
            blitc(can, thumb(key, fi, tw, th, 14), c * pw + pw / 2, r * ph + ph / 2, a, 0.7 + 0.3 * a)
    scroll = g['speed'] * (t - t0)
    big = np.tile(can, (3, 3, 1))
    ang = math.radians(-7)
    c_, s_ = math.cos(ang), math.sin(ang)
    zoom = 1.0 + 0.03 * (t - t0)
    A = np.array([[c_ * zoom, -s_ * zoom, 0], [s_ * zoom, c_ * zoom, 0], [0, 0, 1]], np.float64)
    Tc = np.array([[1, 0, -cw * 1.5 - (scroll % cw) + cw / 2], [0, 1, -chh * 1.5], [0, 0, 1]], np.float64)
    Pm = np.array([[1, 0, 0], [0, 1, 0], [0, -0.00022 if not fmt9 else -0.00012, 1]], np.float64)
    Tb = np.array([[1, 0, W / 2], [0, 1, H / 2 - (70 if not fmt9 else 0)], [0, 0, 1]], np.float64)
    fr = cv2.warpPerspective(big, Tb @ Pm @ A @ Tc, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=rgb(DARK))
    if caption:
        # dégradé sombre sous la légende
        y0 = F['wall_ty'] - (250 if not fmt9 else 340)
        gh = H - y0
        al = (np.clip(np.linspace(0, 1.5 if not fmt9 else 3.2, gh), 0, 1) ** 1.3 * 0.94 * eo3(u(t, t0 + 0.3, 0.3)))[:, None, None]
        reg = fr[y0:]
        reg[:] = (reg * (1 - al) + np.array(rgb('#07080F'), np.float32) * al).astype(np.uint8)
        big_caption(fr, t, t0 + 0.5, '45 shorts', 'tous rendus par du code', F['wall_ty'], YEL, '18 identités · 21 déclinaisons')
    return fr


# ------------------------------------------------------------------ scène 4 : le juge à l'aveugle
def judge_tiles():
    """72 vignettes : 4 par identité (2 shorts × 2 instants)."""
    out = []
    for k, r in enumerate(IDS):
        ss = [s for s in ALL_SHORTS if s.startswith(r[0] + '__')][:2]
        for s in ss:
            for fi in (20, 85):
                out.append((k, 'w_' + s, fi))
    return out


JT = None


def scene_judge(t, n):
    global JT
    if JT is None:
        JT = judge_tiles()
    g = F['judge']
    fr = dark_bg(t)
    rng = np.random.default_rng(72)
    perm = rng.permutation(72)
    jit = rng.uniform(-1, 1, (72, 2))
    cols, rows = g['cols'], g['rows']
    t_sort = T_JUDGE + 1.1
    t_tick = T_JUDGE + 2.3

    def sorted_pos(k, m):
        if F['fmt'] == '16x9':
            return g['x0'] + k * g['pw'], g['y0'] + m * g['ph']
        return g['x0'] + (k % 9) * g['pw'], g['y0'] + (k // 9) * (4 * g['ph'] + 28) + m * g['ph']

    done = min(N, int(max(0, (t - t_tick)) / 0.055))
    # cadres des groupes
    for k in range(N):
        a = eo3(u(t, t_sort + 0.5 + 0.02 * k, 0.3))
        if a <= 0:
            continue
        x, y = sorted_pos(k, 0)
        ok = k < done
        fw, fh = g['tw'] + 10, 4 * g['ph'] - (g['ph'] - g['th']) + 10
        blit(fr, rr(fw, fh, 10, '#3CF2A022' if ok else None, '#3CF2A0' if ok else '#5A6080', 3), x - 5, y - 5, a)
    for idx, (k, key, fi) in enumerate(JT):
        m = idx % 4
        sp = perm[idx]
        x0 = g['x0'] + (sp % cols) * g['pw'] + jit[idx, 0] * 5
        y0 = g['y0'] + (sp // cols) * g['ph'] + jit[idx, 1] * 5
        if F['fmt'] == '9x16':
            y0 += (sp // cols >= 4) * 28
        x1, y1 = sorted_pos(k, m)
        mv = eio(u(t, t_sort + 0.025 * k + 0.02 * m, 0.62))
        x = x0 + (x1 - x0) * mv
        y = y0 + (y1 - y0) * mv - 26 * math.sin(math.pi * mv)
        a = eo3(u(t, T_JUDGE + 0.004 * ((idx * 37) % 72), 0.25))
        wob = math.sin(t * 9 + idx) * 2.0 * (1 - mv) * (t > T_JUDGE + 0.4)
        spr = thumb(key, fi, g['tw'], g['th'], 7)
        blit(fr, spr, x + wob, y, a)
    # coches
    for k in range(done):
        x, y = sorted_pos(k, 0)
        pop = back(u(t, t_tick + k * 0.055, 0.15))
        cx, cy = x + g['tw'] / 2, y + 4 * g['ph'] - (g['ph'] - g['th']) + 2
        blitc(fr, rr(34, 34, 17, '#3CF2A0'), cx, cy, 1, pop)
        blitc(fr, check_spr(22, '#0B0D17'), cx, cy, 1, pop)
    # légende
    y = F['judge_ty']
    if t < t_sort + 0.9:
        a = eo3(u(t, T_JUDGE + 0.25, 0.25)) * (1 - u(t, t_sort + 0.6, 0.3))
        s1 = '72 images anonymes, mélangées'
        blitc(fr, T(s1, DEMO, fit(s1, DEMO, 60, W - 220), '#FFFFFF'), W / 2 - (30 if F['fmt'] == '9x16' else 0), y, a)
        s2 = 'un juge indépendant, sans contexte'
        blitc(fr, T(s2, MONO, 34 if F['fmt'] == '16x9' else 28, '#C4CBE6'), W / 2 - (30 if F['fmt'] == '9x16' else 0), y + 76, a)
    else:
        col = '#3CF2A0' if done >= N else '#FFFFFF'
        big = f'{done}/18'
        a = eo3(u(t, t_sort + 0.9, 0.2))
        bs = 150 if F['fmt'] == '16x9' else 112
        sb = Tt(big, ('unbounded', 900), bs, col)
        pulse = 1 + 0.10 * (1 - eo3(u(t, t_tick + N * 0.055, 0.3))) * (done >= N)
        s1 = 'Juge à l’aveugle' + NB + ': zéro erreur'
        if F['fmt'] == '16x9':
            ssp = T(s1, GROT, 58, '#FFFFFF')
            ref = Tt('18/18', ('unbounded', 900), bs, col).shape[1]
            tw = ref + 50 + ssp.shape[1]
            x0 = W / 2 - tw / 2
            blitc(fr, sb, x0 + ref / 2, y, a, pulse)
            a2 = eo3(u(t, t_tick + N * 0.055, 0.25))
            blit(fr, ssp, x0 + ref + 50, y - ssp.shape[0] / 2 - 28, a2)
            blit(fr, T('18 groupes purs sur 18 · 72 images sur 72', MONO, 34, '#C4CBE6'), x0 + ref + 54, y + 26, a2)
        else:
            blitc(fr, sb, W / 2 - 30, y - 16, a, pulse)
            a2 = eo3(u(t, t_tick + N * 0.055, 0.25))
            blitc(fr, T(s1, GROT, 42, '#FFFFFF'), W / 2 - 30, y + 66, a2)
    return fr


# ------------------------------------------------------------------ scène 5 : un prompt -> un studio -> des épisodes
def typed_count(t):
    total = sum(len(l) for l in PROMPT)
    return int(total * u(t, TYPE0, TYPE1 - TYPE0))


def scene_term(t, n):
    fr = dark_bg(t)
    g = F['term']
    fmt9 = F['fmt'] == '9x16'
    # --- titre
    hx, hy = F['th_xy']
    hs = F['th_size']
    if t < T_CHK[0]:
        parts = [('Un seul ', '#FFFFFF'), ('prompt.', YEL)]
        a = eo3(u(t, T_TERM + 0.1, 0.25))
    elif t < T_EP[0]:
        parts = [('Votre agent ', '#FFFFFF'), ('fait le reste.', YEL)]
        a = eo3(u(t, T_CHK[0], 0.25))
    else:
        e = 0 if t < T_EP[1] else 1 if t < T_EP[2] else 2
        parts = [('Épisode ', '#FFFFFF'), (f'{e + 1}', YEL), (' : rendu.', '#FFFFFF')]
        a = eo3(u(t, T_EP[e], 0.2))
    hs = fit(''.join(p_[0] for p_ in parts), DEMO, hs, g['w'])
    x = hx
    for txt, col in parts:
        s = T(txt, DEMO, hs, col)
        blit(fr, s, x, hy + 18 * (1 - a), a)
        x += font(DEMO, hs).getlength(txt)
    # --- terminal
    blit(fr, shadow(g['w'], g['h'], 22, 30, 200), g['x'] - 90, g['y'] - 90 + 34)
    blit(fr, rr(g['w'], g['h'], 22, '#10131F', '#2A3050', 2), g['x'], g['y'])
    blit(fr, rr(g['w'], 54, 22, '#1A1F33'), g['x'], g['y'])
    rect(fr, g['x'] + 2, g['y'] + 30, g['x'] + g['w'] - 2, g['y'] + 54, rgb('#1A1F33'))
    for k, c in enumerate(('#FF5F57', '#FEBC2E', '#28C840')):
        blit(fr, rr(16, 16, 8, c), g['x'] + 24 + k * 26, g['y'] + 19)
    blitc(fr, T('votre agent', MONO, 22, '#7C86A8'), g['x'] + g['w'] / 2, g['y'] + 27)
    tx, ty = g['x'] + 34, g['y'] + 78
    left = typed_count(t)
    fs, lh = g['fs'], g['lh']
    cur_xy = (tx + font(MONO, fs).getlength('> '), ty)
    for li, line in enumerate(PROMPT):
        if left <= 0:
            break
        txt = line[:left]
        left -= len(line)
        if li == 0 and txt:
            blit(fr, T('>', MONOB, fs, '#3CF2A0'), tx, ty)
            blit(fr, T(' ' + txt[1:], MONO, fs, '#E8ECFF'), tx, ty)
        else:
            blit(fr, T(txt, MONO, fs, '#E8ECFF'), tx, ty + li * lh)
        cur_xy = (tx + font(MONO, fs).getlength(txt), ty + li * lh)
    if t < T_CHK[0] and (t < TYPE1 or int(t * 3) % 2 == 0):
        rect(fr, cur_xy[0] + 8, cur_xy[1] + 6, cur_xy[0] + 8 + fs * 0.55, cur_xy[1] + fs * 1.25, rgb('#E8ECFF'))
    cy0 = ty + len(PROMPT) * lh + int(lh * 0.6)
    for k, (txt, tc) in enumerate(zip(CHECKS, T_CHECKS)):
        a = eo3(u(t, tc, 0.18))
        if a <= 0:
            continue
        yy = cy0 + k * lh
        blitc(fr, check_spr(int(fs * 0.95), '#3CF2A0'), tx + fs * 0.45, yy + fs * 0.78, a, back(u(t, tc, 0.2)))
        blit(fr, T(txt, MONO, fs, '#9BE8C4' if k < 3 else '#7FD1B0'), tx + fs * 1.3 - 10 * (1 - a), yy, a)
    # spinner : l'agent travaille
    if TYPE1 + 0.1 < t < T_EP[0]:
        nxt = next((k for k, tc in enumerate(T_CHECKS) if t < tc), None)
        if nxt is not None and nxt < 3:
            msg = ['compare les 18 identités…', 'bootstrap_studio.py…', 'rendu image par image…'][nxt]
            prev = T_CHECKS[nxt - 1] if nxt else TYPE1
            if t > prev + 0.2:
                yy = cy0 + nxt * lh
                sp = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
                dots = '.' * (1 + int(t * 6) % 3)
                blit(fr, T(msg, MONO, fs, '#6F7AA6'), tx + fs * 1.3, yy, 0.9)
                ang = t * 9
                blitc(fr, rr(10, 10, 5, '#6F7AA6'), tx + fs * 0.45 + 9 * math.cos(ang), yy + fs * 0.78 + 9 * math.sin(ang))
    # --- à droite : le menu des 18 styles, puis le téléphone
    mg = F['menu']
    px, py, pw_, ph_ = F['phone']
    sel = IDX['pixel-arcade']
    hop_seq = [3, 9, 1, 14, 6, 17, 11, 4, 12, 7, 15, 0, 10, 13]
    t_grow = T_CHK[1]
    gz = eio(u(t, t_grow, 0.55))
    if t < T_EP[0] + 0.3:
        for k in range(N):
            c, r = k % 6, k // 6
            x = mg['x'] + c * mg['pw']
            y = mg['y'] + r * mg['ph']
            a = eo3(u(t, T_TERM + 0.35 + 0.04 * k, 0.3))
            if a <= 0:
                continue
            fade = 1 - 0.75 * eo3(u(t, T_CHK[0], 0.3)) if k != sel else 1
            fade *= 1 - (eo3(u(t, t_grow, 0.4)) if k != sel else 0)
            if k == sel and gz > 0:
                continue
            spr = thumb('c_' + IDS[k][0], 60, mg['tw'], mg['th'], 10)
            blit(fr, spr, x, y + 14 * (1 - a), a * fade)
        # curseur de l'agent qui compare
        if T_TERM + 1.3 < t < t_grow:
            if t < T_CHK[0]:
                hi = int((t - (T_TERM + 1.3)) / 0.25)
                k = hop_seq[min(hi, len(hop_seq) - 1)]
                if hi >= len(hop_seq) - 1:
                    k = sel
                col = '#FFFFFF'
            else:
                k, col = sel, '#3CF2A0'
            c, r = k % 6, k // 6
            blit(fr, rr(mg['tw'] + 14, mg['th'] + 14, 14, None, col, 4), mg['x'] + c * mg['pw'] - 7, mg['y'] + r * mg['ph'] - 7)
            if t >= T_CHK[0]:
                lab = T('Arcade Pixel', ('rubik-mono-one', 400), 22, '#0B0D17')
                bx = mg['x'] + c * mg['pw'] + mg['tw'] / 2
                by = mg['y'] + r * mg['ph'] - 28
                blitc(fr, rr(lab.shape[1] + 24, 40, 10, '#3CF2A0'), bx, by, 1, back(u(t, T_CHK[0], 0.2)))
                blitc(fr, lab, bx, by, 1, back(u(t, T_CHK[0], 0.2)))
    # téléphone
    if gz > 0:
        c, r = sel % 6, sel // 6
        sx, sy = mg['x'] + c * mg['pw'], mg['y'] + r * mg['ph']
        x = sx + (px - sx) * gz
        y = sy + (py - sy) * gz
        w2 = int(mg['tw'] + (pw_ - mg['tw']) * gz)
        h2 = int(mg['th'] + (ph_ - mg['th']) * gz)
        if t < T_EP[0]:
            img = cframe('c_pixel-arcade', 60)
            # « rendu » : l'image se dévoile de haut en bas entre ✓ studio et ✓ épisode 1
            prog = u(t, T_CHK[1] + 0.7, T_CHK[2] - T_CHK[1] - 0.85)
            ep = cframe('e_0', 0)
            if prog > 0:
                img = img.copy()
                cut = int(img.shape[0] * prog)
                img[:cut] = ep[:cut]
                img[max(0, cut - 6):cut] = rgb('#3CF2A0')
            else:
                img = cv2.convertScaleAbs(img, alpha=1 - 0.55 * gz)
        else:
            e = 0 if t < T_EP[1] else 1 if t < T_EP[2] else 2
            te = t - T_EP[e]
            img = cframe(f'e_{e}', te * 30)
            sw = eo3(u(t, T_EP[e], 0.28))
            if e > 0 and sw < 1:   # balayage vertical, comme dans un fil de shorts
                prev = cframe(f'e_{e - 1}', 2.0 * 30 + te * 30)
                hh = img.shape[0]
                cut = int(hh * sw)
                img = np.vstack([prev[cut:], img[:cut]])
        img = cv2.resize(img, (w2, h2), interpolation=cv2.INTER_AREA)
        blit(fr, glow(int(h2 * 1.7), '#3CF2A0'), x + w2 / 2 - h2 * 0.85, y + h2 / 2 - h2 * 0.85, 0.22 * gz)
        blit(fr, shadow(w2 + 20, h2 + 20, 40, 26, 210), x - 10 - 78, y - 10 - 78 + 30, gz)
        blit(fr, rr(w2 + 20, h2 + 20, int(12 + 34 * gz), '#05060B', '#3A4266', 3), x - 10, y - 10)
        blit(fr, card_rgba(img, int(8 + 28 * gz)), x, y)
        if t >= T_CHK[1] + 0.6 and t < T_EP[0]:
            lab = 'rendu…'
            blitc(fr, T(lab, MONOB, 24, '#3CF2A0'), x + w2 / 2, y + h2 + 42)
        if t >= T_EP[0]:
            e = 0 if t < T_EP[1] else 1 if t < T_EP[2] else 2
            for k in range(3):
                on = k <= e
                bx = x + w2 / 2 + (k - 1) * 34
                blitc(fr, rr(22, 22, 11, '#3CF2A0' if on else '#2A3050'), bx, y + h2 + 44, 1, back(u(t, T_EP[k], 0.2)) if on else 1)
    return fr


# ------------------------------------------------------------------ scène 6 : les 4 panneaux puis la fin
def panel_img(k, t, pw, ph):
    ident, big, word = PANELS[k]
    r = IDS[IDX[ident]]
    horiz = F['fmt'] == '9x16'
    bg = rgb(r[6]) if ident != 'brut-meme' else rgb(YEL)
    ink = rgb(r[7]) if ident != 'brut-meme' else (17, 17, 17)
    acc = {'gazette-1900': '#B3261E', 'brut-meme': '#111111', 'pixel-arcade': '#3CF2A0', 'neon-lab': '#38F9FF'}[ident]
    im = np.empty((ph, pw, 3), np.uint8)
    im[:] = bg
    tp = t - (T_SLAM + k)
    fk = (r[4], r[5])
    inkh = '#%02x%02x%02x' % ink
    # carte inclinée qui joue le short
    cw, chh = (300, 533) if not horiz else (214, 380)
    ang = (-7, 6, -5, 7)[k]
    img = cframe('c_' + ident, pingpong(30 + tp * 30, clip_len('c_' + ident)))
    card = card_rgba(cv2.resize(img, (cw, chh), interpolation=cv2.INTER_AREA), 26, acc, 5)
    cx, cy = (pw / 2, ph * 0.72) if not horiz else (pw - 250, ph / 2 + (22 if k == 0 else 0))
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    hw, hh = cw / 2, chh / 2
    quad = [(cx + c * dx - s * dy, cy + s * dx + c * dy) for dx, dy in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]
    slide = (1 - eo3(u(tp, 0.1, 0.4))) * (220 if not horiz else 260)
    quad = [(x + (slide if horiz else 0), y + (0 if horiz else slide)) for x, y in quad]
    blitc(im, shadow(cw, chh, 26, 20, 110 if lum(bg) > 0.4 else 200), cx + (slide if horiz else 0), cy + 22 + (0 if horiz else slide))
    quad_blit(im, card, quad)
    # chiffre + mot, dans la police de l'identité
    bsz = {'gazette-1900': 250, 'brut-meme': 300, 'pixel-arcade': 190, 'neon-lab': 150}[ident]
    wsz = {'gazette-1900': 66, 'brut-meme': 78, 'pixel-arcade': 54, 'neon-lab': 60}[ident]
    if horiz:
        bsz, wsz = int(bsz * 0.78), int(wsz * 0.88)
    numc = {'gazette-1900': '#B3261E', 'brut-meme': '#111111', 'pixel-arcade': '#3CF2A0', 'neon-lab': '#38F9FF'}[ident]
    sb = Tt(big, fk, fit(big, fk, bsz, (pw - 70) if not horiz else 520), numc)
    sw = Tt(word.upper() if ident in ('brut-meme', 'pixel-arcade') else word, fk, fit(word, fk, wsz, (pw - 60) if not horiz else 500), inkh)
    pop = 1.5 - 0.5 * back(u(tp, 0.12, 0.22), 2.0)
    a = eo3(u(tp, 0.1, 0.15))
    aw = eo3(u(tp, 0.3, 0.2))
    if not horiz:
        ty = 230
        if ident == 'neon-lab':
            blitc(im, glow(700, '#38F9FF'), pw / 2, ty, 0.25)
        blitc(im, sb, pw / 2, ty, a, pop)
        blitc(im, sw, pw / 2, ty + sb.shape[0] / 2 + 64 + 14 * (1 - aw), aw)
    else:
        # 9:16 : le bandeau du haut et celui du bas restent dans la zone sûre
        tx = 72 + 250
        ty = {0: ph / 2 + 70, 1: ph / 2 - 30, 2: ph / 2 - 30, 3: ph / 2 - 120}[k]
        if ident == 'neon-lab':
            blitc(im, glow(700, '#38F9FF'), tx, ty, 0.25)
        blitc(im, sb, tx, ty, a, pop)
        blitc(im, sw, tx, ty + sb.shape[0] / 2 + 52 + 14 * (1 - aw), aw)
    return im


def scene_slam(t, n, base):
    fr = base
    horiz = F['fmt'] == '9x16'
    out = t - T_END
    for k in range(4):
        tp = t - (T_SLAM + k)
        if tp <= 0:
            continue
        pw, ph = (W // 4, H) if not horiz else (W, H // 4)
        e = eo3(u(tp, 0, 0.3))
        im = panel_img(k, t, pw, ph)
        sg = 1 if k % 2 == 0 else -1
        ex = eio(u(out, 0.06 * k, 0.4)) if out > 0 else 0
        if not horiz:
            y = int(sg * H * (1 - e) + (-sg) * H * ex)
            x = k * pw
        else:
            x = int(sg * W * (1 - e) + (-sg) * W * ex)
            y = k * ph
        x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + pw, W), min(y + ph, H)
        if x1 > x0 and y1 > y0:
            fr[y0:y1, x0:x1] = im[y0 - y:y1 - y, x0 - x:x1 - x]
            # filet de séparation
            if not horiz and k > 0:
                rect(fr, x0, y0, x0 + 4, y1, (10, 10, 16))
            if horiz and k > 0:
                rect(fr, x0, y0, x1, y0 + 4, (10, 10, 16))
    return fr


def scene_end(t, n):
    fr = dark_bg(t)
    fmt9 = F['fmt'] == '9x16'
    te = t - T_END
    # le titre caméléon : il change de police sur chaque temps, puis se pose
    seq = [('playfair-display', 900), ('rubik-mono-one', 400), ('fredoka', 700), ('anton', 400), ('space-mono', 700), DEMO]
    k = min(len(seq) - 1, int(max(0, te - 0.3) / 0.5))
    fk = seq[k]
    name = 'StudioVisualIdentity'
    base = 110 if not fmt9 else 60
    mul = {'anton': 1.45, 'playfair-display': 1.2, 'fredoka': 1.2, 'rubik-mono-one': 0.82, 'space-mono': 1.0}.get(fk[0], 1.0)
    size = fit(name, fk, base * mul, (W - 200) if not fmt9 else 860)
    y0 = 190 if not fmt9 else 420
    cx = W / 2 - (30 if fmt9 else 0)
    a = eo3(u(te, 0.25, 0.3))
    local = 1 + 0.06 * (1 - eo3(u(te, 0.3 + 0.5 * k, 0.15))) if k > 0 else 1
    blitc(fr, Tt(name, fk, size, '#FFFFFF'), cx, y0, a, local)
    a2 = eo3(u(te, 0.7, 0.3))
    if not fmt9:
        blitc(fr, T('18 identités · 21 déclinaisons · 45 shorts · open source', MONO, 36, '#C4CBE6'), cx, y0 + 118 + 12 * (1 - a2), a2)
    else:
        blitc(fr, T('18 identités · 21 déclinaisons', MONO, 30, '#AEB6D4'), cx, y0 + 90 + 12 * (1 - a2), a2)
        blitc(fr, T('45 shorts · open source', MONO, 30, '#AEB6D4'), cx, y0 + 134 + 12 * (1 - a2), a2)
    a3 = eo3(u(te, 1.1, 0.3))
    url = 'github.com/killerwolf/StudioVisualIdentity'
    us = 42 if not fmt9 else 29
    su = T(url, MONOB, us, '#0B0D17')
    uy = y0 + (232 if not fmt9 else 250)
    blitc(fr, rr(su.shape[1] + 56, su.shape[0] + 26, 16, YEL), cx, uy, a3, 0.9 + 0.1 * back(u(te, 1.1, 0.3)))
    blitc(fr, su, cx, uy, a3)
    a4 = eo3(u(te, 1.6, 0.3))
    cta = 'Donnez le prompt à votre agent.'
    blitc(fr, T(cta, GROT, 52 if not fmt9 else 40, '#FFFFFF'), cx, uy + (112 if not fmt9 else 110) + 12 * (1 - a4), a4)
    # pellicule des 18 identités
    tw, th, pitch = (168, 298, 186) if not fmt9 else (150, 267, 166)
    rows = 1 if not fmt9 else 2
    total = N * pitch
    for r in range(rows):
        yy = (712 if not fmt9 else 950 + r * 290)
        for kk in range(N):
            j = (kk + r * 9) % N
            x = (kk * pitch + (1 if r == 0 else -1) * 40 * te) % total - pitch
            a5 = eo3(u(te, 0.4 + 0.03 * kk, 0.4))
            spr = thumb('c_' + IDS[j][0], 60, tw, th, 14)
            for xx in (x, x - total, x + total):
                if -pitch < xx < W:
                    blit(fr, spr, xx, yy + 30 * (1 - a5), a5)
    # nuancier
    seg = W / N
    for kk in range(N):
        e = eo3(u(te, 0.2 + 0.02 * kk, 0.3))
        rect(fr, kk * seg, H - 26 * e, (kk + 1) * seg + 1, H, rgb(IDS[kk][6] if lum(rgb(IDS[kk][6])) > 0.12 else IDS[kk][8]))
    fo = u(t, DUR - 0.4, 0.4)
    if fo > 0:
        fr = cv2.convertScaleAbs(fr, alpha=1 - fo)
    return fr


# ------------------------------------------------------------------ montage
def push(a, b, x, vertical):
    """b pousse a (x de 0 à 1)."""
    x = eio(x)
    out = np.empty_like(a)
    if vertical:
        c = int(H * x)
        out[:H - c] = a[c:]
        out[H - c:] = b[:c]
    else:
        c = int(W * x)
        out[:, :W - c] = a[:, c:]
        out[:, W - c:] = b[:, :c]
    return out


def render(t, n=None):
    n = int(round(t * FPS)) if n is None else n
    if t < T_COV:
        fr = scene_hook(t, n)
    elif t < T_WALL:
        fr = scene_cover(t, n)
    elif t < T_JUDGE:
        fr = scene_wall(t, n)
        x = u(t, T_WALL, 0.2)
        if x < 1:   # le carrousel s'éloigne
            prev = scene_cover(T_WALL - 0.001, n)
            sc = 1 - 0.25 * eo3(x)
            sm = cv2.resize(prev, (int(W * sc), int(H * sc)), interpolation=cv2.INTER_AREA)
            ov = np.dstack([sm, np.full(sm.shape[:2], 255, np.uint8)])
            base = np.empty_like(fr)
            base[:] = rgb(DARK)
            blitc(base, ov, W / 2, H / 2, 1 - eo3(x))
            fr = np.maximum(fr, base) if False else cv2.addWeighted(base, 1 - eo3(x), fr, eo3(x), 0)
    elif t < T_TERM:
        fr = scene_judge(t, n)
        x = u(t, T_JUDGE, 0.35)
        if x < 1:
            fr = push(scene_wall(t, n), fr, x, False)
    elif t < T_SLAM:
        fr = scene_term(t, n)
        x = u(t, T_TERM, 0.35)
        if x < 1:
            fr = push(scene_judge(t, n), fr, x, True)
    elif t < T_END + 0.65:
        base = scene_term(t, n) if t < T_SLAM + 3.3 else np.zeros((H, W, 3), np.uint8)
        if t >= T_END:
            base = scene_end(t, n)
        fr = scene_slam(t, n, base)
    else:
        fr = scene_end(t, n)
    return finish(fr, n)


def video(fmt, t0=0.0, t1=DUR):
    setfmt(fmt)
    TMP.mkdir(parents=True, exist_ok=True)
    out = TMP / f'video_{fmt}.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(out)],
                         stdin=subprocess.PIPE)
    import time
    st = time.time()
    n0, n1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    for n in range(n0, n1):
        p.stdin.write(render(n / FPS, n).tobytes())
        if n % 60 == 0:
            print(f'{fmt} {n}/{n1} {time.time() - st:.0f}s', flush=True)
    p.stdin.close()
    p.wait()
    print(out)


def stills(fmt, times):
    setfmt(fmt)
    d = TMP / 'stills'
    d.mkdir(parents=True, exist_ok=True)
    for t in times:
        fr = render(float(t))
        Image.fromarray(fr).save(d / f'{fmt}_{float(t):06.2f}.jpg', quality=88)
    print(d)


def sheet(fmt, times, out, cols=None, tw=None):
    setfmt(fmt)
    tw = tw or (640 if fmt == '16x9' else 270)
    th = int(tw * H / W)
    cols = cols or (4 if fmt == '16x9' else 6)
    rows = math.ceil(len(times) / cols)
    im = Image.new('RGB', (cols * tw, rows * th), '#000000')
    for k, t in enumerate(times):
        fr = Image.fromarray(render(float(t))).resize((tw, th), Image.LANCZOS)
        ImageDraw.Draw(fr).text((8, 6), f'{float(t):.1f}s', fill='#ffffff', font=font(MONOB, 20), stroke_width=3, stroke_fill='#000000')
        im.paste(fr, ((k % cols) * tw, (k // cols) * th))
    im.save(out, quality=86)
    print(out)


if __name__ == '__main__':
    import build_audio  # noqa: E402  (même dossier)
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
    if cmd == 'clips':
        clips()
    elif cmd == 'stills':
        stills(sys.argv[2], sys.argv[3:])
    elif cmd == 'sheet':
        if len(sys.argv) > 2:
            sheet(sys.argv[2], sys.argv[4:], sys.argv[3])
        else:
            sheet('16x9', [0.9, 2.3, 3.2, 5.2, 8.2, 11.7, 15.6, 19.0, 21.6, 25.0, 27.6, 30.2, 34.2, 38.6, 41.5, 42.2][:12] and
                  [0.9, 3.2, 5.2, 8.2, 11.7, 15.6, 21.6, 25.0, 27.6, 32.2, 38.6, 41.8], HERE / 'planche-demo-fr.jpg')
    elif cmd == 'video':
        video(sys.argv[2], *(float(x) for x in sys.argv[3:5]))
    elif cmd == 'audio':
        build_audio.audio()
    elif cmd == 'final':
        build_audio.final(sys.argv[2])
    elif cmd == 'gif':
        build_audio.gif()
    elif cmd == 'thumb':
        build_audio.thumb()
    elif cmd == 'narration':
        build_audio.write_narration()
    elif cmd == 'all':
        clips()
        build_audio.write_narration()
        for f in ('16x9', '9x16'):
            video(f)
        build_audio.audio()
        for f in ('16x9', '9x16'):
            build_audio.final(f)
        build_audio.gif()
        build_audio.thumb()
        sheet('16x9', [0.9, 3.2, 5.2, 8.2, 11.7, 15.6, 21.6, 25.0, 27.6, 32.2, 38.6, 41.8], HERE / 'planche-demo-fr.jpg')
    else:
        print(__doc__)
