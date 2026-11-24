"""
python manage.py essai_ia — Un seul petit appel IA, pour vérifier la chaîne.

Avec IA_FOURNISSEUR=faux (défaut) : gratuit, rien ne sort de la machine.
Avec IA_FOURNISSEUR=openrouter : UN vrai appel, quelques dixièmes de
centime. L'appel est journalisé dans AppelIA (visible dans l'admin).
"""

from django.conf import settings
from django.core.management.base import BaseCommand

from ia.erreurs import ErreurIA
from ia.services import appeler

SCHEMA_ESSAI = {
    "type": "object",
    "properties": {
        "reponse": {"type": "string"},
        "stress": {"type": "integer"},
        "indices": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "texte": {"type": "string"},
                    "liens": {"type": "array", "items": {"type": "object"}},
                },
                "required": ["texte", "liens"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["reponse", "stress", "indices"],
    "additionalProperties": False,
}


class Command(BaseCommand):
    help = "Fait un seul appel IA de test (faux ou OpenRouter selon IA_FOURNISSEUR)."

    def handle(self, *args, **options):
        modele = settings.IA_MODELE_INTERROGATOIRE
        self.stdout.write(f"Fournisseur : {settings.IA_FOURNISSEUR} — modèle : {modele or '?'}")
        messages = [
            {
                "role": "system",
                "content": "Tu es Gros Minou, un chat roux gourmand. Réponds en une phrase, "
                "en JSON : reponse, stress (0-100), indices (liste vide).",
            },
            {"role": "user", "content": "Où étais-tu dimanche midi ?"},
        ]
        try:
            donnees, journal = appeler(
                type_appel="interrogatoire",
                modele=modele,
                messages=messages,
                nom_schema="interrogatoire",
                schema=SCHEMA_ESSAI,
            )
        except ErreurIA as erreur:
            self.stderr.write(self.style.ERROR(f"Échec ({erreur.type_erreur}) : {erreur.detail}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Réponse : {donnees.get('reponse')}"))
        self.stdout.write(
            f"Jetons : {journal.jetons_entree} + {journal.jetons_sortie} — "
            f"coût : {journal.cout_usd} $ — durée : {journal.duree_ms} ms"
        )
