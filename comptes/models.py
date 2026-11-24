"""
comptes/models.py — Paliers d'abonnement et profil des joueurs (spec §3.1).

Exigences O3 (comptes et rôles) et O6 (offre Free / Pro) :
  - Palier : ce qu'un abonnement autorise (parties par mois, questions…) ;
  - Profil : complète le User de Django (un profil par utilisateur), créé
    automatiquement à l'inscription par un signal (comptes/signals.py).

Le rôle administrateur n'est pas ici : c'est user.is_staff.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models

# Valeurs de départ (spec §3.1). Elles seront recalculées à partir des coûts
# observés dans /gestion/couts/ (spec §10, pricing).
PALIER_GRATUIT = "Free"
PALIER_PRO = "Pro"
VALEURS_PALIERS = {
    PALIER_GRATUIT: {
        "prix_mensuel_eur": Decimal("0.00"),
        "parties_par_mois": 3,
        "questions_par_partie": 20,
        "cartes_par_partie": 6,
    },
    PALIER_PRO: {
        "prix_mensuel_eur": Decimal("4.99"),  # provisoire, à recalculer (§10)
        "parties_par_mois": 30,
        "questions_par_partie": 40,
        "cartes_par_partie": 6,
    },
}


class Palier(models.Model):
    """Un niveau d'abonnement : Free ou Pro."""

    nom = models.CharField(max_length=30, unique=True)
    prix_mensuel_eur = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0"))
    parties_par_mois = models.PositiveIntegerField()
    questions_par_partie = models.PositiveIntegerField()
    cartes_par_partie = models.PositiveIntegerField(default=6)

    class Meta:
        ordering = ["prix_mensuel_eur"]

    def __str__(self) -> str:
        return self.nom

    @classmethod
    def gratuit(cls) -> "Palier":
        """Renvoie le palier Free (le crée s'il manque, par sécurité)."""
        palier, _ = cls.objects.get_or_create(
            nom=PALIER_GRATUIT, defaults=VALEURS_PALIERS[PALIER_GRATUIT]
        )
        return palier


class Profil(models.Model):
    """Informations du joueur qui ne sont pas dans le User de Django."""

    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profil"
    )
    # PROTECT : on ne peut pas supprimer un palier tant que des joueurs l'utilisent.
    palier = models.ForeignKey(Palier, on_delete=models.PROTECT, related_name="profils")
    pseudo = models.CharField(max_length=40, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.pseudo or self.utilisateur.username} ({self.palier})"
