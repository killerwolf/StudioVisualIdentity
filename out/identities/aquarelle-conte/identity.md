# Aquarelle Conte — design system

## Nom
**Aquarelle Conte** (`aquarelle-conte`), v1.0. C'est un album jeunesse peint à l'aquarelle, qu'on feuillette le soir.

## Promesse en une phrase
Chaque short est une page d'album : un paysage peint à l'eau qui respire, un petit personnage ou un monument en vecteur aquarellé, et une phrase courte posée sur du papier crème, racontée par une conteuse.

## Mood & références de genre
- Histoire du soir, lumière de veilleuse, tendresse, lenteur assumée.
- Genres : album jeunesse illustré, conte animé, « il était une fois » documentaire.
- Matières : papier cold-press à grain, pigments transparents qui se superposent, bords de lavis un peu plus foncés.
- On ne cite aucune œuvre existante. Les personnages sont inventés (Lulu la petite chouette) et les monuments sont stylisés (blocs de pierre).

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Hex | Usage réel |
|---|---|---|
| Fond (papier) | `#F7F1E6` | papier du bas de page, fondu final |
| Surface | `#EFE4D0` | murs, cartouches, halo de lune |
| Accent 1 corail | `#E88D72` | toits, aube et crépuscule, voile de la felouque, bec |
| Accent 2 bleu | `#6C9BCF` | ciels, mer, collines lointaines ; en version profonde `#4E7FB8`, c'est le mot mis en valeur dans les titres (3,7:1 : uniquement ≥ 92 px, AA grand texte) |
| Accent 3 or | `#F2C14E` | étoiles, Lune, Soleil, feu du phare, yeux |
| Accent 4 vert | `#7FB685` | collines proches, arbres (sert aussi de « succès ») |
| Texte | `#3A3042` | tous les titres et le corps de texte (contraste sur `#F7F1E6` 11,1:1, AAA) |
| Muted | `#8A6A55` | troncs, coques, contours bois |
| Danger / surtitre | `#B2573E` | surtitres, mots d'alerte (« fort de Qaitbay ») ; contraste 4,3:1 sur le papier : AA **grand texte** uniquement (réservé à ≥ 54 px) |
| Ciel de nuit | `#33406E` | haut des ciels nocturnes |

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Display** : Fraunces 700, 108 px, interligne 1.0, interlettrage −2 px. Réservé au titre du hook (2 lignes), avec un mot en `#4E7FB8`.
- **Titre** : Fraunces 700, 92 px, interlettrage −1,5 px. Il porte le mot-clé, la date ou le chiffre de chaque temps.
- **Corps** : Nunito 600, 58 px, interligne 1.18, deux lignes au maximum.
- **Surtitre** : Nunito 600, 54 px, couleur `#B2573E` (« Histoire du soir », « Il était une fois… »).
- Toujours ferré à gauche (x = 64, largeur 880). Les exposants passent par `<sup>` (XIV<sup>e</sup>), jamais par le caractère « ᵉ ».

## Formes & matières
- **Lavis p5** : polygones déformés récursivement (subdivision et bruit gaussien proportionnel à la longueur du segment), 16 à 40 couches à 3–14 % d'opacité, avec un contour 20 % plus foncé une couche sur six.
- **Bandes de ciel** (`band()`) : leur bord supérieur est subdivisé tous les 90 px. Ne jamais déformer un grand rectangle, sinon il en sort des « montagnes ».
- **Vecteur aquarellé (Paper.js, `wc()`)** : 2 à 3 copies translucides du tracé (α 0,5 à 0,75), jitterées de 1 à 3 px, plus un bord à 62 % de la teinte. Formes rondes et pierres arrondies (rayon 3).
- **Grain papier** : relief cold-press calculé une fois (3 octaves de bruit, éclairage rasant), canvas en `soft-light` à 0,55, avec une vignette chaude en `multiply`.
- **Mise en page « page d'album »** : l'illustration occupe 0–1090 px et se termine par un bord de lavis crème. Le texte est posé sur le papier en dessous.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- Entrée du texte, « l'encre s'imbibe » : 0,6 s `outCubic` (opacité, flou 8→0 px, translateY 18→0 px). Sortie en 0,4 s `inOutSine`.
- Emphase : `outBack` (cercles pointillés, loupe), toujours sur des objets, jamais sur le texte.
- Respiration : texte en scale ±0,4 %, personnages ±1,2 %.
- Rythme : un temps toutes les 3 à 3,5 s, et pas plus de 2 blocs de texte à l'écran.
- Staggers : 0,09 s (étoiles, cercles), 0,03 s par pierre et 0,13–0,15 s par rang, 0,022 s pour un réassemblage massif.
- Pendant une montée d'objet, un léger dépassement est permis (`outCubic` depuis 160 px au-dessus).
- **Jamais** : de cut sec, de zoom punchy, de texte qui rebondit, de clignotement rapide, de couleur saturée hors palette, de noir pur, ni de secousse en dehors d'un séisme ou d'un choc narratif.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
- 2D orthographique multiplane : trois plans (ciel, loin, près) et le vecteur collé au plan « près ».
- Un seul mouvement, un travelling latéral lent `inOutSine` sur toute la durée. Décalages : ciel −10 px, loin −20/−30 px, près −30/−60 px. Les calques font au moins 1240 px de large pour ne jamais découvrir le bord.
- Cadrage fixe en plan d'ensemble, avec le sujet (personnage ou monument) dans le tiers central, entre 640 et 1000 px.
- Pas de profondeur de champ : la distance se lit par la valeur (les plans lointains sont plus bleus et plus clairs) et par la parallaxe.
- Secousse de 7 px seulement pour un séisme.

## Transitions (liste nommée, durée, quand les utiliser)
| Nom | Durée | Équiv. ffmpeg | Quand |
|---|---|---|---|
| `lavis-qui-s-ouvre` | 0,9–1,2 s | `circleopen` | changement d'heure ou d'époque : le nouveau ciel se révèle dans une tache d'eau déformée qui grandit depuis la source de lumière (Soleil, feu, Lune). 3 paliers, ou `bloomSoft` à 5 paliers si l'écart de valeur est fort (nuit → matin). |
| `fondu-de-ciel` | 2,0 s | `dissolve` | évolution dans la même scène (aube → jour) |
| `encre-qui-s-imbibe` | 0,6 s / 0,4 s | `fade` | entrée et sortie de chaque bloc de texte |
| `fondu-papier` | 0,8 s | `fadewhite` | fin de chaque short : tout se dissout dans le papier `#F7F1E6` |

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
1. **0–3,4 s, hook** : la scène est déjà peinte à la frame 0. Un événement visuel démarre avant 0,25 s (étoile filante, pierres qui tombent du ciel). Le surtitre arrive à 0,05 s et le titre display à 0,15 s.
2. **3,4–10 s, développement** : 2 ou 3 temps de 3 à 3,5 s, chacun ouvert par un `lavis-qui-s-ouvre` ou un geste du sujet. Chaque temps a un mot-clé en Fraunces 92 et une phrase en Nunito 58.
3. **10–13 s, chute** : la révélation ou le retournement (loupe magique, séisme), avec un seul geste fort.
4. **Fin, 12–16 s** : retour au calme (nuit, matin). La formule de conte (« Bonne nuit, Lulu… », « Fin. ») précède un `fondu-papier` de 0,8 s.
- Durée : 15–16 s. Son généré : music-box (enfants) ou pad (histoire). Signature sonore : chime E6 au hook, swell sur chaque lavis, chime grave final.

## Zones sûres
- Haut 220 px : uniquement du ciel. Le sommet du phare est à ≈ 300 px et l'étiquette de toise à ≈ 290 px.
- Bas 320 px (> 1600 px) : papier vide. Le texte s'arrête à 1560 px.
- Droite 120 px : aucun texte (largeur 880 depuis x = 64) ; le décor peut y déborder.
- Gauche : marge de 64 px.

## Librairies recommandées et pourquoi
- **p5.js 2.3 (mode instance, sans preload)** : moteur de lavis. Tout est pré-rendu une fois au `ready` dans des `p5.Graphics`, ce qui prend environ 1 à 2 s pour 6 à 9 calques. Chaque frame compose ensuite les calques par `drawingContext.drawImage` avec `globalAlpha` et des clips (transitions). C'est rapide et déterministe (graine mulberry32).
- **Paper.js 0.17** : vecteur pour les personnages, bâtiments, faisceaux, toises et pointillés. Les matrices absolues sont posées par frame (`applyMatrix=false`, `item.matrix = …`) et le rendu se fait à la main avec `paper.view.update()` et `autoUpdate=false`. Cela permet d'écrire des animations « fonction pure de t », comme des pierres qui tombent puis se réassemblent, sans état.
- Le texte est en DOM : polices @fontsource et filtres CSS (flou d'entrée).
- Code partagé : `aq.js`, identique dans les deux `src/`.

## Familles de contenus adaptées / inadaptées
- **Adaptées** : `enfants` (histoires du soir, questions d'enfants), `histoire` (« il était une fois » : monuments, légendes, inventions), certains `geographie` (paysages, saisons).
- **Possibles avec prudence** : `explicatif` simple, à une seule idée.
- **Inadaptées** : `evenements` (actualité, urgence), `engagement` agressif (votes nerveux, compteurs), données denses, data-viz chiffrée, rythme en dessous de 2 s par plan, `abstrait` techno.

## Shorts de preuve (chemins)
- `out/shorts/aquarelle-conte__enfants__ou-vont-les-etoiles-le-jour/` : « Où vont les étoiles le jour ? », 15 s.
- `out/shorts/aquarelle-conte__histoire__phare-d-alexandrie/` : « Il était une fois le Phare d'Alexandrie », 16 s.

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)

> **Voix réellement utilisée pour tous les shorts : Fish Audio « Arnold »** (`d704cf8f1216490cbfbed89955f0e938`, modèle `s2.1-pro`, conteur masculin FR). Les noms de voix Gemini (Orus, Kore, Aoede…) qui suivent sont des suggestions historiques de casting par ton : Gemini a été abandonné (quota). Le placement, le débit et les silences décrits ici restent valables.

- Voix : Gemini **Aoede** (conteuse), douce, avec un sourire dans la voix. Débit ≤ 2,6 mots/s, en pratique 2,3–2,6.
- La voix parle en continu avec des respirations de 0,1 s entre les lignes. Elle commence à 0,3 s et s'arrête avant le `fondu-papier`.
- Le visuel laisse libre tout ce qui n'est pas écrit : l'écran ne porte qu'un mot-clé et une phrase courte, la voix raconte le reste (par exemple Ptolémée ou les 100–130 m sont dits ou montrés, pas les deux).
- La musique est déjà à −18 dB. Avec `--voice`, `assemble.py` la duck automatiquement.

## Risques et limites
- **Coût de rendu** : ≈ 1,2 s/frame avec 4 rendus concurrents, dominé par la capture Chromium d'un canvas plein cadre et par le grain/blend CSS. Compter environ 9 min pour 15 s en période chargée.
- **Grands polygones déformés** : la variance est proportionnelle à la longueur du segment, d'où des « montagnes ». Utiliser `band()` et des points tous les 90 px.
- **Grands clips de lavis** (rayon > 1000 px) : on voit des arêtes droites. Utiliser un blob à 24 points et 4 niveaux, et `bloomSoft`.
- **Calques parallaxe** : largeur ≥ 1080 + décalage max + 20 px (un échec réel a découvert une bande de 15 px).
- Le style se prête mal aux contenus rapides ou chiffrés. Les faits historiques doivent être formulés prudemment (« vers », « environ »).
- Les blocs sont stylisés : ils évoquent le phare (3 étages) sans prétendre à l'exactitude archéologique.
