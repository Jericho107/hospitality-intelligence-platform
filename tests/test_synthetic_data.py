from datetime import date
from pathlib import Path

import pandas as pd

from hospitality_intelligence.contracts import load_and_validate_sources
from hospitality_intelligence.generate_synthetic_data import (
    GenerationConfig,
    generate,
)

FIXED_CONFIG = GenerationConfig(
    days=45,
    seed=17,
    anchor_date=date(2026, 9, 1),
    scenario="margin_leakage",
)


def test_same_configuration_produces_identical_files(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    generate(FIXED_CONFIG, first)
    generate(FIXED_CONFIG, second)

    first_files = sorted(path.name for path in first.glob("*.csv"))
    second_files = sorted(path.name for path in second.glob("*.csv"))
    assert first_files == second_files
    assert len(first_files) == 13

    for filename in first_files:
        assert (
            first / filename
        ).read_bytes() == (second / filename).read_bytes()


def test_generated_sources_pass_contract_validation(
    tmp_path: Path,
) -> None:
    generate(FIXED_CONFIG, tmp_path)
    frames = load_and_validate_sources(tmp_path)

    assert len(frames["properties.csv"]) == 3
    assert len(frames["outlets.csv"]) == 8
    assert not frames["pms_bookings_daily.csv"].empty
    assert not frames["inventory_daily.csv"].empty


def test_margin_leakage_scenario_has_controlled_cost_pressure(
    tmp_path: Path,
) -> None:
    generate(FIXED_CONFIG, tmp_path)
    products = pd.read_csv(tmp_path / "products.csv")
    purchases = pd.read_csv(tmp_path / "purchases_daily.csv")
    labour = pd.read_csv(tmp_path / "labour_daily.csv")

    beverage_ids = set(
        products.loc[
            (products["property_id"] == "P002")
            & (products["category"] == "beverage"),
            "product_id",
        ]
    )
    resort_beverage = purchases[
        (purchases["property_id"] == "P002")
        & (purchases["product_id"].isin(beverage_ids))
    ].copy()
    resort_beverage["date"] = pd.to_datetime(
        resort_beverage["date"]
    )
    split = resort_beverage["date"].max() - pd.Timedelta(days=19)
    early = resort_beverage[
        resort_beverage["date"] < split
    ]["unit_cost"].mean()
    late = resort_beverage[
        resort_beverage["date"] >= split
    ]["unit_cost"].mean()

    resort_fnb = labour[
        (labour["property_id"] == "P002")
        & (labour["department_id"] == "D002")
    ].copy()
    resort_fnb["date"] = pd.to_datetime(resort_fnb["date"])
    labour_split = resort_fnb["date"].max() - pd.Timedelta(days=19)
    early_overtime = resort_fnb[
        resort_fnb["date"] < labour_split
    ]["overtime_hours"].mean()
    late_overtime = resort_fnb[
        resort_fnb["date"] >= labour_split
    ]["overtime_hours"].mean()

    assert late > early * 1.07
    assert late_overtime > early_overtime
