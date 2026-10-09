# Stage 2 - Canonical ordering per professional profile.
# After the transducers produce the canonical forms, they are reordered into
# the order defined by the chosen profile, so the result no longer depends on
# the order in which the candidate wrote the information in the résumé.
#
# Example (Full Stack): Git, NodeJS, JS, Postgres, React.js
#   -> normalized & sorted: JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT

# Full Stack Developer: Frontend -> Backend -> Database -> Version control.
_FULL_STACK = [
    "JAVASCRIPT", "TYPESCRIPT", "REACT", "ANGULAR", "VUE",
    "NODE_JS", "DJANGO", "SPRING_BOOT", "EXPRESS", "FASTAPI", "FLASK",
    "POSTGRESQL", "MYSQL", "MONGODB", "SQL", "NOSQL",
    "GIT", "GITHUB", "DOCKER", "KUBERNETES", "REST_API", "GRAPHQL",
]

# Machine Learning Engineer: language -> data libs -> ML libs -> database -> tools.
_MACHINE_LEARNING = [
    "PYTHON",
    "PANDAS", "NUMPY",
    "SCIKIT_LEARN", "TENSORFLOW", "PYTORCH", "KERAS",
    "SQL", "POSTGRESQL", "MONGODB",
    "GIT", "DOCKER", "AWS",
]

# AI Engineer: language -> data -> ML/DL -> big data & GenAI -> database -> deployment.
_AI_ENGINEER = [
    "PYTHON",
    "PANDAS", "NUMPY",
    "SCIKIT_LEARN", "TENSORFLOW", "PYTORCH", "KERAS",
    "SPARK", "HUGGING_FACE",
    "SQL", "POSTGRESQL", "MONGODB", "REDIS",
    "DOCKER", "KUBERNETES", "AWS", "GCP", "GIT",
]

# Cloud Engineer: platforms -> containers -> IaC -> CI/CD -> OS -> database -> version control.
_CLOUD_ENGINEER = [
    "AWS", "AZURE", "GCP",
    "DOCKER", "KUBERNETES", "HELM",
    "TERRAFORM", "ANSIBLE",
    "JENKINS", "GITHUB", "GITLAB",
    "LINUX", "PYTHON", "GO",
    "POSTGRESQL", "MYSQL", "MONGODB", "REDIS", "SQL",
    "GIT",
]

# Canonical order per profile, keyed by the identifier used in the CLI.
PROFILE_ORDER = {
    "full_stack": _FULL_STACK,
    "machine_learning": _MACHINE_LEARNING,
    "ai_engineer": _AI_ENGINEER,
    "cloud_engineer": _CLOUD_ENGINEER,
}


# Returns the profile identifiers that define a canonical order.
def available_profiles():
    return list(PROFILE_ORDER)


# Reordena los canonicos segun el orden del perfil.
# Los que estan en el orden del perfil van primero (en ese orden); los que no,
# se agregan al final en el orden en que llegaron (no se pierde nada).
def sort_qualifications(canonical, profile):
    if profile not in PROFILE_ORDER:
        raise KeyError(f"Unknown profile {profile!r}; available: {', '.join(PROFILE_ORDER)}")
    order = PROFILE_ORDER[profile]
    present = set(canonical)
    ordered = [symbol for symbol in order if symbol in present]      # los del perfil, en su orden
    remaining = [symbol for symbol in canonical if symbol not in order]  # los extra, al final
    return ordered + remaining
