"""Stage 1 — Information extraction from résumé text.

This module applies the regular-expression catalogue defined in
:mod:`resumelens.extraction.patterns` to raw résumé text and returns the
matched surface forms grouped by category. The result can be kept in memory
as an :class:`ExtractionResult` (a plain data structure) or persisted to a
JSON file, as required by the assignment ("keep the extracted information in
a file or a data structure").

The extractor purposely does **not** normalize or deduplicate across
categories: it only reports what the regular expressions recognize. Canonical
forms are produced later, by the Stage 2 transducers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .patterns import PATTERNS, QUALIFICATION_CATEGORIES, PatternSpec


@dataclass
class ExtractionResult:
    """Structured output of the extraction stage.

    Attributes:
        matches: Mapping from category name to the list of matched strings,
            in order of first appearance and without duplicates.
    """

    matches: dict[str, list[str]] = field(default_factory=dict)

    def get(self, category: str) -> list[str]:
        """Return the matches for ``category`` (empty list if none)."""
        return self.matches.get(category, [])

    def qualifications(self) -> list[str]:
        """Flatten the technical-qualification categories into one list.

        These are the surface forms that feed the normalization stage, e.g.
        ``["JS", "React.js", "NodeJS", "Postgres", "Git"]``.
        """
        result: list[str] = []
        for category in QUALIFICATION_CATEGORIES:
            result.extend(self.matches.get(category, []))
        return result

    def to_dict(self) -> dict[str, list[str]]:
        """Return a JSON-serializable view of the result."""
        return {name: list(values) for name, values in self.matches.items()}


def _dedupe_preserving_order(values: list[str]) -> list[str]:
    """Remove duplicates (case-insensitively) while keeping first occurrence."""
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        key = value.casefold()
        if key not in seen:
            seen.add(key)
            unique.append(value)
    return unique


def extract(text: str, patterns: list[PatternSpec] | None = None) -> ExtractionResult:
    """Extract candidate information from ``text``.

    Patterns are applied in catalogue order and each accepted match *claims*
    the span of text it covers, so later patterns cannot match inside it. This
    prevents, for example, the "GitHub" tool pattern from matching inside the
    ``github.com/...`` URL that the contact-information pattern already
    recognized.

    Args:
        text: Raw résumé text.
        patterns: Optional custom catalogue; defaults to
            :data:`resumelens.extraction.patterns.PATTERNS`.

    Returns:
        An :class:`ExtractionResult` whose ``matches`` maps each category with
        at least one hit to its de-duplicated list of matched strings.
    """
    catalogue = patterns if patterns is not None else PATTERNS
    consumed = [False] * len(text)
    matches: dict[str, list[str]] = {}
    for spec in catalogue:
        found: list[str] = []
        for match in spec.regex.finditer(text):
            start, end = match.span()
            if any(consumed[start:end]):
                continue
            value = match.group(0).strip()
            if not value:
                continue
            found.append(value)
            for index in range(start, end):
                consumed[index] = True
        if found:
            matches[spec.name] = _dedupe_preserving_order(found)
    return ExtractionResult(matches=matches)


def extract_file(path: str | Path, patterns: list[PatternSpec] | None = None) -> ExtractionResult:
    """Read a résumé from ``path`` (UTF-8) and extract its information."""
    text = Path(path).read_text(encoding="utf-8")
    return extract(text, patterns=patterns)


def save_result(result: ExtractionResult, path: str | Path) -> Path:
    """Persist ``result`` as pretty-printed JSON and return the written path."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return destination
