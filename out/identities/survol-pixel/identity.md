# Survol pixel — identité visuelle

## Nom
**Survol pixel** (`survol-pixel`). Nom de travail pendant l'analyse : « console rétro » (notes `out/report/notes/console-retro-*`).
Chaque sujet devient un **petit monde en pixel art 16 bits**, survolé par une caméra qui vole sans jamais couper : vue
plongeante pour comprendre la forme, **piqué** vers l'horizon pour sentir le lieu, **remontée** pour conclure.

**Statut : nouvelle identité, pas une dérivation de `pixel-arcade`.** Tout diffère : le moteur (Python numpy, une caméra
3D sténopé, contre Matter.js + p5 + PixiJS dans un navigateur), l'espace (un monde en perspective avec horizon contre une
aire de jeu plate vue de face), les polices (Jersey contre Press Start 2P / Rubik Mono One), la transition signature (le
piqué de caméra contre la mosaïque de pixels), le son (nappe et souffles contre chiptune à blips), la lumière (plein jour
contre fond marine quasi noir). La grille 270×480 ×4 est commune aux deux : ce n'est **pas** une différence (C12).

### Provenance (inspiration de style, crédit)
Style étudié d'après la vidéo de démonstration d'un simulateur de vol en pixel art publiée par **@creativedash**
(https://x.com/creativedash/status/2122000830895386680, reprise par @meta_pavy), analysée image par image le 18/11/2026
(`out/report/notes/console-retro-analyse.md`, planche `out/report/notes/console-retro-source/`). On en reprend une **forme** :
grille unique de gros pixels, palette indexée courte, sol en perspective type « Mode 7 », relief en terrasses à trait
sombre, couches empilées avec ombres portées plates, ciel en paliers, caméra continue sans coupe.

**Ce qui n'est PAS copié** (tout est regénéré par code) : l'avion (silhouette, couleurs, flammes, fumée) et tout sprite de
la source ; le cockpit (arceau, radar, bille, cadrans, manche, interrupteurs) ; le HUD vert filaire (échelles, réticule,
cap) ; la ligne d'aide et tout texte d'interface ; la carte (formes d'îles, rochers, forêts) ; les traînées antialiasées ;
le principe de jeu et les commandes ; le son (la source est muette). Rien n'est emprunté non plus à un jeu existant :
pas d'anneaux à traverser, pas de piste ni de marques d'atterrissage, pas de score ni de compte à rebours, pas de mélodie
qui cite une musique de jeu (C17). Aucun asset téléchargé ; seules les polices Jersey viennent de npm (OFL-1.1).

## Promesse en une phrase
« Chaque sujet devient un petit monde en pixel art 16 bits que la caméra survole, puis frôle jusqu'à l'horizon : la
profondeur d'une console des années 90 au service d'une histoire racontée. »

## Mood & références de genre
Console de salon 16 bits du début des années 90 au **plein jour** : sol couché en perspective vers un horizon, ciel en
bandes plates, brume dorée au loin, îles et montagnes en marches, nuages en piles de lobes hachurés. Le ton n'est pas
celui d'un jeu mais d'un **documentaire maquette** : on survole un monde miniature qu'on peut couper comme un gâteau pour
voir dedans (coupe géologique, coupe d'une terrasse). Calme, lumineux, didactique ; le jeu vidéo est une texture, jamais
le sujet. Références de genre seulement : diorama de musée, bloc-diagramme de manuel de géographie, pixel art 16 bits.

### Règles de signature (à garder intactes)
1. **Une seule grille de gros pixels, une palette indexée.** Toute l'image (sol, relief, nuages, objets, texte, cadres) est
   calculée à **270×480** en indices de palette puis agrandie **×4 au plus proche voisin** (1080×1920). Aucun pixel plus
   gros ou plus petit que 4×4 : les objets ne sont jamais agrandis au-delà de 1:1 (C4), le texte est rendu à la grille
   native sans anticrénelage. Pas de tramage global, **pas d'effet d'écran** (ni scanlines, ni CRT, ni grain, ni
   aberration, ni flou, ni vignettage). Mesuré sur les images natives (indices exacts, une image toutes les 0,5 s) : 15–17 couleurs en plongeante, 14–23 en
   rasante ; sur les fichiers décodés (blocs 4×4, tolérance ΔRGB 25, revue) 18–28 entrées de palette par image, toutes
   dans la palette déclarée et ≤ 32.
2. **La profondeur 3D est obligatoire (règle du propriétaire).** Jamais de rendu 2D plat. Chaque image montre **au moins
   deux indices de profondeur, dont un géométrique** (C2) parmi :
   - **sol en perspective** fuyant vers un **horizon** (« Mode 7 » généralisé : intersection rayon–plan par pixel) ;
   - **relief en terrasses à flancs visibles** : chaque marche a un dessus plat et une **contremarche colorée** (claire si
     elle regarde la lumière nord-ouest, sombre sinon), trait sombre de 1 gros pixel au pied ;
   - **couches empilées en parallaxe** : sol, objets, nuages (une seule altitude), chacun avec sa profondeur ;
   - **ombres portées plates** des nuages et des objets, décalées selon leur hauteur (l'ombre encode l'altitude) ;
   - **une caméra qui avance, tourne, pique** : aucun plan aérien fixe plus de 4 s.
   La vue « de dessus » est une **vue plongeante en perspective de 65–80°**, jamais une orthographique ; le 90° exact
   n'existe qu'au milieu d'un mouvement (≤ 0,5 s). **≥ 50 % de la durée** a un horizon visible ou un relief en
   perspective (tangage ≤ 60°) : 82 % (atoll) et 79 % (Machu Picchu) des images dans les deux preuves.
3. **La caméra vole, sans coupe ni fondu.** Une seule caméra pour tout le short (cible, distance, cap, tangage, roulis).
   On passe de la plongée à la rasante par **le piqué** (tangage 70° → 15° en 0,6 s) et inversement par **la remontée**.
4. **Le monde se coupe comme une maquette.** Une tranchée à travers une île, une entaille dans des terrasses : la coupe montre l'intérieur
   (basalte, calcaire, eau ; pierres, gravier, terre). C'est l'outil didactique de l'identité.
5. **Le texte vit dans des cartouches crème** (Jersey, encre marine, cadre 1 px, coin coupé, liseré crème extérieur,
   ombre plate (2, 2)), jamais posé sur la carte ni dans la perspective. Étiquettes au sol = cartouche à l'écran relié à
   une **épingle** au sol par un trait de 1 px. Dates et chiffres forts : **plaque inversée** encre / or (une seule à la
   fois, ≤ 25 % de la durée). **Jamais** de plaque phosphore verte, jamais de lecture d'instrument « ALT … M » (C10, C11).

### Appliquer la signature à n'importe quel sujet
La forme est fixe, le contenu change : le monde est **construit pour le sujet** (forme guidée + bruit), puis survolé.
- **Décors** : un lieu réel devient une maquette stylisée (relief guidé, matériaux du biome, bâtiments en blocs de la carte
  de hauteurs : murs = flancs, toits = dessus). Mention « reconstitution stylisée » obligatoire pour un lieu réel.
- **Personnages et objets** : panneaux dessinés en code (tableaux ASCII → indices), en 1–3 tailles faites à la main, réduits
  au plus proche voisin, jamais agrandis ; **chacun a son ombre** au sol (posé : ombre écrasée ; en vol : silhouette
  décalée selon l'altitude). Ex. : la frégate de l'atoll, le lama de Machu Picchu.
- **Survol d'un lieu historique** : rasante qui découvre le lieu dans la brume, plongeante pour le plan, piqué sur un
  détail à hauteur d'homme, remontée finale.
- **Schéma posé sur le terrain** : coupes (le monde coupé), flèches et repères dessinés **dans** la carte (sans lettres), les
  mots restant dans des cartouches à épingle.

### Sujet sans paysage (C16)
Quand le sujet n'a pas de lieu, on lui **fabrique un monde-maquette** :
1. **Le cœur humain** → une île à deux bassins (oreillettes en lagons hauts, ventricules en lagons bas, terrasses de muscle),
   canaux = vaisseaux. *Carte* : deux bassins séparés par une cloison de roche. *Panneaux* : petites barques rouges et
   bleues (le sang) avec leur ombre. *Schéma au sol* : flèches dans la carte qui montrent le sens de la circulation ; coupe
   de la cloison. *Piqué* : de la vue plongeante (les deux circuits) à la rasante au ras d'une valve (une écluse qui
   s'ouvre). Cartouches « OREILLETTE », « VENTRICULE » à épingle.
2. **Un événement d'histoire en ville** (ex. la prise de la Bastille) → plan de ville en terrasses (quartiers en marches,
   forteresse en blocs à flancs sombres). *Panneaux* : foules en silhouettes (groupes de 3–5 personnages de 6×10 px) avec
   ombres. *Schéma* : trajet des foules en flèches au sol. *Piqué* : de la plongée (la ville) au pied des tours. Date en
   plaque inversée.
3. **Une notion abstraite** (ex. l'histoire de l'écriture) → une **frise du temps posée au sol comme une route** que la
   caméra suit en rasante, chaque époque étant une terrasse plus haute. *Panneaux* : un objet par époque (tablette, rouleau,
   livre, écran), ombré. *Schéma* : graduations sur les bords de la route (sans lettres) + cartouches à épingle pour les
   dates. *Piqué* : entrée sur la route au début, remontée finale qui montre toute la frise d'un coup.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
Palette **indexée** : un noyau fixe de 23 couleurs (dérivé des mesures k-means de la source, puis déplacé : océan plus
profond, brume dorée, crème et encre, rouge et or) + **3 à 5 couleurs « biome »** déclarées par épisode. Les ombres, la
brume et la brume d'horizon sont des **tables d'indices → indices** (jamais de mélange continu hors palette).

| Rôle | Hex | Usage | Contraste |
|---|---|---|---|
| Fond (océan profond) | `#1E5AA8` | eau du large, le fond de l'atoll | — |
| Surface (cartouche) | `#FBF3D5` | intérieur des cartouches | — |
| Texte (encre) | `#14213D` | texte et cadre des cartouches, socle des coupes | **14,36:1** sur crème |
| Accent 1, rouge brique | `#B5341A` | gorge de la frégate, couverture du lama ; jamais seul sur l'eau (1,13:1) | 5,44:1 sur crème |
| Accent 2, or | `#FFC94A` | dates sur plaque inversée, tête d'épingle | ≈ 10:1 sur encre |
| Accent 3, lagon | `#7CCBEB` | lagon, niveau de la mer dans les coupes | décoratif |
| Océan moyen / haut-fond | `#2C74BE` / `#3FA0D0` | anneaux de profondeur en escalier | décoratif |
| Écume | `#E6FAFF` | moutons (traits de 2–3 cellules), ressac, tireté du niveau de la mer | décoratif |
| Ombre sur l'eau | `#143F7E` | ombres portées (table d'ombre) | décoratif |
| Herbes ×3 / forêt | `#93D94E` `#5DB534` `#2F7A2A` / `#174A22` | marches alternées, trait de niveau, flancs | décoratif |
| Nuage / hachure | `#FBFDFE` / `#AFBBC6` | lobes, moitié basse hachurée une ligne sur deux | décoratif |
| Ciel haut / milieu / bas | `#6FB4E3` `#96CBEB` `#BFE2F1` | paliers plats selon l'élévation du rayon | décoratif |
| Brume dorée | `#EFE2BF` | bande d'horizon (ciel < 0,8° et sol lointain) | décoratif |
| Lointains | `#5B9DCD` / `#92B9A4` | eau / terre au-delà de la 1re distance de brume | décoratif |
| Muted | `#5A5F73` | joints, mentions | 5,69:1 sur crème |
| Succès / danger | `#2F7A2A` / `#B5341A` | rarement utiles : l'identité raconte, elle ne note pas | — |

**Biomes utilisés** — tropical (atoll) : sable `#EBDFA0`, roche `#8A8178`, corail `#E58A7A`, basalte `#4E4A4C`, calcaire
`#E3D3A8` ; montagne (Machu Picchu) : granit `#9C968C`, granit ombre `#5F5A55`, chaume `#C9A35A`, terre `#8A5A3A`.
Autres biomes prévus : littoral tempéré (grève `#CDBB8A`, ardoise `#5E6A78`, pierre `#D9D2C3`), désert (ocre `#D9A55B`,
terre cuite `#B5572E`, pierre `#E3D3A8`).

**Interdits** : texte posé sur la carte ou le ciel ; texte orange vif ; rouge brique comme seul repère sur l'eau ou l'herbe
(1,13 et 2,34:1 : toujours avec un liseré encre et crème) ; courbes de niveau claires ou lumineuses (C11) ; fond quasi noir.

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
Famille **Jersey** (Sarah Cadigan-Fried, OFL-1.1), `@fontsource/jersey-10`, `jersey-15`, `jersey-20` **5.3.0** épinglées
exactement dans `package.json`, sous-ensemble `latin` seulement (accents français complets ; manquent ² ³ ±). Graisse
400 unique, interlettrage 0, interligne = em complet. Rendu PIL `fontmode = "1"` à la résolution native sur coordonnées
entières : la grille est exacte (test `src/test_jersey_grid.py` : 99/99 glyphes par taille, encre = aire du contour / pas²).

| Rôle | Police | Taille native | Corps final | Capitale finale | Usage |
|---|---|---|---|---|---|
| Accroche, mot géant, date | Jersey 20 | 34 px/em | 136 px | 80 px | « UN ANNEAU / EN PLEINE MER ? », « MACHU PICCHU », « DARWIN, 1842 » |
| Récit, étiquettes | Jersey 15 | 27 px/em | 108 px | 60 px | un cartouche par plan, ≤ 6 mots, ≤ 2 lignes ; épingles « terre », « basalte » |
| Mentions secondaires | Jersey 10 | 18,667 px/em | 74,7 px | 40 px | seulement « reconstitution stylisée » et « marches : convention de dessin » ; toute information (durées, faits datés) passe en Jersey 15 sur 2 lignes |

- **≤ 214 px natifs par ligne** (≈ 30 / 20 / 15 caractères en Jersey 10 / 15 / 20), **≤ 2 lignes** : le moteur fait échouer le
  rendu sinon (assertion), comme pour une boîte hors zone sûre.
- Marge haute du cartouche 5 px natifs (accents É, È, À visibles), basse 3.
- L'accroche est **affichée entière** dès 0,12–0,15 s (jamais tapée lettre à lettre) ; les autres cartouches s'ouvrent en
  hauteur en 4 images (0,13 s) puis le texte apparaît d'un coup.

## Formes & matières
- **Le monde** : carte de hauteurs en **terrasses** (dessus constant par cellule) + carte de couleurs. Marches de 3,5 (atoll)
  ou 2,5 et 6 unités (Machu Picchu) ; marches alternées de deux verts, trait sombre au pied de chaque marche, sommets de
  roche, forêts en taches (bruit opensimplex calculé une fois).
- **L'eau** : plan z = 0 ; couleur selon la profondeur du fond en 4 anneaux en escalier (lagon, haut-fond, océan moyen,
  océan) ; moutons d'écume semés (≈ 1 pour 150 cellules) qui alternent entre deux phases à **2 Hz** ; ressac épars.
- **Contremarches** : le flanc d'une marche prend la couleur de flanc du matériau (pierre : granit clair / granit ombre ;
  herbe : vert sombre / forêt), selon qu'il regarde la lumière nord-ouest ou non.
- **Coupes** : une région du monde descend « comme un ascenseur » jusqu'à un socle de roche hachurée (jamais l'encre, couleur du texte) ; ses parois montrent la
  coupe colorée par une fonction de la scène (strates à joints, gravier moucheté, tireté du niveau de la mer).
- **Nuages** : piles de 3–5 disques horizontaux projetés (ellipses aplaties en rasante, ronds en plongée), dessinés à la
  taille projetée au pixel près, moitié basse hachurée une ligne sur deux, liseré bas. **≤ 4 à l'écran.**
- **Objets** : panneaux ASCII (frégate 31×10 en 2 images d'ailes, palmier 11×10, lama 24×22), jamais agrandis, avec ombre.
- **Cartouches** : rectangle crème, cadre encre 1 px, coin coupé d'un pixel, liseré crème extérieur 1 px, ombre plate (2, 2)
  par la table d'ombre (la même règle que les nuages). Plaque inversée : fond encre, cadre crème, texte or.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- **Caméra** : clés interpolées par segment — `inOutSine` pour le piqué et la remontée (0,6 s), `inOutSine` lent pour les
  orbites (3,5–4,7 s), `linear` pour les survols. Roulis ≤ 3° (récit, pas démonstration de vol).
- **Temps du monde** : `inOutCubic` pour les retours en arrière (1,0 s), `inOutSine` pour les transformations lentes
  (3,6 s : le volcan qui s'enfonce marche par marche). Coupe qui s'ouvre : `inOutCubic` 0,8 s.
- **Objets** : la frégate bat des ailes à 3 images/s ; la pluie tombe en pas entiers, s'infiltre lentement (≈ 3 unités/s),
  sort au pied du mur.
- **Cartouches** : ouverture en hauteur 4 images (0,13 s), pas d'animation de sortie (relève franche au plan suivant).
- **Jamais** : coupe franche, fondu enchaîné, mosaïque de pixels (pixel-arcade), flash, clignotement > 3 Hz, zoom
  numérique de l'image, déplacement d'une fraction de gros pixel du texte, tremblement de caméra.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
- **Une seule caméra sténopé** pour tout le short : cible (x, y, z), distance, cap, tangage, roulis ; focale 416 px natifs
  (champ vertical ≈ 60°, horizontal ≈ 36°).
- **Trois cadrages** : **plongeante** 60–72° (comprendre la forme ; aucun horizon, mais flancs, ombres et perspective
  visibles) ; **rasante** 9–20° (horizon à 20–25 % du haut, ciel en paliers, brume dorée ; sentir le lieu) ; **au ras d'un
  détail** 15–19° à courte distance (coupe d'une terrasse, objet).
- Caméra toujours au-dessus du relief (contrôle `--preflight` sur toutes les images : marge minimale 56–63 unités).
- Profondeur de champ : aucune (tout net). La profondeur vient de la perspective, des flancs, des couches et des ombres,
  jamais d'un flou.

## Transitions (liste nommée, durée, quand les utiliser)
- **Le piqué** (signature) : tangage 70° → 15°, distance et cible qui glissent, `inOutSine`, **0,6 s**, souffle (`whoosh`).
  Pour passer de « comprendre » à « sentir ». Série de preuve 90/70/50/30/15° dans `src/dive/` de chaque short : aucun
  relief qui apparaît ou disparaît.
- **La remontée** : l'inverse (15° → 30–64°), 0,6–0,8 s, `whoosh` ; pour conclure ou changer d'échelle. Une coupe se
  regarde **de face** (cap perpendiculaire à la paroi), jamais par l'arête.
- **Le temps qui passe** : la caméra reste en vol pendant que le monde change par marches (retour en arrière 1 s,
  transformation 3,6 s), avec une mention Jersey 15 sur 2 lignes (« il y a des millions / d'années », « pendant des millions / d'années »).
- **La coupe qui s'ouvre** : une région descend jusqu'au socle en 0,8 s (`thud` discret).
- **Interdits** : traversée de nuage (non utilisée : risque de luminance, C13), mosaïque, fondu, coupe.

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
16–19 s, 3–5 vues de 3–5 s reliées par des piqués / remontées de 0,6 s, un cartouche Jersey 15 par vue qui porte l'idée
sans le son (≤ 6 mots).
- **0–1 s, hook** : la forme résultat ou le lieu, déjà en mouvement, et la question en Jersey 20 affichée entière dès
  0,15 s (mêmes mots-clés que la première phrase de la voix).
- **Développement** : piqué vers la rasante ; le mécanisme montré dans le paysage (coupe, transformation par marches,
  objet ombré) ; une étape par cartouche numéroté si besoin (« 1. », « 2. », « 3. »).
- **Chute** : remontée vers la plongée ou survol qui s'éloigne ; date / nom en plaque inversée.
- **Fin** : tenue ≥ 3 s sur l'image qui résume (l'anneau coupé avec le volcan dessous ; la cité dans la brume dorée).
  Bouclable si la dernière vue rime avec la première.

## Zones sûres
Natives (×4 = final) : haut **55 (220 px)**, bas **80 (320 px)**, droite **30 (120 px)**, gauche **16 (64 px)**. Le moteur
vérifie chaque cartouche (boîte + liseré + ombre dans [16, 240] × [55, 400] natifs) et fait échouer le rendu sinon.
Cartouches centrés sur x = 128 (milieu de la bande sûre) ; récit en haut (y = 62), mentions en bas (bas à y = 398).

## Librairies recommandées et pourquoi
- **numpy 2.4.6** : tout le moteur — lancer de rayon par pixel (marche à pas fixes dans la boîte du relief + 6 bissections,
  par paquets de 12 pas avec retrait des rayons arrivés), intersection rayon–plan, cartes réduites par vote majoritaire,
  tables d'indices. Coût mesuré : **15,6–59,1 s / 100 images** sous charge (voir les `short.json`).
- **Pillow 13.0.0** : texte Jersey sans anticrénelage (`fontmode "1"`, lit les `.woff2`), stills JPEG.
- **opensimplex 0.4.5.1** : bruits du monde (côte irrégulière, forêts, crêtes), calculés une fois et mis en cache.
- **scipy** (`binary_dilation`) : boîte englobante autour des coupes.
- **fontTools** (déjà présent via matplotlib) : test de grille des polices.
- **ffmpeg** : encodage rgb24 → x264 crf 14 (intermédiaire), puis `assemble.py mux` (crf 20, maxrate 8M).
- `out/tools/sound.py` : preset **`pad` en `lydian`** (un seul preset), `whoosh`, `swell`, `riser`, `pop`, `chime`, `thud`.
- Pas de navigateur, pas de Chromium : l'identité tourne en Python pur.

## Familles de contenus adaptées / inadaptées
- **Adaptées** : `explicatif` (phénomènes de la Terre, mécanismes montrés en coupe), `histoire` (lieux reconstitués,
  cités, sièges, routes), `geographie` (reliefs, côtes, fleuves — relief schématique annoncé comme tel), `enfants`
  (mondes-maquettes, personnage guide ombré, vues longues). Recettes dans `recipes/`.
- **Possibles** : `evenements` (date en plaque inversée sur le lieu de l'événement).
- **Inadaptées** : `abstrait` (la forme a besoin d'un monde), `engagement` à mécanique de jeu (score, course : c'est le
  terrain de pixel-arcade), sujets qui exigent une géographie exacte à petite échelle sans donnée épinglée.

## Shorts de preuve (chemins)
- `out/shorts/survol-pixel__explicatif__comment-nait-un-atoll/` — « Comment naît un atoll ? » (18,6 s) : volcan en
  terrasses → récif frangeant → récif-barrière et lagon → atoll, niveau de la mer fixe, tranchée coupée vue de face qui montre le
  volcan enfoui sous l'anneau ; frégate et son ombre.
- `out/shorts/survol-pixel__histoire__machu-picchu-pourquoi-une-cite-en-escaliers/` — « Machu Picchu : pourquoi une cité
  en escaliers ? » (18,8 s, reconstitution stylisée) : cité sur l'ensellement, terrasses à murs de pierre, entaille qui
  montre pierres / gravier / terre, pluie qui traverse, lama et son ombre.
- Comparaison avec la source : `out/report/notes/console-retro-source/comparaison.jpg`.

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)
- **Voix non enregistrée** (décision du propriétaire en attente : Gemini « Sulafat » comme le lot 2, ou Fish Audio
  « Arnold »). `narration.json` donne les lignes calées ; les shorts sont livrés avec musique et bruitages seulement, et
  le texte à l'écran porte l'histoire sans le son.
- Une phrase par vue, **≤ 2,6 mots/s en mots prononcés** (« 1842 » = 4–5 mots ; 2,2–2,6 mesurés) ; **silence pendant les
  piqués et les remontées** (le souffle porte la transition). Enfants : 2,0–2,3 mots/s, vues de 4 s.
- La première phrase reprend les mots-clés de l'accroche à l'écran (C20).
- Le visuel laisse la voix dire les nombres et les causes ; l'écran ne garde que l'idée en ≤ 6 mots.

## Risques et limites
- **Lisibilité** : Jersey 10 (capitale 40 px) réservée aux mentions ; tester une image réduite à 360 px de large.
- **Flancs raides vus par la tranche** : sans correctif, les contremarches et les dessus alternent d'un pixel à l'autre et
  grésillent (6–9 % des pixels changent par image). Le moteur relève le niveau de carte réduite selon la pente locale et
  colore les contremarches lointaines avec la carte réduite (1,3–1,6 % mesurés). Contrepartie : les flancs moyens-lointains
  deviennent plus « en blocs » (visible sur l'accroche de Machu Picchu). Éviter aussi les rotations de cap rapides en
  plongeante.
- **Coupe** : la regarder de face (cap perpendiculaire à la paroi), garder les épingles pendant toute la tenue, socle en
  roche hachurée assez haut pour rester < 5 % de l'image ; vue par l'arête, elle se lit comme un « trou noir ».
- **Gros texels près de la caméra** : en rasante très proche, une cellule du monde fait jusqu'à 7 px natifs (blocs). C'est
  le prix du « Mode 7 » ; garder la caméra à ≥ 60 unités d'une coupe, ou affiner la grille du monde (Machu Picchu : ×1,8).
- **Coût** : le lancer de rayon par pixel coûte 15,6–59,1 s / 100 images sous charge ; un relief très étendu en rasante
  approche le budget de 60 s (augmenter `steps` coûte en proportion). Repli prévu : volumes en « sprite stacking ».
- **Relief en marches = convention de dessin** : les terrasses d'un volcan ne sont pas un fait ; le dire à l'écran
  (Jersey 10) quand le public est jeune.
- **Confusions possibles** : pixel-arcade (même grille ×4 : on s'en sépare par le plein jour, la perspective, les
  ombres, Jersey et les cartouches crème), carte-meteo (mer bleue vue de haut : notre océan est profond et saturé,
  luminance moyenne d'image Y mesurée 0,35–0,53 pour l'atoll et 0,41–0,57 pour Machu Picchu contre 0,77, et la rasante
  occupe > 50 % du temps), topo-relief (survol de relief : courbes sombres,
  plein jour, aucune lecture d'altitude). Ressemblance avec *Pilotwings* (Mode 7 sur île) : aucun élément de jeu.
- **Photosensibilité** : aucune image pleine en blanc, écume à 2 Hz, battement d'ailes à 3 Hz, pas de traversée de nuage ;
  variation de luminance moyenne mesurée sur les fichiers finaux (voir `short.json.qualityChecks`).
- **Lieux réels** : toujours « reconstitution stylisée » ; aucune géométrie réelle prétendue ; faits sourcés dans
  `short.json`.
