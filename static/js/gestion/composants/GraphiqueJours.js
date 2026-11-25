/* =====================================================================
   GraphiqueJours.js — Histogramme du coût de l'IA par jour
   =====================================================================
   Props : jours (spec §6.7 par_jour, avec en plus « montant » : le coût
           du jour déjà converti en euros par TableauCouts).
           [{ date, montant, nb_appels, nb_echecs }]

   Un seul jeu de données → une seule couleur, pas de légende (le titre
   de la carte dit ce qui est tracé). Règles suivies (skill dataviz) :
     - barres fines (≤ 24 px), bout arrondi de 4 px, posées sur une ligne
       de base unique ; grille horizontale fine et discrète ;
     - graduations « rondes » sur l'axe vertical (pas de 1, 2 ou 5 × 10ⁿ) ;
     - dessiné en vrais pixels (largeur mesurée) : le texte garde sa
       taille sur ordinateur comme sur téléphone ;
     - survol OU focus clavier d'une barre → bulle avec la date, le coût,
       le nombre d'appels et d'échecs (zone de survol = toute la colonne) ;
     - la couleur des barres (#C98A2A) passe le contrôle de luminosité et
       de contraste sur le fond sombre ; le texte reste dans les couleurs
       de texte du thème, jamais dans la couleur des barres.
   Un tableau des mêmes chiffres est proposé à côté (accessibilité).
   ===================================================================== */

import { euros, jourCourt, nombre } from "../format.js";

const HAUTEUR = 240;
const MARGE = { haut: 16, droite: 12, bas: 28, gauche: 76 };
const NB_INTERVALLES = 4;

/** Pas « rond » de l'axe : 1, 2 ou 5 × 10ⁿ, juste au-dessus de maximum / 4. */
function pasRond(maximum) {
  const brut = (maximum || 0.004) / NB_INTERVALLES;
  const puissance = 10 ** Math.floor(Math.log10(brut));
  for (const multiple of [1, 2, 5, 10]) {
    if (multiple * puissance >= brut) {
      return multiple * puissance;
    }
  }
  return 10 * puissance;
}

export default {
  name: "GraphiqueJours",
  props: {
    jours: { type: Array, required: true },
  },
  data() {
    return { survole: null, largeur: 720, hauteur: HAUTEUR, marge: MARGE };
  },
  mounted() {
    // La largeur réelle du conteneur, mise à jour quand la fenêtre change de taille.
    this.observateur = new ResizeObserver(() => {
      this.largeur = Math.max(280, this.$el.clientWidth);
    });
    this.observateur.observe(this.$el);
  },
  beforeUnmount() {
    this.observateur.disconnect();
  },
  computed: {
    plusHaut() {
      return Math.max(...this.jours.map((j) => j.montant), 0);
    },
    pas() {
      return pasRond(this.plusHaut);
    },
    intervalles() {
      // L'axe s'arrête à la première graduation ronde au-dessus de la plus haute barre.
      return Math.max(1, Math.ceil(this.plusHaut / this.pas));
    },
    maximum() {
      return this.pas * this.intervalles;
    },
    zone() {
      return {
        largeur: this.largeur - MARGE.gauche - MARGE.droite,
        hauteur: HAUTEUR - MARGE.haut - MARGE.bas,
      };
    },
    graduations() {
      return Array.from({ length: this.intervalles + 1 }, (_, i) => {
        const valeur = this.pas * i;
        return {
          valeur,
          y: MARGE.haut + this.zone.hauteur * (1 - i / this.intervalles),
          texte: euros(valeur),
        };
      });
    },
    barres() {
      const bande = this.zone.largeur / this.jours.length;
      const epaisseur = Math.min(24, bande * 0.6);
      const base = MARGE.haut + this.zone.hauteur;
      // Une étiquette de date tous les ~90 px pour ne pas surcharger l'axe.
      const nbEtiquettes = Math.max(2, Math.floor(this.zone.largeur / 90));
      const pasEtiquette = Math.max(1, Math.ceil(this.jours.length / nbEtiquettes));
      return this.jours.map((jour, i) => {
        const h = (jour.montant / this.maximum) * this.zone.hauteur;
        const x = MARGE.gauche + i * bande + (bande - epaisseur) / 2;
        return {
          ...jour,
          index: i,
          xBande: MARGE.gauche + i * bande,
          largeurBande: bande,
          centre: MARGE.gauche + i * bande + bande / 2,
          chemin: h > 0 ? this.cheminBarre(x, base, epaisseur, h) : "",
          etiquette: i % pasEtiquette === 0 || i === this.jours.length - 1 ? jourCourt(jour.date) : "",
          description:
            jourCourt(jour.date) + " : " + euros(jour.montant) + ", " + nombre(jour.nb_appels) +
            " appel" + (jour.nb_appels > 1 ? "s" : "") +
            (jour.nb_echecs ? ", " + jour.nb_echecs + " échec" + (jour.nb_echecs > 1 ? "s" : "") : ""),
        };
      });
    },
    bulle() {
      if (this.survole === null) {
        return null;
      }
      const b = this.barres[this.survole];
      // Garde la bulle dans le graphique, même pour les barres du bord.
      const gauche = Math.min(Math.max(b.centre, 70), this.largeur - 70);
      return { ...b, gauche };
    },
    toutAZero() {
      return this.jours.every((j) => !j.montant);
    },
  },
  methods: {
    // Fonctions de format, utilisables dans le template.
    euros,
    nombre,
    jourCourt,
    /** Barre avec un bout arrondi de 4 px en haut, carrée sur la ligne de base. */
    cheminBarre(x, base, l, h) {
      const r = Math.min(4, h, l / 2);
      const haut = base - h;
      return (
        `M${x},${base} L${x},${haut + r} Q${x},${haut} ${x + r},${haut} ` +
        `L${x + l - r},${haut} Q${x + l},${haut} ${x + l},${haut + r} L${x + l},${base} Z`
      );
    },
  },
  template: `
    <div class="graphique">
      <svg class="graphique__svg" :width="largeur" :height="hauteur" :viewBox="'0 0 ' + largeur + ' ' + hauteur" role="group"
           aria-label="Coût de l'IA par jour, en euros" @mouseleave="survole = null">
        <!-- Grille et graduations -->
        <g aria-hidden="true">
          <g v-for="g in graduations" :key="g.valeur">
            <line :x1="marge.gauche" :x2="largeur - marge.droite" :y1="g.y" :y2="g.y" class="graphique__grille" />
            <text :x="marge.gauche - 8" :y="g.y + 4" text-anchor="end" class="graphique__texte">{{ g.texte }}</text>
          </g>
        </g>
        <!-- Barres : la zone de survol couvre toute la colonne du jour -->
        <g v-for="b in barres" :key="b.date" class="graphique__colonne"
           :class="{ 'graphique__colonne--active': survole === b.index }"
           tabindex="0" role="img" :aria-label="b.description"
           @mouseenter="survole = b.index" @focus="survole = b.index" @blur="survole = null">
          <rect :x="b.xBande" :y="marge.haut" :width="b.largeurBande" :height="hauteur - marge.haut - marge.bas" class="graphique__cible" />
          <path v-if="b.chemin" :d="b.chemin" class="graphique__barre" />
          <text v-if="b.etiquette" :x="b.centre" :y="hauteur - 8" text-anchor="middle" class="graphique__texte">{{ b.etiquette }}</text>
        </g>
      </svg>

      <div v-if="bulle" class="graphique__bulle" :style="{ left: bulle.gauche + 'px' }" aria-hidden="true">
        <strong>{{ jourCourt(bulle.date) }}</strong>
        <span>{{ euros(bulle.montant) }}</span>
        <span>{{ nombre(bulle.nb_appels) }} appel{{ bulle.nb_appels > 1 ? "s" : "" }}<template v-if="bulle.nb_echecs"> · {{ bulle.nb_echecs }} échec{{ bulle.nb_echecs > 1 ? "s" : "" }}</template></span>
      </div>

      <p v-if="toutAZero" class="graphique__vide">
        Aucun coût sur la période. Avec le faux fournisseur d'IA (développement, tests), chaque appel coûte 0 € :
        les coûts réels apparaissent dès que des parties utilisent OpenRouter.
      </p>
    </div>
  `,
};
