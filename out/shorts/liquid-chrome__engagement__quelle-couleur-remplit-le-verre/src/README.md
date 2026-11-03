# Reproduire « Quelle couleur remplit le verre en premier ? » (Chrome Liquide · engagement)

Scène three.js 0.187 sans état (renderAt(t) pur), texte HTML (Syne 800 / Inter 500-600 @fontsource). Graine 7.

```bash
node out/tools/render.mjs out/shorts/liquid-chrome__engagement__quelle-couleur-remplit-le-verre/src/index.html --out /tmp/svi/liquid-b/video.mp4 --duration 15 && .venv/bin/python out/tools/sound.py out/shorts/liquid-chrome__engagement__quelle-couleur-remplit-le-verre/src/sound.json /tmp/svi/liquid-b/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/liquid-b/video.mp4 --music /tmp/svi/liquid-b/music.wav --out out/shorts/liquid-chrome__engagement__quelle-couleur-remplit-le-verre/short.mp4
```

Fichiers : `index.html` (scène, course analytique `RATES`, ralenti τ(t)), `sound.json` (pulse 120 bpm + SFX calés sur départ, pari, ralenti, victoire, CTA).
