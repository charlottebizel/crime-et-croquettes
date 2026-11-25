"""
gestion/urls.py — Pages d'administration (préfixe /gestion/).

    {% url 'gestion:couts' %}  → /gestion/couts/  (tableau de bord des coûts IA)
"""

from django.urls import path

from . import views

app_name = "gestion"

urlpatterns = [
    path("couts/", views.couts, name="couts"),
]
