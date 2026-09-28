from pathlib import Path

from hospitality_intelligence.diagnostics import (
    DriverResult,
    adverse_drivers,
    compare_scenarios,
)
from hospitality_intelligence.generate_synthetic_data import GenerationConfig, generate


def _generate_pair(tmp_path: Path) -> tuple[Path, Path]:
    healthy = tmp_path / "healthy"
    leakage = tmp_path / "leakage"
    common = dict(days=60, seed=42)

    generate(GenerationConfig(**common, scenario="healthy"), healthy)
    generate(GenerationConfig(**common, scenario="margin_leakage"), leakage)
    return healthy, leakage


def test_diagnostic_benchmark_recovers_injected_cost_drivers(tmp_path: Path) -> None:
    healthy, leakage = _generate_pair(tmp_path)
    results = compare_scenarios(healthy, leakage)
    detected = {result.driver for result in adverse_drivers(results)}

    assert {
        "beverage_purchase_cost_pressure",
        "beverage_waste_pressure",
        "fnb_overtime_pressure",
    }.issubset(detected)


def test_identical_scenario_produces_no_adverse_driver(tmp_path: Path) -> None:
    healthy, _ = _generate_pair(tmp_path)
    results = compare_scenarios(healthy, healthy)

    assert adverse_drivers(results) == []


def test_adverse_drivers_rank_largest_relative_change_first() -> None:
    results = [
        DriverResult("a", 100, 120, 20, 0.20, True, "test"),
        DriverResult("b", 100, 160, 60, 0.60, True, "test"),
        DriverResult("c", 100, 110, 10, 0.10, False, "test"),
    ]

    assert [result.driver for result in adverse_drivers(results)] == ["b", "a"]
