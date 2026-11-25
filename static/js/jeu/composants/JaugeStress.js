/* =====================================================================
   JaugeStress.js — Grande jauge de stress de la salle d'interrogatoire
   =====================================================================
   Props : suspect (spec §6.2 : stress 0–100, stress_niveau).
   Le stress est renvoyé par l'IA dans son JSON, validé et stocké par le
   serveur : ici on l'affiche seulement, sans appel au modèle (le « Z »
   de l'exigence O1).
   ===================================================================== */

import { libelleStress } from "../outils.js";

export default {
  name: "JaugeStress",
  props: {
    suspect: { type: Object, required: true },
  },
  computed: {
    libelle() {
      return libelleStress(this.suspect.stress_niveau);
    },
  },
  template: `
    <div class="jauge-stress" :class="'stress--' + suspect.stress_niveau">
      <div class="jauge-stress__haut">
        <span class="jauge-stress__titre">Stress</span>
        <span class="jauge-stress__valeur machine">{{ suspect.stress }} %</span>
      </div>
      <!-- role="meter" : les lecteurs d'écran annoncent une valeur entre 0 et 100 -->
      <div class="barre-stress barre-stress--grande" role="meter"
           aria-valuemin="0" aria-valuemax="100" :aria-valuenow="suspect.stress"
           :aria-label="'Stress de ' + suspect.nom">
        <span class="barre-stress__niveau" :style="{ width: suspect.stress + '%' }"></span>
      </div>
      <span class="jauge-stress__libelle">{{ libelle }}</span>
    </div>
  `,
};
