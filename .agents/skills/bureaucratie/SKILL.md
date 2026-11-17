---
name: bureaucratie
description: Tenir l'état du travail d'un membre du groupe dans le dépôt (état, tickets, journal, décisions), pour reprendre le projet depuis n'importe quel ordinateur ou n'importe quelle session. À charger quand on demande « mets en place ma bureaucratie », « où j'en suis », « crée un ticket », « note cette décision », au début d'une session pour reprendre le travail, et à la fin d'une session pour tout mettre à jour.
---

# Bureaucratie : l'état du travail vit dans le dépôt

Une session d'agent oublie tout quand elle se ferme. Ce qui est écrit dans le dépôt reste. Le but : qu'un autre agent, sur un autre ordinateur, reprenne le travail en lisant quatre fichiers.

Dans un projet de groupe, chaque membre a son dossier. L'agent d'un membre n'écrit que dans le dossier de ce membre : deux agents ne modifient ainsi jamais le même fichier.

## La structure

```text
docs/
├── decisions/            commun à tout le groupe, modifié par PR
│   └── D-001-<sujet>.md
└── <prénom>/             un dossier par membre
    ├── STATUS.md         où j'en suis, ma prochaine action
    ├── tickets/          un fichier par tâche : <INITIALES>-001-<sujet>.md
    ├── journal/          un fichier par jour : AAAA-MM-JJ.md
    └── relectures/       les rapports de relecture croisée, créé au premier rapport
```

Ce dossier se commite sur la branche de la tâche en cours et rejoint `main` avec la PR du membre. Les autres le lisent sur `main`.

Le prénom est en minuscules, sans accent ni espace. Les tickets portent les initiales du membre, pour que deux membres n'aient jamais le même numéro.

## Mettre en place

Quand on te demande de mettre en place la bureaucratie d'un membre :

1. Trouve pour qui tu travailles (`AGENTS.md`, section « Le groupe »). Si tu ne sais pas, demande.
2. Crée `docs/<prénom>/` avec `STATUS.md`, `tickets/` et `journal/`, à partir des templates de `assets/`.
3. Vérifie que `docs/decisions/` existe : il vient avec le kit. S'il manque, dis-le. Ne le crée pas toi-même, ce dossier commun se modifie par PR.
4. Demande au membre sur quoi il travaille en ce moment et écris son premier ticket avec lui.
5. Remplis `STATUS.md` et le journal du jour.

Ne crée jamais le dossier d'un autre membre : son agent le fera.

## Ce que contient chaque fichier

### STATUS.md

Vingt lignes au plus. Trois parties : « Où j'en suis » en trois phrases, « Tickets ouverts » en tableau, « Prochaine action » en liste numérotée que quelqu'un peut suivre sans rien savoir de la session.

Un `STATUS.md` se réécrit, il ne s'allonge pas. Ce qui est fini sort du fichier : le journal en garde la trace.

### Un ticket

Une tâche qui tient en une branche et une PR. Si elle grossit, coupe-la en deux tickets.

Les critères d'acceptation sont des cases à cocher qu'on peut vérifier par oui ou par non : « la page répond en moins d'une seconde », pas « la page est rapide ». Un ticket passe à `terminé` quand toutes ses cases sont cochées et vérifiées, pas avant. Un ticket qu'on ne fera pas passe à `abandonné`, avec la raison en une ligne.

### Le journal du jour

Quatre parties : **Fait**, **Décisions**, **Problèmes et solutions**, **À reprendre**.

« Problèmes et solutions » est la plus utile : chaque problème rencontré, sa cause et ce qui l'a réglé. Un problème qui revient deux fois devient une règle dans le skill du groupe.

On ajoute au journal du jour, on ne réécrit pas les jours passés.

### Une décision

Un choix qui engage le groupe : la stack, le modèle de langage, l'hébergeur, la forme de la base, une règle d'architecture. Quatre parties : le contexte, la décision, ce qu'on a écarté et pourquoi, les conséquences.

Une décision s'écrit sur une branche et part en PR : le groupe l'accepte en fusionnant. Quand on change d'avis, on n'efface pas l'ancienne : on écrit la nouvelle, et l'ancienne passe à `remplacée par D-00N`.

## Au début d'une session

Lis dans l'ordre : `docs/<prénom>/STATUS.md`, les tickets ouverts, le dernier journal, `docs/decisions/`, puis le `STATUS.md` des autres membres. Dis en trois lignes où on en est et propose la prochaine action.

## À la fin d'une session

1. Coche les critères dont tu as vu la preuve (un test lancé, un écran regardé) et mets à jour le statut et la date des tickets touchés. Ce qu'on te rapporte sans preuve se note dans le journal du ticket, et la case reste vide.
2. Complète le journal du jour.
3. Réécris `STATUS.md`.
4. Dis ce qui a été mis à jour. Ne fais pas de commit sans qu'on te le demande.

Un `STATUS.md` périmé trompe le prochain lecteur. Si tu n'as le temps que pour un fichier, c'est celui-là.

## Les templates

| Fichier | Template |
| --- | --- |
| `docs/<prénom>/STATUS.md` | `assets/STATUS.md` |
| un ticket | `assets/ticket.md` |
| un journal du jour | `assets/journal.md` |
| une décision | `docs/decisions/_template.md`, à la racine du dépôt |
