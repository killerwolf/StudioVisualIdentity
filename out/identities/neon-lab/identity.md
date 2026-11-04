# Labo Néon — identité visuelle (neon-lab)

## Nom
**Labo Néon** (`neon-lab`) — la chaîne « LABO/0X » : chaque short est une expérience numérotée.

## Promesse en une phrase
Une nuit de laboratoire où la science se voit en lumière : un phénomène réel (attracteur, orbite, rotation) mis en scène comme une visualisation de musée, précise et émerveillée.

## Mood & références de genre
Noir profond troué de lumière, précision d'instrument, calme puis impulsions. Références de genre (pas d'œuvres précises) : générique de série de science-fiction, visualisation scientifique de planétarium/musée, pochette synthwave sobre (sans soleil rétro ni grille rose kitsch). Pas d'humour visuel, pas de rebond : on observe.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Hex | Usage réel dans les shorts |
|---|---|---|
| Fond | `#05060B` | fond de page et base du champ GLSL |
| Surface | `#11142A` | halo central du champ, ombre des sphères |
| Accent 1 — cyan | `#38F9FF` | sujet principal (Terre, orbite, aile gauche), mot-clé du titre, tag |
| Accent 2 — magenta | `#FF3DCB` | contre-exemple (« Sans rotation », face cachée), pastille du tag, aile droite |
| Accent 3 — lime | `#B6FF3B` | donnée/résultat (σ ρ β, « 27,3 j », face visible, « = ») |
| Texte | `#F2F6FF` | titres et corps |
| Atténué | `#9FB7FF` | étoiles, éléments secondaires |
| Succès | `#B6FF3B` (lime) | ce qui est vrai / vérifié |
| Danger | `#FF3DCB` (magenta) | ce qui serait faux / l'hypothèse écartée |
Les lignes de champ du fond mélangent cyan et magenta à ~10 % d'opacité. Jamais de blanc pur en aplat : le blanc n'apparaît que dans le cœur des points lumineux (bloom).

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Display** : Space Grotesk 700, 118 px, interlettrage −0,035 em, interligne 0,96 (titre de l'abstrait).
- **Titre** : Space Grotesk 700, 100 px (112 px pour les titres courts de beat), −0,035 em, interligne 0,98 ; un mot-clé coloré par titre (`<em>` cyan, magenta ou lime).
- **Corps** : Space Grotesk 500, 56 px, −0,01 em, interligne 1,16 ; une ligne, deux maximum ; mot fort en lime 700.
- **Légende / données** : JetBrains Mono 500, 54 px, +0,01 em ; tout ce qui est mesure, tag `LABO/0X · MOT`, compteurs (`JOUR 16,7`), légendes de type musée (`FACE VISIBLE`).
- Aucun texte < 54 px. Les chiffres utilisent la virgule décimale française et l'espace fine des milliers (`2 000`).

## Formes & matières
- Sphères sombres à **grille lat/long néon** et **liseré fresnel** cyan ; halo additif.
- **Points lumineux** (cœur blanc + halo coloré, mélange additif) pour les particules/lucioles.
- Fond = **champ de force** : lignes iso d'un potentiel (bruit fbm + puits radial), même shader GLSL dans les deux shorts (`field.glsl.js`).
- Traits fins : orbite en pointillés, filets de rappel (3 px) entre légende et objet, arcs de progression (9 px, lueur).
- Matière finale : grade OpenCV (glow des hautes lumières, aberration chromatique radiale ≈ 2 px dans les coins, vignette 22 %).

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- **Entrée** : `glide` = translateY 46 px → 0 + opacité, `outExpo`, 0,6 s.
- **Sortie** : `inExpo`, 0,3 s, léger glissement vers le haut.
- **Emphase** : `pulse` = bloom 0,62 → 1,52 puis décroissance exp(−Δt/0,35 s), synchronisé sur la musique (80 bpm ; une impulsion toutes les 1,5 s en abstrait, à chaque changement de beat en explicatif).
- **Rythme** : beats calés sur la noire de 0,75 s (4,5 / 8,25 / 12,75 s) ; stagger titre → corps 0,8 s.
- Durées : fast 0,3 s, base 0,6 s, slow 2,4 s (dolly d'ouverture).
- **Jamais** : rebond (`outBack`, `outElastic`, `outBounce`), secousse de caméra, rotation de texte, texte qui clignote, couleurs hors palette, coupe sèche sans impulsion.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
- Focale verticale **38°** (≈ 35–40 mm équivalent), caméra plongeante 34–38° sur le plan de l'orbite.
- Mouvements : **dolly-in `outExpo` de 2,4 s** au hook, puis **orbite lente de 15°** (inOutSine, ou sinus périodique pour une boucle), poussée finale de −0,9 u.
- Cadrage vertical : le sujet vit dans la bande 580–1340 px, entre le titre (haut) et les données (bas) ; `setViewOffset` / translation de clip pour descendre le sujet.
- Profondeur : pas de DoF optique (coût CPU) ; profondeur par brouillard exponentiel, taille des points selon 1/w, bloom et vignette.

## Transitions (liste nommée, durée, quand les utiliser)
| Nom | Durée | Quand | Équivalent ffmpeg xfade |
|---|---|---|---|
| `pulse-flash` | 0,35 s | à chaque changement de beat, dans la scène (bloom + lignes de champ) | `fadewhite` |
| `glide` | 0,6 s entrée / 0,3 s sortie | titres, données, légendes | `slideup` |
| `loop-seam` | 0 s | boucle parfaite : la couture tombe sur une impulsion | — |

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
- **0–1 s hook** : le phénomène est déjà lumineux à la frame 0 (impulsion) + tag `LABO/0X` + titre question ou chiffre (visible dès 0,1 s).
- **Développement** : 2 à 3 beats de 3,75–4,5 s, chacun avec un titre court (≤ 4 mots), une légende mono et un objet de démonstration (contre-exemple magenta, preuve lime).
- **Chute** : la donnée-clé en mono lime, symétrique (`ROTATION 27,3 j = RÉVOLUTION 27,3 j`), marquée par impulsion + carillon.
- **Fin** : tenue calme 2–3 s avec poussée de caméra (explicatif) ou boucle parfaite (abstrait).

## Zones sûres
Haut 220 px, bas 320 px, droite 120 px (et marge gauche 72 px). Tag à 232 px, titre à 316 px, données à 1340–1480 px, rien d'important sous 1600 px ni au-delà de x = 960 px. Les légendes sont des étiquettes fixes reliées à l'objet par un filet, pour ne jamais déborder quand l'objet bouge.

## Librairies recommandées et pourquoi
- **three.js** (+ UnrealBloom) : scènes 3D à objets (sphères, orbites), bloom natif, `ShaderMaterial` pour réutiliser le champ GLSL. ≈ 60 s / 100 frames.
- **twgl.js** : GLSL brut et nuages de points massifs (20 000 sprites additifs) quand il n'y a pas de maillage ; boucles parfaites faciles (renderAt pur). ≈ 55 s / 100 frames.
- **OpenCV** : grade signature commun à tous les moteurs (glow, aberration chromatique, vignette), ce qui rend l'identité reconnaissable même quand la scène change de moteur. ≈ 32 s / 100 frames.
- **Matplotlib** (Agg) : explicatifs « simulation + mesure » 100 % Python — simulation numpy (RK4), schéma 2D à traînes néon (LineCollection à alpha dégressif) et vrai graphe en direct (axe log) ; la lueur vient du grade OpenCV. Polices @fontsource converties woff -> ttf (fontTools). ≈ 53 s / 100 frames.

## Familles de contenus adaptées / inadaptées
- **Adaptées** : abstrait (systèmes dynamiques, champs, particules), explicatif scientifique (astronomie, physique, maths), engagement de type « devine le paramètre ».
- **Inadaptées** : enfants (trop sombre, trop précis), histoire/géographie à archives (pas de texture papier), événements festifs, tout contenu qui demande des personnages.

## Shorts de preuve (chemins)
- `out/shorts/neon-lab__abstrait__champ-de-force-lucioles/` — 12 s, boucle parfaite, twgl.js + OpenCV.
- `out/shorts/neon-lab__explicatif__lune-meme-face/` — 16 s, three.js + OpenCV (+ champ GLSL partagé).
- `out/shorts/neon-lab__explicatif__effet-papillon-double-pendule/` — 15 s, Matplotlib + OpenCV (champ de force porté en numpy, LABO/03).

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)

> **Voix réellement utilisée pour tous les shorts : Fish Audio « Arnold »** (`d704cf8f1216490cbfbed89955f0e938`, modèle `s2.1-pro`, conteur masculin FR). Les noms de voix Gemini (Orus, Kore, Aoede…) qui suivent sont des suggestions historiques de casting par ton : Gemini a été abandonné (quota). Le placement, le débit et les silences décrits ici restent valables.

- Voix documentaire posée (Gemini **Orus** pour l'explicatif, **Achernar** calme pour l'abstrait), débit ≤ 2,6 mots/s, une phrase par beat, démarrage 0,1–0,3 s après chaque impulsion.
- Le visuel ne porte que titres courts, chiffres et légendes : la voix porte le « pourquoi » (mécanisme, cause) ; les nombres restent à l'écran (la voix peut ne pas les lire).
- Musique déjà mixée à −18 dB ; impulsions/SFX sur les beats, jamais sous une syllabe accentuée.

## Risques et limites
- Fond très sombre : risque de banding et de compression (crf 20 + 8 Mb/s plafonné) ; garder le champ à faible contraste.
- Le bloom + les points additifs saturent vite en blanc : limiter l'alpha des traînes (≤ 0,26).
- Tout est rendu sur CPU (SwiftShader) : ≈ 1 min / 100 frames par moteur WebGL, + 0,3 min OpenCV ; éviter le raymarching plein écran.
- Échelles astronomiques non respectées (choix pédagogique, à dire dans les notes) ; vérifier chaque fait (ex. 27,3 j = période sidérale).
- Identité froide : peu adaptée à l'émotion ou aux personnages.
