# Recette — short `geographie` en Trait continu

Référence : `out/shorts/trait-continu__geographie__l-italie-a-la-forme-d-une-botte/` (shapely + opensimplex + pycairo, 16 s, 30 i/s, graine 11, rendu 21,5 s).

Pour un short **géographie** (enfants et parents) dans cette identité :

- **Ouvrir par (0–1 s)** : une question d'enfant sur une forme (« L'Italie, une botte ? ») dans la bande orange dès t = 0 ; sur la plaque 1, le trait dessine **l'objet familier** que la forme rappelle (une botte générique inclinée comme la péninsule, 2 700 px à 850 px/s, ≈ 3,2 s).
- **Avance plaque** à ≈ 3,8 s (0,8 s), titre « Suis le trait ».
- **Plaque 2 : le pays d'un seul trait** (≈ 4 100 px à 900 px/s) :
  - contour **tracé à la main** en lon/lat (40–80 points, ≈ 0,1° près), projection équirectangulaire (cos de la latitude moyenne, ≈ 76 px/degré pour 10° de latitude), réduit par `shapely.simplify` (1,2 px) ; c'est un choix de style, le trait simplifie ;
  - ordre du tracé choisi pour la narration : partir d'un point qui permet de finir sur l'image forte (ici : pointe → côte ouest → Alpes → Adriatique → **talon** → golfe → **pointe** → Sicile) ;
  - 2 **arrêts sur repère** de 1,7–1,9 s : point bleu + anneau, étiquette crème (Fredoka 600, 56–60 px) placée à la main dans la mer, fil de repère bleu si l'étiquette est loin du point ; titre de 2 mots par arrêt (« Le talon », « La pointe ») ;
  - les îles sont reliées par un **pont calculé** (`nearest_points` + `bridge_ring`) : le pont fait partie du dessin et peut porter le sens (« le coup de pied »).
- **Fermer par** : l'image finale (« Et le ballon ? » + étiquette « Sicile »), carte complète tenue ≥ 3 s, `chime`.
- **Voix** (Arnold) : 5 lignes, 30 mots, 2,0–2,2 mots/s ; chaque ligne démarre à l'arrêt du traceur (lire les temps avec `video.py --info`).
- **Faits** : ne nommer que des repères vérifiés (talon = Pouilles, pointe = Calabre) ; l'image du ballon est une image d'école, pas une affirmation.
- **Tokens** : `out/identities/trait-continu/tokens.json` ; pipeline : `src/README.md`.
