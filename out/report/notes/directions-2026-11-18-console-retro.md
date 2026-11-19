# Direction d'identité « survol pixel » (ex-console-retro), repérage du 2026-11-18

Étape de repérage du skill `fabrique-identites`, pour N = 1 identité. Ce document ne contient ni code de scène ni rendu
dans le dépôt, et rien n'a été commité. Trois essais techniques ont tourné hors du dépôt, dans le scratchpad de la session :
- la grille de dessin des polices pixel, mesurée avec fontTools sur les `.woff` @fontsource 5.3.0 téléchargés depuis le registre npm ;
- une planche de lisibilité rendue avec PIL sans anticrénelage ;
- un prototype Mode 7 en numpy (§ 5.4).

Sources lues :
- le brief `brief-2026-11-18-console-retro.md` ;
- l'analyse `console-retro-analyse.md` et les images de `console-retro-source/` ;
- `index.json` (pixel-arcade, carte-meteo, topo-relief, trait-continu) et les planches-contacts des trois voisines ;
- `facts.md`, `sound.py` et les `short.json` de pixel-arcade.

**Précision du propriétaire (18/11, intégrée partout).** On copie la **forme** de la source : pixel art en 3D, grille de gros
pixels, palette indexée, sol en perspective Mode 7, terrasses, couches empilées avec ombres portées, caméra continue.
On ne copie **pas son contenu**. L'identité sert des vidéos **didactiques, pour enfants, d'histoire et d'explication**,
avec narration. Elle n'est réservée ni au jeu vidéo ni à l'aviation :
- l'avion et le cockpit ne sont plus obligatoires : **c'est la caméra qui vole** ;
- le HUD devient un cadre facultatif pour des chiffres, des dates et des titres ;
- les deux shorts de preuve ne parlent ni de jeu ni d'avion, et n'appartiennent pas à la famille `engagement`.

---

## 1. Nom, slug, promesse

- **Slug proposé : `survol-pixel`**, et non `console-retro`.
  - « console-retro » annonce un contenu de jeu vidéo, alors que le propriétaire veut une forme qui serve l'histoire, la
    science et les enfants.
  - Le slug nomme ce qui reste constant d'un sujet à l'autre : **un survol**, rendu **en gros pixels**.
  - Il est en français, en kebab-case, comme `carte-meteo`, `trait-continu` ou `topo-relief`.
  - Le nom de travail « console-retro » reste dans les fichiers de notes (`brief-…`, `console-retro-analyse.md`) pour la provenance.
- **Nom affiché : Survol pixel**.
- **Promesse (fr)** : « Chaque sujet devient un petit monde en pixel art 16 bits que la caméra survole, puis frôle jusqu'à
  l'horizon : la profondeur d'une console des années 90 au service d'une histoire racontée. »
- **Promise (en, pour `index.json`)** : "Every topic becomes a small 16-bit pixel-art world the camera flies over, then
  dives toward the horizon: early-90s console depth (Mode-7 ground, terraced relief, layered drop shadows) in service of a
  narrated story."
- **Public** : enfants 6–10, ados, adultes, selon le rythme du § 6.4.
- **Statut : une nouvelle identité, pas une dérivation de `pixel-arcade`.** La règle d'`AGENTS.md` réserve la dérivation à
  une identité qui réutilise le même moteur et ne change que le fond, la palette et les polices. Ici, tout diffère :
  - **le moteur** : Python numpy + Pillow image par image, contre Matter.js + p5 + PixiJS dans le navigateur ;
  - **l'espace** : un monde en perspective avec horizon, contre un terrain de jeu plat vu de face ;
  - **la grille** : une seule grille de 270×480 pour toute la scène, contre un mouvement quantifié à 4 px ;
  - **la transition signature** : le piqué de caméra, contre la mosaïque de pixels ;
  - **les polices** : la famille Jersey, contre Press Start 2P et Rubik Mono One ;
  - **la mécanique** : survol et récit, contre pari sur une course physique.

## 2. Signature en 4 traits (`curation.signatureToPreserve`)

1. **Une seule grille de gros pixels et une palette indexée.**
   - Toute l'image (sol, nuages, objets, texte, cadres) est dessinée à 270×480 puis agrandie ×4 au plus proche voisin.
   - La palette fixe est complétée par 3 couleurs « biome » choisies pour l'épisode (§ 3).
   - Pas de tramage global, pas de scanlines, pas de CRT, pas de grain : du 16 bits propre.
2. **La profondeur 3D est obligatoire (règle du propriétaire).**
   - Chaque plan montre **au moins 2 indices de profondeur** parmi : sol en perspective vers un horizon (Mode 7), relief en
     terrasses à bord sombre, couches en parallaxe (sol, nuages, objets), ombres portées décalées en aplat sombre.
   - **Aucun plan aérien ne reste fixe plus de 4 s** : la carte défile, ou la caméra pique.
   - Un rendu 2D plat est interdit.
   - Le ciel est en paliers plats, et une brume quantifiée efface les lointains.
3. **La caméra vole, sans coupe.**
   - On passe de la vue de dessus à la vue rasante, et inversement, par **le piqué** : une bascule continue de pitch
     (90° ↔ 15°) en 0,4–0,6 s.
   - Il n'y a jamais de coupe franche ni de fondu entre deux vues.
   - Avion, cockpit et HUD sont **facultatifs**.
4. **Le texte vit dans des cartouches de dialogue crème qui projettent leur ombre.**
   - Les polices sont la famille **Jersey** (10/15/20), dessinées au pixel près sans anticrénelage.
   - Le texte est encre marine sur crème, dans un cadre de 1 gros pixel.
   - Chaque cartouche porte une **ombre portée plate** décalée de 2 gros pixels : même règle que les nuages.
   - Les chiffres facultatifs s'affichent en vert phosphore sur une plaque sombre.

`confusableWith` proposé : `["carte-meteo", "pixel-arcade", "topo-relief"]`.

## 3. Palette

Elle est tirée de la palette **mesurée** de la source (k-means, `console-retro-analyse.md` § 3.2), puis rendue nôtre :
- l'océan est poussé plus profond et plus saturé ;
- le ciel finit en **brume dorée** au lieu de bleu pâle, pour s'écarter de la mer de carte-meteo (`#CFE6F5`) ;
- des emplacements de biome permettent de sortir de l'île tropicale.

### 3.1 Noyau fixe (toujours présent, 17 couleurs)

| Rôle | Hex | Source mesurée |
|---|---|---|
| **bg = océan profond** (> 45 % des pixels en vue de dessus) | `#1E5AA8` | `#2a68b0` |
| océan moyen | `#2C74BE` | `#317cbf` |
| haut-fond | `#3FA0D0` | `#4ca4d2` |
| lagon | `#7CCBEB` | `#7ec4f0` |
| écume / ressac | `#E6FAFF` | `#d8f6fc` |
| ombre portée sur l'eau | `#143F7E` | `#1a488e` (luminance × 0,7) |
| herbe claire | `#93D94E` | `#8bdc56` |
| herbe moyenne | `#5DB534` | `#66be3b` |
| herbe sombre / courbe de niveau | `#2F7A2A` | `#43902b` |
| forêt / ombre sur la terre | `#174A22` | `#1a5020` |
| nuage | `#FBFDFE` | `#fbfdfe` |
| hachure de nuage | `#AFBBC6` | `#b0bac2` |
| ciel haut / ciel milieu / ciel clair | `#6FB4E3` / `#96CBEB` / `#BFE2F1` | `#9dd1eb` → `#c7e9f7` |
| **brume dorée** (bande d'horizon) | `#EFE2BF` | absente de la source : c'est notre écart |
| **surface = cartouche** | `#FBF3D5` (crème) | absente de la source |
| **texte = encre** (et cadre de cartouche) | `#14213D` | absente de la source |

### 3.2 Emplacements de biome (3 couleurs par épisode, déclarées dans `short.json`)

| Biome | Couleurs | Usage |
|---|---|---|
| tropical | sable `#EBDFA0`, roche `#8A8178`, corail `#E58A7A` | îles, atolls, lagons |
| montagne (Andes, Alpes) | granit `#9C968C`, granit ombre `#5F5A55`, chaume `#C9A35A` | terrasses, cités, cols |
| littoral tempéré | grève `#CDBB8A`, ardoise `#5E6A78`, pierre claire `#D9D2C3` | abbayes, ports, marées |
| désert / antique | ocre `#D9A55B`, terre cuite `#B5572E`, pierre `#E3D3A8` | pyramides, oasis, cités |

Au plus 17 + 3 = 20 couleurs en vue de dessus, comme la source (16 couleurs pour 92 % des pixels).

### 3.3 Accents et états

| Rôle | Hex |
|---|---|
| accent 1, marqueur / repère (pastille, flèche au sol) | `#B5341A` (rouge brique) |
| accent 2, chiffre et date sur plaque HUD | `#FFC94A` (or) |
| accent 3, phosphore HUD (facultatif) | `#7DF5A5` sur plaque `#062A1C` |
| success | `#1F6B2A` |
| danger | `#B5341A` |
| muted (légende secondaire dans le cartouche) | `#5A5F73` |

### 3.4 Brume quantifiée (correctif du prototype)

- **Le mélange continu vers la couleur de brume est interdit** : il crée des couleurs hors palette.
- On précalcule une **table de brume** : pour chaque couleur du noyau et du biome, 2 niveaux intermédiaires vers `#EFE2BF`,
  quantifiés et ajoutés à la palette.
- On l'applique **par bandes de lignes** selon la distance (par exemple 8 lignes par niveau près de l'horizon), comme les
  paliers du ciel.
- Une vue rasante compte au plus ≈ 32 couleurs, la source ≈ 24–32.

### 3.5 Contrastes WCAG (calculés le 18/11, fond réel du texte)

Les polices pixel n'ont **pas de graisse grasse**. L'exception « ≥ 3:1 pour un titre gras ≥ 90 px » ne s'applique donc pas :
**tout texte doit atteindre ≥ 4,5:1**.

| Texte | Fond | Contraste |
|---|---|---|
| encre `#14213D` | cartouche `#FBF3D5` | **14,36:1** |
| rouge `#B5341A` (mot clé) | cartouche | 5,44:1 |
| vert `#1F6B2A` (succès) | cartouche | 5,91:1 |
| bleu océan `#1E5AA8` (mot clé) | cartouche | 6,12:1 |
| muted `#5A5F73` | cartouche | 5,69:1 |
| phosphore `#7DF5A5` | plaque HUD `#062A1C` | 11,42:1 |
| or `#FFC94A` | plaque HUD | 10,11:1 |
| crème `#FBF3D5` | plaque HUD | 13,93:1 |
| crème `#FBF3D5` | océan `#1E5AA8` | 6,12:1 (ok, mais le texte reste en cartouche) |
| crème `#FBF3D5` | cartouche inversé `#14213D` (bandeau de titre) | 14,36:1 |

Interdits :
- **pas de texte posé directement sur la carte** : la carte est trop chargée, le texte va toujours en cartouche ou sur une plaque ;
- pas de texte orange vif (`#E8542A` ne fait que 3,29:1 sur la crème) ;
- pas de texte sur le ciel.

## 4. Typographie

**Famille Jersey** (Sarah Cadigan-Fried, Soft Type Project, OFL-1.1), `@fontsource/jersey-10`, `jersey-15` et `jersey-20`
**5.3.0**. Aucune identité ne l'utilise. Elle n'est pas dans `node_modules` : il faut l'ajouter à `package.json` **avec une
version exacte** (`"5.3.0"`, sans `^`).

### 4.1 Mesures (fontTools sur les `.woff`, planche rendue avec PIL `fontmode = "1"` puis ×4)

| Police | Unités/em | Pas de grille | Px/em natif | Capitale / x natif | Usage | Taille finale (×4) |
|---|---|---|---|---|---|---|
| **Jersey 20** | 1292 | 38 | **34** (entier) | 20 / 15 | accroche, mot géant | corps 136 px, capitale 80 px |
| **Jersey 15** | 1350 | 50 | **27** (entier) | 15 / 11 | titre de cartouche, chiffres HUD | corps 108 px, capitale 60 px |
| **Jersey 10** | 1400 | 75 | **18,667** (non entier) | 10 / 8 | texte courant, légendes | corps 74,7 px, capitale 40 px (≥ 54 px ✓) |

- **Les accents du sous-ensemble `latin` sont complets** : é è ê ë à â î ï ô û ù ü ÿ ç, É È Ê À Â Î Ï Ô Û Ù Ç, œ Œ, « », ’,
  …, —, –, °, €, ×, ÷.
- **Manquent ² ³ ±.** Il faut écrire « km² » en toutes lettres (« kilomètres carrés ») ou dessiner un glyphe ² de 3×4 gros
  pixels à la main dans le moteur.
- **Le sous-ensemble `latin-ext` ne contient pas les accents français** : ne charger que `latin`.
- **Lisibilité** : la planche montre des capitales et bas-de-casse nettes. Jersey est condensée, d'allure sportive ou
  « écran de score », très différente de la Press Start 2P de pixel-arcade, large et à chasse fixe.
- **Lettres par ligne**, sur une largeur utile de 270 − 18 − 30 = 222 px natifs, moins 2 × 4 px de marge intérieure de
  cartouche ≈ 214 px (estimation tirée de la planche, à vérifier par le studio) :
  - Jersey 10 ≈ 6,3 px par caractère, soit **≈ 33 caractères** ;
  - Jersey 15 ≈ 9,4 px, soit **≈ 22 caractères** ;
  - Jersey 20 ≈ 12 px, soit **≈ 17 caractères**.

### 4.2 Polices écartées

| Police | Raison |
|---|---|
| Press Start 2P | celle de pixel-arcade |
| Silkscreen, Tiny5, Micro 5 | 8, 8 et 11 px/em : trop petites à l'échelle 1. À l'échelle 2, leurs pixels font 8 px contre 4 px pour la scène, ce qui casse la grille unique |
| Pixelify Sans, VT323, DotGothic16 | pas de grille propre : pas irréguliers (≈ 90 unités pour Pixelify, demi-pas pour VT323), points ronds pour DotGothic |
| Handjet | modulaire variable, pas une grille carrée |

### 4.3 Dessin du texte

- Le texte est dessiné **à la résolution native**, avec PIL `ImageFont.truetype(<…-latin-400-normal.woff2>, size)`.
  `ImageDraw.fontmode = "1"` coupe l'anticrénelage : seuls deux indices de palette existent, encre et fond.
  PIL lit les `.woff2` (vérifié le 18/11 avec Pillow 13 dans `.venv` : le FreeType embarqué a brotli). fontTools, lui, a
  besoin des `.woff` : brotli n'est pas installé.
- Jersey 15 et Jersey 20 ont un px/em entier : `size = 27` et `size = 34` tombent exactement sur la grille.
- **Jersey 10 (18,667)** a un px/em non entier. Le studio doit choisir l'une de deux solutions :
  - (a) construire un **atlas de glyphes** : rasteriser chaque glyphe à 18,667 avec `fontmode "1"`, vérifier sur une
    image fixe qu'aucun pixel n'est dédoublé ou perdu, et passer à (b) en cas de défaut ;
  - (b) lire les contours par fontTools et remplir les cellules du pas de 75 unités : bitmap exact garanti.
- Le texte n'est jamais déplacé d'une fraction de gros pixel. Il entre par paliers, lettre par lettre : la machine à écrire
  des boîtes de dialogue, ≈ 30 caractères/s.

## 5. Moteur proposé (à vérifier par le studio)

### 5.1 Principes

- **Python seul** (numpy + Pillow, plus opensimplex 0.4.5.1 et shapely 2.2.0 déjà épinglés pour trait-continu), image par
  image, sur le modèle de `trait-continu` (`traceur.py`).
- Une fonction `frame(t) -> np.uint8[480, 270]` produit des **indices de palette**.
- La conversion en RGB se fait par la table de palette, puis l'image est agrandie ×4 avec `repeat(4, 0).repeat(4, 1)`.
  Le facteur 4 est pair, ce qui est compatible avec le sous-échantillonnage de chroma de yuv420p.
- Les images brutes partent en `rgb24` par un tube vers `ffmpeg -c:v libx264 -pix_fmt yuv420p`.
- Déterministe : graines dans `short.json`.

### 5.2 Le monde

- **Monde inventé** :
  - champ de hauteurs opensimplex, plus une forme guidée (cône de volcan, anneau d'atoll, crête andine) ;
  - **quantification en terrasses** : 8–12 niveaux, chaque marche alterne deux verts, son bord aval est tracé d'un trait
    sombre de 1 gros pixel en escalier ;
  - anneaux de hauts-fonds autour des côtes, sable, ressac en pixels épars ;
  - forêts en grappes de boules (3–5 px, reflet en haut à gauche, ombre en bas à droite).
- **Hachures et écume « posées à la main »** :
  - moutons d'écume = traits de 1×2 à 1×4 px semés sur une grille jitterée (≈ 1 pour 12×12) ;
  - leur scintillement est tiré d'une graine et change ≤ 4 fois par seconde ;
  - les nuages ont une hachure horizontale une ligne sur deux sur leur moitié basse.
- **Nuages** : piles de 2–4 lobes circulaires, à **une seule altitude**, avec une **ombre portée en aplat** décalée de
  (≈ −5, +55) gros pixels en vue de dessus.
- **Parallaxe** : la couche de nuages défile plus vite que le sol (facteur ≈ 1,3).

### 5.3 Les vues

- **Vue de dessus** : la carte d'indices (par exemple 1024×1024) défile, le nord reste en haut, ≈ 60–120 gros px/s.
- **Vue rasante (Mode 7)** :
  - projection inverse par ligne en numpy : chaque ligne d'écran sous l'horizon échantillonne la carte à une distance
    `z = alt / (y − y_h)` ;
  - la rotation applique le cap et le roulis ;
  - l'horizon est placé à 30–40 % du haut (ligne native 145–190) : le format vertical demande un horizon plus haut que
    les 41 % de la source ;
  - au-dessus de l'horizon, ciel en 3–4 paliers plats de 16–19 lignes, puis brume dorée par bandes (§ 3.4).
- **Relief qui se lève en perspective** : le Mode 7 plat ne montre les terrasses qu'en texture. Pour un volcan ou une crête
  qui *monte* à l'horizon, le studio teste en priorité un **rendu « voxel space » par colonnes** :
  - pour chacune des 270 colonnes, une marche de 150–250 pas en profondeur, avec y-buffer ;
  - c'est la technique des « bandes empilées » revendiquée par l'auteur de la source, vectorisée en numpy sur les colonnes ;
  - repli : Mode 7 plat, plus le relief en *sprite stacking* (variante B ci-dessous).
- **Bascule (le piqué)** : interpolation du pitch de 90° (projection orthographique de dessus) à 15° (Mode 7). Entre les
  deux, l'horizon remonte du bas de l'écran et le ciel apparaît.
- **Objets, décors, personnages** : billboards (bâtiments, temples, abbaye, personnage guide, arbre), avec deux règles :
  - **dessinés à la main en code** (tableaux ASCII → indices) en **3 tailles** (1, 2/3, 1/3), choisies selon la distance ;
    au-delà, échantillonnage au plus proche voisin **sur la grille native**, donc toujours dans la palette et la grille ;
  - chaque objet a son **ombre portée plate**, avec un décalage propre à sa hauteur : l'ombre encode l'altitude, comme dans
    la source.
- **Schéma explicatif posé au sol** : flèches, coupes et étiquettes sont dessinées *dans la carte d'indices*, et suivent
  donc la perspective. Un exemple : une coupe de terrasse posée comme une maquette sur le terrain. Les chiffres restent en
  cartouche à l'écran.
- **Cartouches** :
  - cadre de 1 px `#14213D`, intérieur crème, coin coupé d'un pixel ;
  - ombre plate de 2 px en `#143F7E` sur l'eau, `#174A22` sur la terre ;
  - entrée par paliers (hauteur 0 → pleine en 4 images) ;
  - placement en bas du tiers haut ou au-dessus de la zone basse, toujours dans les zones sûres.
- **Plaque HUD (facultative)** : rectangle `#062A1C` à cadre `#2F7A2A`, chiffres Jersey 15 en phosphore ou en or. Les
  usages prévus sont l'altitude d'un site, une date ou un compteur d'années. **Pas de tableau de bord de cockpit.**

### 5.4 Zones sûres en pixels natifs

| Côté | Natif | Final |
|---|---|---|
| haut | 55 | 220 px |
| bas | 80 | 320 px |
| droite | 30 | 120 px |
| gauche | 16 | 64 px |

### 5.5 Coût

- **Prototype mesuré** le 18/11 dans le scratchpad, hors dépôt, sur ce Mac (i7 4 cœurs) **chargé : moyenne de charge
  20–35** :
  - carte opensimplex 512² en ≈ 4 s, une seule fois ;
  - **Mode 7 + table de palette + brume + agrandissement ×4 : 2,9 s pour 100 images** ;
  - mesure prise **sans** nuages, sprites, texte ni encodage.
- **Estimation (non mesurée) du short complet : 10–30 s pour 100 images.** La marche voxel et l'encodage x264 dominent.
  C'est du même ordre que trait-continu (4,9) et carte-meteo (18), bien en dessous de topo-relief (108–169).
- **Mesure à faire par le studio** : `time` sur le rendu complet de chaque short, écrit dans `short.json.renderTimeSec`,
  avec la charge (`uptime`) notée dans `renderCostNote`.

## 6. Mouvement, caméra, transition, son

### 6.1 Grammaire

- Un short = **3 à 5 vues de 2,5 à 4 s**, reliées par des mouvements continus de 0,4 à 0,6 s, sans coupe ni fondu.
- Les vues : **dessus** (comprendre la forme), **rasante** (sentir le lieu), **frôlée** (passer au ras d'un objet, nuages
  en parallaxe), retour **dessus** (conclure).
- Le short est bouclable comme la source : la dernière vue rejoint la première.

### 6.2 Transitions

- **Signature, « le piqué »** : pitch 90° → 15° avec easing `inOutSine`, en 0,5 s, avec un léger zoom.
  **« La remontée »** est son inverse.
- **Secondaire, « la traversée du nuage »** : la caméra passe dans la couche de nuages, qui couvre un temps l'écran de
  blanc hachuré, en 0,4 s. Deux règles de photosensibilité :
  - **au plus une par short** ;
  - la luminance monte en ≥ 0,3 s, jamais en un saut.
- **Mosaïque de pixels interdite** : c'est la transition de pixel-arcade.

### 6.3 Mouvement des éléments

- Tout bouge par **pas entiers de gros pixel**. La caméra est en virgule flottante, mais l'échantillonnage tombe sur la
  grille.
- Le roulis de la vue rasante ne dépasse pas 25° : c'est un récit, pas une démonstration de vol.
- Pas de flash, pas de clignotement au-delà de 3 Hz. Le scintillement de l'écume est un changement local et de faible
  amplitude.

### 6.4 Rythme selon le public

| Public | Durée d'une vue | Débit de la voix | Durée du piqué |
|---|---|---|---|
| enfants | 3,5–4 s | 2,2 mots/s | 0,6 s |
| ados et adultes | 2,5–3 s | 2,6 mots/s | 0,4–0,5 s |

### 6.5 Son (`out/tools/sound.py`)

- pixel-arcade utilise le preset `chiptune` et des événements `blip` (111) et `coin` (21) : **à ne pas reprendre**.
- Proposition :
  - preset **`drone`** (bourdon grave = vent et moteur de survol), plus un preset **`pad`** en gamme `lydian` ou `majpent`
    pour la couleur 16 bits douce ;
  - événement **`whoosh`** filtré sur chaque piqué ou remontée ;
  - **`swell`** à l'arrivée d'un lieu ;
  - **`chime`** discret à la révélation finale.
- Pas de bips d'interface. Mix sous la voix (ducking par `tts.py`).
- Si le studio veut une vraie mélodie « carte du monde de console », il peut ajouter un preset `pulse` lent (≤ 0,25 de
  gain), sans `blip` ni `coin`.

## 7. Familles, sujets, shorts recommandés

Familles retenues pour les preuves : **`explicatif`** et **`histoire`**. Elles sont les plus éloignées du jeu vidéo et
prouvent le « n'importe quel sujet » : un phénomène naturel, puis un lieu humain. Aucun titre ci-dessous n'existe dans `out/shorts`.

| Famille | Sujet 1 (**à faire**) | Sujet 2 (réserve) |
|---|---|---|
| explicatif | **« Comment naît un atoll ? »** | « Pourquoi le lagon est-il turquoise et le large bleu foncé ? » |
| histoire | **« Machu Picchu : pourquoi une cité en escaliers ? »** | « Le Mont-Saint-Michel, une île deux fois par jour » |

Règles de faits et de lieux :
- **L'atoll** est un monde inventé : la règle le permet, puisque les faits sont dans le texte.
- **Machu Picchu** et le **Mont-Saint-Michel** sont des **reconstitutions stylisées**, annoncées comme telles dans un
  cartouche ou la description (« reconstitution stylisée »). Aucune géométrie réelle n'est prétendue.
- `world-atlas` 2.0.2 (déjà épinglé) ne contient pas ces sites à l'échelle voulue : `land-10m` et `countries-10m` restent
  trop grossiers pour un site ou un petit îlot.
- **Pour un sujet `geographie` réel** :
  - préconvertir une fois, hors rendu, le topojson en tableaux numpy (décodage des arcs en Python, ou `topo2geo` de
    topojson-client) ;
  - **vérifier que le polygone existe et tient au cadrage prévu**, sinon changer de sujet ;
  - ne jamais rien charger du réseau au rendu.

### 7.1 Short 1 : `survol-pixel__explicatif__comment-nait-un-atoll` (≈ 16 s, ≈ 41 mots)

| t (s) | Vue / mouvement | Image | Voix (≈ 2,6 mots/s) | Écran |
|---|---|---|---|---|
| 0–0,8 | dessus, défilement | un anneau de corail turquoise au milieu du bleu profond, nuages et ombres | (accroche visuelle) | cartouche Jersey 20 « UN ANNEAU EN PLEINE MER ? » dès 0,3 s |
| 0,3–3,6 | dessus → **piqué** à 3,2 s | | « Un anneau de corail en plein océan. D'où vient-il ? » (10 mots) | |
| 3,6–7,4 | rasante : un volcan en terrasses se lève à l'horizon, récif frangeant | | « Au départ, un volcan sort de la mer. Le corail pousse sur ses bords. » (14) | plaque HUD « ÉTAPE 1 » |
| 7,4–11,2 | rasante, accéléré du temps : les terrasses s'enfoncent marche par marche, le lagon s'élargit | | « Le volcan s'enfonce lentement ; le corail, lui, grandit vers la lumière. » (12) | plaque HUD « DES MILLIONS D'ANNÉES » |
| 11,2–11,7 | **remontée** | | | |
| 11,7–16 | dessus : le volcan a disparu, il reste l'anneau et son lagon (rime avec 0 s) | | « Il ne reste qu'un anneau : un atoll. Darwin l'avait deviné en 1842. » (13) | cartouche « ATOLL = ANCIEN VOLCAN » |

**Faits, à vérifier par le studio avant la voix :**
- théorie de l'affaissement de Charles Darwin, dans *The Structure and Distribution of Coral Reefs* (1842) ;
- les coraux constructeurs vivent en eau peu profonde et éclairée ;
- ordre récif frangeant → récif-barrière → atoll ;
- confirmation par les forages d'Enewetak en 1952, qui atteignent le basalte sous plus de 1 200 m de calcaire corallien.
  Ce dernier fait n'est pas dans la voix, il peut aller dans la description.

### 7.2 Short 2 : `survol-pixel__histoire__machu-picchu-cite-en-escaliers` (≈ 17 s, ≈ 44 mots)

| t (s) | Vue / mouvement | Voix | Écran |
|---|---|---|---|
| 0–3,4 | rasante basse dans une vallée andine, nuages en parallaxe ; une crête en terrasses (biome montagne : granit, chaume) surgit derrière un nuage | « Une cité inca perchée à 2 430 mètres, toute en escaliers. Pourquoi ? » (11) | cartouche Jersey 20 « MACHU PICCHU » à 0,4 s ; plaque HUD « ALT 2 430 M » |
| 3,4–3,9 | **remontée** vers la vue de dessus | | |
| 3,9–7,6 | dessus : les terrasses en arcs concentriques, la cité au sommet ; la carte défile | « Au quinzième siècle, les Incas taillent la montagne en terrasses. » (10) | plaque HUD « XVe SIÈCLE » ; cartouche « reconstitution stylisée » en Jersey 10 |
| 7,6–8,1 | **piqué** au ras d'une terrasse | | |
| 8,1–12,4 | rasante : **coupe d'une terrasse posée au sol comme une maquette** (pierres, gravier, terre) ; la pluie (pixels bleus en pas entiers) traverse les couches et s'évacue | « Chaque marche retient la terre et laisse filer la pluie : la montagne ne glisse pas. » (15) | étiquettes au sol « TERRE », « GRAVIER », « PIERRES » |
| 12,4–17 | survol en montée, la crête s'éloigne dans la brume dorée, puis remontée | « Les Espagnols ne l'ont jamais trouvée. Elle est révélée au monde en 1911. » (13) | cartouche « 1911 » |

**Faits, sources usuelles (UNESCO, sites sur l'archéologie inca), à vérifier par le studio :**
- ≈ 2 430 m d'altitude ;
- construction au XVe siècle, attribuée à l'empereur Pachacutec ;
- terrasses agricoles (*andenes*) à drainage en couches (pierres, gravier, terre) qui limitent l'érosion et les glissements ;
- non signalée par les conquistadors ;
- révélée internationalement par Hiram Bingham en 1911, guidé par des habitants de la région. La voix dit « révélée au
  monde », pas « découverte ».

**Ne pas citer** de nombre exact de terrasses ni de pourcentage de construction souterraine : les chiffres divergent selon
les sources.

### 7.3 Recettes par famille (la signature appliquée à n'importe quel sujet)

| Famille | Ouverture (< 1 s) | Corps | Texte | Clôture |
|---|---|---|---|---|
| **explicatif** | vue de dessus sur le résultat (l'anneau, le delta, le cratère) avec la question en cartouche | piqué → rasante pour montrer le mécanisme dans le paysage ; **schéma posé au sol** (flèches, coupe en maquette) ; accéléré du temps par paliers de terrasses | cartouche question en Jersey 20 ; étapes en plaque HUD (« ÉTAPE 1 ») ; mots clés en bleu ou rouge dans la crème | remontée vers la vue de dessus du début : la forme est enfin comprise |
| **enfants** | un **personnage guide original** (par exemple un petit dirigeable rond orange, ou un oiseau de papier) entre dans la vue de dessus avec son ombre | vues longues (4 s) ; une seule idée par vue ; objets en gros billboards (arbre, maison, animal), chacun avec son ombre ; roulis ≤ 10° | ≤ 4 mots par cartouche, Jersey 15 au minimum ; pas de HUD chiffré | le guide se pose, la caméra remonte ; question douce, sans pression |
| **histoire** | rasante sur le lieu reconstitué qui surgit de la brume ; date en plaque HUD | alternance dessus (plan, organisation) et rasante (échelle humaine) ; billboards de bâtiments et de foules en silhouettes ; mention « reconstitution stylisée » | date et lieu en HUD or ; récit en cartouche ; jamais de faux document | remontée : le lieu dans son paysage, date finale en cartouche |
| **geographie** | vue de dessus d'une **côte réelle** (`world-atlas` 2.0.2 préconverti, polygone vérifié au cadrage) | survol le long du tracé ; piqué sur le relief, avec un relief **schématique** annoncé comme tel tant qu'aucune donnée d'altitude épinglée n'existe ; pastilles de lieux = billboards ombrés | noms de lieux en cartouches petites (Jersey 10) avec flèche au sol | remontée à une altitude qui montre l'ensemble, chiffre clé en cartouche |
| evenements (facultatif) | plaque HUD compte à rebours sur une vue de dessus | survol du lieu de l'événement | date en Jersey 20 | remontée |

## 8. Voisines et différences

### 8.1 `pixel-arcade`

Signature de pixel-arcade : terrain de jeu marine sombre, mouvement quantifié à 4 px, HUD Press Start 2P, physique
pré-simulée avec photo-finish, mosaïque de pixels et blips. C'est une **nouvelle identité**, pour les raisons du § 1.

1. **Fond** : monde en plein jour, océan saturé `#1E5AA8` avec terre verte en terrasses et ciel. Pixel-arcade a un fond
   uni `#0E0B1F` quasi noir, sans décor.
2. **Espace** : perspective Mode 7 avec horizon, parallaxe et ombres portées. Pixel-arcade est un plan plat de face, sans
   profondeur.
3. **Texte** : Jersey condensée, encre sur cartouches crème ombrées. Pixel-arcade a Press Start 2P et Rubik Mono One en
   couleurs néon sur cadres marine.
4. **Transition** : le piqué de caméra continu. Pixel-arcade utilise la mosaïque (`pixelize`).
5. **Son** : bourdon, nappe et whoosh. Pixel-arcade a du chiptune avec blip et coin.
6. **Moteur** : Python numpy. Pixel-arcade tourne dans le navigateur (Matter, p5, Pixi).

### 8.2 `carte-meteo` (risque n° 1 : mer bleue et terre verte vues de dessus)

1. **Saturation et valeur** : océan profond `#1E5AA8` (luminance ≈ 0,10), terres saturées à 3 verts plus un trait de
   niveau. Carte-meteo a une mer très pâle `#CFE6F5` et un vert tendre uni.
2. **Grille** : gros pixels de 4 px partout, contours en escalier. Carte-meteo est vectorielle, lisse et anticrénelée
   (D3 en SVG).
3. **Profondeur** : vues rasantes avec horizon, ciel en paliers, brume dorée, nuages volumineux à ombre portée.
   Carte-meteo reste vue de dessus à plat.
4. **Habillage** : ni isobares, ni traînées de vent, ni pastilles de température, ni front diagonal. Cartouches de
   dialogue crème en police pixel, contre cartouches blancs en Atkinson et Space Grotesk.
5. **Garde-fou mesurable** : en vue de dessus, l'océan profond reste > 45 % des pixels, et chaque short a au moins 50 % de
   sa durée en vue rasante ou en piqué.

### 8.3 `topo-relief` (survol de relief, surtout pour Machu Picchu)

1. **Lumière** : plein jour, palette saturée et ciel visible. Topo-relief est un bloc de nuit vert forêt `#14221C`.
2. **Courbes** : traits de niveau **sombres** de 1 gros pixel en escalier, un aplat de vert par marche. Topo-relief a des
   courbes **lumineuses** ocre et turquoise qui brillent.
3. **Rendu** : grille pixel, palette indexée, sans éclairage 3D. Topo-relief est en three.js lisse avec ombrage.
4. **Typographie et HUD** : Jersey sur cartouche crème. Topo-relief a l'altitude en JetBrains Mono et le titre en Inter.
5. **Coût** : 10–30 s pour 100 images (estimé), contre 108–169 (mesuré).

### 8.4 `trait-continu` (modèle de moteur seulement)

Le moteur est du même type (Python image par image), mais aucun trait visuel n'est commun : pas d'orange, pas de plaque
grise, pas de tracé continu.

## 9. Ce qu'on ne copie pas de la source (et nos versions)

| Source | Notre version |
|---|---|
| l'avion de chasse anthracite et rouge, sa postcombustion, sa fumée | **pas d'avion obligatoire** : la caméra vole. Guide facultatif original (petit dirigeable rond orange `#B5341A` et crème, ou oiseau de papier) |
| le cockpit (arceau à plaques orange, radar, bille, écran à silhouette, manche) | aucun tableau de bord. Seulement une **plaque HUD** rectangulaire facultative pour un chiffre ou une date |
| le HUD vert filaire (échelles, réticule, cap) | phosphore réservé aux chiffres en Jersey 15 sur plaque sombre. Ni réticule ni échelles |
| la ligne d'aide (« MOVE TO STEER · … ») en monospace sur bandeau translucide | cartouches de dialogue crème en police pixel, texte en français lié au récit |
| la carte (forme des îles, rochers, forêts) | mondes générés par graine et forme guidée par sujet, lieux réels seulement d'après des données épinglées |
| les traînées blanches antialiasées, hors grille | rien hors grille, pas de traînée |
| la palette exacte | dérivée puis déplacée : océan plus profond, brume dorée, crème et encre, biomes |
| le curseur, les commandes de jeu | absents |

## 10. Risques

1. **Lisibilité du texte pixel sur téléphone.**
   - Jersey 10 donne des capitales de 40 px à l'écran : c'est le minimum.
   - Le corps est de 74,7 px, mais les bas-de-casse condensées peuvent fatiguer. Limite : 2 lignes par cartouche de corps.
   - Le studio vérifie une image fixe à 360 px de large (taille d'aperçu).
2. **Photosensibilité.**
   - Aucun flash.
   - La traversée du nuage, seul grand saut de luminance, a lieu au plus une fois et monte en ≥ 0,3 s.
   - L'écume scintille ≤ 4 fois par seconde, localement.
   - Le roulis reste ≤ 25° pour éviter le mal des transports.
3. **Aliasing Mode 7.** Le crénelage scintillant près de l'horizon fait partie du style, mais il peut devenir du bruit et
   gonfler le débit H.264. Trois parades à tester :
   - masquer les ≈ 20 dernières lignes par la brume ;
   - choisir un niveau de détail de la carte (une carte réduite pour les lointains) ;
   - viser un débit de ≈ 8–12 Mb/s et vérifier le poids des mp4.
4. **Coût.** La marche voxel n'est pas mesurée : si elle dépasse ≈ 60 s pour 100 images, on passe à la variante B.
5. **Reconnaissance.**
   - Contre carte-meteo, voir le garde-fou du § 8.2.
   - Contre pixel-arcade, le test aveugle doit séparer les deux : les fonds jour et nuit et les polices y aideront.
6. **Effet « jeu fait par IA » ou générique.**
   - Le risque : un rendu de bruit sans intention, des terrasses en anneaux trop réguliers, des nuages identiques.
   - Parades : formes guidées par le sujet (le volcan, la crête), billboards dessinés à la main en code, hachures et écume
     posées selon des règles, et la grammaire du piqué au service du récit, jamais en démonstration.
7. **Exactitude** des faits historiques (§ 7.2), et mention « reconstitution stylisée » obligatoire pour les sites.
8. **Polices à épingler** : `@fontsource/jersey-10`, `jersey-15` et `jersey-20` en `5.3.0` exact dans `package.json`.
   Elles sont absentes de `node_modules` aujourd'hui.

---

## Variante de repli B : « Maquette empilée » (si le voxel space échoue ou coûte trop)

- **Même palette, mêmes polices, mêmes cartouches, même piqué.**
- Seule change la façon de lever le relief : sol Mode 7 plat, et volumes en **sprite stacking**. Chaque volcan, temple,
  abbaye ou arbre est une pile de 8–24 tranches horizontales en pixel art, dessinées en code et superposées avec un
  décalage vertical de 1 px par tranche.
- Les piles tournent avec le cap de la caméra : c'est un vrai volume 3D, toujours sur la grille.
- La lecture « pile de tranches » prolonge celle des nuages de la source.
- Coût attendu plus faible : quelques dizaines de blits par image.
- Limite : les reliefs étendus (une chaîne de montagnes entière) se lisent moins bien. Elle convient surtout aux sujets
  centrés sur un objet ou un lieu : un monument, une île, un volcan isolé.
