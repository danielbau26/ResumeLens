"""Stage 2 — Qualification normalization using finite-state transducers."""

from .normalizer import (
    NormalizationResult,
    normalize,
    normalize_extraction,
    save_result,
)
from .ordering import PROFILE_ORDER, available_profiles, sort_qualifications
from .transducers import (
    build_all,
    build_transducer,
    combined_transducer,
    export_diagrams,
    normalize_token,
)
from .transformations import RULES, TransductionRule, canonical_forms

__all__ = [
    "NormalizationResult",
    "normalize",
    "normalize_extraction",
    "save_result",
    "PROFILE_ORDER",
    "available_profiles",
    "sort_qualifications",
    "build_all",
    "build_transducer",
    "combined_transducer",
    "export_diagrams",
    "normalize_token",
    "RULES",
    "TransductionRule",
    "canonical_forms",
]
