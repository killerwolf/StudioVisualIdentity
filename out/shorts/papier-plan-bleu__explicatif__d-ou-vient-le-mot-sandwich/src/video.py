"""D'où vient le mot sandwich ? — essai C4 de la composition : habillage « plan-bleu » (lyrics-chemin) × mécanique « pop-papier-12ips ».

Même épisode, même voix (Sulafat) et même code de scène que papier-decoupe__explicatif__d-ou-vient-le-mot-sandwich ; seuls changent
le thème (src/plan-bleu.json : couleurs, polices Barlow Condensed / JetBrains Mono lues dans node_modules/@fontsource) et le tapis :
une feuille de plan bleue quadrillée, pliée en six, avec le crayon jaune et la tasse de café de lyrics-chemin, dessinée par tapis_plan() ci-dessous qui remplace papier.tapis
pour ce short seulement (le moteur partagé out/shared/papier-moteur/ n'est pas modifié ; les tranches parallèles relancent ce fichier,
le remplacement s'applique donc aussi à elles). Reproduire : bash src/build.sh (depuis ce dossier ou la racine).
Commandes : video.py [video|images t…|chronologie|narration] (narration écrit ../narration.json).
"""
import json
import os
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
MOTEUR = SRC.parents[2] / "shared" / "papier-moteur"
os.environ["THEME_ESSAI"] = str(SRC / "plan-bleu.json")
sys.path.insert(0, str(MOTEUR / "pipeline"))
import numpy as np  # noqa: E402
import cv2  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402
import papier as P  # noqa: E402
import elements as E  # noqa: E402
from episode import Episode  # noqa: E402


def tapis_plan(W, H):
    """Feuille de plan bleue (habillage plan-bleu) : quadrillage clair, plis en 2 × 3 panneaux, grain ; crayon jaune et tasse de café."""
    a = np.empty((H, W, 3), np.float32)
    a[:] = P.MAT
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # panneaux du pliage : chacun un peu plus clair ou plus sombre, plis nets
    px, py = W / 2, (H / 3, 2 * H / 3)
    pan = (xx >= px).astype(np.int32) + 2 * ((yy >= py[0]).astype(np.int32) + (yy >= py[1]).astype(np.int32))
    a *= np.array([1.03, 0.98, 0.995, 1.025, 1.02, 0.975], np.float32)[pan][..., None]
    a *= (1 - 0.22 * (((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 2.2)[..., None]
    g = cv2.GaussianBlur(np.random.default_rng(7).normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.2)
    a *= (1 + 0.035 * g)[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    calque = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(calque)
    p = 54
    for x in range(-p // 2, W, p):
        fort = (x + p // 2) % (5 * p) == 0
        d.line([(x, 0), (x, H)], fill=(205, 222, 250, 46 if fort else 20), width=2 if fort else 1)
    for y in range(-p // 2, H, p):
        fort = (y + p // 2) % (5 * p) == 0
        d.line([(0, y), (W, y)], fill=(205, 222, 250, 46 if fort else 20), width=2 if fort else 1)
    # plis : un trait clair et un trait sombre côte à côte
    for x in (int(px),):
        d.line([(x - 1, 0), (x - 1, H)], fill=(235, 242, 255, 38), width=2)
        d.line([(x + 1, 0), (x + 1, H)], fill=(8, 22, 50, 46), width=2)
    for y in py:
        y = int(y)
        d.line([(0, y - 1), (W, y - 1)], fill=(235, 242, 255, 38), width=2)
        d.line([(0, y + 1), (W, y + 1)], fill=(8, 22, 50, 46), width=2)
    img.alpha_composite(calque)
    # objets du plan bleu (comme dans lyrics-chemin) : crayon jaune et tasse de café, en bas, hors des bandes et des sous-titres
    obj = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    o = ImageDraw.Draw(obj)
    cx, cy, r = 70, H - 170, 150                                   # tasse vue de dessus, coupée par le bord gauche
    o.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(236, 230, 214, 255))
    o.ellipse((cx - r + 22, cy - r + 22, cx + r - 22, cy + r - 22), fill=(92, 56, 34, 255))
    o.ellipse((cx - r + 40, cy - r + 40, cx + r - 40, cy + r - 40), fill=(108, 66, 40, 255))
    crayon = Image.new("RGBA", (560, 40), (0, 0, 0, 0))            # crayon : gomme rose, virole, corps jaune, bois, mine
    c = ImageDraw.Draw(crayon)
    c.rounded_rectangle((0, 4, 46, 36), 8, fill=(236, 140, 132, 255))
    c.rectangle((40, 3, 76, 37), fill=(190, 190, 186, 255))
    c.rectangle((76, 3, 470, 37), fill=(255, 210, 63, 255))
    c.rectangle((76, 3, 470, 13), fill=(255, 226, 120, 255))
    c.rectangle((76, 27, 470, 37), fill=(222, 176, 40, 255))
    c.polygon([(470, 3), (540, 20), (470, 37)], fill=(232, 196, 150, 255))
    c.polygon([(522, 15), (540, 20), (522, 25)], fill=(60, 60, 64, 255))
    crayon = crayon.rotate(14, expand=True, resample=Image.BICUBIC)
    obj.alpha_composite(crayon, (W - crayon.width + 40, H - 300))
    ombre = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ombre.putalpha(obj.getchannel("A").point(lambda v: v * 0.45).filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(10)))
    img.alpha_composite(ombre, (10, 12))
    img.alpha_composite(obj)
    return img


P.tapis = tapis_plan


def narration(ep, style):
    ep.calculer()
    lignes = [{"t": round(r.t0, 2), "maxDuration": round(r.duree + r.pause_apres, 2), "text": r.texte} for r in ep.repliques]
    (SRC.parent / "narration.json").write_text(json.dumps({
        "language": "fr", "style": style,
        "voiceUsed": {"provider": "Gemini", "name": "Sulafat", "model": "gemini-3.8-flash-tts",
                      "note": "une réplique par appel, silences de début et de fin rognés ; l'audio est mixé par le moteur papier, pas par tts.py"},
        "lines": lignes, "duration": ep.duree}, ensure_ascii=False, indent=1) + "\n")
    print("narration :", len(lignes), "lignes, durée", ep.duree)

ep = Episode("short", format="short", serie="D'OÙ ÇA VIENT ? · 01")
r0 = ep.replique("../voice_lines/00.mp3", "D'où vient le mot sandwich ?", pause_apres=0.4)
r1 = ep.replique("../voice_lines/01.mp3", "D'un aristocrate anglais : John Montagu, quatrième comte de Sandwich.", pause_apres=1.6)

s = ep.scene("accroche", 0)
s.pose(E.etiquette("D'OÙ ÇA VIENT ? · 01"), 540, 330, effet="aucun", son=None)
s.pose(E.bandes([("« Sandwich »", "jaune")], taille=92), 540, 600, effet="aucun", son=None)
s.pose(E.note("Ça vient d'où ?", "rose", w=300, h=230, taille=46), 760, 920, 0.5)

s = ep.scene("comte", r1.debut(-0.15))
s.pose(E.bandes([("« Sandwich »", "jaune")], taille=80), 540, 470, effet="aucun", son=None)
s.pose(E.carte("John Montagu", "4e comte de Sandwich", w=640, h=230, eyebrow="ANGLETERRE · XVIIIe SIÈCLE"), 540, 720, r1.debut(0.6))
s.pose(E.note("1re trace écrite du mot", "jaune", w=300, h=230, taille=40), 300, 1030, r1.fin(0.1))
s.pose(E.tampon("1762", "rouge", taille=90), 790, 1040, r1.fin(0.6))

if len(sys.argv) > 1 and sys.argv[1] == "narration":
    narration(ep, "vive et rythmée, comme une conteuse, chaleureuse")
else:
    ep.lancer()
