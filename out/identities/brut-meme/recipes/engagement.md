# Recette — short `engagement` en Brut Mème

Référence : `out/shorts/brut-meme__engagement__test-des-3-secondes-stroop/` (15,5 s, PixiJS + GSAP, seed 47, 120 bpm).

Pour un short engagement dans cette identité :

**Ouvrir par** (0–1 s) — le défi est déjà à l'écran à la frame 0 :
- tag rouge Inter 900 56 px à (60, 236) qui nomme le format (« TEST DES 3 SECONDES ») ;
- l'objet du défi en Anton auto-fit 900 px (ici « ROUGE » écrit en jaune) + une ligne Inter 900 64 px de consigne ;
- `slam` d'un sticker rond rouge (« DIS LA COULEUR ! ») à 0,4 s, shake 10 px, `pop` ;
- à 1,0 s, `bg-invert` jaune : la règle en 3 lignes géantes (« DIS LA / COULEUR, / PAS LE MOT » — la 3e en bloc rouge `slam`).

**Structurer en** (2,0 → 8,6 s) — 3 rounds qui accélèrent, un `punch-cut` à chaque tic :
- round = tag « ROUND n/3 » + contenu (1, puis 3, puis 6 éléments) + anneau de compte à rebours Pixi en (540, 1360) : disque rouge R 130, anneau jaune R 168 qui se vide, chiffre Anton 190 px ;
- tics 0,5 s → 0,4 s → 0,3 s (punch force 0,4, `tick` + petit `impact`) ;
- **STOP** : coupe franche vers les blocs-réponses (aplats dans la couleur à nommer + ombre dure 14 px), disque noir « STOP » jaune, shake 14–18 px, `impact` + `coin` ;
- garder ≥ 0,75 s de lecture sur chaque réponse (1,25 s sur la dernière).

**Fermer par** (8,6 → 15,5 s) :
- explication en une ligne (8,6–12,2 s) : « LIRE » géant jaune / « VA PLUS VITE QUE » / « NOMMER » géant rouge, puis à 10,4 s une étiquette blanche (ombre rouge) de 3 lignes Inter 900 56 px — c'est la seule phrase longue, doublée par la voix ;
- CTA en `bg-invert` jaune à 12,2 s : « TON SCORE » (rescale) + « EN COMMENTAIRE » (bloc noir, `slide-snap`), sticker « 0, 1, 2 OU 3 ? » `slam` à 12,7 s, starburst noir « /3 » à 13,0 s, chevrons qui rebondissent sur chaque temps ;
- fin propre tenue 2,5 s ; jauge rubalise pleine à la dernière frame.

Tokens : `motion.punchIn`, `motion.shake`, `typography.display` (auto-fit), `shapes.sticker`, `layout.countdownCenter`, `sound` (pulse 120 bpm, impact par cut). Voix : Fenrir, mots-clés seulement pendant les rounds.
