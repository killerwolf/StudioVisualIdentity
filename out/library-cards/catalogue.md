# Catalogue des librairies et outils

**Base de travail pour créer de nouvelles identités de chaîne.** Ce catalogue recense toutes les librairies et tous les outils
envisageables pour rendre des shorts par code, et dit pour chacun s'il a déjà servi dans les 18 identités (39 shorts), où, et
sinon pourquoi. On itère à partir de cette liste : une nouvelle identité part d'abord des cases « Non » pour trouver une
signature que personne n'a encore, ou recombine des cases « Oui » déjà maîtrisées (fiches dans `out/library-cards/<lib>.json`).

Établi le 2026-11-04, mis à jour le 2026-11-05 en scannant le code source des 39 shorts (`out/shorts/*/src`), le moteur partagé
(`out/shared`, dont `out/shared/papier-moteur` des 4 identités papier), les outils (`out/tools`, dont le nouvel outil
`out/tools/catalogue_scan.py`), la démo (`out/demo`, `out/showcase`), les rapports (`out/report`) et les skills de
[killerwolf/skills](https://github.com/killerwolf/skills). Le rescan se fait avec `out/tools/catalogue_scan.py --check` (nouvel outil,
stdlib seule), qui confronte le code à la colonne « Déjà utilisée ? ».

## Légende

- **Statut** : disponibilité dans l'environnement de rendu de la campagne (conteneur Claude Code, 4 cœurs, pas de GPU).
  ✅ déjà installé · 📦 une installation (`npm i` / `pip`) · ⚠️ fonctionne, avec limites · 🔌 via un connecteur MCP · ❌ impossible ici.
  Sur une autre machine (le Mac du studio privé, un GPU), ⚠️ et 📦 peuvent changer.
- **Déjà utilisée ?** : **Oui** = importée par au moins un short livré ou un outil du pipeline ; Non = jamais importée.
- **Où** : identités, shorts (titre abrégé) ou fichiers concernés. Les coûts mesurés et les pièges sont dans la fiche de la librairie.

## Tableau

| Catégorie | Librairie | Statut | Déjà utilisée ? | Où, concrètement |
|---|---|---|---|---|
| 3D / WebGL | three.js | ✅ | **Oui** | neon-lab « lune même face », cosmos-doc (2 shorts), topo-relief (2 shorts), liquid-chrome « verre » |
| 3D / WebGL | A-Frame | 📦 | **Oui** | pastel-diorama « choisis ta boîte », gabarit `out/tools/templates/aframe-template.html` |
| 3D / WebGL | Babylon.js | 📦 | **Oui** | liquid-chrome « pendule de Newton chromé », GlowLayer |
| 3D / WebGL | PlayCanvas | 📦 | Non | |
| 3D / WebGL | React Three Fiber + drei | 📦 | Non | |
| 3D / WebGL | OGL | 📦 | Non | |
| 3D / WebGL | regl | 📦 | Non | seulement cité en comparaison dans la fiche twgl |
| 3D / WebGL | twgl | 📦 | **Oui** | neon-lab « champ de force lucioles », shaders GLSL maison |
| 3D / WebGL | Threlte | 📦 | Non | |
| 3D / WebGL | three EffectComposer (addons) | 📦 | **Oui** | EffectComposer, RenderPass, UnrealBloomPass, ShaderPass, OutputPass, BokehPass sur neon-lab, cosmos-doc, liquid-chrome |
| 3D / WebGL | postprocessing (paquet npm) | 📦 | Non | le bloom passe par les addons three, pas par ce paquet |
| 3D / WebGL | Theatre.js | 📦 | Non | |
| 3D / WebGL | cannon-es / Rapier / Ammo.js | 📦 | Non | la seule physique est 2D (Matter.js) ou fluide (Taichi) |
| 3D / WebGL | troika-three-text | 📦 | Non | textes posés en HTML ou canvas par-dessus la 3D |
| 3D / WebGL | LYGIA / glsl-noise | 📦 | Non | bruit maison dans `svi.js` et dans les shaders |
| 2D canvas | PixiJS | 📦 | **Oui** | pixel-arcade « quelle couleur conquiert l'écran », brut-meme (2 shorts) |
| 2D canvas | p5.js (v2) | 📦 | **Oui** | pixel-arcade (2 shorts), riso-zine (2), aquarelle-conte (2) |
| 2D canvas | Two.js | 📦 | Non | |
| 2D canvas | Paper.js | 📦 | **Oui** | bauhaus-kinetic (2 shorts), aquarelle-conte (2) |
| 2D canvas | Konva / Fabric.js | 📦 | Non | |
| 2D canvas | Zdog | 📦 | **Oui** | pastel-diorama « d'où vient la pluie » |
| 2D canvas | Rough.js | 📦 | **Oui** | tableau-craie « comment une graine devient un arbre » |
| 2D canvas | Matter.js | 📦 | **Oui** | pixel-arcade « quelle bille gagne la course », pré-simulé en Node |
| 2D canvas | canvas-sketch | 📦 | Non | |
| 2D canvas | Canvas2D brut | ✅ | **Oui** | topo-relief, aquarelle-conte, tableau-craie, gazette-1900, overlays de la démo |
| 2D canvas | GLSL fragment shaders | ✅ | **Oui** | neon-lab via twgl, cosmos-doc et topo-relief via ShaderMaterial |
| 2D canvas | Node.js, pré-simulation | ✅ | **Oui** | pixel-arcade : la course Matter.js est simulée en Node puis rejouée dans Chromium, à cause de l'écart `Math.atan2` |
| Animation | GSAP (cœur) | 📦 | **Oui** | la plus utilisée : 8 identités, 16 shorts (swiss-data, gazette-1900, brut-meme, tableau-craie, riso-zine, pastel-diorama, atlas-grave, cosmos-doc) |
| Animation | GSAP SplitText / MorphSVG / DrawSVG / MotionPath | 📦 | Non | seul `gsap.min.js` est chargé, aucun plugin |
| Animation | anime.js (v4) | 📦 | **Oui** | bauhaus-kinetic (2 shorts) |
| Animation | Motion / Framer Motion | 📦 | Non | |
| Animation | Popmotion / Tween.js | 📦 | Non | |
| Animation | mo.js | 📦 | Non | |
| Animation | Web Animations API / CSS keyframes | ✅ | Non | aucun `@keyframes` : tout est piloté image par image par `window.renderAt(t)` et les easings de `svi.js` |
| SVG / data / typo | D3.js | 📦 | **Oui** | swiss-data (2 shorts), atlas-grave (2), topo-relief (2), surtout d3-geo |
| SVG / data / typo | topojson-client | 📦 | Non | installé dans `package.json` mais jamais importé dans un short |
| SVG / data / typo | flubber | 📦 | **Oui** | bauhaus-kinetic (2 shorts), morphing de formes |
| SVG / data / typo | KUTE.js | 📦 | Non | |
| SVG / data / typo | Vivus | 📦 | Non | |
| SVG / data / typo | SVG.js / Snap.svg | 📦 | Non | |
| SVG / data / typo | opentype.js | 📦 | Non | |
| SVG / data / typo | Splitting.js | 📦 | Non | |
| SVG / data / typo | @fontsource | 📦 | **Oui** | 23 polices en npm, injectées par `S.loadFonts` de `svi.js` dans toutes les scènes HTML ; 21 sont référencées, Fredoka et Major Mono Display sont installées mais jamais référencées |
| SVG / data / typo | Polices embarquées (.ttf/.woff2 hors @fontsource) | ✅ | **Oui** | identités papier (papier-decoupe, atelier-papier, carnet-archives, cabinet-curiosites) via `out/shared/papier-moteur` : Abril Fatface, Courier Prime, Dela Gothic One, DM Mono, Kalam, Special Elite (et DM Serif Display, en doublon avec @fontsource) dans `out/shared/papier-moteur/assets/fonts`, chargées par `ImageFont.truetype` de `papier.py` selon `themes/*.json`. Hors embarqué : la vitrine `out/showcase/page.tpl.html` charge Bricolage Grotesque (avec Hanken Grotesk et JetBrains Mono) depuis Google Fonts, par le réseau, sans fichier dans le dépôt |
| SVG / data / typo | fontTools | ✅ | **Oui** | conversion woff → ttf pour que Matplotlib lise les polices @fontsource, neon-lab « effet papillon » |
| SVG / data / typo | Mermaid CLI | ✅ | Non | |
| SVG / data / typo | rsvg-convert | ✅ | Non dans les identités ; **Oui** dans killerwolf/skills, devto-post | aucune identité ni outil du dépôt ne l'appelle ; seul `skills/devto-post/scripts/make-cover.py` (couverture d'article) l'utilise |
| SVG / data / typo | ImageMagick | ✅ | Non | |
| Vidéo code → MP4 | Remotion | 📦 | Non | niveau C, non tenté faute de CPU, noté dans `out/report/README.md` |
| Vidéo code → MP4 | Motion Canvas / Revideo | 📦 | Non | |
| Vidéo code → MP4 | Editly / FFCreator / etro.js | 📦 | Non | |
| Lottie / Rive | lottie-web, dotLottie, python-lottie | 📦 | Non | |
| Lottie / Rive | Rive runtime | ⚠️ | Non | demande un `.riv` fait dans l'éditeur Rive |
| Python | Manim | 📦 | **Oui** | tableau-craie « pourquoi le ciel est bleu », sans Pango ni LaTeX, textes en overlays PIL |
| Python | MoviePy | 📦 | Non | |
| Python | Matplotlib (Agg) | ✅ | **Oui** | neon-lab « effet papillon » : `buffer_rgba` → ffmpeg rawvideo |
| Python | matplotlib.animation | ✅ | Non | pas de FuncAnimation, rendu image par image à la main |
| Python | Pillow | ✅ | **Oui** | `textpng.py`, overlays tableau-craie, liquid-chrome, neon-lab ; identités papier (papier-decoupe, atelier-papier, carnet-archives, cabinet-curiosites) via `out/shared/papier-moteur` : tout le rendu image par image (`papier.py`, `elements.py`, `episode.py`) |
| Python | pycairo | ✅ | **Oui** | atlas-grave : textures gravure et papier précalculées en PNG |
| Python | skia-python | 📦 | Non | |
| Python | OpenCV | ✅ | **Oui** | passes de post-prod : grain gazette-1900, bloom neon-lab (3 shorts), trames riso-zine (2), fluide liquid-chrome, plus le test de reconnaissance aveugle ; identités papier (papier-decoupe, atelier-papier, carnet-archives, cabinet-curiosites) via `out/shared/papier-moteur` : texture et bords du papier (`papier.py`) |
| Python | Blender (bpy) | ⚠️ | Non | non tenté : Cycles ≈ 25 à 30 s par image sur CPU |
| Python | Taichi | 📦 | **Oui** | liquid-chrome « quatre peintures », fluide MPM 24 k particules |
| Python | PyVista / VTK, pyrender, ModernGL, VisPy | ⚠️ | Non | rendu hors écran à configurer |
| Python | Plotly + Kaleido | 📦 | Non | |
| Python | trimesh / shapely / opensimplex | 📦 | Non | |
| Audio | numpy / scipy synthèse | ✅ | **Oui** | `sound.py` : musique et bruitages des 31 shorts ; `tts.py` : mixage avec ducking ; identités papier (papier-decoupe, atelier-papier, carnet-archives, cabinet-curiosites) via `out/shared/papier-moteur` : calcul des images et mixage voix + musique + bruitages fournis en fichiers (`son.py`, `assets/audio`), sans scipy |
| Audio | Tone.js | 📦 | Non | |
| Audio | librosa | 📦 | Non | |
| Audio | pydub | 📦 | Non | |
| Audio | ElevenLabs | 🔌 | Non | voix off = Fish Audio ; ElevenLabs n'apparaît que dans studio-mate, pour le studio privé |
| Audio | Fish Audio, connecteur MCP | 🔌 | **Oui** | voix « Arnold », modèle s2.1-pro : les 31 voix off et la démo, une ligne par appel, mixées par `tts.py --engine files` (les 8 shorts papier n'utilisent pas Fish Audio) |
| Audio | Gemini TTS, google-genai | 📦 | **Oui** | skill gemini-voices, voix alternatives de la démo, et 3 shorts au début avant l'abandon pour quota gratuit ; les 8 shorts des identités papier déclarent la voix Gemini « Sulafat » (gemini-3.8-flash-tts) dans `narration.json` : voix réellement mixée, les `voice_lines/*.mp3` sont présents et intégrés à `short.mp4` par `son.py` du moteur papier (pas de `voice_report.json`, pas de `tts.py`), mêmes fichiers pour les 4 identités, réutilisés depuis le studio Un Jour Une Histoire et non régénérés dans le dépôt |
| Audio | Freesound API | ⚠️ | **Oui** | `out/tools/freesound.py` et skill sound-design ; demande `FREESOUND_API_KEY` |
| Audio | OpenGameArt, sons CC0 | ✅ | **Oui** | bruitages de la démo et bibliothèque livrée avec le skill sound-design |
| Encodage | ffmpeg | ✅ | **Oui** | partout : `render.mjs`, `assemble.py`, démo, GIF d'aperçu par palettegen, skill sound-design ; identités papier (papier-decoupe, atelier-papier, carnet-archives, cabinet-curiosites) via `out/shared/papier-moteur` : pipe rawvideo par tranches, concat, loudnorm et silencedetect (`episode.py`, `son.py`) |
| Encodage | ffprobe | ✅ | **Oui** | mesures de durée, niveaux et débit dans `check.py` et `assemble.py` ; identités papier (papier-decoupe, atelier-papier, carnet-archives, cabinet-curiosites) via `out/shared/papier-moteur` : durée des répliques (`episode.py`) |
| Encodage | Playwright + Chromium | ✅ | **Oui** | `render.mjs` capture chaque image ; c'est le poste de coût principal, ≈ 0,3 s par image |
| Encodage | WebCodecs | ✅ | Non | |
| Encodage | gifski | 📦 | Non | le GIF est fait avec ffmpeg |
| Services | Adobe Express | 🔌 | Non | |
| Services | Canva | 🔌 | Non | |
| Services | Notion, connecteur MCP | 🔌 | **Oui** | skill studio-mate : pilotage des studios, idées à valider, retours de relecture ; pas de rendu |

**Bilan** : 36 lignes « Oui » sur 83 (recompté le 2026-11-05 ; l'ancien total « 85 » comptait 3 lignes de trop, le tableau en avait 82,
plus la ligne des polices embarquées ajoutée), dont 20 librairies de scène. Les identités papier n'ajoutent aucune librairie de
scène : elles recombinent Pillow, OpenCV, numpy et ffmpeg. Des modules maison complètent le tout et ne sont pas des
librairies : `out/tools/lib/svi.js` (helpers partagés des scènes : format, zones sûres, PRNG, bruit, easings, chargement des
polices, contrat `renderAt`), `out/tools/textpng.py` (overlays de texte en PNG) et le moteur `out/shared/papier-moteur/pipeline`
(`chaine.py`, `papier.py`, `elements.py`, `episode.py`, `son.py` : rendu Python image par image sans navigateur, des 4 identités papier).

## Comment s'en servir pour une nouvelle identité

1. **Chercher la signature dans les « Non »** : une librairie jamais utilisée donne plus facilement un rendu que les 18 identités
   n'ont pas (voir `curation.confusableWith` dans `out/identities/index.json`). Vérifier d'abord son statut et son coût de rendu
   sur CPU ; une ligne ⚠️ ou un moteur 3D lourd peut coûter plus que les ≈ 60 s / 100 images de three.js avec bloom.
2. **Recombiner des « Oui »** quand le budget est serré : les fiches `out/library-cards/<lib>.json` donnent les pièges déjà payés
   et les coûts mesurés, et `out/report/facts.md` les correctifs.
3. **Garder le pipeline** : scène HTML ou script Python qui expose un rendu image par image, capture Playwright ou pipe rawvideo,
   son numpy/scipy, voix Fish Audio, `check.py` en fin de course. Une librairie qui ne sait pas rendre une image à un temps `t`
   donné (animation temps réel non pilotable) ne rentre pas dans ce pipeline sans adaptation.

## Maintenance

- Quand une nouvelle identité ou un nouveau short utilise une librairie, passer sa ligne à **Oui**, compléter « Où » et ajouter
  ou enrichir sa fiche dans `out/library-cards/`.
- Quand une librairie est essayée puis abandonnée, laisser « Non » et noter la raison dans « Où », comme pour Remotion et Blender.
- Les statuts de la légende décrivent l'environnement de la campagne ; les mettre à jour si le pipeline change de machine.
- Rescan après chaque nouvelle identité ou nouveau short : `python3 -I out/tools/catalogue_scan.py --check --skills /home/user/skills`
  (depuis la racine du dépôt). Il liste les « Non » utilisées, les « Oui » sans fichier, les librairies et polices absentes du tableau ;
  il ne modifie rien. Les connecteurs MCP (Notion) et les sons CC0 restent « Oui sans fichier » : usage par consignes ou par fichiers audio.
- Ne jamais retirer une ligne « Non » : elle reste la réserve de signatures pour les prochaines identités.
