"""
gestion/taux.py — Taux de change euro → dollar pour le tableau de bord des coûts.

OpenRouter facture en dollars ; le tableau de bord affiche des euros.
On demande le taux du jour à l'API publique Frankfurter
(https://frankfurter.dev : gratuite, sans clé, taux de référence de la
Banque centrale européenne, publiés chaque jour ouvrable vers 16 h).

Deux protections pour que la page ne tombe jamais à cause de l'API :
  1. cache de 6 h : au plus un appel à Frankfurter toutes les 6 heures
     (le taux BCE ne change qu'une fois par jour de toute façon) ;
  2. taux de secours : si l'API ne répond pas (panne, pas d'Internet,
     réponse bizarre), on prend TAUX_USD_POUR_1_EUR et TAUX_DATE des
     réglages, et l'écran le signale (« taux de secours »).

Réglage TAUX_CHANGE_URL vide → on n'appelle jamais l'API (tests, hors ligne).
"""

import json
import logging
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache

journal = logging.getLogger(__name__)

CLE_CACHE = "gestion:taux_usd_pour_1_eur"
DUREE_CACHE = 6 * 60 * 60  # secondes
DELAI_API = 3  # secondes : la page n'attend pas plus longtemps


def taux_de_secours() -> dict:
    """Le taux fixe des réglages (variables d'environnement)."""
    return {
        "usd_pour_1_eur": float(settings.TAUX_USD_POUR_1_EUR),
        "date_taux": settings.TAUX_DATE,
        "source": "secours",
    }


def _demander_a_frankfurter(url: str) -> dict:
    """Appelle l'API. Réponse attendue :
    {"amount": 1.0, "base": "EUR", "date": "2026-11-24", "rates": {"USD": 1.0968}}
    Lève ValueError si la réponse n'a pas cette forme."""
    requete = Request(url, headers={"User-Agent": "crimes-et-croquette"})
    with urlopen(requete, timeout=DELAI_API) as reponse:  # noqa: S310 (URL des réglages)
        donnees = json.load(reponse)
    taux = float(donnees["rates"]["USD"])
    if not 0.5 < taux < 2:  # garde-fou : un taux absurde ne doit pas fausser les coûts
        raise ValueError(f"taux improbable : {taux}")
    return {"usd_pour_1_eur": taux, "date_taux": str(donnees["date"]), "source": "bce"}


def taux_du_jour() -> dict:
    """{usd_pour_1_eur, date_taux, source} avec source = "bce" ou "secours"."""
    url = settings.TAUX_CHANGE_URL
    if not url:
        return taux_de_secours()

    en_cache = cache.get(CLE_CACHE)
    if en_cache:
        return en_cache

    try:
        taux = _demander_a_frankfurter(url)
    except (URLError, OSError, ValueError, KeyError, TypeError) as erreur:
        # On note la panne dans les logs (visibles sur Render) et on continue.
        journal.warning("Taux de change indisponible (%s) : taux de secours utilisé.", erreur)
        taux = taux_de_secours()
        # On garde le secours 10 minutes seulement, pour réessayer bientôt.
        cache.set(CLE_CACHE, taux, 10 * 60)
        return taux

    cache.set(CLE_CACHE, taux, DUREE_CACHE)
    return taux
