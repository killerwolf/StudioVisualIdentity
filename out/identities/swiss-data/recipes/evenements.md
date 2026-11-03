# Recette — un short `evenements` dans l'identité Grille Suisse

Référence : `out/shorts/swiss-data__evenements__j-272-eclipse-2-aout-2027/` (15 s, D3.js + d3-geo + GSAP, rendu 92,3 s).

**Pour un short evenements (compte à rebours, date, record) dans cette identité :**

- **Ouvrir par** (0–3 s) : « J– » rouge 240 px + nombre de jours en Archivo Black 460 px qui **décompte** (365 → 272, `expo.out` 1,4 s, un `tick` par dizaine), titre de l'événement Inter 800 112 px par `wipe-ligne`. Motif de l'événement en formes pures (ici disque rouge = Soleil, disque noir = Lune qui glisse dessus en 3 s `power2.out`). Kicker `01 · DÉCOMPTE`, date `JJ.MM.AAAA` à droite.
- **Structurer en** trois rubriques séparées par le `volet-rouge` (coupes à 3,475 / 8,475 / 12,475 s) :
  1. `02 · TOTALITÉ` — la durée clé en chiffres géants empilés (« 6 » encre / « 23 » rouge 420 px, unités Inter 800 130 px) comptée par un timer `power3.out` 2,3 s + barre de progression D3 (`scaleLinear` 0 → 7 min, graduations par minute), lieu en label 62 px.
  2. `03 · LE TRACÉ` — carte schématique d3-geo (`geoEquirectangular().fitExtent`, `geoGraticule` 6°, cadre 4 px) avec la bande tracée en trait rouge 30 px par `stroke-dashoffset` (2,4 s, linéaire) ; chaque point s'allume (`back.out(3)`) et la liste de pays passe du gris fantôme à l'encre au passage de la bande.
- **Fermer par** `04 · À NOTER` : le record en chiffre géant rouge (« 2114 », 360 px) révélé par masque, le disque noir recouvre totalement le rouge, couronne rouge qui s'ouvre (1,0 s), rappel « date · J–N » ; tenue ≥ 1 s.
- Son : `pulse` 120 bpm (tonalité différente du short geographie), `swell` sous l'approche de la Lune, `blip` montant à chaque minute du timer, `riser` + `pop` par pays sous le tracé, `impact` + `chime` final.
- Toujours présenter la carte comme « tracé approximatif » (points saisis à la main).
