# Comparaison des 14 identités

La voix off **réellement utilisée** pour les 31 shorts est Fish Audio « Arnold » ; les noms de voix Gemini de la table §2 sont les suggestions d'origine de `narration.json` (`voiceGeminiSuggestion`).

Toutes les valeurs viennent des fichiers livrés (`identities/*/tokens.json`, `shorts/*/short.json`) ou de mesures faites pendant la campagne. Index machine : `report/campaign.json`, matrice : `report/matrix.json`, tests de reconnaissance : `report/recognition.json`.

## 1. Tableau comparatif

| Identité | Promesse (résumé) | Fond / accents | Display / texte | Signature de mouvement | Transitions phares | Libs | Coût mesuré (s/100 frames) |
|---|---|---|---|---|---|---|---|
| **neon-lab** — Labo Néon | la science vue en lumière, visualisation de musée | `#05060B` / cyan `#38F9FF`, magenta `#FF3DCB`, lime `#B6FF3B` | Space Grotesk 700 / JetBrains Mono | glides `outExpo`, pulses de bloom au temps fort, orbite 15° | pulse-flash, glide, loop-seam | three.js, twgl.js, OpenCV, Matplotlib | 54,0 (Matplotlib) – 55,5 (twgl) – 182,9 (three+bloom) + OpenCV 15–37 |
| **pastel-diorama** — Diorama Pastel | monde de jouets doux pour 6–10 ans | `#FFE8EF` / rose, ciel, jaune, menthe | Baloo 2 800 / Nunito | rebonds `back.out(1.8)`, squash & stretch, flottement | pastille-pop, teinte-ciel, couvercle-pop | Zdog, A-Frame, GSAP | 66,0 (Zdog) – 82,9 (A-Frame sans ombres) |
| **atlas-grave** — Atlas Gravé | le savoir s'imprime à l'encre sur une carte gravée | `#EFE3C8` / sang-de-bœuf, bleu ardoise, or | Cormorant Garamond 700 / Cinzel, Plex Mono | encre qui sèche (`power2.out`), zooms cartographiques lents, sceaux | encre-qui-seche, sceau, panoramique-parchemin | D3.js, GSAP, pycairo | 128,7 – 135,7 |
| **tableau-craie** — Tableau Craie | un prof bienveillant dessine le monde à la craie | `#1F3A30` / craie crème, orange, bleu, rouge | Nunito 800 / Caveat 700 | tout s'écrit (Create, dashoffset), coup de chiffon | chiffon, craie-qui-se-pose | Manim, Rough.js, GSAP | 19,1 (Manim) – 309,2 (Rough.js + filtre SVG plein cadre) |
| **swiss-data** — Grille Suisse | un chiffre qui claque par écran sur grille 12 col. | `#F4F1EA` / rouge `#E3241B`, noir, bleu | Archivo Black / Inter 600–800 | volets rouges `expo.out`, compteurs, push-in | volet-rouge, coupe-nette, wipe-ligne | D3.js, GSAP | **13,7 – 20,5** |
| **pixel-arcade** — Arcade Pixel | vraie physique filmée comme une partie d'arcade | `#0E0B1F` / rose, vert, jaune, bleu | Rubik Mono One / Press Start 2P | `steps(6)`, quantifié 4 px, clignotements, screenshake | pixel-mosaic, step-slide-out, blink-in | Matter.js, p5.js, PixiJS | 32,6 (PixiJS) – 43,4 |
| **liquid-chrome** — Chrome Liquide | matière chromée hypnotique en plan-séquence | `#0B0B10` / lilas, rose, menthe, or pâle | Syne 800 / Inter | simulation continue, ralentis, aucune coupe | fondu-chrome, glisse-haut, dissolution-lente | Taichi, three.js, OpenCV, Babylon.js | 105,6 (Taichi+OpenCV) – 123,2 (Babylon, CPU peu chargé) – 178,0 (three.js) |
| **gazette-1900** — Gazette 1900 | chaque grand moment arrive en une de journal | `#E9E1CF` / rouge `#B3261E`, encre | Playfair Display 900 / IBM Plex Mono | une qui tourbillonne et se pose (`power3.out`), tampons, typewriter | tourniquet, flash de coupe, coup de tampon | GSAP, OpenCV | 33,3 – 65,3 + OpenCV 21–28 |
| **bauhaus-kinetic** — Bauhaus Cinétique | chaque idée devient un puzzle géométrique | `#F2EDE3` / rouge, jaune, bleu, noir | Unbounded 800 / Space Grotesk 500 | staggers en grille `outBack(1.6)`, morphing, snap 90° | grid-wipe, snap-90, shape-morph | anime.js, flubber, Paper.js | 28,2 – 31,7 |
| **aquarelle-conte** — Aquarelle Conte | chaque short est une page d'album racontée | `#F7F1E6` / corail, bleu, ocre, sauge | Fraunces 700 / Nunito 600 | lavis qui se diffusent, parallaxe multiplane, respiration | lavis-qui-s-ouvre, fondu-de-ciel, encre-qui-s-imbibe | p5.js, Paper.js | 109,2 – 117,6 |
| **brut-meme** — Brut Mème *(réhabilitée)* | énergie mème brutaliste, un chiffre ou un mot qui claque au beat | `#111111` / jaune `#FFE600`, rouge `#FF2D2D`, blanc | Anton (plein cadre) / Inter | coupes au beat `power4.out`, punch-in 1,15 -> 1 en 3 images, shake ≤ 18 px | hard-cut, punch-cut, slam | PixiJS, GSAP | 49,8 – 58,5 |
| **cosmos-doc** — Cosmos Doc *(réhabilitée)* | documentaire spatial cinéma, lumière d'étoile et échelle | `#000004` / ambre `#FFB347`, bleu glace `#6EC6FF`, braise | Bebas Neue / Inter | une seule courbe lente `sine.inOut`, fondus + interlettrage qui se resserre, flare anamorphique | dip-to-black, fade-tracking, fade-out | three.js, GSAP | 174,9 – 186,4 |
| **riso-zine** — Zine Riso *(réhabilitée)* | fanzine risographie bicolore, collage et annotations au marqueur | `#F6F0E4` / rose fluo `#FF48B0`, bleu `#0078BF`, jaune `#FFE800` | Space Mono / Permanent Marker | animation « on twos » 12 i/s, repérage qui glisse, découpes qui claquent | coupe-de-page, slam-découpe, trait-marqueur | p5.js, GSAP, OpenCV | 25,9 – 43,0 (navigateur) + OpenCV 28–36 |
| **topo-relief** — Relief Topo *(réhabilitée)* | expédition topographique 3D, courbes de niveau qui s'allument | `#14221C` / ocre `#E8C872`, terracotta `#D9734E`, sarcelle `#9FD3C7` | Inter 800 / JetBrains Mono | terrain qui s'extrude, courbes qui montent, survols de drone `outCubic` | courbes-qui-montent, survol, fondu-carte | three.js, D3.js | 108,2 – 169,0 |

**Attention, coûts sous contention** : 10 studios rendaient en même temps sur 4 cœurs (load average mesuré 16–22). Référence machine calme (Phase 0) : three.js + bloom = 59,8 s/100 frames, Manim simple ≈ 4,8 s/100 frames, Taichi 20 k particules ≈ 9,4 s/100 frames. Les temps ci-dessus surestiment donc d'environ ×2–3 le coût sur une machine dédiée.

## 2. Les 31 shorts

| Short | Durée (s) | renderTimeSec | s/100 frames | Poids (Mo) | Narration (lignes / mots / voix Gemini suggérée à l'origine) |
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
| `pixel-arcade__engagement__quelle-couleur-conquiert-l-ecran` (3ᵉ, PixiJS) | 15.5 | 151.4 | 32.6 | 1.4 | 6 / 31 mots / Fenrir |
| `liquid-chrome__abstrait__pendule-de-newton-chrome` (3ᵉ, Babylon.js, boucle parfaite) | 12.0 | 443.5 | 123.2 | 5.2 | 5 / 23 mots / Achernar |
| `neon-lab__explicatif__effet-papillon-double-pendule` (3ᵉ, Matplotlib) | 15.0 | 243.1 | 54.0 | 2.8 | 4 / 30 mots / Orus |
| `brut-meme__engagement__test-des-3-secondes-stroop` | 15.5 | 231.6 | 49.8 | 3.0 | 7 / 37 mots / Fenrir |
| `brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde` | 16.0 | 280.8 | 58.5 | 4.9 | 6 / 41 mots / Fenrir |
| `cosmos-doc__evenements__voyager-1-a-un-jour-lumiere` | 15.0 | 787.1 | 174.9 | 6.1 | 4 / 30 mots / Charon |
| `cosmos-doc__explicatif__pourquoi-venus-plus-chaude-que-mercure` | 15.0 | 838.7 | 186.4 | 7.5 | 4 / 34 mots / Orus |
| `riso-zine__evenements__geminides-j-39` | 16.0 | 340.2 | 70.9 | 17.0 | 6 / 38 mots / Puck |
| `riso-zine__geographie__5-plus-grands-deserts` | 16.0 | 299.1 | 62.3 | 16.9 | 7 / 44 mots / Puck |
| `topo-relief__geographie__comment-mesure-t-on-l-everest` | 15.0 | 760.5 | 169.0 | 8.8 | 6 / 34 mots / Orus |
| `topo-relief__histoire__hannibal-traverse-les-alpes` | 15.0 | 486.7 | 108.2 | 7.8 | 5 / 29 mots / Orus |

Les trois 3ᵉ shorts ont été rendus à 22:22–22:37 avec seulement 3 studios actifs : leurs coûts sont proches d'une machine peu chargée et ne se comparent pas directement aux 20 premiers. Les 8 shorts des identités réhabilitées (cosmos-doc, brut-meme, riso-zine, topo-relief) ont été rendus le 2026-11-04 entre 00:24 et 00:57 UTC, 4 studios en parallèle (charge 15–23) : coûts sous contention, comme le premier tour. Pour riso-zine, `renderTimeSec` inclut la passe OpenCV (navigateur 124–206 s + OpenCV 134–175 s).

QA automatique (`tools/check.py --all`, résultat dans `report/qa.json`) : **31/31 OK** — 1080×1920, 30 fps, H.264 yuv420p, 12–18,75 s, piste audio, aucune frame noire (blackdetect ≥ 0,25 s), aucun gel ≥ 3 s, fichiers requis présents. Les `renderTimeSec` excluent l'attente de slot. Ils excluent aussi les passes OpenCV séparées (indiquées dans les notes de chaque `short.json`), **sauf pour riso-zine**, dont le `renderTimeSec` inclut sa passe OpenCV.

## 3. Matrice identité × famille × librairie

| Identité \ famille | abstrait | enfants | explicatif | histoire | geographie | evenements | engagement |
|---|---|---|---|---|---|---|---|
| neon-lab | twgl.js, OpenCV | | three.js, OpenCV ; Matplotlib, OpenCV | | | | |
| pastel-diorama | | Zdog, GSAP | | | | | A-Frame, GSAP |
| atlas-grave | | | | D3.js, GSAP, pycairo | D3.js, GSAP, pycairo | | |
| tableau-craie | | Rough.js, GSAP | Manim (+PIL) | | | | |
| swiss-data | | | | | D3.js, GSAP | D3.js, GSAP | |
| pixel-arcade | p5.js | | | | | | Matter.js, p5.js ; PixiJS |
| liquid-chrome | Taichi, OpenCV ; Babylon.js | | | | | | three.js |
| gazette-1900 | | | | GSAP, OpenCV | | GSAP, OpenCV | |
| bauhaus-kinetic | | | Paper.js, flubber, anime.js | | | | Paper.js, flubber, anime.js |
| aquarelle-conte | | p5.js, Paper.js | | p5.js, Paper.js | | | |
| brut-meme *(réh.)* | | | | | | PixiJS, GSAP | PixiJS, GSAP |
| cosmos-doc *(réh.)* | | | three.js, GSAP | | | three.js, GSAP | |
| riso-zine *(réh.)* | | | | | p5.js, GSAP, OpenCV | p5.js, GSAP, OpenCV | |
| topo-relief *(réh.)* | | | | three.js, D3.js | three.js, D3.js | | |
| **Couverture (identités)** | 3 | 3 | 4 | 4 | 4 | 5 | 5 |

- **Librairies niveau A** (8/8 utilisées dans au moins un short livré) : three.js (neon-lab, liquid-chrome, cosmos-doc, topo-relief), Matter.js (pixel-arcade), p5.js (pixel-arcade, aquarelle-conte, riso-zine), GSAP (8 identités), D3.js (atlas-grave, swiss-data, topo-relief), Manim (tableau-craie), A-Frame (pastel-diorama), Taichi (liquid-chrome).
- **Librairies niveau B** (11/11 utilisées, ≥ 5 requises) : twgl.js, OpenCV, Zdog, pycairo, Rough.js, anime.js, flubber, Paper.js au premier tour ; **PixiJS** (pixel-arcade, territoire), **Babylon.js** (liquid-chrome, pendule de Newton) et **Matplotlib** (neon-lab, double pendule) ajoutées par un 3ᵉ short — elles n'avaient été attribuées à aucun studio au premier tour (choix d'orchestration, pas un échec technique).
- **Niveau C** (Blender, Remotion) : non tenté, faute de marge CPU.

## 4. Test de reconnaissance à l'aveugle

Deux tests indépendants, tous deux reproductibles (`tools/recognition.py`).

**a) Juge visuel aveugle** — un agent sans aucun contexte a reçu 40 frames anonymisées (2 par short, noms aléatoires `img_XXXX.jpg`, graine 2026, clé cachée hors de sa portée) avec la consigne « faire 10 groupes de 4 par style, pas par sujet ». Résultat confronté à la clé : **10 groupes purs sur 10, 40/40 images bien classées**. Confiance déclarée 0,85–0,98 ; la plus basse pour liquid-chrome (0,85). Confusions jugées les plus difficiles par le juge : les deux styles plats sur papier crème (swiss-data vs bauhaus-kinetic) — séparés par la grammaire « infographie rouge seule » vs « tuiles rouge/jaune/bleu/noir » — et les trois identités sur fond sombre (liquid-chrome / neon-lab / pixel-arcade).

**a bis) 2ᵉ juge aveugle, 14 identités** — un nouvel agent sans contexte a reçu 56 frames anonymisées (2 shorts par identité × 2 frames, graine 1104, clé cachée) : **14 groupes purs sur 14, 56/56 images bien classées** (confiance 0,94–0,98). Les 4 identités réhabilitées ont toutes été isolées, y compris des voisines qu'on pouvait craindre (cosmos-doc vs neon-lab, brut-meme vs pixel-arcade, riso-zine vs swiss-data, topo-relief vs atlas-grave). Confusions jugées les plus difficiles : swiss-data vs bauhaus-kinetic (crème, grotesques grasses), et les 5 styles sur fond sombre, séparés par la technique de rendu (particules lumineuses, flares photoréalistes, 3D brillante, courbes de niveau, pixels).

**b) Signature mesurée** — histogramme couleur Lab 8×8×8 (Bhattacharyya) + histogramme de gradients (χ²), 8 frames par short, plus proche voisin parmi tous les autres shorts. Sur les 20 shorts initiaux : **18/20 (90 %)**, intra 0,212 vs inter 0,831 (ratio 0,25). Sur les 23 shorts : **21/23 (91 %)**, intra 0,274 vs inter 0,837 (ratio 0,33) ; les 3 nouveaux shorts ont tous pour plus proche voisin un short de leur identité. Sur les **31 shorts (14 identités) : 29/31 (94 %)**, intra 0,250 vs inter 0,846 (ratio 0,30) ; les 8 shorts des identités réhabilitées ont tous pour plus proche voisin l'autre short de leur identité (distances 0,08–0,23). Les 2 échecs sont les deux premiers shorts **liquid-chrome** : sur 31 shorts, l'un a pour plus proche voisin un short neon-lab, l'autre cosmos-doc/Voyager (fonds quasi noirs + accents pastel/néon) — la palette seule ne les sépare pas ; c'est la matière (chrome liquide vs points lumineux) et la typo (Syne vs Space Grotesk/Mono) qui les distinguent, comme l'a fait le juge.

**Verdict** : chaque identité est reconnaissable à l'aveugle ; deux shorts d'une même identité se ressemblent plus que deux shorts d'identités différentes (ratio intra/inter 0,30 sur 31 shorts). Point de vigilance : liquid-chrome et neon-lab partagent le fond noir ; pour une chaîne qui les ferait cohabiter, durcir la différence de palette. **Vérifié** : le 3ᵉ short liquid-chrome (Babylon.js) utilise la variante « graphite chaud / perle » (`#121016`–`#1A161E`) et la mesure le classe bien avec liquid-chrome (plus proche voisin : quatre-peintures, distance 0,51), pas avec neon-lab.

## 5. Classement pour une chaîne durable et industrialisable

Critères (pondération) : coût de rendu mesuré (25 %), facilité de templatisation par un agent — combien de choses changent d'un épisode à l'autre (25 %), largeur de familles et de sujets possibles (20 %), force de reconnaissance (15 %), risques de production constatés (15 %).

| Rang | Identité | Pourquoi |
|---|---|---|
| **1** | **swiss-data** | Le moins cher de la campagne (13,7–20,5 s/100 frames, < 1 Mo par short), zéro physique, zéro 3D. Un épisode = un jeu de données + 4 écrans « un chiffre par écran » ; tout est piloté par une timeline GSAP sur un module partagé (`grille.js`). S'étend à n'importe quel sujet chiffré (géo, actu, classements, sport, économie). Risque : visuellement sobre — l'identité tient à la discipline de la grille. |
| **2** | **gazette-1900** | Identité la plus mémorable (« une » qui tourbillonne + tampon + grain). Format « ce jour-là » = calendrier éditorial infini (365 anniversaires/an), recette en pages de 6 temps à 128 bpm. Coût moyen (33–65 s/100 + OpenCV 21–28). Risques : poids des fichiers (grain -> 16–20 Mo), gravures procédurales à concevoir par sujet. |
| **3** | **pixel-arcade** | Mécanique d'engagement la plus forte (pari, photo-finish, commentaire) et variété quasi infinie par graine : 600 graines pré-simulées en 35 s, filtrage automatique. Coût bas (32,6–43 s/100). Le 3ᵉ short (territoire PixiJS, 12 min de production) prouve que la formule se décline vite en nouveaux jeux. Risques : déterminisme fragile (piège `atan2` Node ≠ Chromium, réglages friction Matter), lassitude du genre « course de billes ». |
| 4 | brut-meme *(réhabilitée)* | Bon marché (50–58 s/100 frames), moteur commun (`brut.js`) où un épisode = une liste de chiffres ou de mots ; mécanique de défi (Stroop) et de compteurs « pendant ces 15 s » déclinable à l'infini. Règle photosensibilité intégrée (≤ 3 flashs/s, pas de flash plein cadre). Risque : ton « mème » qui vieillit vite et lasse si tous les épisodes crient. |
| 5 | bauhaus-kinetic | Très bon marché (28–32 s/100), quiz et explicatifs géométriques réutilisables ; demande un travail de conception visuelle par sujet (chaque idée doit devenir un puzzle). |
| 6 | tableau-craie | Le meilleur explicatif (Manim à 19 s/100 frames) ; mais la variante navigateur Rough.js + filtre SVG plein cadre est la plus chère de la campagne (309 s/100) et a révélé un bug de raster SwiftShader ; à industrialiser côté Manim. |
| 7 | riso-zine *(réhabilitée)* | Très reconnaissable (encres en surimpression, 12 i/s), bon marché côté navigateur (26–43 s/100) mais une passe OpenCV obligatoire (28–36 s/100) et des fichiers lourds (17 Mo, grain au plafond 8 Mb/s). Bien pour agendas, listes, géographie légère. Risque : bug p5 v2 de cache de style après save/restore (rendu jeté), à connaître. |
| 8 | pastel-diorama | Excellent pour une chaîne enfants avec personnages récurrents (Plip, le renard) ; deux moteurs (Zdog, A-Frame) à maintenir ; coût 66–83 s/100. |
| 9 | topo-relief *(réhabilitée)* | Moteur de terrain procédural réutilisable pour toute montagne ou itinéraire (Everest, Hannibal) avec courbes D3 calculées une fois (224 ms) ; mais three.js cher (108–169 s/100) et cadrage vertical laborieux (8 séries de stills pour Hannibal). |
| 10 | atlas-grave | Très beau, très « documentaire », mais cher (129–136 s/100) et limité par des côtes dessinées à la main (grossières au-delà de ×2,5). |
| 11 | aquarelle-conte | Charme fort pour « histoire du soir » ; coût 109–118 s/100 ; chaque épisode demande des décors et personnages vectoriels nouveaux. |
| 12 | neon-lab | Spectaculaire ; la boucle abstraite est bon marché (twgl 55 s/100) mais l'explicatif three.js + bloom est cher (183 s/100 sous contention) et chaque sujet scientifique demande une scène 3D. |
| 13 | cosmos-doc *(réhabilitée)* | Le plus « cinéma » de la campagne, distinct de neon-lab ; mais chaque sujet demande une scène 3D (planètes, sonde) et le rendu est parmi les plus chers (175–186 s/100 sous contention). |
| 14 | liquid-chrome | Hypnotique mais le plus coûteux par seconde utile (Taichi 106, three.js 178 s/100), le moins varié (toujours des fluides) et le seul confondu par la mesure couleur (avec neon-lab). |

**Recommandation** : pour une chaîne durable, lancer **swiss-data** (data/actu), **gazette-1900** (histoire/éphémérides) et **pixel-arcade** (engagement) — trois publics, trois mécaniques, trois coûts bas à moyens, aucune confusion visuelle entre elles. Parmi les identités réhabilitées, **brut-meme** (rang 4) est la plus industrialisable : elle peut remplacer ou compléter pixel-arcade sur l'engagement pour un public plus âgé.
