"""
jeu/api.py — API JSON du jeu, lue par l'écran de partie en Vue.

Décision D-001 (docs/decisions/) : Django rend les pages de contenu, Vue rend
les écrans de jeu et dialogue avec le serveur en JSON. Le contrat complet
(adresses, corps des requêtes et des réponses, erreurs) est dans
docs/specification.md §5.4.

Pour l'instant, en lecture seule :
  - la partie de démonstration, sans base de données ni IA (jeu/demo.py) ;
  - les vraies parties, lues en base (jeu/lecture.py), pour leurs joueurs.
Les écritures (question, carte, avis, fiche, accusation) suivront la même
forme ; elles appelleront jeu/services.py.

Format d'erreur commun à toute l'API :
    {"erreur": {"type": "<code court>", "message": "<phrase pour le joueur>"}}
Jamais de stack trace : le message est écrit pour être affiché tel quel.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from . import demo, lecture
from .models import Partie, Suspect
from .services import assurer_fiche


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


def _partie_du_joueur(request, pk):
    """Renvoie (partie, None) si le joueur connecté y participe, sinon (None, erreur JSON).

    Une partie d'un autre joueur répond 404, comme si elle n'existait pas (spec §8).
    """
    if not request.user.is_authenticated:
        return None, reponse_erreur(
            "connexion", "Votre session a expiré : reconnectez-vous pour reprendre l'enquête.", 401
        )
    partie = (
        Partie.objects.select_related("enquete", "hote__profil__palier")
        .filter(pk=pk, participations__joueur=request.user)
        .first()
    )
    if partie is None:
        return None, reponse_erreur(
            "introuvable", "Cette enquête n'existe pas ou ne fait pas partie de vos dossiers.", 404
        )
    return partie, None


@require_GET
def partie(request, pk: int):
    """GET /api/parties/<pk>/ — état d'une vraie partie, vu par le joueur connecté."""
    partie, erreur = _partie_du_joueur(request, pk)
    if erreur:
        return erreur
    assurer_fiche(partie, request.user)
    return JsonResponse(lecture.etat_partie(partie, request.user))


@require_GET
def interrogatoire(request, pk: int, suspect_id: int):
    """GET /api/parties/<pk>/suspects/<id>/ — un suspect de la partie et sa conversation."""
    partie, erreur = _partie_du_joueur(request, pk)
    if erreur:
        return erreur
    suspect = Suspect.objects.filter(pk=suspect_id, enquete_id=partie.enquete_id).first()
    if suspect is None:
        return reponse_erreur("introuvable", "Ce suspect ne fait pas partie de l'enquête.", 404)
    return JsonResponse(lecture.interrogatoire(partie, suspect))
