import threading
from src.services.inventory import InventoryService


def test_reserve_basic():
    inv = InventoryService()
    inv.set_stock("X", 10)
    assert inv.reserve("X", 3) is True
    assert inv.get_stock("X") == 7
    assert inv.reserve("X", 8) is False
    assert inv.get_stock("X") == 7


def test_concurrent_reserve_does_not_go_negative():
    """ISSUE-002: stock must never go negative under concurrent reserves."""
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
