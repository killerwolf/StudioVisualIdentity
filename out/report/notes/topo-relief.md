# Journal — studio topo-relief (Phase 2/3, production tardive)

- 2026-11-04 00:25 UTC — Démarrage. Lu STUDIO_BRIEF, facts.md, fiche directions.json, affiche Phase 1 (réutilisée : heightmap ridged + d3.contours -> texture + relief three.js en plongée).
- 00:28 — Décision : signature visuelle = **maquette en relief découpée** (bloc extrudé avec flancs striés, posé sur une grille menthe) + **courbes de niveau qui s'allument en montant** (shader onBeforeCompile : uLevel balaie la hauteur, bande de scan menthe). Distinct d'atlas-grave (carte plate parchemin) et de neon-lab (néon noir) : fond vert forêt, lueur cuite dans la texture (shadowBlur canvas) et pas de bloom (UnrealBloom = 183 s/100 f mesuré par neon-lab).
- 00:28 — Décision : moteur commun `topo.js` (copié à l'identique dans les deux src/) pour garantir la cohérence (mêmes tokens, même shader, même HUD altitude JetBrains Mono).
