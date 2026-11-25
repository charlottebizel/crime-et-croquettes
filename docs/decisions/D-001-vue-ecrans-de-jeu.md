---
id: D-001
titre: Les écrans de jeu sont des applications Vue 3 qui lisent une API JSON ; Django garde les pages de contenu
statut: acceptée
proposée-par: Loïc
date: 2026-11-25
---
## Contexte

À la revue n°1 (17/11), le professeur demande un vrai framework frontend (« comme Vue.js ») à la place des templates Django + HTMX. Le projet 1 était en React : Vue respecte la contrainte « changer de framework frontend ». Il reste 5 semaines avant la remise, et l'écran de partie (LB-001) existe déjà en templates.

## Décision

- **Option A** : Django rend les pages de contenu (accueil, comptes, page légale, tarifs) ; les écrans interactifs (partie, puis nouvelle enquête, mes parties, tableau de bord des coûts) sont des applications **Vue 3**.
- Les écrans Vue lisent et écrivent leurs données par une **API JSON** (`/api/…`, spec §5.4) écrite en Django simple (`JsonResponse`), avec la session et le CSRF de Django.
- **Pas d'étape de build** : Vue 3.5.13 (`vue.esm-browser.prod.js`, licence MIT) est copié dans `static/vendor/vue/` et chargé par une carte d'imports ; les composants sont des modules JavaScript (`static/js/jeu/`). Rien à changer sur Render ni dans le CI.
- HTMX est retiré.

## Écarté

- **Option B, application Vue complète (SPA) avec Vue Router et Pinia** : tout le front à refaire (connexion, routage, pages de contenu), plus de travail à 5 semaines de la remise, et trop proche de l'architecture du projet 1.
- **Vite et fichiers `.vue`** : demande Node.js et `npm run build` sur Render et dans le CI (réglages de l'hébergeur à modifier) pour un gain limité à notre échelle. Reste possible plus tard sans changer les composants.
- **Vue depuis un CDN** : dépendance à un service extérieur le jour de la démo, et transmission de l'adresse IP des visiteurs à un tiers (RGPD).
- **Django REST Framework ou django-ninja** : utiles pour une grosse API ; pour sept endpoints, `JsonResponse` suffit et n'ajoute aucune dépendance.

## Conséquences

- Backend (Charlotte) : les vues du jeu prévues en fragments HTMX deviennent des endpoints JSON (spec §5.4), qui appellent `jeu/services.py`. Les clés JSON sont celles du §6 : rien à réinventer.
- Frontend (Loïc) : les composants Vue de l'écran de partie sont faits (LB-002) et contiennent déjà le code des appels POST (question, carte, avis, fiche), testé avec des réponses simulées.
- Le dessin des chats existe en double : `templates/composants/chat.html` (pages Django) et `ChatPortrait.js` (Vue). Toute modification se fait dans les deux.
- Les tests Python vérifient ce que le serveur fournit à Vue (page, API, fichiers JS) ; le rendu et les clics se vérifient dans le navigateur.
- La tâche du plan « Fragment d'erreur, saisie conservée » (S4) devient : messages d'erreur de l'API affichés par Vue (déjà en place côté front).
