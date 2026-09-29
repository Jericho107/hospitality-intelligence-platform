"""Generate deterministic PBIR visual containers from governed report contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from hospitality_intelligence.bi_contracts import (
    DEFAULT_REPORT_CONTRACT,
    REPORT_ROOT,
    extract_tmdl_measures,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LAYOUT = ROOT / "config" / "report_layout.yml"

TYPE_MAP = {
    "card": ("cardVisual", "Data"),
    "cards": ("multiRowCard", "Fields"),
    "line": ("lineChart", "Y"),
    "clustered_bar": ("clusteredBarChart", "Y"),
    "matrix": ("pivotTable", "Values"),
}


def _load_yaml(path: Path) -> dict[str, object]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected mapping at root")
    return payload


def _field(ref: str) -> dict[str, object]:
    table, column = ref.split(".", 1)
    return {
        "field": {
            "Column": {
                "Expression": {"SourceRef": {"Entity": table}},
                "Property": column,
            }
        },
        "queryRef": f"{table}.{column}",
        "nativeQueryRef": column,
        "active": True,
    }


def _measure(table: str, name: str) -> dict[str, object]:
    return {
        "field": {
            "Measure": {
                "Expression": {"SourceRef": {"Entity": table}},
                "Property": name,
            }
        },
        "queryRef": f"{table}.{name}",
        "nativeQueryRef": name,
    }


def _measure_table_lookup() -> dict[str, str]:
    tables = extract_tmdl_measures()
    result: dict[str, str] = {}
    for table, measures in tables.items():
        for measure in measures:
            if measure in result:
                raise ValueError(f"Measure name is ambiguous across tables: {measure}")
            result[measure] = table
    return result


def _build_visual(
    page_id: str,
    visual: dict[str, object],
    layout: dict[str, object],
    measure_tables: dict[str, str],
) -> dict[str, object]:
    visual_id = str(visual["id"])
    contract_type = str(visual["type"])
    measures = [str(value) for value in visual["measures"]]
    visual_type, measure_role = TYPE_MAP[contract_type]

    query_state: dict[str, object] = {
        measure_role: {
            "projections": [_measure(measure_tables[name], name) for name in measures]
        }
    }

    category = layout.get("category")
    if category:
        query_state["Category"] = {"projections": [_field(str(category))]}

    rows = layout.get("rows")
    if rows:
        query_state["Rows"] = {
            "projections": [_field(str(reference)) for reference in rows]
        }

    position = {
        "x": layout["x"],
        "y": layout["y"],
        "z": layout["z"],
        "height": layout["height"],
        "width": layout["width"],
        "tabOrder": layout["tab"],
    }

    return {
        "$schema": (
            "https://developer.microsoft.com/json-schemas/fabric/item/report/"
            "definition/visualContainer/2.0.0/schema.json"
        ),
        "name": visual_id,
        "position": position,
        "visual": {
            "visualType": visual_type,
            "query": {"queryState": query_state},
            "drillFilterOtherVisuals": True,
        },
        "annotations": [
            {"name": "contractVisualId", "value": visual_id},
            {"name": "contractPageId", "value": page_id},
        ],
    }


def generate(
    report_contract: Path = DEFAULT_REPORT_CONTRACT,
    layout_path: Path = DEFAULT_LAYOUT,
    output_root: Path = REPORT_ROOT,
) -> int:
    report = _load_yaml(report_contract)
    layout = _load_yaml(layout_path)
    measure_tables = _measure_table_lookup()

    pages = report.get("pages")
    layouts = layout.get("pages")
    if not isinstance(pages, list) or not isinstance(layouts, dict):
        raise ValueError("Report/layout pages are invalid")

    count = 0
    for page in pages:
        page_id = str(page["id"])
        page_layout = layouts.get(page_id)
        if not isinstance(page_layout, dict):
            raise ValueError(f"Missing layout for page: {page_id}")

        for visual in page["visuals"]:
            visual_id = str(visual["id"])
            visual_layout = page_layout.get(visual_id)
            if not isinstance(visual_layout, dict):
                raise ValueError(f"Missing layout for visual: {page_id}:{visual_id}")

            payload = _build_visual(page_id, visual, visual_layout, measure_tables)
            path = (
                output_root
                / "definition"
                / "pages"
                / page_id
                / "visuals"
                / visual_id
                / "visual.json"
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            count += 1

    return count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate PBIR visual containers.")
    parser.add_argument("--output-root", type=Path, default=REPORT_ROOT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    count = generate(output_root=args.output_root)
    print(f"Generated {count} PBIR visual containers.")


if __name__ == "__main__":
    main()
