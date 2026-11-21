# Vidéo démo « Caméléon » (français, 43 s)

- `demo_16x9.mp4` (1920×1080) et `demo_9x16.mp4` (1080×1920) : 43 s, 30 i/s, H.264 yuv420p, musique + bruitages.
- `demo_16x9_novo.mp4`, `demo_9x16_novo.mp4` : les mêmes, sans voix (musique + bruitages).
  **Tant que `voice_fr/` n'existe pas, `demo_*.mp4` et `demo_*_novo.mp4` ont le même contenu** : aucune voix n'a été générée.
- `demo_preview.gif` : 12 premières secondes, muettes, pour le README.
- `thumb/thumbnail_fr_1280.jpg` (et `_1920`) : la vignette.
- `planche-demo-fr.jpg` : planche de 12 images de la version 16:9.
- `narration_fr.json` : le texte de la voix off et son minutage ; `sound_fr.json` : les bruitages posés.
- `v1/` : l'ancienne démo anglaise « 14 styles » (51 s), ses sources et ses vignettes.

## L'idée

La démo est un **caméléon** : elle prend tour à tour le fond, la police et la couleur de chacune des 18 identités, et sa matière
est faite des vrais shorts du dépôt. Tout le texte à l'écran est en français, et la vidéo se comprend sans le son.

## Déroulé

| Temps | Plan |
| --- | --- |
| 0 – 2,5 s | Accroche : un mur de cartes « template » toutes identiques défile, « ENCORE LA MÊME VIDÉO ? » claque mot par mot. |
| 2,5 – 4 s | Le mur s'éteint, une carte prend vie et change de style quatre fois par seconde : « Et si la vôtre ne ressemblait à aucune autre ? » |
| 4 – 14 s | Carrousel en profondeur des **18 identités**, du plus clair au plus sombre : le fond, le halo, le nom fantôme et le titre prennent les couleurs et la police de chaque identité (une par demi-seconde). |
| 14 – 18 s | Le même mur incliné que l'accroche, mais chaque carte est un vrai short : « 45 shorts, tous rendus par du code ». |
| 18 – 22 s | Le juge à l'aveugle : 72 images mélangées se rangent en 18 colonnes, les coches tombent, « 18/18, zéro erreur ». |
| 22 – 29 s | « Un seul prompt. » L'agent tape le prompt, compare les 18 styles, en choisit un, crée le studio, rend l'épisode 1. |
| 29 – 35 s | Épisodes 1, 2, 3 : trois vrais shorts de la même identité (Arcade Pixel) s'enchaînent dans le téléphone. |
| 35 – 39 s | Quatre panneaux, chacun dans une identité : 18 identités · 21 déclinaisons · 45 shorts · 100 % open source. |
| 39 – 43 s | Carton de fin : le nom change de police sur chaque temps puis se pose, adresse du dépôt, « Donnez le prompt à votre agent. » |

## Fabrication

Pas de navigateur : chaque image est dessinée en Python (numpy, OpenCV, Pillow) puis envoyée à ffmpeg.
Depuis la racine du dépôt, avec le venv du dépôt :

```bash
.venv/bin/python out/demo/build.py all
```

Les étapes, une par une (`build.py <étape>`) :

- `clips` : extrait les images utiles des shorts (cache dans `$SVI_TMP`, par défaut `/tmp/svi/demo_fr`) ;
- `narration` : écrit `narration_fr.json` ;
- `video 16x9` puis `video 9x16` : l'image seule (environ 10 min par format sur 4 cœurs) ;
- `audio` : musique + bruitages, et la voix si elle existe ;
- `final 16x9` puis `final 9x16` : assemblage, niveau ramené à −14 LUFS ;
- `gif`, `thumb`, `sheet` : aperçu, vignette, planche ;
- `stills 16x9 3.2 8.0 …` : images de contrôle à des instants donnés.

Le minutage (120 BPM, un temps = 0,5 s) et la géométrie des deux formats sont en tête de `build.py`.

## Voix off : l'emplacement est prêt, aucune voix n'est générée ici

1. Le texte et les créneaux sont dans `narration_fr.json` (12 lignes, débit ≤ 2,8 mots/s).
2. Déposer une ligne par fichier dans `out/demo/voice_fr/00.mp3` … `11.mp3` (recette du dépôt : un seul appel Gemini « Sulafat »,
   découpe par ligne, voir `out/report/notes/voix-lot2.md`).
3. Relancer `build.py audio` puis `build.py final 16x9` et `build.py final 9x16` : la musique baisse d'environ 9 dB sous la voix,
   `demo_*.mp4` reçoit la voix, `demo_*_novo.mp4` reste sans voix. Pas besoin de refaire l'image.

`audio` prévient si une ligne dépasse son créneau de plus de 0,6 s.

## Son

- **Musique** : synthétisée par code dans `build_audio.py` (numpy/scipy), calée sur le montage. Les 2,5 premières secondes
  sont une « musique de template » volontairement banale, qui déraille quand la carte change de style.
- **Bruitages** : uniquement les sons CC0 de `sfx/` (OpenGameArt : Kenney, bart, pyranostudios, Hazmat Harry,
  Cassie-OrbitGames, rubberduck, wobbleboxx ; auteurs et liens dans `sfx/credits.json`).
- **Brouhaha** du mur de shorts : les voix françaises déjà présentes dans `brouhaha/`, très bas.
- Le mix est limité puis normalisé à −14 LUFS (crête −1,5 dBTP).

## Règles tenues

- Chiffres : 18 identités, 21 déclinaisons, 45 shorts, juge à l'aveugle 18 groupes purs sur 18 (72 images sur 72), open source.
- Photosensibilité : aucun flash plein cadre ; le fond du carrousel glisse du clair au sombre une seule fois ; la carte qui
  change de style quatre fois par seconde occupe moins de 15 % de l'image.
- Zones sûres du 9:16 : rien d'important dans les 220 px du haut, les 320 px du bas ni les 120 px de droite.
