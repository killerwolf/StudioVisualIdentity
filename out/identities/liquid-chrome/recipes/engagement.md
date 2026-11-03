# Recette — short « engagement » dans l'identité Chrome Liquide

Référence : `out/shorts/liquid-chrome__engagement__quelle-couleur-remplit-le-verre/` (three.js, 15 s, 450 frames, rendu sans état).

Pour un short **engagement** dans cette identité :

- **Ouvrir par** (0–1 s) : la question lisible à la frame 0 — chapeau Inter 500 54 px MAJUSCULES « QUELLE COULEUR » + titre Syne 800 92 px « remplit le verre / en premier ? » (dégradé chrome sur « en premier ? »). Quatre éprouvettes déjà en place, numérotées 1–4 dans la couleur de leur liquide ; les filets démarrent à 0,45 s avec 4 `pop` en arpège (D5, F#5, A5, C#6).
- **Structurer en** :
  1. 0,45–9,65 s : course analytique (débits par seconde de course intégrés, tableau `RATES`) avec **deux changements de tête** (rose en tête jusqu'à τ ≈ 4,4, puis or, puis menthe) ; pourcentages Inter 600 54 px qui flottent au-dessus du liquide ; légende-statut « COURSE · 4 COULEURS » → « FAIS TON PARI… » (4,6 s, double `blip`).
  2. 9,65–11,65 s : **ralenti ×0,5** (légende « RALENTI · ×0,5 », `riser` puis `swell`) ; le dépassement décisif tombe dans le ralenti (τ ≈ 10,3), `whoosh`.
  3. 11,65 s : le gagnant atteint 100 % → `impact` + `chime` ; les filets se coupent, les perdants s'atténuent (envMap −0,6, chiffres à 45 %), le gagnant s'illumine (émissif pulsé), la caméra glisse de 18 % vers lui.
- **Fermer par** : « Menthe gagne ! » (glisse-haut 0,6 s, couleur du gagnant) puis, à 12,6 s, la pilule CTA menthe « Commente ta couleur ↓ » (Inter 500 60 px, `outBack` 0,6 s, `coin`) tenue 2,4 s ; le clapot s'amortit, pas de noir.
- **Tokens** : environnement PMREM néon du poster, chrome (metalness 1, roughness 0,06, iridescence 0,35), liquide (metalness 0,85, roughness 0,14, iridescence 0,45), verre additif (MeshPhysicalMaterial noir, AdditiveBlending), fov 30, BokehPass aperture 0,0022, `setViewOffset` −30 px pour centrer sur la zone sûre.
- **Variantes** : même gabarit pour « quelle goutte touche le fond en premier », « quel blob grossit le plus vite » — garder 4 couleurs = 4 accents, numéros 1–4, CTA par couleur.
- **Coût mesuré** : 800,9 s pour 450 frames (178 s/100 frames, SwiftShader, CPU saturé par 10 studios). Ne pas utiliser la transmission (≈ 5 s/frame) : verre additif.
