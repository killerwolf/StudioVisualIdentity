# Recette : short `enfants` en Aquarelle Conte

Référence : `out/shorts/aquarelle-conte__enfants__ou-vont-les-etoiles-le-jour/` (15 s, graine 7, p5.js + Paper.js, music-box).

Pour un short enfants dans cette identité :

- **Ouvrir par** une page déjà peinte à la frame 0, avec un événement visuel avant 0,25 s (étoile filante, battement d'ailes, feuille qui tombe). Le surtitre `Histoire du soir` (Nunito 600, 54 px, `#B2573E`) arrive à 0,05 s, puis la question de l'enfant en display (Fraunces 700, 108 px, interlettrage −2 px, un mot en `#4E7FB8`) à 0,15 s, avec l'entrée « encre qui s'imbibe » (0,6 s outCubic). Le personnage inventé cligne des yeux vers 1,2 s. Son : chime E6 sur l'événement du hook.
- **Structurer en** 3 temps de 3–3,5 s :
  1. Le phénomène (ex. le Soleil se lève). Transition `lavis-qui-s-ouvre` (1,2 s) depuis la source de lumière, puis `fondu-de-ciel` (2 s).
  2. La révélation avec un geste emphatique `outBack` : loupe magique (le ciel de nuit clippé dans le cercle), pointillés Paper.js en stagger 0,09 s. Titre Fraunces 92 « Elles sont toujours là ! ».
  3. L'explication en une phrase de 7–8 mots (Nunito 58, 2 lignes), scientifiquement exacte.
  Le personnage suit l'action du regard (pupilles Paper.js orientées vers l'objet).
- **Fermer par** le retour au calme : `lavis-qui-s-ouvre` vers la nuit, réapparition des étoiles et des étincelles, puis les paupières qui se ferment en 1,5 s inOutSine. Ensuite « Bonne nuit, <prénom>… » (Fraunces 92) et `fondu-papier` de 0,8 s. Son : swell à chaque lavis, chime F5 final.
- **Tokens** : `out/identities/aquarelle-conte/tokens.json` (palette, Fraunces/Nunito, outCubic/inOutSine/outBack, safeArea 220/320/120). Mise en page « page d'album » : illustration 0–1090 px, texte à x = 64 entre 1150 et 1560 px.
- **Voix** : Aoede, chuchotée et lente, 6 lignes de ≤ 3,1 s, ≤ 2,6 mots/s.
- **À éviter** : la peur, la vitesse, plus de 2 blocs de texte, les animaux dans un comportement faux présenté comme un fait (rester dans le registre du conte).
