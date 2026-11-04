# Ce qui a échoué, et pourquoi

Sources : journaux horodatés des studios (`out/report/notes/<slug>.md`), rapports de fin de studio, journal orchestrateur (`decisions.md`). Aucune librairie n'a dû être remplacée (aucun blocage > 20 min). PixiJS, Babylon.js et Matplotlib n'étaient attribués à aucun studio au premier tour (choix d'orchestration : le minimum de 5 libs B était atteint) ; ajoutés ensuite par un 3ᵉ short chacune, sans blocage. Tous les temps sont mesurés.

## Échecs d'environnement (orchestrateur)

| Quoi | Cause | Coût | Contournement |
|---|---|---|---|
| **Voix off : 1 débordement résiduel** | Fish Audio (Arnold) : la ligne « Premier : le Nil. » (atlas-grave plus-longs-fleuves, t = 8,3 s) dure 0,94 s pour un `maxDuration` de 0,8 s, même à ×1,35 | débordement de 0,14 s sur 180 lignes (aucun nouveau débordement sur les 45 lignes des identités réhabilitées) ; texte non réécrit | rallonger `maxDuration` de cette ligne ou la reformuler, puis relancer `tts.py --engine files` sur ce short |
| **Voix off Gemini abandonnée** | le plan gratuit Gemini (~10 requêtes/jour/modèle) n'a permis que 3 shorts et mélangeait les modèles ; remplacé par Fish Audio (tous les shorts refaits avec une seule voix) | historique conservé dans `facts.md` | aucune |
| `manimpango` ne compile pas | pangocairo absent | ~5 min | `--no-deps` + stub (voir `facts.md`) ; **pas de `Text()` ni `MathTex`** (pas de LaTeX) : texte en overlays PIL |
| Commande shell bloquée 5 min | heredoc aplati au milieu d'une commande chaînée -> attente d'`EOF` sur stdin | 5 min | fichiers écrits via l'outil d'écriture |
| Pas de PR ouverte (résolu) | le dépôt distant ne contenait qu'une branche de travail, sans branche de base | — | résolu : `main` créée, tout y est fusionné (`main`) |
| **Sur-souscription CPU** | les slots ne bornent que les rendus `render.mjs`/`slot.sh` ; les ré-encodages ffmpeg, Node pré-simulations, compositions numpy des 10 studios tournaient hors slot -> **load average 16–22 sur 4 cœurs** | temps de rendu × 2–3 par rapport à une machine calme | les `renderTimeSec` sont donc des mesures sous contention (voir `facts.md`) |
| Workflow plafonné à 2 agents concurrents | moteur de workflow : min(16, CPU − 2) | — | 10 studios lancés comme sous-agents indépendants |

## Rendus abandonnés ou refaits (studios)

| Identité / short | Ce qui a raté | Pourquoi | Résolution | Coût |
|---|---|---|---|---|
| aquarelle-conte / enfants | **1er rendu complet jeté** : bande non peinte de 15–20 px à droite en fin de travelling | calque de parallaxe trop étroit pour l'amplitude du travelling | calques élargis à 1240 px, rendu refait | 507 s perdues |
| liquid-chrome / engagement | **1er rendu complet tué** à 60 frames | verre en transmission (refraction) three.js = ~5 s/frame sous SwiftShader saturé (≈ 37 min estimées) | verre « reflets seuls » (MeshPhysicalMaterial noir additif) | ~5 min |
| liquid-chrome / abstrait | 1er test Taichi : la peinture se comporte comme de l'eau (éclabousse jusqu'en haut, surface martelée), 206 s/100 frames | pas de viscosité, 32 k particules | viscosité μ 0,05, 24 k particules, 80 substeps, shading demi-résolution limité à la bbox | itérations courtes |
| tableau-craie / enfants | tracé fantôme intermittent (13,8–15,5 s), absent du DOM | **bug de raster Chromium/SwiftShader** sous filtre SVG plein cadre, déclenché par des éléments à opacité 0 + rotation 200° | `display:none` après effacement, plus de rotation ; seul le segment 13,5–15,5 s re-rendu (63,4 s) et raccordé | 63 s |
| tableau-craie / explicatif | `assemble.py --overlay` avec 18 PNG plein cadre > 8 min sous contention | un flux `-loop 1` décodé par overlay + filtre `fade` alpha par overlay | compositeur numpy maison (`src/composite.py`) ≈ 40 s | ~10 min |
| pixel-arcade / engagement | **la course Chromium divergeait de la trace Node** à la frame 102 (vainqueur pouvant changer) | `Math.atan2` diffère au dernier bit entre V8/Node 22 et Chromium (0.17467219900823971 vs 0.1746721990082397) -> chaos | angles/longueurs des rampes précalculés en dur dans Node | ~10 min |
| pixel-arcade / engagement | billes collées aux rampes | Matter 0.20 colle les corps aux pentes < ~0,25 rad dès que friction > 0 (même friction statique 0) | friction 0, vitesse réglée par `frictionAir` 0,014 | — |
| pixel-arcade / engagement | nudge anti-blocage empirait les blocages | poussée vers le centre -> remontée des rampes | poussée dans le sens de la rampe | — |

## Défauts acceptés (livrés en connaissance de cause)

- **gazette-1900** : le grain de film sature le plafond 8 Mb/s -> le short 1789 pèse 19,8 Mo (le plus lourd). Correctif possible : grain plus léger, en ne relançant que la passe OpenCV (~2,5 min).
- **tableau-craie / explicatif** : le grain de craie est fixé à l'écran, pas au dessin : pendant le zoom molécule on devine le rebord du tableau à travers le grain.
- **liquid-chrome / abstrait** : petites bulles d'air et bord supérieur un peu granuleux dans le fluide MPM (lus comme des bulles de peinture).
- **atlas-grave** : côtes simplifiées à la main -> grossières au-delà de ×2,5 de zoom.
- **swiss-data / événements** : tracé de la bande de totalité simplifié à 10 points approximatifs (noté comme schématique dans les fichiers).
- **Contrastes limites** : blanc sur rouge bauhaus 4,2:1, corail aquarelle 4,3:1, bleu aquarelle 3,7:1 -> réservés aux grands textes (≥ 54 px gras / ≥ 92 px) ; libellés gris pâles swiss-data volontairement sous AA pendant l'apparition puis passent au noir.
- **Petits textes décoratifs** : quelques légendes de bauhaus-kinetic (« polygones réguliers pavent sans trou ») sont proches de 54 px ; les HUD des posters Phase 1 (30–34 px) n'ont pas été repris dans les shorts.
- **Peu de boucles parfaites** (deux : neon-lab/abstrait et liquid-chrome/pendule-de-newton) : la balle qui grossit (pixel-arcade) et les récits ont une fin, pas une boucle.

## Limites de librairies constatées

- **Manim sans Pango ni LaTeX** : seulement des formes ; plusieurs pièges (`play(run_time=)` écrase les durées, `.animate` à préparer, `insert_n_curves` plante sur groupe vide, pas d'`add_to_back`, horloge caméra à piloter par `renderer.time`).
- **Capture Playwright = l'essentiel du coût** : ~0,3 s/frame de screenshot quand le JS de scène ne coûte que 6–8 ms (bauhaus-kinetic, mesuré).
- **SVG plein cadre filtré** (feTurbulence, feImage) très cher sous SwiftShader : 309 s/100 frames pour tableau-craie/enfants ; atlas-grave a remplacé ses filtres par des PNG pycairo précalculés.
- **GSAP `immediateRender:false`** : l'état de départ n'est pas appliqué avant le début du tween -> poser les états initiaux en dur (swiss-data).
- **anime.js v4 / p5 v2** : API différentes des versions documentées partout (pas de `anime()` global, pas de `preload()`).
- **Dépôt `"type":"module"`** : les scripts Node `require()` (pré-simulation Matter) ont besoin d'un `package.json` `commonjs` local dans `src/`.

## 3ᵉ shorts (PixiJS, Babylon.js, Matplotlib) — 22:22 → 22:37

| Short | Problème | Cause | Résolution |
|---|---|---|---|
| neon-lab / effet papillon (Matplotlib) | les polices @fontsource `.woff2` ne se chargent pas (`FT_Open_Face` 0x55) | FreeType de Matplotlib sans brotli | `.woff` -> `.ttf` via fontTools (déjà installé) puis `fontManager.addfont` ; sous-ensemble grec de JetBrains Mono renommé pour servir de repli à Δ, θ |
| liquid-chrome / pendule (Babylon.js) | plantage au 1er still | le sélecteur de couleur de GlowLayer matchait tous les meshes dont le nom commence par « b » (socle, barres) | billes renommées `ball<i>` |
| liquid-chrome / pendule | bande grise dure à l'horizon | sol brillant infini | sol retiré, fond en calque 2D |
| pixel-arcade / territoire (PixiJS) | écran rempli trop lentement (10 s), batailles plates à ~25 % chacune | réglages de l'automate | 2 sous-pas synchrones par frame et force d'attaque au carré, avant tout rendu |

Un seul rendu complet par short, aucun rejeté. Voix off : Fish Audio (Arnold) sur les 31 shorts, voir la ligne « Voix off : 1 débordement résiduel ». Pic : `topo-relief__histoire__hannibal-traverse-les-alpes` atteint −0,0 dB (27 échantillons à 0 dB vers 3,6 s) alors que la musique seule et la voix seule plafonnent à −1,0 dB : somme des deux sous le limiteur (−0,45 dBFS) puis dépassement à l'encodage AAC ; accepté (non écouté), correctif possible : `alimiter` à 0,89 dans `assemble.py mux`.

## Identités réhabilitées (cosmos-doc, brut-meme, riso-zine, topo-relief) — 2026-11-04 00:24 → 00:57

| Short | Problème | Cause | Résolution |
|---|---|---|---|
| riso-zine / déserts | **1er rendu complet jeté** : les dunes du Sahara disparaissent après la 1ʳᵉ image de leur page | bug p5 v2 : cache de style désynchronisé après un save/restore manuel autour d'un clip ; invisible sur stills isolés | resynchronisation du style après chaque restore, appliquée aux 2 shorts, 1 re-rendu |
| riso-zine / Géminides | jaune imprimé sur bleu = vert ; pluie de météores qui s'arrête à ~6 s ; trop dense (« feu d'artifice ») | surimpression multiply ; horloge non bouclée | défonce du bleu/rose sous le jaune, horloge bouclée, densité réduite (stills) |
| topo-relief / Hannibal | 8 séries de stills pour le cadrage | crête des Alpes + départ d'itinéraire impossibles à tenir ensemble en vertical ; signe de l'offset de visée inversé | itinéraire raccourci, caméra reculée, offset de visée par keyframe |
| topo-relief / Hannibal | compteur d'altitude plat (450 m) de 4,4 à 7,3 s alors que le texte dit « l'armée grimpe » | le compteur affiche l'altitude max atteinte et l'itinéraire suit une vallée | accepté ; la montée est portée par la caméra et la voix off |
| cosmos-doc / Voyager | compteur d'heures figé à 00 sur les stills ; flare mal placé | texte écrit avant le seek GSAP ; projection avec la caméra de l'image précédente | écriture après le seek ; `updateMatrixWorld()` avant projection |
| brut-meme / Stroop | « TON SCORE EN COMMENTAIRE » débordait de 1080 px | titre auto-ajusté mesuré pendant qu'il passait à la ligne | `white-space: nowrap` pendant la mesure |
| riso-zine (les 2) | 17 Mo par short | grain + trames saturent le plafond 8 Mb/s | accepté, comme gazette-1900 |

Aucune librairie bloquée ni remplacée. Les commits de l'orchestrateur ont parfois embarqué des fichiers de studios encore en cours d'écriture (les studios ne committent pas) ; sans conséquence, chaque livraison finale a été recommittée.
