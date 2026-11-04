"""D'où vient le mot sandwich ? — short de preuve de l'identité « papier-decoupe » (moteur papier du gabarit, Python/Pillow/OpenCV).

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
