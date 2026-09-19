"""Order service."""

from typing import Optional, Dict, Any
from datetime import datetime

from src.core import db
from src.models.order import Order, LineItem
from src.services.inventory import InventoryService
from src.services.pricing import PricingService


class OrderService:
    def __init__(self):
        self.inventory = InventoryService()
        self.pricing = PricingService()

    def create_order(self, customer_id: str, items: list) -> str:
        for it in items:
            quantity = it["quantity"]
            if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
                raise ValueError(f"Invalid quantity for {it['sku']}: {quantity!r}")

        order_id = db.next_order_id()
        line_items = []
        for it in items:
            price = self.pricing.get_price(it["sku"]) or 0.0
            line_items.append(LineItem(sku=it["sku"], quantity=it["quantity"], unit_price=price))

        # reserve inventory
        for li in line_items:
            ok = self.inventory.reserve(li.sku, li.quantity)
            if not ok:
                for prev in line_items:
                    if prev is li:
                        break
                    self.inventory.release(prev.sku, prev.quantity)
                raise ValueError(f"Insufficient stock for {li.sku}")

        order = Order(
            order_id=order_id,
            customer_id=customer_id,
            items=line_items,
            status="pending",
            created_at=datetime.utcnow(),
        )
        order.total = self.pricing.calculate_total(order)
        db.save_order(order_id, order.to_dict())
        return order_id

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        return db.get_order(order_id)

    def update_quantity(self, order_id: str, delta: int) -> bool:
        """Atomically apply a quantity delta to an order."""
        return db.apply_quantity_delta(order_id, delta) is not None
