Tu travailles dans le dépôt `killerwolf/StudioVisualIdentity`, branche `claude/new-session-ae9hjs` (fais `git pull origin claude/new-session-ae9hjs` d'abord). Mission : ajouter la voix off française générée par **Gemini TTS** à tous les shorts de `out/shorts/*/`, à partir de leurs `narration.json`, sans toucher aux vidéos ni aux autres fichiers. La variable d'environnement `GEMINI_API_KEY` est disponible dans ce conteneur (vérifie-la avec `test -n "$GEMINI_API_KEY" && echo ok`, sans jamais afficher sa valeur). Si elle est absente, arrête-toi et dis-le.

Contexte à lire d'abord : `out/report/README.md` (section « Voix off Gemini »), l'en-tête de `out/tools/tts.py` et `out/tools/assemble.py`, et un `narration.json` d'exemple. Chaque `narration.json` contient `language`, `style`, `voice` (voix Gemini préconstruite suggérée) et `lines` [{t, maxDuration, text}] calées sur la vidéo. `tts.py` synthétise chaque ligne, la place à son temps `t`, l'accélère au plus ×1,35 si elle dépasse `maxDuration`, puis remixe le short avec la musique duckée sous la voix (sidechain) via `assemble.py mux`.

Étapes :
1. Mise en place minimale (les dossiers `.venv/` et `node_modules/` ne sont pas dans git) : `uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python numpy scipy google-genai` (ffmpeg est déjà installé).
2. Si la skill `gemini-api-dev` est disponible, utilise-la et vérifie le nom de modèle TTS actuel ainsi que la forme exacte de la requête et de la réponse audio (WAV ou PCM L16 24 kHz). Le site de doc peut être bloqué par le réseau ; dans ce cas, appuie-toi sur les types du SDK installé (`google.genai.types.SpeechConfig` / `VoiceConfig` / `PrebuiltVoiceConfig`). Corrige `out/tools/tts.py` si l'API diffère de ce qu'il suppose : il n'a jamais été exécuté contre l'API réelle.
3. Teste sur **un seul** short : `.venv/bin/python out/tools/tts.py out/shorts/swiss-data__geographie__ou-vivent-8-milliards` (cela produit `voice.wav`, `short_vo.mp4` et `voice_report.json`). Vérifie :
   - que la voix est bien en français, avec la bonne voix, sans coupure ni silence parasite ;
   - le niveau sonore (`ffmpeg -i short_vo.mp4 -af volumedetect -f null -`) : la voix doit nettement dominer la musique, sans saturation ;
   - la durée, identique à celle de la vidéo ;
   - les débordements signalés dans `voice_report.json`.
   Ajuste `--music-db`/`--voice-db` ou le prompt de style si besoin. Si une ligne déborde toujours après ×1,35, signale-le ; ne réécris pas le texte sans le noter.
4. Lance tous les shorts : `.venv/bin/python out/tools/tts.py --all --replace`. Chaque `short.mp4` devient la version avec voix, l'original est gardé en `short_novo.mp4`, et `short.json.sound.voice` passe à `true`.
5. Contrôle : `.venv/bin/python out/tools/check.py --all` doit rester à 100 % OK. Extrais le son de 3 shorts de familles différentes et vérifie qu'ils ont une piste audio. Si `check.py` signale des frames noires ou une mauvaise durée, c'est le remix qui pose problème.
6. Mets à jour le rapport sans rien inventer :
   - `out/report/README.md` et `out/report/failures.md` : la voix off est désormais générée (modèle et voix réellement utilisés) ;
   - `out/report/facts.md` : temps mesuré par short, débordements, réglages de niveau ;
   - `out/report/decisions.md` : une ligne horodatée par choix fait.
   Ne modifie aucun autre fichier.
7. Poids : les dépôts Git n'aiment pas les gros binaires. Ne commite pas `voice.wav` (ajoute `out/shorts/*/voice.wav` à `.gitignore`). Garde `short.mp4` (avec voix), `short_novo.mp4` et `voice_report.json`.
8. Commite avec un message clair, puis pousse sur `claude/new-session-ae9hjs` (réessaie jusqu'à 4 fois si le réseau échoue). Donne-moi ensuite un résumé : nombre de shorts traités, modèle, voix, débordements, temps total, et tout ce qui a échoué.
