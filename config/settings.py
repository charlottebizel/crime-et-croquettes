"""
Réglages Django de Crimes et Croquette.

Toutes les valeurs sensibles ou qui changent entre le local et la production
sont lues dans les variables d'environnement (fichier `.env` en local,
variables Render en production). Voir `.env.example` et CLAUDE.md.
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Charge le fichier .env s'il existe (en local). En production, Render
# fournit directement les variables d'environnement.
load_dotenv(BASE_DIR / ".env")


def env_bool(nom: str, defaut: bool = False) -> bool:
    return os.environ.get(nom, str(defaut)).strip().lower() in {"1", "true", "yes", "on"}


def env_liste(nom: str, defaut: str = "") -> list[str]:
    return [v.strip() for v in os.environ.get(nom, defaut).split(",") if v.strip()]


# --- Sécurité -----------------------------------------------------------

DEBUG = env_bool("DEBUG", False)

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        # Clé de secours uniquement pour le développement local.
        SECRET_KEY = "dev-uniquement-ne-pas-utiliser-en-production"
    else:
        raise RuntimeError("La variable d'environnement SECRET_KEY est obligatoire.")

ALLOWED_HOSTS = env_liste("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_liste("CSRF_TRUSTED_ORIGINS")

# Render termine le HTTPS devant l'application.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "3600"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True


# --- Applications -------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Nos apps
    "comptes",
    "jeu",
    "ia",
    "gestion",
    "pages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --- Base de données ----------------------------------------------------
# DATABASE_URL (Neon) si elle est définie, sinon un fichier SQLite local.

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# --- Authentification ---------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Où envoyer un visiteur non connecté qui demande une page protégée
# (@login_required), et où aller après connexion / déconnexion.
# LOGIN_REDIRECT_URL passera à "jeu:liste" quand la page « Mes parties » existera.
LOGIN_URL = "comptes:connexion"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# --- Langue et fuseau horaire -------------------------------------------

LANGUAGE_CODE = "fr-be"
TIME_ZONE = "Europe/Brussels"
USE_I18N = True
USE_TZ = True


# --- Fichiers statiques (WhiteNoise) ------------------------------------

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- IA (OpenRouter) ----------------------------------------------------
# La clé n'est jamais dans le dépôt. Par défaut on utilise le faux fournisseur
# pour ne pas consommer le budget (1 € pour tout le projet).

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
IA_FOURNISSEUR = os.environ.get("IA_FOURNISSEUR", "faux")
IA_MODELE_GENERATION = os.environ.get("IA_MODELE_GENERATION", "")
IA_MODELE_INTERROGATOIRE = os.environ.get("IA_MODELE_INTERROGATOIRE", "")
IA_DELAI_SECONDES = int(os.environ.get("IA_DELAI_SECONDES", "20"))