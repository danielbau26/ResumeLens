"""Regular-expression catalogue for Stage 1 (information extraction).

Each :class:`PatternSpec` bundles a regular expression together with a
human-readable description of the *language* (set of strings) it recognizes.
This keeps the formal definition required by the assignment next to its
Python ``re`` implementation.

The extraction stage only *detects* candidate information; it does **not**
decide whether two surface forms are equivalent (that is Stage 2 —
normalization). Therefore the patterns below deliberately accept the common
spelling/abbreviation variants that appear in real résumés (e.g. ``JS``,
``Javascript``, ``JavaScript``) and leave the canonicalization to the
transducers of the next stage.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class PatternSpec:
    """A named regular expression with its recognized language documented.

    Attributes:
        name: Category identifier (e.g. ``"programming_languages"``).
        description: Plain-language description of the pattern/language it
            recognizes, used in the design documentation.
        regex: Compiled regular expression applied to the résumé text.
    """

    name: str
    description: str
    regex: re.Pattern[str]


# Case-insensitive matching is used throughout so that résumé casing does not
# hide a qualification; word boundaries avoid matching inside larger tokens.
_FLAGS = re.IGNORECASE

# --- Word-like helpers -------------------------------------------------------
# A left boundary that does not treat "." or "+" as separators, so that tokens
# such as "React.js", "Node.js", "C++" or "C#" are matched as a whole.
_LB = r"(?<![\w.+#])"
_RB = r"(?![\w+#])"


def _alt(*options: str) -> str:
    """Build a non-capturing alternation from already-escaped options."""
    return r"(?:" + r"|".join(options) + r")"


# --- 1. Contact information --------------------------------------------------
# Language: standard e-mail addresses, phone numbers and profile URLs.
EMAIL = PatternSpec(
    name="email",
    description=(
        "E-mail addresses: a local part of word characters, dots, plus, "
        "underscore or hyphen, followed by '@', a domain, and a TLD of at "
        "least two letters."
    ),
    regex=re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", _FLAGS),
)

PHONE = PatternSpec(
    name="phone",
    description=(
        "Phone numbers: an optional '+' country prefix followed by 7 to 15 "
        "digits, allowing spaces, dots, hyphens and parentheses as separators."
    ),
    regex=re.compile(
        r"(?<!\w)(?:\+\d{1,3}[\s.\-]?)?(?:\(\d{1,4}\)[\s.\-]?)?"
        r"\d{3}[\s.\-]?\d{3,4}[\s.\-]?\d{0,4}(?!\w)",
        _FLAGS,
    ),
)

URL = PatternSpec(
    name="url",
    description=(
        "Web/profile URLs: either an explicit scheme/'www.' prefix followed "
        "by a host and optional path, or a bare LinkedIn/GitHub/GitLab "
        "profile link. The prefix requirement avoids matching dotted tokens "
        "such as 'React.js'."
    ),
    regex=re.compile(
        _alt(
            r"(?:https?://|www\.)[A-Za-z0-9\-.]+\.[A-Za-z]{2,}(?:/[^\s,;]*[^\s,;.])?",
            r"(?:linkedin|github|gitlab)\.com(?:/[^\s,;]*[^\s,;.])?",
        ),
        _FLAGS,
    ),
)

# --- 2. Programming languages ------------------------------------------------
# Language: the surface forms (incl. abbreviations) of the programming
# languages relevant to the supported profiles.
PROGRAMMING_LANGUAGES = PatternSpec(
    name="programming_languages",
    description=(
        "Programming languages relevant to the supported profiles, including "
        "spelling variants and abbreviations (e.g. JavaScript/Javascript/JS)."
    ),
    regex=re.compile(
        _LB
        + _alt(
            r"JavaScript", r"Javascript", r"JS",
            r"TypeScript", r"TS",
            r"Python", r"Py",
            r"Java(?!Script)",
            r"C\+\+", r"C#", r"C",
            r"Go(?:lang)?",
            r"Rust",
            r"Ruby",
            r"PHP",
            r"Kotlin",
            r"Swift",
            r"Scala",
            r"R",
        )
        + _RB,
        _FLAGS,
    ),
)

# --- 3. Frameworks and libraries ---------------------------------------------
FRAMEWORKS = PatternSpec(
    name="frameworks_libraries",
    description=(
        "Frameworks and libraries (frontend, backend and ML), including "
        "spelling variants (e.g. React/React.js/ReactJS, Node.js/NodeJS, "
        "Scikit-learn/sklearn/scikit learn)."
    ),
    regex=re.compile(
        _LB
        + _alt(
            r"React(?:\.js|JS)?", r"Angular", r"Vue(?:\.js|JS)?",
            r"Node(?:\.js|JS)?",
            r"Django", r"Flask", r"FastAPI",
            r"Spring\s?Boot", r"Spring",
            r"Express(?:\.js|JS)?",
            r"Pandas", r"NumPy",
            r"Scikit[\s\-]?learn", r"sklearn",
            r"TensorFlow", r"Tensor\s?Flow",
            r"PyTorch", r"Py\s?Torch",
            r"Keras",
            r"\.NET",
        )
        + _RB,
        _FLAGS,
    ),
)

# --- 4. Databases ------------------------------------------------------------
DATABASES = PatternSpec(
    name="databases",
    description=(
        "SQL and NoSQL database technologies, including spelling variants "
        "(e.g. Postgres/PostgreSQL, Mongo/MongoDB)."
    ),
    regex=re.compile(
        _LB
        + _alt(
            r"PostgreSQL", r"PostgreSQL", r"Postgres",
            r"MySQL", r"MariaDB",
            r"SQLite",
            r"MongoDB", r"Mongo",
            r"Redis",
            r"Cassandra",
            r"DynamoDB",
            r"Oracle",
            r"SQL\s?Server",
            r"NoSQL",
            r"SQL",
        )
        + _RB,
        _FLAGS,
    ),
)

# --- 5. Tools and technologies ----------------------------------------------
TOOLS = PatternSpec(
    name="tools_technologies",
    description=(
        "Tools, platforms and technologies such as version control, "
        "containers, CI/CD and cloud providers."
    ),
    regex=re.compile(
        _LB
        + _alt(
            r"Git(?:Hub|Lab)?",
            r"Docker", r"Kubernetes", r"K8s",
            r"Jenkins",
            r"Terraform", r"Ansible",
            r"AWS", r"Amazon\s?Web\s?Services",
            r"Azure",
            r"GCP", r"Google\s?Cloud",
            r"REST\s?APIs?", r"REST",
            r"GraphQL",
            r"Linux",
        )
        + _RB,
        _FLAGS,
    ),
)

# --- 6. Academic qualifications ---------------------------------------------
# Language: academic degrees and the field they are awarded in.
ACADEMIC = PatternSpec(
    name="academic_qualifications",
    description=(
        "Academic degrees (BSc/MSc/PhD/Bachelor/Master/etc.), optionally "
        "followed by the field of study."
    ),
    regex=re.compile(
        r"\b"
        + _alt(
            r"Ph\.?\s?D", r"Doctorate",
            r"M\.?Sc", r"Master(?:'s)?(?:\s+of\s+Science)?",
            r"B\.?Sc", r"Bachelor(?:'s)?(?:\s+of\s+Science)?",
            r"B\.?A", r"M\.?B\.?A",
            r"Associate(?:'s)?\s+Degree",
            r"Engineer(?:ing)?\s+Degree",
        )
        + r"(?:\s+(?:of|in)\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3})?",
        re.UNICODE,
    ),
)

# --- 7. Professional experience ---------------------------------------------
# Language: "<n> year(s) of experience [in/developing ...]".
EXPERIENCE = PatternSpec(
    name="professional_experience",
    description=(
        "Years of professional experience: a number (digits or spelled out) "
        "followed by 'year(s) of experience' and an optional area/activity."
    ),
    regex=re.compile(
        r"\b(?:\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten)\+?\s+"
        r"years?\s+of\s+experience"
        r"(?:\s+(?:in|developing|with|building)\s+[^.,;\n]+)?",
        _FLAGS,
    ),
)


# Ordered catalogue applied by the extractor.
PATTERNS: list[PatternSpec] = [
    EMAIL,
    PHONE,
    URL,
    PROGRAMMING_LANGUAGES,
    FRAMEWORKS,
    DATABASES,
    TOOLS,
    ACADEMIC,
    EXPERIENCE,
]

# Categories that represent technical qualifications (fed to later stages).
QUALIFICATION_CATEGORIES: tuple[str, ...] = (
    "programming_languages",
    "frameworks_libraries",
    "databases",
    "tools_technologies",
)
