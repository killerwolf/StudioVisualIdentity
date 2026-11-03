# Recette — short « abstrait » dans l'identité Chrome Liquide

Référence : `out/shorts/liquid-chrome__abstrait__quatre-peintures-mpm/` (Taichi MLS-MPM + OpenCV, 14 s, 420 frames).

Pour un short **abstrait** dans cette identité :

- **Ouvrir par** (0–1 s) : une goutte de matière déjà en chute à la frame 0 (spawn à y ≈ 830 px, vy = −0,5), légende Inter 500 54 px `#C8D3FF` « MATIÈRE · FLUIDE » + titre Syne 800 92 px sur 3 lignes avec **un** mot en dégradé chrome (overlay `o1.png`, fondu-chrome 0,45 s, visible dès 0,3 s). Impact sourd (`thud` + `glass`) à l'atterrissage (~0,6 s).
- **Structurer en** :
  1. 0–5,7 s : quatre chutes régulières, une par accent (`#C8D3FF`, `#FF9AE8`, `#7CF7E4`, `#FFE29A`), stagger 1,55 s, chacune annoncée par un `whoosh` et ponctuée d'un `thud`+`glass` montant (D5, F#5, A5, C#6 — gamme lydienne de ré).
  2. 6,6–10,8 s : deuxième carton « …et se mélangent. » ; tourbillon doux (force tangentielle gaussienne, 7,2–10,6 s, intensité sin²) et diffusion de couleur via la grille (taux 0 → 0,0016/sous-pas en 2 s) ; `swell` long.
  3. 11,3–14 s : la matière se pose, carton final « Hypnotique. » (un seul mot, dégradé), `chime` grave-aigu.
- **Fermer par** : la matière encore vivante (pas de fondu au noir — le fond sombre déclencherait `blackdetect`), dernier carton tenu 2,5 s ; la fin peut boucler visuellement sur un verre plein.
- **Tokens** : fond `#0B0B10` + halos, table `#1A1A24`, verre liseré chrome `#DBE3FF`, shading OpenCV (spéculaire n=90 ×1,25 + lustre n=14 ×0,22, env néon, Fresnel (1−n_z)²), caption y = 232, titre y = 306, x = 72.
- **Paramètres MPM** : grille 90×196 (dx = 1/160 = 12 px), dt = 1e-4, 80 sous-pas/frame, E = 600, μ = 0,05, gravité 20, 4 × 6 000 particules ; splat bilinéaire en 540×960, flou σ = 2, seuil densité 0,12–0,32.
- **Coût mesuré** : 443,7 s pour 420 frames (105,6 s/100 frames : simulation 332,7 s + ombrage 106,1 s), 1 thread, lancé via `out/tools/slot.sh`.
