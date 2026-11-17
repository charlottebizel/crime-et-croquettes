"""
comptes/forms.py — Formulaires d'inscription et de connexion.

On s'appuie sur les formulaires fournis par Django (UserCreationForm,
AuthenticationForm) : ils gèrent déjà la vérification des mots de passe,
leur hachage et les messages d'erreur en français. On ajoute seulement :
  - un champ e-mail obligatoire et unique à l'inscription ;
  - des libellés adaptés à l'univers du jeu ;
  - la classe CSS « champ » sur chaque champ (style de theme.css).
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


def _styliser(formulaire: forms.Form, autocompletes: dict[str, str]) -> None:
    """Ajoute la classe CSS du thème et l'attribut autocomplete à chaque champ.

    autocomplete aide les navigateurs et les gestionnaires de mots de passe
    à remplir correctement les champs (accessibilité et confort).
    """
    for nom, champ in formulaire.fields.items():
        champ.widget.attrs["class"] = "champ"
        if nom in autocompletes:
            champ.widget.attrs["autocomplete"] = autocompletes[nom]


class InscriptionForm(UserCreationForm):
    """Création d'un compte joueur : nom d'agent, e-mail, mot de passe ×2."""

    email = forms.EmailField(
        label="Adresse e-mail",
        help_text="Uniquement pour retrouver votre compte. Jamais partagée.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nom d'agent"
        self.fields["username"].help_text = "Lettres, chiffres et @ . + - _ (150 caractères max)."
        _styliser(
            self,
            {
                "username": "username",
                "email": "email",
                "password1": "new-password",
                "password2": "new-password",
            },
        )

    def clean_email(self) -> str:
        """Refuse une adresse déjà utilisée (comparaison sans tenir compte des majuscules)."""
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un agent utilise déjà cette adresse e-mail.")
        return email


class ConnexionForm(AuthenticationForm):
    """Connexion : même logique que Django, libellés du jeu et style du thème."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nom d'agent"
        self.fields["password"].label = "Mot de passe"
        _styliser(self, {"username": "username", "password": "current-password"})