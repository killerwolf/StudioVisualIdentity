# Lyrics punchy — concept (`lyrics-punchy`)

Document de direction artistique, à exécuter tel quel par l'agent qui codera l'identité. Rédigé le 18/11/2026.
Images de contrôle : `frame-1…4*.jpg` dans ce dossier (prototype Pillow, `prototype/proto_frames.py` ; textes de remplissage).

## 1. Intention et public

- Vidéo de paroles verticale (TikTok, 1080×1920, 30 fps) : **les paroles sont la vedette**, le son vient de la bibliothèque TikTok à la publication (vidéo rendue muette).
- Public : 13–30 ans, écoute au casque ou sans le son ; on doit pouvoir **lire la chanson** d'un coup d'œil et sentir le rythme sans audio.
- Nouvelle famille de contenus à déclarer : `paroles`.

## 2. Signature (ce qu'on ne change pas)

1. **Colonne justifiée par l'axe de largeur.** Chaque rang de texte remplit exactement la colonne de 876 px : on ne change pas seulement la taille, on étire ou on serre la police variable **Anybody** (axe `wdth` 50–150). Un mot court devient large et bas, un groupe long devient étroit et haut. Sur un temps fort, le mot arrive trop large et « se resserre » en 5 images.
2. **Mur en camaïeu.** La ligne finie monte au-dessus de la ligne en cours et y reste, dans 3 tons de la **même teinte que le fond**, de plus en plus proches du fond. Un seul rang vif à la fois (crème, mot du moment en couleur d'accent).
3. **Carton d'illustration.** Un mot-clé déclenche un carré couleur d'accent, posé de travers (±4°) sur le mur, avec un pictogramme dessiné par code en 3 couleurs (encre, crème, une seule « couleur vraie »).

Différences vérifiées avec le catalogue (20 déclinaisons dans ce worktree, plus `survol-pixel` dans le worktree principal) :

| Voisine | Sa signature | Ce qui nous sépare |
|---|---|---|
| `brut-meme` (la plus proche) | noir / jaune / rouge, Anton, un mot plein cadre, coupes franches, punch-in caméra | fond coloré jamais noir, Anybody large (pas condensée), le texte **s'accumule** (mur) au lieu d'être remplacé, pas de zoom caméra, pas de sticker rond ni rubalise |
| `swiss-data` | grille visible, un chiffre géant, volets rouges | pas de grille visible, pas de chiffres, fond sombre saturé |
| `bauhaus-kinetic` | crème + formes primaires, Unbounded | pas de formes géométriques hors carton, fond sombre monochrome |
| `riso-zine`, `gazette-1900` | papier, trame, 12 fps | aplats nets, 30 fps, aucune texture |
| `neon-lab`, `liquid-chrome` | noir + néon / chrome | aucun halo, aucun dégradé, aucun noir |

## 3. Palette

Trois camaïeux, un par section de la chanson. Contrastes mesurés sur le fond (script du prototype).

| Rôle | `nuit` (refrain) | `lagon` (couplet) | `braise` (tension) |
|---|---|---|---|
| Fond | `#2A1160` | `#063F4A` | `#5E0F2C` |
| Mur 1 (ligne la plus récente) | `#B9A4F5` 7,2:1 | `#8FD9DC` 7,2:1 | `#F2A5B5` 6,9:1 |
| Mur 2 | `#8468DB` 3,7:1 | `#4FA9B0` 4,2:1 | `#D0708A` 4,0:1 |
| Mur 3 (décoratif, déjà lu) | `#5F45B8` 2,3:1 | `#2F8791` 2,8:1 | `#A64A66` 2,4:1 |
| Accent (mot du moment, carton) | `#E6FF4F` 13,9:1 | `#FF8A5C` 5,0:1 | `#FFD166` 9,2:1 |
| Encre (pictos, plaques) | `#140A33` | `#04252C` | `#33061A` |

- Texte vif : crème `#FFF6E5` (10,8 à 14,5:1 sur les trois fonds).
- Couleurs vraies autorisées dans un carton ou un éclat, une seule à la fois : rouge `#FF3B3B`, vert `#3DDC84`, bleu drapeau `#1F3FBF`, blanc cassé `#F4F1EA`, rouge drapeau `#E1262D`.
- Les trois fonds ont une luminance voisine : changer de camaïeu n'est pas un flash.
- Jamais : noir pur, dégradé, flou, ombre portée, texture.

## 4. Typographie

**Anybody** (Etcetera Type Co, SIL OFL 1.1, Google Fonts), paquet npm `@fontsource-variable/anybody` 5.3.0 (à épingler sans `^`). Axes vérifiés sur le fichier : `wdth` 50–150, `wght` 100–900. Glyphes vérifiés : É À Ç Œ ’ chiffres `. _ / [ ]`. Une seule famille, tout en capitales (accents conservés).

| Rôle | Graisse | Largeur | Taille |
|---|---|---|---|
| Ligne en cours (rang) | 900 | 50–150, calculée | 120 à 250 px, calculée |
| Mur | 800 | 50–150, calculée | 56 à 118 px, calculée |
| Texte dans un carton | 900 | 78 | 58 px mini |

Ajustement d'un rang (même règle pour le mur) : taille = taille maxi × 876 / largeur à `wdth` 100, bornée ; puis on cherche le `wdth` qui donne 876 px ; si c'est encore trop large à `wdth` 50, on réduit la taille ; si c'est trop court à `wdth` 150, le rang reste aligné à gauche. En CSS : `font-variation-settings: "wdth" X, "wght" 900`, `white-space: nowrap`, interlettrage 0.

## 5. Grille et zones sûres

Zones interdites au texte : haut 220 px, **bas 360 px**, **droite 140 px**, gauche 64 px (plus strict que le dépôt, à cause de la légende et du disque du son). Voir `frame-2b-zones-sures.jpg`.

| Zone | Coordonnées | Contenu |
|---|---|---|
| Colonne | x 64–940 (876 px) | tout le texte |
| Compteur de temps | 4 points Ø 26 px, de (64, 249) à (210, 275) | le temps de la mesure en cours, en accent |
| Mur | y 300–800, lignes empilées depuis le bas, 26 px entre elles | 4 lignes passées au plus |
| Carton | carré 440 px, centre (712, 476), rotation ±4° en alternance | un seul à la fois ; ne recouvre jamais la ligne la plus récente du mur |
| Ligne en cours | haut fixe y 850, jusqu'à 1 500 ; 34 px entre rangs | 1 à 3 rangs |
| y 1 500–1 560 | vide | marge |

## 6. Lisibilité

- Unité d'affichage = un mot, ou un petit groupe : articles, prépositions et pronoms de 3 lettres ou moins se collent au mot suivant (« IN THE », « J'AI ÇA »). Jamais de lettre isolée, jamais de phrase entière d'un coup.
- Ligne en cours : **6 unités et 3 rangs au maximum**, 3 unités par rang au maximum. Une ligne chantée plus longue est coupée en deux lignes au moment de la préparation.
- Durée minimale d'une unité avant la suivante : **0,25 s**. Si le débit dépasse 4 unités par seconde, on regroupe par deux.
- Une ligne complète reste vive au moins 0,4 s après sa dernière unité ; elle reste au moins 2 s dans le mur.
- Tailles : jamais sous 120 px pour la ligne en cours, jamais sous 56 px pour le mur.
- À l'écran : 6 unités vives au plus, plus 4 lignes de mur.

## 7. Mouvement

Tout est une fonction du temps `t` et de `lyrics.json` (pas de timeline GSAP, pas d'état). Durées en images à 30 fps.

| Nom | Quand | Mouvement |
|---|---|---|
| `pose` | unité d'accent 0 (contretemps) | opacité 0→1 et échelle 0,9→1 en 2 images |
| `claque` | accent 1 (sur un temps) | échelle 1,3→1 en 3 images, `wdth` +40 %→valeur calculée en 5 images, courbe (1−k)³ |
| `coup` | accent 2 (temps fort, mot déclencheur), au plus un par mesure | comme `claque` avec échelle 1,7→1 en 4 images, puis toute la colonne descend de 12 px et revient en 5 images |
| respiration | chaque temps | la ligne en cours passe à 1,02 puis revient en 4 images ; le mur ne bouge pas |
| mot du moment | durée de l'unité | couleur d'accent, puis crème quand l'unité suivante arrive |
| `empilement` | première unité de la ligne suivante | la ligne finie se recompose sur un rang, graisse 800, glisse en bas du mur en 6 images ; les autres montent d'un cran et perdent un ton ; la 5e disparaît en 4 images |
| `chute-de-pile` (transition signature) | changement de section | les lignes du mur tombent sous le cadre, une image d'écart entre elles, pendant que le fond passe à la nouvelle teinte en 10 images |
| sortie de carton | sur un temps | échelle 1→0 en 3 images |

Entrée d'une unité : 2 images **avant** l'instant chanté (l'œil lit le mot quand la syllabe commence).

On ne fait jamais : lettre par lettre, fondu long, rotation continue, zoom de caméra, tremblement de plus de 12 px, deux `coup` dans la même mesure.

Photosensibilité : pas de flash plein cadre ; `chute-de-pile` et fonds plein cadre espacés d'au moins 1,6 s ; au plus 3 changements rapides par seconde, dans moins de 25 % de l'écran.

## 8. Illustration des mots

Trois types, du plus courant au plus rare.

| Type | Part d'écran | Durée | Règle |
|---|---|---|---|
| `carton` | 10 % (carré 440 px) | 4 temps, borné à 0,8–2,5 s, sortie sur un temps | cas par défaut : objets, lieux, portraits |
| `eclat` | 35 % au plus, centré sur le mot | 2 temps | matière qui touche le mot (sang, feu) ; le mot reste lisible, en crème sur l'éclat |
| `fond` | plein cadre | 2 s au plus, un par 8 s au plus | drapeaux, ciel ; le mur est masqué et la ligne en cours passe en **mode plaque** (chaque rang sur une plaque encre arrondie, voir `frame-4`) |

Densité : un déclencheur par ligne au plus, **au moins 2,5 s entre deux débuts**, jamais deux visuels en même temps, au plus la moitié du temps avec un visuel. Si deux mots d'une ligne déclenchent, on garde la priorité la plus haute.

Style des pictogrammes : aplats, formes arrondies, 3 couleurs (encre, crème, une couleur vraie), dessinés en SVG ou Canvas par code, lisibles en 0,5 s. Aucun logo, aucune mascotte, aucune image téléchargée (règle du dépôt).

### Bibliothèque de déclencheurs (extensible)

Fichier `triggers.json` du moteur, une entrée par déclencheur :
`{ "id", "match": ["mots ou expressions, minuscules sans accent"], "type": "carton|eclat|fond", "dessin": "nom de la fonction", "temps": 4, "priorite": 1–3, "note" }`.
Les expressions de plusieurs mots (« tour eiffel », « plan mode ») sont cherchées avant les mots seuls et forment une seule unité d'affichage. Ajouter un déclencheur = une entrée + une fonction de dessin.

| id | Mots | Type | Visuel |
|---|---|---|---|
| `plan-mode` | plan mode | carton | pastille « PLAN MODE » + liste de 3 lignes dont 2 cochées (`frame-2`) |
| `lignes` | lines, lignes | carton | 5 barres de texte qui se tapent une à une, sans couleur de syntaxe |
| `version` | 2.0, version | carton | étiquette « v2.0 » tamponnée |
| `serveur-panne` | server down, mcp, panne | carton | baie de 3 tiroirs, diode rouge, « 503 », croix (`frame-3`) |
| `cles-api` | api key(s), clé(s) | carton | une clé et une chaîne masquée `sk-••••••` |
| `fichier-md` | .md, markdown | carton | feuille au coin plié marquée « .MD », pile de 3 |
| `mauvais-changement` | bad change, revert | carton | bloc de diff : une ligne `−` rouge, une ligne `+` verte, croix |
| `ship` | ship, ship it, livre | carton | colis tamponné « SHIPPED », un nouveau tampon à chaque répétition |
| `sang` | sang, blood | eclat | éclaboussure rouge procédurale (graine fixe), sur le mot |
| `feu` | feu, flamme, fire | eclat | 3 flammes en aplat derrière le mot |
| `france` | france | fond | trois bandes verticales qui descendent en 6 images (`frame-4`) |
| `tour-eiffel` | tour eiffel | carton | silhouette de jour en aplat (jamais l'éclairage de nuit, qui est protégé) |
| `coeur` | cœur, love, heart | carton | cœur en courbes qui bat sur le temps |
| `argent` | argent, thune, money, cash | carton | 3 billets en éventail |
| `nuit` | nuit, lune, night | carton | croissant de lune et 3 étoiles |
| `telephone` | téléphone, phone | carton | téléphone qui vibre |
| `portrait` | nom d'une personnalité (une entrée par personne, ex. `sarko`) | carton | portrait 3 tons, voir ci-dessous |

### Portrait d'une personnalité

- Rendu : buste dans le carton, **3 tons** (encre, crème, ton moyen du camaïeu) avec trame de points dans le ton moyen, nom en 58 px sous le visage. Reconnaissable mais clairement dessiné.
- Comment l'obtenir, par ordre de préférence :
  1. **Photo sous licence libre** (Wikimedia Commons : domaine public, CC0 ou CC BY ; éviter CC BY-SA, qui impose la même licence au dérivé), recadrée puis réduite à 3 tons par code (Pillow / OpenCV : niveaux de gris, flou léger, seuils, trame). C'est la voie la plus fidèle. Garder la source, l'auteur et la licence dans `portraits/<id>/SOURCE.md` et créditer dans la description de la vidéo.
  2. **Dessin vectoriel écrit à la main** (SVG), d'après plusieurs photos regardées mais jamais décalquées : sans droit de photographe, mais ressemblance moyenne.
- La voie 1 demande **une exception à la règle du dépôt** (« aucune image téléchargée »), du même genre que celle du 05/11/2026 pour les données factuelles. À décider par Hamdi.
- Garde-fous : seulement si le nom est chanté ; jamais d'`eclat` (sang, feu) dans les 2,5 s autour d'un portrait ; pas de portrait dégradant ; pas de rendu photo-réaliste ; pas de personne privée.

## 9. Jetons (à reprendre dans `tokens.json`, format `core-tokens.schema.json`)

```json
{
  "color": { "bg": "#2A1160", "surface": "#140A33", "text": "#FFF6E5", "accent": ["#E6FF4F", "#FF8A5C", "#FFD166"] },
  "typography": {
    "display": { "family": "Anybody", "fontsourceSlug": "anybody (paquet @fontsource-variable/anybody)", "weight": 900, "sizePx": 250, "sizeNote": "120–250 px, rang ajusté à 876 px par l'axe wdth 50–150" },
    "title":   { "family": "Anybody", "fontsourceSlug": "anybody", "weight": 800, "sizePx": 118, "sizeNote": "mur : 56–118 px" },
    "body":    { "family": "Anybody", "fontsourceSlug": "anybody", "weight": 900, "sizePx": 58 },
    "caption": { "family": "Anybody", "fontsourceSlug": "anybody", "weight": 800, "sizePx": 56 }
  },
  "motion": { "durationSec": { "fast": 0.1, "base": 0.2, "slow": 0.33 }, "staggerSec": 0.033, "hookDeadlineSec": 0.5, "sourceUnits": "s",
              "easingRaw": { "enter": "(1-k)^3", "exit": "linéaire 3 images" } },
  "transitions": [ { "name": "empilement", "duration": 0.2 }, { "name": "chute-de-pile", "duration": 0.33 } ],
  "safeAreaPx": { "top": 220, "bottom": 360, "right": 140, "left": 64 },
  "canvas": { "width": 1080, "height": 1920, "fps": 30 }
}
```

## 10. Limites connues

- Identité prévue pour 15 à 40 s ; au-delà, alterner les camaïeux à chaque section pour éviter la lassitude.
- Débit très rapide (rap au-delà de 5 mots par seconde) : le regroupement par deux réduit l'effet « mot par mot ».
- Le mur suppose des lignes courtes ; une ligne de plus de 30 caractères descend sous 56 px et doit être coupée.
