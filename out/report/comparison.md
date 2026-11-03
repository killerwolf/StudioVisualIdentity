# Comparaison des 10 identités

Toutes les valeurs viennent des fichiers livrés (`identities/*/tokens.json`, `shorts/*/short.json`) ou de mesures faites pendant la campagne. Index machine : `report/campaign.json`, matrice : `report/matrix.json`, tests de reconnaissance : `report/recognition.json`.

## 1. Tableau comparatif

| Identité | Promesse (résumé) | Fond / accents | Display / texte | Signature de mouvement | Transitions phares | Libs | Coût mesuré (s/100 frames) |
|---|---|---|---|---|---|---|---|
| **neon-lab** — Labo Néon | la science vue en lumière, visualisation de musée | `#05060B` / cyan `#38F9FF`, magenta `#FF3DCB`, lime `#B6FF3B` | Space Grotesk 700 / JetBrains Mono | glides `outExpo`, pulses de bloom au temps fort, orbite 15° | pulse-flash, glide, loop-seam | three.js, twgl.js, OpenCV | 55,5 (twgl) – 182,9 (three+bloom) + OpenCV 32–37 |
| **pastel-diorama** — Diorama Pastel | monde de jouets doux pour 6–10 ans | `#FFE8EF` / rose, ciel, jaune, menthe | Baloo 2 800 / Nunito | rebonds `back.out(1.8)`, squash & stretch, flottement | pastille-pop, teinte-ciel, couvercle-pop | Zdog, A-Frame, GSAP | 66,0 (Zdog) – 82,9 (A-Frame sans ombres) |
| **atlas-grave** — Atlas Gravé | le savoir s'imprime à l'encre sur une carte gravée | `#EFE3C8` / sang-de-bœuf, bleu ardoise, or | Cormorant Garamond 700 / Cinzel, Plex Mono | encre qui sèche (`power2.out`), zooms cartographiques lents, sceaux | encre-qui-seche, sceau, panoramique-parchemin | D3.js, GSAP, pycairo | 128,7 – 135,7 |
| **tableau-craie** — Tableau Craie | un prof bienveillant dessine le monde à la craie | `#1F3A30` / craie crème, orange, bleu, rouge | Nunito 800 / Caveat 700 | tout s'écrit (Create, dashoffset), coup de chiffon | chiffon, craie-qui-se-pose | Manim, Rough.js, GSAP | 19,1 (Manim) – 309,2 (Rough.js + filtre SVG plein cadre) |
| **swiss-data** — Grille Suisse | un chiffre qui claque par écran sur grille 12 col. | `#F4F1EA` / rouge `#E3241B`, noir, bleu | Archivo Black / Inter 600–800 | volets rouges `expo.out`, compteurs, push-in | volet-rouge, coupe-nette, wipe-ligne | D3.js, GSAP | **13,7 – 20,5** |
| **pixel-arcade** — Arcade Pixel | vraie physique filmée comme une partie d'arcade | `#0E0B1F` / rose, vert, jaune, bleu | Rubik Mono One / Press Start 2P | `steps(6)`, quantifié 4 px, clignotements, screenshake | pixel-mosaic, step-slide-out, blink-in | Matter.js, p5.js | 41,0 – 43,4 |
| **liquid-chrome** — Chrome Liquide | matière chromée hypnotique en plan-séquence | `#0B0B10` / lilas, rose, menthe, or pâle | Syne 800 / Inter | simulation continue, ralentis, aucune coupe | fondu-chrome, glisse-haut, dissolution-lente | Taichi, three.js, OpenCV | 105,6 (Taichi+OpenCV) – 178,0 (three.js) |
| **gazette-1900** — Gazette 1900 | chaque grand moment arrive en une de journal | `#E9E1CF` / rouge `#B3261E`, encre | Playfair Display 900 / IBM Plex Mono | une qui tourbillonne et se pose (`power3.out`), tampons, typewriter | tourniquet, flash de coupe, coup de tampon | GSAP, OpenCV | 33,3 – 65,3 + OpenCV 21–28 |
| **bauhaus-kinetic** — Bauhaus Cinétique | chaque idée devient un puzzle géométrique | `#F2EDE3` / rouge, jaune, bleu, noir | Unbounded 800 / Space Grotesk 500 | staggers en grille `outBack(1.6)`, morphing, snap 90° | grid-wipe, snap-90, shape-morph | anime.js, flubber, Paper.js | 28,2 – 31,7 |
| **aquarelle-conte** — Aquarelle Conte | chaque short est une page d'album racontée | `#F7F1E6` / corail, bleu, ocre, sauge | Fraunces 700 / Nunito 600 | lavis qui se diffusent, parallaxe multiplane, respiration | lavis-qui-s-ouvre, fondu-de-ciel, encre-qui-s-imbibe | p5.js, Paper.js | 109,2 – 117,6 |

**Attention, coûts sous contention** : 10 studios rendaient en même temps sur 4 cœurs (load average mesuré 16–22). Référence machine calme (Phase 0) : three.js + bloom = 59,8 s/100 frames, Manim simple ≈ 4,8 s/100 frames, Taichi 20 k particules ≈ 9,4 s/100 frames. Les temps ci-dessus surestiment donc d'environ ×2–3 le coût sur une machine dédiée.

## 2. Les 20 shorts

| Short | Durée (s) | renderTimeSec | s/100 frames | Poids (Mo) | Voix off prévue (lignes / mots / voix) |
|---|---|---|---|---|---|
| `aquarelle-conte__enfants__ou-vont-les-etoiles-le-jour` | 15.0 | 529 | 117.6 | 6.7 | 6 / 38 mots / Aoede |
| `aquarelle-conte__histoire__phare-d-alexandrie` | 16.0 | 524.2 | 109.2 | 5.8 | 5 / 38 mots / Aoede |
| `atlas-grave__geographie__plus-longs-fleuves-du-monde` | 15.0 | 610.8 | 135.7 | 4.8 | 8 / 39 mots / Orus |
| `atlas-grave__histoire__premier-tour-du-monde-1519-1522` | 16.0 | 617.8 | 128.7 | 8.0 | 8 / 37 mots / Charon |
| `bauhaus-kinetic__engagement__trouve-l-intrus` | 14.0 | 133.3 | 31.7 | 1.6 | 8 / 27 mots / Fenrir |
| `bauhaus-kinetic__explicatif__abeilles-hexagones` | 16.0 | 135.2 | 28.2 | 1.7 | 5 / 36 mots / Orus |
| `gazette-1900__evenements__9-novembre-1989-mur-de-berlin` | 15.0 | 149.8 | 33.3 | 16.0 | 8 / 38 mots / Orus |
| `gazette-1900__histoire__1789-en-20-secondes` | 18.75 | 367.2 | 65.3 | 19.8 | 7 / 49 mots / Orus |
| `liquid-chrome__abstrait__quatre-peintures-mpm` | 14.0 | 443.7 | 105.6 | 2.1 | 6 / 25 mots / Achernar |
| `liquid-chrome__engagement__quelle-couleur-remplit-le-verre` | 15.0 | 800.9 | 178.0 | 4.4 | 7 / 33 mots / Achernar |
| `neon-lab__abstrait__champ-de-force-lucioles` (boucle parfaite) | 12.0 | 199.7 | 55.5 | 10.6 | 3 / 25 mots / Achernar |
| `neon-lab__explicatif__lune-meme-face` | 16.0 | 877.7 | 182.9 | 6.8 | 4 / 37 mots / Orus |
| `pastel-diorama__enfants__d-ou-vient-la-pluie` | 16.0 | 316.8 | 66.0 | 2.6 | 5 / 43 mots / Leda |
| `pastel-diorama__engagement__choisis-ta-boite-renard` | 15.0 | 373.1 | 82.9 | 2.8 | 5 / 39 mots / Puck |
| `pixel-arcade__abstrait__la-balle-peut-elle-s-echapper` | 15.0 | 184.3 | 41.0 | 2.3 | 6 / 27 mots / Achernar |
| `pixel-arcade__engagement__quelle-bille-gagne-la-course` | 16.0 | 208.5 | 43.4 | 1.7 | 6 / 37 mots / Fenrir |
| `swiss-data__evenements__j-272-eclipse-2-aout-2027` | 15.0 | 92.3 | 20.5 | 0.9 | 4 / 29 mots / Charon |
| `swiss-data__geographie__ou-vivent-8-milliards` | 15.0 | 61.5 | 13.7 | 0.9 | 6 / 35 mots / Orus |
| `tableau-craie__enfants__comment-une-graine-devient-un-arbre` | 15.5 | 1437.7 | 309.2 | 6.3 | 7 / 46 mots / Kore |
| `tableau-craie__explicatif__pourquoi-le-ciel-est-bleu` | 16.5 | 94.4 | 19.1 | 9.0 | 6 / 41 mots / Kore |

QA automatique (`tools/check.py --all`, résultat dans `report/qa.json`) : **20/20 OK** — 1080×1920, 30 fps, H.264 yuv420p, 12–18,75 s, piste audio, aucune frame noire (blackdetect ≥ 0,25 s), aucun gel ≥ 3 s, fichiers requis présents. Les `renderTimeSec` excluent l'attente de slot et les passes OpenCV séparées (indiquées dans les notes de chaque `short.json`).

## 3. Matrice identité × famille × librairie

| Identité \ famille | abstrait | enfants | explicatif | histoire | geographie | evenements | engagement |
|---|---|---|---|---|---|---|---|
| neon-lab | twgl.js, OpenCV | | three.js, OpenCV | | | | |
| pastel-diorama | | Zdog, GSAP | | | | | A-Frame, GSAP |
| atlas-grave | | | | D3.js, GSAP, pycairo | D3.js, GSAP, pycairo | | |
| tableau-craie | | Rough.js, GSAP | Manim (+PIL) | | | | |
| swiss-data | | | | | D3.js, GSAP | D3.js, GSAP | |
| pixel-arcade | p5.js | | | | | | Matter.js, p5.js |
| liquid-chrome | Taichi, OpenCV | | | | | | three.js |
| gazette-1900 | | | | GSAP, OpenCV | | GSAP, OpenCV | |
| bauhaus-kinetic | | | Paper.js, flubber, anime.js | | | | Paper.js, flubber, anime.js |
| aquarelle-conte | | p5.js, Paper.js | | p5.js, Paper.js | | | |
| **Couverture** | 3 | 3 | 3 | 3 | 2 | 2 | 4 |

- **Librairies niveau A** (8/8 utilisées dans au moins un short livré) : three.js (neon-lab, liquid-chrome), Matter.js (pixel-arcade), p5.js (pixel-arcade, aquarelle-conte), GSAP (5 identités), D3.js (atlas-grave, swiss-data), Manim (tableau-craie), A-Frame (pastel-diorama), Taichi (liquid-chrome).
- **Librairies niveau B** (8 utilisées, ≥ 5 requises) : twgl.js, OpenCV, Zdog, pycairo, Rough.js, anime.js, flubber, Paper.js. Non utilisées : PixiJS, Babylon.js, Matplotlib (leurs identités candidates — brut-meme pour PixiJS — n'ont pas été retenues).
- **Niveau C** (Blender, Remotion) : non tenté, faute de marge CPU.

## 4. Test de reconnaissance à l'aveugle

Deux tests indépendants, tous deux reproductibles (`tools/recognition.py`).

**a) Juge visuel aveugle** — un agent sans aucun contexte a reçu 40 frames anonymisées (2 par short, noms aléatoires `img_XXXX.jpg`, graine 2026, clé cachée hors de sa portée) avec la consigne « faire 10 groupes de 4 par style, pas par sujet ». Résultat confronté à la clé : **10 groupes purs sur 10, 40/40 images bien classées**. Confiance déclarée 0,85–0,98 ; la plus basse pour liquid-chrome (0,85). Confusions jugées les plus difficiles par le juge : les deux styles plats sur papier crème (swiss-data vs bauhaus-kinetic) — séparés par la grammaire « infographie rouge seule » vs « tuiles rouge/jaune/bleu/noir » — et les trois identités sur fond sombre (liquid-chrome / neon-lab / pixel-arcade).

**b) Signature mesurée** — histogramme couleur Lab 8×8×8 (Bhattacharyya) + histogramme de gradients (χ²), 8 frames par short, plus proche voisin parmi les 19 autres shorts : **18/20 (90 %)** ont pour plus proche voisin un short de la même identité ; distance moyenne intra-identité 0,212 contre 0,831 inter-identités (ratio 0,25). Les 2 échecs : les deux shorts **liquid-chrome** ont pour plus proche voisin un short neon-lab (fonds quasi noirs + accents pastel/néon) — la palette seule ne les sépare pas ; c'est la matière (chrome liquide vs points lumineux) et la typo (Syne vs Space Grotesk/Mono) qui les distinguent, comme l'a fait le juge.

**Verdict** : chaque identité est reconnaissable à l'aveugle ; deux shorts d'une même identité se ressemblent plus que deux shorts d'identités différentes (ratio 0,25). Point de vigilance : liquid-chrome et neon-lab partagent le fond noir ; pour une chaîne qui les ferait cohabiter, durcir la différence de palette (p. ex. liquid-chrome sur fond gris perle ou graphite chaud).

## 5. Classement pour une chaîne durable et industrialisable

Critères (pondération) : coût de rendu mesuré (25 %), facilité de templatisation par un agent — combien de choses changent d'un épisode à l'autre (25 %), largeur de familles et de sujets possibles (20 %), force de reconnaissance (15 %), risques de production constatés (15 %).

| Rang | Identité | Pourquoi |
|---|---|---|
| **1** | **swiss-data** | Le moins cher de la campagne (13,7–20,5 s/100 frames, < 1 Mo par short), zéro physique, zéro 3D. Un épisode = un jeu de données + 4 écrans « un chiffre par écran » ; tout est piloté par une timeline GSAP sur un module partagé (`grille.js`). S'étend à n'importe quel sujet chiffré (géo, actu, classements, sport, économie). Risque : visuellement sobre — l'identité tient à la discipline de la grille. |
| **2** | **gazette-1900** | Identité la plus mémorable (« une » qui tourbillonne + tampon + grain). Format « ce jour-là » = calendrier éditorial infini (365 anniversaires/an), recette en pages de 6 temps à 128 bpm. Coût moyen (33–65 s/100 + OpenCV 21–28). Risques : poids des fichiers (grain -> 16–20 Mo), gravures procédurales à concevoir par sujet. |
| **3** | **pixel-arcade** | Mécanique d'engagement la plus forte (pari, photo-finish, commentaire) et variété quasi infinie par graine : 600 graines pré-simulées en 35 s, filtrage automatique. Coût bas (41–43 s/100). Risques : déterminisme fragile (piège `atan2` Node ≠ Chromium, réglages friction Matter), lassitude du genre « course de billes ». |
| 4 | bauhaus-kinetic | Très bon marché (28–32 s/100), quiz et explicatifs géométriques réutilisables ; demande un travail de conception visuelle par sujet (chaque idée doit devenir un puzzle). |
| 5 | tableau-craie | Le meilleur explicatif (Manim à 19 s/100 frames) ; mais la variante navigateur Rough.js + filtre SVG plein cadre est la plus chère de la campagne (309 s/100) et a révélé un bug de raster SwiftShader ; à industrialiser côté Manim. |
| 6 | pastel-diorama | Excellent pour une chaîne enfants avec personnages récurrents (Plip, le renard) ; deux moteurs (Zdog, A-Frame) à maintenir ; coût 66–83 s/100. |
| 7 | atlas-grave | Très beau, très « documentaire », mais cher (129–136 s/100) et limité par des côtes dessinées à la main (grossières au-delà de ×2,5). |
| 8 | aquarelle-conte | Charme fort pour « histoire du soir » ; coût 109–118 s/100 ; chaque épisode demande des décors et personnages vectoriels nouveaux. |
| 9 | neon-lab | Spectaculaire ; la boucle abstraite est bon marché (twgl 55 s/100) mais l'explicatif three.js + bloom est cher (183 s/100 sous contention) et chaque sujet scientifique demande une scène 3D. |
| 10 | liquid-chrome | Hypnotique mais le plus coûteux par seconde utile (Taichi 106, three.js 178 s/100), le moins varié (toujours des fluides) et le seul confondu par la mesure couleur (avec neon-lab). |

**Recommandation** : pour une chaîne durable, lancer **swiss-data** (data/actu), **gazette-1900** (histoire/éphémérides) et **pixel-arcade** (engagement) — trois publics, trois mécaniques, trois coûts bas à moyens, aucune confusion visuelle entre elles.
