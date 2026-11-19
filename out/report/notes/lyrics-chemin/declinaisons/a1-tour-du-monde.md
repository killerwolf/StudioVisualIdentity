# A1 — « Le premier tour du monde » (histoire, narré, 41 s)

Short narré 1080×1920, 30 i/s, 41,0 s. Habillage `portulan`, dessin `tour-du-monde`. Maquette : `proto/magellan.js`.
Images : `images/a1-01` à `a1-06` (clé : `a1-03-image-cle-magellan-5.90s.jpg` ; finale : `a1-06-image-finale-40.90s.jpg`).

## L'idée

Le texte de la narration **est la route** de l'expédition Magellan–Elcano : il s'écrit à l'encre le long du trajet, sur une carte
marine posée sur une table. La carte est vue **depuis le pôle Sud** (projection azimutale équidistante) : dans cette vue un tour du
monde devient une **boucle qui se referme**. Au zoom arrière on découvre la boucle entière, fermée au point de départ, et la phrase
finale s'écrit dessous.

Pourquoi cette projection, et pas un planisphère : le voyage va vers l'ouest. Sur une carte nord en haut, le texte courrait de droite à
gauche, à l'envers presque partout. Vu du pôle Sud, l'ouest tourne dans le sens inverse des aiguilles : le texte se lit vers le bas le
long de l'Atlantique, **à l'endroit dans le Pacifique**, vers le haut dans l'océan Indien, et à l'endroit à l'arrivée. Il reste à
l'envers sur deux tronçons courts (« 20 SEPT. » au départ, « 6 SEPT. 1522 » le long de l'Afrique) : on l'accepte comme la légende
circulaire d'une monnaie ; ces mots ont été lus en gros plan, caméra tournée.

## Narration (français, 93 mots, ≈ 39 s de voix)

> Le 20 septembre 1519, cinq navires quittent l'Espagne.
> À leur tête, Fernand de Magellan. Son pari : atteindre les îles aux épices par l'ouest.
> Tout au sud de l'Amérique, il trouve enfin un passage : le détroit qui porte aujourd'hui son nom.
> De l'autre côté, un océan immense. Plus de trois mois de mer.
> Aux Philippines, Magellan est tué au combat.
> C'est Juan Sebastián Elcano qui ramène le dernier navire, la Victoria, par le cap de Bonne-Espérance.
> Le 6 septembre 1522, dix-huit hommes rentrent au port.
> Ils viennent de boucler le premier tour du monde.

Texte à envoyer à la voix (nombres en lettres, pour qu'ils ne soient pas lus chiffre à chiffre) : « Le vingt septembre mille cinq cent
dix-neuf… », « Le six septembre mille cinq cent vingt-deux, dix-huit hommes… ». « Sebastián Elcano » se dit à l'espagnole
(« Sébastiane Elcano ») ; vérifier à l'écoute, sinon écrire phonétiquement.

### Faits et sources

| Affirmation | Fait | Source |
|---|---|---|
| 20 septembre 1519, cinq navires | départ de Sanlúcar de Barrameda ; Trinidad, San Antonio, Concepción, Victoria, Santiago | Pigafetta, *Relation du premier voyage autour du monde* ; Britannica, « Ferdinand Magellan » |
| îles aux épices par l'ouest | but : les Moluques, par une route occidentale (traité de Tordesillas) | idem |
| détroit | traversé du 21 octobre au 28 novembre 1520 | Pigafetta |
| plus de trois mois de mer | du 28 novembre 1520 à Guam, le 6 mars 1521 (98 jours ; Pigafetta écrit « trois mois et vingt jours ») | Pigafetta |
| tué aux Philippines | île de Mactan, 27 avril 1521 | Pigafetta |
| Elcano, la Victoria, Bonne-Espérance | seul navire à boucler le tour, cap doublé en mai 1522 | Britannica, « Juan Sebastián del Cano » |
| 6 septembre 1522, dix-huit hommes | retour à Sanlúcar ; 18 Européens à bord | Pigafetta ; liste des survivants (Archivo General de Indias) |

**Sources citées de mémoire, non rouvertes pendant ce travail : à contrôler avant publication.** Deux nuances connues : l'équipage de
départ varie selon les sources (≈ 237 à 270 hommes : le texte ne donne pas de chiffre) ; outre les 18 Européens, quelques hommes
embarqués en Asie étaient à bord (le texte dit « dix-huit hommes », formule d'usage).

## Ce qui s'écrit au sol

Capitales, 36–44 px dans le monde. Dix unités sur la route, deux rangs finaux. Tout le reste de la narration est porté par le trait
qui avance (trajets « muets ») et par les annotations.

| Dit | Écrit | Où sur la route |
|---|---|---|
| Le 20 septembre 1519 | `20 SEPT.` puis `1519` | de l'Espagne au large du Cap-Vert ; coupé en deux pour laisser passer le croisement avec la route du retour |
| cinq navires | *(annotation : cinq petits navires au bleu de Prusse, en face de « 1519 »)* | |
| Fernand de Magellan | `MAGELLAN` | le long du Brésil et de l'Argentine |
| le détroit | `LE DÉTROIT` | juste après la sortie du détroit, côte du Chili |
| un océan immense | `UN OCÉAN` · `IMMENSE` | Pacifique sud |
| Magellan est tué | `MAGELLAN` · `EST TUÉ` + croix † | arrivée sur Guam et les Philippines |
| Elcano | `ELCANO` | de Timor vers l'océan Indien |
| la Victoria | `LA VICTORIA` | océan Indien, jusqu'au cap |
| Le 6 septembre 1522 | `6 SEPT.` · `1522` | Atlantique sud, le long de l'Afrique |
| dix-huit hommes | `18 HOMMES` | des Açores à l'Espagne (à l'endroit, il ferme la boucle) |
| le premier tour du monde | rangs finaux : `LE PREMIER` / `TOUR DU MONDE` | sous la carte, 95 px |

## Surface et habillage `portulan`

- **Feuille** : parchemin `#E9DCBC` (dégradé `#F1E7CC` haut gauche → `#D9C79E` bas droit, attaché à la feuille), taches, fibres, bords
  brunis, les quatre plis de l'identité (arête fine à largeur constante à l'écran), double filet d'encadrement.
- **Carte** : disque de 640 px de rayon centré en (512, 846), 4,6 px par degré depuis le pôle Sud, méridien 6° O en haut (l'Espagne est
  en haut, l'Afrique pend vers le centre). Bordure graduée tous les 5°. Terres `#CDB684`, trait de côte sépia, liseré bleu-gris au large.
  Côtes réelles : `world-atlas` 2.0.2 `land-50m.json` (Natural Earth, domaine public), déjà dans le dépôt. L'Antarctique n'est pas
  dessiné (inconnu en 1522) ; la carte **s'efface vers le bas** (y 1290–1385) pour laisser le parchemin nu aux rangs finaux.
- **Réseau de rhumbs** : 16 nœuds sur un cercle de 560 px, lignes fines sépia, vermillon et bleu à 10–16 %.
- **Noms** (décor, jamais un mot de la narration) : Cormorant Garamond italique 500, 14–21 px, sépia à 55 %, à l'endroit dans l'image
  finale. Rose des vents à l'encre dans le Pacifique (196, 1196).
- **Sol** : table en noyer `#3A281B`, veinée, visible au bord.
- **Objets posés** : boussole en laiton sur le pôle (rayon 96, elle couvre l'Antarctique), compas à pointes sèches en haut à droite
  (hors du disque), sceau de cire rouge et son ruban en bas à droite (zone basse, décor).

| Rôle | Couleur | Contraste |
|---|---|---|
| Encre sèche | sépia `#3A2718` | 10,4:1 sur le parchemin (8,5 au plus sombre ; 7,2 sur les terres) |
| **Encre fraîche (mot dit)** | vermillon `#B8301A` | 4,4:1 (3,6 au plus sombre ; 3,1 sur les terres) : suffisant pour un mot de 120 px et plus, **sous 4,5** |
| Annotations | bleu de Prusse `#27506E` | 6,3:1 ; navires, croix ; jamais du texte |
| Pointe | point d'encre vermillon luisant (0,10 em) | |

**Typographie** : Cormorant Garamond 700, capitales (`@fontsource/cormorant-garamond`, SIL OFL 1.1, déjà dans le dépôt ; à épingler).
Hauteur de capitale 0,63 em, écart au trait 0,20 em, espace entre mots +0,16 em (`gapW`). Ses chiffres sont elzéviriens (« 1519 » à
hauteurs inégales) : gardé, c'est d'époque. Rangs finaux : même police, 95 px.

## Dessin `tour-du-monde`

- Une **route** : 43 jalons (longitude, latitude) lissés (Catmull-Rom), 3 369 px de long, listés dans `proto/magellan.js` (`WP`).
  Elle passe au large des côtes, traverse la Patagonie au détroit, se croise une fois (au large du Cap-Vert, aller et retour).
- Dix **arêtes** = dix tronçons de cette route, donnés par un jalon, un décalage et une longueur (table `G.aretes`). Corps calculés :
  43 / 44 / 37 / 36 / 36 / 36 / 44 / 39 / 40 / 37 px (`proto/storyboard-magellan.json`).
- `20 SEPT.` et `1519` sont posés **sous** le trait (côté large) ; les autres au-dessus.
- Escales marquées d'un petit cercle quand la pointe y passe (Espagne, entrée du détroit, Guam, Cebu, Tidore, cap, Cap-Vert) ; point
  vermillon sur l'Espagne quand la boucle se ferme.

## Storyboard (temps estimés ; caméra = point du monde au point de lecture, zoom, angle)

| Temps (s) | Voix | Au sol | Caméra |
|---|---|---|---|
| 0,0–1,2 | « Le vingt septembre » | `20 SEPT.` s'écrit dès l'image 0 (pointe visible) | très gros plan (384, 318) ×4,9, 121° ; côte du Maroc et rhumbs dans le champ |
| 1,2–2,3 | « mille cinq cent dix-neuf, » | `1519` | glissé 0,2 s → (332, 452) ×5,7, 98° |
| 2,3–4,0 | « cinq navires quittent l'Espagne. » | cinq navires bleus posés un à un (2,6–3,6) en face de « 1519 » | cadrage tenu, dérive lente |
| 4,0–4,6 | (pause) | le trait repart vers le sud-ouest | virage 0,6 s (17°) |
| 4,6–6,3 | « À leur tête, Fernand de Magellan. » | `MAGELLAN` (5,1–6,3) | (362, 637) ×3,9, 82° ; l'Amérique du Sud entre par le bas |
| 6,6–10,0 | « Son pari : atteindre les îles aux épices par l'ouest. » | trajet muet : le trait descend la côte jusqu'à l'entrée du détroit | **respiration** : recul à ×2,3 sur (380, 700), on voit l'Atlantique et la ligne qui file ; retour à ×4 en fin |
| 10,5–13,2 | « Tout au sud de l'Amérique, il trouve enfin un passage : » | le trait franchit le détroit (épingle) ; cercle d'escale | virage lent autour de (368, 760) ×4,5, de 82° à 93° |
| 13,2–15,9 | « le détroit qui porte aujourd'hui son nom. » | `LE DÉTROIT` (13,6–14,8) | (213, 895) ×3,7, 93° |
| 16,4–18,2 | « De l'autre côté, un océan » | `UN OCÉAN` (17,3–18,2) | virage 0,5 s → (269, 1087) ×4,1, 51° |
| 18,2–19,2 | « immense. » | `IMMENSE` | glissé → (393, 1217) ×5,0, 32° ; rien d'autre que la mer dans le cadre |
| 19,4–20,6 | « Plus de trois mois de mer. » | trajet muet, lent | recul à ×2,6, dérive le long du trait ; la rose des vents passe à gauche |
| 21,2–22,8 | « Aux Philippines, Magellan » | `MAGELLAN` (22,0–22,8) | (563, 1277) ×4,1, 4° |
| 22,8–24,2 | « est tué au combat. » | `EST TUÉ` ; croix † bleue à 23,3 | glissé → (730, 1249) ×5,5, −26° |
| 24,2–26,0 | « C'est Juan Sebastián » | trajet muet rapide : Philippines, Brunei, Moluques, Timor | recul à ×2,4 puis virage (−68°) en 1,2 s |
| 26,0–27,2 | « Elcano » | `ELCANO` (26,2–27,2) | (783, 953) ×4,1, −94° |
| 27,2–29,3 | « qui ramène le dernier navire, la Victoria, » | `LA VICTORIA` (28,3–29,3) | virage → (683, 728) ×3,1, −119° ; la boussole passe à gauche |
| 29,3–31,0 | « par le cap de Bonne-Espérance. » | trajet muet : le cap est doublé, cercle d'escale | glissé le long du trait, ×3 |
| 31,6–33,4 | « Le six septembre mille cinq cent vingt-deux, » | `6 SEPT.` · `1522` | (542, 509) ×3,8, −125° |
| 33,4–34,2 | (souffle) | trajet muet : croisement, Cap-Vert, Açores | virage de 117° en 0,8 s, creux de zoom 30 % |
| 34,2–35,4 | « dix-huit hommes rentrent au port. » | `18 HOMMES` (34,4–35,3) ; le trait touche l'Espagne, point vermillon | (381, 243) ×3,8, −8,5° |
| 35,6–37,4 | « Ils viennent de boucler » | la boucle est fermée | **zoom arrière** 1,8 s jusqu'à (512, 860) ×1, 0° |
| 37,2–39,2 | « le premier tour du monde. » | rangs finaux `LE PREMIER` (37,2) / `TOUR DU MONDE` (38,0) | image d'ensemble |
| 39,2–41,0 | (silence) | dernier rang encore vermillon | recul lent à ×0,955 |

La caméra tourne de 246° dans un sens (de 121° à −125°), puis revient de 117° pour l'arrivée : jamais deux rotations de plus de 90°
de suite, la plus rapide est le virage de 33,4 s (≈ 146°/s en moyenne, à mesurer à l'audit).

## Voix (ElevenLabs — profil recherché)

- **Homme, 45–60 ans, français de France sans accent régional**, timbre grave et chaud, grain léger ; diction de **narrateur de
  documentaire historique** (retenue, phrases posées, fin de phrase qui descend) ; ni voix de bande-annonce, ni voix de publicité.
- Dans la bibliothèque : langue *French*, usage *Narration / Documentary / Audiobook*, descripteurs *deep, warm, calm, mature*.
  Écarter les voix clonées de personnalités et les accents québécois, belge ou suisse.
- Débit 2,4–2,6 mots/s, pauses de 0,5–0,6 s aux retours à la ligne du texte, un vrai silence avant « Ils viennent de boucler… ».
- Réglages à l'essai : stabilité plutôt haute, peu d'exagération de style ; une seule prise pour tout le texte (ne pas générer phrase
  par phrase : le ton doit tenir d'un bout à l'autre).
- Lit sonore proposé, très bas (−24 dB sous la voix) : ressac et bois qui craque, une note tenue de violoncelle à partir du zoom arrière.

## Ce qui change dans le moteur pour A1

Habillage `portulan` ; dessin `tour-du-monde` ; **arête `courbe`** avec la flèche et `gapW` ; **route continue** (avance de la pointe
interpolée entre les unités, `routeD(t)` dans la maquette) ; cadrages « muets » (recul qui suit la pointe sans texte, à déclarer comme
des `respiration` multiples) ; durées de transition en secondes.

## Incertitudes propres à A1

- **Lisibilité de la carte** : une vue du pôle Sud n'est pas familière. Les noms d'océans et de continents aident ; à faire juger par
  Hamdi sur l'image finale. Repli : planisphère en bandeau, mais le texte y serait à l'envers presque partout.
- **Texte à l'envers** sur deux tronçons de l'image finale (voir « L'idée »).
- **Vermillon à 4,4:1** : s'il manque de présence en vidéo, foncer en `#A62A16` (≈ 5,2:1).
- **Corps 36 px** sur les tronçons serrés ; la route ne laisse pas de place pour plus de texte : ne rien ajouter au sol.
- **Mots rigides sur une courbe** : l'écart au trait varie avec la courbure (visible sur « IMMENSE ») ; acceptable sur les images,
  à juger en mouvement.
- Les jalons de la route sont posés à l'œil au large des côtes : c'est un tracé d'illustration, pas le journal de bord.
