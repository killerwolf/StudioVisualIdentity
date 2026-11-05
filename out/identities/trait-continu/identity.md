# Trait continu — identité visuelle

## Nom
**Trait continu** (`trait-continu`) — « le traceur » : une table traçante générique, sans marque, qui dessine toute l'idée d'une scène d'**un seul trait graphite jamais levé**, puis fait avancer sa plaque pour recommencer.

## Promesse en une phrase
« Un seul trait, qui avance sur deux axes sans jamais se lever, dessine l'idée devant toi ; puis la plaque avance et on recommence. »

## Mood & références de genre
Atelier de dessin technique pour enfants, cahier de géométrie, table traçante (plotter) de bureau d'études, jeu « relier sans lever le crayon ». Références de genre seulement : dessin technique, tracés de plotter à stylo, cartes d'écolier simplifiées. Le ton est calme, mécanique et précis, pas bricolé : on regarde une machine patiente qui avance à vitesse constante, s'arrête sur un point clé, puis repart. **C'est une machine de bureau d'études, pas un objet de loisir** : aucun cadre arrondi autour de la plaque, aucun bouton rond, aucune agitation de l'objet, aucun nom de produit, aucun argument de souvenir d'enfance (voir Risques).

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Hex | Usage | Contraste (WCAG, calculé) |
|---|---|---|---|
| Fond | `#F26A21` | orange plein cadre, uni, sans dégradé | — |
| Surface | `#D3D4CE` | plaque gris métal à angles vifs, grain de surface opensimplex ±3,5 % (marbrure) et ±2,8 % (grain fin) ; ombre portée `rgba(77,23,0,0.30)` décalée de (10, 14) px | 2,05:1 sur l'orange (grande surface, pas d'inversion) |
| Accent 1 — trait | `#3A3D42` | trait graphite unique 7 px, curseurs, chariot, graduations | 7,31:1 sur la plaque |
| Accent 2 — repères | `#1D47A8` | point de départ (anneau), repères de lieu (point + anneau), « +1 », flèche de sens, fil de repère | 5,59:1 sur la plaque |
| Accent 3 — étiquettes | `#FFF8EE` | étiquette crème à angles vifs, liseré `#22252A` 3 px | texte `#22252A` dessus : 14,58:1 |
| Texte sur l'orange | `#1A1410` | titres | 5,96:1 |
| Texte sur plaque / étiquette | `#22252A` | légendes | 10,31:1 / 14,58:1 |
| Règles | plaque assombrie de 7,5 % (≈ `#C3C4BD`) | bandes graduées haut et gauche | décoratif |
| Succès / danger | `#1D47A8` / `#1A1410` | pas de rouge ni de vert : la « bonne réponse » est un repère bleu ; l'alerte reste typographique | — |

**Interdits** : texte crème sur l'orange (2,90:1) ou blanc (3,06:1), même en titre ; bleu sur l'orange (2,72:1) ; un trait d'une autre couleur que le graphite. Les repères bleus vivent **sur la plaque**, jamais sur l'orange.

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Une seule famille : Fredoka** (`@fontsource/fredoka`, déjà installée, utilisée par aucune autre identité). Aucune police ajoutée (pas de Lexend).
- **Titres** : Fredoka 700, **104 px**, interligne 1,08, interlettrage 0, couleur `#1A1410`, 1 à 4 mots sur 1–2 lignes, centrés sur x = 510 dans la bande orange (centre y ≈ 355, bande 230–470, glyphes à partir de y ≈ 240).
- **Repère chiffré** : Fredoka 700, 76 px, bleu `#1D47A8`, sur la plaque (« +1 »).
- **Étiquettes** : Fredoka 600, 60 px (56 px pour un mot long comme « Pouilles »), `#22252A` sur étiquette crème. Jamais en dessous de 54 px.
- Rendu par Pillow, qui lit directement les `.woff2` @fontsource (`textpng.font_path`), puis converti en surface cairo prémultipliée. pycairo ne charge pas les `.woff2` : ne pas l'utiliser pour le texte.
- **Jamais de texte écrit par le trait.**

## Formes & matières
- **Fond** : orange plein, sans texture.
- **La plaque** : rectangle 820 × 960 px (x 120–940, y 500–1460) **à angles vifs**, posé à plat, 4 vis aux coins (cercle 10 px, fente), ombre portée sur l'orange. Grain de surface opensimplex (graine du short) calculé une fois.
- **Deux règles graduées** intégrées à la plaque : bande de 56 px le long du bord haut et du bord gauche, graduations tous les 24 px, une longue toutes les 5.
- **Deux curseurs triangulaires graphite** (30 × 44 px) : celui du haut suit x, celui de gauche suit y. Deux guides pointillés (2 px, graphite à 32 %) les relient au chariot. C'est l'indice des deux axes.
- **Le chariot** (tête du traceur) : carré de 46 px à angles vifs, liseré graphite 4 px, fond gris clair translucide, point de stylo au centre. Il suit la pointe du trait.
- **Le trait** : graphite `#3A3D42`, 7 px, extrémités et angles carrés (`LINE_CAP_SQUARE`, `LINE_JOIN_MITER`), **en escalier de 12 px** (chaque pas sur un seul axe), vibration fixe ±0,5 px par sommet (opensimplex), grain de mine de crayon (masque opensimplex, opacité 0,62–1). Un seul trait par plaque, jamais levé ; les allers-retours (antennes) se superposent ; les ponts entre formes disjointes (Sicile) font partie du dessin.
- **Repères bleus** : anneau de départ (rayon 17, 6 px), point de lieu (point 13 px + anneau 26 px), fil de repère droit 5 px, arc fléché horaire 9 px.
- **Étiquettes crème** à angles vifs, liseré 3 px : seul élément « papier » de l'identité.
- Formes des dessins : grandes formes (2 500 à 5 200 px de chemin par plaque), 140 à 230 sommets après escalier. Pas de hachures, pas de remplissage.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- **Le trait** avance **à vitesse constante** (820 px/s pour le petit escargot, 850 px/s pour la botte, 900 px/s pour une carte ou un grand dessin ; plage permise 650–900), linéaire : la machine n'a pas d'easing. Il peut **s'arrêter net** sur un point clé (1,7–1,9 s) puis repartir à la même vitesse ; jamais d'accélération ni de ralenti.
- **Curseurs et chariot** suivent la pointe image par image (proportion exacte de x et de y) ; ils ne rebondissent pas.
- **Repères et étiquettes** : apparition `backOut(1.6)` en 0,28 s (mise à l'échelle depuis leur centre), quand la pointe atteint le jalon ; le fil de repère se tire en 0,25 s ; la flèche de sens se dessine en 0,5 s.
- **Titres** : entrée 0,3 s `backOut` avec glissement de 26 px vers le haut et fondu ; sortie en fondu 0,2 s ; jamais deux titres à la fois.
- **Avance plaque** : 3 crans de 0,2 s (chaque cran : `outCubic` 0,09 s puis arrêt 0,11 s), course 1 484 px vers le haut ; plaque vierge `outCubic` 0,35 s depuis le bas, lancée 0,25 s après le 1er cran (chevauchement 0,35 s : aucune image à plus de 78 % d'orange uni), arrêt sec (clac) à la fin du 3ᵉ cran.
- Durées tokens : fast 0,28 s / base 0,6 s / slow 1,9 s ; cliquetis sonore toutes les 0,24 s pendant le tracé ; hook : titre présent dès 0 s, trait en mouvement dès 0,3 s.
- **Jamais** : deux traits à la fois, un trait en couleur, un trait levé (tout raccord est un pont dessiné), du texte écrit par le trait, un zoom sur la plaque, un fondu enchaîné classique entre scènes, une agitation de l'objet pour effacer, un easing sur le trait, un flash.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
- Caméra **fixe, frontale, orthographique** : la plaque est vue à plat, entière, toujours au même endroit (x 120–940, y 500–1460).
- **Aucun mouvement de caméra** : pas de zoom, pas de panoramique, pas de travelling. Le seul mouvement de grande surface est mécanique : l'avance de la plaque.
- Pas de profondeur de champ ; tout est net. L'ombre portée de la plaque est la seule profondeur.

## Transitions (liste nommée, durée, quand les utiliser)
| Nom | Durée | xfade ffmpeg équivalent | Quand |
|---|---|---|---|
| **avance plaque** (signature) | 0,6 s (3 crans de 0,2 s ; la plaque vierge entre 0,25 s après le 1er cran, en 0,35 s, et s'arrête à la fin du 3ᵉ cran) | `slideup` (approximation : l'original est en crans) | entre deux plaques (deux idées) ; 1 fois par short de 15 s, 2 au plus. SFX : `click` à chaque cran, `thud` au clac |
| **arrêt sur repère** | 1,7–1,9 s | — | le traceur s'arrête sur un point clé ; repère bleu + étiquette crème ; la voix nomme le point |
| **relève de titre** | 0,2 s sortie + 0,3 s entrée | `fade` | changement de titre dans la bande orange (pendant l'avance plaque, la plaque masque la bande) |
| *variante non prouvée* : **la plaque se vide** | 0,8 s | `dissolve` | effacer sur place par un masque de bruit opensimplex précalculé (seuil qui monte), l'objet reste immobile ; à réserver à une fin en boucle |

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
1. **Hook (0–1 s)** : la question d'enfant est déjà dans la bande orange à t = 0 (≤ 4 mots) ; plaque vierge avec l'anneau bleu de départ ; le trait part à 0,3 s, curseurs et chariot bougent.
2. **Plaque 1 (≈ 0,3–5 s)** : un premier dessin simple d'un seul trait (2 700–3 900 px) qui pose l'idée (un petit escargot ; une botte). Une étiquette crème au plus.
3. **Avance plaque (0,6 s)** : 3 crans, clac à la fin du 3ᵉ, nouveau titre.
4. **Plaque 2 (≈ 5–13 s)** : le dessin qui répond (4 000–5 200 px), avec 1–2 **arrêts sur repère** de 1,7–1,9 s et 2–3 repères bleus ; un titre de 2–3 mots par temps de 3–4 s.
5. **Chute et fin (≈ 3 s)** : dessin complet tenu, question ouverte ou mot final dans la bande orange ; fin propre (tenue ≥ 2,5 s), pas de boucle forcée.

## Zones sûres
Haut 220 px, bas 320 px, droite 120 px, gauche 60 px. Bande titre entre y 230 et 470 ; plaque x 120–940, y 500–1460 (ombre jusqu'à 954 × 1474) : rien d'important sous y = 1474, rien à droite de x = 954. Textes centrés sur x = 510 (milieu de la zone 60–960). Les étiquettes restent dans la plaque (« Pouilles » déborde de 4 px de la plaque, jusqu'à x = 944).

## Librairies recommandées et pourquoi
- **shapely 2.2.0** (épinglée, `uv pip install shapely==2.2.0`) porte la signature : elle construit **le chemin unique**. `segmentize` (2 px) puis quantification sur une grille de 12 px avec un seul axe par pas = l'escalier ; `linemerge` raccorde les morceaux qui se touchent ; `nearest_points` calcule le pont le plus court vers une composante disjointe (la Sicile) ; `Polygon.exterior.simplify` réduit un contour tracé à la main ; `affinity` tourne et ajuste un dessin à sa boîte ; `substring(chemin, 0, L(t))` et `interpolate` donnent l'état à t sans horloge (≈ 0,02 s / 100 images).
- **opensimplex 0.4.5.1** (épinglée) : grain de surface de la plaque, masque de grain du trait, vibration ±0,5 px. Champs calculés **une seule fois** par graine (3,8 s mesurés) et mis en cache `.npz` ; jamais appelé par image.
- **pycairo 1.29** dessine la plaque, les règles, le trait, les repères ; **Pillow 13** pose les textes Fredoka (lit les `.woff2`) ; **numpy** compose ; **ffmpeg** encode (pipe `rawvideo bgra` → x264 crf 16, puis `assemble.py mux` crf 20).
- **skia-python est écarté** : la version 144.1 s'installe mais son import échoue ici (`ImportError: libEGL.so.1` ; un lien vers le libEGL de Chromium donne `undefined symbol: eglQueryString`) et il faudrait un paquet système. pycairo fait le même travail.
- Coût mesuré : **4,9 s / 100 images** sous charge partagée (rendus complets v2 : 22,8 s pour 465 images et 23,4 s pour 480 images ; v1 : 21,1 et 21,5 s), 2,79 s / 100 images à charge plus basse ; md5 du mp4 identique sur deux rendus (v1).
- Moteur réutilisable : `out/shorts/trait-continu__enfants__dessine-un-escargot-d-un-seul-trait/src/traceur.py` (copie identique dans le short Italie) ; une scène = des morceaux de chemin, des arrêts, des repères et des titres.

## Familles de contenus adaptées / inadaptées
- **Adaptées** : **enfants** (« dessine un … d'un seul trait », formes d'animaux, spirales, symétries, comptage de pattes avec allers-retours), **géographie** schématique (silhouettes de pays, « la France est un hexagone », îles reliées par des ponts), géométrie et explicatif simple (une figure qui se construit), engagement doux (« devine ce que trace la machine » avant la fin du tracé).
- **Inadaptées** : histoire et événements (pas de personnages, pas d'ambiance), données denses (un seul trait ne fait pas un graphique à plusieurs séries), abstrait pur et boucles hypnotiques (le trait linéaire est lent), tout ce qui demande de la couleur ou du texte long, et tout argument de souvenir d'un produit.

## Shorts de preuve (chemins)
- `out/shorts/trait-continu__enfants__dessine-un-escargot-d-un-seul-trait/` — 15,5 s, graine 7, 2 plaques (3 888 px puis 5 210 px), rendu 22,8 s.
- `out/shorts/trait-continu__geographie__l-italie-a-la-forme-d-une-botte/` — 16,0 s, graine 11, 2 plaques (2 688 px puis 4 115 px + 2 arrêts), rendu 23,4 s.

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)
- Voix prévue : **Fish Audio « Arnold »** (conteur masculin FR), ton doux et enjoué ; narration écrite (`narration.json`), non enregistrée dans cette livraison.
- Public 6–10 ans : **2,0–2,3 mots/s**, **28 à 33 mots pour 15 s**, 4 à 6 lignes, une phrase courte par plaque ou par repère ; `maxDuration ≥ mots / 2,2`.
- La voix démarre avec le trait (0,2 s), se tait pendant l'avance plaque (le clac porte la transition), et reprend quand le traceur **s'arrête sur un repère** : l'arrêt laisse la phrase finir avant que le trait reparte.
- Le visuel ne porte que la question (titre), 1–2 mots par temps et les noms de lieux ; la voix nomme ce que le trait fait (« du centre, on tourne », « ici, le talon »). Pas de CTA pressant : une question ouverte à la fin.

## Risques et limites
- **Distance avec un produit de dessin existant (obligatoire)** : la première direction reproduisait l'habillage d'un objet de dessin du commerce, notoire (cadre de couleur aux coins arrondis autour d'un écran gris, deux boutons ronds blancs en bas, effacement en agitant l'objet). **Ne jamais réintroduire** : cadre ou bord en plastique arrondi autour de la plaque, boutons ronds (en particulier deux dans les coins bas), agitation de l'objet pour effacer, nom ou allusion de produit dans le titre, le texte ou la narration, argument de souvenir d'enfance ; ne pas décrire le grain de la plaque ni l'effacement avec le vocabulaire de ce produit. Les deux axes passent par les **règles graduées et leurs curseurs**, l'effacement par **l'avance plaque**.
- **Sens de la coquille (simplification assumée)** : la flèche bleue « vers la droite » (arc horaire) est dessinée au-dessus d'un escargot vu de profil. La convention « dextre » se juge **vu depuis l'apex** (le sommet de la spirale) : vue de profil, selon le côté qu'on regarde, une coquille dextre peut sembler tourner dans l'autre sens. La flèche est donc une simplification ; le texte « la plupart tournent à droite » reste juste. Pour un nouveau short, préférer une coquille vue du dessus ou écrire « vu du dessus ».
- **Escalier** : en dessous de 12 px, le pas ressemble à de l'aliasing sur téléphone ; ne pas descendre sous 12 px ni sous 6 px d'épaisseur. Les petites spirales (rayon < 50 px) deviennent des carrés : garder les détails ≥ 4 pas.
- **Lisibilité des cartes** : la Calabre et la Sicile sont petites à cette échelle (≈ 180 px pour la Sicile) ; les étiquettes doivent être placées à la main, dans la mer, avec un fil de repère si le lieu est trop proche d'une autre étiquette.
- **Rythme** : un trait linéaire est lent ; au-delà de 5 200 px par plaque l'enfant décroche. Les arrêts sur repère servent à caler la voix, pas à meubler (≤ 2 s).
- **Contours tracés à la main** (80 et 18 points lon/lat, ≈ 0,1°) : silhouettes plausibles, pas des cartes exactes ; ne pas s'en servir pour des distances.
- **Typographie ronde** cousine de Baloo 2 (pastel-diorama) et Nunito (tableau-craie) : l'identité tient par le fond orange plein, la plaque grise et le trait unique, pas par la police.
- **Voix** : narration écrite mais non enregistrée ; débit enfant (2,2 mots/s) à vérifier avec Arnold, plus lent que les 2,6 mots/s des autres identités.
- Moteur dupliqué dans chaque `src/` (même fichier) : toute correction doit être recopiée dans les deux shorts.
