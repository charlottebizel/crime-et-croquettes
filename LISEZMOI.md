# Kit de départ : programmer en groupe avec des agents

À poser à la racine du dépôt de votre projet, sur une branche, puis à fusionner par une PR.

## Ce qu'il contient

| Fichier | À quoi il sert |
| --- | --- |
| `AGENTS.md` | Les règles du groupe, lues par l'agent de chaque membre à chaque session. À remplir : le produit, le groupe, les commandes. |
| `CLAUDE.md` | Une ligne, `@AGENTS.md`, pour que Claude Code lise le même fichier que les autres agents. |
| `.agents/skills/bureaucratie/` | Le skill qui crée et tient le dossier `docs/<prénom>/` de chaque membre. |
| `.agents/skills/ma-stack/` | Le template du skill de votre stack. À renommer et à remplir en groupe. |
| `consignes/consigne-lot.md` | Le modèle que votre agent remplit pour confier un lot à un sous-agent. |
| `consignes/relecture-croisee.md` | Le modèle pour faire relire ce travail par un autre agent. |
| `docs/decisions/` | Les décisions du groupe, une par fichier, acceptées par PR. |

## Pour commencer

1. Un membre copie le contenu du kit dans le dépôt, dossier caché `.agents/` compris, remplit `AGENTS.md` (le tableau du groupe surtout) et ouvre une PR. Si le dépôt a déjà un `AGENTS.md`, il y ajoute les sections du kit et garde les règles du projet.
2. Chaque membre, sur son poste, demande à son agent : « Mets en place ma bureaucratie. » L'agent crée `docs/<prénom>/` et écrit le premier ticket avec lui.
3. Le groupe renomme et remplit le skill de sa stack, ensemble, puis reporte ses vérifications dans la table « Commandes » de `AGENTS.md`.

## Selon votre agent

Codex et OpenCode lisent `AGENTS.md` et `.agents/skills/` sans rien faire.

Claude Code lit `CLAUDE.md` : celui du kit tient en une ligne, `@AGENTS.md`, qui importe le fichier commun. Si votre dépôt a déjà un `CLAUDE.md`, ajoutez-y cette ligne au lieu de le remplacer. Claude Code cherche ses skills dans `.claude/skills/` : demandez-lui une fois « Copie les dossiers de .agents/skills dans .claude/skills ». La règle de `AGENTS.md` lui fait refaire la copie après chaque modification.

Vous pouvez supprimer ce fichier une fois le kit en place.
