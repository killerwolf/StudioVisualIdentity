# Source de l'analyse « console-retro »

- **Œuvre analysée** : vidéo de démonstration d'un simulateur de vol en pixel art (« 32 KB », rendu par bandes empilées, sans polygones), publiée par **@creativedash** : https://x.com/creativedash/status/2122000830895386680
- **Repost consulté** : **@meta_pavy**, https://x.com/meta_pavy/status/2122241297482408234 (texte coréen : « pas de 3D, pas de polygones : un simulateur de vol de 32 Ko fait uniquement de bandes empilées, la sensation pixel Super Famicom du début des années 90, poussée jusque-là avec l'IA »).
- **Récupération** : 2026-11-18, via l'API publique de syndication de X (variante mp4 1486×1080, 60 fps, 11,35 s, piste audio AAC présente mais silencieuse). Une variante 2974×2160 existe ; elle n'a pas été utilisée.
- **Copie de travail** (hors dépôt, jamais versionnée) : `/Users/killerwolf/git/StudioVisualIdentity-sources/console-retro/` (`source_1080.mp4`, `tweet.json`).
- **Méthode** : ffmpeg (images à 3 i/s, détection de changements de plan, signal de différence image par image à 60 i/s, extraction audio, ebur128/astats), Python 3 + numpy + Pillow + scikit-learn (mesure de la taille du gros pixel par DFT des gradients, reconstruction des trames en résolution native, k-means des palettes, corrélation des ombres, flux par corrélation de phase). Détail et chiffres : `../console-retro-analyse.md`.

## Contenu de ce dossier (depuis le 2026-11-22)

| Fichier | Contenu |
|---|---|
| `palette.png` | nuanciers mesurés par type de vue (hex + part des pixels) : des valeurs mesurées, pas des images de la source |
| `avant/` | nos propres images, tirées de nos `short.mp4` avant la passe de détail |

Les images extraites de la vidéo de @creativedash ont été **retirées du dépôt le 2026-11-22**, avant qu'il soit rendu public pour la promotion. Il s'agit des 6 `frame_*.jpg` et de la planche-contact `contact-sheet.jpg`, ainsi que des planches qui mêlaient la source et nos shorts : `comparaison.jpg`, `comparaison-avant-apres.jpg`, `prototypes-abc.jpg`, `final-abc.jpg` et `retouche-fable.jpg`. Elles restent dans la copie de travail du propriétaire, hors dépôt. Les notes de studio qui les citent (`survol-pixel.md`, `survol-pixel-detail.md`, `challenge-…`) sont un historique : ces chemins n'existent plus dans le dépôt.

## Statut

L'œuvre analysée appartient à @creativedash. **Rien n'en est réutilisé** dans nos shorts : ni image, ni sprite, ni avion, ni cockpit, ni texte d'interface, ni son. L'identité qui en découle copie un *style* (grille de gros pixels, palette, construction de la profondeur), pas l'œuvre ; tout est regénéré par code.
