# Formalization

## 1. Regular Expressions (Stage 1 — Extraction)

For each relevant information type we define a regular expression, explain the language / textual
pattern it recognizes, and implement it with Python's `re` module. All patterns live in
`src/resumelens/extraction/patterns.py`; the extraction driver is `src/resumelens/extraction/extractor.py`.

**Custom word boundaries.** `\b` treats `.`, `+` and `#` as separators, which breaks tokens such as
`React.js`, `C++` or `C#`. We therefore define our own boundaries:

- `LB = (?<![\w.+#])` — the token cannot be preceded by a letter, digit, `.`, `+` or `#`
  (so the `js` inside `React.js` is not extracted on its own).
- `RB = (?![\w+#])` — the token cannot be followed by a letter, digit, `+` or `#`
  (so `Java` is not extracted from `JavaScript`). A final `.` is allowed (`Git.`).

**Extraction rules.**

- Matching is case-insensitive (`re.IGNORECASE`), except for academic qualifications, whose field of
  study must start with an uppercase letter to know where it ends.
- Skills are searched in a copy of the text where e-mails and URLs were replaced by spaces, so that
  `github.com/jdoe` does not produce the tool `GitHub`.
- Matches are de-duplicated case-insensitively, keeping the first form and the order of appearance.
- The result is a dictionary (data structure) that can be saved as JSON (file).

| Category | Regular expression (core) | Language recognized |
|---|---|---|
| `emails` | `(?<![\w.+-])[A-Za-z0-9_%+-]+(?:\.[A-Za-z0-9_%+-]+)*@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}(?![\w-])` | A local part (dots allowed, but not two in a row), `@`, a domain with optional sub-domains and a TLD of at least 2 letters. |
| `phones` | `(?<!\d)(?!(?:19\|20)\d{2}\s?[-–]\s?(?:19\|20)\d{2}(?!\d))(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3}[\s.-]?\d{3,4}(?:[\s.-]?\d{2,4})?(?!\d)` | An optional country code, an optional area code (with or without parentheses) and a number of 6+ digits separated by spaces, dots or hyphens. A year range such as `2019-2023` is explicitly excluded. |
| `urls` | `(?:https?://\|www\.)host\.[A-Za-z]{2,}(?:/path)?` or `(?:linkedin\|github\|gitlab)\.com(?:/path)?` | Web addresses that start with `http(s)://` or `www.`, or bare LinkedIn/GitHub/GitLab profile links. The mandatory prefix prevents `React.js` from being taken as a URL. |
| `programming_languages` | `LB (?:JavaScript\|JS\|TypeScript\|TS\|Python\|Java\|C\+\+\|C#\|Golang\|Ruby\|PHP\|Kotlin\|Swift\|Rust\|Scala\|Bash) RB` | Names and abbreviations of programming languages. Single letters (`C`, `R`) and `Go` were excluded because, with case-insensitive matching, they produce false positives (e.g. the verb "go"). |
| `frameworks_libraries` | `LB (?:React(?:\.js\|JS)?\|Angular\|Vue(?:\.js\|JS)?\|Node(?:\.js\|JS)?\|Express\|Django\|Flask\|FastAPI\|Spring\s?Boot\|Pandas\|NumPy\|Scikit[\s-]?learn\|sklearn\|Tensor\s?Flow\|Py\s?Torch\|Keras\|PySpark\|Spark\|Hugging\s?Face) RB` | Frontend, backend, data and ML frameworks/libraries with their spelling variants (`React.js`, `ReactJS`, `Tensor Flow`, `scikit learn`...). |
| `databases` | `LB (?:PostgreSQL\|Postgres\|MySQL\|SQLite\|MongoDB\|Mongo\|Redis\|Oracle\|NoSQL\|SQL) RB` | SQL and NoSQL database technologies. Longer forms come first so `PostgreSQL` is not cut to `Postgres`. |
| `tools_technologies` | `LB (?:GitHub\|GitLab\|Git\|Docker\|Kubernetes\|K8s\|Helm\|Jenkins\|Terraform\|Ansible\|AWS\|Azure\|GCP\|REST\s?APIs?\|GraphQL\|Linux) RB` | Version control, containers, CI/CD, infrastructure as code, cloud providers, APIs and operating systems. |
| `academic_qualifications` | `\b(?:Ph\.?\s?D\|M\.?Sc\|B\.?Sc\|MBA\|Master(?:'s)?\|Bachelor(?:'s)?)(?:\s+(?:of\|in)\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3})?` | An academic degree, optionally followed by `of`/`in` and a field of study of up to 4 capitalized words (`MSc in Computer Science`). |
| `professional_experience` | `\b(?:\d{1,2}\|one\|…\|ten)\+?\s+years?\s+of\s+experience(?:\s+(?:in\|developing\|with\|building)\s+[^.,;\n]+)?` | "<n> year(s) of experience", with n as a number or a word, optionally followed by the area until the end of the phrase. |
| `other_qualifications` | `\b(?:machine[\s-]learning\|deep[\s-]learning\|data[\s-]processing\|predictive\s+models?\|web\s+(?:applications?\|development)\|microservices\|CI/CD)\b` | General competences relevant to the profiles that are not a specific technology. |

Only the four technical categories (`programming_languages`, `frameworks_libraries`, `databases`,
`tools_technologies`) are sent to Stage 2 (`get_skills`). The full dictionary (name, contact,
education, experience) is kept for Stage 4.

## 2. Finite-State Transducers (Stage 2 — Normalization)

Each row of the transformation table (`src/resumelens/normalization/transformations.py`) maps a
canonical form to its surface variants, e.g. `REACT ← {react, react.js, reactjs}`. Each row is compiled
into one **character-level** finite-state transducer with pyformlang (`transducers.py`).

**Design.**

- The input word is cleaned (extra spaces removed) and lower-cased before being read, so `JS`, `js`
  and `Js` follow the same path and Σ only contains lowercase characters.
- The transducer reads the word one character at a time. The **first** transition writes the
  canonical form; every other transition writes ε (nothing).
- Variants that start with the same characters **share** that part of the path (`react`, `react.js`
  and `reactjs` share `r-e-a-c-t`). Therefore from each state there is at most one transition per
  character: the transducers are **deterministic**.
- The state where each variant ends is an accepting state, so a transducer can have several final
  states. A word that is not a variant has no path or does not end in a final state, so `translate`
  produces no output and the token is reported as *unrecognized*.
- Writing the canonical form on the first transition (instead of the last) is required by the shared
  paths: `react` ends inside the path of `react.js`, so writing on the last character would output
  the canonical form twice.

The 7-tuple of any transducer is produced by `formal_definition(canonical)` and its diagram by
`draw_transducer(canonical)`. The Graphviz (`.dot`) file of every transducer is in [`diagrams/`](diagrams/).

### 2.1 `M_JAVASCRIPT` — {js, javascript} → JAVASCRIPT

- **Q** = {q0, q1, …, q11} (|Q| = 12)
- **Σ** = {j, s, a, v, c, r, i, p, t}
- **Γ** = {JAVASCRIPT}
- **δ**: δ(q0, j) = q1, δ(q1, s) = q2, δ(q1, a) = q3, δ(q3, v) = q4, δ(q4, a) = q5, δ(q5, s) = q6,
  δ(q6, c) = q7, δ(q7, r) = q8, δ(q8, i) = q9, δ(q9, p) = q10, δ(q10, t) = q11 (|δ| = 11)
- **ω**: ω(q0, j) = JAVASCRIPT; ω = ε for every other transition
- **q0** = q0
- **F** = {q2, q11}

### 2.2 `M_REACT` — {react, react.js, reactjs} → REACT

- **Q** = {q0, …, q10} (|Q| = 11)
- **Σ** = {r, e, a, c, t, ., j, s}
- **Γ** = {REACT}
- **δ**: δ(q0, r) = q1, δ(q1, e) = q2, δ(q2, a) = q3, δ(q3, c) = q4, δ(q4, t) = q5, δ(q5, .) = q6,
  δ(q6, j) = q7, δ(q7, s) = q8, δ(q5, j) = q9, δ(q9, s) = q10 (|δ| = 10)
- **ω**: ω(q0, r) = REACT; ω = ε for every other transition
- **q0** = q0
- **F** = {q5, q8, q10} — q5 is final (end of `react`) even though the path continues.

### 2.3 `M_SCIKIT_LEARN` — {scikit-learn, scikit learn, scikitlearn, sklearn} → SCIKIT_LEARN

- **Q** = {q0, …, q29} (|Q| = 30)
- **Σ** = {s, c, i, k, t, -, l, e, a, r, n, ␣} — the hyphen and the space are distinct input symbols,
  which is exactly the naming variation this transducer absorbs.
- **Γ** = {SCIKIT_LEARN}
- **δ**: the four variants share `s`; `sklearn` branches at `k`, and the other three share
  `s-c-i-k-i-t` and branch on `-`, `␣` or `l` (|δ| = 29).
- **ω**: ω(q0, s) = SCIKIT_LEARN; ω = ε for every other transition
- **q0** = q0
- **F** = {q12, q18, q23, q29}

### 2.4 Sorting into the profile canonical order

After transduction, the canonical forms are de-duplicated (`JS` and `JavaScript` give a single
`JAVASCRIPT`) and sorted with the order of each profile (`ordering.py`), so the input of Stage 3 does
not depend on how the candidate wrote the résumé.

Since Stage 2 does not know yet which profile the résumé belongs to, it produces **one sorted list per
profile** (`by_profile`). Each list contains **only** the canonical forms that belong to that profile
(design decision): a skill that is irrelevant for a profile is not sent to its automaton, which keeps
the automata simpler.

| Profile | Canonical order (grouped) |
|---|---|
| `full_stack` | Frontend (JAVASCRIPT, TYPESCRIPT, REACT, ANGULAR, VUE) → Backend (NODE_JS, DJANGO, SPRING_BOOT, EXPRESS, FASTAPI, FLASK) → Database (POSTGRESQL, MYSQL, MONGODB, SQL, NOSQL) → Version control / tools (GIT, GITHUB, DOCKER, KUBERNETES, REST_API, GRAPHQL) |
| `machine_learning` | Language (PYTHON) → Data (PANDAS, NUMPY) → ML libs (SCIKIT_LEARN, TENSORFLOW, PYTORCH, KERAS) → Database (SQL, POSTGRESQL, MONGODB) → Tools (GIT, DOCKER, AWS) |
| `ai_engineer` | Language → Data → ML/DL libs → Big data & GenAI (SPARK, HUGGING_FACE) → Database (SQL, POSTGRESQL, MONGODB, REDIS) → Deployment (DOCKER, KUBERNETES, AWS, GCP, GIT) |
| `cloud_engineer` | Cloud (AWS, AZURE, GCP) → Containers (DOCKER, KUBERNETES, HELM) → IaC (TERRAFORM, ANSIBLE) → CI/CD (JENKINS, GITHUB, GITLAB) → OS & scripting (LINUX, PYTHON, GO) → Database (POSTGRESQL, MYSQL, MONGODB, REDIS, SQL) → Version control (GIT) |

Worked example (Wednesday Addams):

```
Git, NodeJS, JS, Postgres, React.js
  --transduce-->  GIT, NODE_JS, JAVASCRIPT, POSTGRESQL, REACT
  --sort(full_stack)-->        JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT
  --sort(machine_learning)-->  POSTGRESQL, GIT
```

## 3. Finite Automata (Stage 3 — Qualification Pattern Recognition)

Each profile pattern is a **sequence of groups**; a candidate satisfies a group by having any of its
symbols. All four automata are built by the same generic function (`automata.py`) from the profile
definitions in `src/resumelens/recognition/profiles/`, so the four profiles are processed by the same
software solution:

- One state per step: from q(i) the automaton moves to q(i+1) by reading any symbol of group i+1.
- **Loop** on q(i+1) with the symbols of the same group, so a candidate can list several of them
  (e.g. PANDAS and NUMPY).
- **Optional group**: an extra ε-transition q(i) → q(i+1) allows skipping it.
- **Extras**: loops on the final state, for skills accepted after the last required group.
- A profile without optional groups is a **DFA**; a profile with optional groups is an **ε-NFA**.

Each automaton receives its own list from `by_profile` (Stage 2) and returns ACCEPTED or REJECTED;
the résumé is classified into every profile whose automaton accepts it. The 5-tuple, type and
justification of each automaton are produced by `formal_definition(profile)` and its diagram by
`draw_automaton(profile)`. The Graphviz (`.dot`) file of every automaton is in [`diagrams/`](diagrams/) (`automaton_<profile>.dot`).

### Profile 1 — Full Stack Developer

**Pattern.** A Full Stack Developer must show, in this order, a client-side language (JavaScript or TypeScript), a frontend framework (React, Angular or Vue), a backend technology (Node.js, Django, Spring Boot, Express, FastAPI or Flask), a SQL/NoSQL database and version control (Git/GitHub). Docker, Kubernetes, REST APIs and GraphQL are accepted as extra tools after version control but are not required: the assignment's own Full Stack example (Wednesday Addams) does not mention REST APIs and must be accepted.

```
q0 --[Language]--> q1   {JAVASCRIPT, TYPESCRIPT}
q1 --[Frontend]--> q2   {REACT, ANGULAR, VUE}
q2 --[Backend]--> q3   {NODE_JS, DJANGO, SPRING_BOOT, EXPRESS, FASTAPI, FLASK}
q3 --[Database]--> q4   {POSTGRESQL, MYSQL, MONGODB, SQL, NOSQL}
q4 --[Version control]--> q5   {GIT, GITHUB}
q5 loop (extras)          {DOCKER, KUBERNETES, REST_API, GRAPHQL}
```

- **Q** = {q0, q1, q2, q3, q4, q5}
- **Σ** = {JAVASCRIPT, TYPESCRIPT, REACT, ANGULAR, VUE, NODE_JS, DJANGO, SPRING_BOOT, EXPRESS, FASTAPI, FLASK, POSTGRESQL, MYSQL, MONGODB, SQL, NOSQL, GIT, GITHUB, DOCKER, KUBERNETES, REST_API, GRAPHQL}
- **δ** (for every symbol a of each group):

  | Group | Advance | Loop | ε |
  |---|---|---|---|
  | Language {JAVASCRIPT, TYPESCRIPT} | δ(q0, a) = q1 | δ(q1, a) = q1 | — |
  | Frontend {REACT, ANGULAR, VUE} | δ(q1, a) = q2 | δ(q2, a) = q2 | — |
  | Backend {NODE_JS, DJANGO, SPRING_BOOT, EXPRESS, FASTAPI, FLASK} | δ(q2, a) = q3 | δ(q3, a) = q3 | — |
  | Database {POSTGRESQL, MYSQL, MONGODB, SQL, NOSQL} | δ(q3, a) = q4 | δ(q4, a) = q4 | — |
  | Version control {GIT, GITHUB} | δ(q4, a) = q5 | δ(q5, a) = q5 | — |
  | Extras {DOCKER, KUBERNETES, REST_API, GRAPHQL} | — | δ(q5, a) = q5 | — |

  Total: 40 transitions.
- **q0** = q0
- **F** = {q5}
- **Type: DFA.** There are no ε-transitions and from each state there is at most one transition per symbol, because the groups do not share symbols. Missing transitions go to an implicit dead state (partial DFA).

### Profile 2 — Machine Learning Engineer

**Pattern.** A Machine Learning Engineer must show Python, a data-processing library (Pandas or NumPy), a machine-learning library (Scikit-learn, TensorFlow, PyTorch or Keras), a database (SQL, PostgreSQL or MongoDB) and Git. This is the pattern of the assignment's example automaton, extended with loops so that a candidate may list several libraries of the same group (e.g. Pandas and NumPy, as in the Mary Jane Watson example). Docker and AWS are optional extras after Git.

```
q0 --[Language]--> q1   {PYTHON}
q1 --[Data processing]--> q2   {PANDAS, NUMPY}
q2 --[ML libraries]--> q3   {SCIKIT_LEARN, TENSORFLOW, PYTORCH, KERAS}
q3 --[Database]--> q4   {SQL, POSTGRESQL, MONGODB}
q4 --[Version control]--> q5   {GIT}
q5 loop (extras)          {DOCKER, AWS}
```

- **Q** = {q0, q1, q2, q3, q4, q5}
- **Σ** = {PYTHON, PANDAS, NUMPY, SCIKIT_LEARN, TENSORFLOW, PYTORCH, KERAS, SQL, POSTGRESQL, MONGODB, GIT, DOCKER, AWS}
- **δ** (for every symbol a of each group):

  | Group | Advance | Loop | ε |
  |---|---|---|---|
  | Language {PYTHON} | δ(q0, a) = q1 | δ(q1, a) = q1 | — |
  | Data processing {PANDAS, NUMPY} | δ(q1, a) = q2 | δ(q2, a) = q2 | — |
  | ML libraries {SCIKIT_LEARN, TENSORFLOW, PYTORCH, KERAS} | δ(q2, a) = q3 | δ(q3, a) = q3 | — |
  | Database {SQL, POSTGRESQL, MONGODB} | δ(q3, a) = q4 | δ(q4, a) = q4 | — |
  | Version control {GIT} | δ(q4, a) = q5 | δ(q5, a) = q5 | — |
  | Extras {DOCKER, AWS} | — | δ(q5, a) = q5 | — |

  Total: 24 transitions.
- **q0** = q0
- **F** = {q5}
- **Type: DFA.** There are no ε-transitions and from each state there is at most one transition per symbol, because the groups do not share symbols. Missing transitions go to an implicit dead state (partial DFA).

### Profile 3 — AI Engineer (team-defined, AI/data)

**Pattern.** An AI Engineer shares the ML foundation (Python, data processing, ML/DL libraries) but is distinguished by big-data or generative-AI tooling (Spark or Hugging Face) and by deployment skills (Docker, Kubernetes, AWS or GCP), followed by Git. The database group is optional, because it is not what characterizes this role.

```
q0 --[Language]--> q1   {PYTHON}
q1 --[Data processing]--> q2   {PANDAS, NUMPY}
q2 --[ML / Deep learning]--> q3   {SCIKIT_LEARN, TENSORFLOW, PYTORCH, KERAS}
q3 --[Big data & GenAI]--> q4   {SPARK, HUGGING_FACE}
q4 --[Database (optional)]--> q5   {SQL, POSTGRESQL, MONGODB, REDIS}
q5 --[Deployment]--> q6   {DOCKER, KUBERNETES, AWS, GCP}
q6 --[Version control]--> q7   {GIT}
```

- **Q** = {q0, q1, q2, q3, q4, q5, q6, q7}
- **Σ** = {PYTHON, PANDAS, NUMPY, SCIKIT_LEARN, TENSORFLOW, PYTORCH, KERAS, SPARK, HUGGING_FACE, SQL, POSTGRESQL, MONGODB, REDIS, DOCKER, KUBERNETES, AWS, GCP, GIT}
- **δ** (for every symbol a of each group):

  | Group | Advance | Loop | ε |
  |---|---|---|---|
  | Language {PYTHON} | δ(q0, a) = q1 | δ(q1, a) = q1 | — |
  | Data processing {PANDAS, NUMPY} | δ(q1, a) = q2 | δ(q2, a) = q2 | — |
  | ML / Deep learning {SCIKIT_LEARN, TENSORFLOW, PYTORCH, KERAS} | δ(q2, a) = q3 | δ(q3, a) = q3 | — |
  | Big data & GenAI {SPARK, HUGGING_FACE} | δ(q3, a) = q4 | δ(q4, a) = q4 | — |
  | Database {SQL, POSTGRESQL, MONGODB, REDIS} | δ(q4, a) = q5 | δ(q5, a) = q5 | δ(q4, ε) = q5 |
  | Deployment {DOCKER, KUBERNETES, AWS, GCP} | δ(q5, a) = q6 | δ(q6, a) = q6 | — |
  | Version control {GIT} | δ(q6, a) = q7 | δ(q7, a) = q7 | — |

  Total: 37 transitions.
- **q0** = q0
- **F** = {q7}
- **Type: ε-NFA.** It has ε-transitions that allow skipping the optional groups (Database), so it is an ε-NFA.

### Profile 4 — Cloud Engineer (team-defined, software engineering)

**Pattern.** A Cloud Engineer must show a cloud platform (AWS, Azure or GCP), containers/orchestration (Docker, Kubernetes or Helm), infrastructure as code (Terraform or Ansible), an operating system or scripting skill (Linux, Python or Go) and Git. CI/CD (Jenkins, GitHub, GitLab) and databases are optional complementary groups.

```
q0 --[Cloud platform]--> q1   {AWS, AZURE, GCP}
q1 --[Containers]--> q2   {DOCKER, KUBERNETES, HELM}
q2 --[Infrastructure as code]--> q3   {TERRAFORM, ANSIBLE}
q3 --[CI/CD (optional)]--> q4   {JENKINS, GITHUB, GITLAB}
q4 --[OS & scripting]--> q5   {LINUX, PYTHON, GO}
q5 --[Database (optional)]--> q6   {POSTGRESQL, MYSQL, MONGODB, REDIS, SQL}
q6 --[Version control]--> q7   {GIT}
```

- **Q** = {q0, q1, q2, q3, q4, q5, q6, q7}
- **Σ** = {AWS, AZURE, GCP, DOCKER, KUBERNETES, HELM, TERRAFORM, ANSIBLE, JENKINS, GITHUB, GITLAB, LINUX, PYTHON, GO, POSTGRESQL, MYSQL, MONGODB, REDIS, SQL, GIT}
- **δ** (for every symbol a of each group):

  | Group | Advance | Loop | ε |
  |---|---|---|---|
  | Cloud platform {AWS, AZURE, GCP} | δ(q0, a) = q1 | δ(q1, a) = q1 | — |
  | Containers {DOCKER, KUBERNETES, HELM} | δ(q1, a) = q2 | δ(q2, a) = q2 | — |
  | Infrastructure as code {TERRAFORM, ANSIBLE} | δ(q2, a) = q3 | δ(q3, a) = q3 | — |
  | CI/CD {JENKINS, GITHUB, GITLAB} | δ(q3, a) = q4 | δ(q4, a) = q4 | δ(q3, ε) = q4 |
  | OS & scripting {LINUX, PYTHON, GO} | δ(q4, a) = q5 | δ(q5, a) = q5 | — |
  | Database {POSTGRESQL, MYSQL, MONGODB, REDIS, SQL} | δ(q5, a) = q6 | δ(q6, a) = q6 | δ(q5, ε) = q6 |
  | Version control {GIT} | δ(q6, a) = q7 | δ(q7, a) = q7 | — |

  Total: 42 transitions.
- **q0** = q0
- **F** = {q7}
- **Type: ε-NFA.** It has ε-transitions that allow skipping the optional groups (CI/CD, Database), so it is an ε-NFA.

### Summary of design decisions

| Decision | Reason |
|---|---|
| Loops on every group state | A candidate may have several skills of the same group (Mary Jane lists Pandas and NumPy). |
| Extras as loops on the final state (Full Stack, ML) | Optional skills at the end do not need ε, so these automata stay deterministic (DFA). |
| ε-transitions for optional groups in the middle (AI, Cloud) | The automaton must be able to skip a step and continue with the following ones. |
| REST_API as an extra in Full Stack | The assignment's Full Stack example (Wednesday Addams) has no REST API and must be accepted. |

## 4. Context-Free Grammar / DSL (Stage 4 — Candidate Profile Language)

Define the grammar in EBNF, identifying terminals and non-terminals, and explain the structural characteristics of the language.

```
(* EBNF grammar goes here *)
```
