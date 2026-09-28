"""Source contracts and cross-source validation for the hospitality flagship."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import Literal

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, model_validator

MONEY_TOLERANCE = 0.02
QUANTITY_TOLERANCE = 0.01


class StrictModel(BaseModel):
    """Base contract with no silent extra fields."""

    model_config = ConfigDict(extra="forbid")


class PropertyRecord(StrictModel):
    property_id: str
    property_name: str
    archetype: Literal["urban_hotel", "leisure_resort", "boutique_hotel"]
    rooms_count: int = Field(gt=0)
    city: str


class OutletRecord(StrictModel):
    outlet_id: str
    property_id: str
    outlet_name: str
    outlet_type: Literal["breakfast", "restaurant", "bar", "lounge"]


class ProductRecord(StrictModel):
    product_id: str
    outlet_id: str
    property_id: str
    product_name: str
    category: Literal["food", "beverage"]
    menu_price: float = Field(gt=0)
    standard_unit_cost: float = Field(gt=0)
    inventory_usage_per_unit: float = Field(gt=0)


class SupplierRecord(StrictModel):
    supplier_id: str
    supplier_name: str
    category: Literal["food", "beverage"]


class DepartmentRecord(StrictModel):
    department_id: str
    department_name: str


class PMSInventoryRecord(StrictModel):
    date: date
    property_id: str
    rooms_available: int = Field(gt=0)


class PMSBookingRecord(StrictModel):
    date: date
    property_id: str
    segment: Literal["corporate", "leisure", "group"]
    channel: Literal["direct", "ota", "corporate"]
    rooms_sold: int = Field(ge=0)
    room_revenue: float = Field(ge=0)


class POSCheckRecord(StrictModel):
    date: date
    property_id: str
    outlet_id: str
    covers: int = Field(ge=0)
    gross_revenue: float = Field(ge=0)
    discount_amount: float = Field(ge=0)
    net_revenue: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_revenue_identity(self) -> POSCheckRecord:
        if abs((self.gross_revenue - self.discount_amount) - self.net_revenue) > MONEY_TOLERANCE:
            raise ValueError("net_revenue must equal gross_revenue - discount_amount")
        return self


class POSProductMixRecord(StrictModel):
    date: date
    property_id: str
    outlet_id: str
    product_id: str
    units_sold: int = Field(ge=0)
    net_revenue: float = Field(ge=0)


class PurchaseRecord(StrictModel):
    date: date
    property_id: str
    product_id: str
    supplier_id: str
    quantity: float = Field(ge=0)
    unit_cost: float = Field(gt=0)
    purchase_cost: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_purchase_identity(self) -> PurchaseRecord:
        if abs((self.quantity * self.unit_cost) - self.purchase_cost) > MONEY_TOLERANCE:
            raise ValueError("purchase_cost must equal quantity * unit_cost")
        return self


class InventoryRecord(StrictModel):
    date: date
    property_id: str
    product_id: str
    opening_qty: float = Field(ge=0)
    receipts_qty: float = Field(ge=0)
    usage_qty: float = Field(ge=0)
    waste_qty: float = Field(ge=0)
    closing_qty: float = Field(ge=0)
    weighted_unit_cost: float = Field(gt=0)
    inventory_value: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_inventory_identities(self) -> InventoryRecord:
        expected_closing = self.opening_qty + self.receipts_qty - self.usage_qty - self.waste_qty
        if abs(expected_closing - self.closing_qty) > QUANTITY_TOLERANCE:
            raise ValueError("inventory roll-forward does not balance")
        inventory_value_delta = abs(
            (self.closing_qty * self.weighted_unit_cost) - self.inventory_value
        )
        if inventory_value_delta > MONEY_TOLERANCE:
            raise ValueError("inventory_value must equal closing_qty * weighted_unit_cost")
        return self


class LabourRecord(StrictModel):
    date: date
    property_id: str
    department_id: str
    scheduled_hours: float = Field(ge=0)
    actual_hours: float = Field(ge=0)
    overtime_hours: float = Field(ge=0)
    labour_cost: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_overtime(self) -> LabourRecord:
        if self.overtime_hours - self.actual_hours > QUANTITY_TOLERANCE:
            raise ValueError("overtime_hours cannot exceed actual_hours")
        return self


class BudgetRecord(StrictModel):
    month: date
    property_id: str
    department_id: str
    budget_revenue: float = Field(ge=0)
    budget_cost: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_month_grain(self) -> BudgetRecord:
        if self.month.day != 1:
            raise ValueError("budget month must be represented by the first calendar day")
        return self


SOURCE_MODELS: dict[str, type[StrictModel]] = {
    "properties.csv": PropertyRecord,
    "outlets.csv": OutletRecord,
    "products.csv": ProductRecord,
    "suppliers.csv": SupplierRecord,
    "departments.csv": DepartmentRecord,
    "pms_inventory_daily.csv": PMSInventoryRecord,
    "pms_bookings_daily.csv": PMSBookingRecord,
    "pos_checks_daily.csv": POSCheckRecord,
    "pos_product_mix_daily.csv": POSProductMixRecord,
    "purchases_daily.csv": PurchaseRecord,
    "inventory_daily.csv": InventoryRecord,
    "labour_daily.csv": LabourRecord,
    "budget_monthly.csv": BudgetRecord,
}

KEY_COLUMNS: dict[str, list[str]] = {
    "properties.csv": ["property_id"],
    "outlets.csv": ["outlet_id"],
    "products.csv": ["product_id"],
    "suppliers.csv": ["supplier_id"],
    "departments.csv": ["department_id"],
    "pms_inventory_daily.csv": ["date", "property_id"],
    "pms_bookings_daily.csv": ["date", "property_id", "segment", "channel"],
    "pos_checks_daily.csv": ["date", "property_id", "outlet_id"],
    "pos_product_mix_daily.csv": ["date", "property_id", "outlet_id", "product_id"],
    "purchases_daily.csv": ["date", "property_id", "product_id", "supplier_id"],
    "inventory_daily.csv": ["date", "property_id", "product_id"],
    "labour_daily.csv": ["date", "property_id", "department_id"],
    "budget_monthly.csv": ["month", "property_id", "department_id"],
}


def _validate_rows(filename: str, frame: pd.DataFrame) -> None:
    model = SOURCE_MODELS[filename]
    for record in frame.to_dict(orient="records"):
        model.model_validate(record)


def _validate_unique_keys(filename: str, frame: pd.DataFrame) -> None:
    keys = KEY_COLUMNS[filename]
    duplicated = frame.duplicated(keys, keep=False)
    if duplicated.any():
        raise ValueError(f"{filename}: duplicate business key detected for {keys}")


def _require_members(values: Iterable[str], allowed: set[str], label: str) -> None:
    unknown = sorted(set(values) - allowed)
    if unknown:
        raise ValueError(f"{label}: unknown references: {unknown[:10]}")


def _validate_cross_source(frames: dict[str, pd.DataFrame]) -> None:
    properties = frames["properties.csv"]
    outlets = frames["outlets.csv"]
    products = frames["products.csv"]
    suppliers = frames["suppliers.csv"]
    departments = frames["departments.csv"]

    property_ids = set(properties["property_id"])
    outlet_ids = set(outlets["outlet_id"])
    product_ids = set(products["product_id"])
    supplier_ids = set(suppliers["supplier_id"])
    department_ids = set(departments["department_id"])

    outlet_property = dict(zip(outlets["outlet_id"], outlets["property_id"], strict=True))
    product_property = dict(zip(products["product_id"], products["property_id"], strict=True))
    product_outlet = dict(zip(products["product_id"], products["outlet_id"], strict=True))
    product_category = dict(zip(products["product_id"], products["category"], strict=True))
    supplier_category = dict(zip(suppliers["supplier_id"], suppliers["category"], strict=True))

    _require_members(outlets["property_id"], property_ids, "outlets.property_id")
    _require_members(products["property_id"], property_ids, "products.property_id")
    _require_members(products["outlet_id"], outlet_ids, "products.outlet_id")

    for row in products.itertuples(index=False):
        if outlet_property[row.outlet_id] != row.property_id:
            raise ValueError(
                f"products.csv: product {row.product_id} property does not match its outlet"
            )

    for filename in [
        "pms_inventory_daily.csv",
        "pms_bookings_daily.csv",
        "pos_checks_daily.csv",
        "pos_product_mix_daily.csv",
        "purchases_daily.csv",
        "inventory_daily.csv",
        "labour_daily.csv",
        "budget_monthly.csv",
    ]:
        _require_members(frames[filename]["property_id"], property_ids, f"{filename}.property_id")

    for filename in ["pos_checks_daily.csv", "pos_product_mix_daily.csv"]:
        _require_members(frames[filename]["outlet_id"], outlet_ids, f"{filename}.outlet_id")

    for filename in ["pos_product_mix_daily.csv", "purchases_daily.csv", "inventory_daily.csv"]:
        _require_members(frames[filename]["product_id"], product_ids, f"{filename}.product_id")

    _require_members(
        frames["purchases_daily.csv"]["supplier_id"],
        supplier_ids,
        "purchases.supplier_id",
    )
    _require_members(
        frames["labour_daily.csv"]["department_id"],
        department_ids,
        "labour.department_id",
    )
    _require_members(
        frames["budget_monthly.csv"]["department_id"],
        department_ids,
        "budget.department_id",
    )

    for row in frames["pos_checks_daily.csv"].itertuples(index=False):
        if outlet_property[row.outlet_id] != row.property_id:
            raise ValueError("POS check property does not match outlet ownership")

    for row in frames["pos_product_mix_daily.csv"].itertuples(index=False):
        if outlet_property[row.outlet_id] != row.property_id:
            raise ValueError("POS product-mix property does not match outlet ownership")
        if product_outlet[row.product_id] != row.outlet_id:
            raise ValueError("POS product-mix product does not belong to the reported outlet")
        if product_property[row.product_id] != row.property_id:
            raise ValueError("POS product-mix product does not belong to the reported property")

    for row in frames["purchases_daily.csv"].itertuples(index=False):
        if product_property[row.product_id] != row.property_id:
            raise ValueError("Purchase product does not belong to the reported property")
        if supplier_category[row.supplier_id] != product_category[row.product_id]:
            raise ValueError("Purchase supplier category does not match product category")

    for row in frames["inventory_daily.csv"].itertuples(index=False):
        if product_property[row.product_id] != row.property_id:
            raise ValueError("Inventory product does not belong to the reported property")

    room_inventory = frames["pms_inventory_daily.csv"].groupby(
        ["date", "property_id"], as_index=False
    )["rooms_available"].sum()
    bookings = frames["pms_bookings_daily.csv"].groupby(
        ["date", "property_id"], as_index=False
    )["rooms_sold"].sum()
    room_check = room_inventory.merge(bookings, on=["date", "property_id"], how="left").fillna(0)
    if (room_check["rooms_sold"] > room_check["rooms_available"]).any():
        raise ValueError("PMS cross-check failed: rooms_sold exceeds rooms_available")

    checks = frames["pos_checks_daily.csv"].groupby(
        ["date", "property_id", "outlet_id"], as_index=False
    )["net_revenue"].sum()
    mix = frames["pos_product_mix_daily.csv"].groupby(
        ["date", "property_id", "outlet_id"], as_index=False
    )["net_revenue"].sum()
    pos_reconciliation = checks.merge(
        mix,
        on=["date", "property_id", "outlet_id"],
        how="outer",
        suffixes=("_checks", "_mix"),
    ).fillna(0)
    pos_reconciliation["delta"] = (
        pos_reconciliation["net_revenue_checks"]
        - pos_reconciliation["net_revenue_mix"]
    ).abs()
    if (pos_reconciliation["delta"] > MONEY_TOLERANCE).any():
        raise ValueError("POS cross-check failed: product mix does not reconcile to outlet checks")

    purchases = frames["purchases_daily.csv"].groupby(
        ["date", "property_id", "product_id"], as_index=False
    )["quantity"].sum()
    inventory = frames["inventory_daily.csv"].groupby(
        ["date", "property_id", "product_id"], as_index=False
    )["receipts_qty"].sum()
    purchase_reconciliation = purchases.merge(
        inventory,
        on=["date", "property_id", "product_id"],
        how="outer",
    ).fillna(0)
    purchase_reconciliation["delta"] = (
        purchase_reconciliation["quantity"] - purchase_reconciliation["receipts_qty"]
    ).abs()
    if (purchase_reconciliation["delta"] > QUANTITY_TOLERANCE).any():
        raise ValueError(
            "Procurement cross-check failed: purchases do not reconcile to inventory receipts"
        )

    inventory_frame = frames["inventory_daily.csv"].copy()
    inventory_frame["date"] = pd.to_datetime(inventory_frame["date"])
    inventory_frame = inventory_frame.sort_values(["property_id", "product_id", "date"])
    inventory_frame["previous_closing"] = inventory_frame.groupby(
        ["property_id", "product_id"]
    )["closing_qty"].shift(1)
    continuity = inventory_frame.dropna(subset=["previous_closing"]).copy()
    continuity["delta"] = (continuity["opening_qty"] - continuity["previous_closing"]).abs()
    if (continuity["delta"] > QUANTITY_TOLERANCE).any():
        raise ValueError(
            "Inventory cross-check failed: opening quantity breaks roll-forward continuity"
        )


def load_and_validate_sources(data_dir: Path) -> dict[str, pd.DataFrame]:
    """Load all required source files and validate row + cross-source contracts."""

    frames: dict[str, pd.DataFrame] = {}
    for filename in SOURCE_MODELS:
        path = data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing required source file: {path}")
        frame = pd.read_csv(path)
        _validate_unique_keys(filename, frame)
        _validate_rows(filename, frame)
        frames[filename] = frame

    _validate_cross_source(frames)
    return frames
