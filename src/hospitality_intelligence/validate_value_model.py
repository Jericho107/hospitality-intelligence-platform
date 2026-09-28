"""Validate that the opportunity model reacts to controlled synthetic leakage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Value-model result must be a mapping")
    return payload


def _exposure_map(payload: dict[str, object]) -> dict[str, float]:
    opportunities = payload["opportunities"]
    if not isinstance(opportunities, list):
        raise ValueError("opportunities must be a list")
    return {
        str(item["driver"]): float(item["observed_exposure"])
        for item in opportunities
        if isinstance(item, dict)
    }


def validate(
    healthy_path: Path,
    leakage_path: Path,
    minimum_total_ratio: float,
) -> None:
    healthy = _load(healthy_path)
    leakage = _load(leakage_path)

    healthy_base = float(healthy["base_total"])
    leakage_base = float(leakage["base_total"])
    if leakage_base <= healthy_base * minimum_total_ratio:
        raise ValueError(
            f"Leakage base opportunity not sufficiently separated: "
            f"healthy={healthy_base}, leakage={leakage_base}"
        )

    healthy_exposure = _exposure_map(healthy)
    leakage_exposure = _exposure_map(leakage)
    required = {"purchase_price", "waste", "overtime_premium"}
    if set(healthy_exposure) != required or set(leakage_exposure) != required:
        raise ValueError("Unexpected value-driver set")

    for driver in required:
        if leakage_exposure[driver] <= healthy_exposure[driver]:
            raise ValueError(
                f"{driver}: leakage exposure must exceed healthy exposure "
                f"({leakage_exposure[driver]} <= {healthy_exposure[driver]})"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate synthetic value-proof separation.")
    parser.add_argument("--healthy", type=Path, required=True)
    parser.add_argument("--leakage", type=Path, required=True)
    parser.add_argument("--minimum-total-ratio", type=float, default=2.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    validate(args.healthy, args.leakage, args.minimum_total_ratio)
    print("Value-proof synthetic separation: PASS")


if __name__ == "__main__":
    main()
