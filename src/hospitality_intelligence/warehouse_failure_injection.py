"""Controlled PostgreSQL mutations for reverse-testing the warehouse boundary."""

from __future__ import annotations

import argparse

from hospitality_intelligence.db import execute_query


def mutate_raw_pos_revenue() -> None:
    """Change one raw target value without touching the source CSV."""

    execute_query(
        """
        UPDATE raw.pos_product_mix_daily
        SET net_revenue = ((net_revenue::numeric + 10)::numeric(14,2))::text
        WHERE ctid = (
            SELECT ctid
            FROM raw.pos_product_mix_daily
            ORDER BY date, property_id, outlet_id, product_id
            LIMIT 1
        )
        """
    )


def mutate_fact_labour_cost() -> None:
    """Change one analytical fact without changing raw or source state."""

    execute_query(
        """
        UPDATE analytics.fact_labour_daily
        SET labour_cost = labour_cost + 10
        WHERE ctid = (
            SELECT ctid
            FROM analytics.fact_labour_daily
            ORDER BY date_key, property_key, department_key
            LIMIT 1
        )
        """
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inject a controlled PostgreSQL reconciliation failure."
    )
    parser.add_argument(
        "--case",
        choices=["raw_pos_revenue", "fact_labour_cost"],
        required=True,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.case == "raw_pos_revenue":
        mutate_raw_pos_revenue()
        print("Injected raw POS revenue mutation.")
    elif args.case == "fact_labour_cost":
        mutate_fact_labour_cost()
        print("Injected analytical labour-cost mutation.")


if __name__ == "__main__":
    main()
