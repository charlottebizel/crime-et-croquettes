"""
jeu/services.py — Règles du jeu, sans HTTP (les vues appellent ces fonctions).

Pour l'instant :
  - poser une question à un suspect (spec §4, étape 4) ;
  - créer la fiche de déduction d'un joueur (spec §3.4, 15 cases).
La vérification du quota `questions_par_partie` arrive en S4 (tâche quotas).
"""

from dataclasses import dataclass, field

from django.db import transaction
from django.db.models import F

from ia import services as ia_services

from .models import CaseFiche, EntreeCarnet, EtatSuspect, Message, Partie

QUESTION_MAX = 300


@dataclass
class ResultatQuestion:
    question: Message
    reponse: Message
    entrees: list[EntreeCarnet] = field(default_factory=list)


def interroger_suspect(partie, suspect, question: str, joueur, fournisseur=None):
    """Pose `question` à `suspect` et enregistre le résultat dans la partie.

    En cas d'ErreurIA (réponse invalide, fournisseur en échec…), l'erreur est
    relancée et RIEN n'est enregistré dans la partie (ni la question, ni le
    compteur) ; seul l'AppelIA raté reste dans le journal (spec §7.5).

    La vue doit déjà avoir vérifié que `joueur` participe à `partie`.
    """
    question = question.strip()
    if not question or len(question) > QUESTION_MAX:
        raise ValueError(f"La question doit faire entre 1 et {QUESTION_MAX} caractères.")
    if partie.statut != Partie.Statut.EN_COURS:
        raise ValueError("Cette partie est terminée.")
    if suspect.enquete_id != partie.enquete_id:
        raise ValueError("Ce suspect n'appartient pas à cette enquête.")

    etat = EtatSuspect.objects.get(partie=partie, suspect=suspect)

    # Appel IA (journalisé). Lève ErreurIA en cas d'échec.
    donnees, appel = ia_services.interroger(
        partie=partie,
        suspect=suspect,
        question=question,
        stress=etat.stress,
        utilisateur=joueur,
        fournisseur=fournisseur,
    )

    # Tout ou rien : si une écriture échoue, aucune n'est gardée.
    with transaction.atomic():
        message_question = Message.objects.create(
            partie=partie, suspect=suspect, auteur=joueur, est_suspect=False, texte=question
        )
        message_reponse = Message.objects.create(
            partie=partie,
            suspect=suspect,
            est_suspect=True,
            texte=donnees["reponse"],
            stress_avant=etat.stress,
            stress_apres=donnees["stress"],
            appel_ia=appel,
        )
        etat.stress = donnees["stress"]
        etat.save(update_fields=["stress"])

        entrees = []
        for indice in donnees["indices"]:
            entree = EntreeCarnet.objects.create(
                partie=partie,
                type=EntreeCarnet.Type.TEMOIGNAGE,
                suspect_source=suspect,
                message=message_reponse,
                texte=indice["texte"],
            )
            entree.liens_suspects.set(indice["suspects"])
            entree.liens_objets.set(indice["objets"])
            entree.liens_lieux.set(indice["lieux"])
            entrees.append(entree)

        # F() : incrément fait par la base, sûr même si deux joueurs posent
        # une question au même moment.
        Partie.objects.filter(pk=partie.pk).update(questions_posees=F("questions_posees") + 1)
    partie.refresh_from_db(fields=["questions_posees"])

    return ResultatQuestion(question=message_question, reponse=message_reponse, entrees=entrees)


def assurer_fiche(partie, joueur) -> None:
    """Crée les 15 cases de la fiche de déduction de `joueur` si elles manquent.

    Spec §3.4 : une case par suspect, objet et lieu de l'enquête, état
    « inconnu ». Sans danger si on l'appelle plusieurs fois (les cases déjà
    présentes ne sont pas recréées) : on l'appelle au lancement de la partie,
    quand un joueur la rejoint, et par sécurité avant d'afficher la fiche.
    """
    existantes = CaseFiche.objects.filter(partie=partie, joueur=joueur)
    deja = {
        (case.suspect_id, case.objet_id, case.lieu_id)
        for case in existantes.only("suspect_id", "objet_id", "lieu_id")
    }
    enquete = partie.enquete
    a_creer = []
    for suspect in enquete.suspects.all():
        if (suspect.pk, None, None) not in deja:
            a_creer.append(CaseFiche(partie=partie, joueur=joueur, suspect=suspect))
    for objet in enquete.objets.all():
        if (None, objet.pk, None) not in deja:
            a_creer.append(CaseFiche(partie=partie, joueur=joueur, objet=objet))
    for lieu in enquete.lieux.all():
        if (None, None, lieu.pk) not in deja:
            a_creer.append(CaseFiche(partie=partie, joueur=joueur, lieu=lieu))
    CaseFiche.objects.bulk_create(a_creer)
