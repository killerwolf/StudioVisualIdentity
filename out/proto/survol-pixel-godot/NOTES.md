Essai Godot archivé le 2026-11-22 (perdu au test à l'aveugle, 6,5 contre 7,5 pour le moteur actuel). Projet complet et rendu : tag git local archive/survol-pixel-godot-2026-11-22.

# Journal : Survol pixel dans Godot

## Phase 1, 19/11/2026, de 01:54 à 02:20 environ (horloge du Mac)

### Vérifications techniques
| Vérification | Résultat |
|---|---|
| Format | **OK**. Fenêtre racine en 270×480, `--fixed-fps 30`, exactement 558 images gardées (les 4 premières à t = 0 sont jetées). ffmpeg ×4 au plus proche donne 1080×1920, 30 i/s, H.264 yuv420p (ffprobe). |
| Déterminisme | **OK au bit près.** Trois rendus complets : 2 avec les caches chauds, 1 à froid (`projet/.godot` et `app_userdata/survol-pixel-godot` effacés). Les 558 PNG ont les mêmes md5 et le mp4 est identique (`625539099d0ed1000b871fc25b4a5ac9`). Les 4 images de préchauffage sont elles aussi identiques à froid et à chaud. Encodage : `-fflags +bitexact -flags:v +bitexact -map_metadata -1 -threads 4`. |
| Relief réel en 3D | **OK.** Maillage dense déplacé dans le vertex shader (518 000 sommets), paliers de 3,5 avec contremarche, normales par différences finies. La lumière `light()` donne la couleur de palette au soleil, ×(0,62 ; 0,67 ; 0,80) à l'ombre. Ombres portées par la carte d'ombre de Godot : orthogonale, 8192, sans flou ; relief, arbres et nuages en projettent. `custom_aabb` est posé sur le maillage et les MultiMesh déplacés dans le shader. |
| Brume | **OK** avec la sortie `FOG` du fragment shader : elle s'applique après l'éclairage, sans activer la brume de l'Environment. 10 paliers en racine carrée de la distance (300 → 1 900). |
| Cartouches Jersey 15 | **OK.** Police woff2 chargée par chemin absolu (`FontFile.load_dynamic_font`), sans anticrénelage, hinting ni sous-pixel. Corps 27 (Jersey 15) et 18 (Jersey 10 ; 18,67 dans `survol.py`, Godot n'accepte que des entiers). Assertions de largeur et de zone sûre portées. Avec le corps 19, « marches : convention de dessin » sortait de la zone sûre (221 px) ; il tient avec le corps 18. Ombre de cartouche par multiplication, puis passe palette sur l'image composée. |
| Couleurs par image | La passe palette seule donne une médiane de 38 et un maximum de 51 : **hors règle**. `plafond.py` (même garde-fou que `cap_colors` de `video.py`) corrige 79 images sur 562 (maximum 34 avant) ; résultat **21–32, médiane 30**. |

### Pièges rencontrés
- `DEPTH` est un nom réservé dans un shader spatial (« Redefinition of 'DEPTH' ») ; renommé `SEA_DEPTH`.
- Un `assert` qui échoue dans un script de dessin laisse Godot bloqué à 0 % de CPU au moment de quitter (Movie Maker). Il est remplacé par `push_error`.
- Les avertissements d'inférence de type sont traités comme des erreurs ; désactivés dans `project.godot`.
- Passe palette au plus proche en RGB : l'eau lointaine à l'ombre, brumée, virait au gris-brun (`HZ_R1`, `ROCK`). On ne choisit plus que dans la même famille de teinte (bleu / non bleu).

### L'atoll
- Même durée (18,6 s), mêmes textes, mêmes temps de cartouches et d'épingles (`CARDS`, `PINS`), mêmes `sink()` et `cut_open()`, même voix (`voice_lines/` Sulafat), même `sound.json`.
- Caméra : mêmes 8 clés et même interpolation (PCHIP), avec plus d'amplitude :
  - accroche de plus loin (340 au lieu de 300, lacet −38°) ;
  - lacet de la coupe −18° → +22° au lieu de −12° → +12° ;
  - plan final plus large et plus tourné (lacet −36°, recul 340).
- Mer : écume qui glisse au lieu de clignoter, ombres de nuages réelles qui dérivent, ressac renouvelé 2 fois par seconde.
- Reliefs : terrasses lisses à contremarche inclinée, et non des marches d'une case.
- Pas fait faute de temps : la frégate et son ombre, les palmiers des motus.
- Nuages : 130 au plus, écartés de l'axe caméra–sujet et de la caméra. Il en reste surtout au loin : la mer proche a peu d'ombres de nuages.

### Mesures (images natives, `mesures.py`, seuil 24)
| | Godot | Moteur actuel (`short_novo.mp4`) | Source (note de Fable) |
|---|---|---|---|
| Pixels qui changent par image | 7,4 % | 5,2 % | 26–33 % |
| Scintillement A-B-A, moyenne | 1,45 % | 0,95 % | 2,4 % |
| Scintillement A-B-A, maximum | 3,9 % | 5,0 % | 3,4 % (pire fenêtre) |
| Couleurs par image (natif, avant encodage) | 21–32 | 24–32 | — |

- Rendu : Godot 35,6 s plus plafond et ffmpeg 18,4 s, soit **54 s pour 558 images (9,7 s/100)**, machine chargée (charge 1 min 5,4). Moteur actuel : 356,6 s (63,9 s/100) sur CPU.
- `check.py` sur la copie : `ok: true`, 0 erreur, 0 avertissement. Intensité : −16,0 LUFS, comme le short actuel.
