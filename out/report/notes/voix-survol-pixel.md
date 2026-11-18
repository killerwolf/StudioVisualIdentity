# Voix off Survol pixel — Gemini « Sulafat » (18/11/2026)

Décision du propriétaire (relayée par BalthouPro) : voix off Gemini pour les 2 shorts survol-pixel, avec le skill `studio:gemini-voices`.
Clé lue dans le `.env` d'un autre projet du propriétaire, en lançant le script avec ce projet comme dossier courant (autorisé par le propriétaire). Elle n'a été ni copiée, ni affichée, ni écrite dans ce dépôt.

## Appels à l'API

5 requêtes en tout, dont 2 générations réussies. Aucune relance.

| # | Type | Modèle | Résultat |
|---|---|---|---|
| 1 | génération (atoll) | `gemini-3.8-flash-tts`, script du skill tel quel (API v1) | **404** « Model 'gemini-3.8-flash-tts' not found… set the API version to 'v1beta' », aucun audio |
| 2 | lecture `models.list` (×2 : la 1re sortie était vide à cause d'un filtre de mon script) | — | 28 modèles, **aucun modèle `*-tts`** visible en v1 |
| 3 | génération (atoll) | `gemini-omni-flash-preview` (essai décidé par le propriétaire) | **400** « The field 'speech_config' … is only available in v1beta », aucun audio |
| 4 | génération (atoll) | `gemini-3.8-flash-tts`, copie locale du script forcée en **v1beta** | OK : 20,60 s, −19,7 LUFS |
| 5 | génération (Machu Picchu) | idem | OK : 18,48 s, −18,4 LUFS |

## Cause et correctif

Le script `gemini_voix.py` du skill (google-genai ≥ 2.34, API `interactions`) appelle la version v1 de l'API. Or `speech_config` et les modèles TTS n'existent qu'en v1beta.
Le lot 2 avait réussi le 05/11 avec le même script : le changement vient du côté de l'API ou du SDK. Le skill n'a pas été modifié. Le correctif a été appliqué dans une copie locale, hors dépôt :

```diff
-    client = genai.Client(api_key=cle, http_options={"retry_options": {"attempts": 0, "http_status_codes": [599]}})
+    client = genai.Client(api_key=cle, http_options={"api_version": "v1beta", "retry_options": {"attempts": 0, "http_status_codes": [599]}})
```

## Entrée envoyée

- Voix `Sulafat`. Style passé en annotation `speech_metadata` (non lu) : « voix documentaire claire et posée, conteuse curieuse, débit régulier ».
- Texte : les lignes de `narration.json` jointes par `<long pause>`, avec les nombres en toutes lettres (« mille huit cent quarante-deux », « deux mille quatre cent trente », « quinzième siècle », « mille neuf cent onze »). `narration.json` n'a pas été modifié.

## Découpe en `voice_lines/NN.mp3`

- Horodatage des mots par faster-whisper `small` (CPU, local, Python 3.11 via uv), pour trouver le premier mot de chaque ligne.
- Coupe 80 ms avant ce premier mot, bords rognés.
- Pauses internes > 0,25 s ramenées à 0,25 s : Gemini marque une pause après chaque virgule et chaque point d'interrogation.
- Fondus de 8 ms ; MP3 mono 44,1 kHz 128 kb/s.
- Transcription vérifiée mot à mot : exacte. Les seules différences sont des homophones de la reconnaissance (« Pierre » pour pierres, « Révéler » pour révélée).

## Lignes (après `tts.py`, atempo ≤ ×1,35)

| Short | Ligne | Brut découpé (s) | Final (s) | maxDuration | Débordement | Chevauchement |
|---|---|---|---|---|---|---|
| atoll | 00 | 3,40 | 3,11 | 3,1 | non | non |
| atoll | 01 | 2,69 | 2,69 | 3,0 | non | non |
| atoll | 02 | 3,64 | 3,60 | 3,6 | non | non |
| atoll | 03 | 2,49 | 2,46 | 3,0 | non | non |
| atoll | 04 | 2,58 | 2,55 | 3,5 | non | non |
| Machu Picchu | 00 | 4,92 | 4,67 | 4,65 | non | non |
| Machu Picchu | 01 | 3,28 | 3,28 | 3,5 | non | non |
| Machu Picchu | 02 | 3,85 | 3,81 | 4,4 | non | non |
| Machu Picchu | 03 | 2,27 | 2,23 | 3,5 | non | non |

## Mixage et vérification

- `tts.py --engine files --replace` : `short.mp4` est voisé ; `short_novo.mp4` (musique + effets sonores) est intact.
- Étiquettes corrigées : `fish-connector` → `gemini-3.8-flash-tts` dans `voice_report.json` et `short.json.sound` ; `voiceUsed` renseigné dans `narration.json`.
- Mesures des shorts finaux :

| Short | Durée | Sonie intégrée | Crête | LRA |
|---|---|---|---|---|
| atoll | 18,6 s | −15,9 LUFS | −1,7 dBFS | 5,2 LU |
| Machu Picchu | 18,8 s | −13,7 LUFS | −1,5 dBFS | 3,3 LU |

- `check.py` : ok sur les 2 shorts, 0 avertissement.
- Mix final transcrit par faster-whisper : texte complet et intelligible sous la musique.
- **Non écouté** par l'assistant (pas d'écoute possible) : le timbre, l'intonation et l'équilibre voix / musique sont à valider à l'oreille par le propriétaire.
- Audios bruts (mp3 + wav) gardés hors dépôt, dans `StudioVisualIdentity-sources/console-retro/voix/`.
