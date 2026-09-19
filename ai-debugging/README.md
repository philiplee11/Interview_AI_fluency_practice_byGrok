# OrderFlow

A small in-memory order-processing service: it manages inventory, calculates prices and discounts, creates and updates orders, and runs a background worker for async tasks.

Originally built as an AI-debugging practice exercise with intentionally seeded bugs (see `docs/KNOWN_ISSUES.md`). All seeded issues, plus several unlisted ones found during the debugging pass, have since been fixed and covered by regression tests — this README describes the service as it stands now.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

Run the sample entry point:

```bash
python -m src.main
```

## Architecture

- `src/main.py` — sample entry point: seeds stock/prices and creates one order.
- `src/models/order.py` — `Order` and `LineItem` dataclasses.
- `src/services/order_service.py` — `OrderService`: creates orders, validates input, coordinates inventory and pricing.
- `src/services/inventory.py` — `InventoryService`: stock lookups and atomic reservations.
- `src/services/pricing.py` — `PricingService`: price lookups with a shared, TTL-based cache, and discount calculation.
- `src/services/worker.py` — `BackgroundWorker`: a simple threaded task queue.
- `src/core/db.py` — the in-memory "database": module-level dicts for orders, inventory, and prices, all guarded by a single shared lock. Every atomic operation (reservations, quantity updates, order-ID generation) lives here as one function that does its full read-modify-write inside one critical section.
- `src/core/config.py` — configuration constants and feature flags.
- `src/utils/pagination.py` — inclusive-range slicing helpers.
- `src/legacy/discount.py` — the older discount-rate calculator, still used for `LEGACY*` codes and as a fallback when `USE_NEW_PRICING` is off.

## Functionality

### Orders

`OrderService.create_order(customer_id, items)`:

1. Validates every line item's `quantity` up front — it must be a real positive `int` (not `bool`, not a float, not zero or negative) — before allocating an order ID or touching inventory. Invalid input raises `ValueError` naming the actual problem (`"Invalid quantity for ..."` vs. `"Insufficient stock for ..."`).
2. Looks up each item's price (falls back to `0.0` if the SKU has no price set).
3. Reserves inventory for each item atomically; if any reservation fails, everything reserved so far for this order is released before raising.
4. Computes the order total, applying a discount code if present, and saves the order.

`OrderService.update_quantity(order_id, delta)` atomically applies a quantity delta to an existing order (add or subtract units) in one critical section — it takes a delta, not an absolute value, so the read-modify-write can't be corrupted by a caller's own stale read.

### Inventory

`InventoryService.reserve(sku, qty)` and `.release(sku, qty)` wrap atomic `db` operations. A reservation is a single check-and-subtract critical section — no window exists between checking available stock and committing the subtraction, so concurrent reservations can't oversell. Negative quantities are rejected.

### Pricing

`PricingService` caches prices in a single dict shared across every instance (not per-instance), guarded by one lock so a price update from any instance invalidates the cache for all of them immediately. Reads and writes each run as one uninterrupted operation, including the underlying `db` call, so a concurrent update can't have its cache invalidation missed by a slower, overlapping read.

`set_price` rejects `None` and negative prices.

`calculate_total` applies at most one discount per order:
- `SAVE10` / `SAVE20` — 10% / 20% off (new pricing path).
- `LEGACY10` / `LEGACY20` / any other `LEGACY*` code — 10% / 20% / 5% off (legacy path, also used when `USE_NEW_PRICING` is `False`).
- A non-string `discount_code` is logged and ignored (zero discount applied) rather than crashing the order.

### Background worker

`BackgroundWorker` runs one task-processing thread over an internal queue. `start()` is idempotent under concurrent calls (guarded by a lock, so it can't spawn duplicate worker threads). Each task's simulated file handle is opened in the OS temp directory and always closed afterward, tracked accurately by `open_file_count()`.

### Pagination

`get_slice_inclusive(items, start, end)` returns items from `start` to `end` inclusive. It does not support Python-style negative indexing — a negative `end` returns an empty list and prints a warning, rather than silently guessing what the caller meant.

## Concurrency model

All shared state lives in `src/core/db.py` behind one module-level lock. Every operation that needs to read a value and act on it — reserving stock, applying a quantity delta, generating an order ID — does so inside a single `with _lock:` block, never as two separate locked calls. This is what makes the service correct under concurrent access: locking each primitive dict operation isn't enough on its own, since the gap between two separately-locked calls is exactly where a race can happen.

## Testing

```bash
pytest -q
```

19 tests, including deterministic "forced interleave" tests for the concurrency-sensitive paths (inventory reservation, order quantity updates, pricing cache, worker startup) — these force a specific bad thread interleaving on purpose, rather than relying on raw thread-scheduling luck, so they reliably fail against a regression and reliably pass against a fix.

## History

`docs/KNOWN_ISSUES.md` documents the originally seeded bugs (ISSUE-001 through 006) as a historical record of the practice exercise's starting state. All of them are now fixed; several additional bugs found during the debugging pass (duplicate-thread races, unvalidated input, an incorrect discount rate, dead code) are not listed there but are covered by the current test suite.
