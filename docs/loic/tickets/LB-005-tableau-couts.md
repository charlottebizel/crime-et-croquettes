---
id: LB-005
titre: Tableau de bord des coûts de l'IA (administrateurs)
statut: en cours
membre: Loïc
branche: feature/revue-2
créé: 2026-11-25
---
## Objectif

Exigence O4 : l'administrateur voit les coûts de l'IA par jour et par utilisateur, à partir du journal `AppelIA`. Capture obligatoire du rapport de chaque revue.

## Critères d'acceptation

- [x] `/gestion/couts/` réservé aux administrateurs (visiteur → connexion, joueur → 403), lien « Coûts IA » seulement pour eux.
- [x] API `/api/gestion/couts/?jours=7|30|90` (spec §6.7), calculée par `gestion/statistiques.py`.
- [x] Tuiles : coût de la période, appels et échecs, coût moyen d'une question et d'une génération (base du pricing), budget depuis le début.
- [x] Histogramme du coût par jour : survol et clavier, graduations rondes, couleur validée (luminosité et contraste), tableau jour par jour.
- [x] Consommation par joueur et 20 derniers appels, sans le détail technique des erreurs.
- [x] Utilisable sur téléphone (pas de défilement horizontal, tableaux défilants dans leur boîte).
- [x] Montants affichés en euros, au taux du jour de la BCE (API Frankfurter, cache 6 h, taux de secours si l'API ne répond pas) ; budget en pourcentage avec jauge.
- [x] Tests (`gestion/tests.py`), sans appel réseau (API de change imitée).
- [x] Vérifié chez Loïc en local (coûts à 0 avec le faux fournisseur), captures faites.
- [ ] Capture avec de vrais coûts (appels OpenRouter réels) pour le rapport de la revue n°2.

## Notes

- 2026-11-25 : écrit par l'agent (requêtes et écran), alors que la répartition prévoyait les requêtes pour Charlotte : à signaler dans la PR.
- 2026-11-25 : montants passés en euros à la demande de Loïc. Le JSON garde les dollars exacts, l'écran convertit. Taux : API Frankfurter (BCE, gratuite, sans clé), `gestion/taux.py`. Nouvelles variables facultatives : `TAUX_CHANGE_URL`, `TAUX_USD_POUR_1_EUR`, `TAUX_DATE`, `BUDGET_IA_EUR` (valeurs par défaut dans `settings.py`).
