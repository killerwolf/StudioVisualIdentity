# Survol pixel : passe de détail (18/11/2026) — diagnostic chiffré, corrections, avant / après

Demande du propriétaire, après la planche `console-retro-source/comparaison.jpg` : « la vidéo d'origine est beaucoup plus
détaillée ; la nôtre est moins jolie, plus carrée, moins bien définie. Refais. »
Planche avant / après : `console-retro-source/comparaison-avant-apres.jpg` (pour chaque short : source 4 images, avant 5,
après 5). Images « avant » conservées dans `console-retro-source/avant/` (extraites des `short.mp4` d'avant aux instants des stills ;
Machu Picchu n'a que 4 stills, la 5e image est prise à 3,0 s ; md5 atoll
`a40c8f88a5fa53d882cd22759ba467be`, Machu Picchu `3a0cd79b335b8947263941c498f036bf`).

## Méthode

Scripts dans le scratchpad de la session (hors dépôt). La vidéo source est lue comme donnée, jamais copiée.

- **Source** : grille reconstituée (pas 3,939 px, phase 3,5 ; 2,5) → 377 × 261 cellules (la ligne d'aide du bas est
  retirée), 30 i/s. Les mesures de la source restent gonflées par le H.264, l'avion et les traînées : compacité k-means
  < 1 et gradients un peu surestimés.
- **Nous** : (a) **natif du moteur** (indices exacts, 1 image sur 10, rendu avec puis sans cartouches, ce qui donne la part
  exacte d'écran couverte par les cartouches) ; (b) **fichier final** décodé, échantillonné au centre des blocs 4 × 4.
- Indicateurs par image (médianes) :
  - `diffCells` : part des cellules qui diffèrent d'une voisine de plus de 24 sur un canal ;
  - `grad` : énergie moyenne du gradient de luminance ;
  - `flat1` / `flat5` : part de l'écran couverte par des aplats connexes d'une même couleur (k-means 16) de plus de 1 % / 5 % de l'écran ;
  - les objets (règles HSV) :
    - nuages : blanc ≥ 25 cellules ;
    - écume : blanc de 1 à 6 cellules ;
    - arbres : vert sombre de 3 à 60 cellules ;
    - îles : terre ≥ 30 cellules.
- **Mouvement** :
  - vitesse de caméra par corrélation de phase (la méthode de l'analyse) ;
  - part de pixels qui changent par image (seuil 24) ;
  - pixels **A-B-A**, qui partent et reviennent en 3 images : la signature du crénelage, à distinguer du simple défilement.

## 1. Diagnostic (avant)

### 1.1 Grille

| | Source (paysage) | Survol pixel (portrait) |
|---|---|---|
| Gros pixel | 3,94 px | 4 px |
| Rapporté à la largeur / hauteur | 1/377 / 1/274 | 1/270 / 1/480 |
| Cellules sur la plus petite dimension | 274 (hauteur) | 270 (largeur) |
| Affichées à la même largeur (téléphone tenu droit) | 377 cellules | 270 cellules : nos pixels paraissent 1,4 × plus gros |

**Test A/B de grille** : même image, sans cartouches, à 270×480 ×4 et à 360×640 ×3, focale ×4/3 pour garder le champ, avec le
vrai passage x264 en yuv420p.

| | ×4 (actuel) | ×3 |
|---|---|---|
| Coût par image (atoll 0,5 s / Machu Picchu 7 s) | 91 / 409 ms | 145 / 775 ms (×1,6–1,9) |
| Pixels décodés à plus de 24 de leur couleur (chroma 4:2:0 à cheval sur les cellules de 3 px) | **0 %** | **1,1–1,2 %** (bavure de couleur) |
| `diffCells` natif (même monde) | 0,101 / 0,216 | 0,086 / 0,180 |

→ **La grille n'est pas l'écart principal, et le ×3 est rejeté** : il fait baver la chroma (on perd le « pas de flou »), coûte
×1,6–1,9 et donne *moins* de détail par cellule tant que le monde n'a pas plus de contenu. L'intuition de l'orchestrateur est
confirmée : le passage à une grille plus fine n'aide qu'avec un monde plus riche, et c'est le monde qui manquait.

### 1.2 Netteté de bout en bout

Sur les fichiers finaux (après x264, puis le mux en crf 20) :

| | Écart moyen de luminance dans un bloc 4 × 4 | Entre deux pixels d'un même bloc | Entre deux pixels de part et d'autre d'un bord de bloc |
|---|---|---|---|
| Atoll | 0,06 | 0,009 | 6,1 |
| Machu Picchu | 0,06 | 0,007 | 6,5 |

L'agrandissement est entier, au plus proche voisin, sans flou : le « moins bien défini » ne vient pas de l'encodage.

### 1.3 Détail, couleurs, aplats, cartouches (natif, sans cartouches, médianes)

| Mesure | Source | Atoll avant | Machu Picchu avant |
|---|---|---|---|
| `diffCells` (cellules ≠ voisine) | **0,221** | 0,111 | 0,146 |
| `grad` (énergie de gradient) | **12,4** | 6,1 | 5,6 |
| Aplats > 1 % de l'écran | 0,66 | 0,91 | 0,82 |
| Aplats > 5 % de l'écran | **0,50** | 0,85 | 0,59 |
| Nuages par écran (taille médiane, cellules) | **14 (139)** | 12 (31), ≤ 3 vrais nuages, le reste = écume | 2 (153) |
| Arbres par écran (taille) | **24 (6)** | 0 | 26 (7,5), des taches de forêt, pas des arbres |
| Îles / masses de terre (taille) | 8 (228) | 5 (115) | 3 (**1 379** : une seule masse) |
| Écume (traits par écran) | 129 | 206 | 51 |
| Couleurs par image (natif) | ≈ 16 effectives (k-means : 87 % des pixels à < 20 de 16 centres) | 13–21 indices | 13–21 indices |
| Compacité k = 8 (part couverte par 8 couleurs) | 0,70 | 0,92 | 0,91 |
| **Part de l'écran sous les cartouches** | 0 (ligne d'aide ≈ 3 %) | **18,9 %** (max 26,8 %) | **19,6 %** (max 23,8 %) |

Lecture :
- **Densité de détail divisée par deux** (`diffCells`, `grad`).
- **Grands aplats**, surtout l'océan nu de l'atoll : 85 % de l'écran en plages de plus de 5 %.
- **Pas d'arbres, 2 à 3 nuages trop petits**, une seule grosse masse verte à Machu Picchu.
- Le nombre de couleurs n'est pas en cause : 8 couleurs couvrent 91–92 % de nos images contre 70 % pour la source. Notre
  image tient sur moins de couleurs à la fois, à cause des grandes plages.
- L'écume n'est pas en déficit : nous en avons plus que la source.

### 1.4 « Carré »

- **Texels agrandis** : en rasante proche, une cellule du monde couvre 2 à 7 pixels natifs, sur des plages de couleur à bords
  droits (les flancs de Machu Picchu, la grande roche grise de 7 s, les terrasses en larges bandes lisses).
- **Relief naturel quantifié à 10,8 unités** à Machu Picchu : de grosses marches plates qui lisent comme des blocs.

### 1.5 Caméra et scintillement

| | Source | Atoll avant | Machu Picchu avant |
|---|---|---|---|
| Vitesse (corrélation de phase) | **3,5–4,8 cellules/image** en vue aérienne (106–143 /s), 8,1 en poursuite (242 /s) | 0,03 cellule/image (≈ 1 /s) | 0,04 (≈ 1,3 /s) |
| Pixels qui changent par image (fichier) | 27,7 % | 2,4 % | 4,5 % |
| Pixels A-B-A (crénelage) | 4,0 % (en partie le bruit H.264) | 0,23 % | 0,55 % |
| Bande de la revue (x 100–550, y 1180–1380, 5,5–9 s) | — | — | 1,50 % |

Le Farneback médian sur toute la vidéo (8 cellules/image) surestimait la vitesse : la corrélation de phase par vue donne les
chiffres ci-dessus, cohérents avec l'analyse (~100 cellules/s). Notre caméra est **quasi immobile** en comparaison. C'est un vrai
écart de « vie », mais il est contraint par la lecture des cartouches et par le plafond de scintillement de la revue.

### 1.6 Tableau « écart → cause → correction »

| Écart mesuré | Cause | Correction (18/11) |
|---|---|---|
| Détail ÷ 2 (`diffCells` 0,11–0,15 contre 0,22) | monde en grandes plages, aucun micro-détail | micro-détail sous la cellule (lecture décalée + moucheture), arbres, bandes crénelées, pâtés coralliens, rebords de terrasse, toits à deux pans, murs appareillés |
| Océan nu (aplats > 5 % : 85 %) | 3 petits nuages, anneaux de profondeur lisses et minces | 24 nuages en coton à l'échelle de la source avec leurs ombres ; front externe de pente irrégulière (bandes de 2 à 10 cellules) ; seuils crénelés ; lagon à pâtés coralliens |
| Nuages « soucoupes » de 31 cellules | piles de disques plats, vues de dessus = ellipses | tas de boules (couronne + boules empilées + sommet), hachure basse, liseré bleuté, ombres de couronne |
| Pas d'arbres (atoll), forêt en taches (Machu Picchu) | forêt = couleur de carte | arbres en boules au rayon projeté (≤ 7 px), reflet, ombre propre, ombre portée, semés en grappes |
| « Carré » de près | texels de 2–7 px à bords droits ; relief naturel en marches de 10,8 | bords en escalier irrégulier et moucheture sous la cellule ; relief naturel 10,8 → 6,3, terrasses agricoles 4,5 → 2,9 ; murs en assises |
| Une seule masse verte (1 379 cellules) | pente boisée uniforme | arbres, rebords, contours plus serrés : 404 cellules après |
| Cartouches : 19–20 % de l'écran | Jersey verrouillée sur sa grille de pixels à ×4 (34 / 27 / 18,7 px/em) ; ×3 rejeté | **non corrigé** (voir § 3) |
| Caméra quasi immobile (≈ 1 cellule/s contre 100–140) | cartouches à lire, plafond de scintillement | l'atoll **avance** (distance 385 → 330 dans le crochet, cible +24 dans la rasante finale) ; le plan en plongeante de Machu Picchu tourne **moins** (10° → 6° en 3,8 s) pour tenir le plafond de 2 % |
| Grille 4 px contre 3,94 | — | aucune (écart nul ; ×3 rejeté, § 1.1) |

## 2. Ce qui a changé dans le moteur (`survol.py`, identique dans les deux `src/`, md5 `9d38995aa862a43b9885777fac65e41a`)

1. **Micro-détail sous la cellule** (`Renderer(micro=0,12, jitter=0,42)`, table `pal.speckle`). Seulement au niveau de mip 0,
   quand une cellule couvre ≥ 2 pixels natifs. Sous-grille de 2^m cases par cellule (m = ⌊−log2 empreinte⌋, borné à 3).
   - Lecture de la carte de couleurs décalée par un hachage fixe dans le monde, sur le même dessus seulement : des bords en
     escalier irrégulier au lieu de grands carrés.
   - Moucheture sur 12 % des sous-cases.
   - Uniquement des indices de palette, rien n'est moyenné.
   - Mesuré : appliquée aussi à 1 pixel par cellule, la moucheture crénelait (+0,9 point dans la bande de la revue). Elle est
     donc réservée aux cellules ≥ 2 px.
2. **Murs appareillés** (`Renderer(course=…)`, `World(coursed=…)`) : assises sombres et joints décalés d'une demi-pierre, par
   la table d'ombre, seulement si l'assise fait ≥ 3 px.
3. **Nuages refaits** (`Cloud`, `draw_clouds`, `cloud_shadow_disks`) :
   - tas de boules dessinées au rayon projeté au pixel près, un peu aplaties en rasante ;
   - haut blanc, moitié basse hachurée une ligne sur deux, liseré bleuté (`CLOUD_RIM` `#CFE3F2`, 24e couleur du noyau) ;
   - ombres plates des boules de la couronne.
4. **Arbres** (`scatter_trees`, `tree_stamp`, `draw_trees`) :
   - boules de feuillage de rayon projeté 1,25–7 px (sous 1,25 px, la couleur de forêt de la carte suffit) ;
   - 4 tons, et ombre portée plate décalée selon la hauteur ;
   - occultation pixel par pixel. Le test sur le seul pixel du pied a été retiré : il basculait sur les arêtes des marches.
5. **`hash01`, `ragged`** : bruit fixe dans le monde, et seuils crénelés pour les scènes.

Scènes (`video.py`) :
- **Atoll** :
  - bandes de hauts-fonds crénelées, front externe de pente irrégulière ;
  - pâtés coralliens dans le lagon ;
  - arbres en grappes sur les terrasses du volcan ;
  - 24 nuages à l'altitude 90, hors de l'anneau et jamais traversés (contrôle sur tout le short). Plus hauts que la caméra des
    rasantes, ils restent dans le ciel et ne passent jamais devant la coupe : un premier essai à l'altitude 46 posait un
    nuage géant sur la coupe à 10,5 s ;
  - caméra qui avance.
- **Machu Picchu** :
  - marches naturelles 6,3, agricoles 2,9 ;
  - rebord clair en haut de chaque terrasse ;
  - toits à deux pans ;
  - murs de pierre appareillés ;
  - forêt de nuage en grappes (arbres) ;
  - 14 nuages bas jamais traversés ;
  - plan en plongeante moins tournant.
- **Inchangés** : textes, narration, son, grille, polices (test de grille Jersey : 99/99 glyphes exacts pour les trois tailles).

## 3. Avant / après (mêmes métriques)

### 3.1 Détail (natif, sans cartouches, médianes)

| Mesure | Source | Atoll avant → après | Machu Picchu avant → après |
|---|---|---|---|
| `diffCells` | 0,221 | 0,111 → **0,153** | 0,146 → **0,330** |
| `grad` | 12,4 | 6,1 → **7,5** | 5,6 → **14,0** |
| Aplats > 1 % de l'écran | 0,66 | 0,91 → 0,86 | 0,82 → **0,61** |
| Aplats > 5 % de l'écran | 0,50 | 0,85 → **0,80** | 0,59 → **0,35** |
| Nuages dans le cadre, compte exact du moteur (centre projeté dans l'image) | ≈ 13–14 (classifieur) | **0–1 → 3–11** (médiane 8 en plongeante) | **0–3 → 3–7** (médiane 5) |
| Taille d'un nuage (classifieur¹ ; part de l'écran) | 139 cellules (0,14 %) | 31 → 39 (0,03 %)¹ | 153 → 177 (0,14 %) |
| Ombres de nuages | une par nuage (silhouette décalée de ≈ 60 cellules) | une par nuage par construction (boules de la couronne), décalage (0,30 ; −0,62) × 90 = (27 ; −56) unités | idem, décalage selon l'altitude au-dessus de la cité |
| Arbres (classifieur, taille ; part de l'écran) | 24 grappes (6 cellules, 0,006 %) | 0 → 0² | 26 (7,5) → **284 (6 ; 0,005 %)** |
| Boules d'arbres dessinées, compte exact du moteur | — | 0 → 0–1 107 (présentes sur 45 % des images, volcan émergé) | 0 → **2 965–5 884** |
| Masses de terre (taille ; part de l'écran) | 8 (228 ; 0,23 %) | 5 (115) → 6 (119 ; 0,09 %) | 3 (1 379 ; 1,06 %) → 7 (**404 ; 0,31 %**) |
| Écume : traits par écran (taille) | 129 (1 cellule) | 206 → 208 (2) | 51 → 50 (1) |
| Couleurs par image (indices, natif) | ≈ 16 effectives | 13–21 → 16–24 | 13–21 → 17–22 |
| Entrées de palette par image, fichier décodé (blocs 4×4, ΔRGB ≤ 25) | — | → 22–28 (sur 29) | → 20–26 (sur 28) |
| Cartouches (part de l'écran) | — | 18,9 % → 18,9 % | 19,6 % → 19,5 % |

Parts de l'écran : source 377 × 261 = 98 400 cellules, nous 270 × 480 = 129 600.
¹ Le classifieur « composantes blanches ≥ 25 cellules » est faussé pour nos nuages : la hachure une ligne sur deux coupe
chaque nuage en bandes blanches, ce qui sous-estime la taille et gonfle le nombre (d'où les comptes exacts du moteur sur
la ligne du dessus). À l'œil, un nuage fait 15–25 cellules de large en plongeante, comme dans la source.
² Le classifieur « vert sombre » (V < 0,42) ne voit pas les boules de l'atoll, dont le feuillage `GRASS_D` est à V ≈ 0,48.
Le compte exact est sur la ligne suivante.

### 3.2 Netteté, scintillement, mouvement (fichiers finaux)

| Mesure | Source | Atoll avant → après | Machu Picchu avant → après |
|---|---|---|---|
| Écart dans un bloc 4 × 4 / de part et d'autre d'un bord de bloc | — | 0,009 / 6,1 → 0,015 / 6,8 | 0,007 / 6,5 → 0,036 / 10,2 |
| Bande de la revue (≤ ~2 %) | — | — | **1,50 % → 1,13 %** |
| Pixels qui changent par image (moyenne) | 27,7 % | 2,4 % → 3,4 % | 4,5 % → 9,7 % |
| Pixels A-B-A (crénelage) | 4,0 % | 0,23 % → 0,38 % | 0,55 % → 1,40 % |
| Vitesse de caméra (corrélation de phase, cellules/image) | 3,5–4,8 | 0,031 → 0,053 | 0,043 → 0,057 |
| Caméra d'après `cam_path` : rotation médiane / max (°/image) | — | 0,103 / 4,61 → 0,103 / 4,65 | 0,072 / 4,68 → 0,072 / 4,68 |
| À-coups : dérivée seconde de la rotation, P95 / max (°/image²) | accélération P95 6,3 cellules/image² (Farneback) | 0,047 / 0,56 → 0,047 / 0,54 | 0,101 / 0,49 → 0,101 / 0,47 |
| Déplacement médian de la caméra (unités/image) | — | 0,41 → 0,45 (elle avance) | 0,81 → 0,81 |
| Luminance moyenne : max ; saut max sur 1 image ; variation max sur 10 images | — | 0,544 ; 0,050 ; 0,157 → 0,554 ; 0,045 ; 0,127 | 0,575 ; 0,024 ; 0,118 → 0,567 ; 0,025 ; 0,109 |
| Poids `short.mp4` | — | 3,2 → 4,4 Mo | 4,0 → 8,3 Mo (≤ 15) |

Les vitesses et les à-coups de la caméra sont ceux d'avant (mêmes clés, sauf le crochet de l'atoll qui avance et le plan en
plongeante de Machu Picchu qui tourne moins) : aucun à-coup ajouté. Les pics de rotation (≈ 4,6 °/image) sont les piqués
et les remontées de 0,6 s.

Machu Picchu change plus de pixels par image. Ce n'est pas du crénelage du moteur : à mouvement de caméra égal, une image
deux fois plus détaillée change deux fois plus de pixels. Le plan final (forêt dense qui défile à ≈ 6°/s) monte à
1,4–3,2 % de pixels A-B-A, sous les 4,0 % de la source. Le premier rendu de la passe était à 2,82 % dans la bande de la revue ;
deux causes isolées et corrigées : la moucheture à 1 px par cellule, et la rotation du plan.

### 3.3 Coût

| | Avant (après revue) | Banc 60 images | Rendu complet après la passe de détail |
|---|---|---|---|
| Atoll | 87,0 s, 15,6 s/100 | 16,9 s/100 (charge 2,2) | **109,2 s, 19,6 s/100** |
| Machu Picchu | 333,6 s, 59,1 s/100 | 57,3 s/100 (charge 3,0) | **356,0 s, 63,1 s/100** |

Les deux rendus tournaient en parallèle, charge 1 min 2,7–8,9, moyenne 4,4 (`measuredUnderLoad: true`). Le surcoût est de +4 s/100 environ
(+25 % / +7 %), loin du plafond autorisé de 2,5× (39 et 148 s/100).
`check.py` : ok sur les deux shorts (seul avertissement : voix absente, attendu). Contrôle préalable de la caméra : marge
minimale 49,4 (atoll) et 51,0 (Machu Picchu).

## 4. Ce qui reste

- **Atoll** : le détail progresse (+38 % de `diffCells`) mais reste à 70 % de la source. L'océan profond occupe 75–80 % de
  l'écran et c'est le sujet (« en pleine mer »). Les leviers restants touchent la composition : hauts-fonds ou bancs
  submergés autour, plus de plongeante. Or **C15** (challenge) interdit l'archipel et plafonne les nuages. Cette passe
  **lève le plafond « ≤ 4 nuages » de C15** (3–11 dans le cadre), en application de la piste de la passe (« nuages en piles
  hachurées avec ombres décalées »). Contrôle C15 refait sur `comparaison-avant-apres.jpg` (5 images « après » de l'atoll
  contre les 4 images de la source) : **aucune image confondable**. Un seul anneau centré, pas d'archipel ni d'avion, format
  vertical, cartouches. La ressemblance porte sur la matière (nuages en coton, hauts-fonds), pas sur la composition. Le
  propriétaire doit encore valider ; le retour en arrière tient à `_clouds()` dans `video.py`.
- **Cartouches** : 19–20 % de l'écran, inchangé. Les polices Jersey ne sont exactes sur leur grille qu'à 34 / 27 / 18,7 px/em
  à ×4. Les seules réductions possibles changent la hiérarchie : passer l'accroche et les dates de Jersey 20 (136 px) à
  Jersey 15 (108 px, toujours ≥ 90 px) ôterait environ 5 points d'écran pendant ces plans. C'est une décision de design,
  laissée au propriétaire.
- **Vie de la caméra** : nous restons à ≈ 1,6 cellule/s contre 100–140 pour la source. Une caméra plus rapide demanderait des
  plans sans texte ou des cartouches plus courts, et ferait monter le scintillement : à arbitrer.
- **Géométrie en cellules** : de très près (coupe de Machu Picchu, 12,4 s), les bords de terrasse gardent un escalier
  régulier d'une cellule. Le micro-détail ne casse que la couleur, pas la forme.
- **Reconnaissance** (`recognition.py`) non relancée : à refaire à l'intégration, sur une copie.
