#!/usr/bin/env python3
"""
briques.py — lecture commune des briques (habillages, mécaniques, formats, recettes) pour check.py, build_index.py,
recognition.py et la vitrine (out/showcase/build.py). Aucune dépendance hors stdlib. Lecture seule : n'écrit rien.

Modèle : vidéo = Habillage × Mécanique × Format (+ Son) ; une combinaison nommée et validée = une recette
(out/report/notes/composition/proposition.md). Fiches :
  out/habillages/<id>/habillage.json        (une famille, ex. « craie », a ses variantes dans variantes/<v>.json)
  out/mecaniques/<id>/mecanique.json
  out/formats/<id>.json
  out/recettes/<id>.json                    (etiquettes.json et propositions.json, dans le même dossier, ne sont pas des recettes)

Clé d'habillage d'un short (`pate`) : l'id de l'habillage, ou « famille/variante » pour une famille (craie/ardoise,
craie/tableau-vert). Les anciens ids remplacés (ardoise, craie-verte) sont ramenés à leur variante.

Ordre de lecture des briques d'un short (le premier qui répond gagne) :
  1. out/recettes/etiquettes.json  (étiquetage des 50 shorts existants + la recette adoptée « Données qui se tracent »)
  2. le short.json du short        (les shorts nés d'une case de la matrice déclarent leurs briques eux-mêmes)
  3. la recette du même id que le préfixe du dossier (<recette>__<famille>__<sujet>)
Aucun short.json n'est réécrit.
"""
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'out'
NON_RECETTES = {'etiquettes.json', 'propositions.json'}


def _load(p):
    return json.loads(Path(p).read_text())


@lru_cache(None)
def recettes():
    """id -> manifeste de recette (out/recettes/*.json, sans etiquettes.json ni propositions.json)."""
    out = {}
    for f in sorted((OUT / 'recettes').glob('*.json')):
        if f.name in NON_RECETTES:
            continue
        r = _load(f)
        out[r['id']] = {**r, '_fichier': str(f.relative_to(ROOT))}
    return out


@lru_cache(None)
def habillages():
    """clé de pâte -> fiche. Clés : id simple (grille-suisse), famille (craie), variante (craie/ardoise).
    Les fiches remplacées (statut « remplacee ») sont gardées, avec leur ancien id."""
    out = {}
    for f in sorted((OUT / 'habillages').glob('*/habillage.json')):
        h = _load(f)
        out[h['id']] = {**h, '_fichier': str(f.relative_to(ROOT))}
        for v in sorted((f.parent / 'variantes').glob('*.json')) if (f.parent / 'variantes').exists() else []:
            hv = _load(v)
            out[hv['id']] = {**hv, '_fichier': str(v.relative_to(ROOT))}
    return out


@lru_cache(None)
def mecaniques():
    return {m['id']: {**m, '_fichier': str(f.relative_to(ROOT))}
            for f in sorted((OUT / 'mecaniques').glob('*/mecanique.json')) for m in [_load(f)]}


@lru_cache(None)
def formats():
    return {x['id']: {**x, '_fichier': str(f.relative_to(ROOT))} for f in sorted((OUT / 'formats').glob('*.json')) for x in [_load(f)]}


@lru_cache(None)
def etiquettes():
    p = OUT / 'recettes/etiquettes.json'
    return _load(p)['shorts'] if p.exists() else {}


@lru_cache(None)
def propositions():
    """cases proposées de la matrice (matrice.md), pas encore essayées : C3, C5…C8 (out/recettes/propositions.json)."""
    p = OUT / 'recettes/propositions.json'
    return _load(p)['cases'] if p.exists() else []


@lru_cache(None)
def anciens_ids():
    """ancien id d'habillage remplacé -> clé de variante (ardoise -> craie/ardoise, craie-verte -> craie/tableau-vert)."""
    m = {}
    for k, h in habillages().items():
        if h.get('ancienId'):
            m[h['ancienId']] = k
        if h.get('remplacePar'):
            m[h['id']] = h['remplacePar']
    return m


def pate(habillage, variante=None):
    """clé de pâte : « famille/variante » pour une famille, l'id sinon ; un ancien id remplacé devient sa variante."""
    if not habillage:
        return None
    if variante:
        return f'{habillage}/{variante}'
    return anciens_ids().get(habillage, habillage)


def familles():
    """id de famille -> liste des clés de variante."""
    return {k: h.get('variantes') or [] for k, h in habillages().items() if h.get('type') == 'famille'}


def actifs():
    """habillages en service (fiches remplacées exclues), au niveau de la pâte : une famille compte par ses variantes.
    Rend (habillages, pates) : habillages = ids de premier niveau (craie compte 1), pates = clés de ligne de matrice."""
    H = habillages()
    top = [k for k, h in H.items() if '/' not in k and h.get('statut') != 'remplacee']
    pates = []
    for k in top:
        pates += familles()[k] if k in familles() else [k]
    return top, pates


def briques_du_short(nom):
    """briques d'un short (nom de dossier sous out/shorts/) : recette, habillage, variante, pate, mecanique, format,
    statut de la recette, source (etiquettes | short.json | recette | prefixe)."""
    e = etiquettes().get(nom)
    src = 'etiquettes'
    if not e:
        sj = OUT / 'shorts' / nom / 'short.json'
        j = _load(sj) if sj.exists() else {}
        if j.get('habillage') and j.get('mecanique'):
            e, src = {k: j.get(k) for k in ('recette', 'habillage', 'variante', 'mecanique', 'format')}, 'short.json'
            # un ancien id (craie-verte) : la recette du short donne la variante à jour
            r = recettes().get(e.get('recette') or '')
            if r and r.get('habillageAvant') == e['habillage']:
                e.update(habillage=r['habillage'], variante=r.get('variante'))
        else:
            r = recettes().get(nom.split('__')[0])
            if r:
                e, src = {'recette': r['id'], 'habillage': r['habillage'], 'variante': r.get('variante'),
                          'mecanique': r['mecanique'], 'format': (r.get('formats') or [None])[0]}, 'recette'
            else:
                return {'recette': nom.split('__')[0], 'habillage': None, 'variante': None, 'pate': None,
                        'mecanique': None, 'format': None, 'statut': None, 'source': 'prefixe'}
    rid = e.get('recette') or nom.split('__')[0]
    r = recettes().get(rid) or {}
    p = pate(e.get('habillage'), e.get('variante'))
    fam, _, var = p.partition('/') if p and '/' in p else (e.get('habillage'), '', e.get('variante'))
    return {'recette': rid, 'habillage': fam, 'variante': var or None, 'pate': p, 'mecanique': e.get('mecanique'),
            'format': e.get('format'), 'statut': r.get('statut'), 'source': src}


def nom_pate(cle):
    h = habillages().get(cle) or {}
    return h.get('nom') or cle


# ---------- couleurs ----------
def _lum(h):
    h = h.lstrip('#')[:6]
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contraste(a, b):
    """rapport de contraste WCAG entre deux couleurs hex, None si l'une manque."""
    try:
        la, lb = sorted((_lum(a), _lum(b)), reverse=True)
        return round((la + 0.05) / (lb + 0.05), 2)
    except Exception:
        return None
