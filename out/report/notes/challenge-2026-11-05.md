# Contre-expertise des directions du 2026-11-05

Agent adversarial de la fabrique d'identités. Cible : `out/report/notes/directions-2026-11-05.md` (4 directions). Sources
croisées : `out/identities/index.json` (18 identités), `out/library-cards/catalogue.md`, `out/tools/STUDIO_BRIEF.md`,
`out/report/facts.md`, `out/report/failures.md`, `package.json`, et les planches-contact de tableau-craie, atlas-grave,
pastel-diorama, swiss-data, riso-zine, topo-relief, brut-meme, pixel-arcade, gazette-1900, bauhaus-kinetic et liquid-chrome,
que j'ai regardées.
Aucun code de scène, aucun rendu ni aucun commit dans le dépôt. Ce fichier est le seul que j'ai écrit dans le dépôt.

## Essais faits pour trancher (scratchpad, hors du dépôt, machine calme, charge < 1,7)

Dossier : `/tmp/claude-0/-home-user/8cf151ed-3f7a-5398-82ba-b09460d909f9/scratchpad/challenge/`.

| # | Essai | Résultat |
|---|---|---|
| E1 | **trait-continu sans skia** : venv jetable avec `shapely==2.2.0`, `opensimplex==0.4.5.1`, pycairo et numpy. Chemin shapely (hexagone + spirale + pont, 1 039 points en escalier de 6 px, 6 228 px), grain opensimplex, titre Fredoka 700 lu par PIL, dissolution par masque de bruit, pipe `bgra` vers x264 veryfast crf 14 | **3,89 s / 100 images**, et **md5 du mp4 identique sur deux exécutions**. Mais le champ de bruit opensimplex (540×960, plus un champ 270×480) coûte **9,9 s une seule fois** : il est impossible à recalculer à chaque image. |
| E2 | **tableau-depart, WAAPI** : 99 cellules × 6 bascules = 1 782 `element.animate()` en pause, seek par `currentTime`, CSS 3D `rotateX`, Chromium + SwiftShader (flags de `render.mjs`) | **md5 identique** au même t après des allers-retours vers t = 1,9 puis t = 0,1, y compris au milieu d'une bascule. 25,6 s / 100 images en capture **PNG** (le chiffre de 12,1 s du repérage, en JPEG, reste plausible). **Piège trouvé** : quand plusieurs volets sont empilés avec `fill:'both'`, un volet futur s'affiche **avant** son `delay` (le haut de la cellule montrait déjà un caractère suivant). Voir §3. |
| E3 | **Photosensibilité de la cascade** : 75 images de cascade analysées en luminance relative WCAG | Le plus grand écart de luminance moyenne sur un bloc de 25 % du cadre (540×960) en 2,5 s est **0,093**. Le seuil d'un flash général est 0,10. Le plus grand écart d'une image à la suivante sur le tableau est **0,0076**. Le plus grand écart sur un bloc de 270×270 est 0,124 (localisé et non répété). |
| E4 | **domino-cascade, coût réel** : three.js 0.187 (celui du dépôt), `InstancedMesh`, PCFSoft, 1080×1920, SwiftShader, capture JPEG q92 | 320 dominos / ombre 2048 : **38,9 s/100** ; **1 000 dominos / 2048 : 42,8** ; 1 000 / **1024 : 41,8**. Passer l'ombre à 1024 fait gagner **2 %, pas les 20 % annoncés**. Le nombre de dominos ne pèse presque pas : le coût vient du remplissage des pixels sous SwiftShader. |
| E5 | Contrastes WCAG de toutes les palettes, recalculés | Les chiffres du repérage sont justes. Il ne calcule pas trois paires qui comptent : terre/mer de carte-meteo, isobares/mer, palette/boîtier de tableau-depart (voir les §7). |

---

## 1. `trait-continu` — Trait continu

### 1.1 Confusion
Les identités les plus proches, avec leur `signatureToPreserve` :
- **tableau-craie** : « dark green chalkboard with chalk grain », « everything draws itself (Manim Create / stroke-dashoffset) »,
  « Caveat handwriting + Nunito titles », « eraser-cloth wipe between ideas ».
- **atlas-grave** : « laid-paper parchment and engraved hand-drawn maps », « ink that draws itself », « Cormorant Garamond /
  Cinzel serif », « wax seals, compass rose, slow pans ».
- **pastel-diorama** : « pink pastel toy diorama on a felt base », « soft rounded toys and invented recurring characters »,
  « Baloo 2 titles and pill labels », « bouncy back.out motion ».

**Verdict : on les distingue en moins d'une seconde.** Le premier indice est la couleur du fond : un orange plein et un gris
aluminium clair, alors que tableau-craie est vert ardoise sombre, atlas-grave parchemin et pastel-diorama rose. Le deuxième est
la matière : un trait graphite **unique** et fin, sans hachures, sans craie multicolore et sans 3D. C'est la direction la plus
éloignée des 18. Deux réserves :
- la typographie ronde (Fredoka) est cousine de Baloo 2 (pastel-diorama) et de Nunito (tableau-craie). Elle ne distingue rien
  dans la famille enfants : ce sont le fond et le trait qui portent l'identité ;
- **une promesse creuse sur l'escalier**. À 1:1, un pas de 6 px se lit comme un escalier. À l'échelle d'un téléphone (≈ 0,3 mm
  par marche) et après le ré-encodage de la plateforme, il ressemble à de **l'aliasing** et non à un mécanisme voulu (vu sur E1,
  réduit à 360 px). Il faut un pas de **12 px au minimum** et un trait de 6 à 8 px, sinon on abandonne l'escalier.

### 1.2 Règles
**Non conforme en l'état.** Prenez ensemble les éléments décrits : un jouet à dessin, un cadre en plastique épais aux coins
arrondis, un écran gris aluminium, un trait graphite unique, **deux molettes blanches en bas**, l'effacement **en secouant**, le
sous-titre « l'écran à manivelles », et l'argument « nostalgie du jouet » pour les adultes. Cela reproduit l'habillage
commercial de l'**Etch A Sketch** (Ohio Art, aujourd'hui Spin Master). Ce jouet est notoire et sa forme est défendue comme une
marque. Passer du rouge à l'orange n'y change rien : le produit est vendu en plusieurs couleurs, et c'est la combinaison
cadre, écran gris, deux molettes et secousse qui le fait reconnaître. Le repérage l'admet lui-même : sa promesse adulte repose
sur le fait qu'on **reconnaît le produit**. C'est la définition d'une imitation d'habillage. La règle du brief, « aucun
personnage/logo/œuvre existant », s'étend aux produits existants (consigne de la mission). **Je retire l'objet.**

**Variante imposée : on garde le mécanisme, on change l'objet.** On garde un seul trait continu, jamais levé, qui avance à
vitesse constante, la décomposition visible en deux axes, puis un effacement total.
- **Métaphore : « le traceur »**, une table traçante XY générique, sans marque. **Fond plein cadre orange `#F26A21`** (aucune
  identité ne l'utilise). La plaque de travail est le gris aluminium `#D3D4CE`, rectangulaire, **à angles vifs**, posée
  à plat et vissée par 4 vis aux coins. Il n'y a ni cadre jouet, ni bord en plastique brillant, ni molettes.
- **L'indice des deux axes devient deux règles graduées** : une le long du bord haut de la plaque, une le long du bord gauche.
  Un curseur triangulaire graphite glisse sur chacune, en proportion de x et de y. C'est le même indice pédagogique que les
  molettes (« deux axes font un trait en escalier »), sans le jouet. Un petit chariot (la tête du traceur) suit la pointe.
- **La transition signature cesse d'être la secousse** : secouer pour effacer, c'est le geste propre au produit. Elle devient
  **« l'avance plaque »** : la plaque entière remonte cran par cran (3 crans en `steps`, 0,6 s) et sort par le haut, puis une
  plaque vierge entre par le bas avec un « clac » de butée. Ce mouvement vertical mécanique, en crans, ne ressemble ni au chiffon
  horizontal de tableau-craie ni au volet de swiss-data. La dissolution par masque de bruit reste possible comme variante
  (« la plaque se démagnétise »), sans secousse du cadre.
- Interdits à écrire dans identity.md : deux boutons ronds dans les coins bas, un cadre rouge ou orange aux coins arrondis
  autour d'un écran gris, une secousse globale de l'objet, et tout nom ou allusion de produit dans le titre, le texte ou la
  narration.

**Faits des sujets (vérifiés)** : la plupart des escargots ont une coquille qui s'enroule vers la droite (dextre). L'insecte a
3 parties et 6 pattes, l'araignée 2 parties (céphalothorax et abdomen) et 8 pattes. Les 3 façades maritimes et les 3 frontières
terrestres de l'Hexagone sont la lecture scolaire admise. Le talon de la botte est bien les Pouilles et la pointe la Calabre.
**Aucun de ces sujets n'est dans `out/shorts`** : vérifié sur les 39 dossiers. Pour le dessin d'une fourmi ou d'une
araignée d'un seul trait, chaque patte doit faire un aller-retour superposé : la longueur du chemin double et il faut compter
2 fois plus de temps de tracé.

### 1.3 Assets
Les contours de la France et de l'Italie peuvent se tracer à la main : l'escalier et la simplification les absorbent. C'est le
seul cas où le tracé manuel est un choix de style et non un défaut. La règle sur les données géographiques est traitée au §2.3.
Si elle est adoptée, `trait-continu` peut exporter `world-atlas` une fois en JSON par Node, puis `simplify` dans shapely.

### 1.4 Faisabilité
**Confirmée sans skia (E1).** pycairo, shapely, numpy et le pipe ffmpeg suffisent : le résultat est déterministe (même md5 sur
deux exécutions) et l'état à t est calculé comme `substring(chemin, 0, v·t)`, sans horloge. skia-python n'apporte rien ici.
Trois corrections :
- **opensimplex** coûte 9,9 s par champ demi-résolution (numpy pur, sans numba). On calcule le grain et le masque de dissolution
  **une seule fois** par short et on les met en cache (`.npy`). On n'appelle jamais opensimplex sur un champ à chaque image.
  On peut aussi le remplacer par un bruit de valeurs numpy de 20 lignes, ce qui supprime une dépendance.
- shapely et opensimplex **ne sont pas dans `.venv`**. Le brief des studios dit « n'installe rien » : l'orchestrateur doit les
  préinstaller (`uv pip install shapely==2.2.0 opensimplex==0.4.5.1`, ce sont des roues PyPI et non des paquets système) et
  les ajouter à la liste d'installation d'`AGENTS.md`.
- `linemerge` ne relie pas les composantes disjointes : le repérage l'a vu. Il faut écrire les ponts, et ils se voient.

### 1.5 Coût
Le repérage annonce 4,94 s ; je mesure **3,89 s / 100 images** au repos. Le chiffre est crédible et c'est la direction la moins
chère après la famille papier (3,6 à 3,9 s, même chaîne). Avec la règle « ×2 à 3 en charge » de `facts.md`, on obtient **8 à
12 s / 100 images** : l'estimation du repérage est juste. Un short de 15 s représente ≈ 20 s au repos et ≈ 50 s en charge.
Il faut ajouter ≈ 10 s fixes pour le bruit, ou 0 s avec un cache.

### 1.6 Public et familles
Public : kids 6–10. Familles : enfants et geographie. **C'est le meilleur élargissement des quatre** : enfants n'a que 3
identités (tableau-craie, pastel-diorama, aquarelle-conte), qui sont sombre, rose 3D et crème aquarelle. Geographie en a 4.
Points à corriger :
- **débit** : à 2,0–2,3 mots/s, 15 s donnent ≈ 30 à 33 mots. Le sujet « Hexagone » qui nomme les 6 côtés dépasse : il faut
  nommer les familles de côtés (« trois au bord de la mer, trois avec nos voisins ») et non les 6 noms ;
- **≤ 4 mots à l'écran** : c'est compatible avec Fredoka 96–120 px sur la bande haute, qui devient une **bande orange au-dessus
  de la plaque** dans la variante ;
- la question d'enfant en accroche est bonne. La « nostalgie adulte » est à **retirer** : c'est l'argument du produit.

### 1.7 Photosensibilité et lisibilité
Pas de flash. La secousse disparaît dans la variante. L'avance de plaque déplace une grande surface claire sur un fond orange de
luminance proche : le contraste orange/plaque est de 2,05:1, l'écart de luminance est faible, il n'y a pas d'inversion.
Contrastes vérifiés : trait/plaque 7,31:1, texte `#1A1410` sur orange 5,96:1, bleu repère 5,59:1, crème `#FFF8EE` sur orange
brûlé 4,91:1. **Le crème sur l'orange principal tombe à 2,90:1, et le blanc à 3,06:1** : à interdire même pour les titres.

### 1.8 Polices
Fredoka est installée et inutilisée : c'est un bon choix. **Lexend n'est pas nécessaire** : Fredoka 500–600 à 58–64 px se lit
bien pour des légendes de 4 mots, et Nunito est installé en secours. **Aucune police nouvelle n'est requise.** Si le studio
veut un corps distinct, Lexend sera la seule ajoutée pour cette identité.

### 1.9 Verdict : **MODIFIER** (recommandée sous condition)
Correctif obligatoire : abandonner l'objet jouet (cadre, deux molettes, secousse) au profit du **traceur sur fond orange**
(plaque à angles vifs, deux règles à curseurs, transition « avance plaque »). Escalier de 12 px au minimum, trait de 6 à 8 px.
Bruit calculé une seule fois. Pas de Lexend. Pas d'argument de nostalgie.
Promesse « reconnaissable en 1 s » : en l'état, ce qu'on reconnaît, c'est **le produit d'un autre**. Après la correction, on
reconnaît un fond orange plein, une plaque grise et un trait unique qui avance avec ses deux curseurs : c'est assez distinct, à
prouver sur le premier still.

---

## 2. `carte-meteo` — Carte Météo

### 2.1 Confusion
- **swiss-data** : « visible 12-column grid on warm off-white », « one giant Archivo Black number per screen », « red wipe
  transitions », « palette limited to red / black / blue ».
- **riso-zine** : « cream paper with 2–3 overprinted spot inks (fluo pink, blue, yellow) », « misregistration + halftone
  dots », « Space Mono + Permanent Marker annotations », « stepped 12 fps motion, collage cut-outs ».
- **atlas-grave** et **topo-relief** : « laid-paper parchment and engraved hand-drawn maps » ; « dark forest-green 3D terrain
  block with glowing contour lines ».
- **Voisine omise par le repérage : pastel-diorama** (« pink pastel toy diorama… »). Son short « d'où vient la pluie » montre
  déjà un soleil, des nuages et des gouttes en pictogrammes sur un ciel pâle.

**Verdict : on les distingue en moins d'une seconde**, à condition que **la silhouette de la carte se voie**. Le code du
bulletin télé est immédiat : fond bleu ciel, terre verte, pastilles de température rondes. Le seul danger est interne : avec
**terre `#DCEFC8` sur mer `#CFE6F5` = 1,06:1**, la France ne se détache de la mer que par la teinte, deux pastels de même
luminance. Sur un téléphone compressé, on voit alors un fond bleu-vert uni avec des ronds, ce qui rappelle swiss-data (fond
clair et chiffres). **Correctif** : terre `#BFE3A0` ou plus soutenue (≥ 1,25:1 contre la mer) **et** un trait de côte
`#3E5A72` de 3 px. Les pictogrammes restent plats et sans visage, pour s'éloigner de pastel-diorama.

### 2.2 Règles
- Le genre du bulletin météo est générique. Les symboles de front (triangles bleus pour le froid, demi-cercles rouges pour le
  chaud) sont la **convention météorologique standard** : ce n'est pas une œuvre. Le repérage interdit déjà le logo Météo-France,
  l'habillage de chaîne et le présentateur. J'ajoute : pas de carte en relief ombré « façon TF1 ou France 2 », pas de jingle
  imitant un indicatif connu.
- **Licence GSAP** : DrawSVG et MotionPath sont gratuits depuis GSAP 3.13, mais sous la licence propre de GSAP, **qui n'est pas
  une licence open-source au sens strict**. Le cœur GSAP sert déjà dans 8 identités : c'est un précédent accepté, pas un
  blocage. MotionPath n'est même pas nécessaire : poser les symboles le long du front avec `getPointAtLength` ou d3 coûte quelques
  lignes.
- **Faits** :
  - le record de 46,0 °C à Vérargues le 28/06/2019 est exact ;
  - le solstice du 21/12/2026 est exact, et **J-46 l'est aujourd'hui (5/11)**. Ce titre est périssable : le compte change chaque
    jour. Le format « J-N » est déjà pris par riso-zine (« Géminides J-39 ») et swiss-data (« J-272 éclipse »). C'est permis,
    mais cela n'élargit rien ;
  - Nice contre Paris : l'ordre de grandeur est correct (Paris-Montsouris ≈ 640 mm, ≈ 110 jours de pluie ≥ 1 mm ; Nice
    ≈ 60 jours). Le repérage demande à juste titre de vérifier sur les normales 1991–2020 avant publication ;
  - mistral : correct (vent de nord à nord-ouest, effet de couloir entre les Alpes et le Massif central, rafales > 100 km/h).
  - Aucun sujet n'est déjà dans `out/shorts`.

### 2.3 Assets — `world-atlas` : librairie ou asset ?
**Mon avis : c'est un asset de données. Il faut l'admettre, sous une règle écrite.**
- Sur le fond, ce n'est **pas du code** : c'est de la géométrie que personne n'a générée par code. Dire que « c'est un paquet
  npm donc une librairie », c'est jouer sur les mots.
- Mais la règle « aucun asset téléchargé » a déjà une interprétation de fait. Les **23 polices @fontsource** sont des fichiers
  binaires (`.woff2`), non générés, récupérés par `npm i` et épinglés dans `package.json`. Le dépôt contient en plus
  `out/shared/papier-moteur/assets/` (polices, musique, bruitages, logos) importé avec la famille papier. La règle réelle est
  donc : *pas de téléchargement ponctuel, non versionné ou au moment du rendu, et pas d'œuvre graphique d'un tiers*. Elle n'est
  pas « zéro octet non généré ».
- Ce qu'apporte `world-atlas` : des données **factuelles** (la forme réelle des côtes), du **domaine public** (Natural Earth)
  sous paquet ISC, **versionnées et reproductibles**. Ce n'est pas une illustration, et le style visible (aplats, couleurs,
  trait, symboles) reste généré par code.
- Ce que coûte le refus : atlas-grave a tracé ses côtes à la main et l'a payé. Son défaut accepté dans `failures.md` est
  « côtes simplifiées à la main → grossières au-delà de ×2,5 de zoom ». Et pour une identité géographie, une côte fausse est
  presque une **erreur de fait**, ce que le brief interdit (« ne pas affirmer de faits faux »). Refuser la donnée publique
  dégrade la justesse au nom d'une pureté que les polices ne respectent déjà pas.

**Règle proposée, à écrire dans `STUDIO_BRIEF.md` ou `AGENTS.md`** :
> Données factuelles admises : géométries, mesures et tables publiées sous licence domaine public, CC0, CC-BY (crédit noté) ou
> licence de paquet permissive (MIT, ISC, OFL pour les polices), **distribuées par un registre de paquets (npm, PyPI) à version
> exacte épinglée** (`"world-atlas": "2.0.2"`, sans `^`), installées par `npm i` ou `pip`, **jamais chargées par le réseau au
> rendu**. La source, la licence et la version sont notées dans `identity.md` (Librairies) et dans une fiche
> `out/library-cards/<paquet>.json`. Sont exclus : images, icônes, illustrations, textures, cartes stylisées, sons et tout
> contenu dont l'apparence est l'œuvre d'un tiers. Les données n'apportent que la forme du réel, le style reste généré par code.

Détails pour le studio : `countries-50m.json` (pas de 10m dans world-atlas). Le MultiPolygon « France » contient les DROM : il
faut **filtrer la Guyane et les îles** avant `fitExtent`. On projette **une découpe européenne précalculée** et non le monde
entier à chaque image.

### 2.4 Faisabilité
Elle repose sur des briques « Oui » maîtrisées : d3-geo (swiss-data, atlas-grave, topo-relief), GSAP seek, canvas 2D.
- topojson-client (« Non ») n'est qu'un **décodeur de 2 fonctions** (`feature`, `mesh`). Il ne porte pas la signature : c'est la
  donnée qui la porte, avec d3. Ce n'est pas grave, mais la direction n'apporte pas vraiment de librairie nouvelle.
- **Le vent** : une intégration séquentielle depuis t = 0 (`SEQUENTIAL`) casse l'accès direct aux stills et allonge chaque
  série de stills. **Correctif imposé** : précalculer les trajectoires en Node et les rejouer (la leçon de pixel-arcade sur
  `Math.atan2` : le navigateur ne fait que lire), ou utiliser des trajectoires analytiques (point de départ tiré par la graine +
  écoulement le long d'une ligne de courant fixe).
- `d3.contours` à chaque image sur 128×228 est faisable : quelques dizaines de ms, mesuré à 224 ms en 256² dans `facts.md`.
- Seek de DrawSVG avec `tl.seek(t, false)` : compatible, avec le piège connu `immediateRender:false`.

### 2.5 Coût
Le repérage annonce ≈ 15 au repos et 30–45 en charge, sans l'avoir mesuré. C'est **crédible** : swiss-data (D3 SVG + GSAP)
mesure 13,7–20,5 en charge, et la capture (≈ 0,3 s par image en charge) domine. Le contre-modèle est atlas-grave à 129–136 :
même famille d3-geo, mais filtres et PNG lourds. **Conditions** : aucun filtre SVG plein cadre, pas de projection du monde
entier à chaque image, dégradés et nuages en PNG précalculés (pycairo). Le premier still doit fournir une mesure.

### 2.6 Public et familles
Public : adults puis teens. Familles : geographie (4 → 5) et evenements (5 → 6, la famille la plus encombrée après
histoire et explicatif). L'élargissement est moyen, **mais c'est la seule géographie claire et froide**, puisque les 4
existantes sont crème, parchemin ou vert sombre. Débit adulte de 2,4–2,8 mots/s : compatible avec des pastilles chiffrées et des
bandeaux de ≤ 8 mots. Tailles : chiffres 72–110 px et villes 54 px. **Les noms de villes à 54 px doivent être sur un cartouche
blanc**, jamais directement sur la terre ou la mer.

### 2.7 Photosensibilité et lisibilité
Pas d'éclair plein cadre. La règle du repérage (éclair local ≤ 10 % du cadre et ≤ 3 par seconde) est bonne. Le passage du front
en 0,9 s n'inverse pas la luminance : on passe d'une carte pastel à une carte pastel.
Contrastes : texte bleu nuit 11,92 / 12,6 / 15,37:1 ; rouge sur blanc 4,67:1 ; bleu sur blanc 5,73:1.
**Contrastes oubliés** :
- **terre/mer 1,06:1** (à corriger, voir §2.1) ;
- **isobares blanches sur mer 1,29:1, sur terre 1,22:1**. Elles sont **invisibles sur téléphone**, et la promesse « les
  isobares ondulent » est donc creuse. Il faut des isobares `#FFFFFF` à 5–6 px **avec un liseré** `#9CC3DE`, ou bleu moyen
  `#7FA9C9` sur la mer ;
- le front bleu `#1F5FD6` sur la mer descend à **4,44:1** et le front rouge sur la mer à **3,62:1**. C'est acceptable pour des
  formes, pas pour du texte ;
- les traînées de vent n'ont pas de couleur définie. Sur un fond pâle, il les faut sombres et translucides (`#10263D` à 25 %),
  pas blanches.

### 2.8 Polices
Outfit et Atkinson Hyperlegible, deux nouvelles : c'est une de trop. La signature repose sur **les chiffres des pastilles** :
**on garde Atkinson Hyperlegible**, en 700 pour les titres en bandeau comme pour les chiffres, et en 400 ou 700 pour le corps.
Elle n'a pas de graisse 800, mais son 700 à 96–120 px suffit, et l'esprit « lisibilité de service public » colle au
bulletin. **On retire Outfit** : aucune police installée n'est indispensable pour les titres, et Inter est à éviter parce qu'il
signe swiss-data.

### 2.9 Verdict : **MODIFIER** (recommandée)
Correctifs : contraste terre/mer ≥ 1,25:1 et trait de côte ; isobares visibles ; vent précalculé ou analytique ; règle
`world-atlas` adoptée par l'orchestrateur, avec version exacte et filtrage des DROM ; une seule police (Atkinson
Hyperlegible) ; pictogrammes plats sans visage ; pas de « J-N » comme sujet de preuve, au profit d'un sujet non périssable.
Promesse en 1 s : oui, le bulletin météo se reconnaît instantanément, **à condition que la carte se voie**.

---

## 3. `tableau-depart` — Tableau des départs

### 3.1 Confusion
- **brut-meme** : « black / #FFE600 yellow / red only », « Anton auto-fitted to fill the frame », « hard cuts on the beat with
  3-frame punch-in », « round stickers and hazard-stripe progress bar ».
- **pixel-arcade** : « dark navy pixel playfield, motion quantised to 4 px », « Press Start 2P HUD (score, time) »…
- **gazette-1900** : « broadsheet front page that spins in and lands »…
- **Voisine omise par le repérage : cosmos-doc** (« Bebas Neue capitals with tracking that tightens » sur noir) : des capitales
  condensées claires sur un fond très sombre.

**Verdict : on les distingue en mouvement, pas sur une image fixe.** En mouvement, la bascule de palettes est unique et se
reconnaît en 1 s. Sur une vignette, ou sur la planche-contact de brut-meme que j'ai regardée (l'écran « EN 15 SECONDES » :
lignes dans des cases noires, chiffres jaunes, libellés blancs condensés), on voit la même chose : fond quasi noir,
capitales condensées blanches, accent jaune-ambre. **La palette `#2B2F36` sur le boîtier `#1B1E23` ne fait que 1,24:1** :
la grille de cellules, censée être l'élément distinctif, **disparaît** dans la compression. Correctifs : palettes `#3A4049`
ou plus claires, fente de charnière nette, joints de 4 px plus sombres que le boîtier, et **l'ambre ne domine jamais**
(statut ponctuel, jamais un mot entier en ambre).

### 3.2 Règles
- L'afficheur à palettes est un **mécanisme générique**. « Solari » est un nom de fabricant : il ne doit apparaître ni dans le
  nom de l'identité ni dans les textes. Le repérage s'y tient (« Tableau des départs »).
- On ne copie ni la charte d'un opérateur ni d'une gare réelle : pas de jaune sur noir ou bleu « SNCF », pas de pictogrammes
  d'opérateur, pas de logo. Le repérage le dit déjà. **« TGV » est une marque déposée de la SNCF** : le citer comme fait
  historique (usage nominatif) est admis. Il faut écrire « TGV » dans une cellule comme du texte, **jamais dans sa typographie
  ou son logo**.
- **Faits** :
  - premier service commercial le 27/09/1981 Paris → Lyon, record d'essai de 380 km/h le 26/02/1981, 2 h 40 puis 2 h en 1983 :
    exact ;
  - Halley : périhélie le 9/02/1986, prochain le 28/07/2061, période ≈ 76 ans : exact ;
  - latitudes de Reykjavik, Helsinki et Oslo : exactes ;
  - tunnels : Manche 50,5 km, Seikan 53,9 km, Gothard 57,1 km (2016). C'est exact pour les **tunnels de grande ligne**.
    Certains tunnels de métro sont plus longs : il faut le préciser (« le plus long tunnel ferroviaire de grande ligne »), et
    le Brenner (≈ 64 km, en construction) le dépassera.
  - Aucun sujet n'est déjà dans `out/shorts` (cosmos-doc a traité Voyager et Vénus, pas Halley).

### 3.3 Assets
Rien à télécharger. Les clacs viennent de `sound.py` (`click`).

### 3.4 Faisabilité
**WAAPI est déterministe sous SwiftShader (E2 : md5 identiques, au milieu d'une bascule comme aux arrêts).** L'affirmation du
repérage tient. Deux nuances :
- **le piège `fill:'both'` est incomplet** dans le repérage. Si l'on empile un volet par bascule (6 × 2 par cellule), les
  volets **futurs** sont visibles avant leur `delay`, parce que `fill:'both'` applique aussi leur état initial (E2 : caractère
  suivant visible trop tôt). Il faut **4 éléments par cellule** (haut fixe, bas fixe, volet haut, volet bas), dont le texte et
  l'angle sont **calculés comme fonction pure de t** ;
- dans ce cas, **WAAPI n'est plus nécessaire** : une boucle JS de 99 cellules fait la même chose. La librairie « Non » ne porte
  pas vraiment la signature, c'est le mécanisme qui la porte. Ce n'est pas bloquant, mais il ne faut pas compter la direction
  comme une preuve d'adoption de WAAPI.

Il y a aussi un **conflit avec le hook < 1 s**. Une cascade complète (2 à 8 caractères intermédiaires × 95 ms, plus 11
colonnes × 35 ms, plus 9 lignes × 60 ms) dure ≈ 1,5 à 1,8 s. Pendant ce temps, le texte est illisible **par construction**. Le
premier mot lisible arrive donc après 1 s. Correctif : la ligne d'accroche est **déjà affichée** à t = 0, ou la première
cascade se limite à 1 ou 2 caractères intermédiaires.

**Largeur** : 11 colonnes de 76 px plus 10 joints de 6 px font 896 px. La zone utile (1080 − 72 − 120) est de **888 px**. Il
faut des joints de 4 px au plus, ou des cellules de 74 px.

### 3.5 Coût
Le repérage annonce 12,1 au repos (mesuré en JPEG) et 25–40 en charge : c'est **crédible**. Mon E2 en PNG sans perte donne 25,6
au repos : le PNG est plus cher, et cela ne contredit pas le chiffre JPEG. C'est la direction la plus sûre en coût après
trait-continu.

### 3.6 Public et familles
Public : teens et adults. Familles : evenements (5 → 6) et engagement (5 → 6). **C'est le plus faible élargissement des
quatre** : ce sont les deux familles les plus servies après histoire et explicatif, et il y a déjà 3 identités sombres en
engagement ou événements (pixel-arcade, brut-meme, cosmos-doc). 11 caractères par ligne et 2–3 s par temps conviennent aux
teens. Titres de 96–110 px : conforme.

### 3.7 Photosensibilité et lisibilité
**Le risque de flash est faible, et mesuré (E3)** : l'écart de luminance sur un bloc de 25 % du cadre est de 0,093 en 2,5 s,
sous le seuil de 0,10, et de 0,0076 d'une image à l'autre. Les règles du repérage restent nécessaires et sont à durcir :
- aucune bascule de tout le tableau à moins de 1,6 s d'intervalle ;
- **aucune transition du vide au texte sur plus de la moitié du tableau en même temps** : c'est le seul cas où le seuil
  pourrait être franchi, puisqu'une cellule vide qui reçoit un glyphe varie de ≈ 0,2 en luminance ;
- le voyant de statut s'allume une fois en 0,15 s et ne clignote jamais.

Pas de motif rayé à risque : la fente de charnière est sombre sur sombre.
Contrastes vérifiés : texte 11,9:1 et 10,46:1 sur la moitié haute ; ambre 7,35:1 ; vert 7,53:1 ; corail 4,81:1 ; secondaire
6,27:1. **Le seul défaut est palette/boîtier à 1,24:1** (§3.1).

### 3.8 Polices
Barlow Condensed porte la signature (un caractère par palette) : **on la garde**. **Barlow est à retirer** : les en-têtes de
colonnes et la légende passent en Barlow Condensed 500–600. Bebas Neue (installée) est à éviter : elle signe cosmos-doc.

### 3.9 Verdict : **MODIFIER**, en réserve
Correctifs : grille contrastée (palette ≥ 1,6:1 contre le boîtier) ; ambre minoritaire ; 4 éléments par cellule pilotés par t ;
hook déjà lisible à t = 0 ; joints ≤ 4 px ; une seule police ; règle « jamais plus de 50 % du tableau du vide au texte à la
fois ». Mécanique forte et faisable, mais c'est un dixième fond sombre et un élargissement minimal des familles.

---

## 4. `domino-cascade` — Réaction en chaîne

### 4.1 Confusion
- **pastel-diorama** : « pink pastel toy diorama on a felt base », « soft rounded toys and invented recurring characters »,
  « Baloo 2 titles and pill labels », « bouncy back.out motion ».
- **bauhaus-kinetic** : « cream ground with red / yellow / blue / black primary shapes », « Unbounded 800 headlines »…
- **liquid-chrome** : « chrome / iridescent liquid matter in one continuous macro shot »… ; **pixel-arcade** : « real
  pre-simulated physics with photo finish »…

**Verdict : on les distingue en mouvement, en 1 à 2 s.** Le lilas `#E8E2F4` et le rose de pastel-diorama `#FFE8EF` sont deux
pastels très clairs de luminance voisine, dans une 3D douce à ombres portées : sur une vignette, l'ambiance générale se
ressemble. Ce sont les rangées de dominos qui distinguent, pas le fond. La palette sarcelle, corail et encre écarte bien
bauhaus-kinetic. Le registre « satisfying physique » est déjà occupé par deux identités sombres. Domino-cascade en serait la
première version claire, ce qui est un vrai plus.

### 4.2 Règles
Aucun personnage, logo ni œuvre. Dominos génériques. **Faits** : le résultat de Whitehead (*Am. J. Phys.*, 1983), où chaque
domino peut en renverser un ≈ 1,5 fois plus grand, est exact. 1,5⁹ ≈ 38,4, donc 5 cm × 38,4 ≈ 1,92 m : exact. Aucun sujet
n'est déjà dans `out/shorts`. Le sujet 3 (« combien resteront debout ») est honnête seulement si le compteur lit la vraie
simulation, ce qui est prévu.

### 4.3 Assets
Rien à télécharger. Rapier est une librairie (WASM) et pas un asset. Elle est absente de `node_modules` : il faut une ligne
`package.json` à version exacte (`0.21.0`), à valider.

### 4.4 Faisabilité
- **Rapier pré-simulé en Node puis rejoué** : l'architecture est saine. C'est celle de pixel-arcade, et le navigateur ne simule
  jamais. Je ne l'ai pas re-testé : je prends le « même hash sur deux exécutions » du repérage. Il faut préférer
  `@dimforge/rapier3d-deterministic-compat` 0.21.0 si la simulation doit pouvoir se refaire sur une autre machine (le Mac du
  studio).
- **La signature n'est pas prouvée.** Le mot écrit par les faces tombées demande ≈ 1 000 dominos disposés pour que **chacun
  tombe du bon côté**. L'essai brut n'en fait tomber que 231 sur 300. Concevoir un champ qui écrit un mot lisible en vue
  plongeante de trois quarts est un vrai travail de level design, qui n'existe dans aucun short du dépôt. C'est le risque n° 1,
  devant le coût.
- Le texte en calque HTML est correct.

### 4.5 Coût
- Le repérage annonce 44 au repos (mesuré) et 65–90 en charge. Mon essai E4 confirme le repos : **38,9 pour 320 dominos et 42,8
  pour 1 000**. Mais **la conversion vers la charge est sous-estimée** : `facts.md` donne ×2 à 3 entre la charge et le calme,
  pas ×1,5 à 2. On arrive donc à **85–130 s/100 en charge**.
- **Le levier annoncé est faux** : ombre 1024 = −2 % (E4), pas −20 %. Le coût est celui du remplissage SwiftShader en
  1080×1920. Les vrais leviers sont un champ caméra plus serré (moins de sol ombré), une ombre de contact précalculée en
  texture une fois les dominos à terre, ou pas d'antialias MSAA. Aucun n'a été mesuré.
- **Est-ce acceptable pour 2 shorts de 15 s en parallèle d'un autre studio sur 4 cœurs ?** Oui en budget : 900 images à ≈ 0,4 à
  0,6 s l'image, si deux rendus seulement se partagent la machine (contention plus faible que les 10 studios de la campagne),
  font ≈ 6 à 9 min de rendu final. C'est sous cosmos-doc (175–186) et topo-relief (108–169). SwiftShader étant multithread, il
  ralentira l'autre studio. **Le coût n'est pas éliminatoire. Ce qui l'est, c'est le coût multiplié par les itérations** : une
  signature non prouvée (le champ qui écrit un mot) demandera plusieurs séries de stills et probablement plus d'un rendu
  complet.

### 4.6 Public et familles
« kids, teens, adults » : **pas de décision de public**. Le débit, la taille des textes et la voix ne sont pas fixés. Il faut en
choisir un : **teens** (pari, 2,6–3,0 mots/s). Familles : abstrait (3 → 4) et engagement (5 → 6). L'élargissement est bon côté
abstrait, qui n'a que des identités sombres. Le sujet 1, « aucun texte après le hook », est parfait pour l'abstrait et laisse
toute la place à la voix.

### 4.7 Photosensibilité et lisibilité
Le repérage écrit « rien à signaler ». **Je ne suis pas d'accord.** Pas de flash : chaque domino change une seule fois, de
l'ivoire à la face colorée, sans aller-retour. Mais **un champ de rangées régulières à fort contraste** (tranche ivoire et
ombre portée, faces encre `#2B1E4A` et ivoire = 14,44:1) qui couvre plus de 25 % du cadre et **défile sous une caméra en
travelling**, c'est un **motif rayé en mouvement**. Les critères de motif d'Ofcom et du test de Harding le visent. Sur mon
still E4, les rangées forment justement des bandes alternées. S'y ajoute le scintillement possible des ombres fines (aliasing
d'ombre en mouvement). Correctifs : espacement irrégulier ou en courbes (spirales, serpentins), pas de grille rectiligne
plein cadre pendant un travelling, ombre douce, et un contrôle des stills en mouvement.
Contrastes : texte encre 11,98:1 et 14,44:1 ; secondaire 5,86:1. Sarcelle sur lilas 3,37:1 et corail sur lilas 2,85:1 :
décoratifs, ce que le repérage dit. **Ivoire sur lilas 1,21:1** : les dominos debout ne se détachent du sol que par leurs
ombres.

### 4.8 Polices
Bricolage Grotesque porte la carte de titre : **on la garde**. **Azeret Mono est à retirer** : les compteurs passent en IBM
Plex Mono (installée, utilisée seulement pour les dépêches de gazette-1900) ou en chiffres tabulaires de Bricolage, à vérifier
(`font-variant-numeric: tabular-nums`).

### 4.9 Verdict : **ÉCARTER** (pour cette série)
Raisons : la signature (le mot écrit par les dominos) n'est pas prouvée et coûte cher à itérer ; le coût en charge est
sous-estimé (85–130 et non 65–90) et le levier annoncé est faux ; il y a un risque de motif rayé que le repérage n'a pas vu ;
il n'y a pas de public décidé. À revoir plus tard avec un still qui prouve le mot lisible à 1 000 dominos et une mesure en
charge.
Promesse en 1 s : creuse au début. À 1 s, on voit une pichenette et quelques dominos. La « vague révélatrice » n'existe qu'à
la fin de la chaîne.

---

## Classement (mon jugement)

| Rang | Direction | Distinctivité | Règles | Faisabilité | Coût | Verdict |
|---|---|---|---|---|---|---|
| 1 | `carte-meteo` | bonne (code de genre neuf, seule géographie claire et froide), sous réserve du contraste terre/mer | propres, sous réserve de la règle sur les données | sûre : briques « Oui » (d3-geo, GSAP) | 15 au repos, 30–45 en charge, crédible | MODIFIER |
| 2 | `trait-continu` | la meilleure des 4, à reconfirmer après la refonte de l'objet | **non conforme** en l'état (habillage Etch A Sketch) | prouvée sans skia (E1) | la moins chère : 3,9 au repos | MODIFIER |
| 3 | `tableau-depart` | forte en mouvement, faible en vignette (dixième fond sombre, proche de brut-meme) | propre | prouvée (E2), deux pièges à corriger | 12 au repos | MODIFIER, en réserve |
| 4 | `domino-cascade` | bonne (premier abstrait clair) | propre | signature non prouvée | 39–43 au repos, 85–130 en charge | ÉCARTER |

Je place carte-meteo devant trait-continu, à l'inverse du repérage, pour une seule raison : **trait-continu doit changer
d'objet**, et sa distinctivité après la refonte n'est pas encore prouvée. carte-meteo n'a besoin que de réglages. **Je
recommande quand même de produire les deux.** Si le premier still du traceur n'est pas convaincant (on n'y lit pas « un seul
trait, deux axes » en 1 s), tableau-depart le remplace.

## Correctifs obligatoires pour les 2 directions recommandées

**`carte-meteo`**
1. Terre et mer à ≥ 1,25:1 (par exemple terre `#BFE3A0`) plus un trait de côte `#3E5A72` de 3 px.
2. Isobares visibles : blanc 5–6 px avec liseré `#9CC3DE`, ou `#7FA9C9`. Traînées de vent sombres et translucides.
3. Vent précalculé en Node puis rejoué, ou trajectoires analytiques. Pas de `SEQUENTIAL`.
4. `world-atlas` à **version exacte `2.0.2`**, une fois la règle adoptée. DROM filtrés. Découpe européenne précalculée.
   Licence et source dans `identity.md` et dans une fiche librairie.
5. Une seule nouvelle police : **Atkinson Hyperlegible**. Pas d'Outfit.
6. Pictogrammes plats et sans visage. Aucun habillage de chaîne. Textes de ≤ 54 px toujours sur cartouche blanc.
7. Sujets de preuve non périssables (Nice/Paris, mistral, record de 2019). « J-46 » est à éviter ou à recalculer le jour du rendu.
8. Pas de filtre SVG plein cadre. Coût mesuré dès le premier still.

**`trait-continu`**
1. **Abandon de l'objet jouet** : ni cadre à coins arrondis autour d'un écran gris, ni deux molettes, ni secousse, ni nom ou
   allusion de produit, ni argument de nostalgie. On passe au **traceur** : fond orange plein cadre, plaque aluminium à angles
   vifs, deux règles à curseurs pour les axes, transition « avance plaque » en crans verticaux.
2. Escalier de **12 px au minimum** et trait de 6 à 8 px, sinon on supprime l'escalier.
3. Grain et masque de bruit calculés **une fois** et mis en cache. Jamais d'opensimplex plein champ à chaque image.
4. Aucune police nouvelle (Fredoka partout). Ni crème ni blanc sur l'orange principal.
5. Narration ≤ 33 mots pour 15 s (kids à 2,0–2,3 mots/s). Hexagone : nommer les familles de côtés, pas les 6.
6. shapely 2.2.0 et opensimplex 0.4.5.1 **préinstallés par l'orchestrateur** dans `.venv`, puisque les studios n'installent
   rien.
7. Premier still à t ≈ 4 s : plaque, deux curseurs, chariot et dessin à moitié tracé reconnaissable, plus la paire de stills de
   l'avance plaque.

## Décisions laissées à l'orchestrateur

1. **Règle sur les données factuelles** (§2.3) : l'adopter, ou la refuser et imposer le tracé à la main avec le défaut
   d'atlas-grave. Je recommande de l'adopter et de l'écrire dans `STUDIO_BRIEF.md` et `AGENTS.md`.
2. **Polices** : je propose au plus une nouvelle police par identité, donc **une seule pour les deux directions recommandées**
   (Atkinson Hyperlegible pour carte-meteo, aucune pour trait-continu), au lieu des 7 proposées. Barlow Condensed seulement si
   tableau-depart est produite. Pas de Lexend, d'Outfit, de Barlow ni d'Azeret Mono.
3. **Nouvelles dépendances à préinstaller** : `world-atlas@2.0.2` (npm) et `shapely`, `opensimplex` (PyPI), à versions
   exactes. Rapier seulement si domino-cascade revient.
4. **La variante « traceur » de trait-continu** : la valider telle quelle, ou en choisir une autre. Une variante acceptable doit
   garder un trait unique et un effacement total, sans cadre à molettes, sans écran gris encadré et sans secousse.
5. **La contrainte « une Python et une JavaScript »** du repérage : ce n'est pas une règle du brief. La garder ou non décide du
   remplaçant si trait-continu échoue au premier still (tableau-depart est en JavaScript).
6. **Licence GSAP** : les plugins DrawSVG et MotionPath sont gratuits mais pas open-source au sens strict. L'accepter comme
   pour le cœur GSAP, ou imposer d3 avec `getPointAtLength` (ma préférence, c'est plus simple).
7. **Statut des assets de `out/shared/papier-moteur/assets/`** (musique, bruitages, logos tiers) : ils contredisent déjà la
   lettre de la règle « aucun asset téléchargé ». Il faut l'écrire clairement pour que la règle des données ne paraisse pas
   arbitraire.
8. Mise à jour d'en-tête relevée par le repérage : `catalogue.md` parle encore de « 14 identités (31 shorts) ».
