from django.shortcuts import render


def accueil(request):
    """Landing page publique (template remplacé par le frontend)."""
    return render(request, "pages/accueil.html")
