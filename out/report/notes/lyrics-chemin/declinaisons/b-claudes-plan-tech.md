# B — « Claude's Plan », version tech (paroles, 32,6 s)

Vidéo de paroles muette 1080×1920, 30 i/s, 32,62 s, **mêmes temps que la version actuelle** (154,5 BPM, 1 temps = 0,388 s).
Paroles en anglais, jamais traduites. Habillage `editeur`, dessin `cargo`. Maquette : `proto/cargo.js`.
Images (jeu de remplissage « Monday's draft ») : `images/b-01-suggestion-fantome-4.30s.jpg`, `images/b-02-flanc-echec-14.50s.jpg`,
`images/b-03-image-finale-32.50s.jpg`. Les mêmes avec les vraies paroles : hors dépôt,
`~/git/StudioVisualIdentity-sources/lyrics-claudes-plan/stills-tech/`. **Ni les vraies paroles ni l'audio n'entrent dans le dépôt.**

## Le problème

Le plan d'architecte, le crayon et le café racontent un bureau d'études. La chanson raconte des développeurs de la Silicon Valley qui
codent avec une IA : il faut leur établi à eux. On garde la mécanique et le jaune du mot chanté ; on change la surface, les objets,
la police et le dessin.

## Trois habillages pesés

| | Habillage | Pour | Contre |
|---|---|---|---|
| 1 | **Éditeur de code sombre sur un écran vertical** (retenu) | lu « dev » au premier coup d'œil ; coloration syntaxique = couleur de l'encre sèche ; curseur bloc = la pointe ; **texte fantôme d'une suggestion d'IA = le pré-posé** de l'identité ; la grille de points remplace le quadrillage ; l'écran vertical d'un développeur a le format 9:16 | le texte suit des traits inclinés, ce qu'un vrai éditeur ne fait pas : c'est un éditeur stylisé, assumé ; la chasse fixe est large (voir « Typographie ») |
| 2 | Terminal | encore plus brut, vert ou ambre sur noir | une seule couleur, donc plus de coloration ; rappelle `pixel-arcade` et le rétro, pas la Silicon Valley de 2026 ; tout y est horizontal |
| 3 | Tableau blanc de start-up au feutre | vrai lieu du « plan », objets évidents (feutres, aimants, notes collées) | fond blanc éblouissant sur téléphone ; ambiance salle de réunion ; proche de l'ardoise de A2 ; pas de police à chasse fixe justifiée |

L'art ASCII pur (texte sur une grille de caractères, tout horizontal) a été écarté : la caméra ne tournerait plus jamais, on perdrait
les virages qui font l'identité.

## Le dessin final : un porte-conteneurs

| Option | Verdict |
|---|---|
| Bateau en papier (dessin actuel) | bon jeu de mots, mais c'est un pliage : il appartient au papier. Et ses arêtes de 450 px sont trop courtes pour une police à chasse fixe |
| Fusée | cliché des start-up, silhouette étroite, rien à voir avec le refrain (déjà écartée au concept) |
| Schéma d'architecture | colle au « mode plan », mais rien à découvrir au zoom arrière |
| **Porte-conteneurs** (retenu) | garde *ship* ; **chaque ligne du couplet est un conteneur** (une ligne de code dans sa boîte, numérotée comme dans la gouttière) ; pendant le voyage on croit lire un fichier ou un schéma de boîtes, au zoom arrière ces boîtes sont la cargaison. Les développeurs y liront aussi les « conteneurs » qu'ils déploient |

Ce que le dessin raconte : tout ce que la chanson empile (le plan, les lignes, la panne, les clés, les fichiers de notes, le mauvais
changement) part quand même en mer. Le mauvais changement est **le conteneur de travers**, en haut de la pile.

| Partie du dessin | Moment (thème, pas les paroles) | Arête |
|---|---|---|
| Nom du navire, peint sur la coque | titre | `titre` |
| Conteneur du bas (violet) | le début de journée | `c1` |
| Conteneur du milieu (vert) | les lignes qu'on écrit | `c2` |
| Conteneur du haut (orange) | « depuis la version… » | `c3` |
| Flanc gauche de la coque, qui descend | la panne ; ✗ rouge et notification d'échec | `coqueG` |
| Quille | les clés ; pastille « clé » | `quille` |
| Flanc droit, qui remonte | encore un fichier de notes ; onglet de fichier | `coqueD` |
| Fanion en tête de mât | la relance isolée ; la caméra respire ensuite | `fanion` |
| Conteneur de travers (rouge, −8°), souligné d'un trait ondulé | le mauvais changement | `c8` |
| Première vague | « beaucoup de mauvais changements » | `vague1` |
| Sortie de terminal sous le navire, quatre rangs précédés de `>` | le refrain répété, comme un journal de déploiement | `final` |

## Habillage `editeur`

- **Feuille = la dalle d'un écran vertical** : x 44–1036, y 120–1560, coins 16 px ; fond `#141B30` → `#0B101D`, halo bleu très léger en
  haut à gauche (la lumière de l'identité). **Grille de points** tous les 20 px (10–16 %), croix tous les 100 px (30 %).
- **Habillage d'éditeur, décor sans aucun mot** : barre de titre (trois pastilles, un onglet avec une icône de fichier et des barres
  grises, une pastille « mode » violette avec ▶▶), **gouttière de numéros de ligne** à gauche (JetBrains Mono 11 px, seul texte de
  décor, équivalent du « PL. 01 — 1:1 »), barre d'état en bas.
- **Sol** : tapis de bureau anthracite `#16171B` feutré. Coque de l'écran noire, menton de 52 px.
- **Traits du dessin** : bleu ardoise `#8497C4`, 3,2 px. Conteneurs : contour 2,4 px dans la couleur de syntaxe de la ligne, aplat à
  9 %, ondulations verticales aux deux bouts, numéro de ligne (`01`…) en gris commentaire ; conteneurs de décor en gris, remplis de barres.
- **Pointe = curseur bloc jaune** (0,56 × 1,18 em), plein pendant la frappe, **clignotant sur le temps** au repos (allumé un temps sur deux).
- **Pré-posé = texte fantôme** : JetBrains Mono 400 *italique*, `#8B98B8` à 80 %, posé un temps avant l'attaque comme une suggestion
  d'assistant ; à l'attaque le mot passe en 700 jaune d'un coup (« accepté »). La chasse fixe garantit que rien ne bouge au changement de graisse.
- **Annotations rouges = idiomes d'éditeur** (jamais du texte) : ✗ d'un contrôle en échec, **soulignement ondulé** d'une erreur, fanion.
- **Objets croisés en route** (panneaux flottants avec ombre, sans mot) : notification d'échec (pastille rouge ✗, barres), pastille
  « clé » (clé ambre, cinq points masqués), onglet de fichier (icône verte, barre).
- **Objets physiques**, révélés par le zoom arrière : note collée jaune sur le bord droit de l'écran, deux autocollants sur le menton
  (rond irisé au chevron, cœur en pixels), **clavier mécanique** coupé par le bas du cadre (touches ivoire, modificateurs gris, Échap
  jaune), **canette** vue de dessus (aluminium, liseré menthe, sans marque). Aucun logo, aucune marque.

| Rôle | Couleur | Contraste sur `#141B30` |
|---|---|---|
| **Encre fraîche (mot chanté)** | jaune `#FFD84A` (le jaune de l'identité, inchangé) | 12,3:1 |
| Encre sèche, texte courant | `#D5DCEA` (60 % en gros plan) | 12,4:1 |
| Encre sèche, mot-clé (`kw`) | violet `#B79CF7` | 7,4:1 |
| Encre sèche, fichier ou chaîne (`str`) | vert `#93D8A0` | 10,2:1 |
| Encre sèche, nombre (`num`) | orange `#F2A65A` | 8,4:1 |
| Pré-posé (suggestion) | `#8B98B8` italique | 5,9:1 |
| Annotations | rouge `#FF6B5E` | 6,1:1 |
| Numéros, invites `>` (décor) | gris commentaire `#66769A` | 3,8:1 |

Le jaune reste **réservé au mot chanté** (seule exception décorative : la touche Échap et un voyant du château, hors lecture).
Jamais : néon, halo lumineux, balayage d'écran cathodique, reflet de vitre.

### Typographie

**JetBrains Mono** (JetBrains, licence **SIL Open Font License 1.1**), paquet `@fontsource/jetbrains-mono` déjà dans le dépôt
(à épingler à sa version installée). Graisses : **700** paroles, **800** nom du navire et rangs finaux, **400 italique** texte fantôme,
400 gouttière. **Minuscules** pour les paroles (c'est du code), capitales pour le nom du navire ; les sigles gardent leurs capitales.

Conséquences de la chasse fixe (0,6 em par signe, contre ≈ 0,44 pour Barlow Condensed) :

| Règle de l'identité | Valeur pour `editeur` |
|---|---|
| Corps dans le monde 36–60 px | **28–46 px** (calculés : conteneurs 29–30, coque 30–32, vague 36, mauvais changement 38, fanion 44, nom 53) |
| Plancher à l'écran 120 px | **96 px** (`floorPx`) : œil de la lettre plus haut (0,55 em), aussi lisible |
| Cadrage ≤ 780 px, 1 à 3 unités | **13 signes au plus par cadrage** : presque toujours une unité seule ; la caméra glisse plus souvent, comme un œil qui suit la frappe |
| Interlettrage 0–0,15 em pour finir l'arête | **aucun** (0,04 em au plus) : on centre le texte dans sa boîte |
| Rangs finaux ≤ 88 px, largeur 850 | **≤ 68 px, alignés à gauche** en x 176, largeur 760 ; 68 px sur le remplissage, **60 px avec les vraies paroles** |

## Dessin `cargo` (repère monde = image finale)

- Coque : L (110, 706), R (946, 706), BL (288, 1120), BR (780, 1120) ; flancs à 61°, texte **sous** le trait (à l'extérieur) ; pont L–R.
- Conteneurs (hauteur 80, pas 86) : `c1` x 200–760 y 622 ; `c2` x 338–920 y 536 ; `c3` x 230–740 y 450 ; `c8` x 566–866 y 364, tourné
  de −8° autour de son coin bas gauche ; quatre conteneurs de décor complètent les rangs (table `BOX` de la maquette). Le texte est
  **centré dans la boîte** (arête sans trait, option `inside`).
- Château à gauche (96–182 × 414–706), mât jusqu'à y 236, fanion dont la longueur **suit le texte** (texte + 46 px).
- Nom du navire : (290, 846) → (766, 846), centré. Ligne de flottaison pointillée à y 1010.
- Première vague : x 96–640, y 1182, amplitude 7, longueur d'onde 180 ; elle se prolonge sans texte de 700 à 940.
- Rangs finaux : y 1262, 1344, 1426, 1508, une unité par rang sauf le premier (deux unités) ; invite `>` grise en x 112.
- Tout le dessin tient dans x 96–946 ; rien d'utile sous y 1560.

Les arêtes gardent les noms de `bateau.json` quand le rôle est le même (`titre`, `coqueG`, `quille`, `coqueD`, `fanion`, `vague1`) ;
`voileG`, `voileD`, `pontD`, `pontG` deviennent `c1`, `c2`, `c3`, `c8`.

## Storyboard (temps du morceau ; mots du remplissage ; cadrages calculés par la maquette)

| N° | Arrivée (s) | Où | Mots (attaque) | Caméra (monde), zoom, angle | Transition d'arrivée |
|---|---|---|---|---|---|
| 1 | 0,00 | nom sur la coque | MONDAY'S (0,00) | (426, 819) ×2,9, 0° | — ; grille de points, curseur visible à l'image 0 |
| 2 | 1,49 | nom sur la coque | DRAFT (1,55) | (682, 819) ×3,75 | glissé |
| 3 | 3,01 | conteneur 01 | i fold (3,20) · my day (4,47, fantôme dès 4,08) | (376, 647) ×3,4 | **fouetté** 1 temps ; le conteneur se trace avec la ligne |
| 4 | 4,99 | conteneur 01 | in draft mode (5,05, fantôme) | (624, 647) ×3,4 | glissé |
| 5 | 6,95 | conteneur 02 | i draw (7,18, fantôme) · lines (7,57) | (502, 562) ×3,75 | **retour chariot** : fouetté d'un temps vers la gauche, une ligne plus haut |
| 6 | 7,90 | conteneur 02 | but not (7,96, fantôme) · for show (8,26) | (762, 562) ×3,3 | glissé |
| 7 | 9,90 | conteneur 03 | i've been (10,29, fantôme) | (367, 476) ×5,0 | retour chariot |
| 8 | 10,72 | conteneur 03 | up since (10,78, fantôme) | (531, 476) ×5,7 | glissé |
| 9 | 11,01 | conteneur 03 | 5 a.m. (11,07) → sèche en orange | (668, 476) ×7,6 | glissé ; le château se trace à gauche |
| 10 | 12,82 | flanc gauche | printer down (13,01) ; ✗ rouge à 13,7, notification | (148, 834) ×3,6, **61°** | **virage** 1,5 temps au coin L |
| 11 | 14,12 | flanc gauche | cuz no ink (14,18) | (233, 1032) ×4,3, 61° | glissé |
| 12 | 16,31 | quille | draft mode's (16,70, fantôme) → violet | (408, 1105) ×3,6, 0° | **virage** 1,5 temps au coin BL |
| 13 | 17,03 | quille | my spare keys (17,09) ; pastille « clé » | (651, 1105) ×3,3 | glissé |
| 14 | 19,16 | flanc droit | make another (19,36) | (844, 1005) ×3,4, **−62°** | **virage** 1,3 temps au coin BR |
| 15 | 20,38 | flanc droit | note.txt (20,44) → vert ; onglet de fichier | (922, 811) ×5,1, −62° | glissé |
| 16 | 22,52 | fanion | and yet (22,88) ; le mât et le fanion se tracent | (258, 264) ×4,2, 0° | **fouetté** 1 temps |
| 17 | 25,24 | — | (recul : le château, le haut de la pile) | (430, 420) ×2,3, −3° | respiration 4 temps |
| 18 | 25,79 | conteneur de travers | wrong (25,98) · fold (26,64) ; trait ondulé à 26,75 | (721, 363) ×3,4, −7° | fouetté 1 temps |
| 19 | 27,42 | première vague | such a lot (27,62, fantôme) | (210, 1158) ×3,6 | fouetté 0,57 temps |
| 20 | 28,04 | première vague | of wrong (28,10, fantôme) | (421, 1159) ×4,6 | glissé |
| 21 | 28,52 | première vague | folds (28,58) | (578, 1157) ×6,2 | glissé |
| 22 | 31,07 | image entière | refrain : we sail, (29,2) · we sail, (29,9) / and we sail, (30,7) / (31,54) / (32,12) | (512, 860) ×1, 0° | **zoom arrière** 29,515 → 31,068 (1 mesure) : l'écran, le clavier, la canette |

Différences de rythme avec la version actuelle : trois virages au lieu de quatre (aux coins de la coque, tous ≤ 62°, plus d'épingle à
114°) ; les trois conteneurs se lisent **à plat**, avec des retours chariot ; cadrages plus nombreux (22 contre 20) et plus courts.
À vérifier à l'audit : les cadrages 8 et 20 ne tiennent que ≈ 0,3–0,5 s (règle : 0,5 s) → regrouper « i've been up since » dans un seul
cadrage à 92 px (18 signes : il faut alors accepter 1 000 px de large ou descendre le plancher à 72 px sur ce cadrage) ou laisser la
caméra **glisser en continu** sur cette ligne (variante « défilement », à essayer en vidéo).

## Ce qui change dans le moteur pour B

1. L'**habillage** `editeur` (voir README) : c'est l'essentiel.
2. Le **dessin** `cargo.json`, avec une liste **`boites`** (x, y, largeur, couleur, numéro, rotation, arête liée ou décor) tracée en même
   temps que la ligne qu'elle contient ; château, mât, ligne de flottaison en décor daté par l'arête voisine.
3. Trois petites options de mise en page : `inside` (texte centré sur son arête, pour une boîte), **classe** par unité (4ᵉ valeur) pour
   la couleur sèche, rangs finaux **alignés à gauche** avec une invite.
4. Annotations nouvelles : `ondule` (trait ondulé sous la ligne) ; `croix` placée **de l'autre côté du trait** que le texte (sinon elle
   tombe sur le mot suivant) ; `fanion` dont la longueur suit le texte.
5. `floorPx: 96` transmis à l'audit ; pointe et pré-posé fournis par l'habillage.

Le fichier de paroles garde ses temps ; seuls changent `dessin`, `habillage`, les noms d'arêtes, les cadrages (`cad`) et les classes.
La maquette lit un fichier de mots de rechange (`?data=`) : c'est ainsi que les vraies paroles ont été essayées sans entrer dans le dépôt.

## Incertitudes propres à B

- **Corps 29–30 px** dans les conteneurs à l'image finale : le plus petit texte des trois propositions. Les lignes ont été lues en gros
  plan ; le refrain (60–68 px) et le nom du navire (53 px) portent l'image finale. Si Hamdi veut plus gros : deux conteneurs par ligne
  de paroles (pile de six rangs), ou une police à chasse fixe étroite (Iosevka, SIL OFL, 0,5 em : +20 % de signes ; paquet à ajouter).
- **Le navire se lit-il ?** Sur l'image finale oui (coque, pile, château, fanion), à faire confirmer ; la coque est très peu remplie.
- **Cadrages courts** sur les passages rapides (voir storyboard).
- **Clignotement du curseur** : petit, un temps sur deux (≈ 1,3 Hz), sans risque de photosensibilité ; à voir en mouvement.
- Le texte fantôme en italique gris est moins lisible que le pré-posé ivoire à 50 % du plan bleu : 5,9:1, à juger en vidéo.
- La coloration par classe demande de marquer les unités à la main (trois ou quatre mots par chanson).
