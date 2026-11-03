# Journal studio — aquarelle-conte

- 2026-11-03T21:09:53Z START Phase 2. Lu STUDIO_BRIEF, facts, fiche directions.json, affiche + src.
- 2026-11-03T21:09:53Z DECISION architecture : module partagé aq.js (copié à l identique dans les deux src/) = moteur de lavis p5 (pré-rendu dans p5.Graphics au ready, composé par frame via drawingContext.drawImage), transition signature « lavis qui s ouvre » (clip polygone déformé 3 paliers), grain papier calculé en JS une fois (canvas soft-light), Paper.js sur un 2e canvas pour personnages/bâtiments vectoriels (copies jitterées translucides = vecteur aquarelle).
- 2026-11-03T21:09:53Z DECISION mise en page « page d album » commune : illustration 0–1080 px, texte sur papier crème 1150–1560 px (toujours AA).
- 2026-11-03T21:24:49Z ECHEC/FIX enfants rendu 1 (507 s, 112.8 s/100 f, CPU partagé) : bande de 15-20 px à droite non couverte en fin de travelling (calque près 1180 px, décalage -120). Calques far/near portés à 1240 px ; re-rendu complet (correction réelle). Texte final avancé à 12.0 s.
