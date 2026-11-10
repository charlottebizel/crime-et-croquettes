import pytest


@pytest.fixture(autouse=True)
def stockage_statique_simple(settings):
    """En test, pas de manifest WhiteNoise (il n'existe qu'après collectstatic)."""
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
