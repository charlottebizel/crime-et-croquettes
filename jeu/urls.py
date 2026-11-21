"""
jeu/urls.py — Adresses de l'app jeu (préfixe /parties/, voir config/urls.py).

Noms à utiliser dans les templates :
    {% url 'jeu:partie_demo' %}   → /parties/demo/

Les autres adresses de la spec §5.2 (jeu:liste, jeu:partie, jeu:question…)
seront ajoutées ici avec les vraies vues.
"""

from django.urls import path

from . import views

app_name = "jeu"

urlpatterns = [
    path("demo/", views.partie_demo, name="partie_demo"),
]
