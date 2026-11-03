# Recette — un short `geographie` dans l'identité Grille Suisse

Référence : `out/shorts/swiss-data__geographie__ou-vivent-8-milliards/` (15 s, D3.js + GSAP, rendu 61,5 s).

**Pour un short geographie dans cette identité :**

- **Ouvrir par** (0–3 s) : le chiffre-monde géant en rouge Archivo Black (`display`, 780 px) qui **roule** dès la frame 0 (compteur `power2.out` 0,9 s, un `tick` par unité) + le titre-question en Inter 800 122 px révélé par `wipe-ligne` (expo.out 0,6 s, stagger 0,08 s). Kicker `01 · MONDE`, repère `SOURCE · ANNÉE` à droite. À 1,6 s, une barre empilée 48 px annonce la répartition (teaser de la suite).
- **Structurer en** deux rubriques de 5 s séparées par le `volet-rouge` (lancé à 3,0 s et 8,0 s, coupe à 3,475 / 8,475) :
  1. `02 · CONTINENTS` — unit chart D3 (1 carré = 100 millions ; 10 colonnes, carrés 76 px, stagger 0,017 s, entrée depuis le centre `expo.out` 0,4 s), puis lecture chiffrée en bas (Archivo Black 200 px, baseline 1590, label à col 6,2) : 59 % Asie, `swap-lecture` vers 18 % Afrique en bleu avec le reste atténué à 18 %.
  2. `03 · PAYS` — classement en barres (rail `#E7E2D7` 34 px, n° 1 en rouge, `expo.out` 1,0 s, stagger 0,12 s), valeurs alignées à x = 960.
- **Fermer par** (11–15 s) : la barre n° 2 passe au rouge, le chiffre-synthèse « 1/3 » en lecture basse + **push-in** ×1,08 sur 3 s `sine.inOut`, tenue jusqu'à 15 s. CTA en voix : « devine le 6e en commentaire ».
- Son : `pulse` 120 bpm, `impact` au hook, `whoosh`+`thud` à chaque volet, `pop` par groupe d'unités, `blip` par barre, `chime` sur la chute.
- Tokens : `out/identities/swiss-data/tokens.json`. Données arrondies à la source (ONU WPP), jamais plus de 2 décimales.
