# Recette — un short `geographie` dans l'identité Carte Météo

Référence : `out/shorts/carte-meteo__geographie__le-mistral-pourquoi-il-souffle-si-fort/` (16 s, D3.js + topojson-client + world-atlas, rendu 87,0 s = 18,1 s/100 images).

**Pour un short geographie (un vent, un climat régional, un relief qui canalise l'air) dans cette identité :**

- **Ouvrir par** (0–3,4 s) : la France entière au plan large ×1 (`cam(1, 540, 1000)`), présente dès la frame 0 avec ses isobares (`#587A96` 3 px) et le vent déjà en mouvement (traînées sombres effilées) ; le bandeau blanc pope en `back.out(1.4)` 0,35 s : titre Space Grotesk 700 108 px (le phénomène, ≤ 15 caractères) + sous-titre Atkinson Hyperlegible 700 56 px `#3E5A72` (la question). A (bleu) et D (rouge) popent à 0,25 et 0,4 s, cohérents avec le sens du vent (rotation horaire autour de l'A, antihoraire autour de la D).
- **Structurer en** trois plans séparés par le `passage-du-front` (front **froid** pour un vent ou du froid ; 0,9 s `power2.inOut`, départs ≈ 3,4 / 8,3 / 12,6 s) :
  1. le **mécanisme** (≈ 4–8 s) : zoom ×2–2,3 sur la région, pictogrammes plats (montagnes 3 triangles) et cartouches blancs 54 px qui popent quand le front passe sur eux ; les traînées rapides (pondérées par la vitesse locale) dessinent le phénomène ;
  2. le **chiffre** (≈ 9–12,5 s) : une grande pastille (r 128) reliée à son lieu par un trait de rappel, compteur `power2.out` 0,9 s, anneau bleu -> rouge quand la valeur clé est atteinte ; 2 noms de lieux au plus ; vent ×1,5 ;
  3. la **conséquence** (≈ 13,5–16 s) : pictogramme de conclusion (nuages chassés en `power2.in` 1,9 s, soleil qui pope), titre court.
- **Fermer par** une tenue ≥ 1,5 s sur le plan de conclusion ; question ouverte dans la voix ou en CTA (« et chez vous ? »).
- **Données** : champ de vent écrit à la main en lon/lat dans `src/precompute.js` (le relief repousse, le couloir accélère), lignes de courant intégrées en Node, `wind.json` rejoué ; le dire « schématique ». Faits climatologiques sourcés, sans station inventée.
- Voix : 4 lignes (une par plan) à 0,3 s puis 0,2–0,3 s après chaque front, ≈ 2,5 mots/s, Fish Audio « Arnold ».
- Son : `pad`, `whoosh` 0,9 s à chaque front, `pop` par élément, `tick` par pas du compteur, `impact` + `chime` à la valeur clé, `swell` final.
- Tokens : `out/identities/carte-meteo/tokens.json`. Code partagé : `src/meteo.js`.
