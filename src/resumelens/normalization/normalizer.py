# Etapa 2 - Une todo: recibe la lista de la etapa 1, la traduce con los
# transductores, quita repetidos y la ordena para cada perfil.
#
#   ["Git", "NodeJS", "JS", "Postgres", "React.js"]            <- get_skills() de la etapa 1
#        | translate() en cada palabra
#   ["GIT", "NODE_JS", "JAVASCRIPT", "POSTGRESQL", "REACT"]
#        | sort_skills(..., "full_stack")
#   ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]    -> va a la etapa 3
import json

from .transducers import translate
from .ordering import sort_for_all_profiles

# es el que trae la funcion que traduce y ordena
# recibe la lista de la etapa 1 y hace 3 cosas: 
def normalize(skills):
    canonical = [] #lista de formas canonicas sin repetir
    translations = {} # un diccionario de que se trajo a que
    unrecognized = [] # y la lista de lo que no se recorrio

    # traduce cada habilidad. si da none ningun transductor
    # la acepto y va a no reconocidad
    for skill in skills:
        result = translate(skill)
        if result is None:
            unrecognized.append(skill)
        # si si se tradujo, guarda la traduccion: "React.js": "REACT"
        # y la agrega a la lista solo si no esta repetida
        #  porque “JS” y “JavaScript” dan los dos JAVASCRIPT
        else:
            translations[skill] = result
            if result not in canonical:
                canonical.append(result)
    # devuelve todo en un diccionario. "by_profile" trae las habilidades
    # ordenadas para cada perfil y eso es lo que se recibe en la etapa 3
    return {
        "canonical": canonical,
        "translations": translations,
        "unrecognized": unrecognized,
        "by_profile": sort_for_all_profiles(canonical),
    }

# guarda el diccionario en un archivo JSON.
def save_result(data, path):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
