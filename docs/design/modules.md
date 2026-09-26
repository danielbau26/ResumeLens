# Module Design

Document the design of each module in the pipeline: functions, inputs, and outputs.

## Stage 1 — Extraction (`src/resumelens/extraction/`)

**Files:** `patterns.py` (regex catalogue), `extractor.py` (driver), `__main__.py` (CLI).

Data structures:
- `PatternSpec(name, description, regex)` — a named regex with its documented language.
- `ExtractionResult(matches: dict[str, list[str]])` — category → ordered, de-duplicated matches.

| Function | Input | Output | Description |
|---|---|---|---|
| `extract(text, patterns=None)` | résumé text `str` | `ExtractionResult` | Applies the catalogue in order; each match claims its span so later patterns can't overlap it; de-duplicates per category (case-insensitive, order preserving). |
| `extract_file(path, patterns=None)` | path to a `.txt` résumé | `ExtractionResult` | Reads UTF-8 text and calls `extract`. |
| `save_result(result, path)` | `ExtractionResult`, output path | written `Path` | Persists the result as pretty JSON ("keep the extracted information in a file"). |
| `ExtractionResult.qualifications()` | — | `list[str]` | Flattens the technical-qualification categories (programming languages, frameworks/libraries, databases, tools) into the input for Stage 2. |
| `ExtractionResult.get(category)` | category name | `list[str]` | Matches for one category (empty if none). |

**CLI:** `python -m resumelens.extraction --input <file> [--output <json>]`.

## Stage 2 — Normalization (`src/resumelens/normalization/`)

**Files:** `transformations.py` (rule catalogue), `transducers.py` (pyformlang FSTs), `ordering.py`
(profile order + sort), `normalizer.py` (orchestrator), `__main__.py` (CLI).

Data structures:
- `TransductionRule(canonical, variants, category)` — a canonical form and the surface variants it accepts.
- `NormalizationResult(canonical, mapping, unrecognized, profile)` — canonical output plus a
  surface→canonical trace and the tokens no transducer recognized.

| Function | Input | Output | Description |
|---|---|---|---|
| `build_transducer(rule)` | `TransductionRule` | `FST` | Character-level pyformlang FST accepting the (case-folded) variants and emitting the canonical form. |
| `build_all()` | — | `dict[str, FST]` | One FST per canonical form, keyed by canonical symbol. |
| `combined_transducer()` | — | `FST` | Union of all per-rule FSTs (the single-transducer view). |
| `normalize_token(token)` | `str` | `str \| None` | Canonical form of a surface token, or `None` if unrecognized. |
| `export_diagrams(dest, canonicals=None)` | dir, optional subset | written `Path`s | Graphviz `.dot` per transducer (`.png` too if `dot` is installed). |
| `sort_qualifications(canonical, profile)` | canonical list, profile id | `list[str]` | Reorders into the profile's canonical order; unordered symbols appended last. |
| `normalize(tokens, profile=None)` | surface tokens | `NormalizationResult` | Transduce → dedup → (sort). Keeps a mapping trace and unrecognized bucket. |
| `normalize_extraction(result, profile=None)` | `ExtractionResult` | `NormalizationResult` | Convenience over `result.qualifications()`. |
| `save_result(result, path)` | result, path | written `Path` | Persists the result as JSON. |

**CLI:** `python -m resumelens.normalization --input <resume.txt\|extraction.json> [--profile full_stack\|machine_learning] [--output <json>]`.

## Stage 3 — Recognition (`src/resumelens/recognition/`)

| Function | Input | Output | Description |
|---|---|---|---|

## Stage 4 — Grammar / DSL (`src/resumelens/grammar/`)

| Function | Input | Output | Description |
|---|---|---|---|

## Visualization (`src/resumelens/visualization/`)

| Function | Input | Output | Description |
|---|---|---|---|
