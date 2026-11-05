# Directions d'identité — repérage du 2026-11-05

Agent de repérage (scout) de la fabrique d'identités. Quatre directions nouvelles ; deux seront produites par des studios.
Aucun code de scène, aucun rendu dans le dépôt, aucun commit. Les seuls essais techniques ont tourné dans un répertoire
temporaire hors du dépôt (détail en fin de fichier).

## Ce qui est pris (synthèse des 18 identités)

- **Fonds sombres (9)** : neon-lab (quasi-noir néon), cosmos-doc (noir spatial), liquid-chrome (graphite chromé), topo-relief
  (vert forêt 3D), tableau-craie (vert ardoise), pixel-arcade (marine pixel), brut-meme (noir/jaune), atelier-papier et
  cabinet-curiosites (bleu nuit). Le menu n'a pas besoin d'un dixième fond sombre.
- **Crème / papier (8)** : swiss-data, bauhaus-kinetic, riso-zine, atlas-grave, aquarelle-conte, gazette-1900, carnet-archives
  (kraft), papier-decoupe (tapis vert + bandes de papier). Le papier découpé, le collage et le stop-motion à 12 i/s sont pris.
- **Pastel** : pastel-diorama (rose, jouets 3D ronds).
- **Teintes de fond jamais utilisées** : orange, lilas, bleu ciel pâle, gris aluminium clair.
- **Mécaniques déjà vues** : le tracé qui se dessine seul (tableau-craie, atlas-grave), le pari sur une course physique
  (pixel-arcade, liquid-chrome), le chiffre géant (swiss-data, brut-meme), le pendule chromé (liquid-chrome), la une de journal
  (gazette-1900), le volet plein cadre (swiss-data, bauhaus-kinetic).
- **Familles, en nombre d'identités qui les ont prouvées** : histoire 8, explicatif 8, événements 5, engagement 5, géographie 4,
  abstrait 3, enfants 3. Les directions ci-dessous visent surtout enfants, abstrait, géographie et événements. Aucune ne
  prend histoire ni explicatif comme famille principale.

## Vue d'ensemble

| # | Slug | Fond | Librairie « Non » qui porte la signature | Langage | Familles | Public | Coût estimé (s/100 images) |
|---|---|---|---|---|---|---|---|
| 1 | `trait-continu` | gris aluminium clair dans un cadre orange | shapely + opensimplex (pycairo pour le tracé) | **Python** | enfants, geographie | kids 6–10 | **5** au repos, mesuré ; ≈ 8–12 en charge |
| 2 | `carte-meteo` | bleu ciel pâle (mer) et vert tendre (terre) | topojson-client (+ world-atlas, + plugins GSAP DrawSVG et MotionPath) | **JavaScript** | geographie, evenements | adults, teens | ≈ 15 au repos ; 30–45 en charge (estimé) |
| 3 | `tableau-depart` | anthracite (le seul fond sombre) | Web Animations API (seek par `currentTime`) | **JavaScript** | evenements, engagement | teens, adults | **12** au repos, mesuré ; 25–40 en charge |
| 4 | `domino-cascade` | lilas clair | Rapier (`@dimforge/rapier3d-compat`) | **JavaScript** (+ pré-simulation Node) | abstrait, engagement | kids, teens, adults | **44** au repos, mesuré ; 60–90 en charge |

Contraintes de l'ensemble : un seul fond sombre (3) ; aucun style papier ; une direction pour enfants (1) ; deux directions
couvrent événements ou engagement (2, 3, 4) ; une librairie principale Python (1) ; des librairies principales JavaScript
(2, 3, 4) ; toutes sous ≈ 90 s/100 images.

---

## 1. `trait-continu` — Trait continu

### Slug et nom
`trait-continu` — **Trait continu** (l'écran à manivelles).

### Promesse en une phrase
Un jouet à dessin orange dont l'écran gris aluminium trace toute l'idée d'**un seul trait graphite ininterrompu**, piloté par
deux molettes qui tournent sous l'écran ; on le secoue, et tout s'efface.

### Signature en 4 traits
1. **Type** : titres Fredoka 700, ronds et pleins, en encre sombre sur la bande haute du cadre orange. Jamais de texte écrit
   par le trait.
2. **Palette** : orange jouet (cadre) + gris aluminium (écran) + un seul trait graphite. L'écran reste monochrome.
3. **Matière / forme** : un cadre en plastique épais aux coins arrondis, avec un reflet brillant ; deux molettes blanches en bas.
   Un écran à grain de poudre (bruit opensimplex). **Une ligne unique et continue**, de 5 px, sans lever le crayon, dont les
   courbes sont **en escalier** : pas de 6 px, comme avec deux molettes horizontale et verticale.
4. **Transition signature : « la secousse »**. Le cadre entier tremble (± 18 px, 3 oscillations amorties en 0,6 s), puis le
   trait se dissout sous la poudre (masque de bruit, 0,8 s) et l'écran redevient vierge.

### Palette
| Rôle | Hex | Contraste calculé |
|---|---|---|
| Fond = cadre | `#F26A21` (orange jouet) | — |
| Surface = écran | `#D3D4CE` (gris aluminium) | — |
| Trait | `#3A3D42` (graphite) | 7,31:1 sur l'écran |
| Accent 1 : étiquettes de légende | `#FFF8EE` (crème) | texte `#22252A` dessus : 14,58:1 |
| Accent 2 : repères sur l'écran (point de départ, flèche) | `#1D47A8` (bleu jouet) | 5,59:1 sur l'écran |
| Accent 3 : bandeau sombre du cadre | `#C2410C` (orange brûlé) | texte `#FFF8EE` dessus : 4,91:1 |
| Texte sur le cadre | `#1A1410` | **5,96:1** sur `#F26A21` (≥ 4,5 : corps autorisé) |
| Texte sur l'écran | `#22252A` | 10,31:1 |

Interdit : texte blanc sur l'orange (3,06:1), réservé aux titres ≥ 90 px gras s'il le faut, et de préférence jamais.

### Typographie
- **Fredoka** (installée, `@fontsource/fredoka`, aucune identité ne l'utilise) : titres en 700, de 96 à 120 px, sur la bande
  haute du cadre.
- **Lexend** (**à ajouter** : `"@fontsource/lexend": "^5.3.0"` dans `package.json`, version 5.3.0 vérifiée). Conçue pour
  faciliter la lecture, utile pour un public de 6 à 10 ans. Corps 600 à 58–64 px ; légendes 500 à 54 px sur étiquette crème.
- Texte posé par `textpng.py` (PIL lit les `.woff2`, c'est un fait vérifié) et composé en numpy. pycairo ne charge pas les
  `.woff2` simplement.

### Langage de mouvement
- **Le trait** avance à vitesse **constante** (650–900 px/s, linéaire : les molettes n'ont pas d'easing), avec un pas de
  6 px. Les molettes tournent en proportion exacte de dx (molette gauche) et de dy (molette droite), et la vue rapprochée en
  incrustation les montre. C'est l'indice visible qui fait comprendre l'objet.
- **Titres** : apparition en `back.out(1.6)` sur 0,3 s (léger rebond d'un autocollant), décalage de 0,08 s par mot.
- **Légendes** : étiquette crème qui glisse de 40 px en `power2.out` sur 0,25 s.
- **Secousse** : sinus amorti à 5 Hz sur 0,6 s, puis dissolution de 0,8 s. 2 à 3 secousses au plus par short.
- **Jamais** : deux traits à la fois, un trait en couleur, un trait levé, du texte écrit par le trait, un zoom sur l'écran
  (le jouet reste entier et cadré), un fondu enchaîné classique.

### Librairies
- **Librairie « Non » qui porte la signature : shapely 2.2.0** (PyPI, vérifiée par `pip index versions shapely`). Elle
  construit **le chemin unique**. Elle simplifie un contour (`simplify`), le rééchantillonne (`segmentize`), le décale
  (`offset_curve` pour un double trait de relief), raccorde plusieurs formes en un parcours continu (`linemerge`, puis des
  ponts calculés entre composantes) et coupe le chemin à une abscisse donnée (`substring`). L'état du trait à l'instant t
  est donc `substring(chemin, 0, v·t)` : c'est déterministe, on le calcule soi-même, sans horloge.
- **opensimplex 0.4.5.1** (PyPI, vérifiée), aussi en « Non » dans le catalogue : grain de poudre de l'écran, masque de la
  dissolution, légère vibration du trait (± 0,5 px). Graine fixée.
- **pycairo** (« Oui », déjà dans `.venv`) dessine le cadre, l'écran et le trait. Pillow / `textpng.py` pour les textes,
  numpy pour la composition, ffmpeg en `rawvideo` (pipe `bgra`).
- **Pipeline** : un script Python `src/video.py` rend chaque image i (t = i/30) en pur calcul de t, sans état ; image →
  stdin ffmpeg → `video.mp4` ; puis `sound.py` (cliquetis de molettes : preset `tick`, et `thud` pour la secousse),
  `assemble.py mux` et `tts.py --engine files`.
- **Écarté : skia-python 144.1** (PyPI, existe ; roue manylinux_2_28 cp311). **Son import échoue ici** :
  `ImportError: libEGL.so.1`. Le paquet système `libegl1` manque, et un lien vers le `libEGL.so` de Chromium ne suffit pas
  (`undefined symbol: eglQueryString`). Il faudrait passer par `apt-get install libegl1`, ce que la règle des studios
  interdit. pycairo fait le même travail.
- **Contours géographiques** : les tracer à la main, en polygones de 40 à 80 points, comme atlas-grave l'a fait pour ses
  côtes. Alternative : exporter une fois `world-atlas` en JSON via Node (voir la direction 2). L'Hexagone et la botte se
  dessinent très bien à la main ; l'escalier des molettes absorbe la simplification.
- **Mesure** (scratchpad, machine calme) : 100 images 1080×1920 de cadre + écran + trait de 352 points (shapely) + grain +
  encodage x264 = **4,94 s**.

### Familles et sujets
**enfants**
1. **« Dessine un escargot d'un seul trait »** (14 s). La spirale part du centre et s'enroule ; la coquille grandit avec
   l'escargot en ajoutant des tours ; chez la plupart des espèces, elle tourne vers la droite. Fin : « Et toi, ta spirale
   tourne dans quel sens ? »
2. **« Araignée ou insecte ? Compte les pattes ! »** (15 s). Une fourmi tracée d'un trait : 3 parties, 6 pattes. Secousse.
   Une araignée d'un trait : 2 parties, 8 pattes. Conclusion : l'araignée n'est pas un insecte.

**geographie**
3. **« Pourquoi on appelle la France l'Hexagone »** (15 s). Le trait fait le tour de la France puis la recouvre de 6 côtés
   droits : 3 façades maritimes (Manche et mer du Nord, Atlantique, Méditerranée) et 3 frontières terrestres (nord-est,
   Alpes, Pyrénées).
4. **« L'Italie a la forme d'une botte »** (14 s). Le trait suit la botte ; des repères bleus marquent le talon (Pouilles)
   et la pointe (Calabre) ; la Sicile arrive au bout comme un ballon qu'on vient de frapper.

Aucun de ces sujets n'est dans `out/shorts`.

### Public
**kids 6–10** : rythme de 3–4 s par idée, ≤ 4 mots à l'écran par temps, voix à 2,0–2,3 mots/s, question d'enfant en
accroche, pas de CTA pressant. Ça marche aussi pour les adultes, sur le registre de la nostalgie du jouet.

### Voisines et différences
- **tableau-craie** (tout se dessine seul) :
  1. le fond est un gris aluminium clair dans un cadre orange, pas un tableau vert sombre ;
  2. le trait est **un seul trait graphite continu en escalier** au lieu de traits de craie libres et multicolores ;
  3. on efface en **secouant tout le cadre**, pas d'un coup de chiffon horizontal.
- **pastel-diorama** (enfants) :
  1. un objet plat vu de face, pas un diorama 3D sur socle de feutre ;
  2. orange, gris et graphite, aucun rose pastel ;
  3. pas de personnage récurrent : le jouet est le seul personnage.
- **atlas-grave** (carte qui se trace) :
  1. une ligne unique de 5 px de graphite, pas une gravure à hachures sur parchemin ;
  2. Fredoka ronde au lieu de Cinzel ou Cormorant ;
  3. aucun cartouche, aucun sceau, aucune rose des vents : l'écran reste vide en dehors du trait.

### Coût estimé
**≈ 5 s/100 images au repos (mesuré)**, ≈ 8–12 s en charge en comptant les textes composés en numpy. C'est comparable à la
famille papier (3,6–3,9 s, même chaîne Python → ffmpeg) et 10 fois moins que Manim sous contention (19,1 s). Un short de
15 s demande ≈ 25 s de rendu.

### Risques
- **Ressemblance de marque** : le jouet à deux molettes au cadre rouge et au lettrage doré est un habillage commercial connu.
  Il faut garder le cadre **orange**, sans aucun lettrage sur le cadre, des molettes blanches unies, et ne jamais écrire de
  nom de produit. Ne pas appeler l'identité par un nom de marque.
- **Lisibilité** : un trait de 5 px graphite sur gris (7,3:1) se lit bien, mais un dessin trop détaillé devient illisible
  sur téléphone. Viser 300 à 900 points par dessin et de grandes formes.
- **Rythme** : le trait linéaire peut paraître lent. Le chemin doit faire 2 500 à 5 000 px par scène, soit 3–6 s à 800 px/s.
- **Zones sûres** : les molettes tombent dans les 320 px du bas ; c'est voulu, elles sont décoratives. Le titre se place
  entre 230 et 470 px.
- **Photosensibilité** : la secousse ne change pas la luminance. Rien à signaler.
- **Technique** : `linemerge` ne relie pas des formes disjointes. Il faut calculer soi-même les ponts (segment le plus court
  entre composantes), et ces ponts font partie du dessin.

---

## 2. `carte-meteo` — Carte Météo

### Slug et nom
`carte-meteo` — **Carte Météo** (le bulletin).

### Promesse en une phrase
Une carte météo de télévision, mer bleu ciel pâle et terres vert tendre, où les isobares blanches ondulent, où des
pastilles de température pop, et où **un front froid à triangles bleus balaie l'écran** pour changer de sujet.

### Signature en 4 traits
1. **Type** : Outfit 800 pour les titres en bandeau, Atkinson Hyperlegible 700 pour les chiffres dans les pastilles.
   Les chiffres sont lisibles d'un coup d'œil.
2. **Palette** : bleu ciel pâle (mer) + vert tendre (terres) + rouge front chaud / bleu front froid / orange chaleur, texte
   bleu nuit. Aucun crème, aucun noir.
3. **Matière / forme** : aplats de carte nets, isobares blanches de 4 px qui ondulent lentement, traînées de vent (2 000 à
   3 000 particules à courte traîne), **pastilles rondes** de température, pictogrammes météo faits de formes simples
   (soleil, nuage, gouttes).
4. **Transition signature : « le passage du front »**. Une ligne de front froid (triangles bleus) ou chaud (demi-cercles
   rouges) traverse tout le cadre en diagonale en 0,9 s ; derrière elle, la carte a changé : nouveau zoom, nouvelles
   pastilles.

### Palette
| Rôle | Hex | Contraste calculé |
|---|---|---|
| Fond = mer | `#CFE6F5` | — |
| Surface = terres | `#DCEFC8` ; cartes et bandeaux `#FFFFFF` | — |
| Accent 1 : front chaud / record | `#D63A2A` | 4,67:1 sur blanc ; blanc dessus 4,67:1 |
| Accent 2 : front froid / pluie | `#1F5FD6` | 5,73:1 sur blanc ; blanc dessus 5,73:1 |
| Accent 3 : chaleur (pastilles) | `#F59A2C` | décoratif (2,2:1 sur blanc) ; texte `#10263D` dessus : 6,98:1 |
| Texte | `#10263D` (bleu nuit) | **11,92:1** sur la mer, 12,6:1 sur les terres, 15,37:1 sur blanc |
| Texte secondaire | `#3E5A72` | 5,6:1 sur la mer |

### Typographie
- **Outfit** (**à ajouter** : `"@fontsource/outfit": "^5.3.0"`, version 5.3.0 vérifiée) : titres 800, 96–120 px, dans un
  bandeau blanc en haut ; sous-titres 600, 64 px.
- **Atkinson Hyperlegible** (**à ajouter** : `"@fontsource/atkinson-hyperlegible": "^5.3.0"`, version 5.3.0 vérifiée) :
  chiffres des pastilles 700, 72–110 px ; corps 700, 56–60 px ; noms de villes 54 px.
- Les deux paquets sont nouveaux : aucune identité n'a ce couple.

### Langage de mouvement
- **Pastilles** : pop en `back.out(1.4)` sur 0,35 s, décalage de 0,06 s entre pastilles (de la côte vers l'intérieur des
  terres). Le chiffre défile de l'ancienne valeur à la nouvelle sur 0,5 s en `power2.out`.
- **Carte** : panoramique et zoom par interpolation de la projection d3 (`geoConicConformal` centré France), 1,5–2,5 s,
  `sine.inOut`.
- **Isobares** : champ de pression = bruit 3D à évolution lente (`svi.js` noise3), courbes par `d3.contours`, recalculées à
  chaque t. Un cycle dure environ 20 s, donc elles respirent sans jamais clignoter.
- **Vent** : particules advectées dans le champ ; la position à t est calculée par intégration depuis t = 0 avec un pas
  fixe (`window.SEQUENTIAL = true`), ou mieux, précalculée en Node et rejouée.
- **Front** : `power2.inOut`, 0,9 s, symboles posés le long du chemin.
- **Jamais** : globe 3D qui tourne, carte de nuit, flash d'éclair plein cadre, logo ou habillage imitant une chaîne de télé
  ou Météo-France, présentateur.

### Librairies
- **Librairie « Non » qui porte la signature : topojson-client 3.1.0** (npm, vérifiée ; installée dans `node_modules` mais
  jamais importée). Elle décode les frontières et les côtes qui font la carte. Il faut lui ajouter **`world-atlas` 2.0.2**
  (npm, vérifiée ; **non installé** : une ligne `"world-atlas": "^2.0.2"`), qui fournit Natural Earth en TopoJSON
  (`countries-50m.json`, domaine public, licence ISC). C'est une donnée versionnée comme une police @fontsource, pas un
  téléchargement au rendu. **À valider par l'orchestrateur au regard de la règle « aucun asset téléchargé »** ; à défaut,
  tracer les contours à la main comme atlas-grave (côtes grossières au-delà d'un zoom ×2,5).
- **Plugins GSAP DrawSVGPlugin et MotionPathPlugin** (« Non » dans le catalogue) : ils sont **déjà présents** dans
  `node_modules/gsap/dist/` (gsap 3.15.0, fichiers vérifiés). DrawSVG trace la ligne de front, MotionPath pose les
  triangles et les demi-cercles le long du front. Il faut les enregistrer avec `gsap.registerPlugin(DrawSVGPlugin,
  MotionPathPlugin)`. Le seek reste `tl.seek(t, false)` sans retour (fait vérifié).
- **d3** 7.9.2 (« Oui ») : `d3-geo` pour la projection, `d3-contour` pour les isobares, canvas 2D pour le vent.
- **Pipeline** : scène HTML servie par `render.mjs`, qui importe `/node_modules/topojson-client/dist/topojson-client.min.js`,
  `/node_modules/world-atlas/countries-50m.json`, `/node_modules/d3/dist/d3.min.js` et `/node_modules/gsap/dist/*.js`.
  `window.renderAt(t)` recalcule la projection, les contours et les particules (ou lit leur état précalculé). Ensuite
  `sound.py` (`swell` pour le front, `pop` pour les pastilles, preset `pad`), `assemble.py mux` et `tts.py`.
- **Risque d'API** : topojson-client v3 s'importe en UMD (`window.topojson`) ou en ESM (`/node_modules/topojson-client/src/index.js`).
  Préférer le bundle UMD. `world-atlas` v2 n'a plus de `world/110m.json` (c'était la v1) : les fichiers sont
  `countries-50m.json`, `countries-110m.json` et `land-*.json`.

### Familles et sujets
**geographie**
1. **« Il pleut plus à Nice qu'à Paris (si, si) »** (15 s). Sur les normales climatiques, Nice reçoit plus d'eau par an
   (≈ 730–760 mm) que Paris (≈ 640 mm), mais en environ deux fois moins de jours de pluie (≈ 60 contre ≈ 110). Moins
   souvent, mais plus fort. **Vérifier les valeurs exactes sur les normales Météo-France 1991–2020 avant publication.**
2. **« Le mistral : pourquoi il souffle si fort dans la vallée du Rhône »** (16 s). Un vent du nord canalisé entre les Alpes
   et le Massif central, qui accélère dans le couloir. Ses rafales peuvent dépasser 100 km/h et il chasse les nuages, d'où
   le ciel bleu de Provence.

**evenements**
3. **« J-46 : le 21 décembre, le jour le plus court de l'année »** (14 s). Solstice d'hiver le 21 décembre 2026 ; à Paris,
   environ 8 h 15 de jour. Le terminateur (ligne jour/nuit) balaie la carte comme un front.
4. **« 28 juin 2019 : 46 °C, record absolu de chaleur en France »** (15 s). 46,0 °C à Vérargues (Hérault), record national
   de température. Les pastilles montent une à une jusqu'au rouge.

### Public
**adults** en priorité (bulletin, chiffres vérifiables), **teens** ensuite (records et chiffres-chocs). Sujets simples
possibles pour les enfants, mais ce n'est pas le cœur.

### Voisines et différences
- **swiss-data** (géographie, événements, chiffres) :
  1. fond bleu ciel pâle et terres vertes au lieu d'un blanc cassé à grille 12 colonnes visible ;
  2. les chiffres vivent dans des **pastilles rondes** posées sur la carte, pas en chiffre géant Archivo Black ;
  3. on change de sujet par un **front à triangles bleus en diagonale**, pas par un volet rouge horizontal.
- **riso-zine** (géographie, événements) :
  1. aplats nets sans trame ni décalage de calage ;
  2. aucun rose fluo : le bleu et le rouge sont des codes météo ;
  3. mouvement continu à 30 i/s (isobares, vent), pas saccadé à 12 i/s.
- **atlas-grave** / **topo-relief** (cartes) :
  1. carte plate vue du dessus, sans parchemin et sans terrain 3D ;
  2. symboles météo et pastilles au lieu de gravures, de courbes de niveau lumineuses ou de compteurs d'altitude ;
  3. fond clair et froid, ni sépia ni vert forêt sombre.

### Coût estimé
**≈ 15 s/100 images au repos, 30–45 en charge (estimé, non mesuré).** Raisonnement : capture Playwright ≈ 0,3 s/image
incompressible (≈ 10–12 s/100 au repos), plus une carte canvas 2D et des contours d3 recalculés sur une grille de 128×228
(d3.contours en 256² coûte 224 ms ; en 128² ≈ 50 ms par image, soit ≈ +5 s/100), plus 2 000 traînées de vent en canvas
(négligeable). Les comparables mesurés en charge sont swiss-data (D3 SVG + GSAP) à 13,7–20,5 et bauhaus-kinetic à
28,2–31,7. À éviter absolument : tout filtre SVG plein cadre (309 s/100 pour tableau-craie). Pour le dégradé des terres et
les nuages, utiliser des PNG précalculés.

### Risques
- **Imitation d'une marque réelle** : ne copier ni l'habillage d'une chaîne ni le logo Météo-France. Pas de présentateur.
  Les données citées sont publiques (normales climatiques, records).
- **Faits** : les normales changent selon la période de référence. Citer la période (1991–2020) et arrondir.
- **Données géographiques** : dépendance `world-atlas` à valider (voir Librairies). Le contour de la France en 50m est
  correct jusqu'à un zoom ×3 environ.
- **Lisibilité** : les isobares blanches sur bleu pâle sont faibles (c'est voulu, elles sont décoratives). Les textes vont
  toujours dans un bandeau ou une pastille blanche.
- **Photosensibilité** : pas d'éclair plein cadre. Si un orage est montré, éclair local ≤ 10 % du cadre et ≤ 3 par seconde.
- **Confusion** : proche du « data » de swiss-data si on abuse des barres et des tableaux. Garder la carte visible à
  l'écran à chaque temps.

---

## 3. `tableau-depart` — Tableau des départs

### Slug et nom
`tableau-depart` — **Tableau des départs** (afficheur à palettes).

### Promesse en une phrase
Un grand afficheur de gare à palettes : chaque lettre **claque et défile** avant de se poser, la ligne s'allume en vert ou
en orange, et l'info tombe comme un départ.

### Signature en 4 traits
1. **Type** : Barlow Condensed 600 en capitales blanc chaud, une lettre par palette, fente de charnière visible au milieu de
   chaque cellule.
2. **Palette** : anthracite (boîtier) et gris ardoise (palettes) + voyants de statut ambre / vert / rouge corail. Pas de
   jaune vif, pas de noir pur.
3. **Matière / forme** : grille de cellules de 76×130 px (11 colonnes dans la zone sûre), demi-palettes qui basculent en 3D
   (rotateX), légère ombre portée sous la demi-palette qui tombe, rivets du boîtier.
4. **Transition signature : « la cascade »**. Tout le tableau rebascule colonne par colonne, de gauche à droite, en passant
   par 2 à 8 caractères intermédiaires avant le nouveau texte. Chaque palette fait un clac synthétisé.

### Palette
| Rôle | Hex | Contraste calculé |
|---|---|---|
| Fond = boîtier | `#1B1E23` | — |
| Surface = palette | `#2B2F36` (moitié haute `#33383F`) | — |
| Accent 1 : retard / à suivre | `#FFB020` (ambre) | 7,35:1 sur palette ; 9,14:1 sur fond |
| Accent 2 : à l'heure / bonne réponse | `#3DDC84` (vert signal) | 7,53:1 sur palette |
| Accent 3 : annulé / faux | `#FF6B5E` (corail) | 4,81:1 sur palette |
| Texte | `#F4F1E8` | **11,9:1** sur palette, 14,8:1 sur fond |
| Texte secondaire (en-têtes « HEURE · DESTINATION ») | `#AAB2BC` | 6,27:1 sur palette |

### Typographie
- **Barlow Condensed** (**à ajouter** : `"@fontsource/barlow-condensed": "^5.3.0"`, 5.3.0 vérifiée) : palettes 600,
  96–110 px (1 caractère par cellule) ; grandes palettes de titre 700, 140–180 px (cellules doubles).
- **Barlow** (**à ajouter** : `"@fontsource/barlow": "^5.3.0"`, 5.3.0 vérifiée) : en-têtes de colonnes et légende sous le
  tableau, 600, 54–60 px.
- Les condensées laissent 11 caractères par ligne en zone sûre. Les titres doivent être pensés en lignes de 11 caractères :
  « PROCHAIN », « DÉPART : », « HALLEY ».

### Langage de mouvement
- **Demi-palette** : rotation de 0 à −180° en 90 ms, `cubic-bezier(.5,0,.9,.6)` (accélération de la gravité), 95 ms entre
  deux palettes d'une même cellule.
- **Décalage** : 25–40 ms par colonne, 60 ms par ligne. Le nombre de caractères intermédiaires est tiré par une graine fixe
  (2 à 8 selon la distance alphabétique).
- **Voyant de statut** : s'allume en 0,15 s (montée de luminance locale, sans clignoter), puis reste fixe.
- **Caméra** : fixe. Un seul mouvement permis : une poussée lente de 3 % pendant le hook.
- **Jamais** : fondu sur du texte, glissement ou zoom du tableau, lettres qui se transforment en morphing, caractères hors de
  la grille, animation qui n'est pas une bascule de palette.

### Librairies
- **Librairie « Non » qui porte la signature : Web Animations API** (native Chromium, rien à installer ; ligne « Web
  Animations API / CSS keyframes : Non » du catalogue). Chaque demi-palette reçoit une `element.animate([...], {delay,
  duration, fill:'both'})` mise en pause. `window.renderAt(t)` pose `anim.currentTime = t*1000` sur toutes les animations.
  C'est un seek natif, sans timeline JavaScript à maintenir, et la 3D CSS (`perspective`, `rotateX`, `backface-visibility`)
  donne la vraie bascule.
- **Testé** (scratchpad, Playwright + SwiftShader comme `render.mjs`) : 99 cellules × 6 bascules. **Même image (même md5)
  au même t après un aller-retour à un autre t** : le seek est déterministe. **12,1 s/100 images** de capture au repos.
- **Splitting.js 1.1.0** (npm, vérifiée, « Non ») : optionnel, pour découper la légende Barlow en caractères. Inutile si on
  construit les cellules soi-même.
- **GSAP** n'est pas nécessaire. `sound.py` : le clac des palettes = preset `click` court, une fois par bascule et regroupé
  par paquets de 10 ms pour éviter la saturation ; `chime` à l'arrivée.
- **Pipeline** : scène HTML servie par `render.mjs`, contrat `window.ready` / `window.renderAt(t)`. Aucun import externe à
  part les polices `/node_modules/@fontsource/barlow-condensed/...`.
- **Risque d'API** : garder `fill:'both'`. Sans lui, l'état avant le `delay` n'est pas appliqué, comme le piège GSAP
  `immediateRender:false`. Ne pas mélanger avec des `@keyframes` CSS en lecture : tout passe par `getAnimations()` en pause.

### Familles et sujets
**evenements**
1. **« 27 septembre 1981 : le premier TGV commercial quitte Paris »** (15 s). Ligne « 27/09/1981 · PARIS → LYON · TGV ».
   Le statut passe à « À L'HEURE ». Record d'essai : 380 km/h le 26 février 1981. Paris–Lyon en 2 h 40 à l'ouverture, puis
   en 2 h en 1983.
2. **« Prochain départ : la comète de Halley, en 2061 »** (15 s). Compte à rebours en années, puis en jours. Dernier
   passage au plus près du Soleil le 9 février 1986 ; le prochain le 28 juillet 2061 ; une période d'environ 76 ans.

**engagement**
3. **« Parie : quelle capitale est la plus au nord ? »** (15 s). Trois lignes : OSLO / HELSINKI / REYKJAVIK. « Commente
   1, 2 ou 3 » ; les palettes cascadent ; REYKJAVIK (64° 08′ N) passe au vert, devant Helsinki (60° 10′) et Oslo (59° 55′).
4. **« Le plus long tunnel ferroviaire du monde ? »** (16 s). MANCHE 50,5 km / SEIKAN 53,9 km / GOTHARD 57,1 km. Les
   longueurs se dévoilent l'une après l'autre ; le Gothard (Suisse, inauguré en 2016) gagne.

### Public
**teens** (pari, défi, rythme de 2–3 s) et **adults** (dates, nostalgie du train).

### Voisines et différences
- **brut-meme** (événements, engagement, fond sombre) :
  1. anthracite et ardoise avec voyants ambre/vert, jamais de noir et jaune #FFE600 ;
  2. le texte est **découpé en cellules fixes** d'une grille, pas une Anton qui remplit le cadre ;
  3. le changement se fait par **bascule de palettes colonne par colonne**, pas par une coupe sèche avec punch-in.
- **pixel-arcade** (engagement, fond sombre, grille) :
  1. cellules physiques à charnière et typo condensée lisse, pas de pixels de 4 px en Press Start 2P ;
  2. aucune physique ni course : l'information arrive ligne par ligne ;
  3. sons de clac mécanique, pas de chiptune.
- **gazette-1900** (événements, dates) :
  1. tableau électromécanique sombre, pas une une de journal sépia ;
  2. sans-serif condensée au lieu de Playfair Display 900 ;
  3. pas de coup de tampon : le statut s'allume en vert ou en ambre.

### Coût estimé
**12 s/100 images au repos (mesuré, capture seule)**, ≈ 25–40 s en charge. C'est la capture Playwright (≈ 0,3 s/image) qui
domine. La 3D CSS de 99 cellules coûte peu, comme bauhaus-kinetic (JS de scène à 6–8 ms par image, total 28–32 en charge).

### Risques
- **Fond sombre** : c'est le dixième du menu. Le distinguer par l'anthracite chaud, les voyants et la grille de cellules
  visible, jamais du noir pur.
- **Photosensibilité** : une cascade fait changer beaucoup de petites surfaces à ~10 Hz. Comme les deux faces d'une palette
  ont la même teinte, la luminance moyenne du cadre reste stable : ce n'est pas un flash. Ne jamais basculer tout le tableau
  plus d'une fois toutes les 1,6 s, et ne pas faire de palettes de couleur différente au verso.
- **Lisibilité** : 11 caractères par ligne obligent à réécrire les titres. Les accents (É, À) doivent tenir dans la cellule.
- **Son** : 99 clacs simultanés saturent. Les regrouper.
- **Ressemblance** : ne reproduire ni la charte ni le logo d'un opérateur ferroviaire réel (pas de logo SNCF ou autre).
  Les noms de villes et de trains sont des faits.

---

## 4. `domino-cascade` — Réaction en chaîne

### Slug et nom
`domino-cascade` — **Réaction en chaîne**.

### Promesse en une phrase
Des centaines de vrais dominos mats sur un sol lilas tombent en vague, simulés par la physique, et **leurs faces renversées
révèlent le mot ou le chiffre** de l'idée.

### Signature en 4 traits
1. **Type** : Bricolage Grotesque 800 en violet encre, posée comme une carte au sol ; compteurs en Azeret Mono.
2. **Palette** : sol et fond lilas clair, dominos ivoire sur la tranche et **sarcelle / rose corail / violet encre** sur les
   faces. Jamais rouge-jaune-bleu primaires (ce serait bauhaus-kinetic, constaté sur le still d'essai).
3. **Matière / forme** : dominos en plastique mat légèrement arrondis, ombres portées douces, vue de trois quarts plongeante
   (fov 35°), aucune autre forme dans le cadre.
4. **Transition signature : « la vague révélatrice »**. Le front de chute traverse le cadre ; les dominos tombés montrent
   leur face colorée, qui forme le prochain titre ou chiffre en « pixels » de dominos ; la caméra suit le front.

### Palette
| Rôle | Hex | Contraste calculé |
|---|---|---|
| Fond = sol | `#E8E2F4` (lilas clair) | — |
| Surface = tranche et carte de titre | `#FFF9EE` (ivoire) | — |
| Accent 1 : face | `#0F8A7A` (sarcelle) | 3,37:1 sur fond, décoratif ; blanc dessus 4,25:1 (≥ 54 px gras seulement) |
| Accent 2 : face | `#F0457A` (rose corail) | décoratif ; texte encre dessus 4,21:1 (titres seulement) |
| Accent 3 : face et texte | `#2B1E4A` (violet encre) | 11,98:1 sur fond ; ivoire dessus 14,44:1 |
| Texte | `#2B1E4A` | **11,98:1** sur fond, 14,44:1 sur carte ivoire |
| Texte secondaire | `#5B4F78` | 5,86:1 sur fond |

### Typographie
- **Bricolage Grotesque** (**à ajouter** : `"@fontsource/bricolage-grotesque": "^5.3.0"`, 5.3.0 vérifiée) : titres 800,
  100–130 px ; corps 600, 58 px.
- **Azeret Mono** (**à ajouter** : `"@fontsource/azeret-mono": "^5.3.0"`, 5.3.0 vérifiée) : compteurs (« 287 / 300
  tombés »), 600, 64–96 px.
- Les textes vont en calque HTML par-dessus le canvas WebGL. troika-three-text n'est pas nécessaire.

### Langage de mouvement
- **Dominos** : **uniquement la physique** (Rapier, pas de 1/240 s, 8 sous-pas par image, frottement 0,4). Rien n'est
  animé à la main.
- **Caméra** : suit le front de chute avec un retard (lerp à 0,08 par image), 1 à 2 travellings par short. Hauteur
  constante.
- **Textes** : la carte de titre glisse sur 60 px en `power3.out` sur 0,4 s ; les compteurs s'incrémentent à chaque domino
  tombé (lu dans la simulation).
- **Durées** : une chaîne de 300 dominos tombe en ≈ 10–12 s ; le hook (pichenette) a lieu avant 0,5 s.
- **Jamais** : ralenti truqué, coupe pendant que la vague avance, domino posé en keyframe, rebond cartoon, couleur primaire,
  fond sombre.

### Librairies
- **Librairie « Non » qui porte la signature : Rapier**, paquet npm **`@dimforge/rapier3d-compat` 0.21.0** (vérifié ;
  existe aussi en `@dimforge/rapier3d-deterministic-compat` 0.21.0). Cannon-es 0.20.0 (vérifié) est l'alternative. Rapier
  fournit la vraie chute en chaîne et l'effondrement, ce qui fait la crédibilité du « satisfying ».
- **Testé** (scratchpad) : 300 dominos, 450 images × 8 sous-pas en **≈ 5,5 s** sous Node 22 ; **même hash sur deux
  exécutions** ; 231 dominos tombés sur 300 avec des réglages bruts (à régler).
- **Déterminisme** : pré-simuler **en Node** et enregistrer les transformations par image (300 × 450 × 7 flottants ≈ 3,8 Mo
  en Float32 binaire, ou quantifiées). Le navigateur se contente de rejouer : c'est la leçon de pixel-arcade (`Math.atan2`
  diffère entre Node et Chromium), et le navigateur n'a jamais à simuler. Le `package.json` local `{"type":"module"}` ou
  `commonjs` va dans `src/` (fait vérifié).
- **Risque d'API** : Rapier est en 0.x et son API JS change entre versions mineures (`RAPIER.init()` asynchrone, puis
  `world.timestep` au lieu d'un argument de `step`). Fixer la version exacte `0.21.0` et ne pas suivre de vieux exemples.
- **three.js** 0.187 (« Oui ») pour le rendu : `InstancedMesh` avec `setColorAt` (face et tranche par vertex color, ou
  deux InstancedMesh), un seul `DirectionalLight` avec `shadowMap` 2048 PCFSoft, pas de bloom, pas d'EffectComposer.
- **Pipeline** : `src/sim.mjs` (Node) écrit `src/frames.bin` ; `src/index.html` est servi par `render.mjs`, importe
  `/node_modules/three/build/three.module.js` et lit `frames.bin` par `fetch` ; `renderAt(t)` écrit les matrices de l'image
  `round(t*30)`. `sound.py` : `tick` en rafale suivant la densité de chutes, `thud` final.

### Familles et sujets
**abstrait**
1. **« 300 dominos, une seule pichenette »** (15 s, boucle possible). Une spirale de 300 dominos tombe du centre vers
   l'extérieur, et le dernier domino tombe sur le premier plan. Aucun texte après le hook.
2. **« Chaque domino peut en renverser un 1,5 fois plus grand »** (16 s). Dix dominos qui grandissent chacun de ×1,5 : le
   premier fait 5 cm, le dernier ≈ 1,9 m (1,5⁹ ≈ 38). C'est le résultat de L. Whitehead (*American Journal of Physics*,
   1983) ; à rendre avec une échelle visible.

**engagement**
3. **« Combien de dominos resteront debout ? »** (15 s). 200 dominos avec trois trous dans la chaîne. « Ton pronostic en
   commentaire » ; le compteur s'arrête sur la vraie valeur simulée.
4. **« Devine le mot avant que la vague finisse »** (14 s). La vague révèle un mot de 5 lettres en faces colorées, lettre
   après lettre. La voix invite à commenter avant la dernière lettre ; un mot neutre comme « MERCI » ou « BRAVO ».

### Public
**kids, teens, adults** : le « satisfying » physique traverse les âges. Le pari vise les teens ; la version ×1,5 vise
adultes et teens.

### Voisines et différences
- **pastel-diorama** (3D pastel, engagement) :
  1. sol lilas uni et dominos géométriques, pas de diorama rose sur feutre ni de jouets ronds ;
  2. aucun personnage, aucune mascotte ;
  3. mouvement 100 % physique et sans rebond cartoon (`back.out`), au lieu de pops.
- **liquid-chrome** (« pendule de Newton chromé », abstrait satisfying) :
  1. plastique mat coloré, aucun reflet chromé ni irisé ;
  2. fond clair lilas au lieu d'un graphite sombre ;
  3. une vague qui traverse plusieurs plans avec une caméra qui suit, au lieu d'un plan macro fixe.
- **pixel-arcade** / **bauhaus-kinetic** (paris physiques ; formes colorées sur fond clair) :
  1. 3D ombrée sans pixels ni HUD Press Start ;
  2. palette sarcelle, rose et violet, sans primaires ;
  3. la réponse est **écrite par les dominos tombés**, pas affichée en HUD ni en grille.

### Coût estimé
**44 s/100 images au repos (mesuré)** : 320 dominos instanciés, ombre PCFSoft 2048, 1080×1920 sous SwiftShader, capture
comprise. En charge (×1,5–2), cela donne ≈ 65–90 s. C'est le plus cher des quatre, sous le seuil, comparable à three.js
+ bloom (≈ 60 au repos) sans le bloom. Leviers si ça dépasse : ombre 1024 en PCF simple (≈ −20 %), ou ombres de contact
précalculées en texture une fois les dominos posés. Pré-simulation Rapier ≈ 5 s par short, négligeable.

### Risques
- **Coût** : au seuil des 90 s en charge. Mesurer dès le premier still et réduire l'ombre si besoin.
- **Physique** : des chaînes qui s'arrêtent (231/300 sur l'essai brut). Il faut régler l'espacement (≈ 0,6 × la hauteur),
  le frottement et l'impulsion, puis **choisir la graine en Node** comme pixel-arcade. Le sujet 3 suppose qu'on maîtrise où
  la chaîne casse.
- **Lisibilité** : un mot écrit en dominos demande une grille d'au moins 40×24 ≈ 1 000 dominos. Il faut vérifier le coût
  (InstancedMesh supporte bien ce nombre ; l'ombre devient le poste principal) et que la vue plongeante ne déforme pas le
  mot. Prévoir le mot aussi en carte de titre.
- **Confusion** : avec des couleurs primaires, on retombe sur bauhaus-kinetic (constaté). La palette sarcelle, rose et
  violet sur lilas est non négociable.
- **Photosensibilité** : rien à signaler (pas de flash, luminance stable).

---

## Classement

1. **`trait-continu`**
2. **`carte-meteo`**
3. **`tableau-depart`**
4. **`domino-cascade`**

**Justification.** **Distinctivité d'abord.** `trait-continu` est la plus éloignée des 18 : c'est la seule identité qui
montre un **objet** (le jouet) plutôt qu'un fond. Sa couleur dominante, l'orange, n'est utilisée par aucune identité, et sa
grammaire (un trait unique en escalier, effacé par une secousse) ne se confond pas avec les traits multiples de
tableau-craie. `carte-meteo` emprunte un code de genre que personne n'a (le bulletin météo) sur la seule teinte de fond
encore libre côté froid (bleu ciel pâle). `tableau-depart` a une mécanique très forte (la palette qui claque), mais elle
ajoute un dixième fond sombre et partage la grille de cellules et le registre du pari avec pixel-arcade et brut-meme ; en
vignette, le risque de confusion est plus élevé. `domino-cascade` est neuve par sa physique 3D, mais son terrain du
« satisfying physique » est déjà occupé par liquid-chrome (pendule) et pixel-arcade (course), et sa palette a dû être
écartée des primaires pour ne pas rappeler bauhaus-kinetic.

**Largeur éditoriale ensuite.** Les deux premières couvrent les familles les moins prouvées : enfants (3 identités),
géographie (4) et événements (5). `trait-continu` donne au menu une identité enfants qui n'est ni pastel ni aquarelle ni
craie, et `carte-meteo` une géographie claire qui n'est ni crème ni parchemin. Ensemble, elles respectent la contrainte
« une Python + une JavaScript ».

**Coût enfin.** `trait-continu` est la moins chère de tout le menu en Python hors papier (5 s/100, mesuré) ; `carte-meteo`
et `tableau-depart` sont dans la gamme des scènes DOM (≈ 15 et 12 au repos). `domino-cascade` (44 au repos) frôle le
plafond en charge, ce qui confirme sa quatrième place.

Recommandation : produire **`trait-continu`** et **`carte-meteo`**, et garder `tableau-depart` en réserve pour un besoin
« événements / engagement » adolescent.

### Ce que le studio devra prouver en priorité dans son premier still
- **`trait-continu`** : un still à t ≈ 4 s où l'on reconnaît **le jouet entier** (cadre orange, écran gris, molettes) **et**
  un dessin à moitié tracé d'un seul trait en escalier dont la forme se devine déjà, avec le titre Fredoka lisible sur la
  bande du cadre. Plus une seconde paire de stills de la secousse.
- **`carte-meteo`** : un still où la France (via topojson-client + world-atlas, ou à la main) est nette, avec des isobares,
  au moins trois pastilles lisibles en Atkinson et une **ligne de front à triangles bleus en cours de traversée** ; et la
  décision écrite sur la dépendance `world-atlas`.
- **`tableau-depart`** : deux stills à 1/30 s d'écart **au milieu d'une cascade**, avec des demi-palettes visiblement
  inclinées en 3D, un titre de 11 caractères lisible, et la preuve md5 que le même t donne la même image.
- **`domino-cascade`** : un still où le **mot ou le chiffre est lisible dans les faces tombées** pendant que le front de
  chute est encore visible, avec sa mesure de coût par image en charge (≤ 0,9 s).

---

## Vérifications faites (2026-11-05)

Le réseau (proxy) répondait. Versions relevées avec `npm view <pkg> version` et `pip index versions <pkg>`.

| Paquet | Registre | Version courante | Statut ici |
|---|---|---|---|
| `shapely` | PyPI | 2.2.0 | installé en scratchpad, testé |
| `opensimplex` | PyPI | 0.4.5.1 | installé en scratchpad, testé |
| `skia-python` | PyPI | 144.1 (roue cp311 manylinux_2_28) | **import impossible : `libEGL.so.1` absent** (paquet système `libegl1`) |
| `topojson-client` | npm | 3.1.0 | déjà dans `node_modules` |
| `world-atlas` | npm | 2.0.2 | non installé (une ligne à ajouter, à valider) |
| `gsap` (DrawSVGPlugin, MotionPathPlugin) | npm | 3.15.0 | plugins présents dans `node_modules/gsap/dist/` |
| `@dimforge/rapier3d-compat` | npm | 0.21.0 | installé en scratchpad, testé (déterministe en Node) |
| `@dimforge/rapier3d-deterministic-compat` | npm | 0.21.0 | non testé |
| `cannon-es` | npm | 0.20.0 | non testé (alternative) |
| `splitting` | npm | 1.1.0 | non testé (optionnel) |
| `three` | npm | 0.187.0 | déjà installé ; testé avec ombres (44 s/100) |
| `d3` | npm | 7.9.2 | déjà installé |
| `@fontsource/fredoka` | npm | 5.3.0 | déjà installé |
| `@fontsource/lexend`, `outfit`, `atkinson-hyperlegible`, `barlow-condensed`, `barlow`, `bricolage-grotesque`, `azeret-mono` | npm | 5.3.0 chacun | à ajouter (une ligne chacun) |

Essais (tous hors du dépôt, dans le scratchpad de session ; machine calme, un seul rendu à la fois) :
- pycairo + shapely + opensimplex + grain numpy + x264 : **4,94 s / 100 images**.
- WAAPI + CSS 3D, 99 cellules, Playwright + SwiftShader : **12,1 s / 100 images**, md5 identique au même t.
- three.js 0.187, 320 boîtes instanciées, ombre PCFSoft 2048 : **44,1 s / 100 images**.
- Rapier 0.21.0, 300 dominos, 450 images × 8 sous-pas : **≈ 5,5 s**, même hash sur deux exécutions.

Remarque : l'en-tête de `out/library-cards/catalogue.md` parle encore de « 14 identités (31 shorts) ». Les 4 identités papier
n'y ajoutent aucune librairie nouvelle (Pillow, OpenCV, NumPy et ffmpeg sont déjà à « Oui »).
