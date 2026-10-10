# Etapa 3 - Patron del perfil Full Stack Developer.
# Lenguaje -> Frontend -> Backend -> Base de datos -> Control de versiones,
# y al final, opcionalmente, herramientas extra (Docker, Kubernetes, REST API, GraphQL).
 
PROFILE = {
    #"groups" es la lista de pasos en orden. Cada paso es un diccionario con tres cosas:
    # cada elemento de groups es el paso
    #"name": el nombre del paso, que se usa en la justificación del tipo de autómata.
    #"symbols": las palabras que sirven para cumplir ese paso. Con tener cualquiera de ellas basta.
    #"optional": si es False, el paso es obligatorio; si es True, se puede saltar.

    #El orden de la lista importa, porque es el orden en que el autómata los va a revisar.

    #"extras": ["DOCKER", "KUBERNETES", "REST_API", "GRAPHQL"], como bien su nombre lo dice son cosas que pueden aparecer despues
    # de que el candidato haya sido rechazado, pero no se va a rechazar a alguien por saber mas, por eso se usa un tipo de autom

    "name": "Full Stack Developer",
    "groups": [
        {"name": "Language", "symbols": ["JAVASCRIPT", "TYPESCRIPT"], "optional": False},
        {"name": "Frontend", "symbols": ["REACT", "ANGULAR", "VUE"], "optional": False},
        {"name": "Backend", "symbols": ["NODE_JS", "DJANGO", "SPRING_BOOT", "EXPRESS", "FASTAPI", "FLASK"], "optional": False},
        {"name": "Database", "symbols": ["POSTGRESQL", "MYSQL", "MONGODB", "SQL", "NOSQL"], "optional": False},
        {"name": "Version control", "symbols": ["GIT", "GITHUB"], "optional": False},
    ],
    "extras": ["DOCKER", "KUBERNETES", "REST_API", "GRAPHQL"],
}
 