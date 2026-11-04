# Recette — short **explicatif** dans l'identité Labo Néon

Référence : `out/shorts/neon-lab__explicatif__lune-meme-face/` (16 s, three.js + OpenCV, champ GLSL partagé).

**Pour un short explicatif dans cette identité :**

- **Ouvrir par** (0–1 s) : la question en titre (Space Grotesk 700, 100 px, mot-clé en cyan) qui glisse dès 0,05 s (`glide` outExpo 0,6 s), tag `LABO/0X · MOT` ; la scène 3D déjà lumineuse avec impulsion de bloom (0,62 → 1,52) et **dolly-in outExpo 2,4 s**. Whoosh + carillon à 0 s.
- **Structurer en** 3 beats calés sur la noire de 0,75 s (80 bpm) :
  1. **Hypothèse écartée** (≈ 3,75 s) : titre court magenta (« **Sans** rotation ? »), objet fantôme magenta qui montre ce qui se passerait, légende mono fixe + filet (`FACE CACHÉE`).
  2. **Preuve** (≈ 4,5 s) : titre-équation lime (« 1 rotation = 1 orbite »), deux arcs de progression synchrones (cyan = révolution, lime = rotation), compteur mono `JOUR 00,0 → 27,3` ; clics à chaque double-croche, riser vers la chute.
  3. **Cause** (≈ 3,25 s) : titre « Verrouillée par **marée** », la donnée symétrique mono (`ROTATION 27,3 j = RÉVOLUTION 27,3 j`), une ligne de corps 56 px, effet visuel exagéré et signalé (renflement).
  Chaque changement de beat = `pulse-flash` (0,35 s) + `glide` des textes, sortie inExpo 0,3 s.
- **Fermer par** : tenue 2–3 s sur la donnée-clé lime, poussée de caméra −0,9 u (inOutSine), carillon + swell ; pas de fondu au noir.
- **Exactitude** : faits vérifiés (27,3 j = période sidérale, rotation = révolution) ; échelles et vitesses non réalistes indiquées dans `short.json`.
- **Budget** : three.js + UnrealBloom ≈ 60 s / 100 frames, + OpenCV ≈ 32 s / 100 frames.
- **Voix** : Orus (documentaire), une phrase par beat, ≤ 2,6 mots/s, les chiffres restent à l'écran.

## Variante « simulation + mesure » (Matplotlib)

Référence : `out/shorts/neon-lab__explicatif__effet-papillon-double-pendule/` (15 s, Matplotlib + OpenCV).

- **Ouvrir par** : titre de beat 104 px (« Effet papillon »), donnée mono lime sous le titre (`Δθ = 0,001 rad`), le système simulé déjà en mouvement à 0,5 s.
- **Structurer en** : même grille de beats (0 / 4,5 / 8,25 / 12,0 s) ; zone schéma 640–1250 px ; graphe de mesure 1410–1590 px avec deux repères physiques seulement (`1 mm`, `1 m`, mono 54 px) et la valeur live en lime à droite ; deux objets comparés = cyan (référence, fin, dessus) et magenta (variante, large, dessous) pour rester lisibles superposés.
- **Fermer par** : titre lime (« Imprévisible ») + la donnée chiffrée tirée de la simulation (`×1 000 en 10,0 s`).
- **Physique** : RK4 à pas fixe, paramètres et conditions initiales écrits dans `short.json` ; choisir les conditions initiales par pré-simulation pour caler l'événement sur un beat.

> Voix réellement utilisée pour les shorts de preuve : Fish Audio « Arnold » (`d704cf8f1216490cbfbed89955f0e938`, `s2.1-pro`). Les noms Gemini ci-dessus sont des suggestions historiques de casting par ton.
