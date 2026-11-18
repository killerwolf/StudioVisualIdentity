# Lyrics chemin — storyboard du plan-séquence (0 à 32,6 s)

Extrait : les 21 premières mesures du morceau test (154,5 BPM ; 1 temps = 0,388 s ; 1 mesure = 1,553 s ; premier temps à 0,00 s).
Les **temps sont ceux du vrai morceau** ; les **mots sont des paroles de remplissage inventées** (le vrai texte reste hors dépôt).
Les nombres de ce document sortent de la maquette (`proto/scene.html`, exportés dans `proto/storyboard-calcule.json` par
`proto/dump.mjs`) : ce sont eux qui ont produit les images de `images/`.

Repère : **monde = image finale**. Un point (x, y) du monde est le pixel (x, y) de l'image 1080×1920 à la fin, quand le zoom vaut 1.
La colonne « caméra » donne le point du monde placé sur le **point de lecture de l'écran (512, 860)**, le zoom, et l'angle de la
caméra (sens horaire, 0° = image finale). « Corps » = corps du texte chanté à l'écran, en px. « Mesure » = mesure.temps de l'arrivée.

## Le dessin et le chemin

```
                 fanion  [7]
                   A (510,300)
                  /|\
        [1] voile/ | \voile [2]
            G   /  |  \   D
   L (98,634)  /   |   \      R (922,634)
     \--------TL---C---TR--------/
      \  [8] pont G | pont D [3] /
   [4] \           C (510,774)  / [6]
  flanc \     [0] NOM DU BATEAU/ flanc
     G   \____________________/   D
        BL (290,1054)  [5]  BR (730,1054)
   ~~~~~~~ [9] première vague (y 1132) ~~~~~~~
        [10] le refrain, en grand (y 1262, 1384, 1502)
```

Ordre de parcours : 0 nom → 1 voile gauche (monte) → 2 voile droite (descend) → 3 pont droit → 4 flanc gauche (descend) → 5 quille →
6 flanc droit (monte) → 7 fanion → 8 pont gauche → 9 première vague → 10 refrain et zoom arrière. Toutes les lignes se lisent de
gauche à droite ; aucune n'est à l'envers dans l'image finale.

## Plan-séquence

| N° | Cadrage tenu (s) | Mesure | Où | Mots à l'écran (attaque en s) | Caméra (monde) | Zoom | Angle | Corps | Transition d'arrivée (s, durée en temps) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.00 – 1.23 | 1.1 | nom sur la coque | MONDAY'S (0.00) | (434, 935) | ×3.94 | 0° | 213 | — |
| 2 | 1.49 – 2.62 | 1.4 | nom sur la coque | DRAFT (1.55) | (622, 935) | ×4.63 | 0° | 250 | glissé 1.23 → 1.49 (0.7 t) |
| 3 | 3.01 – 4.82 | 2.4 | voile, pente gauche (monte) | I FOLD (3.20) · MY DAY (4.47, pré-posé) | (341, 587) | ×4.14 | -57° | 164 | **fouetté** 2.62 → 3.01 (1.0 t) |
| 4 | 5.05 – 6.02 | 4.2 | voile, pente gauche (monte) | IN DRAFT MODE (5.05, pré-posé) | (438, 397) | ×3.84 | -57° | 152 | glissé 4.82 → 5.05 (0.6 t) |
| 5 | 6.80 – 8.14 | 5.2 | voile, pente droite (descend) | I DRAW (7.18, pré-posé) · LINES (7.57) · BUT NOT (7.96, pré-posé) | (597, 431) | ×2.89 | 57° | 104 | **virage** 6.02 → 6.80 (2.0 t) |
| 6 | 8.26 – 9.32 | 6.2 | voile, pente droite (descend) | FOR SHOW (8.26) | (695, 624) | ×6.11 | 57° | 220 | glissé 8.14 → 8.26 (0.3 t) |
| 7 | 9.90 – 10.95 | 7.2 | pont droit | I'VE BEEN (10.29, pré-posé) · UP SINCE (10.78, pré-posé) | (664, 743) | ×3.17 | -17° | 120 | **virage** 9.32 → 9.90 (1.5 t) |
| 8 | 11.07 – 12.43 | 8.1 | pont droit | 5 A.M. (11.07) | (832, 686) | ×5.78 | -17° | 220 | glissé 10.95 → 11.07 (0.3 t) |
| 9 | 12.82 – 13.88 | 9.2 | flanc gauche (descend) | PRINTER DOWN (13.01) | (139, 776) | ×3.65 | 59° | 151 | **fouetté** 12.43 → 12.82 (1.0 t) |
| 10 | 14.12 – 15.73 | 10.1 | flanc gauche (descend) | CUZ NO INK (14.18) | (224, 961) | ×4.97 | 59° | 206 | glissé 13.88 → 14.12 (0.6 t) |
| 11 | 16.31 – 16.93 | 11.2 | quille | DRAFT MODE'S (16.70, pré-posé) | (441, 1036) | ×4.49 | 0° | 162 | **virage** 15.73 → 16.31 (1.5 t) |
| 12 | 17.09 – 18.66 | 11.4 | quille | MY SPARE KEYS (17.09) | (639, 1036) | ×4.14 | 0° | 149 | glissé 16.93 → 17.09 (0.4 t) |
| 13 | 19.16 – 20.14 | 13.2 | flanc droit (monte) | MAKE ANOTHER (19.36) | (813, 928) | ×3.44 | -59° | 150 | **virage** 18.66 → 19.16 (1.3 t) |
| 14 | 20.38 – 22.13 | 14.1 | flanc droit (monte) | NOTE.TXT (20.44) | (897, 743) | ×5.06 | -59° | 220 | glissé 20.14 → 20.38 (0.6 t) |
| 15 | 22.52 – 23.69 | 15.2 | fanion | AND YET (22.88) | (593, 246) | ×5.00 | 0° | 220 | **fouetté** 22.13 → 22.52 (1.0 t) |
| 16 | 25.24 – 25.40 | 17.1 | fanion | (recul : la pointe de la voile apparaît) | (536, 474) | ×2.30 | -3° | — | respiration 23.69 → 25.24 (4.0 t) |
| 17 | 25.79 – 27.20 | 17.3 | pont gauche | WRONG (25.98) · FOLD (26.64) | (309, 739) | ×2.34 | 17° | 140 | **fouetté** 25.40 → 25.79 (1.0 t) |
| 18 | 27.42 – 28.39 | 18.3 | première vague | SUCH A LOT (27.62, pré-posé) · OF WRONG (28.10, pré-posé) | (255, 1103) | ×3.00 | -3° | 120 | **fouetté** 27.20 → 27.42 (0.6 t) |
| 19 | 28.58 – 29.52 | 19.2 | première vague | FOLDS (28.58) | (475, 1111) | ×5.50 | -10° | 220 | glissé 28.39 → 28.58 (0.5 t) |
| 20 | 31.07 – 32.62 | 21.1 | image entière | (image d’ensemble) | (512, 860) | ×1.00 | 0° | — | **zoom arrière** 29.52 → 31.07 (4.0 t) |

Pendant un cadrage tenu, la caméra n'est pas figée : poussée de 3 % et travelling de 8 % de la largeur du groupe, dans le sens de
l'écriture (elle accompagne la pointe). À l'écran, la ligne garde un dixième de son angle (6° au plus).

## Seconde par seconde

| Temps (s) | Ce qu'on voit | Ce qui s'écrit |
|---|---|---|
| 0,0 – 1,2 | Très gros plan : premier mot du titre, jaune, 213 px de corps, sur le quadrillage bleu. Poussée lente. | Le mot s'écrit en 0,28 s dès l'image 0 (lisible avant 0,3 s). |
| 1,2 – 2,6 | Glissé vers la droite, calé sur le premier temps de la mesure 2 : second mot du titre (250 px). Le premier sèche en ivoire. | Second mot, en direct. |
| 2,6 – 3,0 | **Fouetté** d'un temps vers le pied gauche de la voile, la caméra bascule de 57° ; flou de mouvement. | Rien. |
| 3,0 – 4,8 | La ligne monte légèrement à l'écran. La tasse de café entre en haut de l'image. | Premier groupe en direct (3,20) ; le suivant, trop rapide, est pré-posé pâle à 4,08 puis repassé jaune à 4,47. Le trait avance sous les mots. |
| 4,8 – 6,0 | Glissé le long de la pente jusqu'au sommet. | Dernier groupe de la ligne : trop rapide pour le direct, mais la règle des 60 % ne laisse pas d'avance ; il apparaît d'un coup à l'arrivée de la caméra (5,01) et passe au jaune à 5,05. Le trait finit jusqu'au sommet (5,9 – 6,2). |
| 6,0 – 6,8 | **Virage en épingle** de 2 temps autour du sommet (114°), creux de zoom de 20 % : on voit un instant les deux pentes. | Premier groupe pré-posé de la ligne suivante à 6,80. |
| 6,8 – 8,1 | Pente droite, texte à 104 px (passage rapide : quatre attaques en 1,1 s). Le crayon est posé juste au-dessus. Image `03`. | « pré-posé / direct / pré-posé » : le jaune avance de groupe en groupe, 7,18 – 7,57 – 7,96. |
| 8,1 – 9,3 | Glissé court, gros plan sur la fin de la ligne (220 px), tenue 0,9 s. | Fin de ligne en direct (8,26). Le trait rejoint le pied droit de la voile. |
| 9,3 – 9,9 | **Virage** d'un temps et demi vers le centre du pont (74°). Le mât en pointillé se trace au passage. | Premier groupe pré-posé à 9,90 (0,39 s d'avance), le second à 10,39. |
| 9,9 – 12,4 | Pont droit, texte sous le trait. À 11,07, gros plan sur le chiffre (220 px), tenu 1,4 s. | Repassage à 10,29 et 10,78 ; le chiffre en direct. |
| 12,4 – 12,8 | **Fouetté** d'un temps, départ sur le premier temps de la mesure 9 : toute la largeur du bateau, de la pointe droite à la pointe gauche (824 px de monde), creux de zoom de 28 %. | Rien. |
| 12,8 – 15,7 | Flanc gauche : la ligne **descend** (6° à l'écran). Le bord de la feuille et le sol passent en bas à gauche. Croix rouge à 13,7. | Deux groupes en direct (13,01 et 14,18). |
| 15,7 – 16,3 | **Virage** au coin bas gauche (59°), la caméra se remet à plat. | Groupe pré-posé à 16,31. |
| 16,3 – 18,7 | Quille, horizontale. La clé est posée sous la ligne, à droite. | Repassage à 16,70, puis direct à 17,09. |
| 18,7 – 19,2 | **Virage** au coin bas droit (59°). | Rien. |
| 19,2 – 22,1 | Flanc droit : la ligne **remonte**. La note collée entre par la droite. Gros plan sur le dernier mot (220 px). | Direct (19,36 et 20,44). Longue tenue sur la fin : 1,7 s. |
| 22,1 – 22,5 | **Fouetté** d'un temps vers le sommet du mât. | Rien. |
| 22,5 – 23,7 | Le fanion. Son contour rouge se trace autour du mot (22,6 – 23,3). | Direct (22,88). |
| 23,7 – 25,2 | **Respiration** : recul lent de 4 temps jusqu'à ×2,3. On voit la pointe de la voile, les deux pentes, le mât, le crayon. Image `04`. On comprend que les lignes dessinent quelque chose. | Rien (silence des paroles). |
| 25,4 – 25,8 | **Fouetté** vers la pointe gauche. | Rien. |
| 25,8 – 27,2 | Pont gauche, deux mots seulement, très espacés, sous le trait. Boucle rouge de correcteur autour d'eux (26,75 – 27,2). | Direct (25,98 et 26,64). |
| 27,2 – 27,4 | **Fouetté** court (0,6 temps) sous la coque. | Premier groupe pré-posé à 27,38, le second à 27,71. |
| 27,4 – 29,5 | La première vague : la ligne ondule, la caméra roule avec elle (−3° à −10°). Gros plan sur le dernier mot (220 px). | Repassage à 27,62 et 28,10, direct à 28,58. À 29,20 le refrain commence à s'écrire, immense, sous la vague. |
| 29,5 – 31,1 | **Zoom arrière** d'une mesure, du premier temps de la mesure 20 au premier temps de la mesure 21 : de ×5,5 à ×1, l'image se redresse à 0°. Le bateau est presque entier dans le cadre à 30,3 (vérifié sur une image). | Refrain : 29,20, 29,90, 30,70. Filets d'eau sous la coque. |
| 31,1 – 32,6 | **Image d'ensemble** : la feuille entière, le sol, les quatre rubans. Recul lent de ×1 à ×0,955. Image `05`. | Refrain : 31,54 et 32,12 (le dernier est jaune sur l'image finale). Trois filets d'eau finissent de se tracer dans le bas. |

## Unités, débit et règle du pré-posé

Seuil : moins de **0,30 s par mot** (plus de 3,3 mots/s) → unité pré-posée. Sur l'extrait : 9 unités pré-posées sur 24.

| Ligne | Corps monde (px) | Interlettrage (px) | Unités : attaque–fin (durée par mot) |
|---|---|---|---|
| nom sur la coque | 54 | 2.7 | MONDAY'S 0.00–1.55 (1.55 s/mot) · DRAFT 1.55–2.62 (1.07 s/mot) |
| voile, pente gauche (monte) | 40 | 0.0 | I FOLD 3.20–4.47 (0.63 s/mot) · MY DAY 4.47–5.05 (0.29 s/mot, **pré-posé**) · IN DRAFT MODE 5.05–5.86 (0.27 s/mot, **pré-posé**) |
| voile, pente droite (descend) | 36 | 0.0 | I DRAW 7.18–7.57 (0.19 s/mot, **pré-posé**) · LINES 7.57–7.96 (0.39 s/mot) · BUT NOT 7.96–8.26 (0.15 s/mot, **pré-posé**) · FOR SHOW 8.26–9.14 (0.44 s/mot) |
| pont droit | 38 | 0.0 | I'VE BEEN 10.29–10.78 (0.24 s/mot, **pré-posé**) · UP SINCE 10.78–11.07 (0.14 s/mot, **pré-posé**) · 5 A.M. 11.07–12.20 (0.57 s/mot) |
| flanc gauche (descend) | 42 | 0.0 | PRINTER DOWN 13.01–14.18 (0.58 s/mot) · CUZ NO INK 14.18–15.48 (0.43 s/mot) |
| quille | 36 | 0.0 | DRAFT MODE'S 16.70–17.09 (0.19 s/mot, **pré-posé**) · MY SPARE KEYS 17.09–18.58 (0.50 s/mot) |
| flanc droit (monte) | 44 | 0.0 | MAKE ANOTHER 19.36–20.44 (0.54 s/mot) · NOTE.TXT 20.44–21.26 (0.82 s/mot) |
| fanion | 44 | 0.0 | AND YET 22.88–23.52 (0.32 s/mot) |
| pont gauche | 60 | 8.3 | WRONG 25.98–26.64 (0.66 s/mot) · FOLD 26.64–27.20 (0.56 s/mot) |
| première vague | 40 | 0.0 | SUCH A LOT 27.62–28.10 (0.16 s/mot, **pré-posé**) · OF WRONG 28.10–28.58 (0.24 s/mot, **pré-posé**) · FOLDS 28.58–29.20 (0.62 s/mot) |

Le refrain (dans la mer) : cinq attaques à 29,20 – 29,90 – 30,70 – 31,54 – 32,12, en direct, corps 88 / 88 / 78 / 78 / 88 px à
l'échelle 1.

## Objets rencontrés en route

| Objet | Position monde (centre) | Vu pendant |
|---|---|---|
| Tasse et auréole de café | (262, 452) | voile gauche, virage du sommet |
| Crayon | (741, 476), incliné à 68° | voile droite, respiration |
| Croix rouge | (131, 943) | flanc gauche |
| Clé | (706, 1104) | quille |
| Note collée | (968, 838) | flanc droit |
| Fanion rouge | de (510, 222) à ≈ (705, 286) | fanion, respiration |
| Boucle rouge | autour des deux mots du pont gauche | pont gauche |
| Ruban aux quatre coins de la feuille (36, 96, 1008×1704) | coins | image d'ensemble |
