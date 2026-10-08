"""Stage 3 — generic builder: turns a profile pattern into a finite automaton."""

from __future__ import annotations

from dataclasses import dataclass

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
