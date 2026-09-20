"""Pagination / range helpers."""

from typing import List, Any


def get_slice_inclusive(items: List[Any], start: int, end: int) -> List[Any]:
    """Return items from index `start` to `end` inclusive."""
    if start < 0:
        start = 0
    if end < start:
        return []
    return items[start:end]


def get_orders_in_range(orders: List[dict], start_idx: int, end_idx: int) -> List[dict]:
    return get_slice_inclusive(orders, start_idx, end_idx)
