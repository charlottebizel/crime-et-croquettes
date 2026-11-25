"""
gestion/api_urls.py — API JSON d'administration (préfixe /api/gestion/).

    /api/gestion/couts/?jours=30  → chiffres du tableau de bord (spec §6.7)
"""

from django.urls import path

from . import views

app_name = "api_gestion"

urlpatterns = [
    path("couts/", views.api_couts, name="couts"),
]
