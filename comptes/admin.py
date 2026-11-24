from django.contrib import admin

from .models import Palier, Profil


@admin.register(Palier)
class PalierAdmin(admin.ModelAdmin):
    list_display = (
        "nom",
        "prix_mensuel_eur",
        "parties_par_mois",
        "questions_par_partie",
        "cartes_par_partie",
    )


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ("utilisateur", "pseudo", "palier", "cree_le")
    list_filter = ("palier",)
    search_fields = ("utilisateur__username", "pseudo")
