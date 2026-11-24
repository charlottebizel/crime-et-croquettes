"""
Migration de données : crée les paliers Free et Pro, puis un profil Free
pour chaque utilisateur qui existait déjà avant l'ajout des profils
(sinon `user.profil` planterait pour eux, par exemple en production).

Les valeurs sont copiées ici (et non importées depuis models.py) : une
migration doit rester identique même si le code change plus tard.
"""

from decimal import Decimal

from django.db import migrations

PALIERS = [
    {
        "nom": "Free",
        "prix_mensuel_eur": Decimal("0.00"),
        "parties_par_mois": 3,
        "questions_par_partie": 20,
        "cartes_par_partie": 6,
    },
    {
        "nom": "Pro",
        "prix_mensuel_eur": Decimal("4.99"),
        "parties_par_mois": 30,
        "questions_par_partie": 40,
        "cartes_par_partie": 6,
    },
]


def creer_paliers_et_profils(apps, schema_editor):
    Palier = apps.get_model("comptes", "Palier")
    Profil = apps.get_model("comptes", "Profil")
    User = apps.get_model("auth", "User")

    for valeurs in PALIERS:
        Palier.objects.get_or_create(nom=valeurs["nom"], defaults=valeurs)

    gratuit = Palier.objects.get(nom="Free")
    for utilisateur in User.objects.filter(profil__isnull=True):
        Profil.objects.create(utilisateur=utilisateur, palier=gratuit, pseudo=utilisateur.username)


def annuler(apps, schema_editor):
    # Retour arrière : la migration 0001 supprimera de toute façon les tables.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("comptes", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(creer_paliers_et_profils, annuler),
    ]
