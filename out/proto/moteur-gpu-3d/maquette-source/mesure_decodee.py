# Scintillement A-B-A sur fichier décodé (méthode de la note survol-pixel) : 1 pixel par gros pixel, 30 i/s, seuil 24.
import subprocess, sys, numpy as np
def frames(path, w, h, vf):
    raw = subprocess.run(['ffmpeg','-loglevel','error','-i',path,'-vf',vf,'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).astype(np.int16)
path, kind = sys.argv[1], sys.argv[2]
if kind == 'source':   # 1486x1080 à 60 i/s, gros pixels de 4 : centre de chaque bloc ; on retire le bandeau de texte du bas
    f = frames(path, 371, 250, 'fps=30,crop=1484:1000:0:0,scale=371:250:flags=neighbor')
else:
    f = frames(path, 270, 480, 'scale=270:480:flags=neighbor')
d02 = np.abs(f[:-2]-f[2:]).max(3) < 24
d01 = np.abs(f[:-2]-f[1:-1]).max(3) >= 24
x = d02 & d01
ch = (np.abs(f[1:]-f[:-1]).max(3) >= 24).reshape(len(f)-1,-1).mean(1)*100
per = x.reshape(len(x),-1).mean(1)*100
print(kind, 'images', len(f), 'ABA moyen %.2f %%' % per.mean(), 'par seconde', np.round([per[i:i+30].mean() for i in range(0,len(per),30)],2), 'pixels changés %.1f %%' % ch.mean())
