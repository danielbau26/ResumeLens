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
- `VARIANTS` — a plain `dict[str, list[str]]` mapping each canonical form to its (lowercase) surface
  variants (e.g. `"JAVASCRIPT": ["js", "javascript"]`). One entry = one transducer.
- `PROFILE_ORDER` — a `dict[str, list[str]]` giving the canonical order per profile.
- The normalization result is a plain `dict`:
  `{"canonical", "translations", "unrecognized", "by_profile"}` — `translations` is a
  `{surface: canonical}` map and `by_profile` is `{profile: [sorted canonical skills]}`. This is easy
  to show in Streamlit (`st.json`, `st.dataframe`).

| Function | Input | Output | Description |
|---|---|---|---|
| `build_transducer(canonical)` | canonical `str` | `FST` | Deterministic character-level pyformlang FST that reads a variant and emits the canonical form. Variants that share a prefix share states. |
| `translate(word)` | `str` | `str \| None` | Lower-cases the word and runs it through each transducer; returns the canonical form or `None`. |
| `formal_definition(canonical)` | canonical `str` | `dict` | The complete 7-tuple `{Q, Σ, Γ, δ, ω, q0, F}` of that transducer. |
| `draw_transducer(canonical)` | canonical `str` | `graphviz.Digraph` | The transducer's diagram (graphical representation). |
| `save_diagrams(folder)` | folder path | — | Writes a `.dot` diagram per transducer. |
| `sort_skills(canonical, profile)` | canonical list, profile id | `list[str]` | Keeps only the skills present in the profile order, in that order (others are not sent to that profile). |
| `sort_for_all_profiles(canonical)` | canonical list | `dict` | `{profile: sort_skills(...)}` for every profile. |
| `normalize(skills)` | surface skills `list[str]` | `dict` | Translate → dedup → sort for every profile. Returns `{canonical, translations, unrecognized, by_profile}`. |
| `save_result(result, path)` | result `dict`, path | — | Persists the result dict as JSON. |

**CLI:** `python -m resumelens.normalization <resume.txt>` (prints the Stage 1 skills and the normalized result as JSON).

## Stage 3 — Recognition (`src/resumelens/recognition/`)

| Function | Input | Output | Description |
|---|---|---|---|

## Stage 4 — Grammar / DSL (`src/resumelens/grammar/`)

| Function | Input | Output | Description |
|---|---|---|---|

## Visualization (`src/resumelens/visualization/`)

| Function | Input | Output | Description |
|---|---|---|---|
