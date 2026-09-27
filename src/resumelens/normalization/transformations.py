"""Transformation catalogue for Stage 2 (qualification normalization).

The same qualification is written in many ways across résumés (``JS``,
``Javascript``, ``JavaScript`` …). This module declares, as data, the set of
*transformations* that map every surface form the extraction stage can emit
(see :data:`resumelens.extraction.patterns.QUALIFICATION_CATEGORIES`) onto a
single **canonical** representation.

These canonical forms are the output alphabet symbols (Γ) of the finite-state
transducers built in :mod:`resumelens.normalization.transducers`. Canonical
forms use ``UPPER_SNAKE_CASE`` so they are unambiguous and stable as input for
the Stage 3 recognition automata.

.. note::
   Per the assignment, these transformations are our own proposal; they cover
   at least the illustrative examples given in the statement (JS, React,
   NodeJS, Postgres, pandas, sklearn, TensorFlow, PyTorch …).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TransductionRule:
    """A canonical qualification together with the surface forms it accepts.

    Attributes:
        canonical: The canonical output symbol (Γ), e.g. ``"JAVASCRIPT"``.
        variants: The surface forms (Σ*) that must be mapped to ``canonical``,
            e.g. ``["JS", "Javascript", "JavaScript"]``.
        category: The extraction category this qualification belongs to, one of
            :data:`resumelens.extraction.patterns.QUALIFICATION_CATEGORIES`.
    """

    canonical: str
    variants: list[str]
    category: str


# --- Programming languages ---------------------------------------------------
_LANGUAGES: list[TransductionRule] = [
    TransductionRule("JAVASCRIPT", ["JavaScript", "Javascript", "JS"], "programming_languages"),
    TransductionRule("TYPESCRIPT", ["TypeScript", "TS"], "programming_languages"),
    TransductionRule("PYTHON", ["Python", "Py"], "programming_languages"),
    TransductionRule("JAVA", ["Java"], "programming_languages"),
    TransductionRule("CPP", ["C++"], "programming_languages"),
    TransductionRule("CSHARP", ["C#"], "programming_languages"),
    TransductionRule("GO", ["Go", "Golang"], "programming_languages"),
    TransductionRule("RUBY", ["Ruby"], "programming_languages"),
    TransductionRule("PHP", ["PHP"], "programming_languages"),
    TransductionRule("KOTLIN", ["Kotlin"], "programming_languages"),
    TransductionRule("SWIFT", ["Swift"], "programming_languages"),
]

# --- Frameworks and libraries ------------------------------------------------
_FRAMEWORKS: list[TransductionRule] = [
    TransductionRule("REACT", ["React", "React.js", "ReactJS"], "frameworks_libraries"),
    TransductionRule("ANGULAR", ["Angular"], "frameworks_libraries"),
    TransductionRule("VUE", ["Vue", "Vue.js", "VueJS"], "frameworks_libraries"),
    TransductionRule("NODE_JS", ["NodeJS", "Node.js", "Node"], "frameworks_libraries"),
    TransductionRule("DJANGO", ["Django"], "frameworks_libraries"),
    TransductionRule("FLASK", ["Flask"], "frameworks_libraries"),
    TransductionRule("FASTAPI", ["FastAPI"], "frameworks_libraries"),
    TransductionRule("SPRING_BOOT", ["Spring Boot", "SpringBoot", "Spring"], "frameworks_libraries"),
    TransductionRule("EXPRESS", ["Express", "Express.js", "ExpressJS"], "frameworks_libraries"),
    TransductionRule("PANDAS", ["Pandas", "pandas"], "frameworks_libraries"),
    TransductionRule("NUMPY", ["NumPy", "Numpy"], "frameworks_libraries"),
    TransductionRule("SCIKIT_LEARN", ["Scikit-learn", "scikit learn", "sklearn"], "frameworks_libraries"),
    TransductionRule("TENSORFLOW", ["TensorFlow", "Tensor Flow"], "frameworks_libraries"),
    TransductionRule("PYTORCH", ["PyTorch", "Py Torch"], "frameworks_libraries"),
    TransductionRule("KERAS", ["Keras"], "frameworks_libraries"),
    TransductionRule("SPARK", ["Apache Spark", "PySpark", "Spark"], "frameworks_libraries"),
    TransductionRule("HUGGING_FACE", ["Hugging Face", "HuggingFace"], "frameworks_libraries"),
]

# --- Databases ---------------------------------------------------------------
_DATABASES: list[TransductionRule] = [
    TransductionRule("POSTGRESQL", ["PostgreSQL", "Postgres"], "databases"),
    TransductionRule("MYSQL", ["MySQL"], "databases"),
    TransductionRule("MARIADB", ["MariaDB"], "databases"),
    TransductionRule("SQLITE", ["SQLite"], "databases"),
    TransductionRule("MONGODB", ["MongoDB", "Mongo"], "databases"),
    TransductionRule("REDIS", ["Redis"], "databases"),
    TransductionRule("NOSQL", ["NoSQL"], "databases"),
    TransductionRule("SQL", ["SQL"], "databases"),
]

# --- Tools and technologies --------------------------------------------------
_TOOLS: list[TransductionRule] = [
    TransductionRule("GIT", ["Git"], "tools_technologies"),
    TransductionRule("GITHUB", ["GitHub"], "tools_technologies"),
    TransductionRule("GITLAB", ["GitLab"], "tools_technologies"),
    TransductionRule("DOCKER", ["Docker"], "tools_technologies"),
    TransductionRule("KUBERNETES", ["Kubernetes", "K8s"], "tools_technologies"),
    TransductionRule("JENKINS", ["Jenkins"], "tools_technologies"),
    TransductionRule("TERRAFORM", ["Terraform"], "tools_technologies"),
    TransductionRule("ANSIBLE", ["Ansible"], "tools_technologies"),
    TransductionRule("HELM", ["Helm"], "tools_technologies"),
    TransductionRule("AWS", ["AWS", "Amazon Web Services"], "tools_technologies"),
    TransductionRule("AZURE", ["Azure"], "tools_technologies"),
    TransductionRule("GCP", ["GCP", "Google Cloud"], "tools_technologies"),
    TransductionRule("REST_API", ["REST API", "REST APIs", "REST"], "tools_technologies"),
    TransductionRule("GRAPHQL", ["GraphQL"], "tools_technologies"),
    TransductionRule("LINUX", ["Linux"], "tools_technologies"),
]

# Ordered catalogue of every transformation rule.
RULES: list[TransductionRule] = [*_LANGUAGES, *_FRAMEWORKS, *_DATABASES, *_TOOLS]


def canonical_forms() -> list[str]:
    """Return the list of canonical output symbols (Γ), in catalogue order."""
    return [rule.canonical for rule in RULES]


def rule_for_canonical(canonical: str) -> TransductionRule | None:
    """Return the rule producing ``canonical`` (or ``None`` if unknown)."""
    for rule in RULES:
        if rule.canonical == canonical:
            return rule
    return None
