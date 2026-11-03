# Recette — short « enfants » en Diorama Pastel

Référence : `out/shorts/pastel-diorama__enfants__d-ou-vient-la-pluie/` (Zdog + GSAP, 16 s, graine 4, src/index.html réutilisable tel quel).

**Pour un short enfants dans cette identité :**

- **Ouvrir par (0–3.2 s)** : la maquette déjà visible (socle feutrine menthe `#9BE7B0` sur galette blanche, pop d'échelle 0.62 -> 1 en `back.out(1.8)` 0.9 s), le personnage inventé qui rebondit au-dessus (×1.5, `back.out(2.2)` 0.75 s, saut `|sin(t·3.6)|`), kicker jaune Nunito 800 56 px + question en Baloo 2 800 132 px avec un mot-clé en `#E23D72`. Tout visible avant 0.3 s. À 2.8 s le personnage se pose (`power2.in` 0.45 s puis squash `elastic.out(1,0.4)`), le titre sort en `back.in(1.6)` 0.35 s.
- **Structurer en (3.2–13.6 s)** : 3 étapes de ~3.3 s, chacune annoncée par une **pastille-pop** blanche en haut (Baloo 2 96 px, puce numérotée colorée : rose `#FFB3C6`, bleu `#8ED6FF`, jaune `#FFD670`). Une seule action par étape, portée par le personnage (il change d'état plutôt que de disparaître : goutte -> vapeur translucide -> gouttelette -> goutte). Changements d'ambiance par **teinte-ciel** (1.4 s). Une étiquette-pilule courte au maximum par étape (« brrr, froid ! », 56 px). Voix : une phrase ≤ 9 mots par étape (≤ 2.6 mots/s).
- **Fermer par (13.6–16 s)** : pastille « ↻ Le cycle de… » (puce menthe), récapitulatif fléché en pointillés (rose montée / bleu descente, `power2.out` 1.3 s) + 3 mots-clés en pilules staggerées 0.3 s, clin d'œil du personnage à 15.1 s, fin tenue sans coupe (état ≈ début : boucle narrative).
- **Son** : music-box F majpent 96 bpm, `pop` C6/F6 à chaque entrée, `chime` à chaque pastille, `swell` sous une transformation, `tick` en pluie, `impact`+`pop` à l'atterrissage.
- **Tokens** : `tokens.json` (couleurs, typos, easings enter/exit/emphasis, safe area 220/320/120). Coût mesuré : 66 s/100 frames (CPU partagé).
- **Exactitude** : vérifier la science pour 6–10 ans (ici : le soleil chauffe -> évaporation ; le froid en altitude -> condensation en gouttelettes = nuage ; gouttes plus grosses et lourdes -> précipitation), et dire à la voix ce que l'image simplifie (vapeur invisible).
