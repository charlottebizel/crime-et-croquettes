"""
jeu/tests.py — Tests de l'écran de partie de démonstration (ticket LB-001).

Lancement : pytest   (style pytest, comme pages/tests.py)
Aucun appel à l'IA : la démo utilise des données en dur (jeu/demo.py).
"""

import pytest
from django.urls import reverse

from jeu import demo

URL_DEMO = "jeu:partie_demo"


def test_demo_repond_sans_connexion(client):
    reponse = client.get(reverse(URL_DEMO))
    assert reponse.status_code == 200
    assert "Qui a volé le saumon du dimanche ?" in reponse.content.decode()


def test_cinq_suspects_affiches(client):
    contenu = client.get(reverse(URL_DEMO)).content.decode()
    for suspect in demo.SUSPECTS:
        assert f'id="suspect-{suspect["id"]}"' in contenu
        assert suspect["nom"] in contenu


def test_premier_suspect_par_defaut(client):
    reponse = client.get(reverse(URL_DEMO))
    assert reponse.context["suspect_courant"]["id"] == 1


@pytest.mark.parametrize("valeur", ["abc", "99", ""])
def test_suspect_invalide_retombe_sur_le_premier(client, valeur):
    reponse = client.get(reverse(URL_DEMO), {"suspect": valeur})
    assert reponse.status_code == 200
    assert reponse.context["suspect_courant"]["id"] == 1


def test_conversation_du_suspect_choisi_avec_mention_ia(client):
    reponse = client.get(reverse(URL_DEMO), {"suspect": 2})
    contenu = reponse.content.decode()
    assert reponse.context["suspect_courant"]["nom"] == "Gros Minou"
    assert "nouveau shampooing" in contenu
    # Chaque réponse du suspect porte la mention (exigence O7).
    nb_reponses = sum(1 for m in reponse.context["echanges"] if m["est_suspect"])
    assert contenu.count("Généré par IA") == nb_reponses


def test_suspect_jamais_interroge_affiche_l_etat_vide(client):
    contenu = client.get(reverse(URL_DEMO), {"suspect": 3}).content.decode()
    assert "Pas encore interrogé" in contenu


def test_contexte_respecte_la_spec(client):
    """Les clés de la spec §6.1 sont présentes ; la conversation s'appelle
    « echanges » (et pas « messages », réservé aux notifications Django)."""
    contexte = client.get(reverse(URL_DEMO)).context
    for cle in (
        "partie",
        "enquete",
        "suspects",
        "suspect_courant",
        "echanges",
        "cartes_tirees",
        "entrees_carnet",
        "fiche",
        "compteurs",
        "joueurs",
        "inspecteur",
    ):
        assert cle in contexte, cle


def test_aucune_solution_envoyee_au_navigateur():
    contexte = demo.contexte_partie(None)
    for cle in ("coupable", "objet_crime", "lieu_crime", "solution"):
        assert cle not in contexte
        assert cle not in contexte["enquete"]


def test_carnet_et_fiche_affiches(client):
    contenu = client.get(reverse(URL_DEMO)).content.decode()
    assert 'id="carnet"' in contenu
    assert "Pièce à conviction : toujours vraie" in contenu
    assert 'class="case case--barre"' in contenu
    assert 'class="case case--valide"' in contenu


def test_boutons_inactifs_en_demo(client):
    contenu = client.get(reverse(URL_DEMO)).content.decode()
    assert "Disponible quand le jeu sera branché" in contenu


@pytest.mark.parametrize(
    ("stress", "niveau"),
    [(0, "calme"), (34, "calme"), (35, "mal_a_l_aise"), (59, "mal_a_l_aise"), (60, "nerveux")],
)
def test_niveau_stress(stress, niveau):
    assert demo.niveau_stress(stress) == niveau
