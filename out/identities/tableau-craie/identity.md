# Tableau Craie — identité visuelle

## Nom
**Tableau Craie** (`tableau-craie`) — vulgarisation façon tableau noir de classe : tout se dessine à la craie, devant toi, puis s'efface au chiffon.

## Promesse en une phrase
« Un prof bienveillant t'explique le monde en le dessinant à la craie : une idée = un schéma qui s'écrit, puis un coup de chiffon. »

## Mood & références de genre
Salle de classe chaleureuse, carnet de sciences, schémas de prof passionné. Références de genre (pas d'œuvre précise) : vidéos « whiteboard/chalkboard explainer », manuels scolaires annotés, croquis de démonstration. Imperfection assumée : traits tremblés, hachures, poussière de craie, vieilles traces d'effacement. Jamais froid ni « corporate » : c'est de la main, pas de la vectorielle propre.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Hex | Usage |
|---|---|---|
| Fond (ardoise) | `#1F3A30` | vignette radiale `#24443A` → `#16291F`, bruit ±7, 26 traces de chiffon (craie 5 %) |
| Surface | `#264639` | sol/Terre, aplats de fond d'objet |
| Accent 1 — craie blanche | `#FFF6D5` | tracés neutres, lumière, sol, flèches |
| Accent 2 — craie orange | `#FFB84C` | soleil, chaleur, mots-clés « réponse », graines |
| Accent 3 — craie bleue | `#7FD1FF` | eau, ciel, mot-clé de la question |
| Accent 4 — craie rouge | `#FF7A7A` | contraste, rouge physique, fruits |
| Texte | `#F7F3E3` | titres et légendes neutres |
| Muted | `#A9BFAF` | détails secondaires (cailloux) |
| Succès | `#9BE58A` | vert végétal, « ça marche » |
| Danger | `#FF7A7A` | (partagé avec l'accent rouge) |
Contraste : toutes les craies sur `#1F3A30` dépassent 7:1 (blanc/crème ≈ 11:1, bleu ≈ 8:1, orange ≈ 8:1, rouge ≈ 5,6:1 → AA gros texte et ≥ 54 px).

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Display / titres** : Nunito 800 (`@fontsource/nunito`), 100–108 px pour le hook (2–3 lignes), 92–96 px pour les en-têtes d'étape, 160 px pour un chiffre-choc (« ×5 »). Interlettrage −1.
- **Corps / légendes manuscrites** : Caveat 700 (`@fontsource/caveat`), 72–76 px pour les mots-clés, 60–66 px pour les légendes d'objets (jamais < 60 px, Caveat a un petit œil). Interlettrage 0, légère rotation (−6° à +6°) autorisée.
- Tout texte reçoit le **même grain de craie** que les tracés (masque 26 % trous / 12 % demi-teinte + halo 1 px).
- Pas de grec dans les sous-ensembles latin : écrire « 450 nm » plutôt que λ.

## Formes & matières
- Tracés main levée : Rough.js (`roughness 1.5`, `bowing 1.2`, `strokeWidth 5–9`) ou, en Manim, 3 passes (trait 7 px op. 0,88 / trait fin décalé 0,45× op. 0,65 / halo 1,7× op. 0,10) déformées par un tremblé sinusoïdal lisse (amplitude 1,7–3,6 px).
- Remplissages en **hachures** (gap 8–14 px, angle 45° ou −41°) — jamais d'aplat lisse, sauf petits points (yeux, fruits).
- Grain de craie déterministe (graine 77) appliqué en écran (pas en monde) sur tout le dessin et le texte.
- Ardoise avec rebord en bois et 3 bâtons de craie (blanc/orange/bleu) dans la zone basse décorative — signature visible dans toutes les frames.
- Personnages : bonhomme bâton, graine avec deux yeux et un sourire — inventés, simples.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- **Écriture** (« tout se dessine ») : `Create` Manim / `stroke-dashoffset` GSAP, `power1.inOut` (≈ inOutSine), 0,4–1,2 s par objet, stagger 0,12 s entre traits (0,18–0,25 s entre ondes/racines).
- **Craie qui se pose** (texte) : fondu 0,25 s + glissement 14 px, `power3.out` (outCubic).
- **Emphase** : pop `back.out(2–3)` (outBack) 0,3–0,45 s pour feuilles, fruits, barre « ×5 » ; rebond `bounce.out` pour ce qui tombe.
- Durées tokens : fast 0,35 s / base 0,8 s / slow 1,6 s ; hook lisible avant 0,8 s.
- **Jamais** : flash, glitch, shake, rotation 3D, néon, tracé qui « boil » (la craie ne tremble pas une fois posée), texte qui défile, plus de 2 mots-clés neufs à la fois.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
- 2D frontale fixe, orthographique : on regarde le tableau.
- Un seul mouvement : **zoom lent** 1,0 → 1,07–1,12 sur le détail expliqué (molécule, racines), `inOutSine` 2–3 s, retour à 1,0 pendant le chiffon ; dézoom final léger (0,96–0,97) pour la vue d'ensemble.
- Les titres/légendes sont en « HUD » (ne zooment pas), le grain reste en espace écran.
- Pas de profondeur de champ (tout est net).

## Transitions (liste nommée, durée, quand les utiliser)
| Nom | Durée | xfade ffmpeg équivalent | Quand |
|---|---|---|---|
| **chiffon** | 0,4–0,6 s | `smoothleft` | entre deux idées : un chiffon (bande crème 3–6 % d'opacité) balaie gauche → droite, chaque tracé s'efface quand il passe sur son centre, 3 traces d'effacement restent (2,5 %) |
| **craie-qui-se-pose** | 0,25 s | `fade` | apparition/disparition des mots-clés et en-têtes |
En enfants, le dessin **s'accumule** (graine → arbre) ; le chiffon n'efface que l'étape « échafaudage » avant la transformation finale.

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
1. **Hook 0–1 s** : la question en Nunito 100–108 px est déjà là à t=0 + un premier objet se dessine (soleil, graine qui tombe) avant 0,8 s.
2. **Développement** : 3–4 étapes de 2–4 s ; chaque étape = 1 en-tête (ou rien) + 1 schéma qui s'écrit + 1–2 mots-clés Caveat. Chiffon entre idées.
3. **Chute** (≈ dernières 3–4 s) : le schéma « réponse » (coucher de soleil teinté / arbre qui pousse) + un chiffre ou une phrase-clé.
4. **Fin** : tenue 0,8–1,2 s sur la dernière image (fin propre) ; en enfants, « et ça recommence » = boucle narrative.

## Zones sûres
Haut 220 px, bas 320 px, droite 120 px (+ gauche 60 px). Les en-têtes commencent à y ≈ 250–262 ; aucun texte sous y = 1600 ; textes centrés sur x = 510 (milieu de la zone 60–960). Le rebord bois (y 1752–1840) est purement décoratif et vit dans la zone basse.

## Librairies recommandées et pourquoi
- **Manim** (CE 0.22, Cairo) : schémas scientifiques précis (ondes paramétriques, barres proportionnelles, géométrie Terre/atmosphère), `Create` natif, caméra `MovingCameraScene`. Texte via overlays PNG (pas de Pango/LaTeX ici).
- **Rough.js** (`rough.svg`) : le trait main levée et les hachures « gratuits », chemins SVG mesurables (`getTotalLength`) donc animables à l'écriture.
- **GSAP 3** : timeline unique en pause, `seek(t)` par frame → déterministe ; easings nommés (`back.out`, `bounce.out`, `power3.out`), `svgOrigin` pour zoomer.
- PIL/numpy : ardoise, grain, overlays Caveat/Nunito et compositing frame par frame.

## Familles de contenus adaptées / inadaptées
- **Adaptées** : explicatif (sciences, « pourquoi… ? »), enfants (cycles de vie, étapes), histoire des sciences, géographie schématique (cartes croquis), engagement « devine la suite du schéma ».
- **Inadaptées** : événements/actualité chaude (le rendu « cours » refroidit l'urgence), abstrait pur (le style appelle un propos), contenu photo-réaliste, data dense (> 3 séries).

## Shorts de preuve (chemins)
- `out/shorts/tableau-craie__explicatif__pourquoi-le-ciel-est-bleu/` — Manim + overlays craie (16,5 s).
- `out/shorts/tableau-craie__enfants__comment-une-graine-devient-un-arbre/` — Rough.js + GSAP (15,5 s).

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)
- Voix « prof bienveillant » (Gemini `Kore`), débit ≈ 2,6 mots/s, une phrase par étape (5–8 mots), démarrage 0,1–0,2 s.
- Le visuel ne porte que la question, les en-têtes d'étape et 1–2 mots-clés : la voix raconte le « comment » (ex. « le rouge traverse l'air, le bleu rebondit partout »).
- Laisser 0,3–0,5 s de silence de voix sur chaque chiffon (le whoosh sonore porte la transition) ; musique boîte à musique (−18 dB) duckée sous la voix.

## Risques et limites
- Lisibilité de Caveat en petit : rester ≥ 60 px et sur fond uni.
- Le grain de craie (trous 26 %) peut « scintiller » en compression si la caméra zoome fort : garder les zooms ≤ 12 %.
- Manim sans Text/MathTex : toute formule passe par overlays PNG (pas de λ dans le sous-ensemble latin des polices).
- Rough.js régénère le tracé à chaque appel : toujours fixer `seed`, et ne pas re-générer par frame (pas de « boil »).
- Le chiffon (bande claire) peut être lu comme un rayon de lumière s'il passe sur un schéma de soleil : le garder rapide (≤ 0,6 s).
- Coût CPU modéré mais le compositing d'overlays par ffmpeg (`-loop` × 18) est très lent sous contention → compositing numpy.
