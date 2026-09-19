import threading
import time
from src.core import db
from src.services.inventory import InventoryService


class _SlowGetDict(dict):
    """Behaves exactly like a dict, except .get() sleeps before returning.
    Used to inject a delay into the real production function's own read,
    instead of replacing the function with a hand-written stand-in."""

    def get(self, *args, **kwargs):
        result = super().get(*args, **kwargs)
        time.sleep(0.05)
        return result


def test_reserve_basic():
    inv = InventoryService()
    inv.set_stock("X", 10)
    assert inv.reserve("X", 3) is True
    assert inv.get_stock("X") == 7
    assert inv.reserve("X", 8) is False
    assert inv.get_stock("X") == 7


def test_reserve_rejects_negative_quantity():
    """A negative qty must not flip the check-then-act comparison and add
    stock back instead of failing."""
    inv = InventoryService()
    inv.set_stock("SKU-A", 10)

    assert inv.reserve("SKU-A", -5) is False, "Negative quantity must be rejected"
    assert inv.get_stock("SKU-A") == 10, "Stock must be unchanged after a rejected reservation"


def test_concurrent_reserve_does_not_go_negative():
    inv = InventoryService()
    inv.set_stock("Y", 50)

    success_count = 0
    lock = threading.Lock()

    def try_reserve():
        nonlocal success_count
        if inv.reserve("Y", 10):
            with lock:
                success_count += 1

    threads = [threading.Thread(target=try_reserve) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    stock = inv.get_stock("Y")
    # At most 5 successful reserves of 10 from 50
    assert success_count <= 5
    assert stock >= 0, f"Stock went negative: {stock}"
    assert stock == 50 - success_count * 10


def test_concurrent_reserve_forced_interleave():
    """Deterministic version of test_concurrent_reserve_does_not_go_negative:
    forces two reservations to overlap on the real db.try_reserve_stock's
    check-then-act, instead of hoping raw thread scheduling happens to
    trigger it."""
    inv = InventoryService()
    inv.set_stock("SKU-Z", 10)

    # Swap the real shared inventory dict for one whose .get(sku, ...) sleeps.
    # The actual db.try_reserve_stock code still runs unmodified; only its
    # own read of the current stock level now takes 50ms.
    db._inventory = _SlowGetDict(db._inventory)

    results = []

    def worker():
        results.append(inv.reserve("SKU-Z", 8))

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start()
    time.sleep(0.01)  # ensure t1 enters the critical section first
    t2.start()
    t1.join()
    t2.join()

    stock = inv.get_stock("SKU-Z")
    assert results.count(True) == 1, f"Expected exactly one reservation to succeed, got {results}"
    assert stock == 2, f"Expected stock to be 2 under forced contention, got {stock}"
