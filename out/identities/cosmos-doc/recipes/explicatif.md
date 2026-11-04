# Recette — short `explicatif` dans l'identité Cosmos Doc

Référence : `out/shorts/cosmos-doc__explicatif__pourquoi-venus-plus-chaude-que-mercure/` (15 s, 3 plans, three.js + GSAP, `src/cosmos.js`).

**Pour un short explicatif dans cette identité :**

- **Ouvrir par** (0–4,45 s) le sujet en gros plan dès la frame 0 (planète en croissant/gibbeuse, centre y≈620 px, rayon ≈430 px), soleil hors champ haut-gauche (`flare.set(150,330,1.0,1.0)`), tag ambre `COSMOS · ÉPISODE NN` (Bebas 54, tracking 0,7→0,3 em, t=0), **titre-question** Bebas 118 px sur 3 lignes à y=1140 (mot-clé en ambre, fade-tracking 0,9 s dès t=0,05), filet ambre 150×3 à t=0,7. Dolly-in 1 u inOutSine. Son : `impact` + `swell` à 0, `chime` à 0,75.
- **Structurer en** deux plans de comparaison séparés par des **dip-to-black 0,6 s** (4,15→4,75 et 8,0→8,6) :
  1. le contre-exemple (4,45–8,3 s) : en-tête Bebas 150 (nom) + ligne Inter 56 (distance), bloc bas en deux colonnes « étiquette Bebas 58 / valeur Bebas 150 » ambre vs glacier, puis la **cause** en Bebas 96 + ligne Inter ; une animation de mécanisme (photons `Motes` qui repartent) ;
  2. le sujet (8,3–15 s) : même en-tête, puis le mécanisme inverse (photons piégés entre sol et atmosphère, marche aléatoire 1,25 u/s) + la cause chiffrée (« Atmosphère de CO₂ » / « 92 fois la pression terrestre »).
  Une phrase de voix off par plan (≤ 2,6 mots/s), textes = noms + chiffres seulement.
- **Fermer par** (11,55–15 s) : sortie des textes, **rampe de 3 s** (émissif 0→0,95, atmosphère crème→orange, `night` 0→0,85) et **chiffre-choc** Bebas 300 ambre en haut (y=236), « Jour et nuit » Bebas 120 + ligne Inter glacier en bas ; impact à l'arrivée du chiffre, dolly continu jusqu'à la dernière frame (pas de figé), pas de boucle.

Tokens : `identities/cosmos-doc/tokens.json` (sine.inOut partout, fov 36, bloom 0,62/0,7/0,78, grain 0,028, vignette 0,38). Musique : `drone` 64 bpm, mineur.
