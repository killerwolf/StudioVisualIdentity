#!/usr/bin/env python3
"""
tts.py — voix off Gemini TTS à partir d'un narration.json, calée sur les horodatages, puis remix du short.

PRÉREQUIS : variable d'environnement GEMINI_API_KEY (ou GOOGLE_API_KEY) ; `pip install google-genai` (>= 2.30).
Sans clé, le script s'arrête proprement (code 3) sans toucher aux fichiers : le short muet+musique reste valide.

USAGE
  python out/tools/tts.py out/shorts/<dossier>                 # génère voice.wav + short_vo.mp4
  python out/tools/tts.py out/shorts/<dossier> --replace       # remplace short.mp4 (l'original -> short_novo.mp4)
  python out/tools/tts.py --all [--replace]                    # tous les shorts
  options : --model gemini-3.8-flash-tts  --voice Kore  --dry-run

FORMAT narration.json (cf. mission §6) :
  {"language": "fr", "style": "enjoué, pour enfants de 6-10 ans", "voice": "Leda" (optionnel),
   "lines": [{"t": 0.3, "maxDuration": 2.5, "text": "…"}, …]}
Chaque ligne est synthétisée séparément avec la consigne de style, puis posée à son temps t. Si l'audio
dépasse maxDuration, il est accéléré (atempo ≤ 1.35) ; au-delà, il déborde et un avertissement est noté.
La musique est duckée sous la voix par assemble.py mux (sidechaincompress).
Les fichiers sources (music.wav / video_silent.mp4) doivent exister dans le dossier du short (src/ ou racine).
"""
import argparse, re, base64, io, json, os, subprocess, sys, time, wave
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy import signal

ROOT = Path(__file__).resolve().parents[2]
SR = 48000
MODELS = ['gemini-3.8-flash-lite-tts', 'gemini-3.1-flash-tts-preview', 'gemini-3.8-flash-tts']
MIN_GAP = 21  # s entre deux requêtes (limite mesurée : ~3 requêtes/min en plan gratuit)
# voix préconstruites Gemini TTS (mapping indicatif par style)
VOICE_BY_STYLE = [('enfant', 'Leda'), ('conte', 'Aoede'), ('calme', 'Achernar'), ('doux', 'Sulafat'),
                  ('énergique', 'Puck'), ('enjoué', 'Puck'), ('dramatique', 'Charon'), ('grave', 'Charon'),
                  ('documentaire', 'Orus'), ('pédagogique', 'Kore'), ('clair', 'Kore'), ('quiz', 'Fenrir'),
                  ('mystérieux', 'Enceladus'), ('chuchoté', 'Enceladus'), ('journal', 'Iapetus'), ('rétro', 'Algenib')]


def pick_voice(style, override=None):
    if override:
        return override
    s = (style or '').lower()
    for k, v in VOICE_BY_STYLE:
        if k in s:
            return v
    return 'Kore'


def pcm_from_part(data, mime):
    """Gemini renvoie soit du WAV (audio/wav), soit du PCM L16 brut 24 kHz mono (audio/L16;rate=24000)."""
    if isinstance(data, str):
        data = base64.b64decode(data)
    mime = (mime or '').lower()
    if 'wav' in mime or data[:4] == b'RIFF':
        sr, x = wavfile.read(io.BytesIO(data))
    else:
        rate = 24000
        for tok in mime.split(';'):
            if 'rate=' in tok:
                rate = int(tok.split('=')[1])
        sr, x = rate, np.frombuffer(data, dtype='<i2')
    x = x.astype(np.float32)
    if x.ndim > 1:
        x = x.mean(1)
    x /= 32768.0
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    return x


def synth(client, text, style, voice, lang, model):
    from google.genai import types
    # IMPORTANT : tout préfixe de consigne ("Dis d'un ton…") est LU À VOIX HAUTE par le modèle (mesuré : 3,1 s -> 6,1 s).
    # On envoie donc le texte seul ; le style passe par le choix de la voix. `style` et `lang` restent informatifs.
    prompt = text
    cfg = types.GenerateContentConfig(
        response_modalities=['AUDIO'],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice))))
    last = None
    for m in [model] + [x for x in MODELS if x != model]:
        for attempt in range(12):
            try:
                r = client.models.generate_content(model=m, contents=prompt, config=cfg)
                part = r.candidates[0].content.parts[0].inline_data
                time.sleep(MIN_GAP)  # une génération après l'autre, jamais en parallèle
                return pcm_from_part(part.data, part.mime_type), m
            except Exception as e:
                last = e
                msg = str(e)
                if 'RESOURCE_EXHAUSTED' in msg:
                    if 'PerDay' in msg:
                        break  # quota journalier épuisé : modèle suivant
                    mm = re.search(r"retryDelay': '([\d.]+)s", msg)
                    time.sleep(float(mm.group(1)) + 1 if mm else 20)  # limite par minute : on attend
                else:
                    time.sleep(2 ** min(attempt, 4))
    raise RuntimeError(f'TTS failed: {last}')


def trim_silence(x, th=0.01):
    idx = np.where(np.abs(x) > th)[0]
    if len(idx) == 0:
        return x
    return x[max(0, idx[0] - 480): idx[-1] + 2400]


def atempo(x, factor):
    tmp_in, tmp_out = '/tmp/svi_tts_in.wav', '/tmp/svi_tts_out.wav'
    wavfile.write(tmp_in, SR, (x * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp_in, '-filter:a', f'atempo={factor:.3f}', tmp_out], check=True)
    return wavfile.read(tmp_out)[1].astype(np.float32) / 32768.0


def find(d, names):
    for n in names:
        for p in (d / n, d / 'src' / n):
            if p.exists():
                return p
    return None


def process(d, a, client):
    d = Path(d)
    nar = json.load(open(d / 'narration.json'))
    sj = json.load(open(d / 'short.json')) if (d / 'short.json').exists() else {}
    dur = float(sj.get('duration', 15))
    voice = pick_voice(nar.get('style'), a.voice or nar.get('voice'))
    track = np.zeros(int((dur + 1) * SR), np.float32)
    report = []
    for ln in nar['lines']:
        x, used = synth(client, ln['text'], nar.get('style', 'naturel'), voice, nar.get('language', 'fr'), a.model)
        x = trim_silence(x)
        maxd = float(ln.get('maxDuration', 99))
        L = len(x) / SR
        if L > maxd:
            f = min(1.35, L / maxd)
            x = atempo(x, f)
        s = int(float(ln['t']) * SR)
        e = min(len(track), s + len(x))
        track[s:e] += x[:e - s]
        report.append({'t': ln['t'], 'sec': round(len(x) / SR, 2), 'max': maxd, 'over': round(len(x) / SR - maxd, 2) > 0.05, 'model': used})
    track = track[:int(dur * SR)]
    pk = np.max(np.abs(track)) + 1e-9
    track = track / pk * 0.89
    wavfile.write(d / 'voice.wav', SR, (np.stack([track, track], 1) * 32767).astype(np.int16))
    # source vidéo : short_novo.mp4 (si déjà remplacé) > video_silent.mp4 > short.mp4 ; musique : music.wav ou piste de la source
    video = find(d, ['short_novo.mp4', 'video_silent.mp4', 'short.mp4'])
    music = find(d, ['music.wav', 'sound.wav'])
    if music is None and video is not None:
        music = Path('/tmp') / f'svi_music_{d.name}.wav'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(video), '-vn', '-ac', '2', '-ar', str(SR), str(music)], check=True)
        # la piste extraite est déjà au niveau du mix final -> on la baisse de 2 dB de plus sous la voix
    out = d / 'short_vo.mp4'
    if video is None:
        print(f'[tts] {d.name}: aucune vidéo source -> voice.wav seulement', file=sys.stderr)
    else:
        cmd = [sys.executable, str(ROOT / 'out/tools/assemble.py'), 'mux', '--video', str(video), '--voice', str(d / 'voice.wav'), '--out', str(out)]
        if music:
            cmd += ['--music', str(music), '--music-db', '-20']
        subprocess.run(cmd, check=True)
        if a.replace:
            if not (d / 'short_novo.mp4').exists():
                os.replace(d / 'short.mp4', d / 'short_novo.mp4')
            os.replace(out, d / 'short.mp4')
    sj.setdefault('sound', {})['voice'] = True
    sj['sound']['voiceEngine'] = report[0]['model'] if report else None
    sj['sound']['voiceName'] = voice
    json.dump(sj, open(d / 'short.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(report, open(d / 'voice_report.json', 'w'), indent=1)
    print(f'[tts] {d.name}: {len(report)} lignes, voix {voice}, débordements: {sum(r["over"] for r in report)}')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('dir', nargs='?'); p.add_argument('--all', action='store_true')
    p.add_argument('--model', default=MODELS[0]); p.add_argument('--voice')
    p.add_argument('--replace', action='store_true'); p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    dirs = sorted(x for x in (ROOT / 'out/shorts').iterdir() if (x / 'narration.json').exists()) if a.all else [Path(a.dir)]
    if a.dry_run:
        for d in dirs:
            n = json.load(open(d / 'narration.json'))
            print(d.name, pick_voice(n.get('style')), len(n['lines']), 'lignes')
        return
    if not key:
        print('[tts] GEMINI_API_KEY absent : voix off non générée (le short sans voix reste valide).', file=sys.stderr)
        sys.exit(3)
    from google import genai
    client = genai.Client(api_key=key)
    for d in dirs:
        try:
            process(d, a, client)
        except Exception as e:
            print(f'[tts] ÉCHEC {d.name}: {e}', file=sys.stderr)


if __name__ == '__main__':
    main()
