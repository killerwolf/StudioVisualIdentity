# Recette — short `engagement` en Arcade Pixel

Référence : `out/shorts/pixel-arcade__engagement__quelle-bille-gagne-la-course/` (16,0 s, Matter.js + p5.js, graine 17).

Pour un short engagement dans cette identité :

**Ouvrir par** (0–2,4 s) — un pari explicite, visible dès la frame 0 :
- panneau-titre question en Rubik Mono One 104 px (surface `#1D1740`, bordure 8 px bleue `#4FB3FF`, ombre dure 16 px), mot-clé en vert `#3CF2A0` ;
- consigne « PARIE SUR TA COULEUR ▶ » en Press Start 2P 56 px dans un second panneau (bordure rose), flèche clignotante 4 Hz ;
- les 4 « joueurs » déjà en place (ROSE / VERTE / JAUNE / BLEUE = les 4 accents), flèches de couleur clignotantes au-dessus ;
- son « coin » à 0,05 s ; compte à rebours 3-2-1-GO en Rubik 240 px jaune, `pop-scale` 3 paliers, **sur les temps à 125 bpm** (0,96 / 1,44 / 1,92 / 2,40 s) ; à GO, le titre sort en `step-slide-out` (0,4 s, 6 paliers) + screenshake 8 px.

**Structurer en** (2,4 → ~12 s) — la simulation joue seule, lisible en plan fixe :
- pré-simuler en Node (`simulate.js --scan`) : vainqueur entre 11,2 et 13,2 s, dernier ≤ 14,6 s, écart 1er–2e minimal, ≤ 2 nudges, plusieurs changements de leader ; geler la graine ;
- HUD à y = 236 px : `TIME 09.43` (label jaune) + 4 cases de classement qui se remplissent à chaque arrivée (case n°1 bordée de jaune) ;
- feedback de chaque collision issu de la physique : picot allumé 9 frames, étincelles 2×2, blip dont la hauteur = la couleur (E5/G5/A5/C6), clic sur choc entre billes, flèche blanche clignotante au-dessus du leader ;
- voix off dans les creux : après GO, au changement de leader.

**Fermer par** (~12 → 16 s) :
- arrivée serrée -> bannière `PHOTO FINISH !` + écart (« +0.10 S ») en `blink-in` (12 Hz, 0,3 s), coin aigu C7 + impact sur le 1er ;
- `pixel-mosaic` 0,6 s (13,95–14,55 s, whoosh) -> carte de fin : « BLEUE GAGNE ! » 120 px dans la couleur du vainqueur, classement 4 lignes (rang, nom coloré, temps) en stagger 0,12 s, puis CTA « TU AVAIS PARIÉ SUR QUI ? » + « ▼ COMMENTE ▼ » vert clignotant 4 Hz ;
- pas de boucle : fin propre sur la carte (≥ 1,5 s de lecture).

## Variante « territoire » (PixiJS)

Référence : `out/shorts/pixel-arcade__engagement__quelle-couleur-conquiert-l-ecran/` (15,5 s, PixiJS + automate `conquest.js`, graine 175).

- **Ouvrir par** le même hook et le même compte à rebours (0,96 / 1,44 / 1,92 / 2,40 s) : titre 4 lignes Rubik 88 px « QUELLE COULEUR CONQUIERT L'ÉCRAN ? », panneau « PARIE SUR TA COULEUR ▶ », les 4 couleurs en germes de 3×3 cellules dans les coins avec flèches clignotantes. Le HUD affiche déjà les 4 pourcentages (00 %) dans leur couleur.
- **Structurer en** : expansion (2,4 → 5,7 s, l'écran se remplit), bannière `BATAILLE ! / ÉCRAN PLEIN` en `blink-in`, puis bataille aux frontières jusqu'au gel à 12,0 s. Le HUD montre les % entiers en direct, une barre empilée des 4 parts au-dessus du terrain et un soulignement jaune sous le leader. Les poussées (force 5) font clignoter le cadre et le % de la couleur à 12 Hz pendant 0,5 s. Son : le leader « chante » une note sur chaque temps, coin à chaque changement de leader.
- **Pré-simuler** (`simulate.cjs --scan`) : écran plein entre 4,5 et 7 s, au moins 3 changements de leader après le plein, écart final < 1,2 %, aucune couleur sous 8 %.
- **Fermer par** : gel à 12,0 s avec impact + coin, bannière `PHOTO FINISH ! +0.19 %`, `pixel-mosaic` 13,3–13,9 s, puis la carte de fin standard (« ROSE GAGNE ! », 4 lignes avec les % au centième, CTA « TU AVAIS PARIÉ SUR QUI ? ▼ COMMENTE ▼ »).
