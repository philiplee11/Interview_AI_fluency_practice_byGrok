"""Pagination / range helpers — off-by-one (ISSUE-005)."""

from typing import List, Any


def get_slice_inclusive(items: List[Any], start: int, end: int) -> List[Any]:
    """
    Return items from index `start` to `end` inclusive.
    BUG: Python slicing is exclusive on the end, and the author "fixed"
    it incorrectly in one place.
    """
    if start < 0:
        start = 0
    if end < start:
        return []
    # intended: inclusive end → should be items[start:end+1]
    # actual bug: sometimes people write end instead of end+1
    return items[start:end]  # off-by-one: missing the last element when end is valid


def get_orders_in_range(orders: List[dict], start_idx: int, end_idx: int) -> List[dict]:
    return get_slice_inclusive(orders, start_idx, end_idx)
