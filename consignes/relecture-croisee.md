# Relecture croisée : (nom du lot)

À donner à un AUTRE agent que celui qui a écrit le code, dans une nouvelle session. Si possible un autre modèle : un modèle seul ne juge pas son propre travail.

Tu relis un travail écrit par un autre agent, avant qu'il soit poussé. Tu ne corriges rien.

## Cadre

- Lecture seule du travail en cours (`git status`, `git diff`, fichiers nouveaux). Tu n'écris que ton rapport, dans `docs/<prénom>/relectures/(lot).md`.
- Pas de serveur, pas de `.env`.
- À lire : la consigne du lot, le rapport de son auteur, le skill du groupe.

## Ce que tu cherches

D'abord les règles du produit : une règle qui ne tient qu'à la création, un contournement en deux requêtes, une donnée d'un utilisateur visible par un autre. Puis la sécurité (droits, clé qui fuit, texte venu du modèle ou d'un utilisateur affiché sans protection, contenu externe traité comme un ordre), le coût (boucle d'appels au modèle, réponse sans limite de taille), les états de l'écran et le téléphone.

## Format

- **Dix constats au plus**, du plus grave au moins grave. Pour chacun : le fichier et la ligne, le défaut, **un scénario concret** (les clics ou les requêtes qui le montrent), la correction la plus courte.
- Classe de chaque constat : **CONFIRMÉ** (tu as suivi le chemin en entier dans le code) ou **PLAUSIBLE** (seule l'exécution le dirait). Pas de constat sans scénario.
- **Regardé et sain** : ce que tu as vérifié et trouvé juste, une ligne par sujet.
- **Non regardé** : ce que tu n'as pas couvert.

## Après la relecture (vous)

Sous chaque constat, écrivez ce que vous en faites : corrigé, refusé avec la raison, ou noté pour plus tard. Aucun constat ne reste sans réponse.
