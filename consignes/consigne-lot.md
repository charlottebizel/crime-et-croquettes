# Consigne de lot : (nom du lot)

Une consigne pour confier un lot à un sous-agent. C'est l'agent principal qui la remplit, une par lot, à partir du plan et du ticket : le membre du groupe dit ce qu'il veut et relit le découpage, il ne remplit pas ce fichier. Plus la consigne tranche, moins le sous-agent devine.

## Contexte

(Le produit en deux phrases. Ce que ce lot apporte à l'utilisateur, et pourquoi maintenant. Le ticket : `docs/<prénom>/tickets/XX-000-….md`.)

## À lire d'abord

1. `AGENTS.md`, puis le skill du groupe.
2. Les fichiers voisins à imiter : (une route, un écran, un test du même domaine).
3. Les décisions qui s'appliquent : (D-00N).

## Spécification

- **Données** : (tables ou collections, champs, types, ce qui est obligatoire).
- **Règles** : (qui peut faire quoi, à la création et à la modification).
- **Écrans** : (chaque écran et ses états : vide, chargement, erreur, succès, très long ; sur téléphone d'abord).
- **Modèle de langage** : (ce qu'on lui envoie, ce qu'on attend, ce que le code vérifie avant de s'en servir, ce qui part dans le journal des appels).
- **Budgets** : (taille maximale d'une réponse, nombre de résultats, coût maximal d'un appel).

## Contraintes

- Fichiers autorisés : (liste ou dossiers). Ne touche à rien d'autre.
- Aucun commit, aucun push. N'ouvre pas `.env`. Aucun vrai appel au modèle dans les tests.
- Code en anglais, textes affichés en français.

## Vérifications à rejouer avant de rendre

(Les commandes du skill, dans l'ordre.) Donne les chiffres : nombre de tests, durée.

## Rapport attendu

- **Fait** : fichiers créés ou modifiés.
- **Choix** : ce que tu as tranché, et pourquoi.
- **Vérifié** : les commandes et leurs résultats.
- **Non vérifié** : ce que tu n'as pas pu lancer ou regarder.
- **Points fragiles** : ce qu'un relecteur doit regarder en premier.
