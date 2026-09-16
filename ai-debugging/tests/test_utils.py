from src.utils.pagination import get_slice_inclusive, get_orders_in_range


def test_inclusive_slice():
    """ISSUE-005: end index must be inclusive."""
    items = ["a", "b", "c", "d", "e"]
    # request indices 1..3 inclusive → b, c, d
    result = get_slice_inclusive(items, 1, 3)
    assert result == ["b", "c", "d"], f"Got {result}"


def test_orders_in_range():
    orders = [{"id": i} for i in range(10)]
    got = get_orders_in_range(orders, 0, 2)
    assert len(got) == 3
    assert got[0]["id"] == 0 and got[-1]["id"] == 2
