# Test Cases

Test cases and scenarios used to validate each stage of the pipeline. All of them are automated with
`pytest` in `tests/`. Run from the project root:

```bash
PYTHONPATH=src python -m pytest -v
```

## Stage 1 — Extraction (`tests/test_extraction.py`)

| # | Scenario | Input | Expected output |
|---|---|---|---|
| 1 | Assignment example (Wednesday Addams) | Wednesday Addams fragment | `get_skills` == `[JS, React.js, NodeJS, Postgres, Git]` |
| 2 | Candidate name | Wednesday Addams fragment | `name` == `Wednesday Addams` |
| 3 | Programming-language variants | `JavaScript, JS, TypeScript, Python` | all four in `programming_languages` |
| 4 | Dotted tokens not split | `React.js and Node.js and Scikit-learn` | `React.js`, `Node.js`, `Scikit-learn` captured whole |
| 5 | Dotted token is not a URL | `React.js` | `urls` == `[]` |
| 6 | Contact information | `john.doe@example.com \| +1 212 555 0142 \| github.com/jdoe` | e-mail, phone and URL extracted |
| 7 | URL host not taken as a tool | `github.com/jdoe. … Git.` | `urls` == `[github.com/jdoe]`, `tools` == `[Git]` |
| 8 | Experience and academic degree | `5 years of experience in backend development. MSc in Computer Science.` | experience phrase + degree with field |
| 9 | Other qualifications | `machine learning and data processing pipelines` | both in `other_qualifications` |
| 10 | Case-insensitive de-duplication, order kept | `Git, git, GIT, Docker, git` | `tools` == `[Git, Docker]` |
| 11 | Database variants | `Postgres, PostgreSQL, MongoDB, NoSQL, SQL` | variants in `databases` |
| 12 | Empty input | `""` | `name` == `""`, no skills |
| 13 | File read + JSON save round-trip | résumé file | reloaded JSON matches |
| 14 | Sample résumés shipped | — | both sample files exist |
| 15 | Year range is not a phone | `2019-2023. Call +57 300 123 4567` | `phones` == `[+57 300 123 4567]` |
| 16 | The verb "go" is not a language | `I go to work every day. Skills: Python` | `programming_languages` == `[Python]` |

## Stage 2 — Normalization (`tests/test_normalization.py`)

| # | Scenario | Input | Expected output |
|---|---|---|---|
| 1 | Variant → canonical (parametrized) | `JS`, `Javascript`, `React.js`, `ReactJS`, `NodeJS`, `Postgres`, `sklearn`, `scikit learn`, `Tensor Flow`, `Py Torch`, `K8s`, `PySpark`, `Hugging Face`, … | `JAVASCRIPT`, `REACT`, `NODE_JS`, `POSTGRESQL`, `SCIKIT_LEARN`, `TENSORFLOW`, `PYTORCH`, `KUBERNETES`, `SPARK`, `HUGGING_FACE`, … |
| 2 | Every declared variant translates | all `VARIANTS` | each → its canonical form |
| 3 | Unknown token | `COBOL` | `None` |
| 4 | Case-insensitive | `javascript`, `POSTGRES` | `JAVASCRIPT`, `POSTGRESQL` |
| 5 | Statement example | `Git, NodeJS, JS, Postgres, React.js` | `by_profile.full_stack` == `[JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT]` |
| 6 | Order independence | permutation of #5 | same `by_profile` |
| 7 | De-duplication | `JS, JavaScript, Javascript` | `canonical` == `[JAVASCRIPT]` |
| 8 | Unrecognized kept | `JS, COBOL, Git` | `canonical` == `[JAVASCRIPT, GIT]`, `unrecognized` == `[COBOL]` |
| 9 | Skill outside the profile is dropped | `JS, Ruby, Git` | `RUBY` in `canonical`; `full_stack` == `[JAVASCRIPT, GIT]` |
| 10 | Unknown profile | `sort_skills(..., "unknown_profile")` | `KeyError` |
| 11 | ML sample end-to-end | Mary Jane Watson résumé | `machine_learning` == `[PYTHON, PANDAS, NUMPY, SCIKIT_LEARN, TENSORFLOW, SQL, GIT]` |
| 12 | Four profiles available | `PROFILE_ORDER` | `[full_stack, machine_learning, ai_engineer, cloud_engineer]` |
| 13 | AI Engineer ordering | AI résumé skills | `[PYTHON, PANDAS, PYTORCH, SPARK, HUGGING_FACE, POSTGRESQL, DOCKER, AWS, GIT]` |
| 14 | Cloud Engineer ordering | Cloud résumé skills | `[AWS, AZURE, DOCKER, KUBERNETES, HELM, TERRAFORM, JENKINS, LINUX, GIT]` |
| 15 | Valid FST | `build_transducer("SCIKIT_LEARN")` | start `q0`, ≥1 final state, `SCIKIT_LEARN` in Γ |
| 16 | 7-tuple | `formal_definition("JAVASCRIPT")` | Q, Σ, Γ, δ, ω, q0, F filled |
| 17 | JSON save round-trip | `normalize([JS, Git])` | reloaded `canonical`, `translations`, `by_profile` match |
| 18 | Every Stage 1 skill is recognized | all skills Stage 1 can extract | `unrecognized` == `[]` |

## Stage 3 — Recognition (`tests/test_recognition.py`)

| # | Scenario | Input | Expected output |
|---|---|---|---|
| 1 | Assignment example automaton | `PYTHON, PANDAS, TENSORFLOW, POSTGRESQL, GIT` | `machine_learning` ACCEPTED |
| 2 | Wednesday Addams | sample résumé | only `full_stack` ACCEPTED |
| 3 | Mary Jane Watson | sample résumé | only `machine_learning` ACCEPTED |
| 4 | Several symbols of one group (loop) | `PYTHON, PANDAS, NUMPY, SCIKIT_LEARN, TENSORFLOW, SQL, GIT` | ACCEPTED |
| 5 | Missing required group | `JS, React.js, Postgres, Git` (no backend) | `full_stack` REJECTED |
| 6 | Wrong order | `GIT, PYTHON, PANDAS, TENSORFLOW, POSTGRESQL` | REJECTED |
| 7 | Empty sequence | `[]` in every profile | REJECTED |
| 8 | Extras after the final state | Full Stack + `Docker, REST APIs` | `full_stack` ACCEPTED |
| 9 | Optional group skipped (ε) | AI résumé without database | `ai_engineer` ACCEPTED |
| 10 | Required group missing | AI résumé without Spark / Hugging Face | `ai_engineer` REJECTED |
| 11 | AI Engineer full example | `Git, Python, PyTorch, Pandas, Hugging Face, PySpark, Postgres, Docker, AWS` | `ai_engineer` ACCEPTED |
| 12 | Cloud Engineer full example | `Git, Terraform, Docker, AWS, Kubernetes, Helm, Jenkins, Linux, Azure` | `cloud_engineer` ACCEPTED |
| 13 | Optional groups skipped (ε) | `AWS, Docker, Terraform, Linux, Git` | `cloud_engineer` ACCEPTED |
| 14 | Profile missing in the input | `by_profile` with only `full_stack` | others REJECTED with empty sequence |
| 15–18 | Automaton type (parametrized) | each profile | `full_stack`, `machine_learning`: DFA; `ai_engineer`, `cloud_engineer`: ε-NFA |
| 19 | 5-tuple | `formal_definition("machine_learning")` | Q = {q0…q5}, q0, F = {q5}, Σ, δ, type DFA, justification |
| 20 | Consistency with Stage 2 | every profile | group symbols + extras == `PROFILE_ORDER[profile]` |
| 21 | JSON save round-trip | Wednesday skills | reloaded result ACCEPTED, profile name kept |

## Stage 4 — Grammar / DSL

| # | Scenario | Input | Expected output |
|---|---|---|---|

## End-to-End Scenarios

| # | Scenario | Résumé | Expected result |
|---|---|---|---|
| 1 | Assignment Full Stack example | `wednesday_addams.txt` | Accepted profiles: `full_stack` |
| 2 | Assignment ML example | `mary_jane_watson.txt` | Accepted profiles: `machine_learning` |
| 3 | AI candidate (also satisfies ML) | Python, Pandas, PyTorch, PySpark, Hugging Face, Postgres, Docker, AWS, Git | Accepted profiles: `machine_learning`, `ai_engineer` |
| 4 | Cloud candidate | AWS, Azure, Docker, Kubernetes, Helm, Terraform, Jenkins, Linux, Git | Accepted profiles: `cloud_engineer` |
