# Faits techniques vérifiés

Chaque ligne vient d'une mesure ou d'un test fait pendant cette campagne (date : 2026-11-03).
Les faits hérités de la mission (§4) sont repris en fin de fichier ; les nôtres sont en premier.

## Environnement mesuré (Phase 0)

| Élément | Valeur |
|---|---|
| `nproc` | **4** cœurs, 15 Go RAM, pas de GPU (WebGL via SwiftShader) |
| Node / npm | v22.23.4 / 10.9.9 |
| Playwright / Chromium | 1.63.0 préinstallé (`/opt/pw-browsers`), **non réinstallé** |
| ffmpeg | 6.1.1 (libx264) |
| Python | 3.11 via `uv venv --python 3.11 .venv` (le système est en 3.13) |
| Libs JS | three 0.187.0, matter-js 0.20.0, **p5 2.3.4**, gsap 3.15.0, d3 7.9.2, aframe 1.8.0, pixi.js 8.22.0, babylonjs 9.33.2, zdog 1.1.3, paper 0.17.0, **animejs 4.5.0**, flubber 0.4.2, roughjs 4.6.6, twgl.js 7.0.0 |
| Libs Python | manim 0.22.1, taichi 1.7.4, numpy 2.4.6, scipy 1.17.1, opencv 5.0.0 (headless), pycairo 1.29.2, matplotlib 3.11.2, Pillow 13.0.0, google-genai 2.34.0 |

## Faits nouveaux (vérifiés ici)

- **manimpango ne compile pas** (pangocairo absent). Procédure qui marche : `uv pip install --no-deps manim`, puis ses dépendances listées par `importlib.metadata.requires('manim')` sans manimpango, puis un **stub** `manimpango/__init__.py` exposant `list_fonts, register_font, unregister_font, MarkupUtils, PangoUtils, TextSetting, Alignment` + un `manimpango-0.7.1.dist-info/METADATA`. `import manim` passe alors ; `Text()` est indisponible -> texte par overlays PNG (`out/tools/textpng.py`). `MathTex` demande LaTeX, **absent** de l'environnement : ne pas l'utiliser.
- **PIL lit directement les `.woff2` de @fontsource** (`ImageFont.truetype(...woff2)`), pas besoin de TTF. Le sous-ensemble `latin` couvre les accents français.
- **ESM + Playwright préinstallé** : `import { chromium } from 'playwright'` échoue en ESM (NODE_PATH ignoré) ; utiliser `createRequire(import.meta.url)('playwright')`.
- **Heredoc dans une commande shell longue** : une commande Bash contenant un heredoc suivi d'autres commandes a été aplatie et a bloqué 5 min en attente de `EOF`. Écrire les fichiers avec un outil d'écriture, pas en heredoc inline au milieu d'une chaîne.
- **A-Frame 1.8** headless : fonctionne avec SwiftShader ; un petit bouton XR apparaît en bas à droite -> `xr-mode-ui="enabled:false"` + CSS `.a-enter-vr,.a-enter-ar{display:none!important}` (template : `out/tools/templates/aframe-template.html`).
- **p5 est en version 2.x** (2.3.4) : `preload()` n'existe plus (setup async), certaines API changent. **anime.js est en v4** : API par imports nommés (`animate`, `createTimeline`, `stagger`), plus de `anime({...})` global.
- **Temps de rendu mesurés (4 cœurs, 1 rendu)** : three.js InstancedMesh 800 + UnrealBloom 1080×1920 : **59,8 s / 100 frames** (90 frames en 53,8 s). Manim 3 s (3 animations simples, 1080×1920) : **4,3 s** au total. Taichi 20 k particules + flou cv2 + pipe ffmpeg, 90 frames : **8,5 s**. Still A-Frame (12 sphères) : 1,5 s.
- **Gemini TTS** : la clé `GEMINI_API_KEY` **n'était pas présente** dans le conteneur au moment des rendus (l'API répond 403 « unregistered callers ») ; l'hôte de documentation `aistudio.google.com` est hors de la politique réseau. `out/tools/tts.py` est prêt (SDK google-genai 2.34, `SpeechConfig/PrebuiltVoiceConfig`, modèle `gemini-3.8-flash-tts` puis repli `gemini-3.8-flash-lite-tts`) et se lance dès que la clé est disponible.
- **Poids des livrables** : crf 14 sur particules+bloom = 9,3 Mo/3 s ; ré-encodage livrable crf 20 + maxrate 8M = 3,8 Mo/3 s (plafond ≈ 15 Mo pour 15 s).
- **Niveau sonore** : `sound.py` normalise à crête −1 dBFS et RMS ≤ −18 dBFS ; après mux AAC le mix mesure **−21,1 dB moyen / −0,8 dB crête** (volumedetect).
- **Slots CPU** : `render.mjs` réserve un slot parmi `nproc` (verrous `mkdir` atomiques dans `/tmp/svi-slots`) ; plusieurs agents peuvent lancer des rendus sans dépasser 4 rendus simultanés. Pour les rendus Python lourds, utiliser `out/tools/slot.sh <commande>`.

## Faits hérités de la mission (§4) — appliqués d'emblée

- Pipeline navigateur : serveur statique local -> `page.evaluate(t => window.renderAt(t), f/30)` -> `screenshot jpeg q92` -> `image2pipe` ffmpeg `libx264 veryfast crf 14 yuv420p` -> `.part.mp4` renommé.
- Flags Chromium : `--use-angle=swiftshader --enable-unsafe-swiftshader --ignore-gpu-blocklist --disable-accelerated-2d-canvas`.
- Contrat : `window.ready`, `window.renderAt(t)` ; `window.SEQUENTIAL = true` pour les scènes à état.
- GSAP : `renderAt = t => { tl.seek(t, false); }` (ne jamais retourner la timeline : thenable) ; `immediateRender:false` sur les `fromTo`.
- A-Frame : `geometry`/`material` en chaînes ; caméra via `Matrix4.lookAt` ; `renderer.setAnimationLoop(null)` + `scene.pause()` puis rendu manuel.
- regl ne rend que sa première frame -> twgl.js ou ShaderMaterial three.js.
- > ~500 entités -> `InstancedMesh`.
- Manim : `frame_width=9, frame_height=16, 1080×1920`.
- Taichi MPM : `dt ≤ 1e-4`, `E ≈ 400–1000`, clamp, 80–130 substeps/frame, accumulation de points + flou gaussien.
- Matter.js : pré-simuler en Node pur pour choisir les graines, puis rendre. Nudge anti-blocage si pas de progrès > 1,2 s.
- Assemblage : `xfade` 0,5–1 s, `tpad=stop_mode=clone`, overlays PNG `fade…:alpha=1`, durées `0.45` pas `.45`.
- Stills + planche-contact AVANT le rendu complet.
- Budgets (2 cœurs, campagne précédente) : three.js ~1 min/100 frames ; A-Frame avec ombres 5–10 min/100 frames ; Blender Cycles 25–30 s/frame.

## Mesures ajoutées par les studios (Phase 2)

<!-- Les mesures par short sont dans out/shorts/*/short.json (renderTimeSec) et agrégées ici en Phase 4. -->
