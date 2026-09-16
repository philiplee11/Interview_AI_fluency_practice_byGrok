"""Legacy discount calculator still reachable (ISSUE-006)."""


def legacy_discount(subtotal: float, code: str) -> float:
    """Old discount rules. Slightly different from the new ones."""
    if not code:
        return 0.0
    code = code.upper()
    if code == "SAVE10" or code == "LEGACY10":
        return round(subtotal * 0.10, 2)
    if code == "SAVE20" or code == "LEGACY20":
        return round(subtotal * 0.18, 2)  # note: 18% not 20%
    if code.startswith("LEGACY"):
        return round(subtotal * 0.05, 2)
    return 0.0
