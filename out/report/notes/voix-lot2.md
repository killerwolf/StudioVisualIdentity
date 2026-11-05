# Voix off lot 2 — identité trait-continu (2026-11-05 00:54 UTC)

**Mise à jour 18:35 UTC : résolu, les 4 shorts sont voisés avec Gemini « Sulafat » (voir « Reprise avec Gemini » en bas).** Statut initial : **BLOQUÉ par les crédits Fish Audio.** 1 ligne sur 10 générée ; aucun mixage ; aucun short modifié hormis le fichier audio ci-dessous.

## Crédits
- Avant : `package_balance` 35 + `package_extra_balance` 2 000 (affiché « 2 035 »), plan free, 500 octets max/appel, `package_cycle_ends_at` 2026-10-15T07:44:33Z (date passée).
- Besoin calculé : 314 crédits (1 crédit / octet UTF-8, 10 lignes).
- Après : `package_balance` 5, `package_extra_balance` 2 000 (inchangé).
- Dépensé : 30 crédits (1 appel réussi). Les 2 000 crédits « extra » ne sont pas utilisables par `text_to_speech` : seul `package_balance` est débité, et il est épuisé.

## Appels text_to_speech (voix Arnold d704cf8f1216490cbfbed89955f0e938, modèle s2.1-pro, texte tel quel)
5 appels envoyés pour le short escargot, 1 réussi, 4 refusés :
| # | Ligne | Résultat |
|---|---|---|
| 00 | « Un escargot, d'un seul trait ? » | OK, task de45e44e3465434fa241744d89bd55fd, 30 crédits, téléchargé (curl OK), 1,78 s ≤ maxDuration 2,4 s, pas de débordement |
| 01 | « Du centre, on tourne. » | Échec : `Insufficient credits: this call needs 21 credits. Check get_credit_balance, or top up at https://fish.audio/go-premium/` |
| 02 | « Il grandit : un tour de plus. » | Échec : `… needs 29 credits …` |
| 03 | « La plupart tournent à droite. » | Échec : `… needs 30 credits …` |
| 04 | « Et toi, ta spirale tourne dans quel sens ? » | Échec : `… needs 42 credits …` |

Short Italie (5 lignes, 162 crédits) : aucun appel.
Les appels refusés ne sont pas facturés. Aucune relance.

## Mixage / check.py
Non lancés : `tts.py --engine files` exige les 5 fichiers `voice_lines/00.mp3`…`04.mp3` (il échouerait à la ligne 01 sans rien écrire). Les deux `short.mp4` restent les versions musique + SFX sans voix (`sound.voice: false`).

## Fichiers créés
- `out/shorts/trait-continu__enfants__dessine-un-escargot-d-un-seul-trait/voice_lines/` (dossier)
- `out/shorts/trait-continu__enfants__dessine-un-escargot-d-un-seul-trait/voice_lines/00.mp3` (28 489 octets, 1,78 s)
- `out/report/notes/voix-lot2.md` (ce journal)
Aucun autre fichier modifié.

## Pour reprendre
Il faut 284 crédits `package_balance` de plus (lignes 01–04 escargot : 122 ; 00–04 Italie : 162). Après recharge : générer seulement les 9 lignes manquantes (ne pas refaire 00 escargot), nommage `voice_lines/00.mp3`…`04.mp3` (index 0, pas 01), puis `.venv/bin/python out/tools/tts.py out/shorts/<dossier> --engine files --replace` et ajouter `voiceUsed` dans narration.json comme pour swiss-data.

---

# Reprise avec Gemini « Sulafat » (2026-11-05 18:00–18:35 UTC) — 4 shorts voisés et mixés

**Décision du propriétaire** : les 4 shorts du lot 2 reçoivent la voix Gemini « Sulafat », celle des 8 shorts papier, au lieu d'Arnold (crédits Fish Audio épuisés). La ligne 00 Arnold de l'escargot est remplacée pour l'homogénéité (copie hors dépôt, non versionnée).

## Appels Gemini : 4 (un par short), 0 échec, 0 relance
- Skill `gemini-voices`, commande `voix` (`gemini_voix.py`, API `interactions`), modèle **`gemini-3.8-flash-tts`**, voix `Sulafat`, lancé par `uv`.
- Entrée : texte des lignes de `narration.json`, dans l'ordre, séparées par `<long pause>` ; aucun préfixe lu : le style passe en annotation `speech_metadata`.
  - trait-continu (×2) : « conteuse chaleureuse et douce pour enfants de six à dix ans, débit lent et posé, sourire dans la voix ».
  - carte-meteo mistral : « voix documentaire claire et posée, ton de bulletin météo naturel, débit régulier » ; chaleur : idem « et un peu soutenu ».
  - chaleur : nombres envoyés en toutes lettres (« quarante-quatre virgule un degrés, en deux mille trois », « quarante-six degrés ») ; le texte de `narration.json` n'est pas modifié.
- Audio complet : escargot 16,88 s (−19,3 LUFS), Italie 18,72 s (−17,7), mistral 16,08 s (−17,1), chaleur 13,64 s (−17,3).

## Découpe en `voice_lines/00.mp3`…
- La découpe du skill (`decouper`, coupe aux n−1 silences les plus longs) s'est **trompée** sur l'escargot : elle a coupé dans « Il grandit : | un tour de plus » (pause de 0,67 s au deux-points) et collé « La plupart… » à la ligne suivante. Non utilisée.
- Découpe retenue : horodatage des mots par faster-whisper (`small`, CPU, local, aucun appel API) pour repérer le premier mot de chaque ligne, puis coupe au plus long silence (`silencedetect` −45 dB) entre la fin de la ligne et le premier mot suivant ; fondus de 8 ms ; MP3 mono 44,1 kHz 128 kb/s. Transcription vérifiée ligne à ligne (erreurs de reconnaissance seulement : « calibre », « cicille », « l'héro » pour Calabre, Sicile, l'Hérault ; non écouté par l'assistant).
- Lignes qui dépassaient `maxDuration` : pauses internes (> 0,25 s) ramenées à 0,25 s, sans toucher au texte ni aux mots.

## Durées (après rognage par `tts.py`) et accélération appliquée par `tts.py` (atempo ≤ ×1,35)
| Short | Ligne | Brut (s) | maxDuration | Atempo | Final (s) | Débord. |
|---|---|---|---|---|---|---|
| escargot | 00 | 2,30 | 2,4 | — | 2,30 | non |
| escargot | 01 | 2,12 (pause 0,47 → 0,25) | 2,0 | ×1,06 | 2,00 | non |
| escargot | 02 | 2,70 (pause 0,79 → 0,25) | 2,8 | — | 2,70 | non |
| escargot | 03 | 1,76 | 2,35 | — | 1,76 | non |
| escargot | 04 | 3,43 (3 pauses → 0,25) | 3,7 | — | 3,43 | non |
| Italie | 00 | 3,36 | 4,15 | — | 3,36 | non |
| Italie | 01 | 2,91 (pause 0,80 → 0,25) | 2,8 | ×1,04 | 2,80 | non |
| Italie | 02 | 2,51 (2 pauses → 0,25) | 2,3 | ×1,09 | 2,30 | non |
| Italie | 03 | 3,13 (2 pauses → 0,25) | 2,3 | **×1,35 (plafond)** | 2,31 | non (+0,01 s, fin à 12,61 s < ligne suivante 12,75 s) |
| Italie | 04 | 2,05 | 2,4 | — | 2,05 | non |
| mistral | 00 | 2,83 (pause 0,57 → 0,25) | 2,9 | — | 2,83 | non |
| mistral | 01 | 4,32 | 4,5 | — | 4,32 | non |
| mistral | 02 | 4,02 | 4,3 | — | 4,02 | non |
| mistral | 03 | 2,31 | 2,6 | — | 2,31 | non |
| chaleur | 00 | 3,09 | 4,2 | — | 3,09 | non |
| chaleur | 01 | 3,71 | 4,6 | — | 3,71 | non |
| chaleur | 02 | 2,84 | 3,0 | — | 2,84 | non |
| chaleur | 03 | 1,87 | 2,2 | — | 1,87 | non |

Débit parlé (mots / durée des lignes, pauses internes comprises) : escargot ≈ 2,3 mots/s, Italie ≈ 2,3 (cible 2,0–2,2 : un peu au-dessus, à cause des pauses raccourcies et de l'atempo), mistral ≈ 2,9, chaleur ≈ 2,9 en mots dits (cible 2,4–2,8 : un peu au-dessus). Chaleur : aucune ligne ne déborde, aucune regénération nécessaire.

## Mixage et contrôle
- `.venv/bin/python out/tools/tts.py out/shorts/<dossier> --engine files --replace --voice "Gemini – Sulafat"` pour les 4 : `short_novo.mp4` (musique + bruitages d'origine), `short.mp4` avec voix, `voice_report.json`, `voice.wav` (ignoré par git). 0 débordement signalé.
- `tts.py --engine files` écrit `model: fish-connector` dans `voice_report.json` et `sound.voiceEngine` : corrigé à la main en `gemini-3.8-flash-tts` / `gemini` (outil non modifié).
- `narration.json` : `voice` = « Sulafat (Gemini) », bloc `voiceUsed` (Gemini, Sulafat, gemini-3.8-flash-tts, 2026-11-05, note), `voiceNote` retiré, `voicePlannedHistory` garde la trace d'Arnold.
- Niveaux `short.mp4` (volumedetect) : escargot moyen −19,4 dB / pic −1,4 dBFS ; Italie −18,4 / −1,5 ; mistral −17,4 / −1,4 ; chaleur −19,8 / −1,6.
- `check.py` : 4/4 OK, plus d'avertissement « voix absente » (l'escargot garde « image figée ≥3 s à 12 s », visuel, voulu) ; `check.py --all` : 43/43 OK.
