# Analyse de la source « console-retro » (simulateur de vol pixel art, @creativedash)

Analyse image par image d'une vidéo dont on veut reprendre le **style** (pas le contenu) pour une nouvelle identité de shorts verticaux 1080×1920.
Provenance, méthode et images de référence : `console-retro-source/SOURCE.md`. Date : 2026-11-18.

## 0. Fiche technique de la source

| Mesure | Valeur |
|---|---|
| Fichier | `source_1080.mp4`, H.264 1486×1080, 60 i/s, 11,35 s, ~11 Mb/s |
| Audio | AAC 48 kHz stéréo, **silence numérique intégral** (ebur128 : −70 LUFS = plancher, astats : crête −∞ dB) |
| Nature | capture d'écran d'un jeu web jouable (curseur de souris visible, ligne d'aide en bas) |
| Grille de gros pixels | **3,94 px source** en x et en y (stable sur toutes les vues) → résolution native ≈ **377×274** |
| Coupes franches | **aucune** : `select='gt(scene,0.3)'` ne détecte rien (score max 0,06) ; les changements de vue sont des mouvements de caméra continus |

## 1. Découpage (cut list) et rythme

Changements repérés sur le signal de différence image à image à 60 i/s (pics à 3,25–3,6 s, 5,5 s, 9,05 s) puis vérifiés sur des planches à 10–20 i/s.

| # | Début → fin (s) | Durée | Vue | Description |
|---|---|---|---|---|
| 1 | 0,00 → 3,25 | 3,25 s | **aérienne (top-down)** | carte nord en haut, l'avion tourne au centre-gauche (~45 % × 48 % de l'écran), traînées blanches derrière lui, île en terrasses puis haute mer |
| 2 | 3,25 → 3,65 | 0,40 s | transition | la caméra bascule de la verticale vers l'horizon (pitch ~90° → ~15°) en suivant l'avion ; l'avion grossit (sprite ×3), le ciel apparaît en haut |
| 3 | 3,65 → 5,40 | 1,75 s | **poursuite (chase)** | caméra derrière et au-dessus, horizon à ~41 % du haut (y natif 111/272), roulis et montée (à 3,75 s l'horizon descend à ~64 %), postcombustion orange, fumée grise en boules |
| 4 | 5,40 → 5,65 | 0,25 s | transition | le sprite de l'avion se dissout (~0,1 s), le tableau de bord **monte depuis le bas** (~0,15 s), l'arceau de la verrière apparaît |
| 5 | 5,65 → 9,00 | 3,35 s | **cockpit** | tableau fixe sur le tiers bas (y > ~165/272), paysage en perspective dans la verrière avec roulis jusqu'à ~70–80° (8,25 s), HUD vert filaire |
| 6 | 9,00 → 9,30 | 0,30 s | transition | le tableau **redescend**, la caméra se relève de l'horizon vers la verticale |
| 7 | 9,30 → 11,35 | 2,05 s | **aérienne** | même grammaire qu'en 1, altitude un peu plus haute au début puis île à droite |

**Rythme** : 3 vues en 11,35 s, plans de 1,75 à 3,35 s, transitions de 0,25 à 0,40 s, cycle aérienne → poursuite → cockpit → aérienne (bouclable). Pour un short de 12–19 s, cela donne une grammaire « 3–4 vues de 2–4 s reliées par des bascules de caméra de 0,3–0,4 s », sans fondu ni coupe franche.

La ligne d'aide change à chaque vue (« … SPACE FOR CHASE VIEW » / « … FOR THE COCKPIT » / « … FOR OVERHEAD ») et passe **du bas vers le haut** de l'écran en vue cockpit (le tableau occupe le bas).

## 2. Description des vues

### 2.1 Vue aérienne (top-down)

- **Océan** : aplat bleu profond `#2a68b0` (56 % des pixels) ; **moutons d'écume** = petits traits blancs/bleu pâle de 1×2 à 1×4 gros pixels, inclinés, semés régulièrement (densité ≈ 1 trait pour 12×12 gros pixels), qui scintillent d'une image à l'autre.
- **Hauts-fonds** : bandes concentriques autour des îles et des bancs de sable, du plus profond au plus clair `#2a68b0` → `#317cbf` → `#4ca4d2` → `#7ec4f0`, contours en escalier (pas de dégradé lisse, pas de tramage régulier : la transition est un bord crénelé avec quelques pixels isolés).
- **Ressac** : liseré de pixels blancs/cyan `#d8f6fc` épars, 2–4 gros pixels de large, collé au sable.
- **Plage** : bande de sable `#e4dda5` de 2–4 gros pixels.
- **Terre en terrasses** : verts `#8bdc56` / `#66be3b` / `#43902b` en plages, **courbes de niveau** = traits sombres de 1 gros pixel, en escalier, espacés de 8–12 gros pixels (8 à 12 courbes visibles sur la grande île). Chaque marche alterne deux verts et son bord bas est souligné par le trait sombre : lecture immédiate d'un relief étagé.
- **Rocher / sommet** : gris `#7e7a75` avec ombrage gris foncé, en haut des îles.
- **Arbres** : amas de boules vert foncé `#1a5020` de 3–5 gros pixels, reflet clair en haut à gauche, ombre propre en bas à droite ; forêts en grappes.
- **Nuages** : masses blanches `#fbfdfe` composées de 2–4 lobes circulaires empilés verticalement (aspect de « boules de coton » ou de pile de disques), ombrage par **hachures horizontales gris clair `#b0bac2`** sur la moitié basse (lignes de 2–6 gros pixels, une rangée sur deux), liseré bleuté en bas : volume lu comme une pile de tranches.
- **Ombres des nuages** : silhouettes pleines bleu sombre `#1a488e` sur l'eau, vert sombre sur la terre (voir § 3.4 pour le décalage).
- **Avion** : sprite sombre (anthracite, accents rouge-orange, verrière cyan), postcombustion orange, petites bouffées grises ; **traînées** = deux fines courbes blanches continues (1 px, antialiasées, hors grille) qui deviennent pointillées en vieillissant. *Design de l'avion à ne pas reprendre.*

### 2.2 Vue perspective / poursuite (« Mode 7 »)

- Sol plan texturé projeté en perspective vers un horizon droit (incliné selon le roulis), la même carte qu'en vue aérienne : îles en terrasses, hauts-fonds, nuages.
- **Ciel en bandes** : dégradé à paliers larges (16–19 lignes natives chacun) séparés par des rampes courtes de 1 ligne par niveau (mesure ligne par ligne, § 3.2). Haut `#9dd1eb` → `#b5def5` → le plus clair `#c7e9f7` → `#bde0f5`, puis **brume** qui assombrit et désature vers l'horizon (`#a4c7e4` → `#8dbece`).
- **Brume au sol** : les terres lointaines virent au vert-gris `#92b9a4` / `#749378` et se fondent dans le bleu-ciel ; l'eau lointaine passe de `#2966ad` à `#5b9dcd`.
- **Nuages** en vue rasante : ellipses aplaties (billboards) avec la même hachure, plus petites vers l'horizon ; leurs ombres restent visibles sur l'eau.
- **Avion** en gros plan (≈ 1/4 de la largeur), flammes de réacteur orange-jaune en dégradé, fumée en disques gris semi-transparents (plus lisses que la grille).

### 2.3 Cockpit

- **Arceau de verrière** : deux arcs gris foncé en haut avec plaques orange `#da5423`, montant central vertical ; reflets en **bandes diagonales claires** (rayons) traversant la verrière et le tableau.
- **HUD** : vert clair `#8cfbae` semi-transparent, traits de 1 gros pixel : échelles verticales graduées gauche/droite, cadre rectangulaire, réticule central, nombres (vitesse « 387 », altitude « 13317 »), barre de cap en bas.
- **Tableau** : gris-bleu sombres `#3e3f4c` / `#2b2e39` / `#0b0b13`, rivets clairs, écran radar vert sur noir-vert `#041c0d` (balayage, tracé de côte en vert vif `#26a553`), horizon artificiel (bille ciel `#6199d5` / terre `#7e3d1f`) au centre, 4 cadrans à aiguilles orange, écran de droite avec silhouette d'avion verte et jauges en barres, rangées de voyants orange/jaune, manche au centre, interrupteurs à droite, mouchetis orange sur le métal. *Disposition et éléments à ne pas reprendre.*

### 2.4 Ligne d'aide et curseur

- Ligne d'aide : capitales en police **monospace vectorielle** (non pixel, antialiasée, hors grille), approche large (~0,5 em), hauteur de capitales ≈ 11 px source (≈ 2,8 gros pixels), gris très clair sur bandeau bleu marine semi-transparent, centrée en bas (y ≈ 1040–1068) puis en haut en vue cockpit. Séparateur « · ». *Texte d'interface à ne pas reprendre.*
- **Curseur de souris** macOS (flèche noire) visible presque partout : artefact de capture, **hors style**.

## 3. Mesures

### 3.1 Taille du gros pixel et résolution native

**Méthode** : sur 8 images pleine résolution (0,5 à 10,3 s, toutes les vues), somme des gradients absolus horizontaux (resp. verticaux) par colonne (resp. ligne), puis recherche fine de la période par DFT entre 3,5 et 4,5 px (pas 0,002) ; contrôle par FFT simple (pic à 3,94, rapport signal/bruit 16–81) et autocorrélation (décalage 4, corrélation 0,64–0,96).

**Résultat** : période **3,938 px en x et 3,940–3,946 px en y**, identique dans les trois vues → la scène entière (carte, avion, nuages, cockpit, HUD) est rendue sur **une seule grille écran d'environ 377×274 gros pixels**, puis agrandie au plus proche voisin (le léger flou observé vient de la mise à l'échelle non entière et de la compression H.264). Phase de grille retrouvée (3,5 ; 2,5 px) ; les trames reconstituées en échantillonnant le centre de chaque cellule font 375×272.
Exceptions hors grille : traînées blanches, fumée, ligne d'aide.

**Recommandation pour 1080×1920** :

| Résolution native | Facteur | Gros pixel | Commentaire |
|---|---|---|---|
| **270×480** | **×4** | 4 px | **recommandé** : même taille de gros pixel que la source (3,94 px), entier, 480 lignes pour une composition verticale |
| 360×640 | ×3 | 3 px | autant de colonnes que la source (377) ; plus fin, utile si beaucoup de texte en pixel font |
| 216×384 | ×5 | 5 px | plus « gros grain », lisible sur petit écran, mais peu de place pour le relief |

Agrandissement obligatoirement au plus proche voisin et entier ; pas de mise à l'échelle fractionnaire (c'est ce qui floute la source).

### 3.2 Palettes par vue

k-means sur les trames natives reconstituées (`palette.png`, % des pixels).

**Vue aérienne** (3 trames)

| Rôle | Hex | Part |
|---|---|---|
| océan profond | `#2a68b0` | 56,3 % |
| océan moyen | `#317cbf` | 8,1 % |
| nuage blanc / écume | `#fbfdfe` | 5,2 % |
| ombre portée sur l'eau | `#1a488e` | 4,5 % |
| herbe claire | `#8bdc56` | 4,5 % |
| herbe moyenne | `#66be3b` | 4,4 % |
| herbe sombre / courbes | `#43902b` | 3,5 % |
| haut-fond | `#4ca4d2` | 3,5 % |
| forêt | `#1a5020` | 2,6 % |
| lagon clair | `#7ec4f0` | 1,8 % |
| hachure de nuage | `#b0bac2` | 1,8 % |
| ressac | `#d8f6fc` | 1,6 % |
| sable | `#e4dda5` | 1,3 % |
| roche | `#7e7a75` | 0,9 % |

**Perspective / poursuite** (2 trames) : `#b8def4` 24,0 % (ciel), `#2966ad` 14,7 % (eau), `#cdebf7` 11,2 % (bande de ciel claire), `#a1d0ec` 10,6 %, `#87c0e6` 10,0 % (brume), `#367cbd` 6,0 %, `#5b9dcd` 5,7 % (eau lointaine), `#5fb338` 5,3 %, `#87d853` 3,0 %, `#92b9a4` 2,4 % (terre dans la brume), `#35782b` 2,3 %, `#749378` 2,0 %, `#2c1f23` 1,7 % (avion), `#dfdfa5` 1,0 %.

**Cockpit, tableau** : `#3e3f4c` 19,7 %, `#2b2e39` 19,2 %, `#0b0b13` 13,6 %, `#1c2127` 11,7 %, `#041c0d` 10,8 % (fond d'écran radar), `#555764` 6,7 %, `#767784` 3,8 %, `#26a553` 3,1 % (vert écran), `#da5423` 2,2 % (orange accent), `#9d9ea9`, `#c8cfd4`, `#6199d5`, `#7e3d1f` (bille), `#eeb569`, `#61f191` (chiffres), `#f3f8f2`.
**Cockpit, verrière** : `#b5def4` 21,3 %, `#9ed1ef` 16,6 %, `#89c5eb` 15,1 %, `#c5e8f8` 12,9 %, `#2b68af` 12,5 %, `#73b3e4` 9,3 %, HUD `#8cfbae` 1,4 %, orange `#ce4315` / `#f29651`.

**Palette indexée ?** Comptage brut inutilisable (2 700–5 400 couleurs distinctes à 5 bits/canal à cause du H.264). Test de compacité : part des pixels à moins de 20 (distance RGB) de leur centre k-means.

| Vue | k = 8 | k = 16 | k = 24 | k = 32 |
|---|---|---|---|---|
| aérienne | 75 % | **92 %** | 94 % | 94 % |
| perspective | 65 % | 80 % | 89 % | 90 % |
| cockpit | 60 % | 83 % | 89 % | 91 % |

→ La vue aérienne se comporte comme une **palette indexée d'environ 16 couleurs** (le reste est bruit de compression, bords antialiasés, traînées et avion). La perspective ne l'est pas : la brume mélange les couleurs avec la distance (rampes continues). Le cockpit tient dans ~24–32 couleurs.

**Tramage** : motifs en damier 2×2 sur 0,06–0,31 % des cellules, alternance de lignes 0,9–1,8 % → **pas de tramage global** (ni Bayer ni damier). Le seul « tramage » est local et dessiné : hachures horizontales des nuages, pixels épars du ressac et des hauts-fonds.

### 3.3 Contours, lignes de balayage, effets d'écran

- **Pas de contour noir** généralisé : les formes sont séparées par la couleur ; seuls les courbes de niveau (1 gros pixel sombre) et les instruments du cockpit ont un trait.
- **Pas de lignes de balayage (scanlines), pas de courbure CRT, pas d'aberration chromatique, pas de grain, pas de vignettage.** Le léger flou est celui de la capture.
- Effets de lumière : bandes diagonales claires (reflets de verrière) en vue cockpit uniquement.

### 3.4 Profondeur et volume (signature à préserver)

Demande du propriétaire : la profondeur 3D de la source est un trait de signature. Voici comment elle est produite en pixel art.

1. **Perspective type Mode 7 vers l'horizon.** Le sol est la *même carte 2D* que la vue aérienne, projetée sur un plan : chaque ligne d'écran échantillonne la carte à une distance qui augmente vers l'horizon (échelle ∝ 1/(y − y_horizon)). Mesures sur la trame 4,3 s : horizon à y ≈ 111/272 (41 % du haut) ; près de l'horizon les motifs ne font plus que **1,6–2 lignes** de haut contre 2,5–5 lignes en bas d'écran ; le rapport largeur/hauteur des motifs vaut 1,5–2,4 (écrasement vertical par le raccourci). Au-delà de ~40 lignes sous l'horizon, la texture devient du crénelage scintillant de 1 gros pixel : c'est l'aspect « bandes empilées » revendiqué par l'auteur. L'horizon s'incline avec le roulis (jusqu'à ~70–80° en cockpit).
2. **Ciel et brume en paliers.** Le ciel n'est pas un dégradé lisse mais **3–4 bandes plates de 16–19 lignes** séparées par des rampes d'environ 1 ligne par niveau, la bande la plus claire juste au-dessus de la zone de brume ; puis ~20 lignes de brume qui assombrissent et désaturent jusqu'à l'horizon. Au sol, la brume (fondu vers `#87c0e6` / `#92b9a4`) croît avec la distance : terres vertes → vert-gris → bleu ciel.
3. **Couches empilées et parallaxe.** Trois plans distincts : sol (carte), nuages (couche plus haute, avec leur propre ombre décalée ; la parallaxe nuages/sol en vue aérienne n’a pas été mesurée), avion (encore au-dessus, avec sa propre ombre). En vue perspective, les nuages sont des billboards aplatis qui rétrécissent avec la distance.
4. **Relief en terrasses** (vue aérienne). 8 à 12 marches visibles sur la grande île, espacées de 8–12 gros pixels ; chaque marche = aplat d'un des 3 verts + **trait sombre de 1 gros pixel en escalier** sur son bord ; sommet rocheux gris ombré au-dessus ; plage et ressac au pied. En perspective, ces marches deviennent des stries horizontales vert clair / vert foncé qui donnent le volume des îles.
5. **Ombres portées.** Couleur : version sombre et saturée du fond (eau `#2a68b0` → ombre `#1a488e`, luminance ×≈0,7 ; sur l'herbe, vert sombre). Forme : silhouette pleine sans flou. Décalage mesuré par corrélation masque-nuage / masque-ombre sur 4 trames aériennes natives : **(dx, dy) = (−16…+5, +57…+64) gros pixels**, soit presque plein sud et ≈ 22 % de la hauteur d'écran ; il est le même pour des nuages de tailles très différentes → **une seule altitude de nuages**, l'offset ne varie pas d'un nuage à l'autre. L'avion projette une ombre en forme d'avion décalée d'environ **(+33…+38, +55…+66) gros pixels** (2 observations, ±5) : décalage différent de celui des nuages, donc l'offset encode l'altitude/la position de chaque couche. En vue perspective, les ombres des nuages tombent sur l'eau en bas à gauche des nuages.
6. **Volume des nuages.** Lobes circulaires empilés (2–4), haut blanc pur, moitié basse hachurée de lignes horizontales gris clair une rangée sur deux, liseré bleuté au bas : lecture « pile de tranches » éclairée par le haut.
7. **Mouvement de caméra.** Vue aérienne : la carte défile sous l'avion (nord toujours en haut, c'est l'avion qui pivote) à ≈ 60–300 gros pixels/s (médiane ~100, corrélation de phase à 10 i/s) ; l’avion reste près du centre (≈ 45 % × 48 %). Les bascules entre vues sont des **rotations de caméra continues** (pitch 90° ↔ ~15° en 0,3–0,4 s), jamais des coupes. Cockpit : le paysage roule autour du centre, le tableau reste fixe.

### 3.5 Caméra (synthèse)

| Vue | Mouvement | Vitesse / amplitude |
|---|---|---|
| aérienne | défilement + suivi de l'avion, nord fixe | ~100 gros px/s (pointes 300) |
| bascule aérienne ↔ poursuite | pitch continu, zoom sur l'avion | 0,30–0,40 s |
| poursuite | derrière/au-dessus, roulis et montée de l'avion | horizon 41 % → 64 % du haut |
| cockpit | roulis du paysage seul | jusqu'à ~70–80° |
| entrée / sortie cockpit | tableau qui glisse verticalement, dissolution du sprite | 0,10–0,15 s |

### 3.6 Typographie

- **Chiffres du HUD et des écrans** : police pixel sur la grille, chiffres d'environ 5 gros pixels de haut, vert `#61f191` / `#8cfbae` sur fond sombre ou sur le ciel.
- **Ligne d'aide** : police monospace vectorielle (non pixel), capitales espacées, ≈ 2,8 gros pixels de haut, gris clair sur bandeau marine translucide.
- Aucun autre texte. Pour nos shorts il faudra une vraie police pixel (≥ 54 px à l'écran, soit ≥ 14 lignes natives à ×4, ex. police 7×9 ×2 ou 10×14).

### 3.7 Audio

Piste présente mais **entièrement silencieuse** (−70 LUFS, crête −∞ dB) : aucune information sur moteur, musique ou bruitages. Le son de l'identité sera à concevoir (piste chiptune / bruit de réacteur filtré façon console 16 bits), sans référence dans la source.

## 4. Traits reconnaissables (à garder dans l'identité)

1. **Grille unique de gros pixels** (~4 px à l'écran, ~270–377 colonnes natives) appliquée à toute la scène, agrandie au plus proche voisin.
2. **Profondeur Mode 7** : la même carte vue de dessus puis couchée vers un horizon, motifs écrasés et scintillants près de l'horizon.
3. **Ciel et brume en paliers** plats bleu-ciel, brume qui désature les lointains.
4. **Archipel tropical à palette courte** : bleu océan dominant (> 50 %), anneaux de hauts-fonds turquoise, sable crème, 3 verts, courbes de niveau sombres de 1 pixel = relief en terrasses.
5. **Couches empilées avec ombres portées décalées** (nuages ~60 gros px vers le bas, objet volant avec son propre décalage), ombres en aplat sombre saturé.
6. **Nuages en piles de lobes hachurés** et moutons d'écume en petits traits blancs semés.
7. **Bascules de caméra continues** entre vue de dessus, vue rasante et vue intérieure (0,3–0,4 s), sans coupe ni fondu.
8. **Pas d'effets d'écran** : ni scanlines, ni CRT, ni grain : la netteté « console 16 bits propre » fait partie du style.

## 5. Ce qu'il ne faut PAS copier

On reprend un style, pas l'œuvre de @creativedash :

- le **design de l'avion** (silhouette, couleurs anthracite/rouge, flammes, fumée) et tout sprite de la source ;
- la **disposition du cockpit** (arceau à plaques orange, radar à gauche, bille au centre, écran à silhouette d'avion à droite, manche, interrupteurs, mouchetis), ses instruments et son HUD tel quel ;
- le **texte d'interface** (« MOVE TO STEER · CLICK TO ROLL · … ») et sa mise en forme en bandeau ;
- la **carte** (formes des îles, emplacement des rochers et forêts) et tout élément graphique extrait des images ;
- le principe de jeu (contrôles, trajectoire de vol) ;
- le **curseur** de souris (artefact de capture).

Tout sera regénéré par code avec nos propres sujets, cartes, objets et polices ; les images de `console-retro-source/` restent des références d'analyse.
