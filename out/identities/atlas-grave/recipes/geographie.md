# Recette — un short `geographie` dans l'identité Atlas Gravé

Référence : `out/shorts/atlas-grave__geographie__plus-longs-fleuves-du-monde/` (15 s, D3 + GSAP + pycairo).

**Pour un short géographie dans cette identité :**

- **Ouvrir par** (0–0,5 s) la planche titrée : en-tête Cinzel 600 54 px sanguine « PLANCHE N · THÈME », titre Cormorant Garamond 700 108 px sur deux lignes (y 400/500), filet or + losange sanguine (y 544). Sous le titre, une **mappemonde NaturalEarth1** (fenêtre x 76, y 590, 840×470) dont les côtes s'encrent en 1,1 s (`pathLength=1`, `power1.out`), terres hachurées en 0,7 s, puis les objets du sujet (fleuves, frontières) tracés en bleu d'encre `#2D4A5A` en 1,0 s. Titre visible dès la frame 0 (opacité 0,35 → 1 en 0,5 s).
- **Structurer en** compte à rebours de 5 temps forts de **1,5 s** (2 temps à 80 bpm) : pour chaque rang, zoom cartographique (k 2,1, 0,7 s `sine.inOut`) centré sur l'objet, objet passé en sanguine (`#8C2F1B`), **sceau** à chiffre romain (`back.out(1.6)`, 0,35 s), et ligne de tableau qui s'encre sous la carte (chiffre romain Cinzel 54, nom Cormorant 62, mesure IBM Plex Mono 54 alignée à x = 904, ruban « déroulé » de longueur proportionnelle). Afficher dès 1,2 s les **rangs vides** (chiffres romains + pointillés à 40 %) pour créer le suspense ; remplir du bas (V) vers le haut (I) ; le n° 1 a un zoom plus fort (k 2,4) et une tenue de 1,8 s.
- **Chute** (≈ 10–13 s) : recul (k 1,3) et nuance factuelle — p. ex. échange en fondu des rangs disputés, cartouche guilloché (pycairo) avec la question en Cormorant 80 et la précision en italique sanguine 58.
- **Fermer par** (13–15 s) la relance dans le même cartouche (« ton pari en commentaire », italique bleu), recul lent k 1,16 sur 1,9 s, dernière 1,5 s tenue : fin propre, toute l'information lisible sur le dernier frame (bon poster).
- **Son** : `pad` ré dorien 80 bpm, *tick* de plume pendant le tracé, *thud + chime* à chaque sceau (notes montantes A5 → A6), *riser* avant le n° 1, *glass* au cartouche, *swell* final.
- **Voix off** : 1 phrase ≤ 1,4 s par rang (« Cinquième : l'Ienisseï. »), la mesure du n° 1 en toutes lettres, puis la nuance + la question.
- Tokens : `out/identities/atlas-grave/tokens.json`.
