# Relief Topo (`topo-relief`)

## Nom
**Relief Topo** — maquette topographique 3D d'expédition, courbes de niveau lumineuses et altimètre.

## Promesse en une phrase
Chaque sujet devient un **terrain qu'on survole** : le relief s'extrude sous nos yeux, les courbes de niveau s'allument en montant et un altimètre en chiffres mono dit exactement où l'on est.

## Mood & références de genre
Documentaire d'expédition, carnet de cordée, carte IGN réinventée en maquette de table, salle des cartes de nuit. Calme, précis, un peu héroïque. Pas de parchemin (c'est atlas-grave), pas de néon sur noir (c'est neon-lab) : ici le fond est **vert forêt**, la lueur est chaude (or) et minérale (menthe), et l'objet central est **un bloc de relief en volume** avec ses flancs striés comme des strates.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Couleur | Usage |
|---|---|---|
| Fond | `#14221C` vert forêt nuit | fond de scène, brouillard, dégradés haut/bas |
| Surface | `#1E3329` | flancs de la maquette, aplats hypsométriques bas |
| Accent 1 — or | `#E8C872` | altitude : HUD ALT, balises, courbes hautes (> 60 % de l'altitude max), mot-clé du titre |
| Accent 2 — terre cuite | `#D9734E` | kicker numéroté, itinéraire principal, flèches, anneaux radar |
| Accent 3 — menthe | `#9FD3C7` | courbes basses, coordonnées, sous-titres, hypothèses alternatives, géoïde, grille de table |
| Texte | `#F1EEDC` | titres Inter, silhouettes |
| Muted | `#9AA898` | mentions (« relief exagéré ») |
| Succès / danger | menthe / terre cuite | pas de rouge pur ni de vert pur |
Aplats hypsométriques (d3.scaleLinear) : `#12241b → #1E3329 → #33442d → #4d4a32 → #6a5f3e`. Contraste : texte crème sur fond ≥ 12:1, or sur fond ≈ 10:1, menthe ≈ 9:1, terre cuite ≈ 4.9:1 (kickers 54 px gras uniquement).

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Inter 800** — titres 100 px, interligne 1.0, interlettrage −3.5 px ; 1 à 3 lignes ; mot-clé en or (`<em>`).
- **JetBrains Mono 700** — altimètre 104 px (−2 px), 76 px pour une plage de valeurs ; kickers 54 px capitales (+2 px) en terre cuite ; étiquettes de balises 54 px.
- **JetBrains Mono 500** — coordonnées et sous-titres 54 px (+1 px) en menthe.
- Nombres au format français via `d3.formatLocale` (virgule décimale, espace insécable des milliers) : « 8 848,86 m ». Minimum absolu 54 px.

## Formes & matières
- **La maquette** : heightfield procédural 256×256 (bruit « ridged » + gaussiennes de massif / chaîne / cols), extrudé dans un bloc three.js de 12 unités, flancs à strates menthe, posé sur une grille de table menthe à 10 %.
- **Les courbes** : calculées par `d3.contours` (36–40 niveaux, maîtresse toutes les 5), peintes dans deux textures : carte hypsométrique mate (map) et lignes lumineuses avec halo `shadowBlur` (emissiveMap). La lueur est **cuite**, pas de bloom.
- **Balises** : point or + tige verticale + étiquette mono, projetées 3D -> 2D.
- **Itinéraires** : tubes lumineux (cœur + halo additif), terre cuite pour le tracé établi, menthe pour les hypothèses.
- **Neige** : calotte qui blanchit par shader (`uSnow`) et flocons ronds (Points + texture radiale).
- **Silhouettes inventées** : pictos d'éléphants génériques (ellipses + rectangles), jamais de personne réelle.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- `rise` = cubic-bezier(0.16, 0.84, 0.30, 1) : extrusion du relief (0.12–0.3 -> 1 en 2.2–2.6 s).
- Balayage des courbes `uLevel` 0 -> 1 en 2.8–3.1 s (inOutSine), avec bande de scan menthe ; l'altimètre est synchronisé dessus puis tenu.
- `glide` = cubic-bezier(0.45, 0, 0.25, 1) : déplacements caméra entre images clés (beats de 2.2–3.6 s).
- Texte : entrée outCubic 0.3 s (fondu + 26 px de montée), sortie inCubic 0.3 s ; balises en cascade de 0.25 s.
- Boucles d'ambiance : impulsions le long des faisceaux, anneaux radar, flocons, pas d'éléphants — toujours lents.
- **Jamais** : secousses, zooms brusques, rebonds élastiques, bloom néon, texte qui défile, chiffres sans unité, coupe sèche au milieu d'un survol.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
- PerspectiveCamera fov vertical 54° (≈ 35 mm) ; plongée 40–60° ; le sujet tient dans la fenêtre y 420–1150.
- Mouvements : orbite drone lente, suivi d'itinéraire par l'arrière avec avance de visée, plan rasant pour un « niveau zéro », recul final vers la vue de maquette.
- Images clés `(t, azimut, rayon, hauteur, visée)` interpolées en `glide` ; scène sans état (rendu parallélisable, seekable).
- Pas de profondeur de champ : net partout ; le **brouillard couleur fond** (9 -> 40 unités) fait la perspective atmosphérique.

## Transitions (liste nommée, durée, quand les utiliser)
| Nom | Durée | Quand |
|---|---|---|
| courbes-qui-montent | 3.0 s | ouverture : extrusion + courbes qui s'allument (dans la scène) |
| survol | 2.2–3.6 s | changement de beat : la caméra glisse, le bloc texte fait fondu 0.3 s |
| fondu-carte (xfade `fade`) | 0.6 s | seulement si l'on concatène deux plans : fondu au vert forêt |
| recul-maquette | 2.4–2.8 s | fin : recul et plongée vers la vue large |

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
- **0–1 s** : titre-question Inter présent dès la frame 0 + relief qui s'extrude + courbes qui s'allument + altimètre qui compte.
- **~3 s** : l'altitude/le contexte est posé (impact sonore).
- **3–12 s** : 3 à 4 beats numérotés (kicker mono terre cuite « 01 / … »), un objet 3D par beat (satellites, anneaux, nappe, itinéraire, balises).
- **12–15 s** : chute (nuance, débat, « ça bouge encore ») + question d'engagement ; recul vers la maquette, tenue propre.

## Zones sûres
Haut 220 px (HUD à partir de y=236), bas 320 px (rien sous y≈1600), droite 120 px (texte ≤ x=960). Fenêtre relief y 420–1150 ; bloc texte y 1170–1600. Dégradé haut 0–470 px et bas à partir de 1040 px pour garantir le contraste du texte au-dessus du relief.

## Librairies recommandées et pourquoi
- **three.js** : relief extrudé, shader `onBeforeCompile` sur MeshStandardMaterial (balayage d'altitude, neige), sprites lumineux, tubes, projection des balises. Éviter transmission et UnrealBloom (coût mesuré dans facts.md).
- **D3.js** : `d3.contours` (isolignes du heightfield), `d3.geoPath` + `geoTransform` vers canvas, `d3.scaleLinear` (teintes hypsométriques, couleur des lignes), `d3.formatLocale` (nombres FR).
- DOM/CSS pour toute la typo (polices @fontsource via `S.loadFonts`), `svi.js` pour le contrat et le bruit.

## Familles de contenus adaptées / inadaptées
- **Adaptées** : géographie (sommets, volcans, fleuves, failles, glaciers), histoire d'itinéraires (traversées, expéditions, batailles en terrain), explicatif sciences de la Terre (tectonique, érosion, mesure).
- **Possibles** : événements liés à un lieu (éruption, séisme), engagement « quel chemin choisirais-tu ? ».
- **Inadaptées** : enfants (palette sombre, ton sérieux), abstrait pur, sujets sans lieu ni altitude, données statistiques plates (swiss-data le fait mieux).

## Shorts de preuve (chemins)
- `out/shorts/topo-relief__geographie__comment-mesure-t-on-l-everest/` — 15 s, three.js + D3.js.
- `out/shorts/topo-relief__histoire__hannibal-traverse-les-alpes/` — 15 s, three.js + D3.js.

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)

> **Voix réellement utilisée pour tous les shorts : Fish Audio « Arnold »** (`d704cf8f1216490cbfbed89955f0e938`, modèle `s2.1-pro`, conteur masculin FR). Les noms de voix Gemini (Orus, Kore, Aoede…) qui suivent sont des suggestions historiques de casting par ton : Gemini a été abandonné (quota). Le placement, le débit et les silences décrits ici restent valables.

Voix documentaire grave (Gemini **Orus**), une phrase courte par beat, ≈ 2,3–2,5 mots/s, posée sur le début de chaque survol (0.1 s après le changement de kicker). L'écran ne porte que titres, chiffres et mots-clés : la voix raconte le « comment » (méthode, contexte), l'écran montre le « combien » (altitude, nombre). Les survols de 2–3 s laissent de l'air ; le drone sonore est à −18 dB et peut être duqué.

## Risques et limites
- **Coût** : three.js + relief 256² + textures 2048² ≈ 169 s / 100 frames sous contention (4 studios) ; prévoir 12–15 min pour 15 s.
- **Lisibilité** : en plongée verticale, il est difficile de voir à la fois le départ d'un itinéraire et la crête : reculer la caméra (R ≈ 10, h ≈ 11) et utiliser la « visée » pour placer la tête de tracé au tiers médian.
- **Exactitude** : relief stylisé, jamais un MNT ; le dire si l'on exagère (« relief exagéré ») et signaler les débats (cols d'Hannibal).
- **Proximité** : ne pas glisser vers neon-lab (pas de bloom, pas de fond noir) ni vers atlas-grave (pas de carte plate, pas de serif).
- Les glyphes flèches de JetBrains Mono ne sont pas tous dans le sous-ensemble latin chargé (« → » a disparu à l'écran) : écrire en toutes lettres.
