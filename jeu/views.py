"""
jeu/views.py — Pages du jeu.

Depuis la décision D-001, l'écran de partie est une application Vue :
la vue Django ne renvoie qu'une « coquille » (templates/jeu/partie.html)
avec l'adresse de l'API à lire. Les données arrivent ensuite en JSON
(jeu/api.py).
"""

from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from . import demo


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
