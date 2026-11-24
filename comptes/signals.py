"""
comptes/signals.py — Création automatique du profil.

Chaque fois qu'un User est créé (inscription, createsuperuser, admin…),
Django envoie le signal post_save : on en profite pour lui créer son Profil,
rattaché au palier Free. Ainsi `user.profil` existe toujours.

Le signal est branché dans ComptesConfig.ready() (comptes/apps.py).
"""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Palier, Profil


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def creer_profil(sender, instance, created, raw=False, **kwargs):
    # raw=True pendant un loaddata : on ne touche à rien.
    if created and not raw:
        Profil.objects.get_or_create(
            utilisateur=instance,
            defaults={"palier": Palier.gratuit(), "pseudo": instance.username},
        )
