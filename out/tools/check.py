#!/usr/bin/env python3
"""
check.py — contrôle qualité automatique d'un dossier de short (ou de tous).

USAGE
  python out/tools/check.py out/shorts/<dossier>         # un short
  python out/tools/check.py --all                        # tous les shorts -> out/report/qa.json

Vérifie : short.mp4 lisible par ffprobe, 1080×1920, 30 fps, H.264 yuv420p, durée 10–20 s, piste audio présente,
absence de frames noires (blackdetect ≥ 0.25 s) et figées longues (freezedetect ≥ 3 s, avertissement seulement),
présence de short.json / narration.json / stills (3–5) / src/. Imprime un JSON {ok, errors, warnings}.
"""
import json, subprocess, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def probe(p):
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
                                   'stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt:format=duration',
                                   '-of', 'json', str(p)])
    return json.loads(out)


def check(d):
    d = Path(d)
    err, warn = [], []
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
            if not (9.9 <= dur <= 20.1): err.append(f'durée {dur:.2f}s hors 10–20 s')
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
    return {'short': d.name, 'ok': not err, 'errors': err, 'warnings': warn, 'info': info}


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        res = [check(p) for p in sorted((ROOT / 'out' / 'shorts').iterdir()) if p.is_dir()]
        (ROOT / 'out' / 'report' / 'qa.json').write_text(json.dumps(res, indent=1, ensure_ascii=False))
        for r in res:
            print(('OK  ' if r['ok'] else 'FAIL'), r['short'], '; '.join(r['errors'] + r['warnings']))
        print(f"{sum(r['ok'] for r in res)}/{len(res)} OK")
    else:
        print(json.dumps(check(sys.argv[1]), indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
