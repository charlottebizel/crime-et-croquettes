# État de Loïc, mis à jour le 2026-11-25

## Où j'en suis

Écran de partie en Vue (LB-002) : PR #18 en attente de review. Revue n°2 (1er décembre) : LB-003 (`charger_demo`), LB-004 (Mes parties et vraies parties en lecture) et LB-005 (tableau de bord des coûts) poussés sur `feature/revue-2`, **PR #19 ouverte** (base `feature/vue-ecran-partie`, à fusionner après #18), **en attente de la review de Charlotte**. Contrôles avant push : `check` OK, aucune migration manquante, 112 tests passés, Ruff OK. Vérifié chez moi : `charger_demo`, Mes parties, vraie partie en lecture, tableau de bord (coûts à 0 $ en local, faux fournisseur) ; captures faites. Sur une vraie partie, les actions (question, carte, avis, fiche) ne marchent pas encore : il manque les endpoints POST.

## Tickets ouverts

| Ticket | Sujet | Statut |
| --- | --- | --- |
| LB-002 | Écran de partie en Vue 3 et API JSON de démo | en review (PR #18) |
| LB-003 | Commande charger_demo | en review (PR #19) ; reste : lancement sur Render |
| LB-004 | Mes parties et vraies parties en lecture | en review (PR #19) ; reste : endpoints POST |
| LB-005 | Tableau de bord des coûts | en cours (capture avec vrais coûts à faire, après connexion à OpenRouter) |
| LB-006 | Icône œil sur les mots de passe | écrit et vérifié, à pousser sur `feature/oeil-mot-de-passe` |

## Prochaine action

1. Attendre la review de Charlotte sur #18 puis #19 ; une fois #18 fusionnée, passer la base de #19 à `main`.
2. Après déploiement : Charlotte lance `python manage.py charger_demo` sur Render (`DEMO_MOT_DE_PASSE` défini avant).
3. Décider avec Charlotte qui écrit les endpoints POST (question, carte, avis, fiche) avant la revue.
4. Captures faites : Mes parties, vraie partie, tableau de bord (à 0 $), accès refusé. Reste : tableau de bord avec de vrais appels OpenRouter (clé chez Charlotte).
