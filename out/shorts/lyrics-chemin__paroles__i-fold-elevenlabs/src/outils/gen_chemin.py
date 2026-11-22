#!/usr/bin/env python3
"""gen_chemin.py — mots horodatés (faster-whisper, plusieurs passes) -> fichier de paroles lyrics-chemin (format paroles.remplissage.json).

Reprend la structure du remplissage « Monday's Draft » (mêmes unités, arêtes, cadrages, types de transition, annotations) et
recalcule les temps sur un nouvel enregistrement du même texte.

    python3 gen_chemin.py --base paroles.remplissage.json --runs a.json b.json c.json --out chemin.json \
        --bpm 152 --shift -5.87 [--fix and#0=21.92] [--zoom-beats 8] [--end 34.7] [--report align.txt]

--shift : temps vidéo = temps audio + shift (pré-roulé moins point d'entrée). --fix : temps audio forcé d'un mot (mot#occurrence).
--end : fin de la musique en temps audio (la vidéo s'arrête là, ou après le zoom arrière + 1,2 s si c'est plus tard).
"""
import argparse, difflib, json, re, statistics

MERGE = False   # fusionner les cadrages trop courts : le groupe ne tient plus dans le cadre (règle 1), essai abandonné
LYR = ("i fold my day in draft mode i draw lines but not for show i've been up since 5 am printer down cuz no ink "
       "draft mode's my spare keys make another note txt and yet wrong fold such a lot of wrong folds").split()
# unités du remplissage -> nombre de mots chantés (dans l'ordre des lignes, titre exclu)
UNIT_WORDS = {"I FOLD": 2, "MY DAY": 2, "IN DRAFT MODE": 3, "I DRAW": 2, "LINES": 1, "BUT NOT": 2, "FOR SHOW": 2, "I'VE BEEN": 2,
              "UP SINCE": 2, "5 A.M.": 2, "PRINTER DOWN": 2, "CUZ NO INK": 3, "DRAFT MODE'S": 2, "MY SPARE KEYS": 3,
              "MAKE ANOTHER": 2, "NOTE.TXT": 2, "AND YET": 2, "WRONG": 1, "FOLD": 1, "SUCH A LOT": 3, "OF WRONG": 2, "FOLDS": 1}


def toks(run):
    out = []
    for seg in json.load(open(run)):
        for w in seg['words']:
            raw = w['w'].strip().lower().replace('’', "'")
            if raw.startswith('.') and out and raw.strip('.') in ('m', 'txt'):      # « a » + « .m. » ; « note » + « .txt. »
                piece = raw.strip('.')
                if piece == 'm' and out[-1]['t'] == 'a': out[-1]['t'] = 'am'; out[-1]['e'] = w['e']; continue
                out.append(dict(t=piece, s=w['s'], e=w['e'])); continue
            for p in re.split(r'[\s.]+', re.sub(r"[^a-z0-9'.\s]", '', raw)):
                p = p.strip("'")
                if not p: continue
                if p == '5am': out += [dict(t='5', s=w['s'], e=w['s'] + 0.2), dict(t='am', s=w['s'] + 0.2, e=w['e'])]; continue
                out.append(dict(t=p, s=w['s'], e=w['e']))
    return out


def align(run):
    """lyric index -> token. Matching words by difflib; a replaced block (sung word heard as another) is mapped by position."""
    T = toks(run)
    sm = difflib.SequenceMatcher(a=LYR, b=[x['t'] for x in T], autojunk=False)
    m = {}
    for op, i0, i1, j0, j1 in sm.get_opcodes():
        if op == 'equal':
            for k in range(i1 - i0): m[i0 + k] = T[j0 + k]
        elif op == 'replace':
            ni, nj = i1 - i0, j1 - j0
            if abs(ni - nj) > 1 or ni > 4: continue
            used = set()
            for k in range(ni):
                j = j0 + min(nj - 1, round(k * nj / ni))
                if j in used: continue
                used.add(j); m[i0 + k] = dict(T[j], weak=True)
    # mots collés (début identique au voisin) ou de durée nulle : inutilisables (les deux)
    bad = set()
    for i in m:
        x = m[i]
        if x['e'] - x['s'] < 0.03: bad.add(i)
        if i + 1 in m and abs(m[i + 1]['s'] - x['s']) < 0.03: bad |= {i, i + 1}
    for i in bad: m.pop(i, None)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True); ap.add_argument('--runs', nargs='+', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--bpm', type=float, required=True); ap.add_argument('--shift', type=float, default=0.0)
    ap.add_argument('--fix', action='append', default=[]); ap.add_argument('--zoom-beats', type=float, default=4)
    ap.add_argument('--end', type=float, help='fin de la musique (temps audio)'); ap.add_argument('--report')
    ap.add_argument('--note', default=''); ap.add_argument('--tail', type=float, default=1.0)
    a = ap.parse_args()
    B = json.load(open(a.base)); BEAT = 60 / a.bpm
    runs = [align(r) for r in a.runs]
    occ, fixes = {}, {}
    for f in a.fix:
        k, v = f.split('='); fixes[k] = float(v)
    starts, ends, rep = [], [], []
    for i, w in enumerate(LYR):
        n = occ.get(w, 0); occ[w] = n + 1; key = f'{w}#{n}'
        cs = [r[i]['s'] for r in runs if i in r]; ce = [r[i]['e'] for r in runs if i in r]
        if i in runs[0]:   # la première passe (avec les paroles en amorce) sert de référence : une autre passe à plus de 0,6 s est écartée
            ref = runs[0][i]['s']; keep = [k for k, c in enumerate(cs) if abs(c - ref) <= 0.6]
            cs = [cs[k] for k in keep]; ce = [ce[k] for k in keep]
        if key in fixes: s, src = fixes[key], 'fix'
        elif cs: s, src = statistics.median(cs), 'median'
        else: s, src = None, 'missing'
        starts.append(s); ends.append(statistics.median(ce) if ce else None)
        rep.append(f'{key:12s} {" ".join(f"{c:6.2f}" for c in cs):24s} spread {max(cs) - min(cs) if cs else 0:4.2f}  -> {s if s is None else round(s, 2)} ({src})')
    for i in range(len(LYR)):          # trous : interpolation
        if starts[i] is None:
            j = next((k for k in range(i + 1, len(LYR)) if starts[k] is not None), None)
            if j is None: starts[i] = starts[i - 1] + 0.25; ends[i] = None; continue
            starts[i] = starts[i - 1] + (starts[j] - starts[i - 1]) / (j - i + 1)
    for i in range(len(LYR)):
        if ends[i] is None or ends[i] <= starts[i]: ends[i] = starts[i] + 0.25
    for i in range(1, len(LYR)): starts[i] = max(starts[i], starts[i - 1] + 0.06)
    V = lambda t: round(t + a.shift, 3)

    # ---------- unités ----------
    wi = 0; lines = []
    for L in B['lignes']:
        L = json.loads(json.dumps(L))
        if L['arete'] == 'titre': lines.append(L); continue
        us = []
        for u in L['u']:
            n = UNIT_WORDS[u[0]]; us.append([u[0], wi, wi + n]); wi += n
        L['_w'] = us; lines.append(L)
    assert wi == len(LYR)
    nxt_attack = lambda k: starts[k] if k < len(LYR) else 1e9
    for L in lines:
        if L['arete'] == 'titre': continue
        new = []
        for j, (txt, w0, w1) in enumerate(L['_w']):
            t = V(starts[w0])
            if j + 1 < len(L['_w']): e = V(starts[L['_w'][j + 1][1]])
            else: e = V(min(ends[w1 - 1], nxt_attack(w1) - 0.12)); e = max(e, t + 0.3)
            new.append([txt, t, round(e, 3)])
        L['u'] = new
    # cadrages : ceux du remplissage ; si l'un tient moins de 0,55 s, on essaie les autres découpages contigus dont aucun groupe
    # n'est plus long (en caractères) que le plus long groupe du remplissage (il tient alors dans le cadre) ; on garde celui
    # dont le groupe le plus court dure le plus longtemps.
    def parts(n):
        if n == 1: yield [[0]]; return
        for p in parts(n - 1):
            yield p[:-1] + [p[-1] + [n - 1]]; yield p + [[n - 1]]
    span = lambda L, g: L['u'][g[-1]][2] - L['u'][g[0]][1]
    chars = lambda L, g: len(' '.join(L['u'][i][0] for i in g))
    for L in lines:
        if L['arete'] == 'titre': continue
        if min(span(L, g) for g in L['cad']) >= 0.55: continue
        cmax = max(chars(L, g) for g in L['cad'])
        best = max((p for p in parts(len(L['u'])) if all(chars(L, g) <= cmax for g in p)), key=lambda p: (min(span(L, g) for g in p), -len(p)))
        if best != L['cad']: L['cad'] = best; L.pop('glide', None)

    # ---------- titre ----------
    first = next(L for L in lines if L['arete'] != 'titre')
    a0 = first['u'][0][1]
    T = lines[0]
    win = a0 - 0.2 - 1.0 * BEAT                  # le titre se lit jusqu'au départ du fouetté
    T['u'] = [["MONDAY'S", 0, round(win * 0.5, 3)], ["DRAFT", round(win * 0.5, 3), round(win + 0.25, 3)]]
    T['glide'] = [min(0.26, win * 0.15)]
    if win < 2.0: T['cad'] = [[0, 1]]; T.pop('glide')   # fenêtre courte : le titre entier dans un seul cadrage
    # ---------- arrivées de chaque ligne ----------
    prev = T
    for L in lines[1:]:
        pu = prev['u'][-1]; leave = pu[1] + 0.6 * (pu[2] - pu[1]) + 0.02
        g = prev['cad'][-1]; u0 = prev['u'][g[0]]
        if len(prev['cad']) == 1: parr = prev['arr']           # arrivée (estimée) du dernier cadrage de la ligne précédente
        else: nw = sum(UNIT_WORDS.get(prev['u'][i][0], 1) for i in [g[0]]); parr = u0[1] - (BEAT / 2 if (u0[2] - u0[1]) / nw < 0.30 else 0.06)
        target = max(leave, parr + 0.5)                       # règle 3 : ce cadrage tenu 0,5 s si possible
        att = L['u'][0][1]; want = L.get('temps', 1) * BEAT
        arr = att - 0.19
        if arr - want < target: arr = min(att - 0.02, target + want)
        dur = max(0.15, min(want, arr - leave, max(0.6 * BEAT, arr - target)))
        L['arr'] = round(arr, 3); L['temps'] = round(dur / BEAT, 3)
        if 'annotation' in L:   # décalée avec l'attaque de sa ligne
            old = next(x for x in B['lignes'] if x['arete'] == L['arete'])
            L['annotation']['t'] = round(L['annotation']['t'] - old['u'][0][1] + att, 3)
        prev = L
    # ---------- respiration (recul après « AND YET ») ----------
    R = dict(B['respiration']); fan = next(L for L in lines if L['arete'] == 'fanion'); pg = next(L for L in lines if L['arete'] == 'pontG')
    fu = fan['u'][-1]; leave = fu[1] + 0.6 * (fu[2] - fu[1]) + 0.02
    arriv = pg['arr'] - pg['temps'] * BEAT - 0.15
    rd = min(4 * BEAT, arriv - leave)
    resp = None
    if rd >= 1.2 * BEAT: R['arrivee'] = round(arriv, 3); R['temps'] = round(rd / BEAT, 3); resp = R
    # ---------- zoom arrière et fin ----------
    last = lines[-1]['u'][-1][2]
    z0 = round(last + 0.3, 3)
    end_audio = V(a.end) if a.end else z0 + a.zoom_beats * BEAT + 1.2
    zb = a.zoom_beats
    while zb > 4 and z0 + zb * BEAT + 1.2 > end_audio: zb -= 1
    z1 = round(z0 + zb * BEAT, 3)
    duree = round(max(end_audio, z1 + a.tail), 3)
    for L in lines: L.pop('_w', None)
    out = {"note": a.note, "titre": B['titre'], "langue": "en", "sens": "ltr", "bpm": a.bpm, "t0": 0, "duree": duree, "dessin": B['dessin'],
           "zoomArriere": [z0, z1], **({"respiration": resp} if resp else {}), "lignes": lines, "refrain": {"u": [], "rangs": []}}
    s = json.dumps(out, ensure_ascii=False, indent=1)
    s = re.sub(r'\[\s+("[^"]*"|\d[\d.]*),\s+([\d.]+),\s+([\d.]+)\s+\]', r'[\1, \2, \3]', s)
    open(a.out, 'w').write(s)
    if a.report: open(a.report, 'w').write('\n'.join(rep) + '\n')
    print('\n'.join(rep)); print(f'duree {duree}  zoom {z0}-{z1}  respiration {resp and (resp["arrivee"], resp["temps"])}')


if __name__ == '__main__':
    main()
