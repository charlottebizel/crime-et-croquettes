"""
jeu/admin.py — Consultation des enquêtes et des parties dans l'admin Django.

Réservé aux admins (is_staff) : c'est le seul endroit où la solution
d'une enquête est visible avant la fin d'une partie.
"""

from django.contrib import admin

from .models import (
    Accusation,
    CartePreuve,
    Enquete,
    EntreeCarnet,
    Lieu,
    Message,
    Objet,
    Participation,
    Partie,
    Suspect,
)


class SuspectInline(admin.StackedInline):
    model = Suspect
    extra = 0


class ObjetInline(admin.TabularInline):
    model = Objet
    extra = 0


class LieuInline(admin.TabularInline):
    model = Lieu
    extra = 0


class CarteInline(admin.TabularInline):
    model = CartePreuve
    extra = 0


@admin.register(Enquete)
class EnqueteAdmin(admin.ModelAdmin):
    list_display = ("titre", "theme", "difficulte", "statut", "creee_par", "cree_le")
    list_filter = ("statut", "difficulte")
    search_fields = ("titre",)
    inlines = [SuspectInline, ObjetInline, LieuInline, CarteInline]


class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 0


@admin.register(Partie)
class PartieAdmin(admin.ModelAdmin):
    list_display = ("code_invitation", "enquete", "hote", "statut", "questions_posees", "cree_le")
    list_filter = ("statut",)
    search_fields = ("code_invitation", "hote__username")
    inlines = [ParticipationInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("partie", "suspect", "est_suspect", "texte", "cree_le")
    list_filter = ("est_suspect",)


@admin.register(EntreeCarnet)
class EntreeCarnetAdmin(admin.ModelAdmin):
    list_display = ("partie", "type", "texte", "cree_le")
    list_filter = ("type",)


@admin.register(Accusation)
class AccusationAdmin(admin.ModelAdmin):
    list_display = ("partie", "joueur", "suspect", "objet", "lieu", "correcte", "cree_le")
    list_filter = ("correcte",)
