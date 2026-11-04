# Recette — short `evenements` dans l'identité Cosmos Doc

Référence : `out/shorts/cosmos-doc__evenements__voyager-1-a-un-jour-lumiere/` (15 s, 4 plans, three.js + GSAP, `src/cosmos.js`).

**Pour un short événement dans cette identité :**

- **Ouvrir par** (0–4,45 s) l'objet de l'événement à l'image dès la frame 0 en vue 3/4 arrière (jamais de face : une parabole de face devient un disque illisible), soleil = étoile flare haut-gauche (`flare.set(170,300,.95,.62)`), tag `COSMOS · ÉVÉNEMENT`, **nom en Bebas 230** à y=1110 + promesse en Bebas 104 sur 2 lignes (mot-clé ambre), filet ambre à 0,9 s. Dolly-in 1,2 u.
- **Structurer en** trois plans séparés par des **dip-to-black 0,6 s** (4,15 / 8,0 / 12,45) :
  1. **le contexte daté** (4,45–8,3 s) : recul de 5 u qui révèle l'échelle (bord ambré de l'héliosphère), deux blocs « étiquette glacier Bebas 60 / valeur Bebas 104–124 » (date de lancement en haut, jalon en bas) ;
  2. **la mesure** (8,3–12,75 s) : plan large fixe, distance en haut, **compteur GSAP** (proxy 0→24 linéaire, 3,2 s) en Bebas 250 en bas, synchronisé avec un point de lumière glacier à longue traîne qui rejoint le point bleu pâle (qui pulse à l'arrivée) ; 24 `tick` dans le son ;
  3. **la chute** (12,75–15 s) : retour au gros plan, l'objet s'éloigne de 2,6 u dans le noir, étiquette **datée prudemment** (« VERS FIN 2026 ») + chiffre-titre Bebas 156 ambre + ligne Inter.
- **Fermer par** une tenue en mouvement (l'objet continue de s'éloigner), `impact` à 13,0 s, `chime` à 13,45 s, drone qui s'éteint en 0,8 s ; pas de boucle.

Règles : dates futures toujours au conditionnel visuel (« vers », « environ ») ; une phrase de voix off par plan (Charon, lente) ; tokens dans `identities/cosmos-doc/tokens.json`.
