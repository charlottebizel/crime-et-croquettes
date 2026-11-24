from django.contrib import admin

from .models import AppelIA


@admin.register(AppelIA)
class AppelIAAdmin(admin.ModelAdmin):
    """Journal en lecture seule : on ne modifie pas l'historique des coûts."""

    list_display = (
        "cree_le",
        "type",
        "modele",
        "utilisateur",
        "jetons_entree",
        "jetons_sortie",
        "cout_usd",
        "duree_ms",
        "succes",
        "erreur_type",
    )
    list_filter = ("type", "succes", "erreur_type", "modele")
    date_hierarchy = "cree_le"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
