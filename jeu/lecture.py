"""
jeu/lecture.py — Transforme une partie en base en données JSON pour l'écran Vue (LB-004).

C'est l'équivalent « base de données » de jeu/demo.py : mêmes clés, celles
de docs/specification.md §6. L'écran Vue ne sait pas s'il affiche la démo
ou une vraie partie.

Lecture seule : aucune fonction ici ne modifie la base (sauf assurer_fiche,
appelée par la vue avant de lire la fiche).

Règle d'or (spec §8) : la solution (coupable, objet, lieu), l'alibi, les
connaissances et le secret des suspects ne sortent JAMAIS d'ici.
"""

from django.db.models import Prefetch

from . import demo
from .models import (
    AvisCarnet,
    CaseFiche,
    EntreeCarnet,
    EtatSuspect,
    Message,
)


def niveau_stress(stress: int) -> str:
    """Même seuils que la démo (spec §6.2)."""
    return demo.niveau_stress(stress)


def pseudo(utilisateur) -> str:
    """Nom affiché d'un joueur : son pseudo, sinon son nom de connexion."""
    if utilisateur is None:
        return "Agent disparu"  # compte supprimé (spec §8)
    profil = getattr(utilisateur, "profil", None)
    return (profil.pseudo if profil and profil.pseudo else "") or utilisateur.username


def _suspect(etat: EtatSuspect, interroges: set[int]) -> dict:
    """Un suspect au format spec §6.2 (sans rien de ce que seul le serveur sait)."""
    suspect = etat.suspect
    return {
        "id": suspect.pk,
        "numero": suspect.numero,
        "nom": suspect.nom,
        "role": suspect.role,
        "apparence": suspect.apparence,
        "stress": etat.stress,
        "stress_niveau": niveau_stress(etat.stress),
        "interroge": suspect.pk in interroges,
    }


def _etiquette(carte) -> str:
    """« Lieu · Cuisine », « Objet · Pelote de laine / Lieu · Salon »…"""
    morceaux = []
    if carte.suspect:
        morceaux.append(f"Suspect · {carte.suspect.nom}")
    if carte.objet:
        morceaux.append(f"Objet · {carte.objet.nom}")
    if carte.lieu:
        morceaux.append(f"Lieu · {carte.lieu.nom}")
    return " / ".join(morceaux)


def carte(carte) -> dict:
    return {
        "code": carte.code,
        "titre": carte.titre,
        "texte": carte.texte,
        "etiquette": _etiquette(carte),
    }


def entree(entree: EntreeCarnet, avis: AvisCarnet | None) -> dict:
    """Une entrée du carnet au format spec §6.4, avec l'avis du joueur connecté."""
    if entree.type == EntreeCarnet.Type.PREUVE:
        source = f"Pièce n° {entree.carte.code}" if entree.carte else "Pièce à conviction"
    else:
        nom = entree.suspect_source.nom if entree.suspect_source else "un suspect"
        source = f"Déposition de {nom}"
    liens = [s.nom for s in entree.liens_suspects.all()]
    liens += [o.nom for o in entree.liens_objets.all()]
    liens += [lieu.nom for lieu in entree.liens_lieux.all()]
    return {
        "id": entree.pk,
        "type": entree.type,
        "source": source,
        "texte": entree.texte,
        "liens": " · ".join(liens),
        # « Nouveau » = un témoignage que ce joueur n'a pas encore jugé
        # (on ne mémorise pas ses visites ; voir spec §6.4).
        "est_nouvelle": entree.type == EntreeCarnet.Type.TEMOIGNAGE and not (avis and avis.avis),
        "avis": (avis.avis or None) if avis else None,
        "note": avis.note if avis else "",
    }


def message(message: Message, avec_carnet: set[int]) -> dict:
    """Une réplique au format spec §6.3."""
    return {
        "est_suspect": message.est_suspect,
        "texte": message.texte,
        "stress_avant": message.stress_avant,
        "stress_apres": message.stress_apres,
        "a_ajoute_au_carnet": message.pk in avec_carnet,
        "auteur": None if message.est_suspect else pseudo(message.auteur),
    }


def compteurs(partie) -> dict:
    """Spec §6.6. Les plafonds viennent du palier de l'hôte (exigence O4)."""
    palier = partie.hote.profil.palier
    questions_max = palier.questions_par_partie
    cartes_max = min(palier.cartes_par_partie, partie.enquete.cartes.count())
    cartes_tirees = partie.cartes_tirees.count()
    en_cours = partie.statut == partie.Statut.EN_COURS
    return {
        "questions_posees": partie.questions_posees,
        "questions_max": questions_max,
        "questions_restantes": max(questions_max - partie.questions_posees, 0),
        "cartes_tirees": cartes_tirees,
        "cartes_max": cartes_max,
        "peut_poser_question": en_cours and partie.questions_posees < questions_max,
        "peut_tirer_carte": en_cours and cartes_tirees < cartes_max,
    }


def _suspects_interroges(partie) -> set[int]:
    return set(
        Message.objects.filter(partie=partie, est_suspect=False).values_list(
            "suspect_id", flat=True
        )
    )


def _fiche(partie, joueur) -> list[dict]:
    """Spec §6.5 : trois groupes, dans l'ordre de l'enquête."""
    cases = {
        (c.suspect_id, c.objet_id, c.lieu_id): c
        for c in CaseFiche.objects.filter(partie=partie, joueur=joueur)
    }
    enquete = partie.enquete

    def groupe(type_, titre, elements, cle):
        return {
            "type": type_,
            "titre": titre,
            "cases": [
                {"id": cases[cle(e)].pk, "nom": e.nom, "etat": cases[cle(e)].etat}
                for e in elements
                if cle(e) in cases
            ],
        }

    return [
        groupe("suspects", "Suspects", enquete.suspects.all(), lambda e: (e.pk, None, None)),
        groupe("objets", "Objets", enquete.objets.all(), lambda e: (None, e.pk, None)),
        groupe("lieux", "Lieux", enquete.lieux.all(), lambda e: (None, None, e.pk)),
    ]


def etat_partie(partie, joueur) -> dict:
    """GET /api/parties/<pk>/ : état complet vu par `joueur` (sans conversations)."""
    interroges = _suspects_interroges(partie)
    etats = EtatSuspect.objects.filter(partie=partie).select_related("suspect")
    etats = sorted(etats, key=lambda e: e.suspect.numero)

    avis_du_joueur = AvisCarnet.objects.filter(joueur=joueur)
    entrees = (
        EntreeCarnet.objects.filter(partie=partie)
        .select_related("carte", "suspect_source")
        .prefetch_related(
            "liens_suspects",
            "liens_objets",
            "liens_lieux",
            Prefetch("avis", queryset=avis_du_joueur, to_attr="avis_joueur"),
        )
        .order_by("-cree_le", "-pk")  # plus récente d'abord
    )
    cartes_tirees = partie.cartes_tirees.select_related(
        "carte__suspect", "carte__objet", "carte__lieu"
    ).order_by("tiree_le", "pk")

    return {
        "partie": {
            "pk": partie.pk,
            "statut": partie.statut,
            "code_invitation": partie.code_invitation,
        },
        "enquete": {"titre": partie.enquete.titre, "synopsis": partie.enquete.synopsis},
        "suspects": [_suspect(e, interroges) for e in etats],
        "cartes_tirees": [carte(t.carte) for t in cartes_tirees],
        "entrees_carnet": [entree(e, e.avis_joueur[0] if e.avis_joueur else None) for e in entrees],
        "fiche": _fiche(partie, joueur),
        "compteurs": compteurs(partie),
        "joueurs": [
            pseudo(p.joueur)
            for p in partie.participations.select_related("joueur__profil").order_by("cree_le")
        ],
        "inspecteur": demo.INSPECTEUR,
        "mode_demo": False,
    }


def interrogatoire(partie, suspect) -> dict:
    """GET /api/parties/<pk>/suspects/<sid>/ : un suspect et sa conversation."""
    etat = EtatSuspect.objects.select_related("suspect").get(partie=partie, suspect=suspect)
    messages = list(
        Message.objects.filter(partie=partie, suspect=suspect)
        .select_related("auteur__profil")
        .order_by("cree_le", "pk")
    )
    avec_carnet = set(
        EntreeCarnet.objects.filter(message__in=messages).values_list("message_id", flat=True)
    )
    return {
        "suspect": _suspect(etat, _suspects_interroges(partie)),
        "echanges": [message(m, avec_carnet) for m in messages],
    }
