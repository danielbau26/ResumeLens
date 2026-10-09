"""Command-line entry point for Stage 2 normalization.

Accepts either a raw résumé text file (it is extracted first) or a Stage 1
extraction JSON file, normalizes the qualifications, and optionally sorts them
by a professional profile.

Usage:
    python -m resumelens.normalization --input data/sample_resumes/wednesday_addams.txt --profile full_stack
    python -m resumelens.normalization --input examples/output/wednesday_addams.json --profile full_stack -o out.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ..extraction import extract_from_file
from .normalizer import normalize_extraction, save_result
from .ordering import available_profiles


def _load_extraction(path: Path) -> dict:
    """Load a Stage 1 extraction dict from a résumé .txt or a Stage 1 .json file."""
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return extract_from_file(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m resumelens.normalization",
        description="Normalize résumé qualifications with finite-state transducers (Stage 2).",
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Résumé text file (.txt) or Stage 1 extraction JSON (.json).",
    )
    parser.add_argument(
        "--profile", "-p", choices=available_profiles(), default=None,
        help="Profile whose canonical order is used to sort the output.",
    )
    parser.add_argument(
        "--output", "-o",
        help="Optional path to write the normalized result as JSON.",
    )
    args = parser.parse_args(argv)

    extraction = _load_extraction(Path(args.input))
    result = normalize_extraction(extraction, profile=args.profile)

    if args.output:
        destination = save_result(result, args.output)
        print(f"Normalized qualifications written to {destination}")
    else:
        json.dump(result.to_dict(), sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
