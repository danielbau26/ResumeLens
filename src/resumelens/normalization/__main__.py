# Optional: lets you test stage 2 from the terminal, without Streamlit.
#   python -m resumelens.normalization --input <resume.txt|extraction.json> --profile full_stack
# --input accepts a raw résumé (.txt, extracted first) or a Stage 1 JSON (.json).
import argparse
import json
from pathlib import Path

from ..extraction import extract_from_file
from .normalizer import normalize_extraction, save_result
from .ordering import available_profiles


# Load a Stage 1 extraction dict from a résumé .txt or a Stage 1 .json file.
def _load_extraction(path):
    path = Path(path)
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return extract_from_file(path)


def main():
    parser = argparse.ArgumentParser(prog="python -m resumelens.normalization")
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--profile", "-p", choices=available_profiles(), default=None)
    parser.add_argument("--output", "-o")
    args = parser.parse_args()

    extraction = _load_extraction(args.input)
    result = normalize_extraction(extraction, profile=args.profile)

    if args.output:
        save_result(result, args.output)
        print(f"Normalized qualifications written to {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
