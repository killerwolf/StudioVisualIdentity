# Recette — short `enfants` en Trait continu

Référence : `out/shorts/trait-continu__enfants__dessine-un-escargot-d-un-seul-trait/` (shapely + opensimplex + pycairo, 15,5 s, 30 i/s, graine 7, rendu 21,1 s).

Pour un short **enfants** (6–10 ans) dans cette identité :

- **Ouvrir par (0–1 s)** : la question d'enfant dans la bande orange dès t = 0 (Fredoka 700, 104 px, `#1A1410`, ≤ 4 mots sur 2 lignes : « Un escargot d'un trait ? ») ; plaque vierge avec l'anneau bleu `#1D47A8` au point de départ ; le trait part à 0,3 s, les deux curseurs et le chariot bougent. SFX `tick` toutes les 0,24 s pendant le tracé.
- **Structurer en 2 plaques** :
  1. **Plaque 1 (0,3–5 s)** : le geste de base, petit et simple (spirale de 2,5 tours partie du centre + corps, 3 900 px à 820 px/s). Une étiquette crème (Fredoka 600, 60 px) nomme le geste (« Du centre ») au moment où la voix le dit.
  2. **Avance plaque** (3 crans de 0,2 s + entrée 0,35 s, `click` ×3 puis `thud`), nouveau titre (« Un tour de plus »).
  3. **Plaque 2 (6,4–12,3 s)** : la même forme, plus grande et plus riche (coquille de 4 tours, 5 200 px à 900 px/s), avec 2 repères bleus au plus : « +1 » (Fredoka 700, 76 px) quand commence le tour ajouté, puis une flèche en arc qui montre le sens (« Vers la droite »).
  - Un temps = 3–4 s, ≤ 4 mots à l'écran (titre + étiquette compris).
- **Fermer par** : la question ouverte dans la bande orange (« Et toi, quel sens ? »), dessin complet tenu ≥ 2,5 s, `chime` doux ; aucun appel pressant (on invite à dessiner).
- **Voix** (Arnold, Fish Audio) : 5 lignes, 28 mots, 2,0–2,2 mots/s, silence pendant l'avance plaque. Faits à vérifier avant d'écrire (ici : la plupart des escargots ont une coquille dextre).
- **Tokens** : `out/identities/trait-continu/tokens.json` (orange `#F26A21`, plaque `#D3D4CE`, trait `#3A3D42` 7 px en escalier de 12 px, music-box majpent 92 bpm).
- **Pipeline** : écrire `src/video.py` (morceaux de chemin + jalons + repères + titres) en réutilisant `src/traceur.py` ; `video.py --info` pour lire les jalons et caler la narration ; `video.py --stills …` ; `video.py --sound-json src/sound.json` ; puis la commande de `src/README.md`.
- **Pièges** : un aller-retour (antenne, patte) double la longueur du chemin ; les spirales de rayon < 50 px deviennent des carrés à 12 px de pas.
