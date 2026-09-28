"""Stage 2 finite-state transducers, implemented with pyformlang.

Each :class:`~resumelens.normalization.transformations.TransductionRule` is
compiled into a **character-level** finite-state transducer (FST):

* the input alphabet ``Σ`` is the set of characters of the accepted variants
  (matching is done on a case-folded token, so ``JS`` and ``js`` share paths);
* the output alphabet ``Γ`` is the singleton canonical symbol, e.g.
  ``{JAVASCRIPT}``;
* every variant is a path of states from the start state ``q0`` that converges
  on a single accepting state; the canonical symbol is emitted on the first
  transition (``ω``) and the empty string on the rest.

Thus running :meth:`pyformlang.fst.FST.translate` on the characters of any
accepted variant yields the canonical form, and any other word yields nothing.
A :func:`combined_transducer` unions all per-rule FSTs into the single
transducer view, and :func:`export_diagrams` renders the graphical
representation required by the assignment.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from pyformlang.fst import FST

from .transformations import RULES, TransductionRule


def _fold(token: str) -> str:
    """Case-normalize a token so casing variants collapse onto shared paths."""
    return token.casefold()


def build_transducer(rule: TransductionRule) -> FST:
    """Build the character-level FST for a single transformation ``rule``.

    The FST accepts exactly the (case-folded) variants of ``rule`` and outputs
    ``rule.canonical`` once per accepted word.
    """
    fst = FST()
    start = "q0"
    accept = "qf"
    fst.add_start_state(start)
    fst.add_final_state(accept)

    counter = 0
    for variant in rule.variants:
        symbols = list(_fold(variant))
        if not symbols:
            continue
        # Walk the characters, creating fresh intermediate states per variant so
        # that branches only merge at the shared accepting state.
        current = start
        for index, symbol in enumerate(symbols):
            is_last = index == len(symbols) - 1
            target = accept if is_last else f"{rule.canonical}_{counter}"
            counter += 1
            # Emit the canonical symbol on the first transition, nothing after.
            output = [rule.canonical] if index == 0 else []
            fst.add_transition(current, symbol, target, output)
            current = target
    return fst


def build_all() -> dict[str, FST]:
    """Build one FST per canonical form, keyed by the canonical symbol."""
    return {rule.canonical: build_transducer(rule) for rule in RULES}


def combined_transducer() -> FST:
    """Union every per-rule FST into a single transducer.

    This is the "one transducer" view: it accepts the variants of *all* rules
    and outputs the corresponding canonical symbol for each.
    """
    fst: FST | None = None
    for rule in RULES:
        current = build_transducer(rule)
        fst = current if fst is None else fst.union(current)
    return fst if fst is not None else FST()


# A cached per-rule map so token normalization does not rebuild FSTs each call.
_TRANSDUCERS: dict[str, FST] = {}


def normalize_token(token: str) -> str | None:
    """Return the canonical form of ``token`` or ``None`` if unrecognized.

    Runs the token's characters through each rule's FST and returns the first
    canonical symbol produced. Because variant sets are disjoint, at most one
    rule accepts a given token.
    """
    if not _TRANSDUCERS:
        _TRANSDUCERS.update(build_all())
    symbols = list(_fold(token.strip()))
    for canonical, fst in _TRANSDUCERS.items():
        for output in fst.translate(symbols):
            if output:
                return output[0]
    return None


def export_diagrams(dest_dir: str | Path, canonicals: list[str] | None = None) -> list[Path]:
    """Write a Graphviz diagram per transducer into ``dest_dir``.

    A ``.dot`` file is always written (via :meth:`FST.write_as_dot`); a ``.png``
    is additionally rendered when the Graphviz ``dot`` binary is available.

    Args:
        dest_dir: Output directory (created if missing).
        canonicals: Optional subset of canonical names to export; defaults to
            all rules.

    Returns:
        The list of files written.
    """
    destination = Path(dest_dir)
    destination.mkdir(parents=True, exist_ok=True)
    transducers = build_all()
    if canonicals is not None:
        transducers = {name: transducers[name] for name in canonicals if name in transducers}

    dot_binary = shutil.which("dot")
    written: list[Path] = []
    for canonical, fst in transducers.items():
        dot_path = destination / f"{canonical}.dot"
        fst.write_as_dot(str(dot_path))
        written.append(dot_path)
        if dot_binary:
            png_path = destination / f"{canonical}.png"
            subprocess.run(
                [dot_binary, "-Tpng", str(dot_path), "-o", str(png_path)],
                check=False,
            )
            if png_path.exists():
                written.append(png_path)
    return written
