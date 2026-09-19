import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.core import db
from src.services.order_service import OrderService
from src.services.inventory import InventoryService
from src.services.pricing import PricingService


def _seed():
    inv = InventoryService()
    pricing = PricingService()
    inv.set_stock("SKU-A", 1000)
    pricing.set_price("SKU-A", 10.0)


def test_create_order_basic():
    _seed()
    svc = OrderService()
    oid = svc.create_order("c1", [{"sku": "SKU-A", "quantity": 3}])
    order = svc.get_order(oid)
    assert order is not None
    assert order["quantity"] == 3
    assert order["status"] == "pending"


def test_create_order_rejects_invalid_quantity():
    """Zero or negative quantity must be rejected before any stock is
    touched or an order_id is allocated, not discovered later as a
    misleading 'insufficient stock' failure."""
    _seed()
    inv = InventoryService()
    svc = OrderService()

    for bad_quantity in (0, -5, 2.5, True, "3", None):
        try:
            svc.create_order("c1", [{"sku": "SKU-A", "quantity": bad_quantity}])
            assert False, f"quantity={bad_quantity!r} should have been rejected"
        except ValueError as e:
            assert "Invalid quantity" in str(e), f"Unexpected error message: {e}"

        assert inv.get_stock("SKU-A") == 1000, "Stock must be untouched by a rejected order"
        assert isinstance(inv.get_stock("SKU-A"), int), "Stock type must stay int, never drift to float"


def test_concurrent_quantity_updates():
    _seed()
    svc = OrderService()
    oid = svc.create_order("c1", [{"sku": "SKU-A", "quantity": 1}])

    n_threads = 20
    increments_per_thread = 5
    expected = 1 + n_threads * increments_per_thread

    def worker():
        for _ in range(increments_per_thread):
            svc.update_quantity(oid, 1)

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    final = svc.get_order(oid)["quantity"]
    assert final == expected, f"Lost updates: expected {expected}, got {final}"


class _SlowGetDict(dict):
    """Behaves exactly like a dict, except .get() sleeps before returning.
    Used to inject a delay into the real production function's own read,
    instead of replacing the function with a hand-written stand-in."""

    def get(self, *args, **kwargs):
        result = super().get(*args, **kwargs)
        time.sleep(0.05)
        return result


def test_concurrent_quantity_updates_forced_interleave():
    """Deterministic version of test_concurrent_quantity_updates: forces two
    updates to overlap on the real db.apply_quantity_delta's read-modify-write,
    instead of hoping raw thread scheduling happens to trigger it."""
    _seed()
    svc = OrderService()
    oid = svc.create_order("c1", [{"sku": "SKU-A", "quantity": 1}])

    # Swap the real per-order dict for one whose .get("quantity", ...) sleeps.
    # The actual db.apply_quantity_delta code still runs unmodified; only its
    # own read of the current quantity now takes 50ms.
    db._orders[oid] = _SlowGetDict(db._orders[oid])

    def worker():
        svc.update_quantity(oid, 1)

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start()
    time.sleep(0.01)  # ensure t1 enters the critical section first
    t2.start()
    t1.join()
    t2.join()

    final = svc.get_order(oid)["quantity"]
    assert final == 3, f"Expected 3 after two +1 updates under forced contention, got {final}"
