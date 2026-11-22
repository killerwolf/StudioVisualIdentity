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

## Retouche Fable (18/11)

Passe de retouche dirigée par le directeur artistique « Fable » (décision 38 du propriétaire) : 6 retouches classées par
impact sur la ressemblance de style, appliquées en une passe, puis les 2 shorts re-rendus sur CPU. Rapport et essais de
Fable hors dépôt ; planche avant / après : `notes/console-retro-source/retouche-fable.jpg` (même mise en page que
`final-abc.jpg`, AVANT = `short.mp4` du commit HEAD, APRÈS = nouveau `short.mp4`).

Inchangés : moteur de profondeur (4 rayons, vote, carte fine, pas sûrs), brume en 6 paliers, cartouches et leurs temps,
voix et `narration.json`, temps des clés de caméra, caméra de Machu Picchu, plans de coupe (à Machu Picchu, le fond du
plan de coupe change : le pain de sucre y est un cône vert au lieu d'une tour grise), terrasses, cité, anneau.

### Les retouches

1. **Nuages** (les deux shorts) :
   - `survol.py`, `draw_clouds` : la hachure une ligne sur deux (« store ») devient un **modelé tramé en damier** sur le
     tiers bas droit, plus un croissant plein `HATCH` tout en bas. Seule modification du moteur, hors `Renderer._march` :
     la parité GPU n'est pas à refaire. Nouveau md5 de `survol.py` : `fcd91b270940396784d5e986d9dcd57b`, identique dans
     les 2 `src/` ; `survol_gpu.py` inchangé (`3fe2511babdb6770839da17583e2a2f2`).
   - atoll : 100 nuages (70), rayon 11–20 (8–13), espacement 36 (40) ; exclusion de l'anneau et marge caméra gardées.
   - Machu Picchu : 60 nuages (40), rayon 9–16 × K (7–11 × K), 36 lointains (26).
   - Contrôle géométrique toutes les 0,1 s (`check_clouds.py`, hors dépôt) : l'anneau, la coupe et la cité ne sont
     jamais cachés à plus de 5 % ; cartouches dessinés après les nuages. Nuages visibles (rayon ≥ 2 px) : médiane 17
     (atoll) et 12 (Machu Picchu) par image ; au moins 6 sur 91 % et 99 % des images.
2. **Écume de l'atoll** : traits de 4 unités le long de Y, ½ à 1 unité de large, `LAGOON` à tête `FOAM`, même hachage
   dans la mer extérieure, la fenêtre fine et la tuile au-delà du monde (pas de couture vue à la frontière de la fenêtre
   à 0,0 et 18,5 s).
3. **Forêt de Machu Picchu** :
   - nouvelle couleur de biome `FOREST_SH` `#0F3620` ; ombre `FOREST → FOREST_SH`, `FOREST_SH → INK` ; même rampe de
     brume que `INK` ;
   - variante C de Fable (`essai2.py`) : sol `GRASS_D`, clairières `GRASS_M` (seuil 0,40), sous-bois `FOREST` par grandes
     plages (bruit d'échelle 14 < −0,35) ; arbres `density 0,5, r 0,9–2,2`, en bouquets ; la variante B (arbres sombres
     sur sol moyen) n'est pas reprise ;
   - plus loin que l'essai, comme Fable le demandait : `FOREST` réservé aux pieds de marche dans `nat` et dans la carte
     grossière (clairières `GRASS_M` en plages). **Cela ne suffisait pas** : 17–21 % de pixels sombres en survol. La
     mesure par couleur montre que le sombre venait des **contremarches ombrées** (`fd = FOREST`) du flanc boisé, vu de
     face. **Écart au rapport, à valider par le propriétaire** : contremarches naturelles éclaircies d'un ton, éclairée
     `GRASS_M` / ombrée `GRASS_D` (au lieu de `GRASS_D` / `FOREST`) ; les contremarches de pierre (terrasses, cité) ne
     changent pas. Les leviers de Fable seuls donnaient 17–21,5 % de pixels sombres en survol (natif) ; avec ce levier,
     7–15 % en natif et 12,7 % sur le fichier. Le risque nommé par Fable (terrasses moins détachées de la forêt) est en
     partie pris : la face éclairée d'une contremarche de forêt a maintenant le ton `GRASS_M` de la bande basse des
     terrasses ; sur la planche, les terrasses se détachent encore. Revenir en arrière : 2 valeurs dans `world()` et
     ≈ 20 min de rendu de Machu Picchu.
4. **Caméra de l'atoll** (clés 0,0 et 18,6 s seulement, aucun temps déplacé) : 0,0 s `ty C0−110, dist 300, pitch 33` ;
   18,6 s `tx C0−6, ty C0+40, dist 310, pitch 30, roll −10`, lacet −22. Le plan final montre l'anneau entier, la coupe
   et l'horizon ; pas de cadrage vu du nord. `--preflight` : marge 85,8 (inchangée).
5. **Pain de sucre** : `gauss(…, 25 × K, 21 × K, 104 × K)`. Diagnostic : l'« aiguille grise » n'était pas le granite
   du sommet mais les **murs de pierre des terrasses agricoles** (couronne `agz`, 1 ≤ e < 2,2) qui montaient sur le
   flanc sud du pic. Correction : les cellules de la couronne où le relief naturel dépasse la jupe des terrasses de
   2 × K, au nord (`peak`), redeviennent du relief naturel boisé (et reçoivent des arbres). Le seuil du granite n'a
   **pas** été monté à 112 × K comme proposé : le sommet du pic fait 105 × K, le garder à 100 × K laisse une petite cime
   de granite (2 marches) sur des flancs boisés. Le seuil est désormais une carte (`RZ`), uniforme. `--preflight` :
   41,6 (inchangé).
6. **Finitions** :
   - rampe du ciel resserrée dans les 2 `video.py` : `(0,4 HAZE) (1,2 SKY_1) (2,4 SKY_LO) (4 SKY_2) (6,5 SKY_MID)
     (10 SKY_4) (90 SKY_HI)` ;
   - socle de la coupe de l'atoll : une dalle sombre sur douze (part 0,33 → 0,08) ;
   - « treillis » au bord gauche de Machu Picchu (4,5 et 17,5 s) : **cause trouvée, non corrigée**. C'est la limite
     entre la couronne des terrasses agricoles (marches de 2,9) et le flanc naturel (marches de 6,3) : de petits murs de
     pierre de hauteurs variées, vus de profil, en zigzag. La corriger touche aux terrasses, hors du périmètre.
   - **Ajout hors rapport, atoll** : garde-fou `cap_colors` (≤ 32 indices par image, critère du challenge). Avec la
     rampe de ciel resserrée, `SKY_MID` apparaît dans la bande de ciel et 9,5–11 s et 13,5 s montaient à 33 indices. La
     couleur la plus rare (1 à 10 pixels natifs de brume lointaine `HZ_G3` / `HZ_R1`) est fondue dans la couleur
     présente la plus proche ; cartouches et nuages protégés ; sans effet sous 33. Machu Picchu reste à 19–29 indices.

Son : aucun événement visible n'a changé de temps (nuages sans bruitage, clés de caméra aux mêmes temps) ; `sound.json`
inchangé.

### Rendus (CPU, sans `SURVOL_GPU`)

| Short | Images | Durée | s/100 images | Charge 1 min | Monde |
|---|---|---|---|---|---|
| Atoll (livré, seul) | 558 | 356,6 s | **63,9** | 3,79 → 3,44 | 6,5 s |
| Atoll (1er rendu, sans garde-fou, en parallèle) | 558 | 458,1 s | 82,1 | 3,79 → 5,02 | 15,1 s |
| Machu Picchu (en parallèle du 1er rendu de l'atoll pendant ≈ 8 min) | 564 | 1 209,4 s | **214,43** | 3,77 → 2,88 | 28,6 s |

Avant la retouche (passe A+B+C, les deux en parallèle, charge 4,4–10,4) : 107,18 et 266,29 s/100. Les rendus sont plus
rapides surtout parce que la machine était moins chargée ; la retouche n'ajoute pas de coût mesurable.

Chaîne : `sound.py`, `assemble.py mux`, copie vers `short_novo.mp4`, `tts.py --engine files --replace` (voix existante,
aucun appel), libellés Gemini Sulafat remis dans `voice_report.json` et `short.json` (fichiers identiques au commit
HEAD). `check.py` : ok, 0 avertissement, sur les 2 shorts.

### Mesures après, contre les critères de Fable

`measure2.py` de Fable sur les nouveaux `short.mp4` (30 i/s, 1 px par gros pixel) :

| Mesure | Critère | Atoll avant → après | Machu Picchu avant → après |
|---|---|---|---|
| A-B-A, short entier | atoll ≤ 2,5 % | 0,87 → **0,57 %** | 2,00 → 2,10 % |
| A-B-A, pire fenêtre | (source 3,4 %) | 1,78 → 1,38 % (bascule) | 4,29 → 4,49 % (piqué) |
| Pixels qui changent par image | atoll ≥ 12 % à 0–2,9 et 15–18,6 s | 6,5 → 5,2 % ; accroche 6,5 → **7,0 %**, final 11,4 → **5,6 %** | 21,6 → 20,4 % |
| Pixels sombres (lum. < 70) | ≤ 15 % en survol | 2,1 → 3,1 % | 21,8 → **12,0 %** ; survol 24,0 → **12,7 %**, piqué 28,1 → 15,1 % |
| `INK` hors coupe (natif) | ≤ 3 % | — | 0,5–2,5 % (5,8 % au piqué, 8,1 % à la coupe : joints de pierre) |
| Nuages `CLOUD+HATCH+CLOUD_RIM` (natif) | 3–8 % en médiane | 1,3–5,5 % (médiane ≈ 3,6) | 1,4–9,2 % (médiane ≈ 4,7) |
| `SH_WATER` (natif, atoll) | 2–6 % | 0,6–2,6 % | — |
| Nuages visibles, hors plan de coupe | ≥ 6 sur 80 % des images | **81 %** (91 % avec la coupe) | 99 % |
| Couleurs par image (natif, cartouches) | ≤ 32 | 24–32 | 19–29 |
| Écume à 1,5 s, moitié basse hors anneau | ≥ 80 % des taches ≥ 3 px, aucun pixel isolé | **53 %** ; 10 pixels isolés sur 55 taches | — |
| Ciel | ≥ 3 paliers quand il dépasse 5 % | tenu (pas de 0,5 s) | tenu |
| Plan final à 18,5 s | anneau entier ; horizon à 8–20 % | anneau entier ; horizon à 10,2 % | — |
| Socle | ≤ 1 dalle sur 10 d'une autre teinte | 8,0 % | — |
| Pain de sucre (0,6 / 17,5 s) | largeur à mi-hauteur ≥ 40 % de la hauteur visible ; granite ≤ 50 % | — | 69 / 72 % ; granite 14,8 % des cellules au-dessus de la cité (cime) |
| Reconnaissance | voisin de Machu Picchu = l'atoll | — | l'atoll (0,764) |

| Son | Atoll | Machu Picchu |
|---|---|---|
| Loudness intégrée ; crête ; LRA (ebur128) | −16,0 LUFS ; −1,7 dBFS ; 5,3 LU | −13,8 LUFS ; −1,5 dBFS ; 3,9 LU |

Taille : atoll 6,6 Mo (8,9), Machu Picchu 13,2 Mo (13,8).

**Écarts** :
- **Mouvement de l'atoll non atteint** (≥ 12 % visé). L'accroche gagne peu (7,0 %), le plan final perd (5,6 % contre
  11,4 %) : reculer à 310 unités pour avoir l'anneau entier ralentit le défilement à l'écran. Essai de lacet plus fort
  sur les deux clés (mesure native, `motion.py` hors dépôt) : 7,3 → 9,1 % (lacet −55 / −50), 10,0 % (−70 / −62), sans
  atteindre 12 %, au prix du cadrage choisi par Fable : non retenu. Atteindre 12 % demanderait de déplacer des temps de
  clé ou d'accélérer la caméra, ce qui était exclu.
- **Pixels sombres de Machu Picchu** : critère tenu en survol (12,7 %), à la limite au piqué (15,1 %), mais par un levier
  hors rapport (contremarches naturelles éclaircies).
- **Nuages** : la médiane native reste dans le bas de la fourchette à l'atoll (≈ 3,6 %), les nuages proches étant exclus
  autour de l'anneau et de la trajectoire de la caméra ; ≥ 6 nuages visibles sur 81 % des images hors coupe (limite).
- **Écume** : 53 % des taches du large font ≥ 3 px (80 % visés) : au loin, la réduction de carte rend les traits en
  points (le risque prévu par Fable) ; de près, les traits sont nets.
- **Scintillement de Machu Picchu** : stable (2,00 → 2,10 % sur tout le short, 4,29 → 4,49 % au piqué), toujours un peu
  au-dessus de la source au piqué.

### Intégration

- Images régénérées : `stills/` (mêmes noms, mêmes instants), `src/dive/` (série et planche ; 19–31 et 18–27
  couleurs), `poster.jpg` (atoll à 13,5 s), `contact-sheet.jpg` (9 stills).
- Documentation : `identity.md` (nuages, écume, forêt, contremarches, socle, caméra, ciel, palette 41 à Machu Picchu),
  `tokens.json` v1.2.0 (`FOREST_SH`, ciel, nuages, écume, forêt, socle, coût), les 2 `short.json` (coût, couleurs,
  nuages, mesures, notes ; SFX et `reproduce` inchangés), les 2 `src/README.md`, `build_index.py` (note de coût).
- Chaîne : `aggregate.py` ; `check.py --all` **45/45** ; `recognition.py` **41/45 inchangé** (intra 0,235, inter
  0,864) : Machu Picchu reconnu, plus proche voisin l'atoll (0,764) ; l'atoll toujours plus proche d'aquarelle-conte
  « phare d'Alexandrie » (0,690, avant 0,722) ; bloc `blindJudgeSurvol` conservé (jugé sur des images de la passe de
  détail) ; `build_index.py` : coût 63,9–214,4, rang 10 conservé ; `catalogue_scan.py --check` sans écart ; vitrine
  régénérée en local avec `--videos-for survol-pixel`, **non republiée**.

- **Rejugement de Fable (18/11)** : retouches 1 réussie à Machu Picchu / partielle à l'atoll, 2 partielle, 3 réussie, 4 cadrage réussi / mouvement raté, 5 partielle, 6 réussie (sauf ciel de Machu Picchu en vue haute). Les 3 écarts du studio sont gardés (contremarches éclaircies, murs sortis du pain de sucre avec granite à 100 × K, cap_colors). Fable recommande d'arrêter là : ce qui reste (atoll presque immobile, mer à moitié vide, pas de terre verte) tient au sujet et à la règle « pas d'archipel ». Rapports : `fable-retouches-2026-11-18.md`, `fable-rejugement-2026-11-18.md`.

## Ancienne section survol-pixel d'AGENTS.md (archivée le 2026-11-21)

Déplacée ici pendant l'harmonisation des identités, pour que la section d'`AGENTS.md` garde la même forme que celle du lot 2. Texte d'origine, inchangé :

- **Owner rules** (signature, keep them): (1) **3D depth** is the rule — perspective ground (Mode 7 style) at any pitch, terraces,
  cast shadows, layered depth, a camera that moves forward; (2) **form, not content** — a pixel-art look for explainers, kids, history
  and narrated shorts, not a video-game or flight theme (no score, no game element; HUD and cockpit optional, absent from the proofs).
- A new identity, **not a derivation of pixel-arcade**: other engine (one 3D camera, numpy ray casting on a terraced heightfield),
  other fonts (Jersey, not Press Start 2P), other transition (the dive / climb-back, not a pixel mosaic), other sound (no chiptune blips).
- Engine: pure Python `survol.py` (identical md5 in both shorts' `src/`), `video.py` per short; opensimplex fields cached in
  `$SURVOL_CACHE` (outside the repository). A new topic = a new terrain / heightfield, a camera path, sprites with shadows and the cut-away.
- **Detail pass (2026-11-18)**: sub-cell micro-detail, coursed walls, ball-heap clouds, tree clusters with cast shadows; both shorts
  re-rendered (`out/report/notes/survol-pixel-detail.md`). The challenge's « ≤ 4 clouds » cap (C15) is lifted (3–11 clouds in frame);
  the owner reopened C15 in the A+B+C pass (other atolls far away, more clouds, but no green archipelago copied from the source).
- **A+B+C pass (2026-11-18)**, owner request: (A) a world filled to the horizon (atoll 1,080 units with other atolls, seamounts, banks;
  Machu Picchu 1,536 units of Andean ridges) and a new haze in 6 steps with a world-fixed jagged border towards a very pale blue
  `HAZE #DCEEF5`, sky in 7 steps (11 core colours added, 35 in all); (B) 4 rays per pixel with a majority vote on the palette index,
  a 4× finer colour map around the subject, slope bias and « far wall = top colour » rule removed, relief cast shadow, safe-step ray
  march on block max maps (128/32/8/2) + 8 bisections; (C) a PCHIP camera that flies, banks and rolls (5–13°), one Jersey 15 cartouche
  at a time; Machu Picchu's dive (8.0 → 10.0 s) and climb-back (13.4 → 15.6 s) slowed down (owner decision). Owner decisions 34 and 36:
  atoll cartouches « il y a des millions / d'années », « pendant des millions / d'années », the « lagon » pin and the final « basalte » /
  « calcaire » pins removed; « reconstitution stylisée » only at the end (16.9–18.8 s); haze tables relaxed to 6 steps. Full CPU renders
  (both in parallel on 4 cores): **atoll 107.18 s/100 frames (598.1 s), Machu Picchu 266.29 (1,501.9 s)**, 1-min load 4.4–10.4; the
  owner lifted the cost cap for B. Flicker is the main remaining risk: A-B-A pixels on the decoded files 3.56 % over Machu Picchu
  (1.40 % before), 7.3 % in its dive and 5.4 % in its climb-back (source 4.0 %); atoll 1.06 %. Voice remixed on the new timings without
  any new call. Before / after board: `out/report/notes/console-retro-source/final-abc.jpg`; log `out/report/notes/survol-pixel.md`
  § « Passe A+B+C ».
- **Optional GPU ray march** (`src/survol_gpu.py`, same file in both shorts): `SURVOL_GPU=1`, `taichi==1.7.2`, Metal (AMD Radeon Pro 560,
  the default Metal device); only the ray march moves to the GPU, frame 1.5–1.9 s → 0.7–0.8 s. Not bit-exact (Metal division is not
  correctly rounded; 0 px palette-index difference on 6 frames but 0–0.2 % of rays off by 1–2 ulp, see `out/report/facts.md`), so the
  delivered renders are CPU and the module stays experimental; CPU remains the default and the fallback.
- **Fable retouch (2026-11-18, owner decision 38)**: 6 art-director fixes in one pass, both shorts re-rendered on CPU with the same voice and timings:
  bigger, more numerous clouds with a dithered underside (the only engine change, `draw_clouds`), foam strokes on the atoll sea, a light Machu Picchu forest
  with a dark-green `FOREST_SH` shadow (no more navy), a wider forested sugarloaf, a wider final atoll shot, a tighter sky ramp. Cost 63.9–214.4 s/100 frames;
  the atoll's on-screen motion is still below Fable's target (`out/report/notes/survol-pixel.md` § « Retouche Fable »).
- **Voice-over: Gemini « Sulafat »** (owner decision, 2026-11-18), the lot 2 recipe: one `gemini-3.8-flash-tts` call per short, split
  into `voice_lines/NN.mp3` by word timestamps, mixed by `tts.py --engine files --replace` (`short_novo.mp4` = music + SFX). The call
  needs API **v1beta** (see `out/report/facts.md`). Atoll 18.6 s at −16.0 LUFS (peak −1.7 dBFS), Machu Picchu 18.8 s at −13.8 LUFS (peak −1.5 dBFS), after the A+B+C remix (−15.9 / −13.7 before). Log:
  `out/report/notes/voix-survol-pixel.md`.
- Evidence: 2 proof shorts (`explicatif` atoll, `histoire` Machu Picchu), QA ok (0 warnings). **Blind visual judge**
  (during the review, fresh agent, 24 anonymised frames, survol-pixel + pixel-arcade, carte-meteo, topo-relief, pastel-diorama,
  trait-continu): **6/6 pure groups, 24/24** (`recognition.json` → `blindJudgeSurvol`; frames from the detail pass, it does not cover the
  A+B+C pass). Measured recognition (after the A+B+C pass, 41/45 overall, unchanged): Machu Picchu's nearest neighbour is its sibling
  (0.754); the **atoll still fails** (nearest aquarelle-conte « phare d'Alexandrie » at 0.722, sibling 3rd at 0.754: blue ocean against
  green mountain); carte-meteo moved closer (2nd neighbour of Machu Picchu at 0.785); colour + edges miss its signature, which is
  geometric (perspective, terraces, pixel grid). Render cost 107.18–266.29 s/100 frames on CPU under load (A+B+C renders, 1-min load
  4.4–10.4, `measuredUnderLoad: true`; 19.6–63.1 after the detail pass, 15.6–59.1 before it).
