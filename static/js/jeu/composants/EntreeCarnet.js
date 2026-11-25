/* =====================================================================
   EntreeCarnet.js — Une entrée du carnet d'indices
   =====================================================================
   Props : entree (spec §6.4).
   Événement : « avis » (valeur "fiable" | "douteux" | "faux" | null)
   quand le joueur clique sur un tampon. Recliquer sur l'avis choisi
   l'enlève (null).

   - Témoignage : résumé par l'IA à partir d'une réponse ; le joueur juge.
   - Preuve : vient d'une carte tirée, toujours vraie, pas d'avis.
   ===================================================================== */

const AVIS = [
  { valeur: "fiable", libelle: "Fiable" },
  { valeur: "douteux", libelle: "Douteux" },
  { valeur: "faux", libelle: "Faux" },
];

export default {
  name: "EntreeCarnet",
  props: {
    entree: { type: Object, required: true },
  },
  emits: ["avis"],
  data() {
    return { choix: AVIS };
  },
  computed: {
    estPreuve() {
      return this.entree.type === "preuve";
    },
  },
  methods: {
    basculer(valeur) {
      this.$emit("avis", this.entree.avis === valeur ? null : valeur);
    },
  },
  template: `
    <article class="entree"
             :class="['entree--' + entree.type, entree.avis ? 'entree--avis-' + entree.avis : '']">
      <span class="entree__scotch" aria-hidden="true"></span>

      <div class="entree__haut">
        <span class="entree__type">{{ estPreuve ? "Preuve" : "Témoignage" }}</span>
        <span class="entree__source machine">{{ entree.source }}</span>
        <span v-if="entree.est_nouvelle" class="tampon entree__nouveau">Nouveau</span>
      </div>

      <p class="entree__texte machine">{{ entree.texte }}</p>
      <p class="entree__liens">Lié à : {{ entree.liens }}</p>

      <template v-if="!estPreuve">
        <div class="avis" role="group" aria-label="Votre avis sur ce témoignage">
          <button v-for="a in choix" :key="a.valeur" type="button"
                  class="avis__bouton" :class="'avis__bouton--' + a.valeur"
                  :aria-pressed="entree.avis === a.valeur ? 'true' : 'false'"
                  @click="basculer(a.valeur)">{{ a.libelle }}</button>
        </div>
        <p v-if="entree.note" class="manuscrit entree__note">→ {{ entree.note }}</p>
        <p class="mention-ia">Résumé rédigé par IA à partir de la réponse du suspect.</p>
      </template>
      <p v-else class="entree__vraie machine">Pièce à conviction : toujours vraie</p>
    </article>
  `,
};
