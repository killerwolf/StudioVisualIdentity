# Prompt : sound design Freesound pour la vidéo démo

À coller dans une **nouvelle session** Claude Code sur ce dépôt.

Cette session doit avoir deux choses, sans quoi rien ne marchera :
- `FREESOUND_API_KEY` dans les variables d'environnement. Une clé gratuite s'obtient sur https://freesound.org/apiv2/apply.
- `freesound.org` et `cdn.freesound.org` autorisés par le réseau de l'environnement.

Le 2026-11-04, freesound.org répondait 403 depuis le conteneur cloud alors que example.com passait. Freesound bloque peut-être les IP de datacenter. Si c'est le cas, lancez cette session en local (Claude Code sur votre machine).

---

```text
Lis AGENTS.md puis out/demo/README.md. Travaille sur la branche main.

Objectif : donner un vrai sound design à la vidéo démo out/demo/demo_{16x9,9x16}.mp4. Aujourd'hui, les effets sont
synthétisés par code (out/tools/sound.py via sound_specs() dans out/demo/build.py) et sonnent « cheap ». Il faut les
remplacer par de vrais sons Freesound, calés sur chaque apparition de texte et chaque transition.

1. Vérifie l'accès : `python3 out/tools/freesound.py search "whoosh" --max-dur 1.5 -n 5`. Si ça échoue (clé absente
   ou réseau 403), arrête-toi et dis-le-moi. Ne remplace pas les sons par des sons inventés.
2. Lis la timeline dans out/demo/build.py (CUT, C0, CD, CEND, TERM, RES0, EP_T, SLAM, SLAMS, END, DUR, CUES) et
   sound_specs(). Chaque événement y a un instant et un type. Liste les moments à sonoriser :
   - accroche : lignes de titre à 0,15 s et CUES.hookLine2, glitch puis coupure à CUT ;
   - carte « 14 IDENTITIES » à CUT + 0,25 et « NONE ALIKE » à CUES.noneAlike ;
   - allumage de chaque palier du brouhaha (C0 + k·CD), montée jusqu'à CEND, coupure nette à CEND ;
   - « too many choices? » (CEND + 0,35, doux) ;
   - ouverture du terminal à TERM, frappe clavier de CUES.typeStart à CUES.typeEnd, les trois ✓ (CUES.checks) ;
   - apparition du téléphone à RES0 et chaque changement d'épisode (EP_T[1..]) ;
   - les trois slams (SLAMS) et l'écran de fin (END, les lettres apparaissent en cascade).
3. Pour chaque type, cherche 2 ou 3 candidats CC0 (licence par défaut du script) de moins de 2 s, triés par
   rating_desc ou downloads_desc. Types : whoosh rapide, swoosh doux, pop ou bubble, UI click, typewriter ou
   mechanical keyboard, success ding, riser, cinematic boom ou impact, glitch, braam court, sub drop, shimmer.
   Télécharge les retenus : `python3 out/tools/freesound.py get <id> --dir out/demo/sfx --name <type>`.
   out/demo/sfx/credits.json garde l'auteur et la licence ; ne le supprime pas.
   Écoute-les. Tu ne peux pas les entendre, alors mesure : durée, niveau (volumedetect), attaque (silencedetect).
   Si un son est trop long, coupe-le avec atrim et fais un fondu.
4. Dans out/demo/build.py, ajoute une fonction sfx_freesound() qui pose ces fichiers aux bons instants avec
   adelay et volume, en une seule passe ffmpeg -> /tmp/svi/demo/sfx.wav. Elle remplace la piste « sfx » de
   sound_specs(). Garde les musiques « hook » et « outro » de sound.py, ou remplace-les aussi par des boucles CC0
   si c'est clairement mieux. Les voix doivent rester intelligibles : effets 6 à 10 dB sous la voix pendant
   qu'elle parle. Pas plus de 3 flashs sonores agressifs par seconde.
5. Reconstruis : `.venv/bin/python out/demo/build.py audio`, puis `final 16x9` et `final 9x16`, puis `gif`.
   Les calques overlay_*.mov et base_*.mp4 sont dans /tmp/svi/demo. S'ils n'y sont plus, relance
   `build.py base <fmt>` et `build.py overlay <fmt>`, un seul rendu par format à la fois.
   Vérifie les niveaux par segment (volumedetect) et que le pic reste sous -1 dBFS.
6. Mets à jour out/demo/README.md (section son + crédits Freesound) et sound.json.
   Commit, push sur main, et envoie-moi les deux MP4.
```
