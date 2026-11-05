# Recette — un short `evenements` dans l'identité Carte Météo

Référence : `out/shorts/carte-meteo__evenements__28-juin-2019-46-degres-record-de-chaleur/` (15 s, D3.js + topojson-client + world-atlas, rendu 84,6 s = 18,8 s/100 images).

**Pour un short evenements (un record daté, une tempête, une canicule — pas de compte à rebours « J-N ») dans cette identité :**

- **Ouvrir par** (0–3,6 s) : la France entière, bandeau à onglet **rouge** (chaleur) ou bleu (froid, tempête) avec **la date en titre** (Space Grotesk 700 108 px) et l'enjeu en sous-titre ; une pastille « ? » reliée au lieu par un trait de rappel, dont l'anneau hésite entre orange et rouge (`mix` sinusoïdal) : le suspense est posé avant 0,5 s. Flux de vent cohérent avec l'épisode (ici, flux de sud entre une D ibérique et un A d'Europe centrale).
- **Structurer en** trois plans séparés par le `passage-du-front` (front **chaud** à demi-cercles rouges pour la chaleur ; départs ≈ 3,6 / 8,6 / 12,6 s) :
  1. **le contexte** (≈ 4–8,5 s) : zoom ×2,4 sur la région, l'ancien record dans une pastille orange (r 120) qui pope au passage du front puis compte jusqu'à sa valeur (`power2.out` 0,6 s) ; bandeau « L'ancien record » + date et lieu ;
  2. **l'événement** (≈ 9,5–12,5 s) : zoom ×2,6, l'ancien record pâlit à 55 %, la nouvelle pastille (r 128) compte de l'ancienne valeur à la nouvelle en 1,4 s, l'anneau passe de l'orange au rouge, puis la pastille se remplit de rouge (chiffre blanc ≥ 54 px gras, 4,67:1) avec un anneau d'onde 0,8 s et deux anneaux rouges plats ;
  3. **la chute** (≈ 13,5–15 s) : retour au plan large, les deux pastilles côte à côte, l'écart chiffré en titre (« +1,9 °C ») ; tenue ≥ 1,5 s.
- **Fermer par** la tenue ; CTA en voix ou dans `short.json` (« votre record à vous ? »).
- **Faits** : valeur, lieu (commune + département), date complète ; ancien record daté ; virgule décimale ; positions des communes à ≈ 1 km. Ne jamais faire passer le compteur pour une série horaire.
- **Ne pas** teinter la terre en orange ou rouge (voile radial testé : orange sur vert = olive « sale », mer beige) ; la chaleur se dit par les fronts chauds, les anneaux et la pastille pleine.
- Voix : 4 lignes, ≈ 2,8 mots parlés/s (les dates et décimales se lisent en toutes lettres). Son : `pad`, `whoosh` par front, `pop` + `tick` des compteurs, `impact` + `chime` sur la valeur record, `swell` final.
- Tokens : `out/identities/carte-meteo/tokens.json`. Code partagé : `src/meteo.js`.
