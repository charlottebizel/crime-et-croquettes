from django.urls import reverse


def test_accueil_repond(client):
    reponse = client.get(reverse("pages:accueil"))
    assert reponse.status_code == 200
    assert "Crimes et Croquette" in reponse.content.decode()


def test_accueil_propose_la_demo(client):
    """Le bouton de l'accueil mène à l'écran de partie de démonstration."""
    contenu = client.get(reverse("pages:accueil")).content.decode()
    assert f'href="{reverse("jeu:partie_demo")}"' in contenu
    assert "Lancer l'enquête de démo" in contenu
