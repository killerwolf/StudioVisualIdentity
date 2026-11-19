# Reproduire

**Essai C4 de la composition** (`out/report/notes/composition/matrice.md`) : habillage `plan-bleu` (la pâte de Lyrics chemin)
× mécanique `pop-papier-12ips` (le moteur papier) × format `narre-court`. Même épisode, même code de scène et même voix
(Gemini Sulafat, `../voice_lines/` copiées de `papier-decoupe__explicatif__d-ou-vient-le-mot-sandwich`, aucun nouvel appel) que
les 4 shorts « sandwich » du papier ; seuls changent :

- `plan-bleu.json` : le thème (couleurs du plan bleu : feuille `#1B4C92`, papier ivoire `#F3F0E4`, jaune réservé `#FFD84A`,
  corail `#FF7D5C` ; polices Barlow Condensed 800 / 600 italique et JetBrains Mono, lues dans `node_modules/@fontsource`) ;
- `tapis_plan()` dans `video.py` : la feuille de plan bleue quadrillée et pliée, avec le crayon jaune et la tasse de café, qui
  remplace `papier.tapis` pour ce short seulement.

Le moteur partagé `out/shared/papier-moteur/` n'est pas modifié et aucun thème n'y est ajouté (StudioGabarit lit ce dossier).

```bash
npm i                                   # polices @fontsource (une fois)
PY=<python avec pillow, numpy, opencv-python-headless> bash out/shorts/papier-plan-bleu__explicatif__d-ou-vient-le-mot-sandwich/src/build.sh
python3 out/tools/check.py out/shorts/papier-plan-bleu__explicatif__d-ou-vient-le-mot-sandwich
```
