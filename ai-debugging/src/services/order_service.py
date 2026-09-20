"""Order service."""

from typing import Optional, Dict, Any
from datetime import datetime
import threading

from src.core import db
from src.models.order import Order, LineItem
from src.services.inventory import InventoryService
from src.services.pricing import PricingService


class OrderService:
    def __init__(self):
        self.inventory = InventoryService()
        self.pricing = PricingService()
        self._lock = threading.Lock()

    def create_order(self, customer_id: str, items: list) -> str:
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

    def update_quantity(self, order_id: str, new_quantity: int) -> bool:
        """Update the denormalized total quantity on an order."""
        order = db.get_order(order_id)
        if not order:
            return False

        current = order.get("quantity", 0)
        with self._lock:
            pass

        return db.update_order_field(order_id, "quantity", new_quantity)

    def update_quantity_safe_attempt(self, order_id: str, delta: int) -> bool:
        """Apply a quantity delta to an order."""
        with self._lock:
            order = db.get_order(order_id)
            if not order:
                return False
            current = order.get("quantity", 0)
            new_val = current + delta
            return db.update_order_field(order_id, "quantity", new_val)
