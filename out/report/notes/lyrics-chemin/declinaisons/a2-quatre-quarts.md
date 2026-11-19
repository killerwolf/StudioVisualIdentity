# A2 — « Le quatre-quarts » (recette, narré, 30 s)

Short narré 1080×1920, 30 i/s, 30,0 s. Habillage `ardoise`, dessin `quatre-quarts`. Maquette : `proto/quatre-quarts.js`.
Images : `images/a2-01` à `a2-04` (clé : `a2-03-image-cle-coupe-17.90s.jpg` ; finale : `a2-04-image-finale-29.90s.jpg`).

## L'idée

Le nom du gâteau est sa recette : quatre ingrédients, à parts égales. Le texte dessine donc **un gâteau rond vu de dessus, coupé en
quatre parts** : les deux coups de couteau portent les phrases, chaque part reçoit le nom d'un ingrédient, le moule se trace quand la
voix dit « moule », la cuisson s'écrit dessous. L'image finale est une fiche de recette qu'on peut capturer et garder.

Contraste voulu avec A1 : ton chaleureux et pratique contre récit grave, surface sombre contre parchemin clair, arêtes droites et
virages à 40° contre une longue courbe.

## Narration (français, 59 mots, ≈ 27 s de voix)

> Le quatre-quarts.
> Tout est dans son nom : quatre ingrédients, à parts égales.
> Pesez trois œufs, avec leur coquille.
> Puis le même poids de sucre, de farine, et de beurre fondu.
> Fouettez les œufs avec le sucre, ajoutez la farine, puis le beurre.
> Versez dans un moule beurré.
> Quarante-cinq minutes, à cent quatre-vingts degrés.
> Quatre parts égales. Un seul gâteau.

Recette : c'est la formule traditionnelle du quatre-quarts (breton), où l'on pèse les œufs avec leur coquille et où l'on prend le même
poids de sucre, de farine et de beurre ; trois œufs font environ 180 g, pour un moule de 20 à 22 cm ; cuisson courante 40 à 50 min à
180 °C, à vérifier à la lame du couteau. Variantes laissées de côté pour tenir en 30 s : pincée de sel, levure chimique, blancs montés.
**Source à citer à la publication : à contrôler** (par exemple l'article « quatre-quarts » du *Larousse gastronomique* ; non rouvert
pendant ce travail).

## Ce qui s'écrit au sol

| Dit | Écrit | Où |
|---|---|---|
| Le quatre-quarts | `QUATRE-QUARTS` (titre, 103 px) | en haut, droit |
| quatre ingrédients, | `QUATRE INGRÉDIENTS` | première coupe, du bord haut gauche au centre |
| à parts égales | `À PARTS ÉGALES` | même coupe, du centre au bord bas droit |
| trois œufs | `3 ŒUFS` (84 px) | part du haut |
| sucre | `SUCRE` | part de droite |
| farine | `FARINE` | part du bas |
| beurre | `BEURRE` | part de gauche |
| Fouettez les œufs avec le sucre | `ŒUFS` · `+ SUCRE` | seconde coupe, du bord bas gauche au centre |
| ajoutez la farine, puis le beurre | `+ FARINE` · `+ BEURRE` | seconde coupe, du centre au bord haut droit |
| un moule beurré | *(le cercle cannelé du moule se trace, sans texte)* | autour |
| Quarante-cinq minutes, à 180 degrés | rangs finaux : `45 MINUTES` / `À 180 °C` (100 px) | sous le gâteau |
| Quatre parts égales. Un seul gâteau. | *(double soulignement à la craie rose sous le titre)* | |

Les quatre noms d'ingrédients sont **horizontaux** dans l'image finale, les phrases sur les coupes à ±45°.

## Surface et habillage `ardoise`

- **Feuille** : ardoise de bistrot `#2C3836` (dégradé `#364643` → `#222C2B`), nappes de poussière de craie essuyée, traînées de chiffon
  à −14°, mouchetis ; **cadre en chêne** de 30 px (`#D2AC74` → `#B58A52`, veiné, coupes d'onglet), ombre intérieure du cadre.
- **Sol** : plan de travail en marbre clair `#E7E3DC`, veines grises.
- **Craie** : le calque d'encre est **érodé** par un grain attaché au monde (`textErode`) : il grossit avec le zoom, c'est lui qui fait la
  craie. Traits 3,6 px.
- **Pointe** : un **bâton de craie jaune** (1,5 em de long, incliné à 52°, ombre portée) qui suit l'écriture. Un point lumineux se lisait
  comme un point final : écarté.
- **Objets posés** : deux œufs et un fouet en haut, cuillère en bois et plaquette de beurre sur son papier en bas (zone basse, décor).
  À la réalisation, ajouter si la place le permet un voile de farine près du beurre ; rien sur le gâteau.

| Rôle | Couleur | Contraste sur l'ardoise |
|---|---|---|
| Craie sèche | blanc cassé `#F1EEE6` (66 % en gros plan) | 10,5:1 (8,6 au plus clair) |
| **Craie fraîche (mot dit)** | jaune beurre `#FFD766` | 8,8:1 (7,2 au plus clair) |
| Annotations | craie rose `#F29A85` | 5,6:1 ; soulignement ; jamais du texte |

**Typographie** : celle de l'identité, Barlow Condensed 700 (phrases) et 800 (titre, ingrédients, rangs finaux), capitales
(`@fontsource/barlow-condensed` 5.3.0). « Œ » et « É » sont dans le sous-ensemble latin.

## Dessin `quatre-quarts`

Repère monde = image finale. Cercle du gâteau : centre **C (512, 930)**, rayon 390 ; moule : second cercle cannelé à 407.

| Arête | Chemin | Texte | Corps calculé |
|---|---|---|---|
| `titre` | (192, 400) → (832, 400), centré, sans trait | QUATRE-QUARTS | 103 px (800) |
| `coupe1a` | TL (236, 654) → C, marges 34 / 62 | QUATRE INGRÉDIENTS | 39 px |
| `coupe1b` | C → BR (788, 1206), marges 62 / 34 | À PARTS ÉGALES | 50 px |
| `oeufs` | (352, 712) → (672, 712), centré, sans trait | 3 ŒUFS | 84 px (800) |
| `sucre` | (618, 960) → (878, 960) | SUCRE | 84 px |
| `farine` | (372, 1146) → (652, 1146) | FARINE | 84 px |
| `beurre` | (140, 960) → (410, 960) | BEURRE | 84 px |
| `coupe2a` | BL (236, 1206) → C, marges 34 / 62 | ŒUFS + SUCRE | 54 px |
| `coupe2b` | C → TR (788, 654), marges 62 / 34 | + FARINE + BEURRE | 44 px |
| rangs finaux | y 1452 et 1562, centrés sur x 512 | 45 MINUTES / À 180 °C | 100 px |

La marge de 62 px au centre empêche les phrases des deux coupes de se toucher. Les corps des quatre demi-coupes diffèrent (39 à 54 px)
parce que chacun est ajusté à son arête : à la réalisation, **imposer un corps commun de 40 px** aux quatre (`em: [40, 40]`), plus net.

## Storyboard (temps estimés)

| Temps (s) | Voix | Au sol | Caméra |
|---|---|---|---|
| 0,0–1,3 | « Le quatre-quarts. » | `QUATRE-QUARTS` s'écrit dès l'image 0, bâton de craie visible | (512, 349) ×1,22, 0° ; œufs et fouet dans le champ |
| 1,3–2,9 | « Tout est dans son nom : » | — | poussée lente de 3 % sur le titre, puis virage 0,8 s (40°) |
| 2,9–4,4 | « quatre ingrédients, » | `QUATRE` · `INGRÉDIENTS` ; la première coupe se trace | (378, 769) ×3,1, 40,5° |
| 4,45–5,5 | « à parts égales. » | `À PARTS` · `ÉGALES` ; la coupe atteint le bord | glissé par le centre → (678, 1060) ×2,65 |
| 5,6–8,4 | « Pesez trois œufs, avec leur coquille. » | `3 ŒUFS` (6,5–7,3) | fouetté 0,5 s, rotation ramenée à 0° → (512, 670) ×2,6 |
| 8,9–10,5 | « Puis le même poids de sucre, » | `SUCRE` (9,9–10,5) | glissé 0,4 s → (748, 918) ×2,4 |
| 10,7–11,5 | « de farine, » | `FARINE` | glissé → (512, 1104) ×2,6 |
| 11,8–13,2 | « et de beurre fondu. » | `BEURRE` | glissé → (275, 918) ×2,6 |
| 13,9–15,8 | « Fouettez les œufs avec le sucre, » | `ŒUFS` · `+ SUCRE` ; la seconde coupe se trace | virage 0,7 s (−40,5°) → (345, 1059) ×2,65 |
| 16,0–18,3 | « ajoutez la farine, puis le beurre. » | `+ FARINE` · `+ BEURRE` ; la coupe atteint le bord | glissé par le centre → (644, 767) ×2,8 (image clé à 17,9) |
| 18,8–20,8 | « Versez dans un moule beurré. » | le moule cannelé se trace d'un tour (18,9–20,8) | **zoom arrière** 19,0–20,8, rotation ramenée à 0° |
| 21,2–24,4 | « Quarante-cinq minutes, à cent quatre-vingts degrés. » | `45 MINUTES` (21,2) / `À 180 °C` (22,6) | image d'ensemble |
| 25,0–27,6 | « Quatre parts égales. Un seul gâteau. » | double soulignement rose sous le titre (25,2–25,8) | recul lent à ×0,955 |
| 27,6–30,0 | (silence) | `À 180 °C` encore jaune | tenue |

Les quatre ingrédients s'enchaînent sans rotation (glissés de 0,4 s, sens des aiguilles d'une montre) : c'est le passage le plus rapide,
un mot par cadrage, chacun tenu ≥ 0,6 s. Deux virages seulement, de 40°.

## Voix (ElevenLabs — profil recherché)

- **Femme, 30–45 ans, français de France**, voix chaude et souriante, proche du micro, un peu basse ; diction de **cheffe qui explique
  à quelqu'un dans sa cuisine** : simple, gourmande, précise sur les verbes (« pesez », « fouettez », « versez ») ; ni voix de publicité
  ni ton d'animatrice.
- Dans la bibliothèque : langue *French*, usage *Conversational / Narration*, descripteurs *warm, soft, friendly, calm*.
- Débit 2,5–2,7 mots/s ; pauses nettes après « Le quatre-quarts. » et avant « Quatre parts égales. » ; l'énumération « de sucre, de
  farine, et de beurre fondu » doit laisser ≈ 0,5 s par ingrédient (un cadrage chacun).
- Texte envoyé : « cent quatre-vingts degrés » en lettres ; « quatre-quarts » se dit « katkar » (vérifier que le t de « quarts » reste muet).
- Lit sonore proposé, très bas : crissement de craie sur chaque mot écrit (banque CC0 du skill `sound-design`), un fouet qui tinte à 14 s,
  porte de four à 21 s. Pas de musique, ou une guitare sèche à peine audible.

## Ce qui change dans le moteur pour A2

Habillage `ardoise` (dont `textErode` et la pointe-objet) ; dessin `quatre-quarts` : uniquement des arêtes droites, plus un **cercle
tracé sans texte** pendant le zoom arrière (primitive `cercle` liée à un intervalle de temps) et une annotation `souligne`.
Aucune règle de caméra nouvelle. Durées de transition en secondes.

## Incertitudes propres à A2

- **Accroche** : à ×1,22 le titre entier tient, mais le haut de l'image montre le marbre et le cadre (zone haute). Si c'est trop vide,
  ouvrir à ×2 sur « QUATRE- » puis glisser sur « QUARTS » (le titre se coupe au trait d'union, à prévoir dans la mise en page).
- **Voisinage** avec `tableau-craie` (voir README).
- Le « = » entre les parts (craie rose, pour « le même poids ») a été envisagé et pas dessiné : la place manque près du bord.
- Recette donnée sans sel ni levure : choix d'écriture, à valider.
