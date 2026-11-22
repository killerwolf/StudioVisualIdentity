#!/usr/bin/env python3
"""
paris.py — passe dédiée à Paris (décision 49) : la tour dans son quartier, en fin de journée. Ce n'est PAS un short de preuve.

Plan INVENTÉ et seulement évocateur, généré par code (aucune carte, image ni donnée ; les photos de référence, hors dépôt,
n'ont servi qu'à régler proportions et couleurs). Échelle : 1 unité ≈ 4 m, deux fois plus grosse que `../villes/`.

Ce qui est dessiné :
  - immeubles haussmanniens : façade crème à travées, corniche, BRISIS sombre à lucarnes côté rue, terrasson de zinc clair,
    souches de cheminées sur les mitoyens avec leurs pots, cours en puits, angles coupés ;
  - soleil bas (fin de journée) : faces ouest et sud chaudes, longues ombres bleu-gris, jamais noires ;
  - le Champ-de-Mars (pelouses en bandes, allées, alignements), les avenues plantées, l'école à dôme, la tour en treillis
    (hauteur / base ≈ 2,65, grande arche, fût effilé), la Seine avec quais bas et hauts, ponts, péniches, les jardins d'en face.

Moteur : celui de `../maquette-source/maquette.py`, par `moteur_ville.py` (copie du générateur de `../villes/`, qui reste
inchangé) : palette indexée, carte peinte tramée, vote majoritaire.

USAGE (depuis ce dossier)
  ../.venv/bin/python paris.py --out sortie/tour1/paris.mp4 --stills 0.5,2.5,4.5 --json sortie/tour1/mesures.json
"""
import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import moteur_ville as V  # noqa: E402  (copie de ../villes/villes.py avec deux options : ombre réglable, toits mansardés)

mq = V.mq
pk, F_MAP = V.pk, V.F_MAP
WX, WY, K, NX, NY = V.WX, V.WY, V.K, V.NX, V.NY
NW, NH, SCALE, FPS, DUR = V.NW, V.NH, V.SCALE, V.FPS, 5.0

# soleil de fin de journée : bas, à l'ouest-sud-ouest ; brume et ciel chauds
# Le soleil est derrière la caméra, dans l'axe du Champ-de-Mars (dans le monde réel cet axe pointe au sud-est : c'est la
# direction de l'ombre au couchant d'été). L'ombre de la tour s'allonge donc sur toute la longueur des pelouses.
SUN = np.array([-0.06, 0.998])
SUN_TAN = 0.2126                # soleil à 12° : l'ombre de la tour fait 4,7 fois sa hauteur
for mod in (V, mq):
    mod.SUN, mod.SUN_TAN, mod.KSH = SUN, SUN_TAN, SUN / SUN_TAN
mq.HAZE = '#F5D3B6'
mq.SKYC = ['#F5D3B6', '#F3C6AC', '#E6BFB4', '#CFBCC4', '#B2B9D2']     # couchant : orangé à l'horizon, rose, puis lavande
mq.FAR = 1300.0

COLS = {
    # pierre (réchauffée par le soleil bas), zinc (peu bleu), brisis, lucarnes, souches et pots
    'P1': '#F2C99C', 'P2': '#E3C4A0', 'P3': '#7C8597', 'PW': '#8C7462',
    'ZN0': '#F3DCC0', 'ZN1': '#D2C6BD', 'ZN2': '#B4B3BA',
    'B1': '#4A5273', 'B2': '#404967', 'B3': '#343B55', 'LU': '#EFE3CC',
    'CS1': '#E8D3B4', 'CS2': '#D2BFA2', 'CS3': '#858B9A', 'PO': '#B4603F', 'PO2': '#7E4330',
    # sol
    'CO': '#4F4E5A', 'CO2': '#6A6C7B', 'RU1': '#8F8A80', 'RU2': '#868178', 'TR': '#C9BCA6', 'AL': '#EAD9C0', 'AL2': '#DBC8AA',
    'LA1': '#72905E', 'LA2': '#647F54', 'Q1': '#DCCDB8', 'Q2': '#C9B9A2', 'QM': '#B5A690',
    'SE1': '#3F4B44', 'SE2': '#4A5850', 'SE3': '#5A695E', 'SEO': '#2F3B3A',
    # arbres, tour, bateaux, tours lointaines
    'T0': '#6F8A3F', 'T1': '#557236', 'T2': '#3F592F', 'T3': '#2C3F28',
    'E1': '#A9775A', 'E2': '#7E6052', 'E3': '#56443F',
    'OR1': '#E9B84A', 'OR2': '#B8862E', 'BO1': '#F1EDE3', 'BO2': '#4B6591', 'TG1': '#BFC6CF', 'TG2': '#A2ABB8', 'TG3': '#8891A0',
}


class ParisPal(V.CityPal):
    """Ombre bleu-gris froide, jamais noire."""
    SHADE_MUL = (0.30, 0.31, 0.32)
    SHADE_ADD = (22.0, 36.0, 56.0)


CX = 448.0                      # axe du Champ-de-Mars
TOWER = (CX, 548.0)
TH, TB = 82.0, 14.4             # hauteur de la tour, demi-base (rapport 2,85 de face)
RIV = [(-40, 540), (200, 588), (448, 612), (700, 596), (940, 540)]
HW = 18.5                       # demi-largeur du fleuve (≈ 150 m)


# cadrage : depuis la rive d'en face, soleil dans le dos ; la Seine et le pont au premier plan, la tour, puis son ombre
# qui file sur le Champ-de-Mars jusqu'à l'école ; virage de 5°
CAM = {'start': (CX - 96.0, 802.0), 'yaw': (163.0, 158.0), 'speed': 20.0, 'z': (118.0, 126.0), 'pitch': (-27.5, -30.0)}


def eiffel(bx, zs, P):
    """Tour en treillis : quatre piles fines et ajourées qui penchent vers l'axe, grande arche, premier étage en plateau
    mince, tronc pincé jusqu'au deuxième étage, fût en lame qui s'effile, flèche."""
    cx, cy = TOWER
    o1 = V.orient(pk(P['E1']), pk(P['E2']), pk(P['E3']))
    o2 = V.orient(pk(P['E2']), pk(P['E3']), pk(P['E3']))
    f = (pk(P['E2']),) + o1
    fd = (pk(P['E3']),) + o2
    z1, z2, z3 = 14.3, 28.7, 69.0

    def frame(x, y, hs, za, zb, t, belt):
        """Un tronçon de pile à claire-voie : quatre montants d'angle, une ceinture un tronçon sur deux ; le fond passe à travers."""
        for sx in (-1, 1):
            for sy in (-1, 1):
                bx.col(x + sx * (hs - t / 2), y + sy * (hs - t / 2), t / 2, za, zb, f)
        if belt:
            bx.col(x, y, hs, zb - 0.4, zb, f)

    n1 = 5
    for i in range(n1):                                   # piles, du sol au premier étage
        a, b = i / n1, (i + 1) / n1
        c = 11.9 - 5.0 * (a ** 0.7)
        hs = 2.5 - 1.2 * a
        for sx in (-1, 1):
            for sy in (-1, 1):
                frame(cx + sx * c, cy + sy * c, hs, z1 * a, z1 * b, 0.95 - 0.2 * a, i % 2 == 1)
    for sgn in (-1, 1):                                   # la grande arche, sur les quatre faces
        for t in np.arange(-7.8, 7.8, 1.2):
            za = 12.6 * math.sqrt(max(0.0, 1 - ((t + 0.6) / 8.4) ** 2))
            if za > 1.5:
                bx.add(cx + t, cx + t + 1.2, cy + sgn * 8.3 - 0.45, cy + sgn * 8.3 + 0.45, za - 0.9, za + 0.2, *f)
                bx.add(cx + sgn * 8.3 - 0.45, cx + sgn * 8.3 + 0.45, cy + t, cy + t + 1.2, za - 0.9, za + 0.2, *f)
    bx.col(cx, cy, 8.8, z1 - 0.3, z1 + 0.6, fd)            # premier étage : un plateau mince
    n2 = 4
    for i in range(n2):                                   # le tronc pincé : quatre montants qui se rejoignent vite
        a, b = i / n2, (i + 1) / n2
        c = 5.0 - 3.4 * (a ** 0.7)
        hs = 1.9 - 0.8 * a
        zz0, zz1 = z1 + 0.6 + (z2 - z1 - 0.6) * a, z1 + 0.6 + (z2 - z1 - 0.6) * b
        for sx in (-1, 1):
            for sy in (-1, 1):
                frame(cx + sx * c, cy + sy * c, hs, zz0, zz1, 0.9 - 0.2 * a, i == 1)
    bx.col(cx, cy, 3.7, z2 - 0.5, z2 + 0.5, fd)            # deuxième étage
    n3 = 12
    for i in range(n3):                                   # le fût
        a, b = i / n3, (i + 1) / n3
        hs = 0.8 + 1.9 * (1 - a) ** 2.2
        bx.col(cx, cy, hs, z2 + 0.5 + (z3 - z2 - 0.5) * a, z2 + 0.5 + (z3 - z2 - 0.5) * b, f)
    bx.col(cx, cy, 1.5, z3, z3 + 1.4, fd)                  # troisième étage, flèche
    bx.col(cx, cy, 0.75, z3 + 1.4, z3 + 4.0, f)
    bx.col(cx, cy, 0.35, z3 + 4.0, TH, f)
    # l'ombre vient d'un VOLUME PLEIN invisible (profil de la tour) : les piles ajourées ne projetteraient que des miettes
    r0 = int(TB) + 2
    ix, iy = np.meshgrid(np.arange(int(cx) - r0, int(cx) + r0), np.arange(int(cy) - r0, int(cy) + r0), indexing='ij')
    r = np.maximum(np.abs(ix + 0.5 - cx), np.abs(iy + 0.5 - cy))
    prof = np.interp(r, [0.0, 1.6, 2.7, 3.7, 8.8, 14.4, 15.0], [TH, z3, z2 + 2, z2, z1 + 0.6, 3.0, 0.0])
    zs[ix, iy] = np.maximum(zs[ix, iy], prof)


def plan(seed, P):
    rng = np.random.default_rng(seed)
    bx = V.Boxes()
    zs = np.zeros((WX, WY), np.float32)
    xc = (np.arange(WX) + 0.5)[:, None] + np.zeros((1, WY))
    yc = np.zeros((WX, 1)) + (np.arange(WY) + 0.5)[None, :]

    def cseg(p, q):
        dx, dy = q[0] - p[0], q[1] - p[1]
        t = np.clip(((xc - p[0]) * dx + (yc - p[1]) * dy) / (dx * dx + dy * dy), 0, 1)
        return np.hypot(xc - p[0] - t * dx, yc - p[1] - t * dy)

    d_riv = np.minimum.reduce([cseg(a, b) for a, b in zip(RIV[:-1], RIV[1:])])
    north = yc > np.interp(xc, [p[0] for p in RIV], [p[1] for p in RIV])          # rive d'en face
    water = d_riv < HW
    isle = cseg((150, 566), (318, 596)) < 2.6                                     # une île en longue allée plantée
    water &= ~isle
    quai_bas = (d_riv >= HW) & (d_riv < HW + 4.0)
    quai_haut = (d_riv >= HW + 4.0) & (d_riv < HW + 12.0)
    # ponts : un grand sur l'axe, deux autres
    BR = [(CX, 4.6), (262.0, 3.4), (640.0, 2.0)]
    bridge = np.zeros((WX, WY), bool)
    for bxp, bw in BR:
        bridge |= (np.abs(xc - bxp) < bw) & (d_riv < HW + 4.0)
    # le Champ-de-Mars, la tour, l'école, les jardins d'en face
    champ = (np.abs(xc - CX) < 36) & (yc > 268) & (yc < 528)
    parvis = (np.abs(xc - CX) < 30) & (yc >= 528) & (d_riv >= HW + 3.0) & ~north
    ecole = (np.abs(xc - CX) < 52) & (yc > 206) & (yc <= 268)
    troc = (xc > CX - 44) & (xc < CX + 56) & north & (d_riv >= HW + 3.0) & (yc < 770)
    reserved = water | isle | quai_bas | quai_haut | bridge | champ | parvis | ecole | troc
    # voies : avenues plantées de part et d'autre, rues, diagonales
    street = np.zeros((WX, WY), bool)
    avenue = np.zeros((WX, WY), bool)
    AVX = [CX - 41.5, CX + 41.5]
    for ax in AVX:
        avenue |= (np.abs(xc - ax) < 3.6) & (yc > 150) & ~north & (d_riv > HW + 3)
    avenue |= (np.abs(yc - 199.5) < 3.6)                                          # avenue devant l'école
    DIAG = [((CX, 200), (250, 20)), ((CX, 200), (650, 20)), ((CX + 45, 290), (720, 520)), ((CX - 45, 290), (150, 500)),
            ((CX + 45, 520), (820, 330)), ((CX + 100, 640), (820, 900)), ((CX + 200, 200), (720, 720)),
            ((CX - 45, 525), (150, 320)), ((CX - 70, 330), (130, 575)), ((CX - 230, 250), (CX - 200, 590)),
            ((CX - 44, 700), (150, 930)), ((CX + 44, 700), (760, 930)), ((CX, 760), (CX, 1150))]
    d_diag = np.minimum.reduce([cseg(a, b) for a, b in DIAG])
    avenue |= d_diag < 3.4
    # îlots : bandes verticales de largeur variable, rues transversales propres à chaque bande (pas de quadrillage régulier)
    z = np.zeros((WX, WY), np.float32)
    hauss = np.zeros((WX, WY), bool)
    court = np.zeros((WX, WY), bool)
    pid = np.zeros((WX, WY), np.int32)
    pb = np.zeros((4, WX, WY), np.float32)                                       # bornes de la parcelle de chaque case
    near = lambda x_, y_: (CX - 230 < x_ < CX + 170) and (300 < y_ < 830)         # noqa: E731  détails fins : près du trajet
    npid = 1
    free = ~(reserved | avenue)
    xs = [4]
    while xs[-1] < WX - 30:
        xs.append(xs[-1] + int(rng.integers(23, 38)))
    stacks = []
    for x0, x1n in zip(xs[:-1], xs[1:]):
        x1 = x1n - 3                                                               # rue de 3 cases (12 m, 0,6 fois la façade)
        y = int(rng.integers(0, 12))
        while y < WY - 20:
            hgt = int(rng.integers(15, 31))
            y0, y1 = y, min(y + hgt, WY - 2)
            y = y1 + int(rng.integers(3, 6))
            w, h = x1 - x0, y1 - y0
            if w < 8 or h < 8:
                continue
            blk = np.zeros((w, h), bool)
            blk[:] = free[x0:x1, y0:y1]
            if blk.mean() < 0.25:
                continue
            ii, jj = np.meshgrid(np.arange(w), np.arange(h), indexing='ij')
            cut = (np.minimum(ii, w - 1 - ii) + np.minimum(jj, h - 1 - jj)) < 3      # angles coupés
            blk &= ~cut
            nxp = max(2, int(round(w / 7.5)))
            rows = 2 if h >= 15 else 1
            xb = np.round(np.linspace(0, w, nxp + 1)).astype(int)
            yb = np.round(np.linspace(0, h, rows + 1)).astype(int)
            zblk = np.zeros((w, h), np.float32)
            pblk = np.zeros((w, h), np.int32)
            for a in range(nxp):
                for b in range(rows):
                    zr = (5.6, 6.2, 6.5, 6.5, 6.8, 7.1, 7.4)[int(rng.integers(0, 7))]
                    zblk[xb[a]:xb[a + 1], yb[b]:yb[b + 1]] = zr
                    for q_, v_ in enumerate((x0 + xb[a], x0 + xb[a + 1], y0 + yb[b], y0 + yb[b + 1])):
                        pb[q_, x0 + xb[a]:x0 + xb[a + 1], y0 + yb[b]:y0 + yb[b + 1]] = v_
                    pblk[xb[a]:xb[a + 1], yb[b]:yb[b + 1]] = npid
                    npid += 1
            cblk = np.zeros((w, h), bool)
            for a in range(1, nxp):                                                # cours en puits, le long des mitoyens
                if rng.random() < 0.9:
                    cw, chh = int(rng.integers(3, 5)), int(rng.integers(4, 7))
                    cyy = yb[1] if rows == 2 else h // 2
                    cblk[max(2, xb[a] - cw // 2):min(w - 2, xb[a] - cw // 2 + cw), max(3, cyy - chh // 2):min(h - 3, cyy - chh // 2 + chh)] = True
            if w >= 22 and h >= 20:                                                  # grande cour carrée au cœur des grands îlots
                cblk[w // 2 - 3:w // 2 + 3, h // 2 - 3:h // 2 + 3] = True
            if rows == 2 and rng.random() < 0.5:                                    # une fente de cour le long du mur du fond
                a = int(rng.integers(0, nxp))
                cblk[xb[a] + 2:max(xb[a] + 3, xb[a + 1] - 2), yb[1] - 1:yb[1] + 1] = True
            cblk &= blk
            bmask = blk & ~cblk
            z[x0:x1, y0:y1] = np.where(bmask, zblk, z[x0:x1, y0:y1])
            hauss[x0:x1, y0:y1] |= bmask
            court[x0:x1, y0:y1] |= cblk
            pid[x0:x1, y0:y1] = np.where(bmask, pblk, pid[x0:x1, y0:y1])
            if near((x0 + x1) / 2, (y0 + y1) / 2):                                  # souches de cheminées : longues et basses, en travers sur les mitoyens
                for a in range(1, nxp):
                    for b in range(rows):
                        ycn = (yb[b] + yb[b + 1]) / 2
                        ln = min(5.4, (yb[b + 1] - yb[b]) - 3.0)
                        ja, jb = int(ycn - ln / 2), int(ycn + ln / 2)
                        if ln >= 2.6 and 1 <= xb[a] < w - 1 and bmask[xb[a] - 1:xb[a] + 1, ja:jb + 1].all():
                            gx = x0 + xb[a]
                            zt = float(max(zblk[xb[a], ja], zblk[xb[a] - 1, ja]))
                            stacks.append((gx - 0.42, gx + 0.42, y0 + ycn - ln / 2, y0 + ycn + ln / 2, zt, zt + 0.85))
    # repères en volumes
    f_ch = (pk(P['CS1']),) + V.orient(pk(P['CS1']), pk(P['CS2']), pk(P['CS3']))
    f_po = (pk(P['PO']),) + V.orient(pk(P['PO']), pk(P['PO']), pk(P['PO2']))       # les pots : terre cuite, un par un
    for (a0, a1, b0, b1, c0, c1) in stacks:
        bx.add(a0, a1, b0, b1, c0, c1, *f_ch)
        for yp in np.arange(b0 + 0.25, b1 - 0.5, 0.9):
            bx.add(a0 + 0.14, a1 - 0.14, yp, yp + 0.5, c1, c1 + 0.55, *f_po)
        i0 = int((a0 + a1) / 2)
        zs[i0 - 1:i0 + 1, int(b0):int(b1) + 1] = np.maximum(zs[i0 - 1:i0 + 1, int(b0):int(b1) + 1], c1 + 0.3)
    eiffel(bx, zs, P)
    stone = V.faces(P, 'P1', 'P2', 'P3', top='ZN1', alt='PW', mode=3)

    def bloc(x0, x1, y0, y1, zt, mans=True):
        z[int(x0):int(x1), int(y0):int(y1)] = zt
        hauss[int(x0):int(x1), int(y0):int(y1)] = mans
        court[int(x0):int(x1), int(y0):int(y1)] = False

    # l'école : un long corps, deux ailes, un pavillon central à dôme
    bloc(CX - 46, CX + 46, 232, 244, 6.0)
    bloc(CX - 46, CX - 38, 212, 232, 5.6)
    bloc(CX + 38, CX + 46, 212, 232, 5.6)
    bloc(CX - 9, CX + 9, 240, 252, 7.6)
    dome = (pk(P['ZN1']), (pk(P['ZN0']), pk(P['ZN2']), pk(P['B1'])))
    prisms = [(CX, 246.0, 6.0, 7.6, 10.4) + dome, (CX, 246.0, 4.4, 10.4, 12.6) + dome, (CX, 246.0, 2.4, 12.6, 14.2) + dome,
              (CX, 246.0, 0.6, 14.2, 16.4) + dome]
    zs[int(CX) - 5:int(CX) + 5, 241:251] = 13.0
    # en face : deux ailes de palais de part et d'autre de l'axe, bassin au milieu
    for sgn in (-1, 1):
        for k in range(5):
            xa = CX + sgn * (16 + 6 * k)
            bloc(min(xa, xa + sgn * 6), max(xa, xa + sgn * 6), 716 + 2.5 * k, 726 + 2.5 * k, 5.2, mans=False)
    # silhouettes lointaines dans la brume : une tour sombre isolée dans l'axe, un dôme doré
    dk = V.faces(P, 'B1', 'B2', 'B3', top='B2')
    bx.add(CX + 38, CX + 44, 46, 50, 0, 52, *dk)
    zs[int(CX) + 38:int(CX) + 44, 46:50] = 52
    gold = (pk(P['OR1']), (pk(P['OR1']), pk(P['OR2']), pk(P['OR2'])))
    prisms += [(CX + 196.0, 318.0, 5.0, 6.5, 11.0) + gold, (CX + 196.0, 318.0, 3.4, 11.0, 14.0) + gold, (CX + 196.0, 318.0, 0.8, 14.0, 18.0) + gold]
    bloc(CX + 186, CX + 206, 308, 328, 6.5)
    # tours lointaines (volumes de verre)
    tg = V.faces(P, 'TG1', 'TG2', 'TG3', top='TG1')
    tr2 = np.random.default_rng(seed + 9)
    for k in range(11):
        tx, ty = tr2.uniform(300, 400), tr2.uniform(1118, 1144)
        hw_, hh = tr2.uniform(2.2, 3.6), tr2.uniform(12, 26)
        bx.add(tx - hw_, tx + hw_, ty - hw_, ty + hw_, 0, hh, *tg)
    pile = V.faces(P, 'Q1', 'Q2', 'CS3', top='Q1')
    deck = V.faces(P, 'Q1', 'Q2', 'CS3', top='TR')
    for bxp, bw in BR:                                                         # ponts : tablier en volume sur piles de pierre, l'eau passe dessous
        yr = float(np.interp(bxp, [p[0] for p in RIV], [p[1] for p in RIV]))
        bx.add(bxp - bw, bxp + bw, yr - HW - 4.5, yr + HW + 4.5, 1.05, 1.75, *deck)
        for dy in (-14.6, -7.3, 0.0, 7.3, 14.6):                             # piles, avec un départ d'arche de chaque côté
            bx.add(bxp - bw - 0.5, bxp + bw + 0.5, yr + dy - 0.8, yr + dy + 0.8, 0.0, 1.05, *pile)
            bx.add(bxp - bw, bxp + bw, yr + dy - 2.0, yr + dy + 2.0, 0.65, 1.05, *pile)
        zs[int(bxp - bw):int(bxp + bw) + 1, int(yr - HW - 4):int(yr + HW + 4)] = 1.75
    # péniches le long des quais bas
    boat = (pk(P['BO1']),) + V.orient(pk(P['BO1']), pk(P['BO1']), pk(P['BO2']))
    for k in range(16):
        bxx = 150 + 44 * k + tr2.uniform(-8, 8)
        yr = float(np.interp(bxx, [p[0] for p in RIV], [p[1] for p in RIV]))
        side = -1 if k % 2 else 1
        if min(abs(bxx - b[0]) for b in BR) > 12:
            bx.add(bxx - 4.0, bxx + 4.0, yr + side * (HW - 2.2) - 0.9, yr + side * (HW - 2.2) + 0.9, 0.0, 0.9, *boat)
    z[avenue & ~reserved] = 0
    hauss &= z > 0
    court &= ~(avenue | reserved)
    zone = (xc > CX - 230) & (xc < CX + 170) & (yc > 300) & (yc < 830)
    openc = ~hauss & ~court
    lu = (pk(P['ZN1']),) + V.orient(pk(P['LU']), pk(P['LU']), pk(P['CS3']))
    odd = ((np.arange(WX)[:, None] + np.arange(WY)[None, :]) & 1) == 1          # une lucarne par travée, au droit des fenêtres
    for (di, dj) in ((0, 1), (-1, 0)):                                         # faces nord (au soleil, vers la caméra) et ouest
        nb = np.roll(np.roll(openc, -di, 0), -dj, 1)                           # la case voisine est une rue
        ii, jj = np.nonzero(hauss & zone & nb & odd)
        zr = z[ii, jj]
        for i_, j_, z_ in zip(ii.tolist(), jj.tolist(), zr.tolist()):
            if dj == 1:
                bx.add(i_ + 0.1, i_ + 0.9, j_ + 0.65, j_ + 1.3, z_ - 1.35, z_ - 0.25, *lu)
            else:
                bx.add(i_ - 0.3, i_ + 0.35, j_ + 0.1, j_ + 0.9, z_ - 1.35, z_ - 0.25, *lu)
    # quais, ponts, île : cases surélevées
    kind = np.zeros((WX, WY), np.uint8)
    z[quai_haut & ~bridge] = 1.5
    z[quai_bas & ~bridge] = 0.35
    z[bridge & (d_riv < HW)] = 0.0
    z[bridge & quai_bas] = 0.35
    z[isle] = 0.6
    kind[quai_haut | quai_bas | bridge | isle] = 1
    hauss[quai_haut | quai_bas | bridge | isle] = False
    return dict(z=z, hauss=hauss, court=court, pid=pid, pb=pb, kind=kind, water=water, isle=isle, quai_bas=quai_bas, quai_haut=quai_haut,
                bridge=bridge, champ=champ, parvis=parvis, ecole=ecole, troc=troc, avenue=avenue, north=north, d_riv=d_riv,
                boxes=bx, zs=zs, prisms=prisms, AVX=AVX, DIAG=DIAG, rng=rng)


def assemble(pl, pal, seed):
    P = pal.ix
    rng = np.random.default_rng(seed + 50)
    up = V.up
    z = pl['z']
    zf = up(z)
    bld = up(pl['hauss'] | ((z > 2.0) & ~pl['hauss']))
    hb = mq.hash2(NX // 2 + 1, NY // 2 + 1, 21).repeat(2, 0).repeat(2, 1)[:NX, :NY]
    X, Y = V.XX, V.YY
    n1, n2 = V.noise(7, rng), V.noise(30, rng)
    m = np.zeros((NX, NY), np.uint8)
    mb = np.zeros((NX, NY), np.uint8)
    ma = np.zeros((NX, NY), np.uint8)
    tag = np.zeros((NX, NY), np.uint8)

    def flat(mask, name):
        m[mask] = P[name]
        ma[mask] = 0

    def blend(mask, a, b, f):
        m[mask] = P[a]
        mb[mask] = P[b]
        ma[mask] = np.round(np.clip(f, 0, 1) * 15)[mask] if isinstance(f, np.ndarray) else int(round(f * 15))

    # chaussée, trottoirs
    blend(np.ones((NX, NY), bool), 'RU1', 'RU2', 0.2 + 0.6 * n2)
    walk = V.dilate(bld, 2) & ~bld
    flat(walk, 'TR')
    flat(up(pl['court']), 'CO')
    # Champ-de-Mars : pelouses en bandes rectangulaires, allées claires
    champ = up(pl['champ'])
    flat(champ | up(pl['parvis']) | up(pl['troc']), 'AL')
    blend((champ | up(pl['parvis'])) & (hb < 0.5), 'AL', 'AL2', 0.5)
    dxc = np.abs(X - CX)
    lawn = champ & (dxc > 3.0) & (dxc < 17.0) & (((Y - 272) % 42.0) > 5.0) & (Y < 505)
    side = champ & (dxc >= 21.0)
    blend(lawn, 'LA1', 'LA2', 0.15 + 0.7 * n1)
    blend(side, 'LA2', 'LA1', 0.3 * n1)
    troc = up(pl['troc'])
    # esplanade d'en face : claire et dégagée dans l'axe (c'est là que tombe l'aiguille d'ombre), pelouses sur les côtés
    blend(troc & (((X - CX) < -8.0) | ((X - CX) > 40.0)) & (Y < 712), 'LA1', 'LA2', 0.2 + 0.6 * n1)
    blend(up(pl['ecole']) & ~bld, 'AL', 'AL2', 0.4)
    # Seine : vert-gris, deux tons tramés et des plages plus claires
    water = up(pl['water'])
    d_riv = up(pl['d_riv'])
    blend(water, 'SE1', 'SE2', np.clip(0.9 * (n2 - 0.3), 0, 1))
    blend(water & (n2 > 0.7), 'SE2', 'SE3', (n2 - 0.7) * 2.5)
    hr = mq.hash2(NX // 8 + 1, NY // 2 + 1, 33).repeat(8, 0).repeat(2, 1)[:NX, :NY]      # reflets : traits de 4 unités le long du courant
    refl = water & (hr < 0.035)
    # quais : bas clair au ras de l'eau, haut avec chaussée ; ponts ; île
    flat(up(pl['quai_bas']), 'Q1')
    blend(up(pl['quai_haut']), 'Q2', 'RU1', 0.5)
    flat(up(pl['quai_haut']) & (d_riv < HW + 3.6), 'QM')                # le couronnement du mur de quai
    blend(up(pl['isle']), 'AL', 'LA2', 0.4)
    # toits : terrasson de zinc clair, un ton par immeuble ; bande sombre du brisis côté rue
    roof = bld & (zf > 2.0)
    hs_ = up(pl['hauss'])
    px0, px1, py0, py1 = (up(pl['pb'][q_]) for q_ in range(4))
    dW, dE, dS, dN = X - px0, px1 - X, Y - py0, py1 - Y
    lit_pan = np.minimum(dW, dS) <= np.minimum(dE, dN)                  # terrasson à pans : ceux qui regardent le soleil sont clairs
    flat(roof, 'ZN1')
    flat(roof & hs_ & ~lit_pan, 'ZN2')
    street_side = ~bld & ~up(pl['court'])
    rim = roof & hs_ & V.dilate(street_side, 2)                        # le brisis vu d'en haut : une bande sombre d'une unité, de près
    # ombres portées : balayage vers le soleil bas ; longues, bleu-gris
    zsw = np.maximum(z, pl['zs'])
    shade_c = np.zeros(z.shape, bool)
    reach = int(min(400, zsw.max() / SUN_TAN + 2))
    for i in range(1, reach):
        ox, oy = int(round(SUN[0] * i)), int(round(SUN[1] * i))
        src = np.roll(np.roll(zsw, -ox, 0), -oy, 1)
        shade_c |= src > z + math.hypot(ox, oy) * SUN_TAN + 0.35
    shadow = up(shade_c)
    # arbres : alignements doubles des avenues, masses du Champ-de-Mars, quais hauts, jardins
    tr = []
    for ax in pl['AVX']:
        for o in (-2.4, 2.4):
            tr.append(V.row_trees(rng, [(ax + o, 152), (ax + o, 520)], 3.4, 0.0, 1.7))
    for a, b in pl['DIAG']:
        for o in (-2.3, 2.3):
            tr.append(V.row_trees(rng, [a, b], 3.6, o, 1.6))
    for sgn in (-1, 1):
        for o in (23.5, 28.0, 32.5):
            tr.append(V.row_trees(rng, [(CX + sgn * o, 274), (CX + sgn * o, 522)], 3.3, 0.0, 1.7))
        for t in np.linspace(0, math.pi / 2, 9):                         # bosquets en courbes symétriques près de la tour
            tr.append(np.array([[CX + sgn * (19 - 13 * math.sin(t)), 508 + 16 * math.cos(t) - 14, 0, 1.8, 3.4]], np.float32))
    for o in (HW + 6.0, HW + 9.0):
        tr.append(V.row_trees(rng, RIV, 3.6, o, 1.7))
        tr.append(V.row_trees(rng, RIV, 3.6, -o, 1.7))
    tr.append(V.row_trees(rng, [(152, 566), (316, 596)], 3.0, 0.0, 1.4))
    tr.append(V.park_trees(rng, troc & ((X - CX) < -12.0) & (Y < 712), 0.6, step=3.6, size=(1.5, 1.9)))
    trees = np.concatenate(tr)
    ci, cj = np.clip(trees[:, 0].astype(int), 0, WX - 1), np.clip(trees[:, 1].astype(int), 0, WY - 1)
    ok = (z[ci, cj] <= 1.6) & ~pl['water'][ci, cj] & ~pl['bridge'][ci, cj] & (trees[:, 0] > 4) & (trees[:, 0] < WX - 4)
    trees = trees[ok]
    trees[:, 2] = z[ci, cj][ok]
    trees[:, 4] = trees[:, 3] * 1.9
    tx, ty, tz, tw, th = trees.T
    R = 44
    for i in range(1, R):                                                   # ombre longue de chaque arbre, vers l'opposé du soleil
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                cx_ = ((tx - SUN[0] * i * 0.5) * K).astype(int) + dx
                cy_ = ((ty - SUN[1] * i * 0.5) * K).astype(int) + dy
                ok2 = (dx * dx + dy * dy <= (tw * K * 0.9) ** 2) & (i * 0.5 * SUN_TAN < th * 0.8) & (cx_ >= 0) & (cx_ < NX) & (cy_ >= 0) & (cy_ < NY)
                shadow[cx_[ok2], cy_[ok2]] |= zf[cx_[ok2], cy_[ok2]] < 2.0
    m0 = m.copy()
    m0[rim] = P['B2']                                                   # de près seulement
    m0[refl & ~shadow] = P['SE3']
    m[refl & ~shadow] = P['SE3']
    ridge = roof & hs_ & (np.abs(np.minimum(dW, dS) - np.minimum(dE, dN)) < 0.3)
    m0[ridge & ~rim] = P['ZN0']                                         # l'arêtier de zinc entre deux pans
    m = np.where(shadow, pal.luts[0][m], m)
    m0 = np.where(shadow, pal.luts[0][m0], m0)
    mb = np.where(shadow, pal.luts[0][mb], mb)
    w = {'z': z, 'kind': pl['kind'], 'map': m0, 'map_far': m, 'mapb': mb, 'mapa': ma, 'tag': tag,
         'open_water': np.zeros((NX, NY), bool)}
    return w, trees


def ciel(f, r, u, sky_idx):
    """Ciel de couchant : cinq paliers serrés (un par 2° environ), bords tramés."""
    th = math.tan(mq.VFOV / 2)
    x = ((np.arange(NW) + 0.5) / NW * 2 - 1) * th * NW / NH
    y = (1 - (np.arange(NH) + 0.5) / NH * 2) * th
    dz = f[2] + x[None, :] * r[2] + y[:, None] * u[2]
    el = dz / np.sqrt(1 + x[None, :] ** 2 + y[:, None] ** 2)
    bay = (mq.BAYER[np.arange(NH)[:, None] % 4, np.arange(NW)[None, :] % 4] + 0.5) / 16.0
    # le dégradé part de l'horizon apparent (la brume qui noie le sol lointain, environ 9° sous l'horizontale)
    band = np.clip(np.floor(np.clip(el + 0.155, 0, 1) * 30.0 + (bay - 0.5) * 0.9), 0, len(sky_idx) - 1).astype(int)
    return sky_idx[band]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gpu', default='radeon', choices=['radeon', 'intel'])
    ap.add_argument('--seed', type=int, default=1811)
    ap.add_argument('--out', default='sortie/paris.mp4')
    ap.add_argument('--frames')
    ap.add_argument('--stills')
    ap.add_argument('--dump')
    ap.add_argument('--json')
    a = ap.parse_args()
    out = Path(a.out)
    t0 = time.perf_counter()
    pal = ParisPal({**V.COMMON, **COLS})
    P = pal.ix
    for n_ in ('SE1', 'SE2', 'SE3'):                                    # sur l'eau sombre, l'ombre doit rester lisible : bleu nuit
        pal.luts[0][P[n_]] = P['SEO']
    pl = plan(a.seed, P)
    w, trees = assemble(pl, pal, a.seed)
    spec = {
        'kinds': [('P1', 'P2', 'P3', 'PW'), ('Q1', 'Q2', 'CS3', None)], 'sun_tones': True,
        'mansard': {'hauss': pl['hauss'], 'court': pl['court'], 'h': 1.5,
                    'mats': (pk(P['B1']), pk(P['B2']), pk(P['B3'])), 'court_mat': pk(P['CO2'])},
        'boxes': pl['boxes'], 'prisms': pl['prisms'], 'trees': trees, 'strokes': 0, 'tree_simple': True,
        'clouds': (175.0, 190.0, 110, 9.0, 15.0), 'cloud_gap': 115, 'cloud_box': (-420, WX, -100, WY),
        # la tour, son ombre et le fleuve restent au soleil : pas de disque d'ombre de nuage sur l'eau
        'cloud_free': [(np.array(TOWER), np.array(TOWER) - V.KSH * TH, 60.0), (np.array([0.0, 575.0]), np.array([896.0, 590.0]), 75.0)],
    }
    mesh, mask, mg = V.build_mesh(w, spec, pal, a.seed)
    t_world = time.perf_counter() - t0
    # cadrage : au-dessus des îlots à l'est du Champ-de-Mars, la tour au centre gauche, virage faible
    cam = CAM
    fog = (float(os.environ.get('P_FOG', 300.0)), 60.0, 150.0)
    nframes = int(round(DUR * FPS))
    cams = V.camera_table(cam, nframes)
    zs = np.maximum(w['z'], pl['zs'])
    for eye, *_ in cams:
        i, j = int(np.clip(eye[0], 6, WX - 7)), int(np.clip(eye[1], 6, WY - 7))
        assert eye[2] - zs[i - 6:i + 7, j - 6:j + 7].max() > 8.0, f'caméra trop basse à {eye}'
    t1 = time.perf_counter()
    mq.GEOM_WGSL = mq.GEOM_WGSL.replace('WIN_S', '1u').replace('WALL_K', '2.0')
    eng = mq.Engine(a.gpu, 4, mesh, w, mask, mg, pal)
    f, r, u = mq.basis(*cams[0][1:])
    eng.frame(mq.view_proj(cams[0][0], f, r, u), cams[0][0], 0, *fog)
    t_init = time.perf_counter() - t1
    out.parent.mkdir(parents=True, exist_ok=True)
    todo = [int(x) for x in a.frames.split(',')] if a.frames else list(range(nframes))
    stills = {int(round(float(s) * FPS)): s for s in a.stills.split(',')} if a.stills else {}
    ff = None
    if not a.frames:
        part = out.with_suffix('.part.mp4')
        ff = subprocess.Popen(
            ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{NW}x{NH}',
             '-framerate', str(FPS), '-i', '-', '-vf', f'scale={NW * SCALE}:{NH * SCALE}:flags=neighbor',
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', str(FPS),
             '-movflags', '+faststart', str(part)], stdin=subprocess.PIPE)
    md5 = hashlib.md5()
    frames = np.zeros((len(todo), NH, NW), np.uint8) if a.dump else None
    ncol, tg = [], 0.0
    t2 = time.perf_counter()
    for k, n in enumerate(todo):
        eye, yaw, pitch, roll = cams[n]
        f, r, u = mq.basis(yaw, pitch, roll)
        ta = time.perf_counter()
        idx = eng.frame(mq.view_proj(eye, f, r, u), eye, n, *fog).copy()
        tg += time.perf_counter() - ta
        skym = (idx == mq.SKY_CODE) | (idx == pal.sky[0])                # ciel, et sol lointain entièrement noyé dans la brume
        idx[skym] = ciel(f, r, u, pal.sky)[skym]
        md5.update(idx.tobytes())
        ncol.append(len(np.unique(idx)))
        if frames is not None:
            frames[k] = idx
        rgb = pal.table[idx]
        if ff:
            ff.stdin.write(rgb.tobytes())
        if a.frames or n in stills:
            name = f'img_{n:03d}.png' if a.frames else f'still_{float(stills[n]):.1f}s.png'
            Image.fromarray(rgb).resize((NW * SCALE, NH * SCALE), Image.NEAREST).save(out.parent / name)
    if ff:
        ff.stdin.close()
        ff.wait()
        os.replace(part, out)
    total = time.perf_counter() - t2
    if a.dump:
        np.save(a.dump, frames)
    res = {
        'gpu': eng.info.get('device'), 'seed': a.seed, 'frames': len(todo), 'triangles': len(mesh) // 3, 'trees': int(len(trees)),
        'worldBuildSec': round(t_world, 2), 'gpuInitSec': round(t_init, 2), 'renderSec': round(total, 2),
        'secPer100Frames': round(total / len(todo) * 100, 2), 'msPerFrameTotal': round(total / len(todo) * 1000, 1),
        'msPerFrameGpu': round(tg / len(todo) * 1000, 1),
        'colorsPerFrame': [int(min(ncol)), int(np.median(ncol)), int(max(ncol))], 'paletteSize': len(pal.rgb),
        'md5NativeIndexFrames': md5.hexdigest(), 'md5Mp4': hashlib.md5(out.read_bytes()).hexdigest() if ff else None,
        'load1min': round(os.getloadavg()[0], 2),
    }
    print(json.dumps(res, indent=1, ensure_ascii=False))
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
