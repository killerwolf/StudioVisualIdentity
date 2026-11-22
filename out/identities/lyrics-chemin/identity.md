# Lyrics chemin — identité visuelle

## Nom
**Lyrics chemin** (`lyrics-chemin`) — vidéo de paroles verticale et muette où **les paroles s'écrivent à plat sur un plan d'architecte bleu posé au sol**, au moment où elles sont chantées, pendant qu'une caméra vue de dessus suit la pointe du tracé en un seul plan-séquence ; au refrain, un grand zoom arrière révèle que toutes les lignes dessinaient une image (ici, un bateau en papier). Deuxième identité de la famille de contenus `paroles`, conçue sans regarder `lyrics-punchy`. Concept, storyboard et maquette du directeur artistique : `out/report/notes/lyrics-chemin/`.

## Promesse en une phrase
« On suit la chanson du bout du crayon : chaque mot s'écrit en jaune à l'instant où il est chanté, la caméra file d'un trait à l'autre sur le plan, et à la fin on recule pour découvrir que les paroles dessinaient quelque chose. »

## Mood & références de genre
Plan d'architecte en cyanotype, table de travail vue de dessus (« flat lay » : tasse, crayon, clé, note collée), caméra « top shot » des génériques et des vidéos de dessin à main levée, plan-séquence qui suit une ligne (à la manière d'un tracé de métro animé). Le ton est **appliqué et complice** : un carnet de bord de la chanson, pas un clip qui claque. Public ados et adultes, écoute avec ou sans le son. Références de genre seulement : aucune pochette, aucun logo, aucune marque.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
Contrastes calculés sur le bleu de la feuille.

| Rôle | Couleur | Contraste |
|---|---|---|
| Fond (feuille cyanotype) | `#1B4C92`, dégradé `#2460AE` (haut gauche) → `#133A74` (bas droit), attaché à la feuille : la lumière tourne avec la caméra | — |
| Surface (sol, béton chaud moucheté) | `#CFC8BA` ; ombre de la feuille `rgba(4,14,40,0.45)` | — |
| Texte (encre sèche) | ivoire `#F3F0E4` ; 100 % à l'échelle 1, **60 % en gros plan** pour que le mot chanté domine | 7,4:1 (5,5 au plus clair, 9,8 au plus sombre) |
| Accent 1 (encre fraîche) | jaune `#FFD84A`, **réservé au mot chanté** ; sèche en ivoire en 0,35 s | 6,1:1 (4,5 au plus clair) |
| Accent 2 (crayon rouge) | `#FF7D5C` : croix, fanion, boucle de correction ; **jamais de texte** | 3,3:1 (décor) |
| Crayon (pré-posé) | ivoire à 50 % : unité posée d'avance, avant d'être « repassée à l'encre » | — |
| Objets posés | tasse `#EDE8DC` / café `#2E1B0E`, crayon `#F2C230`, clé `#C9A24A`, note `#F4E6A6`, ruban `#E9DFC3` | décor |

- Le **jaune ne sert qu'au mot chanté** : c'est le repère de lecture de tout le système.
- Quadrillage blanc 20 px (3,5 à 7 %) et 100 px (10 %), cadre fin, repère `PL. 01 — 1:1`, taches et fibres attachées au monde.
- Jamais : fond noir, néon, bloom, reflet de vitre, flash.

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
| Rôle | Police | Paquet | Taille |
|---|---|---|---|
| Paroles (ligne du dessin) | **Barlow Condensed 700**, capitales | `@fontsource/barlow-condensed` **5.3.0** (épinglé) | 36–60 px dans le monde (ajusté à l'arête) ; à l'écran, mot chanté **120–220 px** (titre 250) |
| Refrain écrit dans la mer | **Barlow Condensed 800** | idem | ≤ 88 px à l'échelle 1, **même corps pour tous les rangs**, rang ≤ 850 px (81,8 px sur la preuve ; 71,5 px avec les vraies paroles, dont le rang « AND THEY … » est plus long : sous les 78 px du concept) |
| Repères du plan (décor) | JetBrains Mono 400 | `@fontsource/jetbrains-mono` (déjà dans le dépôt) | 11–15 px dans le monde |

- **Ajustement à l'arête** : corps = clamp(longueur utile / largeur de la ligne à 1 em, bornes de l'arête), puis interlettrage de 0 à 0,15 em pour finir l'arête (latin seulement). Les mots sont posés **entiers et rigides** sur le chemin (tangente au centre du mot), jamais lettre par lettre.
- Le texte est posé **sur** son trait (0,16 em au-dessus) ; sur les ponts et les flancs, **sous** le trait (à l'extérieur de la coque).
- **Planchers à l'écran** (mot chanté) : 120 px ; 104 px si la ligne est un passage rapide (`minPx`) ; **92 px si tout le cadrage dépasse 4,5 mots/s** (ligne entière pré-posée, lisible avant d'être chantée). Plafond 220 px (titre 250).

### Langue des paroles (règle d'Hamdi, 19/11/2026)
Les paroles s'affichent **toujours dans la langue du morceau, jamais traduites** (anglais pour un morceau en anglais, etc.). Le fichier de paroles porte `langue` et `sens`.
- **Anglais** (preuve) : Barlow Condensed en capitales, comme ci-dessus.
- **Français** : même police (latin complet, accents sur capitales É, È, À, Ç) ; **0,12 em de plus au-dessus des lignes** pour que l'accent ne touche pas le trait voisin ; les élisions (« J'AI ») restent dans le mot.
- **Arabe (droite à gauche)** : police **Cairo** 700 (paroles) / 800 (refrain), `@fontsource/cairo` (SIL OFL 1.1, à épingler), sous-ensemble `arabic`, `ctx.direction = 'rtl'`. Pas de capitales, **jamais d'interlettrage** (l'ajustement se fait par le corps seul, 40–64 px dans le monde). Le dessin étant symétrique, il est **retourné en miroir** avant la mise en page (x → 1080 − x, angles opposés) : chaque arête se lit de droite à gauche, la caméra voyage en sens inverse, les virages changent de signe, les objets changent de côté. Un mot est toujours dessiné **entier** (la cursive ne se coupe pas) ; révélation par un masque qui avance de droite à gauche. Chiffres et sigles latins restent de gauche à droite dans leur mot.
- **État** : anglais rendu et vérifié ; français et arabe spécifiés, **pas codés** (le moteur ne fait encore ni le miroir ni la police Cairo).

### Règles de pré-pose (lisibilité d'un passage rapide)
Calcul par unité (`durée / nombre de mots`), sur la grille du morceau (1 temps = 60 / bpm).
1. **En direct** (défaut) : un mot s'écrit de gauche à droite à partir de 0,08 s avant son attaque, en `min(50 % de sa durée, 0,28 s)` ; jaune tant qu'il est chanté, puis sèche en ivoire.
2. **Pré-posé au crayon** : moins de **0,30 s par mot** (plus de 3,3 mots/s) → l'unité est posée d'avance en ivoire à 50 %, d'un geste de 0,15 s, **un temps avant son attaque** ou dès que la caméra arrive si c'est plus tard ; à l'attaque elle passe au jaune d'un coup (« repassée à l'encre »). Le direct reste le changement de couleur, calé sur la voix.
3. **Ligne entière pré-posée** : au-delà de **4,5 mots/s** sur tout un cadrage, le groupe est posé à l'arrivée de la caméra, seul le repassage suit la voix ; plancher de corps 92 px.
4. La règle « ne pas quitter un mot avant 60 % de sa durée » passe avant l'avance du pré-posé : sans marge, le groupe apparaît à l'arrivée de la caméra.

## Formes & matières
- **Feuille dépliée** : un pli vertical et trois horizontaux, dessinés en **arête nette à largeur constante à l'écran** (1,5 px clair / 1,5 px sombre, halo de 10 px) ; chaque panneau prend la lumière un peu différemment (± 2 à 3 %), ce qui fait la cassure de lumière sans larges bandes en gros plan.
- **Traits du dessin** : 3,2 px dans le monde, ivoire ; le mât en pointillé (pli) ; les vagues en sinusoïde.
- **Repères d'architecte** autour du titre (cote avec sa longueur en JetBrains Mono, croix de repère, ligne de construction pointillée tirée par la pointe) : ils donnent la matière « plan » dès l'image 0.
- **Objets posés**, seuls à avoir une épaisseur (ombre attachée à la lumière du monde, multipliée par le zoom) : tasse et auréole sèche (bord éclairé, paroi intérieure, ménisque, bulles, reflet de fenêtre), crayon (trois facettes, cône de bois veiné, mine, virole cannelée, gomme), clé en laiton (dégradé, biseau, dents), note collée (coin relevé, trois traits au stylo, ruban), ruban de masquage translucide aux bouts déchirés aux quatre coins. Dessinés par code, à plat, **aucun mot dessus**.
- **Pointe** : un point jaune lumineux (0,11 em) qui écrit.
- Finition écran : vignette douce et grain fixe très léger.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
Tout est une fonction de `t` et du fichier de paroles (aucun état). Unité de temps : le temps du morceau (0,388 s à 154,5 BPM).

| Nom | Quand | Mouvement |
|---|---|---|
| écriture | mot en direct | révélation gauche → droite en `min(50 %, 0,28 s)` dès 0,08 s avant l'attaque ; la pointe suit |
| pré-pose | unité < 0,30 s/mot | ivoire 50 % en 0,15 s, un temps avant ; jaune d'un coup à l'attaque |
| séchage | 0,10 s après la fin du mot | jaune → ivoire en 0,35 s |
| trait | pendant l'écriture | 0,3 em devant la pointe ; fini jusqu'au sommet en 0,35 s après le dernier mot (emmène l'œil) |
| annotation | sur un mot | croix, fanion ou boucle au crayon rouge, tracés en 0,3 à 0,7 s |

Jamais : lettre isolée qui saute, rebond, échelle du texte qui pulse, fondu au noir, deux grandes rotations de suite (> 90°), rotation résiduelle du texte à l'écran au-delà de 6°.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
Caméra **verticale, sans perspective** (translation, rotation, échelle ×1 à ×6,1). Le point de lecture est (512, 860), au centre de la bande x 64–960.

| Mouvement | Durée | Courbe | Détail |
|---|---|---|---|
| **cadrage** (repos) | ≥ 0,5 s | — | groupe de mots centré, ≤ 780 px de large ; poussée de 3 % et dérive dans le sens de l'écriture (≤ 8 % du groupe, ≤ 40 px/s) |
| **glissé** | 0,12–0,26 s | `cubic-bezier(.3,0,.15,1)` | d'un cadrage au suivant sur la même ligne ; part après 60 % du mot en cours |
| **virage** | 1,3–3 temps | `cubic-bezier(.5,0,.3,1)` | la caméra pivote autour du sommet ; creux de zoom de 30 % ; **3 temps pour un virage en épingle** (> 90°) |
| **fouetté** | 0,6–1 temps | `cubic-bezier(.7,0,.2,1)` | la ligne suivante est ailleurs ; creux de zoom de 28 % ; flou de mouvement |
| **respiration** | 4 temps | sinus | après une phrase isolée : recul à ×2,3, on devine le dessin sans le voir |
| **zoom arrière** | 4 temps (1 mesure) | échelle `cubic-bezier(.5,0,.12,1)` en log, position `cubic-bezier(.3,0,.1,1)` | de ×5,5 à ×1, rotation ramenée à 0°, puis recul lent à ×0,955 |

- **Inclinaison** : la caméra tourne avec la ligne mais laisse à l'écran un dixième de son angle (6° au plus).
- **Flou de mouvement** réel : obturateur 180° (1/60 s), sous-images au pas de 3 px du point le plus rapide de l'écran (coins compris, rotation comprise), 64 au plus — au-delà on raccourcit l'obturateur plutôt que d'espacer les copies —, moyenne en flottants (aucune strie).
- Mesuré sur la preuve (`chemin_audit.mjs`) : virage en épingle 114° en 3 temps, rotation de pointe 249°/s ; fouettés jusqu'à 698°/s (couverts par le flou) ; vitesse au repos ≤ 40 px/s.

## Transitions (liste nommée, durée, quand les utiliser)
- **`virage`** (signature, 1,3–3 temps) : la ligne suivante part du sommet où l'on est ; on voit un instant les deux pentes.
- **`fouette`** (1 temps) : saut d'un bout du dessin à l'autre, posé sur un temps, arrivée un demi-temps avant l'attaque.
- **`glisse`** (0,12–0,26 s) : dans une même ligne.
- **`respiration`** (4 temps) : dans un long silence des paroles.
- **`zoom-arriere`** (1 mesure, une seule fois) : la révélation de l'image entière, au refrain.
- Pas de coupe, pas de fondu : un seul plan-séquence du début à la fin.

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
- **0–0,3 s (accroche)** : très gros plan sur le premier mot du titre, déjà en train de s'écrire à l'image 0 (pointe jaune visible), entouré des repères d'architecte (cote, croix, ligne de construction) : on sait tout de suite qu'on est sur un plan.
- **Développement** : une ligne chantée = une arête du dessin ; 1 à 3 cadrages par ligne ; virage quand la ligne suivante part du même sommet, fouetté sinon ; un objet posé croisé en route sur les lignes qui en parlent ; annotations rouges sur 2 ou 3 mots.
- **Respiration** au premier long silence : recul qui laisse deviner le dessin.
- **Chute** : au refrain, **zoom arrière d'une mesure** ; le refrain s'écrit en grand dans la mer pendant qu'on découvre l'image.
- **Fin** : l'image d'ensemble tenue ≥ 1,5 s, le dernier mot du refrain encore jaune ; pas de noir. Durée conseillée : jusqu'au premier refrain (20–40 s) ; la preuve fait 32,6 s.
- **Son** : vidéo rendue **muette** ; la chanson vient de la bibliothèque de l'appli à la publication, depuis 0:00 (piste silencieuse posée pour `check.py`).

## Zones sûres
Haut 220 px, bas 320 px, droite 120 px, gauche 64 px. Le **mot chanté** reste entièrement dans x 64–960, y 220–1600 de son attaque à 60 % de sa durée (ensuite la caméra peut partir) ; corps à l'écran 120–220 px (planchers 104 / 92 ci-dessus). Image finale : rien d'utile dans les 220 px du haut, les 320 px du bas, les 120 px de droite (la note collée et les filets d'eau, décor, peuvent y entrer). Contrôle sans rendu, image par image : `node out/tools/chemin_audit.mjs <scene.html> [--query data=…]` (zones sûres, corps, cadrages ≥ 0,5 s, départ après 60 %, vitesse au repos, chevauchements dans l'image finale ; sortie 1 si une règle échoue).

## Librairies recommandées et pourquoi
- **Canvas 2D** (Chromium par `out/tools/render.mjs`, contrat `window.ready` / `window.renderAt(t)`) : texte vectoriel net à tout zoom (×1 à ×6) sans texture géante, `ctx.letterSpacing`, mise en forme arabe faite par le navigateur ; une caméra 2D (translation, rotation, échelle) suffit puisque tout est à plat.
- Écartés : three.js / Babylon (texte en texture, flou en gros plan), SVG + GSAP (flou de mouvement par sous-images trop cher), Godot (sortirait du pipeline `renderAt`).
- **Moteur partagé** : `out/shared/chemin-moteur/chemin.js` + `dessins/<id>.json` (sommets, arêtes, côté du texte, marges, bornes de corps, objets, mer). Un épisode = un fichier de paroles (lignes → arêtes, unités `[texte, début, fin]`, cadrages, transitions en temps, annotations, refrain) ; un nouveau dessin = un nouveau JSON (et, s'il a d'autres objets, leur dessin dans le moteur).
- **`out/tools/chemin_audit.mjs`** : contrôle des règles de lisibilité et du confort de caméra, sans rendre d'image.
- Les horaires des mots viennent de la même chaîne que `lyrics-punchy` (faster-whisper puis correction à la main) ; `lyrics_align.py` peut préparer les unités.

## Familles de contenus adaptées / inadaptées
- **Adaptées** : **`paroles`** (extrait de chanson jusqu'au premier refrain, 20–40 s), chanson dont le refrain porte une image (bateau, maison, cœur, fusée…), comptine, poème récité dont les vers peuvent dessiner une forme (calligramme animé).
- **Inadaptées** : rap très rapide sur toute la durée (au-delà de 4,5 mots/s le système ne fait plus que du pré-posé), chanson longue sans répétition (le dessin manque d'arêtes), explicatif ou histoire (pas de place pour une donnée), contenu sans image finale à révéler.

## Shorts de preuve (chemins)
- `out/shorts/lyrics-chemin__paroles__claudes-plan/` — 32,6 s, 979 images, plan-séquence complet jusqu'au zoom arrière et au bateau. Rendu avec le jeu de **remplissage** (« Monday's draft », nos mots, **en anglais**, la langue du morceau test « Claude's Plan », calés sur ses horaires, 154,5 BPM) : les vraies paroles et l'audio ne sont pas dans le dépôt ; la version avec les paroles réelles est rendue hors dépôt (`~/git/StudioVisualIdentity-sources/lyrics-claudes-plan/`). Rendu 2 033,6 s (207,7 s / 100 images) en parallèle de la version aux vraies paroles et sous forte charge ; 10 premières secondes rendues seules : 138 s / 100 images. Le flou de mouvement domine.
- `out/shorts/lyrics-chemin__paroles__i-fold-elevenlabs/` et `out/shorts/lyrics-chemin__paroles__i-fold-lyria/` (« I Fold », 22/11/2026) — la même chanson de remplissage « Monday's Draft », cette fois **chantée** : le texte de claudes-plan a été mis en musique par deux générateurs, **ElevenLabs Music** (28,8 s, 152 BPM) et **Google Lyria 3.5** (22,1 s, 155 BPM, appelé par treg). Même bateau, même habillage `plan-bleu`, même scène ; seuls les temps changent. Les mots chantés sont horodatés par faster-whisper (trois passes), puis `src/refaire.sh` et `outils/gen_chemin.py` (dans le `src/` de la version ElevenLabs) recalculent `chemin.json` à partir du remplissage. **Ces deux vidéos ne sont pas muettes** : la chanson est dans `short.mp4` (−14 LUFS) ; les mp3 restent hors dépôt et suivent les conditions des fournisseurs (`LICENSE-CONTENT.md`). Aucun format ne décrit une vidéo de paroles chantée : elles déclarent `paroles-muet` (durée, règles), l'écart est écrit dans `short.json` (`formatEcart`). `chemin_audit.mjs` relève 3 (ElevenLabs) et 8 (Lyria) cadrages tenus moins de 0,5 s : le chant est plus serré que le morceau test, laissés tels quels. Le morceau de Lyria, plus court, ne laisse qu'une mesure de 4 temps au zoom arrière (8 chez ElevenLabs).

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)
**Pas de voix off.** La « voix » est la chanson, ajoutée dans l'appli à la publication (sauf les deux versions « I Fold », où une chanson générée sur nos paroles de remplissage est incluse dans la vidéo). Le visuel porte tout le texte et se lit sans le son : jamais plus de deux ou trois mots chantés à l'écran à la fois, le mot chanté seul en jaune, l'encre sèche atténuée en gros plan, planchers de corps, pré-pose dès 3,3 mots/s.

## Risques et limites
- **Droits** : l'audio et les paroles d'une chanson ne sont pas à nous. Ils restent hors du dépôt, la vidéo est publiée muette ; le dépôt ne garde que le moteur et un jeu de remplissage. Exception « I Fold » : les paroles sont les nôtres (remplissage) et la musique est générée par IA (ElevenLabs Music, Google Lyria 3.5) ; la vidéo la contient, sous les conditions de ces fournisseurs.
- **Un dessin par chanson** : placer les lignes sur les arêtes (ordre, côtés, marges) se fait à la main ; une chanson plus longue ou plus bavarde demande un autre dessin ou des arêtes en plus (vagues, nuages, sillage). Le bas de la feuille reste peu rempli si l'extrait s'arrête au premier refrain.
- **Corps dans l'image finale** : 36–60 px pour les lignes du bateau, sous la règle « 54 px » du dépôt ; voulu (déjà lues en gros plan), à faire valider.
- **Confort** : les fouettés tournent vite (jusqu'à ~700°/s de pointe sur un temps) ; le flou les rend lisibles comme des « whip pans », mais deux fouettés rapprochés fatiguent. Ne jamais enchaîner deux rotations de plus de 90°.
- **Coût** : le flou de mouvement en flottants multiplie le coût des images en mouvement (jusqu'à 64 sous-images) ; mesuré dans `short.json`.
- **Voisinage** : fond bleu et objets à plat ; aucune identité existante n'a de caméra vue de dessus, mais `topo-relief` / `atlas-grave` (cartes, plans) en sont les plus proches par la matière ; pas de test de reconnaissance fait.
- **Langues** : français et arabe spécifiés, non codés.
- **Paroles non confirmées** : au-delà de 19,5 s, les horaires viennent d'une transcription automatique non corrigée à l'oreille (refrain de 29,2 à 32,1 s compris).
- `render.mjs` sort du `yuvj420p` (entrée MJPEG) : le passage en `yuv420p` se fait au moment de poser la piste silencieuse ; `check.py` admet jusqu'à 60 s pour la famille `paroles`.

## Annexe — Lyrics chemin dans le modèle en briques (2026-11-20)
Depuis le 20/11/2026 (choix 118, options 124 et 125 ; `out/report/notes/composition/proposition.md`), le catalogue se lit aussi en **briques** : vidéo = habillage × mécanique × format (+ son), une combinaison nommée = une **recette**. Lyrics chemin est la recette `lyrics-chemin` (`out/recettes/lyrics-chemin.json`) : habillage **`plan-bleu`** (`out/habillages/plan-bleu/habillage.json`) × mécanique **`trace-chemin`** (`out/mecaniques/trace-chemin/mecanique.json`, la seule mécanique exécutable avec `pop-papier-12ips` : un habillage = un fichier `out/shared/chemin-moteur/habillages/<id>.js`) × format `paroles-muet`. Ce document décrit l'ensemble ; la signature est partagée : feuille de plan bleu, encre jaune réservée et Barlow Condensed pour l'habillage ; plan-séquence de dessus, mot posé sur le trait, fouettés et zoom arrière final pour la mécanique.

Les autres recettes de la même mécanique (même moteur, autre habillage) : `chemin-editeur` (éditeur de code, `paroles-muet`), `chemin-ardoise` (famille d'habillage `craie`, variante `ardoise`, `narre-long`), `chemin-portulan` (`narre-long`), `chemin-craie-verte` (essai C1 : `craie/tableau-vert`) et `chemin-grille-suisse` (recette adoptée « Données qui se tracent », `narre-court`, d'après l'essai C2). Mesure à deux étages (`out/report/recognition-briques.json`, 20/11/2026) : `trace-chemin` est retrouvée sous un autre habillage par 5 de ses 6 shorts (le quatre-quarts à l'ardoise a pour voisin une simulation de pixel-arcade, la recette du chemin arrive 2ᵉ) ; l'habillage `plan-bleu` n'a qu'un short dans le catalogue (le short C4, abandonné, est exclu), il n'a donc pas encore de pair mesurable.

Nouvelle recette sur ce mouvement (une autre pâte sur le chemin) : `/fabrique-identites recette <habillage> trace-chemin` (`.claude/skills/fabrique-identites/SKILL.md`). Les règles de la recette `paroles` (`recipes/paroles.md`) valent pour toute recette de `trace-chemin` au format `paroles-muet` ; pour un format narré (`narre-court`, `narre-long`), le texte de la voix est la route : voir `out/report/notes/lyrics-chemin/declinaisons/` et l'essai C2 (`out/report/notes/composition/essais.md`).
