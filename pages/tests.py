from django.urls import reverse


def test_accueil_repond(client):
    reponse = client.get(reverse("pages:accueil"))
    assert reponse.status_code == 200
    assert "Crimes et Croquette" in reponse.content.decode()
