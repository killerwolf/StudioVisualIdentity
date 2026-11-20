# Recettes et briques (version minimale le 2026-11-19, lues par les outils depuis le 2026-11-20)

Modèle validé par Hamdi le 19/11/2026 (choix 118) : **vidéo = Habillage × Mécanique × Format (+ Son)**. Une combinaison
validée, avec un nom, s'appelle une **recette**. Détail : [`out/report/notes/composition/proposition.md`](../report/notes/composition/proposition.md) ;
plan : [`migration.md`](../report/notes/composition/migration.md) (étapes 0, 1 et 2 le 19/11 ; étapes 3 à 7 le 20/11, option 125).

**Aucun short existant n'est modifié.** Depuis le 20/11/2026, les fiches sont lues par les outils, tous à travers
`out/tools/briques.py` : `check.py` (durée par format ; `check.py --briques` contrôle les fiches → `out/report/qa-briques.json`),
`build_index.py` (`out/identities/index.json` schéma 2.0 : `habillages[]`, `mecaniques[]`, `formats[]`, `recettes[]`,
`compatibilite[]`), `recognition.py --briques` (reconnaissance à deux étages → `out/report/recognition-briques.json`) et la
vitrine (`out/showcase/build.py`). `out/identities/` reste le dossier de preuve de chaque recette du même id.

## Le vocabulaire

| Brique | Ce que c'est | Où | Combien |
|---|---|---|---|
| Habillage | la pâte : palette par rôles, typo, matière, contraintes, adaptateurs | `out/habillages/<id>/habillage.json` (famille : `variantes/<v>.json`) | 25 en service (26 tons : la famille `craie` en a 2) ; 2 fiches remplacées gardées |
| Mécanique | le mouvement : texte, caméra, transitions, rythme, `requiert`, moteur | `out/mecaniques/<id>/mecanique.json` | 19 (2 exécutables) |
| Format | la livraison : durée, audio, zones sûres | `out/formats/<id>.json` | 4 |
| Recette | une combinaison nommée : habillage + mécanique + formats + statut + preuves | `out/recettes/<id>.json` | 29 (27 validées, 1 essai, 1 abandonnée) |

- **Niveau** de chaque brique : `executable` = un adaptateur existe et le moteur l'applique sans toucher au code de la
  mécanique (chemin-moteur : 4 habillages, papier-moteur : 4 habillages) ; `declare` = valeurs relevées (souvent les
  `coreTokens` de l'index) mais le code des scènes écrit ses valeurs en dur.
- **Étiquetage des shorts** : `etiquettes.json` donne pour chacun des 50 shorts sa recette, son habillage, sa mécanique et
  son format (51 depuis le 20/11/2026 : s'y ajoute le short de la recette adoptée « Données qui se tracent »). Il est tenu ici et **pas** dans les `short.json` (consigne du 19/11 : ne modifier aucun short existant ;
  `migration.md` étape 2 prévoyait des champs dans `short.json`, à faire plus tard si on le veut). Les 3 shorts issus des essais (C1, C2, C4), eux, déclarent aussi leurs briques dans leur propre `short.json`.
- `famille` (le sujet : `histoire`, `explicatif`, `paroles`…) n'est pas un format : `lyrics-chemin__histoire__le-premier-tour-du-monde`
  est de famille `histoire` au format `narre-long`.
- Les signatures (`curation.signatureToPreserve` de l'index) sont coupées en deux dans `signaturePortee` de chaque recette
  (moitié habillage, moitié mécanique). Ce découpage est un jugement, relu à la main.

## Familles d'habillage (depuis le 20/11/2026)

Un habillage peut être une **famille** à plusieurs **variantes** quand deux pâtes sont la même matière en deux tons (règle de
voisinage, proposition § 8.3 ; verdict de l'essai C1). Première famille : **`craie`** (`out/habillages/craie/habillage.json`,
variantes dans `out/habillages/craie/variantes/`) :

| Variante | Remplace la fiche | Ton | Adaptateur `trace-chemin` | Recettes |
|---|---|---|---|---|
| `craie/ardoise` | `out/habillages/ardoise/` (gardée, marquée `remplacee`) | bistrot, adultes | `ardoise.js` | chemin-ardoise |
| `craie/tableau-vert` | `out/habillages/craie-verte/` (gardée, marquée `remplacee`) | école, enfants | `craie-verte.js` | tableau-craie, chemin-craie-verte (essai C1) |

Dans les recettes et `etiquettes.json` : `"habillage": "craie"` + `"variante": "ardoise"` ou `"tableau-vert"` (l'ancien id est
gardé dans `habillageAvant`). Les fichiers d'adaptateur, la maquette de la vitrine et les `narration-chemin.json` gardent les
anciens ids (`ardoise`, `craie-verte`) : rien n'est renommé.

## Le tableau des combinaisons

Depuis le 20/11/2026, **la référence est calculée** : `compatibilite[]` de `out/identities/index.json` (états `teste`,
`compatible`, `a-tester`, `incompatible` ; build_index.py), à partir des fiches, de `etiquettes.json`, de `qa.json` et de
`propositions.json` (cases proposées non rendues C3, C5–C8, avec la raison écrite des incompatibles). Le tableau ci-dessous
est la copie lisible du 20/11/2026.

États : **testé** (un short existe et passe `check.py`), **compatible** (adaptateur + image fixe, pas de short), **à
tester** (besoins remplis sur le papier, pas d'adaptateur), **incompatible** (contrainte violée, raison écrite). Une case
absente vaut « inconnu ».

### Testées (29 : 27 recettes de chaîne, dont « Données qui se tracent » adoptée le 20/11/2026, + 1 essai + 1 essai abandonné)

| Habillage | Mécanique | Format | Recette | Shorts |
|---|---|---|---|---|
| grille-suisse | chiffre-volet-compteur | narre-court | swiss-data | 2 |
| gazette-sepia | tourniquet-tampon | narre-court | gazette-1900 | 2 |
| arcade-marine | simulation-deterministe | narre-court | pixel-arcade | 3 |
| brut-jaune | punch-cut-slam | narre-court | brut-meme | 2 |
| meteo-clair | carte-champs-front | narre-court | carte-meteo | 2 |
| bauhaus-primaires | puzzle-grille-morph | narre-court | bauhaus-kinetic | 2 |
| craie · tableau-vert | ecriture-trace-chiffon | narre-court | tableau-craie | 2 |
| riso-3-encres | impression-on-twos | narre-court | riso-zine | 2 |
| orange-graphite | traceur-escalier-plaque | narre-court | trait-continu | 2 |
| pixel-jour | survol-terrain | narre-court | survol-pixel | 2 |
| diorama-pastel | maquette-rebond | narre-court | pastel-diorama | 2 |
| relief-vert | survol-terrain | narre-court | topo-relief | 2 |
| gravure-parchemin | carte-trace-panoramique | narre-court | atlas-grave | 2 |
| aquarelle | lavis-multiplan | narre-court | aquarelle-conte | 2 |
| neon-labo | orbite-phenomene-neon | boucle, narre-court | neon-lab | 3 |
| cosmos-noir | travelling-cine-3d | narre-court | cosmos-doc | 2 |
| chrome-irise | plan-sequence-matiere | boucle, narre-court | liquid-chrome | 3 |
| papier-decoupe | pop-papier-12ips | narre-court | papier-decoupe | 2 |
| atelier-papier | pop-papier-12ips | narre-court | atelier-papier | 2 |
| carnet-archives | pop-papier-12ips | narre-court | carnet-archives | 2 |
| cabinet-curiosites | pop-papier-12ips | narre-court | cabinet-curiosites | 2 |
| punchy | colonne-mot-a-mot | paroles-muet | lyrics-punchy | 1 |
| plan-bleu | trace-chemin | paroles-muet | lyrics-chemin | 1 |
| editeur | trace-chemin | paroles-muet | chemin-editeur | 1 |
| craie · ardoise | trace-chemin | narre-long | chemin-ardoise | 1 |
| portulan | trace-chemin | narre-long | chemin-portulan | 1 |
| **craie · tableau-vert** | **trace-chemin** | **narre-long** | **essai C1** `chemin-craie-verte` | 1 |
| **grille-suisse** | **trace-chemin** | **narre-court** | **Données qui se tracent** `chemin-grille-suisse` (recette adoptée le 20/11/2026, issue de l'essai C2) | 1 |
| plan-bleu | pop-papier-12ips | narre-court | essai C4 `papier-plan-bleu` — **abandonné** le 20/11/2026 (presque un doublon d'Atelier papier ; short gardé comme exemple) | 1 |

### Proposées, pas encore essayées (`matrice.md`)

| # | Habillage × Mécanique × Format | État | Raison ou question |
|---|---|---|---|
| C3 | carnet-archives × trace-chemin × narre-long | à tester | porter un habillage du moteur Python vers le moteur JS |
| C5 | grille-suisse × pop-papier-12ips × narre-court | à tester | la grille suisse survit-elle au stop-motion à 12 i/s ? |
| C6 | brut-jaune × colonne-mot-a-mot × paroles-muet | incompatible | Anton n'a pas d'axe `wdth`, exigé par la colonne justifiée (réparable avec une police variable) |
| C7 | portulan × survol-terrain (survol.py) | incompatible | le moteur impose une grille 270×480 en palette indexée : un parchemin anticrénelé ne passe pas |
| C8 | pixel-jour × simulation-deterministe × narre-court | à tester | même grille 270×480 ×4 : faut-il un habillage parent `pixel-16` ? |

Verdicts des essais C1, C2, C4 et décision du 20/11/2026 (C2 adopté, famille craie, C4 abandonné) : [`out/report/notes/composition/essais.md`](../report/notes/composition/essais.md).

Statuts d'une recette (`statut`) : `validee` (recette de chaîne : catalogue, ou essai adopté comme C2), `essai` (C1), `abandonnee`
(C4 : le short reste, la combinaison n'est pas proposée). La clé `case` donne la case de `matrice.md` d'où vient une recette
(C1, C2, C4) ; `essai` ne reste que sur les recettes encore à l'essai ou abandonnées.
