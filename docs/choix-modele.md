# Choix du modèle IA

Note de travail pour la section « choix et justification du modèle » du rapport.
À compléter avec les coûts **observés** dans `/gestion/couts/` dès les premiers vrais appels.

## Décision (10 novembre 2026)

| Rôle | Variable | Modèle OpenRouter |
|---|---|---|
| Génération d'une enquête | `IA_MODELE_GENERATION` | `openai/gpt-6-luna` |
| Interrogatoire des suspects | `IA_MODELE_INTERROGATOIRE` | `openai/gpt-6-luna` |

## Candidats comparés

Prix relevés sur l'API publique d'OpenRouter (`/api/v1/models`) le 10/11/2026, en dollars par million de jetons.

| Modèle | Entrée | Sortie | Sorties JSON par schéma | Remarque |
|---|---|---|---|---|
| **`openai/gpt-6-luna`** | 0,10 $ | 0,50 $ | oui | Retenu |
| `openai/gpt-6-luna-pro` | 0,10 $ | 0,50 $ | oui | Même prix, candidat pour la génération |
| `openai/gpt-5.6-luna` | 0,20 $ | 1,20 $ | oui | Ancienne génération, plus cher |
| `openai/gpt-6-sol` | 2,00 $ | 10,00 $ | oui | 20× plus cher |
| `openai/gpt-6-astra` | 10,00 $ | 50,00 $ | oui | Hors budget |

## Justification

- **Budget** : 1 € pour tout le projet. Luna est le modèle GPT-6 le moins cher.
- **Sorties structurées** : Luna accepte `response_format` en `json_schema` strict, nécessaire pour le carnet d'indices et la génération (spec §7).
- **Disponibilité** : plusieurs fournisseurs (OpenAI, Azure, Amazon Bedrock), donc moins de risque de panne.
- **Pas de variante `:free`** : conformément aux consignes du cours (débit limité, prompts parfois conservés).

## Estimation de coût (avant mesure)

| Action | Jetons entrée | Jetons sortie | Coût estimé |
|---|---|---|---|
| Une question à un suspect | ~2 000 | ~300 | ~0,00035 $ |
| Une génération d'enquête | ~1 500 | ~3 000 | ~0,0017 $ |
| Une partie Free (1 génération + 20 questions) | | | ~0,0087 $ |
| Une partie Pro (1 génération + 40 questions) | | | ~0,0157 $ |

Ordre de grandeur : 1 € (~1,15 $) ≈ 3 000 questions ou ~130 parties Free.

## Points ouverts

- **Zero Data Retention** : la spec impose `provider: {"zdr": true, "data_collection": "deny"}`. L'API publique n'indique pas quels fournisseurs de Luna la respectent. À vérifier au premier vrai appel : si aucun ne convient, OpenRouter refuse la requête.
- **Chaînage de modèles** (fonctionnalité supplémentaire) : tester `gpt-6-luna-pro` pour la génération. Le chaînage n'a de sens que si la qualité est meilleure.
- **Essais à documenter** : garder ici les prompts testés, les résultats et les pistes abandonnées (demandé dans le rapport).
