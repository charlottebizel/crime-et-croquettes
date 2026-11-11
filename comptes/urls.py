"""
comptes/urls.py — Adresses de l'app comptes.

Noms à utiliser dans les templates (contrat de docs/specification.md §5.1) :
    {% url 'comptes:inscription' %}
    {% url 'comptes:connexion' %}
    {% url 'comptes:deconnexion' %}   (formulaire POST obligatoire)
"""

from django.urls import path

from . import views

app_name = "comptes"

urlpatterns = [
    path("inscription/", views.inscription, name="inscription"),
    path("connexion/", views.Connexion.as_view(), name="connexion"),
    path("deconnexion/", views.Deconnexion.as_view(), name="deconnexion"),
]