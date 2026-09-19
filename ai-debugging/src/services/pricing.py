"""Pricing service."""

import time
import threading
from typing import Optional, Dict, Tuple
from src.core import db
from src.core.config import CACHE_TTL_SECONDS, USE_NEW_PRICING
from src.legacy.discount import legacy_discount


class PricingService:
    # Shared across all instances so a price update on one instance
    # invalidates the entry for every instance, not just the caller's own cache.
    _cache: Dict[str, Tuple[float, float]] = {}
    _cache_lock = threading.Lock()

    def __init__(self):
        self._hits = 0
        self._misses = 0

    def set_price(self, sku: str, price: float) -> None:
        if price is None or price < 0:
            raise ValueError(f"Invalid price for {sku}: {price}")
        with PricingService._cache_lock:
            db.set_price(sku, price)
            PricingService._cache.pop(sku, None)

    def get_price(self, sku: str) -> Optional[float]:
        now = time.time()
        with PricingService._cache_lock:
            if sku in PricingService._cache:
                price, ts = PricingService._cache[sku]
                if now - ts < CACHE_TTL_SECONDS:
                    self._hits += 1
                    return price
            self._misses += 1
            price = db.get_price(sku)
            if price is not None:
                PricingService._cache[sku] = (price, now)
            return price

    def calculate_total(self, order) -> float:
        """Sum line items and apply discount."""
        subtotal = sum(li.unit_price * li.quantity for li in order.items)
        discount = 0.0

        if order.discount_code:
            if not isinstance(order.discount_code, str):
                print(
                    f"Ignoring invalid discount_code for order {order.order_id}: "
                    f"expected str, got {type(order.discount_code).__name__} ({order.discount_code!r})"
                )
            elif USE_NEW_PRICING:
                discount = self._new_discount(subtotal, order.discount_code)
            else:
                discount = legacy_discount(subtotal, order.discount_code)

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
        with PricingService._cache_lock:
            size = len(PricingService._cache)
        return {"hits": self._hits, "misses": self._misses, "size": size}
