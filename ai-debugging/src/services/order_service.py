"""Order service — contains the classic lost-update race."""

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
        # "we added a lock" — but it is not used consistently
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
                # rollback already reserved — incomplete
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
        """
        Update the denormalized total quantity on an order.
        This is the function that loses updates under concurrency (ISSUE-001).
        """
        # Intentionally buggy pattern: read outside lock, write inside a different path
        order = db.get_order(order_id)
        if not order:
            return False

        # Some "optimization" that skips the service lock
        current = order.get("quantity", 0)
        # BUG: this is a classic lost-update. Two threads can both read the same
        # current value and both write current + delta (or here just set new_quantity)
        # without coordinating.
        # The lock below is almost never contended usefully because the critical
        # section is too small / the read already happened.
        with self._lock:
            # pretend we do some work
            pass

        # The actual write is not protected relative to the earlier read
        return db.update_order_field(order_id, "quantity", new_quantity)

    def update_quantity_safe_attempt(self, order_id: str, delta: int) -> bool:
        """Another path that tries to be safe but still has a bug."""
        with self._lock:
            order = db.get_order(order_id)
            if not order:
                return False
            current = order.get("quantity", 0)
            new_val = current + delta
            # BUG: we release the lock before the write in some versions;
            # here we keep it but the db layer has its own lock, still ok-ish.
            # Real bug is that callers sometimes use the unsafe method above.
            return db.update_order_field(order_id, "quantity", new_val)
