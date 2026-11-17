---
name: ma-stack
description: (Ce que fait ce skill et quand le charger. Nommez la stack avec ses frameworks et écrivez les mots que vous tapez vraiment, par exemple « ajoute un écran », « écris une route », « lance les tests », « pourquoi ce test est rouge ». L'agent ne lit que cette description pour décider de charger le skill.)
---

# (Stack du groupe : frameworks et hébergeur)

> Template. Renommez le dossier et la ligne `name:` avec le nom de votre stack, en minuscules et avec des tirets (`stack-django-htmx`). Remplacez chaque passage entre parenthèses, puis supprimez ces lignes de citation. Gardez le fichier sous 200 lignes : le détail va dans des fichiers à côté.

Ce skill décrit la stack du projet et la façon dont le groupe veut qu'on y travaille. Lis-le en entier avant d'écrire du code.

## Avant de toucher au code

1. Lis `AGENTS.md` et les décisions de `docs/decisions/`. Le dépôt prime sur ce skill : s'ils se contredisent, signale-le.
2. Lis les versions réelles dans (le fichier de dépendances et son fichier de verrouillage). Ne les suppose pas.
3. Trouve un fichier voisin qui fait déjà ce que tu dois faire, et copie sa forme.

## La stack en une table

| Couche | Choix | Remarque |
| --- | --- | --- |
| Back | (framework, version) | (comment le projet a été créé) |
| Front | (framework, version) | |
| Base | (moteur) | |
| Modèle de langage | (SDK ou bibliothèque, modèle, fournisseur) | (où est la clé, quel plafond) |
| Qualité | (lint, types, tests) | |
| Production | (hébergeur, comment on déploie) | |

## Nos règles (le cœur)

> C'est la partie la plus importante. Écrivez-y comment VOUS voulez que le code soit, pas seulement ce qui a mal tourné. Une règle utile dit quoi faire, où, et pourquoi en une phrase. Donnez des limites qu'on peut compter.

- **Où va chaque chose** : (où vit une règle métier, où vit la validation, où vit un appel au modèle).
- **Les noms** : (comment on nomme une classe, une route, un composant, un test).
- **La taille** : (longueur maximale d'une fonction, d'un fichier, d'un composant).
- **La langue** : code en anglais, textes affichés en français.
- **Le style** : (un développeur ou un projet de référence : « code comme le ferait… », « comme dans la documentation de… »).
- **Les erreurs** : (ce que voit l'utilisateur quand le modèle échoue, ce qui part dans le journal).
- **Ce qu'on ne fait pas** : (deux ou trois interdits, chacun avec sa raison).

## Les vérifications, dans l'ordre

| # | Commande | Ce qu'elle attrape |
| --- | --- | --- |
| 1 | (lint) | |
| 2 | (types ou analyse statique) | |
| 3 | (tests) | |
| 4 | (build) | |
| 5 | l'essai réel : (l'écran sur téléphone, un vrai appel au modèle avec son coût noté) | ce que les tests ne voient pas |

Avant de dire « fini », lance-les dans cet ordre et montre les sorties réelles. Dis ce que tu n'as pas vérifié.

## Pièges déjà payés

> Un piège entre ici quand il vous a coûté du temps une fois. Trois parties : ce qu'on voit, la cause, la parade.

- **(Ce qu'on voit)** : (la cause). (La parade.)

## Quel fichier lire, et quand

> À remplir quand le skill grandit : un fichier par sujet dans `references/`, des modèles à copier dans `assets/`.

| Tu dois… | Lis |
| --- | --- |
| (écrire un écran) | `references/(interface).md` |
