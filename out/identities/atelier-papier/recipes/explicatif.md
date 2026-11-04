# Recette — un short `explicatif` dans l'identité Atelier papier

Référence : `out/shorts/atelier-papier__explicatif__d-ou-vient-le-mot-sandwich/` (scène : `src/video.py`, moteur `out/shared/papier-moteur/`, thème `src/THEME`).

- **Ouvrir par** : Ouvrir par l'étiquette « D'OÙ ÇA VIENT ? · 01 », le mot entre guillemets en bande jaune et un post-it question à 0,5 s.
- **Structurer en** : Le mot reste en haut, réduit ; la carte de l'origine (nom, titre, eyebrow = pays et siècle) arrive sur la réplique ; la date de la première trace écrite en tampon rouge à la fin de la phrase.
- **Fermer par** : Laisser 1,5 s de silence sur le tampon avant l'écran de fin, ou finir sur une question au spectateur.
- **Écrire** : une `ep.replique("../voice_lines/NN.mp3", "texte exact")` par ligne de voix, une `ep.scene(…, rN.debut(-0.15))` par réplique, les pièces posées sur `rN.debut(+x)` ou `rN.fin(+x)` ; `video.py narration` écrit `narration.json`, `video.py images t…` des images de contrôle.
- **Reproduire** : `bash out/shorts/<dossier>/src/build.sh` (narration → vidéo voix comprise → stills).
- **Pièges** : le texte ne va jamais sur le tapis ; un titre de plus de 14 caractères par bande déborde à 96 px (passer à 86) ; l'écran de fin ajoute 3,2 s à la durée.
