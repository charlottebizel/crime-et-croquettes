"""
config/urls.py — Adresses racine du projet.

Chaque app a son propre fichier urls.py, inclus ici avec un préfixe.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Comptes : /comptes/inscription/, /comptes/connexion/, /comptes/deconnexion/
    path("comptes/", include("comptes.urls")),
    # Pages publiques (accueil, et plus tard tarifs et page légale)
    path("", include("pages.urls")),
]