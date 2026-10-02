from __future__ import annotations

from pathlib import Path

from hospitality_intelligence.generate_synthetic_data import GenerationConfig, generate


def _files(directory: Path) -> dict[str, bytes]:
    return {
        path.name: path.read_bytes()
        for path in sorted(directory.glob("*.csv"))
    }


def test_same_seed_anchor_and_scenario_are_byte_reproducible(tmp_path: Path) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    config = GenerationConfig(days=60, seed=107, scenario="margin_leakage")

    generate(config, left)
    generate(config, right)

    assert _files(left)
    assert _files(left) == _files(right)


def test_different_seed_changes_operating_sources(tmp_path: Path) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"

    generate(GenerationConfig(days=60, seed=42, scenario="healthy"), left)
    generate(GenerationConfig(days=60, seed=107, scenario="healthy"), right)

    assert (left / "pms_bookings_daily.csv").read_bytes() != (
        right / "pms_bookings_daily.csv"
    ).read_bytes()


def test_scenario_switch_preserves_master_data_but_changes_controlled_operations(
    tmp_path: Path,
) -> None:
    healthy = tmp_path / "healthy"
    leakage = tmp_path / "leakage"
    common = dict(days=60, seed=42)

    generate(GenerationConfig(**common, scenario="healthy"), healthy)
    generate(GenerationConfig(**common, scenario="margin_leakage"), leakage)

    for filename in {
        "properties.csv",
        "outlets.csv",
        "products.csv",
        "suppliers.csv",
        "departments.csv",
    }:
        assert (healthy / filename).read_bytes() == (leakage / filename).read_bytes()

    assert (healthy / "purchases_daily.csv").read_bytes() != (
        leakage / "purchases_daily.csv"
    ).read_bytes()
    assert (healthy / "labour_daily.csv").read_bytes() != (
        leakage / "labour_daily.csv"
    ).read_bytes()
