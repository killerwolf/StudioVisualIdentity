# Journal studio — trait-continu (Trait continu)

Studio lancé le 2026-11-05. Heures en UTC. Autre studio en parallèle : carte-meteo (4 cœurs partagés).

## 00:32 — Lecture et installation
- Lu : STUDIO_BRIEF.md, AGENTS.md, facts.md, failures.md, directions §1, challenge §1 (correctifs obligatoires appliqués : traceur et non jouet, escalier ≥ 12 px, trait 6–8 px, bruit calculé une fois, Fredoka seule, pas de nostalgie, ≤ 33 mots / 15 s).
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
- Ce qui n'a pas été fait : la voix (Fish Audio Arnold) n'est pas enregistrée (narration écrite seulement) ; la variante « la plaque se démagnétise » (dissolution opensimplex) est documentée mais pas prouvée dans un short.
- Temps réel total du studio : ≈ 25 min (00:32 → 00:56).
