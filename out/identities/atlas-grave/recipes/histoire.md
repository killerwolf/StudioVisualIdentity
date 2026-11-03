# Recette — un short `histoire` dans l'identité Atlas Gravé

Référence : `out/shorts/atlas-grave__histoire__premier-tour-du-monde-1519-1522/` (16 s, D3 + GSAP + pycairo).

**Pour un short histoire dans cette identité :**

- **Ouvrir par** (0–0,5 s) la planche titrée (en-tête Cinzel « PLANCHE N · VOYAGES », titre Cormorant 108 px sur deux lignes, filet or, bornes chronologiques Cinzel 700 56 px sanguine « 1519 – 1522 ») et une **carte plate équirectangulaire** (fenêtre x 76, y 640, 840×660, 6 px/degré à k = 1) déjà gravée, avec l'acteur posé sur son point de départ (caravelle pycairo 92 px) et la première légende datée (« SEPT. 1519 / Départ de Sanlúcar »).
- **Structurer en** étapes datées de **1,5–2,8 s** : la route se trace en pointillé sanguine derrière le navire (longitudes « déroulées » et carte répétée en tuiles pour un tour complet sans saut), la caméra suit le navire (moyenne glissante ±0,6 s, regard décalé de 12° vers l'avant) et **zoome** sur les lieux-clés (détroit k 1,75, Philippines k 1,45 ; 0,8–1,0 s `sine.inOut`). Chaque étape change la légende par la transition « encre-qui-sèche » (sortie 0,3 s, entrée 0,4 s `power2.out` + 12 px). Un **compteur visuel** (5 caravelles → 1, croix sanguine `power2.out` 0,4 s, *thud*) porte la tension sans texte long. L'événement dramatique reçoit un **sceau** sanguine (croix) avec *impact*.
- **Chute** (≈ 13,4 s) : l'arrivée, avec le chiffre-clé en grand (« 18 survivants », Cormorant 84 px).
- **Fermer par** (13,6–16 s) un recul en vue d'ensemble (k ≈ 0,36, la route entière lisible comme une boucle autour du monde) puis le **cartouche guilloché** posant un duel (« Magellan ou Elcano ? » + italique sanguine « qui mérite le nom du voyage ? »), tenu 1,4 s : fin propre.
- **Son** : `pad` ré dorien 80 bpm (identique à la géographie), *chime* à chaque date, *thud* à chaque perte, *riser → impact* pour la mort, *chime A6 + swell* au retour, *glass* au cartouche.
- **Voix off** : récit au passé simple/présent de narration, une phrase courte par étape (≤ 2,6 mots/s), dates laissées à l'écran pour ne pas surcharger la voix.
- Prudence : formuler les durées et effectifs avec « plus de », « environ » ; vérifier chaque date affichée.
- Tokens : `out/identities/atlas-grave/tokens.json`.
