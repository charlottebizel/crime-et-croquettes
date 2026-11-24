"""
jeu/models.py — Modèles du jeu (spec §3.2 à §3.4).

Trois familles :
  - l'enquête générée (Enquete, Suspect, Objet, Lieu, CartePreuve) ;
  - la partie jouée (Partie, Participation, EtatSuspect, CarteTiree, Message) ;
  - le carnet et la déduction (EntreeCarnet, AvisCarnet, CaseFiche, Accusation).

Règle d'or : la solution (Enquete.coupable / objet_crime / lieu_crime) ne
doit jamais être envoyée au navigateur tant que la partie est en cours.

Choix de suppression (on_delete) :
  - tout ce qui dépend d'une enquête ou d'une partie : CASCADE (spec §3) ;
  - un joueur supprime son compte (spec §8) : ses participations, avis,
    cases et accusations disparaissent (CASCADE) ; ses traces dans les
    données partagées de la partie (messages, cartes tirées) restent, avec
    l'auteur à NULL, pour ne pas casser la partie des autres joueurs.
"""

import secrets

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

STRESS_VALIDATEURS = [MinValueValidator(0), MaxValueValidator(100)]


# --- Enquête -----------------------------------------------------------------


class Enquete(models.Model):
    class Difficulte(models.TextChoices):
        FACILE = "facile", "Facile"
        NORMAL = "normal", "Normal"
        DIFFICILE = "difficile", "Difficile"

    class Statut(models.TextChoices):
        GENERATION = "generation", "En cours de génération"
        PRETE = "prete", "Prête"
        ERREUR = "erreur", "Erreur"

    titre = models.CharField(max_length=80)
    synopsis = models.TextField(blank=True)
    theme = models.CharField(max_length=60, blank=True)
    difficulte = models.CharField(
        max_length=10, choices=Difficulte.choices, default=Difficulte.NORMAL
    )
    creee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enquetes_creees",
    )
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.GENERATION)

    # La solution. related_name="+" : pas d'accès inverse (suspect.enquetes_…),
    # pour ne pas exposer la solution par accident.
    coupable = models.ForeignKey(
        "Suspect", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    objet_crime = models.ForeignKey(
        "Objet", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    lieu_crime = models.ForeignKey(
        "Lieu", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    # L'appel IA qui a généré l'enquête (journal des coûts, O4).
    appel_ia = models.ForeignKey(
        "ia.AppelIA", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-cree_le"]
        verbose_name = "enquête"

    def __str__(self) -> str:
        return self.titre


class Suspect(models.Model):
    enquete = models.ForeignKey(Enquete, on_delete=models.CASCADE, related_name="suspects")
    numero = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    nom = models.CharField(max_length=30)
    role = models.CharField(max_length=40)
    personnalite = models.TextField()
    # Lu par le frontend pour dessiner le chat (spec §3.2) :
    # {"pelage", "rayures", "rayures_opacite", "yeux", "museau", "accessoire"}
    apparence = models.JSONField(default=dict)
    alibi = models.TextField()
    alibi_est_vrai = models.BooleanField(default=True)
    connaissances = models.TextField()
    secret = models.TextField(blank=True)
    stress_initial = models.PositiveSmallIntegerField(default=20, validators=STRESS_VALIDATEURS)

    class Meta:
        ordering = ["enquete", "numero"]
        constraints = [
            models.UniqueConstraint(fields=["enquete", "numero"], name="suspect_numero_unique"),
            models.CheckConstraint(
                condition=Q(numero__gte=1, numero__lte=5), name="suspect_numero_1_a_5"
            ),
            models.CheckConstraint(
                condition=Q(stress_initial__lte=100), name="suspect_stress_initial_max_100"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nom} ({self.role})"


class Objet(models.Model):
    enquete = models.ForeignKey(Enquete, on_delete=models.CASCADE, related_name="objets")
    nom = models.CharField(max_length=30)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["enquete", "pk"]

    def __str__(self) -> str:
        return self.nom


class Lieu(models.Model):
    enquete = models.ForeignKey(Enquete, on_delete=models.CASCADE, related_name="lieux")
    nom = models.CharField(max_length=30)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["enquete", "pk"]
        verbose_name_plural = "lieux"

    def __str__(self) -> str:
        return self.nom


class CartePreuve(models.Model):
    """Pièce à conviction, toujours vraie. Pointe vers au moins un élément."""

    enquete = models.ForeignKey(Enquete, on_delete=models.CASCADE, related_name="cartes")
    code = models.CharField(max_length=2)  # A1 … A6
    titre = models.CharField(max_length=40)
    texte = models.CharField(max_length=200)
    suspect = models.ForeignKey(
        Suspect, on_delete=models.CASCADE, null=True, blank=True, related_name="cartes"
    )
    objet = models.ForeignKey(
        Objet, on_delete=models.CASCADE, null=True, blank=True, related_name="cartes"
    )
    lieu = models.ForeignKey(
        Lieu, on_delete=models.CASCADE, null=True, blank=True, related_name="cartes"
    )
    ordre = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["enquete", "ordre"]
        verbose_name = "carte preuve"
        verbose_name_plural = "cartes preuves"
        constraints = [
            models.UniqueConstraint(fields=["enquete", "code"], name="carte_code_unique"),
            models.CheckConstraint(
                condition=Q(suspect__isnull=False) | Q(objet__isnull=False) | Q(lieu__isnull=False),
                name="carte_pointe_vers_un_element",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.titre}"


# --- Partie ------------------------------------------------------------------

# Sans 0/O ni 1/I/L : un code facile à dicter à un ami.
ALPHABET_CODE = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


def nouveau_code_invitation() -> str:
    """8 caractères au hasard (secrets = hasard cryptographique, non devinable)."""
    return "".join(secrets.choice(ALPHABET_CODE) for _ in range(8))


class Partie(models.Model):
    class Statut(models.TextChoices):
        EN_COURS = "en_cours", "En cours"
        GAGNEE = "gagnee", "Gagnée"
        PERDUE = "perdue", "Perdue"

    enquete = models.ForeignKey(Enquete, on_delete=models.CASCADE, related_name="parties")
    hote = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="parties_hebergees"
    )
    code_invitation = models.CharField(max_length=8, unique=True, default=nouveau_code_invitation)
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.EN_COURS)
    questions_posees = models.PositiveIntegerField(default=0)  # compteur partagé
    cree_le = models.DateTimeField(auto_now_add=True)
    terminee_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-cree_le"]

    def __str__(self) -> str:
        return f"Partie {self.code_invitation} — {self.enquete}"


class Participation(models.Model):
    class Role(models.TextChoices):
        HOTE = "hote", "Hôte"
        JOUEUR = "joueur", "Joueur"

    partie = models.ForeignKey(Partie, on_delete=models.CASCADE, related_name="participations")
    joueur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="participations"
    )
    role = models.CharField(max_length=6, choices=Role.choices, default=Role.JOUEUR)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("partie", "joueur")]

    def __str__(self) -> str:
        return f"{self.joueur} dans {self.partie} ({self.role})"


class EtatSuspect(models.Model):
    """Stress d'un suspect dans une partie donnée (créé au lancement)."""

    partie = models.ForeignKey(Partie, on_delete=models.CASCADE, related_name="etats_suspects")
    suspect = models.ForeignKey(Suspect, on_delete=models.CASCADE, related_name="etats")
    stress = models.PositiveSmallIntegerField(validators=STRESS_VALIDATEURS)

    class Meta:
        unique_together = [("partie", "suspect")]
        verbose_name = "état d'un suspect"
        verbose_name_plural = "états des suspects"
        constraints = [
            models.CheckConstraint(condition=Q(stress__lte=100), name="etat_stress_max_100"),
        ]

    def __str__(self) -> str:
        return f"{self.suspect.nom} : stress {self.stress}"


class CarteTiree(models.Model):
    partie = models.ForeignKey(Partie, on_delete=models.CASCADE, related_name="cartes_tirees")
    carte = models.ForeignKey(CartePreuve, on_delete=models.CASCADE, related_name="tirages")
    tiree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cartes_tirees",
    )
    tiree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("partie", "carte")]
        ordering = ["tiree_le"]
        verbose_name = "carte tirée"
        verbose_name_plural = "cartes tirées"

    def __str__(self) -> str:
        return f"{self.carte.code} tirée dans {self.partie.code_invitation}"


class Message(models.Model):
    """Une réplique de la conversation avec un suspect (question ou réponse)."""

    partie = models.ForeignKey(Partie, on_delete=models.CASCADE, related_name="messages")
    suspect = models.ForeignKey(Suspect, on_delete=models.CASCADE, related_name="messages")
    auteur = models.ForeignKey(  # NULL = réponse du suspect (ou compte supprimé)
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
    )
    est_suspect = models.BooleanField(default=False)
    texte = models.TextField()
    stress_avant = models.PositiveSmallIntegerField(null=True, blank=True)
    stress_apres = models.PositiveSmallIntegerField(null=True, blank=True)
    appel_ia = models.ForeignKey(
        "ia.AppelIA", on_delete=models.SET_NULL, null=True, blank=True, related_name="messages"
    )
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["cree_le", "pk"]

    def __str__(self) -> str:
        qui = self.suspect.nom if self.est_suspect else "Question"
        return f"{qui} : {self.texte[:40]}"


# --- Carnet et déduction -----------------------------------------------------


class EntreeCarnet(models.Model):
    """Un indice du carnet, commun à toute la partie."""

    class Type(models.TextChoices):
        TEMOIGNAGE = "temoignage", "Témoignage"
        PREUVE = "preuve", "Preuve"

    partie = models.ForeignKey(Partie, on_delete=models.CASCADE, related_name="entrees")
    type = models.CharField(max_length=10, choices=Type.choices)
    suspect_source = models.ForeignKey(  # pour un témoignage
        Suspect, on_delete=models.CASCADE, null=True, blank=True, related_name="temoignages"
    )
    carte = models.ForeignKey(  # pour une preuve
        CartePreuve, on_delete=models.CASCADE, null=True, blank=True, related_name="entrees"
    )
    message = models.ForeignKey(  # la réponse qui l'a produite
        Message, on_delete=models.SET_NULL, null=True, blank=True, related_name="entrees"
    )
    texte = models.CharField(max_length=200)
    liens_suspects = models.ManyToManyField(Suspect, blank=True, related_name="entrees_liees")
    liens_objets = models.ManyToManyField(Objet, blank=True, related_name="entrees_liees")
    liens_lieux = models.ManyToManyField(Lieu, blank=True, related_name="entrees_liees")
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["cree_le", "pk"]
        verbose_name = "entrée du carnet"
        verbose_name_plural = "entrées du carnet"

    def __str__(self) -> str:
        return f"[{self.type}] {self.texte[:40]}"


class AvisCarnet(models.Model):
    """Avis et note personnels d'un joueur sur une entrée du carnet."""

    class Avis(models.TextChoices):
        FIABLE = "fiable", "Fiable"
        DOUTEUX = "douteux", "Douteux"
        FAUX = "faux", "Faux"

    entree = models.ForeignKey(EntreeCarnet, on_delete=models.CASCADE, related_name="avis")
    joueur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="avis_carnet"
    )
    # "" = pas encore d'avis (convention Django : pas de NULL sur un texte).
    avis = models.CharField(max_length=7, choices=Avis.choices, blank=True, default="")
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = [("entree", "joueur")]
        verbose_name = "avis sur le carnet"
        verbose_name_plural = "avis sur le carnet"

    def __str__(self) -> str:
        return f"{self.joueur} : {self.avis or 'sans avis'}"


class CaseFiche(models.Model):
    """Une case de la fiche de déduction personnelle (15 par joueur)."""

    class Etat(models.TextChoices):
        INCONNU = "inconnu", "Inconnu"
        BARRE = "barre", "Barré"
        VALIDE = "valide", "Validé"

    partie = models.ForeignKey(Partie, on_delete=models.CASCADE, related_name="cases")
    joueur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cases_fiche"
    )
    suspect = models.ForeignKey(Suspect, on_delete=models.CASCADE, null=True, blank=True)
    objet = models.ForeignKey(Objet, on_delete=models.CASCADE, null=True, blank=True)
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, null=True, blank=True)
    etat = models.CharField(max_length=7, choices=Etat.choices, default=Etat.INCONNU)

    class Meta:
        verbose_name = "case de la fiche"
        verbose_name_plural = "cases de la fiche"
        constraints = [
            # Exactement un des trois éléments est renseigné.
            models.CheckConstraint(
                condition=(
                    Q(suspect__isnull=False, objet__isnull=True, lieu__isnull=True)
                    | Q(suspect__isnull=True, objet__isnull=False, lieu__isnull=True)
                    | Q(suspect__isnull=True, objet__isnull=True, lieu__isnull=False)
                ),
                name="case_un_seul_element",
            ),
            # Une seule case par élément et par joueur.
            models.UniqueConstraint(
                fields=["partie", "joueur", "suspect"],
                condition=Q(suspect__isnull=False),
                name="case_suspect_unique",
            ),
            models.UniqueConstraint(
                fields=["partie", "joueur", "objet"],
                condition=Q(objet__isnull=False),
                name="case_objet_unique",
            ),
            models.UniqueConstraint(
                fields=["partie", "joueur", "lieu"],
                condition=Q(lieu__isnull=False),
                name="case_lieu_unique",
            ),
        ]

    def __str__(self) -> str:
        element = self.suspect or self.objet or self.lieu
        return f"{element} : {self.etat}"


class Accusation(models.Model):
    partie = models.ForeignKey(Partie, on_delete=models.CASCADE, related_name="accusations")
    joueur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accusations"
    )
    suspect = models.ForeignKey(Suspect, on_delete=models.CASCADE, related_name="+")
    objet = models.ForeignKey(Objet, on_delete=models.CASCADE, related_name="+")
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, related_name="+")
    correcte = models.BooleanField()
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["cree_le"]

    def __str__(self) -> str:
        resultat = "juste" if self.correcte else "fausse"
        return f"{self.joueur} accuse {self.suspect.nom} ({resultat})"
