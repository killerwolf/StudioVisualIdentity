# Grille Suisse (swiss-data)

## Nom
**Grille Suisse** — slug `swiss-data`. Infographie de presse en mouvement, héritée de l'affiche typographique suisse.

## Promesse en une phrase
Un chiffre qui claque par écran, posé sur une grille 12 colonnes visible, révélé par des volets rouges nets : on comprend une donnée en 4 secondes.

## Mood & références de genre
Rigueur, clarté, autorité journalistique, sang-froid. Genre : infographie de quotidien, affiche du Style typographique international (grille apparente, asymétrie, fer à gauche, gros corps), datavis éditoriale. Aucune illustration figurative : seules les formes géométriques (carrés, barres, disques) portent le sens.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Valeur | Usage |
|---|---|---|
| fond | `#F4F1EA` | papier crème, toujours plein cadre |
| surface | `#FFFFFF` | réservé (cartouches éventuels) — non utilisé dans les 2 shorts |
| accent 1 | `#E3241B` rouge | LE chiffre clé, la valeur n° 1, le volet de transition, le disque-Soleil |
| accent 2 | `#111111` encre | texte, filets, barres secondaires, disque-Lune |
| accent 3 | `#1B4DE3` bleu | deuxième série (Afrique) — un seul usage par short maximum |
| texte | `#111111` | contraste 17:1 sur le fond |
| muted / ghost / rail | `#6B665C` / `#B9B3A6` / `#E7E2D7` | séries tertiaires, éléments « pas encore actifs », rails de barres |
| danger / succès | `#E3241B` / `#1B4DE3` | même rouge / même bleu (pas de vert : la palette reste à 3 encres) |
Filets de grille : `#E2DDD2`, 1,5 px. Règle : au plus **une** couleur forte en plus du rouge à l'écran.

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Display** : `archivo-black` 400 — chiffres géants 200–780 px (typiquement 360–460 px), interlettrage −0,06 em ; unités (`%`, `min`, `s`) à ~30 % du corps du chiffre.
- **Titre** : `inter` 800, 92–122 px, −0,045 em, interligne ≈ 1,05, fer à gauche à x = 66.
- **Corps / labels** : `inter` 600–800, 58–62 px, −0,02 em.
- **Kicker** : `inter` 800 54 px rouge, interlettrage 0, format `01 · RUBRIQUE` ; repère à droite (source ou date) `inter` 600 54 px, aligné à x = 960.
- Minimum absolu : 54 px. Jamais d'italique, jamais de centrage (tout est fer à gauche, sauf valeurs alignées à droite sur x = 960).

## Formes & matières
Grille 12 colonnes (72 → 960 px, 74 px/col) **visible** en filets fins ; filet d'en-tête noir 8 px à y = 232 ; filets de section 4 px. Formes : barres plates (34–48 px) sur rail `#E7E2D7`, carrés unitaires (76 px, gouttière 12,8 px), disques pleins, tracé géographique en trait épais (30 px, extrémités franches). Aucune ombre, aucun dégradé, aucun arrondi, aucune texture : aplats purs.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- **Entrées** : `expo.out` 0,6 s (lignes de titre par masque horizontal, stagger 0,08 s) ; barres `expo.out` 0,8–1,0 s, stagger 0,10–0,12 s ; unités (carrés) 0,4 s, stagger 0,017 s.
- **Compteurs** : `power2.out` (0,9 s), `power3.out` (2,3 s), `expo.out` (1,4 s) — le chiffre roule puis se fige ; un tick sonore par unité franchie.
- **Sorties** : `power2.in` 0,3 s (y −40) ; les scènes ne sortent pas, elles sont **coupées** sous le volet.
- **Emphase** : passage d'une barre de l'encre au rouge (0,3 s), atténuation du reste à 18 % d'opacité, `back.out(3)` pour les points.
- **Volet rouge** : 0,45 s `expo.inOut` pour couvrir, coupe, 0,45 s pour découvrir.
- **Jamais** : rebond élastique sur le texte, rotation, fondu enchaîné, flou, parallaxe, particules, texte qui tremble.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
2D plate orthographique (SVG). Caméra fixe, cadrage dicté par la grille. Un seul mouvement autorisé : **push-in** lent ×1,08 sur la valeur finale (`svgOrigin` au coin bas-gauche du chiffre), 3 s `sine.inOut`. Pas de profondeur de champ : tout est net.

## Transitions (liste nommée, durée, quand les utiliser)
| Nom | Durée | Usage | ffmpeg |
|---|---|---|---|
| `volet-rouge` | 0,95 s (0,45 + 0,05 + 0,45) | entre chaque rubrique 01 → 02 → 03 → 04 ; filet noir 24 px en bord d'attaque | `wipeleft` |
| `coupe-nette` | 0 s | sous le volet, et changement de kicker | cut |
| `wipe-ligne` | 0,6 s | révélation de chaque ligne de texte | `wiperight` |
| `swap-lecture` | 0,3 + 0,5 s | remplacer un chiffre-lecture par le suivant | `slideup` |

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
15 s, rubriques de ~5 s calées sur 120 bpm :
1. **0–0,3 s hook** : chiffre géant déjà à l'écran qui roule (compteur) + titre-question révélé ligne à ligne. Kicker `01 · …`.
2. **3,0 s** volet rouge → `02 · …` : une visualisation D3 (unit chart, barres, timer) qui se construit, puis un chiffre-lecture en bas (baseline y = 1590).
3. **8,0 s** volet rouge → `03 · …` : seconde visualisation (classement, tracé géographique).
4. **11–12,5 s chute** : le chiffre-synthèse (« 1/3 », « 2114 ») en rouge, push-in lent ou dernier volet `04 · À NOTER`.
5. **14–15 s** fin propre : tenue de l'image finale ≥ 1 s (pas de boucle).

## Zones sûres
Haut 220 px (filet d'en-tête à 232), bas 320 px (rien sous y = 1600 ; la lecture chiffrée a sa ligne de base à 1590), droite 120 px (tout s'aligne à x = 960), gauche 60 px (les chiffres Archivo Black commencent à x ≈ 48–60 pour compenser leur approche). Les 320 px du bas restent vides : place des sous-titres de la plateforme.

## Librairies recommandées et pourquoi
- **D3.js 7.9** : échelles (`scaleLinear`) pour la grille et les barres, `d3.sum`, `d3.format`, `d3.line` + `curveCatmullRom`, **d3-geo** (`geoEquirectangular().fitExtent`, `geoGraticule`, `geoPath`) pour des cartes schématiques sans aucune donnée téléchargée. Construit tout le SVG une fois.
- **GSAP 3.15** : une seule timeline `paused`, seekée par `renderAt` (`tl.seek(t,false)`, `immediateRender:false`), easings nommés, `attr` tweens sur le SVG, `svgOrigin` pour le push-in. Les compteurs tweenent un objet d'état lu dans `renderAt` (robuste au seek).
- Rendu mesuré : 13,7 s / 100 frames (geographie, 61,5 s) et 20,5 s / 100 frames (evenements avec d3-geo, 92,3 s), CPU partagé — SVG pur, très économique.

## Familles de contenus adaptées / inadaptées
- **Adaptées** : geographie (classements, parts, cartes schématiques), evenements (comptes à rebours, dates, durées), explicatif chiffré, engagement (sondage « devine le chiffre »).
- **Inadaptées** : enfants (trop froid, pas de personnage), abstrait contemplatif, histoire narrative sans données (la grille réclame des chiffres).

## Shorts de preuve (chemins)
- `out/shorts/swiss-data__geographie__ou-vivent-8-milliards/short.mp4` — « Où vivent les 8 milliards d'humains ? »
- `out/shorts/swiss-data__evenements__j-272-eclipse-2-aout-2027/short.mp4` — « J-272 : l'éclipse totale du 2 août 2027 »

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)

> **Voix réellement utilisée pour tous les shorts : Fish Audio « Arnold »** (`d704cf8f1216490cbfbed89955f0e938`, modèle `s2.1-pro`, conteur masculin FR). Les noms de voix Gemini (Orus, Kore, Aoede…) qui suivent sont des suggestions historiques de casting par ton : Gemini a été abandonné (quota). Le placement, le débit et les silences décrits ici restent valables.

Une phrase par rubrique (4–5 s), qui **lit** le chiffre affiché ou le contextualise ; débit 2,4–2,6 mots/s, voix documentaire (Orus) ou grave (Charon). La voix démarre à 0,3 s et après chaque volet (+0,1 s). Le visuel ne porte que titres, chiffres et mots-clés : la voix apporte les verbes et la source. Les 320 px du bas sont libres pour les sous-titres automatiques.

## Risques et limites
- Monotonie si chaque short a la même mise en page : varier la visualisation centrale (unit chart, barres, timer, carte) tout en gardant en-tête, volet et lecture.
- Les chiffres géants saturent vite la largeur (3 chiffres max à 460 px, 4 à 360 px).
- Cartes schématiques simplifiées à la main : toujours les présenter comme « tracé approximatif », jamais comme carte exacte.
- Données : arrondir et sourcer dans le repère à droite (`ONU · 2024`) ; ne jamais afficher plus de précision que la source.
- Texte gris « fantôme » (#B9B3A6) volontairement sous AA tant qu'il est inactif : il doit passer à l'encre avant la fin de la rubrique.
