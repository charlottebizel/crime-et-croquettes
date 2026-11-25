/* =====================================================================
   TableauCouts.js — Tableau de bord des coûts de l'IA (exigence O4)
   =====================================================================
   Props : urlApi (adresse de /api/gestion/couts/).

   Contenu, de haut en bas :
     1. filtre de période (7, 30 ou 90 jours), sur une seule ligne ;
     2. tuiles : coût de la période, appels et échecs, coût moyen d'une
        question et d'une génération (base du pricing, spec §10), budget
        consommé depuis le début du projet ;
     3. histogramme du coût par jour, avec le tableau des mêmes chiffres ;
     4. consommation par joueur ;
     5. les 20 derniers appels (réussis ou non).

   Toutes les données viennent du journal AppelIA : rien n'est estimé.
   Montants : l'API les donne en dollars (monnaie de facturation
   d'OpenRouter) avec le taux du jour de la BCE (clé « devise », voir
   gestion/taux.py) ; on les affiche en
   euros, comme le budget du projet. La conversion se fait ici, une seule
   fois, avec eur().
   ===================================================================== */

import { lireJSON } from "../../jeu/api.js";
import { dateHeure, dateLongue, euros, jourCourt, nombre, pourcent, taux } from "../format.js";
import GraphiqueJours from "./GraphiqueJours.js";

export default {
  name: "TableauCouts",
  components: { GraphiqueJours },
  props: {
    urlApi: { type: String, required: true },
  },
  data() {
    return { donnees: null, chargement: true, erreur: "", jours: 30 };
  },
  computed: {
    t() {
      return this.donnees.totaux;
    },
    devise() {
      return this.donnees.devise;
    },
    /** Jours du graphique, avec le coût déjà converti en euros. */
    joursEnEuros() {
      return this.donnees.par_jour.map((j) => ({ ...j, montant: this.versEuros(j.cout_usd) }));
    },
    /** Part du budget de la clé OpenRouter déjà consommée (0 à 1). */
    partBudget() {
      const budget = this.devise.budget_eur;
      return budget ? this.versEuros(this.t.cout_depuis_le_debut) / budget : 0;
    },
  },
  mounted() {
    this.charger();
  },
  methods: {
    nombre,
    pourcent,
    jourCourt,
    dateHeure,
    dateLongue,
    euros,
    taux,
    /** Dollars → euros, au taux fourni par le serveur (1 € = x $). */
    versEuros(usd) {
      return (usd || 0) / this.devise.usd_pour_1_eur;
    },
    /** Montant en dollars, affiché en euros. */
    eur(usd) {
      return euros(this.versEuros(usd));
    },
    async charger() {
      this.chargement = true;
      this.erreur = "";
      try {
        this.donnees = await lireJSON(this.urlApi + "?jours=" + this.jours);
      } catch (e) {
        this.erreur = e.message;
      } finally {
        this.chargement = false;
      }
    },
    choisirPeriode(jours) {
      if (jours !== this.jours) {
        this.jours = jours;
        this.charger();
      }
    },
  },
  template: `
    <div class="couts">
      <header class="couts__entete">
        <div>
          <h1 class="titre-section"><span class="titre-section__num">Admin</span>Coûts de l'IA</h1>
          <p class="couts__intro">
            Chaque appel au modèle est enregistré (jetons, coût, durée, succès ou échec).
            <template v-if="donnees">
              Montants en euros, convertis depuis le dollar (monnaie de facturation d'OpenRouter)
              <template v-if="devise.source === 'bce'">au taux de référence de la BCE du {{ dateLongue(devise.date_taux) }}</template>
              <template v-else>au taux de secours du {{ dateLongue(devise.date_taux) }} (taux du jour indisponible)</template>
              : 1 € = {{ taux(devise.usd_pour_1_eur) }} $.
            </template>
          </p>
        </div>
        <div class="periode" role="group" aria-label="Période affichée">
          <button v-for="j in (donnees ? donnees.periodes_possibles : [7, 30, 90])" :key="j" type="button"
                  class="periode__bouton" :aria-pressed="j === jours ? 'true' : 'false'"
                  @click="choisirPeriode(j)">{{ j }} jours</button>
        </div>
      </header>

      <p v-if="chargement && !donnees" class="chargement machine">Calcul des coûts…</p>
      <div v-else-if="erreur" class="erreur-chargement" role="alert">
        <p>{{ erreur }}</p>
        <button type="button" class="btn" @click="charger">Réessayer</button>
      </div>

      <template v-else-if="donnees">
        <!-- Tuiles -->
        <section class="tuiles" aria-label="Résumé de la période" :aria-busy="chargement ? 'true' : 'false'">
          <div class="tuile">
            <p class="tuile__libelle">Coût sur {{ donnees.periode.jours }} jours</p>
            <p class="tuile__valeur">{{ eur(t.cout_usd) }}</p>
            <p class="tuile__detail">{{ nombre(t.jetons_entree) }} jetons envoyés · {{ nombre(t.jetons_sortie) }} reçus</p>
          </div>
          <div class="tuile">
            <p class="tuile__libelle">Appels au modèle</p>
            <p class="tuile__valeur">{{ nombre(t.nb_appels) }}</p>
            <p class="tuile__detail">{{ nombre(t.nb_echecs) }} échec{{ t.nb_echecs > 1 ? "s" : "" }} ({{ pourcent(t.taux_echec) }}) · {{ nombre(t.duree_moyenne_ms) }} ms en moyenne</p>
          </div>
          <div class="tuile">
            <p class="tuile__libelle">Coût moyen d'une question</p>
            <p class="tuile__valeur">{{ eur(t.cout_moyen_question) }}</p>
            <p class="tuile__detail">Interrogatoires réussis, base du pricing</p>
          </div>
          <div class="tuile">
            <p class="tuile__libelle">Coût moyen d'une génération</p>
            <p class="tuile__valeur">{{ eur(t.cout_moyen_generation) }}</p>
            <p class="tuile__detail">Enquêtes générées avec succès</p>
          </div>
          <div class="tuile tuile--budget">
            <p class="tuile__libelle">Depuis le début du projet</p>
            <p class="tuile__valeur">{{ eur(t.cout_depuis_le_debut) }}</p>
            <p class="tuile__detail">{{ pourcent(partBudget) }} du budget de la clé OpenRouter ({{ euros(devise.budget_eur) }})</p>
            <div class="budget" role="meter" aria-label="Part du budget consommée"
                 aria-valuemin="0" aria-valuemax="100" :aria-valuenow="Math.round(partBudget * 100)">
              <span class="budget__niveau" :class="{ 'budget__niveau--alerte': partBudget >= 0.8 }"
                    :style="{ width: Math.min(partBudget, 1) * 100 + '%' }"></span>
            </div>
          </div>
        </section>

        <!-- Coût par jour -->
        <section class="carte-couts" aria-labelledby="titre-par-jour">
          <h2 id="titre-par-jour" class="carte-couts__titre">Coût par jour</h2>
          <p class="carte-couts__sous-titre">Du {{ jourCourt(donnees.periode.debut) }} au {{ jourCourt(donnees.periode.fin) }} · survolez une barre pour le détail</p>
          <GraphiqueJours :jours="joursEnEuros" />
          <details class="carte-couts__table">
            <summary>Voir les chiffres jour par jour</summary>
            <div class="table-defilante">
              <table>
                <thead><tr><th scope="col">Jour</th><th scope="col">Appels</th><th scope="col">Échecs</th><th scope="col">Jetons envoyés</th><th scope="col">Jetons reçus</th><th scope="col">Coût</th></tr></thead>
                <tbody>
                  <tr v-for="j in donnees.par_jour" :key="j.date">
                    <th scope="row">{{ jourCourt(j.date) }}</th><td>{{ nombre(j.nb_appels) }}</td><td>{{ nombre(j.nb_echecs) }}</td>
                    <td>{{ nombre(j.jetons_entree) }}</td><td>{{ nombre(j.jetons_sortie) }}</td><td>{{ eur(j.cout_usd) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </details>
        </section>

        <!-- Par joueur -->
        <section class="carte-couts" aria-labelledby="titre-par-joueur">
          <h2 id="titre-par-joueur" class="carte-couts__titre">Par joueur</h2>
          <p v-if="!donnees.par_utilisateur.length" class="carte-couts__vide">Aucun appel sur la période.</p>
          <div v-else class="table-defilante">
            <table>
              <thead><tr><th scope="col">Joueur</th><th scope="col">Palier</th><th scope="col">Appels</th><th scope="col">Coût</th><th scope="col">Parties ce mois</th></tr></thead>
              <tbody>
                <tr v-for="u in donnees.par_utilisateur" :key="u.pseudo">
                  <th scope="row">{{ u.pseudo }}</th><td>{{ u.palier }}</td><td>{{ nombre(u.nb_appels) }}</td>
                  <td>{{ eur(u.cout_usd) }}</td><td>{{ nombre(u.parties_ce_mois) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- Derniers appels -->
        <section class="carte-couts" aria-labelledby="titre-derniers">
          <h2 id="titre-derniers" class="carte-couts__titre">Derniers appels</h2>
          <p v-if="!donnees.derniers_appels.length" class="carte-couts__vide">Aucun appel enregistré pour l'instant.</p>
          <div v-else class="table-defilante">
            <table>
              <thead><tr><th scope="col">Date</th><th scope="col">Joueur</th><th scope="col">Type</th><th scope="col">Modèle</th><th scope="col">Jetons</th><th scope="col">Durée</th><th scope="col">Coût</th><th scope="col">Résultat</th></tr></thead>
              <tbody>
                <tr v-for="a in donnees.derniers_appels" :key="a.id">
                  <td>{{ dateHeure(a.date) }}</td><td>{{ a.pseudo }}</td><td>{{ a.type }}</td>
                  <td class="machine">{{ a.modele }}</td><td>{{ nombre(a.jetons_entree) }} / {{ nombre(a.jetons_sortie) }}</td>
                  <td>{{ nombre(a.duree_ms) }} ms</td><td>{{ eur(a.cout_usd) }}</td>
                  <td>
                    <span class="resultat" :class="a.succes ? 'resultat--ok' : 'resultat--echec'">
                      <span aria-hidden="true">{{ a.succes ? "✓" : "✕" }}</span>
                      {{ a.succes ? "Réussi" : "Échec" + (a.erreur ? " : " + a.erreur : "") }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>
    </div>
  `,
};
