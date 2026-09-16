"""Inventory service — can go negative under race (ISSUE-002)."""

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
        """
        Try to reserve `qty` units.
        BUG: check-then-act race. Two threads can both see enough stock
        and both subtract, driving the counter negative.
        """
        # No lock around the whole check + adjust
        current = db.get_stock(sku)
        if current < qty:
            return False
        # window for race here
        new_level = db.adjust_stock(sku, -qty)
        # even if new_level is negative we already committed
        return True

    def release(self, sku: str, qty: int) -> None:
        db.adjust_stock(sku, qty)

    def reserve_safe(self, sku: str, qty: int) -> bool:
        """Correct version that exists but is not always called."""
        with self._lock:
            current = db.get_stock(sku)
            if current < qty:
                return False
            db.adjust_stock(sku, -qty)
            return True
