# Moteur 3D sur carte graphique : note de conception (phase 0, 18/11/2026)

Phase 0 seulement : une note, des essais de pile et un prototype. Rien n'est décidé ; la suite revient au propriétaire.
Branche `moteur-gpu-3d` (worktree à part, depuis `identite-console-retro`), commits locaux, aucun push. Rien de
`survol-pixel`, de `out/shorts/` ni de `index.json` n'a été touché. Aucune génération payante.

- Prototype et essais : `out/proto/moteur-gpu-3d/` (README, versions exactes, mp4 de 6 s, mesures brutes).
- Machine : MacBook Pro Intel i7-7820HQ 4 cœurs, 16 Go, macOS 13.7.8 ; AMD Radeon Pro 560 (4 Go) et Intel HD Graphics 630, toutes deux Metal 3.
- Charge 1 min pendant les mesures : 2,4–2,9 (d'autres processus tournaient).

## Résumé

- **Pile recommandée : wgpu-py 0.33.0 (Metal), en Python, sans navigateur.** Elle marche sur ce Mac, sur les deux
  cartes, que l'on choisit par leur nom ; une seule roue de 8,5 Mo dans un environnement local.
- **Le prototype est fait.** Une vallée en terrasses de 790 774 triangles, une caméra qui avance, 270×480 agrandi ×4 :
  **2,6 s pour 100 images** sur la Radeon, contre 64–214 s pour `survol.py`.
- **Répétable** : deux rendus sur la même carte donnent les mêmes octets (images natives et mp4). Entre la Radeon et
  l'Intel, 93 pixels diffèrent sur 23,3 millions.
- **Ce que la carte graphique ne règle pas** : le scintillement (2,97 % sans suréchantillonnage, 2,64 % avec 16
  échantillons par pixel) et la direction artistique. Le rejugement de Fable dit déjà que ce qui sépare `survol-pixel`
  de sa source « n'est plus le moteur ».
- **Coût de développement estimé : 5 à 7 jours d'agent** pour un moteur partagé et une identité avec 2 shorts de preuve.
- **Question à trancher avant tout développement** : nouvelle identité avec une signature propre, ou second moteur de
  `survol-pixel` (voir § 6).

## 1. Choix de la pile

### Ce qui a été essayé sur ce Mac

Le même triangle, avec une division flottante dans le shader, rendu en 270×480 par chaque pile (`essais/`).

| Pile | Résultat | Moteur graphique | Carte | Remarques |
|---|---|---|---|---|
| **wgpu-py 0.33.0** | marche | Metal (wgpu-native, dans la roue) | les deux, listées par `enumerate_adapters_sync()` et choisies par leur nom | roue x86_64 toute faite, 8,5 Mo ; shaders en WGSL ; cibles entières (`r8uint`) |
| **moderngl 5.13.0** | marche | OpenGL 4.1 d'Apple (`4.1 ATI-4.14.4`) | Radeon, prise d'office ; choix de l'Intel non essayé | pas de roue : compilé à l'installation (demande les outils Xcode) ; OpenGL est figé et déprécié par Apple |
| **Chrome 157 sans affichage** (playwright-core 1.65.1, WebGL2, donc three.js) | marche | ANGLE sur Metal | Radeon par défaut ; Intel avec `--force_low_power_gpu` | `--use-angle=gl` : contexte inutilisable (paramètres nuls) ; `--use-angle=swiftshader` : rendu logiciel, marche |
| **headless-gl (`gl` 8.1.6)** | **ne s'installe pas** | ANGLE compilé | — | npm compile ANGLE à l'installation et échoue (`python` absent du PATH) ; WebGL 1 seulement (d'après sa documentation) |
| taichi 1.7.2 (rappel, `facts.md`) | marche | Metal | Radeon | division non IEEE, parité avec numpy à 1–2 ulp près : écarté pour les rendus livrés |

Temps par image du triangle, relecture comprise : wgpu 5 ms (sur l'Intel ; la mesure sur la Radeon inclut la
compilation du shader), moderngl 10 ms, Chrome 24 ms (dont le transfert vers Node). À cette taille, le coût ne départage pas les piles.

Faits utiles relevés au passage :

- **Playwright et Chromium ne sont pas installés sur ce Mac** : pas de `playwright` dans `node_modules`, pas de cache
  `ms-playwright`. `render.mjs` ne peut donc pas tourner ici tel quel. L'essai passe par `playwright-core` et le
  Chrome du système, avec un profil temporaire.
- `render.mjs` force SwiftShader par défaut (`--gl swiftshader`) et capture en JPEG qualité 92 : c'est du rendu
  logiciel, et un JPEG n'est pas exact au pixel. Pour un moteur sur carte graphique il faudrait une variante qui lit
  les pixels par `readPixels`.
- Le Chrome du système se met à jour seul. Pour figer une version il faudrait télécharger un Chromium épinglé
  (environ 170 Mo), non fait.

### Comparaison

| Critère | wgpu-py | three.js dans Chrome | moderngl |
|---|---|---|---|
| Marche ici, sur la carte dédiée | oui | oui | oui |
| Choix de la carte | par son nom, dans le code | par un drapeau de lancement | implicite |
| Version figée | oui (`wgpu==0.33.0`) | non sans Chromium épinglé | oui, mais compilé sur place |
| Dépend de | Metal | ANGLE puis Metal | OpenGL d'Apple, déprécié |
| Rendu logiciel de secours | non essayé | oui (SwiftShader, celui du conteneur de la campagne) | non |
| Travail de moteur | maillages et shaders à écrire | graphe de scène, ombres et caméras fournis | maillages et shaders à écrire |
| Suite du pipeline | Python, comme `survol-pixel` et `trait-continu` : cartouches Pillow, tuyau ffmpeg | contrat `window.renderAt(t)` du dépôt, texte par le DOM (anticrénelé) | Python |
| Déjà dans le dépôt | non (une roue à ajouter) | three 0.187.0 oui ; Playwright non installé ici | non |

### Recommandation

**wgpu-py.** Raisons :

1. La carte est choisie par son nom et le rendu échoue si elle manque : pas de bascule silencieuse vers l'Intel ou
   vers un rendu logiciel.
2. La version est figée par une ligne de `requirements.txt`, sans navigateur qui se met à jour.
3. Le pixel art indexé se rend en **codes entiers** (voir § 3), ce que le graphe de scène de three.js n'apporte pas :
   il faudrait de toute façon écrire ses propres shaders.
4. Le reste du pipeline existe déjà en Python.

Contrepartie à connaître : c'est une dépendance nouvelle, alors que three.js est déjà dans `package.json`. Mais la
voie three.js demande elle aussi une installation sur ce Mac (Playwright et un Chromium épinglé).

**three.js dans Chrome reste le plan de repli** si le moteur doit un jour tourner dans le conteneur sans carte
graphique : c'est la seule voie essayée qui a un rendu logiciel.

**moderngl est écarté** : il marche, mais sur une API qu'Apple n'entretient plus.

## 2. Rendu image par image, déterministe

### Principe (appliqué par le prototype)

- **Horloge pilotée** : l'image n est un pur calcul de t = n / 30. Aucun temps réel, aucune boucle d'animation, aucun
  état conservé d'une image à l'autre. Une image isolée se rend sans les précédentes (stills).
- **Graine** dans `short.json` : le monde (bruit, matières) sort de `numpy.random.default_rng(graine)`, sur le processeur.
- **Tout ce qui peut se calculer une fois se calcule sur le processeur** : relief, matières, ombres portées du relief,
  maillage, trajectoire de caméra (en double précision, convertie en simple à l'envoi).
- **La carte graphique ne produit que des entiers** : une cible `r8uint`, sans mélange, sans anticrénelage flottant,
  sans texture filtrée. Les hachages du shader sont en arithmétique entière, identique sur toutes les cartes.
- **Sortie** : 129 600 octets relus par image (270×480), palette appliquée par numpy, RVB envoyé par un tuyau à ffmpeg
  avec les réglages de `render.mjs` (`libx264 veryfast crf 14 yuv420p`, 30 i/s, `+faststart`, fichier `.part.mp4`
  renommé). ffmpeg agrandit ×4 au plus proche voisin (`scale=1080:1920:flags=neighbor`).

### Ce qui est mesuré

| Comparaison | Résultat |
|---|---|
| Radeon, deux lancements séparés, 180 images | **0 pixel d'écart** ; même md5 des images natives ; même md5 du mp4 |
| Intel, deux lancements séparés | 0 pixel d'écart |
| Radeon contre Intel | **93 pixels sur 23 328 000 (0,0004 %)** ; 106 images sur 180 identiques ; au pire 3 pixels dans une image |
| Essai du triangle en couleurs flottantes, Radeon contre Intel | 3 198 pixels sur 129 600 diffèrent d'un niveau |

### Ce qui change d'une carte à l'autre

- L'arithmétique flottante des shaders : division, fusion produit-addition. C'est le fait déjà noté pour taichi.
  L'essai du triangle le confirme : 2,5 % des pixels diffèrent d'un niveau quand on sort une couleur flottante.
- Avec des codes entiers, il ne reste que les fragments posés exactement sur une frontière : bord de triangle, seuil
  de palier de brume. D'où 93 pixels au lieu de dizaines de milliers.
- Le pilote et la version de macOS, la version de wgpu-native : non essayés ici, à supposer différents.

### Comment le tester

1. **Sur la carte de référence, au bit près.** `short.json` garde le nom de la carte, la version de wgpu et le md5
   des images natives (le prototype l'imprime : `md5NativeIndexFrames`). Un nouveau rendu doit redonner ce md5.
   Le md5 se prend sur les indices de palette, avant l'encodage.
2. **Sur une autre carte, avec une tolérance.** `mesures.py ecart` compte les pixels différents. Seuil proposé :
   au plus 0,01 % des pixels par image (13 pixels natifs), soit quatre fois le pire cas mesuré.
3. **Refus du rendu logiciel.** Le moteur s'arrête si la carte demandée n'est pas trouvée.

Limite : le md5 du mp4 n'est stable que pour une même version de ffmpeg et de libx264. Celui des images natives ne
dépend pas de l'encodeur.

## 3. Le pixel art en 3D

### Chaîne proposée (celle du prototype)

1. **Passe géométrie** à SS × (270×480), dans une cible entière. Chaque fragment écrit un code :
   matière × 8 + palier de brume. La matière est un attribut du sommet, sans interpolation.
2. **Passe de vote** : chaque pixel natif prend le code majoritaire de ses SS × SS échantillons ; à égalité, le plus
   petit code. Aucune moyenne de couleurs : on reste dans la palette. C'est le `vote4` de `survol.py`, avec 16 ou 64
   échantillons au lieu de 4.
3. **Palette par table** : code → indice de palette → RVB, sur le processeur. Il n'y a pas de quantification d'une
   image en couleurs : une quantification ou un tramage après coup bascule d'une image à l'autre et dépend de la carte.
4. **Agrandissement ×4 au plus proche voisin** par ffmpeg.

### Ombres, brume, ciel, textes

- **Ombres portées du relief** : calculées une fois par monde sur le processeur, rangées dans la matière (variante
  ombrée). Pas de carte d'ombre sur la carte graphique, donc ni acné ni scintillement d'ombre.
- **Contremarches** : trois tons selon l'orientation de la paroi, fixés à la construction du maillage.
- **Ombres d'objets mobiles** (nuages) : non faites. Proposé : un masque monde calculé une fois par image, lu en
  coordonnées entières, comme `disk_mask`.
- **Brume en 6 paliers** : seuils sur la distance à la caméra, frontière crénelée fixée dans le monde par un hachage
  entier par case de 4 unités. Chaque matière se fond dans la rampe de sa famille (5 familles), le dernier palier est
  la couleur du bas du ciel.
- **Ciel en 5 paliers** selon l'élévation du rayon, calculé par numpy ; il suit le roulis.
- **Textes** : non faits. Proposé : cartouches Pillow sans anticrénelage, posés sur l'image d'indices, comme aujourd'hui.
- **Plan de coupe** : non fait. Sur un maillage, c'est un retrait de cases et des parois colorées par strate selon
  l'altitude.

### Face aux limites mesurées de `survol-pixel`

| Limite de `survol-pixel` | Mesure connue | Ce que le prototype montre |
|---|---|---|
| **Coût** | 63,9–214,4 s pour 100 images sur processeur | **2,4–3,3 s pour 100 images**, soit 20 à 80 fois moins. Scène plus simple : voir § 5 |
| **Silhouettes en marches d'une cellule** | le coût fixe la taille des cellules | des cases deux fois plus fines (2,8 millions de triangles) ne coûtent rien de plus : 2,4 s pour 100 images. Les marches en plan sont deux fois plus petites, pas supprimées |
| **Plusieurs rayons par pixel et monde plus grand** | passe A+B+C (4 rayons par pixel, monde 2,4 à 3 fois plus grand) : de 19,6–63,1 à 63,9–214,4 s pour 100 images | 16 échantillons : +0,1 s pour 100 images ; 64 : +0,7 s |
| **Scintillement** | A-B-A 2,1 % sur le short de Machu Picchu, 4,5 % au piqué ; source 2,4–3,4 % (mesures de Fable, sur fichier décodé) | A-B-A natif : 2,97 % avec 1 échantillon, 2,64 % avec 16, 2,61 % avec 64, **1,95 %** avec des cases deux fois plus fines |
| **Parité processeur / carte graphique** | taichi : 1–2 ulp d'écart | sans objet : un seul moteur, plus de parité à tenir |

Lecture honnête du scintillement :

- **Le suréchantillonnage ne le règle presque pas** (−0,3 point). La note de `survol-pixel` l'avait déjà mesuré
  (vote 2×2 : −0,15 point) et en donnait la cause : des contremarches en bandes d'un pixel sur les pentes lointaines.
- Le prototype est au niveau de la source et de `survol-pixel`, sans réglage, mais les méthodes diffèrent (indices
  natifs ici, fichier décodé chez Fable) et la scène n'est pas la même : ces chiffres ne se comparent pas au point près.
- Ce que la carte graphique apporte, c'est le prix des remèdes : géométrie plus fine (mesuré : −0,7 point), terrasses
  regroupées au loin, essais de caméra en quelques secondes au lieu de dizaines de minutes.

Pour supprimer les marches en plan, il faut des terrasses tracées par courbes de niveau (polygones extrudés) au lieu
de cases carrées. Non essayé.

## 4. Compatibilité avec `check.py` et le pipeline des shorts

| Élément | État |
|---|---|
| **`check.py`** | Le mp4 du prototype a le bon format, vérifié par ffprobe : 1080×1920, 30/1, h264, yuv420p, aucune image noire. Il lui manque ce qu'un essai n'a pas : durée de 10 à 20 s, piste audio, `short.json`, `narration.json`, `src/`. Rien à changer dans `check.py` |
| **Son et voix** | La vidéo muette sort au même format que celle de `survol-pixel`. La suite est inchangée : `sound.py`, `assemble.py mux`, copie vers `short_novo.mp4`, `tts.py --engine files --replace` |
| **`short.json.reproduce`** | Même forme que celle de `survol-pixel` : `.venv/bin/python …/src/video.py --out …`, puis son, mux, voix. Champs à ajouter : carte, moteur graphique, version de wgpu, suréchantillonnage, md5 des images natives |
| **Stills** | `--stills 0.5,3,5.5` écrit des PNG 1080×1920 ; une image se rend seule, sans les précédentes |
| **Convention des moteurs Python** | Un module partagé copié à l'identique dans le `src/` de chaque short (comme `survol.py` et `traceur.py`), un `video.py` par short |
| **`bootstrap_studio.py`** | Copie déjà les `.py` du `src/` d'un short de preuve : rien à changer pour le code. À ajouter : `wgpu==0.33.0` dans la mise en place du studio et dans le « Set-up » de `AGENTS.md` |
| **`slot.sh`** | Il compte des cœurs. Deux rendus sur la même carte se partagent sa mémoire : prévoir un seul rendu à la fois sur la carte graphique |
| **Catalogue** | Une fiche `out/library-cards/wgpu.json` et une ligne dans `catalogue.md` ; `catalogue_scan.py --check` |
| **`recognition.py`** | Il compare couleurs et contours. Une identité en pixel art survolé sera proche de `survol-pixel` si la palette l'est |
| **Machine de rendu** | Les rendus se font sur le Mac. Le conteneur de la campagne n'a pas de carte graphique : non essayé |

## 5. Coûts

### Rendu (mesuré sur le prototype)

| Réglage | s pour 100 images | Détail par image |
|---|---|---|
| Radeon, 16 échantillons, 790 774 triangles | **2,6–2,7** | 19,6 ms carte graphique et relecture ; 5,5 ms palette et ciel ; 0,8 ms tuyau |
| Intel HD 630, mêmes réglages | 2,5–3,1 | 18,5–24,4 ms carte graphique |
| Radeon, cases de 0,5 (2 843 698 triangles) | 2,4 | 16,7 ms carte graphique |
| Radeon, 64 échantillons | 3,3 | 26,4 ms carte graphique |

- À ajouter une fois par rendu : monde et maillage 0,4 s (2,4 s en cases de 0,5), compilation des shaders 2–3 s.
- Un short de 18,6 s (558 images) prendrait environ 15 s à ce rythme.
- **Attendu pour un vrai short : 5 à 15 s pour 100 images** (estimation, non mesurée). Le prototype n'a ni nuages,
  ni arbres, ni cartouches, ni plan de coupe, et ces parties restent en partie sur le processeur.
- Le temps par image varie peu avec la géométrie : il est dominé par l'aller-retour avec la carte, pas par le dessin.

### Développement (estimation, en jours d'agent)

| Lot | Jours |
|---|---|
| Moteur partagé : maillage par cases et par courbes de niveau, caméra, brume, palette, vote, objets (arbres, nuages et leurs ombres), plan de coupe, cartouches, garde-fous (zones sûres, couleurs par image, caméra au-dessus du relief), tests de répétabilité | 2 à 3 |
| Identité par la fabrique : directions, challenge, 2 shorts de preuve, stills, son | 2 à 3 |
| Intégration et revue : voix, `index.json`, fiche de librairie, catalogue, reconnaissance, juge à l'aveugle | 1 |
| **Total** | **5 à 7** |

Repère : `survol.py` fait 1 249 lignes et a demandé plusieurs passes de réglage. Le gain attendu est sur
la boucle de réglage : un short entier se re-rend en moins d'une minute au lieu de 6 à 20 minutes.

## 6. Risques

1. **Dépendance à la machine et au pilote.**
   - Tout repose sur Metal, sur un Mac Intel dont le système n'évolue plus.
   - wgpu-py est en version 0.x : son API change entre versions. D'où la version exacte.
   - D'une carte à l'autre, l'image n'est pas identique au bit (93 pixels sur 23,3 millions).
   - Sans carte graphique (conteneur), rien n'a été essayé.
2. **Nouvelle identité ou dérivation.**
   - La règle de `AGENTS.md` vise une identité qui reprend un moteur existant et ne change que fond, palette et
     polices. Ici le moteur est nouveau : ce n'est pas une dérivation au sens de la règle.
   - Mais si le rendu reste « un petit monde en pixel art 16 bits survolé », c'est la signature de `survol-pixel`.
     Les deux seraient confondues, par l'œil comme par `recognition.py`.
   - Deux issues propres, à choisir par le propriétaire :
     - **une nouvelle identité** avec sa signature : autre palette, autres polices, autre transition, autre son, et
       une matière que le lancer de rayons ne sait pas faire (vrais volumes, objets en 3D, courbes de niveau) ;
     - **un second moteur pour `survol-pixel`** : même identité, shorts de preuve re-rendus. C'est exclu de cette
       mission, mais c'est l'usage le plus direct de ce travail.
3. **Le moteur ne règle pas ce qui reste à régler.**
   - Le rejugement de Fable classe les écarts restants : atoll presque immobile, mer vide, forêt en rangs, reliefs
     trop réguliers. Ce sont des choix de scène, pas de moteur.
   - Le scintillement ne baisse pas tout seul (§ 3).
4. **Travail à refaire et entretien.**
   - Nuages, arbres, coupe, cartouches et réglages de brume de `survol.py` sont à réécrire.
   - Deux moteurs 3D à entretenir, dont un en WGSL.
5. **Déterminisme.**
   - Le md5 des images natives ne vaut que pour une carte, un pilote et une version de wgpu.
   - Toute sortie flottante ajoutée au shader (dégradé, mélange, texture filtrée) ramène les écarts de l'essai du triangle.
6. **Règles d'identité.**
   - Le prototype ne reprend ni sprite, ni logo, ni texte, ni son. Sa scène (une vallée en terrasses avec une rivière)
     et sa palette sont provisoires.
   - Un moteur de survol rapide pousse vers le simulateur de vol : garder la règle « la forme, pas le contenu » et
     l'absence d'élément de jeu.

## 7. Prototype

Fait, en environ 1 h : `out/proto/moteur-gpu-3d/proto.py`, 6 s, 180 images, `sortie/proto.mp4` (2,5 Mo) et 3 stills.

- Monde : 448 × 704 unités, terrasses de 2,5 unités de haut, rivière, sable, prés, forêt, roche, neige ; graine 2611.
- Caméra : avance de 30 unités par seconde en suivant la rivière, tangage de −19° à −27°, roulis dans les virages.
- Ce qu'il n'a pas : nuages, arbres, objets, textes, plan de coupe, son. Ce n'est pas un short de preuve.
- Défauts visibles : berges en dents de scie d'une case (réduites de moitié avec `--cell 0.5`), ciel en bandes
  larges, contremarches lointaines en hachures.

Mesures brutes : `out/proto/moteur-gpu-3d/sortie/mesures_*.json` et le README du prototype.

## 8. Seconde maquette, visée « qualité source » (décision 47, 18/11/2026)

Le premier prototype était un test technique en aplats. La seconde maquette garde le même moteur et vise le niveau de
la vidéo source : `out/proto/moteur-gpu-3d/maquette-source/` (mp4 de 5 s, planche source / maquette, README avec l'avis
détaillé). Elle a été faite en deux temps : une première version (commit `fd1733b`), puis une reprise sur ses écarts.

**Ce qu'elle prouve**

- Le moteur porte une scène riche sans changer de principe : 2,6 millions de triangles, 10 320 arbres, 300 nuages en
  tas de boules ombrées, 34 000 traits d'écume, une carte peinte du sol, les ombres portées du relief, des arbres et
  des nuages, une brume en paliers tramés. Tout reste en indices de palette.
- Je la juge au niveau de la source pour la qualité du rendu : mer, écume, nuages, horizon, terrasses et bois. Restent
  différents les nuages vus de près côté soleil, des prés en dégradés tramés plutôt qu'en aplats, et un mouvement un peu
  plus lent (22 % de pixels changés par image contre 28 %).
- **Le scintillement se traite par le contenu.** Par le même calcul sur fichier décodé : maquette 3,19 %, source 4,36 %.
  En mesure native, 4,45 % au départ, 3,02 % à la fin. Trois leviers ont compté :
  - la trame se choisit dans l'espace de l'écran (matrice de Bayer sur les pixels natifs) et non par texel du monde ;
  - les traits fins (écume) sont de la géométrie que le shader élargit pour ne jamais passer sous un pixel ;
  - le détail plus fin qu'un pixel est retiré au loin (réductions de la carte par vote, contremarches d'un seul ton).
- La boucle de réglage est courte : 14 allers-retours en 30 minutes environ, chacun avec un rendu complet de 5 s.

**Son coût**

- **2,5–2,9 s pour 100 images** sur la Radeon (charge 4), soit 25–29 ms par image : le coût du premier prototype. La
  richesse de la scène ne coûte presque rien par image.
- 7,4 s de préparation du monde par rendu, sur le processeur.
- Répétable : deux rendus sur la Radeon donnent le même md5 (images natives et mp4).
- **L'écart entre cartes monte à 0,04 % des pixels** (0,11 % au pire sur une image), contre 0,0004 % pour le prototype
  en aplats. La tolérance de 0,01 % proposée au § 2 ne tient pas pour une scène tramée : il faut la fixer autour de
  0,5 % par image, ou rendre toujours sur la même carte.

## Suite possible

1. Le propriétaire tranche : nouvelle identité ou second moteur de `survol-pixel`.
2. S'il s'agit d'une nouvelle identité : la faire passer par la fabrique, avec ce moteur comme contrainte technique
   et une signature distincte de `survol-pixel`.
3. Avant tout rendu de preuve : terrasses par courbes de niveau, terrasses regroupées au loin, et une mesure du
   scintillement sur une scène complète.
