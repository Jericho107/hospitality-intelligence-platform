"""Validate Power BI semantic-model and report decision contracts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
POWERBI_ROOT = ROOT / "powerbi"
SEMANTIC_ROOT = POWERBI_ROOT / "HospitalityExecutive.SemanticModel"
REPORT_ROOT = POWERBI_ROOT / "HospitalityExecutive.Report"
DEFAULT_REPORT_CONTRACT = ROOT / "config" / "report_contract.yml"
BI_MEASURE_CONTRACT = ROOT / "config" / "bi_measure_contracts.yml"
METRIC_CONTRACT = ROOT / "config" / "metric_contracts.yml"

MEASURE_RE = re.compile(
    r"^\s*measure\s+(?:'([^']+)'|([A-Za-z][A-Za-z0-9 _%&]*?))\s*=\s*(.+)$",
    re.MULTILINE,
)
TABLE_RE = re.compile(r"^table\s+(?:'([^']+)'|([^\n]+))$", re.MULTILINE)

RATIO_MEASURES = {
    "Occupancy %",
    "ADR",
    "RevPAR",
    "Average Check",
    "Discount Rate",
    "Waste %",
    "Labour Cost per Hour",
    "Overtime Share",
}
MATERIALIZED_RATIO_COLUMNS = {
    "occupancy_pct",
    "adr",
    "revpar",
    "average_check",
    "discount_rate",
    "waste_pct",
    "labour_cost_per_hour",
    "overtime_share",
}


class VisualContract(BaseModel):
    id: str = Field(min_length=1)
    type: str = Field(min_length=1)
    measures: list[str] = Field(min_length=1)


class PageContract(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    question: str = Field(min_length=10)
    visuals: list[VisualContract] = Field(min_length=1)


class ReportContract(BaseModel):
    status: str
    audience: list[str] = Field(min_length=1)
    global_slicers: list[str] = Field(min_length=1)
    pages: list[PageContract] = Field(min_length=1)
    forbidden_measures: list[str] = Field(min_length=1)


class BIMeasureMap(BaseModel):
    metric_id: str
    dax_measure: str
    table: str


class BIMeasureContract(BaseModel):
    measures: list[BIMeasureMap] = Field(min_length=1)


def _yaml(path: Path) -> dict[str, object]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected mapping at root")
    return payload


def _json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected object at root")
    return payload


def extract_tmdl_measures() -> dict[str, dict[str, str]]:
    """Return table -> measure -> single-line DAX expression."""

    tables: dict[str, dict[str, str]] = {}
    table_dir = SEMANTIC_ROOT / "definition" / "tables"
    for path in sorted(table_dir.glob("*.tmdl")):
        text = path.read_text(encoding="utf-8")
        table_match = TABLE_RE.search(text)
        if table_match is None:
            raise ValueError(f"{path}: table declaration not found")
        table_name = (table_match.group(1) or table_match.group(2)).strip()
        measures: dict[str, str] = {}
        for match in MEASURE_RE.finditer(text):
            measure_name = (match.group(1) or match.group(2)).strip()
            measures[measure_name] = match.group(3).strip()
        tables[table_name] = measures
    return tables


def _flat_measures(tables: dict[str, dict[str, str]]) -> set[str]:
    return {measure for measures in tables.values() for measure in measures}


def _implemented_metric_ids() -> set[str]:
    payload = _yaml(METRIC_CONTRACT)
    rows = payload.get("metrics")
    if not isinstance(rows, list):
        raise ValueError("metric_contracts.yml: metrics must be a list")
    return {
        str(row["id"])
        for row in rows
        if isinstance(row, dict) and row.get("status") == "implemented"
    }


def _validate_measure_contracts(tables: dict[str, dict[str, str]]) -> None:
    mapping = BIMeasureContract.model_validate(_yaml(BI_MEASURE_CONTRACT))
    implemented = _implemented_metric_ids()
    seen_ids: set[str] = set()
    seen_dax: set[str] = set()

    for row in mapping.measures:
        if row.metric_id not in implemented:
            raise ValueError(f"BI mapping references non-implemented metric: {row.metric_id}")
        if row.metric_id in seen_ids:
            raise ValueError(f"Duplicate BI metric mapping: {row.metric_id}")
        if row.dax_measure in seen_dax:
            raise ValueError(f"Duplicate BI DAX mapping: {row.dax_measure}")
        if row.table not in tables:
            raise ValueError(f"Unknown BI table in mapping: {row.table}")
        if row.dax_measure not in tables[row.table]:
            raise ValueError(
                f"{row.metric_id}: DAX measure {row.dax_measure!r} not found in {row.table}"
            )
        seen_ids.add(row.metric_id)
        seen_dax.add(row.dax_measure)

    if seen_ids != implemented:
        missing = sorted(implemented - seen_ids)
        extra = sorted(seen_ids - implemented)
        raise ValueError(f"BI mapping coverage mismatch. missing={missing} extra={extra}")


def _validate_ratio_logic(tables: dict[str, dict[str, str]]) -> None:
    flat = {name: expr for measures in tables.values() for name, expr in measures.items()}
    for measure in RATIO_MEASURES:
        expression = flat.get(measure)
        if expression is None:
            raise ValueError(f"Required ratio measure missing: {measure}")
        if "DIVIDE(" not in expression.upper():
            raise ValueError(f"{measure}: ratio must use DIVIDE")

    for path in (SEMANTIC_ROOT / "definition" / "tables").glob("*.tmdl"):
        text = path.read_text(encoding="utf-8").lower()
        for column in MATERIALIZED_RATIO_COLUMNS:
            pattern = rf"sum\s*\([^\)]*\[{re.escape(column)}\]"
            if re.search(pattern, text):
                raise ValueError(
                    f"{path.name}: materialized ratio column {column} must not be SUM-aggregated"
                )


def _validate_powerbi_structure(contract: ReportContract) -> None:
    pbism = _json(SEMANTIC_ROOT / "definition.pbism")
    if float(str(pbism.get("version", "0"))) < 4:
        raise ValueError("definition.pbism must use TMDL-capable version >= 4")

    pbir = _json(REPORT_ROOT / "definition.pbir")
    if float(str(pbir.get("version", "0"))) < 4:
        raise ValueError("definition.pbir must use PBIR-capable version >= 4")
    dataset_path = (
        pbir.get("datasetReference", {})
        .get("byPath", {})
        .get("path")
    )
    if dataset_path != "../HospitalityExecutive.SemanticModel":
        raise ValueError(f"Unexpected semantic-model path: {dataset_path!r}")

    report = _json(REPORT_ROOT / "definition" / "report.json")
    if "themeCollection" not in report:
        raise ValueError("PBIR report.json must contain themeCollection")

    version = _json(REPORT_ROOT / "definition" / "version.json")
    if version.get("version") != "2.1.0":
        raise ValueError("PBIR definition version must be pinned to 2.1.0")

    pages_meta = _json(REPORT_ROOT / "definition" / "pages" / "pages.json")
    page_order = pages_meta.get("pageOrder")
    expected = [page.id for page in contract.pages]
    if page_order != expected:
        raise ValueError(f"PBIR page order does not match contract: {page_order} != {expected}")

    for page in contract.pages:
        path = REPORT_ROOT / "definition" / "pages" / page.id / "page.json"
        payload = _json(path)
        if payload.get("name") != page.id:
            raise ValueError(f"{page.id}: PBIR page name mismatch")
        if payload.get("displayName") != page.title:
            raise ValueError(f"{page.id}: PBIR page title mismatch")
        if payload.get("width") != 1280 or payload.get("height") != 720:
            raise ValueError(f"{page.id}: page must use governed 1280x720 canvas")




def _visual_measure_names(payload: dict[str, object]) -> set[str]:
    visual = payload.get("visual")
    if not isinstance(visual, dict):
        return set()
    query = visual.get("query")
    if not isinstance(query, dict):
        return set()
    state = query.get("queryState")
    if not isinstance(state, dict):
        return set()

    names: set[str] = set()
    for role in state.values():
        if not isinstance(role, dict):
            continue
        projections = role.get("projections", [])
        if not isinstance(projections, list):
            continue
        for projection in projections:
            if not isinstance(projection, dict):
                continue
            field = projection.get("field")
            if not isinstance(field, dict):
                continue
            measure = field.get("Measure")
            if isinstance(measure, dict) and isinstance(measure.get("Property"), str):
                names.add(measure["Property"])
    return names


def _validate_visual_containers(
    contract: ReportContract,
    tables: dict[str, dict[str, str]],
) -> None:
    all_measures = _flat_measures(tables)
    expected_paths: set[Path] = set()

    for page in contract.pages:
        seen_tabs: set[int] = set()
        for visual in page.visuals:
            path = (
                REPORT_ROOT
                / "definition"
                / "pages"
                / page.id
                / "visuals"
                / visual.id
                / "visual.json"
            )
            expected_paths.add(path)
            if not path.exists():
                raise ValueError(f"Missing PBIR visual container: {page.id}:{visual.id}")

            payload = _json(path)
            if payload.get("name") != visual.id:
                raise ValueError(f"{page.id}:{visual.id}: PBIR visual name mismatch")

            position = payload.get("position")
            if not isinstance(position, dict):
                raise ValueError(f"{page.id}:{visual.id}: missing visual position")
            x = float(position.get("x", -1))
            y = float(position.get("y", -1))
            width = float(position.get("width", -1))
            height = float(position.get("height", -1))
            if x < 0 or y < 0 or width <= 0 or height <= 0:
                raise ValueError(f"{page.id}:{visual.id}: invalid visual geometry")
            if x + width > 1280 or y + height > 720:
                raise ValueError(f"{page.id}:{visual.id}: visual exceeds governed canvas")
            tab = int(position.get("tabOrder", -1))
            if tab < 0 or tab in seen_tabs:
                raise ValueError(f"{page.id}:{visual.id}: invalid/duplicate tab order")
            seen_tabs.add(tab)

            bound = _visual_measure_names(payload)
            expected = set(visual.measures)
            if bound != expected:
                raise ValueError(
                    f"{page.id}:{visual.id}: PBIR measure binding mismatch "
                    f"{sorted(bound)} != {sorted(expected)}"
                )
            unknown = bound - all_measures
            if unknown:
                raise ValueError(
                    f"{page.id}:{visual.id}: PBIR references unknown measures {sorted(unknown)}"
                )

            annotations = payload.get("annotations", [])
            if not isinstance(annotations, list):
                raise ValueError(f"{page.id}:{visual.id}: annotations must be a list")
            annotation_map = {
                str(row.get("name")): str(row.get("value"))
                for row in annotations
                if isinstance(row, dict)
            }
            if annotation_map.get("contractVisualId") != visual.id:
                raise ValueError(f"{page.id}:{visual.id}: missing contractVisualId annotation")
            if annotation_map.get("contractPageId") != page.id:
                raise ValueError(f"{page.id}:{visual.id}: missing contractPageId annotation")

    committed = set(
        REPORT_ROOT.glob("definition/pages/*/visuals/*/visual.json")
    )
    extras = committed - expected_paths
    missing = expected_paths - committed
    if extras or missing:
        raise ValueError(
            "PBIR visual file coverage mismatch. "
            f"missing={[str(p) for p in sorted(missing)]} "
            f"extra={[str(p) for p in sorted(extras)]}"
        )

def validate_bi_assets(contract_path: Path = DEFAULT_REPORT_CONTRACT) -> tuple[int, int]:
    """Validate semantic model, governed measures and report decision contract."""

    tables = extract_tmdl_measures()
    all_measures = _flat_measures(tables)
    contract = ReportContract.model_validate(_yaml(contract_path))

    if contract.status != "visuals_materialized_runtime_pending":
        raise ValueError(
            "Report status must remain explicit until Power BI Desktop runtime validation is proven"
        )

    _validate_measure_contracts(tables)
    _validate_ratio_logic(tables)
    _validate_powerbi_structure(contract)

    page_ids = [page.id for page in contract.pages]
    if len(page_ids) != len(set(page_ids)):
        raise ValueError("Report page IDs must be unique")

    forbidden = set(contract.forbidden_measures)
    if forbidden & all_measures:
        raise ValueError(
            f"Deferred/forbidden measures exist in TMDL: {sorted(forbidden & all_measures)}"
        )

    visual_ids: set[str] = set()
    for page in contract.pages:
        for visual in page.visuals:
            key = f"{page.id}:{visual.id}"
            if key in visual_ids:
                raise ValueError(f"Duplicate visual contract ID: {key}")
            visual_ids.add(key)
            for measure in visual.measures:
                if measure in forbidden:
                    raise ValueError(f"{key}: forbidden measure referenced: {measure}")
                if measure not in all_measures:
                    raise ValueError(f"{key}: unknown semantic-model measure: {measure}")

    _validate_visual_containers(contract, tables)

    return len(all_measures), len(visual_ids)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Power BI contracts.")
    parser.add_argument("--contract", type=Path, default=DEFAULT_REPORT_CONTRACT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    measures, visuals = validate_bi_assets(args.contract)
    print(f"Validated {measures} DAX measures and {visuals} governed visual contracts.")
    print("Power BI Desktop runtime validation: NOT PROVEN.")


if __name__ == "__main__":
    main()
