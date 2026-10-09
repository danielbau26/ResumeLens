# Test Cases

Document the test cases and scenarios used to validate each stage of the pipeline.

## Stage 1 — Extraction

Automated in `tests/test_extraction.py` (run with `pytest`). All 14 cases pass.

| # | Scenario | Input | Expected Output |
|---|---|---|---|
| 1 | Assignment example (Wednesday Addams) | `JS, React.js, NodeJS, Postgres, Git` skills block | `get_skills(data)` == `[JS, React.js, NodeJS, Postgres, Git]` |
| 2 | Name is first non-empty line | Wednesday résumé | `data["name"]` == `Wednesday Addams` |
| 3 | Programming-language variants | `JavaScript, JS, TypeScript, Python` | all recognized under `programming_languages` |
| 4 | Dotted tokens not split | `React.js and Node.js and Scikit-learn` | `React.js`, `Node.js`, `Scikit-learn` captured whole |
| 5 | Dotted token not a URL | `React.js` | `data["urls"]` == `[]` |
| 6 | Contact information | `john.doe@example.com \| +1 212 555 0142 \| github.com/jdoe` | `emails`, `phones` and `urls` extracted |
| 7 | URL host not reclaimed as tool | `github.com/jdoe. … Git.` | `urls`=`[github.com/jdoe]`, `tools_technologies`=`[Git]` (no stray `github`) |
| 8 | Experience + academic degree | `5 years of experience … MSc in Computer Science.` | experience phrase + degree with field |
| 9 | Other qualifications | `… machine learning and data processing …` | detected under `other_qualifications` |
| 10 | Case-insensitive dedup, order kept | `Git, git, GIT, Docker, git` | `tools_technologies` == `[Git, Docker]` |
| 11 | Database variants | `Postgres, PostgreSQL, MongoDB, NoSQL, SQL` | all under `databases` |
| 12 | Empty input | `""` | `name` == `""` and `get_skills(data)` == `[]` |
| 13 | File read + JSON save round-trip | résumé file | JSON reload matches expected lists |
| 14 | Sample résumés shipped | — | both sample files exist |

## Stage 2 — Normalization

Automated in `tests/test_normalization.py` (run with `pytest`). All cases pass (full suite: 54).

| # | Scenario | Input | Expected Output |
|---|---|---|---|
| 1 | Variant → canonical (parametrized) | `JS`, `Javascript`, `React.js`, `ReactJS`, `NodeJS`, `Postgres`, `sklearn`, `scikit learn`, `Tensor Flow`, `Py Torch`, `K8s`, … | each maps to its canonical form (`JAVASCRIPT`, `REACT`, `NODE_JS`, `POSTGRESQL`, `SCIKIT_LEARN`, `TENSORFLOW`, `PYTORCH`, `KUBERNETES`, …) |
| 2 | Every declared variant transduces | all `TRANSFORMATIONS` variants | each → its `canonical` |
| 3 | Unknown token | `COBOL` | `normalize_token` returns `None` |
| 4 | Case-insensitive | `javascript`, `POSTGRES` | `JAVASCRIPT`, `POSTGRESQL` |
| 5 | Canonical statement example | `Git, NodeJS, JS, Postgres, React.js` + `full_stack` | `[JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT]` |
| 6 | Order independence | any permutation of #5 input | same sorted output |
| 7 | Dedup of equivalent variants | `JS, JavaScript, Javascript` | `[JAVASCRIPT]` |
| 8 | Unrecognized kept, not dropped | `JS, COBOL, Git` | canonical `[JAVASCRIPT, GIT]`, unrecognized `[COBOL]` |
| 9 | Unordered canonical appended last | `JS, Ruby, Git` + `full_stack` | `[JAVASCRIPT, GIT, RUBY]` |
| 10 | Unknown profile rejected | `sort_qualifications(..., "unknown")` | raises `KeyError` |
| 11 | ML sample end-to-end | Mary Jane Watson résumé + `machine_learning` | `[PYTHON, PANDAS, NUMPY, SCIKIT_LEARN, TENSORFLOW, SQL, GIT]` |
| 12 | Combined transducer | chars of `js` | `[[JAVASCRIPT]]` |
| 13 | FST 7-tuple sanity | `M_SCIKIT_LEARN` | start `{q0}`, final `{qf}`, Γ `{SCIKIT_LEARN}`, \|Q\| > 2 |
| 14 | JSON save round-trip | `normalize([JS, Git], full_stack)` | reloaded `canonical`/`profile`/`mapping` match |
| 15 | All four profiles available | `available_profiles()` | `[full_stack, machine_learning, ai_engineer, cloud_engineer]` |
| 16 | AI Engineer ordering | AI résumé tokens + `ai_engineer` | `[PYTHON, PANDAS, PYTORCH, SPARK, HUGGING_FACE, POSTGRESQL, DOCKER, AWS, GIT]` |
| 17 | Cloud Engineer ordering | Cloud résumé tokens + `cloud_engineer` | `[AWS, AZURE, DOCKER, KUBERNETES, HELM, TERRAFORM, JENKINS, LINUX, GIT]` |

## Stage 3 — Recognition

| # | Scenario | Input | Expected Output |
|---|---|---|---|

## Stage 4 — Grammar / DSL

| # | Scenario | Input | Expected Output |
|---|---|---|---|

## End-to-End Scenarios

| # | Scenario | Résumé | Profile | Expected Result |
|---|---|---|---|---|
