# État de Loïc, mis à jour le 2026-11-18

## Où j'en suis

Gabarit de base et comptes mergés sur `main`, kit agents en place. L'écran de partie de démonstration (LB-001) est écrit et vérifié par l'agent sur une copie du projet ; il reste à l'appliquer chez moi et à ouvrir la PR. J'attends les modèles du jeu de Charlotte pour brancher les vraies actions.

## Tickets ouverts

| Ticket | Sujet | Statut |
| --- | --- | --- |
| LB-001 | Écran de partie avec données en dur | en cours |

## Prochaine action

1. Sur `feature/ecran-partie`, appliquer les 16 fichiers de code livrés le 2026-11-18, lancer `pytest` et ouvrir `/parties/demo/`.
2. Faire les captures (écran complet, vue téléphone, onglet fiche), puis ouvrir la PR avec Charlotte en reviewer en signalant : fichiers `jeu/` et `config/urls.py` touchés, `messages` renommé `echanges` dans la spec.
