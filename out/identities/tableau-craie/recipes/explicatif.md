# Recette — short `explicatif` en Tableau Craie

Référence : `out/shorts/tableau-craie__explicatif__pourquoi-le-ciel-est-bleu/` (Manim + overlays PNG craie, 16,5 s, 30 fps).

Pour un short **explicatif** dans cette identité :

- **Ouvrir par (0–1 s)** : la question en Nunito 800 108 px (2 lignes, le mot-clé dans sa craie : « bleu » en `#7FD1FF`), présente dès t = 0, centrée x = 510, y = 250–480 ; en même temps le premier objet du schéma se dessine (`Create`, ≤ 0,7 s) avec un soulignement craie sous le mot-clé (0,3–0,65 s). Son : `tick` (craie posée) + `pop`.
- **Structurer en 3–4 idées de 2,2–4,9 s** séparées par le **chiffon** (0,4–0,5 s, `inOutSine`, whoosh 0,45–0,5 s) :
  1. le phénomène de départ (lumière blanche → ondes de 4 couleurs, stagger 0,25) ;
  2. le mécanisme, avec **zoom lent** 1,0 → 1,07 sur le détail (3 s, `inOutSine`) ;
  3. le chiffre-choc : barres hachurées proportionnelles (`GrowFromEdge`, `ease_out_back`) + « ×5 » Nunito 160 px ;
  4. la conséquence observable (coucher de soleil : trajet long, teinte orange 17 % en 0,9 s, dézoom 0,965).
  Une idée = 1 en-tête Nunito 92 px OU rien + 1–2 légendes Caveat 60–72 px dans la couleur de l'objet.
- **Fermer par** : la phrase-réponse en Caveat 72 px sur 2 lignes (couleur question puis couleur réponse) + `swell` + `chime`, tenue ≥ 1 s, pas de fondu au noir (fin propre).
- **Tokens** : `motion.duration` fast 0,35 / base 0,8 / slow 1,6 ; stagger 0,12 ; `transitions.chiffon` ; grain 77 sur tout ; safe area 220/320/120.
- **Voix** : 6 phrases de 5–8 mots (Kore, ≈ 2,6 mots/s), une par idée, silences sur les chiffons.
- **Pipeline** : `bash out/shorts/tableau-craie__explicatif__pourquoi-le-ciel-est-bleu/src/build.sh` (assets PIL → Manim sous `slot.sh` → `composite.py` overlays → `sound.py` → `assemble.py mux`).

> Voix réellement utilisée pour les shorts de preuve : Fish Audio « Arnold » (`d704cf8f1216490cbfbed89955f0e938`, `s2.1-pro`). Les noms Gemini ci-dessus sont des suggestions historiques de casting par ton.
