"""Stage 1 — Résumé information extraction using regular expressions."""

from .extractor import (
    ExtractionResult,
    extract,
    extract_file,
    save_result,
)
from .patterns import PATTERNS, QUALIFICATION_CATEGORIES, PatternSpec

__all__ = [
    "ExtractionResult",
    "extract",
    "extract_file",
    "save_result",
    "PATTERNS",
    "QUALIFICATION_CATEGORIES",
    "PatternSpec",
]
