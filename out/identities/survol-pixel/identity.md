# Survol pixel — identité visuelle

## Nom
**Survol pixel** (`survol-pixel`). Nom de travail pendant l'analyse : « console rétro » (notes `out/report/notes/console-retro-*`).
Chaque sujet devient un **petit monde en pixel art 16 bits**, survolé par une caméra qui vole sans jamais couper : vue
haute pour comprendre la forme, **piqué** vers le détail ou l'horizon pour sentir le lieu, **remontée** pour conclure.

**Passe A+B+C (18/11/2026)**, à la demande du propriétaire : monde rempli jusqu'à l'horizon et brume refaite (A), fin des
« cubes » et des bascules de détail (B), caméra qui vole et textes allégés (C). Journal : `out/report/notes/survol-pixel.md`
§ « Passe A+B+C » ; planche avant / après : `out/report/notes/console-retro-source/final-abc.jpg`.

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
bandes plates, brume bleu pâle au loin (dorée avant la passe A+B+C), îles et montagnes en marches, nuages en piles de lobes hachurés. Le ton n'est pas
celui d'un jeu mais d'un **documentaire maquette** : on survole un monde miniature qu'on peut couper comme un gâteau pour
voir dedans (coupe géologique, coupe d'une terrasse). Calme, lumineux, didactique ; le jeu vidéo est une texture, jamais
le sujet. Références de genre seulement : diorama de musée, bloc-diagramme de manuel de géographie, pixel art 16 bits.

### Règles de signature (à garder intactes)
1. **Une seule grille de gros pixels, une palette indexée.** Toute l'image (sol, relief, nuages, objets, texte, cadres) est
   calculée à **270×480** en indices de palette puis agrandie **×4 au plus proche voisin** (1080×1920). Aucun pixel plus
   gros ou plus petit que 4×4 : les objets ne sont jamais agrandis au-delà de 1:1 (C4), le texte est rendu à la grille
   native sans anticrénelage. Pas de tramage global, **pas d'effet d'écran** (ni scanlines, ni CRT, ni grain, ni
   aberration, ni flou, ni vignettage). **4 rayons par pixel natif, vote majoritaire sur l'indice de palette** (jamais de
   moyenne : la palette reste exacte). Mesuré après la passe A+B+C sur les stills natifs (indices exacts, cartouches
   compris) : 23–30 couleurs par image (atoll) et 19–26 (Machu Picchu), toujours ≤ 32 (contrôle « Palette » de la revue du challenge) ; médiane 26 et 23 sur la
   frise du prototype (sans cartouches). La **palette déclarée** passe à **40 couleurs par épisode** (35 de noyau + 5 biome ;
   28–29 avant ; **41 à Machu Picchu** depuis la retouche Fable, avec `FOREST_SH`) : la phrase « palette déclarée ≤ 32 » ne tient plus, seul le compte par image reste ≤ 32 (écart signalé au
   propriétaire).
2. **La profondeur 3D est obligatoire (règle du propriétaire).** Jamais de rendu 2D plat. Chaque image montre **au moins
   deux indices de profondeur, dont un géométrique** (C2) parmi :
   - **sol en perspective** fuyant vers un **horizon** (« Mode 7 » généralisé : intersection rayon–plan par pixel) ;
   - **relief en terrasses à flancs visibles** : chaque marche a un dessus plat et une **contremarche colorée** (claire si
     elle regarde la lumière nord-ouest, sombre sinon), trait sombre de 1 gros pixel au pied ;
   - **couches empilées en parallaxe** : sol, objets, nuages (une seule altitude), chacun avec sa profondeur ;
   - **ombres portées plates** des nuages et des objets, décalées selon leur hauteur (l'ombre encode l'altitude) ;
   - **une caméra qui avance, vire, roule et pique** : aucun plan aérien fixe plus de 4 s.
   Une vue « de dessus » reste une **plongeante en perspective** (jamais une orthographique ; le 90° exact n'existe qu'au
   milieu d'un mouvement, ≤ 0,5 s). Depuis la passe A+B+C, les preuves volent **entre 19° et 40°** de tangage (atoll 25–40°,
   médiane 26,5° ; Machu Picchu 19–38°, médiane 29°) : **100 % de la durée** a un horizon ou un relief en perspective
   (tangage ≤ 60° ; 82 % et 79 % avant). La série `src/dive/` (90/70/50/30/15°) reste la preuve du moteur à tout tangage.
3. **La caméra vole, sans coupe ni fondu.** Une seule caméra pour tout le short (cible, distance, cap, tangage, roulis),
   interpolée en **PCHIP** (cubique monotone : vol sans à-coups ni rebond sous le relief). Elle avance et vire, avec un
   **roulis de 5–13°** dans les virages. On descend vers le détail par **le piqué** et on en ressort par **la remontée** ;
   à Machu Picchu, ils sont **ralentis** (36° → 20° en 2,0 s ; 19° → 30° en 2,2 s, décision du propriétaire du 18/11) pour
   limiter le scintillement (0,6 s avant la passe).
4. **Le monde se coupe comme une maquette.** Une tranchée à travers une île, une entaille dans des terrasses : la coupe montre l'intérieur
   (basalte, calcaire, eau ; pierres, gravier, terre). C'est l'outil didactique de l'identité.
5. **Le texte vit dans des cartouches crème** (Jersey, encre marine, cadre 1 px, coin coupé, liseré crème extérieur,
   ombre plate (2, 2)), jamais posé sur la carte ni dans la perspective, **un seul à la fois** (passe A+B+C : texte à
   l'écran 3,8–5,4 % de la surface en médiane, contre 18–20 % avant). Étiquettes au sol = cartouche à l'écran relié à
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
Palette **indexée** : un noyau fixe de **35 couleurs** (24 dérivées des mesures k-means de la source, puis déplacées :
océan plus profond, crème et encre, rouge et or ; + 11 ajoutées par la passe A+B+C : 3 paliers de ciel et 8 paliers de
brume) + **3 à 5 couleurs « biome »** déclarées par épisode. Les ombres, la brume et la moucheture des contremarches sont
des **tables d'indices → indices** (jamais de mélange continu hors palette).

**Brume en 6 paliers** (passe A+B+C ; la règle « brume par tables » est assouplie de 2 à 6 tables, décision du
propriétaire du 18/11) : chaque matière a sa rampe de 6 indices (ex. herbe → `HZ_G1` → `HZ_G2` → `HZ_G3` → `HZ_G4` →
`HAZE` ; eau → `HZ_W1` → `WATER_FAR` → `HZ_W2` → `HZ_W3` → `HAZE`), seuils en multiples d'une distance de référence (la
distance de la caméra, **bornée en bas** : 220 pour l'atoll, 280 à Machu Picchu), frontière **crénelée fixe dans le monde**
(cases de 8 unités, ±10 %). Le dernier palier, `HAZE`, est le **bleu très pâle `#DCEEF5`** = bas du ciel : plus de bande
crème. La brume avance d'un cran à la fois (saut moyen ΔRGB 29–63, contre 94–176 avec 2 tables).

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
| Nuage / hachure / liseré | `#FBFDFE` / `#AFBBC6` / `#CFE3F2` | boules de coton, moitié basse hachurée une ligne sur deux, liseré bleuté au bas (ajouté le 18/11) | décoratif |
| Ciel, 7 paliers | `#6FB4E3` `#83C0E8` `#96CBEB` `#AAD6EF` `#BFE2F1` `#CCE7F3` puis `HAZE` | paliers plats selon l'élévation du rayon (90°, 20°, 13°, 8°, 4,5°, 2,2°, 0,7°) | décoratif |
| `HAZE` (brume d'horizon) | `#DCEEF5` | dernier palier de brume et bas du ciel ; remplace la brume dorée `#EFE2BF` (passe A+B+C) | décoratif |
| Brume verte ×4 | `#3E8A3E` `#5E9C6C` `#86B59C` `#B3D3CF` | `HZ_G1–4` : herbe, forêt, roche, sable vers `HAZE` | décoratif |
| Brume d'eau ×3 / de roche | `#4688C6` `#7AAFD9` `#A8CDE6` / `#9AA3A4` | `HZ_W1–3` : eaux vers `HAZE` ; `HZ_R1` : roche, granit, chaume au 1er palier | décoratif |
| Lointains | `#5B9DCD` / `#92B9A4` | `WATER_FAR` (palier de la rampe d'eau) / `LAND_FAR` | décoratif |
| Muted | `#5A5F73` | joints, mentions | 5,69:1 sur crème |
| Succès / danger | `#2F7A2A` / `#B5341A` | rarement utiles : l'identité raconte, elle ne note pas | — |

**Biomes utilisés** — tropical (atoll) : sable `#EBDFA0`, roche `#8A8178`, corail `#E58A7A`, basalte `#4E4A4C`, calcaire
`#E3D3A8` ; montagne (Machu Picchu) : granit `#9C968C`, granit ombre `#5F5A55`, chaume `#C9A35A`, terre `#8A5A3A`, neige
`#EEF3F4` (sommets lointains, passe A+B+C).
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
| Mot géant (réservé) | Jersey 20 | 34 px/em | 136 px | 80 px | plus utilisée dans les preuves depuis la passe A+B+C (avant : accroches et dates) |
| Accroche, date, récit, étiquettes | Jersey 15 | 27 px/em | 108 px | 60 px | un seul cartouche à la fois, ≤ 6 mots, ≤ 2 lignes : « UN ANNEAU / EN PLEINE MER ? », « MACHU PICCHU », « DARWIN, 1842 » ; épingles « terre », « basalte » |
| Mentions secondaires | Jersey 10 | 18,667 px/em | 74,7 px | 40 px | seulement « reconstitution stylisée » et « marches : convention de dessin » ; toute information (durées, faits datés) passe en Jersey 15 sur 2 lignes |

- **≤ 214 px natifs par ligne** (≈ 30 / 20 / 15 caractères en Jersey 10 / 15 / 20), **≤ 2 lignes** : le moteur fait échouer le
  rendu sinon (assertion), comme pour une boîte hors zone sûre.
- Marge haute du cartouche 5 px natifs (accents É, È, À visibles), basse 3.
- L'accroche est **affichée entière** dès 0,12–0,15 s (jamais tapée lettre à lettre) ; les autres cartouches s'ouvrent en
  hauteur en 4 images (0,13 s) puis le texte apparaît d'un coup.

## Formes & matières
- **Le monde** : carte de hauteurs en **terrasses** (dessus constant par cellule) + carte de couleurs. Marches de 3,5 (atoll)
  ou 2,9 (terrasses agricoles) et 6,3 unités (relief naturel) à Machu Picchu (affinées le 18/11 : 4,5 et 10,8 avant) ;
  marches alternées de deux verts, **rebord clair en haut et trait sombre au pied** de chaque terrasse, sommets de roche,
  toits à deux pans (moitié à l'ombre), forêts en taches (bruit opensimplex calculé une fois).
- **Un monde rempli jusqu'à l'horizon** (passe A+B+C) : 1 080 unités pour l'atoll (×3 : d'autres atolls en anneaux de
  sable et de corail, monts sous-marins, bancs, houle à grandes bandes de profondeur ; jamais d'île verte ni d'archipel
  copié de la source), 1 536 pour Machu Picchu (×2,4 : crêtes et vallées andines, seconde rivière, sommets enneigés
  possibles). **Ombre portée du relief** calculée une fois par monde.
- **Carte de couleurs fine** (passe A+B+C, remplace le micro-détail de la passe de détail) : 4 cases par cellule de
  hauteur sur une **fenêtre autour du sujet** (320 unités pour l'atoll, 512 pour Machu Picchu), carte grossière ailleurs ;
  la carte grossière reprend dans la fenêtre la réduction de la fine (pas de saut à la frontière). Niveau de réduction
  choisi par l'empreinte du sous-rayon avec un **décalage fixe par cellule** (hachage) : une transition est semée dans le
  monde au lieu d'être une ligne qui balaie l'écran. Supprimés : lecture décalée et moucheture sous la cellule, biais de
  pente, règle « mur lointain = couleur du dessus ». Reste une **moucheture des contremarches** fixe dans le monde
  (`wall_speck` 0,25–0,3). Indices seulement, rien n'est moyenné.
- **Arbres en grappes** (18/11) : boules de feuillage au rayon projeté (≤ 7 px, jamais agrandies), reflet haut-gauche,
  ombre propre bas-droite, **ombre portée plate** décalée selon la hauteur ; semées par grappes (bruit) sur les pentes
  naturelles, les terrasses du volcan, jamais sur les terrasses agricoles, la cité ou les coupes.
- **Murs appareillés** (18/11) : contremarches de pierre en assises (0,9 × échelle), joints décalés d'une demi-pierre,
  seulement quand l'assise fait ≥ 3 pixels natifs.
- **L'eau** : plan z = 0 ; couleur selon la profondeur du fond en 4 bandes **crénelées** (seuils décalés d'un bruit fixe par
  cellule, quelques cellules isolées, front externe de pente irrégulière : bandes de 2 à 10 cellules) ; pâtés coralliens dans
  le lagon ; **traits d'écume** (retouche Fable du 18/11, au lieu de points blancs qui se lisaient comme de la neige) :
  4 unités de long sur ½ à 1 de large, tous alignés sur l'axe Y du monde, bleu clair (`LAGOON`) à tête blanche (`FOAM`),
  ≈ 1,6 % des cellules du large, même hachage dans la mer extérieure, la fenêtre fine et la mer au-delà du monde ; deux
  phases qui alternent à **2 Hz** ; ressac épars.
- **Contremarches** : le flanc d'une marche prend la couleur de flanc du matériau (pierre : granit clair / granit ombre ;
  herbe : vert sombre / forêt à l'atoll ; vert moyen / vert sombre à Machu Picchu depuis la retouche Fable, pour une forêt
  claire), selon qu'il regarde la lumière nord-ouest ou non.
- **Forêt** (retouche Fable, Machu Picchu) : **bouquets d'arbres sur une terre claire** (sol `GRASS_D`, clairières `GRASS_M`,
  sous-bois `FOREST` seulement par grandes plages et aux pieds de marche) ; l'ombre sur la forêt est un vert sombre
  `FOREST_SH` `#0F3620`, **jamais le bleu nuit `INK`** ; arbres semés en bouquets séparés par des vides.
- **Coupes** : une région du monde descend « comme un ascenseur » jusqu'à un socle de roche (en dalles de 2 unités depuis la passe A+B+C : les rayures d'une unité scintillaient en rasante ; une dalle sombre sur douze depuis la retouche Fable, plus de damier ; jamais l'encre, couleur du texte) ; ses parois montrent la
  coupe colorée par une fonction de la scène (strates à joints, gravier moucheté, tireté du niveau de la mer).
- **Nuages** (refaits le 18/11) : **tas de boules de coton** (couronne de 3–5 boules, 1–3 boules empilées au-dessus, parfois
  une boule sommitale), chaque boule dessinée au rayon projeté au pixel près, un peu aplatie en rasante, haut blanc,
  **modelé tramé en damier sur le tiers bas droit puis croissant plein gris-bleu tout en bas** (retouche Fable : la hachure
  une ligne sur deux se lisait comme un store), liseré bleuté au bas ; **ombres plates** des boules de la couronne,
  décalées selon l'altitude. Retouche Fable : **100 nuages** plus gros (rayon 11–20) dans le monde de l'atoll, **60**
  (rayon 9–16 × échelle) à Machu Picchu, 12–17 visibles par image en médiane ; contrôle géométrique : jamais plus de 5 %
  de l'anneau, de la coupe ou de la cité cachés par un nuage (passe A+B+C : 70 et 40 nuages ; passe de détail : 3 à 11
  et 3 à 7 dans le cadre) (C15 rouverte par le propriétaire le 18/11 ; passe de détail : 3 à 11 et 3 à 7 dans le cadre), à une seule altitude choisie **au-dessus de la caméra des
  plans rasants** (ils restent dans le ciel et ne passent jamais devant la coupe), et placés pour que la caméra ne les
  traverse jamais (contrôle sur tout le short).
- **Objets** : panneaux ASCII (frégate 31×10 en 2 images d'ailes, palmier 11×10, lama 24×22), jamais agrandis, avec ombre.
- **Cartouches** : rectangle crème, cadre encre 1 px, coin coupé d'un pixel, liseré crème extérieur 1 px, ombre plate (2, 2)
  par la table d'ombre (la même règle que les nuages). Plaque inversée : fond encre, cadre crème, texte or.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- **Caméra** : clés interpolées en **PCHIP** (cubique monotone, passe A+B+C ; avant : `inOutSine` / `linear` par segment) :
  la caméra vole sans à-coups, avance (vitesse médiane mesurée sur le prototype, avant le ralenti de Machu Picchu :
  14 unités/s à l'atoll, 52 à Machu Picchu) et vire avec un
  **roulis de 5–13°** (≥ 5° pendant 56–59 % du temps ; avant ≤ 3°). Piqué et remontée de Machu Picchu ralentis à 2,0 et
  2,2 s.
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
- **Cadrages** (passe A+B+C ; retouche Fable : l'accroche de l'atoll part de plus loin, 300 unités à 33°, et avance ; le
  plan final recule à 310 unités à 30° pour montrer l'anneau entier, la coupe et l'horizon) : **vol** à 25–40° de tangage (comprendre la forme et sentir le lieu à la fois : horizon,
  ciel en 7 paliers, resserrés vers l'horizon depuis la retouche Fable (0,4 / 1,2 / 2,4 / 4 / 6,5 / 10° puis le haut), et brume en haut de l'image, sujet en perspective au centre) ; **plan de coupe** lent à 19–25°, regardé
  de face (coupe d'une terrasse, tranchée de l'atoll). La plongeante 60–72° et la rasante 9–15° des preuves précédentes
  restent possibles (série `src/dive/`), mais ne sont plus utilisées dans les preuves.
- Caméra toujours au-dessus du relief (contrôle `--preflight` sur toutes les images : marge minimale 85,8 unités pour
  l'atoll, 41,6 à Machu Picchu, refait après la passe A+B+C).
- Profondeur de champ : aucune (tout net). La profondeur vient de la perspective, des flancs, des couches et des ombres,
  jamais d'un flou.

## Transitions (liste nommée, durée, quand les utiliser)
- **Le piqué** (signature) : la caméra descend vers le détail, distance et cible qui glissent, souffle (`whoosh`). Passe
  A+B+C : Machu Picchu 36° → 20° et distance 250 → 72 en **2,0 s** (8,0 → 10,0 s), ralenti par décision du propriétaire
  (0,6 s avant : 10–13 % de pixels A-B-A au prototype) ; atoll 37° → 27° pendant le retour en arrière. Série de preuve
  90/70/50/30/15° dans `src/dive/` de chaque short (régénérée) : aucun relief qui apparaît ou disparaît.
- **La remontée** : l'inverse, `whoosh` ; Machu Picchu 19° → 30° et distance 62 → 300 en **2,2 s** (13,4 → 15,6 s) ; atoll
  26° → 35–38°. Pour conclure ou changer d'échelle. Une coupe se regarde **de face** (cap perpendiculaire à la paroi),
  jamais par l'arête.
- **Le temps qui passe** : la caméra reste en vol pendant que le monde change par marches (retour en arrière 1 s,
  transformation 3,6 s). Les mentions « il y a des millions / d'années » et « pendant des millions / d'années » ont été
  retirées par le propriétaire (18/11, un seul cartouche à la fois) : la voix les dit.
- **La coupe qui s'ouvre** : une région descend jusqu'au socle en 0,8 s (`thud` discret).
- **Interdits** : traversée de nuage (non utilisée : risque de luminance, C13), mosaïque, fondu, coupe.

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
16–19 s, 3–5 vues de 3–5 s reliées par un vol continu, des piqués et des remontées (0,6–2,2 s), **un seul cartouche
Jersey 15 à la fois**, calé sur les débuts de mots de la voix, qui porte l'idée sans le son (≤ 6 mots).
- **0–1 s, hook** : la forme résultat ou le lieu, déjà en mouvement, et la question en Jersey 15 affichée entière dès
  0,12–0,15 s (mêmes mots-clés que la première phrase de la voix).
- **Développement** : piqué vers la rasante ; le mécanisme montré dans le paysage (coupe, transformation par marches,
  objet ombré) ; une étape par cartouche numéroté si besoin (« 1. », « 2. », « 3. »).
- **Chute** : remontée vers la plongée ou survol qui s'éloigne ; date / nom en plaque inversée.
- **Fin** : tenue ≥ 3 s sur l'image qui résume (l'anneau coupé avec le volcan dessous ; la cité dans la brume).
  Bouclable si la dernière vue rime avec la première.

## Zones sûres
Natives (×4 = final) : haut **55 (220 px)**, bas **80 (320 px)**, droite **30 (120 px)**, gauche **16 (64 px)**. Le moteur
vérifie chaque cartouche (boîte + liseré + ombre dans [16, 240] × [55, 400] natifs) et fait échouer le rendu sinon.
Cartouches centrés sur x = 128 (milieu de la bande sûre) ; récit en haut (y = 62), mentions en bas (bas à y = 398).

## Librairies recommandées et pourquoi
- **numpy 2.4.6** : tout le moteur — lancer de 4 rayons par pixel (marche à **pas sûrs** sur des cartes de maxima par
  blocs de 128, 32, 8 et 2, sinon pas géométriques, puis 8 bissections), intersection rayon–plan, vote majoritaire 2×2
  sur l'indice, cartes réduites, tables d'indices. Coût mesuré sur CPU après la retouche Fable : **63,9 s / 100 images**
  (atoll, seul, charge 3,4–3,8) et **214,43** (Machu Picchu, charge 2,9–5,0) ; passe A+B+C 107,18 et 266,29 (en
  parallèle, charge 4,4–10,4) ; passe de détail 19,6–63,1. Le plafond de coût a été levé par le propriétaire pour B (voir les `short.json`).
- **taichi 1.7.2** (facultatif, expérimental) : `src/survol_gpu.py` porte la seule marche des rayons sur GPU (Metal),
  activée par `SURVOL_GPU=1` ; image 1,5–1,9 s → 0,7–0,8 s. Pas identique au bit près (division Metal non IEEE, voir
  `out/report/facts.md`) : les rendus livrés sont sur CPU.
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
  volcan enfoui sous l'anneau ; frégate et son ombre ; d'autres atolls jusqu'à l'horizon (passe A+B+C).
- `out/shorts/survol-pixel__histoire__machu-picchu-pourquoi-une-cite-en-escaliers/` — « Machu Picchu : pourquoi une cité
  en escaliers ? » (18,8 s, reconstitution stylisée) : cité sur l'ensellement, terrasses à murs de pierre, entaille qui
  montre pierres / gravier / terre, pluie qui traverse, lama et son ombre.
- Comparaison avec la source : `out/report/notes/console-retro-source/comparaison.jpg` ; avant / après la passe A+B+C :
  `out/report/notes/console-retro-source/final-abc.jpg`.

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)
- **Voix : Gemini « Sulafat »** (décision du propriétaire du 18/11, comme le lot 2) : un appel `gemini-3.8-flash-tts` par
  short en **API v1beta** (la v1 renvoie 404 pour ce modèle), lignes de `narration.json` jointes par `<long pause>`, nombres
  en toutes lettres, style en annotation ; découpe en `voice_lines/NN.mp3` par horodatage des mots, mixage
  `tts.py --engine files --replace` (`short_novo.mp4` garde musique et bruitages). Passe A+B+C : même voix remixée sur les
  nouveaux temps, sans nouvel appel ; atoll −16,0 LUFS (crête −1,7 dBFS), Machu Picchu −13,8 LUFS (crête −1,5 dBFS)
  (avant : −15,9 et −13,7). Journal : `out/report/notes/voix-survol-pixel.md`. Le texte à l'écran porte toujours l'histoire sans le son.
- Une phrase par vue, **≤ 2,6 mots/s en mots prononcés** (« 1842 » = 4–5 mots ; 2,2–2,6 mesurés) ; **silence pendant les
  piqués et les remontées** (le souffle porte la transition). Enfants : 2,0–2,3 mots/s, vues de 4 s.
- La première phrase reprend les mots-clés de l'accroche à l'écran (C20).
- Le visuel laisse la voix dire les nombres et les causes ; l'écran ne garde que l'idée en ≤ 6 mots.

## Risques et limites
- **Lisibilité** : Jersey 10 (capitale 40 px) réservée aux mentions ; tester une image réduite à 360 px de large.
- **Scintillement en mouvement (risque principal depuis la passe A+B+C)** : la passe a supprimé les bascules de matière
  (remontée de Machu Picchu : 1,66 % → 0,21 % de points du monde qui changent de matière ; grands sauts de couleur 1,5 % →
  0,1–0,4 %) et les « cubes » (biais de pente et règle « mur lointain = couleur du dessus » supprimés), mais le
  **crénelage monte** : contremarches et dessus en bandes de 1 px sur les pentes lointaines, sous une caméra deux fois plus
  rapide qui vire. Pixels A-B-A (aller-retour sur 3 images) sur les fichiers décodés, même méthode que la source (4,0 %) :
  Machu Picchu **3,56 %** sur tout le short (1,40 % avant la passe), **7,3 %** pendant le piqué ralenti, **5,4 %** pendant
  la remontée, 6,7 % au survol de 6,5–7,5 s ; atoll 1,06 % (0,38 % avant), 2,6 % au plus. Mesure native du prototype
  (piqué 13,3 %, remontée 10,1 %) : 7,8 % et 7,1 % aux mêmes instants après le ralenti. Le ralenti a donc presque divisé
  par deux le scintillement des transitions, qui reste au-dessus de la source. Leviers restants : marches naturelles plus
  hautes au loin, virages plus lents ; re-mesurer après tout changement de caméra.
- **Coupe** : la regarder de face (cap perpendiculaire à la paroi), garder les épingles pendant toute la tenue, socle en
  roche (dalles) assez haut pour rester < 5 % de l'image ; vue par l'arête, elle se lit comme un « trou noir ».
- **Gros texels près de la caméra** : en rasante très proche, une cellule du monde fait jusqu'à 7 px natifs. Depuis la
  passe A+B+C, la carte de couleurs fine (4 cases par cellule) autour du sujet casse les grands carrés de couleur (elle
  remplace le micro-détail de la passe de détail), mais la **géométrie** reste en cellules : les bords de terrasse vus de
  près gardent un escalier régulier. Garder la caméra à ≥ 60 unités d'une coupe,
  ou affiner la grille du monde (Machu Picchu : ×1,8).
- **Densité contre scintillement** : plus de détail = plus de pixels qui changent quand la caméra tourne. Mesuré à la
  passe de détail : moucheture à 1 pixel par cellule +0,9 point ; mesuré au prototype A+B+C (à 7 s, en coupant chaque
  élément) : réduction de carte et moucheture sans effet, arbres −0,9 point, vote 2×2 −0,15 point : c'est la géométrie
  (marches de 1 px au loin) qui scintille. Re-mesurer après tout changement de détail ou de caméra.
- **Coût** : après la retouche Fable, **63,9–214,4 s / 100 images** sur CPU (4 rayons par pixel, mondes 3× et
  2,4× plus grands, carte fine ; passe A+B+C 107,18–266,29 sous une charge plus forte ; passe de détail 19,6–63,1), soit
  1,1–3,6 fois le plafond de 60 s/100 du challenge, levé par le propriétaire pour B. Un short de 19 s prend 6 min (atoll)
  à 20 min (Machu Picchu) sur 4 cœurs partagés. Pistes :
  recalculer le monde à 15 Hz pendant l'enfoncement de l'atoll, alléger `ground` ; la marche sur GPU (`SURVOL_GPU=1`)
  divise le temps par image par 2 environ mais n'est pas identique au bit près. Repli prévu : volumes en « sprite stacking ».
- **Relief en marches = convention de dessin** : les terrasses d'un volcan ne sont pas un fait ; le dire à l'écran
  (Jersey 10) quand le public est jeune.
- **Confusions possibles** : pixel-arcade (même grille ×4 : on s'en sépare par le plein jour, la perspective, les
  ombres, Jersey et les cartouches crème), carte-meteo (mer bleue vue de haut : notre océan est profond et saturé,
  luminance moyenne d'image Y mesurée sur les fichiers finaux de la passe A+B+C : moyenne 0,47 (atoll) et 0,48 (Machu
  Picchu), maximum 0,51–0,52, contre 0,77 ; la caméra vole sous 40° tout le temps), topo-relief (survol de relief : courbes sombres,
  plein jour, aucune lecture d'altitude). Ressemblance avec *Pilotwings* (Mode 7 sur île) : aucun élément de jeu.
- **Photosensibilité** : aucune image pleine en blanc, écume à 2 Hz, battement d'ailes à 3 Hz, pas de traversée de nuage ;
  variation de luminance moyenne mesurée sur les fichiers finaux (voir `short.json.qualityChecks`).
- **Lieux réels** : toujours « reconstitution stylisée » ; aucune géométrie réelle prétendue ; faits sourcés dans
  `short.json`.
