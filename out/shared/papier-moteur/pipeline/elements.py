"""Éléments de la chaîne (STYLE_GUIDE.md § 2), prêts à poser par le moteur.

Chaque fonction renvoie un **groupe** : une liste de (pièce, dx, dy, angle) autour d'un point d'ancrage.
Le moteur pose le groupe en (x, y) et anime toutes ses pièces ensemble.
"""
import math
import zlib

from PIL import Image, ImageDraw, ImageFilter

import numpy as np

import chaine as C
import papier as P


def seul(piece, angle=0.0):
    return [(piece, 0, 0, angle)]


# ---------- logo ----------
def bouton(r=34):
    """Le bouton « marche / redémarrer » jaune, tracé à l'encre (pastille ronde avec ombre)."""
    w = 2 * r
    k = 3
    c = Image.new("RGBA", (w * k, w * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.ellipse((0, 0, w * k - 1, w * k - 1), fill=P.YELLOW)
    R = r * k
    m = int(R * 0.42)
    ep = int(R * 0.15)
    d.arc((m, m, w * k - m, w * k - m), start=-55, end=235, fill=P.INK, width=ep)
    d.line([(R, int(R * 0.30)), (R, int(R * 0.98))], fill=P.INK, width=ep)
    for y in (int(R * 0.30), int(R * 0.98)):
        e = int(R * 0.075)
        d.ellipse((R - e, y - e, R + e, y + e), fill=P.INK)
    c = c.resize((w, w), Image.LANCZOS)
    m0 = 40
    out = Image.new("RGBA", (w + 2 * m0, w + 2 * m0), (0, 0, 0, 0))
    ombre = Image.new("L", out.size, 0)
    ImageDraw.Draw(ombre).ellipse((m0 + 6, m0 + 10, m0 + w + 6, m0 + w + 10), fill=110)
    out.putalpha(ombre.filter(ImageFilter.GaussianBlur(7)))
    out.alpha_composite(c, (m0, m0))
    return seul((out, m0))


def logo_coin(r=34):
    """Petit logo en coin : le bouton + le nom de la chaîne (chaine.json)."""
    return bouton(r) + [(P.bande(C.NOM_COMPLET, taille=30, pad=(16, 10), seed=90), r + 118, 0, -1.4)]


def titre_chaine(taille=110):
    """Le nom de la chaîne en deux bandes (bleu puis papier, chaine.json), côte à côte, centrées sur l'ancrage.
    Nom d'un seul mot : une seule bande bleue."""
    pad = (int(taille * 0.27), int(taille * 0.16))
    ai = P.bande(C.NOM[0], taille=taille, fill=P.BLUE, ink=P.PAPER, pad=pad, seed=73)
    if not C.NOM[1]:
        return [(ai, 0, 0, -1.4)]
    rb = P.bande(C.NOM[1], taille=taille, pad=pad, seed=74)
    wa, wr = ai[0].width - 80, rb[0].width - 80
    x0 = -(wa + wr - 20) / 2
    return [(ai, x0 + wa / 2, -6, -1.4), (rb, x0 + wa - 20 + wr / 2, 8, 1.4)]


def slogan(taille=52):
    return seul(P.bande(C.SLOGAN, "hand", taille, P.PAPER, P.INK, (28, 8), 75), -0.6)


# ---------- textes ----------
def etiquette(texte, seed=91):
    """Étiquette de série ou d'œil : DM Mono sur bande encre (« PAPER EXPLAINS · 01 »)."""
    return seul(P.bande(texte, "mono", 28, P.INK, P.PAPER, (22, 14), seed), -1.4)


COULEURS = {"papier": (P.PAPER, P.INK), "bleu": (P.BLUE, P.PAPER), "jaune": (P.YELLOW, P.INK),
            "rouge": (P.RED, P.PAPER), "rose": (P.PINK, P.INK), "cyan": (P.CYAN, P.INK), "encre": (P.INK, P.PAPER)}


def bandes(lignes, taille=96, ecart=None, seed=94):
    """Titre en plusieurs bandes empilées, inclinées en alternance. lignes : [(texte, couleur)]."""
    ecart = ecart or int(taille * 1.65)
    n = len(lignes)
    out = []
    for i, (s, coul) in enumerate(lignes):
        fond, encre = COULEURS[coul]
        b = P.bande(s, taille=taille, fill=fond, ink=encre, seed=seed + i)
        out.append((b, (-1) ** i * 30, (i - (n - 1) / 2) * ecart, -1.4 if i % 2 == 0 else 1.4))
    return out


def bande(s, couleur="papier", taille=78, police="display", seed=95, angle=-1.4):
    fond, encre = COULEURS[couleur]
    pad = (30, 8) if police == "hand" else (36, 22)
    return seul(P.bande(s, police, taille, fond, encre, pad, seed), angle)


def note(s, couleur="jaune", w=300, h=220, taille=44, seed=5, angle=3.0):
    """Post-it."""
    return seul(P.sticky(s, COULEURS[couleur][0], w, h, taille, seed), angle)


def carte(titre, sous=None, w=440, h=200, couleur="papier", eyebrow=None, taille=46, seed=3, angle=-1.4):
    fond, encre = COULEURS[couleur]
    return seul(P.carte(titre, sous, w, h, fond, encre, seed, eyebrow, taille), angle)


def sous_titre(s, largeur=760, taille=54, etiquette_haut=None):
    """Sous-titre incrusté : Kalam, encre sur papier."""
    f = P.police("hand", taille)
    ls = P.lignes(s, f, largeur)
    pas = int(taille * 1.25)
    h = 36 + len(ls) * pas + (40 if etiquette_haut else 0)
    w = int(max(f.getlength(l) for l in ls)) + 70
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    y = 16
    if etiquette_haut:
        P.texte(d, (w // 2, y + 4), etiquette_haut, P.police("mono", 24), P.INK_SOFT, "ma")
        y += 40
    for l in ls:
        P.texte(d, (w // 2, y), l, f, P.INK, "ma")
        y += pas
    return seul(P.papier(w, h, P.PAPER, zlib.crc32(s.encode()) % 1000, 0.8, c))


# ---------- objets ----------
def ticket(lignes_ticket, total, legende="", largeur=560, seed=92, angle=-2.3):
    """Ticket de caisse (série Receipts). lignes_ticket : [(libellé, valeur)]. Chiffres vrais uniquement."""
    f, fb = P.police("mono-r", 30), P.police("mono", 34)
    h = 210 + 52 * len(lignes_ticket) + 200
    c = Image.new("RGBA", (largeur, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    P.texte(d, (largeur // 2, 46), f"{C.NOM_COMPLET.upper()} · RECEIPT", P.police("mono", 30), P.INK, "mm")
    if legende:
        P.texte(d, (largeur // 2, 92), legende, P.police("hand", 34), P.INK_SOFT, "mm")
    y = 150

    def tirets(y):
        for x in range(30, largeur - 30, 16):
            d.line([(x, y), (x + 8, y)], fill=P.INK, width=3)
    tirets(y)
    y += 30
    for nom, val in lignes_ticket:
        P.texte(d, (36, y), nom, f, P.INK)
        P.texte(d, (largeur - 36, y), val, f, P.INK, "ra")
        y += 52
    y += 6
    tirets(y)
    y += 26
    P.texte(d, (36, y), "TOTAL", fb, P.INK)
    P.texte(d, (largeur - 36, y), total, fb, P.RED, "ra")
    y += 78
    for i, x in enumerate(range(70, largeur - 70, 9)):
        d.rectangle((x, y, x + (2 if i % 3 else 5), y + 56), fill=P.INK)
    img, m = P.papier(largeur, h, P.WHITE, seed, contenu=c)
    dents = Image.new("L", img.size, 255)
    pts = [(m, m + h)] + [(m + x, m + h - (16 if k % 2 else 0)) for k, x in enumerate(range(0, largeur + 1, 24))]
    pts += [(m + largeur, m + h + 40), (m, m + h + 40)]
    ImageDraw.Draw(dents).polygon(pts, fill=0)
    img.putalpha(Image.fromarray(np.minimum(np.asarray(img.getchannel("A")), np.asarray(dents))))
    return seul((img, m), angle)


_avatars = {}
BOUCHE = C.BOUCHE                    # boîte de la bouche dans les images d'origine (505×700), à mesurer pour un nouvel avatar


def _image_avatar(nom):
    """assets/avatar/<nom>.png (505×700, voir assets/A_FOURNIR.md) ; sans fichier, une silhouette en papier."""
    f = P.RACINE / "assets/avatar" / f"{nom}.png"
    if f.exists():
        return Image.open(f).convert("RGBA")
    im = Image.new("RGBA", (505, 700), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((60, 400, 445, 1000), fill=P.INK_SOFT)                # le buste, coupé par le bas de l'image
    d.ellipse((130, 90, 375, 380), fill=P.KRAFT)                    # la tête
    x0, x1, y0, _ = BOUCHE
    d.rounded_rectangle((x0 - 28, y0 + 10, x1 + 28, y0 + 22), 6, fill=P.INK)   # la bouche au repos
    for x in (205, 300):
        d.ellipse((x - 12, 200, x + 12, 224), fill=P.INK)           # les yeux
    if "salut" in nom:
        d.line([(420, 520), (480, 280)], fill=P.INK_SOFT, width=52)  # le bras qui salue
    return im


def avatar(nom=None, hauteur=520):
    """L'avatar récurrent de la chaîne (chaine.json : avatar, avatar_salut)."""
    nom = nom or C.AVATAR
    k = (nom, hauteur)
    if k not in _avatars:
        im = _image_avatar(nom)
        _avatars[k] = (im.resize((int(im.width * hauteur / im.height), hauteur), Image.LANCZOS), 0)
    return seul(_avatars[k])


def avatars_parlants(nom=None, hauteur=520):
    """L'avatar avec la bouche plus ou moins ouverte : liste de 4 groupes (niveau de voix 0 à 3).
    À passer à `pose(..., bouches=…, parle=réplique)` : le moteur choisit l'image au rythme de la voix."""
    nom = nom or C.AVATAR
    im0 = _image_avatar(nom)
    x0, x1, y0, y1 = BOUCHE
    out = [avatar(nom, hauteur)]
    for n in (1, 2, 3):
        im = im0.copy()
        d = ImageDraw.Draw(im)
        cx, w, h = (x0 + x1) / 2, (x1 - x0) * (0.80 + 0.06 * n), 8 + 9 * n
        haut = y0 + 2
        d.ellipse((cx - w / 2, haut, cx + w / 2, haut + h), fill=(92, 28, 30, 255))
        d.chord((cx - w / 2 + 6, haut, cx + w / 2 - 6, haut + h * 0.7), 180, 360, fill=(250, 248, 240, 255))
        d.ellipse((cx - w / 4, haut + h * 0.55, cx + w / 4, haut + h - 1), fill=(200, 84, 84, 255))
        out.append(seul((im.resize((int(im.width * hauteur / im.height), hauteur), Image.LANCZOS), 0)))
    return out


def lien(a, b, couleur=P.PAPER, largeur=5, pas=16):
    """Trait en pointillés entre deux points (coordonnées relatives à l'ancrage)."""
    (x0, y0), (x1, y1) = a, b
    gx, gy = min(x0, x1) - 10, min(y0, y1) - 10
    w, h = int(abs(x1 - x0)) + 20, int(abs(y1 - y0)) + 20
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    n = max(1, int(math.hypot(x1 - x0, y1 - y0) / pas))
    for k in range(0, n, 2):
        p = (x0 - gx + (x1 - x0) * k / n, y0 - gy + (y1 - y0) * k / n)
        q = (x0 - gx + (x1 - x0) * (k + 1) / n, y0 - gy + (y1 - y0) * (k + 1) / n)
        d.line([p, q], fill=couleur, width=largeur)
    return [((c, 0), gx + w / 2, gy + h / 2, 0.0)]


def boucle_agent(ecart=270, echelle=1.0):
    """Le cycle d'un agent : THINK → ACT → CHECK, reliés en pointillés."""
    pos = [(-ecart, 0), (0, -int(ecart * 0.62)), (ecart, 0)]
    out = []
    for a, b in ((pos[0], pos[1]), (pos[1], pos[2]), (pos[2], pos[0])):
        out += lien(a, b)
    for (x, y), (mot, sous, coul), ang in zip(pos, [("Think", "plans the step", "papier"), ("Act", "use a tool", "jaune"),
                                                   ("Check", "did it work?", "cyan")], (-1.4, 1.4, -0.6)):
        out += [(p, x, y, ang) for p, _, _, _ in carte(mot, sous, int(300 * echelle), int(170 * echelle), coul,
                                                       taille=int(46 * echelle), seed=zlib.crc32(mot.encode()) % 50)]
    return out


# ---------- ressources externes (STYLE_GUIDE.md § 2.1) ----------
def _scotch(img, x, y, angle, w=120, h=38):
    """Un morceau de scotch translucide collé sur une image."""
    s = Image.new("RGBA", (w, h), P.PAPER + (150,))
    s = s.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(s, (int(x - s.width / 2), int(y - s.height / 2)))


def _ouvrir(chemin, largeur, recadre=None):
    im = Image.open(P.RACINE / chemin if not str(chemin).startswith("/") else chemin).convert("RGB")
    if recadre:
        x, y, w, h = recadre
        im = im.crop((x, y, x + w, y + h))
    return im.resize((largeur, int(im.height * largeur / im.width)), Image.LANCZOS)


def legende(s, seed=96):
    """Petite légende de source sous une image : DM Mono sur bande papier (« SOURCE · OPENAI.COM »)."""
    return P.bande(s.upper(), "mono", 22, P.PAPER, P.INK_SOFT, (16, 8), seed)


def image(chemin, largeur=760, recadre=None, source=None, scotch=True, angle=-1.4, seed=97):
    """Image, photo ou capture d'écran posée sur le tapis : bord papier, ombre, scotch en haut,
    légende de source en dessous (`source`, ex. « openai.com » ou « Wikimedia Commons »).
    recadre = (x, y, l, h) en pixels de l'image d'origine (ex. pour isoler un détail d'une capture)."""
    im = _ouvrir(chemin, largeur, recadre)
    out, m = P.cadre(im, 12)
    if scotch:
        _scotch(out, m + 70, m + 6, -8 + seed % 5)
        _scotch(out, out.width - m - 70, m + 6, 7 - seed % 4)
    groupe = [((out, m), 0, 0, angle)]
    if source:
        groupe.append((legende(source, seed), largeur / 2 - 120, im.height / 2 + 34, angle + 1.0))
    return groupe


def portrait(chemin=None, nom="", hauteur=360, recadre=None, couleur="papier", seed=98, angle=1.4, parodie=False):
    """Une personne qui parle : sa photo découpée (ou, sans photo libre, une silhouette en papier),
    avec son nom en dessous (DM Mono sur bande encre). Se pose avec `pose(..., parle=réplique)`.
    parodie=True : ajoute un tampon rose « PARODY » sur le coin (répliques inventées, STYLE_GUIDE.md § 2.1)."""
    if chemin:
        im = Image.open(P.RACINE / chemin if not str(chemin).startswith("/") else chemin).convert("RGB")
        if recadre:
            x, y, w, h = recadre
            im = im.crop((x, y, x + w, y + h))
        im = im.resize((int(im.width * hauteur / im.height), hauteur), Image.LANCZOS)
        piece = P.cadre(im, 12)
    else:
        w = int(hauteur * 0.8)
        c = Image.new("RGBA", (w, hauteur), (0, 0, 0, 0))
        d = ImageDraw.Draw(c)
        tete = int(hauteur * 0.21)
        d.ellipse((w / 2 - tete, hauteur * 0.16, w / 2 + tete, hauteur * 0.16 + 2 * tete), fill=P.INK_SOFT)
        d.ellipse((w / 2 - w * 0.42, hauteur * 0.66, w / 2 + w * 0.42, hauteur * 1.3), fill=P.INK_SOFT)
        piece = P.papier(w, hauteur, COULEURS[couleur][0], seed, contenu=c)
    groupe = [(piece, 0, 0, angle)]
    if nom:
        b = P.bande(nom.upper(), "mono", 28, P.INK, P.PAPER, (20, 12), seed + 1)
        groupe.append((b, 0, hauteur / 2 + 20, -angle))
    if parodie:
        t = P.bande("PARODY", "display", 34, P.PINK, P.INK, (22, 12), seed + 2)
        groupe.append((t, hauteur * 0.32, -hauteur / 2 + 10, -9.0))
    return groupe


def citation(texte, auteur, source, largeur=760, taille=48, couleur="papier", seed=99, angle=-0.6):
    """Une vraie citation, mot pour mot, entre guillemets, avec qui l'a dite et où
    (ex. source = « blog post · 2023 »). Seulement des citations vérifiées (Recherche)."""
    fond, encre = COULEURS[couleur]
    f = P.police("hand", taille)
    ls = P.lignes(f"“{texte}”", f, largeur - 80)
    pas = int(taille * 1.25)
    h = 60 + len(ls) * pas + 70
    c = Image.new("RGBA", (largeur, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    y = 34
    for l in ls:
        P.texte(d, (40, y), l, f, encre)
        y += pas
    P.texte(d, (largeur - 40, y + 18), f"— {auteur} · {source}".upper(), P.police("mono", 24),
            encre if fond != P.PAPER else P.INK_SOFT, "ra")
    return seul(P.papier(largeur, h, fond, seed, contenu=c), angle)


def emplacements_fin_long():
    """Écran de fin d'une vidéo longue : 2 emplacements vidéo et le rond d'abonnement, laissés vides pour YouTube."""
    c = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    for x0 in (120, 760):
        x1, y0, y1 = x0 + 560, 330, 645
        for x in range(x0, x1, 22):
            d.line([(x, y0), (x + 11, y0)], fill=P.PAPER, width=4)
            d.line([(x, y1), (x + 11, y1)], fill=P.PAPER, width=4)
        for y in range(y0, y1, 22):
            d.line([(x0, y), (x0, y + 11)], fill=P.PAPER, width=4)
            d.line([(x1, y), (x1, y + 11)], fill=P.PAPER, width=4)
    cx, cy, r = 1560, 470, 150
    for k in range(0, 360, 12):
        a0, a1 = math.radians(k), math.radians(k + 6)
        d.line([(cx + r * math.cos(a0), cy + r * math.sin(a0)), (cx + r * math.cos(a1), cy + r * math.sin(a1))],
               fill=P.PAPER, width=4)
    return [((c, 0), 0, 0, 0.0)]


# ---------- rythme calme (vidéos longues) ----------
def feuille(w=760, h=560, titre=None, couleur="papier", seed=88, angle=-0.6):
    """Grande feuille de papier posée une fois ; on y écrit ensuite des lignes (`ligne`). Titre en DM Mono."""
    fond, encre = COULEURS[couleur]
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if titre:
        d = ImageDraw.Draw(c)
        P.texte(d, (44, 36), titre.upper(), P.police("mono", 26), encre if fond != P.PAPER else P.INK_SOFT)
        d.line([(44, 82), (w - 44, 82)], fill=(*P.INK_SOFT, 90), width=2)
    return seul(P.papier(w, h, fond, seed, contenu=c), angle)


def ligne(s, taille=50, puce=None, couleur="encre", largeur=None, police="hand"):
    """Une ligne écrite à l'encre, sans papier (à poser sur une `feuille`), alignée à gauche sur l'ancrage.
    puce : « 1 », « ✓ », « – »… (en DM Mono). couleur : encre | bleu | rouge (un seul mot fort par feuille)."""
    f = P.police(police, taille)
    ink = {"encre": P.INK, "bleu": P.BLUE, "rouge": P.RED, "doux": P.INK_SOFT}[couleur]
    fp = P.police("mono", int(taille * 0.62))
    dx = int(taille * 1.1) if puce else 0
    ls = P.lignes(s, f, largeur - dx) if largeur else [s]
    w = dx + int(max(f.getlength(l) for l in ls)) + 8
    pas = int(taille * 1.25)
    h = pas * len(ls) + 10
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    if puce:
        P.texte(d, (0, int(taille * 0.42)), puce, fp, P.INK_SOFT)
    for i, l in enumerate(ls):
        P.texte(d, (dx, i * pas), l, f, ink)
    return [((c, 0), w / 2, h / 2, 0.0)]


def telephone(chemin, hauteur=820, angle=-1.0):
    """Un iPhone dessiné (coque noire, îlot, ombre) autour d'une capture d'écran mobile (rapport ≈ 9:19,5)."""
    ecran = Image.open(chemin).convert("RGB")
    k = 3                                                       # dessin en grand puis réduit (bords lisses)
    sh = hauteur * k
    bord = int(sh * 0.028)
    sw = int(sh * ecran.width / ecran.height)
    w, h = sw + 2 * bord, sh + 2 * bord
    corps = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(corps)
    r = int(w * 0.16)
    d.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=(28, 28, 30, 255))
    d.rounded_rectangle((4 * k, 4 * k, w - 1 - 4 * k, h - 1 - 4 * k), r - 4 * k, outline=(70, 70, 74, 255), width=2 * k)
    masque = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(masque).rounded_rectangle((0, 0, sw - 1, sh - 1), r - bord, fill=255)
    corps.paste(ecran.resize((sw, sh), Image.LANCZOS), (bord, bord), masque)
    il = int(sw * 0.30)
    d.rounded_rectangle((w / 2 - il / 2, bord + sh * 0.012, w / 2 + il / 2, bord + sh * 0.012 + sw * 0.085), sw, fill=(0, 0, 0, 255))
    for y0, y1 in ((0.20, 0.25), (0.29, 0.36), (0.38, 0.45)):    # boutons sur la tranche
        d.rectangle((0, h * y0, 3 * k, h * y1), fill=(50, 50, 54, 255))
    corps = corps.resize((w // k, h // k), Image.LANCZOS)
    m0 = 40
    out = Image.new("RGBA", (corps.width + 2 * m0, corps.height + 2 * m0), (0, 0, 0, 0))
    ombre = Image.new("L", out.size, 0)
    ombre.paste(corps.getchannel("A").point(lambda v: int(v * 0.45)), (m0 + 10, m0 + 16))
    out.putalpha(ombre.filter(ImageFilter.GaussianBlur(12)))
    out.alpha_composite(corps, (m0, m0))
    return seul((out, m0), angle)


_logos = {}


def logo(cle, variante="icone", hauteur=110, papier=True, angle=-1.0, seed=60, teinte=None):
    """Logo de la librairie (assets/logos, outil pipeline/logos.py) : « emoji/robot »… Les logos de marques ont été retirés du dépôt public (2026-11-22) : à ajouter soi-même avec pipeline/logos.py, sous sa propre responsabilité (droit des marques).
    variante : icone | icone-noire | icone-blanche | icone-couleur | nom. papier=True : posé sur un autocollant de papier
    (style du tapis) ; un emoji se pose plutôt sans papier. teinte : nouvelle couleur (degrés, 0 = rouge, 120 = vert,
    210 = bleu) de la couleur bleue dominante, ex. un 🤖 d'une couleur différente par agent ; jamais sur un logo de marque."""
    chemin = P.RACINE / "assets/logos" / (f"{cle}.png" if "/" in cle else f"{cle}/{variante}.png")
    k = (chemin, hauteur, teinte)
    if k not in _logos:
        im = Image.open(chemin).convert("RGBA")
        if teinte is not None and teinte is not False:
            # la couleur dominante (le bleu du 🤖) prend la teinte voulue ; le reste (yeux, contours) ne bouge pas
            hsv = np.array(im.convert("RGB").convert("HSV")).astype(np.int32)
            bleu = (hsv[..., 0] > 125) & (hsv[..., 0] < 175) & (hsv[..., 1] > 60)
            hsv[..., 0] = np.where(bleu, int(teinte * 255 / 360) % 256, hsv[..., 0])
            hsv[..., 1] = np.where(bleu, np.maximum(hsv[..., 1], 170), hsv[..., 1])
            rgb = Image.fromarray(hsv.astype(np.uint8), "HSV").convert("RGB").convert("RGBA")
            rgb.putalpha(im.getchannel("A"))
            im = rgb
        _logos[k] = im.resize((max(1, int(im.width * hauteur / im.height)), hauteur), Image.LANCZOS)
    im = _logos[k]
    if not papier:
        m0 = 40
        out = Image.new("RGBA", (im.width + 2 * m0, im.height + 2 * m0), (0, 0, 0, 0))
        ombre = Image.new("L", out.size, 0)
        ombre.paste(im.getchannel("A").point(lambda v: int(v * 0.35)), (m0 + 6, m0 + 9))
        out.putalpha(ombre.filter(ImageFilter.GaussianBlur(6)))
        out.alpha_composite(im, (m0, m0))
        return seul((out, m0), angle)
    pad = int(hauteur * 0.32)
    w, h = im.width + 2 * pad, im.height + 2 * pad
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    c.alpha_composite(im, (pad, pad))
    return seul(P.papier(w, h, P.WHITE, seed, contenu=c), angle)


# ---------- correction au stylo rouge, fiches, tampons (Shorts plus visuels) ----------
_ENCRES = {"rouge": P.RED, "bleu": P.BLUE, "encre": P.INK, "vert": (38, 150, 90)}


def entoure(w, h, couleur="rouge", epaisseur=9, seed=1):
    """Un rond tracé à la main au feutre (sans papier), à poser sur une feuille autour d'un mot ou d'une ligne.
    Le trait fait un tour et un peu plus, en spirale légère, comme un vrai coup de stylo."""
    r = np.random.default_rng(seed)
    k, m = 3, 30
    c = Image.new("RGBA", ((w + 2 * m) * k, (h + 2 * m) * k), (0, 0, 0, 0))
    cx, cy = c.width / 2, c.height / 2
    a0, n = r.uniform(0, 2 * math.pi), 120
    pts = []
    for i in range(int(n * 1.12)):
        t = a0 + 2 * math.pi * i / n
        rr = 0.94 + 0.10 * i / n + 0.03 * math.sin(3 * t + seed)
        pts.append((cx + w / 2 * k * rr * math.cos(t), cy + h / 2 * k * rr * math.sin(t)))
    ImageDraw.Draw(c).line(pts, fill=_ENCRES[couleur] + (235,), width=epaisseur * k, joint="curve")
    return [((c.resize((w + 2 * m, h + 2 * m), Image.LANCZOS), 0), 0, 0, 0.0)]


def barre(w, couleur="rouge", epaisseur=8, seed=2):
    """Un trait de feutre (pour barrer ou souligner), légèrement ondulé."""
    r = np.random.default_rng(seed)
    k, m = 3, 20
    c = Image.new("RGBA", ((w + 2 * m) * k, (2 * m + epaisseur) * k), (0, 0, 0, 0))
    y0 = c.height / 2
    pts = [(m * k + w * k * i / 30, y0 + r.normal(0, 1.2) * k + 3 * k * math.sin(i / 5 + seed)) for i in range(31)]
    ImageDraw.Draw(c).line(pts, fill=_ENCRES[couleur] + (235,), width=epaisseur * k, joint="curve")
    return [((c.resize((c.width // k, c.height // k), Image.LANCZOS), 0), 0, 0, 0.0)]


def brouillon(w=480, h=560, titre="DRAFT v1", premiere=None, n=8, seed=40, angle=-1.0):
    """Une page de brouillon : titre en DM Mono, une 1re ligne écrite (facultative, Kalam), puis des lignes grises
    de texte figuré. Lignes repérables : la ligne i est à dy = brouillon_y(h, i) du centre (pour y poser `entoure`)."""
    r = np.random.default_rng(seed)
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    if titre:
        P.texte(d, (40, 34), titre.upper(), P.police("mono", 26), P.INK_SOFT)
        d.line([(40, 78), (w - 40, 78)], fill=(*P.INK_SOFT, 90), width=2)
    for i in range(n):
        y = brouillon_y(h, i) + h / 2
        if i == 0 and premiere:
            P.texte(d, (40, y - 26), premiere, P.police("hand", 38), P.INK)
            continue
        long = (w - 80) * (0.55 if i == n - 1 else r.uniform(0.72, 1.0))
        x = 40
        while x < 40 + long - 20:                               # des « mots » gris de longueurs variées
            lm = min(r.uniform(40, 120), 40 + long - x)
            d.rounded_rectangle((x, y - 7, x + lm, y + 7), 7, fill=(*P.MUTED, 255))
            x += lm + 16
    return seul(P.papier(w, h, P.WHITE, seed, contenu=c), angle)


def brouillon_y(h, i):
    """Position verticale (depuis le centre du brouillon) de sa ligne i."""
    return -h / 2 + 128 + i * 54


def tampon(s, couleur="rouge", taille=70, angle=-8.0, seed=3):
    """Un coup de tampon : cadre arrondi et mots en display, encre un peu passée (pas de papier)."""
    f = P.police("display", taille)
    s = s.upper()
    x0, y0, x1, y1 = f.getbbox(s)
    pad, ep = int(taille * 0.35), max(5, taille // 11)
    w, h = (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad
    c = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    ink = _ENCRES[couleur]
    d.rounded_rectangle((10, 10, w + 10, h + 10), int(taille * 0.25), outline=ink, width=ep)
    P.texte(d, (w / 2 + 10, h / 2 + 10), s, f, ink, "mm")
    a = np.array(c.getchannel("A")).astype(np.float32)
    trous = np.random.default_rng(seed).random(a.shape) < 0.10       # encre qui n'a pas pris partout
    a[trous] *= 0.25
    c.putalpha(Image.fromarray((a * 0.92).astype(np.uint8)))
    return [((c, 0), 0, 0, angle)]


def fiche(eyebrow, titre, lignes=(), citation=None, w=620, logo_cle=None, seed=70, angle=-1.0):
    """Une fiche comme dans le studio (une page Notion reconstituée avec ses vraies valeurs, jamais inventées) :
    logo de l'outil + eyebrow en DM Mono, titre, propriétés en pastilles [(propriété, valeur, couleur)],
    et une citation facultative (vraie remarque, mot pour mot ou traduite fidèlement) avec un trait rouge à gauche."""
    fp, ft, fv, fc = P.police("mono", 24), P.police("display", 34), P.police("mono", 26), P.police("hand", 36)
    lt = P.lignes(titre.upper(), ft, w - 80)
    lc = P.lignes(citation, fc, w - 110) if citation else []
    h = 40 + 58 + len(lt) * 46 + 18 + len(lignes) * 56 + (24 + len(lc) * 44 if lc else 0) + 34
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    y = 34
    if logo_cle:
        ic = Image.open(P.RACINE / "assets/logos" / logo_cle / "icone.png").convert("RGBA")
        ic = ic.resize((int(ic.width * 44 / ic.height), 44), Image.LANCZOS)
        c.alpha_composite(ic, (40, y))
    P.texte(d, (40 + (60 if logo_cle else 0), y + 10), eyebrow.upper(), fp, P.INK_SOFT)
    y += 64
    for l in lt:
        P.texte(d, (40, y), l, ft, P.INK)
        y += 46
    y += 18
    pastilles = {"rouge": (P.RED, P.PAPER), "vert": ((38, 150, 90), P.PAPER), "jaune": (P.YELLOW, P.INK),
                 "gris": (P.MUTED, P.INK), "bleu": (P.BLUE, P.PAPER), "rose": (P.PINK, P.INK)}
    for prop, val, coul in lignes:
        P.texte(d, (40, y + 8), prop, fp, P.INK_SOFT)
        fond, ink = pastilles[coul]
        lv = fv.getlength(val)
        x = 250
        d.rounded_rectangle((x, y, x + lv + 30, y + 42), 10, fill=fond)
        P.texte(d, (x + 15, y + 6), val, fv, ink)
        y += 56
    if lc:
        y += 14
        d.rectangle((40, y, 48, y + len(lc) * 44), fill=P.RED)
        for l in lc:
            P.texte(d, (68, y - 2), l, fc, P.INK)
            y += 44
    return seul(P.papier(w, h, P.WHITE, seed, contenu=c), angle)
