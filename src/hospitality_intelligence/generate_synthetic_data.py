"""Generate seeded synthetic hospitality operating-source files."""

from __future__ import annotations

import argparse
import csv
import math
import random
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path


@dataclass(frozen=True)
class GenerationConfig:
    """Configuration for deterministic synthetic source generation."""

    days: int = 120
    seed: int = 42
    anchor_date: date = date(2026, 9, 1)
    scenario: str = "margin_leakage"


PROPERTIES = [
    {
        "property_id": "P001",
        "property_name": "Pretoria Urban House",
        "archetype": "urban_hotel",
        "rooms_count": 140,
        "city": "Paris",
        "base_occupancy": 0.72,
        "base_adr": 185.0,
    },
    {
        "property_id": "P002",
        "property_name": "Pretoria Coastal Resort",
        "archetype": "leisure_resort",
        "rooms_count": 220,
        "city": "Da Nang",
        "base_occupancy": 0.68,
        "base_adr": 210.0,
    },
    {
        "property_id": "P003",
        "property_name": "Pretoria Boutique Maison",
        "archetype": "boutique_hotel",
        "rooms_count": 60,
        "city": "Lisbon",
        "base_occupancy": 0.77,
        "base_adr": 265.0,
    },
]

OUTLETS = [
    ("O001", "P001", "Urban Breakfast", "breakfast", 28.0),
    ("O002", "P001", "Urban Restaurant", "restaurant", 62.0),
    ("O003", "P001", "Urban Bar", "bar", 31.0),
    ("O004", "P002", "Resort Breakfast", "breakfast", 30.0),
    ("O005", "P002", "Resort Restaurant", "restaurant", 68.0),
    ("O006", "P002", "Pool Bar", "bar", 34.0),
    ("O007", "P003", "Boutique Breakfast", "breakfast", 34.0),
    ("O008", "P003", "Boutique Lounge", "lounge", 48.0),
]

PRODUCT_TEMPLATES = {
    "breakfast": [
        ("Breakfast Buffet", "food", 26.0, 8.2, 1.0),
        ("Specialty Coffee", "beverage", 6.5, 1.3, 1.0),
        ("Fresh Juice", "beverage", 8.0, 2.2, 1.0),
    ],
    "restaurant": [
        ("Signature Main", "food", 32.0, 10.5, 1.0),
        ("Chef Starter", "food", 18.0, 5.2, 1.0),
        ("Wine Glass", "beverage", 14.0, 3.9, 1.0),
    ],
    "bar": [
        ("Signature Cocktail", "beverage", 16.0, 4.6, 1.0),
        ("Premium Beer", "beverage", 9.0, 2.4, 1.0),
        ("Bar Snack", "food", 12.0, 3.4, 1.0),
    ],
    "lounge": [
        ("Craft Cocktail", "beverage", 18.0, 5.0, 1.0),
        ("Wine Glass", "beverage", 16.0, 4.2, 1.0),
        ("Small Plate", "food", 20.0, 6.8, 1.0),
    ],
}

SUPPLIERS = [
    ("S001", "Prime Foods", "food"),
    ("S002", "Cellar Partners", "beverage"),
    ("S003", "Fresh Market Logistics", "food"),
]

DEPARTMENTS = [
    ("D001", "Rooms"),
    ("D002", "Food & Beverage"),
    ("D003", "Operations"),
]


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows generated for {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _round_money(value: float) -> float:
    return round(value + 1e-9, 2)


def _dates(config: GenerationConfig) -> list[date]:
    return [config.anchor_date + timedelta(days=offset) for offset in range(config.days)]


def _is_leakage_period(current: date, config: GenerationConfig) -> bool:
    if config.scenario != "margin_leakage":
        return False
    return current >= config.anchor_date + timedelta(days=max(0, config.days - 20))


def _make_master_data() -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    properties = [
        {key: value for key, value in property_row.items() if not key.startswith("base_")}
        for property_row in PROPERTIES
    ]
    outlets = [
        {
            "outlet_id": outlet_id,
            "property_id": property_id,
            "outlet_name": outlet_name,
            "outlet_type": outlet_type,
        }
        for outlet_id, property_id, outlet_name, outlet_type, _ in OUTLETS
    ]
    products: list[dict[str, object]] = []
    product_number = 1
    for outlet_id, property_id, _, outlet_type, _ in OUTLETS:
        for product_name, category, menu_price, standard_cost, usage in PRODUCT_TEMPLATES[
            outlet_type
        ]:
            products.append(
                {
                    "product_id": f"PRD-{product_number:03d}",
                    "outlet_id": outlet_id,
                    "property_id": property_id,
                    "product_name": product_name,
                    "category": category,
                    "menu_price": menu_price,
                    "standard_unit_cost": standard_cost,
                    "inventory_usage_per_unit": usage,
                }
            )
            product_number += 1
    suppliers = [
        {"supplier_id": supplier_id, "supplier_name": name, "category": category}
        for supplier_id, name, category in SUPPLIERS
    ]
    departments = [
        {"department_id": department_id, "department_name": name}
        for department_id, name in DEPARTMENTS
    ]
    return properties, outlets, products, suppliers, departments


def _allocate_integer(total: int, weights: list[float]) -> list[int]:
    if total <= 0:
        return [0] * len(weights)
    weight_sum = sum(weights)
    raw = [total * weight / weight_sum for weight in weights]
    allocated = [int(value) for value in raw]
    remainder = total - sum(allocated)
    ranking = sorted(
        range(len(raw)),
        key=lambda index: raw[index] - allocated[index],
        reverse=True,
    )
    for index in ranking[:remainder]:
        allocated[index] += 1
    return allocated


def _allocate_money(total: float, weights: list[float]) -> list[float]:
    cents = round(total * 100)
    integer_allocations = _allocate_integer(cents, weights)
    return [value / 100 for value in integer_allocations]


def generate(config: GenerationConfig, output_dir: Path) -> None:
    """Generate the full synthetic source-system surface."""

    if config.days < 30:
        raise ValueError("days must be >= 30 so monthly and leakage patterns remain testable")
    if config.scenario not in {"margin_leakage", "healthy"}:
        raise ValueError("scenario must be one of: margin_leakage, healthy")

    rng = random.Random(config.seed)
    properties, outlets, products, suppliers, departments = _make_master_data()
    product_map = {row["product_id"]: row for row in products}
    outlet_products: dict[str, list[dict[str, object]]] = {}
    for product in products:
        outlet_products.setdefault(str(product["outlet_id"]), []).append(product)

    pms_inventory: list[dict[str, object]] = []
    pms_bookings: list[dict[str, object]] = []
    pos_checks: list[dict[str, object]] = []
    pos_product_mix: list[dict[str, object]] = []
    purchases: list[dict[str, object]] = []
    inventory: list[dict[str, object]] = []
    labour: list[dict[str, object]] = []
    budget: list[dict[str, object]] = []

    product_units: dict[tuple[str, date], int] = {}
    prior_closing: dict[tuple[str, str], float] = {}

    for current in _dates(config):
        day_index = (current - config.anchor_date).days
        weekend_factor = 1.08 if current.weekday() >= 4 else 0.97
        seasonal_wave = 1 + 0.12 * math.sin(day_index / 11)

        rooms_sold_by_property: dict[str, int] = {}
        for property_row in PROPERTIES:
            property_id = str(property_row["property_id"])
            rooms_available = int(property_row["rooms_count"])
            demand = float(property_row["base_occupancy"]) * weekend_factor * seasonal_wave
            if property_id == "P002":
                demand *= 1.08 if current.month in {9, 10} else 0.95
                if _is_leakage_period(current, config):
                    demand *= 1.04
            demand *= rng.uniform(0.94, 1.06)
            rooms_sold = max(
                0,
                min(rooms_available, round(rooms_available * min(demand, 0.97))),
            )
            rooms_sold_by_property[property_id] = rooms_sold
            pms_inventory.append(
                {
                    "date": current.isoformat(),
                    "property_id": property_id,
                    "rooms_available": rooms_available,
                }
            )

            allocation_weights = [0.26, 0.20, 0.10, 0.18, 0.16, 0.10]
            sold_allocations = _allocate_integer(rooms_sold, allocation_weights)
            adr_base = float(property_row["base_adr"]) * (
                1 + 0.05 * math.sin(day_index / 13)
            )
            combinations = [
                ("corporate", "corporate"),
                ("corporate", "direct"),
                ("group", "direct"),
                ("leisure", "direct"),
                ("leisure", "ota"),
                ("group", "ota"),
            ]
            for (segment, channel), sold in zip(
                combinations,
                sold_allocations,
                strict=True,
            ):
                multiplier = {
                    "corporate": 0.93,
                    "direct": 1.04,
                    "ota": 0.96,
                }[channel]
                segment_multiplier = {
                    "corporate": 0.98,
                    "leisure": 1.05,
                    "group": 0.88,
                }[segment]
                adr = (
                    adr_base
                    * multiplier
                    * segment_multiplier
                    * rng.uniform(0.98, 1.02)
                )
                pms_bookings.append(
                    {
                        "date": current.isoformat(),
                        "property_id": property_id,
                        "segment": segment,
                        "channel": channel,
                        "rooms_sold": sold,
                        "room_revenue": _round_money(sold * adr),
                    }
                )

        outlet_daily_covers: dict[tuple[str, date], int] = {}
        for outlet_id, property_id, _, outlet_type, avg_check in OUTLETS:
            rooms_sold = rooms_sold_by_property[property_id]
            base_cover_factor = {
                "breakfast": 0.82,
                "restaurant": 0.52,
                "bar": 0.38,
                "lounge": 0.44,
            }[outlet_type]
            covers = max(
                0,
                round(
                    rooms_sold
                    * base_cover_factor
                    * rng.uniform(0.90, 1.10)
                ),
            )
            if property_id == "P002" and _is_leakage_period(current, config):
                covers = round(covers * 1.06)
            discount_rate = 0.035 + rng.uniform(0, 0.025)
            net_revenue = _round_money(
                covers * avg_check * rng.uniform(0.94, 1.06)
            )
            gross_revenue = _round_money(
                net_revenue / max(0.80, 1 - discount_rate)
            )
            discount_amount = _round_money(gross_revenue - net_revenue)
            pos_checks.append(
                {
                    "date": current.isoformat(),
                    "property_id": property_id,
                    "outlet_id": outlet_id,
                    "covers": covers,
                    "gross_revenue": gross_revenue,
                    "discount_amount": discount_amount,
                    "net_revenue": net_revenue,
                }
            )
            outlet_daily_covers[(outlet_id, current)] = covers

            outlet_product_rows = outlet_products[outlet_id]
            weights = [0.46, 0.32, 0.22]
            revenue_allocations = _allocate_money(net_revenue, weights)
            for product, product_revenue in zip(
                outlet_product_rows,
                revenue_allocations,
                strict=True,
            ):
                units = max(
                    0,
                    round(product_revenue / float(product["menu_price"])),
                )
                product_id = str(product["product_id"])
                product_units[(product_id, current)] = units
                pos_product_mix.append(
                    {
                        "date": current.isoformat(),
                        "property_id": property_id,
                        "outlet_id": outlet_id,
                        "product_id": product_id,
                        "units_sold": units,
                        "net_revenue": _round_money(product_revenue),
                    }
                )

        for product_id, product in product_map.items():
            property_id = str(product["property_id"])
            category = str(product["category"])
            units_sold = product_units[(product_id, current)]
            usage = round(
                units_sold * float(product["inventory_usage_per_unit"]),
                2,
            )
            opening = prior_closing.get(
                (property_id, product_id),
                max(20.0, usage * 1.8 + 10.0),
            )
            leakage = (
                property_id == "P002"
                and category == "beverage"
                and _is_leakage_period(current, config)
            )
            waste_rate = rng.uniform(0.012, 0.025) + (0.055 if leakage else 0)
            waste = round(usage * waste_rate, 2)
            target_closing = max(18.0, usage * 1.5)
            receipts = max(
                0.0,
                round(usage + waste + target_closing - opening, 2),
            )
            closing = round(opening + receipts - usage - waste, 2)

            supplier_id = (
                "S002"
                if category == "beverage"
                else rng.choice(["S001", "S003"])
            )
            unit_cost = float(product["standard_unit_cost"]) * rng.uniform(
                0.98,
                1.025,
            )
            if leakage:
                unit_cost *= 1.12
            unit_cost = _round_money(unit_cost)
            purchase_cost = _round_money(receipts * unit_cost)
            purchases.append(
                {
                    "date": current.isoformat(),
                    "property_id": property_id,
                    "product_id": product_id,
                    "supplier_id": supplier_id,
                    "quantity": receipts,
                    "unit_cost": unit_cost,
                    "purchase_cost": purchase_cost,
                }
            )
            inventory.append(
                {
                    "date": current.isoformat(),
                    "property_id": property_id,
                    "product_id": product_id,
                    "opening_qty": round(opening, 2),
                    "receipts_qty": receipts,
                    "usage_qty": usage,
                    "waste_qty": waste,
                    "closing_qty": closing,
                    "weighted_unit_cost": unit_cost,
                    "inventory_value": _round_money(closing * unit_cost),
                }
            )
            prior_closing[(property_id, product_id)] = closing

        for property_row in PROPERTIES:
            property_id = str(property_row["property_id"])
            rooms_sold = rooms_sold_by_property[property_id]
            property_outlets = [
                row for row in OUTLETS if row[1] == property_id
            ]
            covers = sum(
                outlet_daily_covers[(row[0], current)]
                for row in property_outlets
            )
            department_parameters = {
                "D001": (rooms_sold * 0.42 + 28, 22.0),
                "D002": (covers * 0.16 + 36, 20.5),
                "D003": (rooms_sold * 0.12 + 24, 19.0),
            }
            for department_id, (scheduled_base, rate) in department_parameters.items():
                scheduled = round(
                    max(12.0, scheduled_base * rng.uniform(0.96, 1.04)),
                    2,
                )
                actual_factor = rng.uniform(0.97, 1.06)
                if (
                    property_id == "P002"
                    and department_id == "D002"
                    and _is_leakage_period(current, config)
                ):
                    actual_factor *= 1.15
                actual = round(scheduled * actual_factor, 2)
                overtime = round(max(0.0, actual - scheduled), 2)
                labour_cost = _round_money(
                    actual * rate + overtime * rate * 0.35
                )
                labour.append(
                    {
                        "date": current.isoformat(),
                        "property_id": property_id,
                        "department_id": department_id,
                        "scheduled_hours": scheduled,
                        "actual_hours": actual,
                        "overtime_hours": overtime,
                        "labour_cost": labour_cost,
                    }
                )

    months = sorted({current.replace(day=1) for current in _dates(config)})
    for month_start in months:
        for property_row in PROPERTIES:
            property_id = str(property_row["property_id"])
            rooms_revenue_budget = (
                int(property_row["rooms_count"])
                * float(property_row["base_occupancy"])
                * float(property_row["base_adr"])
                * 30
            )
            fnb_budget = rooms_revenue_budget * (
                0.30 if property_id == "P002" else 0.22
            )
            budget_parameters = {
                "D001": (
                    rooms_revenue_budget,
                    rooms_revenue_budget * 0.23,
                ),
                "D002": (
                    fnb_budget,
                    fnb_budget * 0.55,
                ),
                "D003": (
                    0.0,
                    rooms_revenue_budget * 0.10,
                ),
            }
            for department_id, (revenue_budget, cost_budget) in budget_parameters.items():
                budget.append(
                    {
                        "month": month_start.isoformat(),
                        "property_id": property_id,
                        "department_id": department_id,
                        "budget_revenue": _round_money(revenue_budget),
                        "budget_cost": _round_money(cost_budget),
                    }
                )

    _write_csv(output_dir / "properties.csv", properties)
    _write_csv(output_dir / "outlets.csv", outlets)
    _write_csv(output_dir / "products.csv", products)
    _write_csv(output_dir / "suppliers.csv", suppliers)
    _write_csv(output_dir / "departments.csv", departments)
    _write_csv(output_dir / "pms_inventory_daily.csv", pms_inventory)
    _write_csv(output_dir / "pms_bookings_daily.csv", pms_bookings)
    _write_csv(output_dir / "pos_checks_daily.csv", pos_checks)
    _write_csv(output_dir / "pos_product_mix_daily.csv", pos_product_mix)
    _write_csv(output_dir / "purchases_daily.csv", purchases)
    _write_csv(output_dir / "inventory_daily.csv", inventory)
    _write_csv(output_dir / "labour_daily.csv", labour)
    _write_csv(output_dir / "budget_monthly.csv", budget)


def _parse_anchor(value: str) -> date:
    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).astimezone(UTC).date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("anchor must be ISO-8601") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic hospitality source data."
    )
    parser.add_argument("--output-dir", default="data/sample")
    parser.add_argument("--days", type=int, default=120)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--anchor",
        type=_parse_anchor,
        default=date(2026, 9, 1),
    )
    parser.add_argument(
        "--scenario",
        choices=["margin_leakage", "healthy"],
        default="margin_leakage",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = GenerationConfig(
        days=args.days,
        seed=args.seed,
        anchor_date=args.anchor,
        scenario=args.scenario,
    )
    generate(config, Path(args.output_dir))
    print(
        f"Generated {config.days} days of synthetic hospitality sources "
        f"for scenario={config.scenario!r}."
    )


if __name__ == "__main__":
    main()
