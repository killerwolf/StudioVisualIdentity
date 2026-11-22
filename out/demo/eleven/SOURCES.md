# Musique et bruitages ElevenLabs (21/11/2026)

Générés pour la démo à la demande du propriétaire du dépôt, une génération par élément et sans relance, depuis un flow ElevenLabs.
- `music.mp3` : modèle `eleven_music_v2_5`, instrumental, 41,04 s, 615 crédits.
- `sfx/*.mp3` : 10 bruitages, modèle `eleven_text_to_sound_v3`, 29 crédits au total.

Le total est de 644 crédits. Les consignes envoyées sont dans `brief.json` : la description de la musique section par section, et une description par bruitage.

Contrairement aux shorts de preuve, dont le son est entièrement fait par code ou issu de sons CC0, la démo utilise ces fichiers générés par ElevenLabs.
Si un fichier manque, `build_audio.py` revient à la musique synthétisée et aux sons CC0.
