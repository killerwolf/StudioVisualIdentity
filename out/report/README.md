# Identités visuelles pour shorts 9:16 — rapport de campagne (lisible par agent)

**But** : 10 identités visuelles et cinématiques distinctes pour des chaînes de shorts verticaux (TikTok / Reels / Shorts), chacune **prouvée par 2 vidéos réelles** rendues par code avec des librairies open-source, puis documentée en design system exploitable par un agent de production.

**Bilan** : 10 identités · 20 shorts (1080×1920, 30 fps, H.264, 12–18,75 s, son généré) · QA automatique **20/20 OK** · 7 familles couvertes ≥ 2 fois · 8/8 librairies niveau A + 8 niveau B utilisées · reconnaissance à l'aveugle **10/10 groupes purs** (juge visuel) et **18/20** (mesure couleur) · 1 h 46 de travail mural sur **4 cœurs** (20:27 -> 22:13 UTC, 2026-11-03) · voix off **non générée** (clé Gemini absente, pipeline prêt).

Toutes les affirmations de ce dossier sont mesurées : temps (`facts.md`, `short.json.renderTimeSec`), QA (`qa.json`), reconnaissance (`recognition.json`).

## Index des identités

| id | Nom | Familles prouvées | Libs | Design system | Shorts de preuve |
|---|---|---|---|---|---|
| `swiss-data` | Grille Suisse | geographie, evenements | D3.js, GSAP | `identities/swiss-data/` | `shorts/swiss-data__geographie__ou-vivent-8-milliards`, `shorts/swiss-data__evenements__j-272-eclipse-2-aout-2027` |
| `gazette-1900` | Gazette 1900 | histoire, evenements | GSAP, OpenCV | `identities/gazette-1900/` | `shorts/gazette-1900__histoire__1789-en-20-secondes`, `shorts/gazette-1900__evenements__9-novembre-1989-mur-de-berlin` |
| `pixel-arcade` | Arcade Pixel | engagement, abstrait | Matter.js, p5.js | `identities/pixel-arcade/` | `shorts/pixel-arcade__engagement__quelle-bille-gagne-la-course`, `shorts/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper` |
| `bauhaus-kinetic` | Bauhaus Cinétique | explicatif, engagement | anime.js, flubber, Paper.js | `identities/bauhaus-kinetic/` | `shorts/bauhaus-kinetic__explicatif__abeilles-hexagones`, `shorts/bauhaus-kinetic__engagement__trouve-l-intrus` |
| `tableau-craie` | Tableau Craie | explicatif, enfants | Manim, Rough.js, GSAP | `identities/tableau-craie/` | `shorts/tableau-craie__explicatif__pourquoi-le-ciel-est-bleu`, `shorts/tableau-craie__enfants__comment-une-graine-devient-un-arbre` |
| `pastel-diorama` | Diorama Pastel | enfants, engagement | Zdog, A-Frame, GSAP | `identities/pastel-diorama/` | `shorts/pastel-diorama__enfants__d-ou-vient-la-pluie`, `shorts/pastel-diorama__engagement__choisis-ta-boite-renard` |
| `atlas-grave` | Atlas Gravé | geographie, histoire | D3.js, GSAP, pycairo | `identities/atlas-grave/` | `shorts/atlas-grave__geographie__plus-longs-fleuves-du-monde`, `shorts/atlas-grave__histoire__premier-tour-du-monde-1519-1522` |
| `aquarelle-conte` | Aquarelle Conte | enfants, histoire | p5.js, Paper.js | `identities/aquarelle-conte/` | `shorts/aquarelle-conte__enfants__ou-vont-les-etoiles-le-jour`, `shorts/aquarelle-conte__histoire__phare-d-alexandrie` |
| `neon-lab` | Labo Néon | abstrait, explicatif | three.js, twgl.js, OpenCV | `identities/neon-lab/` | `shorts/neon-lab__abstrait__champ-de-force-lucioles` (boucle parfaite), `shorts/neon-lab__explicatif__lune-meme-face` |
| `liquid-chrome` | Chrome Liquide | abstrait, engagement | Taichi, three.js, OpenCV | `identities/liquid-chrome/` | `shorts/liquid-chrome__abstrait__quatre-peintures-mpm`, `shorts/liquid-chrome__engagement__quelle-couleur-remplit-le-verre` |

L'ordre du tableau est le classement de durabilité/industrialisation (argumenté dans `comparison.md` §5). Index machine complet : `report/campaign.json` (20 shorts avec durée, temps de rendu, libs, mécanique d'engagement) et `report/matrix.json` (identité × famille × libs).

## Recommandation

Pour une chaîne durable : **1. swiss-data** (data / actu : le moins cher, 13,7–20,5 s/100 frames, < 1 Mo/short, épisode = jeu de données), **2. gazette-1900** (histoire / « ce jour-là » : identité la plus mémorable, calendrier infini), **3. pixel-arcade** (engagement : pari + photo-finish, variété infinie par graine pré-simulée). Trois publics, trois mécaniques, aucune confusion visuelle entre elles.

## Comment réutiliser (pour un agent de production)

1. **Choisir l'identité** dans le tableau, lire `identities/<id>/identity.md` (16 sections normalisées : palette, typo, mouvement, caméra, transitions, structure type, zones sûres, voix off, risques) et `identities/<id>/tokens.json` (valeurs exactes utilisées).
2. **Choisir la recette** : `identities/<id>/recipes/<famille>.md` (« ouvrir par…, structurer en…, fermer par… », durées, chemin du short de référence).
3. **Copier le short de référence** : `shorts/<id>__<famille>__<sujet>/src/` contient tout le code + un `README.md` avec la commande de reproduction exacte. 6 identités ont un module commun identique dans leurs deux shorts — swiss-data `grille.js`, gazette-1900 `gazette.js` + `post.py`, bauhaus-kinetic `bk.js`, aquarelle-conte `aq.js`, atlas-grave `atlas.js` + `textures.py`, neon-lab `field.glsl.js` + `neon_grade.py` : changer le contenu (données, textes, dates), pas le module. Les 4 autres changent de moteur d'un short à l'autre (pastel-diorama Zdog / A-Frame, liquid-chrome Taichi / three.js, tableau-craie Manim / Rough.js, pixel-arcade Matter / physique maison) et ne partagent que les tokens : partir du short de la même famille.
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
| `tts.py` | **voix off Gemini TTS** depuis `narration.json`, calée sur les temps, musique duckée |
| `slot.sh` | réserve un slot CPU pour un rendu Python |
| `aggregate.py` | fusion des cartes librairie + index `campaign.json` / `matrix.json` |
| `recognition.py` | test de reconnaissance mesuré + paquet anonymisé pour juge aveugle |
| `STUDIO_BRIEF.md` | le brief exact donné aux 10 studios (règles, schémas) |

Mise en place (une fois, depuis la racine du dépôt) : `npm i` (libs + polices @fontsource listées dans `package.json`), `uv venv --python 3.11 .venv` + paquets Python (voir `facts.md` pour Manim sans manimpango). Playwright/Chromium préinstallés (ne pas réinstaller).

### Voix off Gemini (à lancer)

La clé `GEMINI_API_KEY` n'était pas disponible dans le conteneur pendant la campagne. Dès qu'elle l'est :

```
.venv/bin/python out/tools/tts.py --all --dry-run      # liste voix / lignes
.venv/bin/python out/tools/tts.py --all --replace      # génère voice.wav, remixe short.mp4 (original -> short_novo.mp4)
```

`tts.py` synthétise chaque ligne avec `gemini-3.8-flash-tts` (repli `gemini-3.8-flash-lite-tts`), voix préconstruite choisie par `narration.json.voice` ou le style, accélère légèrement (≤ ×1,35) une ligne qui dépasse son `maxDuration`, place chaque ligne à son temps `t`, puis remixe avec la musique duckée (sidechain) et met `short.json.sound.voice = true`. **Non testé contre l'API** (pas de clé) : vérifier le premier short à l'oreille.

## Fichiers du rapport

| Fichier | Contenu |
|---|---|
| `README.md` | ce document |
| `comparison.md` | tableau comparatif, table des 20 shorts, matrice identité × famille × librairie, tests de reconnaissance, classement argumenté |
| `directions-contact-sheet.jpg` | les 14 directions explorées (Phase 1) ; posters et sources dans `posters/` |
| `directions.json` / `selection.json` | fiches des 14 directions ; sélection de 10, rejets justifiés, couverture |
| `facts.md` | faits techniques vérifiés, versions, nproc, coûts de rendu mesurés, pièges nouveaux |
| `decisions.md` | journal horodaté des choix faits sans validation humaine |
| `failures.md` | ce qui a échoué et pourquoi (rendus jetés, bugs, limites, défauts acceptés) |
| `qa.json`, `recognition.json`, `campaign.json`, `matrix.json` | données machine |
| `notes/<id>.md` | journaux horodatés de chaque studio |

## Ce qui n'a pas marché (résumé — détail dans `failures.md`)

- **Voix off absente** des 20 shorts : clé Gemini indisponible ; seul le script horodaté (`narration.json`) est livré.
- **CPU sur-souscrit** : 10 studios sur 4 cœurs (load 16–22) ; tous les temps de rendu sont ×2–3 au-dessus d'une machine calme.
- **2 rendus complets jetés** (aquarelle-conte : bande non peinte ; liquid-chrome : verre réfractif à ~5 s/frame), 1 segment re-rendu (tableau-craie : bug de raster SwiftShader sous filtre SVG).
- **Déterminisme Node ≠ navigateur** pour Matter.js (`Math.atan2` au dernier bit) : corrigé par géométrie précalculée.
- **Manim sans texte** (pas de Pango ni LaTeX) : texte en overlays.
- **Non explorés** : PixiJS, Babylon.js, Matplotlib (niveau B) et Blender/Remotion (niveau C) ; pas de 3ᵉ short par identité ; une seule boucle parfaite (neon-lab/abstrait).
- **Pas de PR** : le dépôt distant n'a pas de branche de base ; tout est poussé sur `claude/new-session-ae9hjs`.
