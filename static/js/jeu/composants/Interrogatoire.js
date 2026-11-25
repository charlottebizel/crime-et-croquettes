/* =====================================================================
   Interrogatoire.js — Salle d'interrogatoire, conversation et question
   =====================================================================
   Props :
     suspect      : suspect interrogé (spec §6.2)
     echanges     : sa conversation (spec §6.3)
     inspecteur   : apparence de l'avatar du joueur
     compteurs    : spec §6.6 (questions restantes)
     modeDemo     : true = formulaire inactif
     chargement   : true pendant le chargement de la conversation
     envoiEnCours : true pendant qu'une question part au serveur
     erreur       : message d'erreur à afficher (IA, quota, réseau…), ou ""
   Événement : « poser » (texte) quand le joueur envoie sa question.

   La question tapée n'est effacée qu'après un succès : le parent appelle
   vider(). En cas d'erreur elle reste dans le champ (exigence O5).
   Chaque réponse du suspect porte « Généré par IA » (O7, AI Act art. 50).
   ===================================================================== */

import { nextTick } from "vue";

import ChatPortrait from "./ChatPortrait.js";
import JaugeStress from "./JaugeStress.js";
import { TITRE_INACTIF_DEMO, deuxChiffres } from "../outils.js";

export default {
  name: "Interrogatoire",
  components: { ChatPortrait, JaugeStress },
  props: {
    suspect: { type: Object, required: true },
    echanges: { type: Array, default: () => [] },
    inspecteur: { type: Object, default: () => ({}) },
    compteurs: { type: Object, required: true },
    modeDemo: { type: Boolean, default: false },
    chargement: { type: Boolean, default: false },
    envoiEnCours: { type: Boolean, default: false },
    erreur: { type: String, default: "" },
  },
  emits: ["poser"],
  data() {
    return { question: "", titreInactif: TITRE_INACTIF_DEMO };
  },
  computed: {
    numero() {
      return deuxChiffres(this.suspect.numero);
    },
    champInactif() {
      return this.modeDemo || !this.compteurs.peut_poser_question || this.envoiEnCours;
    },
    restantes() {
      const n = this.compteurs.questions_restantes;
      return n + " question" + (n > 1 ? "s" : "");
    },
  },
  watch: {
    // Nouvelle réponse ou autre suspect : on descend au dernier échange.
    echanges: {
      handler() {
        this.descendre();
      },
      deep: true,
    },
  },
  mounted() {
    this.descendre();
  },
  methods: {
    descendre() {
      nextTick(() => {
        const zone = this.$refs.conversation;
        if (zone) {
          zone.scrollTop = zone.scrollHeight;
        }
      });
    },
    envoyer() {
      const texte = this.question.trim();
      if (texte && !this.champInactif) {
        this.$emit("poser", texte);
      }
    },
    vider() {
      this.question = "";
    },
  },
  template: `
    <section class="plateau__centre interrogatoire" aria-labelledby="titre-interrogatoire">
      <div class="salle">
        <!-- Décor : lampe et faisceau de lumière (purement décoratif) -->
        <div class="salle__decor" aria-hidden="true">
          <span class="salle__faisceau"></span>
          <svg class="salle__lampe" width="80" height="60" viewBox="0 0 80 60"><path d="M40 0 L40 18" stroke="#3A4865" stroke-width="3"/><path d="M14 44 Q40 6 66 44 Z" fill="#26324A" stroke="#3A4865" stroke-width="2" stroke-linejoin="round"/><ellipse cx="40" cy="45" rx="13" ry="5" fill="#FFE3A0"/></svg>
          <span class="salle__sol"></span>
        </div>

        <p class="salle__horodatage machine">
          Salle d'interrogatoire
          <span class="salle__rec"><span class="salle__point"></span>Enregistrement</span>
        </p>

        <div class="salle__suspect">
          <div class="salle__portrait">
            <ChatPortrait :apparence="suspect.apparence" :label="suspect.nom" />
          </div>
          <h2 id="titre-interrogatoire" class="salle__nom machine">N° {{ numero }} · {{ suspect.nom }}</h2>
        </div>

        <JaugeStress :suspect="suspect" />

        <p class="salle__ia">Suspect joué par une IA</p>
      </div>

      <!-- aria-live : une nouvelle réponse est lue automatiquement -->
      <div ref="conversation" class="conversation" aria-live="polite" :aria-busy="chargement ? 'true' : 'false'">
        <p v-if="chargement" class="conversation__chargement machine">Le suspect s'installe sous la lampe…</p>
        <template v-else-if="echanges.length">
          <template v-for="(message, index) in echanges" :key="index">
            <div v-if="message.est_suspect" class="bulle bulle--suspect">
              <p class="bulle__auteur">{{ suspect.nom }}</p>
              <p class="bulle__texte">{{ message.texte }}</p>
              <p class="bulle__infos">
                <span class="mention-ia">Généré par IA</span>
                <span v-if="message.stress_avant !== null && message.stress_avant !== undefined" class="bulle__stress machine">Stress {{ message.stress_avant }} → {{ message.stress_apres }} %</span>
                <span v-if="message.a_ajoute_au_carnet" class="bulle__carnet">Ajouté au carnet</span>
              </p>
            </div>
            <div v-else class="bulle bulle--joueur">
              <div class="bulle__contenu">
                <p class="bulle__auteur">{{ message.auteur }}</p>
                <p class="bulle__texte">{{ message.texte }}</p>
              </div>
              <span class="bulle__avatar" aria-hidden="true">
                <ChatPortrait :apparence="inspecteur" accessoire="inspecteur" label="" />
              </span>
            </div>
          </template>
        </template>
        <div v-else class="conversation__vide">
          <p class="conversation__vide-titre">Pas encore interrogé</p>
          <p>{{ suspect.nom }} se lèche les pattes sous la lampe. À vous la première question, inspecteur.</p>
        </div>
      </div>

      <!-- Erreurs IA, quota ou réseau (exigence O5) -->
      <p v-if="erreur" class="erreur-action" role="alert">{{ erreur }}</p>

      <form class="question" @submit.prevent="envoyer">
        <label for="question" class="etiquette">Question à {{ suspect.nom }}</label>
        <div class="question__ligne">
          <input id="question" v-model="question" type="text" class="champ" maxlength="300"
                 placeholder="Pourquoi avez-vous des poils sur le comptoir ?"
                 :disabled="champInactif" :title="modeDemo ? titreInactif : null">
          <button type="submit" class="btn btn--ambre" :disabled="champInactif || !question.trim()"
                  :title="modeDemo ? titreInactif : null">
            {{ envoiEnCours ? "Interrogatoire…" : "Interroger" }}
          </button>
        </div>
        <p class="question__aide">
          Les suspects répondent grâce à une IA : ils peuvent mentir, c'est le jeu.
          N'écrivez aucune donnée personnelle.
          <template v-if="compteurs.peut_poser_question">Encore {{ restantes }} dans cette partie.</template>
          <template v-else>Plus de questions disponibles dans cette partie.</template>
        </p>
      </form>
    </section>
  `,
};
