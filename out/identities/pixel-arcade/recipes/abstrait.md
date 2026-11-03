# Recette — short `abstrait` en Arcade Pixel

Référence : `out/shorts/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper/` (15,0 s, p5.js, physique maison `ring.js`, graine 1007).

Pour un short abstrait dans cette identité :

**Ouvrir par** (0–1 s) — la mécanique déjà en mouvement :
- panneau-titre question Rubik Mono One 80 px (titre long, ≤ 12 caractères/ligne), mot-clé vert, même panneau que l'engagement (surface + bordure bleue + ombre dure) ;
- HUD `REBONDS 00` (Press Start 2P 56 px, label jaune) à y = 236 px ;
- la balle tombe déjà ; premier rebond ≤ 0,5 s (0,48 s ici) avec blip + onde + screenshake 4 px ; son « coin » à 0,05 s.

**Structurer en** (1 → ~12 s) — une règle simple, un compteur, une tension qui monte :
- une règle énoncée en mots-clés (« CHAQUE REBOND / ELLE GRANDIT », 0,8–5 s, `blink-in`) ;
- chaque événement physique **laisse une trace** : la tuile touchée prend la couleur suivante des 4 accents et le reste (l'anneau devient l'historique coloré de la partie), la balle grandit de 0,4 px logique, onde d'impact 10 frames, fantômes à alpha décroissant ;
- le décor tourne **par paliers** (1 tuile de 5° toutes les 3 frames), marqueurs de brèche jaunes clignotants 4 Hz ;
- son : un blip par rebond qui **monte** dans la pentatonique (2 octaves puis reboucle), coin tous les 10 rebonds, riser 1,5 s avant l'événement final (connu grâce à la pré-simulation) ;
- pré-simuler en Node (`simulate.cjs --scan`) pour placer l'événement final entre 11,4 et 12,4 s avec ≥ 24 rebonds.

**Fermer par** (~12 → 15 s) :
- l'évasion : screenshake 12 px / 6 frames, l'anneau **éclate** (chaque tuile part en ligne droite + gravité), « ÉVADÉE ! » Rubik 150 px vert en `blink-in`, glass + impact + coin ;
- `pixel-mosaic` 0,6 s (13,25–13,85 s) -> carte de fin identique à celle de l'engagement : résultat 120 px, 3 lignes de score (REBONDS / TAILLE / TEMPS) en stagger 0,12 s, ligne finale clignotante « ▶ RECORD ! » ;
- fin propre (pas de boucle : la croissance de la balle rend la boucle parfaite impossible sans tricher).
