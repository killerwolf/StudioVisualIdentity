#!/usr/bin/env python3
"""
build_audio.py — son, assemblage, aperçu et vignette de la démo « Caméléon » (appelé par build.py).

- Musique : synthétisée par code (numpy/scipy, 120 BPM, la mineur), calée sur le montage.
- Bruitages : uniquement les sons CC0 de out/demo/sfx/ (crédits : sfx/credits.json).
- Brouhaha du mur de shorts : les voix françaises déjà présentes dans out/demo/brouhaha/ (aucune génération).
- Voix off : mixée seulement si out/demo/voice_fr/NN.mp3 existent (voir narration_fr.json), avec ducking de la musique.
"""
import json, math, shutil, subprocess
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

import __main__ as _m
B = _m if hasattr(_m, 'NARRATION') else __import__('build')

SR = 48000
HERE = Path(__file__).resolve().parent
SFX = HERE / 'sfx'
BEAT = 0.5


# ------------------------------------------------------------------ outils
def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), 'low')
    return signal.lfilter(b, a, x, axis=0)


def hp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), 'high')
    return signal.lfilter(b, a, x, axis=0)


def tax(d):
    return np.arange(int(d * SR)) / SR


class Track:
    def __init__(self, dur):
        self.x = np.zeros((int(dur * SR) + SR, 2))

    def add(self, y, t, g=1.0, pan=0.0):
        i = int(round(t * SR))
        if i < 0:
            y = y[-i:]
            i = 0
        n = min(len(y), len(self.x) - i)
        if n <= 0:
            return
        if y.ndim == 1:
            l, r = math.cos((pan + 1) * math.pi / 4) * 1.414, math.sin((pan + 1) * math.pi / 4) * 1.414
            self.x[i:i + n, 0] += y[:n] * g * l
            self.x[i:i + n, 1] += y[:n] * g * r
        else:
            self.x[i:i + n] += y[:n] * g


def kick():
    t = tax(0.34)
    f = 46 + 150 * np.exp(-t * 34)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10)
    click = hp(np.random.default_rng(1).uniform(-1, 1, len(t)), 3000) * np.exp(-t * 300) * 0.25
    return np.tanh((y + click) * 1.6)


def hat(d=0.05, seed=2, dec=70):
    t = tax(d)
    return hp(np.random.default_rng(seed).uniform(-1, 1, len(t)), 7500) * np.exp(-t * dec)


def clap():
    t = tax(0.22)
    n = np.random.default_rng(5).uniform(-1, 1, len(t))
    b, a = signal.butter(2, [900 / (SR / 2), 4200 / (SR / 2)], 'band')
    env = sum(np.exp(-np.clip(t - d, 0, None) * 38) * (t >= d) for d in (0, 0.011, 0.023)) / 2
    return signal.lfilter(b, a, n) * env


def bass(m, d):
    t = tax(d)
    f = hz(m)
    y = signal.sawtooth(2 * np.pi * f * t) * 0.6 + np.sin(2 * np.pi * f * t)
    y = lp(y, 520)
    return y * np.minimum(1, t * 300) * np.exp(-t * 3.5) * np.minimum(1, (d - t) * 60)


def pluck(m, d=0.3, bright=2600):
    t = tax(d)
    f = hz(m)
    y = signal.sawtooth(2 * np.pi * f * t, 0.5) * 0.5 + signal.square(2 * np.pi * f * t) * 0.25 + np.sin(2 * np.pi * 2 * f * t) * 0.2
    y = lp(y, bright)
    return y * np.minimum(1, t * 500) * np.exp(-t * 11)


def pad(notes, d, cut=1500):
    t = tax(d)
    y = sum(signal.sawtooth(2 * np.pi * hz(m) * (1 + dt) * t) for m in notes for dt in (-0.004, 0.003, 0.0)) / (3 * len(notes))
    y = lp(y, cut)
    return y * np.minimum(1, t * 6) * np.minimum(1, (d - t) * 4)


def stab(notes, d=0.22):
    t = tax(d)
    y = sum(signal.sawtooth(2 * np.pi * hz(m) * (1 + dt) * t) for m in notes for dt in (-0.005, 0.005)) / (2 * len(notes))
    return lp(y, 3200) * np.minimum(1, t * 400) * np.exp(-t * 13)


def load(name):
    sr, y = wavfile.read(SFX / f'{name}.wav')
    y = y.astype(np.float64) / (32768.0 if y.dtype == np.int16 else (np.abs(y).max() or 1))
    if y.ndim == 1:
        y = np.stack([y, y], 1)
    pk = np.abs(y).max()
    return y / pk if pk else y


def pitch(y, ratio):
    n = int(len(y) / ratio)
    idx = np.linspace(0, len(y) - 1, n)
    return np.stack([np.interp(idx, np.arange(len(y)), y[:, c]) for c in range(y.shape[1])], 1)


def decode(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(path), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


CH = [(45, [57, 60, 64]), (41, [57, 60, 65]), (48, [55, 60, 64]), (43, [55, 59, 62])]  # Am F C G (basse, accord)


# ------------------------------------------------------------------ musique
def music():
    D = B.DUR
    drums, tonal, fx = Track(D), Track(D), Track(D)
    K, HH, CL = kick(), hat(), clap()
    OH = hat(0.16, 3, 22)

    # 0 -> 2,5 s : la « musique de template » (ukulélé joyeux, filtré comme un haut-parleur de téléphone), puis elle déraille
    muz = Track(3.2)
    cmaj = [(60, 64, 67), (60, 64, 67), (65, 69, 72), (67, 71, 74)]
    for i in range(int(2.9 / 0.25)):
        ch = cmaj[(i // 4) % 4]
        muz.add(pluck(ch[(0, 2, 1, 2)[i % 4]] + 12, 0.3, 4000), i * 0.25, 0.5)
        if i % 4 == 0:
            muz.add(pluck(ch[0] - 12, 0.5, 1200), i * 0.25, 0.6)
    m = hp(lp(muz.x, 3400), 380)
    n0, n1 = int(2.45 * SR), int(2.95 * SR)      # arrêt de bande à 2,5 s
    sp = np.ones(n1)
    sp[n0:] = np.linspace(1, 0.05, n1 - n0) ** 1.5
    pos = np.cumsum(sp)
    pos = pos[pos < len(m) - 1]
    m2 = np.stack([np.interp(pos, np.arange(len(m)), m[:, c]) for c in range(2)], 1)
    m2[-int(0.08 * SR):] *= np.linspace(1, 0, int(0.08 * SR))[:, None]
    fx.add(m2, 0, 1.25)
    for t in (0.03, 0.50, 0.90):   # un coup grave sous chaque mot de l'accroche
        drums.add(K, t, 0.9)

    def groove(t0, t1, full=True, hats=True, kicks=True, claps=True, arp=True, bassg=1.0, stabs=True):
        nb = int(round((t1 - t0) / BEAT))
        for b in range(nb):
            t = t0 + b * BEAT
            bar = int((t - 4.0) // 2.0)
            root, chord = CH[bar % 4]
            if kicks and (full or b % 2 == 0):
                drums.add(K, t, 0.95)
            if hats:
                drums.add(HH, t + 0.25, 0.30, 0.2)
                if full:
                    drums.add(HH, t + 0.125, 0.12, -0.3)
                    drums.add(HH, t + 0.375, 0.12, 0.3)
                    if b % 4 == 3:
                        drums.add(OH, t + 0.25, 0.22, 0.1)
            if claps and full and b % 2 == 1:
                drums.add(CL, t, 0.55)
            if bassg:
                tonal.add(bass(root - 12, 0.24), t, 0.55 * bassg)
                tonal.add(bass(root - 12, 0.22), t + 0.25, 0.42 * bassg)
                if full and b % 4 == 3:
                    tonal.add(bass(root, 0.12), t + 0.375, 0.3 * bassg)
            if arp:
                pat = [0, 1, 2, 1, 0, 2, 1, 2]
                for s in range(4):
                    nt = chord[pat[(b * 4 + s) % 8]] + (12 if (b * 4 + s) % 8 in (2, 5) else 0)
                    tonal.add(pluck(nt + 12, 0.26, 3200 if full else 1800), t + s * 0.125, 0.16 if full else 0.11, 0.5 * math.sin(b + s))
                    tonal.add(pluck(nt + 12, 0.26, 1500), t + s * 0.125 + 0.1875, 0.06, -0.5 * math.sin(b + s))  # écho
            if stabs and full and b % 4 in (0, 3):
                tonal.add(stab([c + 12 for c in chord]), t + (0 if b % 4 == 0 else 0.25), 0.22)

    def pads(t0, t1, g=0.16, cut=1500):
        t = t0
        while t < t1 - 0.01:
            bar = int((t - 4.0) // 2.0)
            d = min(2.0, t1 - t)
            tonal.add(pad(CH[bar % 4][1], d + 0.3, cut), t, g)
            t += 2.0

    # 4 -> 6 : entrée à mi-régime ; 6 -> 18 : plein régime (carrousel, mur)
    groove(4.0, 6.0, full=False, claps=False)
    groove(6.0, 18.0)
    pads(4.0, 18.0)
    # 18 -> 22 : le juge — on retire la grosse caisse, on garde le fil
    groove(18.0, 22.0, full=False, kicks=False, hats=True, bassg=0.5)
    pads(18.0, 22.0, 0.32, 1900)
    # 22 -> 29 : le prompt — presque rien, puis ça remonte
    groove(22.0, 27.0, full=False, kicks=False, hats=False, arp=False, bassg=0.7, stabs=False)
    groove(27.0, 29.0, full=False, kicks=True, hats=True, bassg=0.8)
    pads(22.0, 29.0, 0.3, 1100)
    for i in range(8):   # roulement 28 -> 29
        drums.add(CL, 28.0 + i * 0.125, 0.18 + 0.05 * i)
    # 29 -> 39 : épisodes et chiffres
    groove(29.0, 39.0)
    pads(29.0, 39.0)
    # 39 : accord final
    tonal.add(pad([45, 57, 60, 64, 71], 4.2, 2200), 39.0, 0.3)
    for k, mnote in enumerate((69, 72, 76, 81)):
        tonal.add(pluck(mnote, 1.2, 3000), 39.0 + k * 0.125, 0.22)
    drums.add(K, 39.0, 1.0)

    # pompage (sidechain) de la partie tonale sur chaque grosse caisse
    env = np.ones(len(tonal.x))
    for t0, t1, step in ((4.0, 6.0, 1.0), (6.0, 18.0, 0.5), (27.0, 29.0, 1.0), (29.0, 39.0, 0.5)):
        t = t0
        while t < t1 - 0.01:
            i = int(t * SR)
            n = int(0.3 * SR)
            env[i:i + n] = np.minimum(env[i:i + n], 1 - 0.55 * np.exp(-np.arange(n) / (0.09 * SR)))
            t += step
    tonal.x *= env[:, None]
    mix = drums.x * 0.8 + tonal.x * 1.0 + fx.x
    n = int(1.2 * SR)
    e = int(D * SR)
    mix[e - n:e] *= np.linspace(1, 0, n)[:, None] ** 2
    mix[e:] = 0
    return mix


# ------------------------------------------------------------------ bruitages (sons CC0 de sfx/)
def sfx_track():
    D = B.DUR
    tr = Track(D)
    S = {n: load(n) for n in ('click', 'ding', 'glitch', 'impact', 'impact_light', 'key1', 'key2', 'key3', 'pop', 'riser', 'whoosh_fast', 'whoosh_soft')}
    ev = []

    def put(name, t, g=0.6, ratio=1.0, pan=0.0):
        y = S[name] if ratio == 1.0 else pitch(S[name], ratio)
        yy = y.copy()
        yy[:, 0] *= 1 - max(0, pan)
        yy[:, 1] *= 1 + min(0, pan)
        tr.add(yy, t, g)
        ev.append({'t': round(t, 3), 'sfx': name, 'gain': round(g, 2)})

    # accroche : trois mots qui claquent
    for k, t in enumerate((0.03, 0.50, 0.90)):
        put('impact_light' if k < 2 else 'impact', t, 0.75 + 0.1 * k)
        put('whoosh_fast', t - 0.12, 0.25)
    # la carte change de style
    put('glitch', B.T_MUT - 0.02, 0.6)
    for k in range(6):
        put('pop', B.T_MUT + 0.25 * k, 0.4, 0.9 + 0.08 * k)
    put('riser', B.T_COV - 1.76, 0.55)
    put('impact', B.T_COV, 0.95)
    put('whoosh_soft', B.T_COV - 0.25, 0.5)
    # carrousel : un petit tic à chaque identité
    for k in range(1, B.N):
        put('click', B.cov_start(k), 0.32, 0.85 + 0.02 * k, pan=0.3 if k % 2 else -0.3)
        if k < 3:
            put('whoosh_fast', B.cov_start(k) - 0.05, 0.3)
    # mur
    put('whoosh_soft', B.T_WALL - 0.3, 0.6)
    put('impact', B.T_WALL, 0.8)
    put('impact_light', B.T_WALL + 0.5, 0.8)
    put('pop', B.T_WALL + 1.3, 0.4)
    # juge
    put('whoosh_fast', B.T_JUDGE - 0.1, 0.5)
    put('whoosh_soft', B.T_JUDGE + 1.05, 0.5)
    for k in range(B.N):
        put('click', B.T_JUDGE + 2.3 + k * 0.055, 0.35, 0.9 + 0.035 * k)
    put('ding', B.T_JUDGE + 2.3 + B.N * 0.055, 0.7)
    # terminal : frappe
    put('whoosh_fast', B.T_TERM - 0.1, 0.5)
    total = sum(len(l) for l in B.PROMPT)
    rng = np.random.default_rng(11)
    for c in range(0, total, 3):
        t = B.TYPE0 + (B.TYPE1 - B.TYPE0) * c / total
        put(f'key{1 + int(rng.integers(0, 3))}', t + float(rng.uniform(-0.012, 0.012)), 0.32, float(rng.uniform(0.94, 1.06)))
    for hi in range(14):
        put('click', B.T_TERM + 1.3 + 0.25 * hi, 0.12, 1.3, pan=-0.5)
    for k, t in enumerate(B.T_CHECKS):
        put('ding', t, 0.5 if k < 3 else 0.35, 1.0 + 0.06 * k)
    put('whoosh_soft', B.T_CHK[1], 0.45)
    put('riser', B.T_EP[0] - 1.76, 0.6)
    put('impact', B.T_EP[0], 0.9)
    for t in B.T_EP[1:]:
        put('whoosh_fast', t - 0.05, 0.5)
        put('impact_light', t, 0.55)
    # panneaux
    for k in range(4):
        put('whoosh_fast', B.T_SLAM + k - 0.08, 0.45)
        put('impact', B.T_SLAM + k + 0.12, 0.85, 1.0 - 0.04 * k)
    # fin
    put('whoosh_soft', B.T_END - 0.1, 0.6)
    put('impact_light', B.T_END + 0.3, 0.6)
    for k in range(1, 6):
        put('click', B.T_END + 0.3 + 0.5 * k, 0.3, 1.0 + 0.05 * k)
    put('ding', B.T_END + 1.1, 0.4, 1.12)
    json.dump({'duration': D, 'bpm': 120, 'note': 'sons CC0 de out/demo/sfx/ (voir sfx/credits.json), posés par build_audio.py', 'events': ev},
              open(HERE / 'sound_fr.json', 'w'), ensure_ascii=False, indent=1)
    return tr.x


def brouhaha():
    """Le mur des 45 shorts « parle » : quelques voix françaises déjà enregistrées, très bas."""
    tr = Track(B.DUR)
    files = sorted((HERE / 'brouhaha').glob('*.mp3'))
    for k, f in enumerate(files[:8]):
        y = decode(f)
        y = y / (np.abs(y).max() or 1)
        t0 = B.T_WALL + 0.15 + 0.22 * k
        d = B.T_JUDGE - 0.2 - t0
        y = y[int(0.3 * SR):int((0.3 + d) * SR)]
        n = len(y)
        env = np.minimum(1, np.arange(n) / (0.4 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.35 * SR))
        tr.add(hp(y * env, 200), t0, 0.07, pan=(-0.8 + 1.6 * (k % 4) / 3))
    return tr.x


def limit(x, peak=0.84):
    x = np.tanh(x * 1.1) / np.tanh(1.1)
    pk = np.abs(x).max()
    return x * (peak / pk) if pk > 0 else x


def write_wav(path, x):
    wavfile.write(path, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))


def voice_files():
    d = HERE / 'voice_fr'
    fs = [d / f'{k:02d}.mp3' for k in range(len(B.NARRATION))]
    return fs if all(f.exists() for f in fs) else None


def audio():
    B.TMP.mkdir(parents=True, exist_ok=True)
    n = int(B.DUR * SR)
    bed = limit((music() * 0.62 + sfx_track() * 0.9 + brouhaha())[:n])
    write_wav(B.TMP / 'bed.wav', bed)
    print(B.TMP / 'bed.wav')
    vf = voice_files()
    if vf:
        voice = np.zeros(n)
        for (t0, t1, _), f in zip(B.NARRATION, vf):
            y = decode(f)
            y = y / (np.abs(y).max() or 1) * 0.9
            i = int(t0 * SR)
            m = min(len(y), n - i)
            voice[i:i + m] += y[:m]
            if len(y) / SR > (t1 - t0) + 0.6:
                print(f'ATTENTION : {f.name} dure {len(y) / SR:.2f} s pour un créneau de {t1 - t0:.2f} s')
        # ducking : la musique baisse d'environ 9 dB sous la voix
        pres = (np.abs(voice) > 0.02).astype(np.float64)
        k = int(0.3 * SR)
        pres = np.minimum(1, signal.fftconvolve(pres, np.ones(k) / k * 4, 'same'))
        b, a = signal.butter(1, 6 / (SR / 2))
        duck = 1 - 0.64 * np.clip(signal.filtfilt(b, a, pres), 0, 1)
        mixv = bed * duck[:, None] + np.stack([voice, voice], 1) * 1.05
        write_wav(B.TMP / 'mix_voice.wav', limit(mixv, 0.89))
        print(B.TMP / 'mix_voice.wav')
    elif (B.TMP / 'mix_voice.wav').exists():
        (B.TMP / 'mix_voice.wav').unlink()


def final(fmt):
    v = B.TMP / f'video_{fmt}.mp4'

    def mux(wav, out):
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(v), '-i', str(wav), '-map', '0:v', '-map', '1:a',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '26', '-pix_fmt', 'yuv420p', '-r', '30',   # ~20 Mo par fichier
                        '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-t', str(B.DUR),
                        '-movflags', '+faststart', str(out)], check=True)
        print(out)
    novo = HERE / f'demo_{fmt}_novo.mp4'
    mux(B.TMP / 'bed.wav', novo)
    if (B.TMP / 'mix_voice.wav').exists() and voice_files():
        mux(B.TMP / 'mix_voice.wav', HERE / f'demo_{fmt}.mp4')
    else:
        shutil.copyfile(novo, HERE / f'demo_{fmt}.mp4')   # en attendant la voix : même contenu que _novo
        print(HERE / f'demo_{fmt}.mp4', '(sans voix : voice_fr/ absent)')


def gif():
    src = HERE / 'demo_16x9.mp4'
    pal = B.TMP / 'palette.png'
    vf = 'fps=10,scale=480:-1:flags=lanczos'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-t', '12', '-i', str(src), '-vf', vf + ',palettegen=max_colors=128:stats_mode=diff', str(pal)], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-t', '12', '-i', str(src), '-i', str(pal), '-lavfi', vf + '[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4',
                    str(HERE / 'demo_preview.gif')], check=True)
    print(HERE / 'demo_preview.gif')


def thumb():
    """Vignette 16:9 : le mur des vrais shorts + le titre."""
    from PIL import Image
    B.setfmt('16x9')
    fr = B.scene_wall(B.T_WALL + 2.6, 0, caption=False)
    W = B.W
    x = np.linspace(0, 1, W)[None, :, None]     # voile sombre à gauche
    al = np.clip(1.25 - x * 1.7, 0, 1) ** 1.2 * 0.93
    fr = (fr * (1 - al) + np.array(B.rgb('#07080F'), np.float32) * al).astype(np.uint8)
    y = 150
    for txt in ('18 identités', 'visuelles'):
        B.blit(fr, B.Tt(txt, ('unbounded', 900), 150, '#05060B'), 100 + 8, y + 10)
        B.blit(fr, B.Tt(txt, ('unbounded', 900), 150, B.YEL), 100, y)
        y += 190
    y += 40
    B.blit(fr, B.T('45 shorts pour le prouver.', B.GROT, 66, '#FFFFFF'), 100, y)
    B.blit(fr, B.T('Un prompt pour lancer la vôtre.', B.GROT, 66, '#FFFFFF'), 100, y + 88)
    lab = B.T('open source · rendu par du code', B.MONOB, 38, '#0B0D17')
    B.blit(fr, B.rr(lab.shape[1] + 48, lab.shape[0] + 24, 14, '#3CF2A0'), 100, y + 215)
    B.blit(fr, lab, 124, y + 227)
    fr = B.finish(fr, 0)
    d = HERE / 'thumb'
    d.mkdir(exist_ok=True)
    im = Image.fromarray(fr)
    im.save(d / 'thumbnail_fr_1920.jpg', quality=90)
    im.resize((1280, 720), Image.LANCZOS).save(d / 'thumbnail_fr_1280.jpg', quality=88)
    print(d / 'thumbnail_fr_1280.jpg')


def write_narration():
    def wps(txt, a, b):
        words = [w for w in txt.replace(B.NB, ' ').replace('…', ' ').split() if any(c.isalnum() for c in w)]
        return round(len(words) / (b - a), 2)
    out = {'language': 'fr', 'voice': 'à générer après validation : Gemini « Sulafat » (un seul appel, découpe par ligne)',
           'note': 'Aucune voix générée pour l’instant. Déposer une ligne par fichier dans out/demo/voice_fr/NN.mp3 (NN = index), '
                   'puis `build.py audio` et `build.py final <fmt>` : la musique est atténuée sous la voix. Débit visé ≤ 2,8 mots/s.',
           'duration': B.DUR,
           'lines': [{'index': k, 'file': f'voice_fr/{k:02d}.mp3', 'start': a, 'end': b, 'text': txt, 'wordsPerSec': wps(txt, a, b)}
                     for k, (a, b, txt) in enumerate(B.NARRATION)]}
    json.dump(out, open(HERE / 'narration_fr.json', 'w'), ensure_ascii=False, indent=1)
    print(HERE / 'narration_fr.json')
    for l in out['lines']:
        print(f"  {l['start']:5.1f}–{l['end']:5.1f}  {l['wordsPerSec']:.2f} m/s  {l['text']}")
