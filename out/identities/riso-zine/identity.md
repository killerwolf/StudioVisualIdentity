# Zine Riso — identité `riso-zine`

## Nom
**Zine Riso** (`riso-zine`) : un fanzine photocopié-risographié qu'on feuillette, page par page, pour les sujets géographie et événements.

## Promesse en une phrase
Un chiffre fort, une forme découpée, une annotation au marqueur : la géo et l'agenda racontés comme un fanzine imprimé à la main, en trois encres qui débordent.

## Mood & références de genre
Fanzine indé, impression risographie bicolore/tricolore, affiche de concert, collage aux ciseaux, agenda punk. Imperfection chaleureuse et curiosité : encres fluo qui se superposent (multiply), repérage qui bouge, trame visible, papier crème qui tremble. Animation **on twos** (12 pas/s) : tout saccade un peu, comme un flip-book. L'inverse de swiss-data (grille propre, aplats nets, volets rouges, Archivo Black) et d'atlas-grave (gravure, parchemin, sépia) : ici rien n'est aligné au pixel, tout est imprimé en points.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Valeur | Usage |
|---|---|---|
| Fond / surface | `#F6F0E4` papier crème | le « blanc » est toujours du papier réservé (texte réservé dans le bleu, étoiles, fissures de glace) |
| Accent 1 — rose fluo | `#FF48B0` | passe décalée sous les titres, ombres de collage (37 %), coches, bâtons de comptage, lueur d'horizon |
| Accent 2 — bleu | `#0078BF` | titres (passe du dessus), annotations au marqueur, ciel, glace, Terre |
| Accent 3 — jaune | `#FFE800` | fonds d'étiquettes, soleils, déserts chauds, texte « réservé » dans le bleu (« ? », « GLACÉ ! »), têtes d'étoiles filantes |
| Texte | `#1A1A1A` | noms, chiffres d'étiquettes, CTA (tambour noir) |
| Succès / danger | rose `#FF48B0` | coche ✔ tracée au marqueur rose ; pas de rouge d'alerte |
Superpositions (multiply) voulues : rose×jaune = rouge-orangé (dunes), rose×bleu = violet (passes de titre). À éviter : jaune×bleu = vert (réserver le bleu sous le jaune).
Trames : jaune 0° pas 9 px, rose 45° pas 8 px, bleu 15° pas 7 px.

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Space Mono 700** (`space-mono`) : géant 340 px / −14 px (J-39, 120), numéro 236 px / −10 px (N°5), titres 96–112 px / −4 px en MAJUSCULES, imprimés en **deux passes** (rose dessous, bleu dessus) décalées du défaut de repérage ; étiquettes 48–74 px sur tag jaune ; noms 112 px en encre noire.
- **Permanent Marker 400** (`permanent-marker`) : annotations 54–86 px, bleu (ou noir), tournées de −3 à −9°, qui s'écrivent de gauche à droite. Les chiffres dans une annotation passent en Space Mono (le « 1 » du marqueur se lit « 7 »).
- Glyphes hors sous-ensemble latin à éviter : ≈, →, ✓ (on dessine la coche, on écrit « soit », « 13–14 »).

## Formes & matières
Formes **découpées aux ciseaux** : blobs à contour bruité (`R.blobPts`, dentelure fine + lobes), rectangles « déchirés » (ciel), toujours avec une **ombre de collage** décalée (+16/+18 px) dans une autre encre à 37 %, et la découpe masque ce qui est dessous. Matières : trame de points ronds (taille ∝ √couverture, ±14 % par point), texte et étoiles **réservés** (papier) dans l'encre, contour pointillé au crayon bleu pour une forme « fantôme » (le n°1 attendu), bâtons de comptage. Post OpenCV : manques d'encre, densité de rouleau inégale, grain + fibres du papier, bavure 0,7 px, feuille qui ondule.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- **Tout est quantifié à 12 pas/s** (`t' = floor(t·12)/12` avant `tl.seek`) : animation on twos.
- Entrée de titre : *slam* x −150 px, rotation −8° → 0, `power3.out`, 0,3 s. Étiquette : scaleX 0→1 depuis la gauche, `power2.out`, 0,25 s.
- Découpe qui tombe : échelle 0,55→1, rotation −20°→0, +160 px → 0, `back.out(1.7)`, 0,42 s. Tampon (GLACÉ !, note-le !) : échelle 2,2→1, `back.out(2.2)`, 0,3 s.
- Marqueur : révélation clip-path gauche→droite, 0,4–0,6 s, linéaire (par pas). Stagger de collage : 0,13 s.
- Défaut de repérage : tiré à chaque pas (±4 px), **kick** à ±14 px pendant 0,34 s après chaque coupe.
- Jamais : fondu enchaîné doux, flou de mouvement, interpolation à 30 fps lisse, dégradé lisse non tramé, ombre portée floue, alignement parfait des encres.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
2D plat, pas de caméra ni de profondeur de champ. Le « mouvement de caméra » est celui de la **feuille** : micro-rotation (σ 0,18°) + translation (σ 2,2 px) + zoom 1,012, changés à chaque pas (post.py). Recadrages brusques = coupes de page. Les compositions sont frontales : grand chiffre en haut à gauche, forme au centre-bas.

## Transitions (liste nommée, durée, quand les utiliser)
- **coupe-de-page** (0 s) : entre chaque beat ; masquée par le kick de repérage + slam du titre. Transition par défaut.
- **slam-découpe** (0,42 s) : entrée de la forme principale d'une page.
- **trait-marqueur** (0,45 s ; `wiperight` si on assemble des clips avec ffmpeg) : annotation qui s'écrit.
Pas de `xfade` fondu : un zine se tourne, il ne se fond pas.

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
- **0–2,5 s hook** : page de couverture déjà imprimée à la frame 0 — tag « ZINE GÉO #13 » / « AGENDA DU CIEL », titre ou chiffre géant en deux passes, une annotation-question au marqueur, une grande découpe qui bouge.
- **Développement** : 3–5 pages de 1,6–3 s, une idée par page (chiffre + forme + annotation), coupe sèche + kick.
- **Chute** (~3 s) : la page du chiffre-surprise (tampon GLACÉ !, compteur 120, coches).
- **Fin (2–3 s)** : planche-récap (collage de toutes les découpes) ou retour à la couverture (boucle J-39) + CTA au marqueur.

## Zones sûres
Haut 220 px, bas 320 px, droite 120 px (contenu entre y = 230 et y = 1600, x ≤ 960). Seules les découpes décoratives (ciel, ville) peuvent mordre la marge droite. Texte ≥ 54 px partout, titres ≥ 96 px.

## Librairies recommandées et pourquoi
- **p5.js v2** (instance, sans preload) : une `p5.Graphics` en niveaux de gris par encre, primitives simples (beginShape, circle, text réservé) ; le tramage se fait en un seul `ctx.arc` path par encre en multiply (≈ 100 k points/frame, négligeable devant la capture). Piège : `ctx.save/restore` manuel désynchronise le cache de style p5 → `R.resync(g)`.
- **GSAP 3** : timeline pausée, `tl.seek(t', false)` sur temps quantifié ; anime le DOM (titres en deux passes, tags) et des objets d'état lus par p5.
- **OpenCV (Python cv2)** : passe d'impression frame par frame via pipes ffmpeg (sous `slot.sh`) : feuille qui ondule, manques d'encre, grain, fibres.
- À éviter : WebGL/3D (contraire au plat imprimé), filtres SVG plein cadre (coûteux).

## Familles de contenus adaptées / inadaptées
Adaptées : **geographie** (superficies, comparaisons « soit 25 × la France », formes découpées), **evenements** (agenda, J-xx, conseils pratiques), engagement (questions au marqueur), enfants (collage ludique). Inadaptées : histoire grave/solennelle, explicatif qui exige précision géométrique ou 3D, abstrait fluide (le on-twos casse la fluidité).

## Shorts de preuve (chemins)
- `out/shorts/riso-zine__geographie__5-plus-grands-deserts/` — Les 5 plus grands déserts du monde (le n°1 est glacé !)
- `out/shorts/riso-zine__evenements__geminides-j-39/` — J-39 : les Géminides, la pluie d'étoiles filantes du 13–14 décembre

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)
Voix **Puck** (Gemini TTS), décontractée, complice ; ≈ 2,6 mots/s, une phrase courte par page, posée sur la coupe (0,1 s après). L'écran ne porte que chiffres, noms et mots-clés ; la voix dit le lien (« vingt-cinq fois la France », « ce sont les poussières de Phaéton »). Silence de la voix pendant les tampons (GLACÉ !) pour laisser le SFX verre/chime frapper.

## Risques et limites
- Lisibilité : rose seul sur papier < 3:1 → jamais de texte rose seul ; texte informatif en noir ou bleu, titres en deux passes.
- Jaune sur bleu donne du vert si on ne réserve pas le bleu : toujours réserver.
- Le on-twos + le grain font monter le débit (≈ 8 Mb/s) et fatiguent sur > 20 s.
- Sous-ensemble latin des polices : pas de ≈ → ✓.
- Coût : ~30 s/100 frames (p5 + capture) + ~34 s/100 frames OpenCV sous contention.
