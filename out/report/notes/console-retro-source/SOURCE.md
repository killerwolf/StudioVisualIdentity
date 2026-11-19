# Source de l'analyse « console-retro »

- **Œuvre analysée** : vidéo de démonstration d'un simulateur de vol en pixel art (« 32 KB », rendu par bandes empilées, sans polygones), publiée par **@creativedash** : https://x.com/creativedash/status/2122000830895386680
- **Repost consulté** : **@meta_pavy**, https://x.com/meta_pavy/status/2122241297482408234 (texte coréen : « pas de 3D, pas de polygones : un simulateur de vol de 32 Ko fait uniquement de bandes empilées, la sensation pixel Super Famicom du début des années 90, poussée jusque-là avec l'IA »).
- **Récupération** : 2026-11-18, via l'API publique de syndication de X (variante mp4 1486×1080, 60 fps, 11,35 s, piste audio AAC présente mais silencieuse). Une variante 2974×2160 existe ; elle n'a pas été utilisée.
- **Copie de travail** (hors dépôt, jamais versionnée) : `/Users/killerwolf/git/StudioVisualIdentity-sources/console-retro/` (`source_1080.mp4`, `tweet.json`).
- **Méthode** : ffmpeg (images à 3 i/s, détection de changements de plan, signal de différence image par image à 60 i/s, extraction audio, ebur128/astats), Python 3 + numpy + Pillow + scikit-learn (mesure de la taille du gros pixel par DFT des gradients, reconstruction des trames en résolution native, k-means des palettes, corrélation des ombres, flux par corrélation de phase). Détail et chiffres : `../console-retro-analyse.md`.

## Contenu de ce dossier

| Fichier | Contenu |
|---|---|
| `contact-sheet.jpg` | 16 images de la source (horodatage en haut à gauche de chaque vignette) : 0,00 · 0,75 · 1,50 · 2,25 · 3,00 · 3,40 · 3,75 · 4,50 · 5,25 · 5,60 · 6,25 · 7,00 · 8,25 · 9,10 · 9,75 · 10,75 s |
| `palette.png` | nuanciers mesurés par type de vue (hex + part des pixels) |
| `frame_0.5s.jpg` | vue aérienne (île en terrasses, nuages, ombres) |
| `frame_3.40s.jpg` | transition aérienne → poursuite (bascule de la caméra) |
| `frame_4.3s.jpg` | vue de poursuite, perspective vers l'horizon |
| `frame_5.60s.jpg` | transition poursuite → cockpit (le tableau de bord monte) |
| `frame_7.0s.jpg` | vue cockpit |
| `frame_10.3s.jpg` | retour en vue aérienne |

## Statut de ces images

Ces images sont gardées **uniquement comme référence d'analyse** du style. **Rien n'en est réutilisé** dans nos shorts : ni image, ni sprite, ni avion, ni cockpit, ni texte d'interface, ni son. L'identité qui en découle copie un *style* (grille de gros pixels, palette, construction de la profondeur), pas l'œuvre ; tout est regénéré par code.
