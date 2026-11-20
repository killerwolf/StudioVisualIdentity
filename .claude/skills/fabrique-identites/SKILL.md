---
name: fabrique-identites
description: Orchestre la création de nouvelles identités visuelles de shorts pour ce dépôt, à partir du catalogue des librairies (out/library-cards/catalogue.md). L'orchestrateur ne produit rien lui-même, il fait tout faire par des sous-agents Opus 5.5 (préparation, repérage, challenge adversarial, studios, intégration, revue), puis commit et ouvre la PR. Sait aussi créer une nouvelle recette à partir de briques existantes (un habillage et une mécanique du dépôt, sans nouvelle identité), enrichir le catalogue (rescan du dépôt) et challenger une identité existante. Déclencheurs - « nouvelles identités », « génère N identités », « fabrique d'identités », « nouvelle recette », « mets l'habillage X sur la mécanique Y », « compose X × Y », « enrichis le catalogue », « challenge l'identité X », /fabrique-identites.
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
- `/fabrique-identites recette <habillage> <mecanique> [<format>]` : compose une **nouvelle recette** avec des briques qui
  existent déjà (voir « Nouvelle recette à partir de briques existantes »). C'est le mode à prendre dès qu'on veut une pâte
  connue sur un mouvement connu : ce n'est **pas** une nouvelle identité.

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
| `out/habillages/`, `out/mecaniques/`, `out/formats/`, `out/recettes/` | les briques (modèle « vidéo = habillage × mécanique × format (+ son) », `out/report/notes/composition/proposition.md`) : une fiche par brique, une recette par combinaison nommée ; `out/recettes/README.md` les explique, `out/recettes/propositions.json` liste les cases proposées non rendues |
| `out/identities/index.json` → `habillages[]`, `mecaniques[]`, `recettes[]`, `compatibilite[]` | la matrice calculée (états `teste`, `compatible`, `a-tester`, `incompatible`) : où chercher une combinaison avant de la proposer |
| `out/showcase/README.md`, `build.py`, `page.tpl.html` | la vitrine publiée (artifact claude.ai https://claude.ai/artifact/VJEgxZpSjAn3cGGb51c1nK) : comment la régénérer et la republier |

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
   d'identités et de shorts, tableau par famille), `catalogue.md` (lignes passées à « Oui » avec « Où »), et la **vitrine** :
   ajouter les nouvelles identités à `ORDER` dans `out/tools/build_index.py` (et à `REHAB` si besoin), mettre à jour les
   chiffres fixes de `page.tpl.html` (en-tête, « N° x / N », tests de reconnaissance, limites, voix), régénérer
   `out/showcase/build/` avec `.venv/bin/python out/showcase/build.py` et vérifier `index.html` dans un navigateur
   (Playwright) : toutes les identités, tous les shorts, aperçus et posters présents.
8. **Revue adversariale aval** (1 agent) : juge aveugle sur des frames anonymisées (chaque nouvelle identité doit être
   reconnue entre elle-même et ses voisines), conformité d'`identity.md` (16 sections dans l'ordre), `tokens.json` contre
   `core-tokens.schema.json`, zones sûres et tailles de texte sur les stills, cohérence `short.json` / `narration.json`
   (lignes sans chevauchement, débit ≈ 2,6 mots/s), poids des mp4. Verdict : bloquant / à corriger / accepté. Un seul
   tour de corrections par les studios concernés, puis re-vérification ciblée.
9. **Livraison** (orchestrateur) : commit par lots cohérents, push, PR avec le résumé des identités, des coûts mesurés,
   des crédits voix dépensés et des défauts acceptés ; abonnement à la PR. Puis **republier la vitrine** avec l'outil
   Artifact sur la même adresse (`url` = https://claude.ai/artifact/VJEgxZpSjAn3cGGb51c1nK, `file_path` =
   `out/showcase/build/index.html`, `root` = `out/showcase/build`, `files` = tous les `v/*.mp4` et `p/*.jpg`, ≤ 64 Mo et
   ≤ 255 fichiers par publication, en plusieurs publications sinon) et vérifier la page publiée. La vitrine fait partie
   du livrable : une identité absente de la page n'est pas livrée.
   Piège connu de l'environnement cloud : si `git push` échoue avec « missing necessary objects » en n'envoyant aucun objet
   (`Total 0`), c'est la négociation de push injectée dans la configuration (`push.negotiate=true`) qui croit à tort que le
   serveur a déjà les objets ; pousser avec `git -c push.negotiate=false push`. Un refus « fatal error in commit_refs » vient
   de GitHub lui-même : attendre et retenter.

## Nouvelle recette à partir de briques existantes

Règle (proposition.md § 2.5, généralise `variantOf`) : **une nouvelle pâte sur une mécanique existante, ou une pâte existante
sur une autre mécanique, est une nouvelle recette (et, pour une pâte neuve, un nouvel habillage), pas une nouvelle
identité.** Pas de dossier `out/identities/<id>/` sauf si on écrit un design system complet ; pas d'entrée dans `ORDER` ni
`CURATION` de `build_index.py`. Exemples dans le dépôt : `chemin-grille-suisse` (recette adoptée « Données qui se tracent »,
essai C2), `chemin-craie-verte` (essai C1), `papier-plan-bleu` (essai C4, abandonné).

Déroulé (mêmes règles que plus haut : tout ce qui exécute est fait par un sous-agent Opus 5.5, l'orchestrateur briefe,
regarde, décide et commit) :

1. **Lire la case** (orchestrateur) : dans `out/identities/index.json`, `compatibilite[]` pour le couple (clé de pâte =
   `habillage` ou `famille/variante`, ex. `craie/tableau-vert`). `teste` = existe déjà (ne pas refaire) ; `incompatible` = raison
   écrite, ne pas lancer sans la lever ; `a-tester` = la fiche de l'habillage donne ce que demande `mecanique.requiert`, mais
   pas d'adaptateur (lire `alerte` : cadence 12 i/s, grille pixel) ; case absente = inconnue : vérifier `requiert` (rôles de
   palette, projection, crochets) contre `habillage.json` avant de proposer. Une mécanique `declare` (code copié dans chaque
   short) n'accepte pas d'habillage sans écrire un moteur : choisir de préférence une mécanique `executable` (`trace-chemin`,
   `pop-papier-12ips`). Si la case n'est pas dans `out/recettes/propositions.json`, l'y ajouter avec sa question et son coût.
2. **Adaptateur** (1 agent) : un fichier **à côté** de l'existant, jamais une modification d'un moteur partagé ni d'un short
   existant : `out/shared/chemin-moteur/habillages/<habillage>.js` (partir d'un habillage voisin, mêmes crochets) ou un thème
   JSON du moteur papier (dans le dossier du nouveau short tant que la recette est un essai, comme C4). Les couleurs et la police
   de titre de l'adaptateur doivent être celles de `habillage.json` (`check.py --briques` le contrôle) ; si l'habillage n'a pas
   de fiche, en écrire une (`out/habillages/<id>/habillage.json`, niveau `declare` ou `executable`). Deux pâtes de la même
   matière en deux tons = une **famille** à variantes (`out/habillages/craie/` : `variantes/<v>.json`), pas deux habillages.
3. **Contenu et voix** : réutiliser de préférence un texte et une voix qui existent (les trois essais l'ont fait : aucun
   appel de voix) ; sinon, voix comme au § 6 ci-dessus.
4. **Short** (1 agent) : dossier `out/shorts/<recette>__<famille>__<sujet>/` (livrables habituels de `STUDIO_BRIEF.md`) dont le
   `short.json` déclare `recette`, `habillage` (+ `variante`), `mecanique`, `format`. Un seul rendu à la fois. `check.py` OK, et
   l'audit de la mécanique s'il existe (`chemin_audit.mjs`).
5. **Recette** (orchestrateur) : `out/recettes/<id>.json` avec `habillage`, `variante`, `mecanique`, `formats`, `statut`
   (`essai` tant qu'Hamdi n'a pas validé ; `validee` ; `abandonnee`, short gardé), `case` si elle vient de la matrice,
   `question`, `shorts`, `adaptateur`, `signaturePortee` (quelle brique porte la signature), `posterT`. Mettre à jour les
   `recettes` des fiches d'habillage et de mécanique concernées.
6. **Contrôles** : `python3 out/tools/check.py --briques` (0 erreur), `python3 out/tools/check.py --all`,
   `python3 out/tools/build_index.py` (la case passe à `teste`), puis `.venv/bin/python out/tools/recognition.py --briques`
   (`out/report/recognition-briques.json` ; ne pas lancer le mode par défaut, qui réécrit `recognition.json`) : la nouvelle
   recette doit rester voisine de son habillage parmi les shorts d'**une autre** mécanique, et de sa mécanique parmi les shorts
   d'**un autre** habillage (tests croisés). Une recette à un seul short est notée « sans pair », ce n'est pas un échec.
7. **Regarder et juger soi-même** (orchestrateur) : planche contact et comparaison aux mêmes instants avec les shorts de
   l'habillage et de la mécanique d'origine (modèle : `out/report/notes/composition/essais/`), verdict écrit dans
   `essais.md` ; ne pas relayer l'auto-évaluation de l'agent.
8. **Vitrine** : `.venv/bin/python out/showcase/build.py` (la case et le short apparaissent seuls dans « Composer », lus dans
   l'index ; n'encode que les aperçus nouveaux). Republier seulement si Hamdi le demande.

## Enrichir le catalogue

Un agent (Opus 5.5) exécute `python3 out/tools/catalogue_scan.py --check` : il liste les librairies réellement importées
par les shorts, les outils, la démo et les skills, et signale les écarts avec `catalogue.md` (ligne « Non » alors que la
librairie est importée, ligne « Oui » sans fichier, librairie importée absente du tableau). L'agent corrige les lignes,
ajoute les nouvelles (catégorie, statut, Oui/Non, Où) et met à jour le bilan et la date. Il ne retire jamais une ligne
« Non » : ce sont les pistes à explorer.

## Règles qui ne se discutent pas

- Pas de scène, de rendu, de design system ni de relecture écrits par l'orchestrateur : un sous-agent Opus 5.5 à chaque fois.
- Une nouvelle identité qui réutilise un moteur existant et ne change que le fond, la palette et les polices n'est **pas** une nouvelle identité : depuis le 20/11/2026, c'est une **nouvelle recette** (mode `recette` ci-dessus). Les 3 dérivations de Papier découpé restent enregistrées comme `variantOf` dans `build_index.py` (`FAMILIES`) pour les lecteurs actuels de l'index ; on n'en ajoute plus de nouvelles par ce biais.
- Une nouvelle identité garde **une** signature (type, palette, transition signature) distincte de toutes les voisines ;
  si le challenge ou la revue la juge confusable, on change la direction, pas la présentation.
- Pas d'asset téléchargé, pas de personnage, logo ni œuvre existants, faits exacts dans les explicatifs, photosensibilité
  (≤ 3 flashs/s, pas de flash plein cadre).
- Les coûts de rendu sont mesurés et écrits (`renderTimeSec`), jamais estimés dans les livrables.
- Jamais plus de 4 rendus simultanés (slots de `render.mjs`), les rendus complets en arrière-plan.
