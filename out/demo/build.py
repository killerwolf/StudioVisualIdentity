#!/usr/bin/env python3
"""
build.py — vidéo démo « 14 styles » (≈ 51 s), en 16:9 (1920×1080) et 9:16 (1080×1920).

USAGE (depuis la racine du dépôt)
  .venv/bin/python out/demo/build.py layout            # écrit out/demo/layout.json (géométrie + timeline, lue par overlay.html)
  .venv/bin/python out/demo/build.py base 16x9|9x16    # mosaïque des 14 vraies vidéos (+ épisode « résultat ») -> /tmp/svi/demo/base_<fmt>.mp4
  node out/tools/render.mjs out/demo/overlay.html --query fmt=16x9 --width 1920 --height 1080 --duration 60 --alpha --out /tmp/svi/demo/overlay_16x9.mov
  .venv/bin/python out/demo/build.py audio             # mix : son des vignettes par paliers (1,2,3,5,12), voix off, SFX, musiques
  .venv/bin/python out/demo/build.py final 16x9|9x16   # base + overlay + audio -> out/demo/demo_<fmt>.mp4
  .venv/bin/python out/demo/build.py gif               # aperçu muet pour le README -> out/demo/demo_preview.gif
  .venv/bin/python out/demo/build.py all               # tout, dans l'ordre (overlay compris)

Voix off : Fish Audio « Energetic Male » (802e3bc2b27e49c2995d23ef70e6ac89), modèle drama-3, lignes dans voice_en/NN.mp3
(texte et indications de jeu dans narration.json). Variantes non utilisées : voice_alt/.
"""
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TMP = Path('/tmp/svi/demo')
SHORTS = ROOT / 'out' / 'shorts'

# ---- timeline (secondes) ----
CUT = 3.2                     # fin de l'accroche (la question est dite à 3,0 s)
C0, CD = 7.4, 2.0             # début et durée des cycles audio (brouhaha : 10 s en tout)
COUNTS = [1, 2, 3, 5, 12]     # vignettes audibles par cycle
CEND = C0 + CD * len(COUNTS)  # 17.4
TERM = CEND + 2.0             # terminal + prompt (19.4)
RES0 = TERM + 7.6             # épisodes produits (27.0)
# épisodes montrés dans le téléphone : (dossier du short, nom du style, voix (brouhaha/NN.mp3) ou None = son original, durée)
# épisode 1 = son original (Arnold) ; 2-4 = une autre voix française qui lit le MÊME texte que la vidéo (sa 1re ligne)
EPISODES = [('swiss-data__geographie__ou-vivent-8-milliards', 'Swiss Grid', None, 4.3),
            ('cosmos-doc__evenements__voyager-1-a-un-jour-lumiere', 'Cosmos Doc', '07', 3.5),
            ('brut-meme__engagement__test-des-3-secondes-stroop', 'Brut Meme', '02', 3.9),
            ('neon-lab__explicatif__lune-meme-face', 'Neon Lab', '05', 3.4)]
EP_T = [round(RES0 + sum(e[3] for e in EPISODES[:k]), 2) for k in range(len(EPISODES) + 1)]
RES1 = EP_T[-1]               # 42.1
SLAM = RES1
SLAMS = [round(SLAM + d, 2) for d in (0.15, 1.99, 3.85)]  # « Fourteen styles! » « Thirty-one videos! » « Open source! » (pauses mesurées)
END = round(SLAM + 5.7, 2)
DUR = round(END + 3.6, 2)
# (instant, fichier, gain) — gains pour l'arc de ton : chuchotement (02) très bas à l'origine, cri (04) très haut
VOICE = [(0.15, '00', 1.6), (3.4, '01', 1.7), (CEND + 0.3, '02', 9.0), (TERM + 0.1, '03', 1.9), (SLAM + 0.1, '04', 1.3), (END + 0.1, '05', 1.6)]
CUES = {'hookLine2': 1.73, 'noneAlike': 5.44, 'typeStart': TERM + 0.5, 'typeEnd': TERM + 4.8,
        'checks': [TERM + 5.2, TERM + 5.9, TERM + 6.6]}

# mosaïque : ordre d'affichage (alternance clair / sombre) et ordre d'apparition du son
TILES = [
    ('gazette-1900', 'gazette-1900__histoire__1789-en-20-secondes', 'Gazette 1900'),
    ('neon-lab', 'neon-lab__explicatif__lune-meme-face', 'Neon Lab'),
    ('pastel-diorama', 'pastel-diorama__engagement__choisis-ta-boite-renard', 'Pastel Diorama'),
    ('pixel-arcade', 'pixel-arcade__engagement__quelle-bille-gagne-la-course', 'Pixel Arcade'),
    ('swiss-data', 'swiss-data__evenements__j-272-eclipse-2-aout-2027', 'Swiss Grid'),
    ('cosmos-doc', 'cosmos-doc__evenements__voyager-1-a-un-jour-lumiere', 'Cosmos Doc'),
    ('riso-zine', 'riso-zine__geographie__5-plus-grands-deserts', 'Riso Zine'),
    ('tableau-craie', 'tableau-craie__explicatif__pourquoi-le-ciel-est-bleu', 'Chalkboard'),
    ('bauhaus-kinetic', 'bauhaus-kinetic__engagement__trouve-l-intrus', 'Bauhaus Kinetic'),
    ('liquid-chrome', 'liquid-chrome__abstrait__pendule-de-newton-chrome', 'Liquid Chrome'),
    ('aquarelle-conte', 'aquarelle-conte__enfants__ou-vont-les-etoiles-le-jour', 'Watercolor Tale'),
    ('brut-meme', 'brut-meme__engagement__test-des-3-secondes-stroop', 'Brut Meme'),
    ('atlas-grave', 'atlas-grave__histoire__premier-tour-du-monde-1519-1522', 'Engraved Atlas'),
    ('topo-relief', 'topo-relief__geographie__comment-mesure-t-on-l-everest', 'Topo Relief'),
]
AUDIBLE = ['gazette-1900', 'pixel-arcade', 'brut-meme', 'pastel-diorama', 'swiss-data', 'neon-lab',
           'tableau-craie', 'cosmos-doc', 'aquarelle-conte', 'riso-zine', 'atlas-grave', 'topo-relief']


def audible_from(ident):
    """Instant où la vignette devient audible (None = jamais)."""
    if ident not in AUDIBLE:
        return None
    k = AUDIBLE.index(ident)
    for c, n in enumerate(COUNTS):
        if k < n:
            return C0 + c * CD
    return None


def layouts():
    L = {}
    # 16:9 : 7 × 2 vignettes 9:16 (274 × 487), centrées verticalement
    tw, th = 274, 487
    x0, y0 = (1920 - 7 * tw) // 2, (1080 - 2 * th) // 2
    L['16x9'] = {'W': 1920, 'H': 1080, 'tile': [tw, th],
                 'cells': [[x0 + (i % 7) * tw, y0 + (i // 7) * th] for i in range(14)],
                 'empty': [], 'result': [1240, 80, 520, 924], 'terminal': [110, 150, 1060, 640]}
    # 9:16 : 4 × 4 vignettes (270 × 480) ; les cellules 5 et 6 (centre) accueillent la carte titre
    tw, th = 270, 480
    order = [i for i in range(16) if i not in (5, 6)]
    L['9x16'] = {'W': 1080, 'H': 1920, 'tile': [tw, th],
                 'cells': [[(i % 4) * tw, (i // 4) * th] for i in order],
                 'empty': [[270, 480, 540, 480]], 'result': [190, 360, 700, 1244], 'terminal': [70, 420, 880, 900]}
    return L


def write_layout():
    idx = {i['id']: i for i in json.load(open(ROOT / 'out/identities/index.json'))['identities']}
    tiles = []
    for ident, d, name in TILES:
        c = idx[ident]['coreTokens']['color']
        tiles.append({'id': ident, 'dir': d, 'name': name, 'bg': c['bg'], 'accent': (c['accent'] or ['#ffffff'])[0],
                      'audibleFrom': audible_from(ident)})
    lay = {'timeline': {'CUT': CUT, 'C0': C0, 'CD': CD, 'COUNTS': COUNTS, 'CEND': CEND, 'TERM': TERM,
                        'RES0': RES0, 'RES1': RES1, 'SLAM': SLAM, 'END': END, 'DUR': DUR,
                        'SLAMS': SLAMS, 'CUES': CUES, 'voice': [{'t': t, 'file': f} for t, f, g in VOICE],
                        'EPS': [{'t0': EP_T[k], 't1': EP_T[k + 1], 'name': e[1], 'dir': e[0],
                                 'accent': next((x['accent'] for x in tiles if x['dir'].split('__')[0] == e[0].split('__')[0]), '#E3241B')}
                                for k, e in enumerate(EPISODES)]},
           'tiles': tiles, 'formats': layouts(),
           'url': 'github.com/killerwolf/StudioVisualIdentity'}
    json.dump(lay, open(HERE / 'layout.json', 'w'), ensure_ascii=False, indent=1)
    print('layout.json écrit')
    return lay


def run(cmd):
    print('+', ' '.join(map(str, cmd))[:300], file=sys.stderr)
    subprocess.run(list(map(str, cmd)), check=True)


def base(fmt):
    lay = write_layout()
    F = lay['formats'][fmt]
    tw, th = F['tile']
    TMP.mkdir(parents=True, exist_ok=True)
    inputs, fc = [], []
    for i, t in enumerate(lay['tiles']):
        inputs += ['-stream_loop', '-1', '-i', SHORTS / t['dir'] / 'short.mp4']
        fc.append(f'[{i}:v]trim=0:{DUR - CUT:.2f},setpts=PTS-STARTPTS,fps=30,scale={tw}:{th}:flags=lanczos,setsar=1,'
                  f'tpad=start_duration={CUT}:start_mode=clone[t{i}]')
    n = len(lay['tiles'])
    canvas = f'color=c=0x0b0b14:s={F["W"]}x{F["H"]}:r=30:d={DUR}'
    fc.append(f'{canvas}[bg0]')
    last = 'bg0'
    for i, (x, y) in enumerate(F['cells']):
        fc.append(f'[{last}][t{i}]overlay={x}:{y}:shortest=0:eof_action=pass[b{i}]')
        last = f'b{i}'
    rx, ry, rw, rh = F['result']
    for k, e in enumerate(EPISODES):
        t0, t1 = EP_T[k], EP_T[k + 1]
        inputs += ['-i', SHORTS / e[0] / 'short.mp4']
        fc.append(f'[{n + k}:v]trim=0:{t1 - t0 + 0.2:.2f},setpts=PTS-STARTPTS+{t0}/TB,scale={rw}:{rh}:flags=lanczos,setsar=1[res{k}]')
        nxt = 'vout' if k == len(EPISODES) - 1 else f'r{k}'
        fc.append(f"[{last}][res{k}]overlay={rx}:{ry}:enable='between(t,{t0},{t1})':eof_action=pass[{nxt}]")
        last = nxt
    out = TMP / f'base_{fmt}.mp4'
    run(['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(fc), '-map', '[vout]', '-t', DUR,
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', '30', out])
    print(out)


def sound_specs():
    """SFX + musiques via out/tools/sound.py (3 fichiers WAV)."""
    TMP.mkdir(parents=True, exist_ok=True)
    ev = []
    for k in range(7):                                   # glitch de fin d'accroche
        ev.append({'t': round(2.85 + 0.075 * k, 3), 'type': 'click', 'gain': 0.5})
    ev += [{'t': CUT - 0.35, 'type': 'whoosh', 'gain': 0.8, 'dur': 0.4}, {'t': CUT, 'type': 'impact', 'gain': 1.0},
           {'t': CUT + 0.05, 'type': 'glass', 'note': 'A5', 'gain': 0.4}]
    for c in range(len(COUNTS)):
        t = C0 + c * CD
        ev += [{'t': round(t - 0.25, 3), 'type': 'whoosh', 'gain': 0.45, 'dur': 0.35}, {'t': t, 'type': 'pop', 'note': 'E6', 'gain': 0.6}]
    ev += [{'t': CEND - 2.4, 'type': 'riser', 'gain': 0.7, 'dur': 2.4}, {'t': CEND, 'type': 'thud', 'gain': 0.9}]
    # apparitions de texte (en attendant de vrais SFX Freesound, cf. out/tools/freesound.py)
    ev += [{'t': 0.12, 'type': 'whoosh', 'gain': 0.5, 'dur': 0.25}, {'t': 0.17, 'type': 'pop', 'note': 'C6', 'gain': 0.5},
           {'t': CUES['hookLine2'] - 0.05, 'type': 'whoosh', 'gain': 0.5, 'dur': 0.25}, {'t': CUES['hookLine2'], 'type': 'impact', 'gain': 0.55},
           {'t': CUT + 0.25, 'type': 'pop', 'note': 'G5', 'gain': 0.55}, {'t': CUES['noneAlike'], 'type': 'impact', 'gain': 0.6},
           {'t': CUES['noneAlike'] + 0.02, 'type': 'glass', 'note': 'E6', 'gain': 0.35},
           {'t': CEND + 0.35, 'type': 'swell', 'note': 'E3', 'gain': 0.3, 'dur': 1.6},
           {'t': TERM, 'type': 'whoosh', 'gain': 0.4, 'dur': 0.3}, {'t': TERM + 0.05, 'type': 'blip', 'note': 'A5', 'gain': 0.3}]
    for k in range(1, len(EPISODES)):                    # changement d'épisode
        ev += [{'t': round(EP_T[k] - 0.15, 3), 'type': 'whoosh', 'gain': 0.55, 'dur': 0.3},
               {'t': EP_T[k] + 0.05, 'type': 'pop', 'note': ['E6', 'G6', 'B6'][k - 1], 'gain': 0.5}]
    k = 0
    tt = TERM + 0.5
    tt = CUES['typeStart']
    while tt < CUES['typeEnd']:                          # frappe clavier
        ev.append({'t': round(tt, 3), 'type': 'tick', 'gain': 0.22})
        tt += 0.055 + 0.03 * ((k * 7) % 3); k += 1
    ev += [{'t': c, 'type': 'blip', 'note': n, 'gain': 0.42} for c, n in zip(CUES['checks'], ['C6', 'E6', 'G6'])]
    ev += [{'t': RES0 - 0.2, 'type': 'whoosh', 'gain': 0.6, 'dur': 0.45}, {'t': RES0 + 0.3, 'type': 'pop', 'note': 'C6', 'gain': 0.5}]
    ev += [{'t': SLAMS[0], 'type': 'impact', 'gain': 0.9}, {'t': SLAMS[1], 'type': 'impact', 'gain': 0.9}, {'t': SLAMS[2], 'type': 'impact', 'gain': 1.0},
           {'t': END, 'type': 'whoosh', 'gain': 0.5, 'dur': 0.5}, {'t': END + 0.3, 'type': 'chime', 'note': 'A5', 'gain': 0.5},
           {'t': END + 0.3, 'type': 'swell', 'note': 'A3', 'gain': 0.45, 'dur': 3.4}]
    ev, synth_ev = sfx_samples(ev)               # vrais sons CC0 (out/demo/sfx/) quand ils existent, synthèse sinon
    specs = {
        'sfx': {'duration': DUR, 'seed': 14, 'bpm': 120, 'key': 'A', 'scale': 'minor', 'music': {'preset': 'none'}, 'events': synth_ev, 'reverb': 0.12},
        'hook': {'duration': CUT, 'seed': 3, 'bpm': 112, 'key': 'C', 'scale': 'major', 'music': {'preset': 'pluck-arp', 'gain': 0.5, 'loop': True}, 'events': []},
        'outro': {'duration': DUR - TERM, 'seed': 9, 'bpm': 112, 'key': 'A', 'scale': 'minor', 'music': {'preset': 'pulse', 'gain': 0.5, 'octave': 3}, 'events': []},
    }
    for name, spec in specs.items():
        p = TMP / f'{name}.json'
        json.dump(spec, open(p, 'w'))
        run([sys.executable, ROOT / 'out/tools/sound.py', p, TMP / f'{name}.wav'])
    specs['samples'] = ev
    json.dump(specs, open(HERE / 'sound.json', 'w'), indent=1)


SFX = HERE / 'sfx'


def _sample_role(e, k):
    """Type d'événement (sound.py) -> rôle de fichier CC0 dans out/demo/sfx/ (None = garder la synthèse)."""
    ty = e['type']
    if ty == 'whoosh':
        return 'whoosh_fast' if e.get('dur', 0.4) <= 0.35 else 'whoosh_soft'
    if ty == 'impact':
        return 'impact' if e['gain'] >= 0.8 else 'impact_light'
    if ty == 'tick':
        keys = sorted(p.stem for p in SFX.glob('key*.wav'))
        return keys[k % len(keys)] if keys else None
    return {'pop': 'pop', 'click': 'click', 'thud': 'impact', 'glass': 'shimmer', 'blip': 'ding',
            'chime': 'ding', 'riser': 'riser'}.get(ty)


def _peak_db(f):
    out = subprocess.run(['ffmpeg', '-i', str(f), '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(out.split('max_volume:')[1].split('dB')[0])


def sfx_samples(ev):
    """Pose les sons CC0 aux instants des événements -> TMP/samples.wav ; renvoie (événements posés, événements à synthétiser)."""
    placed, synth, inputs, fc = [], [], [], []
    peaks = {}
    for k, e in enumerate(ev):
        role = _sample_role(e, k)
        f = SFX / f'{role}.wav' if role else None
        if not f or not f.exists():
            synth.append(e); continue
        if role not in peaks:
            peaks[role] = _peak_db(f)
        g = e['gain'] * 0.9 * 10 ** ((-1 - peaks[role]) / 20)    # crête ramenée à -1 dBFS, puis gain de l'événement
        i = len(inputs) // 2
        ms = int(e['t'] * 1000)
        inputs += ['-i', f]
        trim = f"atrim=0:{e['dur'] + 0.4:.2f},afade=t=out:st={e['dur']:.2f}:d=0.4," if e['type'] == 'riser' else ''
        fc.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,{trim}adelay={ms}|{ms},volume={g:.3f},apad,atrim=0:{DUR}[s{i}]")
        placed.append({**e, 'file': f'sfx/{role}.wav'})
    out = TMP / 'samples.wav'
    if placed:
        fc.append(f"{''.join(f'[s{i}]' for i in range(len(placed)))}amix=inputs={len(placed)}:duration=longest:normalize=0[out]")
        run(['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(fc), '-map', '[out]', '-t', DUR, '-ar', '48000', out])
    elif out.exists():
        out.unlink()
    print(f'SFX : {len(placed)} sons CC0, {len(synth)} synthétisés', file=sys.stderr)
    return placed, synth


# Brouhaha : chaque tuile audible = musique de son short (short_novo.mp4, sans Arnold) + SA voix (brouhaha/NN.mp3),
# une voix différente par tuile (fr, ja, es, de, en ; hommes et femmes). Index = position dans AUDIBLE.
# Voix françaises uniquement : 00-07 Fish Audio (8 voix), 08-11 Gemini TTS (Aoede, Puck, Charon, Leda).
BROUHAHA_VOICES = 12
BROUHAHA_GAP = [0.5, 0.9, 0.6, 0.8, 0.4, 0.7, 1.0, 0.5, 0.9, 0.6, 0.8, 0.7]   # silence entre deux répétitions
BROUHAHA_LAG = [0.1, 0.15, 0.1, 0.1, 0.3, 0.1, 0.45, 0.25, 0.6, 0.35, 0.8, 0.5]  # entrée après l'allumage de la tuile


def brouhaha_clips():
    """Normalise (loudnorm) chaque voix et ajoute le silence de fin -> TMP/bh_NN.wav, lu en boucle."""
    TMP.mkdir(parents=True, exist_ok=True)
    for k in range(BROUHAHA_VOICES):
        src, dst = HERE / 'brouhaha' / f'{k:02d}.mp3', TMP / f'bh_{k:02d}.wav'
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-af',
             f'loudnorm=I=-19:TP=-2:LRA=9,aformat=sample_rates=48000:channel_layouts=stereo,apad=pad_dur={BROUHAHA_GAP[k]}', dst])


def audio():
    lay = write_layout()
    sound_specs()
    brouhaha_clips()
    inputs, fc, labels, bus = [], [], [], []
    i = 0
    ms = int(CUT * 1000)
    for t in lay['tiles']:
        T = t['audibleFrom']
        if T is None:
            continue
        k = AUDIBLE.index(t['id'])
        gate = f"clip((t-{T})/0.25,0,1)*clip(({CEND}-t)/0.04,0,1)"
        # musique du short (sans voix), en fond
        inputs += ['-stream_loop', '-1', '-i', SHORTS / t['dir'] / 'short_novo.mp4']
        fc.append(f"[{i}:a]atrim=0:{DUR - CUT:.2f},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
                  f"adelay={ms}|{ms},volume='0.28*{gate}':eval=frame,apad,atrim=0:{DUR}[m{i}]")
        bus.append(f'[m{i}]'); i += 1
        if k >= BROUHAHA_VOICES:
            continue
        # sa voix, en boucle, légèrement panoramiquée
        T0 = T + BROUHAHA_LAG[k]
        vms = int(T0 * 1000)
        pan = ((k * 5) % 11 - 5) / 9           # -0.55 .. +0.55
        lg, rg = min(1, 1 - pan), min(1, 1 + pan)
        inputs += ['-stream_loop', '-1', '-i', TMP / f'bh_{k:02d}.wav']
        fc.append(f"[{i}:a]atrim=0:{CEND - T0 + 0.1:.2f},asetpts=PTS-STARTPTS,pan=stereo|c0={lg:.2f}*c0|c1={rg:.2f}*c1,"
                  f"adelay={vms}|{vms},volume='0.62*clip((t-{T0})/0.05,0,1)*clip(({CEND}-t)/0.04,0,1)':eval=frame,apad,atrim=0:{DUR}[v{i}]")
        bus.append(f'[v{i}]'); i += 1
    # crescendo du bus : 0.8 au 1er cycle -> 1.0 au dernier, puis +60 % sur les 4 dernières secondes ; limiteur propre au bus
    last = C0 + CD * (len(COUNTS) - 1)
    cres = f"(0.8+0.2*clip((t-{C0})/{last - C0},0,1))*(1+0.6*clip((t-({CEND}-2))/2,0,1))"
    fc.append(f"{''.join(bus)}amix=inputs={len(bus)}:duration=longest:normalize=0,volume='{cres}':eval=frame,"
              f"alimiter=limit=0.8:attack=4:release=60[bh]")
    labels.append('[bh]')
    for k, e in enumerate(EPISODES):
        t0, t1 = EP_T[k], EP_T[k + 1]
        d = t1 - t0
        ms = int(t0 * 1000)
        if e[2] is None:      # son original (voix Arnold comprise)
            inputs += ['-i', SHORTS / e[0] / 'short.mp4']; g = 0.75
        else:                 # musique seule + voix française différente
            inputs += ['-i', SHORTS / e[0] / 'short_novo.mp4']; g = 0.6
        fc.append(f"[{i}:a]atrim=0:{d:.2f},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
                  f"afade=t=in:d=0.08,afade=t=out:st={d - 0.3:.2f}:d=0.3,adelay={ms}|{ms},volume={g},apad,atrim=0:{DUR}[a{i}]")
        labels.append(f'[a{i}]'); i += 1
        if e[2] is not None:
            vms = int((t0 + 0.25) * 1000)
            inputs += ['-i', TMP / f'bh_{int(e[2]):02d}.wav']
            fc.append(f"[{i}:a]atrim=0:{d - 0.3:.2f},afade=t=out:st={d - 0.55:.2f}:d=0.25,adelay={vms}|{vms},volume=1.5,apad,atrim=0:{DUR}[a{i}]")
            labels.append(f'[a{i}]'); i += 1
    for t, f, g in VOICE:
        inputs += ['-i', HERE / 'voice_en' / f'{f}.mp3']
        ms = int(t * 1000)
        fc.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms},volume={g},apad,atrim=0:{DUR}[a{i}]")
        labels.append(f'[a{i}]'); i += 1
    tracks = [('sfx', 0, 0.9), ('hook', 0, 0.55), ('outro', TERM, 0.32)]
    if (TMP / 'samples.wav').exists():
        tracks.append(('samples', 0, 0.8))
    for name, start, gain in tracks:
        inputs += ['-i', TMP / f'{name}.wav']
        ms = int(start * 1000)
        fc.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms},volume={gain},apad,atrim=0:{DUR}[a{i}]")
        labels.append(f'[a{i}]'); i += 1
    fc.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=longest:normalize=0,alimiter=limit=0.89:attack=5:release=80:level=disabled,"
              f"afade=t=out:st={DUR - 0.6}:d=0.6[aout]")
    out = TMP / 'mix.wav'
    run(['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(fc), '-map', '[aout]', '-t', DUR, '-ar', '48000', out])
    print(out)


def overlay(fmt):
    write_layout()
    F = layouts()[fmt]
    run(['node', ROOT / 'out/tools/render.mjs', HERE / 'overlay.html', '--query', f'fmt={fmt}', '--width', F['W'], '--height', F['H'],
         '--duration', DUR, '--alpha', '--out', TMP / f'overlay_{fmt}.mov'])


def final(fmt):
    out = HERE / f'demo_{fmt}.mp4'
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', TMP / f'base_{fmt}.mp4', '-i', TMP / f'overlay_{fmt}.mov', '-i', TMP / 'mix.wav',
         '-filter_complex', '[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]', '-map', '[v]', '-map', '2:a',
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '10M', '-bufsize', '20M', '-pix_fmt', 'yuv420p', '-r', '30',
         '-c:a', 'aac', '-b:a', '192k', '-t', DUR, '-movflags', '+faststart', out])
    print(out)


def gif():
    src = HERE / 'demo_16x9.mp4'
    pal = TMP / 'palette.png'
    vf = 'fps=12,scale=720:-1:flags=lanczos'
    run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '0', '-t', '12', '-i', src, '-vf', f'{vf},palettegen=max_colors=128', pal])
    run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '0', '-t', '12', '-i', src, '-i', pal, '-lavfi', f'{vf}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4',
         HERE / 'demo_preview.gif'])
    print(HERE / 'demo_preview.gif')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    fmt = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd == 'layout': write_layout()
    elif cmd == 'base': base(fmt)
    elif cmd == 'audio': audio()
    elif cmd == 'overlay': overlay(fmt)
    elif cmd == 'final': final(fmt)
    elif cmd == 'gif': gif()
    elif cmd == 'all':
        audio()
        for f in ('16x9', '9x16'):
            base(f); overlay(f); final(f)
        gif()
