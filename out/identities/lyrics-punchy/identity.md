# Lyrics punchy — identité visuelle

## Nom
**Lyrics punchy** (`lyrics-punchy`) — vidéo de paroles verticale où **les paroles sont la vedette** : une colonne de texte justifiée par l'axe de largeur d'une police variable, qui s'empile en mur au fil de la chanson, ponctuée de petits cartons illustrés. Première identité de la famille de contenus `paroles`. Concept, chaîne et storyboard du directeur artistique : `out/report/notes/lyrics-punchy/`.

## Promesse en une phrase
« Chaque mot chanté tombe pile sur le temps et remplit exactement la colonne, les lignes lues s'empilent en camaïeu, et un carton dessiné illustre le mot qui compte : on lit la chanson d'un coup d'œil, même sans le son. »

## Mood & références de genre
Lyric video typographique de 2020–2026 (vidéos de paroles cinétiques, cartons de TikTok « lyrics »), affiche de concert sérigraphiée en aplats, typographie variable « élastique ». Le ton est **sec et rythmé** : le texte claque sur les temps, rien ne flotte. Public 13–30 ans, écoute au casque ou sans le son. Références de genre seulement : aucune pochette, aucun logo, aucune mascotte.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
Trois **camaïeux**, un par section de la chanson ; les trois fonds ont une luminance voisine (changer de camaïeu n'est pas un flash). Contrastes calculés sur le fond.

| Rôle | `nuit` (refrain, titre) | `lagon` (couplet) | `braise` (tension) |
|---|---|---|---|
| Fond | `#2A1160` | `#063F4A` | `#5E0F2C` |
| Mur 1 (ligne la plus récente) | `#B9A4F5` 7,2:1 | `#8FD9DC` 7,2:1 | `#F2A5B5` 6,9:1 |
| Mur 2 | `#8468DB` 3,7:1 | `#4FA9B0` 4,2:1 | `#D0708A` 4,0:1 |
| Mur 3 (décoratif, déjà lu) | `#5F45B8` 2,3:1 | `#2F8791` 2,8:1 | `#A64A66` 2,4:1 |
| Accent (mot du moment, carton, compteur) | `#E6FF4F` 13,9:1 | `#FF8A5C` 5,0:1 | `#FFD166` 9,2:1 |
| Encre (pictogrammes, pastilles) | `#140A33` | `#04252C` | `#33061A` |

- Texte vif : crème `#FFF6E5` (14,5 / 10,8 / 12,4:1).
- **Couleurs vraies**, une seule à la fois, dans un carton : rouge `#FF3B3B`, vert `#3DDC84`, bleu drapeau `#1F3FBF`, blanc cassé `#F4F1EA`, rouge drapeau `#E1262D`.
- Mur 2 (3,7–4,2:1) n'est lisible que parce que le texte du mur fait ≥ 56 px en graisse 800 ; mur 3 ne porte rien à lire.
- Jamais : noir pur, dégradé, flou, ombre portée, texture.

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
Une seule famille : **Anybody** (Etcetera Type Co, SIL OFL 1.1), paquet npm **`@fontsource-variable/anybody` 5.3.0** épinglé, fichier `standard.css` (famille CSS `Anybody Variable`, axes `wdth` 50–150 et `wght` 100–900 ; le moteur vérifie au démarrage que l'axe de largeur répond). Tout en capitales, accents conservés, interlettrage 0, `white-space: nowrap`.

| Rôle | Graisse | Largeur (`wdth`) | Taille |
|---|---|---|---|
| Ligne en cours (rang) | 900 | 50–150, calculée | 120 à 250 px, calculée |
| Mur | 800 | 50–150, calculée | 56 à 118 px, calculée |
| Texte dans un carton | 900 | 78 | ≥ 58 px à l'échelle du carton |

**Ajustement d'un rang** (signature) : taille = taille maxi × 876 / largeur à `wdth` 100, bornée ; puis on cherche le `wdth` qui donne exactement 876 px ; trop large à `wdth` 50 : on réduit la taille ; trop court à `wdth` 150 : le rang reste aligné à gauche (« 2.0 »). Un mot court devient large et bas, un groupe long étroit et haut.

### Langue des paroles (règle d'Hamdi, 19/11/2026)
Les paroles s'affichent **toujours dans la langue du morceau, jamais traduites** : anglais à l'écran pour un morceau en anglais, français pour un morceau en français, arabe pour un morceau en arabe. Le texte de remplissage en français des images du concept n'était qu'un exemple ; le jeu de remplissage du dépôt est écrit dans la langue du morceau test (anglais). `lyrics.json` porte la langue (`langue`).
- **Écritures latines** (anglais, français…) : Anybody, en capitales, comme ci-dessus.
- **Arabe** : Anybody ne couvre pas l'arabe. Police : **Noto Sans Arabic** (Google, SIL OFL 1.1), paquet npm **`@fontsource-variable/noto-sans-arabic` 5.3.0** à épingler, fichier `standard.css` (axes `wdth` 62,5–100 et `wght` 100–900 : la colonne se justifie encore par l'axe de largeur, sur une plage plus étroite, puis par la taille). Graisses : 800 pour la ligne en cours, 700 pour le mur. Pas de capitales en arabe (l'écriture n'a pas de casse) ; ligatures et formes contextuelles laissées au moteur de texte, jamais de lettres isolées.
- **Sens d'écriture arabe** : de droite à gauche (`direction: rtl`, `lang="ar"`). La colonne s'aligne sur son bord droit (x 940) ; dans un rang, les unités se posent de droite à gauche ; un rang trop court à `wdth` 100 reste aligné à droite. Le mur, les cartons et le compteur ne changent pas de place ; les chiffres (« 2.0 ») restent en chiffres occidentaux, de gauche à droite dans le flux bidirectionnel.
- **État v1** : le moteur rend les écritures latines ; le mode arabe (police, `rtl`, alignement à droite) est spécifié ici mais pas encore codé ni essayé.

## Formes & matières
- Aplats nets, aucun relief. La seule forme hors texte est le **carton** : carré couleur d'accent de 440 px aux coins arrondis (36 px), posé de travers (±4° en alternance), qui porte un pictogramme en 3 couleurs (encre, crème, une couleur vraie), dessiné en SVG par code.
- **Compteur de temps** : 4 points de 26 px en haut à gauche (centres de (77, 262) à (197, 262)), le temps de la mesure en cours en couleur d'accent, les autres en mur 3.
- Pas de grille visible, pas de cadre, pas de sticker rond, pas de rubalise (ce qui sépare de `brut-meme`).

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
Tout est une fonction du temps `t` et de `lyrics.json` (aucun état, aucune timeline). Durées en images à 30 i/s ; chaque unité entre **2 images avant** l'instant chanté.

| Nom | Quand | Mouvement |
|---|---|---|
| `pose` | unité d'accent 0 (contretemps) | opacité 0→1 et échelle 0,9→1 en 2 images |
| `claque` | accent 1 (sur un temps) | échelle 1,3→1 en 3 images, `wdth` +40 % → valeur calculée en 5 images, courbe (1−k)³ |
| `coup` | accent 2 (premier temps de mesure ou mot déclencheur), un par mesure au plus | échelle 1,7→1 en 4 images, puis toute la colonne descend de 12 px et revient en 5 images |
| respiration | chaque temps | la ligne en cours passe à 1,02 **en hauteur** puis revient en 4 images ; le mur ne bouge pas |
| mot du moment | durée de l'unité | couleur d'accent, puis crème quand l'unité suivante arrive |
| `empilement` | première unité de la ligne suivante | la ligne finie se recompose sur un rang (800) et glisse en bas du mur en 6 images ; les autres montent d'un cran et perdent un ton ; la 5e disparaît en 4 images |
| sortie de carton | sur un temps | échelle 1→0 en 3 images ; le dernier carton du short est tenu jusqu'à la fin |

Jamais : lettre par lettre, fondu long, rotation continue, zoom de caméra, tremblement de plus de 12 px, deux `coup` dans la même mesure. Le mot qui arrive en `claque` / `coup` est volontairement trop large pendant 3 à 5 images : il déborde de la colonne le temps de se resserrer (mesuré : 31 images sur 585 dans le short de preuve, toutes à l'entrée d'un mot).

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
Aucune caméra : plan 2D frontal fixe. Seuls la colonne de texte (`coup`, `empilement`, `chute-de-pile`) et le carton bougent. Pas de zoom, pas de panoramique, pas de punch-in.

## Transitions (liste nommée, durée, quand les utiliser)
- **`chute-de-pile`** (transition signature, 0,33 s) : au changement de section, posée sur le temps qui précède le premier mot ; les lignes du mur et la ligne en cours tombent sous le cadre, une image d'écart entre elles, pendant que le fond passe au nouveau camaïeu en 10 images. Au moins 1,6 s entre deux (photosensibilité).
- **`empilement`** (0,2 s) : entre deux lignes d'une même section.
- Pas de fondu au noir, pas de coupe franche du fond.

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
- **0–0,5 s (accroche)** : la première unité est déjà en `coup` à l'image 0. Si le morceau commence sans voix, le **titre** occupe le passage, un mot par mesure en `coup`.
- **Développement** : une section = un camaïeu ; 1 ligne chantée = 1 à 6 unités sur 1 à 3 rangs ; un carton au plus par ligne sur le mot qui compte.
- **Fin** : la dernière ligne vive et son carton tenus jusqu'à la dernière image ; pas de noir, pas de fondu. Durée conseillée 15–40 s ; la preuve fait 19,5 s.
- **Son** : la vidéo est rendue **muette** ; la chanson vient de la bibliothèque de l'appli à la publication, à partir de 0:00 (une piste silencieuse est posée pour `check.py`).

## Zones sûres
Plus strictes que le dépôt (légende et disque du son TikTok) : **haut 220 px, bas 360 px, droite 140 px, gauche 64 px**. Colonne de texte x 64–940 (876 px). Mur y 300–800 (4 lignes au plus, 26 px entre elles, empilées depuis le bas). Ligne en cours de y 850 à 1 500 au plus (34 px entre rangs). Carton centré (712, 476) ; **s'il couvrirait une ligne du mur encore lisible (tons 1–2), il remonte et rétrécit** (jusqu'à 340 px, cas de « version » dans la preuve : 421 px) ; sinon ces lignes passent au ton 3 pendant le carton. Contrôle image par image : `out/tools/lyrics_audit.mjs`.

## Librairies recommandées et pourquoi
- **DOM + police variable** (Chromium par `out/tools/render.mjs`) : seul moyen simple de piloter l'axe `wdth` en continu (`font-variation-settings`) et de mesurer la largeur exacte d'un texte ; le canvas 2D ne sait pas régler un axe variable.
- **SVG en ligne** pour les pictogrammes (`out/shared/lyrics-moteur/dessins.js`) : net à toutes les échelles, animable en fonction de `t`.
- **`out/tools/lyrics_align.py`** (bibliothèque standard, `difflib`) : paroles exactes + mots horodatés → `lyrics.json` (alignement, grille des temps, accents, unités, rangs, déclencheurs, densité) et validation des règles.
- **faster-whisper** (hors rendu, `uv run --with faster-whisper --with "av<16"`) : horodatage brouillon des mots. librosa ne s'installe pas sur le Mac de référence (llvmlite) ; le tempo se mesure à part.
- Moteur partagé : `out/shared/lyrics-moteur/` (`lyrics.js`, `dessins.js`, `triggers.json`). Un nouvel épisode = un nouveau `lyrics.json`, sans code.

## Familles de contenus adaptées / inadaptées
- **Adaptées** : **`paroles`** (nouvelle famille : vidéo de paroles d'une chanson, d'un refrain, d'un extrait de 15 à 40 s), slogans rythmés, poèmes scandés, punchlines sur un beat.
- **Inadaptées** : explicatif, histoire, géographie (pas de place pour un schéma), contenu sans rythme (le système vit de la grille des temps), rap très rapide au-delà de 5 mots/s (le regroupement par deux casse l'effet « mot par mot »), enfants (débit et ton).

## Shorts de preuve (chemins)
- `out/shorts/lyrics-punchy__paroles__claudes-plan/` — 19,5 s, 585 images, rendu 116,9 s (20,0 s / 100 images, charge moyenne 4,5–15). Rendu avec le jeu de **remplissage** (nos mots, **en anglais**, la langue du morceau test « Claude's Plan », calés sur ses horaires, 154,5 BPM) : les vraies paroles et l'audio ne sont pas dans le dépôt ; la version avec les paroles anglaises réelles est rendue hors dépôt (`~/git/StudioVisualIdentity-sources/lyrics-claudes-plan/`). Un seul short de preuve pour l'instant (voir Risques).

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)
**Pas de voix off.** La « voix » est la chanson, ajoutée dans l'appli à la publication. Le visuel porte tout le texte : il doit se lire sans le son (casque débranché), d'où les règles de lisibilité : une unité = un mot ou un petit groupe (les articles, prépositions et pronoms de 3 lettres ou moins se collent au mot suivant) ; jamais de lettre isolée ; ≥ 0,25 s par unité (au-delà de 4 unités/s on regroupe par deux) ; ≤ 6 unités et ≤ 3 rangs par ligne ; une ligne complète reste vive ≥ 0,4 s et ≥ 2 s dans le mur ; ≤ 6 unités vives + 4 lignes de mur à l'écran.

## Risques et limites
- **Droits** : l'audio et les paroles d'une chanson ne sont pas à nous. Ils restent hors du dépôt (`~/git/StudioVisualIdentity-sources/lyrics-<morceau>/`), la vidéo est publiée muette et le son vient de la bibliothèque de l'appli. Le dépôt ne garde que le moteur et un jeu de remplissage.
- **Paroles non confirmées** : l'horodatage vient de Whisper (±0,3 s, mots étalés sur les silences corrigés par la règle « > 0,8 s → début = fin − 0,3 s »). Toute correction se fait à la main dans `lyrics.json` après écoute des aperçus.
- **Confusion avec `brut-meme`** (la plus proche : texte qui claque sur le beat) : ne jamais passer au noir / jaune, ni à une police condensée fixe, ni remplacer le mot au lieu de l'empiler, ni zoomer la caméra.
- **Lignes longues** : au-delà de ~30 caractères, une ligne du mur descend à 56 px ; la couper à la préparation.
- **Carton sur le mur** : avec 3 ou 4 lignes lisibles dans le mur, le carton ne trouve plus de place au-dessus et les lignes passent au ton 3 pendant 4 temps (repli prévu, non rencontré dans la preuve).
- **v1 incomplète** : les types d'illustration `eclat` (sang, feu) et `fond` (drapeau plein cadre, mode plaque) et les dessins `fichier-md`, `mauvais-changement`, `ship`, `tour-eiffel`, `coeur`, `argent`, `nuit`, `telephone` sont décrits dans `triggers.json` mais pas encore dessinés (carton générique avec le mot en attendant). Les portraits de personnalités demandent une décision sur les images sous licence libre.
- **Un seul short de preuve** (le dépôt en demande 2–3) ; coût de rendu mesuré sous forte charge (≈ 30 s / 100 images, la capture d'écran domine).
- `render.mjs` sort du `yuvj420p` (entrée MJPEG) : le passage en `yuv420p` se fait au moment de poser la piste silencieuse.
