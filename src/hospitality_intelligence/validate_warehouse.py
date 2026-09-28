"""Warehouse reconciliation controls for the typed analytical layer."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from hospitality_intelligence.config import DatabaseSettings, load_settings
from hospitality_intelligence.db import fetch_one

MONEY_TOLERANCE = Decimal("0.01")
QUANTITY_TOLERANCE = Decimal("0.01")


@dataclass(frozen=True)
class PairControl:
    """One source-to-fact equality control."""

    name: str
    source_query: str
    target_query: str
    tolerance: Decimal = Decimal("0.00")


@dataclass(frozen=True)
class DiscrepancyControl:
    """A query that must return zero mismatched rows."""

    name: str
    query: str


@dataclass(frozen=True)
class ValidationResult:
    """Observed delta for one warehouse control."""

    name: str
    source_value: Decimal
    target_value: Decimal
    delta: Decimal
    tolerance: Decimal

    @property
    def passed(self) -> bool:
        """Return whether the observed delta is inside the contract."""

        return abs(self.delta) <= self.tolerance


ROW_COUNT_CONTROLS = (
    PairControl(
        "room_inventory_row_count",
        "SELECT COUNT(*) FROM raw.pms_inventory_daily",
        "SELECT COUNT(*) FROM analytics.fact_room_inventory_daily",
    ),
    PairControl(
        "room_bookings_row_count",
        "SELECT COUNT(*) FROM raw.pms_bookings_daily",
        "SELECT COUNT(*) FROM analytics.fact_room_bookings_daily",
    ),
    PairControl(
        "pos_outlet_row_count",
        "SELECT COUNT(*) FROM raw.pos_checks_daily",
        "SELECT COUNT(*) FROM analytics.fact_pos_outlet_daily",
    ),
    PairControl(
        "pos_product_row_count",
        "SELECT COUNT(*) FROM raw.pos_product_mix_daily",
        "SELECT COUNT(*) FROM analytics.fact_pos_product_daily",
    ),
    PairControl(
        "purchases_row_count",
        "SELECT COUNT(*) FROM raw.purchases_daily",
        "SELECT COUNT(*) FROM analytics.fact_purchases_daily",
    ),
    PairControl(
        "inventory_row_count",
        "SELECT COUNT(*) FROM raw.inventory_daily",
        "SELECT COUNT(*) FROM analytics.fact_inventory_daily",
    ),
    PairControl(
        "labour_row_count",
        "SELECT COUNT(*) FROM raw.labour_daily",
        "SELECT COUNT(*) FROM analytics.fact_labour_daily",
    ),
    PairControl(
        "budget_row_count",
        "SELECT COUNT(*) FROM raw.budget_monthly",
        "SELECT COUNT(*) FROM analytics.fact_budget_monthly",
    ),
)

QUANTITY_CONTROLS = (
    PairControl(
        "rooms_available",
        "SELECT COALESCE(SUM(rooms_available::numeric), 0) "
        "FROM raw.pms_inventory_daily",
        "SELECT COALESCE(SUM(rooms_available), 0) "
        "FROM analytics.fact_room_inventory_daily",
        QUANTITY_TOLERANCE,
    ),
    PairControl(
        "rooms_sold",
        "SELECT COALESCE(SUM(rooms_sold::numeric), 0) "
        "FROM raw.pms_bookings_daily",
        "SELECT COALESCE(SUM(rooms_sold), 0) "
        "FROM analytics.fact_room_bookings_daily",
        QUANTITY_TOLERANCE,
    ),
    PairControl(
        "covers",
        "SELECT COALESCE(SUM(covers::numeric), 0) FROM raw.pos_checks_daily",
        "SELECT COALESCE(SUM(covers), 0) FROM analytics.fact_pos_outlet_daily",
        QUANTITY_TOLERANCE,
    ),
    PairControl(
        "units_sold",
        "SELECT COALESCE(SUM(units_sold::numeric), 0) "
        "FROM raw.pos_product_mix_daily",
        "SELECT COALESCE(SUM(units_sold), 0) "
        "FROM analytics.fact_pos_product_daily",
        QUANTITY_TOLERANCE,
    ),
    PairControl(
        "purchase_quantity",
        "SELECT COALESCE(SUM(quantity::numeric), 0) FROM raw.purchases_daily",
        "SELECT COALESCE(SUM(quantity), 0) FROM analytics.fact_purchases_daily",
        QUANTITY_TOLERANCE,
    ),
    PairControl(
        "inventory_usage",
        "SELECT COALESCE(SUM(usage_qty::numeric), 0) FROM raw.inventory_daily",
        "SELECT COALESCE(SUM(usage_qty), 0) FROM analytics.fact_inventory_daily",
        QUANTITY_TOLERANCE,
    ),
    PairControl(
        "inventory_waste",
        "SELECT COALESCE(SUM(waste_qty::numeric), 0) FROM raw.inventory_daily",
        "SELECT COALESCE(SUM(waste_qty), 0) FROM analytics.fact_inventory_daily",
        QUANTITY_TOLERANCE,
    ),
    PairControl(
        "labour_actual_hours",
        "SELECT COALESCE(SUM(actual_hours::numeric), 0) FROM raw.labour_daily",
        "SELECT COALESCE(SUM(actual_hours), 0) FROM analytics.fact_labour_daily",
        QUANTITY_TOLERANCE,
    ),
    PairControl(
        "labour_overtime_hours",
        "SELECT COALESCE(SUM(overtime_hours::numeric), 0) FROM raw.labour_daily",
        "SELECT COALESCE(SUM(overtime_hours), 0) FROM analytics.fact_labour_daily",
        QUANTITY_TOLERANCE,
    ),
)

MONEY_CONTROLS = (
    PairControl(
        "room_revenue",
        "SELECT COALESCE(SUM(room_revenue::numeric), 0) "
        "FROM raw.pms_bookings_daily",
        "SELECT COALESCE(SUM(room_revenue), 0) "
        "FROM analytics.fact_room_bookings_daily",
        MONEY_TOLERANCE,
    ),
    PairControl(
        "pos_outlet_net_revenue",
        "SELECT COALESCE(SUM(net_revenue::numeric), 0) FROM raw.pos_checks_daily",
        "SELECT COALESCE(SUM(net_revenue), 0) "
        "FROM analytics.fact_pos_outlet_daily",
        MONEY_TOLERANCE,
    ),
    PairControl(
        "pos_product_net_revenue",
        "SELECT COALESCE(SUM(net_revenue::numeric), 0) "
        "FROM raw.pos_product_mix_daily",
        "SELECT COALESCE(SUM(net_revenue), 0) "
        "FROM analytics.fact_pos_product_daily",
        MONEY_TOLERANCE,
    ),
    PairControl(
        "purchase_cost",
        "SELECT COALESCE(SUM(purchase_cost::numeric), 0) FROM raw.purchases_daily",
        "SELECT COALESCE(SUM(purchase_cost), 0) "
        "FROM analytics.fact_purchases_daily",
        MONEY_TOLERANCE,
    ),
    PairControl(
        "inventory_value",
        "SELECT COALESCE(SUM(inventory_value::numeric), 0) "
        "FROM raw.inventory_daily",
        "SELECT COALESCE(SUM(inventory_value), 0) "
        "FROM analytics.fact_inventory_daily",
        MONEY_TOLERANCE,
    ),
    PairControl(
        "labour_cost",
        "SELECT COALESCE(SUM(labour_cost::numeric), 0) FROM raw.labour_daily",
        "SELECT COALESCE(SUM(labour_cost), 0) FROM analytics.fact_labour_daily",
        MONEY_TOLERANCE,
    ),
    PairControl(
        "budget_revenue",
        "SELECT COALESCE(SUM(budget_revenue::numeric), 0) FROM raw.budget_monthly",
        "SELECT COALESCE(SUM(budget_revenue), 0) "
        "FROM analytics.fact_budget_monthly",
        MONEY_TOLERANCE,
    ),
    PairControl(
        "budget_cost",
        "SELECT COALESCE(SUM(budget_cost::numeric), 0) FROM raw.budget_monthly",
        "SELECT COALESCE(SUM(budget_cost), 0) "
        "FROM analytics.fact_budget_monthly",
        MONEY_TOLERANCE,
    ),
)

LINEAGE_CONTROLS = (
    DiscrepancyControl(
        "room_inventory_business_key_lineage",
        """
        SELECT COUNT(*) FROM (
            SELECT date::date, property_id, rooms_available::integer
            FROM raw.pms_inventory_daily
            EXCEPT
            SELECT d.full_date, p.property_id, f.rooms_available
            FROM analytics.fact_room_inventory_daily f
            JOIN analytics.dim_date d USING (date_key)
            JOIN analytics.dim_property p USING (property_key)
        ) diff
        """,
    ),
    DiscrepancyControl(
        "room_booking_business_key_lineage",
        """
        SELECT COUNT(*) FROM (
            SELECT
                date::date,
                property_id,
                segment,
                channel,
                rooms_sold::integer,
                room_revenue::numeric(14,2)
            FROM raw.pms_bookings_daily
            EXCEPT
            SELECT
                d.full_date,
                p.property_id,
                s.segment_name,
                c.channel_name,
                f.rooms_sold,
                f.room_revenue
            FROM analytics.fact_room_bookings_daily f
            JOIN analytics.dim_date d USING (date_key)
            JOIN analytics.dim_property p USING (property_key)
            JOIN analytics.dim_room_segment s USING (segment_key)
            JOIN analytics.dim_channel c USING (channel_key)
        ) diff
        """,
    ),
    DiscrepancyControl(
        "pos_outlet_business_key_lineage",
        """
        SELECT COUNT(*) FROM (
            SELECT
                date::date,
                property_id,
                outlet_id,
                covers::integer,
                net_revenue::numeric(14,2)
            FROM raw.pos_checks_daily
            EXCEPT
            SELECT
                d.full_date,
                p.property_id,
                o.outlet_id,
                f.covers,
                f.net_revenue
            FROM analytics.fact_pos_outlet_daily f
            JOIN analytics.dim_date d USING (date_key)
            JOIN analytics.dim_property p USING (property_key)
            JOIN analytics.dim_outlet o USING (outlet_key)
        ) diff
        """,
    ),
    DiscrepancyControl(
        "pos_product_business_key_lineage",
        """
        SELECT COUNT(*) FROM (
            SELECT
                date::date,
                property_id,
                outlet_id,
                product_id,
                units_sold::integer,
                net_revenue::numeric(14,2)
            FROM raw.pos_product_mix_daily
            EXCEPT
            SELECT
                d.full_date,
                p.property_id,
                o.outlet_id,
                pr.product_id,
                f.units_sold,
                f.net_revenue
            FROM analytics.fact_pos_product_daily f
            JOIN analytics.dim_date d USING (date_key)
            JOIN analytics.dim_property p USING (property_key)
            JOIN analytics.dim_outlet o USING (outlet_key)
            JOIN analytics.dim_product pr USING (product_key)
        ) diff
        """,
    ),
    DiscrepancyControl(
        "purchase_business_key_lineage",
        """
        SELECT COUNT(*) FROM (
            SELECT
                date::date,
                property_id,
                product_id,
                supplier_id,
                quantity::numeric(14,2),
                purchase_cost::numeric(14,2)
            FROM raw.purchases_daily
            EXCEPT
            SELECT
                d.full_date,
                p.property_id,
                pr.product_id,
                s.supplier_id,
                f.quantity,
                f.purchase_cost
            FROM analytics.fact_purchases_daily f
            JOIN analytics.dim_date d USING (date_key)
            JOIN analytics.dim_property p USING (property_key)
            JOIN analytics.dim_product pr USING (product_key)
            JOIN analytics.dim_supplier s USING (supplier_key)
        ) diff
        """,
    ),
    DiscrepancyControl(
        "inventory_business_key_lineage",
        """
        SELECT COUNT(*) FROM (
            SELECT
                date::date,
                property_id,
                product_id,
                usage_qty::numeric(14,2),
                waste_qty::numeric(14,2),
                inventory_value::numeric(14,2)
            FROM raw.inventory_daily
            EXCEPT
            SELECT
                d.full_date,
                p.property_id,
                pr.product_id,
                f.usage_qty,
                f.waste_qty,
                f.inventory_value
            FROM analytics.fact_inventory_daily f
            JOIN analytics.dim_date d USING (date_key)
            JOIN analytics.dim_property p USING (property_key)
            JOIN analytics.dim_product pr USING (product_key)
        ) diff
        """,
    ),
    DiscrepancyControl(
        "labour_business_key_lineage",
        """
        SELECT COUNT(*) FROM (
            SELECT
                date::date,
                property_id,
                department_id,
                actual_hours::numeric(14,2),
                overtime_hours::numeric(14,2),
                labour_cost::numeric(14,2)
            FROM raw.labour_daily
            EXCEPT
            SELECT
                d.full_date,
                p.property_id,
                dep.department_id,
                f.actual_hours,
                f.overtime_hours,
                f.labour_cost
            FROM analytics.fact_labour_daily f
            JOIN analytics.dim_date d USING (date_key)
            JOIN analytics.dim_property p USING (property_key)
            JOIN analytics.dim_department dep USING (department_key)
        ) diff
        """,
    ),
    DiscrepancyControl(
        "budget_business_key_lineage",
        """
        SELECT COUNT(*) FROM (
            SELECT
                month::date,
                property_id,
                department_id,
                budget_revenue::numeric(14,2),
                budget_cost::numeric(14,2)
            FROM raw.budget_monthly
            EXCEPT
            SELECT
                d.full_date,
                p.property_id,
                dep.department_id,
                f.budget_revenue,
                f.budget_cost
            FROM analytics.fact_budget_monthly f
            JOIN analytics.dim_date d USING (date_key)
            JOIN analytics.dim_property p USING (property_key)
            JOIN analytics.dim_department dep USING (department_key)
        ) diff
        """,
    ),
)

DIMENSION_LINEAGE_CONTROLS = (
    DiscrepancyControl(
        "property_dimension_lineage",
        """
        SELECT COUNT(*) FROM (
            (
                SELECT
                    property_id,
                    property_name,
                    archetype,
                    rooms_count::integer,
                    city
                FROM raw.properties
                EXCEPT
                SELECT
                    property_id,
                    property_name,
                    archetype,
                    rooms_count,
                    city
                FROM analytics.dim_property
            )
            UNION ALL
            (
                SELECT
                    property_id,
                    property_name,
                    archetype,
                    rooms_count,
                    city
                FROM analytics.dim_property
                EXCEPT
                SELECT
                    property_id,
                    property_name,
                    archetype,
                    rooms_count::integer,
                    city
                FROM raw.properties
            )
        ) diff
        """,
    ),
    DiscrepancyControl(
        "outlet_dimension_lineage",
        """
        SELECT COUNT(*) FROM (
            (
                SELECT outlet_id, property_id, outlet_name, outlet_type
                FROM raw.outlets
                EXCEPT
                SELECT o.outlet_id, p.property_id, o.outlet_name, o.outlet_type
                FROM analytics.dim_outlet o
                JOIN analytics.dim_property p USING (property_key)
            )
            UNION ALL
            (
                SELECT o.outlet_id, p.property_id, o.outlet_name, o.outlet_type
                FROM analytics.dim_outlet o
                JOIN analytics.dim_property p USING (property_key)
                EXCEPT
                SELECT outlet_id, property_id, outlet_name, outlet_type
                FROM raw.outlets
            )
        ) diff
        """,
    ),
    DiscrepancyControl(
        "product_dimension_lineage",
        """
        SELECT COUNT(*) FROM (
            (
                SELECT
                    product_id,
                    outlet_id,
                    property_id,
                    product_name,
                    category,
                    menu_price::numeric(14,2),
                    standard_unit_cost::numeric(14,2),
                    inventory_usage_per_unit::numeric(14,4)
                FROM raw.products
                EXCEPT
                SELECT
                    pr.product_id,
                    o.outlet_id,
                    p.property_id,
                    pr.product_name,
                    pr.category,
                    pr.menu_price,
                    pr.standard_unit_cost,
                    pr.inventory_usage_per_unit
                FROM analytics.dim_product pr
                JOIN analytics.dim_outlet o USING (outlet_key)
                JOIN analytics.dim_property p USING (property_key)
            )
            UNION ALL
            (
                SELECT
                    pr.product_id,
                    o.outlet_id,
                    p.property_id,
                    pr.product_name,
                    pr.category,
                    pr.menu_price,
                    pr.standard_unit_cost,
                    pr.inventory_usage_per_unit
                FROM analytics.dim_product pr
                JOIN analytics.dim_outlet o USING (outlet_key)
                JOIN analytics.dim_property p USING (property_key)
                EXCEPT
                SELECT
                    product_id,
                    outlet_id,
                    property_id,
                    product_name,
                    category,
                    menu_price::numeric(14,2),
                    standard_unit_cost::numeric(14,2),
                    inventory_usage_per_unit::numeric(14,4)
                FROM raw.products
            )
        ) diff
        """,
    ),
    DiscrepancyControl(
        "supplier_dimension_lineage",
        """
        SELECT COUNT(*) FROM (
            (
                SELECT supplier_id, supplier_name, category
                FROM raw.suppliers
                EXCEPT
                SELECT supplier_id, supplier_name, category
                FROM analytics.dim_supplier
            )
            UNION ALL
            (
                SELECT supplier_id, supplier_name, category
                FROM analytics.dim_supplier
                EXCEPT
                SELECT supplier_id, supplier_name, category
                FROM raw.suppliers
            )
        ) diff
        """,
    ),
    DiscrepancyControl(
        "department_dimension_lineage",
        """
        SELECT COUNT(*) FROM (
            (
                SELECT department_id, department_name
                FROM raw.departments
                EXCEPT
                SELECT department_id, department_name
                FROM analytics.dim_department
            )
            UNION ALL
            (
                SELECT department_id, department_name
                FROM analytics.dim_department
                EXCEPT
                SELECT department_id, department_name
                FROM raw.departments
            )
        ) diff
        """,
    ),
    DiscrepancyControl(
        "room_segment_dimension_lineage",
        """
        SELECT COUNT(*) FROM (
            (
                SELECT DISTINCT segment FROM raw.pms_bookings_daily
                EXCEPT
                SELECT segment_name FROM analytics.dim_room_segment
            )
            UNION ALL
            (
                SELECT segment_name FROM analytics.dim_room_segment
                EXCEPT
                SELECT DISTINCT segment FROM raw.pms_bookings_daily
            )
        ) diff
        """,
    ),
    DiscrepancyControl(
        "date_dimension_lineage",
        """
        WITH source_dates AS (
            SELECT date::date AS full_date FROM raw.pms_inventory_daily
            UNION
            SELECT date::date FROM raw.pms_bookings_daily
            UNION
            SELECT date::date FROM raw.pos_checks_daily
            UNION
            SELECT date::date FROM raw.pos_product_mix_daily
            UNION
            SELECT date::date FROM raw.purchases_daily
            UNION
            SELECT date::date FROM raw.inventory_daily
            UNION
            SELECT date::date FROM raw.labour_daily
            UNION
            SELECT month::date FROM raw.budget_monthly
        ),
        expected AS (
            SELECT
                full_date,
                EXTRACT(YEAR FROM full_date)::integer AS year_number,
                EXTRACT(MONTH FROM full_date)::integer AS month_number,
                EXTRACT(DAY FROM full_date)::integer AS day_number,
                DATE_TRUNC('month', full_date)::date AS month_start,
                TRIM(TO_CHAR(full_date, 'Day')) AS day_name,
                EXTRACT(ISODOW FROM full_date) IN (6, 7) AS is_weekend
            FROM source_dates
        )
        SELECT COUNT(*) FROM (
            (
                SELECT * FROM expected
                EXCEPT
                SELECT
                    full_date,
                    year_number,
                    month_number,
                    day_number,
                    month_start,
                    day_name,
                    is_weekend
                FROM analytics.dim_date
            )
            UNION ALL
            (
                SELECT
                    full_date,
                    year_number,
                    month_number,
                    day_number,
                    month_start,
                    day_name,
                    is_weekend
                FROM analytics.dim_date
                EXCEPT
                SELECT * FROM expected
            )
        ) diff
        """,
    ),
    DiscrepancyControl(
        "channel_dimension_lineage",
        """
        SELECT COUNT(*) FROM (
            (
                SELECT DISTINCT channel FROM raw.pms_bookings_daily
                EXCEPT
                SELECT channel_name FROM analytics.dim_channel
            )
            UNION ALL
            (
                SELECT channel_name FROM analytics.dim_channel
                EXCEPT
                SELECT DISTINCT channel FROM raw.pms_bookings_daily
            )
        ) diff
        """,
    ),
)

ALL_PAIR_CONTROLS = ROW_COUNT_CONTROLS + QUANTITY_CONTROLS + MONEY_CONTROLS


def _decimal(value: object) -> Decimal:
    return Decimal(str(value))


def evaluate_pair(
    control: PairControl,
    settings: DatabaseSettings,
) -> ValidationResult:
    """Evaluate one source-to-fact aggregate equality control."""

    source_value = _decimal(fetch_one(control.source_query, settings)[0])
    target_value = _decimal(fetch_one(control.target_query, settings)[0])
    return ValidationResult(
        name=control.name,
        source_value=source_value,
        target_value=target_value,
        delta=source_value - target_value,
        tolerance=control.tolerance,
    )


def evaluate_discrepancy(
    control: DiscrepancyControl,
    settings: DatabaseSettings,
) -> ValidationResult:
    """Evaluate one zero-mismatch business-key lineage control."""

    mismatch_count = _decimal(fetch_one(control.query, settings)[0])
    return ValidationResult(
        name=control.name,
        source_value=Decimal("0"),
        target_value=mismatch_count,
        delta=mismatch_count,
        tolerance=Decimal("0"),
    )


def run_warehouse_validation(
    settings: DatabaseSettings | None = None,
) -> list[ValidationResult]:
    """Validate facts at count, aggregate, and business-key lineage levels."""

    runtime = settings or load_settings()
    pair_results = [
        evaluate_pair(control, runtime)
        for control in ALL_PAIR_CONTROLS
    ]
    fact_lineage_results = [
        evaluate_discrepancy(control, runtime)
        for control in LINEAGE_CONTROLS
    ]
    dimension_lineage_results = [
        evaluate_discrepancy(control, runtime)
        for control in DIMENSION_LINEAGE_CONTROLS
    ]
    return pair_results + fact_lineage_results + dimension_lineage_results


def main() -> None:
    results = run_warehouse_validation()
    for result in results:
        print(
            f"{result.name}: "
            f"source={result.source_value} "
            f"target={result.target_value} "
            f"delta={result.delta} "
            f"status={'PASS' if result.passed else 'FAIL'}"
        )
    if any(not result.passed for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
