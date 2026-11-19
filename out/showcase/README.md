# Page vitrine (artifact claude.ai)

Page publiée : https://claude.ai/artifact/VJEgxZpSjAn3cGGb51c1nK (privée ; partage depuis son menu Share).

Elle s'ouvre sur la section **« Composer ses identités »** (proposition du 19/11/2026 : le modèle Habillage × Mécanique × Format (+ Son) = Recette, un exemple illustré, l'inventaire en chiffres, la matrice habillages × mécaniques avec les essais C1, C2, C4, l'effort et les choix numérotés 118 / 119 / 120 à renvoyer sur Telegram). Source : `out/report/notes/composition/` ; les données de la matrice sont lues dans la maquette `vitrine-composer.html`.

Puis elle présente les 20 identités (23 déclinaisons : Papier découpé est affiché avec ses 3 dérivations regroupées sous « Dérivations ») dans l'ordre du classement de `out/identities/index.json` (statuts « réhabilitée » et « ajoutée »), avec leurs 50 shorts jouables (aperçus 540×960 ; 47 voisés, 3 vidéos de paroles muettes car la chanson est hors dépôt), un filtre par famille (dont Paroles), la superposition des zones sûres TikTok, le coût de rendu mesuré par short, la matrice identité × famille × librairie, les tests de reconnaissance à l'aveugle et les limites constatées. Les 4 shorts de Lyrics chemin affichent leur habillage (Plan bleu, Éditeur de code, Ardoise, Portulan).

| Fichier | Rôle |
|---|---|
| `page.tpl.html` | gabarit de la page (CSS, textes fixes, rendu JS) ; `__DATA__`, `__META__` et `__COMPOSER__` sont remplacés par les données |
| `build.py` | régénère `build/` depuis le dépôt : `data.json` (tokens, `short.json`, `narration.json`), `index.html`, aperçus vidéo et posters |
| `build/` | sortie non versionnée (≈ 45 Mo : 50 aperçus `v/*.mp4`, 51 images `p/*.jpg`) |

Régénérer :

```bash
.venv/bin/python out/showcase/build.py
```

Depuis le worktree `identite-lyrics` (tant que `main` n'y est pas fusionné), ajouter Survol pixel lu dans le checkout de `main` (ordre de `main`, puis les identités lyrics ; QA fusionnée par short ; reconnaissance = le `recognition.json` qui mesure le plus de shorts) :

```bash
python3 out/showcase/build.py --also-from ~/git/StudioVisualIdentity
```

Pour ne pas ré-encoder les 45 aperçus déjà faits dans `main`, copier d'abord `~/git/StudioVisualIdentity/out/showcase/build/{v,p}` dans `build/` puis les `touch` (les `short.mp4` hors lyrics sont identiques entre les deux branches) : seuls les 5 aperçus lyrics sont alors encodés.

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
