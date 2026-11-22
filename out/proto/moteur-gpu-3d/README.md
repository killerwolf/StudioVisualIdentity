Prototype archivé le 2026-11-22 : code et notes seulement. Les rendus (vidéos, images) sont dans le tag git local archive/moteur-gpu-3d-2026-11-22, hors dépôt public.

# Prototype « moteur 3D sur carte graphique » (phase 0, 18/11/2026)

Ce dossier est un **essai technique**, pas un short de preuve ni une identité : rien ici n'est référencé par
`out/identities/index.json` ni par `out/shorts/`. La note de conception est dans
`out/report/notes/moteur-gpu-3d-conception.md`. La palette et la scène sont provisoires.

## Ce qu'il y a

| Fichier | Rôle |
|---|---|
| `proto.py` | une vallée en terrasses (maillage numpy), une caméra qui avance en virant, rendu wgpu (Metal) en codes entiers, vote majoritaire, palette indexée, tuyau vers ffmpeg (×4 au plus proche voisin, 1080×1920, 30 i/s, H.264 yuv420p) |
| `mesures.py` | compare deux séries d'images natives (pixels différents) et mesure le scintillement A-B-A |
| `sortie/proto.mp4` | 6 s, 180 images, rendu sur la Radeon Pro 560, suréchantillonnage 4×4 |
| `sortie/still_*.png` | 3 images du même rendu |
| `sortie/mesures_*.json` | mesures brutes : 2 rendus Radeon, 1 rendu Intel |
| `essais/` | les petits tests de pile : `essai_wgpu.py`, `essai_moderngl.py`, `essai_chrome.mjs` |

## Installer (tout est local à ce dossier, rien en global)

```bash
cd out/proto/moteur-gpu-3d
uv venv --python 3.11 .venv
uv pip install -p .venv -r requirements.txt            # wgpu 0.33.0, numpy 2.4.6, pillow 13.0.0
uv pip install -p .venv -r essais/requirements.txt     # seulement pour essai_moderngl.py (compilé à l'installation)
(cd essais && PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH npm i)   # seulement pour essai_chrome.mjs (playwright-core 1.65.1, sans navigateur téléchargé)
```

Il faut aussi `ffmpeg` dans le PATH (9.0.2 ici). Mesuré sur macOS 13.7.8, Python 3.11.18, Node 22.23.3, Chrome 157.0.8103.79.

## Lancer

```bash
.venv/bin/python proto.py --out sortie/proto.mp4 --stills 0.5,3,5.5 --json sortie/mesures_radeon_1.json
.venv/bin/python proto.py --gpu intel --no-video --dump /tmp/intel.npy      # autre carte, images natives seulement
.venv/bin/python mesures.py ecart /tmp/radeon.npy /tmp/intel.npy
.venv/bin/python mesures.py aba /tmp/radeon.npy
.venv/bin/python essais/essai_wgpu.py
.venv/bin/python essais/essai_moderngl.py
PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH node essais/essai_chrome.mjs
```

Options de `proto.py` : `--gpu radeon|intel`, `--ss 1|2|4|8` (échantillons par côté de pixel natif), `--seconds`,
`--seed`, `--cell` (taille d'une case du monde, 1.0 ou 0.5), `--dump` (images natives en `.npy`, à écrire hors dépôt).

## Résultats (18/11/2026, charge 1 min 2,4–2,9 pendant les mesures)

| Mesure | Valeur |
|---|---|
| Coût, Radeon, 4×4, 790 774 triangles | **2,6–2,7 s pour 100 images** (26 ms par image : 19,6 ms carte graphique et relecture, 5,5 ms palette et ciel, 0,8 ms tuyau) |
| Coût, Intel HD 630, mêmes réglages | 2,5–3,1 s pour 100 images |
| Coût, Radeon, cases de 0,5 (2 843 698 triangles) | 2,4 s pour 100 images |
| Coût, Radeon, 8×8 (64 échantillons par pixel) | 3,3 s pour 100 images |
| Construction du monde et du maillage (processeur) | 0,4 s (2,4 s en cases de 0,5) ; compilation des shaders 2–3 s au premier lancement |
| Deux rendus sur la Radeon | **identiques** : même md5 des 180 images natives (`38013e19…`) et même md5 du mp4 (`f823be2d…`) |
| Deux rendus sur l'Intel | identiques (`7f9bcc59…`) |
| Radeon contre Intel | **93 pixels différents sur 23 328 000** (0,0004 %) ; 106 images sur 180 identiques ; au pire 3 pixels dans une image |
| Scintillement A-B-A natif | 2,97 % (1 échantillon) ; 2,64 % (4×4) ; 2,61 % (8×8) ; 1,95 % (cases de 0,5, 4×4) |
| Couleurs par image | 32–33 (palette provisoire de 42) |

Lecture et limites : voir la note.
