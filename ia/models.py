"""
ia/models.py — Journal des appels au modèle d'IA (spec §3.5, exigence O4).

Chaque appel, réussi ou raté, crée une ligne AppelIA : c'est la base du
tableau de bord des coûts (/gestion/couts/) et du calcul du pricing.

Le journal doit rester exact même si un joueur supprime son compte ou une
partie : les liens vers l'utilisateur et la partie passent alors à NULL
(SET_NULL) au lieu d'effacer la ligne.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models


class AppelIA(models.Model):
    class Type(models.TextChoices):
        GENERATION = "generation", "Génération d'enquête"
        INTERROGATOIRE = "interrogatoire", "Interrogatoire"

    class Erreur(models.TextChoices):
        DELAI = "delai", "Délai dépassé"
        PANNE = "panne", "Service indisponible"
        CREDIT = "credit", "Crédit épuisé"
        INVALIDE = "invalide", "Réponse invalide"

    cree_le = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appels_ia",
    )
    partie = models.ForeignKey(
        "jeu.Partie",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appels_ia",
    )
    type = models.CharField(max_length=14, choices=Type.choices)
    modele = models.CharField(max_length=100)
    jetons_entree = models.PositiveIntegerField(default=0)
    jetons_sortie = models.PositiveIntegerField(default=0)
    cout_usd = models.DecimalField(max_digits=10, decimal_places=6, default=Decimal("0"))
    duree_ms = models.PositiveIntegerField(default=0)
    succes = models.BooleanField(default=False)
    # "" = pas d'erreur (convention Django : pas de NULL sur un texte).
    erreur_type = models.CharField(max_length=8, choices=Erreur.choices, blank=True, default="")
    # Détail technique pour les admins : JAMAIS affiché à un joueur.
    erreur_detail = models.TextField(blank=True)

    class Meta:
        ordering = ["-cree_le"]
        verbose_name = "appel IA"
        verbose_name_plural = "appels IA"
        indexes = [models.Index(fields=["cree_le"])]  # requêtes « par jour » du tableau de bord

    def __str__(self) -> str:
        etat = "ok" if self.succes else f"échec ({self.erreur_type})"
        return f"{self.get_type_display()} — {self.modele} — {etat}"
