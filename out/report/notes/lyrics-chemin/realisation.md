# Lyrics chemin — journal de réalisation (2026-11-19)

Réalisation du concept de Fable (`concept.md`, `storyboard.md`, `technique.md`, maquette `proto/scene.html`) en identité
`lyrics-chemin` : moteur `out/shared/chemin-moteur/`, contrôle `out/tools/chemin_audit.mjs`, short de preuve
`out/shorts/lyrics-chemin__paroles__claudes-plan/`, design system `out/identities/lyrics-chemin/`.

## 1. Le mouvement jugé en vidéo (10 premières secondes)

Méthode : rendu vidéo de 0 à 10 s (maquette d'origine, puis moteur), bandes d'images par ffmpeg (`select` + `tile`) sur le premier
fouetté (2,5–3,1 s) et le virage en épingle (5,7–7,0 s), et mesures image par image sans rendu (`chemin_audit.mjs` : rotation et
vitesse de pointe par transition, déplacement du coin le plus rapide).

| Constat sur la maquette | Mesure | Correction |
|---|---|---|
| Fouettés : copies distinctes du mot (« DRAFT DRAFT ») au lieu d'une traînée | pas entre sous-images jusqu'à ~11 px ; le nombre de sous-images était estimé par `dθ·700` (sous-estime les coins à ~1 100 px du centre) et plafonné à 48 ; moyenne 8 bits par `globalAlpha = 1/(i+1)` | déplacement réel de 9 points de l'écran (coins compris) entre t − 1/60 et t ; une sous-image tous les 3 px, 64 au plus ; au-delà, obturateur raccourci plutôt que copies espacées ; moyenne en flottants (`Float32Array`) — plus aucune strie sur les bandes |
| Virage en épingle 114° en 2 temps : l'écran n'est plus qu'un papier flou pendant 4 images, puis la ligne réapparaît presque verticale | rotation de pointe 368°/s | **3 temps** (repli prévu par `technique.md`), départ 5,78 s (après 60 % de la dernière unité), arrivée 6,95 s ; courbe `(.5,0,.3,1)`, creux de zoom 30 % : 249°/s, on voit la pente et le sommet passer |
| Mot chanté qui frôle le bord (x 62, 1 028) au repos | 11 unités hors zone sûre sur 1 à 14 images | cadrage à **780 px** au lieu de 820, dérive plafonnée à 40 px/s à l'écran |
| Groupe « SUCH A LOT OF WRONG » (vague) : 1 006 px à 120 px de corps, impossible à cadrer | — | plancher **92 px** quand tout le cadrage dépasse 4,5 mots/s (ligne entière pré-posée, déjà lisible avant d'être chantée) ; règle ajoutée à l'identité |
| Fouettés d'un temps | 463 à 698°/s de pointe | gardés : sous un vrai flou ils se lisent comme des « whip pans » ; noté en risque |
| Glissés courts (0,12 s) vers les gros plans | 7 000 à 16 000 px/s au point de lecture | gardés (3–4 images, couverts par le flou) |

Après correction, `chemin_audit.mjs` ne relève **aucune** erreur, sur le remplissage comme sur les vraies paroles.

## 2. Défauts relevés par Fable

| Défaut | Correction |
|---|---|
| Ouverture un peu vide | dès l'image 0 : pointe jaune visible, cote d'architecte au-dessus du titre (longueur en JetBrains Mono), croix de repère, ligne de construction pointillée tirée par la pointe sous le titre |
| Plis en larges bandes en gros plan | pli à **largeur constante à l'écran** (arête 1,5 px claire / 1,5 px sombre, halo 10 px) + chaque panneau de la feuille légèrement plus clair ou plus sombre (± 2 à 3 %) : la cassure de lumière sans bande |
| Objets trop « icônes » | tasse (bord éclairé, paroi intérieure, ménisque, bulles, reflet de fenêtre, auréole sèche irrégulière), crayon (3 facettes, bois veiné, mine éclairée, virole cannelée), clé (dégradé laiton, biseau, dents), note (coin relevé, traits au stylo), ruban translucide aux bouts déchirés |
| Espacement irrégulier du refrain | rangs composés d'un bloc : **même corps pour tous les rangs** (le plus grand qui fait tenir chaque rang dans 850 px), **même espace entre tous les mots** (0,27 em), rangs centrés sur x 512, vague aplatie (amplitude 4 px au lieu de 8) pour que les mots rigides ne penchent plus l'un vers l'autre |
| Stries du flou de mouvement | voir § 1 |

## 3. Écarts au concept (et pourquoi)

- **Virage en épingle en 3 temps** au lieu de 2 (confort, mesuré) ; les autres virages restent à 1,3–1,5 temps.
- **Cadrage 780 px** au lieu de 820 (zone sûre tenue avec la dérive et la poussée).
- **Planchers de corps** : 104 px (passage rapide) devient 92 px quand tout le cadrage dépasse 4,5 mots/s ; la pente droite de la voile
  (98–100 px) et le premier groupe de la vague (93–95 px) sont dans ce cas.
- **Courbe des virages** `(.5,0,.3,1)` et creux de zoom 30 % (au lieu de `(.6,0,.25,1)` et 20 %).
- **Annotations accrochées à la mise en page** (croix à côté du dernier mot de l'unité, fanion et boucle autour de la ligne) au lieu de
  coordonnées en dur : indispensable pour que la version aux vraies paroles reste juste.
- **Refrain** : rangs centrés et corps commun (le concept avait 88 / 78 / 88 px et des rangs décalés).
- **Corps du refrain** : corps commun = le plus grand qui fait tenir chaque rang dans 850 px : 81,8 px sur le remplissage, mais **71,5 px avec les vraies paroles** (rang plus long), sous les 78 px de la règle 7 du concept. Lisible dans l'image finale ; à corriger si besoin en coupant le rang en deux ou en élargissant à 900 px.
- **Repères d'architecte** autour du titre : ajout (défaut « ouverture vide »).
- **`check.py`** : la durée admise passe à 60 s pour la famille `paroles` (l'extrait va jusqu'au refrain, 32,6 s).
- Non fait : encre qui bave dans le papier, refrain qui finit par couvrir toute la mer (le bas de la feuille reste peu rempli),
  français et arabe (spécifiés dans `identity.md`, pas codés), test de reconnaissance.

## 4. Version aux vraies paroles (hors dépôt)

`~/git/StudioVisualIdentity-sources/lyrics-claudes-plan/chemin.paroles.json` : mêmes temps et cadrages, mots réels (titre, couplets,
refrain). Au-delà de 19,5 s les mots et les temps viennent de la transcription automatique, **non vérifiés à l'oreille**. Rendue par
lien symbolique dans `tmp/` du short (ignoré par git). Sorties : `chemin-paroles-muette.mp4` et `apercu_chemin_avec_son.mp4`
(audio local mixé), dans ce dossier hors dépôt ; rien de ces fichiers n'est versionné.
