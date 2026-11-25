---
id: LB-002
titre: Écran de partie en Vue 3 et API JSON de démo
statut: en cours
membre: Loïc
branche: feature/vue-ecran-partie
créé: 2026-11-25
---
## Objectif

Suite à la demande du professeur à la revue n°1, l'écran de partie devient une application Vue 3 qui lit ses données dans une API JSON, sans changer son apparence (décision D-001).

## Critères d'acceptation

- [x] `/parties/demo/` charge l'application Vue (coquille + carte d'imports + `static/js/jeu/main.js`), Vue copié dans `static/vendor/vue/`.
- [x] `GET /api/parties/demo/` et `GET /api/parties/demo/suspects/<id>/` renvoient les clés de la spec §6 ; suspect inconnu → 404 au format d'erreur commun.
- [x] Changer de suspect se fait sans recharger la page et met à jour l'adresse (`?suspect=`).
- [x] Onglets Carnet / Fiche au clavier (flèches, Début, Fin), onglet mémorisé.
- [x] En démo, avis et fiche fonctionnent dans le navigateur ; question, carte et accusation inactives.
- [x] Code des POST (question, carte, avis, fiche) prêt selon la spec §5.4, erreur affichée et question conservée.
- [x] HTMX retiré de `base.html`.
- [x] Spec, D-001, AGENTS.md et README mis à jour.
- [ ] Vérifié chez Loïc (navigateur avec les vraies polices).
- [ ] PR relue par Charlotte.

## Notes

- 2026-11-25 : vérifié par l'agent sur une copie complète du projet (avec les modèles de Charlotte) : 79 tests pytest verts, Ruff OK, `makemigrations --check` OK, `collectstatic` OK avec le stockage de production. Navigateur en `DEBUG=False` : 5 suspects, changement de suspect, jauge, défilement, avis, fiche, onglets au clavier, rechargement, `?suspect=99`, téléphone 375 px sans défilement horizontal, aucune erreur JavaScript. Mode réel simulé (réponses d'API imitées) : erreur IA affichée avec question conservée, succès qui met à jour jauge, compteur et carnet, carte tirée, avis refusé annulé ; en-tête CSRF présent sur chaque POST.
- Fichiers à supprimer par Loïc (remplacés par Vue) : `templates/jeu/_*.html` (7 fragments) et `static/js/partie.js`.
