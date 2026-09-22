"""Command-line entry point for Stage 1 extraction.

Usage:
    python -m resumelens.extraction --input data/sample_resumes/wednesday.txt
    python -m resumelens.extraction --input <file> --output out.json
"""

from __future__ import annotations

import argparse
import json
import sys

from .extractor import extract_file, save_result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m resumelens.extraction",
        description="Extract candidate information from a résumé (Stage 1).",
    )
    parser.add_argument("--input", "-i", required=True, help="Path to the résumé text file.")
    parser.add_argument(
        "--output",
        "-o",
        help="Optional path to write the extracted information as JSON.",
    )
    args = parser.parse_args(argv)

    result = extract_file(args.input)

    if args.output:
        destination = save_result(result, args.output)
        print(f"Extracted information written to {destination}")
    else:
        json.dump(result.to_dict(), sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
