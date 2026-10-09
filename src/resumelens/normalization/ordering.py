# Etapa 2 - Orden canonico de cada perfil.
#
# El enunciado pide ordenar las habilidades normalizadas segun el perfil, para que
# el resultado no dependa del orden en que la persona escribio su hoja de vida.
# El automata de la etapa 3 lee los simbolos en secuencia, asi que necesita que
# siempre lleguen en el mismo orden.
#
# Decision de diseño: a cada perfil solo se le pasan las habilidades que estan en
# su lista. Por ejemplo, si alguien tiene React, eso no le sirve al automata de
# Cloud Engineer, entonces no se le manda. Asi los automatas son mas sencillos.

PROFILE_ORDER = {
    "full_stack": [
        "JAVASCRIPT", "TYPESCRIPT", "REACT", "ANGULAR", "VUE",
        "NODE_JS", "DJANGO", "SPRING_BOOT", "EXPRESS", "FASTAPI", "FLASK",
        "POSTGRESQL", "MYSQL", "MONGODB", "SQL", "NOSQL",
        "GIT", "GITHUB", "DOCKER", "KUBERNETES", "REST_API", "GRAPHQL",
    ],

    "machine_learning": [
        "PYTHON",
        "PANDAS", "NUMPY",
        "SCIKIT_LEARN", "TENSORFLOW", "PYTORCH", "KERAS",
        "SQL", "POSTGRESQL", "MONGODB",
        "GIT", "DOCKER", "AWS",
    ],

    "ai_engineer": [
        "PYTHON",
        "PANDAS", "NUMPY",
        "SCIKIT_LEARN", "TENSORFLOW", "PYTORCH", "KERAS",
        "SPARK", "HUGGING_FACE",
        "SQL", "POSTGRESQL", "MONGODB", "REDIS",
        "DOCKER", "KUBERNETES", "AWS", "GCP", "GIT",
    ],

    "cloud_engineer": [
        "AWS", "AZURE", "GCP",
        "DOCKER", "KUBERNETES", "HELM",
        "TERRAFORM", "ANSIBLE",
        "JENKINS", "GITHUB", "GITLAB",
        "LINUX", "PYTHON", "GO",
        "POSTGRESQL", "MYSQL", "MONGODB", "REDIS", "SQL",
        "GIT",
    ],
}


def sort_skills(canonical_skills, profile):
    order = PROFILE_ORDER[profile]
    sorted_skills = []
    for skill in order:
        if skill in canonical_skills:
            sorted_skills.append(skill)
    return sorted_skills


def sort_for_all_profiles(canonical_skills):
    result = {}
    for profile in PROFILE_ORDER:
        result[profile] = sort_skills(canonical_skills, profile)
    return result
