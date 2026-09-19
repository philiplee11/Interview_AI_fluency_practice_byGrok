# Known Issues / Ticket Backlog

These are the symptoms reported by the "team". Use them as your starting point.

## ISSUE-001 — Lost order quantity updates under concurrent load
**Severity:** High  
**Symptoms:** When multiple workers call `OrderService.update_quantity` for the same order at the same time, the final quantity is frequently lower than expected.  
**Repro:** `pytest tests/test_order_service.py::test_concurrent_quantity_updates -q`  
**Notes from previous engineer:** "I think it's a race. We added a lock somewhere but maybe not everywhere."

## ISSUE-002 — Inventory goes negative
**Severity:** High  
**Symptoms:** `InventoryService.reserve` can drive stock below zero when two reservations race. Also, after a failed order the stock is not always released correctly.  
**Repro:** `pytest tests/test_inventory.py -q`

## ISSUE-003 — Pricing cache returns stale or wrong prices
**Severity:** Medium  
**Symptoms:** After a price update, some clients still see the old price for a long time. Occasionally the discount percentage is applied twice.  
**Repro:** `pytest tests/test_pricing.py -q`

## ISSUE-004 — Background worker leaks file handles / never stops cleanly
**Severity:** Medium  
**Symptoms:** After running the worker for a while and then calling `stop()`, open file descriptors keep growing. Sometimes the process hangs on shutdown.  
**Repro:** `pytest tests/test_worker.py -q` (may be flaky)

## ISSUE-005 — Off-by-one in pagination / range queries
**Severity:** Low  
**Symptoms:** `get_orders_in_range(start, end)` sometimes returns one fewer order than expected when the range is inclusive on both ends.  
**Repro:** look at `tests/test_utils.py`

## ISSUE-006 — Legacy discount calculator still used in one path
**Severity:** Low  
**Symptoms:** Some orders receive a different discount than the new pricing service. Code path is hard to find.  
**Notes:** Search for imports from `src.legacy`.

---

**Your job:** Diagnose root causes with the help of AI, write the smallest correct fixes, and make the relevant tests pass. Do not rewrite the entire service.

**Note:** this list may not be exhaustive.
