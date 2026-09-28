"""Load validated CSV sources into the PostgreSQL raw landing schema."""

from __future__ import annotations

import argparse
from pathlib import Path

from hospitality_intelligence.config import DatabaseSettings, load_settings
from hospitality_intelligence.contracts import load_and_validate_sources
from hospitality_intelligence.db import connect, execute_sql_file

ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = ROOT / "sql"

RAW_TABLES = {
    "properties.csv": "properties",
    "outlets.csv": "outlets",
    "products.csv": "products",
    "suppliers.csv": "suppliers",
    "departments.csv": "departments",
    "pms_inventory_daily.csv": "pms_inventory_daily",
    "pms_bookings_daily.csv": "pms_bookings_daily",
    "pos_checks_daily.csv": "pos_checks_daily",
    "pos_product_mix_daily.csv": "pos_product_mix_daily",
    "purchases_daily.csv": "purchases_daily",
    "inventory_daily.csv": "inventory_daily",
    "labour_daily.csv": "labour_daily",
    "budget_monthly.csv": "budget_monthly",
}


def create_raw_schema(settings: DatabaseSettings | None = None) -> None:
    """Create raw and analytics schemas."""

    execute_sql_file(SQL_DIR / "00_raw_schema.sql", settings=settings)


def _truncate_raw(settings: DatabaseSettings | None = None) -> None:
    tables = ", ".join(f"raw.{table}" for table in RAW_TABLES.values())
    with connect(settings) as connection, connection.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE {tables}")


def _copy_csv(
    table_name: str,
    csv_path: Path,
    settings: DatabaseSettings | None = None,
) -> int:
    """COPY one already-validated CSV file into a raw TEXT table."""

    with csv_path.open("r", encoding="utf-8") as handle:
        row_count = sum(1 for _ in handle) - 1

    with (
        connect(settings) as connection,
        connection.cursor() as cursor,
        csv_path.open("r", encoding="utf-8") as handle,
        cursor.copy(
            f"COPY raw.{table_name} FROM STDIN WITH CSV HEADER"
        ) as copy,
    ):
        for line in handle:
            copy.write(line)

    return row_count


def ingest_all(
    data_dir: Path,
    settings: DatabaseSettings | None = None,
) -> dict[str, int]:
    """Validate source files, reset raw state, and load every dataset."""

    runtime = settings or load_settings()
    load_and_validate_sources(data_dir)
    create_raw_schema(runtime)
    _truncate_raw(runtime)

    return {
        filename: _copy_csv(table, data_dir / filename, runtime)
        for filename, table in RAW_TABLES.items()
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load hospitality source files into PostgreSQL raw schema."
    )
    parser.add_argument("--data-dir", default="data/sample")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    loaded = ingest_all(Path(args.data_dir))
    for filename, row_count in loaded.items():
        print(f"{filename}: loaded={row_count}")


if __name__ == "__main__":
    main()
