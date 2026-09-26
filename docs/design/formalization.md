# Formalization

## 1. Regular Expressions (Stage 1 — Extraction)

For each relevant information type we define a regular expression, explain the language / textual
pattern it recognizes, and implement it with Python's `re` module. The catalogue lives in
`src/resumelens/extraction/patterns.py` (each `PatternSpec` stores the regex together with its
documented language); the extraction driver is `src/resumelens/extraction/extractor.py`.

Notation used below: `_LB = (?<![\w.+#])` and `_RB = (?![\w+#])` are left/right boundaries that treat
`.`, `+`, `#` as part of a token, so `React.js`, `Node.js`, `C++` and `C#` are matched whole. Matching
is case-insensitive. Patterns are applied in catalogue order and each accepted match *claims* its span,
so later patterns cannot match inside an earlier one (e.g. `github` is not re-extracted as a tool from
inside a `github.com/...` URL).

| Category | Regular Expression (core) | Language Recognized |
|---|---|---|
| `email` | `[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}` | A local part, `@`, a domain and a TLD of ≥2 letters. |
| `phone` | `(?:\+\d{1,3}[\s.\-]?)?(?:\(\d{1,4}\)[\s.\-]?)?\d{3}[\s.\-]?\d{3,4}[\s.\-]?\d{0,4}` | Optional `+` country prefix and 7–15 digits with space/dot/hyphen/parenthesis separators. |
| `url` | `(?:https?://\|www\.)[A-Za-z0-9\-.]+\.[A-Za-z]{2,}(?:/…)?` or `(?:linkedin\|github\|gitlab)\.com(?:/…)?` | Web/profile URLs with an explicit scheme/`www.` prefix, or bare LinkedIn/GitHub/GitLab links. The prefix requirement prevents matching dotted tokens such as `React.js`. |
| `programming_languages` | `_LB (?:JavaScript\|Javascript\|JS\|TypeScript\|TS\|Python\|Java(?!Script)\|C\+\+\|C#\|C\|Go(?:lang)?\|Rust\|Ruby\|PHP\|Kotlin\|Swift\|Scala\|R) _RB` | Surface forms and abbreviations of the programming languages relevant to the four profiles. |
| `frameworks_libraries` | `_LB (?:React(?:\.js\|JS)?\|Angular\|Vue(?:\.js\|JS)?\|Node(?:\.js\|JS)?\|Django\|Flask\|FastAPI\|Spring\s?Boot\|…\|Pandas\|NumPy\|Scikit[\s\-]?learn\|sklearn\|TensorFlow\|PyTorch\|Keras) _RB` | Frontend/backend/ML frameworks and libraries with their spelling variants. |
| `databases` | `_LB (?:PostgreSQL\|Postgres\|MySQL\|MariaDB\|SQLite\|MongoDB\|Mongo\|Redis\|…\|NoSQL\|SQL) _RB` | SQL and NoSQL database technologies with variants. |
| `tools_technologies` | `_LB (?:Git(?:Hub\|Lab)?\|Docker\|Kubernetes\|K8s\|Jenkins\|Terraform\|Ansible\|AWS\|Azure\|GCP\|REST\s?APIs?\|GraphQL\|Linux) _RB` | Version control, containers, CI/CD and cloud providers. |
| `academic_qualifications` | `\b(?:Ph\.?\s?D\|M\.?Sc\|Master…\|B\.?Sc\|Bachelor…\|…)(?:\s+(?:of\|in)\s+[A-Z]\w+…)?` | An academic degree, optionally followed by the field of study. |
| `professional_experience` | `\b(?:\d{1,2}\|one\|…\|ten)\+?\s+years?\s+of\s+experience(?:\s+(?:in\|developing\|with\|building)\s+[^.,;\n]+)?` | "<n> year(s) of experience …" with an optional area/activity. |

> The table shows the essential structure of each regex; the authoritative,
> fully-commented definitions are in `patterns.py`.

## 2. Finite-State Transducers (Stage 2 — Normalization)

For each transducer, provide the complete 7-tuple: M = (Q, Σ, Γ, δ, ω, q0, F)

- Q:
- Σ:
- Γ:
- δ:
- ω:
- q0:
- F:

Include a graphical representation of each transducer.

## 3. Finite Automata (Stage 3 — Qualification Pattern Recognition)

For each profile automaton, provide the complete 5-tuple: M = (Q, Σ, δ, q0, F)

- Q:
- Σ:
- δ:
- q0:
- F:
- Type (DFA / NFA / ε-NFA) and justification:

Include the transition diagram and an explanation of the profile pattern represented.

### Profile 1 — Full Stack Developer
### Profile 2 — Machine Learning Engineer
### Profile 3 — (Software engineering, team-defined)
### Profile 4 — (AI/data, team-defined)

## 4. Context-Free Grammar / DSL (Stage 4 — Candidate Profile Language)

Define the grammar in EBNF, identifying terminals and non-terminals, and explain the structural characteristics of the language.

```
(* EBNF grammar goes here *)
```
