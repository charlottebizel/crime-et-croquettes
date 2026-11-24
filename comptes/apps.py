from django.apps import AppConfig


class ComptesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "comptes"

    def ready(self):
        # Branche le signal qui crée le Profil de chaque nouvel utilisateur.
        from . import signals  # noqa: F401
