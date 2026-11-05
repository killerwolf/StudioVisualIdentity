# Page vitrine (artifact claude.ai)

Page publiée : https://claude.ai/artifact/VJEgxZpSjAn3cGGb51c1nK (privée ; partage depuis son menu Share).

Elle présente les 20 identités dans l'ordre du classement de `out/identities/index.json` (statuts « réhabilitée » et « ajoutée »), avec leurs 43 shorts jouables (aperçus 540×960 voisés), un filtre par famille, la superposition des zones sûres TikTok, le coût de rendu mesuré par short, la matrice identité × famille × librairie, les tests de reconnaissance à l'aveugle et les limites constatées.

| Fichier | Rôle |
|---|---|
| `page.tpl.html` | gabarit de la page (CSS, textes fixes, rendu JS) ; `__DATA__` est remplacé par les données |
| `build.py` | régénère `build/` depuis le dépôt : `data.json` (tokens, `short.json`, `narration.json`), `index.html`, aperçus vidéo et posters |
| `build/` | sortie non versionnée (≈ 35 Mo : 43 aperçus `v/*.mp4`, 44 images `p/*.jpg`) |

Régénérer :

```bash
.venv/bin/python out/showcase/build.py
```

Ré-encoder tous les aperçus, par exemple après un remix de la voix off :

```bash
.venv/bin/python out/showcase/build.py --force-videos
```

Ré-encoder seulement les aperçus d'une identité (par exemple quand la voix off du lot 2 sera mixée) :

```bash
.venv/bin/python out/showcase/build.py --videos-for trait-continu --videos-for carte-meteo
```

Puis republier avec l'outil Artifact : `file_path` = `out/showcase/build/index.html`, `root` = `out/showcase/build`, `files` = les chemins `v/*.mp4` et `p/*.jpg`, `url` = l'adresse ci-dessus pour mettre à jour la même page.

Les chiffres de l'en-tête (identités, shorts, QA, plus proche voisin) et la mesure de reconnaissance sont calculés par `build.py` depuis `index.json`, `qa.json` et `recognition.json` ; les textes fixes (juges visuels, directions, limites, colophon) sont dans `page.tpl.html` : les mettre à jour quand `out/report/` change.
