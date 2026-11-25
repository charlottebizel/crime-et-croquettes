/* =====================================================================
   PieceConviction.js — Une pièce à conviction tirée (étiquette kraft)
   =====================================================================
   Props : carte ({ code, titre, texte, etiquette }).
   Les cartes sont tirées par notre code, jamais par l'IA : toujours vraies.
   ===================================================================== */

export default {
  name: "PieceConviction",
  props: {
    carte: { type: Object, required: true },
  },
  template: `
    <article class="piece">
      <span class="piece__oeillet" aria-hidden="true"></span>
      <p class="piece__code machine">Pièce n° {{ carte.code }}</p>
      <h3 class="piece__titre">{{ carte.titre }}</h3>
      <p class="piece__texte machine">{{ carte.texte }}</p>
      <p class="piece__etiquette">{{ carte.etiquette }}</p>
    </article>
  `,
};
