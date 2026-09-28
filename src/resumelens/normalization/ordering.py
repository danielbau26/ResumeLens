"""Profile-defined canonical ordering of normalized qualifications.

After normalization the qualifications are a *set* of canonical symbols whose
order still reflects how the candidate happened to write the résumé. Before the
Stage 3 recognition automata consume them, they are reordered into the
**canonical order defined by the selected professional profile**, so the result
no longer depends on the résumé's wording order.

Example (Full Stack, from the assignment)::

    Git, NodeJS, JS, Postgres, React.js
        --normalize-->  JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT   (sorted)

All four supported profiles are ordered here: the two predefined ones (Full
Stack Developer, Machine Learning Engineer) and the two team-defined ones
(AI Engineer, Cloud Engineer). Defining the orders here — rather than in the
Stage 3 recognition module — keeps the recognition stage decoupled: it only
builds the automata and consumes the already-sorted canonical sequence.
Canonical tokens that are not part of a profile's order are appended at the end
in first-seen order, so no information is lost.
"""

from __future__ import annotations

# Full Stack Developer: Frontend -> Backend -> Database -> Version control/tools.
_FULL_STACK: list[str] = [
    # Frontend
    "JAVASCRIPT", "TYPESCRIPT", "REACT", "ANGULAR", "VUE",
    # Backend
    "NODE_JS", "DJANGO", "SPRING_BOOT", "EXPRESS", "FASTAPI", "FLASK",
    # Database
    "POSTGRESQL", "MYSQL", "MONGODB", "SQL", "NOSQL",
    # Version control / tools
    "GIT", "GITHUB", "DOCKER", "KUBERNETES", "REST_API", "GRAPHQL",
]

# Machine Learning Engineer: language -> data libs -> ML libs -> database -> tools.
_MACHINE_LEARNING: list[str] = [
    # Language
    "PYTHON",
    # Data processing
    "PANDAS", "NUMPY",
    # Machine-learning libraries
    "SCIKIT_LEARN", "TENSORFLOW", "PYTORCH", "KERAS",
    # Database
    "SQL", "POSTGRESQL", "MONGODB",
    # Tools
    "GIT", "DOCKER", "AWS",
]

# AI Engineer (team-defined): language -> data -> ML/DL libs -> big data & GenAI
# -> database -> deployment/tools. Distinguished from the ML Engineer profile by
# the big-data / generative-AI tooling (Spark, Hugging Face).
_AI_ENGINEER: list[str] = [
    # Language
    "PYTHON",
    # Data processing
    "PANDAS", "NUMPY",
    # Machine-learning / deep-learning libraries
    "SCIKIT_LEARN", "TENSORFLOW", "PYTORCH", "KERAS",
    # Big data & generative AI
    "SPARK", "HUGGING_FACE",
    # Database
    "SQL", "POSTGRESQL", "MONGODB", "REDIS",
    # Deployment / tools
    "DOCKER", "KUBERNETES", "AWS", "GCP", "GIT",
]

# Cloud Engineer (team-defined): cloud platforms -> containers/orchestration ->
# infrastructure as code -> CI/CD -> OS & scripting -> database -> version control.
_CLOUD_ENGINEER: list[str] = [
    # Cloud platforms
    "AWS", "AZURE", "GCP",
    # Containers / orchestration
    "DOCKER", "KUBERNETES", "HELM",
    # Infrastructure as code
    "TERRAFORM", "ANSIBLE",
    # CI/CD
    "JENKINS", "GITHUB", "GITLAB",
    # OS / scripting
    "LINUX", "PYTHON", "GO",
    # Database
    "POSTGRESQL", "MYSQL", "MONGODB", "REDIS", "SQL",
    # Version control
    "GIT",
]

# Canonical order per profile, keyed by the profile identifier used in the CLI.
PROFILE_ORDER: dict[str, list[str]] = {
    "full_stack": _FULL_STACK,
    "machine_learning": _MACHINE_LEARNING,
    "ai_engineer": _AI_ENGINEER,
    "cloud_engineer": _CLOUD_ENGINEER,
}


def available_profiles() -> list[str]:
    """Return the profile identifiers that define a canonical order."""
    return list(PROFILE_ORDER)


def sort_qualifications(canonical: list[str], profile: str) -> list[str]:
    """Reorder ``canonical`` symbols into ``profile``'s canonical order.

    Symbols listed in the profile order come first, in that order; any
    remaining symbols are appended in their original (first-seen) order.

    Args:
        canonical: Normalized canonical symbols (already de-duplicated).
        profile: A key of :data:`PROFILE_ORDER`.

    Returns:
        The reordered list.

    Raises:
        KeyError: If ``profile`` has no defined order.
    """
    if profile not in PROFILE_ORDER:
        raise KeyError(
            f"Unknown profile {profile!r}; available: {', '.join(PROFILE_ORDER)}"
        )
    order = PROFILE_ORDER[profile]
    rank = {symbol: index for index, symbol in enumerate(order)}
    present = set(canonical)

    ordered = [symbol for symbol in order if symbol in present]
    remaining = [symbol for symbol in canonical if symbol not in rank]
    return ordered + remaining
