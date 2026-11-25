---
id: LB-003
titre: Commande charger_demo (enquête du saumon et comptes de démo en base)
statut: en cours
membre: Loïc
branche: feature/revue-2
créé: 2026-11-25
---
## Objectif

Avoir en base, en local comme en production, une enquête complète et une partie en cours, pour montrer le vrai jeu (exigence O2 : données de démonstration). Tâche S3 de la répartition.

## Critères d'acceptation

- [x] 3 comptes : `admin` (superutilisateur), `moustache` (Pro), `joueur` (Free) ; mot de passe via `DEMO_MOT_DE_PASSE`, sinon aléatoire et affiché une fois.
- [x] Enquête complète : 5 suspects (avec personnalité, alibi, connaissances, secret), 5 objets, 5 lieux, 6 cartes, solution.
- [x] Chaque élément de la solution est prouvé par au moins une carte (spec §7.3).
- [x] Partie en cours `SAUMON42` : interrogatoires, 2 cartes tirées, 5 entrées de carnet, avis et fiche de l'hôte, fiche vierge de l'invité.
- [x] Relançable sans danger ; `--reinitialiser` pour repartir de zéro.
- [x] Tests (`jeu/test_parties.py`).
- [ ] Lancée en production par Charlotte (Render : shell ou commande de build).

## Notes

- 2026-11-25 : écrit par l'agent. Reprend les suspects et conversations de `jeu/demo.py` (ajout de l'interrogatoire de Monsieur Félix, pour que son témoignage du carnet ait une réponse liée).
- Ajout dans `jeu/services.py` (fichier de Charlotte) : `assurer_fiche(partie, joueur)`, qui crée les 15 cases de la fiche si elles manquent.
