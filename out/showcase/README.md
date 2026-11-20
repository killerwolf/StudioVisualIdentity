# Page vitrine (artifact claude.ai)

Page publiée : https://claude.ai/artifact/VJEgxZpSjAn3cGGb51c1nK (privée ; partage depuis son menu Share).

Elle s'ouvre sur la section **« Composer ses identités »** (modèle validé le 19/11/2026, choix 118 : Habillage × Mécanique × Format (+ Son) = Recette ; option 124 le 20/11 : C2 = recette adoptée « Données qui se tracent », famille d'habillage « Craie », C4 abandonné ; option 125 le 20/11 : plan complet). Depuis le 20/11/2026 (migration.md étape 6), **toute la section est calculée depuis les fiches** : `build.py` lit les sections briques de `out/identities/index.json` (schéma 2.0 : `habillages[]`, `mecaniques[]`, `formats[]`, `recettes[]`, `compatibilite[]`, produites par `out/tools/build_index.py` depuis `out/habillages/`, `out/mecaniques/`, `out/formats/`, `out/recettes/`, dont `propositions.json` pour C3, C5–C8) et `out/report/recognition-briques.json` (reconnaissance à deux étages, `recognition.py --briques`). Chiffres de la section (recettes, habillages, mécaniques, shorts, facile / moyen / difficile), matrice (extrait et complète), cases rendues C1, C2, C4 (vidéo, verdict, statut), cases proposées et reconnaissance à deux étages : tout vient de là. La maquette `out/report/notes/composition/vitrine-composer.html` n'est plus lue (gardée, marquée « remplacée »). Les 3 shorts nés de la matrice ont des aperçus `v/` et posters `p/` ; ils comptent dans « shorts livrés » (53) et dans le contrôle qualité de l'en-tête, pas dans les bandes des identités. Textes fixes encore écrits à la main dans `page.tpl.html` : l'exemple « Le quatre-quarts », les verdicts résumés de la ligne « survol de relief », l'effort et les décisions.

Captures de contrôle (20/11/2026, en-tête + section Composer, 390 px et 1240 px, clair et sombre) : `out/report/notes/composition/vitrine/`.

Puis elle présente les 20 identités (23 déclinaisons : Papier découpé est affiché avec ses 3 dérivations regroupées sous « Dérivations ») dans l'ordre du classement de `out/identities/index.json` (statuts « réhabilitée » et « ajoutée »), avec leurs 50 shorts jouables (aperçus 540×960 ; 47 voisés, 3 vidéos de paroles muettes car la chanson est hors dépôt), un filtre par famille (dont Paroles), la superposition des zones sûres TikTok, le coût de rendu mesuré par short, la matrice identité × famille × librairie, les tests de reconnaissance à l'aveugle et les limites constatées. Les 4 shorts de Lyrics chemin affichent leur habillage (Plan bleu, Éditeur de code, Ardoise, Portulan).

| Fichier | Rôle |
|---|---|
| `page.tpl.html` | gabarit de la page (CSS, textes fixes, rendu JS) ; `__DATA__`, `__META__` et `__COMPOSER__` sont remplacés par les données |
| `build.py` | régénère `build/` depuis le dépôt : `data.json` (tokens, `short.json`, `narration.json`), `index.html`, aperçus vidéo et posters |
| `build/` | sortie non versionnée (≈ 53 Mo : 53 aperçus `v/*.mp4` dont 3 nés de la matrice, 54 images `p/*.jpg`) |

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

Les chiffres de l'en-tête (identités, shorts, QA, plus proche voisin, recettes, habillages · mécaniques, reconnu par l'habillage / par la mécanique) et les mesures de reconnaissance sont calculés par `build.py` depuis `index.json`, `qa.json`, `recognition.json` et `recognition-briques.json` ; les textes fixes (juges visuels, directions, limites, colophon) sont dans `page.tpl.html` : les mettre à jour quand `out/report/` change.
