# Stage 2 - Orchestrator: translate -> de-duplicate -> sort.
# Takes the surface skills from Stage 1, runs each one through the transducers,
# removes duplicates, and (if a profile is given) sorts them into the profile's
# canonical order. Returns a plain dictionary so it is easy to show in Streamlit.

import json

from ..extraction import get_skills
from .ordering import sort_qualifications
from .transducers import normalize_token


# Quita duplicados conservando el primero que aparecio.
def _dedupe(values):
    seen = []
    for value in values:
        if value not in seen:
            seen.append(value)
    return seen


# Funcion principal de la etapa 2.
# Recibe la lista de skills (de la etapa 1) y devuelve un diccionario con:
#   canonical    -> lista de formas canonicas (deduplicada y, si hay perfil, ordenada)
#   mapping      -> pares (superficie, canonico), para ver de donde salio cada uno
#   unrecognized -> tokens que ningun transductor reconocio (no se pierden)
#   profile      -> el perfil usado para ordenar (o None)
def normalize(skills, profile=None):
    mapping = []
    canonical = []
    unrecognized = []

    for token in skills:
        result = normalize_token(token)   # pasa el token por los FST
        if result is None:
            unrecognized.append(token)
        else:
            mapping.append((token, result))
            canonical.append(result)

    canonical = _dedupe(canonical)
    if profile is not None:
        canonical = sort_qualifications(canonical, profile)

    return {
        "profile": profile,
        "canonical": canonical,
        "mapping": mapping,
        "unrecognized": _dedupe(unrecognized),
    }


# Conveniencia: recibe el diccionario de la etapa 1 y normaliza sus skills.
def normalize_extraction(data, profile=None):
    return normalize(get_skills(data), profile=profile)


# Guarda el resultado como JSON (indent=2 lo deja ordenado, ensure_ascii=False
# conserva tildes y caracteres especiales).
def save_result(result, path):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
