"""
jeu/tests.py — Tests de l'écran de partie (Vue) et de l'API JSON de démo.

Lancement : pytest
Aucun appel à l'IA : la démo utilise des données en dur (jeu/demo.py).
Le rendu et les clics de l'application Vue se vérifient dans le navigateur ;
ici on teste ce que le serveur fournit à Vue.
"""

import json
import re

import pytest
from django.contrib.staticfiles import finders
from django.urls import reverse

from jeu import demo

PAGE_DEMO = "jeu:partie_demo"
API_DEMO = "api_jeu:partie_demo"
API_SUSPECT = "api_jeu:interrogatoire_demo"

# --- La page (coquille de l'application Vue) --------------------------------


def test_page_demo_repond_sans_connexion(client):
    reponse = client.get(reverse(PAGE_DEMO))
    assert reponse.status_code == 200
    contenu = reponse.content.decode()
    assert demo.TITRE in contenu  # dans le <title>


def test_page_fournit_le_point_de_montage_vue(client):
    contenu = client.get(reverse(PAGE_DEMO)).content.decode()
    assert 'id="app-partie"' in contenu
    assert f'data-url-api="{reverse(API_DEMO)}"' in contenu
    assert 'data-mode-demo="oui"' in contenu
    assert '<script type="importmap">' in contenu
    assert "vendor/vue/vue.esm-browser.prod.js" in contenu
    assert 'type="module"' in contenu and "js/jeu/main.js" in contenu


def test_page_pose_le_cookie_csrf(client):
    """Vue renvoie ce cookie dans X-CSRFToken pour ses requêtes POST."""
    reponse = client.get(reverse(PAGE_DEMO))
    assert "csrftoken" in reponse.cookies


def test_plus_de_htmx(client):
    contenu = client.get(reverse(PAGE_DEMO)).content.decode()
    assert "htmx" not in contenu.lower()


# --- Les fichiers JavaScript ------------------------------------------------


def test_vue_est_copie_dans_static():
    assert finders.find("vendor/vue/vue.esm-browser.prod.js")
    assert finders.find("vendor/vue/LICENSE.txt")


def test_chaque_import_relatif_existe():
    """Une faute de frappe dans un import casse tout l'écran sans erreur serveur :
    on suit les imports depuis main.js et on vérifie que chaque fichier existe."""
    a_visiter, vus = ["js/jeu/main.js"], set()
    while a_visiter:
        chemin = a_visiter.pop()
        if chemin in vus:
            continue
        vus.add(chemin)
        fichier = finders.find(chemin)
        assert fichier, f"fichier introuvable : {chemin}"
        with open(fichier, encoding="utf-8") as f:
            source = f.read()
        dossier = chemin.rsplit("/", 1)[0]
        for relatif in re.findall(r'from "(\.{1,2}/[^"]+)"', source):
            morceaux = dossier.split("/")
            for partie in relatif.split("/"):
                if partie == "..":
                    morceaux.pop()
                elif partie != ".":
                    morceaux.append(partie)
            a_visiter.append("/".join(morceaux))
    assert len(vus) >= 10  # main, api, outils et les composants


# --- L'API JSON -------------------------------------------------------------


def test_api_partie_demo(client):
    reponse = client.get(reverse(API_DEMO))
    assert reponse.status_code == 200
    assert reponse["Content-Type"] == "application/json"
    donnees = reponse.json()
    for cle in (
        "partie",
        "enquete",
        "suspects",
        "cartes_tirees",
        "entrees_carnet",
        "fiche",
        "compteurs",
        "joueurs",
        "inspecteur",
        "mode_demo",
    ):
        assert cle in donnees, cle
    assert len(donnees["suspects"]) == 5
    assert {"id", "nom", "apparence", "stress", "stress_niveau", "interroge"} <= set(
        donnees["suspects"][0]
    )


def test_api_suspect_avec_conversation(client):
    reponse = client.get(reverse(API_SUSPECT, args=[2]))
    assert reponse.status_code == 200
    donnees = reponse.json()
    assert donnees["suspect"]["nom"] == "Gros Minou"
    assert any(m["est_suspect"] for m in donnees["echanges"])
    assert any("shampooing" in m["texte"] for m in donnees["echanges"])


def test_api_suspect_jamais_interroge(client):
    donnees = client.get(reverse(API_SUSPECT, args=[3])).json()
    assert donnees["echanges"] == []
    assert donnees["suspect"]["interroge"] is False


def test_api_suspect_inconnu_renvoie_une_erreur_lisible(client):
    reponse = client.get(reverse(API_SUSPECT, args=[99]))
    assert reponse.status_code == 404
    erreur = reponse.json()["erreur"]
    assert erreur["type"] == "introuvable"
    assert erreur["message"]


def test_api_refuse_les_ecritures(client):
    assert client.post(reverse(API_DEMO)).status_code == 405


def test_aucune_solution_envoyee_au_navigateur(client):
    """Ni la partie ni les interrogatoires ne contiennent la solution."""
    textes = [client.get(reverse(API_DEMO)).content.decode()]
    for suspect in demo.SUSPECTS:
        textes.append(client.get(reverse(API_SUSPECT, args=[suspect["id"]])).content.decode())
    for texte in textes:
        cles = set(re.findall(r'"(\w+)":', texte))
        assert not cles & {"coupable", "objet_crime", "lieu_crime", "solution", "secret", "alibi"}


def test_api_en_json_valide_et_accents_preserves(client):
    brut = client.get(reverse(API_DEMO)).content.decode()
    assert json.loads(brut)["enquete"]["titre"] == demo.TITRE


@pytest.mark.parametrize(
    ("stress", "niveau"),
    [(0, "calme"), (34, "calme"), (35, "mal_a_l_aise"), (59, "mal_a_l_aise"), (60, "nerveux")],
)
def test_niveau_stress(stress, niveau):
    assert demo.niveau_stress(stress) == niveau
