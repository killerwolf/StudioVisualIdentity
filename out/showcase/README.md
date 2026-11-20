# Page vitrine (artifact claude.ai)

Page publiée : https://claude.ai/artifact/VJEgxZpSjAn3cGGb51c1nK (privée ; partage depuis son menu Share).

Elle s'ouvre sur la section **« Composer ses identités »** (modèle validé le 19/11/2026, choix 118 : Habillage × Mécanique × Format (+ Son) = Recette, un exemple illustré, l'inventaire en chiffres, la matrice habillages × mécaniques avec les **cases C1, C2, C4 rendues** (vidéo et verdict ; depuis le 20/11/2026, option 124 : C2 = recette adoptée « Données qui se tracent », cerclée de vert, C4 abandonné, grisé, C1 reste un essai), la **famille d'habillage « Craie »** (ardoise et tableau vert), l'effort et les décisions). Source : `out/report/notes/composition/` ; les données de la matrice sont lues dans la maquette `vitrine-composer.html`, les recettes nées d'une case dans `out/recettes/<id>.json` (clé `case`, ou `essai`, et `statut`) : leurs 3 shorts ont des aperçus `v/` et posters `p/` mais ne comptent pas dans les chiffres de l'en-tête (ils ne sont pas dans l'index).

Puis elle présente les 20 identités (23 déclinaisons : Papier découpé est affiché avec ses 3 dérivations regroupées sous « Dérivations ») dans l'ordre du classement de `out/identities/index.json` (statuts « réhabilitée » et « ajoutée »), avec leurs 50 shorts jouables (aperçus 540×960 ; 47 voisés, 3 vidéos de paroles muettes car la chanson est hors dépôt), un filtre par famille (dont Paroles), la superposition des zones sûres TikTok, le coût de rendu mesuré par short, la matrice identité × famille × librairie, les tests de reconnaissance à l'aveugle et les limites constatées. Les 4 shorts de Lyrics chemin affichent leur habillage (Plan bleu, Éditeur de code, Ardoise, Portulan).

| Fichier | Rôle |
|---|---|
| `page.tpl.html` | gabarit de la page (CSS, textes fixes, rendu JS) ; `__DATA__`, `__META__` et `__COMPOSER__` sont remplacés par les données |
| `build.py` | régénère `build/` depuis le dépôt : `data.json` (tokens, `short.json`, `narration.json`), `index.html`, aperçus vidéo et posters |
| `build/` | sortie non versionnée (≈ 48 Mo : 53 aperçus `v/*.mp4` dont 3 essais, 54 images `p/*.jpg`) |

Régénérer :

```bash
.venv/bin/python out/showcase/build.py
```

`main` est fusionné dans `identite-lyrics` depuis le 19/11/2026 (Survol pixel compris) : plus besoin de `--also-from` (l'option reste pour lire un autre checkout).

Ré-encoder tous les aperçus, par exemple après un remix de la voix off :

```bash
.venv/bin/python out/showcase/build.py --force-videos
```

Ré-encoder seulement les aperçus d'une identité (par exemple après un re-rendu ou un remix de la voix off de Survol pixel) :

```bash
.venv/bin/python out/showcase/build.py --videos-for survol-pixel
```

Puis republier avec l'outil Artifact : `file_path` = `out/showcase/build/index.html`, `root` = `out/showcase/build`, `files` = les chemins `v/*.mp4` et `p/*.jpg`, `url` = l'adresse ci-dessus pour mettre à jour la même page.

Les chiffres de l'en-tête (identités, shorts, QA, plus proche voisin) et la mesure de reconnaissance sont calculés par `build.py` depuis `index.json`, `qa.json` et `recognition.json` ; les textes fixes (juges visuels, directions, limites, colophon) sont dans `page.tpl.html` : les mettre à jour quand `out/report/` change.
