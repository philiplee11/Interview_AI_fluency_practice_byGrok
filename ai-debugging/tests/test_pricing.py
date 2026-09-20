import time
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
