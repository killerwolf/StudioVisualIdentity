# Recette — short `enfants` en Tableau Craie

Référence : `out/shorts/tableau-craie__enfants__comment-une-graine-devient-un-arbre/` (Rough.js + GSAP, 15,5 s, 30 fps).

Pour un short **enfants** (6–10 ans) dans cette identité :

- **Ouvrir par (0–1,2 s)** : la question en Nunito 800 100 px sur 3 lignes courtes (dernière ligne dans la craie du héros, ici vert `#9BE58A`), soulignée à la craie (0,15–0,55 s) ; le héros (graine avec deux yeux et un sourire) **tombe** avec `bounce.out` 0,9 s pendant que le sol s'écrit (0,5 s). Son : `pop` à chaque rebond.
- **Structurer en 4 étapes numérotées de 2,3–2,6 s** (« 1. Elle boit », « 2. Les racines », « 3. La tige pousse », « Photosynthèse ») : en-tête Nunito 96 px qui se pose (0,25 s `power3.out`), un schéma Rough.js qui **s'écrit** (`stroke-dashoffset`, stagger 0,12–0,22 s) et un mot-clé Caveat 66–76 px. Le dessin **s'accumule** d'une étape à l'autre (l'enfant voit la plante grandir) ; un zoom lent 1,0 → 1,1 sur la terre pour les racines.
- **Pop d'émerveillement** : feuilles / fruits / couronne en `back.out(1.6–3)` 0,3–0,7 s, avec `pop` musicaux montants (A5 → F6).
- **Transition** : un seul **chiffon** (0,6 s) pour effacer l'échafaudage (soleil, flèches, légendes, tige) avant la métamorphose finale.
- **Fermer par** : le résultat (arbre) + une nouvelle graine qui tombe + « Et ça recommence ! » (boucle narrative), tenue ≈ 1 s ; `chime` final.
- **Tokens** : mêmes que l'explicatif (palette, Caveat/Nunito, grain 77, chiffon, music-box F majpent 92 bpm) → reconnaissable à l'aveugle.
- **Voix** : 7 phrases de 3–7 mots (Kore, ton enjoué), ≈ 2,6 mots/s.
- **Pipeline** : `node out/tools/render.mjs …/src/index.html --out /tmp/v.mp4 --duration 15.5` → `sound.py` → `assemble.py mux` (voir `src/README.md`).

> Voix réellement utilisée pour les shorts de preuve : Fish Audio « Arnold » (`d704cf8f1216490cbfbed89955f0e938`, `s2.1-pro`). Les noms Gemini ci-dessus sont des suggestions historiques de casting par ton.
