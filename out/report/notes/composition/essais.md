# Essais C1, C2, C4 : verdicts (2026-11-19)

Décision d'Hamdi : choix 118 (modèle + version minimale + essais C1, C2, C4). Combinaisons décrites dans
[`matrice.md`](matrice.md) ; recettes d'essai dans `out/recettes/chemin-craie-verte.json`, `chemin-grille-suisse.json`,
`papier-plan-bleu.json`. Aucune nouvelle voix : les trois shorts réutilisent une voix qui existait. Aucun moteur partagé
modifié : deux habillages neufs dans `out/shared/chemin-moteur/habillages/` (`craie-verte.js`, `grille-suisse.js`), un dessin
neuf (`dessins/barres-humains.json`), et pour C4 un thème et un fond rangés dans le dossier du short.

Jugement à l'œil (le mien, sur les planches et les comparaisons ci-dessous), **pas mesuré** : `recognition.py` n'a pas été
relancé (il réécrit `recognition.json` et ne sait pas encore séparer habillage et mécanique, étape 5 de `migration.md`).

| Essai | Short | Rendu | `check.py` | Planche | Comparaison |
|---|---|---|---|---|---|
| C1 craie-verte × trace-chemin × narré long | `out/shorts/chemin-craie-verte__explicatif__le-quatre-quarts/short.mp4` (25,6 s) | 779,7 s, 101,5 s / 100 images | OK, 0 avertissement | [`essais/C1-planche.jpg`](essais/C1-planche.jpg) | [`essais/C1-comparaison.jpg`](essais/C1-comparaison.jpg) : ardoise / C1 / tableau-craie aux mêmes instants |
| C2 grille-suisse × trace-chemin × narré court | `out/shorts/chemin-grille-suisse__geographie__ou-vivent-8-milliards/short.mp4` (15 s) | 124,4 s, 27,7 s / 100 images | OK, 0 avertissement | [`essais/C2-planche.jpg`](essais/C2-planche.jpg) | [`essais/C2-comparaison.jpg`](essais/C2-comparaison.jpg) : swiss-data 8 milliards / C2 / swiss-data éclipse / bauhaus |
| C4 plan-bleu × pop-papier-12ips × narré court | `out/shorts/papier-plan-bleu__explicatif__d-ou-vient-le-mot-sandwich/short.mp4` (12,2 s) | 15 s (4 tranches) | OK, 1 avertissement (image figée ≥ 3 s à 3,2 s, comme l'épisode d'origine) | [`essais/C4-planche.jpg`](essais/C4-planche.jpg) | [`essais/C4-comparaison.jpg`](essais/C4-comparaison.jpg) : papier-decoupe / C4 / lyrics-chemin (plan bleu) |

Les `chemin_audit.mjs` de C1 et C2 disent « aucune » erreur.

## C1 — Craie verte sur le chemin : distinct de l'ardoise, mais de la même famille

- **Reconnaissable ?** Oui, comme Tableau Craie : tableau vert pleine image, craie orange pour le mot dit et bleue pour les
  annotations, écriture manuscrite Caveat en minuscules, rebord en bois avec trois bâtons de craie et une brosse. Le décor du
  dessin (œufs, fouet, cuillère, beurre) est dessiné à la craie au lieu d'être des objets réels.
- **Doublon de l'ardoise ?** Pas à l'image : sur la comparaison, aux mêmes instants, on distingue toujours les deux (vert et
  minuscules manuscrites contre noir et majuscules étroites ; craie dessinée contre objets ; tableau pleine image contre ardoise
  encadrée sur du marbre). Mais c'est la **même matière** (craie érodée par le même grain, même dessin, même mise en page) en
  deux tons, et le code de C1 est dérivé à 80 % de `ardoise.js`. Recommandation : **un habillage parent `craie` avec deux tons**
  (`ardoise` = bistrot, adultes ; `craie-verte` = école, enfants), pas deux marques distinctes sur la même mécanique.
- **Qu'apporte-t-il ?** À Tableau Craie, un mouvement qu'il n'avait pas : une caméra qui suit la craie en un plan et un zoom
  arrière qui révèle la recette entière. Face à l'ardoise, seulement un autre ton.
- **Limites** : une seule police (le moteur n'en prend qu'une : Caveat partout, Nunito absent des titres) ; le moteur ne connaît
  pas le chiffon de Tableau Craie (c'est sa mécanique, pas sa pâte). Le texte au sol est passé en minuscules : c'est du
  contenu, pas l'habillage.

## C2 — Grille suisse sur le chemin : oui, l'habillage survit au changement de mécanique

- **Reconnaissable ?** Oui, nettement : crème chaud, 12 colonnes visibles, Archivo Black, rouge / noir / bleu et rien d'autre,
  filets de section « 01 · MONDE » / « ONU · 2024 ». Sur la comparaison, les images de C2 se rangent avec les deux shorts
  swiss-data et pas avec bauhaus (son voisin `confusableWith`).
- **Différent de l'existant ?** Oui : swiss-data montre un écran par chiffre, séparés par des volets rouges ; C2 suit l'écriture
  en un seul plan, chaque chiffre remplit sa barre, et le zoom arrière montre que la page entière était un graphique, à la
  même échelle (Asie 4,72 Md, Afrique 1,44, Inde 1,45, Chine 1,41). C'est **le premier habillage prouvé sur deux
  mécaniques**, ce que la règle de reconnaissance (proposition § 8) attendait.
- **Faiblesses** : l'image d'ouverture est trop vide (le titre au corps minimal dans une page encore blanche) ; « 1 carré =
  100 millions » n'a plus de sens sans les carrés de l'unit chart d'origine (le texte de la voix a été gardé tel quel) ; les
  filets de la grille deviennent des bandes grises floues en gros plan.

## C4 — Plan bleu dans le moteur papier : ça marche, mais on voit surtout du papier découpé

- **Faisable ?** Oui, et c'est le moins cher : un thème JSON, un fond (`tapis_plan()`) et 15 s de rendu, sans toucher au
  moteur ni à `out/shared/papier-moteur/themes/` (le thème et le fond sont dans le dossier du short).
- **Reconnaissable ?** À moitié. Le crayon jaune, la tasse de café, le jaune réservé et les lettres Barlow rappellent le plan
  bleu. Mais l'image est dominée par les bandes, cartes, notes et tampons du papier : **elle ressemble beaucoup à Atelier
  papier** (tapis bleu nuit quadrillé, mêmes pièces). Ce qui fait le plan bleu dans Lyrics chemin, c'est surtout l'écriture
  à l'encre jaune le long du trait, et ça appartient à la mécanique.
- **Leçon** : dans le moteur papier, la mécanique porte la signature (pièces de papier, pop à 12 i/s) ; l'habillage ne change
  que le fond et les couleurs, d'où quatre dérivations proches et maintenant une cinquième. À garder comme exemple de
  combinaison possible mais **peu utile** : ne pas en faire une recette de chaîne.

## Ce qu'on en tire pour le modèle

1. **Un habillage fort sur un fond plat se transporte bien** (C2) ; un habillage dont la signature tient dans le geste
   d'écriture se transporte mal (C4). La règle de § 8 (« une recette est reconnaissable quand ses deux briques le sont ») se
   vérifie dans les deux sens.
2. **Les doublons d'habillage se règlent par un parent à deux tons** (C1), pas par une fusion.
3. Le moteur du chemin prend un nouvel habillage en un fichier (C1 : ~110 lignes, C2 : ~70 lignes + un dessin) ; le moteur
   papier en un thème, mais il ne change que la surface.
4. Prochaine étape utile, si on continue : mesurer ces 3 shorts avec un `recognition.py` qui sépare habillage et mécanique
   (étape 5) ; C3 (carnet-archives sur le chemin) et C5 (grille suisse dans le papier) compléteraient le tableau dans l'autre sens.
