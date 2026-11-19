# Premières combinaisons à essayer (2026-11-19)

Modèle : [`proposition.md`](proposition.md) ; habillages, mécaniques et niveaux : [`inventaire.md`](inventaire.md).
États : **testé** (un short existe), **compatible** (un adaptateur existe et une image fixe est rendue), **à tester** (les
besoins de la mécanique sont remplis sur le papier, pas d'adaptateur), **incompatible** (une contrainte est violée).

## 1. Ce qui est déjà prouvé

26 cases **testées**, une par recette. Seules deux mécaniques en ont plusieurs :

| Mécanique | Habillages testés | Shorts |
|---|---|---|
| `trace-chemin` | `plan-bleu`, `editeur`, `ardoise`, `portulan` | `lyrics-chemin__paroles__claudes-plan`, `…__paroles__claudes-plan-tech`, `…__explicatif__le-quatre-quarts`, `…__histoire__le-premier-tour-du-monde` |
| `pop-papier-12ips` | `papier-decoupe`, `atelier-papier`, `carnet-archives`, `cabinet-curiosites` | 2 épisodes × 4 thèmes (`<id>__explicatif__d-ou-vient-le-mot-sandwich`, `<id>__histoire__la-fourchette-a-fait-scandale`) |

Aucun habillage n'a encore été porté sur une deuxième mécanique : c'est ce qui manque pour juger la règle de
reconnaissance (« l'habillage reste reconnaissable d'une mécanique à l'autre »).

## 2. Mesures gratuites, avec les shorts qui existent

Aucun rendu, seulement `recognition.py` (étape 5 de `migration.md`) sur des vidéos qui sont déjà là.

| # | Question | Shorts | Ce qu'on apprend |
|---|---|---|---|
| M1 | Le descripteur de mécanique reconnaît-il `trace-chemin` sous 4 habillages et `pop-papier-12ips` sous 4 habillages ? | les 4 shorts du chemin, les 8 shorts papier | si le nouveau descripteur temporel marche : chaque short doit avoir pour voisin « mécanique » un short de la même mécanique, d'un autre habillage |
| M2 | `survol-terrain` est-elle vraiment une seule mécanique ? | `topo-relief` (2) et `survol-pixel` (2) | si leurs 4 shorts sont voisins en mécanique, on la garde commune ; sinon deux mécaniques |
| M3 | Même sujet, habillages voisins, mécaniques différentes | `atlas-grave__histoire__premier-tour-du-monde-1519-1522` et `lyrics-chemin__histoire__le-premier-tour-du-monde` | `gravure-parchemin` et `portulan` sont-ils un doublon d'habillage (voisins en apparence) ? Les mécaniques doivent les séparer |

## 3. Combinaisons à rendre (5 à 8)

Classées de la moins chère à la plus chère. « Coût » = travail avant le premier short, voix non comprise.

| # | Habillage × Mécanique × Format | État aujourd'hui | Pourquoi l'essayer | Ce qu'il faut écrire | Coût |
|---|---|---|---|---|---|
| C1 | `craie-verte` (tableau-craie) × `trace-chemin` × `narre-long` | à tester | **doublon probable** avec `ardoise` (déjà testé) : si les deux images sont indiscernables, on fusionne les deux habillages (un parent `craie`, deux tons) | un adaptateur `habillages/craie-verte.js` dérivé d'`ardoise.js` (couleurs, Caveat/Nunito, rebord en bois) ; réutiliser le dessin `quatre-quarts` et sa voix | 0,5 session |
| C2 | `grille-suisse` (swiss-data) × `trace-chemin` × `narre-court` | à tester | **premier habillage porté sur une 2ᵉ mécanique** : un chiffre écrit le long d'une barre qui devient le graphique final. Teste la règle de reconnaissance (le short doit rester voisin des 2 shorts swiss-data en apparence) | adaptateur `habillages/grille-suisse.js` depuis l'objet `T` de `grille.js` (FACILE) ; un dessin en barres (arêtes droites, primitive `final`) ; reprendre le texte et la voix de `swiss-data__geographie__ou-vivent-8-milliards` | 1 session |
| C3 | `carnet-archives` (papier) × `trace-chemin` × `narre-long` | à tester | porter un habillage **d'un moteur Python vers un moteur JS** : le kraft et la machine à écrire comme surface du chemin. Teste que `habillage.json` neutre suffit à écrire l'adaptateur | adaptateur JS ; fibres du kraft réécrites en canvas (`noiseTile`) ; dessin libre (ex. un dossier ou un tampon) | 1 session |
| C4 | `plan-bleu` × `pop-papier-12ips` × `narre-court` | à tester | l'inverse de C3 : **un habillage du chemin dans le moteur papier**, par un simple `themes/plan-bleu.json`. Le moins cher de tous si le moteur accepte la feuille bleue comme `tapis` | un thème JSON (`tapis`, `couleurs`, `polices` Barlow Condensed) ; peut-être une 4ᵉ branche de `tapis()` (feuille bleue pliée) ; ré-rendre l'épisode « sandwich » tel quel | 0,5 session |
| C5 | `grille-suisse` × `pop-papier-12ips` × `narre-court` | à tester | la grille suisse **en stop-motion à 12 i/s** : la pâte survit-elle à un mouvement qui la contredit (nette et rapide contre papier qui saute) ? Contrôle aussi la contrainte `cadence` | un thème JSON ; tapis uni crème avec grille 12 colonnes | 0,5 session |
| C6 | `brut-jaune` (brut-meme) × `colonne-mot-a-mot` × `paroles-muet` | **incompatible** tel quel | Anton n'a pas d'axe `wdth`, exigé par la colonne justifiée. Exemple d'incompatibilité **réparable** : garder la palette noir/jaune/rouge et prendre une police à axe de largeur proche (Anybody est déjà là). Les deux recettes sont déjà notées `confusableWith` : vérifier que la mécanique les sépare | sortir `CAMAIEUX` dans un habillage (étape 8.4) ; un ton `brut` | 1 session |
| C7 | `portulan` × `survol-terrain` (moteur `survol.py`) | **incompatible** | `pixel-jour` impose la grille 270×480 indexée : un parchemin anticrénelé ne passe pas. Le garder dans la matrice comme exemple de case `incompatible` avec sa raison écrite ; l'inverse (`relief-vert` sur `survol.py`) est la vraie question de M2 | rien | — |
| C8 | `pixel-jour` (survol-pixel) × `simulation-deterministe` (pixel-arcade) × `narre-court` | à tester | les deux partagent la grille 270×480 ×4 ; une course de billes en plein jour, palette indexée, dans la lumière du survol. Teste si `pixel-16` doit devenir un habillage parent commun | habillage `pixel-jour` exprimé pour p5/Matter (palette indexée → couleurs fixes) ; une des 3 simulations existantes | 1 à 1,5 session |

**Premier lot conseillé : C1, C2 et C4.** C1 tranche un doublon, C2 donne le premier vrai test de reconnaissance d'un
habillage entre deux mécaniques, C4 est le moins cher (un fichier JSON sur un moteur qui sait déjà changer de thème). Les
trois réutilisent un texte et une voix existants, donc aucun appel de voix.

Aucun de ces essais n'est lancé : ils attendent la validation d'Hamdi et au moins les étapes 0 et 1 de `migration.md`.
