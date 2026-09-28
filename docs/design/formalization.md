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

Each transformation rule (`src/resumelens/normalization/transformations.py`) is compiled into a
**character-level** finite-state transducer with pyformlang (`transducers.py`). Design:

- The input alphabet **Σ** is the set of characters of the accepted variants; matching is performed on
  a **case-folded** token, so casing variants (`JS` / `js`) share paths and Σ stays lowercase.
- The output alphabet **Γ** is the singleton canonical symbol (e.g. `{JAVASCRIPT}`).
- Every variant is a path of fresh states from the start state `q0` that converges on a single
  accepting state `qf`. The canonical symbol is emitted on the **first** transition of each path (the
  output relation **ω**); all later transitions output ε.
- Because different variants that share a first character create distinct transitions out of `q0`,
  these are **nondeterministic** finite-state transducers (an NFST). `translate` explores all paths and
  returns the canonical symbol for an accepted word, and nothing for a rejected one.

The authoritative construction is in code; the graphical representations are exported as Graphviz
files in [`docs/design/diagrams/`](diagrams/) (`*.dot`, one per transducer). Below are three
representative 7-tuples.

Notation: `q0` = start, `qf` = accepting, `sᵢ` = intermediate states. δ is written as
`(state, input) → state`; ω as `(state, input) → output`.

### 2.1 `M_JAVASCRIPT` — {JS, Javascript, JavaScript} → JAVASCRIPT

Diagram: [`diagrams/JAVASCRIPT.dot`](diagrams/JAVASCRIPT.dot) · |Q| = 21, |δ| = 22.

- **Q**: `{q0, qf}` ∪ intermediate states, one chain per variant (`js`, `javascript`, `javascript`
  again for the mixed-case form, all folded to `javascript`).
- **Σ**: `{j, s, a, v, c, r, i, p, t}` (characters of the folded variants).
- **Γ**: `{JAVASCRIPT}`.
- **δ**: three character-chains from `q0` to `qf`, e.g. for `js`: `(q0,j)→s1, (s1,s)→qf`; for
  `javascript`: `(q0,j)→s2, (s2,a)→s3, …, (s10,t)→qf`.
- **ω**: emits `JAVASCRIPT` on the first transition of each chain, ε afterwards, e.g.
  `(q0,j)→JAVASCRIPT`, `(s1,s)→ε`.
- **q0**: `q0`.
- **F**: `{qf}`.

### 2.2 `M_REACT` — {React, React.js, ReactJS} → REACT

Diagram: [`diagrams/REACT.dot`](diagrams/REACT.dot) · |Q| = 19, |δ| = 20.

- **Q**: `{q0, qf}` ∪ intermediate states for the three variant chains.
- **Σ**: `{r, e, a, c, t, ., j, s}`.
- **Γ**: `{REACT}`.
- **δ**: chains `react`, `react.js`, `reactjs` from `q0` to `qf` (the `.` and the `js`/`JS` suffixes are
  ordinary input characters after case folding).
- **ω**: `REACT` on the first transition of each chain, ε afterwards.
- **q0**: `q0`. **F**: `{qf}`.

### 2.3 `M_SCIKIT_LEARN` — {Scikit-learn, scikit learn, sklearn} → SCIKIT_LEARN

Diagram: [`diagrams/SCIKIT_LEARN.dot`](diagrams/SCIKIT_LEARN.dot) · |Q| = 30, |δ| = 31.

- **Q**: `{q0, qf}` ∪ intermediate states for the three chains.
- **Σ**: `{s, c, i, k, t, -, (space), l, e, a, r, n}` — note the hyphen and the space are distinct input
  symbols, which is exactly the naming-variation this stage must absorb.
- **Γ**: `{SCIKIT_LEARN}`.
- **δ**: chains `scikit-learn`, `scikit␣learn`, `sklearn` from `q0` to `qf`.
- **ω**: `SCIKIT_LEARN` on the first transition of each chain, ε afterwards.
- **q0**: `q0`. **F**: `{qf}`.

### 2.4 Combined transducer

`combined_transducer()` unions all per-rule FSTs into a single machine (≈513 states, 493 transitions)
whose Γ is the full set of canonical symbols — the "one transducer" view of the whole normalization
stage.

### 2.5 Sorting into profile canonical order

After transduction the canonical symbols are de-duplicated and reordered into the order defined by the
selected profile (`ordering.py`), so the Stage 3 input does not depend on the résumé's wording. All
four supported profiles define an order (kept in Stage 2 so the Stage 3 recognition module only builds
automata and consumes the already-sorted sequence):

| Profile (`--profile`) | Canonical order (grouped) |
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
