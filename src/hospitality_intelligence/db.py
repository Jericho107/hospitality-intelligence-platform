"""PostgreSQL helpers for the hospitality decision system."""

from __future__ import annotations

from pathlib import Path

import psycopg

from hospitality_intelligence.config import DatabaseSettings, load_settings


def connect(settings: DatabaseSettings | None = None) -> psycopg.Connection:
    """Open a PostgreSQL connection."""

    return psycopg.connect((settings or load_settings()).dsn)


def split_sql_statements(sql_text: str) -> list[str]:
    """Split repository SQL files into executable statements."""

    return [
        statement.strip()
        for statement in sql_text.split(";")
        if statement.strip()
    ]


def execute_sql_file(
    path: Path,
    settings: DatabaseSettings | None = None,
) -> None:
    """Execute a repository SQL file in one transaction."""

    statements = split_sql_statements(path.read_text(encoding="utf-8"))
    with connect(settings) as connection, connection.cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)


def execute_query(
    query: str,
    settings: DatabaseSettings | None = None,
) -> None:
    """Execute one SQL statement."""

    with connect(settings) as connection, connection.cursor() as cursor:
        cursor.execute(query)


def fetch_one(
    query: str,
    settings: DatabaseSettings | None = None,
) -> tuple[object, ...]:
    """Fetch exactly one SQL row."""

    with connect(settings) as connection, connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
        if row is None:
            raise ValueError("Query returned no rows")
        return tuple(row)
