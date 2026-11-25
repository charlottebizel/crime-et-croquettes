/* =====================================================================
   static/js/gestion/main.js — Point d'entrée du tableau de bord des coûts (Vue 3)
   =====================================================================
   Chargé par templates/gestion/couts.html. Le template fournit l'adresse
   de l'API sur #app-couts (data-url-api). Réservé aux administrateurs :
   le serveur le vérifie sur la page ET sur l'API.
   ===================================================================== */

import { createApp } from "vue";

import TableauCouts from "./composants/TableauCouts.js";

const racine = document.getElementById("app-couts");

if (racine) {
  createApp(TableauCouts, { urlApi: racine.dataset.urlApi }).mount(racine);
}
