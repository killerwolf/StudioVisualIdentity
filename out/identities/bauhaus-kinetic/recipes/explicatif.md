# Recette — short explicatif dans l'identité Bauhaus Cinétique

Référence : `out/shorts/bauhaus-kinetic__explicatif__abeilles-hexagones/` (16 s, rendu 135 s sous charge). Code réutilisable : `src/bk.js` (tokens, grille, géométrie, grid-wipe) + `src/index.html` (structure de timeline).

**Pour un short explicatif dans cette identité :**

- **Ouvrir par (0–2,4 s)** : la grille 6×10 se dessine (500 ms `outQuad`), l'objet du sujet pop en stagger 60 ms (`outBack(1.6)`) dès t = 0, la carte de titre blanche monte (600 ms) avec la question en Unbounded 800 90 px, un seul mot en rouge. Un shape-morph (flubber, 900 ms `inOutCubic`) complète l'objet vers 1,1–2,0 s. Signature : quart de cercle bleu en haut à droite, pied de page Bauhaus, « N°xx ».
- **Structurer en (3 scènes × ~3,6 s)** séparées par un **grid-wipe** (départs à 2,4 / 6,0 / 9,6 / 13,0 s, coupe +0,525 s). Chaque scène : titre display 100 px (2–3 mots, `x −80 -> 0`, 450 ms) + sous-titre Space Grotesk 56 px (≤ 2 lignes) + une figure Paper.js qui porte l'argument :
  1. comparaison en panneaux (2×2, 430×380 px, stagger 380 ms, pastilles ✓/✕ en snap-90) ;
  2. chiffres : contour tracé + barre qui pousse + valeur qui compte (1,1 s `inOutCubic`, stagger 300 ms), puis on atténue les autres (opacité 0,28) et un badge rouge snap-90 donne la conclusion ;
  3. démonstration par morph : grille d'objets qui pop depuis le centre (stagger 18 ms) puis se morphent (stagger 22 ms, 700 ms).
- **Fermer par (13,5–16 s)** : grid-wipe, reprise de l'objet du hook (rime visuelle) + carte « réponse » (fait daté, source nommée), tenue ≥ 1,2 s. Fin propre, pas de boucle.
- **Son** : `pluck-arp` 120 bpm, do pentatonique majeur, gain 0,42 ; pop par élément de stagger, whoosh + thud sur chaque wipe, riser sous les barres, coin/chime sur les révélations.
- **Voix** : Orus, une phrase de 7–9 mots par scène, 0,2 s après chaque coupe.
- **Tokens** : `out/identities/bauhaus-kinetic/tokens.json`.
