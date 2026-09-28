import pytest

from hospitality_intelligence.contracts import (
    InventoryRecord,
    POSCheckRecord,
    PurchaseRecord,
)


def test_pos_check_revenue_identity_rejects_inconsistent_net_revenue() -> None:
    with pytest.raises(ValueError, match="net_revenue"):
        POSCheckRecord(
            date="2026-09-01",
            property_id="P001",
            outlet_id="O001",
            covers=10,
            gross_revenue=100.0,
            discount_amount=10.0,
            net_revenue=95.0,
        )


def test_purchase_identity_rejects_inconsistent_cost() -> None:
    with pytest.raises(ValueError, match="purchase_cost"):
        PurchaseRecord(
            date="2026-09-01",
            property_id="P001",
            product_id="PRD-001",
            supplier_id="S001",
            quantity=5.0,
            unit_cost=10.0,
            purchase_cost=48.0,
        )


def test_inventory_rollforward_rejects_broken_balance() -> None:
    with pytest.raises(ValueError, match="roll-forward"):
        InventoryRecord(
            date="2026-09-01",
            property_id="P001",
            product_id="PRD-001",
            opening_qty=20.0,
            receipts_qty=10.0,
            usage_qty=5.0,
            waste_qty=1.0,
            closing_qty=30.0,
            weighted_unit_cost=3.0,
            inventory_value=90.0,
        )
