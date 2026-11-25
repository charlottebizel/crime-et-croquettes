"""
gestion/tests.py — Tests du tableau de bord des coûts (LB-005, exigence O4).

Lancement : pytest. On crée des lignes AppelIA à la main : aucun appel à l'IA.
"""

import io
import json
import re
from datetime import timedelta
from decimal import Decimal
from urllib.error import URLError

import pytest
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone

from gestion import taux
from gestion.statistiques import tableau_de_bord
from ia.models import AppelIA

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def sans_api_de_change(settings):
    """Les tests n'appellent jamais Internet : pas d'URL → taux de secours."""
    settings.TAUX_CHANGE_URL = ""
    settings.TAUX_USD_POUR_1_EUR = Decimal("1.0968")
    settings.TAUX_DATE = "2026-11-18"
    cache.clear()


@pytest.fixture
def admin():
    return User.objects.create_user("chef", "c@exemple.invalid", "x", is_staff=True)


@pytest.fixture
def joueur():
    return User.objects.create_user("agent", "a@exemple.invalid", "x")


def appel(utilisateur, cout, *, type_=AppelIA.Type.INTERROGATOIRE, succes=True, il_y_a=0):
    a = AppelIA.objects.create(
        utilisateur=utilisateur,
        type=type_,
        modele="test/modele",
        jetons_entree=100,
        jetons_sortie=20,
        cout_usd=Decimal(cout),
        duree_ms=500,
        succes=succes,
        erreur_type="" if succes else AppelIA.Erreur.DELAI,
        erreur_detail="" if succes else "Timeout technique interne",
    )
    if il_y_a:
        # auto_now_add empêche de fixer la date à la création : on la change ensuite.
        AppelIA.objects.filter(pk=a.pk).update(cree_le=timezone.now() - timedelta(days=il_y_a))
    return a


# --- Accès ----------------------------------------------------------------------


def test_page_redirige_un_visiteur(client):
    reponse = client.get(reverse("gestion:couts"))
    assert reponse.status_code == 302
    assert reverse("comptes:connexion") in reponse["Location"]


def test_page_interdite_a_un_joueur(client, joueur):
    client.force_login(joueur)
    assert client.get(reverse("gestion:couts")).status_code == 403


def test_page_admin_monte_vue(client, admin):
    client.force_login(admin)
    contenu = client.get(reverse("gestion:couts")).content.decode()
    assert 'id="app-couts"' in contenu
    assert f'data-url-api="{reverse("api_gestion:couts")}"' in contenu
    assert "js/gestion/main.js" in contenu


def test_api_interdite_aux_non_admins(client, joueur):
    assert client.get(reverse("api_gestion:couts")).status_code == 401
    client.force_login(joueur)
    reponse = client.get(reverse("api_gestion:couts"))
    assert reponse.status_code == 403
    assert reponse.json()["erreur"]["type"] == "interdit"


def test_lien_du_menu_seulement_pour_les_admins(client, admin, joueur):
    client.force_login(joueur)
    assert "Coûts IA" not in client.get("/").content.decode()
    client.force_login(admin)
    assert "Coûts IA" in client.get("/").content.decode()


# --- Chiffres ---------------------------------------------------------------------


def test_totaux_et_moyennes(joueur):
    appel(joueur, "0.001")
    appel(joueur, "0.003")
    appel(joueur, "0.020", type_=AppelIA.Type.GENERATION)
    appel(joueur, "0.000", succes=False)
    t = tableau_de_bord(30)["totaux"]
    assert t["nb_appels"] == 4
    assert t["nb_echecs"] == 1
    assert t["taux_echec"] == 0.25
    assert t["cout_usd"] == pytest.approx(0.024)
    assert t["cout_moyen_question"] == pytest.approx(0.002)  # échec exclu de la moyenne
    assert t["cout_moyen_generation"] == pytest.approx(0.02)
    assert t["jetons_entree"] == 400


def test_par_jour_couvre_toute_la_periode(joueur):
    appel(joueur, "0.004", il_y_a=2)
    appel(joueur, "0.001")
    jours = tableau_de_bord(7)["par_jour"]
    assert len(jours) == 7  # jours sans appel inclus, à zéro
    assert jours[-1]["date"] == timezone.localdate().isoformat()
    assert jours[-1]["cout_usd"] == pytest.approx(0.001)
    assert jours[-3]["cout_usd"] == pytest.approx(0.004)
    assert sum(j["nb_appels"] for j in jours) == 2


def test_periode_filtre_les_vieux_appels(joueur):
    appel(joueur, "0.5", il_y_a=40)
    appel(joueur, "0.1")
    assert tableau_de_bord(30)["totaux"]["cout_usd"] == pytest.approx(0.1)
    assert tableau_de_bord(90)["totaux"]["cout_usd"] == pytest.approx(0.6)
    # Le budget depuis le début compte tout, quelle que soit la période.
    assert tableau_de_bord(7)["totaux"]["cout_depuis_le_debut"] == pytest.approx(0.6)


def test_periode_inconnue_retombe_sur_30_jours():
    assert tableau_de_bord(12)["periode"]["jours"] == 30


def test_par_utilisateur_et_compte_supprime(joueur):
    appel(joueur, "0.002")
    appel(None, "0.001")
    lignes = tableau_de_bord(30)["par_utilisateur"]
    assert lignes[0]["pseudo"] == "agent" and lignes[0]["palier"] == "Free"
    assert lignes[1]["pseudo"] == "Compte supprimé"


def test_derniers_appels_sans_detail_technique(client, admin, joueur):
    appel(joueur, "0.001", succes=False)
    client.force_login(admin)
    reponse = client.get(reverse("api_gestion:couts"), {"jours": 7})
    assert reponse.status_code == 200
    donnees = reponse.json()
    assert donnees["periode"]["jours"] == 7
    dernier = donnees["derniers_appels"][0]
    assert dernier["succes"] is False and dernier["erreur"] == "Délai dépassé"
    assert "Timeout technique interne" not in reponse.content.decode()


# --- Fichiers JavaScript ----------------------------------------------------------


def test_chaque_import_relatif_existe():
    a_visiter, vus = ["js/gestion/main.js"], set()
    while a_visiter:
        chemin = a_visiter.pop()
        if chemin in vus:
            continue
        vus.add(chemin)
        fichier = finders.find(chemin)
        assert fichier, f"fichier introuvable : {chemin}"
        with open(fichier, encoding="utf-8") as f:
            source = f.read()
        dossier = chemin.rsplit("/", 1)[0]
        for relatif in re.findall(r'from "(\.{1,2}/[^"]+)"', source):
            morceaux = dossier.split("/")
            for partie in relatif.split("/"):
                if partie == "..":
                    morceaux.pop()
                elif partie != ".":
                    morceaux.append(partie)
            a_visiter.append("/".join(morceaux))
    assert len(vus) >= 5


# --- Devise : taux de change (gestion/taux.py) -------------------------------------


class FausseReponse(io.BytesIO):
    """Imite la réponse de urlopen (utilisable avec « with »)."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_devise_sans_api_donne_le_taux_de_secours():
    devise = tableau_de_bord(30)["devise"]
    assert devise == {
        "usd_pour_1_eur": 1.0968,
        "date_taux": "2026-11-18",
        "source": "secours",
        "budget_eur": 1.0,
    }


def test_taux_du_jour_lu_dans_la_reponse_de_l_api(settings, monkeypatch):
    settings.TAUX_CHANGE_URL = "https://api.exemple.invalid/latest"
    appels = []

    def faux_urlopen(requete, timeout):
        appels.append(requete.full_url)
        corps = {"amount": 1.0, "base": "EUR", "date": "2026-11-24", "rates": {"USD": 1.1012}}
        return FausseReponse(json.dumps(corps).encode())

    monkeypatch.setattr(taux, "urlopen", faux_urlopen)
    assert taux.taux_du_jour() == {
        "usd_pour_1_eur": 1.1012,
        "date_taux": "2026-11-24",
        "source": "bce",
    }
    taux.taux_du_jour()  # deuxième lecture : vient du cache
    assert len(appels) == 1


@pytest.mark.parametrize(
    "probleme",
    [URLError("pas de réseau"), {"rates": {}}, {"date": "2026-11-24", "rates": {"USD": 42}}],
)
def test_api_en_panne_ou_reponse_bizarre_donne_le_secours(settings, monkeypatch, probleme):
    settings.TAUX_CHANGE_URL = "https://api.exemple.invalid/latest"

    def faux_urlopen(requete, timeout):
        if isinstance(probleme, Exception):
            raise probleme
        return FausseReponse(json.dumps(probleme).encode())

    monkeypatch.setattr(taux, "urlopen", faux_urlopen)
    assert taux.taux_du_jour()["source"] == "secours"
