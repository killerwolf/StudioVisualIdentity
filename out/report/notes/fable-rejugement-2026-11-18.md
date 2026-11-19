# Survol pixel : rejugement après la passe de retouche (18/11/2026)

Lecture seule : aucun fichier du dépôt modifié. Jugé sur les nouveaux `short.mp4` (atoll 14:07, Machu Picchu 13:57), avec `measure2.py`, des images extraites, des crops à 100 % et des paires t / t + 1/30 s.

Dossier (noté `FR/`) : `scratchpad de session (hors dépôt, non conservé)`

- Mesures : `FR/v2/mesures.txt` (avant : `FR/mesures.txt`).
- Images : `FR/v2/atoll/row1.jpg` (0,3 / 2,7 / 6,5 / 12,5 s), `FR/v2/atoll/row2.jpg` (16,0 / 17,3 / 18,5 s + source), `FR/v2/machu/row1.jpg` (0,6 / 4,5 / 7,0 / 9,0 s), `FR/v2/machu/row2.jpg` (11,0 / 14,5 / 17,5 s + source), `FR/v2/CROPS_v2.jpg` (mer source / atoll, terre source / forêt, treillis).

## 1. Mesures refaites

Mes chiffres recoupent ceux du studio.

| Mesure | Source | Atoll avant → après | Machu Picchu avant → après |
|---|---|---|---|
| Scintillement A-B-A, short entier | 2,4 % | 0,87 → 0,57 % | 2,00 → 2,10 % |
| Scintillement A-B-A, pire fenêtre | 3,4 % | 1,78 → 1,38 % | 4,29 → 4,49 % (piqué) |
| Pixels qui changent par image | 26–33 % | 6,5 → **5,2 %** | 21,6 → 20,4 % |
| dont accroche / plan final | | 6,5 → 7,0 % / 11,4 → **5,6 %** | |
| Pixels sombres (luminance < 70) | 3–6 % | 2,1 → 3,1 % | 21,8 → **12,0 %** (survol 12,7 ; piqué 15,1) |
| Pixels blancs (nuages, écume, cartouches) | 2,5–6,4 % | 6,6 → 6,5 % | 11,2 → 13,1 % |
| Paire à 9,0 s, pixels changés | | | 42,6 → 41,8 % |

## 2. Verdict par retouche

| # | Retouche | Verdict | Raison |
|---|---|---|---|
| 1 | Nuages | **Réussie à Machu Picchu, partielle à l'atoll** | Machu Picchu : des tas de coton partout, modelé tramé propre, plus de « store ». Atoll : les nuages restent à l'horizon ; au premier plan on voit leurs ombres mais presque jamais le nuage lui-même (2,7 s, 16,0 s, 17,3 s). Les ombres sur le relief de Machu Picchu ne se voient toujours pas. |
| 2 | Écume de l'atoll | **Partielle** | Le motif est acquis : des traits orientés, plus de neige. Mais ils sont environ deux fois plus longs et trois fois plus rares que dans la source (`FR/v2/CROPS_v2.jpg`, vignettes 1 et 2), et ils disparaissent au-delà du premier tiers de la mer. Le critère chiffré (80 % des taches ≥ 3 px) n'est pas tenu : 53 %. Le scintillement a baissé, pas monté. |
| 3 | Forêt de Machu Picchu | **Réussie** | Pixels sombres 21,8 → 12,0 %, le bleu nuit ne se voit plus que dans les joints de pierre, bouquets et clairières lisibles. Reste une régularité de rangs sur le versant proche (9,0 s). |
| 4 | Caméra de l'atoll | **Cadrage réussi, mouvement raté** | L'accroche (0,3 s) et le plan final (18,5 s) sont les deux meilleures images du short : anneau entier, horizon, nuages, autres atolls. Mais le mouvement a baissé (6,5 → 5,2 %), et le plan final est deux fois plus lent qu'avant. Mon erreur : j'ai fixé un cadrage large et une cible de mouvement incompatibles sans déplacer de temps de clé. |
| 5 | Pain de sucre | **Partielle** | Ce n'est plus une tour grise, et le diagnostic du studio (les murs de terrasse montaient sur le pic) est le bon. Le critère est tenu. Mais le pic reste un cône raide et régulier, rayé de bandes vertes, qui se lit comme une ruche ou un sapin (14,5 s, 17,5 s). |
| 6 | Finitions | **Réussie, sauf le ciel de Machu Picchu en vue haute** | Socle de l'atoll propre. Ciel de l'atoll en paliers lisibles. À Machu Picchu, le ciel reste blanchâtre à 0,6 et 4,5 s (la bande visible est trop mince), il n'est en paliers qu'au piqué et à la remontée. |

## 3. Écarts du studio

1. **Contremarches naturelles éclaircies : à garder.** C'est ce levier qui fait tenir le critère de pixels sombres ; mes propres leviers n'y arrivaient pas (19–20 % à l'essai). Le risque annoncé ne se réalise pas : les terrasses restent détachées par leurs murs de pierre gris et leur vert plus clair (`FR/v2/machu/row1.jpg`, 7,0 et 9,0 s). Contrepartie à connaître : le versant boisé est maintenant rayé de bandes claires horizontales, ce qui accentue l'aspect « ruche » du pain de sucre.
2. **Murs sortis du pain de sucre, seuil de granite à 100 × K : à garder.** La cause réelle était les murs, pas le granite ; ma proposition de monter le seuil à 112 × K aurait supprimé la cime puisque le sommet fait 105 × K. Le cône vert au fond du plan de coupe (11,0 s) ne gêne pas la lecture de la coupe.
3. **Garde-fou `cap_colors` : à garder.** Il ne touche que 1 à 10 pixels de brume lointaine sur quelques images, et il protège un critère du challenge (≤ 32 couleurs par image) que ma rampe de ciel avait fait sauter. Je n'ai vu aucune trace visible sur les images de 9,5 à 13,5 s que j'ai extraites (6,5 et 12,5 s seulement : contrôle partiel).

Les deux critères non tenus à l'atoll (mouvement, écume) et le treillis non corrigé sont à accepter en l'état. Le studio a eu raison de ne pas forcer le lacet au prix du cadrage, et de ne pas toucher aux terrasses.

## 4. Ce qui sépare encore les shorts de la source, classé

1. **L'atoll est presque immobile** : 5,2 % de pixels changent par image contre 26–33 %. La source est un vol, l'atoll est un plan de maquette qui tourne lentement. C'est l'écart le plus visible, et il tient au propos (une coupe à lire) autant qu'à la caméra.
2. **La moitié basse de l'atoll reste une mer presque vide** : des traits rares, pas de nuage au premier plan, des ombres sans leur nuage. La source remplit ce même espace de nuages, d'ombres et de hauts-fonds.
3. **L'atoll n'a pas de terre verte** : c'est voulu (pas d'archipel copié), mais c'est ce qui le laisse hors de la reconnaissance mesurée (toujours plus proche d'aquarelle-conte) et loin de la gamme bleu / vert / sable de la source.
4. **Machu Picchu est encore deux à quatre fois plus sombre et plus chargé** : 12 % de pixels sombres contre 3–6 %, une forêt en rangs de boules là où la source a des bouquets posés sur de grands aplats clairs.
5. **Les reliefs naturels sont trop réguliers** : cônes à bandes parallèles (pain de sucre, versants), contre des côtes et des courbes de niveau irrégulières dans la source.
6. **Défauts mineurs** : scintillement du piqué de Machu Picchu à 4,5 % contre 3,4 % ; treillis au bord gauche à 4,5 et 17,5 s ; ombres de nuages absentes du relief ; ciel blanchâtre en vue haute.

## 5. Jugement global

La passe a fait ce qu'elle pouvait faire sans toucher au propos : Machu Picchu a nettement gagné (clair, nuageux, sans bleu nuit, sans tour grise) et ressemble maintenant à un cousin crédible de la source. L'atoll a gagné ses motifs (écume, ombres, socle, deux beaux cadrages) mais reste un plan lent sur une mer aux deux tiers vide, et je me suis trompé en lui fixant une cible de mouvement que mon propre cadrage rendait inatteignable. Je garderais les trois écarts du studio et j'arrêterais là : ce qui reste tient au sujet de l'atoll et à la règle « pas d'archipel », pas à un réglage.
