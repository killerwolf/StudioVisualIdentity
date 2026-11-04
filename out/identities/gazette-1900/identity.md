# Gazette 1900

## Nom
**Gazette 1900** — le journal inventé *Le Petit Crieur*, édition spéciale. Slug : `gazette-1900`.

## Promesse en une phrase
Chaque grand moment arrive comme une une de journal qui tourbillonne, se pose sur la pile et se fait tamponner : l'histoire racontée à la vitesse d'un crieur de rue, avec le grain d'une actualité filmée.

## Mood & références de genre
Crieur de journaux, « Édition spéciale ! », urgence d'antan. Références de genre (aucune œuvre précise) : unes de presse quotidienne fin XIXe – début XXe, actualités filmées muettes, gravures sur bois en hachures, tampons administratifs, dépêches d'agence tapées à la machine. Ton : sérieux, rythmé, un peu emphatique, jamais parodique.

## Palette (rôles : fond, surface, accent 1-3, texte, danger/succès)
| Rôle | Valeur | Usage réel dans les shorts |
|---|---|---|
| fond (papier) | `#E9E1CF` | fond de chaque une |
| surface | `#D8CDB4` | blocs de béton (mur 1989), aplats secondaires |
| accent 1 — rouge tampon | `#B3261E` | kicker, tampons, labels de dépêche, dates du récapitulatif, cocarde, bonnets, compteur « 37 » |
| accent 2 — encre | `#1E1B18` | tout le texte, filets, hachures, silhouettes |
| accent 3 — fond de gravure | `#E4DAC4` | intérieur des plaques gravées, frise |
| texte | `#1E1B18` | contraste encre/papier ≈ 13:1 (AA largement) ; rouge/papier ≈ 5,6:1 |
| table (desk) | `#1E1B18` | visible seulement pendant le tourniquet de la 1re une et dans les coins des unes inclinées |
| danger / succès | `#B3261E` / `#1E1B18` | pas de vert : le rouge signale l'événement, l'encre fait foi |

Après post-traitement OpenCV, la palette est virée sépia (B×0,955, G×0,985) et vignettée de 30 % max dans les coins.

## Typographie (familles @fontsource, tailles, graisses, interlettrage)
- **Manchette du journal** « LE PETIT CRIEUR » : Playfair Display 900, 92 px, +1 px.
- **Date-titre (display)** : Playfair Display 900, 230 px ajusté à la colonne de 900 px (`fitWidth`, min 120 px ; 300 px pour les unes-titres « 1789 »), interlettrage −4 px, interligne 0,86, chiffres alignés.
- **Titre d'événement (title)** : Playfair Display 900, 84 px, 2 lignes max avec `<br>` explicite (réduit jusqu'à 62 px si besoin).
- **Kicker** : DM Serif Display 400, 60 px, rouge.
- **Légende (caption)** : DM Serif Display italique, 54 px, une ligne.
- **Dépêche (body)** : IBM Plex Mono 500, 54 px, interligne 1,16 ; label en 700 rouge (« DÉPÊCHE — », « ARTICLE 1 — », « VOTEZ — », « ET VOUS ? ») ; curseur ▌ clignotant à 1,5 Hz.
- **Ligne méta** : IBM Plex Mono 500, 54 px (date à gauche, prix à droite, sans jour de semaine pour tenir sur une ligne).
- **Tampon** : DM Serif Display 400, 60 px, capitales, +3 px, cadre 7 px + filet intérieur 2 px, fond papier 90 %.
- Taille minimale de tout texte lisible : **54 px**.

## Formes & matières
Une une = feuille 1080×1920 avec double filet (3 px + 1 px à 12 px), colonne unique de 900 px (x 60 → 960), filets épais/fins sous la manchette. Gravure 894×430 dans un cadre 3 px : **tout est dessiné en hachures** (canvas 2D) — lignes horizontales d'épaisseur variable pour ciels et fumées, hachures verticales ombrées pour cylindres (tours, colonnes), rayons alternés fin/épais pour soleils et feux d'artifice. Silhouettes **inventées** en encre pleine (tête + épaules + buste, chapeaux génériques : tricorne, haut-de-forme, calotte, bonnet rouge ; bras levé). Matière finale : papier taché, fibres, bavure d'encre, grain argentique, rayures et poussières de pellicule (OpenCV).

## Langage de mouvement (easings nommés, durées, staggers, ce qu'on ne fait jamais)
Grille **128 bpm** (temps = 0,46875 s) ; **une une = 6 temps = 2,8125 s** (unes d'ouverture/clôture : 4 ou 8 temps).
- **Tourniquet** (entrée de une) : rotation −540° → ±1,1–1,6° (alterné), échelle 0,06 → 1, **0,55 s `power3.out`**. La une précédente reste dessous et s'assombrit à 45 % (`power1.in`, 0,55 s) : la pile se lit dans les coins.
- **Coup de tampon** : échelle 2,6 → 1, rotation +6° → ±7–8°, opacité 0 → 1, **0,16 s `power4.in`**, à +1,5 temps (0,62 s sur la 1re une).
- **Dépêche typewriter** : 34 caractères/s (40–70 pour listes et chiffres), démarre à +0,62 s.
- **Zoom brusque** : ×1,1 en **0,14 s `expo.out`** à +4 temps, centré sur la manchette.
- **Ken Burns** : ×1,05–1,07 linéaire sur la gravure pendant toute l'une.
- **Staggers** : lignes de récapitulatif 0,26 s ; blocs du mur 0,045 s (`power2.in`, 0,62 s) ; chiffres-dépêches tous les 3 temps.
- **Jamais** : fondus enchaînés lents, rebonds élastiques, glissements « app moderne », texte qui flotte hors d'une une, couleurs hors palette.

## Langage de caméra (cadrages, mouvements, focale, profondeur de champ)
2D frontale, orthographique. Cadre plein sur la une (légèrement inclinée). Mouvements : zoom brusque sur la manchette, Ken Burns lent sur la gravure, **tremblement de projecteur** (gate weave ±2 px, sinusoïdes 3–18 Hz, OpenCV) et **flicker** de luminosité ±4 %. Pas de profondeur de champ : la profondeur vient de la pile d'unes assombries.

## Transitions (liste nommée, durée, quand les utiliser)
| Nom | Durée | xfade ffmpeg équivalent | Quand |
|---|---|---|---|
| tourniquet | 0,55 s | aucun (dans la scène GSAP) | à chaque nouveau beat narratif, sur le temps fort |
| flash de coupe | 2 frames (0,067 s) | `fadewhite` | au départ de chaque tourniquet (OpenCV `--flash`) |
| coup de tampon | 0,16 s | aucun | révéler le mot-clé de l'une |
| coupe sèche | 0 s | aucun | si l'on assemble des plans séparés |

## Structure type d'un short (hook 0–1 s, développement, chute, fin/boucle)
- **0–0,6 s (hook)** : la première une est déjà en plein tourbillon à la frame 0, se pose à 0,5 s, tampon rouge à 0,62 s (« Édition spéciale »).
- **Développement** : une une par date/fait (6 temps chacune) : tourniquet → tampon → dépêche tapée → zoom brusque.
- **Chute** : une de clôture (récapitulatif, compteur, frise) avec la question à l'audience dans la dépêche.
- **Fin** : tampon « Au prochain numéro » (signature de l'identité) et tenue ~0,5 s ; pas de boucle parfaite (fin propre).

## Zones sûres
Haut 220 px (la manchette commence à y = 228), bas 320 px (la dépêche finit avant y = 1600), droite 120 px (colonne x 60 → 960). Le zoom brusque ×1,1 fait déborder les bords décoratifs de ~30 px dans la marge droite : seulement le cadre de la gravure, jamais un texte.

## Librairies recommandées et pourquoi
- **GSAP** (indispensable) : timeline unique seekée (`tl.seek(t,false)`, `immediateRender:false`) — déterministe image par image, idéale pour tourniquets, tampons, chutes de blocs, compteur. Coût mesuré : 65 s/100 frames sous forte contention CPU (10 studios), la page DOM 1080×1920 est le coût, pas GSAP.
- **OpenCV** (indispensable pour la matière) : post-traitement par frame via pipes ffmpeg (`post.py`), 27,6 s/100 frames ; c'est lui qui fait passer la page vectorielle propre pour une pellicule.
- Canvas 2D natif pour les gravures en hachures (aucune dépendance).
- Compatibles : roughjs (traits tremblés), d3 (cartes/frises gravées) ; à éviter : three/babylon (la 3D casse le mensonge de l'imprimé).

## Familles de contenus adaptées / inadaptées
- **Adaptées** : `histoire` (chronologies, « X en N secondes »), `evenements` (anniversaires « Ce jour-là », éphémérides), `geographie` historique (cartes gravées), `engagement` (vote dans la dépêche).
- **Inadaptées** : `enfants` (trop sérieux, texte dense), `abstrait` (l'identité vit du texte imprimé), `explicatif` scientifique moderne (le grain d'antan brouille les schémas précis).

## Shorts de preuve (chemins)
- `out/shorts/gazette-1900__histoire__1789-en-20-secondes/short.mp4` (18,75 s)
- `out/shorts/gazette-1900__evenements__9-novembre-1989-mur-de-berlin/short.mp4` (15,0 s)

## Place de la voix off (où elle parlera, débit conseillé, ce que le visuel laisse libre)

> **Voix réellement utilisée pour tous les shorts : Fish Audio « Arnold »** (`d704cf8f1216490cbfbed89955f0e938`, modèle `s2.1-pro`, conteur masculin FR). Les noms de voix Gemini (Orus, Kore, Aoede…) qui suivent sont des suggestions historiques de casting par ton : Gemini a été abandonné (quota). Le placement, le débit et les silences décrits ici restent valables.

Voix **Orus** (documentaire), style speaker d'actualités filmées / crieur. Une phrase courte par une, posée juste après le tourniquet (≈ +0,1 s) et terminée avant le tourniquet suivant ; débit ≈ 2,6 mots/s, 5 à 7 mots par une. L'écran ne montre que dates, titres et mots-clés : la voix donne le liant (« les États généraux s'ouvrent », « Berlin fait la fête »). Les dépêches tapées doublent la voix en mots-clés, jamais en phrase complète à lire. Musique duckée sous la voix par `assemble.py mux --voice`.

## Risques et limites
- **Poids** : le grain argentique par frame sature le plafond de 8 Mb/s du mux (≈ 20 Mo pour 18,75 s) ; baisser σ du grain ou l'appliquer une frame sur deux si un plafond plus bas est imposé.
- **Densité de texte** : une une porte 6 blocs de texte ; au-delà de 2,8 s par une le spectateur lit, en deçà il ne lit que la date — garder la voix pour le liant.
- **Rouge sur aplat noir** : un tampon en `multiply` disparaît sur la foule noire → fond papier 90 % obligatoire.
- **Faits historiques** : formulations prudentes (ex. le Mur n'est pas abattu la nuit même : on parle de frontière ouverte et de Berlinois qui attaquent le béton).
- **Portraits** : uniquement des silhouettes génériques inventées ; jamais de personnage reconnaissable.
- Le rendu DOM 1080×1920 est lent quand le CPU est partagé (≈ 0,65 s/frame) : prévoir ~6 min par short de 18 s + 2,5 min d'OpenCV.
