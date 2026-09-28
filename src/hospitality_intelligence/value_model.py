"""Auditable management-action opportunity model for synthetic hospitality data."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "config" / "action_value_contract.yml"


@dataclass(frozen=True)
class Opportunity:
    driver: str
    observed_exposure: float
    conservative: float
    base: float
    stretch: float
    action: str
    owner: str
    measurement_metric: str
    review_window_days: int
    limitation: str


@dataclass(frozen=True)
class ValueModel:
    property_id: str
    analysis_start: str
    analysis_end: str
    baseline_start: str
    baseline_end: str
    opportunities: list[Opportunity]
    conservative_total: float
    base_total: float
    stretch_total: float


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, object]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Action-value contract root must be a mapping")

    scope = payload.get("scope")
    recovery = payload.get("recovery_scenarios")
    labour = payload.get("labour")
    actions = payload.get("actions")
    if not all(isinstance(item, dict) for item in [scope, recovery, labour, actions]):
        raise ValueError("Malformed action-value contract")

    conservative = float(recovery["conservative"])
    base = float(recovery["base"])
    stretch = float(recovery["stretch"])
    if not 0 <= conservative <= base <= stretch <= 1:
        raise ValueError(\n            "Recovery scenarios must satisfy 0 <= conservative <= base <= stretch <= 1"\n        )
    if int(scope["analysis_window_days"]) <= 0 or int(scope["baseline_window_days"]) <= 0:
        raise ValueError("Value-model windows must be positive")
    premium = float(labour["overtime_premium_rate"])
    if not 0 <= premium <= 1:
        raise ValueError("Overtime premium rate must be between 0 and 1")

    return payload


def _read(data_dir: Path, filename: str) -> pd.DataFrame:
    frame = pd.read_csv(data_dir / filename)
    if "date" in frame.columns:
        frame["date"] = pd.to_datetime(frame["date"])
    return frame


def _windows(
    frame: pd.DataFrame,
    analysis_days: int,
    baseline_days: int,
) -> tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp]:
    end = frame["date"].max()
    analysis_start = end - pd.Timedelta(days=analysis_days - 1)
    baseline_end = analysis_start - pd.Timedelta(days=1)
    baseline_start = baseline_end - pd.Timedelta(days=baseline_days - 1)
    if baseline_start < frame["date"].min():
        raise ValueError("Insufficient history for action-value baseline")
    return analysis_start, end, baseline_start, baseline_end


def _recovery_values(
    exposure: float,
    recovery: dict[str, float],
) -> tuple[float, float, float]:
    return (
        exposure * float(recovery["conservative"]),
        exposure * float(recovery["base"]),
        exposure * float(recovery["stretch"]),
    )


def _opportunity(
    driver: str,
    exposure: float,
    recovery: dict[str, float],
    action: dict[str, object],
) -> Opportunity:
    conservative, base, stretch = _recovery_values(max(0.0, exposure), recovery)
    return Opportunity(
        driver=driver,
        observed_exposure=round(max(0.0, exposure), 2),
        conservative=round(conservative, 2),
        base=round(base, 2),
        stretch=round(stretch, 2),
        action=str(action["title"]),
        owner=str(action["owner"]),
        measurement_metric=str(action["measurement_metric"]),
        review_window_days=int(action["review_window_days"]),
        limitation=str(action["limitation"]),
    )


def evaluate(
    data_dir: Path,
    contract_path: Path = CONTRACT_PATH,
) -> ValueModel:
    """Estimate recoverable opportunity without claiming realized savings."""

    contract = load_contract(contract_path)
    scope = contract["scope"]
    recovery = contract["recovery_scenarios"]
    labour_contract = contract["labour"]
    actions = contract["actions"]
    if not all(isinstance(item, dict) for item in [scope, recovery, labour_contract, actions]):
        raise ValueError("Malformed action-value contract")

    property_id = str(scope["property_id"])
    category = str(scope["product_category"])
    department_id = str(scope["labour_department_id"])
    analysis_days = int(scope["analysis_window_days"])
    baseline_days = int(scope["baseline_window_days"])

    products = _read(data_dir, "products.csv")
    purchases = _read(data_dir, "purchases_daily.csv")
    inventory = _read(data_dir, "inventory_daily.csv")
    labour = _read(data_dir, "labour_daily.csv")

    analysis_start, analysis_end, baseline_start, baseline_end = _windows(
        purchases,
        analysis_days,
        baseline_days,
    )

    beverage_products = products.loc[
        (products["property_id"] == property_id) & (products["category"] == category),
        ["product_id", "standard_unit_cost"],
    ].copy()
    if beverage_products.empty:
        raise ValueError("No products found for action-value scope")

    current_purchases = purchases[
        (purchases["property_id"] == property_id)
        & purchases["product_id"].isin(beverage_products["product_id"])
        & purchases["date"].between(analysis_start, analysis_end)
    ].merge(beverage_products, on="product_id", how="left", validate="many_to_one")

    purchase_price_exposure = (
        (
            current_purchases["unit_cost"] - current_purchases["standard_unit_cost"]
        ).clip(lower=0)
        * current_purchases["quantity"]
    ).sum()

    scoped_inventory = inventory[
        (inventory["property_id"] == property_id)
        & inventory["product_id"].isin(beverage_products["product_id"])
    ].copy()
    baseline_inventory = scoped_inventory[
        scoped_inventory["date"].between(baseline_start, baseline_end)
    ]
    current_inventory = scoped_inventory[
        scoped_inventory["date"].between(analysis_start, analysis_end)
    ]

    baseline_depletion = (
        baseline_inventory["usage_qty"] + baseline_inventory["waste_qty"]
    ).sum()
    baseline_waste_rate = (
        0.0
        if baseline_depletion == 0
        else float(baseline_inventory["waste_qty"].sum() / baseline_depletion)
    )
    current_depletion = current_inventory["usage_qty"] + current_inventory["waste_qty"]
    expected_waste = current_depletion * baseline_waste_rate
    excess_waste_qty = (current_inventory["waste_qty"] - expected_waste).clip(lower=0)
    waste_exposure = float(
        (excess_waste_qty * current_inventory["weighted_unit_cost"]).sum()
    )

    scoped_labour = labour[
        (labour["property_id"] == property_id)
        & (labour["department_id"] == department_id)
    ].copy()
    baseline_labour = scoped_labour[
        scoped_labour["date"].between(baseline_start, baseline_end)
    ]
    current_labour = scoped_labour[
        scoped_labour["date"].between(analysis_start, analysis_end)
    ]

    baseline_actual_hours = float(baseline_labour["actual_hours"].sum())
    baseline_overtime_share = (
        0.0
        if baseline_actual_hours == 0
        else float(baseline_labour["overtime_hours"].sum() / baseline_actual_hours)
    )
    current_actual_hours = float(current_labour["actual_hours"].sum())
    expected_overtime_hours = current_actual_hours * baseline_overtime_share
    excess_overtime_hours = max(
        0.0,
        float(current_labour["overtime_hours"].sum()) - expected_overtime_hours,
    )

    premium_rate = float(labour_contract["overtime_premium_rate"])
    denominator = float(
        current_labour["actual_hours"].sum()
        + premium_rate * current_labour["overtime_hours"].sum()
    )
    base_hourly_rate = (
        0.0 if denominator == 0 else float(current_labour["labour_cost"].sum()) / denominator
    )
    overtime_premium_exposure = excess_overtime_hours * base_hourly_rate * premium_rate

    opportunities = [
        _opportunity(
            "purchase_price",
            float(purchase_price_exposure),
            recovery,
            actions["purchase_price"],
        ),
        _opportunity(
            "waste",
            waste_exposure,
            recovery,
            actions["waste"],
        ),
        _opportunity(
            "overtime_premium",
            overtime_premium_exposure,
            recovery,
            actions["overtime"],
        ),
    ]

    return ValueModel(
        property_id=property_id,
        analysis_start=analysis_start.date().isoformat(),
        analysis_end=analysis_end.date().isoformat(),
        baseline_start=baseline_start.date().isoformat(),
        baseline_end=baseline_end.date().isoformat(),
        opportunities=opportunities,
        conservative_total=round(sum(item.conservative for item in opportunities), 2),
        base_total=round(sum(item.base for item in opportunities), 2),
        stretch_total=round(sum(item.stretch for item in opportunities), 2),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate modeled management opportunity.")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = evaluate(args.data_dir)
    payload = asdict(result)
    print(json.dumps(payload, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
