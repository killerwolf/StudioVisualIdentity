# Environnement de rendu — mise en place (2026-11-18, branche `identite-console-retro`)

Mac Intel i7 4 cœurs, 16 Go, macOS Ventura 13 ; machine partagée avec d'autres sessions Claude (charge 30–75 pendant toute la mise en place). Rien n'a été commité ni supprimé.

## Installé

- **Node** : absent du PATH des shells non interactifs ; présent via nvm (`~/.nvm/versions/node/v24.22.2`, aussi v22.23.3). À préfixer : `export PATH="$HOME/.nvm/versions/node/v24.22.2/bin:$PATH"`.
- **`npm i`** (Node 24.22.2, npm 11.19.1) : 154 paquets, 47 s, 0 vulnérabilité. Le postinstall de `babylonjs` n'a pas été exécuté (allowScripts npm 11) : sans effet attendu sur le rendu.
- **`.venv` Python 3.11.18** (`uv venv --python 3.11 .venv`, CPython téléchargé par uv), paquets **en roues uniquement** (`--only-binary :all:`) :
  numpy 2.4.6, scipy 1.17.1, Pillow 13.0.0, opencv-python-headless **4.11.0.86**, matplotlib 3.11.2, shapely 2.2.0, opensimplex 0.4.5.1, taichi 1.7.2 (roue disponible, import OK), pycairo 1.29.2 (voir ci-dessous).
- **Piège** : sans `--only-binary`, uv choisit une version d'opencv-python-headless sans roue macOS x86_64 et la **compile depuis les sources** (charge 68, plusieurs minutes) : compilation arrêtée. Toujours installer avec `--only-binary :all:` sur ce Mac Intel (facts.md cite opencv 5.0.0 : pas de roue x86_64 macOS).
- **pycairo** : pas de roue macOS, et la lib système cairo est **absente** (ni brew, ni pkg-config). Pas d'installation brew. Contournement sans rien installer de global : pycairo compilé dans la venv contre le cairo 1.18.6 **déjà présent** dans l'env conda `pdf-ocr` :
  `PKG_CONFIG_PATH=/usr/local/Caskroom/miniconda/base/envs/pdf-ocr/lib/pkgconfig uv pip install --python .venv/bin/python --no-binary pycairo pycairo` (28 s). `import cairo` → 1.29.2 / cairo 1.18.6 ; `_cairo.so` pointe sur `@rpath/libcairo.2.dylib` de cet env.
  **Fragile** : si l'env conda `pdf-ocr` est supprimé ou mis à jour, pycairo casse. Solution durable : `brew install cairo` (à décider par Hamdi), puis réinstaller pycairo.

## Non installé

- **Manim** : pas de roue (il dépend de pycairo et manimpango, qui ne compile pas). Faisable maintenant que pycairo existe, via la procédure stub de `facts.md` l. 20, mais non fait (inutile pour une identité Python/pycairo). 
- **Playwright + Chromium** : voir plus bas.
- **google-genai** : non installé (seulement utile pour `tts.py --engine gemini`).

## Chromium / Playwright

- Aucun Chromium Playwright (`~/Library/Caches/ms-playwright` absent) et **le paquet npm `playwright` n'est pas dans `package.json`** (render.mjs fait `require('playwright')`, résolu via NODE_PATH ou node_modules). Google Chrome est installé dans /Applications mais render.mjs ne l'utilise pas.
- Pour les identités navigateur, deux étapes (non exécutées) :
  ```
  npm i --no-save playwright@1.65.1
  npx playwright install chromium            # ≈ 325 Mo : Chrome for Testing 159.0.8154.6 mac-x64 (212,5 Mo) + headless shell (111,7 Mo) + ffmpeg
  npx playwright install --only-shell chromium   # ≈ 112 Mo : headless shell seul, suffit à chromium.launch() headless
  ```
  Tailles mesurées par HEAD sur `storage.googleapis.com/chrome-for-testing-public/159.0.8154.6/mac-x64/`.

## check.py : ce qu'il exige (`out/tools/check.py`)

**Erreurs (bloquantes, `ok: false`)** :
- `short.mp4` présent (c'est **short.mp4** qui est contrôlé, jamais short_novo.mp4) : `mp4 = d / 'short.mp4'` (l. 29).
- 1080×1920 : `if (v['width'], v['height']) != (1080, 1920)` (l. 45).
- 30 fps exactement : `if v['r_frame_rate'] not in ('30/1',)` (l. 46).
- H.264 yuv420p : `if v['codec_name'] != 'h264'` / `if v['pix_fmt'] != 'yuv420p'` (l. 47–48).
- **Une piste audio**, quelle qu'elle soit : `if not a: err.append('pas de piste audio')` (l. 49).
- Durée 9,9–20,1 s : `if not (9.9 <= dur <= 20.1)` (l. 50).
- Aucune frame noire ≥ 0,25 s : `blackdetect=d=0.25:pix_th=0.06` (l. 51–54).
- `short.json` **et** `narration.json` présents et JSON valides : `for f in ('short.json', 'narration.json')` (l. 61–65).
- **≥ 3 stills** `.jpg`/`.png` dans `stills/` : `if not (3 <= len(stills))` (l. 85 ; le message dit « 3–5 » mais il n'y a pas de maximum).
- `src/` non vide (l. 86).

**Avertissements seulement (n'empêchent pas `ok: true`)** :
- image figée ≥ 3 s (`freezedetect=n=0.001:d=3`, l. 55–58) ;
- `narration.json` a des lignes mais `short.json.sound.voice` faux → « voix off absente » (l. 71–72) ;
- nombre de `voice_lines/*.mp3` ≠ nombre de lignes, seulement si `sound.voice` vrai et le dossier existe (l. 74–75) ;
- ligne > 3,2 mots/s par rapport à `maxDuration` (l. 76–79) ;
- `qualityChecks.stillsReviewed == false` (l. 80–81).

**Non vérifié** : loudness (aucune mesure LUFS), présence de `voice_lines/`, champs de `short.json` (seulement sa validité JSON, plus `sound.voice` et `qualityChecks.stillsReviewed` lus pour les avertissements), contenu de `narration.json`, short_novo.mp4.

**Un short sans voix off passe** : testé sur une copie (scratchpad) avec short.mp4 = vidéo + musique/SFX seulement, `sound.voice: false` → `ok: true` avec l'avertissement « voix off absente » ; avec `narration.json` = `{"lines": []}` → `ok: true`, zéro avertissement. Il faut quand même une piste audio et un `narration.json` valide.

## Tests de fumée (sorties uniquement dans le scratchpad, aucun fichier du dépôt modifié)

| Test | Résultat | Durée | Charge (`uptime`, 1 min) |
|---|---|---|---|
| `check.py` sur `trait-continu__geographie__l-italie-a-la-forme-d-une-botte` | ok, 0 avertissement (16,0 s, 1080×1920, 30/1, h264, yuv420p) | 3,5 s | ≈ 31 |
| `check.py` sur `bauhaus-kinetic__engagement__trouve-l-intrus` (navigateur) | ok, 0 avertissement (14,0 s) | 3,2 s | ≈ 31 |
| `sound.py src/sound.json music.wav` (trait-continu Italie) | WAV 48 kHz OK | 2 min 55 s mur pour **6 s CPU** (4 % CPU : machine saturée) | ≈ 31–40 |
| `assemble.py mux --video short_novo.mp4 --music music.wav` | short muxé OK, −18,6 LUFS intégrés (musique seule) | < 3 min (en fond) | ≈ 40 |
| `video.py --stills 0.6,3.6,8.8,15.8` (trait-continu) | 4 stills conformes à l'original (vérifié à l'œil) | 27–39 ms/image, 9,7 s au total | ≈ 74 |
| `video.py --out video.mp4` rendu complet 480 images | OK ; **2,2 s / 100 images** (10,6 s, build 0,18 s) ; SSIM 0,991 contre short_novo.mp4 d'origine | 11 s mur | ≈ 52–55 |
| `assemble.py mux` du re-rendu + `check.py` | ok | — | ≈ 52 |

Méthode : le dossier `src/` du short a été copié dans `scratchpad/smoke/repo/out/shorts/<short>/src/` avec des liens vers `out/tools` et `node_modules` (traceur.py cherche la racine en `parents[4]`), et le cache codé en dur `/tmp/svi/...` de `video.py` a été remplacé par le scratchpad dans la copie. Le rendu pur Python (pycairo + shapely) reste très bon marché même sous forte charge : 2,2 s/100 images contre 23,4 s mesurés pour le short entier pendant la campagne.

## Clé Gemini

- **Non** : ni `GEMINI_API_KEY` ni `GOOGLE_API_KEY` dans l'environnement ; aucun `.env` dans le dépôt ni dans ses dossiers parents (`~/git`, `~`). `FISH_API_KEY` absente aussi.
- Plus tard : `tts.py --engine gemini` lit `GEMINI_API_KEY` (ou `GOOGLE_API_KEY`) et demande `google-genai` ≥ 2.30 ; sans clé il sort proprement (code 3) sans toucher aux fichiers. Le skill `studio:gemini-voices` (`gemini_voix.py`) lit `GEMINI_API_KEY`, sinon un `.env` du dossier courant ou d'un parent ; c'est la voie du lot 2 (un appel par short, découpé en `voice_lines/NN.mp3`, puis `tts.py --engine files --replace`). Utilisable dès qu'Hamdi colle sa clé dans un `.env`.
- **Attention** : `.env` n'est **pas** dans `.gitignore` de ce dépôt ; l'y ajouter avant d'y mettre une clé.
