# Journal — studio carte-meteo (Carte Météo)

Horodatage UTC. Machine partagée avec le studio `trait-continu` (Python), 4 cœurs.

## 2026-11-05 00:31 — installation (une seule fois)
- `npm i --save-exact world-atlas@2.0.2 @fontsource/atkinson-hyperlegible@5.3.0` à la racine : 1,3 s, 0 vulnérabilité.
- Lignes ajoutées à `package.json` (dependencies) : `"@fontsource/atkinson-hyperlegible": "5.3.0"` et `"world-atlas": "2.0.2"` (versions exactes, sans `^`) ; `package-lock.json` mis à jour par npm. Aucun pip.
- Constat : world-atlas 2.0.2 contient bien `countries-10m.json` (3,7 Mo) en plus de 50m/110m, contrairement à ce que dit le challenge ; consigne respectée : seul `countries-50m.json` (756 Ko) est utilisé.
- Licence : paquet ISC (Mike Bostock), données Natural Earth (domaine public).
- topojson-client 3.1.0 : `dist/topojson-client.min.js` (UMD, global `topojson`) et `src/index.js` (ESM) présents.
- Charge au départ : load average 0,03.

## 00:33 — décisions de lecture
- Police titre : **Space Grotesk 700** (installée). Écartées : Archivo Black + Inter (swiss-data, voisine directe), Unbounded (bauhaus), Syne (liquid-chrome), Fredoka (trait-continu en parallèle), Space Mono (riso-zine), Cinzel (atlas-grave), JetBrains Mono (topo-relief). Space Grotesk n'est titre que chez neon-lab (fond noir, laboratoire) : aucune confusion possible avec une carte claire. Corps, pastilles, légendes : Atkinson Hyperlegible 400/700 (nouvelle).
- Isobares : `#6E8FAA` 1,5 px → trop fin à l'échelle d'un téléphone ; je pars sur `#5F7F9A` 4 px (à mesurer).
- Pipeline : décodage world-atlas par topojson-client **une fois** dans `window.ready`, filtrage DROM, découpe Europe, projection conique conforme une fois en espace « base », caméra = `ctx.setTransform` sur des `Path2D` précalculés (rien n'est reprojeté par image). Vent = lignes de courant intégrées en Node (`src/precompute.js` → `src/wind.json`), particule = (ligne, phase) → position fermée en t. Isobares = `d3.contours` sur grille 108×192 (≤ 128²·1,3) recalculée par image.

## 00:40 — contrastes calculés (WCAG, script Python)
- **Échec du correctif tel qu'écrit** : terre `#BFE3A0` sur mer `#CFE6F5` = **1,11:1**, pas 1,25:1 (le challenge proposait `#BFE3A0` « par exemple », mais il ne passe pas son propre seuil). Choix : terre **`#A9D486`** = 1,31:1 contre la mer (texte `#10263D` dessus 9,11:1 ; côte `#3E5A72` dessus 4,28:1). Toujours un vert tendre.
- Isobares : `#6E8FAA` = 2,64:1 sur la mer, 2,38:1 sur la terre ; `#587A96` = 3,51 / 3,17:1 → retenu `#587A96`, 3 px (1,5 px testé au premier still).
- Vent `#10263D` à 35 % d'opacité : couleur effective 2,03:1 sur mer, 2,00:1 sur terre (forme, pas texte).
- Front bleu `#1F5FD6` : 4,44:1 mer / 4,01 terre ; front rouge `#D63A2A` : 3,62 / 3,27 (formes uniquement).
- Texte `#10263D` : 15,37:1 sur cartouche blanc ; `#3E5A72` : 7,22:1 sur blanc ; texte `#10263D` sur orange `#F59A2C` 6,98:1 ; blanc sur rouge 4,67:1 (≥ 54 px gras seulement).

## 00:42 — premier still de preuve (probe.html) : OK après 2 corrections
- topojson-client **UMD** (`/node_modules/topojson-client/dist/topojson-client.min.js`, global `topojson`) marche sous render.mjs du premier coup ; l'ESM `src/index.js` marche en Node (testé dans un script d'exploration). Décodage + filtrage + projection : **308 ms une fois** dans `window.ready`.
- MultiPolygon « France » de countries-50m : 10 polygones (Guyane, Réunion, Mayotte, Martinique, Guadeloupe ×4…) → 3 gardés (métropole 534 pts, Corse, Oléron) par centroïde lon ∈ ]−6, 10[, lat ∈ ]41, 52[, **avant** `fitExtent`. Découpe : 47 pays dont la bbox coupe [−16, 22]×[33, 60] ; projection `geoConicConformal().parallels([44,49]).rotate([-2.5,0]).fitExtent([[90,560],[990,1480]], France)` + `clipExtent`.
- Correction 1 (lecture du still) : les traînées de vent courtes (6 pas) et parallèles se lisaient comme de la **pluie**. → traînées de 16 pas (≈ 1 s), effilées en 3 tronçons (opacité 0,25/0,55/1), densité 42 %, et composante géostrophique (horaire autour de l'A, antihoraire autour de la D) pour courber le flux.
- Correction 2 (coût) : 20,5 s/100 images à vide avec dérive de caméra (carte re-rastérisée à chaque image). → caméra **fixe par plan** et fond de carte mis en cache dans un canvas par caméra : **17,6 s/100 images à vide** (60 images, dont la moitié en double rendu pendant le front). Référence mesurée : page canvas vide = **13,2 s/100** (capture seule). Le coût propre de la scène est donc ≈ 4 s/100.
- JS par image (profil `?prof=1`) : isobares 10–25 ms (23 200 échantillons noise3 + d3.contours), vent 1 ms (appels canvas différés), carte 0,1 ms (blit).

## 00:44 — short 1 : mistral (geographie)
- Stills ×2 séries. Correction : traînées pondérées par la vitesse locale (opacité 0,28→1, épaisseur 0,6→1,15) — sans cela le couloir rhodanien ne ressortait pas (tout le cadre hachuré pareil). Libellés « Massif central » / « Alpes » déplacés sous / au-dessus des pictogrammes (ils les masquaient). Soleil déplacé à l'est du couloir.
- Rendu complet unique lancé 00:45 en arrière-plan : **480 images en 87,0 s = 18,1 s/100** (charge 1–3,6 ; le studio trait-continu tournait en parallèle). Mux → `short.mp4` 5,9 Mo. 8 frames du rendu + 3 frames du fichier final regardées : OK. `check.py` : OK (1 avertissement attendu : voix off non générée).

## 00:47 — short 2 : record de chaleur (evenements)
- Échec visuel corrigé avant rendu : **voile de chaleur radial** orange (α 0,30–0,42) sur les terres → vert + orange = olive « sale », mer beige, la palette claire disparaît. Remplacé par des anneaux rouges plats (et une onde à 46,0) autour de la pastille record. Le halo rouge radial essayé ensuite donnait un anneau brun sur le vert : abandonné aussi.
- Fait ajouté au-delà de la liste du challenge : ancien record 44,1 °C à Conqueyrac (Gard), 12 août 2003 (Météo-France) → écart 1,9 °C. Pas de « J-N ». Le crochet est une pastille « ? °C » (pas de valeur inventée avant la révélation).
- Pastille : le module partagé a été retouché après le rendu du mistral (décalage chiffre/unité) puis **remis à l'identique** pour que `src/` du mistral reproduise exactement sa vidéo sans second rendu ; la pastille « 44,1 / 2003 » passe à r 112 à la place. Ajout sans effet sur le mistral : auto-ajustement du titre (≥ 90 px) si la ligne dépasse 796 px (« L'ancien record »).
- Rendu complet unique lancé 00:48 : **450 images en 84,6 s = 18,8 s/100**. Mux → `short.mp4` 3,2 Mo. 5 frames du fichier final regardées. `check.py` : OK (même avertissement voix).
- `precompute.js` relancé sur les deux shorts : `wind.json` identique au bit près (md5) → reproductible.

## 00:52 — design system
- `identity.md` (16 sections), `tokens.json`, `recipes/geographie.md`, `recipes/evenements.md`, `poster.jpg` (frame 11,6 s du record), `contact-sheet.jpg` (9 frames, `assemble.py sheet --cols 3`).
- Cartes librairie brouillons : `carte-meteo__topojson-client.json`, `carte-meteo__world-atlas.json`, `carte-meteo__d3.json`.
- GSAP **non utilisé** (fonctions fermées de t) ; plugins DrawSVG / MotionPath non utilisés. Librairies réellement utilisées : D3 7.9.2, topojson-client 3.1.0, world-atlas 2.0.2 (+ svi.js).
- Voix off non générée par ce studio (narration.json prête pour Fish Audio « Arnold »).
- Durée totale du studio : ≈ 25 min (00:31 → 00:56 UTC). Aucun blocage de librairie.

## 01:07 — corrections de la revue finale (`revue-2026-11-05.md`, section carte-meteo), un seul tour
- **Short chaleur, vent** : essai 1 (flux SSO courbé + ondulation, traînées 20–26 pas, densité 0,6–0,7) puis essai 2 (traînées 34–48 pas, α 0,7) en stills : les traînées restaient des hachures obliques, lues comme une averse. **Retirées** du short chaleur (air lent sous le dôme ; le mouvement vient des isobares, des fronts et des pops). `src/precompute.js` et `src/wind.json` supprimés de ce short ; `reproduce` et `src/README.md` mis à jour ; `seed` → 0 (plus aucun aléa).
- **Second rendu complet** du short chaleur (seul re-rendu) : **450 images en 84,1 s = 18,7 s/100**. Son régénéré (même `sound.json`), mux, 5 stills refaits depuis le fichier final et regardés, `poster.jpg` et `contact-sheet.jpg` régénérés. `check.py` OK sur les 2 shorts. **Mistral non re-rendu** (md5 de `short.mp4` inchangé : 1a8a95b5…).
- **Narration chaleur** : règle `maxDuration ≥ mots dits / 2,4`, chiffres comptés en mots prononcés (champ `spokenWords`). La date n'est plus relue (« Ce jour-là, … », 10 mots dits, 4,2 s) ; « Ancien record : 44,1 degrés, en 2003. » (11 mots dits, 4,6 s, 4,6 → 9,2) ; « Vérargues, dans l'Hérault, atteint 46 degrés. » décalée à 9,3 s (7 mots dits, 3,0 s) ; « Record absolu pour la France. » à 12,6 s (2,2 s). Aucun chevauchement, fin à 14,8 s.
- **Faits** : note du `short.json` complétée — record de 2003 (44,1 °C, 12 août 2003) **partagé entre Conqueyrac et Saint-Christol-lès-Alès** (Gard), sources de la revue (Futura-Sciences, Europe 1). Texte à l'écran inchangé.
- **identity.md** : écart au challenge déclaré dans Typographie (Space Grotesk en titres au lieu d'Atkinson partout) avec justification ; vent réservé aux shorts où il est le sujet (Formes, Risques) ; opacité du vent harmonisée (21–75 % = 0,25/0,55/1 × 0,28–1) ; règle de débit en mots dits ; coûts mis à jour.
- **tokens.json** : rôles inversés : `display` = Space Grotesk 700 108 px (bandeau), `title` = Atkinson Hyperlegible 700 jusqu'à 96 px (chiffres des pastilles).
- Rectificatif du journal : la grille des isobares est 116×200 (pas 10 px, débord 40 px), pas 108×192 comme écrit à 00:33.
