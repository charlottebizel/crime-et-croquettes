# Crimes et Croquette

Un jeu d'enquête où des chats cherchent le coupable.

Le joueur incarne l'**Inspecteur Moustache**. Une IA génère une enquête (suspects, objets, lieux, pièces à conviction) et **interprète chaque chat suspect** pendant l'interrogatoire. Le joueur pose ses questions, tire des cartes, annote son carnet d'indices, barre ou valide sur sa fiche de déduction, puis accuse le coupable.

Projet 2 du cours 5IDEV — un produit avec l'IA au cœur.

## Équipe

| Membre | Rôle principal |
|---|---|
| Charlotte | Backend Django, dépôt GitHub, Render, Neon, CI/CD |
| Loïc | Frontend : templates Django, HTMX, CSS, illustrations |

Les rôles du cours (lead technique, référent QA, référent déploiement) tournent chaque semaine.

## Stack

- **Backend** : Python 3.12, Django 5
- **Frontend** : templates Django + HTMX (pas de framework JavaScript)
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
    └── _fragment.html        Fragments renvoyés à HTMX (préfixe _)

static/
└── css/
    └── theme.css             Variables de couleurs, polices et composants
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

### HTMX

HTMX est chargé dans `base.html`. Le jeton CSRF est envoyé automatiquement avec chaque requête HTMX (attribut `hx-headers` sur `<body>`), donc les `hx-post` fonctionnent sans rien ajouter.

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

## Historique des features

| Feature | Branche | Contenu |
|---|---|---|
| Gabarit de base | `feature/base-template` | `base.html`, thème CSS, décor de nuit, composant d'illustration des chats |
| Comptes | `feature/comptes` | Inscription, connexion, déconnexion, menu de l'entête, composants de formulaire, 9 tests |