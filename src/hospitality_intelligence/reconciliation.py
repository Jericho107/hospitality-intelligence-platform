"""Exact source-to-raw reconciliation for hospitality landing data."""

from __future__ import annotations

import argparse
import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

from psycopg import sql

from hospitality_intelligence.config import DatabaseSettings, load_settings
from hospitality_intelligence.db import connect


@dataclass(frozen=True)
class DatasetSpec:
    filename: str
    table: str
    columns: tuple[str, ...]
    keys: tuple[str, ...]


@dataclass(frozen=True)
class ReconciliationResult:
    dataset: str
    source_count: int
    target_count: int
    source_hash: str
    target_hash: str
    status: str


DATASETS = (
    DatasetSpec("properties.csv", "properties",
        ("property_id","property_name","archetype","rooms_count","city"),
        ("property_id",)),
    DatasetSpec("outlets.csv", "outlets",
        ("outlet_id","property_id","outlet_name","outlet_type"),
        ("outlet_id",)),
    DatasetSpec("products.csv", "products",
        ("product_id","outlet_id","property_id","product_name","category",
         "menu_price","standard_unit_cost","inventory_usage_per_unit"),
        ("product_id",)),
    DatasetSpec("suppliers.csv", "suppliers",
        ("supplier_id","supplier_name","category"), ("supplier_id",)),
    DatasetSpec("departments.csv", "departments",
        ("department_id","department_name"), ("department_id",)),
    DatasetSpec("pms_inventory_daily.csv", "pms_inventory_daily",
        ("date","property_id","rooms_available"), ("date","property_id")),
    DatasetSpec("pms_bookings_daily.csv", "pms_bookings_daily",
        ("date","property_id","segment","channel","rooms_sold","room_revenue"),
        ("date","property_id","segment","channel")),
    DatasetSpec("pos_checks_daily.csv", "pos_checks_daily",
        ("date","property_id","outlet_id","covers","gross_revenue",
         "discount_amount","net_revenue"),
        ("date","property_id","outlet_id")),
    DatasetSpec("pos_product_mix_daily.csv", "pos_product_mix_daily",
        ("date","property_id","outlet_id","product_id","units_sold","net_revenue"),
        ("date","property_id","outlet_id","product_id")),
    DatasetSpec("purchases_daily.csv", "purchases_daily",
        ("date","property_id","product_id","supplier_id","quantity",
         "unit_cost","purchase_cost"),
        ("date","property_id","product_id","supplier_id")),
    DatasetSpec("inventory_daily.csv", "inventory_daily",
        ("date","property_id","product_id","opening_qty","receipts_qty",
         "usage_qty","waste_qty","closing_qty","weighted_unit_cost",
         "inventory_value"),
        ("date","property_id","product_id")),
    DatasetSpec("labour_daily.csv", "labour_daily",
        ("date","property_id","department_id","scheduled_hours","actual_hours",
         "overtime_hours","labour_cost"),
        ("date","property_id","department_id")),
    DatasetSpec("budget_monthly.csv", "budget_monthly",
        ("month","property_id","department_id","budget_revenue","budget_cost"),
        ("month","property_id","department_id")),
)


def canonical_hash(rows: list[tuple[str, ...]]) -> str:
    """Hash an ordered sequence of string rows."""

    payload = "\n".join("\x1f".join(row) for row in rows).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _source_rows(data_dir: Path, spec: DatasetSpec) -> list[tuple[str, ...]]:
    with (data_dir / spec.filename).open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        rows = [
            tuple(str(row[column]) for column in spec.columns)
            for row in reader
        ]

    key_indexes = [spec.columns.index(key) for key in spec.keys]
    rows.sort(key=lambda row: tuple(row[index] for index in key_indexes))
    return rows


def _target_rows(
    spec: DatasetSpec,
    settings: DatabaseSettings,
) -> list[tuple[str, ...]]:
    query = sql.SQL("SELECT {} FROM {}.{} ORDER BY {}").format(
        sql.SQL(", ").join(sql.Identifier(column) for column in spec.columns),
        sql.Identifier("raw"),
        sql.Identifier(spec.table),
        sql.SQL(", ").join(sql.Identifier(key) for key in spec.keys),
    )
    with connect(settings) as connection, connection.cursor() as cursor:
        cursor.execute(query)
        return [
            tuple("" if value is None else str(value) for value in row)
            for row in cursor.fetchall()
        ]


def reconcile_dataset(
    data_dir: Path,
    spec: DatasetSpec,
    settings: DatabaseSettings,
) -> ReconciliationResult:
    """Compare one CSV source with its raw PostgreSQL landing table."""

    source = _source_rows(data_dir, spec)
    target = _target_rows(spec, settings)
    source_hash = canonical_hash(source)
    target_hash = canonical_hash(target)
    passed = len(source) == len(target) and source_hash == target_hash

    return ReconciliationResult(
        dataset=spec.filename,
        source_count=len(source),
        target_count=len(target),
        source_hash=source_hash,
        target_hash=target_hash,
        status="PASS" if passed else "FAIL",
    )


def run_reconciliation(
    data_dir: Path,
    settings: DatabaseSettings | None = None,
) -> list[ReconciliationResult]:
    """Reconcile all source files against the raw landing schema."""

    runtime = settings or load_settings()
    return [
        reconcile_dataset(data_dir, spec, runtime)
        for spec in DATASETS
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reconcile CSV sources against PostgreSQL raw landing tables."
    )
    parser.add_argument("--data-dir", default="data/sample")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = run_reconciliation(Path(args.data_dir))
    for result in results:
        print(
            f"{result.dataset}: {result.status} "
            f"source={result.source_count} target={result.target_count}"
        )
    if any(result.status != "PASS" for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
