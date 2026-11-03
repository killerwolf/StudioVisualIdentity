#!/usr/bin/env python3
"""
assemble.py — assemblage ffmpeg des shorts (mux son, voix off, overlays, concat xfade).

SOUS-COMMANDES
  mux     : vidéo muette + musique/SFX (+ voix off optionnelle) -> short.mp4
            (ré-encode en crf 20, maxrate 8M : poids livrable ~4–15 Mo ; --copy pour garder le flux crf 14)
     python out/tools/assemble.py mux --video v.mp4 --music sound.wav [--voice voice.wav] --out short.mp4
            [--music-db -18] [--voice-db -3] [--overlay over.png:START:END[:FADE]] ...
     - La piste audio est coupée/complétée à la durée exacte de la vidéo (apad + atrim).
     - Avec --voice, la musique est automatiquement « duckée » (sidechaincompress) sous la voix.
     - --overlay : PNG RGBA plein cadre 1080×1920 (voir textpng.py), fondu entrée/sortie alpha.
  concat  : enchaîne des clips avec xfade
     python out/tools/assemble.py concat --clips a.mp4 b.mp4 c.mp4 --out x.mp4 [--xfade fade] [--dur 0.5]
     - les clips doivent avoir même taille/fps ; tpad=stop_mode=clone évite les trous.
  frames  : extrait des frames d'un mp4 (vérification)
     python out/tools/assemble.py frames --video short.mp4 --times 1,7,14 --dir stills/ [--prefix final]
  sheet   : planche-contact d'images (PIL)
     python out/tools/assemble.py sheet --images a.jpg b.jpg ... --out sheet.jpg [--cols 3] [--thumb 360] [--labels "A,B,C"]

Toutes les durées sont écrites avec un zéro initial (0.45 et non .45) — piège ffmpeg connu.
"""
import argparse, json, os, subprocess, sys
from pathlib import Path


def run(cmd):
    print('+', ' '.join(str(c) for c in cmd), file=sys.stderr)
    r = subprocess.run([str(c) for c in cmd])
    if r.returncode != 0:
        sys.exit(r.returncode)


def probe_duration(path):
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)])
    return float(out.strip())


def f2(x):
    return f'{float(x):.3f}'


def cmd_mux(a):
    dur = probe_duration(a.video)
    inputs = ['-i', a.video]
    vf_chain = []
    idx = 1
    ov_labels = []
    for ov in a.overlay or []:
        parts = ov.split(':')
        png, st, en = parts[0], float(parts[1]), float(parts[2])
        fd = float(parts[3]) if len(parts) > 3 else 0.3
        inputs += ['-loop', '1', '-t', f2(dur), '-i', png]
        ov_labels.append((idx, st, en, fd))
        idx += 1
    music_idx = voice_idx = None
    if a.music:
        inputs += ['-i', a.music]; music_idx = idx; idx += 1
    if a.voice:
        inputs += ['-i', a.voice]; voice_idx = idx; idx += 1

    fc = []
    vlast = '0:v'
    for k, (i, st, en, fd) in enumerate(ov_labels):
        fo_st = max(st, en - fd)
        fc.append(f'[{i}:v]format=rgba,fade=t=in:st={f2(st)}:d={f2(fd)}:alpha=1,fade=t=out:st={f2(fo_st)}:d={f2(fd)}:alpha=1[o{k}]')
        fc.append(f'[{vlast}][o{k}]overlay=0:0:enable=\'between(t,{f2(st)},{f2(en)})\'[v{k}]')
        vlast = f'v{k}'
    amap = None
    mg = 10 ** (a.music_db / 20) / 10 ** (-18 / 20)  # sound.py normalise déjà à ~-18 dBFS RMS
    if music_idx is not None and voice_idx is not None:
        vg = 10 ** (a.voice_db / 20)
        fc.append(f'[{music_idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={mg:.3f},apad,atrim=0:{f2(dur)}[m]')
        fc.append(f'[{voice_idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={vg:.3f},apad,atrim=0:{f2(dur)},asplit=2[vo][sc]')
        fc.append('[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[md]')
        fc.append('[md][vo]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[aout]')
        amap = '[aout]'
    elif music_idx is not None:
        fc.append(f'[{music_idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={mg:.3f},apad,atrim=0:{f2(dur)}[aout]')
        amap = '[aout]'
    elif voice_idx is not None:
        fc.append(f'[{voice_idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,apad,atrim=0:{f2(dur)}[aout]')
        amap = '[aout]'

    cmd = ['ffmpeg', '-y', '-loglevel', 'error'] + inputs
    if fc:
        cmd += ['-filter_complex', ';'.join(fc)]
    vmap = '0:v' if vlast == '0:v' else f'[{vlast}]'
    cmd += ['-map', vmap]
    if amap:
        cmd += ['-map', amap]
    if a.copy and not ov_labels:
        cmd += ['-c:v', 'copy']
    else:  # livrable : crf 20 plafonné à 8 Mb/s (~15 Mo max pour 15 s) — l'intermédiaire de rendu reste en crf 14
        cmd += ['-c:v', 'libx264', '-preset', 'faster', '-crf', str(a.crf), '-maxrate', '8M', '-bufsize', '16M',
                '-pix_fmt', 'yuv420p', '-r', '30']
    cmd += ['-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-t', f2(dur), '-movflags', '+faststart', a.out]
    run(cmd)
    print(a.out)


def cmd_concat(a):
    clips = a.clips
    if len(clips) == 1:
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', clips[0], '-c', 'copy', a.out]); return
    durs = [probe_duration(c) for c in clips]
    inputs = []
    for c in clips:
        inputs += ['-i', c]
    fc = []
    for i in range(len(clips)):
        fc.append(f'[{i}:v]settb=AVTB,fps=30,format=yuv420p,tpad=stop_mode=clone:stop_duration={f2(a.dur)}[c{i}]')
    last = 'c0'
    offset = 0.0
    for i in range(1, len(clips)):
        offset += durs[i - 1] - a.dur if i == 1 else durs[i - 1] - a.dur
        fc.append(f'[{last}][c{i}]xfade=transition={a.xfade}:duration={f2(a.dur)}:offset={f2(offset)}[x{i}]')
        last = f'x{i}'
    total = sum(durs) - a.dur * (len(clips) - 1)
    fc.append(f'[{last}]trim=0:{f2(total)}[vout]')
    run(['ffmpeg', '-y', '-loglevel', 'error'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[vout]',
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', '30', a.out])
    print(a.out)


def cmd_frames(a):
    os.makedirs(a.dir, exist_ok=True)
    for t in [float(x) for x in a.times.split(',')]:
        out = os.path.join(a.dir, f'{a.prefix}_{t:05.2f}s.jpg')
        run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f2(t), '-i', a.video, '-frames:v', '1', '-q:v', '3', out])
        print(out)


def cmd_sheet(a):
    from PIL import Image, ImageDraw, ImageFont
    ims = [Image.open(p).convert('RGB') for p in a.images]
    tw = a.thumb
    th = int(tw * 1920 / 1080)
    labels = a.labels.split(',') if a.labels else None
    lab_h = 44 if labels else 0
    cols = a.cols
    rows = (len(ims) + cols - 1) // cols
    gap = 8
    sheet = Image.new('RGB', (cols * tw + (cols + 1) * gap, rows * (th + lab_h) + (rows + 1) * gap), (18, 18, 20))
    d = ImageDraw.Draw(sheet)
    root = Path(__file__).resolve().parents[2]
    try:
        font = ImageFont.truetype(str(root / 'node_modules/@fontsource/inter/files/inter-latin-700-normal.woff2'), 26)
    except Exception:
        font = ImageFont.load_default()
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        x = gap + c * (tw + gap)
        y = gap + r * (th + lab_h + gap)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + lab_h))
        if labels and i < len(labels):
            d.text((x + 4, y + 6), labels[i].strip(), fill=(235, 235, 235), font=font)
    sheet.save(a.out, quality=88)
    print(a.out)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest='cmd', required=True)
    m = sp.add_parser('mux')
    m.add_argument('--video', required=True); m.add_argument('--music'); m.add_argument('--voice')
    m.add_argument('--out', required=True); m.add_argument('--music-db', type=float, default=-18)
    m.add_argument('--voice-db', type=float, default=-1.0)
    m.add_argument('--overlay', action='append')
    m.add_argument('--crf', type=int, default=20); m.add_argument('--copy', action='store_true', help='copie le flux vidéo sans ré-encodage')
    c = sp.add_parser('concat')
    c.add_argument('--clips', nargs='+', required=True); c.add_argument('--out', required=True)
    c.add_argument('--xfade', default='fade'); c.add_argument('--dur', type=float, default=0.5)
    f = sp.add_parser('frames')
    f.add_argument('--video', required=True); f.add_argument('--times', required=True)
    f.add_argument('--dir', required=True); f.add_argument('--prefix', default='final')
    s = sp.add_parser('sheet')
    s.add_argument('--images', nargs='+', required=True); s.add_argument('--out', required=True)
    s.add_argument('--cols', type=int, default=3); s.add_argument('--thumb', type=int, default=360)
    s.add_argument('--labels')
    a = p.parse_args()
    {'mux': cmd_mux, 'concat': cmd_concat, 'frames': cmd_frames, 'sheet': cmd_sheet}[a.cmd](a)


if __name__ == '__main__':
    main()
