# Recette — un short `histoire` dans l'identité Cabinet de curiosités

Référence : `out/shorts/cabinet-curiosites__histoire__la-fourchette-a-fait-scandale/` (scène : `src/video.py`, moteur `out/shared/papier-moteur/`, thème `src/THEME`).

- **Ouvrir par** : Ouvrir par l'étiquette de série « L'HISTOIRE DE… · 01 » et le titre en trois bandes (papier / sujet / mot fort) déjà posés à 0 s, un tampon de date à 0,6 s.
- **Structurer en** : Une scène par moment de l'histoire : étiquette de lieu et de date, une carte (lieu, eyebrow = date) posée au début de la réplique, un post-it pour le détail surprenant, une bande rouge pour le chiffre clé.
- **Fermer par** : Fermer sur « Et vous ? » en bande bleue et deux post-it de vote ; l'écran de fin (3,2 s) suit.
- **Écrire** : une `ep.replique("../voice_lines/NN.mp3", "texte exact")` par ligne de voix, une `ep.scene(…, rN.debut(-0.15))` par réplique, les pièces posées sur `rN.debut(+x)` ou `rN.fin(+x)` ; `video.py narration` écrit `narration.json`, `video.py images t…` des images de contrôle.
- **Reproduire** : `bash out/shorts/<dossier>/src/build.sh` (narration → vidéo voix comprise → stills).
- **Pièges** : le texte ne va jamais sur le tapis ; un titre de plus de 14 caractères par bande déborde à 96 px (passer à 86) ; l'écran de fin ajoute 3,2 s à la durée.
