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

| Function | Input | Output | Description |
|---|---|---|---|

## Stage 3 — Recognition (`src/resumelens/recognition/`)

| Function | Input | Output | Description |
|---|---|---|---|

## Stage 4 — Grammar / DSL (`src/resumelens/grammar/`)

| Function | Input | Output | Description |
|---|---|---|---|

## Visualization (`src/resumelens/visualization/`)

| Function | Input | Output | Description |
|---|---|---|---|
