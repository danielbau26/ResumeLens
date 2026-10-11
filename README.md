# ResumeLens: Formal Language-Based Resume Screening

**Course:** Computación y Estructuras Discretas III — 2026-2 Integrative Task 1

**Team:** *DiscreteFarmers*

**Members:** *Daniel Bautista, Jeanfer Rivera, Samuel Rengifo*

**Professor:** *Juan Marcos*

**Live app:** <https://discretefarmers-resumelens.streamlit.app/> (deploys the `main` branch)

## Problem Statement

Recruitment processes often require reviewing large numbers of résumés to determine whether
candidates satisfy the qualifications expected for a particular professional profile. Résumés usually
contain similar types of information — education, professional experience, technical skills, contact
information, and projects — but the way this information is written and organized varies considerably
(e.g., `JavaScript`, `Javascript`, and `JS` refer to the same language; `Scikit-learn`, `sklearn`, and
`scikit learn` refer to the same library).

**ResumeLens** processes textual résumés and determines whether the qualifications identified in a
candidate's résumé satisfy the patterns defined for a professional profile. The purpose of ResumeLens
is **not** to rank candidates or make hiring decisions — it only evaluates whether explicitly
identified qualifications satisfy formally defined qualification patterns.

## Supported Professional Profiles

1. **Full Stack Developer** *(predefined)* — `full_stack`
2. **Machine Learning Engineer** *(predefined)* — `machine_learning`
3. **AI Engineer** *(team-defined, AI/data)* — `ai_engineer`
4. **Cloud Engineer** *(team-defined, software engineering)* — `cloud_engineer`

All four profiles are processed through the **same general software solution** rather than independent
implementations: each profile is a declarative pattern in `src/resumelens/recognition/profiles/`, and
one generic function builds the four automata from those patterns.

## Pipeline / Formal Models

| Stage | Goal | Formal model | Implementation |
|---|---|---|---|
| 1. Extraction | Extract relevant textual information from résumés | Regular expressions | Python `re` |
| 2. Normalization | Transform equivalent textual representations into a canonical form, then sort by the profile-defined canonical order | Finite-state transducers | `pyformlang` |
| 3. Recognition | Classify the résumé against each profile's accepted qualification pattern | Finite automata (DFA / ε-NFA) | `pyformlang` |
| 4. Candidate Profile Language | Structurally represent and validate the résumé's information; generate a visualization | Context-free grammar (DSL) | `textX` |

Each stage's output is the next stage's input:

```
résumé text
  → Stage 1  extract_info(text) / get_skills(data)   → ["JS", "React.js", "NodeJS", "Postgres", "Git"]
  → Stage 2  normalize(skills)                        → {"canonical", "translations", "unrecognized", "by_profile"}
  → Stage 3  recognize(result["by_profile"])          → {profile: {"profile", "sequence", "result"}}
  → Stage 4  generate_candidate → validate (textX)    → validated candidate → Markdown summary
```

## Project Structure

```
ResumeLens/
├── README.md
├── requirements.txt                 # streamlit, pyformlang, graphviz, textX
├── pyproject.toml                   # package config + pytest config
├── docs/
│   ├── literature_review.md         # theoretical background per stage
│   ├── design/
│   │   ├── modules.md               # module design: functions, inputs/outputs
│   │   ├── formalization.md         # regex, FST 7-tuples, FSA 5-tuples, EBNF grammar
│   │   ├── test_cases.md            # test cases and scenarios per stage
│   │   └── diagrams/                # Graphviz .dot diagrams (transducers + automata)
│   └── poster/                      # research poster
├── src/resumelens/
│   ├── extraction/                  # Stage 1: regex extraction (patterns.py, extractor.py)
│   ├── normalization/               # Stage 2: FSTs (transformations.py, transducers.py, ordering.py, normalizer.py)
│   ├── recognition/                 # Stage 3: finite automata (automata.py, recognizer.py)
│   │   └── profiles/                # one pattern per profile
│   ├── grammar/                     # Stage 4: candidate.tx (textX), generator.py, validator.py
│   ├── visualization/               # Markdown candidate renderer
│   ├── ui/interface.py              # Streamlit user interface
│   └── app.py                       # Streamlit entry point
├── tests/                           # pytest suites: extraction, normalization, recognition, grammar
├── data/sample_resumes/             # wednesday_addams.txt, mary_jane_watson.txt
└── examples/output/                 # example extraction / normalization JSON
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -e .                     # installs the package + its dependencies
```

## Running the application (Streamlit UI)

The normal way to use ResumeLens is the web interface, which runs all four stages on a pasted or
uploaded résumé and shows the ACCEPTED/REJECTED result per profile plus a downloadable summary.

```bash
streamlit run src/resumelens/app.py
```

It is also deployed publicly at <https://discretefarmers-resumelens.streamlit.app/>.

## Running each stage from the terminal (optional)

Each stage can also be run on its own for inspection (run from the project root):

```bash
# Stage 1 — extracted information (JSON) + the skills passed to Stage 2
python -m resumelens.extraction data/sample_resumes/wednesday_addams.txt

# Stage 2 — normalization: canonical forms, translations and the per-profile sorted order
python -m resumelens.normalization data/sample_resumes/wednesday_addams.txt

# Stage 3 — recognition: ACCEPTED/REJECTED for each of the four profiles
python -m resumelens.recognition data/sample_resumes/wednesday_addams.txt

# Stage 4 — full pipeline: generates and validates the candidate DSL, writes candidate.md
python -m resumelens.grammar data/sample_resumes/wednesday_addams.txt
```

Worked example (the assignment's own Full Stack case): the Wednesday Addams résumé produces
`JS, React.js, NodeJS, Postgres, Git` (Stage 1) → `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT`
(Stage 2) → `full_stack` ACCEPTED (Stage 3) → validated candidate profile + Markdown (Stage 4).

## Tests

```bash
pip install -e ".[dev]"
pytest
```

All suites pass (`tests/test_extraction.py`, `test_normalization.py`, `test_recognition.py`,
`test_grammar.py`). The scenarios behind them are documented in
[`docs/design/test_cases.md`](docs/design/test_cases.md).

## Design documentation

- [`docs/design/modules.md`](docs/design/modules.md) — module design (functions, inputs/outputs).
- [`docs/design/formalization.md`](docs/design/formalization.md) — regular expressions, FST 7-tuples,
  FSA 5-tuples and the EBNF grammar.
- [`docs/design/test_cases.md`](docs/design/test_cases.md) — test cases and scenarios per stage.
- [`docs/literature_review.md`](docs/literature_review.md) — theoretical background guiding the design.
- `docs/design/diagrams/` — Graphviz `.dot` diagrams for every transducer and automaton.

## Deliverables

1. Research poster (`docs/poster/`) — in English.
2. Design documents (`docs/design/`): module design, formalization, test cases.
3. Python implementation (`src/`): the four formal models, the Streamlit UI, and the tests.
4. 10-minute technical presentation (in English), based on the poster.

## AI Collaboration Disclosure (Nivel 3)

This project used AI assistance (Nivel de uso de IAG 3 — *Colaboración con IAG*). A record of how AI
was used across the project, including the kinds of prompts and the author-provided content, is kept
in [`docs/ai_log.md`](docs/ai_log.md).
