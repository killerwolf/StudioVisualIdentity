#!/usr/bin/env python3
"""
check.py — contrôle qualité automatique d'un dossier de short (ou de tous).

USAGE
  python out/tools/check.py out/shorts/<dossier>         # un short
  python out/tools/check.py --all                        # tous les shorts -> out/report/qa.json
  python out/tools/check.py --briques                    # fiches des briques -> out/report/qa-briques.json

Vérifie : short.mp4 lisible par ffprobe, 1080×1920, 30 fps, H.264 yuv420p, durée 10–20 s (10–60 s pour la famille « paroles » et pour un short qui déclare "longForm": true dans short.json — déclinaisons narrées de lyrics-chemin, dont le texte est la route), piste audio présente,
absence de frames noires (blackdetect ≥ 0.25 s) et figées longues (freezedetect ≥ 3 s, avertissement seulement),
présence de short.json / narration.json / stills (3–5) / src/. Imprime un JSON {ok, errors, warnings}.

DURÉE ET FORMAT (depuis le 20/11/2026, migration.md étape 3) : le format du short est lu par out/tools/briques.py
(etiquettes.json, puis short.json, puis la recette du préfixe) et sa durée dans out/formats/<format>.json (dureeSec, avec la
même tolérance de 0,1 s que l'ancienne règle). Sans format connu, repli sur l'ancienne règle (paroles / longForm : 60 s,
sinon 20 s). Chaque ligne de qa.json porte aussi `briques` (recette, habillage, mécanique, format, statut de la recette) : un
short d'essai (C1) ou d'une recette abandonnée (C4) est contrôlé comme les autres ; son statut est indiqué, pas compté comme
un échec.

MODE --briques : contrôle les fiches out/habillages, out/mecaniques, out/formats, out/recettes et etiquettes.json :
  - erreurs : fiche illisible ou champ obligatoire absent ; recette qui pointe vers une brique, un format ou un short qui
    n'existe pas ; étiquette d'un short absent ; short sans briques ; chemin d'adaptateur absent ; adaptateur d'un moteur
    exécutable (chemin-moteur, papier-moteur, lyrics-moteur) dont les couleurs ou la police de titre ne sont pas celles de
    la fiche ;
  - avertissements : contraste de palette.encre sur la surface du texte < contrasteTexteMin (4,5:1), corpsMinPx < 54 sans
    exception écrite, format d'une recette que sa mécanique ne déclare pas, besoins de palette de la mécanique non remplis.
  Une recette à un seul short, un essai ou une recette abandonnée n'est pas une erreur. Sortie : out/report/qa-briques.json.
"""
import json, subprocess, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import briques as B  # noqa: E402


def probe(p):
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
                                   'stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt:format=duration',
                                   '-of', 'json', str(p)])
    return json.loads(out)


def check(d):
    d = Path(d)
    err, warn = [], []
    briq = B.briques_du_short(d.name)
    mp4 = d / 'short.mp4'
    info = {}
    if not mp4.exists():
        err.append('short.mp4 manquant')
    else:
        try:
            j = probe(mp4)
            v = [s for s in j['streams'] if s['codec_type'] == 'video']
            a = [s for s in j['streams'] if s['codec_type'] == 'audio']
            dur = float(j['format']['duration'])
            info = {'duration': round(dur, 2)}
            if not v:
                err.append('pas de piste vidéo')
            else:
                v = v[0]
                info.update(width=v['width'], height=v['height'], fps=v['r_frame_rate'], codec=v['codec_name'], pix=v['pix_fmt'])
                if (v['width'], v['height']) != (1080, 1920): err.append(f"taille {v['width']}x{v['height']}")
                if v['r_frame_rate'] not in ('30/1',): err.append(f"fps {v['r_frame_rate']}")
                if v['codec_name'] != 'h264': err.append('codec ' + v['codec_name'])
                if v['pix_fmt'] != 'yuv420p': err.append('pix_fmt ' + v['pix_fmt'])
            if not a: err.append('pas de piste audio')
            sj0 = json.load(open(d / 'short.json')) if (d / 'short.json').exists() else {}
            fam = sj0.get('family')
            fmt = B.formats().get(briq.get('format') or '')
            if fmt and fmt.get('dureeSec'):
                # durée du format (out/formats/<id>.json), même tolérance de 0,1 s que l'ancienne règle
                lo, hi = fmt['dureeSec']
                dmin, dmax = lo - 0.1, hi + 0.1
                info['format'] = fmt['id']
            else:
                # repli : une vidéo de paroles suit un extrait de chanson (jusqu'à 60 s) ; un short narré déclaré longForm aussi
                dmin, dmax = 9.9, (60.1 if fam == 'paroles' or sj0.get('longForm') is True else 20.1)
                info['format'] = None
            if not (dmin <= dur <= dmax): err.append(f'durée {dur:.2f}s hors {dmin + 0.1:.0f}–{dmax - 0.1:.0f} s')
            bd = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(mp4), '-vf', 'blackdetect=d=0.25:pix_th=0.06', '-an', '-f', 'null', '-'],
                                capture_output=True, text=True).stderr
            blacks = re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', bd)
            if blacks: err.append(f'frames noires: {blacks[:3]}')
            fz = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(mp4), '-vf', 'freezedetect=n=0.001:d=3', '-an', '-f', 'null', '-'],
                                capture_output=True, text=True).stderr
            fr = re.findall(r'freeze_start: ([\d.]+)', fz)
            if fr: warn.append(f'image figée ≥3 s à {fr[:3]}')
        except Exception as e:
            err.append('ffprobe: ' + str(e))
    for f in ('short.json', 'narration.json'):
        if not (d / f).exists(): err.append(f + ' manquant')
        else:
            try: json.load(open(d / f))
            except Exception as e: err.append(f'{f} invalide: {e}')
    # livrabilité : voix off, rythme de narration, relecture des stills (avertissements seulement)
    try:
        nar = json.load(open(d / 'narration.json')) if (d / 'narration.json').exists() else {}
        sj = json.load(open(d / 'short.json')) if (d / 'short.json').exists() else {}
        lines = nar.get('lines') or []
        if lines and not (sj.get('sound') or {}).get('voice'):
            warn.append('voix off absente (narration.json a des lignes mais short.json.sound.voice est faux)')
        nvl = len(list((d / 'voice_lines').glob('*.mp3'))) if (d / 'voice_lines').exists() else 0
        if lines and (sj.get('sound') or {}).get('voice') and (d / 'voice_lines').exists() and nvl != len(lines):
            warn.append(f'voice_lines : {nvl} fichiers pour {len(lines)} lignes')
        for i, l in enumerate(lines):
            md = float(l.get('maxDuration') or 0)
            if md > 0 and len(str(l.get('text', '')).split()) / md > 3.2:
                warn.append(f"ligne {i} : {len(str(l['text']).split())} mots en {md} s (> 3,2 mots/s)")
        if (sj.get('qualityChecks') or {}).get('stillsReviewed') is False:
            warn.append('stills non relus (qualityChecks.stillsReviewed = false)')
    except Exception as e:
        warn.append('lecture narration/short.json : ' + str(e))
    stills = list((d / 'stills').glob('*.jpg')) + list((d / 'stills').glob('*.png')) if (d / 'stills').exists() else []
    if not (3 <= len(stills)): err.append(f'stills: {len(stills)} (3–5 attendus)')
    if not (d / 'src').exists() or not any((d / 'src').iterdir()): err.append('src/ vide')
    return {'short': d.name, 'ok': not err, 'errors': err, 'warnings': warn, 'info': info,
            'briques': {k: briq[k] for k in ('recette', 'pate', 'mecanique', 'format', 'statut', 'source')}}


# ---------- mode --briques ----------
ROLES = ('fond', 'surface', 'encre', 'vif', 'second')
NEUTRES = set(ROLES) | {'decor', 'serie'}
STATUTS = {'validee', 'essai', 'abandonnee'}
MOTEURS_EXEC = ('out/shared/chemin-moteur/', 'out/shared/papier-moteur/', 'out/shared/lyrics-moteur/')


def _chemin_adaptateur(v):
    """premier chemin d'une valeur d'adaptateur (« out/…/x.json (+ …) — note » -> out/…/x.json)."""
    return str(v).split(' ')[0].strip()


def _couleurs_du_fichier(txt):
    """couleurs écrites dans un adaptateur : hex #RRGGBB, et triplets [r, g, b] (thèmes du moteur papier)."""
    hexes = {h.upper() for h in re.findall(r'#[0-9A-Fa-f]{6}\b', txt)}
    for r, g, b in re.findall(r'[\[(]\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*[\])]', txt):
        hexes.add('#%02X%02X%02X' % (int(r), int(g), int(b)))
    return hexes


def check_briques():
    err, warn, notes = [], [], []
    E = lambda q, m: err.append(f'{q} : {m}')
    W = lambda q, m: warn.append(f'{q} : {m}')
    H, M, F, R = B.habillages(), B.mecaniques(), B.formats(), B.recettes()
    # 1. fiches : champs obligatoires
    for k, h in H.items():
        q = h['_fichier']
        if h.get('type') == 'famille':
            for v in h.get('variantes') or []:
                if v not in H: E(q, f'variante {v} sans fiche')
            continue
        for c in ('id', 'nom', 'niveau', 'palette', 'typo'):
            if not h.get(c): E(q, f'champ « {c} » absent')
        if h.get('niveau') not in ('executable', 'declare'): E(q, f"niveau {h.get('niveau')!r} (executable | declare)")
        if h.get('statut') == 'remplacee' and h.get('remplacePar') not in H: E(q, f"remplacée par {h.get('remplacePar')!r}, fiche absente")
    for k, m in M.items():
        for c in ('id', 'nom', 'niveau', 'moteur', 'formats'):
            if not m.get(c): E(m['_fichier'], f'champ « {c} » absent')
        for f in m.get('formats') or []:
            if f not in F: E(m['_fichier'], f'format {f} inconnu')
    for k, f in F.items():
        for c in ('id', 'dureeSec', 'canevas', 'zonesSuresPx'):
            if not f.get(c): E(f['_fichier'], f'champ « {c} » absent')
    # 2. recettes : références
    for rid, r in R.items():
        q = r['_fichier']
        p = B.pate(r.get('habillage'), r.get('variante'))
        if p not in H: E(q, f'habillage {p!r} sans fiche')
        elif H[p].get('statut') == 'remplacee': W(q, f'habillage {p} remplacé par {H[p].get("remplacePar")}')
        if r.get('mecanique') not in M: E(q, f"mécanique {r.get('mecanique')!r} sans fiche")
        for f in r.get('formats') or []:
            if f not in F: E(q, f'format {f!r} sans fiche')
            elif r.get('mecanique') in M and f not in (M[r['mecanique']].get('formats') or []):
                W(q, f"format {f} non déclaré par la mécanique {r['mecanique']}")
        if r.get('statut') not in STATUTS: E(q, f"statut {r.get('statut')!r} ({' | '.join(sorted(STATUTS))})")
        if not r.get('shorts'): E(q, 'aucun short de preuve')
        for d in r.get('shorts') or []:
            if not (ROOT / d / 'short.mp4').exists(): E(q, f'short absent : {d}')
        if len(r.get('shorts') or []) == 1:
            notes.append(f"{rid} : une seule preuve ({r.get('statut')})")
    # 3. étiquettes et briques de chaque short
    for name in B.etiquettes():
        if not (ROOT / 'out/shorts' / name).is_dir(): E('out/recettes/etiquettes.json', f'short absent : {name}')
    for d in sorted(x for x in (ROOT / 'out/shorts').iterdir() if x.is_dir()):
        b = B.briques_du_short(d.name)
        if b['source'] == 'prefixe' or not b['pate'] or not b['mecanique'] or not b['format']:
            E(f'out/shorts/{d.name}', 'briques inconnues (ni etiquettes.json, ni short.json, ni recette du préfixe)'); continue
        r = R.get(b['recette'])
        if not r: E(f'out/shorts/{d.name}', f"recette {b['recette']!r} sans fiche"); continue
        if B.pate(r['habillage'], r.get('variante')) != b['pate'] or r['mecanique'] != b['mecanique']:
            E(f'out/shorts/{d.name}', f"briques {b['pate']} × {b['mecanique']} ≠ recette {r['id']} ({B.pate(r['habillage'], r.get('variante'))} × {r['mecanique']})")
        if f'out/shorts/{d.name}' not in (r.get('shorts') or []):
            W(r['_fichier'], f'le short {d.name} se réclame de la recette mais n\'est pas dans sa liste « shorts »')
    # 4. adaptateurs, contraste, corps
    for k, h in H.items():
        if h.get('type') == 'famille': continue
        q, pal = h['_fichier'], h.get('palette') or {}
        for mec, v in (h.get('adaptateurs') or {}).items():
            a = _chemin_adaptateur(v)
            if mec not in M: E(q, f'adaptateur pour une mécanique inconnue : {mec}')
            if not (ROOT / a).exists(): E(q, f'adaptateur absent : {a}'); continue
            if not (ROOT / a).is_file() or h.get('statut') == 'remplacee': continue
            txt = (ROOT / a).read_text(errors='ignore')
            if a.startswith('out/shared/papier-moteur/themes/') and not (json.loads(txt).get('polices') or {}):
                # thème sans polices : le moteur papier garde ses polices par défaut (pipeline/papier.py)
                txt += (ROOT / 'out/shared/papier-moteur/pipeline/papier.py').read_text(errors='ignore')
            cols = _couleurs_du_fichier(txt)
            manque = [f'{r} {pal[r]}' for r in ROLES if isinstance(pal.get(r), str) and pal[r].upper() not in cols]
            tit = ((h.get('typo') or {}).get('titre') or {}).get('famille')
            pol = tit and re.sub(r'\s+', '', tit).lower() not in re.sub(r'\s+', '', txt).lower()
            if manque or pol:
                msg = (f"adaptateur {a} : couleurs absentes ({', '.join(manque)})" if manque else f'adaptateur {a}') + (f' ; police de titre « {tit} » absente' if pol else '')
                # erreur pour une fiche « executable » d'un moteur partagé (l'adaptateur doit être la fiche) ; une fiche
                # « declare » (valeurs relevées dans les tokens d'une autre recette, ex. tableau-vert, grille-suisse) : avertissement
                (E if a.startswith(MOTEURS_EXEC) and h.get('niveau') == 'executable' else W)(q, msg + ('' if h.get('niveau') == 'executable' else ' (fiche « declare »)'))
        fond = pal.get('surface') or pal.get('fond')
        lis = h.get('lisibilite') or {}
        cmin = lis.get('contrasteTexteMin') or 4.5
        c = B.contraste(pal.get('encre'), fond) if isinstance(pal.get('encre'), str) and isinstance(fond, str) else None
        if c is not None and c < cmin:
            W(q, f"encre {pal['encre']} sur {'surface' if pal.get('surface') else 'fond'} {fond} : {c}:1 < {cmin}:1")
        if (lis.get('corpsMinPx') or 0) < 54 and not lis.get('exception'):
            W(q, f"corpsMinPx {lis.get('corpsMinPx')} < 54 sans exception écrite")
    # 5. besoins de palette des mécaniques (rôles neutres seulement) pour chaque recette
    for rid, r in R.items():
        m, p = M.get(r.get('mecanique')) or {}, B.pate(r.get('habillage'), r.get('variante'))
        req = [x for x in ((m.get('requiert') or {}).get('palette') or []) if x in NEUTRES]
        pal = (H.get(p) or {}).get('palette') or {}
        miss = [x for x in req if not pal.get(x)]
        if miss: W(r['_fichier'], f"palette.{', palette.'.join(miss)} absente(s) de {p}, exigée(s) par {m.get('id')}")
    return {'ok': not err, 'errors': err, 'warnings': warn, 'notes': notes,
            'counts': {'habillages': len(B.actifs()[0]), 'pates': len(B.actifs()[1]), 'fiches': len(H), 'mecaniques': len(M),
                       'formats': len(F), 'recettes': len(R), 'etiquettes': len(B.etiquettes())}}


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--briques':
        res = check_briques()
        (ROOT / 'out' / 'report' / 'qa-briques.json').write_text(json.dumps(res, indent=1, ensure_ascii=False))
        for e in res['errors']: print('ERREUR ', e)
        for w in res['warnings']: print('avert. ', w)
        print(f"briques : {'OK' if res['ok'] else 'FAIL'} ; {len(res['errors'])} erreurs, {len(res['warnings'])} avertissements ; {res['counts']}")
        sys.exit(0 if res['ok'] else 1)
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        res = [check(p) for p in sorted((ROOT / 'out' / 'shorts').iterdir()) if p.is_dir()]
        (ROOT / 'out' / 'report' / 'qa.json').write_text(json.dumps(res, indent=1, ensure_ascii=False))
        for r in res:
            st = r['briques'].get('statut')
            print(('OK  ' if r['ok'] else 'FAIL'), r['short'], f'[{st}] ' if st and st != 'validee' else '', '; '.join(r['errors'] + r['warnings']))
        print(f"{sum(r['ok'] for r in res)}/{len(res)} OK")
    else:
        print(json.dumps(check(sys.argv[1]), indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
