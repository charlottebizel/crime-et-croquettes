"""
ia/fournisseurs/faux.py — Faux fournisseur (spec §7.6).

Aucun appel réseau, coût 0 : utilisé en local, dans la CI et les tests.
Renvoie des JSON valides prédéfinis, qui changent à chaque appel pour
que l'écran de jeu ait l'air vivant. `FauxFournisseur(invalide=True)`
renvoie volontairement un JSON cassé (pour tester la gestion d'erreur).

La réponse « génération d'enquête » sera ajoutée avec la génération (S4).
"""

import itertools
import json
from decimal import Decimal

from . import ReponseIA

REPONSES_INTERROGATOIRE = [
    {
        "reponse": "Moi ? Je faisais ma sieste au soleil, comme tout chat respectable.",
        "stress": 25,
        "indices": [],
    },
    {
        "reponse": "J'ai vu une ombre rousse filer vers la cuisine… mais je n'en dirai pas plus.",
        "stress": 40,
        "indices": [{"texte": "Une ombre rousse a filé vers la cuisine.", "liens": []}],
    },
    {
        "reponse": "Miaou ? Ces questions me donnent des poils hérissés, inspecteur.",
        "stress": 55,
        "indices": [],
    },
]

# Un compteur commun : les réponses tournent d'un appel à l'autre.
_suivante = itertools.cycle(range(len(REPONSES_INTERROGATOIRE)))


class FauxFournisseur:
    nom = "faux"

    def __init__(self, invalide: bool = False):
        self.invalide = invalide

    def completer(self, modele: str, messages: list[dict], nom_schema: str, schema: dict):
        if self.invalide:
            contenu = "{ ceci n'est pas du JSON"
        elif nom_schema == "interrogatoire":
            contenu = json.dumps(REPONSES_INTERROGATOIRE[next(_suivante)], ensure_ascii=False)
        else:
            raise NotImplementedError(f"Pas de réponse prédéfinie pour le schéma {nom_schema!r}")

        # Jetons simulés : à peu près 1 jeton pour 4 caractères.
        taille_prompt = sum(len(m["content"]) for m in messages)
        return ReponseIA(
            contenu=contenu,
            modele=f"faux/{modele or 'modele'}",
            jetons_entree=taille_prompt // 4,
            jetons_sortie=len(contenu) // 4,
            cout_usd=Decimal("0"),
        )
