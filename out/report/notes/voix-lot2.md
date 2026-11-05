# Voix off lot 2 — identité trait-continu (2026-11-05 00:54 UTC)

**Statut : BLOQUÉ par les crédits Fish Audio.** 1 ligne sur 10 générée ; aucun mixage ; aucun short modifié hormis le fichier audio ci-dessous.

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
