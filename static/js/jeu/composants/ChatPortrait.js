/* =====================================================================
   ChatPortrait.js — Tête de chat dessinée en SVG
   =====================================================================
   Version Vue de templates/composants/chat.html (même dessin, mêmes
   couleurs par défaut, mêmes accessoires). Garder les deux en accord.

   Props :
     apparence  : { pelage, rayures, rayures_opacite, yeux, museau, accessoire }
                  (Suspect.apparence, spec §3.2). Absente = Inspecteur Moustache.
     accessoire : force l'accessoire (sinon apparence.accessoire).
                  couronne | serviette | pelote | monocle | bandana | inspecteur | aucun
     label      : texte lu par les lecteurs d'écran ("" = décoratif).

   Le SVG remplit son conteneur : c'est le parent qui fixe la taille.
   Sécurité : les couleurs viennent de l'IA ; le backend les valide
   (#RRGGBB, spec §7.3) et Vue échappe de toute façon les attributs.
   ===================================================================== */

export default {
  name: "ChatPortrait",
  props: {
    apparence: { type: Object, default: () => ({}) },
    accessoire: { type: String, default: "" },
    label: { type: String, default: "Portrait de chat" },
  },
  computed: {
    // Couleurs avec valeurs par défaut (celles de l'Inspecteur Moustache).
    c() {
      const a = this.apparence || {};
      return {
        pelage: a.pelage || "#D9A066",
        rayures: a.rayures || "#9C6A33",
        opacite: a.rayures_opacite ?? 1,
        yeux: a.yeux || "#7CC4A6",
        museau: a.museau || "#FBE9D0",
      };
    },
    acc() {
      return this.accessoire || (this.apparence && this.apparence.accessoire) || "aucun";
    },
  },
  template: `
    <svg class="chat" viewBox="0 0 100 100"
         :role="label ? 'img' : null" :aria-label="label || null" :aria-hidden="label ? null : 'true'">
      <!-- Oreilles -->
      <path d="M17 46 L20 7 L45 26 Z" :fill="c.pelage" stroke="#2B2320" stroke-width="2.6" stroke-linejoin="round"/>
      <path d="M83 46 L80 7 L55 26 Z" :fill="c.pelage" stroke="#2B2320" stroke-width="2.6" stroke-linejoin="round"/>
      <path d="M23 35 L24 17 L37 27 Z" fill="#F4A9A8"/>
      <path d="M77 35 L76 17 L63 27 Z" fill="#F4A9A8"/>
      <!-- Tête et rayures -->
      <ellipse cx="50" cy="57" rx="36" ry="31" :fill="c.pelage" stroke="#2B2320" stroke-width="2.6"/>
      <path d="M41 28 L43 38 M50 26 L50 38 M59 28 L57 38 M15 55 L24 57 M15 63 L24 62 M85 55 L76 57 M85 63 L76 62"
            fill="none" :stroke="c.rayures" stroke-width="3.6" stroke-linecap="round" :stroke-opacity="c.opacite"/>
      <!-- Museau, yeux -->
      <ellipse cx="50" cy="70" rx="15" ry="10.5" :fill="c.museau"/>
      <ellipse cx="36" cy="53" rx="8" ry="9" :fill="c.yeux" stroke="#2B2320" stroke-width="2"/>
      <ellipse cx="64" cy="53" rx="8" ry="9" :fill="c.yeux" stroke="#2B2320" stroke-width="2"/>
      <ellipse cx="36" cy="54" rx="2.6" ry="6.5" fill="#1E1A17"/>
      <ellipse cx="64" cy="54" rx="2.6" ry="6.5" fill="#1E1A17"/>
      <circle cx="38.5" cy="49.5" r="1.8" fill="#FFFFFF"/>
      <circle cx="66.5" cy="49.5" r="1.8" fill="#FFFFFF"/>
      <!-- Nez, bouche, moustaches -->
      <path d="M46 63 L54 63 L50 67.5 Z" fill="#E58C8C" stroke="#2B2320" stroke-width="1.5" stroke-linejoin="round"/>
      <path d="M50 67.5 Q50 72.5 44.5 72 M50 67.5 Q50 72.5 55.5 72" fill="none" stroke="#2B2320" stroke-width="1.8" stroke-linecap="round"/>
      <path d="M33 69 L11 65 M33 72 L11 74 M67 69 L89 65 M67 72 L89 74" stroke="#2B2320" stroke-width="1.5" stroke-linecap="round"/>

      <!-- Accessoires -->
      <g v-if="acc === 'couronne'">
        <path d="M27 52 Q36 41 45 52 Z" :fill="c.pelage" stroke="#2B2320" stroke-width="1.8"/>
        <path d="M55 52 Q64 41 73 52 Z" :fill="c.pelage" stroke="#2B2320" stroke-width="1.8"/>
        <path d="M33 27 L36 10 L43 19 L50 6 L57 19 L64 10 L67 27 Z" fill="#F2C14E" stroke="#2B2320" stroke-width="2.4" stroke-linejoin="round"/>
        <circle cx="50" cy="20" r="2.6" fill="#E06C75" stroke="#2B2320" stroke-width="1"/>
        <path d="M30 84 Q50 94 70 84" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-dasharray="0.1 5.5" stroke-linecap="round"/>
      </g>
      <g v-else-if="acc === 'serviette'">
        <path d="M32 83 Q50 79 68 83 L50 99 Z" fill="#FFFFFF" stroke="#2B2320" stroke-width="2.4" stroke-linejoin="round"/>
        <circle cx="44" cy="86" r="1.8" fill="#C8372D"/>
        <circle cx="55" cy="87" r="1.8" fill="#C8372D"/>
        <circle cx="50" cy="92" r="1.8" fill="#C8372D"/>
        <circle cx="58" cy="76" r="1.3" fill="#B06A2E"/>
        <circle cx="42" cy="77" r="1.1" fill="#B06A2E"/>
      </g>
      <g v-else-if="acc === 'pelote'">
        <path d="M56 73 Q66 82 75 80" fill="none" stroke="#E06C75" stroke-width="2.4" stroke-linecap="round"/>
        <circle cx="84" cy="85" r="11" fill="#E06C75" stroke="#2B2320" stroke-width="2.4"/>
        <path d="M76 80 Q84 84 80 94 M80 76 Q90 82 87 95 M86 75 Q94 80 94 88" fill="none" stroke="#2B2320" stroke-width="1.4"/>
      </g>
      <g v-else-if="acc === 'monocle'">
        <path d="M27 41 L42 44 M58 44 L73 41" stroke="#F4F1EC" stroke-width="3.6" stroke-linecap="round"/>
        <circle cx="64" cy="53" r="11.5" fill="#FFFFFF" fill-opacity="0.22" stroke="#C9A227" stroke-width="3"/>
        <path d="M75 58 Q81 72 77 92" fill="none" stroke="#C9A227" stroke-width="1.6"/>
      </g>
      <g v-else-if="acc === 'bandana'">
        <path d="M24 81 Q50 95 76 81 L71 91 Q50 102 29 91 Z" fill="#3E7CB1" stroke="#2B2320" stroke-width="2.4" stroke-linejoin="round"/>
        <circle cx="40" cy="91" r="1.5" fill="#FFFFFF"/>
        <circle cx="50" cy="94" r="1.5" fill="#FFFFFF"/>
        <circle cx="60" cy="91" r="1.5" fill="#FFFFFF"/>
        <rect x="17" y="19" width="16" height="6" rx="2" fill="#F3E1C7" stroke="#2B2320" stroke-width="1.5" transform="rotate(-35 25 22)"/>
      </g>
      <g v-else-if="acc === 'inspecteur'">
        <path d="M15 40 Q16 5 50 5 Q84 5 85 40 Q50 31 15 40 Z" fill="#9B7444" stroke="#2B2320" stroke-width="2.6" stroke-linejoin="round"/>
        <path d="M31 11 L28 36 M50 5 L50 33 M69 11 L72 36 M17 25 Q50 14 83 25" fill="none" stroke="#6E4F2A" stroke-width="2"/>
        <path d="M28 38 Q50 48 72 38 Q50 42 28 38 Z" fill="#7C5A32" stroke="#2B2320" stroke-width="2.2" stroke-linejoin="round"/>
        <path d="M27 72 Q37 61 50 67 Q63 61 73 72 Q65 70 59 73 Q54 74 50 70.5 Q46 74 41 73 Q35 70 27 72 Z" fill="#4A3426" stroke="#2B2320" stroke-width="1.5" stroke-linejoin="round"/>
      </g>
    </svg>
  `,
};
