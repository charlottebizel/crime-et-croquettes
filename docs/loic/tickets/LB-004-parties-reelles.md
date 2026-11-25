---
id: LB-004
titre: Mes parties et vraies parties en lecture (écran Vue branché sur la base)
statut: en cours
membre: Loïc
branche: feature/revue-2
créé: 2026-11-25
---
## Objectif

Afficher une vraie partie enregistrée en base dans l'écran Vue, et permettre au joueur de retrouver ses parties.

## Critères d'acceptation

- [x] `/parties/` liste les parties du joueur connecté, avec « Reprendre l'enquête ».
- [x] `/parties/<pk>/` monte l'écran Vue sur `/api/parties/<pk>/` (`mode_demo` faux).
- [x] `GET /api/parties/<pk>/` et `…/suspects/<id>/` renvoient les clés du §6, lues en base (`jeu/lecture.py`).
- [x] Avis et fiche personnels à chaque joueur ; compteurs selon le palier de l'hôte.
- [x] Accès : non connecté → redirection (page) ou 401 (API) ; partie d'un autre joueur → 404.
- [x] Ni la solution, ni l'alibi, ni les connaissances, ni le secret d'un suspect ne sortent de l'API (test).
- [x] Lien « Mes parties » dans le menu.
- [ ] Les écritures (question, carte, avis, fiche) : endpoints POST à écrire (spec §5.4). D'ici là, ces boutons affichent une erreur sur une vraie partie.

## Notes

- 2026-11-25 : écrit par l'agent. « Nouveau » sur une entrée du carnet = témoignage pas encore jugé par ce joueur (on ne mémorise pas les visites) ; spec §6.4 mise à jour.
