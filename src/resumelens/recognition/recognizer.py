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
    for profile_key in PROFILES:
        
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