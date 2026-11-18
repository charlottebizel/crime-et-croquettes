"""
jeu/views.py — Vues du jeu.

Pour l'instant une seule vue : la démonstration de l'écran de partie
(ticket LB-001), avec des données en dur (jeu/demo.py). Les vraies vues
(spec §5.2 : jeu:partie, jeu:question, jeu:tirer_carte…) seront écrites
par Charlotte quand les modèles existeront ; elles enverront les mêmes
variables au même template.
"""

from django.shortcuts import render

from . import demo


def partie_demo(request):
    """Écran de partie de démonstration, sans base de données ni IA.

    Publique (pas de connexion requise) : elle ne contient aucune donnée de
    joueur et pourra servir d'aperçu depuis la landing page.
    Paramètre optionnel : ?suspect=<id> pour choisir le suspect interrogé.
    """
    contexte = demo.contexte_partie(request.GET.get("suspect"))
    return render(request, "jeu/partie.html", contexte)
