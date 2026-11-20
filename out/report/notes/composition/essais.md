# Essais C1, C2, C4 : verdicts (2026-11-19)

> **Décision du 20/11/2026 (Hamdi, option 124).** C2 est corrigé (1re image = un « 8 » rouge géant en gros plan ;
> « 1 carré = 100 millions » remplacé par l'échelle « 100 % = 8 Md », piste entière = 8 milliards, Asie 59 %, Afrique 18 % ;
> la réplique de voix « Un carré… » retirée, aucune nouvelle voix ; 13,8 s, planche [`essais/C2-planche-2026-11-20.jpg`](essais/C2-planche-2026-11-20.jpg))
> et **adopté comme recette de chaîne « Données qui se tracent »** (`out/recettes/chemin-grille-suisse.json`, statut `validee`) :
> ce n'est plus un essai. **Ardoise et craie verte deviennent une famille d'habillage « craie »** à deux variantes
> (`craie/ardoise`, `craie/tableau-vert` ; `out/habillages/craie/`), les anciennes fiches gardées et marquées `remplacee` ;
> C1 reste un essai. **C4 est abandonné** (statut `abandonnee`, short gardé comme exemple). Les verdicts ci-dessous sont
> ceux du 19/11 et ne sont pas réécrits (les faiblesses de C2 qu'ils citent sont corrigées).

Décision d'Hamdi : choix 118 (modèle + version minimale + essais C1, C2, C4). Combinaisons décrites dans
[`matrice.md`](matrice.md) ; recettes d'essai dans `out/recettes/chemin-craie-verte.json`, `chemin-grille-suisse.json`,
`papier-plan-bleu.json`. Aucune nouvelle voix : les trois shorts réutilisent une voix qui existait. Aucun moteur partagé
modifié : deux habillages neufs dans `out/shared/chemin-moteur/habillages/` (`craie-verte.js`, `grille-suisse.js`), un dessin
neuf (`dessins/barres-humains.json`), et pour C4 un thème et un fond rangés dans le dossier du short.

Jugement à l'œil (le mien, sur les planches et les comparaisons ci-dessous), **pas mesuré** le 19/11 : `recognition.py` n'a pas été
relancé (il réécrit `recognition.json` et ne sait pas encore séparer habillage et mécanique, étape 5 de `migration.md`).

> **Mesure du 20/11/2026 (option 125, `recognition.py --briques`, `out/report/recognition-briques.json`)** : 53 shorts, C4 exclu
> (abandonné). Habillage, top-1 42/47 (5 shorts seuls de leur habillage non comptés). **Test croisé de l'habillage entre
> mécaniques : 5/6.** C2 et les deux swiss-data se retrouvent l'un l'autre au 1er rang parmi les shorts d'une autre mécanique
> (3/3) : la mesure confirme le verdict à l'œil. Les deux tableau-craie ont C1 pour premier voisin (2/2), mais C1, lui,
> a pour voisin papier-decoupe (tapis vert) et ne trouve un tableau-craie qu'au 3ᵉ rang : craie-verte sur le chemin est
> reconnue depuis Tableau Craie, pas l'inverse. Mécanique (descripteur temporel neuf) : test croisé entre habillages 13/18
> (`trace-chemin` 5/6, `pop-papier-12ips` 8/8 ; `survol-terrain` 0/4 : Relief topo et Survol pixel ne bougent pas pareil) ;
> contrôle sans les shorts du même sujet (les 4 papiers rendent les mêmes épisodes) : toujours 13/18, c'est le mouvement qui est reconnu.
> C4, mis à part, a pour plus proche voisin d'habillage `lyrics-chemin__paroles__claudes-plan` (le plan bleu) et pour voisin de
> mécanique un short papier (carnet-archives).

| Essai | Short | Rendu | `check.py` | Planche | Comparaison |
|---|---|---|---|---|---|
| C1 craie-verte × trace-chemin × narré long | `out/shorts/chemin-craie-verte__explicatif__le-quatre-quarts/short.mp4` (25,6 s) | 779,7 s, 101,5 s / 100 images | OK, 0 avertissement | [`essais/C1-planche.jpg`](essais/C1-planche.jpg) | [`essais/C1-comparaison.jpg`](essais/C1-comparaison.jpg) : ardoise / C1 / tableau-craie aux mêmes instants |
| C2 grille-suisse × trace-chemin × narré court | `out/shorts/chemin-grille-suisse__geographie__ou-vivent-8-milliards/short.mp4` (15 s) | 124,4 s, 27,7 s / 100 images | OK, 0 avertissement | [`essais/C2-planche.jpg`](essais/C2-planche.jpg) | [`essais/C2-comparaison.jpg`](essais/C2-comparaison.jpg) : swiss-data 8 milliards / C2 / swiss-data éclipse / bauhaus |
| C4 plan-bleu × pop-papier-12ips × narré court | `out/shorts/papier-plan-bleu__explicatif__d-ou-vient-le-mot-sandwich/short.mp4` (12,2 s) | 15 s (4 tranches) | OK, 1 avertissement : image figée ≥ 3 s à 3,2 s (le plan où rien ne bouge entre deux répliques ; l'épisode d'origine sur tapis vert ne le déclenche pas, son quadrillage plus contrasté et ses chiffres de règle suffisent à le « faire bouger » pour le détecteur) | [`essais/C4-planche.jpg`](essais/C4-planche.jpg) | [`essais/C4-comparaison.jpg`](essais/C4-comparaison.jpg) : papier-decoupe / C4 / lyrics-chemin (plan bleu) |

Les `chemin_audit.mjs` de C1 et C2 disent « aucune » erreur.

## C1 — Craie verte sur le chemin : distinct de l'ardoise, mais de la même famille

- **Reconnaissable ?** Oui, comme Tableau Craie : tableau vert pleine image, craie orange pour le mot dit et bleue pour les
  annotations, écriture manuscrite Caveat en minuscules, rebord en bois avec trois bâtons de craie et une brosse. Le décor du
  dessin (œufs, fouet, cuillère, beurre) est dessiné à la craie au lieu d'être des objets réels.
- **Doublon de l'ardoise ?** Pas à l'image : sur la comparaison, aux mêmes instants, on distingue toujours les deux (vert et
  minuscules manuscrites contre noir et majuscules étroites ; craie dessinée contre objets ; tableau pleine image contre ardoise
  encadrée sur du marbre). Mais c'est la **même matière** (craie érodée par le même grain, même dessin, même mise en page) en
  deux tons, et `craie-verte.js` a les mêmes crochets que `ardoise.js` (dont il est parti). Recommandation : **un habillage parent `craie` avec deux tons**
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
  même échelle (Asie 4,72 Md, Afrique 1,44, Inde 1,45, Chine 1,41). Avec C1 (craie-verte) et C4 (plan-bleu), c'est l'un des trois premiers habillages portés sur une deuxième mécanique, et
  **le cas le plus net** des trois : ce que la règle de reconnaissance (proposition § 8) attendait.
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
