"""
comptes/views.py — Inscription, connexion et déconnexion des joueurs.

Exigence O3 (comptes et rôles) :
  - inscription      : crée un compte joueur et le connecte directement ;
  - connexion        : vue standard de Django (LoginView) ;
  - déconnexion      : en POST uniquement (sécurité : un simple lien ne
                       doit pas pouvoir déconnecter quelqu'un).

Le rôle administrateur n'est jamais donné à l'inscription : c'est
user.is_staff, attribué à la main (createsuperuser ou admin Django).
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import ConnexionForm, InscriptionForm


def inscription(request):
    """Affiche le formulaire d'inscription (GET) ou crée le compte (POST)."""
    # Un agent déjà connecté n'a rien à faire ici.
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.method == "POST":
        formulaire = InscriptionForm(request.POST)
        if formulaire.is_valid():
            utilisateur = formulaire.save()  # mot de passe haché par Django
            login(request, utilisateur)  # connexion immédiate après inscription
            messages.success(
                request,
                f"Bienvenue dans la brigade, agent {utilisateur.username} !",
            )
            return redirect(settings.LOGIN_REDIRECT_URL)
        # Formulaire invalide : on réaffiche la page avec les erreurs
        # et les valeurs déjà saisies (sauf les mots de passe).
    else:
        formulaire = InscriptionForm()

    return render(request, "comptes/inscription.html", {"form": formulaire})


class Connexion(LoginView):
    """Connexion d'un joueur (nom d'agent + mot de passe)."""

    template_name = "comptes/connexion.html"
    authentication_form = ConnexionForm
    redirect_authenticated_user = True  # déjà connecté → redirigé

    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, f"Content de vous revoir, agent {form.get_user().username}.")
        return reponse


class Deconnexion(LogoutView):
    """Déconnexion (POST uniquement, imposé par Django 5).

    La redirection après déconnexion est réglée par LOGOUT_REDIRECT_URL
    dans config/settings.py.
    """

    def post(self, request, *args, **kwargs):
        reponse = super().post(request, *args, **kwargs)
        messages.info(request, "Vous avez quitté le commissariat. À bientôt, agent.")
        return reponse