# Revue adversariale aval de `survol-pixel`, 2026-11-18

Étape 8 du skill `fabrique-identites`. Objet : l'identité `survol-pixel` et ses 2 shorts de preuve, commit `accd0bb`, branche `identite-console-retro`.

Ce que j'ai fait :
- Je n'ai rien modifié, ni l'identité ni les shorts. Je n'ai rien commité.
- Mes mesures sont dans le scratchpad de la session (`review/`, `judge/`, `repo/`) :
  - images extraites de chaque `short.mp4` à 2 i/s (37 et 38 images) ;
  - planches, recadrages pleine résolution, luminance à 30 i/s ;
  - grille et palette mesurées sur les pixels décodés.

## Verdict global : **à corriger**

Ce qui est acquis :
- les 4 exigences du propriétaire sont tenues sur le fond ;
- le juge aveugle est parfait (6/6 groupes purs) ;
- la grille et la palette sont exactes ;
- aucun risque de photosensibilité.

**Aucun point bloquant pour l'identité.** Il y a en revanche :
- **1 défaut de lisibilité prioritaire** : la coupe finale de l'atoll ;
- 1 défaut visuel : un moiré qui grésille dans Machu Picchu ;
- 1 échec de la reconnaissance mesurée ;
- des points de forme ;
- **2 étapes du processus non faites**, qui bloquent la *livraison* mais pas l'identité :
  - la voix off ;
  - l'intégration (index, vitrine, rapports).

## Tableau des verdicts

| # | Point | Verdict | Preuve | Correctif |
|---|---|---|---|---|
| 1 | **Coupe finale de l'atoll (12,2–18,6 s) : le « losange marine »** | **à corriger (prioritaire)** | voir § 1 | voir § 1 |
| 2 | Moiré sur le flanc raide de Machu Picchu (5,5–9,0 s) | **à corriger** | voir § 2 | voir § 2 |
| 3 | Reconnaissance mesurée (`recognition.py`) | **à corriger** | voir § 3 | voir § 3 |
| 4 | Mentions informatives en Jersey 10 | **à corriger** | voir § 4 | voir § 4 |
| 5 | Voix off absente | **à corriger, livraison** | voir § 5 | voir § 5 |
| 6 | Intégration non faite (étape 7) | **à corriger, livraison** | voir § 6 | voir § 6 |
| 7 | Chiffres faux ou incomparables dans `identity.md` | **à corriger** (texte seulement) | voir § 7 | voir § 7 |
| R1 | Vraie profondeur 3D en pixel art | **accepté** | voir § R1 | — |
| R2 | La forme, pas le contenu | **accepté** | voir § R2 | (facultatif) prouver un sujet sans paysage |
| R3 | Distincte des voisines | **accepté** (juge) / à corriger (mesure, point 3) | voir § R3 | — |
| R4 | Rien de copié | **accepté** | voir § R4 | — |
| 8 | `identity.md` : 16 sections dans l'ordre | **accepté** | voir § 8 | — |
| 9 | `tokens.json` contre `core-tokens.schema.json` | **accepté**, avec réserve | voir § 9 | — |
| 10 | Zones sûres et tailles de texte | **accepté** (sauf point 4) | voir § 10 | — |
| 11 | Cohérence de `short.json` et `narration.json` | **accepté** | voir § 11 | (mineur) aligner le vocabulaire |
| 12 | `check.py` et poids des fichiers | **accepté** | voir § 12 | — |
| 13 | Photosensibilité | **accepté** | voir § 13 | — |
| 14 | Faits | **accepté** | voir § 14 | — |
| 15 | Autres défauts visuels | **accepté** | voir § 15 | (facultatif) liseré crème |

## Détail des points

### 1. Coupe finale de l'atoll : le « losange marine »

**Ce que montrent les images.** Aux images 11,5–18,5 s (et sur `comparaison.jpg`, rang 2, colonnes 4–5) :
- Un grand losange encre `#14213D` uni occupe le bas de l'image.
- Il couvre **10–13 % des pixels** sous y = 620, et c'est la tache la plus sombre et la plus massive de l'image.
- Le volcan en basalte, qui est le message, n'en couvre que **4 %**.
- La tenue dure 6,4 s, dont 3,6 s sous « DARWIN, 1842 », sans aucune épingle : « basalte », « calcaire » et « lagon » ont disparu après 11,4 s.
- Le tireté du niveau de la mer n'est plus qu'un trait clair de 1 px sur le bord de la coupe.
- L'eau des parois (`#2C74BE` sur l'océan `#1E5AA8`) ne se distingue presque pas.

**Diagnostic : ce n'est pas un artefact, mais ça se lit mal.**
- **Pourquoi ce n'est pas un artefact.** La géométrie est la coupe voulue :
  - un quart d'île de 100×100 cellules est retiré jusqu'au socle (z = −72) ;
  - la caméra regarde *dans* l'entaille, l'arête vers elle ;
  - on voit les deux parois intérieures : le calcaire en beige, et le volcan en basalte gris sous le calcaire, en triangle dont le sommet est sous l'anneau ;
  - le losange est le fond de l'entaille, c'est-à-dire le socle, vu en perspective ;
  - le recadrage à 13,5 s le confirme : les parois sont continues, sans trou ni plan lointain manquant.
- **Pourquoi ça se lit mal.** Pour un spectateur naïf sur téléphone :
  - la scène se lit comme « un trou noir / une pyramide sombre dans la mer » ;
  - le socle encre se lit comme un vide ou une ombre, pas comme « le fond de la maquette » ;
  - rien ne dit que le triangle gris est le volcan, à part le cartouche « 3. UN VOLCAN / SOUS L'ANNEAU ».
- **Le même problème plus tôt.** À 4,5–8,0 s, la paroi de basalte forme une grande dalle grise unie : 18–24 % de l'image, sans strates. On la lit comme un toit ou une pyramide grise. L'épingle « basalte » et le tireté sauvent ce passage.

**Correctif (rendu de l'atoll seulement, sans toucher au moteur commun) :**
1. **Plan final : tourner le cap de 35–45°** pour voir une paroi presque de face, comme à 10 s, au lieu de l'arête. Sinon, baisser le tangage vers 35–40°. Le socle passe alors de ≈ 12 % à < 4 % de l'image.
2. **Remonter le socle** de −72 à juste sous la base du volcan (≈ −40), ou le peindre en roche `#8A8178` hachurée plutôt qu'en encre. L'encre est la couleur du texte : elle ne doit pas être la plus grande surface de l'image.
3. **Garder les épingles « basalte » et « calcaire » pendant la tenue finale.** On peut ajouter « niveau de la mer » sur le tireté, épaissi à 2 cellules et en écume `#E6FAFF`.
4. **Peindre l'eau des parois** en lagon `#7CCBEB`, ou en hachure une ligne sur deux, pour qu'on voie la tranche d'eau au-dessus du récif.
5. Facultatif : un liseré clair de 1 px sur l'arête de la coupe.

À vérifier ensuite : une image à 13,5 s et une à 17,0 s, montrées à quelqu'un qui n'a pas le contexte, doivent faire dire « volcan sous le récif ».

### 2. Moiré sur le flanc raide de Machu Picchu (5,5–9,0 s)

**Mesure.**
- Sous « XVe SIÈCLE », une bande mouchetée vert clair et vert sombre court entre la montagne grise et les terrasses : zone x 100–550, y 1180–1380.
- Ce sont les contremarches vues par la tranche.
- Elle **grésille** en mouvement : 6,5 % des pixels de la bande changent à chaque image (pointe 29 %), contre 1,0 % pour une zone de forêt témoin.
- Le journal du studio dit ce moiré « absent des images du short ». **C'est faux.** Il est présent sur 3,5 s, et sur le still `02_plongee-cite-terrasses_7.0s.jpg`.

**Correctif.** Dans `survol.py`, sur le niveau de carte réduite :
- étendre le vote majoritaire aux **flancs** (couleur de contremarche) quand la pente vue par la tranche dépasse ≈ 70°, ou forcer un niveau de réduction plus grossier sur ce flanc ;
- sinon, changer le cadrage du plan 5,5–9 s pour sortir ce flanc du champ.

Il faut ensuite re-rendre Machu Picchu seulement.

### 3. Reconnaissance mesurée (`recognition.py`, lancé sur une copie)

**Résultat.**
- La copie était dans `scratchpad/repo/`, et `out/report/recognition.json` du dépôt n'a pas été touché (md5 identique avant et après).
- Les deux shorts sont des **échecs** de premier voisin. Dans les deux cas, le frère arrive **2e** :

  | Short | 1er voisin | Distance | Frère (2e) |
  |---|---|---|---|
  | atoll | aquarelle-conte « phare d'Alexandrie » | 0,6545 | 0,6664 |
  | Machu Picchu | papier-decoupe « fourchette » | 0,6269 | 0,6664 |

- Top-1 global : 40/45.
- **Aucun voisin de la direction n'apparaît dans les 6 plus proches** : ni pixel-arcade, ni carte-meteo, ni topo-relief.

**Lecture.**
- La mesure compare des histogrammes Lab et des contours. Or les deux preuves ont des dominantes opposées : bleu océan pour l'atoll, vert montagne pour Machu Picchu. La distance entre les frères (0,666) est donc près de 3 fois l'intra moyen (0,23).
- Ce n'est pas une confusion avec une voisine, mais le contrôle 8 du challenge (« le plus proche voisin de chaque short est son frère ») **n'est pas tenu**.

**Correctif, au choix :**
- (a) Rendre visibles **dans les deux shorts** les constantes de la signature : ciel en paliers, brume dorée et cartouches crème. Concrètement, ajouter à l'atoll une vraie rasante de ≥ 3 s avec ciel et brume, car aujourd'hui 0–3 s et 12–18,6 s n'ont presque pas de ciel, seulement une bande dans la zone haute que l'interface TikTok masque. Relancer ensuite la mesure sur copie.
- (b) Accepter l'échec et l'écrire dans `comparison.md`, avec ces chiffres, comme pour les échecs de liquid-chrome.

Je recommande (a), parce qu'elle répond aussi au point « ≥ 50 % d'horizon visible », voir § R1.

### 4. Mentions informatives en Jersey 10

**Mesure.**
- Jersey 10 donne des capitales de 40 px finals et un œil d'environ 28 px.
- Elle porte deux informations de fond :
  - « il y a des millions d'années » et « pendant des millions d'années » ;
  - le fait daté « basalte trouvé dessous en 1952 ».
- Ces mentions sont lisibles à 360 px de large, mais **sous la règle du dépôt** (texte courant ≥ 54 px).

**Correctif.**
- Passer ces trois mentions en Jersey 15 : capitale 60 px, et ≤ 20 caractères par ligne, donc en 2 lignes (« basalte trouvé / dessous en 1952 »).
- Garder Jersey 10 pour « reconstitution stylisée » et « marches : convention de dessin » seulement.

### 5. Voix off absente

**Constat.**
- `short.mp4` et `short_novo.mp4` sont identiques (même taille, 3 356 831 et 4 542 442 octets).
- `check.py` avertit : « voix off absente ».
- Les 43 autres shorts du dépôt sont doublés.

**Correctif.**
- Décision du propriétaire à obtenir : Gemini « Sulafat », une requête par short, ou Fish Audio « Arnold ».
- Puis `tts.py --engine files --replace`, et corriger le libellé `voiceEngine` si la voix vient de Gemini.
- Les lignes de `narration.json` sont prêtes et tiennent le débit (§ 11).

### 6. Intégration non faite (étape 7)

**Constat.**
- `survol-pixel` est absent de `index.json`, `comparison.md`, `catalogue.md` et de la vitrine.
- `git status` montre des fichiers modifiés hors de cette revue : `aggregate.py`, `slot.sh`, cartes `jersey/numpy/pillow/scipy.json`… Une intégration semble en cours dans une autre session. Je n'y ai pas touché.

**Correctif.** Terminer l'étape 7, puis porter dans `recognition.json` le résultat du juge aveugle (clé `blindJudgeSurvol`, chiffres en R3).

### 7. Chiffres faux ou incomparables dans `identity.md` (texte seulement)

- **« luminance ≈ 0,10 contre 0,77 »** (§ Risques). 0,10 est la luminance *relative* de la seule couleur océan. Or la moyenne d'image mesurée (Y) est de **0,35–0,53** pour l'atoll et **0,41–0,57** pour Machu Picchu. La différence avec carte-meteo (0,77) reste nette, mais il faut écrire ces chiffres.
- **« 13–23 couleurs par image »**. Je mesure **18–26 et 18–28** entrées de palette par image, sur les blocs 4×4 décodés, avec une tolérance ΔRGB ≤ 25. C'est toujours dans la palette déclarée et sous 32, mais le seuil « ≤ 20 en plongeante » n'est pas démontré. Au choix : écrire « ≤ 28 » ou le re-mesurer sur les images natives.
- **Journal** (`notes/survol-pixel.md`, C3) : corriger « moiré absent des images du short » (voir § 2).

### R1. Vraie profondeur 3D en pixel art — accepté

**Grille.**
- Écart moyen d'un pixel à la moyenne de son bloc 4×4 aligné : **0,32** (atoll) et **0,39** (Machu Picchu), sur 0–255. C'est du bruit d'encodage.
- Le même calcul sur une grille décalée de 2 px donne 6,2 et 3,5.
- La grille de 4 px est donc exacte, sans pixel intermédiaire ni mixel.

**Palette.**
- Seulement **0,1–0,4 %** des blocs sont à plus de ΔRGB 25 de la palette `tokens.json` (noyau et biomes). C'est une palette indexée.

**Pas d'effet d'écran** : aucune trace de scanlines, de grain ou de flou à l'œil.

**Indices de profondeur, tous vus :**
- sol en perspective jusqu'à l'horizon : Machu Picchu 0–4,5 s et 15–18,8 s, atoll 3,5–11 s ;
- terrasses à contremarches visibles ;
- ombres portées de la frégate et des nuages ;
- nuages empilés en parallaxe ;
- caméra en mouvement continu ;
- piqué sans saut dans `src/dive/` ;
- coupe en volume.

**Réserve.** L'atoll passe 0–3 s et 12–18,6 s en plongeante quasi sans horizon visible hors de la zone haute que l'interface masque. La profondeur y tient par les ombres et la coupe, mais c'est le moment le moins « 3D » de l'identité (voir § 3a).

### R2. La forme, pas le contenu — accepté

- Récits didactiques : explicatif et histoire, sans jeu, sans avion, sans HUD.
- `identity.md` contient « Appliquer la signature à n'importe quel sujet » et « Sujet sans paysage », avec 3 cas travaillés.
- Il y a 4 recettes : explicatif, histoire, géographie, enfants.
- Limite connue : les deux preuves restent des paysages. Rien ne prouve encore un sujet sans paysage. Ce n'est pas exigé.

### R3. Distincte des voisines — accepté pour le juge, à corriger pour la mesure

**Juge aveugle.**
- Un agent neuf (opus) a reçu seulement 24 images mélangées : 6 identités × 2 shorts × 2 images à 35 % et 75 % de la durée.
- Les 6 identités : survol-pixel, pixel-arcade, carte-meteo, topo-relief, pastel-diorama et trait-continu.
- La clé est dans `scratchpad/judge_key.json`.
- Résultat : **6/6 groupes purs, 24/24 images**, confiance haute partout.
- Sa seule hésitation va dans le bon sens : « survol » et pixel-arcade partagent une police pixel, mais se séparent par « terrain 3D de jour, cartouches crème » contre « grille néon sombre ».

**Mesure** : voir § 3.

### R4. Rien de copié — accepté

D'après `comparaison.jpg` et les images :
- aucun avion, cockpit, HUD, ligne d'aide ni archipel ;
- un seul sujet centré ;
- ≤ 3 nuages à l'écran ;
- objets originaux : frégate, lama, palmiers ;
- pas d'anneaux, de score ni de piste.

La parenté avec la source tient à la palette de l'océan et à l'écume en traits, ce qui relève du style revendiqué. La provenance est créditée dans `identity.md`.

### 8. `identity.md` : 16 sections dans l'ordre — accepté

Ordre vérifié : Nom, Promesse, Mood, Palette, Typographie, Formes, Mouvement, Caméra, Transitions, Structure, Zones sûres, Librairies, Familles, Shorts de preuve, Voix, Risques. Les sous-sections `###` sont dans les bonnes sections.

### 9. `tokens.json` contre `core-tokens.schema.json` — accepté, avec réserve

`jsonschema` n'est pas installé : vérification à la main.
- `color.bg` et `color.accent[]` présents, `surface` et `text` aussi.
- `typography` : rôles avec famille, slug @fontsource et taille en px.
- `motion` en secondes, avec `hookDeadline` 0,15.
- `safeArea` sur 4 côtés (220 / 320 / 120 / 64).
- `transitions[]`.

**Réserve.** `coreTokens` (avec `canvas` et `safeAreaPx`) est produit par `build_index.py`, qui n'a pas encore tourné. À re-vérifier dans `index.json` après l'intégration.

### 10. Zones sûres et tailles de texte — accepté (sauf point 4)

**Zones sûres**, mesurées sur les 75 images (pixels crème exacts des cartouches) :
- boîtes entre **x = 68–951** et **y = 246–1595** ;
- limites : x 60–960, y 220–1600 ;
- tout est dedans, avec 5 px de marge seulement en bas (« reconstitution stylisée »).

**Contrastes**, recalculés sur les couleurs rendues :
- encre sur crème : **14,36:1** ;
- or sur encre : **10,4:1**.

**Tailles** : récit Jersey 15 avec capitale 60 px ; accroche Jersey 20 avec capitale 80 px.

### 11. Cohérence de `short.json` et `narration.json` — accepté

- **Lignes sans chevauchement.** La dernière ligne finit à 18,5 s (atoll) et 18,6 s (Machu Picchu), dans la durée du short.
- **Débit**, en mots prononcés : 2,33–2,58 (atoll) et 2,27–2,58 (Machu Picchu). C'est ≤ 2,6, et loin du plafond de 3,2.
- **Mots à l'écran** : ≤ 6 par cartouche de récit.
- **Accroche visible dès l'image 0.**
- Mineur : la voix dit « la pluie s'écoule », le cartouche « LA PLUIE FILE ». Aligner sur un seul verbe (C20).

### 12. `check.py` et poids des fichiers — accepté

- `check.py` : **ok** sur les 2 shorts, 0 erreur, 1 avertissement (voix, § 5).
- Format : 1080×1920, 30 i/s, h264 yuv420p, durées 18,6 et 18,8 s.
- Poids : **3,4 Mo et 4,5 Mo**, sous le plafond de 15 Mo.

### 13. Photosensibilité — accepté

Luminance moyenne à 30 i/s :

| | Atoll | Machu Picchu |
|---|---|---|
| Plus grand saut d'une image à l'autre | 0,058 | 0,035 |
| Plus grande variation sur 1/3 s | 0,147 | 0,133 |
| Sauts > 0,1 | 0 | 0 |
| Aire qui change de > 0,2 d'une image à l'autre | ≤ 12,9 % | ≤ 18,9 % |

Aucun flash plein cadre ni image blanche. Écume à 2 Hz.

### 14. Faits — accepté

Vérifiés par recherche web (sources de l'USGS et de la GSA, WaterHistory.org reprenant Wright) :
- **Darwin, 1842** : c'est la date du livre.
- **Enewetak** : forage F-1 en 1952, basalte à ≈ 1 405–1 410 m sous Elugelab, et E-1 à ≈ 1 270 m. La formulation « basalte trouvé dessous en 1952 » est juste. La nuance de Ladd (les trois stades ne sont pas prouvés) est respectée dans `short.json`.
- **Machu Picchu** : 2 430 m, XVe siècle, 1911 : justes.
- **Couches de la terrasse**, de bas en haut : pierres, gravier, terre. C'est juste ; la couche de sable intermédiaire décrite par Wright est omise, simplification acceptable.
- **Formulations du challenge** : celles de C18 et C19 sont présentes.

### 15. Autres défauts visuels — accepté

- **Cartouche vide pendant 1 image** à 12,0 s (atoll) et 15,0 s (Machu Picchu). C'est l'ouverture en hauteur prévue (0,13 s), pas un bug.
- **Nuage qui passe sous « reconstitution stylisée »** (Machu Picchu, 16,5–18,5 s). Le liseré tient le contraste. Facultatif : un liseré crème extérieur plus franc.
- **Atoll à 4,5 s** : le quart d'île qui descend « en ascenseur » laisse voir sa calotte verte au fond. C'est bizarre sur une image fixe, mais lisible en mouvement.
- Aucun trou, aucune apparition de relief, aucun texte qui déborde, aucune couleur hors palette.

## Re-vérification ciblée après le tour de corrections

1. **Atoll (point 1)** :
   - images à 13,5 et 17,0 s : socle < 5 % de l'image, épingles « basalte » et « calcaire » présentes ;
   - test « spectateur naïf ».
2. **Machu Picchu (point 2)** : changement de pixels par image dans la bande x 100–550, y 1180–1380, entre 5,4 et 9,0 s : ≤ 2 % en moyenne.
3. **`recognition.py` sur copie** : le frère arrive 1er pour les deux shorts, ou l'échec est documenté dans `comparison.md`.
4. **Jersey 15** pour les trois mentions, et `check.py` ok.
5. **Voix mixée** : `check.py` sans avertissement.
6. **Intégration** : `index.json` (`coreTokens` valide), vitrine, et `recognition.json.blindJudgeSurvol`.
