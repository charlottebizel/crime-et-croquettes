"""
jeu/fabriques.py — Fabrique une petite enquête complète, pour les tests.

Pas d'appel IA : tout est écrit en dur. Version réduite de l'enquête du
saumon (la vraie démo sera chargée par la commande `charger_demo`).
"""

from .models import CartePreuve, Enquete, EtatSuspect, Lieu, Objet, Participation, Partie, Suspect

APPARENCE = {
    "pelage": "#F0A04B",
    "rayures": "#C7741F",
    "rayures_opacite": 1,
    "yeux": "#9BC53D",
    "museau": "#FBE3C4",
    "accessoire": "aucun",
}

NOMS_SUSPECTS = ["Duchesse", "Gros Minou", "Pistache", "Monsieur Félix", "Mistigri"]
NOMS_OBJETS = ["Pelote de laine", "Griffoir", "Boîte en carton", "Plumeau", "Souris en peluche"]
NOMS_LIEUX = ["Cuisine", "Salon", "Panier", "Rebord de fenêtre", "Jardin"]


def creer_enquete(coupable_index: int = 1) -> Enquete:
    """Crée une enquête « prête » : 5 suspects, 5 objets, 5 lieux, 6 cartes."""
    enquete = Enquete.objects.create(
        titre="Qui a volé le saumon du dimanche ?",
        synopsis="Le saumon a disparu de la cuisine.",
        theme="cuisine",
        statut=Enquete.Statut.PRETE,
    )
    suspects = [
        Suspect.objects.create(
            enquete=enquete,
            numero=i + 1,
            nom=nom,
            role=f"Rôle de {nom}",
            personnalite="Parle peu, mais bien.",
            apparence=APPARENCE,
            alibi="Je dormais dans mon panier.",
            alibi_est_vrai=(i != coupable_index),
            connaissances="J'ai senti une odeur de poisson au salon.",
            secret="J'ai renversé le lait hier.",
            stress_initial=20,
        )
        for i, nom in enumerate(NOMS_SUSPECTS)
    ]
    objets = [Objet.objects.create(enquete=enquete, nom=nom) for nom in NOMS_OBJETS]
    lieux = [Lieu.objects.create(enquete=enquete, nom=nom) for nom in NOMS_LIEUX]
    for i in range(6):
        CartePreuve.objects.create(
            enquete=enquete,
            code=f"A{i + 1}",
            titre=f"Preuve {i + 1}",
            texte="Une touffe de poils roux.",
            suspect=suspects[coupable_index] if i % 2 == 0 else None,
            lieu=lieux[0] if i % 2 == 1 else None,
            ordre=i + 1,
        )
    enquete.coupable = suspects[coupable_index]
    enquete.objet_crime = objets[0]
    enquete.lieu_crime = lieux[0]
    enquete.save()
    return enquete


def lancer_partie(enquete: Enquete, hote) -> Partie:
    """Crée la partie, la participation de l'hôte et l'état des 5 suspects."""
    partie = Partie.objects.create(enquete=enquete, hote=hote)
    Participation.objects.create(partie=partie, joueur=hote, role=Participation.Role.HOTE)
    for suspect in enquete.suspects.all():
        EtatSuspect.objects.create(partie=partie, suspect=suspect, stress=suspect.stress_initial)
    return partie
