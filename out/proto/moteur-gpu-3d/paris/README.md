# Paris, passe dédiée (moteur wgpu, phase 0, 18/11/2026)

Passe demandée par la décision 49 : un survol de 5 s de la tour dans son quartier, en fin de journée, jugé à chaque tour par
un juge séparé qui compare le rendu à des photos réelles. **Ce n'est ni un short de preuve ni une identité** ; rien ici
n'est référencé par `index.json` ni par `out/shorts/`. L'ancien Paris de `../villes/` est resté tel quel (version de départ).

Tout est généré par code. Le plan est inventé et seulement évocateur : aucune carte, tuile ni donnée géographique, et
**aucune photo, ni dans le rendu ni dans le dépôt**. Les photos n'ont servi qu'à régler proportions et couleurs.

## Brief (direction artistique du propriétaire)

- Moins de bâtiments, mais plus gros et dessinés : toits mansardés en zinc (brisis sombre côté rue, terrasson clair),
  lucarnes alignées sur les travées, souches de cheminées sur les mitoyens avec leurs pots, cours en puits, angles coupés,
  pierre crème, zinc gris-bleu.
- Soleil de fin de journée, longues ombres bleu-gris froid, jamais noires ; palette plus chaude, ville claire.
- Seine, quais bas et hauts plantés, ponts lisibles ; tour fine (hauteur / base ≈ 2,6), grande arche, fût effilé.
- Caméra composée pour le plan, virage faible, motifs d'au moins 2 pixels. Pixel, trame, horizon en fondu.

## Fichiers

| Fichier | Rôle |
|---|---|
| `paris.py` | plan, peinture de la carte, tour, caméra, rendu |
| `moteur_ville.py` | copie du générateur de `../villes/villes.py` avec des options en plus : ombre réglable, toits mansardés, tons selon le soleil, murs de cour, zones sans ombre de nuage. `../villes/` n'est pas modifié |
| `mesure_decodee.py` | scintillement A-B-A sur le mp4, cadre entier ou bande de lignes |
| `mesure_ombre.py` | longueur visible de l'ombre de la tour, mesurée sur une image rendue |
| `sortie/tour1/` … `sortie/tour4/` | par tour : `paris.mp4` (5 s, 1080×1920, 30 i/s, H.264 yuv420p), 3 images à 0,5 / 2,5 / 4,5 s, `mesures.json` |

`sortie/tour4/` est la version finale. Le code du dépôt est celui du tour 4 : les tours 1 à 3 ne se re-rendent pas tels quels.

```bash
../.venv/bin/python paris.py --out sortie/tour4/paris.mp4 --stills 0.5,2.5,4.5 --json sortie/tour4/mesures.json
../.venv/bin/python mesure_decodee.py sortie/tour4/paris.mp4 maquette 380,480
../.venv/bin/python mesure_ombre.py sortie/tour4/still_4.5s.png 4.5
```

Environnement : celui du prototype (`../.venv`, `../requirements.txt` : wgpu 0.33.0, numpy 2.4.6, pillow 13.0.0) et ffmpeg.

## Références (hors dépôt, Wikimedia Commons, licences libres)

Les 12 photos de référence (Wikimedia Commons) restent hors dépôt ; leurs titres, auteurs et licences sont notés dans la copie de travail du propriétaire.

## Tours et notes des juges

Chaque tour est noté par un juge neuf, sans le contexte du constructeur. Le constructeur ne se note pas.

| Critère | Tour 1 | Tour 2 | Tour 3 | Tour 4 |
|---|---|---|---|---|
| Forme urbaine | 4 | 4 | 5 | non jugé à ce commit |
| Toits | 3 | 5 | 5 | |
| Tour | 4 | 5 | 5 | |
| Seine, quais et ponts | 3 | 4 | 5 | |
| Lumière | 4 | 4 | 4 | |
| Palette | 6 | 7 | 7 | |
| Caméra | 6 | 6 | 6 | |
| Mouvement | 6 | 6 | 7 | |
| **Global** | **4,5** | **5** | **5,5** | |
| Version de départ (`../villes/`), notée par le même juge | 2,5 | 2,5 | 3 | |

Verdict du juge au tour 3 : pas encore publiable ; l'écart principal est la lumière.

Ce qui a changé à chaque tour :

- **Tour 1** : échelle doublée (1 unité ≈ 4 m), îlots construits un par un (parcelles, angles coupés, cours, souches),
  façade + brisis à lucarnes, soleil bas, tour refaite, Champ-de-Mars, Seine et quais, caméra au-dessus des îlots.
- **Tour 2** : brisis réduit à un filet, terrasson à pans, souches longues et basses, lucarnes en volume ; tour à piles
  ajourées et grande arche ; caméra plus haute pour montrer la Seine ; rues élargies ; soleil à 15°.
- **Tour 3** : soleil au sud, caméra au sud-ouest ; tour affinée, deux plateaux ; cours plus grandes à murs sombres, pans
  coupés plus grands, avenues obliques ; ponts en volume sur piles ; pots séparés.
- **Tour 4** : soleil à 12° dans l'axe du Champ-de-Mars et derrière la caméra, qui regarde depuis la rive d'en face :
  l'ombre de la tour file sur les pelouses ; tons des façades calculés selon le soleil, pierre plus orangée ; ciel de
  couchant en dégradé ; tour pincée, premier étage mince, piles plus ajourées ; reflets en traits sur l'eau ; silhouettes
  lointaines (tour sombre, dôme doré).

## L'ombre de la tour : ce qui n'allait pas

Aux tours 2 et 3, l'ombre était calculée et dans le cadre, mais elle ne se lisait pas comme une ombre de tour.
Mesure sur les images du tour 3 (`mesure_ombre.py`) : l'axe de l'ombre est entièrement dans le cadre, avec 2,0 à 2,2 hauteurs
de tour de points plus sombres que leurs témoins, mais le plus long tronçon continu ne fait que 0,9 hauteur. Causes :

- elle est coupée en morceaux par les arbres des quais, le pont et les changements de sol ;
- sa partie large tombe sur l'eau sombre, où elle contraste peu ;
- vue du sud-ouest, elle part presque dans le prolongement de la tour, derrière sa silhouette.

Le balayage d'ombre lui-même n'était pas en cause : la tour projette son ombre par un volume plein invisible (son profil),
pas par ses piles ajourées. Au tour 4, l'ombre tombe sur un seul sol dégagé, le Champ-de-Mars, de biais par rapport à la vue.
Mesure sur les images du tour 4 : 3,0 à 3,6 hauteurs de tour de points plus sombres que leurs témoins (ombre théorique :
4,7 hauteurs à 12°), plus long tronçon continu de 0,9 à 1,7 hauteur. Le détecteur compare chaque point à deux témoins à
±18 unités ; là où les témoins sont eux-mêmes à l'ombre ou dans les arbres, il sous-compte.

## Mesures (tour 4)

| Mesure | Valeur |
|---|---|
| Scintillement A-B-A, fichier décodé, cadre entier | 1,24 % (tour 1 : 1,82 % ; tour 2 : 1,48 % ; tour 3 : 1,30 %) |
| Bande du bas (lignes natives 380 à 480) | 2,16 % (tour 3 : 2,45 %) |
| Bande d'horizon (lignes natives 60 à 180) | 1,39 % (tour 3 : 0,76 %) |
| Scintillement A-B-A natif | 1,07 % en moyenne, 1,38 % au pire |
| Pixels changés par image, décodé | 14,4 % |
| Coût par image | 67 à 80 ms (machine chargée par une autre session ; non mesuré au calme) |
| Préparation, une fois | 8,6 s pour la ville, 3,9 s pour les shaders |
| Triangles | 2 159 470 |
| Déterminisme | deux rendus identiques : md5 des images natives `982e7298…`, md5 du mp4 `7e494f1e…` |

La bande d'horizon scintille plus qu'au tour 3 : elle contient maintenant de la ville lointaine au lieu de brume.

## Ce qui n'a pas été fait

- La trame des rangées d'arbres fixée au monde : les houppiers ont seulement été simplifiés.
- Des arches en courbe sous les ponts : il y a des piles avec un départ d'arche, pas d'arc.
- Un liseré orangé distinct sur les arêtes : les faces au soleil sont réchauffées en entier.
- Les détails fins (souches, pots, lucarnes) n'existent que près du trajet de la caméra.
