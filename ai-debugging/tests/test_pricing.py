import time
import threading
from unittest.mock import patch
from src.core import db
from src.services.pricing import PricingService
from src.models.order import Order, LineItem
from src.core.config import CACHE_TTL_SECONDS


def test_cache_invalidation_on_price_update():
    ps = PricingService()
    ps.set_price("SKU-Z", 100.0)
    assert ps.get_price("SKU-Z") == 100.0

    ps.set_price("SKU-Z", 150.0)
    got = ps.get_price("SKU-Z")
    assert got == 150.0, f"Stale cache returned {got}"


def test_no_stale_write_after_concurrent_price_update():
    """A slow reader must not backfill a stale price after a writer's
    invalidation already ran while the cache was still empty."""
    ps = PricingService()
    db.set_price("SKU-Q", 100.0)

    real_get_price = db.get_price

    def slow_get_price(sku):
        result = real_get_price(sku)  # read the current price immediately
        time.sleep(0.05)  # delay the write-back, forcing the writer to run first
        return result

    results = {}

    def reader():
        with patch("src.services.pricing.db.get_price", side_effect=slow_get_price):
            results["read"] = ps.get_price("SKU-Q")

    def writer():
        ps.set_price("SKU-Q", 150.0)

    t1 = threading.Thread(target=reader)
    t1.start()
    time.sleep(0.01)  # ensure the reader has entered its critical section first
    t2 = threading.Thread(target=writer)
    t2.start()
    t1.join()
    t2.join()

    assert results["read"] == 100.0, "reader should still see the price as of when it started"
    assert db.get_price("SKU-Q") == 150.0

    cached = PricingService._cache.get("SKU-Q")
    assert cached is None or cached[0] == 150.0, (
        f"Stale price leaked into cache after concurrent update: {cached}"
    )
    assert ps.get_price("SKU-Q") == 150.0, "subsequent read must not return a stale cached price"


def test_set_price_rejects_none_and_negative():
    ps = PricingService()

    for bad_price in (None, -50.0):
        try:
            ps.set_price("SKU-BAD", bad_price)
            assert False, f"price={bad_price} should have been rejected"
        except ValueError as e:
            assert "Invalid price" in str(e), f"Unexpected error message: {e}"

    assert ps.get_price("SKU-BAD") is None, "A rejected price must never reach db or cache"


def test_save20_discount_is_twenty_percent():
    """SAVE20/LEGACY20 must apply a genuine 20% discount, not 18%."""
    ps = PricingService()
    order = Order(
        order_id="t3",
        customer_id="c",
        items=[LineItem(sku="A", quantity=1, unit_price=100.0)],
        discount_code="LEGACY20",
    )
    total = ps.calculate_total(order)
    assert total == 80.0, f"Expected 80.0 after a genuine 20% discount, got {total}"


def test_invalid_discount_code_type_is_ignored_not_fatal():
    """A non-string discount_code must not crash the order. It should be
    ignored (no discount applied), letting the sale complete normally."""
    ps = PricingService()
    order = Order(
        order_id="t2",
        customer_id="c",
        items=[LineItem(sku="A", quantity=1, unit_price=100.0)],
        discount_code=123,  # invalid type, e.g. a numeric ID stored by mistake
    )
    total = ps.calculate_total(order)
    assert total == 100.0, f"Expected full price with no discount, got {total}"


def test_discount_not_applied_twice():
    ps = PricingService()
    order = Order(
        order_id="t1",
        customer_id="c",
        items=[LineItem(sku="A", quantity=1, unit_price=100.0)],
        discount_code="LEGACY10",
    )
    total = ps.calculate_total(order)
    assert total == 90.0, f"Expected 90.0 after single 10% discount, got {total}"
