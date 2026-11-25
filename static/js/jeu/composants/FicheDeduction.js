/* =====================================================================
   FicheDeduction.js — Fiche de déduction (suspects, objets, lieux)
   =====================================================================
   Props : fiche (spec §6.5 : 3 groupes de cases { id, nom, etat }).
   Événement : « tourner » (case) quand le joueur clique sur une case :
   inconnu → barré → validé → inconnu. Rien ici n'appelle l'IA.
   ===================================================================== */

const LIBELLES = { inconnu: "Inconnu", barre: "Barré", valide: "Validé" };
const MARQUES = { inconnu: "", barre: "✕", valide: "✓" };

export default {
  name: "FicheDeduction",
  props: {
    fiche: { type: Array, required: true },
  },
  emits: ["tourner"],
  methods: {
    libelle(etat) {
      return LIBELLES[etat] || etat;
    },
    marque(etat) {
      return MARQUES[etat] || "";
    },
  },
  template: `
    <div class="fiche__papier">
      <p class="manuscrit">Je barre, je valide… rien ici n'appelle l'IA.</p>
      <div v-for="groupe in fiche" :key="groupe.type" class="fiche__groupe">
        <h3 class="fiche__titre">{{ groupe.titre }}</h3>
        <button v-for="c in groupe.cases" :key="c.id" type="button"
                class="case" :class="'case--' + c.etat"
                :aria-label="c.nom + ' : ' + libelle(c.etat) + '. Cliquer pour changer.'"
                @click="$emit('tourner', c)">
          <span class="case__marque" aria-hidden="true">{{ marque(c.etat) }}</span>
          <span class="case__nom">{{ c.nom }}</span>
          <span class="case__etat">{{ libelle(c.etat) }}</span>
        </button>
      </div>
    </div>
  `,
};
