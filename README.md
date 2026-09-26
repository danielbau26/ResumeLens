# ResumeLens: Formal Language-Based Resume Screening

**Course:** Computación y Estructuras Discretas III — 2026-2 Integrative Task 1

**Team:** *DiscreteFarmers*

**Members:** *Daniel Bautista, Jeanfer Rivera Samuel Rengifo*

**Professor:** *Juan Marcos*

**Deadline:** October 11, 2026

## Problem Statement

Recruitment processes often require reviewing large numbers of résumés to determine whether
candidates satisfy the qualifications expected for a particular professional profile. Résumés usually
contain similar types of information, education, professional experience, technical skills, contact
information, and projects. But the way this information is written and organized varies considerably
(e.g., `JavaScript`, `Javascript`, and `JS` refer to the same language; `Scikit-learn`, `sklearn`, and
`scikit learn` refer to the same library).

**ResumeLens** processes textual résumés and determines whether the qualifications identified in a
candidate's résumé satisfy the patterns defined for a professional profile. The purpose of ResumeLens
is **not** to rank candidates or make hiring decisions — it only evaluates whether explicitly identified
qualifications satisfy formally defined qualification patterns.

## Supported Professional Profiles

1. **Full Stack Developer** *(predefined)*
2. **Machine Learning Engineer** *(predefined)*
3. *(AI Engineer — defined by the team)*
4. *(Cloud Engineer — defined by the team)*

All four profiles are processed through the same general pipeline rather than independent
implementations.

## Pipeline / Formal Models

| Stage | Goal | Formal model | Implementation |
|---|---|---|---|
| 1. Extraction | Extract relevant textual information from résumés | Regular expressions | Python `re` |
| 2. Normalization | Transform equivalent textual representations into a canonical form, then sort by profile-defined canonical order | Finite-state transducers | `pyformlang` |
| 3. Recognition | Classify the résumé against a profile's accepted qualification pattern | Finite automata (DFA / NFA / ε-NFA) | `pyformlang` |
| 4. Candidate Profile Language | Structurally represent and validate the résumé's extracted, normalized, and classified information; generate a visualization | Context-free grammar (DSL) | `textX` |

Each stage's output is the next stage's input:
`raw résumé text → extracted strings → normalized & sorted qualifications → profile classification → validated candidate profile → HTML/Markdown visualization`.

## Project Structure

```
ResumeLens/
├── README.md                      # This file
├── requirements.txt                # Python dependencies (pyformlang, textX, ...)
├── docs/                           # All design documents (Markdown)
│   ├── literature_review.md        # Literature review supporting design decisions
│   ├── design/
│   │   ├── modules.md              # Module design: functions, inputs/outputs
│   │   ├── formalization.md        # Formal definitions: regex, FST 7-tuples, FSA 5-tuples, EBNF grammar
│   │   └── test_cases.md           # Test cases and scenarios per stage
│   └── poster/                     # Research poster
├── src/
│   └── resumelens/
│       ├── extraction/             # Stage 1: regex-based information extraction
│       ├── normalization/          # Stage 2: finite-state transducers (pyformlang)
│       ├── recognition/            # Stage 3: finite automata per profile (pyformlang)
│       │   └── profiles/           # One automaton definition per professional profile
│       ├── grammar/                # Stage 4: textX grammar (.tx) + DSL validation
│       ├── visualization/          # HTML/Markdown candidate-profile renderer
│       ├── ui/                     # Command-line / UI entry point
│       └── pipeline.py             # Orchestrates stages 1-4 end to end
├── tests/                          # Unit and end-to-end tests, including test scenarios
│   └── fixtures/sample_resumes/    # Sample résumé inputs used by tests
├── data/sample_resumes/            # Sample résumé text files for manual runs/demos
└── examples/output/                # Example generated HTML/Markdown outputs
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Install the package (editable) so the modules are importable, then run a stage.

```bash
pip install -e .
```

**Stage 1 — Extraction** (implemented):

```bash
# Print the extracted information as JSON
python -m resumelens.extraction --input data/sample_resumes/wednesday_addams.txt

# Or save it to a file
python -m resumelens.extraction --input data/sample_resumes/wednesday_addams.txt \
    --output examples/output/wednesday_addams.json
```

Full end-to-end pipeline entry point (`python -m resumelens.ui …`) will be wired up as the remaining
stages are implemented.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

## Deliverables

1. Research poster (`docs/poster/`) — in English.
2. Design documents (`docs/design/`):
   - Module design (functions, inputs/outputs)
   - Formalization (regex, FST/FSA 7-/5-tuples, EBNF grammar)
   - Test cases and scenarios
3. Python implementation (`src/`): complete and correct model, UI, and tests.
4. 10-minute technical presentation (in English), based on the poster.

## AI Collaboration Disclosure (Nivel 3)

This project used AI assistance for completing tasks
and entregables. A record of AI interactions — including author-provided content and prompts used —
is kept in *(location, e.g. `docs/ai_log.md`)*.
