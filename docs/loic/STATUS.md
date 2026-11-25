# État de Loïc, mis à jour le 2026-11-25

## Où j'en suis

Écran de partie en Vue (LB-002) poussé, PR en attente de review. Pour la revue n°2 (1er décembre), LB-003 (`charger_demo`), LB-004 (Mes parties et vraies parties en lecture) et LB-005 (tableau de bord des coûts) sont écrits dans le projet par l'agent et vérifiés sur une copie (107 tests). Vérifié chez moi : `charger_demo`, Mes parties, vraie partie en lecture, tableau de bord (coûts à 0 $ en local, faux fournisseur) ; captures faites. Sur une vraie partie, les actions (question, carte, avis, fiche) ne marchent pas encore : il manque les endpoints POST.

## Tickets ouverts

| Ticket | Sujet | Statut |
| --- | --- | --- |
| LB-002 | Écran de partie en Vue 3 et API JSON de démo | en review |
| LB-003 | Commande charger_demo | en cours (à appliquer et pousser) |
| LB-004 | Mes parties et vraies parties en lecture | en cours (à appliquer et pousser) |
| LB-005 | Tableau de bord des coûts | en cours (capture avec vrais coûts à faire, après connexion à OpenRouter) |
| LB-006 | Icône œil sur les mots de passe | ouvert |

## Prochaine action

1. Merger LB-002, puis créer `feature/revue-2` depuis `main`, lancer `pytest`, `python manage.py charger_demo`, tester en `moustache` puis en `admin`.
2. PR avec Charlotte en reviewer (signaler : `jeu/services.py` modifié, requêtes du tableau de bord écrites côté Loïc).
3. Décider avec Charlotte qui écrit les endpoints POST (question, carte, avis, fiche) avant la revue.
4. Captures faites : Mes parties, vraie partie, tableau de bord (à 0 $), accès refusé. Reste : tableau de bord avec de vrais appels OpenRouter (clé chez Charlotte).
