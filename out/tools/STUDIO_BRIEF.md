# Brief studio — Phase 2 & 3 (un sous-agent = une identité)

Tu es le studio d'**une** identité visuelle. Tu livres **uniquement** dans :
- `out/identities/<slug>/` (identity.md, tokens.json, poster.jpg, contact-sheet.jpg, recipes/<famille>.md)
- `out/shorts/<slug>__<famille>__<sujet-slug>/` (un dossier par short)
- `out/library-cards/_drafts/<slug>__<lib>.json` (brouillons de cartes librairie ; l'orchestrateur les fusionne)
Tu **ne modifies jamais** `out/tools/`, ni les fichiers d'une autre identité, ni `out/report/` (sauf `out/report/notes/<slug>.md`, ton journal : décisions horodatées, échecs, temps mesurés). Ne fais **aucun** commit git.

Racine du dépôt : `/home/user/StudioVisualIdentity`. Toutes les commandes se lancent depuis la racine.

## Harnais (déjà testé — lis l'en-tête de chaque fichier)
| Outil | Rôle |
|---|---|
| `node out/tools/render.mjs <scene.html> --out <x.mp4> --duration 15` | rendu vidéo muet 1080×1920 30 fps (contrat `window.ready` / `window.renderAt(t)` / `window.SEQUENTIAL`) |
| `node out/tools/render.mjs <scene.html> --stills 0.5,4,9,13 --stills-dir <dir>` | stills JPEG aux temps donnés |
| `out/tools/lib/svi.js` | helpers ES module : `rng`, `noise3`, `ease.*`, `cubicBezier`, `seg`, `loadFonts`, `SAFE`, `installContract` |
| `out/tools/templates/aframe-template.html` | template A-Frame déterministe qui marche |
| `.venv/bin/python out/tools/sound.py spec.json music.wav` | musique + SFX synthétisés (presets pluck-arp, pad, lofi, music-box, pulse, drone, chiptune ; SFX whoosh, impact, pop, tick, chime, riser, thud, blip, swell, click, coin, glass) |
| `.venv/bin/python out/tools/textpng.py …` / `from textpng import text_layer` | overlays texte PNG RGBA plein cadre (polices @fontsource, pour Manim/Taichi/OpenCV) |
| `.venv/bin/python out/tools/assemble.py mux --video v.mp4 --music music.wav --out short.mp4 [--overlay o.png:START:END:FADE]` | mux final (musique à −18 dB environ), overlays |
| `.venv/bin/python out/tools/assemble.py concat --clips a.mp4 b.mp4 --xfade fade --dur 0.5 --out x.mp4` | enchaînement xfade |
| `.venv/bin/python out/tools/assemble.py frames --video short.mp4 --times 1,7,14 --dir <dir>` | extraction de frames |
| `.venv/bin/python out/tools/assemble.py sheet --images a.jpg b.jpg … --out sheet.jpg --cols 3` | planche-contact |
| `.venv/bin/python out/tools/check.py out/shorts/<dossier>` | QA automatique (taille, fps, durée, audio, frames noires, fichiers requis) |
| `out/tools/slot.sh <commande>` | réserve un slot CPU pour un rendu Python lourd (Manim/Taichi/OpenCV) |
| `.venv/bin/python out/tools/tts.py out/shorts/<dossier>` | voix off Gemini TTS depuis narration.json (nécessite GEMINI_API_KEY ; absent pour l'instant — ne pas lancer) |

Librairies : `node_modules/` à la racine (three 0.187, matter-js 0.20, **p5 2.3** (pas de preload), gsap 3.15, d3 7.9, aframe 1.8, pixi.js 8, babylonjs 9, zdog, paper, **animejs 4** (imports nommés), flubber, roughjs, twgl.js, topojson-client) ; servies par `render.mjs` sous `/node_modules/...`. Polices @fontsource : inter, space-grotesk, fraunces, baloo-2, playfair-display, jetbrains-mono, bebas-neue, press-start-2p, dm-serif-display, caveat, fredoka, archivo-black, ibm-plex-mono, cormorant-garamond, unbounded, syne, anton, nunito, space-mono, rubik-mono-one, permanent-marker, cinzel, major-mono-display. Python : `.venv/bin/python` (3.11 : manim 0.22 **sans Text()/MathTex** — texte via textpng overlays —, taichi 1.7.4, numpy, scipy, opencv, pycairo, matplotlib, PIL). **N'installe rien** (pas de npm i, pas de playwright install). Lis `out/report/facts.md` (faits vérifiés : GSAP seek sans retour, A-Frame en chaînes, Matter pré-simulé en Node, Taichi MPM dt ≤ 1e-4, etc.).

## CPU : 4 cœurs partagés par 10 studios
`render.mjs` et `slot.sh` réservent automatiquement un slot CPU (4 max) : tu peux attendre un slot, c'est normal. Lance les rendus complets **en arrière-plan** et avance (son, JSON, second short) pendant ce temps. Privilégie 12–16 s par short, scènes légères. **Un seul rendu complet par short**, sauf correction réelle.

## Cycle obligatoire pour chaque short
1. Choisir un **sujet concret** dans la famille (vrai titre publiable, en français ; pas de lorem ipsum). Données inventées ou simplifiées à la main mais plausibles ; ne pas affirmer de faits faux (les explicatifs doivent être scientifiquement corrects).
2. Écrire la scène dans `src/` (HTML/JS ou Python), **déterministe** (graine fixée, notée dans short.json).
3. Rendre 3–5 **stills** aux moments clés dans `stills/`, les assembler en planche-contact (`assemble.py sheet`) et **les regarder** (réduis à ~360 px de large dans /tmp puis lis l'image). Corriger : hook visible < 1 s, texte ≥ 54 px (titres ≥ 90 px), contraste AA, rien d'important dans les 220 px du haut / 320 px du bas / 120 px de droite, pas de frame vide.
4. Rendu complet (arrière-plan) -> `src/video_silent.mp4` est **interdit** (poids) : rends dans `/tmp/svi/<dossier>/video.mp4`.
5. Son minimal : `src/sound.json` -> `/tmp/svi/<dossier>/music.wav` (événements calés sur les beats de la scène) ; ≤ 10 min de travail son.
6. `assemble.py mux` -> `out/shorts/<dossier>/short.mp4` (avec son ; overlays si besoin).
7. Vérifier 3 frames du **fichier final** (`assemble.py frames` -> /tmp, puis les regarder) + `check.py` doit être OK.
8. Écrire `short.json` et `narration.json` (schémas ci-dessous). `stills/` garde 3–5 frames clés (JPEG, peuvent être les stills de l'étape 3 ou du fichier final).

`src/` doit contenir tout le code + un `README.md` d'une ligne de commande exacte de reproduction (ex. `node out/tools/render.mjs out/shorts/X/src/index.html --out /tmp/v.mp4 --duration 15 && .venv/bin/python out/tools/sound.py out/shorts/X/src/sound.json /tmp/m.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/v.mp4 --music /tmp/m.wav --out out/shorts/X/short.mp4`).

## Contraintes non négociables
1080×1920, 30 fps, H.264 yuv420p, 10–20 s, hook visuel dans la 1re seconde, fin propre ou boucle parfaite. Open-source et gratuit, **aucun asset téléchargé**, tout généré par code. Aucun personnage/logo/œuvre existant, aucune photo de personne réelle ; personnages inventés. Laisse de la **place à la voix off** : les visuels ne doivent pas dépendre d'un texte à l'écran trop long ; le texte à l'écran = titres, chiffres, mots-clés.

## Schémas (respecter les clés)
`short.json`
```json
{"identity": "slug", "family": "histoire", "title": "…", "hook": "texte/visuel des 1res secondes", "duration": 16.0,
 "libraries": ["Manim", "GSAP"], "seed": 4, "renderTimeSec": 310, "structure": [{"t": 0, "beat": "hook"}, {"t": 3, "beat": "…"}],
 "engagement": {"mechanic": "question / vote / suspense / boucle", "cta": "…"}, "loopable": false,
 "sound": {"type": "generated", "voice": false},
 "qualityChecks": {"stillsReviewed": true, "textMinPx": 56, "safeAreaOk": true}, "notes": "…",
 "reproduce": "commande exacte"}
```
Familles (valeurs exactes) : `abstrait`, `enfants`, `explicatif`, `histoire`, `geographie`, `evenements`, `engagement`. `renderTimeSec` = temps **mesuré** du rendu complet (sortie JSON de render.mjs).

`narration.json` (voix off prévue, non enregistrée — sera synthétisée par Gemini TTS)
```json
{"language": "fr", "style": "enjoué, pour enfants de 6-10 ans", "voice": "Leda",
 "lines": [{"t": 0.3, "maxDuration": 2.5, "text": "…"}]}
```
Débit conseillé ≈ 2,6 mots/s (FR) : `maxDuration` ≥ nb_mots / 2.6. Les lignes ne se chevauchent pas. Voix Gemini possibles : Kore (claire), Puck (enjouée), Charon (grave), Leda (douce/jeune), Aoede (conteuse), Orus (documentaire), Fenrir (énergique), Enceladus (chuchotée), Iapetus (neutre), Achernar (calme).

`out/library-cards/_drafts/<slug>__<lib>.json`
```json
{"name": "…", "role": "3D | physique | typo | data | science | fluides | post-traitement", "bestFor": ["…"], "avoidFor": ["…"],
 "renderCostPer100Frames": "…s (mesuré, scène X)", "gotchas": ["…"], "snippetPath": "shorts/…/src", "pairsWellWith": ["…"]}
```

## Phase 3 — design system de l'identité
`out/identities/<slug>/tokens.json` (schéma de la mission : id, name, version, color{bg,surface,accent[],text,muted,success,danger}, typography{display,title,body,caption : family/weight/size/tracking}, motion{easing{enter,exit,emphasis}, duration{fast,base,slow}, stagger, hookDeadline}, camera{fov,moves,dof}, transitions[{name,ffmpegXfade,duration,use}], safeArea{top:220,bottom:320,right:120}, libraries[]). Les valeurs doivent être **celles réellement utilisées** dans tes shorts.

`out/identities/<slug>/identity.md` — sections obligatoires, dans cet ordre, en titres `##` : `Nom`, `Promesse en une phrase`, `Mood & références de genre`, `Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)`, `Typographie (familles @fontsource, tailles, graisses, interlettrage)`, `Formes & matières`, `Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)`, `Langage de caméra (cadrages, mouvements, focale, profondeur de champ)`, `Transitions (liste nommée, durée, quand les utiliser)`, `Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)`, `Zones sûres`, `Librairies recommandées et pourquoi`, `Familles de contenus adaptées / inadaptées`, `Shorts de preuve (chemins)`, `Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)`, `Risques et limites`.

`poster.jpg` : still 1080×1920 représentatif (peut être une frame d'un short). `contact-sheet.jpg` : 6–9 frames issues des shorts de l'identité (`assemble.py sheet --cols 3`). `recipes/<famille>.md` : pour chaque famille couverte, « pour un short <famille> dans cette identité : ouvrir par…, structurer en…, fermer par… », avec durées, tokens et chemin du short de référence.

## Fin de mission du studio
Réponds avec un résumé structuré : dossiers des shorts, durée et renderTimeSec de chacun, résultat check.py, librairies utilisées, ce qui a échoué (et pourquoi), temps réels. Si une librairie bloque > 20 min, remplace-la par une alternative de même catégorie et note-le dans `out/report/notes/<slug>.md`.
