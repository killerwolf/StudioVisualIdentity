#!/usr/bin/env python3
"""planche.py <video.mp4> <chemin.json> <planche.jpg> [t1,t2,...] — 6 images de la vidéo livrée (3×2, 360×640 chacune) :
titre, fouetté du couplet (mi-transition vers le flanc gauche), une ligne du couplet (pont droit), le refrain (pont gauche),
milieu du zoom arrière, image finale. Le temps est inscrit en bas de chaque vignette."""
import json, subprocess, sys, tempfile, os

vid, data, out = sys.argv[1:4]
D = json.load(open(data)); L = {l['arete']: l for l in D['lignes']}; beat = 60 / D['bpm']
if len(sys.argv) > 4: ts = [float(x) for x in sys.argv[4].split(',')]
else:
    cg = L['coqueG']; z0, z1 = D['zoomArriere']
    ts = [L['titre']['u'][-1][1] + 0.3, cg['arr'] - cg['temps'] * beat / 2, L['pontD']['u'][-1][1] + 0.15,
          L['pontG']['u'][-1][1] + 0.1, (z0 + z1) / 2, D['duree'] - 0.1]
tmp = tempfile.mkdtemp()
font = '/System/Library/Fonts/Supplemental/Arial.ttf'
for i, t in enumerate(ts):
    dt = f",drawtext=fontfile={font}:text='{t:.2f} s':x=12:y=h-40:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.6" if False else ''  # drawtext absent de ce ffmpeg
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', vid, '-frames:v', '1', '-vf', f'scale=360:640{dt}', f'{tmp}/{i}.png'], check=True)
ins = sum([['-i', f'{tmp}/{i}.png'] for i in range(6)], [])
lay = '0_0|360_0|720_0|0_640|360_640|720_640'
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', f'xstack=inputs=6:layout={lay}', '-q:v', '3', out], check=True)
print(out, ' '.join(f'{t:.2f}' for t in ts))
