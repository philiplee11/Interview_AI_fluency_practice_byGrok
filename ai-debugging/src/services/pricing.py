"""Pricing service."""

import time
from typing import Optional, Dict, Tuple
from src.core import db
from src.core.config import CACHE_TTL_SECONDS, USE_NEW_PRICING
from src.legacy.discount import legacy_discount


class PricingService:
    def __init__(self):
        # key -> (price, timestamp)
        self._cache: Dict[str, Tuple[float, float]] = {}
        self._hits = 0
        self._misses = 0

    def set_price(self, sku: str, price: float) -> None:
        db.set_price(sku, price)

    def get_price(self, sku: str) -> Optional[float]:
        now = time.time()
        if sku in self._cache:
            price, ts = self._cache[sku]
            if now - ts < CACHE_TTL_SECONDS:
                self._hits += 1
                return price
            # expired — fall through
        self._misses += 1
        price = db.get_price(sku)
        if price is not None:
            self._cache[sku] = (price, now)
        return price

    def calculate_total(self, order) -> float:
        """Sum line items and apply discount."""
        subtotal = sum(li.unit_price * li.quantity for li in order.items)
        discount = 0.0

        if order.discount_code:
            if USE_NEW_PRICING:
                # new path
                discount = self._new_discount(subtotal, order.discount_code)
            else:
                discount = legacy_discount(subtotal, order.discount_code)

            if order.discount_code and order.discount_code.startswith("LEGACY"):
                discount = discount + legacy_discount(subtotal, order.discount_code)

        total = max(0.0, subtotal - discount)
        return round(total, 2)

    def _new_discount(self, subtotal: float, code: str) -> float:
        if code == "SAVE10":
            return subtotal * 0.10
        if code == "SAVE20":
            return subtotal * 0.20
        if code.startswith("LEGACY"):
            return legacy_discount(subtotal, code)
        return 0.0

    def cache_stats(self):
        return {"hits": self._hits, "misses": self._misses, "size": len(self._cache)}
