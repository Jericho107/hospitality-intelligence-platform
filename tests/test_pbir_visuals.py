from pathlib import Path

import json
import yaml

from hospitality_intelligence.generate_pbir_visuals import generate


def test_pbir_visual_generation_is_complete_and_deterministic(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    report_root = tmp_path / "HospitalityExecutive.Report"

    count = generate(output_root=report_root)
    assert count == 20

    committed = root / "powerbi" / "HospitalityExecutive.Report"
    generated_files = sorted(report_root.glob("definition/pages/*/visuals/*/visual.json"))
    assert len(generated_files) == 20

    for generated in generated_files:
        relative = generated.relative_to(report_root)
        committed_file = committed / relative
        assert committed_file.exists(), relative
        assert json.loads(generated.read_text()) == json.loads(committed_file.read_text())


def test_all_visuals_fit_governed_canvas() -> None:
    root = Path(__file__).resolve().parents[1]
    for path in (root / "powerbi" / "HospitalityExecutive.Report").glob(
        "definition/pages/*/visuals/*/visual.json"
    ):
        payload = json.loads(path.read_text())
        pos = payload["position"]
        assert pos["x"] >= 0 and pos["y"] >= 0
        assert pos["x"] + pos["width"] <= 1280
        assert pos["y"] + pos["height"] <= 720


def test_layout_covers_every_report_visual() -> None:
    root = Path(__file__).resolve().parents[1]
    report = yaml.safe_load((root / "config" / "report_contract.yml").read_text())
    layout = yaml.safe_load((root / "config" / "report_layout.yml").read_text())

    contract_ids = {
        (page["id"], visual["id"])
        for page in report["pages"]
        for visual in page["visuals"]
    }
    layout_ids = {
        (page_id, visual_id)
        for page_id, visuals in layout["pages"].items()
        for visual_id in visuals
    }

    assert contract_ids == layout_ids
