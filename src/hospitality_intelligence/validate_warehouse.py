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
        "SELECT COALESCE(SUM(rooms_sold::numeric), 0) FROM raw.pms_bookings_daily",
        "SELECT COALESCE(SUM(rooms_sold), 0) FROM analytics.fact_room_bookings_daily",
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
        "SELECT COALESCE(SUM(units_sold::numeric), 0) FROM raw.pos_product_mix_daily",
        "SELECT COALESCE(SUM(units_sold), 0) FROM analytics.fact_pos_product_daily",
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
        "SELECT COALESCE(SUM(room_revenue::numeric), 0) FROM raw.pms_bookings_daily",
        "SELECT COALESCE(SUM(room_revenue), 0) FROM analytics.fact_room_bookings_daily",
        MONEY_TOLERANCE,
    ),
    PairControl(
        "pos_outlet_net_revenue",
        "SELECT COALESCE(SUM(net_revenue::numeric), 0) FROM raw.pos_checks_daily",
        "SELECT COALESCE(SUM(net_revenue), 0) FROM analytics.fact_pos_outlet_daily",
        MONEY_TOLERANCE,
    ),
    PairControl(
        "pos_product_net_revenue",
        "SELECT COALESCE(SUM(net_revenue::numeric), 0) FROM raw.pos_product_mix_daily",
        "SELECT COALESCE(SUM(net_revenue), 0) FROM analytics.fact_pos_product_daily",
        MONEY_TOLERANCE,
    ),
    PairControl(
        "purchase_cost",
        "SELECT COALESCE(SUM(purchase_cost::numeric), 0) FROM raw.purchases_daily",
        "SELECT COALESCE(SUM(purchase_cost), 0) FROM analytics.fact_purchases_daily",
        MONEY_TOLERANCE,
    ),
    PairControl(
        "inventory_value",
        "SELECT COALESCE(SUM(inventory_value::numeric), 0) FROM raw.inventory_daily",
        "SELECT COALESCE(SUM(inventory_value), 0) FROM analytics.fact_inventory_daily",
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
        "SELECT COALESCE(SUM(budget_revenue), 0) FROM analytics.fact_budget_monthly",
        MONEY_TOLERANCE,
    ),
    PairControl(
        "budget_cost",
        "SELECT COALESCE(SUM(budget_cost::numeric), 0) FROM raw.budget_monthly",
        "SELECT COALESCE(SUM(budget_cost), 0) FROM analytics.fact_budget_monthly",
        MONEY_TOLERANCE,
    ),
)

ALL_CONTROLS = ROW_COUNT_CONTROLS + QUANTITY_CONTROLS + MONEY_CONTROLS


def _decimal(value: object) -> Decimal:
    return Decimal(str(value))


def evaluate_pair(
    control: PairControl,
    settings: DatabaseSettings,
) -> ValidationResult:
    """Evaluate one source-to-fact control."""

    source_value = _decimal(fetch_one(control.source_query, settings)[0])
    target_value = _decimal(fetch_one(control.target_query, settings)[0])
    return ValidationResult(
        name=control.name,
        source_value=source_value,
        target_value=target_value,
        delta=source_value - target_value,
        tolerance=control.tolerance,
    )


def run_warehouse_validation(
    settings: DatabaseSettings | None = None,
) -> list[ValidationResult]:
    """Validate row counts, operational quantities, and financial totals."""

    runtime = settings or load_settings()
    return [evaluate_pair(control, runtime) for control in ALL_CONTROLS]


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
