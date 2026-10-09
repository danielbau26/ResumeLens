"""Stage 2 orchestrator: transduce, de-duplicate and sort qualifications.

This ties the pieces together: surface-form tokens (from Stage 1) are pushed
through the finite-state transducers, the resulting canonical symbols are
de-duplicated, and — when a professional profile is given — reordered into that
profile's canonical order. Tokens that no transducer recognizes are kept in a
separate ``unrecognized`` list so nothing is silently dropped.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ..extraction import get_skills
from .ordering import sort_qualifications
from .transducers import normalize_token


@dataclass
class NormalizationResult:
    """Structured output of the normalization stage.

    Attributes:
        canonical: The de-duplicated (and, if a profile was given, sorted)
            canonical qualifications — the input for Stage 3.
        mapping: The ``(surface, canonical)`` pairs produced by the transducers,
            in input order, as a normalization trace.
        unrecognized: Surface tokens that no transducer accepted.
        profile: The profile used to sort ``canonical`` (or ``None``).
    """

    canonical: list[str] = field(default_factory=list)
    mapping: list[tuple[str, str]] = field(default_factory=list)
    unrecognized: list[str] = field(default_factory=list)
    profile: str | None = None

    def to_dict(self) -> dict:
        """Return a JSON-serializable view of the result."""
        return {
            "profile": self.profile,
            "canonical": list(self.canonical),
            "mapping": [list(pair) for pair in self.mapping],
            "unrecognized": list(self.unrecognized),
        }


def _dedupe_preserving_order(values: list[str]) -> list[str]:
    """Remove duplicates while keeping first occurrence (mirrors extractor)."""
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            unique.append(value)
    return unique


def normalize(surface_tokens: list[str], profile: str | None = None) -> NormalizationResult:
    """Normalize ``surface_tokens`` into canonical qualifications.

    Args:
        surface_tokens: Surface forms, e.g. ``["JS", "React.js", "NodeJS"]``.
        profile: Optional profile identifier used to sort the output
            (see :data:`resumelens.normalization.ordering.PROFILE_ORDER`).

    Returns:
        A :class:`NormalizationResult`.
    """
    mapping: list[tuple[str, str]] = []
    unrecognized: list[str] = []
    canonical: list[str] = []

    for token in surface_tokens:
        result = normalize_token(token)
        if result is None:
            unrecognized.append(token)
            continue
        mapping.append((token, result))
        canonical.append(result)

    canonical = _dedupe_preserving_order(canonical)
    if profile is not None:
        canonical = sort_qualifications(canonical, profile)

    return NormalizationResult(
        canonical=canonical,
        mapping=mapping,
        unrecognized=_dedupe_preserving_order(unrecognized),
        profile=profile,
    )


def normalize_extraction(data: dict, profile: str | None = None) -> NormalizationResult:
    """Normalize the qualifications flattened from a Stage 1 extraction dict."""
    return normalize(get_skills(data), profile=profile)


def save_result(result: NormalizationResult, path: str | Path) -> Path:
    """Persist ``result`` as pretty-printed JSON and return the written path."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return destination
