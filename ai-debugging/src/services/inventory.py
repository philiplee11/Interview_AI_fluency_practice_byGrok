"""Inventory service."""

from src.core import db


class InventoryService:
    def set_stock(self, sku: str, qty: int) -> None:
        db.set_stock(sku, qty)

    def get_stock(self, sku: str) -> int:
        return db.get_stock(sku)

    def reserve(self, sku: str, qty: int) -> bool:
        """Try to reserve `qty` units. Check and reserve happen atomically."""
        return db.try_reserve_stock(sku, qty)

    def release(self, sku: str, qty: int) -> None:
        db.adjust_stock(sku, qty)
