#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""lyrics_align.py — paroles exactes + mots horodatés -> lyrics.json pour l'identité Lyrics punchy.

Étapes 3 à 7 de out/report/notes/lyrics-punchy/pipeline.md : alignement sur le texte exact (difflib), grille des temps,
accents, unités et rangs, déclencheurs et règles de densité ; puis validation des règles de lisibilité (concept.md § 6 et § 8).
Bibliothèque standard seulement.

    python3 out/tools/lyrics_align.py --paroles paroles.txt --mots transcription-mots.json --out lyrics.json \
        --bpm 154.5 --t0 0 --duree 19.5 --titre "CLAUDE'S PLAN" [--source main] [--artiste …] [--langue en]
    python3 out/tools/lyrics_align.py --valider lyrics.json        # validation seule

Format de paroles.txt : une ligne chantée par ligne ; une ligne « # <id-section> <camaieu> » ouvre une section
(camaïeu : nuit, lagon, braise). Suffixe facultatif « | carton +N » : décale de N temps le carton déclenché par la ligne
(décision de relecture, marquée source « main »).
Format des mots horodatés (faster-whisper) : [{start, end, text, words: [{w, s, e}]}].
"""
import argparse, difflib, json, math, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRIGGERS = ROOT / 'out' / 'shared' / 'lyrics-moteur' / 'triggers.json'
FPS = 30
SNAP = 0.07            # un mot à moins de 70 ms d'une croche est ramené sur la croche
LONG = 0.8             # un mot de plus de 0,8 s commence 0,3 s avant sa fin (Whisper étale les mots sur les silences)
MIN_UNIT = 0.25        # durée minimale d'une unité avant la suivante
MAX_UNITS, MAX_RANGS, MAX_PER_RANG = 6, 3, 3
DENSITY = 2.5          # au moins 2,5 s entre deux débuts de visuel
CARTON_MIN, CARTON_MAX = 0.8, 2.5
# articles, prépositions, pronoms, conjonctions de 3 lettres ou moins : se collent au mot suivant
SMALL = set('''i a an the my in on at of to for but not and or cuz its it's i've i'm we you me so by up is our your her his
le la les l un une des de du d en a au aux et ou je j tu il on ne ma mon mes ta ton tes sa son ses ce ca qui que qu nos vos'''.split())


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def norm(w):
    """minuscules, sans accent, sans ponctuation (le point est gardé entre deux caractères : 2.0, .md)."""
    w = strip_accents(w.lower()).replace('’', "'")
    w = re.sub(r"[^a-z0-9.']", '', w)
    w = w.strip("'")
    w = re.sub(r'\.+$', '', w)
    return w


def norm_match(w):
    """forme de recherche des déclencheurs : sans apostrophe ni possessif « 's »."""
    w = norm(w)
    w = re.sub(r"'s$", '', w)
    return w.replace("'", '')


def is_small(w):
    n = norm(w)
    return n in SMALL or n.replace("'", '') in SMALL


def load_mots(path, duree):
    segs = json.load(open(path))
    words = [dict(w=w['w'].strip(), s=float(w['s']), e=float(w['e'])) for seg in segs for w in seg['words']]
    out = []
    for w in words:                               # « 2 » + « .0, » -> « 2.0, » ; « another » + « .md, »
        if out and w['w'].startswith('.') and len(w['w']) > 1:
            out[-1]['w'] += w['w']; out[-1]['e'] = w['e']
        else:
            out.append(w)
    for w in out:
        if w['e'] - w['s'] > LONG:
            w['s'] = round(w['e'] - 0.3, 3)
    return [w for w in out if w['s'] < duree + 2]


def load_paroles(path):
    sections, lines, cur = [], [], None
    for raw in open(path, encoding='utf-8'):
        raw = raw.rstrip('\n')
        if not raw.strip():
            continue
        if raw.startswith('#'):
            parts = raw[1:].split()
            cur = dict(id=parts[0], camaieu=parts[1] if len(parts) > 1 else 'nuit')
            sections.append(cur)
            continue
        shift = 0
        if '|' in raw:
            raw, opt = raw.split('|', 1)
            m = re.search(r'carton\s*([+-]\d+)', opt)
            shift = int(m.group(1)) if m else 0
        if cur is None:
            cur = dict(id='section-1', camaieu='nuit'); sections.append(cur)
        lines.append(dict(section=cur['id'], words=raw.split(), cartonShift=shift))
    return sections, lines


def align(lines, mots, source_label):
    """horaire de chaque mot des paroles exactes (difflib sur les formes normalisées)."""
    P = [(li, wi, w) for li, l in enumerate(lines) for wi, w in enumerate(l['words'])]
    pn = [norm(w) for _, _, w in P]
    wn = [norm(m['w']) for m in mots]
    times = [None] * len(P)
    src = [None] * len(P)
    sm = difflib.SequenceMatcher(None, pn, wn, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                times[i1 + k] = (mots[j1 + k]['s'], mots[j1 + k]['e']); src[i1 + k] = source_label
        elif tag == 'replace':                    # ex. « Plano » -> « plan mode » : l'empan de Whisper réparti au prorata des lettres
            s, e = mots[j1]['s'], mots[j2 - 1]['e']
            chars = [max(1, len(pn[i])) for i in range(i1, i2)]
            tot, acc = sum(chars), 0
            for k, i in enumerate(range(i1, i2)):
                a = s + (e - s) * acc / tot; acc += chars[k]
                times[i] = (round(a, 3), round(s + (e - s) * acc / tot, 3)); src[i] = 'reparti'
    # mots sans horaire (insertions) : répartis entre leurs voisins
    i = 0
    while i < len(P):
        if times[i] is None:
            j = i
            while j < len(P) and times[j] is None:
                j += 1
            a = times[i - 1][1] if i > 0 else (times[j][0] - 0.3 * (j - i) if j < len(P) else 0.0)
            b = times[j][0] if j < len(P) else a + 0.3 * (j - i)
            chars = [max(1, len(pn[k])) for k in range(i, j)]
            tot, acc = sum(chars), 0
            for k in range(i, j):
                s0 = a + (b - a) * acc / tot; acc += chars[k - i]
                times[k] = (round(s0, 3), round(a + (b - a) * acc / tot, 3)); src[k] = 'reparti'
            i = j
        else:
            i += 1
    # horaires croissants
    last = -1.0
    for k in range(len(P)):
        s, e = times[k]
        if s <= last:
            s = round(last + 0.01, 3)
        times[k] = (s, max(e, s + 0.05)); last = s
    out = [[] for _ in lines]
    for k, (li, wi, w) in enumerate(P):
        out[li].append(dict(w=w, s=times[k][0], e=times[k][1], source=src[k]))
    return out


class Grid:
    def __init__(self, bpm, t0, tpm):
        self.beat = 60.0 / bpm; self.t0 = t0; self.tpm = tpm

    def beat_of(self, t):
        return (t - self.t0) / self.beat

    def t_of(self, b):
        return round(self.t0 + b * self.beat, 3)

    def snap(self, t):
        e = round(self.beat_of(t) * 2) / 2
        return self.t_of(e) if abs(self.t_of(e) - t) < SNAP else round(t, 3)

    def on_beat(self, t):
        b = round(self.beat_of(t))
        return abs(self.t_of(b) - t) < SNAP, b

    def ceil_beat(self, t):
        return self.t_of(math.ceil(self.beat_of(t) - 1e-6))


def load_triggers():
    tr = json.load(open(TRIGGERS))['triggers']
    exprs = []
    for t in tr:
        for m in t['match']:
            exprs.append((m.split(), t))
    exprs.sort(key=lambda x: -len(x[0]))          # expressions longues d'abord
    return exprs


def tokens_of(line_words, exprs):
    """regroupe les expressions de plusieurs mots en un seul jeton, et note les déclencheurs."""
    toks, i = [], 0
    nm = [norm_match(w['w']) for w in line_words]
    while i < len(line_words):
        hit = None
        for ws, t in exprs:
            if nm[i:i + len(ws)] == ws:
                hit = (ws, t); break
        n = len(hit[0]) if hit else 1
        part = line_words[i:i + n]
        toks.append(dict(words=part, trig=hit[1] if hit else None, expr=n > 1))
        i += n
    return toks


def units_of(toks):
    units, i = [], 0
    while i < len(toks):
        grp = [toks[i]]
        if not toks[i]['expr'] and len(toks[i]['words']) == 1 and is_small(toks[i]['words'][0]['w']) and i + 1 < len(toks):
            grp.append(toks[i + 1]); i += 1
        i += 1
        words = [w for g in grp for w in g['words']]
        trig = next((g['trig'] for g in grp if g['trig']), None)
        units.append(dict(words=words, trig=trig))
    # débit : une unité doit durer au moins 0,25 s avant la suivante, sinon on la regroupe avec la précédente
    k = 1
    while k < len(units):
        if units[k]['words'][0]['s'] - units[k - 1]['words'][0]['s'] < MIN_UNIT:
            units[k - 1]['words'] += units[k]['words']
            units[k - 1]['trig'] = units[k - 1]['trig'] or units[k]['trig']
            del units[k]
        else:
            k += 1
    return units


def rangs_of(n):
    if n <= MAX_RANGS:
        return list(range(n))
    per = math.ceil(n / MAX_RANGS)
    per = max(2, min(MAX_PER_RANG, per))
    return [min(MAX_RANGS - 1, i // per) for i in range(n)]


def build(args):
    grid = Grid(args.bpm, args.t0, 4)
    sections, plines = load_paroles(args.paroles)
    mots = load_mots(args.mots, args.duree)
    aligned = align(plines, mots, args.source)
    exprs = load_triggers()
    lignes = []
    for pl, words in zip(plines, aligned):
        for w in words:
            w['s'] = grid.snap(w['s'])
        if words[0]['s'] >= args.duree:
            continue
        units = units_of(tokens_of(words, exprs))
        chunks = [units] if len(units) <= MAX_UNITS else [units[:len(units) // 2], units[len(units) // 2:]]
        for ch in chunks:
            lignes.append(dict(section=pl['section'], shift=pl['cartonShift'], units=ch))
    # titre sur le passage sans voix : un mot par mesure, coup sur chaque premier temps
    first = lignes[0]['units'][0]['words'][0]['s']
    out_sections, out_lines = [], []
    intro_end = 0.0
    if args.titre and first >= grid.beat * grid.tpm:
        tw = args.titre.upper().split()
        intro_end = grid.t_of(math.floor(grid.beat_of(first - 2 / FPS)))
        out_sections.append(dict(id='intro', debut=0.0, fin=intro_end, camaieu=args.camaieu_intro))
        us = [dict(texte=w, t=grid.t_of(i * grid.tpm), fin=grid.t_of((i + 1) * grid.tpm), accent=2, rang=i if len(tw) <= 3 else i // 2,
                   source='main') for i, w in enumerate(tw[:MAX_UNITS])]
        out_lines.append(dict(section='intro', debut=0.0, fin=intro_end, unites=us))
    # sections : début sur le temps qui précède la première unité (moins 2 images d'entrée)
    sec_start = {}
    for L in lignes:
        if L['section'] not in sec_start:
            sec_start[L['section']] = grid.t_of(math.floor(grid.beat_of(L['units'][0]['words'][0]['s'] - 2 / FPS)))
    if out_sections:
        out_sections[0]['fin'] = min(out_sections[0]['fin'], sec_start[lignes[0]['section']])
        out_lines[0]['fin'] = out_sections[0]['fin']
    order = [s for s in sections if s['id'] in sec_start]
    for i, s in enumerate(order):
        fin = sec_start[order[i + 1]['id']] if i + 1 < len(order) else args.duree
        out_sections.append(dict(id=s['id'], debut=sec_start[s['id']], fin=fin, camaieu=s['camaieu']))
    # accents, rangs, horaires d'unités
    for li, L in enumerate(lignes):
        nxt = lignes[li + 1]['units'][0]['words'][0]['s'] if li + 1 < len(lignes) else args.duree
        us = []
        for ui, u in enumerate(L['units']):
            t = u['words'][0]['s']
            fin = L['units'][ui + 1]['words'][0]['s'] if ui + 1 < len(L['units']) else min(nxt, max(w['e'] for w in u['words']) + 0.4)
            ob, b = grid.on_beat(t)
            acc = (2 if b % grid.tpm == 0 else 1) if ob else 0
            srcs = {w['source'] for w in u['words']}
            us.append(dict(texte=' '.join(w['w'] for w in u['words']).upper(), t=t, fin=round(fin, 3), accent=acc,
                           source='whisper' if srcs == {'whisper'} else ('main' if srcs == {'main'} else 'reparti'),
                           _trig=u['trig']))
        for u, r in zip(us, rangs_of(len(us))):
            u['rang'] = r
        out_lines.append(dict(section=L['section'], debut=us[0]['t'], fin=round(nxt, 3), unites=us, _shift=L['shift']))
    # déclencheurs : un par ligne au plus, priorité la plus haute ; densité (2,5 s entre débuts, jamais deux visuels)
    prev_start, prev_end = -99.0, -99.0
    for L in out_lines:
        cands = [(ui, u['_trig']) for ui, u in enumerate(L['unites']) if u.get('_trig')]
        if not cands:
            continue
        top = max(c[1]['priorite'] for c in cands)
        cands = [c for c in cands if c[1]['priorite'] == top]
        need = max(prev_start + DENSITY, prev_end)
        ok = [c for c in cands if L['unites'][c[0]]['t'] >= need]
        ui, trig = ok[0] if ok else cands[0]
        u = L['unites'][ui]
        debut, src = u['t'], None
        if debut < need:
            debut = grid.ceil_beat(need); src = 'densite'
        if L.get('_shift'):
            debut = round(debut + L['_shift'] * grid.beat, 3); src = 'main'
        if trig['type'] != 'carton':
            print(f"! déclencheur {trig['id']} de type {trig['type']} : non rendu par le moteur v1", file=sys.stderr)
        fin = grid.ceil_beat(debut + trig['temps'] * grid.beat)
        fin = min(max(fin, debut + CARTON_MIN), debut + CARTON_MAX)
        if L is out_lines[-1] and args.duree - debut <= CARTON_MAX:
            fin = args.duree                        # dernier carton tenu jusqu'à la fin
        d = dict(id=trig['id'], type=trig['type'], dessin=trig['dessin'], debut=round(debut, 3), fin=round(fin, 3), temps=trig['temps'])
        if src:
            d['source'] = src
        u['declencheur'] = d
        u['accent'] = 2
        prev_start, prev_end = debut, fin
    # au plus un accent 2 par mesure (on garde le déclencheur, sinon le premier)
    seen = {}
    for L in out_lines:
        for u in L['unites']:
            if u['accent'] == 2:
                m = int((grid.beat_of(u['t']) + 1e-2) // grid.tpm)
                if m in seen:
                    keep_new = 'declencheur' in u and 'declencheur' not in seen[m]
                    loser = seen[m] if keep_new else u
                    loser['accent'] = 1
                    if keep_new:
                        seen[m] = u
                else:
                    seen[m] = u
    for L in out_lines:
        L.pop('_shift', None)
        for u in L['unites']:
            u.pop('_trig', None)
    data = dict(titre=args.titre_morceau or args.titre or '', artiste=args.artiste or '', langue=args.langue,
                bpm=args.bpm, t0=args.t0, tempsParMesure=4, duree=args.duree, sections=out_sections, lignes=out_lines)
    return data


def valider(d):
    """règles de lisibilité et de densité ; renvoie (erreurs, avertissements, mesures)."""
    err, warn = [], []
    vis = []
    for li, L in enumerate(d['lignes']):
        us = L['unites']
        if len(us) > MAX_UNITS: err.append(f'ligne {li} : {len(us)} unités > {MAX_UNITS}')
        rangs = {}
        for u in us:
            rangs.setdefault(u['rang'], []).append(u)
        if len(rangs) > MAX_RANGS: err.append(f'ligne {li} : {len(rangs)} rangs')
        for r, x in rangs.items():
            if len(x) > MAX_PER_RANG: err.append(f'ligne {li} rang {r} : {len(x)} unités')
        for a, b in zip(us, us[1:]):
            if b['t'] - a['t'] < MIN_UNIT - 1e-6: err.append(f"ligne {li} : « {a['texte']} » {b['t'] - a['t']:.2f} s < {MIN_UNIT}")
        if li + 1 < len(d['lignes']):
            vif = d['lignes'][li + 1]['unites'][0]['t'] - us[-1]['t']
            if vif < 0.4: warn.append(f'ligne {li} : dernière unité vive {vif:.2f} s < 0,4 s')
        for u in us:
            if len(u['texte'].replace(' ', '')) <= 1: err.append(f"unité d'une lettre : {u['texte']}")
            if 'declencheur' in u: vis.append(u['declencheur'])
    vis.sort(key=lambda v: v['debut'])
    for a, b in zip(vis, vis[1:]):
        if b['debut'] - a['debut'] < DENSITY - 1e-6: err.append(f"cartons {a['id']} -> {b['id']} : {b['debut'] - a['debut']:.2f} s < {DENSITY}")
        if b['debut'] < a['fin'] - 1e-6: err.append(f"deux visuels en même temps : {a['id']} et {b['id']}")
    tot = sum(v['fin'] - v['debut'] for v in vis)
    if tot > d['duree'] / 2: err.append(f'visuels {tot:.1f} s > moitié de {d["duree"]} s')
    for v in vis:
        if not (CARTON_MIN - 1e-6 <= v['fin'] - v['debut'] <= CARTON_MAX + 1e-6): err.append(f"carton {v['id']} dure {v['fin'] - v['debut']:.2f} s")
    beat = 60 / d['bpm']
    deux = {}
    for L in d['lignes']:
        for u in L['unites']:
            if u['accent'] == 2:
                m = int(((u['t'] - d['t0']) / beat + 1e-2) // d['tempsParMesure'])
                if m in deux: err.append(f"deux accents 2 dans la mesure {m} : {deux[m]} / {u['texte']}")
                deux[m] = u['texte']
    mes = dict(lignes=len(d['lignes']), unites=sum(len(L['unites']) for L in d['lignes']),
               ecartsCartons=[round(b['debut'] - a['debut'], 2) for a, b in zip(vis, vis[1:])],
               cartons=[(v['id'], v['debut'], v['fin']) for v in vis], partVisuels=round(tot / d['duree'], 2))
    return err, warn, mes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--paroles'); ap.add_argument('--mots'); ap.add_argument('--out')
    ap.add_argument('--bpm', type=float, default=120.0); ap.add_argument('--t0', type=float, default=0.0)
    ap.add_argument('--duree', type=float, default=19.5)
    ap.add_argument('--titre', help='titre affiché sur le passage sans voix du début (un mot par mesure)')
    ap.add_argument('--titre-morceau'); ap.add_argument('--artiste'); ap.add_argument('--langue', default='fr')
    ap.add_argument('--camaieu-intro', default='nuit')
    ap.add_argument('--source', default='whisper', help='étiquette des horaires appariés (whisper, ou main pour des horaires écrits à la main)')
    ap.add_argument('--valider')
    a = ap.parse_args()
    if a.valider:
        d = json.load(open(a.valider))
    else:
        d = build(a)
        Path(a.out).write_text(json.dumps(d, ensure_ascii=False, indent=1))
        print('écrit', a.out)
    err, warn, mes = valider(d)
    print(json.dumps(dict(ok=not err, erreurs=err, avertissements=warn, mesures=mes), ensure_ascii=False, indent=1))
    sys.exit(1 if err else 0)


if __name__ == '__main__':
    main()
