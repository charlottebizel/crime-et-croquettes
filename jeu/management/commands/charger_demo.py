"""
jeu/management/commands/charger_demo.py — Données de démonstration en base (ticket LB-003).

    python manage.py charger_demo                 # crée ce qui manque
    python manage.py charger_demo --reinitialiser # efface puis recrée l'enquête de démo

Crée (spec §9) :
  - 3 comptes : « admin » (administrateur), « moustache » (palier Pro, hôte
    de la partie), « joueur » (palier Free, invité dans la partie) ;
  - l'enquête « Qui a volé le saumon du dimanche ? » complète : 5 suspects,
    5 objets, 5 lieux, 6 pièces à conviction et la solution ;
  - une partie en cours, avec des interrogatoires, des cartes tirées, un
    carnet annoté et une fiche de déduction déjà commencée.

Aucun appel à l'IA : tout est écrit en dur (exigence O2 : « données de
démonstration »). Les suspects, conversations et cartes reprennent
jeu/demo.py, pour que la démo publique et la démo en base racontent la
même histoire.

Mots de passe : lus dans la variable d'environnement DEMO_MOT_DE_PASSE.
Si elle est absente, un mot de passe aléatoire est tiré et affiché UNE fois.
Un compte qui existe déjà garde son mot de passe : la commande peut être
relancée sans danger (idempotente).
"""

import os
import secrets

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from comptes.models import PALIER_PRO, Palier
from jeu import demo
from jeu.models import (
    AvisCarnet,
    CartePreuve,
    CarteTiree,
    CaseFiche,
    Enquete,
    EntreeCarnet,
    EtatSuspect,
    Lieu,
    Message,
    Objet,
    Participation,
    Partie,
    Suspect,
)
from jeu.services import assurer_fiche

THEME_DEMO = "démo"
CODE_PARTIE_DEMO = "SAUMON42"

# --- Ce que seul le serveur sait (jamais envoyé au navigateur) --------------
# Personnalité, alibi, connaissances et secret servent au prompt de l'IA
# (spec §7.2). Le coupable est Gros Minou, avec la boîte en carton, dans la cuisine.

FICHES_SUSPECTS = {
    "Duchesse": {
        "personnalite": "Persane hautaine. Parle d'elle à la troisième personne et "
        "méprise tout ce qui n'est pas brossé.",
        "alibi": "Se faisait brosser sur son coussin du salon pendant toute la sieste.",
        "alibi_est_vrai": True,
        "connaissances": "A entendu un bruit de carton froissé du côté du panier de "
        "Gros Minou vers midi et quart.",
        "secret": "A caché la télécommande sous son coussin pour qu'on ne change pas "
        "sa chaîne animalière.",
        "stress_initial": 20,
    },
    "Gros Minou": {
        "personnalite": "Roux gourmand et jovial. Ment en ronronnant et change de sujet "
        "dès qu'on parle de nourriture.",
        "alibi": "Dit avoir dormi dans son panier pendant toute la sieste.",
        "alibi_est_vrai": False,
        "connaissances": "A volé le saumon dans la cuisine, l'a emporté dans une boîte "
        "en carton et l'a mangé derrière son panier. Sait que Pistache jouait avec la "
        "pelote au salon.",
        "secret": "A déjà volé le jambon de Noël l'an dernier.",
        "stress_initial": 30,
    },
    "Pistache": {
        "personnalite": "Chaton surexcité. Parle vite et se contredit sur des détails "
        "sans importance.",
        "alibi": "Jouait avec la pelote de laine au salon.",
        "alibi_est_vrai": True,
        "connaissances": "A vu Gros Minou traîner une boîte en carton vers son panier, "
        "mais croyait que c'était un jeu.",
        "secret": "A griffé le canapé neuf et accuse le griffoir d'être trop dur.",
        "stress_initial": 35,
    },
    "Monsieur Félix": {
        "personnalite": "Vieux matou noir, calme et précis. Parle comme un notaire.",
        "alibi": "Sur le rebord de la fenêtre avec Mistigri, à regarder les oiseaux.",
        "alibi_est_vrai": True,
        "connaissances": "De la fenêtre, a vu une ombre rousse passer dans la cuisine "
        "juste avant midi.",
        "secret": "Ne voit plus très bien de près et refuse de l'admettre.",
        "stress_initial": 10,
    },
    "Mistigri": {
        "personnalite": "Chatte de gouttière débrouillarde et méfiante. Répond souvent "
        "par une autre question.",
        "alibi": "Sur le rebord de la fenêtre avec Monsieur Félix.",
        "alibi_est_vrai": True,
        "connaissances": "A senti une odeur de poisson venant du panier de Gros Minou en rentrant.",
        "secret": "Sort la nuit par la chatière alors que c'est interdit.",
        "stress_initial": 25,
    },
}

OBJETS = [
    ("Pelote de laine", "Une pelote rouge, le jouet préféré de Pistache."),
    ("Griffoir", "Un poteau couvert de corde, au salon."),
    ("Boîte en carton", "Une boîte à chaussures vide, assez grande pour un saumon."),
    ("Plumeau", "Le plumeau de la femme de ménage, rangé dans le placard."),
    ("Souris en peluche", "Une souris grise qui couine quand on la mord."),
]

LIEUX = [
    ("Cuisine", "Là où le saumon attendait le dîner."),
    ("Salon", "Le canapé, le griffoir et le coussin de Duchesse."),
    ("Panier", "Le panier de Gros Minou, près du radiateur."),
    ("Rebord de fenêtre", "Le poste d'observation préféré des chats."),
    ("Jardin", "On y accède par la chatière."),
]

# Pièces à conviction : toujours vraies. Chaque élément de la solution est
# prouvé par au moins une carte (spec §7.3) : Gros Minou (A3), la boîte en
# carton (A3), la cuisine (A1, A4).
CARTES = [
    ("A1", "Poils roux", demo.CARTES_TIREES[0]["texte"], None, None, "Cuisine"),
    ("A2", "Pelote déroulée", demo.CARTES_TIREES[1]["texte"], None, "Pelote de laine", None),
    (
        "A3",
        "Carton suspect",
        "Une boîte en carton qui sent le poisson, cachée derrière le panier de Gros Minou.",
        "Gros Minou",
        "Boîte en carton",
        None,
    ),
    (
        "A4",
        "Empreintes grasses",
        "Des empreintes de pattes grasses sur le plan de travail de la cuisine.",
        None,
        None,
        "Cuisine",
    ),
    (
        "A5",
        "Coussin impeccable",
        "Le coussin de Duchesse est brossé et sans la moindre miette.",
        "Duchesse",
        None,
        "Salon",
    ),
    (
        "A6",
        "Traces sur la vitre",
        "Deux paires de traces de museau sur la vitre, côté rebord.",
        "Mistigri",
        None,
        "Rebord de fenêtre",
    ),
]

# Carnet de la partie, dans l'ordre chronologique (le plus ancien d'abord).
# (type, suspect source ou code de carte, texte, suspects, objets, lieux, réponse liée)
CARNET = [
    ("preuve", "A1", None, [], [], ["Cuisine"], None),
    (
        "temoignage",
        "Monsieur Félix",
        "Était sur le rebord de la fenêtre avec Mistigri pendant toute la sieste.",
        ["Monsieur Félix", "Mistigri"],
        [],
        ["Rebord de fenêtre"],
        ("Monsieur Félix", 0),
    ),
    ("preuve", "A2", None, [], ["Pelote de laine"], ["Salon"], None),
    (
        "temoignage",
        "Gros Minou",
        "Affirme avoir dormi dans son panier pendant toute la sieste de midi.",
        ["Gros Minou"],
        [],
        ["Panier"],
        ("Gros Minou", 0),
    ),
    (
        "temoignage",
        "Gros Minou",
        "A vu Pistache près de la cuisine, de la laine accrochée aux moustaches.",
        ["Pistache"],
        ["Pelote de laine"],
        ["Cuisine"],
        ("Gros Minou", 1),
    ),
]


class Command(BaseCommand):
    help = "Charge l'enquête de démonstration (le saumon du dimanche) et les comptes de démo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reinitialiser",
            action="store_true",
            help="Supprime l'enquête de démo existante (et sa partie) avant de la recréer.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        mot_de_passe = os.environ.get("DEMO_MOT_DE_PASSE", "")
        mot_de_passe_tire = not mot_de_passe
        if mot_de_passe_tire:
            mot_de_passe = secrets.token_urlsafe(9)

        admin, cree_admin = self.compte("admin", mot_de_passe, administrateur=True)
        moustache, cree_moustache = self.compte("moustache", mot_de_passe, pseudo="Moustache")
        joueur, cree_joueur = self.compte("joueur", mot_de_passe, pseudo="Joueur")

        # moustache passe au palier Pro (l'admin le fera à la main pour les autres).
        moustache.profil.palier = Palier.objects.get(nom=PALIER_PRO)
        moustache.profil.save(update_fields=["palier"])

        existantes = Enquete.objects.filter(titre=demo.TITRE, theme=THEME_DEMO)
        if existantes.exists() and options["reinitialiser"]:
            existantes.delete()  # CASCADE : suspects, cartes, partie, carnet…
            self.stdout.write("Ancienne enquête de démo supprimée.")
        if existantes.exists():
            self.stdout.write("L'enquête de démo existe déjà : rien à recréer.")
        else:
            partie = self.creer_partie(moustache, joueur)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Enquête de démo créée. Partie n° {partie.pk}, code {partie.code_invitation}."
                )
            )

        nouveaux = [
            c.username
            for c, cree in ((admin, cree_admin), (moustache, cree_moustache), (joueur, cree_joueur))
            if cree
        ]
        if nouveaux:
            self.stdout.write(f"Comptes créés : {', '.join(nouveaux)}.")
            if mot_de_passe_tire:
                self.stdout.write(
                    self.style.WARNING(
                        f"Mot de passe de ces comptes (affiché une seule fois) : {mot_de_passe}"
                    )
                )
            else:
                self.stdout.write("Mot de passe : celui de DEMO_MOT_DE_PASSE.")

    # ------------------------------------------------------------------

    def compte(self, nom, mot_de_passe, administrateur=False, pseudo=""):
        """Crée le compte s'il manque. Un compte existant n'est pas modifié."""
        utilisateur = User.objects.filter(username=nom).first()
        if utilisateur:
            return utilisateur, False
        if administrateur:
            utilisateur = User.objects.create_superuser(nom, f"{nom}@exemple.invalid", mot_de_passe)
        else:
            utilisateur = User.objects.create_user(nom, f"{nom}@exemple.invalid", mot_de_passe)
        if pseudo:
            # Le profil a été créé par le signal de comptes/signals.py.
            utilisateur.profil.pseudo = pseudo
            utilisateur.profil.save(update_fields=["pseudo"])
        return utilisateur, True

    def creer_partie(self, hote, invite):
        enquete = Enquete.objects.create(
            titre=demo.TITRE,
            synopsis=demo.etat_partie()["enquete"]["synopsis"],
            theme=THEME_DEMO,
            difficulte=Enquete.Difficulte.FACILE,
            statut=Enquete.Statut.PRETE,
        )

        suspects = {}
        for infos in demo.SUSPECTS:
            suspects[infos["nom"]] = Suspect.objects.create(
                enquete=enquete,
                numero=infos["numero"],
                nom=infos["nom"],
                role=infos["role"],
                apparence=infos["apparence"],
                **FICHES_SUSPECTS[infos["nom"]],
            )
        objets = {
            nom: Objet.objects.create(enquete=enquete, nom=nom, description=description)
            for nom, description in OBJETS
        }
        lieux = {
            nom: Lieu.objects.create(enquete=enquete, nom=nom, description=description)
            for nom, description in LIEUX
        }
        cartes = {}
        for ordre, (code, titre, texte, suspect, objet, lieu) in enumerate(CARTES, start=1):
            cartes[code] = CartePreuve.objects.create(
                enquete=enquete,
                code=code,
                titre=titre,
                texte=texte,
                suspect=suspects.get(suspect),
                objet=objets.get(objet),
                lieu=lieux.get(lieu),
                ordre=ordre,
            )

        # La solution, connue du serveur seulement.
        enquete.coupable = suspects["Gros Minou"]
        enquete.objet_crime = objets["Boîte en carton"]
        enquete.lieu_crime = lieux["Cuisine"]
        enquete.save(update_fields=["coupable", "objet_crime", "lieu_crime"])

        # --- La partie en cours -------------------------------------------
        partie = Partie.objects.create(enquete=enquete, hote=hote, code_invitation=CODE_PARTIE_DEMO)
        Participation.objects.create(partie=partie, joueur=hote, role=Participation.Role.HOTE)
        Participation.objects.create(partie=partie, joueur=invite, role=Participation.Role.JOUEUR)
        for infos in demo.SUSPECTS:
            EtatSuspect.objects.create(
                partie=partie, suspect=suspects[infos["nom"]], stress=infos["stress"]
            )

        # Interrogatoires déjà joués (les mêmes que la démo publique).
        reponses = {}  # (nom du suspect, n° de la réponse) → Message
        questions = 0
        for infos in demo.SUSPECTS:
            suspect = suspects[infos["nom"]]
            numero_reponse = 0
            for echange in demo.CONVERSATIONS.get(infos["id"], []):
                message = Message.objects.create(
                    partie=partie,
                    suspect=suspect,
                    auteur=None if echange["est_suspect"] else hote,
                    est_suspect=echange["est_suspect"],
                    texte=echange["texte"],
                    stress_avant=echange["stress_avant"],
                    stress_apres=echange["stress_apres"],
                )
                if echange["est_suspect"]:
                    reponses[(infos["nom"], numero_reponse)] = message
                    numero_reponse += 1
                else:
                    questions += 1
        partie.questions_posees = questions
        partie.save(update_fields=["questions_posees"])

        # Cartes tirées et carnet.
        for code in ("A1", "A2"):
            CarteTiree.objects.create(partie=partie, carte=cartes[code], tiree_par=hote)
        entrees = []
        for type_, source, texte, noms_s, noms_o, noms_l, reponse in CARNET:
            if type_ == "preuve":
                entree = EntreeCarnet.objects.create(
                    partie=partie,
                    type=EntreeCarnet.Type.PREUVE,
                    carte=cartes[source],
                    texte=cartes[source].texte,
                )
            else:
                entree = EntreeCarnet.objects.create(
                    partie=partie,
                    type=EntreeCarnet.Type.TEMOIGNAGE,
                    suspect_source=suspects[source],
                    message=reponses.get(reponse),
                    texte=texte,
                )
            entree.liens_suspects.set([suspects[n] for n in noms_s])
            entree.liens_objets.set([objets[n] for n in noms_o])
            entree.liens_lieux.set([lieux[n] for n in noms_l])
            entrees.append(entree)

        # Avis et fiche de l'hôte (l'invité commence avec une fiche vierge).
        AvisCarnet.objects.create(entree=entrees[1], joueur=hote, avis=AvisCarnet.Avis.FIABLE)
        AvisCarnet.objects.create(
            entree=entrees[3],
            joueur=hote,
            avis=AvisCarnet.Avis.DOUTEUX,
            note="Il sent le saumon… et il est roux !",
        )
        for joueur in (hote, invite):
            assurer_fiche(partie, joueur)
        etats = {case["nom"]: case["etat"] for groupe in demo.FICHE for case in groupe["cases"]}
        for case in CaseFiche.objects.filter(partie=partie, joueur=hote).select_related(
            "suspect", "objet", "lieu"
        ):
            element = case.suspect or case.objet or case.lieu
            case.etat = etats.get(element.nom, CaseFiche.Etat.INCONNU)
            case.save(update_fields=["etat"])

        return partie
