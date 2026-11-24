"""
ia/fournisseurs — Les « fournisseurs » savent parler à un modèle d'IA.

Deux fournisseurs, même interface (méthode `completer`) :
  - faux       : réponses prédéfinies, gratuites (local, CI, tests) ;
  - openrouter : vrai appel à OpenRouter (payant).

Le choix se fait avec la variable d'environnement IA_FOURNISSEUR.
Seul ia/services.py utilise ce module (règle IA n°1 du dépôt).
"""

from dataclasses import dataclass
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


@dataclass
class ReponseIA:
    """Ce que renvoie un fournisseur : le texte brut et la consommation."""

    contenu: str  # le JSON renvoyé par le modèle, pas encore lu
    modele: str
    jetons_entree: int = 0
    jetons_sortie: int = 0
    cout_usd: Decimal = Decimal("0")


def obtenir_fournisseur():
    """Renvoie le fournisseur choisi par IA_FOURNISSEUR (`faux` par défaut)."""
    nom = settings.IA_FOURNISSEUR
    if nom == "faux":
        from .faux import FauxFournisseur

        return FauxFournisseur()
    if nom == "openrouter":
        from .openrouter import FournisseurOpenRouter

        return FournisseurOpenRouter()
    raise ImproperlyConfigured(f"IA_FOURNISSEUR inconnu : {nom!r} (attendu : faux ou openrouter)")
