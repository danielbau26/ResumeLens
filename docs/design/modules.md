# Module Design

Document the design of each module in the pipeline: functions, inputs, and outputs.

## Stage 1 — Extraction (`src/resumelens/extraction/`)

**Files:** `patterns.py` (regex catalogue), `extractor.py` (driver), `__main__.py` (CLI).

Data structures:
- Regexes are plain string constants (`EMAIL_REGEX`, `LANGUAGES_REGEX`, …) and `PATTERNS` is a
  `dict[str, str]` mapping each category to its regex.
- The extraction result is a plain `dict[str, list[str]]` (category → matches) plus a `"name"` entry.
  Categories: `emails, phones, urls, programming_languages, frameworks_libraries, databases,
  tools_technologies, academic_qualifications, professional_experience, other_qualifications`.

| Function | Input | Output | Description |
|---|---|---|---|
| `extract_info(text)` | résumé text `str` | `dict` | Applies every regex; blanks emails/URLs before searching the other categories (so a host like `github.com` is not re-read as a tool); de-duplicates per category (case-insensitive, order preserving). Adds the `name` (first non-empty line). |
| `get_name(text)` | résumé text `str` | `str` | The first non-empty line (used by Stage 4). |
| `get_skills(data)` | extraction `dict` | `list[str]` | Flattens the 4 technical-qualification categories (languages, frameworks/libraries, databases, tools) — the input for Stage 2. |
| `extract_from_file(path)` | path to a `.txt` résumé | `dict` | Reads UTF-8 text and calls `extract_info`. |
| `save_result(data, path)` | extraction `dict`, output path | — | Persists the dict as pretty JSON ("keep the extracted information in a file"). |

**CLI:** `python -m resumelens.extraction <resume.txt>` (prints the JSON dict and the Stage 2 skills list).

## Stage 2 — Normalization (`src/resumelens/normalization/`)

**Files:** `transformations.py` (rule catalogue), `transducers.py` (pyformlang FSTs), `ordering.py`
(profile order + sort), `normalizer.py` (orchestrator), `__main__.py` (CLI).

Data structures:
- `TRANSFORMATIONS` — a plain `dict[str, list[str]]` mapping each canonical form to the surface
  variants it accepts (e.g. `"JAVASCRIPT": ["JavaScript", "Javascript", "JS"]`).
- The normalization result is a plain `dict`: `{"profile", "canonical", "mapping", "unrecognized"}`
  (`mapping` is a list of `(surface, canonical)` pairs) — easy to show in Streamlit.

| Function | Input | Output | Description |
|---|---|---|---|
| `build_transducer(canonical, variants)` | canonical `str`, variants `list[str]` | `FST` | Character-level pyformlang FST accepting the (case-folded) variants and emitting the canonical form. |
| `build_all()` | — | `dict[str, FST]` | One FST per canonical form, keyed by canonical symbol. |
| `combined_transducer()` | — | `FST` | Union of all per-canonical FSTs (the single-transducer view). |
| `normalize_token(token)` | `str` | `str \| None` | Canonical form of a surface token, or `None` if unrecognized. |
| `export_diagrams(dest, canonicals=None)` | dir, optional subset | written `Path`s | Graphviz `.dot` per transducer (`.png` too if `dot` is installed). |
| `sort_qualifications(canonical, profile)` | canonical list, profile id | `list[str]` | Reorders into the profile's canonical order; unordered symbols appended last. |
| `normalize(skills, profile=None)` | surface skills `list[str]` | `dict` | Transduce → dedup → (sort). Returns `{profile, canonical, mapping, unrecognized}`. |
| `normalize_extraction(data, profile=None)` | extraction `dict` | `dict` | Convenience over `get_skills(data)`. |
| `save_result(result, path)` | result `dict`, path | — | Persists the result dict as JSON. |

**CLI:** `python -m resumelens.normalization --input <resume.txt\|extraction.json> [--profile full_stack\|machine_learning\|ai_engineer\|cloud_engineer] [--output <json>]`.

## Stage 3 — Recognition (`src/resumelens/recognition/`)

| Function | Input | Output | Description |
|---|---|---|---|

## Stage 4 — Grammar / DSL (`src/resumelens/grammar/`)

| Function | Input | Output | Description |
|---|---|---|---|

## Visualization (`src/resumelens/visualization/`)

| Function | Input | Output | Description |
|---|---|---|---|
