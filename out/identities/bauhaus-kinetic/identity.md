# Bauhaus Cinétique (bauhaus-kinetic)

## Nom
**Bauhaus Cinétique** — slug `bauhaus-kinetic`, version 1.0.0.

## Promesse en une phrase
Des formes primaires qui s'emboîtent sur une grille stricte pour expliquer ou défier en 15 secondes : chaque idée devient un puzzle géométrique qui se résout sous nos yeux.

## Mood & références de genre
Jeu de formes primaires, rythme, optimisme graphique, logique. Références de genre : affiche Bauhaus et constructivisme (aplats, cercle/carré/triangle), motion design géométrique « flat », jeux de logique et casse-têtes visuels. Pas d'ombre, pas de dégradé, pas de texture : la matière, c'est l'aplat et le bord net.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Valeur | Usage réel |
|---|---|---|
| fond | `#F2EDE3` (papier crème) | fond de toutes les scènes, quarts de disque des tuiles, joints des pavages |
| surface | `#FFFFFF` | cartes de titre, panneaux de pavage, pastilles de libellé |
| accent 1 | `#E63B2E` rouge | mot-clé du titre (`<em>`), cellule centrale, badge « −7 % », erreur ✕, compte à rebours final |
| accent 2 | `#F5B700` jaune | miel, cellules, carré « 3 s » |
| accent 3 | `#1D4ED8` bleu | quart de cercle d'angle, hexagones, triangle « 5 s » |
| accent 4 / texte | `#111111` encre | texte, grille (opacité 0,09), barres d'horizon, pied de page, cadres 8–12 px |
| muted | `#6B6458` | légende secondaire (contraste 5,3:1 sur le fond) |
| succès | `#111111` (pastille ✓ encre) | validation |
| danger | `#E63B2E` (pastille ✕ rouge) | erreur, trou |
Texte blanc uniquement sur rouge, bleu ou encre ; texte encre sur jaune et blanc (AA respecté partout).

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Display** : Unbounded 800, 100 px, interlettrage −3 px, interligne 1,04 (titres de scène : « Seuls 3 », « Trouve l'intrus »).
- **Titre** : Unbounded 800, 90–92 px, −3 px (cartes de titre, CTA « T'as trouvé en combien ? »).
- **Chiffres** : Unbounded 800, 58–120 px, −2 à −4 px (valeurs 4,56 / compte à rebours).
- **Corps** : Space Grotesk 500, 56 px, interligne 1,12, interlettrage 0 (sous-titres, pastilles).
- **Légende** : Unbounded 800, 54 px (numéro « N°06 »).
Un seul mot par titre en rouge (`<em>`). Jamais plus de 2 lignes de corps à l'écran.

## Formes & matières
Grille 6×10 (cellules 180×192 px) toujours visible en filigrane (encre, opacité 0,09), qui se « dessine » au démarrage. Vocabulaire : hexagone (pointe en haut), carré, cercle, triangle équilatéral, quart de disque, demi-disque, barres. Aplats purs, joints de 7–8 px couleur fond entre les tuiles, cadres encre 8–12 px. Signature fixe : pied de page Bauhaus dans la zone non sûre basse (rectangle encre + disque rouge + triangle jaune) et quart de cercle bleu en haut à droite sur les cartes de titre. Tout est dessiné par code (Paper.js), aucun asset.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- **Easings** : entrée `outBack(1.6)` (le « snap »), sortie `inQuart`, emphase/déplacement `inOutQuart`, morphs `inOutCubic`, tracés/barres `inOutCubic`, atténuations `outQuad`.
- **Durées** : fast 280 ms (pastilles, morph de badge), base 450 ms (titres, badges), slow 900 ms (déplacement + morph de la cellule).
- **Staggers** : 60 ms entre cellules d'un groupe ; 18–40 ms en grille depuis le centre (`stagger(ms,{grid:[c,r],from:'center'})`) ; 380 ms entre panneaux ; révélation `from: index` de l'élément clé.
- **Gestes signatures** : pop en stagger (échelle 0 -> 1 + rotation 60°), snap 90° (rotation 90° -> 0°), morph de forme (flubber), contour qui se trace, barre qui pousse, vague de « respiration » (échelle −6 %) pendant une attente.
- **Jamais** : rotation libre continue, flou, ombre portée, rebond élastique long, mouvement hors grille, texte qui défile, caméra qui bouge.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
2D plate, caméra fixe, cadrage centré sur la grille 6×10 ; pas de zoom, pas de parallaxe, pas de profondeur de champ. Le « mouvement de caméra » est remplacé par les transitions grid-wipe et par des changements d'échelle des objets (ex. l'intrus grossit ×1,3).

## Transitions (liste nommée, durée, quand les utiliser)
- **grid-wipe** (1,05 s, coupe à 0,525 s) : 6 colonnes rouge/jaune/bleu/encre/rouge/jaune tombent en stagger 45 ms (300 ms `inOutQuart`), couvrent l'écran, la scène change, puis elles repartent vers le bas. Entre deux idées (chaque changement de scène). Réalisée en DOM dans la scène ; équivalent ffmpeg `wipedown` si l'on monte des clips séparés. SFX : whoosh + thud à la coupe.
- **snap-90** (450 ms) : un élément arrive en tournant de 90° avec `outBack(1.6)` (badges, cadres, tuile qui se remet droite).
- **shape-morph** (280–900 ms) : une forme devient une autre via flubber (carré -> hexagone, cercle -> hexagone, cercle -> carré -> triangle -> hexagone pour le compte à rebours).

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
- **0–0,6 s hook** : la grille se dessine, l'objet-clé pop en stagger dès 0,1 s, le titre-question ou le défi est lisible avant 0,6 s.
- **Développement** : 2 à 3 scènes de 3–3,6 s séparées par des grid-wipes, une idée chiffrée par scène (titre display + 1–2 lignes de corps + une figure).
- **Chute** : révélation (morph, contour, ✓/✕, badge rouge).
- **Fin** : carte de titre reprise du hook (rime visuelle) ou CTA en formes, tenue ≥ 1,2 s sans coupure ; fin propre, non bouclée.
- Durée 14–16 s ; musique pluck-arp 120 bpm (un temps = 0,5 s) ; les événements visuels tombent sur les temps.

## Zones sûres
Haut 220 px, bas 320 px, droite 120 px, gauche 60 px. Texte et figures entre x = 60 et 960, y = 236 et 1600. Les zones non sûres ne portent que la signature décorative (pied de page Bauhaus, quart de cercle bleu) et les colonnes du grid-wipe.

## Librairies recommandées et pourquoi
- **Paper.js** : toute la géométrie vectorielle (pavages, rayons de miel, quarts de disque `arcTo`, booléens `subtract`, masques `clipped`) ; 2,6 ms/frame pour 64 hexagones redessinés.
- **flubber** : la transition signature shape-morph ; `string:false` + interpolateurs précalculés (0,43 ms/frame pour 64 morphs).
- **anime.js v4** : timeline unique en pause seekée à `t` qui pilote des objets d'état ; staggers en grille natifs (`grid`, `from:'center'`, `from:index`) ; 0,09 ms/frame.
- Texte en DOM (Unbounded / Space Grotesk via @fontsource) au-dessus du canvas. Coût total mesuré : 28–32 s/100 frames sous charge (capture JPEG dominante).

## Familles de contenus adaptées / inadaptées
- **Adaptées** : engagement (casse-têtes visuels, intrus, compte à rebours, votes par formes), explicatif à base géométrique, mathématique ou logique (pavages, proportions, comparaisons chiffrées), abstrait.
- **Moyennement** : enfants (formes et couleurs OK, mais typographie Unbounded serrée), géographie (cartes très stylisées seulement).
- **Inadaptées** : histoire et événements graves ou émotionnels (ton trop ludique), contenus photo-réalistes, tout ce qui demande des personnages expressifs.

## Shorts de preuve (chemins)
- `out/shorts/bauhaus-kinetic__explicatif__abeilles-hexagones/` — « Pourquoi les abeilles construisent en hexagones ? », 16 s.
- `out/shorts/bauhaus-kinetic__engagement__trouve-l-intrus/` — « Trouve l'intrus en 5 secondes », 14 s.

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)
Une phrase par scène, posée 0,1–0,3 s après la coupe du grid-wipe et finie avant le wipe suivant (≈ 3–3,5 s, 7–9 mots). Débit ≈ 2,6 mots/s. L'écran ne porte que le titre (2–3 mots) et les chiffres ; la voix donne la phrase complète et le « pourquoi ». Voix : Orus (explicatif), Fenrir (engagement). Pendant un compte à rebours, la voix ne compte que les 3 dernières secondes et laisse les ticks respirer. Musique pluck-arp à −18 dB, à ducker sous la voix (assemble.py `--voice`).

## Risques et limites
- Lisibilité de la grille : un motif trop régulier peut rendre un « intrus » trop facile ou trop dur ; tester la recherche en vrai avant de rendre.
- Unbounded 800 est large : titres limités à ~11 caractères par ligne à 100 px.
- Identité très ludique : peu adaptée aux sujets graves.
- Le coût de rendu est dominé par la capture navigateur (~0,3 s/frame) : réserver ~2–2,5 min par short de 15 s sous charge.
- Le morph flubber peut produire des formes intermédiaires molles (cercle « carré arrondi ») : garder les morphs ≤ 900 ms.
