# Literature Review

This review presents the theoretical background and tools used in ResumeLens:
regular expressions for extraction, finite-state transducers for normalization,
finite automata for profile recognition, and a candidate domain-specific
language implemented with textX. It connects these concepts with the project’s
implementation choices and the assignment requirements [10].

## 1. Regular expressions and lexical extraction (Stage 1)

Classical regular expressions describe regular languages, which are also
recognized by finite automata [1, 2]. Stage 1 applies patterns to résumé
characters, while Stage 3 recognizes sequences of canonical skill symbols.

Python’s `re` library provides the pattern-matching operations used by the
extractor [9]. Python regex syntax includes features beyond classical
regular expressions, so the theoretical equivalence refers specifically
to classical regular expressions.

The extraction process resembles lexical analysis: predefined patterns
identify relevant fragments of the input text [3]. Two implementation
choices are important:

- **Alternative ordering.** Python’s `re` engine tries alternatives from
  left to right [9]. Longer variants are placed before shorter ones
  where appropriate, such as `PostgreSQL` before `Postgres`.
- **Custom token boundaries.** The standard `\b` boundary depends on word
  characters. Technology names containing `.`, `+`, or `#` need more
  specific boundaries. The `LB` and `RB` patterns help recognize names
  such as `React.js`, `C++`, and `C#` without matching fragments inside
  longer names.

Regular expressions are also used in text processing and information
extraction [4]. ResumeLens uses predefined patterns to extract contact
information, academic qualifications, experience, and technical skills.
This approach follows the assignment’s requirement to use regular
expressions [10].

The extractor recognizes only information covered by its patterns.
It does not provide general language understanding or detect every
possible qualification.

## 2. Finite-state transducers and canonicalization (Stage 2)

Finite-state transducers (FSTs) associate input sequences with output
sequences. ResumeLens implements these transformations using the `FST`
class provided by pyformlang [7].

ResumeLens uses one transducer per canonical skill. Each transducer reads
a supported variant character by character and produces a canonical
symbol. For example, `js` and `javascript` both produce `JAVASCRIPT`.

The accepted variants are defined in `VARIANTS`, and
`build_transducer(canonical)` constructs their transitions.

Variants with a shared prefix reuse the same states. For example,
`react`, `react.js`, and `reactjs` share the `r-e-a-c-t` path. Each state
has at most one transition for a given input character, making each
individual transducer deterministic.

The canonical symbol is emitted on the first transition. The remaining
transitions produce no additional text. A translation is returned only
when the complete input reaches a final state.

Using FSTs satisfies the assignment requirement and makes the
normalization rules explicit through states, transitions, output symbols,
and a formal 7-tuple [10].

After normalization, the program removes duplicate canonical skills
and sorts them according to each profile’s predefined order. This
ordering is a separate processing step, implemented in `ordering.py`.
Skills outside a profile’s catalogue are excluded from that profile’s
recognition sequence.

## 3. Finite automata and profile classification (Stage 3)

Deterministic finite automata (DFAs), nondeterministic finite automata
(NFAs), and ε-NFAs recognize the same class of regular languages [1, 2].
An ε-transition allows an automaton to change state without consuming
an input symbol.

ResumeLens represents each professional profile as an ordered sequence
of skill groups. A required group must contain at least one skill from
its defined set. Loops allow the automaton to read several skills from
the same group.

In this implementation:

- **Full Stack Developer** and **Machine Learning Engineer** use partial
  DFAs. Their groups have disjoint symbols and no ε-transitions.
- **AI Engineer** and **Cloud Engineer** use ε-NFAs. Their optional groups
  are represented by ε-transitions.

Missing transitions in a partial DFA cause rejection and can be understood
as transitions to an implicit dead state. Equivalent DFAs could also be
constructed for the profiles that currently use ε-NFAs [1, 2].

The automata are built with pyformlang [7]. One generic construction
function reads the declarative profile definitions and creates the
corresponding machines.

A profile is accepted when its ordered skill sequence reaches a final
state after all symbols have been consumed. The explicit transitions
make the recognition rules inspectable.

Classification checks the technical skill patterns defined for each profile.
It does not evaluate education, experience quality, candidate suitability,
or hiring priority.

Transducer and automaton diagrams are generated programmatically using
Graphviz and exported as `.dot` files.

## 4. Context-free grammars and DSL design (Stage 4)

Context-free grammars describe language syntax through production rules
[1, 2, 3]. In ResumeLens, the candidate grammar defines a fixed structure
containing contact information, education, experience, skills, and
accepted profiles.

All five sections are required, but their lists may contain zero or more
entries. The grammar therefore supports multiple contacts, education
records, experience descriptions, skills, and accepted profiles.

The current DSL has no recursive nesting. Repeated entries alone do not
require a language beyond the regular-language class. The project uses
a grammar specification and textX to follow the assignment requirements
and define the candidate structure explicitly [10].

A domain-specific language provides vocabulary and syntax tailored to
a particular problem [5]. ResumeLens uses keywords such as `candidate`,
`study`, `job`, `skill`, and `profile`.

The skill rule `[A-Z][A-Z0-9_]*` restricts skill names to uppercase
identifiers. It checks lexical formatting but does not verify whether
a skill belongs to the canonical catalogue. Canonicalization is performed
in Stage 2.

Dejanović et al. describe textX as a Python tool for implementing
domain-specific languages [6]. textX creates a parser and an object model
from a language specification [6, 8].

textX uses Arpeggio, a parser based on Parsing Expression Grammars (PEGs).
Alternatives use ordered choice, so their order must be considered when
designing and testing the grammar [8].

The project documents the candidate syntax using EBNF and implements it
in `candidate.tx` using textX rules.

Stage 4 combines information from the previous stages:

- Extracted candidate information from Stage 1.
- Canonical skills from Stage 2.
- Accepted profile results from Stage 3.

The generator produces a candidate specification, and the validator parses
it using textX. Invalid lexical or syntactic representations are rejected.
Once validation succeeds, the resulting object model is used to generate
a Markdown candidate summary.

## 5. Synthesis — connections between theory and implementation

| Literature or requirement | Implementation choice in ResumeLens |
|---|---|
| Regular languages and finite automata [1, 2] | Pattern-based extraction and recognition of canonical skill sequences. |
| Lexical analysis [3] and Python regex behavior [9] | Ordered alternatives and custom `LB`/`RB` boundaries. |
| Finite-state transducers in pyformlang [7] | One transducer per canonical skill, mapping supported variants to a common output. |
| Deterministic transitions [1, 2] | Shared-prefix construction for individual transducers. |
| ε-transitions and optionality [1, 2] | Optional profile groups represented by ε-transitions in this implementation. |
| pyformlang tools [7] | Construction and execution of transducers and profile automata. |
| Domain-specific languages [5] | Candidate keywords and explicit structural rules. |
| textX and PEG parsing [6, 8] | Grammar implementation with ordered alternatives and object-model generation. |
| Assignment requirements [10] | Four-stage pipeline, formal definitions, validation, and candidate visualization. |

## References

1. Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006).
   *Introduction to Automata Theory, Languages, and Computation*
   (3rd ed.). Addison-Wesley.

2. Sipser, M. (2012). *Introduction to the Theory of Computation*
   (3rd ed.). Cengage Learning.

3. Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006).
   *Compilers: Principles, Techniques, and Tools*
   (2nd ed.). Addison-Wesley.

4. Jurafsky, D., & Martin, J. H.
   *Speech and Language Processing* (3rd ed. draft).
   https://web.stanford.edu/~jurafsky/slp3/

5. Fowler, M., with Parsons, R. (2010).
   *Domain-Specific Languages*. Addison-Wesley.

6. Dejanović, I., Vaderna, R., Milosavljević, G., & Vuković, Ž. (2017).
   TextX: A Python tool for Domain-Specific Languages implementation.
   *Knowledge-Based Systems*, *115*, 1–4.
   https://doi.org/10.1016/j.knosys.2016.10.023

7. pyformlang documentation.
   https://pyformlang.readthedocs.io/

8. textX documentation.
   https://textx.github.io/textX/

9. Python Software Foundation.
   *re — Regular expression operations*. Python documentation.
   https://docs.python.org/3/library/re.html

10. Universidad Icesi, Departamento de Computación y Sistemas Inteligentes
    (2026). *Computación y Estructuras Discretas III — Integrative Task 1*
    [Course assignment statement].