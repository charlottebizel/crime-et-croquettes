"""
ia/tests.py — Tests des fournisseurs et du service d'appel IA.

AUCUN appel réel : le faux fournisseur est utilisé partout, et le client
OpenRouter est remplacé par un objet simulé (aucune requête réseau).
"""

import json
from decimal import Decimal
from types import SimpleNamespace
from unittest import mock

import openai
import pytest
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command

from ia.erreurs import ErreurFournisseur, ReponseInvalide
from ia.fournisseurs import obtenir_fournisseur
from ia.fournisseurs.faux import FauxFournisseur
from ia.models import AppelIA
from ia.services import appeler

MESSAGES = [{"role": "user", "content": "Où étais-tu ?"}]


def appel_test(**kwargs):
    parametres = {
        "type_appel": AppelIA.Type.INTERROGATOIRE,
        "modele": "openai/gpt-6-luna",
        "messages": MESSAGES,
        "nom_schema": "interrogatoire",
        "schema": {},
    }
    parametres.update(kwargs)
    return appeler(**parametres)


# --- Choix du fournisseur ------------------------------------------------------


def test_fournisseur_faux_par_defaut(settings):
    settings.IA_FOURNISSEUR = "faux"
    assert isinstance(obtenir_fournisseur(), FauxFournisseur)


def test_fournisseur_inconnu_refuse(settings):
    settings.IA_FOURNISSEUR = "chatgpt"
    with pytest.raises(ImproperlyConfigured):
        obtenir_fournisseur()


def test_openrouter_sans_cle_refuse(settings):
    settings.IA_FOURNISSEUR = "openrouter"
    settings.OPENROUTER_API_KEY = ""
    with pytest.raises(ErreurFournisseur):
        obtenir_fournisseur()


# --- Service appeler() : journal AppelIA ----------------------------------------


@pytest.mark.django_db
def test_appel_reussi_journalise():
    donnees, journal = appel_test(fournisseur=FauxFournisseur())
    assert "reponse" in donnees
    assert journal.pk is not None
    assert journal.succes is True
    assert journal.erreur_type == ""
    assert journal.cout_usd == 0
    assert journal.jetons_entree > 0
    assert journal.modele.startswith("faux/")


@pytest.mark.django_db
def test_json_illisible_journalise_comme_invalide():
    with pytest.raises(ReponseInvalide):
        appel_test(fournisseur=FauxFournisseur(invalide=True))
    journal = AppelIA.objects.get()
    assert journal.succes is False
    assert journal.erreur_type == "invalide"
    assert "JSON illisible" in journal.erreur_detail


@pytest.mark.django_db
def test_validation_refusee_journalisee():
    def refuser(_donnees):
        raise ReponseInvalide("stress manquant")

    with pytest.raises(ReponseInvalide):
        appel_test(fournisseur=FauxFournisseur(), valider=refuser)
    journal = AppelIA.objects.get()
    assert journal.succes is False
    assert journal.erreur_detail == "stress manquant"


@pytest.mark.django_db
def test_validation_peut_nettoyer_les_donnees():
    _, journal = appel_test(fournisseur=FauxFournisseur(), valider=lambda d: {"ok": True})
    assert journal.succes is True


@pytest.mark.django_db
def test_echec_du_fournisseur_journalise():
    class FournisseurEnPanne:
        def completer(self, *args):
            raise ErreurFournisseur("APIConnectionError: réseau coupé")

    with pytest.raises(ErreurFournisseur):
        appel_test(fournisseur=FournisseurEnPanne())
    journal = AppelIA.objects.get()
    assert journal.succes is False
    assert "réseau coupé" in journal.erreur_detail


# --- OpenRouter, avec un client simulé ------------------------------------------


@pytest.fixture
def openrouter(settings):
    settings.OPENROUTER_API_KEY = "cle-de-test"
    from ia.fournisseurs.openrouter import FournisseurOpenRouter

    fournisseur = FournisseurOpenRouter()
    fournisseur.client = mock.Mock()
    return fournisseur


def test_openrouter_envoie_les_bonnes_options(openrouter):
    openrouter.client.chat.completions.create.return_value = SimpleNamespace(
        model="openai/gpt-6-luna",
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"reponse": "Miaou"}'))],
        usage=SimpleNamespace(prompt_tokens=120, completion_tokens=30, cost=0.000027),
    )
    reponse = openrouter.completer("openai/gpt-6-luna", MESSAGES, "interrogatoire", {"a": 1})

    options = openrouter.client.chat.completions.create.call_args.kwargs
    assert options["response_format"]["json_schema"]["strict"] is True
    assert options["extra_body"]["provider"]["data_collection"] == "deny"
    assert options["extra_body"]["provider"]["zdr"] is True
    assert json.loads(reponse.contenu) == {"reponse": "Miaou"}
    assert reponse.jetons_entree == 120
    assert reponse.jetons_sortie == 30
    assert reponse.cout_usd == Decimal("0.000027")


def test_openrouter_transforme_les_erreurs_du_sdk(openrouter):
    openrouter.client.chat.completions.create.side_effect = openai.APITimeoutError(
        request=mock.Mock()
    )
    with pytest.raises(ErreurFournisseur) as erreur:
        openrouter.completer("m", MESSAGES, "interrogatoire", {})
    assert "APITimeoutError" in erreur.value.detail


# --- Commande essai_ia -----------------------------------------------------------


@pytest.mark.django_db
def test_commande_essai_ia_avec_le_faux(settings, capsys):
    settings.IA_FOURNISSEUR = "faux"
    call_command("essai_ia")
    assert "Réponse :" in capsys.readouterr().out
    assert AppelIA.objects.filter(succes=True).count() == 1
