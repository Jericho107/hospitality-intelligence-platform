"""Build the typed dimensional analytical store from the raw landing layer."""

from __future__ import annotations

from pathlib import Path

from hospitality_intelligence.config import DatabaseSettings
from hospitality_intelligence.db import execute_sql_file

ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = ROOT / "sql"


def build_analytics_store(
    settings: DatabaseSettings | None = None,
) -> None:
    """Create dimensional tables and rebuild them from raw sources."""

    execute_sql_file(
        SQL_DIR / "10_dimensional_schema.sql",
        settings=settings,
    )
    execute_sql_file(
        SQL_DIR / "20_transform.sql",
        settings=settings,
    )


def main() -> None:
    build_analytics_store()
    print("Rebuilt analytics dimensional store.")


if __name__ == "__main__":
    main()
