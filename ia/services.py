"""
ia/services.py — Point d'entrée UNIQUE vers le modèle d'IA (règle IA n°1).

Aucune vue, aucun template, aucun JavaScript n'appelle le modèle
directement : tout passe par `appeler()`, qui
  1. demande la réponse au fournisseur choisi (faux ou OpenRouter) ;
  2. lit le JSON renvoyé et le fait valider ;
  3. enregistre l'appel dans AppelIA, qu'il réussisse ou non (O4).
"""

import json
import time
from collections.abc import Callable

from .erreurs import ErreurIA, ReponseInvalide
from .fournisseurs import obtenir_fournisseur
from .models import AppelIA


def appeler(
    *,
    type_appel: str,
    modele: str,
    messages: list[dict],
    nom_schema: str,
    schema: dict,
    valider: Callable[[dict], dict] | None = None,
    utilisateur=None,
    partie=None,
    fournisseur=None,
) -> tuple[dict, AppelIA]:
    """Fait un appel IA journalisé et renvoie (données validées, AppelIA).

    `valider` reçoit le dict lu dans le JSON et renvoie les données propres,
    ou lève ReponseInvalide. En cas d'échec, l'AppelIA est enregistré avec
    succes=False, puis l'ErreurIA est relancée pour que la vue l'affiche.
    """
    fournisseur = fournisseur or obtenir_fournisseur()
    journal = AppelIA(type=type_appel, modele=modele, utilisateur=utilisateur, partie=partie)
    debut = time.monotonic()
    try:
        reponse = fournisseur.completer(modele, messages, nom_schema, schema)
        journal.modele = reponse.modele
        journal.jetons_entree = reponse.jetons_entree
        journal.jetons_sortie = reponse.jetons_sortie
        journal.cout_usd = reponse.cout_usd

        try:
            donnees = json.loads(reponse.contenu)
        except json.JSONDecodeError as erreur:
            raise ReponseInvalide(f"JSON illisible : {erreur}") from erreur
        if not isinstance(donnees, dict):
            raise ReponseInvalide("Le JSON n'est pas un objet")
        if valider is not None:
            donnees = valider(donnees)
    except ErreurIA as erreur:
        journal.succes = False
        journal.erreur_type = erreur.type_erreur
        journal.erreur_detail = erreur.detail[:2000]
        raise
    else:
        journal.succes = True
        return donnees, journal
    finally:
        # Exécuté dans tous les cas : l'appel est toujours journalisé.
        journal.duree_ms = int((time.monotonic() - debut) * 1000)
        journal.save()
