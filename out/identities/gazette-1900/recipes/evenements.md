# Recette — un short `evenements` dans l'identité Gazette 1900

Référence : `out/shorts/gazette-1900__evenements__9-novembre-1989-mur-de-berlin/` (15,0 s, GSAP + OpenCV, graine 1989).

**Pour un short evenements (anniversaire « Ce jour-là ») dans cette identité :**

- **Ouvrir par** l'une de l'époque (8 temps = 3,75 s à 128 bpm) en tourniquet dès la frame 0, kicker « Ce jour-là », date-titre « 9 NOV. 1989 » ajustée à 900 px, événement en 84 px sur 2 lignes, gravure de nuit (feux d'artifice en rayons clairs), tampon « Édition spéciale » à 0,62 s, dépêche « la frontière est ouverte ! », zoom brusque à +5 temps.
- **Structurer en** (1) une une « dépêches » (10 temps) : trois chiffres-clés Playfair 900 128 px tamponnés tous les 3 temps (« AOÛT 1961 », « 155 KM », « 28 ANS ») avec leur ligne tapée en IBM Plex Mono 54 px ; (2) une une-action (6 temps) où l'image bouge vraiment : fissure à +0,62 s, blocs qui tombent 2 temps plus tard (`power2.in` 0,62 s, stagger 0,045 s), tampon « Ouvert ! ».
- **Fermer par** l'une d'aujourd'hui (8 temps) datée du jour anniversaire : compteur « il y a 00 → 37 ANS » (`power2.out` 4 temps, blips), frise 1961–1989–2026 qui se dessine (2 × 2 temps), dépêche-question « ET VOUS ? racontez en commentaire. », tampon signature « Au prochain numéro » à +6 temps.
- **Tokens** : `out/identities/gazette-1900/tokens.json`. Durées : tourniquet 0,55 s, tampon 0,16 s, zoom 0,14 s, une 2,8125 s.
- **Post** : `post.py video … --flash 3.75,8.4375,11.25`.
- **Son** : `gen_sound.py` (preset `pulse` en la mineur ; verre + thud à la fissure, impact lourd à la chute, blips du compteur, chime à 37).
- **Voix** : Orus ; « Ce jour-là, 9 novembre 1989 : le Mur de Berlin tombe ! » puis un chiffre par phrase.
- **Pièges** : rester exact (le Mur n'est pas démoli dans la nuit : on dit frontière ouverte, Berlinois qui attaquent le béton) ; l'anniversaire se calcule depuis la date de publication.

> Voix réellement utilisée pour les shorts de preuve : Fish Audio « Arnold » (`d704cf8f1216490cbfbed89955f0e938`, `s2.1-pro`). Les noms Gemini ci-dessus sont des suggestions historiques de casting par ton.
