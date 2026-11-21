---
id: LB-001
titre: Écran de partie avec données en dur
statut: en cours            # ouvert | en cours | bloqué | terminé | abandonné
branche: feature/ecran-partie
créé: 2026-11-18
mis-à-jour: 2026-11-18
---
## Contexte

L'écran de partie est le cœur du jeu (exigence O1) : le joueur y interroge les chats suspects joués par l'IA, voit leur stress, tire les pièces à conviction, tient son carnet d'indices et sa fiche de déduction. Les modèles et les vraies vues du jeu ne sont pas encore faits par Charlotte : on construit l'écran sur des données en dur qui respectent exactement les variables de contexte de `docs/specification.md` §6.1 à §6.6. Quand les vraies vues arriveront, les templates ne changeront pas.

Référence visuelle : la maquette « nuit et polar » (fiches avec toise, salle d'interrogatoire, bulles, carnet sur papier, fiche sur presse-papier).

## Critères d'acceptation

- [x] `/parties/demo/` affiche l'écran avec l'enquête « Qui a volé le saumon du dimanche ? » sans aucun appel au modèle.
- [x] Les 5 suspects s'affichent avec leur portrait (`composants/chat.html`), leur numéro et leur jauge de stress.
- [x] La conversation du suspect sélectionné s'affiche, chaque réponse avec la mention « Généré par IA ».
- [x] Le carnet distingue témoignages (avec avis Fiable / Douteux / Faux et note) et preuves.
- [x] La fiche de déduction montre suspects, objets et lieux avec leur état (inconnu, barré, validé).
- [x] Les compteurs (questions 12/20, cartes 2/6) s'affichent dans l'entête de la partie.
- [x] Les templates n'utilisent que les noms de variables de la spec §6.1 à §6.6 (avec `echanges` à la place de `messages`, spec corrigée).
- [x] L'écran est utilisable à 375 px de large (téléphone), sans défilement horizontal.
- [x] Les tests de la vue de démonstration passent (`pytest`), ainsi que `ruff check .`.
- [ ] La PR est relue et approuvée par Charlotte.

## Journal du ticket

- 2026-11-18 : créé.
- 2026-11-18 : code proposé et vérifié par l'agent sur une copie du projet : 27 tests pytest verts (dont 17 nouveaux), `ruff check` et `ruff format --check` OK, rendu regardé à 1440 px et à 375 px (pas de défilement horizontal), onglets testés. Reste à faire par Loïc : appliquer les fichiers, vérifier chez lui, ouvrir la PR. La case « relue par Charlotte » reste vide.
