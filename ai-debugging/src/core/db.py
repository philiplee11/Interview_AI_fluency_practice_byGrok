"""Very naive in-memory 'database' with shared mutable state."""

from threading import Lock
from typing import Any, Dict, List, Optional
import copy

_lock = Lock()
_orders: Dict[str, Dict[str, Any]] = {}
_inventory: Dict[str, int] = {}
_prices: Dict[str, float] = {}
_order_counter = 0


def reset():
    """Test helper."""
    global _orders, _inventory, _prices, _order_counter
    with _lock:
        _orders = {}
        _inventory = {}
        _prices = {}
        _order_counter = 0


def next_order_id() -> str:
    global _order_counter
    _order_counter += 1
    return f"ORD-{_order_counter:05d}"


def save_order(order_id: str, data: Dict[str, Any]) -> None:
    with _lock:
        _orders[order_id] = copy.deepcopy(data)


def get_order(order_id: str) -> Optional[Dict[str, Any]]:
    with _lock:
        o = _orders.get(order_id)
        return copy.deepcopy(o) if o else None


def update_order_field(order_id: str, field: str, value: Any) -> bool:
    """Update a single field. Used by concurrent updaters."""
    with _lock:
        if order_id not in _orders:
            return False
        _orders[order_id][field] = value
        return True


def list_orders() -> List[Dict[str, Any]]:
    with _lock:
        return [copy.deepcopy(o) for o in _orders.values()]


def set_stock(sku: str, qty: int) -> None:
    with _lock:
        _inventory[sku] = qty


def get_stock(sku: str) -> int:
    with _lock:
        return _inventory.get(sku, 0)


def adjust_stock(sku: str, delta: int) -> int:
    """Returns new stock level."""
    with _lock:
        current = _inventory.get(sku, 0)
        new = current + delta
        _inventory[sku] = new
        return new


def set_price(sku: str, price: float) -> None:
    with _lock:
        _prices[sku] = price


def get_price(sku: str) -> Optional[float]:
    with _lock:
        return _prices.get(sku)
