/* =====================================================================
   Compteurs.js — Questions posées et pièces tirées
   =====================================================================
   Props : compteurs (spec §6.6). Le nombre de questions est le quota du
   palier (exigence O4) : le joueur voit ce qui lui reste.
   ===================================================================== */

export default {
  name: "Compteurs",
  props: {
    compteurs: { type: Object, required: true },
  },
  template: `
    <div class="compteurs">
      <span class="compteur" title="Questions posées dans cette partie">
        <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M4 5h16v11H10l-5 4v-4H4z"/></svg>
        <span class="machine">{{ compteurs.questions_posees }} / {{ compteurs.questions_max }}</span>
        <span class="sr-only">questions posées</span>
      </span>
      <span class="compteur" title="Pièces à conviction tirées">
        <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M4 4h10l6 6v10H4z"/><path d="M14 4v6h6"/></svg>
        <span class="machine">{{ compteurs.cartes_tirees }} / {{ compteurs.cartes_max }}</span>
        <span class="sr-only">pièces tirées</span>
      </span>
    </div>
  `,
};
