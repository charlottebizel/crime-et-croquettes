"""
ia/schemas.py — Schémas JSON imposés au modèle (spec §7).

Envoyés en `response_format: json_schema` strict : le modèle ne peut
répondre qu'avec un JSON de cette forme. Le mode strict exige que tous
les champs soient « required » et interdit les champs en plus
(additionalProperties: false).

Les limites de longueur et les règles du jeu (stress, identifiants…)
sont vérifiées ensuite en Python, dans ia/validation.py.
"""

SCHEMA_INTERROGATOIRE = {
    "type": "object",
    "properties": {
        "reponse": {"type": "string", "description": "Réplique du suspect, 600 caractères max"},
        "stress": {"type": "integer", "description": "Nouveau stress du suspect, de 0 à 100"},
        "indices": {
            "type": "array",
            "description": "0 à 2 informations utiles pour l'enquête, tirées de la réponse",
            "items": {
                "type": "object",
                "properties": {
                    "texte": {"type": "string", "description": "200 caractères max"},
                    "liens": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "enum": ["suspect", "objet", "lieu"]},
                                "id": {"type": "integer"},
                            },
                            "required": ["type", "id"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["texte", "liens"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["reponse", "stress", "indices"],
    "additionalProperties": False,
}
