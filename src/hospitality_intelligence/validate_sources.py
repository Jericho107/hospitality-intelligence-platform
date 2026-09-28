"""CLI validation for synthetic hospitality source systems."""

from __future__ import annotations

import argparse
from pathlib import Path

from hospitality_intelligence.contracts import load_and_validate_sources


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate hospitality source contracts."
    )
    parser.add_argument("--data-dir", default="data/sample")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frames = load_and_validate_sources(Path(args.data_dir))
    row_count = sum(len(frame) for frame in frames.values())
    print(f"Validated {len(frames)} source files and {row_count} rows.")


if __name__ == "__main__":
    main()
