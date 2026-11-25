"""
jeu/api.py — API JSON du jeu, lue par l'écran de partie en Vue.

Décision D-001 (docs/decisions/) : Django rend les pages de contenu, Vue rend
les écrans de jeu et dialogue avec le serveur en JSON. Le contrat complet
(adresses, corps des requêtes et des réponses, erreurs) est dans
docs/specification.md §5.4.

Pour l'instant : la partie de démonstration, en lecture seule, sans base de
données ni IA (données de jeu/demo.py). Les endpoints de vraies parties
(GET d'une partie, question, carte, avis, fiche, accusation) suivront la
même forme ; Charlotte les branchera sur jeu/services.py.

Format d'erreur commun à toute l'API :
    {"erreur": {"type": "<code court>", "message": "<phrase pour le joueur>"}}
Jamais de stack trace : le message est écrit pour être affiché tel quel.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from . import demo


def reponse_erreur(type_erreur: str, message: str, statut: int) -> JsonResponse:
    """Réponse d'erreur au format commun de l'API (spec §5.4)."""
    return JsonResponse({"erreur": {"type": type_erreur, "message": message}}, status=statut)


@require_GET
def partie_demo(request):
    """GET /api/parties/demo/ — état complet de la partie de démo (sans conversations)."""
    return JsonResponse(demo.etat_partie())


@require_GET
def interrogatoire_demo(request, suspect_id: int):
    """GET /api/parties/demo/suspects/<id>/ — un suspect et sa conversation."""
    donnees = demo.interrogatoire(suspect_id)
    if donnees is None:
        return reponse_erreur("introuvable", "Ce suspect ne fait pas partie de l'enquête.", 404)
    return JsonResponse(donnees)
