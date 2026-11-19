# Recette — short `explicatif` en Survol pixel

Référence : `out/shorts/survol-pixel__explicatif__comment-nait-un-atoll/` (numpy + Pillow + opensimplex, 18,6 s, graine 1842, moteur `src/survol.py`, monde de 1 080 unités ; état après la passe A+B+C du 18/11/2026).

Pour un short **explicatif** (un mécanisme de la Terre, de la nature, d'une machine) dans cette identité :

- **Ouvrir par (0–1 s)** : le **résultat** vu à 35–40° en perspective (l'anneau, le delta, le cratère), d'autres formes du même sujet jusqu'à l'horizon, caméra qui approche déjà en virant (roulis 5–10°), et la question entière dès 0,15 s en Jersey 15 (`size 27` natif, 108 px) dans un cartouche crème : « UN ANNEAU / EN PLEINE MER ? ». Un objet ombré traverse (frégate et son ombre) : l'indice de profondeur géométrique (C2).
- **Structurer en 3 étapes numérotées** (un cartouche Jersey 15 par étape, ≤ 6 mots, « 1. », « 2. », « 3. ») ; **un seul cartouche ou une seule épingle à la fois**, calé sur les débuts de mots de la voix :
  1. **La descente** (`whoosh`, 37° → 27°) ; pendant ce temps, **le temps remonte** (le monde change par marches, 1 s, `riser`) ; la voix dit « il y a des millions d'années » (la mention à l'écran a été retirée le 18/11).
  2. **La coupe s'ouvre** (0,8 s) : une tranchée (bande sud du monde) descend jusqu'à un socle de roche en dalles de 2 unités ; la paroi montre l'intérieur (basalte, calcaire, eau, tireté fixe du niveau de la mer). Étiquettes à épingle une à une (« basalte », puis « calcaire »).
  3. **La transformation lente** (3,6 s, `inOutSine`) pendant un plan de coupe lent à 25° qui glisse le long de la tranchée : le volcan s'enfonce marche par marche, le récif reste à la surface. « marches : convention de dessin » (Jersey 10) quand le public est jeune.
- **Fermer par** : la coupe **de face** (le volcan enfoui sous l'anneau, « 3. UN VOLCAN / SOUS L'ANNEAU », puis l'épingle « niveau de la mer » seule), **la remontée** (26° → 35–38°) et un départ au-dessus de l'anneau vers les autres formes, brume en 6 paliers vers le bleu pâle ; nom et date en plaque inversée Jersey 15 or sur encre (« DARWIN, 1842 », ≤ 25 % de la durée), puis la preuve en Jersey 15 sur 2 lignes (« basalte trouvé / dessous en 1952 » : dire ce que la mesure a montré, pas plus). `chime`.
- **Voix** : 5 lignes, 40 mots prononcés, 2,3–2,6 mots/s, silence pendant les transitions ; la 1re phrase reprend les mots de l'accroche.
- **Monde** : le sujet au centre, d'autres exemples du même phénomène jusqu'à l'horizon (ici d'autres atolls, monts sous-marins, bancs), jamais un décor copié de la source (pas d'archipel vert) ; carte de couleurs fine sur une fenêtre autour du sujet ; `--preflight` après tout changement de caméra.
- **Faits** : vérifier avant d'écrire (ici : Darwin 1842 ; forages d'Enewetak 1952, basalte sous ≈ 1 270–1 400 m de calcaire) ; ne jamais dire qu'un volcan « disparaît » s'il reste dessous.
- **Tokens** : `out/identities/survol-pixel/tokens.json` (biome tropical, pad lydian 84 bpm).
- **Pipeline** : écrire `src/video.py` (champs du monde fonction d'un paramètre de temps, caméra, cartouches, épingles) avec `src/survol.py` ; `--preflight` ; `--stills … --dir …` ; `--dive --dir src/dive` ; puis la commande de `src/README.md`.
