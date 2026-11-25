# Crimes et Croquette

Un jeu d'enquête où des chats cherchent le coupable.

Le joueur incarne l'**Inspecteur Moustache**. Une IA génère une enquête (suspects, objets, lieux, pièces à conviction) et **interprète chaque chat suspect** pendant l'interrogatoire. Le joueur pose ses questions, tire des cartes, annote son carnet d'indices, barre ou valide sur sa fiche de déduction, puis accuse le coupable.

Projet 2 du cours 5IDEV — un produit avec l'IA au cœur.

## Équipe

| Membre | Rôle principal |
|---|---|
| Charlotte | Backend Django, dépôt GitHub, Render, Neon, CI/CD |
| Loïc | Frontend : écrans Vue 3, templates Django, CSS, illustrations |

Les rôles du cours (lead technique, référent QA, référent déploiement) tournent chaque semaine.

## Stack

- **Backend** : Python 3.12, Django 5
- **Frontend** : templates Django pour les pages de contenu, **Vue 3** pour les écrans de jeu (API JSON, sans étape de build, voir `docs/decisions/D-001-vue-ecrans-de-jeu.md`)
- **Base de données** : PostgreSQL sur Neon
- **Hébergement** : Render (gunicorn + WhiteNoise)
- **IA** : OpenRouter (appels uniquement côté serveur)
- **Qualité** : Ruff, pytest, GitHub Actions

Détails techniques et contrat backend ↔ frontend : [`docs/specification.md`](docs/specification.md).
Règles de travail sur le dépôt : [`CLAUDE.md`](CLAUDE.md).

## Installation locale

```bash
python -m venv .venv
# Windows : .venv\Scripts\activate    —    macOS/Linux : source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # puis compléter les valeurs (voir CLAUDE.md)
python manage.py migrate
python manage.py runserver
```

Le site est alors sur http://127.0.0.1:8000/.

## Workflow Git

- `main` = production : chaque merge déploie.
- Une branche `feature/<nom>` par fonctionnalité.
- Chaque Pull Request est **relue et approuvée par l'autre membre** avant le merge.

## Frontend

### Organisation des fichiers

```
templates/
├── base.html                 Gabarit commun à toutes les pages
├── composants/
│   ├── chat.html             Portrait de chat en SVG (suspects, inspecteur)
│   └── decor_nuit.html       Décor de fond (pluie, lune, ville)
└── <app>/                    Pages de chaque app (pages/, jeu/, comptes/…)

static/
├── css/
│   ├── theme.css             Variables de couleurs, polices et composants
│   └── partie.css            Écran de partie
├── js/gestion/               Application Vue du tableau de bord des coûts (admin)
├── js/jeu/                   Application Vue des écrans de jeu
│   ├── main.js               Point d'entrée (monte l'application sur #app-partie)
│   ├── api.js                lireJSON / envoyerJSON (CSRF, erreurs lisibles)
│   ├── outils.js             Petites fonctions partagées
│   └── composants/           EcranPartie, Interrogatoire, CarteSuspect, JaugeStress,
│                             Compteurs, PieceConviction, EntreeCarnet,
│                             FicheDeduction, ChatPortrait
└── vendor/vue/               Vue 3.5.13 (vue.esm-browser.prod.js + licence MIT)
```

### Créer une page

Toute page hérite de `base.html` :

```django
{% extends "base.html" %}

{% block titre %}Mes parties · Crimes et Croquette{% endblock %}

{% block contenu %}
  <h1>Mes parties</h1>
  ...
{% endblock %}
```

Blocs disponibles : `titre`, `description`, `head_extra`, `entete`, `nav`, `contenu`, `scripts`.

### Thème « nuit et polar »

Toutes les couleurs et polices sont des variables CSS dans `static/css/theme.css` (section 1). On n'écrit jamais une couleur en dur dans une page.

| Variable | Usage |
|---|---|
| `--nuit`, `--nuit-2`, `--nuit-3` | Fonds sombres |
| `--texte`, `--texte-doux` | Textes sur fond sombre |
| `--ambre` | Action principale (lumière de la lampe) |
| `--rouge` | Accusation, tampons, erreurs |
| `--vert` | Calme, validé |
| `--papier`, `--kraft`, `--encre` | Carnet, dossiers, pièces à conviction |

| Police | Usage |
|---|---|
| Bebas Neue | Titres façon tampon |
| Special Elite | Dépositions, dossiers (machine à écrire) |
| Caveat | Notes manuscrites de l'inspecteur |
| Inter | Texte courant |

Composants CSS prêts à l'emploi : `.btn`, `.btn--ambre`, `.btn--tampon`, `.panneau`, `.titre-section`, `.papier`, `.machine`, `.manuscrit`, `.tampon`, `.mention-ia`, `.champ`, `.etiquette`, `.sr-only`.

### Illustrer un chat

```django
{# Un suspect : son apparence vient de la base (Suspect.apparence) #}
<div style="width: 120px; height: 120px">
  {% include "composants/chat.html" with apparence=suspect.apparence label=suspect.nom %}
</div>

{# L'inspecteur (couleurs par défaut) #}
{% include "composants/chat.html" with accessoire="inspecteur" label="Inspecteur Moustache" %}
```

Accessoires disponibles : `couronne`, `serviette`, `pelote`, `monocle`, `bandana`, `inspecteur`, `aucun`.

### Vue 3 (écrans de jeu)

- **Pas de build** : Vue est dans `static/vendor/vue/`. Le template de l'écran déclare une carte d'imports (`<script type="importmap">`) qui fait pointer `import … from "vue"` vers ce fichier, puis charge `static/js/jeu/main.js` en module.
- **Un composant = un fichier JS** dans `static/js/jeu/composants/`, qui exporte un objet Vue (`props`, `data`, `computed`, `methods`, `template` en chaîne). Les composants s'importent entre eux avec des chemins relatifs (`./ChatPortrait.js`) ; un test pytest vérifie que chaque import pointe vers un fichier existant.
- **Données** : le template passe l'adresse de l'API dans `data-url-api` ; Vue lit tout le reste en JSON (spec §5.4). Les écritures passent par `envoyerJSON()`, qui ajoute l'en-tête `X-CSRFToken`.
- **Erreurs** : l'API renvoie `{"erreur": {"type", "message"}}` ; Vue affiche le message et garde la saisie du joueur.
- **Dessin des chats** : `ChatPortrait.js` (Vue) est la copie de `templates/composants/chat.html` (Django) : toute modification se fait dans les deux.

### Formulaires

Chaque champ s'affiche avec le composant commun (libellé, aide, erreurs) :

```django
<form method="post" novalidate>
  {% csrf_token %}
  {% include "composants/erreurs_formulaire.html" %}
  {% for champ in form %}
    {% include "composants/champ.html" with champ=champ %}
  {% endfor %}
  <button class="btn btn--ambre btn--large" type="submit">Valider</button>
</form>
```

Les pages de formulaire utilisent le style « dossier » (`.page-formulaire`, `.dossier`, `.dossier__onglet`, `.dossier__tampon`, `.dossier__titre`).

### Accessibilité et transparence IA

- Lien « Aller au contenu », contour de focus visible, textes alternatifs sur les illustrations.
- Le pied de page rappelle sur toutes les pages que les suspects sont interprétés par une IA, avec un lien vers la page légale.
- Chaque réponse du modèle doit afficher la mention `<span class="mention-ia">Généré par IA</span>`.

## Comptes joueurs

| Page | URL | Nom Django |
|---|---|---|
| Inscription | `/comptes/inscription/` | `comptes:inscription` |
| Connexion | `/comptes/connexion/` | `comptes:connexion` |
| Déconnexion (POST uniquement) | `/comptes/deconnexion/` | `comptes:deconnexion` |

- L'inscription demande un nom d'agent, un e-mail unique et un mot de passe (règles de sécurité de Django), puis connecte le joueur directement.
- Le rôle administrateur n'est jamais donné à l'inscription : il se donne avec `python manage.py createsuperuser` ou dans l'admin Django.
- Après connexion ou déconnexion, on revient à l'accueil (`LOGIN_REDIRECT_URL` et `LOGOUT_REDIRECT_URL` dans `config/settings.py`).

### Tests

```bash
python manage.py test comptes      # ou : pytest
```

Les tests utilisent le stockage de fichiers statiques simple de Django (`override_settings`), car le stockage WhiteNoise de production exige `collectstatic`.

## Données de démonstration

```bash
python manage.py charger_demo                  # crée ce qui manque (sans danger si relancé)
python manage.py charger_demo --reinitialiser  # efface l'enquête de démo puis la recrée
```

Crée trois comptes (`admin`, `moustache` en Pro, `joueur` en Free), l'enquête « Qui a volé le saumon du dimanche ? » en base et une partie en cours (code `SAUMON42`). Le mot de passe des comptes est lu dans la variable d'environnement `DEMO_MOT_DE_PASSE` (à mettre dans `.env`) ; sans elle, il est tiré au hasard et affiché une seule fois. Aucun appel à l'IA.

Connectez-vous en `moustache`, puis **Mes parties** → **Reprendre l'enquête** : c'est l'écran de jeu Vue, branché sur la base de données.

## Mes parties et vraies parties

- `/parties/` (`jeu:liste`) : les enquêtes du joueur connecté.
- `/parties/<pk>/` (`jeu:partie`) : la même application Vue que la démo, avec l'API `/api/parties/<pk>/` (lecture : `jeu/lecture.py`).
- Accès : connexion obligatoire, et seulement les parties où l'on joue (sinon 404, la partie « n'existe pas » pour les autres).
- Les écritures (question, carte, avis, fiche, accusation) arrivent ensuite (spec §5.4).

## Tableau de bord des coûts (administrateurs)

- `/gestion/couts/` (`gestion:couts`), lien **Coûts IA** dans le menu des administrateurs.
- Chiffres calculés par `gestion/statistiques.py` à partir du journal `ia.AppelIA` ; API `/api/gestion/couts/?jours=7|30|90`.
- Écran Vue (`static/js/gestion/`) : tuiles (coût, appels et échecs, coût moyen d'une question et d'une génération, budget consommé depuis le début), histogramme du coût par jour (survol ou clavier, tableau jour par jour), consommation par joueur, 20 derniers appels.
- **Montants en euros.** OpenRouter facture en dollars : le journal garde le coût exact en dollars et l'écran convertit avec le taux du jour de la BCE, demandé à l'API gratuite [Frankfurter](https://frankfurter.dev) (`gestion/taux.py`, sans clé, mis en cache 6 h). Si l'API ne répond pas, le taux de secours `TAUX_USD_POUR_1_EUR` du `.env` est utilisé et l'écran l'indique. `TAUX_CHANGE_URL` vide = jamais d'appel à l'API.
- La tuile « Depuis le début du projet » montre la part consommée du budget `BUDGET_IA_EUR` (1 € par défaut), avec une jauge qui passe au rouge à 80 %.
- Avec le faux fournisseur d'IA (développement, tests), chaque appel coûte 0 € : les coûts réels apparaissent avec OpenRouter.

## Écran de partie (démo)

Page : `/parties/demo/` (`jeu:partie_demo`), publique, sans base de données ni IA ; accessible depuis le bouton « Lancer l'enquête de démo » de l'accueil. Paramètre `?suspect=<id>` pour ouvrir un suspect.

- La page (`templates/jeu/partie.html`) n'est qu'une coquille : l'écran est l'application Vue de `static/js/jeu/`.
- API de démo : `GET /api/parties/demo/` (état de la partie) et `GET /api/parties/demo/suspects/<id>/` (un suspect et sa conversation), dans `jeu/api.py`. Données en dur dans `jeu/demo.py`, au format de la spec §6.
- En démo : changer de suspect, onglets Carnet / Fiche (clavier compris), avis sur les témoignages et cases de la fiche fonctionnent dans le navigateur, sans être enregistrés. Questions, cartes et accusation sont inactives.
- Le code des vraies actions (question, carte, avis, fiche) est déjà dans `EcranPartie.js` : il appellera les endpoints de la spec §5.4 quand Charlotte les aura écrits.

## Historique des features

| Feature | Branche | Contenu |
|---|---|---|
| Gabarit de base | `feature/base-template` | `base.html`, thème CSS, décor de nuit, composant d'illustration des chats |
| Comptes | `feature/comptes` | Inscription, connexion, déconnexion, menu de l'entête, composants de formulaire, 9 tests |
| Écran de partie (démo) | `feature/ecran-partie` | Écran de jeu en données en dur, fragments HTMX (remplacés par Vue, voir plus bas), onglets carnet / fiche, 17 tests |
| Écran de partie en Vue | `feature/vue-ecran-partie` | Décision D-001 : écran de partie en Vue 3 sans build, API JSON de démo, HTMX retiré, 18 tests |
| Revue n°2 | `feature/revue-2` | `charger_demo`, Mes parties et vraies parties en lecture, tableau de bord des coûts (Vue), 28 tests |
