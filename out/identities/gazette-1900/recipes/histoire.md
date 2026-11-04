# Recette — un short `histoire` dans l'identité Gazette 1900

Référence : `out/shorts/gazette-1900__histoire__1789-en-20-secondes/` (18,75 s, GSAP + OpenCV, graine 1789).

**Pour un short histoire dans cette identité :**

- **Ouvrir par** une une-titre (4 temps = 1,875 s à 128 bpm) déjà en plein tourniquet à la frame 0 (rotation −300°, échelle 0,28 → posée à 0,5 s), date-titre géante Playfair 900 300 px (« 1789 »), sous-titre promesse (« EN 20 SECONDES »), gravure emblème, tampon « Édition spéciale » à 0,62 s.
- **Structurer en** une une par date (6 temps = 2,8125 s) : tourniquet 0,55 s `power3.out` → date-titre 230 px ajustée à 900 px + titre d'événement 84 px sur 2 lignes → gravure en hachures 894×430 (Ken Burns ×1,07) → légende italique 54 px → dépêche tapée 34 car/s à +0,62 s → tampon mot-clé (`power4.in` 0,16 s) à +1,5 temps → zoom brusque ×1,1 à +4 temps. Maximum 5 dates pour rester ≤ 20 s.
- **Fermer par** une une-récapitulatif (6 temps) : liste des dates tapée à 70 car/s (stagger 0,26 s), dépêche-question « VOTEZ — quelle date ? », tampon signature « Au prochain numéro » à +4 temps, tenue 0,9 s.
- **Tokens** : `out/identities/gazette-1900/tokens.json` (palette papier/encre/rouge, Playfair/DM Serif/IBM Plex Mono, bpm 128).
- **Post** : `post.py video raw.mp4 video.mp4 --seed 1900 --flash <débuts des unes>` (via `out/tools/slot.sh`).
- **Son** : `gen_sound.py` (preset `pulse` mineur, whoosh au tourniquet, thud à la pose, impact au tampon, ticks de machine à écrire, click au zoom).
- **Voix** : Orus, une phrase de 5–7 mots par une, démarrée 0,1–0,2 s après le tourniquet.
- **Pièges** : silhouettes inventées uniquement ; jour de la semaine retiré de la ligne méta (débordement) ; `<br>` explicite dans les titres.

> Voix réellement utilisée pour les shorts de preuve : Fish Audio « Arnold » (`d704cf8f1216490cbfbed89955f0e938`, `s2.1-pro`). Les noms Gemini ci-dessus sont des suggestions historiques de casting par ton.
