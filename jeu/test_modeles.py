"""
jeu/test_modeles.py — Tests des modèles du jeu et du journal AppelIA.

On vérifie surtout les règles que la base de données impose elle-même
(contraintes) et les choix de suppression (on_delete).
"""

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction

from ia.models import AppelIA
from jeu.fabriques import creer_enquete, lancer_partie
from jeu.models import (
    ALPHABET_CODE,
    CartePreuve,
    CaseFiche,
    Message,
    Participation,
    Partie,
    Suspect,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def joueur():
    return User.objects.create_user("moustache", "m@example.com", "x")


@pytest.fixture
def enquete():
    return creer_enquete()


def test_enquete_complete(enquete):
    assert enquete.suspects.count() == 5
    assert enquete.objets.count() == 5
    assert enquete.lieux.count() == 5
    assert enquete.cartes.count() == 6
    assert enquete.coupable.nom == "Gros Minou"
    assert not enquete.coupable.alibi_est_vrai


def test_numero_de_suspect_unique_par_enquete(enquete):
    with pytest.raises(IntegrityError), transaction.atomic():
        Suspect.objects.create(
            enquete=enquete, numero=1, nom="Doublon", role="x", personnalite="x",
            alibi="x", connaissances="x",
        )  # fmt: skip


def test_numero_de_suspect_entre_1_et_5(enquete):
    enquete.suspects.filter(numero=5).delete()
    with pytest.raises(IntegrityError), transaction.atomic():
        Suspect.objects.create(
            enquete=enquete, numero=6, nom="Sixième", role="x", personnalite="x",
            alibi="x", connaissances="x",
        )  # fmt: skip


def test_carte_doit_pointer_vers_un_element(enquete):
    with pytest.raises(IntegrityError), transaction.atomic():
        CartePreuve.objects.create(enquete=enquete, code="B1", titre="Vide", texte="x", ordre=9)


def test_case_fiche_un_seul_element(enquete, joueur):
    partie = lancer_partie(enquete, joueur)
    suspect = enquete.suspects.first()
    objet = enquete.objets.first()
    with pytest.raises(IntegrityError), transaction.atomic():
        CaseFiche.objects.create(partie=partie, joueur=joueur, suspect=suspect, objet=objet)
    with pytest.raises(IntegrityError), transaction.atomic():
        CaseFiche.objects.create(partie=partie, joueur=joueur)


def test_case_fiche_unique_par_element(enquete, joueur):
    partie = lancer_partie(enquete, joueur)
    suspect = enquete.suspects.first()
    CaseFiche.objects.create(partie=partie, joueur=joueur, suspect=suspect)
    with pytest.raises(IntegrityError), transaction.atomic():
        CaseFiche.objects.create(partie=partie, joueur=joueur, suspect=suspect)


def test_partie_recoit_un_code_invitation(enquete, joueur):
    partie = lancer_partie(enquete, joueur)
    assert len(partie.code_invitation) == 8
    assert set(partie.code_invitation) <= set(ALPHABET_CODE)
    assert partie.statut == Partie.Statut.EN_COURS
    assert partie.etats_suspects.count() == 5


def test_un_joueur_ne_participe_qu_une_fois(enquete, joueur):
    partie = lancer_partie(enquete, joueur)
    with pytest.raises(IntegrityError), transaction.atomic():
        Participation.objects.create(partie=partie, joueur=joueur)


def test_journal_ia_conserve_apres_suppression_du_compte(enquete, joueur):
    partie = lancer_partie(enquete, joueur)
    appel = AppelIA.objects.create(
        utilisateur=joueur, partie=partie, type=AppelIA.Type.INTERROGATOIRE, modele="faux"
    )
    joueur.delete()  # supprime aussi la partie qu'il hébergeait
    appel.refresh_from_db()
    assert appel.utilisateur is None
    assert appel.partie is None


def test_message_garde_si_l_auteur_supprime_son_compte(enquete, joueur):
    autre = User.objects.create_user("pistache", "p@example.com", "x")
    partie = lancer_partie(enquete, joueur)
    Participation.objects.create(partie=partie, joueur=autre)
    message = Message.objects.create(
        partie=partie, suspect=enquete.suspects.first(), auteur=autre, texte="Où étiez-vous ?"
    )
    autre.delete()
    message.refresh_from_db()
    assert message.auteur is None
