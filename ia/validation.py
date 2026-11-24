"""
ia/validation.py — Vérification des réponses du modèle (spec §7.3).

On ne fait jamais confiance au modèle : même avec un schéma strict, il peut
renvoyer un stress à 250, un identifiant d'une autre enquête, un texte trop
long… Une réponse refusée lève ReponseInvalide (erreur `invalide`) : elle
est journalisée dans AppelIA et rien n'est enregistré dans la partie.

La validation de la génération d'enquête arrivera avec la génération (S4).
"""

from .erreurs import ReponseInvalide

REPONSE_MAX = 600
INDICE_MAX = 200
INDICES_MAX = 2
VARIATION_STRESS_MAX = 40


def _entier(valeur) -> bool:
    # bool est une sous-classe de int en Python : True ne doit pas passer pour 1.
    return isinstance(valeur, int) and not isinstance(valeur, bool)


def valider_interrogatoire(donnees: dict, enquete, stress_actuel: int) -> dict:
    """Renvoie une réponse propre ou lève ReponseInvalide.

    Résultat : {"reponse": str, "stress": int, "indices": [
        {"texte": str, "suspects": [ids], "objets": [ids], "lieux": [ids]}]}
    """
    reponse = donnees.get("reponse")
    if not isinstance(reponse, str) or not reponse.strip():
        raise ReponseInvalide("reponse vide ou absente")
    if len(reponse) > REPONSE_MAX:
        raise ReponseInvalide(f"reponse trop longue ({len(reponse)} > {REPONSE_MAX})")

    stress = donnees.get("stress")
    if not _entier(stress) or not 0 <= stress <= 100:
        raise ReponseInvalide(f"stress invalide : {stress!r}")
    # Variation bornée à 40 points (on corrige au lieu de refuser).
    stress = max(
        stress_actuel - VARIATION_STRESS_MAX, min(stress, stress_actuel + VARIATION_STRESS_MAX)
    )

    indices = donnees.get("indices")
    if not isinstance(indices, list):
        raise ReponseInvalide("indices n'est pas une liste")
    if len(indices) > INDICES_MAX:
        raise ReponseInvalide(f"trop d'indices ({len(indices)} > {INDICES_MAX})")

    # Identifiants autorisés : uniquement ceux de CETTE enquête, par type.
    autorises = {
        "suspect": set(enquete.suspects.values_list("pk", flat=True)),
        "objet": set(enquete.objets.values_list("pk", flat=True)),
        "lieu": set(enquete.lieux.values_list("pk", flat=True)),
    }

    indices_propres = []
    for indice in indices:
        if not isinstance(indice, dict):
            raise ReponseInvalide("indice mal formé")
        texte = indice.get("texte")
        if not isinstance(texte, str) or not texte.strip():
            raise ReponseInvalide("texte d'indice vide")
        if len(texte) > INDICE_MAX:
            raise ReponseInvalide(f"indice trop long ({len(texte)} > {INDICE_MAX})")
        liens = indice.get("liens")
        if not isinstance(liens, list):
            raise ReponseInvalide("liens n'est pas une liste")

        ids = {"suspect": [], "objet": [], "lieu": []}
        for lien in liens:
            if not isinstance(lien, dict):
                raise ReponseInvalide("lien mal formé")
            type_lien, id_lien = lien.get("type"), lien.get("id")
            if type_lien not in autorises:
                raise ReponseInvalide(f"type de lien inconnu : {type_lien!r}")
            if not _entier(id_lien) or id_lien not in autorises[type_lien]:
                raise ReponseInvalide(f"{type_lien} {id_lien!r} absent de cette enquête")
            if id_lien not in ids[type_lien]:
                ids[type_lien].append(id_lien)

        indices_propres.append(
            {
                "texte": texte.strip(),
                "suspects": ids["suspect"],
                "objets": ids["objet"],
                "lieux": ids["lieu"],
            }
        )

    return {"reponse": reponse.strip(), "stress": stress, "indices": indices_propres}
