# Survol pixel après la passe A+B+C : retouches pour une seule passe (18/11/2026)

Analyse en lecture seule : aucun fichier du dépôt modifié, rien de commité, aucun short rendu en entier.
Les essais sont des images isolées calculées hors dépôt : `essai.py` charge `survol.py` et `video.py` en mémoire et y remplace du texte.

Dossier (noté `FR/`) : `scratchpad de session (hors dépôt, non conservé)`

- Scripts : `FR/measure2.py` (mesures sur les mp4), `FR/essai.py` et `FR/essai2.py` (essais ; les remplacements exacts sont dans `VAR`).
- Mesures brutes : `FR/mesures.txt`.
- Planches : `FR/ESSAI_atoll_avant-apres_1.5_6.5_16.0_18.3.jpg`, `FR/ESSAI_machu_avant-apres_4.5_7.0_9.0_17.5.jpg`, `FR/ESSAI_atoll_cadrages_accroche_final_final-vu-du-nord.jpg`, `FR/CROPS_mer_source-vs-atoll.jpg`, `FR/CROPS_terre_source-vs-machu.jpg`, `FR/CROPS_divers.jpg`, `FR/machu/PAIRE_pique_9.0.jpg`.

## 1. Constat

### Corrigé depuis ce matin

| Écart du matin | État |
|---|---|
| 1. Monde fini et vide | Corrigé pour le relief : crêtes jusqu'à l'horizon à Machu Picchu, autres atolls et hauts-fonds au loin. La mer proche de l'atoll reste vide (retouches 1 et 2). |
| 2 et 8. Brume en plaques, bande crème | Corrigé : 6 paliers vers un bleu pâle, plus de plaque gris-vert ni de bande crème. |
| 3 et 6. Cubes, bascules de détail | Corrigé : murs lointains gris, plus de bascule vert / gris visible dans les images extraites. |
| 5. Textes | Corrigé : un cartouche à la fois. |
| 4 et 10. Caméra, cadrage | Corrigé à Machu Picchu. L'atoll bouge encore peu (retouche 4). |
| 7. Éclairage | Partiel : ombres portées du relief présentes, mais ombres bleu nuit dans la forêt (retouche 3). |
| 9. Végétation | Partiel : forêt en rangs réguliers sur fond très sombre (retouche 3). |

### Mesures (fichiers finaux, 30 i/s, 1 pixel par gros pixel)

| Mesure | Source (plans aériens et poursuite) | Atoll | Machu Picchu |
|---|---|---|---|
| Pixels qui changent d'une image à l'autre (seuil 24) | 26–33 % | **6,5 %** (coupe 3,6 %) | 21,6 % |
| Scintillement A-B-A, short entier | 2,4 % (1,8–3,4 selon le plan) | 0,87 % | 2,00 % |
| Scintillement A-B-A, pire fenêtre | 3,4 % | 1,8 % (bascule) | **4,3 %** (piqué), 3,4 % (remontée) |
| Pixels sombres (luminance < 70) | 3–6 % | 2 % | **22 %** (28 % au piqué) |
| Ombres de nuages sur l'eau (image native) | 3–6 % en vue aérienne | 0–0,7 % | sans objet |
| Densité de contours (voisin horizontal différent) | 9–15 % | 6–8 % | 14–21 % |

Lecture :
- Le scintillement n'est plus le problème : Machu Picchu est au niveau de la source, sauf 2 s de piqué à 4,3 %. Ma mesure n'est pas celle de la note du studio (qui donne 4,0 % pour la source et 7,3 % au piqué) ; les deux disent que le piqué dépasse la source, la mienne de peu.
- L'atoll est 4 à 5 fois plus statique que la source.
- Machu Picchu est 4 à 7 fois plus sombre que la source : forêt `FOREST` et ombres `INK` (4,4 à 10,6 % de l'écran en bleu nuit selon l'image).
- Ce qui sépare le plus les shorts de la source n'est plus le moteur. Ce sont trois motifs : les nuages en coton avec leur ombre, les traits d'écume sur la mer, les bouquets d'arbres sombres sur une terre claire.

Je n'utilise pas la part d'aplats comme critère : sur un mp4, le bruit de compression la fausse (41,7 % sur le fichier de l'atoll contre 76,6 % sur l'image native au même calcul).

## 2. Retouches, classées par impact sur la ressemblance de style

Les essais montrent la direction, pas un réglage final. Coûts : le temps par image des essais est resté égal ou inférieur à celui de l'état actuel (atoll 0,7–1,4 s contre 0,7–1,7 s ; Machu Picchu 2,3–2,5 s contre 2,2–3,4 s), sur 5 images par variante et sous charge 3–4. Aucune retouche ne devrait donc allonger le rendu de façon sensible ; ce n'est pas mesuré sur un short entier.

### 1. Nuages : plus gros, plus nombreux, près de la caméra, avec leur ombre (les deux shorts)

- **Problème.** La source a 10 à 25 tas de coton par image, gros (25 à 40 pixels natifs), chacun avec une ombre sombre nette. Chez nous : 2 à 6 petits nuages, surtout à l'horizon, ombres quasi absentes (0–0,7 % de l'écran contre 3–6 %). Le bas des boules est hachuré une ligne sur deux, ce qui se lit comme un store. Voir `FR/atoll/row1.jpg` (1,5 / 3,5 / 6,5 / 12,5 s), `FR/machu/row1.jpg`, `FR/CROPS_mer_source-vs-atoll.jpg`.
- **Retouche.**
  - `video.py` de l'atoll, `_clouds()` : rayon `uniform(8.0, 13.0)` → `(11.0, 20.0)` ; 70 → 100 nuages ; espacement 40 → 36. Garder l'exclusion de 88 unités autour de l'anneau et la marge caméra.
  - `video.py` de Machu Picchu, `_clouds()` : rayon `(7.0, 11.0) * K` → `(9.0, 16.0) * K` ; 40 → 60 nuages ; `far = len(out) >= 14` → `>= 24`.
  - `survol.py`, `draw_clouds` : remplacer la hachure `jj % 2` par un modelé tramé en damier, limité au tiers bas droit, plus un croissant plein `HATCH` tout en bas. Lignes essayées : `lower = (v > 0.38 - 0.45 * u)`, `col[lower & ((ii + jj) % 2 == 0)] = HA`, `col[(v > 0.72 - 0.45 * u) & (ay >= 3)] = HA`.
  - Machu Picchu : les ombres de nuages ne se voient pas sur le relief. Vérifier `cloud_shadow_disks(..., ground_z=CITY_Z * 0.6)` et la table `shadow` ; si l'ombre tombe sur la forêt sombre, la retouche 3 la rendra visible.
- **Essai.** `FR/ESSAI_atoll_avant-apres_1.5_6.5_16.0_18.3.jpg` et `FR/ESSAI_machu_avant-apres_4.5_7.0_9.0_17.5.jpg`, rangée du bas.
- **Critère.** Sur images natives sans cartouche : `CLOUD` + `HATCH` + `CLOUD_RIM` entre 3 et 8 % de l'écran en médiane (essai : 2–4,5 %) ; à l'atoll, `SH_WATER` entre 2 et 6 % (essai : 0,7–6,5 %) ; au moins 6 nuages visibles sur 80 % des images hors plan de coupe.
- **Risques.** Un nuage peut passer devant le sujet, une épingle ou la coupe (vu sur l'essai de cadrage nord) : contrôler les images de 4 à 15 s et écarter les nuages fautifs par leur graine. La limite « ≤ 4 nuages » du challenge (C15) est déjà levée, mais la validation du propriétaire reste due.
- **Coût.** Nul à l'essai.

### 2. Mer de l'atoll : des traits d'écume orientés au lieu de points blancs

- **Problème.** La mer occupe 50 à 85 % de l'image. La source la couvre de traits courts, fins, tous dans le même sens, bleu clair à blanc. Nous avons des points blancs isolés de 1 à 2 pixels, qui se lisent comme de la neige ou un ciel étoilé. Voir `FR/CROPS_mer_source-vs-atoll.jpg` (vignettes 1 et 2 : source ; 3 : atoll à 1,5 s).
- **Retouche**, `video.py` de l'atoll, aux trois endroits qui sèment l'écume, avec le même hachage pour qu'il n'y ait pas de couture au bord de la fenêtre fine :
  - `static()`, mer extérieure : `foam = (S.hash01(xx, yy // 4, 50 + ph) < 0.016) & (dep > 9)`, peint en `LAGOON`, la case de tête en `FOAM` ;
  - `fine_fields()`, `out['foam']` : `S.hash01(floor(X), floor(Y / 4), 50 + ph) < 0.016`, restreint à la moitié de la cellule en largeur (`(floor(X * FK) % FK) < 2`) ;
  - `outside_tile()` : même règle, en `LAGOON`.
  - Soit des traits de 4 unités de long sur 0,5 à 1 de large, alignés sur l'axe Y du monde.
- **Essai.** `FR/ESSAI_atoll_avant-apres_1.5_6.5_16.0_18.3.jpg`, rangée du bas.
- **Critère.** Sur une image native à 1,5 s : au moins 80 % des taches d'écume du large font 3 pixels ou plus dans leur grand axe, et aucune n'est un pixel isolé dans la moitié basse. Scintillement A-B-A de l'atoll ≤ 2,5 % sur le short entier (aujourd'hui 0,87 % ; source 2,4 %).
- **Risques.** Les deux phases d'écume alternent : un trait de 7 pixels qui s'allume et s'éteint se voit plus qu'un point. Si le critère A-B-A est dépassé, garder une seule phase et faire glisser les traits. À l'essai, les traits s'arrêtent net au-delà d'une certaine distance (réduction de carte) : vérifier que cette limite ne balaie pas l'écran quand la caméra avance, sinon baisser la densité avec la distance.
- **Coût.** Nul.

### 3. Forêt de Machu Picchu : plus de bleu nuit, des bouquets et des clairières

- **Problème.** Le versant boisé occupe 40 à 50 % de l'image du début à 9 s puis de 15 s à la fin. C'est une trame de boules claires en rangs sur un sol `FOREST`, rayé d'ombres `INK` (bleu nuit) : 4,4 à 10,6 % de l'écran en `INK`, 22 % de pixels sombres contre 3–6 % dans la source. La source fait l'inverse : des bouquets d'arbres sombres sur une terre claire, avec une ombre d'un ton plus foncé, jamais bleue. Voir `FR/CROPS_terre_source-vs-machu.jpg` (vignettes 1–2 : source ; 3 : 7,0 s) et `FR/machu/PAIRE_pique_9.0.jpg`.
- **Cause dans le code.** `video.py`, table `shadow` : `'FOREST': 'INK'`. Toute ombre d'arbre ou de relief sur le sol de forêt devient bleu nuit.
- **Retouche**, `video.py` de Machu Picchu :
  - ajouter une couleur de biome `FOREST_SH` (`#0F3620` à l'essai) ; `shadow` : `'FOREST': 'FOREST_SH'`, `'FOREST_SH': 'INK'` ; lui donner la rampe de brume de `INK` ;
  - `fine_colours()`, bloc « forêt variée » : sol `GRASS_D` au lieu de `FOREST` ; clairières `GRASS_M` plus fréquentes (seuil du bruit 0,55 → 0,40) ; sous-bois `FOREST` seulement par grandes plages (bruit d'échelle 14, seuil −0,35) ;
  - `world()`, `scatter_trees` : `density=0.5, r=(0.9, 2.2), cluster=(n2 - 0.02) * 3.2` pour des bouquets séparés par des vides.
  - Pour atteindre le critère, aller plus loin que mon essai : dans `nat` (hors zone `wild`) et dans la carte grossière, réserver `FOREST` aux pieds de marche.
- **Essai.** `FR/ESSAI_machu_avant-apres_4.5_7.0_9.0_17.5.jpg`, rangée du bas. Une première variante (arbres sombres sur sol moyen, `FR/essais/MP_A-vs-B.jpg`) a échoué : tout se fond et les pixels sombres montent à 27–35 %. Ne pas la reprendre.
- **Critère.** `INK` ≤ 3 % de l'écran hors plan de coupe (essai : 2,6–2,9 %, sauf 6,6 % à 9,0 s où il vient des joints de pierre). Pixels sombres (luminance < 70) ≤ 15 % en survol : **mon essai n'atteint que 19,4–20,5 %**, d'où la dernière ligne de la retouche. Reconnaissance mesurée : le plus proche voisin de Machu Picchu doit rester l'atoll.
- **Risques.** Les terrasses claires se détachent moins d'une forêt éclaircie : garder au moins un ton d'écart (terrasses `GRASS_L` / `GRASS_M`, forêt `GRASS_D`). Une couleur de plus dans la palette déclarée (41) ; le compte par image reste ≤ 32 (essai : 19–25).
- **Coût.** Nul à l'essai.

### 4. Caméra de l'atoll : une accroche qui avance, un plan final large

- **Problème.** L'atoll change 6,5 % de ses pixels par image contre 26–33 % pour la source. De 0 à 2,9 s la caméra n'avance que de 38 unités, et le bas de l'image est une mer vide. Le plan final sort l'anneau par le bas et coupe la maquette au bord du cadre : `FR/atoll/row2.jpg`, 16,5 et 18,3 s.
- **Retouche**, `video.py` de l'atoll, `cam_path`, **sans déplacer aucun temps de clé** :
  - clé 0,0 s : `ty=C0 - 110, dist=300, pitch=33` (au lieu de `C0 - 40`, 245, 40) : la caméra part de plus loin, plus bas, avec l'horizon et les autres atolls en haut ;
  - clé 18,6 s : `tx=C0 - 6, ty=C0 + 40, dist=310, pitch=30, roll=-10`, lacet inchangé (−22) : anneau entier, coupe visible, horizon et nuages au tiers haut ;
  - clés de 3,9 à 13,4 s (plan de coupe) : ne pas toucher.
- **Essai.** `FR/ESSAI_atoll_cadrages_accroche_final_final-vu-du-nord.jpg`, vignettes 1 et 2. La vignette 3 (vue du nord) est plus propre mais cache la coupe au moment où le cartouche dit « basalte trouvé dessous en 1952 » : ne pas la retenir.
- **Critère.** Pixels qui changent par image ≥ 12 % en moyenne de 0 à 2,9 s et de 15 à 18,6 s (aujourd'hui 6,5 % et 11,4 %). À 18,5 s, l'anneau entier est dans le cadre et l'horizon se trouve entre 8 et 20 % de la hauteur. `--preflight` : marge caméra / relief ≥ 40.
- **Risques.** `_clouds()` écarte les nuages selon la trajectoire : les nuages changent donc de place, à revoir avec la retouche 1. Le cartouche d'accroche tombe sur l'horizon : vérifier son contraste. La frégate et son ombre sont calées sur l'ancien cadrage.
- **Coût.** Nul : à 310 unités, l'image de 18,3 s se calcule dans le même temps.

### 5. Pain de sucre de Machu Picchu : un sommet, pas un obélisque

- **Problème.** Le pic derrière la cité est une aiguille grise 3 à 4 fois plus haute que large, qui se lit comme une tour ou une cheminée. Il est dans le cadre de 0 à 9 s et de 14 à 18,8 s. Voir `FR/CROPS_divers.jpg` (vignette 3) et `FR/machu/row2.jpg`.
- **Retouche**, `video.py` de Machu Picchu, `site_height()` : `gauss(xx, yy, C0 + 4 * K, C0 + 60 * K, 15 * K, 15 * K, 108 * K)` → `(…, 25 * K, 21 * K, 104 * K)`. Monter aussi le seuil du granite sur ce sommet (`top > 100 * K` → `112 * K` environ) pour que ses flancs soient boisés et seul le haut rocheux.
- **Essai.** `FR/ESSAI_machu_avant-apres_4.5_7.0_9.0_17.5.jpg`, colonnes 1 et 4 : le pic passe d'une aiguille à un cône. Le seuil du granite n'a pas été essayé.
- **Critère.** À 0,6 s et 17,5 s, largeur du pic à mi-hauteur ≥ 40 % de sa hauteur visible ; granite ≤ 50 % de sa surface.
- **Risques.** Le pic élargi mord sur la vallée et la rivière au nord, et peut s'approcher de la caméra : relancer `--preflight` (marge actuelle 41,6). La première rivière se voit un peu moins à 0,6 s.
- **Coût.** Nul.

### 6. Finitions : rampe du ciel et socle de la coupe

- **Problème a.** Avec l'horizon en haut du cadre, la bande de ciel visible ne couvre que 0 à 8° d'élévation : elle reste blanchâtre (`#D9ECF4` à Machu Picchu sur toute sa hauteur, contre `#9DD1EB` → `#C7E9F7` dans la source).
- **Retouche a.** Dans les deux `video.py`, passer au `Renderer` : `sky=[(0.4, 'HAZE'), (1.2, 'SKY_1'), (2.4, 'SKY_LO'), (4.0, 'SKY_2'), (6.5, 'SKY_MID'), (10.0, 'SKY_4'), (90.0, 'SKY_HI')]`. Aucun changement du moteur.
- **Problème b.** Le socle de la maquette de l'atoll est un damier aléatoire basalte / roche qui ressemble à un QR code et attire l'œil de 14 à 18,6 s : `FR/CROPS_mer_source-vs-atoll.jpg`, vignette 4.
- **Retouche b.** `video.py` de l'atoll, `build_world()` : part de dalles `< 0.33` → `< 0.08`.
- **Essai.** Les deux sont dans les planches d'essai (ciel : colonnes 2 et 3 ; socle : atoll à 16,0 s).
- **Critère.** Au moins 3 paliers de ciel visibles quand le ciel occupe plus de 5 % de l'image. Sur le socle, pas plus d'une dalle sur dix d'une autre teinte.
- **Risques.** Le dernier palier de brume doit rester égal au bas du ciel (`HAZE`), c'est le cas. Les dalles ont été introduites contre un scintillement de rayures : ne pas revenir à des rayures.
- **Coût.** Nul.

## 3. Ce qu'il ne faut pas toucher

- **Le moteur de profondeur** : lancer de rayons, 4 rayons par pixel et vote, carte fine, pas sûrs, terrasses, ombres portées du relief. C'est la signature et c'est ce qui a supprimé les bascules.
- **La brume en 6 paliers** et sa teinte bleu pâle, y compris la distance de référence bornée.
- **Les cartouches** : un à la fois, leurs textes, leurs temps. La voix et `narration.json` ne bougent pas ; aucun temps de clé de caméra ne bouge.
- **La caméra de Machu Picchu**, piqué et remontée ralentis compris. Son scintillement est au niveau de la source ; l'accélérer le ferait remonter.
- **Les plans de coupe** des deux shorts (atoll 3,9–13,4 s, Machu Picchu 10–13,4 s) : ils sont lisibles et portent le propos.
- **Les terrasses agricoles, les murs appareillés et la cité** de Machu Picchu ; l'anneau, le lagon et le récif de l'atoll.
- **Pas d'île verte ni d'archipel** autour de l'atoll, pas d'élément de jeu, pas de HUD : la mer se remplit avec des nuages, des ombres, de l'écume et des hauts-fonds, rien d'autre.
- **Ne pas chercher à baisser encore le scintillement** par un sur-échantillonnage plus fort : il coûterait un multiple du rendu pour un défaut qui n'est plus visible.
- **Le rendu reste sur CPU.**

## 4. Limites de cette analyse

- Les essais portent sur 4 à 5 images par short, pas sur le mouvement. Les critères de scintillement et de mouvement ne pourront être vérifiés que sur les rendus complets, avec `FR/measure2.py`.
- Les seuils chiffrés (nuages 3–8 %, pixels sombres ≤ 15 %, mouvement ≥ 12 %) sont des cibles que je fixe d'après la source ; ils ne viennent pas d'un test de spectateurs.
- Le « treillis » visible sur un versant proche, au bord gauche à 4,5 s et 17,5 s de Machu Picchu (`FR/CROPS_divers.jpg`, vignette 1), n'a pas été diagnostiqué. Il reste hors de cette liste.
