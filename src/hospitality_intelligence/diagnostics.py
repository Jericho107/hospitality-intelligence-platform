"""Counterfactual benchmark for validating hospitality diagnostic logic.

This module compares paired synthetic scenarios generated with the same seed and
anchor. It is a validation harness, not a production counterfactual engine.
"""

from __future__ import annotations

import argparse
import json
from datetime import timedelta
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class ScenarioSnapshot:
    beverage_unit_cost: float
    beverage_waste_rate: float
    fnb_overtime_share: float
    rooms_sold: float
    fnb_net_revenue: float


@dataclass(frozen=True)
class DriverResult:
    driver: str
    baseline: float
    candidate: float
    delta: float
    relative_delta: float | None
    adverse: bool
    context: str


def _read(data_dir: Path, filename: str) -> pd.DataFrame:
    path = data_dir / filename
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _safe_ratio(numerator: float, denominator: float) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def _final_window(frame: pd.DataFrame, date_column: str, days: int = 20) -> pd.DataFrame:
    """Return the final calendar window from a dated source frame."""

    dates = pd.to_datetime(frame[date_column])
    end = dates.max()
    start = end - timedelta(days=days - 1)
    return frame.loc[dates.between(start, end)].copy()


def snapshot(data_dir: Path, property_id: str = "P002") -> ScenarioSnapshot:
    """Build scenario-level evidence for the controlled leakage property."""

    products = _read(data_dir, "products.csv")
    purchases = _final_window(_read(data_dir, "purchases_daily.csv"), "date")
    inventory = _final_window(_read(data_dir, "inventory_daily.csv"), "date")
    labour = _final_window(_read(data_dir, "labour_daily.csv"), "date")
    bookings = _final_window(_read(data_dir, "pms_bookings_daily.csv"), "date")
    pos = _final_window(_read(data_dir, "pos_checks_daily.csv"), "date")

    beverage_products = set(
        products.loc[
            (products["property_id"] == property_id) & (products["category"] == "beverage"),
            "product_id",
        ]
    )

    bev_purchases = purchases[
        (purchases["property_id"] == property_id)
        & purchases["product_id"].isin(beverage_products)
    ]
    weighted_cost = _safe_ratio(
        float((bev_purchases["unit_cost"] * bev_purchases["quantity"]).sum()),
        float(bev_purchases["quantity"].sum()),
    )

    bev_inventory = inventory[
        (inventory["property_id"] == property_id)
        & inventory["product_id"].isin(beverage_products)
    ]
    waste_rate = _safe_ratio(
        float(bev_inventory["waste_qty"].sum()),
        float((bev_inventory["usage_qty"] + bev_inventory["waste_qty"]).sum()),
    )

    fnb_labour = labour[
        (labour["property_id"] == property_id) & (labour["department_id"] == "D002")
    ]
    overtime_share = _safe_ratio(
        float(fnb_labour["overtime_hours"].sum()),
        float(fnb_labour["actual_hours"].sum()),
    )

    rooms_sold = float(
        bookings.loc[bookings["property_id"] == property_id, "rooms_sold"].sum()
    )
    fnb_net_revenue = float(
        pos.loc[pos["property_id"] == property_id, "net_revenue"].sum()
    )

    return ScenarioSnapshot(
        beverage_unit_cost=weighted_cost,
        beverage_waste_rate=waste_rate,
        fnb_overtime_share=overtime_share,
        rooms_sold=rooms_sold,
        fnb_net_revenue=fnb_net_revenue,
    )


def _driver(
    name: str,
    baseline: float,
    candidate: float,
    adverse_threshold: float | None,
    context: str,
) -> DriverResult:
    delta = candidate - baseline
    relative = None if baseline == 0 else delta / baseline
    adverse = (
        adverse_threshold is not None
        and relative is not None
        and relative >= adverse_threshold
    )
    return DriverResult(
        driver=name,
        baseline=baseline,
        candidate=candidate,
        delta=delta,
        relative_delta=relative,
        adverse=adverse,
        context=context,
    )


def compare_scenarios(
    baseline_dir: Path,
    candidate_dir: Path,
) -> list[DriverResult]:
    """Compare paired synthetic scenarios and return explicit driver evidence."""

    base = snapshot(baseline_dir)
    candidate = snapshot(candidate_dir)

    return [
        _driver(
            "beverage_purchase_cost_pressure",
            base.beverage_unit_cost,
            candidate.beverage_unit_cost,
            0.08,
            "adverse_cost",
        ),
        _driver(
            "beverage_waste_pressure",
            base.beverage_waste_rate,
            candidate.beverage_waste_rate,
            0.50,
            "adverse_waste",
        ),
        _driver(
            "fnb_overtime_pressure",
            base.fnb_overtime_share,
            candidate.fnb_overtime_share,
            0.50,
            "adverse_labour",
        ),
        _driver(
            "room_demand_change",
            base.rooms_sold,
            candidate.rooms_sold,
            None,
            "demand_context",
        ),
        _driver(
            "fnb_revenue_change",
            base.fnb_net_revenue,
            candidate.fnb_net_revenue,
            None,
            "revenue_context",
        ),
    ]


def adverse_drivers(results: list[DriverResult]) -> list[DriverResult]:
    """Return adverse drivers ranked by relative deterioration."""

    return sorted(
        (result for result in results if result.adverse),
        key=lambda result: result.relative_delta or 0.0,
        reverse=True,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark hospitality diagnostic recovery.")
    parser.add_argument("--baseline-dir", required=True)
    parser.add_argument("--candidate-dir", required=True)
    parser.add_argument("--require-adverse", nargs="*", default=[])
    parser.add_argument("--require-none", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = compare_scenarios(Path(args.baseline_dir), Path(args.candidate_dir))
    print(json.dumps([asdict(result) for result in results], indent=2))

    detected = {result.driver for result in adverse_drivers(results)}
    required = set(args.require_adverse)

    if not required.issubset(detected):
        missing = sorted(required - detected)
        raise SystemExit(f"Required adverse drivers not detected: {missing}")
    if args.require_none and detected:
        raise SystemExit(f"Expected no adverse drivers, detected: {sorted(detected)}")


if __name__ == "__main__":
    main()
