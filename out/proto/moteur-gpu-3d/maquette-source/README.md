# Maquette « qualité source » (moteur wgpu, phase 0, 18/11/2026)

Seconde maquette du prototype, après la décision 47 : même moteur wgpu que `../proto.py`, scène riche et éclairée.
**Ce n'est ni un short de preuve ni une identité** ; rien ici n'est référencé par `index.json` ni par `out/shorts/`.

Le monde est inventé : une côte (mer à l'ouest, plaine en terrasses, bois, rivière, lac, montagnes enneigées à l'est),
survolée par une caméra qui avance et vire vers l'intérieur des terres. On copie une forme (pixel art survolé), pas la
vidéo source : ni avion, ni archipel, ni interface, ni sprite, ni texte.

| Fichier | Rôle |
|---|---|
| `maquette.py` | monde, carte peinte, maillage, shaders, rendu vers ffmpeg |
| `planche.py` | fabrique la planche de comparaison (la vidéo source reste hors dépôt) |
| `mesure_decodee.py` | scintillement A-B-A sur fichier décodé, même calcul pour la source et pour la maquette |
| `sortie/maquette.mp4` | 5 s, 150 images, 1080×1920, 30 i/s, H.264 yuv420p, 5,7 Mo |
| `sortie/still_*.png` | 5 images du même rendu |
| `planche-source-maquette.jpg` | 5 instants source / maquette, vue entière et crop à 100 % |
| `sortie/mesures_*.json` | mesures brutes : 2 rendus Radeon, 1 rendu Intel |

## Lancer

Avec l'environnement du prototype (`../.venv`, `../requirements.txt` : wgpu 0.33.0, numpy 2.4.6, pillow 13.0.0) et ffmpeg :

```bash
../.venv/bin/python maquette.py --out sortie/maquette.mp4 --stills 0.5,1.5,2.5,3.5,4.5 --json sortie/mesures_radeon_1.json
../.venv/bin/python maquette.py --frames 0,75,149 --out /tmp/essai/x.mp4      # images isolées, sans vidéo
../.venv/bin/python planche.py /chemin/vers/source_1080.mp4
../.venv/bin/python mesure_decodee.py sortie/maquette.mp4 maquette
../.venv/bin/python mesure_decodee.py /chemin/vers/source_1080.mp4 source
```

## Ce que fait le moteur

- **Processeur, une fois (7,4 s)** : relief en terrasses ; carte peinte du sol à 2 texels par unité. Chaque texel porte
  un ton A, un ton B et la part de B en seizièmes : prés en 4 verts avec la lumière du soleil sur les pentes, roche,
  neige, bandes de profondeur de la mer, franges de sable et d'écume. S'y ajoutent les lignes de niveau, les ombres
  portées du relief et des arbres, les réductions de la carte par vote majoritaire, 10 320 arbres et 300 nuages en
  volumes, 34 000 traits d'écume, le masque d'ombre des nuages et les tables d'ombre et de brume.
- **Carte graphique, par image** : 2 622 030 triangles, un indice de palette par fragment, jamais de couleur flottante.
  - **Trame** : le choix entre A et B se fait par une matrice de Bayer posée sur les pixels natifs. Il y a de la trame
    partout, et aucun texel isolé qui scintille.
  - **Nuages** : des tas de boules empilées, chaque boule étant une sphère à facettes ; le ton de chaque facette vient
    du soleil et de sa hauteur dans le tas (le bas est sombre). L'ombre au sol est décalée selon le soleil.
  - **Écume** : chaque trait est un petit zigzag posé sur l'eau, orienté dans le monde ; le shader l'élargit avec la
    distance pour qu'il ne soit jamais plus fin qu'un pixel natif. Il bat à 2 Hz.
  - Ombre des nuages par table, brume en 6 paliers tramés, vote majoritaire 4×4.
- **Processeur, par image** : ciel en 5 paliers tramés, palette (151 couleurs, 76 à 119 par image), tuyau vers ffmpeg.

## Mesures (rendu final, charge 1 min de 4 environ)

| Mesure | Valeur |
|---|---|
| Coût, Radeon | **2,5–2,9 s pour 100 images**, soit 25–29 ms par image (dont 18 ms de carte graphique et de relecture) |
| Coût, Intel HD 630 | 4,0 s pour 100 images |
| Préparation, une fois par rendu | monde et maillage 7,4 s ; shaders 3,1 s |
| Deux rendus sur la Radeon | **identiques** : md5 des images natives `c2e23833…`, md5 du mp4 `ef8108b2…` |
| Radeon contre Intel | 7 233 pixels différents sur 19 440 000 (0,04 %) ; au pire 0,11 % d'une image |
| Scintillement A-B-A natif | 3,02 % en moyenne (4,38 % au pire) ; 4,45 % au début du travail |
| Scintillement A-B-A sur fichier décodé, même calcul | **maquette 3,19 % ; source 4,36 %** |
| Pixels qui changent d'une image à l'autre, fichier décodé | maquette 22,4 % ; source 27,7 % |

Sous une forte charge de la machine (14 à 30), les rendus de la première version prenaient 3,8–4,8 s pour 100 images.

## Avis : où en est la maquette face à la source

Je la juge au niveau de la source pour la qualité du rendu ; la planche permet d'en juger à 100 %.

Au niveau de la source :
- la mer : bandes de profondeur tramées, hauts-fonds, frange d'écume, traits d'écume fins jusqu'au loin, ombres des nuages ;
- les nuages : tas de boules modelés en blanc et lavande, avec leur ombre décalée ;
- l'horizon en fondu, les montagnes enneigées lisibles dans la brume ;
- la terre : terrasses, lignes de niveau, trame dans les prés, bois en houppiers distincts sur fond sombre ;
- le scintillement : en dessous de celui de la source, par le même calcul.

Ce qui reste différent, du plus visible au moins visible :
1. **Les nuages vus de près et du côté du soleil** restent presque blancs ; ceux de la source ont des étages en anneaux
   concentriques bien dessinés.
2. **Les prés** sont en dégradés tramés ; ceux de la source sont en aplats nets avec un semis de points. C'est un choix
   de dessin plus qu'un manque.
3. **Les terrasses lointaines** font des rayures sombres assez lourdes.
4. **Le mouvement** : 22 % de pixels changés par image contre 28 % ; la caméra peut voler plus vite.
5. **L'écart entre cartes graphiques** (0,04 %) : sans effet visible, mais le md5 ne vaut que pour une carte.

Pour aller plus loin : étages de nuages en anneaux (ton par altitude plutôt que par facette), terrasses par courbes de
niveau, canopée fusionnée au loin, puis un vrai sujet avec cartouches et plan de coupe.

Méthode : 14 allers-retours « je rends, je regarde, je corrige » (9 pour la première version, 5 pour la seconde), en
30 minutes d'horloge environ. Trois d'entre eux ont été guidés par une mesure du scintillement par paire de couleurs.
