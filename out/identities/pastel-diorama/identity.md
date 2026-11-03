# Diorama Pastel — identité visuelle

## Nom
**Diorama Pastel** (`pastel-diorama`) — une maquette de chambre d'enfant posée sur un socle de feutrine, filmée comme un petit plateau de stop-motion.

## Promesse en une phrase
Expliquer ou faire jouer les 6–10 ans dans un monde de jouets doux et rassurants où chaque idée « saute » en place avec un rebond, sans jamais faire peur ni brusquer.

## Mood & références de genre
Chambre d'enfant, jouets en bois et feutrine, douceur, sécurité, émerveillement. Genre : film d'animation en stop-motion pour tout-petits, livre pop-up, maquette de vitrine. Personnages inventés à visage minimal (deux points, joues roses, sourire en arc) : Plip la goutte, le petit renard. Tout est rond, rien n'est pointu ni sombre.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Couleur | Usage |
|---|---|---|
| Fond | `#FFE8EF` (dégradé radial `#FFF4F7` -> `#FFDCE7` + trame de points `#FFC9D8`) | fond permanent, identique dans les deux shorts |
| Surface | `#FFFFFF` | pastilles d'étape, cartes CTA, galette du socle |
| Accent 1 rose | `#FF8FAB` | toits, joues, flèche évaporation, pastille n°1 |
| Accent 2 bleu | `#8ED6FF` | eau, boîtes cadeau, pastille condensation |
| Accent 3 jaune | `#FFD670` | soleil, rubans, kicker, compte à rebours |
| Accent 4 menthe | `#9BE7B0` | socle en feutrine, succès (bonne boîte) |
| Texte | `#3B2E5A` (violet nuit) | tout le texte, traits des visages |
| Encre d'accent | `#E23D72` (mot-clé du titre, ≥ 3:1 sur le fond pour du texte ≥ 96 px), `#2F7FB5` (mot-clé dans les cartes blanches) |
| Succès / danger | `#9BE7B0` / `#E23D72` | bonne réponse / alerte douce (jamais de rouge vif) |
| Personnages | goutte `#6EC3F5`, renard `#FF9E5E`, nuage de pluie `#C9D3EE` | |

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Display** : Baloo 2 800, 132 px, interligne 1.0, interlettrage −0.01em, ombre portée pleine `0 8px 0 #FFC2D3` (titre-question du hook, 2 lignes max).
- **Titre** : Baloo 2 800, 96 px, dans une pastille blanche arrondie avec puce numérotée de 112 px (étapes « 1 · Évaporation », « 1, 2 ou 3 ? »).
- **Corps** : Nunito 800, 60 px, interligne 1.15 (cartes CTA blanches, 2 lignes max).
- **Légende** : Nunito 800, 56 px (kicker jaune, mots-clés en pilule, étiquettes « vide ! »). Jamais sous 56 px.
- **Chiffres** : Baloo 2 800, 84 px dans des pastilles rondes ; compte à rebours 190 px dans une bulle jaune de 250 px.

## Formes & matières
Tout est arrondi : traits ronds Zdog (stroke épais), boîtes A-Frame à arêtes arrondies (géométrie `roundbox` maison), sphères, cônes doux. Matière feutrine mate (`roughness: 1`, `metalness: 0`, aucune brillance), ombres portées « jouet » pleines et décalées vers le bas sous les éléments d'interface (`0 8–14px 0`), ombres de contact = disques transparents. Socle circulaire menthe sur galette blanche, arbres-boules, maisonnette au toit rose, fleurs-points. Visages : deux points + reflet blanc, joues roses, sourire en arc.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- Entrées : `back.out(1.8)` 0.5 s (pastilles, cartes, personnages) ; sorties : `back.in(1.6)` 0.3 s.
- Atterrissages : `bounce.out` (boîtes qui tombent, couvercle qui se referme) ; squash & stretch `elastic.out(1,0.35)` 0.6–0.9 s à chaque contact.
- Trajets : `power1.inOut` (montée de la vapeur 2.6 s), `power2.in` (chute de la goutte 1.15 s), échanges de boîtes `inOutCubic` 0.6–0.85 s avec arc avant/arrière.
- Stagger : 0.16 s (numéros, pilules), 0.07 s (bouffées du nuage).
- Flottement permanent : personnage `sin(t·3.1)·8 px`, nuage `sin(t·1.6)·10 px`, respiration des boîtes ±5 %.
- Durées : fast 0.3 s, base 0.5 s, slow 1.3 s.
- **Jamais** : coupe sèche, flash, shake de caméra, chute brutale sans rebond, mouvement linéaire visible, noir à l'écran, personnage qui a peur ou pleure.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
Plan-séquence unique sur la maquette, vue en plongée douce (~25–28°) : Zdog `rotate.x = −TAU/13`, A-Frame fov 30 à ~13 m, lookAt scripté (`Matrix4.lookAt`). Mouvement signature : **travelling latéral de maquette** (sinus lent 0.45 rad/s, ±0.12 rad ou ±0.7 m). Push-in doux de 13 % sur le moment de suspense. Pas de profondeur de champ (tout est net, comme une maquette photographiée). Le socle occupe le tiers inférieur-milieu (y ≈ 1000–1500), le ciel au-dessus reste libre pour l'action et la voix.

## Transitions (liste nommée, durée, quand les utiliser)
- **pastille-pop** (0.3 s sortie + 0.5 s entrée) : changement d'étape ; la pastille du haut sort en `back.in`, la suivante rebondit. Équivalent ffmpeg `fade` 0.3 s si clips séparés.
- **teinte-ciel** (1.4 s) : changement d'ambiance (altitude, froid) par un dégradé bleu `#DDEBFF` en fondu. Équivalent `fadewhite`.
- **couvercle-pop** (0.5 s) : révélation (couvercle qui saute, nuage qui éclate) + confettis aux couleurs d'accent. Équivalent `circleopen`.
Les transitions sont faites dans la scène (un seul plan), jamais de coupe.

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
1. **Hook 0–1 s** : la maquette est déjà là (pop d'échelle 0.62 -> 1), le personnage rebondit au-dessus, titre-question en 132 px + kicker jaune (visibles dès 0.1 s).
2. **Mise en place 1–3 s** : le personnage fait un geste (saute, salue, plonge dans la boîte).
3. **Développement 3–11 s** : 3 étapes en pastilles numérotées (≈ 3.3 s chacune) ou une épreuve (mélange 5 s + compte à rebours 3-2-1).
4. **Chute 11–14 s** : révélation (splash, couvercle-pop + confettis) avec squash élastique.
5. **Fin 14–16 s** : récapitulatif (cycle fléché, mots-clés) ou carte CTA blanche, clin d'œil du personnage ; fin propre, état proche du début (boucle narrative).

## Zones sûres
Haut 220 px (rien ; kicker/pastilles à partir de y = 236), bas 320 px (rien d'important sous y = 1600 ; cartes CTA à y = 1400–1580), droite 120 px (textes calés à gauche x = 72, largeur ≤ 900), gauche 60 px. Le socle décoratif peut déborder légèrement dans les marges, jamais un texte ni un personnage.

## Librairies recommandées et pourquoi
- **Zdog** : pseudo-3D plate à traits ronds = exactement le look « jouet en feutrine » ; ultra léger, déterministe ; personnages en quelques formes ; `renderOrigin` donne les positions écran des ancres.
- **GSAP** : timeline d'états avec easings nommés (back, elastic, bounce) ; `seek(t,false)` sans retour, un tween par propriété -> stills et vidéo identiques.
- **A-Frame** : vraie 3D (volumes, éclairage doux hémisphérique) quand il faut des objets manipulables (boîtes qui s'échangent, couvercles) ; chaînes pour `geometry/material`, boucle coupée, rendu manuel. Sans ombres temps réel.
- Overlays texte en DOM (Baloo 2 / Nunito) dans les deux cas : la typo est identique quelle que soit la librairie.

## Familles de contenus adaptées / inadaptées
- **Adaptées** : enfants (cycles, « d'où vient… ? », animaux, saisons), engagement (jeux de suivi, devinettes, « choisis ta boîte »), explicatif très simple (3 étapes), évènements doux (anniversaire, rentrée).
- **Inadaptées** : histoire violente, actualité grave, data dense (graphes chargés), géographie précise (cartes détaillées), tout ce qui demande de l'ironie ou de la tension sombre.

## Shorts de preuve (chemins)
- `out/shorts/pastel-diorama__enfants__d-ou-vient-la-pluie/` — Zdog + GSAP, 16 s, cycle de l'eau avec Plip la goutte.
- `out/shorts/pastel-diorama__engagement__choisis-ta-boite-renard/` — A-Frame + GSAP, 15 s, jeu des 3 boîtes et du petit renard.

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)
La voix (Gemini : Leda pour expliquer, Puck pour jouer) parle sur chaque étape, une phrase courte par pastille, en démarrant 0.05–0.1 s après l'apparition de la pastille. Débit ≤ 2.6 mots/s, phrases de 4 à 10 mots. Le visuel ne montre que le mot-clé (« Évaporation », « 1, 2 ou 3 ? ») : la voix donne la phrase complète. Le ciel entre la pastille du haut et le socle (y ≈ 600–1000) reste libre pour l'action ; aucun sous-titre long. La musique music-box (−18 dB) laisse de la place aux médiums de la voix ; les SFX sont courts (pop, chime).

## Risques et limites
- Rose sur rose : l'encre d'accent `#E23D72` ne passe AA (3:1) qu'en grand corps ; dans les petites tailles, rester en `#3B2E5A`.
- Vapeur « visible » : la vraie vapeur d'eau est invisible ; on la figure par des volutes translucides et la voix le précise.
- A-Frame sous SwiftShader : coût de rendu bien plus élevé que Zdog (voir short.json) et pas d'ombres temps réel (5–10 min/100 frames) ; arêtes arrondies = géométrie maison.
- Univers très doux : peu adapté à la tension ; le suspense passe par le rythme (accélération des échanges, compte à rebours) et le son, pas par l'image.
- Personnages simples : risque de ressemblance générique avec des mascottes existantes -> garder les visages minimalistes inventés.
