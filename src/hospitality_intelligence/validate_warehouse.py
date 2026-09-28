"""Warehouse reconciliation controls for the typed analytical layer."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from hospitality_intelligence.config import DatabaseSettings, load_settings
from hospitality_intelligence.db import fetch_one

MONEY_TOLERANCE = Decimal("0.01")


@dataclass(frozen=True)
class WarehouseControl:
    name: str
    query: str
    tolerance: Decimal = Decimal("0.00")


CONTROLS = (
    WarehouseControl(
        "room_inventory_row_count",
        "SELECT (SELECT COUNT(*) FROM raw.pms_inventory_daily) - "
        "(SELECT COUNT(*) FROM analytics.fact_room_inventory_daily)",
    ),
    WarehouseControl(
        "room_bookings_row_count",
        "SELECT (SELECT COUNT(*) FROM raw.pms_bookings_daily) - "
        "(SELECT COUNT(*) FROM analytics.fact_room_bookings_daily)",
    ),
    WarehouseControl(
        "pos_outlet_row_count",
        "SELECT (SELECT COUNT(*) FROM raw.pos_checks_daily) - "
        "(SELECT COUNT(*) FROM analytics.fact_pos_outlet_daily)",
    ),
    WarehouseControl(
        "pos_product_row_count",
        "SELECT (SELECT COUNT(*) FROM raw.pos_product_mix_daily) - "
        "(SELECT COUNT(*) FROM analytics.fact_pos_product_daily)",
    ),
    WarehouseControl(
        "room_revenue_total",
        "SELECT COALESCE(SUM(room_revenue::numeric),0) FROM raw.pms_bookings_daily",
        MONEY_TOLERANCE,
    ),
    WarehouseControl(
        "room_revenue_fact_total",
        "SELECT COALESCE(SUM(room_revenue),0) FROM analytics.fact_room_bookings_daily",
        MONEY_TOLERANCE,
    ),
    WarehouseControl(
        "pos_net_source_total",
        "SELECT COALESCE(SUM(net_revenue::numeric),0) FROM raw.pos_checks_daily",
        MONEY_TOLERANCE,
    ),
    WarehouseControl(
        "pos_net_fact_total",
        "SELECT COALESCE(SUM(net_revenue),0) FROM analytics.fact_pos_outlet_daily",
        MONEY_TOLERANCE,
    ),
    WarehouseControl(
        "purchase_cost_source_total",
        "SELECT COALESCE(SUM(purchase_cost::numeric),0) FROM raw.purchases_daily",
        MONEY_TOLERANCE,
    ),
    WarehouseControl(
        "purchase_cost_fact_total",
        "SELECT COALESCE(SUM(purchase_cost),0) FROM analytics.fact_purchases_daily",
        MONEY_TOLERANCE,
    ),
    WarehouseControl(
        "labour_cost_source_total",
        "SELECT COALESCE(SUM(labour_cost::numeric),0) FROM raw.labour_daily",
        MONEY_TOLERANCE,
    ),
    WarehouseControl(
        "labour_cost_fact_total",
        "SELECT COALESCE(SUM(labour_cost),0) FROM analytics.fact_labour_daily",
        MONEY_TOLERANCE,
    ),
)


def _decimal(value: object) -> Decimal:
    return Decimal(str(value))


def run_warehouse_validation(
    settings: DatabaseSettings | None = None,
) -> list[tuple[str, Decimal]]:
    """Return zero-delta controls for counts and paired financial totals."""

    runtime = settings or load_settings()
    direct_controls = CONTROLS[:4]
    results: list[tuple[str, Decimal]] = []

    for control in direct_controls:
        value = _decimal(fetch_one(control.query, runtime)[0])
        results.append((control.name, value))

    paired = [
        ("room_revenue", CONTROLS[4], CONTROLS[5]),
        ("pos_net_revenue", CONTROLS[6], CONTROLS[7]),
        ("purchase_cost", CONTROLS[8], CONTROLS[9]),
        ("labour_cost", CONTROLS[10], CONTROLS[11]),
    ]
    for name, source_control, fact_control in paired:
        source_value = _decimal(fetch_one(source_control.query, runtime)[0])
        fact_value = _decimal(fetch_one(fact_control.query, runtime)[0])
        results.append((name, source_value - fact_value))

    return results


def main() -> None:
    results = run_warehouse_validation()
    for name, delta in results:
        print(f"{name}: delta={delta}")
    if any(abs(delta) > MONEY_TOLERANCE for _, delta in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
