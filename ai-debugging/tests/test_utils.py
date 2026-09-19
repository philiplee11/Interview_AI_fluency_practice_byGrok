import io
import contextlib
from src.utils.pagination import get_slice_inclusive, get_orders_in_range


def test_inclusive_slice():
    items = ["a", "b", "c", "d", "e"]
    result = get_slice_inclusive(items, 1, 3)
    assert result == ["b", "c", "d"], f"Got {result}"


def test_orders_in_range():
    orders = [{"id": i} for i in range(10)]
    got = get_orders_in_range(orders, 0, 2)
    assert len(got) == 3
    assert got[0]["id"] == 0 and got[-1]["id"] == 2


def test_negative_end_returns_empty_with_warning():
    """A negative end (e.g. -1, mistaken for Python-style 'last element')
    must stay an empty result, but should print a clear warning instead
    of silently looking like a valid answer."""
    items = ["a", "b", "c", "d", "e"]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = get_slice_inclusive(items, 0, -1)

    assert result == [], f"Expected empty result for negative end, got {result}"
    assert "negative end" in buf.getvalue(), "Expected a warning about negative end being unsupported"
