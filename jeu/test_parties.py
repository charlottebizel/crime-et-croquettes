"""
jeu/test_parties.py — Tests de charger_demo (LB-003) et des vraies parties en lecture (LB-004).

Lancement : pytest. Aucun appel à l'IA.
"""

import json

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse

from jeu.models import CaseFiche, Enquete, EntreeCarnet, Message, Partie

pytestmark = pytest.mark.django_db


@pytest.fixture
def partie_demo(monkeypatch):
    monkeypatch.setenv("DEMO_MOT_DE_PASSE", "Croquette-Demo-42")
    call_command("charger_demo")
    return Partie.objects.get(code_invitation="SAUMON42")


@pytest.fixture
def moustache(partie_demo):
    return User.objects.get(username="moustache")


# --- LB-003 : charger_demo ----------------------------------------------------


def test_charger_demo_cree_tout(partie_demo):
    enquete = partie_demo.enquete
    assert enquete.suspects.count() == 5
    assert enquete.objets.count() == 5
    assert enquete.lieux.count() == 5
    assert enquete.cartes.count() == 6
    assert enquete.coupable.nom == "Gros Minou"
    assert enquete.objet_crime.nom == "Boîte en carton"
    assert enquete.lieu_crime.nom == "Cuisine"
    # Chaque élément de la solution est prouvé par au moins une carte (spec §7.3).
    assert enquete.cartes.filter(suspect=enquete.coupable).exists()
    assert enquete.cartes.filter(objet=enquete.objet_crime).exists()
    assert enquete.cartes.filter(lieu=enquete.lieu_crime).exists()
    assert partie_demo.participations.count() == 2
    assert partie_demo.cartes_tirees.count() == 2
    assert EntreeCarnet.objects.filter(partie=partie_demo).count() == 5
    assert (
        partie_demo.questions_posees
        == Message.objects.filter(partie=partie_demo, est_suspect=False).count()
    )
    # 15 cases par joueur.
    for joueur in ("moustache", "joueur"):
        assert CaseFiche.objects.filter(partie=partie_demo, joueur__username=joueur).count() == 15


def test_charger_demo_comptes_et_paliers(partie_demo):
    assert User.objects.get(username="admin").is_staff
    assert User.objects.get(username="moustache").profil.palier.nom == "Pro"
    assert User.objects.get(username="joueur").profil.palier.nom == "Free"
    assert User.objects.get(username="joueur").check_password("Croquette-Demo-42")


def test_charger_demo_est_idempotent(partie_demo):
    call_command("charger_demo")
    assert Enquete.objects.filter(titre=partie_demo.enquete.titre).count() == 1
    assert User.objects.filter(username="moustache").count() == 1


def test_charger_demo_reinitialiser(partie_demo):
    ancien = partie_demo.pk
    call_command("charger_demo", reinitialiser=True)
    assert not Partie.objects.filter(pk=ancien).exists()
    assert Partie.objects.filter(code_invitation="SAUMON42").count() == 1


# --- LB-004 : pages -------------------------------------------------------------


def test_mes_parties_exige_la_connexion(client):
    reponse = client.get(reverse("jeu:liste"))
    assert reponse.status_code == 302
    assert reverse("comptes:connexion") in reponse["Location"]


def test_mes_parties_liste_la_partie(client, moustache, partie_demo):
    client.force_login(moustache)
    contenu = client.get(reverse("jeu:liste")).content.decode()
    assert "Qui a volé le saumon du dimanche ?" in contenu
    assert reverse("jeu:partie", args=[partie_demo.pk]) in contenu


def test_mes_parties_vide(client, db):
    client.force_login(User.objects.create_user("nouveau", "n@exemple.invalid", "x"))
    assert "Aucun dossier" in client.get(reverse("jeu:liste")).content.decode()


def test_page_partie_monte_vue_sur_l_api_reelle(client, moustache, partie_demo):
    client.force_login(moustache)
    contenu = client.get(reverse("jeu:partie", args=[partie_demo.pk])).content.decode()
    assert f'data-url-api="{reverse("api_jeu:partie", args=[partie_demo.pk])}"' in contenu
    assert 'data-mode-demo="non"' in contenu


def test_page_partie_d_un_autre_joueur_404(client, partie_demo):
    client.force_login(User.objects.create_user("intrus", "i@exemple.invalid", "x"))
    assert client.get(reverse("jeu:partie", args=[partie_demo.pk])).status_code == 404


# --- LB-004 : API --------------------------------------------------------------


def test_api_partie(client, moustache, partie_demo):
    client.force_login(moustache)
    donnees = client.get(reverse("api_jeu:partie", args=[partie_demo.pk])).json()
    assert donnees["mode_demo"] is False
    assert [s["nom"] for s in donnees["suspects"]][:2] == ["Duchesse", "Gros Minou"]
    assert donnees["compteurs"]["questions_max"] == 40  # palier Pro de l'hôte
    assert len(donnees["cartes_tirees"]) == 2
    assert donnees["cartes_tirees"][0]["etiquette"] == "Lieu · Cuisine"
    assert len(donnees["entrees_carnet"]) == 5
    assert donnees["entrees_carnet"][-1]["type"] == "preuve"  # la plus ancienne en dernier
    avis = {e["texte"]: e["avis"] for e in donnees["entrees_carnet"]}
    assert "douteux" in avis.values()
    etats = [c["etat"] for g in donnees["fiche"] for c in g["cases"]]
    assert len(etats) == 15 and "barre" in etats and "valide" in etats
    assert donnees["joueurs"] == ["Moustache", "Joueur"]


def test_api_fiche_et_avis_sont_personnels(client, partie_demo):
    client.force_login(User.objects.get(username="joueur"))
    donnees = client.get(reverse("api_jeu:partie", args=[partie_demo.pk])).json()
    assert {c["etat"] for g in donnees["fiche"] for c in g["cases"]} == {"inconnu"}
    assert all(e["avis"] is None for e in donnees["entrees_carnet"])


def test_api_interrogatoire(client, moustache, partie_demo):
    client.force_login(moustache)
    minou = partie_demo.enquete.suspects.get(nom="Gros Minou")
    donnees = client.get(reverse("api_jeu:interrogatoire", args=[partie_demo.pk, minou.pk])).json()
    assert donnees["suspect"]["stress"] == 72
    assert donnees["suspect"]["interroge"] is True
    assert donnees["echanges"][0]["auteur"] == "Moustache"
    assert any(m["a_ajoute_au_carnet"] for m in donnees["echanges"])


def test_api_suspect_d_une_autre_enquete_404(client, moustache, partie_demo):
    from jeu.fabriques import creer_enquete

    autre = creer_enquete().suspects.first()
    client.force_login(moustache)
    reponse = client.get(reverse("api_jeu:interrogatoire", args=[partie_demo.pk, autre.pk]))
    assert reponse.status_code == 404
    assert reponse.json()["erreur"]["type"] == "introuvable"


def test_api_non_connecte_401(client, partie_demo):
    reponse = client.get(reverse("api_jeu:partie", args=[partie_demo.pk]))
    assert reponse.status_code == 401
    assert reponse.json()["erreur"]["type"] == "connexion"


def test_api_partie_d_un_autre_joueur_404(client, partie_demo):
    client.force_login(User.objects.create_user("intrus", "i@exemple.invalid", "x"))
    assert client.get(reverse("api_jeu:partie", args=[partie_demo.pk])).status_code == 404


def test_api_ne_revele_jamais_la_solution_ni_les_secrets(client, moustache, partie_demo):
    """Ni la solution, ni l'alibi, ni les connaissances, ni le secret d'un suspect."""
    client.force_login(moustache)
    textes = [client.get(reverse("api_jeu:partie", args=[partie_demo.pk])).content.decode()]
    for suspect in partie_demo.enquete.suspects.all():
        url = reverse("api_jeu:interrogatoire", args=[partie_demo.pk, suspect.pk])
        textes.append(client.get(url).content.decode())
    secrets_serveur = []
    for suspect in partie_demo.enquete.suspects.all():
        secrets_serveur += [suspect.secret, suspect.connaissances, suspect.personnalite]
    for texte in textes:
        donnees = json.dumps(json.loads(texte), ensure_ascii=False)
        assert '"coupable"' not in donnees and '"secret"' not in donnees
        for secret in secrets_serveur:
            assert secret not in donnees
