"""Stage 3 — generic builder: turns a profile pattern into a finite automaton."""

from __future__ import annotations

from dataclasses import dataclass
##instalar pyformlang

from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol


@dataclass(frozen=True)
class ProfilePattern:
    """Qualification pattern of one professional profile.

    Attributes:
        profile: Profile identifier (same keys as ``PROFILE_ORDER``).
        description: Plain-language description of the pattern.
        groups: Ordered groups of interchangeable canonical symbols. A word is
            accepted when it contains one or more symbols of each group, in
            group order.
    """

    profile: str
    description: str
    groups: tuple[tuple[str, ...], ...]

    def alphabet(self) -> set[str]:
        """Return every symbol used by the pattern (the alphabet Σ)."""
        return {symbol for group in self.groups for symbol in group}

def build_automaton(pattern: ProfilePattern) -> DeterministicFiniteAutomaton:
    """Build the DFA that recognizes ``pattern``.

    State ``q{i}`` means "groups 0..i-1 are satisfied". Reading a symbol of
    group ``i`` moves ``q{i} -> q{i+1}``; ``q{i+1}`` loops on the same group so
    several symbols of one group are allowed. The last state is accepting.
    """
    symbols = [symbol for group in pattern.groups for symbol in group]
    if len(symbols) != len(set(symbols)):
        raise ValueError(f"Groups of profile {pattern.profile!r} must be disjoint")

    dfa = DeterministicFiniteAutomaton()
    dfa.add_start_state(State("q0"))
    dfa.add_final_state(State(f"q{len(pattern.groups)}"))
    for index, group in enumerate(pattern.groups):
        source = State(f"q{index}")
        target = State(f"q{index + 1}")
        for symbol in group:
            dfa.add_transition(source, Symbol(symbol), target)
            dfa.add_transition(target, Symbol(symbol), target)
    return dfa
