# Lyrics chemin, déclinaisons — journal de réalisation (2026-11-19)

Réalisation des trois propositions de Fable (`README.md`, `b-claudes-plan-tech.md`, `a2-quatre-quarts.md`, `a1-tour-du-monde.md`,
maquette `proto/`), dans l'ordre validé par Hamdi (choix 105) : B, puis A2, puis A1.

| | Short | Habillage / dessin | Durée | Son | check.py |
|---|---|---|---|---|---|
| B | `out/shorts/lyrics-chemin__paroles__claudes-plan-tech/` | `editeur` / `cargo` | 32,62 s | muet (chanson ajoutée dans l'appli) | OK |
| A2 | `out/shorts/lyrics-chemin__explicatif__le-quatre-quarts/` | `ardoise` / `quatre-quarts` | 25,6 s | voix ElevenLabs | OK |
| A1 | `out/shorts/lyrics-chemin__histoire__le-premier-tour-du-monde/` | `portulan` / `tour-du-monde` | 45,0 s | voix ElevenLabs | OK |

Hors dépôt : `~/git/StudioVisualIdentity-sources/lyrics-claudes-plan/` (B aux vraies paroles : `chemin-tech.paroles.json`,
`chemin-tech-paroles-muette.mp4`, `apercu_tech_avec_son.mp4`, `stills-tech-final/`) et `~/git/StudioVisualIdentity-sources/lyrics-chemin-narres/`
(voix maîtres, textes envoyés, mots horodatés, `mots.py`).

## 1. Le moteur : un habillage par épisode

`out/shared/chemin-moteur/chemin.js` ne garde que la mise en page des mots, la pose de l'encre, la caméra, le flou de mouvement et les
mesures de l'audit. Tout ce qui est matière est dans `habillages/<id>.js` (`plan-bleu`, `editeur`, `ardoise`, `portulan`) ; les briques
communes (chemins, textures, ombre) dans `outils.js`. Le fichier d'épisode nomme `dessin` et `habillage` (défaut `plan-bleu`).

**Contrôle de l'extraction** : 8 images du short plan bleu (dont une en plein flou de mouvement, 2,8 s) rendues avant et après sont
**identiques à l'octet**, et la sortie de `chemin_audit.mjs` est identique. Le short existant n'a pas été re-rendu.

Interface d'un habillage (champs facultatifs sauf `fonts`, `font`, `cap`, `gap`, `col`, `floor`, `sheet`) : polices et corps (`em`,
`trackMax`, `gapW`, `floorPx`, `floorFast`, `maxPx`, `cap`, `gap`, `belowY`, `liftAbove/Below`), couleurs (`col.fresh/dry/stroke/annot`,
`dryColor(unité)`), pré-posé (`ghost` : `wipe` crayon ou `fade` suggestion, couleur, graisse, style), `typed` (frappe caractère par
caractère), `prepare`, `floor`, `sheet`, `under`, `stroke`, `tip`, `afterInk`, `annotations{type}`, `textErode`, `objects`, `finish`, `route`.

Ajouts au moteur : arête `troncon` d'une route (et `courbe`), flèche des mots rigides sur une courbe, `gapW` compté dans le corps,
option `inside` (texte centré dans une boîte), classe d'unité (4ᵉ valeur), rangs finaux alignés à gauche (`final.gauche`) ou plats,
calque d'encre érodé (`textErode`), transitions en secondes (`duree`), shorts sans `bpm` (`temps` sert de durée de référence),
plusieurs reculs muets (`respirations`). `chemin_audit.mjs` lit le plancher de l'habillage (via le corps plancher de chaque unité) et
imprime le corps de chaque ligne dans l'image finale.

## 2. B — Claude's Plan, version tech

- **Texte trop petit dans les conteneurs (29–30 px à l'image finale)** : chaque ligne de couplet est **repliée sur deux rangs** dans son
  conteneur (comme une ligne de code repliée ; numéros 01–06 en gouttière), conteneurs de 660 px, corps commun imposé : **46 px**
  à l'image finale (vraies paroles comprises). La pile monte jusqu'à y 242 (conteneur de travers compris) : la coque et le pont
  paraissent plus chargés, le navire se lit mieux. Les rangs se lisent avec un **retour chariot** (glissé de 0,15–0,2 s).
- **Cadrages < 0,5 s** : « i've been / up since 5 a.m. » est coupé en deux rangs (« i've been » seul, puis « up since 5 a.m. » d'un
  bloc) ; la vague passe à deux cadrages (« such a lot » / « of wrong folds ») arrivant 0,02 s plus tôt. Audit : aucune erreur, sur le
  remplissage comme sur les vraies paroles.
- Planchers abaissés sur trois cadrages pré-posés en suggestion (lisibles avant d'être chantés) : 86 px (« up since 5 a.m. »,
  « i've been » sur ses 0,05 dernières secondes), 80 px (« but not for show »), 92 px (la vague). Plancher de l'habillage : 96 px.
- Annotations : ✗ placée de l'autre côté du trait que le texte ; soulignement ondulé sous « wrong fold » ; fanion qui suit la longueur
  du texte. Panneaux d'interface accrochés aux unités (ils apparaissent en 0,15 s).
- Curseur bloc : suit la frappe caractère par caractère, reste au bout de la dernière ligne écrite entre deux lignes, clignote sur le
  temps au repos, et finit au bout du refrain dans la sortie de terminal.
- Respiration : ×1,6 sur (505, 450) au lieu de ×2,3 (la pile est plus haute).
- Rendu : 979 images en 929,5 s (94,9 s / 100 images) ; vraies paroles 848,6 s (86,7 s / 100). Corps restants petits à l'image
  finale (dessin de Fable, inchangé) : flancs et quille 30–32 px, vague 36 px.

## 3. A2 — Le quatre-quarts

- **Faits** (recherche web, sources dans `short.json`) : principe confirmé (quatre ingrédients à poids égal, origine bretonne, 180 °C).
  Écarts au texte de Fable : « avec leur coquille » retiré (la plupart des recettes pèsent les œufs cassés) ; cuisson « quarante
  minutes » au lieu de 45 (30 à 45 min selon les sources pour ce volume). Rang final : `40 MINUTES`.
- **Voix** : ElevenLabs « Gipsy Paladini — Narration, conversation » (bibliothèque, fr-standard, femme, âge moyen, chaleureuse),
  `eleven_multilingual_v2`, **une** génération de 336 caractères = **336 crédits**, aucune reprise. 24,1 s, débit plus rapide que
  l'estimation (27 s).
- Mots horodatés par faster-whisper `small` (fr) ; temps recopiés dans `narration-chemin.json`. Le zoom arrière passe sur « Versez dans
  un moule beurré » (16,25–17,9 s), le moule se trace pendant ; « Quatre parts égales » déclenche le double soulignement (21,2 s).
- Corps commun de 40 px imposé aux quatre demi-coupes (recommandation de Fable) ; plancher 104 px sur « QUATRE INGRÉDIENTS »
  (trop large à 120 px une fois tourné).
- Rendu : 768 images en 925,9 s (120,6 s / 100 : le calque de craie érodé coûte à chaque sous-image du flou).

## 4. A1 — Le premier tour du monde

- **Faits** : dates, nombre de navires, mort aux Philippines, retour de la Victoria sous Elcano le 6 septembre 1522 avec 18 hommes :
  confirmés, texte inchangé. Arrivée à Sanlúcar le 6, à Séville le 8 ; équipage de départ 239 à 270 selon les sources (non cité).
- **Voix** : ElevenLabs « Justin Doré — Documentary Narrator » (bibliothèque, fr-standard, homme, âge moyen, grave, posé),
  `eleven_multilingual_v2`, **une** génération de 601 caractères = **601 crédits**, aucune reprise. 43,1 s (39 s estimées) : le short
  passe à 45 s. « Sebastián » est lu à la française, non corrigé.
- Horodatage : faster-whisper a bouclé sur un passage (≈ 30 s) puis s'est repris ; tous les mots écrits au sol sont dans la partie juste.
- Route continue : la pointe (point vermillon luisant) avance avec l'écriture, puis trace le trajet muet entre deux textes ; la carte
  (terres, côtes, bordure) est rendue **une fois** en image à 3 px par unité au lieu d'être redessinée à chaque sous-image.
- Cinq reculs muets (`respirations`) pour les phrases sans texte au sol : Atlantique, entrée du détroit, Pacifique, Moluques, cap.
- Écarts : « MAGELLAN / EST TUÉ » en deux cadrages (trop large d'un bloc) ; `gapW` 0,6 sur « LE DÉTROIT » (les mots rigides se
  chevauchaient du côté concave) ; corps maximal 190 px sur « 20 SEPT. » (zone sûre) ; navires posés du côté opposé au texte.

## 5. Commun

- **check.py** : la limite de 20 s ne convenait pas aux shorts narrés (25,6 et 45 s). Ajout d'une règle étroite : un short qui déclare
  `"longForm": true` dans `short.json` est admis jusqu'à 60 s, comme la famille `paroles`. A2 est rangé en `explicatif`, A1 en `histoire`.
- **Crédits ElevenLabs** : 336 + 601 = **937 crédits** pour 937 caractères (budget ≈ 1 000, plafond 2 500). `account_get_usage` a été
  refusé par le connecteur (droits insuffisants) : le chiffre vient du coût annoncé par chaque génération.
- **Licence** : voix générées sur le compte ElevenLabs d'Hamdi ; fichiers maîtres hors dépôt, voix mixée dans `short.mp4`.
- **Lit sonore** : non posé (facultatif ; aucun son libre de droits adapté déjà présent dans le dépôt).
- Non fait : test de reconnaissance, relecture à l'oreille des vraies paroles de B après 19,5 s (héritée), français et arabe pour les
  paroles, `lyrics_align.py` non utilisé (temps recopiés à la main depuis les mots horodatés).
