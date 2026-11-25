/* =====================================================================
   EcranPartie.js — Composant racine de l'écran de partie
   =====================================================================
   Props (fournies par main.js à partir du template) :
     urlApi   : adresse de la partie dans l'API (ex. /api/parties/demo/)
     modeDemo : true = actions serveur désactivées ; avis et fiche
                fonctionnent quand même, mais restent dans le navigateur

   Rôle :
     - charge l'état de la partie (GET urlApi) puis la conversation du
       suspect choisi (GET urlApi + "suspects/<id>/") ;
     - garde cet état et le transmet aux composants enfants ;
     - réagit à leurs événements (choisir un suspect, poser une question,
       tirer une carte, donner un avis, cocher la fiche) ;
     - gère les onglets Carnet / Fiche (clavier compris).

   Adresses et formats des requêtes : docs/specification.md §5.4.
   ===================================================================== */

import CarteSuspect from "./CarteSuspect.js";
import Compteurs from "./Compteurs.js";
import EntreeCarnet from "./EntreeCarnet.js";
import FicheDeduction from "./FicheDeduction.js";
import Interrogatoire from "./Interrogatoire.js";
import PieceConviction from "./PieceConviction.js";
import { envoyerJSON, lireJSON } from "../api.js";
import { TITRE_INACTIF_DEMO } from "../outils.js";

const CLE_ONGLET = "cc-onglet-partie";
const ONGLETS = ["carnet", "fiche"];
const ETAT_SUIVANT = { inconnu: "barre", barre: "valide", valide: "inconnu" };

/** localStorage peut être bloqué (navigation privée) : on ne plante jamais. */
function lireMemoire(cle) {
  try {
    return window.localStorage.getItem(cle);
  } catch (e) {
    return null;
  }
}
function ecrireMemoire(cle, valeur) {
  try {
    window.localStorage.setItem(cle, valeur);
  } catch (e) {
    /* stockage indisponible : tant pis */
  }
}

export default {
  name: "EcranPartie",
  components: {
    CarteSuspect,
    Compteurs,
    EntreeCarnet,
    FicheDeduction,
    Interrogatoire,
    PieceConviction,
  },
  props: {
    urlApi: { type: String, required: true },
    modeDemo: { type: Boolean, default: false },
  },
  data() {
    const ongletMemorise = lireMemoire(CLE_ONGLET);
    return {
      etat: null, // réponse de GET urlApi (spec §6.1, sans les conversations)
      chargement: true,
      erreurChargement: "",
      suspectId: null,
      echanges: [],
      chargementSuspect: false,
      envoiEnCours: false,
      erreurAction: "",
      onglet: ONGLETS.includes(ongletMemorise) ? ongletMemorise : "carnet",
      titreInactif: TITRE_INACTIF_DEMO,
    };
  },
  computed: {
    suspectCourant() {
      if (!this.etat) {
        return null;
      }
      return this.etat.suspects.find((s) => s.id === this.suspectId) || null;
    },
    peutTirer() {
      return !this.modeDemo && this.etat.compteurs.peut_tirer_carte && !this.envoiEnCours;
    },
  },
  mounted() {
    this.charger();
  },
  methods: {
    /* ---------------- Chargement ---------------- */

    async charger() {
      this.chargement = true;
      this.erreurChargement = "";
      try {
        this.etat = await lireJSON(this.urlApi);
      } catch (erreur) {
        this.erreurChargement = erreur.message;
        this.chargement = false;
        return;
      }
      this.chargement = false;
      // Suspect demandé dans l'adresse (?suspect=<id>), sinon le premier.
      const demande = Number(new URLSearchParams(window.location.search).get("suspect"));
      const existe = this.etat.suspects.some((s) => s.id === demande);
      this.choisirSuspect(existe ? demande : this.etat.suspects[0].id);
    },

    async choisirSuspect(id) {
      if (id === this.suspectId && this.echanges.length) {
        return;
      }
      this.suspectId = id;
      this.erreurAction = "";
      this.echanges = [];
      this.chargementSuspect = true;
      // L'adresse garde le suspect choisi (lien partageable, rechargement).
      const adresse = new URL(window.location.href);
      adresse.searchParams.set("suspect", id);
      window.history.replaceState(null, "", adresse);
      try {
        const donnees = await lireJSON(this.urlApi + "suspects/" + id + "/");
        if (this.suspectId !== id) {
          return; // le joueur a déjà cliqué sur un autre suspect
        }
        this.majSuspect(donnees.suspect);
        this.echanges = donnees.echanges;
      } catch (erreur) {
        this.erreurAction = erreur.message;
      } finally {
        if (this.suspectId === id) {
          this.chargementSuspect = false;
        }
      }
    },

    /** Remplace les données d'un suspect (stress, interrogé…) dans la liste. */
    majSuspect(suspect) {
      const actuel = this.etat.suspects.find((s) => s.id === suspect.id);
      if (actuel) {
        Object.assign(actuel, suspect);
      }
    },

    /* ---------------- Actions (spec §5.4) ---------------- */

    async poserQuestion(texte) {
      if (this.modeDemo) {
        return;
      }
      this.envoiEnCours = true;
      this.erreurAction = "";
      try {
        const r = await envoyerJSON(this.urlApi + "suspects/" + this.suspectId + "/question/", {
          question: texte,
        });
        this.echanges.push(...r.echange);
        this.majSuspect(r.suspect);
        this.etat.entrees_carnet.unshift(...r.nouvelles_entrees);
        this.etat.compteurs = r.compteurs;
        this.$refs.interrogatoire.vider(); // succès seulement : sinon la question reste
      } catch (erreur) {
        this.erreurAction = erreur.message;
      } finally {
        this.envoiEnCours = false;
      }
    },

    async tirerCarte() {
      if (!this.peutTirer) {
        return;
      }
      this.envoiEnCours = true;
      this.erreurAction = "";
      try {
        const r = await envoyerJSON(this.urlApi + "cartes/tirer/", {});
        this.etat.cartes_tirees.push(r.carte);
        this.etat.entrees_carnet.unshift(r.entree);
        this.etat.compteurs = r.compteurs;
      } catch (erreur) {
        this.erreurAction = erreur.message;
      } finally {
        this.envoiEnCours = false;
      }
    },

    async donnerAvis(entree, avis) {
      const ancien = entree.avis;
      entree.avis = avis; // affichage immédiat
      if (this.modeDemo) {
        return; // démo : l'avis reste dans le navigateur
      }
      try {
        const r = await envoyerJSON(this.urlApi + "carnet/" + entree.id + "/avis/", {
          avis: avis || "",
        });
        Object.assign(entree, r.entree);
      } catch (erreur) {
        entree.avis = ancien; // on annule l'affichage
        this.erreurAction = erreur.message;
      }
    },

    async tournerCase(caseFiche) {
      const ancien = caseFiche.etat;
      caseFiche.etat = ETAT_SUIVANT[ancien] || "inconnu"; // affichage immédiat
      if (this.modeDemo) {
        return; // démo : la fiche reste dans le navigateur
      }
      try {
        const r = await envoyerJSON(this.urlApi + "fiche/" + caseFiche.id + "/", {});
        Object.assign(caseFiche, r.case);
      } catch (erreur) {
        caseFiche.etat = ancien;
        this.erreurAction = erreur.message;
      }
    },

    /* ---------------- Onglets Carnet / Fiche ---------------- */

    choisirOnglet(nom, donnerFocus) {
      this.onglet = nom;
      ecrireMemoire(CLE_ONGLET, nom);
      if (donnerFocus) {
        this.$nextTick(() => this.$refs["onglet-" + nom].focus());
      }
    },
    clavierOnglets(evenement) {
      const i = ONGLETS.indexOf(this.onglet);
      const cibles = {
        ArrowRight: ONGLETS[(i + 1) % ONGLETS.length],
        ArrowLeft: ONGLETS[(i - 1 + ONGLETS.length) % ONGLETS.length],
        Home: ONGLETS[0],
        End: ONGLETS[ONGLETS.length - 1],
      };
      if (cibles[evenement.key]) {
        evenement.preventDefault();
        this.choisirOnglet(cibles[evenement.key], true);
      }
    },
  },
  template: `
    <p v-if="chargement" class="chargement machine">Ouverture du dossier…</p>

    <div v-else-if="erreurChargement" class="erreur-chargement" role="alert">
      <p>{{ erreurChargement }}</p>
      <button type="button" class="btn" @click="charger">Réessayer</button>
    </div>

    <div v-else class="ecran-partie">
      <p v-if="modeDemo" class="bandeau-demo" role="note">
        <strong>Démonstration</strong> : enquête d'exemple, sans IA. Changez de suspect, donnez votre avis sur les témoignages et cochez votre fiche :
        rien n'est enregistré. Questions, cartes et accusation seront branchées avec le jeu complet.
      </p>

      <!-- Entête de l'affaire -->
      <header class="affaire">
        <div class="affaire__dossier">
          <span class="tampon affaire__tampon">Confidentiel</span>
          <div>
            <p class="affaire__numero machine">Affaire · code {{ etat.partie.code_invitation }}</p>
            <h1 class="affaire__titre">{{ etat.enquete.titre }}</h1>
          </div>
        </div>
        <div class="affaire__actions">
          <Compteurs :compteurs="etat.compteurs" />
          <!-- Accuser : l'écran d'accusation sera la prochaine feature -->
          <button type="button" class="btn btn--tampon" disabled :title="titreInactif">
            <svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M1 12h4M19 12h4"/></svg>
            Accuser
          </button>
        </div>
      </header>

      <details class="synopsis">
        <summary class="machine">Lire le résumé de l'affaire</summary>
        <p>{{ etat.enquete.synopsis }}</p>
      </details>

      <div class="plateau">
        <!-- Colonne gauche : suspects et pièces à conviction -->
        <aside class="plateau__gauche">
          <section aria-labelledby="titre-suspects">
            <h2 id="titre-suspects" class="titre-section"><span class="titre-section__num">01</span>Suspects</h2>
            <div class="grille-suspects">
              <CarteSuspect v-for="s in etat.suspects" :key="s.id"
                            :suspect="s" :actif="s.id === suspectId"
                            @choisir="choisirSuspect" />
            </div>
          </section>

          <section aria-labelledby="titre-pieces">
            <div class="entete-section">
              <h2 id="titre-pieces" class="titre-section"><span class="titre-section__num">02</span>Pièces à conviction</h2>
              <span class="machine texte-doux">{{ etat.compteurs.cartes_tirees }} / {{ etat.compteurs.cartes_max }}</span>
            </div>
            <div class="pieces">
              <PieceConviction v-for="carte in etat.cartes_tirees" :key="carte.code" :carte="carte" />
              <p v-if="!etat.cartes_tirees.length" class="texte-doux">Aucune pièce tirée pour l'instant.</p>
            </div>
            <button type="button" class="btn btn--tirer" :disabled="!peutTirer"
                    :title="modeDemo ? titreInactif : null" @click="tirerCarte">
              Tirer une carte
            </button>
          </section>
        </aside>

        <!-- Colonne centre : salle d'interrogatoire -->
        <Interrogatoire v-if="suspectCourant" ref="interrogatoire"
                        :suspect="suspectCourant" :echanges="echanges"
                        :inspecteur="etat.inspecteur" :compteurs="etat.compteurs"
                        :mode-demo="modeDemo" :chargement="chargementSuspect"
                        :envoi-en-cours="envoiEnCours" :erreur="erreurAction"
                        @poser="poserQuestion" />

        <!-- Colonne droite : onglets Carnet / Fiche -->
        <aside class="plateau__droite onglets onglets--actifs">
          <div class="onglets__liste" role="tablist" aria-label="Carnet et fiche" @keydown="clavierOnglets">
            <button type="button" role="tab" id="onglet-carnet" ref="onglet-carnet" class="onglets__onglet"
                    aria-controls="panneau-carnet" :aria-selected="onglet === 'carnet' ? 'true' : 'false'"
                    :tabindex="onglet === 'carnet' ? 0 : -1" @click="choisirOnglet('carnet')">Carnet d'indices</button>
            <button type="button" role="tab" id="onglet-fiche" ref="onglet-fiche" class="onglets__onglet"
                    aria-controls="panneau-fiche" :aria-selected="onglet === 'fiche' ? 'true' : 'false'"
                    :tabindex="onglet === 'fiche' ? 0 : -1" @click="choisirOnglet('fiche')">Fiche de déduction</button>
          </div>

          <section v-show="onglet === 'carnet'" id="panneau-carnet" class="onglets__panneau carnet"
                   role="tabpanel" aria-labelledby="onglet-carnet">
            <h2 class="onglets__titre">Carnet d'indices</h2>
            <p class="manuscrit carnet__intro">Rempli par l'IA à chaque réponse. À moi de juger.</p>
            <div class="carnet__entrees">
              <EntreeCarnet v-for="entree in etat.entrees_carnet" :key="entree.id" :entree="entree"
                            @avis="(valeur) => donnerAvis(entree, valeur)" />
              <p v-if="!etat.entrees_carnet.length">Le carnet est encore vide.</p>
            </div>
          </section>

          <section v-show="onglet === 'fiche'" id="panneau-fiche" class="onglets__panneau fiche"
                   role="tabpanel" aria-labelledby="onglet-fiche">
            <h2 class="onglets__titre">Fiche de déduction</h2>
            <FicheDeduction :fiche="etat.fiche" @tourner="tournerCase" />
          </section>
        </aside>
      </div>
    </div>
  `,
};
