# Recette — short **abstrait** dans l'identité Labo Néon

Référence : `out/shorts/neon-lab__abstrait__champ-de-force-lucioles/` (12 s, boucle parfaite, twgl.js + OpenCV).

**Pour un short abstrait dans cette identité :**

- **Ouvrir par** (0–1 s) : le système déjà vivant à la frame 0, sur une impulsion (`pulse` : halo/taille ×1,35, décroissance exp 0,32–0,35 s), tag `LABO/0X · MOT` (JetBrains Mono 500, 54 px, cyan, pastille magenta) à 232 px, titre-chiffre Space Grotesk 700 118 px à 316 px (« **2 000** lucioles, un attracteur » : le chiffre en cyan).
- **Structurer en** : une seule boucle de **12 s** (4 mesures à 80 bpm) ; impulsions toutes les **1,5 s** ; caméra en orbite **±15° sinusoïdale** + respiration de dolly, toutes deux périodiques en T ; champ de force GLSL (`field.glsl.js`, `uLoop = (cos, sin)(2πt/T)`) ; une ligne de données mono lime à 1500 px (paramètres du système : `σ 10 · ρ 28 · β 8/3`). Couleur pilotée par la position (cyan ↔ magenta), lime pour ~9 % des particules.
- **Fermer par** : la boucle — frame T identique à frame 0, la couture tombe sur une impulsion. Technique : particules réparties sur une trajectoire pré-calculée, la particule i avance de K espacements en T, attributs périodiques de période gcd(K, N) ; son rendu sur 3 cycles puis tranche du cycle central (`loopslice.py`).
- **Post** : `neon_grade.py` (glow 0,55, aberration 0,0022, vignette 0,22) via `out/tools/slot.sh`.
- **Budget** : ≈ 55 s / 100 frames (twgl, 20 000 points + champ plein écran) + ≈ 32 s / 100 frames (OpenCV).
- **Voix** : 3 phrases maximum, calme (Achernar), une toutes les ~4 s.
