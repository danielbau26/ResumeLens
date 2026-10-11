# Literature Review

This review surveys the theoretical and tooling background behind each stage of ResumeLens —
regular expressions for extraction, finite-state transducers for normalization, finite automata for
profile classification, and context-free grammars for the candidate DSL — together with the design
literature that shaped specific implementation choices. Its purpose, as requested by the assignment,
is to guide the project, avoid redundant approaches, make informed decisions, and ground the pipeline
in an established theoretical foundation before implementation.

## 1. Regular expressions and lexical extraction (Stage 1)

Regular expressions implement exactly the class of **regular languages** characterized by Kleene's
theorem — the same class recognized by finite automata [1, 2]. This equivalence is why Stage 1
(extraction) and Stage 3 (recognition) rest on the same theoretical footing even though they use
different tools (`re` vs. `pyformlang` automata): both decide membership in a regular language, one
over characters, the other over canonical qualification symbols.

Treating regex-based extraction as a **lexical-analysis** problem — rather than a general NLP task —
follows classical compiler-construction practice, where a lexer tokenizes raw input before any
higher-level parsing happens [3]. Two lexical-analysis conventions from that literature informed
`patterns.py` directly:

- **Longest-match (maximal munch).** Lexers prefer the longest valid token at a given position [3].
  `patterns.py` applies this manually by listing longer alternatives before shorter ones in each
  alternation (e.g. `PostgreSQL` before `Postgres`), so a longer technology name is not cut short by an
  earlier, shorter match.
- **Custom token boundaries.** The standard `\b` word boundary is defined over `\w` characters and
  therefore mishandles tokens containing `.`, `+` or `#` — exactly the compiler-construction problem of
  choosing a correct *token delimiter* for a given alphabet [3]. This motivated the hand-written
  `LB`/`RB` boundaries used throughout `patterns.py` to keep `React.js`, `C++` and `C#` intact.

Information extraction with regular expressions over free text is also a long-standing technique in
computational linguistics, surveyed alongside finite-state methods in Jurafsky & Martin's treatment of
regular expressions and text normalization [4]. We deliberately scoped Stage 1 to pattern-based
extraction rather than statistical Named-Entity Recognition (e.g. spaCy-style NER models): the
assignment requires a **formal**, auditable model, and a rule-based extractor keeps the scope aligned
with the course (regular languages) while avoiding the redundancy of building a separate ML pipeline
only to re-derive what a catalogue of regexes already expresses deterministically.

## 2. Finite-state transducers and canonicalization (Stage 2)

Finite-state transducers (FSTs) — automata that read an input tape and write an output tape — are the
standard formal device for **normalization and canonicalization** tasks in language processing,
surveyed comprehensively by Mohri [5]. Mohri's treatment of FSTs as composable input/output mappings
directly matches Stage 2's design: each `build_transducer(canonical)` is a single transducer mapping a
set of accepted surface strings to one output symbol, which is exactly the "mapping to a canonical
representation" use case Mohri identifies as a core FST application.

Spelling and form normalization via finite-state machines also has roots in computational morphology,
where Koskenniemi's two-level model uses finite-state transducers to relate surface word forms to
canonical lexical forms [6]. Although ResumeLens normalizes whole technology names rather than
morphological inflections, the underlying idea — many surface strings, one canonical output, computed
by a finite-state device rather than a lookup table — is the same, and justified choosing a transducer
over a plain dictionary lookup: a transducer gives the normalization a stated formal definition
(the 7-tuple) that a dictionary lookup does not.

Automata **determinism** is a well-studied property with direct performance and reasoning benefits
[1, 2]: a deterministic machine has at most one transition per symbol from each state, which makes
acceptance checking and self-explanation (`formal_definition`) straightforward. This motivated building
the transducers so that variants sharing a prefix **share states** (`react`, `react.js` and `reactjs`
reuse the same `r-e-a-c-t` path) rather than branching into separate paths per variant — the resulting
machine is a **deterministic FST (DFST)** by construction, not by a separate determinization pass.

## 3. Finite automata and profile classification (Stage 3)

The DFA/NFA/ε-NFA distinction, and the proof that all three recognize exactly the regular languages, is
foundational automata theory [1, 2]. Stage 3 relies on a specific, well-known consequence of that
theory: adding an ε-transition to skip an optional part of a pattern is the standard way to express
*optionality* in a finite automaton without leaving the regular-language class. This is why a profile
pattern with an optional skill group is built as an ε-NFA (AI Engineer, Cloud Engineer) while a profile
with only mandatory groups is a DFA (Full Stack Developer, Machine Learning Engineer): the automaton
type is read off the pattern definition, not chosen arbitrarily.

Using a deterministic, rule-based automaton for candidate–profile matching is also a deliberate
alternative to statistical applicant-tracking approaches (keyword scoring, embedding similarity, or
learned classifiers), which are common in industry ATS software but offer no formal guarantee about
*why* a candidate was accepted or rejected. A finite-automaton classifier trades some flexibility
(it cannot "almost" accept a sequence) for full **auditability**: every ACCEPTED/REJECTED outcome can
be traced through an explicit transition sequence. This trade-off is explicitly why the assignment
frames the task as pattern *recognition* rather than candidate *ranking*, and it is why ResumeLens
states — in its own problem statement — that it does not rank candidates.

## 4. Context-free grammars and DSL design (Stage 4)

Context-free grammars (CFGs) are the standard formalism for describing nested, block-structured
languages that regular languages cannot express, such as the Candidate DSL's arbitrarily repeated
blocks inside a single top-level structure [1, 2, 3]. Designing a small external DSL for a specific,
structured artifact — rather than overloading an existing format like JSON or YAML — follows the
guidance in Fowler & Parsons' treatment of domain-specific languages, which favors a purpose-built
external DSL when the artifact has its own vocabulary and structural rules worth enforcing at parse
time [7]. The Candidate DSL applies this directly: `skill` tokens are lexically restricted to the
canonical `[A-Z][A-Z0-9_]*` form, which a generic format could not enforce without a separate schema
layer.

The `textX` project itself is documented by Dejanović et al. [8]. One detail from that paper is
particularly relevant to how `candidate.tx` should be understood: `textX` grammars are implemented on
top of `Arpeggio`, a **Parsing Expression Grammar (PEG)** engine, not a classical CFG parser. PEGs
resolve alternatives with *ordered choice* instead of general ambiguity resolution, so a `textX`
grammar is guaranteed unambiguous by construction. This is why `candidate.tx` can be written and
reasoned about using ordinary EBNF notation (as required by the assignment) while still being
implemented and parsed deterministically by `textX`.

## 5. Synthesis — how this review shaped design decisions

| Literature | Design decision in ResumeLens |
|---|---|
| Longest-match lexing [3] | Longer surface forms listed before shorter ones in `patterns.py` alternations. |
| Custom token boundaries in lexical analysis [3] | Hand-written `LB`/`RB` regex boundaries instead of `\b`. |
| FSTs for canonicalization [5, 6] | One transducer per canonical symbol instead of a plain string-to-string dictionary. |
| Automata determinism [1, 2] | Prefix-sharing transducer construction &rarr; deterministic FST by design. |
| ε-transitions encode optionality [1, 2] | Optional profile groups &rarr; ε-NFA; all-mandatory profiles &rarr; DFA. |
| Rule-based vs. statistical classification | Deterministic automata chosen over ML scoring, matching the "recognize, don't rank" scope. |
| External DSL design guidance [7] | A purpose-built Candidate DSL instead of reusing JSON/YAML. |
| PEG-based `textX` parsing [8] | `candidate.tx` can use ordinary EBNF without ambiguity concerns. |

## References

1. Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006). *Introduction to Automata Theory, Languages,
   and Computation* (3rd ed.). Addison-Wesley.
2. Sipser, M. (2012). *Introduction to the Theory of Computation* (3rd ed.). Cengage Learning.
3. Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and
   Tools* (2nd ed.). Addison-Wesley.
4. Jurafsky, D., & Martin, J. H. *Speech and Language Processing* (3rd ed. draft). Chapters on regular
   expressions, text normalization, and finite-state methods. Stanford University.
5. Mohri, M. (1997). Finite-State Transducers in Language and Speech Processing. *Computational
   Linguistics*, 23(2), 269–311.
6. Koskenniemi, K. (1983). *Two-Level Morphology: A General Computational Model for Word-Form
   Recognition and Production*. University of Helsinki.
7. Fowler, M., & Parsons, R. (2010). *Domain-Specific Languages*. Addison-Wesley.
8. Dejanović, I., Vaderna, R., Milosavljević, G., & Vuković, Ž. (2017). TextX: A Python tool for
   Domain-Specific Languages implementation. *Knowledge-Based Systems*, 115, 1–4.
9. pyformlang documentation. https://pyformlang.readthedocs.io/
10. textX documentation. https://textx.github.io/textX/
11. Python Software Foundation. *re — Regular expression operations*. Python documentation.
    https://docs.python.org/3/library/re.html
12. Universidad Icesi, Departamento de Computación y Sistemas Inteligentes (2026). *Computación y
    Estructuras Discretas III — Integrative Task 1* [Course assignment statement].
