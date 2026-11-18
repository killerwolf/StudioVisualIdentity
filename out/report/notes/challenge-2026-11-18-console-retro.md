# Challenge adversarial de la direction « survol pixel » (ex-console-retro), 2026-11-18

Étape 3 du skill `fabrique-identites`. Direction attaquée : `directions-2026-11-18-console-retro.md`, slug proposé `survol-pixel`.

Ce que j'ai lu :
- le brief, l'analyse de la source et ses images (planche-contact, image 4,3 s) ;
- `console-retro-setup.md`, `facts.md`, `failures.md` et `sound.py` ;
- `index.json` et les planches-contacts de pixel-arcade, carte-meteo, topo-relief et pastel-diorama.

Ce que j'ai mesuré moi-même :
- dans le scratchpad de la session, hors dépôt, sans rien installer ni commiter ;
- sur ce Mac Intel 4 cœurs, avec une charge `uptime` de **7 à 13** au moment des mesures. C'est moins que les 20–35 de la direction : mes temps ne sont donc pas « sous la même charge » que les siens.

## Verdict : **MODIFIER** (garder la direction, avec 20 corrections obligatoires)

- **Ce qui tient :**
  - la direction répond à l'esprit des quatre exigences ;
  - le moteur Python image par image est réaliste ;
  - Jersey est un bon choix, et le problème de grille de Jersey 10 n'existe pas en pratique (voir C8) ;
  - les contrastes de texte annoncés sont justes, je les ai tous recalculés à l'identique.
- **Ce qui ne tient pas en l'état :**
  1. **Le moteur proposé ne sait pas faire la transition signature.** Le « voxel space » par colonnes simule le tangage en décalant l'horizon. Il ne peut pas basculer continûment de 90° à 15°. Le « piqué », trait n° 3 de la signature, n'est pas réalisable tel qu'écrit.
  2. **La vue de dessus est orthographique, donc plate.** C'est en tension directe avec R1 (« no flat 2D rendering »).
  3. **Les deux textes de voix sont trop longs.** Ils font 46 et 50 mots écrits, et non 41 et 44. Trois lignes dépassent le seuil de 3,2 mots/s de `check.py`.
  4. **Plusieurs éléments rapprochent l'identité des voisines** : la plaque HUD phosphore de pixel-arcade, la lecture « ALT 2 430 M » sur un relief en terrasses de topo-relief, et la même grille 270×480 ×4 que pixel-arcade.
  5. **Il y a deux erreurs de fait** (atoll) et deux formulations excessives (Machu Picchu).

## Verdict par exigence du propriétaire

| Exigence | Verdict | Motif |
|---|---|---|
| **R1** : vraie profondeur 3D pixel art | **Partiellement satisfaite, à corriger** | Sol Mode 7, terrasses, parallaxe, ombres et caméra qui avance sont bien prévus. Deux défauts. (1) La vue de dessus à 90° orthographique est un rendu 2D plat avec des ombres : il faut une vraie caméra perspective inclinée (C1, C2). (2) Le moteur de relief choisi ne peut pas suivre le piqué : il faut un modèle de caméra unique (C1). Gros pixels, palette limitée et hachures : OK. |
| **R2** : la forme, pas le contenu ; tout sujet ; 2 familles hors `engagement` | **Satisfaite sur le papier, preuve faible** | Les familles `explicatif` et `histoire` sont hors jeu et hors avion, et il y a des recettes pour 5 familles. Mais **les deux preuves sont des survols de paysage**, le cas où la forme va de soi. Rien ne prouve un personnage, un objet ni un sujet sans paysage. Et l'atoll reprend le **décor même de la source** (mer tropicale, île verte, nuages hachurés) : C14, C15, C16. |
| **R3** : distincte de pixel-arcade, pas confusable avec carte-meteo ni topo-relief | **Partiellement satisfaite** | Le statut de « nouvelle identité » est bien justifié face à pixel-arcade, car le moteur, l'espace et les polices diffèrent. En revanche : (a) **la grille de gros pixels est la même** : pixel-arcade rend aussi en 270×480 ×4 (`facts.md` l. 70) et quantifie son mouvement à 4 px. Ce n'est donc pas une différence, contrairement au § 8.1. (b) La plaque HUD `#062A1C` avec chiffres phosphore et or reprend le code de pixel-arcade (`#3CF2A0` et `#FFD23F` sur `#0E0B1F`). (c) « ALT 2 430 M » sur une crête en terrasses survolée par une caméra drone, c'est littéralement la signature de topo-relief (« drone fly-over camera », « altitude readout »). Correctifs C10, C11, C12. Face à carte-meteo, la différence de luminance est forte (océan 0,10 contre 0,77) : OK. |
| **R4** : rien de copié de la source ni d'un jeu | **Satisfaite, avec deux vigilances** | Avion, cockpit, texte d'interface et formes de carte sont bien exclus. Vigilances : (1) l'atoll en vue de dessus risque de reproduire la *composition* de la source (C15) ; (2) un survol d'île en Mode 7 évoque d'emblée *Pilotwings* (SNES). Pas d'anneaux à traverser, de piste d'atterrissage, de score ni de mélodie qui cite un jeu (C17). |

## Constats chiffrés (mes mesures)

1. **Coût du moteur.** Prototypes numpy à 270×480, carte de hauteurs 1024², charge 7–13 :

   | Méthode | Temps par image | Pour 100 images | Ce qu'elle sait faire |
   |---|---|---|---|
   | voxel space par colonnes, 200 pas | 0,096 s | ≈ 10 s | tangage limité (décalage d'horizon) : **ne fait pas le piqué** |
   | voxel space par colonnes, 120 pas | 0,063 s | ≈ 6 s | idem |
   | lancer de rayon par pixel sur la carte de hauteurs, 96 pas géométriques | 0,59–0,72 s, quel que soit le tangage (89°, 50°, 15°) | ≈ 60–70 s | **tout tangage**, avec le flanc des terrasses visible |
   | table de palette + agrandissement ×4 + `tobytes` | 0,022 s | ≈ 2 s | — |

   Pour comparer : topo-relief coûte 108–169 s pour 100 images, pastel-diorama 66–83.
   - Le lancer de rayon partout donne ≈ 5 min de rendu pour un short de 16 s : acceptable.
   - Le lancer de rayon réservé aux 15 images d'un piqué ajoute ≈ 10 s : négligeable.
   - L'estimation de la direction (10–30 s pour 100 images) n'est réaliste que si le relief n'est pas lancé par pixel.

2. **Polices Jersey 5.3.0.** Version publiée le 19/07/2026 : l'épinglage exact est possible et elle a plus de deux semaines. Mesures avec fontTools sur les `.woff` du registre npm, puis rendu PIL `fontmode = "1"` :
   - **grille** : 75, 50 et 38 unités par pixel, soit 18,667, 27 et 34 px par em. Capitales de 10, 15 et 20 px natifs. Confirmé ;
   - **rendu de Jersey 10 à `size = 56/3`** : sur 98 glyphes (A–Z, a–z, chiffres, accents, œ, « », ponctuation), le nombre de pixels encrés est **égal au nombre exact** calculé sur le contour, pour les trois tailles. **0 écart.** La solution (a) ou (b) du § 4.3 est inutile, à condition de poser le texte sur des coordonnées entières ;
   - **largeur moyenne d'une bas-de-casse** : 7,0, 10,8 et 14,0 px natifs. La direction annonçait 6,3, 9,4 et 12. Ses nombres de lettres par ligne sont donc trop optimistes de 10 à 15 %. Par ligne de 214 px : **≈ 30, ≈ 20 et ≈ 15 caractères** ;
   - **chaînes prévues qui débordent** de 214 px :

     | Chaîne | Police | Largeur native |
     |---|---|---|
     | « UN ANNEAU EN PLEINE MER ? » | Jersey 20 | **353** |
     | « ATOLL = ANCIEN VOLCAN » | Jersey 20 | **295** |
     | « ATOLL = ANCIEN VOLCAN » | Jersey 15 | **222** |
     | « DES MILLIONS D'ANNÉES » | Jersey 15 | **223** |

     Les coupes qui tiennent : « UN ANNEAU / EN PLEINE MER ? » = 140 / 206 ; « DES MILLIONS / D'ANNÉES » = 127 / 90 ;
   - **accents** : le haut de « É » est à 14, 20 et 25 px natifs, contre une capitale de 10, 15 et 20. Il faut 4 à 5 px de plus que la capitale au-dessus du texte ;
   - **glyphes absents** : ² ³ ±. Confirmé.

3. **Contrastes.** Les 10 valeurs du § 3.5 sont exactes. Ce que la direction ne regarde pas, ce sont les contrastes **non textuels** (WCAG 1.4.11, ≥ 3:1 pour un repère graphique utile) :

   | Couple | Contraste | Conséquence |
   |---|---|---|
   | rouge brique `#B5341A` (marqueur, flèche au sol, dirigeable) sur océan `#1E5AA8` | **1,13** | |
   | même rouge sur océan moyen | 1,25 | |
   | même rouge sur herbe `#5DB534` | 2,34 | invisible en luminance, et pour un daltonien deutéranope |
   | ombre de cartouche `#143F7E` sur océan | **1,51** | l'ombre ne se voit presque pas |
   | cadre encre `#14213D` sur cette ombre | 1,55 | |
   | crème de cartouche sur brume dorée | **1,16** | le cartouche ne se détache que par son cadre de 1 px |
   | crème de cartouche sur nuage | **1,09** | idem |
   | crème de cartouche sur lagon | 1,63 | idem |
   | or `#FFC94A` sur crème | **1,38** | |

4. **Débit de la voix**, mots écrits (nombres comptés comme mots prononcés), sur la fenêtre de chaque plan :

   | Ligne | Mots écrits | Fenêtre | Débit écrit | Débit, nombres prononcés |
   |---|---|---|---|---|
   | A1 | 9 | 3,3 s | 2,7 mots/s | |
   | A2 | 14 | 3,8 s | **3,7 mots/s** | |
   | A3 | 11 | 3,8 s | 2,9 mots/s | |
   | A4 | 12 | 4,3 s | 2,8 mots/s | **4,2 mots/s** (« mille huit cent quarante-deux ») |
   | M1 | 12 | 3,4 s | **3,5 mots/s** | **4,4 mots/s** (« deux mille quatre cent trente ») |
   | M2 | 10 | 3,7 s | 2,7 mots/s | |
   | M3 | 15 | 4,3 s | **3,5 mots/s** | |
   | M4 | 13 | 4,6 s | 2,8 mots/s | 3,7 mots/s |

   - Totaux : **46 mots** pour l'atoll (annoncé ≈ 41), **50 mots** pour Machu Picchu (annoncé ≈ 44).
   - Cible : 2,6 mots/s, sur une fenêtre réduite des transitions et des respirations.

## Corrections obligatoires pour le studio

### Moteur et profondeur (R1)

**C1. Un seul modèle de caméra sténopé pour tout le short** : position (x, y, alt), cap, tangage et roulis.
- **Sol plat** : intersection rayon–plan en forme close, par pixel ou par ligne. Elle couvre aussi le tangage de 90°. C'est le « Mode 7 » généralisé.
- **Relief**, au choix, à mesurer dès le premier jour sur 30 images :
  - (a) lancer de rayon par pixel sur la carte de hauteurs. Mesuré ici à 0,6–0,7 s par image ; budget **≤ 60 s pour 100 images** sous la charge notée, sinon passer à (b) ;
  - (b) la variante B, des volumes en *sprite stacking* : décalage des tranches proportionnel à cos(tangage), valable à tout tangage.
- Le « voxel space » par colonnes **n'est autorisé que si le tangage reste ≤ 35° pendant tout le plan**. Il est interdit dans un piqué.
- **Interdiction de changer de moteur de relief au milieu d'un plan** : sans coupe ni fondu, le changement se verrait comme un saut.
- Preuve à fournir dans `src/` : une série de 5 images fixes du piqué, aux tangages 90°, 70°, 50°, 30° et 15°, sans relief qui apparaît ou disparaît d'un coup.

**C2. La « vue de dessus » devient une vue plongeante à 65–80° en perspective**, pas une projection orthographique à 90°.
- On doit y voir le **flanc sombre** des terrasses (contremarche colorée en ombre au point d'impact du rayon sur une paroi) et la parallaxe des nuages.
- Le 90° exact n'est permis que **≤ 0,5 s**, au milieu d'un mouvement.
- Règle mesurable : chaque image fixe montre au moins 2 indices de profondeur, **dont au moins un géométrique** (horizon visible, flanc de terrasse, ou objet dont la hauteur projette une ombre). Les ombres de nuages seules ne suffisent pas.

**C3. Anticrénelage du lointain : une carte réduite pour le lointain, et ce n'est plus une option.**
- Au-delà de la distance où une cellule de carte fait moins d'un pixel d'écran, on échantillonne une carte réduite (moitié, quart), calculée par vote majoritaire d'indices, sans moyenne, pour rester dans la palette.
- Raisons :
  - le scintillement des rayures vertes en terrasses près de l'horizon fait un motif rayé en mouvement sur une grande surface (risque de photosensibilité, voir C13) ;
  - il fait exploser le débit H.264.

**C4. Les objets en panneaux (« billboards ») ne sont jamais agrandis au-delà de 1:1.**
- Un agrandissement créerait des pixels plus gros que la grille : des « mixels », qui cassent le trait n° 1 de la signature.
- Au plus près, on dessine la plus grande taille faite à la main et on borne la distance de caméra, ou on passe l'objet en *sprite stacking*.

### Texte, polices et lisibilité

**C5. Rôles des polices :**
- **Jersey 20 (`size = 34`)** : accroche et mot géant ;
- **Jersey 15 (`size = 27`)** : tout le texte de récit et les étiquettes ;
- **Jersey 10 (`size = 56/3`)** : seulement les mentions secondaires d'une ligne (« reconstitution stylisée », source), jamais le récit.
- Au plus **2 lignes par cartouche**, et **≤ 214 px natifs** par ligne, mesurés avec `ImageFont.getlength` dans le code. Une assertion fait échouer le rendu en cas de dépassement.
- Corriger le § 4.1 : ≈ 30, 20 et 15 caractères par ligne.

**C6. Hauteur de ligne = em complet** (19, 27 et 34 px natifs) et marge intérieure haute ≥ 5 px natifs. Sinon les accents des capitales (É, È, À, Ç) touchent le cadre. Vérifier « ÉTAPE », « SIÈCLE » et « ANNÉES » sur image fixe.

**C7. Réécrire les cartouches qui débordent :**
- « UN ANNEAU / EN PLEINE MER ? » (2 lignes) ;
- « DES MILLIONS / D'ANNÉES » ;
- « ATOLL = ANCIEN VOLCAN » est supprimé (voir C18).

L'accroche est **affichée entière dès 0,3 s**, ou tapée à ≥ 40 caractères/s. À 30 caractères/s, elle ne serait complète qu'à ≈ 1,1 s, alors que la règle demande une accroche visible en moins de 1 s.

**C8. Jersey 10 : supprimer l'alternative (a)/(b) du § 4.3.**
- PIL `fontmode = "1"` à `size = 56/3`, sur origine entière, rend exactement la grille : 0 écart sur 98 glyphes.
- Garder dans `src/` un **test de non-régression** :
  - pour chaque glyphe, le nombre de pixels encrés est égal à l'aire du contour divisée par 75² ;
  - pour une ligne entière, l'encre totale est égale à la somme de ses glyphes, pour attraper un crénage qui déplacerait d'un pixel.
- Toutes les positions de texte sont des entiers natifs.

**C9. Aucun texte dessiné dans la carte projetée.**
- La perspective écrase les lettres (1,6–2 lignes par motif près de l'horizon) : illisible.
- Les étiquettes « au sol » (TERRE, GRAVIER, PIERRES) sont des cartouches à l'écran en Jersey 15, reliés à une **épingle ancrée au sol** (point projeté) par un trait de 1 px.
- Les flèches et la coupe peuvent rester dans la carte, sans lettres.

### Distinction avec les voisines (R3)

**C10. Supprimer la plaque HUD phosphore.**
- Le vert `#7DF5A5` et l'or sur fond quasi noir, en police pixel, c'est le HUD de pixel-arcade.
- Les chiffres et dates vont sur un **cartouche inversé** : encre `#14213D`, chiffres crème `#FBF3D5` (14,36:1) ou or `#FFC94A` (or sur encre ≈ 10:1), cadre crème de 1 px et même ombre portée que les cartouches.
- Une seule plaque à l'écran, et **pas plus de 25 % de la durée** du short.

**C11. Interdire le motif « ALT … M ».**
- Une lecture d'altitude sur relief en terrasses survolé, c'est la signature de topo-relief.
- L'altitude de Machu Picchu passe dans la voix et dans un cartouche de récit (« À 2 430 m »), pas en lecture d'instrument.
- Les courbes de niveau restent **sombres** et le ciel de jour toujours visible dans la vue rasante. Aucune ligne claire ou lumineuse sur fond sombre.

**C12. Corriger le § 8.1 : la grille 270×480 ×4 n'est pas une différence avec pixel-arcade**, qui a la même.
- La différence doit tenir sur la perspective, la lumière du jour, les ombres portées, les cartouches crème et Jersey.
- Règle mesurable : **≥ 50 % de la durée avec un horizon visible ou un relief en perspective** (tangage ≤ 60°), écrit dans `short.json.qualityChecks`.

### Photosensibilité

**C13. Trois règles.**
- **Traversée de nuage** : 0,4 s ne permet pas une montée ≥ 0,3 s *et* une descente. Au choix :
  - (a) durée ≥ 1,2 s, couverture blanche ≤ 70 % de l'image grâce à la hachure, et luminance moyenne qui ne varie jamais de plus de 0,2 en 1/3 s ;
  - (b) supprimer cette transition.
  - Au plus une par short, et toujours ≥ 1,6 s d'une autre forte variation de luminance.
- **Écume** : scintillement **≤ 3 Hz** (règle du dépôt : au plus 3 flashs par seconde), pas 4.
- **Rayures en terrasses** près de l'horizon : pas de motif rayé régulier à 1 px sur plus de 25 % de l'image en mouvement (voir C3).

### Preuves, contenu et faits (R2, R4)

**C14. Chaque short contient au moins :**
- un **objet ou personnage original dessiné à la main en code**, avec sa propre ombre portée dont le décalage encode la hauteur. Atoll : par exemple un banc de poissons-perroquets ou une pirogue. Machu Picchu : par exemple un lama, ou un paysan en silhouette ;
- un **schéma posé au sol**. Pour l'atoll : la coupe volcan / récif / niveau de la mer, présentée comme une maquette. Pour Machu Picchu : la coupe de terrasse, déjà prévue.

Sans eux, R2 (« sets, characters, objects ») n'est pas prouvé.

**C15. Atoll : il ne faut pas reproduire la source.**
- Interdits : un archipel d'îles éparses et un ciel semé de nuages façon source.
- Un seul sujet centré : volcan, puis anneau.
- **Au plus 4 nuages à l'écran.**
- Biome tropical avec sable, corail et roche bien visibles.
- Vérification : comparer côte à côte 3 images fixes du short avec `console-retro-source/contact-sheet.jpg`. Si l'on peut confondre une image avec la source, on refait la composition.
- La règle « océan > 45 % des pixels » cesse d'être un garde-fou de signature : elle lierait l'identité aux îles, contre R2. Elle reste vraie pour l'atoll seulement, et le garde-fou contre carte-meteo devient C12 plus la luminance (R1 dans la revue).

**C16. Dans `identity.md`, ajouter une section « sujet sans paysage »** avec 3 exemples travaillés :
- un organe ou une machine devient un **monde-maquette**. Par exemple, le cœur devient une île à deux bassins, et les flèches au sol montrent la circulation ;
- un événement d'histoire en ville : plan de la ville en terrasses, foules en silhouettes ;
- une notion abstraite : une frise du temps posée au sol comme une route que la caméra suit.

Pour chacun : la carte, les panneaux, le schéma au sol, et le moment du piqué.

**C17. Ne rien emprunter à un jeu existant.**
- Pas d'anneaux à traverser, de piste ni de marques d'atterrissage, de score, de compte à rebours de jeu.
- Musique générée par `sound.py` sans motif mélodique qui rappelle une musique de jeu connue.
- `sound.py` n'accepte **qu'un seul `music.preset`** : choisir `drone` *ou* `pad` (proposé : `pad` en `lydian`), pas les deux.
- Les événements sonores retenus (`whoosh`, `swell`, `chime`) existent bien.

**C18. Faits de l'atoll à corriger :**
- « Darwin l'avait deviné en 1842 » devient « Darwin l'a expliqué en 1842 ». Il a conçu la théorie vers 1836, pendant le voyage du *Beagle* ; 1842 est la date du livre.
- **Le volcan ne « disparaît » pas** : il s'enfonce et reste **sous** le récif. C'est tout le sens des forages d'Enewetak (1952, basalte atteint sous ≈ 1 200–1 400 m de calcaire).
  - La voix devient par exemple « Le volcan a sombré ; l'anneau de corail est resté à la surface ».
  - L'image finale montre, dans la coupe au sol, le volcan enfoui sous le récif.
  - Le cartouche « ATOLL = ANCIEN VOLCAN » est remplacé par « UN VOLCAN / SOUS L'ANNEAU ».
- **Montrer les 3 étapes** : récif frangeant, récif-barrière avec lagon, atoll. Sinon le « ÉTAPE 1 » n'a pas de suite.
- Le **niveau de la mer reste fixe** à l'écran pendant que le volcan descend : c'est le mécanisme à comprendre.
- Ajouter un cartouche Jersey 10 « relief en marches : convention de dessin ». Les terrasses d'un volcan sont un style, pas un fait, et les enfants pourraient le croire.

**C19. Faits de Machu Picchu à corriger :**
- « la montagne ne glisse pas » devient « la pente tient » ou « la terre ne part pas avec la pluie ». Les terrasses réduisent l'érosion et les glissements, elles ne les suppriment pas : le site reste surveillé pour ses glissements de terrain.
- « Les Espagnols ne l'ont jamais trouvée » devient « Les Espagnols ne semblent pas l'avoir atteinte ». Des documents coloniaux mentionnent le lieu, et des habitants y vivaient en 1911.
- « taillent la montagne » devient « bâtissent des terrasses » : ce sont des murs de soutènement remblayés.
- Ordre des couches, de bas en haut : **pierres, gravier, terre**. Confirmé.
- Rien sur la résistance aux séismes (affirmation souvent exagérée), ni nombre de terrasses, ni pourcentage « souterrain ».
- On garde « XVe siècle » (Pachacutec, et les datations au radiocarbone de 2021 donnent une occupation dès ≈ 1420), « ≈ 2 430 m » et « révélée au monde en 1911 ».

**C20. Débit et durée.**
- **≤ 2,6 mots/s par ligne**, nombres comptés en mots prononcés, sur la fenêtre réelle de la ligne (fenêtre du plan moins la transition et 0,3 s de respiration).
- Concrètement : **≈ 38–40 mots** pour 16–17 s, ou allonger les shorts à **18–19 s** (le plafond de `check.py` est 20,1 s).
- Lignes à réécrire en priorité : A2, A4, M1 et M3.
- Pour un spectateur sans le son : **un cartouche par plan qui porte l'idée du plan en ≤ 6 mots** (Jersey 15, ≤ 2 lignes). « ÉTAPE 1 » seul ne suffit pas.
- Le texte de l'accroche et le début de la voix disent la même chose avec les mêmes mots-clés : pas « anneau en pleine mer » à l'écran et « anneau de corail en plein océan » à la voix.

### Livrable

Deux règles de livraison, qui font partie de C3 et C20 pour la numérotation :
- **Encodage du livrable** selon la règle du dépôt : `assemble.py mux`, crf 20, maxrate 8 Mb/s (et non les « 8–12 Mb/s » du § 10.3). Poids `short.mp4` ≤ 15 Mo.
- `renderTimeSec` mesuré avec `time`, et `uptime` noté dans `renderCostNote`.

## Améliorations facultatives

1. Remplacer l'atoll par un sujet explicatif **hors île tropicale**, pour prouver R2 plus franchement et s'écarter de la source. Exemple : « Comment une dune avance-t-elle ? », biome désert. Atoll et Machu Picchu montreraient alors deux biomes différents de la source, au lieu d'un seul.
2. Faire du guide original (le dirigeable) un **personnage récurrent** dans la recette `enfants`, et le montrer dans une image fixe de `identity.md`.
3. Donner aux cartouches un **cadre crème de 1 px à l'extérieur du cadre encre**, quand ils passent sur la brume ou les nuages (contraste 1,09–1,16 sinon).
4. Inscrire la technique (« numpy : caméra sténopé, sol Mode 7 et relief en carte de hauteurs ») comme nouvelle ligne du catalogue : c'est la « combinaison jamais faite » qui ancre la direction (`catalogue.md`).
5. Un preset `pad` à la gamme `lydian`, avec un `swell` à chaque arrivée de lieu, suffit. Éviter `pulse` : il ramène vers le chiptune de pixel-arcade.

## Contrôles que la revue finale doit faire

1. `check.py` sur les 2 shorts : `ok`, **0 avertissement de débit** (> 3,2 mots/s).
2. **Profondeur.** Sur ≥ 6 images fixes par short, au moins 2 indices de profondeur, dont un géométrique (C2). Un horizon ou un relief en perspective est visible sur ≥ 50 % de la durée, à vérifier par l'échantillonnage du tangage déclaré dans `short.json`.
3. **Piqué.** Les 5 images à 90°, 70°, 50°, 30° et 15° (C1) : pas de saut de relief, la grille est respectée (aucun pixel plus gros que 4×4 à l'écran, pour C4).
4. **Palette.**
   - Compter les couleurs distinctes de chaque image fixe à la résolution native : ≤ 20 en vue plongeante, ≤ 32 en vue rasante.
   - Vérifier que toutes appartiennent à la table de palette déclarée.
5. **Texte.**
   - Aucune ligne de plus de 214 px natifs, au plus 2 lignes par cartouche.
   - Accents non rognés.
   - Test de grille Jersey 10 présent et vert (C8).
   - Une image fixe réduite à 360 px de large doit rester lisible.
6. **Contrastes.** Texte ≥ 4,5:1 sur son fond réel. Les marqueurs graphiques ont un liseré qui leur donne ≥ 3:1 contre le terrain (constat chiffré 3 ; amélioration facultative 3).
7. **Photosensibilité.**
   - Variation de luminance moyenne image par image (≤ 3 transitions fortes par seconde, aucune image pleine en blanc) ;
   - écume ≤ 3 Hz ;
   - pas de grand motif rayé scintillant près de l'horizon (C13).
8. **Reconnaissance.**
   - Juge aveugle : les nouvelles images contre pixel-arcade, carte-meteo, topo-relief et la source. Chaque short doit être rangé avec son frère.
   - `recognition.py` sur une copie : le plus proche voisin de chaque short est son frère.
   - La luminance moyenne des vues plongeantes reste très en dessous de 0,77 (carte-meteo).
9. **Source.** Comparaison côte à côte avec `console-retro-source/contact-sheet.jpg` (C15) : aucune image confondable, ni avion, ni cockpit, ni ligne d'aide, ni archipel copié.
10. **Faits.** Les textes finaux contiennent les formulations de C18 et C19, et la mention « reconstitution stylisée » figure dans le short Machu Picchu.
11. **Coût.** `renderTimeSec` et `uptime` renseignés ; le moteur de relief retenu (a ou b de C1) est justifié par la mesure.
12. **Poids.** `short.mp4` ≤ 15 Mo par short.
13. **Polices** : `@fontsource/jersey-10`, `jersey-15` et `jersey-20` épinglées à `"5.3.0"` exact dans `package.json`, sous-ensemble `latin` seulement.
