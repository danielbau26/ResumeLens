# Stage 3 - Receives the skills sorted per profile from Stage 2
# (normalize(...)["by_profile"]) and runs each list through its profile automaton.
# Returns ACCEPTED or REJECTED for every profile.
 
import json
 
from .profiles import PROFILES
from .automata import accepts
 
# recibe el by profile de la etapa 2, lista de skills ordenada pro perfil
# "by_profile": {
    #"full_stack":       ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"],
    #"machine_learning": ["POSTGRESQL", "GIT"],
    #"ai_engineer":      ["POSTGRESQL", "GIT"],
    #"cloud_engineer":   ["POSTGRESQL", "GIT"],

def recognize(by_profile):
    # crea el diccionario de resultados y recorre los perfiles
    results = {}
    # da 4 vueltas una por perfil
    for profile_key in PROFILES:
        # mira si este perfil de la lista de perfiles, esta en la lista
        # de by_profile (respuesta de la etapa 2) al menos con algo
        # por cada fila (sequencia (lista interna)), miro si la acepto o no y 
        # guardo los 4 resultados
        if profile_key in by_profile:
            # saca la lista de ese perfil, si no viene dev lista vacia
            # la lista vacia automaticamente la rechaza y no se cae el programa
            sequence = by_profile[profile_key]
        else:
            sequence = []
        # pasa la lista por el automata del perfil y guarda Accepted o rejected
        if accepts(profile_key, sequence):
            result = "ACCEPTED"
        else:
            result = "REJECTED"
        # el diccionario de result guarda tres cosas por pefil 
        # el nombre, la lista que leyo el automata y el resultado
        # esto es lo que va a recibir la etapa 4
        results[profile_key] = {
            "profile": PROFILES[profile_key]["name"],
            "sequence": sequence,
            "result": result,
        }
    return results

# recorre los resultados y devuelve solo las claves de los perfiles acceptados
# la clasificacion del cv entre los 4 perfiles
def accepted_profiles(results):
    accepted = []
    for profile_key in results:
        if results[profile_key]["result"] == "ACCEPTED":
            accepted.append(profile_key)
    return accepted
 
# guarda ese resultado en un json 
def save_result(results, path):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)
 