"""
jeu/urls.py — Pages du jeu (préfixe /parties/, voir config/urls.py).

Noms à utiliser dans les templates :
    {% url 'jeu:liste' %}             → /parties/          (mes parties)
    {% url 'jeu:partie_demo' %}       → /parties/demo/     (démo publique)
    {% url 'jeu:partie' partie.pk %}  → /parties/<pk>/     (une vraie partie)

L'API JSON lue par l'écran Vue est dans jeu/api_urls.py.
"""

from django.urls import path

from . import views

app_name = "jeu"

urlpatterns = [
    path("", views.liste, name="liste"),
    path("demo/", views.partie_demo, name="partie_demo"),
    path("<int:pk>/", views.partie, name="partie"),
]
