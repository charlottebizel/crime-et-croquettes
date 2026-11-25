/* =====================================================================
   static/js/jeu/main.js — Point d'entrée de l'écran de partie (Vue 3)
   =====================================================================
   Chargé par templates/jeu/partie.html (<script type="module">).
   « vue » est résolu par la carte d'imports du template, qui pointe vers
   static/vendor/vue/vue.esm-browser.prod.js : pas de CDN, pas de build.

   Le template fournit deux réglages sur l'élément #app-partie :
     data-url-api    → adresse de l'API de la partie (ex. /api/parties/demo/)
     data-mode-demo  → "oui" pour la démo (actions serveur désactivées)
   ===================================================================== */

import { createApp } from "vue";

import EcranPartie from "./composants/EcranPartie.js";

const racine = document.getElementById("app-partie");

if (racine) {
  createApp(EcranPartie, {
    urlApi: racine.dataset.urlApi,
    modeDemo: racine.dataset.modeDemo === "oui",
  }).mount(racine);
}
