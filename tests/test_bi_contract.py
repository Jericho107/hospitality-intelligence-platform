from pathlib import Path

import yaml

from hospitality_intelligence.validate_bi_contract import validate_bi_contract


def test_repository_bi_contract_is_valid() -> None:
    assert validate_bi_contract() == []


def test_deferred_metric_is_rejected(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    semantic = yaml.safe_load((root / "bi" / "semantic_model.yml").read_text(encoding="utf-8"))
    semantic["measures"].append(
        {
            "metric_id": "labour_cost_pct",
            "name": "Labour Cost %",
            "expression": "DIVIDE(SUM(kpi_labour_daily[labour_cost]), 1)",
            "format": "0.0%",
        }
    )

    semantic_path = tmp_path / "semantic.yml"
    semantic_path.write_text(yaml.safe_dump(semantic, sort_keys=False), encoding="utf-8")

    errors = validate_bi_contract(
        semantic_path,
        root / "bi" / "report_spec.yml",
        root / "bi" / "dax" / "measures.dax",
    )

    assert any("deferred" in error or "not an implemented metric" in error for error in errors)


def test_unknown_visual_measure_is_rejected(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    report = yaml.safe_load((root / "bi" / "report_spec.yml").read_text(encoding="utf-8"))
    report["pages"][0]["visuals"].append({"type": "kpi", "measure": "Imaginary KPI"})

    report_path = tmp_path / "report.yml"
    report_path.write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")

    errors = validate_bi_contract(
        root / "bi" / "semantic_model.yml",
        report_path,
        root / "bi" / "dax" / "measures.dax",
    )

    assert any("Imaginary KPI" in error for error in errors)
