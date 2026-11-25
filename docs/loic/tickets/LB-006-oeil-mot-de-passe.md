---
id: LB-006
titre: Icône « œil » pour afficher ou masquer le mot de passe
statut: en review
membre: Loïc
branche: revue-02/oeil-mot-de-passe
créé: 2026-11-25
---
## Objectif

Sur les pages d'inscription et de connexion, permettre au joueur de voir ce qu'il tape dans les champs de mot de passe (moins d'erreurs, surtout sur téléphone).

## Critères d'acceptation

- [x] Un bouton avec une icône d'œil à droite de chaque champ de mot de passe (connexion : 1 champ ; inscription : 2 champs).
- [x] Un clic affiche le mot de passe en clair ; un second clic le masque à nouveau (l'icône change : œil / œil barré).
- [x] Accessible : vrai `<button type="button">`, libellé fixe « Afficher le mot de passe » + état `aria-pressed` (bouton bascule : changer aussi le libellé ferait double emploi ; la bulle au survol, elle, dit « Masquer » quand c'est visible), utilisable au clavier, zone de clic d'au moins 44 px.
- [x] Sans JavaScript, le champ reste un champ de mot de passe normal (pas de bouton inutile).
- [x] Le bouton n'envoie pas le formulaire et n'est pas lu comme un champ par Django.
- [x] Fait une seule fois, dans le composant commun `templates/composants/champ.html` : tous les futurs formulaires en profitent.
- [x] Test : les pages de connexion et d'inscription contiennent le bouton ; le script ne casse pas la soumission.

## Notes

- 2026-11-25 : idée de Loïc en testant la connexion `admin`.
- 2026-11-25 : écrit par l'agent. Fichiers : `templates/composants/champ.html` (bouton écrit caché), `static/js/oeil.js` (nouveau, chargé par `base.html`), `static/css/theme.css`, 4 tests dans `comptes/tests.py`. Avant l'envoi du formulaire, le champ repasse en mode mot de passe (pas mémorisé comme texte). L'œil propre à Edge est masqué pour n'en garder qu'un. Sur le papier du dossier, l'icône prend les encres du thème (contraste 7,3:1) : le gris et l'ambre du fond de nuit y étaient trop pâles (2,4:1 et 1,8:1). Vérifié au navigateur : clic, clavier (Tab + Espace), connexion avec le mot de passe affiché, sans JavaScript, téléphone.
