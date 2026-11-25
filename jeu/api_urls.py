"""
jeu/api_urls.py — Adresses de l'API JSON du jeu (préfixe /api/parties/).

Règle de forme, utilisée par le frontend Vue (spec §5.4) :
    <adresse de la partie>                 → état de la partie
    <adresse de la partie>suspects/<id>/   → un suspect et sa conversation
La démo et les vraies parties suivent la même forme : seul le début change
(/api/parties/demo/ ou /api/parties/<pk>/).
"""

from django.urls import path

from . import api

app_name = "api_jeu"

urlpatterns = [
    path("demo/", api.partie_demo, name="partie_demo"),
    path(
        "demo/suspects/<int:suspect_id>/",
        api.interrogatoire_demo,
        name="interrogatoire_demo",
    ),
]
