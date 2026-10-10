# Module Design

Design of each module of the pipeline: functions, inputs and outputs. Each stage is a Python package
inside `src/resumelens/`, and the output of one stage is the input of the next one:

```
résumé text
  -> Stage 1 extract_info(text)               -> data (dict)
  -> get_skills(data)                         -> ["JS", "React.js", ...]
  -> Stage 2 normalize(skills)                -> {"canonical", "translations", "unrecognized", "by_profile"}
  -> Stage 3 recognize(result["by_profile"])  -> {profile: {"profile", "sequence", "result"}}
  -> Stage 4 (textX)                          -> validated candidate profile -> HTML / Markdown
```

## Stage 1 — Extraction (`src/resumelens/extraction/`)

**Files:** `patterns.py` (regular expressions), `extractor.py` (functions), `__main__.py` (optional
terminal test).

Data structure: a plain dictionary `category -> list of matches`, plus the candidate name:

```python
{"name": "Wednesday Addams", "emails": [], "phones": [], "urls": [],
 "programming_languages": ["JS"], "frameworks_libraries": ["React.js", "NodeJS"],
 "databases": ["Postgres"], "tools_technologies": ["Git"],
 "academic_qualifications": [], "professional_experience": ["3 years of experience developing web applications"],
 "other_qualifications": ["web applications"]}
```

| Function | Input | Output | Description |
|---|---|---|---|
| `get_name(text)` | résumé text `str` | `str` | First non-empty line of the résumé (candidate name, used in Stage 4). |
| `extract_info(text)` | résumé text `str` | `dict` | Applies every regex of `PATTERNS`. Skills are searched in a copy of the text without e-mails and URLs; academic qualifications without `IGNORECASE`; matches are de-duplicated case-insensitively in order of appearance. |
| `get_skills(data)` | `dict` from `extract_info` | `list[str]` | Joins the four technical categories into one list. **Input of Stage 2.** |
| `extract_from_file(path)` | path to a `.txt` résumé | `dict` | Reads the file (UTF-8) and calls `extract_info`. |
| `save_result(data, path)` | `dict`, output path | — | Saves the extracted information as JSON. |

**Terminal test:** `python -m resumelens.extraction ../data/sample_resumes/wednesday_addams.txt` (from `src`).

## Stage 2 — Normalization (`src/resumelens/normalization/`)

**Files:** `transformations.py` (variants table), `transducers.py` (pyformlang FSTs), `ordering.py`
(profile orders), `normalizer.py` (orchestrator), `__main__.py` (optional terminal test).

Data structures:
- `VARIANTS`: `canonical -> list of lowercase variants`, e.g. `"REACT": ["react", "react.js", "reactjs"]`.
- `PROFILE_ORDER`: `profile -> canonical forms in the profile order`.

| Function | Input | Output | Description |
|---|---|---|---|
| `build_transitions(canonical, variants)` | canonical form, variants | `(transitions, finals)` | Builds the tuples `(from, char, to, [output])`, sharing the path of variants with a common prefix. |
| `build_transducer(canonical)` | canonical form | `FST` | Creates the pyformlang FST: `add_transitions`, start state `q0`, final states. |
| `TRANSDUCERS` | — | `dict[str, FST]` | One transducer per canonical form, built once when the module is imported. |
| `translate(word)` | surface token `str` | `str` or `None` | Lower-cases the token and runs it through the transducers; returns the canonical form of the first one that accepts it. |
| `formal_definition(canonical)` | canonical form | `dict` | 7-tuple (Q, Σ, Γ, δ, ω, q0, F). |
| `draw_transducer(canonical)` | canonical form | `graphviz.Digraph` | Transition diagram (`letter / output`). |
| `save_diagrams(folder)` | folder path | — | Writes one `.dot` file per transducer. |
| `sort_skills(canonical_skills, profile)` | canonical list, profile id | `list[str]` | Keeps only the profile's symbols, in the profile order. Unknown profile raises `KeyError`. |
| `sort_for_all_profiles(canonical_skills)` | canonical list | `dict[str, list[str]]` | `sort_skills` for the four profiles. |
| `normalize(skills)` | list from `get_skills` | `dict` | Translates, de-duplicates and sorts. Returns `canonical`, `translations`, `unrecognized` and `by_profile` (**input of Stage 3**). |
| `save_result(data, path)` | `dict`, output path | — | Saves the normalization result as JSON. |

**Terminal test:** `python -m resumelens.normalization ../data/sample_resumes/wednesday_addams.txt` (from `src`).

## Stage 3 — Recognition (`src/resumelens/recognition/`)

**Files:** `profiles/` (one pattern per profile: `full_stack.py`, `machine_learning.py`,
`ai_engineer.py`, `cloud_engineer.py`, collected in `profiles/__init__.py`), `automata.py`
(pyformlang automata), `recognizer.py` (classification), `__main__.py` (optional terminal test).

Data structure of a profile:

```python
PROFILE = {
    "name": "Machine Learning Engineer",
    "groups": [
        {"name": "Language", "symbols": ["PYTHON"], "optional": False},
        {"name": "Data processing", "symbols": ["PANDAS", "NUMPY"], "optional": False},
        ...
    ],
    "extras": ["DOCKER", "AWS"],
}
```

| Function | Input | Output | Description |
|---|---|---|---|
| `build_transitions(profile_key)` | profile id | `(transitions, final)` | Advance and loop transitions per group, ε for optional groups, loops on the final state for extras. |
| `automaton_type(profile_key)` | profile id | `"DFA"` or `"ε-NFA"` | ε-NFA if the profile has an optional group, DFA otherwise. |
| `build_automaton(profile_key)` | profile id | `DeterministicFiniteAutomaton` or `EpsilonNFA` | Creates the pyformlang automaton of the profile. |
| `AUTOMATA` | — | `dict` | The four automata, built once when the module is imported. |
| `accepts(profile_key, sequence)` | profile id, sorted canonical list | `bool` | Runs the sequence through the profile automaton. |
| `formal_definition(profile_key)` | profile id | `dict` | 5-tuple (Q, Σ, δ, q0, F), type and justification. |
| `draw_automaton(profile_key)` | profile id | `graphviz.Digraph` | Transition diagram (symbols between the same states are merged in one edge). |
| `save_diagrams(folder)` | folder path | — | Writes one `.dot` file per automaton. |
| `recognize(by_profile)` | `by_profile` from Stage 2 | `dict` | For each profile: `profile` (name), `sequence` and `result` (`ACCEPTED`/`REJECTED`). **Input of Stage 4.** |
| `accepted_profiles(results)` | `dict` from `recognize` | `list[str]` | Profiles whose automaton accepted the résumé (classification). |
| `save_result(results, path)` | `dict`, output path | — | Saves the recognition result as JSON. |

**Terminal test:** `python -m resumelens.recognition ../data/sample_resumes/wednesday_addams.txt` (from `src`).

## Stage 4 — Grammar / DSL (`src/resumelens/grammar/`)

| Function | Input | Output | Description |
|---|---|---|---|

## Visualization (`src/resumelens/visualization/`)

| Function | Input | Output | Description |
|---|---|---|---|
