---
name: fabrique-identites
description: Orchestre la création de nouvelles identités visuelles de shorts pour ce dépôt, à partir du catalogue des librairies (out/library-cards/catalogue.md). L'orchestrateur ne produit rien lui-même, il fait tout faire par des sous-agents Opus 5.5 (préparation, repérage, challenge adversarial, studios, intégration, revue), puis commit et ouvre la PR. Sait aussi enrichir le catalogue (rescan du dépôt) et challenger une identité existante. Déclencheurs - « nouvelles identités », « génère N identités », « fabrique d'identités », « enrichis le catalogue », « challenge l'identité X », /fabrique-identites.
---

# Fabrique d'identités

Ce skill fait de la session un **chef d'orchestre**. Il ne lit le dépôt que pour briefer, décider et livrer.
Tout ce qui exécute du code (installer, écrire une scène, rendre, mesurer, rédiger un design system, relire,
réviser le catalogue) est confié à un sous-agent lancé avec l'outil `Agent`, `subagent_type: "general-purpose"`
et **`model: "opus"` (Opus 5.5), sans exception, y compris l'agent adversarial**. Les sous-agents ne commitent jamais ;
seul l'orchestrateur commit, pousse et ouvre la PR.

Le rôle de ce dépôt : produire le maximum d'identités visuelles prouvées (menu avec preuves). Le choix d'un style pour une
chaîne donnée revient à StudioGabarit, pas à ce skill.

## Modes

- `/fabrique-identites N` (défaut N = 2) : produit N nouvelles identités complètes.
- `/fabrique-identites catalogue` : rescanne le dépôt et met le catalogue à jour (voir « Enrichir le catalogue »).
- `/fabrique-identites challenge <slug>` : lance seulement l'agent adversarial sur une identité existante.

## Sources à donner aux agents (chemins relatifs à la racine du dépôt)

| Fichier | Pour quoi |
|---|---|
| `out/library-cards/catalogue.md` | la base : chaque librairie, son statut, déjà utilisée ou non, où |
| `out/identities/index.json` | les identités existantes : `curation.signatureToPreserve`, `curation.confusableWith`, palettes, familles |
| `out/identities/<id>/contact-sheet.jpg`, `out/report/directions-contact-sheet.jpg` | regarder avant de proposer |
| `out/tools/STUDIO_BRIEF.md` | les règles de production d'un studio, les schémas `short.json`, `narration.json`, cartes, `identity.md` |
| `out/report/facts.md`, `out/report/failures.md` | pièges mesurés, coûts de rendu, ce qui a échoué |
| `AGENTS.md` | format des livrables, voix off Fish Audio « Arnold », zones sûres, contraintes |
| `out/tools/catalogue_scan.py` | rescan des librairies réellement importées (base de l'enrichissement) |

## Déroulé pour N identités

Chaque étape est un brief complet : le sous-agent ne connaît que ce qu'on lui écrit. Lancer en parallèle tout ce qui est
indépendant ; attendre la notification de fin, ne pas interroger en boucle.

0. **Branche** (orchestrateur) : `git fetch origin main` puis repartir de `origin/main` sur la branche de travail.
1. **Préparation** (1 agent) : `npm i`, venv Python 3.11 (`uv`), paquets listés dans `AGENTS.md` § Set-up avec les
   contournements de `facts.md` (Manim sans manimpango), Playwright déjà présent (ne jamais `playwright install`).
   Fumée obligatoire : stills d'un short existant avec `render.mjs`, `sound.py`, `assemble.py mux`, `check.py` ;
   mesurer les s/100 images à vide. Vérifier si les outils MCP Fish Audio sont joignables depuis un sous-agent.
2. **Repérage** (1 agent, en parallèle de 1) : proposer 2N directions, chacune ancrée sur au moins une ligne « Non » du
   catalogue (ou une combinaison jamais faite), réalisable dans le pipeline image par image (`window.renderAt(t)` ou
   script Python qui produit des images à un temps t, CPU seul, SwiftShader), sans asset téléchargé. Par direction :
   slug, nom, promesse, signature en 4 traits, palette hex avec contrastes, typos @fontsource, mouvement, 2 familles
   avec 2 sujets concrets chacune (titres français non encore traités dans `out/shorts`), public, librairies,
   les identités voisines et 3 différences concrètes, coût estimé, risques. Sortie : `out/report/notes/directions-<date>.md`.
3. **Challenge amont** (1 agent adversarial) : attaque chaque direction : confusion avec les identités existantes (citer
   leur `signatureToPreserve`), faisabilité réelle de la librairie (version, API, SwiftShader), coût CPU, cohérence
   public/famille, photosensibilité, promesse creuse. Verdict par direction : garder / modifier (correctif concret) / écarter,
   et un classement. Sortie : `out/report/notes/challenge-<date>.md`.
4. **Sélection** (orchestrateur) : choisir N directions en lisant 2 et 3 ; assigner les sujets pour éviter les doublons
   entre studios ; noter la décision dans `out/report/decisions.md`.
5. **Studios** (N agents en parallèle, un par identité) : brief = règles de `STUDIO_BRIEF.md` (livrables, schémas, cycle
   stills → rendu → son → mux → QA, un seul rendu complet par short) + la direction retenue + les correctifs du challenge
   + les sujets assignés + l'obligation d'écrire les brouillons de cartes `out/library-cards/_drafts/<slug>__<lib>.json`
   et le journal `out/report/notes/<slug>.md`. Livrable : `out/identities/<slug>/` complet (identity.md 16 sections,
   tokens.json, recipes, poster, contact-sheet) et 2 shorts de preuve (`short_novo.mp4`, `short.json`, `narration.json`,
   `stills/`, `src/` avec README de reproduction), `check.py` OK.
6. **Voix off** : Fish Audio « Arnold » (`d704cf8f1216490cbfbed89955f0e938`, `s2.1-pro`), une ligne de `narration.json`
   par appel, texte seul, `voice_lines/NN.mp3`, puis `tts.py --engine files --replace` short par short. Par l'agent
   d'intégration si le connecteur lui est joignable, sinon par l'orchestrateur (seule exception au « rien soi-même »,
   parce que le connecteur peut n'être joignable que depuis la session). Cela dépense des crédits : le dire dans le rapport.
7. **Intégration** (1 agent) : `aggregate.py` (fusion des cartes), `build_index.py`, `check.py --all`, `recognition.py`
   (sur copie si on veut garder l'ancien rapport), mise à jour de `comparison.md`, `README.md`, `AGENTS.md` (nombres
   d'identités et de shorts, tableau par famille), `catalogue.md` (lignes passées à « Oui » avec « Où »), vitrine
   `out/showcase/build.py`.
8. **Revue adversariale aval** (1 agent) : juge aveugle sur des frames anonymisées (chaque nouvelle identité doit être
   reconnue entre elle-même et ses voisines), conformité d'`identity.md` (16 sections dans l'ordre), `tokens.json` contre
   `core-tokens.schema.json`, zones sûres et tailles de texte sur les stills, cohérence `short.json` / `narration.json`
   (lignes sans chevauchement, débit ≈ 2,6 mots/s), poids des mp4. Verdict : bloquant / à corriger / accepté. Un seul
   tour de corrections par les studios concernés, puis re-vérification ciblée.
9. **Livraison** (orchestrateur) : commit par lots cohérents, push, PR avec le résumé des identités, des coûts mesurés,
   des crédits voix dépensés et des défauts acceptés ; abonnement à la PR.

## Enrichir le catalogue

Un agent (Opus 5.5) exécute `python3 out/tools/catalogue_scan.py --check` : il liste les librairies réellement importées
par les shorts, les outils, la démo et les skills, et signale les écarts avec `catalogue.md` (ligne « Non » alors que la
librairie est importée, ligne « Oui » sans fichier, librairie importée absente du tableau). L'agent corrige les lignes,
ajoute les nouvelles (catégorie, statut, Oui/Non, Où) et met à jour le bilan et la date. Il ne retire jamais une ligne
« Non » : ce sont les pistes à explorer.

## Règles qui ne se discutent pas

- Pas de scène, de rendu, de design system ni de relecture écrits par l'orchestrateur : un sous-agent Opus 5.5 à chaque fois.
- Une nouvelle identité garde **une** signature (type, palette, transition signature) distincte de toutes les voisines ;
  si le challenge ou la revue la juge confusable, on change la direction, pas la présentation.
- Pas d'asset téléchargé, pas de personnage, logo ni œuvre existants, faits exacts dans les explicatifs, photosensibilité
  (≤ 3 flashs/s, pas de flash plein cadre).
- Les coûts de rendu sont mesurés et écrits (`renderTimeSec`), jamais estimés dans les livrables.
- Jamais plus de 4 rendus simultanés (slots de `render.mjs`), les rendus complets en arrière-plan.
