# AI Collaboration Log

**Level of AI use:** Nivel 3 — *Colaboración con IAG* (as declared in the course rubric).

At this level the team is allowed to use generative AI to help complete tasks and deliverables, taking
advantage of these tools to improve the products, **while keeping a record of the interactions and
being able to modify and justify the generated results, demonstrating conceptual understanding.** This
document is that record.

## Tool used

- **Claude (Anthropic), via the Claude Code agent** — used as a pair-programming, documentation and
  code-review assistant throughout the project.

- **ChatGPT (OpenAI)** — used for explanations of formal language concepts, reviewed for Stage 4, tests, Streamlit setup, deployment guidance, documentation review.

## How AI was used (by category)

| Area | AI assistance | Author (team) responsibility |
|---|---|---|
| Project scaffolding | Proposed the initial folder structure, `pyproject.toml`, `.gitignore` and the first README/design-doc skeletons. | Reviewed, accepted and adjusted the structure. |
| Stage 1 — Extraction | Produced an initial regex-based extractor; **later the team wrote and pasted their own version**, which the AI integrated verbatim (only translating header comments on request). | The team authored the final `patterns.py` / `extractor.py`. |
| Stage 2 — Normalization | Produced an initial transducer implementation and a simplification; **the team then pasted their own `VARIANTS`/`translate`/`formal_definition` version**, which the AI integrated verbatim. | The team authored the final Stage 2 code. |
| Stage 3 — Recognition | Implemented by the team. The AI **reviewed** it and verified it against the assignment examples. | The team authored the automata, profiles and recognizer. |
| Stage 4 — Grammar / DSL | Implemented by the team (`candidate.tx`, generator, validator, visualization, Streamlit UI). The AI **reviewed** it, ran it end to end and fixed defects (see below). | The team authored the grammar, DSL and UI. |
| Tests | Wrote/updated some test suites and fixed two testing defects. | The team authored most test scenarios. |
| Documentation | Drafted and kept up to date `formalization.md`, `modules.md`, `test_cases.md`, the `README`, the literature review, the poster and this log. | Reviewed content; must verify the academic citations. |
| Git / workflow | Helped create commits, pull requests and merges, and audited the branch state before merging to `dev`/`main`. | Owned the repository and the final decisions. |

## Main AI-assisted activities (chronological summary)

1. **Initial setup** — generated the repository skeleton (packages per stage, test folder, docs
   structure) and the first README from the assignment statement.
2. **Stage 1 (extraction)** — first a dataclass-based implementation; then migrated to the team's
   simpler plain-dict version (functions `extract_info`, `get_skills`, …) when they provided it,
   updating all downstream consumers and tests to keep the suite green.
3. **Stage 2 (normalization)** — first a transducer implementation with pyformlang; then simplified to
   a plain-dict API; then replaced with the team's own version (`VARIANTS`, `translate`,
   `formal_definition`, `draw_transducer`) integrated literally.
4. **Stage 3 (recognition) — review** — read the team's automata code, confirmed the four 5-tuples,
   the DFA/ε-NFA classification and the assignment's exact example
   (`PYTHON, PANDAS, TENSORFLOW, POSTGRESQL, GIT` → `machine_learning` ACCEPTED).
5. **Stage 4 (grammar/DSL) — review and fixes** — ran the full pipeline end to end and fixed:
   - a test file that `pytest` was silently skipping (`tests/grammar.py` → `tests/test_grammar.py`),
   - a test calling a non-existent helper (`extract_from_file_text` → `extract_info`),
   - a Windows-only editor launch that crashed the Stage 4 CLI on macOS/Linux
     (`subprocess.run(["code.cmd", …])`).
6. **Documentation** — completed the literature review, kept the design docs and README synchronized
   with the real code, and drafted the research poster.
7. **Repository hygiene** — audited the branch state, discovered that trailing fixes were missing from
   `dev`, and merged them before promoting `dev` → `main`.

## Verification and understanding

- All AI-assisted or AI-reviewed code is exercised by the automated test suite (`pytest`), and the
  assignment's own worked examples were reproduced exactly (Stages 1–3) and run end to end (Stage 4).
- Where the team supplied their own implementations, the AI integrated them without changing the logic;
  the team remains the author of that code and is responsible for explaining it.
- The team is responsible for independently verifying the academic references listed in
  `docs/literature_review.md` before submission.
