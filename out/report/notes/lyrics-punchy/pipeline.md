# Lyrics punchy — chaîne de synchronisation et de rendu

## Règles de droits (à respecter avant tout)

- **Ni l'audio ni les paroles réelles n'entrent dans le dépôt** (dépôt public). Ils vivent dans
  `~/git/StudioVisualIdentity-sources/lyrics-<morceau>/` : `<morceau>.wav`, `transcription-mots.json`, `paroles.txt`, `lyrics.json`.
- Le dépôt ne contient que le moteur, la bibliothèque de déclencheurs et un jeu de **remplissage** (`lyrics.remplissage.json`, nos mots, marqué comme tel).
- La vidéo est rendue **muette** ; le son est ajouté dans l'appli à la publication, à partir de 0:00.
- Le rendu avec les vraies paroles est écrit hors dépôt lui aussi, tant qu'Hamdi n'a pas décidé du contraire.

## Ce qui est disponible sur ce Mac (vérifié le 18/11/2026)

| Besoin | État |
|---|---|
| `.venv` du worktree `-lyrics` | absent ; celui du worktree principal a numpy, scipy, pillow, opencv, pycairo, pas d'outil audio |
| faster-whisper | fonctionne par `uv run --with faster-whisper --with "av<16"` (rien d'installé globalement) ; modèles `small` et `small.en` déjà en cache ; essai sur une phrase de synthèse : 13 mots horodatés en 10 s ; le brouillon `transcription-mots.json` du morceau test existe déjà |
| librosa | **ne s'installe pas** : sa dépendance `llvmlite` 0.50 échoue à la compilation sur ce Mac (Intel, Python 3.11). Ne pas insister. |
| Détection du tempo | scipy seul (flux spectral, autocorrélation, puis recherche de phase), environ 30 lignes. Essai sur un métronome à 154,5 BPM : il trouve **77,2**, la moitié (erreur d'octave classique), phase juste à 20 ms près. Il faut donc borner la recherche (ex. 100–200 BPM) ou faire confirmer le tempo à l'oreille. Non essayé sur le vrai morceau ; inutile pour le test, le tempo est déjà mesuré. |
| node | pas dans le `PATH` ; présent dans `~/.nvm/versions/node/v22.23.3/bin` (à ajouter au `PATH` de la commande) |
| `node_modules`, Playwright | absents du worktree `-lyrics` : `npm i` à faire, comme le dit `AGENTS.md` |
| Police | `@fontsource-variable/anybody` 5.3.0 existe sur npm |

## Étapes

1. **Paroles exactes** : fournies par Hamdi dans `paroles.txt` (une ligne chantée par ligne, une ligne vide entre sections, `# refrain` / `# couplet` en tête de section). La transcription ne sert qu'aux horaires.
2. **Horaires des mots** : faster-whisper avec `word_timestamps=True`, langue fixée, `initial_prompt` = les paroles exactes. Résultat brut : `transcription-mots.json` (`[{start, end, text, words:[{w, s, e}]}]`).
3. **Alignement sur le texte exact** (`out/tools/lyrics_align.py`, à écrire, en-tête PEP 723 pour `uv run`) :
   - normaliser les deux suites de mots (minuscules, sans accents ni ponctuation) ;
   - les apparier avec `difflib.SequenceMatcher` ; un mot apparié prend l'horaire de Whisper ;
   - un mot non apparié est réparti entre ses voisins, au prorata du nombre de caractères ;
   - **méfiance** : Whisper étale parfois un mot sur un silence (dans le brouillon, un mot dure 1,8 s). Si un mot dure plus de 0,8 s, son début = sa fin − 0,3 s ;
   - forcer des horaires croissants, puis marquer chaque mot `source: "whisper" | "reparti" | "main"`.
4. **Grille des temps** : `bpm` et `t0` (instant du temps 0) viennent d'une mesure (ici 154,5 et 0) ou de la détection scipy. Un mot à moins de 70 ms d'une croche est ramené sur la croche.
5. **Accents** : 2 = premier temps d'une mesure ou mot déclencheur ; 1 = sur un temps ; 0 = contretemps. Au plus un accent 2 par mesure (on garde le déclencheur).
6. **Unités et lignes** : regroupement des petits mots, coupe des lignes de plus de 6 unités (règles de `concept.md` § 6).
7. **Déclencheurs** : recherche des expressions de `triggers.json`, application des règles de densité (§ 8), écriture du déclencheur sur l'unité.
8. **Relecture** : l'aperçu au métronome et la page avec la musique (ci-dessous). Toute correction se fait à la main dans `lyrics.json` (`source: "main"`), jamais en relançant l'alignement par-dessus.

## Format `lyrics.json`

```json
{
  "titre": "…", "artiste": "…", "langue": "en",
  "bpm": 154.5, "t0": 0.0, "tempsParMesure": 4, "duree": 19.5,
  "sections": [ { "id": "refrain-1", "debut": 0.0, "fin": 3.9, "camaieu": "nuit" } ],
  "lignes": [
    { "section": "refrain-1", "debut": 0.0, "fin": 3.9,
      "unites": [
        { "texte": "MOT", "t": 0.39, "fin": 0.78, "accent": 2, "rang": 0, "source": "whisper",
          "declencheur": { "id": "plan-mode", "debut": 0.39, "temps": 4 } }
      ] }
  ]
}
```

`t` = instant chanté (le moteur affiche 2 images avant). `rang` = rang dans la ligne en cours (0 à 2). `declencheur` est facultatif.

## Rendu

- Moteur du dépôt : **`out/tools/render.mjs`** (scène HTML, `window.renderAt(t)`), adapté : texte en DOM (net, police variable par `font-variation-settings`), pictogrammes en SVG en ligne, aucun état donc pas de `SEQUENTIAL`. Mesures de texte faites une fois dans `window.ready`, après `document.fonts.ready`.
- Moteur partagé de l'identité : `out/shared/lyrics-moteur/` (`lyrics.js` = lecteur de `lyrics.json`, `triggers.json`, `dessins/`). Un nouvel épisode = un nouveau `lyrics.json`, sans code.
- La scène lit son fichier de données par `?data=` ; par défaut `lyrics.remplissage.json`.
- Coût attendu : la capture domine (environ 0,3 s par image selon `AGENTS.md`), soit 3 minutes pour 19,5 s. À mesurer et écrire dans `short.json`.
- `check.py` exige une piste audio et `narration.json` : mettre une piste **silencieuse** dans `short.mp4` et `{"lines": []}` dans `narration.json`. La version de 36 s dépasse la limite de 20 s de `check.py` : elle se rend à part.

## Aperçus pour caler

1. **Métronome** : `apercu_metronome.mp4` = la vidéo + un clic généré par code à 154,5 BPM depuis `t0` (clic aigu sur le premier temps). Vérifie que les entrées tombent sur les temps, sans la chanson.
2. **Avec la musique** : `apercu_avec_musique.html`, copie de `~/git/AIReboot/episodes/ar-16-claudes-plan-dance/apercu_avec_musique.html` : la vidéo muette suit le lecteur YouTube officiel (`HhcFXn-ZY6E`) en iframe, rien n'est téléchargé. Changer seulement le nom du fichier vidéo et le titre. À ouvrir par un petit serveur local.
3. En interne seulement : `ffmpeg` peut poser `claudes-plan.wav` sous la vidéo, dans le dossier `-sources`, jamais dans le dépôt.

## Passer à un autre morceau

Créer `~/git/StudioVisualIdentity-sources/lyrics-<morceau>/`, y mettre l'audio (obtenu avec l'accord d'Hamdi) et `paroles.txt`, lancer les étapes 2 à 7, relire avec les aperçus, rendre. Ajouter au besoin des déclencheurs dans `triggers.json`.
