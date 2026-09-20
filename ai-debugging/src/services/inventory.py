"""Inventory service."""

from src.core import db
import threading


class InventoryService:
    def __init__(self):
        self._lock = threading.Lock()

    def set_stock(self, sku: str, qty: int) -> None:
        db.set_stock(sku, qty)

    def get_stock(self, sku: str) -> int:
        return db.get_stock(sku)

    def reserve(self, sku: str, qty: int) -> bool:
        """Try to reserve `qty` units."""
        current = db.get_stock(sku)
        if current < qty:
            return False
        new_level = db.adjust_stock(sku, -qty)
        return True

    def release(self, sku: str, qty: int) -> None:
        db.adjust_stock(sku, qty)

    def reserve_safe(self, sku: str, qty: int) -> bool:
        """Reserve `qty` units, holding a lock across the check and the adjust."""
        with self._lock:
            current = db.get_stock(sku)
            if current < qty:
                return False
            db.adjust_stock(sku, -qty)
            return True
