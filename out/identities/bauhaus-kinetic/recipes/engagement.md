# Recette — short engagement dans l'identité Bauhaus Cinétique

Référence : `out/shorts/bauhaus-kinetic__engagement__trouve-l-intrus/` (14 s, rendu 133 s sous charge). Code : `src/index.html` + `src/bk.js` (identique au short explicatif).

**Pour un short engagement dans cette identité :**

- **Ouvrir par (0–1,5 s)** : le défi en Unbounded 800 100 px sur 2 lignes (« Trouve / l'intrus », mot-clé en rouge), entrée `x −80 -> 0` stagger 90 ms dès t = 0 ; la grille de jeu (5×6 tuiles de 150 px, joints 16 px) pop en stagger 40 ms depuis le centre (`stagger(40,{grid:[5,6],from:'center'})`, `outBack(1.6)`) ; badge de compte à rebours (rayon 100 px, en haut à droite, x ≤ 940) en snap. Tout est lisible avant 0,8 s.
- **Structurer en** :
  1. **Attente (1,5–6,5 s, 5 s pile)** : à chaque seconde le badge se morphe (flubber, 280 ms `outBack`) cercle -> carré -> triangle -> hexagone -> cercle en changeant de couleur et de chiffre ; 5 cases sous la grille se remplissent ; une vague de respiration (échelle −6 %) traverse la grille à chaque seconde pour qu'aucune frame ne soit figée. SFX tick à chaque seconde, riser sur la dernière.
  2. **Révélation (6,5–9 s)** : impact ; les autres tuiles s'atténuent à 0,22 en stagger 35 ms **depuis l'intrus** (`from: index`) ; l'intrus grossit ×1,3 avec un cadre encre 12 px en snap-90 ; pastille noire « tourné de 90° » ; puis l'intrus se remet droit (rotation −90°, `outBack(2)`, 500 ms) = l'explication en geste.
- **Fermer par (9–14 s)** : grid-wipe (coupe à 9,525 s), CTA « T'as trouvé / en combien ? » (92 px) et 4 réponses en formes primaires : 4 carrés pop en stagger 120 ms puis se morphent (flubber 600 ms) en cercle rouge « 1 s », carré jaune « 3 s », triangle bleu « 5 s », hexagone encre « raté » ; « Réponds en commentaire » (56 px) à +1,5 s ; tenue 3 s avec un léger balancement (±3°). Fin propre.
- **Son** : même lit `pluck-arp` 120 bpm que l'explicatif ; pops sur les staggers, ticks au compte à rebours, impact + chime à la révélation, whoosh + thud au wipe.
- **Voix** : Fenrir, tutoiement, ne compte que « trois, deux, un » ; question CTA répétée à l'oral.
- **Tokens** : `out/identities/bauhaus-kinetic/tokens.json`. Pour varier le jeu : changer la différence de l'intrus (rotation 90°, couleur du point, miroir) et l'index (`SEED`), garder le motif de couleurs `(i + 2j) mod 4`.
