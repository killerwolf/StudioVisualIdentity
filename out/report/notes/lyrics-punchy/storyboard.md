# Lyrics punchy — storyboard du short de preuve

Morceau test : « Claude's Plan » (Jeff Guo), les 19,5 premières secondes. Dossier prévu : `out/shorts/lyrics-punchy__paroles__claudes-plan/`.

- Tempo ≈ 154,5 BPM : un temps = 0,388 s, une mesure = 1,553 s, temps 0 = début du morceau (relevé AR-16).
- Vidéo muette, 19,5 s (585 images) ; son ajouté dans l'appli à partir de 0:00.
- **Les paroles ne sont pas écrites ici.** Chaque `[…]` est un emplacement à remplir depuis `paroles.txt` (hors dépôt) quand Hamdi aura confirmé le texte. Tant que ce n'est pas fait, le moteur affiche `lyrics.remplissage.json` (nos mots, en français, comme sur les images `frame-*.jpg`).
- Les instants « mot-clé » viennent du brouillon Whisper (à ±0,3 s) ; à recaler à l'aperçu.

| Plan | Temps (s) | Section | Camaïeu | Texte affiché | Mouvement | Visuel déclenché |
|---|---|---|---|---|---|---|
| 1 | 0,0–3,9 | refrain | `nuit` | `[ligne 1 du refrain]` puis `[ligne 2 du refrain]` si elle existe | image 0 : première unité déjà en `claque` (accroche avant 0,5 s) ; unités sur les temps ; compteur de temps actif ; si le passage est sans voix, afficher le titre « CLAUDE'S PLAN » en 2 rangs, un `coup` par mesure | aucun (on installe le système), voir `frame-1` |
| 2 | 3,9–7,1 | couplet, ligne 1 | `lagon` | `[couplet 1, ligne 1 : le matin en « plan mode »]` | à 3,9 : `chute-de-pile` + changement de teinte ; mot-clé en `coup` | **`plan-mode`**, carton à l'instant du mot-clé (≈ 5,2 s), 4 temps, les cases se cochent sur 2 temps ; voir `frame-2` |
| 3 | 7,1–10,3 | couplet, ligne 2 | `lagon` | `[couplet 1, ligne 2 : des lignes, mais pas du code]` | `empilement` de la ligne 1 à 7,1 | **`lignes`**, carton ≈ 7,6 s, 4 temps, une barre tapée par croche |
| 4 | 10,3–13,3 | couplet, ligne 3 | `lagon` | `[couplet 1, ligne 3 : là depuis la version 2.0]` | `empilement` ; « 2.0 » forme une seule unité | **`version`**, carton ≈ 11,1 s, 4 temps, tampon avec `coup` |
| 5 | 13,3–16,4 | couplet, ligne 4 | `braise` | `[couplet 1, ligne 4 : serveur en panne à cause de MCP]` | à 13,3 : `chute-de-pile` vers `braise` (9,4 s après la précédente) | **`serveur-panne`**, carton ≈ 14,0 s, 4 temps, la diode passe au rouge sur le temps suivant ; voir `frame-3` |
| 6 | 16,4–19,5 | couplet, ligne 5 | `braise` | `[couplet 1, ligne 5 : les clés d'API]` | `empilement` ; dernière unité tenue ; le carton reste jusqu'à la fin | **`cles-api`**, carton ≈ 17,3 s, tenu jusqu'à 19,5 |

Image de fin (19,5 s) : mur de 2 lignes en `braise`, ligne 5 vive, carton `cles-api`. Pas de noir, pas de fondu.

Écarts entre débuts de cartons : 2,4 s · 3,5 s · 2,9 s · 3,3 s. Le premier écart est juste sous la règle des 2,5 s : décaler `lignes` d'un temps (≈ 8,0 s) si l'aperçu le confirme.

## Suite, pour une version longue de 36 s (hors `check.py`)

| Temps (s) | Section | Camaïeu | Texte | Visuel |
|---|---|---|---|---|
| 19,5–22,9 | `[ligne : encore un .md]` | `braise` | mot-clé ≈ 20,4 s | `fichier-md`, la pile gagne une feuille |
| 22,9–27,4 | `[ligne : un mauvais changement]` | `braise` | mot-clé ≈ 26,0 s | `mauvais-changement`, la croix tombe en `coup` |
| 27,4–36,0 | `[refrain : ça livre, ça livre]` | `nuit` (`chute-de-pile` à 27,4) | une répétition par unité | `ship`, un tampon par répétition, 2 cartons au plus sur le passage |

## Images fixes à livrer (`stills/`)

0,4 s (accroche) · 5,4 s (carton `plan-mode`) · 11,3 s (mur de 2 lignes + `version`) · 14,2 s (`braise`, `serveur-panne`) · 19,3 s (fin).

## Critères de fin pour l'agent qui code

1. `check.py` passe sur le dossier du short (piste audio silencieuse, `narration.json` avec `lines: []`).
2. Sur les 5 images fixes : aucun texte hors de x 64–940 et y 220–1 560, aucune taille sous 56 px, un seul carton.
3. `apercu_metronome.mp4` : les entrées d'accent 1 et 2 tombent sur le clic.
4. `apercu_avec_musique.html` s'ouvre et suit le lecteur YouTube.
5. Rien dans `git status` ne contient l'audio ni les paroles réelles.

## Remplacer le remplissage par les vraies paroles

Hamdi confirme le texte → `paroles.txt` dans `~/git/StudioVisualIdentity-sources/lyrics-claudes-plan/` → étapes 3 à 7 de `pipeline.md` avec le `transcription-mots.json` déjà présent → relecture aux deux aperçus → rendu avec `?data=` vers le `lyrics.json` hors dépôt.
