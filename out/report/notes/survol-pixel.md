# Journal du studio « Survol pixel » (`survol-pixel`), 2026-11-18

Étape 5 du skill `fabrique-identites`, une identité, deux shorts de preuve. Mac Intel i7 4 cœurs partagé avec d'autres
sessions (charge 1 min entre 2,9 et 38 pendant la journée). Rien n'a été commité ni supprimé.

## Livrables

- Identité : `out/identities/survol-pixel/` (`identity.md` 16 sections, `tokens.json`, `recipes/{explicatif,histoire,geographie,enfants}.md`, `poster.jpg`, `contact-sheet.jpg`).
- Shorts : `out/shorts/survol-pixel__explicatif__comment-nait-un-atoll/` (18,6 s) et
  `out/shorts/survol-pixel__histoire__machu-picchu-pourquoi-une-cite-en-escaliers/` (18,8 s) : `short.mp4` (musique + bruitages,
  sans voix), `short_novo.mp4` (copie identique, source future de `tts.py`), `short.json`, `narration.json`, `stills/`,
  `src/` (`survol.py` moteur identique dans les deux, md5 égal ; `video.py` ; `sound.json` ; `test_jersey_grid.py` ;
  `dive/` série du piqué ; `README.md`).
- Comparaison avec la source : `out/report/notes/console-retro-source/comparaison.jpg`.
- Cartes : `out/library-cards/_drafts/survol-pixel__{numpy,pillow,opensimplex,jersey,scipy}.json`.
- `package.json` : `@fontsource/jersey-10`, `jersey-15`, `jersey-20` ajoutées en **5.3.0 exact** (`npm i --save-exact`), sous-ensemble latin utilisé.

## Mesures

| | Atoll | Machu Picchu |
|---|---|---|
| Images | 558 | 564 |
| Rendu complet (moteur, `time`) | **122,3 s → 21,9 s/100** (rendu final) ; 1er rendu 159,7 s → 28,6 s/100 | **331,6 s → 58,8 s/100** |
| Charge 1 min (début → fin, relevés /20 s) | 6,9 → 4,4 (4,6–7,3) ; 1er rendu 13,6 → 5,8 (5,2–14,5) | 13,6 → 6,2 (5,2–16,1) |
| Banc préalable 60 images (charge 4,5) | 27,5 s/100 | 56,9 s/100 |
| `check.py` | ok, 1 avertissement attendu (voix absente) | idem |
| Poids `short.mp4` | 3,4 Mo | 4,5 Mo |
| Part des images à tangage ≤ 60° (C12) | 81,9 % | 79,3 % |
| Couleurs par image (natif) | 13–23 | 14–21 |
| Luminance moyenne (YAVG/255) : max, saut max 1 image, variation max sur 10 images (1/3 s) | 0,516 ; 0,050 ; 0,126 | 0,551 ; 0,030 ; 0,114 |
| Marge mini caméra / relief (`--preflight`) | 63,2 | 56,2 |

Les deux premiers rendus ont tourné en parallèle (`SVI_SLOTS=4 out/tools/slot.sh`) : `measuredUnderLoad: true`. L'atoll a été rendu **une seconde fois** pour une correction réelle de fait : la mention « vérifié par forage en 1952 » laissait croire que les trois stades de Darwin étaient prouvés, alors que les forages prouvent l'affaissement (basalte sous le calcaire) ; elle devient « basalte trouvé dessous en 1952 » (205 px natifs). Machu Picchu : un seul rendu.

## Décisions

- **Moteur : variante (a) de C1**, lancer de rayon par pixel sur une carte de hauteurs en terrasses, mesuré dès les premières
  images (0,13–0,85 s/image à charge 5–10) puis confirmé ≤ 60 s/100 en rendu complet. Pas besoin du repli « sprite stacking ».
  Optimisations : marche limitée à la boîte englobante du relief, par paquets de 12 pas avec retrait des rayons arrivés ;
  plan z = 0 en forme close ailleurs ; monde de l'atoll recalculé par image (paramètre d'enfoncement), celui de Machu Picchu une fois.
- **Convention de dossier** : moteur copié dans chaque `src/` (comme `traceur.py` de trait-continu) ; cache dans
  `$SURVOL_CACHE` (scratchpad de la session pendant le travail ; défaut `/private/tmp/survol-pixel/<dossier>`), jamais `/tmp/svi`.
- **La coupe « maquette »** est devenue la signature didactique : une région du monde descend jusqu'à un socle encre et
  ses parois sont colorées par une fonction de la scène. Elle sert de schéma posé au sol pour les deux preuves (C14).
- **Machu Picchu** : plateau de la cité raccordé par une « jupe » de terrasses en pente douce (une première version lisait
  comme une tour) ; monde affiné ×1,8 (cellules plus petites en vue rapprochée) ; la coupe est vue depuis l'**aval** (vue
  de l'amont, la terrasse supérieure la cachait).
- **Socle de coupe** en encre `#14213D` plutôt que gris : lit comme un vide, met la coupe en valeur.
- **Voix** : aucune ; `narration.json` prêt (voix proposée Sulafat), `sound.voice: false`.

## Correctifs du challenge, un par un

- **C1** une seule caméra (`CameraPath` : cible, distance, cap, tangage, roulis) pour tout le short ; sol plat par
  intersection rayon–plan, relief par lancer de rayon par pixel (≤ 60 s/100 : 28,6 et 58,8 mesurés) ; aucun changement de
  moteur en cours de plan ; série du piqué 90/70/50/30/15° rendue avec le même moteur dans `src/dive/` des deux shorts
  (pas de relief qui apparaît ou disparaît, vérifié à l'œil). Pas de voxel space.
- **C2** vues plongeantes à 60–72° en perspective, jamais orthographiques (le 90° n'apparaît que dans la série de preuve) ;
  contremarches colorées (claire / sombre selon la lumière nord-ouest) ; chaque image montre un indice géométrique (horizon,
  flanc de terrasse, coupe, ou frégate / lama dont l'ombre encode la hauteur).
- **C3** carte de couleurs réduite par vote majoritaire (3 niveaux, sans moyenne), niveau choisi par l'empreinte anisotrope du
  pixel au sol ; brume quantifiée par tables d'indices. Limite connue : dans la série de preuve à 90–70°, le flanc très raide de
  la montagne de Machu Picchu montre un petit moiré de contremarches vues par la tranche (**erreur relevée par la revue** : il était aussi présent dans le short, 5,5–9,0 s ; corrigé, voir « Corrections après revue »).
- **C4** panneaux (frégate, palmiers, lama) réduits au plus proche voisin et **plafonnés à 1:1** (assertion dans
  `scale_nearest`) ; lama mesuré à d1/profondeur 1,34–1,69 → dessiné à 1:1 ; nuages dessinés à leur taille projetée (jamais agrandis).
- **C5** Jersey 20 (34) accroche et dates, Jersey 15 (27) récit et étiquettes, Jersey 10 (56/3) mentions seulement ; ≤ 2 lignes
  et ≤ 214 px natifs par ligne, assertion `getlength` qui fait échouer le rendu (elle a attrapé « relief en marches :
  convention de dessin », 265 px, réécrit « marches : convention de dessin »).
- **C6** interligne = em complet ; marge haute 5 px natifs ; « SIÈCLE », « RÉVÉLÉE », « BÂTISSENT », « ÉTAPE »-type vérifiés sur stills.
- **C7** accroches en 2 lignes (« UN ANNEAU / EN PLEINE MER ? », « POURQUOI / DES ESCALIERS ? ») affichées entières dès 0,15 / 0,12 s ;
  « ATOLL = ANCIEN VOLCAN » supprimé.
- **C8** PIL `fontmode "1"` à 56/3 sur origine entière ; `src/test_jersey_grid.py` (fontTools `AreaPen` sur `.woff`) :
  99/99 glyphes exacts pour chacune des 3 tailles, encre d'une ligne = somme des glyphes ; sortie non nulle sinon.
- **C9** aucun texte dans la carte projetée ; étiquettes = cartouche Jersey 15 à l'écran + trait 1 px vers une épingle
  (point projeté, tête or cerclée d'encre) ; le trait passe sous le cartouche.
- **C10** aucune plaque phosphore ; plaque inversée encre / or (« DARWIN, 1842 » 3,6 s = 19 %, « XVe SIÈCLE » 3,8 s = 20 %), une seule à la fois.
- **C11** pas de « ALT … M » : l'altitude est une étiquette de récit « À 2 430 m » et une phrase de la voix ; courbes de niveau
  sombres ; ciel de jour visible dans toutes les rasantes.
- **C12** la grille ×4 n'est pas présentée comme une différence avec pixel-arcade (`identity.md`) ; part de tangage ≤ 60° mesurée
  sur la trajectoire de caméra : 81,9 % et 79,3 % (`short.json.qualityChecks.pitchLe60Share`).
- **C13** pas de traversée de nuage ; écume à 2 Hz ; battement d'ailes à 3 Hz ; variation de luminance moyenne ≤ 0,126 sur 1/3 s
  (règle : ≤ 0,2), aucune image blanche ; mip contre les rayures près de l'horizon.
- **C14** objets originaux avec ombre : frégate (atoll, ombre décalée de 34 unités d'altitude), palmiers des motu, lama (Machu
  Picchu) ; schémas posés au sol : la coupe du quart d'île (basalte / calcaire / eau / niveau de la mer) et l'entaille dans
  trois terrasses (pierres / gravier / terre).
- **C15** atoll : un seul sujet centré, ≤ 3 nuages, pas d'archipel ; comparaison côte à côte dans `comparaison.jpg` (aucune image
  confondable : pas d'avion, de cockpit, de ligne d'aide, d'îles éparses).
- **C16** section « Sujet sans paysage » dans `identity.md` (cœur en île à deux bassins, ville en terrasses avec foules, frise du
  temps posée au sol comme une route), chacun avec carte, panneaux, schéma au sol et moment du piqué.
- **C17** aucun élément de jeu ; un seul preset `pad` en `lydian` ; événements `whoosh`, `swell`, `riser`, `thud`, `pop`, `chime`
  (aucun `blip`, `coin`, `chiptune`, `pulse`).
- **C18** « Darwin l'a expliqué en 1842 » ; le volcan s'enfonce et reste sous le récif (coupe finale) ; 3 étapes numérotées (récif
  frangeant, il s'enfonce / le corail monte avec lagon, un volcan sous l'anneau) ; niveau de la mer fixe (tireté clair dans la
  coupe) ; mention « marches : convention de dessin » ; Enewetak 1952 en Jersey 10 (« basalte trouvé dessous en 1952 », formulation exacte).
- **C19** « la pente tient », « bâtissent des terrasses », « révélée au monde en 1911 » ; ordre des couches pierres / gravier /
  terre de bas en haut ; rien sur les séismes, le nombre de terrasses, ni les Espagnols ; « reconstitution stylisée » à l'écran
  tout le short ; sources vérifiées le 18/11 (Burger et al. 2021, Wright, UNESCO WHC 274) dans `short.json`.
- **C20** débit ≤ 2,6 mots/s en mots prononcés (« 1842 » = 5, « 2 430 » = 5) : 2,27–2,58 ; 40 et 38 mots ; shorts allongés à
  18,6 et 18,8 s ; silence pendant piqués et remontées ; un cartouche ≤ 6 mots par plan ; accroche et première phrase avec les
  mêmes mots-clés ; livrable encodé par `assemble.py mux` (crf 20, maxrate 8M), 3,4 et 4,5 Mo ; `renderTimeSec` et charge notés.

## Échecs et corrections en cours de route

1. Faux flancs : rayons entrant dans la boîte du relief par le côté sous le niveau de la mer → priorité au plan z = 0 touché avant.
2. Coupe « vue de dehors » : un rayon passant haut au-dessus de la coupe coloriait la montagne d'en face en coupe → condition
   « point précédent sous le dessus d'origine » (`cut_top0`).
3. Caméra dans la montagne (plan de coupe de Machu Picchu, image toute verte) → assertion caméra / relief dans le moteur et
   `--preflight` sur toutes les images avant rendu.
4. `out/tools/slot.sh` boucle sans fin sur macOS (`nproc` absent) → `SVI_SLOTS=4` (noté dans les README).
5. Cartouches hors zone sûre à droite (« lagon », « 2 430 m ») → assertion de zone sûre dans `cartouche()` ; centrage sur x = 128.

## Sources des faits

- Darwin, *The Structure and Distribution of Coral Reefs*, 1842.
- Forages d'Enewetak 1951–52 : Ladd, Ingerson, Townsend, Russell & Stephenson, « Drilling on Eniwetok Atoll, Marshall Islands », AAPG Bulletin 37(10):2257–2280, 1953 ; Ladd & Schlanger, USGS PP 260-Y ; USGS Professional Paper 260 ; réception : GSA Annual Meeting 2006 (« Drilling for Darwin »).
- Burger et al., « New AMS dates for Machu Picchu », *Antiquity*, 2021 (doi:10.15184/aqy.2021.99).
- Wright & Valencia Zegarra, *Machu Picchu: A Civil Engineering Marvel* (ASCE, 2000) ; Wright et al., *Journal of Hydraulic Engineering*, 1997.
- UNESCO, Historic Sanctuary of Machu Picchu (WHC 274, 1983) ; machupicchu.gob.pe (2 430 m).

## Lisibilité à 360 px (contrôle 5 de la revue)

Stills réduits à 360×640 (taille d'aperçu) : « MACHU PICCHU », « POURQUOI / DES ESCALIERS ? », « reconstitution stylisée »
(Jersey 10, capitale 40 px finale), « DARWIN, 1842 » et « basalte trouvé dessous en 1952 » restent lisibles. Jersey 10 tient la
règle des 54 px comme **taille de police** (74,7 px) ; ses capitales font 40 px : elle est réservée aux mentions.

## Points pour l'intégration

- `package.json` / `package-lock.json` modifiés (Jersey 10/15/20 en 5.3.0 exact) : à commiter ensemble.
- `out/tools/aggregate.py` (CANON, ROLES, PINNED) ne connaît pas numpy, Pillow, scipy ni Jersey : à ajouter pour fusionner les brouillons.
- `out/tools/slot.sh` (et peut-être `render.mjs`, à vérifier) dimensionne ses slots avec `nproc`, absent sur macOS : `SVI_SLOTS=4`.
- Non fait : voix (décision en attente), sujet facultatif « dune », traversée de nuage (supprimée, C13 b), reconnaissance / juge aveugle (revue).

## Corrections après revue (`revue-2026-11-18-survol-pixel.md`, un seul tour)

Un rendu complet de plus par short (moteur `survol.py` modifié, toujours identique dans les deux `src/`).

1. **Coupe de l'atoll (« losange marine »)** — corrigé. Le quart sud-est est remplacé par une **tranchée** (bande sud de
   200 × 50 cellules) dont la paroi passe par le centre du volcan ; le plan final tourne le cap de −50° à −10°/+5° pour la
   voir **de face** ; socle remonté de −72 à −40 et peint en roche hachurée (`#8A8178` / basalte une rangée sur trois) au lieu
   de l'encre ; basalte à joints verticaux ; eau des parois en lagon hachuré ; tireté du niveau de la mer épaissi (2,3 unités,
   écume) ; épingles « basalte », « calcaire », « niveau de la mer » tenues de 12,4 s à la fin. Lecture à 13,5 s et 17,0 s :
   triangle sombre du volcan sous le calcaire et l'anneau.
2. **Moiré de Machu Picchu (5,5–9,0 s)** — corrigé. Dans le moteur : biais de niveau de carte réduite selon la pente locale
   (1,6·log2(1+Δh), seulement au loin) et contremarches lointaines colorées par la carte réduite ; rotation de caméra du plan
   ralentie (cap −22° → −12° au lieu de 0°). Pixels qui changent par image dans la bande x 100–550, y 1180–1380 : natif 8,8 %
   → 1,3–1,5 % ; fichier final 1,59 % en moyenne (revue : 6,5 %). Contrepartie : flancs moyens-lointains plus « en blocs ».
3. **Reconnaissance** — en partie. L'atoll finit par **3,7 s de rasante** (15–17°, ciel en paliers, brume dorée, horizon) qui
   tient dans les 18,6 s et la narration. `recognition.py` relancé **sur une copie** (scratchpad, `out/report` non touché) :
   top-1 41/45 ; Machu Picchu → son frère (0,6635) : **réussi** ; atoll → aquarelle-conte « phare d'Alexandrie » (0,6208),
   frère à 0,6635 : **échec maintenu** (dominante bleue de l'océan contre dominante verte de la montagne ; aucune voisine de la
   direction dans le top). À documenter dans `comparison.md` par l'intégration.
4. **Mentions en Jersey 10** — corrigé : « il y a des millions / d'années », « pendant des millions / d'années », « basalte
   trouvé / dessous en 1952 » en Jersey 15 sur 2 lignes. Jersey 10 ne garde que « reconstitution stylisée » et « marches :
   convention de dessin ».
5. **Chiffres d'`identity.md`** — corrigés : luminance moyenne d'image Y 0,35–0,53 (atoll) et 0,41–0,57 (Machu Picchu) contre
   0,77 pour carte-meteo ; couleurs natives (indices exacts) 15–17 en plongeante, 14–23 en rasante, et 18–28 sur fichiers
   décodés (mesure de la revue). Erreur du journal sur le moiré corrigée (C3).
- Mineur : la voix de Machu Picchu dit maintenant « la pluie file », comme le cartouche.

| | Atoll | Machu Picchu |
|---|---|---|
| Rendu complet après revue | **87,0 s → 15,6 s/100** | **333,6 s → 59,1 s/100** |
| Charge 1 min (relevés /20 s) | 2,9–3,9 | 2,9–29,0 (fin à 23,4) |
| `check.py` | ok (avertissement voix seul) | idem |
| Poids | 3,2 Mo | 4,0 Mo |
| Luminance : max ; variation max sur 1/3 s | 0,544 ; 0,157 | 0,575 ; 0,118 |

## Passe de détail (18/11)

Demande du propriétaire après `console-retro-source/comparaison.jpg` : « la source est beaucoup plus détaillée ; la nôtre est
moins jolie, plus carrée, moins bien définie ». Diagnostic chiffré complet et avant / après : `survol-pixel-detail.md`.
Planche : `console-retro-source/comparaison-avant-apres.jpg` ; images d'avant : `console-retro-source/avant/`.

- **Diagnostic** :
  - la grille n'est pas en cause (4 px contre 3,94). Le test A/B à 360×640 ×3 est rejeté : bavure de chroma 4:2:0 sur 1,1–1,2 %
    des pixels, ×1,6–1,9 de coût, et moins de détail par cellule ;
  - l'agrandissement est net de bout en bout ;
  - l'écart vient du monde :
    - densité de détail divisée par deux (`diffCells` 0,11–0,15 contre 0,22) ;
    - grands aplats (85 % de l'écran en plages > 5 % pour l'atoll) ;
    - 2–3 petits nuages, pas d'arbres, une seule masse verte à Machu Picchu ;
    - texels de 2–7 px à bords droits de près ;
  - les cartouches couvrent 19–20 % de l'écran ;
  - la caméra est quasi immobile (≈ 1 cellule/s contre 100–140).
- **Moteur** (md5 `9d38995aa862a43b9885777fac65e41a`, identique dans les deux `src/`) :
  - micro-détail sous la cellule (lecture décalée + moucheture, seulement si une cellule couvre ≥ 2 px) ;
  - murs appareillés ;
  - nuages en tas de boules (hachure, liseré `CLOUD_RIM`, ombres) ;
  - arbres en grappes (boules au rayon projeté, ombre portée) ;
  - `hash01` / `ragged`.
- **Scènes** :
  - atoll : hauts-fonds crénelés, pâtés coralliens, arbres sur le volcan, 24 nuages à l'altitude 90 jamais traversés,
    caméra qui avance ;
  - Machu Picchu : terrasses et relief plus fins, rebords clairs, toits à deux pans, forêt d'arbres, 14 nuages, plan en
    plongeante moins tournant.
  - Textes, narration, son, grille et polices inchangés ; test Jersey 99/99.
- **Échecs en route** :
  1. Un nuage à l'altitude 46 passait devant la coupe à 10,5 s → nuages au-dessus de la caméra des rasantes, filtre
     anti-traversée calculé sur tout le trajet.
  2. Bande de la revue à 2,82 % au premier rendu → moucheture interdite à 1 px par cellule (−0,9 point) et rotation du plan
     ramenée à 6° → **1,13 %** (avant : 1,50 %).
  3. Arbres qui grésillaient dans les rasantes (A-B-A ×3) → seuil de 1,25 px et suppression du test du pied ;
     le reste est le défilement d'une forêt dense (1,40 % sur le short, source 4,0 %).
- **Mesures** :
  - atoll 109,2 s (19,6 s/100), Machu Picchu 356,0 s (63,1 s/100), en parallèle, charge 2,7–8,9 ;
  - `check.py` ok sur les deux (avertissement voix seul) ;
  - poids 4,4 et 8,3 Mo.
  - `diffCells` natif : atoll 0,111 → 0,153, Machu Picchu 0,146 → 0,330 (source 0,221).
- **À décider (propriétaire)** :
  - le plafond « ≤ 4 nuages » de C15 est levé pour l'atoll ;
  - réduire ou non l'accroche et les dates de Jersey 20 à Jersey 15 pour libérer de l'écran ;
  - une caméra plus rapide (vie) contre le texte et le scintillement.
- **Pour l'intégration** : `index.json` (coût 19,6–63,1 s/100) et la reconnaissance (`recognition.py` sur copie) sont à
  repasser.

## Passe A+B+C, phase 1 (18/11)

Demande du propriétaire après le rapport d'analyse « Fable » (écarts 1–10 avec la source) : options **A** (monde rempli,
brume refaite, horizon), **B** (fin des « cubes » et des bascules de détail) et **C** (caméra qui vole, textes allégés).
Phase 1 seulement : moteur et scènes modifiés (non commités), stills prototypes, mesures, coût. **Aucun rendu complet,
aucun appel payant.** Planche : `console-retro-source/prototypes-abc.jpg` (par short : source, rangée « avant » tirée du
`short.mp4` actuel, rangée « après », mêmes instants, et une paire t / t + 1/30 s avec la carte des bascules). État
d'avant conservé hors dépôt (scratchpad de la session) pour comparer. Dans la carte des bascules, les points vus deux
fois sont colorés ainsi, arêtes comprises :
- rouge : changement de matière ;
- bleu : palier de brume ;
- orange : autre teinte de la même matière.

### Ce qui a changé

- **Moteur** (`survol.py`, md5 `b8cd68deb713b07f9d8480ac200e9b79`, identique dans les deux `src/`) :
  - **4 rayons par pixel (2×2) et vote majoritaire sur l'indice de palette** (`vote4`) : pas de moyenne, palette
    indexée intacte ;
  - **carte de couleurs fine** (4 cases par cellule de hauteur) sur une fenêtre autour du sujet, carte grossière
    ailleurs ; la carte grossière reprend dans la fenêtre la réduction de la fine (pas de saut à la frontière) ;
  - niveau de réduction choisi par l'empreinte du sous-rayon **avec un décalage fixe par cellule (hachage)** : une
    transition est semée dans le monde au lieu d'être une ligne qui balaie l'écran ;
  - **supprimés** : biais de pente du mip, règle « mur lointain = couleur du dessus », moucheture et lecture décalée
    (seuil ≥ 2 px) ; seuil des arbres tiré par arbre dans [1,0 ; 1,8] px (houppiers de même teinte peints dans la carte
    fine) ; appareil de pierre à largeur fixe dans le monde, effacé paroi par paroi (seuil tiré par cellule) ;
  - **brume en 6 paliers** (tables d'indices par matière, `Palette.set_haze`), seuils = multiples d'une distance de
    référence lissée (la `dist` de la caméra, **bornée en bas** : 280 à Machu Picchu, 220 pour l'atoll, sinon le plan de
    coupe rapproché, à 62, faisait glisser tous les paliers d'un coup), frontière crénelée fixe dans le monde (cases de
    8 unités : à 2 unités, le crénelage scintillait au loin) ; le dernier palier est `HAZE`,
    devenu **bleu très pâle `#DCEEF5`** = bas du ciel (plus de bande crème) ; **ciel en 7 paliers doux** ;
    11 couleurs de noyau ajoutées (3 paliers de ciel, 8 de brume) ;
  - **ombre portée du relief** calculée une fois par monde (`relief_shade`) ; moucheture des contremarches fixe dans
    le monde (`wall_speck`) ; ombres des nuages par masque monde tramé une fois par image (`disk_mask`) ;
  - marche du rayon à **pas sûrs** sur des cartes de maxima par blocs (128, 32, 8, 2) puis pas géométriques et 8
    bissections : indispensable avec un monde 2,4–3 fois plus grand ;
  - caméra **PCHIP** (cubique monotone : vol sans à-coups, sans rebond sous le relief) ; `hitinfo` donne le point
    touché par pixel (mesures).
- **Atoll** (`video.py`) : monde de 1 080 unités (×3) ; autour du sujet, **sans île verte** (réserve du propriétaire) :
  5 autres atolls (anneaux de sable et de corail), 3 monts sous-marins, 3 bancs, houle à grandes bandes de profondeur,
  70 nuages jusqu'à l'horizon avec leurs ombres ; au-delà, une mer texturée. Fenêtre fine de 320 unités, recalculée
  seulement quand s, la coupe ou la phase d'écume changent (mémoïsée). Tranchée de coupe plus profonde (50 → 60) ; socle en dalles de 2 unités (les rayures d'une unité scintillaient en
  rasante : A-B-A 9,1 % → 3,9 % à 17 s).
- **Machu Picchu** : monde de 1 536 unités (×2,4) ; crêtes et vallées andines jusqu'au bord (bruit « en arêtes »), une
  seconde rivière lointaine, sommets enneigés possibles (`SNOW`) ; fenêtre fine de 512 unités : parcelles organiques
  sur les terrasses, forêt naturelle en grandes plages de deux verts (plus de rayure d'une marche sur deux), houppiers
  de trois verts, strates du granite, rivière à courant et écume semée,
  traits de pied et de rebord fins.
- **Caméra (les deux)** : elle avance et vire, roulis 5–13° dans les virages, tangage 25–40° hors plans de coupe
  (coupe lente à 19–20°, pour la lecture) ; contrôle préalable : marge minimale 85,8 (atoll) et 41,9 (Machu Picchu).
- **Cartouches** : **un seul à la fois**, tous en Jersey 15 (108 px ≥ 90), calés sur les lignes de `narration.json`
  (débuts de mots repérés par `silencedetect` sur `voice_lines/`). Textes dits et minutage inchangés ; durées
  18,6 / 18,8 s inchangées.

### Mesures avant → après (natif 270×480, sans cartouches sauf « textes »)

Script hors dépôt ; mêmes instants, même code pour les deux moteurs.
- **« Même point »** : chaque pixel de t + 1/30 s est reprojeté dans la caméra de t ; on garde les pixels où les deux
  images voient le même point du monde.
- **« Intérieur »** : pixel dont les 8 voisins ont le même indice ; on écarte ainsi le crénelage des arêtes en mouvement.
- **Instants mesurés** :
  - plans posés : atoll 0,6 / 2,5 / 9,5 / 17 s ; Machu Picchu 0,6 / 7 / 11 / 17 s ;
  - **transitions**, là où l'analyste a trouvé les défauts. Avant : piqué de Machu Picchu 5,2 s, remontée 14,8 s ;
    bascule de l'atoll 3,5 s, remontée 11,7 s. Après : 9,4 et 14,5 s (Machu Picchu), 3,5 et 14,2 s (atoll).

**Bascules d'un même point (par image)**

| Mesure | Atoll avant → après | Machu Picchu avant → après |
|---|---|---|
| Plans posés : intérieur qui change | 0,06–0,14 % → 0,53–0,67 % | 0,07–0,29 % → 0,15–0,85 % |
| Plans posés : dont changement de matière | 0–0,02 % → 0,02–0,05 % | 0,01–0,08 % → 0,03–0,09 % |
| **Piqué** : intérieur qui change / matière / saut > 60 | 5,30 / 0,45 / 4,76 % → **3,39 / 0,57 / 2,98 %** | 1,98 / 0,15 / 1,56 % → **1,08 / 0,03 / 0,08 %** |
| **Remontée** : intérieur qui change / matière / saut > 60 | 2,93 / 0,00 / 2,88 % → **0,46 / 0,03 / 0,30 %** | 5,47 / **1,66** / 1,52 % → **1,55 / 0,21 / 0,37 %** |
| Saut de couleur moyen quand la brume change (max ΔRGB, tous instants) | 94–136 → **29–63** | 98–176 → **31–43** |
| Même point qui change, arêtes comprises | 2,3–12,8 % → 4,4–14,8 % | 5,1–15,7 % → 5,7–16,8 % |

**Mesures de l'analyste, même pixel écran, sans reprojection.** Elles sont faussées par le défilement : la caméra vole
maintenant, donc un pixel change de point du monde d'une image à l'autre.

| Mesure | Atoll avant → après | Machu Picchu avant → après |
|---|---|---|
| Pixels qui passent brume ↔ non-brume, piqué / remontée | 5,4 / 4,9 % → 2,1 / 1,5 % | 4,3 / 1,9 % → 5,0 / 3,2 % |
| Pixels vert ↔ gris, piqué / remontée | 40 / 0 → 323 / 0 px | 10 356 / 17 852 → 25 074 / 16 830 px |
| Pixels qui changent, plans posés | 2,3–2,9 % → 4,8–14,9 % | 5,1–11,2 % → 6,3–31,8 % |

**Scintillement A-B-A** (même pixel, 3 images consécutives ; source 4,0 %, passe de détail 1,40 % sur le short de
Machu Picchu)

| Instants | Atoll avant → après | Machu Picchu avant → après |
|---|---|---|
| Survol | 0,2 % → 1,8–2,5 % (1,5 / 17 s) | 0,3–1,8 % → **4,1–6,3 %** (17 / 7 s) |
| Piqué / remontée | 3,8 / 3,7 % → 4,2 / 3,3 % | 7,9 / 8,1 % → **13,3 / 10,1 %** |

**Image et textes**

| Mesure | Atoll avant → après | Machu Picchu avant → après |
|---|---|---|
| Part de brume à l'écran (médiane) | 11,6 % → 14,8 % | 10,8 % → 32,9 % (6 paliers, relief lisible) |
| Aplats > 5 % / > 1 % de l'écran | 0,78 / 0,86 → **0,63 / 0,82** | 0,35 / 0,62 → **0,31 / 0,49** |
| `diffCells` (source 0,221) | 0,101 → 0,128 | 0,215 → 0,314 |
| Couleurs par image (médiane) | 20 → 26 | 20 → 23 |
| **Textes** : part de l'écran, médiane / max | 18,3 % / 26,8 % → **5,4 % / 9,1 %** | 19,5 % / 23,5 % → **3,8 % / 11,0 %** |
| Images sans aucun texte | 8 % → 14 % | 5 % → 18 % |

**Caméra**

| Mesure | Atoll avant → après | Machu Picchu avant → après |
|---|---|---|
| Tangage médian ; part du temps à 25–40° | 16° ; 19 % → 27° ; 100 % | 18° ; 1 % → 29° ; 73 % |
| Roulis max ; part du temps ≥ 5° | 3° ; 0 % → 12° ; 56 % | 2° ; 0 % → 13° ; 62 % |
| Vitesse médiane | 13 → 14 unités/s (coupe lente) | 24 → 52 unités/s |

**Lecture**
- **Les défauts relevés par l'analyste ont disparu, y compris dans les transitions** :
  - la remontée de Machu Picchu, qui faisait passer les murs du gris au vert, tombe de **1,66 % à 0,21 %** de
    bascules de matière ;
  - les grands sauts (ΔRGB > 60) tombent de 1,5 % à 0,1–0,4 % ;
  - la brume avance d'un cran à la fois (saut moyen ΔRGB 29–63 au lieu de 94–176), vers un bleu pâle égal au bas
    du ciel : plus de plaque gris-vert ni de bande crème ;
  - les murs lointains restent gris ;
  - le plan de coupe ne montre plus de pain de sucre fantôme (bornage de la référence de brume).
- **En revanche, le scintillement monte**, surtout à Machu Picchu : A-B-A 4,1–6,3 % au survol et 10–13 % au piqué et
  à la remontée, contre 4,0 % pour la source.
  - Ce n'est ni la brume ni la texture. Mesuré en coupant chaque élément à 7 s : réduction de carte et moucheture
    sans effet, arbres −0,9 point, vote 2×2 −0,15 point.
  - C'est la géométrie : contremarches et dessus en bandes de 1 px sur les pentes lointaines, sous une caméra deux fois
    plus rapide qui tourne.
  - Corrigé en phase 1 : crénelage de brume trop fin (8,7 → 6,3 %), socle rayé de l'atoll (9,1 → 3,9 %).
  - Le reste demande, au choix, une caméra plus lente au piqué et à la remontée (elles durent ≈ 1 s), ou des marches
    naturelles plus hautes au loin. C'est une décision de phase 2, à juger sur la vidéo.

### Coût (banc : 30 images réparties + 30 images contiguës du plan le plus cher)

| | Avant | Prototype | Short entier estimé | Charge 1 min pendant la mesure |
|---|---|---|---|---|
| Atoll | 0,20 s/image | 1,21 s réparties ; 1,58 s pendant l'enfoncement (8,0 s, monde recalculé à chaque image) | **11–15 min** | 3,2–3,5 |
| Machu Picchu | 0,63 s/image | 3,24 s réparties ; 3,37 s au survol (6,5 s) | **30–32 min** | 3,8–4,3 |

- Machu Picchu est dans la cible (25–35 min).
- L'atoll dépasse la cible de 8 min, mais reste loin du plafond de 45 min. Le reste se répartit ainsi :
  - le monde est recalculé à chaque image pendant l'enfoncement (≈ 0,5–0,7 s) ;
  - environ 0,5 s de tableaux de 518 000 sous-rayons dans `ground`.

  Pistes pour la phase 2 :
  - recalculer le monde à 15 Hz pendant l'enfoncement (animation en pas, lisible en pixel art) ;
  - alléger `ground` (moins de `np.where` sur les sous-rayons).
- Le coût a été mesuré avant les deux derniers réglages (référence de brume bornée, crénelage à 8 unités, socle en
  dalles), qui ne changent rien au calcul.
- Une première mesure prise pendant un pic de charge (≈ 57, étude GPU en parallèle) donnait 2–4 fois plus : ces
  chiffres ont été jetés.

### Décisions laissées au propriétaire (phase 2)

- **Cartouches retirés** (un seul à la fois, 18,6 s ne suffisent pas pour tous) :
  - atoll : « il y a des millions / d'années », « pendant des millions / d'années », l'épingle « lagon » et les
    épingles finales « basalte » / « calcaire » ;
  - « niveau de la mer » est montré seul de 13,4 à 15,0 s ;
  - « marches : convention de dessin » passe en haut, de 6,3 à 7,6 s.
- Machu Picchu : « reconstitution stylisée » n'est plus affichée qu'**à la fin** (16,9–18,8 s). Avant, elle restait à
  l'écran tout le short ; le challenge (C, point 10) n'exige que sa présence.
- Les épingles « pierres », « gravier », « terre » passent dans l'ordre de la voix, 0,5–0,75 s chacune. Elles sont
  courtes, mais ce sont des mots seuls.
- Toutes les accroches et dates passent en Jersey 15.
- **C15 rouverte** :
  - autres atolls et monts sous-marins au loin ;
  - plus de 4 nuages à l'écran par moments ;
  - aucune île verte : l'archipel de la source n'est pas copié.
- Ajouter au design system 11 couleurs de noyau et la nouvelle valeur de `HAZE`. La règle « brume par tables » est
  assouplie à 6 tables.

### Risques pour la phase 2

- **Scintillement en mouvement**, le risque principal (voir plus haut) :
  - Machu Picchu, A-B-A 4–6 % au survol et 10–13 % pendant le piqué et la remontée (source 4,0 %) : contremarches et
    dessus à 1 px sur les pentes lointaines ;
  - atoll, 1,8–4,2 %.
  - Leviers :
    - ralentir le piqué et la remontée ;
    - rehausser les marches naturelles au loin ;
    - ou accepter, si la vidéo le supporte.
- **Calage voix** : prévu sur les débuts de mots, à vérifier à l'oreille une fois remixé (`tts.py --engine files`,
  sans nouvel appel).
- **Lisibilité** : « MACHU PICCHU » en Jersey 15 est plus petit qu'avant (108 px). Les épingles de 0,5 s sont à
  juger sur la vidéo.
- **À mettre à jour à l'intégration** : `identity.md`, `tokens.json` (luts, ciel, `HAZE`), les `src/README.md`,
  `short.json` (coût, `reproduce`), `index.json`, ainsi que les séries `src/dive/` (non régénérées ici).

## Passe A+B+C, phase 2 (18/11)

Phase 2 : décisions du propriétaire appliquées, rendus complets des 2 shorts, voix existante remixée, intégration. **Aucun
appel payant, aucune nouvelle voix.** Planche finale : `console-retro-source/final-abc.jpg` (par short : 1 image de la source,
rangée AVANT tirée du `short.mp4` du commit d'avant la passe, rangée APRÈS tirée du `short.mp4` final, aux instants de
`prototypes-abc.jpg` ; plus 2 instants de transition : atoll 3,5 / 14,2 s ; Machu Picchu piqué 9,0 s et remontée 14,5 s,
comparés aux transitions d'avant : piqué 9,6 s et remontée 14,8 s, d'après la structure de l'ancien `short.json` (piqué à 9,3 s ; le « piqué 5,2 s » des mesures de phase 1 tombe en fait sur l'ancienne remontée de 4,9 s) ; atoll 3,5 et 11,7 s).

### Décisions du propriétaire (18/11)

- **Choix 34** : cartouches retirés à l'atoll : « il y a des millions / d'années », « pendant des millions / d'années »,
  l'épingle « lagon » et les épingles finales « basalte » / « calcaire ».
- **Choix 36** : « reconstitution stylisée » à Machu Picchu seulement à la fin (16,9–18,8 s) ; règle « brume par tables »
  assouplie (6 paliers) ; **C15 rouverte** (d'autres atolls au loin, plus de 4 nuages à l'écran par moments, mais pas
  d'archipel vert copié de la source).
- **Piqué et remontée de Machu Picchu ralentis** : 8,0 → 10,0 s et 13,4 → 15,6 s (≈ 1 s au prototype), contre le
  scintillement mesuré en phase 1.
- **Plafond de coût levé pour B.**
- **GPU seulement si la parité est à 0 pixel** : non garanti (voir plus bas), donc rendus sur CPU.

### Rendus complets (CPU, les 2 en parallèle sur 4 cœurs, donc sous charge)

| Short | Images | Durée | s/100 images | Charge 1 min début → fin | Construction du monde |
|---|---|---|---|---|---|
| Atoll | 558 | 598,1 s | **107,18** | 5,98 → 4,42 | 19,8 s |
| Machu Picchu | 564 | 1 501,9 s | **266,29** | 6,26 → 10,40 | 39,3 s |

Avant la passe : 19,6 et 63,1 s/100 images. Le prototype estimait 11–15 et 30–32 min ; l'atoll a pris 10 min et Machu
Picchu 25 min, mais sous charge et à deux.

- Son : bruitages recalés sur les nouveaux temps (`src/sound.json`).
- Voix : la voix existante a été remixée par `tts.py --engine files --replace`, sans appel Gemini.
- Les libellés Gemini Sulafat ont été remis dans `short.json` et `voice_report.json`.
- `check.py` : ok, 0 avertissement, sur les 2 shorts.

### Mesures sur les shorts finaux

**Scintillement A-B-A**

Deux méthodes, à ne pas mélanger :

- **Fichier décodé** (méthode de la source, 4,0 %) : 1 px par gros pixel, seuil 24, sur `short.mp4`. Fenêtres :
  - Machu Picchu : piqué 8,0–10,0 s, remontée 13,4–15,6 s ;
  - atoll : descente 3,2–4,0 s, remontée 13,9–14,6 s.
- **Natif** (méthode du prototype, `measure_abc.py` avec `ABA=1`) : indices exacts, sans cartouches, 3 images consécutives.

| Mesure | Atoll avant → après | Machu Picchu avant → après |
|---|---|---|
| Décodé, short entier | 0,38 % → **1,06 %** | 1,40 % → **3,56 %** |
| Décodé, piqué / descente (moyenne ; max) | 1,74 % → 2,58 % (4,4) | 2,94 % (11,3) → **7,30 % (8,8)** |
| Décodé, remontée (moyenne ; max) | 0,12 % → 1,61 % (1,7) | 2,42 % (7,6) → **5,42 % (7,1)** |
| Décodé, survol (atoll 1–2 s ; Machu 6,5–7,5 s) | 0,25 % → 1,56 % | 0,23 % → 6,71 % |
| Décodé, plan final 16,5–17,5 s | 0,17 % → 1,93 % | 1,53 % → 3,40 % |
| Natif, piqué : prototype → final | 4,2 % → 4,18 % (3,5 s) | **13,3 % → 7,8 %** (9,4 s) ; 10,9 / 9,9 % à 8,4 / 9,0 s |
| Natif, remontée : prototype → final | 3,3 % → 3,25 % (14,2 s) | **10,1 % → 7,1 %** (14,5 s) ; 7,0 / 6,1 % à 14,0 / 15,0 s |

Lecture :

- **Le ralenti a presque divisé par deux le scintillement des transitions de Machu Picchu** (mesure native 13,3 / 10,1 % →
  7,8 / 7,1 %).
- Il reste **au-dessus de la source** : sur le fichier décodé, 7,3 % au piqué, 5,4 % à la remontée et 6,7 % au survol de
  7 s, contre 4,0 % pour la source.
- **Il a monté par rapport à la passe de détail** : 1,40 → 3,56 % sur tout le short (atoll 0,38 → 1,06 %).
- Les pics d'avant (11,3 % sur une image au piqué) sont devenus un plateau plus bas mais plus long, sur 2 s.
- Atoll : sa caméra n'a pas changé depuis le prototype, d'où les mêmes valeurs natives.
- Dans les fenêtres de transition, les bascules de matière restent faibles :
  - Machu Picchu, intérieur 0,01–0,28 %, grands sauts 0,07–0,43 % ;
  - atoll 3,5 s : 0,57 / 2,98 %, comme au prototype.

**Son, image, caméra**

| Mesure | Atoll | Machu Picchu |
|---|---|---|
| Loudness intégrée (ebur128) ; crête ; LRA | −16,0 LUFS ; −1,7 dBFS ; 5,3 LU | −13,8 LUFS ; −1,5 dBFS ; 3,9 LU |
| Luminance Y moyenne / max (décodé) | 0,472 / 0,512 | 0,484 / 0,515 |
| Variation de luminance max par image / sur 10 images | 0,032 / 0,043 | 0,028 / 0,037 |
| Tangage min / médian / max ; part ≤ 60° | 25 / 26,5 / 40° ; 100 % | 19 / 29 / 38° ; 100 % |
| Roulis max ; part du temps ≥ 5° | 12° ; 56 % | 13° ; 59 % |
| `--preflight` : marge minimale caméra / relief | 85,8 | 41,6 (41,9 au prototype) |
| Couleurs par still natif, cartouches compris | 23–30 | 19–26 |
| Couleurs de la série `dive/` (90 → 15°) | 19–30 | 17–24 |
| Taille du fichier | 8,9 Mo | 13,8 Mo |

- Avant la passe : −15,9 et −13,7 LUFS.
- Palette déclarée : 40 couleurs par épisode (35 de noyau + 5 biome). La phrase « palette déclarée ≤ 32 » d'`identity.md` ne
  tient plus ; le compte par image reste ≤ 32 (critère du challenge).

### Marche des rayons sur GPU (facultative, expérimentale)

Module `src/survol_gpu.py` :

- même fichier dans les 2 `src/` ;
- activé par `SURVOL_GPU=1`, import sous garde dans `survol.py` ; le CPU reste le défaut et le secours ;
- `taichi==1.7.2` (1.7.3 et 1.7.4 n'ont pas de roue macOS x86_64), backend Metal ;
- carte utilisée : celle que Metal choisit par défaut, l'AMD Radeon Pro 560 (l'Intel HD 630 est la carte basse consommation) ;
- seule la marche des rayons passe sur le GPU, pas le sol, la brume ni les arbres ;
- gain : marche 0,2–0,5 s → ~0,1 s, image 1,5–1,9 s → 0,7–0,8 s.

**Parité CPU / GPU** (atoll, 6 images) : 0 pixel d'écart sur l'indice de palette, mais 0 à 0,2 % des rayons diffèrent de
1–2 ulp sur la distance d'impact. Explication :

- la division Metal n'est pas arrondie au plus proche : 29 % des quotients diffèrent de numpy ;
- `div_rn` la corrige (division arrondie exactement), et elle est exacte quand on la teste seule (16 millions de cas) ;
- les quotients B/dxy sont calculés par numpy ;
- il reste un écart d'1 ulp sur `(pz − bm) / ndz` une fois tout le noyau compilé ; une barrière anti-fma n'y change rien.

Le bit près n'est donc pas garanti, et **les rendus livrés sont sur CPU**. Fait vérifié ajouté à `facts.md`.

Deux commentaires du code annoncent un résultat « au bit près » : la docstring de `survol_gpu.py` et le commentaire de
`survol.py` au-dessus de l'import GPU. Ils n'ont pas été modifiés, pour garder le md5 du moteur qui a fait les rendus. Les
`src/README.md` disent la limite.

### Intégration (18/11)

- **Images régénérées sans re-rendre les shorts** :
  - `stills/` : mêmes noms, mêmes instants, écart moyen 2/255 avec les images du `short.mp4` ;
  - `src/dive/` : série et planche ;
  - `poster.jpg` : le still de l'atoll à 13,5 s, comme avant ;
  - `contact-sheet.jpg` : les 9 stills.
- **Deux noms de stills ne décrivent plus l'image** :
  - `05_darwin-1842_17.0s` montre « basalte trouvé dessous en 1952 » (la plaque DARWIN passe de 15,0 à 16,8 s) ;
  - `04_revelee-1911_17.5s` montre « reconstitution stylisée » (la date passe de 15,1 à 16,9 s).
- **Documentation** : `identity.md`, `tokens.json` (v1.1.0 : 35 couleurs de noyau, `HAZE`, 6 paliers de brume, ciel en
  7 paliers, caméra, pas sûrs), `recipes/`, les 2 `src/README.md` (section GPU), les 2 `short.json` (coût, structure, SFX,
  mesures ; libellés de voix et `reproduce` intacts).
- **Chaîne** :
  - `aggregate.py` ;
  - `check.py --all` : **45/45** ;
  - `recognition.py` : **41/45 inchangé**, intra 0,235 contre inter 0,866 :
    - Machu Picchu est reconnu, son plus proche voisin est l'atoll (0,754) ;
    - l'atoll ne l'est toujours pas : il est plus proche d'aquarelle-conte « phare d'Alexandrie » (0,722), sa sœur arrive
      3ᵉ (0,754) ;
    - carte-meteo se rapproche : 2ᵉ voisin de Machu Picchu (0,785), 4ᵉ de l'atoll (0,770) ;
    - bloc `blindJudgeSurvol` conservé, mais jugé sur des images d'avant la passe ;
  - `build_index.py` : coût 107,2–266,3, rang 10 conservé ;
  - `catalogue_scan.py --check` : taichi et pyobjc (framework Metal) ajoutés au catalogue, carte `taichi.json` avec
    `usedBy` survol-pixel, motif `pyobjc Metal` ajouté au scan ;
  - vitrine régénérée en local avec `--videos-for survol-pixel`, **non republiée**.
- **À trancher par le propriétaire** :
  - le rang 10 : survol-pixel est désormais plus cher que topo-relief pour Machu Picchu, et que pastel-diorama ;
  - le scintillement des transitions, au-dessus de la source ;
  - la republication de la vitrine.

- **Moteur final** (après la phase 2 : module GPU branché sous garde, commentaires de parité corrigés) : `survol.py` md5 `77af51cf56252527124c1da4c960fc2d`, `survol_gpu.py` md5 `3fe2511babdb6770839da17583e2a2f2`, identiques dans les deux `src/`. Les commentaires ne changent pas le rendu CPU.
