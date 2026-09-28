"""Build the governed KPI marts from validated analytical facts."""

from __future__ import annotations

from pathlib import Path

from hospitality_intelligence.config import DatabaseSettings
from hospitality_intelligence.db import execute_sql_file

ROOT = Path(__file__).resolve().parents[2]
SQL_PATH = ROOT / "sql" / "30_kpi_marts.sql"


def build_metrics(settings: DatabaseSettings | None = None) -> None:
    """Create and refresh all implemented KPI marts."""

    execute_sql_file(SQL_PATH, settings=settings)


def main() -> None:
    build_metrics()
    print("Governed KPI marts built.")


if __name__ == "__main__":
    main()
