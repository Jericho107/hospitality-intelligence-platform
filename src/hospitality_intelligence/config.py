"""Runtime configuration for the hospitality analytical store."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseSettings:
    """PostgreSQL connection settings loaded from environment variables."""

    host: str = "localhost"
    port: int = 5432
    database: str = "hospitality_intelligence"
    user: str = "hospitality"
    password: str = "local_only"

    @property
    def dsn(self) -> str:
        """Return a Psycopg-compatible connection string."""

        return (
            f"host={self.host} port={self.port} dbname={self.database} "
            f"user={self.user} password={self.password}"
        )


def load_settings() -> DatabaseSettings:
    """Load database settings from HOSPITALITY_DB_* environment variables."""

    return DatabaseSettings(
        host=os.getenv("HOSPITALITY_DB_HOST", "localhost"),
        port=int(os.getenv("HOSPITALITY_DB_PORT", "5432")),
        database=os.getenv("HOSPITALITY_DB_NAME", "hospitality_intelligence"),
        user=os.getenv("HOSPITALITY_DB_USER", "hospitality"),
        password=os.getenv("HOSPITALITY_DB_PASSWORD", "local_only"),
    )
