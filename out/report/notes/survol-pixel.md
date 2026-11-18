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
