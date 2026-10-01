from datetime import date, timedelta
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


def test_margin_leakage_scenario_changes_only_documented_operating_pressure(
    tmp_path: Path,
) -> None:
    leakage_dir = tmp_path / "leakage"
    healthy_dir = tmp_path / "healthy"
    leakage_config = GenerationConfig(
        days=45,
        seed=17,
        anchor_date=date(2026, 9, 1),
        scenario="margin_leakage",
    )
    healthy_config = GenerationConfig(
        days=45,
        seed=17,
        anchor_date=date(2026, 9, 1),
        scenario="healthy",
    )
    generate(leakage_config, leakage_dir)
    generate(healthy_config, healthy_dir)

    products = pd.read_csv(leakage_dir / "products.csv")
    beverage_ids = set(
        products.loc[
            (products["property_id"] == "P002")
            & (products["category"] == "beverage"),
            "product_id",
        ]
    )

    leakage_purchases = pd.read_csv(leakage_dir / "purchases_daily.csv")
    healthy_purchases = pd.read_csv(healthy_dir / "purchases_daily.csv")
    leakage_inventory = pd.read_csv(leakage_dir / "inventory_daily.csv")
    healthy_inventory = pd.read_csv(healthy_dir / "inventory_daily.csv")
    leakage_labour = pd.read_csv(leakage_dir / "labour_daily.csv")
    healthy_labour = pd.read_csv(healthy_dir / "labour_daily.csv")
    leakage_bookings = pd.read_csv(leakage_dir / "pms_bookings_daily.csv")
    healthy_bookings = pd.read_csv(healthy_dir / "pms_bookings_daily.csv")

    for frame in [
        leakage_purchases,
        healthy_purchases,
        leakage_inventory,
        healthy_inventory,
        leakage_labour,
        healthy_labour,
        leakage_bookings,
        healthy_bookings,
    ]:
        frame["date"] = pd.to_datetime(frame["date"])

    split = pd.Timestamp(leakage_config.anchor_date) + timedelta(
        days=leakage_config.days - 20
    )

    leakage_beverage = leakage_purchases[
        (leakage_purchases["property_id"] == "P002")
        & (leakage_purchases["product_id"].isin(beverage_ids))
        & (leakage_purchases["date"] >= split)
    ]
    healthy_beverage = healthy_purchases[
        (healthy_purchases["property_id"] == "P002")
        & (healthy_purchases["product_id"].isin(beverage_ids))
        & (healthy_purchases["date"] >= split)
    ]
    assert (
        leakage_beverage["unit_cost"].mean()
        > healthy_beverage["unit_cost"].mean() * 1.08
    )

    leakage_waste = leakage_inventory[
        (leakage_inventory["property_id"] == "P002")
        & (leakage_inventory["product_id"].isin(beverage_ids))
        & (leakage_inventory["date"] >= split)
        & (leakage_inventory["usage_qty"] > 0)
    ].copy()
    healthy_waste = healthy_inventory[
        (healthy_inventory["property_id"] == "P002")
        & (healthy_inventory["product_id"].isin(beverage_ids))
        & (healthy_inventory["date"] >= split)
        & (healthy_inventory["usage_qty"] > 0)
    ].copy()
    leakage_waste["waste_rate"] = (
        leakage_waste["waste_qty"] / leakage_waste["usage_qty"]
    )
    healthy_waste["waste_rate"] = (
        healthy_waste["waste_qty"] / healthy_waste["usage_qty"]
    )
    assert (
        leakage_waste["waste_rate"].mean()
        > healthy_waste["waste_rate"].mean() + 0.04
    )

    leakage_fnb = leakage_labour[
        (leakage_labour["property_id"] == "P002")
        & (leakage_labour["department_id"] == "D002")
        & (leakage_labour["date"] >= split)
    ]
    healthy_fnb = healthy_labour[
        (healthy_labour["property_id"] == "P002")
        & (healthy_labour["department_id"] == "D002")
        & (healthy_labour["date"] >= split)
    ]
    assert (
        leakage_fnb["actual_hours"].mean()
        > healthy_fnb["actual_hours"].mean() * 1.10
    )
    assert (
        leakage_fnb["overtime_hours"].mean()
        > healthy_fnb["overtime_hours"].mean()
    )

    leakage_rooms = leakage_bookings[
        (leakage_bookings["property_id"] == "P002")
        & (leakage_bookings["date"] >= split)
    ]["rooms_sold"].sum()
    healthy_rooms = healthy_bookings[
        (healthy_bookings["property_id"] == "P002")
        & (healthy_bookings["date"] >= split)
    ]["rooms_sold"].sum()
    assert leakage_rooms >= healthy_rooms
