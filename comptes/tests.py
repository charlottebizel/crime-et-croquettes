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


class ProfilEtPalierTests(TestCase):
    """Profil créé automatiquement (signal) et paliers créés par la migration."""

    def test_paliers_free_et_pro_existent(self):
        from .models import Palier

        noms = set(Palier.objects.values_list("nom", flat=True))
        self.assertEqual(noms, {"Free", "Pro"})
        free = Palier.objects.get(nom="Free")
        self.assertEqual(free.prix_mensuel_eur, 0)
        self.assertEqual(free.parties_par_mois, 3)
        self.assertEqual(free.questions_par_partie, 20)

    def test_nouvel_utilisateur_recoit_un_profil_free(self):
        utilisateur = User.objects.create_user("pistache", "p@example.com", "x")
        self.assertEqual(utilisateur.profil.palier.nom, "Free")
        self.assertEqual(utilisateur.profil.pseudo, "pistache")

    def test_inscription_cree_aussi_le_profil(self):
        self.client.post(
            reverse("comptes:inscription"),
            {
                "username": "mistigri",
                "email": "mistigri@example.com",
                "password1": "Croquette-Secrete-42",
                "password2": "Croquette-Secrete-42",
            },
        )
        self.assertEqual(User.objects.get(username="mistigri").profil.palier.nom, "Free")

    def test_palier_utilise_ne_peut_pas_etre_supprime(self):
        from django.db.models import ProtectedError

        from .models import Palier

        User.objects.create_user("felix", "f@example.com", "x")
        with self.assertRaises(ProtectedError):
            Palier.objects.get(nom="Free").delete()

    def test_supprimer_l_utilisateur_supprime_son_profil(self):
        from .models import Profil

        utilisateur = User.objects.create_user("duchesse", "d@example.com", "x")
        utilisateur.delete()
        self.assertFalse(Profil.objects.filter(pseudo="duchesse").exists())


@override_settings(STORAGES=STOCKAGE_TESTS)
class OeilMotDePasseTests(TestCase):
    """LB-006 : bouton « œil » à côté de chaque champ de mot de passe."""

    def test_connexion_a_un_bouton_oeil(self):
        reponse = self.client.get(reverse("comptes:connexion"))
        self.assertContains(reponse, 'class="champ-mdp__oeil"', count=1)
        self.assertContains(reponse, 'data-oeil="id_password"')

    def test_inscription_a_un_bouton_par_mot_de_passe(self):
        reponse = self.client.get(reverse("comptes:inscription"))
        self.assertContains(reponse, 'class="champ-mdp__oeil"', count=2)
        self.assertContains(reponse, 'data-oeil="id_password1"')
        self.assertContains(reponse, 'data-oeil="id_password2"')

    def test_bouton_sans_effet_sur_le_formulaire(self):
        """type="button" (n'envoie pas), sans name (pas lu par Django), caché sans JavaScript."""
        contenu = self.client.get(reverse("comptes:connexion")).content.decode()
        debut = contenu.index('<button type="button" class="champ-mdp__oeil"')
        bouton = contenu[debut : contenu.index(">", debut)]
        self.assertNotIn("name=", bouton)
        self.assertIn("hidden", bouton)
        self.assertIn('aria-pressed="false"', bouton)

    def test_script_charge_et_champs_ordinaires_sans_oeil(self):
        reponse = self.client.get(reverse("comptes:inscription"))
        self.assertContains(reponse, "js/oeil.js")
        self.assertNotContains(reponse, 'data-oeil="id_username"')
        self.assertNotContains(reponse, 'data-oeil="id_email"')
