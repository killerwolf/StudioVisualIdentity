# Arcade Pixel — identité visuelle

## Nom
**Arcade Pixel** (`pixel-arcade`). Une borne d'arcade 8-bit inventée : chaque short est une partie, avec un HUD, un compte à rebours ou un score, et une carte de fin de partie.

## Promesse en une phrase
Une vraie simulation physique, déterministe, filmée comme une partie d'arcade : on parie, on suit, on voit le score tomber.

## Mood & références de genre
Salle d'arcade, défi, compétition, score, nostalgie 8-bit **inventée** (aucun jeu, personnage ou logo existant). Genres : course de billes, tournoi, jeu d'adresse, « satisfying physics ». Ton : enjoué et nerveux pour l'engagement, hypnotique et tendu pour l'abstrait. Le pixel est assumé : basse résolution 270×480 agrandie ×4 en plus-proche-voisin, scanlines légères, étoiles fixes, grille de fond.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Couleur | Usage réel |
|---|---|---|
| Fond | `#0E0B1F` | nuit violette, fond de toutes les frames |
| Surface | `#1D1740` | panneaux (titre, bannière, cadre du terrain) |
| Accent 1 — rose | `#FF4F79` | bille ROSE, ombre portée des titres, hélices ; = **danger** |
| Accent 2 — vert | `#3CF2A0` | bille VERTE, mot-clé du titre, CTA clignotant, « ÉVADÉE » ; = **succès** |
| Accent 3 — jaune | `#FFD23F` | bille JAUNE, labels HUD (TIME / REBONDS), chiffres du compte à rebours, case n°1 |
| Accent 4 — bleu | `#4FB3FF` | bille BLEUE, rampes, bordures des panneaux, anneau au repos |
| Texte | `#FFFFFF` | tout texte courant, reflets des sprites |
| Muted | `#8A7FD6` / grille `#16123A` / étoiles `#2A2358` | décor, jamais porteur d'information |
Les 4 accents sont aussi les **4 « joueurs »** : toute mécanique à 4 entités leur attribue une couleur fixe (ROSE, VERTE, JAUNE, BLEUE). Contraste texte blanc / fond : 18,6:1 ; jaune / surface : 11,4:1 (AA largement).

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Rubik Mono One 400** (`rubik-mono-one`) — titres et résultats. Titre court 104 px, titre long 80 px (≤ 12 caractères par ligne), résultat de fin 120 px, compte à rebours 240 px. Interlettrage −0,02 em, interligne 1,05–1,1. Ombre portée dure 8 px rose (titres) ou 10–12 px noir/rose (fin, compte à rebours). Toujours en capitales.
- **Press Start 2P 400** (`press-start-2p`) — HUD, consignes, classement, CTA. **56 px partout** (jamais moins : la règle des 54 px prime sur le 32 px « authentique » du poster Phase 1), interligne 64–84 px, interlettrage 0. ≤ 15 caractères par ligne dans 888 px.
- Le texte est en DOM (net) au-dessus du canvas pixel ; les nombres changent par paliers (chronomètre au centième, compteur à 2 chiffres).

## Formes & matières
Pixels carrés de 4 px écran (1 px logique). Sprites dessinés à la main en rectangles : billes 12×14 avec contour nuit et reflet blanc 2 pixels, picots 4×4 avec reflet, rampes en « escalier » de pixels avec liseré clair, anneau de 72 tuiles (5°) à 3 niveaux de lumière. Panneaux = aplats `surface` + bordure 8 px d'accent + ombre portée dure 16 px noire (aucun flou, aucun dégradé, aucun arrondi). Étincelles 2×2 balistiques, ondes d'impact en anneau de 16 pixels, traînées et fantômes à alpha décroissant. Scanlines 2 px à 20 % sur toute l'image.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- Le **mouvement physique** est continu (Matter.js 120 Hz, ou intégrateur maison 240 Hz) mais **affiché quantifié** au pixel logique (pas de 4 px).
- Le **mouvement graphique** est en paliers : `steps(6)` pour entrer/sortir (sortie du titre : 0,4 s en 6 paliers), `pop-scale` 1,4 → 1,2 → 1,0 en 3 paliers de 2 frames (compte à rebours), clignotement **4 Hz** pour tout ce qui appelle l'œil (flèches, CTA, marqueurs de brèche), **12 Hz pendant 0,3 s** pour l'entrée d'une bannière.
- Durées : fast 0,07 s (un palier), base 0,4 s, slow 0,6 s (pixel-mosaic). Stagger 0,12 s entre lignes du classement.
- Screenshake : 4 px / 2 frames (rebond), 8 px / 4 frames (choc entre billes, départ, arrivée), 12 px / 6 frames (évasion), toujours alterné gauche/droite par pas de 4 px.
- Rythme global 125 bpm (temps = 0,48 s) : le compte à rebours 3-2-1-GO tombe sur les temps (0,96 / 1,44 / 1,92 / 2,40 s).
- **Jamais** : easing doux (ease-in-out, ressort), flou de mouvement, anti-aliasing, rotation libre de texte, zoom continu, fondu enchaîné long.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
2D orthographique **fixe**, plein cadre, toute l'aire de jeu visible (on doit pouvoir suivre sa couleur sans coupe). Pas de focale ni de profondeur de champ. Seul « mouvement » : le screenshake quantifié. Si un jour la piste doit être plus haute que l'écran : défilement **par paliers** d'un écran, jamais de travelling doux.

## Transitions (liste nommée, durée, quand les utiliser)
| Nom | Durée | xfade ffmpeg équivalent | Quand |
|---|---|---|---|
| `pixel-mosaic` | 0,6 s | `pixelize` | jeu -> carte de fin. Blocs 1, 2, 4, 8, 16 px logiques puis retour (10 paliers) ; la coupe a lieu au pic (16). Son : whoosh. |
| `step-slide-out` | 0,4 s | `slideleft` | le panneau-titre quitte l'écran vers la gauche au top départ, en 6 paliers. |
| `blink-in` | 0,3 s | `fadefast` | apparition des bannières (PHOTO FINISH, ÉVADÉE) : clignote à 12 Hz puis reste. |
Les shorts sont des plans-séquences (une seule scène simulée) ; les transitions sont rendues **dans la scène**, pas par concat.

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
1. **0–0,1 s — hook** : panneau-titre question (Rubik) + HUD + entités déjà visibles ; « coin » sonore. Engagement : « PARIE SUR TA COULEUR ▶ » ; abstrait : la balle bouge déjà, 1er rebond à 0,48 s.
2. **0,96–2,4 s** (engagement) : compte à rebours 3-2-1-GO sur les temps ; le titre sort en `step-slide-out`.
3. **Développement** (2,4 → ~12 s) : la simulation joue seule ; HUD vivant (chrono ou compteur), feedback de chaque collision (picot allumé, étincelles, blip, onde).
4. **Chute** (~11,8–12 s) : événement fort pré-calculé (arrivée serrée, évasion) + bannière `blink-in` + screenshake.
5. **Fin** : `pixel-mosaic` (0,6 s) -> carte de fin « partie terminée » : résultat 120 px, 3–4 lignes de score en stagger 0,12 s, CTA clignotant 4 Hz. Durées : engagement 16,0 s, abstrait 15,0 s.

## Zones sûres
Haut 220 px, bas 320 px, droite 120 px (gauche 60 px). HUD posé à y = 236 px ; terrain de jeu entre 320 et 1600 px ; aucun texte au-delà de x = 960 px. En logique 270×480 : contenu utile dans x 15–240, y 55–400.

## Librairies recommandées et pourquoi
- **Matter.js 0.20** — courses/billes/pachinko : vraie physique 2D, rapide en Node pur (600 graines simulées en 35 s) pour **choisir** une course, puis rejouée à l'identique dans Chromium (SEQUENTIAL, 4 sous-pas de 8,33 ms par frame). Piège : construire le monde sans `Math.atan2`/`Math.hypot` (diffèrent au dernier bit entre Node et Chromium) ; billes `friction: 0` (sinon collées sur les pentes faibles).
- **p5.js 2.3** — rendu pixel : canvas 270×480 `pixelDensity(1)` + `noSmooth()`, upscale CSS `pixelated`. Suffit seul pour les mécaniques « satisfying » à physique maison (anneau à brèche).

## Familles de contenus adaptées / inadaptées
- **Adaptées** : engagement (paris, votes, « qui gagne ? »), abstrait (satisfying physics, boucles de jeu), enfants (couleurs franches, jeu), événements sportifs fictifs (tournois).
- **Inadaptées** : histoire et géographie (la basse résolution ne porte ni cartes ni archives), explicatif dense (texte 56 px pixel = peu de mots), tout sujet grave (le ton arcade banalise).

## Shorts de preuve (chemins)
- `out/shorts/pixel-arcade__engagement__quelle-bille-gagne-la-course/` — Matter.js + p5.js, 16,0 s.
- `out/shorts/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper/` — p5.js, 15,0 s.

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)
La voix commente la partie comme un speaker d'arcade (engagement : Fenrir, énergique) ou murmure le suspense (abstrait : Achernar, calme). Débit ≤ 2,6 mots/s, phrases de 4 à 9 mots, posées dans les creux sonores : après le GO (2,5 s), au milieu du développement, sur la chute, sur la carte de fin. Le visuel ne porte que des **mots-clés** (titre-question, PARIE, PHOTO FINISH, ÉVADÉE, scores) : la voix ajoute le récit (qui mène, pourquoi c'est serré). La musique chiptune est à −18 dB et sera duckée sous la voix.

## Risques et limites
- La physique est chaotique : toute modification du monde (un picot, un angle) change la course -> re-scanner les graines et régénérer `trace.json` + `sound.json`.
- Déterminisme inter-moteurs fragile (atan2/hypot) : toujours vérifier `?verify=1` (SIM OK) avant un rendu complet.
- Rendu frame à frame obligatoire (SEQUENTIAL) : pas de rendu parallèle par segments ; un still à t = 14 s coûte 14 s de simulation.
- Peu de texte possible (56 px pixel, ≤ 15 caractères/ligne) : l'identité ne convient pas aux explications longues.
- Clignotements 4–12 Hz : rester sous 3 flashs plein écran par seconde (photosensibilité) — on ne flashe que des éléments, jamais l'écran entier.
