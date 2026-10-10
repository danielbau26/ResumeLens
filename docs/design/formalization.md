# Formalization

## 1. Regular Expressions (Stage 1 — Extraction)

For each relevant information type we define a regular expression, explain the language / textual
pattern it recognizes, and implement it with Python's `re` module. The regexes are plain string
constants in `src/resumelens/extraction/patterns.py` and are collected in `PATTERNS`
(a `dict[str, str]` mapping each category to its regex); the extraction driver is
`src/resumelens/extraction/extractor.py`.

Notation used below: `LB = (?<![\w.+#])` and `RB = (?![\w+#])` are left/right boundaries that treat
`.`, `+`, `#` as part of a token, so `React.js`, `Node.js`, `C++` and `C#` are matched whole. Most
patterns match case-insensitively (academic degrees are the exception — they need the uppercase field
name). To avoid re-reading a URL host as a tool (e.g. `github` inside `github.com/...`), the extractor
first blanks emails and URLs with `re.sub` and searches the remaining categories on that cleaned text.

| Category | Regular Expression (core) | Language Recognized |
|---|---|---|
| `emails` | `[A-Za-z0-9_%+-]+(?:\.[A-Za-z0-9_%+-]+)*@[A-Za-z0-9-]+(?:\.[…])*\.[A-Za-z]{2,}` | A local part (dots allowed, not doubled), `@`, a domain and a TLD of ≥2 letters. |
| `phones` | `(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3}[\s.-]?\d{3,4}(?:[\s.-]?\d{2,4})?` | Phone numbers with optional country/area code; a lookahead rejects year ranges like `2019-2023`. |
| `urls` | `(?:https?://\|www\.)…` or `(?:linkedin\|github\|gitlab)\.com(?:/…)?` | Web/profile URLs with an explicit scheme/`www.` prefix, or bare LinkedIn/GitHub/GitLab links. The prefix requirement prevents matching dotted tokens such as `React.js`. |
| `programming_languages` | `LB (?:JavaScript\|JS\|TypeScript\|TS\|Python\|Java\|C\+\+\|C#\|Golang\|Ruby\|PHP\|Kotlin\|Swift\|Rust\|Scala\|Bash) RB` | Programming languages (longer forms listed first, e.g. `JavaScript` before `JS`). |
| `frameworks_libraries` | `LB (?:React(?:\.js\|JS)?\|Angular\|Vue(?:\.js\|JS)?\|Node(?:\.js\|JS)?\|Express\|Django\|Flask\|FastAPI\|Spring\s?Boot\|Pandas\|NumPy\|Scikit[\s-]?learn\|sklearn\|Tensor\s?Flow\|Py\s?Torch\|Keras\|PySpark\|Spark\|Hugging\s?Face) RB` | Frontend/backend/ML frameworks and libraries with their spelling variants. |
| `databases` | `LB (?:PostgreSQL\|Postgres\|MySQL\|SQLite\|MongoDB\|Mongo\|Redis\|Oracle\|NoSQL\|SQL) RB` | SQL and NoSQL database technologies with variants. |
| `tools_technologies` | `LB (?:GitHub\|GitLab\|Git\|Docker\|Kubernetes\|K8s\|Helm\|Jenkins\|Terraform\|Ansible\|AWS\|Azure\|GCP\|REST\s?APIs?\|GraphQL\|Linux) RB` | Version control, containers, CI/CD and cloud providers. |
| `academic_qualifications` | `\b(?:Ph\.?\s?D\|M\.?Sc\|B\.?Sc\|MBA\|Master(?:'s)?\|Bachelor(?:'s)?)(?:\s+(?:of\|in)\s+[A-Z]\w+…)?` | An academic degree, optionally followed by the field of study (matched **without** IGNORECASE). |
| `professional_experience` | `\b(?:\d{1,2}\|one\|…\|ten)\+?\s+years?\s+of\s+experience(?:\s+(?:in\|developing\|with\|building)\s+[^.,;\n]+)?` | "<n> year(s) of experience …" with an optional area/activity. |
| `other_qualifications` | `\b(?:machine[\s-]learning\|deep[\s-]learning\|data[\s-]processing\|predictive\s+models?\|web\s+(?:applications?\|development)\|microservices\|CI/CD)\b` | Free-text competencies relevant to the profiles. |

> The table shows the essential structure of each regex; the authoritative, fully-commented
> definitions are the string constants in `patterns.py`.

## 2. Finite-State Transducers (Stage 2 — Normalization)

Each entry of the transformation catalogue (`VARIANTS`, a plain `dict[str, list[str]]` of lowercase
variants in `src/resumelens/normalization/transformations.py`) is compiled by
`build_transducer(canonical)` into a **character-level** finite-state transducer with pyformlang
(`transducers.py`). `formal_definition(canonical)` returns the complete 7-tuple programmatically, and
`draw_transducer(canonical)` produces its diagram. Design:

- The input alphabet **Σ** is the set of characters of the accepted variants; the input word is
  lower-cased before translating, so casing variants (`JS` / `js`) are the same input.
- The output alphabet **Γ** is the singleton canonical symbol (e.g. `{JAVASCRIPT}`).
- Each variant is a path from the start state `q0` to an accepting state. The canonical symbol is
  emitted on the **first** transition of each path (the output relation **ω**); all later transitions
  output ε.
- Variants that **share a prefix share states** (a shared `(state, letter)` edge is reused), so from
  every state there is at most one transition per letter: these are **deterministic** finite-state
  transducers (DFST). `translate` follows the single path and returns the canonical symbol for an
  accepted word, or nothing for a rejected one.

The authoritative construction is in code; the graphical representations are exported as Graphviz
files in [`docs/design/diagrams/`](diagrams/) (`*.dot`, one per transducer). Below are three
representative 7-tuples.

Notation: `q0` = start, `qf` = accepting, `sᵢ` = intermediate states. δ is written as
`(state, input) → state`; ω as `(state, input) → output`.

### 2.1 `M_JAVASCRIPT` — {js, javascript} → JAVASCRIPT

Diagram: [`diagrams/JAVASCRIPT.dot`](diagrams/JAVASCRIPT.dot) · |Q| = 12, |δ| = 11, F = `{q2, q11}`.

- **Q**: `{q0, …, q11}`. Both variants share the first edge `(q0,j)→q1`; `js` ends at `q2`,
  `javascript` continues `q1 → … → q11`.
- **Σ**: `{j, s, a, v, c, r, i, p, t}`.
- **Γ**: `{JAVASCRIPT}`.
- **δ**: `(q0,j)→q1, (q1,s)→q2` (path `js`); `(q1,a)→q3, (q3,v)→q4, …, (q10,t)→q11` (path `javascript`).
- **ω**: `JAVASCRIPT` on the first transition `(q0,j)`, ε on every later transition.
- **q0**: `q0`. **F**: `{q2, q11}` (one accepting state per variant end).

### 2.2 `M_REACT` — {react, react.js, reactjs} → REACT

Diagram: [`diagrams/REACT.dot`](diagrams/REACT.dot) · |Q| = 11, |δ| = 10, F = `{q5, q8, q10}`.

- **Q**: `{q0, …, q10}`. The three variants share the common prefix `react` (`q0 → … → q5`); then
  `react.js` goes `q5 →.→ q6 → j → q7 → s → q8` and `reactjs` goes `q5 → j → q9 → s → q10`.
- **Σ**: `{r, e, a, c, t, ., j, s}`.
- **Γ**: `{REACT}`.
- **ω**: `REACT` on `(q0,r)`, ε afterwards.
- **q0**: `q0`. **F**: `{q5, q8, q10}`.

### 2.3 `M_SCIKIT_LEARN` — {scikit-learn, scikit learn, scikitlearn, sklearn} → SCIKIT_LEARN

Diagram: [`diagrams/SCIKIT_LEARN.dot`](diagrams/SCIKIT_LEARN.dot) · |Q| = 30, |δ| = 29, F has 4 states.

- **Q**: `{q0, …, q29}` — the four variants share prefixes where possible (`sc…`, `sk…`).
- **Σ**: `{s, c, i, k, t, -, (space), l, e, a, r, n}` — the hyphen and the space are distinct input
  symbols, which is exactly the naming-variation this stage must absorb.
- **Γ**: `{SCIKIT_LEARN}`.
- **ω**: `SCIKIT_LEARN` on the first transition, ε afterwards.
- **q0**: `q0`. **F**: one accepting state per variant end.

> These tuples are produced programmatically by `formal_definition(canonical)` in `transducers.py`.

### 2.4 Determinism

Because variants that share a prefix share states, every `(state, letter)` pair has at most one target,
so each `M_canonical` is a **deterministic** finite-state transducer. There is one transducer per
canonical form (all built in `TRANSDUCERS`); `translate(word)` runs the word through them and returns
the single canonical output, or `None`.

### 2.5 Sorting into profile canonical order

After transduction the canonical symbols are de-duplicated and reordered for **each** profile
(`sort_for_all_profiles` in `ordering.py`), so the Stage 3 input does not depend on the résumé's
wording. Design decision: `sort_skills(canonical, profile)` keeps **only** the skills that appear in
that profile's order (a skill irrelevant to a profile is simply not sent to its automaton), which keeps
the Stage 3 automata simple. All four profiles define an order:

| Profile | Canonical order (grouped) |
|---|---|
| `full_stack` | Frontend → Backend → Database → Version control |
| `machine_learning` | Language → Data libs → ML libs → Database → Tools |
| `ai_engineer` | Language → Data → ML/DL libs → Big data & GenAI (SPARK, HUGGING_FACE) → Database → Deployment |
| `cloud_engineer` | Cloud platforms → Containers/orchestration (incl. HELM) → IaC → CI/CD → OS & scripting → Database → Version control |

Worked example (Full Stack):

```
Git, NodeJS, JS, Postgres, React.js
  --transduce-->  GIT, NODE_JS, JAVASCRIPT, POSTGRESQL, REACT
  --sort(full_stack)-->  JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT
```

`ai_engineer` and `cloud_engineer` are the two team-defined profiles; their qualification sets are our
design. Three canonical forms were added to the catalogue for them — `SPARK`, `HUGGING_FACE` (AI) and
`HELM` (Cloud) — end to end (extraction regex + transducers), so the pipeline stays consistent.

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
