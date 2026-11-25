"""
jeu/demo.py — Données en dur de l'enquête de démonstration.

Enquête : « Qui a volé le saumon du dimanche ? ». Aucune base de données,
aucun appel à l'IA.

Utilisé par l'API JSON de démo (jeu/api.py), elle-même lue par l'écran de
partie en Vue (static/js/jeu/). Les clés renvoyées sont EXACTEMENT celles de
docs/specification.md §6 : les vraies vues de l'API (Charlotte) renverront
les mêmes, et le frontend Vue ne changera pas.

La solution de l'enquête n'est volontairement pas présente : elle ne doit
jamais atteindre le navigateur.
"""

TITRE = "Qui a volé le saumon du dimanche ?"

# --- Apparence des chats (spec §3.2) --------------------------------------
# Lue par le composant Vue ChatPortrait (static/js/jeu/composants/) pour dessiner
# chaque portrait, et par templates/composants/chat.html côté Django.

INSPECTEUR = {
    "pelage": "#D9A066",
    "rayures": "#9C6A33",
    "rayures_opacite": 1,
    "yeux": "#7CC4A6",
    "museau": "#FBE9D0",
    "accessoire": "inspecteur",
}

SUSPECTS = [
    {
        "id": 1,
        "numero": 1,
        "nom": "Duchesse",
        "role": "La persane snob",
        "apparence": {
            "pelage": "#F7F4EF",
            "rayures": "#F7F4EF",
            "rayures_opacite": 0,
            "yeux": "#5BA3D9",
            "museau": "#FFFFFF",
            "accessoire": "couronne",
        },
        "stress": 24,
    },
    {
        "id": 2,
        "numero": 2,
        "nom": "Gros Minou",
        "role": "Le roux gourmand",
        "apparence": {
            "pelage": "#F0A04B",
            "rayures": "#C7741F",
            "rayures_opacite": 1,
            "yeux": "#9BC53D",
            "museau": "#FBE3C4",
            "accessoire": "serviette",
        },
        "stress": 72,
    },
    {
        "id": 3,
        "numero": 3,
        "nom": "Pistache",
        "role": "Le chaton turbulent",
        "apparence": {
            "pelage": "#B3AEA8",
            "rayures": "#6E6862",
            "rayures_opacite": 1,
            "yeux": "#F2C14E",
            "museau": "#EDE9E4",
            "accessoire": "pelote",
        },
        "stress": 41,
    },
    {
        "id": 4,
        "numero": 4,
        "nom": "Monsieur Félix",
        "role": "Le vieux matou",
        "apparence": {
            "pelage": "#34302E",
            "rayures": "#34302E",
            "rayures_opacite": 0,
            "yeux": "#E8B93B",
            "museau": "#F4F1EC",
            "accessoire": "monocle",
        },
        "stress": 12,
    },
    {
        "id": 5,
        "numero": 5,
        "nom": "Mistigri",
        "role": "La chatte de gouttière",
        "apparence": {
            "pelage": "#C98B4B",
            "rayures": "#34302E",
            "rayures_opacite": 0.9,
            "yeux": "#7CC4A6",
            "museau": "#F4F1EC",
            "accessoire": "bandana",
        },
        "stress": 33,
    },
]

# --- Conversations déjà jouées, par id de suspect (spec §6.3) --------------
# auteur = pseudo du joueur pour une question, None pour une réponse du suspect.

CONVERSATIONS = {
    1: [
        {
            "est_suspect": False,
            "texte": "Que faisiez-vous pendant la sieste de midi ?",
            "stress_avant": None,
            "stress_apres": None,
            "a_ajoute_au_carnet": False,
            "auteur": "Inspecteur Moustache",
        },
        {
            "est_suspect": True,
            "texte": "Je me faisais brosser, évidemment. Une duchesse ne traîne pas "
            "près des cuisines, inspecteur.",
            "stress_avant": 20,
            "stress_apres": 24,
            "a_ajoute_au_carnet": False,
            "auteur": None,
        },
    ],
    2: [
        {
            "est_suspect": False,
            "texte": "Où étiez-vous pendant la sieste de midi ?",
            "stress_avant": None,
            "stress_apres": None,
            "a_ajoute_au_carnet": False,
            "auteur": "Inspecteur Moustache",
        },
        {
            "est_suspect": True,
            "texte": "Dans mon panier, évidemment. Je dors seize heures par jour, "
            "inspecteur. C'est un travail à plein temps.",
            "stress_avant": 30,
            "stress_apres": 34,
            "a_ajoute_au_carnet": True,
            "auteur": None,
        },
        {
            "est_suspect": False,
            "texte": "Avez-vous vu quelqu'un près de la cuisine ?",
            "stress_avant": None,
            "stress_apres": None,
            "a_ajoute_au_carnet": False,
            "auteur": "Inspecteur Moustache",
        },
        {
            "est_suspect": True,
            "texte": "Pistache. Ce chaton saute partout. Il avait de la laine "
            "accrochée aux moustaches, si vous voulez mon avis.",
            "stress_avant": 34,
            "stress_apres": 45,
            "a_ajoute_au_carnet": True,
            "auteur": None,
        },
        {
            "est_suspect": False,
            "texte": "Pourquoi sentez-vous le saumon ?",
            "stress_avant": None,
            "stress_apres": None,
            "a_ajoute_au_carnet": False,
            "auteur": "Inspecteur Moustache",
        },
        {
            "est_suspect": True,
            "texte": "Le… saumon ? C'est mon nouveau shampooing. Ronron. Vous devriez "
            "plutôt interroger Duchesse, elle n'aime pas partager.",
            "stress_avant": 45,
            "stress_apres": 72,
            "a_ajoute_au_carnet": False,
            "auteur": None,
        },
    ],
    4: [
        {
            "est_suspect": False,
            "texte": "Où étiez-vous pendant la sieste de midi ?",
            "stress_avant": None,
            "stress_apres": None,
            "a_ajoute_au_carnet": False,
            "auteur": "Inspecteur Moustache",
        },
        {
            "est_suspect": True,
            "texte": "Sur le rebord de la fenêtre, avec Mistigri. Nous observions les "
            "mésanges. Je n'ai pas bougé une moustache, inspecteur.",
            "stress_avant": 10,
            "stress_apres": 12,
            "a_ajoute_au_carnet": True,
            "auteur": None,
        },
    ],
}

# --- Pièces à conviction déjà tirées (spec §6.1, CartePreuve) --------------

CARTES_TIREES = [
    {
        "code": "A1",
        "titre": "Poils roux",
        "texte": "Des poils roux sur le comptoir, juste à côté de l'assiette vide.",
        "etiquette": "Lieu · Cuisine",
    },
    {
        "code": "A2",
        "titre": "Pelote déroulée",
        "texte": "Une pelote de laine déroulée jusque sous le canapé.",
        "etiquette": "Objet · Pelote de laine",
    },
]

# --- Carnet d'indices, le plus récent d'abord (spec §6.4) ------------------

ENTREES_CARNET = [
    {
        "id": 5,
        "type": "temoignage",
        "source": "Déposition de Gros Minou",
        "texte": "A vu Pistache près de la cuisine, de la laine accrochée aux moustaches.",
        "liens": "Pistache · Cuisine · Pelote de laine",
        "est_nouvelle": True,
        "avis": None,
        "note": "",
    },
    {
        "id": 4,
        "type": "temoignage",
        "source": "Déposition de Gros Minou",
        "texte": "Affirme avoir dormi dans son panier pendant toute la sieste de midi.",
        "liens": "Gros Minou · Panier",
        "est_nouvelle": False,
        "avis": "douteux",
        "note": "Il sent le saumon… et il est roux !",
    },
    {
        "id": 3,
        "type": "preuve",
        "source": "Pièce n° A2",
        "texte": "Pelote de laine déroulée jusque sous le canapé.",
        "liens": "Pelote de laine · Salon",
        "est_nouvelle": False,
        "avis": None,
        "note": "",
    },
    {
        "id": 2,
        "type": "temoignage",
        "source": "Déposition de Monsieur Félix",
        "texte": "Était sur le rebord de la fenêtre avec Mistigri pendant toute la sieste.",
        "liens": "Monsieur Félix · Mistigri · Rebord de fenêtre",
        "est_nouvelle": False,
        "avis": "fiable",
        "note": "",
    },
    {
        "id": 1,
        "type": "preuve",
        "source": "Pièce n° A1",
        "texte": "Poils roux sur le comptoir, à côté de l'assiette vide.",
        "liens": "Cuisine",
        "est_nouvelle": False,
        "avis": None,
        "note": "",
    },
]

# --- Fiche de déduction (spec §6.5) : etat = inconnu | barre | valide ------

FICHE = [
    {
        "type": "suspects",
        "titre": "Suspects",
        "cases": [
            {"id": 1, "nom": "Duchesse", "etat": "inconnu"},
            {"id": 2, "nom": "Gros Minou", "etat": "inconnu"},
            {"id": 3, "nom": "Pistache", "etat": "inconnu"},
            {"id": 4, "nom": "Monsieur Félix", "etat": "barre"},
            {"id": 5, "nom": "Mistigri", "etat": "barre"},
        ],
    },
    {
        "type": "objets",
        "titre": "Objets",
        "cases": [
            {"id": 6, "nom": "Pelote de laine", "etat": "valide"},
            {"id": 7, "nom": "Griffoir", "etat": "inconnu"},
            {"id": 8, "nom": "Boîte en carton", "etat": "inconnu"},
            {"id": 9, "nom": "Plumeau", "etat": "barre"},
            {"id": 10, "nom": "Souris en peluche", "etat": "inconnu"},
        ],
    },
    {
        "type": "lieux",
        "titre": "Lieux",
        "cases": [
            {"id": 11, "nom": "Cuisine", "etat": "inconnu"},
            {"id": 12, "nom": "Salon", "etat": "inconnu"},
            {"id": 13, "nom": "Panier", "etat": "inconnu"},
            {"id": 14, "nom": "Rebord de fenêtre", "etat": "barre"},
            {"id": 15, "nom": "Jardin", "etat": "inconnu"},
        ],
    },
]


def niveau_stress(stress: int) -> str:
    """Traduit un stress 0–100 en niveau (seuils de la spec §6.2)."""
    if stress < 35:
        return "calme"
    if stress < 60:
        return "mal_a_l_aise"
    return "nerveux"


def _suspects_enrichis() -> list[dict]:
    """Ajoute les clés calculées de la spec §6.2 (stress_niveau, interroge)."""
    return [
        {
            **suspect,
            "stress_niveau": niveau_stress(suspect["stress"]),
            "interroge": bool(CONVERSATIONS.get(suspect["id"])),
        }
        for suspect in SUSPECTS
    ]


def etat_partie() -> dict:
    """État complet de la partie de démo, SANS les conversations (spec §6.1).

    Renvoyé par GET /api/parties/demo/. Les conversations sont chargées
    suspect par suspect (interrogatoire()), comme le fera l'API réelle.
    """
    questions_posees, questions_max = 12, 20
    cartes_tirees, cartes_max = len(CARTES_TIREES), 6

    return {
        "partie": {"pk": 0, "statut": "en_cours", "code_invitation": "SAUMON42"},
        "enquete": {
            "titre": TITRE,
            "synopsis": "Dimanche, pendant la sieste de midi, le saumon prévu pour le "
            "dîner a disparu de la cuisine. Cinq chats étaient dans la maison.",
        },
        "suspects": _suspects_enrichis(),
        "cartes_tirees": CARTES_TIREES,
        "entrees_carnet": ENTREES_CARNET,
        "fiche": FICHE,
        "compteurs": {
            "questions_posees": questions_posees,
            "questions_max": questions_max,
            "questions_restantes": questions_max - questions_posees,
            "cartes_tirees": cartes_tirees,
            "cartes_max": cartes_max,
            "peut_poser_question": questions_posees < questions_max,
            "peut_tirer_carte": cartes_tirees < cartes_max,
        },
        "joueurs": ["Inspecteur Moustache"],
        "inspecteur": INSPECTEUR,
        # Propre à la démo : l'écran désactive les actions qui demandent le backend.
        "mode_demo": True,
    }


def interrogatoire(suspect_id: int) -> dict | None:
    """Un suspect et sa conversation (spec §6.2 et §6.3), ou None s'il n'existe pas.

    Renvoyé par GET /api/parties/demo/suspects/<id>/.
    """
    suspect = next((s for s in _suspects_enrichis() if s["id"] == suspect_id), None)
    if suspect is None:
        return None
    return {"suspect": suspect, "echanges": CONVERSATIONS.get(suspect_id, [])}
