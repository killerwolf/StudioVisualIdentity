# Journal studio swiss-data (Grille Suisse)

- 2026-11-03T21:09:03Z — démarrage Phase 2. Lecture brief, facts, fiche, poster. Plan : 2 scènes HTML D3 (SVG, échelles, d3-geo projection+graticule) + GSAP (timeline seek). Module partagé grille.js copié dans chaque src/ (tokens identiques).
- 2026-11-03T21:12Z — geographie : stills revus (2 itérations). Corrections : états initiaux DOM (opacity 0) car immediateRender:false ne pose pas le "from" avant le début du tween quand on seek directement ; "%" en tspan séparé 110 px (le "18 %" 200 px chevauchait le label) ; labels "vivent / en Asie|Afrique" homogènes.
- 2026-11-03T21:15Z — geographie : rendu complet 450 frames en 61,5 s (13,7 s/100 frames). Mux OK, 3 frames finales vérifiées, check.py OK.
- 2026-11-03T21:17Z — evenements : kicker "01 · COMPTE À REBOURS" chevauchait la date à droite -> "01 · DÉCOMPTE" ; "Espagne (Cadix)" trop large pour la colonne -> "Espagne" + label "Cadix" sur la carte.
- Décision : carte d3-geo sans données téléchargées : projection équirectangulaire + graticule générés par d3, 10 points lon/lat saisis à la main le long de la ligne de centralité (approximatifs, signalés comme tels).
- Décision : narration — Orus (documentaire) pour geographie, Charon (grave, compte à rebours) pour evenements. "272" se prononce en 3 mots : ligne 1 de l'éclipse à ~2,9 mots/s parlés, accepté (3,1 s).
- Décision : son commun preset pulse 120 bpm (D mineur geo / A mineur éclipse), même grammaire SFX (whoosh+thud par volet) -> reconnaissable à l'aveugle. mksound.py calcule les instants des ticks à partir des easings GSAP.
- 2026-11-03T21:20Z — evenements : rendu complet en attente de slot CPU (4/4 occupés par les autres studios).
- 2026-11-03T21:21Z — Phase 3 rédigée pendant l'attente de slot : identity.md, tokens.json, recipes/{geographie,evenements}.md, cartes D3/GSAP en brouillon. poster.jpg = frame 6,2 s du short geographie (unit chart + 59 %).
- 2026-11-03T21:32Z — evenements : rendu complet 450 frames en 92,3 s (20,5 s/100 frames ; ~8 min d'attente de slot avant démarrage). Mux OK, 4 frames finales vérifiées, check.py OK.
- 2026-11-03T21:32Z — contact-sheet.jpg (8 frames des 2 shorts finaux). Fin de mission. Temps réel total ≈ 25 min (dont ~8 min d'attente CPU). Aucun échec de librairie ; un seul rendu complet par short.
