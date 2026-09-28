"""Create controlled broken BI contracts for reverse testing."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def inject_unknown_measure(source: Path, output: Path) -> None:
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["pages"][0]["visuals"][0]["measures"] = ["Controllable Contribution"]
    output.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inject controlled BI contract failure.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case", choices=["unknown_measure"], required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inject_unknown_measure(args.source, args.output)
    print(f"Injected BI contract failure into {args.output}")


if __name__ == "__main__":
    main()
