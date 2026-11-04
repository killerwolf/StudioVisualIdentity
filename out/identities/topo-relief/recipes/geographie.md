# Recette — short `geographie` dans l'identité topo-relief

Référence : `out/shorts/topo-relief__geographie__comment-mesure-t-on-l-everest/` (15 s, three.js + D3.js, 760,5 s de rendu).

**Pour un short géographie dans cette identité :**

1. **Ouvrir par (0–3,4 s)** la question en titre Inter 800 100 px (mot-clé en or `#E8C872`) **dès la frame 0**, coordonnées JetBrains Mono 54 px menthe en haut (y=236), et l'altimètre `ALT` 104 px qui compte de 0 à la valeur (format FR `d3.formatLocale`). En dessous, la maquette s'extrude (`rise` 0.12 -> 1 en 2.6 s) et les courbes `d3.contours` s'allument du bas vers le haut (`uLevel` 0 -> 1 en 3.1 s, inOutSine). Son : `riser` + `tick` puis `impact` quand la valeur est atteinte.
2. **Structurer en** 3–4 beats de 2,2–2,4 s numérotés par un kicker JetBrains Mono 700 54 px terre cuite (`01 / GNSS`, `02 / RADAR`, `03 / GÉOÏDE`), un titre de 1–2 lignes et un sous-titre mono 54 px menthe. **Un objet 3D par beat** (satellites + faisceaux pulsés, anneaux radar, nappe ondulée « NIVEAU 0 »), une **image clé drone** par beat interpolée en `glide` (azimut qui tourne de 0.3 rad, plongée 40–60°, plan rasant pour un niveau). Texte : fondu outCubic 0.3 s + 26 px de montée. Son : `whoosh` à chaque beat, `blip`/`chime` pour les objets.
3. **Fermer par (12,6–15 s)** la nuance (« la montagne bouge encore », effet exagéré signalé en muted `#9AA898`), un recul-plongée vers la vue large de la maquette, `thud` + `chime`, et une question d'engagement en légende.

Tokens : `tokens.json` (palette, Inter 800 / JetBrains Mono 500-700, `rise`, `glide`, fov 54°, brouillard 9–40). Voix off : Orus, une phrase de 5–7 mots par beat, posée 0,1 s après le kicker.
Pièges : satellites ou objets hauts qui montent dans le HUD (garder < 2,6 unités au-dessus du sommet) ; balise 3D projetée hors écran -> poser l'étiquette en position fixe.
