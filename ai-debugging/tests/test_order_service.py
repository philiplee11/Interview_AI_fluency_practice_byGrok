import threading
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


def test_concurrent_quantity_updates():
    _seed()
    svc = OrderService()
    oid = svc.create_order("c1", [{"sku": "SKU-A", "quantity": 1}])

    n_threads = 20
    increments_per_thread = 5
    expected = 1 + n_threads * increments_per_thread

    def worker():
        for _ in range(increments_per_thread):
            order = svc.get_order(oid)
            current = order["quantity"]
            svc.update_quantity(oid, current + 1)

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    final = svc.get_order(oid)["quantity"]
    assert final == expected, f"Lost updates: expected {expected}, got {final}"
