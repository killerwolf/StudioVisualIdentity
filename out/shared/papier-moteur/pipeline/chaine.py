"""Ce qui est propre à la chaîne dans le moteur : lit chaine.json à la racine du studio.

Tant qu'un champ contient encore {{…}} (gabarit pas encore instancié), on prend un texte neutre :
le moteur reste utilisable pour un essai, sans rien inventer sur la chaîne.
"""
import json
import os
import shutil
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
_d = json.loads((RACINE / "chaine.json").read_text(encoding="utf-8"))


def _val(cle, defaut):
    v = _d.get(cle, defaut)
    return defaut if isinstance(v, str) and "{{" in v else v


NOM = (_val("nom_1", "Ma"), _val("nom_2", "Chaîne"))
NOM_COMPLET = " ".join(m for m in NOM if m)
SLOGAN = _val("slogan", "Votre slogan ici.")
FIN_SHORT = _val("fin_short", "À bientôt !")
FIN_LONG = _val("fin_long", "À suivre")
AVATAR = _val("avatar", "avatar")
AVATAR_SALUT = _val("avatar_salut", "avatar-salut")
BOUCHE = tuple(_d.get("bouche", (214, 291, 268, 287)))    # boîte de la bouche dans une image d'avatar de 505×700
SITE = _val("site", "")
THEMES = [t for t in _d.get("themes", []) if "{{" not in t]


def chrome():
    """La commande du navigateur sans écran (captures, logos SVG) : variable CHROME, sinon le premier trouvé.
    Sous root (session cloud), Chrome refuse de démarrer sans --no-sandbox."""
    noms = (os.environ.get("CHROME"), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome")
    for nom in noms:
        if nom and shutil.which(nom):
            return [shutil.which(nom)] + (["--no-sandbox"] if hasattr(os, "geteuid") and os.geteuid() == 0 else [])
    raise SystemExit("Chrome introuvable : indiquer son chemin dans la variable CHROME (hors-git/DU_MAC_AU_CLOUD.md).")


def user_agent(usage):
    """Identité envoyée aux sites interrogés (Wikimedia demande un contact)."""
    contact = f"; {SITE}" if SITE else ""
    return f"{NOM_COMPLET.replace(' ', '')}-studio/1.0 ({usage}{contact})"
