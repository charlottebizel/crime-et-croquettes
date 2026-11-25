---
id: LB-006
titre: Icône « œil » pour afficher ou masquer le mot de passe
statut: ouvert
membre: Loïc
branche: feature/oeil-mot-de-passe
créé: 2026-11-25
---
## Objectif

Sur les pages d'inscription et de connexion, permettre au joueur de voir ce qu'il tape dans les champs de mot de passe (moins d'erreurs, surtout sur téléphone).

## Critères d'acceptation

- [ ] Un bouton avec une icône d'œil à droite de chaque champ de mot de passe (connexion : 1 champ ; inscription : 2 champs).
- [ ] Un clic affiche le mot de passe en clair ; un second clic le masque à nouveau (l'icône change : œil / œil barré).
- [ ] Accessible : vrai `<button type="button">`, libellé lu par les lecteurs d'écran (« Afficher le mot de passe » / « Masquer le mot de passe »), état `aria-pressed`, utilisable au clavier, zone de clic d'au moins 44 px.
- [ ] Sans JavaScript, le champ reste un champ de mot de passe normal (pas de bouton inutile).
- [ ] Le bouton n'envoie pas le formulaire et n'est pas lu comme un champ par Django.
- [ ] Fait une seule fois, dans le composant commun `templates/composants/champ.html` : tous les futurs formulaires en profitent.
- [ ] Test : les pages de connexion et d'inscription contiennent le bouton ; le script ne casse pas la soumission.

## Notes

- 2026-11-25 : idée de Loïc en testant la connexion `admin`.
