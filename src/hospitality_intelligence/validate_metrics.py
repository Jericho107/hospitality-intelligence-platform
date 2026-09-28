"""Independent validation of materialized hospitality KPI marts."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from hospitality_intelligence.config import DatabaseSettings, load_settings
from hospitality_intelligence.db import fetch_one

METRIC_TOLERANCE = Decimal("0.00001")


@dataclass(frozen=True)
class MetricControl:
    """A discrepancy query that must return zero mismatches."""

    name: str
    query: str


@dataclass(frozen=True)
class MetricValidationResult:
    """Observed mismatch count for one KPI contract."""

    name: str
    mismatch_count: int

    @property
    def passed(self) -> bool:
        return self.mismatch_count == 0


CONTROLS = (
    MetricControl(
        "rooms_kpi_reconciliation",
        """
        WITH expected AS (
            SELECT
                i.date_key,
                i.property_key,
                i.rooms_available,
                COALESCE(SUM(b.rooms_sold), 0)::integer AS rooms_sold,
                COALESCE(SUM(b.room_revenue), 0)::numeric(16,2) AS room_revenue,
                (COALESCE(SUM(b.rooms_sold), 0)::numeric / i.rooms_available)
                    ::numeric(12,8) AS occupancy_pct,
                CASE
                    WHEN COALESCE(SUM(b.rooms_sold), 0) = 0 THEN NULL
                    ELSE (COALESCE(SUM(b.room_revenue), 0)::numeric / SUM(b.rooms_sold))
                        ::numeric(16,6)
                END AS adr,
                (COALESCE(SUM(b.room_revenue), 0)::numeric / i.rooms_available)
                    ::numeric(16,6) AS revpar
            FROM analytics.fact_room_inventory_daily i
            LEFT JOIN analytics.fact_room_bookings_daily b
                ON b.date_key = i.date_key
               AND b.property_key = i.property_key
            GROUP BY i.date_key, i.property_key, i.rooms_available
        ),
        diff AS (
            (SELECT * FROM expected EXCEPT SELECT * FROM analytics.kpi_rooms_daily)
            UNION ALL
            (SELECT * FROM analytics.kpi_rooms_daily EXCEPT SELECT * FROM expected)
        )
        SELECT COUNT(*) FROM diff
        """,
    ),
    MetricControl(
        "fnb_kpi_reconciliation",
        """
        WITH expected AS (
            SELECT
                date_key,
                property_key,
                outlet_key,
                covers,
                gross_revenue::numeric(16,2),
                discount_amount::numeric(16,2),
                net_revenue::numeric(16,2),
                CASE WHEN covers = 0 THEN NULL
                    ELSE (net_revenue / covers::numeric)::numeric(16,6) END,
                CASE WHEN gross_revenue = 0 THEN NULL
                    ELSE (discount_amount / gross_revenue)::numeric(12,8) END
            FROM analytics.fact_pos_outlet_daily
        ),
        diff AS (
            (SELECT * FROM expected EXCEPT SELECT * FROM analytics.kpi_fnb_outlet_daily)
            UNION ALL
            (SELECT * FROM analytics.kpi_fnb_outlet_daily EXCEPT SELECT * FROM expected)
        )
        SELECT COUNT(*) FROM diff
        """,
    ),
    MetricControl(
        "purchasing_kpi_reconciliation",
        """
        WITH expected AS (
            SELECT
                f.date_key,
                f.property_key,
                f.product_key,
                f.supplier_key,
                f.quantity::numeric(16,2),
                f.purchase_cost::numeric(16,2),
                (f.quantity * p.standard_unit_cost)::numeric(16,4),
                (f.purchase_cost - (f.quantity * p.standard_unit_cost))::numeric(16,4)
            FROM analytics.fact_purchases_daily f
            JOIN analytics.dim_product p ON p.product_key = f.product_key
        ),
        diff AS (
            (SELECT * FROM expected EXCEPT SELECT * FROM analytics.kpi_purchasing_daily)
            UNION ALL
            (SELECT * FROM analytics.kpi_purchasing_daily EXCEPT SELECT * FROM expected)
        )
        SELECT COUNT(*) FROM diff
        """,
    ),
    MetricControl(
        "inventory_kpi_reconciliation",
        """
        WITH expected AS (
            SELECT
                date_key,
                property_key,
                product_key,
                usage_qty::numeric(16,2),
                waste_qty::numeric(16,2),
                weighted_unit_cost::numeric(16,2),
                (usage_qty * weighted_unit_cost)::numeric(16,4),
                (waste_qty * weighted_unit_cost)::numeric(16,4),
                CASE WHEN usage_qty + waste_qty = 0 THEN NULL
                    ELSE (waste_qty / (usage_qty + waste_qty))::numeric(12,8) END
            FROM analytics.fact_inventory_daily
        ),
        diff AS (
            (SELECT * FROM expected EXCEPT SELECT * FROM analytics.kpi_inventory_daily)
            UNION ALL
            (SELECT * FROM analytics.kpi_inventory_daily EXCEPT SELECT * FROM expected)
        )
        SELECT COUNT(*) FROM diff
        """,
    ),
    MetricControl(
        "labour_kpi_reconciliation",
        """
        WITH expected AS (
            SELECT
                date_key,
                property_key,
                department_key,
                actual_hours::numeric(16,2),
                overtime_hours::numeric(16,2),
                labour_cost::numeric(16,2),
                CASE WHEN actual_hours = 0 THEN NULL
                    ELSE (labour_cost / actual_hours)::numeric(16,6) END,
                CASE WHEN actual_hours = 0 THEN NULL
                    ELSE (overtime_hours / actual_hours)::numeric(12,8) END
            FROM analytics.fact_labour_daily
        ),
        diff AS (
            (SELECT * FROM expected EXCEPT SELECT * FROM analytics.kpi_labour_daily)
            UNION ALL
            (SELECT * FROM analytics.kpi_labour_daily EXCEPT SELECT * FROM expected)
        )
        SELECT COUNT(*) FROM diff
        """,
    ),
    MetricControl(
        "rooms_algebraic_identity",
        """
        SELECT COUNT(*)
        FROM analytics.kpi_rooms_daily
        WHERE adr IS NOT NULL
          AND ABS(revpar - (adr * occupancy_pct)) > 0.0001
        """,
    ),
    MetricControl(
        "metric_domain_ranges",
        """
        SELECT
            (SELECT COUNT(*) FROM analytics.kpi_rooms_daily
             WHERE occupancy_pct < 0 OR occupancy_pct > 1)
          + (SELECT COUNT(*) FROM analytics.kpi_fnb_outlet_daily
             WHERE discount_rate IS NOT NULL
               AND (discount_rate < 0 OR discount_rate > 1))
          + (SELECT COUNT(*) FROM analytics.kpi_inventory_daily
             WHERE waste_pct IS NOT NULL
               AND (waste_pct < 0 OR waste_pct > 1))
          + (SELECT COUNT(*) FROM analytics.kpi_labour_daily
             WHERE overtime_share IS NOT NULL
               AND (overtime_share < 0 OR overtime_share > 1))
        """,
    ),
)


def run_metric_validation(
    settings: DatabaseSettings | None = None,
) -> list[MetricValidationResult]:
    """Validate all materialized KPI marts independently from build SQL."""

    runtime = settings or load_settings()
    return [
        MetricValidationResult(
            name=control.name,
            mismatch_count=int(fetch_one(control.query, runtime)[0]),
        )
        for control in CONTROLS
    ]


def main() -> None:
    results = run_metric_validation()
    for result in results:
        print(
            f"{result.name}: mismatches={result.mismatch_count} "
            f"status={'PASS' if result.passed else 'FAIL'}"
        )
    if any(not result.passed for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
