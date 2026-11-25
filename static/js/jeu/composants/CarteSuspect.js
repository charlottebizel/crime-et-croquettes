/* =====================================================================
   CarteSuspect.js — Fiche anthropométrique d'un suspect (photo + toise)
   =====================================================================
   Props : suspect (spec §6.2), actif (booléen : suspect interrogé).
   Événement : « choisir » quand on clique, pour l'interroger.
   ===================================================================== */

import ChatPortrait from "./ChatPortrait.js";
import { deuxChiffres } from "../outils.js";

export default {
  name: "CarteSuspect",
  components: { ChatPortrait },
  props: {
    suspect: { type: Object, required: true },
    actif: { type: Boolean, default: false },
  },
  emits: ["choisir"],
  computed: {
    numero() {
      return deuxChiffres(this.suspect.numero);
    },
  },
  template: `
    <button type="button"
            class="carte-suspect"
            :class="['stress--' + suspect.stress_niveau, { 'carte-suspect--active': actif }]"
            :aria-pressed="actif ? 'true' : 'false'"
            :aria-label="'Interroger ' + suspect.nom + ', ' + suspect.role + ', stress ' + suspect.stress + ' %'"
            @click="$emit('choisir', suspect.id)">
      <!-- Photo devant la toise (graduations dessinées en CSS) -->
      <span class="carte-suspect__photo" aria-hidden="true">
        <span class="carte-suspect__toise carte-suspect__toise--haut">1m20</span>
        <span class="carte-suspect__toise carte-suspect__toise--milieu">0m60</span>
        <span class="carte-suspect__chat">
          <ChatPortrait :apparence="suspect.apparence" label="" />
        </span>
        <span class="carte-suspect__numero">N° {{ numero }}</span>
      </span>

      <span class="carte-suspect__texte">
        <span class="carte-suspect__nom">{{ suspect.nom }}</span>
        <span class="carte-suspect__role">{{ suspect.role }}</span>
        <span class="carte-suspect__stress">
          <span class="machine">Stress</span>
          <span class="barre-stress"><span class="barre-stress__niveau" :style="{ width: suspect.stress + '%' }"></span></span>
        </span>
        <span v-if="suspect.interroge" class="carte-suspect__badge">Interrogé</span>
      </span>
    </button>
  `,
};
