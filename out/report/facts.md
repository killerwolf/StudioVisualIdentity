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
- **Gemini TTS** *(historique — abandonné, voir « Voix off Fish Audio » plus bas)* : la clé `GEMINI_API_KEY` **n'était pas présente** dans le conteneur au moment des rendus (l'API répond 403 « unregistered callers ») ; l'hôte de documentation `aistudio.google.com` est hors de la politique réseau. `out/tools/tts.py` est prêt (SDK google-genai 2.34, `SpeechConfig/PrebuiltVoiceConfig`, modèle `gemini-3.8-flash-tts` puis repli `gemini-3.8-flash-lite-tts`) et se lance dès que la clé est disponible.
- **Poids des livrables** : crf 14 sur particules+bloom = 9,3 Mo/3 s ; ré-encodage livrable crf 20 + maxrate 8M = 3,8 Mo/3 s (plafond ≈ 15 Mo pour 15 s).
- **Niveau sonore** : `sound.py` normalise à crête −1 dBFS et RMS ≤ −18 dBFS ; après mux AAC le mix mesure **−21,1 dB moyen / −0,8 dB crête** (volumedetect).
- **Slots CPU** : `render.mjs` réserve un slot parmi `nproc` (verrous `mkdir` atomiques dans `/tmp/svi-slots`) ; plusieurs agents peuvent lancer des rendus sans dépasser 4 rendus simultanés. Pour les rendus Python lourds, utiliser `out/tools/slot.sh <commande>`. Sur macOS (pas de `nproc`), `slot.sh` se replie sur `sysctl -n hw.ncpu` depuis le 2026-11-18 (avant, il bouclait sans fin) ; `render.mjs` lit `os.cpus().length`, qui marche partout. Les deux comptent les cœurs logiques (8 sur le Mac Intel i7 4 cœurs) : passer `SVI_SLOTS=4` pour un slot par cœur physique.

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

Conditions : 10 studios en parallèle sur 4 cœurs ; load average mesuré **16–22** (21:37 UTC) car seuls les rendus passent par les slots (ffmpeg, pré-simulations Node, compositions numpy n'y passent pas). Les coûts ci-dessous sont donc ×2–3 au-dessus d'une machine calme. Détail par short : `report/comparison.md` §2.

### Coûts de rendu mesurés (s / 100 frames, 1080×1920, sous contention)
| Technique | s/100 frames | Short source |
|---|---|---|
| D3 SVG + GSAP (aplats, peu de nœuds) | 13,7 – 20,5 | swiss-data ×2 |
| Manim (formes, sans texte) | 19,1 | tableau-craie/explicatif |
| Paper.js + flubber + anime.js (DOM/canvas 2D) | 28,2 – 31,7 | bauhaus-kinetic ×2 |
| GSAP DOM + canvas 2D (gravures hachurées) | 33,3 – 65,3 (+ OpenCV 21–28) | gazette-1900 ×2 |
| p5 v2 basse résolution ×4 (+ Matter) | 41,0 – 43,4 | pixel-arcade ×2 |
| twgl.js (shader GLSL plein cadre + points additifs) | 55,5 (+ OpenCV 32) | neon-lab/abstrait |
| Zdog (pseudo-3D plate) | 66,0 | pastel-diorama/enfants |
| A-Frame sans ombres | 82,9 | pastel-diorama/engagement |
| Taichi MPM 24 k particules 90×196, 80 substeps + shading cv2 | 105,6 (simulation 79 + shading 25) | liquid-chrome/abstrait |
| p5 v2 lavis précalculés + Paper.js | 109,2 – 117,6 | aquarelle-conte ×2 |
| D3 geo + GSAP + PNG pycairo | 128,7 – 135,7 | atlas-grave ×2 |
| three.js MeshPhysical iridescent + DOF | 178,0 | liquid-chrome/engagement |
| three.js + UnrealBloom | 182,9 (+ OpenCV 37) | neon-lab/explicatif |
| Rough.js SVG sous filtre plein cadre (feImage + flou) | **309,2** | tableau-craie/enfants |
| *3ᵉ shorts, 3 studios actifs seulement :* | | |
| PixiJS 8 ParticleContainer 17 094 cellules -> RenderTexture 270×480 ×4 | 32,6 (automate 0,11 en Node) | pixel-arcade/territoire |
| Matplotlib Agg 1080×1920, figure réutilisée + 2 fonds plein cadre | 52,8 (+ OpenCV 15,5) | neon-lab/effet papillon |
| Babylon.js 9 PBR + GlowLayer + DOF + reflet cube procédural | 123,2 | liquid-chrome/pendule |
| *Identités réhabilitées, 4 studios actifs (charge 15–23) :* | | |
| p5 v2 (calques d'encre en multiply) + GSAP à 12 i/s | 25,9 – 43,0 (+ OpenCV 28–36) | riso-zine ×2 |
| PixiJS 8 + GSAP (typo DOM plein cadre, stickers) | 49,8 – 58,5 (scène seule 0,2) | brut-meme ×2 |
| three.js terrain extrudé + shader courbes (texture D3 précalculée) | 108,2 – 169,0 | topo-relief ×2 |
| three.js planètes procédurales + bloom + grain + flare anamorphique | 174,9 – 186,4 | cosmos-doc ×2 |

- **La capture d'écran domine** : ~0,3 s par screenshot JPEG 1080×1920 alors que le JS de scène coûte 6–8 ms/frame (bauhaus-kinetic) ; Matter.js 0,024 s/100 frames de physique (pixel-arcade). Optimiser la scène n'a d'effet que sur les scènes WebGL lourdes ou les filtres SVG.
- **Filtres SVG plein cadre** (feTurbulence/feImage) = poste de coût n°1 en 2D : les remplacer par des textures PNG précalculées (pycairo/PIL) — fait par atlas-grave.
- **Verre en transmission three.js** (`MeshPhysicalMaterial.transmission`) ≈ 5 s/frame sous SwiftShader saturé : inutilisable ; simuler le verre par reflets d'environnement additifs.
- **Taichi MPM** : sans viscosité la « peinture » se comporte comme de l'eau ; μ 0,05, E 600, dt 1e-4, 80 substeps, 24 k particules sur grille 90×196 donne une peinture épaisse stable (liquid-chrome).

### Pièges nouveaux (vérifiés)
- **`Math.atan2` diffère au dernier bit entre Node 22 et Chromium** (0.17467219900823971 vs 0.1746721990082397) : une course Matter pré-simulée en Node divergeait dans le navigateur à la frame 102. Ne jamais construire la géométrie d'un monde rejoué avec `atan2`/`hypot` calculés des deux côtés : précalculer en Node et coder en dur. Vérifier par un mode `?verify=1` qui compare les temps d'arrivée.
- **Matter.js 0.20** colle les corps aux pentes < ~0,25 rad dès que `friction > 0` (même `frictionStatic: 0`) : friction 0 et `frictionAir` ≈ 0,014.
- **Dépôt `"type": "module"`** : un script Node de pré-simulation en `require()` a besoin d'un `package.json` `{"type":"commonjs"}` local.
- **GSAP `immediateRender:false`** sur `fromTo` : l'état de départ n'est pas posé avant le début du tween -> poser les états initiaux en CSS/attributs.
- **three.js + shader custom** : le rendu final applique sa conversion sRGB -> un ShaderMaterial « délavé » ; linéariser les couleurs du shader (`pow(c, 2.2)`).
- **Chromium/SwiftShader sous filtre SVG** : tracé fantôme intermittent avec des éléments à opacité 0 + rotation de 200° ; mettre `display:none` aux éléments effacés.
- **Manim 0.22** : `play(..., run_time=)` écrase la durée de chaque animation ; les `.animate` doivent passer par `prepare_animation` ; `insert_n_curves` plante sur un groupe vide ; pas d'`add_to_back` (utiliser `bring_to_back`) ; piloter la caméra par `renderer.time`.
- **Overlays ffmpeg** : 18 PNG plein cadre `-loop 1` + `fade` alpha > 8 min sous contention ; un compositeur numpy (lecture/écriture par pipes) prend ~40 s. Au-delà de ~5 overlays, composer en Python.
- **Polices** : Syne 800 à 92 px ≈ 75 px par caractère -> 11 caractères max par ligne en zone sûre ; Playfair a des chiffres elzéviriens par défaut (`font-variant-numeric: lining-nums`) ; certains glyphes (↻ ✓) manquent dans Baloo/Nunito -> SVG inline.
- **Débit de livrable** : le grain de film (OpenCV) sature le plafond 8 Mb/s (16–20 Mo / 15–19 s) ; les styles en aplats tombent sous 1 Mo pour 15 s.
- **Matplotlib ne lit pas les `.woff2`** (FreeType sans brotli, `FT_Open_Face` 0x55) : convertir les `.woff` @fontsource en `.ttf` avec fontTools, puis `matplotlib.font_manager.fontManager.addfont`. Les sous-ensembles d'une même police (latin / grec) partagent le nom de famille : renommer pour les déclarer en repli.
- **PixiJS 8 headless** : `await app.init({preserveDrawingBuffer:true, autoStart:false})` dans `window.ready`, ticker arrêté, `app.renderer.render(app.stage)` dans `renderAt` ; `ParticleContainer` + texture blanche 1×1 teintée pour > 10 k cellules ; RenderTexture basse résolution en `nearest` pour le pixel-art. Garder la simulation hors de Pixi (entiers + PRNG) pour la vérifier en Node.
- **Babylon.js 9 headless** : `new BABYLON.Engine(canvas, true, {preserveDrawingBuffer:true, stencil:true})`, jamais `runRenderLoop`, `await scene.whenReadyAsync()` puis `scene.render()` dans `renderAt` ; reflets via un environnement procédural capturé une fois en cube ; le sélecteur de GlowLayer par préfixe de nom attrape d'autres meshes -> noms explicites.
- **p5 v2 + save/restore manuel autour d'un clip** : le cache de style de p5 se désynchronise du contexte canvas ; un `stroke()` répété est ignoré et le trait disparaît — invisible sur des stills isolés, visible seulement en rendu séquentiel (riso-zine, 1 rendu jeté). Resynchroniser le style après chaque `restore()`.
- **d3.contours** sur une grille 256² : 224 ms une seule fois au chargement, rien par frame ; peindre les courbes dans une texture canvas pour three.js (topo-relief).
- **three.js : projeter une position monde vers l'écran** (flare, étiquettes) exige `camera.updateMatrixWorld()` avant `project()`, sinon on utilise la caméra de l'image précédente (cosmos-doc).
- **Glyphes manquants** : « → » rend un point en JetBrains Mono 700 ; mesurer les titres auto-ajustés avec `white-space: nowrap` sinon seul le premier mot est mesuré (brut-meme).
- **Workflow** : le moteur de workflow limite à 2 agents concurrents sur 4 CPU (min(16, CPU − 2)).

## Voix off Gemini TTS (mesures réelles)

- Modèles TTS visibles avec la clé : `gemini-3.8-flash-tts`, `gemini-3.8-flash-lite-tts`, `gemini-3.1-flash-tts-preview`, `gemini-2.5-*-preview-tts` (le 2.5 flash est refusé en 400). Réponse : `audio/wav` 24 kHz, lu tel quel par `pcm_from_part`.
- **Un préfixe de consigne dans le prompt est lu à voix haute** (3,1 s -> 6,1 s pour la même phrase) : `tts.py` envoie le texte seul.
- Plan gratuit : ~3 requêtes/min (pause de 21 s entre requêtes, attente du `retryDelay`) et ~10 requêtes/jour par modèle ; générations strictement séquentielles.
- Temps mesuré par short : swiss-data 177 s (6 lignes), pixel-arcade 153 s (6), liquid-chrome 125 s (5) ; neon-lab : échec immédiat (429 journalier).
- Débordements après ×1,35 : swiss-data 0 ; pixel-arcade 0 ; liquid-chrome 2 (ligne 2 : 2,27 s pour 2,0 ; ligne 5 : 1,03 s pour 0,9 ; texte non réécrit).
- Niveaux (moyenne / pic du short final) : swiss-data −17,5 / −1,3 dB ; pixel-arcade −20,6 / −1,7 dB ; liquid-chrome −18,1 / −1,6 dB. Réglages inchangés : musique −20 dB + sidechain, voix normalisée à 0,89. Durées identiques à la vidéo d'origine ; `check.py --all` : 23/23 OK.
- Le rendu de swiss-data (test) n'est pas conservé : à refaire avec le reste. Voix non écoutée, seulement mesurée.
- **API v1 contre v1beta (vérifié le 2026-11-18, voix de survol-pixel)** : le script `gemini_voix.py` du skill gemini-voices (google-genai, API `interactions`) appelle la version **v1** de l'API. En v1, `gemini-3.8-flash-tts` renvoie **404** (« Model … not found … set the API version to 'v1beta' »), `models.list` n'y montre aucun modèle `*-tts`, et le champ `speech_config` est refusé en **400** (« only available in v1beta »). Correctif : créer le client avec `http_options={"api_version": "v1beta", ...}` (les autres options inchangées), appliqué dans une copie locale du script ; le skill n'a pas été modifié. Le même script avait réussi pour le lot 2 le 2026-11-05 : le changement vient de l'API ou du SDK. Détail : `notes/voix-survol-pixel.md`.

## Voix off Fish Audio (connecteur) — mesures réelles

- Connecteur Fish Audio : plan **gratuit**, 10 000 crédits (1 crédit/octet UTF-8), 500 octets max par appel ; modèle `s2.1-pro` (défaut), `drama-3` (acteur, 85 crédits pour la même phrase avec balises). Un appel identique répété dans les 5 min est gratuit (observé : 2 lignes à 0 crédit). Les URL `platform.r2.fish.audio` sont téléchargeables depuis le conteneur.
- Voix testées (même phrase, 47 crédits chacune) : Clémence, Voix de documentaire, Le narrateur (Axel Frances), Féminine, Voix Mâle Dynamique, Arnold, Yuta, voix fr, Arnold `drama-3` ; **choix de l'utilisateur : Arnold**. Voix clonant des personnalités réelles volontairement non utilisées.
- 135 lignes × Arnold, 23 shorts ; remix `tts.py --engine files --replace` en 2 min 38 s au total. Débordements : 1 (voir `failures.md`). Niveaux (moyenne / pic) : atlas-grave fleuves −15,6 / −1,5 dB ; pixel-arcade bille −17,6 / −1,5 dB ; tableau-craie graine −16,2 / −1,5 dB. Durées identiques aux vidéos ; piste audio AAC présente ; `check.py --all` : 23/23 OK.
- Identités réhabilitées (2026-11-04) : 45 lignes × Arnold, 8 shorts, **1 711 crédits** consommés (somme des `credits_charged`, égale à l'estimation 1 crédit/octet) ; solde avant : 4 914 crédits. Téléchargement direct de `platform.r2.fish.audio` autorisé par le réseau ; durées des lignes 0,52–3,74 s. Remix `tts.py --engine files --replace` : 0 débordement. Niveaux (moyenne / pic) : brut-meme Stroop −16,1 / −1,5 dB ; brut-meme 15 s −16,7 / −1,5 ; cosmos-doc Voyager −16,7 / −1,5 ; cosmos-doc Vénus −16,7 / −1,6 ; riso-zine Géminides −15,7 / −1,4 ; riso-zine déserts −15,9 / −1,5 ; topo-relief Everest −16,6 / −1,4 ; topo-relief Hannibal −16,2 / **−0,0** (27 échantillons à 0 dB, voir `failures.md`). Durées audio = durées vidéo (15,0 / 15,5 / 16,0 s).
- Voix non écoutée par l'assistant, seulement mesurée.

