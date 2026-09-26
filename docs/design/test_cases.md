# Test Cases

Document the test cases and scenarios used to validate each stage of the pipeline.

## Stage 1 — Extraction

Automated in `tests/test_extraction.py` (run with `pytest`). All 12 cases pass.

| # | Scenario | Input | Expected Output |
|---|---|---|---|
| 1 | Assignment example (Wednesday Addams) | `JS, React.js, NodeJS, Postgres, Git` skills block | `qualifications()` == `[JS, React.js, NodeJS, Postgres, Git]` |
| 2 | Programming-language variants | `JavaScript, Javascript, JS, TypeScript, Python` | all recognized under `programming_languages` |
| 3 | Dotted tokens not split | `React.js and Node.js and Scikit-learn` | `React.js`, `Node.js`, `Scikit-learn` captured whole |
| 4 | Dotted token not a URL | `React.js` | `url` == `[]` |
| 5 | Contact information | `john.doe@example.com \| +1 212 555 0142 \| github.com/jdoe` | email, phone and url extracted |
| 6 | URL host not reclaimed as tool | `github.com/jdoe. … Git.` | `url`=`[github.com/jdoe]`, `tools`=`[Git]` (no stray `github`) |
| 7 | Experience + academic degree | `5 years of experience … MSc in Computer Science.` | experience phrase + degree with field |
| 8 | Case-insensitive dedup, order kept | `Git, git, GIT, Docker, git` | `tools` == `[Git, Docker]` |
| 9 | Database variants | `Postgres, PostgreSQL, MongoDB, NoSQL, SQL` | all under `databases` |
| 10 | Empty input | `""` | `matches` == `{}` |
| 11 | File read + JSON save round-trip | résumé file | JSON reload matches expected lists |
| 12 | Sample résumés shipped | — | both sample files exist |

## Stage 2 — Normalization

| # | Scenario | Input | Expected Output |
|---|---|---|---|

## Stage 3 — Recognition

| # | Scenario | Input | Expected Output |
|---|---|---|---|

## Stage 4 — Grammar / DSL

| # | Scenario | Input | Expected Output |
|---|---|---|---|

## End-to-End Scenarios

| # | Scenario | Résumé | Profile | Expected Result |
|---|---|---|---|---|
