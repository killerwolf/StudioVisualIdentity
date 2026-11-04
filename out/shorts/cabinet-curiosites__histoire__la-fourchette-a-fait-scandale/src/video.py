"""La fourchette a fait scandale — short de preuve de l'identité « cabinet-curiosites » (moteur papier du gabarit, Python/Pillow/OpenCV).

Le thème (couleurs, polices, tapis) vient de src/THEME (vide = papier découpé d'origine) via THEME_ESSAI ;
le moteur partagé est out/shared/papier-moteur/ (pipeline/ + assets/). Reproduire : bash src/build.sh (depuis ce dossier ou la racine).
Commandes : video.py [video|images t…|chronologie|narration] (narration écrit ../narration.json).
"""
import json
import os
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
MOTEUR = SRC.parents[2] / "shared" / "papier-moteur"
THEME = (SRC / "THEME").read_text().strip() if (SRC / "THEME").exists() else ""
if THEME:
    os.environ["THEME_ESSAI"] = str(MOTEUR / "themes" / f"{THEME}.json")
sys.path.insert(0, str(MOTEUR / "pipeline"))
import elements as E  # noqa: E402
from episode import Episode  # noqa: E402


def narration(ep, style):
    ep.calculer()
    lignes = [{"t": round(r.t0, 2), "maxDuration": round(r.duree + r.pause_apres, 2), "text": r.texte} for r in ep.repliques]
    (SRC.parent / "narration.json").write_text(json.dumps({
        "language": "fr", "style": style,
        "voiceUsed": {"provider": "Gemini", "name": "Sulafat", "model": "gemini-3.8-flash-tts",
                      "note": "une réplique par appel, silences de début et de fin rognés ; l'audio est mixé par le moteur papier, pas par tts.py"},
        "lines": lignes, "duration": ep.duree}, ensure_ascii=False, indent=1) + "\n")
    print("narration :", len(lignes), "lignes, durée", ep.duree)

ep = Episode("short", format="short", serie="L'HISTOIRE DE… · 01")
r0 = ep.replique("../voice_lines/00.mp3", "La fourchette a fait scandale !", pause_apres=0.3)
r1 = ep.replique("../voice_lines/01.mp3", "An mille, à Venise : une princesse byzantine mange avec une fourchette d'or.", pause_apres=0.3)
r2 = ep.replique("../voice_lines/02.mp3", "Un moine s'indigne : quel luxe scandaleux !", pause_apres=0.3)
r3 = ep.replique("../voice_lines/03.mp3", "Il faudra des siècles pour qu'elle gagne nos tables.", pause_apres=0.3)
r4 = ep.replique("../voice_lines/04.mp3", "Et vous : les doigts ou la fourchette ?", pause_apres=0.3)

s = ep.scene("accroche", 0)
s.pose(E.etiquette("L'HISTOIRE DE… · 01"), 540, 330, effet="aucun", son=None)
s.pose(E.bandes([("La fourchette", "papier"), ("a fait", "bleu"), ("scandale", "rouge")], taille=86), 540, 700, effet="aucun", son=None)
s.pose(E.tampon("AN 1000", "rouge", taille=110), 760, 1080, 0.6)

s = ep.scene("venise", r1.debut(-0.15))
s.pose(E.etiquette("VENISE · AN 1000"), 540, 330, effet="aucun", son=None)
s.pose(E.carte("Venise", "une princesse venue de Byzance", w=560, h=240, eyebrow="AN 1000 ENVIRON"), 400, 640, r1.debut(0.1))
s.pose(E.note("Une fourchette d'or !", "jaune", w=300, h=240, taille=42), 800, 900, r1.debut(1.8))
s.pose(E.bande("2 dents", "rouge", taille=60), 360, 1020, r1.debut(3.0))

s = ep.scene("moine", r2.debut(-0.15))
s.pose(E.bandes([("Un moine", "papier"), ("s'indigne", "rouge")], taille=96), 540, 560, effet="aucun", son=None)
s.pose(E.carte("Pierre Damien", "moine italien, XIe siècle", w=600, h=220, eyebrow="LE TÉMOIN"), 540, 880, r2.debut(0.5))
s.pose(E.tampon("LUXE !", "rouge", taille=80), 800, 1080, r2.debut(1.6))

s = ep.scene("siecles", r3.debut(-0.15))
s.pose(E.bandes([("Des siècles", "papier"), ("plus tard…", "jaune")], taille=92), 540, 520, effet="aucun", son=None)
for i, (txt, coul) in enumerate([("2 dents", "rose"), ("3 dents", "cyan"), ("4 dents", "jaune")]):
    s.pose(E.note(txt, coul, w=260, h=200, taille=46, seed=10 + i, angle=(-3, 2, -2)[i]), 230 + i * 310, 900, r3.debut(0.4 + 0.5 * i))

s = ep.scene("vote", r4.debut(-0.15))
s.pose(E.bandes([("Et vous ?", "bleu")], taille=120), 540, 560, effet="aucun", son=None)
s.pose(E.note("Les doigts ?", "rose", w=300, h=230, taille=46), 320, 900, r4.debut(0.5))
s.pose(E.note("La fourchette ?", "jaune", w=300, h=230, taille=46, seed=7, angle=-3), 760, 920, r4.debut(1.1))

if len(sys.argv) > 1 and sys.argv[1] == "narration":
    narration(ep, "vive et rythmée, comme une crieuse de journaux, chaleureuse")
else:
    ep.lancer()
