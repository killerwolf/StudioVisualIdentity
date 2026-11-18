# Lyrics chemin — technique de rendu conseillée

## Choix : canvas 2D et une caméra à trois paramètres

Tout est à plat et vu à la verticale : la caméra n'a besoin que d'une **translation, d'une rotation et d'une échelle**. Un seul
`<canvas>` 2D suffit, rendu image par image par l'outil du dépôt (`out/tools/render.mjs`, contrat `window.ready` /
`window.renderAt(t)`, pas d'état entre les images). Aucune librairie de plus, rien d'installé hors du dépôt.

| Piste | Verdict |
|---|---|
| **Canvas 2D** (retenu) | Texte vectoriel net à tout zoom (×1 à ×6) sans texture géante ; `ctx.letterSpacing`, mise en forme arabe faite par le navigateur ; maquette déjà faite avec |
| three.js / Babylon (dans le dépôt) | Inutile sans perspective ; texte en texture, donc flou en gros plan ou atlas énorme |
| Godot 4.7.2 (installé dans `~/Applications`) | Une vraie 3D n'apporterait qu'une ombre et une parallaxe d'objets de quelques pixels ; coût : sortir du pipeline `renderAt`, refaire la typographie. À ne rouvrir que si l'on veut une caméra inclinée (ce qui contredit l'idée « à plat ») |
| SVG + GSAP | Possible, mais le flou de mouvement par sous-images coûte cher en SVG |

Mesure sur la maquette (MacBook, Chrome installé, machine non isolée) : 6 images fixes en 4,6 s, dont le chargement de la page. Le
coût par image d'un rendu complet n'a **pas** été mesuré (aucune vidéo rendue à ce stade).

## Ce qui existe déjà : la maquette

`proto/scene.html` (≈ 330 lignes) a produit les images. C'est une **maquette de direction artistique** : données en dur, pas de
fichier de paroles, pas d'audit. À reprendre comme référence de look et de mouvement, pas comme moteur.

```bash
# depuis la racine du dépôt (playwright-core n'est pas dans package.json : npm i --no-save playwright-core)
export SVI_CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
node out/tools/render.mjs out/report/notes/lyrics-chemin/proto/scene.html --stills 0.9,4.6,7.7,24.9,32.5 --stills-dir /tmp/chemin --no-slot
node out/report/notes/lyrics-chemin/proto/dump.mjs > out/report/notes/lyrics-chemin/proto/storyboard-calcule.json
# ?guides=1 à la fin de l'adresse de la scène : zones sûres en surimpression
```

Attention : `npm i <paquet>` retire `playwright-core` de `node_modules` (il n'est pas déclaré) ; le réinstaller avec `--no-save`.

## Architecture proposée pour le moteur

Un moteur partagé `out/shared/chemin-moteur/` (à créer), un épisode = deux fichiers de données.

1. **`dessin.json`** — le dessin, dans le repère de l'image finale (1080×1920) : sommets, arêtes ordonnées (`droite` ou `vague`),
   côté du texte (`dessus` / `dessous`), marges aux deux bouts, bornes de corps, objets posés (type, position, angle), annotations
   rouges, feuille. Un dessin est réutilisable pour plusieurs chansons ; un nouveau dessin = un nouveau fichier, pas du code.
2. **`paroles.json`** — titre, langue, sens d'écriture, BPM, premier temps, puis les lignes : unités `{texte, t, fin}` et, pour
   chaque ligne, l'arête qu'elle occupe. Les cadrages (quelles unités sont montrées ensemble) sont **calculés** par les règles de
   `concept.md` et peuvent être forcés à la main (`cadrages: [[0,1],[2]]`).
3. **Mise en page** (une fois, dans `window.ready`) : pour chaque ligne, corps = `clamp(longueur utile / largeur à 1 em, min, max)`,
   interlettrage pour finir l'arête (0 à 0,15 em, latin seulement), position de chaque **mot** en abscisse curviligne. Les mots sont
   posés **entiers** sur le chemin (tangente au centre du mot) : c'est indispensable pour l'arabe et ça évite les lettres qui se
   chevauchent dans les creux d'une vague.
4. **Caméra** : liste de poses `{x, y, zoom, angle, arrivée, durée, type}` déduite des cadrages ; `camAt(t)` interpole (position en
   linéaire, zoom en logarithme, angle par le plus court chemin, courbes de `concept.md`). Transformation :
   `translate(512, 860) · rotate(−angle) · scale(zoom) · translate(−x, −y)`.
5. **Dessin d'une image** : sol → feuille (dégradé, taches, fibres, quadrillage, plis, cadre) → traits et mots (états : absent,
   pré-posé, en cours d'écriture, frais, sec) → annotations → objets et leurs ombres → vignette et grain en repère écran.
6. **Flou de mouvement** : quand la caméra bouge de plus de 8 px par image à l'écran, moyenner N sous-images réparties sur une
   demi-image (obturateur 180°). Compter N sur le **déplacement du coin le plus rapide** (rotation comprise), une sous-image tous
   les 3 px, 64 au plus. La maquette plafonne à 48 avec une estimation grossière et laisse voir des stries sur les fouettés : à
   corriger.
7. **Audit** (nouvel outil, à écrire) : pour chaque image, projeter la boîte du mot chanté à l'écran et vérifier les règles 1 à 5 de
   `concept.md` (zone sûre, corps ≥ 120 px ou 104 en passage rapide, vitesse au repos, cadrage ≥ 0,5 s, départ après 60 % du mot).
   Vérifier aussi qu'aucun mot n'en recouvre un autre dans l'image finale (boîtes orientées). L'audit doit faire échouer le rendu.

## Détails qui comptent

- **Déterminisme** : bruits à graine fixe générés dans `window.ready` ; aucune fonction du temps réel.
- **Textures attachées au monde** (taches, fibres) dessinées en motif dans le repère du monde : elles grossissent avec le zoom, ce
  qui donne le papier. Le grain fin et la vignette restent en repère écran.
- **Ombres** : `shadowOffset` et `shadowBlur` du canvas ne suivent pas la transformation ; il faut les multiplier par le zoom et
  tourner le décalage de `−angle` pour que l'ombre reste attachée à la lumière du monde.
- **Quadrillage** : épaisseur constante à l'écran (1 px), opacité qui baisse à l'échelle 1 pour ne pas moirer.
- **Encre sèche** : opacité `mix(1, 0,6, clamp((zoom − 1,2) / 1,5))`. Sans cela, une ancienne ligne plus grosse (le titre) domine
  la ligne chantée.
- **Polices** : `S.loadFonts` de `out/tools/lib/svi.js` (Barlow Condensed 700 et 800, JetBrains Mono 400), attendues avant toute
  mesure de largeur. Pour le français, charger le sous-ensemble `latin` (accents compris) ; pour l'arabe, `@fontsource/cairo`
  sous-ensemble `arabic`, `ctx.direction = 'rtl'`, pas de `letterSpacing`.
- **Arabe** : retourner le dessin (`x → 1080 − x`, angles opposés) **avant** la mise en page ; révélation par un masque qui avance
  de droite à gauche ; objets retournés aussi. Non codé, non testé.
- **Son** : la vidéo est muette (le morceau est ajouté dans l'application à la publication). Les temps viennent de `paroles.json`.
- **Photosensibilité** : aucun flash plein cadre ; rien à ajouter.
- **Sortie** : 1080×1920, 30 images/s, H.264 yuv420p, par `render.mjs`. Un rendu complet à la fois, en arrière-plan.

## Ordre de travail conseillé pour l'agent qui code

1. Sortir les données de la maquette en `dessin.json` et `paroles.json` (remplissage), retrouver les 5 images à l'identique.
2. Écrire l'audit, le faire passer sur l'extrait.
3. Rendre 10 s (0 à 10 s : titre, fouetté, virage en épingle) et juger le mouvement **en vidéo** avant d'aller plus loin : c'est le
   point que les images fixes ne prouvent pas.
4. Flou de mouvement propre, puis rendu complet de l'extrait (32,6 s) et mesure du coût.
5. Seulement ensuite : version française, puis arabe en miroir.

## Ce qui reste incertain

- **Le mouvement n'a pas été vu.** Aucune vidéo n'a été rendue : le confort des virages (114° en 2 temps), des fouettés d'un temps et
  du zoom arrière d'une mesure est un pari raisonné, pas un constat. Si c'est trop nerveux : allonger les virages à 3 temps et
  réduire l'inclinaison résiduelle.
- **Temps après 19,5 s** : ils viennent d'une transcription automatique non corrigée à la main (les temps d'avant ont été recalés).
  Les attaques du refrain en particulier (29,2 à 32,1 s) sont à vérifier à l'oreille ; au-delà de 33 s la transcription est
  inutilisable.
- **Durée** : l'extrait fait 32,6 s, un peu plus que les 20 à 30 s demandés, parce que le refrain qui justifie le dessin commence à
  29,2 s.
- **Le bas de la feuille** reste peu rempli sur l'extrait ; sur le morceau entier, le refrain répété doit remplir la mer (rangées
  supplémentaires), ce qui n'est pas dessiné.
- **Corps du texte dans l'image finale** : 36 à 43 px pour les lignes du bateau, sous la règle « 54 px » du dépôt. C'est voulu (ces
  lignes ont déjà été lues en gros plan), mais à faire valider.
- **Un dessin par chanson** : placer les lignes sur les arêtes a été fait à la main (ordre, côtés, marges). Une chanson plus longue
  ou plus bavarde demande un autre dessin ou des arêtes en plus (vagues, nuages, sillage). Rien n'est automatisé.
- **Voisinage** avec les identités existantes (fond bleu, objets à plat) : pas de test de reconnaissance fait.
