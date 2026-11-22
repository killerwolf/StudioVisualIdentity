# Trois survols de ville (moteur wgpu, phase 0, 18/11/2026)

Essai demandé avant de trancher la suite : le moteur de la maquette tient-il sur un sujet urbain ?
**Ce ne sont ni des shorts de preuve ni une identité** ; rien ici n'est référencé par `index.json` ni par `out/shorts/`.

Paris, New York et Tokyo en vue d'oiseau, 5 s chacun. Les plans sont **inventés et seulement évocateurs** : quelques
tracés écrits à la main (fleuve, voies, parcs), le reste sort de bruits et de hachages à graine. Aucune carte, tuile,
image ni donnée géographique ; aucun logo, enseigne ni marque. Les repères sont des volumes stylisés.

| Fichier | Rôle |
|---|---|
| `villes.py` | générateur de ville partagé et rendu ; importe le moteur de `../maquette-source/maquette.py` sans le modifier |
| `plans.py` | un plan par ville : eau, parcs, voies, parcelles, hauteurs, toits, repères, caméra |
| `planche.py` | fabrique la planche |
| `sortie/paris.mp4`, `sortie/newyork.mp4`, `sortie/tokyo.mp4` | 5 s, 150 images, 1080×1920, 30 i/s, H.264 yuv420p |
| `sortie/trois-villes.mp4` | les trois à la suite, 15 s, coupes franches (`ffmpeg -f concat -c copy`) |
| `planche-villes.jpg` | 2 images par ville, le nom sous chaque paire |
| `sortie/mesures_*.json` | mesures brutes |

## Lancer

Avec l'environnement du prototype (`../.venv`, `../requirements.txt` : wgpu 0.33.0, numpy 2.4.6, pillow 13.0.0) et ffmpeg :

```bash
for v in paris newyork tokyo; do
  ../.venv/bin/python villes.py $v --out sortie/$v.mp4 --stills 1.0,3.8 --json sortie/mesures_$v.json
done
(cd sortie && ffmpeg -y -f concat -safe 0 -i enchainement.txt -c copy -movflags +faststart trois-villes.mp4)
../.venv/bin/python planche.py
```

## Comment la ville est faite

- **La ville est une carte de hauteurs** par case de 1 unité (environ 8 m), comme le relief en terrasses de la maquette.
  Les toits sont les dessus des cases, peints dans la carte ; les façades sont les contremarches, avec une trame de
  fenêtres ; les ombres portées des immeubles viennent du même balayage que celles du relief.
- **Un plan par ville** donne, par texel : eau, parcs, voies, parcelles (un hachage par parcelle), hauteur, type de
  façade et de toit. Les repères qui ne sont pas des blocs (tours en treillis, dôme, ponts, trains) sont des volumes ajoutés.
- Ajouts au shader de la maquette, faits par remplacement de texte au chargement : une trame de fenêtres (taille réglable
  par ville) et l'abandon des façades basses au loin.
- Chaque plan est composé pour sa caméra : elle regarde vers le nord, avance à 27–30 unités par seconde et ne vire que
  de 11°. C'est ce qui tient le scintillement (voir plus bas).

| Ville | Forme urbaine | Repères |
|---|---|---|
| Paris | îlots à cour et à angles coupés sur une trame par quartier, toits de zinc gris-bleu, façades crème, étoile de douze avenues plantées, fleuve en courbes avec quais, ponts et île | arc au centre de l'étoile (au premier plan), tour en treillis brune sur l'autre rive, jardin en long à son pied, dôme doré, tour sombre isolée, cathédrale sur l'île |
| New York | île étroite entre deux rivières, quadrillage d'avenues et de rues, une diagonale, tours à gradins en brique, pierre et verre, jetées, rive d'en face | grand parc rectangulaire avec réservoir, tour à gradins et mât, tour à couronne claire, aiguilles de verre, deux ponts suspendus à câbles |
| Tokyo | baie et terre-pleins rectangulaires, tissu bas, dense et irrégulier, mosaïque de toits clairs, bleus, bruns et verts, fleuve à ponts | grand faisceau de voies sur viaduc avec quatre rames, tour rouge et blanche en treillis, quartier de tours dont une à deux sommets, jardins, bois sombre |

## Mesures (rendus finaux, Radeon Pro 560, charge 1 min de 3 environ)

| | Paris | New York | Tokyo |
|---|---|---|---|
| Triangles | 2 708 368 | 2 112 940 | 2 583 062 |
| Coût par image | 26–27 ms | 24–25 ms | 26–27 ms |
| Soit pour 100 images | 2,6–2,7 s | 2,4–2,5 s | 2,6–2,7 s |
| Préparation de la ville (processeur, une fois) | 12,5 s | 5,9 s | 11,2 s |
| Deux rendus, md5 des images natives et du mp4 | identiques (`f3fce9b9…`) | identiques (`e2e14d15…`) | identiques (`a51a0127…`) |

### Scintillement, avant et après la reprise

Scintillement A-B-A ; « décodé » = sur le mp4, même calcul que pour la vidéo source (4,36 %) et la maquette du paysage (3,19 %).

| | Paris | New York | Tokyo |
|---|---|---|---|
| Avant (commit `b9268a1`), natif | 6,25 % | 4,12 % | 5,34 % |
| Avant, décodé | 6,33 % | 4,60 % | 6,79 % |
| **Après, natif** | **3,38 %** | **3,10 %** | **3,22 %** |
| **Après, décodé** | **3,37 %** | **3,39 %** | **3,89 %** |
| Pixels changés par image, décodé (avant → après) | 38,6 → 31,0 % | 28,6 → 25,6 % | 38,0 → 31,4 % |

Les trois villes sont maintenant sous la source. Ce qui a compté, mesuré sur Paris et New York :

| Essai | Scintillement natif |
|---|---|
| Paris, caméra d'origine (32 unités/s, virage de 48°) | 6,25 % |
| Paris, même vitesse, virage de 12° | 3,35 % |
| Paris, 20 unités/s, virage de 12° | 2,61 % |
| Paris, 20 unités/s, sans virage | 1,94 % |
| New York, fenêtres d'une unité, 30 unités/s | 4,70 % |
| New York, même caméra, fenêtres de 2 unités | 3,10 % |

- **Le virage est le premier facteur.** Un lacet rapide fait glisser tout l'écran, lointain compris, de 2 à 3 pixels par
  image : chaque détail fin clignote. Une ville demande une caméra qui vire peu.
- **La taille du plus petit motif est le second** : à New York, ce sont les fenêtres.
- Sans effet mesurable à Paris : retirer les filets fins des toits, les ombres et les façades au loin, réduire la carte plus tôt.
- Je n'ai donc pas eu besoin de fondre les îlots lointains en masses ni d'augmenter le nombre d'échantillons du vote.

## Avis

**Ce qui marche**
- Le moteur tient le sujet sans changer de principe, au même coût par image que le paysage.
- Les trois villes se distinguent d'un coup d'œil par leur forme et leur couleur.
- Les ombres portées des tours, les fenêtres, les nuages et leurs ombres, l'horizon en fondu passent tels quels.

**Se reconnaissent-elles sans légende ?** (mon jugement sur la planche et les mp4)
- Paris : oui. L'étoile et son arc, les avenues plantées, les îlots à cour sous le zinc et le fleuve à ponts la
  désignent ; la tour en treillis confirme mais ne porte plus seule la reconnaissance.
- New York : oui, tout de suite (île entre deux rivières, quadrillage, tours, parc, ponts suspendus).
- Tokyo : oui. La baie à terre-pleins, le viaduc et ses rames, la mosaïque de petits toits et la tour rouge et blanche
  vont ensemble ; c'est la moins immédiate des trois.

**Ce qui manque, par ville, du plus visible au moins visible**
- Paris : la cathédrale sur l'île reste au bord du cadre ; les ponts sont de simples tabliers ; le plan est inversé
  (l'étoile est du côté de la caméra, au sud dans le monde inventé) ; pas de relief.
- New York : les fenêtres de 2 unités sont grosses ; les toits des tours sont nus ; la pointe sud n'est plus à l'image.
- Tokyo : la voie rapide et la boucle ferrée se lisent mal ; le quartier de tours reste loin, dans la brume ; les
  rames sont immobiles.

**Ce que cela dit du moteur pour des sujets urbains**
- Il tient, à condition de **composer le plan pour la caméra** : virage faible, vitesse modérée, motifs d'au moins deux
  pixels. C'est une règle d'écriture de scène, pas une limite du rendu.
- Les diagonales sont en marches d'une case (8 m) : acceptable ici, visible sur les avenues en étoile de près.
- Les objets fins ou courbes (câbles, treillis, rames) s'ajoutent à la main en petits volumes alignés sur les axes.
- Un plan de ville fait 100 à 130 lignes ; le soin va aux repères et au cadrage plus qu'au tissu.

Méthode : 19 allers-retours (Paris 11, New York 4, Tokyo 4), en 35 minutes d'horloge environ, générateur compris.
