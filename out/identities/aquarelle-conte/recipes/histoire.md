# Recette : short `histoire` en Aquarelle Conte

Référence : `out/shorts/aquarelle-conte__histoire__phare-d-alexandrie/` (16 s, graine 11, p5.js + Paper.js, preset pad).

Pour un short histoire dans cette identité :

- **Ouvrir par** « Il était une fois… » en surtitre (Nunito 600, 54 px, `#B2573E`) à 0,05 s, puis le nom du monument ou du personnage en display (Fraunces 700, 108 px, un mot en `#4E7FB8`) à 0,15 s. Le hook visuel commence dès la frame 0 : le monument se construit pierre par pierre (blocs Paper.js qui tombent de 160 px en outCubic, 0,03 s par pierre, 0,15 s par rang) sur un ciel de crépuscule en bandes (`band()`). Son : chime E6 et ticks légers sur les rangs.
- **Structurer en** 3 temps de ≈ 3 s, chacun = une date ou un chiffre en Fraunces 92 + une phrase en Nunito 58 :
  1. Origine (« Vers 280 av. J.-C. » + lieu et commanditaire).
  2. Apogée : `lavis-qui-s-ouvre` vers la nuit depuis la source de lumière (le feu), faisceau tournant et figurants (felouque). Une toise pointillée et une étiquette en cartouche papier donnent l'ordre de grandeur (« 100–130 m »).
  3. Chute : secousse de 7 px, puis les éléments tombent du haut vers le bas, en fonction pure de t (pas d'état), et finissent translucides dans la mer.
  Toujours formuler les faits avec prudence (« vers », « environ ») et ne jamais afficher un fait non vérifié.
- **Fermer par** l'héritage : `lavis-qui-s-ouvre` vers un matin (`bloomSoft`, 5 paliers, à cause du fort écart de valeur). Les **mêmes** pierres se réassemblent en un nouvel édifice (stagger 0,022 s, arc de 170 px, inOutCubic). Puis « Fin. » en Fraunces 92 à 14,3 s et `fondu-papier` de 0,8 s. Son : impact et thuds au séisme, swell au matin, chime D5 final.
- **Tokens** : `out/identities/aquarelle-conte/tokens.json`. Durée 15–16 s. Parallaxe ciel −10 / mer −20 / près −30 px.
- **Voix** : Aoede, ton d'album documentaire, 5 lignes, la dernière avant 15,6 s.
- **À éviter** : les cartes chiffrées denses, les visages de personnages historiques réels, les dates à la seconde près, les reconstitutions présentées comme exactes.
