"""
gestion/views.py — Pages et API réservées aux administrateurs (ticket LB-005).

Pour l'instant : le tableau de bord des coûts de l'IA (exigence O4).
  - la page /gestion/couts/ est une « coquille » qui monte l'application Vue
    static/js/gestion/ (décision D-001) ;
  - l'API /api/gestion/couts/ renvoie les chiffres en JSON.

Accès : administrateurs seulement (user.is_staff), vérifié par le serveur.
  - visiteur non connecté → page : redirection vers la connexion ; API : 401 ;
  - joueur connecté non administrateur → 403.
"""

from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET

from .statistiques import tableau_de_bord


def reserve_aux_admins(vue):
    """Décorateur pour une PAGE réservée aux administrateurs."""

    @wraps(vue)
    def verifier(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.is_staff:
            raise PermissionDenied("Réservé aux administrateurs.")
        return vue(request, *args, **kwargs)

    return verifier


def _erreur(type_erreur, message, statut):
    """Même format d'erreur que l'API du jeu (spec §5.4)."""
    return JsonResponse({"erreur": {"type": type_erreur, "message": message}}, status=statut)


@reserve_aux_admins
def couts(request):
    """Page du tableau de bord des coûts (coquille de l'application Vue)."""
    return render(request, "gestion/couts.html", {"url_api": reverse("api_gestion:couts")})


@require_GET
def api_couts(request):
    """GET /api/gestion/couts/?jours=7|30|90 — chiffres du tableau de bord."""
    if not request.user.is_authenticated:
        return _erreur("connexion", "Votre session a expiré : reconnectez-vous.", 401)
    if not request.user.is_staff:
        return _erreur("interdit", "Ce tableau de bord est réservé aux administrateurs.", 403)
    try:
        jours = int(request.GET.get("jours", 30))
    except ValueError:
        jours = 30
    return JsonResponse(tableau_de_bord(jours))
