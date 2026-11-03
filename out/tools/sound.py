#!/usr/bin/env python3
"""
sound.py — sound design minimal 100 % généré par code (numpy/scipy -> WAV 48 kHz stéréo).

USAGE
  python out/tools/sound.py spec.json out.wav
  python out/tools/sound.py --demo out.wav            # démo de tous les sons

SPEC (JSON)
{
  "duration": 15.0,            # secondes
  "seed": 3,
  "bpm": 96,
  "key": "D", "scale": "majpent",       # major, minor, majpent, minpent, dorian, lydian, wholetone
  "music": {"preset": "pluck-arp"|"pad"|"lofi"|"music-box"|"pulse"|"drone"|"chiptune"|"none",
            "gain": 0.5, "octave": 4, "density": 0.6, "loop": false},
  "events": [ {"t": 0.0, "type": "whoosh"|"impact"|"pop"|"tick"|"chime"|"riser"|"thud"|"blip"|"swell"|"click"|"coin"|"glass",
               "gain": 0.8, "note": "A5", "dur": 0.6} ]
}
Le mix final est normalisé avec une crête à -1 dBFS et un niveau moyen proche de -18 dBFS RMS
(le « volume modéré » demandé). assemble.py applique ensuite le gain voulu sous la vidéo.
Déterministe : même spec -> même WAV.
"""
import json, sys, math
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
NOTE_IDX = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6,
            'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
SCALES = {'major': [0, 2, 4, 5, 7, 9, 11], 'minor': [0, 2, 3, 5, 7, 8, 10], 'majpent': [0, 2, 4, 7, 9],
          'minpent': [0, 3, 5, 7, 10], 'dorian': [0, 2, 3, 5, 7, 9, 10], 'lydian': [0, 2, 4, 6, 7, 9, 11],
          'wholetone': [0, 2, 4, 6, 8, 10]}


def midi_to_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def note_to_midi(n):
    n = n.strip()
    name = n[:-1] if n[-1].isdigit() else n
    octv = int(n[-1]) if n[-1].isdigit() else 4
    if len(name) > 2:  # e.g. 'C#' with multi-digit octave not supported
        name = name[:2]
    return 12 * (octv + 1) + NOTE_IDX[name]


def env_adsr(n, a=0.005, d=0.1, s=0.6, r=0.2, sr=SR):
    a_n, d_n, r_n = int(a * sr), int(d * sr), int(r * sr)
    s_n = max(0, n - a_n - d_n - r_n)
    e = np.concatenate([np.linspace(0, 1, max(a_n, 1)), np.linspace(1, s, max(d_n, 1)),
                        np.full(s_n, s), np.linspace(s, 0, max(r_n, 1))])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def osc(freq, dur, kind='sine', detune=0.0):
    t = t_axis(dur)
    ph = 2 * np.pi * freq * (1 + detune) * t
    if kind == 'sine':
        return np.sin(ph)
    if kind == 'tri':
        return signal.sawtooth(ph, 0.5)
    if kind == 'saw':
        return signal.sawtooth(ph)
    if kind == 'square':
        return signal.square(ph) * 0.6
    raise ValueError(kind)


def lowpass(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), 'low')
    return signal.lfilter(b, a, x)


def highpass(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), 'high')
    return signal.lfilter(b, a, x)


def bandpass(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi / (SR / 2), 0.99)], 'band')
    return signal.lfilter(b, a, x)


# ---------- instruments ----------
def pluck(freq, dur=0.6, bright=0.5):
    """Karplus-Strong."""
    n = int(dur * SR)
    period = max(2, int(SR / freq))
    rnd = np.random.default_rng(int(freq * 100))
    buf = rnd.uniform(-1, 1, period)
    buf = lowpass(buf, 2000 + 8000 * bright)
    out = np.zeros(n)
    decay = 0.996
    for i in range(n):
        out[i] = buf[i % period]
        buf[i % period] = decay * 0.5 * (buf[i % period] + buf[(i + 1) % period])
    return out * env_adsr(n, 0.001, 0.05, 0.8, min(0.2, dur / 3))


def bell(freq, dur=1.2):
    t = t_axis(dur)
    partials = [(1, 1.0), (2.76, 0.45), (5.4, 0.25), (8.93, 0.12)]
    x = sum(a * np.sin(2 * np.pi * freq * p * t) * np.exp(-t * (2.5 + p)) for p, a in partials)
    return x * env_adsr(len(t), 0.002, 0.05, 1, 0.05)


def music_box(freq, dur=0.9):
    t = t_axis(dur)
    x = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 4 * t) * np.exp(-t * 12)
    return x * np.exp(-t * 4.5) * env_adsr(len(t), 0.001, 0.01, 1, 0.03)


def pad_note(freq, dur):
    x = sum(osc(freq, dur, 'saw', d) for d in (-0.006, 0, 0.007)) / 3
    x = lowpass(x, 1200, 2)
    return x * env_adsr(len(x), min(0.8, dur / 3), 0.2, 0.8, min(1.0, dur / 3))


def chip(freq, dur=0.18):
    x = osc(freq, dur, 'square')
    return x * env_adsr(len(x), 0.002, 0.04, 0.5, 0.05)


def kick(dur=0.4):
    t = t_axis(dur)
    f = 50 + 120 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9)


def noise(dur, seed=0):
    return np.random.default_rng(seed).uniform(-1, 1, int(dur * SR))


def hat(dur=0.06, seed=1):
    x = highpass(noise(dur, seed), 7000)
    return x * np.exp(-t_axis(dur) * 60)


# ---------- SFX ----------
def sfx(kind, note='A5', dur=None, seed=0):
    f = midi_to_hz(note_to_midi(note)) if isinstance(note, str) else float(note)
    if kind == 'whoosh':
        d = dur or 0.7
        n = noise(d, seed); t = t_axis(d)
        fc = 300 + 5000 * np.sin(np.pi * t / d) ** 2
        out = np.zeros_like(n); zi = None
        # time-varying bandpass in blocks
        blk = 512
        for i in range(0, len(n), blk):
            c = fc[min(i, len(fc) - 1)]
            b, a = signal.butter(2, [max(80, c * 0.5) / (SR / 2), min(c * 1.6, SR / 2.1) / (SR / 2)], 'band')
            out[i:i + blk] = signal.lfilter(b, a, n[i:i + blk])
        return out * np.sin(np.pi * t / d) ** 1.5 * 1.6
    if kind == 'riser':
        d = dur or 1.5
        t = t_axis(d)
        fr = 200 * (2 ** (3 * t / d))
        x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * 0.4 + bandpass(noise(d, seed), 1000, 8000) * 0.3 * (t / d)
        return x * (t / d) ** 2
    if kind == 'impact':
        d = dur or 0.9
        return kick(d) * 1.2 + lowpass(noise(d, seed), 900) * np.exp(-t_axis(d) * 14) * 0.8
    if kind == 'thud':
        d = dur or 0.35
        return kick(d) * 0.9
    if kind == 'pop':
        d = dur or 0.12
        t = t_axis(d)
        fr = f * (1.6 - 0.6 * t / d)
        return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 35)
    if kind == 'blip':
        d = dur or 0.09
        return osc(f, d, 'tri') * np.exp(-t_axis(d) * 30)
    if kind == 'tick':
        d = dur or 0.03
        return highpass(noise(d, seed), 3000) * np.exp(-t_axis(d) * 200)
    if kind == 'click':
        d = dur or 0.02
        return osc(2500, d, 'sine') * np.exp(-t_axis(d) * 300)
    if kind == 'chime':
        return bell(f, dur or 1.5)
    if kind == 'glass':
        return bell(f * 2, dur or 1.0) * 0.7
    if kind == 'coin':
        d = 0.25
        a = chip(f, 0.07); b = chip(f * 1.5, d - 0.07)
        return np.concatenate([a, b])
    if kind == 'swell':
        d = dur or 2.0
        x = pad_note(f / 2, d) + pad_note(f / 2 * 1.5, d) * 0.6
        return x * np.sin(np.pi * t_axis(d) / d)
    raise ValueError('unknown sfx ' + kind)


# ---------- music generator ----------
def gen_music(spec, total):
    m = spec.get('music', {})
    preset = m.get('preset', 'pluck-arp')
    if preset == 'none':
        return np.zeros(int(total * SR))
    rnd = np.random.default_rng(spec.get('seed', 1))
    bpm = spec.get('bpm', 96)
    beat = 60 / bpm
    root = NOTE_IDX[spec.get('key', 'C')]
    sc = SCALES[spec.get('scale', 'majpent')]
    octave = m.get('octave', 4)
    density = m.get('density', 0.6)
    out = np.zeros(int((total + 3) * SR))

    def place(x, t, g=1.0):
        i = int(t * SR)
        if i >= len(out):
            return
        e = min(len(out), i + len(x))
        out[i:e] += x[:e - i] * g

    def deg(d, o=0):
        n = len(sc)
        return 12 * (octave + 1 + o + d // n) + root + sc[d % n]

    # chord progression (degrees): I - vi - IV - V like in scale space
    prog = [0, 5, 3, 4] if len(sc) == 7 else [0, 3, 1, 4]
    bar = beat * 4
    nbars = int(math.ceil(total / bar)) + 1
    melody_deg = 2
    for b in range(nbars):
        t0 = b * bar
        ch = prog[b % len(prog)]
        if preset in ('pad', 'lofi', 'drone'):
            for k in (0, 2, 4):
                place(pad_note(midi_to_hz(deg(ch + k, -1)), bar * 1.05), t0, 0.22)
        if preset == 'drone':
            continue
        steps = 8
        for s in range(steps):
            t = t0 + s * beat / 2
            if preset == 'pluck-arp':
                d = ch + [0, 2, 4, 7][s % 4]
                place(pluck(midi_to_hz(deg(d)), beat * 1.2, 0.4), t, 0.35)
            elif preset == 'music-box':
                if rnd.random() < density:
                    melody_deg = int(np.clip(melody_deg + rnd.integers(-2, 3), 0, 9))
                    place(music_box(midi_to_hz(deg(ch + melody_deg, 1)), 1.0), t, 0.32)
            elif preset == 'chiptune':
                d = ch + [0, 4, 2, 4, 7, 4, 2, 4][s]
                place(chip(midi_to_hz(deg(d)), beat / 2.2), t, 0.16)
                if s % 4 == 0:
                    place(chip(midi_to_hz(deg(ch, -2)), beat * 0.9), t, 0.14)
            elif preset == 'pulse':
                if s % 2 == 0:
                    place(kick(0.35), t, 0.55)
                place(hat(0.05, s + b), t + beat / 4, 0.12)
                if s % 4 == 0:
                    place(pluck(midi_to_hz(deg(ch, -1)), beat * 1.8, 0.2), t, 0.3)
            elif preset == 'lofi':
                if s % 4 == 0:
                    place(kick(0.3), t, 0.35)
                if s % 4 == 2:
                    place(bandpass(noise(0.12, s), 1500, 5000) * np.exp(-t_axis(0.12) * 30), t, 0.15)
                if rnd.random() < density * 0.5:
                    place(bell(midi_to_hz(deg(ch + int(rnd.integers(0, 5)), 1)), 0.9), t, 0.12)
            elif preset == 'pad':
                if s % 4 == 0 and rnd.random() < density:
                    place(bell(midi_to_hz(deg(ch + int(rnd.integers(0, 5)), 1)), 1.4), t, 0.12)
    out = out[:int(total * SR)]
    # gentle fade in/out (or loop crossfade)
    fi, fo = int(0.05 * SR), int(0.8 * SR)
    out[:fi] *= np.linspace(0, 1, fi)
    if not m.get('loop'):
        out[-fo:] *= np.linspace(1, 0, fo)
    return out * m.get('gain', 0.5)


def simple_reverb(x, mix=0.18):
    ir_len = int(1.2 * SR)
    t = np.arange(ir_len) / SR
    ir = np.random.default_rng(9).uniform(-1, 1, ir_len) * np.exp(-t * 4.5)
    ir = lowpass(ir, 5000)
    wet = signal.fftconvolve(x, ir)[:len(x)]
    wet /= (np.max(np.abs(wet)) + 1e-9)
    return x * (1 - mix) + wet * mix * np.max(np.abs(x))


def render(spec):
    total = float(spec['duration'])
    mus = gen_music(spec, total)
    fx = np.zeros_like(mus)
    for i, ev in enumerate(spec.get('events', [])):
        x = sfx(ev['type'], ev.get('note', 'A5'), ev.get('dur'), seed=spec.get('seed', 1) * 100 + i)
        g = ev.get('gain', 0.8)
        s = int(ev['t'] * SR)
        if s >= len(fx):
            continue
        e = min(len(fx), s + len(x))
        fx[s:e] += x[:e - s] * g
    mix = simple_reverb(mus + fx * 0.9, spec.get('reverb', 0.18))
    # stereo: slight Haas widening on music
    L = mix
    R = np.concatenate([np.zeros(int(0.008 * SR)), mix])[:len(mix)] * 0.9 + mix * 0.1
    st = np.stack([L, R], 1)
    peak = np.max(np.abs(st)) + 1e-9
    st = st / peak * 10 ** (-1 / 20)
    rms = np.sqrt(np.mean(st ** 2)) + 1e-9
    target = 10 ** (-18 / 20)
    if rms > target:  # never louder than -18 dBFS RMS
        st *= target / rms
    return (st * 32767).astype(np.int16)


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == '--demo':
        spec = {'duration': 12, 'seed': 2, 'bpm': 100, 'key': 'D', 'scale': 'majpent', 'music': {'preset': 'pluck-arp'},
                'events': [{'t': 0.2, 'type': 'whoosh'}, {'t': 1.0, 'type': 'impact'}, {'t': 2, 'type': 'pop'},
                           {'t': 3, 'type': 'chime', 'note': 'A5'}, {'t': 4, 'type': 'tick'}, {'t': 5, 'type': 'coin', 'note': 'E6'},
                           {'t': 6, 'type': 'riser'}, {'t': 7.5, 'type': 'thud'}, {'t': 8, 'type': 'glass', 'note': 'C6'},
                           {'t': 9, 'type': 'swell', 'note': 'D4'}]}
        out = sys.argv[2]
    else:
        spec = json.load(open(sys.argv[1]))
        out = sys.argv[2]
    wavfile.write(out, SR, render(spec))
    print(out)


if __name__ == '__main__':
    main()
