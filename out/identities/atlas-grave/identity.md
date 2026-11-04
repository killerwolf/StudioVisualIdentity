# Atlas Gravé — design system

## Nom
**Atlas Gravé** (`atlas-grave`). Chaque short est une planche numérotée d'un atlas imaginaire du XVIIIe siècle : « PLANCHE V · FLEUVES », « PLANCHE IX · VOYAGES ».

## Promesse en une phrase
Un savoir géographique ou historique s'imprime sous vos yeux, à l'encre, sur une carte gravée qui bouge à peine, et finit sur une question ouverte.

## Mood & références de genre
Cabinet de cartographe, papier vergé, encre sépia, solennité érudite. Genres : atlas des Lumières, gravure en taille-douce, documentaire historique posé. Rien de numérique à l'œil : pas d'aplat saturé, pas de lueur, pas de dégradé « tech ». Le mouvement est celui d'une plume et d'une loupe qui glisse sur la carte.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Hex | Usage réel dans les shorts |
|---|---|---|
| Fond | `#EFE3C8` | papier vergé (texture pycairo `paper.png`) |
| Surface | `#E2D2AE` | voile sous la fenêtre de carte ; terres `#E6D6B2` hachurées à −40° |
| Accent 1 — sanguine | `#8C2F1B` | rangs (chiffres romains), dates Cinzel, tracé de route, sceaux, fleuve actif ; **danger** (perte d'un navire, mort) |
| Accent 2 — bleu d'encre | `#2D4A5A` | eau, mers hachurées, chiffres IBM Plex Mono, compteur ; **succès** |
| Accent 3 — or | `#B8862B` | filets ornementaux et liseré du cartouche **uniquement** (contraste 2,6:1, jamais pour du texte) |
| Texte | `#2A1F14` | titres, noms, légendes (contraste 13:1 sur le fond) |
| Atténué | `#6B5A43` | réserve (non utilisé pour du texte < 54 px) |

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Display** : Cormorant Garamond 700, 108 px, interlettrage 0 — titre sur 2 lignes (y 400 / 500).
- **Titre de planche & dates** : Cinzel 600, 54 px, +0,06 em (en-tête) ; Cinzel 700, 56 px, +0,06–0,08 em (dates « SEPT. 1519 », « 1519 – 1522 », compteur « 5 NAVIRES »), chiffres romains Cinzel 700 54 px.
- **Corps** : Cormorant Garamond 700, 62–68 px (noms, légendes d'événement), 76–84 px (cartouche, chiffre-clé « 18 survivants ») ; italique 700 56–58 px pour la relance en sanguine.
- **Mesures** : IBM Plex Mono 600, 54 px (« 6 650 km »), alignées à droite sur x = 904.
- Aucun texte informatif sous 54 px ; titres ≥ 90 px.

## Formes & matières
Papier vergé (vergeures tous les 9 px, pontuseaux tous les 150 px, nuages de pâte, rousseurs) ; cadre de planche double filet + bordure graduée noir/blanc (46,196)–(946,1636) ; fenêtre de carte à double filet ; terres hachurées fines, mers en lignes horizontales ondulées ; cartouche ovale guilloché (14 trochoïdes) ; rose des vents 16 pointes à demi-pointes hachurées, nord sanguine ; caravelle gravée ; sceau circulaire sanguine (double cercle). Léger tremblé d'encre (feDisplacementMap 2,4 px) sur la carte uniquement. Vignettage sépia fixe en dernier calque. Tout est généré : pycairo pour les matières, D3 pour la carte et les données.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- **Tracé à l'encre** : `stroke-dashoffset` (côtes 1,1 s `power1.out` ; fleuves/rubans 0,9–1,0 s `power2.out`/`sine.inOut`), route au pointillé qui s'allonge derrière le navire.
- **Apparition à l'encre** (enter) : opacité 0 → 1 + montée de 10–14 px, 0,4–0,5 s `power2.out`.
- **Sceau** (emphasis) : échelle 1,6 → 1, 0,35 s `back.out(1.6)`, accompagné d'un *thud + chime*.
- **Sortie** : 0,25–0,3 s `sine.inOut`.
- **Rythme** : un temps fort toutes les **1,5 s** (2 temps à 80 bpm) — compte à rebours V → I, changements de légende, pertes de navires.
- Durées tokens : fast 0,35 s, base 0,6 s, slow 1,2 s. Hook complet ≤ 0,5 s (titre à 35 % d'opacité dès la frame 0).
- **Jamais** : rebonds élastiques, secousses de caméra, rotation 3D, flou de mouvement, couleur saturée hors palette, texte qui défile, coupe sèche plein cadre.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
Caméra 2D orthographique sur la carte seulement (titre, tableau et légendes restent fixes, comme une page). Mouvements : **zoom cartographique lent** k 1 → 1,75–2,4 sur le sujet (0,7–1,0 s `sine.inOut`) ; **panoramique sur parchemin** qui suit le sujet (moyenne glissante ±0,6 s pour lisser) ; **recul final** en vue d'ensemble (k 1,16 sur la mappemonde ; k 0,36 sur la carte plate déroulée). Pas de profondeur de champ : gravure nette, vignettage fixe.

## Transitions (liste nommée, durée, quand les utiliser)
| Nom | Durée | Équivalent ffmpeg xfade | Quand |
|---|---|---|---|
| encre-qui-sèche | 0,3 s sortie + 0,4 s entrée | `fade` | changement de date / légende |
| sceau | 0,35 s | `circleopen` | révélation d'un rang, d'un événement-clé |
| panoramique-parchemin | 0,7 s | `slideleft` | passage d'un lieu à un autre (mouvement de caméra, jamais de coupe) |
| cartouche-final | 0,5 s | `fade` | ouverture de la question finale |
Les shorts sont des plans-séquences : les transitions se font dans la scène ; les équivalents xfade servent si on assemble des clips.

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
1. **0–0,5 s — hook** : planche titrée (en-tête Cinzel + titre 108 px) et carte du monde qui s'encre ; le sujet est déjà visible (fleuves bleus, navire à quai).
2. **0,5–2,2 s — mise en place** : tracé complet, structure annoncée (rangs vides I–V, compteur 5 navires).
3. **2,2–10 s — développement en temps forts de 1,5 s** : zoom sur chaque sujet, sceau, ligne de tableau ou légende datée.
4. **10–13,5 s — chute** : la nuance (débat Nil/Amazone ; mort de Magellan, retour d'Elcano, 18 survivants).
5. **13,5–fin — clôture** : recul en vue d'ensemble + **cartouche guilloché** posant un duel « X ou Y ? » ; dernière 1,5 s tenue (fin propre, pas de boucle).

## Zones sûres
Haut 220 px, bas 320 px, droite 120 px (TikTok). Tout le texte entre y = 250 et y = 1580, x ≤ 904. Le cadre gravé (y 196–1636) déborde volontairement d'un filet décoratif dans les marges ; aucun contenu n'y est placé.

## Librairies recommandées et pourquoi
- **D3.js 7.9** : `d3-geo` (NaturalEarth1, Equirectangular, graticule, `geoArea` pour réorienter les anneaux dessinés à la main), `d3.line` + `curveCatmullRom`/`curveBasis` pour fleuves et routes, échelles pour les longueurs, sélections SVG.
- **GSAP 3.15** : timeline d'état unique `paused`, seekée par `renderAt` (`tl.seek(t,false)`, `immediateRender:false`) — orchestre caméra, sceaux, légendes, compteurs.
- **pycairo 1.29** : toutes les matières gravées en PNG précalculés (papier, cadre, cartouche guilloché, rose, mer, caravelle, vignette) : remplace les filtres SVG plein cadre coûteux à chaque frame.

## Familles de contenus adaptées / inadaptées
- **Adaptées** : `geographie` (classements, records, fleuves, frontières, découvertes), `histoire` (expéditions, routes, batailles sur carte, chronologies), `explicatif` à composante spatiale (migrations, routes commerciales).
- **Possibles avec adaptation** : `engagement` (duel/vote en cartouche final).
- **Inadaptées** : `enfants` (trop solennel, texte serré), `abstrait` (sans carte ni donnée l'identité perd son sens), `evenements` à forte énergie (le rythme posé de 1,5 s contredit l'urgence).

## Shorts de preuve (chemins)
- `out/shorts/atlas-grave__geographie__plus-longs-fleuves-du-monde/` — 15 s, D3 + GSAP + pycairo.
- `out/shorts/atlas-grave__histoire__premier-tour-du-monde-1519-1522/` — 16 s, D3 + GSAP + pycairo.

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)

> **Voix réellement utilisée pour tous les shorts : Fish Audio « Arnold »** (`d704cf8f1216490cbfbed89955f0e938`, modèle `s2.1-pro`, conteur masculin FR). Les noms de voix Gemini (Orus, Kore, Aoede…) qui suivent sont des suggestions historiques de casting par ton : Gemini a été abandonné (quota). Le placement, le débit et les silences décrits ici restent valables.

Voix documentaire posée (Orus pour la géographie, Charon pour l'histoire), débit ≤ 2,6 mots/s, une phrase courte par temps fort de 1,5 s (« Cinquième : l'Ienisseï. »). Le visuel ne montre que noms, dates et chiffres : la voix porte le récit (« Trois mois pour traverser le Pacifique »), la nuance (débat des mesures) et la question finale. Le tableau et les légendes sont fixes pendant que la voix parle ; la musique (pad ré dorien, 80 bpm) laisse le médium libre (pas de mélodie dense).

## Risques et limites
- Côtes simplifiées à la main : lisibles à l'échelle monde, approximatives en zoom > 2,5 (ne pas zoomer sur un pays).
- Faits contestés (longueurs de fleuves, effectifs d'équipage) : toujours signaler la nuance à l'écran ou en voix off.
- Le tremblé d'encre (`feDisplacementMap`) et le motif mer en image coûtent ~0,1 s/frame en SwiftShader ; éviter de l'appliquer au plein cadre.
- Palette peu contrastée pour l'or : ne jamais l'utiliser pour du texte.
- Identité lente par nature : sur TikTok, la tenir à 12–16 s et garder un temps fort toutes les 1,5 s.
