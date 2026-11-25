/* =====================================================================
   static/js/jeu/api.js — Dialogue avec l'API JSON du jeu
   =====================================================================
   Deux fonctions, utilisées par les composants :
     lireJSON(url)            → GET, renvoie le JSON de la réponse
     envoyerJSON(url, objet)  → POST JSON, avec le jeton CSRF de Django

   En cas de problème, elles lèvent une ErreurApi dont le message est
   prêt à être affiché au joueur (jamais de détail technique) :
     - le serveur répond une erreur : on reprend son message
       ({"erreur": {"type", "message"}}, spec §5.4) ;
     - le réseau ne répond pas : message générique.
   ===================================================================== */

export class ErreurApi extends Error {
  constructor(message, statut, type) {
    super(message);
    this.name = "ErreurApi";
    this.statut = statut; // code HTTP (0 = pas de réponse du tout)
    this.type = type || "inconnue"; // ex. "introuvable", "quota", "delai"…
  }
}

/** Lit un cookie par son nom (sert au jeton « csrftoken » posé par Django). */
function lireCookie(nom) {
  const prefixe = nom + "=";
  for (const morceau of document.cookie.split(";")) {
    const valeur = morceau.trim();
    if (valeur.startsWith(prefixe)) {
      return decodeURIComponent(valeur.slice(prefixe.length));
    }
  }
  return "";
}

/** Transforme une réponse HTTP en données, ou en ErreurApi lisible. */
async function traiter(reponse) {
  let corps = null;
  try {
    corps = await reponse.json();
  } catch (e) {
    corps = null; // réponse vide ou pas du JSON
  }
  if (!reponse.ok) {
    const erreur = corps && corps.erreur ? corps.erreur : {};
    throw new ErreurApi(
      erreur.message || "Le serveur n'a pas pu répondre (code " + reponse.status + ").",
      reponse.status,
      erreur.type,
    );
  }
  return corps;
}

/** Envoie la requête et transforme une coupure réseau en ErreurApi. */
async function appeler(url, options) {
  let reponse;
  try {
    reponse = await fetch(url, { credentials: "same-origin", ...options });
  } catch (e) {
    throw new ErreurApi(
      "Impossible de joindre le serveur. Vérifiez votre connexion puis réessayez.",
      0,
      "reseau",
    );
  }
  return traiter(reponse);
}

export function lireJSON(url) {
  return appeler(url, { headers: { Accept: "application/json" } });
}

export function envoyerJSON(url, donnees) {
  return appeler(url, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      // Sans ce jeton, Django refuse toute écriture (erreur 403).
      "X-CSRFToken": lireCookie("csrftoken"),
    },
    body: JSON.stringify(donnees),
  });
}
