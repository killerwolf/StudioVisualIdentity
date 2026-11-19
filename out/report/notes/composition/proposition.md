# Composition — le catalogue en briques (proposition, 2026-11-19)

Statut : **proposition à valider**. Ce document décrit le modèle visé. Rien n'est migré : `out/identities/`,
`out/shorts/` et `out/shared/` sont inchangés. Le plan d'exécution est dans [`migration.md`](migration.md),
l'état actuel du catalogue identité par identité dans [`inventaire.md`](inventaire.md), les premières combinaisons à
essayer dans [`matrice.md`](matrice.md), et une maquette de vitrine dans [`vitrine-composer.html`](vitrine-composer.html).

## 1. Le constat

Une « identité » du catalogue regroupe aujourd'hui deux choses différentes :

- **la pâte** (statique) : palette, matière, typographies, objets, lumière. C'est ce qu'on voit sur une image fixe ;
- **la mécanique** (dynamique) : comment le texte arrive, comment la caméra et les éléments bougent, le rythme et les
  transitions. C'est ce qu'on voit seulement en vidéo.

Le dépôt le montre déjà trois fois, sans l'avoir nommé :

| Preuve | Mécanique commune | Habillages | Où |
|---|---|---|---|
| `lyrics-chemin` | texte posé sur un trait, caméra de dessus qui suit la pointe, zoom arrière final qui révèle un dessin | `plan-bleu`, `editeur`, `ardoise`, `portulan` (4 shorts) | `out/shared/chemin-moteur/habillages/*.js` |
| famille papier | pop stop-motion à 12 i/s, bandes inclinées, sous-titres sur bande | `papier-decoupe`, `atelier-papier`, `carnet-archives`, `cabinet-curiosites` (8 shorts, même texte) | `out/shared/papier-moteur/themes/*.json` |
| `lyrics-punchy` | colonne justifiée par l'axe de largeur, mur de lignes passées, carton illustré | camaïeux `nuit`, `lagon`, `braise` (dans un seul short) | `CAMAIEUX` dans `out/shared/lyrics-moteur/lyrics.js` |

Trois autres indices vont dans le même sens :

- `core-tokens.schema.json` découpe déjà les tokens en trois blocs : `color` et `typography` (pâte), `motion` et
  `transitions` (mécanique), `safeAreaPx` et `canvas` (format). Le modèle ci-dessous sort de ce découpage, il ne
  l'invente pas.
- `index.json` connaît déjà la notion : `variantOf`, `variants` et `variantAxis.shared/varies` décrivent exactement
  « même mécanique, autre habillage » pour la famille papier. La règle de `fieldNotes.variantOf` (« même moteur, autre
  fond/palette/polices = dérivation, pas nouvelle identité ») devient la règle générale ci-dessous.
- `recognition.py` ne mesure que la pâte (histogrammes Lab et de bords sur 8 images fixes). Les 4 shorts papier se
  rangent par thème, pas par mécanique : chacun a pour plus proche voisin son jumeau du même thème. L'outil de
  reconnaissance actuel juge donc des **habillages**, pas des identités.

## 2. Le modèle

**Vidéo = Habillage × Mécanique × Format (+ Son).** Une combinaison validée, avec un nom, s'appelle une **recette**.

### 2.1 Habillage (la pâte)

Tout ce qu'une image fixe montre, et rien de ce qui bouge. Un habillage fournit :

| Bloc | Contenu | Exemple (`plan-bleu`) |
|---|---|---|
| `palette` | rôles nommés, pas des couleurs libres : `fond`, `surface`, `encre` (texte courant), `vif` (couleur réservée à l'élément actif : mot dit, chiffre qui tombe), `second` (annotations), `decor[]` ; contraste calculé de chaque rôle sur `fond` et `surface` | fond béton, surface bleu de plan, encre blanche, vif jaune, second rouge |
| `typo` | rôles `titre`, `texte`, `mono` (et `manuscrit` s'il existe) : famille, slug @fontsource, graisses, axes variables, hauteur de capitale, écritures couvertes (latin, arabe…) | Barlow Condensed 700/800, JetBrains Mono |
| `matiere` | sol, support (feuille, écran, ardoise…), grain, nature du trait, bords (découpés, nets, pixel) | plan plié scotché, grain d'écran |
| `lumiere` | direction, ombre portée (oui/non, qui en porte), vignette, effet d'écran | ombres sur les objets seulement, vignette légère |
| `objets` | catalogue d'objets de décor dessinés par code (id, taille, règle « aucun mot dessus ») | règle, crayon, scotch |
| `lisibilite` | corps plancher à l'écran (`corpsMinPx`), contraste minimal du texte, couleur réservée, interdits (ex. pas de texte sur `decor`) | 120 px pour le mot dit |
| `contraintes` | ce que la matière impose à n'importe quelle mécanique : `grillePixel` (270×480 ×4), `paletteIndexee`, `projection` attendue (`plane`, `3d`, `ecran`), `cadence` imposée (12 i/s du papier) | aucune |
| `sonMatiere` | bruitages qui viennent de la matière (pose de papier, craie, clavier) — facultatif | — |
| `adaptateurs` | pour chaque mécanique qu'il sait habiller : le fichier qui traduit la pâte dans le vocabulaire du moteur | `trace-chemin` → `out/shared/chemin-moteur/habillages/plan-bleu.js` |

Un habillage ne contient **aucune durée, aucun easing, aucune caméra**. S'il en contient, c'est de la mécanique et elle
doit sortir (voir § 6, la cadence du papier, cas limite).

### 2.2 Mécanique (le mouvement)

Tout ce qui ne se voit qu'en vidéo. Une mécanique fournit :

| Bloc | Contenu | Exemple (`trace-chemin`) |
|---|---|---|
| `texte` | comment le texte entre, reste et sort ; mots à l'écran au plus ; unité (mot, ligne, chiffre) | mot entier posé sur le trait au moment où il est dit, encre fraîche qui sèche en 0,35 s |
| `camera` | type (fixe, plan-séquence, survol, coupes), projection, vitesses bornées | dessus sans perspective, translation/rotation/échelle, zoom arrière unique |
| `scene` | ce qui bouge en dehors du texte (simulation, dessin qui se trace, pièces qui tombent) | la pointe trace le trait |
| `transitions` | la liste fermée des transitions autorisées | glissés, virages au temps, filés d'un temps |
| `rythme` | ce qui pilote le temps : voix (lignes horodatées), musique (bpm), données, simulation | mots horodatés (chanson ou voix) |
| `contenu` | la donnée d'épisode attendue, avec son schéma | `dessins/<id>.json` + fichier de paroles ou de narration |
| `requiert` | **ce que l'habillage doit fournir**, rôle par rôle et crochet par crochet (§ 3) | `palette.vif`, `palette.encre`, `typo.titre`, crochets `floor`, `sheet`, `tip`, `objects`, `finish` |
| `formats` | formats que la mécanique sait remplir, durée naturelle | `paroles-muet`, `narre-long` |
| `moteur` | chemin du code, environnement (navigateur `renderAt(t)` ou Python), outil d'audit | `out/shared/chemin-moteur/chemin.js`, `out/tools/chemin_audit.mjs` |
| `signature` | les éléments de signature qui appartiennent au mouvement | caméra qui suit la pointe ; révélation finale |

### 2.3 Format

Le contrat de livraison, indépendant du style. Il remplace la logique écrite en dur dans `check.py`
(`dmax = 60.1 if fam == 'paroles' or longForm`).

| Format | Durée | Audio livré | Autres règles |
|---|---|---|---|
| `narre-court` | 10–20 s | voix off mixée | accroche < 1 s ; ≤ 3,2 mots/s |
| `narre-long` | 20–60 s | voix off mixée | remplace `"longForm": true` |
| `paroles-muet` | 10–60 s | piste silencieuse ou lit très bas ; la chanson est ajoutée dans l'application | paroles jamais traduites, vraies paroles hors dépôt |
| `boucle` | 10–20 s | voix off ou musique | dernière image = première (`loopable`) |

Tous partagent le canevas (1080×1920, 30 i/s, H.264 yuv420p) et les zones sûres (haut 220, bas 320, droite 120, gauche
60–72). Un format pourra un jour être autre chose qu'un short vertical (carré, 16:9) : c'est la seule brique qui
toucherait alors au canevas.

**La famille de contenus n'est pas un format.** Aujourd'hui `paroles` sert aux deux : famille de contenus (comme
`histoire`, `explicatif`) et contrat de livraison (muet, jusqu'à 60 s). Dans le modèle, `famille` reste une étiquette du
short (le sujet) et `format` décrit la livraison. `lyrics-chemin__histoire__le-premier-tour-du-monde` est un short de
famille `histoire` au format `narre-long` ; `lyrics-chemin__paroles__claudes-plan` est de famille `paroles` au format
`paroles-muet`.

### 2.4 Son

Brique facultative, choisie par recette ou par épisode : `voix` (fournisseur, nom, modèle, langue : Arnold, Sulafat,
ElevenLabs…), `lit` (musique ou nappe, niveau, ducking), `sfx` (banque), `master` (−14 LUFS). Outils : `tts.py`,
`sound.py`, et `pipeline/son.py` pour le papier (qui mixe lui-même : couplage noté dans `inventaire.md`).
Les bruitages **de matière** (papier posé, craie qui crisse) restent dans l'habillage (`sonMatiere`) ; les bruitages **de
mouvement** (whoosh d'un filé, impact d'un chiffre) restent dans la mécanique ; la brique Son ne porte que la voix, le lit
et le mixage.

### 2.5 Recette

Une recette est une combinaison nommée et validée :

```json
{
  "id": "lyrics-chemin",
  "nom": "Lyrics chemin",
  "habillage": "plan-bleu",
  "mecanique": "trace-chemin",
  "formats": ["paroles-muet"],
  "son": null,
  "statut": "validee",
  "signaturePortee": { "habillage": ["plan bleu plié sur béton", "encre jaune réservée au mot dit"],
                       "mecanique": ["caméra de dessus qui suit la pointe", "zoom arrière final qui révèle le dessin"] },
  "promesse": { "fr": "…", "en": "…" },
  "public": ["teens", "adults"],
  "confusableWith": ["topo-relief", "atlas-grave"],
  "dossier": "out/identities/lyrics-chemin/",
  "shorts": ["out/shorts/lyrics-chemin__paroles__claudes-plan"]
}
```

- **Les 22 entrées actuelles et `survol-pixel` (fusionnée dans `main`) deviennent 23 recettes, avec le même id.** Le dossier `out/identities/<id>/` reste leur
  dossier de preuve (identity.md, tokens.json, recipes/, poster, planche) ; StudioGabarit et `bootstrap_studio.py`
  continuent de les trouver au même endroit.
- Les 3 déclinaisons de `lyrics-chemin` deviennent 3 recettes nouvelles (total : 26 recettes, 26 habillages, 19 mécaniques ; voir `inventaire.md`) (ids proposés : `chemin-editeur`,
  `chemin-ardoise`, `chemin-portulan`), dont les shorts existants gardent leur nom de dossier.
- La règle de `fieldNotes.variantOf` se généralise : **une nouvelle pâte sur une mécanique existante est une nouvelle
  recette (et un nouvel habillage), pas une nouvelle identité.** `variantOf` devient dérivable des recettes (deux recettes qui
  partagent une mécanique sont sœurs par construction) ; il est gardé dans `identities[]` pour les lecteurs actuels.

### 2.6 La doctrine du mélange, revue

`AGENTS.md` dit aujourd'hui : garder la signature d'**une** identité, n'emprunter aux autres que la structure ; mélanger deux
signatures donne un rendu générique. Le modèle ne la contredit pas, il la précise :

- chaque `signatureToPreserve` actuelle est coupée en deux moitiés, habillage et mécanique (ex. `swiss-data` : grille
  12 colonnes, Archivo Black, rouge/noir/bleu = habillage ; volets rouges et un chiffre par écran = mécanique) ;
- une recette déclare dans `signaturePortee` **quelle brique porte la signature** ;
- le mélange interdit reste interdit : deux habillages dans une même vidéo, ou deux mécaniques qui se disputent l'écran.
  Ce qui devient permis : une pâte reconnaissable sur un mouvement emprunté, ou un mouvement reconnaissable habillé
  d'une autre pâte. C'est exactement ce que `lyrics-chemin` a fait quatre fois.

## 3. Les interfaces entre briques

### 3.1 Une spécification neutre, plus un adaptateur par moteur

Les moteurs du dépôt ne parlent pas la même langue : le papier lit un JSON (`themes/<id>.json` : `tapis`, `couleurs.MAT`,
`polices.display`…), le chemin appelle des fonctions (`floor`, `sheet`, `objects`, `tip`, `finish`), lyrics-punchy lit un
dictionnaire `CAMAIEUX` (`bg`, `mur[3]`, `accent`, `encre`), et la plupart des autres identités ont leurs couleurs écrites
dans le code de chaque short. Un format unique d'habillage « que tout moteur lit » obligerait à réécrire tous les moteurs.

On fait donc deux étages :

1. **`habillage.json`, neutre** : les rôles du § 2.1, en valeurs (hex, slug de police, px). C'est ce que lisent l'index,
   `check.py`, la vitrine et un humain. Il ne contient pas de code.
2. **un adaptateur par mécanique** : le fichier que le moteur lit réellement (`habillages/plan-bleu.js`,
   `themes/carnet-archives.json`, une entrée de `CAMAIEUX`). L'adaptateur prend ses valeurs dans `habillage.json` quand
   le moteur le permet (cible), ou les recopie en attendant (état de départ : c'est déjà le cas, les fichiers existent).
   `check.py --briques` contrôle que les couleurs et polices de l'adaptateur sont celles du `habillage.json`.

Une partie de l'habillage n'est pas réductible à des valeurs : le dessin d'une feuille pliée, d'une ardoise, d'un
écran. Ces **crochets de matière** sont du code et vivent dans l'adaptateur. La mécanique déclare ceux qu'elle appelle ;
l'habillage déclare ceux qu'il fournit.

### 3.2 Ce qu'un habillage doit fournir à une mécanique

| Catégorie | Champ | Obligatoire pour |
|---|---|---|
| Couleurs | `palette.fond`, `palette.encre` (contraste ≥ 4,5:1 sur la surface qui porte le texte) | toutes |
| | `palette.vif` (réservée, jamais en décor) | mécaniques à élément actif : `trace-chemin`, mur de paroles, chiffre qui tombe |
| | `palette.second` | mécaniques à annotations |
| | `palette.serie[n]` (n couleurs distinguables) | mécaniques de données, de simulation (billes, territoires) |
| Typo | `typo.titre` + `typo.texte` avec hauteur de capitale | toutes |
| | axe variable `wdth` | colonne justifiée (`lyrics-punchy`) |
| | écritures couvertes | épisode en arabe, etc. |
| Matière | crochets nommés (ex. `floor`, `sheet`, `tip`, `objects`, `finish`, `textErode`) ou leurs équivalents par moteur | selon `mecanique.requiert.crochets` |
| | `projection` compatible | une mécanique de dessus (`plane`) ne prend pas un habillage qui exige un sol en perspective (`3d`) |
| Lisibilité | `corpsMinPx` (lu par l'audit : `chemin_audit.mjs` lit déjà `floorPx` de l'habillage), contraste du texte | toutes |
| Contraintes | `grillePixel`, `paletteIndexee`, `cadence` | la mécanique doit les respecter, ou la case est `incompatible` |

### 3.3 Ce qu'une mécanique attend et promet

Une mécanique **attend** : un habillage qui remplit son `requiert`, un fichier de contenu conforme à son schéma, un format
qu'elle sait remplir, une piste de temps (voix horodatée, bpm ou données). Elle **promet** : un rendu déterministe
(`renderAt(t)` ou équivalent Python), le respect des zones sûres du format, un audit si elle en a un, et le respect des
`contraintes` de l'habillage.

Exemple de déclaration (`out/mecaniques/trace-chemin/mecanique.json`, extrait) :

```json
{
  "id": "trace-chemin",
  "moteur": { "code": "out/shared/chemin-moteur/chemin.js", "env": "navigateur", "audit": "out/tools/chemin_audit.mjs" },
  "requiert": {
    "palette": ["fond", "encre", "vif", "second"],
    "typo": ["titre"],
    "crochets": ["prepare", "floor", "sheet", "under", "tip", "objects", "finish"],
    "crochetsFacultatifs": ["afterInk", "textErode", "dryColor", "route"],
    "valeurs": ["cap", "gap", "em", "trackMax", "floorPx", "maxPx"],
    "projection": "plane"
  },
  "contenu": { "dessin": "out/shared/chemin-moteur/dessins/<id>.json", "episode": "paroles.*.json | narration-chemin.json" },
  "formats": ["paroles-muet", "narre-long"],
  "rythme": "mots horodatés (chanson ou voix)"
}
```

Le `requiert.crochets` de `trace-chemin` est la liste réelle des fonctions exportées par `habillages/plan-bleu.js`
(`prepare, floor, sheet, under, tip, afterInk, objects, finish`) ; l'interface complète est décrite dans
`out/report/notes/lyrics-chemin/declinaisons/README.md` § « Ce qui change ».

### 3.4 Brique déclarée, brique exécutable

`AGENTS.md` le dit : pour la plupart des identités, « les tokens sont de la documentation, le code des scènes écrit les
valeurs en dur ». Il faut donc distinguer deux niveaux pour chaque brique :

- **déclarée** : un manifeste décrit la brique (valeurs, rôles, signature). On peut la lire, la comparer, la mettre dans
  la matrice. On ne peut pas encore l'appliquer à une autre mécanique.
- **exécutable** : un adaptateur existe et le moteur l'applique sans toucher au code de la mécanique.

Aujourd'hui seuls trois moteurs ont des habillages exécutables : `chemin-moteur` (4), `papier-moteur` (4), `lyrics-moteur`
(3 camaïeux). Tout le reste est déclarable sans toucher au code, et devient exécutable mécanique par mécanique (voir
`migration.md`). L'index affiche ce niveau ; la vitrine aussi.

## 4. Arborescence

Nouveaux dossiers, à côté de l'existant (rien n'est déplacé ni renommé) :

```
out/
  habillages/<id>/
    habillage.json        palette, typo, matière, lumière, objets, lisibilité, contraintes, adaptateurs
    planche.jpg           1 image fixe par mécanique déjà habillée (copie de stills existants, ou essai)
  mecaniques/<id>/
    mecanique.json        texte, caméra, scène, transitions, rythme, contenu, requiert, formats, moteur, signature
    README.md             (facultatif) comment écrire un épisode
  formats/<id>.json       durée min/max, audio livré, canevas, zones sûres, règles de débit
  sons/<id>.json          voix, lit, sfx, master (facultatif)
  recettes/<id>.json      habillage + mécanique + formats + son + signature + curation + dossier de preuve
  identities/<id>/        INCHANGÉ : dossier de preuve de la recette du même id (identity.md, tokens.json, recipes/…)
  shared/<moteur>/        INCHANGÉ : code des moteurs et des adaptateurs (chemin.js importe habillages/<id>.js par chemin)
  shorts/<recette>__<famille>__<sujet>/   INCHANGÉ ; short.json reçoit habillage, mecanique, format, recette
```

Pourquoi les adaptateurs restent dans `out/shared/` : `chemin.js` les importe par un chemin écrit en dur
(`/out/shared/chemin-moteur/habillages/${D.habillage}.js`), le papier lit `themes/<id>.json` relativement à son pipeline.
Les déplacer changerait du code de rendu pour un gain nul ; `habillage.json` pointe vers eux.

Pourquoi les recettes ont leur propre dossier alors que `out/identities/` existe : `out/recettes/<id>.json` est un petit
manifeste de composition ; `out/identities/<id>/` reste la documentation longue (16 sections) et les images. Une nouvelle
recette peut naître avec seulement son manifeste et un short ; elle n'a un dossier `identities/` que si on lui écrit un
design system complet.

## 5. Le nouvel index

`out/identities/index.json` passe en `schemaVersion: "2.0"`, **en ajoutant** des sections, sans retirer `identities[]`
(lue par la vitrine actuelle, `bootstrap_studio.py`, StudioGabarit et les agents) :

```json
{
  "schemaVersion": "2.0",
  "counts": { "recettes": 26, "habillages": 26, "mecaniques": 19, "formats": 4, "shorts": 50 },
  "identities": [ { "id": "lyrics-chemin", "…": "champs actuels inchangés",
                    "habillage": "plan-bleu", "mecanique": "trace-chemin", "formats": ["paroles-muet"] } ],
  "habillages": [ { "id": "plan-bleu", "nom": "Plan bleu", "niveau": "executable", "palette": {}, "typo": {},
                    "adaptateurs": { "trace-chemin": "out/shared/chemin-moteur/habillages/plan-bleu.js" },
                    "recettes": ["lyrics-chemin"], "planche": "out/habillages/plan-bleu/planche.jpg" } ],
  "mecaniques": [ { "id": "trace-chemin", "niveau": "executable", "moteur": {}, "requiert": {}, "formats": [],
                    "recettes": ["lyrics-chemin", "chemin-editeur", "chemin-ardoise", "chemin-portulan"] } ],
  "formats": [ { "id": "narre-long", "dureeSec": [20, 60], "audio": "voix" } ],
  "compatibilite": [
    { "habillage": "editeur", "mecanique": "trace-chemin", "format": "paroles-muet", "etat": "teste",
      "preuve": ["out/shorts/lyrics-chemin__paroles__claudes-plan-tech"], "recette": "chemin-editeur" },
    { "habillage": "craie-verte", "mecanique": "trace-chemin", "etat": "a-tester",
      "raison": "requiert rempli par habillage.json ; pas d'adaptateur" }
  ]
}
```

La matrice est **creuse** : seules les cases qui ont une preuve ou un jugement sont écrites ; une case absente vaut
« inconnu ». Les quatre états sont **calculés** par `build_index.py`, pas déclarés à la main, sauf `incompatible` qui
exige une raison écrite :

| État | Critère (vérifiable) |
|---|---|
| `teste` | au moins un short dont `short.json` déclare ce couple (et ce format) passe `check.py` |
| `compatible` | l'habillage a un adaptateur pour cette mécanique **et** au moins une image fixe rendue (`out/habillages/<id>/planche.jpg` ou `essais/`) ; pas encore de short |
| `a-tester` | `habillage.json` remplit `mecanique.requiert` (rôles, valeurs, projection) mais aucun adaptateur n'existe |
| `incompatible` | une contrainte est violée (ex. `survol-pixel` exige une grille 270×480 indexée et un sol en perspective ; `trace-chemin` exige un plan sans perspective et du texte anticrénelé à 120 px) ; raison obligatoire |

`curation.confusableWith` se dédouble : `confusableWith` des habillages (même pâte) et des mécaniques (même mouvement),
la recette héritant des deux.

## 6. Cas limites repérés

- **La cadence du papier (12 i/s en 4 pas)** : c'est un mouvement, donc de la mécanique, mais il est indissociable de la
  matière (un papier découpé ne glisse pas en douceur). On le range dans la mécanique `pop-papier-12ips` et on l'écrit dans
  `habillage.contraintes.cadence` des 4 habillages papier : un habillage papier sur une mécanique fluide sera
  `incompatible` tant qu'on ne l'a pas essayé.
- **Le pixel commun** : `survol-pixel` (PR #4, fusionnée dans `main` en `ee30e24`, pas encore dans `identite-lyrics`) et `pixel-arcade` partagent la
  grille 270×480 ×4, et la note de `survol-pixel` dit déjà que « ce n'est pas une différence ». Dans le modèle : deux
  habillages distincts (palette, polices, lumière), qui partagent une contrainte `grillePixel`. La contrainte peut
  devenir un habillage parent commun (`pixel-16`) si un jour on veut porter l'un sur la mécanique de l'autre.
- **La mécanique qui est la matière** : `trait-continu` (le traceur, ses règles et sa plaque sont le mouvement),
  `liquid-chrome` (une matière liquide simulée), et les transitions qui sont des objets de matière : le front de
  `carte-meteo`, le lavis qui s'ouvre d'`aquarelle-conte` (`bloom()`), le défaut de repérage de `riso-zine`, les courbes
  qui montent dans le shader de `topo-relief`. Pour celles-là, la séparation reste déclarée : voir `inventaire.md`.
- **L'habillage lié au dessin** (`trace-chemin`) : les 4 habillages du chemin lisent des champs propres à leur dessin
  (`G.mat` et la ligne `'vague1'` pour `plan-bleu`, `G.boites` pour `editeur`, `G.moule` pour `ardoise`, `G.route` pour
  `portulan` ; détail dans `inventaire.md`). Le **dessin** est du contenu d'épisode, donc il appartient à la mécanique
  (`contenu`), mais ses primitives de décor doivent devenir génériques (`boites`, `cercle`, `route`, `final` déclarés
  dans `mecanique.json`) pour qu'un habillage sache les dessiner toutes, ou déclarer celles qu'il ne sait pas faire
  (`habillage.adaptateurs.trace-chemin.primitives`). Tant que ce n'est pas fait, un habillage du chemin n'est
  `compatible` qu'avec son propre dessin.
- **Le texte comme matière** : dans `lyrics-punchy`, la police variable (axe `wdth`) est à la fois typographie (habillage)
  et moteur de mise en page (mécanique). On la range dans `mecanique.requiert.typo` : la mécanique exige une police à axe
  de largeur ; l'habillage choisit laquelle.

## 7. Les outils

| Outil | Aujourd'hui | Demain |
|---|---|---|
| `check.py` | durée max par `family == 'paroles'` ou `longForm` | lit `short.json.format` → `out/formats/<id>.json` (durée, audio attendu, débit) ; repli sur l'ancienne règle si `format` est absent. Nouveau mode `check.py --briques` : chaque manifeste est valide, chaque `recette` pointe vers des briques qui existent, l'adaptateur a les couleurs et polices de son `habillage.json`, `palette.encre` a ≥ 4,5:1 sur la surface du texte, `corpsMinPx` ≥ 54 (ou exception écrite) |
| `build_index.py` | dictionnaires en dur (`ORDER`, `CURATION`, `FAMILIES`, `LYRICS`, `VOICE_*`…) | lit `out/recettes/*.json` (curation, signature, ordre, voix) ; ajoute `habillages[]`, `mecaniques[]`, `formats[]`, `compatibilite[]` ; garde `identities[]` intact. Les dictionnaires en dur migrent dans les manifestes, un par un |
| `recognition.py` | clé = préfixe du dossier (`d.name.split('__')[0]`), descripteur d'apparence seul, 43 shorts mesurés sur 48 | clé lue dans `short.json` (`habillage`, `mecanique`, repli sur le préfixe). Deux mesures : **habillage** (descripteur actuel, inchangé) et **mécanique** (descripteur temporel nouveau, § 8). Sans ce changement, les 4 habillages de `lyrics-chemin` apparaîtraient comme un échec de reconnaissance alors qu'ils sont voulus |
| `chemin_audit.mjs`, `lyrics_audit.mjs` | audits de mécanique | inchangés ; déclarés dans `mecanique.moteur.audit` |
| `bootstrap_studio.py` | `--from <identité>` | inchangé (une recette a le même id) ; plus tard `--habillage X --mecanique Y` pour une recette `a-tester` |
| vitrine (`out/showcase/build.py`) | une carte par identité | ajoute une vue « composer » (maquette : `vitrine-composer.html`) qui lit `compatibilite[]` ; les cartes actuelles deviennent la vue « recettes » |

## 8. La règle de reconnaissance

**On mesure la reconnaissance des habillages et des mécaniques séparément ; une recette est reconnaissable quand ses deux
briques le sont.**

1. **Habillage** — c'est ce que l'outil actuel sait mesurer, et c'est ce que le public reconnaît d'abord sur une
   miniature. Test : pour chaque short, son plus proche voisin (descripteur Lab + bords actuel) doit avoir **le même
   habillage**. Le test qui compte est celui **entre mécaniques différentes** : deux shorts du même habillage sur deux
   mécaniques doivent rester voisins. Aujourd'hui aucun habillage n'a été porté sur deux mécaniques : ce test n'a pas
   encore de matière (c'est un des buts de `matrice.md`).
2. **Mécanique** — nouveau descripteur temporel, mesuré sur les images en niveaux de gris réduites (l'apparence ne compte
   plus) : énergie de différence image à image dans le temps, mouvement global estimé (corrélation de phase : translation,
   rotation, échelle de la caméra), taux de coupes (détection de changement de plan), part de l'image qui bouge. Test :
   le plus proche voisin doit avoir **la même mécanique**, et ce test compte surtout **entre habillages différents** :
   les 4 shorts de `trace-chemin` (4 habillages) et les 8 shorts de `pop-papier-12ips` (4 habillages) sont les premiers
   jeux de contrôle — ils existent déjà.
3. **Voisinage** — deux habillages dont la distance est inférieure à la distance moyenne entre deux shorts d'un même
   habillage sont un doublon probable : les fusionner, ou en faire un parent et un enfant. Candidats déjà signalés par les
   notes et l'inventaire : `ardoise` / `craie-verte` (tableau-craie), `portulan` / `gravure-parchemin` (atlas-grave) / `carnet-archives`, `grille-suisse` / `bauhaus-primaires`
   (voir `matrice.md`).
4. **Le juge aveugle** (images fixes) juge les habillages ; un juge aveugle sur vidéo muette en niveaux de gris jugerait
   les mécaniques. Les résultats existants (`blindJudge14`, `blindJudgeLot2`) sont rattachés aux habillages des recettes
   qu'ils ont jugées.

Conséquence pour une chaîne : la marque d'une chaîne, c'est d'abord **un habillage fixe** ; elle peut alterner deux ou
trois mécaniques selon le sujet (un chiffre → mécanique de données, une histoire → trace sur carte), à condition que
l'habillage reste reconnaissable entre ses mécaniques (test 1).

## 9. Décisions demandées à Hamdi

1. Valider les quatre briques et le mot « recette » (et l'emplacement `out/recettes/` à côté d'`out/identities/` gardé
   tel quel).
2. Valider la règle de reconnaissance à deux étages (§ 8).
3. Valider l'ordre de `migration.md` : manifestes seulement d'abord (aucun rendu touché), outils ensuite, adaptateurs
   enfin, mécanique par mécanique.
4. Choisir les 2 ou 3 premières combinaisons de `matrice.md` à essayer.
