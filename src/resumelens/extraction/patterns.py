# Stage 1 - Regular expressions to pull information out of the résumé.
# Each category has its own regex. The extractor applies them in PATTERNS order.
#
# LB and RB are hand-made word "boundaries". We don't use \b because \b does not
# play well with React.js, C++ or C# (the dot, the + and the # are not letters).
#   LB = no letter, digit, dot, + or # before   ("js" in "React.js" won't match alone)
#   RB = no letter, digit, + or # after          ("Java" in "JavaScript" won't match)

LB = r"(?<![\w.+#])"
RB = r"(?![\w+#])"

# contact

# user@domain.com
# - the user part may contain dots, but not two in a row (juan..perez is invalid)
# - the boundaries stop it from sticking to other letters
EMAIL_REGEX = (
    r"(?<![\w.+-])"
    r"[A-Za-z0-9_%+-]+(?:\.[A-Za-z0-9_%+-]+)*"   # user: juan.perez
    r"@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*"        # @gmail / @mail.icesi
    r"\.[A-Za-z]{2,}"                            # .com / .co
    r"(?![\w-])"
)

# +57 300 123 4567 / (602) 555 0142 / 602-555-0142 / 3001234567
PHONE_REGEX = (
    r"(?<!\d)"
    r"(?!(?:19|20)\d{2}\s?[-–]\s?(?:19|20)\d{2}(?!\d))"   # not a year range: 2019-2023
    r"(?:\+?\d{1,3}[\s.-]?)?"                              # optional country code: +57
    r"(?:\(?\d{2,4}\)?[\s.-]?)?"                           # optional area code: (602)
    r"\d{3}[\s.-]?\d{3,4}"                                 # number: 555 0142
    r"(?:[\s.-]?\d{2,4})?"                                 # optional final block
    r"(?!\d)"
)

# https://... / www.... / linkedin.com/in/... / github.com/...
# that prefix is required so "React.js" is not taken as a link
URL_REGEX = (
    r"(?:https?://|www\.)[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}(?:/[^\s,;]*[^\s,;.])?"
    r"|(?:linkedin|github|gitlab)\.com(?:/[^\s,;]*[^\s,;.])?"
)

# technical skills
# Longer forms go first: "JavaScript" before "JS", "PostgreSQL" before "Postgres".

LANGUAGES_REGEX = LB + (
    r"(?:JavaScript|JS|TypeScript|TS|Python|Java|C\+\+|C#|Golang"
    r"|Ruby|PHP|Kotlin|Swift|Rust|Scala|Bash)"
) + RB

FRAMEWORKS_REGEX = LB + (
    r"(?:React(?:\.js|JS)?|Angular|Vue(?:\.js|JS)?|Node(?:\.js|JS)?|Express"
    r"|Django|Flask|FastAPI|Spring\s?Boot"
    r"|Pandas|NumPy|Scikit[\s-]?learn|sklearn|Tensor\s?Flow|Py\s?Torch|Keras"
    r"|PySpark|Spark|Hugging\s?Face)"
) + RB

DATABASES_REGEX = LB + (
    r"(?:PostgreSQL|Postgres|MySQL|SQLite|MongoDB|Mongo|Redis|Oracle|NoSQL|SQL)"
) + RB

TOOLS_REGEX = LB + (
    r"(?:GitHub|GitLab|Git|Docker|Kubernetes|K8s|Helm|Jenkins|Terraform|Ansible"
    r"|AWS|Azure|GCP|REST\s?APIs?|GraphQL|Linux)"
) + RB

# education and experience

# BSc / MSc / PhD / Bachelor / Master... + optional "in Computer Science"
# (the field must start with an uppercase letter, which is why this regex runs WITHOUT IGNORECASE)
ACADEMIC_REGEX = (
    r"\b(?:Ph\.?\s?D|M\.?Sc|B\.?Sc|MBA|Master(?:'s)?|Bachelor(?:'s)?)"
    r"(?:\s+(?:of|in)\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3})?"
)

# "3 years of experience developing web applications"
EXPERIENCE_REGEX = (
    r"\b(?:\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten)\+?\s+"
    r"years?\s+of\s+experience"
    r"(?:\s+(?:in|developing|with|building)\s+[^.,;\n]+)?"
)

# other competencies
# "machine learning", "data processing", "web applications"...
OTHER_REGEX = (
    r"\b(?:machine[\s-]learning|deep[\s-]learning|data[\s-]processing"
    r"|predictive\s+models?|web\s+(?:applications?|development)"
    r"|microservices|CI/CD)\b"
)

# catalogue
# category -> regex  (applied in this order)
PATTERNS = {
    "emails": EMAIL_REGEX,
    "phones": PHONE_REGEX,
    "urls": URL_REGEX,
    "programming_languages": LANGUAGES_REGEX,
    "frameworks_libraries": FRAMEWORKS_REGEX,
    "databases": DATABASES_REGEX,
    "tools_technologies": TOOLS_REGEX,
    "academic_qualifications": ACADEMIC_REGEX,
    "professional_experience": EXPERIENCE_REGEX,
    "other_qualifications": OTHER_REGEX,
}

# These categories are the skills handed to stage 2
QUALIFICATION_CATEGORIES = ["programming_languages", "frameworks_libraries",
                            "databases", "tools_technologies"]
