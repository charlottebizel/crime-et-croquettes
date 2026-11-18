/* =====================================================================
   static/js/partie.js — Écran de partie
     1. Onglets « Carnet d'indices / Fiche de déduction ».
     2. La conversation s'ouvre défilée jusqu'au dernier échange.
   =====================================================================
   Amélioration progressive : sans JavaScript, les deux panneaux restent
   affichés l'un sous l'autre. Avec JavaScript, on montre les onglets et
   on n'affiche qu'un panneau à la fois, comme dans la maquette.

   Accessibilité (modèle « tabs » du W3C) :
     - les onglets ont role="tab", aria-selected et aria-controls ;
     - flèches gauche/droite, Début et Fin pour passer d'un onglet à l'autre ;
     - seul l'onglet actif est dans l'ordre de tabulation (tabindex).

   Le dernier onglet ouvert est mémorisé dans le navigateur (localStorage),
   entouré de try/catch : en navigation privée, ça peut échouer sans gêne.
   ===================================================================== */

(function () {
  "use strict";

  var CLE_MEMOIRE = "cc-onglet-partie";

  function activerOnglets(conteneur) {
    var liste = conteneur.querySelector("[role='tablist']");
    if (!liste) {
      return;
    }
    var onglets = Array.prototype.slice.call(liste.querySelectorAll("[role='tab']"));

    // Affiche ou cache les panneaux selon l'onglet choisi.
    function choisir(onglet, donnerFocus) {
      onglets.forEach(function (autre) {
        var actif = autre === onglet;
        var panneau = document.getElementById(autre.getAttribute("aria-controls"));
        autre.setAttribute("aria-selected", actif ? "true" : "false");
        autre.tabIndex = actif ? 0 : -1;
        if (panneau) {
          panneau.hidden = !actif;
        }
      });
      if (donnerFocus) {
        onglet.focus();
      }
      try {
        window.localStorage.setItem(CLE_MEMOIRE, onglet.id);
      } catch (e) {
        /* stockage indisponible : on ignore */
      }
    }

    onglets.forEach(function (onglet, index) {
      onglet.addEventListener("click", function () {
        choisir(onglet, false);
      });
      onglet.addEventListener("keydown", function (evenement) {
        var cible = null;
        if (evenement.key === "ArrowRight") {
          cible = onglets[(index + 1) % onglets.length];
        } else if (evenement.key === "ArrowLeft") {
          cible = onglets[(index - 1 + onglets.length) % onglets.length];
        } else if (evenement.key === "Home") {
          cible = onglets[0];
        } else if (evenement.key === "End") {
          cible = onglets[onglets.length - 1];
        }
        if (cible) {
          evenement.preventDefault();
          choisir(cible, true);
        }
      });
    });

    // Onglet de départ : celui mémorisé, sinon le premier (le carnet).
    var memorise = null;
    try {
      memorise = document.getElementById(window.localStorage.getItem(CLE_MEMOIRE) || "");
    } catch (e) {
      memorise = null;
    }
    var depart = onglets.indexOf(memorise) >= 0 ? memorise : onglets[0];

    liste.hidden = false;
    conteneur.classList.add("onglets--actifs");
    choisir(depart, false);
  }

  document.querySelectorAll("[data-onglets]").forEach(activerOnglets);

  // La conversation s'ouvre sur le dernier échange (le plus récent est en bas).
  var conversation = document.getElementById("conversation");
  if (conversation) {
    conversation.scrollTop = conversation.scrollHeight;
  }
})();
