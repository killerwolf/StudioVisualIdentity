# Cabinet de curiosités

## Nom
Cabinet de curiosités (`cabinet-curiosites`) — déclinaison C de la phase 1 du studio Un Jour Une Histoire (2026-11-03) ; thème themes/cabinet-curiosites.json.

## Promesse en une phrase
Chaque objet devient une pièce de collection : fond bleu nuit, étiquettes de musée crème et or, lettres à empattements.

## Mood & références de genre
Vitrine de musée la nuit : fond bleu nuit uni avec vignettage, étiquettes crème, bandes vert canard, bordeaux et or. Références de genre : cabinets de curiosités, cartels de musée, catalogues d'exposition. Ton : élégant, mystérieux, érudit sans être savant.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Valeur | Usage réel dans les shorts |
|---|---|---|
| fond (tapis) | `#161E34` | tapis « nuit » plein cadre |
| surface (papier) | `#F2E8D0` | toutes les pièces qui portent du texte |
| texte (encre) | `#141826` | tout le texte, sur papier |
| encre douce | `#56545C` | yeux de carte, légendes secondaires |
| accent 1 — le sujet | `#1C4C54` | bande du sujet (texte papier dessus) |
| accent 2 — mot fort | `#841E30` | bande d'un mot fort, tampon, total |
| accent 3 — action | `#D6AC58` | post-it, bande d'action (texte encre) |
| accent 4 — commentaire | `#CE969C` | post-it de commentaire |
| accent 5 — détail | `#76A8AA` | post-it de détail |

Règle : le texte ne se pose **jamais** directement sur le tapis : toujours sur une pièce de papier (bande, carte, post-it, sous-titre).

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Titres en bandes** : DM Serif Display 400, capitales, 86–120 px, une bande par ligne, inclinées en alternance (−1,4° / +1,4°).
- **Titre de carte** : DM Serif Display, 46 px ; œil de carte en DM Mono, 24 px.
- **Sous-titres incrustés** (Short) : DM Serif Display (italique), 54 px, encre sur bande papier, centrés vers y = 1330, une réplique à la fois.
- **Étiquette de série** (« L'HISTOIRE DE… · 01 ») : DM Mono, 28 px, papier sur bande encre.
- Tampons : DM Serif Display, capitales, cadre arrondi, encre un peu passée.
Fichiers : `out/shared/papier-moteur/assets/fonts/` (woff2 / ttf lus directement par Pillow ; jamais une police du système).

## Formes & matières
Pièces de papier à bord coupé aux ciseaux (contour irrégulier déterministe), grain de papier ±3,5 %, ombre portée floue en bas à droite (décalage 9/14 px, 42 %). Éléments : bandes, cartes, post-it (bandeau collant en haut), tickets de caisse, tampons, images scotchées, portraits en silhouette papier, logos et emoji de la librairie. Fond : aplat sombre vignetté, sans grille.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- **Stop-motion** : le mouvement avance par pas de 1/12 s (rendu à 30 i/s).
- **pop** (par défaut) : 4 pas, échelle 0,35 → 1,15 → 0,96 → 1 (0,33 s), avec un bruit de papier posé.
- **chute** / **glisse** : 5 pas avec ralenti à l'arrivée (0,42 s), depuis le haut ou la gauche.
- **dépose** (rythme calme, vidéos longues) : 3 pas, sans rebond.
- **frisson** du personnage : ±2 px et ±0,25°, change à chaque pas.
- Décalage entre deux pièces d'une même scène : ≈ 0,5 s, calé sur les phrases de la voix.
- Jamais : fondu lisse, interpolation fluide à 30 i/s, rebond élastique continu, texte qui apparaît sans pièce.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
Plan fixe frontal, vue de dessus sur la table ; pas de profondeur de champ. Caméra optionnelle (`ep.camera`) : zoom autour d'un point et tremblement, pour les vidéos sans voix seulement.

## Transitions (liste nommée, durée, quand les utiliser)
- **Glissé de scène** : la scène qui se termine glisse vers la gauche en pas (0,25 s), avec un bruit de glissement ; à chaque nouvelle scène.
- **Écran de fin** (Short, 3,2 s) : bouton, nom de la chaîne en deux bandes, slogan, personnage qui salue, post-it.
- **Générique** (Long, 5 s) et **onglets de chapitres** (Long).

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
- 0–0,15 s : la première scène est déjà posée (étiquette de série + titre en 2–3 bandes) ; la voix démarre à 0,15 s.
- Développement : une scène par réplique, 2 à 4 pièces posées sur les phrases.
- Chute : question au spectateur (vote en commentaire) sur deux post-it.
- Fin : écran de fin de 3,2 s ajouté par le moteur. Durée totale = voix + pauses + 3,2 s.

## Zones sûres
Haut 220 px, bas 320 px, droite 120 px, gauche 60 px (TikTok). Logo en coin à (150, 150) dans la marge haute ; sous-titres vers y = 1330 ; rien d'important sous y = 1600.

## Librairies recommandées et pourquoi
Moteur Python partagé `out/shared/papier-moteur/` (Pillow + NumPy + OpenCV + ffmpeg) : rendu image par image déterministe, en tranches parallèles (`JOBS`), sans navigateur ; ≈ 2–4 s de calcul par 100 images sur 4 cœurs. Mixage voix + musique + bruitages et mastering −14 LUFS intégrés (`son.py`).

## Familles de contenus adaptées / inadaptées
- Adaptées : `explicatif` (prouvé), `histoire` (prouvé), `engagement` (vote sur post-it), objets du quotidien, mots et expressions.
- Inadaptées : `abstrait` (pas de matière en mouvement continu), `geographie` riche en cartes (pas de cartographie dans le moteur).

## Shorts de preuve (chemins)
- `out/shorts/cabinet-curiosites__explicatif__d-ou-vient-le-mot-sandwich/` — D'où vient le mot sandwich ?
- `out/shorts/cabinet-curiosites__histoire__la-fourchette-a-fait-scandale/` — La fourchette a fait scandale

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)
Voix off continue, une réplique par scène ; le moteur trouve le début de chaque phrase dans l'audio et y pose les pièces. Débit conseillé 2,4–2,8 mots/s (adultes) ; voix des preuves : Gemini Sulafat (féminine, chaude), une réplique par appel, silences rognés. Les sous-titres reprennent le texte exact de chaque réplique.

## Risques et limites
Fond sombre : voisins neon-lab / cosmos-doc / liquid-chrome dans un fil ; garder les pièces papier crème et l'or. Les bandes or avec texte crème manquent de contraste : texte encre sur or. Le moteur mixe lui-même la voix (pas d'étape `tts.py`) ; l'écran de fin ajoute 3,2 s : garder la voix sous ≈ 16 s pour rester sous 20 s.
