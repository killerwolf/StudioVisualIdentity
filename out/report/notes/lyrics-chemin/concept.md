# Lyrics chemin — concept (second essai de vidéo de paroles, 2026-11-19)

Statut : **proposition de direction artistique**, pas encore une identité. Conçue sans lire ni regarder `lyrics-punchy`
(demande du propriétaire : un second essai non influencé). Images : `images/` ; maquette qui les a produites : `proto/scene.html`.

## L'idée en trois lignes

1. Les paroles s'écrivent **à plat sur un plan d'architecte posé au sol**, au moment où elles sont chantées ; chaque ligne de la
   chanson est un trait du dessin.
2. La caméra, à la verticale et en gros plan, **suit la pointe du tracé** d'une ligne à l'autre en un seul plan-séquence
   (glissés, virages, fouettés calés sur le tempo) ; on ne voit jamais plus de deux ou trois mots à la fois.
3. Au refrain final, **grand zoom arrière** : tout le texte dessinait un bateau en papier, sur une feuille bleue tenue au sol par
   quatre bouts de ruban, avec une tasse, un crayon, une clé et une note posés dessus.

## Pourquoi un bateau en papier

Le morceau test raconte une journée de développeur avec un assistant de code : on commence en « mode plan », on écrit des lignes,
le serveur tombe, on empile les clés et les fichiers de notes, on accumule les mauvais changements… et à la fin, quand même, on
livre. En anglais, livrer se dit *to ship*. Trois options ont été pesées :

| Option | Dessin final | Pour | Contre |
|---|---|---|---|
| A | **Bateau en papier** vu de face, sur des vagues | Jeu de mots direct avec le refrain (*ship*) ; dessin fait de **segments droits**, donc chaque ligne de paroles tient sur une arête ; symétrique, donc se retourne tel quel pour l'arabe ; un bateau plié dans une feuille, c'est le plan lui-même qui prend la mer | Dessin simple, presque enfantin : il faut une exécution soignée pour qu'il ne fasse pas « clipart » |
| B | **Fusée** sur son pas de tir | « Lancer », « version 2.0 » | Cliché des start-up ; silhouette étroite et haute, lignes trop courtes ; rien à voir avec le refrain |
| C | **Organigramme / plan de métro** de la journée | Colle au « mode plan » | Pas d'image à découvrir au zoom arrière : un schéma reste un schéma, la surprise est faible |

**Choix : A, le bateau en papier.** La chanson dit trois fois la même chose à trois échelles, et le dessin aussi :
le support est un **plan** (le titre), les traits du plan sont des **lignes écrites** (le couplet), et le plan dessine un
**bateau** (le refrain). Le découpage raconte l'histoire :

| Partie du dessin | Moment de la chanson (thème, pas les paroles) | Sens |
|---|---|---|
| Nom du bateau, peint sur la coque | Titre | On l'a sous les yeux dès la première image sans savoir que c'est une coque |
| Voile, pente montante | Le début de journée | On monte |
| Voile, pente descendante | Les lignes qu'on écrit | Virage en épingle au sommet |
| Pont droit (sous le trait) | « Depuis la version… » | On file vers la pointe droite |
| Flanc gauche de la coque, qui descend | La panne | La ligne qui parle de chute descend ; croix au crayon rouge |
| Quille | Les clés | Une vraie clé est posée à côté |
| Flanc droit, qui remonte | Encore un fichier de notes | Une note collée au ruban au bout |
| Fanion au sommet du mât | La petite relance isolée (« mais quand même ») | L'espoir tient dans un drapeau rouge ; c'est là que la caméra respire |
| Pont gauche (sous le trait), entouré au crayon rouge | Le mauvais changement | Corrigé comme une copie |
| Première vague sous la quille | « Beaucoup de mauvais changements » | La mer sur laquelle le bateau flotte, ce sont eux |
| Mer, en très grand | Le refrain répété | Seul texte lisible à l'échelle de l'image finale : il est chanté pendant qu'on la découvre |

Dans le dépôt, tout est montré avec des **paroles de remplissage inventées** (une chanson de bateau en papier, « Monday's draft »),
calées sur les temps réels du morceau. Paroles et audio réels restent hors dépôt.

## Surface, lumière, effet « à plat vu de dessus »

- **Feuille** : papier de plan cyanotype, bleu `#1B4C92` (dégradé `#2460AE` en haut à gauche vers `#133A74` en bas à droite :
  c'est la lumière, attachée à la feuille, donc elle tourne avec la caméra). Quadrillage blanc 20 px (3,5 à 7 %) et 100 px (10 %),
  cadre fin, repère `PL. 01 — 1:1`, taches et fibres de papier attachées au monde.
- **Plis** : la feuille a été dépliée (un pli vertical, trois horizontaux, un liseré clair et un liseré sombre). C'est ce qui dit
  « papier posé », plus que n'importe quelle texture.
- **Sol** : béton clair chaud `#CFC8BA` moucheté, visible seulement au bord pendant le voyage, puis tout autour à la fin.
  Ombre portée de la feuille (décalage 12/18 px, flou 26 px).
- **Objets posés** (les seules choses qui ont une ombre, donc une épaisseur) : tasse de café vue de dessus et son auréole, crayon
  jaune, clé en laiton, note jaune pâle tenue par un ruban, ruban de masquage aux quatre coins. Dessinés par code, à plat, sans
  contour, 3 à 4 tons chacun. Aucun mot dessus. L'ombre suit la lumière du monde, pas l'écran.
- **Encre** : ivoire `#F3F0E4` (contraste calculé 7,4:1 sur le bleu moyen, 5,5:1 sur la zone la plus claire, 9,8:1 sur la plus
  sombre), **encre fraîche** jaune `#FFD84A` pour le mot chanté (6,1:1 ; 4,5:1 au plus clair), **crayon rouge** `#FF7D5C` pour les
  annotations (fanion, boucle, croix ; 3,3:1, décor seulement, jamais de texte en rouge).
- **Finition écran** : vignette douce et grain fixe très léger. Pas de bloom, pas de reflets.

## Typographie (libre de droits)

| Rôle | Police | Licence | Paquet |
|---|---|---|---|
| Paroles | **Barlow Condensed Bold (700)**, capitales | SIL OFL 1.1 | `@fontsource/barlow-condensed` 5.3.0 (ajouté à `package.json`, version exacte) |
| Refrain en grand (la mer) | **Barlow Condensed ExtraBold (800)** | idem | idem |
| Repères du plan | JetBrains Mono 400 | SIL OFL 1.1 | déjà dans le dépôt |
| Arabe | **Cairo Bold / ExtraBold** | SIL OFL 1.1 | `@fontsource/cairo` (à ajouter au moment de coder l'arabe) |

Barlow Condensed : étroite (une ligne de 27 signes tient sur une arête de 450 px), formes de signalétique technique qui vont au
plan, accents français complets. Tailles :

- **Dans le dessin** (repère de l'image finale) : chaque ligne est ajustée à son arête, corps entre **36 et 54 px**, interlettrage
  de 0 à 0,15 em pour finir l'arête (jamais d'interlettrage en arabe). Le titre fait 54 px, le refrain 78 à 88 px.
- **À l'écran pendant le chant** : le zoom est choisi pour que le corps du mot chanté fasse **entre 120 et 220 px** (hauteur de
  capitale 84 à 154 px). Le titre monte à 250 px.
- Le texte est posé **sur** son trait (0,16 em au-dessus) ; sur les deux ponts, **sous** le trait, pour ne pas heurter la voile ;
  sur les deux flancs, à l'extérieur de la coque.

## Palette (rôles)

| Rôle | Couleur |
|---|---|
| Fond (feuille) | `#1B4C92`, haut `#2460AE`, bas `#133A74` |
| Encre sèche | `#F3F0E4` (à 60 % d'opacité en gros plan, 100 % à l'échelle 1) |
| Encre fraîche, mot chanté | `#FFD84A` |
| Annotation | `#FF7D5C` |
| Sol | `#CFC8BA` |
| Objets | tasse `#EDE8DC` / café `#2E1B0E`, crayon `#F2C230`, clé `#C9A24A`, note `#F4E6A6`, ruban `#E9DFC3` |

## Le tracé : ce qui s'écrit en direct, ce qui est pré-posé

Rien n'est tracé d'avance. Le trait du chemin et les mots avancent avec la **pointe** (un point jaune lumineux, 0,11 em).

- **En direct** (règle par défaut) : un mot s'écrit de gauche à droite à partir de 0,08 s avant son attaque, en
  `min(50 % de sa durée, 0,28 s)`. Il reste jaune tant qu'il est chanté, puis sèche en ivoire en 0,35 s.
- **Pré-posé au crayon** : quand le débit dépasse **3,3 mots par seconde**, c'est-à-dire **moins de 0,30 s par mot** (à 154,5 BPM :
  plus vite que trois quarts de temps par mot), l'unité est posée d'avance en ivoire à 50 %, d'un seul geste de 0,15 s, **un temps
  (0,39 s) avant son attaque** ou dès que la caméra arrive sur le cadrage si c'est plus tard. À l'attaque, elle est « repassée à
  l'encre » : elle devient jaune d'un coup. Le direct reste donc le changement de couleur, calé sur la voix.
- **Ligne entière pré-posée** : au-delà de **4,5 mots par seconde** sur toute la ligne (moins de 0,22 s par mot), la ligne est posée
  d'un coup à l'arrivée de la caméra et seul le repassage suit la voix.
- Le calcul se fait par unité (`durée / nombre de mots`). Sur l'extrait, 9 unités sur 24 sont pré-posées (voir `storyboard.md`).
- Le trait de l'arête suit la pointe (0,3 em d'avance) et **se termine jusqu'au sommet suivant** dans les 0,35 s qui suivent le
  dernier mot : c'est lui qui emmène l'œil vers la ligne suivante.

## Caméra

Verticale, sans perspective : translation, rotation, échelle. Le tempo donne l'unité : 1 temps = 0,388 s, 1 mesure = 1,553 s.

| Mouvement | Quand | Durée | Courbe | Détail |
|---|---|---|---|---|
| **Cadrage** (repos) | pendant qu'un groupe de mots est chanté | — | — | le groupe est centré sur le point de lecture (512, 860) ; lente poussée de 3 % et léger travelling de 8 % de la largeur dans le sens de l'écriture |
| **Glissé** | d'un cadrage au suivant sur la même ligne | 0,12 à 0,26 s | `cubic-bezier(.3,0,.15,1)` | part après 60 % du mot en cours, arrive entre un demi-temps avant l'attaque et l'attaque |
| **Virage** | la ligne suivante part du sommet où l'on est | 1,3 à 2 temps | `cubic-bezier(.6,0,.25,1)` | la caméra pivote autour du sommet ; creux de zoom de 20 % au milieu |
| **Fouetté** | la ligne suivante est ailleurs | **1 temps** | `cubic-bezier(.7,0,.2,1)` | creux de zoom de 28 % ; flou de mouvement réel (sous-images) ; part sur un temps, arrive un demi-temps avant l'attaque |
| **Respiration** | long silence (fanion) | 4 temps | sinus | recul à ×2,3 : la pointe de la voile se devine, pas le bateau |
| **Zoom arrière final** | premier temps de la mesure 20 → premier temps de la mesure 21 | **1 mesure** | échelle `cubic-bezier(.5,0,.12,1)` en logarithme, position `cubic-bezier(.3,0,.1,1)` | de ×5,5 à ×1, rotation ramenée à 0°, puis recul lent jusqu'à ×0,955 |

- **Inclinaison** : la caméra tourne avec la ligne, mais laisse à l'écran un dixième de son angle (6° au plus). Une ligne qui monte
  monte un peu, une ligne qui descend descend un peu ; le texte reste horizontal pour l'œil.
- **Un seul grand virage** dans l'extrait (114° au sommet de la voile). Les autres rotations font moins de 80°. Deux grandes
  rotations de suite donnent le tournis : c'est pour cela que la troisième ligne ne monte pas le long du mât.

## Règles de lisibilité

1. Le mot chanté est **entièrement dans la zone sûre** (x 64 à 960, y 220 à 1600) du début à la fin de sa durée, jaune, et c'est le
   texte le plus contrasté de l'image (l'encre sèche descend à 60 % en gros plan).
2. Corps à l'écran du mot chanté : **120 px au moins**, 220 px au plus (titre 250). Seule dérogation : un passage plus rapide que
   0,30 s par mot peut descendre à **104 px** pour garder dans un même cadrage les mots pré-posés et le mot chanté.
3. Un cadrage dure **0,5 s au moins**. Une unité plus courte que 0,45 s partage le cadrage de sa voisine. Largeur d'un cadrage :
   820 px au plus à l'écran.
4. La caméra **ne quitte jamais un mot avant 60 %** de sa durée, et arrive au plus tard sur l'attaque du mot suivant. Cette règle
   passe avant l'avance du pré-posé : si elle ne laisse pas de marge, le groupe pré-posé apparaît à l'arrivée de la caméra.
5. Au repos, vitesse de la caméra sous 60 px/s à l'écran. Rotation à l'écran sous 6°.
6. Photosensibilité : aucun flash ; le passage au jaune ne concerne qu'un mot.
7. Zoom arrière : le refrain écrit dans la mer fait 78 à 88 px de corps à l'échelle 1 ; il devient lisible avant la fin du zoom.
8. Image finale : rien d'utile dans les 220 px du haut, les 320 px du bas, les 120 px de droite. La note collée et les filets d'eau
   peuvent y entrer : ce sont des décors.

## Langues

- Les paroles sont **toujours dans la langue du morceau**, jamais traduites.
- **Français** : même police, accents sur capitales (É, È, À, Ç) ; prévoir 0,12 em de plus au-dessus des lignes (l'accent ne doit
  pas toucher le trait de la ligne voisine).
- **Arabe (droite à gauche)** : le dessin est symétrique, donc on le **retourne en miroir** : chaque arête se lit de droite à
  gauche, la caméra voyage en sens inverse, les virages changent de signe, les objets changent de côté. Police Cairo ; pas de
  capitales, pas d'interlettrage (l'ajustement se fait par le corps seul, 40 à 64 px) ; révélation de droite à gauche ; un mot est
  toujours dessiné **entier** (jamais lettre par lettre, la cursive casserait). Chiffres et sigles latins restent de gauche à droite
  dans leur mot.

## Jugement sur les images (sévère)

| Image | Lisibilité | Beauté | Défaut à corriger |
|---|---|---|---|
| `01-ouverture-titre` | Très bonne | Sobre, un peu vide | L'accroche repose sur un seul mot jaune sur du bleu ; il manque un indice de matière (un objet qui entre, la pointe visible) dès la première seconde |
| `02-ligne-ecrite-en-direct` | Très bonne | Bonne : la tasse et son ombre posent le « vu de dessus » | Les plis, très agrandis, deviennent de larges bandes diagonales ; à affiner (pli plus net, plus fin) |
| `03-pre-pose-et-encre` | Bonne : jaune = chanté, pâle = pré-posé, la différence se lit sans explication | Bonne : ancienne ligne, crayon et tasse composent un vrai « flat lay » | Corps à 104 px seulement (passage rapide) ; ailleurs, quand le titre voisin est plus gros que la ligne chantée (quille), il lui dispute l'œil malgré l'atténuation à 60 % |
| `04-respiration-fanion` | Bonne | **La plus belle** : on comprend que les lignes font un dessin sans savoir lequel | Léger flou (la caméra recule encore à cet instant) |
| `05-image-d-ensemble` | Bateau reconnu d'emblée ; refrain lisible ; lignes du bateau à 36–43 px, lisibles mais petites | Bonne, la feuille au sol fonctionne | Les mots du refrain posés un par un sur la vague ont un espacement irrégulier ; le tiers bas de la feuille est peu rempli sur 32 s (il se remplit si le refrain continue) ; objets encore un peu « icônes » |

Ce qui serait plus beau, et que la maquette ne fait pas : une encre qui bave légèrement dans le papier (contour irrégulier), des
plis avec une vraie cassure de lumière, des objets dessinés avec un peu plus de matière (reflet du café, bois du crayon), et un
refrain qui finit par recouvrir toute la mer.
