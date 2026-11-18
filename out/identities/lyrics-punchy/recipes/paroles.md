# Recette — short `paroles` en Lyrics punchy

Référence : `out/shorts/lyrics-punchy__paroles__claudes-plan/` (DOM + SVG par `render.mjs`, Anybody variable, 19,5 s, 30 i/s, 154,5 BPM, rendu 116,9 s, 20,0 s / 100 images). Moteur : `out/shared/lyrics-moteur/`.

Pour un short **paroles** (extrait de chanson, 15–40 s) dans cette identité :

- **Langue** : les paroles s'affichent dans la langue du morceau, jamais traduites (`--langue`) ; arabe : Noto Sans Arabic, de droite à gauche (spécifié dans `identity.md`, pas encore codé).
- **Préparer hors dépôt** : `~/git/StudioVisualIdentity-sources/lyrics-<morceau>/` avec l'audio (obtenu avec l'accord du propriétaire), `paroles.txt` (une ligne chantée par ligne, `# <section> <camaïeu>` en tête de section, `| carton +N` pour décaler un carton de N temps) et les mots horodatés (`uv run --with faster-whisper --with "av<16"`, `word_timestamps=True`, langue fixée). Le tempo (`bpm`, `t0`) se mesure à part et se confirme à l'oreille.
- **Caler** : `python3 out/tools/lyrics_align.py --paroles … --mots … --out lyrics.json --bpm … --t0 … --duree … --titre "<TITRE>"` ; il aligne le texte exact sur Whisper, ramène les mots sur la croche (70 ms), regroupe les petits mots, coupe les lignes de plus de 6 unités, pose les accents (un `coup` par mesure), choisit un déclencheur par ligne (priorité, ≥ 2,5 s entre débuts, jamais deux visuels) et **valide** les règles. Corriger ensuite à la main dans `lyrics.json` (`source: "main"`), jamais en relançant par-dessus.
- **Ouvrir par (0–0,5 s)** : la première unité déjà en `coup` à l'image 0 ; si le morceau commence sans voix, le titre en 2 rangs, un mot par mesure (`--titre`). Camaïeu `nuit`.
- **Structurer par sections** :
  1. une section = un camaïeu (`lagon` couplet, `braise` tension, `nuit` refrain), `chute-de-pile` sur le temps qui précède le premier mot de la section (≥ 1,6 s entre deux) ;
  2. une ligne = 1 à 6 unités sur 1 à 3 rangs justifiés à 876 px ; `empilement` à la ligne suivante, 4 lignes de mur au plus ;
  3. un carton par ligne au plus, sur le mot qui porte l'image (`triggers.json`), 4 temps, sortie sur un temps ; ≤ 50 % du temps avec un visuel.
- **Fermer par** : la dernière ligne vive et son carton tenus jusqu'à la dernière image ; pas de noir.
- **Contrôler** : `node out/tools/lyrics_audit.mjs <scene.html> [--query data=…]` (zones sûres image par image, tailles ≥ 120 / 56 px, carton qui ne couvre aucune ligne lisible du mur) ; puis stills, rendu, piste silencieuse en `yuv420p`, `check.py`.
- **Écouter** : rendre la version aux vraies paroles hors dépôt (lien symbolique dans `tmp/` du short, ignoré par git, `--query data=../tmp/lyrics.json`), poser l'audio et un clic à 4 temps par ffmpeg (`apercu_avec_son.mp4`, `apercu_metronome.mp4`) : les entrées d'accent 1 et 2 doivent tomber sur le clic.
- **Tokens** : `out/identities/lyrics-punchy/tokens.json`.
- **Pièges** : `render.mjs` ne sert que le dépôt (lien symbolique pour les données externes) ; il sort du `yuvj420p` refusé par `check.py` ; une ligne de plus de ~30 caractères tombe à 56 px dans le mur ; Whisper étale les mots qui suivent un silence (le « I » à 5,62–7,42 s du morceau test) ; un mot corrigé (« Plano » → « plan mode ») prend l'empan de Whisper réparti au prorata des lettres (`source: "reparti"`).
