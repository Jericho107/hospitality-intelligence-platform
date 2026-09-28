"""Controlled failure injection for reverse-testing source contracts."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def inject_pos_revenue_mismatch(data_dir: Path) -> None:
    """Break POS product-mix reconciliation without changing the check source."""

    path = data_dir / "pos_product_mix_daily.csv"
    frame = pd.read_csv(path)
    if frame.empty:
        raise ValueError(
            "Cannot inject failure into an empty product-mix file"
        )
    frame.loc[0, "net_revenue"] = round(
        float(frame.loc[0, "net_revenue"]) + 10.0,
        2,
    )
    frame.to_csv(path, index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inject a controlled source-data failure."
    )
    parser.add_argument("--data-dir", default="data/sample")
    parser.add_argument(
        "--case",
        choices=["pos_revenue_mismatch"],
        default="pos_revenue_mismatch",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.case == "pos_revenue_mismatch":
        inject_pos_revenue_mismatch(Path(args.data_dir))
        print("Injected controlled POS revenue mismatch.")


if __name__ == "__main__":
    main()
