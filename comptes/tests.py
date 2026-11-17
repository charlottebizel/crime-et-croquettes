"""
comptes/tests.py — Tests de l'inscription, de la connexion et de la déconnexion.

Lancement : pytest   (ou python manage.py test comptes)
Aucun appel à l'IA ici : rien ne coûte.
"""

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

# En production, WhiteNoise exige un « manifeste » créé par collectstatic.
# Pendant les tests, on ne lance pas collectstatic : on utilise donc le
# stockage simple de Django, sinon toute page qui charge theme.css plante.
STOCKAGE_TESTS = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


@override_settings(STORAGES=STOCKAGE_TESTS)
class InscriptionTests(TestCase):
    def donnees(self, **modifs):
        donnees = {
            "username": "moustache",
            "email": "moustache@example.com",
            "password1": "Croquette-Secrete-42",
            "password2": "Croquette-Secrete-42",
        }
        donnees.update(modifs)
        return donnees

    def test_page_inscription_s_affiche(self):
        reponse = self.client.get(reverse("comptes:inscription"))
        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, "Rejoindre la brigade")

    def test_inscription_cree_le_compte_et_connecte(self):
        reponse = self.client.post(reverse("comptes:inscription"), self.donnees())
        self.assertRedirects(reponse, "/", fetch_redirect_response=False)
        utilisateur = User.objects.get(username="moustache")
        self.assertEqual(utilisateur.email, "moustache@example.com")
        self.assertFalse(utilisateur.is_staff)  # jamais admin par l'inscription
        self.assertEqual(int(self.client.session["_auth_user_id"]), utilisateur.pk)

    def test_mots_de_passe_differents_refuses(self):
        reponse = self.client.post(
            reverse("comptes:inscription"), self.donnees(password2="autre-chose-99")
        )
        self.assertEqual(reponse.status_code, 200)  # on reste sur le formulaire
        self.assertFalse(User.objects.filter(username="moustache").exists())

    def test_email_deja_utilise_refuse(self):
        User.objects.create_user("duchesse", "moustache@example.com", "x")
        reponse = self.client.post(
            reverse("comptes:inscription"), self.donnees(email="MOUSTACHE@example.com")
        )
        self.assertContains(reponse, "Un agent utilise déjà cette adresse e-mail.")

    def test_agent_connecte_redirige(self):
        User.objects.create_user("moustache", "m@example.com", "Croquette-Secrete-42")
        self.client.login(username="moustache", password="Croquette-Secrete-42")
        reponse = self.client.get(reverse("comptes:inscription"))
        self.assertRedirects(reponse, "/", fetch_redirect_response=False)


@override_settings(STORAGES=STOCKAGE_TESTS)
class ConnexionTests(TestCase):
    def setUp(self):
        User.objects.create_user("moustache", "m@example.com", "Croquette-Secrete-42")

    def test_connexion_reussie(self):
        reponse = self.client.post(
            reverse("comptes:connexion"),
            {"username": "moustache", "password": "Croquette-Secrete-42"},
        )
        self.assertRedirects(reponse, "/", fetch_redirect_response=False)
        self.assertIn("_auth_user_id", self.client.session)

    def test_mauvais_mot_de_passe(self):
        reponse = self.client.post(
            reverse("comptes:connexion"),
            {"username": "moustache", "password": "faux"},
        )
        self.assertEqual(reponse.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_deconnexion_en_post(self):
        self.client.login(username="moustache", password="Croquette-Secrete-42")
        reponse = self.client.post(reverse("comptes:deconnexion"))
        self.assertRedirects(reponse, "/", fetch_redirect_response=False)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_deconnexion_en_get_refusee(self):
        # Un simple lien ne doit pas pouvoir déconnecter quelqu'un.
        reponse = self.client.get(reverse("comptes:deconnexion"))
        self.assertEqual(reponse.status_code, 405)