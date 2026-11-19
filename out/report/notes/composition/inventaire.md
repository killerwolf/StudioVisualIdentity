# Inventaire : chaque identité découpée en habillage, mécanique et format (2026-11-19)

Relevé en lecture seule par un sous-agent (Sonnet), relu et corrigé par l'orchestrateur de la conception (Opus) ; deux
notes FACILE vérifiées dans le code (`swiss-data` : 1 à 2 hex hors de l'objet `T` de `grille.js` ; `brut-meme` : 0 à 3).
Modèle et vocabulaire : [`proposition.md`](proposition.md).

**Périmètre : 23 identités** = les 22 entrées de `out/identities/index.json` (19 racines + 3 dérivations de
`papier-decoupe`) + `survol-pixel` (PR #4, fusionnée dans `main` en `ee30e24`, pas encore dans `identite-lyrics` ; lue sur
la branche `identite-console-retro`). **50 shorts** : 48 dans `out/shorts/` ici, plus 2 de `survol-pixel`.

## 0. Trois architectures de code

- **A. Moteur partagé avec interface de matière** : `chemin-moteur` (contrat `habillage`, 4 fichiers `habillages/*.js`)
  et `papier-moteur` (thèmes JSON). Ce sont les seuls habillages **exécutables** aujourd'hui, avec les 3 camaïeux de
  `lyrics-moteur` (sélectionnés par section, mais écrits dans le moteur).
- **B. Module propre à l'identité, copié dans chaque short** : `aq.js`, `bk.js`, `brut.js`, `gazette.js`, `grille.js`,
  `meteo.js`, `cosmos.js`, `topo.js`, `riso.js`, `atlas.js`, `traceur.py`, `survol.py`. Une constante de couleurs en
  tête, des littéraux ailleurs. Copies identiques aujourd'hui (vérifié par `diff`), sans source unique.
- **C. Pas de moteur commun, chaque short réimplémente** : `neon-lab`, `liquid-chrome`, `pastel-diorama`, `pixel-arcade`
  (seules les simulations sont des modules), `tableau-craie` (Rough.js d'un côté, Manim de l'autre).

Les `tokens.json` ne sont lus par aucun code, sauf `tableau-craie__explicatif__pourquoi-le-ciel-est-bleu/src/scene.py:15-16`.

Critère de séparation : **FACILE** = la matière passe par une interface ou un objet de constantes, le mouvement ne la
référence pas ; **MOYEN** = objet de constantes mais littéraux ailleurs, ou matière dessinée dans la même fonction que le
mouvement ; **DIFFICILE** = pas de code commun, ou la mécanique est la matière.

## 1. Tableau

| Identité (= recette) | Habillage(s) | Mécanique | Moteur | Shorts (formats) | Séparation |
|---|---|---|---|---|---|
| lyrics-chemin | `plan-bleu`, `editeur`, `ardoise`, `portulan` | `trace-chemin` | `out/shared/chemin-moteur/` (A) | 4 : 2 paroles-muet 32,6 s, 1 narré 25,6 s, 1 narré 45 s | FACILE, déjà séparé (réserve : habillage lié au dessin) |
| papier-decoupe | `papier-decoupe` (tapis vert) | `pop-papier-12ips` | `out/shared/papier-moteur/` (A) | 2 narrés 12,3 et 19,7 s | FACILE, déjà séparé |
| atelier-papier | `atelier-papier` (tapis bleu nuit) | `pop-papier-12ips` | idem, `themes/atelier-papier.json` | 2 (mêmes épisodes) | FACILE, déjà séparé |
| carnet-archives | `carnet-archives` (kraft, sépia) | `pop-papier-12ips` | idem | 2 | FACILE, déjà séparé |
| cabinet-curiosites | `cabinet-curiosites` (bleu nuit, or) | `pop-papier-12ips` | idem | 2 | FACILE, déjà séparé |
| swiss-data | `grille-suisse` | `chiffre-volet-compteur` | `src/grille.js` (B, ×2) | 2 narrés 15 s | FACILE |
| brut-meme | `brut-jaune` | `punch-cut-slam` | `src/brut.js` (B, ×2) | 2 narrés 15,5 et 16 s | FACILE |
| lyrics-punchy | `punchy` (camaïeux nuit, lagon, braise) | `colonne-mot-a-mot` | `out/shared/lyrics-moteur/` | 1 paroles-muet 19,5 s | MOYEN |
| gazette-1900 | `gazette-sepia` | `tourniquet-tampon` | `src/gazette.js` + `post.py` (B) | 2 narrés 15 et 18,75 s | MOYEN |
| bauhaus-kinetic | `bauhaus-primaires` | `puzzle-grille-morph` | `src/bk.js` (B) | 2 narrés 14 et 16 s | MOYEN |
| aquarelle-conte | `aquarelle` | `lavis-multiplan` | `src/aq.js` (B) | 2 narrés 15 et 16 s | MOYEN |
| atlas-grave | `gravure-parchemin` | `carte-trace-panoramique` | `src/atlas.js` + `textures.py` (B) | 2 narrés 15 et 16 s | MOYEN |
| carte-meteo | `meteo-clair` | `carte-champs-front` | `src/meteo.js` (B) | 2 narrés 15 et 16 s | MOYEN |
| cosmos-doc | `cosmos-noir` | `travelling-cine-3d` | `src/cosmos.js` (B) | 2 narrés 15 s | MOYEN |
| topo-relief | `relief-vert` | `survol-terrain` | `src/topo.js` (B) | 2 narrés 15 s | MOYEN |
| survol-pixel | `pixel-jour` (biomes tropical, montagne) | `survol-terrain` | `src/survol.py` (B) | 2 narrés 18,6 et 18,8 s | MOYEN |
| riso-zine | `riso-3-encres` | `impression-on-twos` | `src/riso.js` + `post.py` (B) | 2 narrés 16 s | MOYEN |
| tableau-craie | `craie-verte` | `ecriture-trace-chiffon` | aucun commun (C) | 2 narrés 15,5 et 16,5 s | MOYEN |
| pixel-arcade | `arcade-marine` | `simulation-deterministe` | simulations `ring.js`, `course.js`, `conquest.js` (C) | 3 narrés 15–16 s | MOYEN |
| trait-continu | `orange-graphite` | `traceur-escalier-plaque` | `src/traceur.py` (B) | 2 narrés 15,5 et 16 s | DIFFICILE |
| pastel-diorama | `diorama-pastel` | `maquette-rebond` | aucun commun (C, Zdog / A-Frame) | 2 narrés 16 et 15 s | DIFFICILE |
| neon-lab | `neon-labo` | `orbite-phenomene-neon` | aucun commun (C) | 3 : 1 boucle 12 s, 2 narrés | DIFFICILE |
| liquid-chrome | `chrome-irise` | `plan-sequence-matiere` | aucun commun (C, 3 moteurs) | 3 : 1 boucle 12 s, 2 narrés | DIFFICILE |

Les ids d'habillage hors `chemin-moteur` et `papier-moteur` sont proposés ici ; les ids de mécanique viennent du relevé.

## 2. Chiffres

- **Séparation, sur 23 identités : 7 FACILE, 12 MOYEN, 4 DIFFICILE.**
  - Sur les 7 FACILE, **5 sont déjà séparées dans le code** (`lyrics-chemin` et ses 4 habillages, les 4 recettes papier) ;
    **2 se séparent en extrayant un objet de constantes** (`swiss-data` : `T` de `grille.js:6-14` ; `brut-meme` : `C`/`X`
    de `brut.js:15-16`, palette écrite 3 fois dans le même fichier).
  - Les 12 MOYEN ont un objet de constantes, mais des littéraux dans les `index.html` ou une transition qui est un objet
    de matière (front météo, lavis qui s'ouvre, défaut de repérage riso, courbes qui montent dans un shader).
  - Les 4 DIFFICILE n'ont pas de code commun, ou leur mouvement est leur matière.
- **26 habillages** : 4 chemin + 4 papier + 1 punchy (3 tons) + 17 autres, un par identité.
- **19 mécaniques** : une seule est partagée par deux identités sans code commun (`survol-terrain` : `topo-relief` en
  three.js, `survol-pixel` en numpy) ; deux sont partagées par construction (`trace-chemin`, `pop-papier-12ips`).
- **Recettes : 26** = les 22 entrées actuelles + `survol-pixel` + les 3 déclinaisons de `lyrics-chemin`
  (`chemin-editeur`, `chemin-ardoise`, `chemin-portulan`).
- **Formats prouvés** : `narre-court` (43 shorts), `narre-long` (2 : quatre-quarts, premier tour du monde), `paroles-muet`
  (3), `boucle` (2 : pendule de Newton chrome, lucioles néon).
- **Combinaisons habillage × mécanique déjà prouvées par un short : 26** (une par recette). Aucun habillage n'a encore été
  porté sur deux mécaniques.

## 3. Fiches courtes

Palettes : 3 à 5 rôles clés (fond, texte, vif, second). « Couplages » = ce qui empêche de séparer, avec fichier et ligne.

### Déjà séparées
- **lyrics-chemin / `trace-chemin`** — Canvas 2D sans état (`renderAt(t)`). Mot entier posé sur le trait au moment dit,
  encre fraîche qui sèche en 0,35 s, pré-pose sous 0,30 s/mot (`chemin.js:13`) ; caméra de dessus sans perspective
  (jusqu'à ×6,1), glissés, virages, filés, zoom arrière final unique ; calage bpm 154,5 ou mots horodatés.
  Habillages : `plan-bleu` (`#1B4C92` / `#F3F0E4` / vif `#FFD84A` / `#FF7D5C`, Barlow Condensed), `editeur` (`#141B30`,
  coloration syntaxique, JetBrains Mono), `ardoise` (`#2C3836`, craie `#F1EEE6`, `textErode`), `portulan` (`#E9DCBC`,
  sépia, vermillon, Cormorant Garamond). `chemin.js` ne contient aucune couleur (`HB` chargé à la ligne 23).
  **Couplage habillage ↔ dessin** : `plan-bleu.js:155-156, 172` (`G.mat`, ligne `'vague1'`), `editeur.js:76, 83, 85`
  (`G.boites`, `G.flottaison`), `ardoise.js:47` (`G.moule`), `portulan.js:16-19` (`G.projection`, `G.route`) ;
  `chemin.js` lève « tronçon sans route (habillage) ». Les 4 habillages ne vont pas avec n'importe quel dessin.
  Incohérence : `identity.md` classe encore explicatif et histoire « inadaptées » alors que 2 shorts les prouvent.
- **famille papier / `pop-papier-12ips`** — Python (Pillow, OpenCV), mouvement à 12 i/s : pop en 4 pas (0,35 → 1,15 →
  0,96 → 1), chute en 5 pas, tampon, glissé de scène 0,25 s, sous-titres sur bande ; Sulafat, mix et master −14 LUFS
  dans le moteur. Habillage = `themes/<id>.json` (`tapis`, `couleurs`, `polices`) écrasant les globales de
  `papier.py:28-36`. Les 4 `video.py` ne diffèrent que par une ligne de docstring : **même épisode, 4 habillages**.
  Résidus : grille verte en dur `papier.py:251-256` (fausse sur le tapis bleu), 3 tapis en branches de `tapis()`
  (`:234-261`), RGB hors thème `elements.py:208-210, 448, 547`, `chaine.json` (marque) dans le moteur.

### FACILE à extraire
- **swiss-data / `chiffre-volet-compteur`** — D3 + GSAP seeké. Titre par masque horizontal, compteurs qui roulent, volet
  rouge plein cadre 0,45 s, push-in ×1,08, scènes de 4–5 s à 120 bpm. Habillage `T` de `grille.js:6-14`
  (`#F4F1EA`, `#E3241B`, `#111111`, `#1B4DE3`, Archivo Black, Inter). Résidus : `#D5CFC2` dans `index.html`, temps des
  scènes dans `index.html`.
- **brut-meme / `punch-cut-slam`** — PixiJS + GSAP. Coupes franches au temps, punch-in ×1,15 en 3 images, slam de mot,
  inversion noir/jaune, texte ajusté à la largeur. Habillage `#111111`, `#FFE600`, `#FF2D2D`, Anton, Inter 900.
  Palette écrite 3 fois dans `brut.js` (`:15`, `:16`, `BASE_CSS` `:184`).

### MOYEN
- **lyrics-punchy / `colonne-mot-a-mot`** — DOM + SVG sans état. Mot qui tombe sur le temps, colonne justifiée par l'axe
  `wdth` (`fit()`), mur de 4 lignes passées en camaïeu, carton penché. Camaïeux dans le moteur (`lyrics.js:11-16`),
  police en dur (`:37, 41, 47, 309-310`). **La police à axe de largeur fait partie de la mécanique** (`setupMeasure`
  lève une erreur sans `wdth`).
- **gazette-1900 / `tourniquet-tampon`** — page qui tourne (−540° → ±1,5°), tampon, dépêche en machine à écrire, 128 bpm ;
  matière film par `post.py`. `pageHTML` porte le titre « LE PETIT CRIEUR » (`gazette.js:70`) ; le tremblement de
  projecteur (mouvement) est dans `post.py` avec la matière.
- **bauhaus-kinetic / `puzzle-grille-morph`** — Paper.js + anime.js + flubber, snap-90, stagger en grille, morph, volet en
  6 colonnes. `C` dans `bk.js:7` mais 16–20 hex dans `index.html` ; le stagger dépend de la géométrie des tuiles.
- **aquarelle-conte / `lavis-multiplan`** — p5 (calques pré-rendus) + Paper.js, travelling multiplan, « lavis qui
  s'ouvre » (`bloom()`, `aq.js:82-87`) : **la transition est la matière**. 52 hex dans `index.html`.
- **atlas-grave / `carte-trace-panoramique`** — D3 geo + GSAP, fleuves en `stroke-dashoffset`, panoramique lent, sceau.
  Matière en PNG générés (`textures.py`) : bon point. Côtes codées dans `atlas.js`.
- **carte-meteo / `carte-champs-front`** — canvas + d3-geo Lambert + isobares ; **le front météo est la transition**
  (`drawFront`, `frontS`, `meteo.js:201-230`).
- **cosmos-doc / `travelling-cine-3d`** — three.js + bloom + grain, dolly lent, interlettrage qui se resserre, noir de
  0,6 s entre plans. Littéraux `cosmos.js:100, 155-159` ; matière (`setup()`) séparée de la caméra : bon point.
- **topo-relief / `survol-terrain`** — three.js, relief extrudé, courbes qui s'allument en montant (shader `uLevel`),
  orbite de drone, plongée. Rampe hypsométrique et lumières en dur (`topo.js:56-97`).
- **survol-pixel / `survol-terrain`** — numpy, lancer de rayons, palette indexée 270×480 ×4, une caméra qui vole sans
  coupe (`CameraPath`, `survol.py:132`). Biomes = 2 habillages partiels (`Palette(BIOME)`). Tables d'ombre et de brume
  liées aux noms de matière (`set_lut`, `set_haze`).
- **riso-zine / `impression-on-twos`** — p5 (une couche par encre) + GSAP quantifié à 12 i/s, défaut de repérage tiré à
  chaque pas : **l'architecture à 3 encres est la palette**.
- **tableau-craie / `ecriture-trace-chiffon`** — deux moteurs (Rough.js / Manim). Tracé progressif indépendant des
  couleurs ; grain de craie dans le rendu.
- **pixel-arcade / `simulation-deterministe`** — 3 simulations (`ring.js`, `course.js`, `conquest.js`), mouvement
  quantifié, mosaïque de pixels. Simulations neutres de couleur sauf `course.js:13` ; 22–44 hex dans les `index.html`.

### DIFFICILE
- **trait-continu / `traceur-escalier-plaque`** — palette facile (`traceur.py:35-41`), mais le traceur (plaque, règles,
  curseurs, chariot) **est** le mouvement.
- **pastel-diorama / `maquette-rebond`** — Zdog dans un short, A-Frame dans l'autre ; 46 littéraux, couleurs dans la
  définition des personnages, timeline écrite par état de contenu (`index.html:137`).
- **neon-lab / `orbite-phenomene-neon`** — twgl, Matplotlib, three.js ; couleurs en `vec3` dans `field.glsl.js` ; la
  matière est le shader et le grade.
- **liquid-chrome / `plan-sequence-matiere`** — Babylon, Taichi, three.js ; aucune ligne commune ; la matière (chrome,
  physique) est la mécanique.

## 4. Voisinages repérés (matière pour `matrice.md`)

- **Habillages proches** : craie (`craie-verte` ↔ `ardoise`), parchemin (`gravure-parchemin` ↔ `portulan` ↔
  `carnet-archives`), crème plat (`grille-suisse` ↔ `bauhaus-primaires`), noir 3D (`neon-labo` ↔ `cosmos-noir` ↔
  `chrome-irise`), grille pixel 270×480 commune (`arcade-marine` ↔ `pixel-jour`).
- **Mécaniques proches, non fusionnées** : tracés `stroke-dashoffset` (tableau-craie, atlas-grave, une scène de
  swiss-data) ; mouvement à 12 i/s (riso-zine, papier, pixel-arcade `steps(6)`) ; travelling 3D (cosmos-doc, topo-relief,
  neon-lab, liquid-chrome) ; volet (swiss-data `addWipe` et bauhaus `makeWipe`, deux codes).
- **Même sujet, deux recettes** : `atlas-grave__histoire__premier-tour-du-monde-1519-1522` et
  `lyrics-chemin__histoire__le-premier-tour-du-monde` (habillages voisins, mécaniques différentes) : un contrôle gratuit
  pour la règle de reconnaissance.

## 5. Dettes repérées en passant (hors composition)

- 14 modules copiés dans chaque short sans source unique (toute correction est à répliquer).
- `lyrics-chemin/identity.md` et `recipes/` en retard sur les 3 déclinaisons.
- Familles « adaptées » dans les `identity.md` mais jamais prouvées : presque toutes les identités en déclarent 1 à 3.
- `out/report/recognition.json` mesure 43 shorts sur 48 (les 5 shorts de paroles et narrés longs du 19/11 n'y sont pas).
