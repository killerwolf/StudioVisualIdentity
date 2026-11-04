# Brut Mème — identité visuelle

## Nom
**Brut Mème** (`brut-meme`, v1.0.0). Affiche brutaliste qui crie, montée comme un mème : noir, jaune « chantier », rouge, typo condensée qui remplit l'écran, coupes franches sur le temps.

## Promesse en une phrase
Un fait ou un défi par coupe, en lettres géantes qui claquent sur le beat : impossible de scroller sans lire.

## Mood & références de genre
Énergie brute, sarcasme bienveillant, contraste maximal, zéro dégradé, zéro douceur. Références de genre (aucune œuvre copiée) : affiche brutaliste / suisse sous stéroïdes, compilation virale « tu savais que… », panneaux de chantier, étiquettes de promo de supermarché, stickers collés de travers, télé-réalité « chrono ». Le ton : l'animateur qui te met au défi, pas le professeur.
**Distincte de pixel-arcade** : pas de pixel art, pas de bleu nuit, pas de Press Start 2P, pas de physique ni de course ; ici tout est aplat vectoriel net, typo condensée géante et montage au cut.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Valeur | Usage |
|---|---|---|
| Fond | `#111111` | fond par défaut (jamais #000 pur : l'ombre dure #000 doit se voir) |
| Surface | `#FFE600` | fond « acte 2 » (inversion), surligneurs, blocs, jauge |
| Accent 1 | `#FFE600` jaune | mot-clé, chiffre géant sur noir, anneau du compte à rebours |
| Accent 2 | `#FF2D2D` rouge | tags, stickers ronds, chiffre « grave » (décès), bloc de réponse |
| Accent 3 | `#FFFFFF` blanc | texte courant sur noir, anneau des stickers |
| Texte | `#FFFFFF` sur noir / `#111111` sur jaune | contraste ≥ 15:1 (blanc/#111) et ≥ 14:1 (#111/jaune) |
| Danger | `#FF2D2D` | STOP, erreurs, décès |
| Succès | `#FFE600` | bonne réponse, « TEMPS ÉCOULÉ » |
| Trame | `#262626` sur noir, `#E8D000` sur jaune | texture de points, jamais porteuse d'info |
Le rouge n'est jamais utilisé pour du texte < 90 px sur noir (contraste 4,6:1 seulement) ; en petit, rouge = fond de tag avec texte blanc.

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Display — Anton 400** (`@fontsource/anton`), capitales, interlignage 0,86, interlettrage −2 px. Taille **auto-fit** : chaque mot-titre est ajusté pour remplir **900 px de large** (x 90–990 recentré dans 60–960), plafond 330–600 px selon la scène. Tailles réellement obtenues : 158 px (EN COMMENTAIRE) à 470 px (BLEU). Chiffres géants : idem, `font-variant-numeric: tabular-nums`.
- **Titre de section — Anton 132 px** dans un surligneur (jaune/texte noir sur fond noir ; noir/texte jaune sur fond jaune).
- **Corps — Inter 900, 56–64 px**, interlettrage −2 px : une seule ligne d'unité ou d'explication (« bébés sont nés », « VA PLUS VITE QUE »).
- **Tag — Inter 900 56 px** blanc sur rouge, padding 12/20 px, toujours à (60, 236) : « TEST DES 3 SECONDES », « ROUND 2/3 · PLUS VITE », « ● EN DIRECT · 07,3 S ».
- **Sticker — Inter 900 58–66 px**, interlignage 0,98, centré dans un disque rouge.
- Piège : un titre ajusté doit être en `white-space: nowrap`, sinon la mesure se fait sur un seul mot et le titre déborde (vérifié).

## Formes & matières
Aplats purs + **ombres dures** décalées (10–16 px, #000 ; blanc ou rouge quand le fond est noir). Formes récurrentes, toutes dessinées en PixiJS Graphics ou en CSS :
- **tag** rectangle rouge ; **surligneur** bloc jaune collé derrière le mot ;
- **sticker rond** rouge, bordure #111 8 px + anneau blanc 7 px + ombre dure, tourné de −10° ;
- **starburst** 10–12 pointes (jaune ou noir) pour « /3 », « ?! » ;
- **blocs-réponses** pleins dans la couleur à nommer ;
- **jauge rubalise** (rayures diagonales jaune/noir 34 px, cadre blanc) à y 1556 = progression du short, présente du début à la fin ;
- **trame de points** 24 px en diagonale (pré-rendue une fois en texture, teintée selon le fond) ;
- pictos plats : pastilles, carrés, éclairs zigzag, enveloppes, orbite pointillée, cœur en béziers.
Jamais : dégradé, flou, transparence décorative, 3D, pixel art, photo.

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
- **Beat** : 120 bpm (0,5 s). Chaque scène commence sur un temps, chaque événement important tombe sur un temps ou un demi-temps.
- **punch-in** : à chaque cut, toute la caméra passe de **scale 1,15 à 1 en 3 frames** (courbe (1−k)²) ; force 1 sur les cuts de scène, 0,25–0,5 sur les tics/stickers.
- **slam** (GSAP, `power4.in`, 0,1 s) : sticker ou mot qui arrive de scale 2,4 + 18° vers 1 et −10°, suivi d'un **shake** seedé 8–18 px amorti en 0,12 s (fenêtre 0,45 s).
- **slide-snap** (GSAP, `power4.out`, 0,1 s) : ligne/label qui entre de ±1 100 px.
- **rescale** (GSAP, `power4.out`, 0,1 s) : premier titre d'une scène de 1,6 à 1.
- **stagger** : 0,2 s entre lignes de récap (chaque ligne = un mini-cut).
- Compteurs : valeur = débit × temps écoulé, mise à jour à chaque frame (pas d'easing sur les chiffres).
- **On ne fait jamais** : fondu enchaîné, easing doux > 0,2 s, mouvement flottant, rotation continue, parallaxe, **flash plein cadre**.
- **Photosensibilité** : au plus une inversion de fond noir↔jaune toutes les 1,6 s (≤ 1 grand changement de luminance par seconde, très en dessous du seuil de 3 flashs/s) ; les changements rapides (éclairs, tics) restent dans de petites zones (< 25 % de l'écran) et ≤ 2/s ; le shake est un déplacement ≤ 18 px, jamais un clignotement. Éclairs dessinés en zigzag, jamais d'éclair blanc plein écran.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
2D frontale, orthographique, plan fixe plein cadre. Seuls mouvements : **punch-in** (zoom 1,15→1 en 3 frames, origine (540, 900)) et **shake**. Pas de travelling, pas de profondeur de champ, pas de perspective. Le « cadrage » est typographique : le mot clé occupe toute la largeur utile.

## Transitions (liste nommée, durée, quand les utiliser)
| Nom | Durée | Quand |
|---|---|---|
| `hard-cut` | 0 | tout changement de scène, sur le temps |
| `punch-cut` | 0,1 s (3 frames) | cut + punch-in + `impact` sonore : début de scène, STOP, révélation |
| `slam` | 0,1 s | sticker / mot-clé + shake + `pop` |
| `slide-snap` | 0,1 s | 2e ligne d'un titre, lignes de récap (stagger 0,2 s), `whoosh` |
| `bg-invert` | 0 | fond noir↔jaune pour un changement d'acte (règle, CTA, récap) ; max 1 / 1,6 s |
Aucun `xfade` ffmpeg : l'identité est 100 % coupes franches (les shorts sont rendus d'un seul tenant).

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
1. **Hook 0–1 s** : la frame 0 montre déjà le mot géant + le tag rouge ; un sticker slam à 0,4–0,6 s.
2. **Règle / cadre (1–2,2 s)** : une phrase en 2–3 lignes géantes, souvent en `bg-invert` jaune.
3. **Développement (2–12 s)** : une idée par scène de 1,5–2,2 s (3–4 temps) : cut → label → chiffre/mot géant → sticker au temps suivant ; accélération progressive (tics 0,5 → 0,4 → 0,3 s).
4. **Chute (≈ 8,5–13,5 s)** : explication en une ligne ou récap en liste (stagger 0,2 s).
5. **Fin (dernières 2–3 s)** : CTA en question directe (« TON SCORE EN COMMENTAIRE », « ET TOI, T'AS FAIT QUOI ? »), sticker + starburst, fin propre tenue ≥ 1,5 s. Pas de boucle.
Durée 15,5–16 s.

## Zones sûres
Haut 220 px, bas 320 px, droite 120 px, gauche 60 px. Contenu utile x 60–960, y 236–1590 : tag à y 236, titres ajustés à 900 px, stickers dans (560–960, 1030–1540), jauge à y 1556–1586. La zone y > 1600 ne contient que la trame.

## Librairies recommandées et pourquoi
- **PixiJS 8.22** : toutes les formes (fond, trame en texture, blocs à ombre dure, anneau de compte à rebours, starburst, éclairs, orbite, cœur, jauge rubalise) dans un seul `Graphics` vidé à chaque frame ; headless : `await app.init({preserveDrawingBuffer:true, autoStart:false})` dans `window.ready`, `app.ticker.stop()`, `app.renderer.render(app.stage)` dans `renderAt`. Coût de scène ≈ 2 ms/frame : c'est la capture qui coûte.
- **GSAP 3.15** : slams / slides / rescales des textes DOM (Anton/Inter via @fontsource) dans une timeline en pause, `tl.seek(t, false)` ; `fromTo` avec `immediateRender:false`, états initiaux cachés en CSS (`.later{visibility:hidden}` + `autoAlpha`). GSAP peut aussi tweener un objet proxy lu par Pixi (starburst « /3 »).
- Le texte reste en **DOM** (net, crénage correct, ajustement automatique) ; la caméra (punch/shake) est calculée en JS et appliquée au conteneur commun DOM+canvas.
- Moteur partagé : `src/brut.js` (copié à l'identique dans chaque short).

## Familles de contenus adaptées / inadaptées
- **Adaptées** : engagement (défis, tests, quiz chronométrés, votes), evenements (chiffres du monde, compteurs, comptes à rebours, « ce qui se passe pendant… »), listes/tops, faits surprenants, annonces.
- **Possibles avec prudence** : explicatif très court (une seule idée), géographie en chiffres.
- **Inadaptées** : enfants (trop agressif), histoire ou sujets graves/émotionnels (le ton mème banalise), abstrait contemplatif, tout ce qui a besoin d'images détaillées ou de lenteur.

## Shorts de preuve (chemins)
- `out/shorts/brut-meme__engagement__test-des-3-secondes-stroop/` — 15,5 s, PixiJS + GSAP, effet Stroop en 3 rounds qui accélèrent.
- `out/shorts/brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde/` — 16,0 s, PixiJS + GSAP, compteurs live calés sur l'horloge du short.

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)

> **Voix réellement utilisée pour tous les shorts : Fish Audio « Arnold »** (`d704cf8f1216490cbfbed89955f0e938`, modèle `s2.1-pro`, conteur masculin FR). Les noms de voix Gemini (Orus, Kore, Aoede…) qui suivent sont des suggestions historiques de casting par ton : Gemini a été abandonné (quota). Le placement, le débit et les silences décrits ici restent valables.

Voix **Fenrir** (énergique) ou **Puck** (enjouée), débit 2,6 mots/s, phrases de 1–7 mots qui doublent le mot-clé à l'écran (« Rouge ! », « Plus vite ! », « Et toi, t'as fait quoi ? »). Elle parle dans les 0,1–0,3 s après chaque cut et se tait pendant les tics de compte à rebours (le son porte le rythme). Une seule phrase longue autorisée (l'explication, ~4 s). Le visuel n'affiche que des mots-clés et des chiffres : la voix peut ajouter le « pourquoi » sans conflit. Musique `pulse` 120 bpm à −18 dB sous la voix ; impacts courts qui ne masquent pas la parole.

## Risques et limites
- **Photosensibilité** : les inversions noir/jaune sont le premier risque ; respecter ≤ 1 inversion / 1,6 s et ne jamais faire de flash plein cadre (cf. Langage de mouvement).
- **Fatigue** : 15 s de cris visuels suffisent ; au-delà de 20 s le procédé lasse.
- **Ton** : le registre mème peut banaliser un sujet grave (les décès sont traités en carrés neutres, sans emoji ni blague).
- **Chiffres** : les compteurs « live » sont des moyennes (débit × temps) ; toujours écrire « ≈ / environ ».
- **Proximité** avec swiss-data (aplats + chiffres) : la différence tient à la typo condensée géante, aux stickers, au punch-in et au jaune/noir ; ne pas glisser vers une grille sobre.
- **Rendu** : 49,8 s / 100 frames sous contention (load ≈ 17–23) ; la capture domine (scène ≈ 0,2 s / 100 frames).
