# Vidéo démo « Caméléon » (français, 41 s)

- `demo_16x9.mp4` (1920×1080) et `demo_9x16.mp4` (1080×1920) : 41 s, 30 i/s, H.264 yuv420p, **voix off + son des shorts + musique + bruitages**, −14 LUFS.
- `demo_16x9_novo.mp4`, `demo_9x16_novo.mp4` : les mêmes sans la voix off, produits par `build.py final` (non versionnés).
- `demo_preview.gif` : 12 premières secondes, muettes, pour le README.
- `thumb/thumbnail_fr_1280.jpg` (et `_1920`) : la vignette.
- `planche-demo-fr.jpg` : planche de 12 images de la version 16:9.
- `narration_fr.json` : le texte de la voix off et son minutage réel ; `sound_fr.json` : les bruitages et les extraits de shorts posés.
- `voice_fr_raw/demo.mp3` : la voix brute (un seul fichier) ; `voice_fr/00.mp3` … `10.mp3` : une ligne par fichier.
- `eleven/brief.json` : le cahier des charges d'une musique et de dix bruitages externes (optionnels, voir plus bas).

## L'idée

La démo est un **caméléon** : elle prend tour à tour le fond, la police et la couleur de chacune des 18 identités, et sa matière
est faite des vrais shorts du dépôt, **qu'on entend aussi** : dès qu'un short est à l'écran, sa propre bande son entre en fondu.
Tout le texte à l'écran est en français, sans sous-titres incrustés : l'image suffit, et **c'est la voix qui cale le montage**.

## Déroulé

| Temps | Plan | Voix off |
| --- | --- | --- |
| 0 – 2 s | Un mur de cartes « template » toutes identiques défile, « ENCORE / LA MÊME / VIDÉO ? » claque sur chaque mot. | « Encore la même vidéo ? » |
| 2 – 3,5 s | Le mur s'éteint, une carte prend vie et change de style quatre fois par seconde (on entend le zapping). | « Et si la vôtre ne ressemblait à aucune autre ? » |
| 3,5 – 14,8 s | Carrousel en profondeur des **18 identités**, du plus sombre au plus clair : fond, halo, nom fantôme et titre prennent les couleurs et la police de chaque identité. De 7,8 à 11 s la voix se tait : on écoute les shorts. Les quatre dernières cartes arrivent sur leur nom : Gazette (11 s), pixel (12 s), néon (13 s), aquarelle (14 s). | « Voici dix-huit identités visuelles pour vos vidéos courtes. » puis « Gazette, pixel, néon, aquarelle… » |
| 14,8 – 16 s | Le carrousel fait un tour complet en accélérant (flou de filé). | « … à chacune sa signature. » |
| 16 – 19,5 s | Le même mur incliné que l'accroche, mais chaque carte est un vrai short : « 45 shorts, tous rendus par du code ». | « Quarante-cinq shorts le prouvent, tous rendus par du code. » |
| 19,5 – 23 s | « Un seul prompt. » L'agent tape le prompt et compare les 18 styles. | « Le plus simple ? Donnez un prompt à votre agent. » |
| 23 – 26 s | « Votre agent fait le reste. » ✓ style choisi (23 s), ✓ studio créé (24 s), l'épisode 1 se rend. | « Il choisit le style, crée votre studio… et réalise votre premier épisode. » |
| 26 – 32,5 s | Le drop : épisodes 1, 2, 3 (26, 28 et 30 s), trois vrais shorts de la même identité (Arcade Pixel), avec leur son. | « Puis le deuxième. Le troisième. À votre image. » |
| 32,5 – 36,5 s | Quatre panneaux, chacun dans une identité : 18 identités · 21 déclinaisons · 45 shorts · 100 % open source. | « Dix-huit identités. Quarante-cinq shorts. Tout est open source. » |
| 36,5 – 41 s | Carton de fin : le nom change de police sur chaque temps puis se pose, adresse du dépôt, « Donnez le prompt à votre agent. » | « Studio Visual Identity. À vous de jouer. » |

La scène du juge à l'aveugle (18/18) a été retirée à la demande de l'auteur : on voit déjà que les styles diffèrent.

## Fabrication

Pas de navigateur : chaque image est dessinée en Python (numpy, OpenCV, Pillow) puis envoyée à ffmpeg.
Depuis la racine du dépôt, avec le venv du dépôt :

```bash
.venv/bin/python out/demo/build.py all
```

Les étapes, une par une (`build.py <étape>`) :

- `clips` : extrait les images utiles des shorts (cache dans `$SVI_TMP`, par défaut `/tmp/svi/demo_fr`) ;
- `voice` : découpe `voice_fr_raw/demo.mp3` en `voice_fr/NN.mp3` ; `narration` : écrit `narration_fr.json` ; `brief` : écrit `eleven/brief.json` ;
- `video 16x9` puis `video 9x16` : l'image seule (environ 12 min par format sur 4 cœurs) ;
- `audio` : les quatre couches de son ;
- `final 16x9` puis `final 9x16` : assemblage, niveau ramené à −14 LUFS, limiteur de sécurité à −2 dB ;
- `gif`, `thumb`, `sheet` : aperçu, vignette, planche ;
- `stills 16x9 3.2 8.0 …` : images de contrôle à des instants donnés.

Le minutage (120 BPM, un temps = 0,5 s), la table `VOICE` et la géométrie des deux formats sont en tête de `build.py`.

## Voix off

- **Gemini « Puck »**, style « voix off de bande-annonce, très punchy » : **un seul appel**, les 12 lignes jointes par `<long pause>`
  (`voice_fr_raw/demo.mp3`, 39,84 s). `build.py` ne fait aucun appel réseau : il découpe ce fichier. Onze lignes sont utilisées :
  la sixième du fichier brut (« Testées à l'aveugle… ») est restée de côté avec la scène du juge.
- **Découpe** : silences (`ffmpeg silencedetect`, −38 dB, 0,25 s) + horodatage des mots par faster-whisper `small` (CPU, local,
  `uv run --with faster-whisper`). Les lignes découpées ont été retranscrites une par une : texte conforme (whisper entend
  « shirts » pour « shorts » et « prouve » pour « prouvent », rien d'autre).
- **Recalage** : dans `VOICE`, chaque ligne est une suite de morceaux (début et fin dans le fichier brut, instant dans la vidéo).
  Les pauses internes sont resserrées ou étirées pour que chaque mot tombe sur son image (« Gazette », « pixel », « néon »,
  « aquarelle » sur leur carte ; « crée votre studio » sur la coche ; « le deuxième », « le troisième » sur le changement d'épisode).
- Pour changer de voix : remplacer `voice_fr_raw/demo.mp3`, relever les silences, corriger `VOICE`, puis `voice`, `narration`,
  `audio`, `final`. Si les instants changent, refaire aussi `video`.

## Son

Quatre couches, mixées par `build_audio.py` :

- **Voix off**, devant, légèrement compressée.
- **Le son propre des shorts** (voix + musique de leur `short.mp4`) dès qu'ils sont à l'écran, avec fondus d'entrée et de sortie :
  zapping de la carte qui change de style, short de la carte au centre du carrousel (même horloge que l'image), six shorts à la
  fois sur le mur, les trois épisodes dans le téléphone, les quatre panneaux. Baissé de 13 dB sous la voix off, à plein niveau
  dans les silences ; chaque short est ramené au même niveau moyen.
- **Musique** synthétisée par code (numpy/scipy). Les 2 premières secondes sont une « musique de template » volontairement banale,
  qui déraille quand la carte change de style ; l'arpège se retire quand les shorts « parlent » ; un silence d'une double croche
  précède le drop des épisodes. Baissée de 7 dB sous la voix.
- **Bruitages** : les sons CC0 de `sfx/` (OpenGameArt : Kenney, bart, pyranostudios, Hazmat Harry, Cassie-OrbitGames, rubberduck,
  wobbleboxx ; auteurs et liens dans `sfx/credits.json`) et la synthèse de `out/tools/sound.py`. Montées (riser + bruit filtré +
  aspiration inversée) avant chaque révélation, impact + chute de basse sur le carrousel, le mur, « 45 shorts », le drop,
  chaque panneau et le coup final ; souffle et tic à chaque glissement du carrousel ; frappe au clavier et touche Entrée ;
  un peu de réverbération. La liste complète est dans `sound_fr.json`.

## Musique et bruitages externes (optionnels)

`eleven/brief.json` (écrit par `build.py brief`, en anglais pour un modèle de génération) décrit :

- **une musique** `eleven/music.mp3` : durée exacte, 120 BPM, grille des temps, et les sections avec leurs instants (musique de
  template qui casse, montée du carrousel, impact du mur, passage calme du prompt, drop des épisodes, quatre coups, coup final) ;
- **dix bruitages** `eleven/sfx/<nom>.mp3` (`whoosh`, `whoosh_long`, `impact`, `impact_light`, `riser`, `pop`, `click`, `ding`, `key`,
  `glitch`), chacun réutilisé à plusieurs instants, avec la liste de ces instants.

Dès qu'un fichier est présent, `build.py audio` le prend à la place du son de repli, aux mêmes instants : la musique est calée à
t = 0, ramenée au niveau de la musique synthétisée, baissée de 7 dB sous la voix off et de 3 dB sous le son des shorts ; les
bruitages ont leurs silences de début et de fin rognés. Fichier absent : musique synthétisée et sons CC0, comme aujourd'hui.
`sound_fr.json` indique ce qui a servi (`music`, `externalSfxUsed`). Il suffit ensuite de relancer `audio` puis `final`.

## Règles tenues

- Chiffres : 18 identités, 21 déclinaisons, 45 shorts, open source.
- Photosensibilité : aucun flash plein cadre ; le fond du carrousel glisse du sombre au clair, puis change deux fois à 2 s d'écart,
  en fondu (sombre à 12 s pour « pixel », clair à 14 s pour « aquarelle ») ; pendant le tour complet il glisse vers le sombre sans clignoter ; la carte qui change de
  style quatre fois par seconde occupe moins de 15 % de l'image.
- Pas de sous-titres incrustés.
- Zones sûres du 9:16 : rien d'important dans les 220 px du haut, les 320 px du bas ni les 120 px de droite.
