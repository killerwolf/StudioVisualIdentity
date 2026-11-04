# Chrome Liquide — identité visuelle

## Nom
**Chrome Liquide** (`liquid-chrome`). Matière brillante, couleurs pastel métallisées, noir profond, une seule prise.

## Promesse en une phrase
Une matière liquide, chromée et hypnotique qu'on regarde couler jusqu'au bout : chaque short est un plan-séquence de satisfaction où la physique fait le spectacle.

## Mood & références de genre
Vidéo « satisfying », publicité de parfum ou de cosmétique de luxe, macro de fluides, ASMR visuel. Calme, lent, précis. Les reflets sont des panneaux néon de studio (lilas en haut, rose à gauche, menthe à droite, or en bas) qui glissent sur des surfaces bombées. Pas d'humour cartoon, pas de collage : du métal et du verre sur du noir.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Valeur | Usage réel |
|---|---|---|
| Fond | `#0B0B10` | noir bleuté, toujours relevé par 2–3 halos radiaux (rose 16 %, menthe 12 %, lilas 10 %) et une « table » `#1A1A24` sous le sujet, pour qu'aucune frame ne soit détectée comme noire |
| Surface | `#1A1A24` | table / socle sous le verre, fonds de pastilles |
| Accent 1 | `#C8D3FF` lilas chrome | légendes, matière n° 1, panneau haut de l'environnement |
| Accent 2 | `#FF9AE8` rose | matière n° 2, panneau gauche |
| Accent 3 | `#7CF7E4` menthe | matière n° 3, couleur de **succès** (vainqueur, pilule CTA) |
| Accent 4 | `#FFE29A` or | matière n° 4, panneau bas |
| Texte | `#FFFFFF` | titres, chiffres ; ombre portée `#0B0B10` 55 % floutée 10 px dans les overlays Python |
| Graphite chaud / perle | `#121016` → `#1A161E`, socle `#4A4250`, clé `#FFE9C8`, perle `#F4EEF8` | variante chaude (short Babylon) : fonds graphite et reflets perle/or plutôt que noir bleuté + néon froid, pour ne pas se confondre avec neon-lab |
| Danger | `#FF9AE8` | réutilise le rose (alerte/erreur) ; non utilisé dans les shorts de preuve |
| Dégradé chrome | `#C8D3FF → #FF9AE8 45 % → #7CF7E4 80 % → #FFE29A` | **un seul mot-clé** par titre |

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Display / titre** : Syne 800, 92 px, interlignage 1.0, interlettrage −0.03em, aligné à gauche en x = 72, y = 306. Syne 800 est très large (≈ 75 px par caractère à 92 px) : **11 caractères max par ligne**, 3 lignes max.
- **Légende** : Inter 500, 54 px, MAJUSCULES, interlettrage 0.2em, `#C8D3FF`, y = 232 ; elle sert de « statut » (COURSE · 4 COULEURS → FAIS TON PARI… → RALENTI · ×0,5) ou de chapeau de question (QUELLE COULEUR).
- **Chiffres** : Syne 800 76 px aux couleurs des matières ; pourcentages Inter 600 54 px, qui flottent juste au-dessus du niveau du liquide.
- **CTA** : Inter 500 60 px, texte `#0B0B10` sur pilule menthe `#7CF7E4`, rayon 999 px.
- Jamais de texte < 54 px ; jamais plus d'un mot en dégradé.

## Formes & matières
- Gouttes chrome déformées par bruit (icosaèdre subdivisé, bruit 3D lent, bas plus lourd) — la signature héritée du poster.
- Liquides : métal coloré irisé (metalness 0.85, roughness 0.14, iridescence 0.45, clearcoat 1) ou, en 2D, peinture visqueuse ombrée par OpenCV (normales d'un champ de hauteur multi-échelle, spéculaire Blinn n=90 + lustre n=14, reflet d'environnement néon, liseré de Fresnel).
- Verre : contenant fin, liseré chrome antialiasé + 2 reflets verticaux doux ; en 3D, MeshPhysicalMaterial noir en blending additif (seuls les reflets néon s'ajoutent), anneau chrome au col.
- Les formes sont rondes, bombées, sans arêtes vives ; pas de contour noir.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- La matière bouge **dès la frame 0** (goutte déjà en chute, filets qui démarrent à 0,45 s).
- Entrées de texte : `outCubic` 0,45 s (fondu + montée de 30 px) ; sorties : fondu linéaire 0,35 s ; emphase (CTA) : `outBack` 0,6 s.
- Stagger des événements matière : 1,55 s entre deux chutes (rythme régulier, hypnotique).
- **Ralenti ×0,5** sur la dernière ligne droite avant la chute (annoncé par la légende « RALENTI · ×0,5 »).
- Simulations continues : viscosité de peinture (μ = 0,05), clapot amorti (e^−1,8t) après l'arrêt.
- Jamais : coupe franche, shake, rebond élastique cartoon, zoom brutal, texte qui clignote, plus de 2 textes simultanés.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
- Focale serrée (three.js fov 30°), cadrage macro sur l'objet ; en 2D (Taichi) plan fixe frontal, le verre occupe y 640–1594.
- Mouvements : dérive latérale sinusoïdale lente (0,25 u, période ≈ 125 s), travelling avant de 0,5 u sur toute la durée (`inOutSine`), et après la chute un glissement de 18 % vers le sujet gagnant (`outCubic` 0,6 s).
- Profondeur de champ forte : BokehPass (focus = distance caméra, aperture 0,0022, maxblur 0,008) ; gouttes chrome floues en arrière-plan sur les côtés, jamais derrière un chiffre.

## Transitions (liste nommée, durée, quand les utiliser)
| Nom | ffmpeg xfade | Durée | Quand |
|---|---|---|---|
| fondu-chrome | `fade` | 0,45 s | entrée/sortie de chaque carton titre (overlays `assemble.py --overlay o.png:A:B:0.45`) |
| glisse-haut | `slideup` | 0,6 s | titre de résultat et CTA qui montent de 30–40 px |
| dissolution-lente | `dissolve` | 0,8 s | uniquement si deux plans doivent s'enchaîner ; les shorts de l'identité restent des plans-séquences |

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
1. **Hook 0–1 s** : la matière est déjà en mouvement à la frame 0, la question/le titre est lisible avant 0,3 s.
2. **Développement** (1–9,6 s) : une suite d'événements matière réguliers (chutes toutes les 1,55 s, ou course avec changements de tête), la légende change de statut.
3. **Chute** (9,6–11,7 s) : ralenti ×0,5 ou tourbillon, puis l'instant décisif (dépassement, mélange) ; chime + impact.
4. **Fin** (11,7–15 s) : un mot en dégradé (« Hypnotique. », « Menthe gagne ! »), CTA éventuel, la matière continue de vivre doucement (clapot amorti) : fin propre, pas de noir.

## Zones sûres
Haut 220 px, bas 320 px, droite 120 px. Légende à y = 232, titre à y = 306, x = 72 ; chiffres au plus bas à y = 1492–1568 ; rien d'important au-delà de x = 960 (l'image three.js est décalée de 30 px à gauche avec `setViewOffset` pour centrer le sujet sur la zone utile, centre 510 px).

## Librairies recommandées et pourquoi
- **Taichi** (MLS-MPM, ti.cpu) : vrais fluides visqueux, chutes et mélanges crédibles ; seule librairie qui donne la « matière » de l'identité en 2D. Coût mesuré dans `out/library-cards/_drafts/liquid-chrome__taichi.json`.
- **OpenCV** : transforme les points Taichi en surface liquide brillante (flou gaussien, Sobel → normales, spéculaire, reflets néon, composition) et dessine le verre antialiasé.
- **three.js** : chrome et verre physiquement plausibles (PMREM procédural, MeshPhysicalMaterial irisé, verre additif, BokehPass) ; scènes sans état faciles à rendre en stills.
- **Babylon.js** : objets PBR chrome irisés en macro avec post-traitement intégré (DefaultRenderingPipeline ACES + DOF, GlowLayer pour les éclats) et environnement procédural capturé une fois par ReflectionProbe ; idéal pour les **boucles parfaites** analytiques (123 s/100 frames mesuré).

## Familles de contenus adaptées / inadaptées
- **Adaptées** : abstrait (satisfying, boucles de matière), engagement (courses, « quelle couleur… », votes par couleur), explicatif court sur la matière (mercure, tension superficielle, viscosité), teasers produit/beauté.
- **Inadaptées** : histoire et géographie (pas de personnages, pas de cartes), enfants très jeunes (ambiance nocturne et lente), données denses (le chrome brouille la lecture de petits chiffres).

## Shorts de preuve (chemins)
- `out/shorts/liquid-chrome__abstrait__quatre-peintures-mpm/` — Taichi MPM + OpenCV, 14 s.
- `out/shorts/liquid-chrome__engagement__quelle-couleur-remplit-le-verre/` — three.js, 15 s.
- `out/shorts/liquid-chrome__abstrait__pendule-de-newton-chrome/` — Babylon.js, 12 s, boucle parfaite (pendule de Newton, T = 2,4 s × 5).

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)

> **Voix réellement utilisée pour tous les shorts : Fish Audio « Arnold »** (`d704cf8f1216490cbfbed89955f0e938`, modèle `s2.1-pro`, conteur masculin FR). Les noms de voix Gemini (Orus, Kore, Aoede…) qui suivent sont des suggestions historiques de casting par ton : Gemini a été abandonné (quota). Le placement, le débit et les silences décrits ici restent valables.

Voix Gemini **Achernar** (calme), débit 2,3–2,6 mots/s, phrases de 2 à 6 mots posées **entre** les impacts sonores (les chutes et la victoire restent « à nu »). Le visuel ne porte que 1 titre + 1 légende à la fois et laisse la moitié basse de l'écran à la matière : la voix raconte ce qu'on ressent (« Chacune tombe de tout son poids »), l'écran ne la double pas mot à mot. La musique (pad / pulse) est duckée sous la voix par `assemble.py --voice`.

## Risques et limites
- **Coût mesuré** : Taichi MPM + ombrage OpenCV = 443,7 s pour 14 s (105,6 s/100 frames, 24 k particules, 1 thread) ; three.js = 800,9 s pour 15 s (178 s/100 frames, CPU saturé). Ne pas dépasser ~25 k particules ni 15 s sans budget.
- **Proximité avec neon-lab** : un test d'histogramme de couleurs a confondu les deux identités (quasi-noir + accents néon). Ce qui distingue Chrome Liquide : la matière chrome/perle (reflets larges, pas de traits lumineux), les pastels irisés, Syne 800, et les fonds graphite chauds (#121016–#1A161E, halos perle/or) à privilégier.
- **Fond très sombre** : `#0B0B10` seul est détecté noir par `blackdetect` ; toujours garder des halos et une matière visible ≥ 2 % de l'image.
- **Syne 800 très large** : 11 caractères/ligne à 92 px, les titres doivent être courts (sinon légende + titre).
- **Mélange MPM** : les couleurs ne se mélangent pas seules (particules) — on diffuse la couleur via la grille, à doser (trop fort = gris lavande terne).
- **Transmission three.js** sous SwiftShader : ~5 s/frame mesuré, rendu abandonné -> verre additif (reflets seuls, pas de réfraction). Les gouttes de fond doivent rester sur les côtés pour ne pas masquer les chiffres.
- **Artefacts MPM** : petites bulles d'air et bord supérieur légèrement granuleux (seuil de densité) ; lus comme des bulles de peinture, mais visibles en plein écran.
