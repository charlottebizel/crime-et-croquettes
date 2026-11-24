"""
ia/fournisseurs/openrouter.py — Vrai appel au modèle via OpenRouter (spec §7.4).

OpenRouter accepte le format de l'API OpenAI : on utilise donc le SDK
`openai` en changeant seulement l'adresse (base_url).

Options envoyées à chaque appel :
  - response_format json_schema strict : le modèle doit respecter le schéma ;
  - provider.zdr / data_collection=deny : aucun fournisseur qui conserve
    ou réutilise les prompts (données des joueurs) ;
  - provider.require_parameters : seulement les fournisseurs qui gèrent
    vraiment les sorties structurées ;
  - usage.include : OpenRouter renvoie le coût réel dans `usage.cost`.

La clé OPENROUTER_API_KEY reste côté serveur : jamais envoyée au navigateur.
"""

from decimal import Decimal

import openai
from django.conf import settings

from ..erreurs import ErreurFournisseur
from . import ReponseIA

URL_OPENROUTER = "https://openrouter.ai/api/v1"


class FournisseurOpenRouter:
    nom = "openrouter"

    def __init__(self):
        if not settings.OPENROUTER_API_KEY:
            raise ErreurFournisseur("OPENROUTER_API_KEY est vide")
        self.client = openai.OpenAI(
            base_url=URL_OPENROUTER,
            api_key=settings.OPENROUTER_API_KEY,
            timeout=settings.IA_DELAI_SECONDES,
            max_retries=0,  # pas de nouvel essai caché : chaque appel est journalisé
        )

    def completer(self, modele: str, messages: list[dict], nom_schema: str, schema: dict):
        try:
            reponse = self.client.chat.completions.create(
                model=modele,
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {"name": nom_schema, "strict": True, "schema": schema},
                },
                extra_body={
                    "provider": {
                        "zdr": True,
                        "data_collection": "deny",
                        "require_parameters": True,
                    },
                    "usage": {"include": True},
                },
            )
        except openai.OpenAIError as erreur:
            # Le détail (type + message) va dans le journal, pas au joueur.
            raise ErreurFournisseur(f"{type(erreur).__name__}: {erreur}") from erreur

        if not reponse.choices:
            raise ErreurFournisseur("Réponse sans contenu (choices vide)")

        usage = reponse.usage
        # `cost` est un champ propre à OpenRouter (en dollars) : le SDK OpenAI
        # ne le connaît pas, on le lit donc avec getattr.
        cout = getattr(usage, "cost", None) if usage else None
        return ReponseIA(
            contenu=reponse.choices[0].message.content or "",
            modele=reponse.model or modele,
            jetons_entree=usage.prompt_tokens if usage else 0,
            jetons_sortie=usage.completion_tokens if usage else 0,
            cout_usd=Decimal(str(cout)) if cout is not None else Decimal("0"),
        )
