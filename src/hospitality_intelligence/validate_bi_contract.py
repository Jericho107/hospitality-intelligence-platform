"""Validate the Executive BI contract against governed analytical metrics."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

from hospitality_intelligence.metric_contracts import load_metric_contracts

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEMANTIC = ROOT / "bi" / "semantic_model.yml"
DEFAULT_REPORT = ROOT / "bi" / "report_spec.yml"
DEFAULT_DAX = ROOT / "bi" / "dax" / "measures.dax"

DAX_TABLE_COLUMN = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\[([A-Za-z_][A-Za-z0-9_]*)\]")
FIELD_REFERENCE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)$")


def _load_yaml(path: Path) -> dict[str, object]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected mapping at root")
    return payload


def validate_bi_contract(
    semantic_path: Path = DEFAULT_SEMANTIC,
    report_path: Path = DEFAULT_REPORT,
    dax_path: Path = DEFAULT_DAX,
) -> list[str]:
    errors: list[str] = []
    semantic = _load_yaml(semantic_path)
    report = _load_yaml(report_path)
    dax = dax_path.read_text(encoding="utf-8")
    contracts = load_metric_contracts()

    contract_by_id = {metric.id: metric for metric in contracts.metrics}
    implemented = {metric.id for metric in contracts.metrics if metric.status == "implemented"}
    deferred = {metric.id for metric in contracts.metrics if metric.status == "deferred"}

    tables = semantic.get("tables", [])
    measures = semantic.get("measures", [])
    relationships = semantic.get("relationships", [])
    if not isinstance(tables, list) or not isinstance(measures, list):
        return ["semantic model tables/measures must be lists"]

    table_columns: dict[str, set[str]] = {}
    for table in tables:
        if not isinstance(table, dict):
            errors.append("table definition must be a mapping")
            continue
        name = table.get("name")
        columns = table.get("columns", [])
        if not isinstance(name, str) or not isinstance(columns, list):
            errors.append("table requires name and columns")
            continue
        if name in table_columns:
            errors.append(f"duplicate table: {name}")
        table_columns[name] = {str(column) for column in columns}

    measure_names: set[str] = set()
    measure_ids: set[str] = set()
    for measure in measures:
        if not isinstance(measure, dict):
            errors.append("measure definition must be a mapping")
            continue
        metric_id = str(measure.get("metric_id", ""))
        name = str(measure.get("name", ""))
        expression = str(measure.get("expression", ""))

        if metric_id not in implemented:
            errors.append(f"BI measure {metric_id!r} is not an implemented metric")
        if metric_id in deferred:
            errors.append(f"deferred metric leaked into BI layer: {metric_id}")
        if metric_id in measure_ids:
            errors.append(f"duplicate BI metric id: {metric_id}")
        if name in measure_names:
            errors.append(f"duplicate BI measure name: {name}")
        measure_ids.add(metric_id)
        measure_names.add(name)

        contract = contract_by_id.get(metric_id)
        if contract and contract.name != name:
            errors.append(
                f"{metric_id}: BI name {name!r} diverges from contract name {contract.name!r}"
            )

        for table_name, column_name in DAX_TABLE_COLUMN.findall(expression):
            if table_name not in table_columns:
                errors.append(f"{metric_id}: unknown DAX table {table_name}")
            elif column_name not in table_columns[table_name]:
                errors.append(f"{metric_id}: unknown DAX column {table_name}[{column_name}]")

        if f"[{name}]" not in dax:
            errors.append(f"{metric_id}: measure missing from canonical DAX file")

    missing = implemented - measure_ids
    if missing:
        errors.append(f"implemented metrics missing from BI contract: {sorted(missing)}")

    leaked = deferred & measure_ids
    if leaked:
        errors.append(f"deferred metrics present in BI contract: {sorted(leaked)}")

    for relation in relationships if isinstance(relationships, list) else []:
        if not isinstance(relation, dict):
            errors.append("relationship must be a mapping")
            continue
        for endpoint in ("from", "to"):
            value = str(relation.get(endpoint, ""))
            match = FIELD_REFERENCE.match(value)
            if not match:
                errors.append(f"invalid relationship endpoint: {value}")
                continue
            table_name, column_name = match.groups()
            if table_name not in table_columns or column_name not in table_columns[table_name]:
                errors.append(f"unknown relationship field: {value}")

    pages = report.get("pages", [])
    if not isinstance(pages, list) or len(pages) < 4:
        errors.append("report must define at least four decision pages")
        return errors

    seen_page_ids: set[str] = set()
    for page in pages:
        if not isinstance(page, dict):
            errors.append("page must be a mapping")
            continue
        page_id = str(page.get("id", ""))
        question = str(page.get("decision_question", ""))
        visuals = page.get("visuals", [])
        if page_id in seen_page_ids:
            errors.append(f"duplicate page id: {page_id}")
        seen_page_ids.add(page_id)
        if len(question) < 20:
            errors.append(f"{page_id}: missing substantive decision question")
        if not isinstance(visuals, list) or not visuals:
            errors.append(f"{page_id}: no visuals defined")
            continue

        for visual in visuals:
            if not isinstance(visual, dict):
                errors.append(f"{page_id}: visual must be a mapping")
                continue
            referenced_measures = []
            if "measure" in visual:
                referenced_measures.append(str(visual["measure"]))
            if isinstance(visual.get("measures"), list):
                referenced_measures.extend(str(item) for item in visual["measures"])
            unknown_measures = set(referenced_measures) - measure_names
            if unknown_measures:
                errors.append(f"{page_id}: unknown measures {sorted(unknown_measures)}")

            axis = visual.get("axis")
            if axis:
                match = FIELD_REFERENCE.match(str(axis))
                if not match:
                    errors.append(f"{page_id}: invalid axis reference {axis}")
                else:
                    table_name, column_name = match.groups()
                    if table_name not in table_columns or column_name not in table_columns[table_name]:
                        errors.append(f"{page_id}: unknown axis {axis}")

            rows = visual.get("rows", [])
            if isinstance(rows, list):
                for row in rows:
                    match = FIELD_REFERENCE.match(str(row))
                    if not match:
                        errors.append(f"{page_id}: invalid row field {row}")
                        continue
                    table_name, column_name = match.groups()
                    if table_name not in table_columns or column_name not in table_columns[table_name]:
                        errors.append(f"{page_id}: unknown row field {row}")

    required_exec = {"Occupancy %", "ADR", "RevPAR", "Net F&B Revenue", "Waste Cost", "Overtime Share"}
    executive = next((page for page in pages if page.get("id") == "executive_overview"), None)
    if not executive:
        errors.append("executive_overview page is required")
    else:
        used = set()
        for visual in executive.get("visuals", []):
            if "measure" in visual:
                used.add(str(visual["measure"]))
            if isinstance(visual.get("measures"), list):
                used.update(str(item) for item in visual["measures"])
        missing_exec = required_exec - used
        if missing_exec:
            errors.append(f"executive overview missing measures: {sorted(missing_exec)}")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Executive BI contracts.")
    parser.add_argument("--semantic", type=Path, default=DEFAULT_SEMANTIC)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--dax", type=Path, default=DEFAULT_DAX)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    errors = validate_bi_contract(args.semantic, args.report, args.dax)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print("Executive BI contract validation: PASS")


if __name__ == "__main__":
    main()
