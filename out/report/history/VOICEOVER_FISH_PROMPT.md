# Prompt — voix off Fish Audio pour les 8 derniers shorts

Tu travailles dans le dépôt `killerwolf/StudioVisualIdentity`. Mission : ajouter la voix off française **Fish Audio « Arnold »** aux **8 shorts qui n'ont pas encore de voix**, avec exactement la même méthode et la même voix que les 23 autres. Ne touche ni aux vidéos sources, ni aux 23 shorts déjà voisés, ni à `tts.py` (sauf bug bloquant, à signaler).

## 0. Prérequis (vérifie, sinon arrête-toi et dis-le)

- **Branche** : `git fetch origin` puis `git checkout claude/determined-euler-3dv4t4 && git pull origin claude/determined-euler-3dv4t4`. Si la PR #1 est déjà fusionnée, pars de `claude/new-session-ae9hjs` à jour et travaille sur la branche qui t'est assignée.
- **Connecteur Fish Audio** actif dans la session (outils `mcp__Fish_Audio__*`, notamment `text_to_speech` et `get_credit_balance`). Si les outils sont différés, charge-les avec ToolSearch (`select:mcp__Fish_Audio__text_to_speech,mcp__Fish_Audio__get_credit_balance`). Sans ce connecteur : arrête-toi.
- **Crédits** : appelle `get_credit_balance`. Il faut au moins **~1 800 crédits** (1 crédit = 1 octet UTF-8 de texte ; besoin estimé : 1 711). Plan gratuit : 500 octets max par appel (aucune ligne n'en approche).
- **Environnement Python** (non versionné) : `uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python numpy scipy` ; `ffmpeg` est déjà installé.

## 1. Les 8 shorts concernés (45 lignes, 1 711 octets)

Ce sont ceux dont `short.json` n'a pas `sound.voice == true` :

| Short (`out/shorts/<dossier>`) | Lignes |
|---|---|
| `brut-meme__engagement__test-des-3-secondes-stroop` | 7 |
| `brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde` | 6 |
| `cosmos-doc__evenements__voyager-1-a-un-jour-lumiere` | 4 |
| `cosmos-doc__explicatif__pourquoi-venus-plus-chaude-que-mercure` | 4 |
| `riso-zine__evenements__geminides-j-39` | 6 |
| `riso-zine__geographie__5-plus-grands-deserts` | 7 |
| `topo-relief__geographie__comment-mesure-t-on-l-everest` | 6 |
| `topo-relief__histoire__hannibal-traverse-les-alpes` | 5 |

Recalcule la liste toi-même (elle peut avoir changé) :
```bash
python3 - <<'EOF'
import json,glob,os
for f in sorted(glob.glob('out/shorts/*/short.json')):
    d=os.path.dirname(f)
    if not json.load(open(f)).get('sound',{}).get('voice') and os.path.exists(d+'/narration.json'):
        L=json.load(open(d+'/narration.json'))['lines']
        print(os.path.basename(d), len(L), sum(len(l['text'].encode()) for l in L))
EOF
```

## 2. Synthèse des lignes (connecteur Fish Audio)

Voix **Arnold** : `voice_id = d704cf8f1216490cbfbed89955f0e938`, modèle par défaut (`s2.1-pro`), `language = "fr"`. Ne change pas de voix : la série doit être homogène.

Règles :
- **Un appel `text_to_speech` par ligne** de `narration.json`, avec le texte **tel quel** (aucune balise, aucun préfixe de style : tout texte ajouté est lu ou facturé). Ne réécris pas le texte.
- Envoie les appels d'un même lot **en parallèle** (plusieurs appels dans un même tour) ; les résultats reviennent dans l'ordre des appels. Note pour chaque appel son `task_id`, dans l'ordre des lignes (index 0, 1, 2…).
- **Ne relance jamais un appel pour « réessayer »** : chaque répétition (hors 5 min, texte identique) est refacturée. Si le téléchargement échoue, retélécharge la même URL.
- N'utilise **aucune voix imitant une personne réelle** (hommes/femmes politiques, sportifs, etc.), et pas de `drama-3` (≈ ×2 le coût) ni d'autre voix que Arnold.

## 3. Téléchargement et rangement

Chaque résultat contient `audio_url` (forme `https://platform.r2.fish.audio/tasks/<AAAA-MM-JJ>/<task_id>.mp3` ; **copie l'URL exacte renvoyée**, la date peut différer de celle d'aujourd'hui). Télécharge-la avec `curl` vers :

```
out/shorts/<dossier>/voice_lines/00.mp3, 01.mp3, 02.mp3 …   (numéro = index de la ligne dans narration.json, sur 2 chiffres)
```

Vérifie ensuite : nombre de `.mp3` == nombre de lignes pour chaque short, et chaque fichier est un audio valide (`ffprobe -v error -show_entries format=duration -of csv=p=0 <fichier>` renvoie une durée). Un fichier vide ou HTML = téléchargement raté (retélécharge l'URL, ne régénère pas).

## 4. Mixage

Pour chacun des 8 shorts (ou une seule commande si tu les as tous) :

```bash
.venv/bin/python out/tools/tts.py out/shorts/<dossier> --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Cela place chaque ligne à son temps `t`, l'accélère au plus ×1,35 si elle dépasse `maxDuration`, remixe avec la musique duckée (sidechain), remplace `short.mp4` (l'original est conservé en `short_novo.mp4`) et met `short.json.sound.voice = true`. **N'utilise pas `--all`** : il repasserait les 23 shorts déjà faits (et écraserait `short_novo.mp4` cohérent). Le mixage prend ~7 s par short ; lance-le en arrière-plan si la commande dépasse 2 minutes.

## 5. Contrôles

- `.venv/bin/python out/tools/check.py --all` doit rester à **31/31 OK** (ou au nombre total de shorts du moment). Frames noires ou mauvaise durée = problème du remix : signale-le.
- Pour 3 shorts de familles différentes : piste audio présente (`ffprobe -select_streams a`), durée identique à la vidéo, `ffmpeg -i short.mp4 -af volumedetect -f null -` → pic ≈ −1,5 dB, pas de saturation.
- Lis chaque `voice_report.json` : liste les lignes `over: true` (débordements après ×1,35). **Ne réécris pas le texte** ; note-les seulement.
- Tu ne peux pas écouter l'audio : dis-le, ne prétends pas avoir évalué la qualité.

## 6. Rapports (sans rien inventer)

Mets à jour, en cohérence avec ce qui existe déjà :
- `out/report/README.md` : section « Voix off Fish Audio (générée) » : passe de « 23 shorts sur 31 » à « 31 sur 31 » (retire la phrase sur les 8 shorts sans voix) ; ligne « Voix off » plus bas.
- `out/report/failures.md` : ligne « Voix off : 1 débordement résiduel » (ajoute les nouveaux débordements) et la phrase « les 8 shorts … sont encore sans voix » de la ligne « Un seul rendu complet par short… ».
- `out/report/facts.md` (section « Voix off Fish Audio ») : crédits réellement consommés (somme des `credits_charged`), nombre de lignes, débordements, niveaux mesurés.
- `out/report/decisions.md` : une ligne datée par choix fait.
Ne modifie aucun autre fichier.

## 7. Git

- Ne commite pas `voice.wav` (déjà ignoré par `.gitignore`). Garde `short.mp4` (avec voix), `short_novo.mp4`, `voice_lines/*.mp3`, `voice_report.json`, `short.json`.
- Commit clair, puis `git push -u origin <branche>` (jusqu'à 4 essais avec attente 2 s, 4 s, 8 s, 16 s si le réseau échoue). Si une PR existe déjà pour la branche, ne la recrée pas ; sinon ouvre-la (prête pour relecture).
- Si un conflit apparaît dans les rapports (`decisions.md`, `failures.md`), fusionne la branche de base **dans** ta branche (pas de rebase, pas de force-push) en gardant les deux côtés.

## 8. Compte rendu final

Donne-moi : nombre de shorts traités (attendu 8), lignes synthétisées (attendu 45), crédits consommés et solde restant, débordements (short, ligne, durée vs max), résultat de `check.py`, et tout ce qui a échoué. Précise que la voix n'a pas été écoutée.
