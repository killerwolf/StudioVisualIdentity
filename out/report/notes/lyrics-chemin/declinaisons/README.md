# Lyrics chemin — déclinaisons (2026-11-19)

Statut : **propositions de direction artistique**, à réaliser par un agent ensuite. Rien n'est rendu en vidéo, aucune voix n'est générée.
L'identité `lyrics-chemin` ne change pas : le texte s'écrit à plat sur une surface au moment où il est dit, la caméra vue de dessus suit
la pointe en plan-séquence, un zoom arrière final révèle le dessin formé par le texte. Ce dossier ajoute :

| | Document | Sujet | Habillage (surface) | Dessin final | Durée | Son |
|---|---|---|---|---|---|---|
| A1 | [`a1-tour-du-monde.md`](a1-tour-du-monde.md) | Histoire : Magellan–Elcano, 1519–1522 | `portulan` : carte marine à l'encre sur parchemin, table en noyer | la route complète, **boucle fermée** autour du pôle Sud | 41 s | voix off |
| A2 | [`a2-quatre-quarts.md`](a2-quatre-quarts.md) | Recette : le quatre-quarts | `ardoise` : craie sur ardoise de bistrot, plan de travail en marbre | le **gâteau vu de dessus, coupé en quatre parts égales** | 30 s | voix off |
| B | [`b-claudes-plan-tech.md`](b-claudes-plan-tech.md) | Paroles : « Claude's Plan », version tech | `editeur` : éditeur de code sombre sur un écran vertical, clavier, canette | un **porte-conteneurs** : chaque ligne est un conteneur (*ship*) | 32,6 s | chanson (muet) |

Planche des trois images finales : `images/planche-images-finales.jpg`.

## Ce qui reste commun (la signature, à ne pas toucher)

- Un seul plan-séquence, caméra verticale sans perspective (translation, rotation, échelle), point de lecture (512, 860).
- **Une couleur d'encre fraîche réservée au mot dit ou chanté**, qui sèche en 0,35 s ; encre sèche atténuée à 60 % en gros plan.
- Mots posés **entiers et rigides** sur le trait ; une ligne de texte = un trait du dessin ; pré-pose des passages rapides.
- Objets posés dessinés par code, seuls à avoir une ombre, **aucun mot dessus** ; annotations dans une seconde couleur, jamais du texte.
- Zoom arrière une seule fois, à la fin ; image d'ensemble tenue ≥ 1,5 s, le dernier mot encore « frais » ; pas de noir.
- Zones sûres : haut 220, bas 320, droite 120, gauche 64 ; mot dit dans x 64–960, y 220–1600.

## Ce qui change : un « habillage » et un « dessin » par épisode

Aujourd'hui `out/shared/chemin-moteur/chemin.js` porte en dur le plan bleu (couleurs, polices, feuille, objets). Le travail de fond est de
séparer trois choses, et **seulement** ça :

1. **Habillage** (`out/shared/chemin-moteur/habillages/<id>.js`, nouveau) : tout ce qui est matière. Interface montrée par la maquette
   (`proto/core.js` appelle ces fonctions, `proto/magellan.js`, `quatre-quarts.js`, `cargo.js` les fournissent) :

   | Champ | Rôle |
   |---|---|
   | `fonts`, `font`, `weight`, `wFinal`, `cap`, `gap`, `em`, `trackMax`, `gapW`, `floorPx` | police, graisses, hauteur de capitale, écart au trait, bornes de corps dans le monde, interlettrage max, espace ajouté entre mots, plancher de corps à l'écran |
   | `col.dry`, `col.fresh`, `col.ghost`, `col.stroke`, `dryColor(unité)` | encre sèche, encre fraîche, pré-posé, trait ; couleur sèche par unité (coloration syntaxique) |
   | `ghostStyle`, `ghostWeight`, `ghostAlpha` | aspect du pré-posé (crayon, craie pâle, suggestion en italique) |
   | `floor()`, `sheet()` | sol et feuille (textures attachées au monde, plis, quadrillage) |
   | `under()`, `stroke()`, `inkExtras()` | décor du dessin sous le texte, tracé d'une arête, annotations |
   | `textErode()` | grain appliqué au calque d'encre (craie) |
   | `objects()`, `tip()` | objets posés et pointe (point d'encre, bâton de craie, curseur bloc) |
   | `finish()` | vignette et grain d'écran |

   Premier habillage à écrire : `plan-bleu`, **extraction à l'identique** de l'existant (contrôle : les 5 images de
   `out/report/notes/lyrics-chemin/images/` doivent ressortir au pixel près). Les trois autres viennent ensuite.
2. **Dessin** (`out/shared/chemin-moteur/dessins/<id>.json`) : sommets, arêtes, objets. Trois ajouts au format :
   - arête de type **`courbe`** (liste de points lissés) avec deux règles de pose : *flèche* (le mot rigide est décollé du trait de la
     flèche de l'arc sous lui) et `gapW` (espace ajouté entre mots, qui se referment du côté concave) — nécessaire à A1 ;
   - **`route` continue** : la pointe ne saute jamais, elle trace le trajet « muet » entre deux textes (A1) ;
   - primitives de décor liées à une arête : **`boites`** (conteneurs, B), **`cercle`** (moule, A2) ; la « mer » devient `final`
     (rangs de fin, alignés au centre ou à gauche).
3. **Fichier de l'épisode** (`paroles.*.json` ou `narration-chemin.json`) : ajoute `habillage`, garde `dessin` ; une unité peut porter une
   4ᵉ valeur, sa **classe** (`kw`, `str`, `num`), lue par `dryColor`. Pour un short narré : pas de `bpm` ; les transitions se donnent en
   secondes (`duree`) au lieu de temps (`temps`).

Rien d'autre ne bouge : mise en page des mots, règles de pré-pose, caméra, flou de mouvement, audit.
`out/tools/chemin_audit.mjs` doit recevoir le plancher de corps de l'habillage (`floorPx`) au lieu de 120 en dur.

## Short narré : la voix d'abord

Même chaîne que pour une chanson, la voix remplace le morceau :

1. Écrire le texte (dans chaque document), le faire dire **d'un seul tenant** par la voix choisie (ElevenLabs, par l'agent suivant ;
   écrire les nombres en toutes lettres dans le texte envoyé, voir chaque document).
2. Horodater les mots de l'audio obtenu (faster-whisper puis correction à l'oreille, ou les horodatages de l'API si elle les donne) ;
   `out/tools/lyrics_align.py` prépare les unités.
3. Remplacer les **temps estimés** de ce dossier par les temps mesurés (les temps d'ici supposent ≈ 4,6 syllabes/s et des pauses de
   0,5 s : ils servent à dimensionner, pas à caler).
4. Rendre l'image, puis poser la voix (et un lit sonore très discret, voir chaque document) ; `check.py`.
   La vidéo d'un short narré **porte son audio** (à la différence d'une vidéo de paroles, publiée muette).
5. Écrire `narration.json` (lignes horodatées) pour les sous-titres éventuels et pour `check.py`.

Débit visé : 2,4 à 2,7 mots/s. Jamais plus de deux ou trois mots dits à l'écran à la fois ; ce qui s'écrit au sol est un **mot clé ou une
phrase courte** de ce qui est dit (jamais un mot que la voix ne prononce pas, abréviations de date admises).

## Maquette et images

`proto/` est une **maquette d'images fixes** (pas de transitions, pas de flou, pas d'audit) : elle prouve le look, la mise en page et les
cadrages au repos. Ce n'est pas le moteur.

```bash
# depuis la racine du dépôt ; node 22 ou 24 (nvm), playwright-core déjà dans node_modules
export SVI_CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
node out/tools/render.mjs out/report/notes/lyrics-chemin/declinaisons/proto/scene.html --query d=magellan --stills 0.9,5.9,40.9 --stills-dir /tmp/x --no-slot
#   d=magellan | quatre-quarts | cargo ; &guides=1 : zone sûre ; &cam=x,y,zoom,angle : cadrage forcé
node out/report/notes/lyrics-chemin/declinaisons/proto/dump.mjs magellan   # corps, interlettrages, cadrages calculés (storyboard-*.json)
```

| Image | Temps | Ce qu'elle montre |
|---|---|---|
| `images/a1-01-ouverture-0.90s.jpg` | 0,9 s | accroche : la date s'écrit au vermillon, côte et lignes de rhumb |
| `images/a1-02-cinq-navires-3.80s.jpg` | 3,8 s | annotation au bleu de Prusse : cinq navires le long du trait |
| `images/a1-03-image-cle-magellan-5.90s.jpg` | 5,9 s | **image clé** : « MAGELLAN » le long de l'Amérique du Sud |
| `images/a1-04-ocean-immense-18.75s.jpg` | 18,75 s | le vide du Pacifique |
| `images/a1-05-est-tue-23.70s.jpg` | 23,7 s | croix accrochée au mot |
| `images/a1-06-image-finale-40.90s.jpg` | 40,9 s | **image finale** : la boucle fermée |
| `images/a2-01-ouverture-0.90s.jpg` | 0,9 s | accroche : le titre à la craie, œufs et fouet |
| `images/a2-02-sucre-10.20s.jpg` | 10,2 s | un ingrédient dans sa part, bâton de craie |
| `images/a2-03-image-cle-coupe-17.90s.jpg` | 17,9 s | **image clé** : texte sur la coupe, caméra tournée de 40° |
| `images/a2-04-image-finale-29.90s.jpg` | 29,9 s | **image finale** : le gâteau en quatre parts |
| `images/b-01-suggestion-fantome-4.30s.jpg` | 4,3 s | **image clé** : mot chanté en jaune, suite en « suggestion » italique, curseur bloc |
| `images/b-02-flanc-echec-14.50s.jpg` | 14,5 s | **image clé** : flanc de la coque, caméra tournée de 61°, ✗ et notification |
| `images/b-03-image-finale-32.50s.jpg` | 32,5 s | **image finale** : le porte-conteneurs dans l'éditeur, clavier et canette |

Les images de B montrent le **jeu de remplissage** (« Monday's draft »). Les mêmes images avec les vraies paroles sont hors dépôt :
`~/git/StudioVisualIdentity-sources/lyrics-claudes-plan/stills-tech/` (données : `cargo.paroles.reelles.json` au même endroit, lu par
un lien symbolique dans `proto/tmp/`, ignoré par git).

## Ordre de travail conseillé

1. Extraire l'habillage `plan-bleu` du moteur, sans changement d'image (contrôle au pixel).
2. **B d'abord** (aucune voix à produire, temps déjà connus) : habillage `editeur`, dessin `cargo`, audit, 10 premières secondes en vidéo,
   puis rendu complet, version aux vraies paroles hors dépôt.
3. A2 (arêtes droites seulement, moteur presque inchangé) : voix, horodatage, habillage `ardoise`, dessin `quatre-quarts`.
4. A1 en dernier (arête `courbe`, route continue : le plus de moteur) : voix, horodatage, habillage `portulan`, dessin `tour-du-monde`.

## Ce qui reste incertain (commun)

- **Aucun mouvement n'a été vu** : les trois propositions ne sont jugées que sur des images fixes au repos.
- **Temps de A1 et A2 estimés**, sans voix : les cadrages tiennent sur le papier (≥ 0,5 s chacun), à revérifier à l'audit une fois la
  voix horodatée.
- **Voisinage** : `ardoise` ressemble par la matière à l'identité existante `tableau-craie`, `portulan` à `atlas-grave` / `topo-relief` /
  `carnet-archives`. La mécanique (texte-chemin, caméra de dessus, révélation) les distingue ; aucun test de reconnaissance fait.
- **Corps dans l'image finale** : 29–54 px pour les lignes du dessin (règle du dépôt : 54 px). Comme pour l'identité : voulu, ces lignes
  ont été lues en gros plan ; seuls les rangs finaux (68–100 px) sont faits pour être lus à l'échelle 1.
- **Lit sonore** des shorts narrés : proposé, pas essayé.
