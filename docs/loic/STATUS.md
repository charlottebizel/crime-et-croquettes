# État de Loïc, mis à jour le 2026-11-25

## Où j'en suis

Revue n°1 passée ; le professeur demande un framework frontend. Décision D-001 : les écrans de jeu passent en Vue 3 avec une API JSON, sans build. L'écran de partie en Vue (LB-002) est écrit dans le projet et vérifié par l'agent ; il reste à le vérifier chez moi, supprimer les anciens fragments et ouvrir la PR. Charlotte doit écrire les endpoints JSON réels (spec §5.4) au lieu des vues HTMX.

## Tickets ouverts

| Ticket | Sujet | Statut |
| --- | --- | --- |
| LB-001 | Écran de partie avec données en dur (templates) | mergé, remplacé par LB-002 |
| LB-002 | Écran de partie en Vue 3 et API JSON de démo | en cours |

## Prochaine action

1. Créer `feature/vue-ecran-partie`, supprimer les fichiers remplacés (`git rm templates/jeu/_*.html static/js/partie.js`), lancer `pytest` et ouvrir `/parties/demo/`.
2. PR avec Charlotte en reviewer : lui signaler D-001 et la spec §5.4 (endpoints JSON à écrire), et les fichiers de son domaine touchés (`jeu/`, `config/urls.py`).
3. Mettre à jour la répartition des tâches (PDF) : les tâches « fragments HTMX » deviennent « endpoints JSON » et « écrans Vue ».
