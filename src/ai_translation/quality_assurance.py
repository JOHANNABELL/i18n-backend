
# =========================================================
# =============== PROTECTION DES VARIABLES =================
# =========================================================

def protect_variables(text: str):
    """
    Protège les variables dynamiques comme {name}, {count}
    afin qu'elles ne soient pas modifiées par le modèle.
    """
    pattern = r"\{.*?\}"
    matches = re.findall(pattern, text)

    placeholders = {}
    for i, match in enumerate(matches):
        placeholder = f"__VAR_{i}__"
        placeholders[placeholder] = match
        text = text.replace(match, placeholder)

    return text, placeholders


def restore_variables(text: str, placeholders: dict):
    """
    Restaure les variables après traduction.
    """
    for placeholder, original in placeholders.items():
        text = text.replace(placeholder, original)
    return text


# =========================================================
# ================= RECURSION JSON ========================
# =========================================================

def translate_dict(data, translator):
    """
    Parcourt récursivement un dict imbriqué
    et traduit uniquement les valeurs string.
    """

    result = {}

    for key, value in data.items():

        if isinstance(value, dict):
            # Cas objet imbriqué
            result[key] = translate_dict(value, translator)

        elif isinstance(value, list):
            # Cas liste
            result[key] = [
                translate_dict(v, translator) if isinstance(v, dict)
                else translator(v) if isinstance(v, str)
                else v
                for v in value
            ]

        elif isinstance(value, str):
            # Cas string simple
            result[key] = translator(value)

        else:
            # int, bool, None, etc.
            result[key] = value

    return result

