# Stage 3 - Collects the patterns of the 4 profiles in a single dictionary.
# The keys are the same ones used in Stage 2 (PROFILE_ORDER).
 
from .full_stack import PROFILE as FULL_STACK
from .machine_learning import PROFILE as MACHINE_LEARNING
from .ai_engineer import PROFILE as AI_ENGINEER
from .cloud_engineer import PROFILE as CLOUD_ENGINEER

#Los 4 archivos tienen una variable que se llama igual, PROFILE. Si se importaran las 4 con ese nombre, 
# cada una pisaría a la anterior. El as le pone otro nombre al importarla: “trae PROFILE de full_stack.py,
#  pero aquí llámalo FULL_STACK”.

# la etapa 2 devuelve esto: "by_profile": {
    #"full_stack":       ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"],
    #"machine_learning": ["POSTGRESQL", "GIT"],
    #"ai_engineer":      ["POSTGRESQL", "GIT"],
    #"cloud_engineer":   ["POSTGRESQL", "GIT"],
# por cada candidato, ya ordenado, para los 4 perfiles

#este usa es misma clave

#clave usada en esta etapa

#name, groups y extras de cada uno que se referencia en el automata
PROFILES = {
    "full_stack": FULL_STACK,
    "machine_learning": MACHINE_LEARNING,
    "ai_engineer": AI_ENGINEER,
    "cloud_engineer": CLOUD_ENGINEER,
}
 
















