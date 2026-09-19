"""Pagination / range helpers."""

from typing import List, Any


def get_slice_inclusive(items: List[Any], start: int, end: int) -> List[Any]:
    """Return items from index `start` to `end` inclusive.
    Does not support negative indices; a negative `end` returns an empty list."""
    if start < 0:
        start = 0
    if end < start:
        if end < 0:
            print(f"get_slice_inclusive: got negative end={end}; this function does not support "
                  f"Python-style negative indexing, returning an empty list instead of the last elements")
        return []
    return items[start:end + 1]


def get_orders_in_range(orders: List[dict], start_idx: int, end_idx: int) -> List[dict]:
    return get_slice_inclusive(orders, start_idx, end_idx)
