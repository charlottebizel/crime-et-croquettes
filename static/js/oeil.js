/* =====================================================================
   static/js/oeil.js — Bouton « œil » des champs de mot de passe (LB-006)
   =====================================================================
   Chargé sur toutes les pages par templates/base.html (defer : le script
   s'exécute quand la page est prête). Le bouton lui-même est écrit par
   templates/composants/champ.html, caché (attribut hidden) :
     - sans JavaScript, il reste caché → champ de mot de passe normal ;
     - avec JavaScript, ce script l'affiche et le rend utile.

   Accessibilité : bouton à bascule = libellé FIXE (« Afficher le mot de
   passe ») + état aria-pressed (true quand le mot de passe est visible).
   Un lecteur d'écran annonce « Afficher le mot de passe, bouton bascule,
   activé ». Changer aussi le libellé ferait double emploi avec l'état.
   ===================================================================== */

(function () {
  "use strict";

  document.querySelectorAll("[data-oeil]").forEach(function (bouton) {
    var champ = document.getElementById(bouton.dataset.oeil);
    if (!champ) {
      return;
    }
    bouton.hidden = false;

    bouton.addEventListener("click", function () {
      var afficher = champ.type === "password";
      champ.type = afficher ? "text" : "password";
      bouton.setAttribute("aria-pressed", afficher ? "true" : "false");
      // Bulle au survol de la souris (le libellé lu reste le même).
      bouton.title = afficher ? "Masquer le mot de passe" : "Afficher le mot de passe";
    });

    // Avant l'envoi, on remet le champ en mode « mot de passe » : le
    // navigateur ne doit pas le mémoriser comme un texte ordinaire
    // (historique de saisie) et le gestionnaire de mots de passe le
    // reconnaît bien.
    if (champ.form) {
      champ.form.addEventListener("submit", function () {
        champ.type = "password";
        bouton.setAttribute("aria-pressed", "false");
      });
    }
  });
})();
