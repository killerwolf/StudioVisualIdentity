# Recette — short « engagement » en Diorama Pastel

Référence : `out/shorts/pastel-diorama__engagement__choisis-ta-boite-renard/` (A-Frame + GSAP, 15 s, graine 7, src/index.html avec géométrie `roundbox`).

**Pour un short engagement dans cette identité :**

- **Ouvrir par (0–3.2 s)** : les objets du jeu tombent sur le socle en `bounce.out` 0.6 s (stagger 0.07 s), le personnage pop dessus (`back.out(2.2)` 0.6 s) et salue ; kicker jaune « Choisis ta boîte ! » + question Baloo 2 132 px (« Où se cache le renard ? »). Le personnage montre l'enjeu (il saute dans la boîte, couvercle qui se referme en `bounce.out`) avant 3 s.
- **Structurer en (3.2–11.6 s)** :
  1. pastille-pop « Ça mélange… » puis **6 échanges** pré-calculés (une boîte passe devant, l'autre derrière, petit saut), durées décroissantes 0.85 -> 0.6 s, `inOutCubic` ; boîtes identiques pour un vrai suivi ;
  2. pastille « 1, 2 ou 3 ? », numéros ronds Baloo 2 84 px projetés sur la face avant de chaque boîte (stagger 0.16 s), **push-in** caméra 13 % (2.6 s `sine.inOut`) ;
  3. carte CTA blanche « Écris ton choix en commentaire ! » (Nunito 800 60 px, y = 1400) + compte à rebours 3-2-1 (bulle jaune 190 px, `back.out(2)`, 0.7 s par chiffre) sur un `riser`.
- **Fermer par (11.6–15 s)** : ouvrir d'abord la mauvaise boîte attendue (couvercle-pop, étiquette « vide ! »), puis la bonne (couvercle qui part en arrière, personnage qui jaillit `back.out(2.4)`, confettis aux 5 couleurs, numéro gagnant en menthe `#9BE7B0` ×1.3, les autres à 45 %), pastille « ✓ Boîte n°3 ! », puis carte CTA « Tu l'avais trouvé ? Dis-le en commentaire ! » et salut final. Fin tenue.
- **Son** : music-box F majpent 96 bpm, `thud` aux chutes, `whoosh`+`tick` par échange, `blip` au compte à rebours, `riser` 1.5 s, `pop` grave sur la boîte vide, `coin`+`chime`+`glass` à la révélation.
- **Technique** : A-Frame en chaînes (`geometry`/`material`), boucle coupée (`setAnimationLoop(null)` + `pause()`), caméra `Matrix4.lookAt`, rendu manuel ; pas d'ombres temps réel (disques transparents). Coût mesuré : voir `short.json` (renderTimeSec).
- **Tokens** : `tokens.json`. Garder le même socle, la même palette, les mêmes pastilles que le short enfants pour que l'identité soit reconnaissable à l'aveugle.
