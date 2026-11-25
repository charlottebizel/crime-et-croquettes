"""
jeu/views.py — Pages du jeu.

Depuis la décision D-001, l'écran de partie est une application Vue :
la vue Django ne renvoie qu'une « coquille » (templates/jeu/partie.html)
avec l'adresse de l'API à lire. Les données arrivent ensuite en JSON
(jeu/api.py).

Accès (spec §8) : les vraies parties exigent d'être connecté ET de participer
à la partie. Une partie d'un autre joueur répond 404, comme si elle
n'existait pas (on ne révèle pas son existence).
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from . import demo
from .models import Participation, Partie
from .services import assurer_fiche


@ensure_csrf_cookie
def partie_demo(request):
    """Écran de partie de démonstration (publique, sans base de données ni IA).

    ensure_csrf_cookie : pose le cookie « csrftoken », que le frontend Vue
    renverra dans l'en-tête X-CSRFToken de ses requêtes POST (exigé par
    Django pour toute écriture).
    """
    return render(
        request,
        "jeu/partie.html",
        {
            "titre_page": demo.TITRE,
            "url_api": reverse("api_jeu:partie_demo"),
            "mode_demo": True,
        },
    )


@login_required
def liste(request):
    """« Mes parties » : les enquêtes du joueur connecté, la plus récente d'abord."""
    participations = (
        Participation.objects.filter(joueur=request.user)
        .select_related("partie__enquete", "partie__hote")
        .order_by("-partie__cree_le")
    )
    return render(request, "jeu/liste.html", {"participations": participations})


@login_required
@ensure_csrf_cookie
def partie(request, pk):
    """Écran d'une vraie partie : la même application Vue que la démo,
    branchée sur /api/parties/<pk>/."""
    partie = get_object_or_404(
        Partie.objects.select_related("enquete"), pk=pk, participations__joueur=request.user
    )
    assurer_fiche(partie, request.user)  # par sécurité : 15 cases pour ce joueur
    return render(
        request,
        "jeu/partie.html",
        {
            "titre_page": partie.enquete.titre,
            "url_api": reverse("api_jeu:partie", args=[partie.pk]),
            "mode_demo": False,
        },
    )
