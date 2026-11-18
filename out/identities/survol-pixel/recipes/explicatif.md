# Recette — short `explicatif` en Survol pixel

Référence : `out/shorts/survol-pixel__explicatif__comment-nait-un-atoll/` (numpy + Pillow + opensimplex, 18,6 s, graine 1842, moteur `src/survol.py`).

Pour un short **explicatif** (un mécanisme de la Terre, de la nature, d'une machine) dans cette identité :

- **Ouvrir par (0–1 s)** : le **résultat** vu en plongeante 68–72° en perspective (l'anneau, le delta, le cratère), caméra déjà en mouvement, et la question entière dès 0,15 s en Jersey 20 (`size 34` natif, 136 px) dans un cartouche crème : « UN ANNEAU / EN PLEINE MER ? ». Un objet ombré traverse (frégate et son ombre) : l'indice de profondeur géométrique (C2).
- **Structurer en 3 étapes numérotées** (un cartouche Jersey 15 par étape, ≤ 6 mots, « 1. », « 2. », « 3. ») :
  1. **Le piqué** (0,6 s, `whoosh`) vers la rasante 14–16° ; pendant le piqué, **le temps remonte** (le monde change par marches, 1 s, mention Jersey 10 « il y a des millions d'années »).
  2. **La coupe s'ouvre** (0,8 s) : un quart du monde descend jusqu'au socle encre ; la paroi montre l'intérieur (basalte, calcaire, eau, tireté fixe du niveau de la mer). Étiquettes à épingle (« basalte », « calcaire », « lagon »).
  3. **La transformation lente** (3,6 s, `inOutSine`) pendant une orbite : le volcan s'enfonce marche par marche, le récif reste à la surface. Mention Jersey 10 « pendant des millions d'années » ; « marches : convention de dessin » quand le public est jeune.
- **Fermer par** : **la remontée** (0,6 s) vers une plongeante 44–48° qui montre la forme finale **et** la coupe (le volcan enfoui sous l'anneau) ; nom et date en plaque inversée Jersey 20 or sur encre (« DARWIN, 1842 », ≤ 25 % de la durée), preuve en Jersey 10 (« basalte trouvé dessous en 1952 » : dire ce que la mesure a montré, pas plus). Tenue ≥ 3 s, `chime`.
- **Voix** : 5 lignes, 40 mots prononcés, 2,3–2,6 mots/s, silence pendant piqué et remontée ; la 1re phrase reprend les mots de l'accroche.
- **Faits** : vérifier avant d'écrire (ici : Darwin 1842 ; forages d'Enewetak 1952, basalte sous ≈ 1 270–1 400 m de calcaire) ; ne jamais dire qu'un volcan « disparaît » s'il reste dessous.
- **Tokens** : `out/identities/survol-pixel/tokens.json` (biome tropical, pad lydian 84 bpm).
- **Pipeline** : écrire `src/video.py` (champs du monde fonction d'un paramètre de temps, caméra, cartouches, épingles) avec `src/survol.py` ; `--preflight` ; `--stills … --dir …` ; `--dive --dir src/dive` ; puis la commande de `src/README.md`.
