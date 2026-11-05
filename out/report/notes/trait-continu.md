# Journal studio — trait-continu (Trait continu)

Studio lancé le 2026-11-05. Heures en UTC. Autre studio en parallèle : carte-meteo (4 cœurs partagés).

## 00:32 — Lecture et installation
- Lu : STUDIO_BRIEF.md, AGENTS.md, facts.md, failures.md, directions §1, challenge §1 (correctifs obligatoires appliqués : traceur et non objet de loisir, escalier ≥ 12 px, trait 6–8 px, bruit calculé une fois, Fredoka seule, pas d'argument de souvenir, ≤ 33 mots / 15 s).
- Installé (seul usage de pip du studio) : `/root/.local/bin/uv pip install --python .venv/bin/python shapely==2.2.0 opensimplex==0.4.5.1` → 2 paquets en 6 ms ; `import shapely, opensimplex` OK.
- Versions : shapely 2.2.0, opensimplex 0.4.5.1, numpy 2.4.6, pycairo 1.29.2, Pillow 13.0.0, ffmpeg 6.1.1. Charge machine 0,05.

## 00:35–00:45 — Moteur et premier still
- Moteur commun `src/traceur.py` (copie identique dans les 2 shorts) : shapely construit le chemin (segmentize 2 px → grille de 12 px, un seul axe par pas → escalier ; `linemerge` pour raccorder les morceaux du corps ; `nearest_points` pour le pont vers une composante disjointe : la Sicile ; `simplify(1,2 px)` sur le contour de l'Italie ; `substring(chemin, 0, L(t))` pour l'état à t). Jalons exacts : chaque pas fait 12 px, donc longueur au jalon = index × 12.
- Piège 1 : ma classe `Path` masquait `pathlib.Path` (TypeError) → renommée `Trace`.
- Piège 2 : on ne peut pas poser d'attribut sur une `cairo.ImageSurface` (garder le tampon numpy vivant) → liste globale `_KEEP`.
- Piège 3 : `simplify(0)` de shapely supprimerait les demi-tours (allers-retours des antennes, colinéaires) → fusion des points alignés **de même sens** écrite à la main.
- opensimplex : champs fine (410×480) + coarse (102×120) + vibration (2×4096) = **≈ 4,0 s une seule fois**, mis en cache `/tmp/svi/<dossier>/noise_seed<N>.npz` ; ensuite 0 s. Jamais appelé par image.
- **Premier still (t = 4 s, escargot)** regardé réduit à 360 px : on lit en 1 s le fond orange plein, la plaque grise à angles vifs, le trait unique en escalier, les deux curseurs sur les règles (haut, gauche) et le chariot carré. Coût : **36–46 ms/image** (≈ 4 s / 100 images, machine calme, charge 0,1).
- Corrections après stills : (1) le titre passait par-dessus la plaque pendant l'avance et 3 images étaient presque entièrement orange → plaques dessinées au-dessus de la bande titre, plaque vierge qui commence à entrer pendant le 3ᵉ cran (`OVERLAP = 0,45 s`), titre suivant dès que la bande est dégagée ; (2) escargot 1 agrandi (R 150 → 172), tête plus ronde.
- Italie : la botte du hook sortait de la plaque (rotation/échelle mal placées) → ajustement automatique de la boîte englobante ; « Pouilles » recouvrait la pointe → étiquette dans l'Adriatique + fil de repère bleu vers le talon ; contour 80 points saisis à la main → 74 après `simplify`, Sicile 18 points.
- Narration : 5 lignes chacun, 28 mots (escargot) et 30 mots (Italie), `maxDuration ≥ mots / 2,2`, sans chevauchement (arrêts du traceur de 1,9 s au talon et 1,7 s à la pointe pour caler les lignes).

## 00:46 — Rendus complets lancés (arrière-plan, `out/tools/slot.sh`), charge 1,7 (carte-meteo actif)
- Escargot : rendu complet **21,1 s** pour 465 images (4,55 s / 100 images) ; Italie : **21,5 s** pour 480 images (4,49 s / 100 images). Les deux en parallèle, avec carte-meteo actif (charge 1,7 → 5,5). Un seul rendu complet par short.

## 00:47 — Son, mux, vérifications
- `sound.json` : music-box majpent 92 bpm + événements générés depuis la scène (`video.py --sound-json`) : `tick` toutes les 0,24 s quand le traceur avance, `click` à chaque cran et chaque arrêt, `thud` au clac, `pop` / `chime` sur les repères. 50 et 41 événements.
- Narration escargot : ligne 4 « La plupart tournent vers la droite. » faisait 6 mots (2,73 s) et aurait chevauché la question finale → « La plupart tournent à droite. » (5 mots). Hook Italie réécrit en vraie question d'enfant sans promesse d'explication causale : « C'est vrai que l'Italie a la forme d'une botte ? ».
- 5 frames du fichier final de chaque short extraites et regardées ; `check.py` : **OK** pour les deux (avertissement seul : voix off prévue, non enregistrée).
- Déterminisme : second rendu de l'escargot → **md5 du mp4 identique** (c28b0879…) ; ce second rendu a pris 13,0 s (2,79 s / 100 images, charge plus basse).
- Mesures pour les cartes : shapely `substring` + `interpolate` ≈ 0,02 s / 100 images (223 sommets, 4 116 px) ; construction du chemin 1–3 ms ; opensimplex 3,83 s une fois (cache .npz).
- Poids : 1,3 Mo par short (aplats).

## 00:50–00:55 — Design system
- `identity.md` (16 sections), `tokens.json`, `recipes/enfants.md`, `recipes/geographie.md`, `poster.jpg` (escargot à 4,0 s), `contact-sheet.jpg` (9 frames, 3 colonnes).
- Cartes : `_drafts/trait-continu__shapely.json`, `_drafts/trait-continu__opensimplex.json`.
- Ce qui n'a pas été fait : la voix (Fish Audio Arnold) n'est pas enregistrée (narration écrite seulement) ; la variante « la plaque se vide » (dissolution opensimplex) est documentée mais pas prouvée dans un short.
- Temps réel total du studio : ≈ 25 min (00:32 → 00:56).

## 01:05–01:20 — Corrections de la revue finale (out/report/notes/revue-2026-11-05.md, section trait-continu)
- **Avance plaque** : la revue mesurait 3 images (escargot, 5,90–5,97 s) et 2 (Italie, 4,23–4,27 s) à plus de 85 % d'orange uni. Mon sondage (scratchpad `orange_probe.py`, part de pixels à ± 24 de `#F26A21`) reproduit exactement ces chiffres. Dans le code, `OVERLAP = 0,45` était en fait le **délai** avant l'entrée de la plaque vierge (et non un chevauchement) : le porter à 0,55 l'aurait fait entrer plus tard. Délais essayés : 0,45 → 3 et 2 images > 85 % (max 97,6 %) ; 0,35 → 0 (max 80,4 %) ; 0,30 → 0 (max 80,4 %) ; **0,25 → 0 (max 77,7 %)**. Retenu : `ENTER_DELAY = 0,25 s` (chevauchement réel `OVERLAP = 3 × 0,2 − 0,25 = 0,35 s`, contre 0,15 s avant) ; le clac tombe pile à la fin du 3ᵉ cran. Plancher normal hors transition ≈ 62 % d'orange (la plaque couvre 38 % du cadre).
- Conséquence : plaque 2 et narration avancées de 0,2 s (escargot ligne 3 : 6,35 → 6,25 ; Italie lignes 2–5 : −0,2 s). `sound.json` régénérés (50 et 41 événements). `voice_lines/00.mp3` de l'escargot laissé tel quel (ligne 1 inchangée à 0,2 s).
- **Rendus complets v2** (un par short, `slot.sh`, en parallèle, charge ≈ 3,3) : escargot **22,8 s** / 465 images (4,91 s / 100) ; Italie **23,4 s** / 480 images (4,87 s / 100). Mesure sur les fichiers finaux muxés (42 images de transition chacun) : maximum 77,7 % et 76,9 % d'orange, 0 image > 85 %.
- **Vocabulaire** : trois termes de la v1 (la matière du grain, le métal de la plaque et le nom de la variante d'effacement) décrivaient le mécanisme d'objets du commerce. Remplacés par « grain de surface », « plaque gris métal », « grain de mine de crayon » (trait) et « la plaque se vide » (variante). Les interdits d'identity.md sont reformulés sans les mots du produit (« objet de dessin du commerce », « boutons ronds », « agitation de l'objet », « souvenir d'enfance »). Fichiers : traceur.py (×2), identity.md, tokens.json, carte opensimplex, ce journal.
- **Escargot, sens de la coquille** : note ajoutée (short.json `notes`, identity.md Risques) : « dextre » se juge vu depuis l'apex ; la flèche horaire sur un escargot de profil est une simplification ; « la plupart tournent à droite » reste juste.
- Détails de la revue repris : bande titre 230–470 dans identity.md, vitesses 820 / 850 / 900 px/s, `uv` au lieu de `/root/.local/bin/uv` dans les README, transition 0,6 s dans tokens/identity/recettes, stills de transition remplacés (5,85 s et 4,15 s), poster et planche-contact refaits.
- Vérification : `grep -riE "poudre|aluminium|démagnétise|molette|secousse|jouet|nostalgie"` sur out/identities/trait-continu et les 2 dossiers de shorts → aucune occurrence (exit 1). `check.py` : OK pour les 2. Nouvel avertissement escargot : « image figée ≥ 3 s à 12 s » (tenue finale de 3,47 s sur le dessin complet et la question, 0,2 s plus longue qu'en v1) : c'est une fin propre voulue, laissée sans re-rendu (un seul rendu par short).
