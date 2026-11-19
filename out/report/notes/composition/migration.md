# Migration vers les briques : plan par étapes réversibles (2026-11-19)

Statut : **plan, rien n'est exécuté.** Modèle : [`proposition.md`](proposition.md) ; état de départ :
[`inventaire.md`](inventaire.md).

## Règles qui tiennent pendant toute la migration

1. **Les shorts existants restent identiques.** Aucune étape ne touche un `short.mp4`, un `stills/` ni un `src/`
   existant. Contrôle à chaque étape : `git diff --stat <avant> -- out/shorts out/shared` vide (étapes de manifestes), ou,
   pour une étape qui touche un moteur partagé, ré-rendu des stills au pixel près comme pour l'extraction de
   `plan-bleu` (commit `dcd7d59` : « images et audit du short identiques »).
2. **Les ids et chemins sont gelés** : `out/identities/<id>/`, le préfixe `<id>__<famille>__<sujet>` des shorts,
   `out/shared/papier-moteur/themes/<id>.json` (lus par StudioGabarit), `bootstrap_studio.py --from <id>`. Une recette
   a l'id de l'identité dont elle vient.
3. **L'index est additif** : `identities[]` garde ses champs ; on ajoute des sections. Contrôle : les champs existants de
   `identities[]` sont identiques avant et après (`jq 'del(.identities[].habillage, …)'` comparé à l'ancien index).
4. **Chaque étape s'annule en supprimant ce qu'elle a ajouté** (dossiers neufs, champs neufs) ou par `git revert` d'un
   seul commit. Une étape = un commit.

## Les étapes

| # | Étape | Ce qui change | Contrôle « identique » | Annulation | Effort |
|---|---|---|---|---|---|
| 0 | **Fusionner `main` dans `identite-lyrics`** (survol-pixel, PR #4, `ee30e24`) | conflits attendus sur `out/identities/index.json` (le régénérer par `build_index.py` au lieu de fusionner à la main : ajouter `survol-pixel` à `ORDER`, `CURATION`…), `AGENTS.md` (sections et décomptes : 20 identités, 50 shorts), `package.json`, `out/report/*` | `check.py` des 50 shorts ; index régénéré contient les 23 entrées | `git reset` avant le commit de fusion, ou revert de la fusion | 0,5 session |
| 1 | **Manifestes seulement** : `out/formats/*.json` (4), `out/mecaniques/<id>/mecanique.json` (19), `out/habillages/<id>/habillage.json` (26), `out/recettes/<id>.json` (26) ; niveau `executable` ou `declare` ; adaptateurs = chemins des fichiers existants | uniquement des fichiers neufs ; valeurs reprises de `coreTokens` (index) et de l'inventaire ; un script jetable dans le scratchpad fait le premier jet, relu à la main | `git diff --stat -- out/shorts out/shared out/identities` vide | supprimer les 4 dossiers | 1 à 1,5 session |
| 2 | **`short.json` déclare ses briques** : `habillage`, `mecanique`, `format`, `recette` (50 shorts) | champs ajoutés aux `short.json` ; `longForm` gardé (lu par l'ancien `check.py`) | `md5` des `short.mp4` inchangés ; `check.py --all` donne le même `qa.json` | revert du commit | 0,5 session |
| 3 | **`check.py`** : lit `out/formats/<format>.json` (repli sur la règle actuelle si `format` absent) ; mode `--briques` (manifestes valides, références existantes, couleurs et polices de l'adaptateur = celles du `habillage.json` pour les 3 moteurs exécutables, contraste ≥ 4,5:1, `corpsMinPx`) | code de l'outil seulement | `check.py --all` : mêmes OK/FAIL que l'ancien sur les 50 shorts | revert | 0,5 session |
| 4 | **`build_index.py` v2** : lit `out/recettes/*.json` ; ajoute `habillages[]`, `mecaniques[]`, `formats[]`, `compatibilite[]` (états calculés, § 5 de la proposition) ; `schemaVersion` 2.0 | l'index gagne des sections ; les dictionnaires en dur (`CURATION`, `FAMILIES`, `LYRICS`…) restent la source dans cette étape | champs existants de `identities[]` identiques (règle 3) ; `bootstrap_studio.py` testé sur une identité | revert | 1 session |
| 5 | **`recognition.py`** : clé lue dans `short.json` ; mesure habillage (descripteur actuel) et mesure mécanique (descripteur temporel neuf) ; les 50 shorts | sortie dans un **nouveau** fichier `out/report/recognition-briques.json` ; `recognition.json` n'est pas réécrit | — (lecture seule des vidéos) | supprimer le fichier | 1 session |
| 6 | **Vitrine « composer »** dans `out/showcase/` (à partir de la maquette `vitrine-composer.html`), lue depuis `compatibilite[]` | `page.tpl.html` + `build.py` ; la vue actuelle devient « recettes » | la vue recettes affiche les mêmes données | revert | 0,5 à 1 session |
| 7 | **Docs** : `AGENTS.md` (le modèle en une section, la doctrine du mélange revue), skill `fabrique-identites` (« nouvelle pâte sur une mécanique existante = nouvelle recette »), mise à jour de `lyrics-chemin/identity.md` et `recipes/` | texte | — | revert | 0,5 session |
| 8 | **Briques exécutables, une mécanique à la fois**, dans l'ordre de facilité (ci-dessous) | code de moteur, **à côté** du code des shorts existants | stills au pixel près sur les shorts du moteur (règle 1) | revert | 0,5 à 1 session par mécanique |

**Total des étapes 0 à 7 : 5 à 6,5 sessions.** Étape 8, première vague (5 mécaniques) : 3 à 4 sessions.

### Variante minimale (80 % du gain, 2 sessions)

Fidèle à la règle « réemployer l'existant, la plus petite solution possible » : étapes **0, 1 et 2** seulement, plus un
tableau `compatibilite` écrit à la main dans `out/recettes/README.md` au lieu d'être calculé. On a alors le vocabulaire,
les briques déclarées, la matrice lisible et les shorts étiquetés, sans toucher à un seul outil. Les étapes 3 à 6 ne se
justifient qu'au moment où on produit réellement des combinaisons nouvelles (au-delà de 3 ou 4).

### Étape 8 : ordre conseillé des mécaniques

1. **`trace-chemin`** : déjà exécutable. Reste à rendre les primitives de dessin génériques (`boites`, `cercle`,
   `route`, `final`) pour qu'un habillage ne lise plus `G.mat`, `G.boites`, `G.moule` ou la ligne `'vague1'` en dur
   (`inventaire.md` § 3). Contrôle : les 4 shorts du chemin, stills au pixel près. C'est le moteur des premiers essais de
   `matrice.md`.
2. **`pop-papier-12ips`** : déjà exécutable. Rendre configurables la grille verte (`papier.py:251-256`) et les RGB hors
   thème (`elements.py`) **avec la valeur actuelle par défaut** (sinon les 8 shorts papier changent). `chaine.json` reste
   où il est (StudioGabarit).
3. **`chiffre-volet-compteur`** (swiss-data) et **`punch-cut-slam`** (brut-meme) : promouvoir `grille.js` et `brut.js`
   en moteurs `out/shared/grille-moteur/` et `out/shared/brut-moteur/` qui prennent un habillage ; **les copies dans
   `src/` des shorts existants ne bougent pas** (elles restent la preuve figée).
4. **`colonne-mot-a-mot`** (lyrics-punchy) : sortir `CAMAIEUX` et la police dans un habillage ; la mécanique exige une
   police à axe `wdth`.
5. Les 12 MOYEN : **seulement à la demande**, quand une combinaison de `matrice.md` en a besoin. Les 4 DIFFICILE restent
   déclarés (on les reproduit, on ne les recombine pas).

## Risques

| Risque | Parade |
|---|---|
| La fusion de `main` (étape 0) casse les décomptes ou l'index | régénérer l'index au lieu de le fusionner ; refaire les décomptes d'`AGENTS.md` à la main, un par un |
| StudioGabarit, `bootstrap_studio.py` ou un agent lit `index.json` et casse | index additif (règle 3) ; test de `bootstrap_studio.py` à l'étape 4 |
| Toucher un moteur partagé change un short publié | règle 1 : stills au pixel près, ou ne pas toucher (copier à côté) |
| `recognition.py` réécrit `recognition.json` et perd les juges aveugles | sortie dans un fichier neuf (étape 5) |
| Deux sources de vérité (manifestes et dictionnaires de `build_index.py`) pendant la transition | les dictionnaires restent la source jusqu'à l'étape 4 incluse ; on bascule ensuite, un dictionnaire par commit, en comparant l'index |
| Briques déclarées prises pour exécutables | champ `niveau` dans chaque manifeste, affiché par l'index et la vitrine |
| Sur-ingénierie (19 manifestes de mécaniques que personne n'utilise) | variante minimale d'abord ; l'étape 8 seulement pour les mécaniques qu'une combinaison réclame |
| Confusion famille / format (`paroles`) | `format` est un champ neuf ; `family` ne change pas |
| Une autre session travaille dans le même dépôt | un worktree par étape qui touche des outils ; `git add` par chemins explicites |
