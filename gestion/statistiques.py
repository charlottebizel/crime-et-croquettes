"""
gestion/statistiques.py — Chiffres du tableau de bord des coûts (ticket LB-005, exigence O4).

Toutes les données viennent du journal ia.AppelIA, où ia/services.py
enregistre CHAQUE appel au modèle (réussi ou raté) avec ses jetons, son
coût et sa durée. Rien n'est estimé ici : on additionne ce qui a été payé.

Les clés renvoyées sont celles de docs/specification.md §6.7 :
par_jour, par_utilisateur, totaux, derniers_appels.

Les montants sont en dollars (USD) : c'est la monnaie dans laquelle
OpenRouter facture et renvoie le coût de chaque appel. On ne les convertit
pas ici : la clé « devise » donne le taux du jour (gestion/taux.py : API
Frankfurter / BCE, sinon taux de secours) et l'écran affiche les euros. Ainsi le chiffre exact reste
disponible et le taux peut changer sans toucher aux données.
"""

from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from ia.models import AppelIA
from jeu.models import Partie

from .taux import taux_du_jour

PERIODES = (7, 30, 90)  # jours proposés dans le filtre du tableau de bord


def _usd(valeur) -> float:
    """Decimal ou None → nombre JSON, arrondi au millionième de dollar."""
    return round(float(valeur or Decimal("0")), 6)


def _par_jour(appels, debut, fin) -> list[dict]:
    """Une ligne par jour de la période, y compris les jours sans appel (à zéro)."""
    lignes = {
        ligne["jour"]: ligne
        for ligne in appels.annotate(jour=TruncDate("cree_le"))
        .values("jour")
        .annotate(
            nb_appels=Count("id"),
            nb_echecs=Count("id", filter=Q(succes=False)),
            jetons_entree=Sum("jetons_entree"),
            jetons_sortie=Sum("jetons_sortie"),
            cout_usd=Sum("cout_usd"),
        )
    }
    resultat = []
    jour = debut
    while jour <= fin:
        ligne = lignes.get(jour, {})
        resultat.append(
            {
                "date": jour.isoformat(),
                "nb_appels": ligne.get("nb_appels", 0),
                "nb_echecs": ligne.get("nb_echecs", 0),
                "jetons_entree": ligne.get("jetons_entree") or 0,
                "jetons_sortie": ligne.get("jetons_sortie") or 0,
                "cout_usd": _usd(ligne.get("cout_usd")),
            }
        )
        jour += timedelta(days=1)
    return resultat


def _par_utilisateur(appels) -> list[dict]:
    """Consommation par joueur, du plus coûteux au moins coûteux."""
    debut_mois = timezone.localdate().replace(day=1)
    parties_du_mois = dict(
        Partie.objects.filter(cree_le__date__gte=debut_mois)
        .values("hote__username")
        .annotate(n=Count("id"))
        .values_list("hote__username", "n")
    )
    lignes = (
        appels.values("utilisateur__username", "utilisateur__profil__palier__nom")
        .annotate(nb_appels=Count("id"), cout_usd=Sum("cout_usd"))
        .order_by("-cout_usd", "-nb_appels")
    )
    return [
        {
            # Compte supprimé : le journal garde l'appel, sans l'utilisateur (spec §8).
            "pseudo": ligne["utilisateur__username"] or "Compte supprimé",
            "palier": ligne["utilisateur__profil__palier__nom"] or "—",
            "nb_appels": ligne["nb_appels"],
            "cout_usd": _usd(ligne["cout_usd"]),
            "parties_ce_mois": parties_du_mois.get(ligne["utilisateur__username"], 0),
        }
        for ligne in lignes
    ]


def _totaux(appels) -> dict:
    totaux = appels.aggregate(
        nb_appels=Count("id"),
        nb_echecs=Count("id", filter=Q(succes=False)),
        cout_usd=Sum("cout_usd"),
        jetons_entree=Sum("jetons_entree"),
        jetons_sortie=Sum("jetons_sortie"),
        duree_moyenne_ms=Avg("duree_ms"),
    )
    reussis = appels.filter(succes=True)
    moyennes = reussis.aggregate(
        generation=Avg("cout_usd", filter=Q(type=AppelIA.Type.GENERATION)),
        question=Avg("cout_usd", filter=Q(type=AppelIA.Type.INTERROGATOIRE)),
    )
    nb = totaux["nb_appels"]
    return {
        "nb_appels": nb,
        "nb_echecs": totaux["nb_echecs"],
        "taux_echec": round(totaux["nb_echecs"] / nb, 4) if nb else 0,
        "cout_usd": _usd(totaux["cout_usd"]),
        "jetons_entree": totaux["jetons_entree"] or 0,
        "jetons_sortie": totaux["jetons_sortie"] or 0,
        "duree_moyenne_ms": round(totaux["duree_moyenne_ms"] or 0),
        # Base du calcul du pricing (spec §10) : coût moyen d'une action réussie.
        "cout_moyen_generation": _usd(moyennes["generation"]),
        "cout_moyen_question": _usd(moyennes["question"]),
        # Tout l'historique, pour suivre le budget de 1 € du projet.
        "cout_depuis_le_debut": _usd(AppelIA.objects.aggregate(t=Sum("cout_usd"))["t"]),
    }


def _derniers_appels(nombre=20) -> list[dict]:
    """Les derniers appels, SANS erreur_detail (détail technique réservé à l'admin Django)."""
    appels = AppelIA.objects.select_related("utilisateur").order_by("-cree_le", "-pk")[:nombre]
    return [
        {
            "id": a.pk,
            "date": timezone.localtime(a.cree_le).isoformat(timespec="seconds"),
            "pseudo": a.utilisateur.username if a.utilisateur else "Compte supprimé",
            "type": a.get_type_display(),
            "modele": a.modele,
            "jetons_entree": a.jetons_entree,
            "jetons_sortie": a.jetons_sortie,
            "cout_usd": _usd(a.cout_usd),
            "duree_ms": a.duree_ms,
            "succes": a.succes,
            "erreur": a.get_erreur_type_display() if a.erreur_type else "",
        }
        for a in appels
    ]


def tableau_de_bord(jours: int = 30) -> dict:
    """Données de /gestion/couts/ pour les `jours` derniers jours (aujourd'hui compris)."""
    if jours not in PERIODES:
        jours = 30
    fin = timezone.localdate()
    debut = fin - timedelta(days=jours - 1)
    appels = AppelIA.objects.filter(cree_le__date__gte=debut)
    return {
        "periode": {"jours": jours, "debut": debut.isoformat(), "fin": fin.isoformat()},
        "periodes_possibles": list(PERIODES),
        "devise": {**taux_du_jour(), "budget_eur": float(settings.BUDGET_IA_EUR)},
        "par_jour": _par_jour(appels, debut, fin),
        "par_utilisateur": _par_utilisateur(appels),
        "totaux": _totaux(appels),
        "derniers_appels": _derniers_appels(),
    }
