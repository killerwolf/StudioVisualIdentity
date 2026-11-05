# Carte Météo (carte-meteo)

## Nom
**Carte Météo** — slug `carte-meteo`. Le bulletin météo comme langage graphique : une carte claire et vraie, des isobares, du vent, des pastilles chiffrées, et un front qui balaie l'écran pour changer de sujet.

## Promesse en une phrase
Une carte météo claire, mer bleu ciel pâle et terres vert tendre, où les isobares respirent, où le vent file en traînées sombres, où les pastilles de température « popent », et où **un front à triangles bleus ou à demi-cercles rouges balaie l'écran en diagonale** pour passer au plan suivant.

## Mood & références de genre
Service public, clarté, calme, « on comprend la carte d'un coup d'œil ». Genre : carte d'analyse météorologique (isobares, centres A/D, symboles de front normalisés), infographie cartographique plate vue du dessus. Le code « bulletin » est générique et immédiat ; **aucun habillage de chaîne, aucun logo, aucun présentateur, aucune carte en relief ombré façon journal télévisé**. Pictogrammes plats et géométriques, **sans visage** (montagnes, nuages, soleil), pour rester loin de pastel-diorama.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Valeur | Contraste mesuré (WCAG) | Usage |
|---|---|---|---|
| fond = mer | `#CFE6F5` | — | plein cadre, toujours |
| terres | `#A9D486` | **1,31:1** contre la mer | toutes les terres (pas de distinction par pays : les frontières font le travail) |
| trait de côte | `#3E5A72`, 3 px écran | 5,60:1 sur mer, 4,28:1 sur terre | côtes (topojson.mesh a === b) |
| frontières | `#3E5A72` à 55 %, 2 px, pointillé 9/7 | — | topojson.mesh a !== b |
| surface | `#FFFFFF` | — | bandeau titre, cartouches, disques des pastilles, A/D, liseré du front |
| accent 1 : front chaud / record / dépression | `#D63A2A` | 4,67:1 sur blanc ; blanc dessus 4,67:1 ; 3,62:1 sur mer | demi-cercles, anneaux chauds, pastille record pleine (blanc ≥ 54 px gras dessus) |
| accent 2 : front froid / vent / anticyclone | `#1F5FD6` | 5,73:1 sur blanc ; 4,44:1 sur mer | triangles, onglet du bandeau « vent », lettre A |
| accent 3 : chaleur | `#F59A2C` | 2,20:1 sur blanc (décoratif) ; texte `#10263D` dessus 6,98:1 | anneau des pastilles tièdes, soleil |
| texte | `#10263D` | 15,37:1 sur blanc, 11,92:1 sur mer, 9,11:1 sur terre | tout texte, toujours sur blanc |
| texte secondaire | `#3E5A72` | 7,22:1 sur blanc | sous-titre du bandeau, unités |
| isobares | `#587A96`, 3 px | 3,51:1 sur mer, 3,17:1 sur terre | courbes de pression, pas d'étiquette |
| vent | `#10263D` à 21–75 % selon la vitesse | effectif ≈ 2:1 | traînées effilées |
| relief | `#86BE68` + contour `#3E5A72` + neige blanche | — | pictogrammes montagne |
| danger / succès | `#D63A2A` / `#1F5FD6` | — | mêmes rouge et bleu (codes météo, pas de vert sémantique) |

**Écart au correctif du challenge** : la terre `#BFE3A0` proposée en exemple ne mesure que **1,11:1** contre la mer (pas 1,25) ; `#A9D486` (1,31:1) la remplace. Isobares : `#6E8FAA` à 1,5 px (2,64:1) testé puis écarté, trop faible sur téléphone ; `#587A96` à 3 px retenu. Aucun crème, aucun noir, aucun rose fluo.

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Titres : Space Grotesk 700** (`space-grotesk`, déjà installée), 108 px dans le bandeau, une ligne de ≤ 15 caractères, auto-ajustée jusqu'à 90 px si elle dépasse 796 px ; interlettrage 0. Lettres A / D : Space Grotesk 700, 100 px. *Pourquoi elle* : les voisines utilisent Archivo Black + Inter (swiss-data), Space Mono (riso-zine), Cinzel (atlas-grave), JetBrains Mono (topo-relief) ; Unbounded (bauhaus), Syne (liquid-chrome) et Fredoka (trait-continu) sont exclues ; Space Grotesk n'est titre que chez neon-lab, fond noir de laboratoire, impossible à confondre avec une carte claire. Ses chiffres ronds et son « ç » ouvert lisent bien les dates (« 28 juin 2019 »).
- **Pastilles, corps, légendes : Atkinson Hyperlegible 700** (`atkinson-hyperlegible` 5.3.0, **seule police ajoutée**) : chiffres des pastilles 54–96 px auto-ajustés au disque ; sous-titre du bandeau 56 px `#3E5A72` ; noms de lieux et unités 54 px. Poids 400 installé, non utilisé dans les 2 shorts. Police dessinée pour la lisibilité (distinction 1/l/I, 0/O) : l'esprit « service public » du bulletin.
- **Écart déclaré au challenge (correctif 5)** : le challenge prescrivait **Atkinson Hyperlegible partout**, y compris les titres en bandeau (700 à 96–120 px). Les titres et les lettres A / D sont ici en **Space Grotesk 700**. Justification : (1) ce n'est pas une police nouvelle (déjà dans `package.json`), la règle « une seule nouvelle police » est tenue ; (2) un seul dessin pour tout aplatissait la hiérarchie : à 108 px, Atkinson 700 a des formes larges et neutres qui se confondent avec les chiffres des pastilles, alors que le contraste grotesque géométrique (titre) / humaniste lisible (chiffres, lieux) sépare d'un coup d'œil « le sujet » et « la donnée » ; (3) Space Grotesk n'est la police titre d'aucune voisine (seulement de neon-lab, identité sombre non voisine). Revenir à Atkinson 700 en titre reste possible sans autre changement (même bandeau, même taille).
- Minimum absolu : 54 px, et **tout texte ≤ 60 px est sur cartouche blanc** (jamais directement sur la terre ou la mer). Pas d'italique. Virgule décimale française (« 44,1 »).

## Formes & matières
Aplats nets en canvas 2D, aucune texture, aucun dégradé de fond, aucun filtre. Carte : vraie géométrie Natural Earth 1:50 m, terres d'une seule couleur, côte 3 px, frontières pointillées. Isobares 3 px lissées (courbes quadratiques par milieux). Vent : traînées effilées en 3 tronçons (opacité 0,25 / 0,55 / 1 de la queue à la tête, multipliée par 0,28–1 selon la vitesse locale : 21–75 % au total ; épaisseur 0,6 / 0,8 / 1 × 6 px), plus sombres et plus épaisses là où l'air va vite. **Seulement quand le vent est le sujet** (le mistral) : un flux lent donne des traînées courtes qui se lisent comme de la pluie ; le short record de chaleur n'en a pas. **Pastilles** : disque blanc + anneau coloré 18 px + liseré blanc 7 px ; la pastille record devient pleine rouge, chiffre blanc. Cartouches : gélules blanches. Bandeau titre : rectangle blanc à rayon 26 et onglet couleur 16 px (bleu pour le vent et le froid, rouge pour la chaleur). Centres de pression : lettre A bleue / D rouge sur disque blanc. Pictogrammes plats sans visage : montagne (3 triangles, neige), nuage (union de disques, contour `#8FB0C8`), soleil (disque + 8 rayons triangulaires). Front : trait 11 px sur liseré blanc 20 px, symboles tous les 128 px (triangles hauts de 46 px ou demi-cercles r 34), côté avant.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- **Pop** : `back.out(1.4)` en 0,35 s (pastilles, cartouches, A/D, bandeau, pictogrammes, soleil). Pas de stagger fixe : **chaque élément pope au moment où le front passe sur lui** (+0,08 s) ; au hook, A puis D à 0,15 s d'écart.
- **Compteurs** : `power2.out`, 0,6 s (ancien record), 0,9 s (rafales), 1,4 s (record) ; l'anneau passe de l'orange au rouge en même temps ; à la valeur finale, la pastille se remplit de rouge et un anneau d'onde s'élargit (0,8 s).
- **Front** : `power2.inOut`, 0,9 s, de s = −160 à s = 2380 px le long de la diagonale (60°).
- **Isobares** : champ de pression = centres gaussiens + `noise3` lent (cycle ≈ 20 s) recalculé à chaque image : elles respirent sans clignoter.
- **Vent** : particules rejouées sur des lignes de courant précalculées (position fermée en t, cycle ligne + 18 pas) ; 15 pas/s ; facteur ×1,5 pour « ça accélère ».
- **Nuages** : chassés vers le sud-est en `power2.in` 1,9 s, fondus sur la fin.
- **Jamais** : globe 3D, carte de nuit, éclair plein cadre (éclair local ≤ 10 % du cadre et ≤ 3/s si un orage est montré), flash, caméra qui tremble, pictogramme avec visage, tableau ou barres de données, texte posé à même la carte.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
2D vue du dessus, projection conique conforme de Lambert centrée France (parallèles 44° et 49°). Trois focales : **large ×1** (France entière calée dans x 90→990, y 560→1480), **régionale ×1,7–2,3** (couloir rhodanien, Provence), **locale ×2,4–2,6** (Gard / Hérault). **Plan fixe par séquence** : on ne zoome pas en continu (le fond de carte est mis en cache, et le mouvement vient du vent, des isobares et des pops) ; le changement de plan se fait **derrière le front**. Pas de profondeur de champ : tout est net.

## Transitions (liste nommée, durée, quand les utiliser)
| Nom | Durée | Usage | ffmpeg |
|---|---|---|---|
| `passage-du-front` | 0,9 s | **signature** : changement de sujet / de plan. Front froid (triangles bleus) pour le vent, le froid, la pluie ; front chaud (demi-cercles rouges) pour la chaleur. Diagonale haut-gauche -> bas-droite ; derrière lui, la nouvelle carte. Whoosh 0,9 s | `diagbr` |
| `pop-au-passage` | 0,35 s | apparition des éléments du nouveau plan au passage du front | — |
| `compteur-pastille` | 0,6–1,4 s | révélation d'une valeur | — |
| `coupe` | 0 s | jamais seule : toujours sous un front | cut |

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
15–16 s, 4 plans séparés par 3 passages de front (≈ 3,4–3,6 s / 8,3–8,6 s / 12,6 s) :
1. **0–0,4 s hook** : la carte est là dès la frame 0 (vent et isobares en mouvement) ; le bandeau pope (titre = sujet ou date, sous-titre = question ou promesse) ; A / D ou pastille « ? ».
2. **Plan 2 (≈ 4–8 s)** : premier zoom, le mécanisme ou le premier chiffre (pictogrammes + cartouches, ou pastille + compteur).
3. **Plan 3 (≈ 9–12,5 s)** : le chiffre clé dans une grande pastille (r 128), compteur puis passage au rouge.
4. **Plan 4 (≈ 13,5–16 s) chute** : retour au large ou plan de conclusion (soleil, deux pastilles côte à côte, écart chiffré), tenue ≥ 1,5 s, fin propre (pas de boucle).

## Zones sûres
Haut 220 px (le bandeau commence à y = 246), bas 320 px (aucun texte ni pastille sous y = 1600 ; la carte et le vent continuent dessous, c'est du fond), droite 120 px (cartouches bornés à x ≤ 960 par code), gauche 60 px. Les A/D sont repoussés dans x 130→880. Les pastilles sont décalées de leur lieu par un trait de rappel pour rester dans la zone utile.

## Librairies recommandées et pourquoi
- **world-atlas 2.0.2** (npm, version exacte épinglée dans `package.json`, installée par `npm i`, jamais chargée par le réseau) : `countries-50m.json`, géométries **Natural Earth (domaine public)**, paquet sous **licence ISC** (Mike Bostock). Donnée factuelle (forme réelle des côtes), pas une illustration : le style visible reste généré par code. Fiche : `out/library-cards/_drafts/carte-meteo__world-atlas.json`. Le paquet contient aussi `countries-10m.json` (3,7 Mo) : non utilisé (consigne 50 m ; la côte 50 m reste propre jusqu'à ×2,6, testé).
- **topojson-client 3.1.0** : `topojson.feature` (pays) et `topojson.mesh` (côtes a === b, frontières a !== b). Le **bundle UMD** `dist/topojson-client.min.js` marche sous `render.mjs` (global `topojson`) ; l'ESM `src/index.js` marche en Node.
- **Filtrage des DROM** : le MultiPolygon « France » contient 10 polygones (Guyane, Réunion, Mayotte, Antilles…) ; on ne garde que ceux dont le centroïde (`d3.geoCentroid`) est dans lon ]−6, 10[, lat ]41, 52[ (métropole, Corse, Oléron) **avant** `fitExtent`, sinon la France est minuscule.
- **Découpe précalculée** : une seule fois dans `window.ready` (≈ 300 ms) : 47 pays dont la bbox coupe [−16, 22]×[33, 60], projetés par `d3.geoConicConformal().parallels([44,49]).rotate([-2.5,0]).fitExtent(...).clipExtent(...)` en `Path2D` ; la caméra n'est ensuite qu'un `ctx.setTransform`, et le fond de carte est rastérisé une fois par plan (cache canvas).
- **D3 7.9.2** : `d3-geo` (projection, centroïdes, bbox), `d3-contour` (isobares sur une grille écran 116×200 de 10 px débordant du cadre de 40 px pour que les bords des contours restent hors champ). Canvas 2D pour tout le dessin (vent, front, texte).
- **Vent** : `src/precompute.js` (Node) intègre des lignes de courant (RK2, pas 1/15 s) dans un champ lon/lat schématique et écrit `wind.json` ; le navigateur projette une fois et rejoue (position fermée en t, **jamais `window.SEQUENTIAL`**).
- **svi.js** : `loadFonts`, `noise3`, `mix`, `installContract`. **GSAP non utilisé** (toutes les animations sont des fonctions fermées de t ; les easings `back.out`, `power2.*`, `sine.inOut` sont réécrits dans `meteo.js`) ; plugins DrawSVG / MotionPath écartés (licence non open source au sens strict) — les symboles du front sont posés le long d'une polyligne calculée.
- **Coût mesuré** : page canvas vide = 13,2 s/100 images (capture seule, à vide) ; still de preuve 17,6 s/100 à vide ; shorts **18,1 et 18,7 s/100 images** (87,0 s et 84,1 s ; 1er rendu du short chaleur, avec vent : 84,6 s) avec le studio trait-continu en parallèle. Aucun filtre SVG.

## Familles de contenus adaptées / inadaptées
- **Adaptées** : `geographie` (vents, climats régionaux, reliefs qui canalisent l'air, « pourquoi il pleut plus ici »), `evenements` (records datés, tempêtes, canicules, premières neiges — sans « J-N »), `explicatif` météo (fronts, anticyclones, brise de mer).
- **Inadaptées** : `histoire` sans dimension météo, `enfants` en premier public (possible pour des sujets simples), `abstrait`, classements et comparaisons chiffrées en barres (territoire de swiss-data : ici la carte reste visible à chaque plan), tout sujet hors d'Europe de l'Ouest sans refaire la découpe et la projection.

## Shorts de preuve (chemins)
- `out/shorts/carte-meteo__geographie__le-mistral-pourquoi-il-souffle-si-fort/short.mp4` — « Le mistral : pourquoi il souffle si fort » (16 s, rendu 87,0 s)
- `out/shorts/carte-meteo__evenements__28-juin-2019-46-degres-record-de-chaleur/short.mp4` — « 28 juin 2019 : 46 °C, record de chaleur en France » (15 s, re-rendu après revue sans traînées de vent : 84,1 s)
- Still de preuve de l'identité : `out/shorts/carte-meteo__geographie__le-mistral-pourquoi-il-souffle-si-fort/src/probe.html`

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)
Voix réellement utilisée : **Gemini « Sulafat »** (`gemini-3.8-flash-tts`, voix féminine chaude, la même que les identités papier), style « voix documentaire claire et posée, ton de bulletin météo naturel », sans imiter un présentateur ; un appel par short, découpé en `voice_lines/NN.mp3`, mixé par `tts.py --engine files` (Arnold, Fish Audio, était prévu : décision du propriétaire après épuisement des crédits Fish Audio, `out/report/notes/voix-lot2.md`). Débit mesuré ≈ 2,9 mots/s parlés (pauses internes comprises), un peu au-dessus de la cible ; aucune ligne ne déborde. Les nombres sont envoyés en toutes lettres à Gemini (« quarante-quatre virgule un »), le texte de `narration.json` reste en chiffres. 4 lignes par short (4–6 au maximum), une par plan, qui démarrent à 0,3 s puis 0,2–0,3 s après chaque front. Débit adultes 2,4–2,8 mots/s parlés : compter les chiffres en mots dits (« 44,1 » = 4 mots, « 2019 » = 4) et exiger `maxDuration ≥ mots dits / 2,4` ; ne pas relire la date déjà affichée dans le bandeau ; ados 2,6–3,0 mots/s avec des bandeaux de ≤ 6 mots. Le visuel ne porte que le titre (≤ 3 mots), un sous-titre (≤ 5 mots), des noms de lieux et un chiffre : la voix apporte le mécanisme (« coincé entre… », « il accélère »), la période et la source. Les 320 px du bas restent libres pour d'éventuels sous-titres.

## Risques et limites
- **Imitation** : ne jamais copier l'habillage d'une chaîne de télévision ni le logo ou la charte de Météo-France ; pas de présentateur, pas de carte en relief ombré « façon JT », pas de jingle imitant un indicatif connu. Les symboles de front et les lettres A/D sont des conventions météorologiques, pas une marque.
- **Faits** : les normales changent selon la période de référence (citer 1991–2020 par exemple, et arrondir) ; les records doivent être datés et localisés (46,0 °C, Vérargues, 28/06/2019). Les champs de vent et de pression des shorts sont **schématiques** : le dire dans les notes, ne jamais les présenter comme l'analyse d'un jour donné.
- **Géographie** : découpe et projection calées sur la France ; un autre pays demande une autre découpe (et une autre parallèle standard). Côte 50 m propre jusqu'à ×2,6 environ ; au-delà, passer à `countries-10m.json` (3,7 Mo) en le disant.
- **Vent qui ressemble à de la pluie** : des traînées courtes, droites et parallèles se lisent comme des hachures de pluie (constaté au premier still, puis par la revue finale sur le short chaleur, où même allongées et courbées elles restaient des hachures obliques). Garder des traînées longues (16 pas), effilées, pondérées par la vitesse, dans un flux rapide et courbé ; sinon, ne pas en mettre.
- **Confusion** : avec swiss-data si on ajoute barres ou tableaux ; avec pastel-diorama si les pictogrammes prennent un visage ou du volume ; avec atlas-grave / topo-relief si on assombrit le fond ou ajoute du relief.
- **Photosensibilité** : aucun flash ; le front ne change pas la luminance globale (carte pastel -> carte pastel).
- **Poids** : les traînées de vent font monter le débit (≈ 5,9 Mo pour 16 s), sans atteindre le plafond.
