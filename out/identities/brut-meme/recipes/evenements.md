# Recette — short `evenements` en Brut Mème

Référence : `out/shorts/brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde/` (16,0 s, PixiJS + GSAP, seed 15, 120 bpm).

Pour un short evenements dans cette identité :

**Ouvrir par** (0–2,2 s) — la contrainte de temps est le hook :
- tag horloge rouge « ● EN DIRECT · 00,0 S » (Inter 900 56 px, chiffres tabulaires) qui tourne pendant tout le short et se fige à 15,0 s ;
- titre 3 lignes Anton auto-fit 900 px (« PENDANT / CES 15 / SECONDES, », le nombre en jaune), rescale 1,6 → 1 dès la frame 1 ;
- surligneur jaune « DANS LE MONDE… » en `slam` à 0,6 s + shake ;
- la jauge rubalise (y 1556) commence à se remplir : elle EST l'horloge visuelle.

**Structurer en** (2,2 → 12,4 s) — un compteur par scène de 1,5–2 s, `hard-cut` sur le temps :
- label de section Anton 132 px en surligneur (`slide-snap` à +0,03 s) ;
- chiffre géant Anton auto-fit, **valeur = débit × temps écoulé du short** (honnête : « depuis le début de la vidéo »), mise à jour à chaque frame ;
- une ligne d'unité Inter 900 60 px (« bébés sont nés ») ;
- sticker rond rouge du débit (« ≈ 4,2 PAR SECONDE ») en `slam` à +0,5 s, shake 9 px, punch 0,5 ; second punch 0,3 à +1,0 s ;
- un picto Pixi par scène, piloté par le même débit : pastilles (une par naissance, pop à l'apparition), carrés neutres (décès), éclairs zigzag renouvelés à chaque temps, flux d'enveloppes, orbite de la Terre, cœur qui bat à 72/min ;
- alterner le fond (jaune pour 1 scène sur 3 environ ; jamais 2 inversions en moins de 1,6 s) ;
- son : un SFX par unité comptée quand le débit est lisible (blip par bébé, thud par battement), ticks rapides sinon.

**Fermer par** (12,4 → 16,0 s) :
- récap en `bg-invert` jaune : « EN 15 SECONDES » + 6 barres noires (ombre blanche) qui entrent en `slide-snap` alterné gauche/droite, stagger 0,2 s, chiffres Anton 112 px jaunes, tous préfixés « ≈ » ;
- question finale sur fond noir : « ET TOI, / T'AS FAIT / QUOI ? » (dernière ligne en surligneur `slam`), sticker « DIS-LE EN COMM' » + starburst jaune « ?! » à 14,4 s ;
- à 15,0 s, l'horloge devient « TEMPS ÉCOULÉ · 15,0 S » (tag jaune `slam`, punch 1, shake 16 px, `impact` + `chime`) ; tenue 1 s, fin propre.

Chiffres : arrondis, formulation « environ / ≈ », sources d'ordre de grandeur notées dans `short.json`. Tokens : `motion.punchIn`, `motion.beat`, `shapes.hazardBar`, `typography.caption` (tabular-nums), `color.danger` réservé au chiffre grave (décès). Voix : Fenrir, énumération rythmée qui suit les cuts avec ~0,5 s de retard.
