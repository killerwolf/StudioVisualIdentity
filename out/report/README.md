# Identités visuelles pour shorts 9:16 — rapport de campagne (lisible par agent)

> Les chemins de ce document sont relatifs au dossier `out/` (ex. `identities/swiss-data/` = `out/identities/swiss-data/`). Pour un agent qui veut **définir sa propre identité** à partir de ce travail : lire d'abord `AGENTS.md` (racine) et charger `out/identities/index.json`.

**But** : 14 identités visuelles (10 retenues en Phase 1, plus les 4 écartées puis réhabilitées à la demande) et cinématiques distinctes pour des chaînes de shorts verticaux (TikTok / Reels / Shorts), chacune **prouvée par 2 vidéos réelles** rendues par code avec des librairies open-source, puis documentée en design system exploitable par un agent de production.

**Bilan** : **14 identités** · **31 shorts** (1080×1920, 30 fps, H.264, 12–18,75 s, son généré) · QA automatique **31/31 OK** · 7 familles couvertes ≥ 3 fois · **8/8 librairies niveau A + 11/11 niveau B** · reconnaissance à l'aveugle **14/14 groupes purs, 56/56 images** (juge visuel indépendant) et **29/31** (mesure couleur, plus proche voisin) · premier tour 1 h 46 (2026-11-03 20:27 -> 22:13 UTC), 3ᵉ shorts 22:22 -> 22:37, identités réhabilitées 2026-11-04 00:24 -> 00:57, sur **4 cœurs** · voix off Fish Audio « Arnold » **31/31** (Gemini abandonné, voir « Voix off Fish Audio »).

Toutes les affirmations de ce dossier sont mesurées : temps (`facts.md`, `short.json.renderTimeSec`), QA (`qa.json`), reconnaissance (`recognition.json`).

## Index des identités

| id | Nom | Familles prouvées | Libs | Design system | Shorts de preuve |
|---|---|---|---|---|---|
| `swiss-data` | Grille Suisse | geographie, evenements | D3.js, GSAP | `identities/swiss-data/` | `shorts/swiss-data__geographie__ou-vivent-8-milliards`, `shorts/swiss-data__evenements__j-272-eclipse-2-aout-2027` |
| `gazette-1900` | Gazette 1900 | histoire, evenements | GSAP, OpenCV | `identities/gazette-1900/` | `shorts/gazette-1900__histoire__1789-en-20-secondes`, `shorts/gazette-1900__evenements__9-novembre-1989-mur-de-berlin` |
| `pixel-arcade` | Arcade Pixel | engagement ×2, abstrait | Matter.js, p5.js, PixiJS | `identities/pixel-arcade/` | `shorts/pixel-arcade__engagement__quelle-bille-gagne-la-course`, `shorts/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper`, `shorts/pixel-arcade__engagement__quelle-couleur-conquiert-l-ecran` (PixiJS) |
| `brut-meme` | Brut Mème *(réh.)* | engagement, evenements | PixiJS, GSAP | `identities/brut-meme/` | `shorts/brut-meme__engagement__test-des-3-secondes-stroop`, `shorts/brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde` |
| `bauhaus-kinetic` | Bauhaus Cinétique | explicatif, engagement | anime.js, flubber, Paper.js | `identities/bauhaus-kinetic/` | `shorts/bauhaus-kinetic__explicatif__abeilles-hexagones`, `shorts/bauhaus-kinetic__engagement__trouve-l-intrus` |
| `tableau-craie` | Tableau Craie | explicatif, enfants | Manim, Rough.js, GSAP | `identities/tableau-craie/` | `shorts/tableau-craie__explicatif__pourquoi-le-ciel-est-bleu`, `shorts/tableau-craie__enfants__comment-une-graine-devient-un-arbre` |
| `riso-zine` | Zine Riso *(réh.)* | geographie, evenements | p5.js, GSAP, OpenCV | `identities/riso-zine/` | `shorts/riso-zine__geographie__5-plus-grands-deserts`, `shorts/riso-zine__evenements__geminides-j-39` |
| `pastel-diorama` | Diorama Pastel | enfants, engagement | Zdog, A-Frame, GSAP | `identities/pastel-diorama/` | `shorts/pastel-diorama__enfants__d-ou-vient-la-pluie`, `shorts/pastel-diorama__engagement__choisis-ta-boite-renard` |
| `topo-relief` | Relief Topo *(réh.)* | geographie, histoire | three.js, D3.js | `identities/topo-relief/` | `shorts/topo-relief__geographie__comment-mesure-t-on-l-everest`, `shorts/topo-relief__histoire__hannibal-traverse-les-alpes` |
| `atlas-grave` | Atlas Gravé | geographie, histoire | D3.js, GSAP, pycairo | `identities/atlas-grave/` | `shorts/atlas-grave__geographie__plus-longs-fleuves-du-monde`, `shorts/atlas-grave__histoire__premier-tour-du-monde-1519-1522` |
| `aquarelle-conte` | Aquarelle Conte | enfants, histoire | p5.js, Paper.js | `identities/aquarelle-conte/` | `shorts/aquarelle-conte__enfants__ou-vont-les-etoiles-le-jour`, `shorts/aquarelle-conte__histoire__phare-d-alexandrie` |
| `neon-lab` | Labo Néon | abstrait, explicatif ×2 | three.js, twgl.js, OpenCV, Matplotlib | `identities/neon-lab/` | `shorts/neon-lab__abstrait__champ-de-force-lucioles` (boucle parfaite), `shorts/neon-lab__explicatif__lune-meme-face`, `shorts/neon-lab__explicatif__effet-papillon-double-pendule` (Matplotlib) |
| `cosmos-doc` | Cosmos Doc *(réh.)* | explicatif, evenements | three.js, GSAP | `identities/cosmos-doc/` | `shorts/cosmos-doc__explicatif__pourquoi-venus-plus-chaude-que-mercure`, `shorts/cosmos-doc__evenements__voyager-1-a-un-jour-lumiere` |
| `liquid-chrome` | Chrome Liquide | abstrait ×2, engagement | Taichi, three.js, OpenCV, Babylon.js | `identities/liquid-chrome/` | `shorts/liquid-chrome__abstrait__quatre-peintures-mpm`, `shorts/liquid-chrome__engagement__quelle-couleur-remplit-le-verre`, `shorts/liquid-chrome__abstrait__pendule-de-newton-chrome` (Babylon.js, boucle parfaite) |

L'ordre du tableau est le classement de durabilité/industrialisation (argumenté dans `comparison.md` §5). Index machine complet : `report/campaign.json` (31 shorts avec durée, temps de rendu, libs, mécanique d'engagement) et `report/matrix.json` (identité × famille × libs).

## Recommandation

Pour une chaîne durable : **1. swiss-data** (data / actu : le moins cher, 13,7–20,5 s/100 frames, < 1 Mo/short, épisode = jeu de données), **2. gazette-1900** (histoire / « ce jour-là » : identité la plus mémorable, calendrier infini), **3. pixel-arcade** (engagement : pari + photo-finish, variété infinie par graine pré-simulée). Trois publics, trois mécaniques, aucune confusion visuelle entre elles. Les 4 identités d'abord écartées (cosmos-doc, brut-meme, riso-zine, topo-relief) ont été produites ensuite : chacune est reconnue comme distincte de sa voisine (test mesuré) ; brut-meme se classe 4ᵉ.

## Comment réutiliser (pour un agent de production)

1. **Choisir l'identité** dans le tableau, lire `identities/<id>/identity.md` (16 sections normalisées : palette, typo, mouvement, caméra, transitions, structure type, zones sûres, voix off, risques) et `identities/<id>/tokens.json` (valeurs exactes utilisées).
2. **Choisir la recette** : `identities/<id>/recipes/<famille>.md` (« ouvrir par…, structurer en…, fermer par… », durées, chemin du short de référence).
3. **Copier le short de référence** : `shorts/<id>__<famille>__<sujet>/src/` contient tout le code + un `README.md` avec la commande de reproduction exacte. 10 identités ont un module commun identique dans leurs shorts — swiss-data `grille.js`, gazette-1900 `gazette.js` + `post.py`, bauhaus-kinetic `bk.js`, aquarelle-conte `aq.js`, atlas-grave `atlas.js` + `textures.py`, neon-lab `field.glsl.js` + `neon_grade.py`, brut-meme `brut.js`, cosmos-doc `cosmos.js`, riso-zine `riso.js` (ses deux `post.py` diffèrent légèrement), topo-relief `topo.js` : changer le contenu (données, textes, dates), pas le module. Les 4 autres changent de moteur d'un short à l'autre (pastel-diorama Zdog / A-Frame, liquid-chrome Taichi / three.js / Babylon.js, tableau-craie Manim / Rough.js, pixel-arcade Matter / physique maison / PixiJS) et ne partagent que les tokens : partir du short de la même famille.
4. **Rendre** avec le harnais `tools/` (voir ci-dessous) : stills -> planche-contact -> rendu complet -> `sound.py` -> `assemble.py mux` -> `check.py`.
5. **Voix off** : écrire `narration.json` (≈ 2,6 mots/s, lignes horodatées sans chevauchement, voix suggérée), puis `tts.py`.
6. **Choisir les librairies** avec `library-cards/<lib>.json` (rôle, bestFor/avoidFor, coût mesuré, pièges, snippets, compatibilités).

### Harnais (`out/tools/`, documenté en tête de chaque fichier)

| Fichier | Rôle |
|---|---|
| `render.mjs` | scène HTML (`window.ready`, `window.renderAt(t)`, `window.SEQUENTIAL`) -> mp4 1080×1920 ou stills ; slots CPU partagés |
| `lib/svi.js` | helpers de scène : PRNG, bruit, easings nommés, cubic-bezier, chargement @fontsource, zones sûres, contrat |
| `templates/aframe-template.html` | A-Frame déterministe qui marche en headless |
| `sound.py` | musique + SFX synthétisés (numpy/scipy), normalisés −18 dBFS RMS |
| `textpng.py` | overlays texte PNG (polices @fontsource woff2 via PIL) pour les pipelines Python |
| `assemble.py` | `mux` (son, voix + ducking, overlays, ré-encodage livrable crf 20 / 8 Mb/s), `concat` (xfade), `frames`, `sheet` |
| `check.py` | QA d'un short ou `--all` -> `report/qa.json` |
| `tts.py` | **voix off** (Fish Audio / lignes pré-générées / Gemini) depuis `narration.json`, calée sur les temps, musique duckée |
| `slot.sh` | réserve un slot CPU pour un rendu Python |
| `aggregate.py` | fusion des cartes librairie + index `campaign.json` / `matrix.json` |
| `recognition.py` | test de reconnaissance mesuré + paquet anonymisé pour juge aveugle |
| `STUDIO_BRIEF.md` | le brief exact donné aux 10 studios (règles, schémas) |

Mise en place (une fois, depuis la racine du dépôt) : `npm i` (libs + polices @fontsource listées dans `package.json`), `uv venv --python 3.11 .venv` + paquets Python (voir `facts.md` pour Manim sans manimpango). Playwright/Chromium préinstallés (ne pas réinstaller).

### Voix off Fish Audio (générée)

**État : voix off générée et mixée pour les 31 shorts sur 31** avec la voix Fish Audio « Arnold » (`d704cf8f1216490cbfbed89955f0e938`, modèle `s2.1-pro`, conteur masculin FR) via le connecteur Fish Audio (une ligne = un appel : 135 lignes pour les 23 premiers shorts, puis 45 lignes / 1 711 crédits pour les 8 shorts des identités réhabilitées). Chaque `short.mp4` est la version avec voix ; l'original muet+musique est gardé en `short_novo.mp4`. Rendu mesuré mais **pas écouté** par l'assistant (le choix de la voix a été fait par l'utilisateur sur échantillons).

```
.venv/bin/python out/tools/tts.py --all --engine files --voice "<titre voix>" --replace   # lignes déjà synthétisées dans <short>/voice_lines/NN.mp3
.venv/bin/python out/tools/tts.py --all --engine fish --voice <reference_id> --replace    # synthèse directe (FISH_API_KEY requis)
.venv/bin/python out/tools/tts.py --all --engine gemini --replace                          # moteur Gemini d'origine (GEMINI_API_KEY)
```

`tts.py` place chaque ligne à son temps `t`, accélère légèrement (≤ ×1,35) une ligne qui dépasse son `maxDuration`, puis remixe avec la musique duckée (sidechain) et met `short.json.sound.voice = true` (`voiceProvider`, `voiceName` renseignés). Moteurs : `files` (audio préparé via le connecteur), `fish` (API REST directe, non testée contre l'API réelle), `gemini` (historique : 3 shorts avaient été voisés ainsi avant le passage à Fish ; tous ont été refaits avec Arnold).

## Fichiers du rapport

| Fichier | Contenu |
|---|---|
| `README.md` | ce document |
| `comparison.md` | tableau comparatif, table des 31 shorts, matrice identité × famille × librairie, tests de reconnaissance, classement argumenté |
| `directions-contact-sheet.jpg` | les 14 directions explorées (Phase 1) ; posters et sources dans `posters/` |
| `directions.json` / `selection.json` | fiches des 14 directions ; sélection de 10, rejets justifiés, couverture |
| `facts.md` | faits techniques vérifiés, versions, nproc, coûts de rendu mesurés, pièges nouveaux |
| `decisions.md` | journal horodaté des choix faits sans validation humaine |
| `failures.md` | ce qui a échoué et pourquoi (rendus jetés, bugs, limites, défauts acceptés) |
| `qa.json`, `recognition.json`, `campaign.json`, `matrix.json` | données machine |
| `notes/<id>.md` | journaux horodatés de chaque studio |

## Ce qui n'a pas marché (résumé — détail dans `failures.md`)

- **Voix off** : générée pour les 31 shorts avec Fish Audio (voix « Arnold ») ; voir « Voix off Fish Audio » ci-dessus et `failures.md` (1 débordement résiduel, 1 pic à 0 dB après encodage AAC).
- **CPU sur-souscrit** : 10 studios sur 4 cœurs (load 16–22) ; tous les temps de rendu sont ×2–3 au-dessus d'une machine calme.
- **2 rendus complets jetés** (aquarelle-conte : bande non peinte ; liquid-chrome : verre réfractif à ~5 s/frame), 1 segment re-rendu (tableau-craie : bug de raster SwiftShader sous filtre SVG).
- **Déterminisme Node ≠ navigateur** pour Matter.js (`Math.atan2` au dernier bit) : corrigé par géométrie précalculée.
- **Manim sans texte** (pas de Pango ni LaTeX) : texte en overlays.
- **Niveau B complété après coup** : PixiJS, Babylon.js et Matplotlib n'avaient été attribués à aucun studio dans le premier tour (choix de l'orchestrateur, le minimum de 5 étant atteint) ; ils ont été ajoutés à la demande via un 3ᵉ short pour pixel-arcade, liquid-chrome et neon-lab.
- **Non explorés** : Blender et Remotion (niveau C, optionnels ; Blender Cycles ≈ 25–30 s/frame était incompatible avec 4 cœurs saturés) ; 3ᵉ short seulement pour 3 identités ; deux boucles parfaites seulement (neon-lab/abstrait, liquid-chrome/pendule).
- **Branches** : tout le travail est sur `main` (les branches de travail des sessions ont été fusionnées puis supprimées).
