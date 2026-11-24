"""
ia/erreurs.py — Exceptions levées par la couche IA.

Les vues attrapent ErreurIA pour afficher un message clair au joueur ;
le détail technique (`detail`) va seulement dans le journal AppelIA.

Le classement fin des erreurs du fournisseur (délai, panne, crédit) et les
messages pour le joueur arrivent en S4 (spec §7.5, tâche « 4 erreurs IA »).
"""


class ErreurIA(Exception):
    """Un appel IA n'a pas abouti. `type_erreur` : valeur de AppelIA.Erreur ou ""."""

    type_erreur = ""

    def __init__(self, detail: str = ""):
        super().__init__(detail)
        self.detail = detail


class ErreurFournisseur(ErreurIA):
    """Le fournisseur (OpenRouter) a échoué : réseau, délai, statut HTTP…"""


class ReponseInvalide(ErreurIA):
    """JSON illisible ou refusé par la validation (spec §7.3)."""

    type_erreur = "invalide"
