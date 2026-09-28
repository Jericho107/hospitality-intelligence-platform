"""Controlled KPI corruption for reverse-testing the metric layer."""

from __future__ import annotations

import argparse

from hospitality_intelligence.db import execute_query

CASES = {
    "rooms_adr": """
        UPDATE analytics.kpi_rooms_daily
        SET adr = adr + 1
        WHERE (date_key, property_key) = (
            SELECT date_key, property_key
            FROM analytics.kpi_rooms_daily
            WHERE adr IS NOT NULL
            ORDER BY date_key, property_key
            LIMIT 1
        )
    """,
    "purchase_price_variance": """
        UPDATE analytics.kpi_purchasing_daily
        SET purchase_price_variance = purchase_price_variance + 10
        WHERE (date_key, property_key, product_key, supplier_key) = (
            SELECT date_key, property_key, product_key, supplier_key
            FROM analytics.kpi_purchasing_daily
            ORDER BY date_key, property_key, product_key, supplier_key
            LIMIT 1
        )
    """,
}


def inject(case: str) -> None:
    """Apply one controlled metric-layer mutation."""

    if case not in CASES:
        raise ValueError(f"Unknown case: {case}")
    execute_query(CASES[case])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inject a controlled KPI failure.")
    parser.add_argument("--case", choices=sorted(CASES), required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inject(args.case)
    print(f"Injected KPI failure: {args.case}")


if __name__ == "__main__":
    main()
