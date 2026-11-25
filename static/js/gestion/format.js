/* =====================================================================
   static/js/gestion/format.js — Mise en forme des chiffres (format belge)
   ===================================================================== */

const NOMBRE = new Intl.NumberFormat("fr-BE");

/** 1234 → « 1 234 ». */
export function nombre(valeur) {
  return NOMBRE.format(valeur || 0);
}

/**
 * Montant en euros (« 0,0004 € »). Les appels coûtent souvent moins d'un
 * centime : sous 0,01 € on garde 4 à 6 décimales pour ne pas tout afficher
 * « 0,00 € ». La conversion depuis les dollars se fait avant (TableauCouts).
 */
export function euros(valeur) {
  const v = valeur || 0;
  const petit = v !== 0 && Math.abs(v) < 0.01;
  return new Intl.NumberFormat("fr-BE", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: petit ? 4 : 2,
    maximumFractionDigits: petit ? 6 : 2,
  }).format(v);
}

/** Taux de change avec ses 4 décimales officielles : 1.0968 → « 1,0968 ». */
export function taux(valeur) {
  return new Intl.NumberFormat("fr-BE", { minimumFractionDigits: 4, maximumFractionDigits: 4 }).format(
    valeur || 0,
  );
}

/** « 2026-11-18 » → « 18/11/2026 ». */
export function dateLongue(dateIso) {
  return new Date(dateIso + "T12:00:00").toLocaleDateString("fr-BE");
}

/** 0,0532 → « 5,3 % ». */
export function pourcent(fraction) {
  return new Intl.NumberFormat("fr-BE", { style: "percent", maximumFractionDigits: 1 }).format(
    fraction || 0,
  );
}

/** « 2026-11-25 » → « 25 nov. ». */
export function jourCourt(dateIso) {
  return new Date(dateIso + "T12:00:00").toLocaleDateString("fr-BE", {
    day: "numeric",
    month: "short",
  });
}

/** Date et heure complètes d'un appel. */
export function dateHeure(dateIso) {
  return new Date(dateIso).toLocaleString("fr-BE", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}
