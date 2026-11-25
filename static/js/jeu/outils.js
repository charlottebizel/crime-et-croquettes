/* =====================================================================
   static/js/jeu/outils.js — Petites fonctions partagées par les composants
   ===================================================================== */

/** Message affiché sur les actions pas encore branchées en démo. */
export const TITRE_INACTIF_DEMO = "Disponible quand le jeu sera branché";

/** Libellé du niveau de stress (seuils de la spec §6.2, calculés par le serveur). */
export function libelleStress(niveau) {
  if (niveau === "nerveux") {
    return "Nerveux : il cache quelque chose ?";
  }
  if (niveau === "mal_a_l_aise") {
    return "Mal à l'aise";
  }
  return "Calme";
}

/** Numéro sur deux chiffres : 2 → "02" (étiquette des fiches suspects). */
export function deuxChiffres(nombre) {
  return String(nombre).padStart(2, "0");
}
