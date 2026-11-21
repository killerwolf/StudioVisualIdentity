# StudioVisualIdentity

[![Un prompt, 18 styles visuels pour vos vidéos courtes](out/demo/thumb/hero_fr.jpg)](out/demo/demo_16x9.mp4)

**Donnez un style unique à votre chaîne de vidéos courtes, en un seul prompt.**

## En un prompt

Donnez ce texte à votre agent (Claude Code ou un autre), en remplaçant ce qui est entre crochets :

```text
Lis AGENTS.md de https://github.com/killerwolf/StudioVisualIdentity.
Choisis le style qui convient à une chaîne de [sujet, ex. quiz de géographie] pour [public, ex. ados de 13 à 17 ans] en [langue].
Crée notre studio avec out/tools/bootstrap_studio.py, adapte l'identité visuelle à notre chaîne,
puis réalise notre premier épisode sur [sujet de l'épisode] et montre-moi le résultat.
```

L'agent choisit le style, crée un projet séparé pour votre chaîne (votre identité, des modèles de scènes, les outils de rendu), puis réalise l'épisode.

## La démo (41 s, avec le son)

▶ [16:9](out/demo/demo_16x9.mp4) · [9:16 vertical](out/demo/demo_9x16.mp4)

18 identités visuelles prêtes à l'emploi pour TikTok, Reels et Shorts, chacune prouvée par de vraies vidéos, et un agent qui crée votre studio et fabrique vos premiers épisodes.

## Ce que vous obtenez

- **18 identités complètes, 21 déclinaisons** : couleurs, typographies, mouvements, transitions, structure d'un short, sons. Chacune est décrite comme un design system lisible par un agent.
- **45 vraies vidéos de preuve**, rendues par du code : images, mouvements et sons, sans image ni musique téléchargée. Les voix off viennent de Fish Audio (31 shorts) et de Gemini (14 shorts). Les seules exceptions sont les sons et polices du moteur papier, et des données factuelles libres comme les côtes Natural Earth.
- **Des styles vraiment différents** : un juge indépendant, sans contexte, a classé à l'aveugle 72 images des 18 identités sans une seule erreur.
- **Un studio prêt à produire** : modèles de scènes, rendu image par image, voix off et sons mixés, contrôle qualité.
- **Tout est open source.**

## Ce que ce dépôt fait, et ce qu'il ne fait pas

**Il fait** : choisir un style et le prouver, puis produire des épisodes avec votre agent, un par un.

**Il ne fait pas** la chaîne complète : écriture et validation des sujets, relecture, publication, programmation. Ce dépôt n'est relié à aucun outil de pilotage. Si vous avez déjà votre propre modèle de studio, servez-vous de ce dépôt seulement pour **choisir le style**, puis transposez-le dans votre moteur.

## Les 18 identités

| Identité | En une phrase | Familles prouvées |
|---|---|---|
| [**Grille Suisse**](out/identities/swiss-data/identity.md) | Un chiffre qui claque par écran, posé sur une grille 12 colonnes visible, révélé par des volets rouges nets | evenements, geographie |
| [**Gazette 1900**](out/identities/gazette-1900/identity.md) | Chaque grand moment arrive comme une une de journal qui tourbillonne, se pose sur la pile et se fait tamponner | evenements, histoire |
| [**Arcade Pixel**](out/identities/pixel-arcade/identity.md) | Une vraie simulation physique, déterministe, filmée comme une partie d'arcade | abstrait, engagement |
| [**Brut Mème**](out/identities/brut-meme/identity.md) | Un fait ou un défi par coupe, en lettres géantes qui claquent sur le beat | engagement, evenements |
| [**Carte Météo**](out/identities/carte-meteo/identity.md) | Une carte météo claire où les isobares respirent, le vent file et un front balaie l'écran pour changer de plan | evenements, geographie |
| [**Bauhaus Cinétique**](out/identities/bauhaus-kinetic/identity.md) | Des formes primaires qui s'emboîtent sur une grille stricte pour expliquer ou défier en 15 secondes | engagement, explicatif |
| [**Tableau Craie**](out/identities/tableau-craie/identity.md) | Un prof bienveillant t'explique le monde en le dessinant à la craie | enfants, explicatif |
| [**Zine Riso**](out/identities/riso-zine/identity.md) | Un chiffre fort, une forme découpée, une annotation au marqueur | evenements, geographie |
| [**Trait continu**](out/identities/trait-continu/identity.md) | Un seul trait, jamais levé, dessine l'idée devant toi | enfants, geographie |
| [**Survol pixel**](out/identities/survol-pixel/identity.md) | Chaque sujet devient un petit monde en pixel art 16 bits que la caméra survole, puis frôle jusqu'à l'horizon | explicatif, histoire |
| [**Diorama Pastel**](out/identities/pastel-diorama/identity.md) | Un monde de jouets doux pour les 6–10 ans, où chaque idée « saute » en place avec un rebond | enfants, engagement |
| [**Relief Topo**](out/identities/topo-relief/identity.md) | Chaque sujet devient un terrain qu'on survole | geographie, histoire |
| [**Atlas Gravé**](out/identities/atlas-grave/identity.md) | Un savoir qui s'imprime à l'encre sur une carte gravée, et finit sur une question ouverte | geographie, histoire |
| [**Aquarelle Conte**](out/identities/aquarelle-conte/identity.md) | Chaque short est une page d'album | enfants, histoire |
| [**Labo Néon**](out/identities/neon-lab/identity.md) | Une nuit de laboratoire où la science se voit en lumière | abstrait, explicatif |
| [**Cosmos Doc**](out/identities/cosmos-doc/identity.md) | Un plan de cinéma sur un vrai objet du ciel, où un seul chiffre suffit à donner le vertige | evenements, explicatif |
| [**Chrome Liquide**](out/identities/liquid-chrome/identity.md) | Une matière liquide, chromée et hypnotique qu'on regarde couler jusqu'au bout | abstrait, engagement |
| [**Papier découpé (+ 3 déclinaisons)**](out/identities/papier-decoupe/identity.md) | Chaque idée est une pièce de papier découpée qui saute sur un tapis de découpe vert, en stop-motion | explicatif, histoire |

Vue d'ensemble : [`out/report/directions-contact-sheet.jpg`](out/report/directions-contact-sheet.jpg). Chaque identité a sa planche dans `out/identities/<id>/contact-sheet.jpg`.

## Ce que vous devrez faire ou valider

- **Valider l'identité** proposée par l'agent (nom, couleurs, ton) avant de produire en série.
- **Fournir une clé de voix** : `GEMINI_API_KEY` (la recette utilisée ici est dans [`out/report/notes/voix-lot2.md`](out/report/notes/voix-lot2.md)) ou Fish Audio. Ajoutez `FREESOUND_API_KEY` si vous voulez d'autres bruitages que ceux fournis.
- **Regarder et écouter chaque épisode** avant de le publier. L'agent mesure les niveaux sonores, mais il ne peut pas écouter.
- **Relire les faits** énoncés dans chaque épisode.

## Pour aller plus loin

- [`AGENTS.md`](AGENTS.md) : le guide détaillé pour les agents (en anglais).
- [`out/identities/index.json`](out/identities/index.json) : les 18 identités en données (couleurs, polices, public conseillé, coût de rendu).
- [`out/report/`](out/report/README.md) : le rapport complet de l'exploration, comparaisons et tests à l'aveugle compris.
- **Créer de nouvelles identités** : le skill Claude Code `fabrique-identites` (`.claude/skills/fabrique-identites/`) les fait fabriquer par des sous-agents, à partir du [catalogue des librairies](out/library-cards/catalogue.md).
- **Sound design** : le skill [`sound-design`](https://github.com/killerwolf/skills/tree/main/skills/sound-design) du plugin `studio` (`claude plugin marketplace add killerwolf/skills` puis `claude plugin install studio@killerwolf`).
- [`out/demo/`](out/demo/README.md) : comment la vidéo démo est fabriquée.
