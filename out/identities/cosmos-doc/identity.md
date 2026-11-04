# Cosmos Doc — design system

## Nom
**Cosmos Doc** (`cosmos-doc`) — documentaire spatial cinématographique, « ouverture de film » en 9:16.

## Promesse en une phrase
Chaque short est un plan de cinéma sur un vrai objet du ciel — lumière d'étoile chaude, noir absolu, travelling lent — où un seul chiffre en capitales Bebas Neue suffit à donner le vertige.

## Mood & références de genre
Silence, gravité, échelle vertigineuse. Genre : documentaire astronomique télé/cinéma, ouverture de film spatial, photographie astronomique à longue pose. Tout doit **sembler photographié** : matières procédurales (cratères, nuages en bandes, feuille d'or), lumière d'un seul soleil, flare d'objectif, grain de pellicule, vignette. **Ce n'est pas** une interface : aucune grille, aucun HUD, aucune ligne néon, aucun cadre (c'est la frontière nette avec `neon-lab`, qui est HUD + Space Grotesk + cyan/magenta/lime).

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Couleur | Usage réel |
|---|---|---|
| fond | `#000004` | noir vrai, `scene.background` three.js ; jamais de dégradé de fond |
| surface | `#000006` | pas de cartouche ni de panneau : seul support du texte = halo d'ombre `text-shadow 0 0 30px rgba(0,0,6,.9), 0 0 8px rgba(0,0,6,.8)` |
| accent 1 — ambre | `#FFB347` | lumière d'étoile : tag d'épisode, mot-clé du titre, chiffre-choc final, filet 150×3 px, halo du flare, étoiles chaudes (20 %) |
| accent 2 — glacier | `#6EC6FF` | froid / repère : étiquettes, traînée anamorphique du flare, contre-jour, signal radio, « –180 °C » |
| accent 3 — braise | `#FF6A2A` | chaleur extrême uniquement : photons infrarouges, surface embrasée |
| texte | `#EAF2FF` | titres Bebas Neue |
| texte secondaire | `#AEBBD4` | ligne de contexte Inter |
| succès / danger | `#6EC6FF` / `#FF6A2A` | froid-apaisé / brûlant ; pas de vert ni de rouge « interface » |
Règle : l'ambre et le glacier se répondent (chaud = lumière, froid = ombre/mesure) ; la braise n'apparaît que pour la chaleur.

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Bebas Neue 400** (`@fontsource/bebas-neue`), capitales :
  - chiffre-choc / nom de sonde : **230–300 px**, line-height 0,86, interlettrage final 0,01 em ;
  - titres : **104–156 px** (titre du hook 118 px sur 3 lignes, 230 px pour un nom court), line-height 0,94 ;
  - tag d'épisode : **54 px**, interlettrage **0,3 em** (départ 0,7 em), ambre ;
  - étiquettes : **60 px**, interlettrage **0,22 em**, glacier ou ambre (« JOUR », « DISTANCE », « VERS FIN 2026 »).
- **Inter 400** (`@fontsource/inter`) : **56 px**, line-height 1,2, `#AEBBD4`, **une** ligne de contexte (« 58 millions de km du Soleil »).
- Indices chimiques en `<sub>` (CO₂) : Bebas n'a pas les glyphes ₂. Signe moins : tiret demi-cadratin « – » (le U+2212 n'est pas dans le sous-ensemble latin).
- Largeur utile 888 px (marge gauche 72) : Bebas ≈ 0,4 em/caractère -> à 104 px, 20 caractères par ligne max ; `white-space:nowrap` obligatoire (le tracking de départ élargit la ligne).

## Formes & matières
- **Corps célestes procéduraux** (canvas -> `CanvasTexture`, déterministes) : roche cratérisée avec relief (bumpMap), nuages en bandes torsadées par fbm, carte émissive « surface brûlante » à crêtes. Sphères 128×96.
- **Atmosphères** : coquilles fresnel additives éclairées côté soleil (`atmosphere()` de `cosmos.js`) ; la même coquille, immense (rayon 60), dessine le bord ambré de l'héliosphère.
- **Engins** : géométrie simple en primitives (parabole en LatheGeometry, bus décagonal en feuille d'or, mâts filiformes) — silhouette générique, éclairée par un seul soleil + contre-jour glacier.
- **Lumière** : étoiles = disques doux gaussiens (pas de croix), photons = points doux avec traîne de 9 échos (flou de bougé, pas de trait), flare = halo + cœur + traînée anamorphique glacier + 5 fantômes hexagonaux flous.
- **Pellicule** : grain 2 px (0,028), vignette 0,38, bloom 0,62/0,7/0,78, tone mapping ACES.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- **Un seul easing : `sine.inOut`** (GSAP) / `inOutSine` (svi.js) — textes, caméra, rampes.
- Texte entrant : **fondu + interlettrage qui se resserre** (0,22 em -> 0,01 em), 0,9 s au hook, 1,0–1,4 s ailleurs ; ligne Inter : 0,08 em -> 0 em.
- Texte sortant : fondu 0,5–0,7 s, 0,4 s avant le dip-to-black.
- Stagger entre éléments d'un même plan : 0,3–0,5 s (titre -> sous-titre -> filet).
- Emphase : rampe lente de 3 s (émissif, couleur d'atmosphère, intensité du bloom) — pas d'impulsion.
- Rotations planétaires : 0,025–0,03 rad/s. Compteurs (heures) : tween GSAP linéaire d'un proxy, affiché par `Math.floor`.
- **Jamais** : back/elastic/bounce, translation de texte, rebond, flash blanc, glitch, coupe sèche, lignes néon, grilles.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
- **FOV 36° vertical ≈ 50 mm** plein format ; PerspectiveCamera unique.
- Cadrages : sujet centré horizontalement, centre vertical 620–835 px ; soit titre dessous (1110–1560 px), soit en-tête au-dessus (240–470 px) + bloc chiffré dessous ; le soleil (flare) est **hors centre**, en haut à gauche ou sur le bord gauche, et sa traînée anamorphique traverse le cadre.
- Mouvements : dolly-in de 0,7–1,3 u par plan, recul de 5 u pour révéler l'échelle, dérive latérale ±0,3–0,6 u, sujet qui s'éloigne de 2,6 u en dernier plan — toujours `inOutSine` sur toute la durée du plan.
- Pas de DoF optique (coûteuse sous SwiftShader) : la profondeur vient du bloom, de la vignette, de la parallaxe étoiles/sujet et du voile de poussière galactique (opacité 0,08–0,1).

## Transitions (liste nommée, durée, quand les utiliser)
| Nom | Durée | ffmpeg xfade | Quand |
|---|---|---|---|
| **dip-to-black** | 0,6 s | `fadeblack` | entre chaque plan ; descente 45 %, plancher 6 % pendant ~0,06 s, remontée 45 % — jamais ≥ 0,25 s de noir (blackdetect de `check.py`) |
| **fade-tracking** | 0,9–1,4 s | `fade` | entrée de tout texte |
| **fade-out** | 0,5–0,7 s | `fade` | sortie des textes avant un dip |
Implémentation : uniforme `dip` de la passe film (`dipAt(t, [[a,b],…])` dans `cosmos.js`), aucun assemblage ffmpeg nécessaire.

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
15 s, 3–4 plans de 3,85–4,45 s séparés par des dip-to-black :
1. **Hook 0–4,45 s** : le sujet est à l'image dès la frame 0 avec le flare ; tag ambre + titre-question Bebas entrent à 0,0–0,05 s (lisibles vers 0,6 s), filet ambre à 0,7–0,9 s.
2. **Développement 4,45–8,3 s / 8,3–12,75 s** : un plan = un fait, en-tête (nom/date) + bloc chiffré ; une seule idée visuelle par plan (photons qui s'échappent, recul sur l'héliosphère, signal qui voyage).
3. **Chute 11,5–13,5 s** : le chiffre-choc en Bebas 250–300 ambre, entrée lente + rampe visuelle (surface qui s'embrase, sonde qui s'éloigne).
4. **Fin 13,5–15 s** : tenue sur l'image avec dolly continu (pas de figé), ligne Inter de conclusion ; pas de boucle (fin propre de documentaire).

## Zones sûres
Haut 220 px, bas 320 px, droite 120 px, gauche 72 px. Tag et en-têtes à 236–244 px, bloc bas au plus bas à 1 560 px, largeur de texte 888 px. Le flare et la traînée anamorphique peuvent déborder dans les zones (décor), jamais un texte.

## Librairies recommandées et pourquoi
- **three.js 0.187** : scène 3D, matériaux standard + textures procédurales, `ShaderMaterial` pour étoiles/atmosphères/photons, `EffectComposer` (RenderPass scène + RenderPass flare ortho + UnrealBloom + OutputPass + passe film maison). Tout est dans `cosmos.js`.
- **GSAP 3.15** : timeline unique en pause, `tl.seek(t,false)` dans `renderAt` ; fondu + interlettrage, filet, compteur d'heures (tween d'un objet proxy). États de départ posés en CSS (`opacity:0`).
- À éviter ici : A-Frame (aucun besoin d'ECS), Babylon (doublon), toute librairie 2D « graphique » (casserait l'illusion photographique).

## Familles de contenus adaptées / inadaptées
- **Adaptées** : `explicatif` (astronomie, physique planétaire, ordres de grandeur), `evenements` (missions, éclipses, anniversaires de lancement, records de distance), `histoire` de l'exploration spatiale.
- **Possibles avec effort** : `geographie` vue d'orbite.
- **Inadaptées** : `enfants` (trop lent et sombre), `engagement` (pas de mécanique de jeu, rythme contemplatif), `abstrait` (l'identité exige un vrai sujet), tout sujet terrestre sans lien avec le ciel.

## Shorts de preuve (chemins)
- `out/shorts/cosmos-doc__explicatif__pourquoi-venus-plus-chaude-que-mercure/` — Vénus vs Mercure, photons piégés vs échappés, 15 s.
- `out/shorts/cosmos-doc__evenements__voyager-1-a-un-jour-lumiere/` — Voyager 1, héliosphère, signal de 24 h, 15 s.
Module commun identique : `src/cosmos.js` dans les deux dossiers.

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)
Voix grave documentaire (Gemini **Orus** pour l'explicatif, **Charon** pour l'événement), **une phrase par plan**, démarrant 0,1–0,3 s après la sortie du dip, débit ≈ 2,6 mots/s **au plus** (style « lente, silences entre les phrases »). Le visuel ne porte que des noms, dates et chiffres : la voix porte le **pourquoi** (« sans atmosphère, il brûle le jour et gèle la nuit »). La dernière seconde reste silencieuse sous la musique (drone). Musique : preset `drone` 64 bpm mineur, mixée à −18 dB, SFX graves (impact, thud, swell, riser) calés sur les plans.

## Risques et limites
- **Coût de rendu** (mesuré, load 20–23) : explicatif 838,7 s / 450 frames (186,4 s/100 f), événement 787,1 s / 450 frames (174,9 s/100 f) ; GSAP seul 13,9 ms/100 frames (`src/bench_gsap.html`). Ne pas ajouter de DoF ni de transmission.
- **Noir vrai** vs `check.py` : un plan presque vide (sonde minuscule) + dip trop long déclenche blackdetect (pix_th 0,06, 98 %) — garder un sujet ou un texte assez grand à l'image et des dips à plancher 6 % de ~0,06 s.
- **Grain** : il fait monter le débit (plafond 8 Mb/s) ; rester à 0,028 et 2 px.
- **Flare** : un halo trop grand délave les planètes (vu en stills : 1 500 px -> 1 050 px) ; l'anneau doit rester à 16 % sinon il dessine un second contour.
- **Précision** : schémas volontairement exagérés (épaisseur d'atmosphère, Terre écartée du Soleil vue de 170 UA) — dire « schéma » en voix off si besoin ; dates futures toujours prudentes (« vers fin 2026 »).
- **Lisibilité** : sur fond noir, ambre et glacier passent AA ; ne jamais poser de texte glacier sur le halo ambre du flare.
